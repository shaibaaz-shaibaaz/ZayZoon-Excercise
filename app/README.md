# Flask Application Documentation

## Overview

This Flask application provides two endpoints, `/status` and `/health`, that display real-time status and health information through a simple, styled HTML interface. The application is secured with HTTPS, rate limiting, and HTTP security headers to ensure safe deployment in production environments.

## Features

- **Secure Communication:** Enforces HTTPS and uses SSL/TLS encryption.
- **Rate Limiting:** Protects against abuse by limiting requests per IP.
- **Security Headers:** Adds headers to prevent common web vulnerabilities.
- **User-Friendly Interface:** Displays status messages with a clean design.
- **Custom Error Handling:** Gracefully handles errors and limits sensitive information exposure.

## Code Breakdown

### 1. **Imports and Initialization**
```python
from flask import Flask, jsonify, request, redirect, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
import time

app = Flask(__name__)
```
- **Flask:** The core web framework.
- **Flask-Limiter:** Manages rate limiting.
- **ProxyFix:** Ensures Flask works correctly behind reverse proxies.
- **time:** Provides timestamps.

### 2. **Rate Limiting Setup**
```python
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per minute"])
```
- **Limits:** 100 requests per minute per IP.

### 3. **HTTPS Enforcement**
```python
@app.before_request
def enforce_https():
    if request.headers.get('X-Forwarded-Proto', 'http') != 'https':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
```
- Redirects HTTP requests to HTTPS.

### 4. **Security Headers**
```python
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```
- **Content Security Policy:** Restricts content sources.
- **Clickjacking Protection:** Prevents embedding in iframes.
- **XSS Protection:** Mitigates reflected XSS attacks.

### 5. **HTML Template for Endpoints**
```python
template = """..."""
```
- Provides a simple, responsive design for status messages.

### 6. **Endpoints**
```python
@app.route("/status", methods=["GET"])
def status():
    return render_template_string(template, title="Status", message="Zayzoon rocking here!", timestamp=int(time.time()))

@app.route("/health", methods=["GET"])
def health():
    return render_template_string(template, title="Health Check", message="Status: Healthy", timestamp=int(time.time()))
```
- **`/status`:** Displays the status message.
- **`/health`:** Displays the health status.

### 7. **Error Handling**
```python
@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify(error="Too many requests. Please try again later."), 429

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error="Endpoint not found."), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify(error="An unexpected error occurred."), 500
```
- Custom error messages for rate limit violations, missing pages, and internal server errors.

### 8. **Application Launch**
```python
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=443, ssl_context=('cert.pem', 'key.pem'))
```
- **Host:** `127.0.0.1` for local binding.
- **Port:** `443` for secure HTTPS traffic.
- **SSL Context:** Uses `cert.pem` and `key.pem` for SSL encryption.

## Deployment Notes

1. **SSL/TLS Certificates:** Ensure `cert.pem` and `key.pem` are valid.
2. **Permissions:** Running on port 443 may require elevated privileges.
3. **Reverse Proxy (Optional):** For production, consider using NGINX for better performance and security.

## Conclusion

This Flask application is designed with security and simplicity in mind, making it suitable for both development and production environments. Its modular structure allows easy customization and scalability.

