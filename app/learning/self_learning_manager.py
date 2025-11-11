"""
Advanced Self-Learning Manager - Multi-dimensional learning across all LLM components
"""

import time
import json
import hashlib
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

class LearningPattern:
    """Represents a learned pattern with multi-dimensional context"""
    
    def __init__(self, pattern_id: str, pattern_type: str):
        self.pattern_id = pattern_id
        self.pattern_type = pattern_type  # 'prompt', 'analysis', 'validation', 'reasoning'
        self.creation_time = time.time()
        self.last_used = time.time()
        self.use_count = 0
        self.success_count = 0
        self.quality_scores = []
        self.context_tags = []
        self.linked_patterns = []  # Links to related patterns
        self.temporal_weight = 1.0
        self.reinforcement_score = 0.5
        
    def update_success(self, quality_score: float):
        """Update pattern with successful outcome"""
        self.last_used = time.time()
        self.use_count += 1
        if quality_score >= 0.7:
            self.success_count += 1
        self.quality_scores.append(quality_score)
        
        # Update reinforcement score
        self._update_reinforcement()
        
    def update_failure(self):
        """Update pattern with failed outcome"""
        self.last_used = time.time()
        self.use_count += 1
        self.quality_scores.append(0.0)
        
        # Update reinforcement score
        self._update_reinforcement()
    
    def _update_reinforcement(self):
        """Calculate reinforcement learning score"""
        if self.use_count == 0:
            self.reinforcement_score = 0.5
            return
        
        # Success rate component
        success_rate = self.success_count / self.use_count
        
        # Average quality component
        avg_quality = np.mean(self.quality_scores[-10:]) if self.quality_scores else 0.5
        
        # Recency component (more recent uses get higher weight)
        recency_factor = self._calculate_recency_factor()
        
        # Confidence component (more uses = higher confidence)
        confidence_factor = min(1.0, self.use_count / 10.0)
        
        # Combined reinforcement score
        self.reinforcement_score = (
            success_rate * 0.4 + 
            avg_quality * 0.3 + 
            recency_factor * 0.2 + 
            confidence_factor * 0.1
        )
        
    def _calculate_recency_factor(self) -> float:
        """Calculate temporal decay factor"""
        hours_since_last_use = (time.time() - self.last_used) / 3600
        # Exponential decay: half-life of 7 days (168 hours)
        decay_rate = 0.693 / 168
        return np.exp(-decay_rate * hours_since_last_use)
    
    def apply_temporal_decay(self):
        """Apply temporal decay to reduce weight of old patterns"""
        self.temporal_weight = self._calculate_recency_factor()
        
    def get_overall_score(self) -> float:
        """Get overall pattern score combining all factors"""
        return self.reinforcement_score * self.temporal_weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "creation_time": self.creation_time,
            "last_used": self.last_used,
            "use_count": self.use_count,
            "success_count": self.success_count,
            "success_rate": self.success_count / max(self.use_count, 1),
            "avg_quality": np.mean(self.quality_scores) if self.quality_scores else 0.0,
            "context_tags": self.context_tags,
            "linked_patterns": self.linked_patterns,
            "temporal_weight": self.temporal_weight,
            "reinforcement_score": self.reinforcement_score,
            "overall_score": self.get_overall_score()
        }


