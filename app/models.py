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
                 template_used: str, processing_time: float):
        self.prompt = prompt
        self.response = response
        self.tokens_used = tokens_used
        self.template_used = template_used
        self.processing_time = processing_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "prompt": self.prompt,
            "response": self.response,
            "tokens_used": self.tokens_used,
            "template_used": self.template_used,
            "processing_time": self.processing_time
        }

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