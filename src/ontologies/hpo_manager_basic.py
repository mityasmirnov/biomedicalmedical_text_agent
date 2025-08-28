"""
Basic HPO Manager Fallback

Provides basic HPO functionality when the optimized version is not available.
This is a fallback implementation for backward compatibility.
"""

import logging
from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result wrapper for processing operations."""
    success: bool
    data: Any = None
    error: str = None


class BasicHPOManager:
    """Basic HPO manager for fallback purposes."""
    
    def __init__(self):
        """Initialize basic HPO manager."""
        # Basic HPO mappings for testing
        self.hpo_mappings = {
            "developmental delay": ["HP:0001263"],
            "lactic acidosis": ["HP:0003128"],
            "seizures": ["HP:0001250"],
            "hypotonia": ["HP:0001252"],
            "failure to thrive": ["HP:0001508"],
            "generalized weakness": ["HP:0003324"],
            "recurrent episodes": ["HP:0002027"]
        }
        
        logger.info("Basic HPO manager initialized (fallback mode)")
    
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
            
            # Simple exact matching for testing
            if phenotype_lower in self.hpo_mappings:
                hpo_ids = self.hpo_mappings[phenotype_lower]
                return ProcessingResult(
                    success=True,
                    data={
                        'hpo_id': hpo_ids[0],
                        'hpo_name': self.get_hpo_term_name(hpo_ids[0]),
                        'confidence': 0.9,
                        'match_type': 'exact'
                    }
                )
            
            # Partial matching
            for key, hpo_ids in self.hpo_mappings.items():
                if key in phenotype_lower or phenotype_lower in key:
                    return ProcessingResult(
                        success=True,
                        data={
                            'hpo_id': hpo_ids[0],
                            'hpo_name': self.get_hpo_term_name(hpo_ids[0]),
                            'confidence': 0.7,
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
                if result.success:
                    results.append({
                        'original_text': phenotype,
                        'best_match': result.data,
                        'all_matches': [result.data] if result.data else []
                    })
                else:
                    results.append({
                        'original_text': phenotype,
                        'best_match': None,
                        'all_matches': []
                    })
            
            return ProcessingResult(success=True, data=results)
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e)
            )
    
    def map_phenotype_to_hpo(self, phenotype: str) -> Set[str]:
        """
        Map phenotype text to HPO terms.
        
        Args:
            phenotype: Phenotype text
            
        Returns:
            Set of HPO term IDs
        """
        phenotype_lower = phenotype.lower().strip()
        
        # Simple exact matching for testing
        if phenotype_lower in self.hpo_mappings:
            return set(self.hpo_mappings[phenotype_lower])
        
        # Partial matching
        for key, hpo_ids in self.hpo_mappings.items():
            if key in phenotype_lower or phenotype_lower in key:
                return set(hpo_ids)
        
        return set()
    
    def get_hpo_term_name(self, hpo_id: str) -> Optional[str]:
        """Get HPO term name by ID."""
        # Reverse mapping for testing
        reverse_map = {
            "HP:0001263": "Developmental delay",
            "HP:0003128": "Lactic acidosis", 
            "HP:0001250": "Seizures",
            "HP:0001252": "Hypotonia",
            "HP:0001508": "Failure to thrive",
            "HP:0003324": "Generalized weakness",
            "HP:0002027": "Recurrent episodes"
        }
        
        return reverse_map.get(hpo_id)
    
    def search_terms(self, query: str, limit: int = 10) -> ProcessingResult:
        """Basic search implementation for compatibility."""
        try:
            query_lower = query.lower()
            matches = []
            
            for term_id, term_name in self.hpo_mappings.items():
                if query_lower in term_name.lower():
                    matches.append({
                        'hpo_id': term_id,
                        'hpo_name': term_name,
                        'relevance': 1.0
                    })
            
            return ProcessingResult(
                success=True,
                data=matches[:limit]
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e)
            )
    
    def get_term_info(self, hpo_id: str) -> ProcessingResult:
        """Basic term info implementation for compatibility."""
        try:
            term_name = self.get_hpo_term_name(hpo_id)
            if term_name:
                return ProcessingResult(
                    success=True,
                    data={'id': hpo_id, 'lbl': term_name}
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
