# Enhanced Backend API Structure

This document describes the enhanced backend API structure for the Biomedical Text Agent, which provides advanced features while maintaining full compatibility with the original system.

## 🚀 Overview

The enhanced system consists of five core components that work alongside the existing backend structure:

1. **Enhanced Endpoints** (`enhanced_endpoints.py`) - Complete API endpoint definitions with mock implementations
2. **Enhanced Server** (`enhanced_server.py`) - FastAPI server setup with CORS and error handling
3. **Enhanced SQLite Manager** (`enhanced_sqlite_manager.py`) - Database manager for linked data storage
4. **Enhanced Metadata Orchestrator** (`enhanced_metadata_orchestrator.py`) - Metadata triage pipeline orchestration
5. **Enhanced LangExtract Integration** (`enhanced_langextract_integration.py`) - LangExtract integration with UI support

## 🏗️ Architecture

```
Original System                    Enhanced System
┌─────────────────┐              ┌─────────────────┐
│   endpoints.py  │              │enhanced_endpoints│
│   main.py       │              │enhanced_server  │
│   sqlite_manager│              │enhanced_sqlite  │
│   orchestrator  │              │enhanced_orchestr│
│   extractor     │              │enhanced_langext │
└─────────────────┘              └─────────────────┘
         │                                │
         └───────────┬────────────────────┘
                     │
              ┌─────────────────┐
              │   Main API      │
              │   Router        │
              └─────────────────┘
                     │
              ┌─────────────────┐
              │   FastAPI App   │
              └─────────────────┘
```

## 📁 File Structure

```
src/
├── api/
│   ├── enhanced_endpoints.py          # Enhanced API endpoints
│   ├── enhanced_server.py             # Enhanced FastAPI server
│   ├── endpoints.py                   # Original endpoints
│   └── main.py                       # Main API router (updated)
├── database/
│   ├── enhanced_sqlite_manager.py     # Enhanced database manager
│   └── sqlite_manager.py              # Original database manager
├── metadata_triage/
│   ├── enhanced_metadata_orchestrator.py  # Enhanced orchestrator
│   └── metadata_orchestrator.py           # Original orchestrator
└── langextract_integration/
    ├── enhanced_langextract_integration.py  # Enhanced integration
    └── extractor.py                         # Original extractor
```

## 🔧 Enhanced Features

### 1. Enhanced Endpoints (`enhanced_endpoints.py`)

- **Enhanced Document Management**: CRUD operations with comprehensive metadata
- **Enhanced Extraction**: Multi-mode extraction with confidence scoring
- **Enhanced Search**: Advanced filtering, sorting, and pagination
- **Enhanced Analytics**: Comprehensive system metrics and monitoring
- **Enhanced Health Checks**: Component-level health monitoring

**Key Endpoints:**
- `POST /api/v2/documents` - Create enhanced documents
- `GET /api/v2/documents/{id}` - Retrieve enhanced documents
- `POST /api/v2/extraction/extract` - Submit enhanced extraction
- `POST /api/v2/search/search` - Enhanced search with filters
- `GET /api/v2/analytics/overview` - System analytics
- `GET /api/v2/health/enhanced` - Enhanced health check

### 2. Enhanced Server (`enhanced_server.py`)

- **Advanced Middleware**: CORS, compression, logging, error handling
- **Enhanced Exception Handling**: Comprehensive error management
- **Request Logging**: Detailed request/response logging
- **Component Health Monitoring**: Real-time system health tracking
- **Enhanced WebSocket Support**: Real-time communication

**Server Features:**
- Automatic CORS configuration
- Request/response logging
- Comprehensive error handling
- Enhanced monitoring and metrics
- WebSocket support for real-time updates

### 3. Enhanced SQLite Manager (`enhanced_sqlite_manager.py`)

- **Enhanced Document Storage**: Comprehensive metadata and annotations
- **Relationship Management**: Entity relationship tracking
- **Analytics Storage**: System metrics and performance data
- **Connection Pooling**: Efficient database connection management
- **Advanced Querying**: Complex search and filtering capabilities

