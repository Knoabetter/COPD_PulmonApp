import React, { useEffect, useState } from 'react';
import * as XLSX from 'xlsx';

interface Patient {
  name: string;
  age: string;
  id_number: string;
}

function PatientList() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [file, setFile] = useState<File | null>(null);

  // Handle file upload
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;

    setFile(uploadedFile); // Save the uploaded file
    const reader = new FileReader();
    reader.onload = (event) => {
      const binaryStr = event.target?.result;
      if (binaryStr) {
        const workbook = XLSX.read(binaryStr, { type: 'binary' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData: any[] = XLSX.utils.sheet_to_json(worksheet, { defval: '' });
        console.log("Parsed Excel Data:", jsonData); // Debug: Check parsed data

        const parsedData: Patient[] = jsonData.map((row) => ({
          name: row['name'] || row['Name'],
          age: row['age']?.toString() || row['Age']?.toString(),
          id_number: row['id'] || row['ID'] || '', // Ensure it has a value
        }));
        setPatients(parsedData); // Set the patients data in state
      }
    };
    reader.readAsBinaryString(uploadedFile);
  };

  // Filter patients based on search term (search by ID only)
  const filteredPatients = patients.filter((patient) =>
    (patient.id_number?.toString() || '').toLowerCase().includes(searchTerm.toLowerCase()) // Cast id_number to string
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
              placeholder="Search by ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)} // Search by ID
            />
          </div>
        </div>

        {/* File Upload Section */}
        <div className="mb-4">
          <h6>Upload Data File:</h6>
          <input type="file" accept=".xlsx" onChange={handleFileUpload} />
        </div>

        {/* Patient Table */}
        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Age</th>
                <th>ID Number</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPatients.length > 0 ? (
                filteredPatients.map((patient, index) => (
                  <tr key={index}>
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
                  <td colSpan={4} className="text-center">No patients found</td>
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
