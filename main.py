#!/usr/bin/env python3
"""
HiLabs Contract Analysis System
===============================

A focused extraction system for analyzing healthcare provider contracts
against standard templates using semantic matching and structural analysis.

Usage:
    python main.py --contract TN_Contract1_Redacted.pdf --template TN_Standard_Template_Redacted.pdf
    python main.py --debug  # Enable debug mode with detailed output
    python main.py --help   # Show help message

Features:
- Precise attribute extraction using contextual search patterns
- Semantic similarity matching with SentenceTransformer
- Exact structural match classification
- Support for complex table structures and fee schedules
- Debug mode with detailed extraction logs
"""

import argparse
import sys
from pathlib import Path
from focused_extraction import FocusedExtractor

def main():
    parser = argparse.ArgumentParser(
        description="HiLabs Contract Analysis System - Analyze healthcare contracts against templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --contract TN_Contract1_Redacted.pdf --template TN_Standard_Template_Redacted.pdf
  python main.py --debug
  python main.py --save-files  # Save extracted attributes to files
        """
    )
    
    parser.add_argument(
        '--contract', 
        type=str,
        help='Contract PDF filename (should be in Contracts/TN/ directory)'
    )
    
    parser.add_argument(
        '--template', 
        type=str,
        help='Template PDF filename (should be in Standard Templates/ directory)'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug mode with detailed extraction logs'
    )
    
    parser.add_argument(
        '--save-files', 
        action='store_true',
        help='Save extracted attributes to individual files in debug/extracted_attributes/'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize extractor
        extractor = FocusedExtractor()
        
        # Update paths if provided
        if args.contract:
            contract_path = extractor.base_dir / "Contracts/TN" / args.contract
            if not contract_path.exists():
                print(f"❌ Contract file not found: {contract_path}")
                sys.exit(1)
            extractor.contract_path = contract_path
            
        if args.template:
            template_path = extractor.base_dir / "Standard Templates" / args.template
            if not template_path.exists():
                print(f"❌ Template file not found: {template_path}")
                sys.exit(1)
            extractor.template_path = template_path
        
        print("🔍 HiLabs Contract Analysis System")
        print("=" * 50)
        print(f"📄 Contract: {extractor.contract_path.name}")
        print(f"📋 Template: {extractor.template_path.name}")
        print()
        
        # Extract text from both documents
        print("📄 Extracting text from PDFs...")
        contract_text = extractor.extract_text_from_pdf(extractor.contract_path, debug=args.debug)
        template_text = extractor.extract_text_from_pdf(extractor.template_path, debug=args.debug)
        
        if not contract_text or not template_text:
            print("❌ Failed to extract text from one or both documents")
            sys.exit(1)
        
        # Extract attributes
        print("🔍 Extracting attributes...")
        contract_name = extractor.contract_path.stem
        contract_attributes = extractor.extract_all_attributes(contract_text, contract_name, debug=args.debug)
        template_attributes = extractor.extract_all_attributes(template_text, "TN_Standard_Template", debug=args.debug)
        
        # Analyze results
        print("\n" + "=" * 80)
        print("📊 ANALYSIS RESULTS")
        print("=" * 80)
        
        total_attributes = len(extractor.attribute_contexts)
        contract_success = sum(1 for attr in contract_attributes.values() if attr)
        template_success = sum(1 for attr in template_attributes.values() if attr)
        standard_count = 0
        
        for i, attribute in enumerate(extractor.attribute_contexts.keys(), 1):
            contract_attr_text = contract_attributes.get(attribute, "")
            template_attr_text = template_attributes.get(attribute, "")
            
            print(f"\n{i}. **{attribute}**")
            print(f"   Contract: {len(contract_attr_text)} chars {'✅' if contract_attr_text else '❌'}")
            print(f"   Template: {len(template_attr_text)} chars {'✅' if template_attr_text else '❌'}")
            
            if contract_attr_text and template_attr_text:
                is_match, explanation, similarity = extractor.exact_structural_match(
                    contract_attr_text, template_attr_text, attribute
                )
                status = "✅ STANDARD" if is_match else "❌ NON-STANDARD"
                print(f"   Result: {status} (similarity: {similarity:.3f})")
                print(f"   Explanation: {explanation}")
                
                if is_match:
                    standard_count += 1
            else:
                print("   Result: ❌ EXTRACTION FAILED")
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 SUMMARY")
        print("=" * 80)
        print(f"Contract: {extractor.contract_path.name}")
        print(f"Template: {extractor.template_path.name}")
        print(f"Total Attributes: {total_attributes}")
        print(f"Contract Extractions: {contract_success}/{total_attributes}")
        print(f"Template Extractions: {template_success}/{total_attributes}")
        print(f"Standard Matches: {standard_count}/{total_attributes}")
        print(f"Success Rate: {(standard_count/total_attributes)*100:.1f}%")
        
        # Save files if requested
        if args.save_files:
            print("\n💾 Saving extracted attributes to files...")
            from save_attributes import save_all_attributes
            save_all_attributes(extractor, contract_attributes, template_attributes)
            print("✅ Files saved to debug/extracted_attributes/")
        
        print("\n🎉 Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
