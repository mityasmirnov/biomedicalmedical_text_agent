#!/usr/bin/env python3
"""
Biomedical Text Agent - Unified System Startup Script

This script starts the unified system that connects all components:
- Metadata triage and document retrieval
- Document processing and extraction
- Data storage and retrieval
- RAG system and question answering
- Web UI
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print system banner."""
    print("=" * 70)
    print("🏥 Biomedical Text Agent - Unified System Startup")
    print("=" * 70)
    print()

def check_environment():
    """Check if virtual environment is activated."""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("❌ Virtual environment not detected!")
        print("Please activate the virtual environment first:")
        print("  source venv/bin/activate  # On Unix/Mac")
        print("  venv\\Scripts\\activate     # On Windows")
        print()
        return False
    
    print("✅ Virtual environment detected")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    missing_deps = []
    
    # Check core dependencies
    deps_to_check = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("requests", "requests"),
        ("sqlite3", "sqlite3"),
        ("pathlib", "pathlib")
    ]
    
    for dep_name, import_name in deps_to_check:
        try:
            if import_name == "sqlite3":
                import sqlite3
            elif import_name == "pathlib":
                from pathlib import Path
            else:
                __import__(import_name)
        except ImportError:
            missing_deps.append(dep_name)
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("📦 Installing missing dependencies...")
        
        try:
            for dep in missing_deps:
                if dep == "sqlite3":
                    print("sqlite3 is built into Python")
                    continue
                subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], check=True, capture_output=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("Please install manually: pip install -r requirements.txt")
            return False
    
    print("✅ Core dependencies available")
    return True

def check_configuration():
    """Check if environment is configured."""
    print("🔍 Checking configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please copy env.example to .env and configure your API keys")
        return False
    
    # Check for required API key
    with open(env_file, 'r') as f:
        content = f.read()
        if "OPENROUTER_API_KEY=your_openrouter_api_key_here" in content:
            print("❌ Please configure your OPENROUTER_API_KEY in .env file")
            return False
    
    print("✅ Configuration looks good")
    return True

def check_backend_running():
    """Check if backend is already running."""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_unified_system():
    """Start the unified system."""
    print("🚀 Starting Unified Biomedical Text Agent System...")
    
    try:
        # Change to src directory
        src_dir = Path("src")
        if not src_dir.exists():
            print("❌ src directory not found!")
            return False
        
        os.chdir(src_dir)
        
        # Start the unified application
        print("📡 Starting unified FastAPI application...")
        subprocess.run([
            sys.executable, "unified_app.py"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start unified system: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def main():
    """Main startup function."""
    print_banner()
    
    # Check environment
    if not check_environment():
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check configuration
    if not check_configuration():
        return False
    
    # Check if already running
    if check_backend_running():
        print("✅ Backend is already running at http://127.0.0.1:8000")
        print("🌐 Access the system at: http://127.0.0.1:8000")
        return True
    
    # Start the system
    print("\n🚀 Starting Unified Biomedical Text Agent System...")
    print("=" * 60)
    
    if start_unified_system():
        print("\n✅ Unified system started successfully!")
        print("🌐 Access the system at: http://127.0.0.1:8000")
        print("📚 API documentation at: http://127.0.0.1:8000/api/docs")
        print("🔍 System status at: http://127.0.0.1:8000/api/health")
        return True
    else:
        print("\n❌ Failed to start unified system")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error during startup: {e}")
        sys.exit(1)