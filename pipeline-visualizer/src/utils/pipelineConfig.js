/**
 * Pipeline Configuration
 * Defines the actual pipeline flow matching the architecture diagram
 * Updated: Reflects actual in-memory storage (Redis not implemented yet)
 */

export const PIPELINE_STEPS = [
  {
    id: 'input-data',
    name: 'Input Data',
    description: 'Multiple data input channels',
    icon: 'Database',
    type: 'data',
    color: '#8B5CF6',
    position: { x: 100, y: 50 },
    features: [
      'API input',
      'File Upload',
      'Streaming data',
      'Batch processing'
    ],
    sampleData: {
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
        }
      ]
    }
  },
  {
    id: 'pseudonymization',
    name: 'Pseudonymization',
    description: 'PII detection & secure tokenization',
    icon: 'Shield',
    type: 'process',
    color: '#10B981',
    position: { x: 100, y: 150 },
    port: 5003,
    endpoint: 'http://localhost:5003',
    healthCheck: '/health',
    apiPath: '/pseudonymize',
    features: [
      'PII Detection',
      'Token Mapping',
      'In-Memory Storage (for now)',
      'Reversible tokenization'
    ],
    metrics: ['pii_detected', 'fields_pseudonymized', 'processing_time_ms'],
    storageType: 'in-memory', // Currently uses Python dict, not Redis
    productionRecommendation: 'Use Redis for persistent token storage'
  },
  {
    id: 'autonomous-agent',
    name: 'Autonomous Agent',
    description: 'Financial analysis with RAG',
    icon: 'Brain',
    type: 'process',
    color: '#3B82F6',
    position: { x: 50, y: 300 },
    port: 5001,
    endpoint: 'http://localhost:5001',
    healthCheck: '/agent/status',
    apiPath: '/analyze',
    features: [
      'Financial Analysis',
      'RAG Enhancement',
      'Self-Learning Integration',
      'Multi-step Reasoning'
    ],
    metrics: ['processing_time', 'rag_items_found', 'confidence_score'],
    parallel: true // Runs in parallel with prompt-engine
  },
  {
    id: 'prompt-engine',
    name: 'Prompt Engine',
    description: 'Intelligent prompt generation with Self-Learning',
    icon: 'FileText',
    type: 'process',
    color: '#F59E0B',
    position: { x: 400, y: 300 },
    port: 5000,
    endpoint: 'http://localhost:5000',
    healthCheck: '/health',
    apiPath: '/generate',
    features: [
      'Prompt Generation',
      'Template Management',
      'Vector Acceleration',
      'Self-Learning System (built-in)'
    ],
    metrics: ['generation_mode', 'template_used', 'processing_time'],
    parallel: true, // Runs in parallel with autonomous-agent
    includesSelfLearning: true // Self-Learning API is part of this service
  },
  {
    id: 'validation-system',
    name: 'Validation System',
    description: 'Quality assessment with Vector DB & LLM',
    icon: 'CheckCircle',
    type: 'decision',
    color: '#06B6D4',
    position: { x: 225, y: 450 },
    port: 5002,
    endpoint: 'http://localhost:5002',
    healthCheck: '/health',
    apiPath: '/validate/response',
    features: [
      'Response Quality Assessment',
      'Multi-Criteria Validation',
      'Quality Gates',
      'Uses Vector DB & Ollama'
    ],
    metrics: ['overall_score', 'quality_level', 'validation_time', 'criteria_scores'],
    dependencies: {
      vectorDb: {
        name: 'Qdrant Vector DB',
        port: 6333,
        endpoint: 'http://localhost:6333'
      },
      llm: {
        name: 'Ollama LLM',
        port: 11434,
        endpoint: 'http://localhost:11434',
        models: ['mistral', 'llama3.1:8b', 'phi3:3.8b']
      }
    }
  },
  {
    id: 'self-learning',
    name: 'Self-Learning',
    description: 'Pattern storage & feedback loop (part of Prompt Engine)',
    icon: 'GitBranch',
    type: 'feedback',
    color: '#8B5CF6',
    position: { x: 500, y: 600 },
    port: 5000,
    endpoint: 'http://localhost:5000',
    healthCheck: '/self-learning/status',
    apiPath: '/self-learning/metrics',
    features: [
      'Pattern Learning',
      'Knowledge Graph',
      'Cross-Component Bridge',
      'Continuous Improvement'
    ],
    metrics: ['learning_stats', 'knowledge_graph_stats', 'patterns_learned'],
    isFeedbackLoop: true, // Not a sequential step, runs in background
    partOfPromptEngine: true // This is NOT a separate service
  },
  {
    id: 'repersonalization',
    name: 'Repersonalization',
    description: 'Restore original data securely',
    icon: 'Unlock',
    type: 'process',
    color: '#EF4444',
    position: { x: 225, y: 700 },
    port: 5004,
    endpoint: 'http://localhost:5004',
    healthCheck: '/health',
    apiPath: '/repersonalize',
    features: [
      'Token Reversal',
      'In-Memory Mapping (for now)',
      'Data Restoration',
      'GDPR Compliance'
    ],
    metrics: ['processing_time_ms', 'verified', 'restoration_success'],
    storageType: 'in-memory', // Currently uses in-memory, not Redis
    productionRecommendation: 'Use Redis for persistent token retrieval'
  },
  {
    id: 'output-data',
    name: 'Output Data',
    description: 'Multiple output channels',
    icon: 'Database',
    type: 'data',
    color: '#EC4899',
    position: { x: 225, y: 850 },
    features: [
      'Insights',
      'Recommendations',
      'Visualizations',
      'Multi-channel delivery'
    ]
  }
];

