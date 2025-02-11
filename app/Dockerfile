# Base image
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8443

CMD ["gunicorn", "-b", "0.0.0.0:8443", "app:app", "--certfile=certificate.pem", "--keyfile=private-key.pem"]
