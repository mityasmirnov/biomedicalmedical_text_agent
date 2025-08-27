"""
OpenRouter LLM client for the Biomedical Data Extraction Engine.
"""

import json
import time
import logging
import os
from typing import Dict, List, Optional, Any
import httpx
import asyncio

# Remove circular imports
# from core.base import BaseLLMClient, ProcessingResult, LLMError
# from core.config import get_config
# from core.logging_config import get_logger
# from core.api_usage_tracker import APIUsageTracker, APIUsageRecord

log = logging.getLogger(__name__)

# Simple classes to avoid circular imports
class BaseLLMClient:
    """Simple base LLM client class."""
    def __init__(self, model_name: str = None, config: Optional[Dict[str, Any]] = None):
        self.model_name = model_name or "google/gemma-2-27b-it:free"
        self.config = config or {}

class ProcessingResult:
    """Simple processing result class for LLM operations."""
    def __init__(self, success: bool, data: Any = None, error: str = None, metadata: Dict[str, Any] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}

class LLMError(Exception):
    """Simple LLM error class."""
    pass

class APIUsageTracker:
    """Simple API usage tracker class."""
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def check_daily_limit(self, provider: str, limit: int) -> tuple[bool, int, int]:
        return True, 0, limit
    
    def check_monthly_limit(self, provider: str, limit: int) -> tuple[bool, int, int]:
        return True, 0, limit

