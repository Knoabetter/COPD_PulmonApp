import './App.css'
import Dashboard from './components/Dashboard';
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";

function App() {
  return (
    <div className="App">
      <Dashboard 
        username="MD" 
        onLogout={() => window.location.reload()} 
      />
    </div>
  );   
}

export default App