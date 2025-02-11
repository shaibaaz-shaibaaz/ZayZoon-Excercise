# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app listens on (8443 by default)
EXPOSE 8443

# Start the application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8443", "app:app"]
