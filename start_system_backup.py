#!/usr/bin/env python3
"""
Biomedical Text Agent - Unified System Startup Script.

This script provides a clean, unified way to start the Biomedical Text Agent system
with automatic detection of available features and graceful fallbacks.
"""

import os
import sys
import asyncio
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemManager:
    """Manages the Biomedical Text Agent system startup and configuration."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_path = self.project_root / "src"
        self.frontend_path = self.src_path / "ui" / "frontend"
        self.backend_process = None
        self.backend_port = 8000  # Default port
        
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
        
        # Check if frontend is built
        frontend_build_path = self.frontend_path / "build"
        if not frontend_build_path.exists():
            logger.warning("⚠️  Frontend build not found")
            if not self.build_frontend():
                return False
        else:
            logger.info("✅ Frontend build found")
        
        logger.info("✅ All requirements met")
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
            
            # Build frontend
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
    
    def start_backend(self) -> bool:
        """Start the FastAPI backend server."""
        logger.info("🚀 Starting backend server...")
        
        try:
            # Check for available server options
            server_options = [
                ("standalone_server.py", "Standalone API server"),
                ("src/api/standalone_server.py", "API standalone server"),
                ("src/api/enhanced_server.py", "Enhanced API server")
            ]
            
            server_script = None
            server_name = None
            
            for script_path, name in server_options:
                if Path(script_path).exists():
                    server_script = script_path
                    server_name = name
                    break
            
            if not server_script:
                logger.error("❌ No server script found")
                return False
            
            logger.info(f"✅ Using {server_name}: {server_script}")
            
            # Check if port 8000 is available, if not try 8001
            import socket
            def is_port_available(port):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        s.bind(('127.0.0.1', port))
                        return True
                    except OSError:
                        return False
            
            port = 8000
            if not is_port_available(port):
                port = 8001
                logger.info(f"⚠️  Port 8000 is busy, trying port {port}")
                if not is_port_available(port):
                    port = 8002
                    logger.info(f"⚠️  Port 8001 is busy, trying port {port}")
            
            # Start the server in the background
            self.backend_process = subprocess.Popen([
                sys.executable, str(server_script), "--port", str(port)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            # Check if the process is still running
            if self.backend_process.poll() is None:
                logger.info(f"✅ Backend server started successfully on port {port}")
                # Store the port for system info display
                self.backend_port = port
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                logger.error("❌ Backend server failed to start")
                logger.error(f"stdout: {stdout.decode()}")
                logger.error(f"stderr: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting backend: {e}")
            return False
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check the health of the running system."""
        try:
            import requests
            
            health_status = {}
            
            # Check backend health
            try:
                response = requests.get(f"http://localhost:{self.backend_port}/api/health", timeout=5)
                health_status["backend"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
            except Exception as e:
                health_status["backend"] = {
                    "status": "unreachable",
                    "error": str(e)
                }
            
            # Check frontend
            try:
                response = requests.get(f"http://localhost:{self.backend_port}/", timeout=5)
                health_status["frontend"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
            except Exception as e:
                health_status["frontend"] = {
                    "status": "unreachable",
                    "error": str(e)
                }
            
            return health_status
            
        except ImportError:
            logger.warning("⚠️  requests module not available, skipping health check")
            return {"status": "health_check_unavailable"}
    
    def display_system_info(self):
        """Display system information and available endpoints."""
        logger.info("🎯 Biomedical Text Agent System Information")
        logger.info("=" * 50)
        
        logger.info(f"📋 Available endpoints:")
        logger.info(f"   • Frontend: http://localhost:{self.backend_port}")
        logger.info(f"   • API Base: http://localhost:{self.backend_port}/api/v1")
        logger.info(f"   • Dashboard: http://localhost:{self.backend_port}/dashboard")
        logger.info(f"   • Documents: http://localhost:{self.backend_port}/documents")
        logger.info(f"   • Agents: http://localhost:{self.backend_port}/agents")
        logger.info(f"   • Metadata: http://localhost:{self.backend_port}/metadata")
        logger.info(f"   • Validation: http://localhost:{self.backend_port}/validation")
        logger.info(f"   • Database: http://localhost:{self.backend_port}/database")
        logger.info(f"   • Configuration: http://localhost:{self.backend_port}/config")
        logger.info(f"   • Ontologies: http://localhost:{self.backend_port}/ontologies")
        logger.info(f"   • Prompts: http://localhost:{self.backend_port}/prompts")
        logger.info(f"   • Analytics: http://localhost:{self.backend_port}/analytics")
        logger.info(f"   • API Docs: http://localhost:{self.backend_port}/api/docs")
        
        logger.info("\n💡 System Features:")
        logger.info("   • Unified PubMed Client (enhanced features when available)")
        logger.info("   • Unified HPO Manager (optimized performance when available)")
        logger.info("   • Unified Extraction Orchestrator (RAG integration when available)")
        logger.info("   • Unified Metadata Orchestrator (enhanced pipeline when available)")
        logger.info("   • Automatic fallback to basic implementations when needed")
        
        logger.info("\n🛑 To stop the system, press Ctrl+C")
    
    def stop_system(self):
        """Stop the running system."""
        if self.backend_process:
            logger.info("🛑 Stopping backend server...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=10)
                logger.info("✅ Backend server stopped")
            except subprocess.TimeoutExpired:
                logger.warning("⚠️  Backend server didn't stop gracefully, forcing...")
                self.backend_process.kill()
                self.backend_process.wait()
                logger.info("✅ Backend server force stopped")
    
    async def run_system(self):
        """Run the complete system."""
        try:
            logger.info("🚀 Starting Biomedical Text Agent Unified System")
            logger.info("=" * 50)
            
            # Check requirements
            if not self.check_requirements():
                logger.error("❌ Requirements check failed. Please fix the issues above.")
                return False
            
            # Start backend
            if not self.start_backend():
                logger.error("❌ Failed to start backend server.")
                return False
            
            # Display system information
            self.display_system_info()
            
            # Monitor system health
            logger.info("\n🔍 Monitoring system health...")
            while True:
                health = self.check_system_health()
                if health.get("backend", {}).get("status") == "healthy":
                    logger.info("✅ System running normally")
                else:
                    logger.warning("⚠️  System health issues detected")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down...")
            return True
        except Exception as e:
            logger.error(f"❌ Fatal error in system: {e}")
            return False
        finally:
            self.stop_system()


def main():
    """Main entry point."""
    try:
        system_manager = SystemManager()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "check":
                # Just check requirements
                if system_manager.check_requirements():
                    logger.info("✅ All requirements met")
                    return 0
                else:
                    logger.error("❌ Requirements check failed")
                    return 1
            elif sys.argv[1] == "build":
                # Just build frontend
                if system_manager.build_frontend():
                    logger.info("✅ Frontend built successfully")
                    return 0
                else:
                    logger.error("❌ Frontend build failed")
                    return 1
            else:
                logger.error(f"Unknown command: {sys.argv[1]}")
                logger.info("Available commands: check, build")
                logger.info("No command specified: starts the full system")
                return 1
        
        # Default: run the complete system
        success = asyncio.run(system_manager.run_system())
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("🛑 System stopped by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
