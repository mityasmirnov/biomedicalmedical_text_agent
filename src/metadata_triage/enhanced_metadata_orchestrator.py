"""
Enhanced Metadata Orchestrator

Comprehensive metadata triage system with database integration,
full-text management, and UI support.
"""

import asyncio
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import pandas as pd
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MetadataResult:
    """Structured metadata result with linking information."""
    pmid: str
    title: str
    abstract: str
    authors: List[str]
    journal: str
    publication_date: str
    doi: Optional[str]
    pmc_id: Optional[str]
    relevance_score: float
    classification: str
    content_hash: str
    fulltext_available: bool
    fulltext_url: Optional[str]
    source: str  # 'pubmed', 'europepmc', 'merged'


class FullTextManager:
    """Manages legal full-text download and storage."""
    
    def __init__(self, storage_path: str = "data/fulltext"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Legal download sources
        self.download_strategies = {
            'pmc_open_access': self._download_pmc_open_access,
            'arxiv': self._download_arxiv,
            'biorxiv': self._download_biorxiv,
            'doi_resolver': self._download_via_doi
        }
    
    async def download_fulltext(self, metadata: MetadataResult) -> Optional[str]:
        """Attempt to download full-text legally."""
        logger.info(f"Attempting full-text download for PMID: {metadata.pmid}")
        
        for strategy_name, strategy_func in self.download_strategies.items():
            try:
                fulltext = await strategy_func(metadata)
                if fulltext:
                    # Store full-text
                    filepath = await self._store_fulltext(metadata.pmid, fulltext)
                    logger.info(f"Successfully downloaded full-text via {strategy_name}: {filepath}")
                    return fulltext
            except Exception as e:
                logger.warning(f"Download strategy {strategy_name} failed: {e}")
        
        logger.info(f"No full-text available for PMID: {metadata.pmid}")
        return None
    
    async def _download_pmc_open_access(self, metadata: MetadataResult) -> Optional[str]:
        """Download from PMC Open Access if available."""
        if not metadata.pmc_id:
            return None
        
        # PMC Open Access API
        url = f"https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi"
        params = {
            'verb': 'GetRecord',
            'identifier': f'oai:pubmedcentral.nih.gov:{metadata.pmc_id}',
            'metadataPrefix': 'pmc'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    # Extract full-text from XML response
                    return self._extract_text_from_pmc_xml(content)
        
        return None
    
    async def _download_arxiv(self, metadata: MetadataResult) -> Optional[str]:
        """Download from arXiv if DOI indicates arXiv paper."""
        if not metadata.doi or 'arxiv' not in metadata.doi.lower():
            return None
        
        # Extract arXiv ID from DOI
        arxiv_id = metadata.doi.split('/')[-1]
        url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    # Extract abstract and available text
                    return self._extract_text_from_arxiv_xml(content)
        
        return None
    
    async def _download_biorxiv(self, metadata: MetadataResult) -> Optional[str]:
        """Download from bioRxiv if DOI indicates bioRxiv paper."""
        if not metadata.doi or 'biorxiv' not in metadata.doi.lower():
            return None
        
        # bioRxiv API (if available)
        # Note: This is a placeholder - actual implementation would depend on bioRxiv API
        return None
    
    async def _download_via_doi(self, metadata: MetadataResult) -> Optional[str]:
        """Attempt download via DOI resolver."""
        if not metadata.doi:
            return None
        
        # Try DOI resolver
        url = f"https://doi.org/{metadata.doi}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'text/html' in content_type:
                        content = await response.text()
                        # Extract text from HTML (basic implementation)
                        return self._extract_text_from_html(content)
        
        return None
    
    def _extract_text_from_pmc_xml(self, xml_content: str) -> str:
        """Extract text from PMC XML format."""
        # Placeholder implementation - would use proper XML parsing
        # to extract article text from PMC XML structure
        return xml_content
    
    def _extract_text_from_arxiv_xml(self, xml_content: str) -> str:
        """Extract text from arXiv XML format."""
        # Placeholder implementation
        return xml_content
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract text from HTML content."""
        # Placeholder implementation - would use BeautifulSoup
        # to extract main article text
        return html_content
    
    async def _store_fulltext(self, pmid: str, fulltext: str) -> Path:
        """Store full-text to file."""
        filepath = self.storage_path / f"{pmid}_fulltext.txt"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fulltext)
        
        return filepath


class DatabaseIntegration:
    """Integrates metadata triage with database storage."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    async def store_metadata_batch(self, metadata_results: List[MetadataResult]) -> List[str]:
        """Store batch of metadata results with linking."""
        stored_ids = []
        
        for metadata in metadata_results:
            try:
                # Store metadata
                metadata_id = await self._store_metadata(metadata)
                stored_ids.append(metadata_id)
                
                logger.info(f"Stored metadata for PMID: {metadata.pmid}")
                
            except Exception as e:
                logger.error(f"Failed to store metadata for PMID {metadata.pmid}: {e}")
        
        return stored_ids
    
    async def _store_metadata(self, metadata: MetadataResult) -> str:
        """Store individual metadata record."""
        metadata_dict = {
            'pmid': metadata.pmid,
            'title': metadata.title,
            'abstract': metadata.abstract,
            'authors': '; '.join(metadata.authors),
            'journal': metadata.journal,
            'publication_date': metadata.publication_date,
            'doi': metadata.doi,
            'pmc_id': metadata.pmc_id,
            'relevance_score': metadata.relevance_score,
            'classification': metadata.classification,
            'content_hash': metadata.content_hash,
            'fulltext_available': metadata.fulltext_available,
            'fulltext_url': metadata.fulltext_url,
            'source': metadata.source,
            'created_at': datetime.now().isoformat()
        }
        
        # Store in database
        result = await self.db_manager.store_metadata(metadata_dict)
        return result['id']
    
    async def link_fulltext(self, metadata_id: str, fulltext_path: str) -> str:
        """Link full-text to metadata record."""
        fulltext_dict = {
            'metadata_id': metadata_id,
            'filepath': str(fulltext_path),
            'content_hash': self._calculate_file_hash(fulltext_path),
            'created_at': datetime.now().isoformat()
        }
        
        result = await self.db_manager.store_fulltext(fulltext_dict)
        return result['id']
    
    async def link_extraction(self, metadata_id: str, fulltext_id: Optional[str], extraction_data: Dict) -> str:
        """Link extraction results to metadata and full-text."""
        extraction_dict = {
            'metadata_id': metadata_id,
            'fulltext_id': fulltext_id,
            'extraction_data': extraction_data,
            'created_at': datetime.now().isoformat()
        }
        
        result = await self.db_manager.store_extraction(extraction_dict)
        return result['id']
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """Calculate SHA-256 hash of file."""
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


class EnhancedMetadataOrchestrator:
    """
    Enhanced metadata orchestrator with complete pipeline integration.
    
    Provides end-to-end metadata triage from search to database storage
    with full-text management and extraction linking.
    """
    
    def __init__(self, 
                 pubmed_client,
                 europepmc_client, 
                 classifier,
                 deduplicator,
                 db_manager):
        self.pubmed_client = pubmed_client
        self.europepmc_client = europepmc_client
        self.classifier = classifier
        self.deduplicator = deduplicator
        self.fulltext_manager = FullTextManager()
        self.db_integration = DatabaseIntegration(db_manager)
        
        logger.info("Enhanced metadata orchestrator initialized")
    
    async def process_query(self, 
                          query: str, 
                          max_results: int = 1000,
                          include_fulltext: bool = True,
                          save_to_database: bool = True) -> Dict[str, Any]:
        """
        Complete metadata triage pipeline.
        
        Args:
            query: Search query
            max_results: Maximum results to retrieve
            include_fulltext: Whether to attempt full-text download
            save_to_database: Whether to save results to database
            
        Returns:
            Dictionary with processing results and statistics
        """
        logger.info(f"Starting metadata triage for query: '{query}'")
        start_time = datetime.now()
        
        try:
            # 1. Retrieve metadata from multiple sources
            logger.info("Step 1: Retrieving metadata from multiple sources")
            pubmed_results, europepmc_results = await asyncio.gather(
                self.pubmed_client.search(query, max_results // 2),
                self.europepmc_client.search(query, max_results // 2),
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(pubmed_results, Exception):
                logger.error(f"PubMed search failed: {pubmed_results}")
                pubmed_results = []
            if isinstance(europepmc_results, Exception):
                logger.error(f"Europe PMC search failed: {europepmc_results}")
                europepmc_results = []
            
            logger.info(f"Retrieved {len(pubmed_results)} PubMed results, {len(europepmc_results)} Europe PMC results")
            
            # 2. Deduplicate and merge results
            logger.info("Step 2: Deduplicating and merging results")
            merged_results = await self.deduplicator.merge_and_deduplicate(
                pubmed_results, europepmc_results
            )
            logger.info(f"After deduplication: {len(merged_results)} unique results")
            
            # 3. Classify abstracts for relevance
            logger.info("Step 3: Classifying abstracts for relevance")
            classified_results = await self.classifier.classify_batch(merged_results)
            
            # Filter by relevance threshold
            relevant_results = [r for r in classified_results if r.relevance_score >= 0.5]
            logger.info(f"After classification: {len(relevant_results)} relevant results")
            
            # 4. Attempt full-text download if requested
            fulltext_results = relevant_results
            if include_fulltext:
                logger.info("Step 4: Attempting full-text downloads")
                fulltext_results = await self._process_fulltext_batch(relevant_results)
                fulltext_count = sum(1 for r in fulltext_results if r.fulltext_available)
                logger.info(f"Successfully downloaded {fulltext_count} full-texts")
            
            # 5. Save to database if requested
            stored_ids = []
            if save_to_database:
                logger.info("Step 5: Saving to database")
                stored_ids = await self.db_integration.store_metadata_batch(fulltext_results)
                logger.info(f"Stored {len(stored_ids)} records in database")
            
            # 6. Generate summary statistics
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            summary = {
                'query': query,
                'processing_time_seconds': processing_time,
                'total_retrieved': len(pubmed_results) + len(europepmc_results),
                'after_deduplication': len(merged_results),
                'relevant_results': len(relevant_results),
                'fulltext_available': sum(1 for r in fulltext_results if r.fulltext_available) if include_fulltext else 0,
                'stored_in_database': len(stored_ids),
                'results': fulltext_results,
                'stored_ids': stored_ids
            }
            
            logger.info(f"Metadata triage completed in {processing_time:.2f} seconds")
            return summary
            
        except Exception as e:
            logger.error(f"Metadata triage failed: {e}")
            raise
    
    async def _process_fulltext_batch(self, metadata_results: List[MetadataResult]) -> List[MetadataResult]:
        """Process full-text downloads for batch of metadata results."""
        # Limit concurrent downloads to avoid overwhelming servers
        semaphore = asyncio.Semaphore(5)
        
        async def download_with_semaphore(metadata):
            async with semaphore:
                fulltext = await self.fulltext_manager.download_fulltext(metadata)
                metadata.fulltext_available = fulltext is not None
                return metadata
        
        # Process downloads concurrently
        tasks = [download_with_semaphore(metadata) for metadata in metadata_results]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if not isinstance(r, Exception)]
        
        return valid_results
    
    async def generate_csv_output(self, 
                                results: List[MetadataResult], 
                                output_path: str = "metadata_results.csv") -> str:
        """
        Generate CSV output similar to Leigh_syndrome_case_reports_abstracts.csv.
        
        Args:
            results: List of metadata results
            output_path: Output CSV file path
            
        Returns:
            Path to generated CSV file
        """
        logger.info(f"Generating CSV output: {output_path}")
        
        # Convert to DataFrame
        data = []
        for result in results:
            data.append({
                'PMID': result.pmid,
                'Title': result.title,
                'Abstract': result.abstract,
                'Authors': '; '.join(result.authors),
                'Journal': result.journal,
                'Publication_Date': result.publication_date,
                'DOI': result.doi or '',
                'PMC_ID': result.pmc_id or '',
                'Relevance_Score': result.relevance_score,
                'Classification': result.classification,
                'Fulltext_Available': result.fulltext_available,
                'Source': result.source
            })
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        logger.info(f"CSV output saved: {output_path}")
        return str(output_path)
    
    async def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics from database."""
        try:
            stats = await self.db_integration.db_manager.get_metadata_statistics()
            return stats
        except Exception as e:
            logger.error(f"Failed to get processing statistics: {e}")
            return {}
    
    async def search_stored_metadata(self, 
                                   query: str, 
                                   filters: Optional[Dict] = None) -> List[Dict]:
        """Search stored metadata in database."""
        try:
            results = await self.db_integration.db_manager.search_metadata(query, filters)
            return results
        except Exception as e:
            logger.error(f"Failed to search stored metadata: {e}")
            return []


# Example usage and testing
async def test_enhanced_orchestrator():
    """Test the enhanced metadata orchestrator."""
    # This would be called with actual client instances
    # orchestrator = EnhancedMetadataOrchestrator(
    #     pubmed_client=PubMedClient(),
    #     europepmc_client=EuropePMCClient(),
    #     classifier=AbstractClassifier(),
    #     deduplicator=DocumentDeduplicator(),
    #     db_manager=EnhancedSQLiteManager()
    # )
    
    # # Test query processing
    # results = await orchestrator.process_query(
    #     query="Leigh syndrome case report",
    #     max_results=100,
    #     include_fulltext=True,
    #     save_to_database=True
    # )
    
    # # Generate CSV output
    # csv_path = await orchestrator.generate_csv_output(
    #     results['results'],
    #     "output/leigh_syndrome_results.csv"
    # )
    
    # print(f"Processing completed. Results saved to: {csv_path}")
    # print(f"Summary: {results}")
    
    pass


if __name__ == "__main__":
    # Run test
    asyncio.run(test_enhanced_orchestrator())

