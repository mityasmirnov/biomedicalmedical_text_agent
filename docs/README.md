# Biomedical Data Extraction Engine - Complete Documentation

## Overview

The Biomedical Data Extraction Engine is a comprehensive AI-powered system for extracting structured patient-level data from biomedical literature. This system combines multiple LLM providers, specialized extraction agents, ontology management, and advanced data processing to deliver high-quality biomedical data extraction capabilities.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd biomedical-data-extraction-engine

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys and configuration

# Run the system
python src/main.py extract sample_document.pdf
```

### Basic Usage

```python
import asyncio
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
from core.llm_client.smart_llm_manager import SmartLLMManager

async def extract_patient_data():
    # Initialize LLM client and orchestrator
    llm_client = SmartLLMManager()
    orchestrator = ExtractionOrchestrator(llm_client=llm_client)
    
    # Extract from document
    result = await orchestrator.extract_from_file("medical_paper.pdf")
    
    if result.success:
        records = result.data
        print(f"Extracted {len(records)} patient records")
        return records
    else:
        print(f"Extraction failed: {result.error}")
        return None

# Run extraction
records = asyncio.run(extract_patient_data())
```

## 📚 Documentation Index

### Core Documentation

- **[Comprehensive API Documentation](COMPREHENSIVE_API_DOCUMENTATION.md)** - Complete API reference for all components
- **[LLM Client APIs](LLM_CLIENTS_API.md)** - Detailed documentation for all LLM client implementations
- **[Extraction Agents API](EXTRACTION_AGENTS_API.md)** - Specialized agents for different data types
- **[User Guide](../USER_GUIDE.md)** - User-friendly guide for getting started
- **[System Status](../SYSTEM_STATUS.md)** - Current system status and capabilities

### Component-Specific Documentation

- **[Engine Documentation](Engine.md)** - Core engine architecture and design
- **[Frontend Documentation](Frontend.md)** - Web interface documentation
- **[LANGEXTRACT Integration](LANGEXTRACT.md)** - Language extraction capabilities
- **[API Documentation](../API_DOCUMENTATION.md)** - REST API endpoints and usage

## 🏗️ System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Biomedical Data Extraction Engine        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   LLM Clients   │  │ Extraction      │  │ Ontology    │ │
│  │                 │  │ Agents          │  │ Management  │ │
│  │ • OpenRouter    │  │ • Phenotypes    │  │ • HPO       │ │
│  │ • Ollama        │  │ • Genetics      │  │ • Gene      │ │
│  │ • HuggingFace   │  │ • Treatments    │  │ • UMLS      │ │
│  │ • Smart Manager │  │ • Demographics  │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Orchestrator  │  │   Database      │  │   RAG       │ │
│  │                 │  │   Management    │  │   System    │ │
│  │ • Extraction    │  │ • SQLite        │  │ • Vector    │ │
│  │ • Validation    │  │ • Vector        │  │ • Search    │ │
│  │ • Batch Proc.   │  │ • Neo4j         │  │ • Q&A       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Web API       │  │   CLI           │  │   UI        │ │
│  │                 │  │                 │  │             │ │
│  │ • FastAPI       │  │ • Click         │  │ • React     │ │
│  │ • REST          │  │ • Rich          │  │ • Dashboard │ │
│  │ • WebSocket     │  │ • Progress      │  │ • Analytics │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Document Input** → PDF, HTML, XML, TXT documents
2. **Text Extraction** → OCR and text parsing
3. **Patient Segmentation** → Identify individual patient cases
4. **Multi-Agent Extraction** → Specialized agents for different data types
5. **Ontology Normalization** → HPO, HGNC, UMLS integration
6. **Validation** → Schema and quality checks
7. **Storage** → SQLite, vector database, and export options
8. **Query Interface** → RAG system for question answering

## 🔧 Key Features

### 🤖 Multi-Provider LLM Support
- **OpenRouter** - Access to multiple models (GPT-4, Claude, etc.)
- **Ollama** - Local model inference
- **HuggingFace** - Open-source models with quantization
- **Smart Fallback** - Automatic provider switching

### 🧬 Specialized Extraction Agents
- **Phenotypes Agent** - Clinical phenotypes with HPO integration
- **Genetics Agent** - Gene symbols, mutations, inheritance
- **Treatments Agent** - Medications, dosages, interventions
- **Demographics Agent** - Age, sex, ethnicity, family history

### 🗃️ Advanced Data Management
- **SQLite Database** - Structured patient record storage
- **Vector Database** - Semantic search and similarity
- **Neo4j Integration** - Graph-based knowledge representation
- **Export Options** - CSV, JSON, and custom formats

### 🔍 RAG System
- **Semantic Search** - Find similar cases and documents
- **Question Answering** - Natural language queries
- **Context Retrieval** - Relevant document snippets
- **Source Attribution** - Track information sources

### 🌐 Web Interface
- **FastAPI Backend** - RESTful API endpoints
- **React Frontend** - Modern dashboard interface
- **Real-time Updates** - WebSocket communication
- **Authentication** - User management and security

## 📊 Data Schema

### Patient Record Structure

```python
@dataclass
class PatientRecord:
    # Core Information
    id: str
    patient_id: str
    source_document_id: str
    
    # Demographics
    sex: Optional[int]              # 0=female, 1=male, 2=other
    age_of_onset: Optional[float]   # Age at symptom onset
    age_at_diagnosis: Optional[float] # Age at diagnosis
    ethnicity: Optional[str]
    consanguinity: Optional[int]    # 0=no, 1=yes
    
    # Genetics
    gene: Optional[str]             # Primary gene (HGNC symbol)
    mutations: Optional[str]        # Specific mutations
    inheritance: Optional[str]      # Inheritance pattern
    zygosity: Optional[str]         # Mutation zygosity
    
    # Clinical
    phenotypes: Optional[str]       # HPO terms
    symptoms: Optional[str]         # Symptom descriptions
    diagnostic_findings: Optional[str] # Test results
    
    # Treatment
    treatments: Optional[str]       # Therapeutic interventions
    medications: Optional[str]      # Medications used
    dosages: Optional[str]          # Dosage information
    
    # Outcomes
    survival_status: Optional[int]  # 0=alive, 1=deceased
    survival_time: Optional[float]  # Survival time in months
    
    # Metadata
    confidence_scores: Dict[str, float]
    validation_status: str
    created_at: datetime
    updated_at: datetime
