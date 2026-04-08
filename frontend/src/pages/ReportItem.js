/**
 * Report item page -- form for creating a new lost or found item.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { itemsApi } from '../services/api';

function ReportItem() {
  const navigate = useNavigate();
  const { type } = useParams();

  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'electronics',
    color: '',
    location: '',
    item_type: type || 'lost',
    contact_info: '',
    image_url: '',
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    if (!form.title || !form.description || !form.location) {
      setError('Please fill in all required fields.');
      setSubmitting(false);
      return;
    }

    try {
      const created = await itemsApi.create(form);
      navigate(`/items/${created.id}`);
    } catch (err) {
      setError(err.message || 'Failed to create item');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Report {form.item_type === 'found' ? 'Found' : 'Lost'} Item</h1>
      </div>

      {error && <div className="card" style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Item Type *</label>
              <select name="item_type" value={form.item_type} onChange={handleChange}>
                <option value="lost">Lost</option>
                <option value="found">Found</option>
              </select>
            </div>
            <div className="form-group">
              <label>Category *</label>
              <select name="category" value={form.category} onChange={handleChange}>
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
            <label>Title *</label>
            <input name="title" value={form.title} onChange={handleChange}
              placeholder="e.g. Black iPhone 15 Pro" />
          </div>

          <div className="form-group">
            <label>Description *</label>
            <textarea name="description" value={form.description} onChange={handleChange}
              placeholder="Describe the item in detail -- brand, distinguishing marks, contents..." />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Color</label>
              <input name="color" value={form.color} onChange={handleChange}
                placeholder="e.g. Black, Silver" />
            </div>
            <div className="form-group">
              <label>Location *</label>
              <input name="location" value={form.location} onChange={handleChange}
                placeholder="e.g. Library Building A" />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Contact Info</label>
              <input name="contact_info" value={form.contact_info} onChange={handleChange}
                placeholder="e.g. email or phone" />
            </div>
            <div className="form-group">
              <label>Image URL</label>
              <input name="image_url" value={form.image_url} onChange={handleChange}
                placeholder="http://..." />
            </div>
          </div>

          <button type="submit" className="btn btn-primary" disabled={submitting}
            style={{ marginTop: 8 }}>
            {submitting ? 'Submitting...' : 'Submit Report'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ReportItem;
