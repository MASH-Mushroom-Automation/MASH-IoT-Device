@echo off
REM MASH IoT Device - Demo Mode Launcher
REM Runs the GUI with mock data for demonstration

cd /d "%~dp0touchscreen_ui"

echo ================================================================
echo   MASH IoT Device - DEMO MODE
echo ================================================================
echo.
echo   Running GUI with simulated data
echo   No backend or hardware required
echo.
echo   Press Ctrl+C to exit
echo ================================================================
echo.

python main.py

pause
