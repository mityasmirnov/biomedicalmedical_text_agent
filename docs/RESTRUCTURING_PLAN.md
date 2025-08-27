# 🏗️ Biomedical Text Agent - Complete Restructuring Plan

## 📋 **Overview**

This document outlines the complete restructuring plan to synchronize and connect all modules in the Biomedical Text Agent codebase. The current system has many disconnected components that need to be unified into a single, coherent architecture.

## 🎯 **Current Issues Identified**

### 1. **Disconnected Modules**
- UI has separate backend (`src/ui/backend/`) that doesn't use metadata triage
- LangExtract integration exists but isn't connected to main pipeline
- Multiple database managers not properly coordinated
- API endpoints scattered across different modules

### 2. **Redundant Systems**
- Two separate backend systems (main + UI backend)
- Multiple database initialization scripts
- Duplicate configuration files
- Separate startup scripts

### 3. **Missing Integration**
- Metadata triage not connected to extraction pipeline
- RAG system not utilizing metadata triage results
- Database operations not synchronized between components

## 🏗️ **Proposed Unified Architecture**

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

## 📁 **File Restructuring Plan**

### **Phase 1: Create Unified API Layer**

#### **New Files to Create:**
- `src/api/__init__.py` ✅ **CREATED**
- `src/api/main.py` ✅ **CREATED**
- `src/api/endpoints.py` ✅ **CREATED**

#### **Purpose:**
- Single entry point for all system functionality
- Unified routing for metadata triage, extraction, database, RAG, and user management
- Consistent API structure across all modules

### **Phase 2: Create Unified Orchestrator**

#### **New Files to Create:**
- `src/core/unified_orchestrator.py` ✅ **CREATED**

#### **Purpose:**
- Coordinates all system components
- Manages complete document processing pipeline
- Provides single interface for entire system

### **Phase 3: Create Unified Application**

#### **New Files to Create:**
- `src/unified_app.py` ✅ **CREATED**

#### **Purpose:**
- Single FastAPI application serving all functionality
- Unified UI serving and API endpoints
- Consistent middleware and configuration

### **Phase 4: Update Startup Scripts**

#### **New Files to Create:**
- `start_unified_system.py` ✅ **CREATED**

#### **Purpose:**
- Single startup script for entire system
- Unified dependency checking and configuration
- Consistent startup process

## 🔄 **Files to Move/Reorganize**

### **1. Remove Duplicate Backend**
```
❌ REMOVE: src/ui/backend/ (entire directory)
   - app.py (duplicate)
   - auth.py (not needed)
   - init_db.py (redundant)
   - websocket_manager.py (not used)
   - biomedical_agent.db (will be recreated)
```

### **2. Consolidate Database Operations**
```
✅ KEEP: src/database/sqlite_manager.py
✅ KEEP: src/database/vector_manager.py
❌ REMOVE: src/ui/backend/init_db.py
❌ REMOVE: src/ui/backend/biomedical_agent.db
```

### **3. Update UI Configuration**
```
✅ UPDATE: src/ui/frontend/ (keep React frontend)
❌ REMOVE: src/ui/backend/ (duplicate backend)
✅ UPDATE: src/ui/config.py (simplify)
```

## 🗑️ **Files to Remove (Redundant/Unused)**

### **Backend Duplicates:**
- `src/ui/backend/app.py` - Replaced by `src/unified_app.py`
- `src/ui/backend/auth.py` - Not needed for unified system
- `src/ui/backend/init_db.py` - Replaced by unified orchestrator
- `src/ui/backend/websocket_manager.py` - Not used
- `src/ui/backend/biomedical_agent.db` - Will be recreated

### **Old Startup Scripts:**
- `start_system.py` - Replaced by `start_unified_system.py`
- `run_enhanced_system.py` - No longer needed

### **Duplicate Configuration:**
- `src/ui/backend/requirements.txt` - Use main requirements.txt

## 🔧 **Files to Update**

### **1. Update Main Entry Point**
```python
# src/main.py - Update to use unified orchestrator
from core.unified_orchestrator import UnifiedOrchestrator
```

