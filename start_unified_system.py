#!/usr/bin/env python3
"""
Unified System Startup Script for Biomedical Text Agent

This script provides a single entry point to start the complete integrated system,
including the unified server, frontend, and all system components.
"""

import os
import sys
import asyncio
import logging
import subprocess
import time
import signal
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedSystemManager:
    """Manages the complete unified Biomedical Text Agent system."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_path = self.project_root / "src"
        self.frontend_path = self.src_path / "ui" / "frontend"
        self.server_process = None
        self.frontend_process = None
        
        # Configuration
        self.backend_port = 8000
        self.frontend_port = 3000
        self.host = "127.0.0.1"
        
        # System status
        self.system_status = "stopped"
        self.startup_time = None
        
    def check_requirements(self) -> bool:
        """Check if all system requirements are met."""
        logger.info("🔍 Checking system requirements...")
        
        # Check if src directory exists
        if not self.src_path.exists():
            logger.error("❌ src directory not found")
            logger.error("Please run this script from the project root directory")
            return False
        
        # Check if virtual environment is activated
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.warning("⚠️  Virtual environment not detected")
            logger.info("Consider activating a virtual environment for better dependency management")
        
        # Check if .env file exists
        env_file = self.project_root / ".env"
        if not env_file.exists():
            logger.warning("⚠️  .env file not found")
            logger.info("Copy .env.example to .env and configure your settings")
            logger.info("cp .env.example .env")
        
        # Check if frontend is built
        frontend_build_path = self.frontend_path / "build"
        if not frontend_build_path.exists():
            logger.warning("⚠️  Frontend build not found")
            if not self.build_frontend():
                return False
        else:
            logger.info("✅ Frontend build found")
        
        # Check Python dependencies
        if not self.check_python_dependencies():
            return False
        
        logger.info("✅ All requirements met")
        return True
    
    def check_python_dependencies(self) -> bool:
        """Check if required Python packages are installed."""
        logger.info("🔍 Checking Python dependencies...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlite3",
            "pandas",
            "numpy",
            "pydantic",
            "python-dotenv"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"❌ Missing Python packages: {', '.join(missing_packages)}")
            logger.info("Install missing packages with: pip install -r requirements.txt")
            return False
        
        logger.info("✅ All Python dependencies available")
        return True
    
    def build_frontend(self) -> bool:
        """Build the React frontend if not already built."""
        try:
            logger.info("🔨 Building frontend...")
            
            if not self.frontend_path.exists():
                logger.error("❌ Frontend directory not found")
                return False
            
            # Check if npm is available
            try:
                subprocess.run(["npm", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error("❌ npm not found. Please install Node.js and npm")
                return False
            
            # Install dependencies
            logger.info("📦 Installing frontend dependencies...")
            result = subprocess.run(
                ["npm", "install"], 
                cwd=self.frontend_path, 
                check=True,
                capture_output=True,
                text=True
            )
            
            # Build frontend
            logger.info("🔨 Building frontend...")
            result = subprocess.run(
                ["npm", "run", "build"], 
                cwd=self.frontend_path, 
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info("✅ Frontend built successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error building frontend: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error building frontend: {e}")
            return False
    
    def start_backend_server(self) -> bool:
        """Start the unified backend server."""
        try:
            logger.info("🚀 Starting unified backend server...")
            
            # Start the server using the unified server module
            server_script = self.src_path / "api" / "unified_server.py"
            
            if not server_script.exists():
                logger.error(f"❌ Server script not found: {server_script}")
                return False
            
            # Start server process
            self.server_process = subprocess.Popen(
                [sys.executable, str(server_script), 
                 "--host", self.host, 
                 "--port", str(self.backend_port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if server is running
            if self.server_process.poll() is None:
                logger.info(f"✅ Backend server started on {self.host}:{self.backend_port}")
                return True
            else:
                logger.error("❌ Backend server failed to start")
                stdout, stderr = self.server_process.communicate()
                logger.error(f"stdout: {stdout}")
                logger.error(f"stderr: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start backend server: {e}")
            return False
    
    def start_frontend_dev_server(self) -> bool:
        """Start the frontend development server."""
        try:
            logger.info("🚀 Starting frontend development server...")
            
            # Start frontend dev server
            self.frontend_process = subprocess.Popen(
                ["npm", "start"],
                cwd=self.frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for server to start
            time.sleep(5)
            
            # Check if server is running
            if self.frontend_process.poll() is None:
                logger.info(f"✅ Frontend dev server started on port {self.frontend_port}")
                return True
            else:
                logger.error("❌ Frontend dev server failed to start")
                stdout, stderr = self.frontend_process.communicate()
                logger.error(f"stdout: {stdout}")
                logger.error(f"stderr: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start frontend dev server: {e}")
            return False
    
    def start_system(self, start_frontend: bool = True) -> bool:
        """Start the complete unified system."""
        try:
            logger.info("🚀 Starting Biomedical Text Agent Unified System...")
            
            # Check requirements first
            if not self.check_requirements():
                return False
            
            # Start backend server
            if not self.start_backend_server():
                return False
            
            # Start frontend if requested
            if start_frontend:
                if not self.start_frontend_dev_server():
                    logger.warning("⚠️  Frontend dev server failed to start, continuing with backend only")
            
            # Update system status
            self.system_status = "running"
            self.startup_time = time.time()
            
            logger.info("🎉 Biomedical Text Agent Unified System started successfully!")
            logger.info(f"🌐 Backend API: http://{self.host}:{self.backend_port}")
            logger.info(f"📚 API Documentation: http://{self.host}:{self.backend_port}/api/docs")
            logger.info(f"💚 Health Check: http://{self.host}:{self.backend_port}/health")
            
            if start_frontend:
                logger.info(f"🎨 Frontend: http://localhost:{self.frontend_port}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start system: {e}")
            return False
    
    def stop_system(self):
        """Stop the complete system."""
        logger.info("🛑 Stopping Biomedical Text Agent Unified System...")
        
        # Stop frontend process
        if self.frontend_process and self.frontend_process.poll() is None:
            logger.info("🛑 Stopping frontend dev server...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            self.frontend_process = None
        
        # Stop backend server
        if self.server_process and self.server_process.poll() is None:
            logger.info("🛑 Stopping backend server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
        
        # Update system status
        self.system_status = "stopped"
        
        logger.info("✅ System stopped successfully")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        status = {
            "status": self.system_status,
            "backend": {
                "running": self.server_process is not None and self.server_process.poll() is None,
                "port": self.backend_port,
                "host": self.host
            },
            "frontend": {
                "running": self.frontend_process is not None and self.frontend_process.poll() is None,
                "port": self.frontend_port
            }
        }
        
        if self.startup_time:
            status["uptime"] = time.time() - self.startup_time
        
        return status
    
    def check_system_health(self) -> bool:
        """Check if the system is healthy."""
        try:
            import requests
            
            # Check backend health
            try:
                response = requests.get(f"http://{self.host}:{self.backend_port}/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Backend health check passed")
                    return True
                else:
                    logger.error(f"❌ Backend health check failed: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Backend health check failed: {e}")
                return False
                
        except ImportError:
            logger.warning("⚠️  requests module not available, skipping health check")
            return True
    
    def run_demo(self):
        """Run a demonstration of the system."""
        logger.info("🎯 Running system demonstration...")
        
        # Start system
        if not self.start_system(start_frontend=False):
            logger.error("❌ Failed to start system for demo")
            return False
        
        # Wait for system to be ready
        logger.info("⏳ Waiting for system to be ready...")
        time.sleep(5)
        
        # Check health
        if not self.check_system_health():
            logger.error("❌ System health check failed")
            self.stop_system()
            return False
        
        logger.info("✅ System demonstration completed successfully")
        logger.info("🎉 Your Biomedical Text Agent is ready!")
        logger.info(f"🌐 Access the API at: http://{self.host}:{self.backend_port}")
        logger.info(f"📚 View documentation at: http://{self.host}:{self.backend_port}/api/docs")
        
        return True

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
    if hasattr(signal_handler, 'system_manager'):
        signal_handler.system_manager.stop_system()
    sys.exit(0)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Biomedical Text Agent Unified System")
    parser.add_argument("command", nargs="?", default="start", 
                       choices=["start", "stop", "restart", "status", "demo", "check"],
                       help="Command to execute")
    parser.add_argument("--no-frontend", action="store_true", 
                       help="Start without frontend development server")
    parser.add_argument("--host", default="127.0.0.1", 
                       help="Host to bind backend server to")
    parser.add_argument("--backend-port", type=int, default=8000, 
                       help="Backend server port")
    parser.add_argument("--frontend-port", type=int, default=3000, 
                       help="Frontend development server port")
    
    args = parser.parse_args()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create system manager
    system_manager = UnifiedSystemManager()
    system_manager.host = args.host
    system_manager.backend_port = args.backend_port
    system_manager.frontend_port = args.frontend_port
    
    # Store reference for signal handler
    signal_handler.system_manager = system_manager
    
    try:
        if args.command == "start":
            success = system_manager.start_system(start_frontend=not args.no_frontend)
            if success:
                logger.info("🎉 System started successfully!")
                logger.info("Press Ctrl+C to stop the system")
                
                # Keep the script running
                try:
                    while True:
                        time.sleep(1)
                        # Check if processes are still running
                        if (system_manager.server_process and 
                            system_manager.server_process.poll() is not None):
                            logger.error("❌ Backend server stopped unexpectedly")
                            break
                        if (system_manager.frontend_process and 
                            system_manager.frontend_process.poll() is not None):
                            logger.warning("⚠️  Frontend server stopped unexpectedly")
                except KeyboardInterrupt:
                    logger.info("🛑 Received interrupt signal")
                    system_manager.stop_system()
            else:
                logger.error("❌ Failed to start system")
                sys.exit(1)
                
        elif args.command == "stop":
            system_manager.stop_system()
            
        elif args.command == "restart":
            system_manager.stop_system()
            time.sleep(2)
            success = system_manager.start_system(start_frontend=not args.no_frontend)
            if not success:
                sys.exit(1)
                
        elif args.command == "status":
            status = system_manager.get_system_status()
            print(f"System Status: {status['status']}")
            print(f"Backend: {'Running' if status['backend']['running'] else 'Stopped'}")
            print(f"Frontend: {'Running' if status['frontend']['running'] else 'Stopped'}")
            if 'uptime' in status:
                print(f"Uptime: {status['uptime']:.1f} seconds")
                
        elif args.command == "demo":
            success = system_manager.run_demo()
            if success:
                logger.info("🎯 Demo completed successfully")
                system_manager.stop_system()
            else:
                logger.error("❌ Demo failed")
                sys.exit(1)
                
        elif args.command == "check":
            if system_manager.check_requirements():
                logger.info("✅ System requirements check passed")
            else:
                logger.error("❌ System requirements check failed")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        system_manager.stop_system()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        system_manager.stop_system()
        sys.exit(1)

if __name__ == "__main__":
    main()