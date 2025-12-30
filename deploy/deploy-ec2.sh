#!/bin/bash

# AWS EC2 Deployment Script
# Run this ON the EC2 instance after SSH

set -e

echo "=== Interview Agent EC2 Deployment ==="

# Update system
sudo yum update -y || sudo apt-get update -y

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo yum install -y docker || sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Clone or pull latest code
if [ -d "Interview_Agent" ]; then
    cd Interview_Agent
    git pull
else
    echo "Please copy your project files to this directory"
    exit 1
fi

# Create .env file
echo "Creating .env file..."
cat > .env << EOF
MODEL=gemini/gemini-2.5-flash
GEMINI_API_KEY=${GEMINI_API_KEY:-your_gemini_key_here}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-your_anthropic_key_here}
EOF

# Build and run
echo "Building and starting container..."
docker-compose up -d --build

echo ""
echo "=== Deployment Complete ==="
echo "API available at: http://$(curl -s ifconfig.me):8000"
echo "Health check: http://$(curl -s ifconfig.me):8000/health"
