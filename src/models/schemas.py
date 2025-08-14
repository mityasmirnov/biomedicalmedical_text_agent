from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class SystemStatus(BaseModel):
    status: str = "online"
    uptime: float = 0.0
    last_checked: datetime

class DashboardStats(BaseModel):
    total_documents: int
    extractions_last_24h: int
    validations_pending: int
    accuracy_avg: float

class RecentActivity(BaseModel):
    id: int
    timestamp: datetime
    activity_type: str
    details: Dict[str, Any]
    user: Optional[str] = None
