"""
Main API router for Biomedical Text Agent.

This module creates and configures the main API router that includes all endpoint routers.
"""

from fastapi import APIRouter
from .simple_endpoints import (
    metadata_triage_router,
    extraction_router,
    database_router,
    rag_router,
    user_router,
    dashboard_router,
    agents_router,
    documents_router,
    metadata_router,
    health_router,
    validation_router,
    config_router,
    ontologies_router,
    prompts_router,
    analytics_router,
    auth_router
)

def create_api_router() -> APIRouter:
    """Create and configure the main API router."""
    api_router = APIRouter()
    
    # Include all endpoint routers
    api_router.include_router(metadata_triage_router, prefix="/metadata-triage", tags=["Metadata Triage"])
    api_router.include_router(extraction_router, prefix="/extraction", tags=["Extraction"])
    api_router.include_router(database_router, prefix="/database", tags=["Database"])
    api_router.include_router(rag_router, prefix="/rag", tags=["RAG System"])
    api_router.include_router(user_router, prefix="/users", tags=["User Management"])
    
    # Include UI-specific routers (consolidated from UI backend)
    api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
    api_router.include_router(agents_router, prefix="/agents", tags=["Agents"])
    api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
    api_router.include_router(metadata_router, prefix="/metadata", tags=["Metadata Browser"])
    
    # Include new UI routers
    api_router.include_router(validation_router, prefix="/validation", tags=["Validation"])
    api_router.include_router(config_router, prefix="/config", tags=["Configuration"])
    api_router.include_router(ontologies_router, prefix="/ontologies", tags=["Ontologies"])
    api_router.include_router(prompts_router, prefix="/prompts", tags=["Prompts"])
    api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
    
    # Include health and system endpoints
    api_router.include_router(health_router, tags=["Health & System"])
    
    # Include authentication endpoints
    api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    
    return api_router

# Create the main API router instance
api_router = create_api_router()

__all__ = ["api_router", "create_api_router"]