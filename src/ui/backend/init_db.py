"""
Database Initialization Script
"""

import asyncio
import sqlite3
from pathlib import Path

async def init_database():
    """Initialize SQLite database with required tables."""
    db_path = Path("biomedical_agent.db")
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            permissions TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            metadata TEXT DEFAULT '{}',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS extractions (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            agent_type TEXT NOT NULL,
            extracted_data TEXT DEFAULT '{}',
            status TEXT DEFAULT 'pending',
            confidence_score REAL DEFAULT 0.0,
            processing_time_seconds REAL DEFAULT 0.0,
            validation_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS system_activities (
            id TEXT PRIMARY KEY,
            activity_type TEXT NOT NULL,
            description TEXT NOT NULL,
            user_id TEXT,
            metadata TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS system_alerts (
            id TEXT PRIMARY KEY,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            dismissed_at TIMESTAMP,
            dismissed_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS api_requests (
            id TEXT PRIMARY KEY,
            endpoint TEXT NOT NULL,
            method TEXT NOT NULL,
            user_id TEXT,
            response_status INTEGER,
            response_time_ms REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)
    
    # Create default admin user
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, email, name, password_hash, role, permissions)
        VALUES ('admin', 'admin@example.com', 'Administrator', 
                '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6QBjDKJhOu', 
                'admin', '["read", "write", "admin"]')
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully")

if __name__ == "__main__":
    asyncio.run(init_database())
