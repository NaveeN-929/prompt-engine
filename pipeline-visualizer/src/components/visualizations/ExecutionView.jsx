import React, { useState } from 'react';
import { Play, RotateCcw, Download, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import TimelineStepper from './TimelineStepper';
import CodeViewer from '../common/CodeViewer';
import OutputDisplay from '../common/OutputDisplay';
import { formatDuration } from '../../utils/dataFormatter';

const ExecutionView = ({ pipelineState, onExecute, onReset, stepStatuses }) => {
  const [inputData, setInputData] = useState(JSON.stringify({
    customer_id: 'BIZ_0001',
    name: 'Tech Solutions Inc',
    email: 'info@techsolutions.com',
    phone: '555-234-5678',
    transactions: [
      {
        date: '2025-01-15',
        amount: 50000.00,
        type: 'credit',
        description: 'Customer payment received'
      },
      {
        date: '2025-01-16',
        amount: -5000.00,
        type: 'debit',
        description: 'Payroll'
      }
    ],
    account_info: {
      account_number: '1234-5678-9012',
      routing_number: '021000021',
      bank_name: 'First National Bank',
      account_type: 'business_checking'
    },
    account_balance: 150000.00
  }, null, 2));

  const [inputError, setInputError] = useState(null);

  const handleExecute = () => {
    try {
      const data = JSON.parse(inputData);
      setInputError(null);
      onExecute(data);
    } catch (error) {
      setInputError('Invalid JSON format');
    }
  };

  const handleDownloadResults = () => {
    const results = {
      pipelineState,
      executionTime: pipelineState?.endTime - pipelineState?.startTime,
      timestamp: new Date().toISOString(),
    };
    
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pipeline-results-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Get output data from pipeline results
  const outputData = pipelineState?.steps?.['output-data'];
  const validationResult = pipelineState?.steps?.['validation-system'];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Input & Controls */}
        <div className="lg:col-span-1 space-y-4">
          {/* Controls */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Pipeline Controls
            </h3>
            
            <div className="space-y-3">
              <button
                onClick={handleExecute}
                disabled={pipelineState?.isRunning}
                className={`btn-primary w-full flex items-center justify-center gap-2 ${
                  pipelineState?.isRunning ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                <Play size={18} />
                {pipelineState?.isRunning ? 'Running...' : 'Execute Pipeline'}
              </button>

              <button
                onClick={onReset}
                disabled={pipelineState?.isRunning}
                className={`btn-secondary w-full flex items-center justify-center gap-2 ${
                  pipelineState?.isRunning ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                <RotateCcw size={18} />
                Reset
              </button>

              {pipelineState?.results && (
                <button
                  onClick={handleDownloadResults}
                  className="btn-secondary w-full flex items-center justify-center gap-2"
                >
                  <Download size={18} />
                  Download Results
                </button>
              )}
            </div>
          </div>

          {/* Execution Summary */}
          {(pipelineState?.results || pipelineState?.isRunning) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Execution Summary
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Status:</span>
                  <span className={`text-sm font-medium ${
                    pipelineState?.isRunning ? 'text-processing' :
                    pipelineState?.results?.success ? 'text-success' : 'text-error'
                  }`}>
                    {pipelineState?.isRunning ? 'Running' :
                     pipelineState?.results?.success ? 'Success' : 'Failed'}
                  </span>
                </div>
                
                {pipelineState?.startTime && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Started:</span>
                    <span className="text-sm text-gray-900 dark:text-gray-100">
                      {new Date(pipelineState.startTime).toLocaleTimeString()}
                    </span>
                  </div>
                )}

                {pipelineState?.endTime && (
                  <>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Completed:</span>
                      <span className="text-sm text-gray-900 dark:text-gray-100">
                        {new Date(pipelineState.endTime).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Duration:</span>
                      <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                        {formatDuration(pipelineState.endTime - pipelineState.startTime)}
                      </span>
                    </div>
                  </>
                )}

                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Steps Completed:</span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                    {Object.keys(pipelineState?.steps || {}).length}/9
                  </span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Input Data Editor */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Input Data
            </h3>
            {inputError && (
              <div className="mb-3 p-3 bg-error bg-opacity-10 border border-error rounded-lg flex items-start gap-2">
                <AlertCircle size={18} className="text-error mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-error">Error</div>
                  <div className="text-xs text-error">{inputError}</div>
                </div>
              </div>
            )}
            <textarea
              value={inputData}
              onChange={(e) => setInputData(e.target.value)}
              className="w-full h-64 p-3 bg-gray-900 dark:bg-black text-gray-100 font-mono text-sm rounded-lg border border-gray-700 focus:border-processing focus:outline-none"
              placeholder="Enter JSON input data..."
              disabled={pipelineState?.isRunning}
            />
          </div>
        </div>

        {/* Right Column - Timeline & Output */}
        <div className="lg:col-span-2 space-y-6">
          {/* Output Display - Show prominently if available */}
          {(outputData || validationResult) && (
            <OutputDisplay 
              outputData={outputData}
              validationResult={validationResult}
            />
          )}

          {/* Timeline Stepper */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Pipeline Execution
            </h3>
            <TimelineStepper 
              pipelineState={pipelineState}
              stepStatuses={stepStatuses}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExecutionView;
