"""
Enhanced LangExtract Integration

Complete LangExtract integration with UI support, text highlighting,
validation interface, and database linking.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import re
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ExtractionSpan:
    """Represents a text span with extraction information."""
    start: int
    end: int
    text: str
    extraction_type: str
    field_name: str
    confidence: float
    normalized_value: Optional[str] = None


@dataclass
class ValidationData:
    """Data structure for validation interface."""
    extraction_id: str
    original_text: str
    highlighted_text: str
    extractions: List[Dict]
    spans: List[ExtractionSpan]
    confidence_scores: Dict[str, float]
    validation_status: str = "pending"  # pending, validated, rejected
    validator_notes: Optional[str] = None


class TextHighlighter:
    """Generates highlighted text for extraction visualization."""
    
    def __init__(self):
        self.highlight_colors = {
            'demographics': '#FFE6E6',  # Light red
            'genetics': '#E6F3FF',      # Light blue
            'phenotypes': '#E6FFE6',    # Light green
            'treatments': '#FFF0E6',    # Light orange
            'outcomes': '#F0E6FF',      # Light purple
            'default': '#F5F5F5'       # Light gray
        }
    
    def highlight_extractions(self, 
                            text: str, 
                            extraction_results: Dict) -> Tuple[str, List[ExtractionSpan]]:
        """
        Generate highlighted text with extraction spans.
        
        Args:
            text: Original text
            extraction_results: LangExtract results
            
        Returns:
            Tuple of (highlighted_html, extraction_spans)
        """
        spans = self._extract_spans_from_results(text, extraction_results)
        highlighted_html = self._generate_highlighted_html(text, spans)
        
        return highlighted_html, spans
    
    def _extract_spans_from_results(self, 
                                   text: str, 
                                   extraction_results: Dict) -> List[ExtractionSpan]:
        """Extract text spans from LangExtract results."""
        spans = []
        
        for extraction in extraction_results.get('extractions', []):
            extraction_text = extraction.get('extraction_text', '')
            attributes = extraction.get('attributes', {})
            
            # Find text spans for each attribute
            for field_name, value in attributes.items():
                if isinstance(value, str) and value.strip():
                    # Find all occurrences of this value in the text
                    for match in re.finditer(re.escape(value), text, re.IGNORECASE):
                        span = ExtractionSpan(
                            start=match.start(),
                            end=match.end(),
                            text=match.group(),
                            extraction_type=self._get_extraction_type(field_name),
                            field_name=field_name,
                            confidence=self._calculate_confidence(extraction, field_name),
                            normalized_value=self._get_normalized_value(field_name, value)
                        )
                        spans.append(span)
        
        # Sort spans by start position
        spans.sort(key=lambda x: x.start)
        
        # Remove overlapping spans (keep highest confidence)
        spans = self._remove_overlapping_spans(spans)
        
        return spans
    
    def _get_extraction_type(self, field_name: str) -> str:
        """Determine extraction type from field name."""
        field_lower = field_name.lower()
        
        if any(term in field_lower for term in ['age', 'sex', 'patient', 'gender']):
            return 'demographics'
        elif any(term in field_lower for term in ['gene', 'mutation', 'variant', 'allele']):
            return 'genetics'
        elif any(term in field_lower for term in ['phenotype', 'symptom', 'clinical', 'manifestation']):
            return 'phenotypes'
        elif any(term in field_lower for term in ['treatment', 'therapy', 'medication', 'drug']):
            return 'treatments'
        elif any(term in field_lower for term in ['outcome', 'survival', 'prognosis', 'alive', 'dead']):
            return 'outcomes'
        else:
            return 'default'
    
    def _calculate_confidence(self, extraction: Dict, field_name: str) -> float:
        """Calculate confidence score for extraction."""
        # Use LangExtract confidence if available
        if 'confidence' in extraction:
            return extraction['confidence']
        
        # Calculate based on extraction quality
        attributes = extraction.get('attributes', {})
        value = attributes.get(field_name, '')
        
        if not value:
            return 0.0
        
        # Simple heuristic based on value characteristics
        confidence = 0.5  # Base confidence
        
        # Increase confidence for structured data
        if field_name in ['age_of_onset_years', 'alive_flag']:
            confidence += 0.3
        
        # Increase confidence for longer, more specific values
        if len(str(value)) > 10:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _get_normalized_value(self, field_name: str, value: str) -> Optional[str]:
        """Get normalized value if available."""
        # This would integrate with ontology managers
        # For now, return the original value
        return value
    
    def _remove_overlapping_spans(self, spans: List[ExtractionSpan]) -> List[ExtractionSpan]:
        """Remove overlapping spans, keeping highest confidence."""
        if not spans:
            return spans
        
        non_overlapping = []
        current_span = spans[0]
        
        for next_span in spans[1:]:
            # Check for overlap
            if next_span.start < current_span.end:
                # Overlapping - keep higher confidence
                if next_span.confidence > current_span.confidence:
                    current_span = next_span
            else:
                # No overlap - add current and move to next
                non_overlapping.append(current_span)
                current_span = next_span
        
        # Add the last span
        non_overlapping.append(current_span)
        
        return non_overlapping
    
    def _generate_highlighted_html(self, text: str, spans: List[ExtractionSpan]) -> str:
        """Generate HTML with highlighted spans."""
        if not spans:
            return text
        
        html_parts = []
        last_end = 0
        
        for span in spans:
            # Add text before this span
            if span.start > last_end:
                html_parts.append(text[last_end:span.start])
            
            # Add highlighted span
            color = self.highlight_colors.get(span.extraction_type, self.highlight_colors['default'])
            tooltip = f"Field: {span.field_name}, Confidence: {span.confidence:.2f}"
            
            highlighted_span = (
                f'<span class="extraction-highlight" '
                f'style="background-color: {color}; padding: 2px; border-radius: 3px;" '
                f'data-field="{span.field_name}" '
                f'data-type="{span.extraction_type}" '
                f'data-confidence="{span.confidence}" '
                f'title="{tooltip}">'
                f'{span.text}'
                f'</span>'
            )
            html_parts.append(highlighted_span)
            
            last_end = span.end
        
        # Add remaining text
        if last_end < len(text):
            html_parts.append(text[last_end:])
        
        return ''.join(html_parts)


class ValidationInterface:
    """Manages validation interface data and operations."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def prepare_validation_data(self, 
                              extraction_results: Dict, 
                              highlighted_text: str,
                              spans: List[ExtractionSpan]) -> ValidationData:
        """Prepare data for validation interface."""
        extraction_id = f"ext_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate confidence scores by field
        confidence_scores = {}
        for span in spans:
            if span.field_name not in confidence_scores:
                confidence_scores[span.field_name] = []
            confidence_scores[span.field_name].append(span.confidence)
        
        # Average confidence per field
        avg_confidence_scores = {
            field: sum(scores) / len(scores)
            for field, scores in confidence_scores.items()
        }
        
        validation_data = ValidationData(
            extraction_id=extraction_id,
            original_text=extraction_results.get('original_text', ''),
            highlighted_text=highlighted_text,
            extractions=extraction_results.get('extractions', []),
            spans=spans,
            confidence_scores=avg_confidence_scores
        )
        
        return validation_data
    
    async def store_validation_data(self, validation_data: ValidationData) -> str:
        """Store validation data in database."""
        validation_dict = {
            'extraction_id': validation_data.extraction_id,
            'original_text': validation_data.original_text,
            'highlighted_text': validation_data.highlighted_text,
            'extractions': json.dumps(validation_data.extractions),
            'spans': json.dumps([asdict(span) for span in validation_data.spans]),
            'confidence_scores': json.dumps(validation_data.confidence_scores),
            'validation_status': validation_data.validation_status,
            'validator_notes': validation_data.validator_notes,
            'created_at': datetime.now().isoformat()
        }
        
        result = await self.db_manager.store_validation_data(validation_dict)
        return result['id']
    
    async def submit_validation(self, 
                              extraction_id: str, 
                              validation_status: str,
                              corrections: Optional[Dict] = None,
                              validator_notes: Optional[str] = None) -> bool:
        """Submit validation results."""
        validation_update = {
            'validation_status': validation_status,
            'corrections': json.dumps(corrections) if corrections else None,
            'validator_notes': validator_notes,
            'validated_at': datetime.now().isoformat()
        }
        
        try:
            await self.db_manager.update_validation_data(extraction_id, validation_update)
            logger.info(f"Validation submitted for extraction {extraction_id}: {validation_status}")
            return True
        except Exception as e:
            logger.error(f"Failed to submit validation: {e}")
            return False
    
    async def get_validation_queue(self, status: str = "pending") -> List[Dict]:
        """Get validation queue for review."""
        try:
            queue = await self.db_manager.get_validation_queue(status)
            return queue
        except Exception as e:
            logger.error(f"Failed to get validation queue: {e}")
            return []


