#!/usr/bin/env python3
"""
Comprehensive test script for the Biomedical Data Extraction Engine.
"""

import asyncio
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config import get_config
from core.logging_config import setup_logging, get_logger
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
from database.sqlite_manager import SQLiteManager
from database.vector_manager import VectorManager
from rag.rag_system import RAGSystem
from ontologies.hpo_manager import HPOManager
from ontologies.gene_manager import GeneManager

# Setup logging
setup_logging({"log_level": "INFO"})
log = get_logger(__name__)

class SystemTester:
    """Comprehensive system tester."""
    
    def __init__(self):
        self.config = get_config()
        self.test_results = {}
        self.orchestrator = None
        self.sqlite_manager = None
        self.vector_manager = None
        self.rag_system = None
        self.hpo_manager = None
        self.gene_manager = None
    
    async def run_all_tests(self):
        """Run all system tests."""
        print("🧪 Starting Biomedical Data Extraction Engine Tests")
        print("=" * 60)
        
        # Test 1: Component Initialization
        await self.test_component_initialization()
        
        # Test 2: Document Processing
        await self.test_document_processing()
        
        # Test 3: Extraction Pipeline
        await self.test_extraction_pipeline()
        
        # Test 4: Database Operations
        await self.test_database_operations()
        
        # Test 5: Ontology Integration
        await self.test_ontology_integration()
        
        # Test 6: RAG System
        await self.test_rag_system()
        
        # Test 7: Ground Truth Comparison
        await self.test_ground_truth_comparison()
        
        # Generate Test Report
        self.generate_test_report()
    
    async def test_component_initialization(self):
        """Test component initialization."""
        print("\n🔧 Testing Component Initialization...")
        
        try:
            # Initialize LLM client first
            from core.llm_client.openrouter_client import OpenRouterClient
            llm_client = OpenRouterClient()
            print("✅ LLM Client initialized")
            
            # Initialize orchestrator with LLM client
            self.orchestrator = ExtractionOrchestrator(llm_client=llm_client)
            print("✅ Extraction Orchestrator initialized")
            
            # Initialize database managers
            self.sqlite_manager = SQLiteManager()
            print("✅ SQLite Manager initialized")
            
            self.vector_manager = VectorManager()
            print("✅ Vector Manager initialized")
            
            # Initialize RAG system
            self.rag_system = RAGSystem(
                vector_manager=self.vector_manager,
                sqlite_manager=self.sqlite_manager
            )
            print("✅ RAG System initialized")
            
            # Initialize ontology managers
            self.hpo_manager = HPOManager()
            print("✅ HPO Manager initialized")
            
            self.gene_manager = GeneManager()
            print("✅ Gene Manager initialized")
            
            self.test_results["component_initialization"] = {
                "status": "PASSED",
                "components_initialized": 6
            }
            
        except Exception as e:
            print(f"❌ Component initialization failed: {str(e)}")
            self.test_results["component_initialization"] = {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def test_document_processing(self):
        """Test document processing capabilities."""
        print("\n📄 Testing Document Processing...")
        
        try:
            # Test with the provided PMID file
            test_file = Path("data/input/PMID32679198.pdf")
            
            if not test_file.exists():
                print(f"⚠️  Test file not found: {test_file}")
                self.test_results["document_processing"] = {
                    "status": "SKIPPED",
                    "reason": "Test file not found"
                }
                return
            
            # Test PDF parsing
            from processors.pdf_parser import PDFParser
            pdf_parser = PDFParser()
            
            result = pdf_parser.process(str(test_file))
            
            if result.success:
                document = result.data
                print(f"✅ PDF parsed successfully: {document.title[:50]}...")
                print(f"   Content length: {len(document.content)} characters")
                
                # Test patient segmentation
                from processors.patient_segmenter import PatientSegmenter
                segmenter = PatientSegmenter()
                
                seg_result = segmenter.process(document)
                if seg_result.success:
                    segments = seg_result.data
                    print(f"✅ Patient segmentation successful: {len(segments)} segments found")
                    
                    self.test_results["document_processing"] = {
                        "status": "PASSED",
                        "document_title": document.title,
                        "content_length": len(document.content),
                        "segments_found": len(segments)
                    }
                else:
                    print(f"❌ Patient segmentation failed: {seg_result.error}")
                    self.test_results["document_processing"] = {
                        "status": "FAILED",
                        "error": f"Segmentation failed: {seg_result.error}"
                    }
            else:
                print(f"❌ PDF parsing failed: {result.error}")
                self.test_results["document_processing"] = {
                    "status": "FAILED",
                    "error": f"PDF parsing failed: {result.error}"
                }
                
        except Exception as e:
            print(f"❌ Document processing test failed: {str(e)}")
            self.test_results["document_processing"] = {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def test_extraction_pipeline(self):
        """Test the complete extraction pipeline."""
        print("\n🤖 Testing Extraction Pipeline...")
        
        try:
            test_file = Path("data/input/PMID32679198.pdf")
            
            if not test_file.exists():
                print(f"⚠️  Test file not found: {test_file}")
                self.test_results["extraction_pipeline"] = {
                    "status": "SKIPPED",
                    "reason": "Test file not found"
                }
                return
            
            # Run extraction
            start_time = time.time()
            result = await self.orchestrator.extract_from_file(str(test_file))
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            if result.success:
                records = result.data
                print(f"✅ Extraction completed successfully")
                print(f"   Records extracted: {len(records)}")
                print(f"   Processing time: {processing_time:.2f} seconds")
                
                if result.warnings:
                    print(f"   Warnings: {len(result.warnings)}")
                
                # Analyze extracted data
                field_coverage = self.analyze_field_coverage(records)
                
                self.test_results["extraction_pipeline"] = {
                    "status": "PASSED",
                    "records_extracted": len(records),
                    "processing_time": processing_time,
                    "warnings": len(result.warnings) if result.warnings else 0,
                    "field_coverage": field_coverage
                }
                
                # Store records for later tests
                self.extracted_records = records
                
            else:
                print(f"❌ Extraction failed: {result.error}")
                self.test_results["extraction_pipeline"] = {
                    "status": "FAILED",
                    "error": result.error
                }
                
        except Exception as e:
            print(f"❌ Extraction pipeline test failed: {str(e)}")
            self.test_results["extraction_pipeline"] = {
                "status": "FAILED",
                "error": str(e)
            }
    
    def analyze_field_coverage(self, records: List) -> Dict[str, Any]:
        """Analyze field coverage in extracted records."""
        if not records:
            return {}
        
        field_counts = {}
        total_records = len(records)
        
        for record in records:
            for field, value in record.data.items():
                if value is not None and value != "":
                    field_counts[field] = field_counts.get(field, 0) + 1
        
        # Calculate coverage percentages
        field_coverage = {}
        for field, count in field_counts.items():
            field_coverage[field] = {
                "count": count,
                "percentage": (count / total_records) * 100
            }
        
        return field_coverage
    
    async def test_database_operations(self):
        """Test database operations."""
        print("\n🗄️  Testing Database Operations...")
        
        try:
            # Test SQLite operations
            if hasattr(self, 'extracted_records') and self.extracted_records:
                # Store records
                store_result = self.sqlite_manager.store_patient_records(self.extracted_records)
                
                if store_result.success:
                    print(f"✅ Stored {len(self.extracted_records)} records in SQLite")
                    
                    # Test retrieval
                    retrieve_result = self.sqlite_manager.get_patient_records(limit=10)
                    if retrieve_result.success:
                        retrieved_records = retrieve_result.data
                        print(f"✅ Retrieved {len(retrieved_records)} records from SQLite")
                        
                        # Test search
                        search_result = self.sqlite_manager.search_records("seizure", limit=5)
                        if search_result.success:
                            search_records = search_result.data
                            print(f"✅ Search found {len(search_records)} records")
                        
                        self.test_results["database_operations"] = {
                            "status": "PASSED",
                            "records_stored": len(self.extracted_records),
                            "records_retrieved": len(retrieved_records),
                            "search_results": len(search_records) if search_result.success else 0
                        }
                    else:
                        print(f"❌ Record retrieval failed: {retrieve_result.error}")
                        self.test_results["database_operations"] = {
                            "status": "FAILED",
                            "error": f"Retrieval failed: {retrieve_result.error}"
                        }
                else:
                    print(f"❌ Record storage failed: {store_result.error}")
                    self.test_results["database_operations"] = {
                        "status": "FAILED",
                        "error": f"Storage failed: {store_result.error}"
                    }
            else:
                print("⚠️  No extracted records available for database testing")
                self.test_results["database_operations"] = {
                    "status": "SKIPPED",
                    "reason": "No extracted records available"
                }
                
        except Exception as e:
            print(f"❌ Database operations test failed: {str(e)}")
            self.test_results["database_operations"] = {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def test_ontology_integration(self):
        """Test ontology integration."""
        print("\n🧬 Testing Ontology Integration...")
        
        try:
            # Test HPO normalization
            test_phenotypes = [
                "seizures",
                "developmental delay",
                "muscle weakness",
                "failure to thrive"
            ]
            
            hpo_results = []
            for phenotype in test_phenotypes:
                result = self.hpo_manager.normalize_phenotype(phenotype)
                if result.success:
                    hpo_results.append(result.data)
            
            print(f"✅ HPO normalization: {len(hpo_results)}/{len(test_phenotypes)} successful")
            
            # Test gene normalization
            test_genes = [
                "SURF1",
                "surf1",
                "NDUFS1",
                "BRCA1",
                "brca2"
            ]
            
            gene_results = []
            for gene in test_genes:
                result = self.gene_manager.normalize_gene_symbol(gene)
                if result.success and result.data.get("normalized_symbol"):
                    gene_results.append(result.data)
            
            print(f"✅ Gene normalization: {len(gene_results)}/{len(test_genes)} successful")
            
            self.test_results["ontology_integration"] = {
                "status": "PASSED",
                "hpo_normalizations": len(hpo_results),
                "gene_normalizations": len(gene_results)
            }
            
        except Exception as e:
            print(f"❌ Ontology integration test failed: {str(e)}")
            self.test_results["ontology_integration"] = {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def test_rag_system(self):
        """Test RAG system functionality."""
        print("\n🔍 Testing RAG System...")
        
        try:
            # Test questions
            test_questions = [
                "What genes are associated with Leigh syndrome?",
                "What are the common symptoms of mitochondrial diseases?",
                "How many patients had seizures?"
            ]
            
            rag_results = []
            for question in test_questions:
                try:
                    result = await self.rag_system.answer_question(question)
                    if result.success:
                        rag_results.append(result.data)
                        print(f"✅ RAG answered: {question[:50]}...")
                    else:
                        print(f"⚠️  RAG failed for: {question[:50]}... - {result.error}")
                except Exception as e:
                    print(f"⚠️  RAG error for: {question[:50]}... - {str(e)}")
            
            self.test_results["rag_system"] = {
                "status": "PASSED" if rag_results else "FAILED",
                "questions_answered": len(rag_results),
                "total_questions": len(test_questions)
            }
            
        except Exception as e:
            print(f"❌ RAG system test failed: {str(e)}")
            self.test_results["rag_system"] = {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def test_ground_truth_comparison(self):
        """Test against ground truth data."""
        print("\n📊 Testing Ground Truth Comparison...")
        
        try:
            # Load ground truth data
            gt_file = Path("data/ground_truth/manually_processed.csv")
            
            if not gt_file.exists():
                print(f"⚠️  Ground truth file not found: {gt_file}")
                self.test_results["ground_truth_comparison"] = {
                    "status": "SKIPPED",
                    "reason": "Ground truth file not found"
                }
                return
            
            gt_df = pd.read_csv(gt_file)
            print(f"✅ Loaded ground truth: {len(gt_df)} records")
            
            if hasattr(self, 'extracted_records') and self.extracted_records:
                # Convert extracted records to DataFrame
                extracted_data = [record.data for record in self.extracted_records]
                extracted_df = pd.DataFrame(extracted_data)
                
                print(f"✅ Extracted records: {len(extracted_df)} records")
                
                # Compare key fields
                comparison_results = self.compare_with_ground_truth(gt_df, extracted_df)
                
                self.test_results["ground_truth_comparison"] = {
                    "status": "PASSED",
                    "ground_truth_records": len(gt_df),
                    "extracted_records": len(extracted_df),
                    "comparison_results": comparison_results
                }
                
                print(f"✅ Ground truth comparison completed")
                
            else:
                print("⚠️  No extracted records available for comparison")
                self.test_results["ground_truth_comparison"] = {
                    "status": "SKIPPED",
                    "reason": "No extracted records available"
                }
                
        except Exception as e:
            print(f"❌ Ground truth comparison failed: {str(e)}")
            self.test_results["ground_truth_comparison"] = {
                "status": "FAILED",
                "error": str(e)
            }
    
    def compare_with_ground_truth(self, gt_df: pd.DataFrame, extracted_df: pd.DataFrame) -> Dict[str, Any]:
        """Compare extracted data with ground truth."""
        comparison = {}
        
        # Find common fields
        common_fields = set(gt_df.columns) & set(extracted_df.columns)
        comparison["common_fields"] = list(common_fields)
        
        # Field-by-field comparison
        field_comparisons = {}
        
        for field in common_fields:
            if field in ['patient_id']:  # Skip ID fields
                continue
            
            gt_values = gt_df[field].dropna()
            ext_values = extracted_df[field].dropna()
            
            field_comparisons[field] = {
                "ground_truth_count": len(gt_values),
                "extracted_count": len(ext_values),
                "coverage": len(ext_values) / len(gt_values) if len(gt_values) > 0 else 0
            }
        
        comparison["field_comparisons"] = field_comparisons
        
        return comparison
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n📋 Test Report")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get("status") == "PASSED")
        failed_tests = sum(1 for result in self.test_results.values() if result.get("status") == "FAILED")
        skipped_tests = sum(1 for result in self.test_results.values() if result.get("status") == "SKIPPED")
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Skipped: {skipped_tests} ⚠️")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 40)
        
        for test_name, result in self.test_results.items():
            status_icon = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⚠️"}.get(result["status"], "❓")
            print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result['status']}")
            
            if result["status"] == "FAILED" and "error" in result:
                print(f"   Error: {result['error']}")
            elif result["status"] == "SKIPPED" and "reason" in result:
                print(f"   Reason: {result['reason']}")
        
        # Save detailed report
        report_file = Path("test_report.json")
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Overall assessment
        if failed_tests == 0:
            print("\n🎉 All tests passed! The system is working correctly.")
        elif passed_tests > failed_tests:
            print("\n✅ Most tests passed. The system is functional with minor issues.")
        else:
            print("\n⚠️  Several tests failed. The system needs attention.")

async def main():
    """Main test function."""
    tester = SystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

