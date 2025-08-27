"""
Patient segmentation module for identifying and separating patient cases in documents.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

# Remove circular imports
# from core.base import BaseProcessor, Document, ProcessingResult
# from core.logging_config import get_logger

log = logging.getLogger(__name__)

@dataclass
class PatientSegment:
    """Represents a patient segment within a document."""
    patient_id: str
    content: str
    start_position: int
    end_position: int
    confidence: float
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class PatientSegmenter:
    """Segments documents into individual patient cases."""
    
    def __init__(self, **kwargs):
        self.name = "patient_segmenter"
        self.min_segment_length = kwargs.get("min_segment_length", 100)
        self.max_patients = kwargs.get("max_patients", 20)
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for patient identification."""
        # Explicit patient markers
        self.explicit_patterns = [
            re.compile(r'\b(?:Patient|Case|Subject|Individual)\s+(\d+|[A-Z])\b', re.IGNORECASE),
            re.compile(r'\b(?:P|C|S)(\d+)\b'),  # P1, C1, S1
            re.compile(r'\b(\d+)\.?\s*(?:Patient|Case|Subject)', re.IGNORECASE),
            re.compile(r'\b(?:Patient|Case)\s+([A-Z])\b', re.IGNORECASE),  # Patient A, Case B
        ]
        
        # Section-based patterns (numbered sections that might contain patients)
        self.section_patterns = [
            re.compile(r'^\s*(\d+)\.(\d+)\.?\s+(?:Patient|Case)', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\s*(\d+)\.(\d+)\s+[A-Z]', re.MULTILINE),  # 3.1 PATIENT, 3.2 CASE
        ]
        
        # Narrative patterns that suggest patient boundaries
        self.narrative_patterns = [
            re.compile(r'\b(?:A|An)\s+(\d+)[-\s](?:year|month)[-\s]old\s+(?:male|female|boy|girl|man|woman)', re.IGNORECASE),
            re.compile(r'\b(?:The|This)\s+(?:patient|case|subject|individual)', re.IGNORECASE),
            re.compile(r'\bpresented?\s+(?:with|at)', re.IGNORECASE),
        ]
    
    def process(self, input_data: Any) -> List[PatientSegment]:
        """
        Segment document into patient cases.
        
        Args:
            input_data: Document to segment (can be any object with .content attribute)
            
        Returns:
            List of PatientSegments
        """
        try:
            log.info(f"Segmenting document: {getattr(input_data, 'title', 'Unknown')}")
            
            # Try different segmentation strategies
            segments = []
            
            # Strategy 1: Explicit patient markers
            explicit_segments = self._segment_by_explicit_markers(input_data.content)
            if explicit_segments:
                segments = explicit_segments
                log.info(f"Found {len(segments)} segments using explicit markers")
            
            # Strategy 2: Section-based segmentation
            if not segments:
                section_segments = self._segment_by_sections(input_data.content)
                if section_segments:
                    segments = section_segments
                    log.info(f"Found {len(segments)} segments using section patterns")
            
            # Strategy 3: Narrative-based segmentation
            if not segments:
                narrative_segments = self._segment_by_narrative(input_data.content)
                if narrative_segments:
                    segments = narrative_segments
                    log.info(f"Found {len(segments)} segments using narrative patterns")
            
            # If no segments found, treat entire document as single patient
            if not segments:
                segments = [PatientSegment(
                    patient_id="Patient 1",
                    content=input_data.content,
                    start_position=0,
                    end_position=len(input_data.content),
                    confidence=0.5,
                    metadata={"method": "single_document"}
                )]
                log.info("No patient segments found, treating as single patient")
            
            # Filter and validate segments
            valid_segments = self._validate_segments(segments)
            
            # Add document metadata to segments
            for segment in valid_segments:
                segment.metadata.update({
                    "source_document_id": getattr(input_data, "id", "unknown"),
                    "source_title": getattr(input_data, "title", "Unknown Document"),
                    "document_format": getattr(input_data, "format", "unknown").value if hasattr(input_data, "format") else "unknown"
                })
            
            return valid_segments
            
        except Exception as e:
            log.error(f"Error segmenting document: {str(e)}")
            return []
    
    def _segment_by_explicit_markers(self, text: str) -> List[PatientSegment]:
        """Segment text using explicit patient markers."""
        segments = []
        matches = []
        
        # Find all explicit patient markers
        for pattern in self.explicit_patterns:
            for match in pattern.finditer(text):
                patient_id = match.group(1)
                matches.append((match.start(), match.end(), patient_id, match.group(0)))
        
        if not matches:
            return []
        
        # Sort matches by position
        matches.sort(key=lambda x: x[0])
        
        # Create segments between markers
        for i, (start, end, patient_id, marker) in enumerate(matches):
            # Determine segment boundaries
            segment_start = start
            if i + 1 < len(matches):
                segment_end = matches[i + 1][0]
            else:
                segment_end = len(text)
            
            # Extract segment content
            content = text[segment_start:segment_end].strip()
            
            if len(content) >= self.min_segment_length:
                segments.append(PatientSegment(
                    patient_id=f"Patient {patient_id}",
                    content=content,
                    start_position=segment_start,
                    end_position=segment_end,
                    confidence=0.9,
                    metadata={
                        "method": "explicit_markers",
                        "marker": marker,
                        "pattern_type": "explicit"
                    }
                ))
        
        return segments
    
    def _segment_by_sections(self, text: str) -> List[PatientSegment]:
        """Segment text using section-based patterns."""
        segments = []
        matches = []
        
        # Find section-based patient markers
        for pattern in self.section_patterns:
            for match in pattern.finditer(text):
                section_num = match.group(1)
                subsection_num = match.group(2) if match.lastindex >= 2 else "1"
                matches.append((match.start(), match.end(), f"{section_num}.{subsection_num}", match.group(0)))
        
        if not matches:
            return []
        
        # Sort matches by position
        matches.sort(key=lambda x: x[0])
        
        # Create segments
        for i, (start, end, section_id, marker) in enumerate(matches):
            segment_start = start
            if i + 1 < len(matches):
                segment_end = matches[i + 1][0]
            else:
                segment_end = len(text)
            
            content = text[segment_start:segment_end].strip()
            
            if len(content) >= self.min_segment_length:
                segments.append(PatientSegment(
                    patient_id=f"Patient {section_id}",
                    content=content,
                    start_position=segment_start,
                    end_position=segment_end,
                    confidence=0.8,
                    metadata={
                        "method": "section_based",
                        "marker": marker,
                        "section_id": section_id
                    }
                ))
        
        return segments
    
    def _segment_by_narrative(self, text: str) -> List[PatientSegment]:
        """Segment text using narrative patterns."""
        segments = []
        potential_starts = []
        
        # Find potential patient starts using narrative patterns
        for pattern in self.narrative_patterns:
            for match in pattern.finditer(text):
                potential_starts.append((match.start(), match.group(0)))
        
        if not potential_starts:
            return []
        
        # Sort by position
        potential_starts.sort(key=lambda x: x[0])
        
        # Create segments between potential starts
        for i, (start_pos, marker) in enumerate(potential_starts):
            if i + 1 < len(potential_starts):
                end_pos = potential_starts[i + 1][0]
            else:
                end_pos = len(text)
            
            content = text[start_pos:end_pos].strip()
            
            if len(content) >= self.min_segment_length:
                segments.append(PatientSegment(
                    patient_id=f"Patient {i + 1}",
                    content=content,
                    start_position=start_pos,
                    end_position=end_pos,
                    confidence=0.6,
                    metadata={
                        "method": "narrative_based",
                        "marker": marker,
                        "pattern_type": "narrative"
                    }
                ))
        
        return segments
    
    def _validate_segments(self, segments: List[PatientSegment]) -> List[PatientSegment]:
        """Validate and filter segments."""
        valid_segments = []
        
        for segment in segments:
            # Check minimum length
            if len(segment.content) < self.min_segment_length:
                log.debug(f"Segment {segment.patient_id} too short ({len(segment.content)} chars)")
                continue
            
            # Check for medical content indicators
            medical_indicators = [
                r'\b(?:patient|diagnosis|treatment|symptom|disease|condition)\b',
                r'\b(?:age|year|month|old|male|female)\b',
                r'\b(?:presented|admitted|diagnosed|treated)\b',
                r'\b(?:mg|kg|dose|therapy|medication)\b'
            ]
            
            has_medical_content = any(
                re.search(pattern, segment.content, re.IGNORECASE)
                for pattern in medical_indicators
            )
            
            if not has_medical_content:
                log.debug(f"Segment {segment.patient_id} lacks medical content")
                segment.confidence *= 0.5
            
            valid_segments.append(segment)
        
        # Limit number of segments
        if len(valid_segments) > self.max_patients:
            log.warning(f"Too many segments ({len(valid_segments)}), keeping top {self.max_patients}")
            valid_segments = sorted(valid_segments, key=lambda x: x.confidence, reverse=True)[:self.max_patients]
        
        return valid_segments
    
    def merge_segments(self, segments: List[PatientSegment], similarity_threshold: float = 0.8) -> List[PatientSegment]:
        """Merge similar segments that might represent the same patient."""
        # This is a placeholder for future implementation
        # Would use text similarity measures to identify duplicate patients
        return segments
    
    def get_segment_statistics(self, segments: List[PatientSegment]) -> Dict:
        """Get statistics about the segmentation."""
        if not segments:
            return {}
        
        return {
            "total_segments": len(segments),
            "avg_length": sum(len(s.content) for s in segments) / len(segments),
            "min_length": min(len(s.content) for s in segments),
            "max_length": max(len(s.content) for s in segments),
            "avg_confidence": sum(s.confidence for s in segments) / len(segments),
            "methods_used": list(set(s.metadata.get("method", "unknown") for s in segments))
        }

