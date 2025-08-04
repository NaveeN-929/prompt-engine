"""
Simple data models for API request/response validation
"""

from typing import Dict, Any, Optional, List
from enum import Enum

class ContextType(str, Enum):
    # Banking contexts
    CORE_BANKING = "core_banking"
    LENDING_DECISION = "lending_decision"
    LOAN_APPROVAL = "loan_approval"
    LOAN_OFFERS = "loan_offers"
    CARD_DATA = "card_data"
    RISK_ASSESSMENT = "risk_assessment"

class DataType(str, Enum):
    # Banking data types
    TRANSACTION_HISTORY = "transaction_history"
    TIME_SERIES_DATA = "time_series_data"
    TRANSACTION_ANALYSIS = "transaction_analysis"
    CREDIT_ASSESSMENT = "credit_assessment"
    CARD_TRANSACTIONS = "card_transactions"
    CARD_BEHAVIOR = "card_behavior"

class GenerateRequest:
    """Request for generating a prompt"""
    
    def __init__(self, context: str, data_type: str, input_data: Dict[str, Any]):
        self.context = context
        self.data_type = data_type
        self.input_data = input_data
        
        # Basic validation
        if not isinstance(input_data, dict):
            raise ValueError('input_data must be a dictionary')
        if not input_data:
            raise ValueError('input_data cannot be empty')

class GenerateResponse:
    """Response from prompt generation"""
    
    def __init__(self, prompt: str, response: str, tokens_used: int, 
                 template_used: str, processing_time: float, 
                 generation_mode: str = "basic", agentic_metadata: Dict[str, Any] = None):
        self.prompt = prompt
        self.response = response
        self.tokens_used = tokens_used
        self.template_used = template_used
        self.processing_time = processing_time
        self.generation_mode = generation_mode
        self.agentic_metadata = agentic_metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "prompt": self.prompt,
            "response": self.response,
            "tokens_used": self.tokens_used,
            "template_used": self.template_used,
            "processing_time": self.processing_time,
            "generation_mode": self.generation_mode
        }
        
        if self.agentic_metadata:
            result["agentic_metadata"] = self.agentic_metadata
            
        return result

class AgenticAnalysisResponse:
    """Response from agentic data analysis"""
    
    def __init__(self, analysis: Dict[str, Any], timestamp: float):
        self.analysis = analysis
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "analysis": self.analysis,
            "timestamp": self.timestamp
        }

class AgenticCapabilitiesResponse:
    """Response containing agentic system capabilities"""
    
    def __init__(self, capabilities: List[str], supported_contexts: List[str],
                 supported_data_types: List[str], analysis_features: List[str],
                 learning_stats: Dict[str, Any] = None):
        self.capabilities = capabilities
        self.supported_contexts = supported_contexts
        self.supported_data_types = supported_data_types
        self.analysis_features = analysis_features
        self.learning_stats = learning_stats or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "capabilities": self.capabilities,
            "supported_contexts": self.supported_contexts,
            "supported_data_types": self.supported_data_types,
            "analysis_features": self.analysis_features,
            "learning_stats": self.learning_stats
        }

class LearningFeedbackRequest:
    """Request for submitting learning feedback"""
    
    def __init__(self, input_data: Dict[str, Any], prompt_result: str, 
                 llm_response: str, quality_score: Optional[float] = None,
                 user_feedback: Optional[str] = None):
        self.input_data = input_data
        self.prompt_result = prompt_result
        self.llm_response = llm_response
        self.quality_score = quality_score
        self.user_feedback = user_feedback
        
        # Validation
        if not isinstance(input_data, dict) or not input_data:
            raise ValueError('input_data must be a non-empty dictionary')
        if not prompt_result or not llm_response:
            raise ValueError('prompt_result and llm_response are required')
        if quality_score is not None and (quality_score < 0 or quality_score > 1):
            raise ValueError('quality_score must be between 0 and 1')

class AgenticGenerateRequest:
    """Request for agentic prompt generation"""
    
    def __init__(self, input_data: Dict[str, Any], context: Optional[str] = None, 
                 data_type: Optional[str] = None, mode: str = "agentic",
                 reasoning_steps: int = 5, performance_feedback: Dict[str, Any] = None):
        self.input_data = input_data
        self.context = context
        self.data_type = data_type
        self.mode = mode
        self.reasoning_steps = reasoning_steps
        self.performance_feedback = performance_feedback
        
        # Validation
        if not isinstance(input_data, dict) or not input_data:
            raise ValueError('input_data must be a non-empty dictionary')
        if mode not in ["agentic", "basic", "autonomous", "reasoning", "optimize"]:
            raise ValueError('mode must be one of: agentic, basic, autonomous, reasoning, optimize')
        if reasoning_steps < 1 or reasoning_steps > 20:
            raise ValueError('reasoning_steps must be between 1 and 20')

class FeedbackResponse:
    """Response from feedback system"""
    
    def __init__(self, suggestions: List[str], interaction_count: int, 
                 performance_metrics: Dict[str, Any] = None):
        self.suggestions = suggestions
        self.interaction_count = interaction_count
        self.performance_metrics = performance_metrics or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "suggestions": self.suggestions,
            "interaction_count": self.interaction_count,
            "performance_metrics": self.performance_metrics
        }

class TemplateInfo:
    """Information about a template"""
    
    def __init__(self, name: str, category: str, description: str, 
                 parameters: List[str], examples: List[Dict[str, Any]] = None):
        self.name = name
        self.category = category
        self.description = description
        self.parameters = parameters
        self.examples = examples or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "parameters": self.parameters,
            "examples": self.examples
        }

class TemplatesResponse:
    """Response containing available templates"""
    
    def __init__(self, templates: List[TemplateInfo]):
        self.templates = templates
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "templates": [t.to_dict() for t in self.templates]
        }

class ErrorResponse:
    """Error response"""
    
    def __init__(self, error: str, details: Optional[str] = None):
        self.error = error
        self.details = details
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "error": self.error,
            "details": self.details
        } 