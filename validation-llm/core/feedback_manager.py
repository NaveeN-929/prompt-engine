"""
Feedback Manager - Sends validation feedback to the autonomous agent
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import requests

from config import get_config

logger = logging.getLogger(__name__)

class FeedbackManager:
    """
    Manages sending validation feedback to the autonomous agent
    to help improve future response quality
    """
    
    def __init__(self):
        self.config = get_config()
        self.agent_config = self.config["autonomous_agent"]
        self.prompt_engine_config = self.config["prompt_engine"]
        self.feedback_templates = self.config["feedback_templates"]
        
        # HTTP sessions
        self.agent_session = requests.Session()
        self.agent_session.timeout = self.agent_config["timeout"]
        
        self.prompt_session = requests.Session()
        self.prompt_session.timeout = self.prompt_engine_config["timeout"]
        
        # Feedback statistics
        self.total_feedback_sent = 0
        self.successful_feedback = 0
        self.failed_feedback = 0
        self.feedback_by_quality = {
            "exemplary": 0,
            "high_quality": 0,
            "acceptable": 0,
            "poor": 0
        }
        
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the feedback manager"""
        try:
            logger.info("Initializing Feedback Manager...")
            
            # Test connections to autonomous agent and prompt engine
            agent_status = await self._test_agent_connection()
            prompt_status = await self._test_prompt_engine_connection()
            
            if not agent_status["available"]:
                logger.warning(f"Autonomous agent not available: {agent_status['error']}")
            
            if not prompt_status["available"]:
                logger.warning(f"Prompt engine not available: {prompt_status['error']}")
            
            self.is_initialized = True
            logger.info("Feedback Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize feedback manager: {e}")
            raise
    
    async def send_feedback_to_agent(self,
                                   response_data: Dict[str, Any],
                                   validation_result: Dict[str, Any],
                                   input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send validation feedback to the autonomous agent
        
        Args:
            response_data: Original response from autonomous agent
            validation_result: Complete validation results
            input_data: Original input data for context
            
        Returns:
            Feedback delivery result
        """
        if not self.is_initialized:
            raise RuntimeError("Feedback manager not initialized")
        
        self.total_feedback_sent += 1
        
        try:
            # Prepare feedback message
            feedback_message = self._prepare_feedback_message(
                response_data, validation_result, input_data
            )
            
            # Send feedback to autonomous agent
            agent_feedback_result = await self._send_agent_feedback(feedback_message)
            
            # Send learning feedback to prompt engine if quality is high
            prompt_feedback_result = None
            quality_level = validation_result.get("quality_level", "poor")
            
            if quality_level in ["exemplary", "high_quality"]:
                prompt_feedback_result = await self._send_prompt_engine_feedback(
                    input_data, response_data, validation_result
                )
            
            # Update statistics
            self._update_feedback_statistics(quality_level, agent_feedback_result["success"])
            
            if agent_feedback_result["success"]:
                self.successful_feedback += 1
            else:
                self.failed_feedback += 1
            
            return {
                "feedback_sent": True,
                "agent_feedback": agent_feedback_result,
                "prompt_engine_feedback": prompt_feedback_result,
                "quality_level": quality_level,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.failed_feedback += 1
            logger.error(f"Failed to send feedback: {e}")
            
            return {
                "feedback_sent": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def send_batch_feedback(self, 
                                feedback_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Send feedback for multiple validations in batch
        
        Args:
            feedback_batch: List of feedback data dictionaries
            
        Returns:
            List of feedback results
        """
        logger.info(f"Sending batch feedback for {len(feedback_batch)} validations")
        
        # Create feedback tasks
        feedback_tasks = []
        for item in feedback_batch:
            task = self.send_feedback_to_agent(
                response_data=item["response_data"],
                validation_result=item["validation_result"],
                input_data=item["input_data"]
            )
            feedback_tasks.append(task)
        
        # Execute feedback tasks concurrently
        results = await asyncio.gather(*feedback_tasks, return_exceptions=True)
        
        # Process results
        feedback_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch feedback item {i} failed: {result}")
                feedback_results.append({
                    "feedback_sent": False,
                    "error": str(result),
                    "batch_index": i
                })
            else:
                feedback_results.append(result)
        
        return feedback_results
    
    def _prepare_feedback_message(self,
                                response_data: Dict[str, Any],
                                validation_result: Dict[str, Any],
                                input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare structured feedback message for the autonomous agent"""
        
        quality_level = validation_result.get("quality_level", "poor")
        overall_score = validation_result.get("overall_score", 0.0)
        criteria_scores = validation_result.get("criteria_scores", {})
        
        # Generate feedback text based on quality level
        if quality_level == "exemplary":
            feedback_text = self.feedback_templates["high_quality"].format(
                score=overall_score,
                strengths=self._generate_strengths_summary(criteria_scores, validation_result)
            )
        elif quality_level in ["high_quality", "acceptable"]:
            feedback_text = self.feedback_templates["needs_improvement"].format(
                score=overall_score,
                improvements=self._generate_improvements_summary(criteria_scores, validation_result),
                recommendations=self._generate_recommendations_summary(validation_result)
            )
        else:  # poor quality
            feedback_text = self.feedback_templates["rejected"].format(
                score=overall_score,
                issues=self._generate_issues_summary(criteria_scores, validation_result),
                required_changes=self._generate_required_changes_summary(validation_result)
            )
        
        # Create comprehensive feedback message
        feedback_message = {
            "validation_feedback": {
                "validation_id": validation_result.get("validation_id", "unknown"),
                "overall_score": overall_score,
                "quality_level": quality_level,
                "criteria_scores": criteria_scores,
                "feedback_text": feedback_text,
                "detailed_analysis": validation_result.get("details", {}),
                "recommendations": validation_result.get("recommendations", []),
                "timestamp": datetime.now().isoformat()
            },
            "response_metadata": {
                "request_id": response_data.get("request_id", "unknown"),
                "processing_time": response_data.get("processing_time", 0.0),
                "pipeline_used": response_data.get("pipeline_used", "unknown")
            },
            "input_context": {
                "data_summary": self._summarize_input_data(input_data),
                "complexity": self._assess_input_complexity(input_data)
            }
        }
        
        return feedback_message
    
    async def _send_agent_feedback(self, feedback_message: Dict[str, Any]) -> Dict[str, Any]:
        """Send feedback to the autonomous agent"""
        
        try:
            # Prepare request
            feedback_url = (f"{self.agent_config['base_url']}"
                          f"{self.agent_config['endpoints']['feedback']}")
            
            response = self.agent_session.post(
                feedback_url,
                json=feedback_message,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "response": response.json(),
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.warning(f"Could not send feedback to autonomous agent: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }
    
    async def _send_prompt_engine_feedback(self,
                                         input_data: Dict[str, Any],
                                         response_data: Dict[str, Any],
                                         validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Send learning feedback to the prompt engine for high-quality responses"""
        
        try:
            # Extract response text
            response_text = self._extract_response_text(response_data)
            
            # Prepare learning feedback
            learning_feedback = {
                "input_data": input_data,
                "prompt_result": response_data.get("prompt_used", ""),
                "llm_response": response_text,
                "quality_score": validation_result.get("overall_score", 0.0),
                "user_feedback": f"Validation system quality score: {validation_result.get('overall_score', 0.0):.3f}"
            }
            
            # Send to prompt engine
            learn_url = (f"{self.prompt_engine_config['base_url']}"
                        f"{self.prompt_engine_config['endpoints']['learn']}")
            
            response = self.prompt_session.post(
                learn_url,
                json=learning_feedback,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "response": response.json(),
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.warning(f"Could not send feedback to prompt engine: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }
    
    def _generate_strengths_summary(self, 
                                  criteria_scores: Dict[str, float],
                                  validation_result: Dict[str, Any]) -> str:
        """Generate summary of response strengths"""
        
        strengths = []
        
        # Identify high-scoring criteria
        for criterion, score in criteria_scores.items():
            if score >= 0.8:
                criterion_name = criterion.replace("_", " ").title()
                strengths.append(f"• Excellent {criterion_name} (score: {score:.2f})")
        
        # Add overall quality indicators
        overall_score = validation_result.get("overall_score", 0.0)
        if overall_score >= 0.9:
            strengths.append("• Exceptional overall quality")
        
        return "\n".join(strengths) if strengths else "• High-quality response across multiple dimensions"
    
    def _generate_improvements_summary(self,
                                     criteria_scores: Dict[str, float],
                                     validation_result: Dict[str, Any]) -> str:
        """Generate summary of areas needing improvement"""
        
        improvements = []
        criteria_config = self.config["validation_criteria"]
        
        # Identify low-scoring criteria
        for criterion, score in criteria_scores.items():
            if criterion in criteria_config:
                threshold = criteria_config[criterion]["threshold"]
                if score < threshold:
                    gap = threshold - score
                    criterion_name = criterion.replace("_", " ").title()
                    improvements.append(f"• {criterion_name}: {gap:.2f} points below threshold")
        
        return "\n".join(improvements) if improvements else "• Minor refinements needed"
    
    def _generate_recommendations_summary(self, validation_result: Dict[str, Any]) -> str:
        """Generate summary of specific recommendations"""
        
        recommendations = validation_result.get("recommendations", [])
        
        if not recommendations:
            return "• Continue current approach with minor refinements"
        
        # Format recommendations
        formatted_recs = []
        for i, rec in enumerate(recommendations[:5], 1):  # Limit to top 5
            formatted_recs.append(f"• {rec}")
        
        return "\n".join(formatted_recs)
    
    def _generate_issues_summary(self,
                               criteria_scores: Dict[str, float],
                               validation_result: Dict[str, Any]) -> str:
        """Generate summary of critical issues"""
        
        issues = []
        
        # Identify critically low scores
        for criterion, score in criteria_scores.items():
            if score < 0.5:
                criterion_name = criterion.replace("_", " ").title()
                issues.append(f"• Critical issue with {criterion_name} (score: {score:.2f})")
        
        # Add specific issues from validation details
        details = validation_result.get("details", {})
        if "quality_insights" in details:
            for insight in details["quality_insights"][:3]:  # Top 3 insights
                if "issue" in insight.lower() or "problem" in insight.lower():
                    issues.append(f"• {insight}")
        
        return "\n".join(issues) if issues else "• Multiple quality issues identified"
    
    def _generate_required_changes_summary(self, validation_result: Dict[str, Any]) -> str:
        """Generate summary of required changes"""
        
        changes = [
            "• Improve factual accuracy and data grounding",
            "• Ensure proper response structure and formatting",
            "• Enhance logical consistency in reasoning",
            "• Provide more specific and actionable recommendations"
        ]
        
        # Add specific changes based on validation details
        recommendations = validation_result.get("recommendations", [])
        if recommendations:
            changes.extend([f"• {rec}" for rec in recommendations[:3]])
        
        return "\n".join(changes)
    
    def _summarize_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of input data for context"""
        
        return {
            "has_transactions": "transactions" in input_data,
            "transaction_count": len(input_data.get("transactions", [])),
            "has_balance": "account_balance" in input_data,
            "data_keys": list(input_data.keys()),
            "data_size": len(str(input_data))
        }
    
    def _assess_input_complexity(self, input_data: Dict[str, Any]) -> str:
        """Assess complexity of input data"""
        
        complexity_score = 0
        
        # Factor in data size
        if len(str(input_data)) > 1000:
            complexity_score += 2
        elif len(str(input_data)) > 500:
            complexity_score += 1
        
        # Factor in number of transactions
        transaction_count = len(input_data.get("transactions", []))
        if transaction_count > 20:
            complexity_score += 2
        elif transaction_count > 5:
            complexity_score += 1
        
        # Factor in data structure complexity
        if len(input_data.keys()) > 5:
            complexity_score += 1
        
        if complexity_score >= 4:
            return "high"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _extract_response_text(self, response_data: Dict[str, Any]) -> str:
        """Extract response text from response data"""
        
        # Try different possible keys
        possible_keys = ["analysis", "response", "content", "text", "result"]
        
        for key in possible_keys:
            if key in response_data and isinstance(response_data[key], str):
                return response_data[key]
        
        return str(response_data)
    
    async def _test_agent_connection(self) -> Dict[str, Any]:
        """Test connection to autonomous agent"""
        
        try:
            status_url = (f"{self.agent_config['base_url']}"
                         f"{self.agent_config['endpoints']['status']}")
            
            response = self.agent_session.get(status_url, timeout=10)
            
            if response.status_code == 200:
                return {"available": True, "status": "connected"}
            else:
                return {"available": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    async def _test_prompt_engine_connection(self) -> Dict[str, Any]:
        """Test connection to prompt engine"""
        
        try:
            status_url = (f"{self.prompt_engine_config['base_url']}"
                         f"{self.prompt_engine_config['endpoints']['status']}")
            
            response = self.prompt_session.get(status_url, timeout=10)
            
            if response.status_code == 200:
                return {"available": True, "status": "connected"}
            else:
                return {"available": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _update_feedback_statistics(self, quality_level: str, success: bool):
        """Update feedback statistics"""
        
        if quality_level in self.feedback_by_quality:
            self.feedback_by_quality[quality_level] += 1
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get comprehensive feedback statistics"""
        
        success_rate = self.successful_feedback / max(self.total_feedback_sent, 1)
        
        return {
            "total_feedback_sent": self.total_feedback_sent,
            "successful_feedback": self.successful_feedback,
            "failed_feedback": self.failed_feedback,
            "success_rate": success_rate,
            "feedback_by_quality": self.feedback_by_quality,
            "agent_connection": self.agent_config["base_url"],
            "prompt_engine_connection": self.prompt_engine_config["base_url"]
        }
    
    async def shutdown(self):
        """Shutdown the feedback manager"""
        logger.info("Shutting down feedback manager...")
        
        try:
            self.agent_session.close()
            self.prompt_session.close()
            logger.info("Feedback manager shutdown completed")
        except Exception as e:
            logger.error(f"Error during feedback manager shutdown: {e}")
