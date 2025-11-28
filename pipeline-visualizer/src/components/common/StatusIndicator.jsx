import React from 'react';
import { CheckCircle, XCircle, Loader, Circle, AlertTriangle } from 'lucide-react';
import { getStatusColor } from '../../utils/dataFormatter';

const StatusIndicator = ({ status, label, size = 'md', showLabel = true }) => {
  const iconSize = size === 'sm' ? 16 : size === 'lg' ? 24 : 20;
  
  const getIcon = () => {
    switch (status) {
      case 'healthy':
      case 'success':
        return <CheckCircle size={iconSize} className="text-success" />;
      case 'unhealthy':
      case 'error':
        return <XCircle size={iconSize} className="text-error" />;
      case 'processing':
        return <Loader size={iconSize} className="text-processing animate-spin" />;
      case 'warning':
        return <AlertTriangle size={iconSize} className="text-warning" />;
      default:
        return <Circle size={iconSize} className="text-idle" />;
    }
  };

  const colorClass = getStatusColor(status);
  const dotClass = `status-indicator status-${colorClass}`;

  return (
    <div className="flex items-center gap-2">
      {getIcon()}
      {showLabel && (
        <span className={`text-${colorClass} font-medium capitalize`}>
          {label || status}
        </span>
      )}
    </div>
  );
};

export default StatusIndicator;

