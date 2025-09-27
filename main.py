import os
import json
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
    "No Steerage/SOC": "Provider shall be eligible to participate only in those Networks designated on the Provider Networks Attachment of this Agreement. Provider shall not be recognized as a Participating Provider in such Networks until the later of: 1) the Effective Date of this Agreement or; 2) as determined by in its sole discretion, the date Provider has met applicable credentialing requirements and accreditation requirements. Provider acknowledges that may develop, discontinue, or modify new or existing Networks, products and/or programs. In addition to those Networks designated on the Provider Networks Attachment, may also identify Provider as a Participating Provider in additional Networks, products and/or programs designated in writing from time to time by The terms and conditions of Provider's participation as a Participating Provider in such additional Networks, products and/or programs shall be on the terms and conditions as set forth in this Agreement unless otherwise agreed to in writing by Provider and",
    "Medicaid Fee Schedule": "For purposes of determining the █████ Rate, the total reimbursement amount that Provider and █████ have agreed upon for the applicable provider type(s) for Covered Services provided under this Agreement shall be one hundred percent (100%) of the █████ Professional Provider Market Master Fee Schedule A in effect on the date of service.",
    "Medicare Fee Schedule": "For Covered Services furnished by or on behalf of Provider for a Member enrolled in a Medicare Advantage Network, Provider agrees to accept an amount that is the lesser of Eligible Charges or the Medicare Advantage Rate, minus applicable Cost Shares, and modified before payment as described below. Provider agrees that this amount, plus applicable Cost Shares, is full compensation for Covered Services."
}

def run_analysis():
    """Main function to run the contract analysis pipeline."""
    all_results = []
    
    # Process contracts from both TN and WA directories
    for state in ['TN', 'WA']:
        state_dir = os.path.join(CONTRACTS_DIR, state)
        if not os.path.isdir(state_dir):
            continue

        print(f"\n{'='*20} Processing {state} Contracts {'='*20}")
        
        for contract_filename in os.listdir(state_dir):
            contract_path = os.path.join(state_dir, contract_filename)
            print(f"\n--- Analyzing Contract: {contract_filename} ---")
            
            contract_text = extract_text_from_pdf(contract_path)
            if not contract_text:
                print(f"Skipping {contract_filename} due to read error.")
                continue
                
            extracted_contract_clauses = extract_all_clauses(contract_text)
            
            # Compare each attribute against the standard
            for attribute, standard_clause in STANDARD_CLAUSES.items():
                extracted_clause = extracted_contract_clauses.get(attribute, "")
                
                # Print a preview of the extracted text for debugging
                print(f"  [Extracted Text Preview]: {extracted_clause[:100].strip().replace('\n', ' ')}...")
                
                classification = classify_clause(extracted_clause, standard_clause)
                
                result = {
                    'state': state,
                    'contract': contract_filename,
                    'attribute': attribute,
                    'classification': classification,
                    'extracted_clause_preview': extracted_clause[:200] + '...',
                    'standard_clause_preview': standard_clause[:200] + '...'
                }
                all_results.append(result)
                print(f"  - {attribute}: {classification}")

    # --- Generate Summary Metrics ---
    if all_results:
        total_clauses = len(all_results)
        non_standard_clauses = [r for r in all_results if r['classification'] == 'Non-Standard']
        
        contracts_with_non_standard = set(r['contract'] for r in non_standard_clauses)
        
        summary = {
            'total_clauses_analyzed': total_clauses,
            'standard_clauses_count': total_clauses - len(non_standard_clauses),
            'non_standard_clauses_count': len(non_standard_clauses),
            'contracts_with_non_standard_count': len(contracts_with_non_standard),
            'list_of_contracts_with_non_standard': list(contracts_with_non_standard)
        }
        
        print("\n\n" + '='*20 + " Analysis Summary " + '='*20)
        for key, value in summary.items():
            print(f"- {key.replace('_', ' ').title()}: {value}")
            
        # Save detailed results to a file
        with open(OUTPUT_FILE, 'w') as f:
            json.dump({'summary': summary, 'details': all_results}, f, indent=4)
        print(f"\nDetailed results saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    print("Starting contract analysis pipeline...")
    print("Please ensure you have run 'pip install -r requirements.txt' successfully.")
    print("This may take a few minutes to download the language model on the first run.")
    run_analysis()
