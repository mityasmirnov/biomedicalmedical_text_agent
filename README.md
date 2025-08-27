# 🏥 Biomedical Text Agent - Unified System

A comprehensive, AI-powered system for extracting and analyzing biomedical information from medical literature. This unified system consolidates all functionality into a single, efficient architecture.

## 🚀 **New Unified Architecture**

The Biomedical Text Agent has been completely restructured to provide:

- **Single FastAPI Application** - One backend serving all functionality
- **Consolidated API Endpoints** - All features accessible through unified API
- **Eliminated Duplication** - No more redundant backend systems
- **Streamlined Database** - Single database layer serving all components
- **Unified Frontend** - React frontend with consolidated backend

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

## 📁 **Project Structure**

```
biomedicalmedical_text_agent/
├── src/                          # Main source code
│   ├── api/                      # Unified API layer
│   │   ├── endpoints.py          # All API endpoints
│   │   └── main.py               # API router configuration
│   ├── core/                     # Core system functionality
│   │   ├── unified_orchestrator.py # System coordinator
│   │   ├── config.py             # Configuration management
│   │   └── llm_client/           # LLM integration
│   ├── ui/                       # Frontend only
│   │   ├── frontend/             # React application
│   │   └── config.py             # Frontend configuration
│   ├── metadata_triage/          # Document retrieval & classification
│   ├── langextract_integration/  # Primary extraction engine
│   ├── database/                 # Unified data storage
│   ├── rag/                      # Question answering system
│   └── unified_app.py            # Single FastAPI application
├── start_unified_system.py       # Unified startup script
├── data/                         # Data storage
├── docs/                         # Documentation
└── requirements.txt              # Dependencies
```

## 🚀 **Quick Start**

### 1. **Setup Environment**
```bash
# Clone the repository
git clone <repository-url>
cd biomedicalmedical_text_agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Start the Unified System**
```bash
# Start the complete system
python3 start_unified_system.py

# Or with custom options
python3 start_unified_system.py --host 0.0.0.0 --port 8080 --reload
```

### 3. **Access the System**
- **Frontend**: http://127.0.0.1:8000/
- **API Documentation**: http://127.0.0.1:8000/api/docs
- **Health Check**: http://127.0.0.1:8000/api/health
- **System Status**: http://127.0.0.1:8000/api/v1/system/status

## 🔧 **System Components**

### **Unified API Layer** (`src/api/`)
- **Dashboard Endpoints** - System overview and metrics
- **Agents Endpoints** - AI extraction agent management
- **Documents Endpoints** - Document processing and retrieval
- **Metadata Endpoints** - Metadata browsing and search
- **Extraction Endpoints** - Data extraction from documents
- **Database Endpoints** - Data storage and retrieval
- **RAG Endpoints** - Question answering system

### **Core System** (`src/core/`)
- **Unified Orchestrator** - Coordinates all system components
- **Configuration Management** - Centralized system configuration
- **LLM Integration** - OpenRouter and other LLM providers
- **Logging & Monitoring** - Comprehensive system logging

### **Frontend** (`src/ui/frontend/`)
- **React Application** - Modern, responsive web interface
- **Real-time Updates** - Live system monitoring
- **Interactive Dashboards** - Data visualization and analysis
- **Document Management** - Upload, process, and analyze documents

## 📊 **Key Features**

### **Document Processing**
- **Multi-format Support** - PDF, DOCX, TXT, and more
- **Intelligent Parsing** - Patient segmentation and text extraction
- **Metadata Extraction** - Automatic document classification

### **AI-Powered Extraction**
- **Demographics Agent** - Age, gender, ethnicity extraction
- **Genetics Agent** - Gene variants and mutations
- **Phenotypes Agent** - HPO term identification
- **Treatments Agent** - Medical interventions and procedures

### **Data Management**
- **Unified Database** - SQLite with vector search capabilities
- **Metadata Triage** - Intelligent document prioritization
- **RAG System** - Question answering using extracted data

### **Integration & APIs**
- **PubMed Integration** - Access to biomedical literature
- **Europe PMC Support** - European biomedical database
- **Ontology Integration** - HPO and gene normalization

## 🧪 **Testing**

### **System Health Check**
```bash
# Check system configuration
python3 start_unified_system.py --check

# Run comprehensive tests
python3 test_unified_system.py
```

### **API Testing**
```bash
# Test individual endpoints
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/v1/system/status
```

## 📈 **Performance & Scalability**

- **Unified Architecture** - Eliminates duplicate operations
- **Efficient Database** - Optimized queries and indexing
- **Async Processing** - Non-blocking operations
- **Resource Management** - Intelligent memory and CPU usage

## 🔒 **Security & Privacy**

- **Data Isolation** - Secure document processing
- **API Authentication** - Configurable access control
- **Audit Logging** - Complete operation tracking
- **Privacy Compliance** - HIPAA-ready data handling

## 🤝 **Contributing**

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

## 📚 **Documentation**

- **API Documentation**: http://127.0.0.1:8000/api/docs
- **Implementation Guide**: [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **Restructuring Plan**: [RESTRUCTURING_PLAN.md](RESTRUCTURING_PLAN.md)
- **File Organization**: [FILE_ORGANIZATION.md](FILE_ORGANIZATION.md)

## 🆘 **Support**

- **Issues**: GitHub Issues
- **Documentation**: Comprehensive guides in `/docs`
- **Examples**: Sample data and usage in `/notebooks`

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎯 **What's New in v2.0**

✅ **Unified Architecture** - Single backend system  
✅ **Consolidated APIs** - All endpoints in one place  
✅ **Eliminated Duplication** - No more redundant components  
✅ **Streamlined Database** - Unified data storage  
✅ **Modern Frontend** - React with real-time updates  
✅ **Comprehensive Testing** - Full system validation  

---

*Built with ❤️ for the biomedical research community*
