"""
Core Validation Engine - Orchestrates the complete validation process
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from core.llm_validator import LLMValidator
from core.quality_assessor import QualityAssessor
from core.training_data_manager import TrainingDataManager
from core.feedback_manager import FeedbackManager
from config import get_config, get_validation_threshold

logger = logging.getLogger(__name__)

class ValidationResult:
    """Container for validation results"""
    
    def __init__(self, validation_id: str):
        self.validation_id = validation_id
        self.timestamp = datetime.now().isoformat()
        self.overall_score = 0.0
        self.quality_level = "unassessed"
        self.criteria_scores = {}
        self.validation_details = {}
        self.recommendations = []
        self.training_data_eligible = False
        self.processing_time = 0.0
        self.status = "pending"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "validation_id": self.validation_id,
            "timestamp": self.timestamp,
            "overall_score": self.overall_score,
            "quality_level": self.quality_level,
            "criteria_scores": self.criteria_scores,
            "validation_details": self.validation_details,
            "recommendations": self.recommendations,
            "training_data_eligible": self.training_data_eligible,
            "processing_time": self.processing_time,
            "status": self.status
        }

class ValidationEngine:
    """
    Core validation engine that orchestrates the complete validation process
    for autonomous agent responses
    """
    
    def __init__(self):
        self.config = get_config()
        
        # Initialize core components
        self.llm_validator = LLMValidator()
        self.quality_assessor = QualityAssessor()
        self.training_data_manager = TrainingDataManager()
        self.feedback_manager = FeedbackManager()
        
        # Validation statistics
        self.total_validations = 0
        self.successful_validations = 0
        self.failed_validations = 0
        self.quality_distribution = {
            "exemplary": 0,
            "high_quality": 0,
            "acceptable": 0,
            "poor": 0
        }
        
        # Processing history
        self.validation_history = []
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the validation engine and all components"""
        try:
            logger.info("Initializing Response Validation Engine...")
            
            # Initialize components
            await self.llm_validator.initialize()
            await self.quality_assessor.initialize()
            await self.training_data_manager.initialize()
            await self.feedback_manager.initialize()
            
            self.is_initialized = True
            logger.info("Validation Engine initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize validation engine: {e}")
            raise
    
    async def validate_response(self, 
                              response_data: Dict[str, Any],
                              input_data: Dict[str, Any],
                              validation_config: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate a complete autonomous agent response
        
        Args:
            response_data: The response from autonomous agent to validate
            input_data: Original input data for context validation
            validation_config: Optional validation configuration overrides
            
        Returns:
            Complete validation results with quality assessment
        """
        if not self.is_initialized:
            raise RuntimeError("Validation engine not initialized. Call initialize() first.")
        
        validation_id = f"val_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        start_time = time.time()
        self.total_validations += 1
        
        try:
            logger.info(f"Starting validation {validation_id}")
            
            # Create validation result container
            result = ValidationResult(validation_id)
            
            # Extract response text for validation
            response_text = self._extract_response_text(response_data)
            if not response_text:
                result.status = "error"
                result.validation_details["error"] = "No response text found"
                return result
            
            # Check if fast validation is requested
            fast_mode = validation_config and validation_config.get("fast_mode", False)
            
            # Phase 1: Multi-criteria LLM validation
            logger.info(f"[{validation_id}] Phase 1: Multi-criteria validation (fast_mode: {fast_mode})")
            criteria_results = await self._validate_all_criteria(
                response_text, input_data, validation_config
            )
            result.criteria_scores = criteria_results
            
            # Phase 2: Quality assessment and scoring
            logger.info(f"[{validation_id}] Phase 2: Quality assessment")
            quality_result = await self.quality_assessor.assess_quality(
                response_text, input_data, criteria_results, response_data
            )
            
            result.overall_score = quality_result["overall_score"]
            result.quality_level = quality_result["quality_level"]
            result.validation_details = quality_result["details"]
            
            if not fast_mode:
                # Phase 3: Generate recommendations (skip in fast mode)
                logger.info(f"[{validation_id}] Phase 3: Generating recommendations")
                recommendations = await self._generate_recommendations(
                    criteria_results, quality_result, response_text
                )
                result.recommendations = recommendations
                
                # Phase 4: Training data eligibility assessment (skip in fast mode)
                logger.info(f"[{validation_id}] Phase 4: Training data assessment")
                training_eligible = await self._assess_training_eligibility(
                    result.overall_score, result.quality_level, criteria_results
                )
                result.training_data_eligible = training_eligible
                
                # Phase 5: Store high-quality responses for training (skip in fast mode)
                if training_eligible:
                    logger.info(f"[{validation_id}] Phase 5: Storing training data")
                    await self.training_data_manager.store_training_data(
                        input_data=input_data,
                        response_data=response_data,
                        validation_result=result.to_dict(),
                        quality_level=result.quality_level
                    )
            else:
                logger.info(f"[{validation_id}] Fast mode: Skipping phases 3-5 for speed")
                result.recommendations = []
                result.training_data_eligible = False
            
            # Phase 6: Send feedback to autonomous agent
            logger.info(f"[{validation_id}] Phase 6: Sending feedback")
            await self.feedback_manager.send_feedback_to_agent(
                response_data, result.to_dict(), input_data
            )
            
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            result.status = "completed"
            
            # Update statistics
            self._update_statistics(result)
            
            # Store in history
            self.validation_history.append(result.to_dict())
            if len(self.validation_history) > 1000:
                self.validation_history = self.validation_history[-800:]
            
            self.successful_validations += 1
            logger.info(f"Validation {validation_id} completed successfully in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            self.failed_validations += 1
            processing_time = time.time() - start_time
            
            logger.error(f"Validation {validation_id} failed: {e}")
            
            result = ValidationResult(validation_id)
            result.status = "error"
            result.processing_time = processing_time
            result.validation_details["error"] = str(e)
            
            return result
    
    async def validate_batch(self, 
                           batch_data: List[Dict[str, Any]],
                           validation_config: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """
        Validate multiple responses in batch
        
        Args:
            batch_data: List of {response_data, input_data} dictionaries
            validation_config: Optional validation configuration
            
        Returns:
            List of validation results
        """
        logger.info(f"Starting batch validation of {len(batch_data)} responses")
        
        # Create validation tasks
        validation_tasks = []
        for item in batch_data:
            task = self.validate_response(
                response_data=item["response_data"],
                input_data=item["input_data"], 
                validation_config=validation_config
            )
            validation_tasks.append(task)
        
        # Execute validations concurrently
        results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Filter out exceptions and log errors
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch validation item {i} failed: {result}")
                # Create error result
                error_result = ValidationResult(f"batch_{i}_{int(time.time())}")
                error_result.status = "error"
                error_result.validation_details["error"] = str(result)
                valid_results.append(error_result)
            else:
                valid_results.append(result)
        
        logger.info(f"Batch validation completed: {len(valid_results)} results")
        return valid_results
    
    async def _validate_all_criteria(self, 
                                   response_text: str,
                                   input_data: Dict[str, Any],
                                   validation_config: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Validate response against all criteria using LLM validators"""
        
        criteria = self.config["validation_criteria"]
        if validation_config and "criteria" in validation_config:
            criteria = validation_config["criteria"]
        
        # Create validation tasks for all criteria
        validation_tasks = {}
        for criterion_name in criteria.keys():
            task = self.llm_validator.validate_criterion(
                criterion=criterion_name,
                response_text=response_text,
                input_data=input_data
            )
            validation_tasks[criterion_name] = task
        
        # Execute all validations concurrently
        results = await asyncio.gather(*validation_tasks.values(), return_exceptions=True)
        
        # Collect results - no fallbacks for failed criteria
        criteria_scores = {}
        for i, (criterion_name, result) in enumerate(zip(validation_tasks.keys(), results)):
            if isinstance(result, Exception):
                logger.error(f"Validation failed for {criterion_name}: {result}")
                raise RuntimeError(f"Validation failed for {criterion_name}: {result}")
            else:
                criteria_scores[criterion_name] = result.get("score", 0.0)
        
        return criteria_scores
    
    async def _generate_recommendations(self,
                                      criteria_results: Dict[str, float],
                                      quality_result: Dict[str, Any],
                                      response_text: str) -> List[str]:
        """Generate improvement recommendations based on validation results"""
        
        recommendations = []
        criteria_config = self.config["validation_criteria"]
        
        # Check each criterion against its threshold
        for criterion, score in criteria_results.items():
            threshold = criteria_config.get(criterion, {}).get("threshold", 0.7)
            if score < threshold:
                gap = threshold - score
                if criterion == "content_accuracy":
                    recommendations.append(f"Improve factual accuracy (current: {score:.2f}, target: {threshold:.2f}). Verify all numerical values and claims against input data.")
                elif criterion == "structural_compliance":
                    recommendations.append(f"Fix response structure (current: {score:.2f}, target: {threshold:.2f}). Ensure proper INSIGHTS/RECOMMENDATIONS sections.")
                elif criterion == "logical_consistency":
                    recommendations.append(f"Enhance logical reasoning (current: {score:.2f}, target: {threshold:.2f}). Check for contradictions and improve reasoning chain.")
                elif criterion == "completeness":
                    recommendations.append(f"Address more aspects of the data (current: {score:.2f}, target: {threshold:.2f}). Provide more comprehensive analysis.")
                elif criterion == "business_relevance":
                    recommendations.append(f"Increase business value (current: {score:.2f}, target: {threshold:.2f}). Focus on actionable business insights.")
                elif criterion == "actionability":
                    recommendations.append(f"Make recommendations more specific (current: {score:.2f}, target: {threshold:.2f}). Provide clear next steps.")
        
        # Add overall quality recommendations
        if quality_result["overall_score"] < 0.75:
            recommendations.append("Overall response quality needs improvement. Focus on the highest-impact areas identified above.")
        
        return recommendations
    
    async def _assess_training_eligibility(self,
                                         overall_score: float,
                                         quality_level: str,
                                         criteria_results: Dict[str, float]) -> bool:
        """Assess if response is eligible for training data storage"""
        
        # Must meet minimum quality threshold
        if overall_score < get_validation_threshold("acceptable"):
            return False
        
        # Must not have any critically low scores
        for criterion, score in criteria_results.items():
            if criterion in ["content_accuracy", "structural_compliance"] and score < 0.5:
                return False
        
        # Quality level must be acceptable or higher
        if quality_level == "poor":
            return False
        
        return True
    
    def _extract_response_text(self, response_data: Dict[str, Any]) -> str:
        """Extract the main response text from response data"""
        
        # Try different possible keys for the response text
        possible_keys = ["analysis", "response", "content", "text", "result"]
        
        for key in possible_keys:
            if key in response_data and isinstance(response_data[key], str):
                return response_data[key]
        
        # If response_data itself is a string
        if isinstance(response_data, str):
            return response_data
        
        # Try to extract from nested structures
        if "analysis" in response_data and isinstance(response_data["analysis"], dict):
            for key in possible_keys:
                if key in response_data["analysis"]:
                    return str(response_data["analysis"][key])
        
        logger.warning("Could not extract response text from response_data")
        return ""
    
    def _update_statistics(self, result: ValidationResult):
        """Update validation statistics"""
        
        # Update quality distribution
        if result.quality_level in self.quality_distribution:
            self.quality_distribution[result.quality_level] += 1
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive validation statistics"""
        
        success_rate = self.successful_validations / max(self.total_validations, 1)
        
        return {
            "total_validations": self.total_validations,
            "successful_validations": self.successful_validations,
            "failed_validations": self.failed_validations,
            "success_rate": success_rate,
            "quality_distribution": self.quality_distribution,
            "average_processing_time": self._calculate_average_processing_time(),
            "training_data_stored": self.training_data_manager.get_storage_stats(),
            "recent_validations": len(self.validation_history),
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_average_processing_time(self) -> float:
        """Calculate average processing time from recent validations"""
        
        if not self.validation_history:
            return 0.0
        
        recent_times = [v.get("processing_time", 0.0) for v in self.validation_history[-100:]]
        return sum(recent_times) / len(recent_times) if recent_times else 0.0
    
    async def get_recent_validations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent validation results"""
        return self.validation_history[-limit:] if self.validation_history else []
    
    async def shutdown(self):
        """Shutdown the validation engine and cleanup resources"""
        logger.info("Shutting down validation engine...")
        
        try:
            await self.llm_validator.shutdown()
            await self.quality_assessor.shutdown()
            await self.training_data_manager.shutdown()
            await self.feedback_manager.shutdown()
            
            logger.info("Validation engine shutdown completed")
        except Exception as e:
            logger.error(f"Error during validation engine shutdown: {e}")
