"""
Validation API endpoints with UnifiedOrchestrator integration.

This module provides endpoints for the enhanced LangExtract validation interface.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import asyncio
import json

logger = logging.getLogger(__name__)

# Create the validation router
validation_router = APIRouter()

# Global orchestrator instance (will be set by the app factory)
orchestrator_instance = None

def set_orchestrator(orchestrator):
    """Set the orchestrator instance for the validation endpoints."""
    global orchestrator_instance
    orchestrator_instance = orchestrator

# ============================================================================
# VALIDATION ENDPOINTS
# ============================================================================

@validation_router.get("/queue")
async def get_validation_queue(
    status: Optional[str] = Query(None, description="Filter by status (pending, validated, rejected)"),
    limit: int = Query(100, description="Maximum number of items to return"),
    offset: int = Query(0, description="Number of items to skip")
) -> Dict[str, Any]:
    """
    Get the validation queue with pending and completed validations.
    
    Args:
        status: Optional filter for validation status
        limit: Maximum number of items to return
        offset: Number of items to skip
        
    Returns:
        Dictionary containing queue items and metadata
    """
    try:
        if not orchestrator_instance:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not initialized"
            )
        
        # Get validation queue from orchestrator
        queue_data = await orchestrator_instance.get_validation_queue(
            status=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "queue": queue_data.get("items", []),
            "total_count": queue_data.get("total_count", 0),
            "pending_count": queue_data.get("pending_count", 0),
            "validated_count": queue_data.get("validated_count", 0),
            "rejected_count": queue_data.get("rejected_count", 0),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to get validation queue: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get validation queue: {str(e)}"
        )

@validation_router.get("/{extraction_id}")
async def get_extraction_for_validation(extraction_id: str) -> Dict[str, Any]:
    """
    Get extraction data for validation, including highlighted text and confidence scores.
    
    Args:
        extraction_id: The ID of the extraction to retrieve
        
    Returns:
        Detailed extraction data for validation
    """
    try:
        if not orchestrator_instance:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not initialized"
            )
        
        # Get extraction data from SQLite
        extraction_data = await orchestrator_instance.sqlite_manager.get_extraction_with_validation(
            extraction_id
        )
        
        if not extraction_data:
            raise HTTPException(
                status_code=404,
                detail=f"Extraction {extraction_id} not found"
            )
        
        # Parse JSON fields
        extractions = json.loads(extraction_data.get("extractions", "{}"))
        spans = json.loads(extraction_data.get("spans", "[]"))
        confidence_scores = json.loads(extraction_data.get("confidence_scores", "{}"))
        
        return {
            "extraction_id": extraction_id,
            "document_id": extraction_data.get("document_id"),
            "original_text": extraction_data.get("original_text", ""),
            "highlighted_text": extraction_data.get("highlighted_text", ""),
            "extractions": extractions,
            "spans": spans,
            "confidence_scores": confidence_scores,
            "validation_status": extraction_data.get("validation_status", "pending"),
            "validator_notes": extraction_data.get("validator_notes"),
            "corrections": json.loads(extraction_data.get("corrections", "{}")),
            "created_at": extraction_data.get("created_at"),
            "validated_at": extraction_data.get("validated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get extraction {extraction_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get extraction data: {str(e)}"
        )

@validation_router.post("/{extraction_id}/submit")
async def submit_validation(
    extraction_id: str,
    validation_data: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """
    Submit validation results for an extraction.
    
    Args:
        extraction_id: The ID of the extraction to validate
        validation_data: Validation data including status, notes, and corrections
        
    Returns:
        Confirmation of validation submission
    """
    try:
        if not orchestrator_instance:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not initialized"
            )
        
        # Validate required fields
        status = validation_data.get("status")
        if status not in ["validated", "rejected", "needs_correction"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid status. Must be one of: validated, rejected, needs_correction"
            )
        
        # Submit validation through orchestrator
        result = await orchestrator_instance.submit_validation(
            extraction_id=extraction_id,
            status=status,
            validator_notes=validation_data.get("notes", ""),
            corrections=validation_data.get("corrections", {})
        )
        
        if result.get("error"):
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return {
            "extraction_id": extraction_id,
            "validation_status": status,
            "validator_notes": validation_data.get("notes", ""),
            "corrections": validation_data.get("corrections", {}),
            "submitted_at": datetime.utcnow().isoformat(),
            "message": "Validation submitted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit validation for {extraction_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit validation: {str(e)}"
        )

@validation_router.get("/stats/summary")
async def get_validation_statistics() -> Dict[str, Any]:
    """
    Get validation statistics summary.
    
    Returns:
        Summary statistics about validations
    """
    try:
        if not orchestrator_instance:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not initialized"
            )
        
        # Get validation statistics from database
        stats = await orchestrator_instance.sqlite_manager.get_validation_statistics()
        
        return {
            "total_extractions": stats.get("total_extractions", 0),
            "pending_validations": stats.get("pending_validations", 0),
            "completed_validations": stats.get("completed_validations", 0),
            "validated_count": stats.get("validated_count", 0),
            "rejected_count": stats.get("rejected_count", 0),
            "needs_correction_count": stats.get("needs_correction_count", 0),
            "average_confidence": stats.get("average_confidence", 0),
            "validation_rate": stats.get("validation_rate", 0),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get validation statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get validation statistics: {str(e)}"
        )

# ============================================================================
# EXTRACTION ENDPOINTS WITH ENHANCED FEATURES
# ============================================================================

@validation_router.get("/extraction/{document_id}/highlighted")
async def get_extraction_with_highlights(document_id: str) -> Dict[str, Any]:
    """
    Get extraction results with highlighted text for a document.
    
    Args:
        document_id: The document ID to get extractions for
        
    Returns:
        Extraction results with highlighted text
    """
    try:
        if not orchestrator_instance:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not initialized"
            )
        
        # Get all extractions for the document
        extractions = await orchestrator_instance.sqlite_manager.get_extractions_by_document(
            document_id
        )
        
        if not extractions:
            raise HTTPException(
                status_code=404,
                detail=f"No extractions found for document {document_id}"
            )
        
        # Format results with highlights
        results = []
        for extraction in extractions:
            extraction_data = json.loads(extraction.get("extractions", "{}"))
            spans = json.loads(extraction.get("spans", "[]"))
            
            results.append({
                "extraction_id": extraction.get("id"),
                "original_text": extraction.get("original_text", ""),
                "highlighted_text": extraction.get("highlighted_text", ""),
                "extractions": extraction_data,
                "spans": spans,
                "confidence_scores": json.loads(extraction.get("confidence_scores", "{}")),
                "validation_status": extraction.get("validation_status", "pending"),
                "created_at": extraction.get("created_at")
            })
        
        return {
            "document_id": document_id,
            "extractions": results,
            "total_count": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get extractions for document {document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get extraction data: {str(e)}"
        )

@validation_router.post("/extract-with-validation")
async def extract_document_with_validation(
    document_data: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """
    Extract information from a document using enhanced LangExtract with validation support.
    
    Args:
        document_data: Dictionary containing text and document metadata
        
    Returns:
        Enhanced extraction results with validation interface data
    """
    try:
        if not orchestrator_instance:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not initialized"
            )
        
        # Validate required fields
        text = document_data.get("text")
        document_id = document_data.get("document_id")
        
        if not text or not document_id:
            raise HTTPException(
                status_code=400,
                detail="Both 'text' and 'document_id' are required"
            )
        
        # Extract with enhanced features
        result = await orchestrator_instance.extract_document_with_validation(
            text=text,
            document_id=document_id,
            metadata_id=document_data.get("metadata_id"),
            fulltext_id=document_data.get("fulltext_id")
        )
        
        if result.get("error"):
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return {
            "document_id": document_id,
            "extraction_id": result.get("extraction_id"),
            "extractions": result.get("extractions", {}),
            "highlighted_text": result.get("highlighted_text", ""),
            "spans": result.get("spans", []),
            "confidence_scores": result.get("confidence_scores", {}),
            "validation_data": result.get("validation_data", {}),
            "message": "Extraction completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to extract document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract document: {str(e)}"
        )

# Export the router
__all__ = ["validation_router", "set_orchestrator"]
