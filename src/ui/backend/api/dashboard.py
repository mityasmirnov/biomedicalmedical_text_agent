"""
Dashboard API Endpoints

Provides API endpoints for the main dashboard interface including
system overview, statistics, and real-time monitoring data.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.models import DashboardStats, SystemStatus, RecentActivity
from src.database import DatabaseManager
from src.ui.backend.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


class DashboardOverview(BaseModel):
    """Dashboard overview response model."""
    system_status: SystemStatus
    statistics: DashboardStats
    recent_activities: List[RecentActivity]
    alerts: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]


class SystemMetrics(BaseModel):
    """System performance metrics."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    api_requests_per_minute: int
    extraction_queue_size: int


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    request: Request,
    user=Depends(get_current_user)
) -> DashboardOverview:
    """
    Get comprehensive dashboard overview.
    
    Returns:
        Dashboard overview with system status, stats, and activities
    """
    try:
        db_manager: DatabaseManager = request.app.state.db_manager
        
        # Get system status
        system_status = await _get_system_status(db_manager)
        
        # Get statistics
        statistics = await _get_dashboard_statistics(db_manager)
        
        # Get recent activities
        recent_activities = await _get_recent_activities(db_manager, limit=10)
        
        # Get alerts
        alerts = await _get_system_alerts(db_manager)
        
        # Get performance metrics
        performance_metrics = await _get_performance_metrics(request)
        
        return DashboardOverview(
            system_status=system_status,
            statistics=statistics,
            recent_activities=recent_activities,
            alerts=alerts,
            performance_metrics=performance_metrics
        )
        
    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")


@router.get("/statistics", response_model=DashboardStats)
async def get_dashboard_statistics(
    request: Request,
    days: int = 30,
    user=Depends(get_current_user)
) -> DashboardStats:
    """
    Get dashboard statistics for specified time period.
    
    Args:
        days: Number of days to include in statistics
        
    Returns:
        Dashboard statistics
    """
    try:
        db_manager: DatabaseManager = request.app.state.db_manager
        return await _get_dashboard_statistics(db_manager, days)
        
    except Exception as e:
        logger.error(f"Failed to get dashboard statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to load statistics")


@router.get("/system-status", response_model=SystemStatus)
async def get_system_status(
    request: Request,
    user=Depends(get_current_user)
) -> SystemStatus:
    """
    Get current system status.
    
    Returns:
        Current system status
    """
    try:
        db_manager: DatabaseManager = request.app.state.db_manager
        return await _get_system_status(db_manager)
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to load system status")


@router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics(
    request: Request,
    user=Depends(get_current_user)
) -> SystemMetrics:
    """
    Get real-time system performance metrics.
    
    Returns:
        System performance metrics
    """
    try:
        # Get WebSocket manager for active connections
        websocket_manager = request.app.state.websocket_manager
        
        # Get performance metrics
        metrics = await _get_performance_metrics(request)
        
        return SystemMetrics(
            cpu_usage=metrics.get('cpu_usage', 0.0),
            memory_usage=metrics.get('memory_usage', 0.0),
            disk_usage=metrics.get('disk_usage', 0.0),
            active_connections=len(websocket_manager.active_connections),
            api_requests_per_minute=metrics.get('api_requests_per_minute', 0),
            extraction_queue_size=metrics.get('extraction_queue_size', 0)
        )
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to load metrics")


@router.get("/recent-activities")
async def get_recent_activities(
    request: Request,
    limit: int = 20,
    activity_type: Optional[str] = None,
    user=Depends(get_current_user)
) -> List[RecentActivity]:
    """
    Get recent system activities.
    
    Args:
        limit: Maximum number of activities to return
        activity_type: Filter by activity type
        
    Returns:
        List of recent activities
    """
    try:
        db_manager: DatabaseManager = request.app.state.db_manager
        return await _get_recent_activities(db_manager, limit, activity_type)
        
    except Exception as e:
        logger.error(f"Failed to get recent activities: {e}")
        raise HTTPException(status_code=500, detail="Failed to load activities")


