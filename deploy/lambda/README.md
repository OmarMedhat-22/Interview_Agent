# AWS Lambda Deployment

## Prerequisites

1. **AWS CLI** - configured with credentials
   ```bash
   aws configure
   ```

2. **AWS SAM CLI** - install:
   ```bash
   pip install aws-sam-cli
   ```

3. **Docker** - required for building Lambda packages

## Quick Deploy

### Windows
```cmd
cd deploy\lambda
set GEMINI_API_KEY=your-gemini-key
set ANTHROPIC_API_KEY=your-claude-key
deploy.bat
```

### Linux/Mac
```bash
cd deploy/lambda
export GEMINI_API_KEY=your-gemini-key
export ANTHROPIC_API_KEY=your-claude-key
chmod +x deploy.sh
./deploy.sh
```

## Manual Deploy

```bash
# 1. Build
cd deploy/lambda
sam build --use-container

# 2. Deploy (first time - guided)
sam deploy --guided

# 3. Deploy (subsequent)
sam deploy --parameter-overrides "GeminiApiKey=xxx AnthropicApiKey=yyy"
```

## Test Your API

After deployment, you'll get an API URL like:
```
https://abc123.execute-api.us-east-1.amazonaws.com/
```

Test it:
```bash
# Health check
curl https://YOUR_API_URL/health

# Evaluate
curl -X POST https://YOUR_API_URL/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tell me about yourself",
    "answer": "I am a software engineer with 5 years experience",
    "job_description": "Senior Developer"
  }'
```

## Costs

- **Lambda**: ~$0.20 per 1M requests
- **API Gateway**: ~$1.00 per 1M requests
- **Free Tier**: 1M Lambda requests/month free

## Cleanup

Delete the stack:
```bash
sam delete --stack-name interview-agent-api
```

## Troubleshooting

### Timeout errors
Increase timeout in `template.yaml`:
```yaml
Timeout: 180  # seconds
```

### Memory errors
Increase memory:
```yaml
MemorySize: 1024  # MB
```

### View logs
```bash
sam logs -n InterviewAgentFunction --stack-name interview-agent-api --tail
```
