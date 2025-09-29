# Contract Classification System - User Guide

## Overview

The HiLabs Contract Classification System uses a **hierarchical matching strategy** to compare contracts against standard templates. This approach ensures both accuracy and speed by trying methods in order from most precise to most flexible.

## Hierarchical Matching Strategy

The system attempts to classify contracts using four methods in this specific order:

### 1. **Exact Match** (Threshold: 1.0)
- **What it does**: Character-by-character comparison after normalization
- **When it matches**: 
  - Identical text (ignoring whitespace/formatting)
  - Template placeholders replaced with actual values (e.g., `[XX]` → `90`)
- **Example**: 
  ```
  Template: "Submit claims within [XX] days"
  Contract: "Submit claims within 90 days"
  Result: ✅ EXACT MATCH
  ```

### 2. **Regex Pattern Match** (Threshold: 0.9)
- **What it does**: Identifies structural patterns and legal document formatting
- **When it matches**:
  - Same section numbering and structure
  - Similar legal terminology patterns
  - Matching table structures with different values
- **Example**:
  ```
  Template: "3.1.1 Claims shall be filed..."
  Contract: "3.1.1 Claims must be submitted..."
  Result: ✅ REGEX MATCH (same structure)
  ```

### 3. **Fuzzy Match** (Threshold: 0.8)
- **What it does**: Approximate string matching with synonym recognition
- **When it matches**:
  - Similar content with different wording
  - Legal synonyms (e.g., "shall" ↔ "must", "prior to" ↔ "before")
  - Reordered but equivalent content
- **Algorithms used**:
  - Levenshtein distance
  - Jaro-Winkler similarity
  - Token sort ratio
  - N-gram similarity
- **Example**:
  ```
  Template: "Provider shall submit claims within 90 days"
  Contract: "Healthcare provider must file claims no later than ninety days"
  Result: ✅ FUZZY MATCH (synonyms and reordering)
  ```

### 4. **Semantic Match** (Threshold: 0.7)
- **What it does**: AI-based meaning comparison using lightweight language models
- **When it matches**:
  - Different wording but same meaning
  - Complex paraphrasing
  - Conceptually similar content
- **Model**: Uses `all-MiniLM-L6-v2` for fast inference
- **Example**:
  ```
  Template: "Submit claims within 90 days of service"
  Contract: "Billing statements must be sent within three months of treatment"
  Result: ✅ SEMANTIC MATCH (same meaning)
  ```

## Usage

### Basic Command
```bash
python main.py --contract TN_Contract1_Redacted.pdf --template TN_Standard_Template_Redacted.pdf
```

### With Custom Thresholds
```bash
python main.py --contract contract.pdf --template template.pdf \
  --threshold-regex 0.85 \
  --threshold-fuzzy 0.75 \
  --threshold-semantic 0.65
```

### Classification Only Mode
```bash
python main.py --classification-only
```

### Debug Mode with Detailed Logs
```bash
python main.py --debug --save-files
```

## Understanding Results

### Classification Output
Each attribute shows:
- **Match Type**: Which method succeeded (EXACT/REGEX/FUZZY/SEMANTIC/NO_MATCH)
- **Confidence**: Score from 0.0 to 1.0
- **Explanation**: Human-readable reason for the classification

### Icons
- 🎯 EXACT - Perfect match
- 🔍 REGEX - Pattern match
- 〰️ FUZZY - Approximate match
- 🧠 SEMANTIC - Meaning match
- ❓ NO_MATCH - No suitable match found

## Configuration

### Adjusting Thresholds

Thresholds determine the minimum score needed for each matching method:

- **Strict matching** (fewer false positives):
  ```
  --threshold-regex 0.95 --threshold-fuzzy 0.85 --threshold-semantic 0.75
  ```

- **Relaxed matching** (catch more variations):
  ```
  --threshold-regex 0.85 --threshold-fuzzy 0.70 --threshold-semantic 0.60
  ```

### Attribute-Specific Settings

The system automatically adjusts thresholds for certain attributes:
- **Fee Schedules**: Lower thresholds due to table variations
- **Timely Filing**: Higher thresholds for critical compliance terms

## Performance Optimization

1. **Caching**: Semantic embeddings are cached for faster repeated analysis
2. **Early Exit**: Stops at first successful match method
3. **GPU Support**: Automatically uses GPU if available for semantic matching
4. **Batch Processing**: Processes multiple chunks in parallel

## Troubleshooting

### Issue: Too many false positives
**Solution**: Increase thresholds, especially for fuzzy and semantic matching

### Issue: Valid contracts marked as non-standard
**Solution**: 
1. Check if text extraction succeeded
2. Lower thresholds progressively
3. Review the explanation to understand why matching failed

### Issue: Slow performance
**Solution**:
1. Semantic matching is slowest - increase threshold to reduce its use
2. Enable caching with `--save-files`
3. Use `--classification-only` to skip detailed extraction logs

## Testing

Run the test suite to understand how each matching method works:
```bash
python test_classification.py
```

This demonstrates:
- When each method triggers
- How thresholds affect results
- Real-world matching scenarios
