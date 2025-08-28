#!/usr/bin/env python3
"""
UI Setup Script

This script sets up the complete UI system for the biomedical text agent,
including backend API, frontend React app, and database initialization.
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import argparse


class UISetup:
    """UI setup and management class."""
    
    def __init__(self, project_root: str = None):
        """Initialize UI setup."""
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.ui_root = self.project_root / "src" / "ui"
        self.backend_root = self.ui_root / "backend"
        self.frontend_root = self.ui_root / "frontend"
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed."""
        print("🔍 Checking prerequisites...")
        
        # Check Python
        try:
            python_version = subprocess.check_output([sys.executable, "--version"], text=True).strip()
            print(f"✅ Python: {python_version}")
        except Exception as e:
            print(f"❌ Python check failed: {e}")
            return False
        
        # Check Node.js
        try:
            node_version = subprocess.check_output(["node", "--version"], text=True).strip()
            print(f"✅ Node.js: {node_version}")
        except Exception as e:
            print(f"❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org/")
            return False
        
        # Check npm
        try:
            npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
            print(f"✅ npm: {npm_version}")
        except Exception as e:
            print(f"❌ npm not found: {e}")
            return False
        
        return True
    
    def setup_backend(self) -> bool:
        """Set up the FastAPI backend."""
        print("\n🔧 Setting up FastAPI backend...")
        
        try:
            # Install Python dependencies
            backend_requirements = [
                "fastapi>=0.104.0",
                "uvicorn[standard]>=0.24.0",
                "websockets>=11.0",
                "python-multipart>=0.0.6",
                "python-jose[cryptography]>=3.3.0",
                "passlib[bcrypt]>=1.7.4",
                "aiosqlite>=0.19.0",
                "asyncpg>=0.29.0",
                "redis>=5.0.0",
                "celery>=5.3.0",
                "prometheus-client>=0.19.0",
                "psutil>=5.9.0"
            ]
            
            print("📦 Installing backend dependencies...")
            for requirement in backend_requirements:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", requirement
                ], check=True, capture_output=True)
            
            print("✅ Backend dependencies installed")
            
            # Create backend configuration
            self._create_backend_config()
            
            # Initialize database
            self._initialize_database()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Backend setup failed: {e}")
            return False
    
    def setup_frontend(self) -> bool:
        """Set up the React frontend."""
        print("\n🔧 Setting up React frontend...")
        
        try:
            # Change to frontend directory
            os.chdir(self.frontend_root)
            
            # Install npm dependencies
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], check=True)
            
            print("✅ Frontend dependencies installed")
            
            # Create environment file
            self._create_frontend_env()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Frontend setup failed: {e}")
            return False
        finally:
            # Return to original directory
            os.chdir(self.project_root)
    
    def _create_backend_config(self):
        """Create backend configuration files."""
        print("📝 Creating backend configuration...")
        
        # Create .env file for backend
        env_content = """# Backend Configuration
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./data/database/biomedical_agent.db
REDIS_URL=redis://localhost:6379/0

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Authentication
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# API Settings
API_RATE_LIMIT=1000
API_RATE_LIMIT_PERIOD=3600

# WebSocket Settings
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=1000

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
"""
        
        env_file = self.backend_root / ".env"
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print(f"✅ Created backend .env file: {env_file}")
    
    def _create_frontend_env(self):
        """Create frontend environment files."""
        print("📝 Creating frontend configuration...")
        
        # Create .env.local file for frontend
        env_content = """# Frontend Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/api/v1/ws

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=false
REACT_APP_ENABLE_DEBUG=true

# Authentication
REACT_APP_AUTH_PROVIDER=local
REACT_APP_SESSION_TIMEOUT=3600

# UI Settings
REACT_APP_THEME=light
REACT_APP_LANGUAGE=en
"""
        
        env_file = self.frontend_root / ".env.local"
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print(f"✅ Created frontend .env.local file: {env_file}")
    
    def _initialize_database(self):
        """Initialize the database with required tables."""
        print("🗄️ Initializing database...")
        
        # Create database initialization script
        init_script = self.backend_root / "init_db.py"
        
        init_content = '''"""
Database Initialization Script
"""

import asyncio
import sqlite3
from pathlib import Path

async def init_database():
    """Initialize SQLite database with required tables."""
    db_path = Path("data/database/biomedical_agent.db")
    
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
'''
        
        with open(init_script, "w") as f:
            f.write(init_content)
        
        # Run database initialization
        try:
            subprocess.run([sys.executable, str(init_script)], 
                         cwd=self.backend_root, check=True)
            print("✅ Database initialized")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Database initialization failed: {e}")
    
    def build_frontend(self) -> bool:
        """Build the React frontend for production."""
        print("\n🏗️ Building frontend for production...")
        
        try:
            os.chdir(self.frontend_root)
            subprocess.run(["npm", "run", "build"], check=True)
            print("✅ Frontend built successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Frontend build failed: {e}")
            return False
        finally:
            os.chdir(self.project_root)
    
    def start_development_servers(self):
        """Start both backend and frontend development servers."""
        print("\n🚀 Starting development servers...")
        
        # Start backend server
        backend_cmd = [
            sys.executable, "-m", "uvicorn",
            "src.ui.backend.app:create_app",
            "--factory",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        print("🔧 Starting backend server on http://localhost:8000")
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=self.project_root
        )
        
        # Start frontend server
        print("🔧 Starting frontend server on http://localhost:3000")
        frontend_process = subprocess.Popen(
            ["npm", "start"], 
            cwd=self.frontend_root
        )
        
        print("\n✅ Development servers started!")
        print("📊 Backend API: http://localhost:8000")
        print("📊 API Documentation: http://localhost:8000/api/docs")
        print("🌐 Frontend UI: http://localhost:3000")
        print("\nPress Ctrl+C to stop servers")
        
        try:
            # Wait for processes
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Servers stopped")
    
    def create_production_config(self):
        """Create production configuration files."""
        print("\n📋 Creating production configuration...")
        
        # Docker Compose file
        docker_compose = self.ui_root / "docker-compose.yml"
        compose_content = """version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - DATABASE_URL=postgresql://user:password@db:5432/biomedical_agent
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=biomedical_agent
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
"""
        
        with open(docker_compose, "w") as f:
            f.write(compose_content)
        
        print(f"✅ Created Docker Compose file: {docker_compose}")
        
        # Nginx configuration
        nginx_config = self.ui_root / "nginx.conf"
        nginx_content = """server {
    listen 80;
    server_name localhost;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /api/v1/ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
        
        with open(nginx_config, "w") as f:
            f.write(nginx_content)
        
        print(f"✅ Created Nginx configuration: {nginx_config}")
    
    def run_tests(self) -> bool:
        """Run tests for both backend and frontend."""
        print("\n🧪 Running tests...")
        
        success = True
        
        # Backend tests
        try:
            print("🔧 Running backend tests...")
            subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "-v"
            ], cwd=self.backend_root, check=True)
            print("✅ Backend tests passed")
        except subprocess.CalledProcessError:
            print("❌ Backend tests failed")
            success = False
        
        # Frontend tests
        try:
            print("🌐 Running frontend tests...")
            subprocess.run([
                "npm", "test", "--", "--coverage", "--watchAll=false"
            ], cwd=self.frontend_root, check=True)
            print("✅ Frontend tests passed")
        except subprocess.CalledProcessError:
            print("❌ Frontend tests failed")
            success = False
        
        return success


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Biomedical Text Agent UI Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full setup
  python setup_ui.py --setup-all
  
  # Setup backend only
  python setup_ui.py --setup-backend
  
  # Setup frontend only
  python setup_ui.py --setup-frontend
  
  # Start development servers
  python setup_ui.py --dev
  
  # Build for production
  python setup_ui.py --build
  
  # Run tests
  python setup_ui.py --test
        """
    )
    
    parser.add_argument('--setup-all', action='store_true', help='Setup both backend and frontend')
    parser.add_argument('--setup-backend', action='store_true', help='Setup backend only')
    parser.add_argument('--setup-frontend', action='store_true', help='Setup frontend only')
    parser.add_argument('--dev', action='store_true', help='Start development servers')
    parser.add_argument('--build', action='store_true', help='Build for production')
    parser.add_argument('--test', action='store_true', help='Run tests')
    parser.add_argument('--production-config', action='store_true', help='Create production config files')
    parser.add_argument('--project-root', help='Project root directory')
    
    args = parser.parse_args()
    
    # Initialize setup
    setup = UISetup(args.project_root)
    
    # Check prerequisites
    if not setup.check_prerequisites():
        sys.exit(1)
    
    success = True
    
    # Setup operations
    if args.setup_all or args.setup_backend:
        success &= setup.setup_backend()
    
    if args.setup_all or args.setup_frontend:
        success &= setup.setup_frontend()
    
    # Development servers
    if args.dev:
        if success:
            setup.start_development_servers()
        else:
            print("❌ Setup failed, cannot start development servers")
            sys.exit(1)
    
    # Build for production
    if args.build:
        success &= setup.build_frontend()
    
    # Run tests
    if args.test:
        success &= setup.run_tests()
    
    # Production configuration
    if args.production_config:
        setup.create_production_config()
    
    # Default action
    if not any([args.setup_all, args.setup_backend, args.setup_frontend, 
                args.dev, args.build, args.test, args.production_config]):
        print("🎯 Biomedical Text Agent UI Setup")
        print("Use --help for available options")
        print("\nQuick start:")
        print("  python setup_ui.py --setup-all --dev")
    
    if not success:
        sys.exit(1)
    
    print("\n🎉 UI setup completed successfully!")


if __name__ == "__main__":
    main()

