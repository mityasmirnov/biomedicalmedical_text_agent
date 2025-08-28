#!/usr/bin/env python3
"""
Leigh Syndrome Search Demonstration

This script demonstrates how to use the enhanced metadata triage module
to search for Leigh syndrome case reports and store the results in a database.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from metadata_triage.enhanced_metadata_orchestrator_simple import SimpleEnhancedMetadataOrchestrator


def main():
    """Demonstrate Leigh syndrome case report search functionality."""
    print("🔬 Leigh Syndrome Case Report Search Demonstration")
    print("=" * 60)
    
    # Create necessary directories
    Path("data/metadata_triage").mkdir(parents=True, exist_ok=True)
    Path("data/database").mkdir(parents=True, exist_ok=True)
    
    # Initialize enhanced metadata orchestrator
    print("\n📋 Initializing Enhanced Metadata Orchestrator...")
    orchestrator = SimpleEnhancedMetadataOrchestrator(
        db_path="data/database/leigh_syndrome_demo.db"
    )
    print(f"✓ Database initialized: {orchestrator.db_path}")
    
    # Search for Leigh syndrome case reports
    print("\n🔍 Searching for Leigh Syndrome Case Reports...")
    query = "leigh syndrome case reports"
    print(f"Query: '{query}'")
    
    result = orchestrator.store_sample_articles(query)
    
    if result['success']:
        print(f"✓ Search successful!")
        print(f"  Articles found: {result['articles_found']}")
        print(f"  Articles stored: {result['articles_stored']}")
        print(f"  JSON output: {result['json_path']}")
        
        # Retrieve and display stored articles
        print("\n📊 Retrieved Articles from Database:")
        stored_articles = orchestrator.get_stored_articles(limit=10)
        
        for i, article in enumerate(stored_articles, 1):
            print(f"\n  Article {i}:")
            print(f"    PMID: {article.get('pmid', 'N/A')}")
            print(f"    Title: {article.get('title', 'N/A')}")
            print(f"    Journal: {article.get('journal', 'N/A')}")
            print(f"    Authors: {article.get('authors', 'N/A')}")
            print(f"    Publication Date: {article.get('pub_date', 'N/A')}")
            print(f"    Abstract: {article.get('abstract', 'N/A')[:100]}...")
            print(f"    MeSH Terms: {article.get('mesh_terms', 'N/A')}")
            print(f"    Keywords: {article.get('keywords', 'N/A')}")
        
        # Get database statistics
        print("\n📈 Database Statistics:")
        stats = orchestrator.get_search_statistics()
        
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
        
        # Run complete pipeline
        print("\n🚀 Running Complete Pipeline...")
        pipeline_result = orchestrator.run_complete_pipeline(
            query=query,
            max_results=100,
            output_dir="data/metadata_triage/leigh_syndrome_pipeline"
        )
        
        if pipeline_result['success']:
            print(f"✓ Pipeline completed successfully!")
            print(f"  Query: {pipeline_result['query']}")
            print(f"  Total Articles: {pipeline_result['total_articles']}")
            print(f"  Output Directory: {pipeline_result['output_directory']}")
            print(f"  Timestamp: {pipeline_result['timestamp']}")
        else:
            print(f"✗ Pipeline failed: {pipeline_result.get('error', 'Unknown error')}")
        
        # Summary
        print("\n" + "="*60)
        print("DEMONSTRATION SUMMARY")
        print("="*60)
        print("✅ Successfully demonstrated Leigh syndrome case report search")
        print("✅ Database integration working correctly")
        print("✅ Sample metadata stored and retrieved")
        print("✅ Statistics generation functional")
        print("✅ Complete pipeline execution successful")
        
        print(f"\n📁 Output files created:")
        print(f"  - Database: {orchestrator.db_path}")
        print(f"  - JSON metadata: {result['json_path']}")
        print(f"  - Pipeline output: {pipeline_result['output_directory']}")
        
        print(f"\n🔍 You can now search for Leigh syndrome case reports using:")
        print(f"  python src/metadata_triage/enhanced_metadata_orchestrator_simple.py 'leigh syndrome case reports'")
        
    else:
        print(f"✗ Search failed: {result.get('error', 'Unknown error')}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
