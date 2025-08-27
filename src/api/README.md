# 🌐 API Module - Biomedical Text Agent

> **Communication Interface: REST API Endpoints for Medical Research & Data Access**

The API module provides the **"nervous system"** of the Biomedical Text Agent, enabling external systems, researchers, and applications to interact with the system's medical data processing capabilities through standardized REST endpoints.

## 🏗️ **Biological Purpose & Architecture**

### **Nervous System Analogy**
Like the human nervous system, the API module:
- **Receives** requests from external sources (like sensory input)
- **Processes** requests through appropriate systems (like neural processing)
- **Returns** structured responses (like motor output)
- **Coordinates** multiple internal systems (like central nervous system)

## 📁 **Module Components & Medical Context**

### **🔌 API Endpoints** (`endpoints.py`)
**Biological Purpose**: "Sensory receptors" that receive and route different types of requests

#### **Dashboard Endpoints** (`/dashboard/*`)
- **Function**: System overview and real-time monitoring
- **Medical Analogy**: Like **vital signs monitor** in clinical settings
- **Key Endpoints**:
  - `/dashboard/overview` - System health and performance metrics
  - `/dashboard/ws` - WebSocket for real-time updates
  - `/dashboard/metrics` - Processing statistics and analytics

**Medical Use Case**: Monitoring system performance during large-scale research operations

#### **Metadata Endpoints** (`/metadata/*`)
- **Function**: Literature search and document management
- **Medical Analogy**: Like **medical library system** for research papers
- **Key Endpoints**:
  - `/metadata/search` - Search PubMed, Europe PMC, and local databases
  - `/metadata/collections/{name}/documents` - Access organized research collections
  - `/metadata/download-document` - Download full-text articles
  - `/metadata/stored-documents` - Access locally stored documents

**Medical Use Case**: Literature review, case discovery, and research paper retrieval

#### **Documents Endpoints** (`/documents/*`)
- **Function**: Document processing and AI extraction
- **Medical Analogy**: Like **laboratory processing** of medical samples
- **Key Endpoints**:
  - `/documents/upload` - Upload medical documents for processing
  - `/documents/process` - AI-powered extraction from documents
  - `/documents/status` - Processing status and progress tracking
  - `/documents/results` - Extracted patient data and analysis

**Medical Use Case**: Processing case reports, research papers, and clinical documents

#### **Extraction Endpoints** (`/extraction/*`)
- **Function**: AI-powered data extraction and analysis
- **Medical Analogy**: Like **diagnostic testing** in clinical laboratories
- **Key Endpoints**:
  - `/extraction/extract` - Extract specific data types from text
  - `/extraction/validate` - Validate extracted information
  - `/extraction/batch` - Process multiple documents simultaneously
  - `/extraction/agents` - Manage specialized extraction agents

**Medical Use Case**: Automated patient data extraction for research and clinical analysis

#### **Database Endpoints** (`/database/*`)
- **Function**: Data storage and retrieval operations
- **Medical Analogy**: Like **electronic health record system** for research data
- **Key Endpoints**:
  - `/database/query` - Query stored patient data
  - `/database/export` - Export data in various formats
  - `/database/backup` - Database backup and recovery
  - `/database/stats` - Database statistics and performance metrics

**Medical Use Case**: Accessing stored research data and patient information

#### **RAG Endpoints** (`/rag/*`)
- **Function**: Question answering using extracted knowledge
- **Medical Analogy**: Like **medical consultation system** providing evidence-based answers
- **Key Endpoints**:
  - `/rag/query` - Ask questions about medical data
  - `/rag/context` - Get relevant context for queries
  - `/rag/sources` - Identify source documents for answers
  - `/rag/feedback` - Provide feedback on answer quality

**Medical Use Case**: Clinical decision support and research question answering

#### **Health Endpoints** (`/health/*`)
- **Function**: System health monitoring and diagnostics
- **Medical Analogy**: Like **health checkup** ensuring system wellness
- **Key Endpoints**:
  - `/health` - Overall system health status
  - `/health/system` - Detailed system status and metrics
  - `/health/components` - Individual component health checks

**Medical Use Case**: Ensuring system reliability for critical research operations

### **🔧 API Router** (`main.py`)
**Biological Purpose**: "Neural pathway" that routes requests to appropriate endpoints

- **Function**: Configures and organizes all API endpoints
- **Medical Analogy**: Like **neural routing** directing signals to appropriate brain regions
- **Key Features**:
  - Endpoint organization and grouping
  - Middleware configuration
  - Error handling and logging
  - Authentication and authorization

