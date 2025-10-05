@echo off
echo ========================================
echo Building HiLabs Executable
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Install PyInstaller if not already installed
echo Installing build dependencies...
pip install -r build_requirements.txt

:: Build the executable
echo.
echo Building executable...
pyinstaller --onefile ^
    --name "HiLabs_Launcher" ^
    --icon="hilabs-dash\public\favicon.ico" ^
    --add-data "Backend;Backend" ^
    --add-data "hilabs-dash;hilabs-dash" ^
    --hidden-import "socket" ^
    --hidden-import "subprocess" ^
    --hidden-import "webbrowser" ^
    --hidden-import "pathlib" ^
    --console ^
    launcher.py

if %errorlevel% eq 0 (
    echo.
    echo ========================================
    echo Build successful!
    echo Executable created: dist\HiLabs_Launcher.exe
    echo ========================================
    
    :: Copy the executable to root directory
    copy dist\HiLabs_Launcher.exe . >nul
    echo.
    echo Executable copied to: HiLabs_Launcher.exe
) else (
    echo.
    echo ERROR: Build failed
)

echo.
pause
