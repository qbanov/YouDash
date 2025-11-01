import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Login from './components/Login';
import Map from './components/Map/Map';
import Explorer from './components/Explorer/Explorer';
import Log from './components/Log/Log';
import NewDetectors from './components/NewDetectors/NewDetectors';
import Tickets from './components/Tickets/Tickets';
import Hardware from './components/Hardware/Hardware';
import Contracts from './components/Contracts/Contracts';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/explorer" replace />} />
          <Route path="map" element={<Map />} />
          <Route path="explorer" element={<Explorer />} />
          <Route path="log" element={<Log />} />
          <Route path="newdetectors" element={<NewDetectors />} />
          <Route path="tickets" element={<Tickets />} />
          <Route path="hardware" element={<Hardware />} />
          <Route path="contracts" element={<Contracts />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
