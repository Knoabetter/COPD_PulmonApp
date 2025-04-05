import { useState } from 'react';

function ResultsView() {
  const [selectedPatient, setSelectedPatient] = useState('');
  const [selectedTest, setSelectedTest] = useState('');
  
  // Placeholder test data - would come from API
  const tests = [
    { id: 1, date: '2025-03-15', type: 'Spirometry' },
    { id: 2, date: '2025-02-20', type: 'Spirometry' },
    { id: 3, date: '2024-12-10', type: 'Spirometry' },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <h5 className="mb-0">Test Results</h5>
      </div>
      <div className="card-body">
        <div className="row mb-4">
          <div className="col-md-6">
            <label htmlFor="patientSelect" className="form-label">Select Patient</label>
            <select 
              className="form-select" 
              id="patientSelect"
              value={selectedPatient}
              onChange={(e) => setSelectedPatient(e.target.value)}
            >
              <option value="">-- Select Patient --</option>
              <option value="1">John Doe (ID: 123456789)</option>
              <option value="2">Jane Smith (ID: 987654321)</option>
              <option value="3">Robert Johnson (ID: 456789123)</option>
            </select>
          </div>
          
          <div className="col-md-6">
            <label htmlFor="testSelect" className="form-label">Select Test</label>
            <select 
              className="form-select" 
              id="testSelect"
              value={selectedTest}
              onChange={(e) => setSelectedTest(e.target.value)}
              disabled={!selectedPatient}
            >
              <option value="">-- Select Test --</option>
              {tests.map(test => (
                <option key={test.id} value={test.id}>
                  {test.date} - {test.type}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        {selectedTest ? (
          <div>
            <div className="row">
              <div className="col-md-6">
                <div className="card mb-4">
                  <div className="card-header">Key Metrics</div>
                  <div className="card-body">
                    <table className="table table-sm">
                      <tbody>
                        <tr>
                          <th scope="row">FEV1</th>
                          <td>3.5 L (85%)</td>
                        </tr>
                        <tr>
                          <th scope="row">FVC</th>
                          <td>4.2 L (90%)</td>
                        </tr>
                        <tr>
                          <th scope="row">FEV1/FVC</th>
                          <td>0.83 (95%)</td>
                        </tr>
                        <tr>
                          <th scope="row">PEF</th>
                          <td>9.1 L/s (88%)</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="card mb-4">
                  <div className="card-header">Assessment</div>
                  <div className="card-body">
                    <div className="alert alert-success">
                      Normal spirometry results
                    </div>
                    <p>
                      All spirometry parameters are within normal range.
                      No evidence of obstructive or restrictive ventilatory defects.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="card">
              <div className="card-header">Flow-Volume Loop</div>
              <div className="card-body text-center">
                <div style={{ height: '300px', backgroundColor: '#f8f9fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <p className="text-muted">Flow-Volume Loop Visualization</p>
                </div>
                <div className="mt-3">
                  <button className="btn btn-sm btn-primary me-2">Export Results</button>
                  <button className="btn btn-sm btn-outline-secondary">Print Report</button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="alert alert-info">
            Please select a patient and test to view results.
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultsView;