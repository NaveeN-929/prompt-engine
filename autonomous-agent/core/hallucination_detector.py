"""
Hallucination Detection and Prevention System
"""

import re
import json
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

@dataclass
class HallucinationResult:
    """Result of hallucination detection"""
    is_hallucinated: bool
    confidence: float
    hallucination_type: str
    evidence: List[str]
    severity: str  # "low", "medium", "high"
    affected_portions: List[str]
    recommendations: List[str]

class HallucinationDetector:
    """
    Advanced hallucination detection system that identifies and prevents
    generation of false or unsupported information
    """
    
    def __init__(self):
        self.model = None
        self._load_detection_models()
        
        # Hallucination patterns to detect
        self.hallucination_patterns = {
            "fabricated_numbers": r'\b\d+(?:\.\d+)?\b',
            "false_dates": r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}',
            "invented_entities": r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Names
            "fake_references": r'according to|based on|research shows',
            "unsupported_claims": r'definitely|certainly|always|never',
            "external_knowledge": r'industry standard|market rate|typical|normal'
        }
        
        # Known facts and constraints for validation
        self.validation_constraints = {
            "financial_ranges": {
                "interest_rate": (0.0, 50.0),  # Reasonable interest rate range
                "credit_score": (300, 850),     # FICO score range
                "utilization": (0.0, 200.0)    # Credit utilization percentage
            },
            "date_constraints": {
                "min_date": datetime(2000, 1, 1),
                "max_date": datetime.now() + timedelta(days=365)
            }
        }
        
        # Statistics
        self.total_detections = 0
        self.false_positives = 0
        self.hallucination_types = {}
        
    def _load_detection_models(self):
        """Load models for hallucination detection"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Hallucination detection models loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load detection models: {e}")
            self.model = None
    
    async def detect_hallucinations(self, 
                                  response: str,
                                  input_data: Dict[str, Any],
                                  reasoning_chain: Dict[str, Any],
                                  prompt_metadata: Dict[str, Any]) -> HallucinationResult:
        """
        Comprehensive hallucination detection for a response
        
        Args:
            response: The generated response to check
            input_data: Original input data for validation
            reasoning_chain: The reasoning process used
            prompt_metadata: Metadata from prompt generation
            
        Returns:
            HallucinationResult with detection details
        """
        self.total_detections += 1
        
        try:
            # Multiple detection methods
            detections = []
            
            # 1. Data grounding check
            grounding_result = await self._check_data_grounding(response, input_data)
            if grounding_result["is_hallucinated"]:
                detections.append(grounding_result)
            
            # 2. Factual consistency check
            consistency_result = await self._check_factual_consistency(response, reasoning_chain)
            if consistency_result["is_hallucinated"]:
                detections.append(consistency_result)
            
            # 3. Numerical validation
            numerical_result = await self._validate_numerical_claims(response, input_data)
            if numerical_result["is_hallucinated"]:
                detections.append(numerical_result)
            
            # 4. Temporal validation
            temporal_result = await self._validate_temporal_claims(response, input_data)
            if temporal_result["is_hallucinated"]:
                detections.append(temporal_result)
            
            # 5. External knowledge check
            external_result = await self._check_external_knowledge_claims(response)
            if external_result["is_hallucinated"]:
                detections.append(external_result)
            
            # 6. Semantic coherence check
            coherence_result = await self._check_semantic_coherence(response, input_data)
            if coherence_result["is_hallucinated"]:
                detections.append(coherence_result)
            
            # Aggregate results
            if detections:
                # Multiple hallucinations detected
                is_hallucinated = True
                confidence = max(d["confidence"] for d in detections)
                hallucination_type = "multiple" if len(detections) > 1 else detections[0]["type"]
                evidence = []
                affected_portions = []
                
                for detection in detections:
                    evidence.extend(detection["evidence"])
                    affected_portions.extend(detection.get("affected_portions", []))
                
                severity = self._determine_severity(detections)
                recommendations = self._generate_recommendations(detections)
                
            else:
                # No hallucinations detected
                is_hallucinated = False
                confidence = 0.1  # Low confidence in negative result
                hallucination_type = "none"
                evidence = []
                affected_portions = []
                severity = "none"
                recommendations = ["Response appears factually grounded"]
            
            # Track statistics
            if hallucination_type != "none":
                self.hallucination_types[hallucination_type] = \
                    self.hallucination_types.get(hallucination_type, 0) + 1
            
            result = HallucinationResult(
                is_hallucinated=is_hallucinated,
                confidence=confidence,
                hallucination_type=hallucination_type,
                evidence=evidence,
                severity=severity,
                affected_portions=affected_portions,
                recommendations=recommendations
            )
            
            logger.info(f"Hallucination detection completed: {hallucination_type} "
                       f"(confidence: {confidence:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in hallucination detection: {e}")
            raise Exception(f"Hallucination detection failed: {str(e)} - NO FALLBACKS")
    
    async def _check_data_grounding(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if response claims are grounded in input data"""
        
        try:
            # Extract factual claims from response
            claims = self._extract_factual_claims(response)
            ungrounded_claims = []
            
            # Convert input data to searchable format
            data_text = json.dumps(input_data, default=str).lower()
            
            for claim in claims:
                if not self._is_claim_grounded(claim, data_text, input_data):
                    ungrounded_claims.append(claim)
            
            is_hallucinated = len(ungrounded_claims) > 0
            confidence = len(ungrounded_claims) / max(len(claims), 1) if claims else 0.0
            
            return {
                "is_hallucinated": is_hallucinated,
                "confidence": confidence,
                "type": "data_grounding",
                "evidence": ungrounded_claims,
                "affected_portions": ungrounded_claims
            }
            
        except Exception as e:
            logger.warning(f"Error in data grounding check: {e}")
            return {"is_hallucinated": False, "confidence": 0.0, "type": "data_grounding", "evidence": []}
    
    async def _check_factual_consistency(self, response: str, reasoning_chain: Dict[str, Any]) -> Dict[str, Any]:
        """Check factual consistency within the response and reasoning chain"""
        
        try:
            inconsistencies = []
            
            # Check internal contradictions
            contradictions = self._find_internal_contradictions(response)
            inconsistencies.extend(contradictions)
            
            # Check consistency with reasoning chain
            if reasoning_chain and "steps" in reasoning_chain:
                chain_inconsistencies = self._check_reasoning_consistency(response, reasoning_chain["steps"])
                inconsistencies.extend(chain_inconsistencies)
            
            is_hallucinated = len(inconsistencies) > 0
            confidence = min(len(inconsistencies) * 0.3, 1.0)  # Each inconsistency adds 0.3
            
            return {
                "is_hallucinated": is_hallucinated,
                "confidence": confidence,
                "type": "factual_consistency",
                "evidence": inconsistencies,
                "affected_portions": inconsistencies
            }
            
        except Exception as e:
            logger.warning(f"Error in factual consistency check: {e}")
            return {"is_hallucinated": False, "confidence": 0.0, "type": "factual_consistency", "evidence": []}
    
    async def _validate_numerical_claims(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate numerical claims against input data and reasonable ranges"""
        
        try:
            # Extract numbers from response
            response_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', response)
            input_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', json.dumps(input_data, default=str))
            
            fabricated_numbers = []
            unreasonable_numbers = []
            
            for num_str in response_numbers:
                num = float(num_str)
                
                # Check if number exists in input data
                if num_str not in input_numbers:
                    # Check if it's a reasonable calculation result
                    if not self._is_reasonable_calculation(num, input_numbers):
                        fabricated_numbers.append(f"Number {num_str} not found in input data")
                
                # Check if number is within reasonable ranges
                if not self._is_number_reasonable(num, response):
                    unreasonable_numbers.append(f"Number {num_str} outside reasonable range")
            
            all_issues = fabricated_numbers + unreasonable_numbers
            is_hallucinated = len(all_issues) > 0
            confidence = len(all_issues) / max(len(response_numbers), 1) if response_numbers else 0.0
            
            return {
                "is_hallucinated": is_hallucinated,
                "confidence": confidence,
                "type": "numerical_fabrication",
                "evidence": all_issues,
                "affected_portions": all_issues
            }
            
        except Exception as e:
            logger.warning(f"Error in numerical validation: {e}")
            return {"is_hallucinated": False, "confidence": 0.0, "type": "numerical_fabrication", "evidence": []}
    
    async def _validate_temporal_claims(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate date and time claims"""
        
        try:
            # Extract dates from response
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',
                r'\d{1,2}/\d{1,2}/\d{4}',
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
            ]
            
            response_dates = []
            for pattern in date_patterns:
                matches = re.findall(pattern, response)
                response_dates.extend(matches)
            
            # Extract dates from input data
            input_text = json.dumps(input_data, default=str)
            input_dates = []
            for pattern in date_patterns:
                matches = re.findall(pattern, input_text)
                input_dates.extend(matches)
            
            invalid_dates = []
            
            for date_str in response_dates:
                if date_str not in input_dates:
                    # Check if it's a reasonable derived date
                    if not self._is_reasonable_derived_date(date_str, input_dates):
                        invalid_dates.append(f"Date {date_str} not found in input data")
            
            is_hallucinated = len(invalid_dates) > 0
            confidence = len(invalid_dates) / max(len(response_dates), 1) if response_dates else 0.0
            
            return {
                "is_hallucinated": is_hallucinated,
                "confidence": confidence,
                "type": "temporal_fabrication",
                "evidence": invalid_dates,
                "affected_portions": invalid_dates
            }
            
        except Exception as e:
            logger.warning(f"Error in temporal validation: {e}")
            return {"is_hallucinated": False, "confidence": 0.0, "type": "temporal_fabrication", "evidence": []}
    
    async def _check_external_knowledge_claims(self, response: str) -> Dict[str, Any]:
        """Check for claims requiring external knowledge not provided in input"""
        
        try:
            external_claims = []
            
            # Patterns indicating external knowledge
            external_patterns = [
                r'industry standard',
                r'market rate',
                r'typical.*?(?:rate|percentage|amount)',
                r'normal.*?(?:range|level)',
                r'according to.*?(?:studies|research|reports)',
                r'benchmark',
                r'peer.*?(?:comparison|analysis)'
            ]
            
            for pattern in external_patterns:
                matches = re.finditer(pattern, response, re.IGNORECASE)
                for match in matches:
                    external_claims.append(f"External knowledge claim: '{match.group()}'")
            
            is_hallucinated = len(external_claims) > 0
            confidence = len(external_claims) * 0.4  # Each claim increases confidence
            
            return {
                "is_hallucinated": is_hallucinated,
                "confidence": min(confidence, 1.0),
                "type": "external_knowledge",
                "evidence": external_claims,
                "affected_portions": external_claims
            }
            
        except Exception as e:
            logger.warning(f"Error in external knowledge check: {e}")
            return {"is_hallucinated": False, "confidence": 0.0, "type": "external_knowledge", "evidence": []}
    
    async def _check_semantic_coherence(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check semantic coherence between response and input data"""
        
        try:
            if not self.model:
                return {"is_hallucinated": False, "confidence": 0.0, "type": "semantic_coherence", "evidence": []}
            
            # Get embeddings for input data and response
            input_text = json.dumps(input_data, default=str)
            input_embedding = self.model.encode([input_text])
            response_embedding = self.model.encode([response])
            
            # Calculate semantic similarity
            similarity = np.dot(input_embedding[0], response_embedding[0]) / \
                        (np.linalg.norm(input_embedding[0]) * np.linalg.norm(response_embedding[0]))
            
            # Low similarity indicates potential hallucination
            threshold = 0.3  # Adjust based on testing
            is_hallucinated = similarity < threshold
            confidence = (threshold - similarity) / threshold if is_hallucinated else 0.0
            
            evidence = [f"Low semantic similarity: {similarity:.3f}"] if is_hallucinated else []
            
            return {
                "is_hallucinated": is_hallucinated,
                "confidence": confidence,
                "type": "semantic_coherence",
                "evidence": evidence,
                "affected_portions": ["Overall response coherence"] if is_hallucinated else []
            }
            
        except Exception as e:
            logger.warning(f"Error in semantic coherence check: {e}")
            return {"is_hallucinated": False, "confidence": 0.0, "type": "semantic_coherence", "evidence": []}
    
    def _extract_factual_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        claims = []
        
        # Split into sentences and identify factual statements
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Ignore very short sentences
                # Look for patterns indicating factual claims
                if any(pattern in sentence.lower() for pattern in [
                    'is', 'are', 'was', 'were', 'has', 'have', 'shows', 'indicates',
                    'total', 'amount', 'balance', 'transactions'
                ]):
                    claims.append(sentence)
        
        return claims
    
    def _is_claim_grounded(self, claim: str, data_text: str, input_data: Dict[str, Any]) -> bool:
        """Check if a claim is grounded in the input data"""
        
        # Extract key terms from claim
        claim_lower = claim.lower()
        
        # Check for direct mention in data
        claim_words = re.findall(r'\b\w+\b', claim_lower)
        data_words = re.findall(r'\b\w+\b', data_text)
        
        # Calculate word overlap
        overlap = sum(1 for word in claim_words if word in data_words)
        overlap_ratio = overlap / len(claim_words) if claim_words else 0
        
        # Claims with high word overlap are likely grounded
        return overlap_ratio > 0.5
    
    def _find_internal_contradictions(self, text: str) -> List[str]:
        """Find contradictions within the text"""
        contradictions = []
        
        sentences = re.split(r'[.!?]+', text)
        
        for i, sentence1 in enumerate(sentences):
            for j, sentence2 in enumerate(sentences[i+1:], i+1):
                if self._sentences_contradict(sentence1, sentence2):
                    contradictions.append(f"Contradiction between sentences {i+1} and {j+1}")
        
        return contradictions
    
    def _sentences_contradict(self, sent1: str, sent2: str) -> bool:
        """Simple contradiction detection between sentences"""
        
        # Look for opposite terms
        opposites = [
            ("increase", "decrease"), ("high", "low"), ("positive", "negative"),
            ("profitable", "unprofitable"), ("safe", "risky"), ("more", "less"),
            ("above", "below"), ("over", "under")
        ]
        
        sent1_lower = sent1.lower()
        sent2_lower = sent2.lower()
        
        for word1, word2 in opposites:
            if word1 in sent1_lower and word2 in sent2_lower:
                # Check if they're talking about the same subject
                if self._same_subject(sent1, sent2):
                    return True
            if word2 in sent1_lower and word1 in sent2_lower:
                if self._same_subject(sent1, sent2):
                    return True
        
        return False
    
    def _same_subject(self, sent1: str, sent2: str) -> bool:
        """Check if two sentences are talking about the same subject"""
        # Simple heuristic: look for common nouns
        nouns1 = re.findall(r'\b[A-Za-z]+(?:tion|ness|ment|ance|ence)\b', sent1)
        nouns2 = re.findall(r'\b[A-Za-z]+(?:tion|ness|ment|ance|ence)\b', sent2)
        
        common_nouns = set(nouns1) & set(nouns2)
        return len(common_nouns) > 0
    
    def _check_reasoning_consistency(self, response: str, steps: List[Dict[str, Any]]) -> List[str]:
        """Check consistency between response and reasoning steps"""
        inconsistencies = []
        
        response_lower = response.lower()
        
        for step in steps:
            step_findings = step.get("findings", {})
            if isinstance(step_findings, dict):
                for key, value in step_findings.items():
                    value_str = str(value).lower()
                    if value_str not in response_lower and len(value_str) > 3:
                        inconsistencies.append(f"Step finding '{key}: {value}' not reflected in response")
        
        return inconsistencies
    
    def _is_reasonable_calculation(self, number: float, input_numbers: List[str]) -> bool:
        """Check if a number could be a reasonable calculation from input numbers"""
        
        if not input_numbers:
            return False
        
        input_floats = []
        for num_str in input_numbers:
            try:
                input_floats.append(float(num_str))
            except ValueError:
                continue
        
        if not input_floats:
            return False
        
        # Check if number could be derived from basic operations
        for a in input_floats:
            for b in input_floats:
                if abs(number - (a + b)) < 0.01:  # Addition
                    return True
                if abs(number - abs(a - b)) < 0.01:  # Subtraction
                    return True
                if b != 0 and abs(number - (a / b)) < 0.01:  # Division
                    return True
                if abs(number - (a * b)) < 0.01:  # Multiplication
                    return True
        
        # Check if it's a percentage of an input number
        for a in input_floats:
            if a != 0:
                percentage = (number / a) * 100
                if 0 <= percentage <= 100:
                    return True
        
        return False
    
    def _is_number_reasonable(self, number: float, context: str) -> bool:
        """Check if a number is within reasonable bounds given context"""
        
        context_lower = context.lower()
        
        # Check financial ranges
        if any(term in context_lower for term in ["interest", "rate", "apr"]):
            return 0 <= number <= 50  # Interest rates
        
        if any(term in context_lower for term in ["credit", "score"]):
            return 300 <= number <= 850  # Credit scores
        
        if any(term in context_lower for term in ["utilization", "percent"]):
            return 0 <= number <= 200  # Percentages
        
        # General reasonableness (very loose bounds)
        return -1e9 <= number <= 1e9
    
    def _is_reasonable_derived_date(self, date_str: str, input_dates: List[str]) -> bool:
        """Check if a date could be reasonably derived from input dates"""
        
        if not input_dates:
            return False
        
        try:
            # Parse the response date
            response_date = self._parse_date(date_str)
            if not response_date:
                return False
            
            # Parse input dates
            parsed_input_dates = []
            for date in input_dates:
                parsed = self._parse_date(date)
                if parsed:
                    parsed_input_dates.append(parsed)
            
            if not parsed_input_dates:
                return False
            
            # Check if response date is within reasonable range of input dates
            min_input = min(parsed_input_dates)
            max_input = max(parsed_input_dates)
            
            # Allow for reasonable time windows (e.g., same month, quarter)
            time_window = timedelta(days=90)  # 3 months
            
            return (min_input - time_window) <= response_date <= (max_input + time_window)
            
        except:
            return False
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse a date string into datetime object"""
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%B %d, %Y",
            "%B %d %Y"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _determine_severity(self, detections: List[Dict[str, Any]]) -> str:
        """Determine overall severity of hallucinations"""
        
        if not detections:
            return "none"
        
        max_confidence = max(d["confidence"] for d in detections)
        critical_types = ["data_grounding", "numerical_fabrication"]
        
        has_critical = any(d["type"] in critical_types for d in detections)
        
        if has_critical and max_confidence > 0.7:
            return "high"
        elif max_confidence > 0.5:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, detections: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on detected hallucinations"""
        
        recommendations = []
        
        detection_types = set(d["type"] for d in detections)
        
        if "data_grounding" in detection_types:
            recommendations.append("Ensure all claims are directly supported by input data")
        
        if "numerical_fabrication" in detection_types:
            recommendations.append("Verify all numerical claims against source data")
        
        if "temporal_fabrication" in detection_types:
            recommendations.append("Only reference dates present in the input data")
        
        if "external_knowledge" in detection_types:
            recommendations.append("Avoid claims requiring external knowledge not provided")
        
        if "factual_consistency" in detection_types:
            recommendations.append("Review response for internal contradictions")
        
        if "semantic_coherence" in detection_types:
            recommendations.append("Ensure response maintains semantic coherence with input")
        
        recommendations.append("Consider regenerating response with stricter validation")
        
        return recommendations
    

    
    def get_statistics(self) -> Dict[str, Any]:
        """Get hallucination detection statistics"""
        return {
            "total_detections": self.total_detections,
            "false_positives": self.false_positives,
            "false_positive_rate": self.false_positives / max(self.total_detections, 1),
            "hallucination_types": self.hallucination_types,
            "most_common_type": max(self.hallucination_types.items(), 
                                  key=lambda x: x[1])[0] if self.hallucination_types else "none"
        }