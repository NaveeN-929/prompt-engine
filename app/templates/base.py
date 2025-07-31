"""
Base template classes for the prompt template system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import re

class TemplateParameter:
    """Template parameter definition"""
    
    def __init__(self, name: str, description: str = "", required: bool = True, 
                 default_value: Any = None, validation_regex: str = None):
        self.name = name
        self.description = description
        self.required = required
        self.default_value = default_value
        self.validation_regex = validation_regex
    
    def validate_value(self, value: Any) -> bool:
        """Validate a parameter value"""
        if self.required and value is None:
            return False
        
        if self.validation_regex and value:
            if not re.match(self.validation_regex, str(value)):
                return False
        
        return True
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "required": self.required,
            "default_value": self.default_value,
            "validation_regex": self.validation_regex
        }

class PromptTemplate:
    """Simple prompt template class for banking templates"""
    
    def __init__(self, name: str, context: str, data_type: str, template: str, parameters: Dict[str, Any]):
        self.name = name
        self.context = context
        self.data_type = data_type
        self.template = template
        self.parameters = parameters
    
    def validate_parameters(self, input_data: Dict[str, Any]):
        """Validate input data against template parameters"""
        for param_name, param_info in self.parameters.items():
            if param_info.get("required", True) and param_name not in input_data:
                raise ValueError(f"Required parameter '{param_name}' is missing")
    
    def render(self, input_data: Dict[str, Any]) -> str:
        """Render the template with the provided data"""
        self.validate_parameters(input_data)
        
        # Simple template rendering with {parameter_name} placeholders
        try:
            rendered = self.template.format(**input_data)
            return rendered
        except KeyError as e:
            raise ValueError(f"Missing required parameter in template: {e}")
        except Exception as e:
            raise ValueError(f"Template rendering error: {e}")

class BaseTemplate(ABC):
    """Base class for all prompt templates"""
    
    def __init__(self):
        self.name: str = ""
        self.description: str = ""
        self.category: str = ""
        self.parameters: List[TemplateParameter] = []
        self.template_text: str = ""
        self.examples: List[Dict[str, Any]] = []
    
    @abstractmethod
    def get_parameters(self) -> List[TemplateParameter]:
        """Return the list of parameters for this template"""
        pass
    
    @abstractmethod
    def get_template_text(self) -> str:
        """Return the template text with placeholders"""
        pass
    
    def validate_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data against template parameters"""
        validated_data = {}
        errors = []
        
        # Get required parameters
        params = self.get_parameters()
        param_dict = {p.name: p for p in params}
        
        # Check required parameters
        for param in params:
            if param.required and param.name not in input_data:
                if param.default_value is not None:
                    validated_data[param.name] = param.default_value
                else:
                    errors.append(f"Required parameter '{param.name}' is missing")
            elif param.name in input_data:
                # Validate the value
                if param.validate_value(input_data[param.name]):
                    validated_data[param.name] = input_data[param.name]
                else:
                    errors.append(f"Parameter '{param.name}' has invalid value")
            elif param.default_value is not None:
                validated_data[param.name] = param.default_value
        
        if errors:
            raise ValueError(f"Template validation errors: {'; '.join(errors)}")
        
        return validated_data
    
    def render(self, input_data: Dict[str, Any]) -> str:
        """Render the template with the provided data"""
        validated_data = self.validate_input_data(input_data)
        template_text = self.get_template_text()
        
        # Simple template rendering with {parameter_name} placeholders
        try:
            rendered = template_text.format(**validated_data)
            return rendered
        except KeyError as e:
            raise ValueError(f"Missing required parameter in template: {e}")
        except Exception as e:
            raise ValueError(f"Template rendering error: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get template information"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "parameters": [p.dict() for p in self.get_parameters()],
            "examples": self.examples
        }

class TemplateRegistry:
    """Registry for managing prompt templates"""
    
    def __init__(self):
        self.templates: Dict[str, Any] = {}
    
    def register(self, template: PromptTemplate):
        """Register a template"""
        key = f"{template.context}_{template.data_type}"
        self.templates[key] = template
    
    def get_template(self, context: str, data_type: str) -> Optional[PromptTemplate]:
        """Get a template by context and data type"""
        key = f"{context}_{data_type}"
        return self.templates.get(key)
    
    def get_all_templates(self) -> List[PromptTemplate]:
        """Get all registered templates"""
        return list(self.templates.values()) 