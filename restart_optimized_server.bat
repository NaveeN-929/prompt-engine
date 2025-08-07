@echo off
echo ===================================
echo Restarting Optimized RAG Agent
echo ===================================

echo Stopping existing Python processes...
taskkill /f /im python.exe 2>nul

echo Waiting for processes to stop...
timeout /t 2 /nobreak >nul

echo Changing to autonomous-agent directory...
cd /d "%~dp0autonomous-agent"

echo Starting optimized server (reduced API calls)...
python server_final.py

pause
