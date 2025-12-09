/**
 * API Service
 * Centralized API communication with all backend services
 * Updated: Redis added, Self-Learning is part of Prompt Engine
 */

import axios from 'axios';
import { SERVICES } from '../utils/pipelineConfig';

const OLLAMA_API_KEY = import.meta.env.VITE_OLLAMA_API_KEY;
const getOllamaHeaders = () => (OLLAMA_API_KEY ? { 'Ollama-Api-Key': OLLAMA_API_KEY } : {});

// Configure axios defaults
axios.defaults.timeout = 30000; // 30 seconds

// Timeout for long-running batch operations (large datasets)
const LONG_RUNNING_TIMEOUT_MS = 120000; // 2 minutes

const createLongRunningConfig = (overrides = {}) => ({
  timeout: LONG_RUNNING_TIMEOUT_MS,
  ...overrides
});

/**
 * Health Check Service
 */
export const healthCheckService = {
  /**
   * Check health of all services
   */
  async checkAllServices() {
    const results = {};
    
    for (const [key, service] of Object.entries(SERVICES)) {
      // Skip Redis for now - it doesn't have a standard HTTP health endpoint
      if (key === 'REDIS') {
        // Redis health is checked via the services that use it
        results[key] = {
          status: 'healthy', // Assume healthy if services using it are working
          name: service.name,
          port: service.port,
          data: { note: 'Health checked via dependent services' },
          timestamp: new Date().toISOString(),
          critical: service.critical
        };
        continue;
      }

      try {
        const response = await axios.get(
          `${service.url}${service.healthEndpoint}`,
          {
            timeout: 5000,
            headers: key === 'OLLAMA' ? getOllamaHeaders() : undefined
          }
        );
        results[key] = {
          status: 'healthy',
          name: service.name,
          port: service.port,
          data: response.data,
          timestamp: new Date().toISOString(),
          includesSelfLearning: service.includesSelfLearning || false,
          usesRedis: service.usesRedis || false
        };
      } catch (error) {
        results[key] = {
          status: 'unhealthy',
          name: service.name,
          port: service.port,
          error: error.message,
          timestamp: new Date().toISOString(),
          includesSelfLearning: service.includesSelfLearning || false,
          usesRedis: service.usesRedis || false
        };
      }
    }
    
    return results;
  },

  /**
   * Check single service health
   */
  async checkService(serviceKey) {
    const service = SERVICES[serviceKey];
    if (!service) {
      throw new Error(`Unknown service: ${serviceKey}`);
    }

    // Special handling for Redis
    if (serviceKey === 'REDIS') {
      return {
        status: 'healthy',
        data: { note: 'Health checked via dependent services' },
        timestamp: new Date().toISOString()
      };
    }

    try {
      const response = await axios.get(
        `${service.url}${service.healthEndpoint}`,
        {
          timeout: 5000,
          headers: serviceKey === 'OLLAMA' ? getOllamaHeaders() : undefined
        }
      );
      return {
        status: 'healthy',
        data: response.data,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }
};

/**
 * Pseudonymization Service API
 */
export const pseudonymizationService = {
  /**
   * Pseudonymize data
   */
  async pseudonymize(data) {
    const response = await axios.post(
      `${SERVICES.PSEUDONYMIZATION.url}/pseudonymize`,
      data,
      createLongRunningConfig()
    );
    return response.data;
  },

  /**
   * Get statistics
   */
  async getStats() {
    const response = await axios.get(`${SERVICES.PSEUDONYMIZATION.url}/stats`);
    return response.data;
  }
};

/**
 * PAM (Prompt Augmentation Model) Service API
 */
export const pamService = {
  /**
   * Augment prompt with company and market intelligence
   */
  async augment(inputData, options = {}) {
    console.log('[PAM] Calling augment endpoint:', `${SERVICES.PAM.url}/augment`);
    console.log('[PAM] Request payload:', {
      has_input_data: !!inputData,
      input_data_keys: inputData ? Object.keys(inputData) : [],
      transactions_count: inputData?.transactions?.length || 0,
      context: options.context
    });
    
    try {
      const response = await axios.post(
        `${SERVICES.PAM.url}/augment`,
        {
          input_data: inputData,
          prompt_text: options.prompt_text,
          companies: options.companies,
          context: options.context
        },
      createLongRunningConfig({
        headers: {
          'Content-Type': 'application/json'
        }
      })
      );
      console.log('[PAM] Response received:', {
        status: response.status,
        companies_count: response.data?.companies_analyzed?.length || 0
      });
      return response.data;
    } catch (error) {
      console.error('[PAM] Request failed:', {
        message: error.message,
        response_status: error.response?.status,
        response_data: error.response?.data
      });
      throw error;
    }
  },

  /**
   * Bulk augmentation
   */
  async augmentBulk(requests) {
    const response = await axios.post(
      `${SERVICES.PAM.url}/augment/bulk`,
      { requests }
    );
    return response.data;
  },

  /**
   * Get PAM statistics
   */
  async getStats() {
    const response = await axios.get(`${SERVICES.PAM.url}/stats`);
    return response.data;
  },

  /**
   * Clean up cache
   */
  async cleanup() {
    const response = await axios.post(`${SERVICES.PAM.url}/cleanup`);
    return response.data;
  }
};

/**
 * Autonomous Agent API
 */
export const autonomousAgentService = {
  /**
   * Run analysis via autonomous agent
   */
  async analyze(inputData, options = {}) {
    const response = await axios.post(
      `${SERVICES.AUTONOMOUS_AGENT.url}/analyze`,
      {
        input_data: inputData,
        request_config: {
          generation_type: options.generation_type || 'autonomous',
          include_validation: false // Validation is separate
        }
      },
      createLongRunningConfig()
    );
    return response.data;
  },

  /**
   * Get agent status
   */
  async getStatus() {
    const response = await axios.get(`${SERVICES.AUTONOMOUS_AGENT.url}/agent/status`);
    return response.data;
  }
};

/**
 * Prompt Engine API
 * Note: Self-Learning API is part of this service
 */
export const promptEngineService = {
  /**
   * Generate prompt
   */
  async generate(inputData, options = {}) {
    const response = await axios.post(
      `${SERVICES.PROMPT_ENGINE.url}/generate`,
      {
        input_data: inputData,
        context: options.context,
        data_type: options.data_type,
        generation_type: options.generation_type || 'standard'
      },
      createLongRunningConfig()
    );
    return response.data;
  },

  /**
   * Get system capabilities
   */
  async getCapabilities() {
    const response = await axios.get(`${SERVICES.PROMPT_ENGINE.url}/capabilities`);
    return response.data;
  },

  /**
   * Get statistics
   */
  async getStats() {
    const response = await axios.get(`${SERVICES.PROMPT_ENGINE.url}/stats`);
    return response.data;
  }
};

/**
 * Validation Service API
 */
export const validationService = {
  /**
   * Validate response
   */
  async validateResponse(responseData, inputData) {
    const response = await axios.post(
      `${SERVICES.VALIDATION.url}/validate/response`,
      {
        response_data: responseData,
        input_data: inputData
      },
      createLongRunningConfig()
    );
    return response.data;
  },

  /**
   * Get validation status
   */
  async getStatus() {
    const response = await axios.get(`${SERVICES.VALIDATION.url}/validation/status`);
    return response.data;
  }
};

/**
 * Repersonalization Service API
 */
export const repersonalizationService = {
  /**
   * Repersonalize data
   */
  async repersonalize(pseudonymId) {
    const response = await axios.post(
      `${SERVICES.REPERSONALIZATION.url}/repersonalize`,
      { pseudonym_id: pseudonymId },
      createLongRunningConfig()
    );
    return response.data;
  },

  /**
   * Get statistics
   */
  async getStats() {
    const response = await axios.get(`${SERVICES.REPERSONALIZATION.url}/stats`);
    return response.data;
  }
};

/**
 * Self-Learning API
 * Note: This is part of the Prompt Engine service (port 5000)
 */
export const selfLearningService = {
  /**
   * Get self-learning status
   */
  async getStatus() {
    const response = await axios.get(`${SERVICES.PROMPT_ENGINE.url}/self-learning/status`);
    return response.data;
  },

  /**
   * Get learning metrics
   */
  async getMetrics() {
    const response = await axios.get(`${SERVICES.PROMPT_ENGINE.url}/self-learning/metrics`);
    return response.data;
  },

  /**
   * Get analytics dashboard data
   */
  async getDashboardData() {
    const response = await axios.get(
      `${SERVICES.PROMPT_ENGINE.url}/self-learning/analytics/dashboard`
    );
    return response.data;
  },

  /**
   * Get knowledge graph statistics
   */
  async getKnowledgeGraphStats() {
    const response = await axios.get(
      `${SERVICES.PROMPT_ENGINE.url}/self-learning/knowledge-graph/stats`
    );
    return response.data;
  },

  /**
   * Submit learning feedback (background operation)
   */
  async submitFeedback(validationResult, inputData, response) {
    try {
      await axios.post(
        `${SERVICES.PROMPT_ENGINE.url}/learn`,
        {
          input_data: inputData,
          prompt_result: response.prompt,
          llm_response: response.response,
          quality_score: validationResult.overall_score,
          validation_result: validationResult,
          metadata: response.agentic_metadata || {}
        }
      );
    } catch (error) {
      console.error('Self-learning feedback submission failed:', error);
      // Don't throw - this is a background operation
    }
  }
};

/**
 * Data generator endpoint
 */

/**
 * Qdrant Vector DB API
 */
export const qdrantService = {
  /**
   * Get collections
   */
  async getCollections() {
    const response = await axios.get(`${SERVICES.QDRANT.url}/collections`);
    return response.data;
  },

  /**
   * Get collection info
   */
  async getCollectionInfo(collectionName) {
    const response = await axios.get(
      `${SERVICES.QDRANT.url}/collections/${collectionName}`
    );
    return response.data;
  }
};

/**
 * Ollama LLM API
 */
export const ollamaService = {
  /**
   * List available models
   */
  async listModels() {
    const response = await axios.get(`${SERVICES.OLLAMA.url}/api/tags`, {
      headers: getOllamaHeaders()
    });
    return response.data;
  },

  /**
   * Generate text
   */
  async generate(model, prompt) {
    const response = await axios.post(
      `${SERVICES.OLLAMA.url}/api/generate`,
      {
        model,
        prompt,
        stream: false
      },
      createLongRunningConfig({
        headers: getOllamaHeaders()
      })
    );
    return response.data;
  }
};

/**
 * Pipeline Execution Service
 * Executes the complete pipeline matching the actual architecture
 */
export const pipelineExecutionService = {
  /**
   * Execute complete pipeline with parallel processing
   */
  async executeFullPipeline(inputData, onStepComplete) {
    const results = {
      steps: {},
      startTime: Date.now(),
      endTime: null,
      totalTime: null,
      success: true,
      error: null
    };
    let activeStepId = null;

    const markActiveStepError = (error) => {
      if (!activeStepId) return;
      const errorPayload = {
        status: 'error',
        error: error.message
      };
      if (onStepComplete) onStepComplete(activeStepId, errorPayload);
      results.steps[activeStepId] = {
        ...(results.steps[activeStepId] || {}),
        ...errorPayload
      };
      activeStepId = null;
    };

    try {
      // Step 1: Input Data (already have it)
      if (onStepComplete) onStepComplete('input-data', { data: inputData, status: 'success' });
      results.steps['input-data'] = { data: inputData, status: 'success' };

      // Step 2: Pseudonymization (uses Redis for token storage)
      activeStepId = 'pseudonymization';
      if (onStepComplete) onStepComplete('pseudonymization', { status: 'processing' });
      const pseudoResult = await pseudonymizationService.pseudonymize(inputData);
      if (onStepComplete) onStepComplete('pseudonymization', { ...pseudoResult, status: 'success' });
      results.steps['pseudonymization'] = { ...pseudoResult, status: 'success' };
      activeStepId = null;

      // Step 2.5: PAM Augmentation (optional - enriches with company intelligence)
      let pamResult = null;
      activeStepId = 'pam-service';
      try {
        if (onStepComplete) onStepComplete('pam-service', { status: 'processing' });
        
        console.log('[PAM] Sending data to PAM service:', {
          customer_id: pseudoResult.pseudonymized_data?.customer_id,
          transaction_count: pseudoResult.pseudonymized_data?.transactions?.length,
          sample_descriptions: pseudoResult.pseudonymized_data?.transactions?.slice(0, 2).map(t => t.description)
        });
        
        pamResult = await pamService.augment(pseudoResult.pseudonymized_data, {
          context: 'core_banking'
        });
        
        console.log('[PAM] Augmentation complete:', {
          companies_found: pamResult.companies_analyzed?.length || 0,
          companies: pamResult.companies_analyzed,
          cache_hit: pamResult.cache_hit,
          time_ms: pamResult.processing_time_ms
        });
        
        if (onStepComplete) onStepComplete('pam-service', { ...pamResult, status: 'success' });
        results.steps['pam-service'] = { ...pamResult, status: 'success' };
      } catch (pamError) {
        // PAM is optional - continue without it
        console.error('[PAM] Service error:', pamError);
        console.warn('PAM service unavailable, continuing without augmentation:', pamError.message);
        if (onStepComplete) onStepComplete('pam-service', { status: 'warning', error: pamError.message });
        results.steps['pam-service'] = { status: 'warning', error: pamError.message, optional: true };
      } finally {
        activeStepId = null;
      }

      // Step 3: Parallel execution of Autonomous Agent AND Prompt Engine
      if (onStepComplete) {
        onStepComplete('autonomous-agent', { status: 'processing' });
        onStepComplete('prompt-engine', { status: 'processing' });
      }

      // Use PAM-augmented data if available, otherwise use pseudonymized data
      const dataForAnalysis = pamResult?.augmented_prompt 
        ? { ...pseudoResult.pseudonymized_data, pam_augmented: true, augmentation: pamResult }
        : pseudoResult.pseudonymized_data;

      // Execute both in parallel using Promise.all
      const [agentResult, promptResult] = await Promise.all([
        autonomousAgentService.analyze(dataForAnalysis).catch(err => ({
          error: err.message,
          status: 'error'
        })),
        promptEngineService.generate(dataForAnalysis, { 
          generation_type: 'autonomous' 
        }).catch(err => ({
          error: err.message,
          status: 'error'
        }))
      ]);

      if (onStepComplete) {
        onStepComplete('autonomous-agent', { ...agentResult, status: agentResult.error ? 'error' : 'success' });
        onStepComplete('prompt-engine', { ...promptResult, status: promptResult.error ? 'error' : 'success' });
      }
      results.steps['autonomous-agent'] = { ...agentResult, status: agentResult.error ? 'error' : 'success' };
      results.steps['prompt-engine'] = { ...promptResult, status: promptResult.error ? 'error' : 'success' };

      // Use the result from whichever succeeded (prefer agent result)
      const analysisResult = agentResult.error ? promptResult : agentResult;
      
      if (analysisResult.error) {
        throw new Error('Both Autonomous Agent and Prompt Engine failed');
      }

      // Step 4: Validation System (uses both Vector DB and Ollama internally)
      activeStepId = 'validation-system';
      if (onStepComplete) onStepComplete('validation-system', { status: 'processing' });
      const validationResult = await validationService.validateResponse(
        { analysis: analysisResult.analysis || analysisResult.response },
        inputData
      );
      if (onStepComplete) onStepComplete('validation-system', { ...validationResult, status: 'success' });
      results.steps['validation-system'] = { ...validationResult, status: 'success' };
      activeStepId = null;

      // Step 5: Self-Learning (background feedback loop - non-blocking)
      // Note: This is part of Prompt Engine, not a separate service
      if (onStepComplete) onStepComplete('self-learning', { status: 'processing' });
      // Don't await this - it's a background operation
      selfLearningService.submitFeedback(validationResult, inputData, analysisResult)
        .then(() => {
          if (onStepComplete) onStepComplete('self-learning', { status: 'success' });
          results.steps['self-learning'] = { status: 'success', feedback_submitted: true };
        })
        .catch(() => {
          if (onStepComplete) onStepComplete('self-learning', { status: 'warning' });
          results.steps['self-learning'] = { status: 'warning', feedback_submitted: false };
        });

      // Mark as processing immediately for UI
      results.steps['self-learning'] = { status: 'processing', feedback_submitted: 'pending' };

      // Step 6: Repersonalization (uses Redis to retrieve token mappings)
      activeStepId = 'repersonalization';
      if (onStepComplete) onStepComplete('repersonalization', { status: 'processing' });
      const repersonalResult = await repersonalizationService.repersonalize(
        pseudoResult.pseudonym_id
      );
      if (onStepComplete) onStepComplete('repersonalization', { ...repersonalResult, status: 'success' });
      results.steps['repersonalization'] = { ...repersonalResult, status: 'success' };
      activeStepId = null;

      // Step 7: Output Data
      const outputData = {
        insights: analysisResult.analysis || analysisResult.response,
        validation: validationResult,
        original_data: repersonalResult.original_data,
        quality_score: validationResult.overall_score,
        quality_level: validationResult.quality_level
      };
      if (onStepComplete) onStepComplete('output-data', { ...outputData, status: 'success' });
      results.steps['output-data'] = { ...outputData, status: 'success' };

    } catch (error) {
      markActiveStepError(error);
      results.success = false;
      results.error = error.message;
      console.error('Pipeline execution error:', error);
    }

    results.endTime = Date.now();
    results.totalTime = results.endTime - results.startTime;

    return results;
  }
};

export default {
  healthCheckService,
  pseudonymizationService,
  autonomousAgentService,
  promptEngineService,
  validationService,
  repersonalizationService,
  selfLearningService,
  qdrantService,
  ollamaService,
  pipelineExecutionService
};
