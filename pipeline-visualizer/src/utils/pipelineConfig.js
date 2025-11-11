/**
 * Pipeline Configuration
 * Defines all 8 steps of the end-to-end pipeline with metadata and service endpoints
 */

export const PIPELINE_STEPS = [
  {
    id: 'data-generation',
    name: 'Data Generation',
    description: 'Generate business banking transactions with PII',
    icon: 'Database',
    type: 'data',
    color: '#8B5CF6',
    position: { x: 100, y: 100 },
    features: [
      'Business banking transactions',
      'PII data (names, emails, phone)',
      'Account information',
      'Transaction history'
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
    description: 'PII detection & masking',
    icon: 'Shield',
    type: 'process',
    color: '#10B981',
    position: { x: 350, y: 100 },
    port: 5003,
    endpoint: 'http://localhost:5003',
    healthCheck: '/health',
    apiPath: '/pseudonymize',
    features: [
      'Automatic PII detection (20+ types)',
      'Field-level security',
      'Reversible tokenization',
      'Data utility preservation'
    ],
    metrics: ['pii_detected', 'fields_pseudonymized', 'processing_time_ms']
  },
  {
    id: 'prompt-generation',
    name: 'Prompt Generation',
    description: 'Intelligent prompt creation',
    icon: 'FileText',
    type: 'process',
    color: '#3B82F6',
    position: { x: 600, y: 100 },
    port: 5000,
    endpoint: 'http://localhost:5000',
    healthCheck: '/health',
    apiPath: '/generate',
    features: [
      'Template-based generation',
      'Context inference',
      'Multi-type generation',
      'Agentic intelligence'
    ],
    metrics: ['generation_mode', 'template_used', 'processing_time']
  },
  {
    id: 'rag-enhancement',
    name: 'RAG Enhancement',
    description: 'Vector database context augmentation',
    icon: 'Brain',
    type: 'process',
    color: '#F59E0B',
    position: { x: 850, y: 100 },
    port: 6333,
    endpoint: 'http://localhost:6333',
    healthCheck: '/collections',
    features: [
      'Vector similarity search',
      'Context augmentation',
      'Pattern matching',
      'Knowledge retrieval'
    ],
    metrics: ['rag_items_found', 'similarity_scores', 'vector_db_time']
  },
  {
    id: 'llm-analysis',
    name: 'LLM Analysis',
    description: 'Ollama text generation',
    icon: 'Sparkles',
    type: 'process',
    color: '#EC4899',
    position: { x: 100, y: 300 },
    port: 11434,
    endpoint: 'http://localhost:11434',
    healthCheck: '/api/tags',
    apiPath: '/api/generate',
    features: [
      'Local LLM inference',
      'Multiple model support',
      'Structured output',
      'Fast generation'
    ],
    metrics: ['tokens_used', 'model_name', 'llm_time']
  },
  {
    id: 'validation',
    name: 'Validation',
    description: 'Quality assessment',
    icon: 'CheckCircle',
    type: 'decision',
    color: '#06B6D4',
    position: { x: 350, y: 300 },
    port: 5002,
    endpoint: 'http://localhost:5002',
    healthCheck: '/health',
    apiPath: '/validate/response',
    features: [
      'Multi-criteria assessment',
      'Quality scoring (0-100%)',
      'Automated quality gates',
      'Fast validation (<20s)'
    ],
    metrics: ['overall_score', 'quality_level', 'validation_time', 'criteria_scores']
  },
  {
    id: 'self-learning',
    name: 'Self-Learning',
    description: 'Pattern storage & knowledge graph',
    icon: 'GitBranch',
    type: 'process',
    color: '#8B5CF6',
    position: { x: 600, y: 300 },
    port: 5000,
    endpoint: 'http://localhost:5000',
    healthCheck: '/self-learning/status',
    apiPath: '/self-learning/metrics',
    features: [
      'Pattern learning',
      'Knowledge graph',
      'Cross-component bridge',
      'Continuous improvement'
    ],
    metrics: ['learning_stats', 'knowledge_graph_stats', 'patterns_learned']
  },
  {
    id: 'repersonalization',
    name: 'Repersonalization',
    description: 'Restore original data',
    icon: 'Unlock',
    type: 'process',
    color: '#EF4444',
    position: { x: 850, y: 300 },
    port: 5004,
    endpoint: 'http://localhost:5004',
    healthCheck: '/health',
    apiPath: '/repersonalize',
    features: [
      'Data restoration',
      'Integrity verification',
      'Secure retrieval',
      'GDPR compliance'
    ],
    metrics: ['processing_time_ms', 'verified', 'restoration_success']
  }
];

// Define connections between steps
export const PIPELINE_EDGES = [
  { id: 'e1-2', source: 'data-generation', target: 'pseudonymization', animated: true },
  { id: 'e2-3', source: 'pseudonymization', target: 'prompt-generation', animated: true },
  { id: 'e3-4', source: 'prompt-generation', target: 'rag-enhancement', animated: true },
  { id: 'e4-5', source: 'rag-enhancement', target: 'llm-analysis', animated: true },
  { id: 'e5-6', source: 'llm-analysis', target: 'validation', animated: true },
  { id: 'e6-7', source: 'validation', target: 'self-learning', animated: true },
  { id: 'e7-8', source: 'self-learning', target: 'repersonalization', animated: true },
];

// Service configuration
export const SERVICES = {
  PSEUDONYMIZATION: {
    name: 'Pseudonymization Service',
    port: 5003,
    url: 'http://localhost:5003',
    healthEndpoint: '/health'
  },
  REPERSONALIZATION: {
    name: 'Repersonalization Service',
    port: 5004,
    url: 'http://localhost:5004',
    healthEndpoint: '/health'
  },
  PROMPT_ENGINE: {
    name: 'Prompt Engine',
    port: 5000,
    url: 'http://localhost:5000',
    healthEndpoint: '/health'
  },
  VALIDATION: {
    name: 'Validation Service',
    port: 5002,
    url: 'http://localhost:5002',
    healthEndpoint: '/health'
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
  },
  SELF_LEARNING: {
    name: 'Self-Learning API',
    port: 5000,
    url: 'http://localhost:5000',
    healthEndpoint: '/self-learning/status'
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

