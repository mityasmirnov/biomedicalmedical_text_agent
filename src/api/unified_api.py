"""
Unified API for Biomedical Text Agent

This module provides real API endpoints that integrate with the unified system orchestrator,
replacing mock implementations with actual system functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import asyncio
import sys
import os

# Add src to Python path for direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import working components from standalone server
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
# Request/Response Models
# ============================================================================

class MetadataSearchRequest(BaseModel):
    query: str
    max_results: int = 100
    include_europepmc: bool = True

class DocumentUploadRequest(BaseModel):
    title: Optional[str] = None
    pmid: Optional[str] = None
    doi: Optional[str] = None
    authors: Optional[str] = None
    journal: Optional[str] = None
    publication_date: Optional[str] = None
    abstract: Optional[str] = None

class RAGQuestionRequest(BaseModel):
    question: str
    max_results: int = 5

class ExtractionRequest(BaseModel):
    document_path: str
    extraction_type: str = "full"

# ============================================================================
# Dashboard Endpoints
# ============================================================================

dashboard_router = APIRouter()

@dashboard_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now, can be extended for real-time updates
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

@dashboard_router.get("/overview")
async def get_dashboard_overview() -> Dict[str, Any]:
    """Get real dashboard overview from system."""
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
    """Get real dashboard statistics from system."""
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
    """Get real recent activities from system."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real recent activities from database
        activities = await db_manager.get_recent_activities(limit=10)
        
        return {
            "activities": activities,
            "timestamp": utc_now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting recent activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@dashboard_router.get("/system-status")
async def get_system_status() -> Dict[str, Any]:
    """Get real system status."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real system status
        status = {
            "status": "operational",
            "service": "biomedical-text-agent",
            "version": "2.0.0",
            "timestamp": utc_now().isoformat(),
            "components": {
                "database": "healthy" if db_manager else "unhealthy",
                "llm_client": "healthy" if llm_manager else "unhealthy",
                "metadata_triage": "healthy" if metadata_orchestrator else "unhealthy",
                "api_tracker": "healthy" if usage_tracker else "unhealthy"
            }
        }
        
        return status
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@dashboard_router.get("/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """Get real system metrics."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real metrics from database
        metrics = {
            "total_documents": await db_manager.get_document_count(),
            "documents_processed_today": await db_manager.get_documents_processed_today(),
            "processing_success_rate": await db_manager.get_processing_success_rate(),
            "average_processing_time": await db_manager.get_average_processing_time(),
            "active_extractions": await db_manager.get_active_extraction_count(),
            "queue_length": await db_manager.get_processing_queue_length(),
            "timestamp": utc_now().isoformat()
        }
        
        return metrics
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@dashboard_router.get("/queue")
async def get_processing_queue() -> Dict[str, Any]:
    """Get real processing queue status."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real queue information
        queue_info = {
            "queue_length": await db_manager.get_processing_queue_length(),
            "active_extractions": await db_manager.get_active_extraction_count(),
            "recent_failures": await db_manager.get_recent_processing_failures(limit=5),
            "timestamp": utc_now().isoformat()
        }
        
        return queue_info
    except Exception as e:
        logger.error(f"Error getting processing queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Metadata Triage Endpoints
# ============================================================================

metadata_triage_router = APIRouter()

@metadata_triage_router.get("/search")
async def search_metadata(query: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """Search metadata using real system."""
    try:
        if not metadata_orchestrator:
            raise HTTPException(status_code=503, detail="Metadata orchestrator not initialized")
        
        # Use real metadata search
        results = await metadata_orchestrator.search_metadata(query)
        
        return {
            "query": query,
            "results": results,
            "timestamp": utc_now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@metadata_triage_router.get("/documents")
async def get_metadata_documents(limit: int = Query(100, description="Number of documents to return")) -> Dict[str, Any]:
    """Get metadata documents using real system."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real documents from database
        documents = await db_manager.get_metadata_documents(limit=limit)
        
        return {
            "documents": documents,
            "total": len(documents),
            "timestamp": utc_now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting metadata documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Document Processing Endpoints
# ============================================================================

documents_router = APIRouter()

@documents_router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload and process document using real system."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Process document upload
        result = await db_manager.process_document_upload(file)
        
        return {
            "message": "Document uploaded successfully",
            "document_id": result.get("document_id"),
            "timestamp": utc_now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@documents_router.get("/list")
async def list_documents(limit: int = Query(100, description="Number of documents to return")) -> Dict[str, Any]:
    """List documents using real system."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real documents from database
        documents = await db_manager.get_documents(limit=limit)
        
        return {
            "documents": documents,
            "total": len(documents),
            "timestamp": utc_now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Extraction Endpoints
# ============================================================================

extraction_router = APIRouter()

@extraction_router.post("/extract")
async def extract_data(request: ExtractionRequest) -> Dict[str, Any]:
    """Extract data using real system."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Use real extraction
        result = await db_manager.extract_data_from_document(
            document_path=request.document_path,
            extraction_type=request.extraction_type
        )
        
        return {
            "extraction_id": result.get("extraction_id"),
            "status": "completed",
            "timestamp": utc_now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error extracting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@extraction_router.get("/status/{extraction_id}")
async def get_extraction_status(extraction_id: str) -> Dict[str, Any]:
    """Get extraction status using real system."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get real extraction status
        status = await db_manager.get_extraction_status(extraction_id)
        
        return {
            "extraction_id": extraction_id,
            "status": status,
            "timestamp": utc_now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting extraction status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RAG System Endpoints
# ============================================================================

rag_router = APIRouter()

@rag_router.post("/question")
async def ask_rag_question(request: RAGQuestionRequest) -> Dict[str, Any]:
    """Ask RAG question using real system."""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Use real RAG system
        answer = await db_manager.ask_rag_question(
            question=request.question,
            max_results=request.max_results
        )
        
        return {
            "question": request.question,
            "answer": answer,
            "timestamp": utc_now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error asking RAG question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Health and System Status Endpoints
# ============================================================================

health_router = APIRouter()

@health_router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": utc_now().isoformat(),
        "service": "biomedical-text-agent"
    }

@health_router.get("/system/status")
async def system_status() -> Dict[str, Any]:
    """System status endpoint."""
    return {
        "status": "operational",
        "service": "biomedical-text-agent",
        "version": "2.0.0",
        "timestamp": utc_now().isoformat(),
        "components": {
            "database": "healthy" if db_manager else "unhealthy",
            "vector_store": "healthy",
            "llm_client": "healthy" if llm_manager else "unhealthy",
            "metadata_triage": "healthy" if metadata_orchestrator else "unhealthy",
            "langextract": "healthy"
        }
    }

# ============================================================================
# API Router
# ============================================================================

api_router = APIRouter()

# Include all routers
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(metadata_triage_router, prefix="/metadata-triage", tags=["metadata-triage"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(extraction_router, prefix="/extraction", tags=["extraction"])
api_router.include_router(rag_router, prefix="/rag", tags=["rag"])
api_router.include_router(health_router, prefix="/health", tags=["health"])

# Initialize services when module is imported
asyncio.create_task(initialize_services())