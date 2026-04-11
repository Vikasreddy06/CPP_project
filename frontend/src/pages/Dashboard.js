/**
 * Dashboard page -- displays aggregate statistics and recent items.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { itemsApi } from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentItems, setRecentItems] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [statsData, items] = await Promise.all([
        itemsApi.getStats(),
        itemsApi.getAll(),
      ]);
      setStats(statsData);
      setRecentItems(items.slice(0, 10));
    } catch (err) {
      setError('Failed to load dashboard data. Is the backend running?');
    }
  }

  if (error) {
    return (
      <div>
        <h1>Dashboard</h1>
        <div className="card" style={{ marginTop: 16, color: 'var(--danger)' }}>{error}</div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <Link to="/report" className="btn btn-primary">Report Item</Link>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total_items}</div>
            <div className="stat-label">Total Itemss</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: 'var(--danger)' }}>{stats.total_lost}</div>
            <div className="stat-label">Lost Items</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: 'var(--success)' }}>{stats.total_found}</div>
            <div className="stat-label">Found Items</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.open_items}</div>
            <div className="stat-label">Open</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: 'var(--warning)' }}>{stats.matched_items}</div>
            <div className="stat-label">Matched</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.recovery_rate}%</div>
            <div className="stat-label">Recovery Rate</div>
          </div>
        </div>
      )}

      <h2 style={{ marginBottom: 16 }}>Recent Items</h2>
      {recentItems.length === 0 ? (
        <div className="card">No items reported yet. Click "Report Item" to get started.</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Type</th>
                <th>Category</th>
                <th>Location</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {recentItems.map((item) => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>{item.title}</td>
                  <td><span className={`badge badge-${item.item_type}`}>{item.item_type}</span></td>
                  <td>{item.category}</td>
                  <td>{item.location}</td>
                  <td><span className={`badge badge-${item.status}`}>{item.status}</span></td>
                  <td><Link to={`/items/${item.id}`} className="btn btn-sm btn-primary">View</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
