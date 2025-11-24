import React, { useState, useEffect, useMemo } from 'react';
import Header from './components/layout/Header';
import ViewSelector from './components/layout/ViewSelector';
import FlowDiagram from './components/visualizations/FlowDiagram';
import MetricsDashboard from './components/visualizations/MetricsDashboard';
import ExecutionView from './components/visualizations/ExecutionView';
import { ReactFlowProvider } from 'reactflow';
import useServiceHealth from './hooks/useServiceHealth';
import usePipelineData from './hooks/usePipelineData';

function App() {
  const [currentView, setCurrentView] = useState('flow');
  const [darkMode, setDarkMode] = useState(() => {
    // Check localStorage or system preference
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) return JSON.parse(saved);
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Health monitoring
  const { 
    healthStatus, 
    loading: healthLoading, 
    getHealthySummary 
  } = useServiceHealth(5000); // Poll every 5 seconds

  // Pipeline execution
  const { 
    pipelineState, 
    executePipeline, 
    resetPipeline, 
    getStepStatus 
  } = usePipelineData();

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(prev => {
      const newMode = !prev;
      localStorage.setItem('darkMode', JSON.stringify(newMode));
      return newMode;
    });
  };

  // Apply dark mode class to html element
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Get health summary for header
  const healthSummary = useMemo(() => {
    return getHealthySummary();
  }, [getHealthySummary]);

  // Generate step statuses for visualization components
  const stepStatuses = useMemo(() => {
    const statuses = {};
    const steps = [
      'input-data',
      'pseudonymization', 
      'autonomous-agent', 
      'prompt-engine',
      'validation-system', 
      'self-learning', 
      'repersonalization',
      'output-data'
    ];
    
    steps.forEach(stepId => {
      statuses[stepId] = getStepStatus(stepId);
    });
    
    return statuses;
  }, [getStepStatus, pipelineState]);

  // Handle pipeline execution
  const handleExecutePipeline = async (inputData) => {
    try {
      await executePipeline(inputData);
    } catch (error) {
      console.error('Pipeline execution failed:', error);
    }
  };

  // Render current view
  const renderView = () => {
    if (healthLoading && !healthStatus) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-processing mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">
              Loading services...
            </p>
          </div>
        </div>
      );
    }

    switch (currentView) {
      case 'flow':
        return (
          <div className="flex-1 min-h-0 relative overflow-hidden">
            <ReactFlowProvider>
              <FlowDiagram 
                pipelineState={pipelineState}
                stepStatuses={stepStatuses}
              />
            </ReactFlowProvider>
          </div>
        );
      case 'dashboard':
        return (
          <div className="flex-1 overflow-y-auto">
            <MetricsDashboard 
              healthStatus={healthStatus}
              pipelineState={pipelineState}
            />
          </div>
        );
      case 'execution':
        return (
          <div className="flex-1 overflow-y-auto">
            <ExecutionView
              pipelineState={pipelineState}
              onExecute={handleExecutePipeline}
              onReset={resetPipeline}
              stepStatuses={stepStatuses}
            />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      <Header 
        darkMode={darkMode}
        toggleDarkMode={toggleDarkMode}
        healthSummary={healthSummary}
      />
      
      <ViewSelector 
        currentView={currentView}
        onViewChange={setCurrentView}
      />

      <main className="flex-1 min-h-0 flex flex-col overflow-hidden">
        {renderView()}
      </main>

      <footer className="flex-shrink-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between text-sm">
            <div className="text-gray-600 dark:text-gray-400">
              Pipeline Visualizer v1.0.0 - Self-Learning Prompt Engine System
            </div>
            <div className="flex items-center gap-4">
              <span className="text-gray-500 dark:text-gray-500">
                Parallel Processing: Agent + Prompt Engine | Redis Token Storage
              </span>
              {pipelineState.isRunning && (
                <span className="flex items-center gap-2 text-processing">
                  <span className="w-2 h-2 bg-processing rounded-full animate-pulse"></span>
                  Pipeline Running
                </span>
              )}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
