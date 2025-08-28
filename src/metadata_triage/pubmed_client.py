"""
Unified PubMed Client for Bulk Metadata Retrieval

This module provides a unified PubMed E-utilities API client that internally uses
the enhanced implementation while maintaining backward compatibility with the original API.
"""

# Import the enhanced implementation
from .pubmed_client2 import (
    EnhancedPubMedClient as _EnhancedPubMedClient,
    EnhancedPubMedArticle as _EnhancedPubMedArticle
)

# Create a compatibility PubMedArticle class that matches the original interface
class PubMedArticle:
    """Compatibility PubMedArticle class that matches the original interface."""
    
    def __init__(self, 
                 pmid: str,
                 title: str,
                 sort_title: str,
                 last_author: str,
                 journal: str,
                 authors: str,
                 pub_type: str,
                 pmc_link=None,
                 doi=None,
                 abstract=None,
                 pub_date=None,
                 mesh_terms=None,
                 keywords=None):
        self.pmid = pmid
        self.title = title
        self.sort_title = sort_title
        self.last_author = last_author
        self.journal = journal
        self.authors = authors
        self.pub_type = pub_type
        self.pmc_link = pmc_link
        self.doi = doi
        self.abstract = abstract
        self.pub_date = pub_date
        self.mesh_terms = mesh_terms or []
        self.keywords = keywords or []
    
    def to_dict(self):
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

# Alias the enhanced client as the main client
PubMedClient = _EnhancedPubMedClient

# Utility functions
def create_pubmed_client(email: str = None, api_key: str = None, **kwargs):
    """Create a PubMed client with optional credentials and enhanced features."""
    return PubMedClient(email=email, api_key=api_key, **kwargs)


def fetch_leigh_syndrome_articles(output_path: str = "data/leigh_syndrome_articles.csv", **kwargs):
    """
    Fetch Leigh syndrome case reports (similar to the R script).
    
    Args:
        output_path: Output CSV file path
        **kwargs: Additional arguments passed to the enhanced client
        
    Returns:
        List of PubMedArticle objects
    """
    client = PubMedClient(**kwargs)
    
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


# Backward compatibility: ensure the original PubMedArticle class is available
__all__ = [
    'PubMedClient',
    'PubMedArticle', 
    'create_pubmed_client',
    'fetch_leigh_syndrome_articles'
]

