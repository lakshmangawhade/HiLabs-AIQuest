import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pandas as pd
import numpy as np
from pypdf import PdfReader
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- OCR Configuration ---
# You must install Google's Tesseract-OCR engine and add it to your system's PATH.
# For Windows, you can find the installer here: https://github.com/UB-Mannheim/tesseract/wiki
# After installation, you might need to specify the path to the executable, like this:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize semantic model (will be loaded lazily)
_semantic_model = None

def get_semantic_model():
    """Lazy loading of the sentence transformer model."""
    global _semantic_model
    if _semantic_model is None:
        print("Loading semantic similarity model...")
        _semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _semantic_model

def load_attribute_headers() -> Dict[str, List[str]]:
    """Load and build comprehensive attribute headers from the Excel file."""
    
    # Fallback headers if Excel file is not available
    fallback_headers = {
        "Medicaid Timely Filing": [
            "Submission and Adjudication of Medicaid Claims",
            "Medicaid Claims", "Claims Submission", "Timely Filing",
            "Enterprise Agreement", "Claims Processing", "Medicaid Timely Filing"
        ],
        "Medicare Timely Filing": [
            "Submission and Adjudication of Medicare Advantage Claims",
            "Medicare Advantage Claims", "Medicare Advantage Attachment",
            "Medicare Claims", "6.1-6.1.3", "Medicare Timely Filing"
        ],
        "No Steerage/SOC": [
            "Networks and Provider Panels", "Provider Networks",
            "Network Participation", "Base, 2.11", "2.11",
            "Steerage", "Standard of Care", "Network Requirements"
        ],
        "Medicaid Fee Schedule": [
            "Plan Compensation Schedule", "Compensation Schedule",
            "Specific Reimbursement Terms", "Reimbursement Terms",
            "Medicaid Rate", "Fee Schedule", "Medicaid Fee Schedule",
            "Payment Terms", "Reimbursement"
        ],
        "Medicare Fee Schedule": [
            "Plan Compensation Schedule", "Compensation Schedule",
            "Specific Reimbursement Terms", "Reimbursement Terms",
            "Medicare Advantage Rate", "Fee Schedule", "Medicare Fee Schedule",
            "Payment Terms", "Reimbursement"
        ],
    }
    
    # Try to load from Excel file
    excel_path = Path("HiLabsAIQuest_ContractsAI/Attribute Dictionary.xlsx")
    if excel_path.exists():
        try:
            df = pd.read_excel(excel_path)
            print(f"Loaded attribute dictionary from {excel_path}")
            # Process Excel data to build headers (implementation depends on Excel structure)
            # For now, we'll use the fallback and enhance it
        except Exception as e:
            print(f"Could not load Excel file: {e}. Using fallback headers.")
    
    # Save the headers to JSON for easy review
    headers_path = Path("debug/attribute_headers.json")
    headers_path.parent.mkdir(exist_ok=True)
    with open(headers_path, 'w') as f:
        json.dump(fallback_headers, f, indent=2)
    
    return fallback_headers

# Load headers at module level
ATTRIBUTE_HEADERS = load_attribute_headers()

def extract_text_from_pdf(pdf_path: str, debug: bool = False) -> Optional[str]:
    """
    Extracts text from a PDF using improved hybrid approach.
    1. Uses pypdf for fast direct text extraction
    2. Falls back to PyMuPDF page-level OCR for scanned pages
    3. Caches extracted text for debugging
    """
    pdf_path = Path(pdf_path)
    contract_name = pdf_path.stem
    
    # Create debug directory
    debug_dir = Path("debug")
    debug_dir.mkdir(exist_ok=True)
    
    try:
        # First pass: Check which pages need OCR using pypdf
        reader = PdfReader(str(pdf_path))
        page_texts = []
        ocr_needed = []
        
        if debug:
            print(f"\n{'='*60}")
            print(f"Processing: {contract_name}")
            print(f"{'='*60}")
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            page_texts.append(text)
            needs_ocr = len(text.strip()) < 100
            ocr_needed.append(needs_ocr)
            
            if debug:
                print(f"Page {i+1}: {len(text)} chars direct, OCR needed: {needs_ocr}")
        
        # Second pass: Use PyMuPDF for OCR where needed
        if any(ocr_needed):
            if debug:
                print(f"Opening with PyMuPDF for OCR on {sum(ocr_needed)} pages...")
            
            doc = fitz.open(str(pdf_path))
            for i, page in enumerate(doc):
                if ocr_needed[i]:
                    try:
                        # Render page at 300 DPI
                        pix = page.get_pixmap(dpi=300)
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        
                        # Perform OCR
                        ocr_text = pytesseract.image_to_string(img, config='--psm 6')
                        page_texts[i] = ocr_text
                        
                        if debug:
                            print(f"  Page {i+1} OCR: {len(ocr_text)} chars extracted")
                            
                    except Exception as ocr_error:
                        if debug:
                            print(f"  Page {i+1} OCR failed: {ocr_error}")
            
            doc.close()
        
        # Combine all page texts
        full_text = "\n".join(page_texts)
        
        # Cache the extracted text for debugging
        cache_path = debug_dir / f"{contract_name}.txt"
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        if debug:
            print(f"Total extracted: {len(full_text)} chars")
            print(f"Cached to: {cache_path}")
            print("="*60)
        
        return full_text
        
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return None

