@echo off
echo 🚀 Setting up Autonomous Financial Analysis Agent
echo ============================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python is available
echo.

REM Install dependencies
echo 🔧 Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    echo.
    echo 💡 Try running this manually:
    echo    python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    if exist env.template (
        copy env.template .env >nul
        echo ✅ Created .env file from template
    ) else (
        echo ⚠️ env.template not found, skipping .env creation
    )
) else (
    echo ✅ .env file already exists
)

REM Create logs directory
if not exist logs mkdir logs
echo ✅ Created logs directory

echo.
echo ============================================================
echo ✅ Setup completed successfully!
echo.
echo 🚀 To start the agent:
echo    python run_agent.py
echo.
echo 🧪 To test the agent:
echo    python test_agent.py
echo.
echo 🌐 Web interface will be available at:
echo    http://localhost:5001
echo.
echo 📝 Remember to:
echo    1. Edit .env file with your configuration
echo    2. Ensure your prompt-engine is running on port 5000
echo    3. Ensure Ollama/LLM service is available
echo.
pause
echo 🚀 Setting up Autonomous Financial Analysis Agent
echo ============================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python is available
echo.

REM Install dependencies
echo 🔧 Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    echo.
    echo 💡 Try running this manually:
    echo    python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    if exist env.template (
        copy env.template .env >nul
        echo ✅ Created .env file from template
    ) else (
        echo ⚠️ env.template not found, skipping .env creation
    )
) else (
    echo ✅ .env file already exists
)

REM Create logs directory
if not exist logs mkdir logs
echo ✅ Created logs directory

echo.
echo ============================================================
echo ✅ Setup completed successfully!
echo.
echo 🚀 To start the agent:
echo    python run_agent.py
echo.
echo 🧪 To test the agent:
echo    python test_agent.py
echo.
echo 🌐 Web interface will be available at:
echo    http://localhost:5001
echo.
echo 📝 Remember to:
echo    1. Edit .env file with your configuration
echo    2. Ensure your prompt-engine is running on port 5000
echo    3. Ensure Ollama/LLM service is available
echo.
pause