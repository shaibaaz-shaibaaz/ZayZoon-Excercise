# Zayzoon SRE Exercise

## **Project Overview**

This project is a simple **Flask-based web server** designed to demonstrate infrastructure deployment, containerization, and CI/CD automation using **AWS services** and **GitHub Actions**. The application exposes RESTful endpoints and is deployed on **Amazon ECS Fargate** with infrastructure managed through **AWS CloudFormation**.

---

## **Features**

- **REST API Endpoints:**
  - `/status` - Returns a static message with a timestamp.
  - `/health` - Returns the health status of the application.

- **Containerization:**
  - Dockerized Flask application.

- **Infrastructure as Code (IaC):**
  - Managed using AWS CloudFormation.

- **CI/CD Pipeline:**
  - Automated deployment using GitHub Actions.

- **Monitoring & Observability:**
  - Integrated with Amazon CloudWatch.

---

## **Technology Stack**

- **Backend:** Python, Flask
- **Containerization:** Docker
- **Cloud:** AWS (ECS Fargate, ECR, CloudFormation, CloudWatch)
- **CI/CD:** GitHub Actions

---

## **Prerequisites**

- **AWS CLI** configured with the necessary permissions.
- **Docker** installed.
- **GitHub Repository** with GitHub Actions enabled.

---

## **Deployment Instructions**

### **1. Clone the Repository:**
```bash
git clone <repository-url>
cd <repository-directory>
```

### **2. Build the Docker Image:**
```bash
docker build -t zayzoon-flask-app app/
```

### **3. Push the Image to Amazon ECR:**
```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

docker tag zayzoon-flask-app:latest <account-id>.dkr.ecr.<region>.amazonaws.com/zayzoon-flask-app:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/zayzoon-flask-app:latest
```

### **4. Deploy Infrastructure with CloudFormation:**
```bash
aws cloudformation deploy --template-file infra/cloudformation.yaml --stack-name zayzoon-stack --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
```

### **5. Trigger CI/CD Pipeline:**
- Push changes to `dev` or `main` branch to trigger GitHub Actions.
- The CI/CD pipeline will automatically:
  - Build the Docker image.
  - Push the image to ECR.
  - Deploy updates to ECS.

---

## **API Endpoints**

### **1. `/status` Endpoint:**
- **Method:** GET
- **Response:**
```json
{
  "message": "Zayzoon rocking here!",
  "timestamp": 1729818204
}
```

### **2. `/health` Endpoint:**
- **Method:** GET
- **Response:**
```json
{
  "status": "healthy",
  "timestamp": 1729818204
}
```

---

## **Monitoring & Observability**

- Logs and metrics are collected via **Amazon CloudWatch**.
- Alerts are configured based on resource usage thresholds.

---

## **Cleanup Instructions**

To delete the deployed resources:
```bash
aws cloudformation delete-stack --stack-name zayzoon-stack
```
Ensure that ECR images are manually cleaned up if needed.

---