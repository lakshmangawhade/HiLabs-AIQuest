import React, { useState, useMemo } from 'react';
import { PieChart, Pie, BarChart, Bar, LineChart, Line, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { FileText, TrendingUp, TrendingDown, Award, AlertCircle, CheckCircle, XCircle, Filter } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const COLORS = {
  primary: '#667eea',
  secondary: '#764ba2',
  success: '#48bb78',
  warning: '#f6ad55',
  danger: '#fc8181',
  info: '#63b3ed',
  purple: '#9f7aea',
  pink: '#ed64a6'
};

function Dashboard({ tnData, waData }) {
  const navigate = useNavigate();
  const [selectedState, setSelectedState] = useState('all');
  const [selectedMetric, setSelectedMetric] = useState('compliance');

  // Calculate overall statistics
  const stats = useMemo(() => {
    const allContracts = [...(tnData || []), ...(waData || [])];
    
    const totalContracts = allContracts.length;
    const avgCompliance = allContracts.reduce((sum, c) => sum + c.summary.overview.compliance_rate, 0) / totalContracts;
    
    const fullyCompliant = allContracts.filter(c => c.summary.overview.compliance_rate === 100).length;
    const partiallyCompliant = allContracts.filter(c => c.summary.overview.compliance_rate > 0 && c.summary.overview.compliance_rate < 100).length;
    const nonCompliant = allContracts.filter(c => c.summary.overview.compliance_rate === 0).length;

    // State-specific stats
    const tnAvgCompliance = tnData ? tnData.reduce((sum, c) => sum + c.summary.overview.compliance_rate, 0) / tnData.length : 0;
    const waAvgCompliance = waData ? waData.reduce((sum, c) => sum + c.summary.overview.compliance_rate, 0) / waData.length : 0;

    return {
      totalContracts,
      avgCompliance,
      fullyCompliant,
      partiallyCompliant,
      nonCompliant,
      tnAvgCompliance,
      waAvgCompliance,
      tnCount: tnData ? tnData.length : 0,
      waCount: waData ? waData.length : 0
    };
  }, [tnData, waData]);

  // Prepare data for pie chart
  const complianceDistribution = [
    { name: 'Fully Compliant', value: stats.fullyCompliant, color: COLORS.success },
    { name: 'Partially Compliant', value: stats.partiallyCompliant, color: COLORS.warning },
    { name: 'Non-Compliant', value: stats.nonCompliant, color: COLORS.danger }
  ];

  // Prepare data for state comparison
  const stateComparison = [
    { state: 'Tennessee', compliance: stats.tnAvgCompliance, contracts: stats.tnCount },
    { state: 'Washington', compliance: stats.waAvgCompliance, contracts: stats.waCount }
  ];

  // Get filtered contracts based on selected state
  const getFilteredContracts = () => {
    if (selectedState === 'TN') return tnData || [];
    if (selectedState === 'WA') return waData || [];
    return [...(tnData || []), ...(waData || [])];
  };

  // Prepare contract performance data
  const contractPerformance = getFilteredContracts().map(contract => ({
    name: contract.name.replace('_Redacted', '').replace('_', ' '),
    compliance: contract.summary.overview.compliance_rate,
    standard: contract.summary.overview.standard_count,
    nonStandard: contract.summary.overview.non_standard_count,
    state: contract.state
  }));

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
        exact: COLORS.success,
        regex: COLORS.info,
        fuzzy: COLORS.warning,
        semantic: COLORS.purple,
        no_match: COLORS.danger
      }[type] || COLORS.primary
    }));
  }, [selectedState, tnData, waData]);

  // Prepare radar chart data for attribute analysis
  const attributeAnalysis = useMemo(() => {
    const contracts = getFilteredContracts();
    const attributes = ['Medicare Fee Schedule', 'Medicaid Fee Schedule', 'Medicare Timely Filing', 'Medicaid Timely Filing', 'No Steerage/SOC'];
    
    return attributes.map(attr => {
      const compliantCount = contracts.filter(c => 
        c.summary.attribute_lists?.standard?.includes(attr)
      ).length;
      
      return {
        attribute: attr.replace(' Schedule', '').replace('Timely Filing', 'Filing'),
        compliance: (compliantCount / contracts.length) * 100
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
          <div className="header-filters">
            <select 
              className="filter-select"
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
            >
              <option value="all">All States</option>
              <option value="TN">Tennessee</option>
              <option value="WA">Washington</option>
            </select>
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
              <p className="metric-detail">{stats.tnCount} TN | {stats.waCount} WA</p>
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
            <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #fc8181, #f56565)' }}>
              <AlertCircle size={24} />
            </div>
            <div className="metric-content">
              <p className="metric-label">Need Review</p>
              <h3 className="metric-value">{stats.partiallyCompliant + stats.nonCompliant}</h3>
              <p className="metric-detail">{stats.partiallyCompliant} partial | {stats.nonCompliant} non-compliant</p>
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
                <Bar dataKey="compliance" fill={COLORS.primary} name="Avg Compliance %" radius={[8, 8, 0, 0]} />
                <Bar dataKey="contracts" fill={COLORS.secondary} name="Contract Count" radius={[8, 8, 0, 0]} />
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
            <h3>Attribute Compliance Rate</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={attributeAnalysis}>
                <PolarGrid />
                <PolarAngleAxis dataKey="attribute" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar name="Compliance %" dataKey="compliance" stroke={COLORS.primary} fill={COLORS.primary} fillOpacity={0.6} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Contract Performance Table */}
        <div className="card">
          <div className="table-header">
            <h3>Contract Performance Details</h3>
            <div className="table-filters">
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
                  <th>Compliance Rate</th>
                  <th>Standard</th>
                  <th>Non-Standard</th>
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
                        <span className="count-badge success">{contract.standard}</span>
                      </td>
                      <td>
                        <span className="count-badge danger">{contract.nonStandard}</span>
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
                          onClick={() => navigate(`/contract/${contract.state}/${contract.name.replace(' ', '_')}`)}
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
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="compliance" fill={COLORS.primary} name="Compliance %" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
