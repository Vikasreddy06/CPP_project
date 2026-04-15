/**
 * Navigation bar with role-based links, user info, and logout.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const isAdmin = user?.role === 'admin';

  // Students see: Dashboard, Lost, Found, Report, Claims
  // Admins see everything including Matches, Users, AWS
  const links = [
    { to: '/', label: 'Dashboard' },
    { to: '/lost-items', label: 'Lost' },
    { to: '/found-items', label: 'Found' },
    { to: '/report', label: 'Report' },
    { to: '/claims', label: 'Claims' },
    ...(isAdmin ? [
      { to: '/matches', label: 'Matches' },
      { to: '/users', label: 'Users' },
      { to: '/aws-status', label: 'AWS' },
    ] : []),
  ];

  function handleLogout() {
    logout();
    navigate('/login');
  }

  const roleBadgeColor = isAdmin ? '#e94560' : '#3b82f6';

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
              {user.name} <span style={{ background: roleBadgeColor, color: '#fff', padding: '2px 8px', borderRadius: 10, fontSize: 11, fontWeight: 600, marginLeft: 4 }}>{user.role}</span>
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
