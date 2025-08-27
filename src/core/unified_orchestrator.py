"""
Unified System Orchestrator

This module provides a single interface to coordinate all system components:
- Metadata triage and document retrieval
- Document processing and extraction
- Data storage and retrieval
- RAG system and question answering
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from metadata_triage.metadata_orchestrator import MetadataOrchestrator
from langextract_integration.extractor import LangExtractEngine
from database.sqlite_manager import SQLiteManager
from database.vector_manager import VectorManager
from rag.rag_system import RAGSystem
from core.llm_client.openrouter_client import OpenRouterClient
from core.config import Config

logger = logging.getLogger(__name__)

class UnifiedOrchestrator:
    """
    Unified orchestrator for the entire Biomedical Text Agent system.
    
    This class coordinates all system components and provides a single interface
    for document processing, extraction, storage, and retrieval.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the unified orchestrator.
        
        Args:
            config: System configuration
        """
        self.config = config or Config()
        self.llm_client = None
        self.metadata_orchestrator = None
        self.extraction_engine = None
        self.sqlite_manager = None
        self.vector_manager = None
        self.rag_system = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components."""
        try:
            # Initialize LLM client
            self.llm_client = OpenRouterClient()
            logger.info("LLM client initialized")
            
            # Initialize metadata orchestrator
            self.metadata_orchestrator = MetadataOrchestrator(
                llm_client=self.llm_client
            )
            logger.info("Metadata orchestrator initialized")
            
            # Initialize extraction engine
            self.extraction_engine = LangExtractEngine(config=self.config)
            logger.info("LangExtract engine initialized")
            
            # Initialize database managers
            self.sqlite_manager = SQLiteManager()
            self.vector_manager = VectorManager()
            logger.info("Database managers initialized")
            
            # Initialize RAG system
            self.rag_system = RAGSystem(
                vector_manager=self.vector_manager,
                sqlite_manager=self.sqlite_manager
            )
            logger.info("RAG system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def process_document_pipeline(
        self,
        query: str,
        max_results: int = 100,
        include_europepmc: bool = True,
        extraction_passes: int = 2
    ) -> Dict[str, Any]:
        """
        Run the complete document processing pipeline.
        
        This method orchestrates the entire workflow:
        1. Metadata triage and document retrieval
        2. Document processing and extraction
        3. Data storage and indexing
        4. Quality assessment and validation
        
        Args:
            query: Search query for metadata triage
            max_results: Maximum number of documents to retrieve
            include_europepmc: Whether to include Europe PMC results
            extraction_passes: Number of extraction passes for LangExtract
            
        Returns:
            Dictionary containing pipeline results and statistics
        """
        logger.info(f"Starting document processing pipeline for query: {query}")
        
        try:
            # Step 1: Metadata Triage
            logger.info("Step 1: Running metadata triage")
            metadata_result = await self.metadata_orchestrator.run_complete_pipeline(
                query=query,
                max_results=max_results,
                include_europepmc=include_europepmc
            )
            
            # Step 2: Process retrieved documents
            logger.info("Step 2: Processing retrieved documents")
            processed_docs = []
            extraction_stats = {
                "total_documents": 0,
                "successful_extractions": 0,
                "failed_extractions": 0,
                "total_patients": 0
            }
            
            # Process each document
            for doc in metadata_result.get("final_documents", []):
                try:
                    # Extract text content
                    if "abstract" in doc:
                        text_content = doc["abstract"]
                    elif "content" in doc:
                        text_content = doc["content"]
                    else:
                        continue
                    
                    # Run extraction
                    extraction_result = self.extraction_engine.extract_from_text(
                        text=text_content,
                        extraction_passes=extraction_passes
                    )
                    
                    if extraction_result and extraction_result.get("success"):
                        # Store extracted data
                        doc_id = doc.get("pmid") or doc.get("id")
                        self._store_extracted_data(doc_id, doc, extraction_result)
                        
                        processed_docs.append({
                            "document": doc,
                            "extraction": extraction_result
                        })
                        
                        extraction_stats["successful_extractions"] += 1
                        extraction_stats["total_patients"] += len(
                            extraction_result.get("patient_records", [])
                        )
                    else:
                        extraction_stats["failed_extractions"] += 1
                    
                    extraction_stats["total_documents"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process document {doc.get('id', 'unknown')}: {e}")
                    extraction_stats["failed_extractions"] += 1
                    extraction_stats["total_documents"] += 1
            
            # Step 3: Update vector database
            logger.info("Step 3: Updating vector database")
            self._update_vector_database(processed_docs)
            
            # Step 4: Generate pipeline report
            pipeline_report = {
                "metadata_triage": metadata_result,
                "extraction_stats": extraction_stats,
                "processed_documents": len(processed_docs),
                "pipeline_status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Document processing pipeline completed successfully")
            logger.info(f"Processed {extraction_stats['total_documents']} documents")
            logger.info(f"Extracted {extraction_stats['total_patients']} patient records")
            
            return pipeline_report
            
        except Exception as e:
            logger.error(f"Document processing pipeline failed: {e}")
            raise
    
    def _store_extracted_data(self, doc_id: str, doc_metadata: Dict, extraction_result: Dict):
        """Store extracted data in the database."""
        try:
            # Store document metadata
            self.sqlite_manager.store_document(
                doc_id=doc_id,
                title=doc_metadata.get("title", ""),
                abstract=doc_metadata.get("abstract", ""),
                pmid=doc_metadata.get("pmid"),
                doi=doc_metadata.get("doi"),
                authors=doc_metadata.get("authors", []),
                journal=doc_metadata.get("journal", ""),
                publication_date=doc_metadata.get("publication_date", ""),
                content=doc_metadata.get("content", "")
            )
            
            # Store patient records
            for patient_record in extraction_result.get("patient_records", []):
                self.sqlite_manager.store_patient_record(
                    patient_id=patient_record.get("patient_id", f"{doc_id}_patient_{len(patient_record)}"),
                    source_document_id=doc_id,
                    **patient_record
                )
                
        except Exception as e:
            logger.error(f"Failed to store extracted data: {e}")
    
    def _update_vector_database(self, processed_docs: List[Dict]):
        """Update vector database with processed documents."""
        try:
            for doc_data in processed_docs:
                doc = doc_data["document"]
                extraction = doc_data["extraction"]
                
                # Create document text for vectorization
                doc_text = f"{doc.get('title', '')} {doc.get('abstract', '')}"
                
                # Add to vector database
                self.vector_manager.add_document(
                    doc_id=doc.get("pmid") or doc.get("id"),
                    text=doc_text,
                    metadata={
                        "title": doc.get("title"),
                        "pmid": doc.get("pmid"),
                        "extraction_summary": extraction.get("summary", "")
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to update vector database: {e}")
    
    async def ask_question(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Ask a question using the RAG system.
        
        Args:
            question: Natural language question
            max_results: Maximum number of results to return
            
        Returns:
            RAG system response
        """
        try:
            return await self.rag_system.ask_question(
                question=question,
                max_results=max_results
            )
        except Exception as e:
            logger.error(f"RAG question failed: {e}")
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status and statistics.
        
        Returns:
            Dictionary containing system status information
        """
        try:
            sqlite_stats = self.sqlite_manager.get_database_stats()
            vector_stats = self.vector_manager.get_database_stats()
            
            return {
                "status": "healthy",
                "components": {
                    "llm_client": "initialized" if self.llm_client else "not_initialized",
                    "metadata_orchestrator": "initialized" if self.metadata_orchestrator else "not_initialized",
                    "extraction_engine": "initialized" if self.extraction_engine else "not_initialized",
                    "sqlite_manager": "initialized" if self.sqlite_manager else "not_initialized",
                    "vector_manager": "initialized" if self.vector_manager else "not_initialized",
                    "rag_system": "initialized" if self.rag_system else "not_initialized"
                },
                "database_stats": {
                    "sqlite": sqlite_stats,
                    "vector": vector_stats
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }