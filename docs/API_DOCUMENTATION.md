# Biomedical Data Extraction Engine - API Documentation

## Overview

The Biomedical Data Extraction Engine provides a comprehensive API for extracting structured patient-level data from biomedical literature. This document describes the core APIs, data models, and integration patterns.

## Core Components

### 1. Extraction Orchestrator API

The `ExtractionOrchestrator` is the main entry point for document processing and data extraction.

#### Class: `ExtractionOrchestrator`

```python
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator

# Initialize orchestrator
orchestrator = ExtractionOrchestrator(config=optional_config)
```

#### Methods

##### `extract_from_file(file_path: str) -> ProcessingResult[List[PatientRecord]]`

Extracts patient records from a single document file.

**Parameters:**
- `file_path` (str): Absolute path to the document file (PDF, HTML, XML, TXT)

**Returns:**
- `ProcessingResult[List[PatientRecord]]`: Result containing extracted patient records

**Example:**
```python
result = await orchestrator.extract_from_file("/path/to/document.pdf")
if result.success:
    records = result.data
    print(f"Extracted {len(records)} patient records")
else:
    print(f"Extraction failed: {result.error}")
```

##### `extract_batch(file_paths: List[str]) -> ProcessingResult[List[PatientRecord]]`

Extracts patient records from multiple document files.

**Parameters:**
- `file_paths` (List[str]): List of absolute paths to document files

**Returns:**
- `ProcessingResult[List[PatientRecord]]`: Result containing all extracted patient records

**Example:**
```python
files = ["/path/to/doc1.pdf", "/path/to/doc2.pdf"]
result = await orchestrator.extract_batch(files)
if result.success:
    all_records = result.data
    print(f"Extracted {len(all_records)} total records from {len(files)} files")
```

##### `get_extraction_statistics(records: List[PatientRecord]) -> Dict[str, Any]`

Generates statistics about extracted records.

**Parameters:**
- `records` (List[PatientRecord]): List of patient records to analyze

**Returns:**
- `Dict[str, Any]`: Statistics including field coverage, confidence scores, and source information

### 2. Database Management APIs

#### SQLite Manager

The `SQLiteManager` handles structured data storage and retrieval.

```python
from database.sqlite_manager import SQLiteManager

# Initialize database manager
db_manager = SQLiteManager(db_path="data/database/biomedical_data.db")
```

##### Key Methods

**`store_patient_records(records: List[PatientRecord]) -> ProcessingResult[List[str]]`**

Stores patient records in the database.

**`get_patient_records(pmid: Optional[int] = None, gene: Optional[str] = None, limit: int = 100) -> ProcessingResult[List[Dict[str, Any]]]`**

Retrieves patient records with optional filtering.

**`search_records(query: str, limit: int = 50) -> ProcessingResult[List[Dict[str, Any]]]`**

Performs full-text search across patient records.

**`export_to_csv(output_path: str) -> ProcessingResult[str]`**

Exports all patient records to CSV format.

#### Vector Manager

The `VectorManager` handles semantic search and document indexing.

```python
from database.vector_manager import VectorManager

# Initialize vector manager
vector_manager = VectorManager(index_path="data/vector_indices")
```

##### Key Methods

**`add_documents(documents: List[Document]) -> ProcessingResult[int]`**

Adds documents to the vector index for semantic search.

**`search(query: str, top_k: int = 10) -> ProcessingResult[List[Dict[str, Any]]]`**

Performs semantic search to find similar documents.

### 3. RAG System API

The `RAGSystem` combines retrieval and generation for question answering.

```python
from rag.rag_system import RAGSystem

# Initialize RAG system
rag_system = RAGSystem(
    vector_manager=vector_manager,
    sqlite_manager=sqlite_manager,
    llm_client=llm_client
)
```

##### Key Methods

**`answer_question(question: str, max_context_docs: int = 5, include_patient_records: bool = True) -> ProcessingResult[Dict[str, Any]]`**

Answers questions using retrieval-augmented generation.

**Parameters:**
- `question` (str): Natural language question
- `max_context_docs` (int): Maximum documents to retrieve for context
- `include_patient_records` (bool): Whether to include patient record data

**Returns:**
- `ProcessingResult[Dict[str, Any]]`: Answer with sources and context information

