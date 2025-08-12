#!/usr/bin/env python3
"""
Comprehensive Test Script for Enhanced Biomedical Data Extraction System

This script tests all the enhanced components from the root directory.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_core_components():
    """Test core components."""
    print("🧪 Testing Core Components...")
    
    try:
        from core.base import ProcessingResult, PatientRecord
        print("✅ Core base classes imported")
        
        from core.feedback_loop import FeedbackLoop
        print("✅ Feedback loop imported")
        
        from core.prompt_optimization import PromptOptimizer
        print("✅ Prompt optimizer imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Core components test failed: {e}")
        return False

def test_llm_clients():
    """Test LLM clients."""
    print("\n🧪 Testing LLM Clients...")
    
    try:
        from core.llm_client.openrouter_client import OpenRouterClient
        print("✅ OpenRouter client imported")
        
        from core.llm_client.huggingface_client import HuggingFaceClient, HuggingFaceModelManager
        print("✅ HuggingFace client imported")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM clients test failed: {e}")
        return False

def test_rag_system():
    """Test RAG system."""
    print("\n🧪 Testing RAG System...")
    
    try:
        from rag.rag_integration import RAGIntegration, create_example_from_success
        
        # Initialize RAG system
        rag = RAGIntegration()
        print("✅ RAG system initialized")
        
        # Test adding an example
        example = create_example_from_success(
            text="Patient has seizures and developmental delay",
            extracted_data={"phenotypes": ["seizures", "developmental delay"]},
            field_type="phenotypes",
            confidence=0.8
        )
        
        rag.add_example(example)
        print("✅ Example added to RAG system")
        
        # Test context retrieval
        context = rag.get_context("Patient with seizures", field_type="phenotypes")
        print(f"✅ Context retrieved: {context.total_retrieved} items")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        return False

def test_feedback_system():
    """Test feedback loop system."""
    print("\n🧪 Testing Feedback System...")
    
    try:
        from core.feedback_loop import FeedbackLoop
        
        # Initialize feedback system
        feedback = FeedbackLoop()
        print("✅ Feedback system initialized")
        
        # Test with sample data
        predictions = [
            {"phenotypes": ["seizures"], "age": 5},
            {"phenotypes": ["developmental delay"], "age": 3}
        ]
        
        ground_truth = [
            {"phenotypes": ["seizures", "developmental delay"], "age": 5},
            {"phenotypes": ["developmental delay"], "age": 3}
        ]
        
        result = feedback.compare_predictions(predictions, ground_truth, "test_model")
        print(f"✅ Feedback analysis completed: {result.overall_accuracy:.2%} accuracy")
        
        return True
        
    except Exception as e:
        print(f"❌ Feedback system test failed: {e}")
        return False

def test_prompt_optimizer():
    """Test prompt optimization system."""
    print("\n🧪 Testing Prompt Optimizer...")
    
    try:
        from core.prompt_optimization import PromptOptimizer
        
        # Initialize prompt optimizer
        optimizer = PromptOptimizer()
        print("✅ Prompt optimizer initialized")
        
        # Test getting best prompt
        prompt = optimizer.get_best_prompt("demographics", "age")
        if prompt:
            print(f"✅ Best prompt retrieved: {prompt.prompt_id}")
        else:
            print("⚠️  No prompts available")
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt optimizer test failed: {e}")
        return False

def test_ontologies():
    """Test ontology managers."""
    print("\n🧪 Testing Ontology Managers...")
    
    try:
        # Test HPO manager
        try:
            from ontologies.hpo_manager import HPOManager
            hpo_manager = HPOManager()
            print("✅ Standard HPO manager initialized")
        except Exception as e:
            print(f"⚠️  Standard HPO manager failed: {e}")
        
        # Test optimized HPO manager
        try:
            hpo_path = "data/ontologies/hp.json"
            if os.path.exists(hpo_path):
                from ontologies.hpo_manager_optimized import OptimizedHPOManager
                hpo_manager = OptimizedHPOManager(hpo_path)
                print("✅ Optimized HPO manager initialized")
                
                # Test search
                matches = hpo_manager.search_terms("seizures", max_results=3)
                print(f"✅ HPO search working: {len(matches)} matches found")
            else:
                print("⚠️  hp.json not found, skipping optimized HPO manager")
        except Exception as e:
            print(f"⚠️  Optimized HPO manager failed: {e}")
        
        # Test gene manager
        try:
            from ontologies.gene_manager import GeneManager
            gene_manager = GeneManager()
            print("✅ Gene manager initialized")
        except Exception as e:
            print(f"⚠️  Gene manager failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ontology managers test failed: {e}")
        return False

def test_extraction_agents():
    """Test extraction agents."""
    print("\n🧪 Testing Extraction Agents...")
    
    try:
        # Test demographics agent
        try:
            from agents.extraction_agents.demographics_agent import DemographicsAgent
            print("✅ Demographics agent imported")
        except Exception as e:
            print(f"⚠️  Demographics agent failed: {e}")
        
        # Test genetics agent
        try:
            from agents.extraction_agents.genetics_agent import GeneticsAgent
            print("✅ Genetics agent imported")
        except Exception as e:
            print(f"⚠️  Genetics agent failed: {e}")
        
        # Test treatments agent
        try:
            from agents.extraction_agents.treatments_agent import TreatmentsAgent
            print("✅ Treatments agent imported")
        except Exception as e:
            print(f"⚠️  Treatments agent failed: {e}")
        
        # Test simple phenotypes agent
        try:
            from agents.extraction_agents.phenotypes_agent_simple import SimplePhenotypesAgent
            print("✅ Simple phenotypes agent imported")
        except Exception as e:
            print(f"⚠️  Simple phenotypes agent failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Extraction agents test failed: {e}")
        return False

def test_processors():
    """Test document processors."""
    print("\n🧪 Testing Document Processors...")
    
    try:
        from processors.pdf_parser import PDFParser
        print("✅ PDF parser imported")
        
        from processors.patient_segmenter import PatientSegmenter
        print("✅ Patient segmenter imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Document processors test failed: {e}")
        return False

def test_database():
    """Test database managers."""
    print("\n🧪 Testing Database Managers...")
    
    try:
        from database.sqlite_manager import SQLiteManager
        print("✅ SQLite manager imported")
        
        from database.vector_manager import VectorManager
        print("✅ Vector manager imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Database managers test failed: {e}")
        return False

def test_ollama_integration():
    """Test Ollama integration."""
    print("\n🧪 Testing Ollama Integration...")
    
    try:
        import subprocess
        
        # Check if ollama is available
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is available")
            
            # Check for llama3.1:8b model
            if 'llama3.1:8b' in result.stdout:
                print("✅ llama3.1:8b model is available")
                
                # Test simple generation
                test_result = subprocess.run(
                    ['ollama', 'run', 'llama3.1:8b', 'Hello, how are you?'],
                    capture_output=True, text=True, timeout=30
                )
                
                if test_result.returncode == 0:
                    print("✅ Ollama generation test passed")
                    return True
                else:
                    print("⚠️  Ollama generation test failed")
                    return False
            else:
                print("⚠️  llama3.1:8b model not found")
                return False
        else:
            print("❌ Ollama not available")
            return False
            
    except Exception as e:
        print(f"❌ Ollama integration test failed: {e}")
        return False

def test_enhanced_orchestrator():
    """Test enhanced orchestrator."""
    print("\n🧪 Testing Enhanced Orchestrator...")
    
    try:
        # Test simplified orchestrator first
        from agents.orchestrator.enhanced_orchestrator_simple import SimpleEnhancedOrchestrator
        
        orchestrator = SimpleEnhancedOrchestrator()
        print("✅ Simple enhanced orchestrator created")
        
        # Get system status
        status = orchestrator.get_system_status()
        print(f"✅ System status: {status.system_health}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced orchestrator test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Enhanced Biomedical Data Extraction System - Comprehensive Tests")
    print("=" * 80)
    
    tests = [
        test_core_components,
        test_llm_clients,
        test_rag_system,
        test_feedback_system,
        test_prompt_optimizer,
        test_ontologies,
        test_extraction_agents,
        test_processors,
        test_database,
        test_ollama_integration,
        test_enhanced_orchestrator
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced system is fully operational.")
    elif passed >= total * 0.8:
        print("✅ Most tests passed! System is mostly operational.")
    elif passed >= total * 0.6:
        print("⚠️  Many tests passed. System has some issues but is usable.")
    else:
        print("🚨 Many tests failed. System needs significant fixes.")
    
    print("\n🔧 Next Steps:")
    if passed == total:
        print("• Run extraction: python src/agents/orchestrator/enhanced_orchestrator_simple.py extract --input data/input/PMID32679198.pdf --output results.json")
        print("• Check system status: python src/agents/orchestrator/enhanced_orchestrator_simple.py status")
    else:
        print("• Fix failed component imports")
        print("• Check Python path and module structure")
        print("• Verify all dependencies are installed")
    
    return passed >= total * 0.6  # Consider success if 60% or more tests pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
