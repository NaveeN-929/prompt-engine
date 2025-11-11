/**
 * usePipelineData Hook
 * Manage pipeline execution state and data
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
    endTime: null
  });

  const handleStepComplete = useCallback((stepId, stepData) => {
    setPipelineState(prev => ({
      ...prev,
      currentStep: stepId,
      steps: {
        ...prev.steps,
        [stepId]: stepData
      }
    }));
  }, []);

  const executePipeline = useCallback(async (inputData) => {
    setPipelineState({
      isRunning: true,
      currentStep: null,
      steps: {},
      results: null,
      error: null,
      startTime: Date.now(),
      endTime: null
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
        error: results.success ? null : results.error
      }));

      return results;
    } catch (error) {
      setPipelineState(prev => ({
        ...prev,
        isRunning: false,
        error: error.message,
        endTime: Date.now()
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
      endTime: null
    });
  }, []);

  const getStepStatus = useCallback((stepId) => {
    const stepData = pipelineState.steps[stepId];
    if (!stepData) return 'idle';
    if (stepData.status === 'processing') return 'processing';
    if (stepData.status === 'success') return 'success';
    if (stepData.error) return 'error';
    return 'idle';
  }, [pipelineState.steps]);

  return {
    pipelineState,
    executePipeline,
    resetPipeline,
    getStepStatus
  };
};

export default usePipelineData;

