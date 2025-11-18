import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  getCurrentUser: () => api.get('/auth/me'),
};

// Sites APIs
export const sitesAPI = {
  getAll: (params) => api.get('/sites', { params }),
  getById: (id) => api.get(`/sites/${id}`),
  create: (data) => api.post('/sites', data),
  update: (id, data) => api.put(`/sites/${id}`, data),
  delete: (id) => api.delete(`/sites/${id}`),
  getStatus: (id) => api.get(`/sites/${id}/status`),
  getUptimeHistory: (id, params) => api.get(`/sites/${id}/uptime`, { params }),
  getPerformanceMetrics: (id, params) => api.get(`/sites/${id}/performance`, { params }),
  getSEOMetrics: (id) => api.get(`/sites/${id}/seo`),
};

// Alerts APIs
export const alertsAPI = {
  getAll: (params) => api.get('/alerts', { params }),
  getById: (id) => api.get(`/alerts/${id}`),
  acknowledge: (id) => api.post(`/alerts/${id}/acknowledge`),
  resolve: (id) => api.post(`/alerts/${id}/resolve`),
  getStats: () => api.get('/alerts/stats'),
};

// Clients APIs
export const clientsAPI = {
  getAll: (params) => api.get('/clients', { params }),
  getById: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post('/clients', data),
  update: (id, data) => api.put(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`),
  getSites: (id) => api.get(`/clients/${id}/sites`),
};

// Dashboard APIs
export const dashboardAPI = {
  getOverview: () => api.get('/dashboard/overview'),
  getRecentAlerts: (limit = 5) => api.get('/dashboard/recent-alerts', { params: { limit } }),
  getSitesStatus: () => api.get('/dashboard/sites-status'),
};

// Monitoring APIs
export const monitoringAPI = {
  triggerCheck: (siteId) => api.post(`/monitoring/check/${siteId}`),
  getCheckHistory: (siteId, params) => api.get(`/monitoring/history/${siteId}`, { params }),
};

export default api;
