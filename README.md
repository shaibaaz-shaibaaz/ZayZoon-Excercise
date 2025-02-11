
Zayzoon Flask Application Documentation
This project demonstrates a containerized Flask web application with several key features, including rate limiting, HTTPS enforcement, security headers, and a multi-container ECS Fargate deployment that leverages Redis as a backend. The application is deployed using AWS CloudFormation, which provisions networking resources, an Application Load Balancer, and an ECS cluster with auto scaling. In addition, a CI/CD pipeline is implemented using GitHub Actions to automate deployments.

1. Project Overview
The project is composed of the following major parts:
Application Code (Flask):
 A Python Flask application that serves two endpoints (/status and /health), applies rate limiting (with a fallback to in-memory storage if Redis isn’t available), and enforces several security best practices.


Dockerfile:
 A Docker configuration that builds a slim Python 3.9 container, installs the required Python dependencies, copies the application code, and sets up Gunicorn to serve the Flask app.


CloudFormation Template:
 An AWS CloudFormation template that defines all necessary AWS resources (VPC, subnets, Internet Gateway, security groups, load balancer, ECS cluster and task definition, and auto scaling policies) to deploy the application on AWS ECS Fargate. The task definition contains two containers: the Flask application and a Redis container.


CI/CD Pipeline:
 A GitHub Actions workflow automates the process of building the Docker image, pushing it to Amazon ECR, and deploying the updated CloudFormation stack and ECS service.



2. Application Code Overview
2.1 Flask Application Structure
The main application code is built using Flask and includes the following features:
Endpoints:


/status:
 A simple UI that displays a status message ("Zayzoon rocking here! 🚀") along with a timestamp.
/health:
 A health check endpoint returning a status message ("Status: Healthy ✅") along with a timestamp. This endpoint is used by the load balancer for health checking and is exempt from HTTPS redirection.
Rate Limiting:
 Implemented using the Flask-Limiter package. The default limit is set to 100 requests per minute globally, with additional limits of 10 requests per minute on the /status and /health endpoints.


