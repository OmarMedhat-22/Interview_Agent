@echo off
REM Interview Agent API Server
REM Usage: run_api.bat [port]

set PORT=%1
if "%PORT%"=="" set PORT=8000

echo Starting Interview Agent API on port %PORT%...
echo Press Ctrl+C to stop
echo.

conda run -n interview_agent uvicorn app.main:app --host 0.0.0.0 --port %PORT% --reload
