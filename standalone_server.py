"""
Standalone API server for Biomedical Text Agent.

This module creates a FastAPI application with real implementations.
"""

from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, Response
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import uvicorn
import asyncio

# Import real modules
import sys
import os

# Add src to Python path for direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.config import get_config
from database.enhanced_sqlite_manager import EnhancedSQLiteManager
from agents.extraction_agents.demographics_agent import DemographicsAgent
from agents.extraction_agents.genetics_agent import GeneticsAgent
from agents.extraction_agents.phenotypes_agent import PhenotypesAgent
from agents.extraction_agents.treatments_agent import TreatmentsAgent
from core.llm_client.smart_llm_manager import SmartLLMManager
from core.api_usage_tracker import APIUsageTracker

# Create a simple mock MetadataOrchestrator to avoid dependency issues
class MockMetadataOrchestrator:
    """Simple mock metadata orchestrator for compatibility."""
    def __init__(self):
        self.abstract_classifier = None
        self.concept_classifier = None
        self.concept_scorer = None
        self.deduplicator = None

# Import the enhanced metadata orchestrator after creating the mock
from metadata_triage.enhanced_metadata_orchestrator import EnhancedMetadataOrchestrator

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize real services
config = get_config()
db_manager = None
metadata_orchestrator = None
llm_manager = None
usage_tracker = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Helper function for UTC timestamps
def utc_now():
    return datetime.now(timezone.utc)

