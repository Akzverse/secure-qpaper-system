@echo off
echo ============================================================
echo   Secure Question Paper Management System
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Find virtual-environment Python (Windows Python uses Scripts; MSYS/Git Bash may use bin)
if exist "venv\Scripts\python.exe" (
    set "PYTHON=venv\Scripts\python.exe"
) else if exist "venv\bin\python.exe" (
    set "PYTHON=venv\bin\python.exe"
) else (
    set "PYTHON=python"
)

REM Install requirements
echo Installing dependencies...
%PYTHON% -m pip install -q -r requirements.txt

REM Initialize database and demo users
echo Initializing database and demo users...
%PYTHON% init_demo_users.py

REM Run the application
echo.
echo Starting application...
echo Access at: http://localhost:5000
echo.
%PYTHON% app.py

pause
