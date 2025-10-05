# HiLabs AIQuest - Contract Analysis System Launcher
# PowerShell Script with Advanced Features

param(
    [switch]$Production,
    [switch]$Debug,
    [switch]$SkipInstall,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

# Set console encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Colors and styling
$Host.UI.RawUI.WindowTitle = "HiLabs AIQuest - Contract Analysis System"
$Host.UI.RawUI.BackgroundColor = "Black"
Clear-Host

function Write-Header {
    Write-Host ""
    Write-Host "    ╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "    ║     HiLabs AIQuest - Contract Analysis System            ║" -ForegroundColor Cyan
    Write-Host "    ║     Professional Contract Intelligence Platform          ║" -ForegroundColor Cyan
    Write-Host "    ╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param($Step, $Total, $Message)
    Write-Host "[$Step/$Total] $Message" -ForegroundColor Yellow
    Write-Host ("─" * 60) -ForegroundColor DarkGray
}

function Write-Success {
    param($Message)
    Write-Host "    ✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param($Message)
    Write-Host "    ✗ $Message" -ForegroundColor Red
}

function Write-Warning {
    param($Message)
    Write-Host "    ⚠ $Message" -ForegroundColor Yellow
}

function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
}

function Test-Port {
    param($Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    return $connection.TcpTestSucceeded
}

function Stop-ProcessOnPort {
    param($Port)
    $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($process) {
        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
}

# Display header
Write-Header

# Check prerequisites
Write-Step 1 6 "Checking Prerequisites..."

# Check Python
if (-not (Test-Command "python")) {
    Write-Error "Python is not installed or not in PATH"
    Write-Host "    Please install Python 3.8+ from https://python.org" -ForegroundColor White
    Read-Host "Press Enter to exit"
    exit 1
}
$pythonVersion = python --version 2>&1
Write-Success "Python installed: $pythonVersion"

# Check Node.js
if (-not (Test-Command "node")) {
    Write-Error "Node.js is not installed or not in PATH"
    Write-Host "    Please install Node.js 14+ from https://nodejs.org" -ForegroundColor White
    Read-Host "Press Enter to exit"
    exit 1
}
$nodeVersion = node --version
Write-Success "Node.js installed: $nodeVersion"

# Check npm
if (-not (Test-Command "npm")) {
    Write-Error "npm is not installed"
    Write-Host "    Please reinstall Node.js from https://nodejs.org" -ForegroundColor White
    Read-Host "Press Enter to exit"
    exit 1
}
$npmVersion = npm --version
Write-Success "npm installed: $npmVersion"

Write-Host ""

# Backend setup
if (-not $FrontendOnly) {
    Write-Step 2 6 "Setting up Backend..."
    
    Set-Location -Path "Backend"
    
    if (-not (Test-Path "requirements.txt")) {
        Write-Error "requirements.txt not found in Backend folder"
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Create virtual environment
    if (-not (Test-Path "venv")) {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Gray
        python -m venv venv
        Write-Success "Virtual environment created"
    }
    
    # Activate virtual environment and install packages
    if (-not $SkipInstall) {
        Write-Host "Installing Python packages..." -ForegroundColor Gray
        & "venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
        & "venv\Scripts\pip.exe" install -r requirements.txt --quiet
        Write-Success "Backend dependencies installed"
    } else {
        Write-Warning "Skipping backend dependency installation"
    }
    
    Write-Host ""
    Write-Step 3 6 "Starting Backend Server..."
    
    # Stop any existing process on port 5000
    Stop-ProcessOnPort -Port 5000
    
    # Start backend server
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        & "venv\Scripts\python.exe" main.py
    }
    
    Write-Host "Waiting for backend to initialize..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    if (Test-Port -Port 5000) {
        Write-Success "Backend server started on http://localhost:5000"
    } else {
        Write-Warning "Backend may still be starting up..."
    }
    
    Set-Location -Path ".."
}

Write-Host ""

# Frontend setup
if (-not $BackendOnly) {
    Write-Step 4 6 "Setting up Frontend..."
    
    Set-Location -Path "hilabs-dash"
    
    if (-not (Test-Path "package.json")) {
        Write-Error "package.json not found in hilabs-dash folder"
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    if (-not $SkipInstall) {
        if (Test-Path "node_modules") {
            Write-Host "Updating Node.js packages..." -ForegroundColor Gray
            npm update --silent
        } else {
            Write-Host "Installing Node.js packages (this may take a few minutes)..." -ForegroundColor Gray
            npm install --silent
        }
        Write-Success "Frontend dependencies installed"
    } else {
        Write-Warning "Skipping frontend dependency installation"
    }
    
    Write-Host ""
    Write-Step 5 6 "Syncing Results..."
    
    if (Test-Path "copy-results.js") {
        node copy-results.js
        Write-Success "Results synchronized"
    } else {
        Write-Warning "copy-results.js not found, skipping sync"
    }
    
    Write-Host ""
    
    if ($Production) {
        Write-Step 6 6 "Building Frontend for Production..."
        npm run build --silent
        Write-Success "Frontend built for production"
        
        # You could serve the build folder with a static server here
        Write-Host ""
        Write-Host "Production build created in hilabs-dash/build" -ForegroundColor Green
        Write-Host "You can serve it with any static file server" -ForegroundColor Gray
    } else {
        Write-Step 6 6 "Starting Frontend Dashboard..."
        
        # Stop any existing process on port 3000
        Stop-ProcessOnPort -Port 3000
        
        Write-Host ""
        Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "    ┌─────────────────────────────────────────────────────────┐" -ForegroundColor White
        Write-Host "    │  Backend API:     http://localhost:5000                │" -ForegroundColor White
        Write-Host "    │  Frontend:        http://localhost:3000                │" -ForegroundColor White
        Write-Host "    │                                                         │" -ForegroundColor White
        Write-Host "    │  The dashboard will open in your browser automatically │" -ForegroundColor White
        Write-Host "    │                                                         │" -ForegroundColor White
        Write-Host "    │  Press Ctrl+C to stop all services                     │" -ForegroundColor White
        Write-Host "    └─────────────────────────────────────────────────────────┘" -ForegroundColor White
        Write-Host ""
        
        # Start frontend
        npm start
    }
}

# Cleanup on exit
Write-Host ""
Write-Host "Shutting down services..." -ForegroundColor Yellow

if ($backendJob) {
    Stop-Job -Job $backendJob -Force
    Remove-Job -Job $backendJob -Force
}

Stop-ProcessOnPort -Port 5000
Stop-ProcessOnPort -Port 3000

Write-Success "All services stopped"
Read-Host "Press Enter to exit"
