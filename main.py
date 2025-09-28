import os
import json
import argparse
from pathlib import Path
from extract_clauses import extract_text_from_pdf, extract_all_clauses
from compare_clauses import classify_clause


# --- Configuration ---
BASE_DIR = 'c:\\Users\\91916\\OneDrive\\Desktop\\hilabs\\HiLabsAIQuest_ContractsAI'
CONTRACTS_DIR = os.path.join(BASE_DIR, 'Contracts')
OUTPUT_FILE = 'analysis_results.json'

# The "gold standard" clauses from the Attribute Dictionary
STANDARD_CLAUSES = {
    "Medicaid Timely Filing": "Unless otherwise instructed, or required by Regulatory Requirements, Provider shall submit Claims to using appropriate and current Coded Service Identifier(s), within one hundred twenty (120) days from the date the Health Services are rendered or may refuse payment. If is the secondary payor, the one hundred twenty (120) day period will not begin until Provider receives notification of primary payor's responsibility.",
    "Medicare Timely Filing": "Unless otherwise instructed in the provider manual(s) or Policies applicable to Medicare Advantage Program, or unless required by Regulatory Requirements, Provider shall submit Claims to using appropriate and current Coded Service Identifier(s), within ninety (90) days from the date the Health Services are rendered or will refuse payment. If is the secondary payor, the ninety (90) day period will not begin until Provider receives notification of primary payor's responsibility.",
    "No Steerage/SOC": "Provider shall not steer any Member to any other provider or health care facility. Provider shall not discourage a Member from remaining with Provider or seeking services from another participating Provider. Provider shall not balance bill any Member for any covered services.",
    "Medicaid Fee Schedule": "Provider agrees to accept as payment in full the lesser of (i) the amount billed, or (ii) the fee schedule amount for Covered Services as set forth in the Plan's Medicaid Fee Schedule, which is incorporated by reference herein. Provider agrees that it will not balance bill, charge, or seek to collect from a Member any amounts in excess of the applicable co-payment, coinsurance, and/or deductible for Covered Services.",
    "Medicare Fee Schedule": "Provider agrees to accept as payment in full the lesser of (i) the amount billed, or (ii) the fee schedule amount for Covered Services as set forth in the Plan's Medicare Advantage Fee Schedule, which is incorporated by reference herein. Provider agrees that it will not balance bill, charge, or seek to collect from a Member any amounts in excess of the applicable co-payment, coinsurance, and/or deductible for Covered Services."
}

def run_analysis(debug: bool = False):
    """Run the contract analysis pipeline with optional debug output."""
    all_results = []
    
    # Create debug directory
    if debug:
        Path("debug").mkdir(exist_ok=True)
    
    for state_folder in os.listdir(CONTRACTS_DIR):
        state_path = os.path.join(CONTRACTS_DIR, state_folder)
        if os.path.isdir(state_path):
            print(f"\n==================== Processing {state_folder} Contracts ====================")
            for contract_filename in os.listdir(state_path):
                if contract_filename.endswith('.pdf'):
                    contract_path = os.path.join(state_path, contract_filename)
                    print(f"\n--- Analyzing Contract: {contract_filename} ---")
                    
                    # Extract text with debug info
                    contract_text = extract_text_from_pdf(contract_path, debug=debug)
                    if not contract_text:
                        print(f"Skipping {contract_filename} due to read error.")
                        continue
                    
                    # Extract clauses with new semantic approach
                    extracted_contract_clauses = extract_all_clauses(
                        contract_text, 
                        STANDARD_CLAUSES, 
                        debug=debug
                    )
                    
                    # Compare each attribute against the standard
                    for attribute, standard_clause in STANDARD_CLAUSES.items():
                        clause_data = extracted_contract_clauses.get(attribute, {})
                        extracted_clause = clause_data.get('text', '') if isinstance(clause_data, dict) else clause_data
                        
                        if debug:
                            print(f"\n  === {attribute} ===")
                            if isinstance(clause_data, dict):
                                print(f"  Method: {clause_data.get('method', 'unknown')}")
                                print(f"  Header: {clause_data.get('header', 'none')}")
                                print(f"  Score: {clause_data.get('score', 0.0):.3f}")
                            print(f"  Extracted: {extracted_clause[:200]}...")
                        else:
                            # Simple preview for non-debug mode
                            preview = extracted_clause[:100].strip().replace('\n', ' ') if extracted_clause else "[NO TEXT FOUND]"
                            print(f"  [Extracted Text Preview]: {preview}...")
                        
                        classification = classify_clause(extracted_clause, standard_clause)
                        
                        result = {
                            'state': state_folder,
                            'contract': contract_filename,
                            'attribute': attribute,
                            'classification': classification,
                            'extracted_clause_preview': extracted_clause[:200] + '...' if extracted_clause else '',
                            'standard_clause_preview': standard_clause[:200] + '...',
                            'extraction_score': clause_data.get('score', 0.0) if isinstance(clause_data, dict) else 0.0,
                            'extraction_method': clause_data.get('method', 'legacy') if isinstance(clause_data, dict) else 'legacy'
                        }
                        
                        all_results.append(result)
                        print(f"  - {attribute}: {classification}")
    
    # Generate summary
    total_clauses = len(all_results)
    standard_count = sum(1 for r in all_results if r['classification'] == 'Standard')
    non_standard_count = total_clauses - standard_count
    
    contracts_with_non_standard = set()
    for result in all_results:
        if result['classification'] == 'Non-Standard':
            contracts_with_non_standard.add(result['contract'])
    
    # Calculate average extraction scores
    avg_score = sum(r['extraction_score'] for r in all_results) / len(all_results) if all_results else 0
    
    summary = {
        'total_clauses_analyzed': total_clauses,
        'standard_clauses_count': standard_count,
        'non_standard_clauses_count': non_standard_count,
        'contracts_with_non_standard_count': len(contracts_with_non_standard),
        'list_of_contracts_with_non_standard': list(contracts_with_non_standard),
        'average_extraction_score': round(avg_score, 3)
    }
        
    print("\n\n" + '='*20 + " Analysis Summary " + '='*20)
    for key, value in summary.items():
        print(f"- {key.replace('_', ' ').title()}: {value}")
        
    # Save detailed results to a file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump({'summary': summary, 'details': all_results}, f, indent=4)
    print(f"\nDetailed results saved to {OUTPUT_FILE}")
    
    if debug:
        print(f"\nDebug files saved to: debug/")
        print("- Individual contract text files: debug/[contract_name].txt")
        print("- Attribute headers mapping: debug/attribute_headers.json")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Contract Analysis Pipeline')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode with detailed output and caching')
    args = parser.parse_args()
    
    print("Starting contract analysis pipeline...")
    print("Please ensure you have run 'pip install -r requirements.txt' successfully.")
    print("This may take a few minutes to download the language model on the first run.")
    
    if args.debug:
        print("\n🔍 DEBUG MODE ENABLED")
        print("- Detailed extraction logs will be shown")
        print("- Text files will be cached in debug/ folder")
        print("- Semantic similarity scores will be displayed")
    
    run_analysis(debug=args.debug)
