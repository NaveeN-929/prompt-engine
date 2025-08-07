"""
RAG (Retrieval Augmented Generation) Service with Vector Acceleration
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np
import logging

logger = logging.getLogger(__name__)

class RAGService:
    """
    Advanced RAG service with vector acceleration for knowledge retrieval
    and context augmentation
    """
    
    def __init__(self, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.client = None
        self.embedding_model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        
        # Collection names
        self.collections = {
            "financial_knowledge": "financial_knowledge_base",
            "interaction_patterns": "interaction_patterns",
            "analysis_templates": "analysis_templates",
            "market_data": "market_data_context"
        }
        
        # RAG statistics
        self.total_retrievals = 0
        self.cache_hits = 0
        self.successful_augmentations = 0
        self.vector_searches = 0
        
        # Knowledge cache
        self.knowledge_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def initialize(self):
        """Initialize the RAG service with vector database and embedding model"""
        try:
            logger.info("Initializing RAG service...")
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded (dimension: {self.embedding_dim})")
            
            # Initialize Qdrant client
            try:
                self.client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
                # Test connection
                collections = self.client.get_collections()
                logger.info(f"Connected to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
            except Exception as e:
                logger.warning(f"Qdrant connection failed: {e}, using in-memory mode")
                self.client = QdrantClient(":memory:")
            
            # Create collections
            await self._create_collections()
            
            # Seed with initial knowledge
            await self._seed_financial_knowledge()
            
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    async def _create_collections(self):
        """Create vector collections for different types of knowledge"""
        
        vector_config = VectorParams(size=self.embedding_dim, distance=Distance.COSINE)
        
        for collection_name, qdrant_name in self.collections.items():
            try:
                # Check if collection exists
                existing = self.client.get_collections().collections
                if not any(col.name == qdrant_name for col in existing):
                    self.client.create_collection(
                        collection_name=qdrant_name,
                        vectors_config=vector_config
                    )
                    logger.info(f"Created collection: {qdrant_name}")
                else:
                    logger.info(f"Collection already exists: {qdrant_name}")
                    
            except Exception as e:
                logger.warning(f"Could not create collection {qdrant_name}: {e}")
    
    async def _seed_financial_knowledge(self):
        """Seed the vector database with financial knowledge"""
        
        financial_knowledge = [
            {
                "content": "Cash flow analysis examines the movement of money in and out of a business over a specific period",
                "category": "financial_analysis",
                "type": "definition"
            },
            {
                "content": "Debt-to-income ratio is calculated by dividing total monthly debt payments by gross monthly income",
                "category": "financial_ratios",
                "type": "calculation"
            },
            {
                "content": "A credit utilization ratio below 30% is generally considered good for credit scoring",
                "category": "credit_management",
                "type": "guideline"
            },
            {
                "content": "Emergency funds should typically cover 3-6 months of living expenses for financial security",
                "category": "personal_finance",
                "type": "guideline"
            },
            {
                "content": "Liquidity ratios measure a company's ability to pay short-term obligations without liquidating long-term assets",
                "category": "financial_analysis",
                "type": "definition"
            },
            {
                "content": "Transaction categorization helps identify spending patterns and opportunities for cost optimization",
                "category": "transaction_analysis",
                "type": "insight"
            },
            {
                "content": "Risk assessment should consider both quantitative metrics and qualitative factors",
                "category": "risk_management",
                "type": "best_practice"
            },
            {
                "content": "Seasonal variations in cash flow are common in many businesses and should be factored into analysis",
                "category": "cash_flow",
                "type": "insight"
            }
        ]
        
        collection_name = self.collections["financial_knowledge"]
        
        try:
            # Check if already seeded
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=self.embedding_model.encode("financial analysis").tolist(),
                limit=1
            )
            
            if len(search_result) > 0:
                logger.info("Financial knowledge already seeded")
                return
                
        except:
            pass  # Collection might not exist yet
        
        # Seed knowledge
        points = []
        for i, knowledge in enumerate(financial_knowledge):
            try:
                embedding = self.embedding_model.encode(knowledge["content"])
                
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding.tolist(),
                    payload={
                        "content": knowledge["content"],
                        "category": knowledge["category"],
                        "type": knowledge["type"],
                        "created_at": datetime.now().isoformat(),
                        "source": "seed_data"
                    }
                )
                points.append(point)
                
            except Exception as e:
                logger.warning(f"Could not create point for knowledge {i}: {e}")
        
        if points:
            try:
                self.client.upsert(collection_name=collection_name, points=points)
                logger.info(f"Seeded {len(points)} financial knowledge items")
            except Exception as e:
                logger.warning(f"Could not seed knowledge: {e}")
    
    async def retrieve_context(self, query: str, context_type: str = "general", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from the vector database
        
        Args:
            query: The query text to find relevant context for
            context_type: Type of context to retrieve
            limit: Maximum number of results
            
        Returns:
            List of relevant context items
        """
        self.total_retrievals += 1
        
        try:
            # Check cache first
            cache_key = f"{query}_{context_type}_{limit}"
            cached_result = self._get_cached_context(cache_key)
            if cached_result:
                self.cache_hits += 1
                return cached_result
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Determine collection to search
            collection_map = {
                "financial": "financial_knowledge",
                "analysis": "analysis_templates", 
                "patterns": "interaction_patterns",
                "market": "market_data",
                "general": "financial_knowledge"
            }
            
            collection_key = collection_map.get(context_type, "financial_knowledge")
            collection_name = self.collections[collection_key]
            
            # Perform vector search
            self.vector_searches += 1
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding.tolist(),
                limit=limit,
                score_threshold=0.3  # Minimum similarity threshold
            )
            
            # Format results
            context_items = []
            for result in search_results:
                context_item = {
                    "content": result.payload.get("content", ""),
                    "category": result.payload.get("category", "unknown"),
                    "type": result.payload.get("type", "unknown"),
                    "score": result.score,
                    "source": result.payload.get("source", "vector_db"),
                    "id": result.id
                }
                context_items.append(context_item)
            
            # Cache results
            self._cache_context(cache_key, context_items)
            
            logger.info(f"Retrieved {len(context_items)} context items for query: {query[:50]}")
            return context_items
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    async def augment_prompt(self, original_prompt: str, input_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Augment a prompt with relevant context from RAG
        
        Args:
            original_prompt: The original prompt to augment
            input_data: Input data for context
            
        Returns:
            Tuple of (augmented_prompt, augmentation_metadata)
        """
        try:
            # Extract key concepts from input data and prompt
            analysis_context = self._extract_analysis_context(input_data)
            prompt_concepts = self._extract_prompt_concepts(original_prompt)
            
            # Retrieve relevant context
            financial_context = await self.retrieve_context(
                query=analysis_context, 
                context_type="financial", 
                limit=3
            )
            
            analysis_context_items = await self.retrieve_context(
                query=prompt_concepts,
                context_type="analysis",
                limit=2
            )
            
            # Build augmented prompt
            augmented_prompt = self._build_augmented_prompt(
                original_prompt, financial_context, analysis_context_items, input_data
            )
            
            # Create metadata
            augmentation_metadata = {
                "rag_enabled": True,
                "context_items_used": len(financial_context) + len(analysis_context_items),
                "financial_context_count": len(financial_context),
                "analysis_context_count": len(analysis_context_items),
                "augmentation_timestamp": datetime.now().isoformat(),
                "original_prompt_length": len(original_prompt),
                "augmented_prompt_length": len(augmented_prompt),
                "context_sources": list(set(
                    item["source"] for item in financial_context + analysis_context_items
                ))
            }
            
            self.successful_augmentations += 1
            logger.info(f"Successfully augmented prompt with {augmentation_metadata['context_items_used']} context items")
            
            return augmented_prompt, augmentation_metadata
            
        except Exception as e:
            logger.error(f"Error augmenting prompt: {e}")
            return original_prompt, {"rag_enabled": False, "error": str(e)}
    
    def _extract_analysis_context(self, input_data: Dict[str, Any]) -> str:
        """Extract analysis context from input data"""
        
        context_parts = []
        
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            context_parts.append(f"transaction analysis with {len(transactions)} transactions")
            
            # Extract transaction types
            types = set(tx.get("type", "unknown") for tx in transactions[:5])
            if types:
                context_parts.append(f"transaction types: {', '.join(types)}")
        
        if "account_balance" in input_data:
            context_parts.append("account balance analysis")
        
        if "credit" in str(input_data).lower():
            context_parts.append("credit analysis")
        
        if "loan" in str(input_data).lower():
            context_parts.append("loan analysis")
        
        return " ".join(context_parts) if context_parts else "financial data analysis"
    
    def _extract_prompt_concepts(self, prompt: str) -> str:
        """Extract key concepts from the prompt"""
        
        # Look for key financial terms
        financial_terms = [
            "cash flow", "credit", "debit", "balance", "transaction", "analysis",
            "risk", "assessment", "ratio", "revenue", "expense", "profit", "loss"
        ]
        
        prompt_lower = prompt.lower()
        found_terms = [term for term in financial_terms if term in prompt_lower]
        
        return " ".join(found_terms) if found_terms else "financial analysis"
    
    def _build_augmented_prompt(self, original_prompt: str, 
                               financial_context: List[Dict[str, Any]],
                               analysis_context: List[Dict[str, Any]],
                               input_data: Dict[str, Any]) -> str:
        """Build the final augmented prompt"""
        
        augmented_prompt = f"""
=== RAG-ENHANCED FINANCIAL ANALYSIS ===

**RELEVANT FINANCIAL KNOWLEDGE:**
"""
        
        # Add financial context
        for i, context in enumerate(financial_context, 1):
            augmented_prompt += f"{i}. {context['content']} (Category: {context['category']})\n"
        
        if analysis_context:
            augmented_prompt += f"\n**ANALYSIS BEST PRACTICES:**\n"
            for i, context in enumerate(analysis_context, 1):
                augmented_prompt += f"{i}. {context['content']}\n"
        
        augmented_prompt += f"""
**CONTEXTUAL GUIDANCE:**
- Apply the above knowledge to enhance your analysis
- Use established financial principles and best practices
- Consider industry standards and benchmarks mentioned above
- Ensure your analysis aligns with proven methodologies

=== ORIGINAL ANALYSIS TASK ===
{original_prompt}

=== RAG-ENHANCED INSTRUCTIONS ===
Using the relevant financial knowledge and best practices provided above, perform a comprehensive analysis that:
1. Incorporates established financial principles
2. References appropriate benchmarks and standards
3. Applies proven analytical methodologies
4. Provides context-aware insights based on domain knowledge

Ensure your analysis is grounded in both the provided data and established financial expertise.
"""
        
        return augmented_prompt.strip()
    
    async def store_interaction_pattern(self, input_data: Dict[str, Any], 
                                      prompt: str, response: str, 
                                      quality_score: float):
        """Store successful interaction patterns for future RAG retrieval"""
        
        try:
            if quality_score < 0.7:  # Only store high-quality interactions
                return
            
            # Create pattern description
            pattern_content = f"Successful analysis of {self._describe_input_data(input_data)}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(pattern_content)
            
            # Store in patterns collection
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={
                    "content": pattern_content,
                    "input_summary": self._summarize_input_data(input_data),
                    "prompt_type": self._classify_prompt_type(prompt),
                    "response_length": len(response),
                    "quality_score": quality_score,
                    "created_at": datetime.now().isoformat(),
                    "source": "interaction_pattern"
                }
            )
            
            self.client.upsert(
                collection_name=self.collections["interaction_patterns"],
                points=[point]
            )
            
            logger.info(f"Stored interaction pattern with quality score {quality_score}")
            
        except Exception as e:
            logger.warning(f"Could not store interaction pattern: {e}")
    
    def _describe_input_data(self, input_data: Dict[str, Any]) -> str:
        """Create a description of input data for pattern storage"""
        
        description_parts = []
        
        if "transactions" in input_data:
            tx_count = len(input_data["transactions"])
            description_parts.append(f"{tx_count} transactions")
        
        if "account_balance" in input_data:
            description_parts.append("account balance data")
        
        # Look for specific financial contexts
        data_str = json.dumps(input_data, default=str).lower()
        
        if "credit" in data_str:
            description_parts.append("credit-related data")
        if "loan" in data_str:
            description_parts.append("loan data")
        if "card" in data_str:
            description_parts.append("card transaction data")
        
        return ", ".join(description_parts) if description_parts else "financial data"
    
    def _summarize_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of input data"""
        return {
            "keys": list(input_data.keys()),
            "transaction_count": len(input_data.get("transactions", [])),
            "has_balance": "account_balance" in input_data,
            "data_size": len(str(input_data))
        }
    
    def _classify_prompt_type(self, prompt: str) -> str:
        """Classify the type of prompt"""
        
        prompt_lower = prompt.lower()
        
        if "cash flow" in prompt_lower:
            return "cash_flow_analysis"
        elif "credit" in prompt_lower:
            return "credit_analysis"
        elif "risk" in prompt_lower:
            return "risk_assessment"
        elif "transaction" in prompt_lower:
            return "transaction_analysis"
        else:
            return "general_analysis"
    
    def _get_cached_context(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached context if available and not expired"""
        
        if cache_key in self.knowledge_cache:
            cached_item = self.knowledge_cache[cache_key]
            if time.time() - cached_item["timestamp"] < self.cache_ttl:
                return cached_item["context"]
            else:
                del self.knowledge_cache[cache_key]
        
        return None
    
    def _cache_context(self, cache_key: str, context: List[Dict[str, Any]]):
        """Cache context for future use"""
        
        self.knowledge_cache[cache_key] = {
            "context": context,
            "timestamp": time.time()
        }
        
        # Limit cache size
        if len(self.knowledge_cache) > 100:
            # Remove oldest entries
            sorted_cache = sorted(
                self.knowledge_cache.items(),
                key=lambda x: x[1]["timestamp"]
            )
            self.knowledge_cache = dict(sorted_cache[-80:])
    
    def get_rag_statistics(self) -> Dict[str, Any]:
        """Get RAG service statistics"""
        
        return {
            "total_retrievals": self.total_retrievals,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.cache_hits / max(self.total_retrievals, 1),
            "successful_augmentations": self.successful_augmentations,
            "vector_searches": self.vector_searches,
            "knowledge_cache_size": len(self.knowledge_cache),
            "collections": list(self.collections.keys()),
            "embedding_dimension": self.embedding_dim,
            "vector_database": {
                "host": self.qdrant_host,
                "port": self.qdrant_port,
                "status": "connected" if self.client else "disconnected"
            }
        }
    
    async def get_vector_status(self) -> Dict[str, Any]:
        """Get detailed vector database status"""
        
        try:
            if not self.client:
                return {"status": "disconnected", "error": "No client available"}
            
            # Get collections info
            collections_info = []
            collections = self.client.get_collections()
            
            for collection in collections.collections:
                try:
                    collection_info = self.client.get_collection(collection.name)
                    collections_info.append({
                        "name": collection.name,
                        "points_count": collection_info.points_count,
                        "vectors_count": collection_info.vectors_count if hasattr(collection_info, 'vectors_count') else 0,
                        "status": "active"
                    })
                except Exception as e:
                    collections_info.append({
                        "name": collection.name,
                        "error": str(e),
                        "status": "error"
                    })
            
            return {
                "status": "connected",
                "host": self.qdrant_host,
                "port": self.qdrant_port,
                "total_collections": len(collections.collections),
                "configured_collections": list(self.collections.values()),
                "collections_detail": collections_info,
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimension": self.embedding_dim
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "host": self.qdrant_host,
                "port": self.qdrant_port
            }
RAG (Retrieval Augmented Generation) Service with Vector Acceleration
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np
import logging

logger = logging.getLogger(__name__)

class RAGService:
    """
    Advanced RAG service with vector acceleration for knowledge retrieval
    and context augmentation
    """
    
    def __init__(self, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.client = None
        self.embedding_model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        
        # Collection names
        self.collections = {
            "financial_knowledge": "financial_knowledge_base",
            "interaction_patterns": "interaction_patterns",
            "analysis_templates": "analysis_templates",
            "market_data": "market_data_context"
        }
        
        # RAG statistics
        self.total_retrievals = 0
        self.cache_hits = 0
        self.successful_augmentations = 0
        self.vector_searches = 0
        
        # Knowledge cache
        self.knowledge_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def initialize(self):
        """Initialize the RAG service with vector database and embedding model"""
        try:
            logger.info("Initializing RAG service...")
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded (dimension: {self.embedding_dim})")
            
            # Initialize Qdrant client
            try:
                self.client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
                # Test connection
                collections = self.client.get_collections()
                logger.info(f"Connected to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
            except Exception as e:
                logger.warning(f"Qdrant connection failed: {e}, using in-memory mode")
                self.client = QdrantClient(":memory:")
            
            # Create collections
            await self._create_collections()
            
            # Seed with initial knowledge
            await self._seed_financial_knowledge()
            
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    async def _create_collections(self):
        """Create vector collections for different types of knowledge"""
        
        vector_config = VectorParams(size=self.embedding_dim, distance=Distance.COSINE)
        
        for collection_name, qdrant_name in self.collections.items():
            try:
                # Check if collection exists
                existing = self.client.get_collections().collections
                if not any(col.name == qdrant_name for col in existing):
                    self.client.create_collection(
                        collection_name=qdrant_name,
                        vectors_config=vector_config
                    )
                    logger.info(f"Created collection: {qdrant_name}")
                else:
                    logger.info(f"Collection already exists: {qdrant_name}")
                    
            except Exception as e:
                logger.warning(f"Could not create collection {qdrant_name}: {e}")
    
    async def _seed_financial_knowledge(self):
        """Seed the vector database with financial knowledge"""
        
        financial_knowledge = [
            {
                "content": "Cash flow analysis examines the movement of money in and out of a business over a specific period",
                "category": "financial_analysis",
                "type": "definition"
            },
            {
                "content": "Debt-to-income ratio is calculated by dividing total monthly debt payments by gross monthly income",
                "category": "financial_ratios",
                "type": "calculation"
            },
            {
                "content": "A credit utilization ratio below 30% is generally considered good for credit scoring",
                "category": "credit_management",
                "type": "guideline"
            },
            {
                "content": "Emergency funds should typically cover 3-6 months of living expenses for financial security",
                "category": "personal_finance",
                "type": "guideline"
            },
            {
                "content": "Liquidity ratios measure a company's ability to pay short-term obligations without liquidating long-term assets",
                "category": "financial_analysis",
                "type": "definition"
            },
            {
                "content": "Transaction categorization helps identify spending patterns and opportunities for cost optimization",
                "category": "transaction_analysis",
                "type": "insight"
            },
            {
                "content": "Risk assessment should consider both quantitative metrics and qualitative factors",
                "category": "risk_management",
                "type": "best_practice"
            },
            {
                "content": "Seasonal variations in cash flow are common in many businesses and should be factored into analysis",
                "category": "cash_flow",
                "type": "insight"
            }
        ]
        
        collection_name = self.collections["financial_knowledge"]
        
        try:
            # Check if already seeded
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=self.embedding_model.encode("financial analysis").tolist(),
                limit=1
            )
            
            if len(search_result) > 0:
                logger.info("Financial knowledge already seeded")
                return
                
        except:
            pass  # Collection might not exist yet
        
        # Seed knowledge
        points = []
        for i, knowledge in enumerate(financial_knowledge):
            try:
                embedding = self.embedding_model.encode(knowledge["content"])
                
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding.tolist(),
                    payload={
                        "content": knowledge["content"],
                        "category": knowledge["category"],
                        "type": knowledge["type"],
                        "created_at": datetime.now().isoformat(),
                        "source": "seed_data"
                    }
                )
                points.append(point)
                
            except Exception as e:
                logger.warning(f"Could not create point for knowledge {i}: {e}")
        
        if points:
            try:
                self.client.upsert(collection_name=collection_name, points=points)
                logger.info(f"Seeded {len(points)} financial knowledge items")
            except Exception as e:
                logger.warning(f"Could not seed knowledge: {e}")
    
    async def retrieve_context(self, query: str, context_type: str = "general", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from the vector database
        
        Args:
            query: The query text to find relevant context for
            context_type: Type of context to retrieve
            limit: Maximum number of results
            
        Returns:
            List of relevant context items
        """
        self.total_retrievals += 1
        
        try:
            # Check cache first
            cache_key = f"{query}_{context_type}_{limit}"
            cached_result = self._get_cached_context(cache_key)
            if cached_result:
                self.cache_hits += 1
                return cached_result
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Determine collection to search
            collection_map = {
                "financial": "financial_knowledge",
                "analysis": "analysis_templates", 
                "patterns": "interaction_patterns",
                "market": "market_data",
                "general": "financial_knowledge"
            }
            
            collection_key = collection_map.get(context_type, "financial_knowledge")
            collection_name = self.collections[collection_key]
            
            # Perform vector search
            self.vector_searches += 1
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding.tolist(),
                limit=limit,
                score_threshold=0.3  # Minimum similarity threshold
            )
            
            # Format results
            context_items = []
            for result in search_results:
                context_item = {
                    "content": result.payload.get("content", ""),
                    "category": result.payload.get("category", "unknown"),
                    "type": result.payload.get("type", "unknown"),
                    "score": result.score,
                    "source": result.payload.get("source", "vector_db"),
                    "id": result.id
                }
                context_items.append(context_item)
            
            # Cache results
            self._cache_context(cache_key, context_items)
            
            logger.info(f"Retrieved {len(context_items)} context items for query: {query[:50]}")
            return context_items
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    async def augment_prompt(self, original_prompt: str, input_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Augment a prompt with relevant context from RAG
        
        Args:
            original_prompt: The original prompt to augment
            input_data: Input data for context
            
        Returns:
            Tuple of (augmented_prompt, augmentation_metadata)
        """
        try:
            # Extract key concepts from input data and prompt
            analysis_context = self._extract_analysis_context(input_data)
            prompt_concepts = self._extract_prompt_concepts(original_prompt)
            
            # Retrieve relevant context
            financial_context = await self.retrieve_context(
                query=analysis_context, 
                context_type="financial", 
                limit=3
            )
            
            analysis_context_items = await self.retrieve_context(
                query=prompt_concepts,
                context_type="analysis",
                limit=2
            )
            
            # Build augmented prompt
            augmented_prompt = self._build_augmented_prompt(
                original_prompt, financial_context, analysis_context_items, input_data
            )
            
            # Create metadata
            augmentation_metadata = {
                "rag_enabled": True,
                "context_items_used": len(financial_context) + len(analysis_context_items),
                "financial_context_count": len(financial_context),
                "analysis_context_count": len(analysis_context_items),
                "augmentation_timestamp": datetime.now().isoformat(),
                "original_prompt_length": len(original_prompt),
                "augmented_prompt_length": len(augmented_prompt),
                "context_sources": list(set(
                    item["source"] for item in financial_context + analysis_context_items
                ))
            }
            
            self.successful_augmentations += 1
            logger.info(f"Successfully augmented prompt with {augmentation_metadata['context_items_used']} context items")
            
            return augmented_prompt, augmentation_metadata
            
        except Exception as e:
            logger.error(f"Error augmenting prompt: {e}")
            return original_prompt, {"rag_enabled": False, "error": str(e)}
    
    def _extract_analysis_context(self, input_data: Dict[str, Any]) -> str:
        """Extract analysis context from input data"""
        
        context_parts = []
        
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            context_parts.append(f"transaction analysis with {len(transactions)} transactions")
            
            # Extract transaction types
            types = set(tx.get("type", "unknown") for tx in transactions[:5])
            if types:
                context_parts.append(f"transaction types: {', '.join(types)}")
        
        if "account_balance" in input_data:
            context_parts.append("account balance analysis")
        
        if "credit" in str(input_data).lower():
            context_parts.append("credit analysis")
        
        if "loan" in str(input_data).lower():
            context_parts.append("loan analysis")
        
        return " ".join(context_parts) if context_parts else "financial data analysis"
    
    def _extract_prompt_concepts(self, prompt: str) -> str:
        """Extract key concepts from the prompt"""
        
        # Look for key financial terms
        financial_terms = [
            "cash flow", "credit", "debit", "balance", "transaction", "analysis",
            "risk", "assessment", "ratio", "revenue", "expense", "profit", "loss"
        ]
        
        prompt_lower = prompt.lower()
        found_terms = [term for term in financial_terms if term in prompt_lower]
        
        return " ".join(found_terms) if found_terms else "financial analysis"
    
    def _build_augmented_prompt(self, original_prompt: str, 
                               financial_context: List[Dict[str, Any]],
                               analysis_context: List[Dict[str, Any]],
                               input_data: Dict[str, Any]) -> str:
        """Build the final augmented prompt"""
        
        augmented_prompt = f"""
=== RAG-ENHANCED FINANCIAL ANALYSIS ===

**RELEVANT FINANCIAL KNOWLEDGE:**
"""
        
        # Add financial context
        for i, context in enumerate(financial_context, 1):
            augmented_prompt += f"{i}. {context['content']} (Category: {context['category']})\n"
        
        if analysis_context:
            augmented_prompt += f"\n**ANALYSIS BEST PRACTICES:**\n"
            for i, context in enumerate(analysis_context, 1):
                augmented_prompt += f"{i}. {context['content']}\n"
        
        augmented_prompt += f"""
**CONTEXTUAL GUIDANCE:**
- Apply the above knowledge to enhance your analysis
- Use established financial principles and best practices
- Consider industry standards and benchmarks mentioned above
- Ensure your analysis aligns with proven methodologies

=== ORIGINAL ANALYSIS TASK ===
{original_prompt}

=== RAG-ENHANCED INSTRUCTIONS ===
Using the relevant financial knowledge and best practices provided above, perform a comprehensive analysis that:
1. Incorporates established financial principles
2. References appropriate benchmarks and standards
3. Applies proven analytical methodologies
4. Provides context-aware insights based on domain knowledge

Ensure your analysis is grounded in both the provided data and established financial expertise.
"""
        
        return augmented_prompt.strip()
    
    async def store_interaction_pattern(self, input_data: Dict[str, Any], 
                                      prompt: str, response: str, 
                                      quality_score: float):
        """Store successful interaction patterns for future RAG retrieval"""
        
        try:
            if quality_score < 0.7:  # Only store high-quality interactions
                return
            
            # Create pattern description
            pattern_content = f"Successful analysis of {self._describe_input_data(input_data)}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(pattern_content)
            
            # Store in patterns collection
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={
                    "content": pattern_content,
                    "input_summary": self._summarize_input_data(input_data),
                    "prompt_type": self._classify_prompt_type(prompt),
                    "response_length": len(response),
                    "quality_score": quality_score,
                    "created_at": datetime.now().isoformat(),
                    "source": "interaction_pattern"
                }
            )
            
            self.client.upsert(
                collection_name=self.collections["interaction_patterns"],
                points=[point]
            )
            
            logger.info(f"Stored interaction pattern with quality score {quality_score}")
            
        except Exception as e:
            logger.warning(f"Could not store interaction pattern: {e}")
    
    def _describe_input_data(self, input_data: Dict[str, Any]) -> str:
        """Create a description of input data for pattern storage"""
        
        description_parts = []
        
        if "transactions" in input_data:
            tx_count = len(input_data["transactions"])
            description_parts.append(f"{tx_count} transactions")
        
        if "account_balance" in input_data:
            description_parts.append("account balance data")
        
        # Look for specific financial contexts
        data_str = json.dumps(input_data, default=str).lower()
        
        if "credit" in data_str:
            description_parts.append("credit-related data")
        if "loan" in data_str:
            description_parts.append("loan data")
        if "card" in data_str:
            description_parts.append("card transaction data")
        
        return ", ".join(description_parts) if description_parts else "financial data"
    
    def _summarize_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of input data"""
        return {
            "keys": list(input_data.keys()),
            "transaction_count": len(input_data.get("transactions", [])),
            "has_balance": "account_balance" in input_data,
            "data_size": len(str(input_data))
        }
    
    def _classify_prompt_type(self, prompt: str) -> str:
        """Classify the type of prompt"""
        
        prompt_lower = prompt.lower()
        
        if "cash flow" in prompt_lower:
            return "cash_flow_analysis"
        elif "credit" in prompt_lower:
            return "credit_analysis"
        elif "risk" in prompt_lower:
            return "risk_assessment"
        elif "transaction" in prompt_lower:
            return "transaction_analysis"
        else:
            return "general_analysis"
    
    def _get_cached_context(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached context if available and not expired"""
        
        if cache_key in self.knowledge_cache:
            cached_item = self.knowledge_cache[cache_key]
            if time.time() - cached_item["timestamp"] < self.cache_ttl:
                return cached_item["context"]
            else:
                del self.knowledge_cache[cache_key]
        
        return None
    
    def _cache_context(self, cache_key: str, context: List[Dict[str, Any]]):
        """Cache context for future use"""
        
        self.knowledge_cache[cache_key] = {
            "context": context,
            "timestamp": time.time()
        }
        
        # Limit cache size
        if len(self.knowledge_cache) > 100:
            # Remove oldest entries
            sorted_cache = sorted(
                self.knowledge_cache.items(),
                key=lambda x: x[1]["timestamp"]
            )
            self.knowledge_cache = dict(sorted_cache[-80:])
    
    def get_rag_statistics(self) -> Dict[str, Any]:
        """Get RAG service statistics"""
        
        return {
            "total_retrievals": self.total_retrievals,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.cache_hits / max(self.total_retrievals, 1),
            "successful_augmentations": self.successful_augmentations,
            "vector_searches": self.vector_searches,
            "knowledge_cache_size": len(self.knowledge_cache),
            "collections": list(self.collections.keys()),
            "embedding_dimension": self.embedding_dim,
            "vector_database": {
                "host": self.qdrant_host,
                "port": self.qdrant_port,
                "status": "connected" if self.client else "disconnected"
            }
        }
    
    async def get_vector_status(self) -> Dict[str, Any]:
        """Get detailed vector database status"""
        
        try:
            if not self.client:
                return {"status": "disconnected", "error": "No client available"}
            
            # Get collections info
            collections_info = []
            collections = self.client.get_collections()
            
            for collection in collections.collections:
                try:
                    collection_info = self.client.get_collection(collection.name)
                    collections_info.append({
                        "name": collection.name,
                        "points_count": collection_info.points_count,
                        "vectors_count": collection_info.vectors_count if hasattr(collection_info, 'vectors_count') else 0,
                        "status": "active"
                    })
                except Exception as e:
                    collections_info.append({
                        "name": collection.name,
                        "error": str(e),
                        "status": "error"
                    })
            
            return {
                "status": "connected",
                "host": self.qdrant_host,
                "port": self.qdrant_port,
                "total_collections": len(collections.collections),
                "configured_collections": list(self.collections.values()),
                "collections_detail": collections_info,
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimension": self.embedding_dim
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "host": self.qdrant_host,
                "port": self.qdrant_port
            }