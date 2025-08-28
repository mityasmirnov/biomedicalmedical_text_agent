"""
API Usage Tracker for monitoring and limiting API requests.
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging
from dataclasses import dataclass, asdict

log = logging.getLogger(__name__)

@dataclass
class APIUsageRecord:
    """Record of a single API request."""
    timestamp: float
    api_provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    success: bool
    error_message: Optional[str] = None
    request_id: Optional[str] = None

@dataclass
class UsageStats:
    """Usage statistics for a time period."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens: int
    total_cost: float
    average_response_time: float

class APIUsageTracker:
    """Tracks API usage and enforces limits."""
    
    def __init__(self, database_path: str = "./data/api_usage.db"):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Create usage records table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        api_provider TEXT NOT NULL,
                        model TEXT NOT NULL,
                        prompt_tokens INTEGER DEFAULT 0,
                        completion_tokens INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        cost REAL DEFAULT 0.0,
                        success BOOLEAN NOT NULL,
                        error_message TEXT,
                        request_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create usage limits table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usage_limits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        limit_type TEXT NOT NULL UNIQUE,
                        limit_value INTEGER NOT NULL,
                        reset_period TEXT NOT NULL,
                        last_reset REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create usage summaries table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usage_summaries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        period_start REAL NOT NULL,
                        period_end REAL NOT NULL,
                        period_type TEXT NOT NULL,
                        api_provider TEXT NOT NULL,
                        total_requests INTEGER DEFAULT 0,
                        successful_requests INTEGER DEFAULT 0,
                        failed_requests INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        total_cost REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_usage_provider ON api_usage(api_provider)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_usage_success ON api_usage(success)")
                
                conn.commit()
                log.info(f"API usage database initialized at {self.database_path}")
                
        except Exception as e:
            log.error(f"Failed to initialize API usage database: {e}")
            raise
    
    def record_request(self, record: APIUsageRecord) -> bool:
        """Record an API request in the database."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO api_usage (
                        timestamp, api_provider, model, prompt_tokens, 
                        completion_tokens, total_tokens, cost, success, 
                        error_message, request_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.timestamp, record.api_provider, record.model,
                    record.prompt_tokens, record.completion_tokens, 
                    record.total_tokens, record.cost, record.success,
                    record.error_message, record.request_id
                ))
                
                conn.commit()
                log.debug(f"Recorded API request: {record.api_provider} - {record.model}")
                return True
                
        except Exception as e:
            log.error(f"Failed to record API request: {e}")
            return False
    
    def check_daily_limit(self, api_provider: str, limit: int) -> Tuple[bool, int, int]:
        """
        Check if daily limit has been reached.
        
        Returns:
            Tuple of (can_proceed, current_usage, remaining_requests)
        """
        try:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
            
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM api_usage 
                    WHERE api_provider = ? AND timestamp >= ?
                """, (api_provider, today_start))
                
                current_usage = cursor.fetchone()[0]
                remaining = max(0, limit - current_usage)
                can_proceed = current_usage < limit
                
                return can_proceed, current_usage, remaining
                
        except Exception as e:
            log.error(f"Failed to check daily limit: {e}")
            return True, 0, limit  # Allow request if check fails
    
    def check_monthly_limit(self, api_provider: str, limit: int) -> Tuple[bool, int, int]:
        """
        Check if monthly limit has been reached.
        
        Returns:
            Tuple of (can_proceed, current_usage, remaining_requests)
        """
        try:
            month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp()
            
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM api_usage 
                    WHERE api_provider = ? AND timestamp >= ?
                """, (api_provider, month_start))
                
                current_usage = cursor.fetchone()[0]
                remaining = max(0, limit - current_usage)
                can_proceed = current_usage < limit
                
                return can_proceed, current_usage, remaining
                
        except Exception as e:
            log.error(f"Failed to check monthly limit: {e}")
            return True, 0, limit  # Allow request if check fails
    
    def get_usage_stats(self, api_provider: str, days: int = 30) -> UsageStats:
        """Get usage statistics for the specified period."""
        try:
            start_time = (datetime.now() - timedelta(days=days)).timestamp()
            
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_requests,
                        SUM(total_tokens) as total_tokens,
                        SUM(cost) as total_cost
                    FROM api_usage 
                    WHERE api_provider = ? AND timestamp >= ?
                """, (api_provider, start_time))
                
                row = cursor.fetchone()
                if row and row[0]:
                    return UsageStats(
                        total_requests=row[0],
                        successful_requests=row[1],
                        failed_requests=row[2],
                        total_tokens=row[3] or 0,
                        total_cost=row[4] or 0.0,
                        average_response_time=0.0  # Could be enhanced with timing data
                    )
                else:
                    return UsageStats(0, 0, 0, 0, 0.0, 0.0)
                    
        except Exception as e:
            log.error(f"Failed to get usage stats: {e}")
            return UsageStats(0, 0, 0, 0, 0.0, 0.0)
    
    def get_daily_usage(self, api_provider: str, date: Optional[datetime] = None) -> Dict[str, int]:
        """Get daily usage breakdown for a specific date."""
        if date is None:
            date = datetime.now()
        
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp()
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        strftime('%H', datetime(timestamp, 'unixepoch')) as hour,
                        COUNT(*) as requests,
                        SUM(total_tokens) as tokens
                    FROM api_usage 
                    WHERE api_provider = ? AND timestamp BETWEEN ? AND ?
                    GROUP BY hour
                    ORDER BY hour
                """, (api_provider, date_start, date_end))
                
                hourly_usage = {}
                for row in cursor.fetchall():
                    hourly_usage[row[0]] = {
                        'requests': row[1],
                        'tokens': row[2] or 0
                    }
                
                return hourly_usage
                
        except Exception as e:
            log.error(f"Failed to get daily usage: {e}")
            return {}
    
    def cleanup_old_records(self, days_to_keep: int = 90):
        """Clean up old usage records to prevent database bloat."""
        try:
            cutoff_time = (datetime.now() - timedelta(days=days_to_keep)).timestamp()
            
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM api_usage WHERE timestamp < ?", (cutoff_time,))
                deleted_count = cursor.rowcount
                
                conn.commit()
                log.info(f"Cleaned up {deleted_count} old API usage records")
                
        except Exception as e:
            log.error(f"Failed to cleanup old records: {e}")
    
    def export_usage_data(self, output_path: str, format: str = "csv"):
        """Export usage data to a file."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                if format.lower() == "csv":
                    import csv
                    
                    with open(output_path, 'w', newline='') as csvfile:
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM api_usage ORDER BY timestamp DESC")
                        
                        # Get column names
                        columns = [description[0] for description in cursor.description]
                        writer = csv.writer(csvfile)
                        writer.writerow(columns)
                        
                        # Write data
                        for row in cursor.fetchall():
                            writer.writerow(row)
                            
                elif format.lower() == "json":
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM api_usage ORDER BY timestamp DESC")
                    
                    columns = [description[0] for description in cursor.description]
                    data = []
                    
                    for row in cursor.fetchall():
                        row_dict = dict(zip(columns, row))
                        row_dict['timestamp'] = datetime.fromtimestamp(row_dict['timestamp']).isoformat()
                        data.append(row_dict)
                    
                    with open(output_path, 'w') as jsonfile:
                        json.dump(data, jsonfile, indent=2)
                
                log.info(f"Usage data exported to {output_path}")
                return True
                
        except Exception as e:
            log.error(f"Failed to export usage data: {e}")
            return False
    
    async def get_current_usage(self) -> Dict[str, Any]:
        """Get current API usage statistics."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Get current usage by provider
                cursor.execute("""
                    SELECT api_provider, COUNT(*) as count, SUM(cost) as total_cost
                    FROM api_usage 
                    GROUP BY api_provider
                """)
                provider_usage = {}
                for row in cursor.fetchall():
                    provider_usage[row[0]] = {
                        'requests': row[1],
                        'total_cost': row[2] or 0.0
                    }
                
                # Get requests in the last minute
                minute_ago = (datetime.now() - timedelta(minutes=1)).timestamp()
                cursor.execute("SELECT COUNT(*) FROM api_usage WHERE timestamp >= ?", (minute_ago,))
                requests_per_minute = cursor.fetchone()[0]
                
                return {
                    'providers': provider_usage,
                    'requests_per_minute': requests_per_minute,
                    'total_requests': sum(p['requests'] for p in provider_usage.values())
                }
                
        except Exception as e:
            log.error(f"Failed to get current usage: {e}")
            return {
                'providers': {},
                'requests_per_minute': 0,
                'total_requests': 0
            }
    
    def get_usage_summary(self) -> Dict[str, any]:
        """Get a comprehensive usage summary."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Get total usage
                cursor.execute("SELECT COUNT(*) FROM api_usage")
                total_requests = cursor.fetchone()[0]
                
                # Get usage by provider
                cursor.execute("""
                    SELECT api_provider, COUNT(*) as count, SUM(cost) as total_cost
                    FROM api_usage 
                    GROUP BY api_provider
                """)
                provider_usage = {}
                for row in cursor.fetchall():
                    provider_usage[row[0]] = {
                        'requests': row[1],
                        'total_cost': row[2] or 0.0
                    }
                
                # Get recent activity (last 24 hours)
                day_ago = (datetime.now() - timedelta(days=1)).timestamp()
                cursor.execute("SELECT COUNT(*) FROM api_usage WHERE timestamp >= ?", (day_ago,))
                recent_requests = cursor.fetchone()[0]
                
                return {
                    'total_requests': total_requests,
                    'provider_usage': provider_usage,
                    'recent_requests_24h': recent_requests,
                    'database_size_mb': self.database_path.stat().st_size / (1024 * 1024)
                }
                
        except Exception as e:
            log.error(f"Failed to get usage summary: {e}")
            return {}
