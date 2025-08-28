"""
Test Enhanced LangExtract Integration

This module tests the enhanced LangExtract functionality including:
- Text highlighting
- Validation interface
- Database integration
- UI support features
"""

import asyncio
import pytest
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.langextract_integration import (
    LangExtractEngine,
    BiomedicNormalizer,
    PatientRecord,
    ExtractionVisualizer
)

# Import enhanced functionality
from src.langextract_integration.enhanced_langextract_integration import (
    EnhancedLangExtractEngine,
    TextHighlighter,
    ValidationInterface,
    ExtractionSpan,
    ValidationData
)

from src.database.sqlite_manager import SQLiteManager
from src.core.config import Config


class TestTextHighlighter:
    """Test text highlighting functionality."""
    
    def setup_method(self):
        self.highlighter = TextHighlighter()
    
    def test_highlight_extractions(self):
        """Test extraction highlighting."""
        text = "Patient 1 was a 3-year-old male with Leigh syndrome due to MT-ATP6 c.8993T>G."
        
        extraction_results = {
            'extractions': [{
                'extraction_text': text,
                'attributes': {
                    'patient_id': 'Patient 1',
                    'age_of_onset_years': '3',
                    'sex': 'male',
                    'gene': 'MT-ATP6',
                    'mutation': 'c.8993T>G',
                    'phenotype': 'Leigh syndrome'
                }
            }]
        }
        
        highlighted_html, spans = self.highlighter.highlight_extractions(text, extraction_results)
        
        # Check that we got spans
        assert len(spans) > 0
        
        # Check that spans have correct attributes
        for span in spans:
            assert hasattr(span, 'start')
            assert hasattr(span, 'end')
            assert hasattr(span, 'text')
            assert hasattr(span, 'extraction_type')
            assert hasattr(span, 'field_name')
            assert hasattr(span, 'confidence')
        
        # Check that HTML contains highlighting
        assert 'extraction-highlight' in highlighted_html
        assert 'style="background-color:' in highlighted_html
    
    def test_extraction_type_detection(self):
        """Test extraction type categorization."""
        assert self.highlighter._get_extraction_type('age_of_onset') == 'demographics'
        assert self.highlighter._get_extraction_type('gene_symbol') == 'genetics'
        assert self.highlighter._get_extraction_type('phenotype_hpo') == 'phenotypes'
        assert self.highlighter._get_extraction_type('treatment_drug') == 'treatments'
        assert self.highlighter._get_extraction_type('survival_status') == 'outcomes'
        assert self.highlighter._get_extraction_type('unknown_field') == 'default'
    
    def test_overlapping_spans_removal(self):
        """Test removal of overlapping spans."""
        spans = [
            ExtractionSpan(0, 10, "Patient 1", "demographics", "patient_id", 0.8),
            ExtractionSpan(5, 15, "1 was a", "demographics", "age", 0.7),  # Overlaps
            ExtractionSpan(20, 30, "3-year-old", "demographics", "age", 0.9),
        ]
        
        non_overlapping = self.highlighter._remove_overlapping_spans(spans)
        
        # Should keep first and third span
        assert len(non_overlapping) == 2
        assert non_overlapping[0].confidence == 0.8  # Kept higher confidence
        assert non_overlapping[1].start == 20


class TestValidationInterface:
    """Test validation interface functionality."""
    
    @pytest.fixture
    async def setup_validation(self):
        """Set up validation interface with database."""
        db_manager = SQLiteManager("data/database/test_validation.db")
        validation_interface = ValidationInterface(db_manager)
        
        # Clean up after test
        yield validation_interface, db_manager
        
        # Cleanup
        Path("data/database/test_validation.db").unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_prepare_validation_data(self, setup_validation):
        """Test validation data preparation."""
        validation_interface, _ = await setup_validation
        
        extraction_results = {
            'original_text': "Test patient text",
            'extractions': [{
                'attributes': {'patient_id': 'P1', 'age': '5'}
            }]
        }
        
        spans = [
            ExtractionSpan(0, 4, "Test", "demographics", "patient_id", 0.8),
            ExtractionSpan(5, 12, "patient", "demographics", "age", 0.7)
        ]
        
        validation_data = validation_interface.prepare_validation_data(
            extraction_results,
            "<span>Test patient</span> text",
            spans
        )
        
        assert validation_data.extraction_id.startswith("ext_")
        assert validation_data.original_text == "Test patient text"
        assert validation_data.highlighted_text == "<span>Test patient</span> text"
        assert len(validation_data.spans) == 2
        assert 'patient_id' in validation_data.confidence_scores
        assert 'age' in validation_data.confidence_scores
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_validation(self, setup_validation):
        """Test storing and retrieving validation data."""
        validation_interface, _ = await setup_validation
        
        validation_data = ValidationData(
            extraction_id="test_ext_001",
            original_text="Test text",
            highlighted_text="<span>Test</span> text",
            extractions=[{'test': 'data'}],
            spans=[],
            confidence_scores={'test': 0.9},
            validation_status="pending"
        )
        
        # Store validation data
        validation_id = await validation_interface.store_validation_data(validation_data)
        assert validation_id
        
        # Get validation queue
        queue = await validation_interface.get_validation_queue("pending")
        assert len(queue) > 0
        assert queue[0]['extraction_id'] == "test_ext_001"
    
    @pytest.mark.asyncio
    async def test_submit_validation(self, setup_validation):
        """Test validation submission."""
        validation_interface, _ = await setup_validation
        
        # First store some validation data
        validation_data = ValidationData(
            extraction_id="test_ext_002",
            original_text="Test text",
            highlighted_text="<span>Test</span> text",
            extractions=[],
            spans=[],
            confidence_scores={},
            validation_status="pending"
        )
        
        await validation_interface.store_validation_data(validation_data)
        
        # Submit validation
        success = await validation_interface.submit_validation(
            "test_ext_002",
            "validated",
            corrections={'field1': 'corrected_value'},
            validator_notes="Looks good"
        )
        
        assert success


