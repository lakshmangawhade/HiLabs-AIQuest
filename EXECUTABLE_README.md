# HiLabs AIQuest - Executable Options

This project provides multiple ways to run the HiLabs AIQuest Contract Analysis System as an executable on Windows.

## Quick Start Options

### Option 1: Enhanced Batch File (Simplest)
```bash
run_hilabs.bat
```
- **Features**: Improved error handling, virtual environment support, colored output
- **Requirements**: Python 3.8+ and Node.js 14+ must be installed
- **Best for**: Quick development and testing

### Option 2: PowerShell Script (Advanced)
```powershell
# First, enable PowerShell script execution (run as Administrator):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run the script:
.\run_hilabs.ps1

# With options:
.\run_hilabs.ps1 -Production      # Build for production
.\run_hilabs.ps1 -SkipInstall     # Skip dependency installation
.\run_hilabs.ps1 -BackendOnly     # Run backend only
.\run_hilabs.ps1 -FrontendOnly    # Run frontend only
```
- **Features**: Command-line arguments, better process management, production build support
- **Requirements**: Windows PowerShell 5.0+, Python 3.8+, Node.js 14+
- **Best for**: Advanced users, CI/CD pipelines

### Option 3: Python Launcher (Cross-platform)
```bash
python launcher.py

# With options:
python launcher.py --production      # Build for production
python launcher.py --skip-install    # Skip dependency installation
python launcher.py --backend-only    # Run backend only
python launcher.py --frontend-only   # Run frontend only
```
- **Features**: Cross-platform support, colored terminal output, comprehensive error handling
- **Requirements**: Python 3.8+, Node.js 14+
- **Best for**: Cross-platform deployment

### Option 4: GUI Launcher (User-friendly)
```bash
python gui_launcher.py
```
- **Features**: Graphical interface, real-time status monitoring, one-click start/stop
- **Requirements**: Python 3.8+ with tkinter, Node.js 14+
- **Best for**: Non-technical users, demonstrations

### Option 5: Standalone EXE (No Dependencies)
```bash
# First, build the executable:
build_exe.bat

# Then run the generated executable:
HiLabs_Launcher.exe
```
- **Features**: Single executable file, no Python/Node.js required on target machine
- **Requirements for building**: Python with PyInstaller
- **Requirements for running**: None (all dependencies bundled)
- **Best for**: Distribution to end users

## Building a Standalone Executable

To create a standalone .exe file that doesn't require Python or Node.js:

1. **Install build dependencies:**
   ```bash
   pip install -r build_requirements.txt
   ```

2. **Run the build script:**
   ```bash
   build_exe.bat
   ```

3. **Find your executable:**
   - The executable will be created as `HiLabs_Launcher.exe` in the root directory
   - It includes all Python dependencies but still requires Node.js for the frontend

## Advanced: Creating a Full Installer

For a professional installation experience, you can use tools like:

1. **NSIS (Nullsoft Scriptable Install System)**
   - Create a professional Windows installer
   - Include Node.js runtime
   - Add Start Menu shortcuts
   - Register uninstaller

2. **Inno Setup**
   - Simple script-based installer creation
   - Automatic dependency checking
   - Custom installation wizard

3. **WiX Toolset**
   - Creates MSI installers
   - Enterprise deployment ready
   - Windows Installer technology

## System Requirements

### For Running the Scripts
- **Python**: 3.8 or higher
- **Node.js**: 14.0 or higher
- **npm**: 6.0 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space

### For Running the Standalone EXE
- **Windows**: 10 or higher (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space

## Troubleshooting

### Common Issues

1. **"Python is not recognized"**
   - Install Python from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **"Node is not recognized"**
   - Install Node.js from https://nodejs.org
   - Restart your terminal after installation

3. **Port already in use**
   - The scripts automatically kill processes on ports 5000 and 3000
   - If issues persist, manually check: `netstat -aon | findstr :5000`

4. **PowerShell execution policy error**
   - Run as Administrator: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

5. **Build fails with PyInstaller**
   - Update PyInstaller: `pip install --upgrade pyinstaller`
   - Disable antivirus temporarily during build

## Features Comparison

| Feature | Batch | PowerShell | Python | GUI | EXE |
|---------|-------|------------|--------|-----|-----|
| No installation needed | ❌ | ❌ | ❌ | ❌ | ✅ |
| Colored output | ✅ | ✅ | ✅ | ✅ | ✅ |
| Error handling | ✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ |
| Command-line args | ❌ | ✅ | ✅ | ❌ | ✅ |
| Visual interface | ❌ | ❌ | ❌ | ✅ | ❌ |
| Cross-platform | ❌ | ❌ | ✅ | ✅ | ❌ |
| Production build | ❌ | ✅ | ✅ | ❌ | ✅ |
| Process management | ✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ |

## Support

For issues or questions:
1. Check the main README.md for general setup
2. Review SETUP_GUIDE.md for detailed configuration
3. Check the output logs for specific error messages
4. Ensure all prerequisites are properly installed

## License

This launcher system is part of the HiLabs AIQuest project.
