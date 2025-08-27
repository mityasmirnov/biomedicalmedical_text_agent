# 🏥 Biomedical Text Agent - User Guide

## 🎯 **Welcome to the Unified Biomedical Text Agent v2.0!**

This guide will help you use the completely restructured and unified Biomedical Text Agent system. The new v2.0 architecture eliminates all previous complexity and provides a single, efficient interface for all functionality.

---

## 🚀 **Quick Start Guide**

### **1. Start the System**
```bash
# Navigate to your project directory
cd biomedicalmedical_text_agent

# Activate virtual environment
source venv/bin/activate

# Start the unified system
python3 start_unified_system.py
```

### **2. Access the System**
- **Frontend Interface**: http://127.0.0.1:8000/
- **API Documentation**: http://127.0.0.1:8000/api/docs
- **Health Check**: http://127.0.0.1:8000/api/health

### **3. Start Processing Documents**
The system is now ready to use! Upload documents through the web interface or use the API endpoints.

---

## 🏗️ **What's New in v2.0**

### **✅ Unified Architecture**
- **Single Backend**: One FastAPI application serving everything
- **Consolidated APIs**: All endpoints in one place
- **Eliminated Duplication**: No more redundant systems
- **Streamlined Database**: Unified data storage

### **✅ Simplified Workflow**
- **One Entry Point**: Single startup script
- **Unified Interface**: All features accessible from one place
- **Consistent API**: Same patterns across all functionality
- **Integrated Components**: Everything works together seamlessly

---

## 📚 **Core Features**

### **1. Document Processing**
- **Multi-format Support**: PDF, DOCX, TXT, HTML, XML
- **Intelligent Parsing**: Automatic patient segmentation
- **Batch Processing**: Handle multiple documents efficiently
- **Real-time Status**: Monitor processing progress

### **2. AI-Powered Extraction**
- **Demographics Agent**: Age, gender, ethnicity, consanguinity
- **Genetics Agent**: Gene variants, mutations, inheritance
- **Phenotypes Agent**: HPO term identification and normalization
- **Treatments Agent**: Medical interventions and procedures

### **3. Data Management**
- **Unified Storage**: SQLite database with vector search
- **Metadata Management**: Document classification and organization
- **Export Options**: CSV, JSON, Excel formats
- **Data Validation**: Quality control and error checking

### **4. Question Answering**
- **RAG System**: Ask questions about your extracted data
- **Natural Language**: Use plain English queries
- **Context-Aware**: Intelligent responses based on your data
- **Source Tracking**: See which documents support each answer

---

## 🌐 **Web Interface Guide**

### **Dashboard Overview**
The main dashboard provides:
- **System Status**: Real-time health monitoring
- **Processing Metrics**: Document counts and success rates
- **Recent Activity**: Latest processing jobs
- **Quick Actions**: Upload documents, view data, ask questions

### **Document Management**
1. **Upload Documents**: Drag & drop or click to browse
2. **Processing Queue**: See all documents being processed
3. **Results View**: Browse extracted data and metadata
4. **Export Options**: Download data in various formats

### **Data Exploration**
1. **Patient Records**: View individual patient data
2. **Statistics**: Summary metrics and distributions
3. **Visualizations**: Charts and graphs of your data
4. **Search & Filter**: Find specific information quickly

---

## 🔌 **API Usage Guide**

### **Authentication**
The unified system currently operates without authentication for simplicity. All endpoints are accessible directly.

### **Core Endpoints**

#### **System Status**
```bash
# Check system health
curl http://127.0.0.1:8000/api/health

# Get system status
curl http://127.0.0.1:8000/api/v1/system/status

# View dashboard overview
curl http://127.0.0.1:8000/api/v1/dashboard/overview
```

#### **Document Processing**
```bash
# Upload and process a document
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload" \
  -F "file=@your_document.pdf"

# Get processing status
curl http://127.0.0.1:8000/api/v1/documents/status

# Retrieve extracted data
curl http://127.0.0.1:8000/api/v1/documents/data
```

#### **Data Extraction**
```bash
# Extract data from a document
curl -X POST "http://127.0.0.1:8000/api/v1/extraction/extract" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "doc_123", "extraction_type": "full"}'

# Get extraction results
curl http://127.0.0.1:8000/api/v1/extraction/results/doc_123
```

