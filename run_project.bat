@echo off
echo ========================================
echo HiLabs AIQuest - Contract Analysis System
echo ========================================
echo.

echo [1/4] Installing Backend Dependencies...
cd Backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    echo Please ensure Python 3.8+ is installed
    pause
    exit /b 1
)

echo.
echo [2/4] Starting Backend Server...
start /B cmd /c "python main.py"
timeout /t 3 /nobreak > nul

echo.
echo [3/4] Installing Frontend Dependencies...
cd ..\hilabs-dash
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Node dependencies
    echo Please ensure Node.js 14+ is installed
    pause
    exit /b 1
)

echo.
echo [4/4] Copying latest results to frontend...
call node copy-results.js

echo.
echo ========================================
echo Starting Frontend Dashboard...
echo ========================================
echo.
echo Backend API running at: http://localhost:5000
echo Frontend Dashboard will open at: http://localhost:3000
echo.
echo Press Ctrl+C to stop all services
echo.

npm start
