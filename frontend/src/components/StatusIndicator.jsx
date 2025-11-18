import React from 'react';

const StatusIndicator = ({ status, size = 'md', showLabel = false, animated = false }) => {
  const statusConfig = {
    up: {
      color: 'bg-status-up',
      label: 'Online',
      textColor: 'text-green-700',
    },
    down: {
      color: 'bg-status-down',
      label: 'Offline',
      textColor: 'text-red-700',
    },
    warning: {
      color: 'bg-status-warning',
      label: 'Warning',
      textColor: 'text-yellow-700',
    },
    unknown: {
      color: 'bg-status-unknown',
      label: 'Unknown',
      textColor: 'text-gray-700',
    },
  };

  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  };

  const config = statusConfig[status] || statusConfig.unknown;

  return (
    <div className="flex items-center gap-2">
      <span
        className={`${sizeClasses[size]} ${config.color} rounded-full ${
          animated ? 'animate-pulse' : ''
        }`}
      ></span>
      {showLabel && (
        <span className={`text-sm font-medium ${config.textColor}`}>
          {config.label}
        </span>
      )}
    </div>
  );
};

export default StatusIndicator;