#### **Question Answering**
```bash
# Ask a question about your data
curl -X POST "http://127.0.0.1:8000/api/v1/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What genes are associated with Leigh syndrome?"}'
```

### **API Documentation**
Visit http://127.0.0.1:8000/api/docs for interactive API documentation with examples and testing capabilities.

---

## 💻 **Command Line Interface**

### **Basic Commands**
```bash
# Show help
python3 src/main.py --help

# Check system configuration
python3 src/main.py --check

# Start the system
python3 start_unified_system.py
```

### **Advanced Usage**
```bash
# Start with custom options
python3 start_unified_system.py --host 0.0.0.0 --port 8080 --reload

# Check system health
python3 start_unified_system.py --check

# Run in verbose mode
python3 start_unified_system.py --verbose
```

---

## 📊 **Data Workflow**

### **Complete Processing Pipeline**

#### **Step 1: Document Upload**
1. Upload document through web interface or API
2. System automatically detects document type
3. Document enters processing queue

#### **Step 2: Document Processing**
1. **Text Extraction**: Extract text from document
2. **Patient Segmentation**: Identify individual patient cases
3. **Content Analysis**: Analyze document structure and content

#### **Step 3: AI Extraction**
1. **Demographics**: Extract age, gender, ethnicity
2. **Genetics**: Identify genes, mutations, inheritance
3. **Phenotypes**: Map symptoms to HPO terms
4. **Treatments**: Extract medical interventions

#### **Step 4: Data Storage**
1. **Structured Storage**: Store in SQLite database
2. **Vector Indexing**: Create semantic search index
3. **Metadata Storage**: Store document and processing info

#### **Step 5: Data Access**
1. **Web Interface**: Browse and explore data
2. **API Access**: Programmatic data retrieval
3. **Question Answering**: Natural language queries
4. **Export Options**: Download in various formats

---

## 🔍 **Data Analysis Examples**

### **Basic Queries**
```python
# Example: Find patients with specific gene mutations
import requests

response = requests.get("http://127.0.0.1:8000/api/v1/database/query", 
                       params={"query": "SELECT * FROM patients WHERE gene = 'SURF1'"})
patients = response.json()
print(f"Found {len(patients)} patients with SURF1 mutations")
```

### **Advanced Analytics**
```python
# Example: Analyze phenotype distributions
response = requests.get("http://127.0.0.1:8000/api/v1/dashboard/metrics")
metrics = response.json()

# Get phenotype frequency
phenotype_counts = metrics.get('phenotype_distribution', {})
for phenotype, count in phenotype_counts.items():
    print(f"{phenotype}: {count} patients")
```

### **Question Answering**
```python
# Example: Ask complex questions about your data
question = "What is the average age of onset for SURF1 mutations?"
response = requests.post("http://127.0.0.1:8000/api/v1/rag/ask",
                        json={"question": question})
answer = response.json()
print(f"Q: {question}")
print(f"A: {answer['answer']}")
```

---

## 🧪 **Testing and Validation**

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
curl http://127.0.0.1:8000/api/v1/dashboard/status
```

### **Frontend Testing**
1. Start the system: `python3 start_unified_system.py`
2. Open browser to: http://127.0.0.1:8000/
3. Test document upload and processing
4. Verify data extraction and display

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **System Won't Start**
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Verify virtual environment
source venv/bin/activate

# Check dependencies
pip list | grep fastapi
```

#### **API Endpoints Not Responding**
```bash
# Check if system is running
ps aux | grep uvicorn

# Test basic connectivity
curl http://127.0.0.1:8000/api/health

# Check logs for errors
tail -f logs/application.log
```

#### **Frontend Not Loading**
```bash
# Verify backend is running
curl http://127.0.0.1:8000/api/health

# Check frontend build
ls -la src/ui/frontend/build/

# Restart system
pkill -f uvicorn
python3 start_unified_system.py
```

### **Performance Issues**
```bash
# Monitor system resources
python3 -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
"

# Check database performance
curl http://127.0.0.1:8000/api/v1/database/stats
```

---

## 📈 **Performance Optimization**

