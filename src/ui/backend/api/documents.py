"""
Documents API Endpoints

Connects to your real document storage and metadata triage system.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys

from fastapi import APIRouter, HTTPException

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def get_documents() -> List[Dict[str, Any]]:
    """Get documents from your data directory and metadata triage system."""
    documents = []
    
    try:
        # Scan your data directory for documents
        data_dir = Path("data")
        input_dir = data_dir / "input"
        metadata_dir = data_dir / "metadata_triage"
        
        # Get PDFs from input directory
        if input_dir.exists():
            for pdf_file in input_dir.rglob("*.pdf"):
                metadata = get_document_metadata(pdf_file.name, metadata_dir)
                documents.append(create_document_record(pdf_file, metadata))
        
        # Get documents from metadata triage system
        if metadata_dir.exists():
            for subdir in metadata_dir.iterdir():
                if subdir.is_dir():
                    metadata_files = list(subdir.rglob("*.csv"))
                    if metadata_files:
                        # Get the latest metadata file
                        latest_metadata = max(metadata_files, key=lambda f: f.stat().st_mtime)
                        metadata_docs = parse_metadata_csv(latest_metadata)
                        documents.extend(metadata_docs)
        
        return documents
        
    except Exception as e:
        logger.error(f"Failed to get documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}")
async def get_document(document_id: str) -> Dict[str, Any]:
    """Get specific document details."""
    documents = await get_documents()
    for doc in documents:
        if doc["id"] == document_id:
            return doc
    
    raise HTTPException(status_code=404, detail="Document not found")

@router.get("/{document_id}/full-text")
async def get_document_full_text(document_id: str) -> Dict[str, Any]:
    """Get full text content of a document."""
    # This would integrate with your PDF parser
    try:
        # For now, return metadata
        doc = await get_document(document_id)
        return {
            "id": document_id,
            "content_available": True,
            "content_type": "pdf",
            "file_path": doc.get("source_path"),
            "metadata": doc
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_document_metadata(filename: str, metadata_dir: Path) -> Dict[str, Any]:
    """Get metadata from your existing triage system."""
    metadata = {}
    
    try:
        # Look for metadata files
        for subdir in metadata_dir.iterdir():
            if subdir.is_dir():
                metadata_file = subdir / f"{filename}.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    break
    except Exception as e:
        logger.warning(f"Failed to read metadata for {filename}: {e}")
    
    return metadata

def create_document_record(file_path: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Create a document record from file and metadata."""
    stat = file_path.stat()
    
    return {
        "id": file_path.stem,
        "name": file_path.name,
        "type": "pdf",
        "size": f"{stat.st_size / (1024*1024):.1f} MB",
        "status": metadata.get("status", "pending"),
        "uploaded": metadata.get("upload_date", datetime.fromtimestamp(stat.st_mtime).isoformat()),
        "processed": metadata.get("processed_date"),
        "patient_count": metadata.get("patient_count", 0),
        "extraction_score": metadata.get("extraction_score"),
        "category": metadata.get("category", "Unknown"),
        "source": metadata.get("source", "Local Upload"),
        "pmid": metadata.get("pmid"),
        "doi": metadata.get("doi"),
        "abstract": metadata.get("abstract"),
        "concept_score": metadata.get("concept_score"),
        "classification": metadata.get("classification"),
        "source_path": str(file_path),
        "metadata_path": str(file_path.parent / "metadata_triage" / file_path.stem) if metadata else None
    }

def parse_metadata_csv(csv_file: Path) -> List[Dict[str, Any]]:
    """Parse metadata CSV files from your triage system."""
    documents = []
    
    try:
        import pandas as pd
        df = pd.read_csv(csv_file)
        
        for _, row in df.iterrows():
            doc = {
                "id": str(row.get("PMID", f"doc_{len(documents)}")),
                "name": f"PMID{row.get('PMID', 'Unknown')}.pdf",
                "type": "pdf",
                "size": "Unknown",
                "status": "completed",
                "uploaded": row.get("PubDate", "Unknown"),
                "processed": "Unknown",
                "patient_count": row.get("PatientCount", 0),
                "extraction_score": row.get("ClassificationConfidence", 0) * 100,
                "category": row.get("StudyType", "Unknown"),
                "source": row.get("Source", "PubMed"),
                "pmid": row.get("PMID"),
                "doi": row.get("DOI"),
                "abstract": row.get("Abstract", ""),
                "concept_score": row.get("ConceptDensity", 0),
                "classification": row.get("StudyType", "Unknown"),
                "title": row.get("Title", ""),
                "authors": row.get("Authors", ""),
                "journal": row.get("Journal", ""),
                "source_path": f"data/metadata_triage/{csv_file.parent.name}/pubmed/",
                "metadata_path": str(csv_file)
            }
            documents.append(doc)
            
    except Exception as e:
        logger.warning(f"Failed to parse metadata CSV {csv_file}: {e}")
    
    return documents
