/**
 * Main App component with routing configuration.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';
import LostItems from './pages/LostItems';
import FoundItems from './pages/FoundItems';
import ItemDetail from './pages/ItemDetail';
import ReportItem from './pages/ReportItem';
import Claims from './pages/Claims';
import Matches from './pages/Matches';
import Users from './pages/Users';
import AWSStatus from './pages/AWSStatus';

function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/lost-items" element={<LostItems />} />
          <Route path="/found-items" element={<FoundItems />} />
          <Route path="/items/:id" element={<ItemDetail />} />
          <Route path="/report" element={<ReportItem />} />
          <Route path="/report/:type" element={<ReportItem />} />
          <Route path="/claims" element={<Claims />} />
          <Route path="/matches" element={<Matches />} />
          <Route path="/users" element={<Users />} />
          <Route path="/aws-status" element={<AWSStatus />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
