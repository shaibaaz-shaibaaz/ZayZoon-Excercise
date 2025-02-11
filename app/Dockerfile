# Base image
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and SSL certificates
COPY . .

# Fix permissions for SSL certificates
RUN chmod 644 certificate.pem private-key.pem

# Create a non-root user for security
RUN adduser --disabled-password appuser
USER appuser

# Expose HTTPS port
EXPOSE 443

# Run the Flask app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:443", "app:app", "--certfile=certificate.pem", "--keyfile=private-key.pem"]