class APIUsageRecord:
    """Simple API usage record class."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def get_config():
    """Simple config getter to avoid circular imports."""
    class SimpleConfig:
        def __init__(self):
            self.llm = SimpleLLMConfig()
    
    class SimpleLLMConfig:
        def __init__(self):
            self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
            self.openrouter_api_base = "https://openrouter.ai/api/v1"
            self.default_model = "gpt-3.5-turbo"
            self.temperature = 0.1
            self.max_tokens = 2048
            self.timeout = 60
            self.max_requests_per_minute = 60
            self.max_requests_per_day = 1000
            self.max_requests_per_month = 30000
            self.enable_usage_tracking = False
            self.usage_database_path = "data/api_usage.db"
    
    return SimpleConfig()

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
        self.max_requests_per_minute = app_config.llm.max_requests_per_minute
        self.request_timestamps = []
        
        # API usage tracking
        self.usage_tracker = None
        if app_config.llm.enable_usage_tracking:
            try:
                self.usage_tracker = APIUsageTracker(app_config.llm.usage_database_path)
                log.info("API usage tracking enabled")
            except Exception as e:
                log.warning(f"Failed to initialize API usage tracker: {e}")
        
        # Usage limits
        self.daily_limit = app_config.llm.max_requests_per_day
        self.monthly_limit = app_config.llm.max_requests_per_month
        
        # Setup headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://biomedical-extraction-engine.com",
            "X-Title": "Biomedical Data Extraction Engine"
        }
        
        log.info(f"Initialized OpenRouter client for model: {self.model_name}")
    
    async def _check_usage_limits(self) -> bool:
        """Check if usage limits allow the request to proceed."""
        if not self.usage_tracker:
            return True
        
        try:
            # Check daily limit
            can_proceed, current_usage, remaining = self.usage_tracker.check_daily_limit(
                "openrouter", self.daily_limit
            )
            
            if not can_proceed:
                log.warning(f"Daily limit reached: {current_usage}/{self.daily_limit} requests")
                return False
            
            # Check monthly limit
            can_proceed, current_usage, remaining = self.usage_tracker.check_monthly_limit(
                "openrouter", self.monthly_limit
            )
            
            if not can_proceed:
                log.warning(f"Monthly limit reached: {current_usage}/{self.monthly_limit} requests")
                return False
            
            log.debug(f"Usage limits check passed. Daily: {remaining} remaining, Monthly: {remaining} remaining")
            return True
            
        except Exception as e:
            log.error(f"Failed to check usage limits: {e}")
            return True  # Allow request if check fails
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False
    ) -> ProcessingResult:
        """
        Generate text using OpenRouter API.
        
        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            stop_sequences: Sequences to stop generation
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            stream: Whether to stream the response
            
        Returns:
            ProcessingResult containing the generated text
        """
        start_time = time.time()
        
        try:
            # Check usage limits first
            if not await self._check_usage_limits():
                return ProcessingResult(
                    success=False,
                    error="API usage limit reached. Please try again later or upgrade your plan."
                )
            
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
                "max_tokens": max_tokens or self.default_max_tokens
            }
            
            # Add optional parameters if provided
            if stop_sequences:
                payload["stop"] = stop_sequences
            if top_p is not None:
                payload["top_p"] = top_p
            if frequency_penalty is not None:
                payload["frequency_penalty"] = frequency_penalty
            if presence_penalty is not None:
                payload["presence_penalty"] = presence_penalty
            if stream:
                payload["stream"] = stream
            
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
                # Record failed request
                if self.usage_tracker:
                    self._record_api_usage(False, 0, 0, 0, 0.0, "No choices returned from API")
                
                return ProcessingResult(
                    success=False,
                    error="No choices returned from API"
                )
            
            generated_text = result["choices"][0]["message"]["content"]
            
            # Extract usage information
            usage = result.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            # Estimate cost
            estimated_cost = self.estimate_cost(prompt_tokens, completion_tokens)
            
            # Record successful request
            if self.usage_tracker:
                self._record_api_usage(True, prompt_tokens, completion_tokens, total_tokens, estimated_cost)
            
            log.debug(f"Generated {len(generated_text)} characters in {processing_time:.2f}s")
            
            return ProcessingResult(
                success=True,
                data=generated_text,
                metadata={
                    "model": self.model_name,
                    "usage": usage,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "estimated_cost": estimated_cost,
                    "processing_time": processing_time
                }
            )
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            log.error(f"OpenRouter API error: {error_msg}")
            
            # Record failed request
            if self.usage_tracker:
                self._record_api_usage(False, 0, 0, 0, 0.0, error_msg)
            
            return ProcessingResult(
                success=False,
                error=error_msg
            )
        except httpx.TimeoutException:
            error_msg = f"Request timeout after {self.timeout}s"
            log.error(error_msg)
            
            # Record failed request
            if self.usage_tracker:
                self._record_api_usage(False, 0, 0, 0, 0.0, error_msg)
            
            return ProcessingResult(
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            log.error(f"OpenRouter client error: {error_msg}")
            
            # Record failed request
            if self.usage_tracker:
                self._record_api_usage(False, 0, 0, 0, 0.0, error_msg)
            
            return ProcessingResult(
                success=False,
                error=error_msg
            )
    
    def _record_api_usage(self, success: bool, prompt_tokens: int, completion_tokens: int, 
                          total_tokens: int, cost: float, error_message: str = None):
        """Record API usage in the tracker."""
        if not self.usage_tracker:
            return
        
        try:
            record = APIUsageRecord(
                timestamp=time.time(),
                api_provider="openrouter",
                model=self.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost=cost,
                success=success,
                error_message=error_message,
                request_id=f"openrouter_{int(time.time() * 1000)}"
            )
            
            self.usage_tracker.record_request(record)
            
        except Exception as e:
            log.error(f"Failed to record API usage: {e}")
    
    def get_usage_stats(self, days: int = 30):
        """Get usage statistics for OpenRouter API."""
        if not self.usage_tracker:
            return None
        
        try:
            return self.usage_tracker.get_usage_stats("openrouter", days)
        except Exception as e:
            log.error(f"Failed to get usage stats: {e}")
            return None
    
    def get_remaining_requests(self) -> Dict[str, int]:
        """Get remaining requests for daily and monthly limits."""
        if not self.usage_tracker:
            return {"daily": self.daily_limit, "monthly": self.monthly_limit}
        
        try:
            _, _, daily_remaining = self.usage_tracker.check_daily_limit("openrouter", self.daily_limit)
            _, _, monthly_remaining = self.usage_tracker.check_monthly_limit("openrouter", self.monthly_limit)
            
            return {
                "daily": daily_remaining,
                "monthly": monthly_remaining
            }
        except Exception as e:
            log.error(f"Failed to get remaining requests: {e}")
            return {"daily": self.daily_limit, "monthly": self.monthly_limit}
    
    def export_usage_data(self, output_path: str, format: str = "csv"):
        """Export usage data to a file."""
        if not self.usage_tracker:
            log.warning("Usage tracking not enabled")
            return False
        
        try:
            return self.usage_tracker.export_usage_data(output_path, format)
        except Exception as e:
            log.error(f"Failed to export usage data: {e}")
            return False
    
    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ProcessingResult:
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

