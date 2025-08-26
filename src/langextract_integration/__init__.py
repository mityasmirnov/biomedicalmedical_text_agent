"""
LangExtract Integration Module

This module integrates Google's LangExtract library into the biomedical text agent
for structured information extraction with precise source grounding.

Key Features:
- Schema-aligned extraction classes
- Multi-pass extraction for improved recall
- Source grounding and visualization
- Integration with existing ontology managers
- OpenRouter API support for free models
"""

from .extractor import LangExtractEngine
from .extractor import extract_from_text, extract_from_file
from .schema_classes import (
    PatientRecord,
    Mutation,
    PhenotypeMention,
    TreatmentEvent,
    BiomedicExtractionClasses
)
from .normalizer import BiomedicNormalizer
from .visualizer import ExtractionVisualizer

__all__ = [
    'LangExtractEngine',
    'extract_from_text',
    'extract_from_file',
    'PatientRecord',
    'Mutation', 
    'PhenotypeMention',
    'TreatmentEvent',
    'BiomedicExtractionClasses',
    'BiomedicNormalizer',
    'ExtractionVisualizer'
]

