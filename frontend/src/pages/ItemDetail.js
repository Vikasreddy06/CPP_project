/**
 * Item detail page -- view and edit a single item.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { itemsApi } from '../services/api';

function ItemDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [item, setItem] = useState(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const [error, setError] = useState('');

  useEffect(() => { loadItem(); }, [id]);

  async function loadItem() {
    try {
      const data = await itemsApi.getById(id);
      setItem(data);
      setForm(data);
    } catch (err) {
      setError('Item not found');
    }
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSave() {
    try {
      const updated = await itemsApi.update(id, form);
      setItem(updated);
      setEditing(false);
    } catch (err) {
      setError('Failed to update item');
    }
  }

  async function handleDelete() {
    try {
      await itemsApi.delete(id);
      navigate('/');
    } catch (err) {
      setError('Failed to delete item');
    }
  }

  if (error && !item) {
    return <div className="card" style={{ marginTop: 24 }}>{error}</div>;
  }
  if (!item) return <p>Loading...</p>;

  return (
    <div>
      <div className="page-header">
        <h1>{item.title}</h1>
        <div>
          {!editing && (
            <>
              <button className="btn btn-primary" onClick={() => setEditing(true)} style={{ marginRight: 8 }}>Edit</button>
              <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
            </>
          )}
        </div>
      </div>

      {error && <div className="card" style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

      {editing ? (
        <div className="card">
          <div className="form-row">
            <div className="form-group">
              <label>Title</label>
              <input name="title" value={form.title || ''} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Category</label>
              <select name="category" value={form.category || ''} onChange={handleChange}>
                <option value="electronics">Electronics</option>
                <option value="clothing">Clothing</option>
                <option value="accessories">Accessories</option>
                <option value="books">Books</option>
                <option value="keys">Keys</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea name="description" value={form.description || ''} onChange={handleChange} />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Color</label>
              <input name="color" value={form.color || ''} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Location</label>
              <input name="location" value={form.location || ''} onChange={handleChange} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Status</label>
              <select name="status" value={form.status || 'open'} onChange={handleChange}>
                <option value="open">Open</option>
                <option value="matched">Matched</option>
                <option value="claimed">Claimed</option>
                <option value="closed">Closed</option>
              </select>
            </div>
            <div className="form-group">
              <label>Contact Info</label>
              <input name="contact_info" value={form.contact_info || ''} onChange={handleChange} />
            </div>
          </div>
          <div style={{ marginTop: 16 }}>
            <button className="btn btn-primary" onClick={handleSave} style={{ marginRight: 8 }}>Save</button>
            <button className="btn btn-secondary" onClick={() => { setEditing(false); setForm(item); }}>Cancel</button>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="detail-grid">
            <div className="detail-field">
              <label>Type</label>
              <p><span className={`badge badge-${item.item_type}`}>{item.item_type}</span></p>
            </div>
            <div className="detail-field">
              <label>Status</label>
              <p><span className={`badge badge-${item.status}`}>{item.status}</span></p>
            </div>
            <div className="detail-field">
              <label>Category</label>
              <p>{item.category}</p>
            </div>
            <div className="detail-field">
              <label>Color</label>
              <p>{item.color || 'Not specified'}</p>
            </div>
            <div className="detail-field">
              <label>Location</label>
              <p>{item.location}</p>
            </div>
            <div className="detail-field">
              <label>Contact</label>
              <p>{item.contact_info || 'Not provided'}</p>
            </div>
            <div className="detail-field">
              <label>Date Reported</label>
              <p>{item.date_reported ? new Date(item.date_reported).toLocaleString() : '-'}</p>
            </div>
            <div className="detail-field">
              <label>Date Resolved</label>
              <p>{item.date_resolved ? new Date(item.date_resolved).toLocaleString() : 'Unresolved'}</p>
            </div>
          </div>
          <div style={{ marginTop: 16 }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Description</label>
            <p style={{ marginTop: 4 }}>{item.description}</p>
          </div>
          {item.image_url && (
            <div style={{ marginTop: 16 }}>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Image</label>
              <p style={{ marginTop: 4 }}><img src={item.image_url} alt={item.title} style={{ maxWidth: 300, borderRadius: 8 }} /></p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ItemDetail;
