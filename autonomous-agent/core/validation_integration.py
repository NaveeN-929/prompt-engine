"""
Validation Integration Service
Provides blocking validation integration for the autonomous agent
"""

import asyncio
import json
import logging
import os
import time
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationIntegrationService:
    """
    Service that integrates validation as a blocking quality gate
    before responses are sent to end users
    """
    
    def __init__(self, 
                 validation_url: str = None,
                 quality_threshold: float = 0.65,
                 max_retry_attempts: int = 2):
        
        # Use environment variables for Docker deployment
        if validation_url is None:
            # Use VALIDATOR_HOST for service discovery to avoid conflict with VALIDATION_HOST (bind address)
            validation_host = os.getenv('VALIDATOR_HOST', os.getenv('VALIDATION_HOST', 'localhost'))
            validation_port = os.getenv('VALIDATOR_PORT', os.getenv('VALIDATION_PORT', '5002'))
            validation_url = f"http://{validation_host}:{validation_port}"
        self.validation_url = validation_url
        self.quality_threshold = quality_threshold
        self.max_retry_attempts = max_retry_attempts
        
        # Session for HTTP requests
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Statistics
        self.stats = {
            "total_validations": 0,
            "passed_validations": 0,
            "failed_validations": 0,
            "retries_triggered": 0,
            "validation_errors": 0,
            "average_validation_time": 0.0,
            "total_validation_time": 0.0
        }
        
        # Quality gates configuration
        self.quality_gates = {
            "exemplary": 0.95,      # Premium quality - immediate pass
            "high_quality": 0.80,   # High quality - pass with confidence
            "acceptable": 0.65,     # Acceptable - pass with notes
            "poor": 0.0            # Poor quality - retry or reject
        }
        
    def is_validation_service_available(self) -> bool:
        """Check if validation service is available"""
        try:
            response = self.session.get(f"{self.validation_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_validation_service_health(self) -> Dict[str, Any]:
        """Get detailed health information from validation service"""
        try:
            response = self.session.get(f"{self.validation_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "service_data": health_data,
                    "url": self.validation_url,
                    "last_check": time.time()
                }
            else:
                return {
                    "status": "unhealthy",
                    "http_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "url": self.validation_url,
                    "last_check": time.time(),
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "error": "Health check timed out",
                "url": self.validation_url,
                "last_check": time.time()
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "connection_error",
                "error": "Cannot connect to validation service",
                "url": self.validation_url,
                "last_check": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": self.validation_url,
                "last_check": time.time()
            }
    
    def get_validation_service_detailed_status(self) -> Dict[str, Any]:
        """Get comprehensive status including service capabilities"""
        base_health = self.get_validation_service_health()
        
        # If service is healthy, get additional status information
        if base_health["status"] == "healthy":
            try:
                # Try to get system status from validation service
                status_response = self.session.get(f"{self.validation_url}/system/status", timeout=10)
                if status_response.status_code == 200:
                    system_status = status_response.json()
                    base_health["system_status"] = system_status
                
                # Try to get validation statistics
                stats_response = self.session.get(f"{self.validation_url}/validation/stats", timeout=10)
                if stats_response.status_code == 200:
                    validation_stats = stats_response.json()
                    base_health["validation_statistics"] = validation_stats
                    
            except Exception as e:
                base_health["additional_info_error"] = str(e)
        
        # Add local integration statistics
        base_health["integration_stats"] = self.get_validation_statistics()
        
        return base_health
    
    def refresh_service_status(self) -> Dict[str, Any]:
        """Refresh and return current service status"""
        current_health = self.get_validation_service_health()
        
        return {
            "service_available": current_health["status"] == "healthy",
            "health_data": current_health,
            "integration_stats": self.get_validation_statistics(),
            "last_refresh": time.time()
        }
    
    async def validate_and_gate_response(self, 
                                       response_data: Dict[str, Any],
                                       input_data: Dict[str, Any],
                                       retry_callback = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate response and apply quality gates before allowing user delivery
        
        Args:
            response_data: Response from autonomous agent
            input_data: Original input data
            retry_callback: Optional callback to regenerate response if quality is poor
            
        Returns:
            Tuple of (should_deliver_to_user: bool, enhanced_response: Dict)
        """
        validation_start_time = time.time()
        self.stats["total_validations"] += 1
        
        try:
            # Check if validation service is available
            if not self.is_validation_service_available():
                logger.warning("Validation service unavailable - using fallback assessment")
                return await self._fallback_quality_assessment(response_data, input_data)
            
            # Perform validation
            validation_result = await self._validate_response_quality(response_data, input_data)
            
            if not validation_result["success"]:
                logger.error(f"Validation failed: {validation_result.get('error', 'Unknown error')}")
                self.stats["validation_errors"] += 1
                return await self._fallback_quality_assessment(response_data, input_data)
            
            validation_data = validation_result["data"]
            quality_level = validation_data.get("quality_level", "poor")
            overall_score = validation_data.get("overall_score", 0.0)
            
            # Apply quality gates
            should_deliver, enhanced_response = await self._apply_quality_gates(
                response_data, validation_data, quality_level, overall_score, 
                input_data, retry_callback
            )
            
            # Update statistics
            validation_time = time.time() - validation_start_time
            self.stats["total_validation_time"] += validation_time
            self.stats["average_validation_time"] = (
                self.stats["total_validation_time"] / self.stats["total_validations"]
            )
            
            if should_deliver:
                self.stats["passed_validations"] += 1
            else:
                self.stats["failed_validations"] += 1
            
            return should_deliver, enhanced_response
            
        except Exception as e:
            logger.error(f"Validation integration error: {e}")
            self.stats["validation_errors"] += 1
            return await self._fallback_quality_assessment(response_data, input_data)
    
    async def _validate_response_quality(self, 
                                       response_data: Dict[str, Any],
                                       input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send response to validation service for quality assessment"""
        
        validation_request = {
            "response_data": response_data,
            "input_data": input_data,
            "validation_config": {
                "criteria": {
                    "content_accuracy": {"weight": 0.30, "threshold": 0.8},
                    "structural_compliance": {"weight": 0.25, "threshold": 0.9},
                    "logical_consistency": {"weight": 0.20, "threshold": 0.7},
                    "completeness": {"weight": 0.15, "threshold": 0.6},
                    "business_relevance": {"weight": 0.10, "threshold": 0.5}
                }
            }
        }
        
        try:
            response = self.session.post(
                f"{self.validation_url}/validate/response",
                json=validation_request,
                timeout=30
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error_msg = f"Validation service returned {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('error', 'Unknown error')}"
                except:
                    pass
                return {"success": False, "error": error_msg}
                
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Validation timeout"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to validation service"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _apply_quality_gates(self, 
                                 response_data: Dict[str, Any],
                                 validation_data: Dict[str, Any],
                                 quality_level: str,
                                 overall_score: float,
                                 input_data: Dict[str, Any],
                                 retry_callback = None) -> Tuple[bool, Dict[str, Any]]:
        """Apply quality gates to determine if response should be delivered to user"""
        
        # Create enhanced response with validation metadata
        enhanced_response = response_data.copy()
        enhanced_response["validation"] = {
            "quality_level": quality_level,
            "overall_score": overall_score,
            "validation_timestamp": datetime.now().isoformat(),
            "quality_approved": False,
            "validation_details": validation_data
        }
        
        # Quality gate logic
        if quality_level in ["exemplary", "high_quality"]:
            # Excellent quality - immediate delivery
            enhanced_response["validation"]["quality_approved"] = True
            enhanced_response["validation"]["quality_note"] = f"High quality response ({quality_level})"
            logger.info(f"Response approved: {quality_level} quality (score: {overall_score:.3f})")
            return True, enhanced_response
            
        elif quality_level == "acceptable" and overall_score >= self.quality_threshold:
            # Acceptable quality - deliver with improvement notes
            enhanced_response["validation"]["quality_approved"] = True
            enhanced_response["validation"]["quality_note"] = "Acceptable quality with improvement opportunities"
            enhanced_response["validation"]["improvement_suggestions"] = validation_data.get("recommendations", [])
            logger.info(f"Response approved: acceptable quality (score: {overall_score:.3f})")
            return True, enhanced_response
            
        else:
            # Poor quality - attempt retry if callback provided
            if retry_callback and self.stats.get("current_retry_attempt", 0) < self.max_retry_attempts:
                logger.warning(f"Poor quality response (score: {overall_score:.3f}), attempting retry...")
                self.stats["retries_triggered"] += 1
                self.stats["current_retry_attempt"] = self.stats.get("current_retry_attempt", 0) + 1
                
                try:
                    # Attempt to regenerate response with feedback
                    retry_response = await retry_callback(input_data, validation_data)
                    if retry_response:
                        # Recursively validate the retry response
                        return await self.validate_and_gate_response(retry_response, input_data, retry_callback)
                except Exception as e:
                    logger.error(f"Retry callback failed: {e}")
            
            # Reset retry counter
            self.stats["current_retry_attempt"] = 0
            
            # Poor quality - deliver with warnings (user preference to see responses)
            enhanced_response["validation"]["quality_approved"] = False
            enhanced_response["validation"]["quality_warning"] = f"Response quality below threshold (score: {overall_score:.3f})"
            enhanced_response["validation"]["quality_issues"] = validation_data.get("recommendations", [])
            
            logger.warning(f"Response delivered with quality warning (score: {overall_score:.3f})")
            return True, enhanced_response  # Still deliver but with clear quality warnings
    
    async def _fallback_quality_assessment(self, 
                                         response_data: Dict[str, Any],
                                         input_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Fallback quality assessment when validation service is unavailable"""
        
        enhanced_response = response_data.copy()
        enhanced_response["validation"] = {
            "quality_level": "unknown",
            "overall_score": 0.0,
            "validation_timestamp": datetime.now().isoformat(),
            "quality_approved": True,  # Allow delivery when validation unavailable
            "validation_status": "service_unavailable",
            "quality_note": "Validation service unavailable - response delivered without validation"
        }
        
        # Basic structural checks
        analysis = response_data.get("analysis", "")
        if "=== SECTION 1: INSIGHTS ===" in analysis and "=== SECTION 2: RECOMMENDATIONS ===" in analysis:
            enhanced_response["validation"]["structure_check"] = "passed"
        else:
            enhanced_response["validation"]["structure_check"] = "failed"
            enhanced_response["validation"]["quality_note"] += " - Structure validation failed"
        
        logger.warning("Using fallback quality assessment - validation service unavailable")
        return True, enhanced_response
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation integration statistics"""
        return {
            "validation_stats": self.stats.copy(),
            "quality_gates": self.quality_gates.copy(),
            "configuration": {
                "validation_url": self.validation_url,
                "quality_threshold": self.quality_threshold,
                "max_retry_attempts": self.max_retry_attempts
            },
            "service_status": {
                "validation_service_available": self.is_validation_service_available(),
                "last_check": datetime.now().isoformat()
            }
        }
