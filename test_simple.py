#!/usr/bin/env python3
"""
Simple test script for core functionality.
"""

import sys
import os
from pathlib import Path

# Add src to Python path for imports
current_dir = Path(__file__).parent
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def test_hpo_manager():
    """Test HPO manager functionality."""
    print("Testing HPO Manager...")
    
    try:
        from ontologies.hpo_manager import HPOManager
        
        hpo = HPOManager()
        print("✅ HPO Manager initialized")
        
        # Test phenotype normalization
        test_phenotype = "developmental delay"
        result = hpo.normalize_phenotype(test_phenotype)
        
        if result.success:
            print(f"✅ HPO normalization works: '{test_phenotype}' -> {result.data}")
        else:
            print(f"❌ HPO normalization failed: {result.error}")
        
        return True
        
    except Exception as e:
        print(f"❌ HPO Manager test failed: {e}")
        return False

def test_gene_manager():
    """Test gene manager functionality."""
    print("\nTesting Gene Manager...")
    
    try:
        from ontologies.gene_manager import GeneManager
        
        gene = GeneManager()
        print("✅ Gene Manager initialized")
        
        # Test gene normalization
        test_gene = "SURF1"
        result = gene.normalize_gene_symbol(test_gene)
        
        if result.success:
            print(f"✅ Gene normalization works: '{test_gene}' -> {result.data}")
        else:
            print(f"❌ Gene normalization failed: {result.error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gene Manager test failed: {e}")
        return False

def test_configuration():
    """Test system configuration."""
    print("\nTesting Configuration...")
    
    try:
        from core.config import get_config
        
        config = get_config()
        print("✅ Configuration loaded")
        print(f"   LLM provider: {getattr(config.llm, 'provider', 'Unknown')}")
        print(f"   Database URL: {getattr(config.database, 'url', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Simple Biomedical System Test")
    print("=" * 40)
    
    results = []
    
    results.append(test_configuration())
    results.append(test_hpo_manager())
    results.append(test_gene_manager())
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    for i, result in enumerate(['Configuration', 'HPO Manager', 'Gene Manager']):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{result:15} {status}")
    
    print("-" * 40)
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed.")

if __name__ == "__main__":
    main()
