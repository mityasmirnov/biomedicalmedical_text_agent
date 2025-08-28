"""
Enhanced SQLite Manager for Biomedical Text Agent.

This module provides enhanced database management capabilities for linked data storage,
working alongside the existing sqlite_manager.py structure.
"""

import sqlite3
import logging
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import asyncio
from contextlib import asynccontextmanager
import threading
import queue

# Import the original SQLite manager for compatibility
from .sqlite_manager import SQLiteManager

logger = logging.getLogger(__name__)

# ============================================================================
# Enhanced Database Models and Schemas
# ============================================================================

class EnhancedDocumentSchema:
    """Enhanced document schema with comprehensive metadata."""
    
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS enhanced_documents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        metadata TEXT,  -- JSON string
        extracted_entities TEXT,  -- JSON string
        processing_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        confidence_score REAL DEFAULT 0.0,
        source_file TEXT,
        file_type TEXT,
        file_size INTEGER,
        checksum TEXT,
        version INTEGER DEFAULT 1,
        tags TEXT,  -- JSON string
        annotations TEXT,  -- JSON string
        linked_documents TEXT,  -- JSON string
        processing_history TEXT  -- JSON string
    )
    """
    
    CREATE_INDEXES_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_enhanced_docs_title ON enhanced_documents(title)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_docs_status ON enhanced_documents(processing_status)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_docs_created ON enhanced_documents(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_docs_confidence ON enhanced_documents(confidence_score)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_docs_file_type ON enhanced_documents(file_type)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_docs_tags ON enhanced_documents(tags)"
    ]

class EnhancedExtractionSchema:
    """Enhanced extraction schema for tracking processing requests."""
    
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS enhanced_extractions (
        request_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        extraction_type TEXT NOT NULL,
        parameters TEXT,  -- JSON string
        priority TEXT DEFAULT 'normal',
        status TEXT DEFAULT 'pending',
        result TEXT,  -- JSON string
        error TEXT,
        processing_time REAL,
        confidence_score REAL DEFAULT 0.0,
        metadata TEXT,  -- JSON string
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        retry_count INTEGER DEFAULT 0,
        max_retries INTEGER DEFAULT 3,
        callback_url TEXT,
        worker_id TEXT,
        FOREIGN KEY (document_id) REFERENCES enhanced_documents(id)
    )
    """
    
    CREATE_INDEXES_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_enhanced_extractions_doc_id ON enhanced_extractions(document_id)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_extractions_status ON enhanced_extractions(status)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_extractions_type ON enhanced_extractions(extraction_type)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_extractions_priority ON enhanced_extractions(priority)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_extractions_created ON enhanced_extractions(created_at)"
    ]

class EnhancedAnalyticsSchema:
    """Enhanced analytics schema for tracking system metrics."""
    
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS enhanced_analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric_name TEXT NOT NULL,
        metric_value REAL,
        metric_data TEXT,  -- JSON string
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        category TEXT,
        tags TEXT,  -- JSON string
        source TEXT,
        version TEXT
    )
    """
    
    CREATE_INDEXES_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_enhanced_analytics_name ON enhanced_analytics(metric_name)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_analytics_timestamp ON enhanced_analytics(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_analytics_category ON enhanced_analytics(category)"
    ]

class EnhancedRelationshipsSchema:
    """Enhanced relationships schema for linked data storage."""
    
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS enhanced_relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        relationship_type TEXT NOT NULL,
        relationship_data TEXT,  -- JSON string
        confidence_score REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        source_type TEXT,
        target_type TEXT,
        metadata TEXT,  -- JSON string
        UNIQUE(source_id, target_id, relationship_type)
    )
    """
    
    CREATE_INDEXES_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_enhanced_relationships_source ON enhanced_relationships(source_id)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_relationships_target ON enhanced_relationships(target_id)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_relationships_type ON enhanced_relationships(relationship_type)",
        "CREATE INDEX IF NOT EXISTS idx_enhanced_relationships_confidence ON enhanced_relationships(confidence_score)"
    ]

# ============================================================================
# Enhanced SQLite Manager Class
# ============================================================================

