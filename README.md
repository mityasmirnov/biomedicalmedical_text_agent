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

**Built for the medical research community by researchers, for researchers.** 🧬🔬💊

*Empowering precision medicine through intelligent literature analysis.*
