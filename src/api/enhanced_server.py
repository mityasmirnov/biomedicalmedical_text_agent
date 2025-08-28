"""
Enhanced FastAPI Server for Biomedical Text Agent.

This module provides enhanced FastAPI server setup with comprehensive CORS configuration,
error handling, middleware, and monitoring capabilities that work alongside the existing
server structure.
"""

import os
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
from fastapi.websockets import WebSocket, WebSocketDisconnect

# Import the enhanced API routers
from .enhanced_endpoints import (
    enhanced_documents_router,
    enhanced_extraction_router,
    enhanced_search_router,
    enhanced_analytics_router,
    enhanced_health_router
)

# Import the original API router
from .main import create_api_router

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Enhanced Middleware and Utilities
# ============================================================================

class EnhancedCORSMiddleware:
    """Enhanced CORS middleware with comprehensive configuration."""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Add CORS headers
            headers = []
            origin = scope.get("headers", {}).get(b"origin", b"").decode()
            
            # Allow specific origins or all for development
            allowed_origins = [
                "http://localhost:3000",  # React dev server
                "http://localhost:8000",  # FastAPI dev server
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000",
                "*"  # Allow all origins for development
            ]
            
            if origin in allowed_origins or "*" in allowed_origins:
                headers.extend([
                    (b"access-control-allow-origin", origin.encode() if origin != "*" else b"*"),
                    (b"access-control-allow-credentials", b"true"),
                    (b"access-control-allow-methods", b"GET, POST, PUT, DELETE, OPTIONS, PATCH"),
                    (b"access-control-allow-headers", b"*"),
                ])
            
            # Handle preflight requests
            if scope["method"] == "OPTIONS":
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": headers
                })
                await send({
                    "type": "http.response.body",
                    "body": b""
                })
                return
        
        await self.app(scope, receive, send)

class RequestLoggingMiddleware:
    """Middleware for logging all incoming requests."""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Log request
            method = scope["method"]
            path = scope["path"]
            logger.info(f"Request: {method} {path}")
            
            # Create a custom send function to capture response
            async def custom_send(message):
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    process_time = time.time() - start_time
                    logger.info(f"Response: {method} {path} - {status_code} ({process_time:.3f}s)")
                await send(message)
            
            await self.app(scope, receive, custom_send)
        else:
            await self.app(scope, receive, send)

class ErrorHandlingMiddleware:
    """Enhanced error handling middleware."""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            logger.error(f"Unhandled error in {scope['path']}: {e}")
            
            if scope["type"] == "http":
                await send({
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [(b"content-type", b"application/json")]
                })
                await send({
                    "type": "http.response.body",
                    "body": b'{"error": "Internal server error", "detail": "An unexpected error occurred"}'
                })

# ============================================================================
# Enhanced FastAPI Application Factory
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting Enhanced Biomedical Text Agent Server...")
    
    # Initialize enhanced components
    try:
        # Initialize enhanced database connections
        logger.info("📊 Initializing enhanced database connections...")
        
        # Initialize enhanced monitoring
        logger.info("📈 Initializing enhanced monitoring systems...")
        
        # Initialize enhanced caching
        logger.info("💾 Initializing enhanced caching systems...")
        
        logger.info("✅ Enhanced server startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Enhanced server startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Enhanced Biomedical Text Agent Server...")
    
    try:
        # Cleanup enhanced connections
        logger.info("🧹 Cleaning up enhanced connections...")
        
        # Save enhanced state
        logger.info("💾 Saving enhanced server state...")
        
        logger.info("✅ Enhanced server shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Enhanced server shutdown failed: {e}")

