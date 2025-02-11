import os
import time
import sys
from flask import Flask, jsonify, request, redirect, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# Determine the storage backend for rate limiting.
redis_storage_uri = os.environ.get("REDIS_URL")
if not redis_storage_uri:
    app.logger.warning(
        "No REDIS_URL environment variable set; falling back to in-memory storage for rate limiting. "
        "This is not recommended for production."
    )
    redis_storage_uri = "memory://"

# If using Redis, try to connect before proceeding.
if redis_storage_uri.startswith("redis://"):
    import redis
    max_retries = 5
    for attempt in range(max_retries):
        try:
            r = redis.Redis.from_url(redis_storage_uri)
            r.ping()
            app.logger.info("Connected to Redis on attempt %s/%s", attempt + 1, max_retries)
            break
        except Exception as e:
            app.logger.warning("Could not connect to Redis (attempt %s/%s): %s", attempt + 1, max_retries, e)
            time.sleep(2)
    else:
        app.logger.error("Failed to connect to Redis after %s attempts. Exiting.", max_retries)
        sys.exit(1)

# Configure Flask-Limiter with the chosen storage backend.
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=redis_storage_uri,
    default_limits=["100 per minute"]
)

# Apply ProxyFix to correctly interpret forwarded headers.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# Redirect HTTP to HTTPS based on the 'X-Forwarded-Proto' header.
@app.before_request
def enforce_https():
    # Skip HTTPS redirection for health check requests.
    if request.path == "/health":
        return
    if request.headers.get("X-Forwarded-Proto", "http") != "https":
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)

# Add security headers.
@app.after_request
def set_security_headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Template for a simple UI.
template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; text-align: center; padding: 50px; }
        .container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: inline-block; }
        h1 { color: #333; }
        p { font-size: 1.2em; color: #555; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ message }}</h1>
        <p>Timestamp: {{ timestamp }}</p>
    </div>
</body>
</html>
"""

@app.route("/status", methods=["GET"])
@limiter.limit("10 per minute")  # Rate limit this endpoint.
def status():
    return render_template_string(
        template,
        title="Status",
        message="Zayzoon rocking here Zayzoon rocking here! 🚀",
        timestamp=int(time.time())
    )

@app.route("/health", methods=["GET"])
@limiter.limit("10 per minute")  # Rate limit this endpoint.
def health():
    return render_template_string(
        template,
        title="Health Check",
        message="Status: Healthy ✅",
        timestamp=int(time.time())
    )

# Custom error handling.
@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify(error="Too many requests. Please try again later."), 429

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error="Endpoint not found."), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify(error="An unexpected error occurred."), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)
