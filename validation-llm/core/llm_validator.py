"""
LLM Validator - Uses secondary LLM to validate autonomous agent responses
"""

import asyncio
import json
import re
import time
from typing import Dict, Any, Optional, List
import logging
import requests
from datetime import datetime

from config import get_config, get_validation_prompt

logger = logging.getLogger(__name__)

class LLMValidator:
    """
    Uses a secondary LLM to validate responses from the autonomous agent
    across multiple quality criteria
    """
    
    def __init__(self):
        self.config = get_config()
        self.llm_config = self.config["validation_llm"]["primary_validator"]
        self.speed_llm_config = self.config["validation_llm"]["speed_validator"]
        
        # HTTP session for LLM requests
        self.session = requests.Session()
        self.session.timeout = self.llm_config["timeout"]
        
        # Validation statistics
        self.total_validations = 0
        self.successful_validations = 0
        self.failed_validations = 0
        self.average_response_time = 0.0
        
        # Response caching for efficiency
        self.response_cache = {}
        self.cache_hits = 0
        
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the LLM validator"""
        try:
            logger.info("Initializing LLM Validator...")
            
            # Test connection to validation LLM - REQUIRED, no fallbacks
            connection_test = await self._test_llm_connection()
            if not connection_test["available"]:
                raise RuntimeError(f"Cannot connect to validation LLM: {connection_test['error']}. Please ensure Ollama is running and models are available.")
            
            logger.info(f"Connected to validation LLM: {self.llm_config['model_name']}")
            
            self.is_initialized = True
            logger.info("LLM Validator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM validator: {e}")
            raise
    
    async def validate_criterion(self, 
                                criterion: str,
                                response_text: str,
                                input_data: Dict[str, Any],
                                use_speed_model: bool = False) -> Dict[str, Any]:
        """
        Validate a response against a specific criterion using LLM
        
        Args:
            criterion: The validation criterion to evaluate
            response_text: The response text to validate
            input_data: Original input data for context
            use_speed_model: Whether to use the faster model
            
        Returns:
            Validation result with score and explanation
        """
        if not self.is_initialized:
            raise RuntimeError("LLM Validator not initialized")
        
        self.total_validations += 1
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(criterion, response_text, input_data)
            if cache_key in self.response_cache:
                self.cache_hits += 1
                return self.response_cache[cache_key]
            
            # Get validation prompt for criterion
            prompt_template = get_validation_prompt(criterion)
            if not prompt_template:
                raise ValueError(f"No validation prompt found for criterion: {criterion}")
            
            # Prepare the validation prompt
            validation_prompt = prompt_template.format(
                response=response_text,
                input_data=json.dumps(input_data, indent=2, default=str)
            )
            
            # Select LLM configuration
            llm_config = self.speed_llm_config if use_speed_model else self.llm_config
            
            # Generate validation response
            llm_response = await self._generate_llm_response(validation_prompt, llm_config)
            
            # Parse validation result
            validation_result = self._parse_validation_response(llm_response, criterion)
            
            processing_time = time.time() - start_time
            validation_result["processing_time"] = processing_time
            
            # Update statistics
            self._update_response_time(processing_time)
            self.successful_validations += 1
            
            # Cache result
            self.response_cache[cache_key] = validation_result
            if len(self.response_cache) > 1000:
                self._cleanup_cache()
            
            logger.debug(f"Validated {criterion}: score={validation_result['score']:.3f}, time={processing_time:.3f}s")
            
            return validation_result
            
        except Exception as e:
            self.failed_validations += 1
            logger.error(f"Validation failed for {criterion}: {e}")
            
            # No fallbacks - raise the error to be handled upstream
            raise RuntimeError(f"Validation failed for {criterion}: {e}. Cannot provide fallback validation.")
    
    async def validate_multiple_criteria(self,
                                       criteria: List[str],
                                       response_text: str,
                                       input_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Validate response against multiple criteria concurrently
        
        Args:
            criteria: List of criteria to validate
            response_text: The response text to validate
            input_data: Original input data for context
            
        Returns:
            Dictionary mapping criteria to validation results
        """
        logger.info(f"Validating response against {len(criteria)} criteria")
        
        # Create validation tasks
        validation_tasks = {}
        for criterion in criteria:
            task = self.validate_criterion(criterion, response_text, input_data)
            validation_tasks[criterion] = task
        
        # Execute all validations concurrently
        results = await asyncio.gather(*validation_tasks.values(), return_exceptions=True)
        
        # Collect results - no fallbacks for failed validations
        validation_results = {}
        for criterion, result in zip(validation_tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Validation failed for {criterion}: {result}")
                raise RuntimeError(f"Multi-criteria validation failed for {criterion}: {result}")
            else:
                validation_results[criterion] = result
        
        return validation_results
    
    async def _generate_llm_response(self, prompt: str, llm_config: Dict[str, Any]) -> str:
        """Generate response from the validation LLM"""
        
        # Prepare request payload for Ollama
        payload = {
            "model": llm_config["model_name"],
            "prompt": prompt,
            "options": {
                "temperature": llm_config["temperature"],
                "num_predict": llm_config["max_tokens"]
            },
            "stream": False
        }
        
        # Make async request to Ollama using asyncio
        loop = asyncio.get_event_loop()
        
        def make_request():
            timeout = llm_config.get("timeout")
            return self.session.post(
                f"{llm_config['host']}/api/generate",
                json=payload,
                timeout=timeout  # Will be None for no timeout
            )
        
        # Run the blocking request in a thread pool
        response = await loop.run_in_executor(None, make_request)
        
        if response.status_code != 200:
            raise RuntimeError(f"LLM request failed: HTTP {response.status_code}")
        
        result = response.json()
        return result.get("response", "")
    
    def _parse_validation_response(self, llm_response: str, criterion: str) -> Dict[str, Any]:
        """Parse the LLM validation response to extract score and details"""
        
        # Initialize result
        result = {
            "criterion": criterion,
            "score": 0.0,
            "confidence": 0.0,
            "explanation": llm_response,
            "issues": [],
            "recommendations": [],
            "status": "completed"
        }
        
        try:
            # Extract numerical score (0.0 to 1.0)
            score_patterns = [
                r"score[:\s]+([0-9]*\.?[0-9]+)",
                r"([0-9]*\.?[0-9]+)\s*/\s*1\.0",
                r"([0-9]*\.?[0-9]+)\s*out of\s*1",
                r"rating[:\s]+([0-9]*\.?[0-9]+)"
            ]
            
            score_found = False
            for pattern in score_patterns:
                match = re.search(pattern, llm_response.lower())
                if match:
                    score = float(match.group(1))
                    # Ensure score is in valid range
                    result["score"] = max(0.0, min(1.0, score))
                    score_found = True
                    break
            
            if not score_found:
                logger.warning(f"Could not extract score from validation response for {criterion}")
                result["score"] = 0.5  # Default neutral score
            
            # Extract confidence if mentioned
            confidence_match = re.search(r"confidence[:\s]+([0-9]*\.?[0-9]+)", llm_response.lower())
            if confidence_match:
                result["confidence"] = max(0.0, min(1.0, float(confidence_match.group(1))))
            else:
                # Infer confidence from response quality
                result["confidence"] = self._infer_confidence(llm_response)
            
            # Extract issues and recommendations
            result["issues"] = self._extract_issues(llm_response)
            result["recommendations"] = self._extract_recommendations(llm_response)
            
        except Exception as e:
            logger.warning(f"Error parsing validation response for {criterion}: {e}")
            result["score"] = 0.0
            result["issues"] = [f"Response parsing error: {str(e)}"]
        
        return result
    
    def _extract_issues(self, response: str) -> List[str]:
        """Extract identified issues from the validation response"""
        
        issues = []
        
        # Look for common issue indicators
        issue_patterns = [
            r"issue[s]?[:\s]+(.*?)(?=\n|$)",
            r"problem[s]?[:\s]+(.*?)(?=\n|$)",
            r"error[s]?[:\s]+(.*?)(?=\n|$)",
            r"concern[s]?[:\s]+(.*?)(?=\n|$)",
            r"weakness[es]*[:\s]+(.*?)(?=\n|$)"
        ]
        
        for pattern in issue_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                issue = match.strip().rstrip('.')
                if len(issue) > 10:  # Filter out very short matches
                    issues.append(issue)
        
        # Look for bullet points that might be issues
        bullet_issues = re.findall(r"[•\-\*]\s*(.+?)(?=\n|$)", response)
        for issue in bullet_issues:
            if any(keyword in issue.lower() for keyword in ["issue", "problem", "error", "incorrect", "missing", "lack"]):
                issues.append(issue.strip())
        
        return issues[:5]  # Limit to top 5 issues
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from the validation response"""
        
        recommendations = []
        
        # Look for recommendation indicators
        rec_patterns = [
            r"recommend[s]?[:\s]+(.*?)(?=\n|$)",
            r"suggest[s]?[:\s]+(.*?)(?=\n|$)",
            r"should[:\s]+(.*?)(?=\n|$)",
            r"improvement[s]?[:\s]+(.*?)(?=\n|$)"
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                rec = match.strip().rstrip('.')
                if len(rec) > 10:
                    recommendations.append(rec)
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _infer_confidence(self, response: str) -> float:
        """Infer confidence level from response characteristics"""
        
        # Factors that increase confidence
        confidence_indicators = [
            "clearly", "definitely", "certainly", "obviously", "precisely",
            "accurate", "correct", "proper", "excellent", "strong"
        ]
        
        # Factors that decrease confidence
        uncertainty_indicators = [
            "might", "possibly", "perhaps", "unclear", "ambiguous",
            "difficult", "uncertain", "questionable", "problematic"
        ]
        
        response_lower = response.lower()
        
        confidence_score = 0.5  # Base confidence
        
        # Count positive and negative indicators
        positive_count = sum(1 for indicator in confidence_indicators if indicator in response_lower)
        negative_count = sum(1 for indicator in uncertainty_indicators if indicator in response_lower)
        
        # Adjust confidence based on indicators
        confidence_score += (positive_count * 0.1) - (negative_count * 0.15)
        
        # Consider response length (longer responses might be more confident)
        if len(response) > 200:
            confidence_score += 0.1
        elif len(response) < 50:
            confidence_score -= 0.1
        
        return max(0.0, min(1.0, confidence_score))
    
    async def _test_llm_connection(self) -> Dict[str, Any]:
        """Test connection to the validation LLM"""
        try:
            # Simple test request
            payload = {
                "model": self.llm_config["model_name"],
                "prompt": "Test connection. Respond with 'OK'.",
                "options": {"num_predict": 10},
                "stream": False
            }
            
            # Make async request using thread pool
            loop = asyncio.get_event_loop()
            
            def make_test_request():
                return self.session.post(
                    f"{self.llm_config['host']}/api/generate",
                    json=payload,
                    timeout=None  # No timeout for testing
                )
            
            response = await loop.run_in_executor(None, make_test_request)
            
            if response.status_code == 200:
                return {"available": True, "status": "connected"}
            else:
                return {"available": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _generate_cache_key(self, criterion: str, response_text: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key for validation result"""
        
        # Create a hash of the key components
        import hashlib
        
        key_components = f"{criterion}_{response_text[:100]}_{str(input_data)[:100]}"
        return hashlib.md5(key_components.encode()).hexdigest()
    
    def _cleanup_cache(self):
        """Clean up old cache entries"""
        # Keep only the most recent 500 entries
        if len(self.response_cache) > 500:
            # Remove oldest entries (this is a simple approach)
            keys_to_remove = list(self.response_cache.keys())[:-500]
            for key in keys_to_remove:
                del self.response_cache[key]
    
    def _update_response_time(self, processing_time: float):
        """Update average response time"""
        if self.successful_validations == 1:
            self.average_response_time = processing_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.average_response_time = (alpha * processing_time + 
                                        (1 - alpha) * self.average_response_time)
    
    def get_validator_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        
        success_rate = self.successful_validations / max(self.total_validations, 1)
        cache_hit_rate = self.cache_hits / max(self.total_validations, 1)
        
        return {
            "total_validations": self.total_validations,
            "successful_validations": self.successful_validations,
            "failed_validations": self.failed_validations,
            "success_rate": success_rate,
            "average_response_time": self.average_response_time,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": cache_hit_rate,
            "cache_size": len(self.response_cache),
            "model_name": self.llm_config["model_name"],
            "model_host": self.llm_config["host"]
        }
    
    async def shutdown(self):
        """Shutdown the LLM validator"""
        logger.info("Shutting down LLM validator...")
        
        try:
            self.session.close()
            self.response_cache.clear()
            logger.info("LLM validator shutdown completed")
        except Exception as e:
            logger.error(f"Error during LLM validator shutdown: {e}")
