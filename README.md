# HiLabs AIQuest - Contract Analysis System

## Quick Start Guide for Judges

This repository contains a complete contract analysis system with both backend (Python) and frontend (React) components. Everything needed to run the project is included.

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- Git
- Tesseract OCR (for PDF text extraction)

### One-Command Setup & Run

#### Option 1: Using the provided scripts

**Windows:**
```bash
# Clone and enter the repository
git clone https://github.com/lakshmangawhade/HiLabs-AIQuest.git
cd HiLabs-AIQuest

# Run the complete setup and start script
.\run_project.bat
```

**Linux/Mac:**
```bash
# Clone and enter the repository
git clone https://github.com/lakshmangawhade/HiLabs-AIQuest.git
cd HiLabs-AIQuest

# Make the script executable and run
chmod +x run_project.sh
./run_project.sh
```

#### Option 2: Manual Setup (if scripts don't work)

```bash
# 1. Clone the repository
git clone https://github.com/lakshmangawhade/HiLabs-AIQuest.git
cd HiLabs-AIQuest

# 2. Setup Backend
cd Backend
pip install -r requirements.txt
python main.py &  # Runs on port 5000

# 3. Setup Frontend (in new terminal)
cd ../hilabs-dash
npm install
npm start  # Runs on port 3000
```

### What's Included

1. **Backend (Python Flask API)**
   - Contract analysis engine
   - PDF processing with OCR fallback
   - Attribute extraction
   - Comparison algorithms
   - Pre-processed sample contracts and results

2. **Frontend (React Dashboard)**
   - Interactive UI for contract analysis
   - Results visualization
   - File upload interface
   - Comparison views
   - Professional compliance reporting

3. **Sample Data**
   - TN and WA contract samples
   - Standard templates
   - Pre-generated results for demo
   - Debug outputs for testing

### Project Structure
```
HiLabs-AIQuest/
├── Backend/                 # Python backend
│   ├── main.py             # Flask API server
│   ├── requirements.txt    # Python dependencies
│   ├── HiLabsAIQuest_ContractsAI/  # Contract samples
│   ├── results/            # Analysis results
│   └── debug/              # Debug outputs
├── hilabs-dash/            # React frontend
│   ├── package.json        # Node dependencies
│   ├── src/               # React source code
│   └── public/            # Static files & backend mirror
└── run_project.bat/sh     # One-click run scripts
```

### Accessing the Application

Once running:
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/docs

### Features

1. **Upload Contracts**: Upload PDF contracts for analysis
2. **Extract Attributes**: Automatically extract key contract attributes
3. **Compare Contracts**: Compare contracts against standard templates
4. **View Results**: Interactive dashboard with detailed analysis results
5. **Export Reports**: Download analysis results in various formats

---

## Technical Backend Documentation

A modular pipeline to analyze healthcare provider contracts against standard templates using multiple matching strategies. Paths are strictly anchored to the `Backend/` directory to ensure portability across machines.

### Backend Prerequisites
- Python 3.9+
- Tesseract OCR installed (required for OCR fallback)
- Python packages: pandas, pypdf, pymupdf (fitz), pytesseract, pillow

Install Python dependencies:
```bash
pip install pandas pypdf pymupdf pytesseract pillow
```

### Directory Layout (anchored to Backend)
- `Backend/HiLabsAIQuest_ContractsAI/`
  - `Contracts/TN/` and `Contracts/WA/` contain contract PDFs
  - `Standard Templates/` contains `TN_Standard_Template_Redacted.pdf` and `WA_Standard_Redacted.pdf`
- `Backend/results/`  → exported analysis results (JSON + HTML preview)
- `Backend/debug/`    → intermediate logs, cached text, and optionally extracted attribute text files
- `Backend/config.py` → all paths are derived from the file location

### Tesseract OCR Auto-Detection
The backend locates Tesseract in this order:
1. Environment variable `TESSERACT_CMD` (exact path to `tesseract`)
2. `PATH` lookup via `shutil.which('tesseract')`
3. Optional hints in `config.TESSERACT_PATHS`

Quick options on Windows:
```powershell
# Set for current session:
$env:TESSERACT_CMD = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

### Backend CLI Commands

From project root:
```bash
# Process all WA contracts
python Backend\main.py --batch-wa --debug

# Process all TN contracts and save extracted attribute text files
python Backend\main.py --batch-tn --debug --save-files

# Process both states
python Backend\main.py --batch-all

# Process a single contract
python Backend\main.py --contract WA_1_Redacted.pdf --state WA --debug
```

### Backend Outputs
- Results: `Backend/results/<STATE>/<CONTRACT_NAME>/`
  - `main_results.json`, `detailed_results.json`, `summary.json`, `frontend_data.json`
  - `preview.html` for a quick in-browser summary
- Debug/caches:
  - `Backend/debug/focused/` → cached full text for each PDF
  - `Backend/debug/extracted_attributes/<STATE>/<CONTRACT_NAME>/` with per-attribute `.txt` files

### Backend Modules
- `Backend/extract_clauses.py` → text extraction + attribute extraction
- `Backend/compare_clauses.py` → hierarchical classification (exact/regex/fuzzy/semantic)
- `Backend/results_exporter.py` → exporting results and attribute text files
- `Backend/main.py` → CLI entry point

### Troubleshooting

1. **Port already in use**: 
   - Backend: Change port in `Backend/main.py` (default: 5000)
   - Frontend: Change port in `hilabs-dash/package.json` or use `PORT=3001 npm start`

2. **Module not found errors**:
   ```bash
   cd Backend && pip install -r requirements.txt
   cd ../hilabs-dash && npm install
   ```

3. **Tesseract not found**: Set `TESSERACT_CMD` environment variable or add Tesseract to PATH

4. **Template not found**: Ensure templates exist under `Backend/HiLabsAIQuest_ContractsAI/Standard Templates/`

5. **CORS issues**: Already configured in the backend

### Support

For any issues during evaluation, the complete working system with all dependencies is included in this repository. Simply pull and run!

---
**Note for Judges**: All necessary files, including contracts, results, and dependencies are included. The project is ready to run immediately after cloning.
