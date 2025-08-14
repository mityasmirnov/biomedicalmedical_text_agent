"""
PubMed Client for Bulk Metadata Retrieval

This module provides a Python implementation of PubMed E-utilities API client
for bulk metadata retrieval, similar to the R script functionality.
"""

import requests
import xml.etree.ElementTree as ET
import pandas as pd
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib
from pathlib import Path


@dataclass
class PubMedArticle:
    """Represents a PubMed article with metadata."""
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
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
            'Keywords': '; '.join(self.keywords) if self.keywords else ''
        }


class PubMedClient:
    """
    PubMed E-utilities client for bulk metadata retrieval.
    """
    
    def __init__(self, 
                 email: Optional[str] = None,
                 api_key: Optional[str] = None,
                 tool: str = "biomedical_text_agent"):
        """
        Initialize PubMed client.
        
        Args:
            email: Email for NCBI (recommended for higher rate limits)
            api_key: NCBI API key (optional, for higher rate limits)
            tool: Tool name for NCBI tracking
        """
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = email
        self.api_key = api_key
        self.tool = tool
        
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
    
    def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search_articles(self, 
                       query: str, 
                       max_results: int = 1000,
                       date_from: Optional[str] = None,
                       date_to: Optional[str] = None) -> Tuple[List[str], str]:
        """
        Search PubMed articles and return PMIDs.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            date_from: Start date (YYYY/MM/DD format)
            date_to: End date (YYYY/MM/DD format)
            
        Returns:
            Tuple of (PMIDs list, web_env for history)
        """
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
                               batch_size: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch article summaries using esummary.
        
        Args:
            pmids: List of PMIDs (if not using web history)
            web_env: Web environment from search
            query_key: Query key from search
            batch_size: Batch size for requests
            
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
        """Parse XML summaries into dictionaries."""
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
                
                summaries.append(summary)
                
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse XML: {e}")
        
        return summaries
    
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
    
    def create_article_objects(self, 
                             summaries: List[Dict[str, Any]], 
                             abstracts: Dict[str, str]) -> List[PubMedArticle]:
        """
        Create PubMedArticle objects from summaries and abstracts.
        
        Args:
            summaries: List of summary dictionaries
            abstracts: Dictionary of abstracts by PMID
            
        Returns:
            List of PubMedArticle objects
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
            
            article = PubMedArticle(
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
                keywords=keywords
            )
            
            articles.append(article)
        
        return articles
    
    def fetch_articles_by_query(self, 
                               query: str,
                               max_results: int = 1000,
                               batch_size: int = 100,
                               include_abstracts: bool = True,
                               save_intermediate: bool = True,
                               output_dir: str = "data/intermediate") -> List[PubMedArticle]:
        """
        Complete pipeline to fetch articles by query.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results
            batch_size: Batch size for API requests
            include_abstracts: Whether to fetch full abstracts
            save_intermediate: Whether to save intermediate results
            output_dir: Directory for intermediate files
            
        Returns:
            List of PubMedArticle objects
        """
        self.logger.info(f"Starting article fetch for query: {query}")
        
        # Create output directory
        if save_intermediate:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Step 1: Search for articles
        pmids, web_env, query_key = self.search_articles(query, max_results)
        
        if not pmids:
            self.logger.warning("No articles found for query")
            return []
        
        # Step 2: Fetch summaries
        summaries = self.fetch_article_summaries(
            pmids=pmids, 
            web_env=web_env, 
            query_key=query_key,
            batch_size=batch_size
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
        
        # Step 4: Create article objects
        articles = self.create_article_objects(summaries, abstracts)
        
        self.logger.info(f"Successfully fetched {len(articles)} articles")
        return articles
    
    def save_to_csv(self, 
                   articles: List[PubMedArticle], 
                   output_path: str,
                   include_metadata: bool = True) -> None:
        """
        Save articles to CSV file.
        
        Args:
            articles: List of PubMedArticle objects
            output_path: Output CSV file path
            include_metadata: Whether to include additional metadata columns
        """
        # Convert to DataFrame
        data = [article.to_dict() for article in articles]
        df = pd.DataFrame(data)
        
        # Add metadata if requested
        if include_metadata:
            df['FetchDate'] = datetime.now().isoformat()
            df['HasAbstract'] = df['Abstract'].notna() & (df['Abstract'] != '')
            df['HasPMC'] = df['PMCLink'].notna()
            df['HasDOI'] = df['DOI'].notna()
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        self.logger.info(f"Saved {len(articles)} articles to {output_path}")
    
    def get_statistics(self, articles: List[PubMedArticle]) -> Dict[str, Any]:
        """Get statistics about fetched articles."""
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
        
        return {
            'total_articles': total_articles,
            'with_abstracts': with_abstracts,
            'with_pmc': with_pmc,
            'with_doi': with_doi,
            'abstract_rate': with_abstracts / total_articles if total_articles > 0 else 0,
            'pmc_rate': with_pmc / total_articles if total_articles > 0 else 0,
            'doi_rate': with_doi / total_articles if total_articles > 0 else 0,
            'publication_types': pub_types,
            'top_journals': top_journals
        }


# Utility functions

def create_pubmed_client(email: str = None, api_key: str = None) -> PubMedClient:
    """Create a PubMed client with optional credentials."""
    return PubMedClient(email=email, api_key=api_key)


def fetch_leigh_syndrome_articles(output_path: str = "data/leigh_syndrome_articles.csv") -> List[PubMedArticle]:
    """
    Fetch Leigh syndrome case reports (similar to the R script).
    
    Args:
        output_path: Output CSV file path
        
    Returns:
        List of PubMedArticle objects
    """
    client = PubMedClient()
    
    # Query similar to the R script
    query = "Leigh syndrome case report"
    
    articles = client.fetch_articles_by_query(
        query=query,
        max_results=1000,
        include_abstracts=True
    )
    
    # Save to CSV
    client.save_to_csv(articles, output_path)
    
    # Print statistics
    stats = client.get_statistics(articles)
    print(f"Fetched {stats['total_articles']} articles")
    print(f"Abstract rate: {stats['abstract_rate']:.2%}")
    print(f"PMC rate: {stats['pmc_rate']:.2%}")
    
    return articles

