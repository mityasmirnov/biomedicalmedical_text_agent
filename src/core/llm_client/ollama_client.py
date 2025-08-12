"""
Ollama LLM client for local model fallback.
"""

import json
import time
import asyncio
from typing import Dict, List, Optional, Any
import httpx
from core.base import BaseLLMClient, ProcessingResult, LLMError
from core.config import get_config
from core.logging_config import get_logger

log = get_logger(__name__)

class OllamaClient(BaseLLMClient):
    """Client for Ollama local models."""
    
    def __init__(self, model_name: str = None, config: Optional[Dict[str, Any]] = None):
        app_config = get_config()
        self.base_url = app_config.llm.ollama_base_url
        self.timeout = app_config.llm.ollama_timeout
        
        model_name = model_name or app_config.llm.ollama_default_model
        super().__init__(model_name=model_name, config=config)
        
        # Default parameters
        self.default_temperature = app_config.llm.temperature
        self.default_max_tokens = app_config.llm.max_tokens
        
        log.info(f"Initialized Ollama client for model: {self.model_name}")
    
    async def _check_model_availability(self) -> bool:
        """Check if the specified model is available."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                models_data = response.json()
                
                available_models = [model["name"] for model in models_data.get("models", [])]
                return self.model_name in available_models
                
        except Exception as e:
            log.warning(f"Failed to check Ollama model availability: {e}")
            return False
    
    async def _pull_model_if_needed(self) -> bool:
        """Pull the model if it's not available."""
        try:
            if await self._check_model_availability():
                log.info(f"Model {self.model_name} is already available")
                return True
            
            log.info(f"Pulling model {self.model_name}...")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": self.model_name}
                )
                response.raise_for_status()
                
                # Wait for pull to complete
                while True:
                    status_response = await client.get(f"{self.base_url}/api/tags")
                    if status_response.status_code == 200:
                        models_data = status_response.json()
                        available_models = [model["name"] for model in models_data.get("models", [])]
                        if self.model_name in available_models:
                            log.info(f"Model {self.model_name} pulled successfully")
                            return True
                    
                    await asyncio.sleep(2)
                    
        except Exception as e:
            log.error(f"Failed to pull Ollama model {self.model_name}: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ProcessingResult[str]:
        """
        Generate text using Ollama local model.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            ProcessingResult containing generated text
        """
        start_time = time.time()
        
        try:
            # Ensure model is available
            if not await self._pull_model_if_needed():
                return ProcessingResult(
                    success=False,
                    error=f"Failed to load Ollama model: {self.model_name}"
                )
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature or self.default_temperature,
                    "num_predict": max_tokens or self.default_max_tokens,
                    **kwargs
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
            
            processing_time = time.time() - start_time
            
            # Extract generated text
            if "message" not in result:
                return ProcessingResult(
                    success=False,
                    error="No message returned from Ollama"
                )
            
            generated_text = result["message"]["content"]
            
            # Extract usage information (estimated)
            estimated_tokens = len(generated_text.split()) * 1.3  # Rough estimation
            
            log.debug(f"Generated {len(generated_text)} characters in {processing_time:.2f}s")
            
            return ProcessingResult(
                success=True,
                data=generated_text,
                processing_time=processing_time,
                metadata={
                    "model": self.model_name,
                    "provider": "ollama",
                    "estimated_tokens": int(estimated_tokens),
                    "fallback_used": True
                }
            )
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            log.error(f"Ollama API error: {error_msg}")
            return ProcessingResult(
                success=False,
                error=error_msg
            )
        except httpx.TimeoutException:
            error_msg = f"Request timeout after {self.timeout}s"
            log.error(error_msg)
            return ProcessingResult(
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            log.error(f"Ollama client error: {error_msg}")
            return ProcessingResult(
                success=False,
                error=error_msg
            )
    
    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ProcessingResult[str]:
        """
        Generate text using Ollama local model (synchronous).
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            ProcessingResult containing generated text
        """
        try:
            # Run async method in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.generate(prompt, system_prompt, temperature, max_tokens, **kwargs)
                )
                return result
            finally:
                loop.close()
                
        except Exception as e:
            error_msg = f"Sync generation error: {str(e)}"
            log.error(error_msg)
            return ProcessingResult(
                success=False,
                error=error_msg
            )
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models."""
        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                models_data = response.json()
                
                return [model["name"] for model in models_data.get("models", [])]
                
        except Exception as e:
            log.error(f"Error fetching available Ollama models: {str(e)}")
            return []
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """Get information about a specific Ollama model."""
        model_name = model_name or self.model_name
        
        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(f"{self.base_url}/api/show", params={"name": model_name})
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            log.error(f"Error fetching Ollama model info: {str(e)}")
            return {}
    
    def is_server_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