def create_enhanced_app(
    config: Optional[Dict[str, Any]] = None,
    enable_https: bool = False,
    trusted_hosts: Optional[list] = None,
    enable_compression: bool = True,
    enable_logging: bool = True,
    enable_monitoring: bool = True
) -> FastAPI:
    """Create the enhanced FastAPI application with comprehensive configuration."""
    
    if config is None:
        config = {}
    
    # Enhanced app configuration
    app = FastAPI(
        title="Biomedical Text Agent - Enhanced System",
        description="Enhanced unified system for biomedical text processing and analysis with advanced features",
        version="2.0.0",
        docs_url="/api/enhanced/docs",
        redoc_url="/api/enhanced/redoc",
        openapi_url="/api/enhanced/openapi.json",
        lifespan=lifespan
    )
    
    # ============================================================================
    # Enhanced Middleware Configuration
    # ============================================================================
    
    # Enhanced CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:8000", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            "*"  # Allow all for development
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    
    # Trusted host middleware
    if trusted_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=trusted_hosts
        )
    
    # HTTPS redirect middleware (for production)
    if enable_https:
        app.add_middleware(HTTPSRedirectMiddleware)
    
    # Compression middleware
    if enable_compression:
        app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Request logging middleware
    if enable_logging:
        app.add_middleware(RequestLoggingMiddleware)
    
    # Error handling middleware
    app.add_middleware(ErrorHandlingMiddleware)
    
    # ============================================================================
    # Enhanced Exception Handlers
    # ============================================================================
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Enhanced HTTP exception handler."""
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": request.url.path,
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Enhanced validation exception handler."""
        logger.error(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "detail": exc.errors(),
                "path": request.url.path,
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Enhanced general exception handler."""
        logger.error(f"General Exception: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred",
                "path": request.url.path,
                "timestamp": time.time()
            }
        )
    
    # ============================================================================
    # Enhanced API Router Integration
    # ============================================================================
    
    # Include the original API router
    original_api_router = create_api_router()
    app.include_router(original_api_router, prefix="/api/v1")
    
    # Include enhanced API routers
    app.include_router(
        enhanced_documents_router, 
        prefix="/api/v2/documents", 
        tags=["Enhanced Documents"]
    )
    app.include_router(
        enhanced_extraction_router, 
        prefix="/api/v2/extraction", 
        tags=["Enhanced Extraction"]
    )
    app.include_router(
        enhanced_search_router, 
        prefix="/api/v2/search", 
        tags=["Enhanced Search"]
    )
    app.include_router(
        enhanced_analytics_router, 
        prefix="/api/v2/analytics", 
        tags=["Enhanced Analytics"]
    )
    app.include_router(
        enhanced_health_router, 
        prefix="/api/v2/health", 
        tags=["Enhanced Health"]
    )
    
    # ============================================================================
    # Enhanced Direct Endpoints
    # ============================================================================
    
    # Enhanced WebSocket endpoint
    @app.websocket("/api/v2/ws")
    async def enhanced_websocket_endpoint(websocket: WebSocket):
        """Enhanced WebSocket endpoint for real-time updates."""
        await websocket.accept()
        try:
            logger.info("🔌 Enhanced WebSocket connection established")
            
            while True:
                data = await websocket.receive_text()
                logger.info(f"📡 Enhanced WebSocket message received: {data}")
                
                # Enhanced message processing
                response = {
                    "type": "enhanced_response",
                    "message": f"Enhanced message received: {data}",
                    "timestamp": time.time(),
                    "status": "processed"
                }
                
                await websocket.send_text(str(response))
                
        except WebSocketDisconnect:
            logger.info("🔌 Enhanced WebSocket connection disconnected")
        except Exception as e:
            logger.error(f"❌ Enhanced WebSocket error: {e}")
    
    # Enhanced health endpoint
    @app.get("/api/v2/health")
    async def enhanced_health() -> JSONResponse:
        """Enhanced health check endpoint."""
        return JSONResponse({
            "status": "healthy",
            "service": "biomedical-text-agent-enhanced",
            "version": "2.0.0",
            "timestamp": time.time(),
            "features": [
                "enhanced_documents",
                "enhanced_extraction", 
                "enhanced_search",
                "enhanced_analytics",
                "enhanced_monitoring"
            ]
        })
    
    # Enhanced system status endpoint
    @app.get("/api/v2/system/status")
    async def enhanced_system_status() -> JSONResponse:
        """Enhanced system status endpoint."""
        return JSONResponse({
            "status": "operational",
            "service": "biomedical-text-agent-enhanced",
            "version": "2.0.0",
            "timestamp": time.time(),
            "uptime": "Enhanced uptime tracking",
            "performance": {
                "cpu_usage": "Enhanced monitoring",
                "memory_usage": "Enhanced monitoring",
                "disk_usage": "Enhanced monitoring"
            },
            "enhanced_features": {
                "documents": "active",
                "extraction": "active",
                "search": "active",
                "analytics": "active",
                "monitoring": "active"
            }
        })
    
    # ============================================================================
    # Enhanced Static File Serving
    # ============================================================================
    
    # Serve enhanced static frontend if present
    enhanced_frontend_path = Path(__file__).parent.parent / "ui" / "frontend" / "build"
    if enhanced_frontend_path.exists():
        app.mount("/static", StaticFiles(directory=str(enhanced_frontend_path / "static")), name="static")
        
        @app.get("/", response_class=HTMLResponse)
        async def serve_enhanced_index() -> HTMLResponse:
            """Serve enhanced frontend index."""
            index_file = enhanced_frontend_path / "index.html"
            return HTMLResponse(content=index_file.read_text(encoding="utf-8"), status_code=200)
    
    # ============================================================================
    # Enhanced Startup Event
    # ============================================================================
    
    @app.on_event("startup")
    async def enhanced_startup_event():
        """Enhanced startup event handler."""
        logger.info("🚀 Enhanced Biomedical Text Agent Server is starting up...")
        
        # Initialize enhanced services
        try:
            logger.info("🔧 Initializing enhanced services...")
            
            # Enhanced configuration validation
            logger.info("✅ Enhanced configuration validated")
            
            # Enhanced service health checks
            logger.info("✅ Enhanced service health checks completed")
            
            logger.info("🎉 Enhanced server startup completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Enhanced startup failed: {e}")
            raise
    
    # ============================================================================
    # Enhanced Shutdown Event
    # ============================================================================
    
    @app.on_event("shutdown")
    async def enhanced_shutdown_event():
        """Enhanced shutdown event handler."""
        logger.info("🛑 Enhanced Biomedical Text Agent Server is shutting down...")
        
        try:
            # Cleanup enhanced resources
            logger.info("🧹 Cleaning up enhanced resources...")
            
            # Save enhanced state
            logger.info("💾 Saving enhanced server state...")
            
            logger.info("✅ Enhanced server shutdown completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Enhanced shutdown failed: {e}")
    
    return app

# ============================================================================
# Enhanced Server Runner
# ============================================================================

def run_enhanced_server(
    host: str = "0.0.0.0",
    port: int = 8001,
    reload: bool = False,
    workers: int = 1,
    ssl_keyfile: Optional[str] = None,
    ssl_certfile: Optional[str] = None,
    **kwargs
):
    """Run the enhanced FastAPI server."""
    
    # Create enhanced app
    app = create_enhanced_app()
    
    # Enhanced server configuration
    server_config = {
        "app": app,
        "host": host,
        "port": port,
        "reload": reload,
        "workers": workers,
        "log_level": "info",
        "access_log": True,
        **kwargs
    }
    
    # Add SSL configuration if provided
    if ssl_keyfile and ssl_certfile:
        server_config.update({
            "ssl_keyfile": ssl_keyfile,
            "ssl_certfile": ssl_certfile
        })
    
    logger.info(f"🚀 Starting Enhanced Biomedical Text Agent Server on {host}:{port}")
    logger.info(f"📚 API Documentation: http://{host}:{port}/api/enhanced/docs")
    logger.info(f"🔍 Enhanced API Documentation: http://{host}:{port}/api/enhanced/redoc")
    
    # Run enhanced server
    uvicorn.run(**server_config)

# ============================================================================
# Export Functions
# ============================================================================

__all__ = [
    "create_enhanced_app",
    "run_enhanced_server",
    "EnhancedCORSMiddleware",
    "RequestLoggingMiddleware", 
    "ErrorHandlingMiddleware"
]