**Database Features:**
- Enhanced document schemas with metadata
- Extraction request tracking
- Analytics and metrics storage
- Relationship graph support
- Advanced search capabilities

### 4. Enhanced Metadata Orchestrator (`enhanced_metadata_orchestrator.py`)

- **Multi-Worker Pipeline**: Concurrent task processing
- **Enhanced Task Management**: Priority-based task scheduling
- **Retry Logic**: Automatic failure recovery
- **Real-time Monitoring**: Live pipeline status tracking
- **Enhanced Classification**: Multi-modal entity classification

**Pipeline Features:**
- Configurable worker pools
- Priority-based task queuing
- Automatic retry mechanisms
- Real-time status monitoring
- Enhanced processing modes

### 5. Enhanced LangExtract Integration (`enhanced_langextract_integration.py`)

- **Multi-Mode Extraction**: Basic, enhanced, advanced, and custom modes
- **Schema Management**: Configurable extraction schemas
- **Enhanced Entity Linking**: External knowledge base integration
- **Confidence Scoring**: Advanced confidence calculation
- **Cross-Validation**: Multi-pass result validation

**Extraction Features:**
- Multiple extraction modes
- Configurable schemas
- Entity linking and normalization
- Confidence scoring
- Result cross-validation

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- FastAPI
- SQLite3
- Required dependencies from `requirements.txt`

### Installation

1. **Clone the repository** (if not already done)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Enhanced System

#### Option 1: Run Demonstration
```bash
python start_enhanced_system.py demo
```

#### Option 2: Start Enhanced Server
```bash
python start_enhanced_system.py server
```

#### Option 3: Run Default (Demonstration)
```bash
python start_enhanced_system.py
```

### API Access

- **Original API**: `http://localhost:8000/api/v1/`
- **Enhanced API**: `http://localhost:8001/api/v2/`
- **Enhanced Documentation**: `http://localhost:8001/api/enhanced/docs`

## 🔌 API Integration

### Original System Compatibility

The enhanced system maintains full compatibility with the original system:

```python
# Original system still works
from api.main import create_api_router
from database.sqlite_manager import SQLiteManager
from metadata_triage.metadata_orchestrator import MetadataOrchestrator

# Enhanced system works alongside
from api.enhanced_server import create_enhanced_app
from database.enhanced_sqlite_manager import EnhancedSQLiteManager
from metadata_triage.enhanced_metadata_orchestrator import EnhancedMetadataOrchestrator
```

### Enhanced System Usage

```python
# Initialize enhanced components
enhanced_db = EnhancedSQLiteManager()
enhanced_orchestrator = EnhancedMetadataOrchestrator(enhanced_db_manager=enhanced_db)
enhanced_langextract = EnhancedLangExtractIntegration(
    enhanced_db_manager=enhanced_db,
    enhanced_orchestrator=enhanced_orchestrator
)

# Use enhanced features
doc_id = await enhanced_db.create_enhanced_document(
    title="Sample Document",
    content="Document content...",
    metadata={"source": "enhanced", "category": "demo"}
)

extraction_id = await enhanced_langextract.submit_enhanced_extraction(
    document_id=doc_id,
    mode="enhanced",
    schemas=["biomedical_entities"]
)
```

## 📊 Enhanced API Endpoints

### Enhanced Documents

```http
POST /api/v2/documents
GET /api/v2/documents/{id}
PUT /api/v2/documents/{id}
DELETE /api/v2/documents/{id}
```

### Enhanced Extraction

```http
POST /api/v2/extraction/extract
GET /api/v2/extraction/extractions/{request_id}
```

### Enhanced Search

```http
POST /api/v2/search/search
```

### Enhanced Analytics

```http
GET /api/v2/analytics/overview
GET /api/v2/analytics/entities
```

### Enhanced Health

```http
GET /api/v2/health/enhanced
GET /api/v2/health/component/{component_name}
```

## 🔍 Monitoring and Analytics

### Real-time Monitoring

The enhanced system provides comprehensive monitoring:

- **Pipeline Status**: Real-time task processing status
- **Performance Metrics**: Processing times and success rates
- **System Health**: Component-level health monitoring
- **Resource Usage**: CPU, memory, and disk usage tracking

### Analytics Dashboard

Access enhanced analytics at:
- `http://localhost:8001/api/v2/analytics/overview`
- `http://localhost:8001/api/v2/analytics/entities`

## 🧪 Testing and Development

### Running Tests

```bash
# Test enhanced endpoints
python -m pytest tests/test_enhanced_endpoints.py

# Test enhanced database
python -m pytest tests/test_enhanced_sqlite_manager.py

# Test enhanced orchestrator
python -m pytest tests/test_enhanced_metadata_orchestrator.py
```

### Development Mode

```bash
# Start enhanced server with auto-reload
python start_enhanced_system.py server --reload

# Run demonstration with debug logging
python start_enhanced_system.py demo --debug
```

## 🔧 Configuration

### Enhanced System Configuration

```python
enhanced_config = {
    "pipeline": {
        "max_concurrent_tasks": 5,
        "task_timeout": 300,
        "retry_delay": 60
    },
    "extraction": {
        "max_concurrent": 3,
        "timeout": 300
    },
    "database": {
        "connection_pool_size": 10,
        "cleanup_interval": 3600
    }
}
```

### Environment Variables

```bash
# Enhanced system configuration
ENHANCED_MAX_WORKERS=5
ENHANCED_TASK_TIMEOUT=300
ENHANCED_DB_POOL_SIZE=10
ENHANCED_LOG_LEVEL=INFO
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/` is in Python path
2. **Database Errors**: Check SQLite file permissions
3. **Port Conflicts**: Verify ports 8000 and 8001 are available
4. **Dependency Issues**: Install all required packages

### Debug Mode

```bash
# Enable debug logging
export ENHANCED_LOG_LEVEL=DEBUG
python start_enhanced_system.py demo
```

### Health Checks

```bash
# Check enhanced system health
curl http://localhost:8001/api/v2/health/enhanced

# Check component health
curl http://localhost:8001/api/v2/health/component/database
```

## 🔄 Migration and Upgrades

### From Original System

The enhanced system is designed to work alongside the original system:

1. **No Breaking Changes**: Original APIs remain functional
2. **Gradual Migration**: Use enhanced features as needed
3. **Backward Compatibility**: All original functionality preserved
4. **Enhanced Features**: Additional capabilities available

### Future Enhancements

- **GraphQL Support**: Advanced query capabilities
- **Real-time Streaming**: Live data streaming
- **Advanced ML Integration**: Enhanced AI capabilities
- **Distributed Processing**: Multi-node processing support

## 📚 API Documentation

### Interactive Documentation

- **Enhanced Swagger UI**: `http://localhost:8001/api/enhanced/docs`
- **Enhanced ReDoc**: `http://localhost:8001/api/enhanced/redoc`
- **OpenAPI Schema**: `http://localhost:8001/api/enhanced/openapi.json`

### Code Examples

See `start_enhanced_system.py` for comprehensive usage examples.

## 🤝 Contributing

### Development Guidelines

1. **Maintain Compatibility**: Ensure original system compatibility
2. **Follow Patterns**: Use existing enhanced system patterns
3. **Add Tests**: Include comprehensive test coverage
4. **Update Documentation**: Keep this README current

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Include comprehensive docstrings
- Follow existing naming conventions

## 📄 License

This enhanced system is part of the Biomedical Text Agent project and follows the same license terms.

## 🆘 Support

### Getting Help

1. **Check Documentation**: Review this README and API docs
2. **Run Examples**: Use `start_enhanced_system.py` for examples
3. **Check Logs**: Enable debug logging for detailed information
4. **Health Checks**: Use health endpoints to diagnose issues

### Reporting Issues

When reporting issues, include:
- System configuration
- Error logs
- Steps to reproduce
- Expected vs. actual behavior

---

**🎉 The Enhanced Backend API Structure is now fully synchronized with the original backend API structure and ready for use!**
