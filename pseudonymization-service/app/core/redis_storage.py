"""
Redis Storage for Pseudonymization
Persistent token storage with TTL support
"""

import redis
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class RedisStorage:
    """
    Redis-based storage for pseudonym mappings
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", ttl: int = 86400):
        """
        Initialize Redis storage
        
        Args:
            redis_url: Redis connection URL
            ttl: Time-to-live for tokens in seconds (default: 24 hours)
        """
        self.ttl = ttl
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.client.ping()
            logger.info(f"✅ Redis connected: {redis_url}")
        except redis.ConnectionError as e:
            logger.warning(f"⚠️  Redis connection failed: {str(e)}")
            logger.warning("Falling back to in-memory storage")
            self.client = None
        except Exception as e:
            logger.error(f"❌ Redis initialization error: {str(e)}")
            self.client = None
        
        # Fallback in-memory storage
        self.memory_storage = {}
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if self.client:
            try:
                self.client.ping()
                return True
            except:
                return False
        return False
    
    def store(self, pseudonym_id: str, data: Dict[str, Any]) -> bool:
        """
        Store pseudonym mapping
        
        Args:
            pseudonym_id: Unique pseudonym identifier
            data: Original data and metadata
            
        Returns:
            True if successful
        """
        try:
            if self.client and self.is_connected():
                # Store in Redis with TTL
                key = f"pseudonym:{pseudonym_id}"
                value = json.dumps(data)
                self.client.setex(key, self.ttl, value)
                logger.debug(f"Stored in Redis: {pseudonym_id} (TTL: {self.ttl}s)")
                return True
            else:
                # Fallback to memory
                self.memory_storage[pseudonym_id] = data
                logger.debug(f"Stored in memory: {pseudonym_id}")
                return True
        except Exception as e:
            logger.error(f"Storage error: {str(e)}")
            # Fallback to memory
            self.memory_storage[pseudonym_id] = data
            return True
    
    def retrieve(self, pseudonym_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve pseudonym mapping
        
        Args:
            pseudonym_id: Unique pseudonym identifier
            
        Returns:
            Original data if found, None otherwise
        """
        try:
            if self.client and self.is_connected():
                # Retrieve from Redis
                key = f"pseudonym:{pseudonym_id}"
                value = self.client.get(key)
                if value:
                    logger.debug(f"Retrieved from Redis: {pseudonym_id}")
                    return json.loads(value)
                else:
                    logger.debug(f"Not found in Redis: {pseudonym_id}")
                    return None
            else:
                # Fallback to memory
                data = self.memory_storage.get(pseudonym_id)
                if data:
                    logger.debug(f"Retrieved from memory: {pseudonym_id}")
                return data
        except Exception as e:
            logger.error(f"Retrieval error: {str(e)}")
            # Try memory fallback
            return self.memory_storage.get(pseudonym_id)
    
    def delete(self, pseudonym_id: str) -> bool:
        """
        Delete pseudonym mapping
        
        Args:
            pseudonym_id: Unique pseudonym identifier
            
        Returns:
            True if successful
        """
        try:
            if self.client and self.is_connected():
                # Delete from Redis
                key = f"pseudonym:{pseudonym_id}"
                deleted = self.client.delete(key)
                logger.debug(f"Deleted from Redis: {pseudonym_id} (count: {deleted})")
                return deleted > 0
            else:
                # Fallback to memory
                if pseudonym_id in self.memory_storage:
                    del self.memory_storage[pseudonym_id]
                    logger.debug(f"Deleted from memory: {pseudonym_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Deletion error: {str(e)}")
            # Try memory fallback
            if pseudonym_id in self.memory_storage:
                del self.memory_storage[pseudonym_id]
            return False
    
    def count(self) -> int:
        """Get count of stored pseudonyms"""
        try:
            if self.client and self.is_connected():
                # Count Redis keys
                keys = self.client.keys("pseudonym:*")
                return len(keys)
            else:
                return len(self.memory_storage)
        except Exception as e:
            logger.error(f"Count error: {str(e)}")
            return len(self.memory_storage)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            "storage_type": "redis" if (self.client and self.is_connected()) else "memory",
            "connected": self.is_connected(),
            "ttl_seconds": self.ttl,
            "active_pseudonyms": self.count()
        }
        
        if self.client and self.is_connected():
            try:
                info = self.client.info()
                stats["redis_info"] = {
                    "used_memory_human": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "uptime_in_days": info.get("uptime_in_days")
                }
            except:
                pass
        
        return stats

