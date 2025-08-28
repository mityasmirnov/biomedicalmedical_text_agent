"""
Enhanced PubMed Client for Bulk Metadata Retrieval

This module provides an enhanced version of the PubMed client with additional
functionality while maintaining compatibility with the original pubmed_client.py.
"""

import requests
import xml.etree.ElementTree as ET
import pandas as pd
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import hashlib
from pathlib import Path
import sqlite3
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import re


@dataclass
class EnhancedPubMedArticle:
    """Enhanced PubMed article with additional metadata fields."""
    pmid: str
    title: str
    sort_title: str
    last_author: str
    journal: str
    authors: str
    pub_type: str
    pmc_link: Optional[str]
    doi: Optional[str]
    abstract: Optional[str]
    pub_date: Optional[str]
    mesh_terms: List[str]
    keywords: List[str]
    
    # Additional enhanced fields
    publication_year: Optional[int]
    publication_month: Optional[int]
    publication_day: Optional[int]
    language: Optional[str]
    country: Optional[str]
    grant_info: List[str]
    chemical_substances: List[str]
    citation_count: Optional[int]
    impact_factor: Optional[float]
    open_access: bool
    full_text_available: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        base_dict = {
            'PMID': self.pmid,
            'Title': self.title,
            'SortTitle': self.sort_title,
            'LastAuthor': self.last_author,
            'Journal': self.journal,
            'Authors': self.authors,
            'PubType': self.pub_type,
            'PMCLink': self.pmc_link,
            'DOI': self.doi,
            'Abstract': self.abstract,
            'PubDate': self.pub_date,
            'MeshTerms': '; '.join(self.mesh_terms) if self.mesh_terms else '',
            'Keywords': '; '.join(self.keywords) if self.keywords else '',
            'PublicationYear': self.publication_year,
            'PublicationMonth': self.publication_month,
            'PublicationDay': self.publication_day,
            'Language': self.language,
            'Country': self.country,
            'GrantInfo': '; '.join(self.grant_info) if self.grant_info else '',
            'ChemicalSubstances': '; '.join(self.chemical_substances) if self.chemical_substances else '',
            'CitationCount': self.citation_count,
            'ImpactFactor': self.impact_factor,
            'OpenAccess': self.open_access,
            'FullTextAvailable': self.full_text_available
        }
        return base_dict
    
    @classmethod
    def from_basic_article(cls, article: 'PubMedArticle') -> 'EnhancedPubMedArticle':
        """Create enhanced article from basic PubMedArticle."""
        # Parse publication date
        pub_year, pub_month, pub_day = cls._parse_publication_date(article.pub_date)
        
        # Determine open access and full text availability
        open_access = bool(article.pmc_link)
        full_text_available = bool(article.pmc_link or article.doi)
        
        return cls(
            pmid=article.pmid,
            title=article.title,
            sort_title=article.sort_title,
            last_author=article.last_author,
            journal=article.journal,
            authors=article.authors,
            pub_type=article.pub_type,
            pmc_link=article.pmc_link,
            doi=article.doi,
            abstract=article.abstract,
            pub_date=article.pub_date,
            mesh_terms=article.mesh_terms,
            keywords=article.keywords,
            publication_year=pub_year,
            publication_month=pub_month,
            publication_day=pub_day,
            language=None,  # Will be populated if available
            country=None,    # Will be populated if available
            grant_info=[],   # Will be populated if available
            chemical_substances=[],  # Will be populated if available
            citation_count=None,     # Will be populated if available
            impact_factor=None,      # Will be populated if available
            open_access=open_access,
            full_text_available=full_text_available
        )
    
    @staticmethod
    def _parse_publication_date(pub_date: Optional[str]) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """Parse publication date into year, month, day."""
        if not pub_date:
            return None, None, None
        
        try:
            # Handle various date formats
            if re.match(r'\d{4}', pub_date):
                return int(pub_date[:4]), None, None
            elif re.match(r'\d{4}/\d{1,2}', pub_date):
                parts = pub_date.split('/')
                return int(parts[0]), int(parts[1]), None
            elif re.match(r'\d{4}/\d{1,2}/\d{1,2}', pub_date):
                parts = pub_date.split('/')
                return int(parts[0]), int(parts[1]), int(parts[2])
            else:
                return None, None, None
        except (ValueError, IndexError):
            return None, None, None


