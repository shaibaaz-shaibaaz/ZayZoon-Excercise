# Base image
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify installation
RUN which gunicorn

COPY . .

RUN adduser --disabled-password appuser
USER appuser

EXPOSE 443

CMD ["gunicorn", "-b", "0.0.0.0:8443", "app:app", "--certfile=certificate.pem", "--keyfile=private-key.pem"]
