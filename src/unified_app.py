"""
Unified FastAPI Application for Biomedical Text Agent.

This module creates a single FastAPI application that serves both the API endpoints
and the React frontend, consolidating all functionality into one application.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
import uvicorn
from fastapi.websockets import WebSocket, WebSocketDisconnect

# Import the unified API router
from api.main import create_api_router

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_unified_app(config: Optional[object] = None) -> FastAPI:
    """Create the unified FastAPI application."""
    if config is None:
        config = object()
    
    app = FastAPI(
        title="Biomedical Text Agent - Unified System",
        description="Unified system for biomedical text processing and analysis",
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

    # Include the unified API router
    api_router = create_api_router()
    app.include_router(api_router, prefix="/api/v1")

    # Direct WebSocket endpoint for frontend
    @app.websocket("/api/v1/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates."""
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                # Echo back for now, can be extended for real-time updates
                await websocket.send_text(f"Message received: {data}")
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket error: {e}")

    # Health endpoint
    @app.get("/api/health")
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok", "service": "biomedical-text-agent"})

    # System status endpoint
    @app.get("/api/v1/system/status")
    async def system_status() -> JSONResponse:
        return JSONResponse({
            "status": "operational",
            "service": "biomedical-text-agent",
            "version": "1.0.0",
            "timestamp": "2024-01-01T00:00:00Z"
        })

    # Serve static frontend (React build) if present
    frontend_build_path = Path(__file__).parent / "ui" / "frontend" / "build"
    if frontend_build_path.exists():
        # Mount static files
        app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")
        
        # Serve index.html for root and SPA routes
        @app.get("/", response_class=HTMLResponse)
        async def serve_index() -> HTMLResponse:
            index_file = frontend_build_path / "index.html"
            return HTMLResponse(content=index_file.read_text(encoding="utf-8"), status_code=200)

        # SPA fallback for frontend routes - only catch non-API routes
        @app.get("/{full_path:path}")
        async def spa_fallback(full_path: str) -> HTMLResponse:
            # Don't serve frontend for API routes or static files
            if full_path.startswith(("api/", "static/")):
                raise HTTPException(status_code=404, detail="Not found")
            
            index_file = frontend_build_path / "index.html"
            return HTMLResponse(content=index_file.read_text(encoding="utf-8"), status_code=200)
    else:
        @app.get("/")
        async def root():
            return {
                "message": "Biomedical Text Agent API",
                "docs": "/api/docs",
                "frontend": "Not built - run 'npm run build' in src/ui/frontend"
            }

    # Favicon (prevent 404 spam)
    @app.get("/favicon.ico")
    async def favicon() -> Response:
        return Response(status_code=204)

    return app

def run_unified_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    config: Optional[object] = None
):
    """
    Run the unified FastAPI server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
        config: Configuration object
    """
    app = create_unified_app(config)
    
    if reload:
        # For development with reload, use uvicorn.run with reload
        uvicorn.run(
            "unified_app:create_unified_app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    else:
        # For production, use uvicorn.run without reload
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )

if __name__ == "__main__":
    # Development server
    run_unified_server(reload=False)