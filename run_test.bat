@echo off
REM Interview Agent Test Runner
REM Usage: 
REM   run_test.bat                    - Show help
REM   run_test.bat -i                 - Interactive menu
REM   run_test.bat -m claude-4 0      - Use claude-4, run test 0
REM   run_test.bat -o -m claude-4     - Save to file, run all tests

echo Interview Agent Test Runner
echo ===========================
echo.

conda run -n interview_agent python test_api.py %*
