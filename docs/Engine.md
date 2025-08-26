# Biomedical Data Extraction Engine

A comprehensive AI-powered system for extracting structured patient-level data from biomedical literature, designed for clinical research, systematic reviews, and medical database creation.

## 🎯 Overview

The Biomedical Data Extraction Engine transforms unstructured medical literature into structured, queryable patient data using advanced AI agents, medical ontologies, and retrieval-augmented generation (RAG). Built specifically for researchers, clinicians, and data scientists working with biomedical literature.

### Key Capabilities

- **🤖 Multi-Agent Architecture**: Specialized AI agents for demographics, genetics, phenotypes, treatments, and outcomes
- **📄 Document Processing**: Support for PDF, HTML, XML, and text documents with intelligent patient segmentation
- **🧬 Medical Ontology Integration**: HPO (Human Phenotype Ontology) and HGNC gene normalization
- **🗄️ Dual Database System**: SQLite for structured queries and vector database for semantic search
- **🔍 RAG-Powered Q&A**: Natural language querying over extracted medical data
- **⚡ Batch Processing**: Efficient parallel processing of multiple documents
- **📊 Export & Analysis**: Multiple output formats with built-in analysis tools

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd biomedical_extraction_engine

# Install dependencies
pip install -r requirements.txt

# Optional: Install ML libraries for enhanced performance
pip install sentence-transformers faiss-cpu scikit-learn
```

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

## 📈 Performance and Scalability

### Benchmarks

| Document Type | Processing Time | Memory Usage | Accuracy |
|---------------|----------------|--------------|----------|
| Single PDF (10 pages) | ~30 seconds | ~200MB | 85-92% |
| Batch (100 PDFs) | ~45 minutes | ~1GB | 83-90% |
| Large Document (50+ pages) | ~2 minutes | ~500MB | 80-88% |

### Optimization Tips

1. **Parallel Processing**: Use `MAX_WORKERS=8` for multi-core systems
2. **Batch Processing**: Process multiple documents together
3. **Caching**: Enable result caching for repeated processing
4. **Model Selection**: Use faster models for large-scale processing
5. **Memory Management**: Adjust batch size based on available RAM

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

## 📚 Documentation

- **[API Documentation](docs/API_DOCUMENTATION.md)**: Complete API reference
- **[User Guide](docs/USER_GUIDE.md)**: Comprehensive usage guide
- **[Architecture Overview](docs/ARCHITECTURE.md)**: System design details
- **[Troubleshooting Guide](docs/USER_GUIDE.md#troubleshooting)**: Common issues and solutions

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone for development
git clone <repository-url>
cd biomedical_extraction_engine

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 src/
black src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Check the [User Guide](docs/USER_GUIDE.md) for detailed instructions
- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and community support

### Common Issues

| Issue | Solution |
|-------|----------|
| API Key Errors | Verify environment variables are set correctly |
| Memory Issues | Reduce `BATCH_SIZE` and `MAX_WORKERS` |
| Slow Processing | Use faster models or enable parallel processing |
| PDF Parsing Errors | Install additional PDF libraries or enable OCR |

### Performance Monitoring

```bash
# Monitor system resources during processing
python -c "
import psutil
import time

def monitor():
    while True:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        print(f'CPU: {cpu}%, Memory: {memory}%')
        time.sleep(5)

monitor()
"
```

## 🎯 Roadmap

### Current Version (v1.0)
- ✅ Multi-agent extraction system
- ✅ HPO and HGNC ontology integration
- ✅ RAG-based question answering
- ✅ SQLite and vector database support
- ✅ Comprehensive testing suite

### Upcoming Features (v1.1)
- 🔄 ClinicalTrials.gov integration
- 🔄 Patent repository support
- 🔄 Enhanced OCR capabilities
- 🔄 Web-based user interface
- 🔄 Advanced analytics dashboard

### Future Enhancements (v2.0)
- 🔮 Real-time literature monitoring
- 🔮 Federated learning capabilities
- 🔮 Multi-language support
- 🔮 Cloud deployment options
- 🔮 API service offering

---

**Built with ❤️ for the biomedical research community**

*Transform your literature into structured knowledge with AI-powered precision.*

