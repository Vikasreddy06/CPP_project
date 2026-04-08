/**
 * Users management page -- list, create, edit, and delete users.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React, { useEffect, useState } from 'react';
import { usersApi } from '../services/api';
import ConfirmDialog from '../components/ConfirmDialog';

function Users() {
  const [users, setUsers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [form, setForm] = useState({ name: '', email: '', student_id: '', phone: '', role: 'student' });
  const [error, setError] = useState('');

  useEffect(() => { loadUsers(); }, []);

  async function loadUsers() {
    try {
      const data = await usersApi.getAll();
      setUsers(data);
    } catch (err) {
      setError('Failed to load users');
    }
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      if (editId) {
        await usersApi.update(editId, form);
      } else {
        await usersApi.create(form);
      }
      setShowForm(false);
      setEditId(null);
      setForm({ name: '', email: '', student_id: '', phone: '', role: 'student' });
      loadUsers();
    } catch (err) {
      setError(err.message);
    }
  }

  function startEdit(user) {
    setForm({
      name: user.name,
      email: user.email,
      student_id: user.student_id,
      phone: user.phone || '',
      role: user.role,
    });
    setEditId(user.id);
    setShowForm(true);
  }

  async function handleDelete() {
    try {
      await usersApi.delete(deleteId);
      setDeleteId(null);
      loadUsers();
    } catch (err) {
      setError('Delete failed');
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Users</h1>
        <button className="btn btn-primary" onClick={() => { setShowForm(!showForm); setEditId(null); setForm({ name: '', email: '', student_id: '', phone: '', role: 'student' }); }}>
          {showForm ? 'Cancel' : 'Add User'}
        </button>
      </div>

      {error && <div className="card" style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

      {showForm && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h2 style={{ marginBottom: 16 }}>{editId ? 'Edit User' : 'Add User'}</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Name</label>
                <input name="name" value={form.name} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input name="email" type="email" value={form.email} onChange={handleChange} required />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Student ID</label>
                <input name="student_id" value={form.student_id} onChange={handleChange} required={!editId} disabled={!!editId} />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input name="phone" value={form.phone} onChange={handleChange} />
              </div>
            </div>
            <div className="form-group" style={{ maxWidth: 200 }}>
              <label>Role</label>
              <select name="role" value={form.role} onChange={handleChange}>
                <option value="student">Student</option>
                <option value="staff">Staff</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary">{editId ? 'Update' : 'Create'}</button>
          </form>
        </div>
      )}

      {users.length === 0 ? (
        <div className="card">No users registered.</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Student ID</th>
                <th>Role</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td>{u.name}</td>
                  <td>{u.email}</td>
                  <td>{u.student_id}</td>
                  <td>{u.role}</td>
                  <td>
                    <button className="btn btn-sm btn-primary" onClick={() => startEdit(u)} style={{ marginRight: 4 }}>Edit</button>
                    <button className="btn btn-sm btn-danger" onClick={() => setDeleteId(u.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {deleteId && (
        <ConfirmDialog
          title="Delete User"
          message="Are you sure you want to delete this user?"
          onConfirm={handleDelete}
          onCancel={() => setDeleteId(null)}
        />
      )}
    </div>
  );
}

export default Users;
