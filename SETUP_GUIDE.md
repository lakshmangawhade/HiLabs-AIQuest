# HiLabs Contract Analysis System - Setup Guide

## 🚀 Quick Setup for New Contributors

This guide will help you set up the HiLabs Contract Analysis System on your local machine, regardless of your operating system or directory structure.

## ✅ Changes Made for Portability

We've made the following changes to ensure the project works on any machine:

### 1. **Relative Paths**
- ✅ Changed hardcoded absolute path `C:/Users/Lakshman/Desktop/Hilabssharwan/HiLabsAIQuest_ContractsAI` to relative path `HiLabsAIQuest_ContractsAI`
- ✅ All file paths are now relative to the Backend directory

### 2. **Tesseract OCR Configuration**
- ✅ Made Tesseract path auto-detection for multiple platforms
- ✅ Supports Windows, Linux, and macOS installations
- ✅ Can be overridden with `TESSERACT_CMD` environment variable

### 3. **Configuration File**
- ✅ Created `Backend/config.py` for environment-specific settings
- ✅ All configurable paths and settings in one place

## 📋 Prerequisites

1. **Python 3.8+**
2. **Node.js 14+** (for the dashboard)
3. **Tesseract OCR** (optional, for PDF text extraction)

## 🔧 Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/lakshmangawhade/HiLabs-AIQuest.git
cd HiLabs-AIQuest
```

### Step 2: Set Up Backend

```bash
cd Backend
pip install -r requirements.txt
```

### Step 3: Set Up Frontend Dashboard

```bash
cd ../hilabs-dash
npm install
```

### Step 4: Install Tesseract OCR (Optional)

#### Windows:
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR`

#### macOS:
```bash
brew install tesseract
```

#### Linux:
```bash
sudo apt-get install tesseract-ocr  # Ubuntu/Debian
sudo yum install tesseract  # RHEL/CentOS
```

### Step 5: Configure Environment (Optional)

If Tesseract is installed in a non-standard location, set the environment variable:

#### Windows:
```powershell
$env:TESSERACT_CMD = "C:\path\to\tesseract.exe"
```

#### Linux/macOS:
```bash
export TESSERACT_CMD="/path/to/tesseract"
```

## 📁 Directory Structure

```
HiLabs-AIQuest/
├── Backend/
│   ├── HiLabsAIQuest_ContractsAI/
│   │   ├── Contracts/
│   │   │   ├── TN/  # Tennessee contracts (add PDFs here)
│   │   │   └── WA/  # Washington contracts (add PDFs here)
│   │   └── Standard Templates/  # Template PDFs
│   ├── results/  # Analysis results (auto-generated)
│   ├── config.py  # Configuration file
│   ├── main.py  # Main entry point
│   └── requirements.txt
└── hilabs-dash/
    ├── src/  # React source code
    ├── public/  # Static files
    └── package.json
```

## 🏃 Running the Application

### Backend - Contract Analysis

```bash
cd Backend

# Generate sample results (if no PDFs available)
python generate_sample_results.py

# Or analyze actual contracts (requires PDFs)
python main.py --batch-all
```

### Frontend - Dashboard

```bash
cd hilabs-dash

# Copy results to public folder
node copy-results.js

# Start the dashboard
npm start
```

The dashboard will open at http://localhost:3000

## 🔍 Troubleshooting

### Issue: "Template not found" error
**Solution**: Ensure contract PDFs are placed in the correct directories:
- TN contracts: `Backend/HiLabsAIQuest_ContractsAI/Contracts/TN/`
- WA contracts: `Backend/HiLabsAIQuest_ContractsAI/Contracts/WA/`
- Templates: `Backend/HiLabsAIQuest_ContractsAI/Standard Templates/`

### Issue: Tesseract not found
**Solution**: 
1. Install Tesseract OCR for your OS
2. Set `TESSERACT_CMD` environment variable if needed
3. Or edit `Backend/config.py` to add your Tesseract path

### Issue: No results showing in dashboard
**Solution**:
1. Run `python Backend/generate_sample_results.py` to create sample data
2. Run `node hilabs-dash/copy-results.js` to copy results to public folder

## 📝 Configuration Options

Edit `Backend/config.py` to customize:
- Base directories
- Tesseract paths
- Classification thresholds
- Supported states
- Export settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes (ensure all paths are relative!)
4. Test on your local machine
5. Submit a pull request

## 📄 Notes for Developers

- **Never use absolute paths** - Always use relative paths from the Backend directory
- **Test cross-platform** - Ensure changes work on Windows, Linux, and macOS
- **Use config.py** - Put environment-specific settings in the config file
- **Document changes** - Update this guide if you add new dependencies or configurations

## ✅ Summary of Fixes Applied

1. ✅ Fixed `Backend/focused_extraction.py` - Changed absolute path to relative
2. ✅ Made Tesseract OCR path auto-detection work across platforms
3. ✅ Created `Backend/config.py` for centralized configuration
4. ✅ Verified `Backend/main.py` uses relative paths
5. ✅ Confirmed `hilabs-dash/copy-results.js` uses relative paths
6. ✅ Created `Backend/generate_sample_results.py` for testing without PDFs

The project is now fully portable and will work on any machine without path issues! 🎉
