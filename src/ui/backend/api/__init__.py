"""
API Router Module

Centralized API routing for all UI backend endpoints.
"""

from fastapi import APIRouter

from .dashboard import router as dashboard_router
# from ..auth import router as auth_router  # disabled for minimal boot
# The following routers are for modules that are not yet implemented.
# from .knowledge_base import router as knowledge_base_router
# from .database import router as database_router
# from .agents import router as agents_router
# from .documents import router as documents_router
# from .validation import router as validation_router
# from .monitoring import router as monitoring_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
# api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])  # disabled for now
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
# api_router.include_router(knowledge_base_router, prefix="/knowledge-base", tags=["Knowledge Base"])
# api_router.include_router(database_router, prefix="/database", tags=["Database"])
# api_router.include_router(agents_router, prefix="/agents", tags=["Agents"])
# api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
# api_router.include_router(validation_router, prefix="/validation", tags=["Validation"])
# api_router.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])

__all__ = ["api_router"]

