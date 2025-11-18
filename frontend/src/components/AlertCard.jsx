import React from 'react';
import { FiAlertCircle, FiAlertTriangle, FiInfo, FiCheckCircle } from 'react-icons/fi';
import { format } from 'date-fns';

const AlertCard = ({ alert, onAcknowledge, onResolve, compact = false }) => {
  const severityConfig = {
    critical: {
      icon: FiAlertCircle,
      color: 'border-red-500 bg-red-50',
      iconColor: 'text-red-600',
      badge: 'badge-danger',
    },
    warning: {
      icon: FiAlertTriangle,
      color: 'border-yellow-500 bg-yellow-50',
      iconColor: 'text-yellow-600',
      badge: 'badge-warning',
    },
    info: {
      icon: FiInfo,
      color: 'border-blue-500 bg-blue-50',
      iconColor: 'text-blue-600',
      badge: 'badge-info',
    },
  };

  const config = severityConfig[alert.severity] || severityConfig.info;
  const Icon = config.icon;

  if (compact) {
    return (
      <div className={`border-l-4 ${config.color} p-3 rounded`}>
        <div className="flex items-start gap-3">
          <Icon className={`${config.iconColor} flex-shrink-0 mt-0.5`} />
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <p className="font-medium text-gray-900 text-sm">{alert.message}</p>
              <span className={`badge ${config.badge} flex-shrink-0`}>
                {alert.severity}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {format(new Date(alert.created_at), 'MMM d, yyyy h:mm a')}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`card border-l-4 ${config.color}`}>
      <div className="flex items-start gap-4">
        <Icon className={`${config.iconColor} text-2xl flex-shrink-0`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4 mb-2">
            <div>
              <h3 className="font-semibold text-gray-900">{alert.message}</h3>
              <p className="text-sm text-gray-600 mt-1">
                Site: <span className="font-medium">{alert.site_name || 'Unknown'}</span>
              </p>
            </div>
            <span className={`badge ${config.badge}`}>{alert.severity}</span>
          </div>

          {alert.details && (
            <p className="text-sm text-gray-600 mb-3">{alert.details}</p>
          )}

          <div className="flex items-center justify-between">
            <div className="text-xs text-gray-500">
              <p>Created: {format(new Date(alert.created_at), 'MMM d, yyyy h:mm a')}</p>
              {alert.acknowledged_at && (
                <p>Acknowledged: {format(new Date(alert.acknowledged_at), 'MMM d, yyyy h:mm a')}</p>
              )}
            </div>

            {alert.status === 'active' && (
              <div className="flex gap-2">
                {!alert.acknowledged_at && onAcknowledge && (
                  <button
                    onClick={() => onAcknowledge(alert.id)}
                    className="btn-secondary text-sm px-3 py-1"
                  >
                    Acknowledge
                  </button>
                )}
                {onResolve && (
                  <button
                    onClick={() => onResolve(alert.id)}
                    className="btn-primary text-sm px-3 py-1"
                  >
                    Resolve
                  </button>
                )}
              </div>
            )}

            {alert.status === 'resolved' && (
              <div className="flex items-center gap-2 text-green-600">
                <FiCheckCircle />
                <span className="text-sm font-medium">Resolved</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertCard;
