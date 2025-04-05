import { useState, useEffect } from 'react'
import './App.css'
import axios from 'axios'
import LoginForm from './components/LoginForm'
import Dashboard from './components/Dashboard'
import React from 'react'

interface AuthState {
  isAuthenticated: boolean;
  username: string | null;
  isLoading: boolean;
}

function App() {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    username: null,
    isLoading: true
  });

  useEffect(() => {
    // Check authentication status on load
    axios.get('/api/auth/status/')
      .then(response => {
        setAuthState({
          isAuthenticated: response.data.isAuthenticated,
          username: response.data.username || null,
          isLoading: false
        });
      })
      .catch(() => {
        setAuthState({
          isAuthenticated: false,
          username: null,
          isLoading: false
        });
      });
  }, []);

  const handleLoginSuccess = (username: string) => {
    setAuthState({
      isAuthenticated: true,
      username: username,
      isLoading: false
    });
  };

  const handleLogout = () => {
    axios.get('/api/auth/logout/')
      .then(() => {
        setAuthState({
          isAuthenticated: false,
          username: null,
          isLoading: false
        });
      });
  };

  if (authState.isLoading) {
    return <div className="container mt-5"><p>Loading...</p></div>;
  }

  return (
    <div className="container">
      {authState.isAuthenticated ? (
        <Dashboard 
          username={authState.username!} 
          onLogout={handleLogout} 
        />
      ) : (
        <LoginForm onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App