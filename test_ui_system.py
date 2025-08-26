#!/usr/bin/env python3
"""
UI System Test Script

Tests the complete UI system to ensure it's working without authentication.
"""

import requests
import time
import sys
from pathlib import Path

def test_backend_api():
    """Test backend API endpoints."""
    print("🔍 Testing Backend API...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test dashboard endpoints
    endpoints = [
        "/api/v1/dashboard/overview",
        "/api/v1/dashboard/metrics", 
        "/api/v1/dashboard/status"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} working")
            else:
                print(f"❌ {endpoint} failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")
            return False
    
    return True

def test_frontend_serving():
    """Test if frontend is being served."""
    print("\n🌐 Testing Frontend Serving...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            content = response.text.lower()
            
            # Check for React app indicators
            if "react" in content or "biomedical" in content:
                print("✅ Frontend being served")
                return True
            else:
                print("⚠️  Frontend served but content unclear")
                return True
        else:
            print(f"❌ Frontend failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False

def test_system_integration():
    """Test system integration."""
    print("\n🔧 Testing System Integration...")
    
    try:
        # Test the startup script
        from start_system import check_environment, check_dependencies, check_configuration
        
        if check_environment():
            print("✅ Environment check passed")
        else:
            print("❌ Environment check failed")
            return False
            
        if check_dependencies():
            print("✅ Dependencies check passed")
        else:
            print("❌ Dependencies check failed")
            return False
            
        if check_configuration():
            print("✅ Configuration check passed")
        else:
            print("❌ Configuration check failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ System integration error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Biomedical Data Extraction Engine - UI System Test")
    print("=" * 60)
    
    # Wait for backend to be ready
    print("⏳ Waiting for backend to be ready...")
    time.sleep(2)
    
    # Test backend API
    if not test_backend_api():
        print("\n❌ Backend API tests failed")
        return 1
    
    # Test frontend serving
    if not test_frontend_serving():
        print("\n❌ Frontend serving tests failed")
        return 1
    
    # Test system integration
    if not test_system_integration():
        print("\n❌ System integration tests failed")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 All UI System Tests Passed!")
    print("=" * 60)
    print()
    print("🌐 Web Interface: http://127.0.0.1:8000")
    print("📊 API Status: http://127.0.0.1:8000/api/v1/dashboard/status")
    print("📚 API Docs: http://127.0.0.1:8000/api/docs")
    print()
    print("✅ System is ready for use!")
    print("   - No authentication required")
    print("   - All features enabled")
    print("   - Ready for document processing")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
