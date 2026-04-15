/**
 * Report item page -- form for creating a new lost or found item.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { itemsApi, awsApi } from '../services/api';

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
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analysing, setAnalysing] = useState(false);
  const [detectedLabels, setDetectedLabels] = useState([]);

  async function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      setError('Image must be under 5 MB');
      return;
    }
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));

    // Run Rekognition analysis on the uploaded image
    try {
      setAnalysing(true);
      setDetectedLabels([]);
      const fd = new FormData();
      fd.append('file', file);
      const analysis = await awsApi.analyseImageFile(fd);
      if (analysis && !analysis.error) {
        setDetectedLabels(analysis.labels || []);
        if (analysis.estimated_category) {
          setForm((prev) => ({ ...prev, category: analysis.estimated_category }));
        }
        if (analysis.dominant_color && analysis.dominant_color !== 'unknown') {
          const color = analysis.dominant_color.charAt(0).toUpperCase() + analysis.dominant_color.slice(1);
          setForm((prev) => ({ ...prev, color }));
        }
      }
    } catch (err) {
      console.error('Image analysis failed:', err);
    } finally {
      setAnalysing(false);
    }
  }

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
      let imageUrl = form.image_url;
      // Upload image file to S3 if selected
      if (imageFile) {
        setUploading(true);
        const fd = new FormData();
        fd.append('file', imageFile);
        const uploadRes = await awsApi.uploadImage(fd);
        imageUrl = uploadRes.image_url || '';
        setUploading(false);
      }
      const created = await itemsApi.create({ ...form, image_url: imageUrl });
      navigate(`/items/${created.id}`);
    } catch (err) {
      setUploading(false);
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
              <label>Upload Photo</label>
              <input type="file" accept="image/*" onChange={handleFileChange}
                style={{ padding: '6px 0' }} />
              {imagePreview && (
                <img src={imagePreview} alt="Preview" style={{ maxWidth: 200, borderRadius: 8, marginTop: 8 }} />
              )}
              {analysing && <p style={{ fontSize: '0.85rem', color: 'var(--primary)' }}>Analysing image with Rekognition...</p>}
              {detectedLabels.length > 0 && (
                <div style={{ marginTop: 8, padding: '8px 12px', background: '#f0f7ff', borderRadius: 8, fontSize: '0.85rem' }}>
                  <strong>Rekognition detected:</strong>{' '}
                  {detectedLabels.map((l, i) => (
                    <span key={i} style={{ display: 'inline-block', background: '#e0edff', borderRadius: 4, padding: '2px 8px', margin: '2px 4px', fontSize: '0.8rem' }}>
                      {l.Name} ({l.Confidence.toFixed(1)}%)
                    </span>
                  ))}
                </div>
              )}
              {uploading && <p style={{ fontSize: '0.85rem', color: 'var(--primary)' }}>Uploading to S3...</p>}
            </div>
          </div>

          <button type="submit" className="btn btn-primary" disabled={submitting}
            style={{ marginTop: 8 }}>
            {uploading ? 'Uploading image...' : submitting ? 'Submitting...' : 'Submit Report'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ReportItem;
