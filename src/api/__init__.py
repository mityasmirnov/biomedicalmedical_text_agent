"""
Unified API module for Biomedical Text Agent.

This module provides a single REST API interface that connects all system components:
- Metadata triage and document retrieval
- Document processing and extraction
- Data storage and retrieval
- RAG system and question answering
- User management and authentication
"""

from .main import create_api_router
from .endpoints import (
    metadata_triage_router,
    extraction_router,
    database_router,
    rag_router,
    user_router
)

__all__ = [
    'create_api_router',
    'metadata_triage_router',
    'extraction_router', 
    'database_router',
    'rag_router',
    'user_router'
]