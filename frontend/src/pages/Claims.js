/**
 * Claims management page -- list, create, edit, and delete claims.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React, { useEffect, useState } from 'react';
import { claimsApi } from '../services/api';
import ConfirmDialog from '../components/ConfirmDialog';

function Claims() {
  const [claims, setClaims] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [form, setForm] = useState({ item_id: '', claimant_id: '', description: '', evidence: '', status: 'pending' });
  const [error, setError] = useState('');
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => { loadClaims(); }, []);

  async function loadClaims() {
    try {
      const data = await claimsApi.getAll();
      setClaims(data);
    } catch (err) {
      setError('Failed to load claims');
    }
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      if (editId) {
        await claimsApi.update(editId, form);
      } else {
        await claimsApi.create({ ...form, item_id: parseInt(form.item_id), claimant_id: parseInt(form.claimant_id) });
      }
      setShowForm(false);
      setEditId(null);
      setForm({ item_id: '', claimant_id: '', description: '', evidence: '', status: 'pending' });
      loadClaims();
    } catch (err) {
      setError(err.message);
    }
  }

  function startEdit(claim) {
    setForm({
      item_id: claim.item_id,
      claimant_id: claim.claimant_id,
      description: claim.description,
      evidence: claim.evidence || '',
      status: claim.status,
    });
    setEditId(claim.id);
    setShowForm(true);
  }

  async function handleDelete() {
    try {
      await claimsApi.delete(deleteId);
      setDeleteId(null);
      loadClaims();
    } catch (err) {
      setError('Delete failed');
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Claims</h1>
        <button className="btn btn-primary" onClick={() => { setShowForm(!showForm); setEditId(null); setForm({ item_id: '', claimant_id: '', description: '', evidence: '', status: 'pending' }); }}>
          {showForm ? 'Cancel' : 'New Claim'}
        </button>
      </div>

      {error && <div className="card" style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

      {showForm && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h2 style={{ marginBottom: 16 }}>{editId ? 'Edit Claim' : 'Create Claim'}</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Item ID</label>
                <input name="item_id" type="number" value={form.item_id} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label>Claimant ID</label>
                <input name="claimant_id" type="number" value={form.claimant_id} onChange={handleChange} required />
              </div>
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea name="description" value={form.description} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Evidence</label>
              <textarea name="evidence" value={form.evidence} onChange={handleChange} />
            </div>
            {editId && (
              <div className="form-group">
                <label>Status</label>
                <select name="status" value={form.status} onChange={handleChange}>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                  <option value="withdrawn">Withdrawn</option>
                </select>
              </div>
            )}
            <button type="submit" className="btn btn-primary">{editId ? 'Update' : 'Create'}</button>
          </form>
        </div>
      )}

      {claims.length === 0 ? (
        <div className="card">No claims yet.</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Item ID</th>
                <th>Claimant ID</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {claims.map((c) => (
                <React.Fragment key={c.id}>
                  <tr>
                    <td>{c.id}</td>
                    <td>{c.item_id}</td>
                    <td>{c.claimant_id}</td>
                    <td><span className={`badge badge-${c.status}`}>{c.status}</span></td>
                    <td>{c.priority}</td>
                    <td>{c.date_claimed ? new Date(c.date_claimed).toLocaleDateString() : '-'}</td>
                    <td>
                      <button className="btn btn-sm" onClick={() => setExpandedId(expandedId === c.id ? null : c.id)} style={{ marginRight: 4, backgroundColor: 'var(--primary-light, #e3f2fd)', color: 'var(--primary, #1565c0)' }}>{expandedId === c.id ? 'Hide' : 'View'}</button>
                      <button className="btn btn-sm btn-primary" onClick={() => startEdit(c)} style={{ marginRight: 4 }}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => setDeleteId(c.id)}>Delete</button>
                    </td>
                  </tr>
                  {expandedId === c.id && (
                    <tr>
                      <td colSpan="7" style={{ backgroundColor: '#f8f9fa', padding: '16px 20px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                          <div>
                            <strong style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#888' }}>Description</strong>
                            <p style={{ margin: '4px 0 0', fontSize: '0.9rem' }}>{c.description || 'No description provided'}</p>
                          </div>
                          <div>
                            <strong style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#888' }}>Evidence</strong>
                            <p style={{ margin: '4px 0 0', fontSize: '0.9rem' }}>{c.evidence || 'No evidence provided'}</p>
                          </div>
                          <div>
                            <strong style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#888' }}>Status</strong>
                            <p style={{ margin: '4px 0 0' }}><span className={`badge badge-${c.status}`}>{c.status}</span></p>
                          </div>
                          <div>
                            <strong style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#888' }}>Date Resolved</strong>
                            <p style={{ margin: '4px 0 0', fontSize: '0.9rem' }}>{c.date_resolved ? new Date(c.date_resolved).toLocaleString() : 'Pending'}</p>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {deleteId && (
        <ConfirmDialog
          title="Delete Claim"
          message="Are you sure you want to delete this claim?"
          onConfirm={handleDelete}
          onCancel={() => setDeleteId(null)}
        />
      )}
    </div>
  );
}

export default Claims;
