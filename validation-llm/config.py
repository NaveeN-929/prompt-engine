"""
Configuration settings for the Response Validation LLM System
"""

import os
from typing import Dict, Any, List

# Base Configuration
BASE_CONFIG = {
    "system": {
        "name": "Response Validation LLM",
        "version": "1.0.0",
        "description": "Validates autonomous agent responses and collects training data"
    },
    "server": {
        "host": "0.0.0.0",
        "port": 5002,
        "debug": False
    }
}

# LLM Configuration for Validation - Optimized for speed and reliability
# Development setup: Ollama in Docker, validation system locally
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
if not OLLAMA_HOST.startswith("http"):
    OLLAMA_HOST = f"http://{OLLAMA_HOST}:11434"

VALIDATION_LLM_CONFIG = {
    "primary_validator": {
        "model_name": "mistral:latest",  # Using mistral for reliable validation
        "host": OLLAMA_HOST,
        "max_tokens": 100,  # Reduced for faster validation
        "temperature": 0.1,  # Low temperature for consistent validation
        "timeout": 15  # Reduced timeout for faster response
    },
    "speed_validator": {
        "model_name": "mistral:latest",  # Using same model for consistency
        "host": OLLAMA_HOST, 
        "max_tokens": 50,  # Very small for speed
        "temperature": 0.2,
        "timeout": 10  # Reduced timeout for speed validation
    }
}

# Autonomous Agent Integration
AUTONOMOUS_AGENT_CONFIG = {
    "base_url": "http://localhost:5001",
    "endpoints": {
        "analyze": "/analyze",
        "status": "/agent/status",
        "feedback": "/feedback/validation"
    },
    "timeout": 60
}

# Prompt Engine Integration
PROMPT_ENGINE_CONFIG = {
    "base_url": "http://localhost:5000",
    "endpoints": {
        "generate": "/generate",
        "learn": "/learn",
        "status": "/system/status"
    },
    "timeout": 30
}

# Fast Validation Configuration
FAST_VALIDATION_CONFIG = {
    "enabled": True,
    "timeout_seconds": 20,  # Reduced maximum time for entire validation
    "criteria_timeout": 5,  # Reduced maximum time per validation criterion
    "skip_phases": ["detailed_analysis", "cross_validation", "training_data_storage"],
    "min_score_threshold": 0.3,  # Minimum score to consider valid
    "fallback_score": 0.5  # Fallback score when validation fails
}

# Vector Database Configuration - Using same Qdrant instance with different collections
VECTOR_DB_CONFIG = {
    "host": os.getenv("QDRANT_HOST", "localhost"),
    "port": int(os.getenv("QDRANT_PORT", "6333")),  # Same Qdrant instance as main project
    "collections": {
        "validated_responses": "validation_high_quality_responses",
        "validation_patterns": "validation_successful_patterns", 
        "training_data": "validation_training_dataset",
        "feedback_patterns": "validation_feedback_patterns"
    },
    "embedding_model": "all-MiniLM-L6-v2",
    "embedding_dim": 384
}

# Validation Criteria and Thresholds
VALIDATION_CRITERIA = {
    "content_accuracy": {
        "weight": 0.25,
        "threshold": 0.7,
        "description": "Factual correctness against input data"
    },
    "structural_compliance": {
        "weight": 0.15,
        "threshold": 0.8,
        "description": "Proper INSIGHTS/RECOMMENDATIONS format"
    },
    "logical_consistency": {
        "weight": 0.20,
        "threshold": 0.7,
        "description": "Internal reasoning consistency"
    },
    "completeness": {
        "weight": 0.15,
        "threshold": 0.6,
        "description": "All aspects addressed"
    },
    "business_relevance": {
        "weight": 0.15,
        "threshold": 0.6,
        "description": "Practical business applicability"
    },
    "actionability": {
        "weight": 0.10,
        "threshold": 0.5,
        "description": "Implementable recommendations"
    }
}

# Quality Classification Thresholds
QUALITY_THRESHOLDS = {
    "exemplary": 0.90,      # Store as premium training data
    "high_quality": 0.75,   # Store for training with notes
    "acceptable": 0.60,     # Flag for review
    "poor": 0.0            # Reject and provide feedback
}

# Training Data Storage Configuration
TRAINING_DATA_CONFIG = {
    "storage_path": "training_data/",
    "max_storage_size_gb": 10,
    "retention_days": 365,
    "categories": [
        "financial_analysis",
        "transaction_insights", 
        "credit_assessment",
        "investment_advice",
        "risk_management",
        "customer_service"
    ],
    "quality_levels": ["exemplary", "high_quality", "acceptable"]
}

