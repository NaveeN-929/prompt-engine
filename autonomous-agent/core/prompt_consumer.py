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
    
    def get_prompt_engine_capabilities(self) -> Dict[str, Any]:
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
                    "error": f"Prompt engine error: HTTP {response.status_code}",
                    "fallback_prompt": self._create_fallback_prompt(input_data)
                }
                
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_prompt": self._create_fallback_prompt(input_data)
            }
    
    def generate_agentic_prompt(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an agentic prompt using the prompt-engine's agentic capabilities
        """
        try:
            # Use the agentic endpoint if available
            agentic_request = {
                "input_data": input_data,
                "autonomous_mode": True,
                "reasoning_depth": "comprehensive",
                "include_validation": True
            }
            
            logger.info("Requesting agentic prompt generation")
            
            # Try agentic endpoint first
            response = self.session.post(
                f"{self.prompt_engine_url}/agentic/autonomous",
                json=agentic_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "prompt": result.get("optimized_prompt", result.get("prompt", "")),
                    "prompt_metadata": {
                        "source": "prompt_engine_agentic",
                        "agentic_features": True,
                        "generated_at": datetime.now().isoformat(),
                        "prompt_engine_response": result
                    }
                }
            else:
                # Fallback to regular generation
                return self.generate_prompt_from_data(input_data, "agentic_analysis")
                
        except Exception as e:
            logger.warning(f"Agentic prompt generation failed: {e}")
            # Fallback to regular generation
            return self.generate_prompt_from_data(input_data, "agentic_analysis")
    
    def _create_fallback_prompt(self, input_data: Dict[str, Any]) -> str:
        """Create a fallback prompt when prompt engine is unavailable"""
        
        prompt = "Perform a comprehensive financial analysis of the provided data.\n\n"
        
        if "transactions" in input_data:
            tx_count = len(input_data["transactions"])
            prompt += f"Analyze {tx_count} financial transactions, including:\n"
            prompt += "- Cash flow patterns and trends\n"
            prompt += "- Transaction categorization and insights\n"
            prompt += "- Spending behavior analysis\n\n"
        
        if "account_balance" in input_data:
            prompt += "Evaluate account balance and liquidity position:\n"
            prompt += "- Current financial health assessment\n"
            prompt += "- Emergency fund adequacy\n"
            prompt += "- Liquidity risk analysis\n\n"
        
        prompt += "Provide actionable recommendations based on:\n"
        prompt += "- Financial best practices\n"
        prompt += "- Risk management principles\n"
        prompt += "- Wealth building strategies\n"
        prompt += "- Industry benchmarks and standards\n\n"
        
        prompt += "Structure your analysis with clear sections and quantitative insights."
        
        return prompt
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.session.close()