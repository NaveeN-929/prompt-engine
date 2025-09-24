"""
Quality Assessor - Evaluates overall response quality and determines quality levels
"""

import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from config import get_config, get_validation_threshold

logger = logging.getLogger(__name__)

class QualityAssessor:
    """
    Assesses overall response quality by combining multiple validation criteria
    and determining appropriate quality levels for training data classification
    """
    
    def __init__(self):
        self.config = get_config()
        self.criteria_config = self.config["validation_criteria"]
        self.quality_thresholds = self.config["quality_thresholds"]
        
        # Quality assessment statistics
        self.total_assessments = 0
        self.quality_distribution = {
            "exemplary": 0,
            "high_quality": 0,
            "acceptable": 0,
            "poor": 0
        }
        
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the quality assessor"""
        try:
            logger.info("Initializing Quality Assessor...")
            
            # Validate configuration
            self._validate_configuration()
            
            self.is_initialized = True
            logger.info("Quality Assessor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize quality assessor: {e}")
            raise
    
    async def assess_quality(self,
                           response_text: str,
                           input_data: Dict[str, Any],
                           criteria_scores: Dict[str, float],
                           response_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assess overall response quality based on multiple criteria
        
        Args:
            response_text: The response text to assess
            input_data: Original input data for context
            criteria_scores: Scores from individual validation criteria
            response_metadata: Additional metadata about the response
            
        Returns:
            Complete quality assessment with score and classification
        """
        if not self.is_initialized:
            raise RuntimeError("Quality assessor not initialized")
        
        self.total_assessments += 1
        start_time = time.time()
        
        try:
            # Calculate weighted overall score
            overall_score = self._calculate_weighted_score(criteria_scores)
            
            # Determine quality level
            quality_level = self._determine_quality_level(overall_score)
            
            # Perform additional quality checks
            additional_checks = await self._perform_additional_checks(
                response_text, input_data, criteria_scores
            )
            
            # Apply quality adjustments based on additional checks
            adjusted_score, adjusted_level = self._apply_quality_adjustments(
                overall_score, quality_level, additional_checks
            )
            
            # Generate quality insights
            quality_insights = self._generate_quality_insights(
                criteria_scores, additional_checks, adjusted_score
            )
            
            # Create detailed quality report
            quality_report = {
                "overall_score": adjusted_score,
                "quality_level": adjusted_level,
                "criteria_breakdown": criteria_scores,
                "additional_checks": additional_checks,
                "quality_insights": quality_insights,
                "assessment_details": {
                    "weighted_base_score": overall_score,
                    "quality_adjustments": adjusted_score - overall_score,
                    "processing_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Update statistics
            self._update_statistics(adjusted_level)
            
            logger.debug(f"Quality assessment completed: {adjusted_level} ({adjusted_score:.3f})")
            
            return {
                "overall_score": adjusted_score,
                "quality_level": adjusted_level,
                "details": quality_report
            }
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            raise RuntimeError(f"Quality assessment failed: {e}. Cannot provide fallback assessment.")
    
    def _calculate_weighted_score(self, criteria_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score from individual criteria scores"""
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for criterion, score in criteria_scores.items():
            if criterion in self.criteria_config:
                weight = self.criteria_config[criterion]["weight"]
                total_weighted_score += score * weight
                total_weight += weight
            else:
                logger.warning(f"Unknown criterion {criterion}, using default weight 0.1")
                total_weighted_score += score * 0.1
                total_weight += 0.1
        
        # Normalize by total weight
        if total_weight > 0:
            return total_weighted_score / total_weight
        else:
            return 0.0
    
    def _determine_quality_level(self, overall_score: float) -> str:
        """Determine quality level based on overall score"""
        
        if overall_score >= self.quality_thresholds["exemplary"]:
            return "exemplary"
        elif overall_score >= self.quality_thresholds["high_quality"]:
            return "high_quality"
        elif overall_score >= self.quality_thresholds["acceptable"]:
            return "acceptable"
        else:
            return "poor"
    
    async def _perform_additional_checks(self,
                                       response_text: str,
                                       input_data: Dict[str, Any],
                                       criteria_scores: Dict[str, float]) -> Dict[str, Any]:
        """Perform additional quality checks beyond basic criteria"""
        
        additional_checks = {}
        
        # Length appropriateness check
        additional_checks["length_check"] = self._check_response_length(response_text)
        
        # Data utilization check
        additional_checks["data_utilization"] = self._check_data_utilization(
            response_text, input_data
        )
        
        # Professional tone check
        additional_checks["professional_tone"] = self._check_professional_tone(response_text)
        
        # Specificity check
        additional_checks["specificity"] = self._check_specificity(response_text)
        
        # Consistency check across criteria
        additional_checks["criteria_consistency"] = self._check_criteria_consistency(criteria_scores)
        
        # Risk assessment check
        additional_checks["risk_assessment"] = self._check_risk_factors(response_text)
        
        return additional_checks
    
    def _check_response_length(self, response_text: str) -> Dict[str, Any]:
        """Check if response length is appropriate"""
        
        length = len(response_text)
        word_count = len(response_text.split())
        
        # Define optimal ranges
        optimal_length_range = (200, 2000)  # Characters
        optimal_word_range = (50, 400)      # Words
        
        length_appropriate = optimal_length_range[0] <= length <= optimal_length_range[1]
        word_count_appropriate = optimal_word_range[0] <= word_count <= optimal_word_range[1]
        
        score = 1.0
        issues = []
        
        if length < optimal_length_range[0]:
            score -= 0.3
            issues.append("Response is too short for comprehensive analysis")
        elif length > optimal_length_range[1]:
            score -= 0.2
            issues.append("Response is excessively long")
        
        if word_count < optimal_word_range[0]:
            score -= 0.2
            issues.append("Insufficient detail provided")
        elif word_count > optimal_word_range[1]:
            score -= 0.1
            issues.append("May contain unnecessary verbosity")
        
        return {
            "score": max(0.0, score),
            "length": length,
            "word_count": word_count,
            "appropriate": length_appropriate and word_count_appropriate,
            "issues": issues
        }
    
    def _check_data_utilization(self, response_text: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check how well the response utilizes the input data"""
        
        response_lower = response_text.lower()
        
        # Extract key data elements
        data_elements = []
        if "transactions" in input_data:
            data_elements.extend(["transaction", "amount", "payment", "deposit"])
        if "account_balance" in input_data:
            data_elements.extend(["balance", "account"])
        if "customer_id" in input_data:
            data_elements.extend(["customer", "client"])
        
        # Count references to data elements
        referenced_elements = 0
        for element in data_elements:
            if element in response_lower:
                referenced_elements += 1
        
        # Calculate utilization score
        if data_elements:
            utilization_score = referenced_elements / len(data_elements)
        else:
            utilization_score = 1.0  # No specific data to reference
        
        # Check for specific numerical references
        numerical_references = len([x for x in response_text.split() if x.replace('.', '').replace(',', '').isdigit()])
        
        return {
            "score": min(1.0, utilization_score + (numerical_references * 0.1)),
            "referenced_elements": referenced_elements,
            "total_elements": len(data_elements),
            "numerical_references": numerical_references,
            "utilization_rate": utilization_score
        }
    
    def _check_professional_tone(self, response_text: str) -> Dict[str, Any]:
        """Check if response maintains professional tone"""
        
        # Professional indicators
        professional_terms = [
            "analysis", "recommend", "suggest", "indicate", "demonstrate",
            "evidence", "data", "findings", "insights", "strategy"
        ]
        
        # Unprofessional indicators
        unprofessional_terms = [
            "awesome", "cool", "weird", "crazy", "super", "totally",
            "basically", "like", "you know", "obviously"
        ]
        
        response_lower = response_text.lower()
        
        professional_count = sum(1 for term in professional_terms if term in response_lower)
        unprofessional_count = sum(1 for term in unprofessional_terms if term in response_lower)
        
        # Calculate professional tone score
        base_score = 0.7
        professional_bonus = min(0.3, professional_count * 0.05)
        unprofessional_penalty = unprofessional_count * 0.1
        
        score = max(0.0, base_score + professional_bonus - unprofessional_penalty)
        
        return {
            "score": score,
            "professional_terms": professional_count,
            "unprofessional_terms": unprofessional_count,
            "is_professional": score >= 0.7
        }
    
    def _check_specificity(self, response_text: str) -> Dict[str, Any]:
        """Check how specific and concrete the response is"""
        
        # Vague terms that reduce specificity
        vague_terms = [
            "some", "many", "several", "various", "different", "numerous",
            "significant", "substantial", "considerable", "generally", "typically"
        ]
        
        # Specific indicators
        specific_indicators = [
            "%", "$", "increase", "decrease", "ratio", "percentage",
            "exactly", "precisely", "specifically", "particularly"
        ]
        
        response_lower = response_text.lower()
        
        vague_count = sum(1 for term in vague_terms if term in response_lower)
        specific_count = sum(1 for term in specific_indicators if term in response_lower)
        
        # Calculate specificity score
        base_score = 0.6
        specific_bonus = min(0.4, specific_count * 0.08)
        vague_penalty = vague_count * 0.05
        
        score = max(0.0, base_score + specific_bonus - vague_penalty)
        
        return {
            "score": score,
            "vague_terms": vague_count,
            "specific_indicators": specific_count,
            "is_specific": score >= 0.7
        }
    
    def _check_criteria_consistency(self, criteria_scores: Dict[str, float]) -> Dict[str, Any]:
        """Check consistency across validation criteria"""
        
        if not criteria_scores:
            return {"score": 0.0, "is_consistent": False}
        
        scores = list(criteria_scores.values())
        
        # Calculate standard deviation
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Lower standard deviation indicates higher consistency
        consistency_score = max(0.0, 1.0 - (std_dev * 2))  # Scale std_dev to 0-1 range
        
        return {
            "score": consistency_score,
            "standard_deviation": std_dev,
            "mean_score": mean_score,
            "is_consistent": std_dev < 0.3  # Threshold for consistency
        }
    
    def _check_risk_factors(self, response_text: str) -> Dict[str, Any]:
        """Check for potential risk factors in recommendations"""
        
        # High-risk terms that should be qualified
        risk_terms = [
            "guaranteed", "certain", "definitely", "always", "never",
            "impossible", "perfect", "best", "worst", "all", "none"
        ]
        
        # Risk mitigation terms (positive)
        mitigation_terms = [
            "consider", "may", "might", "could", "potentially", "likely",
            "depending", "subject to", "with caution", "risk"
        ]
        
        response_lower = response_text.lower()
        
        risk_count = sum(1 for term in risk_terms if term in response_lower)
        mitigation_count = sum(1 for term in mitigation_terms if term in response_lower)
        
        # Calculate risk assessment score
        base_score = 0.8
        risk_penalty = risk_count * 0.15
        mitigation_bonus = min(0.2, mitigation_count * 0.05)
        
        score = max(0.0, min(1.0, base_score - risk_penalty + mitigation_bonus))
        
        return {
            "score": score,
            "risk_terms": risk_count,
            "mitigation_terms": mitigation_count,
            "is_risk_aware": score >= 0.7
        }
    
    def _apply_quality_adjustments(self,
                                 base_score: float,
                                 base_level: str,
                                 additional_checks: Dict[str, Any]) -> Tuple[float, str]:
        """Apply quality adjustments based on additional checks"""
        
        adjusted_score = base_score
        
        # Weight additional checks
        check_weights = {
            "length_check": 0.1,
            "data_utilization": 0.15,
            "professional_tone": 0.1,
            "specificity": 0.1,
            "criteria_consistency": 0.05,
            "risk_assessment": 0.1
        }
        
        # Apply weighted adjustments
        for check_name, check_result in additional_checks.items():
            if check_name in check_weights:
                weight = check_weights[check_name]
                check_score = check_result.get("score", 0.5)
                
                # Adjustment is difference from neutral (0.5) weighted by importance
                adjustment = (check_score - 0.5) * weight
                adjusted_score += adjustment
        
        # Ensure score stays in valid range
        adjusted_score = max(0.0, min(1.0, adjusted_score))
        
        # Recalculate quality level with adjusted score
        adjusted_level = self._determine_quality_level(adjusted_score)
        
        return adjusted_score, adjusted_level
    
    def _generate_quality_insights(self,
                                 criteria_scores: Dict[str, float],
                                 additional_checks: Dict[str, Any],
                                 overall_score: float) -> List[str]:
        """Generate insights about response quality"""
        
        insights = []
        
        # Overall quality insight
        if overall_score >= 0.9:
            insights.append("Exceptional response quality across all dimensions")
        elif overall_score >= 0.75:
            insights.append("High-quality response with minor areas for improvement")
        elif overall_score >= 0.6:
            insights.append("Acceptable quality with several improvement opportunities")
        else:
            insights.append("Response quality needs significant improvement")
        
        # Criteria-specific insights
        for criterion, score in criteria_scores.items():
            threshold = self.criteria_config.get(criterion, {}).get("threshold", 0.7)
            if score < threshold:
                gap = threshold - score
                insights.append(f"{criterion.replace('_', ' ').title()} below threshold by {gap:.2f}")
        
        # Additional check insights
        if additional_checks.get("data_utilization", {}).get("utilization_rate", 0) < 0.5:
            insights.append("Response could better utilize the provided data")
        
        if not additional_checks.get("professional_tone", {}).get("is_professional", True):
            insights.append("Professional tone could be improved")
        
        if not additional_checks.get("specificity", {}).get("is_specific", True):
            insights.append("Response could be more specific and concrete")
        
        return insights
    
    def _validate_configuration(self):
        """Validate the quality assessor configuration"""
        
        # Check that criteria weights sum to approximately 1.0
        total_weight = sum(criterion.get("weight", 0) for criterion in self.criteria_config.values())
        if abs(total_weight - 1.0) > 0.1:
            logger.warning(f"Criteria weights sum to {total_weight}, not 1.0")
        
        # Check that all quality thresholds are valid
        for level, threshold in self.quality_thresholds.items():
            if not 0.0 <= threshold <= 1.0:
                raise ValueError(f"Invalid quality threshold for {level}: {threshold}")
    
    def _update_statistics(self, quality_level: str):
        """Update quality assessment statistics"""
        
        if quality_level in self.quality_distribution:
            self.quality_distribution[quality_level] += 1
    
    def get_assessor_statistics(self) -> Dict[str, Any]:
        """Get quality assessor statistics"""
        
        return {
            "total_assessments": self.total_assessments,
            "quality_distribution": self.quality_distribution,
            "quality_distribution_percentages": {
                level: (count / max(self.total_assessments, 1)) * 100
                for level, count in self.quality_distribution.items()
            },
            "configuration": {
                "criteria_weights": {
                    criterion: config["weight"] 
                    for criterion, config in self.criteria_config.items()
                },
                "quality_thresholds": self.quality_thresholds
            }
        }
    
    async def shutdown(self):
        """Shutdown the quality assessor"""
        logger.info("Quality assessor shutdown completed")
