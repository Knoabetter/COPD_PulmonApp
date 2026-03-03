import React, { useEffect, useState } from 'react';
import * as XLSX from 'xlsx';

interface Patient {
  id: string;
  firstName: string;
  lastName: string;
}

interface TestResult {
  id: string;
  datePre: string;
  fev1Pre: string;
  fev1PrePercent: string;
  fvcPre: string;
  fvcPrePercent: string;
  fev1FvcPre: string;
  pefPre: string;
  pefPrePercent: string;
}

function ResultsView() {
  const [data, setData] = useState<any[]>([]);
  const [selectedPatient, setSelectedPatient] = useState('');
  const [selectedTest, setSelectedTest] = useState('');
  
  // Load data from Excel - same file as PatientList
  useEffect(() => {
    fetch('/CopyExtractedDataNoID.xlsx')
      .then((res) => res.arrayBuffer())
      .then((arrayBuffer) => {
        const workbook = XLSX.read(arrayBuffer, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData: any[] = XLSX.utils.sheet_to_json(worksheet, { defval: '' });
        console.log("Parsed Excel Data:", jsonData);
        setData(jsonData);
      })
      .catch((error) => {
        console.error("Error reading Excel file:", error);
      });
  }, []);

  // Get unique patients from the data
  const patients = data.map((row, index) => ({
    id: index.toString(),
    firstName: row['First Name'] || '',
    lastName: row['Last Name'] || '',
    fullName: `${row['First Name'] || ''} ${row['Last Name'] || ''}`,
    idNumber: row['ID'] || ''
  }));

  // Filter unique patients by removing duplicates
  const uniquePatients = patients.filter((patient, index, self) => 
    index === self.findIndex(p => p.fullName === patient.fullName && p.idNumber === patient.idNumber)
  );

  // Get tests for selected patient
  const patientTests = selectedPatient ? 
    data.filter((row, index) => index.toString() === selectedPatient || 
      (row['First Name'] === patients[parseInt(selectedPatient)]?.firstName && 
       row['Last Name'] === patients[parseInt(selectedPatient)]?.lastName)) : 
    [];

  // Get the selected test details
  const selectedTestDetails = patientTests.find((_, index) => index.toString() === selectedTest);

  const getAssessment = (fev1Percent: number, fvcPercent: number, ratio: number) => {
    if (ratio < 0.7) {
      if (fev1Percent >= 80) return { text: "Mild obstructive pattern", class: "alert-warning" };
      if (fev1Percent >= 50) return { text: "Moderate obstructive pattern", class: "alert-warning" };
      return { text: "Severe obstructive pattern", class: "alert-danger" };
    }
    
    if (fvcPercent < 80) return { text: "Restrictive pattern", class: "alert-warning" };
    
    return { text: "Normal spirometry results", class: "alert-success" };
  };

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
              onChange={(e) => {
                setSelectedPatient(e.target.value);
                setSelectedTest('');
              }}
            >
              <option value="">-- Select Patient --</option>
              {uniquePatients.map(patient => (
                <option key={patient.id} value={patient.id}>
                  {patient.fullName} (ID: {patient.idNumber})
                </option>
              ))}
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
              {patientTests.map((test, index) => (
                <option key={index} value={index.toString()}>
                  {test['Date_PRE'] || 'Unknown Date'} - Spirometry
                </option>
              ))}
            </select>
          </div>
        </div>
        
        {selectedTestDetails ? (
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
                          <td>{selectedTestDetails['FEV1_PRE']} L ({selectedTestDetails['FEV1_PRE_PERCENT']}%)</td>
                        </tr>
                        <tr>
                          <th scope="row">FVC</th>
                          <td>{selectedTestDetails['FVC_PRE']} L ({selectedTestDetails['FVC_PRE_PERCENT']}%)</td>
                        </tr>
                        <tr>
                          <th scope="row">FEV1/FVC</th>
                          <td>{selectedTestDetails['FEV 1 % FVC_PRE'] || 
                               (selectedTestDetails['FEV1_PRE'] && selectedTestDetails['FVC_PRE'] ? 
                                (parseFloat(selectedTestDetails['FEV1_PRE']) / 
                                 parseFloat(selectedTestDetails['FVC_PRE'])).toFixed(2) : 'N/A')}</td>
                        </tr>
                        <tr>
                          <th scope="row">PEF</th>
                          <td>{selectedTestDetails['PEF_PRE']} L/s ({selectedTestDetails['PEF_PRE_PERCENT']}%)</td>
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
                    {(() => {
                      const fev1Percent = parseFloat(selectedTestDetails['FEV1_PRE_PERCENT'] || '0');
                      const fvcPercent = parseFloat(selectedTestDetails['FVC_PRE_PERCENT'] || '0');
                      let ratio = parseFloat(selectedTestDetails['FEV 1 % FVC_PRE'] || '0');
                      
                      if (!ratio && selectedTestDetails['FEV1_PRE'] && selectedTestDetails['FVC_PRE']) {
                        ratio = parseFloat(selectedTestDetails['FEV1_PRE']) / parseFloat(selectedTestDetails['FVC_PRE']);
                      }
                      
                      const assessment = getAssessment(fev1Percent, fvcPercent, ratio);
                      
                      return (
                        <>
                          <div className={`alert ${assessment.class}`}>
                            {assessment.text}
                          </div>
                          <p>
                            {assessment.text === "Normal spirometry results" 
                              ? 'All spirometry parameters are within normal range. No evidence of obstructive or restrictive ventilatory defects.'
                              : assessment.text.includes('obstructive')
                                ? 'Spirometry shows evidence of airflow limitation with reduced FEV1/FVC ratio.'
                                : 'Spirometry shows reduced lung volumes with preserved FEV1/FVC ratio, suggesting a restrictive pattern.'}
                          </p>
                        </>
                      );
                    })()}
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