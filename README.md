# HiLabs Contract Analysis System

A modular pipeline to analyze healthcare provider contracts against standard templates using multiple matching strategies. Paths are strictly anchored to the `Backend/` directory to ensure portability across machines.

## Prerequisites
- Python 3.9+
- Tesseract OCR installed (required for OCR fallback)
- Python packages:
  - pandas, pypdf, pymupdf (fitz), pytesseract, pillow

Install Python dependencies:
```
pip install pandas pypdf pymupdf pytesseract pillow
```

## Directory Layout (anchored to Backend)
- `Backend/HiLabsAIQuest_ContractsAI/`
  - `Contracts/TN/` and `Contracts/WA/` contain contract PDFs
  - `Standard Templates/` contains `TN_Standard_Template_Redacted.pdf` and `WA_Standard_Redacted.pdf`
- `Backend/results/`  → exported analysis results (JSON + HTML preview)
- `Backend/debug/`    → intermediate logs, cached text, and optionally extracted attribute text files
- `Backend/config.py` → all paths are derived from the file location:
  - `BASE_DIR = BACKEND_DIR / "HiLabsAIQuest_ContractsAI"`
  - `DEBUG_DIR = BACKEND_DIR / "debug"`
  - `RESULTS_DIR = BACKEND_DIR / "results"`

These resolve the same regardless of where you run Python from.

## Tesseract OCR Auto-Detection
The backend locates Tesseract in this order:
1. Environment variable `TESSERACT_CMD` (exact path to `tesseract`)
2. `PATH` lookup via `shutil.which('tesseract')`
3. Optional hints in `config.TESSERACT_PATHS`

Quick options on Windows:
- Set for current session:
```
$env:TESSERACT_CMD = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```
- Or add Tesseract to PATH so `tesseract --version` works in a new terminal.

## How to Run
You can run from the project root (`Hilabs/`) or from `Hilabs/Backend/`.

From project root:
```
# Process all WA contracts
python Backend\main.py --batch-wa --debug

# Process all TN contracts and also save extracted attribute text files
python Backend\main.py --batch-tn --debug --save-files

# Process both states
python Backend\main.py --batch-all

# Process a single contract (state auto-detected from filename prefix)
python Backend\main.py --contract WA_1_Redacted.pdf --state WA --debug
```

From `Hilabs/Backend/` directly:
```
python main.py --batch-wa --debug
python main.py --batch-tn --debug --save-files
```

## Outputs
- Results: `Backend/results/<STATE>/<CONTRACT_NAME>/`
  - `main_results.json`, `detailed_results.json`, `summary.json`, `frontend_data.json`
  - `preview.html` for a quick in-browser summary
- Debug/caches:
  - `Backend/debug/focused/` → cached full text for each PDF
  - If `--save-files` is used: `Backend/debug/extracted_attributes/<STATE>/<CONTRACT_NAME>/` with per-attribute `.txt` files and a `00_SUMMARY.txt`

## Modules
- `Backend/extract_clauses.py` → text extraction + attribute extraction
- `Backend/compare_clauses.py` → hierarchical classification (exact/regex/fuzzy/semantic)
- `Backend/results_exporter.py` → exporting results and (merged) attribute text files (`export_extracted_attributes`)
- `Backend/main.py` → CLI entry point

## Troubleshooting
- Template not found: ensure templates exist under `Backend/HiLabsAIQuest_ContractsAI/Standard Templates/`
- Tesseract not found: set `TESSERACT_CMD` or add Tesseract to PATH
- Running from wrong directory: paths are anchored, but prefer the commands shown above

## Notes
- All project paths are anchored relative to `Backend/` (see `Backend/config.py`).
- Results and debug folders are strictly `Backend/results` and `Backend/debug`.
