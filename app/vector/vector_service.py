"""
Vector Service for Qdrant Integration - Fast similarity search for agentic prompts
"""

import time
import json
import hashlib
from typing import Dict, Any, List, Tuple, Optional
# Conditional import for Python 3.13 compatibility
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("⚠️ sentence-transformers not available (Python 3.13 compatibility)")
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import numpy as np

class VectorService:
    """
    High-performance vector service for prompt generation optimization
    Uses Qdrant for fast similarity search and caching
    """
    
    def __init__(self, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        # Initialize Qdrant client - NO FALLBACKS
        self.client = None

        try:
            # Connect to Qdrant instance
            self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
            # Test the connection
            self.client.get_collections()
            print(f"🔗 Connected to Qdrant at {qdrant_host}:{qdrant_port}")
        except Exception as e:
            print(f"❌ Could not connect to Qdrant at {qdrant_host}:{qdrant_port}: {e}")
            print("🚫 Vector database unavailable - no fallbacks allowed")
            raise Exception(f"Qdrant database unavailable at {qdrant_host}:{qdrant_port}. Vector database is required for operation.")
        
        # Initialize embedding model with Python 3.13 compatibility
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print("🧠 Loading sentence transformer model...")
                # Use device='cpu' to avoid tensor device issues
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
                print("✅ Sentence transformer loaded successfully")
            except Exception as e:
                print(f"⚠️ Error loading sentence transformer: {e}")
                print("🔄 Trying alternative loading method...")
                try:
                    # Alternative: Load with trust_remote_code and explicit device
                    import torch
                    torch.set_num_threads(1)  # Reduce thread conflicts
                    self.embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu', trust_remote_code=True)
                    self.embedding_dim = 384
                    print("✅ Sentence transformer loaded with alternative method")
                except Exception as e2:
                    print(f"❌ Failed to load sentence transformer: {e2}")
                    print("📝 Disabling vector embeddings")
                    self.embedder = None
                    self.embedding_dim = 384
        else:
            print("📝 Sentence transformers not available - using basic text processing")
            self.embedder = None
            self.embedding_dim = 384
        
        # Collection names
        self.collections = {
            'prompts': 'agentic_prompts',
            'patterns': 'successful_patterns',
            'insights': 'data_insights'
        }
        
        # Initialize collections
        self._setup_collections()
        
        # Performance stats
        self.stats = {
            'cache_hits': 0,
            'similarity_searches': 0,
            'embeddings_created': 0,
            'patterns_stored': 0
        }
    
    def _setup_collections(self):
        """Setup Qdrant collections for different data types"""
        if not self.client:
            raise Exception("Qdrant client not available. Vector database is required for operation.")
            
        for collection_name in self.collections.values():
            try:
                # Check if collection exists
                collections = self.client.get_collections()
                if not any(col.name == collection_name for col in collections.collections):
                    # Create collection
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=self.embedding_dim,
                            distance=Distance.COSINE
                        )
                    )
                    print(f"✅ Created collection: {collection_name}")
                else:
                    print(f"✅ Collection exists: {collection_name}")
                    
            except Exception as e:
                print(f"⚠️ Error setting up collection {collection_name}: {e}")
    
    def _create_embedding(self, text: str) -> List[float]:
        """Create vector embedding for text"""
        if not self.embedder:
            # Create a simple hash-based embedding for Python 3.13 compatibility
            return self._create_simple_embedding(text)
            
        try:
            # Use CPU device explicitly and no_grad for efficiency
            import torch
            with torch.no_grad():
                embedding = self.embedder.encode(text, device='cpu', show_progress_bar=False)
                self.stats['embeddings_created'] += 1
                return embedding.tolist()
        except Exception as e:
            print(f"❌ Error creating embedding: {e}")
            # Fallback to simple embedding
            return self._create_simple_embedding(text)
    
    def _create_simple_embedding(self, text: str) -> List[float]:
        """Create a simple hash-based embedding for Python 3.13 compatibility"""
        import hashlib
        import math
        
        # Create a deterministic hash-based embedding
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # Convert to float values between -1 and 1
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            if len(embedding) >= self.embedding_dim:
                break
                
            # Take 4 bytes and convert to float
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                # Convert to signed integer then normalize
                value = int.from_bytes(chunk, byteorder='big', signed=True)
                normalized = math.tanh(value / (2**31))  # Normalize to [-1, 1]
                embedding.append(normalized)
        
        # Pad or truncate to exact dimension
        while len(embedding) < self.embedding_dim:
            embedding.append(0.0)
        
        return embedding[:self.embedding_dim]
    
    def _data_to_text(self, data: Dict[str, Any]) -> str:
        """Convert input data to searchable text"""
        # Create a normalized text representation of the data
        def flatten_dict(d, prefix=''):
            items = []
            for k, v in d.items():
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, f"{prefix}{k}_"))
                elif isinstance(v, list):
                    items.append(f"{prefix}{k}: {len(v)} items")
                    for i, item in enumerate(v[:3]):  # First 3 items only
                        if isinstance(item, dict):
                            for sk, sv in item.items():
                                items.append(f"{prefix}{k}_{sk}: {sv}")
                        else:
                            items.append(f"{prefix}{k}_{i}: {item}")
                else:
                    items.append(f"{prefix}{k}: {v}")
            return items
        
        text_parts = flatten_dict(data)
        return " ".join(text_parts)
    
    def find_similar_prompts(self, input_data: Dict[str, Any],
                           limit: int = 5,
                           min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find similar prompts using vector similarity search
        """
        if not self.client:
            raise Exception("Vector database not available. Vector database is required for operation.")
            
        try:
            # Convert input data to searchable text
            query_text = self._data_to_text(input_data)
            
            # Create embedding for query
            query_embedding = self._create_embedding(query_text)
            
            # Search in prompts collection
            search_result = self.client.search(
                collection_name=self.collections['prompts'],
                query_vector=query_embedding,
                limit=limit,
                score_threshold=min_similarity
            )
            
            self.stats['similarity_searches'] += 1
            
            # Extract results
            similar_prompts = []
            for hit in search_result:
                if hit.score >= min_similarity:
                    similar_prompts.append({
                        'score': hit.score,
                        'data': hit.payload,
                        'id': hit.id
                    })
                    
            if similar_prompts:
                self.stats['cache_hits'] += 1
                print(f"🎯 Found {len(similar_prompts)} similar prompts (best score: {similar_prompts[0]['score']:.3f})")
            
            return similar_prompts
            
        except Exception as e:
            print(f"⚠️ Error in similarity search: {e}")
            return []
    
    def store_successful_prompt(self, input_data: Dict[str, Any],
                              prompt: str,
                              response: str,
                              metadata: Dict[str, Any],
                              quality_score: float = 1.0):
        """
        Store a successful prompt generation for future similarity matching
        """
        if not self.client:
            raise Exception("Vector database not available. Vector database is required for operation.")
            
        try:
            # Create unique ID based on input data
            data_hash = hashlib.md5(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
            
            # Create searchable text
            search_text = self._data_to_text(input_data)
            
            # Create embedding
            embedding = self._create_embedding(search_text)
            
            # Prepare payload
            payload = {
                'input_data': input_data,
                'prompt': prompt,
                'response': response,
                'metadata': metadata,
                'quality_score': quality_score,
                'timestamp': time.time(),
                'search_text': search_text
            }
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collections['prompts'],
                points=[
                    PointStruct(
                        id=data_hash,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            self.stats['patterns_stored'] += 1
            print(f"💾 Stored successful prompt (ID: {data_hash[:8]})")
            
        except Exception as e:
            print(f"❌ Error storing prompt: {e}")
    
    def find_successful_patterns(self, context: str,
                               data_type: str,
                               limit: int = 3) -> List[Dict[str, Any]]:
        """
        Find successful patterns for specific context and data type
        """
        if not self.client:
            raise Exception("Vector database not available. Vector database is required for operation.")

        try:
            # Search by context and data type in metadata
            search_result = self.client.scroll(
                collection_name=self.collections['prompts'],
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.context",
                            match=models.MatchValue(value=context)
                        ),
                        models.FieldCondition(
                            key="metadata.data_type", 
                            match=models.MatchValue(value=data_type)
                        ),
                        models.FieldCondition(
                            key="quality_score",
                            range=models.Range(gte=0.7)  # High quality only
                        )
                    ]
                ),
                limit=limit,
                with_payload=True
            )
            
            patterns = []
            for point in search_result[0]:
                patterns.append({
                    'score': point.payload.get('quality_score', 0),
                    'data': point.payload,
                    'id': point.id
                })
            
            print(f"🔍 Found {len(patterns)} successful patterns for {context}/{data_type}")
            return patterns
            
        except Exception as e:
            print(f"⚠️ Error finding patterns: {e}")
            return []
    
    def get_optimization_cache(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Quick cache lookup for previously optimized prompts
        """
        if not self.client:
            raise Exception("Vector database not available. Vector database is required for operation.")
            
        try:
            # Create hash for cache key
            data_hash = hashlib.md5(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
            
            # Try to retrieve from cache
            result = self.client.retrieve(
                collection_name=self.collections['prompts'],
                ids=[data_hash],
                with_payload=True
            )
            
            if result:
                self.stats['cache_hits'] += 1
                print(f"⚡ Cache hit for prompt (ID: {data_hash[:8]})")
                return result[0].payload
            
            return None
            
        except Exception as e:
            print(f"⚠️ Cache lookup error: {e}")
            return None
    
    def optimize_with_vectors(self, input_data: Dict[str, Any], 
                            base_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use vector similarity to optimize prompt generation
        """
        start_time = time.time()
        
        # 1. Check exact cache first
        cached_result = self.get_optimization_cache(input_data)
        if cached_result:
            return {
                **base_metadata,
                'vector_optimization': True,
                'cache_hit': True,
                'similar_prompts_found': 1,
                'optimization_time': time.time() - start_time
            }
        
        # 2. Find similar prompts
        similar_prompts = self.find_similar_prompts(input_data, limit=5, min_similarity=0.6)
        
        # 3. Extract successful patterns
        successful_patterns = []
        enhancement_suggestions = set()
        
        for similar in similar_prompts:
            if similar['score'] > 0.7:  # High similarity
                prompt_metadata = similar['data'].get('metadata', {})
                
                # Extract enhancement suggestions
                if 'analysis' in prompt_metadata:
                    analysis = prompt_metadata['analysis']
                    if 'enhancement_suggestions' in analysis:
                        enhancement_suggestions.update(analysis['enhancement_suggestions'])
                
                successful_patterns.append({
                    'score': similar['score'],
                    'context': prompt_metadata.get('context'),
                    'data_type': prompt_metadata.get('data_type'),
                    'generation_mode': prompt_metadata.get('generation_mode')
                })
        
        # 4. Update metadata with vector insights
        optimized_metadata = {
            **base_metadata,
            'vector_optimization': True,
            'cache_hit': False,
            'similar_prompts_found': len(similar_prompts),
            'successful_patterns': successful_patterns,
            'vector_enhancement_suggestions': list(enhancement_suggestions),
            'optimization_time': time.time() - start_time
        }
        
        print(f"🚀 Vector optimization completed in {optimized_metadata['optimization_time']:.3f}s")
        return optimized_metadata
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        try:
            # Get collection stats
            collection_stats = {}
            for name, collection in self.collections.items():
                try:
                    info = self.client.get_collection(collection)
                    collection_stats[name] = {
                        'points_count': info.points_count,
                        'vectors_count': info.vectors_count
                    }
                except:
                    collection_stats[name] = {'points_count': 0, 'vectors_count': 0}
            
            return {
                **self.stats,
                'collections': collection_stats,
                'embedding_dimension': self.embedding_dim,
                'cache_hit_rate': self.stats['cache_hits'] / max(1, self.stats['similarity_searches']),
                'total_stored_patterns': sum(c.get('points_count', 0) for c in collection_stats.values())
            }
            
        except Exception as e:
            print(f"⚠️ Error getting stats: {e}")
            return self.stats
    
    def cleanup_old_patterns(self, max_age_days: int = 30):
        """
        Clean up old patterns to keep the vector database optimized
        """
        if not self.client:
            raise Exception("Vector database not available. Vector database is required for operation.")

        try:
            cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
            
            # Find old points
            old_points = self.client.scroll(
                collection_name=self.collections['prompts'],
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="timestamp",
                            range=models.Range(lt=cutoff_time)
                        )
                    ]
                ),
                limit=1000,
                with_payload=False
            )
            
            if old_points[0]:
                old_ids = [point.id for point in old_points[0]]
                
                # Delete old points
                self.client.delete(
                    collection_name=self.collections['prompts'],
                    points_selector=models.PointIdsList(points=old_ids)
                )
                
                print(f"🧹 Cleaned up {len(old_ids)} old patterns")
            
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")