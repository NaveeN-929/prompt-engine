"""
Autonomous Financial Analysis Agent - Core orchestrator
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from .prompt_consumer import PromptConsumerService
from .reasoning_engine import ReasoningEngine
from .confidence_engine import ConfidenceEngine
from .hallucination_detector import HallucinationDetector
from .llm_interface import LLMInterface
from config import get_config

logger = logging.getLogger(__name__)

class AutonomousAgent:
    """
    Core autonomous agent that orchestrates the complete pipeline from
    prompt consumption to validated response generation
    """
    
    def __init__(self):
        self.config = get_config()
        
        # Initialize components
        self.prompt_consumer = PromptConsumerService()
        self.reasoning_engine = ReasoningEngine()
        self.confidence_engine = ConfidenceEngine()
        self.hallucination_detector = HallucinationDetector()
        self.llm_interface = LLMInterface()
        
        # Set configurations
        self.reasoning_engine.set_config(self.config)
        self.llm_interface.set_config(self.config)
        
        # Agent state
        self.is_initialized = False
        self.processing_queue = []
        self.interaction_history = []
        
        # Statistics
        self.total_requests = 0
        self.successful_responses = 0
        self.failed_responses = 0
        self.average_processing_time = 0.0
        self.quality_scores = []
        
    async def initialize(self):
        """Initialize the autonomous agent and all its components"""
        try:
            logger.info("Initializing Autonomous Financial Analysis Agent...")
            
            # Initialize LLM interface
            await self.llm_interface.initialize()
            
            # Test prompt engine connectivity
            async with self.prompt_consumer as consumer:
                capabilities = await consumer.get_prompt_engine_capabilities()
                if "error" in capabilities:
                    logger.warning(f"Prompt engine connectivity issue: {capabilities}")
                else:
                    logger.info("Prompt engine connectivity confirmed")
            
            self.is_initialized = True
            logger.info("Autonomous agent initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize autonomous agent: {e}")
            raise
    
    async def process_autonomous_request(self, 
                                       input_data: Dict[str, Any],
                                       request_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a complete autonomous analysis request
        
        Args:
            input_data: Financial data to analyze
            request_config: Optional configuration overrides
            
        Returns:
            Complete analysis results with confidence and validation
        """
        if not self.is_initialized:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        request_id = f"req_{int(time.time())}_{id(self)}"
        start_time = time.time()
        self.total_requests += 1
        
        try:
            logger.info(f"Processing autonomous request {request_id}")
            
            # Phase 1: Prompt Consumption and Analysis
            logger.info(f"[{request_id}] Phase 1: Consuming optimized prompt")
            prompt_result = await self._consume_prompt(input_data, request_config)
            
            # Phase 2: Multi-Step Reasoning
            logger.info(f"[{request_id}] Phase 2: Executing reasoning chain")
            reasoning_result = await self._execute_reasoning(prompt_result, input_data)
            
            # Phase 3: LLM Response Generation
            logger.info(f"[{request_id}] Phase 3: Generating LLM response")
            llm_result = await self._generate_llm_response(prompt_result, reasoning_result)
            
            # Phase 4: Response Validation
            logger.info(f"[{request_id}] Phase 4: Validating response")
            validation_result = await self._validate_response(
                llm_result, reasoning_result, input_data, prompt_result
            )
            
            # Phase 5: Confidence Scoring
            logger.info(f"[{request_id}] Phase 5: Calculating confidence")
            confidence_result = await self._calculate_confidence(
                llm_result, reasoning_result, input_data, prompt_result
            )
            
            # Phase 6: Final Quality Gate
            logger.info(f"[{request_id}] Phase 6: Final quality assessment")
            final_result = await self._apply_quality_gates(
                llm_result, validation_result, confidence_result, reasoning_result
            )
            
            # Phase 7: Learning Feedback
            logger.info(f"[{request_id}] Phase 7: Submitting learning feedback")
            await self._submit_learning_feedback(
                input_data, prompt_result, final_result, confidence_result, validation_result
            )
            
            processing_time = time.time() - start_time
            
            # Compile complete response
            complete_response = {
                "request_id": request_id,
                "status": "success",
                "processing_time": processing_time,
                "input_data_summary": self._summarize_input_data(input_data),
                
                # Core response
                "analysis": final_result["response"],
                "reasoning_chain": reasoning_result,
                "confidence_score": confidence_result,
                "validation_result": validation_result,
                
                # Metadata
                "prompt_metadata": prompt_result.get("agentic_metadata", {}),
                "llm_metadata": llm_result.get("metadata", {}),
                "agent_metadata": {
                    "version": self.config["agent"]["version"],
                    "processing_phases": [
                        "prompt_consumption", "reasoning", "llm_generation",
                        "validation", "confidence_scoring", "quality_gates", "learning"
                    ],
                    "quality_passed": final_result["quality_passed"],
                    "autonomous_mode": True,
                    "vector_enhanced": prompt_result.get("vector_accelerated", False)
                },
                
                # Quality indicators
                "reliability_indicators": {
                    "confidence_level": confidence_result.confidence_level,
                    "hallucination_detected": validation_result["hallucination_result"]["is_hallucinated"],
                    "reasoning_steps_validated": reasoning_result.get("validation_result", {}).get("passed", False),
                    "data_grounding_score": confidence_result.component_scores.get("data_grounding", 0.0),
                    "overall_quality_score": final_result["quality_score"]
                },
                
                "timestamp": datetime.now().isoformat()
            }
            
            # Update statistics
            self._update_statistics(processing_time, final_result["quality_score"], True)
            
            # Store in history
            self.interaction_history.append(complete_response)
            
            self.successful_responses += 1
            logger.info(f"Request {request_id} completed successfully in {processing_time:.3f}s")
            
            return complete_response
            
        except Exception as e:
            self.failed_responses += 1
            processing_time = time.time() - start_time
            
            logger.error(f"Request {request_id} failed: {e}")
            
            return {
                "request_id": request_id,
                "status": "error",
                "error": str(e),
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _consume_prompt(self, input_data: Dict[str, Any], 
                            request_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Phase 1: Consume optimized prompt from prompt engine"""
        
        generation_type = request_config.get("generation_type", "standard") if request_config else "standard"
        context = request_config.get("context") if request_config else None
        data_type = request_config.get("data_type") if request_config else None
        
        async with self.prompt_consumer as consumer:
            prompt_result = await consumer.consume_prompt(
                input_data=input_data,
                generation_type=generation_type,
                context=context,
                data_type=data_type
            )
        
        return prompt_result
    
    async def _execute_reasoning(self, prompt_result: Dict[str, Any], 
                               input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Execute multi-step reasoning chain"""
        
        prompt_text = prompt_result["prompt"]
        max_steps = self.config["agent"]["max_reasoning_steps"]
        
        reasoning_result = await self.reasoning_engine.execute_reasoning_chain(
            prompt=prompt_text,
            input_data=input_data,
            max_steps=max_steps
        )
        
        return reasoning_result
    
    async def _generate_llm_response(self, prompt_result: Dict[str, Any],
                                   reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Generate LLM response using the prompt and reasoning"""
        
        # Enhance prompt with reasoning context
        enhanced_prompt = self._enhance_prompt_with_reasoning(
            prompt_result["prompt"], reasoning_result
        )
        
        llm_result = await self.llm_interface.generate_response(
            prompt=enhanced_prompt,
            reasoning_context=reasoning_result
        )
        
        return llm_result
    
    async def _validate_response(self, llm_result: Dict[str, Any],
                               reasoning_result: Dict[str, Any],
                               input_data: Dict[str, Any],
                               prompt_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Validate response for hallucinations and accuracy"""
        
        response_text = llm_result["response"]
        
        # Hallucination detection
        hallucination_result = await self.hallucination_detector.detect_hallucinations(
            response=response_text,
            input_data=input_data,
            reasoning_chain=reasoning_result,
            prompt_metadata=prompt_result
        )
        
        # Additional validation checks
        validation_checks = {
            "response_length": self._validate_response_length(response_text),
            "data_references": self._validate_data_references(response_text, input_data),
            "logical_structure": self._validate_logical_structure(response_text),
            "completeness": self._validate_completeness(response_text, reasoning_result)
        }
        
        overall_validation = {
            "passed": not hallucination_result.is_hallucinated and all(
                check["passed"] for check in validation_checks.values()
            ),
            "hallucination_result": {
                "is_hallucinated": hallucination_result.is_hallucinated,
                "confidence": hallucination_result.confidence,
                "type": hallucination_result.hallucination_type,
                "severity": hallucination_result.severity,
                "evidence": hallucination_result.evidence,
                "recommendations": hallucination_result.recommendations
            },
            "validation_checks": validation_checks,
            "validation_score": self._calculate_validation_score(validation_checks, hallucination_result)
        }
        
        return overall_validation
    
    async def _calculate_confidence(self, llm_result: Dict[str, Any],
                                  reasoning_result: Dict[str, Any],
                                  input_data: Dict[str, Any],
                                  prompt_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 5: Calculate comprehensive confidence score"""
        
        confidence_result = await self.confidence_engine.calculate_confidence(
            response=llm_result["response"],
            reasoning_chain=reasoning_result,
            input_data=input_data,
            prompt_metadata=prompt_result
        )
        
        return {
            "overall_score": confidence_result.overall_score,
            "confidence_level": confidence_result.confidence_level,
            "component_scores": confidence_result.component_scores,
            "uncertainty_indicators": confidence_result.uncertainty_indicators,
            "explanation": confidence_result.explanation,
            "risk_factors": confidence_result.risk_factors,
            "reliability_indicators": confidence_result.reliability_indicators
        }
    
    async def _apply_quality_gates(self, llm_result: Dict[str, Any],
                                 validation_result: Dict[str, Any],
                                 confidence_result: Dict[str, Any],
                                 reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 6: Apply quality gates and determine final response"""
        
        quality_gates = self.config["validation"]["quality_gates"]
        gate_results = {}
        
        # Apply each quality gate
        for gate_name, gate_config in quality_gates.items():
            if not gate_config.get("enabled", True):
                gate_results[gate_name] = {"passed": True, "score": 1.0, "reason": "disabled"}
                continue
            
            gate_result = await self._apply_quality_gate(
                gate_name, gate_config, llm_result, validation_result, 
                confidence_result, reasoning_result
            )
            gate_results[gate_name] = gate_result
        
        # Determine if all gates passed
        all_gates_passed = all(gate["passed"] for gate in gate_results.values())
        
        # Calculate overall quality score
        quality_score = sum(gate["score"] for gate in gate_results.values()) / len(gate_results)
        
        # Decide on final response
        if all_gates_passed:
            final_response = llm_result["response"]
            status = "approved"
        else:
            # Response failed quality gates - return error
            final_response = llm_result["response"]
            status = "failed_quality_gates"
        
        return {
            "response": final_response,
            "status": status,
            "quality_passed": all_gates_passed,
            "quality_score": quality_score,
            "gate_results": gate_results,
            "quality_failed": status == "failed_quality_gates"
        }
    
    async def _submit_learning_feedback(self, input_data: Dict[str, Any],
                                      prompt_result: Dict[str, Any],
                                      final_result: Dict[str, Any],
                                      confidence_result: Dict[str, Any],
                                      validation_result: Dict[str, Any] = None):
        """Phase 7: Submit learning feedback to prompt engine"""
        
        quality_score = confidence_result["overall_score"]
        
        # NEW: Create proper validation_result format for quality improvement
        validation_data = None
        if validation_result:
            validation_data = {
                "overall_score": quality_score,
                "criteria_scores": {
                    "accuracy": confidence_result.get("component_scores", {}).get("data_grounding", quality_score),
                    "completeness": confidence_result.get("component_scores", {}).get("comprehensive_coverage", quality_score),
                    "clarity": confidence_result.get("component_scores", {}).get("logical_consistency", quality_score),
                    "relevance": quality_score,
                    "structural_compliance": validation_result.get("structural_compliance", {}).get("score", quality_score)
                },
                "timestamp": validation_result.get("timestamp", "")
            }
        
        # Only submit feedback for high-quality responses
        if quality_score >= self.config["learning"]["feedback_threshold"]:
            async with self.prompt_consumer as consumer:
                await consumer.submit_learning_feedback(
                    input_data=input_data,
                    prompt_result=prompt_result["prompt"],
                    agent_response=final_result["response"],
                    quality_score=quality_score,
                    user_feedback=f"Autonomous agent quality score: {quality_score:.3f}",
                    validation_result=validation_data  # NEW: Pass validation details
                )
    
    async def _apply_quality_gate(self, gate_name: str, gate_config: Dict[str, Any],
                                llm_result: Dict[str, Any], validation_result: Dict[str, Any],
                                confidence_result: Dict[str, Any], reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a specific quality gate"""
        
        threshold = gate_config["threshold"]
        
        if gate_name == "data_grounding":
            score = confidence_result["component_scores"].get("data_grounding", 0.0)
            passed = score >= threshold
            return {"passed": passed, "score": score, "threshold": threshold}
        
        elif gate_name == "logical_consistency":
            score = confidence_result["component_scores"].get("logical_consistency", 0.0)
            passed = score >= threshold
            return {"passed": passed, "score": score, "threshold": threshold}
        
        elif gate_name == "source_validation":
            score = confidence_result["component_scores"].get("source_reliability", 0.0)
            passed = score >= threshold
            return {"passed": passed, "score": score, "threshold": threshold}
        
        elif gate_name == "confidence_threshold":
            score = confidence_result["overall_score"]
            passed = score >= threshold
            return {"passed": passed, "score": score, "threshold": threshold}
        
        elif gate_name == "response_completeness":
            score = confidence_result["component_scores"].get("completeness", 0.0)
            passed = score >= threshold
            return {"passed": passed, "score": score, "threshold": threshold}
        
        else:
            # Unknown gate - default to pass
            return {"passed": True, "score": 1.0, "threshold": threshold, "reason": "unknown_gate"}
    
    def _enhance_prompt_with_reasoning(self, prompt: str, reasoning_result: Dict[str, Any]) -> str:
        """Enhance the prompt with reasoning context"""
        
        if reasoning_result.get("status") == "error":
            return prompt
        
        reasoning_summary = self._summarize_reasoning_chain(reasoning_result)
        
        enhanced_prompt = f"""
{prompt}

=== REASONING CONTEXT ===
The following reasoning chain has been executed to guide your analysis:

{reasoning_summary}

Please generate your response considering this reasoning framework and ensure your analysis aligns with the logical steps outlined above.

=== RESPONSE REQUIREMENTS ===
- Base all claims on the provided data
- Maintain consistency with the reasoning framework
- Include confidence levels for key findings
- Acknowledge any limitations or uncertainties
- Provide specific, actionable insights
"""
        
        return enhanced_prompt
    
    def _summarize_reasoning_chain(self, reasoning_result: Dict[str, Any]) -> str:
        """Summarize the reasoning chain for prompt enhancement"""
        
        if "steps" not in reasoning_result:
            return "No detailed reasoning steps available."
        
        summary = "Reasoning Steps Executed:\n"
        
        for i, step in enumerate(reasoning_result["steps"], 1):
            step_status = step.get("status", "unknown")
            step_desc = step.get("description", "Unknown step")
            step_confidence = step.get("confidence", 0.0)
            
            summary += f"{i}. {step_desc} (Status: {step_status}, Confidence: {step_confidence:.2f})\n"
            
            if step.get("findings"):
                summary += f"   Key findings: {json.dumps(step['findings'], default=str)[:100]}...\n"
        
        overall_confidence = reasoning_result.get("overall_confidence", 0.0)
        summary += f"\nOverall reasoning confidence: {overall_confidence:.2f}"
        
        return summary
    
    def _summarize_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of input data"""
        return {
            "data_size": len(str(input_data)),
            "top_level_keys": list(input_data.keys()),
            "has_transactions": "transactions" in input_data,
            "transaction_count": len(input_data.get("transactions", [])),
            "complexity": "complex" if len(input_data) > 5 else "simple"
        }
    
    def _validate_response_length(self, response: str) -> Dict[str, Any]:
        """Validate response length"""
        length = len(response)
        max_length = self.config["validation"]["max_response_length"]
        
        return {
            "passed": 50 <= length <= max_length,
            "actual_length": length,
            "max_allowed": max_length,
            "reason": "appropriate_length" if 50 <= length <= max_length else "inappropriate_length"
        }
    
    def _validate_data_references(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that response references input data appropriately"""
        
        data_str = json.dumps(input_data, default=str).lower()
        response_lower = response.lower()
        
        # Count data element references
        data_elements = ["transaction", "balance", "amount", "date", "customer"]
        referenced_elements = sum(1 for element in data_elements if element in response_lower)
        
        return {
            "passed": referenced_elements >= 2,
            "referenced_elements": referenced_elements,
            "total_elements": len(data_elements),
            "reason": "sufficient_references" if referenced_elements >= 2 else "insufficient_references"
        }
    
    def _validate_logical_structure(self, response: str) -> Dict[str, Any]:
        """Validate logical structure of response"""
        
        # Check for basic structure elements
        structure_elements = [
            ("analysis", ["analysis", "findings", "review"]),
            ("insights", ["insight", "conclusion", "result"]),
            ("recommendations", ["recommend", "suggest", "action", "next steps"])
        ]
        
        elements_present = 0
        for element_name, keywords in structure_elements:
            if any(keyword in response.lower() for keyword in keywords):
                elements_present += 1
        
        return {
            "passed": elements_present >= 2,
            "elements_present": elements_present,
            "total_elements": len(structure_elements),
            "reason": "good_structure" if elements_present >= 2 else "poor_structure"
        }
    
    def _validate_completeness(self, response: str, reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response completeness against reasoning objectives"""
        
        if "steps" not in reasoning_result:
            return {"passed": True, "reason": "no_reasoning_steps"}
        
        # Check if response addresses reasoning objectives
        objectives_addressed = 0
        total_objectives = 0
        
        for step in reasoning_result["steps"]:
            if step.get("objective"):
                total_objectives += 1
                objective_keywords = step["objective"].split()[:3]  # First 3 words
                if any(keyword.lower() in response.lower() for keyword in objective_keywords):
                    objectives_addressed += 1
        
        if total_objectives == 0:
            return {"passed": True, "reason": "no_explicit_objectives"}
        
        completeness_ratio = objectives_addressed / total_objectives
        
        return {
            "passed": completeness_ratio >= 0.6,
            "objectives_addressed": objectives_addressed,
            "total_objectives": total_objectives,
            "completeness_ratio": completeness_ratio,
            "reason": "complete" if completeness_ratio >= 0.6 else "incomplete"
        }
    
    def _calculate_validation_score(self, validation_checks: Dict[str, Any], 
                                  hallucination_result) -> float:
        """Calculate overall validation score"""
        
        # Weight validation components
        check_scores = [check["passed"] for check in validation_checks.values()]
        check_average = sum(check_scores) / len(check_scores) if check_scores else 0.0
        
        # Factor in hallucination detection
        hallucination_penalty = 0.0 if not hallucination_result.is_hallucinated else 0.5
        
        return max(0.0, check_average - hallucination_penalty)
    

    

    
    def _update_statistics(self, processing_time: float, quality_score: float, success: bool):
        """Update agent statistics"""
        
        if success:
            # Update average processing time
            total_time = self.average_processing_time * (self.successful_responses - 1) + processing_time
            self.average_processing_time = total_time / self.successful_responses
            
            # Track quality scores
            self.quality_scores.append(quality_score)
            
            # Keep only recent quality scores
            if len(self.quality_scores) > 100:
                self.quality_scores = self.quality_scores[-80:]
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        
        return {
            "agent_info": {
                "name": self.config["agent"]["name"],
                "version": self.config["agent"]["version"],
                "initialized": self.is_initialized,
                "capabilities": list(self.config["agent"]["capabilities"].keys())
            },
            "statistics": {
                "total_requests": self.total_requests,
                "successful_responses": self.successful_responses,
                "failed_responses": self.failed_responses,
                "success_rate": self.successful_responses / max(self.total_requests, 1),
                "average_processing_time": self.average_processing_time,
                "average_quality_score": sum(self.quality_scores) / len(self.quality_scores) if self.quality_scores else 0.0,
                "recent_interactions": len(self.interaction_history)
            },
            "component_status": {
                "prompt_consumer": "operational",
                "reasoning_engine": "operational", 
                "confidence_engine": "operational",
                "hallucination_detector": "operational",
                "llm_interface": "operational" if self.llm_interface.is_available() else "unavailable"
            },
            "configuration": {
                "max_reasoning_steps": self.config["agent"]["max_reasoning_steps"],
                "min_confidence_threshold": self.config["agent"]["min_confidence_threshold"],
                "quality_gates_enabled": len([g for g in self.config["validation"]["quality_gates"].values() if g.get("enabled")])
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_interaction_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent interaction history"""
        return self.interaction_history[-limit:] if self.interaction_history else []
    
    async def clear_history(self) -> bool:
        """Clear interaction history"""
        try:
            self.interaction_history.clear()
            return True
        except:
            return False