# 🏥 Biomedical Text Agent - Unified System

> **AI-Powered Biomedical Literature Analysis & Patient Data Extraction**

A comprehensive system for processing biomedical literature, extracting patient information, and providing intelligent search and analysis capabilities for medical researchers, clinicians, and bioinformaticians.

## 🎯 **What This System Does**

The Biomedical Text Agent is designed to bridge the gap between **published medical literature** and **clinical data extraction**. It helps researchers:

- **🔍 Search & Discover** relevant medical papers from PubMed/Europe PMC
- **📄 Process Full-Text** documents (PDFs, research papers, case reports)
- **👥 Extract Patient Data** including demographics, genetics, phenotypes, and treatments
- **🧬 Analyze Genetic Information** with HPO and gene ontology integration
- **💊 Identify Treatment Patterns** across patient populations
- **📊 Build Knowledge Bases** for rare diseases and genetic conditions

## 🏗️ **System Architecture**


```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BIOMEDICAL TEXT AGENT - UNIFIED ARCHITECTURE            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DATA SOURCES  │    │  METADATA       │    │  DOCUMENT      │
│                 │    │  TRIAGE         │    │  PROCESSING    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • PubMed API    │───▶│ • Orchestrator  │───▶│ • PDF Parser   │
│ • Europe PMC    │    │ • Classifier    │    │ • Patient      │
│ • Local Files   │    │ • Concept       │    │   Segmenter    │
│ • Uploads       │    │   Scorer        │    │ • Text         │
└─────────────────┘    │ • Deduplicator  │    │   Extractor    │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED EXTRACTION PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ • LangExtract Engine (Primary Extractor)                                  │
│ • AI Agents (Demographics, Genetics, Phenotypes, Treatments)              │
│ • Ontology Integration (HPO, Gene Normalization)                          │
│ • Validation & Quality Control                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED DATA STORAGE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ • SQLite Database (Structured Patient Records)                            │
│ • Vector Database (FAISS for Semantic Search)                             │
│ • Metadata Store (Document & Processing Info)                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED ACCESS LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ • REST API (FastAPI)                                                      │
│ • RAG System (Question Answering)                                         │
│ • CLI Interface (Command Line)                                            │
│ • Web UI (React Frontend)                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Start**

### **1. Start the System**
```bash
# Activate virtual environment
source venv/bin/activate

# Start unified system
python start_unified_system.py
```

### **2. Access the System**
- **🌐 Frontend**: http://127.0.0.1:8000/
- **📚 API Docs**: http://127.0.0.1:8000/api/docs
- **💚 Health Check**: http://127.0.0.1:8000/api/health

### **3. First Steps**
1. **Search Literature**: Use the metadata search to find relevant papers
2. **Download Papers**: Get full-text documents from PubMed/Europe PMC
3. **Process Documents**: Upload PDFs for AI-powered extraction
4. **Analyze Data**: View extracted patient information and patterns

## 🔬 **Biological & Medical Applications**

### **Rare Disease Research**
- **Leigh Syndrome**: Mitochondrial disorders, genetic mutations
- **Genetic Conditions**: Gene-phenotype correlations, inheritance patterns
- **Case Report Analysis**: Patient presentation patterns, treatment outcomes

### **Clinical Data Mining**
- **Patient Demographics**: Age, sex, ethnicity, consanguinity
- **Genetic Markers**: Gene mutations, inheritance patterns, zygosity
- **Phenotypic Features**: HPO terms, clinical manifestations
- **Treatment Outcomes**: Medication responses, therapeutic strategies

### **Research Applications**
- **Literature Reviews**: Systematic analysis of published research
- **Meta-Analysis**: Cross-study patient data aggregation
- **Drug Discovery**: Treatment pattern identification
- **Biomarker Research**: Phenotype-genotype correlations

## 📁 **Project Structure**

```
biomedicalmedical_text_agent/
├── 🚀 start_unified_system.py    # Main entry point
├── 📚 src/                       # Core system source code
├── 🧪 tests/                     # Comprehensive test suite
├── 📖 docs/                      # Project documentation
├── 🛠️ scripts/                   # Utility scripts & demos
├── 📊 data/                      # Data storage & samples
├── 🌐 venv/                      # Python virtual environment
└── 📋 Configuration files        # Requirements, setup, env
```

## 🧪 **Testing**

```bash
# Run all tests
python tests/run_tests.py

