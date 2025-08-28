"""
Confidence Scoring Engine - Assesses reliability and certainty of responses
"""

import numpy as np
import json
import re
import math
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConfidenceScore:
    """Container for confidence scoring results"""
    overall_score: float
    component_scores: Dict[str, float]
    uncertainty_indicators: List[str]
    confidence_level: str  # "high", "medium", "low"
    explanation: str
    risk_factors: List[str]
    reliability_indicators: Dict[str, Any]

class ConfidenceEngine:
    """
    Advanced confidence scoring system that evaluates response reliability
    through multiple dimensions and uncertainty quantification
    """
    
    def __init__(self):
        self.model = None
        self._load_confidence_models()
        
        # Confidence thresholds
        self.thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        
        # Scoring weights for different components
        self.weights = {
            "data_grounding": 0.25,
            "logical_consistency": 0.20,
            "completeness": 0.15,
            "specificity": 0.15,
            "uncertainty_handling": 0.10,
            "source_reliability": 0.10,
            "external_validation": 0.05
        }
        
        # Statistics tracking
        self.evaluations_count = 0
        self.score_distribution = {"high": 0, "medium": 0, "low": 0}
        
    def _load_confidence_models(self):
        """Load models for confidence assessment"""
        try:
            # Load sentence transformer for semantic analysis
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Confidence scoring models loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load confidence models: {e}")
            self.model = None
    
    async def calculate_confidence(self, 
                                 response: str,
                                 reasoning_chain: Dict[str, Any],
                                 input_data: Dict[str, Any],
                                 prompt_metadata: Dict[str, Any]) -> ConfidenceScore:
        """
        Calculate comprehensive confidence score for a response
        
        Args:
            response: The generated response text
            reasoning_chain: The reasoning process used
            input_data: Original input data for validation
            prompt_metadata: Metadata from prompt generation
            
        Returns:
            ConfidenceScore object with detailed scoring
        """
        self.evaluations_count += 1
        
        try:
            # Calculate individual confidence components
            component_scores = {}
            
            # 1. Data Grounding Score
            component_scores["data_grounding"] = await self._score_data_grounding(
                response, input_data, reasoning_chain
            )
            
            # 2. Logical Consistency Score
            component_scores["logical_consistency"] = await self._score_logical_consistency(
                response, reasoning_chain
            )
            
            # 3. Completeness Score
            component_scores["completeness"] = await self._score_completeness(
                response, reasoning_chain, prompt_metadata
            )
            
            # 4. Specificity Score
            component_scores["specificity"] = await self._score_specificity(
                response, input_data
            )
            
            # 5. Uncertainty Handling Score
            component_scores["uncertainty_handling"] = await self._score_uncertainty_handling(
                response
            )
            
            # 6. Source Reliability Score
            component_scores["source_reliability"] = await self._score_source_reliability(
                reasoning_chain, prompt_metadata
            )
            
            # 7. External Validation Score
            component_scores["external_validation"] = await self._score_external_validation(
                response, input_data
            )
            
            # Calculate weighted overall score
            overall_score = sum(
                score * self.weights[component] 
                for component, score in component_scores.items()
            )
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(overall_score)
            
            # Identify uncertainty indicators
            uncertainty_indicators = self._identify_uncertainty_indicators(response, reasoning_chain)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(component_scores, reasoning_chain)
            
            # Generate explanation
            explanation = self._generate_confidence_explanation(
                overall_score, component_scores, uncertainty_indicators
            )
            
            # Extract reliability indicators
            reliability_indicators = self._extract_reliability_indicators(
                response, reasoning_chain, component_scores
            )
            
            # Update statistics
            self.score_distribution[confidence_level] += 1
            
            confidence_result = ConfidenceScore(
                overall_score=overall_score,
                component_scores=component_scores,
                uncertainty_indicators=uncertainty_indicators,
                confidence_level=confidence_level,
                explanation=explanation,
                risk_factors=risk_factors,
                reliability_indicators=reliability_indicators
            )
            
            logger.info(f"Confidence score calculated: {overall_score:.3f} ({confidence_level})")
            return confidence_result
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            raise Exception(f"Confidence calculation failed: {str(e)} - NO FALLBACKS")
    
    async def _score_data_grounding(self, response: str, input_data: Dict[str, Any], 
                                  reasoning_chain: Dict[str, Any]) -> float:
        """Score how well the response is grounded in the input data"""
        
        score = 0.0
        
        try:
            # Convert input data to searchable text
            data_text = json.dumps(input_data, default=str).lower()
            response_lower = response.lower()
            
            # Check for direct data references
            data_references = 0
            total_claims = 0
            
            # Extract numerical claims from response
            numbers_in_response = re.findall(r'\d+\.?\d*', response)
            numbers_in_data = re.findall(r'\d+\.?\d*', data_text)
            
            # Check if response numbers are found in data
            grounded_numbers = 0
            for num in numbers_in_response:
                if num in numbers_in_data:
                    grounded_numbers += 1
                total_claims += 1
            
            if total_claims > 0:
                score += 0.4 * (grounded_numbers / total_claims)
            
            # Check for entity/concept grounding
            key_entities = self._extract_key_entities(input_data)
            referenced_entities = 0
            
            for entity in key_entities:
                if entity.lower() in response_lower:
                    referenced_entities += 1
            
            if key_entities:
                score += 0.3 * (referenced_entities / len(key_entities))
            
            # Check reasoning chain grounding
            if reasoning_chain and "steps" in reasoning_chain:
                grounded_steps = 0
                total_steps = len(reasoning_chain["steps"])
                
                for step in reasoning_chain["steps"]:
                    if step.get("sources") and "input_data" in str(step.get("sources", [])):
                        grounded_steps += 1
                
                if total_steps > 0:
                    score += 0.3 * (grounded_steps / total_steps)
            
            # Ensure score is between 0 and 1
            score = min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Error in data grounding scoring: {e}")
            score = 0.5  # Fallback score
        
        return score
    
    async def _score_logical_consistency(self, response: str, 
                                       reasoning_chain: Dict[str, Any]) -> float:
        """Score the logical consistency of the response"""
        
        score = 0.8  # Base score
        
        try:
            # Check for logical contradictions in response
            contradictions = self._find_contradictions(response)
            if contradictions:
                score -= 0.2 * len(contradictions)
            
            # Check reasoning chain consistency
            if reasoning_chain and "steps" in reasoning_chain:
                chain_consistency = self._check_reasoning_consistency(reasoning_chain["steps"])
                score = score * chain_consistency
            
            # Check for unsupported claims
            unsupported_claims = self._find_unsupported_claims(response)
            if unsupported_claims:
                score -= 0.1 * len(unsupported_claims)
            
            # Check for logical flow
            flow_score = self._assess_logical_flow(response)
            score = score * flow_score
            
            score = min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Error in logical consistency scoring: {e}")
            score = 0.7
        
        return score
    
    async def _score_completeness(self, response: str, reasoning_chain: Dict[str, Any],
                                prompt_metadata: Dict[str, Any]) -> float:
        """Score how complete the response is"""
        
        score = 0.0
        
        try:
            # Check if response addresses main objectives
            objectives_met = 0
            total_objectives = 0
            
            # Extract objectives from prompt metadata or reasoning chain
            if reasoning_chain and "steps" in reasoning_chain:
                for step in reasoning_chain["steps"]:
                    if step.get("objective"):
                        total_objectives += 1
                        if self._check_objective_addressed(step["objective"], response):
                            objectives_met += 1
            
            if total_objectives > 0:
                score += 0.4 * (objectives_met / total_objectives)
            else:
                score += 0.4  # Assume complete if no explicit objectives
            
            # Check response length appropriateness
            length_score = self._assess_response_length(response)
            score += 0.2 * length_score
            
            # Check for required sections/components
            required_components = ["analysis", "findings", "recommendations"]
            components_present = 0
            
            for component in required_components:
                if component.lower() in response.lower():
                    components_present += 1
            
            score += 0.2 * (components_present / len(required_components))
            
            # Check for confidence statements
            if any(phrase in response.lower() for phrase in ["confidence", "certain", "likely", "uncertain"]):
                score += 0.1
            
            # Check for actionable insights
            if any(phrase in response.lower() for phrase in ["recommend", "suggest", "should", "action"]):
                score += 0.1
            
            score = min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Error in completeness scoring: {e}")
            score = 0.7
        
        return score
    
    async def _score_specificity(self, response: str, input_data: Dict[str, Any]) -> float:
        """Score how specific and detailed the response is"""
        
        score = 0.0
        
        try:
            # Count specific numerical references
            numbers = re.findall(r'\d+\.?\d*', response)
            score += min(0.3, len(numbers) * 0.05)  # Cap at 0.3
            
            # Count specific dates/times
            dates = re.findall(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}', response)
            score += min(0.2, len(dates) * 0.1)  # Cap at 0.2
            
            # Check for specific financial terms
            financial_terms = [
                "transaction", "balance", "credit", "debit", "amount",
                "revenue", "expense", "cash flow", "ratio"
            ]
            terms_used = sum(1 for term in financial_terms if term in response.lower())
            score += min(0.2, terms_used * 0.03)
            
            # Check detail level (sentences with specific information)
            detailed_sentences = 0
            sentences = response.split('.')
            
            for sentence in sentences:
                if re.search(r'\d+', sentence) and len(sentence.split()) > 5:
                    detailed_sentences += 1
            
            score += min(0.3, detailed_sentences * 0.05)
            
            score = min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Error in specificity scoring: {e}")
            score = 0.6
        
        return score
    
    async def _score_uncertainty_handling(self, response: str) -> float:
        """Score how well the response handles uncertainty"""
        
        score = 0.5  # Base score
        
        try:
            uncertainty_phrases = [
                "uncertain", "unclear", "may", "might", "could", "possibly",
                "likely", "unlikely", "appears", "seems", "suggests",
                "confidence", "probability", "estimate", "approximately"
            ]
            
            uncertainty_count = sum(1 for phrase in uncertainty_phrases 
                                  if phrase in response.lower())
            
            # Good uncertainty handling increases score
            if uncertainty_count > 0:
                score += min(0.3, uncertainty_count * 0.1)
            
            # Check for explicit confidence statements
            confidence_patterns = [
                r'confidence.*?(\d+)%',
                r'(\d+)%.*?confident',
                r'certainty.*?(\d+)%'
            ]
            
            for pattern in confidence_patterns:
                if re.search(pattern, response.lower()):
                    score += 0.2
                    break
            
            # Check for hedging language (good for uncertainty)
            hedging_phrases = ["based on available data", "according to", "analysis suggests"]
            hedging_count = sum(1 for phrase in hedging_phrases 
                              if phrase in response.lower())
            
            if hedging_count > 0:
                score += 0.2
            
            score = min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Error in uncertainty handling scoring: {e}")
            score = 0.5
        
        return score
    
    async def _score_source_reliability(self, reasoning_chain: Dict[str, Any],
                                      prompt_metadata: Dict[str, Any]) -> float:
        """Score the reliability of sources used"""
        
        score = 0.7  # Base score
        
        try:
            # Check if vector database was used (higher reliability)
            if prompt_metadata.get("vector_accelerated"):
                score += 0.2
            
            # Check reasoning chain source quality
            if reasoning_chain and "steps" in reasoning_chain:
                reliable_sources = 0
                total_sources = 0
                
                for step in reasoning_chain["steps"]:
                    sources = step.get("sources", [])
                    total_sources += len(sources)
                    
                    for source in sources:
                        if any(reliable in source for reliable in 
                              ["input_data", "calculation", "analysis"]):
                            reliable_sources += 1
                
                if total_sources > 0:
                    score = score * (reliable_sources / total_sources)
            
            # Check prompt source reliability
            generation_mode = prompt_metadata.get("agentic_metadata", {}).get("generation_mode")
            if generation_mode in ["agentic_enhanced", "vector_accelerated"]:
                score += 0.1
            
            score = min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Error in source reliability scoring: {e}")
            score = 0.7
        
        return score
    
    async def _score_external_validation(self, response: str, input_data: Dict[str, Any]) -> float:
        """Score external validation potential"""
        
        # This is a placeholder for external validation
        # In a full implementation, this could check against external APIs,
        # databases, or validation services
        
        score = 0.7  # Conservative score
        
        try:
            # Check if response includes validation statements
            validation_phrases = [
                "verified", "validated", "confirmed", "cross-checked",
                "industry standard", "regulatory requirement"
            ]
            
            validation_count = sum(1 for phrase in validation_phrases 
                                 if phrase in response.lower())
            
            if validation_count > 0:
                score += min(0.3, validation_count * 0.1)
            
        except Exception as e:
            logger.warning(f"Error in external validation scoring: {e}")
        
        return score
    
    def _determine_confidence_level(self, overall_score: float) -> str:
        """Determine confidence level from overall score"""
        if overall_score >= self.thresholds["high"]:
            return "high"
        elif overall_score >= self.thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _identify_uncertainty_indicators(self, response: str, 
                                       reasoning_chain: Dict[str, Any]) -> List[str]:
        """Identify specific uncertainty indicators"""
        indicators = []
        
        # Check for uncertainty language
        uncertainty_phrases = {
            "may", "might", "could", "possibly", "likely", "unlikely",
            "appears", "seems", "suggests", "indicates", "implies"
        }
        
        for phrase in uncertainty_phrases:
            if phrase in response.lower():
                indicators.append(f"Uncertainty language: '{phrase}'")
        
        # Check for incomplete reasoning steps
        if reasoning_chain and "steps" in reasoning_chain:
            incomplete_steps = [
                step for step in reasoning_chain["steps"]
                if step.get("status") != "validated"
            ]
            if incomplete_steps:
                indicators.append(f"{len(incomplete_steps)} reasoning steps not fully validated")
        
        # Check for missing data indicators
        if any(phrase in response.lower() for phrase in ["missing", "unavailable", "insufficient"]):
            indicators.append("Missing or insufficient data mentioned")
        
        return indicators
    
    def _identify_risk_factors(self, component_scores: Dict[str, float],
                             reasoning_chain: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors affecting confidence"""
        risk_factors = []
        
        # Low component scores
        for component, score in component_scores.items():
            if score < 0.5:
                risk_factors.append(f"Low {component} score: {score:.2f}")
        
        # Reasoning chain risks
        if reasoning_chain:
            if reasoning_chain.get("validation_result", {}).get("passed") is False:
                risk_factors.append("Reasoning validation failed")
            
            failed_steps = sum(1 for step in reasoning_chain.get("steps", [])
                             if step.get("status") == "failed")
            if failed_steps > 0:
                risk_factors.append(f"{failed_steps} reasoning steps failed")
        
        return risk_factors
    
    def _generate_confidence_explanation(self, overall_score: float,
                                       component_scores: Dict[str, float],
                                       uncertainty_indicators: List[str]) -> str:
        """Generate human-readable confidence explanation"""
        
        level = self._determine_confidence_level(overall_score)
        
        explanation = f"Confidence Level: {level.upper()} ({overall_score:.2f})\n\n"
        
        # Component breakdown
        explanation += "Component Scores:\n"
        for component, score in component_scores.items():
            status = "✓" if score >= 0.7 else "⚠" if score >= 0.5 else "✗"
            explanation += f"{status} {component.replace('_', ' ').title()}: {score:.2f}\n"
        
        # Uncertainty indicators
        if uncertainty_indicators:
            explanation += f"\nUncertainty Indicators ({len(uncertainty_indicators)}):\n"
            for indicator in uncertainty_indicators[:3]:  # Show top 3
                explanation += f"• {indicator}\n"
        
        # Recommendation
        if level == "high":
            explanation += "\nRecommendation: Response is highly reliable for decision-making."
        elif level == "medium":
            explanation += "\nRecommendation: Response is useful but consider additional validation."
        else:
            explanation += "\nRecommendation: Use with caution; seek additional validation."
        
        return explanation
    
    def _extract_reliability_indicators(self, response: str, reasoning_chain: Dict[str, Any],
                                      component_scores: Dict[str, float]) -> Dict[str, Any]:
        """Extract specific reliability indicators"""
        
        return {
            "data_points_referenced": len(re.findall(r'\d+\.?\d*', response)),
            "reasoning_steps_completed": len(reasoning_chain.get("steps", [])),
            "validation_passed": reasoning_chain.get("validation_result", {}).get("passed", False),
            "uncertainty_acknowledged": any(
                phrase in response.lower() 
                for phrase in ["uncertain", "may", "might", "confidence"]
            ),
            "sources_cited": sum(
                len(step.get("sources", [])) 
                for step in reasoning_chain.get("steps", [])
            ),
            "strongest_component": max(component_scores.items(), key=lambda x: x[1])[0],
            "weakest_component": min(component_scores.items(), key=lambda x: x[1])[0]
        }
    

    
    def get_statistics(self) -> Dict[str, Any]:
        """Get confidence engine statistics"""
        total = sum(self.score_distribution.values())
        
        return {
            "total_evaluations": self.evaluations_count,
            "score_distribution": self.score_distribution,
            "score_percentages": {
                level: (count / total * 100) if total > 0 else 0
                for level, count in self.score_distribution.items()
            },
            "thresholds": self.thresholds,
            "component_weights": self.weights
        }
    
    # Helper methods for specific analysis tasks
    def _extract_key_entities(self, data: Dict[str, Any]) -> List[str]:
        """Extract key entities from input data"""
        entities = []
        
        # Extract from transaction data
        if "transactions" in data:
            for tx in data["transactions"]:
                if "description" in tx:
                    entities.append(tx["description"])
                if "merchant" in tx:
                    entities.append(tx["merchant"])
        
        # Extract other key fields
        for key in ["customer_id", "account_id", "account_type"]:
            if key in data:
                entities.append(str(data[key]))
        
        return entities
    
    def _find_contradictions(self, text: str) -> List[str]:
        """Find potential contradictions in text"""
        # Simplified contradiction detection
        contradictions = []
        
        sentences = text.split('.')
        for i, sentence in enumerate(sentences):
            for j, other_sentence in enumerate(sentences[i+1:], i+1):
                if self._sentences_contradict(sentence, other_sentence):
                    contradictions.append(f"Sentences {i} and {j} may contradict")
        
        return contradictions
    
    def _sentences_contradict(self, sent1: str, sent2: str) -> bool:
        """Check if two sentences contradict each other"""
        # Very simplified contradiction detection
        opposite_pairs = [
            ("increase", "decrease"), ("high", "low"), ("positive", "negative"),
            ("profitable", "unprofitable"), ("safe", "risky")
        ]
        
        sent1_lower = sent1.lower()
        sent2_lower = sent2.lower()
        
        for word1, word2 in opposite_pairs:
            if word1 in sent1_lower and word2 in sent2_lower:
                return True
            if word2 in sent1_lower and word1 in sent2_lower:
                return True
        
        return False
    
    def _check_reasoning_consistency(self, steps: List[Dict[str, Any]]) -> float:
        """Check consistency across reasoning steps"""
        if not steps:
            return 1.0
        
        consistent_steps = 0
        total_connections = 0
        
        for i, step in enumerate(steps[1:], 1):
            total_connections += 1
            prev_step = steps[i-1]
            
            # Check if current step logically follows from previous
            if self._steps_are_consistent(prev_step, step):
                consistent_steps += 1
        
        return consistent_steps / total_connections if total_connections > 0 else 1.0
    
    def _steps_are_consistent(self, step1: Dict[str, Any], step2: Dict[str, Any]) -> bool:
        """Check if two reasoning steps are consistent"""
        # Simplified consistency check
        # In practice, this would be much more sophisticated
        
        # Check if step2 references or builds on step1
        step1_findings = step1.get("findings", {})
        step2_analysis = step2.get("analysis", "")
        
        # Look for references to previous step concepts
        if step1_findings and isinstance(step1_findings, dict):
            for key in step1_findings.keys():
                if key.lower() in step2_analysis.lower():
                    return True
        
        return True  # Default to consistent if unclear
    
    def _find_unsupported_claims(self, text: str) -> List[str]:
        """Find claims that appear unsupported"""
        # Simplified unsupported claim detection
        unsupported = []
        
        # Look for definitive statements without supporting language
        definitive_patterns = [
            r'definitely (\w+)',
            r'certainly (\w+)',
            r'always (\w+)',
            r'never (\w+)'
        ]
        
        for pattern in definitive_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                unsupported.append(f"Definitive claim: '{match}'")
        
        return unsupported
    
    def _assess_logical_flow(self, text: str) -> float:
        """Assess the logical flow of the text"""
        # Simplified logical flow assessment
        
        # Check for logical connectors
        connectors = [
            "therefore", "thus", "consequently", "as a result",
            "because", "since", "due to", "however", "nevertheless",
            "furthermore", "additionally", "moreover"
        ]
        
        connector_count = sum(1 for connector in connectors if connector in text.lower())
        sentences = len(text.split('.'))
        
        # Good logical flow has appropriate use of connectors
        connector_ratio = connector_count / max(sentences, 1)
        
        # Optimal ratio is around 0.1-0.3
        if 0.1 <= connector_ratio <= 0.3:
            return 1.0
        elif connector_ratio < 0.1:
            return 0.7  # Too few connectors
        else:
            return 0.8  # Too many connectors
    
    def _check_objective_addressed(self, objective: str, response: str) -> bool:
        """Check if an objective is addressed in the response"""
        # Extract key terms from objective
        objective_terms = re.findall(r'\b\w+\b', objective.lower())
        response_lower = response.lower()
        
        # Check if significant portion of objective terms appear in response
        found_terms = sum(1 for term in objective_terms if term in response_lower)
        return found_terms / len(objective_terms) >= 0.5 if objective_terms else False
    
    def _assess_response_length(self, response: str) -> float:
        """Assess if response length is appropriate"""
        word_count = len(response.split())
        
        # Optimal range: 100-1000 words for financial analysis
        if 100 <= word_count <= 1000:
            return 1.0
        elif word_count < 100:
            return 0.6  # Too short
        elif word_count > 2000:
            return 0.7  # Too long
        else:
            return 0.8  # Slightly outside optimal range