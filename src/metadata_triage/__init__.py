"""
Metadata triage and document retrieval for Biomedical Text Agent.

This module provides document retrieval and classification:
- PubMed API integration
- Europe PMC integration
- Abstract classification
- Concept scoring
- Deduplication
"""

from .metadata_orchestrator import MetadataOrchestrator
from .pubmed_client import PubMedClient
from .europepmc_client import EuropePMCClient
from .abstract_classifier import AbstractClassifier
from .concept_scorer import ConceptDensityScorer
from .deduplicator import DocumentDeduplicator

__all__ = [
    'MetadataOrchestrator',
    'PubMedClient',
    'EuropePMCClient',
    'AbstractClassifier',
    'ConceptDensityScorer',
    'DocumentDeduplicator'
]