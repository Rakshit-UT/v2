@echo off
echo 🚀 HackRx 6.0 - LLM Query Retrieval System Deployment
echo =================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if all required files exist
if not exist "main.py" (
    echo ❌ Required file main.py not found!
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ Required file requirements.txt not found!
    pause
    exit /b 1
)

if not exist "index.html" (
    echo ❌ Required file index.html not found!
    pause
    exit /b 1
)

echo ✅ All required files found

REM Start the application
echo 🎯 Starting the application...
echo 📡 API will be available at: http://localhost:8000
echo 🌐 Web interface will be available at: http://localhost:8000
echo 📋 API documentation will be available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run with uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
