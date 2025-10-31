import React from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../../services/api';

function UserBar() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/login');
    }
  };

  return (
    <div className="user-bar">
      <div className="user-info">
        <span className="user-label">Zalogowano jako:</span>
        <span className="user-name">Użytkownik</span>
      </div>
      <button className="logout-btn" onClick={handleLogout} title="Wyloguj">
        <img src="/images/logout.png" alt="Logout" className="logout-icon" />
      </button>
    </div>
  );
}

export default UserBar;
