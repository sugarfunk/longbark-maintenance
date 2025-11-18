import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FiArrowLeft, FiExternalLink, FiActivity, FiAlertCircle } from 'react-icons/fi';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import StatusIndicator from '../components/StatusIndicator';
import StatCard from '../components/StatCard';
import AlertCard from '../components/AlertCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { sitesAPI, alertsAPI } from '../services/api';

const SiteDetail = () => {
  const { id } = useParams();
  const [site, setSite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [uptimeData, setUptimeData] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  const [seoMetrics, setSeoMetrics] = useState(null);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetchSiteData();
  }, [id]);

  useEffect(() => {
    if (activeTab === 'uptime') fetchUptimeData();
    if (activeTab === 'performance') fetchPerformanceData();
    if (activeTab === 'seo') fetchSEOData();
    if (activeTab === 'alerts') fetchAlerts();
  }, [activeTab]);

  const fetchSiteData = async () => {
    try {
      setLoading(true);
      const response = await sitesAPI.getById(id);
      setSite(response.data);
    } catch (err) {
      console.error('Error fetching site:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUptimeData = async () => {
    try {
      const response = await sitesAPI.getUptimeHistory(id, { days: 30 });
      setUptimeData(response.data);
    } catch (err) {
      console.error('Error fetching uptime data:', err);
    }
  };

  const fetchPerformanceData = async () => {
    try {
      const response = await sitesAPI.getPerformanceMetrics(id, { days: 7 });
      setPerformanceData(response.data);
    } catch (err) {
      console.error('Error fetching performance data:', err);
    }
  };

  const fetchSEOData = async () => {
    try {
      const response = await sitesAPI.getSEOMetrics(id);
      setSeoMetrics(response.data);
    } catch (err) {
      console.error('Error fetching SEO data:', err);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await alertsAPI.getAll({ site_id: id });
      setAlerts(response.data);
    } catch (err) {
      console.error('Error fetching alerts:', err);
    }
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

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'uptime', label: 'Uptime' },
    { id: 'performance', label: 'Performance' },
    { id: 'seo', label: 'SEO' },
    { id: 'alerts', label: 'Alerts' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Loading site details..." />
      </div>
    );
  }

  if (!site) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card text-center py-12">
          <p className="text-gray-500">Site not found</p>
          <Link to="/sites" className="btn-primary mt-4 inline-block">
            Back to Sites
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Button */}
      <Link
        to="/sites"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <FiArrowLeft />
        Back to Sites
      </Link>

      {/* Site Header */}
      <div className="card mb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">{site.name}</h1>
              <StatusIndicator status={site.status} size="lg" showLabel />
            </div>
            <a
              href={site.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-700 flex items-center gap-2"
            >
              {site.url}
              <FiExternalLink />
            </a>
            {site.client_name && (
              <p className="text-gray-600 mt-2">
                Client: <span className="font-medium">{site.client_name}</span>
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatCard
          icon={FiActivity}
          title="Uptime (30d)"
          value={`${site.uptime_percentage?.toFixed(2) || 0}%`}
          color={site.uptime_percentage >= 99 ? 'success' : site.uptime_percentage >= 95 ? 'warning' : 'danger'}
        />
        <StatCard
          icon={FiActivity}
          title="Avg Response Time"
          value={site.avg_response_time ? `${site.avg_response_time.toFixed(0)}ms` : 'N/A'}
          color="info"
        />
        <StatCard
          icon={FiAlertCircle}
          title="Active Alerts"
          value={site.active_alerts || 0}
          color={site.active_alerts > 0 ? 'danger' : 'success'}
        />
        <StatCard
          icon={FiActivity}
          title="Last Check"
          value={site.last_check_at ? format(new Date(site.last_check_at), 'MMM d, h:mm a') : 'Never'}
          color="primary"
        />
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 border-b-2 font-medium transition-colors duration-200 ${
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Site Information</h2>
              <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">URL</dt>
                  <dd className="text-sm text-gray-900 mt-1">{site.url}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Status</dt>
                  <dd className="mt-1">
                    <StatusIndicator status={site.status} showLabel />
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Check Interval</dt>
                  <dd className="text-sm text-gray-900 mt-1">{site.check_interval || 300}s</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Created</dt>
                  <dd className="text-sm text-gray-900 mt-1">
                    {site.created_at ? format(new Date(site.created_at), 'MMM d, yyyy') : 'N/A'}
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        )}

        {activeTab === 'uptime' && (
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Uptime History (30 Days)</h2>
            {uptimeData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={uptimeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(value) => format(new Date(value), 'MMM d')}
                  />
                  <YAxis domain={[0, 100]} />
                  <Tooltip
                    labelFormatter={(value) => format(new Date(value), 'MMM d, yyyy')}
                    formatter={(value) => [`${value.toFixed(2)}%`, 'Uptime']}
                  />
                  <Area
                    type="monotone"
                    dataKey="uptime"
                    stroke="#22c55e"
                    fill="#86efac"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8">No uptime data available</p>
            )}
          </div>
        )}

        {activeTab === 'performance' && (
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Performance Metrics (7 Days)</h2>
            {performanceData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={(value) => format(new Date(value), 'MMM d')}
                  />
                  <YAxis />
                  <Tooltip
                    labelFormatter={(value) => format(new Date(value), 'MMM d, h:mm a')}
                    formatter={(value) => [`${value.toFixed(0)}ms`, 'Response Time']}
                  />
                  <Line
                    type="monotone"
                    dataKey="response_time"
                    stroke="#3b82f6"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8">No performance data available</p>
            )}
          </div>
        )}

        {activeTab === 'seo' && (
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">SEO Metrics</h2>
            {seoMetrics ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Page Load Time</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {seoMetrics.page_load_time || 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Mobile Friendly</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {seoMetrics.mobile_friendly ? 'Yes' : 'No'}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">SSL Certificate</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {seoMetrics.ssl_valid ? 'Valid' : 'Invalid'}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No SEO data available</p>
            )}
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="space-y-4">
            {alerts.length > 0 ? (
              alerts.map((alert) => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onAcknowledge={handleAcknowledge}
                  onResolve={handleResolve}
                />
              ))
            ) : (
              <div className="card text-center py-12">
                <FiAlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                <p className="text-gray-500">No alerts for this site</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SiteDetail;
