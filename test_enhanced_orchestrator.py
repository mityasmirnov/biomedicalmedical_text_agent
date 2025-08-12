#!/usr/bin/env python3
"""
Test script for the enhanced orchestrator.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_enhanced_orchestrator():
    """Test the enhanced orchestrator."""
    print("🧪 Testing Enhanced Orchestrator...")
    
    try:
        from agents.orchestrator.enhanced_orchestrator import EnhancedExtractionOrchestrator
        
        # Create orchestrator
        orchestrator = EnhancedExtractionOrchestrator()
        print("✅ Enhanced orchestrator created successfully")
        
        # Get system status
        status = orchestrator.get_system_status()
        print(f"✅ System status retrieved: {status.system_health}")
        
        # Display status
        orchestrator.display_system_status()
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_commands():
    """Test CLI commands."""
    print("\n🧪 Testing CLI commands...")
    
    try:
        from agents.orchestrator.enhanced_orchestrator import cli
        
        # Test status command
        print("✅ CLI module imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    """Run tests."""
    print("🚀 Enhanced Orchestrator Test")
    print("=" * 50)
    
    tests = [
        test_enhanced_orchestrator,
        test_cli_commands
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced orchestrator is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
