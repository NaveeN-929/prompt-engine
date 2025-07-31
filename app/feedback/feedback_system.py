"""
Feedback System - Logs interactions and provides optimization suggestions
"""

import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class InteractionLog:
    """Represents a single interaction log entry"""
    
    def __init__(self, prompt: str, response: str, template_name: str, 
                 tokens_used: int, processing_time: float, context: str, data_type: str):
        self.timestamp = datetime.now()
        self.prompt = prompt
        self.response = response
        self.template_name = template_name
        self.tokens_used = tokens_used
        self.processing_time = processing_time
        self.context = context
        self.data_type = data_type
        self.success = True  # Assume success for demo
        self.user_feedback = None  # Could be added later
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "prompt": self.prompt,
            "response": self.response,
            "template_name": self.template_name,
            "tokens_used": self.tokens_used,
            "processing_time": self.processing_time,
            "context": self.context,
            "data_type": self.data_type,
            "success": self.success,
            "user_feedback": self.user_feedback
        }

class FeedbackSystem:
    """Manages interaction logging and provides optimization suggestions"""
    
    def __init__(self):
        self.interactions: List[InteractionLog] = []
        self.optimization_suggestions = self._initialize_suggestions()
    
    def _initialize_suggestions(self) -> Dict[str, List[str]]:
        """Initialize optimization suggestions by template"""
        return {
            "customer_service_complaint": [
                "Consider adding more specific product details to improve response accuracy",
                "Template shows high success rate - consider expanding to similar use cases",
                "Response time is optimal, but could benefit from more empathetic language patterns",
                "Token usage is efficient - template is well-optimized for this context"
            ],
            "customer_service_refund": [
                "Add more specific refund policy details to reduce follow-up questions",
                "Consider including estimated processing times in the template",
                "Template performs well but could benefit from more detailed next steps",
                "High customer satisfaction scores suggest this template is effective"
            ],
            "customer_service_product_inquiry": [
                "Consider adding product specification details to the template",
                "Template could benefit from more technical detail options",
                "Response quality is high but could include more product comparisons",
                "Consider adding FAQ integration for common questions"
            ],
            "data_analysis_csv": [
                "Template could benefit from more specific data visualization suggestions",
                "Consider adding statistical significance testing to the analysis",
                "High accuracy in insights - template is well-optimized",
                "Could benefit from more detailed correlation analysis patterns"
            ],
            "data_analysis_statistical": [
                "Consider adding confidence interval calculations to the template",
                "Template performs well for descriptive statistics",
                "Could benefit from more advanced statistical test suggestions",
                "High accuracy in statistical interpretations"
            ],
            "data_analysis_trend": [
                "Consider adding seasonal decomposition to trend analysis",
                "Template could benefit from more forecasting detail options",
                "High accuracy in trend identification",
                "Could include more anomaly detection patterns"
            ]
        }
    
    def log_interaction(self, prompt: str, response: str, template_name: str,
                       tokens_used: int, processing_time: float, context: str, data_type: str):
        """Log a new interaction"""
        interaction = InteractionLog(
            prompt=prompt,
            response=response,
            template_name=template_name,
            tokens_used=tokens_used,
            processing_time=processing_time,
            context=context,
            data_type=data_type
        )
        
        self.interactions.append(interaction)
        
        # Keep only last 1000 interactions for demo purposes
        if len(self.interactions) > 1000:
            self.interactions = self.interactions[-1000:]
    
    def get_optimization_suggestions(self) -> Dict[str, Any]:
        """Get optimization suggestions based on interaction history"""
        if not self.interactions:
            return {
                "suggestions": ["No interactions logged yet. Start using the system to get personalized suggestions."],
                "interaction_count": 0,
                "performance_metrics": {}
            }
        
        # Analyze recent interactions (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_interactions = [
            i for i in self.interactions 
            if i.timestamp > thirty_days_ago
        ]
        
        # Generate suggestions based on template usage
        suggestions = []
        template_usage = {}
        
        for interaction in recent_interactions:
            template = interaction.template_name
            if template not in template_usage:
                template_usage[template] = {
                    "count": 0,
                    "total_tokens": 0,
                    "avg_processing_time": 0,
                    "total_processing_time": 0
                }
            
            template_usage[template]["count"] += 1
            template_usage[template]["total_tokens"] += interaction.tokens_used
            template_usage[template]["total_processing_time"] += interaction.processing_time
        
        # Calculate averages and generate suggestions
        for template, stats in template_usage.items():
            avg_tokens = stats["total_tokens"] / stats["count"]
            avg_processing_time = stats["total_processing_time"] / stats["count"]
            
            # Add template-specific suggestions
            if template in self.optimization_suggestions:
                template_suggestions = self.optimization_suggestions[template]
                suggestions.extend(random.sample(template_suggestions, min(2, len(template_suggestions))))
            
            # Add performance-based suggestions
            if avg_tokens > 200:
                suggestions.append(f"Template '{template}' shows high token usage ({avg_tokens:.0f} avg). Consider optimizing for efficiency.")
            
            if avg_processing_time > 1.5:
                suggestions.append(f"Template '{template}' has slow processing time ({avg_processing_time:.2f}s avg). Consider simplifying the prompt.")
            
            if stats["count"] > 50:
                suggestions.append(f"Template '{template}' is heavily used ({stats['count']} times). Consider creating variations for different scenarios.")
        
        # Add general suggestions
        total_interactions = len(recent_interactions)
        if total_interactions > 100:
            suggestions.append("High interaction volume detected. Consider implementing automated template optimization.")
        
        if len(template_usage) < 3:
            suggestions.append("Limited template diversity. Consider exploring different template types for better coverage.")
        
        # Calculate performance metrics
        performance_metrics = {
            "total_interactions": len(self.interactions),
            "recent_interactions": len(recent_interactions),
            "template_diversity": len(template_usage),
            "avg_tokens_per_interaction": sum(i.tokens_used for i in recent_interactions) / len(recent_interactions) if recent_interactions else 0,
            "avg_processing_time": sum(i.processing_time for i in recent_interactions) / len(recent_interactions) if recent_interactions else 0,
            "most_used_template": max(template_usage.items(), key=lambda x: x[1]["count"])[0] if template_usage else None
        }
        
        return {
            "suggestions": suggestions[:5],  # Limit to 5 suggestions
            "interaction_count": len(self.interactions),
            "performance_metrics": performance_metrics
        }
    
    def get_template_performance(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a specific template"""
        template_interactions = [i for i in self.interactions if i.template_name == template_name]
        
        if not template_interactions:
            return None
        
        return {
            "template_name": template_name,
            "total_uses": len(template_interactions),
            "avg_tokens": sum(i.tokens_used for i in template_interactions) / len(template_interactions),
            "avg_processing_time": sum(i.processing_time for i in template_interactions) / len(template_interactions),
            "success_rate": sum(1 for i in template_interactions if i.success) / len(template_interactions),
            "last_used": max(i.timestamp for i in template_interactions).isoformat()
        }
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get overall usage statistics"""
        if not self.interactions:
            return {
                "total_interactions": 0,
                "unique_templates": 0,
                "avg_tokens": 0,
                "avg_processing_time": 0
            }
        
        unique_templates = len(set(i.template_name for i in self.interactions))
        avg_tokens = sum(i.tokens_used for i in self.interactions) / len(self.interactions)
        avg_processing_time = sum(i.processing_time for i in self.interactions) / len(self.interactions)
        
        return {
            "total_interactions": len(self.interactions),
            "unique_templates": unique_templates,
            "avg_tokens": avg_tokens,
            "avg_processing_time": avg_processing_time,
            "templates_used": list(set(i.template_name for i in self.interactions))
        }
    
    def clear_interactions(self):
        """Clear all interaction history (for testing/demo purposes)"""
        self.interactions.clear() 