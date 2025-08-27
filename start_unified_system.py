#!/usr/bin/env python3
"""
Unified Startup Script for Biomedical Text Agent

This script starts the unified Biomedical Text Agent system that consolidates
all functionality into a single FastAPI application.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from unified_app import run_unified_server

def main():
    """Main startup function."""
    print("🚀 Starting Biomedical Text Agent - Unified System")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not (Path.cwd() / "src").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Current directory:", Path.cwd())
        print("   Expected to find 'src' directory here")
        sys.exit(1)
    
    # Check if virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected")
        print("   Consider activating your virtual environment first")
        print("   source venv/bin/activate  # or equivalent")
    
    # Check if required directories exist
    required_dirs = ["src", "data", "docs"]
    missing_dirs = [d for d in required_dirs if not Path(d).exists()]
    if missing_dirs:
        print(f"⚠️  Warning: Missing directories: {missing_dirs}")
    
    # Check if frontend is built
    frontend_build = Path("src/ui/frontend/build")
    if not frontend_build.exists():
        print("⚠️  Warning: Frontend not built")
        print("   To build frontend: cd src/ui/frontend && npm run build")
        print("   System will start with API only")
    else:
        print("✅ Frontend build found")
    
    print("\n📋 System Components:")
    print("   • Unified FastAPI Application")
    print("   • Consolidated API Endpoints")
    print("   • Database Management")
    print("   • Metadata Triage System")
    print("   • LangExtract Integration")
    print("   • RAG System")
    print("   • Frontend")
    
    print("\n🔧 Starting unified system...")
    print("   API Documentation: http://127.0.0.1:8000/api/docs")
    print("   Frontend: http://127.0.0.1:8000/")
    print("   Health Check: http://127.0.0.1:8000/api/health")
    print("   System Status: http://127.0.0.1:8000/api/v1/system/status")
    
    print("\n" + "=" * 60)
    
    try:
        # Start the unified server
        run_unified_server(
            host="127.0.0.1",
            port=8000,
            reload=False  # Set to True for development
        )
    except KeyboardInterrupt:
        print("\n\n🛑 System stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start system: {e}")
        logging.error(f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()