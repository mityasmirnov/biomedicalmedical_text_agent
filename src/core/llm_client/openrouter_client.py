"""
OpenRouter LLM client for the Biomedical Data Extraction Engine.
"""

import json
import time
from typing import Dict, List, Optional, Any
import httpx
import asyncio
from core.base import BaseLLMClient, ProcessingResult, LLMError
from core.config import get_config
from core.logging_config import get_logger

log = get_logger(__name__)

class OpenRouterClient(BaseLLMClient):
    """Client for OpenRouter API supporting various LLM models."""
    
    def __init__(self, model_name: str = None, config: Optional[Dict[str, Any]] = None):
        app_config = get_config()
        self.api_key = app_config.llm.openrouter_api_key
        self.api_base = app_config.llm.openrouter_api_base
        
        if not self.api_key:
            raise LLMError("OpenRouter API key not configured")
        
        model_name = model_name or app_config.llm.default_model
        super().__init__(model_name=model_name, config=config)
        
        # Default parameters
        self.default_temperature = app_config.llm.temperature
        self.default_max_tokens = app_config.llm.max_tokens
        self.timeout = app_config.llm.timeout
        
        # Rate limiting
        self.max_requests_per_minute = self.get_config("max_requests_per_minute", 60)
        self.request_timestamps = []
        
        log.info(f"Initialized OpenRouter client for model: {self.model_name}")
    
    def _setup(self) -> None:
        """Setup the OpenRouter client."""
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://biomedical-extraction-engine.com",
            "X-Title": "Biomedical Data Extraction Engine"
        }
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ProcessingResult[str]:
        """
        Generate text using OpenRouter API (async).
        
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
            # Rate limiting
            await self._check_rate_limit()
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature or self.default_temperature,
                "max_tokens": max_tokens or self.default_max_tokens,
                **kwargs
            }
            
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
            
            processing_time = time.time() - start_time
            
            # Extract generated text
            if "choices" not in result or not result["choices"]:
                return ProcessingResult(
                    success=False,
                    error="No choices returned from API"
                )
            
            generated_text = result["choices"][0]["message"]["content"]
            
            # Extract usage information
            usage = result.get("usage", {})
            
            log.debug(f"Generated {len(generated_text)} characters in {processing_time:.2f}s")
            
            return ProcessingResult(
                success=True,
                data=generated_text,
                processing_time=processing_time,
                metadata={
                    "model": self.model_name,
                    "usage": usage,
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
            )
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            log.error(f"OpenRouter API error: {error_msg}")
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
            log.error(f"OpenRouter client error: {error_msg}")
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
        Generate text using OpenRouter API (synchronous).
        
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
    
    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        current_time = time.time()
        
        # Remove timestamps older than 1 minute
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if current_time - ts < 60
        ]
        
        # Check if we're at the limit
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            sleep_time = 60 - (current_time - self.request_timestamps[0])
            if sleep_time > 0:
                log.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
        
        # Add current request timestamp
        self.request_timestamps.append(current_time)
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from OpenRouter."""
        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{self.api_base}/models",
                    headers=self.headers
                )
                response.raise_for_status()
                models_data = response.json()
                
                return [model["id"] for model in models_data.get("data", [])]
                
        except Exception as e:
            log.error(f"Error fetching available models: {str(e)}")
            return []
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """Get information about a specific model."""
        model_name = model_name or self.model_name
        
        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{self.api_base}/models",
                    headers=self.headers
                )
                response.raise_for_status()
                models_data = response.json()
                
                for model in models_data.get("data", []):
                    if model["id"] == model_name:
                        return model
                
                return {}
                
        except Exception as e:
            log.error(f"Error fetching model info: {str(e)}")
            return {}
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost for a request (if pricing info is available)."""
        model_info = self.get_model_info()
        pricing = model_info.get("pricing", {})
        
        if not pricing:
            return 0.0
        
        prompt_cost = (prompt_tokens / 1000) * float(pricing.get("prompt", 0))
        completion_cost = (completion_tokens / 1000) * float(pricing.get("completion", 0))
        
        return prompt_cost + completion_cost
    
    def validate_model(self, model_name: str = None) -> bool:
        """Validate that a model is available."""
        model_name = model_name or self.model_name
        available_models = self.get_available_models()
        return model_name in available_models