@router.get("/alerts")
async def get_system_alerts(
    request: Request,
    severity: Optional[str] = None,
    user=Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get system alerts and notifications.
    
    Args:
        severity: Filter by alert severity (info, warning, error, critical)
        
    Returns:
        List of system alerts
    """
    try:
        db_manager: DatabaseManager = request.app.state.db_manager
        return await _get_system_alerts(db_manager, severity)
        
    except Exception as e:
        logger.error(f"Failed to get system alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to load alerts")


@router.post("/alerts/{alert_id}/dismiss")
async def dismiss_alert(
    alert_id: str,
    request: Request,
    user=Depends(get_current_user)
) -> Dict[str, str]:
    """
    Dismiss a system alert.
    
    Args:
        alert_id: ID of the alert to dismiss
        
    Returns:
        Success message
    """
    try:
        db_manager: DatabaseManager = request.app.state.db_manager
        
        # Update alert status
        await db_manager.execute_query(
            "UPDATE system_alerts SET status = 'dismissed', dismissed_at = ?, dismissed_by = ? WHERE id = ?",
            (datetime.utcnow(), user.get('id') if user else 'unknown', alert_id)
        )
        
        return {"message": "Alert dismissed successfully"}
        
    except Exception as e:
        logger.error(f"Failed to dismiss alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to dismiss alert")


# Helper functions

async def _get_system_status(db_manager: DatabaseManager) -> SystemStatus:
    """Get current system status."""
    try:
        # Check database connectivity
        db_healthy = await db_manager.health_check()
        
        # Check extraction services
        extraction_healthy = True  # TODO: Implement service health checks
        
        # Check API services
        api_healthy = True  # TODO: Implement API health checks
        
        # Determine overall status
        if db_healthy and extraction_healthy and api_healthy:
            status = "healthy"
        elif db_healthy:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return SystemStatus(
            status=status,
            database_status="healthy" if db_healthy else "unhealthy",
            extraction_service_status="healthy" if extraction_healthy else "unhealthy",
            api_service_status="healthy" if api_healthy else "unhealthy",
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return SystemStatus(
            status="unhealthy",
            database_status="unknown",
            extraction_service_status="unknown",
            api_service_status="unknown",
            last_updated=datetime.utcnow()
        )


async def _get_dashboard_statistics(db_manager: DatabaseManager, days: int = 30) -> DashboardStats:
    """Get dashboard statistics."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get document statistics
        total_documents = await db_manager.fetch_scalar(
            "SELECT COUNT(*) FROM documents"
        ) or 0
        
        processed_documents = await db_manager.fetch_scalar(
            "SELECT COUNT(*) FROM documents WHERE status = 'processed'"
        ) or 0
        
        documents_this_period = await db_manager.fetch_scalar(
            "SELECT COUNT(*) FROM documents WHERE created_at >= ?",
            (start_date,)
        ) or 0
        
        # Get extraction statistics
        total_extractions = await db_manager.fetch_scalar(
            "SELECT COUNT(*) FROM extractions"
        ) or 0
        
        successful_extractions = await db_manager.fetch_scalar(
            "SELECT COUNT(*) FROM extractions WHERE status = 'completed'"
        ) or 0
        
        extractions_this_period = await db_manager.fetch_scalar(
            "SELECT COUNT(*) FROM extractions WHERE created_at >= ?",
            (start_date,)
        ) or 0
        
        # Get validation statistics
        validated_extractions = await db_manager.fetch_scalar(
            "SELECT COUNT(*) FROM extractions WHERE validation_status = 'validated'"
        ) or 0
        
        # Get agent performance
        avg_extraction_time = await db_manager.fetch_scalar(
            "SELECT AVG(processing_time_seconds) FROM extractions WHERE status = 'completed'"
        ) or 0.0
        
        # Get error statistics
        failed_extractions = await db_manager.fetch_scalar(
            "SELECT COUNT(*) FROM extractions WHERE status = 'failed'"
        ) or 0
        
        return DashboardStats(
            total_documents=total_documents,
            processed_documents=processed_documents,
            documents_this_period=documents_this_period,
            total_extractions=total_extractions,
            successful_extractions=successful_extractions,
            extractions_this_period=extractions_this_period,
            validated_extractions=validated_extractions,
            failed_extractions=failed_extractions,
            average_extraction_time=avg_extraction_time,
            success_rate=(successful_extractions / total_extractions * 100) if total_extractions > 0 else 0.0
        )
        
    except Exception as e:
        logger.error(f"Failed to get dashboard statistics: {e}")
        # Return empty statistics on error
        return DashboardStats(
            total_documents=0,
            processed_documents=0,
            documents_this_period=0,
            total_extractions=0,
            successful_extractions=0,
            extractions_this_period=0,
            validated_extractions=0,
            failed_extractions=0,
            average_extraction_time=0.0,
            success_rate=0.0
        )


async def _get_recent_activities(
    db_manager: DatabaseManager, 
    limit: int = 20, 
    activity_type: Optional[str] = None
) -> List[RecentActivity]:
    """Get recent system activities."""
    try:
        query = """
            SELECT id, activity_type, description, user_id, created_at, metadata
            FROM system_activities 
            WHERE 1=1
        """
        params = []
        
        if activity_type:
            query += " AND activity_type = ?"
            params.append(activity_type)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        rows = await db_manager.fetch_all(query, params)
        
        activities = []
        for row in rows:
            activities.append(RecentActivity(
                id=row['id'],
                activity_type=row['activity_type'],
                description=row['description'],
                user_id=row['user_id'],
                timestamp=row['created_at'],
                metadata=row['metadata'] or {}
            ))
        
        return activities
        
    except Exception as e:
        logger.error(f"Failed to get recent activities: {e}")
        return []


async def _get_system_alerts(
    db_manager: DatabaseManager, 
    severity: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get system alerts."""
    try:
        query = """
            SELECT id, alert_type, severity, title, message, created_at, status
            FROM system_alerts 
            WHERE status != 'dismissed'
        """
        params = []
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        query += " ORDER BY created_at DESC LIMIT 50"
        
        rows = await db_manager.fetch_all(query, params)
        
        alerts = []
        for row in rows:
            alerts.append({
                'id': row['id'],
                'type': row['alert_type'],
                'severity': row['severity'],
                'title': row['title'],
                'message': row['message'],
                'timestamp': row['created_at'],
                'status': row['status']
            })
        
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to get system alerts: {e}")
        return []


async def _get_performance_metrics(request: Request) -> Dict[str, Any]:
    """Get system performance metrics."""
    try:
        import psutil
        
        # CPU and memory usage
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get database manager for queue size
        db_manager: DatabaseManager = request.app.state.db_manager
        
        # Get extraction queue size
        queue_size = await db_manager.fetch_scalar(
            "SELECT COUNT(*) FROM extractions WHERE status = 'pending'"
        ) or 0
        
        # Get API request rate (simplified - in production, use proper metrics)
        api_requests = await db_manager.fetch_scalar(
            "SELECT COUNT(*) FROM api_requests WHERE created_at >= ?",
            (datetime.utcnow() - timedelta(minutes=1),)
        ) or 0
        
        return {
            'cpu_usage': cpu_usage,
            'memory_usage': memory.percent,
            'disk_usage': (disk.used / disk.total) * 100,
            'extraction_queue_size': queue_size,
            'api_requests_per_minute': api_requests
        }
        
    except ImportError:
        # psutil not available, return mock data
        return {
            'cpu_usage': 25.0,
            'memory_usage': 45.0,
            'disk_usage': 60.0,
            'extraction_queue_size': 0,
            'api_requests_per_minute': 10
        }
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        return {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0,
            'extraction_queue_size': 0,
            'api_requests_per_minute': 0
        }