# Run specific test categories
pytest tests/unit/ -v          # Component tests
pytest tests/integration/ -v   # Integration tests
pytest tests/e2e/ -v          # End-to-end tests
```

## 🔧 **Development**

### **Prerequisites**
- Python 3.11+
- Virtual environment
- Required packages (see `requirements.txt`)

### **Setup**
```bash
# Clone repository
git clone <repository-url>
cd biomedicalmedical_text_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development
python start_unified_system.py --reload
```

## 📊 **System Capabilities**

| **Feature** | **Description** | **Medical Use Case** |
|-------------|-----------------|----------------------|
| **PubMed Integration** | Search & download research papers | Literature review, case discovery |
| **AI Extraction** | Extract patient data from documents | Clinical data mining, research synthesis |
| **HPO Integration** | Human Phenotype Ontology mapping | Phenotype classification, rare disease diagnosis |
| **Gene Analysis** | Genetic variant analysis | Genotype-phenotype correlation |
| **Treatment Analysis** | Medication & therapy extraction | Treatment pattern identification |
| **RAG System** | Intelligent question answering | Clinical decision support, research queries |

## 🤝 **Contributing**

1. **Fork** the repository
2. **Create** a feature branch
3. **Add** tests for new functionality
4. **Ensure** all tests pass
5. **Submit** a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

- **Documentation**: Check the `docs/` folder
- **Issues**: Report bugs via GitHub Issues
- **Questions**: Open a GitHub Discussion

---

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here  # Free tier available
OPENAI_API_KEY=sk-your-openai-key-here          # Optional, for better performance
```

### Basic Usage

```bash
# Extract data from a single document
python src/main.py extract --file "path/to/paper.pdf" --output "results.csv"

# Process multiple documents
python src/main.py batch --input-dir "papers/" --output "batch_results.csv"

# Ask questions about your data
python src/main.py rag --question "What genes are associated with Leigh syndrome?"

# Test the system
python test_system.py
```

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Document Input Layer                     │
├─────────────────────────────────────────────────────────────┤
│  PDF Parser  │  HTML Parser  │  XML Parser  │  Text Parser  │
├─────────────────────────────────────────────────────────────┤
│                 Patient Segmentation                        │
├─────────────────────────────────────────────────────────────┤
│              Multi-Agent Extraction Layer                   │
│  Demographics │  Genetics  │  Phenotypes │  Treatments │... │
├─────────────────────────────────────────────────────────────┤
│                 Ontology Integration                        │
│      HPO Manager      │      Gene Manager (HGNC)           │
├─────────────────────────────────────────────────────────────┤
│                   Storage Layer                             │
│    SQLite Database    │    Vector Database (FAISS)         │
├─────────────────────────────────────────────────────────────┤
│                    RAG System                               │
│  Retrieval Engine  │  Question Answering  │  Context Gen   │
└─────────────────────────────────────────────────────────────┘
```

### Core Modules

- **`agents/`**: AI extraction agents and orchestration
- **`processors/`**: Document parsing and patient segmentation
- **`database/`**: SQLite and vector database management
- **`ontologies/`**: HPO and HGNC normalization
- **`rag/`**: Retrieval-augmented generation system
- **`core/`**: Configuration, logging, and base classes

## 📊 Data Schema

The system extracts comprehensive patient information following a standardized schema:

### Patient Record Structure

```json
{
  "patient_id": "Patient_1",
  "demographics": {
    "sex": 1,
    "age_of_onset": 2.5,
    "age_at_diagnosis": 3.0,
    "ethnicity": "Chinese",
    "consanguinity": 0
  },
  "genetics": {
    "gene": "SURF1",
    "mutations": "c.312delG",
    "inheritance": "autosomal recessive",
    "zygosity": "homozygous"
  },
  "phenotypes": {
    "hpo_terms": ["HP:0001250", "HP:0001263"],
    "symptoms": ["seizures", "developmental delay"],
    "diagnostic_findings": "elevated lactate"
  },
  "treatments": {
    "medications": ["thiamine", "coenzyme Q10"],
    "dosages": ["100mg daily", "50mg twice daily"],
    "response": "partial improvement"
  },
  "outcomes": {
    "survival_status": 1,
    "survival_time": 24,
    "clinical_outcome": "stable condition"
  }
}
```

### Supported Fields

| Category | Fields | Description |
|----------|--------|-------------|
| **Demographics** | sex, age_of_onset, age_at_diagnosis, ethnicity, consanguinity | Basic patient information |
| **Genetics** | gene, mutations, inheritance, zygosity, genetic_testing | Genetic information and testing |
| **Phenotypes** | phenotypes, symptoms, diagnostic_findings, lab_values | Clinical presentations and findings |
| **Treatments** | treatments, medications, dosages, treatment_response | Therapeutic interventions |
| **Outcomes** | survival_status, survival_time, clinical_outcome | Patient outcomes and follow-up |

## 💻 Usage Examples

### Python API

```python
import asyncio
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
from database.sqlite_manager import SQLiteManager
from rag.rag_system import RAGSystem

