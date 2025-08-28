@echo off
echo ====================================
echo Building and Pushing Docker Images
echo Repository: paytechneodemo
echo ====================================

echo.
echo 1. Logging into DockerHub...
docker login

echo.
echo 2. Building Prompt Engine Image (Multi-stage build)...
docker build --target runtime -t paytechneodemo/prompt-engine:latest .
docker tag paytechneodemo/prompt-engine:latest paytechneodemo/prompt-engine:v2.0.0

echo.
echo 3. Building Autonomous Agent Image (Multi-stage build)...
cd autonomous-agent
docker build --target runtime -t paytechneodemo/autonomous-agent:latest .
docker tag paytechneodemo/autonomous-agent:latest paytechneodemo/autonomous-agent:v2.0.0
cd ..

echo.
echo 4. Pushing Prompt Engine Images...
docker push paytechneodemo/prompt-engine:latest
docker push paytechneodemo/prompt-engine:v2.0.0

echo.
echo 5. Pushing Autonomous Agent Images...
docker push paytechneodemo/autonomous-agent:latest
docker push paytechneodemo/autonomous-agent:v2.0.0

echo.
echo ====================================
echo Build and Push Complete!
echo ====================================
echo.
echo Images available at:
echo - paytechneodemo/prompt-engine:latest
echo - paytechneodemo/prompt-engine:v2.0.0
echo - paytechneodemo/autonomous-agent:latest
echo - paytechneodemo/autonomous-agent:v2.0.0
echo.
echo Verifying images...
docker images | findstr paytechneodemo

pause