**Medical Use Case**: Ensuring proper routing of research requests to appropriate processing systems

## 🧬 **Biological Data Flow**

### **1. Request Reception**
```
External Request → API Gateway → Authentication → Request Validation
```

**Biological Analogy**: Like **sensory input** being received and validated

### **2. Request Processing**
```
Validated Request → Route Selection → Component Activation → Data Processing
```

**Biological Analogy**: Like **neural processing** routing signals to appropriate systems

### **3. Response Generation**
```
Processed Data → Response Formatting → Quality Validation → Response Delivery
```

**Biological Analogy**: Like **motor output** delivering processed information

### **4. System Monitoring**
```
Request Metrics → Performance Analysis → Health Monitoring → System Optimization
```

**Biological Analogy**: Like **homeostasis** maintaining optimal system conditions

## 🔬 **Medical Research Applications**

### **Literature Research**
- **Systematic Reviews**: Automated literature search and retrieval
- **Case Discovery**: Finding relevant patient cases across studies
- **Meta-Analysis**: Aggregating data from multiple research papers
- **Literature Synthesis**: Building comprehensive knowledge bases

### **Clinical Data Analysis**
- **Patient Cohort Building**: Identifying patients with specific characteristics
- **Treatment Pattern Analysis**: Discovering effective therapeutic strategies
- **Adverse Event Monitoring**: Tracking medication side effects
- **Outcome Research**: Analyzing treatment effectiveness

### **Research Collaboration**
- **Data Sharing**: Secure access to research data
- **Multi-site Studies**: Coordinating research across institutions
- **Real-time Updates**: Live data integration and analysis
- **Standardized Access**: Consistent API for different research tools

## 🚀 **Technical Implementation**

### **API Architecture**
- **RESTful Design**: Standard HTTP methods and status codes
- **FastAPI Framework**: High-performance Python web framework
- **Async Processing**: Non-blocking request handling
- **OpenAPI Documentation**: Auto-generated API documentation

### **Security Features**
- **Authentication**: API key and token-based access control
- **Authorization**: Role-based access to different endpoints
- **Rate Limiting**: Protection against abuse and overload
- **Data Validation**: Input sanitization and validation

### **Performance Features**
- **Caching**: Intelligent response caching for improved performance
- **Compression**: Response compression for large data transfers
- **Pagination**: Efficient handling of large result sets
- **Background Processing**: Asynchronous processing for long-running tasks

## 📊 **API Usage & Performance**

### **Request Patterns**
- **Search Operations**: 100-1000 requests per minute
- **Document Processing**: 10-100 documents per minute
- **Data Retrieval**: 1000+ records per second
- **Real-time Updates**: WebSocket connections for live data

### **Response Times**
- **Simple Queries**: <100ms response time
- **Complex Searches**: 1-5 seconds response time
- **Document Processing**: 5-30 seconds depending on complexity
- **Batch Operations**: Variable based on batch size

## 🎯 **Future Enhancements**

### **Medical Capabilities**
- **Multi-modal Data**: Support for images, lab results, genetic data
- **Temporal Analysis**: Time-series data processing and analysis
- **Population Studies**: Large-scale epidemiological analysis
- **Precision Medicine**: Personalized data access and analysis

### **Technical Improvements**
- **GraphQL Support**: More flexible query capabilities
- **Real-time Streaming**: Live data streaming capabilities
- **Advanced Caching**: Intelligent cache management
- **API Versioning**: Backward compatibility and evolution

## 🔧 **Usage Examples**

### **Basic API Usage**
```python
import requests

# Search for medical literature
response = requests.get(
    "http://localhost:8000/api/v1/metadata/search",
    params={"query": "Leigh syndrome", "limit": 10}
)

# Process medical document
with open("case_report.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        files={"file": f}
    )
```

### **WebSocket Connection**
```javascript
// Real-time updates
const ws = new WebSocket('ws://localhost:8000/api/v1/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Real-time update:', data);
};
```

### **Batch Processing**
```python
# Process multiple documents
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
response = requests.post(
    "http://localhost:8000/api/v1/extraction/batch",
    json={"documents": documents}
)
```

---

**The API module serves as the communication bridge between the Biomedical Text Agent and the medical research community - enabling seamless access to advanced AI-powered medical data processing capabilities through standardized, secure, and performant REST endpoints.** 🧬🔬💊