async def comprehensive_extraction():
    # Initialize components
    orchestrator = ExtractionOrchestrator()
    db_manager = SQLiteManager()
    rag_system = RAGSystem()
    
    # Extract data from document
    result = await orchestrator.extract_from_file("paper.pdf")
    
    if result.success:
        records = result.data
        print(f"✅ Extracted {len(records)} patient records")
        
        # Store in database
        store_result = db_manager.store_patient_records(records)
        if store_result.success:
            print(f"✅ Stored records in database")
        
        # Ask questions about the data
        answer = await rag_system.answer_question(
            "What are the most common symptoms in these patients?"
        )
        if answer.success:
            print(f"🤖 Answer: {answer.data['answer']}")
    
    else:
        print(f"❌ Extraction failed: {result.error}")

# Run the extraction
asyncio.run(comprehensive_extraction())
```

### Command Line Interface

```bash
# Single document extraction
python src/main.py extract \
    --file "PMID32679198.pdf" \
    --output "extracted_data.csv" \
    --format csv

# Batch processing with parallel workers
python src/main.py batch \
    --input-dir "literature_papers/" \
    --output "batch_results.csv" \
    --workers 8 \
    --pattern "*.pdf"

# Database operations
python src/main.py db stats                    # View database statistics
python src/main.py db search --query "SURF1"  # Search records
python src/main.py db export --output all.csv # Export all data

# Interactive question answering
python src/main.py rag --interactive

# System testing
python test_system.py
```

### Ontology Normalization

```python
from ontologies.hpo_manager import HPOManager
from ontologies.gene_manager import GeneManager

# Initialize ontology managers
hpo_manager = HPOManager()
gene_manager = GeneManager()

# Normalize phenotypes to HPO terms
phenotypes = ["seizures", "developmental delay", "muscle weakness"]
hpo_result = hpo_manager.batch_normalize_phenotypes(phenotypes)

for normalized in hpo_result.data:
    if normalized['best_match']:
        match = normalized['best_match']
        print(f"{normalized['original_text']} → {match['hpo_id']}: {match['hpo_name']}")

# Normalize gene symbols to HGNC standards
genes = ["SURF1", "surf1", "NDUFS1", "brca1"]
gene_result = gene_manager.batch_normalize_genes(genes)

for normalized in gene_result.data:
    print(f"{normalized['original_symbol']} → {normalized['normalized_symbol']} "
          f"(confidence: {normalized['confidence']:.2f})")
```

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
OPENROUTER_API_KEY=sk-or-v1-your-key           # Primary LLM provider (free tier)
OPENAI_API_KEY=sk-your-openai-key              # Alternative provider
HUGGINGFACE_API_TOKEN=hf_your-token            # Local models

# Processing Configuration
MAX_WORKERS=4                                   # Parallel processing workers
BATCH_SIZE=10                                   # Documents per batch
DEFAULT_LLM_MODEL=deepseek/deepseek-chat-v3-0324:free
LLM_TEMPERATURE=0.0                            # Response determinism
LLM_MAX_TOKENS=2000                            # Maximum response length

# Storage Configuration
DATABASE_URL=sqlite:///data/database/biomedical_data.db
DATA_DIR=./data
OUTPUT_DIR=./data/output

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/application.log
```

### Advanced Configuration

Create a `config.yaml` file for complex setups:

