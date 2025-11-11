/**
 * API Service
 * Centralized API communication with all backend services
 */

import axios from 'axios';
import { SERVICES } from '../utils/pipelineConfig';

// Configure axios defaults
axios.defaults.timeout = 30000; // 30 seconds

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
      try {
        const response = await axios.get(
          `${service.url}${service.healthEndpoint}`,
          { timeout: 5000 }
        );
        results[key] = {
          status: 'healthy',
          name: service.name,
          port: service.port,
          data: response.data,
          timestamp: new Date().toISOString()
        };
      } catch (error) {
        results[key] = {
          status: 'unhealthy',
          name: service.name,
          port: service.port,
          error: error.message,
          timestamp: new Date().toISOString()
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

    try {
      const response = await axios.get(
        `${service.url}${service.healthEndpoint}`,
        { timeout: 5000 }
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
      data
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
 * Prompt Engine API
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
      }
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
      }
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
      { pseudonym_id: pseudonymId }
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
 */
export const selfLearningService = {
  /**
   * Get self-learning status
   */
  async getStatus() {
    const response = await axios.get(`${SERVICES.SELF_LEARNING.url}/self-learning/status`);
    return response.data;
  },

  /**
   * Get learning metrics
   */
  async getMetrics() {
    const response = await axios.get(`${SERVICES.SELF_LEARNING.url}/self-learning/metrics`);
    return response.data;
  },

  /**
   * Get analytics dashboard data
   */
  async getDashboardData() {
    const response = await axios.get(
      `${SERVICES.SELF_LEARNING.url}/self-learning/analytics/dashboard`
    );
    return response.data;
  },

  /**
   * Get knowledge graph statistics
   */
  async getKnowledgeGraphStats() {
    const response = await axios.get(
      `${SERVICES.SELF_LEARNING.url}/self-learning/knowledge-graph/stats`
    );
    return response.data;
  }
};

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
    const response = await axios.get(`${SERVICES.OLLAMA.url}/api/tags`);
    return response.data;
  },

  /**
   * Generate text
   */
  async generate(model, prompt) {
    const response = await axios.post(`${SERVICES.OLLAMA.url}/api/generate`, {
      model,
      prompt,
      stream: false
    });
    return response.data;
  }
};

/**
 * Pipeline Execution Service
 * Executes the complete pipeline end-to-end
 */
export const pipelineExecutionService = {
  /**
   * Execute complete pipeline
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

    try {
      // Step 1: Data Generation (already have input data)
      if (onStepComplete) onStepComplete('data-generation', { data: inputData });
      results.steps['data-generation'] = { data: inputData, status: 'success' };

      // Step 2: Pseudonymization
      if (onStepComplete) onStepComplete('pseudonymization', { status: 'processing' });
      const pseudoResult = await pseudonymizationService.pseudonymize(inputData);
      if (onStepComplete) onStepComplete('pseudonymization', pseudoResult);
      results.steps['pseudonymization'] = { ...pseudoResult, status: 'success' };

      // Step 3: Prompt Generation
      if (onStepComplete) onStepComplete('prompt-generation', { status: 'processing' });
      const promptResult = await promptEngineService.generate(
        pseudoResult.pseudonymized_data,
        { generation_type: 'autonomous' }
      );
      if (onStepComplete) onStepComplete('prompt-generation', promptResult);
      results.steps['prompt-generation'] = { ...promptResult, status: 'success' };

      // Step 4: RAG Enhancement (implicit in prompt generation)
      if (onStepComplete) onStepComplete('rag-enhancement', { 
        vector_accelerated: promptResult.vector_accelerated,
        rag_metadata: promptResult.agentic_metadata
      });
      results.steps['rag-enhancement'] = { 
        vector_accelerated: promptResult.vector_accelerated,
        status: 'success' 
      };

      // Step 5: LLM Analysis (already done in prompt generation)
      if (onStepComplete) onStepComplete('llm-analysis', {
        response: promptResult.response,
        tokens_used: promptResult.tokens_used
      });
      results.steps['llm-analysis'] = {
        response: promptResult.response,
        tokens_used: promptResult.tokens_used,
        status: 'success'
      };

      // Step 6: Validation
      if (onStepComplete) onStepComplete('validation', { status: 'processing' });
      const validationResult = await validationService.validateResponse(
        { analysis: promptResult.response },
        inputData
      );
      if (onStepComplete) onStepComplete('validation', validationResult);
      results.steps['validation'] = { ...validationResult, status: 'success' };

      // Step 7: Self-Learning
      if (onStepComplete) onStepComplete('self-learning', { status: 'processing' });
      const learningMetrics = await selfLearningService.getMetrics();
      if (onStepComplete) onStepComplete('self-learning', learningMetrics);
      results.steps['self-learning'] = { ...learningMetrics, status: 'success' };

      // Step 8: Repersonalization
      if (onStepComplete) onStepComplete('repersonalization', { status: 'processing' });
      const repersonalResult = await repersonalizationService.repersonalize(
        pseudoResult.pseudonym_id
      );
      if (onStepComplete) onStepComplete('repersonalization', repersonalResult);
      results.steps['repersonalization'] = { ...repersonalResult, status: 'success' };

    } catch (error) {
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
  promptEngineService,
  validationService,
  repersonalizationService,
  selfLearningService,
  qdrantService,
  ollamaService,
  pipelineExecutionService
};

