"""
Qdrant Cache Module
Caches augmented data in Qdrant vector database for fast retrieval
"""

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import hashlib
import time
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

# Try to import sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available, using basic hashing")
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class QdrantCache:
    """Cache augmented data in Qdrant for similarity-based retrieval"""
    
    def __init__(self, qdrant_host: str, qdrant_port: int, 
                 collection_name: str = "pam_augmented_data",
                 cache_ttl_hours: int = 24,
                 similarity_threshold: float = 0.85):
        """
        Initialize Qdrant cache
        
        Args:
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            collection_name: Name of the collection
            cache_ttl_hours: Cache TTL in hours
            similarity_threshold: Minimum similarity for cache hit
        """
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.collection_name = collection_name
        self.cache_ttl_hours = cache_ttl_hours
        self.similarity_threshold = similarity_threshold
        
        # Connect to Qdrant
        try:
            self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
            logger.info(f"Connected to Qdrant at {qdrant_host}:{qdrant_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            self.client = None
        
        # Initialize embedder
        self.embedder = None
        self.embedding_dim = 384
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                logger.info("Sentence transformer loaded for embeddings")
            except Exception as e:
                logger.warning(f"Could not load sentence transformer: {e}")
        
        # Setup collection
        if self.client:
            self._setup_collection()
        
        # Stats
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'items_stored': 0,
            'items_expired': 0
        }
    
    def _setup_collection(self):
        """Setup Qdrant collection"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name 
                                  for col in collections.collections)
            
            if not collection_exists:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Using existing Qdrant collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to setup collection: {e}")
    
    def _create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        if self.embedder:
            try:
                embedding = self.embedder.encode(text, convert_to_tensor=False)
                return embedding.tolist()
            except Exception as e:
                logger.warning(f"Embedding generation failed: {e}")
        
        # Fallback: Use hash-based pseudo-embedding
        return self._hash_to_embedding(text)
    
    def _hash_to_embedding(self, text: str) -> List[float]:
        """
        Create a deterministic pseudo-embedding from text hash
        
        Args:
            text: Text to hash
            
        Returns:
            Pseudo-embedding vector
        """
        # Create hash
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to floats in range [-1, 1]
        embedding = []
        for i in range(0, min(len(hash_bytes), self.embedding_dim), 1):
            val = (hash_bytes[i] / 255.0) * 2 - 1
            embedding.append(float(val))
        
        # Pad to required dimension
        while len(embedding) < self.embedding_dim:
            embedding.append(0.0)
        
        return embedding[:self.embedding_dim]
    
    def _create_cache_key(self, companies: List[str], context: str = None) -> str:
        """
        Create a cache key for companies and context
        
        Args:
            companies: List of company names
            context: Optional context string
            
        Returns:
            Cache key string
        """
        # Sort companies for consistent keys
        sorted_companies = sorted([c.lower() for c in companies])
        key_parts = sorted_companies
        
        if context:
            key_parts.append(context.lower())
        
        return "|".join(key_parts)
    
    def get_cached_augmentation(self, companies: List[str], 
                               context: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached augmentation data
        
        Args:
            companies: List of company names
            context: Optional context
            
        Returns:
            Cached data or None if not found
        """
        if not self.client or not companies:
            return None
        
        try:
            # Create query key and embedding
            cache_key = self._create_cache_key(companies, context)
            query_embedding = self._create_embedding(cache_key)
            
            # Search for similar entries
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=1,
                score_threshold=self.similarity_threshold
            )
            
            if search_result and len(search_result) > 0:
                hit = search_result[0]
                
                # Check if expired
                payload = hit.payload
                timestamp = payload.get('timestamp')
                
                if timestamp:
                    cache_time = datetime.fromisoformat(timestamp)
                    age_hours = (datetime.utcnow() - cache_time).total_seconds() / 3600
                    
                    if age_hours > self.cache_ttl_hours:
                        logger.info(f"Cache entry expired (age: {age_hours:.1f}h)")
                        self.stats['items_expired'] += 1
                        return None
                
                # Cache hit!
                self.stats['cache_hits'] += 1
                logger.info(f"Cache hit for companies: {', '.join(companies[:3])}")
                
                return {
                    'augmented_data': payload.get('augmented_data'),
                    'companies_analyzed': payload.get('companies_analyzed'),
                    'timestamp': timestamp,
                    'cache_hit': True,
                    'similarity_score': hit.score
                }
            
            # Cache miss
            self.stats['cache_misses'] += 1
            logger.info(f"Cache miss for companies: {', '.join(companies[:3])}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def store_augmentation(self, companies: List[str], 
                          augmented_data: Dict[str, Any],
                          context: str = None):
        """
        Store augmentation data in cache
        
        Args:
            companies: List of company names
            augmented_data: Augmentation data to cache
            context: Optional context
        """
        if not self.client or not companies:
            return
        
        try:
            # Create cache key and embedding
            cache_key = self._create_cache_key(companies, context)
            embedding = self._create_embedding(cache_key)
            
            # Create payload
            payload = {
                'cache_key': cache_key,
                'companies_analyzed': companies,
                'context': context,
                'augmented_data': augmented_data,
                'timestamp': datetime.utcnow().isoformat(),
                'ttl_hours': self.cache_ttl_hours
            }
            
            # Generate unique ID
            point_id = str(uuid.uuid4())
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            self.stats['items_stored'] += 1
            logger.info(f"Stored augmentation for companies: {', '.join(companies[:3])}")
            
        except Exception as e:
            logger.error(f"Error storing in cache: {e}")
    
    def cleanup_expired(self):
        """Clean up expired cache entries"""
        if not self.client:
            return
        
        try:
            # Get all points
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                limit=100
            )
            
            expired_ids = []
            cutoff_time = datetime.utcnow() - timedelta(hours=self.cache_ttl_hours)
            
            for point in scroll_result[0]:
                timestamp = point.payload.get('timestamp')
                if timestamp:
                    cache_time = datetime.fromisoformat(timestamp)
                    if cache_time < cutoff_time:
                        expired_ids.append(point.id)
            
            # Delete expired entries
            if expired_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(points=expired_ids)
                )
                logger.info(f"Cleaned up {len(expired_ids)} expired cache entries")
                self.stats['items_expired'] += len(expired_ids)
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_rate = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'hit_rate_percentage': round(hit_rate, 2),
            'items_stored': self.stats['items_stored'],
            'items_expired': self.stats['items_expired'],
            'collection_name': self.collection_name,
            'ttl_hours': self.cache_ttl_hours,
            'connected': self.client is not None
        }

