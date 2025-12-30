# AWS Deployment Guide

## Option 1: AWS App Runner (Easiest)

### Prerequisites
- AWS CLI configured
- Docker installed

### Steps

1. **Push image to ECR:**
```bash
./deploy/ecr-push.sh us-east-1
```

2. **Create App Runner service:**
   - Go to AWS Console → App Runner
   - Create Service → Container registry → Amazon ECR
   - Select your image
   - Set port to 8000
   - Add environment variables:
     - `MODEL`: gemini/gemini-2.5-flash
     - `GEMINI_API_KEY`: your-key
     - `ANTHROPIC_API_KEY`: your-key

**Cost:** ~$5-15/month for low traffic

---

## Option 2: AWS EC2 (Full Control)

### Steps

1. **Launch EC2 instance:**
   - Amazon Linux 2 or Ubuntu
   - t2.micro (free tier) or t3.small
   - Security group: Allow ports 22 (SSH), 8000 (API)

2. **SSH and deploy:**
```bash
ssh -i your-key.pem ec2-user@<EC2_PUBLIC_IP>

# Copy files via SCP
scp -i your-key.pem -r . ec2-user@<EC2_PUBLIC_IP>:~/Interview_Agent

# Run deployment
cd Interview_Agent
chmod +x deploy/deploy-ec2.sh
./deploy/deploy-ec2.sh
```

3. **Set environment variables:**
```bash
export GEMINI_API_KEY=your-key
export ANTHROPIC_API_KEY=your-key
```

**Cost:** ~$8-15/month (t3.micro)

---

## Option 3: AWS Lambda (Serverless)

For Lambda deployment, install Mangum:

```bash
pip install mangum
```

Add to `app/main.py`:
```python
from mangum import Mangum
handler = Mangum(app)
```

Then use AWS SAM or Serverless Framework.

**Cost:** Pay per request (~$0.20 per 1M requests)

---

## Quick Test After Deployment

```bash
# Health check
curl https://your-api-url/health

# Evaluate
curl -X POST https://your-api-url/evaluate \
  -H "Content-Type: application/json" \
  -d '{"question":"Tell me about yourself","answer":"I am a developer...","job_description":"Software Engineer"}'
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| MODEL | No | Default: gemini/gemini-2.5-flash |
| GEMINI_API_KEY | Yes* | Google Gemini API key |
| ANTHROPIC_API_KEY | Yes* | Anthropic Claude API key |

*At least one API key required based on model used.
