#!/usr/bin/env python3
"""
Test script for the enhanced metadata triage module.

This script tests the enhanced PubMed client and metadata orchestrator
to ensure they can search PubMed, retrieve metadata, and store results
in the database.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from metadata_triage.enhanced_metadata_orchestrator import EnhancedMetadataOrchestrator
from metadata_triage.pubmed_client2 import EnhancedPubMedClient, create_enhanced_pubmed_client


def test_enhanced_pubmed_client():
    """Test the enhanced PubMed client functionality."""
    print("Testing Enhanced PubMed Client...")
    
    try:
        # Create client
        client = create_enhanced_pubmed_client()
        print("✓ Enhanced PubMed client created successfully")
        
        # Test search functionality
        print("Testing search functionality...")
        pmids, web_env, query_key = client.search_articles("leigh syndrome case reports", max_results=10)
        
        if pmids:
            print(f"✓ Search successful, found {len(pmids)} PMIDs")
            print(f"  First few PMIDs: {pmids[:5]}")
        else:
            print("✗ Search failed - no PMIDs returned")
            return False
        
        # Test fetching summaries
        print("Testing summary fetching...")
        summaries = client.fetch_article_summaries(pmids=pmids[:5], batch_size=5)
        
        if summaries:
            print(f"✓ Summary fetching successful, got {len(summaries)} summaries")
            print(f"  Sample summary keys: {list(summaries[0].keys()) if summaries else 'None'}")
        else:
            print("✗ Summary fetching failed")
            return False
        
        # Test fetching abstracts
        print("Testing abstract fetching...")
        abstracts = client.fetch_abstracts(pmids[:5], batch_size=5)
        
        if abstracts:
            print(f"✓ Abstract fetching successful, got {len(abstracts)} abstracts")
            abstract_lengths = [len(abstract) for abstract in abstracts.values()]
            print(f"  Abstract lengths: {abstract_lengths}")
        else:
            print("✗ Abstract fetching failed")
            return False
        
        # Test creating enhanced articles
        print("Testing enhanced article creation...")
        articles = client.create_enhanced_article_objects(summaries, abstracts)
        
        if articles:
            print(f"✓ Article creation successful, created {len(articles)} articles")
            print(f"  Sample article fields: {list(articles[0].__dict__.keys()) if articles else 'None'}")
        else:
            print("✗ Article creation failed")
            return False
        
        # Test CSV export
        print("Testing CSV export...")
        output_file = "test_enhanced_pubmed_export.csv"
        client.save_to_csv(articles, output_file)
        
        if Path(output_file).exists():
            print(f"✓ CSV export successful: {output_file}")
            # Clean up
            Path(output_file).unlink()
        else:
            print("✗ CSV export failed")
            return False
        
        # Test statistics
        print("Testing statistics generation...")
        stats = client.get_statistics(articles)
        
        if stats:
            print(f"✓ Statistics generation successful")
            print(f"  Total articles: {stats.get('total_articles', 'N/A')}")
            print(f"  Abstract rate: {stats.get('abstract_rate', 'N/A'):.2%}")
        else:
            print("✗ Statistics generation failed")
            return False
        
        print("✓ All Enhanced PubMed Client tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced PubMed Client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enhanced_metadata_orchestrator():
    """Test the enhanced metadata orchestrator functionality."""
    print("\nTesting Enhanced Metadata Orchestrator...")
    
    try:
        # Create orchestrator
        orchestrator = EnhancedMetadataOrchestrator(
            db_path="data/database/test_metadata.db"
        )
        print("✓ Enhanced metadata orchestrator created successfully")
        
        # Test database initialization
        print("Testing database initialization...")
        if orchestrator.db_path.exists():
            print("✓ Database file created successfully")
        else:
            print("✗ Database file not created")
            return False
        
        # Test search and store functionality
        print("Testing search and store functionality...")
        result = orchestrator.search_and_store_pubmed_metadata(
            query="leigh syndrome case reports",
            max_results=5,
            save_to_csv=True,
            output_dir="data/metadata_triage/test"
        )
        
        if result['success']:
            print(f"✓ Search and store successful")
            print(f"  Articles found: {result['articles_found']}")
            print(f"  Articles stored: {result['articles_stored']}")
            print(f"  CSV path: {result['csv_path']}")
        else:
            print(f"✗ Search and store failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test retrieving stored articles
        print("Testing article retrieval...")
        stored_articles = orchestrator.get_stored_articles(limit=10)
        
        if stored_articles:
            print(f"✓ Article retrieval successful, got {len(stored_articles)} articles")
            print(f"  Sample article PMID: {stored_articles[0].get('pmid', 'N/A')}")
        else:
            print("✗ Article retrieval failed")
            return False
        
        # Test statistics
        print("Testing orchestrator statistics...")
        stats = orchestrator.get_search_statistics()
        
        if stats:
            print(f"✓ Statistics retrieval successful")
            print(f"  Total articles: {stats.get('total_articles', 'N/A')}")
            print(f"  Recent searches: {len(stats.get('recent_searches', []))}")
        else:
            print("✗ Statistics retrieval failed")
            return False
        
        print("✓ All Enhanced Metadata Orchestrator tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced Metadata Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_leigh_syndrome_search():
    """Test the specific Leigh syndrome search functionality."""
    print("\nTesting Leigh Syndrome Search...")
    
    try:
        # Test the enhanced function
        from metadata_triage.pubmed_client2 import fetch_leigh_syndrome_articles_enhanced
        
        articles = fetch_leigh_syndrome_articles_enhanced(
            output_path="data/metadata_triage/leigh_syndrome_test.csv",
            db_path="data/database/test_metadata.db"
        )
        
        if articles:
            print(f"✓ Leigh syndrome search successful, found {len(articles)} articles")
            
            # Check if CSV was created
            csv_path = Path("data/metadata_triage/leigh_syndrome_test.csv")
            if csv_path.exists():
                print(f"✓ CSV file created: {csv_path}")
                print(f"  File size: {csv_path.stat().st_size} bytes")
            else:
                print("✗ CSV file not created")
                return False
        else:
            print("✗ Leigh syndrome search failed - no articles returned")
            return False
        
        print("✓ Leigh Syndrome Search test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Leigh Syndrome Search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Enhanced Metadata Triage Module Test Suite")
    print("=" * 50)
    
    # Create necessary directories
    Path("data/metadata_triage").mkdir(parents=True, exist_ok=True)
    Path("data/database").mkdir(parents=True, exist_ok=True)
    
    # Run tests
    tests = [
        ("Enhanced PubMed Client", test_enhanced_pubmed_client),
        ("Enhanced Metadata Orchestrator", test_enhanced_metadata_orchestrator),
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
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The enhanced metadata triage module is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
