import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiGlobe, FiAlertCircle, FiActivity, FiArrowRight } from 'react-icons/fi';
import StatCard from '../components/StatCard';
import AlertCard from '../components/AlertCard';
import StatusIndicator from '../components/StatusIndicator';
import LoadingSpinner from '../components/LoadingSpinner';
import { dashboardAPI, alertsAPI } from '../services/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [sitesStatus, setSitesStatus] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [overviewRes, alertsRes, statusRes] = await Promise.all([
        dashboardAPI.getOverview(),
        dashboardAPI.getRecentAlerts(5),
        dashboardAPI.getSitesStatus(),
      ]);

      setOverview(overviewRes.data);
      setRecentAlerts(alertsRes.data);
      setSitesStatus(statusRes.data);
      setError('');
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (alertId) => {
    try {
      await alertsAPI.acknowledge(alertId);
      fetchDashboardData();
    } catch (err) {
      console.error('Error acknowledging alert:', err);
    }
  };

  const handleResolve = async (alertId) => {
    try {
      await alertsAPI.resolve(alertId);
      fetchDashboardData();
    } catch (err) {
      console.error('Error resolving alert:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
          <button onClick={fetchDashboardData} className="btn-primary mt-4">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of your hosting infrastructure</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={FiGlobe}
          title="Total Sites"
          value={overview?.total_sites || 0}
          color="primary"
        />
        <StatCard
          icon={FiAlertCircle}
          title="Active Alerts"
          value={overview?.active_alerts || 0}
          color={overview?.active_alerts > 0 ? 'danger' : 'success'}
        />
        <StatCard
          icon={FiActivity}
          title="Average Uptime"
          value={`${overview?.avg_uptime?.toFixed(2) || 0}%`}
          color={overview?.avg_uptime >= 99 ? 'success' : overview?.avg_uptime >= 95 ? 'warning' : 'danger'}
        />
        <StatCard
          icon={FiActivity}
          title="Avg Response Time"
          value={overview?.avg_response_time ? `${overview.avg_response_time.toFixed(0)}ms` : 'N/A'}
          color="info"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sites Status */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Sites Status</h2>
              <Link
                to="/sites"
                className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center gap-1"
              >
                View All
                <FiArrowRight />
              </Link>
            </div>

            <div className="space-y-3">
              {sitesStatus.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No sites found</p>
              ) : (
                sitesStatus.map((site) => (
                  <Link
                    key={site.id}
                    to={`/sites/${site.id}`}
                    className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors duration-200"
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <StatusIndicator status={site.status} size="md" />
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-gray-900 truncate">{site.name}</p>
                        <p className="text-sm text-gray-500 truncate">{site.url}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 flex-shrink-0">
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          {site.uptime_percentage?.toFixed(2) || '0.00'}%
                        </p>
                        <p className="text-xs text-gray-500">Uptime</p>
                      </div>
                      <FiArrowRight className="text-gray-400" />
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Status Summary */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Status Summary</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <StatusIndicator status="up" size="md" />
                <span className="text-sm font-medium text-gray-700">Online</span>
              </div>
              <span className="text-lg font-bold text-gray-900">
                {sitesStatus.filter(s => s.status === 'up').length}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <StatusIndicator status="warning" size="md" />
                <span className="text-sm font-medium text-gray-700">Warning</span>
              </div>
              <span className="text-lg font-bold text-gray-900">
                {sitesStatus.filter(s => s.status === 'warning').length}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <StatusIndicator status="down" size="md" />
                <span className="text-sm font-medium text-gray-700">Offline</span>
              </div>
              <span className="text-lg font-bold text-gray-900">
                {sitesStatus.filter(s => s.status === 'down').length}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="mt-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Recent Alerts</h2>
            <Link
              to="/alerts"
              className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center gap-1"
            >
              View All
              <FiArrowRight />
            </Link>
          </div>

          <div className="space-y-3">
            {recentAlerts.length === 0 ? (
              <div className="text-center py-8">
                <FiAlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                <p className="text-gray-500">No recent alerts</p>
              </div>
            ) : (
              recentAlerts.map((alert) => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onAcknowledge={handleAcknowledge}
                  onResolve={handleResolve}
                  compact
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
