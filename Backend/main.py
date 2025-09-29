#!/usr/bin/env python3
"""
HiLabs Contract Analysis System
===============================

A hierarchical contract classification system that compares healthcare provider contracts
against standard templates using multiple matching strategies:
1. Exact Match - Character-by-character comparison
2. Regex Pattern Match - Pattern-based structural matching  
3. Fuzzy Match - Approximate string matching
4. Semantic Match - Fast semantic similarity with lightweight models

Usage:
    python main.py --contract TN_Contract1_Redacted.pdf --template TN_Standard_Template_Redacted.pdf
    python main.py --debug  # Enable debug mode with detailed output
    python main.py --classification-only  # Run only classification without extraction details
    python main.py --help   # Show help message

Features:
- Hierarchical matching strategy for optimal accuracy and speed
- Precise attribute extraction using contextual search patterns
- Multiple similarity algorithms with configurable thresholds
- Support for complex table structures and fee schedules
- Detailed classification reports with match explanations
"""

import argparse
import sys
from pathlib import Path
import json
from datetime import datetime
from focused_extraction import FocusedExtractor
from compare_clauses import ContractClassifier, MatchType
from results_exporter import ResultsExporter

def main():
    parser = argparse.ArgumentParser(
        description="HiLabs Contract Analysis System - Analyze healthcare contracts against templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --contract TN_Contract1_Redacted.pdf --template TN_Standard_Template_Redacted.pdf
  python main.py --batch-all  # Process all TN and WA contracts
  python main.py --batch-tn   # Process only TN contracts
  python main.py --batch-wa   # Process only WA contracts
  python main.py --debug
        """
    )
    
    parser.add_argument(
        '--contract', 
        type=str,
        help='Contract PDF filename (should be in Contracts/TN/ or Contracts/WA/ directory)'
    )
    
    parser.add_argument(
        '--template', 
        type=str,
        help='Template PDF filename (should be in Standard Templates/ directory)'
    )
    
    parser.add_argument(
        '--state',
        type=str,
        choices=['TN', 'WA'],
        help='State for single contract processing (TN or WA)'
    )
    
    parser.add_argument(
        '--batch-all',
        action='store_true',
        help='Process all contracts from both TN and WA states'
    )
    
    parser.add_argument(
        '--batch-tn',
        action='store_true',
        help='Process all TN contracts only'
    )
    
    parser.add_argument(
        '--batch-wa',
        action='store_true',
        help='Process all WA contracts only'
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
    
    parser.add_argument(
        '--classification-only',
        action='store_true',
        help='Run only classification without showing extraction details'
    )
    
    parser.add_argument(
        '--threshold-exact',
        type=float,
        default=1.0,
        help='Threshold for exact matching (default: 1.0)'
    )
    
    parser.add_argument(
        '--threshold-regex',
        type=float,
        default=0.9,
        help='Threshold for regex pattern matching (default: 0.9)'
    )
    
    parser.add_argument(
        '--threshold-fuzzy',
        type=float,
        default=0.8,
        help='Threshold for fuzzy matching (default: 0.8)'
    )
    
    parser.add_argument(
        '--threshold-semantic',
        type=float,
        default=0.7,
        help='Threshold for semantic matching (default: 0.7)'
    )
    
    parser.add_argument(
        '--disable-business-rules',
        action='store_true',
        help='Disable business rule analysis for qualifiers and methodology'
    )
    
    args = parser.parse_args()
    
    try:
        # Determine processing mode
        if args.batch_all:
            process_batch(['TN', 'WA'], args)
        elif args.batch_tn:
            process_batch(['TN'], args)
        elif args.batch_wa:
            process_batch(['WA'], args)
        elif args.contract:
            process_single_contract(args)
        else:
            # Default: process all contracts from both states
            print("🚀 No specific arguments provided. Processing all TN and WA contracts...")
            process_batch(['TN', 'WA'], args)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def process_batch(states, args):
    """Process all contracts from specified states."""
    print("🔍 HiLabs Contract Analysis System - Batch Processing")
    print("=" * 60)
    
    # Initialize components
    extractor = FocusedExtractor()
    exporter = ResultsExporter()
    
    # Initialize classifier with custom thresholds
    classifier = ContractClassifier(
        exact_threshold=args.threshold_exact,
        regex_threshold=args.threshold_regex,
        fuzzy_threshold=args.threshold_fuzzy,
        semantic_threshold=args.threshold_semantic,
        enable_business_rules=not args.disable_business_rules
    )
    
    total_processed = 0
    total_errors = 0
    
    for state in states:
        print(f"\n🏛️ Processing {state} contracts...")
        
        # Set up paths for this state
        contracts_dir = extractor.base_dir / f"Contracts/{state}"
        template_file = f"{state}_Standard_Template_Redacted.pdf" if state == "TN" else f"{state}_Standard_Redacted.pdf"
        template_path = extractor.base_dir / "Standard Templates" / template_file
        
        if not template_path.exists():
            print(f"❌ Template not found: {template_path}")
            continue
        
        # Find all contract files for this state
        if state == "TN":
            contract_files = list(contracts_dir.glob("TN_Contract*_Redacted.pdf"))
        else:  # WA
            contract_files = list(contracts_dir.glob("WA_*_Redacted.pdf"))
        
        print(f"📄 Found {len(contract_files)} {state} contracts")
        
        if not contract_files:
            print(f"⚠️ No contract files found in {contracts_dir}")
            continue
        
        # Extract template text once for this state
        print(f"📋 Loading template: {template_path.name}")
        template_text = extractor.extract_text_from_pdf(template_path, debug=args.debug)
        template_name = f"{state}_Standard_Template"
        template_attributes = extractor.extract_all_attributes(template_text, template_name, debug=False)
        
        # Process each contract
        for i, contract_file in enumerate(contract_files, 1):
            print(f"\n📄 [{i}/{len(contract_files)}] Processing: {contract_file.name}")
            
            try:
                # Extract contract text and attributes
                contract_text = extractor.extract_text_from_pdf(contract_file, debug=args.debug)
                contract_name = contract_file.stem
                contract_attributes = extractor.extract_all_attributes(contract_text, contract_name, debug=False)
                
                # Classify all attributes
                classification_results = classifier.classify_all_attributes(
                    contract_attributes,
                    template_attributes,
                    extractor.attribute_contexts
                )
                
                # Generate summary
                summary = classifier.get_classification_summary(classification_results)
                
                # Export results to state-specific directory
                results_dir = exporter.export_contract_results(
                    contract_name=contract_file.name,
                    template_name=template_path.name,
                    results=classification_results,
                    contract_attributes=contract_attributes,
                    template_attributes=template_attributes,
                    state=state  # Pass state for directory structure
                )
                
                # Show brief summary
                compliance_rate = summary['compliance_rate']
                standard_count = summary['standard_count']
                total_attrs = summary['total_attributes']
                
                print(f"   ✅ {compliance_rate:.1f}% compliance ({standard_count}/{total_attrs})")
                print(f"   📁 Results saved to: results/{state}/{contract_name}/")
                
                total_processed += 1
                
            except Exception as e:
                print(f"   ❌ Error processing {contract_file.name}: {e}")
                if args.debug:
                    import traceback
                    traceback.print_exc()
                total_errors += 1
    
    # Final summary
    print(f"\n🎉 Batch processing complete!")
    print(f"📊 Total processed: {total_processed}")
    print(f"❌ Total errors: {total_errors}")
    print(f"📁 Results saved to: results/TN/ and results/WA/")


def process_single_contract(args):
    """Process a single contract."""
    # Initialize extractor
    extractor = FocusedExtractor()
    
    # Determine state from contract name or use provided state
    state = args.state
    if not state and args.contract:
        if args.contract.startswith('TN_'):
            state = 'TN'
        elif args.contract.startswith('WA_'):
            state = 'WA'
        else:
            print("❌ Cannot determine state from contract name. Please specify --state TN or --state WA")
            sys.exit(1)
    
    if not state:
        state = 'TN'  # Default to TN
    
    # Set up paths
    if args.contract:
        contract_path = extractor.base_dir / f"Contracts/{state}" / args.contract
        if not contract_path.exists():
            print(f"❌ Contract file not found: {contract_path}")
            sys.exit(1)
    else:
        # Use default contract for the state
        contracts_dir = extractor.base_dir / f"Contracts/{state}"
        if state == "TN":
            contract_files = list(contracts_dir.glob("TN_Contract*_Redacted.pdf"))
        else:
            contract_files = list(contracts_dir.glob("WA_*_Redacted.pdf"))
        
        if not contract_files:
            print(f"❌ No contracts found in {contracts_dir}")
            sys.exit(1)
        
        contract_path = contract_files[0]  # Use first available contract
    
    if args.template:
        template_path = extractor.base_dir / "Standard Templates" / args.template
    else:
        # Use state-specific template
        template_file = f"{state}_Standard_Template_Redacted.pdf" if state == "TN" else f"{state}_Standard_Redacted.pdf"
        template_path = extractor.base_dir / "Standard Templates" / template_file
    
    if not template_path.exists():
        print(f"❌ Template file not found: {template_path}")
        sys.exit(1)
    
    print("🔍 HiLabs Contract Analysis System")
    print("=" * 50)
    print(f"🏛️ State: {state}")
    print(f"📄 Contract: {contract_path.name}")
    print(f"📋 Template: {template_path.name}")
    print()
    
    # Extract text from both documents
    print("📄 Extracting text from PDFs...")
    contract_text = extractor.extract_text_from_pdf(contract_path, debug=args.debug)
    template_text = extractor.extract_text_from_pdf(template_path, debug=args.debug)
    
    if not contract_text or not template_text:
        print("❌ Failed to extract text from one or both documents")
        sys.exit(1)
    
    # Extract attributes
    print("🔍 Extracting attributes...")
    contract_name = contract_path.stem
    template_name = f"{state}_Standard_Template"
    contract_attributes = extractor.extract_all_attributes(contract_text, contract_name, debug=args.debug and not args.classification_only)
    template_attributes = extractor.extract_all_attributes(template_text, template_name, debug=args.debug and not args.classification_only)
    
    # Initialize classifier with custom thresholds and business rules
    classifier = ContractClassifier(
        exact_threshold=args.threshold_exact,
        regex_threshold=args.threshold_regex,
        fuzzy_threshold=args.threshold_fuzzy,
        semantic_threshold=args.threshold_semantic,
        enable_business_rules=not args.disable_business_rules
    )
    
    # Classify all attributes
    print("\n🤖 Running hierarchical classification...")
    classification_results = classifier.classify_all_attributes(
        contract_attributes,
        template_attributes,
        extractor.attribute_contexts
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 CLASSIFICATION RESULTS")
    print("=" * 80)
    
    if not args.classification_only:
        # Detailed view
        for i, (attribute, result) in enumerate(classification_results.items(), 1):
            contract_attr_text = contract_attributes.get(attribute, "")
            template_attr_text = template_attributes.get(attribute, "")
            
            print(f"\n{i}. **{attribute}**")
            print(f"   Contract: {len(contract_attr_text)} chars {'✅' if contract_attr_text else '❌'}")
            print(f"   Template: {len(template_attr_text)} chars {'✅' if template_attr_text else '❌'}")
            
            if contract_attr_text and template_attr_text:
                icon = "✅" if result.is_standard else "❌"
                status = "STANDARD" if result.is_standard else "NON-STANDARD"
                match_type_icon = {
                    MatchType.EXACT: "🎯",
                    MatchType.REGEX: "🔍",
                    MatchType.FUZZY: "〰️",
                    MatchType.SEMANTIC: "🧠",
                    MatchType.NO_MATCH: "❓"
                }
                
                print(f"   Result: {icon} {status}")
                print(f"   Match Type: {match_type_icon.get(result.match_type, '')} {result.match_type.value.upper()}")
                print(f"   Confidence: {result.confidence:.3f}")
                print(f"   Explanation: {result.explanation}")
            else:
                print("   Result: ❌ EXTRACTION FAILED")
    else:
        # Summary view only
        for attribute, result in classification_results.items():
            icon = "✅" if result.is_standard else "❌"
            match_type = result.match_type.value.upper()
            print(f"{icon} {attribute}: {match_type} (confidence: {result.confidence:.3f})")
    
    # Summary
    summary = classifier.get_classification_summary(classification_results)
    
    print("\n" + "=" * 80)
    print("🎯 SUMMARY")
    print("=" * 80)
    print(f"State: {state}")
    print(f"Contract: {contract_path.name}")
    print(f"Template: {template_path.name}")
    print(f"Total Attributes: {summary['total_attributes']}")
    print(f"Standard Matches: {summary['standard_count']}/{summary['total_attributes']}")
    print(f"Non-Standard: {summary['non_standard_count']}/{summary['total_attributes']}")
    print(f"Compliance Rate: {summary['compliance_rate']:.1f}%")
    print(f"Average Confidence: {summary['average_confidence']:.3f}")
    
    print("\n📊 Match Type Distribution:")
    for match_type, count in summary['match_type_distribution'].items():
        print(f"   {match_type.upper()}: {count}")
    
    # Export results
    print("\n📤 Exporting results...")
    exporter = ResultsExporter()
    results_dir = exporter.export_contract_results(
        contract_name=contract_path.name,
        template_name=template_path.name,
        results=classification_results,
        contract_attributes=contract_attributes,
        template_attributes=template_attributes,
        state=state
    )
    print(f"✅ Results exported to: {results_dir}")
    print(f"🌐 Open preview: {results_dir}/preview.html")
    
    print("\n🎉 Analysis complete!")

if __name__ == "__main__":
    main()
