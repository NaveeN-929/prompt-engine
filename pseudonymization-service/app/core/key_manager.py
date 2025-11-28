"""
Key Management for Pseudonymization
Handles encryption keys and key rotation
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
    Manages encryption keys for pseudonymization
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
            self._generate_new_keys()
    
    def _generate_new_keys(self):
        """Generate new encryption keys"""
        # Generate a secure random key
        self.current_key = secrets.token_hex(32)  # 256-bit key
        self.key_version = "v1_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Save keys
        self._save_keys()
        logger.info(f"Generated new keys: {self.key_version}")
    
    def _save_keys(self):
        """Save keys to secure storage"""
        key_data = {
            "version": self.key_version,
            "key_hash": hashlib.sha256(self.current_key.encode()).hexdigest(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # In production, use proper key management service (AWS KMS, HashiCorp Vault, etc.)
        # For demo, we'll store the key separately
        
        with open(self.key_store_path, 'w') as f:
            json.dump(key_data, f, indent=2)
        
        # Store actual key in environment variable or secure location
        # For demo purposes, store in a separate file
        key_file = self.key_store_path.parent / f"key_{self.key_version}.key"
        with open(key_file, 'w') as f:
            f.write(self.current_key)
        
        # Secure file permissions
        os.chmod(key_file, 0o600)
        
        logger.info(f"Keys saved: {self.key_store_path}")
    
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
                logger.warning(f"Key file not found: {key_file}")
                self._generate_new_keys()
        except Exception as e:
            logger.error(f"Failed to load keys: {str(e)}")
            self._generate_new_keys()
    
    def get_current_key(self) -> str:
        """Get current encryption key"""
        if not self.current_key:
            self._initialize_keys()
        return self.current_key
    
    def get_key_version(self) -> str:
        """Get current key version"""
        return self.key_version
    
    def rotate_keys(self):
        """Rotate encryption keys"""
        old_version = self.key_version
        self._generate_new_keys()
        logger.warning(f"Keys rotated: {old_version} -> {self.key_version}")
    
    def is_initialized(self) -> bool:
        """Check if key manager is initialized"""
        return self.current_key is not None

