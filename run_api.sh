#!/bin/bash

# Interview Agent API Server
# Usage: ./run_api.sh [port]

PORT=${1:-8000}

echo "Starting Interview Agent API on port $PORT..."
echo "Press Ctrl+C to stop"
echo ""

conda run -n interview_agent uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
