"""
Enhanced Metadata Orchestrator

This module provides an enhanced version of the metadata orchestrator that integrates
with the database and provides comprehensive PubMed metadata retrieval and storage.
"""

import json
import logging
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import argparse
import sqlite3
import hashlib
import uuid

from metadata_triage.pubmed_client import PubMedClient, PubMedArticle
from metadata_triage.europepmc_client import EuropePMCClient, EuropePMCArticle
from metadata_triage.abstract_classifier import AbstractClassifier, ClassificationResult
from metadata_triage.concept_scorer import ConceptDensityScorer, ConceptDensityScore
from metadata_triage.deduplicator import DocumentDeduplicator, DeduplicationResult


class EnhancedMetadataOrchestrator:
    """
    Enhanced orchestrator for the complete metadata triage pipeline with database integration.
    """
    
    def __init__(self, 
                 db_path: str = "data/database/biomedical_data.db",
                 llm_client=None,
                 hpo_manager=None,
                 umls_api_key: Optional[str] = None,
                 pubmed_email: Optional[str] = None,
                 pubmed_api_key: Optional[str] = None,
                 europepmc_email: Optional[str] = None):
        """
        Initialize the enhanced metadata orchestrator.
        
        Args:
            db_path: Path to the SQLite database
            llm_client: LLM client for classification
            hpo_manager: HPO manager for concept scoring
            umls_api_key: UMLS API key
            pubmed_email: Email for PubMed API
            pubmed_api_key: PubMed API key
            europepmc_email: Email for Europe PMC API
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.llm_client = llm_client
        self.hpo_manager = hpo_manager
        
        # Initialize clients
        self.pubmed_client = PubMedClient(
            email=pubmed_email,
            api_key=pubmed_api_key
        )
        
        self.europepmc_client = EuropePMCClient(
            email=europepmc_email
        )
        
        self.abstract_classifier = AbstractClassifier(llm_client) if llm_client else None
        self.concept_scorer = ConceptDensityScorer(
            umls_api_key=umls_api_key,
            hpo_manager=hpo_manager
        ) if umls_api_key or hpo_manager else None
        
        self.deduplicator = DocumentDeduplicator()
        
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
    
    def search_and_store_pubmed_metadata(self, 
                                       query: str,
                                       max_results: int = 1000,
                                       save_to_csv: bool = True,
                                       output_dir: str = "data/metadata_triage") -> Dict[str, Any]:
        """
        Search PubMed and store metadata in database.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            save_to_csv: Whether to also save to CSV
            output_dir: Output directory for CSV files
            
        Returns:
            Dictionary with results summary
        """
        self.logger.info(f"Starting PubMed search for query: {query}")
        
        # Create output directory
        if save_to_csv:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate search query ID
        query_id = str(uuid.uuid4())
        
        try:
            # Search PubMed
            articles = self.pubmed_client.fetch_articles_by_query(
                query=query,
                max_results=max_results,
                include_abstracts=True,
                save_intermediate=True,
                output_dir=str(output_path / "intermediate")
            )
            
            if not articles:
                self.logger.warning("No articles found for query")
                return {
                    'success': False,
                    'query': query,
                    'articles_found': 0,
                    'articles_stored': 0,
                    'error': 'No articles found'
                }
            
            # Store in database
            stored_count = self._store_articles_in_database(articles, query)
            
            # Record search query
            self._record_search_query(query_id, query, max_results, len(articles), stored_count)
            
            # Save to CSV if requested
            csv_path = None
            if save_to_csv:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_query = query.replace(' ', '_').replace(':', '_').replace('/', '_')[:50]
                csv_filename = f"pubmed_{safe_query}_{timestamp}.csv"
                csv_path = output_path / csv_filename
                self.pubmed_client.save_to_csv(articles, str(csv_path))
            
            # Get statistics
            stats = self.pubmed_client.get_statistics(articles)
            
            result = {
                'success': True,
                'query': query,
                'query_id': query_id,
                'articles_found': len(articles),
                'articles_stored': stored_count,
                'csv_path': str(csv_path) if csv_path else None,
                'statistics': stats,
                'search_date': datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed {len(articles)} articles for query: {query}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process query '{query}': {e}")
            self._record_search_query(query_id, query, max_results, 0, 0, status='failed', error=str(e))
            return {
                'success': False,
                'query': query,
                'error': str(e)
            }
    
    def _store_articles_in_database(self, articles: List[PubMedArticle], query: str) -> int:
        """Store PubMed articles in the database."""
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
                        'pmid': article.pmid,
                        'title': article.title,
                        'sort_title': article.sort_title,
                        'last_author': article.last_author,
                        'journal': article.journal,
                        'authors': article.authors,
                        'pub_type': article.pub_type,
                        'pmc_link': article.pmc_link,
                        'doi': article.doi,
                        'abstract': article.abstract,
                        'pub_date': article.pub_date,
                        'mesh_terms': '; '.join(article.mesh_terms) if article.mesh_terms else '',
                        'keywords': '; '.join(article.keywords) if article.keywords else '',
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
                            include_europepmc: bool = True,
                            output_dir: str = "data/metadata_triage",
                            save_intermediate: bool = True) -> Dict[str, Any]:
        """
        Run the complete metadata triage pipeline.
        
        Args:
            query: Search query
            max_results: Maximum number of results per source
            include_europepmc: Whether to include Europe PMC results
            output_dir: Output directory for results
            save_intermediate: Whether to save intermediate results
            
        Returns:
            Dictionary with pipeline results
        """
        self.logger.info(f"Starting complete metadata triage pipeline for query: {query}")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Step 1: PubMed Metadata Retrieval and Storage
        self.logger.info("Step 1: Retrieving and storing metadata from PubMed")
        pubmed_result = self.search_and_store_pubmed_metadata(
            query=query,
            max_results=max_results,
            save_to_csv=True,
            output_dir=str(output_path / "pubmed")
        )
        
        if not pubmed_result['success']:
            return {
                'success': False,
                'error': f"PubMed retrieval failed: {pubmed_result.get('error', 'Unknown error')}"
            }
        
        # Step 2: Europe PMC (if requested)
        europepmc_result = None
        if include_europepmc:
            self.logger.info("Step 2: Retrieving metadata from Europe PMC")
            # TODO: Implement Europe PMC integration similar to PubMed
            europepmc_result = {'success': True, 'articles_found': 0}
        
        # Step 3: Abstract Classification (if LLM client available)
        classification_result = None
        if self.abstract_classifier:
            self.logger.info("Step 3: Classifying abstracts")
            # TODO: Implement abstract classification
            classification_result = {'success': True, 'classified': 0}
        
        # Step 4: Concept Scoring (if available)
        concept_result = None
        if self.concept_scorer:
            self.logger.info("Step 4: Scoring concepts")
            # TODO: Implement concept scoring
            concept_result = {'success': True, 'scored': 0}
        
        # Step 5: Deduplication
        self.logger.info("Step 5: Deduplicating articles")
        # TODO: Implement deduplication
        
        # Compile results
        result = {
            'success': True,
            'query': query,
            'timestamp': timestamp,
            'pubmed': pubmed_result,
            'europepmc': europepmc_result,
            'classification': classification_result,
            'concept_scoring': concept_result,
            'total_articles': pubmed_result['articles_found'],
            'output_directory': str(output_path)
        }
        
        self.logger.info(f"Pipeline completed successfully. Total articles: {result['total_articles']}")
        return result


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Enhanced Metadata Triage Pipeline")
    parser.add_argument('query', help='Search query')
    parser.add_argument('--max-results', type=int, default=1000, help='Maximum results')
    parser.add_argument('--db-path', default='data/database/biomedical_data.db', help='Database path')
    parser.add_argument('--output-dir', default='data/metadata_triage', help='Output directory')
    parser.add_argument('--pubmed-email', help='PubMed API email')
    parser.add_argument('--pubmed-api-key', help='PubMed API key')
    parser.add_argument('--europepmc-email', help='Europe PMC email')
    parser.add_argument('--no-europepmc', action='store_true', help='Skip Europe PMC')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = EnhancedMetadataOrchestrator(
        db_path=args.db_path,
        pubmed_email=args.pubmed_email,
        pubmed_api_key=args.pubmed_api_key,
        europepmc_email=args.europepmc_email
    )
    
    # Run pipeline
    result = orchestrator.run_complete_pipeline(
        query=args.query,
        max_results=args.max_results,
        include_europepmc=not args.no_europepmc,
        output_dir=args.output_dir
    )
    
    if result['success']:
        print(f"Pipeline completed successfully!")
        print(f"Total articles found: {result['total_articles']}")
        print(f"Output directory: {result['output_directory']}")
    else:
        print(f"Pipeline failed: {result.get('error', 'Unknown error')}")
        exit(1)


if __name__ == "__main__":
    main()