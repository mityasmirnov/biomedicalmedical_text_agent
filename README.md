# 🏥 Biomedical Text Agent

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

## 🔄 **Recent Consolidation (v2.0)**

The system has been recently consolidated to eliminate redundancy and provide a cleaner, more maintainable codebase:

### **✅ What Was Consolidated**
- **PubMed Client**: Unified with enhanced implementation internally
- **HPO Manager**: Unified with optimized implementation internally  
- **Extraction Orchestrator**: Unified with enhanced implementation internally
- **Metadata Orchestrator**: Unified with both implementations available
- **Startup Scripts**: Single `start_system.py` replaces multiple startup files
- **Package Files**: Consolidated frontend dependencies into single `package.json`
- **UI Components**: Enhanced React components with Material-UI integration

### **🎯 Benefits of Consolidation**
- **Single Source of Truth**: No more confusion about which implementation to use
- **Automatic Enhancement**: Users get enhanced features when available
- **Graceful Fallbacks**: Basic implementations available when enhanced versions unavailable
- **Cleaner Project Structure**: Eliminated redundant files and scripts
- **Better User Experience**: Single startup script with clear options
- **Maintained Compatibility**: All existing code continues to work

### **🔧 Recent Fixes (v2.1)**
- **✅ HPO Data Path**: Fixed path from `data/ontologies/hp.json` to `data/ontologies/hpo/hp.json`
- **✅ HPO Manager**: Fixed fallback to basic mappings when enhanced data unavailable
- **✅ Gene Manager**: Updated to return `ProcessingResult` objects for consistency
- **✅ Import Paths**: Fixed relative import issues in multiple modules
- **✅ LLM Provider**: Now correctly shows "openrouter" instead of "Unknown"
- **✅ Backend Startup**: Fixed import and port conflict issues

### **📁 Current Clean Structure**
```
biomedicalmedical_text_agent/
├── start_system.py                    # ✅ Single unified startup script
├── demo_leigh_syndrome_search.py      # ✅ Essential demo for UI testing
├── demo_leigh_syndrome_search_standalone.py  # ✅ Standalone demo variant
├── CONSOLIDATION_SUMMARY.md           # ✅ Complete consolidation documentation
├── test_simple.py                     # ✅ Simple test script for core functionality
└── src/
    ├── metadata_triage/
    │   ├── pubmed_client.py              # ✅ Unified (uses enhanced internally)
    │   ├── metadata_orchestrator.py      # ✅ Unified (both implementations)
    │   └── enhanced_metadata_orchestrator.py  # ⚠️  Internal (will be refactored)
    ├── ontologies/
    │   ├── hpo_manager.py                # ✅ Unified (uses optimized internally)
    │   ├── hpo_manager_basic.py          # ✅ Fallback implementation
    │   └── gene_manager.py               # ✅ Fixed to use ProcessingResult
    └── agents/orchestrator/
        ├── extraction_orchestrator.py    # ✅ Unified (uses enhanced internally)
        └── extraction_orchestrator_basic.py  # ✅ Fallback implementation
```

## 🚀 **Quick Start**

### **1. Start the Unified System**
```bash
# Activate virtual environment
source venv/bin/activate

# Start the complete system
python start_system.py

# Check system requirements
python start_system.py check

# Build frontend (if needed)
python start_system.py build
```

### **2. Access the System**
- **🌐 Frontend**: http://127.0.0.1:8000/
- **📚 API Docs**: http://127.0.0.1:8000/api/docs
- **💚 Health Check**: http://127.0.0.1:8000/api/health

### **3. Test the System**
```bash
# Run Leigh syndrome demo
python demo_leigh_syndrome_search.py

# Run standalone demo
python demo_leigh_syndrome_search_standalone.py

# Test system components
python test_system.py
```

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
├── 🚀 start_enhanced_system.py      # Enhanced system entry point (RECOMMENDED)
├── 🚀 start_unified_system.py       # Legacy unified system entry point
├── 🖥️ standalone_server.py           # Standalone API server
├── 🧪 test_system.py                # Comprehensive system test
├── 🧪 test_enhanced_metadata_triage.py    # Enhanced metadata triage tests
├── 🧪 test_standalone_metadata_triage.py  # Standalone metadata triage tests
├── 🎯 demo_enhanced_metadata_triage.py    # Enhanced metadata triage demo
├── 🎯 demo_leigh_syndrome_search.py       # Leigh syndrome search demo
├── 📚 src/                          # Core system source code
├── 🧪 tests/                        # Comprehensive test suite
├── 📖 docs/                         # Project documentation
├── 🛠️ scripts/                      # Utility scripts & demos
├── 📊 data/                         # Data storage & samples
├── 🌐 venv/                         # Python virtual environment
└── 📋 Configuration files           # Requirements, setup, env
```

## 🧪 **Testing**

```bash
# Run enhanced system demonstration (RECOMMENDED)
python start_enhanced_system.py demo

