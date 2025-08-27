# 📁 Biomedical Text Agent - File Organization Guide

## 🎯 **Overview**

This document provides the complete file organization for the restructured Biomedical Text Agent system. It shows the current structure, what needs to be changed, and the final organized structure.

## 🔍 **Current File Structure Analysis**

```
biomedicalmedical_text_agent/
├── .git/                          # Git repository
├── scripts/                       # Utility scripts
├── src/                          # Main source code
│   ├── __init__.py
│   ├── main.py                   # CLI interface (needs update)
│   ├── agents/                   # AI extraction agents
│   │   ├── __init__.py
│   │   ├── extraction_agents/    # Demographics, genetics, etc.
│   │   ├── orchestrator/         # Extraction orchestrator
│   │   └── validation_agents/    # Validation logic
│   ├── api/                      # ❌ EMPTY - needs implementation
│   │   └── __init__.py
│   ├── ui/                       # User interface
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── setup_ui.py
│   │   ├── frontend/             # React frontend (KEEP)
│   │   │   ├── package.json
│   │   │   ├── src/
│   │   │   └── public/
│   │   └── backend/              # ❌ DUPLICATE - REMOVE
│   │       ├── app.py            # Duplicate backend
│   │       ├── auth.py           # Not needed
│   │       ├── init_db.py        # Redundant
│   │       ├── websocket_manager.py
│   │       └── biomedical_agent.db
│   ├── utils/                    # Utility functions
│   ├── metadata_triage/          # ✅ KEEP - PubMed/Europe PMC
│   │   ├── __init__.py
│   │   ├── metadata_orchestrator.py
│   │   ├── pubmed_client.py
│   │   ├── europepmc_client.py
│   │   ├── abstract_classifier.py
│   │   ├── concept_scorer.py
│   │   └── deduplicator.py
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── ontologies/               # ✅ KEEP - HPO and gene management
│   │   ├── __init__.py
│   │   ├── hpo_manager.py
│   │   ├── hpo_manager.pydeact
│   │   ├── hpo_manager_optimized.py
│   │   └── gene_manager.py
│   ├── processors/               # ✅ KEEP - Document processing
│   │   ├── __init__.py
│   │   ├── patient_segmenter.py
│   │   └── pdf_parser.py
│   ├── core/                     # ✅ KEEP - Core functionality
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   ├── api_usage_tracker.py
│   │   ├── feedback_loop.py
│   │   ├── prompt_optimization.py
│   │   ├── llm_client/           # LLM integration
│   │   ├── schema_manager/       # Schema management
│   │   ├── document_loader/      # Document loading
│   │   └── feedback/             # Feedback mechanisms
│   ├── database/                 # ✅ KEEP - Database management
│   │   ├── __init__.py
│   │   ├── sqlite_manager.py
│   │   └── vector_manager.py
│   ├── extractors/               # ❌ REDUNDANT - Replace with LangExtract
│   │   ├── __init__.py
│   │   ├── entity_mapper/
│   │   ├── normalizer/
│   │   └── validator/
│   ├── langextract_integration/  # ✅ KEEP - Primary extraction engine
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   ├── normalizer.py
│   │   ├── schema_classes.py
│   │   └── visualizer.py
│   └── rag/                      # ✅ KEEP - RAG system
│       ├── __init__.py
│       ├── rag_integration.py
│       └── rag_system.py
├── data/                         # Data storage
├── docs/                         # Documentation
├── notebooks/                    # Jupyter notebooks
├── requirements.txt              # Python dependencies
├── setup.py                     # Package setup
├── start_system.py              # ❌ OLD - Replace
├── start_unified_system.py      # ✅ NEW - Unified startup
├── run_enhanced_system.py       # ❌ OLD - Remove
├── test_*.py                    # Test files
├── demo.py                      # Demo script
├── env.example                  # Environment template
├── README.md                    # Main documentation
├── SYSTEM_STATUS.md             # System status
├── USER_GUIDE.md                # User guide
├── SETUP_COMPLETE.md            # Setup guide
├── RESTRUCTURING_PLAN.md        # ✅ NEW - This plan
└── FILE_ORGANIZATION.md          # ✅ NEW - This guide
```

## 🏗️ **Proposed File Structure (After Restructuring)**

