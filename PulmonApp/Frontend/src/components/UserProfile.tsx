import React from 'react';
import { useState } from 'react';

interface UserProfileProps {
  username: string;
  onLogout: () => void;
}

function UserProfile({ username, onLogout }: UserProfileProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [email, setEmail] = useState('doctor@hospital.org');
  const [department, setDepartment] = useState('Pulmonary');
  const [notification, setNotification] = useState(true);
  
  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    // Would update user profile via API
    setIsEditing(false);
  };

  return (
    <div className="card">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h5 className="mb-0">User Profile</h5>
        {!isEditing && (
          <button 
            className="btn btn-sm btn-outline-primary"
            onClick={() => setIsEditing(true)}
          >
            Edit Profile
          </button>
        )}
      </div>
      <div className="card-body">
        {isEditing ? (
          <form onSubmit={handleSave}>
            <div className="mb-3">
              <label htmlFor="username" className="form-label">Username</label>
              <input 
                type="text" 
                className="form-control" 
                id="username" 
                value={username} 
                disabled 
              />
            </div>
            <div className="mb-3">
              <label htmlFor="email" className="form-label">Email</label>
              <input 
                type="email" 
                className="form-control" 
                id="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="mb-3">
              <label htmlFor="department" className="form-label">Department</label>
              <input 
                type="text" 
                className="form-control" 
                id="department" 
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
              />
            </div>
            <div className="mb-3 form-check">
              <input 
                type="checkbox" 
                className="form-check-input" 
                id="notification" 
                checked={notification}
                onChange={(e) => setNotification(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="notification">
                Email notifications for new test results
              </label>
            </div>
            <div className="d-flex justify-content-end">
              <button 
                type="button" 
                className="btn btn-outline-secondary me-2"
                onClick={() => setIsEditing(false)}
              >
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                Save Changes
              </button>
            </div>
          </form>
        ) : (
          <div>
            <div className="row mb-4">
              <div className="col-md-4 fw-bold">Username:</div>
              <div className="col-md-8">{username}</div>
            </div>
            <div className="row mb-4">
              <div className="col-md-4 fw-bold">Email:</div>
              <div className="col-md-8">{email}</div>
            </div>
            <div className="row mb-4">
              <div className="col-md-4 fw-bold">Department:</div>
              <div className="col-md-8">{department}</div>
            </div>
            <div className="row mb-4">
              <div className="col-md-4 fw-bold">Notifications:</div>
              <div className="col-md-8">
                {notification ? 'Enabled' : 'Disabled'}
              </div>
            </div>
            <div className="mt-4">
              <button 
                className="btn btn-danger" 
                onClick={onLogout}
              >
                Logout
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default UserProfile;