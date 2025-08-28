"""
Metadata triage and document retrieval for Biomedical Text Agent.

This module provides document retrieval and classification:
- PubMed API integration
- Europe PMC integration
- Abstract classification
- Concept scoring
- Deduplication
- Enhanced PubMed client with caching and database integration
- Enhanced metadata orchestrator with database storage
"""

from .pubmed_client import PubMedClient
from .pubmed_client2 import EnhancedPubMedClient, EnhancedPubMedArticle
from .europepmc_client import EuropePMCClient
from .abstract_classifier import AbstractClassifier
from .concept_scorer import ConceptDensityScorer
from .deduplicator import DocumentDeduplicator

__all__ = [
    'PubMedClient',
    'EnhancedPubMedClient',
    'EnhancedPubMedArticle',
    'EuropePMCClient',
    'AbstractClassifier',
    'ConceptDensityScorer',
    'DocumentDeduplicator'
]