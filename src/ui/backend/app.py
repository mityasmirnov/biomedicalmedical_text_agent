"""
FastAPI Backend Application

Main FastAPI application for the biomedical text agent UI backend.
Provides REST API endpoints, WebSocket connections, and static file serving.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
import uvicorn
from typing import List
from starlette.responses import FileResponse

# Fix imports to work from backend directory
import sys
sys.path.append(str(Path(__file__).parent))

from api import api_router  # relative import
# from websocket_manager import WebSocketManager
# from auth import AuthManager
# from database import DatabaseManager
# from config import UIConfig


# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Minimal placeholders (no heavy services for boot)
# websocket_manager = WebSocketManager()
# auth_manager = AuthManager()
# db_manager = DatabaseManager()


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


def create_app(config: Optional[object] = None) -> FastAPI:
    if config is None:
        config = object()
    app = FastAPI(
        title="Biomedical Text Agent UI",
        description="Web interface for biomedical literature extraction and analysis",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    app.include_router(api_router, prefix="/api/v1")

    # Health endpoint
    @app.get("/api/health")
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    # WebSocket endpoint
    @app.websocket("/api/v1/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await manager.connect(websocket)
        try:
            while True:
                _ = await websocket.receive_text()
                await manager.broadcast("pong")
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    # Serve static frontend (React build) if present
    frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"
    if frontend_build_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")

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


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    config: Optional[object] = None
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
    
    if reload:
        # For development with reload, use uvicorn.run with reload
        uvicorn.run(
            "app:create_app",
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
    run_server(reload=False)  # Disable reload for now to avoid issues

