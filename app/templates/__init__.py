"""
Templates package - Import all template modules
"""

# Import base template classes
from app.templates.base import BaseTemplate, PromptTemplate, TemplateParameter, TemplateRegistry

# Import banking templates
from app.templates.banking import (
    transaction_categorization,
    cash_flow_analysis,
    credit_assessment,
    offer_generation,
    card_spend_analysis,
    credit_utilization
)

# Export all templates
__all__ = [
    'BaseTemplate',
    'PromptTemplate', 
    'TemplateParameter',
    'TemplateRegistry',
    'transaction_categorization',
    'cash_flow_analysis',
    'credit_assessment',
    'offer_generation',
    'card_spend_analysis',
    'credit_utilization'
] 