/**
 * Matches management page -- list, create, edit, and delete matches.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React, { useEffect, useState } from 'react';
import { matchesApi } from '../services/api';
import ConfirmDialog from '../components/ConfirmDialog';

function Matches() {
  const [matches, setMatches] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [form, setForm] = useState({
    lost_item_id: '', found_item_id: '', confidence_score: '', match_type: 'text', status: 'pending', notes: '',
  });
  const [error, setError] = useState('');

  useEffect(() => { loadMatches(); }, []);

  async function loadMatches() {
    try {
      const data = await matchesApi.getAll();
      setMatches(data);
    } catch (err) {
      setError('Failed to load matches');
    }
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const payload = {
        ...form,
        lost_item_id: parseInt(form.lost_item_id),
        found_item_id: parseInt(form.found_item_id),
        confidence_score: parseFloat(form.confidence_score),
      };
      if (editId) {
        await matchesApi.update(editId, payload);
      } else {
        await matchesApi.create(payload);
      }
      setShowForm(false);
      setEditId(null);
      setForm({ lost_item_id: '', found_item_id: '', confidence_score: '', match_type: 'text', status: 'pending', notes: '' });
      loadMatches();
    } catch (err) {
      setError(err.message);
    }
  }

  function startEdit(m) {
    setForm({
      lost_item_id: m.lost_item_id,
      found_item_id: m.found_item_id,
      confidence_score: m.confidence_score,
      match_type: m.match_type,
      status: m.status,
      notes: m.notes || '',
    });
    setEditId(m.id);
    setShowForm(true);
  }

  async function handleDelete() {
    try {
      await matchesApi.delete(deleteId);
      setDeleteId(null);
      loadMatches();
    } catch (err) {
      setError('Delete failed');
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Matches</h1>
        <button className="btn btn-primary" onClick={() => { setShowForm(!showForm); setEditId(null); }}>
          {showForm ? 'Cancel' : 'New Match'}
        </button>
      </div>

      {error && <div className="card" style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

      {showForm && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h2 style={{ marginBottom: 16 }}>{editId ? 'Edit Match' : 'Create Match'}</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Lost Item ID</label>
                <input name="lost_item_id" type="number" value={form.lost_item_id} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label>Found Item ID</label>
                <input name="found_item_id" type="number" value={form.found_item_id} onChange={handleChange} required />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Confidence Score (0-1)</label>
                <input name="confidence_score" type="number" step="0.01" min="0" max="1" value={form.confidence_score} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label>Match Type</label>
                <select name="match_type" value={form.match_type} onChange={handleChange}>
                  <option value="text">Text</option>
                  <option value="image">Image</option>
                  <option value="combined">Combined</option>
                </select>
              </div>
            </div>
            {editId && (
              <div className="form-group">
                <label>Status</label>
                <select name="status" value={form.status} onChange={handleChange}>
                  <option value="pending">Pending</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
            )}
            <div className="form-group">
              <label>Notes</label>
              <textarea name="notes" value={form.notes} onChange={handleChange} />
            </div>
            <button type="submit" className="btn btn-primary">{editId ? 'Update' : 'Create'}</button>
          </form>
        </div>
      )}

      {matches.length === 0 ? (
        <div className="card">No matches detected yet.</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Lost Item</th>
                <th>Found Item</th>
                <th>Confidence</th>
                <th>Type</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {matches.map((m) => (
                <tr key={m.id}>
                  <td>{m.id}</td>
                  <td>{m.lost_item_id}</td>
                  <td>{m.found_item_id}</td>
                  <td>{(m.confidence_score * 100).toFixed(0)}%</td>
                  <td>{m.match_type}</td>
                  <td><span className={`badge badge-${m.status}`}>{m.status}</span></td>
                  <td>
                    <button className="btn btn-sm btn-primary" onClick={() => startEdit(m)} style={{ marginRight: 4 }}>Edit</button>
                    <button className="btn btn-sm btn-danger" onClick={() => setDeleteId(m.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {deleteId && (
        <ConfirmDialog
          title="Delete Match"
          message="Are you sure you want to delete this match?"
          onConfirm={handleDelete}
          onCancel={() => setDeleteId(null)}
        />
      )}
    </div>
  );
}

export default Matches;
