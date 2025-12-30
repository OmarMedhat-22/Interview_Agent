#!/bin/bash

# Push Docker image to AWS ECR
# Usage: ./ecr-push.sh <aws-region> <aws-account-id>

REGION=${1:-us-east-1}
ACCOUNT_ID=${2:-$(aws sts get-caller-identity --query Account --output text)}
REPO_NAME="interview-agent"
IMAGE_TAG="latest"

echo "=== Pushing to ECR ==="
echo "Region: $REGION"
echo "Account: $ACCOUNT_ID"
echo "Repository: $REPO_NAME"
echo ""

# Create ECR repository if not exists
aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION 2>/dev/null || \
    aws ecr create-repository --repository-name $REPO_NAME --region $REGION

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build image
echo "Building Docker image..."
docker build -t $REPO_NAME:$IMAGE_TAG .

# Tag for ECR
docker tag $REPO_NAME:$IMAGE_TAG $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

# Push to ECR
echo "Pushing to ECR..."
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

echo ""
echo "=== Push Complete ==="
echo "Image: $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"
