#!/bin/bash

# AWS Lambda Deployment Script using SAM
# Prerequisites: AWS CLI, SAM CLI installed

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Interview Agent Lambda Deployment ==="
echo "Project: $PROJECT_DIR"
echo ""

# Check prerequisites
if ! command -v sam &> /dev/null; then
    echo "ERROR: SAM CLI not installed"
    echo "Install: pip install aws-sam-cli"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "ERROR: AWS CLI not installed"
    exit 1
fi

cd "$SCRIPT_DIR"

# Get API keys from environment or prompt
GEMINI_KEY=${GEMINI_API_KEY:-}
ANTHROPIC_KEY=${ANTHROPIC_API_KEY:-}

if [ -z "$GEMINI_KEY" ]; then
    read -p "Enter GEMINI_API_KEY: " GEMINI_KEY
fi

if [ -z "$ANTHROPIC_KEY" ]; then
    read -p "Enter ANTHROPIC_API_KEY (or press Enter to skip): " ANTHROPIC_KEY
fi

# Build
echo ""
echo "Building Lambda package..."
sam build --template-file template.yaml

# Deploy
echo ""
echo "Deploying to AWS..."
sam deploy \
    --parameter-overrides "GeminiApiKey=$GEMINI_KEY AnthropicApiKey=$ANTHROPIC_KEY" \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset

echo ""
echo "=== Deployment Complete ==="
echo ""

# Get API URL
API_URL=$(aws cloudformation describe-stacks \
    --stack-name interview-agent-api \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text 2>/dev/null || echo "")

if [ -n "$API_URL" ]; then
    echo "API URL: $API_URL"
    echo ""
    echo "Test commands:"
    echo "  curl ${API_URL}health"
    echo "  curl -X POST ${API_URL}evaluate -H 'Content-Type: application/json' -d '{\"question\":\"Tell me about yourself\",\"answer\":\"I am a developer\",\"job_description\":\"Engineer\"}'"
fi