# Validation Prompts Templates
VALIDATION_PROMPTS = {
    "content_accuracy": """
Evaluate the factual accuracy of this financial analysis response against the provided input data.

INPUT DATA:
{input_data}

RESPONSE TO VALIDATE:
{response}

EVALUATION CRITERIA:
1. Are all numerical values and calculations correct?
2. Are the insights directly supported by the input data?
3. Are there any unsupported claims or assumptions?
4. Is the data interpretation accurate and reasonable?

Provide a score from 0.0 to 1.0 and explain your reasoning.
""",

    "structural_compliance": """
Evaluate whether this response follows the required two-section format.

RESPONSE TO VALIDATE:
{response}

REQUIRED FORMAT:
=== SECTION 1: INSIGHTS ===
[Key findings and analysis]

=== SECTION 2: RECOMMENDATIONS ===
[Actionable suggestions]

EVALUATION CRITERIA:
1. Does it have both section headers exactly as specified?
2. Is there substantial content in each section?
3. Is the content appropriately categorized?
4. Is the overall structure clear and professional?

Provide a score from 0.0 to 1.0 and explain your reasoning.
""",

    "logical_consistency": """
Evaluate the logical consistency and reasoning quality of this response.

RESPONSE TO VALIDATE:
{response}

EVALUATION CRITERIA:
1. Are the insights logically derived from the data?
2. Do the recommendations follow from the insights?
3. Are there any logical contradictions or gaps?
4. Is the reasoning chain clear and sound?
5. Are conclusions appropriately qualified?

Provide a score from 0.0 to 1.0 and explain your reasoning.
""",

    "completeness": """
Evaluate how completely this response addresses the analysis request.

INPUT DATA:
{input_data}

RESPONSE TO VALIDATE:
{response}

EVALUATION CRITERIA:
1. Are all major aspects of the input data analyzed?
2. Are key patterns and trends identified?
3. Are important risks or opportunities highlighted?
4. Is the analysis comprehensive for the provided data?

Provide a score from 0.0 to 1.0 and explain your reasoning.
""",

    "business_relevance": """
Evaluate the business relevance and practical value of this response.

RESPONSE TO VALIDATE:
{response}

EVALUATION CRITERIA:
1. Are the insights valuable for business decision-making?
2. Are the recommendations practical and implementable?
3. Is the analysis relevant to typical business needs?
4. Does it provide actionable intelligence?

Provide a score from 0.0 to 1.0 and explain your reasoning.
""",

    "actionability": """
Evaluate how actionable and specific the recommendations are.

RESPONSE TO VALIDATE:
{response}

EVALUATION CRITERIA:
1. Are the recommendations specific and clear?
2. Can they be realistically implemented?
3. Are next steps or priorities indicated?
4. Is there sufficient detail for action?

Provide a score from 0.0 to 1.0 and explain your reasoning.
"""
}

# Feedback Templates for Autonomous Agent
FEEDBACK_TEMPLATES = {
    "high_quality": """
Validation Result: HIGH QUALITY (Score: {score:.2f})

Strengths:
{strengths}

This response demonstrates excellent quality and has been stored for training data enhancement.
""",

    "needs_improvement": """
Validation Result: NEEDS IMPROVEMENT (Score: {score:.2f})

Areas for Improvement:
{improvements}

Specific Recommendations:
{recommendations}

This feedback will help enhance future response quality.
""",

    "rejected": """
Validation Result: REJECTED (Score: {score:.2f})

Critical Issues:
{issues}

Required Changes:
{required_changes}

This response requires significant revision before acceptance.
"""
}

# Monitoring and Metrics Configuration
METRICS_CONFIG = {
    "collection_interval": 300,  # 5 minutes
    "retention_days": 30,
    "tracked_metrics": [
        "validation_requests",
        "quality_distribution", 
        "processing_times",
        "model_performance",
        "training_data_growth",
        "feedback_impact"
    ]
}

def get_config() -> Dict[str, Any]:
    """Get the complete configuration dictionary"""
    return {
        "base": BASE_CONFIG,
        "validation_llm": VALIDATION_LLM_CONFIG,
        "autonomous_agent": AUTONOMOUS_AGENT_CONFIG,
        "prompt_engine": PROMPT_ENGINE_CONFIG,
        "vector_db": VECTOR_DB_CONFIG,
        "validation_criteria": VALIDATION_CRITERIA,
        "quality_thresholds": QUALITY_THRESHOLDS,
        "training_data": TRAINING_DATA_CONFIG,
        "validation_prompts": VALIDATION_PROMPTS,
        "feedback_templates": FEEDBACK_TEMPLATES,
        "metrics": METRICS_CONFIG
    }

def get_validation_threshold(quality_level: str) -> float:
    """Get the threshold for a specific quality level"""
    return QUALITY_THRESHOLDS.get(quality_level, 0.0)

def get_validation_prompt(criteria: str) -> str:
    """Get the validation prompt template for a specific criteria"""
    return VALIDATION_PROMPTS.get(criteria, "")
