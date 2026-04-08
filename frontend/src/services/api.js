/**
 * API service module -- handles all communication with the Flask backend.
 * Author: Vikas Reddy Amanagantti (x25178849)
 */

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5001';

/**
 * Generic fetch wrapper with error handling and JSON parsing.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const defaults = {
    headers: { 'Content-Type': 'application/json' },
  };
  const config = { ...defaults, ...options };

  const response = await fetch(url, config);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `Request failed with status ${response.status}`);
  }
  return data;
}

/* ------------------------------------------------------------------ */
/* Items                                                               */
/* ------------------------------------------------------------------ */

export const itemsApi = {
  getAll: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/api/items${qs ? '?' + qs : ''}`);
  },
  getById: (id) => request(`/api/items/${id}`),
  create: (data) => request('/api/items', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/api/items/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => request(`/api/items/${id}`, { method: 'DELETE' }),
  getStats: () => request('/api/items/stats'),
};

/* ------------------------------------------------------------------ */
/* Claims                                                              */
/* ------------------------------------------------------------------ */

export const claimsApi = {
  getAll: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/api/claims${qs ? '?' + qs : ''}`);
  },
  getById: (id) => request(`/api/claims/${id}`),
  create: (data) => request('/api/claims', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/api/claims/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => request(`/api/claims/${id}`, { method: 'DELETE' }),
};

/* ------------------------------------------------------------------ */
/* Users                                                               */
/* ------------------------------------------------------------------ */

export const usersApi = {
  getAll: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/api/users${qs ? '?' + qs : ''}`);
  },
  getById: (id) => request(`/api/users/${id}`),
  create: (data) => request('/api/users', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/api/users/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => request(`/api/users/${id}`, { method: 'DELETE' }),
};

/* ------------------------------------------------------------------ */
/* Matches                                                             */
/* ------------------------------------------------------------------ */

export const matchesApi = {
  getAll: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/api/matches${qs ? '?' + qs : ''}`);
  },
  getById: (id) => request(`/api/matches/${id}`),
  create: (data) => request('/api/matches', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/api/matches/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => request(`/api/matches/${id}`, { method: 'DELETE' }),
};

/* ------------------------------------------------------------------ */
/* AWS Services                                                        */
/* ------------------------------------------------------------------ */

export const awsApi = {
  getStatus: () => request('/api/aws/status'),
  uploadImage: (formData) =>
    fetch(`${API_BASE}/api/aws/upload-image`, { method: 'POST', body: formData })
      .then((r) => r.json()),
  analyseImage: (data) => request('/api/aws/analyse-image', { method: 'POST', body: JSON.stringify(data) }),
  triggerMatch: (data) => request('/api/aws/trigger-match', { method: 'POST', body: JSON.stringify(data) }),
  getNotifications: () => request('/api/aws/notifications'),
  getMetrics: () => request('/api/aws/metrics'),
  getLogs: () => request('/api/aws/logs'),
};
