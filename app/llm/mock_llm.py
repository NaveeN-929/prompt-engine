"""
Ollama LLM Interface - Connects to real Ollama instance
"""

import time
import requests
import json
from typing import Dict, Any, List, Tuple

class OllamaLLM:
    """Real LLM interface that connects to Ollama instance"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"
    
    def generate_response(self, prompt: str, template_name: str = None) -> Tuple[str, int, float]:
        """
        Generate a response using Ollama
        
        Returns:
            Tuple of (response_text, tokens_used, processing_time)
        """
        start_time = time.time()
        
        # Prepare the request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 200  # Reduced for faster responses
            }
        }
        
        # Make the API call
        response = requests.post(
            self.api_url,
            json=payload,
            headers={"Content-Type": "application/json"}
            # No timeout - allow unlimited processing time for local LLM
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
        
        # Parse the response
        result = response.json()
        response_text = result.get("response", "")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Estimate token usage (Ollama doesn't always provide exact counts)
        # Rough estimation: 1 token ≈ 4 characters for English text
        estimated_tokens = len(prompt.split()) + len(response_text.split())
        
        return response_text, estimated_tokens, processing_time
    
    def list_models(self) -> List[str]:
        """List available models on the Ollama instance"""
        response = requests.get(f"{self.base_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        else:
            raise Exception(f"Failed to list models: {response.status_code}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        response = requests.get(f"{self.base_url}/api/show", params={"name": self.model})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get model info: {response.status_code}")
    
    def test_connection(self) -> bool:
        """Test if Ollama is accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)  # Keep short timeout for health checks
            return response.status_code == 200
        except:
            return False

# Keep the old MockLLM class for backward compatibility
class MockLLM(OllamaLLM):
    """Backward compatibility wrapper"""
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        super().__init__(base_url, model) 