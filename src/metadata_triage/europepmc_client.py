"""
Europe PMC Client for Bulk Metadata Retrieval

This module provides integration with Europe PMC API for additional
metadata sources and cross-validation with PubMed data.
"""

import requests
import json
import pandas as pd
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class EuropePMCArticle:
    """Represents a Europe PMC article with metadata."""
    pmid: Optional[str]
    pmcid: Optional[str]
    doi: Optional[str]
    title: str
    authors: str
    journal: str
    pub_date: str
    abstract: Optional[str]
    full_text_url: Optional[str]
    citation_count: int
    source: str
    pub_type: str
    mesh_terms: List[str]
    grants: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            'PMID': self.pmid,
            'PMCID': self.pmcid,
            'DOI': self.doi,
            'Title': self.title,
            'Authors': self.authors,
            'Journal': self.journal,
            'PubDate': self.pub_date,
            'Abstract': self.abstract,
            'FullTextURL': self.full_text_url,
            'CitationCount': self.citation_count,
            'Source': self.source,
            'PubType': self.pub_type,
            'MeshTerms': '; '.join(self.mesh_terms) if self.mesh_terms else '',
            'Grants': '; '.join(self.grants) if self.grants else ''
        }


class EuropePMCClient:
    """
    Europe PMC API client for metadata retrieval.
    """
    
    def __init__(self, email: Optional[str] = None):
        """
        Initialize Europe PMC client.
        
        Args:
            email: Email for API requests (optional but recommended)
        """
        self.base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest"
        self.email = email
        
        # Rate limiting (Europe PMC allows higher rates than PubMed)
        self.requests_per_second = 20
        self.last_request_time = 0
        
        self.logger = logging.getLogger(__name__)
        
        # Session for connection pooling
        self.session = requests.Session()
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': f'biomedical_text_agent ({email})' if email else 'biomedical_text_agent'
        })
    
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
                       source: str = "MED",
                       result_type: str = "core",
                       page_size: int = 1000,
                       max_results: int = 10000) -> List[Dict[str, Any]]:
        """
        Search Europe PMC articles.
        
        Args:
            query: Search query
            source: Data source (MED, PMC, ETH, CBA, AGR, etc.)
            result_type: Type of results (core, lite)
            page_size: Number of results per page
            max_results: Maximum total results
            
        Returns:
            List of article dictionaries
        """
        all_results = []
        cursor_mark = "*"
        
        while len(all_results) < max_results:
            self._rate_limit()
            
            params = {
                'query': query,
                'source': source,
                'resultType': result_type,
                'pageSize': min(page_size, max_results - len(all_results)),
                'cursorMark': cursor_mark,
                'format': 'json'
            }
            
            try:
                response = self.session.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'resultList' not in data or 'result' not in data['resultList']:
                    break
                
                results = data['resultList']['result']
                if not results:
                    break
                
                all_results.extend(results)
                
                # Check if we have more results
                next_cursor_mark = data.get('nextCursorMark')
                if not next_cursor_mark or next_cursor_mark == cursor_mark:
                    break
                
                cursor_mark = next_cursor_mark
                
                self.logger.info(f"Fetched {len(all_results)} articles so far...")
                
            except Exception as e:
                self.logger.error(f"Search request failed: {e}")
                break
        
        self.logger.info(f"Found {len(all_results)} articles for query: {query}")
        return all_results[:max_results]
    
    def get_full_text_links(self, pmcid: str) -> List[Dict[str, str]]:
        """
        Get full text links for a PMC article.
        
        Args:
            pmcid: PMC ID (with or without PMC prefix)
            
        Returns:
            List of full text link dictionaries
        """
        if not pmcid.startswith('PMC'):
            pmcid = f'PMC{pmcid}'
        
        self._rate_limit()
        
        try:
            response = self.session.get(f"{self.base_url}/{pmcid}/fullTextUrlList")
            response.raise_for_status()
            
            data = response.json()
            
            if 'fullTextUrlList' in data and 'fullTextUrl' in data['fullTextUrlList']:
                return data['fullTextUrlList']['fullTextUrl']
            
        except Exception as e:
            self.logger.error(f"Failed to get full text links for {pmcid}: {e}")
        
        return []
    
    def get_citations(self, pmid: str = None, pmcid: str = None, doi: str = None) -> Dict[str, Any]:
        """
        Get citation information for an article.
        
        Args:
            pmid: PubMed ID
            pmcid: PMC ID
            doi: DOI
            
        Returns:
            Citation information dictionary
        """
        # Construct identifier
        if pmid:
            identifier = f"MED:{pmid}"
        elif pmcid:
            if not pmcid.startswith('PMC'):
                pmcid = f'PMC{pmcid}'
            identifier = f"PMC:{pmcid}"
        elif doi:
            identifier = f"DOI:{doi}"
        else:
            return {}
        
        self._rate_limit()
        
        try:
            response = self.session.get(f"{self.base_url}/{identifier}/citations")
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get citations for {identifier}: {e}")
            return {}
    
    def get_references(self, pmid: str = None, pmcid: str = None) -> List[Dict[str, Any]]:
        """
        Get references for an article.
        
        Args:
            pmid: PubMed ID
            pmcid: PMC ID
            
        Returns:
            List of reference dictionaries
        """
        # Construct identifier
        if pmid:
            identifier = f"MED:{pmid}"
        elif pmcid:
            if not pmcid.startswith('PMC'):
                pmcid = f'PMC{pmcid}'
            identifier = f"PMC:{pmcid}"
        else:
            return []
        
        self._rate_limit()
        
        try:
            response = self.session.get(f"{self.base_url}/{identifier}/references")
            response.raise_for_status()
            
            data = response.json()
            
            if 'referenceList' in data and 'reference' in data['referenceList']:
                return data['referenceList']['reference']
            
        except Exception as e:
            self.logger.error(f"Failed to get references for {identifier}: {e}")
        
        return []
    
    def create_article_objects(self, results: List[Dict[str, Any]]) -> List[EuropePMCArticle]:
        """
        Create EuropePMCArticle objects from search results.
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            List of EuropePMCArticle objects
        """
        articles = []
        
        for result in results:
            # Extract basic information
            pmid = result.get('pmid')
            pmcid = result.get('pmcid')
            doi = result.get('doi')
            title = result.get('title', '')
            
            # Extract authors
            author_list = result.get('authorList', {}).get('author', [])
            if isinstance(author_list, list):
                authors = ', '.join([
                    f"{author.get('lastName', '')}, {author.get('firstName', '')}"
                    for author in author_list
                    if author.get('lastName')
                ])
            else:
                authors = result.get('authorString', '')
            
            # Extract journal information
            journal = result.get('journalInfo', {}).get('journal', {}).get('title', '')
            if not journal:
                journal = result.get('journalTitle', '')
            
            # Extract publication date
            pub_date = result.get('firstPublicationDate', '')
            if not pub_date:
                pub_date = result.get('electronicPublicationDate', '')
            
            # Extract abstract
            abstract = result.get('abstractText', '')
            
            # Extract full text URL
            full_text_url = None
            if pmcid:
                full_text_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/"
            
            # Extract citation count
            citation_count = result.get('citedByCount', 0)
            
            # Extract source
            source = result.get('source', '')
            
            # Extract publication type
            pub_type_list = result.get('pubTypeList', {}).get('pubType', [])
            if isinstance(pub_type_list, list):
                pub_type = ', '.join(pub_type_list)
            else:
                pub_type = str(pub_type_list) if pub_type_list else ''
            
            # Extract MeSH terms
            mesh_list = result.get('meshHeadingList', {}).get('meshHeading', [])
            mesh_terms = []
            if isinstance(mesh_list, list):
                for mesh in mesh_list:
                    if isinstance(mesh, dict):
                        descriptor = mesh.get('descriptorName', '')
                        if descriptor:
                            mesh_terms.append(descriptor)
            
            # Extract grant information
            grant_list = result.get('grantsList', {}).get('grant', [])
            grants = []
            if isinstance(grant_list, list):
                for grant in grant_list:
                    if isinstance(grant, dict):
                        grant_id = grant.get('grantId', '')
                        agency = grant.get('agency', '')
                        if grant_id or agency:
                            grants.append(f"{agency}: {grant_id}" if agency else grant_id)
            
            article = EuropePMCArticle(
                pmid=pmid,
                pmcid=pmcid,
                doi=doi,
                title=title,
                authors=authors,
                journal=journal,
                pub_date=pub_date,
                abstract=abstract,
                full_text_url=full_text_url,
                citation_count=citation_count,
                source=source,
                pub_type=pub_type,
                mesh_terms=mesh_terms,
                grants=grants
            )
            
            articles.append(article)
        
        return articles
    
    def fetch_articles_by_query(self, 
                               query: str,
                               max_results: int = 1000,
                               include_citations: bool = False,
                               save_intermediate: bool = True,
                               output_dir: str = "data/intermediate") -> List[EuropePMCArticle]:
        """
        Complete pipeline to fetch articles by query.
        
        Args:
            query: Europe PMC search query
            max_results: Maximum number of results
            include_citations: Whether to fetch citation information
            save_intermediate: Whether to save intermediate results
            output_dir: Directory for intermediate files
            
        Returns:
            List of EuropePMCArticle objects
        """
        self.logger.info(f"Starting Europe PMC fetch for query: {query}")
        
        # Create output directory
        if save_intermediate:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Step 1: Search for articles
        results = self.search_articles(query, max_results=max_results)
        
        if not results:
            self.logger.warning("No articles found for query")
            return []
        
        if save_intermediate:
            results_file = Path(output_dir) / f"europepmc_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            self.logger.info(f"Saved raw results to {results_file}")
        
        # Step 2: Create article objects
        articles = self.create_article_objects(results)
        
        # Step 3: Enhance with citation information if requested
        if include_citations:
            self.logger.info("Fetching citation information...")
            for i, article in enumerate(articles):
                try:
                    citation_info = self.get_citations(
                        pmid=article.pmid,
                        pmcid=article.pmcid,
                        doi=article.doi
                    )
                    
                    if citation_info and 'citationList' in citation_info:
                        article.citation_count = len(citation_info['citationList'].get('citation', []))
                    
                    if i % 100 == 0:
                        self.logger.info(f"Processed citations for {i}/{len(articles)} articles")
                        
                except Exception as e:
                    self.logger.error(f"Failed to get citations for article {i}: {e}")
                    continue
        
        self.logger.info(f"Successfully fetched {len(articles)} articles from Europe PMC")
        return articles
    
    def save_to_csv(self, 
                   articles: List[EuropePMCArticle], 
                   output_path: str,
                   include_metadata: bool = True) -> None:
        """
        Save articles to CSV file.
        
        Args:
            articles: List of EuropePMCArticle objects
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
            df['HasFullText'] = df['FullTextURL'].notna()
            df['HasDOI'] = df['DOI'].notna()
            df['HasGrants'] = df['Grants'].notna() & (df['Grants'] != '')
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        self.logger.info(f"Saved {len(articles)} articles to {output_path}")
    
    def get_statistics(self, articles: List[EuropePMCArticle]) -> Dict[str, Any]:
        """Get statistics about fetched articles."""
        if not articles:
            return {}
        
        total_articles = len(articles)
        with_abstracts = sum(1 for a in articles if a.abstract)
        with_full_text = sum(1 for a in articles if a.full_text_url)
        with_doi = sum(1 for a in articles if a.doi)
        with_pmid = sum(1 for a in articles if a.pmid)
        with_pmcid = sum(1 for a in articles if a.pmcid)
        
        # Citation statistics
        citations = [a.citation_count for a in articles if a.citation_count > 0]
        avg_citations = sum(citations) / len(citations) if citations else 0
        
        # Source distribution
        sources = {}
        for article in articles:
            if article.source:
                sources[article.source] = sources.get(article.source, 0) + 1
        
        # Publication type distribution
        pub_types = {}
        for article in articles:
            if article.pub_type:
                types = [t.strip() for t in article.pub_type.split(',')]
                for pub_type in types:
                    pub_types[pub_type] = pub_types.get(pub_type, 0) + 1
        
        return {
            'total_articles': total_articles,
            'with_abstracts': with_abstracts,
            'with_full_text': with_full_text,
            'with_doi': with_doi,
            'with_pmid': with_pmid,
            'with_pmcid': with_pmcid,
            'abstract_rate': with_abstracts / total_articles if total_articles > 0 else 0,
            'full_text_rate': with_full_text / total_articles if total_articles > 0 else 0,
            'average_citations': avg_citations,
            'sources': sources,
            'publication_types': pub_types
        }


# Utility functions

def create_europepmc_client(email: str = None) -> EuropePMCClient:
    """Create a Europe PMC client."""
    return EuropePMCClient(email=email)


def fetch_leigh_syndrome_europepmc(output_path: str = "data/leigh_syndrome_europepmc.csv") -> List[EuropePMCArticle]:
    """
    Fetch Leigh syndrome articles from Europe PMC.
    
    Args:
        output_path: Output CSV file path
        
    Returns:
        List of EuropePMCArticle objects
    """
    client = EuropePMCClient()
    
    # Query for Leigh syndrome case reports
    query = "Leigh syndrome case report"
    
    articles = client.fetch_articles_by_query(
        query=query,
        max_results=1000,
        include_citations=True
    )
    
    # Save to CSV
    client.save_to_csv(articles, output_path)
    
    # Print statistics
    stats = client.get_statistics(articles)
    print(f"Fetched {stats['total_articles']} articles from Europe PMC")
    print(f"Abstract rate: {stats['abstract_rate']:.2%}")
    print(f"Full text rate: {stats['full_text_rate']:.2%}")
    print(f"Average citations: {stats['average_citations']:.1f}")
    
    return articles

