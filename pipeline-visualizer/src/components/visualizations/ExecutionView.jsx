import React, { useState } from 'react';
import { Play, RotateCcw, Download, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import TimelineStepper from './TimelineStepper';
import CodeViewer from '../common/CodeViewer';
import OutputDisplay from '../common/OutputDisplay';
import { formatDuration } from '../../utils/dataFormatter';
import dataset0001 from '../../assets/dataset_0001.json';
import { generateDataset } from '../../utils/dataGenerator';

const DYNAMIC_DATA_PROFILES = [
  { label: 'Balanced growth', value: 'balanced' },
  { label: 'Negative pressure', value: 'negative' },
  { label: 'Neutral stability', value: 'neutral' }
];

const ExecutionView = ({ pipelineState, onExecute, onReset, stepStatuses }) => {
  const [inputData, setInputData] = useState(() => JSON.stringify(dataset0001, null, 2));

  const [inputError, setInputError] = useState(null);
  const [dynamicProfile, setDynamicProfile] = useState(DYNAMIC_DATA_PROFILES[0].value);
  const [dynamicLoading, setDynamicLoading] = useState(false);
  const [dynamicCount, setDynamicCount] = useState(800);
  const [activeGeneratorLabel, setActiveGeneratorLabel] = useState('Default dataset');

  const handleGenerateDynamicDataset = () => {
    if (dynamicLoading || pipelineState?.isRunning) {
      return;
    }

    setDynamicLoading(true);
    setInputError(null);

    try {
      const dataset = generateDataset(dynamicProfile, dynamicCount);
      setInputData(JSON.stringify(dataset, null, 2));
      const profileLabel =
        DYNAMIC_DATA_PROFILES.find((profile) => profile.value === dynamicProfile)?.label ??
        'Dynamic dataset';
      setActiveGeneratorLabel(`${profileLabel} (dynamic, ${dataset.transactions?.length ?? 0} txns)`);
    } catch (error) {
      setInputError(`Failed to generate dynamic dataset: ${error?.message ?? 'unknown error'}`);
    } finally {
      setDynamicLoading(false);
    }
  };

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
  const allSteps = pipelineState?.steps || {};
  const hasProcessingSteps = Object.values(allSteps).some(
    (step) => step?.status === 'processing'
  );
  const isProcessingStatus = pipelineState?.isRunning || hasProcessingSteps;
  const statusClass = isProcessingStatus
    ? 'text-processing'
    : pipelineState?.results?.success
      ? 'text-success'
      : 'text-error';
  const statusText = isProcessingStatus
    ? 'Running'
    : pipelineState?.results?.success
      ? 'Success'
      : 'Failed';

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
                  <span className={`text-sm font-medium ${statusClass}`}>
                    {statusText}
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
            <div className="mb-4 space-y-3">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Generate a synthetic dataset if you need a fresh input shape.
              </p>
              <div className="grid gap-2 sm:grid-cols-3 sm:items-end">
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                    Scenario
                  </label>
                  <select
                    value={dynamicProfile}
                    onChange={(e) => setDynamicProfile(e.target.value)}
                    disabled={pipelineState?.isRunning || dynamicLoading}
                    className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 transition focus:border-processing focus:outline-none dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100"
                  >
                    {DYNAMIC_DATA_PROFILES.map((profile) => (
                      <option key={profile.value} value={profile.value}>
                        {profile.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                    Transactions
                  </label>
                  <input
                    type="number"
                    min={10}
                    max={3000}
                    value={dynamicCount}
                    onChange={(e) => {
                      const parsed = Number(e.target.value);
                      if (Number.isNaN(parsed)) return;
                      setDynamicCount(Math.max(10, Math.min(3000, parsed)));
                    }}
                    disabled={pipelineState?.isRunning || dynamicLoading}
                    className="w-full rounded-md border border-gray-300 bg-white px-2 py-1 text-sm text-gray-700 focus:border-processing focus:outline-none dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100"
                  />
                </div>
                <div className="sm:col-span-3">
                  <button
                    type="button"
                    onClick={handleGenerateDynamicDataset}
                    disabled={pipelineState?.isRunning || dynamicLoading}
                    className={`btn-primary w-full text-sm ${
                      pipelineState?.isRunning || dynamicLoading
                        ? 'opacity-60 cursor-not-allowed'
                        : ''
                    }`}
                  >
                    {dynamicLoading ? 'Generating…' : 'Generate dynamic dataset'}
                  </button>
                </div>
              </div>
            </div>
            <div className="mb-4">
              <span className="text-xs text-gray-400 dark:text-gray-500">
                Active input: {activeGeneratorLabel}
              </span>
            </div>
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
