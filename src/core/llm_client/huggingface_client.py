"""
HuggingFace Client for Local Model Support

This module provides a client for running HuggingFace models locally,
supporting both CPU and GPU execution. It's compatible with the existing
LLM client interface used by the extraction agents.

Location: src/core/llm_client/huggingface_client.py
"""

import logging
import torch
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import json
import time
from pathlib import Path
import os

try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        pipeline,
        BitsAndBytesConfig
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import accelerate
    ACCELERATE_AVAILABLE = True
except ImportError:
    ACCELERATE_AVAILABLE = False


@dataclass
class HuggingFaceResponse:
    """Response object compatible with OpenRouter client."""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str = "stop"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'model': self.model,
            'usage': self.usage,
            'finish_reason': self.finish_reason
        }


class HuggingFaceClient:
    """
    HuggingFace client for running local models.
    Compatible with the existing LLM client interface.
    """
    
    def __init__(self, 
                 model_name: str = "microsoft/DialoGPT-medium",
                 device: str = "auto",
                 cache_dir: Optional[str] = None,
                 use_quantization: bool = False,
                 max_memory: Optional[Dict[str, str]] = None):
        """
        Initialize HuggingFace client.
        
        Args:
            model_name: Name of the HuggingFace model
            device: Device to use ('cpu', 'cuda', 'auto')
            cache_dir: Directory to cache models
            use_quantization: Whether to use 4-bit quantization
            max_memory: Memory allocation per device
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers library is required for HuggingFace client")
        
        self.model_name = model_name
        self.device = self._determine_device(device)
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/huggingface")
        self.use_quantization = use_quantization
        self.max_memory = max_memory
        
        # Model and tokenizer
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        
        # Model configuration
        self.model_config = {
            'max_length': 2048,
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 50,
            'do_sample': True,
            'pad_token_id': None
        }
        
        # Load model
        self._load_model()
        
        logging.info(f"HuggingFace client initialized with model: {model_name}")
    
    def _determine_device(self, device: str) -> str:
        """Determine the best device to use."""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def _load_model(self):
        """Load the model and tokenizer."""
        try:
            # Configure quantization if requested
            quantization_config = None
            if self.use_quantization and self.device == "cuda":
                try:
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
                    logging.info("Using 4-bit quantization")
                except Exception as e:
                    logging.warning(f"Failed to setup quantization: {e}")
                    quantization_config = None
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                trust_remote_code=True
            )
            
            # Set pad token if not available
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model_config['pad_token_id'] = self.tokenizer.pad_token_id
            
            # Load model
            model_kwargs = {
                'cache_dir': self.cache_dir,
                'trust_remote_code': True,
                'torch_dtype': torch.float16 if self.device == "cuda" else torch.float32
            }
            
            if quantization_config:
                model_kwargs['quantization_config'] = quantization_config
                model_kwargs['device_map'] = "auto"
            elif self.max_memory:
                model_kwargs['device_map'] = "auto"
                model_kwargs['max_memory'] = self.max_memory
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # Move to device if not using device_map
            if 'device_map' not in model_kwargs:
                self.model = self.model.to(self.device)
            
            # Create pipeline for easier generation
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                return_full_text=False
            )
            
            logging.info(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            logging.error(f"Failed to load model {self.model_name}: {e}")
            raise
    
    def generate(self, 
                messages: List[Dict[str, str]], 
                model: Optional[str] = None,
                temperature: float = 0.7,
                max_tokens: int = 1000,
                top_p: float = 0.9,
                **kwargs) -> HuggingFaceResponse:
        """
        Generate response using the loaded model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name (ignored, uses loaded model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            **kwargs: Additional generation parameters
            
        Returns:
            HuggingFaceResponse object
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded")
        
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)
        
        # Update generation config
        generation_config = {
            'max_new_tokens': max_tokens,
            'temperature': temperature,
            'top_p': top_p,
            'do_sample': temperature > 0,
            'pad_token_id': self.model_config['pad_token_id'],
            'eos_token_id': self.tokenizer.eos_token_id,
            'return_full_text': False
        }
        
        # Add any additional kwargs
        generation_config.update(kwargs)
        
        try:
            start_time = time.time()
            
            # Generate response
            if self.pipeline:
                outputs = self.pipeline(
                    prompt,
                    **generation_config
                )
                generated_text = outputs[0]['generated_text']
            else:
                # Fallback to direct model generation
                inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        **generation_config
                    )
                
                # Decode only the new tokens
                generated_tokens = outputs[0][inputs.shape[1]:]
                generated_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
            
            generation_time = time.time() - start_time
            
            # Calculate token usage
            input_tokens = len(self.tokenizer.encode(prompt))
            output_tokens = len(self.tokenizer.encode(generated_text))
            
            # Clean up the generated text
            generated_text = self._clean_generated_text(generated_text)
            
            return HuggingFaceResponse(
                content=generated_text,
                model=self.model_name,
                usage={
                    'prompt_tokens': input_tokens,
                    'completion_tokens': output_tokens,
                    'total_tokens': input_tokens + output_tokens,
                    'generation_time': generation_time
                }
            )
            
        except Exception as e:
            logging.error(f"Generation failed: {e}")
            raise
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to a single prompt string."""
        prompt_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        # Add final assistant prompt
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)
    
    def _clean_generated_text(self, text: str) -> str:
        """Clean up generated text."""
        # Remove common artifacts
        text = text.strip()
        
        # Remove repeated patterns
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and line not in cleaned_lines[-3:]:  # Avoid immediate repetition
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if not self.model:
            return {}
        
        try:
            model_size = sum(p.numel() for p in self.model.parameters())
            model_size_mb = model_size * 4 / (1024 * 1024)  # Approximate size in MB
            
            return {
                'model_name': self.model_name,
                'device': self.device,
                'parameters': model_size,
                'size_mb': model_size_mb,
                'quantized': self.use_quantization,
                'vocab_size': self.tokenizer.vocab_size if self.tokenizer else None,
                'max_position_embeddings': getattr(self.model.config, 'max_position_embeddings', None)
            }
        except Exception as e:
            logging.error(f"Failed to get model info: {e}")
            return {'model_name': self.model_name, 'device': self.device}
    
    def test_generation(self) -> bool:
        """Test if the model can generate text."""
        try:
            test_messages = [
                {"role": "user", "content": "Hello, how are you?"}
            ]
            
            response = self.generate(test_messages, max_tokens=50)
            return len(response.content.strip()) > 0
            
        except Exception as e:
            logging.error(f"Generation test failed: {e}")
            return False
    
    def unload_model(self):
        """Unload the model to free memory."""
        if self.model:
            del self.model
            self.model = None
        
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
        
        # Clear CUDA cache if using GPU
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logging.info("Model unloaded")


class HuggingFaceModelManager:
    """
    Manager for multiple HuggingFace models with automatic loading/unloading.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize model manager.
        
        Args:
            cache_dir: Directory to cache models
        """
        self.cache_dir = cache_dir
        self.loaded_models: Dict[str, HuggingFaceClient] = {}
        self.model_configs = self._get_recommended_models()
    
    def _get_recommended_models(self) -> Dict[str, Dict[str, Any]]:
        """Get recommended model configurations for biomedical tasks."""
        return {
            'mixtral-8x7b': {
                'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
                'use_quantization': True,
                'description': 'Large mixture of experts model, good for complex tasks'
            },
            'llama2-7b': {
                'model_name': 'meta-llama/Llama-2-7b-chat-hf',
                'use_quantization': True,
                'description': 'Llama 2 7B chat model'
            },
            'biobert': {
                'model_name': 'dmis-lab/biobert-base-cased-v1.1',
                'use_quantization': False,
                'description': 'BERT model pre-trained on biomedical text'
            },
            'clinicalbert': {
                'model_name': 'emilyalsentzer/Bio_ClinicalBERT',
                'use_quantization': False,
                'description': 'BERT model for clinical text'
            },
            'scibert': {
                'model_name': 'allenai/scibert_scivocab_uncased',
                'use_quantization': False,
                'description': 'BERT model for scientific text'
            },
            'gpt2-medium': {
                'model_name': 'gpt2-medium',
                'use_quantization': False,
                'description': 'GPT-2 medium model for general text generation'
            }
        }
    
    def load_model(self, 
                  model_key: str, 
                  device: str = "auto",
                  **kwargs) -> HuggingFaceClient:
        """
        Load a model by key.
        
        Args:
            model_key: Key from recommended models or custom model name
            device: Device to use
            **kwargs: Additional arguments for HuggingFaceClient
            
        Returns:
            HuggingFaceClient instance
        """
        if model_key in self.loaded_models:
            return self.loaded_models[model_key]
        
        # Get model configuration
        if model_key in self.model_configs:
            config = self.model_configs[model_key].copy()
            config.update(kwargs)
            model_name = config.pop('model_name')
            description = config.pop('description', '')
        else:
            # Assume model_key is a HuggingFace model name
            model_name = model_key
            config = kwargs
            description = f"Custom model: {model_key}"
        
        logging.info(f"Loading model: {description}")
        
        try:
            client = HuggingFaceClient(
                model_name=model_name,
                device=device,
                cache_dir=self.cache_dir,
                **config
            )
            
            # Test the model
            if client.test_generation():
                self.loaded_models[model_key] = client
                logging.info(f"Model {model_key} loaded successfully")
                return client
            else:
                raise RuntimeError("Model failed generation test")
                
        except Exception as e:
            logging.error(f"Failed to load model {model_key}: {e}")
            raise
    
    def unload_model(self, model_key: str):
        """Unload a specific model."""
        if model_key in self.loaded_models:
            self.loaded_models[model_key].unload_model()
            del self.loaded_models[model_key]
            logging.info(f"Model {model_key} unloaded")
    
    def unload_all_models(self):
        """Unload all models."""
        for model_key in list(self.loaded_models.keys()):
            self.unload_model(model_key)
    
    def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models."""
        return list(self.loaded_models.keys())
    
    def get_available_models(self) -> Dict[str, str]:
        """Get available model configurations."""
        return {
            key: config['description'] 
            for key, config in self.model_configs.items()
        }
    
    def get_model_client(self, model_key: str) -> Optional[HuggingFaceClient]:
        """Get a loaded model client."""
        return self.loaded_models.get(model_key)


# Utility functions for integration

def create_huggingface_client(model_name: str = "gpt2-medium", **kwargs) -> HuggingFaceClient:
    """Create a HuggingFace client with sensible defaults."""
    return HuggingFaceClient(model_name=model_name, **kwargs)


def get_recommended_biomedical_model() -> str:
    """Get the recommended model for biomedical text extraction."""
    # Check available resources and recommend accordingly
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
        if gpu_memory >= 16:
            return 'mixtral-8x7b'
        elif gpu_memory >= 8:
            return 'llama2-7b'
        else:
            return 'gpt2-medium'
    else:
        return 'gpt2-medium'


def test_model_availability(model_name: str) -> bool:
    """Test if a model can be loaded and used."""
    try:
        client = HuggingFaceClient(model_name=model_name)
        result = client.test_generation()
        client.unload_model()
        return result
    except Exception:
        return False

