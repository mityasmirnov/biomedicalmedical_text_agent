"""
Enhanced LangExtract Integration for Biomedical Text Agent.

This module provides enhanced LangExtract integration with UI support and advanced
features, working alongside the existing extractor.py structure.
"""

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Import core components
from .extractor import LangExtractEngine
from .normalizer import BiomedicNormalizer
from .schema_classes import BiomedicExtractionClasses
from .visualizer import ExtractionVisualizer

# Import enhanced components
from database.enhanced_sqlite_manager import EnhancedSQLiteManager
from metadata_triage.enhanced_metadata_orchestrator import EnhancedMetadataOrchestrator

logger = logging.getLogger(__name__)

# ============================================================================
# Enhanced Extraction Models
# ============================================================================

class ExtractionMode(Enum):
    """Enhanced extraction mode enumeration."""
    BASIC = "basic"
    ENHANCED = "enhanced"
    ADVANCED = "advanced"
    CUSTOM = "custom"

@dataclass
class EnhancedExtractionRequest:
    """Enhanced extraction request model."""
    request_id: str
    document_id: str
    mode: ExtractionMode
    schemas: List[str]
    parameters: Dict[str, Any]
    priority: str
    callback_url: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class EnhancedExtractionResult:
    """Enhanced extraction result model."""
    request_id: str
    document_id: str
    success: bool
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    processing_time: float
    metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

# ============================================================================
# Enhanced LangExtract Integration Class
# ============================================================================

