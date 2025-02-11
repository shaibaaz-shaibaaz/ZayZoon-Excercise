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

# Add a health check
HEALTHCHECK CMD curl --fail https://localhost/health || exit 1

# Run the Flask app
CMD ["python", "app.py"]
