"""
Quality Improvement Engine - Learns from validation scores to improve prompt quality
This is the missing piece that makes self-learning improve QUALITY, not just SPEED
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import numpy as np


class QualityImprovementEngine:
    """
    Analyzes validation feedback to actively IMPROVE prompt generation
    Not just pattern matching - actual quality-driven learning
    """
    
    def __init__(self, learning_manager):
        self.learning_manager = learning_manager
        
        # Quality improvement strategies
        self.improvement_strategies = {
            'low_accuracy': self._improve_accuracy_strategy,
            'low_completeness': self._improve_completeness_strategy,
            'low_clarity': self._improve_clarity_strategy,
            'low_relevance': self._improve_relevance_strategy,
            'low_structure': self._improve_structure_strategy
        }
        
        # Track improvement history
        self.improvement_history = []
        self.quality_trends = defaultdict(list)
        
        # Prompt enhancement rules learned from feedback
        self.learned_enhancements = {
            'high_quality_patterns': [],  # Patterns that led to high scores
            'low_quality_patterns': [],   # Patterns that led to low scores
            'improvement_rules': []       # Rules for improving prompts
        }
        
        print("🔧 Quality Improvement Engine initialized")
    
    async def analyze_and_improve(self,
                                  input_data: Dict[str, Any],
                                  prompt_used: str,
                                  validation_result: Dict[str, Any],
                                  metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze validation results and generate improvement recommendations
        This is called AFTER validation to learn how to improve
        """
        
        quality_score = validation_result.get('overall_score', 0.5)
        criteria_scores = validation_result.get('criteria_scores', {})
        
        # Track quality trend
        self.quality_trends['overall'].append(quality_score)
        
        # Identify weak areas
        weak_areas = self._identify_weak_areas(criteria_scores)
        
        # Generate improvement strategies
        improvements = {}
        
        if quality_score < 0.75:  # Below target
            print(f"📉 Quality score {quality_score:.2f} - Analyzing for improvements...")
            
            for weak_area, score in weak_areas:
                strategy_key = f"low_{weak_area}"
                if strategy_key in self.improvement_strategies:
                    improvement = await self.improvement_strategies[strategy_key](
                        input_data, prompt_used, score, metadata
                    )
                    improvements[weak_area] = improvement
            
            # Learn what NOT to do
            self._learn_from_failure(prompt_used, weak_areas, metadata)
        
        else:  # High quality
            print(f"✅ Quality score {quality_score:.2f} - Learning success patterns...")
            
            # Learn what TO do
            self._learn_from_success(prompt_used, criteria_scores, metadata)
        
        # Generate improved prompt template
        if improvements:
            improved_template = await self._generate_improved_template(
                prompt_used, improvements, metadata
            )
            
            # Store improvement
            self.improvement_history.append({
                'timestamp': time.time(),
                'original_score': quality_score,
                'weak_areas': weak_areas,
                'improvements': improvements,
                'improved_template': improved_template
            })
            
            return {
                'needs_improvement': True,
                'current_score': quality_score,
                'weak_areas': [area for area, _ in weak_areas],
                'improvements': improvements,
                'improved_template': improved_template,
                'estimated_improvement': self._estimate_improvement(weak_areas)
            }
        
        return {
            'needs_improvement': False,
            'current_score': quality_score,
            'status': 'quality_acceptable'
        }
    
    def _identify_weak_areas(self, criteria_scores: Dict[str, float]) -> List[Tuple[str, float]]:
        """Identify criteria that need improvement"""
        
        weak_areas = []
        thresholds = {
            'accuracy': 0.80,
            'completeness': 0.75,
            'clarity': 0.75,
            'relevance': 0.70,
            'structural_compliance': 0.80
        }
        
        for criterion, score in criteria_scores.items():
            threshold = thresholds.get(criterion, 0.75)
            if score < threshold:
                weak_areas.append((criterion, score))
        
        # Sort by severity (lowest scores first)
        weak_areas.sort(key=lambda x: x[1])
        
        return weak_areas
    
    async def _improve_accuracy_strategy(self,
                                        input_data: Dict[str, Any],
                                        prompt: str,
                                        score: float,
                                        metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy to improve accuracy"""
        
        return {
            'issue': 'Low accuracy - responses not factually correct',
            'root_cause': 'Prompt may not emphasize data grounding',
            'improvements': [
                'Add explicit instruction: "Base ALL statements on provided data ONLY"',
                'Include: "Verify each claim against input data"',
                'Add: "Do not make assumptions beyond the data"',
                'Emphasize: "Quote specific numbers from the data"'
            ],
            'template_additions': [
                '\n**ACCURACY REQUIREMENT:**',
                '- Every statement must be verifiable from input data',
                '- Cite specific numbers and dates from the data',
                '- No assumptions or extrapolations without explicit caveats',
                '- Cross-reference all calculations'
            ],
            'priority': 'HIGH'
        }
    
    async def _improve_completeness_strategy(self,
                                            input_data: Dict[str, Any],
                                            prompt: str,
                                            score: float,
                                            metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy to improve completeness"""
        
        return {
            'issue': 'Low completeness - missing important analysis',
            'root_cause': 'Prompt may not cover all required aspects',
            'improvements': [
                'Add checklist of required analysis points',
                'Include: "Ensure coverage of: revenue, expenses, trends, risks"',
                'Add: "Address all data points provided"',
                'Require: "Analysis of both positive and negative indicators"'
            ],
            'template_additions': [
                '\n**COMPLETENESS CHECKLIST:**',
                '□ Analyze all transaction categories',
                '□ Identify trends and patterns',
                '□ Assess risks and opportunities',
                '□ Provide both short-term and long-term insights',
                '□ Cover cash flow, profitability, and liquidity'
            ],
            'priority': 'HIGH'
        }
    
    async def _improve_clarity_strategy(self,
                                       input_data: Dict[str, Any],
                                       prompt: str,
                                       score: float,
                                       metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy to improve clarity"""
        
        return {
            'issue': 'Low clarity - response hard to understand',
            'root_cause': 'Prompt may not emphasize structure and readability',
            'improvements': [
                'Add: "Use clear, simple language"',
                'Require: "Organize with bullet points and sections"',
                'Include: "Define technical terms"',
                'Add: "Provide executive summary first"'
            ],
            'template_additions': [
                '\n**CLARITY REQUIREMENTS:**',
                '- Use simple, professional language',
                '- Organize with clear headings and bullet points',
                '- Explain technical terms when used',
                '- Start with executive summary',
                '- Use concrete examples'
            ],
            'priority': 'MEDIUM'
        }
    
    async def _improve_relevance_strategy(self,
                                         input_data: Dict[str, Any],
                                         prompt: str,
                                         score: float,
                                         metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy to improve relevance"""
        
        # Detect business context
        context = metadata.get('context', 'business_banking')
        
        return {
            'issue': 'Low relevance - analysis not aligned with business needs',
            'root_cause': f'Prompt may not emphasize {context} context',
            'improvements': [
                f'Add: "Focus on {context} implications"',
                'Include: "Provide actionable business insights"',
                'Require: "Address SME-specific concerns"',
                'Add: "Relate findings to business decisions"'
            ],
            'template_additions': [
                f'\n**{context.upper()} RELEVANCE:**',
                '- Focus on business impact and implications',
                '- Provide actionable recommendations for SMEs',
                '- Address practical business concerns',
                '- Consider cash flow and working capital',
                '- Relate to real-world business decisions'
            ],
            'priority': 'HIGH'
        }
    
    async def _improve_structure_strategy(self,
                                         input_data: Dict[str, Any],
                                         prompt: str,
                                         score: float,
                                         metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy to improve structural compliance"""
        
        return {
            'issue': 'Low structural compliance - not following required format',
            'root_cause': 'Prompt may not clearly specify output structure',
            'improvements': [
                'Add EXPLICIT section markers',
                'Use: "=== SECTION 1: INSIGHTS ===" format',
                'Require: "Exactly two sections"',
                'Add: "No other sections or formatting"'
            ],
            'template_additions': [
                '\n**CRITICAL STRUCTURE REQUIREMENT:**',
                'Your response MUST contain EXACTLY these two sections:',
                '',
                '=== SECTION 1: INSIGHTS ===',
                '[All analytical insights here]',
                '',
                '=== SECTION 2: RECOMMENDATIONS ===',
                '[All actionable recommendations here]',
                '',
                'Use these EXACT section headers. No other sections.'
            ],
            'priority': 'CRITICAL'
        }
    
    def _learn_from_success(self,
                           prompt: str,
                           criteria_scores: Dict[str, float],
                           metadata: Dict[str, Any]):
        """Learn patterns from high-quality results"""
        
        # Extract key patterns from successful prompts
        success_pattern = {
            'prompt_structure': self._extract_prompt_structure(prompt),
            'criteria_scores': criteria_scores,
            'context': metadata.get('context'),
            'data_type': metadata.get('data_type'),
            'timestamp': time.time()
        }
        
        self.learned_enhancements['high_quality_patterns'].append(success_pattern)
        
        # Keep only recent patterns (last 100)
        if len(self.learned_enhancements['high_quality_patterns']) > 100:
            self.learned_enhancements['high_quality_patterns'] = \
                self.learned_enhancements['high_quality_patterns'][-80:]
        
        # Generate improvement rules
        self._generate_improvement_rules()
    
    def _learn_from_failure(self,
                           prompt: str,
                           weak_areas: List[Tuple[str, float]],
                           metadata: Dict[str, Any]):
        """Learn what patterns to AVOID from low-quality results"""
        
        failure_pattern = {
            'prompt_structure': self._extract_prompt_structure(prompt),
            'weak_areas': weak_areas,
            'context': metadata.get('context'),
            'data_type': metadata.get('data_type'),
            'timestamp': time.time()
        }
        
        self.learned_enhancements['low_quality_patterns'].append(failure_pattern)
        
        # Keep only recent patterns
        if len(self.learned_enhancements['low_quality_patterns']) > 100:
            self.learned_enhancements['low_quality_patterns'] = \
                self.learned_enhancements['low_quality_patterns'][-80:]
    
    def _extract_prompt_structure(self, prompt: str) -> Dict[str, Any]:
        """Extract structural patterns from prompt"""
        
        return {
            'length': len(prompt),
            'has_examples': 'example' in prompt.lower(),
            'has_checklist': '□' in prompt or '☐' in prompt,
            'has_sections': '===' in prompt,
            'has_requirements': 'requirement' in prompt.lower(),
            'has_validation': 'verify' in prompt.lower() or 'validate' in prompt.lower()
        }
    
    def _generate_improvement_rules(self):
        """Generate improvement rules from learned patterns"""
        
        if len(self.learned_enhancements['high_quality_patterns']) < 10:
            return  # Need more data
        
        # Analyze what high-quality patterns have in common
        high_quality = self.learned_enhancements['high_quality_patterns'][-20:]
        
        common_features = {
            'has_examples': sum(1 for p in high_quality if p['prompt_structure']['has_examples']) / len(high_quality),
            'has_checklist': sum(1 for p in high_quality if p['prompt_structure']['has_checklist']) / len(high_quality),
            'has_sections': sum(1 for p in high_quality if p['prompt_structure']['has_sections']) / len(high_quality),
            'has_requirements': sum(1 for p in high_quality if p['prompt_structure']['has_requirements']) / len(high_quality),
            'has_validation': sum(1 for p in high_quality if p['prompt_structure']['has_validation']) / len(high_quality)
        }
        
        # Generate rules for features that appear in >70% of high-quality results
        new_rules = []
        for feature, frequency in common_features.items():
            if frequency > 0.7:
                rule = {
                    'feature': feature,
                    'frequency': frequency,
                    'recommendation': f'Include {feature.replace("has_", "")} in prompts',
                    'confidence': frequency
                }
                new_rules.append(rule)
        
        # Update learned rules
        self.learned_enhancements['improvement_rules'] = new_rules
    
    async def _generate_improved_template(self,
                                         original_prompt: str,
                                         improvements: Dict[str, Any],
                                         metadata: Dict[str, Any]) -> str:
        """Generate an improved prompt template based on feedback"""
        
        # Start with original
        improved = original_prompt
        
        # Add improvements for each weak area (highest priority first)
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_improvements = sorted(
            improvements.items(),
            key=lambda x: priority_order.get(x[1].get('priority', 'LOW'), 3)
        )
        
        for area, improvement in sorted_improvements:
            # Add template additions
            if 'template_additions' in improvement:
                additions = '\n'.join(improvement['template_additions'])
                improved += f"\n\n{additions}"
        
        # Apply learned rules
        for rule in self.learned_enhancements['improvement_rules']:
            if rule['confidence'] > 0.8:
                feature = rule['feature']
                if feature == 'has_checklist' and '□' not in improved:
                    improved += '\n\n**QUALITY CHECKLIST:**\n□ Verify all key points covered'
                elif feature == 'has_validation' and 'verify' not in improved.lower():
                    improved += '\n\n**VALIDATION:** Cross-check all statements against input data'
        
        return improved
    
    def _estimate_improvement(self, weak_areas: List[Tuple[str, float]]) -> float:
        """Estimate potential quality improvement"""
        
        if not weak_areas:
            return 0.0
        
        # Calculate improvement potential
        total_gap = sum(0.85 - score for _, score in weak_areas)  # Target is 0.85
        avg_gap = total_gap / len(weak_areas)
        
        # Estimate 60% of gap can be closed with improvements
        estimated_improvement = avg_gap * 0.6
        
        return min(estimated_improvement, 0.25)  # Cap at 25% improvement
    
    async def get_improved_prompt_for_input(self,
                                           input_data: Dict[str, Any],
                                           context: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get an improved prompt template for given input based on learned improvements
        This is the KEY method that makes quality improve over time
        """
        
        # Find similar past interactions
        similar_cases = await self._find_similar_past_cases(input_data, context)
        
        if not similar_cases:
            return None
        
        # Analyze what worked and what didn't
        high_quality_cases = [c for c in similar_cases if c['quality_score'] > 0.80]
        low_quality_cases = [c for c in similar_cases if c['quality_score'] < 0.65]
        
        if not high_quality_cases:
            return None
        
        # Extract best practices from high-quality cases
        best_prompt = max(high_quality_cases, key=lambda x: x['quality_score'])
        
        # Apply learned improvements
        improved_prompt = best_prompt['prompt']
        
        # Add improvements learned from low-quality cases
        if low_quality_cases:
            common_weak_areas = self._find_common_weak_areas(low_quality_cases)
            for weak_area in common_weak_areas:
                if weak_area in self.improvement_strategies:
                    improvement = await self.improvement_strategies[f"low_{weak_area}"](
                        input_data, improved_prompt, 0.5, {'context': context}
                    )
                    if 'template_additions' in improvement:
                        additions = '\n'.join(improvement['template_additions'])
                        improved_prompt += f"\n\n{additions}"
        
        return {
            'improved_prompt': improved_prompt,
            'based_on_quality': best_prompt['quality_score'],
            'improvements_applied': len(common_weak_areas) if low_quality_cases else 0,
            'confidence': best_prompt['quality_score']
        }
    
    async def _find_similar_past_cases(self,
                                      input_data: Dict[str, Any],
                                      context: Optional[str]) -> List[Dict[str, Any]]:
        """Find similar past cases with quality scores"""
        
        # Get from learning manager
        if not self.learning_manager or not hasattr(self.learning_manager, 'interaction_history'):
            return []
        
        similar_cases = []
        for interaction in self.learning_manager.interaction_history[-100:]:  # Last 100
            if interaction.get('quality_score') and interaction.get('quality_score') > 0:
                similar_cases.append({
                    'input_data': interaction['input_data'],
                    'prompt': interaction['prompt_result'],
                    'quality_score': interaction['quality_score'],
                    'criteria_scores': interaction.get('validation_result', {}).get('criteria_scores', {})
                })
        
        return similar_cases
    
    def _find_common_weak_areas(self, low_quality_cases: List[Dict[str, Any]]) -> List[str]:
        """Find commonly weak areas across multiple cases"""
        
        weak_area_counts = defaultdict(int)
        
        for case in low_quality_cases:
            criteria_scores = case.get('criteria_scores', {})
            for criterion, score in criteria_scores.items():
                if score < 0.70:
                    weak_area_counts[criterion] += 1
        
        # Return areas weak in >50% of cases
        threshold = len(low_quality_cases) * 0.5
        common_weak = [area for area, count in weak_area_counts.items() if count >= threshold]
        
        return common_weak
    
    def get_quality_improvement_report(self) -> Dict[str, Any]:
        """Generate report on quality improvements over time"""
        
        if len(self.quality_trends['overall']) < 10:
            return {'status': 'insufficient_data'}
        
        recent_quality = np.mean(self.quality_trends['overall'][-20:])
        early_quality = np.mean(self.quality_trends['overall'][:20])
        improvement = recent_quality - early_quality
        
        return {
            'total_interactions': len(self.quality_trends['overall']),
            'early_avg_quality': early_quality,
            'recent_avg_quality': recent_quality,
            'quality_improvement': improvement,
            'improvement_percentage': (improvement / early_quality * 100) if early_quality > 0 else 0,
            'improvements_generated': len(self.improvement_history),
            'learned_rules': len(self.learned_enhancements['improvement_rules']),
            'high_quality_patterns': len(self.learned_enhancements['high_quality_patterns']),
            'status': 'improving' if improvement > 0.05 else 'stable'
        }

