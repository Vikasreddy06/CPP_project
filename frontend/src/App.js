/**
 * Main App component with routing and authentication.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React, { useState, useEffect, createContext, useContext } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import LostItems from './pages/LostItems';
import FoundItems from './pages/FoundItems';
import ItemDetail from './pages/ItemDetail';
import ReportItem from './pages/ReportItem';
import Claims from './pages/Claims';
import Matches from './pages/Matches';
import Users from './pages/Users';
import AWSStatus from './pages/AWSStatus';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

function ProtectedRoute({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;
  return children;
}

function App() {
  const [user, setUser] = useState(() => {
    try {
      const token = localStorage.getItem('clf_token');
      const u = JSON.parse(localStorage.getItem('clf_user') || 'null');
      return token && u ? u : null;
    } catch { return null; }
  });

  function login(userData, token) {
    localStorage.setItem('clf_token', token);
    localStorage.setItem('clf_user', JSON.stringify(userData));
    setUser(userData);
  }

  function logout() {
    localStorage.removeItem('clf_token');
    localStorage.removeItem('clf_user');
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <div className="app">
        {user && <Navbar />}
        <main className={user ? "main-content" : ""}>
          <Routes>
            <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
            <Route path="/register" element={user ? <Navigate to="/" /> : <Register />} />
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
        {user && <Footer />}
      </div>
    </AuthContext.Provider>
  );
}

export default App;
