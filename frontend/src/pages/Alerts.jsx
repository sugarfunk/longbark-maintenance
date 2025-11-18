import React, { useState, useEffect } from 'react';
import { FiRefreshCw, FiFilter } from 'react-icons/fi';
import AlertCard from '../components/AlertCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { alertsAPI } from '../services/api';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [filteredAlerts, setFilteredAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  useEffect(() => {
    fetchAlerts();
  }, []);

  useEffect(() => {
    filterAlerts();
  }, [alerts, statusFilter, severityFilter, typeFilter]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await alertsAPI.getAll();
      setAlerts(response.data);
    } catch (err) {
      console.error('Error fetching alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterAlerts = () => {
    let filtered = [...alerts];

    if (statusFilter !== 'all') {
      filtered = filtered.filter((alert) => alert.status === statusFilter);
    }

    if (severityFilter !== 'all') {
      filtered = filtered.filter((alert) => alert.severity === severityFilter);
    }

    if (typeFilter !== 'all') {
      filtered = filtered.filter((alert) => alert.alert_type === typeFilter);
    }

    setFilteredAlerts(filtered);
  };

  const handleAcknowledge = async (alertId) => {
    try {
      await alertsAPI.acknowledge(alertId);
      fetchAlerts();
    } catch (err) {
      console.error('Error acknowledging alert:', err);
    }
  };

  const handleResolve = async (alertId) => {
    try {
      await alertsAPI.resolve(alertId);
      fetchAlerts();
    } catch (err) {
      console.error('Error resolving alert:', err);
    }
  };

  const handleAcknowledgeAll = async () => {
    try {
      const activeUnacknowledged = filteredAlerts.filter(
        (a) => a.status === 'active' && !a.acknowledged_at
      );
      await Promise.all(activeUnacknowledged.map((a) => alertsAPI.acknowledge(a.id)));
      fetchAlerts();
    } catch (err) {
      console.error('Error acknowledging all alerts:', err);
    }
  };

  const handleResolveAll = async () => {
    try {
      const activeAlerts = filteredAlerts.filter((a) => a.status === 'active');
      await Promise.all(activeAlerts.map((a) => alertsAPI.resolve(a.id)));
      fetchAlerts();
    } catch (err) {
      console.error('Error resolving all alerts:', err);
    }
  };

  const getAlertStats = () => {
    return {
      total: alerts.length,
      active: alerts.filter((a) => a.status === 'active').length,
      acknowledged: alerts.filter((a) => a.acknowledged_at).length,
      resolved: alerts.filter((a) => a.status === 'resolved').length,
      critical: alerts.filter((a) => a.severity === 'critical').length,
      warning: alerts.filter((a) => a.severity === 'warning').length,
      info: alerts.filter((a) => a.severity === 'info').length,
    };
  };

  const stats = getAlertStats();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Loading alerts..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="text-gray-600 mt-1">
            {filteredAlerts.length} of {alerts.length} alerts
          </p>
        </div>
        <div className="flex gap-3">
          <button onClick={fetchAlerts} className="btn-secondary flex items-center gap-2">
            <FiRefreshCw />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
        <div className="card">
          <p className="text-sm text-gray-500">Total</p>
          <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Active</p>
          <p className="text-2xl font-bold text-orange-600">{stats.active}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Acknowledged</p>
          <p className="text-2xl font-bold text-blue-600">{stats.acknowledged}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Resolved</p>
          <p className="text-2xl font-bold text-green-600">{stats.resolved}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Critical</p>
          <p className="text-2xl font-bold text-red-600">{stats.critical}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Warning</p>
          <p className="text-2xl font-bold text-yellow-600">{stats.warning}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Info</p>
          <p className="text-2xl font-bold text-blue-600">{stats.info}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex items-center gap-2 mb-4">
          <FiFilter className="text-gray-500" />
          <h2 className="font-semibold text-gray-900">Filters</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          {/* Status Filter */}
          <div>
            <label htmlFor="status" className="label">
              Status
            </label>
            <select
              id="status"
              className="input"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          {/* Severity Filter */}
          <div>
            <label htmlFor="severity" className="label">
              Severity
            </label>
            <select
              id="severity"
              className="input"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
            </select>
          </div>

          {/* Type Filter */}
          <div>
            <label htmlFor="type" className="label">
              Type
            </label>
            <select
              id="type"
              className="input"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="uptime">Uptime</option>
              <option value="performance">Performance</option>
              <option value="ssl">SSL</option>
              <option value="seo">SEO</option>
            </select>
          </div>
        </div>

        {/* Bulk Actions */}
        {filteredAlerts.filter((a) => a.status === 'active').length > 0 && (
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              onClick={handleAcknowledgeAll}
              className="btn-secondary text-sm"
              disabled={
                filteredAlerts.filter((a) => a.status === 'active' && !a.acknowledged_at)
                  .length === 0
              }
            >
              Acknowledge All ({filteredAlerts.filter((a) => a.status === 'active' && !a.acknowledged_at).length})
            </button>
            <button
              onClick={handleResolveAll}
              className="btn-primary text-sm"
            >
              Resolve All ({filteredAlerts.filter((a) => a.status === 'active').length})
            </button>
          </div>
        )}
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500">
              {alerts.length === 0
                ? 'No alerts found'
                : 'No alerts match your filters'}
            </p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onAcknowledge={handleAcknowledge}
              onResolve={handleResolve}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default Alerts;
