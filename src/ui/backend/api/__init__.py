"""
API Router Module

Centralized API routing for all UI backend endpoints.
"""

from fastapi import APIRouter

from .dashboard import router as dashboard_router
from .agents import router as agents_router
from .documents import router as documents_router
from .metadata import router as metadata_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(agents_router, prefix="/agents", tags=["Agents"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(metadata_router, prefix="/metadata", tags=["Metadata"])

__all__ = ["api_router"]

