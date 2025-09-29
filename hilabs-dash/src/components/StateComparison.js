import React, { useMemo } from 'react';
import { BarChart, Bar, LineChart, Line, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, Area, AreaChart } from 'recharts';
import { TrendingUp, TrendingDown, Activity, BarChart3, PieChart as PieChartIcon } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import './StateComparison.css';

const COLORS = {
  tn: '#667eea',
  wa: '#764ba2',
  success: '#48bb78',
  warning: '#f6ad55',
  danger: '#fc8181',
  info: '#63b3ed',
  // Bright colors for dark theme
  tnBright: '#818cf8',
  waBright: '#a78bfa',
  successBright: '#6ee7b7',
  warningBright: '#fbbf24',
  dangerBright: '#f87171',
  infoBright: '#93c5fd'
};

function StateComparison({ tnData, waData }) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  // Calculate comprehensive state metrics
  const stateMetrics = useMemo(() => {
    const calculateStateMetrics = (data, stateName) => {
      if (!data || data.length === 0) return null;
      
      const totalContracts = data.length;
      const avgCompliance = data.reduce((sum, c) => sum + c.summary.overview.compliance_rate, 0) / totalContracts;
      const fullyCompliant = data.filter(c => c.summary.overview.compliance_rate === 100).length;
      const partiallyCompliant = data.filter(c => c.summary.overview.compliance_rate > 0 && c.summary.overview.compliance_rate < 100).length;
      const nonCompliant = data.filter(c => c.summary.overview.compliance_rate === 0).length;
      
      // Calculate average confidence
      const avgConfidence = data.reduce((sum, c) => {
        const conf = c.summary.confidence_stats?.average || 0;
        return sum + conf;
      }, 0) / totalContracts;
      
      // Calculate match type totals
      const matchTypes = {};
      data.forEach(contract => {
        Object.entries(contract.summary.match_type_distribution || {}).forEach(([type, count]) => {
          matchTypes[type] = (matchTypes[type] || 0) + count;
        });
      });
      
      // Calculate attribute compliance
      const attributes = {};
      data.forEach(contract => {
        contract.summary.attribute_lists?.standard?.forEach(attr => {
          attributes[attr] = (attributes[attr] || 0) + 1;
        });
      });
      
      return {
        name: stateName,
        totalContracts,
        avgCompliance,
        avgConfidence,
        fullyCompliant,
        partiallyCompliant,
        nonCompliant,
        matchTypes,
        attributes,
        complianceRate: (fullyCompliant / totalContracts) * 100
      };
    };
    
    return {
      tn: calculateStateMetrics(tnData, 'Tennessee'),
      wa: calculateStateMetrics(waData, 'Washington')
    };
  }, [tnData, waData]);

  // Prepare comparison data
  const comparisonData = [
    {
      metric: 'Avg Compliance',
      Tennessee: stateMetrics.tn?.avgCompliance || 0,
      Washington: stateMetrics.wa?.avgCompliance || 0
    },
    {
      metric: 'Avg Confidence',
      Tennessee: (stateMetrics.tn?.avgConfidence || 0) * 100,
      Washington: (stateMetrics.wa?.avgConfidence || 0) * 100
    },
    {
      metric: 'Full Compliance Rate',
      Tennessee: stateMetrics.tn?.complianceRate || 0,
      Washington: stateMetrics.wa?.complianceRate || 0
    }
  ];

  // Prepare contract distribution data
  const distributionData = [
    {
      category: 'Fully Compliant',
      Tennessee: stateMetrics.tn?.fullyCompliant || 0,
      Washington: stateMetrics.wa?.fullyCompliant || 0
    },
    {
      category: 'Partially Compliant',
      Tennessee: stateMetrics.tn?.partiallyCompliant || 0,
      Washington: stateMetrics.wa?.partiallyCompliant || 0
    },
    {
      category: 'Non-Compliant',
      Tennessee: stateMetrics.tn?.nonCompliant || 0,
      Washington: stateMetrics.wa?.nonCompliant || 0
    }
  ];

  // Prepare match type comparison
  const matchTypeComparison = useMemo(() => {
    const types = ['exact', 'regex', 'fuzzy', 'semantic', 'no_match'];
    return types.map(type => ({
      type: type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' '),
      Tennessee: stateMetrics.tn?.matchTypes[type] || 0,
      Washington: stateMetrics.wa?.matchTypes[type] || 0
    }));
  }, [stateMetrics]);

  // Prepare attribute compliance comparison
  const attributeComparison = useMemo(() => {
    const allAttributes = new Set([
      ...(stateMetrics.tn ? Object.keys(stateMetrics.tn.attributes) : []),
      ...(stateMetrics.wa ? Object.keys(stateMetrics.wa.attributes) : [])
    ]);
    
    return Array.from(allAttributes).map(attr => ({
      attribute: attr.replace(' Schedule', '').replace('Timely Filing', 'Filing'),
      Tennessee: ((stateMetrics.tn?.attributes[attr] || 0) / (stateMetrics.tn?.totalContracts || 1)) * 100,
      Washington: ((stateMetrics.wa?.attributes[attr] || 0) / (stateMetrics.wa?.totalContracts || 1)) * 100
    }));
  }, [stateMetrics]);

  // Individual contract performance
  const contractPerformance = useMemo(() => {
    const tnContracts = (tnData || []).map((c, index) => {
      const contractNumber = c.name.match(/\d+/)?.[0] || (index + 1);
      return {
        name: `TN${contractNumber}`,
        compliance: c.summary.overview.compliance_rate,
        state: 'TN',
        standardCount: c.summary.overview.standard_count,
        nonStandardCount: c.summary.overview.non_standard_count
      };
    });
    
    const waContracts = (waData || []).map((c, index) => {
      const contractNumber = c.name.match(/\d+/)?.[0] || (index + 1);
      return {
        name: `WA${contractNumber}`,
        compliance: c.summary.overview.compliance_rate,
        state: 'WA',
        standardCount: c.summary.overview.standard_count,
        nonStandardCount: c.summary.overview.non_standard_count
      };
    });
    
    return [...tnContracts, ...waContracts].sort((a, b) => b.compliance - a.compliance);
  }, [tnData, waData]);

  return (
    <div className="state-comparison">
      <div className="container">
        {/* Header */}
        <div className="comparison-header">
          <h1>State-by-State Comparison</h1>
          <p className="subtitle">Detailed analysis comparing Tennessee and Washington contract compliance</p>
        </div>

        {/* State Summary Cards */}
        <div className="state-cards">
          <div className="state-card tn">
            <div className="state-card-header">
              <h2>Tennessee</h2>
              <span className="state-icon">TN</span>
            </div>
            <div className="state-metrics">
              <div className="state-metric">
                <span className="metric-label">Contracts</span>
                <span className="metric-value">{stateMetrics.tn?.totalContracts || 0}</span>
              </div>
              <div className="state-metric">
                <span className="metric-label">Avg Compliance</span>
                <span className="metric-value">{(stateMetrics.tn?.avgCompliance || 0).toFixed(1)}%</span>
              </div>
              <div className="state-metric">
                <span className="metric-label">Fully Compliant</span>
                <span className="metric-value">{stateMetrics.tn?.fullyCompliant || 0}</span>
              </div>
              <div className="state-metric">
                <span className="metric-label">Avg Confidence</span>
                <span className="metric-value">{((stateMetrics.tn?.avgConfidence || 0) * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>

          <div className="state-card wa">
            <div className="state-card-header">
              <h2>Washington</h2>
              <span className="state-icon">WA</span>
            </div>
            <div className="state-metrics">
              <div className="state-metric">
                <span className="metric-label">Contracts</span>
                <span className="metric-value">{stateMetrics.wa?.totalContracts || 0}</span>
              </div>
              <div className="state-metric">
                <span className="metric-label">Avg Compliance</span>
                <span className="metric-value">{(stateMetrics.wa?.avgCompliance || 0).toFixed(1)}%</span>
              </div>
              <div className="state-metric">
                <span className="metric-label">Fully Compliant</span>
                <span className="metric-value">{stateMetrics.wa?.fullyCompliant || 0}</span>
              </div>
              <div className="state-metric">
                <span className="metric-label">Avg Confidence</span>
                <span className="metric-value">{((stateMetrics.wa?.avgConfidence || 0) * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Comparison Charts */}
        <div className="comparison-grid">
          <div className="chart-card">
            <h3>Key Metrics Comparison</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="metric" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Tennessee" fill={isDark ? COLORS.tnBright : COLORS.tn} radius={[8, 8, 0, 0]} />
                <Bar dataKey="Washington" fill={isDark ? COLORS.waBright : COLORS.wa} radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Contract Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distributionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Tennessee" fill={isDark ? COLORS.tnBright : COLORS.tn} />
                <Bar dataKey="Washington" fill={isDark ? COLORS.waBright : COLORS.wa} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="comparison-grid">
          <div className="chart-card">
            <h3>Match Type Analysis</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={matchTypeComparison}>
                <PolarGrid />
                <PolarAngleAxis dataKey="type" />
                <PolarRadiusAxis />
                <Radar name="Tennessee" dataKey="Tennessee" stroke={isDark ? COLORS.tnBright : COLORS.tn} fill={isDark ? COLORS.tnBright : COLORS.tn} fillOpacity={0.6} />
                <Radar name="Washington" dataKey="Washington" stroke={isDark ? COLORS.waBright : COLORS.wa} fill={isDark ? COLORS.waBright : COLORS.wa} fillOpacity={0.6} />
                <Legend />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Clause Compliance Rates</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={attributeComparison}>
                <PolarGrid stroke={isDark ? '#444' : '#ccc'} />
                <PolarAngleAxis dataKey="attribute" tick={{ fill: isDark ? '#d0d0d0' : '#666' }} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: isDark ? '#d0d0d0' : '#666' }} />
                <Radar name="Tennessee" dataKey="Tennessee" stroke={isDark ? COLORS.tnBright : COLORS.tn} fill={isDark ? COLORS.tnBright : COLORS.tn} fillOpacity={0.6} />
                <Radar name="Washington" dataKey="Washington" stroke={isDark ? COLORS.waBright : COLORS.wa} fill={isDark ? COLORS.waBright : COLORS.wa} fillOpacity={0.6} />
                <Legend />
                <Tooltip contentStyle={{ backgroundColor: isDark ? '#16213e' : '#fff', border: isDark ? '1px solid #2d3561' : '1px solid #e0e0e0' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Performance Ranking */}
        <div className="card">
          <h3>Contract Performance Ranking</h3>
          <div className="ranking-table">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Contract</th>
                  <th>State</th>
                  <th>Compliance Rate</th>
                  <th>Standard</th>
                  <th>Non-Standard</th>
                  <th>Performance</th>
                </tr>
              </thead>
              <tbody>
                {contractPerformance.map((contract, index) => (
                  <tr key={index}>
                    <td className="rank">
                      <span className={`rank-badge ${index < 3 ? 'top' : ''}`}>
                        #{index + 1}
                      </span>
                    </td>
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
                      <span className="count-badge success">{contract.standardCount || 0}</span>
                    </td>
                    <td>
                      <span className="count-badge danger">{contract.nonStandardCount || 0}</span>
                    </td>
                    <td>
                      {contract.compliance >= 80 ? (
                        <span className="performance-badge excellent">
                          <TrendingUp size={14} /> Excellent
                        </span>
                      ) : contract.compliance >= 50 ? (
                        <span className="performance-badge good">
                          <Activity size={14} /> Good
                        </span>
                      ) : (
                        <span className="performance-badge poor">
                          <TrendingDown size={14} /> Needs Improvement
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Insights */}
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-icon" style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)' }}>
              <BarChart3 size={24} />
            </div>
            <div className="insight-content">
              <h4>Best Performing State</h4>
              <p className="insight-value">
                {(stateMetrics.tn?.avgCompliance || 0) > (stateMetrics.wa?.avgCompliance || 0) ? 'Tennessee' : 'Washington'}
              </p>
              <p className="insight-detail">
                Higher average compliance rate across all contracts
              </p>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon" style={{ background: 'linear-gradient(135deg, #48bb78, #38a169)' }}>
              <PieChartIcon size={24} />
            </div>
            <div className="insight-content">
              <h4>Compliance Gap</h4>
              <p className="insight-value">
                {Math.abs((stateMetrics.tn?.avgCompliance || 0) - (stateMetrics.wa?.avgCompliance || 0)).toFixed(1)}%
              </p>
              <p className="insight-detail">
                Difference in average compliance between states
              </p>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon" style={{ background: 'linear-gradient(135deg, #f6ad55, #ed8936)' }}>
              <Activity size={24} />
            </div>
            <div className="insight-content">
              <h4>Total Contracts Analyzed</h4>
              <p className="insight-value">
                {(stateMetrics.tn?.totalContracts || 0) + (stateMetrics.wa?.totalContracts || 0)}
              </p>
              <p className="insight-detail">
                Across both Tennessee and Washington
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default StateComparison;
