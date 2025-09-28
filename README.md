# HiLabs Contract Analysis System

A sophisticated healthcare contract analysis system that compares provider contracts against standard templates using advanced NLP techniques and semantic matching.

## 🎯 Overview

This system analyzes healthcare provider contracts by extracting specific attributes and comparing them against standard templates to determine compliance and standardization levels. It uses focused extraction techniques with contextual search patterns to achieve high precision in attribute identification.

## ✨ Key Features

- **Precise Attribute Extraction**: Uses contextual search patterns to locate exact contract sections
- **Semantic Similarity Matching**: Employs SentenceTransformer for intelligent text comparison
- **Structural Match Classification**: Identifies placeholder replacements and structural consistency
- **Complex Table Support**: Handles fee schedules, rate tables, and structured data
- **Debug Mode**: Detailed extraction logs for troubleshooting and optimization
- **Batch Processing Ready**: Designed for multi-contract analysis workflows

## 📋 Supported Attributes

1. **Medicaid Timely Filing** - Claims submission timeframes and requirements
2. **Medicare Timely Filing** - Medicare Advantage claims processing rules
3. **No Steerage/SOC** - Network participation and provider panel restrictions
4. **Medicaid Fee Schedule** - Reimbursement rates and methodologies
5. **Medicare Fee Schedule** - Medicare Advantage payment structures

## 🚀 Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
# Analyze default contract (TN_Contract2) against template
python main.py

# Analyze specific contract
python main.py --contract TN_Contract1_Redacted.pdf --template TN_Standard_Template_Redacted.pdf

# Enable debug mode for detailed logs
python main.py --debug

# Save extracted attributes to files
python main.py --save-files
```

### Directory Structure

```
hilabs/
├── Contracts/TN/              # Contract PDF files
├── Standard Templates/        # Template PDF files
├── debug/                     # Debug outputs and cached text
├── focused_extraction.py      # Main extraction engine
├── main.py                   # Command-line interface
├── save_attributes.py        # File saving utilities
└── requirements.txt          # Python dependencies
```

## 🔧 System Architecture

### Core Components

1. **FocusedExtractor**: Main extraction engine with contextual search patterns
2. **Semantic Matching**: SentenceTransformer-based similarity scoring
3. **Structural Analysis**: Placeholder replacement detection and validation
4. **Classification Logic**: Standard vs Non-standard determination

### Extraction Process

1. **PDF Text Extraction**: PyMuPDF with page-level rendering for accuracy
2. **Contextual Search**: Multi-strategy pattern matching for each attribute
3. **Content Validation**: Length and keyword-based quality checks
4. **Semantic Comparison**: Similarity scoring between contract and template
5. **Classification**: Standard/Non-standard determination with explanations

## 📊 Results Interpretation

### Classification Criteria

- **✅ STANDARD**: Contract matches template structure with valid placeholder replacements
- **❌ NON-STANDARD**: Significant structural differences or missing content

### Similarity Scores

- **0.9-1.0**: Excellent match (near-identical text)
- **0.7-0.9**: Good match (similar structure, some variations)
- **0.5-0.7**: Moderate match (recognizable structure, notable differences)
- **0.0-0.5**: Poor match (significant structural differences)

## 🛠️ Advanced Usage

### Batch Processing

```python
from focused_extraction import FocusedExtractor

extractor = FocusedExtractor()
contracts = ["TN_Contract1_Redacted.pdf", "TN_Contract2_Redacted.pdf", "TN_Contract3_Redacted.pdf"]

for contract in contracts:
    extractor.contract_path = extractor.base_dir / "Contracts/TN" / contract
    # Process contract...
```

### Custom Attribute Analysis

```python
# Extract specific attribute
contract_text = extractor.extract_text_from_pdf(contract_path)
medicaid_section = extractor.extract_attribute(contract_text, "Medicaid Timely Filing")

# Compare with template
template_text = extractor.extract_text_from_pdf(template_path)
template_section = extractor.extract_attribute(template_text, "Medicaid Timely Filing")

# Analyze match
is_match, explanation, similarity = extractor.exact_structural_match(
    medicaid_section, template_section, "Medicaid Timely Filing"
)
```

## 📈 Performance Metrics

### Current Results (TN Contracts)

| Contract | Success Rate | Standard Matches | Notes |
|----------|-------------|------------------|--------|
| TN_Contract1 | 100% (5/5) | 100% (5/5) | All attributes extracted and classified as standard |
| TN_Contract2 | 80% (4/5) | 60% (3/5) | Medicare Timely Filing not found, fee schedules non-standard |
| TN_Contract3 | 100% (5/5) | 100% (5/5) | Excellent similarity scores across all attributes |

### Extraction Accuracy

- **Medicaid Timely Filing**: 100% success rate across all contracts
- **Medicare Timely Filing**: 67% success rate (missing in some contracts)
- **No Steerage/SOC**: 100% success rate with high similarity scores
- **Fee Schedules**: Variable success depending on contract structure

## 🔍 Troubleshooting

### Common Issues

1. **Low Similarity Scores**: Check for OCR quality issues or structural differences
2. **Missing Attributes**: Verify section numbering and heading variations
3. **Table Extraction**: Ensure proper boundary detection for fee schedules

### Debug Mode

Enable debug mode to see detailed extraction logs:

```bash
python main.py --debug
```

This provides:
- Pattern matching attempts
- Section boundary detection
- Content validation results
- Similarity calculation details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is part of the HiLabs Hackathon 2025 at IIT Kharagpur.

## 🎉 Acknowledgments

- HiLabs for providing the healthcare contract analysis challenge
- IIT Kharagpur for hosting the hackathon
- SentenceTransformers team for the semantic matching capabilities
- PyMuPDF team for robust PDF text extraction
