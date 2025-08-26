"""
Dashboard API Endpoints (lightweight)

Provides minimal endpoints for dashboard overview and basic metrics
without requiring auth or database dependencies, to ensure the UI
can run out-of-the-box.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview() -> Dict[str, Any]:
    """Return a minimal overview using latest pipeline summary if present."""
    data_dir = Path("data/metadata_triage")
    latest_summary = None
    files_indexed = 0

    try:
        if data_dir.exists():
            summaries = sorted(data_dir.rglob("pipeline_summary_*.json"))
            files_indexed = sum(1 for _ in data_dir.rglob("*.csv"))
            if summaries:
                with open(summaries[-1], "r") as f:
                    latest_summary = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to read pipeline summary: {e}")

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "files_indexed": files_indexed,
        "latest_summary": latest_summary or {},
        "status": "ok"
    }


@router.get("/statistics")
async def get_dashboard_statistics() -> Dict[str, Any]:
    """Return dashboard statistics with mock data for now."""
    return {
        "total_documents": 1250,
        "processed_today": 45,
        "success_rate": 94.2,
        "average_processing_time": 2.3,
        "active_agents": 5,
        "total_extractions": 5670,
        "validation_pending": 23,
        "errors_today": 3
    }


@router.get("/recent-activities")
async def get_recent_activities() -> List[Dict[str, Any]]:
    """Return recent system activities."""
    now = datetime.utcnow()
    activities = [
        {
            "id": 1,
            "type": "extraction",
            "description": "Processed PMID32679198.pdf",
            "timestamp": (now - timedelta(minutes=5)).isoformat() + "Z",
            "status": "completed",
            "user": "system"
        },
        {
            "id": 2,
            "type": "validation",
            "description": "Validated 15 phenotype extractions",
            "timestamp": (now - timedelta(minutes=15)).isoformat() + "Z",
            "status": "completed",
            "user": "researcher"
        },
        {
            "id": 3,
            "type": "upload",
            "description": "Uploaded new case report",
            "timestamp": (now - timedelta(minutes=30)).isoformat() + "Z",
            "status": "processing",
            "user": "clinician"
        },
        {
            "id": 4,
            "type": "analysis",
            "description": "Generated RAG response for gene query",
            "timestamp": (now - timedelta(hours=1)).isoformat() + "Z",
            "status": "completed",
            "user": "system"
        }
    ]
    return activities


@router.get("/alerts")
async def get_alerts() -> List[Dict[str, Any]]:
    """Return system alerts and notifications."""
    alerts = [
        {
            "id": 1,
            "type": "info",
            "title": "System Update",
            "message": "New ontology version available for HPO terms",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": "low"
        },
        {
            "id": 2,
            "type": "warning",
            "title": "High Memory Usage",
            "message": "System memory usage is at 85%",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": "medium"
        }
    ]
    return alerts


@router.get("/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """Return basic system metrics, falling back to mock values if psutil missing."""
    try:
        import psutil  # type: ignore
        cpu_usage = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {
            "cpu_usage": cpu_usage,
            "memory_usage": mem.percent,
            "disk_usage": round(disk.used / disk.total * 100, 2),
            "active_connections": 0,
            "api_requests_per_minute": 0,
        }
    except Exception:
        return {
            "cpu_usage": 25.0,
            "memory_usage": 45.0,
            "disk_usage": 60.0,
            "active_connections": 0,
            "api_requests_per_minute": 0,
        }


@router.get("/system-status")
async def get_system_status() -> Dict[str, Any]:
    """Return system status information."""
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "biomedical-text-agent-ui",
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

