"""
Learning Analytics - Performance tracking and insights visualization
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np


class LearningAnalytics:
    """
    Comprehensive learning analytics and performance tracking
    Provides insights into learning progress and system improvements
    """
    
    def __init__(self, learning_manager, knowledge_graph_service):
        self.learning_manager = learning_manager
        self.knowledge_graph = knowledge_graph_service
        
        # Analytics data
        self.performance_snapshots = []
        self.quality_timeline = []
        self.learning_milestones = []
        
        # Trend analysis
        self.trend_window = 50  # Number of interactions to analyze
        
        print("📊 Learning Analytics initialized")
    
    def capture_performance_snapshot(self) -> Dict[str, Any]:
        """Capture a snapshot of current performance"""
        
        snapshot = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'learning_metrics': self.learning_manager.get_learning_metrics(),
            'knowledge_graph_stats': self.knowledge_graph.get_knowledge_stats(),
            'quality_trend': self._calculate_quality_trend(),
            'learning_velocity': self._calculate_learning_velocity(),
            'pattern_effectiveness': self._calculate_pattern_effectiveness()
        }
        
        self.performance_snapshots.append(snapshot)
        
        # Keep only recent snapshots (last 100)
        if len(self.performance_snapshots) > 100:
            self.performance_snapshots = self.performance_snapshots[-80:]
        
        return snapshot
    
    def record_quality_measurement(self, quality_score: float, metadata: Dict[str, Any]):
        """Record a quality measurement"""
        
        measurement = {
            'timestamp': time.time(),
            'quality_score': quality_score,
            'metadata': metadata
        }
        
        self.quality_timeline.append(measurement)
        
        # Check for milestones
        self._check_for_milestones(quality_score)
    
    def _check_for_milestones(self, quality_score: float):
        """Check if any learning milestones have been reached"""
        
        metrics = self.learning_manager.get_learning_metrics()
        
        # Milestone: 100 interactions
        if metrics['total_interactions'] == 100:
            self._record_milestone('100_interactions', 'Reached 100 interactions')
        
        # Milestone: 80% success rate
        if metrics['success_rate'] >= 0.8 and len(self.learning_milestones) == 0:
            self._record_milestone('high_success_rate', 'Achieved 80% success rate')
        
        # Milestone: 1000 patterns
        if metrics['patterns_stored'] >= 1000:
            self._record_milestone('1000_patterns', 'Stored 1000 learning patterns')
        
        # Milestone: Consistent high quality
        if len(self.quality_timeline) >= 10:
            recent_quality = [m['quality_score'] for m in self.quality_timeline[-10:]]
            if all(q > 0.8 for q in recent_quality):
                self._record_milestone('consistent_quality', 'Achieved consistent high quality (10 interactions)')
    
    def _record_milestone(self, milestone_id: str, description: str):
        """Record a learning milestone"""
        
        # Check if already recorded
        if any(m['milestone_id'] == milestone_id for m in self.learning_milestones):
            return
        
        milestone = {
            'milestone_id': milestone_id,
            'description': description,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'metrics_at_milestone': self.learning_manager.get_learning_metrics()
        }
        
        self.learning_milestones.append(milestone)
        print(f"🏆 Learning Milestone: {description}")
    
    def _calculate_quality_trend(self) -> Dict[str, Any]:
        """Calculate quality trend over recent interactions"""
        
        if len(self.quality_timeline) < 10:
            return {'trend': 'insufficient_data', 'direction': 'unknown'}
        
        # Get recent quality scores
        recent_scores = [m['quality_score'] for m in self.quality_timeline[-self.trend_window:]]
        
        # Calculate linear regression trend
        x = np.arange(len(recent_scores))
        y = np.array(recent_scores)
        
        # Simple linear regression
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        
        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Determine trend direction
        if slope > 0.01:
            direction = 'improving'
        elif slope < -0.01:
            direction = 'declining'
        else:
            direction = 'stable'
        
        return {
            'trend': direction,
            'slope': float(slope),
            'current_quality': float(y[-1]) if len(y) > 0 else 0.0,
            'average_quality': float(np.mean(y)),
            'quality_std': float(np.std(y)),
            'sample_size': len(recent_scores)
        }
    
    def _calculate_learning_velocity(self) -> Dict[str, Any]:
        """Calculate how fast the system is learning"""
        
        if len(self.performance_snapshots) < 2:
            return {'velocity': 0.0, 'status': 'insufficient_data'}
        
        # Compare recent snapshots
        recent_snapshot = self.performance_snapshots[-1]
        older_snapshot = self.performance_snapshots[-min(len(self.performance_snapshots), 10)]
        
        time_diff = recent_snapshot['timestamp'] - older_snapshot['timestamp']
        
        recent_metrics = recent_snapshot['learning_metrics']
        older_metrics = older_snapshot['learning_metrics']
        
        # Calculate patterns per hour
        patterns_added = (
            recent_metrics['patterns_stored'] - older_metrics['patterns_stored']
        )
        hours_elapsed = time_diff / 3600
        
        velocity = patterns_added / hours_elapsed if hours_elapsed > 0 else 0
        
        return {
            'velocity': float(velocity),
            'patterns_per_hour': float(velocity),
            'time_period_hours': float(hours_elapsed),
            'patterns_added': patterns_added,
            'status': 'active'
        }
    
    def _calculate_pattern_effectiveness(self) -> Dict[str, Any]:
        """Calculate how effective the learned patterns are"""
        
        metrics = self.learning_manager.get_learning_metrics()
        
        total_patterns = metrics['patterns_stored']
        if total_patterns == 0:
            return {'effectiveness': 0.0, 'status': 'no_patterns'}
        
        # Get pattern statistics from learning manager
        top_patterns = metrics.get('top_patterns', [])
        
        if not top_patterns:
            return {'effectiveness': 0.5, 'status': 'no_data'}
        
        # Calculate average effectiveness of top patterns
        avg_score = np.mean([p['overall_score'] for p in top_patterns])
        
        return {
            'effectiveness': float(avg_score),
            'top_patterns_count': len(top_patterns),
            'total_patterns': total_patterns,
            'status': 'measured'
        }
    
    def generate_learning_report(self) -> Dict[str, Any]:
        """Generate a comprehensive learning report"""
        
        # Capture current snapshot
        current_snapshot = self.capture_performance_snapshot()
        
        # Get insights from learning manager
        insights = self.learning_manager.get_learning_insights()
        
        # Calculate advanced metrics
        quality_distribution = self._analyze_quality_distribution()
        learning_patterns = self._analyze_learning_patterns()
        improvement_recommendations = self._generate_improvement_recommendations()
        
        report = {
            'report_id': f"report_{int(time.time())}",
            'generated_at': datetime.now().isoformat(),
            
            # Current state
            'current_snapshot': current_snapshot,
            'learning_insights': insights,
            
            # Performance analysis
            'quality_distribution': quality_distribution,
            'learning_patterns': learning_patterns,
            'trend_analysis': self._calculate_quality_trend(),
            'learning_velocity': self._calculate_learning_velocity(),
            
            # Milestones
            'milestones_achieved': len(self.learning_milestones),
            'recent_milestones': self.learning_milestones[-5:] if self.learning_milestones else [],
            
            # Recommendations
            'improvement_recommendations': improvement_recommendations,
            
            # Statistics
            'total_measurements': len(self.quality_timeline),
            'total_snapshots': len(self.performance_snapshots),
            
            # Summary
            'summary': self._generate_summary()
        }
        
        return report
    
    def _analyze_quality_distribution(self) -> Dict[str, Any]:
        """Analyze the distribution of quality scores"""
        
        if not self.quality_timeline:
            return {'status': 'no_data'}
        
        scores = [m['quality_score'] for m in self.quality_timeline]
        
        # Calculate percentiles
        percentiles = {
            'p25': float(np.percentile(scores, 25)),
            'p50': float(np.percentile(scores, 50)),
            'p75': float(np.percentile(scores, 75)),
            'p90': float(np.percentile(scores, 90))
        }
        
        # Calculate distribution
        distribution = {
            'exemplary': sum(1 for s in scores if s >= 0.95) / len(scores),
            'high_quality': sum(1 for s in scores if 0.80 <= s < 0.95) / len(scores),
            'acceptable': sum(1 for s in scores if 0.65 <= s < 0.80) / len(scores),
            'poor': sum(1 for s in scores if s < 0.65) / len(scores)
        }
        
        return {
            'mean': float(np.mean(scores)),
            'std': float(np.std(scores)),
            'min': float(np.min(scores)),
            'max': float(np.max(scores)),
            'percentiles': percentiles,
            'distribution': distribution
        }
    
    def _analyze_learning_patterns(self) -> Dict[str, Any]:
        """Analyze learning patterns over time"""
        
        if len(self.performance_snapshots) < 3:
            return {'status': 'insufficient_data'}
        
        # Analyze pattern growth
        snapshots = self.performance_snapshots[-20:]  # Last 20 snapshots
        
        pattern_counts = [
            s['learning_metrics']['patterns_stored'] for s in snapshots
        ]
        
        success_rates = [
            s['learning_metrics']['success_rate'] for s in snapshots
        ]
        
        return {
            'pattern_growth_rate': float(
                (pattern_counts[-1] - pattern_counts[0]) / len(pattern_counts)
            ) if len(pattern_counts) > 1 else 0.0,
            'success_rate_trend': 'improving' if success_rates[-1] > success_rates[0] else 'stable',
            'current_success_rate': float(success_rates[-1]) if success_rates else 0.0,
            'pattern_velocity': self._calculate_learning_velocity()['velocity']
        }
    
    def _generate_improvement_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations for improvement"""
        
        recommendations = []
        
        # Analyze current state
        metrics = self.learning_manager.get_learning_metrics()
        quality_trend = self._calculate_quality_trend()
        
        # Recommendation 1: Success rate
        if metrics['success_rate'] < 0.7:
            recommendations.append({
                'priority': 'high',
                'category': 'performance',
                'recommendation': 'Success rate below 70% - review and refine prompt templates',
                'metric': 'success_rate',
                'current_value': metrics['success_rate'],
                'target_value': 0.7
            })
        
        # Recommendation 2: Quality trend
        if quality_trend['trend'] == 'declining':
            recommendations.append({
                'priority': 'high',
                'category': 'quality',
                'recommendation': 'Quality is declining - review recent patterns and adjust adaptive thresholds',
                'metric': 'quality_trend',
                'current_value': quality_trend['slope'],
                'target_value': 0.0
            })
        
        # Recommendation 3: Pattern diversity
        pattern_types = metrics.get('pattern_types', {})
        if pattern_types:
            min_type = min(pattern_types.values())
            if min_type < 10:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'diversity',
                    'recommendation': 'Low pattern diversity in some categories - encourage varied interactions',
                    'metric': 'pattern_diversity',
                    'details': pattern_types
                })
        
        # Recommendation 4: Knowledge graph usage
        kg_stats = self.knowledge_graph.get_knowledge_stats()
        if kg_stats.get('status') == 'active':
            retrieval_rate = kg_stats.get('retrieval_success_rate', 0)
            if retrieval_rate < 0.5:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'knowledge_graph',
                    'recommendation': 'Low knowledge graph retrieval success - review similarity thresholds',
                    'metric': 'retrieval_success_rate',
                    'current_value': retrieval_rate,
                    'target_value': 0.6
                })
        
        return recommendations
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of learning progress"""
        
        metrics = self.learning_manager.get_learning_metrics()
        quality_trend = self._calculate_quality_trend()
        
        # Determine overall status
        if metrics['success_rate'] > 0.8 and quality_trend['trend'] in ['improving', 'stable']:
            overall_status = 'excellent'
            status_message = 'System is learning effectively with high success rate'
        elif metrics['success_rate'] > 0.65:
            overall_status = 'good'
            status_message = 'System is learning well with room for improvement'
        else:
            overall_status = 'needs_attention'
            status_message = 'System needs tuning to improve learning effectiveness'
        
        return {
            'overall_status': overall_status,
            'status_message': status_message,
            'total_interactions': metrics['total_interactions'],
            'success_rate': metrics['success_rate'],
            'patterns_learned': metrics['patterns_stored'],
            'current_quality': quality_trend.get('current_quality', 0.0),
            'quality_trend': quality_trend['trend'],
            'milestones_achieved': len(self.learning_milestones)
        }
    
    def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """Get data formatted for analytics dashboard"""
        
        return {
            'performance_metrics': {
                'current': self.learning_manager.get_learning_metrics(),
                'trend': self._calculate_quality_trend(),
                'velocity': self._calculate_learning_velocity()
            },
            'quality_analytics': {
                'distribution': self._analyze_quality_distribution(),
                'timeline': self.quality_timeline[-50:] if self.quality_timeline else []
            },
            'learning_progress': {
                'milestones': self.learning_milestones,
                'patterns': self._analyze_learning_patterns()
            },
            'knowledge_graph': self.knowledge_graph.get_knowledge_stats(),
            'recommendations': self._generate_improvement_recommendations(),
            'summary': self._generate_summary(),
            'last_updated': datetime.now().isoformat()
        }

