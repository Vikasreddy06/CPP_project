/**
 * Lost Items listing page with search and filter.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { itemsApi } from '../services/api';
import ConfirmDialog from '../components/ConfirmDialog';

function LostItems() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState('');
  const [deleteId, setDeleteId] = useState(null);

  useEffect(() => { loadItems(); }, []);

  async function loadItems() {
    try {
      const data = await itemsApi.getAll({ type: 'lost' });
      setItems(data);
    } catch (err) {
      console.error('Failed to load lost items:', err);
    }
  }

  async function handleDelete() {
    try {
      await itemsApi.delete(deleteId);
      setDeleteId(null);
      loadItems();
    } catch (err) {
      console.error('Delete failed:', err);
    }
  }

  const filtered = items.filter(
    (item) =>
      item.title.toLowerCase().includes(search.toLowerCase()) ||
      item.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="page-header">
        <h1>Lost Items</h1>
        <Link to="/report/lost" className="btn btn-primary">Report Lost Item</Link>
      </div>

      <div className="form-group" style={{ maxWidth: 400, marginBottom: 20 }}>
        <input
          type="text"
          placeholder="Search lost items..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {filtered.length === 0 ? (
        <div className="card">No lost items found.</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Category</th>
                <th>Color</th>
                <th>Location</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>{item.title}</td>
                  <td>{item.category}</td>
                  <td>{item.color || '-'}</td>
                  <td>{item.location}</td>
                  <td><span className={`badge badge-${item.status}`}>{item.status}</span></td>
                  <td>{item.date_reported ? new Date(item.date_reported).toLocaleDateString() : '-'}</td>
                  <td>
                    <Link to={`/items/${item.id}`} className="btn btn-sm btn-primary" style={{ marginRight: 4 }}>View</Link>
                    <button className="btn btn-sm btn-danger" onClick={() => setDeleteId(item.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {deleteId && (
        <ConfirmDialog
          title="Delete Item"
          message="Are you sure you want to delete this lost item?"
          onConfirm={handleDelete}
          onCancel={() => setDeleteId(null)}
        />
      )}
    </div>
  );
}

export default LostItems;
