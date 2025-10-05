"""
Focused extraction for TN_Contract1_Redacted vs TN_Standard_Template_Redacted
Implements exact structural matching for 5 specific attributes.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from pypdf import PdfReader
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# OCR Configuration
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class FocusedExtractor:
    def __init__(self):
        self.base_dir = Path("C:/Users/Lakshman/Desktop/Hilabssharwan/HiLabsAIQuest_ContractsAI")
        self.debug_dir = Path("debug/focused")
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Target files
        self.contract_path = self.base_dir / "Contracts//TN_Contract2_Redacted.pdf"
        self.template_path = self.base_dir / "Standard Templates/TN_Standard_Template_Redacted.pdf"
        
        # Attribute definitions with precise location context
        self.attribute_contexts = {
            "Medicaid Timely Filing": {
                "agreement": "MEDICAID/COVERKIDS COMMUNITY CARE) PARTICIPATION ATTACHMENT TO THE PROVIDER AGREEMENT",
                "article": "ARTICLE III COMPENSATION AND AUDIT",
                "section": "3.1",
                "subsections": ["3.1.1", "3.1.2", "3.1.3"],
                "keywords": ["medicaid", "coverkids", "timely filing", "claims", "submission"]
            },
            "Medicare Timely Filing": {
                "agreement": "MEDICARE ADVANTAGE PARTICIPATION ATTACHMENT TO THE PROVIDER AGREEMENT",
                "article": "ARTICLE VI COMPENSATIN AND AUDIT",
                "section": "6.1", 
                "subsections": ["6.1.1", "6.1.2", "6.1.3"],
                "keywords": ["medicare advantage", "timely filing", "claims", "submission"]
            },
            "No Steerage/SOC": {
                "agreement": "PROVIDER AGREEMENT",
                "article": "ARTICLE II SERVICES/OBLIGATIONS",
                "section": "2.11 Networks and Provider Panels",
                "subsections": [],
                "keywords": ["networks", "provider panels", "steerage", "standard of care"]
            },
            "Medicaid Fee Schedule": {
                "agreement": "COMPENSATION SCHEDULE (\"ACS\")",
                "article": "ARTICLE IV SPECIFIC REIMBURSEMENT TERMS",
                "section": "MEDICAID",
                "subsections": [],
                "keywords": ["medicaid", "fee schedule", "reimbursement", "compensation"]
            },
            "Medicare Fee Schedule": {
                "agreement": "COMPENSATION SCHEDULE (\"ACS\")",
                "article": "ARTICLE IV SPECIFIC REIMBURSEMENT TERMS", 
                "section": "MEDICARE ADVANTAGE",
                "subsections": [],
                "keywords": ["medicare advantage", "fee schedule", "reimbursement", "compensation"]
            }
        }

    def extract_text_from_pdf(self, pdf_path: Path, debug: bool = True) -> str:
        """Extract text using hybrid OCR approach."""
        contract_name = pdf_path.stem
        
        if debug:
            print(f"\n{'='*60}")
            print(f"Extracting text from: {contract_name}")
            print(f"{'='*60}")
        
        try:
            # First pass: Check pages with pypdf
            reader = PdfReader(str(pdf_path))
            page_texts = []
            ocr_needed = []
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                page_texts.append(text)
                needs_ocr = len(text.strip()) < 100
                ocr_needed.append(needs_ocr)
                
                if debug:
                    print(f"Page {i+1}: {len(text)} chars direct, OCR needed: {needs_ocr}")
            
            # Second pass: OCR where needed
            if any(ocr_needed):
                if debug:
                    print(f"Performing OCR on {sum(ocr_needed)} pages...")
                
                doc = fitz.open(str(pdf_path))
                for i, page in enumerate(doc):
                    if ocr_needed[i]:
                        try:
                            pix = page.get_pixmap(dpi=300)
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            ocr_text = pytesseract.image_to_string(img, config='--psm 6')
                            page_texts[i] = ocr_text
                            
                            if debug:
                                print(f"  Page {i+1} OCR: {len(ocr_text)} chars extracted")
                        except Exception as e:
                            if debug:
                                print(f"  Page {i+1} OCR failed: {e}")
                doc.close()
            
            full_text = "\n".join(page_texts)
            
            # Cache the text
            cache_path = self.debug_dir / f"{contract_name}_full_text.txt"
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            if debug:
                print(f"Total text: {len(full_text)} chars")
                print(f"Cached to: {cache_path}")
            
            return full_text
            
        except Exception as e:
            print(f"Error extracting from {pdf_path}: {e}")
            return ""

    def find_attribute_section(self, text: str, attribute: str, debug: bool = True) -> str:
        """Find the specific section for an attribute using precise location context."""
        context = self.attribute_contexts[attribute]
        
        if debug:
            print(f"\n--- Searching for {attribute} ---")
            print(f"Agreement: {context['agreement']}")
            print(f"Article: {context['article']}")
            print(f"Section: {context['section']}")
        
        best_section = ""
        best_score = 0
        
        # Strategy 1: Direct section search with MORE PRECISE patterns
        section_patterns = []
        
        if attribute == "Medicaid Timely Filing":
            # Look specifically for section 3.1 and its subsections
            section_patterns = [
                r"(?i)3\.1\s+Submission\s+and\s+Adjudication\s+of\s+Medicaid\s+Claims",
                r"(?i)ARTICLE\s+III.*?COMPENSATION.*?AUDIT.*?3\.1\s+Submission",
                r"(?i)3\.1\s+.*?Medicaid\s+Claims"
            ]
        elif attribute == "Medicare Timely Filing":
            # Look specifically for Article VI section 6.1
            section_patterns = [
                r"(?i)ARTICLE\s+VI.*?COMPENSATION.*?AUDIT.*?6\.1",
                r"(?i)6\.1\s+Submission.*?Medicare.*?Advantage.*?Claims",
                r"(?i)6\.1.*?Medicare.*?Claims"
            ]
        elif attribute == "No Steerage/SOC":
            # Look specifically for section 2.11
            section_patterns = [
                r"(?i)2\.11\s+Networks\s+and\s+Provider\s+Panels",
                r"(?i)^2\.11\s+.*?Networks.*?Panels"
            ]
        elif attribute == "Medicaid Fee Schedule":
            # Look for MEDICAID section that appears after MEDICARE in contracts
            # This is typically after "updates, or changes." line
            section_patterns = [
                r"(?i)updates,\s+or\s+changes\.\s*MEDICAID",
                r"(?i)^\s*MEDICAID\s*\n.*?For purposes of determining",
                r"(?i)MEDICAID\s+For purposes of determining.*?Rate"
            ]
        elif attribute == "Medicare Fee Schedule":
            # Look for ARTICLE IV with MEDICARE ADVANTAGE subheading - need to capture tables
            section_patterns = [
                r"(?i)ARTICLE\s+IV.*?SPECIFIC\s+REIMBURSEMENT.*?MEDICARE\s+ADVANTAGE",
                r"(?i)MEDICARE\s+ADVANTAGE[\s\S]*?(?:Fee|Rate|Schedule|Reimbursement)",
                r"(?i)COMPENSATION\s+SCHEDULE.*?MEDICARE"
            ]
        
        # Search for each pattern
        for pattern in section_patterns:
            matches = list(re.finditer(pattern, text))
            
            if debug and matches:
                print(f"  Pattern '{pattern}' found {len(matches)} matches")
            
            for match in matches:
                # Different extraction strategies based on attribute type
                if attribute == "Medicaid Timely Filing":
                    # Start exactly at 3.1 and get through 3.1.3
                    start = match.start()
                    # Look for end at section 3.2 or 3.3
                    end_match = re.search(r"(?i)3\.[23]\s+", text[start:start+5000])
                    if end_match:
                        end = start + end_match.start()
                    else:
                        end = min(len(text), start + 3000)
                    candidate = text[start:end].strip()
                    
                elif attribute == "Medicare Timely Filing":
                    # Start exactly at 6.1 and get through 6.1.3
                    start = match.start()
                    # Look for end at section 6.2 or next article
                    end_match = re.search(r"(?i)(6\.[23]\s+|ARTICLE\s+VII)", text[start:start+5000])
                    if end_match:
                        end = start + end_match.start()
                    else:
                        end = min(len(text), start + 3000)
                    candidate = text[start:end].strip()
                    
                elif attribute == "No Steerage/SOC":
                    # Start exactly at 2.11
                    start = match.start()
                    # Look for end at section 2.12
                    end_match = re.search(r"(?i)2\.12\s+", text[start:start+3000])
                    if end_match:
                        end = start + end_match.start()
                    else:
                        end = min(len(text), start + 2000)
                    candidate = text[start:end].strip()
                    
                elif attribute in ["Medicaid Fee Schedule", "Medicare Fee Schedule"]:
                    # For fee schedules, we need to capture tables
                    # Special handling for MEDICAID which comes after MEDICARE
                    if attribute == "Medicaid Fee Schedule" and "updates" in pattern:
                        # Start right at MEDICAID word
                        medicaid_pos = text[match.start():match.end()].find("MEDICAID")
                        if medicaid_pos >= 0:
                            start = match.start() + medicaid_pos
                        else:
                            start = match.start()
                    else:
                        start = match.start()
                    
                    # Extended search for table content - up to 7000 chars for full tables
                    if attribute == "Medicare Fee Schedule":
                        # For Medicare, stop before MEDICAID section
                        table_end_patterns = [
                            r"(?i)^MEDICAID\s*$",  # Stop at MEDICAID section
                            r"(?i)updates,\s+or\s+changes\.\s*MEDICAID",  # Stop before MEDICAID
                            r"(?i)Tennessee\s+Enterprise\s+Provider\s+Agreement",  # Document footer
                            r"(?i)©\s*202\d",  # Copyright line
                            r"(?i)ARTICLE\s+[V-Z]",  # Next article
                        ]
                    else:
                        # For Medicaid, use different end patterns
                        table_end_patterns = [
                            r"(?i)Tennessee\s+Enterprise\s+Provider\s+Agreement",  # Document footer
                            r"(?i)©\s*202\d",  # Copyright line
                            r"(?i)ARTICLE\s+[V-Z]",  # Next article
                        ]
                    
                    # Search up to 7000 chars for table content
                    search_text = text[start:start+7000]
                    end = start + 7000  # Default
                    
                    for end_pattern in table_end_patterns:
                        end_match = re.search(end_pattern, search_text)
                        if end_match and end_match.start() > 1000:  # Ensure we get substantial content
                            end = start + end_match.start()
                            break
                    
                    candidate = text[start:end].strip()
                    
                    # For Medicaid, ensure we have the table content
                    if attribute == "Medicaid Fee Schedule":
                        # Look for TennCare/CoverKids table indicators
                        if "TennCare" in candidate or "CoverKids" in candidate or "Professional Services" in candidate:
                            # Good, we have the right content
                            pass
                        else:
                            # Try to extend to get table content
                            extended_end = min(len(text), end + 3000)
                            extended_text = text[start:extended_end]
                            if "TennCare" in extended_text or "CoverKids" in extended_text:
                                candidate = extended_text.strip()
                else:
                    # Default extraction
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 2000)
                    candidate = text[start:end].strip()
                
                # Score based on keyword presence
                score = sum(1 for keyword in context['keywords'] 
                          if keyword.lower() in candidate.lower())
                
                # Bonus points for finding the exact section number
                if context['section'].lower() in candidate.lower():
                    score += 2
                
                # Bonus for finding article reference
                if context['article'].lower() in candidate.lower():
                    score += 1
                
                if debug:
                    print(f"    Candidate score: {score}")
                    print(f"    Preview: {candidate[:150]}...")
                
                if score > best_score:
                    best_section = candidate
                    best_score = score
        
        # Strategy 2: Special handling for fee schedules to find ARTICLE IV
        if not best_section and attribute in ["Medicaid Fee Schedule", "Medicare Fee Schedule"]:
            if debug:
                print("  Special search for ARTICLE IV fee schedules...")
            
            # Find ARTICLE IV SPECIFIC REIMBURSEMENT TERMS
            article_pattern = r"(?i)ARTICLE\s+IV\s+SPECIFIC\s+REIMBURSEMENT\s+TERMS"
            article_matches = list(re.finditer(article_pattern, text))
            
            if article_matches:
                for article_match in article_matches:
                    article_start = article_match.start()
                    # Search within this article for the specific subsection
                    article_text = text[article_start:article_start+10000]
                    
                    if attribute == "Medicaid Fee Schedule":
                        # Look for MEDICAID subsection within or after ARTICLE IV
                        # Sometimes MEDICAID appears after MEDICARE ADVANTAGE section
                        medicaid_patterns = [
                            r"(?i)^MEDICAID\s*$",
                            r"(?i)^MEDICAID\s*\n",
                            r"(?i)updates, or changes\.\s*MEDICAID"
                        ]
                        
                        for medicaid_pattern in medicaid_patterns:
                            medicaid_match = re.search(medicaid_pattern, article_text, re.MULTILINE)
                            if medicaid_match:
                                start = article_start + medicaid_match.start()
                                # If pattern includes preceding text, adjust start
                                if "updates" in medicaid_pattern:
                                    # Move to actual MEDICAID word
                                    adjust_match = re.search(r"MEDICAID", text[start:start+100])
                                    if adjust_match:
                                        start = start + adjust_match.start()
                                
                                # Find end - look for next article or end of document
                                end_patterns = [
                                    r"(?i)ARTICLE\s+[V-Z]",
                                    r"(?i)Tennessee\s+Enterprise\s+Provider\s+Agreement",
                                    r"(?i)©\s*202\d.*Tennessee"
                                ]
                                
                                end = start + 5000  # Default
                                for end_pattern in end_patterns:
                                    end_match = re.search(end_pattern, text[start+100:start+7000])
                                    if end_match:
                                        end = start + 100 + end_match.start()
                                        break
                                
                                candidate = text[start:end].strip()
                                
                                # Verify we have table content
                                if len(candidate) > 100 and ("Fee Schedule" in candidate or "%" in candidate or "Per Service" in candidate):
                                    best_section = candidate
                                    best_score = 10  # High score for exact match
                                    if debug:
                                        print(f"  Found MEDICAID section with tables")
                                    break
                    
                    elif attribute == "Medicare Fee Schedule":
                        # Look for MEDICARE ADVANTAGE subsection within ARTICLE IV
                        medicare_pattern = r"(?i)MEDICARE\s+ADVANTAGE"
                        medicare_match = re.search(medicare_pattern, article_text)
                        if medicare_match:
                            start = article_start + medicare_match.start()
                            # Find end - stop before MEDICAID section
                            end_patterns = [
                                r"(?i)^MEDICAID\s*$",  # Stop at MEDICAID section
                                r"(?i)updates,\s+or\s+changes\.\s*MEDICAID",  # Stop before MEDICAID
                                r"(?i)ARTICLE\s+[V-Z]"  # Next article
                            ]
                            
                            end = start + 5000  # Default
                            for end_pattern in end_patterns:
                                end_match = re.search(end_pattern, text[start:start+5000], re.MULTILINE)
                                if end_match:
                                    end = start + end_match.start()
                                    break
                            
                            candidate = text[start:end].strip()
                            
                            if len(candidate) > 100:
                                best_section = candidate
                                best_score = 10  # High score for exact match
                                if debug:
                                    print(f"  Found MEDICARE ADVANTAGE section in ARTICLE IV")
        
        # Strategy 3: Look for specific agreement attachments
        if not best_section:
            if debug:
                print("  Trying agreement attachment search...")
            
            # Look for the specific attachment headers
            attachment_patterns = {
                "Medicaid Timely Filing": [
                    r"(?i)medicaid.*?coverkids.*?community.*?care.*?participation.*?attachment",
                    r"(?i)participation.*?attachment.*?medicaid"
                ],
                "Medicare Timely Filing": [
                    r"(?i)medicare.*?advantage.*?participation.*?attachment",
                    r"(?i)participation.*?attachment.*?medicare"
                ],
                "No Steerage/SOC": [
                    r"(?i)provider.*?agreement",
                    r"(?i)article.*?ii.*?services.*?obligations"
                ],
                "Medicaid Fee Schedule": [
                    r"(?i)compensation.*?schedule.*?acs",
                    r"(?i)article.*?iv.*?specific.*?reimbursement"
                ],
                "Medicare Fee Schedule": [
                    r"(?i)compensation.*?schedule.*?acs",
                    r"(?i)article.*?iv.*?specific.*?reimbursement"
                ]
            }
            
            if attribute in attachment_patterns:
                for pattern in attachment_patterns[attribute]:
                    matches = list(re.finditer(pattern, text))
                    
                    for match in matches:
                        # Extract a larger context around attachment headers
                        start = max(0, match.start() - 500)
                        end = min(len(text), match.end() + 3000)
                        candidate = text[start:end].strip()
                        
                        score = sum(1 for keyword in context['keywords'] 
                                  if keyword.lower() in candidate.lower())
                        
                        if score > best_score:
                            best_section = candidate
                            best_score = score
        
        # Strategy 3: Table detection for fee schedules
        if attribute in ["Medicaid Fee Schedule", "Medicare Fee Schedule"] and not best_section:
            if debug:
                print("  Trying table detection for fee schedule...")
            
            # Look for table-like structures with rates/percentages
            table_patterns = [
                r"(?i)(?:medicaid|medicare).*?(?:rate|fee|schedule).*?(?:\d+%|\$\d+|\d+\.\d+)",
                r"(?i)(?:rate|fee|schedule).*?(?:medicaid|medicare).*?(?:\d+%|\$\d+|\d+\.\d+)",
                r"(?i)(?:\d+%|\$\d+|\d+\.\d+).*?(?:medicaid|medicare).*?(?:rate|fee|schedule)"
            ]
            
            for pattern in table_patterns:
                matches = list(re.finditer(pattern, text))
                
                for match in matches:
                    start = max(0, match.start() - 1000)
                    end = min(len(text), match.end() + 1000)
                    candidate = text[start:end].strip()
                    
                    score = sum(1 for keyword in context['keywords'] 
                              if keyword.lower() in candidate.lower())
                    
                    if score > best_score:
                        best_section = candidate
                        best_score = score
        
        if debug:
            print(f"  Final score: {best_score}")
            if best_section:
                print(f"  Extracted {len(best_section)} chars")
            else:
                print("  No section found!")
        
        return best_section

    def extract_all_attributes(self, text: str, document_name: str, debug: bool = True) -> Dict[str, str]:
        """Extract all 5 attributes from the document text."""
        if debug:
            print(f"\n{'='*50}")
            print(f"EXTRACTING ATTRIBUTES FROM: {document_name}")
            print(f"{'='*50}")
        
        extracted = {}
        
        for attribute in self.attribute_contexts.keys():
            section_text = self.find_attribute_section(text, attribute, debug)
            extracted[attribute] = section_text
            
            # Save individual attribute to file for inspection
            attr_file = self.debug_dir / f"{document_name}_{attribute.replace('/', '_')}.txt"
            with open(attr_file, 'w', encoding='utf-8') as f:
                f.write(f"=== {attribute} ===\n")
                f.write(f"Context: {self.attribute_contexts[attribute]}\n")
                f.write(f"{'='*50}\n")
                f.write(section_text)
            
            if debug:
                print(f"\n✓ {attribute}: {len(section_text)} chars extracted")
                print(f"  Saved to: {attr_file}")
        
        return extracted

    def exact_structural_match(self, contract_text: str, template_text: str, attribute: str) -> Tuple[bool, str, float]:
        """
        Compare contract and template text for exact structural match.
        Returns (is_match, explanation, similarity_score)
        """
        if not contract_text or not template_text:
            return False, "Missing text for comparison", 0.0
        
        # Normalize texts for comparison
        def normalize_text(text):
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text.strip())
            # Remove page numbers, headers, footers
            text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
            # Standardize punctuation
            text = re.sub(r'["""]', '"', text)
            text = re.sub(r"['']", "'", text)
            return text.lower()
        
        norm_contract = normalize_text(contract_text)
        norm_template = normalize_text(template_text)
        
        # Calculate basic similarity
        contract_words = set(norm_contract.split())
        template_words = set(norm_template.split())
        
        if not template_words:
            return False, "Template text is empty", 0.0
        
        intersection = contract_words.intersection(template_words)
        union = contract_words.union(template_words)
        jaccard_similarity = len(intersection) / len(union) if union else 0.0
        
        # Check for placeholder patterns
        placeholder_patterns = [
            r'\[.*?\]',  # [Fee Schedule]
            r'\(XX%\)',  # (XX%)
            r'XX%',      # XX%
            r'█+',       # Redacted blocks
            r'\$X+',     # $XXX
            r'_+',       # Underscores
        ]
        
        template_has_placeholders = any(re.search(pattern, template_text) for pattern in placeholder_patterns)
        
        # Structural similarity check
        def get_structure(text):
            # Extract numbers, percentages, key structural elements
            numbers = re.findall(r'\d+(?:\.\d+)?%?', text)
            bullets = re.findall(r'[•\-\*]\s*', text)
            sections = re.findall(r'\d+\.\d+(?:\.\d+)?', text)
            return {
                'numbers': numbers,
                'bullet_count': len(bullets),
                'section_count': len(sections)
            }
        
        contract_structure = get_structure(contract_text)
        template_structure = get_structure(template_text)
        
        # Determine match
        is_exact_match = False
        explanation = []
        
        # Enhanced structural matching logic
        if jaccard_similarity >= 0.8:
            is_exact_match = True
            explanation.append(f"High text similarity: {jaccard_similarity:.2f}")
        elif jaccard_similarity >= 0.6:
            if template_has_placeholders:
                # Check if contract has actual values where template has placeholders
                is_exact_match = True
                explanation.append(f"Good similarity with placeholder replacement: {jaccard_similarity:.2f}")
            else:
                explanation.append(f"Moderate similarity but no clear placeholder pattern: {jaccard_similarity:.2f}")
        elif jaccard_similarity >= 0.4:
            # Special case: Check if this is a table/fee schedule with structural similarity
            if attribute in ["Medicaid Fee Schedule", "Medicare Fee Schedule"]:
                # Look for percentage/dollar patterns in both texts
                contract_numbers = re.findall(r'\d+(?:\.\d+)?%|\$\d+(?:\.\d+)?', contract_text)
                template_numbers = re.findall(r'\d+(?:\.\d+)?%|\$\d+(?:\.\d+)?', template_text)
                
                if contract_numbers and (template_has_placeholders or not template_numbers):
                    is_exact_match = True
                    explanation.append(f"Table structure with values replacing placeholders: {jaccard_similarity:.2f}")
                else:
                    explanation.append(f"Moderate similarity, checking for structural patterns: {jaccard_similarity:.2f}")
            else:
                explanation.append(f"Moderate text similarity: {jaccard_similarity:.2f}")
        else:
            explanation.append(f"Low text similarity: {jaccard_similarity:.2f}")
        
        # Structure comparison
        if contract_structure['section_count'] == template_structure['section_count']:
            explanation.append("Section structure matches")
        else:
            explanation.append(f"Section count differs: {contract_structure['section_count']} vs {template_structure['section_count']}")
        
        return is_exact_match, "; ".join(explanation), jaccard_similarity

    def run_focused_analysis(self):
        """Run the focused analysis on TN_Contract1 vs TN_Standard_Template."""
        print("🎯 FOCUSED ANALYSIS: TN_Contract1 vs TN_Standard_Template")
        print("="*70)
        
        # Extract text from both documents
        print("\n📄 STEP 1: TEXT EXTRACTION")
        contract_text = self.extract_text_from_pdf(self.contract_path)
        template_text = self.extract_text_from_pdf(self.template_path)
        
        if not contract_text or not template_text:
            print("❌ Failed to extract text from one or both documents")
            return
        
        # Extract attributes from both documents
        print("\n🔍 STEP 2: ATTRIBUTE EXTRACTION")
        contract_attributes = self.extract_all_attributes(contract_text, "TN_Contract1", debug=True)
        template_attributes = self.extract_all_attributes(template_text, "TN_Standard_Template", debug=True)
        
        # Compare each attribute
        print("\n⚖️  STEP 3: EXACT STRUCTURAL MATCHING")
        results = {}
        
        for attribute in self.attribute_contexts.keys():
            print(f"\n--- Comparing {attribute} ---")
            
            contract_attr = contract_attributes.get(attribute, "")
            template_attr = template_attributes.get(attribute, "")
            
            is_match, explanation, similarity = self.exact_structural_match(
                contract_attr, template_attr, attribute
            )
            
            classification = "STANDARD" if is_match else "NON-STANDARD"
            
            results[attribute] = {
                'classification': classification,
                'is_exact_match': is_match,
                'similarity_score': similarity,
                'explanation': explanation,
                'contract_text_length': len(contract_attr),
                'template_text_length': len(template_attr),
                'contract_preview': contract_attr[:200] + "..." if contract_attr else "[NO TEXT]",
                'template_preview': template_attr[:200] + "..." if template_attr else "[NO TEXT]"
            }
            
            print(f"  Result: {classification}")
            print(f"  Similarity: {similarity:.3f}")
            print(f"  Explanation: {explanation}")
            print(f"  Contract text: {len(contract_attr)} chars")
            print(f"  Template text: {len(template_attr)} chars")
        
        # Save results
        results_file = self.debug_dir / "focused_analysis_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Summary
        print(f"\n📊 SUMMARY")
        print("="*50)
        standard_count = sum(1 for r in results.values() if r['is_exact_match'])
        total_count = len(results)
        
        print(f"Total attributes analyzed: {total_count}")
        print(f"Standard matches: {standard_count}")
        print(f"Non-standard: {total_count - standard_count}")
        print(f"Average similarity: {sum(r['similarity_score'] for r in results.values()) / total_count:.3f}")
        
        print(f"\n💾 Results saved to: {results_file}")
        print(f"🔍 Debug files saved to: {self.debug_dir}/")
        
        # Generate detailed recommendations
        self.generate_recommendations(results)
        
        return results
    
    def generate_recommendations(self, results):
        """Generate specific recommendations for improving accuracy."""
        print(f"\n🔧 RECOMMENDATIONS FOR IMPROVEMENT")
        print("="*60)
        
        for attribute, result in results.items():
            if not result['is_exact_match']:
                print(f"\n❌ {attribute}:")
                
                if result['contract_text_length'] == 0:
                    print("  • Issue: No text extracted from contract")
                    print("  • Action: Review extraction patterns and search for alternative section headers")
                    print("  • Check: Look for attachment documents or different article numbering")
                
                elif result['similarity_score'] < 0.3:
                    print("  • Issue: Very low similarity - likely extracting wrong section")
                    print("  • Action: Refine search patterns to target correct content")
                    print("  • Check: Verify section numbers and article references")
                
                elif result['similarity_score'] < 0.6:
                    print("  • Issue: Moderate similarity - may need structural analysis")
                    print("  • Action: Check if contract uses tables/different formatting")
                    print("  • Check: Look for placeholder replacement patterns")
                
                print(f"  • Current similarity: {result['similarity_score']:.3f}")
                print(f"  • Text lengths: Contract={result['contract_text_length']}, Template={result['template_text_length']}")
            else:
                print(f"\n✅ {attribute}: GOOD MATCH (similarity: {result['similarity_score']:.3f})")
        
        print(f"\n📋 NEXT STEPS:")
        print("1. Run the improved extraction again to see if Medicaid Timely Filing is now found")
        print("2. Manually review the extracted fee schedule sections for table structures")
        print("3. Consider if Medicare Fee Schedule might actually be STANDARD due to placeholder replacement")
        print("4. Once satisfied with single contract, expand to all contracts")
        print("5. Add additional parameters (beyond exact structural match) incrementally")
    
    def print_all_extracted_attributes(self):
        """Print all extracted attributes in a readable format for review."""
        print(f"\n{'='*80}")
        print("📋 ALL EXTRACTED ATTRIBUTES - DETAILED VIEW")
        print(f"{'='*80}")
        
        # Read the contract and template texts
        contract_text = self.extract_text_from_pdf(self.contract_path, debug=False)
        template_text = self.extract_text_from_pdf(self.template_path, debug=False)
        
        if not contract_text or not template_text:
            print("❌ Failed to extract text from documents")
            return
        
        # Extract attributes
        contract_attributes = self.extract_all_attributes(contract_text, "TN_Contract1", debug=False)
        template_attributes = self.extract_all_attributes(template_text, "TN_Standard_Template", debug=False)
        
        for i, attribute in enumerate(self.attribute_contexts.keys(), 1):
            print(f"\n{'='*80}")
            print(f"📄 ATTRIBUTE {i}: {attribute}")
            print(f"{'='*80}")
            
            contract_text = contract_attributes.get(attribute, "")
            template_text = template_attributes.get(attribute, "")
            
            print(f"\n🔵 CONTRACT TEXT ({len(contract_text)} chars):")
            print("-" * 60)
            if contract_text:
                # Print first 1000 chars with line breaks preserved
                display_text = contract_text[:1000]
                if len(contract_text) > 1000:
                    display_text += f"\n\n... [TRUNCATED - Total length: {len(contract_text)} chars] ..."
                print(display_text)
            else:
                print("❌ NO TEXT EXTRACTED")
            
            print(f"\n🟢 TEMPLATE TEXT ({len(template_text)} chars):")
            print("-" * 60)
            if template_text:
                # Print first 1000 chars with line breaks preserved
                display_text = template_text[:1000]
                if len(template_text) > 1000:
                    display_text += f"\n\n... [TRUNCATED - Total length: {len(template_text)} chars] ..."
                print(display_text)
            else:
                print("❌ NO TEXT EXTRACTED")
            
            # Show comparison
            if contract_text and template_text:
                is_match, explanation, similarity = self.exact_structural_match(
                    contract_text, template_text, attribute
                )
                print(f"\n⚖️  COMPARISON RESULT:")
                print(f"   Classification: {'✅ STANDARD' if is_match else '❌ NON-STANDARD'}")
                print(f"   Similarity Score: {similarity:.3f}")
                print(f"   Explanation: {explanation}")
            
            print(f"\n{'='*80}")
        
        print(f"\n🎯 SUMMARY:")
        print(f"Contract: {self.contract_path.name}")
        print(f"Template: {self.template_path.name}")
        print(f"Total Attributes: {len(self.attribute_contexts)}")
        
        # Count successful extractions
        contract_success = sum(1 for attr in contract_attributes.values() if attr)
        template_success = sum(1 for attr in template_attributes.values() if attr)
        
        print(f"Contract Extractions: {contract_success}/{len(self.attribute_contexts)}")
        print(f"Template Extractions: {template_success}/{len(self.attribute_contexts)}")
        print(f"{'='*80}")


if __name__ == "__main__":
    extractor = FocusedExtractor()
    results = extractor.run_focused_analysis()
    
    # Print all extracted attributes for detailed review
    print(f"\n" + "="*80)
    print("🔍 DETAILED ATTRIBUTE EXTRACTION REVIEW")
    print("="*80)
    extractor.print_all_extracted_attributes()
