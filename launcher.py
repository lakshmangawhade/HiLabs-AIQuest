#!/usr/bin/env python3
"""
HiLabs AIQuest - Contract Analysis System Launcher
Executable launcher for the HiLabs application
"""

import os
import sys
import subprocess
import time
import socket
import signal
import webbrowser
import argparse
from pathlib import Path
import json
import shutil
from typing import Optional, Tuple

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Print application header"""
    print(f"\n{Colors.CYAN}")
    print("    ╔═══════════════════════════════════════════════════════════╗")
    print("    ║     HiLabs AIQuest - Contract Analysis System            ║")
    print("    ║     Professional Contract Intelligence Platform          ║")
    print("    ╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

def print_step(step: int, total: int, message: str):
    """Print step information"""
    print(f"{Colors.WARNING}[{step}/{total}] {message}{Colors.ENDC}")
    print("─" * 60)

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}    ✓ {message}{Colors.ENDC}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.FAIL}    ✗ {message}{Colors.ENDC}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.WARNING}    ⚠ {message}{Colors.ENDC}")

def check_command(command: str) -> bool:
    """Check if a command is available"""
    return shutil.which(command) is not None

def check_port(port: int, host: str = 'localhost') -> bool:
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def kill_process_on_port(port: int):
    """Kill process running on specified port (Windows)"""
    try:
        # Find process using netstat
        result = subprocess.run(
            f'netstat -aon | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                    time.sleep(1)
    except Exception:
        pass

def check_prerequisites() -> bool:
    """Check if all prerequisites are installed"""
    print_step(1, 6, "Checking Prerequisites...")
    
    # Check Python
    if not check_command('python'):
        print_error("Python is not installed or not in PATH")
        print("    Please install Python 3.8+ from https://python.org")
        return False
    
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        version = result.stdout.strip() or result.stderr.strip()
        print_success(f"Python installed: {version}")
    except Exception as e:
        print_error(f"Error checking Python version: {e}")
        return False
    
    # Check Node.js
    if not check_command('node'):
        print_error("Node.js is not installed or not in PATH")
        print("    Please install Node.js 14+ from https://nodejs.org")
        return False
    
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print_success(f"Node.js installed: {version}")
    except Exception as e:
        print_error(f"Error checking Node.js version: {e}")
        return False
    
    # Check npm
    if not check_command('npm'):
        print_error("npm is not installed")
        print("    Please reinstall Node.js from https://nodejs.org")
        return False
    
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print_success(f"npm installed: {version}")
    except Exception as e:
        print_error(f"Error checking npm version: {e}")
        return False
    
    print()
    return True

def setup_backend(skip_install: bool = False) -> Optional[subprocess.Popen]:
    """Setup and start backend server"""
    print_step(2, 6, "Setting up Backend...")
    
    backend_path = Path('Backend')
    if not backend_path.exists():
        print_error("Backend folder not found")
        return None
    
    os.chdir(backend_path)
    
    # Check requirements.txt
    if not Path('requirements.txt').exists():
        print_error("requirements.txt not found in Backend folder")
        return None
    
    # Create virtual environment if it doesn't exist
    venv_path = Path('venv')
    if not venv_path.exists():
        print("Creating Python virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print_success("Virtual environment created")
    
    # Determine Python executable path
    if sys.platform == 'win32':
        python_exe = venv_path / 'Scripts' / 'python.exe'
        pip_exe = venv_path / 'Scripts' / 'pip.exe'
    else:
        python_exe = venv_path / 'bin' / 'python'
        pip_exe = venv_path / 'bin' / 'pip'
    
    # Install dependencies
    if not skip_install:
        print("Installing Python packages...")
        try:
            subprocess.run([str(python_exe), '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         capture_output=True, check=True)
            subprocess.run([str(pip_exe), 'install', '-r', 'requirements.txt'], 
                         capture_output=True, check=True)
            print_success("Backend dependencies installed")
        except subprocess.CalledProcessError as e:
            print_warning("Some Python packages may have failed to install")
    else:
        print_warning("Skipping backend dependency installation")
    
    print()
    print_step(3, 6, "Starting Backend Server...")
    
    # Kill any existing process on port 5000
    kill_process_on_port(5000)
    
    # Start backend server
    try:
        process = subprocess.Popen(
            [str(python_exe), 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        )
        
        print("Waiting for backend to initialize...")
        time.sleep(5)
        
        if check_port(5000):
            print_success("Backend server started on http://localhost:5000")
        else:
            print_warning("Backend may still be starting up...")
        
        os.chdir('..')
        print()
        return process
    except Exception as e:
        print_error(f"Failed to start backend: {e}")
        os.chdir('..')
        return None

def setup_frontend(skip_install: bool = False, production: bool = False):
    """Setup and start frontend"""
    print_step(4, 6, "Setting up Frontend...")
    
    frontend_path = Path('hilabs-dash')
    if not frontend_path.exists():
        print_error("hilabs-dash folder not found")
        return False
    
    os.chdir(frontend_path)
    
    # Check package.json
    if not Path('package.json').exists():
        print_error("package.json not found in hilabs-dash folder")
        return False
    
    # Install dependencies
    if not skip_install:
        if Path('node_modules').exists():
            print("Updating Node.js packages...")
            subprocess.run(['npm', 'update'], capture_output=True)
        else:
            print("Installing Node.js packages (this may take a few minutes)...")
            subprocess.run(['npm', 'install'], capture_output=True)
        print_success("Frontend dependencies installed")
    else:
        print_warning("Skipping frontend dependency installation")
    
    print()
    print_step(5, 6, "Syncing Results...")
    
    # Copy results if script exists
    if Path('copy-results.js').exists():
        try:
            subprocess.run(['node', 'copy-results.js'], capture_output=True, check=True)
            print_success("Results synchronized")
        except subprocess.CalledProcessError:
            print_warning("Could not sync results (may not exist yet)")
    else:
        print_warning("copy-results.js not found, skipping sync")
    
    print()
    
    if production:
        print_step(6, 6, "Building Frontend for Production...")
        subprocess.run(['npm', 'run', 'build'], check=True)
        print_success("Frontend built for production")
        print(f"\n{Colors.GREEN}Production build created in hilabs-dash/build{Colors.ENDC}")
        print("You can serve it with any static file server")
        return True
    else:
        print_step(6, 6, "Starting Frontend Dashboard...")
        
        # Kill any existing process on port 3000
        kill_process_on_port(3000)
        
        print(f"\n{Colors.CYAN}{'═' * 63}{Colors.ENDC}\n")
        print(f"{Colors.BOLD}    ┌─────────────────────────────────────────────────────────┐")
        print("    │  Backend API:     http://localhost:5000                │")
        print("    │  Frontend:        http://localhost:3000                │")
        print("    │                                                         │")
        print("    │  The dashboard will open in your browser automatically │")
        print("    │                                                         │")
        print("    │  Press Ctrl+C to stop all services                     │")
        print(f"    └─────────────────────────────────────────────────────────┘{Colors.ENDC}\n")
        
        # Open browser after a delay
        time.sleep(3)
        webbrowser.open('http://localhost:3000')
        
        # Start frontend
        try:
            subprocess.run(['npm', 'start'], check=True)
        except KeyboardInterrupt:
            print("\n\nShutting down...")
        
        return True

def cleanup(backend_process: Optional[subprocess.Popen] = None):
    """Cleanup processes on exit"""
    print(f"\n{Colors.WARNING}Shutting down services...{Colors.ENDC}")
    
    if backend_process:
        try:
            backend_process.terminate()
            backend_process.wait(timeout=5)
        except:
            backend_process.kill()
    
    kill_process_on_port(5000)
    kill_process_on_port(3000)
    
    print_success("All services stopped")

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description='HiLabs AIQuest Launcher')
    parser.add_argument('--production', action='store_true', help='Build for production')
    parser.add_argument('--skip-install', action='store_true', help='Skip dependency installation')
    parser.add_argument('--backend-only', action='store_true', help='Run backend only')
    parser.add_argument('--frontend-only', action='store_true', help='Run frontend only')
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print_header()
    
    # Check prerequisites
    if not check_prerequisites():
        input("\nPress Enter to exit...")
        return 1
    
    backend_process = None
    
    try:
        # Setup backend
        if not args.frontend_only:
            backend_process = setup_backend(args.skip_install)
            if not backend_process and not args.backend_only:
                print_error("Failed to start backend")
                input("\nPress Enter to exit...")
                return 1
        
        # Setup frontend
        if not args.backend_only:
            if not setup_frontend(args.skip_install, args.production):
                print_error("Failed to setup frontend")
                input("\nPress Enter to exit...")
                return 1
        
        # If backend only, keep it running
        if args.backend_only and backend_process:
            print(f"\n{Colors.GREEN}Backend is running. Press Ctrl+C to stop.{Colors.ENDC}")
            backend_process.wait()
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
    finally:
        cleanup(backend_process)
        input("\nPress Enter to exit...")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
