# HiLabs AIQuest - Contract Analysis System

## Quick Start Guide for Judges

This repository contains a complete contract analysis system with both backend (Python) and frontend (React) components. Everything needed to run the project is included.

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- Git

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
   - PDF processing
   - Attribute extraction
   - Comparison algorithms
   - Pre-processed sample contracts and results

2. **Frontend (React Dashboard)**
   - Interactive UI for contract analysis
   - Results visualization
   - File upload interface
   - Comparison views

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

### Testing the System

1. The system comes with pre-loaded sample contracts in `Backend/HiLabsAIQuest_ContractsAI/`
2. Results are already generated in `Backend/results/` for quick demo
3. Upload new contracts through the dashboard at http://localhost:3000

### Troubleshooting

If you encounter any issues:

1. **Port already in use**: 
   - Backend: Change port in `Backend/main.py` (default: 5000)
   - Frontend: Change port in `hilabs-dash/package.json` or use `PORT=3001 npm start`

2. **Module not found errors**:
   ```bash
   cd Backend && pip install -r requirements.txt
   cd ../hilabs-dash && npm install
   ```

3. **CORS issues**: Already configured in the backend

### Support

For any issues during evaluation, the complete working system with all dependencies is included in this repository. Simply pull and run!

---
**Note for Judges**: All necessary files, including contracts, results, and dependencies are included. The project is ready to run immediately after cloning.