Redis Integration:
 If the REDIS_URL environment variable is set (and starts with redis://), the application attempts to connect to Redis for rate limiting. Otherwise, it falls back to an in-memory storage, which is not recommended for production.
Security Enhancements:


HTTPS Enforcement:
 A @before_request hook checks the X-Forwarded-Proto header and redirects HTTP requests to HTTPS (except for /health requests).
Security Headers:
 A @after_request hook adds several HTTP security headers, such as Content-Security-Policy, Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, and X-XSS-Protection.
Template Rendering:
 A simple HTML template is defined and rendered with dynamic content (title, message, and timestamp).


Error Handling:
 Custom error handlers return JSON responses for errors like 429 (Too Many Requests), 404 (Not Found), and 500 (Internal Server Error).


Proxy Support:
 The application uses ProxyFix to ensure correct behavior behind a reverse proxy (e.g., an AWS Load Balancer).


2.2 Code Highlights
Redis Connection Retry:
 When a Redis URL is provided, the application attempts to connect multiple times before exiting if unsuccessful.


Gunicorn Integration:
 Although the application can run with Flask’s built-in server for development, Gunicorn is used in production (as specified in the Dockerfile).



3. Dockerfile
The Dockerfile sets up the container environment for the Flask application:
Base Image:
 Uses python:3.9-slim for a lightweight Python environment.


Working Directory:
 Sets the working directory to /app.


Dependency Installation:
 Copies the requirements.txt file and installs the required Python dependencies with pip.


Application Code:
 Copies all application files into the container.


Port Exposure:
 Exposes port 8443 (which the Flask application listens on).


Container Startup:
 Uses Gunicorn as the WSGI server to run the Flask application on 0.0.0.0:8443.



4. CloudFormation Template Overview
The CloudFormation template automates the provisioning of the AWS infrastructure required for the application deployment.
4.1 Networking Components
VPC:
 A Virtual Private Cloud (CIDR: 10.0.0.0/16) with DNS support enabled.


Subnets:
 Two public subnets are created in different Availability Zones (10.0.1.0/24 and 10.0.2.0/24).


Internet Gateway & Routing:
 An Internet Gateway is attached to the VPC, with a route table that directs all outbound traffic (0.0.0.0/0) through it.


Security Groups:
 A security group is defined to allow inbound HTTPS (port 443) and ECS Task communication (port 8443) traffic.


4.2 Load Balancer and Target Group
Application Load Balancer (ALB):
 An internet-facing ALB is created in the public subnets with an HTTPS listener on port 443 that uses an SSL certificate provided via a parameter.


Target Group:
 Configured to route traffic to port 8443 on the ECS tasks, using the /health endpoint for health checks.


4.3 ECS Cluster, Task Definition, and Service
ECS Cluster:
 Hosts the ECS service that runs the application.


Task Definition:
 Defines a multi-container task with two containers:


Flask Application Container:
 Runs the Flask application using environment variables such as REDIS_URL and PORT. It also sends logs to AWS CloudWatch.
Redis Container:
 Provides Redis for rate limiting, with health checks (using redis-cli ping) and logging to CloudWatch.
ECS Service:
 The service runs on AWS Fargate with a desired count of two tasks and is integrated with the ALB through the target group.


4.4 Auto Scaling
Auto Scaling Role & Policies:
 An IAM role allows Application Auto Scaling to manage the ECS service.


Scaling Configuration:
 The ECS service is configured with a scalable target (minimum 1 task, maximum 4 tasks) and a target tracking scaling policy based on CPU utilization.



5. CI/CD Implementation with GitHub Actions
The CI/CD pipeline automates the process of building, pushing, and deploying the application to AWS. The following GitHub Actions workflow is triggered on pushes to the dev, main, or feature branches.
5.1 GitHub Actions Workflow
Below is the complete GitHub Actions YAML file that implements the CI/CD pipeline:
name: Deploy to AWS CloudFormation and ECS

on:
  push:
    branches:
      - dev
      - main
      - feature

permissions:
  id-token: write   
  contents: read     

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Code
      uses: actions/checkout@v3
      
    - name: Configure AWS Credentials
      uses: aws-actions/configure-aws-credentials@v4
      timeout-minutes: 2 
      with:
        role-to-assume: arn:aws:iam::083846066460:role/Zayzoon-Role
        aws-region: us-east-1
        role-session-name: GitHubActionsSession
        audience: sts.amazonaws.com

    - name: Set Environment Variable
      id: set-env
      run: |
        if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
          echo "ENV=prod" >> $GITHUB_ENV
        elif [[ "${{ github.ref }}" == "refs/heads/dev" ]]; then
          echo "ENV=dev" >> $GITHUB_ENV
        else
          echo "ENV=feature" >> $GITHUB_ENV
        fi

    - name: Deploy CloudFormation Stack
      run: |
        aws cloudformation deploy \
          --stack-name zayzoon-stack-${{ env.ENV }} \
          --template-file infra/cloudformation.yaml \
          --parameter-overrides Environment=${{ env.ENV }} \
          --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

    - name: Wait for CloudFormation Stack to Complete
      run: |
        aws cloudformation wait stack-create-complete --stack-name zayzoon-stack-${{ env.ENV }} || \
        aws cloudformation wait stack-update-complete --stack-name zayzoon-stack-${{ env.ENV }}

    - name: Build Docker Image
      run: |
        docker build -t zayzoon-flask-app:${{ github.sha }} -f app/Dockerfile app/

    - name: Login to Amazon ECR
      run: |
        aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 083846066460.dkr.ecr.us-east-1.amazonaws.com

    - name: Push Docker Image to ECR
      run: |
        docker tag zayzoon-flask-app:${{ github.sha }} 083846066460.dkr.ecr.us-east-1.amazonaws.com/zayzoon-flask-app:${{ github.sha }}
        docker push 083846066460.dkr.ecr.us-east-1.amazonaws.com/zayzoon-flask-app:${{ github.sha }}

    - name: Update ECS Service with New Image
      run: |
        CLUSTER_NAME=$(aws cloudformation describe-stacks --stack-name zayzoon-stack-${{ env.ENV }} --query "Stacks[0].Outputs[?OutputKey=='ECSClusterName'].OutputValue" --output text)
        SERVICE_NAME=$(aws cloudformation describe-stacks --stack-name zayzoon-stack-${{ env.ENV }} --query "Stacks[0].Outputs[?OutputKey=='ECSServiceName'].OutputValue" --output text)

        aws ecs update-service \
          --cluster $CLUSTER_NAME \
          --service $SERVICE_NAME \
          --force-new-deployment \
          --desired-count 1

5.2 Explanation of Workflow Steps
Triggering the Workflow:
 The workflow is set to run on any push to the dev, main, or feature branches.


Checkout Code:
 Uses the actions/checkout action to pull the repository code.


Configure AWS Credentials:
 Uses the aws-actions/configure-aws-credentials action to configure AWS credentials by assuming the specified IAM role. This allows the workflow to interact with AWS resources securely.


Set Environment Variable:
 Determines the deployment environment (prod, dev, or feature) based on the Git branch name and sets the ENV variable accordingly.


Deploy CloudFormation Stack:
 Deploys (or updates) the CloudFormation stack using the provided template file (infra/cloudformation.yaml). The stack name and environment parameter are set based on the ENV variable.


Wait for CloudFormation Stack Completion:
 The workflow waits for the CloudFormation stack to complete its create or update operation before proceeding.


Build Docker Image:
 Builds the Docker image for the Flask application, tagging it with the current Git commit SHA.


Login to Amazon ECR:
 Retrieves an authentication token and logs in to Amazon ECR so that the Docker image can be pushed.


Push Docker Image to ECR:
 Tags and pushes the built Docker image to the specified Amazon ECR repository.


Update ECS Service with New Image:
 Retrieves the ECS cluster and service names from the CloudFormation stack outputs and then forces a new deployment on ECS with the updated Docker image.



6. Deployment Instructions
6.1 Prerequisites
AWS Account:
 Ensure you have an AWS account with permissions to create ECS, VPC, ALB, IAM, CloudWatch, and other related resources.


Docker & AWS CLI:
 Install Docker for container builds and the AWS CLI for deploying CloudFormation templates.


GitHub Repository:
 Store the application code, Dockerfile, and CloudFormation template in a GitHub repository where the CI/CD workflow can run.


6.2 Building and Pushing the Docker Image (Locally)
Build the Docker image:

 docker build -t zayzoon-flask-app .


Tag the image for your ECR repository:

 docker tag zayzoon-flask-app:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/zayzoon-flask-app:latest


Push the image to ECR:

 docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/zayzoon-flask-app:latest


6.3 Deploying with CloudFormation
Prepare the CloudFormation template:
 Save the provided CloudFormation YAML into a file (e.g., infra/cloudformation.yaml).


Deploy the stack using AWS CLI:

 aws cloudformation deploy \
  --template-file infra/cloudformation.yaml \
  --stack-name zayzoon-stack-dev \
  --parameter-overrides Environment=dev \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM


Monitor the deployment:
 Use the AWS CloudFormation console or CLI to watch for successful resource creation. Once complete, outputs (such as the Load Balancer DNS name) will be available for accessing your application.



7. Security and Operational Considerations
HTTPS Enforcement & Security Headers:
 The application enforces HTTPS and applies several security headers to protect against common vulnerabilities.


Rate Limiting:
 Limits the number of requests per minute to prevent abuse of the service.


Logging & Monitoring:
 Both containers send logs to AWS CloudWatch for monitoring and troubleshooting.


Auto Scaling:
 The ECS service is configured with auto scaling to handle variable traffic loads.


CI/CD Automation:
 The GitHub Actions workflow automates building, testing, and deployment, ensuring that any changes pushed to the repository are rapidly and reliably deployed to production.



8. Conclusion
This project demonstrates a modern approach to building and deploying a microservice application with strong security, scalability, and operational best practices. By combining a Flask application with Docker, Gunicorn, AWS services (ECS Fargate, CloudFormation, ALB, etc.), and a CI/CD pipeline via GitHub Actions, the project showcases how to create a resilient, production-ready web service.
This documentation serves as a guide for developers and DevOps engineers to understand the architecture, deployment process, and CI/CD automation of the project. As the project evolves, consider extending the monitoring, logging, and testing strategies to further improve the deployment workflow and overall system resilience.


