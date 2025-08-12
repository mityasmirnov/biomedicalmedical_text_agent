"""
Core configuration management for the Biomedical Data Extraction Engine.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(default="sqlite:///./biomedical_extraction.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    neo4j_uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", env="NEO4J_USER")
    neo4j_password: str = Field(default="password", env="NEO4J_PASSWORD")
    
    model_config = {"env_prefix": "DATABASE_"}

class LLMConfig(BaseSettings):
    """Large Language Model configuration settings."""
    
    openrouter_api_key: str = Field(default="", env="OPENROUTER_API_KEY")
    openrouter_api_base: str = Field(default="https://openrouter.ai/api/v1", env="OPENROUTER_API_BASE")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_api_base: str = Field(default="https://api.openai.com/v1", env="OPENAI_API_BASE")
    huggingface_api_token: str = Field(default="", env="HUGGINGFACE_API_TOKEN")
    
    default_model: str = Field(default="deepseek/deepseek-chat-v3-0324:free", env="DEFAULT_LLM_MODEL")
    temperature: float = Field(default=0.0, env="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2000, env="LLM_MAX_TOKENS")
    timeout: int = Field(default=60, env="LLM_TIMEOUT")
    
    # API Usage Limits and Tracking
    max_requests_per_minute: int = Field(default=60, env="MAX_REQUESTS_PER_MINUTE")
    max_requests_per_day: int = Field(default=1000, env="MAX_REQUESTS_PER_DAY")
    max_requests_per_month: int = Field(default=30000, env="MAX_REQUESTS_PER_MONTH")
    enable_usage_tracking: bool = Field(default=True, env="ENABLE_USAGE_TRACKING")
    usage_database_path: str = Field(default="./data/api_usage.db", env="USAGE_DATABASE_PATH")
    
    # Fallback Model Configuration
    enable_fallback_models: bool = Field(default=True, env="ENABLE_FALLBACK_MODELS")
    fallback_strategy: str = Field(default="ollama,huggingface", env="FALLBACK_STRATEGY")
    
    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_default_model: str = Field(default="llama3.1:8b", env="OLLAMA_DEFAULT_MODEL")
    ollama_timeout: int = Field(default=120, env="OLLAMA_TIMEOUT")
    
    # HuggingFace Configuration
    huggingface_default_model: str = Field(default="microsoft/DialoGPT-medium", env="HUGGINGFACE_DEFAULT_MODEL")
    huggingface_device: str = Field(default="auto", env="HUGGINGFACE_DEVICE")
    huggingface_quantization: bool = Field(default=True, env="HUGGINGFACE_QUANTIZATION")
    
    # No env_prefix to allow direct environment variable names

class VectorDBConfig(BaseSettings):
    """Vector database configuration settings."""
    
    faiss_index_path: str = Field(default="./data/vector_indices", env="FAISS_INDEX_PATH")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    chunk_size: int = Field(default=512, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")
    
    model_config = {"env_prefix": "VECTOR_"}

class ProcessingConfig(BaseSettings):
    """Document processing configuration settings."""
    
    max_document_size: str = Field(default="50MB", env="MAX_DOCUMENT_SIZE")
    supported_formats: List[str] = Field(default=["pdf", "html", "xml", "txt"], env="SUPPORTED_FORMATS")
    enable_ocr: bool = Field(default=False, env="ENABLE_OCR")
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    batch_size: int = Field(default=10, env="BATCH_SIZE")
    
    @field_validator('supported_formats', mode='before')
    @classmethod
    def parse_supported_formats(cls, v):
        if isinstance(v, str):
            return [fmt.strip() for fmt in v.split(',')]
        return v
    
    model_config = {"env_prefix": "PROCESSING_"}

class PathConfig(BaseSettings):
    """File path configuration settings."""
    
    data_dir: Path = Field(default=Path("./data"), env="DATA_DIR")
    schemas_dir: Path = Field(default=Path("./data/schemas"), env="SCHEMAS_DIR")
    ontologies_dir: Path = Field(default=Path("./data/ontologies"), env="ONTOLOGIES_DIR")
    output_dir: Path = Field(default=Path("./data/output"), env="OUTPUT_DIR")
    
    @field_validator('data_dir', 'schemas_dir', 'ontologies_dir', 'output_dir', mode='before')
    @classmethod
    def parse_path(cls, v):
        return Path(v) if isinstance(v, str) else v
    
    model_config = {"env_prefix": "PATH_"}

class SecurityConfig(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    jwt_secret_key: str = Field(default="your-jwt-secret-key-change-in-production", env="JWT_SECRET_KEY")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    model_config = {"env_prefix": "SECURITY_"}

class MonitoringConfig(BaseSettings):
    """Monitoring and logging configuration settings."""
    
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    model_config = {"env_prefix": "MONITORING_"}

class Config(BaseSettings):
    """Main configuration class that combines all configuration sections."""
    
    # Application settings
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Configuration sections
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    vector_db: VectorDBConfig = VectorDBConfig()
    processing: ProcessingConfig = ProcessingConfig()
    paths: PathConfig = PathConfig()
    security: SecurityConfig = SecurityConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.paths.data_dir,
            self.paths.schemas_dir,
            self.paths.ontologies_dir,
            self.paths.output_dir,
            Path(self.vector_db.faiss_index_path),
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_schema_path(self, schema_name: str) -> Path:
        """Get the full path to a schema file."""
        return self.paths.schemas_dir / schema_name
    
    def get_ontology_path(self, ontology_name: str) -> Path:
        """Get the full path to an ontology file."""
        return self.paths.ontologies_dir / ontology_name
    
    def get_output_path(self, filename: str) -> Path:
        """Get the full path to an output file."""
        return self.paths.output_dir / filename
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

# Global configuration instance
config = Config()

def get_config() -> Config:
    """Get the global configuration instance."""
    return config

def reload_config() -> Config:
    """Reload the configuration from environment variables."""
    global config
    config = Config()
    return config

