"""
Key Management for Repersonalization
Handles encryption keys (shared with Pseudonymization Service)
"""

import os
import json
import secrets
import hashlib
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class KeyManager:
    """
    Manages encryption keys for repersonalization
    Should be synchronized with Pseudonymization Service keys
    """
    
    def __init__(self, key_store_path: str):
        self.key_store_path = Path(key_store_path)
        self.key_store_path.parent.mkdir(parents=True, exist_ok=True)
        self.current_key = None
        self.key_version = None
        
        # Initialize or load keys
        self._initialize_keys()
    
    def _initialize_keys(self):
        """Initialize or load encryption keys"""
        if self.key_store_path.exists():
            self._load_keys()
        else:
            logger.warning("No keys found. Please ensure keys are synchronized with Pseudonymization Service.")
            # In production, fetch keys from shared key management service
    
    def _load_keys(self):
        """Load keys from storage"""
        try:
            with open(self.key_store_path, 'r') as f:
                key_data = json.load(f)
            
            self.key_version = key_data['version']
            
            # Load actual key
            key_file = self.key_store_path.parent / f"key_{self.key_version}.key"
            if key_file.exists():
                with open(key_file, 'r') as f:
                    self.current_key = f.read().strip()
                
                logger.info(f"Keys loaded: {self.key_version}")
            else:
                logger.error(f"Key file not found: {key_file}")
        except Exception as e:
            logger.error(f"Failed to load keys: {str(e)}")
    
    def get_current_key(self) -> str:
        """Get current encryption key"""
        if not self.current_key:
            self._initialize_keys()
        return self.current_key
    
    def get_key_version(self) -> str:
        """Get current key version"""
        return self.key_version
    
    def sync_keys(self, key_store_path: str):
        """
        Synchronize keys with Pseudonymization Service
        
        Args:
            key_store_path: Path to shared key store
        """
        try:
            # In production, this would sync from shared key management service
            source_path = Path(key_store_path)
            if source_path.exists():
                import shutil
                shutil.copy(source_path, self.key_store_path)
                self._load_keys()
                logger.info("Keys synchronized successfully")
            else:
                logger.error(f"Source key store not found: {key_store_path}")
        except Exception as e:
            logger.error(f"Key synchronization failed: {str(e)}")
    
    def is_initialized(self) -> bool:
        """Check if key manager is initialized"""
        return self.current_key is not None