### **System Tuning**
- **Memory Management**: Adjust batch sizes based on available RAM
- **CPU Utilization**: Use appropriate worker counts for your system
- **Database Optimization**: Regular maintenance and indexing
- **Caching**: Enable result caching for repeated operations

### **Processing Optimization**
- **Batch Processing**: Process multiple documents together
- **Parallel Extraction**: Use multiple AI agents simultaneously
- **Streaming**: Process large documents in chunks
- **Background Jobs**: Use async processing for better responsiveness

---

## 🔮 **Advanced Features**

### **Custom Extraction Schemas**
The system supports custom extraction schemas for specialized use cases:
1. Define your schema in JSON format
2. Upload through the API
3. Use for specialized document types

### **Batch Processing**
```bash
# Process multiple documents
curl -X POST "http://127.0.0.1:8000/api/v1/documents/batch" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "files=@doc3.pdf"
```

### **Data Export and Integration**
- **CSV Export**: For spreadsheet analysis
- **JSON Export**: For programmatic access
- **Excel Export**: For detailed reporting
- **API Integration**: For custom applications

---

## 📚 **Additional Resources**

### **Documentation**
- **API Reference**: http://127.0.0.1:8000/api/docs
- **Implementation Guide**: [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **Restructuring Plan**: [RESTRUCTURING_PLAN.md](RESTRUCTURING_PLAN.md)
- **File Organization**: [FILE_ORGANIZATION.md](FILE_ORGANIZATION.md)

### **Examples and Tutorials**
- **Sample Data**: Available in `/data` directory
- **Notebooks**: Jupyter notebooks with examples
- **Test Files**: Sample documents for testing

### **Support**
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Comprehensive guides and examples
- **Community**: Discussions and support forums

---

## 🎯 **Best Practices**

### **Document Preparation**
1. **Quality**: Use high-quality, readable documents
2. **Format**: Prefer PDF over scanned images
3. **Structure**: Well-organized documents process better
4. **Language**: English documents work best

### **Data Management**
1. **Regular Backups**: Backup your database regularly
2. **Data Validation**: Review extracted data for accuracy
3. **Schema Updates**: Keep extraction schemas current
4. **Performance Monitoring**: Monitor system performance

### **Workflow Optimization**
1. **Batch Processing**: Process documents in batches
2. **Parallel Processing**: Use multiple workers when possible
3. **Caching**: Enable caching for repeated operations
4. **Monitoring**: Use the dashboard to track progress

---

## 🎉 **Getting Started Checklist**

### **✅ Setup Complete**
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] System started successfully
- [ ] Frontend accessible
- [ ] API endpoints responding

### **🚀 Ready to Use**
- [ ] Upload your first document
- [ ] Process and extract data
- [ ] Explore extracted information
- [ ] Ask questions about your data
- [ ] Export results for analysis

---

## 📞 **Need Help?**

### **Immediate Support**
1. **Check this guide** for common solutions
2. **Review system status** at http://127.0.0.1:8000/api/v1/system/status
3. **Check logs** for error messages
4. **Restart system** if needed

### **Long-term Support**
- **Documentation**: Comprehensive guides available
- **Examples**: Sample code and workflows
- **Community**: GitHub discussions and issues
- **Updates**: Regular system improvements

---

## 🎯 **Success Metrics**

### **What You Should See**
- ✅ **System starts** in under 5 seconds
- ✅ **Frontend loads** immediately
- ✅ **Document upload** works smoothly
- ✅ **Data extraction** completes successfully
- ✅ **Question answering** provides relevant responses
- ✅ **Export functions** work correctly

### **Performance Indicators**
- **Processing Speed**: Documents process in reasonable time
- **Data Quality**: Extracted information is accurate
- **System Stability**: No crashes or errors
- **User Experience**: Interface is responsive and intuitive

---

**🎉 Congratulations! You're now using the unified Biomedical Text Agent v2.0!**

The system has been completely restructured to provide a seamless, efficient experience for all your biomedical text processing needs. Enjoy the simplified workflow and improved performance!

---

*For technical details and implementation information, see the [Implementation Guide](IMPLEMENTATION_GUIDE.md) and [Restructuring Plan](RESTRUCTURING_PLAN.md).*