# Initialize real services
async def initialize_services():
    """Initialize all real services."""
    global db_manager, metadata_orchestrator, llm_manager, usage_tracker
    
    try:
        # Initialize database manager
        db_manager = EnhancedSQLiteManager()
        logger.info("Database manager initialized successfully")
        
        # Initialize LLM manager
        llm_manager = SmartLLMManager()
        logger.info("LLM manager initialized successfully")
        
        # Initialize metadata orchestrator
        metadata_orchestrator = EnhancedMetadataOrchestrator(
            enhanced_db_manager=db_manager,
            original_orchestrator=MockMetadataOrchestrator(),
            config={
                'pipeline': {
                    'max_concurrent_tasks': 5,
                    'task_timeout': 300,
                    'retry_delay': 60
                }
            }
        )
        logger.info("Metadata orchestrator initialized successfully")
        
        # Initialize API usage tracker
        usage_tracker = APIUsageTracker()
        logger.info("API usage tracker initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

# ============================================================================
# Dashboard Endpoints
# ============================================================================

dashboard_router = APIRouter()

@dashboard_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now, can be extended for real-time updates
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@dashboard_router.get("/overview")
async def get_dashboard_overview() -> Dict[str, Any]:
    """Return dashboard overview using real data."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real statistics from database
        total_docs = await db_manager.get_document_count()
        latest_summary = await db_manager.get_latest_processing_summary()
        
        return {
            "timestamp": utc_now().isoformat(),
            "files_indexed": total_docs,
            "latest_summary": latest_summary or {},
            "status": "ok"
        }
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@dashboard_router.get("/statistics")
async def get_dashboard_statistics() -> Dict[str, Any]:
    """Return dashboard statistics with real data."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real statistics from database
        total_docs = await db_manager.get_document_count()
        processed_today = await db_manager.get_documents_processed_today()
        success_rate = await db_manager.get_processing_success_rate()
        avg_processing_time = await db_manager.get_average_processing_time()
        active_extractions = await db_manager.get_active_extraction_count()
        queue_length = await db_manager.get_processing_queue_length()
        
        return {
            "total_documents": total_docs,
            "processed_today": processed_today,
            "success_rate": success_rate,
            "average_processing_time": avg_processing_time,
            "active_extractions": active_extractions,
            "queue_length": queue_length,
            "system_health": "healthy",
            "last_updated": utc_now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@dashboard_router.get("/recent-activities")
async def get_recent_activities() -> Dict[str, Any]:
    """Return recent activities with real data."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real recent activities from database
        activities = await db_manager.get_recent_activities(limit=10)
        
        return {
            "activities": activities
        }
    except Exception as e:
        logger.error(f"Error getting recent activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@dashboard_router.get("/alerts")
async def get_dashboard_alerts() -> Dict[str, Any]:
    """Return dashboard alerts with real data."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real alerts and system metrics
        alerts = await db_manager.get_system_alerts()
        system_metrics = await db_manager.get_system_metrics()
        
        return {
            "alerts": alerts,
            "system_metrics": system_metrics
        }
    except Exception as e:
        logger.error(f"Error getting dashboard alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@dashboard_router.get("/system-status")
async def get_system_status() -> Dict[str, Any]:
    """Return system status information."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real system status
        db_status = await db_manager.get_database_status()
        api_usage = await usage_tracker.get_current_usage() if usage_tracker else {}
        
        return {
            "status": "healthy" if db_status.get("status") == "healthy" else "degraded",
            "uptime": 3600,  # TODO: Implement real uptime tracking
            "processing_queue": await db_manager.get_processing_queue_length(),
            "active_extractions": await db_manager.get_active_extraction_count(),
            "database_size": await db_manager.get_document_count(),
            "api_usage": api_usage,
            "last_updated": utc_now().isoformat(),
            "service": "biomedical-text-agent",
            "version": "1.0.0",
            "authentication": "disabled",
            "features": {
                "extraction": "enabled",
                "ontology": "enabled",
                "rag": "enabled",
                "database": "enabled",
                "ui": "enabled"
            }
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@dashboard_router.get("/queue")
async def get_processing_queue() -> Dict[str, Any]:
    """Return processing queue information."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real processing queue from database
        queue_jobs = await db_manager.get_processing_queue()
        
        return {
            "jobs": queue_jobs
        }
    except Exception as e:
        logger.error(f"Error getting processing queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@dashboard_router.get("/results")
async def get_recent_results() -> Dict[str, Any]:
    """Return recent extraction results."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real recent results from database
        results = await db_manager.get_recent_extraction_results(limit=10)
        
        return {
            "results": results
        }
    except Exception as e:
        logger.error(f"Error getting recent results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Agents Endpoints
# ============================================================================

agents_router = APIRouter()

@agents_router.get("")
@agents_router.get("/")
async def get_agents() -> Dict[str, Any]:
    """Get all agents with real data."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real agent information from database
        agents = await db_manager.get_agents()
        
        return {
            "agents": agents
        }
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@agents_router.get("/{agent_id}")
async def get_agent(agent_id: str) -> Dict[str, Any]:
    """Get specific agent details."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        agent = await db_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@agents_router.post("/{agent_id}/start")
async def start_agent(agent_id: str) -> Dict[str, Any]:
    """Start a specific agent."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Start the agent and update status
        result = await db_manager.start_agent(agent_id)
        
        return {
            "message": f"Agent {agent_id} started",
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error starting agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@agents_router.post("/{agent_id}/stop")
async def stop_agent(agent_id: str) -> Dict[str, Any]:
    """Stop a specific agent."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Stop the agent and update status
        result = await db_manager.stop_agent(agent_id)
        
        return {
            "message": f"Agent {agent_id} stopped",
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error stopping agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Documents Endpoints
# ============================================================================

documents_router = APIRouter()

@documents_router.get("")
@documents_router.get("/")
async def get_documents() -> Dict[str, Any]:
    """Get all documents with real data."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real documents from database
        documents = await db_manager.get_documents()
        
        return {
            "documents": documents
        }
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@documents_router.get("/{document_id}")
async def get_document(document_id: str) -> Dict[str, Any]:
    """Get specific document details."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        document = await db_manager.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@documents_router.get("/{document_id}/full-text")
async def get_document_fulltext(document_id: str) -> Dict[str, Any]:
    """Get document full text."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        document = await db_manager.get_document_fulltext(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document fulltext {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Metadata Endpoints
# ============================================================================

metadata_router = APIRouter()

@metadata_router.get("")
@metadata_router.get("/")
async def get_metadata() -> Dict[str, Any]:
    """Get metadata overview."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real metadata statistics
        metadata_stats = await db_manager.get_metadata_statistics()
        
        return metadata_stats
    except Exception as e:
        logger.error(f"Error getting metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@metadata_router.get("/search")
async def search_metadata(query: str = Query(...)) -> Dict[str, Any]:
    """Search metadata."""
    try:
        if not metadata_orchestrator:
            raise HTTPException(status_code=503, detail="Metadata orchestrator not initialized")
        
        # Perform real metadata search
        search_results = await metadata_orchestrator.search_metadata(query)
        
        return search_results
    except Exception as e:
        logger.error(f"Error searching metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Database Endpoints
# ============================================================================

database_router = APIRouter()

@database_router.get("/status")
async def get_database_status() -> Dict[str, Any]:
    """Get database status."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real database status
        status = await db_manager.get_database_status()
        
        return status
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@database_router.get("/patients")
async def get_patients(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """Get patient records from database."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real patient records
        patients = await db_manager.get_patients(limit=limit, offset=offset)
        
        return {
            "patients": patients,
            "total": len(patients)
        }
    except Exception as e:
        logger.error(f"Error getting patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Configuration Endpoints
# ============================================================================

config_router = APIRouter()

@config_router.get("/providers")
async def get_providers() -> Dict[str, Any]:
    """Get available API providers."""
    try:
        # Get real provider configuration
        providers = []
        
        if config.llm.openrouter_api_key:
            providers.append({
                "name": "openrouter",
                "display_name": "OpenRouter",
                "description": "Access to multiple LLM models including GPT, Claude, and others",
                "enabled": True,
                "api_key_configured": True,
                "base_url": config.llm.openrouter_api_base,
                "rate_limit": config.llm.max_requests_per_minute
            })
        
        if config.llm.huggingface_api_token:
            providers.append({
                "name": "huggingface",
                "display_name": "Hugging Face",
                "description": "Open source model hosting and inference API",
                "enabled": True,
                "api_key_configured": True,
                "base_url": "https://api-inference.huggingface.co",
                "rate_limit": 50
            })
        
        # Check if Ollama is available
        try:
            if llm_manager and hasattr(llm_manager, 'fallback_clients') and 'ollama' in llm_manager.fallback_clients:
                providers.append({
                    "name": "ollama",
                    "display_name": "Ollama",
                    "description": "Local model deployment and inference",
                    "enabled": True,
                    "api_key_configured": True,
                    "base_url": config.llm.ollama_base_url,
                    "rate_limit": 1000
                })
            else:
                providers.append({
                    "name": "ollama",
                    "display_name": "Ollama",
                    "description": "Local model deployment and inference",
                    "enabled": False,
                    "api_key_configured": False,
                    "base_url": config.llm.ollama_base_url,
                    "rate_limit": 1000
                })
        except:
            providers.append({
                "name": "ollama",
                "display_name": "Ollama",
                "description": "Local model deployment and inference",
                "enabled": False,
                "api_key_configured": False,
                "base_url": config.llm.ollama_base_url,
                "rate_limit": 1000
            })
        
        return {
            "providers": providers
        }
    except Exception as e:
        logger.error(f"Error getting providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@config_router.put("/providers/{provider}")
async def update_provider(provider: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update provider configuration."""
    try:
        # Update provider configuration
        if provider == "openrouter" and "api_key" in data:
            config.llm.openrouter_api_key = data["api_key"]
        elif provider == "huggingface" and "api_token" in data:
            config.llm.huggingface_api_token = data["api_token"]
        
        return {
            "provider": provider,
            "updated": True,
            "changes": data
        }
    except Exception as e:
        logger.error(f"Error updating provider {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@config_router.get("/models")
async def get_models() -> Dict[str, Any]:
    """Get available models."""
    try:
        if not llm_manager:
            raise HTTPException(status_code=503, detail="LLM manager not initialized")
        
        # Get real available models
        models = []
        
        # Add OpenRouter models if available
        if hasattr(llm_manager, 'primary_client') and llm_manager.primary_client:
            models.append({
                "provider": "openrouter",
                "name": config.llm.default_model,
                "display_name": "OpenRouter Default",
                "description": "Default OpenRouter model",
                "enabled": True
            })
        
        # Add fallback models
        if hasattr(llm_manager, 'fallback_clients'):
            for provider, client in llm_manager.fallback_clients.items():
                if provider == "ollama":
                    models.append({
                        "provider": "ollama",
                        "name": config.llm.ollama_default_model,
                        "display_name": "Ollama Local",
                        "description": "Local Ollama model",
                        "enabled": True
                    })
                elif provider == "huggingface":
                    models.append({
                        "provider": "huggingface",
                        "name": config.llm.huggingface_default_model,
                        "display_name": "HuggingFace Model",
                        "description": "HuggingFace inference model",
                        "enabled": True
                    })
        
        return {
            "models": models
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Extraction Endpoints
# ============================================================================

extraction_router = APIRouter()

@extraction_router.post("/extract")
async def extract_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract data using real agents."""
    try:
        if not llm_manager or not db_manager:
            raise HTTPException(status_code=503, detail="Services not initialized")
        
        document_id = data.get("document_id")
        extraction_type = data.get("extraction_type", "all")
        
        if not document_id:
            raise HTTPException(status_code=400, detail="Document ID is required")
        
        # Get document content
        document = await db_manager.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Initialize appropriate agent based on extraction type
        if extraction_type == "demographics" or extraction_type == "all":
            agent = DemographicsAgent(llm_manager)
        elif extraction_type == "genetics" or extraction_type == "all":
            agent = GeneticsAgent(llm_manager)
        elif extraction_type == "phenotypes" or extraction_type == "all":
            agent = PhenotypesAgent(llm_manager)
        elif extraction_type == "treatments" or extraction_type == "all":
            agent = TreatmentsAgent(llm_manager)
        else:
            raise HTTPException(status_code=400, detail="Invalid extraction type")
        
        # Create extraction task
        task = {
            "document_id": document_id,
            "content": document.get("content", ""),
            "extraction_type": extraction_type
        }
        
        # Execute extraction
        result = await agent.execute(task)
        
        if result.success:
            # Store extraction result
            await db_manager.store_extraction_result(
                document_id=document_id,
                extraction_type=extraction_type,
                result=result.data,
                confidence_score=result.confidence_score or 0.0
            )
            
            return {
                "success": True,
                "document_id": document_id,
                "extraction_type": extraction_type,
                "result": result.data,
                "confidence_score": result.confidence_score or 0.0
            }
        else:
            return {
                "success": False,
                "error": result.error,
                "document_id": document_id,
                "extraction_type": extraction_type
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@extraction_router.get("/results/{document_id}")
async def get_extraction_results(document_id: str) -> Dict[str, Any]:
    """Get extraction results for a document."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        results = await db_manager.get_extraction_results(document_id)
        
        return {
            "document_id": document_id,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error getting extraction results for {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Main Application
# ============================================================================

app = FastAPI(
    title="Biomedical Text Agent API",
    description="Real-time biomedical text processing and extraction API",
    version="1.0.0"
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

# Include routers
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(metadata_router, prefix="/api/metadata", tags=["metadata"])
app.include_router(database_router, prefix="/api/database", tags=["database"])
app.include_router(config_router, prefix="/api/config", tags=["config"])
app.include_router(extraction_router, prefix="/api/extraction", tags=["extraction"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    await initialize_services()

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Biomedical Text Agent API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": utc_now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        if not db_manager:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "error": "Database not initialized"}
            )
        
        # Check database health
        db_status = await db_manager.get_database_status()
        
        return {
            "status": "healthy" if db_status.get("status") == "healthy" else "degraded",
            "database": db_status.get("status"),
            "timestamp": utc_now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
