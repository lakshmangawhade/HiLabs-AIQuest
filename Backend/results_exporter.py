"""
Results Exporter for Frontend Display
====================================

Exports classification results in a structured format suitable for frontend display.
Creates organized folders and JSON files for easy consumption by web applications.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from compare_clauses import ClassificationResult


class ResultsExporter:
    """Exports classification results in frontend-friendly format."""
    
    def __init__(self, base_output_dir: str = "results"):
        """
        Initialize the results exporter.
        
        Args:
            base_output_dir: Base directory for all results
        """
        self.base_output_dir = base_output_dir
        self.ensure_directory_exists(base_output_dir)
    
    def ensure_directory_exists(self, directory: str):
        """Ensure directory exists, create if it doesn't."""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def export_contract_results(self, 
                               contract_name: str,
                               template_name: str,
                               results: Dict[str, ClassificationResult],
                               contract_attributes: Dict[str, str],
                               template_attributes: Dict[str, str],
                               contexts: Optional[Dict[str, Dict[str, Any]]] = None,
                               state: str = "TN") -> str:
        """
        Export results for a single contract in frontend-friendly format.
        
        Args:
            contract_name: Name of the contract file
            template_name: Name of the template file
            results: Classification results
            contract_attributes: Contract attribute texts
            template_attributes: Template attribute texts
            contexts: Optional context information
            state: State abbreviation (TN or WA) for directory structure
            
        Returns:
            Path to the exported results directory
        """
        # Create state-specific contract directory
        contract_dir = os.path.join(self.base_output_dir, state, contract_name.replace(".pdf", ""))
        self.ensure_directory_exists(contract_dir)
        
        # Generate timestamp for this analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create main results file
        main_results = self._create_main_results(
            contract_name, template_name, results, timestamp
        )
        
        # Create detailed results for each attribute
        detailed_results = self._create_detailed_results(
            results, contract_attributes, template_attributes, contexts
        )
        
        # Create summary statistics
        summary = self._create_summary(results)
        
        # Create frontend-ready data structure
        frontend_data = self._create_frontend_data(
            contract_name, template_name, results, summary, timestamp
        )
        
        # Save all files
        self._save_json_file(
            os.path.join(contract_dir, "main_results.json"), 
            main_results
        )
        
        self._save_json_file(
            os.path.join(contract_dir, "detailed_results.json"), 
            detailed_results
        )
        
        self._save_json_file(
            os.path.join(contract_dir, "summary.json"), 
            summary
        )
        
        self._save_json_file(
            os.path.join(contract_dir, "frontend_data.json"), 
            frontend_data
        )
        
        # Create individual attribute files for easy access
        self._create_attribute_files(contract_dir, results, contract_attributes, template_attributes)
        
        # Create HTML preview file
        self._create_html_preview(contract_dir, frontend_data)
        
        print(f"✅ Results exported to: {contract_dir}")
        return contract_dir
    
    def _create_main_results(self, 
                           contract_name: str,
                           template_name: str,
                           results: Dict[str, ClassificationResult],
                           timestamp: str) -> Dict[str, Any]:
        """Create main results structure."""
        return {
            "metadata": {
                "contract_name": contract_name,
                "template_name": template_name,
                "analysis_timestamp": timestamp,
                "total_attributes": len(results),
                "export_version": "1.0"
            },
            "results": {
                attribute_name: {
                    "is_standard": result.is_standard,
                    "match_type": result.match_type.value,
                    "confidence": round(result.confidence, 3),
                    "explanation": result.explanation,
                    "attribute_name": result.attribute_name
                }
                for attribute_name, result in results.items()
            }
        }
    
    def _create_detailed_results(self,
                                results: Dict[str, ClassificationResult],
                                contract_attributes: Dict[str, str],
                                template_attributes: Dict[str, str],
                                contexts: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Create detailed results with full text and context."""
        detailed = {}
        
        for attribute_name, result in results.items():
            contract_text = contract_attributes.get(attribute_name, "")
            template_text = template_attributes.get(attribute_name, "")
            context = contexts.get(attribute_name) if contexts else {}
            
            detailed[attribute_name] = {
                "classification": {
                    "is_standard": result.is_standard,
                    "match_type": result.match_type.value,
                    "confidence": round(result.confidence, 3),
                    "explanation": result.explanation,
                    "matched_sections": result.matched_sections
                },
                "texts": {
                    "contract_text": contract_text,
                    "template_text": template_text,
                    "contract_length": len(contract_text),
                    "template_length": len(template_text)
                },
                "context": context
            }
        
        return detailed
    
    def _create_summary(self, results: Dict[str, ClassificationResult]) -> Dict[str, Any]:
        """Create summary statistics."""
        total = len(results)
        standard_count = sum(1 for r in results.values() if r.is_standard)
        non_standard_count = total - standard_count
        
        # Match type distribution
        match_types = {}
        for result in results.values():
            match_type = result.match_type.value
            match_types[match_type] = match_types.get(match_type, 0) + 1
        
        # Confidence statistics
        confidences = [r.confidence for r in results.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        min_confidence = min(confidences) if confidences else 0
        max_confidence = max(confidences) if confidences else 0
        
        # Standard vs non-standard breakdown
        standard_attributes = [name for name, result in results.items() if result.is_standard]
        non_standard_attributes = [name for name, result in results.items() if not result.is_standard]
        
        return {
            "overview": {
                "total_attributes": total,
                "standard_count": standard_count,
                "non_standard_count": non_standard_count,
                "compliance_rate": round((standard_count / total * 100), 1) if total > 0 else 0
            },
            "match_type_distribution": match_types,
            "confidence_stats": {
                "average": round(avg_confidence, 3),
                "minimum": round(min_confidence, 3),
                "maximum": round(max_confidence, 3)
            },
            "attribute_lists": {
                "standard": standard_attributes,
                "non_standard": non_standard_attributes
            }
        }
    
    def _create_frontend_data(self,
                             contract_name: str,
                             template_name: str,
                             results: Dict[str, ClassificationResult],
                             summary: Dict[str, Any],
                             timestamp: str) -> Dict[str, Any]:
        """Create frontend-optimized data structure."""
        # Convert results to frontend-friendly format
        attributes = []
        for attribute_name, result in results.items():
            attributes.append({
                "id": attribute_name.lower().replace(" ", "_").replace("/", "_"),
                "name": attribute_name,
                "status": "standard" if result.is_standard else "non_standard",
                "match_type": result.match_type.value,
                "confidence": round(result.confidence, 3),
                "explanation": result.explanation,
                "details": {
                    "match_type_label": self._get_match_type_label(result.match_type.value),
                    "confidence_level": self._get_confidence_level(result.confidence),
                    "status_icon": "✅" if result.is_standard else "❌",
                    "status_color": "green" if result.is_standard else "red"
                }
            })
        
        return {
            "contract_info": {
                "contract_name": contract_name,
                "template_name": template_name,
                "analysis_date": timestamp,
                "contract_id": contract_name.replace(".pdf", "").lower()
            },
            "summary": summary,
            "attributes": attributes,
            "charts_data": {
                "compliance_pie": {
                    "standard": summary["overview"]["standard_count"],
                    "non_standard": summary["overview"]["non_standard_count"]
                },
                "match_types": summary["match_type_distribution"],
                "confidence_distribution": self._create_confidence_distribution(results)
            }
        }
    
    def _get_match_type_label(self, match_type: str) -> str:
        """Get human-readable label for match type."""
        labels = {
            "exact": "Exact Match",
            "regex": "Pattern Match", 
            "fuzzy": "Fuzzy Match",
            "semantic": "Semantic Match",
            "no_match": "No Match"
        }
        return labels.get(match_type, match_type.title())
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level description."""
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.8:
            return "High"
        elif confidence >= 0.7:
            return "Medium"
        elif confidence >= 0.5:
            return "Low"
        else:
            return "Very Low"
    
    def _create_confidence_distribution(self, results: Dict[str, ClassificationResult]) -> Dict[str, int]:
        """Create confidence distribution for charts."""
        distribution = {
            "0.9-1.0": 0,
            "0.8-0.9": 0,
            "0.7-0.8": 0,
            "0.5-0.7": 0,
            "0.0-0.5": 0
        }
        
        for result in results.values():
            conf = result.confidence
            if conf >= 0.9:
                distribution["0.9-1.0"] += 1
            elif conf >= 0.8:
                distribution["0.8-0.9"] += 1
            elif conf >= 0.7:
                distribution["0.7-0.8"] += 1
            elif conf >= 0.5:
                distribution["0.5-0.7"] += 1
            else:
                distribution["0.0-0.5"] += 1
        
        return distribution
    
    def _create_attribute_files(self,
                               contract_dir: str,
                               results: Dict[str, ClassificationResult],
                               contract_attributes: Dict[str, str],
                               template_attributes: Dict[str, str]):
        """Create individual files for each attribute."""
        attributes_dir = os.path.join(contract_dir, "attributes")
        self.ensure_directory_exists(attributes_dir)
        
        for attribute_name, result in results.items():
            # Create safe filename
            safe_name = attribute_name.lower().replace(" ", "_").replace("/", "_")
            
            attribute_data = {
                "attribute_name": attribute_name,
                "classification": {
                    "is_standard": result.is_standard,
                    "match_type": result.match_type.value,
                    "confidence": round(result.confidence, 3),
                    "explanation": result.explanation
                },
                "texts": {
                    "contract": contract_attributes.get(attribute_name, ""),
                    "template": template_attributes.get(attribute_name, "")
                }
            }
            
            self._save_json_file(
                os.path.join(attributes_dir, f"{safe_name}.json"),
                attribute_data
            )
    
    def _create_html_preview(self, contract_dir: str, frontend_data: Dict[str, Any]):
        """Create HTML preview file for quick viewing."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contract Analysis Results - {frontend_data['contract_info']['contract_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #eee; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card h3 {{ margin: 0 0 10px 0; color: #333; }}
        .summary-card .value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .attributes {{ }}
        .attribute {{ margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }}
        .attribute.standard {{ border-left: 4px solid #28a745; }}
        .attribute.non_standard {{ border-left: 4px solid #dc3545; }}
        .attribute-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .attribute-name {{ font-weight: bold; font-size: 1.1em; }}
        .status {{ padding: 4px 8px; border-radius: 4px; font-size: 0.9em; }}
        .status.standard {{ background: #d4edda; color: #155724; }}
        .status.non_standard {{ background: #f8d7da; color: #721c24; }}
        .details {{ font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Contract Analysis Results</h1>
            <p><strong>Contract:</strong> {frontend_data['contract_info']['contract_name']}</p>
            <p><strong>Template:</strong> {frontend_data['contract_info']['template_name']}</p>
            <p><strong>Analysis Date:</strong> {frontend_data['contract_info']['analysis_date']}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Attributes</h3>
                <div class="value">{frontend_data['summary']['overview']['total_attributes']}</div>
            </div>
            <div class="summary-card">
                <h3>Standard</h3>
                <div class="value" style="color: #28a745;">{frontend_data['summary']['overview']['standard_count']}</div>
            </div>
            <div class="summary-card">
                <h3>Non-Standard</h3>
                <div class="value" style="color: #dc3545;">{frontend_data['summary']['overview']['non_standard_count']}</div>
            </div>
            <div class="summary-card">
                <h3>Compliance Rate</h3>
                <div class="value">{frontend_data['summary']['overview']['compliance_rate']}%</div>
            </div>
        </div>
        
        <div class="attributes">
            <h2>Attribute Details</h2>
"""
        
        for attr in frontend_data['attributes']:
            status_class = attr['status']
            html_content += f"""
            <div class="attribute {status_class}">
                <div class="attribute-header">
                    <div class="attribute-name">{attr['name']}</div>
                    <div class="status {status_class}">
                        {attr['details']['status_icon']} {attr['status'].title()}
                    </div>
                </div>
                <div class="details">
                    <strong>Match Type:</strong> {attr['details']['match_type_label']} | 
                    <strong>Confidence:</strong> {attr['confidence']} ({attr['details']['confidence_level']}) | 
                    <strong>Explanation:</strong> {attr['explanation']}
                </div>
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>
"""
        
        with open(os.path.join(contract_dir, "preview.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
    
    def _save_json_file(self, filepath: str, data: Dict[str, Any]):
        """Save data as JSON file with proper formatting."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create_index_file(self, contract_dirs: List[str]):
        """Create an index file listing all contract results."""
        index_data = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "total_contracts": len(contract_dirs)
            },
            "contracts": []
        }
        
        for contract_dir in contract_dirs:
            contract_name = os.path.basename(contract_dir)
            summary_file = os.path.join(contract_dir, "summary.json")
            
            if os.path.exists(summary_file):
                with open(summary_file, "r", encoding="utf-8") as f:
                    summary = json.load(f)
                
                index_data["contracts"].append({
                    "contract_name": contract_name,
                    "directory": contract_dir,
                    "summary": summary["overview"],
                    "preview_url": f"{contract_dir}/preview.html"
                })
        
        # Sort by compliance rate (highest first)
        index_data["contracts"].sort(
            key=lambda x: x["summary"]["compliance_rate"], 
            reverse=True
        )
        
        self._save_json_file(
            os.path.join(self.base_output_dir, "TN", "index.json"),
            index_data
        )
        
        print(f"✅ Index file created: {os.path.join(self.base_output_dir, 'TN', 'index.json')}")


def export_results(contract_name: str,
                  template_name: str,
                  results: Dict[str, ClassificationResult],
                  contract_attributes: Dict[str, str],
                  template_attributes: Dict[str, str],
                  contexts: Optional[Dict[str, Dict[str, Any]]] = None) -> str:
    """
    Convenience function to export results.
    
    Returns:
        Path to the exported results directory
    """
    exporter = ResultsExporter()
    return exporter.export_contract_results(
        contract_name, template_name, results, 
        contract_attributes, template_attributes, contexts
    )
