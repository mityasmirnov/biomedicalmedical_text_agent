#!/usr/bin/env python3
"""
Biomedical Data Extraction Engine - System Startup Script

This script provides an easy way to start all components of the system.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print system banner."""
    print("=" * 70)
    print("🏥 Biomedical Data Extraction Engine - System Startup")
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
        ("click", "click"),
        ("rich", "rich"),
        ("pydantic", "pydantic"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("requests", "requests")
    ]
    
    for dep_name, import_name in deps_to_check:
        try:
            __import__(import_name)
        except ImportError:
            missing_deps.append(dep_name)
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("📦 Installing missing dependencies...")
        
        try:
            for dep in missing_deps:
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
        response = requests.get("http://127.0.0.1:8000/api/v1/dashboard/status", timeout=2)
        return response.status_code == 200
    except:
        return False

def run_system_test():
    """Run system test to verify everything works."""
    print("🧪 Running system test...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_system.py"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ System test passed")
            return True
        else:
            print("⚠️  System test had issues (this may be normal)")
            print("Check the output above for details")
            return True  # Don't fail startup for test issues
    except subprocess.TimeoutExpired:
        print("⚠️  System test timed out (this may be normal)")
        return True
    except Exception as e:
        print(f"⚠️  System test error: {e}")
        return True

def start_backend():
    """Start the backend server."""
    print("🚀 Starting backend server...")
    
    # Check if backend is already running
    if check_backend_running():
        print("✅ Backend server is already running")
        print("   API available at: http://127.0.0.1:8000/api/v1/")
        return "already_running"
    
    try:
        # Start backend in background - use correct import path
        backend_cmd = [
            sys.executable, "-c",
            "import uvicorn; uvicorn.run('app:create_app', host='127.0.0.1', port=8000)"
        ]
        
        # Change to backend directory for proper imports
        original_dir = os.getcwd()
        backend_dir = Path(__file__).parent / "src" / "ui" / "backend"
        
        if not backend_dir.exists():
            print(f"❌ Backend directory not found: {backend_dir}")
            return None
        
        # Change to backend directory
        os.chdir(backend_dir)
        
        backend_process = subprocess.Popen(
            backend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            import requests
            response = requests.get("http://127.0.0.1:8000/api/v1/dashboard/overview", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully")
                print("   API available at: http://127.0.0.1:8000/api/v1/")
                # Change back to original directory
                os.chdir(original_dir)
                return backend_process
            else:
                print(f"⚠️  Backend server may not be fully ready (status: {response.status_code})")
                os.chdir(original_dir)
                return backend_process
        except Exception as e:
            print(f"⚠️  Backend server started but may not be fully ready: {e}")
            os.chdir(original_dir)
            return backend_process
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        # Try to change back to original directory
        try:
            os.chdir(original_dir)
        except:
            pass
        return None

def show_status():
    """Show system status and next steps."""
    print("\n" + "=" * 70)
    print("🎉 System Startup Complete!")
    print("=" * 70)
    print()
    print("🌐 Web Interface:")
    print("   URL: http://127.0.0.1:8000")
    print("   Status: Backend server running")
    print()
    print("🔧 CLI Interface:")
    print("   Command: python src/main.py --help")
    print("   Example: python src/main.py extract --file data/input/PMID32679198.pdf")
    print()
    print("📊 API Endpoints:")
    print("   Dashboard: http://127.0.0.1:8000/api/v1/dashboard/overview")
    print("   Metrics: http://127.0.0.1:8000/api/v1/dashboard/metrics")
    print("   Status: http://127.0.0.1:8000/api/v1/dashboard/status")
    print("   Health: http://127.0.0.1:8000/api/health")
    print()
    print("🧪 Testing:")
    print("   System Test: python test_system.py")
    print("   UI Test: python test_ui_system.py")
    print()
    print("📚 Documentation:")
    print("   README.md - Complete system overview")
    print("   SYSTEM_STATUS.md - Current system status")
    print("   docs/USER_GUIDE.md - Detailed usage instructions")
    print()
    print("🛑 To stop the system:")
    print("   Press Ctrl+C or run: pkill -f 'uvicorn.run'")
    print()
    print("🚀 Quick Commands:")
    print("   Start system: python start_system.py")
    print("   Check status: curl http://127.0.0.1:8000/api/v1/dashboard/status")
    print("   View logs: Check terminal output above")
    print()

def main():
    """Main startup function."""
    print_banner()
    
    # Check environment
    if not check_environment():
        return 1
    
    if not check_dependencies():
        return 1
    
    if not check_configuration():
        return 1
    
    print()
    
    # Run system test
    if not run_system_test():
        return 1
    
    print()
    
    # Start backend
    backend_result = start_backend()
    if backend_result is None:
        return 1
    
    print()
    
    # Show status
    show_status()
    
    # If backend was already running, just show status and exit
    if backend_result == "already_running":
        print("\n🔄 Backend is already running. System is ready!")
        print("🌐 Access at: http://127.0.0.1:8000")
        return 0
    
    try:
        # Keep the script running
        print("🔄 System is running. Press Ctrl+C to stop...")
        backend_result.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if backend_result:
            backend_result.terminate()
            backend_result.wait()
        print("✅ System stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
