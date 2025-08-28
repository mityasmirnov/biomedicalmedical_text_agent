"""
Enhanced FastAPI server for Biomedical Text Agent with full functionality.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from pathlib import Path

# Import our enhanced endpoints
from .enhanced_endpoints import enhanced_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_enhanced_app() -> FastAPI:
    """Create and configure the enhanced FastAPI application."""
    
    app = FastAPI(
        title="Biomedical Text Agent API",
        description="Enhanced API for biomedical literature processing and extraction",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Add CORS middleware for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include enhanced API router
    app.include_router(enhanced_router, prefix="/api")
    
    # Health check endpoint
    @app.get("/", response_class=HTMLResponse)
    async def root():
        return """
        <html>
            <head>
                <title>Biomedical Text Agent API</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                    .method { font-weight: bold; color: #1976d2; }
                    .url { font-family: monospace; background: #e3f2fd; padding: 2px 6px; border-radius: 3px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 Biomedical Text Agent API</h1>
                    <p>Enhanced API server is running successfully!</p>
                    
                    <h2>Available Endpoints</h2>
                    
                    <div class="endpoint">
                        <div class="method">GET</div>
                        <div class="url">/api/health</div>
                        <div>Health check endpoint</div>
                    </div>
                    
                    <div class="endpoint">
                        <div class="method">GET</div>
                        <div class="url">/api/dashboard/status</div>
                        <div>System status and health</div>
                    </div>
                    
                    <div class="endpoint">
                        <div class="method">POST</div>
                        <div class="url">/api/metadata/search</div>
                        <div>Search literature metadata</div>
                    </div>
                    
                    <div class="endpoint">
                        <div class="method">POST</div>
                        <div class="url">/api/documents/upload</div>
                        <div>Upload documents for processing</div>
                    </div>
                    
                    <div class="endpoint">
                        <div class="method">GET</div>
                        <div class="url">/api/validation/{extraction_id}</div>
                        <div>Get extraction data for validation</div>
                    </div>
                    
                    <div class="endpoint">
                        <div class="method">GET</div>
                        <div class="url">/api/database/tables</div>
                        <div>Browse database tables</div>
                    </div>
                    
                    <div class="endpoint">
                        <div class="method">GET</div>
                        <div class="url">/api/config/providers</div>
                        <div>Configure API providers</div>
                    </div>
                    
                    <div class="endpoint">
                        <div class="method">GET</div>
                        <div class="url">/api/ontologies</div>
                        <div>Browse ontologies</div>
                    </div>
                    
                    <div class="endpoint">
                        <div class="method">GET</div>
                        <div class="url">/api/prompts</div>
                        <div>Manage system prompts</div>
                    </div>
                    
                    <div class="endpoint">
                        <div class="method">GET</div>
                        <div class="url">/api/analytics/visualizations</div>
                        <div>Data visualizations</div>
                    </div>
                    
                    <h2>Documentation</h2>
                    <p>
                        <a href="/api/docs" target="_blank">📚 Interactive API Documentation (Swagger)</a><br>
                        <a href="/api/redoc" target="_blank">📖 Alternative Documentation (ReDoc)</a>
                    </p>
                    
                    <h2>Frontend</h2>
                    <p>Access the UI at: <a href="http://localhost:3000" target="_blank">http://localhost:3000</a></p>
                    
                    <h2>Status</h2>
                    <p>✅ API Server: Running</p>
                    <p>✅ CORS: Enabled for frontend</p>
                    <p>✅ Enhanced Endpoints: Loaded</p>
                </div>
            </body>
        </html>
        """
    
    # Error handlers
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return HTMLResponse(
            content="""
            <html>
                <head><title>404 - Not Found</title></head>
                <body>
                    <h1>404 - Endpoint Not Found</h1>
                    <p>The requested endpoint does not exist.</p>
                    <p><a href="/">Return to API Home</a></p>
                </body>
            </html>
            """,
            status_code=404
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        return HTMLResponse(
            content="""
            <html>
                <head><title>500 - Internal Server Error</title></head>
                <body>
                    <h1>500 - Internal Server Error</h1>
                    <p>Something went wrong on our end.</p>
                    <p><a href="/">Return to API Home</a></p>
                </body>
            </html>
            """,
            status_code=500
        )
    
    logger.info("Enhanced FastAPI application created successfully")
    return app

def run_enhanced_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True
):
    """Run the enhanced server."""
    
    app = create_enhanced_app()
    
    logger.info(f"Starting enhanced server on {host}:{port}")
    logger.info("Frontend should be accessible at: http://localhost:3000")
    logger.info("API documentation at: http://localhost:8000/api/docs")
    
    uvicorn.run(
        "src.api.enhanced_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

# Create app instance for uvicorn
app = create_enhanced_app()

if __name__ == "__main__":
    run_enhanced_server()
