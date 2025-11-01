import React, { useState } from 'react';
import { authAPI } from '../services/api';
import './Login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      const response = await authAPI.login({ username, password });
      window.location.href = '/explorer';
    } catch (err) {
      setError('Nieprawidłowe dane logowania');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="d-flex align-items-center justify-content-center min-vh-100" style={{backgroundColor: '#f8f9fa'}}>
      <div className="card login-card">
        <div className="card-body p-4">
          <h2 className="login-title text-center mb-4">
            Logowanie
          </h2>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="username" className="form-label">
                Nazwa użytkownika:
              </label>
              <input 
                type="text"
                id="username"
                className="form-control login-input"
                placeholder="Wprowadź nazwę użytkownika"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
              />
            </div>
            
            <div className="mb-3">
              <label htmlFor="password" className="form-label">
                Hasło:
              </label>
              <input 
                type="password"
                id="password"
                className="form-control login-input"
                placeholder="Wprowadź hasło"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>
            
            <button 
              type="submit" 
              className={`btn login-btn w-100 mt-2 ${loading ? 'loading' : ''}`}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </span>
                  Logowanie...
                </>
              ) : (
                'Zaloguj się'
              )}
            </button>
          </form>

          {error && (
            <div className="alert login-error mt-3 mb-0" role="alert">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Login;
