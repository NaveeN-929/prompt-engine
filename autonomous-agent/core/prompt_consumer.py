"""
Prompt Consumer Service - Integrates with the main prompt-engine
"""

import asyncio
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptConsumerService:
    """
    Service to consume prompts from the main prompt-engine and prepare them for RAG enhancement
    """
    
    def __init__(self, prompt_engine_url: str = "http://localhost:5000"):
        self.prompt_engine_url = prompt_engine_url
        self.session = requests.Session()
        self.session.timeout = 30
        
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the prompt engine"""
        try:
            # Try the correct endpoint based on the logs
            response = self.session.get(f"{self.prompt_engine_url}/system/status")
            if response.status_code == 200:
                return {
                    "available": True,
                    "status": "connected",
                    "response": response.json()
                }
            else:
                # Fallback to trying /health
                try:
                    response = self.session.get(f"{self.prompt_engine_url}/health")
                    if response.status_code == 200:
                        return {
                            "available": True,
                            "status": "connected",
                            "response": response.json()
                        }
                except:
                    pass
                
                return {
                    "available": False,
                    "status": f"http_error_{response.status_code}",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "available": False,
                "status": "connection_failed",
                "error": str(e)
            }
    
    async def get_prompt_engine_capabilities(self) -> Dict[str, Any]:
        """Get capabilities from the prompt engine"""
        try:
            response = self.session.get(f"{self.prompt_engine_url}/capabilities")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def generate_prompt_from_data(self, input_data: Dict[str, Any], 
                                 context_type: str = "financial_analysis") -> Dict[str, Any]:
        """
        Generate a prompt using the prompt-engine based on input data
        
        Args:
            input_data: Financial data to analyze
            context_type: Type of analysis context
            
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        try:
            # Prepare request for prompt engine
            prompt_request = {
                "input_data": input_data,
                "context": context_type,
                "analysis_type": "comprehensive",
                "include_reasoning": True,
                "enable_agentic": True
            }
            
            logger.info(f"Requesting prompt generation for {context_type}")
            
            # Call prompt engine
            response = self.session.post(
                f"{self.prompt_engine_url}/generate",
                json=prompt_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the generated prompt
                generated_prompt = result.get("prompt", "")
                
                return {
                    "success": True,
                    "prompt": generated_prompt,
                    "prompt_metadata": {
                        "source": "prompt_engine",
                        "context_type": context_type,
                        "generated_at": datetime.now().isoformat(),
                        "original_data_summary": {
                            "transaction_count": len(input_data.get("transactions", [])),
                            "has_balance": "account_balance" in input_data,
                            "data_keys": list(input_data.keys())
                        },
                        "prompt_engine_response": result
                    }
                }
            else:
                logger.error(f"Prompt engine returned {response.status_code}")
                return {
                    "success": False,
                    "error": f"Prompt engine error: HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_agentic_prompt(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an agentic prompt using the prompt-engine's agentic capabilities
        """
        try:
            # Use the main generate endpoint with agentic generation type
            agentic_request = {
                "input_data": input_data,
                "generation_type": "autonomous"  # This triggers agentic mode
            }
            
            logger.info("Requesting agentic prompt generation via main endpoint")
            
            # Use the main generate endpoint which supports agentic generation
            response = self.session.post(
                f"{self.prompt_engine_url}/generate",
                json=agentic_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "prompt": result.get("prompt", ""),
                    "prompt_metadata": {
                        "source": "prompt_engine_agentic",
                        "agentic_features": True,
                        "generated_at": datetime.now().isoformat(),
                        "prompt_engine_response": result
                    }
                }
            else:
                logger.error(f"Agentic prompt generation failed: HTTP {response.status_code}")
                return {
                    "success": False,
                    "error": f"Agentic prompt generation failed: HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Agentic prompt generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    

    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.session.close()
    
    async def consume_prompt(self, input_data: Dict[str, Any], 
                           generation_type: str = "standard",
                           context: str = None,
                           data_type: str = None) -> Dict[str, Any]:
        """
        Async method to consume prompt from prompt engine
        """
        if generation_type == "agentic":
            return self.generate_agentic_prompt(input_data)
        else:
            return self.generate_prompt_from_data(input_data, context or "financial_analysis")
    
    async def submit_learning_feedback(self, input_data: Dict[str, Any],
                                     prompt_result: str,
                                     agent_response: str,
                                     quality_score: float,
                                     user_feedback: str) -> Dict[str, Any]:
        """
        Submit learning feedback to prompt engine
        """
        try:
            feedback_request = {
                "input_data": input_data,
                "prompt_result": prompt_result,
                "agent_response": agent_response,
                "quality_score": quality_score,
                "user_feedback": user_feedback
            }
            
            response = self.session.post(
                f"{self.prompt_engine_url}/feedback",
                json=feedback_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {"success": True, "response": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}