// Define connections - Updated to match actual architecture
export const PIPELINE_EDGES = [
  { id: 'e1-2', source: 'input-data', target: 'pseudonymization', animated: true },
  // Pseudonymization splits to both Agent and Prompt Engine (parallel)
  { id: 'e2-3a', source: 'pseudonymization', target: 'autonomous-agent', animated: true, label: 'Parallel' },
  { id: 'e2-3b', source: 'pseudonymization', target: 'prompt-engine', animated: true, label: 'Parallel' },
  // Both converge to Validation System
  { id: 'e3-4', source: 'autonomous-agent', target: 'validation-system', animated: true },
  { id: 'e3b-4', source: 'prompt-engine', target: 'validation-system', animated: true },
  // Validation to Repersonalization
  { id: 'e4-6', source: 'validation-system', target: 'repersonalization', animated: true },
  // Self-Learning feedback loop (dashed) - goes back to Prompt Engine since it's part of it
  { id: 'e4-5', source: 'validation-system', target: 'self-learning', animated: true, type: 'step', style: { strokeDasharray: '5,5', stroke: '#8B5CF6' } },
  { id: 'e5-3b', source: 'self-learning', target: 'prompt-engine', animated: false, type: 'step', style: { strokeDasharray: '5,5', stroke: '#8B5CF6' } },
  // Final output
  { id: 'e6-7', source: 'repersonalization', target: 'output-data', animated: true }
];

// Service configuration - ACTUAL implementation (no Redis yet)
export const SERVICES = {
  PSEUDONYMIZATION: {
    name: 'Pseudonymization Service',
    port: 5003,
    url: 'http://localhost:5003',
    healthEndpoint: '/health',
    storage: 'in-memory' // Uses Python dict, not Redis
  },
  AUTONOMOUS_AGENT: {
    name: 'Autonomous Agent',
    port: 5001,
    url: 'http://localhost:5001',
    healthEndpoint: '/agent/status'
  },
  PROMPT_ENGINE: {
    name: 'Prompt Engine',
    port: 5000,
    url: 'http://localhost:5000',
    healthEndpoint: '/health',
    includesSelfLearning: true // Self-Learning API is part of this service
  },
  VALIDATION: {
    name: 'Validation Service',
    port: 5002,
    url: 'http://localhost:5002',
    healthEndpoint: '/health'
  },
  REPERSONALIZATION: {
    name: 'Repersonalization Service',
    port: 5004,
    url: 'http://localhost:5004',
    healthEndpoint: '/health',
    storage: 'in-memory' // Uses in-memory, not Redis
  },
  QDRANT: {
    name: 'Qdrant Vector DB',
    port: 6333,
    url: 'http://localhost:6333',
    healthEndpoint: '/collections'
  },
  OLLAMA: {
    name: 'Ollama LLM',
    port: 11434,
    url: 'http://localhost:11434',
    healthEndpoint: '/api/tags'
  }
};

// Status colors
export const STATUS_COLORS = {
  success: '#10B981',
  processing: '#3B82F6',
  error: '#EF4444',
  idle: '#6B7280',
  warning: '#F59E0B'
};

// Quality level thresholds
export const QUALITY_THRESHOLDS = {
  exemplary: 0.95,
  high_quality: 0.80,
  acceptable: 0.65,
  poor: 0.0
};

export default {
  PIPELINE_STEPS,
  PIPELINE_EDGES,
  SERVICES,
  STATUS_COLORS,
  QUALITY_THRESHOLDS
};
