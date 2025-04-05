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

  useEffect(() => {
    fetch('/CopyExtractedDataNoID.xlsx')
      .then((res) => res.arrayBuffer())
      .then((arrayBuffer) => {
        const workbook = XLSX.read(arrayBuffer, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData: any[] = XLSX.utils.sheet_to_json(worksheet, { defval: '' });
        console.log("Parsed Excel Data:", jsonData);
        const parsedData: Patient[] = jsonData.map((row) => ({
          name: row['name'] || row['Name'],
          age: row['age']?.toString() || row['Age']?.toString(),
          id_number: row['id_number'] || row['ID Number'] || '',
        }));
        setPatients(parsedData);
      })
      .catch((error) => {
        console.error("Error reading Excel file:", error);
      });
  }, []);

  const filteredPatients = patients.filter((patient) =>
    patient.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.id_number?.includes(searchTerm)
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
          </div>
        </div>

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
                    <tr key={index}> {/* 🔑 Use index as the temporary ID */}
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
