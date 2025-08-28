"""
Basic Extraction Orchestrator Fallback

Provides basic extraction functionality when the enhanced version is not available.
This is a fallback implementation for backward compatibility.
"""

from __future__ import annotations

import re
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExtractionConfig:
    """Basic configuration for extraction process."""
    use_rag: bool = False
    use_feedback: bool = False
    use_prompt_optimization: bool = False
    validate_against_truth: bool = False
    ground_truth_path: Optional[str] = None
    output_format: str = 'json'
    save_to_database: bool = False
    batch_size: int = 5
    max_workers: int = 1


@dataclass
class SystemStatus:
    """Basic system status information."""
    agents_loaded: bool
    rag_system_ready: bool
    feedback_system_ready: bool
    prompt_optimizer_ready: bool
    database_ready: bool
    llm_clients_ready: List[str]
    hpo_manager_ready: bool
    gene_manager_ready: bool
    total_extractions: int
    last_extraction: Optional[str]
    system_health: str


class BasicExtractionOrchestrator:
    """Basic extraction orchestrator for fallback purposes."""
    
    def __init__(
        self,
        config: ExtractionConfig = None,
        llm_client_type: str = "auto"
    ):
        """Initialize basic orchestrator."""
        self.config = config or ExtractionConfig()
        self.llm_client_type = llm_client_type
        self.logger = logging.getLogger(__name__)
        
        # Basic statistics
        self.extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'last_extraction': None,
            'agent_performance': {}
        }
        
        self.logger.info("Basic extraction orchestrator initialized (fallback mode)")
    
    @staticmethod
    def split_patients(text: str) -> List[Tuple[str, str]]:
        """Split an article text into (patient_id, section) tuples."""
        pattern = re.compile(r"(Patient\s+\d+)", flags=re.IGNORECASE)
        matches = list(pattern.finditer(text))
        if not matches:
            return [("", text.strip())]
        sections = []
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            label = match.group(1).strip()
            section_text = text[start:end].strip()
            sections.append((label, section_text))
        return sections
    
    def extract_from_text(self, article_text: str) -> List[Dict[str, Any]]:
        """Basic text extraction implementation."""
        records = []
        for patient_label, section in self.split_patients(article_text):
            record = {
                "patient_id": patient_label or "unknown",
                "content": section,
                "extraction_method": "basic_orchestrator"
            }
            records.append(record)
        
        # Update statistics
        self.extraction_stats['total_extractions'] += len(records)
        self.extraction_stats['successful_extractions'] += len(records)
        self.extraction_stats['last_extraction'] = "text_extraction"
        
        return records
    
    async def extract_from_file(self, file_path: str, output_path: Optional[str] = None, validate: bool = False):
        """Basic file extraction implementation."""
        try:
            # Simple text extraction for now
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            records = self.extract_from_text(content)
            
            # Update statistics
            self.extraction_stats['total_extractions'] += len(records)
            self.extraction_stats['successful_extractions'] += len(records)
            self.extraction_stats['last_extraction'] = "file_extraction"
            
            return type('ProcessingResult', (), {
                'success': True,
                'data': records,
                'metadata': {
                    'source_file': file_path,
                    'extraction_method': 'basic_orchestrator'
                }
            })()
            
        except Exception as e:
            self.logger.error(f"Basic extraction failed: {e}")
            self.extraction_stats['failed_extractions'] += 1
            
            return type('ProcessingResult', (), {
                'success': False,
                'error': f"Basic extraction failed: {str(e)}"
            })()
    
    def get_system_status(self) -> SystemStatus:
        """Get basic system status."""
        return SystemStatus(
            agents_loaded=False,
            rag_system_ready=False,
            feedback_system_ready=False,
            prompt_optimizer_ready=False,
            database_ready=False,
            llm_clients_ready=[],
            hpo_manager_ready=False,
            gene_manager_ready=False,
            total_extractions=self.extraction_stats['total_extractions'],
            last_extraction=self.extraction_stats['last_extraction'],
            system_health='basic'
        )
    
    def display_system_status(self):
        """Display basic system status."""
        status = self.get_system_status()
        print(f"Basic Extraction Orchestrator Status:")
        print(f"- Total extractions: {status.total_extractions}")
        print(f"- Last extraction: {status.last_extraction or 'Never'}")
        print(f"- System health: {status.system_health}")
        print(f"- Note: Running in basic fallback mode")
