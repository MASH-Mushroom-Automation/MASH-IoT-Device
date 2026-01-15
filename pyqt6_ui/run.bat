@echo off
REM MASH IoT Device - PyQt6 UI Launcher (Windows)

echo ╔══════════════════════════════════════════════╗
echo ║     MASH IoT Device - PyQt6 UI Launcher     ║
echo ╚══════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements if needed
echo Checking dependencies...
pip install -q -r requirements.txt
echo.

REM Launch application
echo Starting PyQt6 UI...
echo.
python main.py

pause
