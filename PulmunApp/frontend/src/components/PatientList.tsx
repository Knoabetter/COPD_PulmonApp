import React from 'react';
import { useState } from 'react';

function PatientList() {
  const [searchTerm, setSearchTerm] = useState('');
  
  // Placeholder patient data - will come from API in real implementation
  const patients = [
    { id: 1, name: 'John Doe', age: 45, id_number: '123456789' },
    { id: 2, name: 'Jane Smith', age: 52, id_number: '987654321' },
    { id: 3, name: 'Robert Johnson', age: 67, id_number: '456789123' },
  ];
  
  const filteredPatients = patients.filter(patient => 
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.id_number.includes(searchTerm)
  );

  return (
    <div className="card">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h5 className="mb-0">Patient List</h5>
        <button className="btn btn-sm btn-primary">Add New Patient</button>
      </div>
      <div className="card-body">
        <div className="mb-4">
          <div className="input-group">
            <input 
              type="text" 
              className="form-control" 
              placeholder="Search by name or ID..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <button className="btn btn-outline-secondary" type="button">Search</button>
          </div>
        </div>
        
        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Age</th>
                <th>ID Number</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPatients.length > 0 ? (
                filteredPatients.map(patient => (
                  <tr key={patient.id}>
                    <td>{patient.id}</td>
                    <td>{patient.name}</td>
                    <td>{patient.age}</td>
                    <td>{patient.id_number}</td>
                    <td>
                      <button className="btn btn-sm btn-info me-2">View</button>
                      <button className="btn btn-sm btn-secondary">Tests</button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="text-center">No patients found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default PatientList;