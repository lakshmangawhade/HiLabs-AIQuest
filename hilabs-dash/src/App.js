import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Dashboard from './components/Dashboard';
import ContractDetails from './components/ContractDetails';
import StateComparison from './components/StateComparison';
import ContractUpload from './components/ContractUpload';
import Navigation from './components/Navigation';
import './App.css';

function App() {
  const [tnData, setTnData] = useState(null);
  const [waData, setWaData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load data from Backend results
    const loadData = async () => {
      try {
        // Load TN data
        const tnContracts = await loadStateData('TN');
        setTnData(tnContracts);

        // Load WA data
        const waContracts = await loadStateData('WA');
        setWaData(waContracts);

        setLoading(false);
      } catch (error) {
        console.error('Error loading data:', error);
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const loadStateData = async (state) => {
    const contracts = [];
    const contractFolders = state === 'TN' 
      ? ['TN_Contract1_Redacted', 'TN_Contract2_Redacted', 'TN_Contract3_Redacted', 'TN_Contract4_Redacted', 'TN_Contract5_Redacted']
      : ['WA_1_Redacted', 'WA_2_Redacted', 'WA_3_Redacted', 'WA_4_Redacted', 'WA_5_Redacted'];

    for (const folder of contractFolders) {
      try {
        const summaryResponse = await fetch(`/Backend/results/${state}/${folder}/summary.json`);
        const detailsResponse = await fetch(`/Backend/results/${state}/${folder}/detailed_results.json`);
        
        if (summaryResponse.ok && detailsResponse.ok) {
          const summary = await summaryResponse.json();
          const details = await detailsResponse.json();
          
          contracts.push({
            name: folder,
            state: state,
            summary,
            details
          });
        }
      } catch (error) {
        console.error(`Error loading ${folder}:`, error);
      }
    }

    return contracts;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <h2>Loading Contract Analysis Data...</h2>
      </div>
    );
  }

  return (
    <ThemeProvider>
      <Router>
        <div className="App">
          <Navigation />
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="/dashboard" element={<Dashboard tnData={tnData} waData={waData} />} />
            <Route path="/contract/:state/:name" element={<ContractDetails tnData={tnData} waData={waData} />} />
            <Route path="/comparison" element={<StateComparison tnData={tnData} waData={waData} />} />
            <Route path="/upload" element={<ContractUpload />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
