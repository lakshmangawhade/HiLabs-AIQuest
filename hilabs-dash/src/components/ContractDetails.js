import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PieChart, Pie, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { ArrowLeft, FileText, CheckCircle, XCircle, AlertCircle, Info, TrendingUp, Shield, Clock } from 'lucide-react';
import './ContractDetails.css';

const COLORS = {
  success: '#48bb78',
  warning: '#f6ad55',
  danger: '#fc8181',
  info: '#63b3ed',
  primary: '#667eea',
  secondary: '#764ba2'
};

function ContractDetails({ tnData, waData }) {
  const { state, name } = useParams();
  const navigate = useNavigate();
  const [contract, setContract] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const allContracts = [...(tnData || []), ...(waData || [])];
    const foundContract = allContracts.find(c => 
      c.state === state.toUpperCase() && 
      c.name.replace(' ', '_') === name
    );
    setContract(foundContract);
  }, [state, name, tnData, waData]);

  if (!contract) {
    return (
      <div className="contract-details">
        <div className="container">
          <div className="not-found">
            <h2>Contract Not Found</h2>
            <p>The requested contract could not be found.</p>
            <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { summary, details } = contract;

  // Prepare pie chart data for compliance
  const complianceData = [
    { name: 'Standard', value: summary.overview.standard_count, color: COLORS.success },
    { name: 'Non-Standard', value: summary.overview.non_standard_count, color: COLORS.danger }
  ];

  // Prepare match type data
  const matchTypeData = Object.entries(summary.match_type_distribution || {}).map(([type, count]) => ({
    name: type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' '),
    count: count,
    color: {
      exact: COLORS.success,
      regex: COLORS.info,
      fuzzy: COLORS.warning,
      semantic: COLORS.secondary,
      no_match: COLORS.danger
    }[type] || COLORS.primary
  }));

  // Get detailed results for each attribute
  const attributeDetails = Object.entries(details.results || {}).map(([attr, result]) => ({
    name: attr,
    isStandard: result.is_standard,
    matchType: result.match_type,
    confidence: result.confidence,
    explanation: result.explanation
  }));

  const getStatusIcon = (isStandard) => {
    if (isStandard) return <CheckCircle size={18} className="icon-success" />;
    return <XCircle size={18} className="icon-danger" />;
  };

  const getMatchTypeBadge = (type) => {
    const colors = {
      exact: 'success',
      regex: 'info',
      fuzzy: 'warning',
      semantic: 'secondary',
      no_match: 'danger'
    };
    return <span className={`badge badge-${colors[type] || 'primary'}`}>{type.toUpperCase()}</span>;
  };

  return (
    <div className="contract-details">
      <div className="container">
        {/* Header */}
        <div className="details-header">
          <button className="back-button" onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
          <div className="header-info">
            <h1>{contract.name.replace('_Redacted', '').replace('_', ' ')}</h1>
            <div className="header-badges">
              <span className={`state-badge ${contract.state.toLowerCase()}`}>
                {contract.state}
              </span>
              <span className={`compliance-badge ${summary.overview.compliance_rate >= 80 ? 'success' : summary.overview.compliance_rate >= 50 ? 'warning' : 'danger'}`}>
                {summary.overview.compliance_rate.toFixed(1)}% Compliant
              </span>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="metrics-row">
          <div className="metric-card">
            <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)' }}>
              <FileText size={20} />
            </div>
            <div className="metric-content">
              <p className="metric-label">Total Attributes</p>
              <h3 className="metric-value">{summary.overview.total_attributes}</h3>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #48bb78, #38a169)' }}>
              <CheckCircle size={20} />
            </div>
            <div className="metric-content">
              <p className="metric-label">Standard Clauses</p>
              <h3 className="metric-value">{summary.overview.standard_count}</h3>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #fc8181, #f56565)' }}>
              <AlertCircle size={20} />
            </div>
            <div className="metric-content">
              <p className="metric-label">Non-Standard</p>
              <h3 className="metric-value">{summary.overview.non_standard_count}</h3>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #63b3ed, #4299e1)' }}>
              <TrendingUp size={20} />
            </div>
            <div className="metric-content">
              <p className="metric-label">Avg Confidence</p>
              <h3 className="metric-value">{(summary.confidence_stats.average * 100).toFixed(1)}%</h3>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab ${activeTab === 'details' ? 'active' : ''}`}
            onClick={() => setActiveTab('details')}
          >
            Attribute Details
          </button>
          <button 
            className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
            onClick={() => setActiveTab('analysis')}
          >
            Analysis
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="tab-content">
            <div className="charts-grid">
              <div className="chart-card">
                <h3>Compliance Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={complianceData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {complianceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-card">
                <h3>Match Type Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={matchTypeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                      {matchTypeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="summary-cards">
              <div className="summary-card">
                <h4>Standard Attributes</h4>
                <div className="attribute-list">
                  {summary.attribute_lists.standard.map((attr, index) => (
                    <div key={index} className="attribute-item success">
                      <CheckCircle size={16} />
                      <span>{attr}</span>
                    </div>
                  ))}
                  {summary.attribute_lists.standard.length === 0 && (
                    <p className="no-data">No standard attributes found</p>
                  )}
                </div>
              </div>

              <div className="summary-card">
                <h4>Non-Standard Attributes</h4>
                <div className="attribute-list">
                  {summary.attribute_lists.non_standard.map((attr, index) => (
                    <div key={index} className="attribute-item danger">
                      <XCircle size={16} />
                      <span>{attr}</span>
                    </div>
                  ))}
                  {summary.attribute_lists.non_standard.length === 0 && (
                    <p className="no-data">No non-standard attributes found</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'details' && (
          <div className="tab-content">
            <div className="details-table">
              <table>
                <thead>
                  <tr>
                    <th>Attribute</th>
                    <th>Status</th>
                    <th>Match Type</th>
                    <th>Confidence</th>
                    <th>Explanation</th>
                  </tr>
                </thead>
                <tbody>
                  {attributeDetails.map((attr, index) => (
                    <tr key={index}>
                      <td className="attribute-name">{attr.name}</td>
                      <td>{getStatusIcon(attr.isStandard)}</td>
                      <td>{getMatchTypeBadge(attr.matchType)}</td>
                      <td>
                        <div className="confidence-cell">
                          <div className="confidence-bar">
                            <div 
                              className="confidence-fill"
                              style={{ 
                                width: `${attr.confidence * 100}%`,
                                background: attr.confidence >= 0.8 ? COLORS.success : 
                                           attr.confidence >= 0.5 ? COLORS.warning : COLORS.danger
                              }}
                            />
                          </div>
                          <span className="confidence-text">{(attr.confidence * 100).toFixed(1)}%</span>
                        </div>
                      </td>
                      <td className="explanation">{attr.explanation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="tab-content">
            <div className="analysis-grid">
              <div className="analysis-card">
                <div className="analysis-header">
                  <Shield size={24} className="analysis-icon" />
                  <h3>Compliance Analysis</h3>
                </div>
                <div className="analysis-content">
                  <p>This contract shows a compliance rate of <strong>{summary.overview.compliance_rate.toFixed(1)}%</strong> with the standard template.</p>
                  <ul>
                    <li>{summary.overview.standard_count} attributes match the standard template</li>
                    <li>{summary.overview.non_standard_count} attributes deviate from the standard</li>
                    <li>Average confidence score: {(summary.confidence_stats.average * 100).toFixed(1)}%</li>
                  </ul>
                </div>
              </div>

              <div className="analysis-card">
                <div className="analysis-header">
                  <Info size={24} className="analysis-icon" />
                  <h3>Match Type Breakdown</h3>
                </div>
                <div className="analysis-content">
                  <p>The matching algorithms used for this contract analysis:</p>
                  <ul>
                    {Object.entries(summary.match_type_distribution || {}).map(([type, count]) => (
                      <li key={type}>
                        <strong>{type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')}:</strong> {count} attributes
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="analysis-card">
                <div className="analysis-header">
                  <Clock size={24} className="analysis-icon" />
                  <h3>Recommendations</h3>
                </div>
                <div className="analysis-content">
                  {summary.overview.compliance_rate === 100 ? (
                    <p className="recommendation success">
                      ✅ This contract is fully compliant with the standard template. No action required.
                    </p>
                  ) : summary.overview.compliance_rate >= 80 ? (
                    <p className="recommendation warning">
                      ⚠️ This contract has minor deviations. Review the {summary.overview.non_standard_count} non-standard attribute(s) for potential updates.
                    </p>
                  ) : (
                    <p className="recommendation danger">
                      ❌ This contract has significant deviations from the standard. Immediate review and revision recommended for {summary.overview.non_standard_count} non-standard attributes.
                    </p>
                  )}
                </div>
              </div>

              <div className="analysis-card">
                <div className="analysis-header">
                  <TrendingUp size={24} className="analysis-icon" />
                  <h3>Confidence Statistics</h3>
                </div>
                <div className="analysis-content">
                  <div className="stats-grid">
                    <div className="stat">
                      <span className="stat-label">Average</span>
                      <span className="stat-value">{(summary.confidence_stats.average * 100).toFixed(1)}%</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Minimum</span>
                      <span className="stat-value">{(summary.confidence_stats.minimum * 100).toFixed(1)}%</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Maximum</span>
                      <span className="stat-value">{(summary.confidence_stats.maximum * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ContractDetails;
