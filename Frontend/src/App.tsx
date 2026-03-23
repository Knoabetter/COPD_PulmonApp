import { useState } from 'react';
import './App.css'
import Dashboard from './components/Dashboard';
import LoginPage from './components/LoginPage';
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";

function App() {
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem('auth_token')
  );

  const handleLogin = (newToken: string) => {
    localStorage.setItem('auth_token', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
  };

  if (!token) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="App">
      <Dashboard
        username=""
        onLogout={handleLogout}
      />
    </div>
  );
}

export default App
