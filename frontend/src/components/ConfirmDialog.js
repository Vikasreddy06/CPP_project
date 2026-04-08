/**
 * Reusable confirmation dialog component.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

import React from 'react';

function ConfirmDialog({ title, message, onConfirm, onCancel }) {
  return (
    <div className="dialog-overlay" onClick={onCancel}>
      <div className="dialog-box" onClick={(e) => e.stopPropagation()}>
        <h3>{title || 'Confirm Action'}</h3>
        <p>{message || 'Are you sure you want to proceed?'}</p>
        <div className="dialog-actions">
          <button className="btn btn-secondary" onClick={onCancel}>Cancel</button>
          <button className="btn btn-danger" onClick={onConfirm}>Confirm</button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;