**Example:**
```python
result = await rag_system.answer_question("What genes are associated with Leigh syndrome?")
if result.success:
    answer_data = result.data
    print(f"Answer: {answer_data['answer']}")
    print(f"Sources: {len(answer_data['sources'])}")
```

### 4. Ontology Integration APIs

#### HPO Manager

The `HPOManager` normalizes phenotype descriptions to Human Phenotype Ontology terms.

```python
from ontologies.hpo_manager import HPOManager

# Initialize HPO manager
hpo_manager = HPOManager()
```

##### Key Methods

**`normalize_phenotype(phenotype_text: str) -> ProcessingResult[Dict[str, Any]]`**

Normalizes phenotype text to HPO terms.

**`batch_normalize_phenotypes(phenotype_list: List[str]) -> ProcessingResult[List[Dict[str, Any]]]`**

Normalizes multiple phenotypes at once.

**`search_terms(query: str, limit: int = 10) -> ProcessingResult[List[Dict[str, Any]]]`**

Searches HPO terms by query.

#### Gene Manager

The `GeneManager` normalizes gene symbols to HGNC standards.

```python
from ontologies.gene_manager import GeneManager

# Initialize gene manager
gene_manager = GeneManager()
```

##### Key Methods

**`normalize_gene_symbol(gene_symbol: str) -> ProcessingResult[Dict[str, Any]]`**

Normalizes gene symbol to official HGNC symbol.

**`batch_normalize_genes(gene_list: List[str]) -> ProcessingResult[List[Dict[str, Any]]]`**

Normalizes multiple gene symbols at once.

## Data Models

### PatientRecord

The core data structure representing an extracted patient record.

```python
class PatientRecord:
    id: str                          # Unique record identifier
    patient_id: str                  # Patient identifier from source
    source_document_id: str          # Source document identifier
    data: Dict[str, Any]            # Extracted patient data
    confidence_scores: Dict[str, float]  # Field confidence scores
    extraction_metadata: Dict[str, Any]  # Extraction metadata
    validation_status: str           # Validation status
    created_at: datetime            # Creation timestamp
    updated_at: datetime            # Last update timestamp
```

### Document

Represents a processed document.

```python
class Document:
    id: str                     # Unique document identifier
    title: str                  # Document title
    content: str               # Extracted text content
    source_path: str           # Original file path
    metadata: Dict[str, Any]   # Document metadata (PMID, DOI, etc.)
    created_at: datetime       # Processing timestamp
```

### ProcessingResult

Generic result wrapper for all API operations.

```python
class ProcessingResult[T]:
    success: bool              # Operation success status
    data: T                   # Result data (if successful)
    error: Optional[str]      # Error message (if failed)
    warnings: List[str]       # Warning messages
    metadata: Dict[str, Any]  # Additional metadata
```

## Patient Data Schema

The extracted patient data follows a standardized schema:

### Demographics
- `patient_id`: Patient identifier
- `sex`: Sex (0=female, 1=male, 2=other)
- `age_of_onset`: Age at symptom onset (years)
- `age_at_diagnosis`: Age at diagnosis (years)
- `age_at_death`: Age at death (years)
- `ethnicity`: Patient ethnicity
- `consanguinity`: Consanguineous parents (0=no, 1=yes)

### Genetics
- `gene`: Primary gene involved (HGNC symbol)
- `mutations`: Specific mutations/variants
- `inheritance`: Inheritance pattern
- `zygosity`: Mutation zygosity
- `parental_origin`: Origin of mutation
- `genetic_testing`: Type of genetic testing
- `additional_genes`: Other genes mentioned

### Clinical
- `phenotypes`: Clinical phenotypes (HPO terms)
- `symptoms`: Reported symptoms
- `diagnostic_findings`: Diagnostic test results
- `lab_values`: Laboratory values
- `imaging_findings`: Imaging results

### Treatment
- `treatments`: Therapeutic interventions
- `medications`: Medications used
- `dosages`: Medication dosages
- `treatment_response`: Response to treatment
- `adverse_events`: Adverse events

### Outcomes
- `survival_status`: Survival status (0=alive, 1=deceased)
- `survival_time`: Survival time (months)
- `cause_of_death`: Cause of death
- `follow_up_duration`: Follow-up duration (months)
- `clinical_outcome`: Overall clinical outcome

