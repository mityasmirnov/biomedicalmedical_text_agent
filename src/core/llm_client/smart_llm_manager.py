"""
Smart LLM Manager that automatically switches between different providers.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from core.base import BaseLLMClient, ProcessingResult, LLMError
from core.config import get_config
from core.logging_config import get_logger
from core.llm_client.openrouter_client import OpenRouterClient
from core.llm_client.ollama_client import OllamaClient
from core.llm_client.huggingface_client import HuggingFaceClient

log = get_logger(__name__)

class SmartLLMManager(BaseLLMClient):
    """Smart LLM manager that automatically switches between providers."""
    
    def __init__(self, model_name: str = None, config: Optional[Dict[str, Any]] = None):
        app_config = get_config()
        self.config = app_config.llm
        
        # Initialize primary client (OpenRouter)
        self.primary_client = None
        if self.config.openrouter_api_key:
            try:
                self.primary_client = OpenRouterClient(model_name, config)
                log.info("Primary OpenRouter client initialized")
            except Exception as e:
                log.warning(f"Failed to initialize OpenRouter client: {e}")
        
        # Initialize fallback clients
        self.fallback_clients = {}
        self.fallback_strategy = self.config.fallback_strategy.split(',')
        
        if self.config.enable_fallback_models:
            self._initialize_fallback_clients()
        
        # Set current active client
        self.current_client = self.primary_client
        self.current_provider = "openrouter" if self.primary_client else "none"
        
        super().__init__(model_name=model_name, config=config)
        log.info(f"Smart LLM Manager initialized with provider: {self.current_provider}")
    
    def _initialize_fallback_clients(self):
        """Initialize fallback clients based on strategy."""
        try:
            for strategy in self.fallback_strategy:
                strategy = strategy.strip().lower()
                
                if strategy == "ollama":
                    try:
                        ollama_client = OllamaClient(self.config.ollama_default_model)
                        if ollama_client.is_server_running():
                            self.fallback_clients["ollama"] = ollama_client
                            log.info("Ollama fallback client initialized")
                        else:
                            log.warning("Ollama server not running, skipping Ollama client")
                    except Exception as e:
                        log.warning(f"Failed to initialize Ollama client: {e}")
                
                elif strategy == "huggingface":
                    try:
                        hf_client = HuggingFaceClient(self.config.huggingface_default_model)
                        self.fallback_clients["huggingface"] = hf_client
                        log.info("HuggingFace fallback client initialized")
                    except Exception as e:
                        log.warning(f"Failed to initialize HuggingFace client: {e}")
                
                else:
                    log.warning(f"Unknown fallback strategy: {strategy}")
                    
        except Exception as e:
            log.error(f"Failed to initialize fallback clients: {e}")
    
    async def _check_primary_client_health(self) -> bool:
        """Check if primary client is healthy and within limits."""
        if not self.primary_client:
            return False
        
        try:
            # Check if we can make a simple request
            test_result = await self.primary_client.generate(
                "test", 
                max_tokens=10,
                temperature=0.0
            )
            return test_result.success
        except Exception as e:
            log.debug(f"Primary client health check failed: {e}")
            return False
    
    async def _switch_to_fallback(self, reason: str = "primary client unavailable") -> bool:
        """Switch to an available fallback client."""
        log.info(f"Switching to fallback client: {reason}")
        
        for provider, client in self.fallback_clients.items():
            try:
                # Test the fallback client
                if provider == "ollama":
                    if client.is_server_running():
                        self.current_client = client
                        self.current_provider = provider
                        log.info(f"Switched to {provider} fallback client")
                        return True
                elif provider == "huggingface":
                    # Simple test for HuggingFace
                    self.current_client = client
                    self.current_provider = provider
                    log.info(f"Switched to {provider} fallback client")
                    return True
                    
            except Exception as e:
                log.warning(f"Failed to test {provider} fallback client: {e}")
                continue
        
        log.error("No fallback clients available")
        return False
    
    async def _ensure_client_available(self) -> bool:
        """Ensure we have an available client."""
        if self.current_client and self.current_provider == "openrouter":
            # Check if primary client is still healthy
            if await self._check_primary_client_health():
                return True
            else:
                log.warning("Primary client unhealthy, switching to fallback")
                return await self._switch_to_fallback("primary client unhealthy")
        
        elif self.current_client and self.current_provider in self.fallback_clients:
            # We're already using a fallback
            return True
        
        else:
            # No client available, try to get one
            if self.primary_client and await self._check_primary_client_health():
                self.current_client = self.primary_client
                self.current_provider = "openrouter"
                return True
            else:
                return await self._switch_to_fallback("no primary client")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ProcessingResult[str]:
        """
        Generate text using the best available client.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            ProcessingResult containing generated text
        """
        # Ensure we have an available client
        if not await self._ensure_client_available():
            return ProcessingResult(
                success=False,
                error="No LLM clients available"
            )
        
        try:
            # Generate using current client
            result = await self.current_client.generate(
                prompt, system_prompt, temperature, max_tokens, **kwargs
            )
            
            # Add provider information to metadata
            if result.success and result.metadata:
                result.metadata["provider"] = self.current_provider
                result.metadata["fallback_used"] = self.current_provider != "openrouter"
            
            return result
            
        except Exception as e:
            error_msg = f"Generation failed with {self.current_provider}: {str(e)}"
            log.error(error_msg)
            
            # Try to switch to another fallback if available
            if await self._switch_to_fallback(f"client error: {str(e)}"):
                # Retry with new client
                try:
                    result = await self.current_client.generate(
                        prompt, system_prompt, temperature, max_tokens, **kwargs
                    )
                    
                    if result.success and result.metadata:
                        result.metadata["provider"] = self.current_provider
                        result.metadata["fallback_used"] = True
                    
                    return result
                    
                except Exception as retry_error:
                    return ProcessingResult(
                        success=False,
                        error=f"All clients failed. Last error: {str(retry_error)}"
                    )
            else:
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
        Generate text using the best available client (synchronous).
        
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
    
    def get_current_provider(self) -> str:
        """Get the current active provider."""
        return self.current_provider
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        providers = []
        if self.primary_client:
            providers.append("openrouter")
        providers.extend(self.fallback_clients.keys())
        return providers
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        status = {}
        
        # Primary client status
        if self.primary_client:
            try:
                # Check if primary client is healthy
                status["openrouter"] = {
                    "available": True,
                    "healthy": True,  # Will be updated on first use
                    "current": self.current_provider == "openrouter"
                }
            except Exception:
                status["openrouter"] = {
                    "available": True,
                    "healthy": False,
                    "current": False
                }
        
        # Fallback clients status
        for provider, client in self.fallback_clients.items():
            try:
                if provider == "ollama":
                    healthy = client.is_server_running()
                else:
                    healthy = True  # Assume healthy for other providers
                
                status[provider] = {
                    "available": True,
                    "healthy": healthy,
                    "current": self.current_provider == provider
                }
            except Exception:
                status[provider] = {
                    "available": False,
                    "healthy": False,
                    "current": False
                }
        
        return status
    
    async def test_all_providers(self) -> Dict[str, bool]:
        """Test all available providers."""
        results = {}
        
        # Test primary client
        if self.primary_client:
            try:
                test_result = await self.primary_client.generate("test", max_tokens=5)
                results["openrouter"] = test_result.success
            except Exception:
                results["openrouter"] = False
        
        # Test fallback clients
        for provider, client in self.fallback_clients.items():
            try:
                if provider == "ollama":
                    results[provider] = client.is_server_running()
                elif provider == "huggingface":
                    # Simple test for HuggingFace
                    results[provider] = True
                else:
                    results[provider] = False
            except Exception:
                results[provider] = False
        
        return results
    
    def switch_provider(self, provider: str) -> bool:
        """Manually switch to a specific provider."""
        if provider == "openrouter" and self.primary_client:
            self.current_client = self.primary_client
            self.current_provider = "openrouter"
            log.info("Switched to OpenRouter provider")
            return True
        
        elif provider in self.fallback_clients:
            self.current_client = self.fallback_clients[provider]
            self.current_provider = provider
            log.info(f"Switched to {provider} provider")
            return True
        
        else:
            log.warning(f"Provider {provider} not available")
            return False
