import { useState } from 'react';

function TestUpload() {
  const [patientId, setPatientId] = useState('');
  const [testDate, setTestDate] = useState('');
  const [notes, setNotes] = useState('');
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({text: '', type: ''});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage({text: '', type: ''});
    
    // Simulate file upload
    setTimeout(() => {
      setMessage({
        text: 'Files uploaded successfully!', 
        type: 'success'
      });
      setLoading(false);
      // Reset form in real implementation
    }, 2000);
  };

  return (
    <div className="card">
      <div className="card-header">
        <h5 className="mb-0">Upload Spirometry Tests</h5>
      </div>
      <div className="card-body">
        {message.text && (
          <div className={`alert alert-${message.type}`} role="alert">
            {message.text}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="row">
            <div className="col-md-6 mb-3">
              <label htmlFor="patientId" className="form-label">Patient ID or Search</label>
              <div className="input-group">
                <input 
                  type="text" 
                  className="form-control" 
                  id="patientId" 
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  required
                />
                <button className="btn btn-outline-secondary" type="button">Search</button>
              </div>
            </div>
            
            <div className="col-md-6 mb-3">
              <label htmlFor="testDate" className="form-label">Test Date</label>
              <input 
                type="date" 
                className="form-control" 
                id="testDate" 
                value={testDate}
                onChange={(e) => setTestDate(e.target.value)}
                required
              />
            </div>
          </div>
          
          <div className="mb-3">
            <label htmlFor="testFiles" className="form-label">Spirometry Test Files</label>
            <input 
              type="file" 
              className="form-control" 
              id="testFiles" 
              onChange={(e) => setFiles(e.target.files)}
              multiple 
              required
            />
            <div className="form-text">
              Select one or more spirometry test result files.
            </div>
          </div>
          
          <div className="mb-3">
            <label htmlFor="notes" className="form-label">Notes</label>
            <textarea 
              className="form-control" 
              id="notes" 
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            ></textarea>
          </div>
          
          <div className="d-grid gap-2 d-md-flex justify-content-md-end">
            <button 
              type="reset" 
              className="btn btn-outline-secondary me-md-2"
            >
              Clear
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Uploading...' : 'Upload Files'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default TestUpload;