```yaml
llm:
  default_model: "deepseek/deepseek-chat-v3-0324:free"
  temperature: 0.0
  max_tokens: 2000
  timeout: 60

processing:
  max_workers: 8
  batch_size: 20
  enable_ocr: false
  chunk_size: 5000

database:
  url: "sqlite:///data/database/biomedical_data.db"
  enable_wal: true
  
ontologies:
  hpo_data_path: "./data/ontologies/hpo"
  gene_data_path: "./data/ontologies/genes"
  
rag:
  max_context_docs: 10
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
```

## 🧪 Testing and Validation

### Comprehensive Test Suite

```bash
# Run all tests
python test_system.py

# Test specific components
python -m pytest tests/test_extraction.py
python -m pytest tests/test_database.py
python -m pytest tests/test_ontologies.py
```

### Ground Truth Validation

The system includes validation against manually curated data:

```python
# Compare with ground truth
from tests.validation import GroundTruthValidator

validator = GroundTruthValidator("data/ground_truth/manually_processed.csv")
validation_result = validator.validate_extraction_results(extracted_records)

print(f"Accuracy: {validation_result.accuracy:.2f}")
print(f"Field coverage: {validation_result.field_coverage}")
```



## 🔍 Advanced Features

### RAG-Powered Question Answering

```python
# Ask complex questions about your data
questions = [
    "What is the average age of onset for SURF1 mutations?",
    "Which treatments show the best outcomes for Leigh syndrome?",
    "How many patients had both seizures and developmental delay?",
    "What is the survival rate by gene mutation?",
    "Which phenotypes are most commonly associated with mitochondrial diseases?"
]

for question in questions:
    result = await rag_system.answer_question(question)
    if result.success:
        print(f"Q: {question}")
        print(f"A: {result.data['answer']}")
        print(f"Sources: {len(result.data['sources'])} documents")
        print("-" * 60)
```

### Custom Extraction Agents

```python
# Create specialized agents for specific data types
from agents.base_agent import BaseExtractionAgent

class CustomBiomarkerAgent(BaseExtractionAgent):
    """Extract biomarker information."""
    
    async def execute(self, patient_segment, context):
        prompt = f"""
        Extract biomarker information from this patient case:
        {patient_segment}
        
        Focus on:
        - Laboratory values (lactate, pyruvate, etc.)
        - Imaging biomarkers
        - Genetic biomarkers
        - Metabolic markers
        """
        
        result = await self.llm_client.generate(prompt)
        return self.process_biomarker_data(result.data)

# Add to orchestrator
orchestrator.add_agent(CustomBiomarkerAgent(llm_client))
```

### Data Export and Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt

# Export and analyze data
records_result = db_manager.get_patient_records(limit=1000)
df = pd.DataFrame(records_result.data)

# Generate insights
print(f"Total patients: {len(df)}")
print(f"Unique genes: {df['gene'].nunique()}")
print(f"Most common phenotypes: {df['phenotypes'].value_counts().head()}")

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Age distribution
df['age_of_onset'].hist(ax=axes[0,0], bins=20)
axes[0,0].set_title('Age of Onset Distribution')

# Gene frequency
df['gene'].value_counts().head(10).plot(kind='bar', ax=axes[0,1])
axes[0,1].set_title('Most Common Genes')

# Sex distribution
df['sex'].value_counts().plot(kind='pie', ax=axes[1,0])
axes[1,0].set_title('Sex Distribution')

# Survival analysis
survival_data = df[df['survival_status'].notna()]
survival_data.groupby('gene')['survival_time'].mean().plot(kind='bar', ax=axes[1,1])
axes[1,1].set_title('Average Survival Time by Gene')

plt.tight_layout()
plt.savefig('patient_analysis.png', dpi=300)
```

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





## 🎯 Roadmap

### Current Version (v1.0)
- ✅ Multi-agent extraction system
- ✅ RAG-based question answering
- ✅ SQLite and vector database support
- ✅ Comprehensive testing suite


### Upcoming Features (v1.1)
- 🔄 Fix HPO and HGNC ontology integration
- 🔄 ClinicalTrials.gov integration
- 🔄 Patent repository support
- 🔄 Enhanced OCR capabilities
- 🔄 Web-based user interface
- 🔄 Advanced analytics dashboard



**Built with ❤️ for the medical research community by researchers, for researchers.** 🧬🔬💊

*Developed by Sima Smirnov.*
