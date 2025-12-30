@echo off
REM AWS Lambda Deployment Script using SAM (Windows)
REM Prerequisites: AWS CLI, SAM CLI installed

echo === Interview Agent Lambda Deployment ===
echo.

REM Check SAM CLI
where sam >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: SAM CLI not installed
    echo Install: pip install aws-sam-cli
    exit /b 1
)

cd /d "%~dp0"

REM Get API keys
if "%GEMINI_API_KEY%"=="" (
    set /p GEMINI_API_KEY="Enter GEMINI_API_KEY: "
)

if "%ANTHROPIC_API_KEY%"=="" (
    set /p ANTHROPIC_API_KEY="Enter ANTHROPIC_API_KEY (or press Enter to skip): "
)

REM Build
echo.
echo Building Lambda package...
sam build --template-file template.yaml --use-container

REM Deploy
echo.
echo Deploying to AWS...
sam deploy --parameter-overrides "GeminiApiKey=%GEMINI_API_KEY% AnthropicApiKey=%ANTHROPIC_API_KEY%" --no-confirm-changeset --no-fail-on-empty-changeset

echo.
echo === Deployment Complete ===
echo.
echo Check AWS Console for API URL
pause
