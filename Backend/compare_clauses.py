"""
Fuzzy String Matching for Contract Classification
================================================

Implements fuzzy string matching algorithms to find approximate matches
between contract text and templates. Uses multiple similarity metrics
to handle variations in wording while maintaining the same meaning.
"""

import re
import difflib
from typing import Dict, List, Tuple, Optional, Any
import logging
from collections import Counter
import math

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """
    Fuzzy string matching for contract classification.
    
    Uses various string similarity algorithms to find approximate matches
    between contracts and templates when exact or pattern matching fails.
    """
    
    def __init__(self):
        """Initialize the fuzzy matcher with configurable parameters."""
        # Similarity thresholds for different algorithms
        self.thresholds = {
            "levenshtein": 0.85,
            "jaro_winkler": 0.90,
            "token_sort": 0.80,
            "sequence": 0.75,
            "ngram": 0.70
        }
        
        # Weights for combining different similarity scores
        self.weights = {
            "levenshtein": 0.25,
            "jaro_winkler": 0.25,
            "token_sort": 0.20,
            "sequence": 0.15,
            "ngram": 0.15
        }
        
        # Common legal synonyms and variations
        self.legal_synonyms = {
            "shall": ["will", "must", "should", "is required to"],
            "may": ["can", "is permitted to", "has the option to"],
            "prior to": ["before", "preceding", "in advance of"],
            "subsequent to": ["after", "following"],
            "pursuant to": ["according to", "in accordance with", "under"],
            "notwithstanding": ["despite", "regardless of", "even though"],
            "provided that": ["on condition that", "if", "as long as"],
            "in the event": ["if", "when", "should"],
            "compensation": ["payment", "reimbursement", "remuneration"],
            "agreement": ["contract", "arrangement", "understanding"],
            "party": ["participant", "signatory", "entity"],
            "terms": ["conditions", "provisions", "stipulations"],
        }
    
    def match(self, contract_text: str, template_text: str, 
              attribute_name: str) -> Tuple[float, Dict[str, Any], str]:
        """
        Perform fuzzy matching between contract and template text.
        
        Args:
            contract_text: Text from the contract
            template_text: Text from the template
            attribute_name: Name of the attribute being matched
            
        Returns:
            Tuple of (similarity_score, match_details, explanation)
        """
        # Preprocess texts
        contract_processed = self._preprocess_text(contract_text)
        template_processed = self._preprocess_text(template_text)
        
        # Apply synonym normalization
        contract_normalized = self._normalize_synonyms(contract_processed)
        template_normalized = self._normalize_synonyms(template_processed)
        
        # Calculate various similarity scores
        scores = {}
        
        # 1. Levenshtein distance (edit distance)
        scores["levenshtein"] = self._levenshtein_similarity(
            contract_normalized, template_normalized
        )
        
        # 2. Jaro-Winkler distance
        scores["jaro_winkler"] = self._jaro_winkler_similarity(
            contract_normalized, template_normalized
        )
        
        # 3. Token sort ratio (order-independent)
        scores["token_sort"] = self._token_sort_ratio(
            contract_normalized, template_normalized
        )
        
        # 4. Sequence matcher (longest common subsequence)
        scores["sequence"] = self._sequence_similarity(
            contract_normalized, template_normalized
        )
        
        # 5. N-gram similarity
        scores["ngram"] = self._ngram_similarity(
            contract_normalized, template_normalized, n=3
        )
        
        # Calculate weighted final score
        final_score = sum(
            scores[method] * self.weights[method] 
            for method in scores
        )
        
        # Check for structural similarity even with different words
        structure_bonus = self._check_structural_similarity(
            contract_text, template_text, attribute_name
        )
        
        # Adjust final score with structure bonus (max 10% boost)
        final_score = min(1.0, final_score + (structure_bonus * 0.1))
        
        # Generate detailed explanation
        explanation = self._generate_explanation(scores, structure_bonus, final_score)
        
        # Compile match details
        match_details = {
            "individual_scores": scores,
            "final_score": final_score,
            "structure_bonus": structure_bonus,
            "preprocessing": {
                "original_lengths": {
                    "contract": len(contract_text),
                    "template": len(template_text)
                },
                "processed_lengths": {
                    "contract": len(contract_processed),
                    "template": len(template_processed)
                }
            },
            "best_matching_segments": self._find_best_matching_segments(
                contract_normalized, template_normalized
            )
        }
        
        return final_score, match_details, explanation
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for fuzzy matching."""
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation but keep sentence structure
        text = re.sub(r'[^\w\s\.\?\!]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _normalize_synonyms(self, text: str) -> str:
        """Replace legal synonyms with canonical forms."""
        normalized = text
        
        for canonical, synonyms in self.legal_synonyms.items():
            for synonym in synonyms:
                # Use word boundaries to avoid partial replacements
                pattern = r'\b' + re.escape(synonym) + r'\b'
                normalized = re.sub(pattern, canonical, normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """Calculate Levenshtein similarity ratio."""
        if not s1 or not s2:
            return 0.0
        
        # Use dynamic programming for efficiency
        len1, len2 = len(s1), len(s2)
        
        # Create distance matrix
        dist = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        # Initialize first row and column
        for i in range(len1 + 1):
            dist[i][0] = i
        for j in range(len2 + 1):
            dist[0][j] = j
        
        # Fill the matrix
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if s1[i-1] == s2[j-1]:
                    dist[i][j] = dist[i-1][j-1]
                else:
                    dist[i][j] = 1 + min(
                        dist[i-1][j],    # deletion
                        dist[i][j-1],    # insertion
                        dist[i-1][j-1]   # substitution
                    )
        
        # Calculate similarity ratio
        max_len = max(len1, len2)
        if max_len == 0:
            return 1.0
        
        return 1.0 - (dist[len1][len2] / max_len)
    
    def _jaro_winkler_similarity(self, s1: str, s2: str) -> float:
        """Calculate Jaro-Winkler similarity."""
        if not s1 or not s2:
            return 0.0
        
        # Jaro similarity
        jaro = self._jaro_similarity(s1, s2)
        
        # Jaro-Winkler modification
        prefix_len = 0
        for i in range(min(len(s1), len(s2), 4)):  # Max prefix length of 4
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break
        
        # Jaro-Winkler formula with scaling factor p=0.1
        return jaro + (prefix_len * 0.1 * (1 - jaro))
    
    def _jaro_similarity(self, s1: str, s2: str) -> float:
        """Calculate Jaro similarity."""
        len1, len2 = len(s1), len(s2)
        
        if len1 == 0 and len2 == 0:
            return 1.0
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Calculate the match window
        match_window = max(len1, len2) // 2 - 1
        if match_window < 1:
            match_window = 1
        
        s1_matches = [False] * len1
        s2_matches = [False] * len2
        
        matches = 0
        transpositions = 0
        
        # Find matches
        for i in range(len1):
            start = max(0, i - match_window)
            end = min(i + match_window + 1, len2)
            
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break
        
        if matches == 0:
            return 0.0
        
        # Count transpositions
        k = 0
        for i in range(len1):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1
        
        # Calculate Jaro similarity
        return (matches / len1 + matches / len2 + 
                (matches - transpositions / 2) / matches) / 3
    
    def _token_sort_ratio(self, s1: str, s2: str) -> float:
        """Calculate token sort ratio (order-independent comparison)."""
        # Tokenize and sort
        tokens1 = sorted(s1.split())
        tokens2 = sorted(s2.split())
        
        # Rejoin and compare
        sorted1 = ' '.join(tokens1)
        sorted2 = ' '.join(tokens2)
        
        # Use sequence matcher for comparison
        return difflib.SequenceMatcher(None, sorted1, sorted2).ratio()
    
    def _sequence_similarity(self, s1: str, s2: str) -> float:
        """Calculate sequence similarity using difflib."""
        return difflib.SequenceMatcher(None, s1, s2).ratio()
    
    def _ngram_similarity(self, s1: str, s2: str, n: int = 3) -> float:
        """Calculate n-gram similarity."""
        if len(s1) < n or len(s2) < n:
            # Fall back to character-level comparison for short strings
            return self._sequence_similarity(s1, s2)
        
        # Generate n-grams
        ngrams1 = self._generate_ngrams(s1, n)
        ngrams2 = self._generate_ngrams(s2, n)
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(ngrams1.intersection(ngrams2))
        union = len(ngrams1.union(ngrams2))
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_ngrams(self, text: str, n: int) -> set:
        """Generate n-grams from text."""
        ngrams = set()
        
        # Character n-grams
        for i in range(len(text) - n + 1):
            ngrams.add(text[i:i+n])
        
        # Word n-grams
        words = text.split()
        for i in range(len(words) - n + 1):
            ngrams.add(' '.join(words[i:i+n]))
        
        return ngrams
    
    def _check_structural_similarity(self, contract_text: str, 
                                   template_text: str, attribute_name: str) -> float:
        """Check for structural similarity even with different wording."""
        structure_score = 0.0
        
        # Check similar paragraph count
        contract_paragraphs = len(re.split(r'\n\s*\n', contract_text))
        template_paragraphs = len(re.split(r'\n\s*\n', template_text))
        
        if contract_paragraphs == template_paragraphs:
            structure_score += 0.3
        elif abs(contract_paragraphs - template_paragraphs) <= 2:
            structure_score += 0.1
        
        # Check similar sentence count
        contract_sentences = len(re.split(r'[.!?]+', contract_text))
        template_sentences = len(re.split(r'[.!?]+', template_text))
        
        if abs(contract_sentences - template_sentences) <= 2:
            structure_score += 0.2
        
        # Check for similar numerical patterns (dates, amounts, percentages)
        contract_numbers = re.findall(r'\d+(?:\.\d+)?%?', contract_text)
        template_numbers = re.findall(r'\d+(?:\.\d+)?%?', template_text)
        
        if len(contract_numbers) == len(template_numbers):
            structure_score += 0.2
        
        # Check for similar section markers
        contract_sections = re.findall(r'(?:section|article|clause)\s*\d+', 
                                     contract_text, re.IGNORECASE)
        template_sections = re.findall(r'(?:section|article|clause)\s*\d+', 
                                     template_text, re.IGNORECASE)
        
        if len(contract_sections) == len(template_sections):
            structure_score += 0.3
        
        return min(1.0, structure_score)
    
    def _find_best_matching_segments(self, text1: str, text2: str, 
                                   segment_length: int = 50) -> List[Dict[str, Any]]:
        """Find the best matching segments between two texts."""
        matcher = difflib.SequenceMatcher(None, text1, text2)
        matches = []
        
        for match in matcher.get_matching_blocks()[:5]:  # Top 5 matches
            if match.size > 10:  # Minimum match size
                segment1 = text1[max(0, match.a - segment_length//2):
                               match.a + match.size + segment_length//2]
                segment2 = text2[max(0, match.b - segment_length//2):
                               match.b + match.size + segment_length//2]
                
                matches.append({
                    "contract_segment": segment1,
                    "template_segment": segment2,
                    "match_size": match.size,
                    "similarity": self._sequence_similarity(segment1, segment2)
                })
        
        return sorted(matches, key=lambda x: x["similarity"], reverse=True)
    
    def _generate_explanation(self, scores: Dict[str, float], 
                            structure_bonus: float, final_score: float) -> str:
        """Generate a human-readable explanation of the matching results."""
        explanations = []
        
        # Overall assessment
        if final_score >= 0.9:
            explanations.append("Very high similarity - likely the same content with minor variations")
        elif final_score >= 0.8:
            explanations.append("High similarity - same structure with some wording differences")
        elif final_score >= 0.7:
            explanations.append("Moderate similarity - similar content but notable differences")
        else:
            explanations.append("Low similarity - significant differences in content or structure")
        
        # Best performing algorithm
        best_method = max(scores.items(), key=lambda x: x[1])
        explanations.append(f"Best match: {best_method[0]} ({best_method[1]:.2f})")
        
        # Structure assessment
        if structure_bonus > 0.5:
            explanations.append("Strong structural similarity")
        elif structure_bonus > 0.2:
            explanations.append("Some structural similarity")
        
        # Specific insights
        if scores.get("token_sort", 0) > scores.get("sequence", 0):
            explanations.append("Content is similar but reordered")
        
        if scores.get("ngram", 0) > 0.8:
            explanations.append("Many common phrases detected")
        
        return "; ".join(explanations)


"""
Pattern-Based Contract Matching
===============================

