#!/bin/bash

set -e

# Configuration
AWS_REGION="us-west-2"

ECR_REPOSITORY_NAME="rules-repository"
IMAGE_TAG="latest"

echo "🚀 Starting deployment of Rules Service..."

# Configure AWS credentials
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$AWS_REGION

echo "📋 AWS credentials configured"

# Get ECR repository URL
ECR_REPOSITORY_URL=$(aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --query 'repositories[0].repositoryUri' --output text 2>/dev/null || echo "")

if [ -z "$ECR_REPOSITORY_URL" ]; then
    echo "❌ ECR repository not found. Please run 'terraform apply' first to create the infrastructure."
    exit 1
fi

echo "📦 ECR Repository: $ECR_REPOSITORY_URL"

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY_URL

# Build Docker image
echo "🏗️ Building Docker image..."
docker build -t $ECR_REPOSITORY_NAME:$IMAGE_TAG .

# Tag image for ECR
echo "🏷️ Tagging image for ECR..."
docker tag $ECR_REPOSITORY_NAME:$IMAGE_TAG $ECR_REPOSITORY_URL:$IMAGE_TAG

# Push image to ECR
echo "⬆️ Pushing image to ECR..."
docker push $ECR_REPOSITORY_URL:$IMAGE_TAG

echo "✅ Image pushed successfully!"

# Update ECS service to use new image
echo "🔄 Updating ECS service..."
aws ecs update-service --cluster rules-cluster --service rules-service --force-new-deployment

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Service will be available at:"
echo "   - External: http://$(aws elbv2 describe-load-balancers --names rules-alb --query 'LoadBalancers[0].DNSName' --output text)"
echo "   - Internal: rules.barbershop.local"
echo ""
echo "📊 Monitor deployment:"
echo "   aws ecs describe-services --cluster rules-cluster --services rules-service"
