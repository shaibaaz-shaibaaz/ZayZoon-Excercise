# Base image
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the non-privileged port
EXPOSE 8443

# Run Gunicorn bound to port 8443
CMD ["gunicorn", "-b", "0.0.0.0:8443", "app:app"]
