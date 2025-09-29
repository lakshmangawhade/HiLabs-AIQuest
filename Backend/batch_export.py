"""
Batch Export Script
==================

Export results for multiple contracts in batch for frontend display.
"""

import os
import glob
from pathlib import Path
from main import main as run_analysis
from results_exporter import ResultsExporter
import sys


def batch_export_contracts():
    """Export results for all TN contracts."""
    
    # Find all TN contract files
    contracts_dir = Path("HiLabsAIQuest_ContractsAI/Contracts/TN")
    if not contracts_dir.exists():
        print(f"❌ Contracts directory not found: {contracts_dir}")
        return
    
    contract_files = list(contracts_dir.glob("TN_Contract*_Redacted.pdf"))
    
    if not contract_files:
        print("❌ No TN contract files found")
        return
    
    print(f"🔍 Found {len(contract_files)} contract files")
    
    # Initialize exporter
    exporter = ResultsExporter()
    exported_dirs = []
    
    for contract_file in contract_files:
        contract_name = contract_file.name
        print(f"\n📄 Processing: {contract_name}")
        
        try:
            # Run analysis and export
            from focused_extraction import FocusedExtractor
            from contract_classifier import ContractClassifier
            
            # Initialize extractor
            extractor = FocusedExtractor()
            extractor.contract_path = contract_file
            extractor.template_path = Path("HiLabsAIQuest_ContractsAI/Standard Templates/TN_Standard_Template_Redacted.pdf")
            
            # Extract attributes
            print("  🔍 Extracting attributes...")
            contract_attributes = extractor.extract_all_attributes(extractor.contract_path, contract_name)
            template_attributes = extractor.extract_all_attributes(extractor.template_path, "TN_Standard_Template_Redacted")
            
            # Classify
            print("  🤖 Running classification...")
            classifier = ContractClassifier(enable_business_rules=True)
            classification_results = classifier.classify_all_attributes(
                contract_attributes, template_attributes
            )
            
            # Export results
            print("  📤 Exporting results...")
            results_dir = exporter.export_contract_results(
                contract_name=contract_name,
                template_name="TN_Standard_Template_Redacted.pdf",
                results=classification_results,
                contract_attributes=contract_attributes,
                template_attributes=template_attributes,
                contexts=None
            )
            
            exported_dirs.append(results_dir)
            print(f"  ✅ Exported to: {results_dir}")
            
        except Exception as e:
            print(f"  ❌ Error processing {contract_name}: {e}")
            continue
    
    # Create index file
    if exported_dirs:
        print(f"\n📋 Creating index file...")
        exporter.create_index_file(exported_dirs)
        
        print(f"\n🎉 Batch export complete!")
        print(f"📁 Results saved to: results/TN/")
        print(f"🌐 Open index: results/TN/index.json")
        
        # Show summary
        print(f"\n📊 Summary:")
        for i, dir_path in enumerate(exported_dirs, 1):
            contract_name = os.path.basename(dir_path)
            summary_file = os.path.join(dir_path, "summary.json")
            
            if os.path.exists(summary_file):
                import json
                with open(summary_file, "r") as f:
                    summary = json.load(f)
                
                compliance_rate = summary["overview"]["compliance_rate"]
                total_attrs = summary["overview"]["total_attributes"]
                standard_count = summary["overview"]["standard_count"]
                
                print(f"  {i}. {contract_name}: {compliance_rate}% ({standard_count}/{total_attrs})")
    else:
        print("❌ No contracts were successfully processed")


if __name__ == "__main__":
    batch_export_contracts()
