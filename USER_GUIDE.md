# Biomedical Data Extraction Engine - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Basic Usage](#basic-usage)
6. [Advanced Features](#advanced-features)
7. [Data Export and Analysis](#data-export-and-analysis)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Introduction

The Biomedical Data Extraction Engine is an AI-powered system designed to extract structured patient-level data from biomedical literature, particularly scientific papers and case reports. The system uses advanced natural language processing, machine learning agents, and medical ontologies to automatically identify and extract key information about patients, including demographics, genetics, clinical phenotypes, treatments, and outcomes.

### Key Features

- **Automated Data Extraction**: Extract patient records from PDF documents, HTML pages, and text files
- **Medical Ontology Integration**: Normalize phenotypes using HPO (Human Phenotype Ontology) and genes using HGNC standards
- **Multi-Agent Architecture**: Specialized AI agents for different types of medical information
- **RAG-based Question Answering**: Ask questions about your extracted data using natural language
- **Database Integration**: Store and query extracted data using SQLite and vector databases
- **Batch Processing**: Process multiple documents efficiently
- **Export Capabilities**: Export data to CSV, JSON, and other formats

### Supported Document Types

- PDF files (scientific papers, case reports)
- HTML documents (web-based articles)
- Plain text files
- XML documents

### Target Use Cases

- **Clinical Research**: Extract patient data from case reports and clinical studies
- **Systematic Reviews**: Gather structured data from multiple papers for meta-analysis
- **Phenotype-Genotype Studies**: Collect genetic and phenotypic information from literature
- **Drug Discovery**: Extract treatment and outcome information from clinical reports
- **Medical Database Creation**: Build structured databases from unstructured literature

## Installation

### Prerequisites

- Python 3.8 or higher
- 4GB+ RAM (8GB+ recommended for large documents)
- Internet connection for API access
- OpenRouter API key (for free LLM access)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd biomedical_extraction_engine
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Optional: Install additional ML libraries for better performance
pip install sentence-transformers faiss-cpu scikit-learn
```

### Step 3: Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys:

```bash
# Required: OpenRouter API key (free tier available)
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Optional: OpenAI API key (for better performance)
OPENAI_API_KEY=sk-your-openai-key-here

# Optional: Hugging Face token (for local models)
HUGGINGFACE_API_TOKEN=hf_your-token-here
```

### Step 4: Initialize the System

```bash
# Create necessary directories
python -c "from core.config import get_config; get_config()"

# Test the installation
python test_system.py
```

## Quick Start

### Extract Data from a Single Document

```bash
# Using the command-line interface
python src/main.py extract --file "path/to/your/document.pdf" --output "results.csv"

# Using Python API
python -c "
import asyncio
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator

async def extract():
    orchestrator = ExtractionOrchestrator()
    result = await orchestrator.extract_from_file('path/to/document.pdf')
    if result.success:
        print(f'Extracted {len(result.data)} patient records')
    else:
        print(f'Error: {result.error}')

asyncio.run(extract())
"
```

### Process Multiple Documents

```bash
# Batch processing
python src/main.py batch --input-dir "path/to/documents/" --output "batch_results.csv"
```

### Ask Questions About Your Data

```bash
# Interactive Q&A mode
python src/main.py rag --question "What genes are associated with Leigh syndrome?"
```

## Configuration

### Environment Variables

The system uses environment variables for configuration. Key settings include:

#### API Configuration
```bash
# Primary LLM provider (recommended for free usage)
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# Alternative LLM provider
OPENAI_API_KEY=sk-your-openai-key
OPENAI_API_BASE=https://api.openai.com/v1

# Local model support
HUGGINGFACE_API_TOKEN=hf_your-token
```

#### Processing Configuration
```bash
# Performance settings
MAX_WORKERS=4                    # Number of parallel workers
BATCH_SIZE=10                   # Documents per batch
LLM_TIMEOUT=60                  # API timeout in seconds

# Model settings
DEFAULT_LLM_MODEL=deepseek/deepseek-chat-v3-0324:free
LLM_TEMPERATURE=0.0             # Lower = more deterministic
LLM_MAX_TOKENS=2000            # Maximum response length
```

#### Data Storage
```bash
# File paths
DATA_DIR=./data                 # Main data directory
OUTPUT_DIR=./data/output        # Output files
DATABASE_URL=sqlite:///data/database/biomedical_data.db

# Logging
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=./logs/application.log
```

### Configuration File

For advanced users, create a `config.yaml` file:

```yaml
llm:
  default_model: "deepseek/deepseek-chat-v3-0324:free"
  temperature: 0.0
  max_tokens: 2000
  timeout: 60

processing:
  max_workers: 4
  batch_size: 10
  enable_ocr: false

database:
  url: "sqlite:///data/database/biomedical_data.db"
  
paths:
  data_dir: "./data"
  schemas_dir: "./data/schemas"
  ontologies_dir: "./data/ontologies"
  output_dir: "./data/output"

logging:
  level: "INFO"
  file: "./logs/application.log"
```

## Basic Usage

### Command Line Interface

The system provides a comprehensive CLI for common tasks:

#### Extract Data from Documents

```bash
# Single document
python src/main.py extract --file document.pdf

# Multiple documents
python src/main.py extract --file doc1.pdf --file doc2.pdf --file doc3.pdf

# Entire directory
python src/main.py extract --input-dir /path/to/documents/

# With custom output
python src/main.py extract --file document.pdf --output results.csv --format csv
```

#### Batch Processing

```bash
# Process all PDFs in a directory
python src/main.py batch --input-dir papers/ --output batch_results.csv

# With filtering
python src/main.py batch --input-dir papers/ --pattern "*.pdf" --output results.csv

# Parallel processing
python src/main.py batch --input-dir papers/ --workers 8 --output results.csv
```

#### Database Operations

```bash
# View database statistics
python src/main.py db stats

# Search records
python src/main.py db search --query "SURF1 mutation"

# Export data
python src/main.py db export --output all_records.csv --format csv
```

#### Question Answering

```bash
# Ask a question
python src/main.py rag --question "What are the symptoms of Leigh syndrome?"

# Interactive mode
python src/main.py rag --interactive
```

### Python API Usage

#### Basic Extraction

```python
import asyncio
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator

async def extract_data():
    # Initialize the orchestrator
    orchestrator = ExtractionOrchestrator()
    
    # Extract from a single file
    result = await orchestrator.extract_from_file("paper.pdf")
    
    if result.success:
        records = result.data
        print(f"Successfully extracted {len(records)} patient records")
        
        # Access individual records
        for record in records:
            print(f"Patient ID: {record.data.get('patient_id')}")
            print(f"Gene: {record.data.get('gene')}")
            print(f"Phenotypes: {record.data.get('phenotypes')}")
            print("-" * 40)
    else:
        print(f"Extraction failed: {result.error}")

# Run the extraction
asyncio.run(extract_data())
```

#### Database Integration

```python
from database.sqlite_manager import SQLiteManager

# Initialize database manager
db_manager = SQLiteManager()

# Store extracted records
store_result = db_manager.store_patient_records(records)
if store_result.success:
    print(f"Stored {len(records)} records in database")

# Query records
query_result = db_manager.get_patient_records(gene="SURF1", limit=10)
if query_result.success:
    surf1_records = query_result.data
    print(f"Found {len(surf1_records)} SURF1-related records")

# Search records
search_result = db_manager.search_records("seizure", limit=20)
if search_result.success:
    seizure_records = search_result.data
    print(f"Found {len(seizure_records)} records mentioning seizures")
```

#### Ontology Normalization

```python
from ontologies.hpo_manager import HPOManager
from ontologies.gene_manager import GeneManager

# Initialize ontology managers
hpo_manager = HPOManager()
gene_manager = GeneManager()

# Normalize phenotypes
phenotypes = ["seizures", "developmental delay", "muscle weakness"]
hpo_result = hpo_manager.batch_normalize_phenotypes(phenotypes)

if hpo_result.success:
    for normalized in hpo_result.data:
        print(f"Original: {normalized['original_text']}")
        if normalized['best_match']:
            match = normalized['best_match']
            print(f"HPO: {match['hpo_id']} - {match['hpo_name']}")
        print("-" * 30)

# Normalize genes
genes = ["SURF1", "surf1", "NDUFS1"]
gene_result = gene_manager.batch_normalize_genes(genes)

if gene_result.success:
    for normalized in gene_result.data:
        print(f"Original: {normalized['original_symbol']}")
        print(f"Normalized: {normalized['normalized_symbol']}")
        print(f"Confidence: {normalized['confidence']}")
        print("-" * 30)
```

## Advanced Features

### RAG-based Question Answering

The system includes a Retrieval-Augmented Generation (RAG) system that allows you to ask natural language questions about your extracted data.

#### Setting Up RAG

```python
from rag.rag_system import RAGSystem
from database.vector_manager import VectorManager
from database.sqlite_manager import SQLiteManager

# Initialize components
vector_manager = VectorManager()
sqlite_manager = SQLiteManager()
rag_system = RAGSystem(vector_manager, sqlite_manager)

# Add documents to the vector index (one-time setup)
documents = load_your_documents()  # Your document loading logic
await rag_system.add_documents_to_index(documents)
```

#### Asking Questions

```python
# Ask questions about your data
questions = [
    "What are the most common symptoms of Leigh syndrome?",
    "Which genes are frequently mutated in mitochondrial diseases?",
    "What treatments show the best outcomes?",
    "How many patients had onset before age 2?",
    "What is the survival rate for SURF1 mutations?"
]

for question in questions:
    result = await rag_system.answer_question(question)
    if result.success:
        answer_data = result.data
        print(f"Q: {question}")
        print(f"A: {answer_data['answer']}")
        print(f"Sources: {len(answer_data['sources'])} documents")
        print("=" * 60)
```

### Custom Extraction Agents

You can create custom extraction agents for specific types of information:

```python
from agents.base_agent import BaseExtractionAgent
from core.base import ProcessingResult

class CustomTreatmentAgent(BaseExtractionAgent):
    """Custom agent for extracting treatment information."""
    
    def __init__(self, llm_client):
        super().__init__(llm_client)
        self.agent_type = "treatment_extraction"
    
    async def execute(self, patient_segment: str, context: dict) -> ProcessingResult:
        prompt = f"""
        Extract detailed treatment information from this patient case:
        
        {patient_segment}
        
        Focus on:
        - Medications and dosages
        - Therapeutic interventions
        - Treatment duration
        - Response to treatment
        - Side effects
        
        Return structured data in JSON format.
        """
        
        result = await self.llm_client.generate(prompt)
        
        if result.success:
            # Process and validate the extracted data
            treatment_data = self.parse_treatment_data(result.data)
            return ProcessingResult(success=True, data=treatment_data)
        else:
            return ProcessingResult(success=False, error=result.error)
    
    def parse_treatment_data(self, raw_data: str) -> dict:
        # Your custom parsing logic
        pass

# Use the custom agent
custom_agent = CustomTreatmentAgent(llm_client)
orchestrator.add_agent(custom_agent)
```

### Data Validation and Quality Control

```python
from core.validators import DataValidator

# Initialize validator with your schema
validator = DataValidator(schema_path="data/schemas/table_schema.json")

# Validate extracted records
for record in extracted_records:
    validation_result = validator.validate_record(record)
    
    if not validation_result.is_valid:
        print(f"Validation errors for {record.id}:")
        for error in validation_result.errors:
            print(f"  - {error}")
    
    # Check data quality
    quality_score = validator.calculate_quality_score(record)
    print(f"Quality score: {quality_score:.2f}/1.0")
```

### Performance Optimization

#### Parallel Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_documents_parallel(file_paths, max_workers=4):
    """Process multiple documents in parallel."""
    
    orchestrator = ExtractionOrchestrator()
    
    # Create semaphore to limit concurrent API calls
    semaphore = asyncio.Semaphore(max_workers)
    
    async def process_single_file(file_path):
        async with semaphore:
            return await orchestrator.extract_from_file(file_path)
    
    # Process all files concurrently
    tasks = [process_single_file(fp) for fp in file_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Collect successful results
    all_records = []
    for result in results:
        if isinstance(result, Exception):
            print(f"Error processing file: {result}")
        elif result.success:
            all_records.extend(result.data)
    
    return all_records

# Usage
file_paths = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
records = await process_documents_parallel(file_paths, max_workers=8)
```

#### Caching

```python
from functools import lru_cache
import hashlib

class CachedOrchestrator(ExtractionOrchestrator):
    """Orchestrator with caching support."""
    
    def __init__(self):
        super().__init__()
        self.cache = {}
    
    def _get_file_hash(self, file_path):
        """Generate hash for file content."""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    async def extract_from_file(self, file_path):
        # Check cache first
        file_hash = self._get_file_hash(file_path)
        if file_hash in self.cache:
            print(f"Using cached result for {file_path}")
            return self.cache[file_hash]
        
        # Process file
        result = await super().extract_from_file(file_path)
        
        # Cache successful results
        if result.success:
            self.cache[file_hash] = result
        
        return result
```

## Data Export and Analysis

### Export Formats

The system supports multiple export formats:

#### CSV Export

```python
# Export all records to CSV
db_manager = SQLiteManager()
export_result = db_manager.export_to_csv("all_patients.csv")

if export_result.success:
    print(f"Exported data to {export_result.data}")
```

#### JSON Export

```python
import json

# Export records as JSON
records_result = db_manager.get_patient_records(limit=1000)
if records_result.success:
    records = records_result.data
    
    with open("patients.json", "w") as f:
        json.dump(records, f, indent=2, default=str)
```

#### Excel Export

```python
import pandas as pd

# Convert to pandas DataFrame and export to Excel
records_result = db_manager.get_patient_records(limit=1000)
if records_result.success:
    df = pd.DataFrame(records_result.data)
    df.to_excel("patients.xlsx", index=False)
```

### Data Analysis Examples

#### Basic Statistics

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load data
records_result = db_manager.get_patient_records(limit=1000)
df = pd.DataFrame(records_result.data)

# Basic statistics
print("Dataset Overview:")
print(f"Total patients: {len(df)}")
print(f"Unique genes: {df['gene'].nunique()}")
print(f"Sex distribution: {df['sex'].value_counts()}")

# Age analysis
print(f"Mean age of onset: {df['age_of_onset'].mean():.1f} years")
print(f"Age range: {df['age_of_onset'].min()}-{df['age_of_onset'].max()} years")

# Gene frequency
gene_counts = df['gene'].value_counts().head(10)
print("Most common genes:")
print(gene_counts)
```

#### Visualization

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Age distribution
plt.figure(figsize=(10, 6))
plt.subplot(2, 2, 1)
df['age_of_onset'].hist(bins=20)
plt.title('Age of Onset Distribution')
plt.xlabel('Age (years)')

# Gene frequency
plt.subplot(2, 2, 2)
gene_counts.head(10).plot(kind='bar')
plt.title('Top 10 Genes')
plt.xticks(rotation=45)

# Sex distribution
plt.subplot(2, 2, 3)
df['sex'].value_counts().plot(kind='pie')
plt.title('Sex Distribution')

# Survival analysis
plt.subplot(2, 2, 4)
survival_data = df[df['survival_status'].notna()]
survival_data['survival_status'].value_counts().plot(kind='bar')
plt.title('Survival Status')

plt.tight_layout()
plt.savefig('patient_analysis.png', dpi=300, bbox_inches='tight')
plt.show()
```

#### Phenotype Analysis

```python
from collections import Counter
import re

# Analyze phenotypes
all_phenotypes = []
for phenotypes in df['phenotypes'].dropna():
    if isinstance(phenotypes, str):
        # Split phenotypes (assuming comma-separated)
        pheno_list = [p.strip() for p in phenotypes.split(',')]
        all_phenotypes.extend(pheno_list)

# Count phenotype frequency
phenotype_counts = Counter(all_phenotypes)
print("Most common phenotypes:")
for phenotype, count in phenotype_counts.most_common(20):
    print(f"{phenotype}: {count}")
```

### Integration with External Tools

#### R Integration

```python
import subprocess
import pandas as pd

# Export data for R analysis
df.to_csv("patients_for_r.csv", index=False)

# Run R script
r_script = """
library(ggplot2)
library(dplyr)

data <- read.csv("patients_for_r.csv")

# Survival analysis
library(survival)
surv_obj <- Surv(data$survival_time, data$survival_status)
fit <- survfit(surv_obj ~ data$gene)

# Plot survival curves
png("survival_curves.png", width=800, height=600)
plot(fit, main="Survival by Gene", xlab="Time (months)", ylab="Survival Probability")
dev.off()
"""

with open("analysis.R", "w") as f:
    f.write(r_script)

subprocess.run(["Rscript", "analysis.R"])
```

#### SPSS Integration

```python
import pyreadstat

# Export to SPSS format
df.to_spss("patients.sav")

# Or use pyreadstat for more control
pyreadstat.write_sav(df, "patients_detailed.sav", 
                     variable_labels={
                         'patient_id': 'Patient Identifier',
                         'gene': 'Primary Gene',
                         'age_of_onset': 'Age at Symptom Onset (years)'
                     })
```

## Troubleshooting

### Common Issues and Solutions

#### 1. API Key Errors

**Problem**: `Authentication failed` or `Invalid API key`

**Solution**:
```bash
# Check if environment variables are set
echo $OPENROUTER_API_KEY

# Verify API key format
# OpenRouter keys start with "sk-or-v1-"
# OpenAI keys start with "sk-"

# Test API connection
python -c "
from core.llm_client.openrouter_client import OpenRouterClient
client = OpenRouterClient()
print('API client initialized successfully')
"
```

#### 2. Memory Issues

**Problem**: `Out of memory` errors with large documents

**Solution**:
```bash
# Reduce batch size
export BATCH_SIZE=5

# Reduce max workers
export MAX_WORKERS=2

# Enable document chunking
export ENABLE_CHUNKING=true
export CHUNK_SIZE=5000
```

#### 3. Slow Processing

**Problem**: Very slow extraction speed

**Solutions**:
```bash
# Increase parallel workers (if you have sufficient RAM)
export MAX_WORKERS=8

# Use faster model (if available)
export DEFAULT_LLM_MODEL=gpt-3.5-turbo

# Enable caching
export ENABLE_CACHING=true
```

#### 4. PDF Parsing Issues

**Problem**: Cannot extract text from PDF

**Solutions**:
```bash
# Install additional PDF tools
pip install pdfplumber PyPDF2 pdfminer.six

# Enable OCR for scanned PDFs
export ENABLE_OCR=true
pip install pytesseract
```

#### 5. Database Errors

**Problem**: SQLite database locked or corrupted

**Solutions**:
```bash
# Check database file permissions
ls -la data/database/

# Reset database
rm data/database/biomedical_data.db
python -c "from database.sqlite_manager import SQLiteManager; SQLiteManager()"

# Use alternative database
export DATABASE_URL=postgresql://user:pass@localhost/biomedical
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set debug level
export LOG_LEVEL=DEBUG

# Run with verbose output
python src/main.py extract --file document.pdf --verbose

# Check log files
tail -f logs/application.log
```

### Performance Monitoring

```python
import time
import psutil
import logging

# Monitor system resources
def monitor_extraction():
    start_time = time.time()
    start_memory = psutil.virtual_memory().used
    
    # Your extraction code here
    result = await orchestrator.extract_from_file("document.pdf")
    
    end_time = time.time()
    end_memory = psutil.virtual_memory().used
    
    processing_time = end_time - start_time
    memory_used = (end_memory - start_memory) / 1024 / 1024  # MB
    
    logging.info(f"Processing time: {processing_time:.2f} seconds")
    logging.info(f"Memory used: {memory_used:.2f} MB")
    
    return result
```

## Best Practices

### Document Preparation

1. **File Quality**: Use high-quality PDFs with selectable text
2. **File Naming**: Use descriptive names including PMID when available
3. **Organization**: Organize documents by study type, disease, or publication year
4. **Preprocessing**: Remove unnecessary pages (references, appendices) to improve processing speed

### Extraction Optimization

1. **Batch Processing**: Process multiple documents together for efficiency
2. **Incremental Processing**: Process new documents incrementally rather than reprocessing everything
3. **Quality Control**: Regularly review extracted data for accuracy
4. **Schema Consistency**: Maintain consistent data schema across extractions

### Data Management

1. **Backup**: Regularly backup your database and extracted data
2. **Version Control**: Track changes to extraction rules and schemas
3. **Documentation**: Document your extraction parameters and any manual corrections
4. **Validation**: Implement validation rules for critical data fields

### API Usage

1. **Rate Limiting**: Respect API rate limits to avoid service interruption
2. **Error Handling**: Implement robust error handling and retry logic
3. **Cost Management**: Monitor API usage to manage costs
4. **Model Selection**: Choose appropriate models based on accuracy vs. cost trade-offs

### Security

1. **API Keys**: Store API keys securely and never commit them to version control
2. **Data Privacy**: Ensure compliance with data privacy regulations
3. **Access Control**: Implement appropriate access controls for sensitive data
4. **Audit Trail**: Maintain logs of data access and modifications

### Collaboration

1. **Shared Configuration**: Use configuration files for team consistency
2. **Data Sharing**: Establish protocols for sharing extracted data
3. **Quality Assurance**: Implement peer review processes for extracted data
4. **Documentation**: Maintain comprehensive documentation for team members

This user guide provides comprehensive information for getting started with and effectively using the Biomedical Data Extraction Engine. For additional support, refer to the API documentation and troubleshooting resources.