class EnhancedSQLiteManager:
    """Enhanced SQLite manager with advanced features for linked data storage."""
    
    def __init__(self, db_path: str = "enhanced_biomedical_agent.db"):
        """Initialize the enhanced SQLite manager."""
        self.db_path = db_path
        self.connection = None
        self.lock = threading.Lock()
        self.connection_pool = queue.Queue(maxsize=10)
        self._initialize_database()
        
        # Initialize the original SQLite manager for compatibility
        self.original_manager = SQLiteManager(db_path.replace("enhanced_", ""))
    
    def _initialize_database(self):
        """Initialize the enhanced database with all schemas."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create enhanced tables
                logger.info("Creating enhanced database tables...")
                
                # Documents table
                cursor.execute(EnhancedDocumentSchema.CREATE_TABLE_SQL)
                for index_sql in EnhancedDocumentSchema.CREATE_INDEXES_SQL:
                    cursor.execute(index_sql)
                
                # Extractions table
                cursor.execute(EnhancedExtractionSchema.CREATE_TABLE_SQL)
                for index_sql in EnhancedExtractionSchema.CREATE_INDEXES_SQL:
                    cursor.execute(index_sql)
                
                # Analytics table
                cursor.execute(EnhancedAnalyticsSchema.CREATE_TABLE_SQL)
                for index_sql in EnhancedAnalyticsSchema.CREATE_INDEXES_SQL:
                    cursor.execute(index_sql)
                
                # Relationships table
                cursor.execute(EnhancedRelationshipsSchema.CREATE_TABLE_SQL)
                for index_sql in EnhancedRelationshipsSchema.CREATE_INDEXES_SQL:
                    cursor.execute(index_sql)
                
                conn.commit()
                logger.info("Enhanced database tables created successfully")
                
        except Exception as e:
            logger.error(f"Error initializing enhanced database: {e}")
            raise
    
    @asynccontextmanager
    async def _get_connection(self):
        """Get a database connection from the pool."""
        try:
            # Try to get from pool first
            try:
                conn = self.connection_pool.get_nowait()
            except queue.Empty:
                # Create new connection if pool is empty
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
            
            yield conn
            
            # Return connection to pool
            try:
                self.connection_pool.put_nowait(conn)
            except queue.Full:
                # Close connection if pool is full
                conn.close()
                
        except Exception as e:
            logger.error(f"Error managing database connection: {e}")
            raise
    
    def _get_connection_sync(self):
        """Get a database connection synchronously."""
        return sqlite3.connect(self.db_path)
    
    # ============================================================================
    # Enhanced Document Management
    # ============================================================================
    
    async def create_enhanced_document(
        self,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        source_file: Optional[str] = None,
        file_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        annotations: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new enhanced document."""
        try:
            document_id = f"doc_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(title)}"
            
            # Calculate checksum
            checksum = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO enhanced_documents (
                        id, title, content, metadata, source_file, file_type, 
                        file_size, checksum, tags, annotations, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    document_id, title, content,
                    json.dumps(metadata or {}),
                    source_file, file_type,
                    len(content.encode('utf-8')),
                    checksum,
                    json.dumps(tags or []),
                    json.dumps(annotations or {}),
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
                
                conn.commit()
                logger.info(f"Created enhanced document: {document_id}")
                return document_id
                
        except Exception as e:
            logger.error(f"Error creating enhanced document: {e}")
            raise
    
    async def get_enhanced_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an enhanced document by ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM enhanced_documents WHERE id = ?
                """, (document_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving enhanced document: {e}")
            raise
    
    async def update_enhanced_document(
        self,
        document_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update an enhanced document."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Build update query dynamically
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['metadata', 'extracted_entities', 'tags', 'annotations', 'linked_documents']:
                        set_clauses.append(f"{key} = ?")
                        values.append(json.dumps(value))
                    elif key in ['title', 'content', 'processing_status', 'confidence_score']:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                if not set_clauses:
                    return False
                
                set_clauses.append("updated_at = ?")
                values.append(datetime.utcnow())
                values.append(document_id)
                
                query = f"UPDATE enhanced_documents SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(query, values)
                
                conn.commit()
                logger.info(f"Updated enhanced document: {document_id}")
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating enhanced document: {e}")
            raise
    
    async def delete_enhanced_document(self, document_id: str) -> bool:
        """Delete an enhanced document."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM enhanced_documents WHERE id = ?", (document_id,))
                conn.commit()
                
                logger.info(f"Deleted enhanced document: {document_id}")
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting enhanced document: {e}")
            raise
    
    async def search_enhanced_documents(
        self,
        query: str = "",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "DESC"
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Search enhanced documents with advanced filtering."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Build WHERE clause
                where_clauses = []
                values = []
                
                if query:
                    where_clauses.append("(title LIKE ? OR content LIKE ?)")
                    values.extend([f"%{query}%", f"%{query}%"])
                
                if filters:
                    for key, value in filters.items():
                        if key == "processing_status":
                            where_clauses.append("processing_status = ?")
                            values.append(value)
                        elif key == "file_type":
                            where_clauses.append("file_type = ?")
                            values.append(value)
                        elif key == "tags":
                            where_clauses.append("tags LIKE ?")
                            values.append(f"%{value}%")
                
                where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
                
                # Count total results
                count_query = f"SELECT COUNT(*) FROM enhanced_documents WHERE {where_sql}"
                cursor.execute(count_query, values)
                total_count = cursor.fetchone()[0]
                
                # Get paginated results
                order_sql = f"ORDER BY {sort_by} {sort_order}"
                limit_sql = f"LIMIT {limit} OFFSET {offset}"
                
                search_query = f"""
                    SELECT * FROM enhanced_documents 
                    WHERE {where_sql} 
                    {order_sql} 
                    {limit_sql}
                """
                
                cursor.execute(search_query, values)
                rows = cursor.fetchall()
                
                results = [self._row_to_dict(row) for row in rows]
                return results, total_count
                
        except Exception as e:
            logger.error(f"Error searching enhanced documents: {e}")
            raise
    
    # ============================================================================
    # Enhanced Extraction Management
    # ============================================================================
    
    async def create_extraction_request(
        self,
        document_id: str,
        extraction_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        callback_url: Optional[str] = None
    ) -> str:
        """Create a new extraction request."""
        try:
            request_id = f"req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(document_id)}"
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO enhanced_extractions (
                        request_id, document_id, extraction_type, parameters,
                        priority, callback_url, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    request_id, document_id, extraction_type,
                    json.dumps(parameters or {}),
                    priority, callback_url,
                    datetime.utcnow(), datetime.utcnow()
                ))
                
                conn.commit()
                logger.info(f"Created extraction request: {request_id}")
                return request_id
                
        except Exception as e:
            logger.error(f"Error creating extraction request: {e}")
            raise
    
    async def update_extraction_status(
        self,
        request_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        processing_time: Optional[float] = None,
        confidence_score: Optional[float] = None
    ) -> bool:
        """Update extraction request status."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                updates = {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
                
                if result is not None:
                    updates["result"] = json.dumps(result)
                if error is not None:
                    updates["error"] = error
                if processing_time is not None:
                    updates["processing_time"] = processing_time
                if confidence_score is not None:
                    updates["confidence_score"] = confidence_score
                
                if status == "started":
                    updates["started_at"] = datetime.utcnow()
                elif status in ["completed", "failed"]:
                    updates["completed_at"] = datetime.utcnow()
                
                # Build update query
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ["result"]:
                        set_clauses.append(f"{key} = ?")
                        values.append(json.dumps(value) if isinstance(value, dict) else value)
                    else:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                values.append(request_id)
                query = f"UPDATE enhanced_extractions SET {', '.join(set_clauses)} WHERE request_id = ?"
                
                cursor.execute(query, values)
                conn.commit()
                
                logger.info(f"Updated extraction status: {request_id} -> {status}")
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating extraction status: {e}")
            raise
    
    async def get_extraction_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get extraction request by ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM enhanced_extractions WHERE request_id = ?
                """, (request_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving extraction request: {e}")
            raise
    
    async def get_pending_extractions(
        self,
        limit: int = 10,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get pending extraction requests."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                where_clause = "status = 'pending'"
                values = []
                
                if priority:
                    where_clause += " AND priority = ?"
                    values.append(priority)
                
                query = f"""
                    SELECT * FROM enhanced_extractions 
                    WHERE {where_clause}
                    ORDER BY 
                        CASE priority 
                            WHEN 'high' THEN 1 
                            WHEN 'normal' THEN 2 
                            WHEN 'low' THEN 3 
                        END,
                        created_at ASC
                    LIMIT ?
                """
                
                values.append(limit)
                cursor.execute(query, values)
                
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error retrieving pending extractions: {e}")
            raise
    
    # ============================================================================
    # Enhanced Analytics Management
    # ============================================================================
    
    async def record_metric(
        self,
        metric_name: str,
        metric_value: Optional[float] = None,
        metric_data: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None
    ) -> bool:
        """Record a metric for analytics."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO enhanced_analytics (
                        metric_name, metric_value, metric_data, category, tags, source, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric_name, metric_value,
                    json.dumps(metric_data or {}),
                    category,
                    json.dumps(tags or []),
                    source,
                    "2.0.0"
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
            raise
    
    async def get_metrics(
        self,
        metric_name: Optional[str] = None,
        category: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve metrics with filtering."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                where_clauses = []
                values = []
                
                if metric_name:
                    where_clauses.append("metric_name = ?")
                    values.append(metric_name)
                
                if category:
                    where_clauses.append("category = ?")
                    values.append(category)
                
                if start_time:
                    where_clauses.append("timestamp >= ?")
                    values.append(start_time)
                
                if end_time:
                    where_clauses.append("timestamp <= ?")
                    values.append(end_time)
                
                where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
                
                query = f"""
                    SELECT * FROM enhanced_analytics 
                    WHERE {where_sql}
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                
                values.append(limit)
                cursor.execute(query, values)
                
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error retrieving metrics: {e}")
            raise
    
    # ============================================================================
    # Enhanced Relationships Management
    # ============================================================================
    
    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        relationship_data: Optional[Dict[str, Any]] = None,
        confidence_score: float = 0.0,
        source_type: Optional[str] = None,
        target_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Create a relationship between entities."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO enhanced_relationships (
                        source_id, target_id, relationship_type, relationship_data,
                        confidence_score, source_type, target_type, metadata,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    source_id, target_id, relationship_type,
                    json.dumps(relationship_data or {}),
                    confidence_score, source_type, target_type,
                    json.dumps(metadata or {}),
                    datetime.utcnow(), datetime.utcnow()
                ))
                
                conn.commit()
                relationship_id = cursor.lastrowid
                logger.info(f"Created relationship: {relationship_id}")
                return relationship_id
                
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            raise
    
    async def get_relationships(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both"
    ) -> List[Dict[str, Any]]:
        """Get relationships for an entity."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if direction == "outgoing":
                    where_clause = "source_id = ?"
                    params = [entity_id]
                elif direction == "incoming":
                    where_clause = "target_id = ?"
                    params = [entity_id]
                else:  # both
                    where_clause = "(source_id = ? OR target_id = ?)"
                    params = [entity_id, entity_id]
                
                if relationship_type:
                    where_clause += " AND relationship_type = ?"
                    params.append(relationship_type)
                
                query = f"""
                    SELECT * FROM enhanced_relationships 
                    WHERE {where_clause}
                    ORDER BY confidence_score DESC, created_at DESC
                """
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error retrieving relationships: {e}")
            raise
    
    # ============================================================================
    # Utility Methods
    # ============================================================================
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert a database row to a dictionary."""
        if hasattr(row, 'keys'):
            return {key: row[key] for key in row.keys()}
        else:
            # Handle regular tuples
            columns = [description[0] for description in row.description]
            return dict(zip(columns, row))
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Document counts
                cursor.execute("SELECT COUNT(*) FROM enhanced_documents")
                stats["total_documents"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM enhanced_documents WHERE processing_status = 'completed'")
                stats["completed_documents"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM enhanced_documents WHERE processing_status = 'pending'")
                stats["pending_documents"] = cursor.fetchone()[0]
                
                # Extraction counts
                cursor.execute("SELECT COUNT(*) FROM enhanced_extractions")
                stats["total_extractions"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM enhanced_extractions WHERE status = 'pending'")
                stats["pending_extractions"] = cursor.fetchone()[0]
                
                # Relationship counts
                cursor.execute("SELECT COUNT(*) FROM enhanced_relationships")
                stats["total_relationships"] = cursor.fetchone()[0]
                
                # Analytics counts
                cursor.execute("SELECT COUNT(*) FROM enhanced_analytics")
                stats["total_metrics"] = cursor.fetchone()[0]
                
                # Database size
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                stats["database_size_bytes"] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            raise
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """Clean up old data to maintain database performance."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Clean up old analytics data
                cursor.execute("DELETE FROM enhanced_analytics WHERE timestamp < ?", (cutoff_date,))
                analytics_deleted = cursor.rowcount
                
                # Clean up old failed extractions
                cursor.execute("""
                    DELETE FROM enhanced_extractions 
                    WHERE status = 'failed' AND created_at < ?
                """, (cutoff_date,))
                extractions_deleted = cursor.rowcount
                
                conn.commit()
                
                total_deleted = analytics_deleted + extractions_deleted
                logger.info(f"Cleaned up {total_deleted} old records")
                return total_deleted
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            raise
    
    async def close(self):
        """Close all database connections."""
        try:
            # Close connections in pool
            while not self.connection_pool.empty():
                try:
                    conn = self.connection_pool.get_nowait()
                    conn.close()
                except queue.Empty:
                    break
            
            # Close main connection
            if self.connection:
                self.connection.close()
                
            logger.info("Enhanced SQLite manager closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing enhanced SQLite manager: {e}")
            raise

# ============================================================================
# Export Functions
# ============================================================================

__all__ = [
    "EnhancedSQLiteManager",
    "EnhancedDocumentSchema",
    "EnhancedExtractionSchema", 
    "EnhancedAnalyticsSchema",
    "EnhancedRelationshipsSchema"
]