## Configuration

### Environment Variables

The system uses environment variables for configuration:

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# OpenAI API Configuration (optional)
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# Hugging Face Configuration (optional)
HUGGINGFACE_API_TOKEN=your_huggingface_token

# Database Configuration
DATABASE_URL=sqlite:///data/database/biomedical_data.db
REDIS_URL=redis://localhost:6379/0

# Processing Configuration
MAX_WORKERS=4
BATCH_SIZE=10
ENABLE_OCR=False

# Paths Configuration
DATA_DIR=./data
SCHEMAS_DIR=./data/schemas
ONTOLOGIES_DIR=./data/ontologies
OUTPUT_DIR=./data/output

# LLM Configuration
DEFAULT_LLM_MODEL=deepseek/deepseek-chat-v3-0324:free
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=2000
LLM_TIMEOUT=60

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/application.log
```

### Programmatic Configuration

```python
from core.config import Config

# Custom configuration
config = Config(
    llm={"default_model": "deepseek/deepseek-chat-v3-0324:free"},
    processing={"max_workers": 8, "batch_size": 20},
    paths={"data_dir": "/custom/data/path"}
)

# Use with orchestrator
orchestrator = ExtractionOrchestrator(config=config)
```

## Error Handling

All API methods return `ProcessingResult` objects that include error information:

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

## Rate Limiting and Quotas

The system implements rate limiting for LLM API calls:

- OpenRouter: Respects API rate limits (varies by model)
- Automatic retry with exponential backoff
- Configurable timeout settings
- Batch processing to optimize API usage

## Integration Examples

### Basic Extraction Pipeline

```python
import asyncio
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
from database.sqlite_manager import SQLiteManager

async def extract_and_store():
    # Initialize components
    orchestrator = ExtractionOrchestrator()
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

### RAG-based Question Answering

```python
import asyncio
from rag.rag_system import RAGSystem

async def answer_questions():
    # Initialize RAG system
    rag_system = RAGSystem()
    
    # Add documents to index (one-time setup)
    # documents = load_documents()
    # await rag_system.add_documents_to_index(documents)
    
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

# Run Q&A
asyncio.run(answer_questions())
```

### Batch Processing with Ontology Normalization

```python
import asyncio
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
from ontologies.hpo_manager import HPOManager
from ontologies.gene_manager import GeneManager

async def process_with_normalization():
    # Initialize components
    orchestrator = ExtractionOrchestrator()
    hpo_manager = HPOManager()
    gene_manager = GeneManager()
    
    # Process multiple files
    file_paths = ["paper1.pdf", "paper2.pdf", "paper3.pdf"]
    result = await orchestrator.extract_batch(file_paths)
    
    if result.success:
        records = result.data
        
        # Normalize phenotypes and genes
        for record in records:
            # Normalize phenotypes
            if record.data.get('phenotypes'):
                phenotypes = record.data['phenotypes']
                if isinstance(phenotypes, str):
                    phenotypes = [phenotypes]
                
                hpo_result = hpo_manager.batch_normalize_phenotypes(phenotypes)
                if hpo_result.success:
                    record.data['normalized_phenotypes'] = hpo_result.data
            
            # Normalize genes
            if record.data.get('gene'):
                gene_result = gene_manager.normalize_gene_symbol(record.data['gene'])
                if gene_result.success:
                    record.data['normalized_gene'] = gene_result.data
        
        print(f"Processed and normalized {len(records)} records")

# Run batch processing
asyncio.run(process_with_normalization())
```

## Performance Considerations

### Optimization Tips

1. **Batch Processing**: Use `extract_batch()` for multiple files to optimize API usage
2. **Caching**: Results are cached to avoid re-processing identical content
3. **Parallel Processing**: Configure `max_workers` based on your system capabilities
4. **Memory Management**: Large documents are processed in chunks to manage memory usage
5. **Database Indexing**: SQLite indexes are created for common query patterns

### Monitoring and Metrics

```python
# Get system statistics
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

Enable debug logging for detailed troubleshooting:

```python
from core.logging_config import setup_logging

setup_logging({"log_level": "DEBUG", "log_file": "debug.log"})
```

## Support and Contributing

For issues, feature requests, or contributions, please refer to the project repository and documentation.

