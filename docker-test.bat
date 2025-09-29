@echo off
REM Docker Deployment Test Script for Windows
REM This script tests that all Docker services are working correctly

echo =========================================
echo HiLabs Docker Deployment Test
echo =========================================
echo.

REM Check if Docker is installed
echo 1. Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker is installed
    docker --version
) else (
    echo [ERROR] Docker is not installed
    exit /b 1
)

echo.

REM Check if Docker Compose is installed
echo 2. Checking Docker Compose installation...
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker Compose is installed
    docker-compose --version
) else (
    echo [ERROR] Docker Compose is not installed
    exit /b 1
)

echo.

REM Build Docker images
echo 3. Building Docker images...
echo This may take a few minutes on first run...
docker-compose build
if %errorlevel% equ 0 (
    echo [OK] Docker images built successfully
) else (
    echo [ERROR] Failed to build Docker images
    exit /b 1
)

echo.

REM Start services
echo 4. Starting services...
docker-compose up -d
if %errorlevel% equ 0 (
    echo [OK] Services started successfully
) else (
    echo [ERROR] Failed to start services
    exit /b 1
)

echo.

REM Wait for services to be ready
echo 5. Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check backend health
echo 6. Checking backend health...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is healthy
) else (
    echo [WARNING] Backend health check failed, retrying...
    timeout /t 10 /nobreak >nul
    curl -s http://localhost:8000/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Backend is healthy after retry
    ) else (
        echo [ERROR] Backend is not responding
    )
)

echo.

REM Check frontend
echo 7. Checking frontend...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend is accessible
) else (
    echo [WARNING] Frontend may not be ready yet
)

echo.

REM Check API documentation
echo 8. Checking API documentation...
curl -s http://localhost:8000/docs >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] API documentation is accessible
) else (
    echo [WARNING] API documentation not accessible
)

echo.

REM Display service status
echo 9. Service Status:
docker-compose ps

echo.
echo =========================================
echo Deployment Test Complete!
echo =========================================
echo.
echo Access your application at:
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo To view logs: docker-compose logs -f
echo To stop services: docker-compose down
echo.
pause
