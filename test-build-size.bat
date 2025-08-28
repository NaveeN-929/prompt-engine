@echo off
echo ====================================
echo Docker Image Size Comparison Test
echo ====================================

echo.
echo Building Autonomous Agent with Multi-stage Dockerfile...
cd autonomous-agent
docker build --target runtime -t paytechneodemo/autonomous-agent:optimized .
cd ..

echo.
echo ====================================
echo Image Size Comparison:
echo ====================================
docker images | findstr "paytechneodemo/autonomous-agent"

echo.
echo Detailed size information:
docker inspect paytechneodemo/autonomous-agent:optimized --format="{{.Size}}" > temp_size.txt
set /p image_size=<temp_size.txt
del temp_size.txt

echo Image size: %image_size% bytes
echo.

rem Convert bytes to MB
set /a size_mb=%image_size% / 1024 / 1024
echo Image size: %size_mb% MB

echo.
echo ====================================
echo Build complete! 
echo Optimized image should be under 1GB
echo ====================================

pause
