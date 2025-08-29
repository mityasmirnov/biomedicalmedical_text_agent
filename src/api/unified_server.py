"""
Unified Server for Biomedical Text Agent

This server integrates the unified API with proper CORS, middleware,
and startup/shutdown handling for the complete system.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import uvicorn
from pathlib import Path
import asyncio
import signal
import sys

try:
    from .unified_api import api_router
    from core.config import get_config
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.api.unified_api import api_router
    from src.core.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for graceful shutdown
shutdown_event = asyncio.Event()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    logger.info("Starting Biomedical Text Agent Unified Server...")
    
    try:
        # Mount static files if they exist
        static_dir = Path("src/ui/frontend/build")
        if static_dir.exists():
            app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
            logger.info("Static files mounted successfully")
        else:
            logger.warning("Static files directory not found, skipping mount")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Biomedical Text Agent Unified Server...")
        logger.info("Server shutdown complete")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = get_config()
    
    # Create FastAPI app with lifespan management
    app = FastAPI(
        title="Biomedical Text Agent API",
        description="Unified API for biomedical literature analysis and patient data extraction",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.security.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure appropriately for production
    )
    
    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if config.debug else "An unexpected error occurred",
                "timestamp": asyncio.get_event_loop().time()
            }
        )
    
    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = asyncio.get_event_loop().time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = asyncio.get_event_loop().time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
        
        return response
    
    # Include API routes
    app.include_router(api_router, prefix="/api")
    
    # Add health check endpoint at root
    @app.get("/health")
    async def health_check():
        """Root health check endpoint."""
        try:
            orchestrator = await get_orchestrator()
            status = await orchestrator.get_system_status()
            
            return {
                "status": "healthy" if status.overall_status == "healthy" else "degraded",
                "service": "biomedical-text-agent",
                "version": "2.0.0",
                "timestamp": asyncio.get_event_loop().time(),
                "system_status": status.overall_status
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": "biomedical-text-agent",
                "version": "2.0.0",
                "timestamp": asyncio.get_event_loop().time(),
                "error": str(e)
            }
    
    # Add root endpoint
    @app.get("/")
    async def root():
        """Root endpoint that serves the frontend or redirects to API."""
        return {
            "service": "Biomedical Text Agent",
            "version": "2.0.0",
            "status": "running",
            "endpoints": {
                "api": "/api",
                "docs": "/api/docs",
                "health": "/health"
            },
            "message": "Welcome to the Biomedical Text Agent. Use /api for API access or /api/docs for documentation."
        }
    
    return app

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()
    sys.exit(0)

def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run the unified server."""
    config = get_config()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create the application
    app = create_app()
    
    # Configure uvicorn settings
    uvicorn_config = {
        "app": app,
        "host": host,
        "port": port,
        "reload": reload,
        "log_level": config.monitoring.log_level.lower(),
        "access_log": True,
        "use_colors": True,
        "loop": "asyncio"
    }
    
    # Add SSL configuration if needed
    if config.environment == "production":
        # Configure SSL for production
        pass
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Debug mode: {config.debug}")
    logger.info(f"API documentation available at: http://{host}:{port}/api/docs")
    
    try:
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

def main():
    """Main entry point for the unified server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Biomedical Text Agent Unified Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Load configuration if specified
    if args.config:
        from core.unified_config import UnifiedConfig
        config = UnifiedConfig.load_from_file(args.config)
        logger.info(f"Configuration loaded from {args.config}")
    
    # Run the server
    run_server(
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()