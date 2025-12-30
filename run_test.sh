#!/bin/bash

# Interview Agent Test Runner
# Usage: 
#   ./run_test.sh                    - Show help
#   ./run_test.sh -i                 - Interactive menu
#   ./run_test.sh -m claude-4 0      - Use claude-4, run test 0
#   ./run_test.sh -o -m claude-4     - Save to file, run all tests

echo "Interview Agent Test Runner"
echo "==========================="
echo ""

conda run -n interview_agent python test_api.py "$@"
