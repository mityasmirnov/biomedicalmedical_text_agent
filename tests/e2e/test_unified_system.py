#!/usr/bin/env python3
"""
Test script for the unified Biomedical Text Agent system.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_unified_system():
    """Test the complete unified system."""
    print("🧪 Testing Unified Biomedical Text Agent System")
    print("=" * 60)
    
    try:
        # Test 1: API endpoints module loading
        print("1. Testing API endpoints module loading...")
        from api.endpoints import (
            metadata_triage_router,
            extraction_router,
            database_router,
            rag_router,
            user_router,
            dashboard_router,
            agents_router,
            documents_router,
            metadata_router
        )
        print("   ✅ API endpoints loaded successfully")
        
        # Test 2: API router creation
        print("2. Testing API router creation...")
        from api.main import create_api_router
        api_router = create_api_router()
        print("   ✅ API router created successfully")
        
        # Test 3: Unified orchestrator
        print("3. Testing unified orchestrator...")
        from core.unified_orchestrator import UnifiedOrchestrator
        orchestrator = UnifiedOrchestrator()
        print("   ✅ Orchestrator created successfully")
        
        # Test 4: Unified application
        print("4. Testing unified application...")
        from unified_app import create_unified_app
        app = create_unified_app()
        print("   ✅ Unified app created successfully")
        print(f"   📱 App title: {app.title}")
        print(f"   📱 App version: {app.version}")
        
        # Test 5: Check available routers
        print("5. Checking available API routers...")
        available_routers = [r for r in dir() if r.endswith("_router")]
        print(f"   📋 Available routers: {available_routers}")
        
        print("\n🎉 All tests passed! New unified system is ready.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_unified_system()
    sys.exit(0 if success else 1)