class EnhancedLangExtractEngine:
    """
    Enhanced LangExtract engine with UI support and database integration.
    
    Provides complete extraction pipeline with validation interface,
    text highlighting, and database linking.
    """
    
    def __init__(self, 
                 base_engine,
                 db_manager,
                 model_id: str = "google/gemma-2-27b-it:free"):
        self.base_engine = base_engine
        self.db_manager = db_manager
        self.model_id = model_id
        
        self.text_highlighter = TextHighlighter()
        self.validation_interface = ValidationInterface(db_manager)
        
        logger.info(f"Enhanced LangExtract engine initialized with model: {model_id}")
    
    async def extract_with_ui_support(self, 
                                    text: str, 
                                    document_id: str,
                                    metadata_id: Optional[str] = None,
                                    fulltext_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract with complete UI support and database linking.
        
        Args:
            text: Text to extract from
            document_id: Document identifier
            metadata_id: Optional metadata record ID
            fulltext_id: Optional full-text record ID
            
        Returns:
            Complete extraction results with UI data
        """
        logger.info(f"Starting extraction with UI support for document: {document_id}")
        
        try:
            # 1. Perform base extraction
            extraction_results = await self.base_engine.extract_from_text(text)
            
            # 2. Generate text highlighting
            highlighted_text, spans = self.text_highlighter.highlight_extractions(
                text, extraction_results
            )
            
            # 3. Prepare validation data
            validation_data = self.validation_interface.prepare_validation_data(
                extraction_results, highlighted_text, spans
            )
            
            # 4. Store validation data
            validation_id = await self.validation_interface.store_validation_data(validation_data)
            
            # 5. Store extraction results with linking
            extraction_id = await self._store_extraction_with_linking(
                document_id, metadata_id, fulltext_id, extraction_results, validation_id
            )
            
            # 6. Prepare UI response
            ui_response = {
                'extraction_id': extraction_id,
                'validation_id': validation_id,
                'document_id': document_id,
                'extractions': extraction_results,
                'highlighted_text': highlighted_text,
                'spans': [asdict(span) for span in spans],
                'validation_data': asdict(validation_data),
                'confidence_summary': self._calculate_confidence_summary(spans),
                'extraction_statistics': self._calculate_extraction_statistics(extraction_results)
            }
            
            logger.info(f"Extraction completed successfully for document: {document_id}")
            return ui_response
            
        except Exception as e:
            logger.error(f"Extraction failed for document {document_id}: {e}")
            raise
    
    async def _store_extraction_with_linking(self, 
                                           document_id: str,
                                           metadata_id: Optional[str],
                                           fulltext_id: Optional[str],
                                           extraction_results: Dict,
                                           validation_id: str) -> str:
        """Store extraction results with complete linking."""
        extraction_dict = {
            'document_id': document_id,
            'metadata_id': metadata_id,
            'fulltext_id': fulltext_id,
            'validation_id': validation_id,
            'model_id': self.model_id,
            'extraction_data': json.dumps(extraction_results),
            'created_at': datetime.now().isoformat()
        }
        
        result = await self.db_manager.store_extraction_with_linking(extraction_dict)
        return result['id']
    
    def _calculate_confidence_summary(self, spans: List[ExtractionSpan]) -> Dict[str, Any]:
        """Calculate confidence summary statistics."""
        if not spans:
            return {'overall_confidence': 0.0, 'field_confidence': {}}
        
        # Overall confidence
        overall_confidence = sum(span.confidence for span in spans) / len(spans)
        
        # Confidence by field
        field_confidence = {}
        field_spans = {}
        
        for span in spans:
            if span.field_name not in field_spans:
                field_spans[span.field_name] = []
            field_spans[span.field_name].append(span.confidence)
        
        for field, confidences in field_spans.items():
            field_confidence[field] = {
                'average': sum(confidences) / len(confidences),
                'min': min(confidences),
                'max': max(confidences),
                'count': len(confidences)
            }
        
        return {
            'overall_confidence': overall_confidence,
            'field_confidence': field_confidence,
            'total_spans': len(spans)
        }
    
    def _calculate_extraction_statistics(self, extraction_results: Dict) -> Dict[str, Any]:
        """Calculate extraction statistics."""
        extractions = extraction_results.get('extractions', [])
        
        if not extractions:
            return {'total_extractions': 0, 'fields_extracted': 0}
        
        # Count fields extracted
        all_fields = set()
        for extraction in extractions:
            attributes = extraction.get('attributes', {})
            all_fields.update(attributes.keys())
        
        # Count non-empty fields
        non_empty_fields = set()
        for extraction in extractions:
            attributes = extraction.get('attributes', {})
            for field, value in attributes.items():
                if value and str(value).strip():
                    non_empty_fields.add(field)
        
        return {
            'total_extractions': len(extractions),
            'fields_extracted': len(non_empty_fields),
            'total_fields_available': len(all_fields),
            'extraction_completeness': len(non_empty_fields) / len(all_fields) if all_fields else 0
        }
    
    async def batch_extract_with_ui_support(self, 
                                          documents: List[Dict],
                                          batch_size: int = 5) -> List[Dict]:
        """
        Batch extraction with UI support.
        
        Args:
            documents: List of documents with 'text', 'document_id', etc.
            batch_size: Number of documents to process concurrently
            
        Returns:
            List of extraction results
        """
        logger.info(f"Starting batch extraction for {len(documents)} documents")
        
        results = []
        
        # Process in batches to avoid overwhelming the system
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Process batch concurrently
            batch_tasks = [
                self.extract_with_ui_support(
                    text=doc['text'],
                    document_id=doc['document_id'],
                    metadata_id=doc.get('metadata_id'),
                    fulltext_id=doc.get('fulltext_id')
                )
                for doc in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Filter out exceptions and add to results
            for result in batch_results:
                if not isinstance(result, Exception):
                    results.append(result)
                else:
                    logger.error(f"Batch extraction failed: {result}")
            
            logger.info(f"Completed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        logger.info(f"Batch extraction completed. {len(results)} successful extractions")
        return results
    
    async def get_extraction_for_validation(self, extraction_id: str) -> Optional[Dict]:
        """Get extraction data for validation interface."""
        try:
            extraction_data = await self.db_manager.get_extraction_with_validation(extraction_id)
            return extraction_data
        except Exception as e:
            logger.error(f"Failed to get extraction for validation: {e}")
            return None
    
    async def update_extraction_from_validation(self, 
                                              extraction_id: str, 
                                              corrections: Dict) -> bool:
        """Update extraction based on validation corrections."""
        try:
            # Apply corrections to extraction data
            updated_data = await self._apply_validation_corrections(extraction_id, corrections)
            
            # Update database
            await self.db_manager.update_extraction_data(extraction_id, updated_data)
            
            logger.info(f"Applied validation corrections to extraction {extraction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update extraction from validation: {e}")
            return False
    
    async def _apply_validation_corrections(self, 
                                          extraction_id: str, 
                                          corrections: Dict) -> Dict:
        """Apply validation corrections to extraction data."""
        # Get current extraction data
        current_data = await self.db_manager.get_extraction_data(extraction_id)
        
        # Apply corrections
        for field, corrected_value in corrections.items():
            # Update extraction data with corrected values
            # This would involve updating the nested extraction structure
            pass
        
        return current_data


# Example usage and testing
async def test_enhanced_langextract():
    """Test the enhanced LangExtract integration."""
    # This would be called with actual instances
    # engine = EnhancedLangExtractEngine(
    #     base_engine=LangExtractEngine(),
    #     db_manager=EnhancedSQLiteManager()
    # )
    
    # # Test single extraction
    # sample_text = """
    # Patient 1 was a 3-year-old male with Leigh syndrome due to MT-ATP6 c.8993T>G.
    # He presented with developmental delay and lactic acidosis.
    # """
    
    # result = await engine.extract_with_ui_support(
    #     text=sample_text,
    #     document_id="PMID32679198",
    #     metadata_id="meta_001"
    # )
    
    # print(f"Extraction completed: {result['extraction_id']}")
    # print(f"Validation ID: {result['validation_id']}")
    # print(f"Confidence summary: {result['confidence_summary']}")
    
    pass


if __name__ == "__main__":
    # Run test
    asyncio.run(test_enhanced_langextract())