/**
 * usePipelineData Hook
 * Manage pipeline execution state and data
 * Updated to handle parallel processing architecture
 */

import { useState, useCallback } from 'react';
import { pipelineExecutionService } from '../services/apiService';

export const usePipelineData = () => {
  const [pipelineState, setPipelineState] = useState({
    isRunning: false,
    currentStep: null,
    steps: {},
    results: null,
    error: null,
    startTime: null,
    endTime: null,
    parallelSteps: [] // Track steps running in parallel
  });

  const handleStepComplete = useCallback((stepId, stepData) => {
    setPipelineState(prev => {
      const newState = {
        ...prev,
        currentStep: stepId,
        steps: {
          ...prev.steps,
          [stepId]: stepData
        }
      };

      // Track parallel execution
      if (stepId === 'autonomous-agent' || stepId === 'prompt-engine') {
        if (stepData.status === 'processing') {
          newState.parallelSteps = [...prev.parallelSteps, stepId];
        } else if (stepData.status === 'success' || stepData.status === 'error') {
          newState.parallelSteps = prev.parallelSteps.filter(s => s !== stepId);
        }
      }

      return newState;
    });
  }, []);

  const executePipeline = useCallback(async (inputData) => {
    setPipelineState({
      isRunning: true,
      currentStep: null,
      steps: {},
      results: null,
      error: null,
      startTime: Date.now(),
      endTime: null,
      parallelSteps: []
    });

    try {
      const results = await pipelineExecutionService.executeFullPipeline(
        inputData,
        handleStepComplete
      );

      setPipelineState(prev => ({
        ...prev,
        isRunning: false,
        results,
        endTime: Date.now(),
        error: results.success ? null : results.error,
        parallelSteps: []
      }));

      return results;
    } catch (error) {
      setPipelineState(prev => ({
        ...prev,
        isRunning: false,
        error: error.message,
        endTime: Date.now(),
        parallelSteps: []
      }));
      throw error;
    }
  }, [handleStepComplete]);

  const resetPipeline = useCallback(() => {
    setPipelineState({
      isRunning: false,
      currentStep: null,
      steps: {},
      results: null,
      error: null,
      startTime: null,
      endTime: null,
      parallelSteps: []
    });
  }, []);

  const getStepStatus = useCallback((stepId) => {
    const stepData = pipelineState.steps[stepId];
    if (!stepData) return 'idle';
    if (stepData.status === 'processing') return 'processing';
    if (stepData.status === 'success') return 'success';
    if (stepData.status === 'error') return 'error';
    if (stepData.status === 'warning') return 'warning';
    return 'idle';
  }, [pipelineState.steps]);

  const isStepRunning = useCallback((stepId) => {
    return pipelineState.parallelSteps.includes(stepId) || 
           pipelineState.currentStep === stepId;
  }, [pipelineState.parallelSteps, pipelineState.currentStep]);

  return {
    pipelineState,
    executePipeline,
    resetPipeline,
    getStepStatus,
    isStepRunning
  };
};

export default usePipelineData;