# Run comprehensive system test
python test_system.py

# Test enhanced metadata triage
python test_enhanced_metadata_triage.py

# Test standalone metadata triage
python test_standalone_metadata_triage.py

# Run Leigh syndrome search demo
python demo_leigh_syndrome_search.py

# Run specific test categories
pytest tests/unit/ -v          # Component tests
pytest tests/integration/ -v   # Integration tests
pytest tests/e2e/ -v          # End-to-end tests
```

## 🔧 **Development Setup**

### **Prerequisites**
- Python 3.11+
- Virtual environment
- Required packages (see `requirements.txt`)

### **Installation**
```bash
# Clone repository
git clone <repository-url>
cd biomedicalmedical_text_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional required packages
pip install langextract

# Test enhanced system (RECOMMENDED)
python start_enhanced_system.py demo

# Test legacy system
python test_system.py
```

## 🚀 **Enhanced System Features (Currently Working)**

The enhanced system has been successfully integrated and tested with the following working features:

| **Feature** | **Status** | **Description** | **Medical Use Case** |
|-------------|------------|-----------------|----------------------|
| **Enhanced Document Management** | ✅ Working | Create, store, and manage biomedical documents | Clinical data organization |
| **Enhanced Extraction Pipeline** | ✅ Working | AI-powered extraction with LangExtract integration | Patient data extraction |
| **Enhanced Analytics** | ✅ Working | Comprehensive metrics and performance tracking | Research analytics |
| **Enhanced Relationships** | ✅ Working | Entity relationship mapping and analysis | Clinical correlation analysis |
| **Enhanced Search** | ✅ Working | Advanced document search with filtering | Literature discovery |
| **Enhanced Database** | ✅ Working | SQLite with enhanced schemas and performance | Data storage and retrieval |
| **Enhanced Pipeline** | ✅ Working | Asynchronous processing with worker management | Scalable data processing |

## 📊 **Legacy System Capabilities**

| **Feature** | **Description** | **Medical Use Case** |
|-------------|-----------------|----------------------|
| **PubMed Integration** | Search & download research papers | Literature review, case discovery |
| **AI Extraction** | Extract patient data from documents | Clinical data mining, research synthesis |
| **HPO Integration** | Human Phenotype Ontology mapping | Phenotype classification, rare disease diagnosis |
| **Gene Analysis** | Genetic variant analysis | Genotype-phenotype correlation |
| **Treatment Analysis** | Medication & therapy extraction | Treatment pattern identification |
| **RAG System** | Intelligent question answering | Clinical decision support, research queries |

## 🎯 **Current System Status**

### **Recent Accomplishments**
- ✅ **Successfully merged all enhanced feature branches** from Cursor development
- ✅ **Integrated enhanced metadata orchestrator** with PubMed client synchronization
- ✅ **Added comprehensive UI components** (APIManager, EnhancedDashboard, DataVisualization, etc.)
- ✅ **Enhanced backend API structure** for UI integration
- ✅ **Integrated enhanced LangExtract** with UI support and validation interface
- ✅ **Fixed all async context manager issues** for database compatibility
- ✅ **System fully functional** with enhanced processing pipeline

### **System Architecture**
The enhanced system now includes:
- **Enhanced Metadata Orchestrator**: Advanced pipeline management with async workers
- **Enhanced SQLite Manager**: Comprehensive database with enhanced schemas
- **Enhanced LangExtract Integration**: AI-powered extraction with UI support
- **Enhanced API Endpoints**: RESTful API with proper request/response models
- **Enhanced Processing Pipeline**: Asynchronous task processing with monitoring

## 💻 **Usage Examples**

### **Command Line Interface**

The system provides multiple entry points for different use cases:

#### **Enhanced System (RECOMMENDED)**
```bash
# Run enhanced system demonstration
python start_enhanced_system.py demo

