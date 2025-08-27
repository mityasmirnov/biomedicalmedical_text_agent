"""
Medical ontologies for Biomedical Text Agent.

This module provides ontology integration:
- HPO (Human Phenotype Ontology) management
- Gene symbol normalization
- Ontology mapping and validation
"""

from .hpo_manager import HPOManager
from .gene_manager import GeneManager

__all__ = [
    'HPOManager',
    'GeneManager'
]
