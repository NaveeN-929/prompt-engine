"""
Configuration for Repersonalization Service
"""

import os
from typing import List


class Settings:
    """Service configuration"""
    
    # Server settings
    HOST: str = os.getenv("REPERSONAL_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("REPERSONAL_PORT", "5004"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002"
    ]
    
    # Key management (shared with Pseudonymization Service)
    KEY_STORE_PATH: str = os.getenv(
        "KEY_STORE_PATH",
        "./keys/keystore.json"
    )
    
    # Service URLs
    PSEUDONYMIZATION_SERVICE_URL: str = os.getenv(
        "PSEUDONYMIZATION_SERVICE_URL",
        "http://localhost:5003"
    )
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

