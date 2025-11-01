import { useState, useEffect, createContext, useContext } from 'react';
import { Navigate } from 'react-router-dom';
import api from '../services/api';

// Create UserContext
const UserContext = createContext();

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within UserProvider');
  }
  return context;
};

const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await api.get('/api/auth/verify/');
        setIsAuthenticated(true);
        setUser({
          username: response.data.username,
          displayName: response.data.username?.split('@')[0] || 'User'
        });
      } catch (error) {
        setIsAuthenticated(false);
        setUser(null);
      }
    };

    checkAuth();
  }, []);

  if (isAuthenticated === null) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'
      }}>
        Loading...
      </div>
    );
  }

  return isAuthenticated ? (
    <UserContext.Provider value={user}>
      {children}
    </UserContext.Provider>
  ) : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
