"""
Integration Helper - Simplifies integration of self-learning system into existing components
"""

from typing import Dict, Any, Optional
import asyncio

from app.learning.self_learning_manager import SelfLearningManager
from app.learning.knowledge_graph_service import KnowledgeGraphService
from app.learning.cross_component_bridge import CrossComponentBridge
from app.learning.learning_analytics import LearningAnalytics


class SelfLearningIntegration:
    """
    Helper class to integrate self-learning into existing components
    Provides simple API for existing code to use advanced learning features
    """
    
    _instance = None  # Singleton instance
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        # Initialize core components
        self.knowledge_graph = None
        self.learning_manager = None
        self.cross_component_bridge = None
        self.learning_analytics = None
        
        self._setup_complete = False
    
    def setup(self, qdrant_host: str = "localhost", qdrant_port: int = 6333,
             vector_service = None):
        """
        Setup the self-learning system
        
        Args:
            qdrant_host: Qdrant host
            qdrant_port: Qdrant port
            vector_service: Existing vector service (optional)
        """
        
        if self._setup_complete:
            return
        
        try:
            # Initialize knowledge graph
            self.knowledge_graph = KnowledgeGraphService(
                qdrant_host=qdrant_host,
                qdrant_port=qdrant_port
            )
            
            # Initialize learning manager
            self.learning_manager = SelfLearningManager(
                vector_service=vector_service
            )
            
            # Initialize cross-component bridge
            self.cross_component_bridge = CrossComponentBridge(
                learning_manager=self.learning_manager,
                knowledge_graph_service=self.knowledge_graph
            )
            
            # Initialize learning analytics
            self.learning_analytics = LearningAnalytics(
                learning_manager=self.learning_manager,
                knowledge_graph_service=self.knowledge_graph
            )
            
            self._setup_complete = True
            print("✅ Self-Learning Integration setup complete")
            
        except Exception as e:
            print(f"⚠️ Self-Learning Integration setup failed: {e}")
            print("   System will continue without advanced learning features")
    
    def is_ready(self) -> bool:
        """Check if self-learning system is ready"""
        return self._setup_complete and self.learning_manager is not None
    
    async def learn_from_interaction(self,
                                     input_data: Dict[str, Any],
                                     prompt_result: Dict[str, Any],
                                     analysis_result: Optional[Dict[str, Any]] = None,
                                     validation_result: Optional[Dict[str, Any]] = None,
                                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Learn from a complete interaction
        Simplified API for existing components
        """
        
        if not self.is_ready():
            return {'status': 'disabled', 'message': 'Self-learning not initialized'}
        
        try:
            # If we have all components, do full learning cycle
            if analysis_result and validation_result:
                result = await self.learning_manager.learn_from_complete_interaction(
                    input_data=input_data,
                    prompt_result=prompt_result,
                    analysis_result=analysis_result,
                    validation_result=validation_result,
                    metadata=metadata or {}
                )
                
                # Also run cross-component learning
                await self.cross_component_bridge.process_complete_learning_cycle(
                    input_data=input_data,
                    prompt_result=prompt_result,
                    analysis_result=analysis_result,
                    validation_result=validation_result
                )
                
                # Record in analytics
                if 'quality_score' in validation_result or 'overall_score' in validation_result:
                    quality_score = validation_result.get('overall_score', 
                                                         validation_result.get('quality_score', 0.5))
                    self.learning_analytics.record_quality_measurement(
                        quality_score=quality_score,
                        metadata=metadata or {}
                    )
                
                return result
            
            # Partial learning if we don't have all components
            else:
                # Just store prompt knowledge
                await self.knowledge_graph.store_prompt_knowledge(
                    input_data=input_data,
                    prompt=prompt_result.get('prompt', ''),
                    metadata=prompt_result,
                    quality_score=0.5  # Default when no validation
                )
                
                return {'status': 'partial', 'message': 'Stored prompt knowledge only'}
                
        except Exception as e:
            print(f"⚠️ Learning from interaction failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_similar_successful_patterns(self,
                                             input_data: Dict[str, Any],
                                             pattern_type: Optional[str] = None,
                                             limit: int = 5) -> list:
        """
        Get similar successful patterns for given input
        """
        
        if not self.is_ready():
            return []
        
        try:
            return await self.learning_manager.find_similar_successful_patterns(
                input_data=input_data,
                pattern_type=pattern_type,
                limit=limit
            )
        except Exception as e:
            print(f"⚠️ Finding similar patterns failed: {e}")
            return []
    
    async def predict_interaction_quality(self,
                                         input_data: Dict[str, Any],
                                         context: Optional[str] = None) -> Dict[str, Any]:
        """
        Predict the likely quality of an interaction before execution
        """
        
        if not self.is_ready():
            return {'predicted_quality': 0.5, 'confidence': 'low', 
                   'explanation': 'Self-learning not initialized'}
        
        try:
            return await self.learning_manager.predict_interaction_quality(
                input_data=input_data,
                context=context
            )
        except Exception as e:
            print(f"⚠️ Quality prediction failed: {e}")
            return {'predicted_quality': 0.5, 'confidence': 'low', 'error': str(e)}
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get current learning metrics"""
        
        if not self.is_ready():
            return {'status': 'disabled'}
        
        return self.learning_manager.get_learning_metrics()
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get learning insights"""
        
        if not self.is_ready():
            return {'status': 'disabled'}
        
        return self.learning_manager.get_learning_insights()
    
    def generate_learning_report(self) -> Dict[str, Any]:
        """Generate comprehensive learning report"""
        
        if not self.is_ready():
            return {'status': 'disabled'}
        
        return self.learning_analytics.generate_learning_report()
    
    def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """Get analytics dashboard data"""
        
        if not self.is_ready():
            return {'status': 'disabled'}
        
        return self.learning_analytics.get_analytics_dashboard_data()


# Global instance for easy access
_integration = SelfLearningIntegration()


def get_self_learning() -> SelfLearningIntegration:
    """Get the global self-learning integration instance"""
    return _integration


def setup_self_learning(qdrant_host: str = "localhost", 
                       qdrant_port: int = 6333,
                       vector_service = None):
    """Setup the global self-learning system"""
    _integration.setup(
        qdrant_host=qdrant_host,
        qdrant_port=qdrant_port,
        vector_service=vector_service
    )


# Convenience functions for quick integration

async def learn_from_prompt_generation(input_data: Dict[str, Any],
                                       prompt_result: Dict[str, Any],
                                       quality_score: float = 0.5):
    """Quick learning from prompt generation"""
    integration = get_self_learning()
    if integration.is_ready():
        await integration.knowledge_graph.store_prompt_knowledge(
            input_data=input_data,
            prompt=prompt_result.get('prompt', ''),
            metadata=prompt_result,
            quality_score=quality_score
        )


async def learn_from_analysis(analysis_result: Dict[str, Any],
                              quality_score: float,
                              reasoning_chain: Optional[Dict[str, Any]] = None):
    """Quick learning from analysis"""
    integration = get_self_learning()
    if integration.is_ready():
        await integration.knowledge_graph.store_analysis_knowledge(
            analysis_result=analysis_result,
            quality_score=quality_score,
            reasoning_chain=reasoning_chain
        )


async def learn_from_validation(validation_result: Dict[str, Any],
                                input_data: Dict[str, Any],
                                response_data: Dict[str, Any]):
    """Quick learning from validation"""
    integration = get_self_learning()
    if integration.is_ready():
        await integration.knowledge_graph.store_validation_knowledge(
            validation_result=validation_result,
            input_data=input_data,
            response_data=response_data
        )

