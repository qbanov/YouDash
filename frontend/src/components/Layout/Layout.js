import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import UserBar from './UserBar';
import LoadingScreen from './LoadingScreen';
import './Layout.css';

function Layout() {
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="app-layout">
      <LoadingScreen isVisible={isLoading} />
      <UserBar />
      <Sidebar />
      <div className="page-content container-fluid py-3" id="pageContent">
        <div className="row g-3">
          <div className="col-12">
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Layout;
