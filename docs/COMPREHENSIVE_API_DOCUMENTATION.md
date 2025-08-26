# Comprehensive API Documentation

## Biomedical Data Extraction Engine - Complete API Reference

This document provides comprehensive documentation for all public APIs, functions, and components in the Biomedical Data Extraction Engine. It covers the core extraction system, database management, LLM clients, agents, and web interfaces.

## Table of Contents

1. [Core System APIs](#core-system-apis)
2. [LLM Client APIs](#llm-client-apis)
3. [Extraction Agent APIs](#extraction-agent-apis)
4. [Database Management APIs](#database-management-apis)
5. [Ontology Management APIs](#ontology-management-apis)
6. [RAG System APIs](#rag-system-apis)
7. [Web API Endpoints](#web-api-endpoints)
8. [CLI Interface](#cli-interface)
9. [Data Models](#data-models)
10. [Configuration](#configuration)
11. [Error Handling](#error-handling)
12. [Examples and Usage](#examples-and-usage)

## Core System APIs

### ExtractionOrchestrator

The main orchestrator that coordinates document processing and data extraction.

**Location**: `src/agents/orchestrator/extraction_orchestrator.py`

```python
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator

# Initialize orchestrator
orchestrator = ExtractionOrchestrator(
    llm_client=llm_client,
    use_demographics=True,
    use_genetics=True,
    use_phenotypes=True,
    use_treatments=True
)
```

#### Methods

##### `extract_from_file(file_path: str) -> ProcessingResult[List[PatientRecord]]`

Extracts patient records from a single document file.

**Parameters:**
- `file_path` (str): Absolute path to the document file

**Returns:**
- `ProcessingResult[List[PatientRecord]]`: Result containing extracted patient records

**Example:**
```python
result = await orchestrator.extract_from_file("/path/to/document.pdf")
if result.success:
    records = result.data
    print(f"Extracted {len(records)} patient records")
```

##### `extract_batch(file_paths: List[str]) -> ProcessingResult[List[PatientRecord]]`

Extracts patient records from multiple document files.

**Parameters:**
- `file_paths` (List[str]): List of absolute paths to document files

**Returns:**
- `ProcessingResult[List[PatientRecord]]`: Result containing all extracted patient records

##### `split_patients(text: str) -> List[Tuple[str, str]]`

Splits article text into patient sections.

**Parameters:**
- `text` (str): Raw article text

**Returns:**
- `List[Tuple[str, str]]`: List of (patient_label, section_text) tuples

### Enhanced Extraction Orchestrator

**Location**: `src/agents/orchestrator/enhanced_orchestrator.py`

Advanced orchestrator with additional features for complex extraction workflows.

```python
from agents.orchestrator.enhanced_orchestrator import EnhancedExtractionOrchestrator

orchestrator = EnhancedExtractionOrchestrator(
    config=config,
    llm_client=llm_client
)
```

#### Methods

##### `process_document(document: Document) -> ProcessingResult[List[PatientRecord]]`

Processes a document through the complete extraction pipeline.

##### `process_batch(documents: List[Document]) -> ProcessingResult[List[PatientRecord]]`

Processes multiple documents in batch.

##### `validate_extractions(records: List[PatientRecord]) -> ProcessingResult[List[PatientRecord]]`

Validates extracted records against schemas and ontologies.

## LLM Client APIs

### Smart LLM Manager

**Location**: `src/core/llm_client/smart_llm_manager.py`

Automatically manages multiple LLM providers with fallback capabilities.

```python
from core.llm_client.smart_llm_manager import SmartLLMManager

# Initialize with automatic fallback
llm_manager = SmartLLMManager(
    model_name="deepseek/deepseek-chat-v3-0324:free"
)
```

#### Methods

##### `generate(prompt: str, **kwargs) -> ProcessingResult[str]`

Generates text using the best available LLM provider.

**Parameters:**
- `prompt` (str): Input prompt
- `**kwargs`: Additional generation parameters

**Returns:**
- `ProcessingResult[str]`: Generated text or error

##### `switch_to_fallback(reason: str) -> bool`

Manually switches to a fallback provider.

##### `get_current_provider() -> str`

Returns the currently active provider name.

### OpenRouter Client

**Location**: `src/core/llm_client/openrouter_client.py`

Client for OpenRouter API with rate limiting and usage tracking.

```python
from core.llm_client.openrouter_client import OpenRouterClient

client = OpenRouterClient(
    model_name="deepseek/deepseek-chat-v3-0324:free",
    api_key="your_api_key"
)
```

#### Methods

##### `generate(prompt: str, **kwargs) -> ProcessingResult[str]`

Generates text using OpenRouter API.

##### `get_usage_stats() -> Dict[str, Any]`

Retrieves API usage statistics.

### Ollama Client

**Location**: `src/core/llm_client/ollama_client.py`

Client for local Ollama models.

```python
from core.llm_client.ollama_client import OllamaClient

client = OllamaClient(
    model_name="llama3.1:8b",
    base_url="http://localhost:11434"
)
```

#### Methods

##### `generate(prompt: str, **kwargs) -> ProcessingResult[str]`

Generates text using local Ollama model.

##### `is_server_running() -> bool`

Checks if Ollama server is accessible.

### HuggingFace Client

**Location**: `src/core/llm_client/huggingface_client.py`

Client for HuggingFace models with quantization support.

```python
from core.llm_client.huggingface_client import HuggingFaceClient

client = HuggingFaceClient(
    model_name="microsoft/DialoGPT-medium",
    device="auto",
    quantization=True
)
```

#### Methods

##### `generate(prompt: str, **kwargs) -> ProcessingResult[str]`

Generates text using HuggingFace model.

##### `load_model(model_name: str) -> bool`

Loads a specific model into memory.

## Extraction Agent APIs

### Phenotypes Agent

**Location**: `src/agents/extraction_agents/phenotypes_agent.py`

Extracts phenotypic information with HPO integration.

```python
from agents.extraction_agents.phenotypes_agent import PhenotypesAgent

agent = PhenotypesAgent(
    llm_client=llm_client,
    hpo_manager=hpo_manager,
    use_optimized_hpo=True
)
```

#### Methods

##### `extract_phenotypes(text: str) -> ProcessingResult[PhenotypeExtraction]`

Extracts phenotype information from text.

**Parameters:**
- `text` (str): Input text to analyze

**Returns:**
- `ProcessingResult[PhenotypeExtraction]`: Extracted phenotype data

##### `normalize_phenotypes(phenotypes: List[str]) -> ProcessingResult[List[Dict[str, Any]]]`

Normalizes phenotypes to HPO terms.

##### `get_extraction_statistics() -> Dict[str, Any]`

Returns extraction performance statistics.

### Genetics Agent

**Location**: `src/agents/extraction_agents/genetics_agent.py`

Extracts genetic information and mutations.

```python
from agents.extraction_agents.genetics_agent import GeneticsAgent

agent = GeneticsAgent(llm_client=llm_client)
```

#### Methods

##### `extract_genetics(text: str) -> ProcessingResult[Dict[str, Any]]`

Extracts genetic information from text.

##### `normalize_gene_symbols(genes: List[str]) -> ProcessingResult[List[Dict[str, Any]]]`

Normalizes gene symbols to HGNC standards.

### Treatments Agent

**Location**: `src/agents/extraction_agents/treatments_agent.py`

Extracts treatment and medication information.

```python
from agents.extraction_agents.treatments_agent import TreatmentsAgent

agent = TreatmentsAgent(llm_client=llm_client)
```

#### Methods

##### `extract_treatments(text: str) -> ProcessingResult[Dict[str, Any]]`

Extracts treatment information from text.

##### `categorize_treatments(treatments: List[str]) -> ProcessingResult[Dict[str, List[str]]]`

Categorizes treatments by type.

### Demographics Agent

**Location**: `src/agents/extraction_agents/demographics_agent.py`

Extracts demographic information.

```python
from agents.extraction_agents.demographics_agent import DemographicsAgent

agent = DemographicsAgent(llm_client=llm_client)
```

#### Methods

##### `extract_demographics(text: str) -> ProcessingResult[Dict[str, Any]]`

Extracts demographic information from text.

## Database Management APIs

### SQLite Manager

**Location**: `src/database/sqlite_manager.py`

Manages SQLite database operations for patient records.

```python
from database.sqlite_manager import SQLiteManager

db_manager = SQLiteManager(db_path="data/database/biomedical_data.db")
```

#### Methods

##### `store_patient_records(records: List[PatientRecord]) -> ProcessingResult[List[str]]`

Stores patient records in the database.

##### `get_patient_records(pmid: Optional[int] = None, gene: Optional[str] = None, limit: int = 100) -> ProcessingResult[List[Dict[str, Any]]]`

Retrieves patient records with optional filtering.

##### `search_records(query: str, limit: int = 50) -> ProcessingResult[List[Dict[str, Any]]]`

Performs full-text search across patient records.

##### `export_to_csv(output_path: str) -> ProcessingResult[str]`

Exports all patient records to CSV format.

##### `get_statistics() -> ProcessingResult[Dict[str, Any]]`

Returns database statistics and metrics.

### Vector Manager

**Location**: `src/database/vector_manager.py`

Manages vector embeddings and semantic search.

```python
from database.vector_manager import VectorManager

vector_manager = VectorManager(index_path="data/vector_indices")
```

#### Methods

##### `add_documents(documents: List[Document]) -> ProcessingResult[int]`

Adds documents to the vector index.

##### `search(query: str, top_k: int = 10) -> ProcessingResult[List[Dict[str, Any]]]`

Performs semantic search.

##### `update_embeddings() -> ProcessingResult[bool]`

Updates document embeddings.

## Ontology Management APIs

### HPO Manager

**Location**: `src/ontologies/hpo_manager.py`

Manages Human Phenotype Ontology operations.

```python
from ontologies.hpo_manager import HPOManager

hpo_manager = HPOManager()
```

#### Methods

##### `normalize_phenotype(phenotype_text: str) -> ProcessingResult[Dict[str, Any]]`

Normalizes phenotype text to HPO terms.

##### `batch_normalize_phenotypes(phenotype_list: List[str]) -> ProcessingResult[List[Dict[str, Any]]]`

Normalizes multiple phenotypes at once.

##### `search_terms(query: str, limit: int = 10) -> ProcessingResult[List[Dict[str, Any]]]`

Searches HPO terms by query.

### Optimized HPO Manager

**Location**: `src/ontologies/hpo_manager_optimized.py`

Enhanced HPO manager with improved performance.

```python
from ontologies.hpo_manager_optimized import OptimizedHPOManager

hpo_manager = OptimizedHPOManager(hpo_path="data/ontologies/hp.json")
```

#### Methods

##### `get_phenotype_hierarchy(phenotype_id: str) -> ProcessingResult[Dict[str, Any]]`

Retrieves phenotype hierarchy information.

##### `get_related_phenotypes(phenotype_id: str) -> ProcessingResult[List[Dict[str, Any]]]`

Finds related phenotypes.

### Gene Manager

**Location**: `src/ontologies/gene_manager.py`

Manages gene symbol normalization and HGNC integration.

```python
from ontologies.gene_manager import GeneManager

gene_manager = GeneManager()
```

#### Methods

##### `normalize_gene_symbol(gene_symbol: str) -> ProcessingResult[Dict[str, Any]]`

Normalizes gene symbol to official HGNC symbol.

##### `batch_normalize_genes(gene_list: List[str]) -> ProcessingResult[List[Dict[str, Any]]]`

Normalizes multiple gene symbols at once.

##### `get_gene_info(gene_symbol: str) -> ProcessingResult[Dict[str, Any]]`

Retrieves comprehensive gene information.

## RAG System APIs

### RAG System

**Location**: `src/rag/rag_system.py`

Retrieval-augmented generation system for question answering.

```python
from rag.rag_system import RAGSystem

rag_system = RAGSystem(
    vector_manager=vector_manager,
    sqlite_manager=sqlite_manager,
    llm_client=llm_client
)
```

#### Methods

##### `answer_question(question: str, max_context_docs: int = 5, include_patient_records: bool = True) -> ProcessingResult[Dict[str, Any]]`

Answers questions using RAG.

**Parameters:**
- `question` (str): Natural language question
- `max_context_docs` (int): Maximum documents to retrieve
- `include_patient_records` (bool): Whether to include patient data

**Returns:**
- `ProcessingResult[Dict[str, Any]]`: Answer with sources and context

##### `add_documents_to_index(documents: List[Document]) -> ProcessingResult[int]`

Adds documents to the RAG index.

##### `get_context_for_question(question: str, top_k: int = 5) -> ProcessingResult[List[Dict[str, Any]]]`

Retrieves relevant context for a question.

### RAG Integration

**Location**: `src/rag/rag_integration.py`

Advanced RAG integration with multiple data sources.

```python
from rag.rag_integration import RAGIntegration

rag_integration = RAGIntegration(
    config=config,
    llm_client=llm_client
)
```

#### Methods

##### `integrate_knowledge_sources() -> ProcessingResult[bool]`

Integrates multiple knowledge sources.

##### `generate_comprehensive_answer(question: str) -> ProcessingResult[Dict[str, Any]]`

Generates comprehensive answers using multiple sources.

## Web API Endpoints

### FastAPI Backend

**Location**: `src/ui/backend/app.py`

Main web application with REST API endpoints.

```python
from src.ui.backend.app import create_app

app = create_app()
```

#### Health Endpoint

```
GET /api/health
```

Returns system health status.

#### Dashboard Endpoints

**Location**: `src/ui/backend/api/dashboard.py`

```
GET /api/v1/dashboard/overview
GET /api/v1/dashboard/statistics
GET /api/v1/dashboard/recent-activities
GET /api/v1/dashboard/alerts
GET /api/v1/dashboard/metrics
GET /api/v1/dashboard/system-status
```

#### Authentication Endpoints

**Location**: `src/ui/backend/auth.py`

```
POST /api/v1/auth/token
POST /api/v1/auth/register
POST /api/v1/auth/logout
POST /api/v1/auth/verify
POST /api/v1/auth/refresh
```

#### WebSocket Endpoint

```
WS /api/v1/ws
```

Real-time communication for live updates.

## CLI Interface

### Main CLI

**Location**: `src/main.py`

Command-line interface for the extraction engine.

```bash
# Extract from single file
python src/main.py extract document.pdf

# Extract with validation
python src/main.py extract document.pdf --validate --ground-truth truth.json

# Extract with custom output format
python src/main.py extract document.pdf --format csv --output results.csv
```

#### Commands

##### `extract`

Extracts patient data from medical documents.

**Options:**
- `--output, -o`: Output file path
- `--format`: Output format (json, csv, table)
- `--validate`: Enable validation
- `--ground-truth`: Ground truth file for validation

##### `batch`

Processes multiple documents in batch.

##### `query`

Queries the knowledge base.

##### `validate`

Validates extracted data against schemas.

## Data Models

### Core Data Classes

**Location**: `src/core/base.py`

#### ProcessingResult

Generic result container for all operations.

```python
@dataclass
class ProcessingResult(Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

#### Document

Represents a processed document.

```python
@dataclass
class Document:
    id: str
    title: Optional[str] = None
    content: str = ""
    format: DocumentFormat
    source_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

#### PatientRecord

Core patient data structure.

```python
@dataclass
class PatientRecord:
    id: str
    patient_id: str
    pmid: Optional[int] = None
    source_document_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)
    validation_status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### Enums

#### ProcessingStatus

```python
class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

#### DocumentFormat

```python
class DocumentFormat(Enum):
    PDF = "pdf"
    HTML = "html"
    XML = "xml"
    TXT = "txt"
    DOCX = "docx"
    JSON = "json"
```

#### ExtractionType

```python
class ExtractionType(Enum):
    DEMOGRAPHICS = "demographics"
    GENETICS = "genetics"
    PHENOTYPES = "phenotypes"
    TREATMENTS = "treatments"
    OUTCOMES = "outcomes"
    LAB_VALUES = "lab_values"
    IMAGING = "imaging"
    FULL_RECORD = "full_record"
```

## Configuration

### Environment Variables

The system uses comprehensive environment variable configuration:

```bash
# LLM Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_TOKEN=your_huggingface_token
DEFAULT_LLM_MODEL=deepseek/deepseek-chat-v3-0324:free

# Database Configuration
DATABASE_URL=sqlite:///data/database/biomedical_data.db
REDIS_URL=redis://localhost:6379/0
NEO4J_URI=bolt://localhost:7687

# Processing Configuration
MAX_WORKERS=4
BATCH_SIZE=10
ENABLE_OCR=False

# Vector Database Configuration
FAISS_INDEX_PATH=./data/vector_indices
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# API Usage Tracking
ENABLE_USAGE_TRACKING=True
MAX_REQUESTS_PER_MINUTE=60
MAX_REQUESTS_PER_DAY=1000
```

### Programmatic Configuration

```python
from core.config import Config

config = Config(
    llm={
        "default_model": "deepseek/deepseek-chat-v3-0324:free",
        "temperature": 0.0,
        "max_tokens": 2000
    },
    processing={
        "max_workers": 8,
        "batch_size": 20
    },
    database={
        "url": "sqlite:///custom_database.db"
    }
)
```

## Error Handling

### ProcessingResult Pattern

All API methods return `ProcessingResult` objects:

```python
result = await orchestrator.extract_from_file("document.pdf")

if result.success:
    # Handle successful result
    records = result.data
    if result.warnings:
        print(f"Warnings: {result.warnings}")
else:
    # Handle error
    print(f"Error: {result.error}")
    if result.metadata:
        print(f"Additional info: {result.metadata}")
```

### Exception Types

#### LLMError

```python
from core.base import LLMError

try:
    result = await llm_client.generate("prompt")
except LLMError as e:
    print(f"LLM error: {e.message}")
    print(f"Provider: {e.provider}")
    print(f"Model: {e.model}")
```

#### ValidationError

```python
from core.base import ValidationError

try:
    validated_record = schema_manager.validate(record)
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Field: {e.field}")
    print(f"Value: {e.value}")
```

## Examples and Usage

### Basic Extraction Pipeline

```python
import asyncio
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
from core.llm_client.smart_llm_manager import SmartLLMManager
from database.sqlite_manager import SQLiteManager

async def extract_and_store():
    # Initialize components
    llm_client = SmartLLMManager()
    orchestrator = ExtractionOrchestrator(llm_client=llm_client)
    db_manager = SQLiteManager()
    
    # Extract from document
    result = await orchestrator.extract_from_file("paper.pdf")
    
    if result.success:
        records = result.data
        
        # Store in database
        store_result = db_manager.store_patient_records(records)
        
        if store_result.success:
            print(f"Successfully stored {len(records)} records")
        else:
            print(f"Storage failed: {store_result.error}")
    else:
        print(f"Extraction failed: {result.error}")

# Run the pipeline
asyncio.run(extract_and_store())
```

### Advanced RAG System

```python
import asyncio
from rag.rag_system import RAGSystem
from database.vector_manager import VectorManager
from database.sqlite_manager import SQLiteManager
from core.llm_client.smart_llm_manager import SmartLLMManager

async def setup_rag_system():
    # Initialize components
    llm_client = SmartLLMManager()
    vector_manager = VectorManager()
    sqlite_manager = SQLiteManager()
    
    # Create RAG system
    rag_system = RAGSystem(
        vector_manager=vector_manager,
        sqlite_manager=sqlite_manager,
        llm_client=llm_client
    )
    
    # Add documents to index
    documents = load_documents()
    await rag_system.add_documents_to_index(documents)
    
    # Answer questions
    questions = [
        "What are the most common symptoms of Leigh syndrome?",
        "Which genes are frequently mutated in mitochondrial diseases?",
        "What treatments are effective for pyruvate dehydrogenase deficiency?"
    ]
    
    for question in questions:
        result = await rag_system.answer_question(question)
        if result.success:
            answer_data = result.data
            print(f"Q: {question}")
            print(f"A: {answer_data['answer']}")
            print(f"Sources: {len(answer_data['sources'])}")
            print("-" * 50)

# Run RAG system
asyncio.run(setup_rag_system())
```

### Batch Processing with Validation

```python
import asyncio
from agents.orchestrator.enhanced_orchestrator import EnhancedExtractionOrchestrator
from core.config import get_config
from core.llm_client.smart_llm_manager import SmartLLMManager

async def batch_process_with_validation():
    # Initialize components
    config = get_config()
    llm_client = SmartLLMManager()
    orchestrator = EnhancedExtractionOrchestrator(
        config=config,
        llm_client=llm_client
    )
    
    # Process multiple files
    file_paths = ["paper1.pdf", "paper2.pdf", "paper3.pdf"]
    
    for file_path in file_paths:
        try:
            # Extract data
            result = await orchestrator.process_document(file_path)
            
            if result.success:
                records = result.data
                
                # Validate extractions
                validation_result = await orchestrator.validate_extractions(records)
                
                if validation_result.success:
                    validated_records = validation_result.data
                    print(f"Validated {len(validated_records)} records from {file_path}")
                else:
                    print(f"Validation failed for {file_path}: {validation_result.error}")
            else:
                print(f"Extraction failed for {file_path}: {result.error}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

# Run batch processing
asyncio.run(batch_process_with_validation())
```

### Custom Agent Development

```python
from core.base import BaseAgent, ProcessingResult
from typing import Dict, Any

class CustomExtractionAgent(BaseAgent):
    """Custom extraction agent example."""
    
    def __init__(self, llm_client=None, **kwargs):
        super().__init__(llm_client=llm_client, **kwargs)
        self.agent_type = "custom_extraction"
    
    async def extract(self, text: str) -> ProcessingResult[Dict[str, Any]]:
        """Extract custom information from text."""
        try:
            # Custom extraction logic
            extracted_data = await self._perform_extraction(text)
            
            return ProcessingResult(
                success=True,
                data=extracted_data,
                metadata={"agent": self.agent_type}
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e),
                metadata={"agent": self.agent_type}
            )
    
    async def _perform_extraction(self, text: str) -> Dict[str, Any]:
        """Implement custom extraction logic."""
        # Your custom extraction implementation here
        pass

# Usage
agent = CustomExtractionAgent(llm_client=llm_client)
result = await agent.extract("sample text")
```

### Web API Integration

```python
import requests
import json

# Health check
response = requests.get("http://localhost:8000/api/health")
print(f"Health status: {response.json()}")

# Dashboard overview
response = requests.get("http://localhost:8000/api/v1/dashboard/overview")
overview = response.json()
print(f"System overview: {overview}")

# Authentication
auth_data = {
    "username": "user@example.com",
    "password": "password123"
}
response = requests.post("http://localhost:8000/api/v1/auth/token", json=auth_data)
if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Authenticated request
    response = requests.get(
        "http://localhost:8000/api/v1/dashboard/statistics",
        headers=headers
    )
    statistics = response.json()
    print(f"Statistics: {statistics}")
```

## Performance Optimization

### Batch Processing

```python
# Process multiple files efficiently
file_paths = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
result = await orchestrator.extract_batch(file_paths)

# Use appropriate batch sizes
config = Config(processing={"batch_size": 20, "max_workers": 8})
```

### Caching

```python
# Enable result caching
from core.cache import CacheManager

cache_manager = CacheManager()
cached_result = await cache_manager.get_cached_result("cache_key")

if not cached_result:
    result = await orchestrator.extract_from_file("document.pdf")
    await cache_manager.cache_result("cache_key", result)
```

### Memory Management

```python
# Process large documents in chunks
config = Config(processing={"max_document_size": "100MB"})

# Use streaming for large files
async for chunk in orchestrator.stream_process_large_file("large_document.pdf"):
    process_chunk(chunk)
```

## Monitoring and Metrics

### API Usage Tracking

```python
from core.api_usage_tracker import APIUsageTracker

tracker = APIUsageTracker()

# Track API calls
await tracker.track_request(
    provider="openrouter",
    model="deepseek/deepseek-chat-v3-0324:free",
    tokens_used=150,
    cost=0.001
)

# Get usage statistics
stats = await tracker.get_usage_statistics()
print(f"Total requests: {stats['total_requests']}")
print(f"Total cost: ${stats['total_cost']:.4f}")
```

### Performance Metrics

```python
# Get system performance metrics
orchestrator_stats = orchestrator.get_extraction_statistics(records)
db_stats = db_manager.get_statistics()
vector_stats = vector_manager.get_statistics()

print(f"Extraction stats: {orchestrator_stats}")
print(f"Database stats: {db_stats.data}")
print(f"Vector DB stats: {vector_stats.data}")
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure environment variables are set correctly
2. **Memory Issues**: Reduce batch size or max workers for large documents
3. **Timeout Errors**: Increase timeout settings for complex documents
4. **Schema Validation Errors**: Check that extracted data matches expected schema

### Debug Mode

```python
from core.logging_config import setup_logging

# Enable debug logging
setup_logging({
    "log_level": "DEBUG",
    "log_file": "debug.log"
})

# Enable verbose output
config = Config(logging={"log_level": "DEBUG"})
```

### Health Checks

```python
# Check system health
health_status = await orchestrator.check_system_health()

if not health_status.success:
    print(f"System health check failed: {health_status.error}")
    print(f"Components status: {health_status.metadata}")
```

## Support and Contributing

For issues, feature requests, or contributions:

1. Check the existing documentation and examples
2. Review the source code in the `src/` directory
3. Submit issues through the project repository
4. Follow the contribution guidelines

## Version Information

This documentation covers:
- **Core System**: v1.0.0
- **API Endpoints**: v1.0.0
- **Data Models**: v1.0.0
- **Configuration**: v1.0.0

For the latest updates and changes, refer to the project repository and release notes.