```

## 🚀 Getting Started

### 1. Environment Setup

```bash
# Required environment variables
OPENROUTER_API_KEY=your_openrouter_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional
HUGGINGFACE_API_TOKEN=your_hf_token  # Optional

# Database configuration
DATABASE_URL=sqlite:///data/database/biomedical_data.db
REDIS_URL=redis://localhost:6379/0

# Processing configuration
MAX_WORKERS=4
BATCH_SIZE=10
ENABLE_OCR=False
```

### 2. Basic Extraction

```python
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
from core.llm_client.smart_llm_manager import SmartLLMManager

# Initialize system
llm_client = SmartLLMManager()
orchestrator = ExtractionOrchestrator(llm_client=llm_client)

# Extract from document
result = await orchestrator.extract_from_file("paper.pdf")
```

### 3. Batch Processing

```python
# Process multiple files
file_paths = ["paper1.pdf", "paper2.pdf", "paper3.pdf"]
result = await orchestrator.extract_batch(file_paths)

if result.success:
    all_records = result.data
    print(f"Processed {len(all_records)} records from {len(file_paths)} files")
```

### 4. RAG Question Answering

```python
from rag.rag_system import RAGSystem
from database.vector_manager import VectorManager
from database.sqlite_manager import SQLiteManager

# Initialize RAG system
vector_manager = VectorManager()
sqlite_manager = SQLiteManager()
rag_system = RAGSystem(vector_manager, sqlite_manager, llm_client)

# Answer questions
result = await rag_system.answer_question(
    "What are the most common symptoms of Leigh syndrome?"
)

if result.success:
    answer_data = result.data
    print(f"Answer: {answer_data['answer']}")
    print(f"Sources: {len(answer_data['sources'])}")
```

## 🔌 API Endpoints

### REST API

```bash
# Health check
GET /api/health

# Dashboard
GET /api/v1/dashboard/overview
GET /api/v1/dashboard/statistics
GET /api/v1/dashboard/recent-activities

# Authentication
POST /api/v1/auth/token
POST /api/v1/auth/register
POST /api/v1/auth/logout

# WebSocket
WS /api/v1/ws
```

### CLI Commands

```bash
# Extract from single file
python src/main.py extract document.pdf

# Extract with validation
python src/main.py extract document.pdf --validate --ground-truth truth.json

