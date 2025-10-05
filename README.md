# HiLabs AIQuest - Contract Analysis System

**GitHub Repository**: https://github.com/lakshmangawhade/HiLabs-AIQuest

**Team Name:** Radeon, **Team Members:** [Lakshman Gawhade](https://github.com/lakshmangawhade), [Sharwan Bagaria](https://github.com/sharwanbagaria03), [Harshit Pathak](https://github.com/harshitpathak10088)

Video Submission: [https://drive.google.com/drive/folders/1YtKtBoHyjyoA3XRLrcjchG8kSM7A3IPx?usp=drive_link]

# Introduction

Healthcare provider contracts often suffer from inconsistent formatting, complex legal language, and varying compliance requirements across different states and templates. Manual contract analysis is time-consuming, error-prone, and difficult to scale. To address this, we developed a comprehensive contract analysis platform that streamlines the workflow:

1. **Hybrid Text Extraction**: Combines PyPDF and Tesseract OCR for reliable text extraction from both digital and scanned contracts.

2. **Intelligent Attribute Extraction**: Uses context-aware patterns and multi-strategy search to identify key contract clauses like timely filing requirements and fee schedules.

3. **Hierarchical Classification**: Employs a four-tier matching strategy (Exact → Regex → Fuzzy → Semantic) to determine contract compliance against standard templates.

4. **Interactive Dashboard**: Provides real-time insights and detailed compliance reports to support contract management and regulatory compliance.

# Table of Contents

The pipeline of the platform can be divided into the following parts:

1. [Dataset](#dataset)  
2. [Contract Processing Pipeline](#contract-processing-pipeline)  
   2.1. [Hybrid Text Extraction](#hybrid-text-extraction)  
   2.2. [Attribute-Specific Extraction](#attribute-specific-extraction)  
   2.3. [Hierarchical Classification Engine](#hierarchical-classification-engine)  
   2.4. [Compliance Score Calculation](#compliance-score-calculation)  
   2.5. [State-Specific Processing](#state-specific-processing)  
   2.6. [Results Export & Visualization](#results-export--visualization)  
3. [Interactive Analytics Dashboard](#interactive-analytics-dashboard)  
   3.1. [Frontend](#frontend)  
   3.2. [Backend](#backend)  
4. [Technical Architecture](#technical-architecture)

# Requirements

1. Python 3.8+
2. Node.js 14+
3. Tesseract OCR
4. Git

# Dataset

The datasets used in this project include:

1. **TN Contract Samples** (`Backend/HiLabsAIQuest_ContractsAI/Contracts/TN/`)  
   Contains 5 Tennessee healthcare provider contracts with various compliance scenarios, including standard and non-standard clauses.

2. **WA Contract Samples** (`Backend/HiLabsAIQuest_ContractsAI/Contracts/WA/`)  
   Contains 5 Washington state healthcare provider contracts for cross-state compliance analysis.

3. **Standard Templates** (`Backend/HiLabsAIQuest_ContractsAI/Standard Templates/`)  
   Official standard templates for both TN and WA states used as compliance benchmarks:
   - `TN_Standard_Template_Redacted.pdf`
   - `WA_Standard_Redacted.pdf`

4. **Pre-processed Results** (`Backend/results/`)  
   Sample analysis results demonstrating the system's output format and compliance assessments.

## Quick Start Guide for Judges

This repository contains a complete contract analysis system with both backend (Python) and frontend (React) components. Everything needed to run the project is included.

# Contract Processing Pipeline

## Hybrid Text Extraction

The system uses a two-tier approach for reliable text extraction from healthcare contracts, which often contain both digital text and scanned images:

- **Primary Extraction**: PyPDF library for direct text extraction from digital PDFs
- **OCR Fallback**: Tesseract OCR automatically triggered for pages with insufficient text (< 100 characters)
- **Auto-Detection**: Dynamic Tesseract resolution via environment variables → PATH → config hints
- **Caching**: Extracted text cached to `Backend/debug/focused/` to avoid re-processing

## Attribute-Specific Extraction

Healthcare contracts contain specific attributes that require targeted extraction strategies. Our system identifies five key attributes using context-aware patterns:

- **Medicaid Timely Filing**: Article III, Section 3.1 requirements
- **Medicare Timely Filing**: Article VI, Section 6.1 requirements  
- **No Steerage/SOC**: Article II, Section 2.11 network provisions
- **Medicaid Fee Schedule**: Article IV compensation tables
- **Medicare Fee Schedule**: Article IV Medicare Advantage rates

**Multi-Strategy Search Process:**
1. Direct section matching using precise regex patterns
2. Article-based search within document structure
3. Attachment pattern matching for specific agreement types
4. Table detection for fee schedule extraction

## Hierarchical Classification Engine

The classification system employs a four-tier hierarchical approach to determine contract compliance:

1. **Exact Match (Threshold: 1.0)**: Character-by-character comparison for identical clauses
2. **Regex Match (Threshold: 0.9)**: Pattern-based matching for structural variations
3. **Fuzzy Match (Threshold: 0.8)**: Levenshtein distance for minor textual differences
4. **Semantic Match (Threshold: 0.7)**: Lightweight embedding similarity for meaning-based comparison

Each tier is optimized for different types of contract variations, ensuring both accuracy and performance.

## Compliance Score Calculation

The compliance score is calculated using multiple dimensions:

- **Attribute Coverage**: Percentage of successfully extracted attributes
- **Match Quality**: Weighted average of classification confidence scores
- **Template Alignment**: Structural similarity to standard templates
- **Business Rules**: Domain-specific healthcare contract requirements

## State-Specific Processing

The system handles state-specific variations in contract structure and requirements:

- **Tennessee (TN)**: Uses `TN_Standard_Template_Redacted.pdf` with TN-specific article numbering
- **Washington (WA)**: Uses `WA_Standard_Redacted.pdf` with WA-specific formatting
- **Auto-Detection**: Contract state determined from filename prefix or explicit parameter

## Results Export & Visualization

Multiple export formats support different use cases:

- **JSON Results**: Machine-readable format for API integration
- **HTML Preview**: Quick browser-based summary with visual indicators
- **Detailed Reports**: Comprehensive analysis with attribute-level breakdowns
- **Debug Files**: Individual attribute extractions for manual review

### Final processed data format & Summary

The system generates structured output with compliance metrics:

| Attribute | Status | Match Type | Confidence | Details |
|-----------|--------|------------|------------|---------|
| Medicaid Timely Filing | ✅ Standard | Exact | 1.000 | Perfect match |
| Medicare Timely Filing | ❌ Non-Standard | No Match | 0.000 | Missing section |
| No Steerage/SOC | ✅ Standard | Semantic | 0.850 | Similar meaning |
| Medicaid Fee Schedule | ❌ Non-Standard | Fuzzy | 0.650 | Partial match |
| Medicare Fee Schedule | ❌ Non-Standard | No Match | 0.000 | Not found |

> **Example Summary Passed to Frontend:**

```json
{
  "overview": {
    "total_attributes": 5,
    "standard_count": 2,
    "non_standard_count": 3,
    "compliance_rate": 40.0
  },
  "match_type_distribution": {
    "exact": 1,
    "semantic": 1,
    "no_match": 3
  },
  "confidence_stats": {
    "average": 0.500,
    "minimum": 0.000,
    "maximum": 1.000
  }
}
```

# Interactive Analytics Dashboard

## Frontend

The frontend consists of an interactive React dashboard built with modern UI components, providing comprehensive contract analysis visualization and user-friendly interface for contract management.

## 🚀 Setup Instructions

### Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python** (version 3.8 or higher)
- **Node.js** (version 14 or higher)
- **Tesseract OCR** (for PDF text extraction)
- **Git** (for cloning the repository)

### System Requirements

- **Memory:** Minimum 4GB RAM (8GB recommended)
- **Storage:** At least 2GB free disk space
- **CPU:** Multi-core processor (2+ cores recommended)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/lakshmangawhade/HiLabs-AIQuest.git
cd HiLabs-AIQuest
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd Backend

# Install Python dependencies
pip install pandas pypdf pymupdf pytesseract pillow flask flask-cors

# Test backend with sample contracts
python main.py --batch-tn --debug
```

#### 3. Frontend Setup (Optional)

```bash
# Navigate to frontend directory
cd ../hilabs-dash

# Install Node.js dependencies
npm install

# Start development server
npm start
```

#### 4. Tesseract OCR Installation

**Windows:**
```powershell
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install to default location or set environment variable:
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

### Usage Examples

#### Backend-Only Analysis

```bash
cd Backend

# Process all TN contracts with debug output
python main.py --batch-tn --debug --save-files

# Process single contract
python main.py --contract TN_Contract1_Redacted.pdf --state TN --debug
# Process all contracts from both states
python main.py --batch-all --debug

## UI Screenshots

Place the following images in `docs/screenshots/` for the links to render:
- `dashboard_overview.png`
- `state_comparison.png`
- `contracts_table.png`
- `contract_upload.png`
- `clause_classification_summary.png`

### Dashboard Overview
Shows KPIs, compliance distribution, and state comparison.

![Dashboard Overview](docs/screenshots/dashboard_overview.png)

### State-by-State Comparison
Summarizes per-state compliance and confidence metrics.

![State Comparison](docs/screenshots/state_comparison.png)

### Contracts Table
Lists all analyzed contracts with compliance, standard/non-standard counts, and quick actions.

![Contracts Table](docs/screenshots/contracts_table.png)

### Contract Upload & Comparison
Drag-and-drop interface to upload standard template and redacted contract for analysis.

![Contract Upload](docs/screenshots/contract_upload.png)

### Clause Classification Summary
Visual breakdown of standard vs. non-standard clauses per contract.

![Clause Classification Summary](docs/screenshots/clause_classification_summary.png)

### Troubleshooting

1. **Tesseract not found**
   ```bash
   # Verify Tesseract installation
   tesseract --version

   # Set environment variable if needed
   export TESSERACT_CMD=/usr/bin/tesseract
   ```

2. **Python dependencies**
   ```bash
   # Install missing packages
   pip install pandas pypdf pymupdf pytesseract pillow flask flask-cors
   ```

3. **Port conflicts**
   ```bash
   # Change backend port in main.py
   # Change frontend port: PORT=3001 npm start
   ```

4. **Template files missing**
   ```bash
   # Ensure templates exist
   ls Backend/HiLabsAIQuest_ContractsAI/Standard\ Templates/
   ```

### Data Management

#### Sample Contracts

The system includes pre-loaded sample contracts:
- **TN Contracts:** 5 Tennessee healthcare provider contracts
- **WA Contracts:** 5 Washington state contracts
- **Templates:** Standard compliance templates for both states

#### Results Structure

```
Backend/results/
├── TN/
│   ├── TN_Contract1_Redacted/
│   │   ├── summary.json
│   │   ├── detailed_results.json
│   │   └── preview.html
│   └── ...
└── WA/
    └── ...
```

### Getting Started with the Application

1. **Run Backend Analysis:** Execute `python Backend/main.py --batch-all --debug`
2. **Review Results:** Check generated files in `Backend/results/`
3. **View HTML Previews:** Open `preview.html` files in browser
4. **Explore Debug Output:** Review detailed extractions in `Backend/debug/`
5. **Start Frontend (Optional):** Launch React dashboard for interactive analysis

## Backend

The backend is implemented with Python and handles the complete contract analysis pipeline, providing APIs for the dashboard and generating structured compliance reports. Key components include:

- **Text Extraction Engine:** Hybrid PyPDF + Tesseract OCR processing
- **Attribute Extraction:** Context-aware pattern matching for healthcare contract clauses  
- **Classification System:** Four-tier hierarchical matching (Exact → Regex → Fuzzy → Semantic)
- **Results Export:** Multiple format support (JSON, HTML, detailed text files)
- **State Management:** TN and WA specific processing with appropriate templates

### Technical Architecture

The system follows a modular architecture with clear separation of concerns:

```
Backend/
├── extract_clauses.py      # Text extraction + attribute identification
├── compare_clauses.py      # Hierarchical classification engine
├── results_exporter.py     # Multi-format result export
├── main.py                 # CLI interface + batch processing
├── config.py               # Portable path configuration
└── HiLabsAIQuest_ContractsAI/
    ├── Contracts/TN/       # Tennessee contract samples
    ├── Contracts/WA/       # Washington contract samples
    └── Standard Templates/ # Compliance benchmark templates
```

**Key Design Principles:**
- **Portability:** All paths anchored to `Backend/` directory using `__file__` resolution
- **Modularity:** Separate concerns for extraction, classification, and export
- **Scalability:** Batch processing support for multiple contracts
- **Reliability:** Hybrid OCR approach with caching for performance
- **Extensibility:** Plugin-based architecture for new states and attributes

---
**Note for Judges**: All necessary files, including contracts, results, and dependencies are included. The project is ready to run immediately after cloning.