import React, { useState, useEffect } from 'react';
import { FiPlus, FiSearch, FiRefreshCw } from 'react-icons/fi';
import SiteCard from '../components/SiteCard';
import LoadingSpinner from '../components/LoadingSpinner';
import StatusIndicator from '../components/StatusIndicator';
import { sitesAPI, clientsAPI } from '../services/api';

const Sites = () => {
  const [sites, setSites] = useState([]);
  const [filteredSites, setFilteredSites] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [clientFilter, setClientFilter] = useState('all');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'table'
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    filterSites();
  }, [sites, searchTerm, statusFilter, clientFilter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sitesRes, clientsRes] = await Promise.all([
        sitesAPI.getAll(),
        clientsAPI.getAll(),
      ]);
      setSites(sitesRes.data);
      setClients(clientsRes.data);
    } catch (err) {
      console.error('Error fetching sites:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterSites = () => {
    let filtered = [...sites];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (site) =>
          site.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          site.url.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((site) => site.status === statusFilter);
    }

    // Client filter
    if (clientFilter !== 'all') {
      filtered = filtered.filter((site) => site.client_id === parseInt(clientFilter));
    }

    setFilteredSites(filtered);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Loading sites..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sites</h1>
          <p className="text-gray-600 mt-1">
            {filteredSites.length} of {sites.length} sites
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={fetchData}
            className="btn-secondary flex items-center gap-2"
          >
            <FiRefreshCw />
            Refresh
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <FiPlus />
            Add Site
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <label htmlFor="search" className="label">
              Search
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FiSearch className="text-gray-400" />
              </div>
              <input
                id="search"
                type="text"
                className="input pl-10"
                placeholder="Search by name or URL..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

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
              <option value="up">Online</option>
              <option value="warning">Warning</option>
              <option value="down">Offline</option>
            </select>
          </div>

          {/* Client Filter */}
          <div>
            <label htmlFor="client" className="label">
              Client
            </label>
            <select
              id="client"
              className="input"
              value={clientFilter}
              onChange={(e) => setClientFilter(e.target.value)}
            >
              <option value="all">All Clients</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Sites Grid/Table */}
      {filteredSites.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">
            {searchTerm || statusFilter !== 'all' || clientFilter !== 'all'
              ? 'No sites match your filters'
              : 'No sites found. Add your first site to get started.'}
          </p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSites.map((site) => (
            <SiteCard key={site.id} site={site} />
          ))}
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Site
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Client
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Uptime
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Response Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredSites.map((site) => (
                <tr
                  key={site.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => (window.location.href = `/sites/${site.id}`)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusIndicator status={site.status} size="md" showLabel />
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium text-gray-900">{site.name}</p>
                      <p className="text-sm text-gray-500">{site.url}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="badge badge-info">{site.client_name || 'N/A'}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-medium text-gray-900">
                      {site.uptime_percentage?.toFixed(2) || '0.00'}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-medium text-gray-900">
                      {site.avg_response_time ? `${site.avg_response_time.toFixed(0)}ms` : 'N/A'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add Site Modal - Placeholder */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Add New Site</h2>
            <p className="text-gray-600 mb-4">
              Add site functionality coming soon. This will allow you to add new sites to monitor.
            </p>
            <button
              onClick={() => setShowAddModal(false)}
              className="btn-secondary w-full"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sites;