class TestEnhancedLangExtractEngine:
    """Test enhanced LangExtract engine."""
    
    @pytest.fixture
    async def setup_engine(self):
        """Set up enhanced engine with dependencies."""
        # Mock base engine
        class MockBaseEngine:
            async def extract_from_text(self, text):
                return {
                    'extractions': [{
                        'extraction_text': text,
                        'attributes': {
                            'patient_id': 'Patient 1',
                            'age': '5 years',
                            'gene': 'MT-ATP6'
                        }
                    }]
                }
        
        db_manager = SQLiteManager("data/database/test_enhanced.db")
        base_engine = MockBaseEngine()
        
        enhanced_engine = EnhancedLangExtractEngine(
            base_engine=base_engine,
            db_manager=db_manager,
            model_id="test-model"
        )
        
        yield enhanced_engine
        
        # Cleanup
        Path("data/database/test_enhanced.db").unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_extract_with_ui_support(self, setup_engine):
        """Test extraction with UI support."""
        enhanced_engine = await setup_engine
        
        test_text = "Patient 1 is a 5-year-old child with MT-ATP6 mutation."
        
        result = await enhanced_engine.extract_with_ui_support(
            text=test_text,
            document_id="doc_001",
            metadata_id="meta_001"
        )
        
        # Check result structure
        assert 'extraction_id' in result
        assert 'validation_id' in result
        assert 'document_id' in result
        assert 'highlighted_text' in result
        assert 'spans' in result
        assert 'validation_data' in result
        assert 'confidence_summary' in result
        assert 'extraction_statistics' in result
        
        # Check highlighted text contains markup
        assert 'extraction-highlight' in result['highlighted_text']
        
        # Check confidence summary
        assert 'overall_confidence' in result['confidence_summary']
        assert 'field_confidence' in result['confidence_summary']
        
        # Check extraction statistics
        stats = result['extraction_statistics']
        assert stats['total_extractions'] == 1
        assert stats['fields_extracted'] > 0
    
    @pytest.mark.asyncio
    async def test_batch_extraction(self, setup_engine):
        """Test batch extraction with UI support."""
        enhanced_engine = await setup_engine
        
        documents = [
            {
                'text': 'Patient 1 with gene mutation.',
                'document_id': 'doc_001'
            },
            {
                'text': 'Patient 2 with different mutation.',
                'document_id': 'doc_002'
            }
        ]
        
        results = await enhanced_engine.batch_extract_with_ui_support(
            documents=documents,
            batch_size=2
        )
        
        assert len(results) == 2
        assert all('extraction_id' in r for r in results)
        assert all('validation_id' in r for r in results)


class TestIntegration:
    """Test full integration of enhanced LangExtract."""
    
    @pytest.mark.asyncio
    async def test_full_extraction_pipeline(self):
        """Test the complete extraction pipeline."""
        # This test would require actual LangExtract setup
        # For now, we verify the module imports and classes are available
        
        # Check all classes are importable
        assert LangExtractEngine
        assert BiomedicNormalizer
        assert PatientRecord
        assert ExtractionVisualizer
        assert EnhancedLangExtractEngine
        assert TextHighlighter
        assert ValidationInterface
        assert ExtractionSpan
        assert ValidationData
        
        # Check enhanced module has proper attributes
        from src.langextract_integration import ENHANCED_AVAILABLE
        assert ENHANCED_AVAILABLE
    
    def test_database_schema_compatibility(self):
        """Test that database schema supports validation tables."""
        db_manager = SQLiteManager("data/database/test_schema.db")
        
        # Initialize should create all necessary tables
        with db_manager.db_path.open('rb') as f:
            # Basic check that database was created
            assert f.read(16) == b'SQLite format 3\x00'
        
        # Cleanup
        Path("data/database/test_schema.db").unlink(missing_ok=True)


def test_basic_imports():
    """Test that all modules can be imported."""
    try:
        from src.langextract_integration import (
            LangExtractEngine,
            BiomedicNormalizer,
            EnhancedLangExtractEngine,
            TextHighlighter,
            ValidationInterface
        )
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])