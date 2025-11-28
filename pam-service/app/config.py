"""
Configuration for PAM (Prompt Augmentation Model) Service
"""

import os
from typing import Optional

class Settings:
    """PAM Service Configuration"""
    
    # Service Configuration
    HOST: str = os.getenv("PAM_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PAM_PORT", "5005"))
    DEBUG: bool = os.getenv("PAM_DEBUG", "false").lower() == "true"
    
    # Qdrant Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION: str = "pam_augmented_data"
    
    # Ollama Configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "localhost")
    OLLAMA_PORT: int = int(os.getenv("OLLAMA_PORT", "11434"))
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    # Caching Configuration
    CACHE_TTL_HOURS: int = int(os.getenv("PAM_CACHE_TTL_HOURS", "24"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("PAM_SIMILARITY_THRESHOLD", "0.85"))
    
    # Web Scraping Configuration
    SCRAPING_TIMEOUT: int = int(os.getenv("PAM_SCRAPING_TIMEOUT", "10"))
    USER_AGENT: str = "Mozilla/5.0 (compatible; PAM-Service/1.0; +http://prompt-engine)"
    MAX_RETRIES: int = 3
    RATE_LIMIT_DELAY: float = 1.0  # seconds between requests
    
    # LLM Research Configuration
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 500
    LLM_TIMEOUT: int = 30  # seconds
    
    # Feature Flags
    ENABLE_WEB_SCRAPING: bool = os.getenv("PAM_ENABLE_SCRAPING", "true").lower() == "true"
    ENABLE_LLM_RESEARCH: bool = os.getenv("PAM_ENABLE_LLM", "true").lower() == "true"
    ENABLE_CACHING: bool = os.getenv("PAM_ENABLE_CACHING", "true").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("PAM_LOG_LEVEL", "INFO")


# Global settings instance
settings = Settings()

