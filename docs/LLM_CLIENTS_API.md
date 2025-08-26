# LLM Client APIs - Detailed Reference

## Overview

The Biomedical Data Extraction Engine provides multiple LLM client implementations with automatic fallback capabilities. This document covers all LLM client APIs in detail.

## Table of Contents

1. [Smart LLM Manager](#smart-llm-manager)
2. [OpenRouter Client](#openrouter-client)
3. [Ollama Client](#ollama-client)
4. [HuggingFace Client](#huggingface-client)
5. [Base LLM Client](#base-llm-client)
6. [Usage Examples](#usage-examples)
7. [Configuration](#configuration)
8. [Error Handling](#error-handling)

## Smart LLM Manager

**Location**: `src/core/llm_client/smart_llm_manager.py`

The Smart LLM Manager automatically switches between different LLM providers based on availability, health status, and rate limits.

### Initialization

```python
from core.llm_client.smart_llm_manager import SmartLLMManager

# Basic initialization
llm_manager = SmartLLMManager()

# With specific model
llm_manager = SmartLLMManager(
    model_name="deepseek/deepseek-chat-v3-0324:free"
)

# With custom configuration
llm_manager = SmartLLMManager(
    model_name="gpt-4",
    config={
        "temperature": 0.1,
        "max_tokens": 1000
    }
)
```

### Methods

#### `generate(prompt: str, **kwargs) -> ProcessingResult[str]`

Generates text using the best available LLM provider.

**Parameters:**
- `prompt` (str): Input prompt for text generation
- `**kwargs`: Additional generation parameters (temperature, max_tokens, etc.)

**Returns:**
- `ProcessingResult[str]`: Generated text or error information

**Example:**
```python
result = await llm_manager.generate(
    "Extract patient demographics from this text: [text]",
    temperature=0.0,
    max_tokens=500
)

if result.success:
    generated_text = result.data
    print(f"Generated: {generated_text}")
else:
    print(f"Generation failed: {result.error}")
```

#### `switch_to_fallback(reason: str) -> bool`

Manually switches to a fallback provider.

**Parameters:**
- `reason` (str): Reason for switching to fallback

**Returns:**
- `bool`: True if successfully switched, False otherwise

**Example:**
```python
# Force switch to fallback
success = llm_manager.switch_to_fallback("Manual override")
if success:
    print("Switched to fallback provider")
```

#### `get_current_provider() -> str`

Returns the currently active provider name.

**Returns:**
- `str`: Name of the current provider (e.g., "openrouter", "ollama", "huggingface")

**Example:**
```python
current_provider = llm_manager.get_current_provider()
print(f"Currently using: {current_provider}")
```

#### `get_provider_status() -> Dict[str, Any]`

Returns detailed status of all providers.

**Returns:**
- `Dict[str, Any]`: Status information for all providers

**Example:**
```python
status = llm_manager.get_provider_status()
for provider, info in status.items():
    print(f"{provider}: {info['status']} - {info['health']}")
```

#### `check_provider_health(provider_name: str) -> bool`

Checks the health of a specific provider.

**Parameters:**
- `provider_name` (str): Name of the provider to check

**Returns:**
- `bool`: True if provider is healthy, False otherwise

**Example:**
```python
is_healthy = llm_manager.check_provider_health("openrouter")
if is_healthy:
    print("OpenRouter is healthy")
else:
    print("OpenRouter has issues")
```

### Fallback Strategy

The Smart LLM Manager supports configurable fallback strategies:

```python
# Environment variable configuration
FALLBACK_STRATEGY=ollama,huggingface

# Programmatic configuration
config = Config(
    llm={
        "enable_fallback_models": True,
        "fallback_strategy": "ollama,huggingface"
    }
)
```

**Supported fallback providers:**
- `ollama`: Local Ollama models
- `huggingface`: HuggingFace models
- `openai`: OpenAI models (if configured)

## OpenRouter Client

**Location**: `src/core/llm_client/openrouter_client.py`

Client for OpenRouter API with comprehensive rate limiting and usage tracking.

### Initialization

```python
from core.llm_client.openrouter_client import OpenRouterClient

# Basic initialization (uses environment variables)
client = OpenRouterClient()

# With custom configuration
client = OpenRouterClient(
    model_name="deepseek/deepseek-chat-v3-0324:free",
    api_key="your_api_key",
    api_base="https://openrouter.ai/api/v1"
)

# With rate limiting
client = OpenRouterClient(
    model_name="gpt-4",
    max_requests_per_minute=60,
    max_requests_per_day=1000
)
```

### Methods

#### `generate(prompt: str, **kwargs) -> ProcessingResult[str]`

Generates text using OpenRouter API.

**Parameters:**
- `prompt` (str): Input prompt
- `**kwargs`: Generation parameters (temperature, max_tokens, etc.)

**Returns:**
- `ProcessingResult[str]`: Generated text or error

**Example:**
```python
result = await client.generate(
    "Summarize this medical text: [text]",
    temperature=0.1,
    max_tokens=200,
    model="deepseek/deepseek-chat-v3-0324:free"
)

if result.success:
    summary = result.data
    print(f"Summary: {summary}")
```

#### `get_usage_stats() -> Dict[str, Any]`

Retrieves API usage statistics.

**Returns:**
- `Dict[str, Any]`: Usage statistics including request counts and costs

**Example:**
```python
stats = client.get_usage_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Total cost: ${stats['total_cost']:.4f}")
print(f"Requests today: {stats['requests_today']}")
```

#### `get_available_models() -> ProcessingResult[List[Dict[str, Any]]]`

Retrieves list of available models.

**Returns:**
- `ProcessingResult[List[Dict[str, Any]]]`: List of available models

**Example:**
```python
result = await client.get_available_models()
if result.success:
    models = result.data
    for model in models:
        print(f"{model['id']}: {model['name']} - ${model['pricing']['prompt']}/1K tokens")
```

#### `check_rate_limits() -> Dict[str, Any]`

Checks current rate limit status.

**Returns:**
- `Dict[str, Any]`: Rate limit information

**Example:**
```python
limits = client.check_rate_limits()
print(f"Remaining requests this minute: {limits['remaining_per_minute']}")
print(f"Remaining requests today: {limits['remaining_per_day']}")
```

### Rate Limiting

The OpenRouter client implements sophisticated rate limiting:

```python
# Configure rate limits
client = OpenRouterClient(
    max_requests_per_minute=60,
    max_requests_per_day=1000,
    max_requests_per_month=30000
)

# Check if request is allowed
if client.can_make_request():
    result = await client.generate("prompt")
else:
    print("Rate limit exceeded, please wait")
```

## Ollama Client

**Location**: `src/core/llm_client/ollama_client.py`

Client for local Ollama models with server health monitoring.

### Initialization

```python
from core.llm_client.ollama_client import OllamaClient

# Basic initialization
client = OllamaClient()

# With specific model
client = OllamaClient(
    model_name="llama3.1:8b"
)

# With custom server
client = OllamaClient(
    model_name="llama3.1:8b",
    base_url="http://localhost:11434",
    timeout=120
)
```

### Methods

#### `generate(prompt: str, **kwargs) -> ProcessingResult[str]`

Generates text using local Ollama model.

**Parameters:**
- `prompt` (str): Input prompt
- `**kwargs`: Generation parameters

**Returns:**
- `ProcessingResult[str]`: Generated text or error

**Example:**
```python
result = await client.generate(
    "Extract phenotypes from: [text]",
    temperature=0.0,
    top_p=0.9,
    top_k=40
)

if result.success:
    phenotypes = result.data
    print(f"Extracted phenotypes: {phenotypes}")
```

#### `is_server_running() -> bool`

Checks if Ollama server is accessible.

**Returns:**
- `bool`: True if server is running, False otherwise

**Example:**
```python
if client.is_server_running():
    print("Ollama server is running")
else:
    print("Ollama server is not accessible")
```

#### `get_available_models() -> ProcessingResult[List[str]]`

Retrieves list of available models on the server.

**Returns:**
- `ProcessingResult[List[str]]`: List of available model names

**Example:**
```python
result = await client.get_available_models()
if result.success:
    models = result.data
    print(f"Available models: {', '.join(models)}")
```

#### `pull_model(model_name: str) -> ProcessingResult[bool]`

Downloads a model to the local server.

**Parameters:**
- `model_name` (str): Name of the model to download

**Returns:**
- `ProcessingResult[bool]`: Success status

**Example:**
```python
result = await client.pull_model("llama3.1:8b")
if result.success:
    print("Model downloaded successfully")
else:
    print(f"Failed to download model: {result.error}")
```

#### `get_model_info(model_name: str) -> ProcessingResult[Dict[str, Any]]`

Retrieves information about a specific model.

**Parameters:**
- `model_name` (str): Name of the model

**Returns:**
- `ProcessingResult[Dict[str, Any]]`: Model information

**Example:**
```python
result = await client.get_model_info("llama3.1:8b")
if result.success:
    info = result.data
    print(f"Model size: {info['size']}")
    print(f"Modified: {info['modified_at']}")
```

### Server Management

```python
# Check server status
if not client.is_server_running():
    print("Starting Ollama server...")
    # Start server process
    
# Monitor server health
health_status = await client.check_server_health()
print(f"Server health: {health_status}")
```

## HuggingFace Client

**Location**: `src/core/llm_client/huggingface_client.py`

Client for HuggingFace models with quantization and device optimization.

### Initialization

```python
from core.llm_client.huggingface_client import HuggingFaceClient

# Basic initialization
client = HuggingFaceClient()

# With specific model
client = HuggingFaceClient(
    model_name="microsoft/DialoGPT-medium"
)

# With advanced configuration
client = HuggingFaceClient(
    model_name="microsoft/DialoGPT-medium",
    device="cuda",  # or "cpu", "auto"
    quantization=True,
    load_in_8bit=True,
    load_in_4bit=False
)
```

### Methods

#### `generate(prompt: str, **kwargs) -> ProcessingResult[str]`

Generates text using HuggingFace model.

**Parameters:**
- `prompt` (str): Input prompt
- `**kwargs`: Generation parameters

**Returns:**
- `ProcessingResult[str]`: Generated text or error

**Example:**
```python
result = await client.generate(
    "Generate a medical summary: [text]",
    max_length=100,
    do_sample=True,
    temperature=0.7,
    top_p=0.9
)

if result.success:
    summary = result.data
    print(f"Generated summary: {summary}")
```

#### `load_model(model_name: str) -> bool`

Loads a specific model into memory.

**Parameters:**
- `model_name` (str): Name of the model to load

**Returns:**
- `bool`: True if model loaded successfully, False otherwise

**Example:**
```python
success = client.load_model("microsoft/DialoGPT-medium")
if success:
    print("Model loaded successfully")
else:
    print("Failed to load model")
```

#### `get_model_info() -> Dict[str, Any]`

Retrieves information about the loaded model.

**Returns:**
- `Dict[str, Any]`: Model information

**Example:**
```python
info = client.get_model_info()
print(f"Model: {info['model_name']}")
print(f"Device: {info['device']}")
print(f"Quantization: {info['quantization']}")
```

#### `switch_model(model_name: str) -> ProcessingResult[bool]`

Switches to a different model.

**Parameters:**
- `model_name` (str): Name of the new model

**Returns:**
- `ProcessingResult[bool]`: Success status

**Example:**
```python
result = await client.switch_model("gpt2")
if result.success:
    print("Switched to GPT-2 model")
else:
    print(f"Failed to switch model: {result.error}")
```

### Model Management

```python
# Initialize model manager
from core.llm_client.huggingface_client import HuggingFaceModelManager

model_manager = HuggingFaceModelManager()

# List available models
models = model_manager.list_available_models()
print(f"Available models: {models}")

# Download model
success = await model_manager.download_model("microsoft/DialoGPT-medium")
if success:
    print("Model downloaded")
```

## Base LLM Client

**Location**: `src/core/base.py`

Abstract base class that all LLM clients inherit from.

### Abstract Methods

#### `generate(prompt: str, **kwargs) -> ProcessingResult[str]`

**Abstract method** that must be implemented by all LLM clients.

**Parameters:**
- `prompt` (str): Input prompt
- `**kwargs`: Generation parameters

**Returns:**
- `ProcessingResult[str]`: Generated text or error

#### `get_model_info() -> Dict[str, Any]`

**Abstract method** that returns model information.

**Returns:**
- `Dict[str, Any]`: Model metadata

### Common Properties

```python
class BaseLLMClient(ABC):
    model_name: str
    provider: str
    is_available: bool
    last_used: Optional[datetime]
    total_requests: int
    total_tokens: int
```

## Usage Examples

### Basic Text Generation

```python
import asyncio
from core.llm_client.smart_llm_manager import SmartLLMManager

async def generate_text():
    llm = SmartLLMManager()
    
    prompt = "Extract the following information from this medical text: age, sex, symptoms"
    
    result = await llm.generate(prompt)
    
    if result.success:
        print(f"Generated: {result.data}")
    else:
        print(f"Error: {result.error}")

asyncio.run(generate_text())
```

### Batch Processing with Multiple Providers

```python
import asyncio
from core.llm_client.smart_llm_manager import SmartLLMManager

async def batch_generate():
    llm = SmartLLMManager()
    
    prompts = [
        "Extract patient demographics",
        "Extract genetic information",
        "Extract treatment details"
    ]
    
    results = []
    for prompt in prompts:
        result = await llm.generate(prompt)
        results.append(result)
        
        # Check if we need to switch providers
        if not result.success and "rate limit" in result.error.lower():
            llm.switch_to_fallback("Rate limit exceeded")
    
    return results

asyncio.run(batch_generate())
```

### Custom Provider Configuration

```python
from core.llm_client.openrouter_client import OpenRouterClient
from core.llm_client.ollama_client import OllamaClient

# Configure primary provider
primary_client = OpenRouterClient(
    model_name="deepseek/deepseek-chat-v3-0324:free",
    max_requests_per_minute=30
)

# Configure fallback
fallback_client = OllamaClient(
    model_name="llama3.1:8b"
)

# Use in sequence
async def generate_with_fallback(prompt):
    try:
        result = await primary_client.generate(prompt)
        if result.success:
            return result
    except Exception as e:
        print(f"Primary client failed: {e}")
    
    # Try fallback
    try:
        result = await fallback_client.generate(prompt)
        return result
    except Exception as e:
        return ProcessingResult(
            success=False,
            error=f"All providers failed: {e}"
        )
```

### Health Monitoring

```python
import asyncio
from core.llm_client.smart_llm_manager import SmartLLMManager

async def monitor_health():
    llm = SmartLLMManager()
    
    while True:
        # Check current provider health
        current_provider = llm.get_current_provider()
        is_healthy = llm.check_provider_health(current_provider)
        
        if not is_healthy:
            print(f"Provider {current_provider} is unhealthy, switching...")
            llm.switch_to_fallback("Health check failed")
        
        # Get overall status
        status = llm.get_provider_status()
        print(f"Provider status: {status}")
        
        await asyncio.sleep(60)  # Check every minute

# Run health monitoring
asyncio.run(monitor_health())
```

## Configuration

### Environment Variables

```bash
# LLM Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_TOKEN=your_huggingface_token

# Model Configuration
DEFAULT_LLM_MODEL=deepseek/deepseek-chat-v3-0324:free
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=2000
LLM_TIMEOUT=60

# Fallback Configuration
ENABLE_FALLBACK_MODELS=True
FALLBACK_STRATEGY=ollama,huggingface

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.1:8b
OLLAMA_TIMEOUT=120

# HuggingFace Configuration
HUGGINGFACE_DEFAULT_MODEL=microsoft/DialoGPT-medium
HUGGINGFACE_DEVICE=auto
HUGGINGFACE_QUANTIZATION=True

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
MAX_REQUESTS_PER_DAY=1000
MAX_REQUESTS_PER_MONTH=30000
```

### Programmatic Configuration

```python
from core.config import Config

config = Config(
    llm={
        "default_model": "deepseek/deepseek-chat-v3-0324:free",
        "temperature": 0.0,
        "max_tokens": 2000,
        "enable_fallback_models": True,
        "fallback_strategy": "ollama,huggingface",
        "max_requests_per_minute": 60
    }
)

# Use with Smart LLM Manager
llm_manager = SmartLLMManager(config=config)
```

## Error Handling

### Common Error Types

#### Rate Limit Errors

```python
try:
    result = await client.generate("prompt")
except Exception as e:
    if "rate limit" in str(e).lower():
        print("Rate limit exceeded, waiting...")
        await asyncio.sleep(60)
        # Retry or switch provider
    else:
        raise
```

#### Model Loading Errors

```python
try:
    success = client.load_model("model_name")
    if not success:
        print("Failed to load model, trying fallback...")
        # Switch to different model or provider
except Exception as e:
    print(f"Model loading error: {e}")
```

#### Network Errors

```python
try:
    result = await client.generate("prompt")
except Exception as e:
    if "connection" in str(e).lower() or "timeout" in str(e).lower():
        print("Network error, switching to local provider...")
        # Switch to Ollama or other local provider
    else:
        raise
```

### Error Recovery Strategies

```python
class ResilientLLMClient:
    def __init__(self, primary_client, fallback_clients):
        self.primary_client = primary_client
        self.fallback_clients = fallback_clients
        self.current_client = primary_client
    
    async def generate_with_recovery(self, prompt, max_retries=3):
        for attempt in range(max_retries):
            try:
                result = await self.current_client.generate(prompt)
                if result.success:
                    return result
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Try to switch to fallback
                    if self._switch_to_fallback():
                        continue
                
                return ProcessingResult(
                    success=False,
                    error=f"All attempts failed: {e}"
                )
        
        return ProcessingResult(
            success=False,
            error="Max retries exceeded"
        )
    
    def _switch_to_fallback(self):
        for fallback in self.fallback_clients:
            if fallback.is_available:
                self.current_client = fallback
                return True
        return False
```

## Performance Optimization

### Model Caching

```python
class CachedLLMClient:
    def __init__(self, client, cache_size=100):
        self.client = client
        self.cache = {}
        self.cache_size = cache_size
    
    async def generate(self, prompt, **kwargs):
        # Create cache key
        cache_key = self._create_cache_key(prompt, kwargs)
        
        # Check cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Generate and cache
        result = await self.client.generate(prompt, **kwargs)
        self._add_to_cache(cache_key, result)
        
        return result
    
    def _create_cache_key(self, prompt, kwargs):
        # Create deterministic cache key
        import hashlib
        key_data = f"{prompt}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _add_to_cache(self, key, result):
        if len(self.cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = result
```

### Batch Processing

```python
async def batch_generate(client, prompts, batch_size=10):
    results = []
    
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        
        # Process batch concurrently
        batch_tasks = [
            client.generate(prompt) for prompt in batch
        ]
        
        batch_results = await asyncio.gather(*batch_tasks)
        results.extend(batch_results)
        
        # Small delay between batches to avoid overwhelming
        await asyncio.sleep(0.1)
    
    return results
```

## Monitoring and Metrics

### Usage Tracking

```python
class LLMMetrics:
    def __init__(self):
        self.request_count = 0
        self.token_count = 0
        self.error_count = 0
        self.response_times = []
    
    def record_request(self, tokens_used, response_time, success):
        self.request_count += 1
        self.token_count += tokens_used
        self.response_times.append(response_time)
        
        if not success:
            self.error_count += 1
    
    def get_statistics(self):
        if not self.response_times:
            return {}
        
        return {
            "total_requests": self.request_count,
            "total_tokens": self.token_count,
            "error_rate": self.error_count / self.request_count,
            "avg_response_time": sum(self.response_times) / len(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times)
        }

# Usage
metrics = LLMMetrics()

async def generate_with_metrics(client, prompt):
    start_time = time.time()
    
    try:
        result = await client.generate(prompt)
        response_time = time.time() - start_time
        
        metrics.record_request(
            tokens_used=len(prompt.split()),
            response_time=response_time,
            success=result.success
        )
        
        return result
    except Exception as e:
        response_time = time.time() - start_time
        metrics.record_request(
            tokens_used=len(prompt.split()),
            response_time=response_time,
            success=False
        )
        raise
```

This comprehensive documentation covers all LLM client APIs with detailed examples, configuration options, and best practices for optimal usage.