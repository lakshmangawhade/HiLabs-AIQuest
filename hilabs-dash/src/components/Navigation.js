import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BarChart3, FileText, GitCompare, Home } from 'lucide-react';
import './Navigation.css';

function Navigation() {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Home },
    { path: '/comparison', label: 'State Comparison', icon: GitCompare },
  ];

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <BarChart3 size={28} />
          <span>HiLabs Contract Analysis</span>
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

        <div className="nav-info">
          <FileText size={18} />
          <span>Contract Compliance System v1.0</span>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
