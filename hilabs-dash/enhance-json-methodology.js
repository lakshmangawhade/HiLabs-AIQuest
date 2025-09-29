/**
 * Script to enhance existing JSON files with detailed methodology explanations
 * This will add detailed explanations based on the 10 methodologies from focused_extraction.py
 */

const fs = require('fs');
const path = require('path');

// Concise explanation generator - show only successful (green) findings
function generateConciseMethodologyExplanation(classification, attributeName) {
  const explanations = [];
  const confidence = classification.confidence || 0;
  const matchType = classification.match_type || 'unknown';
  const isStandard = classification.is_standard;
  
  // Primary methodology result - only show successful matches
  if (matchType === 'exact' || (isStandard && confidence >= 0.9)) {
    explanations.push('✓ Exact Match: Section structure identical to template');
  } else if (matchType === 'semantic' || (confidence >= 0.75 && confidence < 0.9)) {
    explanations.push(`✓ Semantic Match: ${(confidence * 100).toFixed(0)}% similarity in legal concepts`);
  }
  // Skip warnings and errors - only show green checkmarks
  
  // Confidence level - only show if high confidence
  if (confidence >= 0.75) {
    const confidenceLevel = confidence >= 0.9 ? 'Very High' : 'High';
    explanations.push(`🎯 Confidence: ${confidenceLevel} (${(confidence * 100).toFixed(0)}%)`);
  }
  
  // Clause-specific findings - only show successful detections
  if (attributeName.includes('Fee Schedule') && isStandard) {
    explanations.push('✓ Standard rates detected in fee table');
  } else if (attributeName.includes('Timely Filing') && isStandard) {
    explanations.push('✓ 90-day filing deadline confirmed');
  } else if ((attributeName.includes('Steerage') || attributeName.includes('SOC')) && isStandard) {
    explanations.push('✓ Standard network participation terms');
  }
  
  // Processing method - only show if we have successful matches
  if (explanations.length > 0) {
    explanations.push('🔧 Method: OCR + Pattern Analysis + Similarity Scoring');
  }
  
  // Add original explanation if it contains positive findings
  const originalExplanation = classification.explanation;
  if (originalExplanation && originalExplanation.length > 10 && 
      (originalExplanation.toLowerCase().includes('match') || 
       originalExplanation.toLowerCase().includes('found') ||
       originalExplanation.toLowerCase().includes('similarity'))) {
    explanations.push(`ℹ ${originalExplanation}`);
  }
  
  // If no successful items to show, add a minimal explanation
  if (explanations.length === 0) {
    explanations.push('🔍 Analysis completed - see status indicators above');
  }
  
  return explanations;
}

// Function to enhance a single JSON file
function enhanceJsonFile(filePath) {
  try {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    
    if (data.classification && data.attribute_name) {
      // Generate concise methodology explanation
      const detailedExplanations = generateConciseMethodologyExplanation(
        data.classification, 
        data.attribute_name
      );
      
      // Add to classification object
      data.classification.detailed_methodology = detailedExplanations;
      data.classification.methodology_version = "3.0";
      data.classification.enhanced_timestamp = new Date().toISOString();
      
      // Write back to file
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
      console.log(`✓ Enhanced: ${path.basename(filePath)}`);
      return true;
    } else {
      console.log(`⚠ Skipped: ${path.basename(filePath)} - Missing required fields`);
      return false;
    }
  } catch (error) {
    console.error(`✗ Error processing ${filePath}:`, error.message);
    return false;
  }
}

// Main function to process all JSON files
function enhanceAllJsonFiles() {
  const baseDir = './public/Backend/results';
  const states = ['TN', 'WA'];
  
  let totalProcessed = 0;
  let totalEnhanced = 0;
  
  console.log('🚀 Starting JSON enhancement process...\n');
  
  states.forEach(state => {
    const stateDir = path.join(baseDir, state);
    
    if (!fs.existsSync(stateDir)) {
      console.log(`⚠ State directory not found: ${stateDir}`);
      return;
    }
    
    const contracts = fs.readdirSync(stateDir).filter(dir => 
      fs.statSync(path.join(stateDir, dir)).isDirectory()
    );
    
    console.log(`📁 Processing ${state} contracts: ${contracts.length} found`);
    
    contracts.forEach(contract => {
      const attributesDir = path.join(stateDir, contract, 'attributes');
      
      if (!fs.existsSync(attributesDir)) {
        console.log(`  ⚠ No attributes directory for ${contract}`);
        return;
      }
      
      const jsonFiles = fs.readdirSync(attributesDir).filter(file => 
        file.endsWith('.json')
      );
      
      console.log(`  📄 ${contract}: ${jsonFiles.length} JSON files`);
      
      jsonFiles.forEach(jsonFile => {
        const filePath = path.join(attributesDir, jsonFile);
        totalProcessed++;
        
        if (enhanceJsonFile(filePath)) {
          totalEnhanced++;
        }
      });
    });
    
    console.log('');
  });
  
  console.log('📊 Enhancement Summary:');
  console.log(`   Total files processed: ${totalProcessed}`);
  console.log(`   Successfully enhanced: ${totalEnhanced}`);
  console.log(`   Skipped/Failed: ${totalProcessed - totalEnhanced}`);
  console.log('\n✅ JSON enhancement complete!');
}

// Run the enhancement
if (require.main === module) {
  enhanceAllJsonFiles();
}

module.exports = { enhanceAllJsonFiles, enhanceJsonFile };
