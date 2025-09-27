# HiLabs Hackathon: Smart Contract Language Tagging

This project provides a solution for the "Intelligent Language Classification for Healthcare Contracts" challenge. It automatically processes healthcare contracts, extracts key clauses, and classifies them as `Standard` or `Non-Standard` by comparing them against a predefined set of standard clauses.

## Architecture

The solution is built with a modular Python architecture:

- `main.py`: The main entry point and orchestrator of the analysis pipeline. It manages file paths, controls the flow, and generates the final summary report.
- `extract_clauses.py`: Responsible for parsing PDF contract files, extracting the raw text, and identifying the specific clauses required for analysis based on section headers.
- `compare_clauses.py`: Contains the core classification logic. It uses a `bert-base-uncased` sentence transformer model to compute the semantic similarity between an extracted clause and the standard clause, classifying it as `Standard` or `Non-Standard`.
- `requirements.txt`: Lists all the necessary Python dependencies.

## Setup Instructions

### 1. Install Tesseract-OCR Engine

This project uses Tesseract for Optical Character Recognition (OCR) to read scanned documents. You **must** install it on your system first.

- **Windows**: Download and run the installer from [here](https://github.com/UB-Mannheim/tesseract/wiki). 
  - **Important**: During installation, make sure to check the option "Add Tesseract to system PATH" so the script can find it automatically.
- **macOS**: `brew install tesseract`
- **Linux (Ubuntu/Debian)**: `sudo apt-get install tesseract-ocr`

After installation, you may need to uncomment and update the path in `extract_clauses.py` if the script cannot find Tesseract:
```python
# In extract_clauses.py, update this line with your Tesseract path:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### 2. Install Python Dependencies

1.  **Prerequisites**: Ensure you have Python 3.8+ and `pip` installed on your system.

2.  **Clone the Repository**: Clone this project to your local machine.

3.  **Install Dependencies**: Navigate to the project's root directory in your terminal and install the required libraries using the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

    *Note: The first time you run the analysis, the `transformers` library will download the pre-trained BERT model (approx. 440MB). This is a one-time process.*

## How to Run the Analysis

Once the setup is complete, you can run the entire analysis pipeline with a single command from the project's root directory:

```bash
python main.py
```

The script will:
1.  Process each contract file from the `HiLabsAIQuest_ContractsAI/Contracts/TN` and `HiLabsAIQuest_ContractsAI/Contracts/WA` directories.
2.  Extract the five key attributes from each contract.
3.  Compare them against the internal "gold standard" clauses.
4.  Print the classification for each attribute to the console.
5.  Generate a final summary of the results.

## Output

The script produces two outputs:

1.  **Console Summary**: A high-level summary printed directly to your terminal after the analysis is complete. It looks like this:

    ```
    ==================== Analysis Summary ====================
    - Total Clauses Analyzed: 50
    - Standard Clauses Count: 42
    - Non Standard Clauses Count: 8
    - Contracts With Non Standard Count: 5
    - List Of Contracts With Non Standard: ['TN_Contract2_Redacted.pdf', ...]
    ```

2.  **JSON Report** (`analysis_results.json`): A detailed JSON file is created in the root directory, containing the classification and text previews for every clause in every contract, along with the summary metrics.
