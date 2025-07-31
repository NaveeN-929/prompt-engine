"""
Prompt Generator - Matches requests to templates and generates prompts
"""

import time
from typing import Dict, Any, Tuple, List
from app.templates.base import TemplateRegistry
from app.templates.banking import (
    transaction_categorization,
    cash_flow_analysis,
    credit_assessment,
    offer_generation,
    card_spend_analysis,
    credit_utilization
)

class PromptGenerator:
    """Generates prompts by matching requests to templates"""
    
    def __init__(self):
        self.template_registry = TemplateRegistry()
        self._register_templates()
    
    def _register_templates(self):
        """Register all available templates"""
        # Register banking templates
        self.template_registry.register(transaction_categorization)
        self.template_registry.register(cash_flow_analysis)
        self.template_registry.register(credit_assessment)
        self.template_registry.register(offer_generation)
        self.template_registry.register(card_spend_analysis)
        self.template_registry.register(credit_utilization)
    
    def generate_prompt(self, context: str, data_type: str, input_data: Dict[str, Any]) -> Tuple[str, str, float]:
        """
        Generate a prompt based on context and data type
        
        Returns:
            Tuple of (prompt_text, template_name, processing_time)
        """
        start_time = time.time()
        
        # Find the appropriate template
        template = self.template_registry.get_template(context, data_type)
        if not template:
            raise ValueError(f"No template found for context '{context}' and data_type '{data_type}'")
        
        # Validate input data against template parameters
        template.validate_parameters(input_data)
        
        # Generate the prompt
        prompt_text = template.render(input_data)
        
        processing_time = time.time() - start_time
        
        return prompt_text, template.name, processing_time
    
    def get_available_templates(self) -> Dict[str, Any]:
        """Get information about all available templates"""
        templates = []
        
        for template in self.template_registry.get_all_templates():
            template_info = {
                "name": template.name,
                "category": template.context,
                "description": f"Template for {template.context} - {template.data_type}",
                "parameters": [
                    {
                        "name": param_name,
                        "type": param_info.get("type", "str"),
                        "required": param_info.get("required", True),
                        "default": param_info.get("default", None)
                    }
                    for param_name, param_info in template.parameters.items()
                ],
                "examples": [
                    {
                        "context": template.context,
                        "data_type": template.data_type,
                        "input_data": {
                            param_name: f"<{param_name}_value>"
                            for param_name in template.parameters.keys()
                        }
                    }
                ]
            }
            templates.append(template_info)
        
        return {"templates": templates}
    
    def get_template_parameters(self, context: str, data_type: str) -> Dict[str, Any]:
        """Get detailed information about a specific template"""
        template = self.template_registry.get_template(context, data_type)
        if not template:
            return None
        
        return {
            "name": template.name,
            "context": template.context,
            "data_type": template.data_type,
            "parameters": template.parameters,
            "template": template.template,
            "examples": [
                {
                    "context": template.context,
                    "data_type": template.data_type,
                    "input_data": {
                        param_name: f"<{param_name}_value>"
                        for param_name in template.parameters.keys()
                    }
                }
            ]
        } 