```
biomedicalmedical_text_agent/
├── .git/                          # Git repository
├── scripts/                       # Utility scripts
├── src/                          # Main source code
│   ├── __init__.py
│   ├── main.py                   # ✅ UPDATED - Uses unified orchestrator
│   ├── unified_app.py            # ✅ NEW - Single FastAPI application
│   ├── agents/                   # ✅ KEEP - AI extraction agents
│   │   ├── __init__.py
│   │   ├── extraction_agents/    # Demographics, genetics, etc.
│   │   ├── orchestrator/         # Extraction orchestrator
│   │   └── validation_agents/    # Validation logic
│   ├── api/                      # ✅ NEW - Unified API layer
│   │   ├── __init__.py           # API module exports
│   │   ├── main.py               # Main API router
│   │   └── endpoints.py          # All API endpoints
│   ├── ui/                       # ✅ SIMPLIFIED - Frontend only
│   │   ├── __init__.py
│   │   ├── config.py             # ✅ SIMPLIFIED
│   │   ├── setup_ui.py           # ✅ KEEP
│   │   └── frontend/             # ✅ KEEP - React frontend
│   │       ├── package.json
│   │       ├── src/
│   │       └── public/
│   ├── utils/                    # ✅ KEEP - Utility functions
│   ├── metadata_triage/          # ✅ KEEP - PubMed/Europe PMC
│   │   ├── __init__.py
│   │   ├── metadata_orchestrator.py
│   │   ├── pubmed_client.py
│   │   ├── europepmc_client.py
│   │   ├── abstract_classifier.py
│   │   ├── concept_scorer.py
│   │   └── deduplicator.py
│   ├── models/                   # ✅ KEEP - Data models
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── ontologies/               # ✅ KEEP - HPO and gene management
│   │   ├── __init__.py
│   │   ├── hpo_manager.py        # ✅ KEEP - Active version
│   │   ├── gene_manager.py       # ✅ KEEP
│   │   ├── hpo_manager.pydeact  # ❌ REMOVE - Inactive
│   │   └── hpo_manager_optimized.py # ❌ REMOVE - Redundant
│   ├── processors/               # ✅ KEEP - Document processing
│   │   ├── __init__.py
│   │   ├── patient_segmenter.py
│   │   └── pdf_parser.py
│   ├── core/                     # ✅ KEEP - Core functionality
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   ├── api_usage_tracker.py
│   │   ├── feedback_loop.py
│   │   ├── prompt_optimization.py
│   │   ├── unified_orchestrator.py # ✅ NEW - System coordinator
│   │   ├── llm_client/           # LLM integration
│   │   ├── schema_manager/       # Schema management
│   │   ├── document_loader/      # Document loading
│   │   └── feedback/             # Feedback mechanisms
│   ├── database/                 # ✅ KEEP - Database management
│   │   ├── __init__.py
│   │   ├── sqlite_manager.py
│   │   └── vector_manager.py
│   ├── extractors/               # ❌ REMOVE - Replaced by LangExtract
│   ├── langextract_integration/  # ✅ KEEP - Primary extraction engine
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   ├── normalizer.py
│   │   ├── schema_classes.py
│   │   └── visualizer.py
│   └── rag/                      # ✅ KEEP - RAG system
│       ├── __init__.py
│       ├── rag_integration.py
│       └── rag_system.py
├── data/                         # ✅ KEEP - Data storage
├── docs/                         # ✅ KEEP - Documentation
├── notebooks/                    # ✅ KEEP - Jupyter notebooks
├── requirements.txt              # ✅ KEEP - Python dependencies
├── setup.py                     # ✅ KEEP - Package setup
├── start_unified_system.py      # ✅ NEW - Unified startup script
├── test_*.py                    # ✅ KEEP - Test files
├── demo.py                      # ✅ KEEP - Demo script
├── env.example                  # ✅ KEEP - Environment template
├── README.md                    # ✅ UPDATE - New architecture
├── SYSTEM_STATUS.md             # ✅ UPDATE - New status
├── USER_GUIDE.md                # ✅ UPDATE - New workflow
├── SETUP_COMPLETE.md            # ✅ UPDATE - New setup
├── RESTRUCTURING_PLAN.md        # ✅ NEW - Restructuring plan
└── FILE_ORGANIZATION.md          # ✅ NEW - This guide
```

## 📋 **File Action Summary**

### **✅ NEW FILES (Created)**
- `src/unified_app.py` - Single FastAPI application
- `src/api/__init__.py` - API module exports
- `src/api/main.py` - Main API router
- `src/api/endpoints.py` - All API endpoints
- `src/core/unified_orchestrator.py` - System coordinator
- `start_unified_system.py` - Unified startup script
- `RESTRUCTURING_PLAN.md` - Restructuring documentation
- `FILE_ORGANIZATION.md` - This file organization guide