# Extract with custom output
python src/main.py extract document.pdf --format csv --output results.csv

# Batch processing
python src/main.py batch file1.pdf file2.pdf file3.pdf

# Query knowledge base
python src/main.py query "What genes cause Leigh syndrome?"
```

## 🧪 Testing and Validation

### Running Tests

```bash
# Run all tests
pytest

# Run specific test files
pytest test_enhanced_system.py
pytest test_ui_system.py

# Run with coverage
pytest --cov=src

# Run with verbose output
pytest -v
```

### Validation

```python
from agents.orchestrator.enhanced_orchestrator import EnhancedExtractionOrchestrator

# Initialize with validation
orchestrator = EnhancedExtractionOrchestrator(
    config=config,
    llm_client=llm_client
)

# Extract and validate
result = await orchestrator.process_document("document.pdf")
if result.success:
    records = result.data
    
    # Validate extractions
    validation_result = await orchestrator.validate_extractions(records)
    if validation_result.success:
        validated_records = validation_result.data
        print(f"Validated {len(validated_records)} records")
```

## 📈 Performance and Optimization

### Batch Processing

```python
# Optimize batch size
config = Config(processing={"batch_size": 20, "max_workers": 8})

# Process in parallel
async def process_batch_parallel(file_paths):
    tasks = [orchestrator.extract_from_file(path) for path in file_paths]
    results = await asyncio.gather(*tasks)
    return results
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

## 🔍 Monitoring and Metrics

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

## 🛠️ Development

### Adding New Agents

```python
from core.base import BaseAgent, ProcessingResult

class CustomAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agent_type = "custom"
    
    async def extract(self, text: str) -> ProcessingResult[Dict[str, Any]]:
        # Implement custom extraction logic
        pass
```

### Custom Ontologies

```python
from ontologies.base_ontology import BaseOntology

class CustomOntology(BaseOntology):
    def __init__(self, ontology_path: str):
        super().__init__(ontology_path)
    
    def normalize_term(self, term: str) -> ProcessingResult[Dict[str, Any]]:
        # Implement custom normalization
        pass
```

### Extending the RAG System

```python
from rag.base_rag import BaseRAG

class CustomRAG(BaseRAG):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def custom_retrieval(self, query: str) -> ProcessingResult[List[Dict[str, Any]]]:
        # Implement custom retrieval logic
        pass
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   ```bash
   # Check environment variables
   echo $OPENROUTER_API_KEY
   # Ensure .env file is loaded
   ```

2. **Memory Issues**
   ```python
   # Reduce batch size and workers
   config = Config(processing={"batch_size": 5, "max_workers": 2})
   ```

3. **Timeout Errors**
   ```python
   # Increase timeout settings
   config = Config(llm={"timeout": 120})
   ```

4. **Schema Validation Errors**
   ```python
   # Check extracted data format
   print(record.data)
   # Validate against schema
   schema_manager.validate(record)
   ```

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

## 🤝 Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run linting
black src/
isort src/
flake8 src/
mypy src/
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Include unit tests for new features

### Testing

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- OpenRouter for providing access to multiple LLM models
- HuggingFace for open-source model support
- The biomedical research community for domain expertise
- Contributors and maintainers of this project

## 📞 Support

### Getting Help

1. **Documentation** - Check this documentation first
2. **Issues** - Search existing issues on GitHub
3. **Discussions** - Use GitHub Discussions for questions
4. **Email** - Contact the maintainers directly

### Reporting Issues

When reporting issues, please include:

- System information (OS, Python version)
- Error messages and stack traces
- Steps to reproduce
- Expected vs. actual behavior
- Sample data (if applicable)

### Feature Requests

For feature requests:

1. Check if the feature already exists
2. Search existing feature requests
3. Create a new feature request with:
   - Clear description of the feature
   - Use case and benefits
   - Implementation suggestions (if any)

## 🔄 Version History

### v1.0.0 (Current)
- Core extraction system
- Multi-provider LLM support
- Specialized extraction agents
- RAG system
- Web interface
- CLI tools

### Upcoming Features
- Advanced validation rules
- Machine learning-based extraction
- Real-time collaboration
- Advanced analytics dashboard
- Mobile application

---

**Note**: This documentation is continuously updated. For the latest information, check the project repository and release notes.

For questions, issues, or contributions, please visit the project repository or contact the maintainers.