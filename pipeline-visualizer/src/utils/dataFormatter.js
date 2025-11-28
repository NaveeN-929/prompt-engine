/**
 * Data Formatter Utilities
 * Helper functions to format and display data
 */

/**
 * Format timestamp to readable string
 */
export const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp);
  return date.toLocaleString();
};

/**
 * Format duration in milliseconds to readable string
 */
export const formatDuration = (ms) => {
  if (!ms || ms < 0) return 'N/A';
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
};

/**
 * Format quality score to percentage
 */
export const formatQualityScore = (score) => {
  if (typeof score !== 'number') return 'N/A';
  return `${(score * 100).toFixed(1)}%`;
};

/**
 * Get quality level from score
 */
export const getQualityLevel = (score) => {
  if (score >= 0.95) return { level: 'exemplary', label: 'Exemplary', color: 'success' };
  if (score >= 0.80) return { level: 'high_quality', label: 'High Quality', color: 'success' };
  if (score >= 0.65) return { level: 'acceptable', label: 'Acceptable', color: 'warning' };
  return { level: 'poor', label: 'Poor', color: 'error' };
};

/**
 * Format large numbers with commas
 */
export const formatNumber = (num) => {
  if (typeof num !== 'number') return 'N/A';
  return num.toLocaleString();
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Format JSON for display
 */
export const formatJSON = (data, indent = 2) => {
  if (!data) return '';
  try {
    return JSON.stringify(data, null, indent);
  } catch (error) {
    return String(data);
  }
};

/**
 * Get status color class
 */
export const getStatusColor = (status) => {
  const statusMap = {
    healthy: 'success',
    unhealthy: 'error',
    success: 'success',
    processing: 'processing',
    error: 'error',
    idle: 'idle',
    warning: 'warning'
  };
  return statusMap[status] || 'idle';
};

/**
 * Get status icon
 */
export const getStatusIcon = (status) => {
  const iconMap = {
    healthy: 'CheckCircle',
    unhealthy: 'XCircle',
    success: 'CheckCircle',
    processing: 'Loader',
    error: 'XCircle',
    idle: 'Circle',
    warning: 'AlertTriangle'
  };
  return iconMap[status] || 'Circle';
};

/**
 * Extract metric value safely
 */
export const extractMetric = (data, path, defaultValue = 'N/A') => {
  if (!data) return defaultValue;
  
  const keys = path.split('.');
  let value = data;
  
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key];
    } else {
      return defaultValue;
    }
  }
  
  return value !== null && value !== undefined ? value : defaultValue;
};

/**
 * Calculate percentage
 */
export const calculatePercentage = (value, total) => {
  if (!total || total === 0) return 0;
  return Math.round((value / total) * 100);
};

/**
 * Format bytes to human-readable size
 */
export const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
};

/**
 * Generate unique ID
 */
export const generateId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Deep clone object
 */
export const deepClone = (obj) => {
  try {
    return JSON.parse(JSON.stringify(obj));
  } catch {
    return obj;
  }
};

export default {
  formatTimestamp,
  formatDuration,
  formatQualityScore,
  getQualityLevel,
  formatNumber,
  truncateText,
  formatJSON,
  getStatusColor,
  getStatusIcon,
  extractMetric,
  calculatePercentage,
  formatBytes,
  generateId,
  deepClone
};