class EnhancedPubMedClient:
    """
    Enhanced PubMed E-utilities client with additional functionality.
    """
    
    def __init__(self, 
                 email: Optional[str] = None,
                 api_key: Optional[str] = None,
                 tool: str = "biomedical_text_agent",
                 db_path: Optional[str] = None,
                 enable_caching: bool = True):
        """
        Initialize enhanced PubMed client.
        
        Args:
            email: Email for NCBI (recommended for higher rate limits)
            api_key: NCBI API key (optional, for higher rate limits)
            tool: Tool name for NCBI tracking
            db_path: Optional database path for caching
            enable_caching: Whether to enable result caching
        """
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = email
        self.api_key = api_key
        self.tool = tool
        self.enable_caching = enable_caching
        
        # Rate limiting
        self.requests_per_second = 10 if api_key else 3
        self.last_request_time = 0
        
        self.logger = logging.getLogger(__name__)
        
        # Session for connection pooling
        self.session = requests.Session()
        
        # Common parameters
        self.common_params = {
            'tool': self.tool,
            'email': self.email
        }
        if self.api_key:
            self.common_params['api_key'] = self.api_key
        
        # Database connection for caching
        self.db_path = Path(db_path) if db_path else None
        if self.db_path and self.enable_caching:
            self._initialize_cache_database()
    
    def _initialize_cache_database(self):
        """Initialize cache database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create cache table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pubmed_cache (
                        id TEXT PRIMARY KEY,
                        query_hash TEXT UNIQUE NOT NULL,
                        query_text TEXT NOT NULL,
                        results TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        hit_count INTEGER DEFAULT 0
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_query_hash ON pubmed_cache(query_hash)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON pubmed_cache(expires_at)")
                
                conn.commit()
                self.logger.info("Cache database initialized")
                
        except Exception as e:
            self.logger.warning(f"Failed to initialize cache database: {e}")
            self.enable_caching = False
    
    def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_key(self, query: str, max_results: int, **kwargs) -> str:
        """Generate cache key for query."""
        cache_data = {
            'query': query,
            'max_results': max_results,
            **kwargs
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cached_results(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached results if available and not expired."""
        if not self.enable_caching or not self.db_path:
            return None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT results, expires_at FROM pubmed_cache 
                    WHERE query_hash = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                """, (cache_key,))
                
                row = cursor.fetchone()
                if row:
                    results, expires_at = row
                    
                    # Update hit count
                    cursor.execute("""
                        UPDATE pubmed_cache SET hit_count = hit_count + 1 
                        WHERE query_hash = ?
                    """, (cache_key,))
                    
                    conn.commit()
                    
                    self.logger.info(f"Cache hit for query: {cache_key}")
                    return json.loads(results)
                
        except Exception as e:
            self.logger.warning(f"Cache retrieval failed: {e}")
        
        return None
    
    def _cache_results(self, cache_key: str, query: str, results: List[Dict[str, Any]], 
                      cache_duration_hours: int = 24):
        """Cache results in database."""
        if not self.enable_caching or not self.db_path:
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                expires_at = datetime.now().timestamp() + (cache_duration_hours * 3600)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO pubmed_cache (
                        id, query_hash, query_text, results, expires_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), cache_key, query, json.dumps(results), expires_at))
                
                conn.commit()
                self.logger.info(f"Cached results for query: {cache_key}")
                
        except Exception as e:
            self.logger.warning(f"Failed to cache results: {e}")
    
    def search_articles(self, 
                       query: str, 
                       max_results: int = 1000,
                       date_from: Optional[str] = None,
                       date_to: Optional[str] = None,
                       use_cache: bool = True) -> Tuple[List[str], str, str]:
        """
        Search PubMed articles and return PMIDs with caching support.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            date_from: Start date (YYYY/MM/DD format)
            date_to: End date (YYYY/MM/DD format)
            use_cache: Whether to use caching
            
        Returns:
            Tuple of (PMIDs list, web_env, query_key)
        """
        # Check cache first
        if use_cache and self.enable_caching:
            cache_key = self._get_cache_key(query, max_results, date_from=date_from, date_to=date_to)
            cached_results = self._get_cached_results(cache_key)
            if cached_results:
                # Extract PMIDs from cached results
                pmids = [result.get('pmid', '') for result in cached_results if result.get('pmid')]
                return pmids, None, None
        
        # Perform actual search
        self._rate_limit()
        
        params = {
            **self.common_params,
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'usehistory': 'y',
            'retmode': 'xml'
        }
        
        # Add date range if specified
        if date_from or date_to:
            date_range = ""
            if date_from:
                date_range += date_from
            date_range += ":"
            if date_to:
                date_range += date_to
            params['datetype'] = 'pdat'
            params['mindate'] = date_from if date_from else '1900/01/01'
            params['maxdate'] = date_to if date_to else '2030/12/31'
        
        try:
            response = self.session.get(f"{self.base_url}/esearch.fcgi", params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Extract PMIDs
            pmids = []
            for id_elem in root.findall('.//Id'):
                pmids.append(id_elem.text)
            
            # Extract web environment for history
            web_env = root.find('.//WebEnv')
            web_env = web_env.text if web_env is not None else None
            
            # Extract query key
            query_key = root.find('.//QueryKey')
            query_key = query_key.text if query_key is not None else None
            
            self.logger.info(f"Found {len(pmids)} articles for query: {query}")
            
            return pmids, web_env, query_key
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise
    
    def fetch_article_summaries(self, 
                               pmids: List[str] = None,
                               web_env: str = None,
                               query_key: str = None,
                               batch_size: int = 100,
                               use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch article summaries using esummary with caching support.
        
        Args:
            pmids: List of PMIDs (if not using web history)
            web_env: Web environment from search
            query_key: Query key from search
            batch_size: Batch size for requests
            use_cache: Whether to use caching
            
        Returns:
            List of article summary dictionaries
        """
        summaries = []
        
        if web_env and query_key:
            # Use web history
            total_count = len(pmids) if pmids else 1000  # Estimate if not provided
            
            for start in range(0, total_count, batch_size):
                self._rate_limit()
                
                params = {
                    **self.common_params,
                    'db': 'pubmed',
                    'query_key': query_key,
                    'WebEnv': web_env,
                    'retstart': start,
                    'retmax': batch_size,
                    'retmode': 'xml'
                }
                
                try:
                    response = self.session.get(f"{self.base_url}/esummary.fcgi", params=params)
                    response.raise_for_status()
                    
                    batch_summaries = self._parse_summaries(response.content)
                    summaries.extend(batch_summaries)
                    
                    self.logger.info(f"Fetched summaries {start}-{start + len(batch_summaries)}")
                    
                    if len(batch_summaries) < batch_size:
                        break
                        
                except Exception as e:
                    self.logger.error(f"Failed to fetch batch starting at {start}: {e}")
                    continue
        
        elif pmids:
            # Use direct PMID list
            for i in range(0, len(pmids), batch_size):
                batch_pmids = pmids[i:i + batch_size]
                self._rate_limit()
                
                params = {
                    **self.common_params,
                    'db': 'pubmed',
                    'id': ','.join(batch_pmids),
                    'retmode': 'xml'
                }
                
                try:
                    response = self.session.get(f"{self.base_url}/esummary.fcgi", params=params)
                    response.raise_for_status()
                    
                    batch_summaries = self._parse_summaries(response.content)
                    summaries.extend(batch_summaries)
                    
                    self.logger.info(f"Fetched summaries for PMIDs {i}-{i + len(batch_pmids)}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to fetch batch {i}-{i + len(batch_pmids)}: {e}")
                    continue
        
        return summaries
    
    def _parse_summaries(self, xml_content: bytes) -> List[Dict[str, Any]]:
        """Parse XML summaries into dictionaries with enhanced parsing."""
        summaries = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for doc_sum in root.findall('.//DocSum'):
                summary = {}
                
                # Extract PMID
                pmid_elem = doc_sum.find('./Id')
                summary['pmid'] = pmid_elem.text if pmid_elem is not None else ''
                
                # Extract other fields
                for item in doc_sum.findall('./Item'):
                    name = item.get('Name')
                    item_type = item.get('Type')
                    
                    if item_type == 'List':
                        # Handle list items (like authors)
                        list_items = []
                        for list_item in item.findall('./Item'):
                            list_items.append(list_item.text or '')
                        summary[name] = list_items
                    else:
                        summary[name] = item.text or ''
                
                # Enhanced parsing for additional fields
                summary = self._enhance_summary_parsing(summary)
                summaries.append(summary)
                
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse XML: {e}")
        
        return summaries
    
    def _enhance_summary_parsing(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance summary with additional parsed fields."""
        # Parse publication date
        pub_date = summary.get('PubDate', '')
        if pub_date:
            year, month, day = self._parse_publication_date(pub_date)
            summary['PublicationYear'] = year
            summary['PublicationMonth'] = month
            summary['PublicationDay'] = day
        
        # Parse language
        language = summary.get('LangList', [])
        if isinstance(language, list) and language:
            summary['Language'] = language[0]
        
        # Parse country
        country = summary.get('Country', '')
        summary['Country'] = country
        
        # Parse grant information
        grants = summary.get('GrantList', [])
        if isinstance(grants, list):
            summary['GrantInfo'] = grants
        else:
            summary['GrantInfo'] = []
        
        # Parse chemical substances
        chemicals = summary.get('ChemicalList', [])
        if isinstance(chemicals, list):
            summary['ChemicalSubstances'] = chemicals
        else:
            summary['ChemicalSubstances'] = []
        
        # Determine open access and full text availability
        pmc_link = summary.get('PMCLink', '')
        doi = summary.get('DOI', '')
        summary['OpenAccess'] = bool(pmc_link)
        summary['FullTextAvailable'] = bool(pmc_link or doi)
        
        return summary
    
    def _parse_publication_date(self, pub_date: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """Parse publication date into year, month, day."""
        try:
            if re.match(r'\d{4}', pub_date):
                return int(pub_date[:4]), None, None
            elif re.match(r'\d{4}/\d{1,2}', pub_date):
                parts = pub_date.split('/')
                return int(parts[0]), int(parts[1]), None
            elif re.match(r'\d{4}/\d{1,2}/\d{1,2}', pub_date):
                parts = pub_date.split('/')
                return int(parts[0]), int(parts[1]), int(parts[2])
            else:
                return None, None, None
        except (ValueError, IndexError):
            return None, None, None
    
    def fetch_abstracts(self, pmids: List[str], batch_size: int = 100) -> Dict[str, str]:
        """
        Fetch full abstracts using efetch.
        
        Args:
            pmids: List of PMIDs
            batch_size: Batch size for requests
            
        Returns:
            Dictionary mapping PMID to abstract text
        """
        abstracts = {}
        
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i + batch_size]
            self._rate_limit()
            
            params = {
                **self.common_params,
                'db': 'pubmed',
                'id': ','.join(batch_pmids),
                'rettype': 'abstract',
                'retmode': 'xml'
            }
            
            try:
                response = self.session.get(f"{self.base_url}/efetch.fcgi", params=params)
                response.raise_for_status()
                
                batch_abstracts = self._parse_abstracts(response.content)
                abstracts.update(batch_abstracts)
                
                self.logger.info(f"Fetched abstracts for PMIDs {i}-{i + len(batch_pmids)}")
                
            except Exception as e:
                self.logger.error(f"Failed to fetch abstracts for batch {i}-{i + len(batch_pmids)}: {e}")
                continue
        
        return abstracts
    
    def _parse_abstracts(self, xml_content: bytes) -> Dict[str, str]:
        """Parse XML abstracts into dictionary."""
        abstracts = {}
        
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall('.//PubmedArticle'):
                # Extract PMID
                pmid_elem = article.find('.//PMID')
                if pmid_elem is None:
                    continue
                pmid = pmid_elem.text
                
                # Extract abstract
                abstract_parts = []
                for abstract_text in article.findall('.//AbstractText'):
                    label = abstract_text.get('Label', '')
                    text = abstract_text.text or ''
                    
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)
                
                if abstract_parts:
                    abstracts[pmid] = ' '.join(abstract_parts)
                
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse abstracts XML: {e}")
        
        return abstracts
    
    def create_enhanced_article_objects(self, 
                                      summaries: List[Dict[str, Any]], 
                                      abstracts: Dict[str, str]) -> List[EnhancedPubMedArticle]:
        """
        Create EnhancedPubMedArticle objects from summaries and abstracts.
        
        Args:
            summaries: List of summary dictionaries
            abstracts: Dictionary of abstracts by PMID
            
        Returns:
            List of EnhancedPubMedArticle objects
        """
        articles = []
        
        for summary in summaries:
            pmid = summary.get('pmid', '')
            
            # Extract authors
            authors_list = summary.get('AuthorList', [])
            if isinstance(authors_list, list):
                authors = ', '.join(authors_list)
            else:
                authors = str(authors_list) if authors_list else ''
            
            # Extract last author
            last_author = authors_list[-1] if isinstance(authors_list, list) and authors_list else ''
            
            # Extract publication types
            pub_types = summary.get('PubTypeList', [])
            if isinstance(pub_types, list):
                pub_type = ', '.join(pub_types)
            else:
                pub_type = str(pub_types) if pub_types else ''
            
            # Extract article IDs for PMC and DOI
            pmc_link = None
            doi = None
            article_ids = summary.get('ArticleIds', {})
            if isinstance(article_ids, dict):
                if 'pmc' in article_ids:
                    pmc_link = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_ids['pmc']}"
                doi = article_ids.get('doi')
            
            # Extract MeSH terms
            mesh_terms = summary.get('MeshHeadingList', [])
            if not isinstance(mesh_terms, list):
                mesh_terms = []
            
            # Extract keywords
            keywords = summary.get('KeywordList', [])
            if not isinstance(keywords, list):
                keywords = []
            
            # Create enhanced article
            article = EnhancedPubMedArticle(
                pmid=pmid,
                title=summary.get('Title', ''),
                sort_title=summary.get('SortTitle', ''),
                last_author=last_author,
                journal=summary.get('FullJournalName', ''),
                authors=authors,
                pub_type=pub_type,
                pmc_link=pmc_link,
                doi=doi,
                abstract=abstracts.get(pmid, ''),
                pub_date=summary.get('PubDate', ''),
                mesh_terms=mesh_terms,
                keywords=keywords,
                publication_year=summary.get('PublicationYear'),
                publication_month=summary.get('PublicationMonth'),
                publication_day=summary.get('PublicationDay'),
                language=summary.get('Language'),
                country=summary.get('Country'),
                grant_info=summary.get('GrantInfo', []),
                chemical_substances=summary.get('ChemicalSubstances', []),
                citation_count=summary.get('CitationCount'),
                impact_factor=summary.get('ImpactFactor'),
                open_access=summary.get('OpenAccess', False),
                full_text_available=summary.get('FullTextAvailable', False)
            )
            
            articles.append(article)
        
        return articles
    
    def fetch_articles_by_query(self, 
                               query: str,
                               max_results: int = 1000,
                               batch_size: int = 100,
                               include_abstracts: bool = True,
                               save_intermediate: bool = True,
                               output_dir: str = "data/intermediate",
                               use_cache: bool = True) -> List[EnhancedPubMedArticle]:
        """
        Complete pipeline to fetch articles by query with enhanced functionality.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results
            batch_size: Batch size for API requests
            include_abstracts: Whether to fetch full abstracts
            save_intermediate: Whether to save intermediate results
            output_dir: Directory for intermediate files
            use_cache: Whether to use caching
            
        Returns:
            List of EnhancedPubMedArticle objects
        """
        self.logger.info(f"Starting enhanced article fetch for query: {query}")
        
        # Create output directory
        if save_intermediate:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Step 1: Search for articles
        pmids, web_env, query_key = self.search_articles(query, max_results, use_cache=use_cache)
        
        if not pmids:
            self.logger.warning("No articles found for query")
            return []
        
        # Step 2: Fetch summaries
        summaries = self.fetch_article_summaries(
            pmids=pmids, 
            web_env=web_env, 
            query_key=query_key,
            batch_size=batch_size,
            use_cache=use_cache
        )
        
        if save_intermediate:
            summaries_file = Path(output_dir) / f"summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summaries_file, 'w') as f:
                json.dump(summaries, f, indent=2)
            self.logger.info(f"Saved summaries to {summaries_file}")
        
        # Step 3: Fetch abstracts if requested
        abstracts = {}
        if include_abstracts:
            abstracts = self.fetch_abstracts(pmids, batch_size)
            
            if save_intermediate:
                abstracts_file = Path(output_dir) / f"abstracts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(abstracts_file, 'w') as f:
                    json.dump(abstracts, f, indent=2)
                self.logger.info(f"Saved abstracts to {abstracts_file}")
        
        # Step 4: Create enhanced article objects
        articles = self.create_enhanced_article_objects(summaries, abstracts)
        
        # Cache results if caching is enabled
        if use_cache and self.enable_caching:
            cache_key = self._get_cache_key(query, max_results)
            self._cache_results(cache_key, query, [asdict(article) for article in articles])
        
        self.logger.info(f"Successfully fetched {len(articles)} enhanced articles")
        return articles
    
    def save_to_csv(self, 
                   articles: List[Union[EnhancedPubMedArticle, 'PubMedArticle']], 
                   output_path: str,
                   include_metadata: bool = True) -> None:
        """
        Save articles to CSV file with enhanced metadata support.
        
        Args:
            articles: List of article objects
            output_path: Output CSV file path
            include_metadata: Whether to include additional metadata columns
        """
        # Convert to DataFrame
        if articles and hasattr(articles[0], 'to_dict'):
            data = [article.to_dict() for article in articles]
        else:
            # Fallback for basic PubMedArticle objects
            data = [asdict(article) for article in articles]
        
        df = pd.DataFrame(data)
        
        # Add metadata if requested
        if include_metadata:
            df['FetchDate'] = datetime.now().isoformat()
            df['HasAbstract'] = df['Abstract'].notna() & (df['Abstract'] != '')
            df['HasPMC'] = df['PMCLink'].notna()
            df['HasDOI'] = df['DOI'].notna()
            
            # Add enhanced metadata columns if available
            if 'OpenAccess' in df.columns:
                df['OpenAccess'] = df['OpenAccess'].fillna(False)
            if 'FullTextAvailable' in df.columns:
                df['FullTextAvailable'] = df['FullTextAvailable'].fillna(False)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        self.logger.info(f"Saved {len(articles)} articles to {output_path}")
    
    def get_statistics(self, articles: List[Union[EnhancedPubMedArticle, 'PubMedArticle']]) -> Dict[str, Any]:
        """Get enhanced statistics about fetched articles."""
        if not articles:
            return {}
        
        total_articles = len(articles)
        with_abstracts = sum(1 for a in articles if a.abstract)
        with_pmc = sum(1 for a in articles if a.pmc_link)
        with_doi = sum(1 for a in articles if a.doi)
        
        # Publication type distribution
        pub_types = {}
        for article in articles:
            if article.pub_type:
                types = [t.strip() for t in article.pub_type.split(',')]
                for pub_type in types:
                    pub_types[pub_type] = pub_types.get(pub_type, 0) + 1
        
        # Journal distribution (top 10)
        journals = {}
        for article in articles:
            if article.journal:
                journals[article.journal] = journals.get(article.journal, 0) + 1
        
        top_journals = dict(sorted(journals.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Enhanced statistics for EnhancedPubMedArticle objects
        enhanced_stats = {}
        if hasattr(articles[0], 'publication_year'):
            # Publication year distribution
            years = {}
            for article in articles:
                if hasattr(article, 'publication_year') and article.publication_year:
                    years[article.publication_year] = years.get(article.publication_year, 0) + 1
            
            enhanced_stats['publication_years'] = dict(sorted(years.items(), reverse=True))
            
            # Open access statistics
            if hasattr(articles[0], 'open_access'):
                open_access_count = sum(1 for a in articles if hasattr(a, 'open_access') and a.open_access)
                enhanced_stats['open_access_count'] = open_access_count
                enhanced_stats['open_access_rate'] = open_access_count / total_articles if total_articles > 0 else 0
        
        return {
            'total_articles': total_articles,
            'with_abstracts': with_abstracts,
            'with_pmc': with_pmc,
            'with_doi': with_doi,
            'abstract_rate': with_abstracts / total_articles if total_articles > 0 else 0,
            'pmc_rate': with_pmc / total_articles if total_articles > 0 else 0,
            'doi_rate': with_doi / total_articles if total_articles > 0 else 0,
            'publication_types': pub_types,
            'top_journals': top_journals,
            **enhanced_stats
        }


# Utility functions

def create_enhanced_pubmed_client(email: str = None, api_key: str = None, 
                                db_path: str = None, enable_caching: bool = True) -> EnhancedPubMedClient:
    """Create an enhanced PubMed client with optional credentials and caching."""
    return EnhancedPubMedClient(
        email=email, 
        api_key=api_key, 
        db_path=db_path, 
        enable_caching=enable_caching
    )


def fetch_leigh_syndrome_articles_enhanced(output_path: str = "data/leigh_syndrome_articles_enhanced.csv",
                                         db_path: str = "data/database/biomedical_data.db") -> List[EnhancedPubMedArticle]:
    """
    Fetch Leigh syndrome case reports with enhanced functionality.
    
    Args:
        output_path: Output CSV file path
        db_path: Database path for caching
        
    Returns:
        List of EnhancedPubMedArticle objects
    """
    client = EnhancedPubMedClient(db_path=db_path, enable_caching=True)
    
    # Query similar to the R script
    query = "Leigh syndrome case report"
    
    articles = client.fetch_articles_by_query(
        query=query,
        max_results=1000,
        include_abstracts=True,
        use_cache=True
    )
    
    # Save to CSV
    client.save_to_csv(articles, output_path)
    
    # Print statistics
    stats = client.get_statistics(articles)
    print(f"Fetched {stats['total_articles']} articles")
    print(f"Abstract rate: {stats['abstract_rate']:.2%}")
    print(f"PMC rate: {stats['pmc_rate']:.2%}")
    
    if 'open_access_rate' in stats:
        print(f"Open access rate: {stats['open_access_rate']:.2%}")
    
    return articles


if __name__ == "__main__":
    # Example usage
    client = create_enhanced_pubmed_client()
    
    # Search for Leigh syndrome case reports
    articles = client.fetch_articles_by_query(
        query="leigh syndrome case reports",
        max_results=100,
        include_abstracts=True
    )
    
    print(f"Found {len(articles)} articles")
    
    # Save to CSV
    client.save_to_csv(articles, "leigh_syndrome_enhanced.csv")
    
    # Get statistics
    stats = client.get_statistics(articles)
    print(f"Statistics: {stats}")