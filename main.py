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
    
    parser.add_argument(
        '--export-results',
        action='store_true',
        help='Export results in frontend-friendly format to results/TN/ directory'
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
        contract_attributes = extractor.extract_all_attributes(contract_text, contract_name, debug=args.debug and not args.classification_only)
        template_attributes = extractor.extract_all_attributes(template_text, "TN_Standard_Template", debug=args.debug and not args.classification_only)
        
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
        
        # Analyze results
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
        print(f"Contract: {extractor.contract_path.name}")
        print(f"Template: {extractor.template_path.name}")
        print(f"Total Attributes: {summary['total_attributes']}")
        print(f"Standard Matches: {summary['standard_count']}/{summary['total_attributes']}")
        print(f"Non-Standard: {summary['non_standard_count']}/{summary['total_attributes']}")
        print(f"Compliance Rate: {summary['compliance_rate']:.1f}%")
        print(f"Average Confidence: {summary['average_confidence']:.3f}")
        
        print("\n📊 Match Type Distribution:")
        for match_type, count in summary['match_type_distribution'].items():
            print(f"   {match_type.upper()}: {count}")
        
        # Save detailed classification report
        if args.save_files:
            report_dir = Path("debug/classification_reports")
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "contract": str(extractor.contract_path),
                "template": str(extractor.template_path),
                "summary": summary,
                "detailed_results": {
                    attr: {
                        "is_standard": result.is_standard,
                        "match_type": result.match_type.value,
                        "confidence": result.confidence,
                        "explanation": result.explanation
                    }
                    for attr, result in classification_results.items()
                },
                "thresholds": {
                    "exact": args.threshold_exact,
                    "regex": args.threshold_regex,
                    "fuzzy": args.threshold_fuzzy,
                    "semantic": args.threshold_semantic
                }
            }
            
            report_file = report_dir / f"classification_{contract_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n📄 Classification report saved to: {report_file}")
        
        # Save files if requested
        if args.save_files:
            print("\n💾 Saving extracted attributes to files...")
            from save_attributes import save_all_attributes
            save_all_attributes(extractor, contract_attributes, template_attributes)
            print("✅ Files saved to debug/extracted_attributes/")
        
        # Export results for frontend if requested
        if args.export_results:
            print("\n📤 Exporting results for frontend display...")
            exporter = ResultsExporter()
            results_dir = exporter.export_contract_results(
                contract_name=extractor.contract_path.name,
                template_name=extractor.template_path.name,
                results=classification_results,
                contract_attributes=contract_attributes,
                template_attributes=template_attributes,
                contexts=None  # Contexts not available in current implementation
            )
            print(f"✅ Frontend-ready results exported to: {results_dir}")
            print(f"🌐 Open preview: {results_dir}/preview.html")
        
        print("\n🎉 Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