class EnhancedLangExtractIntegration:
    """Enhanced LangExtract integration with UI support and advanced features."""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        enhanced_db_manager: Optional[EnhancedSQLiteManager] = None,
        enhanced_orchestrator: Optional[EnhancedMetadataOrchestrator] = None
    ):
        """Initialize the enhanced LangExtract integration."""
        self.config = config or {}
        self.enhanced_db_manager = enhanced_db_manager or EnhancedSQLiteManager()
        self.enhanced_orchestrator = enhanced_orchestrator
        
        # Initialize core LangExtract components
        self.extractor = LangExtractEngine()
        self.normalizer = BiomedicNormalizer()
        self.visualizer = ExtractionVisualizer()
        
        # Enhanced extraction configuration
        self.extraction_config = self.config.get("extraction", {})
        self.max_concurrent_extractions = self.extraction_config.get("max_concurrent", 3)
        self.extraction_timeout = self.extraction_config.get("timeout", 300)
        
        # Enhanced processing queue
        self.extraction_queue: asyncio.Queue = asyncio.Queue()
        self.active_extractions: Dict[str, EnhancedExtractionRequest] = {}
        self.completed_extractions: Dict[str, EnhancedExtractionResult] = {}
        
        # Enhanced schemas and templates
        self.enhanced_schemas = self._initialize_enhanced_schemas()
        
        logger.info("Enhanced LangExtract Integration initialized successfully")
    
    def _initialize_enhanced_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Initialize enhanced extraction schemas."""
        schemas = {
            "biomedical_entities": {
                "name": "Biomedical Entities",
                "description": "Comprehensive biomedical entity extraction",
                "fields": ["diseases", "medications", "symptoms", "procedures", "genes"],
                "confidence_threshold": 0.8,
                "enhanced_features": ["entity_linking", "normalization", "confidence_scoring"]
            },
            "clinical_relationships": {
                "name": "Clinical Relationships",
                "description": "Clinical relationship extraction and analysis",
                "fields": ["treatment_relationships", "causal_relationships", "temporal_relationships"],
                "confidence_threshold": 0.75,
                "enhanced_features": ["relationship_graph", "confidence_propagation", "cross_validation"]
            },
            "research_metadata": {
                "name": "Research Metadata",
                "description": "Research paper metadata extraction",
                "fields": ["authors", "institutions", "funding", "methodology", "results"],
                "confidence_threshold": 0.85,
                "enhanced_features": ["metadata_enrichment", "cross_referencing", "validation"]
            }
        }
        return schemas
    
    # ============================================================================
    # Enhanced Extraction Management
    # ============================================================================
    
    async def submit_enhanced_extraction(
        self,
        document_id: str,
        mode: ExtractionMode = ExtractionMode.ENHANCED,
        schemas: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        callback_url: Optional[str] = None
    ) -> str:
        """Submit a new enhanced extraction request."""
        try:
            request_id = f"ext_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(document_id)}"
            
            # Create enhanced extraction request
            request = EnhancedExtractionRequest(
                request_id=request_id,
                document_id=document_id,
                mode=mode,
                schemas=schemas or ["biomedical_entities"],
                parameters=parameters or {},
                priority=priority,
                callback_url=callback_url
            )
            
            # Add to extraction queue
            await self.extraction_queue.put((priority, request))
            
            # Store request
            self.active_extractions[request_id] = request
            
            # Record in database
            self.enhanced_db_manager.create_extraction_request(
                document_id=document_id,
                extraction_type=f"enhanced_{mode.value}",
                parameters={
                    "schemas": schemas,
                    "mode": mode.value,
                    **(parameters or {})
                },
                priority=priority,
                callback_url=callback_url
            )
            
            logger.info(f"Submitted enhanced extraction: {request_id} (mode: {mode.value})")
            return request_id
            
        except Exception as e:
            logger.error(f"Error submitting enhanced extraction: {e}")
            raise
    
    async def start_enhanced_extraction_workers(self):
        """Start enhanced extraction workers."""
        logger.info("🚀 Starting Enhanced Extraction Workers...")
        
        workers = []
        for i in range(self.max_concurrent_extractions):
            worker = asyncio.create_task(self._extraction_worker(f"worker-{i}"))
            workers.append(worker)
        
        # Start monitoring task
        monitor_task = asyncio.create_task(self._monitor_extractions())
        
        logger.info(f"✅ Enhanced extraction workers started: {self.max_concurrent_extractions}")
        
        # Wait for all workers to complete
        await asyncio.gather(*workers, monitor_task)
    
    async def _extraction_worker(self, worker_id: str):
        """Enhanced extraction worker for processing requests."""
        logger.info(f"🔧 Enhanced extraction worker {worker_id} started")
        
        try:
            while True:
                try:
                    # Get next extraction from queue
                    priority, request = await self.extraction_queue.get()
                    
                    # Process the extraction
                    await self._process_enhanced_extraction(request, worker_id)
                    
                    # Mark extraction as done
                    self.extraction_queue.task_done()
                    
                except asyncio.CancelledError:
                    logger.info(f"Worker {worker_id} cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error in worker {worker_id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Fatal error in worker {worker_id}: {e}")
        finally:
            logger.info(f"🔧 Enhanced extraction worker {worker_id} stopped")
    
    async def _process_enhanced_extraction(
        self, 
        request: EnhancedExtractionRequest, 
        worker_id: str
    ):
        """Process an enhanced extraction request."""
        try:
            # Update request status
            request.worker_id = worker_id
            
            # Update database status
            await self.enhanced_db_manager.update_extraction_status(
                request_id=request.request_id,
                status="started"
            )
            
            logger.info(f"Processing enhanced extraction: {request.request_id}")
            
            # Execute extraction based on mode
            start_time = datetime.utcnow()
            result = await self._execute_enhanced_extraction(request)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create enhanced result
            enhanced_result = EnhancedExtractionResult(
                request_id=request.request_id,
                document_id=request.document_id,
                success=result.get("success", False),
                entities=result.get("entities", []),
                relationships=result.get("relationships", []),
                confidence_scores=result.get("confidence_scores", {}),
                processing_time=processing_time,
                metadata=result.get("metadata", {}),
                errors=result.get("errors", []),
                warnings=result.get("warnings", [])
            )
            
            # Store completed result
            self.completed_extractions[request.request_id] = enhanced_result
            
            # Update database
            await self.enhanced_db_manager.update_extraction_status(
                request_id=request.request_id,
                status="completed",
                result=asdict(enhanced_result),
                processing_time=processing_time,
                confidence_score=result.get("overall_confidence", 0.0)
            )
            
            # Update document with extracted entities
            if enhanced_result.entities:
                await self.enhanced_db_manager.update_enhanced_document(
                    document_id=request.document_id,
                    updates={
                        "extracted_entities": enhanced_result.entities,
                        "processing_status": "completed"
                    }
                )
            
            # Create relationships in database
            for rel in enhanced_result.relationships:
                await self.enhanced_db_manager.create_relationship(
                    source_id=f"{request.document_id}_{rel.get('source', 'unknown')}",
                    target_id=f"{request.document_id}_{rel.get('target', 'unknown')}",
                    relationship_type=rel.get("type", "related"),
                    relationship_data=rel.get("data", {}),
                    confidence_score=rel.get("confidence", 0.0),
                    source_type="entity",
                    target_type="entity"
                )
            
            logger.info(f"✅ Enhanced extraction completed: {request.request_id}")
            
        except Exception as e:
            logger.error(f"❌ Error processing enhanced extraction {request.request_id}: {e}")
            
            # Handle extraction failure
            await self._handle_extraction_failure(request, str(e))
    
    async def _execute_enhanced_extraction(self, request: EnhancedExtractionRequest) -> Dict[str, Any]:
        """Execute enhanced extraction based on mode and schemas."""
        try:
            # Get document content
            document = await self.enhanced_db_manager.get_enhanced_document(request.document_id)
            if not document:
                raise ValueError(f"Document {request.document_id} not found")
            
            content = document.get("content", "")
            
            # Execute based on mode
            if request.mode == ExtractionMode.BASIC:
                return await self._execute_basic_extraction(content, request)
            elif request.mode == ExtractionMode.ENHANCED:
                return await self._execute_enhanced_extraction_mode(content, request)
            elif request.mode == ExtractionMode.ADVANCED:
                return await self._execute_advanced_extraction(content, request)
            elif request.mode == ExtractionMode.CUSTOM:
                return await self._execute_custom_extraction(content, request)
            else:
                raise ValueError(f"Unknown extraction mode: {request.mode}")
                
        except Exception as e:
            logger.error(f"Error executing enhanced extraction: {e}")
            raise
    
    async def _execute_basic_extraction(self, content: str, request: EnhancedExtractionRequest) -> Dict[str, Any]:
        """Execute basic extraction using original LangExtract."""
        try:
            # Use original extractor for basic extraction
            extraction_result = await self.extractor.extract(content, request.schemas[0])
            
            return {
                "success": True,
                "entities": extraction_result.get("entities", []),
                "relationships": extraction_result.get("relationships", []),
                "confidence_scores": {"overall": 0.8},
                "metadata": {"mode": "basic", "schema": request.schemas[0]},
                "errors": [],
                "warnings": []
            }
            
        except Exception as e:
            logger.error(f"Error in basic extraction: {e}")
            raise
    
    async def _execute_enhanced_extraction_mode(self, content: str, request: EnhancedExtractionRequest) -> Dict[str, Any]:
        """Execute enhanced extraction with multiple schemas and advanced features."""
        try:
            all_entities = []
            all_relationships = []
            confidence_scores = {}
            
            # Process each schema
            for schema_name in request.schemas:
                if schema_name in self.enhanced_schemas:
                    schema_config = self.enhanced_schemas[schema_name]
                    
                    # Extract using schema
                    schema_result = await self.extractor.extract(content, schema_name)
                    
                    # Apply enhanced features
                    enhanced_entities = await self._apply_enhanced_features(
                        schema_result.get("entities", []),
                        schema_config
                    )
                    
                    enhanced_relationships = await self._apply_enhanced_features(
                        schema_result.get("relationships", []),
                        schema_config
                    )
                    
                    all_entities.extend(enhanced_entities)
                    all_relationships.extend(enhanced_relationships)
                    
                    # Calculate confidence scores
                    confidence_scores[schema_name] = self._calculate_schema_confidence(
                        enhanced_entities, enhanced_relationships, schema_config
                    )
            
            # Calculate overall confidence
            overall_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0
            confidence_scores["overall"] = overall_confidence
            
            return {
                "success": True,
                "entities": all_entities,
                "relationships": all_relationships,
                "confidence_scores": confidence_scores,
                "metadata": {
                    "mode": "enhanced",
                    "schemas_processed": request.schemas,
                    "enhanced_features": ["multi_schema", "confidence_scoring", "entity_linking"]
                },
                "errors": [],
                "warnings": []
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced extraction mode: {e}")
            raise
    
    async def _execute_advanced_extraction(self, content: str, request: EnhancedExtractionRequest) -> Dict[str, Any]:
        """Execute advanced extraction with comprehensive analysis."""
        try:
            # Advanced extraction with multiple passes
            results = {}
            
            # First pass: Basic extraction
            basic_result = await self._execute_basic_extraction(content, request)
            results["basic"] = basic_result
            
            # Second pass: Enhanced analysis
            enhanced_result = await self._execute_enhanced_extraction_mode(content, request)
            results["enhanced"] = enhanced_result
            
            # Third pass: Cross-validation and relationship analysis
            cross_validation = await self._perform_cross_validation(
                basic_result, enhanced_result
            )
            results["cross_validation"] = cross_validation
            
            # Merge and optimize results
            final_entities = self._merge_entities([
                basic_result.get("entities", []),
                enhanced_result.get("entities", [])
            ])
            
            final_relationships = self._merge_relationships([
                basic_result.get("relationships", []),
                enhanced_result.get("relationships", [])
            ])
            
            # Calculate advanced confidence scores
            advanced_confidence = self._calculate_advanced_confidence(results)
            
            return {
                "success": True,
                "entities": final_entities,
                "relationships": final_relationships,
                "confidence_scores": advanced_confidence,
                "metadata": {
                    "mode": "advanced",
                    "passes": ["basic", "enhanced", "cross_validation"],
                    "enhanced_features": ["multi_pass", "cross_validation", "result_optimization"]
                },
                "errors": [],
                "warnings": []
            }
            
        except Exception as e:
            logger.error(f"Error in advanced extraction: {e}")
            raise
    
    async def _execute_custom_extraction(self, content: str, request: EnhancedExtractionRequest) -> Dict[str, Any]:
        """Execute custom extraction based on user-defined parameters."""
        try:
            custom_params = request.parameters
            
            # Apply custom preprocessing
            if custom_params.get("preprocess", False):
                content = await self._apply_custom_preprocessing(content, custom_params)
            
            # Execute extraction with custom schemas
            custom_schemas = custom_params.get("schemas", request.schemas)
            extraction_result = await self.extractor.extract(content, custom_schemas[0])
            
            # Apply custom post-processing
            if custom_params.get("postprocess", False):
                extraction_result = await self._apply_custom_postprocessing(
                    extraction_result, custom_params
                )
            
            return {
                "success": True,
                "entities": extraction_result.get("entities", []),
                "relationships": extraction_result.get("relationships", []),
                "confidence_scores": {"overall": 0.85},
                "metadata": {
                    "mode": "custom",
                    "custom_parameters": custom_params,
                    "enhanced_features": ["custom_preprocessing", "custom_postprocessing"]
                },
                "errors": [],
                "warnings": []
            }
            
        except Exception as e:
            logger.error(f"Error in custom extraction: {e}")
            raise
    
    # ============================================================================
    # Enhanced Feature Application
    # ============================================================================
    
    async def _apply_enhanced_features(
        self, 
        items: List[Dict[str, Any]], 
        schema_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply enhanced features to extracted items."""
        try:
            enhanced_items = []
            
            for item in items:
                enhanced_item = item.copy()
                
                # Apply entity linking
                if "entity_linking" in schema_config.get("enhanced_features", []):
                    enhanced_item["linked_entities"] = await self._link_entities(item)
                
                # Apply normalization
                if "normalization" in schema_config.get("enhanced_features", []):
                    enhanced_item["normalized_value"] = await self._normalize_entity(item)
                
                # Apply confidence scoring
                if "confidence_scoring" in schema_config.get("enhanced_features", []):
                    enhanced_item["confidence_score"] = self._calculate_entity_confidence(item)
                
                enhanced_items.append(enhanced_item)
            
            return enhanced_items
            
        except Exception as e:
            logger.error(f"Error applying enhanced features: {e}")
            return items
    
    async def _link_entities(self, entity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Link entities to external knowledge bases."""
        try:
            # Mock entity linking - in real implementation, this would connect to
            # external knowledge bases like UMLS, MeSH, etc.
            linked_entities = [
                {
                    "source": "umls",
                    "concept_id": f"UMLS:{hash(entity.get('value', ''))}",
                    "confidence": 0.85
                }
            ]
            return linked_entities
            
        except Exception as e:
            logger.error(f"Error linking entities: {e}")
            return []
    
    async def _normalize_entity(self, entity: Dict[str, Any]) -> str:
        """Normalize entity values."""
        try:
            # Use the normalizer component
            normalized = await self.normalizer.normalize(
                entity.get("value", ""),
                entity.get("type", "unknown")
            )
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing entity: {e}")
            return entity.get("value", "")
    
    def _calculate_entity_confidence(self, entity: Dict[str, Any]) -> float:
        """Calculate confidence score for an entity."""
        try:
            # Mock confidence calculation - in real implementation, this would use
            # various factors like context, frequency, validation, etc.
            base_confidence = 0.8
            
            # Adjust based on entity type
            type_confidence = {
                "disease": 0.9,
                "medication": 0.85,
                "symptom": 0.8,
                "procedure": 0.9
            }
            
            entity_type = entity.get("type", "unknown")
            if entity_type in type_confidence:
                base_confidence *= type_confidence[entity_type]
            
            return min(base_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating entity confidence: {e}")
            return 0.5
    
    # ============================================================================
    # Enhanced Result Processing
    # ============================================================================
    
    async def _perform_cross_validation(
        self, 
        basic_result: Dict[str, Any], 
        enhanced_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform cross-validation between different extraction results."""
        try:
            basic_entities = {e.get("value", ""): e for e in basic_result.get("entities", [])}
            enhanced_entities = {e.get("value", ""): e for e in enhanced_result.get("entities", [])}
            
            # Find common entities
            common_values = set(basic_entities.keys()) & set(enhanced_entities.keys())
            common_entities = []
            
            for value in common_values:
                basic_entity = basic_entities[value]
                enhanced_entity = enhanced_entities[value]
                
                # Merge entity information
                merged_entity = {
                    **basic_entity,
                    **enhanced_entity,
                    "cross_validated": True,
                    "validation_confidence": (
                        basic_entity.get("confidence", 0.0) + 
                        enhanced_entity.get("confidence", 0.0)
                    ) / 2
                }
                
                common_entities.append(merged_entity)
            
            return {
                "common_entities": common_entities,
                "validation_score": len(common_entities) / max(len(basic_entities), len(enhanced_entities), 1)
            }
            
        except Exception as e:
            logger.error(f"Error in cross-validation: {e}")
            return {"common_entities": [], "validation_score": 0.0}
    
    def _merge_entities(self, entity_lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Merge entities from multiple extraction passes."""
        try:
            merged_entities = {}
            
            for entity_list in entity_lists:
                for entity in entity_list:
                    value = entity.get("value", "")
                    if value not in merged_entities:
                        merged_entities[value] = entity
                    else:
                        # Merge with existing entity
                        existing = merged_entities[value]
                        merged_entities[value] = {
                            **existing,
                            **entity,
                            "merged_from": existing.get("merged_from", []) + [entity.get("source", "unknown")]
                        }
            
            return list(merged_entities.values())
            
        except Exception as e:
            logger.error(f"Error merging entities: {e}")
            return []
    
    def _merge_relationships(self, relationship_lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Merge relationships from multiple extraction passes."""
        try:
            merged_relationships = {}
            
            for rel_list in relationship_lists:
                for rel in rel_list:
                    key = f"{rel.get('source', '')}_{rel.get('type', '')}_{rel.get('target', '')}"
                    if key not in merged_relationships:
                        merged_relationships[key] = rel
                    else:
                        # Merge with existing relationship
                        existing = merged_relationships[key]
                        merged_relationships[key] = {
                            **existing,
                            **rel,
                            "merged_from": existing.get("merged_from", []) + [rel.get("source", "unknown")]
                        }
            
            return list(merged_relationships.values())
            
        except Exception as e:
            logger.error(f"Error merging relationships: {e}")
            return []
    
    # ============================================================================
    # Enhanced Confidence Calculation
    # ============================================================================
    
    def _calculate_schema_confidence(
        self, 
        entities: List[Dict[str, Any]], 
        relationships: List[Dict[str, Any]], 
        schema_config: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for a schema."""
        try:
            if not entities and not relationships:
                return 0.0
            
            # Calculate entity confidence
            entity_confidence = sum(
                e.get("confidence_score", 0.5) for e in entities
            ) / len(entities) if entities else 0.0
            
            # Calculate relationship confidence
            relationship_confidence = sum(
                r.get("confidence", 0.5) for r in relationships
            ) / len(relationships) if relationships else 0.0
            
            # Weighted average
            total_items = len(entities) + len(relationships)
            if total_items > 0:
                weighted_confidence = (
                    (entity_confidence * len(entities) + relationship_confidence * len(relationships)) / total_items
                )
            else:
                weighted_confidence = 0.0
            
            # Apply schema-specific adjustments
            threshold = schema_config.get("confidence_threshold", 0.8)
            if weighted_confidence < threshold:
                weighted_confidence *= 0.9  # Penalty for low confidence
            
            return min(weighted_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating schema confidence: {e}")
            return 0.5
    
    def _calculate_advanced_confidence(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate advanced confidence scores for multi-pass extraction."""
        try:
            confidence_scores = {}
            
            # Individual pass confidences
            for pass_name, pass_result in results.items():
                if isinstance(pass_result, dict):
                    confidence_scores[pass_name] = pass_result.get("confidence_scores", {}).get("overall", 0.0)
            
            # Cross-validation confidence
            if "cross_validation" in results:
                cross_val = results["cross_validation"]
                confidence_scores["cross_validation"] = cross_val.get("validation_score", 0.0)
            
            # Overall confidence (weighted average)
            valid_scores = [score for score in confidence_scores.values() if score > 0]
            if valid_scores:
                overall_confidence = sum(valid_scores) / len(valid_scores)
            else:
                overall_confidence = 0.0
            
            confidence_scores["overall"] = overall_confidence
            
            return confidence_scores
            
        except Exception as e:
            logger.error(f"Error calculating advanced confidence: {e}")
            return {"overall": 0.5}
    
    # ============================================================================
    # Enhanced Monitoring and Control
    # ============================================================================
    
    async def _monitor_extractions(self):
        """Monitor enhanced extraction performance."""
        logger.info("📊 Enhanced extraction monitoring started")
        
        try:
            while True:
                await asyncio.sleep(60)  # Monitor every minute
                
                # Get extraction statistics
                active_count = len(self.active_extractions)
                completed_count = len(self.completed_extractions)
                queue_size = self.extraction_queue.qsize()
                
                # Log extraction status
                logger.info(f"📊 Extraction Status - Active: {active_count}, "
                          f"Completed: {completed_count}, Queue: {queue_size}")
                
                # Record metrics
                await self.enhanced_db_manager.record_metric(
                    metric_name="extraction_status",
                    metric_data={
                        "active_extractions": active_count,
                        "completed_extractions": completed_count,
                        "queue_size": queue_size
                    },
                    category="extraction_monitoring"
                )
                
        except asyncio.CancelledError:
            logger.info("📊 Enhanced extraction monitoring stopped")
        except Exception as e:
            logger.error(f"Error in extraction monitoring: {e}")
    
    async def _handle_extraction_failure(self, request: EnhancedExtractionRequest, error: str):
        """Handle extraction failure."""
        try:
            logger.error(f"Extraction {request.request_id} failed: {error}")
            
            # Update database status
            await self.enhanced_db_manager.update_extraction_status(
                request_id=request.request_id,
                status="failed",
                error=error
            )
            
            # Create failed result
            failed_result = EnhancedExtractionResult(
                request_id=request.request_id,
                document_id=request.document_id,
                success=False,
                entities=[],
                relationships=[],
                confidence_scores={},
                processing_time=0.0,
                metadata={"error": error},
                errors=[error],
                warnings=[]
            )
            
            self.completed_extractions[request.request_id] = failed_result
            
        except Exception as e:
            logger.error(f"Error handling extraction failure: {e}")
    
    # ============================================================================
    # Enhanced Utility Methods
    # ============================================================================
    
    async def get_extraction_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific extraction request."""
        try:
            if request_id in self.active_extractions:
                request = self.active_extractions[request_id]
                return asdict(request)
            elif request_id in self.completed_extractions:
                result = self.completed_extractions[request_id]
                return asdict(result)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting extraction status: {e}")
            raise
    
    async def get_enhanced_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get available enhanced extraction schemas."""
        return self.enhanced_schemas
    
    async def create_custom_schema(
        self, 
        name: str, 
        description: str, 
        fields: List[str], 
        confidence_threshold: float = 0.8
    ) -> bool:
        """Create a custom extraction schema."""
        try:
            self.enhanced_schemas[name] = {
                "name": name,
                "description": description,
                "fields": fields,
                "confidence_threshold": confidence_threshold,
                "enhanced_features": ["custom_schema"],
                "custom": True
            }
            
            logger.info(f"Created custom schema: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating custom schema: {e}")
            raise
    
    async def close(self):
        """Close the enhanced LangExtract integration."""
        try:
            logger.info("🛑 Closing Enhanced LangExtract Integration...")
            
            # Clear queues and active extractions
            while not self.extraction_queue.empty():
                try:
                    self.extraction_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            self.active_extractions.clear()
            self.completed_extractions.clear()
            
            logger.info("✅ Enhanced LangExtract Integration closed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error closing enhanced integration: {e}")
            raise

# ============================================================================
# Export Functions
# ============================================================================

__all__ = [
    "EnhancedLangExtractIntegration",
    "EnhancedExtractionRequest",
    "EnhancedExtractionResult",
    "ExtractionMode"
]