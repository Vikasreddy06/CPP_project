/**
 * AWS Status page -- displays the connection status for all cloud services.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React, { useEffect, useState } from 'react';
import { awsApi } from '../services/api';

function AWSStatus() {
  const [services, setServices] = useState({});
  const [error, setError] = useState('');

  useEffect(() => { loadStatus(); }, []);

  async function loadStatus() {
    try {
      const data = await awsApi.getStatus();
      setServices(data.aws_services || {});
    } catch (err) {
      setError('Failed to load AWS status. Is the backend running?');
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>AWS Service Status</h1>
        <button className="btn btn-primary" onClick={loadStatus}>Refresh</button>
      </div>

      {error && <div className="card" style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

      <div className="service-grid">
        {Object.entries(services).map(([key, svc]) => (
          <div className="service-card" key={key}>
            <h3>{svc.service}</h3>
            <span className={`service-status ${svc.status === 'connected' ? 'status-connected' : 'status-mock'}`}>
              {svc.status}
            </span>
            <p style={{ marginTop: 12, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              {svc.description}
            </p>
            <div style={{ marginTop: 12, fontSize: '0.85rem' }}>
              {Object.entries(svc)
                .filter(([k]) => !['service', 'status', 'description'].includes(k))
                .map(([k, v]) => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--border)' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{k.replace(/_/g, ' ')}</span>
                    <span style={{ fontWeight: 500 }}>{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>

      {Object.keys(services).length === 0 && !error && (
        <div className="card">Loading service status...</div>
      )}
    </div>
  );
}

export default AWSStatus;
