import React, { useState, useCallback } from 'react';
import { Upload, FileText, CheckCircle, XCircle, AlertCircle, Loader } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import contractDataService from '../services/contractDataService';
import './ContractUpload.css';

const ContractUpload = () => {
  const [templateFile, setTemplateFile] = useState(null);
  const [redactedFile, setRedactedFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  
  const navigate = useNavigate();

  // API base URL
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Poll for job status
  const pollJobStatus = async (jobId) => {
    const maxAttempts = 60; // 5 minutes max
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`${API_URL}/api/contracts/status/${jobId}`);
        const data = await response.json();

        setProgress(data.progress);
        setJobStatus(data.status);

        if (data.status === 'completed') {
          // Fetch results
          const resultsResponse = await fetch(`${API_URL}/api/contracts/results/${jobId}`);
          const resultsData = await resultsResponse.json();
          setResults(resultsData);
          
          // Save results to data service for dashboard integration
          const savedContract = contractDataService.addUploadedContract(resultsData);
          console.log('Contract saved to dashboard:', savedContract);
          
          // Show success message
          setShowSuccessMessage(true);
          
          setProcessing(false);
          return;
        } else if (data.status === 'failed') {
          setError(data.error_message || 'Processing failed');
          setProcessing(false);
          return;
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 5000); // Poll every 5 seconds
        } else {
          setError('Processing timeout');
          setProcessing(false);
        }
      } catch (err) {
        setError('Failed to check job status');
        setProcessing(false);
      }
    };

    poll();
  };

  // Handle file upload and comparison
  const handleCompare = async () => {
    if (!templateFile || !redactedFile) {
      setError('Please upload both files');
      return;
    }

    setProcessing(true);
    setError(null);
    setResults(null);
    setProgress(0);

    const formData = new FormData();
    formData.append('template', templateFile);
    formData.append('redacted', redactedFile);

    try {
      const response = await fetch(`${API_URL}/api/contracts/compare`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      setJobId(data.job_id);
      
      // Start polling for results
      await pollJobStatus(data.job_id);
    } catch (err) {
      setError(err.message);
      setProcessing(false);
    }
  };

  // Export results
  const exportResults = async (format) => {
    if (!jobId || !results) return;

    try {
      const response = await fetch(`${API_URL}/api/contracts/download/${jobId}?format=${format}`);
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `comparison_results_${jobId}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(`Failed to export ${format}`);
    }
  };

  return (
    <div className="contract-upload-container">
      <div className="upload-header">
        <h1>Contract Comparison</h1>
        <p>Upload a standard template and redacted contract to compare attributes</p>
      </div>

      {/* Upload Section */}
      <div className="upload-section">
        <div className="upload-panels">
          <FileUploadPanel
            title="Standard Template"
            subtitle="Upload the standard template contract"
            file={templateFile}
            onFileChange={setTemplateFile}
            disabled={processing}
          />
          <FileUploadPanel
            title="Redacted Contract"
            subtitle="Upload the redacted contract to compare"
            file={redactedFile}
            onFileChange={setRedactedFile}
            disabled={processing}
          />
        </div>

        <div className="action-section">
          <button
            className="compare-button"
            onClick={handleCompare}
            disabled={!templateFile || !redactedFile || processing}
          >
            {processing ? (
              <>
                <Loader className="spinner" />
                Processing... {progress}%
              </>
            ) : (
              <>
                <CheckCircle />
                Extract & Compare
              </>
            )}
          </button>

          {error && (
            <div className="error-message">
              <AlertCircle />
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {processing && (
        <div className="progress-section">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="progress-text">
            {jobStatus === 'processing' ? 'Analyzing contracts...' : 'Initializing...'}
          </p>
        </div>
      )}

      {/* Success Message */}
      {showSuccessMessage && results && (
        <div className="success-section">
          <div className="success-message">
            <CheckCircle className="success-icon" />
            <div className="success-content">
              <h3>Contract Successfully Processed!</h3>
              <p>Your contract has been analyzed and added to the dashboard. You can now view it alongside the existing 10 contracts.</p>
              <button 
                className="view-dashboard-button"
                onClick={() => navigate('/dashboard')}
              >
                <FileText /> View Updated Dashboard
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <ComparisonResults 
          results={results} 
          onExport={exportResults}
          showSuccessMessage={showSuccessMessage}
        />
      )}
    </div>
  );
};

// File Upload Panel Component
const FileUploadPanel = ({ title, subtitle, file, onFileChange, disabled }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileChange(acceptedFiles[0]);
    }
  }, [onFileChange]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    disabled
  });

  const removeFile = () => {
    onFileChange(null);
  };

  return (
    <div className="upload-panel">
      <h3>{title}</h3>
      <p className="upload-subtitle">{subtitle}</p>
      
      {!file ? (
        <div 
          {...getRootProps()} 
          className={`dropzone ${isDragActive ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
        >
          <input {...getInputProps()} />
          <Upload size={48} />
          <p>Drag & drop a PDF file here</p>
          <p className="upload-hint">or click to browse</p>
          <p className="upload-limit">Max size: 50MB</p>
        </div>
      ) : (
        <div className="file-preview">
          <FileText size={48} />
          <p className="file-name">{file.name}</p>
          <p className="file-size">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </p>
          {!disabled && (
            <button 
              className="remove-button"
              onClick={removeFile}
            >
              <XCircle /> Remove
            </button>
          )}
        </div>
      )}
    </div>
  );
};

