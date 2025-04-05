import { useState } from 'react';
import PatientList from './PatientList';
import TestUpload from './TestUpload';
import ResultsView from './ResultsView';
import UserProfile from './UserProfile';
import React from 'react';

interface DashboardProps {
  username: string;
  onLogout: () => void;
}

function Dashboard({ username, onLogout }: DashboardProps) {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'patients':
        return <PatientList />;
      case 'upload':
        return <TestUpload />;
      case 'results':
        return <ResultsView />;
      case 'profile':
        return <UserProfile username={username} onLogout={onLogout} />;
      default:
        return (
          <div className="jumbotron bg-light p-5 rounded">
            <h1>Welcome to Pulmonary Institute Dashboard</h1>
            <p className="lead">
              This application helps manage spirometry test results and provides key insights for physicians.
            </p>
            <hr className="my-4" />
            <p>Use the navigation menu to access different features.</p>
          </div>
        );
    }
  };

  return (
    <div>
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
        <div className="container-fluid">
          <a className="navbar-brand" href="#!">Pulmonary Institute</a>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav">
              <li className="nav-item">
                <a 
                  className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`} 
                  href="#!"
                  onClick={(e) => {e.preventDefault(); setActiveTab('dashboard')}}
                >
                  Dashboard
                </a>
              </li>
              <li className="nav-item">
                <a 
                  className={`nav-link ${activeTab === 'patients' ? 'active' : ''}`} 
                  href="#!"
                  onClick={(e) => {e.preventDefault(); setActiveTab('patients')}}
                >
                  Patients
                </a>
              </li>
              <li className="nav-item">
                <a 
                  className={`nav-link ${activeTab === 'upload' ? 'active' : ''}`} 
                  href="#!"
                  onClick={(e) => {e.preventDefault(); setActiveTab('upload')}}
                >
                  Upload Tests
                </a>
              </li>
              <li className="nav-item">
                <a 
                  className={`nav-link ${activeTab === 'results' ? 'active' : ''}`} 
                  href="#!"
                  onClick={(e) => {e.preventDefault(); setActiveTab('results')}}
                >
                  View Results
                </a>
              </li>
            </ul>
            <ul className="navbar-nav ms-auto">
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle" href="#!" role="button" data-bs-toggle="dropdown">
                  {username}
                </a>
                <ul className="dropdown-menu dropdown-menu-end">
                  <li>
                    <a 
                      className="dropdown-item" 
                      href="#!"
                      onClick={(e) => {e.preventDefault(); setActiveTab('profile')}}
                    >
                      Profile
                    </a>
                  </li>
                  <li><hr className="dropdown-divider" /></li>
                  <li>
                    <a 
                      className="dropdown-item" 
                      href="#!"
                      onClick={(e) => {e.preventDefault(); onLogout()}}
                    >
                      Logout
                    </a>
                  </li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      
      {renderContent()}
    </div>
  );
}

export default Dashboard;