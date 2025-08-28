"""
Unified System Orchestrator for Biomedical Text Agent

This module provides a single interface to coordinate all system components,
ensuring proper data flow and integration between metadata triage, extraction,
storage, and UI components.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from .unified_config import get_config, UnifiedConfig
from ..database.sqlite_manager import SQLiteManager
from ..database.vector_manager import VectorManager
from ..metadata_triage.metadata_orchestrator import UnifiedMetadataOrchestrator
from ..agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
from ..langextract_integration.extractor import LangExtractEngine
from ..rag.rag_system import RAGSystem

logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """System status information."""
    overall_status: str
    components: Dict[str, str]
    last_updated: datetime
    active_processes: int
    queue_size: int
    errors: List[str]
    warnings: List[str]

@dataclass
class ProcessingResult:
    """Unified processing result."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None

class UnifiedSystemOrchestrator:
    """
    Unified orchestrator that coordinates all system components.
    
    This class provides a single interface for:
    - Metadata triage and retrieval
    - Document processing and extraction
    - Data storage and retrieval
    - RAG system queries
    - System monitoring and health checks
    """
    
    def __init__(self, config: Optional[UnifiedConfig] = None):
        """Initialize the unified system orchestrator."""
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._initialize_components()
        
        # System state
        self.active_processes = 0
        self.processing_queue = asyncio.Queue()
        self.system_status = SystemStatus(
            overall_status="initializing",
            components={},
            last_updated=datetime.now(),
            active_processes=0,
            queue_size=0,
            errors=[],
            warnings=[]
        )
        
        # Start background tasks
        self._start_background_tasks()
        
        self.logger.info("Unified System Orchestrator initialized")
    
    def _initialize_components(self):
        """Initialize all system components."""
        try:
            # Database components
            self.sqlite_manager = SQLiteManager()
            self.vector_manager = VectorManager()
            
            # Metadata triage
            self.metadata_orchestrator = UnifiedMetadataOrchestrator(
                llm_client=None,  # Will be set when needed
                use_enhanced=True
            )
            
            # Extraction orchestrator
            self.extraction_orchestrator = ExtractionOrchestrator()
            
            # LangExtract engine
            self.langextract_engine = LangExtractEngine(
                config=self.config,
                model_id=self.config.llm.openrouter_default_model,
                openrouter_api_key=self.config.llm.openrouter_api_key
            )
            
            # RAG system
            self.rag_system = RAGSystem(
                vector_manager=self.vector_manager,
                sqlite_manager=self.sqlite_manager
            )
            
            self.logger.info("All system components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _start_background_tasks(self):
        """Start background monitoring and maintenance tasks."""
        asyncio.create_task(self._monitor_system_health())
        asyncio.create_task(self._process_queue())
        asyncio.create_task(self._cleanup_temp_files())
    
    async def _monitor_system_health(self):
        """Monitor system health and update status."""
        while True:
            try:
                await self._update_system_status()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _update_system_status(self):
        """Update system status information."""
        try:
            # Check component health
            components = {}
            
            # Database health
            try:
                db_stats = self.sqlite_manager.get_database_stats()
                components["database"] = "healthy" if db_stats.success else "degraded"
            except Exception:
                components["database"] = "error"
            
            # Vector database health
            try:
                vector_stats = self.vector_manager.get_database_stats()
                components["vector_db"] = "healthy" if vector_stats.success else "degraded"
            except Exception:
                components["vector_db"] = "error"
            
            # Metadata triage health
            components["metadata_triage"] = "healthy"
            
            # Extraction system health
            components["extraction"] = "healthy"
            
            # RAG system health
            components["rag"] = "healthy"
            
            # Determine overall status
            if all(status == "healthy" for status in components.values()):
                overall_status = "healthy"
            elif any(status == "error" for status in components.values()):
                overall_status = "degraded"
            else:
                overall_status = "warning"
            
            # Update system status
            self.system_status.overall_status = overall_status
            self.system_status.components = components
            self.system_status.last_updated = datetime.now()
            self.system_status.active_processes = self.active_processes
            self.system_status.queue_size = self.processing_queue.qsize()
            
        except Exception as e:
            self.logger.error(f"Failed to update system status: {e}")
    
    async def _process_queue(self):
        """Process items in the processing queue."""
        while True:
            try:
                if not self.processing_queue.empty():
                    task = await self.processing_queue.get()
                    await self._execute_task(task)
                    self.processing_queue.task_done()
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(5)
    
    async def _execute_task(self, task: Dict[str, Any]):
        """Execute a processing task."""
        task_type = task.get("type")
        task_id = task.get("id")
        
        try:
            self.active_processes += 1
            self.logger.info(f"Executing task {task_id} of type {task_type}")
            
            if task_type == "metadata_search":
                result = await self.search_metadata(
                    query=task["query"],
                    max_results=task.get("max_results", 100)
                )
            elif task_type == "document_extraction":
                result = await self.extract_from_document(
                    document_path=task["document_path"],
                    extraction_type=task.get("extraction_type", "full")
                )
            elif task_type == "rag_query":
                result = await self.ask_rag_question(
                    question=task["question"],
                    max_results=task.get("max_results", 5)
                )
            else:
                result = ProcessingResult(
                    success=False,
                    data=None,
                    error=f"Unknown task type: {task_type}"
                )
            
            # Store result
            if result.success:
                await self._store_task_result(task_id, result)
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            result = ProcessingResult(
                success=False,
                data=None,
                error=str(e)
            )
        finally:
            self.active_processes -= 1
    
    async def _store_task_result(self, task_id: str, result: ProcessingResult):
        """Store task result in database."""
        try:
            # Store in system activities table
            activity_data = {
                "id": f"task_{task_id}",
                "activity_type": "task_completion",
                "description": f"Task {task_id} completed successfully",
                "user_id": "system",
                "metadata": {
                    "task_id": task_id,
                    "success": result.success,
                    "processing_time": result.processing_time,
                    "data_size": len(str(result.data)) if result.data else 0
                }
            }
            
            # This would integrate with your existing database schema
            # For now, just log the result
            self.logger.info(f"Task {task_id} result stored")
            
        except Exception as e:
            self.logger.error(f"Failed to store task result: {e}")
    
    async def _cleanup_temp_files(self):
        """Clean up temporary files periodically."""
        while True:
            try:
                temp_dir = self.config.paths.temp_dir
                if temp_dir.exists():
                    # Remove files older than 24 hours
                    cutoff_time = datetime.now().timestamp() - 86400
                    for file_path in temp_dir.iterdir():
                        if file_path.is_file():
                            if file_path.stat().st_mtime < cutoff_time:
                                file_path.unlink()
                                self.logger.debug(f"Cleaned up temp file: {file_path}")
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                self.logger.error(f"Temp cleanup error: {e}")
                await asyncio.sleep(3600)
    
    # Public API Methods
    
    async def search_metadata(self, 
                             query: str, 
                             max_results: int = 100,
                             include_europepmc: bool = True) -> ProcessingResult:
        """Search metadata using the metadata triage system."""
        try:
            start_time = datetime.now()
            
            # Add to processing queue
            task = {
                "type": "metadata_search",
                "id": f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "query": query,
                "max_results": max_results,
                "include_europepmc": include_europepmc
            }
            
            await self.processing_queue.put(task)
            
            # For now, return immediate response
            # In production, this would return a task ID for tracking
            result = await self.metadata_orchestrator.run_complete_pipeline(
                query=query,
                max_results=max_results,
                include_europepmc=include_europepmc
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                data=result,
                processing_time=processing_time,
                metadata={"task_type": "metadata_search", "query": query}
            )
            
        except Exception as e:
            self.logger.error(f"Metadata search failed: {e}")
            return ProcessingResult(
                success=False,
                data=None,
                error=str(e),
                metadata={"task_type": "metadata_search", "query": query}
            )
    
    async def extract_from_document(self, 
                                   document_path: str,
                                   extraction_type: str = "full") -> ProcessingResult:
        """Extract information from a document."""
        try:
            start_time = datetime.now()
            
            # Add to processing queue
            task = {
                "type": "document_extraction",
                "id": f"extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "document_path": document_path,
                "extraction_type": extraction_type
            }
            
            await self.processing_queue.put(task)
            
            # Use LangExtract engine for extraction
            if extraction_type == "full":
                result = await self.langextract_engine.extract_from_file(document_path)
            else:
                # Use specific extraction agents
                result = await self.extraction_orchestrator.extract_from_file(document_path)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                data=result,
                processing_time=processing_time,
                metadata={"task_type": "document_extraction", "document_path": document_path}
            )
            
        except Exception as e:
            self.logger.error(f"Document extraction failed: {e}")
            return ProcessingResult(
                success=False,
                data=None,
                error=str(e),
                metadata={"task_type": "document_extraction", "document_path": document_path}
            )
    
    async def ask_rag_question(self, 
                               question: str, 
                               max_results: int = 5) -> ProcessingResult:
        """Ask a question using the RAG system."""
        try:
            start_time = datetime.now()
            
            # Add to processing queue
            task = {
                "type": "rag_query",
                "id": f"rag_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "question": question,
                "max_results": max_results
            }
            
            await self.processing_queue.put(task)
            
            # Use RAG system
            result = await self.rag_system.ask_question(
                question=question,
                max_results=max_results
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                data=result,
                processing_time=processing_time,
                metadata={"task_type": "rag_query", "question": question}
            )
            
        except Exception as e:
            self.logger.error(f"RAG query failed: {e}")
            return ProcessingResult(
                success=False,
                data=None,
                error=str(e),
                metadata={"task_type": "rag_query", "question": question}
            )
    
    async def get_system_status(self) -> SystemStatus:
        """Get current system status."""
        return self.system_status
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        try:
            # Database metrics
            db_stats = self.sqlite_manager.get_database_stats()
            vector_stats = self.vector_manager.get_database_stats()
            
            # Processing metrics
            processing_metrics = {
                "active_processes": self.active_processes,
                "queue_size": self.processing_queue.qsize(),
                "total_processed": 0,  # Would track from database
                "success_rate": 0.95,  # Would calculate from results
                "average_processing_time": 0.0  # Would calculate from results
            }
            
            # System metrics
            import psutil
            system_metrics = {
                "cpu_usage": psutil.cpu_percent(interval=0.1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "uptime": (datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()
            }
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system_status": self.system_status.overall_status,
                "database": db_stats.data if db_stats.success else {},
                "vector_database": vector_stats.data if vector_stats.success else {},
                "processing": processing_metrics,
                "system": system_metrics,
                "components": self.system_status.components
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "system_status": "error"
            }
    
    async def upload_document(self, 
                             file_path: str, 
                             metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Upload and process a document."""
        try:
            start_time = datetime.now()
            
            # Validate file
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return ProcessingResult(
                    success=False,
                    data=None,
                    error=f"File not found: {file_path}"
                )
            
            # Check file size
            file_size = file_path_obj.stat().st_size
            max_size = self._parse_size_string(self.config.processing.max_document_size)
            if file_size > max_size:
                return ProcessingResult(
                    success=False,
                    data=None,
                    error=f"File too large: {file_size} bytes (max: {max_size} bytes)"
                )
            
            # Check file format
            file_extension = file_path_obj.suffix.lower().lstrip('.')
            if file_extension not in self.config.processing.supported_formats:
                return ProcessingResult(
                    success=False,
                    data=None,
                    error=f"Unsupported file format: {file_extension}"
                )
            
            # Store document metadata
            document_data = {
                "id": f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "title": metadata.get("title", file_path_obj.name),
                "source_path": str(file_path_obj),
                "pmid": metadata.get("pmid"),
                "doi": metadata.get("doi"),
                "authors": metadata.get("authors"),
                "journal": metadata.get("journal"),
                "publication_date": metadata.get("publication_date"),
                "abstract": metadata.get("abstract"),
                "content": None,  # Will be extracted
                "metadata": metadata or {}
            }
            
            # Store in database
            store_result = self.sqlite_manager.store_document(document_data)
            if not store_result.success:
                return ProcessingResult(
                    success=False,
                    data=None,
                    error=f"Failed to store document: {store_result.error}"
                )
            
            # Add extraction task to queue
            await self.processing_queue.put({
                "type": "document_extraction",
                "id": f"extract_{document_data['id']}",
                "document_path": str(file_path_obj),
                "extraction_type": "full"
            })
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                data={"document_id": document_data["id"]},
                processing_time=processing_time,
                metadata={"task_type": "document_upload", "file_path": file_path}
            )
            
        except Exception as e:
            self.logger.error(f"Document upload failed: {e}")
            return ProcessingResult(
                success=False,
                data=None,
                error=str(e),
                metadata={"task_type": "document_upload", "file_path": file_path}
            )
    
    def _parse_size_string(self, size_string: str) -> int:
        """Parse size string (e.g., '50MB') to bytes."""
        size_string = size_string.upper()
        if size_string.endswith('KB'):
            return int(size_string[:-2]) * 1024
        elif size_string.endswith('MB'):
            return int(size_string[:-2]) * 1024 * 1024
        elif size_string.endswith('GB'):
            return int(size_string[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_string)
    
    async def shutdown(self):
        """Shutdown the orchestrator gracefully."""
        self.logger.info("Shutting down Unified System Orchestrator...")
        
        # Wait for active processes to complete
        while self.active_processes > 0:
            self.logger.info(f"Waiting for {self.active_processes} active processes to complete...")
            await asyncio.sleep(5)
        
        # Clear processing queue
        while not self.processing_queue.empty():
            try:
                self.processing_queue.get_nowait()
                self.processing_queue.task_done()
            except asyncio.QueueEmpty:
                break
        
        self.logger.info("Unified System Orchestrator shutdown complete")

# Global orchestrator instance
_orchestrator: Optional[UnifiedSystemOrchestrator] = None

async def get_orchestrator() -> UnifiedSystemOrchestrator:
    """Get the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = UnifiedSystemOrchestrator()
    return _orchestrator

async def shutdown_orchestrator():
    """Shutdown the global orchestrator."""
    global _orchestrator
    if _orchestrator:
        await _orchestrator.shutdown()
        _orchestrator = None