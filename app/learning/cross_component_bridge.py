"""
Cross-Component Learning Bridge - Shares insights across prompt engine, agent, and validator
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CrossComponentBridge:
    """
    Bridges learning across all components:
    - Prompt Engine learnings → Autonomous Agent
    - Autonomous Agent learnings → Validator
    - Validator learnings → Prompt Engine
    Creating a complete feedback loop
    """
    
    def __init__(self, learning_manager, knowledge_graph_service):
        self.learning_manager = learning_manager
        self.knowledge_graph = knowledge_graph_service
        
        # Component connections
        self.component_endpoints = {
            'prompt_engine': None,  # Will be set externally
            'autonomous_agent': None,
            'validator': None
        }
        
        # Cross-learning statistics
        self.insights_shared = {
            'prompt_to_agent': 0,
            'agent_to_validator': 0,
            'validator_to_prompt': 0,
            'full_cycle': 0
        }
        
        # Insight queue for async processing
        self.insight_queue = asyncio.Queue()
        
        print("🌉 Cross-Component Learning Bridge initialized")
    
    def register_component(self, component_name: str, component_ref: Any):
        """Register a component for cross-learning"""
        
        if component_name in self.component_endpoints:
            self.component_endpoints[component_name] = component_ref
            print(f"✅ Registered {component_name} for cross-component learning")
    
    async def share_prompt_insights_to_agent(self,
                                            prompt_metadata: Dict[str, Any],
                                            quality_score: float) -> Dict[str, Any]:
        """
        Share prompt generation insights to autonomous agent
        Helps agent understand what prompt patterns work best
        """
        
        try:
            # Extract key insights from prompt generation
            insights = {
                'prompt_patterns': self._extract_prompt_patterns(prompt_metadata),
                'successful_templates': self._identify_successful_templates(prompt_metadata),
                'context_preferences': self._analyze_context_preferences(prompt_metadata),
                'quality_score': quality_score,
                'timestamp': time.time()
            }
            
            # Store in knowledge graph
            await self.knowledge_graph.store_prompt_knowledge(
                input_data=prompt_metadata.get('input_data', {}),
                prompt=prompt_metadata.get('prompt', ''),
                metadata=prompt_metadata,
                quality_score=quality_score
            )
            
            self.insights_shared['prompt_to_agent'] += 1
            
            logger.info(f"📤 Shared prompt insights to agent (quality: {quality_score:.3f})")
            
            return {
                'status': 'success',
                'insights_shared': insights,
                'component': 'prompt_engine->agent'
            }
            
        except Exception as e:
            logger.error(f"Failed to share prompt insights: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def share_agent_insights_to_validator(self,
                                               analysis_result: Dict[str, Any],
                                               reasoning_chain: Dict[str, Any],
                                               confidence_score: Dict[str, Any]) -> Dict[str, Any]:
        """
        Share agent analysis insights to validator
        Helps validator understand analysis patterns and expected quality
        """
        
        try:
            # Extract key insights from analysis
            insights = {
                'reasoning_quality': self._assess_reasoning_quality(reasoning_chain),
                'analysis_patterns': self._extract_analysis_patterns(analysis_result),
                'confidence_indicators': confidence_score,
                'complexity_level': self._assess_complexity(analysis_result),
                'timestamp': time.time()
            }
            
            # Store in knowledge graph
            await self.knowledge_graph.store_analysis_knowledge(
                analysis_result=analysis_result,
                quality_score=confidence_score.get('overall_score', 0.5),
                reasoning_chain=reasoning_chain
            )
            
            # Store reasoning patterns
            if confidence_score.get('overall_score', 0) > 0.7:
                await self.knowledge_graph.store_reasoning_pattern(
                    reasoning_chain=reasoning_chain,
                    input_data=analysis_result.get('input_data', {}),
                    success_score=confidence_score.get('overall_score', 0.5)
                )
            
            self.insights_shared['agent_to_validator'] += 1
            
            logger.info(f"📤 Shared agent insights to validator")
            
            return {
                'status': 'success',
                'insights_shared': insights,
                'component': 'agent->validator'
            }
            
        except Exception as e:
            logger.error(f"Failed to share agent insights: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def share_validator_insights_to_prompt(self,
                                                validation_result: Dict[str, Any],
                                                input_data: Dict[str, Any],
                                                response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Share validation insights back to prompt engine
        Completes the feedback loop - validator tells prompt engine what works
        """
        
        try:
            # Extract key insights from validation
            insights = {
                'quality_patterns': self._extract_quality_patterns(validation_result),
                'successful_criteria': self._identify_successful_criteria(validation_result),
                'improvement_areas': validation_result.get('recommendations', []),
                'quality_level': validation_result.get('quality_level', 'unknown'),
                'overall_score': validation_result.get('overall_score', 0.0),
                'timestamp': time.time()
            }
            
            # Store in knowledge graph
            await self.knowledge_graph.store_validation_knowledge(
                validation_result=validation_result,
                input_data=input_data,
                response_data=response_data
            )
            
            # Feed back to learning manager
            await self.learning_manager.learn_from_complete_interaction(
                input_data=input_data,
                prompt_result=response_data.get('prompt_metadata', {}),
                analysis_result=response_data,
                validation_result=validation_result,
                metadata={'source': 'validator_feedback'}
            )
            
            self.insights_shared['validator_to_prompt'] += 1
            self.insights_shared['full_cycle'] += 1  # Complete cycle
            
            logger.info(f"📤 Shared validator insights to prompt engine (quality: {insights['overall_score']:.3f})")
            
            return {
                'status': 'success',
                'insights_shared': insights,
                'component': 'validator->prompt_engine',
                'cycle_complete': True
            }
            
        except Exception as e:
            logger.error(f"Failed to share validator insights: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def process_complete_learning_cycle(self,
                                             input_data: Dict[str, Any],
                                             prompt_result: Dict[str, Any],
                                             analysis_result: Dict[str, Any],
                                             validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete learning cycle across all components
        This is the main method that orchestrates cross-component learning
        """
        
        try:
            cycle_id = f"cycle_{int(time.time())}"
            
            logger.info(f"🔄 Starting complete learning cycle {cycle_id}")
            
            # Phase 1: Share prompt insights to agent
            prompt_share = await self.share_prompt_insights_to_agent(
                prompt_metadata=prompt_result,
                quality_score=validation_result.get('overall_score', 0.5)
            )
            
            # Phase 2: Share agent insights to validator
            agent_share = await self.share_agent_insights_to_validator(
                analysis_result=analysis_result,
                reasoning_chain=analysis_result.get('reasoning_chain', {}),
                confidence_score=analysis_result.get('confidence_score', {})
            )
            
            # Phase 3: Share validator insights back to prompt engine
            validator_share = await self.share_validator_insights_to_prompt(
                validation_result=validation_result,
                input_data=input_data,
                response_data={
                    'prompt_metadata': prompt_result,
                    'analysis': analysis_result
                }
            )
            
            # Phase 4: Create cross-component knowledge links
            await self._create_cross_component_links(
                prompt_result, analysis_result, validation_result
            )
            
            # Phase 5: Extract cross-component insights
            cross_insights = await self._extract_cross_component_insights(
                prompt_result, analysis_result, validation_result
            )
            
            logger.info(f"✅ Complete learning cycle {cycle_id} finished")
            
            return {
                'cycle_id': cycle_id,
                'status': 'success',
                'phases_completed': 5,
                'prompt_share': prompt_share,
                'agent_share': agent_share,
                'validator_share': validator_share,
                'cross_insights': cross_insights,
                'total_insights_shared': sum(self.insights_shared.values()),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Complete learning cycle failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _create_cross_component_links(self,
                                           prompt_result: Dict[str, Any],
                                           analysis_result: Dict[str, Any],
                                           validation_result: Dict[str, Any]):
        """Create links between components in knowledge graph"""
        
        try:
            # Generate IDs for each component
            prompt_id = f"prompt_{hash(str(prompt_result))}"
            analysis_id = f"analysis_{hash(str(analysis_result))}"
            validation_id = f"validation_{hash(str(validation_result))}"
            
            quality_score = validation_result.get('overall_score', 0.5)
            
            # Create link in knowledge graph
            await self.knowledge_graph.link_cross_component_knowledge(
                prompt_id=prompt_id,
                analysis_id=analysis_id,
                validation_id=validation_id,
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.warning(f"Failed to create cross-component links: {e}")
    
    async def _extract_cross_component_insights(self,
                                               prompt_result: Dict[str, Any],
                                               analysis_result: Dict[str, Any],
                                               validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights that span multiple components"""
        
        insights = {
            'prompt_quality_correlation': self._analyze_prompt_quality_correlation(
                prompt_result, validation_result
            ),
            'reasoning_effectiveness': self._analyze_reasoning_effectiveness(
                analysis_result, validation_result
            ),
            'end_to_end_patterns': self._identify_end_to_end_patterns(
                prompt_result, analysis_result, validation_result
            )
        }
        
        return insights
    
    def _extract_prompt_patterns(self, metadata: Dict[str, Any]) -> List[str]:
        """Extract patterns from prompt metadata"""
        
        patterns = []
        
        if 'template_used' in metadata:
            patterns.append(f"template:{metadata['template_used']}")
        
        if 'context' in metadata:
            patterns.append(f"context:{metadata['context']}")
        
        if 'generation_mode' in metadata:
            patterns.append(f"mode:{metadata['generation_mode']}")
        
        return patterns
    
    def _identify_successful_templates(self, metadata: Dict[str, Any]) -> List[str]:
        """Identify which templates were successful"""
        
        templates = []
        
        if metadata.get('template_used'):
            templates.append(metadata['template_used'])
        
        return templates
    
    def _analyze_context_preferences(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze context preferences from metadata"""
        
        return {
            'context': metadata.get('context', 'unknown'),
            'data_type': metadata.get('data_type', 'unknown'),
            'complexity': metadata.get('analysis', {}).get('data_complexity', 'simple')
        }
    
    def _assess_reasoning_quality(self, reasoning_chain: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of reasoning"""
        
        return {
            'steps_count': len(reasoning_chain.get('steps', [])),
            'overall_confidence': reasoning_chain.get('overall_confidence', 0.5),
            'validation_passed': reasoning_chain.get('validation_result', {}).get('passed', False)
        }
    
    def _extract_analysis_patterns(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Extract patterns from analysis"""
        
        patterns = []
        
        if 'reasoning_chain' in analysis_result:
            patterns.append('multi_step_reasoning')
        
        if 'confidence_score' in analysis_result:
            patterns.append('confidence_aware')
        
        return patterns
    
    def _assess_complexity(self, analysis_result: Dict[str, Any]) -> str:
        """Assess the complexity of analysis"""
        
        reasoning_chain = analysis_result.get('reasoning_chain', {})
        steps = len(reasoning_chain.get('steps', []))
        
        if steps > 5:
            return 'complex'
        elif steps > 2:
            return 'moderate'
        else:
            return 'simple'
    
    def _extract_quality_patterns(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract quality patterns from validation"""
        
        criteria_scores = validation_result.get('criteria_scores', {})
        
        strong_criteria = [c for c, s in criteria_scores.items() if s > 0.8]
        weak_criteria = [c for c, s in criteria_scores.items() if s < 0.6]
        
        return {
            'strong_criteria': strong_criteria,
            'weak_criteria': weak_criteria,
            'overall_quality': validation_result.get('quality_level', 'unknown')
        }
    
    def _identify_successful_criteria(self, validation_result: Dict[str, Any]) -> List[str]:
        """Identify which criteria were successful"""
        
        criteria_scores = validation_result.get('criteria_scores', {})
        return [c for c, s in criteria_scores.items() if s > 0.75]
    
    def _analyze_prompt_quality_correlation(self,
                                           prompt_result: Dict[str, Any],
                                           validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlation between prompt characteristics and quality"""
        
        return {
            'prompt_mode': prompt_result.get('metadata', {}).get('generation_mode', 'unknown'),
            'final_quality': validation_result.get('overall_score', 0.0),
            'correlation': 'positive' if validation_result.get('overall_score', 0) > 0.7 else 'needs_improvement'
        }
    
    def _analyze_reasoning_effectiveness(self,
                                        analysis_result: Dict[str, Any],
                                        validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how effective the reasoning was"""
        
        reasoning_chain = analysis_result.get('reasoning_chain', {})
        
        return {
            'reasoning_confidence': reasoning_chain.get('overall_confidence', 0.5),
            'validation_score': validation_result.get('overall_score', 0.0),
            'effectiveness': 'high' if validation_result.get('overall_score', 0) > 0.75 else 'moderate'
        }
    
    def _identify_end_to_end_patterns(self,
                                      prompt_result: Dict[str, Any],
                                      analysis_result: Dict[str, Any],
                                      validation_result: Dict[str, Any]) -> List[str]:
        """Identify patterns that span the entire pipeline"""
        
        patterns = []
        
        # Check if vector-enhanced prompts lead to better quality
        if prompt_result.get('vector_accelerated') and validation_result.get('overall_score', 0) > 0.8:
            patterns.append('vector_enhanced_success')
        
        # Check if multi-step reasoning leads to better quality
        reasoning_steps = len(analysis_result.get('reasoning_chain', {}).get('steps', []))
        if reasoning_steps > 3 and validation_result.get('overall_score', 0) > 0.75:
            patterns.append('multi_step_reasoning_success')
        
        # Check for consistent high quality
        if validation_result.get('overall_score', 0) > 0.85:
            patterns.append('high_quality_pipeline')
        
        return patterns
    
    def get_bridge_statistics(self) -> Dict[str, Any]:
        """Get cross-component bridge statistics"""
        
        return {
            'insights_shared': self.insights_shared.copy(),
            'total_insights': sum(self.insights_shared.values()),
            'complete_cycles': self.insights_shared['full_cycle'],
            'registered_components': [
                name for name, ref in self.component_endpoints.items() if ref is not None
            ],
            'knowledge_graph_stats': self.knowledge_graph.get_knowledge_stats(),
            'timestamp': datetime.now().isoformat()
        }