def find_candidate_blocks(text: str, header: str) -> List[Tuple[str, int, str]]:
    """
    Find candidate text blocks around each header occurrence.
    Returns list of (block_text, start_pos, matched_header_variant)
    """
    candidates = []
    
    # Multiple patterns to catch different formatting
    patterns = [
        # Standard section header
        rf"(?i)(\d+\.\d*\s*)?{re.escape(header)}[\s\n:]*",
        # Article/Section format  
        rf"(?i)(ARTICLE|Section)\s+[\dIVX]+\.\s*{re.escape(header)}[\s\n:]*",
        # Numbered subsection
        rf"(?i)\d+\.\d+\.\d*\s*{re.escape(header)}[\s\n:]*",
        # Simple occurrence
        rf"(?i){re.escape(header)}[\s\n:]*"
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            start = match.end()
            
            # Extract 2-3 paragraphs after the header
            # Look for natural break points
            end_patterns = [
                r'\n\s*\d+\.\d*\s*[A-Z]',  # Next numbered section
                r'\n\s*[A-Z][A-Z\s]+:',    # Next all-caps header
                r'\n\s*ARTICLE',           # Next article
                r'\n\s*Section',           # Next section
                r'\n\s*\d+\.\s*[A-Z]',     # Simple numbered item
            ]
            
            # Find the nearest break point, but get at least 500 chars
            min_length = 500
            max_length = 2000
            
            end_pos = start + max_length
            for end_pattern in end_patterns:
                next_match = re.search(end_pattern, text[start:start + max_length])
                if next_match and next_match.start() > min_length:
                    end_pos = start + next_match.start()
                    break
            
            block_text = text[start:end_pos].strip()
            
            if len(block_text) > 100:  # Only keep substantial blocks
                candidates.append((block_text, start, match.group(0)))
    
    return candidates


def semantic_score_candidate(candidate_text: str, standard_clause: str) -> float:
    """
    Score a candidate text block against the standard clause using semantic similarity.
    """
    try:
        model = get_semantic_model()
        
        # Get embeddings
        candidate_embedding = model.encode([candidate_text])
        standard_embedding = model.encode([standard_clause])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(candidate_embedding, standard_embedding)[0][0]
        return float(similarity)
        
    except Exception as e:
        print(f"Semantic scoring failed: {e}")
        return 0.0


def extract_all_clauses(text: str, standard_clauses: Dict[str, str], debug: bool = False) -> Dict[str, Dict]:
    """
    Extract clauses using two-stage approach:
    1. Find candidate blocks around headers
    2. Use semantic similarity to pick the best match
    """
    if not text:
        return {}
    
    extracted_data = {}
    
    for attribute, headers in ATTRIBUTE_HEADERS.items():
        if debug:
            print(f"\n{'='*50}")
            print(f"EXTRACTING: {attribute}")
        
        all_candidates = []
        
        # Stage 1: Find all candidate blocks for this attribute
        for header in headers:
            candidates = find_candidate_blocks(text, header)
            for candidate_text, pos, matched_header in candidates:
                all_candidates.append({
                    'text': candidate_text,
                    'position': pos,
                    'header': matched_header,
                    'score': 0.0
                })
                
                if debug:
                    print(f"  Found candidate via '{matched_header}': {candidate_text[:100]}...")
        
        if not all_candidates:
            if debug:
                print(f"  No candidates found for {attribute}")
            extracted_data[attribute] = {
                'text': '',
                'score': 0.0,
                'header': '',
                'method': 'not_found'
            }
            continue
        
        # Stage 2: Score candidates against standard clause
        if attribute in standard_clauses:
            standard_clause = standard_clauses[attribute]
            
            for candidate in all_candidates:
                candidate['score'] = semantic_score_candidate(candidate['text'], standard_clause)
                
                if debug:
                    print(f"    Score: {candidate['score']:.3f} for '{candidate['header']}'")
            
            # Pick the best candidate
            best_candidate = max(all_candidates, key=lambda x: x['score'])
            
            extracted_data[attribute] = {
                'text': best_candidate['text'],
                'score': best_candidate['score'],
                'header': best_candidate['header'],
                'method': 'semantic_match'
            }
            
            if debug:
                print(f"  BEST: Score {best_candidate['score']:.3f} via '{best_candidate['header']}'")
                print(f"  TEXT: {best_candidate['text'][:200]}...")
        else:
            # Fallback: pick first candidate if no standard clause available
            best_candidate = all_candidates[0]
            extracted_data[attribute] = {
                'text': best_candidate['text'],
                'score': 0.0,
                'header': best_candidate['header'],
                'method': 'first_match'
            }
    
    return extracted_data

if __name__ == '__main__':
    # Example usage for testing
    contract_path = 'c:\\Users\\91916\\OneDrive\\Desktop\\hilabs\\HiLabsAIQuest_ContractsAI\\Contracts\\TN\\TN_Contract1_Redacted.pdf'
    
    print(f"Extracting text from: {contract_path}")
    full_text = extract_text_from_pdf(contract_path)
    
    if full_text:
        print("Text extracted. Now finding clauses...")
        clauses = extract_all_clauses(full_text)
        
        if clauses:
            for attribute, content in clauses.items():
                print(f"\n--- Found: {attribute} ---")
                print(content[:500].strip() + "...")
        else:
            print("Could not find any of the specified clauses in the test file.")
