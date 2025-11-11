"""
Configuration for Pseudonymization Service
"""

import os
from typing import List


class Settings:
    """Service configuration"""
    
    # Server settings
    HOST: str = os.getenv("PSEUDO_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PSEUDO_PORT", "5003"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002"
    ]
    
    # Key management
    KEY_STORE_PATH: str = os.getenv(
        "KEY_STORE_PATH",
        "./keys/keystore.json"
    )
    
    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "86400"))  # 24 hours default
    
    # Service URLs
    REPERSONALIZATION_SERVICE_URL: str = os.getenv(
        "REPERSONALIZATION_SERVICE_URL",
        "http://localhost:5004"
    )
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

