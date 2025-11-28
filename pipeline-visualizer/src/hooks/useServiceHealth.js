/**
 * useServiceHealth Hook
 * Monitor health status of all services with polling
 */

import { useState, useEffect, useCallback } from 'react';
import { healthCheckService } from '../services/apiService';

export const useServiceHealth = (pollInterval = 5000) => {
  const [healthStatus, setHealthStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const checkHealth = useCallback(async () => {
    try {
      setError(null);
      const results = await healthCheckService.checkAllServices();
      setHealthStatus(results);
      setLastUpdated(new Date());
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }, []);

  const checkSingleService = useCallback(async (serviceKey) => {
    try {
      const result = await healthCheckService.checkService(serviceKey);
      setHealthStatus(prev => ({
        ...prev,
        [serviceKey]: result
      }));
      return result;
    } catch (err) {
      console.error(`Error checking ${serviceKey}:`, err);
      return { status: 'unhealthy', error: err.message };
    }
  }, []);

  const getHealthySummary = useCallback(() => {
    const services = Object.values(healthStatus);
    const healthy = services.filter(s => s.status === 'healthy').length;
    const total = services.length;
    return { healthy, total, percentage: total > 0 ? (healthy / total) * 100 : 0 };
  }, [healthStatus]);

  // Initial check
  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  // Polling
  useEffect(() => {
    if (!pollInterval) return;

    const interval = setInterval(() => {
      checkHealth();
    }, pollInterval);

    return () => clearInterval(interval);
  }, [pollInterval, checkHealth]);

  return {
    healthStatus,
    loading,
    error,
    lastUpdated,
    checkHealth,
    checkSingleService,
    getHealthySummary
  };
};

export default useServiceHealth;

