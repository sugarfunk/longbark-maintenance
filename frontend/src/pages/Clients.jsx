import React, { useState, useEffect } from 'react';
import { FiPlus, FiRefreshCw, FiExternalLink, FiEdit, FiTrash2, FiGlobe } from 'react-icons/fi';
import LoadingSpinner from '../components/LoadingSpinner';
import { clientsAPI } from '../services/api';

const Clients = () => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      setLoading(true);
      const response = await clientsAPI.getAll();
      setClients(response.data);
    } catch (err) {
      console.error('Error fetching clients:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Loading clients..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
          <p className="text-gray-600 mt-1">{clients.length} clients</p>
        </div>
        <div className="flex gap-3">
          <button onClick={fetchClients} className="btn-secondary flex items-center gap-2">
            <FiRefreshCw />
            Refresh
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <FiPlus />
            Add Client
          </button>
        </div>
      </div>

      {/* Clients Grid */}
      {clients.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No clients found. Add your first client to get started.</p>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary mt-4"
          >
            Add Client
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clients.map((client) => (
            <ClientCard key={client.id} client={client} onUpdate={fetchClients} />
          ))}
        </div>
      )}

      {/* Add Client Modal - Placeholder */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Add New Client</h2>
            <p className="text-gray-600 mb-4">
              Add client functionality coming soon. This will allow you to add new clients and link them to Invoice Ninja.
            </p>
            <button onClick={() => setShowAddModal(false)} className="btn-secondary w-full">
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const ClientCard = ({ client, onUpdate }) => {
  const [showSites, setShowSites] = useState(false);
  const [sites, setSites] = useState([]);
  const [loadingSites, setLoadingSites] = useState(false);

  const fetchClientSites = async () => {
    if (showSites) {
      setShowSites(false);
      return;
    }

    try {
      setLoadingSites(true);
      const response = await clientsAPI.getSites(client.id);
      setSites(response.data);
      setShowSites(true);
    } catch (err) {
      console.error('Error fetching client sites:', err);
    } finally {
      setLoadingSites(false);
    }
  };

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 mb-1">{client.name}</h3>
          {client.email && (
            <a
              href={`mailto:${client.email}`}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              {client.email}
            </a>
          )}
        </div>
        <div className="flex gap-2">
          <button
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
            title="Edit client"
          >
            <FiEdit />
          </button>
          <button
            className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded"
            title="Delete client"
          >
            <FiTrash2 />
          </button>
        </div>
      </div>

      {client.company && (
        <p className="text-sm text-gray-600 mb-2">
          <span className="font-medium">Company:</span> {client.company}
        </p>
      )}

      {client.phone && (
        <p className="text-sm text-gray-600 mb-2">
          <span className="font-medium">Phone:</span> {client.phone}
        </p>
      )}

      <div className="flex items-center justify-between pt-4 border-t border-gray-200 mt-4">
        <button
          onClick={fetchClientSites}
          className="btn-secondary text-sm flex items-center gap-2"
          disabled={loadingSites}
        >
          <FiGlobe />
          {loadingSites ? 'Loading...' : showSites ? 'Hide Sites' : 'View Sites'}
        </button>

        {client.invoice_ninja_id && (
          <a
            href={`${client.invoice_ninja_url || '#'}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
          >
            Invoice Ninja
            <FiExternalLink />
          </a>
        )}
      </div>

      {showSites && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-2">
            Sites ({sites.length})
          </p>
          {sites.length === 0 ? (
            <p className="text-sm text-gray-500">No sites found for this client</p>
          ) : (
            <ul className="space-y-2">
              {sites.map((site) => (
                <li key={site.id}>
                  <a
                    href={`/sites/${site.id}`}
                    className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-2"
                  >
                    {site.name}
                    <FiExternalLink className="w-3 h-3" />
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default Clients;
