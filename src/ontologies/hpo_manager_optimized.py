"""
Optimized HPO Manager for Biomedical Information Extraction

This module provides an optimized version of the HPO manager with better performance
and caching for large-scale phenotype normalization.
"""

import json
import logging
from typing import List, Dict, Set, Optional, Any
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result wrapper for processing operations."""
    success: bool
    data: Any = None
    error: str = None


class OptimizedHPOManager:
    """Optimized HPO manager with caching and performance improvements."""
    
    def __init__(self, hpo_data_path: str = "data/ontologies/hpo/hp.json"):
        """Initialize optimized HPO manager."""
        self.hpo_data_path = Path(hpo_data_path)
        self.hpo_terms = {}
        self.hpo_names = {}
        self.hpo_synonyms = {}
        self._load_hpo_data()
        
        logger.info("Optimized HPO manager initialized")
    
    def _load_hpo_data(self):
        """Load HPO data from JSON file."""
        try:
            if self.hpo_data_path.exists():
                with open(self.hpo_data_path, 'r') as f:
                    hpo_data = json.load(f)
                
                # Build lookup dictionaries
                for term in hpo_data.get('graphs', [{}])[0].get('nodes', []):
                    term_id = term.get('id')
                    if term_id and term_id.startswith('HP:'):
                        self.hpo_terms[term_id] = term
                        
                        # Store name
                        if 'lbl' in term:
                            self.hpo_names[term['lbl'].lower()] = term_id
                        
                        # Store synonyms
                        if 'meta' in term and 'synonyms' in term['meta']:
                            for syn in term['meta']['synonyms']:
                                if 'val' in syn:
                                    self.hpo_synonyms[syn['val'].lower()] = term_id
                
                # Check if we successfully loaded any terms
                if len(self.hpo_terms) > 0:
                    logger.info(f"Loaded {len(self.hpo_terms)} HPO terms")
                else:
                    logger.warning("No HPO terms loaded from file, falling back to basic mappings")
                    self._load_basic_mappings()
            else:
                logger.warning(f"HPO data file not found: {self.hpo_data_path}")
                # Fallback to basic mappings
                self._load_basic_mappings()
                
        except Exception as e:
            logger.error(f"Failed to load HPO data: {e}")
            self._load_basic_mappings()
    
    def _load_basic_mappings(self):
        """Load basic HPO mappings as fallback."""
        self.hpo_terms = {
            "HP:0001263": {"id": "HP:0001263", "lbl": "Developmental delay"},
            "HP:0003128": {"id": "HP:0003128", "lbl": "Lactic acidosis"},
            "HP:0001250": {"id": "HP:0001250", "lbl": "Seizures"},
            "HP:0001252": {"id": "HP:0001252", "lbl": "Hypotonia"},
            "HP:0001508": {"id": "HP:0001508", "lbl": "Failure to thrive"},
            "HP:0003324": {"id": "HP:0003324", "lbl": "Generalized weakness"},
            "HP:0002027": {"id": "HP:0002027", "lbl": "Recurrent episodes"}
        }
        
        # Build name mappings
        for term_id, term in self.hpo_terms.items():
            if 'lbl' in term:
                self.hpo_names[term['lbl'].lower()] = term_id
    
    def normalize_phenotype(self, phenotype_text: str) -> ProcessingResult:
        """
        Normalize a phenotype text to HPO terms.
        
        Args:
            phenotype_text: Text describing a phenotype
            
        Returns:
            ProcessingResult with normalized data
        """
        try:
            phenotype_lower = phenotype_text.lower().strip()
            
            # Check exact matches first
            if phenotype_lower in self.hpo_names:
                term_id = self.hpo_names[phenotype_lower]
                term = self.hpo_terms[term_id]
                return ProcessingResult(
                    success=True,
                    data={
                        'hpo_id': term_id,
                        'hpo_name': term.get('lbl', ''),
                        'confidence': 0.95,
                        'match_type': 'exact'
                    }
                )
            
            # Check synonyms
            if phenotype_lower in self.hpo_synonyms:
                term_id = self.hpo_synonyms[phenotype_lower]
                term = self.hpo_terms[term_id]
                return ProcessingResult(
                    success=True,
                    data={
                        'hpo_id': term_id,
                        'hpo_name': term.get('lbl', ''),
                        'confidence': 0.90,
                        'match_type': 'synonym'
                    }
                )
            
            # Partial matching
            for name, term_id in self.hpo_names.items():
                if phenotype_lower in name or name in phenotype_lower:
                    term = self.hpo_terms[term_id]
                    return ProcessingResult(
                        success=True,
                        data={
                            'hpo_id': term_id,
                            'hpo_name': term.get('lbl', ''),
                            'confidence': 0.70,
                            'match_type': 'partial'
                        }
                    )
            
            return ProcessingResult(
                success=False,
                error="No HPO match found"
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e)
            )
    
    def batch_normalize_phenotypes(self, phenotype_list: List[str]) -> ProcessingResult:
        """
        Normalize a batch of phenotype texts.
        
        Args:
            phenotype_list: List of phenotype descriptions
            
        Returns:
            ProcessingResult with list of normalization results
        """
        try:
            results = []
            for phenotype in phenotype_list:
                result = self.normalize_phenotype(phenotype)
                results.append({
                    'original_text': phenotype,
                    'best_match': result.data if result.success else None,
                    'error': result.error if not result.success else None
                })
            
            return ProcessingResult(
                success=True,
                data=results
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e)
            )
    
    def search_terms(self, query: str, limit: int = 10) -> ProcessingResult:
        """
        Search HPO terms by query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            ProcessingResult with search results
        """
        try:
            query_lower = query.lower()
            matches = []
            
            for term_id, term in self.hpo_terms.items():
                if 'lbl' in term:
                    name = term['lbl']
                    if query_lower in name.lower():
                        matches.append({
                            'hpo_id': term_id,
                            'hpo_name': name,
                            'relevance': name.lower().count(query_lower)
                        })
            
            # Sort by relevance and limit results
            matches.sort(key=lambda x: x['relevance'], reverse=True)
            matches = matches[:limit]
            
            return ProcessingResult(
                success=True,
                data=matches
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e)
            )
    
    def get_term_info(self, hpo_id: str) -> ProcessingResult:
        """
        Get detailed information about an HPO term.
        
        Args:
            hpo_id: HPO term ID (e.g., 'HP:0001263')
            
        Returns:
            ProcessingResult with term information
        """
        try:
            if hpo_id in self.hpo_terms:
                term = self.hpo_terms[hpo_id]
                return ProcessingResult(
                    success=True,
                    data=term
                )
            else:
                return ProcessingResult(
                    success=False,
                    error=f"HPO term not found: {hpo_id}"
                )
                
        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e)
            )