# Start enhanced system server
python start_enhanced_system.py server

# Test enhanced metadata triage
python test_enhanced_metadata_triage.py
```

#### **Legacy System**
```bash
# Start unified system
python start_unified_system.py

# Start standalone server
python standalone_server.py

# Run comprehensive tests
python test_system.py
```

#### **Demo Scripts**
```bash
# Leigh syndrome search demo
python demo_leigh_syndrome_search.py

# Enhanced metadata triage demo
python demo_enhanced_metadata_triage.py

# Standalone metadata triage demo
python test_standalone_metadata_triage.py
```

### **Python API Usage**

#### **Basic Extraction**
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

#### **Database Integration**
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
```

#### **RAG System**
```python
from rag.rag_system import RAGSystem

# Initialize RAG system
rag_system = RAGSystem()

# Ask questions about your data
questions = [
    "What are the most common symptoms of Leigh syndrome?",
    "Which genes are frequently mutated in mitochondrial diseases?",
    "What treatments show the best outcomes?"
]

for question in questions:
    result = await rag_system.answer_question(question)
    if result.success:
        answer_data = result.data
        print(f"Q: {question}")
        print(f"A: {answer_data['answer']}")
        print(f"Sources: {len(answer_data['sources'])} documents")
        print("-" * 50)
```

#### **Ontology Normalization**
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
genes = ["SURF1", "surf1", "NDUFS1"]
gene_result = gene_manager.batch_normalize_genes(genes)

for normalized in gene_result.data:
    print(f"{normalized['original_symbol']} → {normalized['normalized_symbol']} "
          f"(confidence: {normalized['confidence']:.2f})")
```

## 🔧 **Configuration**

### **Environment Variables**

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

### **Advanced Configuration**

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

## 📊 **Data Schema**

The system extracts comprehensive patient information following a standardized schema:

### **Patient Record Structure**

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

### **Supported Fields**

| Category | Fields | Description |
|----------|--------|-------------|
| **Demographics** | sex, age_of_onset, age_at_diagnosis, ethnicity, consanguinity | Basic patient information |
| **Genetics** | gene, mutations, inheritance, zygosity, genetic_testing | Genetic information and testing |
| **Phenotypes** | phenotypes, symptoms, diagnostic_findings, lab_values | Clinical presentations and findings |
| **Treatments** | treatments, medications, dosages, treatment_response | Therapeutic interventions |
| **Outcomes** | survival_status, survival_time, clinical_outcome | Patient outcomes and follow-up |

## 🔍 **Advanced Features**

### **RAG-Powered Question Answering**

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

### **Custom Extraction Agents**

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

### **Data Export and Analysis**

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

## 🧪 **Testing and Validation**

### **Comprehensive Test Suite**

```bash
# Run all tests
python test_system.py

# Test specific components
python -m pytest tests/test_extraction.py
python -m pytest tests/test_database.py
python -m pytest tests/test_ontologies.py
```

### **Ground Truth Validation**

The system includes validation against manually curated data:

```python
# Compare with ground truth
from tests.validation import GroundTruthValidator

validator = GroundTruthValidator("data/ground_truth/manually_processed.csv")
validation_result = validator.validate_extraction_results(extracted_records)

print(f"Accuracy: {validation_result.accuracy:.2f}")
print(f"Field coverage: {validation_result.field_coverage}")
```

## 🔧 **Performance Optimization**

### **Parallel Processing**

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

### **Caching**

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

## 🎯 **Roadmap**

### **Current Version (v2.0)**
- ✅ Multi-agent extraction system
- ✅ RAG-based question answering
- ✅ SQLite and vector database support
- ✅ Comprehensive testing suite
- ✅ Unified CLI interface
- ✅ FastAPI backend with React frontend

### **Upcoming Features (v2.1)**
- 🔄 Enhanced HPO and HGNC ontology integration
- 🔄 ClinicalTrials.gov integration
- 🔄 Patent repository support
- 🔄 Advanced OCR capabilities
- 🔄 Machine learning model training
- 🔄 Real-time collaboration features

---

**Built with ❤️ for the medical research community by researchers, for researchers.** 🧬🔬💊

*Developed by Sima Smirnov.*
