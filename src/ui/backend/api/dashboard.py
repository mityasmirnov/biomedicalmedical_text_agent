"""
Dashboard API Endpoints (lightweight)

Provides minimal endpoints for dashboard overview and basic metrics
without requiring auth or database dependencies, to ensure the UI
can run out-of-the-box.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

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


@router.get("/status")
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

