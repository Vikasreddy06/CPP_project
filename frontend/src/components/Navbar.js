/**
 * Navigation bar with user info and logout.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();

  let user = null;
  try { user = JSON.parse(localStorage.getItem('clf_user') || 'null'); } catch {}

  const links = [
    { to: '/', label: 'Dashboard' },
    { to: '/lost-items', label: 'Lost' },
    { to: '/found-items', label: 'Found' },
    { to: '/report', label: 'Report' },
    { to: '/claims', label: 'Claims' },
    { to: '/matches', label: 'Matches' },
    { to: '/users', label: 'Users' },
    { to: '/aws-status', label: 'AWS' },
  ];

  function handleLogout() {
    localStorage.removeItem('clf_token');
    localStorage.removeItem('clf_user');
    navigate('/login');
    window.location.reload();
  }

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">Campus Lost &amp; Found</Link>
        <div className="navbar-links">
          {links.map((link) => (
            <Link key={link.to} to={link.to}
              className={location.pathname === link.to ? 'active' : ''}>
              {link.label}
            </Link>
          ))}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginLeft: 'auto' }}>
          {user && (
            <span style={{ fontSize: 12, color: '#a0a0b0' }}>
              {user.name} <span style={{ background: '#e94560', color: '#fff', padding: '2px 8px', borderRadius: 10, fontSize: 11, fontWeight: 600, marginLeft: 4 }}>{user.role}</span>
            </span>
          )}
          <button onClick={handleLogout}
            style={{ background: 'transparent', border: '1px solid #555', color: '#ccc', padding: '4px 12px', borderRadius: 6, fontSize: 12, cursor: 'pointer' }}>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
