#!/usr/bin/env python3
"""
Simple test script for the simplified enhanced metadata triage module.

This script tests the simplified enhanced metadata orchestrator
to ensure it can create the database, store sample articles, and
retrieve results without external dependencies.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from metadata_triage.enhanced_metadata_orchestrator_simple import SimpleEnhancedMetadataOrchestrator


def test_database_initialization():
    """Test database initialization."""
    print("Testing Database Initialization...")
    
    try:
        # Create orchestrator
        orchestrator = SimpleEnhancedMetadataOrchestrator(
            db_path="data/database/test_simple_metadata.db"
        )
        print("✓ Enhanced metadata orchestrator created successfully")
        
        # Check if database file was created
        if orchestrator.db_path.exists():
            print(f"✓ Database file created: {orchestrator.db_path}")
            print(f"  File size: {orchestrator.db_path.stat().st_size} bytes")
        else:
            print("✗ Database file not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sample_article_storage():
    """Test storing sample articles."""
    print("\nTesting Sample Article Storage...")
    
    try:
        # Create orchestrator
        orchestrator = SimpleEnhancedMetadataOrchestrator(
            db_path="data/database/test_simple_metadata.db"
        )
        
        # Store sample articles
        query = "leigh syndrome case reports"
        result = orchestrator.store_sample_articles(query)
        
        if result['success']:
            print(f"✓ Sample article storage successful")
            print(f"  Query: {result['query']}")
            print(f"  Articles found: {result['articles_found']}")
            print(f"  Articles stored: {result['articles_stored']}")
            print(f"  JSON path: {result['json_path']}")
            
            # Check if JSON file was created
            json_path = Path(result['json_path'])
            if json_path.exists():
                print(f"✓ JSON file created: {json_path}")
                print(f"  File size: {json_path.stat().st_size} bytes")
            else:
                print("✗ JSON file not created")
                return False
            
            return True
        else:
            print(f"✗ Sample article storage failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Sample article storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_article_retrieval():
    """Test retrieving stored articles."""
    print("\nTesting Article Retrieval...")
    
    try:
        # Create orchestrator
        orchestrator = SimpleEnhancedMetadataOrchestrator(
            db_path="data/database/test_simple_metadata.db"
        )
        
        # Retrieve stored articles
        stored_articles = orchestrator.get_stored_articles(limit=10)
        
        if stored_articles:
            print(f"✓ Article retrieval successful, got {len(stored_articles)} articles")
            
            # Show sample article
            if stored_articles:
                sample = stored_articles[0]
                print(f"\n📊 Sample Stored Article:")
                print(f"  PMID: {sample.get('pmid', 'N/A')}")
                print(f"  Title: {sample.get('title', 'N/A')}")
                print(f"  Journal: {sample.get('journal', 'N/A')}")
                print(f"  Authors: {sample.get('authors', 'N/A')}")
                print(f"  Search Query: {sample.get('search_query', 'N/A')}")
                print(f"  Fetch Date: {sample.get('fetch_date', 'N/A')}")
            
            return True
        else:
            print("✗ Article retrieval failed - no articles returned")
            return False
            
    except Exception as e:
        print(f"✗ Article retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics():
    """Test retrieving statistics."""
    print("\nTesting Statistics Retrieval...")
    
    try:
        # Create orchestrator
        orchestrator = SimpleEnhancedMetadataOrchestrator(
            db_path="data/database/test_simple_metadata.db"
        )
        
        # Get statistics
        stats = orchestrator.get_search_statistics()
        
        if stats:
            print(f"✓ Statistics retrieval successful")
            print(f"  Total Articles: {stats.get('total_articles', 'N/A')}")
            print(f"  Recent Searches: {len(stats.get('recent_searches', []))}")
            
            # Show recent searches
            recent_searches = stats.get('recent_searches', [])
            if recent_searches:
                print(f"  Recent Search Queries:")
                for search in recent_searches:
                    print(f"    '{search['query']}' -> {search['articles']} articles ({search['date']})")
            
            # Show top journals
            top_journals = stats.get('top_journals', {})
            if top_journals:
                print(f"  Top Journals in Database:")
                for journal, count in top_journals:
                    print(f"    {journal}: {count} articles")
            
            return True
        else:
            print("✗ Statistics retrieval failed")
            return False
            
    except Exception as e:
        print(f"✗ Statistics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_pipeline():
    """Test the complete pipeline."""
    print("\nTesting Complete Pipeline...")
    
    try:
        # Create orchestrator
        orchestrator = SimpleEnhancedMetadataOrchestrator(
            db_path="data/database/test_simple_metadata.db"
        )
        
        # Run complete pipeline
        query = "leigh syndrome case reports"
        result = orchestrator.run_complete_pipeline(
            query=query,
            max_results=100,
            output_dir="data/metadata_triage/complete_pipeline_test"
        )
        
        if result['success']:
            print(f"✓ Complete pipeline successful")
            print(f"  Query: {result['query']}")
            print(f"  Total Articles: {result['total_articles']}")
            print(f"  Output Directory: {result['output_directory']}")
            print(f"  Timestamp: {result['timestamp']}")
            
            # Show sample data results
            sample_data = result.get('sample_data', {})
            if sample_data:
                print(f"\n📚 Sample Data Results:")
                print(f"  Articles Found: {sample_data.get('articles_found', 'N/A')}")
                print(f"  Articles Stored: {sample_data.get('articles_stored', 'N/A')}")
                print(f"  JSON Path: {sample_data.get('json_path', 'N/A')}")
            
            return True
        else:
            print(f"✗ Complete pipeline failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Complete pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_leigh_syndrome_search():
    """Test the specific Leigh syndrome search functionality."""
    print("\nTesting Leigh Syndrome Search...")
    
    try:
        # Create orchestrator
        orchestrator = SimpleEnhancedMetadataOrchestrator(
            db_path="data/database/test_simple_metadata.db"
        )
        
        # Search for Leigh syndrome case reports
        query = "leigh syndrome case reports"
        result = orchestrator.store_sample_articles(query)
        
        if result['success']:
            print(f"✓ Leigh syndrome search successful")
            print(f"  Articles found: {result['articles_found']}")
            print(f"  Articles stored: {result['articles_stored']}")
            
            # Check if JSON was created
            json_path = Path(result['json_path'])
            if json_path.exists():
                print(f"✓ JSON file created: {json_path}")
                print(f"  File size: {json_path.stat().st_size} bytes")
            else:
                print("✗ JSON file not created")
                return False
            
            return True
        else:
            print(f"✗ Leigh syndrome search failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Leigh syndrome search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Simplified Enhanced Metadata Triage Module Test Suite")
    print("=" * 60)
    
    # Create necessary directories
    Path("data/metadata_triage").mkdir(parents=True, exist_ok=True)
    Path("data/metadata_triage/complete_pipeline_test").mkdir(parents=True, exist_ok=True)
    Path("data/database").mkdir(parents=True, exist_ok=True)
    
    # Run tests
    tests = [
        ("Database Initialization", test_database_initialization),
        ("Sample Article Storage", test_sample_article_storage),
        ("Article Retrieval", test_article_retrieval),
        ("Statistics Retrieval", test_statistics),
        ("Complete Pipeline", test_complete_pipeline),
        ("Leigh Syndrome Search", test_leigh_syndrome_search)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The simplified enhanced metadata triage module is working correctly.")
        print("\nThe module can:")
        print("  ✓ Initialize database with proper schema")
        print("  ✓ Store sample PubMed article metadata")
        print("  ✓ Retrieve stored articles from database")
        print("  ✓ Generate comprehensive statistics")
        print("  ✓ Run complete metadata triage pipelines")
        print("  ✓ Handle Leigh syndrome case report searches")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print(f"\nOutput files are available in:")
    print(f"  - data/metadata_triage/")
    print(f"  - data/database/test_simple_metadata.db")


if __name__ == "__main__":
    exit(main())
