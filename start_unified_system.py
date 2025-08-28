#!/usr/bin/env python3
"""
Start script for the Biomedical Text Agent Unified System.

This script starts both the FastAPI backend and serves the React frontend.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Check if all requirements are met."""
    print("Checking requirements...")
    
    # Check if src directory exists
    if not Path("src").exists():
        print("❌ Error: src directory not found")
        print("Please run this script from the project root directory")
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected")
        print("Consider activating a virtual environment for better dependency management")
    
    # Check if frontend is built
    frontend_build_path = Path("src/ui/frontend/build")
    if not frontend_build_path.exists():
        print("⚠️  Warning: Frontend build not found")
        print("Building frontend...")
        try:
            # Change to frontend directory and build
            frontend_dir = Path("src/ui/frontend")
            if frontend_dir.exists():
                subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
                print("✅ Frontend built successfully")
            else:
                print("❌ Frontend directory not found")
                return False
        except subprocess.CalledProcessError as e:
            print(f"❌ Error building frontend: {e}")
            return False
        except FileNotFoundError:
            print("❌ npm not found. Please install Node.js and npm")
            return False
    else:
        print("✅ Frontend build found")
    
    return True

def start_backend():
    """Start the FastAPI backend server."""
    print("\nStarting backend server...")
    
    try:
        # Use the root-level standalone server
        backend_script = Path("standalone_server.py")
        if not backend_script.exists():
            print("❌ Error: Standalone server not found")
            return False
        
        print("✅ Starting standalone API server...")
        
        # Start the server in the background
        process = subprocess.Popen([
            sys.executable, str(backend_script)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Check if the process is still running
        if process.poll() is None:
            print("✅ Backend server started successfully")
            print("   API available at: http://localhost:8000/api/v1")
            print("   API documentation at: http://localhost:8000/api/docs")
            print("   Frontend available at: http://localhost:8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend server failed to start")
            print(f"stdout: {stdout.decode()}")
            print(f"stderr: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

def main():
    """Main function to start the unified system."""
    print("🚀 Starting Biomedical Text Agent Unified System")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend server.")
        sys.exit(1)
    
    print("\n🎉 System started successfully!")
    print("\n📋 Available endpoints:")
    print("   • Frontend: http://localhost:8000")
    print("   • API Base: http://localhost:8000/api/v1")
    print("   • Dashboard: http://localhost:8000/dashboard")
    print("   • Documents: http://localhost:8000/documents")
    print("   • Agents: http://localhost:8000/agents")
    print("   • Metadata: http://localhost:8000/metadata")
    print("   • Validation: http://localhost:8000/validation")
    print("   • Database: http://localhost:8000/database")
    print("   • Configuration: http://localhost:8000/config")
    print("   • Ontologies: http://localhost:8000/ontologies")
    print("   • Prompts: http://localhost:8000/prompts")
    print("   • Analytics: http://localhost:8000/analytics")
    print("   • API Docs: http://localhost:8000/api/docs")
    
    print("\n💡 To stop the system, press Ctrl+C")
    
    try:
        # Keep the main process running
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ System stopped")

if __name__ == "__main__":
    main()