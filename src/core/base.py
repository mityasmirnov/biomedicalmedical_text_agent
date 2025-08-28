"""
Base classes and interfaces for the Biomedical Data Extraction Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid

# Type variables for generic classes
T = TypeVar('T')
InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')

class ProcessingStatus(Enum):
    """Status enumeration for processing tasks."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DocumentFormat(Enum):
    """Supported document formats."""
    PDF = "pdf"
    HTML = "html"
    XML = "xml"
    TXT = "txt"
    DOCX = "docx"
    JSON = "json"

class ExtractionType(Enum):
    """Types of extraction tasks."""
    DEMOGRAPHICS = "demographics"
    GENETICS = "genetics"
    PHENOTYPES = "phenotypes"
    TREATMENTS = "treatments"
    OUTCOMES = "outcomes"
    LAB_VALUES = "lab_values"
    IMAGING = "imaging"
    FULL_RECORD = "full_record"

@dataclass
class ProcessingResult(Generic[T]):
    """Generic result container for processing operations."""
    
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: Optional[float] = None
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata."""
        self.metadata[key] = value

@dataclass
class Document:
    """Document representation."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = None
    content: str = ""
    format: DocumentFormat = DocumentFormat.TXT
    source_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        self.metadata[key] = value

@dataclass
class PatientRecord:
    """Patient record representation."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    pmid: Optional[int] = None
    source_document_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)
    validation_status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def get_field(self, field_name: str, default: Any = None) -> Any:
        """Get a data field value."""
        return self.data.get(field_name, default)
    
    def set_field(self, field_name: str, value: Any, confidence: Optional[float] = None) -> None:
        """Set a data field value with optional confidence score."""
        self.data[field_name] = value
        if confidence is not None:
            self.confidence_scores[field_name] = confidence
        self.updated_at = datetime.now(timezone.utc)
    
    def get_confidence(self, field_name: str) -> Optional[float]:
        """Get confidence score for a field."""
        return self.confidence_scores.get(field_name)

class BaseProcessor(ABC, Generic[InputType, OutputType]):
    """Base class for all processors."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self._setup()
    
    def _setup(self) -> None:
        """Setup the processor. Override in subclasses."""
        pass
    
    @abstractmethod
    def process(self, input_data: InputType) -> ProcessingResult[OutputType]:
        """Process input data and return result."""
        pass
    
    def validate_input(self, input_data: InputType) -> bool:
        """Validate input data. Override in subclasses."""
        return True
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

class BaseExtractor(BaseProcessor[Document, Dict[str, Any]]):
    """Base class for data extractors."""
    
    def __init__(self, extraction_type: ExtractionType, **kwargs):
        self.extraction_type = extraction_type
        super().__init__(name=f"{extraction_type.value}_extractor", **kwargs)
    
    @abstractmethod
    def extract(self, document: Document) -> ProcessingResult[Dict[str, Any]]:
        """Extract data from document."""
        pass
    
    def process(self, input_data: Document) -> ProcessingResult[Dict[str, Any]]:
        """Process document by extracting data."""
        return self.extract(input_data)

class BaseNormalizer(BaseProcessor[Dict[str, Any], Dict[str, Any]]):
    """Base class for data normalizers."""
    
    @abstractmethod
    def normalize(self, data: Dict[str, Any]) -> ProcessingResult[Dict[str, Any]]:
        """Normalize extracted data."""
        pass
    
    def process(self, input_data: Dict[str, Any]) -> ProcessingResult[Dict[str, Any]]:
        """Process data by normalizing it."""
        return self.normalize(input_data)

class BaseValidator(BaseProcessor[Dict[str, Any], bool]):
    """Base class for data validators."""
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> ProcessingResult[bool]:
        """Validate data."""
        pass
    
    def process(self, input_data: Dict[str, Any]) -> ProcessingResult[bool]:
        """Process data by validating it."""
        return self.validate(input_data)

class BaseLLMClient(ABC):
    """Base class for LLM clients."""
    
    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.config = config or {}
        self._setup()
    
    def _setup(self) -> None:
        """Setup the LLM client. Override in subclasses."""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ProcessingResult[str]:
        """Generate text using the LLM."""
        pass
    
    @abstractmethod
    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ProcessingResult[str]:
        """Generate text using the LLM (synchronous)."""
        pass

class BaseAgent(ABC):
    """Base class for AI agents."""
    
    def __init__(self, name: str, llm_client: BaseLLMClient, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.llm_client = llm_client
        self.config = config or {}
        self._setup()
    
    def _setup(self) -> None:
        """Setup the agent. Override in subclasses."""
        pass
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> ProcessingResult[Any]:
        """Execute a task."""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

class BaseDatabase(ABC):
    """Base class for database connections."""
    
    def __init__(self, connection_string: str, config: Optional[Dict[str, Any]] = None):
        self.connection_string = connection_string
        self.config = config or {}
        self._connection = None
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the database."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check database health."""
        pass
    
    def is_connected(self) -> bool:
        """Check if connected to database."""
        return self._connection is not None

class BaseVectorStore(ABC):
    """Base class for vector stores."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._setup()
    
    def _setup(self) -> None:
        """Setup the vector store. Override in subclasses."""
        pass
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> ProcessingResult[List[str]]:
        """Add documents to the vector store."""
        pass
    
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> ProcessingResult[List[Dict[str, Any]]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    async def delete_documents(self, document_ids: List[str]) -> ProcessingResult[bool]:
        """Delete documents from the vector store."""
        pass

# Exception classes
class ExtractionError(Exception):
    """Base exception for extraction errors."""
    pass

class ValidationError(Exception):
    """Exception for validation errors."""
    pass

class ConfigurationError(Exception):
    """Exception for configuration errors."""
    pass

class DatabaseError(Exception):
    """Exception for database errors."""
    pass

class LLMError(Exception):
    """Exception for LLM-related errors."""
    pass

