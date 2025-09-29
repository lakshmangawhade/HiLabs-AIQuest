/**
 * Contract Data Service
 * Manages both existing contracts and newly uploaded contract results
 */

class ContractDataService {
  constructor() {
    this.uploadedContracts = this.loadUploadedContracts();
  }

  // Load uploaded contracts from localStorage
  loadUploadedContracts() {
    const stored = localStorage.getItem('uploadedContracts');
    return stored ? JSON.parse(stored) : [];
  }

  // Save uploaded contracts to localStorage
  saveUploadedContracts(contracts) {
    localStorage.setItem('uploadedContracts', JSON.stringify(contracts));
    this.uploadedContracts = contracts;
  }

  // Add a new uploaded contract result
  addUploadedContract(contractData) {
    const newContract = this.formatUploadedContract(contractData);
    
    // Check if contract already exists (by name)
    const existingIndex = this.uploadedContracts.findIndex(
      contract => contract.name === newContract.name
    );

    if (existingIndex >= 0) {
      // Update existing contract
      this.uploadedContracts[existingIndex] = newContract;
    } else {
      // Add new contract
      this.uploadedContracts.push(newContract);
    }

    this.saveUploadedContracts(this.uploadedContracts);
    return newContract;
  }

  // Format uploaded contract data to match existing contract structure
  formatUploadedContract(apiResults) {
    const { 
      job_id, 
      compliance_rate, 
      total_attributes, 
      standard_count, 
      non_standard_count,
      attributes,
      created_at 
    } = apiResults;

    // Create summary in the same format as existing contracts
    const summary = {
      contract_name: `Uploaded_Contract_${job_id.substring(0, 8)}`,
      template_name: "User_Uploaded_Template",
      compliance_rate: compliance_rate,
      total_attributes: total_attributes,
      standard_count: standard_count,
      non_standard_count: non_standard_count,
      average_confidence: attributes.reduce((sum, attr) => sum + attr.confidence, 0) / attributes.length,
      processing_date: created_at || new Date().toISOString(),
      match_type_distribution: this.calculateMatchTypeDistribution(attributes)
    };

    // Create detailed results in the same format
    const details = {
      contract_info: {
        name: summary.contract_name,
        template: summary.template_name,
        processing_date: summary.processing_date
      },
      classification_results: this.formatClassificationResults(attributes),
      summary: summary
    };

    return {
      name: summary.contract_name,
      state: "UPLOADED", // Special state for uploaded contracts
      summary: summary,
      details: details,
      isUploaded: true // Flag to identify uploaded contracts
    };
  }

  // Calculate match type distribution
  calculateMatchTypeDistribution(attributes) {
    const distribution = {};
    attributes.forEach(attr => {
      const matchType = attr.match_type.toUpperCase();
      distribution[matchType] = (distribution[matchType] || 0) + 1;
    });
    return distribution;
  }

  // Format classification results to match existing structure
  formatClassificationResults(attributes) {
    const results = {};
    
    attributes.forEach(attr => {
      results[attr.name] = {
        is_standard: attr.classification === 'standard',
        confidence: attr.confidence,
        match_type: attr.match_type,
        explanation: attr.explanation,
        template_value: attr.template_value,
        contract_value: attr.redacted_value
      };
    });

    return results;
  }

  // Get all uploaded contracts
  getUploadedContracts() {
    return this.uploadedContracts;
  }

  // Combine existing contracts with uploaded contracts
  combineAllContracts(existingTnData, existingWaData) {
    const allContracts = [];
    
    // Add existing TN contracts
    if (existingTnData) {
      allContracts.push(...existingTnData.map(contract => ({
        ...contract,
        isUploaded: false
      })));
    }

    // Add existing WA contracts
    if (existingWaData) {
      allContracts.push(...existingWaData.map(contract => ({
        ...contract,
        isUploaded: false
      })));
    }

    // Add uploaded contracts
    allContracts.push(...this.uploadedContracts);

    return allContracts;
  }

  // Calculate combined statistics
  calculateCombinedStats(existingTnData, existingWaData) {
    const allContracts = this.combineAllContracts(existingTnData, existingWaData);
    
    if (allContracts.length === 0) {
      return {
        totalContracts: 0,
        averageCompliance: 0,
        totalStandardAttributes: 0,
        totalNonStandardAttributes: 0,
        uploadedContractsCount: 0,
        existingContractsCount: 0
      };
    }

    const totalContracts = allContracts.length;
    const uploadedContractsCount = this.uploadedContracts.length;
    const existingContractsCount = totalContracts - uploadedContractsCount;

    // Calculate overall statistics
    const totalCompliance = allContracts.reduce((sum, contract) => 
      sum + (contract.summary?.compliance_rate || 0), 0
    );
    const averageCompliance = totalCompliance / totalContracts;

    const totalStandardAttributes = allContracts.reduce((sum, contract) => 
      sum + (contract.summary?.standard_count || 0), 0
    );
    const totalNonStandardAttributes = allContracts.reduce((sum, contract) => 
      sum + (contract.summary?.non_standard_count || 0), 0
    );

    // State-wise breakdown
    const tnContracts = allContracts.filter(c => c.state === 'TN');
    const waContracts = allContracts.filter(c => c.state === 'WA');
    const uploadedContracts = allContracts.filter(c => c.state === 'UPLOADED');

    return {
      totalContracts,
      averageCompliance: Math.round(averageCompliance * 10) / 10,
      totalStandardAttributes,
      totalNonStandardAttributes,
      uploadedContractsCount,
      existingContractsCount,
      breakdown: {
        tn: {
          count: tnContracts.length,
          avgCompliance: tnContracts.length > 0 ? 
            Math.round((tnContracts.reduce((sum, c) => sum + (c.summary?.compliance_rate || 0), 0) / tnContracts.length) * 10) / 10 : 0
        },
        wa: {
          count: waContracts.length,
          avgCompliance: waContracts.length > 0 ? 
            Math.round((waContracts.reduce((sum, c) => sum + (c.summary?.compliance_rate || 0), 0) / waContracts.length) * 10) / 10 : 0
        },
        uploaded: {
          count: uploadedContracts.length,
          avgCompliance: uploadedContracts.length > 0 ? 
            Math.round((uploadedContracts.reduce((sum, c) => sum + (c.summary?.compliance_rate || 0), 0) / uploadedContracts.length) * 10) / 10 : 0
        }
      }
    };
  }

  // Remove an uploaded contract
  removeUploadedContract(contractName) {
    this.uploadedContracts = this.uploadedContracts.filter(
      contract => contract.name !== contractName
    );
    this.saveUploadedContracts(this.uploadedContracts);
  }

  // Clear all uploaded contracts
  clearUploadedContracts() {
    this.uploadedContracts = [];
    this.saveUploadedContracts([]);
  }
}

// Create singleton instance
const contractDataService = new ContractDataService();

export default contractDataService;
