"""
Metadata Browser API Endpoints

Provides access to your rich metadata triage system data.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def get_metadata_overview() -> Dict[str, Any]:
    """Get overview of all metadata collections."""
    try:
        data_dir = Path("data/metadata_triage")
        collections = []
        
        if data_dir.exists():
            for subdir in data_dir.iterdir():
                if subdir.is_dir():
                    collection_info = get_collection_info(subdir)
                    collections.append(collection_info)
        
        return {
            "total_collections": len(collections),
            "collections": collections,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get metadata overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections/{collection_name}")
async def get_collection_metadata(collection_name: str) -> Dict[str, Any]:
    """Get metadata for a specific collection."""
    try:
        collection_dir = Path(f"data/metadata_triage/{collection_name}")
        if not collection_dir.exists():
            raise HTTPException(status_code=404, detail="Collection not found")
        
        return get_collection_info(collection_dir, detailed=True)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get collection metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections/{collection_name}/documents")
async def get_collection_documents(
    collection_name: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
    """Get documents from a specific collection."""
    try:
        collection_dir = Path(f"data/metadata_triage/{collection_name}")
        if not collection_dir.exists():
            raise HTTPException(status_code=404, detail="Collection not found")
        
        documents = parse_collection_documents(collection_dir)
        
        # Pagination
        total = len(documents)
        paginated_docs = documents[offset:offset + limit]
        
        return {
            "collection": collection_name,
            "documents": paginated_docs,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get collection documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_metadata(
    query: str = Query(..., description="Search query"),
    collection: Optional[str] = Query(None, description="Limit to specific collection"),
    limit: int = Query(100, ge=1, le=1000)
) -> Dict[str, Any]:
    """Search across all metadata."""
    try:
        results = []
        data_dir = Path("data/metadata_triage")
        
        if collection:
            collections = [data_dir / collection]
        else:
            collections = [subdir for subdir in data_dir.iterdir() if subdir.is_dir()]
        
        for collection_dir in collections:
            if collection_dir.exists():
                collection_results = search_collection(collection_dir, query, limit)
                results.extend(collection_results)
        
        # Sort by relevance and limit results
        results = sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=True)[:limit]
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Failed to search metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_collection_info(collection_dir: Path, detailed: bool = False) -> Dict[str, Any]:
    """Get information about a metadata collection."""
    collection_name = collection_dir.name
    
    # Find the latest pipeline summary
    summary_files = list(collection_dir.glob("pipeline_summary_*.json"))
    latest_summary = None
    if summary_files:
        latest_summary_file = max(summary_files, key=lambda f: f.stat().st_mtime)
        try:
            with open(latest_summary_file, 'r') as f:
                latest_summary = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read summary for {collection_name}: {e}")
    
    # Count documents
    csv_files = list(collection_dir.glob("*.csv"))
    document_count = 0
    if csv_files:
        try:
            import pandas as pd
            for csv_file in csv_files:
                df = pd.read_csv(csv_file)
                document_count += len(df)
        except Exception as e:
            logger.warning(f"Failed to count documents in {collection_name}: {e}")
    
    info = {
        "name": collection_name,
        "document_count": document_count,
        "last_updated": latest_summary.get("timestamp") if latest_summary else "Unknown",
        "pipeline_status": latest_summary.get("status", "Unknown") if latest_summary else "Unknown"
    }
    
    if detailed:
        info.update({
            "summary": latest_summary,
            "files": [f.name for f in collection_dir.iterdir() if f.is_file()],
            "subdirectories": [d.name for d in collection_dir.iterdir() if d.is_dir()]
        })
    
    return info

def parse_collection_documents(collection_dir: Path) -> List[Dict[str, Any]]:
    """Parse documents from a collection directory."""
    documents = []
    
    try:
        # Look for CSV files with metadata
        csv_files = list(collection_dir.glob("*.csv"))
        if csv_files:
            latest_csv = max(csv_files, key=lambda f: f.stat().st_mtime)
            
            import pandas as pd
            df = pd.read_csv(latest_csv)
            
            for _, row in df.iterrows():
                doc = {
                    "pmid": row.get("PMID"),
                    "title": row.get("Title", ""),
                    "abstract": row.get("Abstract", ""),
                    "authors": row.get("Authors", ""),
                    "journal": row.get("Journal", ""),
                    "pub_date": row.get("PubDate", ""),
                    "source": row.get("Source", ""),
                    "doi": row.get("DOI"),
                    "pmc_link": row.get("PMCLink"),
                    "study_type": row.get("StudyType", ""),
                    "is_case_report": row.get("IsCaseReport", False),
                    "clinical_relevance": row.get("ClinicalRelevance", ""),
                    "patient_count": row.get("PatientCount", 0),
                    "classification_confidence": row.get("ClassificationConfidence", 0),
                    "concept_density": row.get("ConceptDensity", 0),
                    "concept_priority_score": row.get("ConceptPriorityScore", 0),
                    "combined_priority_score": row.get("CombinedPriorityScore", 0),
                    "has_abstract": row.get("HasAbstract", False),
                    "abstract_length": row.get("AbstractLength", 0),
                    "top_semantic_types": row.get("TopSemanticTypes", ""),
                    "rank": row.get("Rank", 0)
                }
                documents.append(doc)
                
    except Exception as e:
        logger.warning(f"Failed to parse collection documents: {e}")
    
    return documents

def search_collection(collection_dir: Path, query: str, limit: int) -> List[Dict[str, Any]]:
    """Search within a specific collection."""
    results = []
    
    try:
        documents = parse_collection_documents(collection_dir)
        
        for doc in documents:
            relevance_score = 0
            
            # Simple text search
            query_lower = query.lower()
            if query_lower in doc.get("title", "").lower():
                relevance_score += 10
            if query_lower in doc.get("abstract", "").lower():
                relevance_score += 5
            if query_lower in doc.get("authors", "").lower():
                relevance_score += 3
            if query_lower in doc.get("journal", "").lower():
                relevance_score += 2
            
            if relevance_score > 0:
                doc["relevance_score"] = relevance_score
                doc["collection"] = collection_dir.name
                results.append(doc)
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
    except Exception as e:
        logger.warning(f"Failed to search collection {collection_dir.name}: {e}")
    
    return results
