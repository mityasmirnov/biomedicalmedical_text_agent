"""
Simplified Enhanced Extraction Orchestrator - Fixed Version

This is a corrected version for testing basic functionality.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Core imports
from core.base import ProcessingResult, PatientRecord
from core.llm_client.openrouter_client import OpenRouterClient

# Simple agents
from agents.extraction_agents.demographics_agent import DemographicsAgent
from agents.extraction_agents.genetics_agent import GeneticsAgent
from agents.extraction_agents.phenotypes_agent_simple import SimplePhenotypesAgent
from agents.extraction_agents.treatments_agent import TreatmentsAgent

# Processors
from processors.pdf_parser import PDFParser
from processors.patient_segmenter import PatientSegmenter

# Database
from database.sqlite_manager import SQLiteManager


@dataclass
class SimpleExtractionConfig:
    """Simplified extraction configuration."""
    save_to_database: bool = True
    output_format: str = 'json'


@dataclass
class SimpleSystemStatus:
    """Simplified system status."""
    agents_loaded: bool
    database_ready: bool
    llm_client_ready: bool
    total_extractions: int
    system_health: str


class SimpleEnhancedOrchestrator:
    """Simplified enhanced orchestrator for testing."""
    
    def __init__(self, config: SimpleExtractionConfig = None):
        """Initialize simplified orchestrator."""
        self.config = config or SimpleExtractionConfig()
        
        # Initialize components
        self.llm_client = None
        self.agents = {}
        self.database_manager = None
        
        # Statistics
        self.extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'last_extraction': None
        }
        
        # Initialize system
        self._initialize_system()
        
        logging.info("Simple enhanced orchestrator initialized")
    
    def _initialize_system(self):
        """Initialize system components."""
        try:
            # Initialize LLM client
            self.llm_client = OpenRouterClient()
            logging.info("OpenRouter client initialized")
            
            # Initialize database manager
            self.database_manager = SQLiteManager()
            logging.info("Database manager initialized")
            
            # Initialize agents
            self._initialize_agents()
            
            logging.info("System initialization completed")
            
        except Exception as e:
            logging.error(f"System initialization failed: {e}")
            raise
    
    def _initialize_agents(self):
        """Initialize extraction agents."""
        try:
            self.agents['demographics'] = DemographicsAgent(llm_client=self.llm_client)
            self.agents['genetics'] = GeneticsAgent(llm_client=self.llm_client)
            self.agents['phenotypes'] = SimplePhenotypesAgent(llm_client=self.llm_client)
            self.agents['treatments'] = TreatmentsAgent(llm_client=self.llm_client)
            
            logging.info(f"Initialized {len(self.agents)} extraction agents")
            
        except Exception as e:
            logging.error(f"Agent initialization failed: {e}")
            raise
    
    async def extract_from_file(self, 
                              file_path: str, 
                              output_path: Optional[str] = None) -> ProcessingResult[List[PatientRecord]]:
        """Extract patient data from a file."""
        try:
            # Parse document
            pdf_parser = PDFParser()
            parse_result = pdf_parser.process(file_path)
            
            if not parse_result.success:
                return ProcessingResult(
                    success=False,
                    error=f"Failed to parse file: {parse_result.error}"
                )
            
            document = parse_result.data
            
            # Segment patients
            segmenter = PatientSegmenter()
            segment_result = segmenter.process(document)
            if not segment_result.success:
                return ProcessingResult(
                    success=False,
                    error=f"Failed to segment patients: {segment_result.error}"
                )
            segments = segment_result.data
            
            # Extract data from each segment
            all_records = []
            
            for i, segment in enumerate(segments):
                # Extract data using all agents
                record = await self._extract_from_segment(segment.content, f"segment_{i+1}")
                
                if record:
                    all_records.append(record)
            
            # Save results
            if output_path:
                await self._save_results(all_records, output_path)
            
            # Update statistics
            self._update_extraction_stats(len(all_records), True)
            
            return ProcessingResult(
                success=True,
                data=all_records,
                metadata={
                    'source_file': file_path,
                    'total_segments': len(segments),
                    'extracted_records': len(all_records),
                    'extraction_method': 'simple_enhanced_orchestrator'
                }
            )
            
        except Exception as e:
            logging.error(f"Extraction failed: {e}")
            self._update_extraction_stats(0, False)
            return ProcessingResult(
                success=False,
                error=f"Extraction failed: {str(e)}"
            )
    
    async def _extract_from_segment(self, 
                                   segment_text: str, 
                                   segment_id: str) -> Optional[PatientRecord]:
        """Extract data from a single patient segment."""
        try:
            # Create patient segment object for agents
            from processors.patient_segmenter import PatientSegment
            patient_segment = PatientSegment(
                patient_id=segment_id,
                content=segment_text,
                start_position=0,
                end_position=len(segment_text),
                confidence=1.0
            )
            
            # Extract demographics
            demographics_task = {"patient_segment": patient_segment}
            demographics_result = await self.agents['demographics'].execute(demographics_task)
            
            # Extract genetics
            genetics_task = {"patient_segment": patient_segment}
            genetics_result = await self.agents['genetics'].execute(genetics_task)
            
            # Extract phenotypes
            phenotypes_result = await self.agents['phenotypes'].extract_phenotypes(segment_text)
            
            # Extract treatments
            treatments_result = await self.agents['treatments'].extract(segment_text)
            
            # Combine all extractions
            combined_data = {}
            
            if demographics_result.success:
                combined_data.update(demographics_result.data)
            
            if genetics_result.success:
                combined_data.update(genetics_result.data)
            
            if phenotypes_result.success:
                # Extract phenotype data
                phenotype_data = phenotypes_result.data
                combined_data.update({
                    'phenotypes': phenotype_data.phenotypes,
                    'symptoms': phenotype_data.symptoms,
                    'diagnostic_findings': phenotype_data.diagnostic_findings,
                    'lab_values': phenotype_data.lab_values,
                    'imaging_findings': phenotype_data.imaging_findings
                })
            
            if treatments_result.success:
                combined_data.update(treatments_result.data)
            
            # Create patient record
            record = PatientRecord(
                patient_id=segment_id,
                data=combined_data,
                source_document_id=f"segment_{segment_id}",
                extraction_metadata={
                    'extraction_method': 'simple_enhanced_orchestrator',
                    'agents_used': list(self.agents.keys()),
                    'extraction_timestamp': datetime.now().isoformat()
                }
            )
            
            # Store in database if configured
            if self.config.save_to_database:
                try:
                    self.database_manager.store_patient_records([record])
                except Exception as e:
                    logging.warning(f"Failed to store record in database: {e}")
            
            return record
            
        except Exception as e:
            logging.error(f"Failed to extract from segment {segment_id}: {e}")
            return None
    
    async def _save_results(self, records: List[PatientRecord], output_path: str):
        """Save extraction results to file."""
        try:
            if output_path.endswith('.json'):
                # Save as JSON
                data = [record.data for record in records]
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                    
            elif output_path.endswith('.csv'):
                # Save as CSV
                import pandas as pd
                data = [record.data for record in records]
                df = pd.DataFrame(data)
                df.to_csv(output_path, index=False)
            
            logging.info(f"Results saved to {output_path}")
            
        except Exception as e:
            logging.error(f"Failed to save results: {e}")
    
    def _update_extraction_stats(self, count: int, success: bool):
        """Update extraction statistics."""
        self.extraction_stats['total_extractions'] += count
        if success:
            self.extraction_stats['successful_extractions'] += count
        else:
            self.extraction_stats['failed_extractions'] += 1
        
        self.extraction_stats['last_extraction'] = datetime.now().isoformat()
    
    def get_system_status(self) -> SimpleSystemStatus:
        """Get system status."""
        try:
            agents_loaded = len(self.agents) > 0
            database_ready = self.database_manager is not None
            llm_client_ready = self.llm_client is not None
            
            if all([agents_loaded, database_ready, llm_client_ready]):
                system_health = 'healthy'
            else:
                system_health = 'warning'
            
            return SimpleSystemStatus(
                agents_loaded=agents_loaded,
                database_ready=database_ready,
                llm_client_ready=llm_client_ready,
                total_extractions=self.extraction_stats['total_extractions'],
                system_health=system_health
            )
            
        except Exception as e:
            logging.error(f"Failed to get system status: {e}")
            return SimpleSystemStatus(
                agents_loaded=False,
                database_ready=False,
                llm_client_ready=False,
                total_extractions=0,
                system_health='error'
            )
    
    def display_system_status(self):
        """Display system status."""
        status = self.get_system_status()
        
        print("=" * 50)
        print("Simple Enhanced Orchestrator - System Status")
        print("=" * 50)
        print(f"Agents Loaded: {'✅' if status.agents_loaded else '❌'}")
        print(f"Database Ready: {'✅' if status.database_ready else '❌'}")
        print(f"LLM Client Ready: {'✅' if status.llm_client_ready else '❌'}")
        print(f"Total Extractions: {status.total_extractions}")
        print(f"System Health: {status.system_health}")
        print("=" * 50)
        
        if status.system_health == 'healthy':
            print("🎉 System is operational and ready for extraction!")
        elif status.system_health == 'warning':
            print("⚠️  System is operational but some components are missing")
        else:
            print("🚨 System has critical issues")


# Simple CLI interface
def main():
    """Simple CLI for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Enhanced Orchestrator CLI")
    parser.add_argument('command', choices=['status', 'extract'], help='Command to run')
    parser.add_argument('--input', '-i', help='Input file path (for extract command)')
    parser.add_argument('--output', '-o', help='Output file path (for extract command)')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        orchestrator = SimpleEnhancedOrchestrator()
        orchestrator.display_system_status()
    
    elif args.command == 'extract':
        if not args.input:
            print("Error: Input file path required for extract command")
            return
        
        orchestrator = SimpleEnhancedOrchestrator()
        result = asyncio.run(orchestrator.extract_from_file(args.input, args.output))
        
        if result.success:
            print(f"✅ Extraction completed: {len(result.data)} records extracted")
        else:
            print(f"❌ Extraction failed: {result.error}")


if __name__ == "__main__":
    main()
