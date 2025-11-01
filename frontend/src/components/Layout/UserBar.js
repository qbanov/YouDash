import React from 'react';
import { authAPI } from '../../services/api';
import { useUser } from '../ProtectedRoute';

function UserBar() {
  const user = useUser();

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout error:', error);
      window.location.href = '/login';
    }
  };

  return (
    <div className="user-bar">
      <div className="user-info">
        <span className="user-label">Zalogowano jako:</span>
        <span className="user-name">{user?.displayName || 'User'}</span>
      </div>
      <button className="logout-btn" onClick={handleLogout} title="Wyloguj">
        <img src="/images/logout.png" alt="Logout" className="logout-icon" />
      </button>
    </div>
  );
}

export default UserBar;
