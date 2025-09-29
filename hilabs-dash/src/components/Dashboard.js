import React, { useState, useMemo, useEffect } from 'react';
import { PieChart, Pie, BarChart, Bar, LineChart, Line, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { FileText, TrendingUp, TrendingDown, Award, AlertCircle, CheckCircle, XCircle, Filter, Upload } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import contractDataService from '../services/contractDataService';
import './Dashboard.css';

const COLORS = {
  primary: '#667eea',
  secondary: '#764ba2',
  success: '#48bb78',
  warning: '#f6ad55',
  danger: '#fc8181',
  info: '#63b3ed',
  purple: '#9f7aea',
  pink: '#ed64a6',
  // Bright colors for dark theme
  primaryBright: '#818cf8',
  secondaryBright: '#a78bfa',
  successBright: '#6ee7b7',
  warningBright: '#fbbf24',
  dangerBright: '#f87171',
  infoBright: '#93c5fd',
  purpleBright: '#c084fc'
};

function Dashboard({ tnData, waData }) {
  const navigate = useNavigate();
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [selectedState, setSelectedState] = useState('all');
  const [selectedMetric, setSelectedMetric] = useState('compliance');
  const [uploadedContracts, setUploadedContracts] = useState([]);
  const [combinedStats, setCombinedStats] = useState(null);

  // Load uploaded contracts on component mount and when data changes
  useEffect(() => {
    const uploaded = contractDataService.getUploadedContracts();
    setUploadedContracts(uploaded);
    
    const stats = contractDataService.calculateCombinedStats(tnData, waData);
    setCombinedStats(stats);
  }, [tnData, waData]);

  // Calculate overall statistics including uploaded contracts
  const stats = useMemo(() => {
    const allContracts = contractDataService.combineAllContracts(tnData, waData);
    
    if (allContracts.length === 0) {
      return {
        totalContracts: 0,
        avgCompliance: 0,
        fullyCompliant: 0,
        partiallyCompliant: 0,
        nonCompliant: 0,
        withNonStandard: 0,
        tnAvgCompliance: 0,
        waAvgCompliance: 0,
        uploadedAvgCompliance: 0
      };
    }
    
    const totalContracts = allContracts.length;
    const avgCompliance = allContracts.reduce((sum, c) => {
      const compliance = c.summary?.overview?.compliance_rate || c.summary?.compliance_rate || 0;
      return sum + compliance;
    }, 0) / totalContracts;
    
    const fullyCompliant = allContracts.filter(c => {
      const compliance = c.summary?.overview?.compliance_rate || c.summary?.compliance_rate || 0;
      return compliance === 100;
    }).length;
    
    const partiallyCompliant = allContracts.filter(c => {
      const compliance = c.summary?.overview?.compliance_rate || c.summary?.compliance_rate || 0;
      return compliance > 0 && compliance < 100;
    }).length;
    
    const nonCompliant = allContracts.filter(c => {
      const compliance = c.summary?.overview?.compliance_rate || c.summary?.compliance_rate || 0;
      return compliance === 0;
    }).length;
    
    const withNonStandard = allContracts.filter(c => {
      const nonStandardCount = c.summary?.overview?.non_standard_count || c.summary?.non_standard_count || 0;
      return nonStandardCount > 0;
    }).length;

    // State-specific stats
    const tnContracts = allContracts.filter(c => c.state === 'TN');
    const waContracts = allContracts.filter(c => c.state === 'WA');
    const uploadedContracts = allContracts.filter(c => c.state === 'UPLOADED');
    
    const tnAvgCompliance = tnContracts.length > 0 ? 
      tnContracts.reduce((sum, c) => sum + (c.summary?.overview?.compliance_rate || c.summary?.compliance_rate || 0), 0) / tnContracts.length : 0;
    const waAvgCompliance = waContracts.length > 0 ? 
      waContracts.reduce((sum, c) => sum + (c.summary?.overview?.compliance_rate || c.summary?.compliance_rate || 0), 0) / waContracts.length : 0;
    const uploadedAvgCompliance = uploadedContracts.length > 0 ? 
      uploadedContracts.reduce((sum, c) => sum + (c.summary?.compliance_rate || 0), 0) / uploadedContracts.length : 0;

    return {
      totalContracts,
      avgCompliance,
      fullyCompliant,
      partiallyCompliant,
      nonCompliant,
      withNonStandard,
      tnAvgCompliance,
      waAvgCompliance,
      uploadedAvgCompliance,
      tnCount: tnContracts.length,
      waCount: waContracts.length,
      uploadedCount: uploadedContracts.length
    };
  }, [tnData, waData]);

  // Prepare data for pie chart - based on clauses (including uploaded contracts)
  const complianceDistribution = useMemo(() => {
    const allContracts = contractDataService.combineAllContracts(tnData, waData);
    let totalStandardClauses = 0;
    let totalNonStandardClauses = 0;
    
    allContracts.forEach(contract => {
      const standardCount = contract.summary?.overview?.standard_count || contract.summary?.standard_count || 0;
      const nonStandardCount = contract.summary?.overview?.non_standard_count || contract.summary?.non_standard_count || 0;
      totalStandardClauses += standardCount;
      totalNonStandardClauses += nonStandardCount;
    });
    
    return [
      { name: `Compliant (${totalStandardClauses})`, value: totalStandardClauses, color: isDark ? COLORS.successBright : COLORS.success },
      { name: `Non-Compliant (${totalNonStandardClauses})`, value: totalNonStandardClauses, color: isDark ? COLORS.dangerBright : COLORS.danger }
    ];
  }, [tnData, waData, isDark]);

  // Prepare data for state comparison (including uploaded contracts)
  const stateComparison = useMemo(() => {
    const allContracts = contractDataService.combineAllContracts(tnData, waData);
    
    const tnContracts = allContracts.filter(c => c.state === 'TN');
    const waContracts = allContracts.filter(c => c.state === 'WA');
    const uploadedContracts = allContracts.filter(c => c.state === 'UPLOADED');
    
    const tnClauses = tnContracts.reduce((sum, c) => sum + (c.summary?.overview?.total_attributes || c.summary?.total_attributes || 0), 0);
    const waClauses = waContracts.reduce((sum, c) => sum + (c.summary?.overview?.total_attributes || c.summary?.total_attributes || 0), 0);
    const uploadedClauses = uploadedContracts.reduce((sum, c) => sum + (c.summary?.total_attributes || 0), 0);
    
    const data = [
      { state: 'Tennessee', compliance: stats.tnAvgCompliance, contracts: stats.tnCount, clauses: tnClauses },
      { state: 'Washington', compliance: stats.waAvgCompliance, contracts: stats.waCount, clauses: waClauses }
    ];

    // Add uploaded contracts if any exist
    if (stats.uploadedCount > 0) {
      data.push({ 
        state: 'Uploaded', 
        compliance: stats.uploadedAvgCompliance, 
        contracts: stats.uploadedCount, 
        clauses: uploadedClauses 
      });
    }

    return data;
  }, [tnData, waData, stats]);

  // Get filtered contracts based on selected state (including uploaded contracts)
  const getFilteredContracts = () => {
    const allContracts = contractDataService.combineAllContracts(tnData, waData);
    
    if (selectedState === 'TN') return allContracts.filter(c => c.state === 'TN');
    if (selectedState === 'WA') return allContracts.filter(c => c.state === 'WA');
    if (selectedState === 'uploaded') return allContracts.filter(c => c.state === 'UPLOADED');
    return allContracts;
  };

  // Prepare contract performance data (including uploaded contracts)
  const contractPerformance = useMemo(() => getFilteredContracts().map((contract, index) => {
    let statePrefix, contractNumber, displayName;
    
    if (contract.state === 'UPLOADED') {
      statePrefix = 'UP';
      contractNumber = contract.name.substring(contract.name.length - 8); // Last 8 chars of job ID
      displayName = `UP_${contractNumber}`;
    } else {
      statePrefix = contract.state === 'TN' ? 'TN' : 'WA';
      contractNumber = contract.name.match(/\d+/)?.[0] || (index + 1);
      displayName = `${statePrefix}${contractNumber}`;
    }
    
    const compliance = contract.summary?.overview?.compliance_rate || contract.summary?.compliance_rate || 0;
    const standardCount = contract.summary?.overview?.standard_count || contract.summary?.standard_count || 0;
    const nonStandardCount = contract.summary?.overview?.non_standard_count || contract.summary?.non_standard_count || 0;
    
    return {
      originalName: contract.name,
      name: displayName,
      compliance: compliance,
      state: contract.state,
      standardCount: standardCount,
      nonStandardCount: nonStandardCount,
      isUploaded: contract.isUploaded || false
    };
  }).sort((a, b) => {
    if (selectedMetric === 'compliance') {
      return b.compliance - a.compliance;
    }
    return a.name.localeCompare(b.name);
  }), [selectedState, tnData, waData, selectedMetric]);

  // Calculate match type distribution
  const matchTypeData = useMemo(() => {
    const contracts = getFilteredContracts();
    const matchTypes = {};
    
    contracts.forEach(contract => {
      Object.entries(contract.summary.match_type_distribution || {}).forEach(([type, count]) => {
        matchTypes[type] = (matchTypes[type] || 0) + count;
      });
    });

    return Object.entries(matchTypes).map(([type, count]) => ({
      name: type.charAt(0).toUpperCase() + type.slice(1),
      value: count,
      color: {
        exact: isDark ? COLORS.successBright : COLORS.success,
        regex: isDark ? COLORS.infoBright : COLORS.info,
        fuzzy: isDark ? COLORS.warningBright : COLORS.warning,
        semantic: isDark ? COLORS.purpleBright : COLORS.purple,
        no_match: isDark ? COLORS.dangerBright : COLORS.danger
      }[type] || (isDark ? COLORS.primaryBright : COLORS.primary)
    }));
  }, [selectedState, tnData, waData, isDark]);

  // Prepare radar chart data for attribute analysis
  const attributeAnalysis = useMemo(() => {
    const contracts = getFilteredContracts();
    const attributes = ['Medicare Fee Schedule', 'Medicaid Fee Schedule', 'Medicare Timely Filing', 'Medicaid Timely Filing', 'No Steerage/SOC'];
    return attributes.map(attr => {
      const compliantCount = contracts.filter(c => 
        c.summary.attribute_lists?.standard?.includes(attr)
      ).length;
      
      const compliancePercent = contracts.length > 0 ? (compliantCount / contracts.length) * 100 : 0;
      
      return {
        attribute: attr.replace(' Schedule', '').replace('Timely Filing', 'Filing'),
        compliance: compliancePercent,
        label: `${attr.replace(' Schedule', '').replace('Timely Filing', 'Filing')} (${compliantCount}/${contracts.length})`
      };
    });
  }, [selectedState, tnData, waData]);

  return (
    <div className="dashboard">
      <div className="container">
        {/* Header */}
        <div className="dashboard-header">
          <div>
            <h1>Contract Analysis Dashboard</h1>
            <p className="subtitle">Comprehensive overview of healthcare contract compliance</p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)' }}>
              <FileText size={24} />
            </div>
            <div className="metric-content">
              <p className="metric-label">Total Contracts</p>
              <h3 className="metric-value">{stats.totalContracts}</h3>
              <p className="metric-detail">
                {stats.tnCount} TN | {stats.waCount} WA 
                {stats.uploadedCount > 0 && ` | ${stats.uploadedCount} Uploaded`}
              </p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #48bb78, #38a169)' }}>
              <TrendingUp size={24} />
            </div>
            <div className="metric-content">
              <p className="metric-label">Average Compliance</p>
              <h3 className="metric-value">{stats.avgCompliance.toFixed(1)}%</h3>
              <p className="metric-detail">Across all contracts</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #f6ad55, #ed8936)' }}>
              <Award size={24} />
            </div>
            <div className="metric-content">
              <p className="metric-label">Fully Compliant</p>
              <h3 className="metric-value">{stats.fullyCompliant}</h3>
              <p className="metric-detail">{((stats.fullyCompliant / stats.totalContracts) * 100).toFixed(0)}% of total</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #9f7aea, #805ad5)' }}>
              <AlertCircle size={24} />
            </div>
            <div className="metric-content">
              <p className="metric-label">Need Review</p>
              <h3 className="metric-value">{stats.withNonStandard}</h3>
              <p className="metric-detail">At least 1 clause needs review</p>
            </div>
          </div>

        </div>

        {/* Charts Row 1 */}
        <div className="charts-row">
          <div className="chart-card">
            <h3>Compliance Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={complianceDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {complianceDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>State Comparison</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stateComparison}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="state" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="compliance" fill={isDark ? COLORS.primaryBright : COLORS.primary} name="Avg Compliance %" radius={[8, 8, 0, 0]} />
                <Bar dataKey="contracts" fill={isDark ? COLORS.secondaryBright : COLORS.secondary} name="Contract Count" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="charts-row">
          <div className="chart-card">
            <h3>Match Type Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={matchTypeData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  fill="#8884d8"
                  paddingAngle={2}
                  dataKey="value"
                >
                  {matchTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Clause Compliance Rate</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={attributeAnalysis}>
                <PolarGrid stroke={isDark ? '#444' : '#ccc'} />
                <PolarAngleAxis dataKey="attribute" tick={{ fill: isDark ? '#d0d0d0' : '#666' }} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: isDark ? '#d0d0d0' : '#666' }} />
                <Radar name="Compliance %" dataKey="compliance" stroke={isDark ? COLORS.primaryBright : COLORS.primary} fill={isDark ? COLORS.primaryBright : COLORS.primary} fillOpacity={0.6} />
                <Tooltip contentStyle={{ backgroundColor: isDark ? '#16213e' : '#fff', border: isDark ? '1px solid #2d3561' : '1px solid #e0e0e0' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Contract Performance Table */}
        <div className="card">
          <div className="table-header">
            <h3>Contract Performance Details</h3>
            <div className="table-filters">
              <select 
                className="filter-select"
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
              >
                <option value="all">All Contracts</option>
                <option value="TN">Tennessee</option>
                <option value="WA">Washington</option>
                {stats.uploadedCount > 0 && (
                  <option value="uploaded">Uploaded Contracts</option>
                )}
              </select>
              <button 
                className={`filter-btn ${selectedMetric === 'compliance' ? 'active' : ''}`}
                onClick={() => setSelectedMetric('compliance')}
              >
                Sort by Compliance
              </button>
              <button 
                className={`filter-btn ${selectedMetric === 'name' ? 'active' : ''}`}
                onClick={() => setSelectedMetric('name')}
              >
                Sort by Name
              </button>
            </div>
          </div>
          
          <div className="performance-table">
            <table>
              <thead>
                <tr>
                  <th>Contract</th>
                  <th>State</th>
                  <th>Compliance</th>
                  <th>Standard Clauses</th>
                  <th>Non-Standard Clauses</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {contractPerformance
                  .sort((a, b) => {
                    if (selectedMetric === 'compliance') return b.compliance - a.compliance;
                    return a.name.localeCompare(b.name);
                  })
                  .map((contract, index) => (
                    <tr key={index}>
                      <td className="contract-name">{contract.name}</td>
                      <td>
                        <span className={`state-badge ${contract.state.toLowerCase()}`}>
                          {contract.state}
                        </span>
                      </td>
                      <td>
                        <div className="compliance-cell">
                          <div className="compliance-bar">
                            <div 
                              className="compliance-fill"
                              style={{ 
                                width: `${contract.compliance}%`,
                                background: contract.compliance >= 80 ? COLORS.success : 
                                           contract.compliance >= 50 ? COLORS.warning : COLORS.danger
                              }}
                            />
                          </div>
                          <span className="compliance-text">{contract.compliance.toFixed(1)}%</span>
                        </div>
                      </td>
                      <td>
                        <span className="count-badge success">{contract.standardCount}</span>
                      </td>
                      <td>
                        <span className="count-badge danger">{contract.nonStandardCount}</span>
                      </td>
                      <td>
                        {contract.compliance === 100 ? (
                          <span className="status-badge success">
                            <CheckCircle size={14} /> Compliant
                          </span>
                        ) : contract.compliance > 0 ? (
                          <span className="status-badge warning">
                            <AlertCircle size={14} /> Review
                          </span>
                        ) : (
                          <span className="status-badge danger">
                            <XCircle size={14} /> Non-Compliant
                          </span>
                        )}
                      </td>
                      <td>
                        <button 
                          className="btn btn-primary btn-sm"
                          onClick={() => navigate(`/contract/${contract.state}/${contract.originalName.replace(' ', '_')}`)}
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Contract Compliance Trend */}
        <div className="card">
          <h3>Contract Compliance Overview</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={contractPerformance}>
              <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#444' : '#e0e0e0'} />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} tick={{ fill: isDark ? '#d0d0d0' : '#666' }} />
              <YAxis tick={{ fill: isDark ? '#d0d0d0' : '#666' }} />
              <Tooltip 
                formatter={(value, name) => {
                  if (name === 'Compliance %') {
                    const contract = contractPerformance.find(c => c.compliance === value);
                    if (contract) {
                      return [`${value.toFixed(1)}% (${contract.standardCount}/${contract.standardCount + contract.nonStandardCount})`, name];
                    }
                  }
                  return [value, name];
                }}
                contentStyle={{ backgroundColor: isDark ? '#16213e' : '#fff', border: isDark ? '1px solid #2d3561' : '1px solid #e0e0e0' }} 
              />
              <Legend />
              <Bar dataKey="compliance" fill={isDark ? COLORS.primaryBright : COLORS.primary} name="Compliance %" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
