"""
Prompt Consumer Service - Interfaces with the Prompt Engine
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging

from config import get_config

logger = logging.getLogger(__name__)

class PromptConsumerService:
    """
    Service that consumes optimized prompts from the prompt-engine
    and prepares them for autonomous processing
    """
    
    def __init__(self):
        self.config = get_config()
        self.prompt_engine_url = self.config["prompt_engine"]["url"]
        self.endpoints = self.config["prompt_engine"]["endpoints"]
        self.session = None
        
        # Statistics and monitoring
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_processing_time = 0.0
        
        # Cache for frequently used prompts
        self.prompt_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Content-Type": "application/json"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def consume_prompt(self, 
                           input_data: Dict[str, Any],
                           generation_type: str = "standard",
                           context: Optional[str] = None,
                           data_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Consume an optimized prompt from the prompt-engine
        
        Args:
            input_data: The financial data to analyze
            generation_type: Type of generation (standard, reasoning, autonomous, optimize)
            context: Optional context hint
            data_type: Optional data type hint
            
        Returns:
            Dictionary containing prompt and metadata
        """
        start_time = time.time()
        
        try:
            self.request_count += 1
            
            # Check cache first
            cache_key = self._generate_cache_key(input_data, generation_type, context, data_type)
            cached_result = self._get_cached_prompt(cache_key)
            if cached_result:
                logger.info("Using cached prompt for similar input")
                return cached_result
            
            # Prepare request payload
            payload = {
                "input_data": input_data,
                "generation_type": generation_type
            }
            
            if context:
                payload["context"] = context
            if data_type:
                payload["data_type"] = data_type
            
            # Make request to prompt engine
            url = f"{self.prompt_engine_url}{self.endpoints['generate']}"
            
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Enhance the result with consumer metadata
                    enhanced_result = self._enhance_prompt_result(result, input_data)
                    
                    # Cache the result
                    self._cache_prompt(cache_key, enhanced_result)
                    
                    self.success_count += 1
                    processing_time = time.time() - start_time
                    self.total_processing_time += processing_time
                    
                    logger.info(f"Successfully consumed prompt in {processing_time:.3f}s")
                    return enhanced_result
                    
                else:
                    error_text = await response.text()
                    raise Exception(f"Prompt engine error {response.status}: {error_text}")
                    
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error consuming prompt: {e}")
            
            # Fallback to basic prompt generation
            return self._generate_fallback_prompt(input_data, generation_type)
    
    async def analyze_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use the prompt engine's analysis capabilities to understand input data
        
        Args:
            input_data: The data to analyze
            
        Returns:
            Analysis results from prompt engine
        """
        try:
            url = f"{self.prompt_engine_url}{self.endpoints['analyze']}"
            payload = {"input_data": input_data}
            
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("Successfully analyzed input data")
                    return result["analysis"]
                else:
                    error_text = await response.text()
                    logger.warning(f"Analysis failed {response.status}: {error_text}")
                    return self._fallback_analysis(input_data)
                    
        except Exception as e:
            logger.error(f"Error analyzing input data: {e}")
            return self._fallback_analysis(input_data)
    
    async def get_prompt_engine_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the connected prompt engine
        
        Returns:
            Capabilities dictionary
        """
        try:
            url = f"{self.prompt_engine_url}{self.endpoints['capabilities']}"
            
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("Retrieved prompt engine capabilities")
                    return result
                else:
                    logger.warning(f"Failed to get capabilities: {response.status}")
                    return {"error": "capabilities_unavailable"}
                    
        except Exception as e:
            logger.error(f"Error getting capabilities: {e}")
            return {"error": str(e)}
    
    async def submit_learning_feedback(self, 
                                     input_data: Dict[str, Any],
                                     prompt_result: str,
                                     agent_response: str,
                                     quality_score: float,
                                     user_feedback: Optional[str] = None) -> bool:
        """
        Submit learning feedback to the prompt engine to improve future prompts
        
        Args:
            input_data: Original input data
            prompt_result: The prompt that was generated
            agent_response: The agent's response to the prompt
            quality_score: Quality score (0.0 to 1.0)
            user_feedback: Optional user feedback
            
        Returns:
            True if feedback was successfully submitted
        """
        try:
            url = f"{self.prompt_engine_url}{self.endpoints['learn']}"
            payload = {
                "input_data": input_data,
                "prompt_result": prompt_result,
                "llm_response": agent_response,
                "quality_score": quality_score
            }
            
            if user_feedback:
                payload["user_feedback"] = user_feedback
            
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Successfully submitted learning feedback (quality: {quality_score})")
                    return True
                else:
                    logger.warning(f"Failed to submit feedback: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error submitting learning feedback: {e}")
            return False
    
    def _generate_cache_key(self, input_data: Dict[str, Any], 
                          generation_type: str, 
                          context: Optional[str],
                          data_type: Optional[str]) -> str:
        """Generate a cache key for the request"""
        key_data = {
            "data_hash": hash(str(sorted(input_data.items()))),
            "generation_type": generation_type,
            "context": context,
            "data_type": data_type
        }
        return f"prompt_{hash(str(key_data))}"
    
    def _get_cached_prompt(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached prompt if available and not expired"""
        if cache_key in self.prompt_cache:
            cached_item = self.prompt_cache[cache_key]
            if time.time() - cached_item["timestamp"] < self.cache_ttl:
                return cached_item["result"]
            else:
                # Remove expired cache entry
                del self.prompt_cache[cache_key]
        return None
    
    def _cache_prompt(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache a prompt result"""
        self.prompt_cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
        
        # Limit cache size
        if len(self.prompt_cache) > 100:
            # Remove oldest entries
            sorted_cache = sorted(self.prompt_cache.items(), 
                                key=lambda x: x[1]["timestamp"])
            self.prompt_cache = dict(sorted_cache[-80:])
    
    def _enhance_prompt_result(self, result: Dict[str, Any], 
                             input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance the prompt result with additional metadata for autonomous processing
        """
        enhanced = result.copy()
        
        # Add autonomous processing metadata
        enhanced["autonomous_metadata"] = {
            "consumed_at": datetime.now().isoformat(),
            "consumer_version": "1.0.0",
            "input_data_summary": self._summarize_input_data(input_data),
            "prompt_confidence": self._estimate_prompt_confidence(result),
            "processing_hints": self._generate_processing_hints(result, input_data)
        }
        
        return enhanced
    
    def _summarize_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the input data"""
        summary = {
            "data_size": len(str(input_data)),
            "top_level_keys": list(input_data.keys()),
            "has_transactions": "transactions" in input_data,
            "has_account_data": any(key in input_data for key in ["account", "balance", "customer"]),
            "complexity": "simple" if len(input_data) < 5 else "complex"
        }
        
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            if isinstance(transactions, list):
                summary["transaction_count"] = len(transactions)
                summary["date_range"] = self._extract_date_range(transactions)
        
        return summary
    
    def _estimate_prompt_confidence(self, result: Dict[str, Any]) -> float:
        """Estimate confidence in the generated prompt"""
        confidence = 0.7  # Base confidence
        
        # Higher confidence for vector-accelerated prompts
        if result.get("vector_accelerated"):
            confidence += 0.2
        
        # Higher confidence for agentic mode
        metadata = result.get("agentic_metadata", {})
        if metadata.get("generation_mode") == "agentic_enhanced":
            confidence += 0.1
        
        # Consider processing time (faster usually means more confident)
        processing_time = result.get("processing_time", 1.0)
        if processing_time < 0.5:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_processing_hints(self, result: Dict[str, Any], 
                                 input_data: Dict[str, Any]) -> List[str]:
        """Generate hints for autonomous processing"""
        hints = []
        
        metadata = result.get("agentic_metadata", {})
        
        if metadata.get("vector_accelerated"):
            hints.append("Use vector similarity patterns for validation")
        
        if metadata.get("context") == "core_banking":
            hints.append("Focus on transaction patterns and financial metrics")
        
        if "reasoning" in metadata.get("generation_mode", ""):
            hints.append("Apply multi-step reasoning validation")
        
        if metadata.get("data_complexity") == "complex":
            hints.append("Break down analysis into manageable chunks")
        
        return hints
    
    def _extract_date_range(self, transactions: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Extract date range from transactions"""
        try:
            dates = []
            for tx in transactions:
                if "date" in tx:
                    dates.append(tx["date"])
            
            if dates:
                return {
                    "start": min(dates),
                    "end": max(dates),
                    "span_days": len(set(dates))
                }
        except:
            pass
        
        return None
    
    def _generate_fallback_prompt(self, input_data: Dict[str, Any], 
                                generation_type: str) -> Dict[str, Any]:
        """Generate a basic fallback prompt when prompt engine is unavailable"""
        
        fallback_prompt = f"""
        Analyze the following financial data autonomously and provide comprehensive insights.
        
        **Data to Analyze:**
        {json.dumps(input_data, indent=2)}
        
        **Analysis Requirements:**
        - Perform thorough data validation
        - Identify key patterns and trends
        - Calculate relevant financial metrics
        - Provide risk assessment
        - Generate actionable recommendations
        - Include confidence levels for all findings
        
        **Important:** Base all analysis strictly on the provided data. Do not make assumptions beyond what the data supports.
        """
        
        return {
            "prompt": fallback_prompt,
            "agentic_metadata": {
                "template_used": "fallback_autonomous",
                "generation_mode": "fallback",
                "context": "auto_inferred",
                "data_type": "autonomous"
            },
            "processing_time": 0.1,
            "vector_accelerated": False,
            "autonomous_metadata": {
                "consumed_at": datetime.now().isoformat(),
                "consumer_version": "1.0.0",
                "fallback_reason": "prompt_engine_unavailable",
                "prompt_confidence": 0.5
            }
        }
    
    def _fallback_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide basic analysis when prompt engine analysis fails"""
        return {
            "data_complexity": "unknown",
            "data_volume": "unknown",
            "contains_financial_terms": any(
                term in str(input_data).lower() 
                for term in ["amount", "transaction", "balance", "payment"]
            ),
            "suggested_context": "core_banking",
            "suggested_data_type": "transaction_history" if "transactions" in input_data else "unknown",
            "key_insights": ["Fallback analysis - detailed analysis unavailable"],
            "enhancement_suggestions": ["Use manual analysis approach"]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get consumer service statistics"""
        return {
            "request_count": self.request_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / max(self.request_count, 1),
            "average_processing_time": self.total_processing_time / max(self.success_count, 1),
            "cache_size": len(self.prompt_cache),
            "cache_hit_rate": 0.0  # TODO: Implement cache hit tracking
        }