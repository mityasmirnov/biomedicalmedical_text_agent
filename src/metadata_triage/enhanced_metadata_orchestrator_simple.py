"""
Simplified Enhanced Metadata Orchestrator

This module provides a simplified version of the enhanced metadata orchestrator
that uses only built-in Python modules for testing purposes.
"""

import json
import logging
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import argparse
import hashlib
import uuid


class SimpleEnhancedMetadataOrchestrator:
    """
    Simplified enhanced orchestrator for metadata triage with database integration.
    """
    
    def __init__(self, 
                 db_path: str = "data/database/biomedical_data.db"):
        """
        Initialize the simplified enhanced metadata orchestrator.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with PubMed metadata tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create pubmed_articles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pubmed_articles (
                        id TEXT PRIMARY KEY,
                        pmid TEXT UNIQUE NOT NULL,
                        title TEXT,
                        sort_title TEXT,
                        last_author TEXT,
                        journal TEXT,
                        authors TEXT,
                        pub_type TEXT,
                        pmc_link TEXT,
                        doi TEXT,
                        abstract TEXT,
                        pub_date TEXT,
                        mesh_terms TEXT,
                        keywords TEXT,
                        search_query TEXT,
                        source TEXT DEFAULT 'PubMed',
                        fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        classification_result TEXT,
                        concept_scores TEXT,
                        deduplication_status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create search_queries table for tracking
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS search_queries (
                        id TEXT PRIMARY KEY,
                        query_text TEXT NOT NULL,
                        max_results INTEGER,
                        total_found INTEGER,
                        articles_fetched INTEGER,
                        search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'completed',
                        metadata TEXT
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_pubmed_articles_pmid ON pubmed_articles(pmid)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_pubmed_articles_query ON pubmed_articles(search_query)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_pubmed_articles_journal ON pubmed_articles(journal)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_pubmed_articles_date ON pubmed_articles(pub_date)")
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def store_sample_articles(self, query: str) -> Dict[str, Any]:
        """
        Store sample articles in database for testing purposes.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with results summary
        """
        self.logger.info(f"Storing sample articles for query: {query}")
        
        # Generate search query ID
        query_id = str(uuid.uuid4())
        
        # Create sample articles
        sample_articles = [
            {
                'pmid': '12345678',
                'title': 'Sample Leigh Syndrome Case Report 1',
                'sort_title': 'Sample Leigh Syndrome Case Report 1',
                'last_author': 'Smith J',
                'journal': 'Journal of Medical Genetics',
                'authors': 'Johnson A, Smith J',
                'pub_type': 'Case Reports',
                'pmc_link': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC123456',
                'doi': '10.1000/sample.2023.001',
                'abstract': 'This is a sample abstract for Leigh syndrome case report 1.',
                'pub_date': '2023/01/15',
                'mesh_terms': ['Leigh Disease', 'Mitochondrial Diseases'],
                'keywords': ['Leigh syndrome', 'mitochondrial', 'case report'],
                'publication_year': 2023,
                'publication_month': 1,
                'publication_day': 15,
                'language': 'English',
                'country': 'United States',
                'open_access': True,
                'full_text_available': True
            },
            {
                'pmid': '87654321',
                'title': 'Sample Leigh Syndrome Case Report 2',
                'sort_title': 'Sample Leigh Syndrome Case Report 2',
                'last_author': 'Brown K',
                'journal': 'Neurology Case Reports',
                'authors': 'Davis M, Brown K',
                'pub_type': 'Case Reports',
                'pmc_link': None,
                'doi': '10.1000/sample.2023.002',
                'abstract': 'This is a sample abstract for Leigh syndrome case report 2.',
                'pub_date': '2023/02/20',
                'mesh_terms': ['Leigh Disease', 'Genetic Disorders'],
                'keywords': ['Leigh syndrome', 'genetic', 'case report'],
                'publication_year': 2023,
                'publication_month': 2,
                'publication_day': 20,
                'language': 'English',
                'country': 'United Kingdom',
                'open_access': False,
                'full_text_available': True
            }
        ]
        
        try:
            # Store in database
            stored_count = self._store_articles_in_database(sample_articles, query)
            
            # Record search query
            self._record_search_query(query_id, query, 100, len(sample_articles), stored_count)
            
            # Save to JSON (instead of CSV)
            output_path = Path("data/metadata_triage")
            output_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_query = query.replace(' ', '_').replace(':', '_').replace('/', '_')[:50]
            json_filename = f"pubmed_{safe_query}_{timestamp}.json"
            json_path = output_path / json_filename
            
            with open(json_path, 'w') as f:
                json.dump(sample_articles, f, indent=2)
            
            result = {
                'success': True,
                'query': query,
                'query_id': query_id,
                'articles_found': len(sample_articles),
                'articles_stored': stored_count,
                'json_path': str(json_path),
                'search_date': datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed {len(sample_articles)} sample articles for query: {query}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process query '{query}': {e}")
            self._record_search_query(query_id, query, 100, 0, 0, status='failed', error=str(e))
            return {
                'success': False,
                'query': query,
                'error': str(e)
            }
    
    def _store_articles_in_database(self, articles: List[Dict[str, Any]], query: str) -> int:
        """Store articles in the database."""
        stored_count = 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for article in articles:
                    # Generate unique ID
                    article_id = str(uuid.uuid4())
                    
                    # Prepare data for insertion
                    data = {
                        'id': article_id,
                        'pmid': article['pmid'],
                        'title': article['title'],
                        'sort_title': article['sort_title'],
                        'last_author': article['last_author'],
                        'journal': article['journal'],
                        'authors': article['authors'],
                        'pub_type': article['pub_type'],
                        'pmc_link': article['pmc_link'],
                        'doi': article['doi'],
                        'abstract': article['abstract'],
                        'pub_date': article['pub_date'],
                        'mesh_terms': '; '.join(article['mesh_terms']) if article['mesh_terms'] else '',
                        'keywords': '; '.join(article['keywords']) if article['keywords'] else '',
                        'search_query': query,
                        'fetch_date': datetime.now().isoformat()
                    }
                    
                    # Insert or update article
                    cursor.execute("""
                        INSERT OR REPLACE INTO pubmed_articles (
                            id, pmid, title, sort_title, last_author, journal, authors,
                            pub_type, pmc_link, doi, abstract, pub_date, mesh_terms,
                            keywords, search_query, fetch_date, updated_at
                        ) VALUES (
                            :id, :pmid, :title, :sort_title, :last_author, :journal, :authors,
                            :pub_type, :pmc_link, :doi, :abstract, :pub_date, :mesh_terms,
                            :keywords, :search_query, :fetch_date, CURRENT_TIMESTAMP
                        )
                    """, data)
                    
                    stored_count += 1
                
                conn.commit()
                self.logger.info(f"Stored {stored_count} articles in database")
                
        except Exception as e:
            self.logger.error(f"Failed to store articles in database: {e}")
            raise
        
        return stored_count
    
    def _record_search_query(self, query_id: str, query: str, max_results: int, 
                           total_found: int, articles_fetched: int, 
                           status: str = 'completed', error: str = None):
        """Record search query details in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                metadata = {
                    'error': error
                } if error else {}
                
                cursor.execute("""
                    INSERT INTO search_queries (
                        id, query_text, max_results, total_found, articles_fetched,
                        status, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (query_id, query, max_results, total_found, articles_fetched, 
                     status, json.dumps(metadata)))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to record search query: {e}")
    
    def get_stored_articles(self, 
                           query: Optional[str] = None,
                           limit: int = 100,
                           offset: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieve stored articles from database.
        
        Args:
            query: Filter by search query
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of article dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if query:
                    cursor.execute("""
                        SELECT * FROM pubmed_articles 
                        WHERE search_query LIKE ? 
                        ORDER BY fetch_date DESC 
                        LIMIT ? OFFSET ?
                    """, (f'%{query}%', limit, offset))
                else:
                    cursor.execute("""
                        SELECT * FROM pubmed_articles 
                        ORDER BY fetch_date DESC 
                        LIMIT ? OFFSET ?
                    """, (limit, offset))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve articles: {e}")
            return []
    
    def get_article_by_pmid(self, pmid: str) -> Optional[Dict[str, Any]]:
        """Get a specific article by PMID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM pubmed_articles WHERE pmid = ?
                """, (pmid,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve article {pmid}: {e}")
            return None
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about stored articles and searches."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total articles
                cursor.execute("SELECT COUNT(*) FROM pubmed_articles")
                total_articles = cursor.fetchone()[0]
                
                # Articles by journal
                cursor.execute("""
                    SELECT journal, COUNT(*) as count 
                    FROM pubmed_articles 
                    WHERE journal IS NOT NULL 
                    GROUP BY journal 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                top_journals = [{'journal': row[0], 'count': row[1]} for row in cursor.fetchall()]
                
                # Articles by year
                cursor.execute("""
                    SELECT substr(pub_date, 1, 4) as year, COUNT(*) as count
                    FROM pubmed_articles 
                    WHERE pub_date IS NOT NULL 
                    GROUP BY year 
                    ORDER BY year DESC
                """)
                articles_by_year = [{'year': row[0], 'count': row[1]} for row in cursor.fetchall()]
                
                # Recent searches
                cursor.execute("""
                    SELECT query_text, articles_fetched, search_date 
                    FROM search_queries 
                    ORDER BY search_date DESC 
                    LIMIT 5
                """)
                recent_searches = [{'query': row[0], 'articles': row[1], 'date': row[2]} 
                                 for row in cursor.fetchall()]
                
                return {
                    'total_articles': total_articles,
                    'top_journals': top_journals,
                    'articles_by_year': articles_by_year,
                    'recent_searches': recent_searches
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def run_complete_pipeline(self, 
                            query: str,
                            max_results: int = 1000,
                            output_dir: str = "data/metadata_triage") -> Dict[str, Any]:
        """
        Run the complete metadata triage pipeline with sample data.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            output_dir: Output directory for results
            
        Returns:
            Dictionary with pipeline results
        """
        self.logger.info(f"Starting complete metadata triage pipeline for query: {query}")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Step 1: Store sample articles
        self.logger.info("Step 1: Storing sample articles in database")
        result = self.store_sample_articles(query)
        
        if not result['success']:
            return {
                'success': False,
                'error': f"Sample article storage failed: {result.get('error', 'Unknown error')}"
            }
        
        # Compile results
        pipeline_result = {
            'success': True,
            'query': query,
            'timestamp': timestamp,
            'sample_data': result,
            'total_articles': result['articles_found'],
            'output_directory': str(output_path)
        }
        
        self.logger.info(f"Pipeline completed successfully. Total articles: {pipeline_result['total_articles']}")
        return pipeline_result


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Simplified Enhanced Metadata Triage Pipeline")
    parser.add_argument('query', help='Search query')
    parser.add_argument('--max-results', type=int, default=1000, help='Maximum results')
    parser.add_argument('--db-path', default='data/database/biomedical_data.db', help='Database path')
    parser.add_argument('--output-dir', default='data/metadata_triage', help='Output directory')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = SimpleEnhancedMetadataOrchestrator(
        db_path=args.db_path
    )
    
    # Run pipeline
    result = orchestrator.run_complete_pipeline(
        query=args.query,
        max_results=args.max_results,
        output_dir=args.output_dir
    )
    
    if result['success']:
        print(f"Pipeline completed successfully!")
        print(f"Total articles: {result['total_articles']}")
        print(f"Output directory: {result['output_directory']}")
    else:
        print(f"Pipeline failed: {result.get('error', 'Unknown error')}")
        exit(1)


if __name__ == "__main__":
    main()
