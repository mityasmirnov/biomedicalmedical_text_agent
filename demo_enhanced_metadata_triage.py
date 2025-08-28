#!/usr/bin/env python3
"""
Demonstration script for the enhanced metadata triage module.

This script demonstrates how to use the enhanced PubMed client and metadata orchestrator
to search PubMed, retrieve metadata, and store results in the database.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from metadata_triage.enhanced_metadata_orchestrator import EnhancedMetadataOrchestrator
from metadata_triage.pubmed_client2 import create_enhanced_pubmed_client


def demo_basic_search():
    """Demonstrate basic PubMed search functionality."""
    print("🔍 Basic PubMed Search Demo")
    print("=" * 40)
    
    # Create enhanced PubMed client
    client = create_enhanced_pubmed_client()
    
    # Search for Leigh syndrome case reports
    query = "leigh syndrome case reports"
    print(f"Searching PubMed for: '{query}'")
    
    try:
        # Search for articles
        pmids, web_env, query_key = client.search_articles(query, max_results=20)
        
        if pmids:
            print(f"✓ Found {len(pmids)} articles")
            print(f"  First 5 PMIDs: {pmids[:5]}")
            
            # Fetch summaries for first 5 articles
            print("\nFetching article summaries...")
            summaries = client.fetch_article_summaries(pmids=pmids[:5], batch_size=5)
            
            if summaries:
                print(f"✓ Retrieved {len(summaries)} summaries")
                
                # Show sample summary
                if summaries:
                    sample = summaries[0]
                    print(f"\n📄 Sample Article Summary:")
                    print(f"  PMID: {sample.get('pmid', 'N/A')}")
                    print(f"  Title: {sample.get('Title', 'N/A')[:100]}...")
                    print(f"  Journal: {sample.get('FullJournalName', 'N/A')}")
                    print(f"  Authors: {sample.get('AuthorList', ['N/A'])[:3]}")
                    print(f"  Publication Date: {sample.get('PubDate', 'N/A')}")
            
            # Fetch abstracts
            print("\nFetching article abstracts...")
            abstracts = client.fetch_abstracts(pmids[:5], batch_size=5)
            
            if abstracts:
                print(f"✓ Retrieved {len(abstracts)} abstracts")
                
                # Show sample abstract
                if abstracts:
                    sample_pmid = list(abstracts.keys())[0]
                    sample_abstract = abstracts[sample_pmid]
                    print(f"\n📝 Sample Abstract (PMID: {sample_pmid}):")
                    print(f"  {sample_abstract[:200]}...")
            
            # Create enhanced articles
            print("\nCreating enhanced article objects...")
            articles = client.create_enhanced_article_objects(summaries, abstracts)
            
            if articles:
                print(f"✓ Created {len(articles)} enhanced articles")
                
                # Show sample enhanced article
                if articles:
                    sample_article = articles[0]
                    print(f"\n🔬 Sample Enhanced Article:")
                    print(f"  PMID: {sample_article.pmid}")
                    print(f"  Title: {sample_article.title[:80]}...")
                    print(f"  Journal: {sample_article.journal}")
                    print(f"  Authors: {sample_article.authors[:80]}...")
                    print(f"  Abstract Length: {len(sample_article.abstract) if sample_article.abstract else 0} characters")
                    print(f"  Open Access: {sample_article.open_access}")
                    print(f"  Full Text Available: {sample_article.full_text_available}")
                    print(f"  Publication Year: {sample_article.publication_year}")
                    print(f"  MeSH Terms: {len(sample_article.mesh_terms)} terms")
                    print(f"  Keywords: {len(sample_article.keywords)} keywords")
            
            # Save to CSV
            print("\nSaving articles to CSV...")
            csv_path = "data/metadata_triage/leigh_syndrome_demo.csv"
            client.save_to_csv(articles, csv_path)
            print(f"✓ Saved to: {csv_path}")
            
            # Get statistics
            print("\nGenerating statistics...")
            stats = client.get_statistics(articles)
            print(f"✓ Statistics:")
            print(f"  Total Articles: {stats.get('total_articles', 'N/A')}")
            print(f"  Abstract Rate: {stats.get('abstract_rate', 'N/A'):.1%}")
            print(f"  PMC Rate: {stats.get('pmc_rate', 'N/A'):.1%}")
            print(f"  DOI Rate: {stats.get('doi_rate', 'N/A'):.1%}")
            
            if 'open_access_rate' in stats:
                print(f"  Open Access Rate: {stats.get('open_access_rate', 'N/A'):.1%}")
            
            # Show top journals
            top_journals = stats.get('top_journals', {})
            if top_journals:
                print(f"  Top Journals:")
                for journal, count in list(top_journals.items())[:3]:
                    print(f"    {journal}: {count} articles")
            
            return articles
            
        else:
            print("✗ No articles found")
            return []
            
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return []


def demo_database_integration():
    """Demonstrate database integration functionality."""
    print("\n🗄️ Database Integration Demo")
    print("=" * 40)
    
    # Create enhanced metadata orchestrator
    orchestrator = EnhancedMetadataOrchestrator(
        db_path="data/database/biomedical_data.db"
    )
    
    print("✓ Enhanced metadata orchestrator created")
    print(f"  Database path: {orchestrator.db_path}")
    
    try:
        # Search and store metadata
        query = "leigh syndrome case reports"
        print(f"\nSearching and storing metadata for: '{query}'")
        
        result = orchestrator.search_and_store_pubmed_metadata(
            query=query,
            max_results=15,
            save_to_csv=True,
            output_dir="data/metadata_triage/demo"
        )
        
        if result['success']:
            print(f"✓ Search and store successful")
            print(f"  Articles found: {result['articles_found']}")
            print(f"  Articles stored: {result['articles_stored']}")
            print(f"  CSV saved to: {result['csv_path']}")
            
            # Retrieve stored articles
            print("\nRetrieving stored articles from database...")
            stored_articles = orchestrator.get_stored_articles(limit=10)
            
            if stored_articles:
                print(f"✓ Retrieved {len(stored_articles)} articles from database")
                
                # Show sample stored article
                if stored_articles:
                    sample = stored_articles[0]
                    print(f"\n📊 Sample Stored Article:")
                    print(f"  PMID: {sample.get('pmid', 'N/A')}")
                    print(f"  Title: {sample.get('title', 'N/A')[:80]}...")
                    print(f"  Journal: {sample.get('journal', 'N/A')}")
                    print(f"  Authors: {sample.get('authors', 'N/A')[:80]}...")
                    print(f"  Search Query: {sample.get('search_query', 'N/A')}")
                    print(f"  Fetch Date: {sample.get('fetch_date', 'N/A')}")
            
            # Get database statistics
            print("\nRetrieving database statistics...")
            db_stats = orchestrator.get_search_statistics()
            
            if db_stats:
                print(f"✓ Database statistics:")
                print(f"  Total Articles: {db_stats.get('total_articles', 'N/A')}")
                print(f"  Recent Searches: {len(db_stats.get('recent_searches', []))}")
                
                # Show recent searches
                recent_searches = db_stats.get('recent_searches', [])
                if recent_searches:
                    print(f"  Recent Search Queries:")
                    for search in recent_searches[:3]:
                        print(f"    '{search['query']}' -> {search['articles']} articles ({search['date']})")
                
                # Show top journals
                top_journals = db_stats.get('top_journals', {})
                if top_journals:
                    print(f"  Top Journals in Database:")
                    for journal, count in list(top_journals.items())[:3]:
                        print(f"    {journal}: {count} articles")
            
            return True
            
        else:
            print(f"✗ Search and store failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Database integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_complete_pipeline():
    """Demonstrate the complete metadata triage pipeline."""
    print("\n🚀 Complete Pipeline Demo")
    print("=" * 40)
    
    # Create enhanced metadata orchestrator
    orchestrator = EnhancedMetadataOrchestrator(
        db_path="data/database/biomedical_data.db"
    )
    
    try:
        # Run complete pipeline
        query = "leigh syndrome case reports"
        print(f"Running complete pipeline for: '{query}'")
        
        result = orchestrator.run_complete_pipeline(
            query=query,
            max_results=20,
            include_europepmc=False,  # Skip Europe PMC for demo
            output_dir="data/metadata_triage/complete_pipeline",
            save_intermediate=True
        )
        
        if result['success']:
            print(f"✓ Pipeline completed successfully!")
            print(f"  Query: {result['query']}")
            print(f"  Total Articles: {result['total_articles']}")
            print(f"  Output Directory: {result['output_directory']}")
            print(f"  Timestamp: {result['timestamp']}")
            
            # Show PubMed results
            pubmed_result = result.get('pubmed', {})
            if pubmed_result:
                print(f"\n📚 PubMed Results:")
                print(f"  Articles Found: {pubmed_result.get('articles_found', 'N/A')}")
                print(f"  Articles Stored: {pubmed_result.get('articles_stored', 'N/A')}")
                print(f"  CSV Path: {pubmed_result.get('csv_path', 'N/A')}")
                
                # Show statistics
                stats = pubmed_result.get('statistics', {})
                if stats:
                    print(f"  Statistics:")
                    print(f"    Abstract Rate: {stats.get('abstract_rate', 'N/A'):.1%}")
                    print(f"    PMC Rate: {stats.get('pmc_rate', 'N/A'):.1%}")
                    print(f"    DOI Rate: {stats.get('doi_rate', 'N/A'):.1%}")
            
            return True
            
        else:
            print(f"✗ Pipeline failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Complete pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the demonstration."""
    print("Enhanced Metadata Triage Module Demonstration")
    print("=" * 60)
    
    # Create necessary directories
    Path("data/metadata_triage").mkdir(parents=True, exist_ok=True)
    Path("data/metadata_triage/demo").mkdir(parents=True, exist_ok=True)
    Path("data/metadata_triage/complete_pipeline").mkdir(parents=True, exist_ok=True)
    Path("data/database").mkdir(parents=True, exist_ok=True)
    
    # Run demonstrations
    demos = [
        ("Basic PubMed Search", demo_basic_search),
        ("Database Integration", demo_database_integration),
        ("Complete Pipeline", demo_complete_pipeline)
    ]
    
    results = []
    for demo_name, demo_func in demos:
        print(f"\n{'='*20} {demo_name} {'='*20}")
        try:
            result = demo_func()
            results.append((demo_name, result))
        except Exception as e:
            print(f"✗ {demo_name} demo crashed: {e}")
            results.append((demo_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("DEMONSTRATION SUMMARY")
    print("="*60)
    
    successful = 0
    total = len(results)
    
    for demo_name, result in results:
        status = "SUCCESSFUL" if result else "FAILED"
        print(f"{demo_name}: {status}")
        if result:
            successful += 1
    
    print(f"\nOverall: {successful}/{total} demonstrations successful")
    
    if successful == total:
        print("🎉 All demonstrations completed successfully!")
        print("\nThe enhanced metadata triage module is working correctly and can:")
        print("  ✓ Search PubMed with complex queries")
        print("  ✓ Retrieve comprehensive article metadata")
        print("  ✓ Store results in the database")
        print("  ✓ Export results to CSV")
        print("  ✓ Provide detailed statistics")
        print("  ✓ Run complete metadata triage pipelines")
    else:
        print("❌ Some demonstrations failed. Please check the errors above.")
    
    print(f"\nOutput files are available in:")
    print(f"  - data/metadata_triage/demo/")
    print(f"  - data/metadata_triage/complete_pipeline/")
    print(f"  - data/database/biomedical_data.db")


if __name__ == "__main__":
    main()
