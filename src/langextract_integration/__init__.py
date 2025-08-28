"""
LangExtract integration for Biomedical Text Agent.

This module provides the primary extraction engine:
- Document extraction
- Data normalization
- Schema management
- Visualization tools
- Enhanced UI support with validation interface
"""

from .extractor import LangExtractEngine
from .normalizer import BiomedicNormalizer
from .schema_classes import (
    PatientRecord,
    Mutation,
    PhenotypeMention,
    TreatmentEvent,
    BiomedicExtractionClasses
)
from .visualizer import ExtractionVisualizer

# Import enhanced functionality if available
try:
    from .enhanced_langextract_integration import (
        EnhancedLangExtractEngine,
        TextHighlighter,
        ValidationInterface,
        ExtractionSpan,
        ValidationData
    )
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

__all__ = [
    'LangExtractEngine',
    'BiomedicNormalizer',
    'PatientRecord',
    'Mutation',
    'PhenotypeMention',
    'TreatmentEvent',
    'BiomedicExtractionClasses',
    'ExtractionVisualizer'
]

# Add enhanced exports if available
if ENHANCED_AVAILABLE:
    __all__.extend([
        'EnhancedLangExtractEngine',
        'TextHighlighter',
        'ValidationInterface',
        'ExtractionSpan',
        'ValidationData'
    ])

