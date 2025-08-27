"""
Unified FastAPI Application for Biomedical Text Agent

This module provides a single FastAPI application that unifies all system components:
- Metadata triage and document retrieval
- Document processing and extraction
- Data storage and retrieval
- RAG system and question answering
- Web UI serving
"""

import os
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Import unified API
from api import create_api_router
from core.unified_orchestrator import UnifiedOrchestrator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_unified_app() -> FastAPI:
    """
    Create the unified FastAPI application.
    
    Returns:
        FastAPI: Unified application with all endpoints and UI
    """
    app = FastAPI(
        title="Biomedical Text Agent - Unified System",
        description="AI-powered biomedical literature analysis and data extraction",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Include unified API router
    api_router = create_api_router()
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        try:
            # Initialize orchestrator to check system health
            orchestrator = UnifiedOrchestrator()
            status = orchestrator.get_system_status()
            return JSONResponse(content=status, status_code=200)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                content={"status": "unhealthy", "error": str(e)},
                status_code=500
            )
    
    # System status endpoint
    @app.get("/api/v1/system/status")
    async def system_status():
        """Get comprehensive system status."""
        try:
            orchestrator = UnifiedOrchestrator()
            status = orchestrator.get_system_status()
            return JSONResponse(content=status, status_code=200)
        except Exception as e:
            logger.error(f"System status check failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Dashboard endpoint
    @app.get("/api/v1/dashboard/status")
    async def dashboard_status():
        """Get dashboard status information."""
        try:
            orchestrator = UnifiedOrchestrator()
            status = orchestrator.get_system_status()
            
            # Format for dashboard
            dashboard_data = {
                "system_status": status["status"],
                "database_stats": status.get("database_stats", {}),
                "component_status": status.get("components", {}),
                "timestamp": status.get("timestamp")
            }
            
            return JSONResponse(content=dashboard_data, status_code=200)
        except Exception as e:
            logger.error(f"Dashboard status failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Dashboard metrics endpoint
    @app.get("/api/v1/dashboard/metrics")
    async def dashboard_metrics():
        """Get dashboard metrics."""
        try:
            orchestrator = UnifiedOrchestrator()
            status = orchestrator.get_system_status()
            
            # Extract metrics
            db_stats = status.get("database_stats", {})
            sqlite_stats = db_stats.get("sqlite", {})
            vector_stats = db_stats.get("vector", {})
            
            metrics = {
                "total_documents": sqlite_stats.get("total_documents", 0),
                "total_patients": sqlite_stats.get("total_patients", 0),
                "vector_documents": vector_stats.get("total_documents", 0),
                "system_health": status["status"],
                "timestamp": status.get("timestamp")
            }
            
            return JSONResponse(content=metrics, status_code=200)
        except Exception as e:
            logger.error(f"Dashboard metrics failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Serve static frontend (React build) if present
    frontend_build_path = Path(__file__).parent / "ui" / "frontend" / "build"
    if frontend_build_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")
        
        @app.get("/", response_class=HTMLResponse)
        async def serve_index() -> HTMLResponse:
            """Serve the main React application."""
            index_path = frontend_build_path / "index.html"
            if index_path.exists():
                with open(index_path, "r") as f:
                    content = f.read()
                return HTMLResponse(content=content)
            else:
                raise HTTPException(status_code=404, detail="Frontend not built")
    
    # Fallback for all other routes (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str, request: Request):
        """Serve the React application for SPA routing."""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Check if it's a static file
        static_path = frontend_build_path / full_path
        if static_path.exists() and static_path.is_file():
            return FileResponse(str(static_path))
        
        # Serve index.html for SPA routing
        index_path = frontend_build_path / "index.html"
        if index_path.exists():
            with open(index_path, "r") as f:
                content = f.read()
            return HTMLResponse(content=content)
        else:
            raise HTTPException(status_code=404, detail="Frontend not built")
    
    logger.info("Unified FastAPI application created successfully")
    return app

# Create the application instance
app = create_unified_app()

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "unified_app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )