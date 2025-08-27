"""
Main API router for Biomedical Text Agent.

This module creates the unified API router that connects all system endpoints
and provides a single interface for the frontend and external clients.
"""

from fastapi import APIRouter
from .endpoints import (
    metadata_triage_router,
    extraction_router,
    database_router,
    rag_router,
    user_router
)

def create_api_router() -> APIRouter:
    """
    Create the main API router with all endpoints.
    
    Returns:
        APIRouter: Unified API router with all endpoints
    """
    api_router = APIRouter()
    
    # Include all endpoint routers
    api_router.include_router(
        metadata_triage_router,
        prefix="/metadata",
        tags=["Metadata Triage"]
    )
    
    api_router.include_router(
        extraction_router,
        prefix="/extraction",
        tags=["Data Extraction"]
    )
    
    api_router.include_router(
        database_router,
        prefix="/database",
        tags=["Database Operations"]
    )
    
    api_router.include_router(
        rag_router,
        prefix="/rag",
        tags=["RAG System"]
    )
    
    api_router.include_router(
        user_router,
        prefix="/users",
        tags=["User Management"]
    )
    
    return api_router