#!/usr/bin/env python3
"""
Attribute Saving Utility
========================

Saves extracted contract attributes to individual files for detailed review and analysis.
Creates comparison files with similarity scores and classification results.
"""

from focused_extraction import FocusedExtractor
from pathlib import Path

def save_all_attributes(extractor, contract_attributes, template_attributes):
    """Save all extracted attributes to individual files with comparisons."""
    
    # Create output directory
    output_dir = Path("debug/extracted_attributes")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Saving to: {output_dir}")
    
    # Save each attribute to separate files
    for i, attribute in enumerate(extractor.attribute_contexts.keys(), 1):
        safe_name = attribute.replace('/', '_').replace(' ', '_')
        
        contract_attr_text = contract_attributes.get(attribute, "")
        template_attr_text = template_attributes.get(attribute, "")
        
        # Save contract attribute
        contract_file = output_dir / f"{i:02d}_{safe_name}_CONTRACT.txt"
        _save_attribute_file(contract_file, attribute, extractor.contract_path.name, contract_attr_text)
        
        # Save template attribute
        template_file = output_dir / f"{i:02d}_{safe_name}_TEMPLATE.txt"
        _save_attribute_file(template_file, attribute, extractor.template_path.name, template_attr_text)
        
        # Save comparison
        comparison_file = output_dir / f"{i:02d}_{safe_name}_COMPARISON.txt"
        _save_comparison_file(comparison_file, attribute, extractor, contract_attr_text, template_attr_text)
        
        print(f"✅ Saved {attribute}")
    
    # Create summary file
    _save_summary_file(output_dir, extractor, contract_attributes, template_attributes)
    
    print(f"📄 Files created:")
    for file in sorted(output_dir.glob("*.txt")):
        print(f"   - {file.name}")

def _save_attribute_file(file_path, attribute, source_name, content):
    """Save individual attribute content to file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"ATTRIBUTE: {attribute}\n")
        f.write(f"SOURCE: {source_name}\n")
        f.write(f"LENGTH: {len(content)} characters\n")
        f.write("="*80 + "\n\n")
        if content:
            f.write(content)
        else:
            f.write("❌ NO TEXT EXTRACTED")

def _save_comparison_file(file_path, attribute, extractor, contract_text, template_text):
    """Save comparison analysis to file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"ATTRIBUTE: {attribute}\n")
        f.write(f"COMPARISON: {extractor.contract_path.stem} vs {extractor.template_path.stem}\n")
        f.write("="*80 + "\n\n")
        
        if contract_text and template_text:
            is_match, explanation, similarity = extractor.exact_structural_match(
                contract_text, template_text, attribute
            )
            f.write(f"CLASSIFICATION: {'✅ STANDARD' if is_match else '❌ NON-STANDARD'}\n")
            f.write(f"SIMILARITY SCORE: {similarity:.3f}\n")
            f.write(f"EXPLANATION: {explanation}\n\n")
            
            f.write(f"CONTRACT LENGTH: {len(contract_text)} chars\n")
            f.write(f"TEMPLATE LENGTH: {len(template_text)} chars\n\n")
            
            f.write("CONTRACT PREVIEW (first 500 chars):\n")
            f.write("-" * 40 + "\n")
            f.write(contract_text[:500] + ("..." if len(contract_text) > 500 else "") + "\n\n")
            
            f.write("TEMPLATE PREVIEW (first 500 chars):\n")
            f.write("-" * 40 + "\n")
            f.write(template_text[:500] + ("..." if len(template_text) > 500 else "") + "\n")
        else:
            f.write("❌ CANNOT COMPARE - Missing text from one or both sources\n")

def _save_summary_file(output_dir, extractor, contract_attributes, template_attributes):
    """Save summary of all extractions and results."""
    summary_file = output_dir / "00_SUMMARY.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("EXTRACTION SUMMARY\n")
        f.write("="*50 + "\n\n")
        f.write(f"Contract: {extractor.contract_path.name}\n")
        f.write(f"Template: {extractor.template_path.name}\n")
        f.write(f"Total Attributes: {len(extractor.attribute_contexts)}\n\n")
        
        contract_success = sum(1 for attr in contract_attributes.values() if attr)
        template_success = sum(1 for attr in template_attributes.values() if attr)
        
        f.write(f"Contract Extractions: {contract_success}/{len(extractor.attribute_contexts)}\n")
        f.write(f"Template Extractions: {template_success}/{len(extractor.attribute_contexts)}\n\n")
        
        f.write("ATTRIBUTE DETAILS:\n")
        f.write("-" * 30 + "\n")
        
        for i, attribute in enumerate(extractor.attribute_contexts.keys(), 1):
            contract_attr_text = contract_attributes.get(attribute, "")
            template_attr_text = template_attributes.get(attribute, "")
            
            f.write(f"{i}. {attribute}\n")
            f.write(f"   Contract: {len(contract_attr_text)} chars {'✅' if contract_attr_text else '❌'}\n")
            f.write(f"   Template: {len(template_attr_text)} chars {'✅' if template_attr_text else '❌'}\n")
            
            if contract_attr_text and template_attr_text:
                is_match, explanation, similarity = extractor.exact_structural_match(
                    contract_attr_text, template_attr_text, attribute
                )
                f.write(f"   Result: {'✅ STANDARD' if is_match else '❌ NON-STANDARD'} (similarity: {similarity:.3f})\n")
            f.write("\n")
    
    print(f"📋 Summary saved to: {summary_file}")

def main():
    """Standalone execution - extract and save all attributes."""
    extractor = FocusedExtractor()
    
    print("🔍 SAVING ALL EXTRACTED ATTRIBUTES TO FILES")
    print("="*60)
    
    # Extract text from both documents
    print("📄 Extracting text from PDFs...")
    contract_text = extractor.extract_text_from_pdf(extractor.contract_path, debug=False)
    template_text = extractor.extract_text_from_pdf(extractor.template_path, debug=False)
    
    if not contract_text or not template_text:
        print("❌ Failed to extract text from documents")
        return
    
    # Extract attributes
    print("🔍 Extracting attributes...")
    contract_name = extractor.contract_path.stem
    contract_attributes = extractor.extract_all_attributes(contract_text, contract_name, debug=False)
    template_attributes = extractor.extract_all_attributes(template_text, "TN_Standard_Template", debug=False)
    
    # Save all attributes
    save_all_attributes(extractor, contract_attributes, template_attributes)

if __name__ == "__main__":
    main()
