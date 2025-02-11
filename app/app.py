from flask import Flask, jsonify, request, redirect, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
import time

app = Flask(__name__)

# Apply rate limiting to prevent abuse
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"]  # Adjust as needed
)

# Force HTTPS if behind a proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# Redirect HTTP to HTTPS
@app.before_request
def enforce_https():
    if request.headers.get('X-Forwarded-Proto', 'http') != 'https':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# Add security headers
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Template for a simple UI
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
@limiter.limit("10 per minute")  # Rate limit this endpoint
def status():
    return render_template_string(template, title="Status", message="Zayzoon rocking here! 🚀", timestamp=int(time.time()))

@app.route("/health", methods=["GET"])
@limiter.limit("10 per minute")  # Rate limit this endpoint
def health():
    return render_template_string(template, title="Health Check", message="Status: Healthy ✅", timestamp=int(time.time()))

# Custom error handling
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
    # Running on all interfaces with SSL context
    app.run(host="0.0.0.0", port=443, ssl_context=('certificate.pem', 'private-key.pem'))
