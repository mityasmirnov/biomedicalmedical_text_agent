"""
PubMed E-utilities client for bulk metadata retrieval.
Replaces R scripts with Python implementation.
"""

import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import csv
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import time
from urllib.parse import quote

logger = logging.getLogger(__name__)

class PubMedClient:
    """
    PubMed E-utilities client for literature search and metadata retrieval.
    Generates CSV files in Leigh_syndrome_case_reports_abstracts.csv format.
    """
    
    def __init__(self, email: str = "your.email@example.com", api_key: Optional[str] = None):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = email
        self.api_key = api_key
        self.rate_limit = 0.34  # 3 requests per second (conservative)
        
    async def search_literature(self, 
                              query: str, 
                              max_results: int = 1000,
                              date_range: Optional[str] = None) -> List[Dict]:
        """
        Search PubMed literature and return metadata in CSV format.
        
        Args:
            query: Search query (e.g., "Leigh syndrome case report")
            max_results: Maximum number of results to retrieve
            date_range: Date range filter (e.g., "2020:2024")
            
        Returns:
            List of dictionaries with metadata
        """
        logger.info(f"Starting PubMed search: {query}")
        
        # Step 1: Search for PMIDs
        pmids = await self._search_pmids(query, max_results, date_range)
        logger.info(f"Found {len(pmids)} PMIDs")
        
        # Step 2: Fetch detailed metadata
        metadata_list = await self._fetch_metadata_batch(pmids)
        logger.info(f"Retrieved metadata for {len(metadata_list)} articles")
        
        return metadata_list
    
    async def _search_pmids(self, 
                           query: str, 
                           max_results: int,
                           date_range: Optional[str] = None) -> List[str]:
        """Search PubMed and return list of PMIDs."""
        
        # Build search URL
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': str(max_results),
            'retmode': 'xml',
            'email': self.email
        }
        
        if self.api_key:
            search_params['api_key'] = self.api_key
            
        if date_range:
            search_params['datetype'] = 'pdat'
            search_params['mindate'] = date_range.split(':')[0]
            search_params['maxdate'] = date_range.split(':')[1]
        
        search_url = f"{self.base_url}/esearch.fcgi"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=search_params) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    return self._parse_pmids_from_xml(xml_content)
                else:
                    logger.error(f"PubMed search failed: {response.status}")
                    return []
    
    def _parse_pmids_from_xml(self, xml_content: str) -> List[str]:
        """Parse PMIDs from PubMed search XML response."""
        try:
            root = ET.fromstring(xml_content)
            pmids = []
            
            for id_elem in root.findall('.//Id'):
                pmids.append(id_elem.text)
                
            return pmids
        except ET.ParseError as e:
            logger.error(f"Failed to parse PubMed XML: {e}")
            return []
    
    async def export_to_csv(self, 
                           metadata_list: List[Dict], 
                           filename: str = "pubmed_results.csv") -> str:
        """
        Export metadata to CSV file in Leigh_syndrome_case_reports_abstracts.csv format.
        """
        
        # Define CSV headers matching the expected format
        headers = [
            'pmid', 'title', 'abstract', 'journal', 'publication_date',
            'authors', 'doi', 'keywords', 'relevance_score',
            'case_report_probability', 'patient_count_estimate', 'retrieved_at'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for metadata in metadata_list:
                # Add computed fields
                metadata['relevance_score'] = self._calculate_relevance_score(metadata)
                metadata['case_report_probability'] = self._estimate_case_report_probability(metadata)
                metadata['patient_count_estimate'] = self._estimate_patient_count(metadata)
                
                writer.writerow(metadata)
        
        logger.info(f"Exported {len(metadata_list)} records to {filename}")
        return filename
    
    def _calculate_relevance_score(self, metadata: Dict) -> float:
        """Calculate relevance score based on title and abstract content."""
        text = f"{metadata.get('title', '')} {metadata.get('abstract', '')}".lower()
        
        # Define relevance keywords with weights
        relevance_keywords = {
            'case report': 0.3, 'case study': 0.25, 'patient': 0.2,
            'clinical': 0.15, 'syndrome': 0.1, 'mutation': 0.1,
            'genetic': 0.1, 'phenotype': 0.1
        }
        
        score = 0.0
        for keyword, weight in relevance_keywords.items():
            if keyword in text:
                score += weight
        
        return min(score, 1.0)  # Cap at 1.0
