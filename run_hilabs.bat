@echo off
setlocal enabledelayedexpansion

:: Set console colors
color 0A

:: ASCII Art Header
echo.
echo    ╔═══════════════════════════════════════════════════════════╗
echo    ║     HiLabs AIQuest - Contract Analysis System            ║
echo    ║     Professional Contract Intelligence Platform          ║
echo    ╔═══════════════════════════════════════════════════════════╝
echo.

:: Check Python installation
echo [SETUP] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo    ✗ ERROR: Python is not installed or not in PATH
    echo    Please install Python 3.8 or higher from https://python.org
    echo.
    pause
    exit /b 1
)
python --version

:: Check Node.js installation
echo [SETUP] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo    ✗ ERROR: Node.js is not installed or not in PATH
    echo    Please install Node.js 14+ from https://nodejs.org
    echo.
    pause
    exit /b 1
)
node --version

:: Check npm installation
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo    ✗ ERROR: npm is not installed
    echo    Please reinstall Node.js from https://nodejs.org
    echo.
    pause
    exit /b 1
)
echo [SETUP] npm version: 
npm --version

echo.
echo ═══════════════════════════════════════════════════════════════
echo.

:: Install Backend Dependencies
echo [1/5] Installing Backend Dependencies...
echo ───────────────────────────────────────────────────────────────
cd Backend
if not exist "requirements.txt" (
    color 0C
    echo    ✗ ERROR: requirements.txt not found in Backend folder
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

:: Install requirements
echo Installing Python packages...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo    ⚠ WARNING: Some Python packages may have failed to install
    echo    Attempting to continue...
)

echo    ✓ Backend dependencies installed
echo.

:: Start Backend Server
echo [2/5] Starting Backend Server...
echo ───────────────────────────────────────────────────────────────

:: Kill any existing Python processes on port 5000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Start backend in new window
start "HiLabs Backend Server" /min cmd /c "cd /d %cd% && call venv\Scripts\activate.bat && python main.py"

:: Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

:: Check if backend is running
curl -s http://localhost:5000 >nul 2>&1
if %errorlevel% neq 0 (
    echo    ⚠ Backend may still be starting up...
) else (
    echo    ✓ Backend server started successfully
)
echo.

:: Install Frontend Dependencies
echo [3/5] Installing Frontend Dependencies...
echo ───────────────────────────────────────────────────────────────
cd ..\hilabs-dash

if not exist "package.json" (
    color 0C
    echo    ✗ ERROR: package.json not found in hilabs-dash folder
    pause
    exit /b 1
)

:: Check if node_modules exists and is recent
if exist "node_modules" (
    echo Node modules already installed, checking for updates...
    call npm update >nul 2>&1
) else (
    echo Installing Node.js packages (this may take a few minutes)...
    call npm install >nul 2>&1
)

if %errorlevel% neq 0 (
    color 0E
    echo    ⚠ WARNING: Some npm packages may have failed to install
    echo    Attempting to continue...
) else (
    echo    ✓ Frontend dependencies installed
)
echo.

:: Copy Results
echo [4/5] Syncing contract analysis results...
echo ───────────────────────────────────────────────────────────────
if exist "copy-results.js" (
    call node copy-results.js >nul 2>&1
    if %errorlevel% eq 0 (
        echo    ✓ Results synchronized successfully
    ) else (
        echo    ⚠ Could not sync results (may not exist yet)
    )
) else (
    echo    ⚠ copy-results.js not found, skipping sync
)
echo.

:: Build Frontend (Optional - for production)
:: echo [5/5] Building Frontend for Production...
:: echo ───────────────────────────────────────────────────────────────
:: call npm run build >nul 2>&1
:: echo    ✓ Frontend built successfully
:: echo.

:: Start Frontend
echo [5/5] Starting Frontend Dashboard...
echo ═══════════════════════════════════════════════════════════════
echo.
echo    ┌─────────────────────────────────────────────────────────┐
echo    │  Backend API:     http://localhost:5000                │
echo    │  Frontend:        http://localhost:3000                │
echo    │                                                         │
echo    │  The dashboard will open in your browser automatically │
echo    │                                                         │
echo    │  Press Ctrl+C in this window to stop all services      │
echo    └─────────────────────────────────────────────────────────┘
echo.

:: Kill any existing Node processes on port 3000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Start frontend
npm start

:: Cleanup on exit
echo.
echo Shutting down services...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
echo Services stopped.
pause