// Comparison Results Component
const ComparisonResults = ({ results, onExport }) => {
  const getClassificationIcon = (classification) => {
    return classification === 'standard' ? 
      <CheckCircle className="icon-success" /> : 
      <XCircle className="icon-error" />;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'confidence-high';
    if (confidence >= 0.7) return 'confidence-medium';
    return 'confidence-low';
  };

  return (
    <div className="results-section">
      <h2>Classification Results</h2>
      
      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-icon compliance">
            <CheckCircle />
          </div>
          <div className="card-content">
            <h4>Compliance Rate</h4>
            <p className="card-value">{results.compliance_rate.toFixed(1)}%</p>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon standard">
            <FileText />
          </div>
          <div className="card-content">
            <h4>Standard Attributes</h4>
            <p className="card-value">
              {results.standard_count} / {results.total_attributes}
            </p>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon non-standard">
            <AlertCircle />
          </div>
          <div className="card-content">
            <h4>Non-Standard</h4>
            <p className="card-value">{results.non_standard_count}</p>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon confidence">
            <CheckCircle />
          </div>
          <div className="card-content">
            <h4>Avg Confidence</h4>
            <p className="card-value">
              {(results.average_confidence * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      {/* Detailed Table */}
      <div className="results-table-container">
        <table className="results-table">
          <thead>
            <tr>
              <th>Attribute</th>
              <th>Template Value</th>
              <th>Redacted Value</th>
              <th>Classification</th>
              <th>Confidence</th>
              <th>Match Type</th>
            </tr>
          </thead>
          <tbody>
            {results.attributes.map((attr, index) => (
              <tr key={index}>
                <td className="attribute-name">
                  <strong>{attr.name}</strong>
                </td>
                <td className="value-cell">
                  <div className="value-preview">
                    {attr.template_value.substring(0, 100)}
                    {attr.template_value.length > 100 && '...'}
                  </div>
                </td>
                <td className="value-cell">
                  <div className="value-preview">
                    {attr.redacted_value.substring(0, 100)}
                    {attr.redacted_value.length > 100 && '...'}
                  </div>
                </td>
                <td>
                  <div className="classification-badge">
                    {getClassificationIcon(attr.classification)}
                    <span className={`badge ${attr.classification}`}>
                      {attr.classification}
                    </span>
                  </div>
                </td>
                <td>
                  <div className={`confidence-value ${getConfidenceColor(attr.confidence)}`}>
                    {(attr.confidence * 100).toFixed(1)}%
                  </div>
                </td>
                <td>
                  <span className="match-type">
                    {attr.match_type}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Export Options */}
      <div className="export-section">
        <h3>Export Results</h3>
        <div className="export-buttons">
          <button 
            className="export-button"
            onClick={() => onExport('json')}
          >
            <FileText /> Export JSON
          </button>
          <button 
            className="export-button"
            onClick={() => onExport('csv')}
          >
            <FileText /> Export CSV
          </button>
        </div>
      </div>
    </div>
  );
};

export default ContractUpload;
