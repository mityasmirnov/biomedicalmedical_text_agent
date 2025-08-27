"""
Document processing for Biomedical Text Agent.

This module provides document processing capabilities:
- PDF parsing and text extraction
- Patient case segmentation
- Document structure analysis
"""

from .pdf_parser import PDFParser
from .patient_segmenter import PatientSegmenter

__all__ = [
    'PDFParser',
    'PatientSegmenter'
]
