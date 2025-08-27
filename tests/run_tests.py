#!/usr/bin/env python3
"""
Test runner for Biomedical Text Agent.

This script runs all tests in the proper order:
1. Unit tests
2. Integration tests  
3. End-to-end tests
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all tests in the proper order."""
    test_dir = Path(__file__).parent
    
    print("🧪 Running Biomedical Text Agent Test Suite")
    print("=" * 50)
    
    # Run unit tests first
    print("\n📋 Running Unit Tests...")
    result1 = subprocess.run([
        sys.executable, "-m", "pytest", 
        str(test_dir / "unit"), 
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    if result1.returncode == 0:
        print("✅ Unit tests passed")
    else:
        print("❌ Unit tests failed")
        print(result1.stdout)
        print(result1.stderr)
    
    # Run integration tests
    print("\n📋 Running Integration Tests...")
    result2 = subprocess.run([
        sys.executable, "-m", "pytest", 
        str(test_dir / "integration"), 
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    if result2.returncode == 0:
        print("✅ Integration tests passed")
    else:
        print("❌ Integration tests failed")
        print(result2.stdout)
        print(result2.stderr)
    
    # Run e2e tests
    print("\n📋 Running End-to-End Tests...")
    result3 = subprocess.run([
        sys.executable, "-m", "pytest", 
        str(test_dir / "e2e"), 
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    if result3.returncode == 0:
        print("✅ E2E tests passed")
    else:
        print("❌ E2E tests failed")
        print(result3.stdout)
        print(result3.stderr)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Unit Tests: {'✅ PASSED' if result1.returncode == 0 else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if result2.returncode == 0 else '❌ FAILED'}")
    print(f"E2E Tests: {'✅ PASSED' if result3.returncode == 0 else '❌ FAILED'}")
    
    overall_success = all(r.returncode == 0 for r in [result1, result2, result3])
    print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if overall_success else '💥 SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
