#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test script for the Biomedical Data Extraction Engine.

This script can be run from the project root directory to test all system functionality.
"""

import asyncio
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing module imports...")
    
    try:
        from core.config import get_config
        print("Core config imported")
    except ImportError as e:
        print(f"Core config import failed: {e}")
        return False
    
    try:
        from core.logging_config import setup_logging, get_logger
        print("Logging config imported")
    except ImportError as e:
        print(f"Logging config import failed: {e}")
        return False
    
    try:
        from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
        print("Extraction orchestrator imported")
    except ImportError as e:
        print(f"Extraction orchestrator import failed: {e}")
        return False
    
    try:
        from database.sqlite_manager import SQLiteManager
        print("SQLite manager imported")
    except ImportError as e:
        print(f"SQLite manager import failed: {e}")
        return False
    
    try:
        from database.vector_manager import VectorManager
        print("Vector manager imported")
    except ImportError as e:
        print(f"Vector manager import failed: {e}")
        return False
    
    try:
        from rag.rag_system import RAGSystem
        print("RAG system imported")
    except ImportError as e:
        print(f"RAG system import failed: {e}")
        return False
    
    try:
        from ontologies.hpo_manager import HPOManager
        print("HPO manager imported")
    except ImportError as e:
        print(f"HPO manager import failed: {e}")
        return False
    
    try:
        from ontologies.gene_manager import GeneManager
        print("Gene manager imported")
    except ImportError as e:
        print(f"Gene manager import failed: {e}")
        return False
    
    try:
        from processors.pdf_parser import PDFParser
        print("PDF parser imported")
    except ImportError as e:
        print(f"PDF parser import failed: {e}")
        return False
    
    try:
        from processors.patient_segmenter import PatientSegmenter
        print("Patient segmenter imported")
    except ImportError as e:
        print(f"Patient segmenter import failed: {e}")
        return False
    
    try:
        from langextract_integration.extractor import LangExtractEngine
        print("LangExtract engine imported")
    except ImportError as e:
        print(f"LangExtract engine import failed: {e}")
        return False
    
    print("All core modules imported successfully")
    return True

def test_configuration():
    """Test system configuration."""
    print("\nTesting system configuration...")
    
    try:
        from core.config import get_config
        config = get_config()
        print("Configuration loaded")
        
        # Check key configuration values
        if hasattr(config, 'llm'):
            print(f"   LLM provider: {getattr(config.llm, 'provider', 'Unknown')}")
        if hasattr(config, 'database'):
            print(f"   Database URL: {getattr(config.database, 'url', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"Configuration test failed: {e}")
        return False

def test_database_connection():
    """Test database connectivity."""
    print("\nTesting database connection...")
    
    try:
        from database.sqlite_manager import SQLiteManager
        
        # Test database initialization
        db_manager = SQLiteManager()
        print("Database manager initialized")
        
        # Test basic operations
        stats = db_manager.get_statistics()
        if stats.success:
            print("Database statistics retrieved")
            print(f"   Total records: {stats.data.get('total_records', 0)}")
            print(f"   Total documents: {stats.data.get('total_documents', 0)}")
        else:
            print(f"Database statistics failed: {stats.error}")
        
        return True
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

def test_ontology_managers():
    """Test ontology managers."""
    print("\nTesting ontology managers...")
    
    try:
        # Test HPO manager
        from ontologies.hpo_manager import HPOManager
        hpo_manager = HPOManager()
        print("HPO manager initialized")
        
        # Test phenotype normalization
        test_phenotype = "developmental delay"
        result = hpo_manager.normalize_phenotype(test_phenotype)
        if result.success:
            print(f"HPO normalization works: '{test_phenotype}' -> {result.data}")
        else:
            print(f"HPO normalization failed: {result.error}")
        
        # Test gene manager
        from ontologies.gene_manager import GeneManager
        gene_manager = GeneManager()
        print("Gene manager initialized")
        
        # Test gene normalization
        test_gene = "SURF1"
        result = gene_manager.normalize_gene_symbol(test_gene)
        if result.success:
            print(f"Gene normalization works: '{test_gene}' -> {result.data}")
        else:
            print(f"Gene normalization failed: {result.error}")
        
        return True
    except Exception as e:
        print(f"Ontology test failed: {e}")
        return False

def test_processors():
    """Test document processors."""
    print("\nTesting document processors...")
    
    try:
        from processors.pdf_parser import PDFParser
        from processors.patient_segmenter import PatientSegmenter
        
        pdf_parser = PDFParser()
        print("PDF parser initialized")
        
        patient_segmenter = PatientSegmenter()
        print("Patient segmenter initialized")
        
        return True
    except Exception as e:
        print(f"Processors test failed: {e}")
        return False

def test_llm_client():
    """Test LLM client connectivity."""
    print("\nTesting LLM client...")
    
    try:
        from core.llm_client.openrouter_client import OpenRouterClient
        
        # Check if API key is available
        import os
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("No OpenRouter API key found (set OPENROUTER_API_KEY)")
            print("   LLM functionality will be limited")
            return False
        
        # Initialize client (don't make actual API call to avoid costs)
        client = OpenRouterClient()
        print("LLM client initialized")
        print(f"   API key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
        
        return True
    except Exception as e:
        print(f"LLM client test failed: {e}")
        return False

def test_rag_system():
    """Test RAG system initialization."""
    print("\nTesting RAG system...")
    
    try:
        from rag.rag_system import RAGSystem
        from database.vector_manager import VectorManager
        from database.sqlite_manager import SQLiteManager
        
        vector_manager = VectorManager()
        sqlite_manager = SQLiteManager()
        
        rag_system = RAGSystem(
            vector_manager=vector_manager,
            sqlite_manager=sqlite_manager
        )
        print("RAG system initialized")
        
        return True
    except Exception as e:
        print(f"RAG system test failed: {e}")
        return False

def test_langextract():
    """Test LangExtract integration."""
    print("\nTesting LangExtract integration...")
    
    try:
        from langextract_integration.extractor import LangExtractEngine
        
        # Check if LangExtract is available
        try:
            import langextract
            print("LangExtract package available")
        except ImportError:
            print("LangExtract package not installed")
            print("   Install with: pip install langextract")
            return False
        
        # Test initialization (without API key to avoid costs)
        try:
            engine = LangExtractEngine()
            print("LangExtract engine initialized")
            return True
        except Exception as e:
            if "API key" in str(e) or "OPENROUTER_API_KEY" in str(e):
                print("LangExtract engine requires API key")
                return False
            else:
                print(f"LangExtract engine initialization failed: {e}")
                return False
                
    except Exception as e:
        print(f"LangExtract test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoint availability."""
    print("\nTesting API endpoints...")
    
    try:
        from api.main import create_api_router
        
        router = create_api_router()
        print("API router created")
        
        # Check if key endpoints are available
        routes = [route.path for route in router.routes]
        print(f"   Available routes: {len(routes)}")
        
        # Check for key endpoint categories
        health_routes = [r for r in routes if 'health' in r]
        extraction_routes = [r for r in routes if 'extraction' in r]
        database_routes = [r for r in routes if 'database' in r]
        rag_routes = [r for r in routes if 'rag' in r]
        
        if health_routes:
            print("Health endpoints available")
        if extraction_routes:
            print("Extraction endpoints available")
        if database_routes:
            print("Database endpoints available")
        if rag_routes:
            print("RAG endpoints available")
        
        return True
    except Exception as e:
        print(f"API test failed: {e}")
        return False

def test_frontend():
    """Test frontend availability."""
    print("\nTesting frontend...")
    
    frontend_build = Path("src/ui/frontend/build")
    if frontend_build.exists():
        print("Frontend build found")
        
        # Check for key frontend files
        index_file = frontend_build / "index.html"
        static_dir = frontend_build / "static"
        
        if index_file.exists():
            print("Frontend index file found")
        else:
            print("Frontend index file missing")
        
        if static_dir.exists():
            print("Frontend static files found")
        else:
            print("Frontend static files missing")
        
        return True
    else:
        print("Frontend not built")
        print("   To build frontend: cd src/ui/frontend && npm run build")
        return False

def run_comprehensive_test():
    """Run all system tests."""
    print("Biomedical Data Extraction Engine - System Test")
    print("=" * 60)
    
    test_results = {}
    
    # Run all tests
    test_results['imports'] = test_imports()
    test_results['configuration'] = test_configuration()
    test_results['database'] = test_database_connection()
    test_results['ontologies'] = test_ontology_managers()
    test_results['processors'] = test_processors()
    test_results['llm_client'] = test_llm_client()
    test_results['rag_system'] = test_rag_system()
    test_results['langextract'] = test_langextract()
    test_results['api_endpoints'] = test_api_endpoints()
    test_results['frontend'] = test_frontend()
    
    # Generate summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} {status}")
    
    print("-" * 60)
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! System is ready to use.")
        return True
    elif passed >= total * 0.8:
        print("Most tests passed. System should work with some limitations.")
        return True
    else:
        print("Many tests failed. System may not function properly.")
        return False

def main():
    """Main test function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Biomedical Data Extraction Engine - System Test

Usage:
  python test_system.py          # Run all tests
  python test_system.py --help   # Show this help

This script tests all system components to ensure they are working correctly.
        """)
        return
    
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTesting failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