### **🔄 UPDATED FILES (Modified)**
- `src/main.py` - Updated to use unified orchestrator
- `src/ui/config.py` - Simplified configuration
- `README.md` - Updated with new architecture
- `SYSTEM_STATUS.md` - Updated system status
- `USER_GUIDE.md` - Updated user workflow
- `SETUP_COMPLETE.md` - Updated setup instructions

### **❌ REMOVED FILES (Deleted)**
- `src/ui/backend/` - Entire duplicate backend directory
  - `app.py` - Duplicate FastAPI app
  - `auth.py` - Not needed
  - `init_db.py` - Redundant
  - `websocket_manager.py` - Not used
  - `biomedical_agent.db` - Will be recreated
  - `requirements.txt` - Duplicate
- `src/extractors/` - Entire directory (replaced by LangExtract)
- `src/ontologies/hpo_manager.pydeact` - Inactive version
- `src/ontologies/hpo_manager_optimized.py` - Redundant version
- `start_system.py` - Old startup script
- `run_enhanced_system.py` - Old startup script

### **✅ KEPT FILES (No Changes)**
- `src/agents/` - AI extraction agents
- `src/metadata_triage/` - PubMed/Europe PMC integration
- `src/ontologies/hpo_manager.py` - Active HPO manager
- `src/ontologies/gene_manager.py` - Gene manager
- `src/processors/` - Document processing
- `src/core/` - Core functionality (except new orchestrator)
- `src/database/` - Database management
- `src/langextract_integration/` - Primary extraction engine
- `src/rag/` - RAG system
- `src/ui/frontend/` - React frontend
- All test files, documentation, and data directories

## 🔧 **Implementation Commands**

### **Step 1: Create New Structure**
```bash
# Create new API directory structure
mkdir -p src/api
touch src/api/__init__.py
touch src/api/main.py
touch src/api/endpoints.py

# Create unified orchestrator
touch src/core/unified_orchestrator.py

# Create unified application
touch src/unified_app.py

# Create new startup script
touch start_unified_system.py
```

### **Step 2: Remove Old Components**
```bash
# Remove duplicate backend
rm -rf src/ui/backend/

# Remove old extractors
rm -rf src/extractors/

# Remove redundant HPO managers
rm src/ontologies/hpo_manager.pydeact
rm src/ontologies/hpo_manager_optimized.py

# Remove old startup scripts
rm start_system.py
rm run_enhanced_system.py

# Clean up cache files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### **Step 3: Update Existing Files**
```bash
# Update main.py to use unified orchestrator
# Update UI configuration
# Update documentation files
```

## 📊 **File Count Summary**

### **Before Restructuring:**
- **Total Files**: ~50+ files
- **Duplicate Components**: 3+ backend systems
- **Redundant Code**: ~30% duplication
- **Integration Points**: 5+ separate entry points

### **After Restructuring:**
- **Total Files**: ~40 files
- **Unified Components**: 1 backend system
- **Code Duplication**: <5%
- **Integration Points**: 1 unified entry point

## 🎯 **Benefits of New Organization**

### **1. Clear Module Responsibilities**
- `src/api/` - All API endpoints and routing
- `src/core/` - Core system functionality and coordination
- `src/ui/` - Frontend only (no backend duplication)
- `src/metadata_triage/` - Document retrieval and classification
- `src/langextract_integration/` - Primary data extraction
- `src/database/` - Unified data storage and retrieval
- `src/rag/` - Question answering and search

### **2. Eliminated Redundancy**
- Single backend system
- Unified database layer
- Consistent API structure
- Single startup script

### **3. Improved Maintainability**
- Clear file organization
- Consistent naming conventions
- Logical module grouping
- Easy to navigate structure

### **4. Better Integration**
- All components connected through unified orchestrator
- Consistent data flow
- Shared configuration
- Unified error handling

---

## 📅 **Implementation Timeline**

- **Phase 1**: Create new file structure (✅ COMPLETED)
- **Phase 2**: Remove old components (🔄 NEXT)
- **Phase 3**: Update existing files (🔄 NEXT)
- **Phase 4**: Test new structure (🔄 NEXT)
- **Phase 5**: Update documentation (🔄 NEXT)

---

*This file organization will create a clean, maintainable, and efficient codebase structure.*