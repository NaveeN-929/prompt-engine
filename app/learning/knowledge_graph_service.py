"""
Knowledge Graph Service - Multi-collection vector storage for different knowledge types
"""

import time
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    print("⚠️ Qdrant client not available")
    QDRANT_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class KnowledgeGraphService:
    """
    Multi-dimensional knowledge graph using Qdrant vector database
    Stores different knowledge types: prompts, analyses, validations, reasoning patterns
    """
    
    def __init__(self, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.client = None
        self.embedder = None
        self.embedding_dim = 384
        
        # Knowledge collections
        self.collections = {
            'learning_patterns': 'self_learning_patterns',
            'prompt_knowledge': 'prompt_knowledge_base',
            'analysis_knowledge': 'analysis_knowledge_base',
            'validation_knowledge': 'validation_knowledge_base',
            'reasoning_patterns': 'reasoning_pattern_base',
            'cross_component_links': 'cross_component_knowledge'
        }
        
        # Statistics
        self.storage_stats = {
            'total_stored': 0,
            'retrievals': 0,
            'successful_matches': 0
        }
        
        self._initialize()
    
    def _initialize(self):
        """Initialize Qdrant connection and embedding model"""
        
        if not QDRANT_AVAILABLE:
            print("⚠️ Qdrant not available - knowledge graph disabled")
            return
        
        try:
            # Connect to Qdrant
            self.client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
            self.client.get_collections()
            print(f"🔗 Knowledge Graph connected to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
            
            # Initialize embedding model
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                print("✅ Embedding model loaded for knowledge graph")
            else:
                print("📝 Using simple embeddings for knowledge graph")
            
            # Setup collections
            self._setup_knowledge_collections()
            
        except Exception as e:
            print(f"❌ Knowledge graph initialization failed: {e}")
            self.client = None
    
    def _setup_knowledge_collections(self):
        """Setup all knowledge collections in Qdrant"""
        
        if not self.client:
            return
        
        for collection_key, collection_name in self.collections.items():
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
                    print(f"✅ Created knowledge collection: {collection_name}")
                else:
                    print(f"✅ Knowledge collection exists: {collection_name}")
                    
            except Exception as e:
                print(f"⚠️ Error setting up collection {collection_name}: {e}")
    
    def _create_embedding(self, text: str) -> List[float]:
        """Create vector embedding for text"""
        
        if self.embedder:
            try:
                import torch
                with torch.no_grad():
                    embedding = self.embedder.encode(text, device='cpu', show_progress_bar=False)
                    return embedding.tolist()
            except Exception as e:
                print(f"⚠️ Embedding creation failed: {e}")
                return self._create_simple_embedding(text)
        else:
            return self._create_simple_embedding(text)
    
    def _create_simple_embedding(self, text: str) -> List[float]:
        """Create simple hash-based embedding"""
        
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            if len(embedding) >= self.embedding_dim:
                break
            
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                value = int.from_bytes(chunk, byteorder='big', signed=True)
                normalized = np.tanh(value / (2**31))
                embedding.append(float(normalized))
        
        while len(embedding) < self.embedding_dim:
            embedding.append(0.0)
        
        return embedding[:self.embedding_dim]
    
    async def store_learning_pattern(self,
                                    pattern_data: Dict[str, Any],
                                    pattern_type: str,
                                    quality_score: float,
                                    context_tags: List[str]) -> bool:
        """Store a learning pattern in the knowledge graph"""
        
        if not self.client:
            return False
        
        try:
            # Create unique ID
            pattern_id = hashlib.md5(
                json.dumps(pattern_data, sort_keys=True).encode()
            ).hexdigest()
            
            # Create searchable text
            search_text = self._create_search_text(pattern_data)
            
            # Create embedding
            embedding = self._create_embedding(search_text)
            
            # Prepare payload
            payload = {
                'pattern_id': pattern_id,
                'pattern_type': pattern_type,
                'pattern_data': pattern_data,
                'quality_score': quality_score,
                'context_tags': context_tags,
                'search_text': search_text,
                'timestamp': time.time(),
                'use_count': 0
            }
            
            # Store in appropriate collection
            collection_name = self.collections['learning_patterns']
            
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=pattern_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            self.storage_stats['total_stored'] += 1
            print(f"💾 Stored {pattern_type} pattern in knowledge graph (ID: {pattern_id[:8]})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error storing learning pattern: {e}")
            return False
    
    async def store_prompt_knowledge(self,
                                    input_data: Dict[str, Any],
                                    prompt: str,
                                    metadata: Dict[str, Any],
                                    quality_score: float) -> bool:
        """Store prompt generation knowledge"""
        
        if not self.client:
            return False
        
        try:
            knowledge_id = hashlib.md5(
                (prompt + json.dumps(input_data, sort_keys=True)).encode()
            ).hexdigest()
            
            search_text = f"{self._data_to_text(input_data)} {prompt[:500]}"
            embedding = self._create_embedding(search_text)
            
            payload = {
                'knowledge_id': knowledge_id,
                'input_data': input_data,
                'prompt': prompt,
                'metadata': metadata,
                'quality_score': quality_score,
                'timestamp': time.time()
            }
            
            collection_name = self.collections['prompt_knowledge']
            
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=knowledge_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error storing prompt knowledge: {e}")
            return False
    
    async def store_analysis_knowledge(self,
                                      analysis_result: Dict[str, Any],
                                      quality_score: float,
                                      reasoning_chain: Optional[Dict[str, Any]] = None) -> bool:
        """Store analysis knowledge"""
        
        if not self.client:
            return False
        
        try:
            knowledge_id = hashlib.md5(
                json.dumps(analysis_result, sort_keys=True).encode()
            ).hexdigest()
            
            search_text = self._create_search_text(analysis_result)
            embedding = self._create_embedding(search_text)
            
            payload = {
                'knowledge_id': knowledge_id,
                'analysis_result': analysis_result,
                'reasoning_chain': reasoning_chain,
                'quality_score': quality_score,
                'timestamp': time.time()
            }
            
            collection_name = self.collections['analysis_knowledge']
            
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=knowledge_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error storing analysis knowledge: {e}")
            return False
    
    async def store_validation_knowledge(self,
                                        validation_result: Dict[str, Any],
                                        input_data: Dict[str, Any],
                                        response_data: Dict[str, Any]) -> bool:
        """Store validation knowledge"""
        
        if not self.client:
            return False
        
        try:
            knowledge_id = hashlib.md5(
                json.dumps({
                    'validation': validation_result,
                    'input': input_data
                }, sort_keys=True).encode()
            ).hexdigest()
            
            search_text = self._create_search_text(validation_result)
            embedding = self._create_embedding(search_text)
            
            payload = {
                'knowledge_id': knowledge_id,
                'validation_result': validation_result,
                'input_data': input_data,
                'response_data': response_data,
                'quality_score': validation_result.get('overall_score', 0.5),
                'quality_level': validation_result.get('quality_level', 'unknown'),
                'timestamp': time.time()
            }
            
            collection_name = self.collections['validation_knowledge']
            
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=knowledge_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error storing validation knowledge: {e}")
            return False
    
    async def store_reasoning_pattern(self,
                                     reasoning_chain: Dict[str, Any],
                                     input_data: Dict[str, Any],
                                     success_score: float) -> bool:
        """Store successful reasoning patterns"""
        
        if not self.client:
            return False
        
        try:
            pattern_id = hashlib.md5(
                json.dumps(reasoning_chain, sort_keys=True).encode()
            ).hexdigest()
            
            search_text = self._create_search_text(reasoning_chain)
            embedding = self._create_embedding(search_text)
            
            payload = {
                'pattern_id': pattern_id,
                'reasoning_chain': reasoning_chain,
                'input_data': input_data,
                'success_score': success_score,
                'timestamp': time.time()
            }
            
            collection_name = self.collections['reasoning_patterns']
            
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=pattern_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error storing reasoning pattern: {e}")
            return False
    
    async def find_similar_patterns(self,
                                   query_data: Dict[str, Any],
                                   collection_type: str = 'learning_patterns',
                                   limit: int = 5,
                                   min_quality: float = 0.7) -> List[Dict[str, Any]]:
        """Find similar patterns in knowledge graph"""
        
        if not self.client:
            return []
        
        try:
            self.storage_stats['retrievals'] += 1
            
            # Create query embedding
            search_text = self._create_search_text(query_data)
            query_embedding = self._create_embedding(search_text)
            
            # Get collection name
            collection_name = self.collections.get(collection_type, self.collections['learning_patterns'])
            
            # Search
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=0.7
            )
            
            # Filter by quality if applicable
            similar_patterns = []
            for hit in search_result:
                quality_score = hit.payload.get('quality_score', 0.0)
                if quality_score >= min_quality:
                    similar_patterns.append({
                        'score': hit.score,
                        'quality_score': quality_score,
                        'data': hit.payload,
                        'id': hit.id
                    })
            
            if similar_patterns:
                self.storage_stats['successful_matches'] += 1
                print(f"🎯 Found {len(similar_patterns)} similar patterns (best: {similar_patterns[0]['score']:.3f})")
            
            return similar_patterns
            
        except Exception as e:
            print(f"⚠️ Error finding similar patterns: {e}")
            return []
    
    async def link_cross_component_knowledge(self,
                                           prompt_id: str,
                                           analysis_id: str,
                                           validation_id: str,
                                           quality_score: float) -> bool:
        """Create links between different component knowledge"""
        
        if not self.client:
            return False
        
        try:
            link_id = hashlib.md5(
                f"{prompt_id}_{analysis_id}_{validation_id}".encode()
            ).hexdigest()
            
            # Create a combined embedding
            search_text = f"prompt:{prompt_id} analysis:{analysis_id} validation:{validation_id}"
            embedding = self._create_embedding(search_text)
            
            payload = {
                'link_id': link_id,
                'prompt_id': prompt_id,
                'analysis_id': analysis_id,
                'validation_id': validation_id,
                'quality_score': quality_score,
                'timestamp': time.time()
            }
            
            collection_name = self.collections['cross_component_links']
            
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=link_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            print(f"🔗 Created cross-component knowledge link (ID: {link_id[:8]})")
            return True
            
        except Exception as e:
            print(f"❌ Error creating cross-component link: {e}")
            return False
    
    def _create_search_text(self, data: Dict[str, Any]) -> str:
        """Create searchable text from data"""
        
        def extract_text(obj, max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return str(obj)[:100]
            
            if isinstance(obj, dict):
                texts = []
                for k, v in obj.items():
                    texts.append(f"{k}:{extract_text(v, max_depth, current_depth + 1)}")
                return " ".join(texts)
            elif isinstance(obj, list):
                return " ".join(extract_text(item, max_depth, current_depth + 1) for item in obj[:5])
            else:
                return str(obj)[:100]
        
        return extract_text(data)
    
    def _data_to_text(self, data: Dict[str, Any]) -> str:
        """Convert data to text representation"""
        return self._create_search_text(data)
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        
        if not self.client:
            return {'status': 'disabled'}
        
        try:
            collection_stats = {}
            for key, collection_name in self.collections.items():
                try:
                    info = self.client.get_collection(collection_name)
                    collection_stats[key] = {
                        'points_count': info.points_count,
                        'vectors_count': info.vectors_count
                    }
                except:
                    collection_stats[key] = {'points_count': 0, 'vectors_count': 0}
            
            return {
                'status': 'active',
                'collections': collection_stats,
                'storage_stats': self.storage_stats,
                'total_knowledge_points': sum(
                    c.get('points_count', 0) for c in collection_stats.values()
                ),
                'retrieval_success_rate': (
                    self.storage_stats['successful_matches'] / 
                    max(self.storage_stats['retrievals'], 1)
                )
            }
            
        except Exception as e:
            print(f"⚠️ Error getting knowledge stats: {e}")
            return {'status': 'error', 'error': str(e)}

