"""
Configuration for Autonomous Financial Analysis Agent
"""

import os
from typing import Dict, Any

# Prompt Engine Integration
PROMPT_ENGINE_HOST = os.getenv("PROMPT_ENGINE_HOST", "localhost")
PROMPT_ENGINE_PORT = int(os.getenv("PROMPT_ENGINE_PORT", "5000"))
PROMPT_ENGINE_URL = f"http://{PROMPT_ENGINE_HOST}:{PROMPT_ENGINE_PORT}"

# LLM Configuration (Multiple LLM Support)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")  # Llama 3.1 8B for complex reasoning

# OpenAI API (Optional - for comparison/validation)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# Anthropic Claude (Optional - for validation)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")

# Vector Database Configuration (Inherits from prompt-engine)
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "autonomous_agent_knowledge")

# Agent Configuration
AGENT_NAME = "AutonomousFinancialAgent"
AGENT_VERSION = "1.0.0"
MAX_REASONING_STEPS = int(os.getenv("MAX_REASONING_STEPS", "10"))
MIN_CONFIDENCE_THRESHOLD = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.7"))
ENABLE_FACT_CHECKING = os.getenv("ENABLE_FACT_CHECKING", "true").lower() == "true"
ENABLE_CROSS_VALIDATION = os.getenv("ENABLE_CROSS_VALIDATION", "true").lower() == "true"

# Response Validation
RESPONSE_MAX_LENGTH = int(os.getenv("RESPONSE_MAX_LENGTH", "5000"))
REQUIRE_CONFIDENCE_SCORES = os.getenv("REQUIRE_CONFIDENCE_SCORES", "true").lower() == "true"
REQUIRE_SOURCE_CITATIONS = os.getenv("REQUIRE_SOURCE_CITATIONS", "true").lower() == "true"

# Learning and Adaptation
ENABLE_LEARNING = os.getenv("ENABLE_LEARNING", "true").lower() == "true"
LEARNING_FEEDBACK_THRESHOLD = float(os.getenv("LEARNING_FEEDBACK_THRESHOLD", "0.8"))
MAX_INTERACTION_HISTORY = int(os.getenv("MAX_INTERACTION_HISTORY", "1000"))

# Flask Server Configuration
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "autonomous_agent.log")

# Anti-Hallucination Configuration
HALLUCINATION_DETECTION_MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",  # For semantic similarity
    "microsoft/DialoGPT-medium"  # For coherence checking
]

CONFIDENCE_CALCULATION_METHOD = os.getenv("CONFIDENCE_CALCULATION_METHOD", "ensemble")
UNCERTAINTY_QUANTIFICATION = os.getenv("UNCERTAINTY_QUANTIFICATION", "true").lower() == "true"

# Quality Gates Configuration
QUALITY_GATES = {
    "data_grounding": {"enabled": True, "threshold": 0.8},
    "logical_consistency": {"enabled": True, "threshold": 0.7},
    "source_validation": {"enabled": True, "threshold": 0.9},
    "confidence_threshold": {"enabled": True, "threshold": MIN_CONFIDENCE_THRESHOLD},
    "response_completeness": {"enabled": True, "threshold": 0.8}
}

# Agent Capabilities
AGENT_CAPABILITIES = {
    "financial_analysis": True,
    "risk_assessment": True,
    "transaction_analysis": True,
    "cash_flow_analysis": True,
    "credit_assessment": True,
    "loan_analysis": True,
    "card_analysis": True,
    "pattern_recognition": True,
    "anomaly_detection": True,
    "trend_analysis": True
}

# Integration Settings
PROMPT_ENGINE_ENDPOINTS = {
    "generate": "/generate",
    "learn": "/learn", 
    "analyze": "/agentic/analyze",
    "capabilities": "/capabilities",
    "vector_stats": "/vector/stats"
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary"""
    return {
        "prompt_engine": {
            "host": PROMPT_ENGINE_HOST,
            "port": PROMPT_ENGINE_PORT,
            "url": PROMPT_ENGINE_URL,
            "endpoints": PROMPT_ENGINE_ENDPOINTS
        },
        "llm": {
            "ollama": {
                "host": OLLAMA_HOST,
                "port": OLLAMA_PORT,
                "model": OLLAMA_MODEL
            },
            "openai": {
                "api_key": OPENAI_API_KEY,
                "model": OPENAI_MODEL
            },
            "anthropic": {
                "api_key": ANTHROPIC_API_KEY,
                "model": ANTHROPIC_MODEL
            }
        },
        "vector_db": {
            "host": QDRANT_HOST,
            "port": QDRANT_PORT,
            "collection": QDRANT_COLLECTION
        },
        "agent": {
            "name": AGENT_NAME,
            "version": AGENT_VERSION,
            "max_reasoning_steps": MAX_REASONING_STEPS,
            "min_confidence_threshold": MIN_CONFIDENCE_THRESHOLD,
            "capabilities": AGENT_CAPABILITIES
        },
        "validation": {
            "max_response_length": RESPONSE_MAX_LENGTH,
            "require_confidence_scores": REQUIRE_CONFIDENCE_SCORES,
            "require_source_citations": REQUIRE_SOURCE_CITATIONS,
            "quality_gates": QUALITY_GATES
        },
        "learning": {
            "enabled": ENABLE_LEARNING,
            "feedback_threshold": LEARNING_FEEDBACK_THRESHOLD,
            "max_history": MAX_INTERACTION_HISTORY
        },
        "anti_hallucination": {
            "fact_checking": ENABLE_FACT_CHECKING,
            "cross_validation": ENABLE_CROSS_VALIDATION,
            "detection_models": HALLUCINATION_DETECTION_MODELS,
            "confidence_method": CONFIDENCE_CALCULATION_METHOD,
            "uncertainty_quantification": UNCERTAINTY_QUANTIFICATION
        }
    }