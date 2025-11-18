import React from 'react';
import { Link } from 'react-router-dom';
import { FiExternalLink, FiActivity } from 'react-icons/fi';
import StatusIndicator from './StatusIndicator';

const SiteCard = ({ site }) => {
  const getUptimeColor = (uptime) => {
    if (uptime >= 99) return 'text-green-600';
    if (uptime >= 95) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Link to={`/sites/${site.id}`}>
      <div className="card hover:shadow-lg transition-all duration-200 cursor-pointer">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-gray-900 truncate">{site.name}</h3>
              <StatusIndicator status={site.status} size="md" animated={site.status === 'down'} />
            </div>
            <a
              href={site.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1 truncate"
              onClick={(e) => e.stopPropagation()}
            >
              {site.url}
              <FiExternalLink className="flex-shrink-0" />
            </a>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">Uptime (30d)</p>
            <p className={`text-lg font-bold ${getUptimeColor(site.uptime_percentage || 0)}`}>
              {site.uptime_percentage?.toFixed(2) || '0.00'}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Response Time</p>
            <p className="text-lg font-bold text-gray-900">
              {site.avg_response_time ? `${site.avg_response_time.toFixed(0)}ms` : 'N/A'}
            </p>
          </div>
        </div>

        {site.last_check_at && (
          <div className="flex items-center gap-2 text-xs text-gray-500 border-t border-gray-100 pt-3">
            <FiActivity className="flex-shrink-0" />
            <span>Last checked: {new Date(site.last_check_at).toLocaleString()}</span>
          </div>
        )}

        {site.client_name && (
          <div className="mt-2">
            <span className="badge badge-info">{site.client_name}</span>
          </div>
        )}
      </div>
    </Link>
  );
};

export default SiteCard;
