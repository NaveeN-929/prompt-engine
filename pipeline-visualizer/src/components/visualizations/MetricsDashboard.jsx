import React, { useState, useEffect } from 'react';
import { 
  Activity, Database, Shield, Brain, CheckCircle, 
  AlertCircle, Clock, TrendingUp 
} from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import MetricCard from '../common/MetricCard';
import StatusIndicator from '../common/StatusIndicator';
import { SERVICES } from '../../utils/pipelineConfig';
import { formatDuration } from '../../utils/dataFormatter';

const MetricsDashboard = ({ healthStatus, pipelineState }) => {
  const [performanceData, setPerformanceData] = useState([]);

  // Generate mock performance data over time
  useEffect(() => {
    const generateData = () => {
      const now = Date.now();
      return Array.from({ length: 10 }, (_, i) => ({
        time: new Date(now - (9 - i) * 60000).toLocaleTimeString(),
        responseTime: Math.random() * 5000 + 1000,
        successRate: Math.random() * 20 + 80,
        requests: Math.floor(Math.random() * 50 + 10),
      }));
    };

    setPerformanceData(generateData());
    const interval = setInterval(() => {
      setPerformanceData(prev => {
        const newData = [...prev.slice(1)];
        const now = Date.now();
        newData.push({
          time: new Date(now).toLocaleTimeString(),
          responseTime: Math.random() * 5000 + 1000,
          successRate: Math.random() * 20 + 80,
          requests: Math.floor(Math.random() * 50 + 10),
        });
        return newData;
      });
    }, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  // Calculate service health summary
  const serviceHealth = Object.entries(healthStatus || {}).map(([key, data]) => ({
    name: data.name,
    status: data.status,
  }));

  const healthyCount = serviceHealth.filter(s => s.status === 'healthy').length;
  const unhealthyCount = serviceHealth.filter(s => s.status === 'unhealthy').length;

  const healthPieData = [
    { name: 'Healthy', value: healthyCount, color: '#10B981' },
    { name: 'Unhealthy', value: unhealthyCount, color: '#EF4444' },
  ];

  // Calculate pipeline metrics
  const completedSteps = Object.values(pipelineState?.steps || {}).filter(
    step => step.status === 'success'
  ).length;

  const totalTime = pipelineState?.endTime && pipelineState?.startTime
    ? pipelineState.endTime - pipelineState.startTime
    : 0;

  return (
    <div className="p-6 space-y-6">
      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Services Healthy"
          value={`${healthyCount}/${serviceHealth.length}`}
          icon={Activity}
          color="success"
          trend={healthyCount === serviceHealth.length ? 'up' : 'down'}
          trendValue={`${Math.round((healthyCount / serviceHealth.length) * 100)}%`}
        />
        <MetricCard
          title="Pipeline Steps"
          value={`${completedSteps}/${Object.keys(PIPELINE_STEPS).length || 8}`}
          icon={CheckCircle}
          color="processing"
          subtitle={pipelineState?.isRunning ? 'Running...' : 'Idle'}
        />
        <MetricCard
          title="Total Processing Time"
          value={formatDuration(totalTime)}
          icon={Clock}
          color="warning"
          subtitle="Last execution"
        />
        <MetricCard
          title="System Status"
          value={healthyCount === serviceHealth.length ? 'Operational' : 'Degraded'}
          icon={healthyCount === serviceHealth.length ? CheckCircle : AlertCircle}
          color={healthyCount === serviceHealth.length ? 'success' : 'error'}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Response Time Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Response Time Trend
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="time" 
                stroke="#9CA3AF"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#9CA3AF"
                style={{ fontSize: '12px' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: 'none',
                  borderRadius: '8px',
                  color: '#F3F4F6'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="responseTime" 
                stroke="#3B82F6" 
                strokeWidth={2}
                name="Response Time (ms)"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Service Health Pie Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Service Health Distribution
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={healthPieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {healthPieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Success Rate Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Success Rate
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="time" 
                stroke="#9CA3AF"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#9CA3AF"
                style={{ fontSize: '12px' }}
                domain={[0, 100]}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: 'none',
                  borderRadius: '8px',
                  color: '#F3F4F6'
                }}
              />
              <Legend />
              <Bar 
                dataKey="successRate" 
                fill="#10B981" 
                name="Success Rate (%)"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Request Volume Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Request Volume
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="time" 
                stroke="#9CA3AF"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#9CA3AF"
                style={{ fontSize: '12px' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: 'none',
                  borderRadius: '8px',
                  color: '#F3F4F6'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="requests" 
                stroke="#F59E0B" 
                strokeWidth={2}
                name="Requests"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Service Status Cards */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Service Status
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {serviceHealth.map((service, index) => (
            <div 
              key={index}
              className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {service.name}
                </span>
                <StatusIndicator status={service.status} showLabel={false} size="sm" />
              </div>
              <div className={`text-xs capitalize font-medium ${
                service.status === 'healthy' ? 'text-success' : 'text-error'
              }`}>
                {service.status}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MetricsDashboard;

