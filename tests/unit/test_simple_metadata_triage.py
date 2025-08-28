#!/usr/bin/env python3
"""
Test suite for the unified metadata orchestrator.

This module tests the unified metadata orchestrator functionality
that automatically uses the best available implementation.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from metadata_triage.metadata_orchestrator import UnifiedMetadataOrchestrator


async def test_orchestrator_initialization():
    """Test orchestrator initialization."""
    print("Testing Unified Metadata Orchestrator Initialization...")
    
    try:
        # Create orchestrator
        orchestrator = UnifiedMetadataOrchestrator(
            llm_client=None,  # No LLM client for testing
            use_enhanced=True  # Use enhanced implementation if available
        )
        print("✓ Unified metadata orchestrator created successfully")
        
        # Check if enhanced mode is available
        if orchestrator.use_enhanced:
            print("✓ Enhanced mode available")
        else:
            print("✓ Basic mode (enhanced not available)")
        
        return True
        
    except Exception as e:
        print(f"✗ Orchestrator initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_pipeline_execution():
    """Test pipeline execution."""
    print("\nTesting Pipeline Execution...")
    
    try:
        # Create orchestrator
        orchestrator = UnifiedMetadataOrchestrator(
            llm_client=None,  # No LLM client for testing
            use_enhanced=True  # Use enhanced implementation if available
        )
        
        # Run pipeline
        query = "test query"
        result = await orchestrator.run_complete_pipeline(
            query=query,
            max_results=10,
            include_europepmc=False,  # Skip Europe PMC for testing
            output_dir="data/metadata_triage/test_pipeline",
            save_intermediate=False
        )
        
        if result:
            print(f"✓ Pipeline execution successful")
            print(f"  Query: {query}")
            print(f"  Output directory: {result.get('output_directory', 'N/A')}")
            
            if result.get('enhanced_mode'):
                print("  Mode: Enhanced")
            else:
                print("  Mode: Standard")
            
            return True
        else:
            print("✗ Pipeline execution failed")
            return False
            
    except Exception as e:
        print(f"✗ Pipeline execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_enhanced_features():
    """Test enhanced features availability."""
    print("\nTesting Enhanced Features...")
    
    try:
        # Create orchestrator
        orchestrator = UnifiedMetadataOrchestrator(
            llm_client=None,  # No LLM client for testing
            use_enhanced=True  # Use enhanced implementation if available
        )
        
        # Check enhanced features
        if hasattr(orchestrator, 'orchestrator'):
            print(f"✓ Orchestrator type: {type(orchestrator.orchestrator).__name__}")
            
            if orchestrator.use_enhanced:
                print("✓ Enhanced features available")
            else:
                print("✓ Basic features (enhanced not available)")
            
            return True
        else:
            print("✗ Orchestrator structure not as expected")
            return False
            
    except Exception as e:
        print(f"✗ Enhanced features test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("🧪 Unified Metadata Orchestrator Test Suite")
    print("=" * 50)
    
    tests = [
        test_orchestrator_initialization,
        test_pipeline_execution,
        test_enhanced_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n🛑 Tests stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)