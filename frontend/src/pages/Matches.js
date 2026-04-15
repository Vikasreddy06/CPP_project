/**
 * Matches management page -- auto-calculated confidence scoring.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React, { useEffect, useState } from 'react';
import { matchesApi, itemsApi } from '../services/api';
import ConfirmDialog from '../components/ConfirmDialog';

function Matches() {
  const [matches, setMatches] = useState([]);
  const [items, setItems] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [form, setForm] = useState({ lost_item_id: '', found_item_id: '', match_type: 'text', status: 'pending', notes: '' });
  const [error, setError] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadMatches();
    loadItems();
  }, []);

  async function loadMatches() {
    try { setMatches(await matchesApi.getAll()); }
    catch { setError('Failed to load matches'); }
  }

  async function loadItems() {
    try { setItems(await itemsApi.getAll()); }
    catch {}
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setCreating(true);
    setError('');
    try {
      const payload = {
        lost_item_id: parseInt(form.lost_item_id),
        found_item_id: parseInt(form.found_item_id),
        match_type: form.match_type,
        status: form.status,
        notes: form.notes,
      };
      if (editId) {
        payload.confidence_score = parseFloat(form.confidence_score);
        await matchesApi.update(editId, payload);
      } else {
        // Confidence is auto-calculated by the backend
        await matchesApi.create(payload);
      }
      setShowForm(false);
      setEditId(null);
      setForm({ lost_item_id: '', found_item_id: '', match_type: 'text', status: 'pending', notes: '' });
      loadMatches();
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
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

  async function handleConfirm(matchId) {
    try {
      await matchesApi.update(matchId, { status: 'confirmed' });
      loadMatches();
    } catch { setError('Failed to confirm match'); }
  }

  async function handleDelete() {
    try { await matchesApi.delete(deleteId); setDeleteId(null); loadMatches(); }
    catch { setError('Delete failed'); }
  }

  const lostItems = items.filter(i => i.item_type === 'lost');
  const foundItems = items.filter(i => i.item_type === 'found');

  function getItemLabel(id) {
    const item = items.find(i => i.id === id);
    return item ? `${item.title} (${item.category})` : `#${id}`;
  }

  function getScoreColor(score) {
    if (score >= 0.7) return '#16a34a';
    if (score >= 0.4) return '#d97706';
    return '#dc2626';
  }

  return (
    <div>
      <div className="page-header">
        <h1>Matches</h1>
        <button className="btn btn-primary" onClick={() => { setShowForm(!showForm); setEditId(null); setForm({ lost_item_id: '', found_item_id: '', match_type: 'text', status: 'pending', notes: '' }); }}>
          {showForm ? 'Cancel' : 'Find Match'}
        </button>
      </div>

      {error && <div className="card" style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

      {showForm && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h2 style={{ marginBottom: 4 }}>{editId ? 'Edit Match' : 'Match Lost ↔ Found Item'}</h2>
          {!editId && <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>Select a lost item and a found item. The system will automatically calculate the similarity score using text, category, and color matching.</p>}
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Lost Item</label>
                <select name="lost_item_id" value={form.lost_item_id} onChange={handleChange} required>
                  <option value="">-- Select lost item --</option>
                  {lostItems.map(i => (
                    <option key={i.id} value={i.id}>{i.title} — {i.category} ({i.color || 'no color'})</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Found Item</label>
                <select name="found_item_id" value={form.found_item_id} onChange={handleChange} required>
                  <option value="">-- Select found item --</option>
                  {foundItems.map(i => (
                    <option key={i.id} value={i.id}>{i.title} — {i.category} ({i.color || 'no color'})</option>
                  ))}
                </select>
              </div>
            </div>
            {editId && (
              <div className="form-row">
                <div className="form-group">
                  <label>Status</label>
                  <select name="status" value={form.status} onChange={handleChange}>
                    <option value="pending">Pending</option>
                    <option value="confirmed">Confirmed</option>
                    <option value="rejected">Rejected</option>
                  </select>
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
            )}
            <div className="form-group">
              <label>Notes (optional)</label>
              <textarea name="notes" value={form.notes} onChange={handleChange} placeholder="Any additional notes about this match..." />
            </div>
            <button type="submit" className="btn btn-primary" disabled={creating}>
              {creating ? 'Calculating...' : editId ? 'Update' : 'Calculate & Create Match'}
            </button>
          </form>
        </div>
      )}

      {matches.length === 0 ? (
        <div className="card">No matches detected yet. Click "Find Match" to compare a lost item with a found item.</div>
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
                  <td style={{ fontSize: 13 }}>{getItemLabel(m.lost_item_id)}</td>
                  <td style={{ fontSize: 13 }}>{getItemLabel(m.found_item_id)}</td>
                  <td>
                    <span style={{ fontWeight: 700, color: getScoreColor(m.confidence_score), fontSize: 15 }}>
                      {(m.confidence_score * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td>{m.match_type}</td>
                  <td><span className={`badge badge-${m.status}`}>{m.status}</span></td>
                  <td>
                    {m.status === 'pending' && (
                      <button className="btn btn-sm" onClick={() => handleConfirm(m.id)} style={{ marginRight: 4, background: '#16a34a', color: '#fff', border: 'none' }}>Confirm</button>
                    )}
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
