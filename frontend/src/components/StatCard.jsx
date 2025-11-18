import React from 'react';

const StatCard = ({ icon: Icon, title, value, subtitle, trend, color = 'primary' }) => {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600',
    success: 'bg-green-50 text-green-600',
    warning: 'bg-yellow-50 text-yellow-600',
    danger: 'bg-red-50 text-red-600',
    info: 'bg-blue-50 text-blue-600',
  };

  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className="mt-2">
              <span
                className={`text-sm font-medium ${
                  trend.direction === 'up'
                    ? trend.isPositive
                      ? 'text-green-600'
                      : 'text-red-600'
                    : trend.isPositive
                    ? 'text-red-600'
                    : 'text-green-600'
                }`}
              >
                {trend.direction === 'up' ? '↑' : '↓'} {trend.value}
              </span>
            </div>
          )}
        </div>
        {Icon && (
          <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
    </div>
  );
};

export default StatCard;