Implements regex pattern matching for structural comparison of contracts.
This module identifies common patterns and structures in legal documents
to determine if a contract follows the same format as a standard template.
"""

import re
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class PatternMatcher:
    """
    Pattern-based matching for contract classification.
    
    Uses regex patterns to identify structural similarities between contracts
    and templates, even when exact text doesn't match.
    """
    
    def __init__(self):
        """Initialize the pattern matcher with common legal document patterns."""
        # Define common structural patterns in contracts
        self.structural_patterns = {
            "section_numbering": [
                r'\d+\.\d+(?:\.\d+)?',  # 1.1, 1.1.1
                r'[A-Z]\.\s*\d+',  # A. 1
                r'Article\s+[IVX]+',  # Article IV
                r'Section\s+\d+',  # Section 1
            ],
            "bullet_points": [
                r'[•·▪▫◦‣⁃]\s*',  # Various bullet symbols
                r'\([a-z]\)',  # (a), (b), (c)
                r'\d+\)',  # 1), 2), 3)
                r'[a-z]\)',  # a), b), c)
            ],
            "legal_references": [
                r'pursuant to',
                r'in accordance with',
                r'subject to',
                r'notwithstanding',
                r'hereinafter',
                r'whereas',
            ],
            "date_patterns": [
                r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY
                r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY
                r'[A-Za-z]+\s+\d{1,2},?\s+\d{4}',  # Month DD, YYYY
            ],
            "monetary_patterns": [
                r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # $1,234.56
                r'\d+(?:\.\d+)?%',  # 12.5%
                r'percent',
                r'percentage',
            ],
            "time_periods": [
                r'\d+\s*(?:days?|months?|years?)',
                r'(?:thirty|sixty|ninety)\s*\(\d+\)\s*days?',
                r'calendar\s+(?:days?|months?|years?)',
                r'business\s+(?:days?|months?|years?)',
            ]
        }
        
        # Attribute-specific patterns
        self.attribute_patterns = {
            "Medicaid Timely Filing": {
                "required_elements": [
                    r'medicaid',
                    r'(?:timely\s+filing|submission.*?claims)',
                    r'\d+\s*(?:days?|months?)',  # Time period
                ],
                "structure_patterns": [
                    r'submission\s+and\s+adjudication',
                    r'claims.*?submitted',
                    r'within.*?days',
                ],
            },
            "Medicare Timely Filing": {
                "required_elements": [
                    r'medicare',
                    r'(?:timely\s+filing|submission.*?claims)',
                    r'\d+\s*(?:days?|months?)',  # Time period
                ],
                "structure_patterns": [
                    r'submission.*?medicare.*?claims',
                    r'claims.*?submitted',
                    r'within.*?days',
                ],
            },
            "No Steerage/SOC": {
                "required_elements": [
                    r'(?:networks?|panels?)',
                    r'provider',
                ],
                "structure_patterns": [
                    r'networks\s+and\s+provider\s+panels',
                    r'standard\s+of\s+care',
                    r'steerage',
                ],
            },
            "Medicaid Fee Schedule": {
                "required_elements": [
                    r'medicaid',
                    r'(?:fee\s+schedule|reimbursement|compensation)',
                ],
                "structure_patterns": [
                    r'fee\s+schedule',
                    r'reimbursement.*?rate',
                    r'(?:professional\s+services|facility\s+services)',
                    r'\d+(?:\.\d+)?%.*?(?:medicare|medicaid)',  # Percentage of Medicare/Medicaid
                ],
            },
            "Medicare Fee Schedule": {
                "required_elements": [
                    r'medicare',
                    r'(?:fee\s+schedule|reimbursement|compensation)',
                ],
                "structure_patterns": [
                    r'fee\s+schedule',
                    r'reimbursement.*?rate',
                    r'medicare\s+advantage',
                    r'\d+(?:\.\d+)?%.*?medicare',  # Percentage of Medicare
                ],
            },
        }
    
    def match(self, contract_text: str, template_text: str, 
              attribute_name: str, context: Optional[Dict[str, Any]] = None) -> Tuple[float, Dict[str, Any], str]:
        """
        Match contract text against template using pattern recognition.
        
        Args:
            contract_text: Text from the contract
            template_text: Text from the template
            attribute_name: Name of the attribute being matched
            context: Optional context information
            
        Returns:
            Tuple of (match_score, matched_patterns, explanation)
        """
        # Normalize texts
        contract_norm = self._normalize_text(contract_text)
        template_norm = self._normalize_text(template_text)
        
        # Extract patterns from both texts
        contract_patterns = self._extract_patterns(contract_text, attribute_name)
        template_patterns = self._extract_patterns(template_text, attribute_name)
        
        # Compare structural similarity
        structure_score = self._compare_structures(contract_patterns, template_patterns)
        
        # Check attribute-specific patterns
        attribute_score = self._check_attribute_patterns(contract_text, template_text, attribute_name)
        
        # Check for table structures
        table_score = self._compare_table_structures(contract_text, template_text) if self._has_table_structure(template_text) else 0
        
        # Calculate final score
        weights = {
            "structure": 0.4,
            "attribute": 0.4,
            "table": 0.2
        }
        
        if table_score > 0:
            final_score = (
                weights["structure"] * structure_score +
                weights["attribute"] * attribute_score +
                weights["table"] * table_score
            )
        else:
            # Redistribute weights if no table
            final_score = (
                0.5 * structure_score +
                0.5 * attribute_score
            )
        
        # Generate explanation
        explanation_parts = []
        if structure_score > 0.8:
            explanation_parts.append(f"Strong structural match ({structure_score:.2f})")
        elif structure_score > 0.5:
            explanation_parts.append(f"Moderate structural match ({structure_score:.2f})")
        else:
            explanation_parts.append(f"Weak structural match ({structure_score:.2f})")
        
        if attribute_score > 0.8:
            explanation_parts.append(f"Attribute patterns match well ({attribute_score:.2f})")
        elif attribute_score > 0.5:
            explanation_parts.append(f"Some attribute patterns match ({attribute_score:.2f})")
            
        if table_score > 0:
            explanation_parts.append(f"Table structure similarity: {table_score:.2f}")
        
        explanation = "; ".join(explanation_parts)
        
        matched_patterns = {
            "contract_patterns": contract_patterns,
            "template_patterns": template_patterns,
            "structure_score": structure_score,
            "attribute_score": attribute_score,
            "table_score": table_score
        }
        
        return final_score, matched_patterns, explanation
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for pattern matching."""
        # Convert to lowercase
        text = text.lower()
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep structure
        text = re.sub(r'[^\w\s\.\,\;\:\-\(\)\[\]\{\}\/\%\$]', '', text)
        return text.strip()
    
    def _extract_patterns(self, text: str, attribute_name: str) -> Dict[str, List[str]]:
        """Extract structural patterns from text."""
        patterns_found = {
            "sections": [],
            "bullets": [],
            "legal_terms": [],
            "dates": [],
            "monetary": [],
            "time_periods": [],
            "tables": []
        }
        
        # Extract section numbers
        for pattern in self.structural_patterns["section_numbering"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            patterns_found["sections"].extend(matches)
        
        # Extract bullet points
        for pattern in self.structural_patterns["bullet_points"]:
            matches = re.findall(pattern, text)
            patterns_found["bullets"].extend(matches)
        
        # Extract legal references
        for pattern in self.structural_patterns["legal_references"]:
            if re.search(pattern, text, re.IGNORECASE):
                patterns_found["legal_terms"].append(pattern)
        
        # Extract dates
        for pattern in self.structural_patterns["date_patterns"]:
            matches = re.findall(pattern, text)
            patterns_found["dates"].extend(matches)
        
        # Extract monetary values
        for pattern in self.structural_patterns["monetary_patterns"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            patterns_found["monetary"].extend(matches)
        
        # Extract time periods
        for pattern in self.structural_patterns["time_periods"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            patterns_found["time_periods"].extend(matches)
        
        # Check for table structures
        if self._has_table_structure(text):
            patterns_found["tables"].append("table_detected")
        
        return patterns_found
    
    def _compare_structures(self, patterns1: Dict[str, List[str]], patterns2: Dict[str, List[str]]) -> float:
        """Compare structural patterns between two texts."""
        scores = []
        
        # Compare section numbering
        if patterns1["sections"] and patterns2["sections"]:
            # Check if they use the same numbering style
            style1 = self._get_numbering_style(patterns1["sections"])
            style2 = self._get_numbering_style(patterns2["sections"])
            if style1 == style2:
                scores.append(1.0)
            else:
                scores.append(0.5)
        elif not patterns1["sections"] and not patterns2["sections"]:
            scores.append(1.0)  # Both have no sections
        else:
            scores.append(0.0)
        
        # Compare bullet styles
        if patterns1["bullets"] and patterns2["bullets"]:
            common_bullets = set(patterns1["bullets"]) & set(patterns2["bullets"])
            if common_bullets:
                scores.append(1.0)
            else:
                scores.append(0.5)
        elif not patterns1["bullets"] and not patterns2["bullets"]:
            scores.append(1.0)
        else:
            scores.append(0.0)
        
        # Compare legal terminology usage
        if patterns1["legal_terms"] and patterns2["legal_terms"]:
            common_terms = set(patterns1["legal_terms"]) & set(patterns2["legal_terms"])
            total_terms = set(patterns1["legal_terms"]) | set(patterns2["legal_terms"])
            if total_terms:
                scores.append(len(common_terms) / len(total_terms))
        
        # Compare presence of dates, monetary values, time periods
        for key in ["dates", "monetary", "time_periods"]:
            if bool(patterns1[key]) == bool(patterns2[key]):
                scores.append(1.0)
            else:
                scores.append(0.5)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _get_numbering_style(self, sections: List[str]) -> str:
        """Determine the numbering style used."""
        if not sections:
            return "none"
        
        sample = sections[0]
        if re.match(r'\d+\.\d+', sample):
            return "decimal"
        elif re.match(r'[A-Z]\.\s*\d+', sample):
            return "alpha_numeric"
        elif re.match(r'Article\s+[IVX]+', sample):
            return "roman"
        elif re.match(r'Section\s+\d+', sample):
            return "section"
        else:
            return "other"
    
    def _check_attribute_patterns(self, contract_text: str, template_text: str, attribute_name: str) -> float:
        """Check for attribute-specific patterns."""
        if attribute_name not in self.attribute_patterns:
            return 0.5  # Default score for unknown attributes
        
        patterns = self.attribute_patterns[attribute_name]
        contract_lower = contract_text.lower()
        
        # Check required elements
        required_found = 0
        for pattern in patterns["required_elements"]:
            if re.search(pattern, contract_lower):
                required_found += 1
        
        required_score = required_found / len(patterns["required_elements"]) if patterns["required_elements"] else 0
        
        # Check structure patterns
        structure_found = 0
        for pattern in patterns["structure_patterns"]:
            if re.search(pattern, contract_lower):
                structure_found += 1
        
        structure_score = structure_found / len(patterns["structure_patterns"]) if patterns["structure_patterns"] else 0
        
        # Weight required elements more heavily
        return 0.7 * required_score + 0.3 * structure_score
    
    def _has_table_structure(self, text: str) -> bool:
        """Check if text contains table-like structures."""
        # Look for patterns indicating tables
        table_indicators = [
            r'\|',  # Pipe characters
            r'\t.*\t',  # Tab-separated values
            r'(?:^|\n)\s*\w+\s+\w+\s+\w+\s*(?:\n|$)',  # Column headers
            r'(?:Rate|Fee|Schedule|Percentage).*?(?:\d+%|\$\d+)',  # Table content
        ]
        
        for pattern in table_indicators:
            if re.search(pattern, text, re.MULTILINE):
                return True
        
        # Check for multiple aligned monetary values or percentages
        monetary_matches = re.findall(r'(?:\$\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:\.\d+)?%)', text)
        if len(monetary_matches) > 3:
            return True
        
        return False
    
    def _compare_table_structures(self, contract_text: str, template_text: str) -> float:
        """Compare table structures between texts."""
        # Extract table-like content
        contract_values = self._extract_table_values(contract_text)
        template_values = self._extract_table_values(template_text)
        
        if not contract_values and not template_values:
            return 1.0  # Both have no tables
        
        if not contract_values or not template_values:
            return 0.0  # One has table, other doesn't
        
        # Compare structure
        score = 0.0
        
        # Check if similar number of values
        count_ratio = min(len(contract_values), len(template_values)) / max(len(contract_values), len(template_values))
        score += count_ratio * 0.5
        
        # Check if similar types of values (percentages vs dollar amounts)
        contract_types = self._categorize_values(contract_values)
        template_types = self._categorize_values(template_values)
        
        if contract_types == template_types:
            score += 0.5
        elif len(contract_types & template_types) > 0:
            score += 0.25
        
        return score
    
    def _extract_table_values(self, text: str) -> List[str]:
        """Extract values that appear to be from tables."""
        values = []
        
        # Extract monetary values
        values.extend(re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', text))
        
        # Extract percentages
        values.extend(re.findall(r'\d+(?:\.\d+)?%', text))
        
        return values
    
    def _categorize_values(self, values: List[str]) -> set:
        """Categorize types of values found."""
        types = set()
        
        for value in values:
            if value.startswith('$'):
                types.add('monetary')
            elif value.endswith('%'):
                types.add('percentage')
        
        return types


"""
Fast Semantic Matching for Contract Classification
=================================================

Implements semantic similarity matching using lightweight models
optimized for speed. This is the final fallback when other methods
fail to find matches based on surface-level text similarity.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class SemanticMatcher:
    """
    Semantic similarity matching for contract classification.
    
    Uses fast, lightweight sentence transformers to compare semantic meaning
    between contracts and templates when surface-level matching fails.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = ".semantic_cache"):
        """
        Initialize the semantic matcher with a lightweight model.
        
        Args:
            model_name: Name of the sentence transformer model to use
            cache_dir: Directory for caching embeddings
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Load a lightweight model for fast inference
        logger.info(f"Loading semantic model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Use GPU if available for faster processing
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.model.to(self.device)
        
        # Cache for embeddings to avoid recomputation
        self.embedding_cache = {}
        self._load_cache()
        
        # Semantic similarity thresholds for different attribute types
        self.attribute_thresholds = {
            "Medicaid Timely Filing": 0.75,
            "Medicare Timely Filing": 0.75,
            "No Steerage/SOC": 0.70,
            "Medicaid Fee Schedule": 0.65,  # Lower threshold for tables
            "Medicare Fee Schedule": 0.65,   # Lower threshold for tables
        }
        
        # Keywords that boost semantic similarity for specific attributes
        self.attribute_keywords = {
            "Medicaid Timely Filing": [
                "medicaid", "timely filing", "claim submission", "days", "deadline"
            ],
            "Medicare Timely Filing": [
                "medicare", "timely filing", "claim submission", "days", "deadline"
            ],
            "No Steerage/SOC": [
                "network", "provider panel", "steerage", "standard of care", "referral"
            ],
            "Medicaid Fee Schedule": [
                "medicaid", "fee schedule", "reimbursement", "rate", "payment"
            ],
            "Medicare Fee Schedule": [
                "medicare", "fee schedule", "reimbursement", "rate", "payment"
            ],
        }
    
    def match(self, contract_text: str, template_text: str, 
              attribute_name: str) -> Tuple[float, Dict[str, Any], str]:
        """
        Perform semantic matching between contract and template text.
        
        Args:
            contract_text: Text from the contract
            template_text: Text from the template
            attribute_name: Name of the attribute being matched
            
        Returns:
            Tuple of (similarity_score, match_details, explanation)
        """
        # Preprocess texts
        contract_chunks = self._chunk_text(contract_text)
        template_chunks = self._chunk_text(template_text)
        
        # Get embeddings with caching
        contract_embeddings = self._get_embeddings(contract_chunks, f"contract_{attribute_name}")
        template_embeddings = self._get_embeddings(template_chunks, f"template_{attribute_name}")
        
        # Calculate similarity scores
        chunk_similarities = self._calculate_chunk_similarities(
            contract_embeddings, template_embeddings
        )
        
        # Calculate overall document similarity
        doc_similarity = self._calculate_document_similarity(
            contract_embeddings, template_embeddings
        )
        
        # Check for keyword presence
        keyword_score = self._calculate_keyword_score(
            contract_text, template_text, attribute_name
        )
        
        # Combine scores with weights
        weights = {
            "chunk": 0.4,
            "document": 0.4,
            "keyword": 0.2
        }
        
        final_score = (
            weights["chunk"] * chunk_similarities["max_similarity"] +
            weights["document"] * doc_similarity +
            weights["keyword"] * keyword_score
        )
        
        # Apply attribute-specific threshold adjustment
        threshold = self.attribute_thresholds.get(attribute_name, 0.7)
        
        # Generate explanation
        explanation = self._generate_explanation(
            chunk_similarities, doc_similarity, keyword_score, final_score, threshold
        )
        
        # Compile match details
        match_details = {
            "chunk_similarities": chunk_similarities,
            "document_similarity": doc_similarity,
            "keyword_score": keyword_score,
            "final_score": final_score,
            "threshold": threshold,
            "best_matching_chunks": self._find_best_matching_chunks(
                contract_chunks, template_chunks, 
                contract_embeddings, template_embeddings
            )
        }
        
        return final_score, match_details, explanation
    
    def _chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 128) -> List[str]:
        """
        Split text into overlapping chunks for better semantic matching.
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text.strip())
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence end
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def _get_embeddings(self, texts: List[str], cache_key: str) -> np.ndarray:
        """
        Get embeddings for texts with caching.
        
        Args:
            texts: List of texts to embed
            cache_key: Key for caching
            
        Returns:
            Numpy array of embeddings
        """
        if not texts:
            return np.array([])
        
        # Create a hash for the texts
        text_hash = hashlib.md5(json.dumps(texts).encode()).hexdigest()
        full_cache_key = f"{cache_key}_{text_hash}"
        
        # Check cache
        if full_cache_key in self.embedding_cache:
            return self.embedding_cache[full_cache_key]
        
        # Generate embeddings
        with torch.no_grad():
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=32  # Batch processing for speed
            )
        
        # Cache the embeddings
        self.embedding_cache[full_cache_key] = embeddings
        self._save_cache()
        
        return embeddings
    
    def _calculate_chunk_similarities(self, embeddings1: np.ndarray, 
                                    embeddings2: np.ndarray) -> Dict[str, float]:
        """Calculate similarities between chunks."""
        if len(embeddings1) == 0 or len(embeddings2) == 0:
            return {
                "max_similarity": 0.0,
                "mean_similarity": 0.0,
                "min_similarity": 0.0
            }
        
        # Calculate pairwise cosine similarities
        similarities = cosine_similarity(embeddings1, embeddings2)
        
        # Get statistics
        max_similarities = np.max(similarities, axis=1)
        
        return {
            "max_similarity": float(np.max(max_similarities)),
            "mean_similarity": float(np.mean(max_similarities)),
            "min_similarity": float(np.min(max_similarities))
        }
    
    def _calculate_document_similarity(self, embeddings1: np.ndarray, 
                                     embeddings2: np.ndarray) -> float:
        """Calculate overall document similarity."""
        if len(embeddings1) == 0 or len(embeddings2) == 0:
            return 0.0
        
        # Mean pooling for document representation
        doc_embedding1 = np.mean(embeddings1, axis=0)
        doc_embedding2 = np.mean(embeddings2, axis=0)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(
            doc_embedding1.reshape(1, -1),
            doc_embedding2.reshape(1, -1)
        )[0, 0]
        
        return float(similarity)
    
    def _calculate_keyword_score(self, contract_text: str, template_text: str, 
                               attribute_name: str) -> float:
        """Calculate keyword presence score."""
        if attribute_name not in self.attribute_keywords:
            return 0.5  # Neutral score for unknown attributes
        
        keywords = self.attribute_keywords[attribute_name]
        contract_lower = contract_text.lower()
        template_lower = template_text.lower()
        
        contract_keyword_count = sum(
            1 for keyword in keywords 
            if keyword.lower() in contract_lower
        )
        
        template_keyword_count = sum(
            1 for keyword in keywords 
            if keyword.lower() in template_lower
        )
        
        if len(keywords) == 0:
            return 0.5
        
        # Calculate presence ratio
        contract_ratio = contract_keyword_count / len(keywords)
        template_ratio = template_keyword_count / len(keywords)
        
        # Bonus if both have similar keyword presence
        if contract_ratio > 0 and template_ratio > 0:
            similarity_bonus = min(contract_ratio, template_ratio) / max(contract_ratio, template_ratio)
        else:
            similarity_bonus = 0
        
        return (contract_ratio + template_ratio) / 2 + similarity_bonus * 0.2
    
    def _find_best_matching_chunks(self, chunks1: List[str], chunks2: List[str],
                                  embeddings1: np.ndarray, embeddings2: np.ndarray,
                                  top_k: int = 3) -> List[Dict[str, Any]]:
        """Find the best matching chunk pairs."""
        if len(embeddings1) == 0 or len(embeddings2) == 0:
            return []
        
        # Calculate pairwise similarities
        similarities = cosine_similarity(embeddings1, embeddings2)
        
        # Find top matches
        matches = []
        for i in range(len(chunks1)):
            for j in range(len(chunks2)):
                matches.append({
                    "contract_chunk": chunks1[i][:200] + "..." if len(chunks1[i]) > 200 else chunks1[i],
                    "template_chunk": chunks2[j][:200] + "..." if len(chunks2[j]) > 200 else chunks2[j],
                    "similarity": float(similarities[i, j]),
                    "contract_idx": i,
                    "template_idx": j
                })
        
        # Sort by similarity and return top matches
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        return matches[:top_k]
    
    def _generate_explanation(self, chunk_similarities: Dict[str, float],
                            doc_similarity: float, keyword_score: float,
                            final_score: float, threshold: float) -> str:
        """Generate explanation for semantic matching results."""
        explanations = []
        
        # Overall semantic assessment
        if final_score >= threshold:
            explanations.append(f"Semantic match found (score: {final_score:.2f} >= threshold: {threshold:.2f})")
        else:
            explanations.append(f"Insufficient semantic similarity (score: {final_score:.2f} < threshold: {threshold:.2f})")
        
        # Chunk similarity assessment
        if chunk_similarities["max_similarity"] >= 0.9:
            explanations.append("Very high similarity in some sections")
        elif chunk_similarities["max_similarity"] >= 0.7:
            explanations.append("Good similarity in some sections")
        elif chunk_similarities["max_similarity"] >= 0.5:
            explanations.append("Moderate similarity in some sections")
        else:
            explanations.append("Low chunk-level similarity")
        
        # Document-level assessment
        if doc_similarity >= 0.8:
            explanations.append(f"Strong overall semantic alignment ({doc_similarity:.2f})")
        elif doc_similarity >= 0.6:
            explanations.append(f"Moderate overall semantic alignment ({doc_similarity:.2f})")
        else:
            explanations.append(f"Weak overall semantic alignment ({doc_similarity:.2f})")
        
        # Keyword assessment
        if keyword_score >= 0.8:
            explanations.append("Key terminology strongly present")
        elif keyword_score >= 0.5:
            explanations.append("Some key terminology present")
        else:
            explanations.append("Limited key terminology")
        
        return "; ".join(explanations)
    
    def _load_cache(self):
        """Load embedding cache from disk."""
        cache_file = self.cache_dir / "embeddings.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Convert lists back to numpy arrays
                    for key, value in cache_data.items():
                        self.embedding_cache[key] = np.array(value)
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
    
    def _save_cache(self):
        """Save embedding cache to disk."""
        cache_file = self.cache_dir / "embeddings.json"
        try:
            # Convert numpy arrays to lists for JSON serialization
            cache_data = {}
            for key, value in self.embedding_cache.items():
                cache_data[key] = value.tolist()
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self.embedding_cache.clear()
        cache_file = self.cache_dir / "embeddings.json"
        if cache_file.exists():
            cache_file.unlink()



"""
Contract Analysis Rules and Methodology Detection
================================================

Implements business logic for detecting non-standard contract terms based on 
10 key indicators of non-standard methodologies.
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class ReimbursementMethodology(Enum):
    """Types of reimbursement methodologies."""
    STANDARD_FEE_SCHEDULE = "Professional Provider Market Master Fee Schedule"
    CUSTOM_RATES = "Custom Rates"
    STATE_SPECIFIC = "State-Specific Modifications"
    SPECIAL_PROGRAMS = "Special Programs/Waivers"
    UNUSUAL_TIME_UNITS = "Unusual Time Units"
    NON_STANDARD_SERVICES = "Non-Standard Services"
    FIXED_HISTORICAL = "Fixed Historical References"
    NON_FEDERAL = "Non-Federal Methodology"
    FULL_COVERAGE = "Full Coverage/Exceptions"
    DYNAMIC_ADJUSTMENTS = "Retroactive/Dynamic Adjustments"
    SPECIAL_AFFILIATION = "Special Affiliation Rules"
    YEAR_LOCKED = "Year-Locked Rate"
    MEDICARE_BASED = "Medicare-Based"
    MEDICAID_LAB = "Medicaid Lab"
    FIXED_DOLLAR = "Fixed Dollar Amount"
    PERCENTAGE_BASED = "Percentage-Based"
    CUSTOM = "Custom Methodology"
    UNKNOWN = "Unknown"


@dataclass
class QualifierAnalysis:
    """Results of qualifier analysis."""
    has_qualifiers: bool
    qualifiers_found: List[str]
    qualifier_impact: str
    confidence: float


@dataclass
class MethodologyAnalysis:
    """Results of methodology analysis."""
    methodology_type: ReimbursementMethodology
    is_standard: bool
    confidence: float
    evidence: List[str]
    explanation: str


class ContractAnalyzer:
    """
    Analyzes contract text for non-standard terms and methodologies.
    Uses 10 key indicators to identify non-standard attributes.
    """
    
    def __init__(self):
        """Initialize the analyzer with patterns for 10 non-standard indicators."""
        
        # Qualifier patterns that indicate non-standard terms
        self.qualifier_patterns = {
            "conditional": [
                r"(?i)\b(if|when|provided that|on condition that|subject to)\b",
                r"(?i)\b(unless|except|excluding|but not)\b",
                r"(?i)\b(only if|solely|exclusively)\b",
            ],
            "limitations": [
                r"(?i)\b(up to|maximum|not to exceed|cap|ceiling)\b",
                r"(?i)\b(minimum|at least|floor|no less than)\b",
                r"(?i)\b(limited to|restricted to)\b",
            ],
            "time_based": [
                r"(?i)\b(after|before|within|during|following)\b.*\b(period|months?|years?|days?)\b",
                r"(?i)\b(effective|beginning|starting|ending|through)\b.*\b(date|period)\b",
                r"(?i)\b(retroactive|prospective)\b",
            ],
            "carve_outs": [
                r"(?i)\b(except for|excluding|other than|aside from)\b",
                r"(?i)\b(carve[- ]?out|carved out|exemption)\b",
                r"(?i)\b(not applicable to|does not apply)\b",
            ],
            "special_circumstances": [
                r"(?i)\b(in the event|in case of|upon occurrence)\b",
                r"(?i)\b(special|unique|specific) circumstances?\b",
                r"(?i)\b(case[- ]?by[- ]?case|individually determined)\b",
            ]
        }
        
        # Standard methodology indicators
        self.standard_indicators = [
            "professional provider market master fee schedule",
            "market master fee schedule",
            "professional provider fee schedule",
            "standard fee schedule",
        ]
        
        # ============================================================
        # 10 NON-STANDARD INDICATORS
        # ============================================================
        
        # 1. CUSTOM RATES - Fixed amounts or formulas not tied to official schedules
        self.custom_rates_patterns = [
            r"(?i)\$\d+(?:\.\d{2})?\s*(?:per|for)\s+\w+",
            r"(?i)(?:fixed|flat|set)\s+(?:rate|fee|amount)",
            r"(?i)\d+(?:\.\d+)?%\s*of\s*(?:charges?|billed|usual)",
            r"(?i)proprietary\s+(?:rate|fee|schedule)",
        ]
        
        # 2. STATE-SPECIFIC MODIFICATIONS
        self.state_specific_patterns = [
            r"(?i)state[- ](?:specific|determined|mandated)\s+(?:rate|program|schedule)",
            r"(?i)(?:Tennessee|Texas|California|Florida|state)\s+(?:legislation|statute|law).*?(?:rate|reimbursement)",
            r"(?i)rate\s+corridor",
            r"(?i)state[- ]administered\s+program",
        ]
        
        # 3. SPECIAL PROGRAMS OR WAIVERS
        self.special_programs_patterns = [
            r"(?i)1915\s*\([a-z]\)\s*(?:waiver|program)",
            r"(?i)\b(?:IDD|DD|HCBS|Katie\s+Beckett|TEFRA)\s+(?:waiver|program)",
            r"(?i)transitional\s+(?:services?|care|program)",
            r"(?i)behavioral\s+health\s+waiver",
            r"(?i)specialized?\s+waiver",
        ]
        
        # 4. UNUSUAL TIME UNITS OR MEASUREMENT
        self.unusual_time_patterns = [
            r"(?i)per\s+(?:15|30|45)\s*min(?:ute)?s?",
            r"(?i)per\s+(?:service\s+)?unit(?!ed)",
            r"(?i)per\s+case(?!\s+management)",
            r"(?i)per\s+encounter",
            r"(?i)per\s+episode",
        ]
        
        # 5. NON-STANDARD SERVICES
        self.non_standard_services_patterns = [
            r"(?i)family\s+residential\s+support",
            r"(?i)specialized\s+equipment",
            r"(?i)personal\s+emergency\s+response",
            r"(?i)assistive\s+technology",
            r"(?i)respite\s+care",
            r"(?i)habilitation\s+services?",
            r"(?i)(?:non-medical|ancillary)\s+(?:services?|supplies?)",
        ]
        
        # 6. FIXED HISTORICAL REFERENCES
        self.fixed_historical_patterns = [
            r"(?i)(?:19|20)\d{2}\s+(?:rate|fee|schedule|conversion\s+factor)",
            r"(?i)as\s+of\s+(?:19|20)\d{2}",
            r"(?i)(?:frozen|locked|fixed)\s+(?:at|as\s+of|from)\s+(?:19|20)\d{2}",
            r"(?i)relative\s+weight.*?(?:19|20)\d{2}",
            r"(?i)calendar\s+year\s+(?:19|20)\d{2}",
        ]
        
        # 7. NON-FEDERAL METHODOLOGIES
        self.non_federal_patterns = [
            r"(?i)(?:internal|proprietary|custom)\s+(?:methodology|fee\s+schedule)",
            r"(?i)state[- ]developed\s+(?:rate|schedule|methodology)",
            r"(?i)(?:provider|organization)[- ]specific\s+rate",
            r"(?i)negotiated\s+rate(?!.*medicare|.*medicaid|.*cms)",
        ]
        
        # 8. FULL COVERAGE OR EXCEPTIONS
        self.full_coverage_patterns = [
            r"(?i)100%\s+(?:of|reimbursement)",
            r"(?i)full\s+reimbursement",
            r"(?i)all\s+(?:supplies?|equipment|ancillary\s+costs?)\s+(?:included|covered)",
            r"(?i)inclusive\s+of\s+all\s+(?:costs?|charges?)",
        ]
        
        # 9. RETROACTIVE OR DYNAMIC ADJUSTMENTS
        self.dynamic_adjustments_patterns = [
            r"(?i)retroactive(?:ly)?\s+adjust",
            r"(?i)dynamic\s+(?:adjustment|rate|pricing)",
            r"(?i)corridor\s+(?:monitoring|modeling|adjustment)",
            r"(?i)relative\s+position.*?adjust",
            r"(?i)reconciliation.*?based\s+on",
        ]
        
        # 10. SPECIAL AFFILIATION RULES
        self.affiliation_patterns = [
            r"(?i)affiliate\s+(?:network|provider|arrangement)",
            r"(?i)coordinated\s+(?:care|program).*?(?:rate|reimbursement)",
            r"(?i)(?:ACO|accountable\s+care).*?(?:rate|methodology)",
            r"(?i)network[- ]specific\s+rate",
        ]
        
        # Standard Medicare/Medicaid percentage patterns (template compliance)
        self.standard_medicare_patterns = [
            r"(?i)\d+(?:\.\d+)?%\s*of\s*medicare(?:\s+(?:advantage|fee\s+schedule))?",
            r"(?i)\d+(?:\.\d+)?%\s*of\s*medicaid(?:\s+fee\s+schedule)?",
            r"(?i)medicare.*?rate.*?\d+(?:\.\d+)?%",
            r"(?i)medicaid.*?rate.*?\d+(?:\.\d+)?%",
        ]
        
        # Standard provisions indicating template compliance
        self.standard_provisions = [
            r"(?i)CMS.*?adjust(?:ment|s)",
            r"(?i)bad\s+debt.*?exclud",
            r"(?i)interim\s+payment",
            r"(?i)retroactive.*?reconciliation",
            r"(?i)medicare.*?fee\s+schedule",
            r"(?i)percent\s+of\s+medicare",
            r"(?i)\[.*?percent.*?medicare.*?\]",
        ]
    
    def check_non_standard_indicators(self, text: str) -> Dict[str, Tuple[bool, List[str]]]:
        """
        Check text against all 10 non-standard indicators.
        
        Returns:
            Dictionary mapping indicator name to (found, evidence_list)
        """
        results = {}
        
        # 1. Custom rates
        matches = [re.search(p, text) for p in self.custom_rates_patterns]
        evidence = [m.group() for m in matches if m]
        results["custom_rates"] = (len(evidence) > 0, evidence[:3])
        
        # 2. State-specific
        matches = [re.search(p, text) for p in self.state_specific_patterns]
        evidence = [m.group() for m in matches if m]
        results["state_specific"] = (len(evidence) > 0, evidence[:3])
        
        # 3. Special programs
        matches = [re.search(p, text) for p in self.special_programs_patterns]
        evidence = [m.group() for m in matches if m]
        results["special_programs"] = (len(evidence) > 0, evidence[:3])
        
        # 4. Unusual time units
        matches = [re.search(p, text) for p in self.unusual_time_patterns]
        evidence = [m.group() for m in matches if m]
        results["unusual_time_units"] = (len(evidence) > 0, evidence[:3])
        
        # 5. Non-standard services
        matches = [re.search(p, text) for p in self.non_standard_services_patterns]
        evidence = [m.group() for m in matches if m]
        results["non_standard_services"] = (len(evidence) > 0, evidence[:3])
        
        # 6. Fixed historical
        matches = [re.search(p, text) for p in self.fixed_historical_patterns]
        evidence = [m.group() for m in matches if m]
        results["fixed_historical"] = (len(evidence) > 0, evidence[:3])
        
        # 7. Non-federal
        matches = [re.search(p, text) for p in self.non_federal_patterns]
        evidence = [m.group() for m in matches if m]
        results["non_federal"] = (len(evidence) > 0, evidence[:3])
        
        # 8. Full coverage
        matches = [re.search(p, text) for p in self.full_coverage_patterns]
        evidence = [m.group() for m in matches if m]
        results["full_coverage"] = (len(evidence) > 0, evidence[:3])
        
        # 9. Dynamic adjustments
        matches = [re.search(p, text) for p in self.dynamic_adjustments_patterns]
        evidence = [m.group() for m in matches if m]
        results["dynamic_adjustments"] = (len(evidence) > 0, evidence[:3])
        
        # 10. Special affiliation
        matches = [re.search(p, text) for p in self.affiliation_patterns]
        evidence = [m.group() for m in matches if m]
        results["affiliation"] = (len(evidence) > 0, evidence[:3])
        
        return results
    
    def analyze_qualifiers(self, text: str, attribute_name: str) -> QualifierAnalysis:
        """
        Analyze text for qualifiers that make terms non-standard.
        """
        qualifiers_found = []
        qualifier_types = []
        
        for category, patterns in self.qualifier_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    qualifiers_found.extend(matches)
                    qualifier_types.append(category)
        
        if "Fee Schedule" in attribute_name:
            fee_qualifiers = [
                r"(?i)except.*?(?:service|procedure|code)",
                r"(?i)excluding.*?(?:service|procedure|code)",
                r"(?i)for.*?(?:service|procedure|code).*?only",
                r"(?i)applicable.*?to.*?specific",
            ]
            
            for pattern in fee_qualifiers:
                if re.search(pattern, text):
                    qualifiers_found.append(f"Fee-specific qualifier: {pattern}")
                    qualifier_types.append("fee_specific")
        
        has_qualifiers = len(qualifiers_found) > 0
        
        if not has_qualifiers:
            impact = "No qualifiers detected"
            confidence = 1.0
        elif len(qualifier_types) == 1 and qualifier_types[0] == "time_based":
            impact = "Minor time-based qualifiers only"
            confidence = 0.7
        elif len(qualifiers_found) <= 2:
            impact = "Some qualifiers present - review needed"
            confidence = 0.5
        else:
            impact = "Multiple qualifiers detected - likely non-standard"
            confidence = 0.2
        
        return QualifierAnalysis(
            has_qualifiers=has_qualifiers,
            qualifiers_found=qualifiers_found[:10],
            qualifier_impact=impact,
            confidence=confidence
        )
    
    def analyze_methodology(self, text: str, attribute_name: str) -> MethodologyAnalysis:
        """
        Analyze reimbursement methodology using 10 non-standard indicators.
        """
        text_lower = text.lower()
        
        # First check for explicit standard methodology
        for indicator in self.standard_indicators:
            if indicator in text_lower:
                return MethodologyAnalysis(
                    methodology_type=ReimbursementMethodology.STANDARD_FEE_SCHEDULE,
                    is_standard=True,
                    confidence=1.0,
                    evidence=[f"Found standard indicator: '{indicator}'"],
                    explanation="Uses standard Professional Provider Market Master Fee Schedule"
                )
        
        # Check all 10 non-standard indicators
        indicator_results = self.check_non_standard_indicators(text)
        
        # Count how many indicators triggered
        triggered = [name for name, (found, _) in indicator_results.items() if found]
        
        # If multiple non-standard indicators found, it's definitely non-standard
        if len(triggered) >= 2:
            all_evidence = []
            for name in triggered:
                _, evidence = indicator_results[name]
                all_evidence.extend(evidence)
            
            methodology_map = {
                "custom_rates": ReimbursementMethodology.CUSTOM_RATES,
                "state_specific": ReimbursementMethodology.STATE_SPECIFIC,
                "special_programs": ReimbursementMethodology.SPECIAL_PROGRAMS,
                "unusual_time_units": ReimbursementMethodology.UNUSUAL_TIME_UNITS,
                "non_standard_services": ReimbursementMethodology.NON_STANDARD_SERVICES,
                "fixed_historical": ReimbursementMethodology.FIXED_HISTORICAL,
                "non_federal": ReimbursementMethodology.NON_FEDERAL,
                "full_coverage": ReimbursementMethodology.FULL_COVERAGE,
                "dynamic_adjustments": ReimbursementMethodology.DYNAMIC_ADJUSTMENTS,
                "affiliation": ReimbursementMethodology.SPECIAL_AFFILIATION,
            }
            
            primary_methodology = methodology_map.get(triggered[0], ReimbursementMethodology.CUSTOM)
            
            return MethodologyAnalysis(
                methodology_type=primary_methodology,
                is_standard=False,
                confidence=0.90,
                evidence=all_evidence[:5],
                explanation=f"Non-standard: Multiple indicators found ({', '.join(triggered)})"
            )
        
        # Single non-standard indicator
        elif len(triggered) == 1:
            indicator_name = triggered[0]
            _, evidence = indicator_results[indicator_name]
            
            methodology_map = {
                "custom_rates": (ReimbursementMethodology.CUSTOM_RATES, "Custom rate structure"),
                "state_specific": (ReimbursementMethodology.STATE_SPECIFIC, "State-specific modifications"),
                "special_programs": (ReimbursementMethodology.SPECIAL_PROGRAMS, "Special program/waiver rates"),
                "unusual_time_units": (ReimbursementMethodology.UNUSUAL_TIME_UNITS, "Unusual time-based units"),
                "non_standard_services": (ReimbursementMethodology.NON_STANDARD_SERVICES, "Non-standard services"),
                "fixed_historical": (ReimbursementMethodology.FIXED_HISTORICAL, "Fixed historical references"),
                "non_federal": (ReimbursementMethodology.NON_FEDERAL, "Non-federal methodology"),
                "full_coverage": (ReimbursementMethodology.FULL_COVERAGE, "Full coverage exceptions"),
                "dynamic_adjustments": (ReimbursementMethodology.DYNAMIC_ADJUSTMENTS, "Dynamic adjustments"),
                "affiliation": (ReimbursementMethodology.SPECIAL_AFFILIATION, "Special affiliation rules"),
            }
            
            methodology, explanation = methodology_map.get(
                indicator_name, 
                (ReimbursementMethodology.CUSTOM, "Custom methodology")
            )
            
            return MethodologyAnalysis(
                methodology_type=methodology,
                is_standard=False,
                confidence=0.80,
                evidence=evidence,
                explanation=f"Non-standard: {explanation}"
            )
        
        # No non-standard indicators, check for standard Medicare/Medicaid patterns
        for pattern in self.standard_medicare_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                standard_provisions_found = []
                for provision_pattern in self.standard_provisions:
                    if re.search(provision_pattern, text, re.IGNORECASE):
                        match = re.search(provision_pattern, text, re.IGNORECASE)
                        if match:
                            standard_provisions_found.append(match.group())
                
                if len(standard_provisions_found) >= 2 or "Fee Schedule" in attribute_name:
                    percentage_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*of\s*(medicare|medicaid)", 
                                               text, re.IGNORECASE)
                    if percentage_match:
                        percentage = percentage_match.group(1)
                        base = percentage_match.group(2)
                        
                        return MethodologyAnalysis(
                            methodology_type=ReimbursementMethodology.STANDARD_FEE_SCHEDULE,
                            is_standard=True,
                            confidence=0.95,
                            evidence=[f"Standard template: {percentage}% of {base}", 
                                     f"Standard provisions: {len(standard_provisions_found)} found"],
                            explanation=f"Standard template with {percentage}% of {base}"
                        )
        
        # No clear indicators either way
        return MethodologyAnalysis(
            methodology_type=ReimbursementMethodology.UNKNOWN,
            is_standard=True,
            confidence=0.5,
            evidence=["No clear methodology pattern found"],
            explanation="Cannot determine methodology - assuming standard"
        )
    
    def should_override_to_nonstandard(self, text: str, attribute_name: str, 
                                     current_match_type: str) -> Tuple[bool, str]:
        """
        Determine if a match should be overridden to non-standard.
        """
        # Only apply to fuzzy and semantic matches
        if current_match_type not in ["fuzzy", "semantic"]:
            return False, ""
        
        # Check for non-standard indicators
        indicator_results = self.check_non_standard_indicators(text)
        triggered = [name for name, (found, _) in indicator_results.items() if found]
        
        if len(triggered) >= 2:
            return True, f"Multiple non-standard indicators: {', '.join(triggered[:3])}"
        
        # Analyze qualifiers for fuzzy matches
        if current_match_type == "fuzzy":
            qualifier_analysis = self.analyze_qualifiers(text, attribute_name)
            if qualifier_analysis.has_qualifiers and qualifier_analysis.confidence < 0.5:
                qualifiers_str = ", ".join(qualifier_analysis.qualifiers_found[:3])
                return True, f"Contains non-standard qualifiers: {qualifiers_str}"
        
        # Analyze methodology for fee schedules
        if "Fee Schedule" in attribute_name:
            methodology_analysis = self.analyze_methodology(text, attribute_name)
            if not methodology_analysis.is_standard and methodology_analysis.confidence > 0.7:
                return True, methodology_analysis.explanation
        
        return False, ""
    
    def enhance_classification(self, text: str, attribute_name: str, 
                             match_type: str, original_confidence: float) -> Tuple[bool, float, str]:
        """
        Enhance classification with business rules.
        """
        should_override, override_reason = self.should_override_to_nonstandard(
            text, attribute_name, match_type
        )
        
        if should_override:
            return False, 0.0, override_reason
        
        # For fee schedules, boost confidence if standard methodology is found
        if "Fee Schedule" in attribute_name:
            methodology_analysis = self.analyze_methodology(text, attribute_name)
            if methodology_analysis.is_standard:
                adjusted_confidence = min(1.0, original_confidence * 1.1)
                return True, adjusted_confidence, "Standard fee schedule methodology confirmed"
        
        return True, original_confidence, "Original classification maintained"


"""
Contract Classification System
==============================

A hierarchical classification system that compares contracts against standard templates
using multiple matching strategies in order of precision:
1. Exact Match - Character-by-character comparison
2. Regex Pattern Match - Pattern-based structural matching
3. Fuzzy Match - Approximate string matching with configurable threshold
4. Semantic Match - Fast semantic similarity using lightweight models

The system automatically falls through to less strict methods if higher precision methods fail.
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchType(Enum):
    """Types of matching methods used in classification."""
    EXACT = "exact"
    REGEX = "regex"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    NO_MATCH = "no_match"


@dataclass
class ClassificationResult:
    """Result of contract classification."""
    is_standard: bool
    match_type: MatchType
    confidence: float
    explanation: str
    attribute_name: str
    matched_sections: Optional[Dict[str, Any]] = None


class ContractClassifier:
    """
    Hierarchical contract classification system.
    
    Compares contracts against standard templates using multiple matching strategies
    in order of decreasing strictness.
    """
    
    def __init__(self, 
                 exact_threshold: float = 1.0,
                 regex_threshold: float = 0.9,
                 fuzzy_threshold: float = 0.8,
                 semantic_threshold: float = 0.7,
                 enable_business_rules: bool = True):
        """
        Initialize the classifier with configurable thresholds.
        
        Args:
            exact_threshold: Minimum similarity for exact match (default 1.0)
            regex_threshold: Minimum pattern match score (default 0.9)
            fuzzy_threshold: Minimum fuzzy match score (default 0.8)
            semantic_threshold: Minimum semantic similarity (default 0.7)
            enable_business_rules: Enable business rule analysis (default True)
        """
        self.exact_threshold = exact_threshold
        self.regex_threshold = regex_threshold
        self.fuzzy_threshold = fuzzy_threshold
        self.semantic_threshold = semantic_threshold
        self.enable_business_rules = enable_business_rules
        
        # Initialize matchers (lazy loading)
        self._pattern_matcher = None
        self._fuzzy_matcher = None
        self._semantic_matcher = None
        self._contract_analyzer = None
        
    @property
    def pattern_matcher(self):
        """Lazy load pattern matcher."""
        if self._pattern_matcher is None:
            self._pattern_matcher = PatternMatcher()
        return self._pattern_matcher
        
    @property
    def fuzzy_matcher(self):
        """Lazy load fuzzy matcher."""
        if self._fuzzy_matcher is None:
            self._fuzzy_matcher = FuzzyMatcher()
        return self._fuzzy_matcher
        
    @property
    def semantic_matcher(self):
        """Lazy load semantic matcher."""
        if self._semantic_matcher is None:
            self._semantic_matcher = SemanticMatcher()
        return self._semantic_matcher
    
    @property
    def contract_analyzer(self):
        """Lazy load contract analyzer."""
        if self._contract_analyzer is None:
            self._contract_analyzer = ContractAnalyzer()
        return self._contract_analyzer
    
    def classify_contract(self, 
                         contract_text: str, 
                         template_text: str, 
                         attribute_name: str,
                         context: Optional[Dict[str, Any]] = None) -> ClassificationResult:
        """
        Classify a contract section against a template using hierarchical matching.
        
        Args:
            contract_text: Text from the contract to classify
            template_text: Text from the standard template
            attribute_name: Name of the attribute being compared
            context: Optional context information about the attribute
            
        Returns:
            ClassificationResult with classification details
        """
        if not contract_text or not template_text:
            return ClassificationResult(
                is_standard=False,
                match_type=MatchType.NO_MATCH,
                confidence=0.0,
                explanation="Missing text for comparison",
                attribute_name=attribute_name
            )
        
        logger.info(f"Classifying attribute: {attribute_name}")
        
        # Step 1: Try exact match
        result = self._try_exact_match(contract_text, template_text, attribute_name)
        if result.is_standard:
            logger.info(f"✅ Exact match found for {attribute_name}")
            return result
            
        # Step 2: Try regex pattern matching
        result = self._try_regex_match(contract_text, template_text, attribute_name, context)
        if result.is_standard:
            logger.info(f"✅ Regex pattern match found for {attribute_name}")
            return result
            
        # Step 3: Try fuzzy matching
        result = self._try_fuzzy_match(contract_text, template_text, attribute_name)
        if result.is_standard:
            logger.info(f"✅ Fuzzy match found for {attribute_name}")
            return result
            
        # Step 4: Try semantic matching
        result = self._try_semantic_match(contract_text, template_text, attribute_name)
        if result.is_standard:
            logger.info(f"✅ Semantic match found for {attribute_name}")
            return result
            
        # No match found
        logger.info(f"❌ No match found for {attribute_name}")
        return ClassificationResult(
            is_standard=False,
            match_type=MatchType.NO_MATCH,
            confidence=0.0,
            explanation="No matching method succeeded",
            attribute_name=attribute_name
        )
    
    def _try_exact_match(self, contract_text: str, template_text: str, attribute_name: str) -> ClassificationResult:
        """Try exact text matching."""
        # Normalize texts for comparison
        normalized_contract = self._normalize_text(contract_text)
        normalized_template = self._normalize_text(template_text)
        
        # Check for exact match
        if normalized_contract == normalized_template:
            return ClassificationResult(
                is_standard=True,
                match_type=MatchType.EXACT,
                confidence=1.0,
                explanation="Exact text match",
                attribute_name=attribute_name
            )
        
        # Check for placeholder replacement (e.g., [Fee Schedule] -> actual values)
        if self._is_placeholder_match(contract_text, template_text):
            return ClassificationResult(
                is_standard=True,
                match_type=MatchType.EXACT,
                confidence=0.95,
                explanation="Exact match with placeholder replacement",
                attribute_name=attribute_name
            )
        
        return ClassificationResult(
            is_standard=False,
            match_type=MatchType.EXACT,
            confidence=0.0,
            explanation="No exact match found",
            attribute_name=attribute_name
        )
    
    def _try_regex_match(self, contract_text: str, template_text: str, 
                        attribute_name: str, context: Optional[Dict[str, Any]] = None) -> ClassificationResult:
        """Try regex pattern matching."""
        try:
            match_score, matched_patterns, explanation = self.pattern_matcher.match(
                contract_text, template_text, attribute_name, context
            )
            
            # Adjust threshold for Medicare/Medicaid Fee Schedules with placeholder patterns
            adjusted_threshold = self.regex_threshold
            if "Fee Schedule" in attribute_name and self._has_medicare_placeholder_pattern(template_text, contract_text):
                adjusted_threshold = max(0.8, self.regex_threshold - 0.1)  # Lower threshold for placeholder replacement
                explanation += f"; Adjusted threshold for Medicare fee schedule placeholder replacement"
            
            is_standard = match_score >= adjusted_threshold
            
            return ClassificationResult(
                is_standard=is_standard,
                match_type=MatchType.REGEX,
                confidence=match_score,
                explanation=explanation,
                attribute_name=attribute_name,
                matched_sections={"patterns": matched_patterns}
            )
        except Exception as e:
            logger.error(f"Regex matching error: {e}")
            return ClassificationResult(
                is_standard=False,
                match_type=MatchType.REGEX,
                confidence=0.0,
                explanation=f"Regex matching failed: {str(e)}",
                attribute_name=attribute_name
            )
    
    def _try_fuzzy_match(self, contract_text: str, template_text: str, attribute_name: str) -> ClassificationResult:
        """Try fuzzy string matching."""
        try:
            similarity_score, match_details, explanation = self.fuzzy_matcher.match(
                contract_text, template_text, attribute_name
            )
            
            is_standard = similarity_score >= self.fuzzy_threshold
            
            # Apply business rules if enabled
            if is_standard and self.enable_business_rules:
                enhanced_standard, enhanced_confidence, business_explanation = \
                    self.contract_analyzer.enhance_classification(
                        contract_text, attribute_name, "fuzzy", similarity_score
                    )
                
                if not enhanced_standard:
                    # Override to non-standard based on business rules
                    return ClassificationResult(
                        is_standard=False,
                        match_type=MatchType.FUZZY,
                        confidence=enhanced_confidence,
                        explanation=f"{explanation}; OVERRIDE: {business_explanation}",
                        attribute_name=attribute_name,
                        matched_sections={"fuzzy_details": match_details, "business_rule_override": True}
                    )
                elif enhanced_confidence != similarity_score:
                    # Confidence was adjusted
                    similarity_score = enhanced_confidence
                    explanation = f"{explanation}; {business_explanation}"
            
            return ClassificationResult(
                is_standard=is_standard,
                match_type=MatchType.FUZZY,
                confidence=similarity_score,
                explanation=explanation,
                attribute_name=attribute_name,
                matched_sections={"fuzzy_details": match_details}
            )
        except Exception as e:
            logger.error(f"Fuzzy matching error: {e}")
            return ClassificationResult(
                is_standard=False,
                match_type=MatchType.FUZZY,
                confidence=0.0,
                explanation=f"Fuzzy matching failed: {str(e)}",
                attribute_name=attribute_name
            )
    
    def _try_semantic_match(self, contract_text: str, template_text: str, attribute_name: str) -> ClassificationResult:
        """Try semantic similarity matching."""
        try:
            similarity_score, semantic_details, explanation = self.semantic_matcher.match(
                contract_text, template_text, attribute_name
            )
            
            is_standard = similarity_score >= self.semantic_threshold
            
            # Apply business rules if enabled - especially important for methodology differences
            if is_standard and self.enable_business_rules:
                enhanced_standard, enhanced_confidence, business_explanation = \
                    self.contract_analyzer.enhance_classification(
                        contract_text, attribute_name, "semantic", similarity_score
                    )
                
                if not enhanced_standard:
                    # Override to non-standard based on business rules
                    return ClassificationResult(
                        is_standard=False,
                        match_type=MatchType.SEMANTIC,
                        confidence=enhanced_confidence,
                        explanation=f"{explanation}; OVERRIDE: {business_explanation}",
                        attribute_name=attribute_name,
                        matched_sections={"semantic_details": semantic_details, "business_rule_override": True}
                    )
                elif enhanced_confidence != similarity_score:
                    # Confidence was adjusted
                    similarity_score = enhanced_confidence
                    explanation = f"{explanation}; {business_explanation}"
            
            return ClassificationResult(
                is_standard=is_standard,
                match_type=MatchType.SEMANTIC,
                confidence=similarity_score,
                explanation=explanation,
                attribute_name=attribute_name,
                matched_sections={"semantic_details": semantic_details}
            )
        except Exception as e:
            logger.error(f"Semantic matching error: {e}")
            return ClassificationResult(
                is_standard=False,
                match_type=MatchType.SEMANTIC,
                confidence=0.0,
                explanation=f"Semantic matching failed: {str(e)}",
                attribute_name=attribute_name
            )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove page numbers, headers, footers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        # Standardize punctuation
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"['']", "'", text)
        # Convert to lowercase
        return text.lower()
    
    def _is_placeholder_match(self, contract_text: str, template_text: str) -> bool:
        """Check if contract matches template with placeholder replacement."""
        # Enhanced approach for Medicare/Medicaid fee schedule placeholders
        placeholder_indicators = [
            r'\[.*?\]',  # [Fee Schedule], [XX], [Percent of Medicare]
            r'\(XX%?\)',  # (XX%), (XX)
            r'XX%?',     # XX%, XX
            r'█+',       # Redacted blocks
            r'\$X+',     # $XXX
            r'_{3,}',    # Multiple underscores
        ]
        
        # Check if template has any placeholders
        has_placeholders = any(
            re.search(pattern, template_text) 
            for pattern in placeholder_indicators
        )
        
        if not has_placeholders:
            return False
        
        # Enhanced placeholder detection for Medicare fee schedules
        # Look for specific Medicare/Medicaid placeholder patterns
        medicare_placeholder_patterns = [
            (r'\[Specific Medicare Fee Schedule\]', r'Medicare (?:Physician )?Fee Schedule'),
            (r'\[Percent of\s+Medicare\]', r'(?:ninety|one hundred|thirty five|sixty five|eighty|seventy|fifty)\s+percent\s*\(\d+%?\)'),
            (r'\[Percent of\s+Medicare\]', r'\d+(?:\.\d+)?%'),
            (r'\[.*?Fee Schedule.*?\]', r'Medicare.*?Fee Schedule'),
            (r'\[.*?percent.*?\]', r'\d+(?:\.\d+)?%'),
        ]
        
        # Try Medicare-specific placeholder matching first
        template_normalized = template_text
        contract_normalized = contract_text
        
        # Apply Medicare-specific replacements
        for template_pattern, contract_pattern in medicare_placeholder_patterns:
            if re.search(template_pattern, template_text, re.IGNORECASE):
                # Replace template placeholder with generic marker
                template_normalized = re.sub(template_pattern, 'MEDICARE_PLACEHOLDER', template_normalized, flags=re.IGNORECASE)
                # Replace contract values with same marker
                contract_normalized = re.sub(contract_pattern, 'MEDICARE_PLACEHOLDER', contract_normalized, flags=re.IGNORECASE)
        
        # General placeholder normalization
        for pattern in placeholder_indicators:
            template_normalized = re.sub(pattern, 'PLACEHOLDER', template_normalized)
        
        # Replace numbers/percentages in contract with PLACEHOLDER
        contract_normalized = re.sub(r'\d+(?:\.\d+)?%?', 'PLACEHOLDER', contract_normalized)
        contract_normalized = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', 'PLACEHOLDER', contract_normalized)
        
        # Normalize whitespace and common variations
        template_normalized = re.sub(r'\s+', ' ', template_normalized.strip().lower())
        contract_normalized = re.sub(r'\s+', ' ', contract_normalized.strip().lower())
        
        # Remove common document artifacts (fix: assign back to variables)
        template_normalized = re.sub(r'tennessee enterprise provider agreement.*?#', '', template_normalized)
        template_normalized = re.sub(r'©.*?\d{4}.*?inc\.?', '', template_normalized)
        template_normalized = re.sub(r'\d{2}/\d{2}/\d{4}', '', template_normalized)
        template_normalized = re.sub(r'contraxx id #', '', template_normalized)
        
        contract_normalized = re.sub(r'tennessee enterprise provider agreement.*?#', '', contract_normalized)
        contract_normalized = re.sub(r'©.*?\d{4}.*?inc\.?', '', contract_normalized)
        contract_normalized = re.sub(r'\d{2}/\d{2}/\d{4}', '', contract_normalized)
        contract_normalized = re.sub(r'contraxx id #', '', contract_normalized)
        
        # Calculate similarity
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, template_normalized, contract_normalized).ratio()
        
        # More lenient threshold for Medicare fee schedules with clear placeholder patterns
        if re.search(r'medicare.*?fee schedule', template_text, re.IGNORECASE):
            return similarity >= 0.7  # Lower threshold for Medicare fee schedules
        
        # Standard threshold for other cases
        return similarity >= 0.85
    
    def _has_medicare_placeholder_pattern(self, template_text: str, contract_text: str) -> bool:
        """Check if template has Medicare placeholders and contract has corresponding values."""
        # Check for Medicare fee schedule placeholders in template
        medicare_placeholders = [
            r'\[Specific Medicare Fee Schedule\]',
            r'\[Percent of\s+Medicare\]',
            r'\[.*?Medicare.*?\]',
            r'\[.*?Fee Schedule.*?\]',
        ]
        
        has_placeholder = any(
            re.search(pattern, template_text, re.IGNORECASE) 
            for pattern in medicare_placeholders
        )
        
        if not has_placeholder:
            return False
        
        # Check for corresponding values in contract
        medicare_values = [
            r'Medicare.*?Fee Schedule.*?(?:multiplied by|at)',
            r'\d+(?:\.\d+)?%.*?(?:of )?Medicare',
            r'(?:ninety|one hundred|thirty five|sixty five|eighty|seventy|fifty)\s+percent',
        ]
        
        has_values = any(
            re.search(pattern, contract_text, re.IGNORECASE)
            for pattern in medicare_values
        )
        
        return has_values
    
    def classify_all_attributes(self, 
                               contract_attributes: Dict[str, str],
                               template_attributes: Dict[str, str],
                               contexts: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, ClassificationResult]:
        """
        Classify all attributes in a contract.
        
        Args:
            contract_attributes: Dictionary of attribute_name -> contract_text
            template_attributes: Dictionary of attribute_name -> template_text
            contexts: Optional dictionary of attribute contexts
            
        Returns:
            Dictionary of attribute_name -> ClassificationResult
        """
        results = {}
        
        for attribute_name in contract_attributes:
            contract_text = contract_attributes.get(attribute_name, "")
            template_text = template_attributes.get(attribute_name, "")
            context = contexts.get(attribute_name) if contexts else None
            
            result = self.classify_contract(
                contract_text, 
                template_text, 
                attribute_name,
                context
            )
            
            results[attribute_name] = result
        
        return results
    
    def get_classification_summary(self, results: Dict[str, ClassificationResult]) -> Dict[str, Any]:
        """
        Generate a summary of classification results.
        
        Args:
            results: Dictionary of classification results
            
        Returns:
            Summary statistics and insights
        """
        total = len(results)
        standard_count = sum(1 for r in results.values() if r.is_standard)
        
        match_type_counts = {}
        for result in results.values():
            match_type = result.match_type.value
            match_type_counts[match_type] = match_type_counts.get(match_type, 0) + 1
        
        avg_confidence = sum(r.confidence for r in results.values()) / total if total > 0 else 0
        
        return {
            "total_attributes": total,
            "standard_count": standard_count,
            "non_standard_count": total - standard_count,
            "compliance_rate": (standard_count / total * 100) if total > 0 else 0,
            "match_type_distribution": match_type_counts,
            "average_confidence": avg_confidence,
            "attributes_by_match_type": {
                match_type: [
                    attr for attr, result in results.items() 
                    if result.match_type.value == match_type
                ]
                for match_type in match_type_counts
            }
        }
