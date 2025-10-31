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
      <div className="page-content" id="pageContent">
        <Outlet />
      </div>
    </div>
  );
}

export default Layout;