class SelfLearningManager:
    """
    Advanced self-learning manager that orchestrates multi-dimensional learning
    across all LLM components (prompt generation, analysis, validation)
    """
    
    def __init__(self, vector_service=None):
        self.vector_service = vector_service
        
        # Pattern storage
        self.patterns = {}  # pattern_id -> LearningPattern
        self.pattern_graph = defaultdict(list)  # Links between patterns
        
        # Learning statistics
        self.total_interactions = 0
        self.successful_interactions = 0
        self.learning_sessions = 0
        
        # Quality improvement engine (NEW - for actual quality improvement)
        self.quality_engine = None  # Initialized later to avoid circular imports
        
        # Adaptive thresholds
        self.adaptive_thresholds = {
            'quality_gate': 0.7,
            'similarity_match': 0.8,
            'reinforcement_cutoff': 0.6
        }
        
        # Performance tracking
        self.performance_history = []
        self.quality_trend = []
        
        # Knowledge domains
        self.domain_expertise = defaultdict(lambda: {'count': 0, 'avg_quality': 0.5})
        
        # Initialize quality improvement engine
        try:
            from app.learning.quality_improvement_engine import QualityImprovementEngine
            self.quality_engine = QualityImprovementEngine(self)
        except Exception as e:
            print(f"⚠️ Quality engine initialization failed: {e}")
            self.quality_engine = None
        
        print("🧠 Advanced Self-Learning Manager initialized")
        
    async def learn_from_complete_interaction(self,
                                             input_data: Dict[str, Any],
                                             prompt_result: Dict[str, Any],
                                             analysis_result: Dict[str, Any],
                                             validation_result: Dict[str, Any],
                                             metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learn from a complete interaction cycle: input -> prompt -> analysis -> validation
        This creates a knowledge graph linking all components
        """
        self.total_interactions += 1
        self.learning_sessions += 1
        
        learning_id = f"learn_{int(time.time())}_{self.learning_sessions}"
        
        try:
            # Extract quality metrics
            quality_score = validation_result.get('overall_score', 0.5)
            is_successful = quality_score >= self.adaptive_thresholds['quality_gate']
            
            if is_successful:
                self.successful_interactions += 1
            
            # Create learning patterns for each component
            prompt_pattern = await self._create_prompt_pattern(
                input_data, prompt_result, quality_score
            )
            
            analysis_pattern = await self._create_analysis_pattern(
                input_data, analysis_result, quality_score
            )
            
            validation_pattern = await self._create_validation_pattern(
                validation_result, quality_score
            )
            
            # Link patterns in knowledge graph
            self._link_patterns([prompt_pattern, analysis_pattern, validation_pattern])
            
            # Store in vector database for fast retrieval
            if self.vector_service:
                await self._store_in_vector_db(
                    prompt_pattern, analysis_pattern, validation_pattern,
                    input_data, quality_score
                )
            
            # Update domain expertise
            self._update_domain_expertise(input_data, metadata, quality_score)
            
            # Track performance trends
            self._track_performance(quality_score, metadata)
            
            # **NEW: Quality improvement analysis**
            quality_improvements = {}
            if self.quality_engine and validation_result:
                quality_improvements = await self.quality_engine.analyze_and_improve(
                    input_data=input_data,
                    prompt_used=prompt_result.get('prompt', ''),
                    validation_result=validation_result,
                    metadata=metadata
                )
            
            # Adaptive threshold adjustment
            await self._adjust_adaptive_thresholds()
            
            # Apply temporal decay to old patterns
            self._apply_temporal_decay()
            
            learning_result = {
                "learning_id": learning_id,
                "status": "success",
                "quality_score": quality_score,
                "is_successful": is_successful,
                "patterns_created": 3,
                "patterns_linked": len(prompt_pattern.linked_patterns),
                "vector_storage": "enabled" if self.vector_service else "disabled",
                "adaptive_thresholds": self.adaptive_thresholds.copy(),
                "quality_improvements": quality_improvements,  # NEW: Improvement analysis
                "learning_metrics": self.get_learning_metrics(),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Learning session {learning_id} completed (quality: {quality_score:.3f})")
            
            return learning_result
            
        except Exception as e:
            print(f"❌ Learning session {learning_id} failed: {e}")
            return {
                "learning_id": learning_id,
                "status": "error",
                "error": str(e)
            }
    
    async def _create_prompt_pattern(self, input_data: Dict[str, Any],
                                   prompt_result: Dict[str, Any],
                                   quality_score: float) -> LearningPattern:
        """Create a learning pattern from prompt generation"""
        
        # Create unique pattern ID
        pattern_hash = hashlib.md5(
            json.dumps({
                'input': input_data,
                'prompt': prompt_result.get('prompt', '')[:500]  # First 500 chars
            }, sort_keys=True).encode()
        ).hexdigest()
        
        pattern_id = f"prompt_{pattern_hash[:12]}"
        
        # Get or create pattern
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.update_success(quality_score)
        else:
            pattern = LearningPattern(pattern_id, 'prompt')
            pattern.update_success(quality_score)
            
            # Extract context tags
            pattern.context_tags = self._extract_context_tags(input_data, prompt_result)
            
            self.patterns[pattern_id] = pattern
        
        return pattern
    
    async def _create_analysis_pattern(self, input_data: Dict[str, Any],
                                      analysis_result: Dict[str, Any],
                                      quality_score: float) -> LearningPattern:
        """Create a learning pattern from analysis results"""
        
        # Create unique pattern ID
        pattern_hash = hashlib.md5(
            json.dumps({
                'input': input_data,
                'analysis': str(analysis_result)[:500]
            }, sort_keys=True).encode()
        ).hexdigest()
        
        pattern_id = f"analysis_{pattern_hash[:12]}"
        
        # Get or create pattern
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.update_success(quality_score)
        else:
            pattern = LearningPattern(pattern_id, 'analysis')
            pattern.update_success(quality_score)
            
            # Extract context tags
            pattern.context_tags = self._extract_analysis_tags(analysis_result)
            
            self.patterns[pattern_id] = pattern
        
        return pattern
    
    async def _create_validation_pattern(self, validation_result: Dict[str, Any],
                                       quality_score: float) -> LearningPattern:
        """Create a learning pattern from validation results"""
        
        # Create unique pattern ID based on validation characteristics
        pattern_hash = hashlib.md5(
            json.dumps({
                'quality_level': validation_result.get('quality_level', ''),
                'criteria_scores': validation_result.get('criteria_scores', {})
            }, sort_keys=True).encode()
        ).hexdigest()
        
        pattern_id = f"validation_{pattern_hash[:12]}"
        
        # Get or create pattern
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.update_success(quality_score)
        else:
            pattern = LearningPattern(pattern_id, 'validation')
            pattern.update_success(quality_score)
            
            # Extract context tags
            pattern.context_tags = self._extract_validation_tags(validation_result)
            
            self.patterns[pattern_id] = pattern
        
        return pattern
    
    def _link_patterns(self, patterns: List[LearningPattern]):
        """Link patterns together in the knowledge graph"""
        
        # Create bidirectional links between all patterns
        for i, pattern1 in enumerate(patterns):
            for pattern2 in patterns[i+1:]:
                # Link pattern1 -> pattern2
                if pattern2.pattern_id not in pattern1.linked_patterns:
                    pattern1.linked_patterns.append(pattern2.pattern_id)
                
                # Link pattern2 -> pattern1
                if pattern1.pattern_id not in pattern2.linked_patterns:
                    pattern2.linked_patterns.append(pattern1.pattern_id)
                
                # Update knowledge graph
                self.pattern_graph[pattern1.pattern_id].append(pattern2.pattern_id)
                self.pattern_graph[pattern2.pattern_id].append(pattern1.pattern_id)
    
    async def _store_in_vector_db(self, prompt_pattern: LearningPattern,
                                  analysis_pattern: LearningPattern,
                                  validation_pattern: LearningPattern,
                                  input_data: Dict[str, Any],
                                  quality_score: float):
        """Store patterns in vector database for fast similarity matching"""
        
        if not self.vector_service:
            return
        
        try:
            # Store in dedicated learning collection
            collection_name = 'self_learning_patterns'
            
            # Create comprehensive learning record
            learning_record = {
                'input_data': input_data,
                'prompt_pattern': prompt_pattern.to_dict(),
                'analysis_pattern': analysis_pattern.to_dict(),
                'validation_pattern': validation_pattern.to_dict(),
                'quality_score': quality_score,
                'timestamp': time.time(),
                'context_tags': list(set(
                    prompt_pattern.context_tags + 
                    analysis_pattern.context_tags + 
                    validation_pattern.context_tags
                ))
            }
            
            # Store with quality-weighted importance
            await self._vector_store_learning_record(learning_record, collection_name)
            
        except Exception as e:
            print(f"⚠️ Error storing in vector DB: {e}")
    
    async def _vector_store_learning_record(self, record: Dict[str, Any], collection: str):
        """Store learning record in vector database"""
        # This would use the vector service to store the record
        # Implementation depends on vector service API
        pass
    
    def _extract_context_tags(self, input_data: Dict[str, Any], 
                             prompt_result: Dict[str, Any]) -> List[str]:
        """Extract context tags from input data and prompt"""
        tags = []
        
        # Extract from input data
        if 'transactions' in input_data:
            tags.append('transactions')
        if 'account_balance' in input_data:
            tags.append('balance')
        if 'customer_id' in input_data:
            tags.append('customer')
        
        # Extract from prompt metadata
        metadata = prompt_result.get('agentic_metadata', {}) or prompt_result.get('metadata', {})
        if metadata:
            if 'context' in metadata:
                tags.append(f"context_{metadata['context']}")
            if 'data_type' in metadata:
                tags.append(f"type_{metadata['data_type']}")
        
        return tags
    
    def _extract_analysis_tags(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Extract tags from analysis results"""
        tags = []
        
        # Extract from metadata
        if 'reasoning_chain' in analysis_result:
            tags.append('reasoning')
        if 'confidence_score' in analysis_result:
            confidence = analysis_result['confidence_score']
            if isinstance(confidence, dict):
                confidence = confidence.get('overall_score', 0.5)
            if confidence >= 0.8:
                tags.append('high_confidence')
            elif confidence >= 0.6:
                tags.append('medium_confidence')
            else:
                tags.append('low_confidence')
        
        return tags
    
    def _extract_validation_tags(self, validation_result: Dict[str, Any]) -> List[str]:
        """Extract tags from validation results"""
        tags = []
        
        quality_level = validation_result.get('quality_level', '')
        if quality_level:
            tags.append(f"quality_{quality_level}")
        
        # Extract from criteria scores
        criteria_scores = validation_result.get('criteria_scores', {})
        for criterion, score in criteria_scores.items():
            if score >= 0.8:
                tags.append(f"strong_{criterion}")
            elif score < 0.5:
                tags.append(f"weak_{criterion}")
        
        return tags
    
    def _update_domain_expertise(self, input_data: Dict[str, Any],
                                metadata: Dict[str, Any],
                                quality_score: float):
        """Track expertise development in different domains"""
        
        # Identify domain
        domain = 'general'
        if 'context' in metadata:
            domain = metadata['context']
        elif 'transactions' in input_data:
            domain = 'banking'
        
        # Update domain statistics
        domain_stats = self.domain_expertise[domain]
        domain_stats['count'] += 1
        
        # Update rolling average quality
        old_avg = domain_stats['avg_quality']
        n = domain_stats['count']
        domain_stats['avg_quality'] = ((old_avg * (n - 1)) + quality_score) / n
    
    def _track_performance(self, quality_score: float, metadata: Dict[str, Any]):
        """Track performance trends over time"""
        
        performance_record = {
            'timestamp': time.time(),
            'quality_score': quality_score,
            'metadata': metadata
        }
        
        self.performance_history.append(performance_record)
        self.quality_trend.append(quality_score)
        
        # Keep only recent history (last 1000 interactions)
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-800:]
        if len(self.quality_trend) > 1000:
            self.quality_trend = self.quality_trend[-800:]
    
    async def _adjust_adaptive_thresholds(self):
        """Dynamically adjust thresholds based on performance"""
        
        if len(self.quality_trend) < 20:
            return  # Need more data
        
        # Calculate recent performance
        recent_quality = np.mean(self.quality_trend[-20:])
        overall_quality = np.mean(self.quality_trend)
        
        # Adjust quality gate threshold
        if recent_quality > 0.85 and overall_quality > 0.80:
            # System is performing well, raise the bar
            self.adaptive_thresholds['quality_gate'] = min(0.85, 
                self.adaptive_thresholds['quality_gate'] + 0.01)
        elif recent_quality < 0.65 and overall_quality < 0.70:
            # System struggling, lower the bar temporarily
            self.adaptive_thresholds['quality_gate'] = max(0.60,
                self.adaptive_thresholds['quality_gate'] - 0.01)
        
        # Adjust similarity matching threshold based on pattern success
        if self.patterns:
            avg_pattern_score = np.mean([p.get_overall_score() for p in self.patterns.values()])
            if avg_pattern_score > 0.8:
                self.adaptive_thresholds['similarity_match'] = min(0.9,
                    self.adaptive_thresholds['similarity_match'] + 0.01)
    
    def _apply_temporal_decay(self):
        """Apply temporal decay to all patterns to keep knowledge fresh"""
        
        for pattern in self.patterns.values():
            pattern.apply_temporal_decay()
        
        # Remove patterns that have decayed too much
        patterns_to_remove = [
            pid for pid, pattern in self.patterns.items()
            if pattern.temporal_weight < 0.1 and pattern.use_count < 3
        ]
        
        for pattern_id in patterns_to_remove:
            del self.patterns[pattern_id]
            if pattern_id in self.pattern_graph:
                del self.pattern_graph[pattern_id]
    
    async def get_quality_improved_prompt(self,
                                         input_data: Dict[str, Any],
                                         context: Optional[str] = None) -> Optional[str]:
        """
        NEW METHOD: Get quality-improved prompt based on past validation feedback
        This is the key to improving quality over time!
        """
        if not self.quality_engine:
            return None
        
        improved = await self.quality_engine.get_improved_prompt_for_input(
            input_data=input_data,
            context=context
        )
        
        if improved and improved.get('confidence', 0) > 0.75:
            print(f"🎯 Using quality-improved prompt (based on {improved['based_on_quality']:.2f} quality score)")
            return improved['improved_prompt']
        
        return None
    
    async def find_similar_successful_patterns(self, 
                                              input_data: Dict[str, Any],
                                              pattern_type: Optional[str] = None,
                                              limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar successful patterns for a given input
        This provides predictive guidance before execution
        """
        
        similar_patterns = []
        
        # Filter by pattern type if specified
        candidate_patterns = [
            p for p in self.patterns.values()
            if pattern_type is None or p.pattern_type == pattern_type
        ]
        
        # Filter by success criteria
        successful_patterns = [
            p for p in candidate_patterns
            if p.get_overall_score() >= self.adaptive_thresholds['reinforcement_cutoff']
        ]
        
        # Sort by overall score
        successful_patterns.sort(key=lambda p: p.get_overall_score(), reverse=True)
        
        # Return top patterns
        for pattern in successful_patterns[:limit]:
            similar_patterns.append({
                'pattern': pattern.to_dict(),
                'similarity_score': pattern.get_overall_score(),
                'linked_patterns': self._get_linked_pattern_info(pattern),
                'recommendation': self._generate_pattern_recommendation(pattern)
            })
        
        return similar_patterns
    
    def _get_linked_pattern_info(self, pattern: LearningPattern) -> List[Dict[str, Any]]:
        """Get information about linked patterns"""
        
        linked_info = []
        for linked_id in pattern.linked_patterns[:5]:  # Top 5 linked patterns
            if linked_id in self.patterns:
                linked_pattern = self.patterns[linked_id]
                linked_info.append({
                    'pattern_id': linked_id,
                    'pattern_type': linked_pattern.pattern_type,
                    'score': linked_pattern.get_overall_score()
                })
        
        return linked_info
    
    def _generate_pattern_recommendation(self, pattern: LearningPattern) -> str:
        """Generate recommendation based on pattern"""
        
        if pattern.pattern_type == 'prompt':
            return f"Use similar prompt structure (success rate: {pattern.success_count}/{pattern.use_count})"
        elif pattern.pattern_type == 'analysis':
            return f"Apply similar analysis approach (avg quality: {np.mean(pattern.quality_scores[-5:]) if pattern.quality_scores else 0:.2f})"
        elif pattern.pattern_type == 'validation':
            return f"Expected validation profile (typical score: {np.mean(pattern.quality_scores) if pattern.quality_scores else 0:.2f})"
        else:
            return "Use this successful pattern as reference"
    
    async def predict_interaction_quality(self,
                                         input_data: Dict[str, Any],
                                         context: Optional[str] = None) -> Dict[str, Any]:
        """
        Predict the likely quality of an interaction before execution
        Based on historical patterns
        """
        
        # Find similar past interactions
        similar_patterns = await self.find_similar_successful_patterns(
            input_data, limit=10
        )
        
        if not similar_patterns:
            return {
                'predicted_quality': 0.5,
                'confidence': 'low',
                'explanation': 'No similar patterns found',
                'recommendations': []
            }
        
        # Calculate predicted quality
        quality_scores = [p['similarity_score'] for p in similar_patterns]
        predicted_quality = np.mean(quality_scores)
        quality_std = np.std(quality_scores)
        
        # Determine confidence
        if quality_std < 0.1 and len(similar_patterns) >= 5:
            confidence = 'high'
        elif quality_std < 0.2 and len(similar_patterns) >= 3:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        # Generate recommendations
        recommendations = []
        for pattern_info in similar_patterns[:3]:
            recommendations.append(pattern_info['recommendation'])
        
        return {
            'predicted_quality': predicted_quality,
            'confidence': confidence,
            'confidence_score': 1.0 - min(quality_std, 1.0),
            'similar_patterns_found': len(similar_patterns),
            'explanation': f'Based on {len(similar_patterns)} similar successful patterns',
            'recommendations': recommendations,
            'quality_range': {
                'min': min(quality_scores),
                'max': max(quality_scores),
                'mean': predicted_quality,
                'std': quality_std
            }
        }
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get comprehensive learning metrics"""
        
        return {
            'total_interactions': self.total_interactions,
            'successful_interactions': self.successful_interactions,
            'success_rate': self.successful_interactions / max(self.total_interactions, 1),
            'learning_sessions': self.learning_sessions,
            'patterns_stored': len(self.patterns),
            'pattern_types': {
                'prompt': len([p for p in self.patterns.values() if p.pattern_type == 'prompt']),
                'analysis': len([p for p in self.patterns.values() if p.pattern_type == 'analysis']),
                'validation': len([p for p in self.patterns.values() if p.pattern_type == 'validation'])
            },
            'knowledge_graph_edges': sum(len(links) for links in self.pattern_graph.values()),
            'domain_expertise': dict(self.domain_expertise),
            'adaptive_thresholds': self.adaptive_thresholds.copy(),
            'performance_trend': {
                'recent_quality': np.mean(self.quality_trend[-10:]) if self.quality_trend else 0.0,
                'overall_quality': np.mean(self.quality_trend) if self.quality_trend else 0.0,
                'quality_improvement': self._calculate_quality_improvement()
            },
            'top_patterns': self._get_top_patterns(5)
        }
    
    def _calculate_quality_improvement(self) -> float:
        """Calculate quality improvement over time"""
        
        if len(self.quality_trend) < 20:
            return 0.0
        
        # Compare first 20% vs last 20%
        early_window = int(len(self.quality_trend) * 0.2)
        early_quality = np.mean(self.quality_trend[:early_window])
        recent_quality = np.mean(self.quality_trend[-early_window:])
        
        return recent_quality - early_quality
    
    def _get_top_patterns(self, limit: int) -> List[Dict[str, Any]]:
        """Get top performing patterns"""
        
        if not self.patterns:
            return []
        
        # Sort patterns by overall score
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.get_overall_score(),
            reverse=True
        )
        
        return [p.to_dict() for p in sorted_patterns[:limit]]
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Generate insights about learning progress"""
        
        metrics = self.get_learning_metrics()
        
        insights = []
        
        # Performance trend insight
        improvement = metrics['performance_trend']['quality_improvement']
        if improvement > 0.1:
            insights.append({
                'type': 'performance',
                'level': 'positive',
                'message': f'Quality improved by {improvement:.1%} - system is learning effectively'
            })
        elif improvement < -0.1:
            insights.append({
                'type': 'performance',
                'level': 'warning',
                'message': f'Quality decreased by {abs(improvement):.1%} - review recent patterns'
            })
        
        # Pattern accumulation insight
        if metrics['patterns_stored'] > 100:
            insights.append({
                'type': 'knowledge',
                'level': 'positive',
                'message': f'{metrics["patterns_stored"]} patterns learned - strong knowledge base'
            })
        
        # Domain expertise insight
        for domain, stats in metrics['domain_expertise'].items():
            if stats['count'] > 20 and stats['avg_quality'] > 0.8:
                insights.append({
                    'type': 'expertise',
                    'level': 'positive',
                    'message': f'Expert level achieved in {domain} domain (quality: {stats["avg_quality"]:.2f})'
                })
        
        return {
            'insights': insights,
            'metrics_summary': metrics,
            'timestamp': datetime.now().isoformat()
        }

