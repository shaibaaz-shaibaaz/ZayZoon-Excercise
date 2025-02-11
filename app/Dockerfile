# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a non-root user for security
RUN adduser --disabled-password appuser
USER appuser

# Expose HTTPS port
EXPOSE 443

# Run the Flask app with Gunicorn in production mode
CMD ["gunicorn", "-b", "0.0.0.0:443", "app:app", "--certfile=certificate.pem", "--keyfile=private-key.pem"]
