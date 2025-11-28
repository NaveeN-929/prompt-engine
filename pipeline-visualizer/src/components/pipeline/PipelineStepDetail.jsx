import React from 'react';
import { 
  Database, Shield, FileText, Brain, Sparkles, 
  CheckCircle, GitBranch, Unlock, ExternalLink 
} from 'lucide-react';
import StatusIndicator from '../common/StatusIndicator';
import CodeViewer from '../common/CodeViewer';
import { formatDuration, extractMetric } from '../../utils/dataFormatter';

const iconMap = {
  Database, Shield, FileText, Brain, Sparkles,
  CheckCircle, GitBranch, Unlock
};

const PipelineStepDetail = ({ step, stepData, status, onClose }) => {
  const Icon = iconMap[step.icon] || Database;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div 
          className="p-6 border-b border-gray-200 dark:border-gray-700"
          style={{ backgroundColor: `${step.color}15` }}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div 
                className="p-3 rounded-lg"
                style={{ backgroundColor: `${step.color}30` }}
              >
                <Icon size={32} style={{ color: step.color }} />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {step.name}
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  {step.description}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 text-2xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Status */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Status
            </h3>
            <StatusIndicator status={status} label={status} />
          </div>

          {/* Service Info */}
          {step.endpoint && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Service Information
              </h3>
              <div className="card bg-gray-50 dark:bg-gray-900">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Endpoint:</span>
                    <a 
                      href={step.endpoint}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-processing hover:underline flex items-center gap-1"
                    >
                      {step.endpoint}
                      <ExternalLink size={14} />
                    </a>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Port:</span>
                    <span className="font-mono text-gray-900 dark:text-gray-100">
                      {step.port}
                    </span>
                  </div>
                  {step.apiPath && (
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">API Path:</span>
                      <span className="font-mono text-gray-900 dark:text-gray-100">
                        {step.apiPath}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Features */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Key Features
            </h3>
            <ul className="space-y-2">
              {step.features.map((feature, index) => (
                <li 
                  key={index}
                  className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300"
                >
                  <CheckCircle size={16} className="text-success mt-0.5 flex-shrink-0" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Metrics */}
          {stepData && step.metrics && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Metrics
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {step.metrics.map((metric, index) => {
                  const value = extractMetric(stepData, metric);
                  return (
                    <div 
                      key={index}
                      className="card bg-gray-50 dark:bg-gray-900"
                    >
                      <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                        {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </div>
                      <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                        {typeof value === 'number' && metric.includes('time') 
                          ? formatDuration(value)
                          : String(value)
                        }
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Sample/Actual Data */}
          {(stepData || step.sampleData) && (
            <div className="mb-6">
              <CodeViewer 
                data={stepData || step.sampleData}
                title={stepData ? "Actual Data" : "Sample Data"}
                maxHeight="300px"
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <button
            onClick={onClose}
            className="btn-primary w-full"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default PipelineStepDetail;

