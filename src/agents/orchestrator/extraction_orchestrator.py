"""
Extraction orchestrator that coordinates all extraction agents.
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from core.base import Document, PatientRecord, ProcessingResult
from core.config import get_config
from core.logging_config import get_logger
from core.llm_client.openrouter_client import OpenRouterClient
from core.schema_manager.schema_manager import SchemaManager
from processors.pdf_parser import PDFParser
from processors.patient_segmenter import PatientSegmenter, PatientSegment
from agents.extraction_agents.demographics_agent import DemographicsAgent
from agents.extraction_agents.genetics_agent import GeneticsAgent

log = get_logger(__name__)

class ExtractionOrchestrator:
    """Orchestrates the complete extraction pipeline."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.app_config = get_config()
        
        # Initialize components
        self.llm_client = None
        self.schema_manager = None
        self.pdf_parser = None
        self.patient_segmenter = None
        self.agents = {}
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all pipeline components."""
        try:
            # Initialize LLM client
            self.llm_client = OpenRouterClient()
            log.info("Initialized LLM client")
            
            # Initialize schema manager
            self.schema_manager = SchemaManager()
            log.info("Initialized schema manager")
            
            # Initialize processors
            self.pdf_parser = PDFParser()
            self.patient_segmenter = PatientSegmenter()
            log.info("Initialized document processors")
            
            # Initialize extraction agents
            self.agents = {
                "demographics": DemographicsAgent(self.llm_client),
                "genetics": GeneticsAgent(self.llm_client),
            }
            log.info(f"Initialized {len(self.agents)} extraction agents")
            
        except Exception as e:
            log.error(f"Error initializing components: {str(e)}")
            raise
    
    async def extract_from_file(self, file_path: str) -> ProcessingResult[List[PatientRecord]]:
        """
        Extract patient records from a file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            ProcessingResult containing list of PatientRecords
        """
        try:
            file_path = Path(file_path)
            log.info(f"Starting extraction from file: {file_path}")
            
            # Step 1: Parse document
            document_result = await self._parse_document(file_path)
            if not document_result.success:
                return ProcessingResult(
                    success=False,
                    error=f"Document parsing failed: {document_result.error}"
                )
            
            document = document_result.data
            log.info(f"Successfully parsed document: {document.title}")
            
            # Step 2: Segment into patients
            segments_result = await self._segment_patients(document)
            if not segments_result.success:
                return ProcessingResult(
                    success=False,
                    error=f"Patient segmentation failed: {segments_result.error}"
                )
            
            segments = segments_result.data
            log.info(f"Found {len(segments)} patient segments")
            
            # Step 3: Extract data from each segment
            patient_records = []
            extraction_errors = []
            
            for i, segment in enumerate(segments):
                try:
                    record_result = await self._extract_patient_record(segment, document)
                    if record_result.success:
                        patient_records.append(record_result.data)
                        log.info(f"Successfully extracted record for {segment.patient_id}")
                    else:
                        error_msg = f"Failed to extract {segment.patient_id}: {record_result.error}"
                        extraction_errors.append(error_msg)
                        log.error(error_msg)
                        
                except Exception as e:
                    error_msg = f"Error extracting {segment.patient_id}: {str(e)}"
                    extraction_errors.append(error_msg)
                    log.error(error_msg)
            
            # Prepare result
            if patient_records:
                result = ProcessingResult(
                    success=True,
                    data=patient_records,
                    warnings=extraction_errors,
                    metadata={
                        "source_file": str(file_path),
                        "total_segments": len(segments),
                        "successful_extractions": len(patient_records),
                        "failed_extractions": len(extraction_errors),
                        "document_metadata": document.metadata
                    }
                )
                log.info(f"Extraction completed: {len(patient_records)} records extracted")
                return result
            else:
                return ProcessingResult(
                    success=False,
                    error="No patient records could be extracted",
                    metadata={"extraction_errors": extraction_errors}
                )
                
        except Exception as e:
            log.error(f"Error in extraction pipeline: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Extraction pipeline failed: {str(e)}"
            )
    
    async def _parse_document(self, file_path: Path) -> ProcessingResult[Document]:
        """Parse document based on file type."""
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return self.pdf_parser.process(str(file_path))
        else:
            return ProcessingResult(
                success=False,
                error=f"Unsupported file format: {file_extension}"
            )
    
    async def _segment_patients(self, document: Document) -> ProcessingResult[List[PatientSegment]]:
        """Segment document into patient cases."""
        return self.patient_segmenter.process(document)
    
    async def _extract_patient_record(self, segment: PatientSegment, document: Document) -> ProcessingResult[PatientRecord]:
        """Extract complete patient record from a segment."""
        try:
            log.info(f"Extracting patient record for {segment.patient_id}")
            
            # Run all extraction agents in parallel
            extraction_tasks = {}
            for agent_name, agent in self.agents.items():
                task = {
                    "patient_segment": segment,
                    "document": document
                }
                extraction_tasks[agent_name] = agent.execute(task)
            
            # Wait for all extractions to complete
            extraction_results = await asyncio.gather(
                *extraction_tasks.values(),
                return_exceptions=True
            )
            
            # Combine results
            combined_data = {}
            extraction_metadata = {}
            warnings = []
            
            for i, (agent_name, result) in enumerate(zip(extraction_tasks.keys(), extraction_results)):
                if isinstance(result, Exception):
                    error_msg = f"Agent {agent_name} failed: {str(result)}"
                    warnings.append(error_msg)
                    log.error(error_msg)
                    continue
                
                if result.success:
                    combined_data.update(result.data)
                    extraction_metadata[agent_name] = result.metadata
                    if result.warnings:
                        warnings.extend(result.warnings)
                else:
                    error_msg = f"Agent {agent_name} failed: {result.error}"
                    warnings.append(error_msg)
                    log.error(error_msg)
            
            # Add segment metadata
            combined_data.update({
                "patient_id": segment.patient_id,
                "pmid": self._extract_pmid(document),
            })
            
            # Validate against schema
            validation_result = self.schema_manager.validate_record(combined_data)
            if not validation_result.success:
                return ProcessingResult(
                    success=False,
                    error=f"Schema validation failed: {validation_result.error}"
                )
            
            if validation_result.warnings:
                warnings.extend(validation_result.warnings)
            
            # Normalize the record
            normalization_result = self.schema_manager.normalize_record(combined_data)
            if not normalization_result.success:
                return ProcessingResult(
                    success=False,
                    error=f"Record normalization failed: {normalization_result.error}"
                )
            
            normalized_data = normalization_result.data
            
            # Create PatientRecord
            patient_record = self.schema_manager.create_patient_record(
                data=normalized_data,
                source_document_id=document.id,
                extraction_metadata={
                    "agents_used": list(self.agents.keys()),
                    "agent_results": extraction_metadata,
                    "segment_metadata": segment.metadata,
                    "extraction_timestamp": segment.metadata.get("timestamp")
                }
            )
            
            return ProcessingResult(
                success=True,
                data=patient_record,
                warnings=warnings,
                metadata={
                    "extraction_agents": list(self.agents.keys()),
                    "segment_confidence": segment.confidence,
                    "validation_passed": True
                }
            )
            
        except Exception as e:
            log.error(f"Error extracting patient record: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Patient record extraction failed: {str(e)}"
            )
    
    def _extract_pmid(self, document: Document) -> Optional[int]:
        """Extract PMID from document metadata or filename."""
        # Try metadata first
        pmid = document.metadata.get("pmid")
        if pmid:
            try:
                return int(pmid)
            except (ValueError, TypeError):
                pass
        
        # Try filename
        if document.source_path:
            filename = Path(document.source_path).stem
            if filename.startswith("PMID"):
                try:
                    return int(filename[4:])  # Remove "PMID" prefix
                except (ValueError, TypeError):
                    pass
        
        return None
    
    async def extract_batch(self, file_paths: List[str]) -> ProcessingResult[List[PatientRecord]]:
        """
        Extract patient records from multiple files.
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            ProcessingResult containing list of all PatientRecords
        """
        try:
            log.info(f"Starting batch extraction for {len(file_paths)} files")
            
            all_records = []
            batch_errors = []
            
            # Process files sequentially to avoid overwhelming the LLM API
            for file_path in file_paths:
                try:
                    result = await self.extract_from_file(file_path)
                    if result.success:
                        all_records.extend(result.data)
                        if result.warnings:
                            batch_errors.extend(result.warnings)
                    else:
                        error_msg = f"Failed to process {file_path}: {result.error}"
                        batch_errors.append(error_msg)
                        log.error(error_msg)
                        
                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    batch_errors.append(error_msg)
                    log.error(error_msg)
            
            return ProcessingResult(
                success=True,
                data=all_records,
                warnings=batch_errors,
                metadata={
                    "total_files": len(file_paths),
                    "total_records": len(all_records),
                    "files_with_errors": len(batch_errors)
                }
            )
            
        except Exception as e:
            log.error(f"Error in batch extraction: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Batch extraction failed: {str(e)}"
            )
    
    def get_extraction_statistics(self, records: List[PatientRecord]) -> Dict[str, Any]:
        """Get statistics about extracted records."""
        if not records:
            return {}
        
        stats = {
            "total_records": len(records),
            "fields_extracted": {},
            "avg_confidence": 0,
            "sources": set()
        }
        
        total_confidence = 0
        field_counts = {}
        
        for record in records:
            # Count non-null fields
            for field, value in record.data.items():
                if value is not None and value != "":
                    field_counts[field] = field_counts.get(field, 0) + 1
            
            # Average confidence
            if record.confidence_scores:
                avg_record_confidence = sum(record.confidence_scores.values()) / len(record.confidence_scores)
                total_confidence += avg_record_confidence
            
            # Source tracking
            if record.source_document_id:
                stats["sources"].add(record.source_document_id)
        
        # Calculate field extraction rates
        for field, count in field_counts.items():
            stats["fields_extracted"][field] = {
                "count": count,
                "percentage": (count / len(records)) * 100
            }
        
        # Average confidence
        if total_confidence > 0:
            stats["avg_confidence"] = total_confidence / len(records)
        
        stats["unique_sources"] = len(stats["sources"])
        stats["sources"] = list(stats["sources"])
        
        return stats

