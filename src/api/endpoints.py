"""
API endpoints for Biomedical Text Agent.

This module defines all the API endpoints that connect to the core system components.
Each router handles a specific domain of functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

# Import core system components
from metadata_triage.metadata_orchestrator import MetadataOrchestrator
from langextract_integration.extractor import LangExtractEngine
from database.sqlite_manager import SQLiteManager
from database.vector_manager import VectorManager
from rag.rag_system import RAGSystem
from core.llm_client.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

# ============================================================================
# Metadata Triage Endpoints
# ============================================================================

metadata_triage_router = APIRouter()

class MetadataQuery(BaseModel):
    query: str
    max_results: int = 100
    include_europepmc: bool = True
    save_intermediate: bool = True

@metadata_triage_router.post("/search")
async def search_metadata(query: MetadataQuery):
    """Search and retrieve metadata from PubMed and Europe PMC."""
    try:
        # Initialize components
        llm_client = OpenRouterClient()
        orchestrator = MetadataOrchestrator(llm_client=llm_client)
        
        # Run metadata triage pipeline
        result = await orchestrator.run_complete_pipeline(
            query=query.query,
            max_results=query.max_results,
            include_europepmc=query.include_europepmc,
            save_intermediate=query.save_intermediate
        )
        
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        logger.error(f"Metadata search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Extraction Endpoints
# ============================================================================

extraction_router = APIRouter()

class ExtractionRequest(BaseModel):
    text: str
    extraction_passes: int = 2
    use_patient_segmentation: bool = True

@extraction_router.post("/extract")
async def extract_from_text(request: ExtractionRequest):
    """Extract biomedical information from text using LangExtract."""
    try:
        # Initialize LangExtract engine
        engine = LangExtractEngine()
        
        # Run extraction
        result = engine.extract_from_text(
            text=request.text,
            extraction_passes=request.extraction_passes,
            use_patient_segmentation=request.use_patient_segmentation
        )
        
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@extraction_router.post("/upload")
async def extract_from_file(file: UploadFile = File(...)):
    """Extract biomedical information from uploaded file."""
    try:
        # Read file content
        content = await file.read()
        text = content.decode('utf-8')
        
        # Initialize LangExtract engine
        engine = LangExtractEngine()
        
        # Run extraction
        result = engine.extract_from_text(text=text)
        
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        logger.error(f"File extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Database Endpoints
# ============================================================================

database_router = APIRouter()

@database_router.get("/status")
async def get_database_status():
    """Get database status and statistics."""
    try:
        sqlite_manager = SQLiteManager()
        vector_manager = VectorManager()
        
        # Get database statistics
        sqlite_stats = sqlite_manager.get_database_stats()
        vector_stats = vector_manager.get_database_stats()
        
        return JSONResponse(content={
            "sqlite": sqlite_stats,
            "vector": vector_stats,
            "status": "healthy"
        }, status_code=200)
    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@database_router.get("/patients")
async def get_patients(limit: int = 100, offset: int = 0):
    """Get patient records from database."""
    try:
        sqlite_manager = SQLiteManager()
        patients = sqlite_manager.get_patient_records(limit=limit, offset=offset)
        
        return JSONResponse(content=patients, status_code=200)
    except Exception as e:
        logger.error(f"Failed to retrieve patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RAG System Endpoints
# ============================================================================

rag_router = APIRouter()

class RAGQuestion(BaseModel):
    question: str
    max_results: int = 5

@rag_router.post("/ask")
async def ask_question(request: RAGQuestion):
    """Ask a question using the RAG system."""
    try:
        # Initialize RAG system
        sqlite_manager = SQLiteManager()
        vector_manager = VectorManager()
        rag_system = RAGSystem(
            vector_manager=vector_manager,
            sqlite_manager=sqlite_manager
        )
        
        # Get answer
        answer = await rag_system.ask_question(
            question=request.question,
            max_results=request.max_results
        )
        
        return JSONResponse(content=answer, status_code=200)
    except Exception as e:
        logger.error(f"RAG question failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# User Management Endpoints
# ============================================================================

user_router = APIRouter()

@user_router.get("/profile")
async def get_user_profile():
    """Get current user profile."""
    # For now, return a default profile
    # TODO: Implement proper user authentication
    return JSONResponse(content={
        "user_id": "default",
        "username": "admin",
        "role": "administrator",
        "permissions": ["read", "write", "admin"]
    }, status_code=200)