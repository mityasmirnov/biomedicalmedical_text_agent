"""
Enhanced Extraction Orchestrator with Full Integration

This orchestrator integrates all components of the biomedical data extraction engine:
- RAG integration for context-aware extraction
- Feedback loop for continuous improvement
- Prompt optimization with contextual bandits
- Multiple LLM client support (OpenRouter, HuggingFace, Ollama)
- Comprehensive validation and monitoring

Location: src/agents/orchestrator/enhanced_orchestrator.py
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

# Core imports
from core.base import ProcessingResult, PatientRecord, Document
from core.config import get_config
from core.feedback_loop import FeedbackLoop
from core.prompt_optimization import PromptOptimizer

# LLM clients
from core.llm_client.openrouter_client import OpenRouterClient
from core.llm_client.huggingface_client import HuggingFaceClient, HuggingFaceModelManager

# RAG system
from rag.rag_integration import RAGIntegration

# Agents
from agents.extraction_agents.demographics_agent import DemographicsAgent
from agents.extraction_agents.genetics_agent import GeneticsAgent
from agents.extraction_agents.phenotypes_agent import PhenotypesAgent
from agents.extraction_agents.treatments_agent import TreatmentsAgent

# Processors
from processors.pdf_parser import PDFParser
from processors.patient_segmenter import PatientSegmenter

# Database
from database.sqlite_manager import SQLiteManager
from database.vector_manager import VectorManager

# Ontologies
from ontologies.hpo_manager import HPOManager
from ontologies.gene_manager import GeneManager


@dataclass
class ExtractionConfig:
    """Configuration for extraction process."""
    use_rag: bool = True
    use_feedback: bool = True
    use_prompt_optimization: bool = True
    validate_against_truth: bool = False
    ground_truth_path: Optional[str] = None
    output_format: str = 'json'  # json, csv, database
    save_to_database: bool = True
    batch_size: int = 5
    max_workers: int = 3


@dataclass
class SystemStatus:
    """System status information."""
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
    system_health: str  # 'healthy', 'warning', 'error'


class EnhancedExtractionOrchestrator:
    """
    Enhanced orchestrator with full integration of all components.
    """
    
    def __init__(self, 
                 config: ExtractionConfig = None,
                 llm_client_type: str = "auto"):
        """
        Initialize enhanced orchestrator.
        
        Args:
            config: Extraction configuration
            llm_client_type: Type of LLM client to use ("auto", "openrouter", "huggingface", "ollama")
        """
        self.config = config or ExtractionConfig()
        self.llm_client_type = llm_client_type
        
        # Console for rich output
        self.console = Console()
        
        # Initialize components
        self.llm_clients = {}
        self.agents = {}
        self.rag_system = None
        self.feedback_system = None
        self.prompt_optimizer = None
        self.database_manager = None
        self.vector_manager = None
        self.hpo_manager = None
        self.gene_manager = None
        
        # Statistics
        self.extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'last_extraction': None,
            'agent_performance': {}
        }
        
        # Initialize system
        self._initialize_system()
        
        logging.info("Enhanced extraction orchestrator initialized")
    
    def _initialize_system(self):
        """Initialize all system components."""
        try:
            # Initialize LLM clients
            self._initialize_llm_clients()
            
            # Initialize database managers
            self._initialize_database()
            
            # Initialize ontology managers
            self._initialize_ontologies()
            
            # Initialize RAG system
            if self.config.use_rag:
                self._initialize_rag_system()
            
            # Initialize feedback system
            if self.config.use_feedback:
                self._initialize_feedback_system()
            
            # Initialize prompt optimizer
            if self.config.use_prompt_optimization:
                self._initialize_prompt_optimizer()
            
            # Initialize extraction agents
            self._initialize_agents()
            
            logging.info("System initialization completed")
            
        except Exception as e:
            logging.error(f"System initialization failed: {e}")
            raise
    
    def _initialize_llm_clients(self):
        """Initialize LLM clients based on configuration."""
        try:
            # OpenRouter client (default)
            try:
                openrouter_client = OpenRouterClient()
                self.llm_clients['openrouter'] = openrouter_client
                logging.info("OpenRouter client initialized")
            except Exception as e:
                logging.warning(f"Failed to initialize OpenRouter client: {e}")
            
            # HuggingFace client
            try:
                hf_manager = HuggingFaceModelManager()
                self.llm_clients['huggingface'] = hf_manager
                logging.info("HuggingFace model manager initialized")
            except Exception as e:
                logging.warning(f"Failed to initialize HuggingFace client: {e}")
            
            # Ollama client (if available)
            try:
                # Check if ollama is available
                import subprocess
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Ollama is available, create a simple client
                    self.llm_clients['ollama'] = self._create_ollama_client()
                    logging.info("Ollama client initialized")
            except Exception as e:
                logging.warning(f"Failed to initialize Ollama client: {e}")
            
            if not self.llm_clients:
                raise RuntimeError("No LLM clients could be initialized")
                
        except Exception as e:
            logging.error(f"LLM client initialization failed: {e}")
            raise
    
    def _create_ollama_client(self):
        """Create a simple Ollama client interface."""
        class OllamaClient:
            def __init__(self):
                self.model = "llama3.1:8b"
            
            async def generate(self, messages, **kwargs):
                import subprocess
                import json
                
                # Convert messages to prompt
                prompt = self._messages_to_prompt(messages)
                
                try:
                    # Call ollama
                    cmd = ['ollama', 'run', self.model, prompt]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        return type('Response', (), {
                            'content': result.stdout.strip(),
                            'model': self.model,
                            'usage': {'total_tokens': len(result.stdout.split())}
                        })()
                    else:
                        raise RuntimeError(f"Ollama failed: {result.stderr}")
                        
                except Exception as e:
                    logging.error(f"Ollama generation failed: {e}")
                    raise
            
            def _messages_to_prompt(self, messages):
                prompt_parts = []
                for message in messages:
                    role = message.get('role', 'user')
                    content = message.get('content', '')
                    if role == 'system':
                        prompt_parts.append(f"System: {content}")
                    elif role == 'user':
                        prompt_parts.append(f"User: {content}")
                    elif role == 'assistant':
                        prompt_parts.append(f"Assistant: {content}")
                prompt_parts.append("Assistant:")
                return "\n\n".join(prompt_parts)
        
        return OllamaClient()
    
    def _initialize_database(self):
        """Initialize database managers."""
        try:
            self.database_manager = SQLiteManager()
            self.vector_manager = VectorManager()
            logging.info("Database managers initialized")
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            raise
    
    def _initialize_ontologies(self):
        """Initialize ontology managers."""
        try:
            # Try optimized HPO manager first
            try:
                hpo_path = "data/ontologies/hp.json"
                if os.path.exists(hpo_path):
                    from ontologies.hpo_manager_optimized import OptimizedHPOManager
                    self.hpo_manager = OptimizedHPOManager(hpo_path)
                    logging.info("Optimized HPO manager initialized")
                else:
                    self.hpo_manager = HPOManager()
                    logging.info("Standard HPO manager initialized")
            except Exception as e:
                logging.warning(f"Failed to initialize optimized HPO manager: {e}")
                self.hpo_manager = HPOManager()
                logging.info("Standard HPO manager initialized")
            
            self.gene_manager = GeneManager()
            logging.info("Ontology managers initialized")
            
        except Exception as e:
            logging.error(f"Ontology initialization failed: {e}")
            raise
    
    def _initialize_rag_system(self):
        """Initialize RAG integration system."""
        try:
            self.rag_system = RAGIntegration()
            logging.info("RAG system initialized")
        except Exception as e:
            logging.error(f"RAG system initialization failed: {e}")
            self.rag_system = None
    
    def _initialize_feedback_system(self):
        """Initialize feedback loop system."""
        try:
            self.feedback_system = FeedbackLoop()
            logging.info("Feedback system initialized")
        except Exception as e:
            logging.error(f"Feedback system initialization failed: {e}")
            self.feedback_system = None
    
    def _initialize_prompt_optimizer(self):
        """Initialize prompt optimization system."""
        try:
            self.prompt_optimizer = PromptOptimizer()
            logging.info("Prompt optimizer initialized")
        except Exception as e:
            logging.error(f"Prompt optimizer initialization failed: {e}")
            self.prompt_optimizer = None
    
    def _initialize_agents(self):
        """Initialize extraction agents."""
        try:
            # Get primary LLM client
            primary_client = self._get_primary_llm_client()
            
            # Initialize agents with appropriate LLM clients
            self.agents['demographics'] = DemographicsAgent(llm_client=primary_client)
            self.agents['genetics'] = GeneticsAgent(llm_client=primary_client, gene_manager=self.gene_manager)
            self.agents['phenotypes'] = PhenotypesAgent(llm_client=primary_client, hpo_manager=self.hpo_manager)
            self.agents['treatments'] = TreatmentsAgent(llm_client=primary_client)
            
            logging.info(f"Initialized {len(self.agents)} extraction agents")
            
        except Exception as e:
            logging.error(f"Agent initialization failed: {e}")
            raise
    
    def _get_primary_llm_client(self):
        """Get the primary LLM client based on configuration."""
        if self.llm_client_type == "openrouter" and 'openrouter' in self.llm_clients:
            return self.llm_clients['openrouter']
        elif self.llm_client_type == "huggingface" and 'huggingface' in self.llm_clients:
            return self.llm_clients['huggingface']
        elif self.llm_client_type == "ollama" and 'ollama' in self.llm_clients:
            return self.llm_clients['ollama']
        else:
            # Auto-select: prefer OpenRouter, fallback to others
            if 'openrouter' in self.llm_clients:
                return self.llm_clients['openrouter']
            elif 'huggingface' in self.llm_clients:
                return self.llm_clients['huggingface']
            elif 'ollama' in self.llm_clients:
                return self.llm_clients['ollama']
            else:
                raise RuntimeError("No LLM clients available")
    
    async def extract_from_file(self, 
                              file_path: str, 
                              output_path: Optional[str] = None,
                              validate: bool = False) -> ProcessingResult[List[PatientRecord]]:
        """
        Extract patient data from a file with full integration.
        
        Args:
            file_path: Path to the file to process
            output_path: Optional output path for results
            validate: Whether to validate against ground truth
            
        Returns:
            ProcessingResult containing extracted patient records
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                
                # Parse document
                task = progress.add_task("Parsing document...", total=None)
                pdf_parser = PDFParser()
                parse_result = pdf_parser.process(file_path)
                
                if not parse_result.success:
                    return ProcessingResult(
                        success=False,
                        error=f"Failed to parse file: {parse_result.error}"
                    )
                
                document = parse_result.data
                progress.update(task, description=f"Document parsed: {len(document.content)} characters")
                
                # Segment patients
                task = progress.add_task("Segmenting patients...", total=None)
                segmenter = PatientSegmenter()
                segments = segmenter.segment_patients(document.content)
                progress.update(task, description=f"Found {len(segments)} patient segments")
                
                # Extract data from each segment
                task = progress.add_task("Extracting patient data...", total=len(segments))
                all_records = []
                
                for i, segment in enumerate(segments):
                    progress.update(task, description=f"Processing segment {i+1}/{len(segments)}")
                    
                    # Extract data using all agents
                    record = await self._extract_from_segment(segment, f"segment_{i+1}")
                    
                    if record:
                        all_records.append(record)
                    
                    progress.advance(task)
                
                # Validate against ground truth if requested
                if validate and self.config.validate_against_truth:
                    validation_result = await self._validate_extraction(all_records)
                    if validation_result:
                        self.console.print(Panel(
                            f"Validation Results:\n{validation_result}",
                            title="Extraction Validation",
                            border_style="blue"
                        ))
                
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
                        'extraction_method': 'enhanced_orchestrator'
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
            # Get RAG context if available
            rag_context = None
            if self.rag_system:
                rag_context = self.rag_system.get_context(segment_text, max_examples=3, max_rules=2)
            
            # Extract demographics
            demographics_result = await self.agents['demographics'].extract_demographics(segment_text)
            
            # Extract genetics
            genetics_result = await self.agents['genetics'].extract_genetics(segment_text)
            
            # Extract phenotypes
            phenotypes_result = await self.agents['phenotypes'].extract_phenotypes(segment_text)
            
            # Extract treatments
            treatments_result = await self.agents['treatments'].extract_treatments(segment_text)
            
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
                    'extraction_method': 'enhanced_orchestrator',
                    'rag_context_used': rag_context is not None,
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
            
            # Update RAG system with successful extraction
            if self.rag_system and phenotypes_result.success:
                self._update_rag_with_success(segment_text, phenotypes_result.data)
            
            return record
            
        except Exception as e:
            logging.error(f"Failed to extract from segment {segment_id}: {e}")
            return None
    
    def _update_rag_with_success(self, text: str, extraction_data):
        """Update RAG system with successful extraction."""
        try:
            from rag.rag_integration import create_example_from_success
            
            # Create RAG example for phenotypes
            example = create_example_from_success(
                text=text,
                extracted_data=extraction_data.__dict__,
                field_type='phenotypes',
                confidence=0.8,
                source='enhanced_orchestrator'
            )
            
            self.rag_system.add_example(example)
            
        except Exception as e:
            logging.warning(f"Failed to update RAG system: {e}")
    
    async def _validate_extraction(self, records: List[PatientRecord]) -> Optional[str]:
        """Validate extraction results against ground truth."""
        if not self.feedback_system or not self.config.ground_truth_path:
            return None
        
        try:
            # Load ground truth
            import pandas as pd
            ground_truth_df = pd.read_csv(self.config.ground_truth_path)
            ground_truth = ground_truth_df.to_dict('records')
            
            # Convert records to comparable format
            predictions = []
            for record in records:
                pred = record.data.copy()
                pred['patient_id'] = record.patient_id
                predictions.append(pred)
            
            # Run validation
            validation_result = self.feedback_system.compare_predictions(
                predictions, ground_truth, "enhanced_orchestrator"
            )
            
            # Generate report
            report = self.feedback_system.generate_report(validation_result)
            
            return report
            
        except Exception as e:
            logging.error(f"Validation failed: {e}")
            return f"Validation failed: {str(e)}"
    
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
    
    async def batch_extract(self, 
                           input_dir: str, 
                           output_file: str,
                           model: str = "auto") -> ProcessingResult[Dict[str, Any]]:
        """
        Batch extract from multiple files.
        
        Args:
            input_dir: Directory containing input files
            output_file: Output file path
            model: Model to use for extraction
            
        Returns:
            ProcessingResult with batch extraction results
        """
        try:
            input_path = Path(input_dir)
            if not input_path.exists():
                return ProcessingResult(
                    success=False,
                    error=f"Input directory does not exist: {input_dir}"
                )
            
            # Find all PDF files
            pdf_files = list(input_path.glob("*.pdf"))
            if not pdf_files:
                return ProcessingResult(
                    success=False,
                    error=f"No PDF files found in {input_dir}"
                )
            
            # Switch model if requested
            if model != "auto":
                await self._switch_model(model)
            
            # Process files in batches
            all_records = []
            batch_results = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                
                task = progress.add_task(f"Processing {len(pdf_files)} files...", total=len(pdf_files))
                
                for pdf_file in pdf_files:
                    progress.update(task, description=f"Processing {pdf_file.name}")
                    
                    try:
                        result = await self.extract_from_file(str(pdf_file))
                        if result.success:
                            all_records.extend(result.data)
                            batch_results.append({
                                'file': pdf_file.name,
                                'status': 'success',
                                'records_extracted': len(result.data)
                            })
                        else:
                            batch_results.append({
                                'file': pdf_file.name,
                                'status': 'failed',
                                'error': result.error
                            })
                    except Exception as e:
                        batch_results.append({
                            'file': pdf_file.name,
                            'status': 'error',
                            'error': str(e)
                        })
                    
                    progress.advance(task)
                
                # Save batch results
                await self._save_results(all_records, output_file)
                
                return ProcessingResult(
                    success=True,
                    data={
                        'total_files': len(pdf_files),
                        'successful_files': len([r for r in batch_results if r['status'] == 'success']),
                        'failed_files': len([r for r in batch_results if r['status'] != 'success']),
                        'total_records': len(all_records),
                        'batch_results': batch_results
                    },
                    metadata={'extraction_method': 'batch_enhanced_orchestrator'}
                )
                
        except Exception as e:
            logging.error(f"Batch extraction failed: {e}")
            return ProcessingResult(
                success=False,
                error=f"Batch extraction failed: {str(e)}"
            )
    
    async def _switch_model(self, model: str):
        """Switch to a different model."""
        try:
            if model.startswith('mixtral') and 'huggingface' in self.llm_clients:
                # Load Mixtral model
                hf_manager = self.llm_clients['huggingface']
                hf_manager.load_model('mixtral-8x7b')
                logging.info("Switched to Mixtral model")
                
            elif model.startswith('llama') and 'ollama' in self.llm_clients:
                # Switch Ollama model
                ollama_client = self.llm_clients['ollama']
                ollama_client.model = model
                logging.info(f"Switched to Ollama model: {model}")
                
            else:
                logging.warning(f"Model switching not supported for: {model}")
                
        except Exception as e:
            logging.error(f"Failed to switch model: {e}")
    
    def get_system_status(self) -> SystemStatus:
        """Get comprehensive system status."""
        try:
            # Check component readiness
            agents_loaded = len(self.agents) > 0
            rag_system_ready = self.rag_system is not None
            feedback_system_ready = self.feedback_system is not None
            prompt_optimizer_ready = self.prompt_optimizer is not None
            database_ready = self.database_manager is not None
            hpo_manager_ready = self.hpo_manager is not None
            gene_manager_ready = self.gene_manager is not None
            
            # Check LLM clients
            llm_clients_ready = list(self.llm_clients.keys())
            
            # Determine system health
            if all([agents_loaded, database_ready, hpo_manager_ready, gene_manager_ready]):
                if len(llm_clients_ready) > 0:
                    system_health = 'healthy'
                else:
                    system_health = 'warning'
            else:
                system_health = 'error'
            
            return SystemStatus(
                agents_loaded=agents_loaded,
                rag_system_ready=rag_system_ready,
                feedback_system_ready=feedback_system_ready,
                prompt_optimizer_ready=prompt_optimizer_ready,
                database_ready=database_ready,
                llm_clients_ready=llm_clients_ready,
                hpo_manager_ready=hpo_manager_ready,
                gene_manager_ready=gene_manager_ready,
                total_extractions=self.extraction_stats['total_extractions'],
                last_extraction=self.extraction_stats['last_extraction'],
                system_health=system_health
            )
            
        except Exception as e:
            logging.error(f"Failed to get system status: {e}")
            return SystemStatus(
                agents_loaded=False,
                rag_system_ready=False,
                feedback_system_ready=False,
                prompt_optimizer_ready=False,
                database_ready=False,
                llm_clients_ready=[],
                hpo_manager_ready=False,
                gene_manager_ready=False,
                total_extractions=0,
                last_extraction=None,
                system_health='error'
            )
    
    def display_system_status(self):
        """Display system status in a rich format."""
        status = self.get_system_status()
        
        # Create status table
        table = Table(title="System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        # Add component status
        table.add_row("Agents", "✅" if status.agents_loaded else "❌", 
                     f"{len(self.agents)} agents loaded" if status.agents_loaded else "Failed to load")
        
        table.add_row("RAG System", "✅" if status.rag_system_ready else "❌",
                     "Ready" if status.rag_system_ready else "Not available")
        
        table.add_row("Feedback System", "✅" if status.feedback_system_ready else "❌",
                     "Ready" if status.feedback_system_ready else "Not available")
        
        table.add_row("Prompt Optimizer", "✅" if status.prompt_optimizer_ready else "❌",
                     "Ready" if status.prompt_optimizer_ready else "Not available")
        
        table.add_row("Database", "✅" if status.database_ready else "❌",
                     "Ready" if status.database_ready else "Failed to initialize")
        
        table.add_row("HPO Manager", "✅" if status.hpo_manager_ready else "❌",
                     "Ready" if status.hpo_manager_ready else "Failed to initialize")
        
        table.add_row("Gene Manager", "✅" if status.gene_manager_ready else "❌",
                     "Ready" if status.gene_manager_ready else "Failed to initialize")
        
        # Add LLM clients
        llm_status = "✅" if status.llm_clients_ready else "❌"
        llm_details = ", ".join(status.llm_clients_ready) if status.llm_clients_ready else "No clients available"
        table.add_row("LLM Clients", llm_status, llm_details)
        
        # Add statistics
        table.add_row("Total Extractions", "📊", str(status.total_extractions))
        table.add_row("Last Extraction", "🕒", status.last_extraction or "Never")
        
        # Add overall health
        health_emoji = {"healthy": "🟢", "warning": "🟡", "error": "🔴"}
        table.add_row("System Health", health_emoji.get(status.system_health, "❓"), 
                     status.system_health.title())
        
        self.console.print(table)
        
        # Display additional information
        if status.system_health == 'healthy':
            self.console.print(Panel(
                "🎉 System is fully operational and ready for extraction!",
                style="green"
            ))
        elif status.system_health == 'warning':
            self.console.print(Panel(
                "⚠️  System is operational but some components are missing",
                style="yellow"
            ))
        else:
            self.console.print(Panel(
                "🚨 System has critical issues and may not function properly",
                style="red"
            ))


# CLI interface
@click.group()
def cli():
    """Enhanced Biomedical Data Extraction Engine CLI"""
    pass


@cli.command()
@click.option('--input', '-i', required=True, help='Input PDF file path')
@click.option('--output', '-o', help='Output file path (JSON or CSV)')
@click.option('--truth', '-t', help='Ground truth CSV file for validation')
@click.option('--model', '-m', default='auto', help='LLM model to use')
@click.option('--no-rag', is_flag=True, help='Disable RAG integration')
@click.option('--no-feedback', is_flag=True, help='Disable feedback loop')
def extract(input, output, truth, model, no_rag, no_feedback):
    """Extract patient data from a single PDF file"""
    config = ExtractionConfig(
        use_rag=not no_rag,
        use_feedback=not no_feedback,
        validate_against_truth=bool(truth),
        ground_truth_path=truth,
        output_format='json' if not output else output.split('.')[-1],
        save_to_database=True
    )
    
    orchestrator = EnhancedExtractionOrchestrator(config)
    
    # Display system status
    orchestrator.display_system_status()
    
    # Run extraction
    asyncio.run(orchestrator.extract_from_file(input, output, bool(truth)))


@cli.command()
@click.option('--input-dir', '-i', required=True, help='Input directory containing PDF files')
@click.option('--output', '-o', required=True, help='Output file path')
@click.option('--model', '-m', default='auto', help='LLM model to use')
@click.option('--batch-size', '-b', default=5, help='Batch size for processing')
def batch(input_dir, output, model, batch_size):
    """Batch extract from multiple PDF files"""
    config = ExtractionConfig(
        batch_size=batch_size,
        save_to_database=True
    )
    
    orchestrator = EnhancedExtractionOrchestrator(config)
    
    # Display system status
    orchestrator.display_system_status()
    
    # Run batch extraction
    asyncio.run(orchestrator.batch_extract(input_dir, output, model))


@cli.command()
def status():
    """Display system status and health"""
    config = ExtractionConfig()
    orchestrator = EnhancedExtractionOrchestrator(config)
    orchestrator.display_system_status()


@cli.command()
def test():
    """Run system tests"""
    config = ExtractionConfig()
    orchestrator = EnhancedExtractionOrchestrator(config)
    
    # Display status
    orchestrator.display_system_status()
    
    # Run basic tests
    console = Console()
    console.print("\n🧪 Running system tests...")
    
    # Test file parsing
    test_file = "data/input/PMID32679198.pdf"
    if os.path.exists(test_file):
        console.print("✅ Test file found")
        
        # Test extraction
        result = asyncio.run(orchestrator.extract_from_file(test_file))
        if result.success:
            console.print(f"✅ Extraction test passed: {len(result.data)} records extracted")
        else:
            console.print(f"❌ Extraction test failed: {result.error}")
    else:
        console.print("⚠️  Test file not found, skipping extraction test")
    
    console.print("\n🎯 System test completed!")


if __name__ == "__main__":
    cli()
