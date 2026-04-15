/**
 * Main App component with routing and authentication.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LostItems from './pages/LostItems';
import FoundItems from './pages/FoundItems';
import ItemDetail from './pages/ItemDetail';
import ReportItem from './pages/ReportItem';
import Claims from './pages/Claims';
import Matches from './pages/Matches';
import Users from './pages/Users';
import AWSStatus from './pages/AWSStatus';

function isLoggedIn() {
  return !!localStorage.getItem('clf_token');
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem('clf_user') || 'null');
  } catch { return null; }
}

function ProtectedRoute({ children }) {
  if (!isLoggedIn()) return <Navigate to="/login" />;
  return children;
}

function App() {
  const user = getUser();
  const loggedIn = isLoggedIn();

  return (
    <div className="app">
      {loggedIn && <Navbar />}
      <main className={loggedIn ? "main-content" : ""}>
        <Routes>
          <Route path="/login" element={loggedIn ? <Navigate to="/" /> : <Login />} />
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/lost-items" element={<ProtectedRoute><LostItems /></ProtectedRoute>} />
          <Route path="/found-items" element={<ProtectedRoute><FoundItems /></ProtectedRoute>} />
          <Route path="/items/:id" element={<ProtectedRoute><ItemDetail /></ProtectedRoute>} />
          <Route path="/report" element={<ProtectedRoute><ReportItem /></ProtectedRoute>} />
          <Route path="/report/:type" element={<ProtectedRoute><ReportItem /></ProtectedRoute>} />
          <Route path="/claims" element={<ProtectedRoute><Claims /></ProtectedRoute>} />
          <Route path="/matches" element={<ProtectedRoute><Matches /></ProtectedRoute>} />
          <Route path="/users" element={<ProtectedRoute><Users /></ProtectedRoute>} />
          <Route path="/aws-status" element={<ProtectedRoute><AWSStatus /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
      {loggedIn && <Footer />}
    </div>
  );
}

export default App;
