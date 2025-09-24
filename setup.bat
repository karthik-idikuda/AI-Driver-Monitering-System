@echo off
REM Setup script for Driver Monitoring System on Windows

echo Setting up Driver Monitoring System...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is required but not installed. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist "data\logs" mkdir data\logs
if not exist "data\known_faces" mkdir data\known_faces
if not exist "data\screenshots" mkdir data\screenshots
if not exist "data\recordings" mkdir data\recordings  
if not exist "data\alerts" mkdir data\alerts
if not exist "models" mkdir models

REM Download models
echo Downloading required models...
python download_models.py

echo.
echo Setup completed successfully!
echo.
echo To run the application:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run GUI mode: python main.py --mode gui
echo 3. Or run console mode: python main.py --mode console
echo.
echo For help: python main.py --help

pause
