@echo off
title NEXUS - Environment Setup
echo ========================================================
echo   NEXUS | Green AI Energy Optimization Setup
echo ========================================================
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)
python --version

echo.
echo [2/3] Installing required packages from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [3/3] Verifying SQLite database and ML models...
python -c "import sqlite3, joblib; from pathlib import Path; print('Database ready:', Path('database/energy.db').exists()); print('Model ready:', Path('models/energy_model.pkl').exists())"

echo.
echo ========================================================
echo   SETUP COMPLETED SUCCESSFULLY!
echo   You can now double-click 'run.bat' to start the app.
echo ========================================================
echo.
pause
