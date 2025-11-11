import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const MetricCard = ({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  trendValue,
  color = 'processing',
  subtitle
}) => {
  const getTrendIcon = () => {
    if (!trend) return <Minus size={16} className="text-idle" />;
    if (trend === 'up') return <TrendingUp size={16} className="text-success" />;
    return <TrendingDown size={16} className="text-error" />;
  };

  return (
    <div className="card hover:shadow-lg transition-shadow duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            {value}
          </p>
          {subtitle && (
            <p className="text-xs text-gray-500 dark:text-gray-500">{subtitle}</p>
          )}
          {(trend || trendValue) && (
            <div className="flex items-center gap-1 mt-2">
              {getTrendIcon()}
              {trendValue && (
                <span className={`text-xs font-medium ${
                  trend === 'up' ? 'text-success' : trend === 'down' ? 'text-error' : 'text-idle'
                }`}>
                  {trendValue}
                </span>
              )}
            </div>
          )}
        </div>
        {Icon && (
          <div className={`p-3 rounded-lg bg-${color} bg-opacity-10`}>
            <Icon size={24} className={`text-${color}`} />
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard;

