import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Loader, X, ChevronDown, ChevronUp } from 'lucide-react';
import { PIPELINE_STEPS } from '../../utils/pipelineConfig';
import { formatDuration, extractMetric } from '../../utils/dataFormatter';
import CodeViewer from '../common/CodeViewer';

const TimelineStepper = ({ pipelineState, stepStatuses }) => {
  const [expandedStep, setExpandedStep] = useState(null);

  const getStepIcon = (stepId) => {
    const status = stepStatuses?.[stepId] || 'idle';
    
    if (status === 'success') {
      return <Check size={20} className="text-white" />;
    } else if (status === 'processing') {
      return <Loader size={20} className="text-white animate-spin" />;
    } else if (status === 'error') {
      return <X size={20} className="text-white" />;
    }
    return <div className="w-3 h-3 rounded-full bg-white" />;
  };

  const getStepColor = (stepId) => {
    const status = stepStatuses?.[stepId] || 'idle';
    
    if (status === 'success') return 'bg-success';
    if (status === 'processing') return 'bg-processing';
    if (status === 'error') return 'bg-error';
    return 'bg-idle';
  };

  const toggleStep = (stepId) => {
    setExpandedStep(expandedStep === stepId ? null : stepId);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="space-y-6">
        {PIPELINE_STEPS.map((step, index) => {
          const stepData = pipelineState?.steps?.[step.id];
          const status = stepStatuses?.[step.id] || 'idle';
          const isExpanded = expandedStep === step.id;
          const isLast = index === PIPELINE_STEPS.length - 1;

          return (
            <div key={step.id} className="relative">
              {/* Connecting Line */}
              {!isLast && (
                <div className="absolute left-6 top-14 w-0.5 h-12 bg-gray-300 dark:bg-gray-600" />
              )}

              {/* Step Card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card hover:shadow-lg transition-all duration-200"
              >
                <div 
                  className="flex items-start gap-4 cursor-pointer"
                  onClick={() => toggleStep(step.id)}
                >
                  {/* Step Number/Icon */}
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full ${getStepColor(step.id)} flex items-center justify-center shadow-md`}>
                    {getStepIcon(step.id)}
                  </div>

                  {/* Step Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {step.name}
                      </h3>
                      <div className="flex items-center gap-2">
                        {stepData && step.metrics?.[0] && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {formatDuration(extractMetric(stepData, step.metrics[0]))}
                          </span>
                        )}
                        {isExpanded ? (
                          <ChevronUp size={20} className="text-gray-400" />
                        ) : (
                          <ChevronDown size={20} className="text-gray-400" />
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {step.description}
                    </p>
                    {step.port && (
                      <div className="flex items-center gap-2">
                        <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded font-mono">
                          Port: {step.port}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded capitalize ${
                          status === 'success' ? 'bg-success bg-opacity-10 text-success' :
                          status === 'processing' ? 'bg-processing bg-opacity-10 text-processing' :
                          status === 'error' ? 'bg-error bg-opacity-10 text-error' :
                          'bg-idle bg-opacity-10 text-idle'
                        }`}>
                          {status}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Expanded Content */}
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="mt-4 pl-16 space-y-4"
                  >
                    {/* Features */}
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        Key Features
                      </h4>
                      <ul className="space-y-1">
                        {step.features.map((feature, i) => (
                          <li key={i} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                            <span className="text-success mt-0.5">•</span>
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Metrics */}
                    {stepData && step.metrics && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                          Metrics
                        </h4>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                          {step.metrics.map((metric, i) => {
                            const value = extractMetric(stepData, metric);
                            return (
                              <div key={i} className="bg-gray-50 dark:bg-gray-900 rounded p-2">
                                <div className="text-xs text-gray-500 dark:text-gray-400">
                                  {metric.replace(/_/g, ' ')}
                                </div>
                                <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {typeof value === 'number' && metric.includes('time')
                                    ? formatDuration(value)
                                    : String(value)}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Data */}
                    {stepData && (
                      <div>
                        <CodeViewer 
                          data={stepData}
                          title="Step Data"
                          maxHeight="200px"
                        />
                      </div>
                    )}
                  </motion.div>
                )}
              </motion.div>
            </div>
          );
        })}
      </div>

      {/* Progress Summary */}
      {pipelineState?.isRunning && (
        <div className="mt-6 card bg-processing bg-opacity-10">
          <div className="flex items-center gap-3">
            <Loader size={20} className="text-processing animate-spin" />
            <div>
              <div className="font-semibold text-gray-900 dark:text-gray-100">
                Pipeline Running
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Current step: {pipelineState.currentStep || 'Initializing...'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimelineStepper;

