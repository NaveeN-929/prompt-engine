"""
LLM Interface - Handles communication with various LLM providers
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class LLMInterface:
    """
    Interface for communicating with various LLM providers
    Supports Ollama, OpenAI, and other providers with failover capabilities
    """
    
    def __init__(self):
        self.config = None
        self.primary_provider = None
        self.session = None
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.provider_usage = {}
        
    def set_config(self, config: Dict[str, Any]):
        """Set configuration from parent agent"""
        self.config = config
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers based on configuration"""
        providers = []
        
        # Ollama provider (primary and only)
        ollama_config = self.config["llm"]["ollama"]
        if ollama_config["host"] and ollama_config["model"]:
            providers.append({
                "name": "ollama",
                "type": "ollama",
                "url": f"http://{ollama_config['host']}:{ollama_config['port']}",
                "model": ollama_config["model"],
                "priority": 1
            })
        
        if providers:
            self.primary_provider = providers[0]
        else:
            logger.warning("No LLM providers configured")
    
    async def initialize(self):
        """Initialize the LLM interface"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120),  # 2 minutes timeout
            headers={"Content-Type": "application/json"}
        )
        
        # Test primary provider
        if self.primary_provider:
            available = await self._test_provider(self.primary_provider)
            if available:
                logger.info(f"Primary LLM provider '{self.primary_provider['name']}' is available")
            else:
                logger.warning(f"Primary LLM provider '{self.primary_provider['name']}' is not available")
    
    async def generate_response(self, prompt: str, 
                              reasoning_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate response using available LLM providers with failover
        
        Args:
            prompt: The prompt to send to the LLM
            reasoning_context: Optional reasoning context for enhanced generation
            
        Returns:
            Dictionary containing response and metadata
        """
        self.total_requests += 1
        start_time = time.time()
        
        # Try primary provider only
        providers_to_try = [self.primary_provider] if self.primary_provider else []
        
        for provider in providers_to_try:
            if not provider:
                continue
                
            try:
                logger.info(f"Attempting LLM generation with provider: {provider['name']}")
                
                result = await self._generate_with_provider(provider, prompt, reasoning_context)
                
                if result and result.get("response"):
                    processing_time = time.time() - start_time
                    
                    # Update statistics
                    self.successful_requests += 1
                    self.provider_usage[provider['name']] = \
                        self.provider_usage.get(provider['name'], 0) + 1
                    
                    # Add metadata
                    result["metadata"] = {
                        "provider": provider["name"],
                        "model": provider["model"],
                        "processing_time": processing_time,
                        "attempt_number": providers_to_try.index(provider) + 1,
                        "total_attempts": len(providers_to_try)
                    }
                    
                    logger.info(f"LLM response generated successfully with {provider['name']} "
                               f"in {processing_time:.3f}s")
                    
                    return result
                    
            except Exception as e:
                logger.warning(f"Provider {provider['name']} failed: {e}")
                continue
        
        # All providers failed
        self.failed_requests += 1
        processing_time = time.time() - start_time
        
        logger.error("All LLM providers failed")
        
        return {
            "response": "",
            "metadata": {
                "provider": "none",
                "model": "none",
                "processing_time": processing_time,
                "error": "All providers failed"
            }
        }
    
    async def _generate_with_provider(self, provider: Dict[str, Any], 
                                    prompt: str,
                                    reasoning_context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate response with a specific provider"""
        
        if provider["type"] == "ollama":
            return await self._generate_with_ollama(provider, prompt, reasoning_context)
        elif provider["type"] == "openai":
            return await self._generate_with_openai(provider, prompt, reasoning_context)
        elif provider["type"] == "anthropic":
            return await self._generate_with_anthropic(provider, prompt, reasoning_context)
        else:
            logger.warning(f"Unknown provider type: {provider['type']}")
            return None
    
    async def _generate_with_ollama(self, provider: Dict[str, Any], 
                                  prompt: str,
                                  reasoning_context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate response using Ollama"""
        
        try:
            url = f"{provider['url']}/api/generate"
            
            # Enhance prompt with system context
            system_prompt = self._create_system_prompt(reasoning_context)
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            payload = {
                "model": provider["model"],
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistency
                    "top_p": 0.9,
                    "num_predict": 2000  # Max tokens
                }
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    return {
                        "response": result.get("response", ""),
                        "tokens_used": len(result.get("response", "").split()),
                        "model_info": {
                            "name": provider["model"],
                            "provider": "ollama"
                        }
                    }
                else:
                    logger.error(f"Ollama API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return None
    
    async def _generate_with_openai(self, provider: Dict[str, Any], 
                                  prompt: str,
                                  reasoning_context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate response using OpenAI API"""
        
        try:
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {provider['api_key']}",
                "Content-Type": "application/json"
            }
            
            # Create messages
            messages = [
                {
                    "role": "system",
                    "content": self._create_system_prompt(reasoning_context)
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            payload = {
                "model": provider["model"],
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 2000,
                "top_p": 0.9
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    choice = result["choices"][0]
                    usage = result.get("usage", {})
                    
                    return {
                        "response": choice["message"]["content"],
                        "tokens_used": usage.get("total_tokens", 0),
                        "model_info": {
                            "name": provider["model"],
                            "provider": "openai"
                        }
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return None
    
    async def _generate_with_anthropic(self, provider: Dict[str, Any], 
                                     prompt: str,
                                     reasoning_context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate response using Anthropic API"""
        
        try:
            url = "https://api.anthropic.com/v1/messages"
            
            headers = {
                "x-api-key": provider['api_key'],
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # Create messages
            system_prompt = self._create_system_prompt(reasoning_context)
            
            payload = {
                "model": provider["model"],
                "max_tokens": 2000,
                "temperature": 0.1,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    content = result["content"][0]["text"]
                    usage = result.get("usage", {})
                    
                    return {
                        "response": content,
                        "tokens_used": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                        "model_info": {
                            "name": provider["model"],
                            "provider": "anthropic"
                        }
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Anthropic API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            return None
    
    def _create_system_prompt(self, reasoning_context: Optional[Dict[str, Any]]) -> str:
        """Create system prompt with reasoning context"""
        
        base_prompt = """You are an autonomous financial analysis AI agent. Your role is to provide accurate, data-driven financial analysis based strictly on the provided information.

CRITICAL INSTRUCTIONS:
1. Base ALL analysis on the provided data only
2. Do NOT make assumptions beyond what the data supports
3. Include confidence levels for your findings
4. Acknowledge limitations and uncertainties
5. Provide specific, actionable insights
6. Maintain professional, analytical tone
7. Structure your response clearly with sections

If you are uncertain about any aspect, explicitly state your uncertainty rather than guessing."""
        
        if reasoning_context and reasoning_context.get("steps"):
            reasoning_summary = f"""
REASONING FRAMEWORK:
You have access to a multi-step reasoning chain that has been executed:
- Total steps: {len(reasoning_context['steps'])}
- Overall confidence: {reasoning_context.get('overall_confidence', 'unknown')}
- Validation status: {reasoning_context.get('validation_result', {}).get('passed', 'unknown')}

Use this reasoning framework to guide your analysis and ensure consistency with the logical steps provided."""
            
            base_prompt += reasoning_summary
        
        return base_prompt
    

    
    async def _test_provider(self, provider: Dict[str, Any]) -> bool:
        """Test if a provider is available"""
        
        try:
            test_prompt = "Test connection. Please respond with 'OK'."
            result = await self._generate_with_provider(provider, test_prompt, None)
            return result is not None and result.get("response")
        except:
            return False
    
    def is_available(self) -> bool:
        """Check if any LLM provider is available"""
        return self.primary_provider is not None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get LLM interface statistics"""
        
        success_rate = self.successful_requests / max(self.total_requests, 1)
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate,
            "provider_usage": self.provider_usage,
            "primary_provider": self.primary_provider["name"] if self.primary_provider else None
        }
    
    async def close(self):
        """Close the LLM interface and clean up resources"""
        if self.session:
            await self.session.close()