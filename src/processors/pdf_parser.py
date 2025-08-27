"""
PDF parsing module for the Biomedical Data Extraction Engine.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import fitz  # PyMuPDF

# Remove circular imports
# from core.base import BaseProcessor, Document, DocumentFormat, ProcessingResult
# from core.logging_config import get_logger

log = logging.getLogger(__name__)

# Simple classes to avoid circular imports
class Document:
    """Simple document class for PDF parsing."""
    def __init__(self, title: str, content: str, format: str, source_path: str, metadata: Dict[str, Any]):
        self.title = title
        self.content = content
        self.format = format
        self.source_path = source_path
        self.metadata = metadata

class ProcessingResult:
    """Simple processing result class for PDF parsing."""
    def __init__(self, success: bool, data: Any = None, error: str = None, metadata: Dict[str, Any] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}

class PDFParser:
    """PDF parser that extracts text and metadata from PDF documents."""
    
    def __init__(self, **kwargs):
        self.name = "pdf_parser"
        self.enable_table_extraction = kwargs.get("enable_table_extraction", False)
        self.preserve_formatting = kwargs.get("preserve_formatting", True)
    
    def process(self, input_data: str) -> ProcessingResult:
        """
        Process a PDF file and extract text content.
        
        Args:
            input_data: Path to the PDF file
            
        Returns:
            ProcessingResult containing the Document or error
        """
        try:
            pdf_path = Path(input_data)
            if not pdf_path.exists():
                return ProcessingResult(
                    success=False,
                    error=f"PDF file not found: {pdf_path}"
                )
            
            log.info(f"Processing PDF: {pdf_path}")
            
            # Extract text and metadata
            text_content = self._extract_text(pdf_path)
            metadata = self._extract_metadata(pdf_path)
            
            # Clean the extracted text
            cleaned_text = self._clean_text(text_content)
            
            # Create document
            document = Document(
                title=metadata.get("title", pdf_path.stem),
                content=cleaned_text,
                format="PDF",
                source_path=str(pdf_path),
                metadata=metadata
            )
            
            log.info(f"Successfully processed PDF: {pdf_path} ({len(cleaned_text)} characters)")
            
            return ProcessingResult(
                success=True,
                data=document
            )
            
        except Exception as e:
            log.error(f"Error processing PDF {input_data}: {str(e)}")
            return ProcessingResult(
                success=False,
                error=str(e)
            )
    
    def _extract_text(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyMuPDF."""
        text_content = ""
        
        try:
            doc = fitz.open(str(pdf_path))
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                if self.preserve_formatting:
                    # Extract text with layout preservation
                    text_dict = page.get_text("dict")
                    page_text = self._extract_text_from_dict(text_dict)
                else:
                    # Simple text extraction
                    page_text = page.get_text()
                
                text_content += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"
            
            doc.close()
            
        except Exception as e:
            log.error(f"Error extracting text from PDF: {str(e)}")
            raise
        
        return text_content
    
    def _extract_text_from_dict(self, text_dict: Dict) -> str:
        """Extract text from PyMuPDF text dictionary with formatting preservation."""
        text_lines = []
        
        for block in text_dict.get("blocks", []):
            if "lines" in block:  # Text block
                block_lines = []
                for line in block["lines"]:
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                    if line_text.strip():
                        block_lines.append(line_text.strip())
                
                if block_lines:
                    text_lines.append(" ".join(block_lines))
        
        return "\n".join(text_lines)
    
    def _extract_metadata(self, pdf_path: Path) -> Dict:
        """Extract metadata from PDF."""
        metadata = {
            "filename": pdf_path.name,
            "file_size": pdf_path.stat().st_size,
        }
        
        try:
            doc = fitz.open(str(pdf_path))
            
            # Basic document info
            metadata.update({
                "pages": len(doc),
                "pdf_metadata": doc.metadata
            })
            
            # Extract title from metadata or filename
            pdf_meta = doc.metadata
            if pdf_meta.get("title"):
                metadata["title"] = pdf_meta["title"]
            elif pdf_meta.get("subject"):
                metadata["title"] = pdf_meta["subject"]
            else:
                metadata["title"] = pdf_path.stem
            
            # Additional metadata
            if pdf_meta.get("author"):
                metadata["author"] = pdf_meta["author"]
            if pdf_meta.get("creator"):
                metadata["creator"] = pdf_meta["creator"]
            if pdf_meta.get("producer"):
                metadata["producer"] = pdf_meta["producer"]
            
            doc.close()
            
        except Exception as e:
            log.warning(f"Error extracting PDF metadata: {str(e)}")
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing artifacts and normalizing formatting."""
        if not text:
            return ""
        
        # Remove page markers
        text = re.sub(r'\n--- PAGE \d+ ---\n', '\n', text)
        
        # Remove standalone line numbers (common in academic papers)
        text = re.sub(r'(?m)^\s*\d+\s*$', '', text)
        
        # Fix hyphenated line breaks
        text = re.sub(r'-\s*\n\s*', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple newlines to double
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
        
        # Remove excessive whitespace at line beginnings/ends
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove empty lines at the beginning and end
        text = text.strip()
        
        return text
    
    def extract_tables(self, pdf_path: Path) -> List[Dict]:
        """Extract tables from PDF (placeholder for future implementation)."""
        # This would integrate with libraries like Camelot or Tabula
        # For now, return empty list
        log.info("Table extraction not implemented yet")
        return []
    
    def segment_by_sections(self, text: str) -> Dict[str, str]:
        """Segment text by sections based on headings."""
        sections = {}
        current_section = "introduction"
        current_text = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section heading
            if self._is_section_heading(line):
                # Save previous section
                if current_text:
                    sections[current_section] = '\n'.join(current_text)
                
                # Start new section
                current_section = self._normalize_section_name(line)
                current_text = []
            else:
                current_text.append(line)
        
        # Save last section
        if current_text:
            sections[current_section] = '\n'.join(current_text)
        
        return sections
    
    def _is_section_heading(self, line: str) -> bool:
        """Check if a line is likely a section heading."""
        # Common patterns for section headings
        patterns = [
            r'^\d+\.?\s+[A-Z][^.]*$',  # "1. Introduction" or "1 METHODS"
            r'^[A-Z][A-Z\s]+$',        # "INTRODUCTION" or "METHODS"
            r'^\d+\.\d+\.?\s+[A-Z]',   # "1.1. Background"
            r'^(Abstract|Introduction|Methods|Results|Discussion|Conclusion|References)$',
        ]
        
        return any(re.match(pattern, line, re.IGNORECASE) for pattern in patterns)
    
    def _normalize_section_name(self, heading: str) -> str:
        """Normalize section heading to a standard name."""
        heading = re.sub(r'^\d+\.?\s*', '', heading)  # Remove numbering
        heading = heading.lower().strip()
        
        # Map common variations
        mapping = {
            'abstract': 'abstract',
            'introduction': 'introduction',
            'background': 'introduction',
            'methods': 'methods',
            'methodology': 'methods',
            'materials and methods': 'methods',
            'results': 'results',
            'findings': 'results',
            'discussion': 'discussion',
            'conclusion': 'conclusion',
            'conclusions': 'conclusion',
            'references': 'references',
            'bibliography': 'references',
        }
        
        return mapping.get(heading, heading)