### **2. Update UI Frontend**
```typescript
// src/ui/frontend/src/api/ - Update API calls to use unified endpoints
// Remove references to old backend endpoints
```

### **3. Update Configuration**
```python
# src/core/config.py - Ensure all components use same configuration
# Remove duplicate config files
```

## 📋 **Step-by-Step Implementation**

### **Step 1: Test New Unified System**
```bash
# 1. Test the new unified API endpoints
cd src
python -c "from api.endpoints import *; print('API endpoints loaded successfully')"

# 2. Test the unified orchestrator
python -c "from core.unified_orchestrator import UnifiedOrchestrator; print('Orchestrator loaded successfully')"

# 3. Test the unified application
python -c "from unified_app import create_unified_app; print('Unified app created successfully')"
```

### **Step 2: Remove Old Components**
```bash
# 1. Remove duplicate backend
rm -rf src/ui/backend/

# 2. Remove old startup scripts
rm start_system.py
rm run_enhanced_system.py

# 3. Clean up duplicate files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### **Step 3: Update Frontend API Calls**
```typescript
// Update all API calls in React frontend to use new unified endpoints
// src/ui/frontend/src/api/
```

### **Step 4: Test Complete System**
```bash
# 1. Start unified system
python start_unified_system.py

# 2. Test all endpoints
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/v1/system/status
curl http://127.0.0.1:8000/api/v1/dashboard/status
```

## 🧪 **Testing Strategy**

### **1. Unit Tests**
- Test each new module individually
- Verify imports and dependencies
- Check error handling

### **2. Integration Tests**
- Test module connections
- Verify data flow between components
- Check database operations

### **3. System Tests**
- Test complete pipeline
- Verify UI functionality
- Check API endpoints

## 🚀 **Benefits of Restructuring**

### **1. Unified Architecture**
- Single entry point for all functionality
- Consistent API structure
- Eliminated duplicate code

### **2. Better Integration**
- Metadata triage connected to extraction
- RAG system utilizing all data sources
- Synchronized database operations

### **3. Improved Maintainability**
- Clear module responsibilities
- Consistent coding patterns
- Easier debugging and testing

### **4. Enhanced Performance**
- Eliminated redundant operations
- Optimized data flow
- Better resource utilization

## 📝 **Post-Restructuring Tasks**

### **1. Documentation Updates**
- Update README.md with new architecture
- Document new API endpoints
- Update user guides

### **2. Performance Optimization**
- Profile system performance
- Optimize database queries
- Improve extraction pipeline

### **3. Feature Enhancements**
- Add new extraction capabilities
- Enhance RAG system
- Improve UI functionality

## 🎯 **Success Criteria**

### **1. System Integration**
- ✅ All modules connected through unified API
- ✅ Single database layer serving all components
- ✅ Consistent data flow throughout system

### **2. Functionality**
- ✅ Metadata triage working with extraction
- ✅ RAG system utilizing all data sources
- ✅ UI connected to unified backend

### **3. Performance**
- ✅ No duplicate operations
- ✅ Optimized data flow
- ✅ Consistent response times

## 🔍 **Monitoring and Validation**

### **1. Health Checks**
- `/api/health` - System health status
- `/api/v1/system/status` - Component status
- `/api/v1/dashboard/status` - Dashboard metrics

### **2. Logging**
- Unified logging across all components
- Error tracking and monitoring
- Performance metrics collection

### **3. Testing**
- Automated test suite
- Integration test coverage
- Performance benchmarks

---

## 📅 **Implementation Timeline**

- **Phase 1**: Create unified API layer (✅ COMPLETED)
- **Phase 2**: Create unified orchestrator (✅ COMPLETED)
- **Phase 3**: Create unified application (✅ COMPLETED)
- **Phase 4**: Update startup scripts (✅ COMPLETED)
- **Phase 5**: Remove old components (🔄 NEXT)
- **Phase 6**: Update frontend integration (🔄 NEXT)
- **Phase 7**: Testing and validation (🔄 NEXT)
- **Phase 8**: Documentation and cleanup (🔄 NEXT)

---

*This restructuring plan will transform the fragmented Biomedical Text Agent into a unified, efficient, and maintainable system.*