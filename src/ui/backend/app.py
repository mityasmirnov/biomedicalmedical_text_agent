"""
FastAPI Backend Application

Main FastAPI application for the biomedical text agent UI backend.
Provides REST API endpoints, WebSocket connections, and static file serving.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

from api import api_router
from src.ui.backend.websocket_manager import WebSocketManager
from src.ui.backend.auth import AuthManager
from src.database import DatabaseManager
from src.ui.config import UIConfig


# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
websocket_manager = WebSocketManager()
auth_manager = AuthManager()
db_manager = DatabaseManager()


def create_app(config: Optional[UIConfig] = None) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        config: UI configuration object
        
    Returns:
        Configured FastAPI application
    """
    if config is None:
        config = UIConfig()
    
    # Create FastAPI app
    app = FastAPI(
        title="Biomedical Text Agent UI",
        description="Web interface for biomedical literature extraction and analysis",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    # Add WebSocket manager to app state
    app.state.websocket_manager = websocket_manager
    app.state.auth_manager = auth_manager
    app.state.db_manager = db_manager
    app.state.config = config
    
    # Serve static files (React build)
    frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"
    if frontend_build_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")
        
        @app.get("/", response_class=HTMLResponse)
        @app.get("/{path:path}", response_class=HTMLResponse)
        async def serve_frontend(path: str = ""):
            """Serve React frontend for all routes."""
            index_file = frontend_build_path / "index.html"
            if index_file.exists():
                return HTMLResponse(content=index_file.read_text(), status_code=200)
            else:
                raise HTTPException(status_code=404, detail="Frontend not built")
    else:
        @app.get("/")
        async def root():
            return {
                "message": "Biomedical Text Agent API",
                "docs": "/api/docs",
                "frontend": "Not built - run 'npm run build' in frontend directory"
            }
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup."""
        logger.info("Starting Biomedical Text Agent UI...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Initialize auth manager
        await auth_manager.initialize()
        
        logger.info("UI Backend started successfully")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        logger.info("Shutting down Biomedical Text Agent UI...")
        
        # Close WebSocket connections
        await websocket_manager.disconnect_all()
        
        # Close database connections
        await db_manager.close()
        
        logger.info("UI Backend shutdown complete")
    
    return app


# Dependency for getting current user
security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """Get current authenticated user."""
    auth_manager = request.app.state.auth_manager
    
    if not credentials:
        return None
    
    try:
        user = await auth_manager.verify_token(credentials.credentials)
        return user
    except Exception as e:
        logger.warning(f"Authentication failed: {e}")
        return None


async def require_auth(user=Depends(get_current_user)):
    """Require authentication for protected endpoints."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "biomedical-text-agent-ui",
        "version": "1.0.0"
    }


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    config: Optional[UIConfig] = None
):
    """
    Run the FastAPI server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
        config: UI configuration
    """
    app = create_app(config)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    # Development server
    run_server(reload=True)

