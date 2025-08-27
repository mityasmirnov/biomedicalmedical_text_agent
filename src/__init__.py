"""
Biomedical Text Agent - Unified System

A comprehensive, AI-powered system for extracting and analyzing biomedical information
from medical literature. This unified system consolidates all functionality into a single,
efficient architecture.

Main modules:
- api: Unified API layer
- core: Core system functionality
- ui: Frontend interface
- metadata_triage: Document retrieval and classification
- langextract_integration: Primary extraction engine
- database: Unified data storage
- rag: Question answering system
- agents: AI extraction agents
- ontologies: Medical ontology integration
- processors: Document processing
- models: Data models and schemas
- utils: Utility functions
"""

__version__ = "2.0.0"
__author__ = "Biomedical Text Agent Team"

# Import main components
from .api import create_api_router
from .core import UnifiedOrchestrator
from .unified_app import create_unified_app

__all__ = [
    'create_api_router',
    'UnifiedOrchestrator',
    'create_unified_app',
    '__version__',
    '__author__'
]
