import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BarChart3, FileText, GitCompare, Home, Sun, Moon, Upload } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import './Navigation.css';

function Navigation() {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Home },
    { path: '/comparison', label: 'State Comparison', icon: GitCompare },
    { path: '/upload', label: 'Contract Upload', icon: Upload },
  ];

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <BarChart3 size={28} />
          <span>HiLabs' Negotiation Assist</span>
        </div>
        
        <div className="nav-links">
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>

        <div className="nav-right">
          <div className="nav-info">
            <FileText size={18} />
            <span>Contract Compliance System v1.0</span>
          </div>
          <button className="theme-toggle" onClick={toggleTheme} title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}>
            {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
