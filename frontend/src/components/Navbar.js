/**
 * Navigation bar component with links to all major pages.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navbar() {
  const location = useLocation();

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

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">Campus Lost &amp; Found</Link>
        <div className="navbar-links">
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={location.pathname === link.to ? 'active' : ''}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
