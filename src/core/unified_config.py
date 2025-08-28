"""
Unified Configuration Manager for Biomedical Text Agent

This module provides a single source of truth for all system configuration,
eliminating fragmentation and ensuring consistency across all components.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(default="sqlite:///./data/database/biomedical_data.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    neo4j_uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", env="NEO4J_USER")
    neo4j_password: str = Field(default="password", env="NEO4J_PASSWORD")
    
    # Database performance settings
    max_connections: int = Field(default=20, env="DB_MAX_CONNECTIONS")
    connection_timeout: int = Field(default=30, env="DB_CONNECTION_TIMEOUT")
    enable_wal: bool = Field(default=True, env="DB_ENABLE_WAL")
    
    model_config = {"env_prefix": "DATABASE_"}

class LLMConfig(BaseSettings):
    """Large Language Model configuration settings."""
    
    # Primary provider
    provider: str = Field(default="openrouter", env="LLM_PROVIDER")
    
    # OpenRouter configuration
    openrouter_api_key: str = Field(default="", env="OPENROUTER_API_KEY")
    openrouter_api_base: str = Field(default="https://openrouter.ai/api/v1", env="OPENROUTER_API_BASE")
    openrouter_default_model: str = Field(default="deepseek/deepseek-chat-v3-0324:free", env="OPENROUTER_DEFAULT_MODEL")
    
    # OpenAI configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_api_base: str = Field(default="https://api.openai.com/v1", env="OPENAI_API_BASE")
    openai_default_model: str = Field(default="gpt-4", env="OPENAI_DEFAULT_MODEL")
    
    # HuggingFace configuration
    huggingface_api_token: str = Field(default="", env="HUGGINGFACE_API_TOKEN")
    huggingface_default_model: str = Field(default="microsoft/DialoGPT-medium", env="HUGGINGFACE_DEFAULT_MODEL")
    
    # Ollama configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_default_model: str = Field(default="llama3.1:8b", env="OLLAMA_DEFAULT_MODEL")
    
    # Common LLM settings
    temperature: float = Field(default=0.0, env="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2000, env="LLM_MAX_TOKENS")
    timeout: int = Field(default=60, env="LLM_TIMEOUT")
    
    # API usage limits
    max_requests_per_minute: int = Field(default=60, env="MAX_REQUESTS_PER_MINUTE")
    max_requests_per_day: int = Field(default=1000, env="MAX_REQUESTS_PER_DAY")
    enable_usage_tracking: bool = Field(default=True, env="ENABLE_USAGE_TRACKING")
    
    # Fallback strategy
    enable_fallback_models: bool = Field(default=True, env="ENABLE_FALLBACK_MODELS")
    fallback_strategy: str = Field(default="openrouter,openai,huggingface,ollama", env="FALLBACK_STRATEGY")
    
    model_config = {"env_prefix": "LLM_"}

class PubMedConfig(BaseSettings):
    """PubMed and Europe PMC configuration."""
    
    pubmed_email: str = Field(default="", env="PUBMED_EMAIL")
    pubmed_api_key: str = Field(default="", env="PUBMED_API_KEY")
    europepmc_email: str = Field(default="", env="EUROPEPMC_EMAIL")
    umls_api_key: str = Field(default="", env="UMLS_API_KEY")
    
    # Rate limiting
    max_requests_per_second: int = Field(default=10, env="PUBMED_MAX_REQUESTS_PER_SECOND")
    request_delay: float = Field(default=0.1, env="PUBMED_REQUEST_DELAY")
    
    model_config = {"env_prefix": "PUBMED_"}

class ProcessingConfig(BaseSettings):
    """Document processing configuration."""
    
    max_document_size: str = Field(default="50MB", env="MAX_DOCUMENT_SIZE")
    supported_formats: List[str] = Field(default=["pdf", "html", "xml", "txt"], env="SUPPORTED_FORMATS")
    enable_ocr: bool = Field(default=False, env="ENABLE_OCR")
    
    # Processing performance
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    batch_size: int = Field(default=10, env="BATCH_SIZE")
    chunk_size: int = Field(default=5000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=500, env="CHUNK_OVERLAP")
    
    # Extraction settings
    extraction_passes: int = Field(default=2, env="EXTRACTION_PASSES")
    use_patient_segmentation: bool = Field(default=True, env="USE_PATIENT_SEGMENTATION")
    confidence_threshold: float = Field(default=0.7, env="CONFIDENCE_THRESHOLD")
    
    @field_validator('supported_formats', mode='before')
    @classmethod
    def parse_supported_formats(cls, v):
        if isinstance(v, str):
            return [fmt.strip() for fmt in v.split(',')]
        return v
    
    model_config = {"env_prefix": "PROCESSING_"}

class VectorDBConfig(BaseSettings):
    """Vector database configuration."""
    
    faiss_index_path: str = Field(default="./data/vector_indices", env="FAISS_INDEX_PATH")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    
    # Vector search settings
    max_results: int = Field(default=100, env="VECTOR_MAX_RESULTS")
    similarity_threshold: float = Field(default=0.7, env="VECTOR_SIMILARITY_THRESHOLD")
    
    model_config = {"env_prefix": "VECTOR_"}

class PathConfig(BaseSettings):
    """File path configuration."""
    
    data_dir: Path = Field(default=Path("./data"), env="DATA_DIR")
    schemas_dir: Path = Field(default=Path("./data/schemas"), env="SCHEMAS_DIR")
    ontologies_dir: Path = Field(default=Path("./data/ontologies"), env="ONTOLOGIES_DIR")
    output_dir: Path = Field(default=Path("./data/output"), env="OUTPUT_DIR")
    logs_dir: Path = Field(default=Path("./logs"), env="LOGS_DIR")
    temp_dir: Path = Field(default=Path("./temp"), env="TEMP_DIR")
    
    @field_validator('data_dir', 'schemas_dir', 'ontologies_dir', 'output_dir', 'logs_dir', 'temp_dir', mode='before')
    @classmethod
    def parse_path(cls, v):
        return Path(v) if isinstance(v, str) else v
    
    model_config = {"env_prefix": "PATH_"}

class SecurityConfig(BaseSettings):
    """Security configuration."""
    
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    jwt_secret_key: str = Field(default="your-jwt-secret-key-change-in-production", env="JWT_SECRET_KEY")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # Authentication
    enable_auth: bool = Field(default=False, env="ENABLE_AUTH")
    session_timeout: int = Field(default=3600, env="SESSION_TIMEOUT")
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    model_config = {"env_prefix": "SECURITY_"}

class MonitoringConfig(BaseSettings):
    """Monitoring and logging configuration."""
    
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Performance monitoring
    enable_performance_tracking: bool = Field(default=True, env="ENABLE_PERFORMANCE_TRACKING")
    performance_sampling_rate: float = Field(default=0.1, env="PERFORMANCE_SAMPLING_RATE")
    
    model_config = {"env_prefix": "MONITORING_"}

class UIConfig(BaseSettings):
    """User interface configuration."""
    
    # Frontend settings
    frontend_port: int = Field(default=3000, env="FRONTEND_PORT")
    backend_port: int = Field(default=8000, env="BACKEND_PORT")
    
    # UI features
    enable_real_time_updates: bool = Field(default=True, env="ENABLE_REAL_TIME_UPDATES")
    enable_websockets: bool = Field(default=True, env="ENABLE_WEBSOCKETS")
    websocket_ping_interval: int = Field(default=30, env="WEBSOCKET_PING_INTERVAL")
    
    # Dashboard settings
    dashboard_refresh_interval: int = Field(default=30, env="DASHBOARD_REFRESH_INTERVAL")
    max_dashboard_items: int = Field(default=100, env="MAX_DASHBOARD_ITEMS")
    
    model_config = {"env_prefix": "UI_"}

class UnifiedConfig(BaseSettings):
    """Main unified configuration class."""
    
    # Application settings
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    version: str = Field(default="2.0.0", env="VERSION")
    
    # Configuration sections
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    pubmed: PubMedConfig = PubMedConfig()
    processing: ProcessingConfig = ProcessingConfig()
    vector_db: VectorDBConfig = VectorDBConfig()
    paths: PathConfig = PathConfig()
    security: SecurityConfig = SecurityConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    ui: UIConfig = UIConfig()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
        self._validate_configuration()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.paths.data_dir,
            self.paths.schemas_dir,
            self.paths.ontologies_dir,
            self.paths.output_dir,
            self.paths.logs_dir,
            self.paths.temp_dir,
            Path(self.vector_db.faiss_index_path),
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _validate_configuration(self):
        """Validate critical configuration settings."""
        # Check API keys
        if not self.llm.openrouter_api_key and not self.llm.openai_api_key:
            print("⚠️  Warning: No LLM API keys configured. Some features may not work.")
        
        if not self.pubmed.pubmed_email:
            print("⚠️  Warning: No PubMed email configured. PubMed API may be rate-limited.")
        
        # Check database
        if not self.database.url:
            print("⚠️  Warning: No database URL configured.")
    
    def get_schema_path(self, schema_name: str) -> Path:
        """Get the full path to a schema file."""
        return self.paths.schemas_dir / schema_name
    
    def get_ontology_path(self, ontology_name: str) -> Path:
        """Get the full path to an ontology file."""
        return self.paths.ontologies_dir / ontology_name
    
    def get_output_path(self, filename: str) -> Path:
        """Get the full path to an output file."""
        return self.paths.output_dir / filename
    
    def get_log_path(self, filename: str) -> Path:
        """Get the full path to a log file."""
        return self.paths.logs_dir / filename
    
    def get_temp_path(self, filename: str) -> Path:
        """Get the full path to a temporary file."""
        return self.paths.temp_dir / filename
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            "version": self.version,
            "environment": self.environment,
            "debug": self.debug,
            "database": self.database.model_dump(),
            "llm": self.llm.model_dump(),
            "pubmed": self.pubmed.model_dump(),
            "processing": self.processing.model_dump(),
            "vector_db": self.vector_db.model_dump(),
            "paths": {k: str(v) for k, v in self.paths.model_dump().items()},
            "security": self.security.model_dump(),
            "monitoring": self.monitoring.model_dump(),
            "ui": self.ui.model_dump(),
        }
    
    def save_to_file(self, filepath: str):
        """Save configuration to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'UnifiedConfig':
        """Load configuration from a JSON file."""
        with open(filepath, 'r') as f:
            config_data = json.load(f)
        return cls(**config_data)
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

# Global configuration instance
config = UnifiedConfig()

def get_config() -> UnifiedConfig:
    """Get the global unified configuration instance."""
    return config

def reload_config() -> UnifiedConfig:
    """Reload the configuration from environment variables."""
    global config
    config = UnifiedConfig()
    return config

def get_llm_config() -> LLMConfig:
    """Get LLM configuration."""
    return config.llm

def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return config.database

def get_processing_config() -> ProcessingConfig:
    """Get processing configuration."""
    return config.processing

def get_ui_config() -> UIConfig:
    """Get UI configuration."""
    return config.ui