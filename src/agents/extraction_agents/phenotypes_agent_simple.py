"""
Simplified Phenotypes Agent for Testing

This is a simplified version to test basic functionality.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from core.base import ProcessingResult
from core.llm_client.openrouter_client import OpenRouterClient


@dataclass
class SimplePhenotypeExtraction:
    """Simplified phenotype extraction result."""
    phenotypes: List[str]
    symptoms: List[str]
    diagnostic_findings: List[str]
    lab_values: List[str]
    imaging_findings: List[str]
    extraction_metadata: Dict[str, Any]


class SimplePhenotypesAgent:
    """Simplified phenotypes agent for testing."""
    
    def __init__(self, llm_client=None):
        """Initialize simplified phenotypes agent."""
        self.llm_client = llm_client
        logging.info("Simple phenotypes agent initialized")
    
    async def extract_phenotypes(self, 
                               patient_text: str,
                               patient_id: Optional[str] = None) -> ProcessingResult[SimplePhenotypeExtraction]:
        """Extract phenotypes using simple pattern matching."""
        try:
            # Simple pattern-based extraction
            phenotypes = self._extract_simple_patterns(patient_text)
            
            # Create extraction result
            extraction = SimplePhenotypeExtraction(
                phenotypes=phenotypes,
                symptoms=phenotypes,  # For simplicity, use phenotypes as symptoms
                diagnostic_findings=[],
                lab_values=[],
                imaging_findings=[],
                extraction_metadata={
                    'extraction_method': 'simple_patterns',
                    'extraction_timestamp': datetime.now().isoformat()
                }
            )
            
            return ProcessingResult(
                success=True,
                data=extraction,
                metadata={
                    'agent_type': 'simple_phenotypes',
                    'patient_id': patient_id,
                    'extraction_method': 'simple_patterns'
                }
            )
            
        except Exception as e:
            logging.error(f"Simple phenotype extraction failed: {e}")
            return ProcessingResult(
                success=False,
                error=f"Simple phenotype extraction failed: {str(e)}",
                metadata={'agent_type': 'simple_phenotypes'}
            )
    
    def _extract_simple_patterns(self, text: str) -> List[str]:
        """Extract phenotypes using simple text patterns."""
        phenotypes = []
        text_lower = text.lower()
        
        # Simple keyword matching
        keywords = [
            'seizures', 'seizure', 'epilepsy', 'epileptic',
            'developmental delay', 'delayed development',
            'hypotonia', 'muscular hypotonia', 'low muscle tone',
            'failure to thrive', 'poor growth',
            'intellectual disability', 'mental retardation',
            'autism', 'autistic',
            'visual impairment', 'blindness',
            'hearing loss', 'deafness',
            'cardiac defect', 'heart defect',
            'respiratory distress', 'breathing difficulty'
        ]
        
        for keyword in keywords:
            if keyword in text_lower:
                phenotypes.append(keyword)
        
        return list(set(phenotypes))  # Remove duplicates
