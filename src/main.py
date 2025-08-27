#!/usr/bin/env python3
"""
Main CLI interface for Biomedical Text Agent.

This module provides a command-line interface for the unified Biomedical Text Agent system.
"""

import argparse
import sys
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from unified_app import run_unified_server

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Biomedical Text Agent - Unified System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start the unified system
  %(prog)s --port 8080       # Start on port 8080
  %(prog)s --host 0.0.0.0    # Bind to all interfaces
  %(prog)s --reload          # Enable auto-reload (development)
  %(prog)s --verbose         # Enable verbose logging
        """
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check system configuration and exit"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Check if we're in the right directory
    if not (Path.cwd() / "src").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Current directory:", Path.cwd())
        print("   Expected to find 'src' directory here")
        sys.exit(1)
    
    # System check
    if args.check:
        print("🔍 Checking system configuration...")
        
        # Check required directories
        required_dirs = ["src", "data", "docs"]
        missing_dirs = [d for d in required_dirs if not Path(d).exists()]
        
        if missing_dirs:
            print(f"❌ Missing directories: {missing_dirs}")
            sys.exit(1)
        else:
            print("✅ Required directories found")
        
        # Check frontend build
        frontend_build = Path("src/ui/frontend/build")
        if frontend_build.exists():
            print("✅ Frontend build found")
        else:
            print("⚠️  Frontend not built (will run API only)")
        
        # Check virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment active")
        else:
            print("⚠️  Virtual environment not detected")
        
        print("✅ System configuration check passed")
        return
    
    # Print startup information
    print("🚀 Biomedical Text Agent - Unified System")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Reload: {'Enabled' if args.reload else 'Disabled'}")
    print(f"Verbose: {'Enabled' if args.verbose else 'Disabled'}")
    print()
    
    print("📋 System Components:")
    print("   • Unified FastAPI Application")
    print("   • Consolidated API Endpoints")
    print("   • Database Management")
    print("   • Metadata Triage System")
    print("   • LangExtract Integration")
    print("   • RAG System")
    print("   • React Frontend (if built)")
    
    print("\n🔧 Starting unified system...")
    print(f"   API Documentation: http://{args.host}:{args.port}/api/docs")
    print(f"   Frontend: http://{args.host}:{args.port}/")
    print(f"   Health Check: http://{args.host}:{args.port}/api/health")
    print(f"   System Status: http://{args.host}:{args.port}/api/v1/system/status")
    
    print("\n" + "=" * 60)
    
    try:
        # Start the unified server
        run_unified_server(
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    except KeyboardInterrupt:
        print("\n\n🛑 System stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start system: {e}")
        logging.error(f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

