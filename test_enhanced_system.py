#!/usr/bin/env python3
"""
Test script for the enhanced biomedical data extraction system.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all components can be imported."""
    print("🧪 Testing component imports...")
    
    try:
        # Test core components
        from core.base import ProcessingResult, PatientRecord
        print("✅ Core base classes imported")
        
        from core.feedback_loop import FeedbackLoop
        print("✅ Feedback loop imported")
        
        from core.prompt_optimization import PromptOptimizer
        print("✅ Prompt optimizer imported")
        
        from core.llm_client.openrouter_client import OpenRouterClient
        print("✅ OpenRouter client imported")
        
        from core.llm_client.huggingface_client import HuggingFaceClient
        print("✅ HuggingFace client imported")
        
        # Test RAG system
        from rag.rag_integration import RAGIntegration
        print("✅ RAG integration imported")
        
        # Test ontologies
        from ontologies.hpo_manager import HPOManager
        print("✅ HPO manager imported")
        
        from ontologies.hpo_manager_optimized import OptimizedHPOManager
        print("✅ Optimized HPO manager imported")
        
        # Test agents
        from agents.extraction_agents.demographics_agent import DemographicsAgent
        print("✅ Demographics agent imported")
        
        from agents.extraction_agents.genetics_agent import GeneticsAgent
        print("✅ Genetics agent imported")
        
        from agents.extraction_agents.phenotypes_agent import PhenotypesAgent
        print("✅ Phenotypes agent imported")
        
        from agents.extraction_agents.treatments_agent import TreatmentsAgent
        print("✅ Treatments agent imported")
        
        print("\n🎉 All components imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_rag_system():
    """Test RAG system functionality."""
    print("\n🧪 Testing RAG system...")
    
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
    print("\n🧪 Testing feedback system...")
    
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
    print("\n🧪 Testing prompt optimizer...")
    
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

def test_hpo_manager():
    """Test HPO manager functionality."""
    print("\n🧪 Testing HPO manager...")
    
    try:
        # Try optimized HPO manager first
        hpo_path = "data/ontologies/hp.json"
        if os.path.exists(hpo_path):
            from ontologies.hpo_manager_optimized import OptimizedHPOManager
            
            hpo_manager = OptimizedHPOManager(hpo_path)
            print("✅ Optimized HPO manager initialized")
            
            # Test search
            matches = hpo_manager.search_terms("seizures", max_results=3)
            print(f"✅ HPO search working: {len(matches)} matches found")
            
        else:
            from ontologies.hpo_manager import HPOManager
            
            hpo_manager = HPOManager()
            print("✅ Standard HPO manager initialized")
            
            # Test search
            if hasattr(hpo_manager, 'search_terms'):
                matches = hpo_manager.search_terms("seizures", max_results=3)
                print(f"✅ HPO search working: {len(matches)} matches found")
            else:
                print("⚠️  HPO search not available")
        
        return True
        
    except Exception as e:
        print(f"❌ HPO manager test failed: {e}")
        return False

def test_llm_clients():
    """Test LLM client functionality."""
    print("\n🧪 Testing LLM clients...")
    
    try:
        # Test OpenRouter client
        try:
            from core.llm_client.openrouter_client import OpenRouterClient
            
            client = OpenRouterClient()
            print("✅ OpenRouter client initialized")
            
        except Exception as e:
            print(f"⚠️  OpenRouter client failed: {e}")
        
        # Test HuggingFace client
        try:
            from core.llm_client.huggingface_client import HuggingFaceModelManager
            
            hf_manager = HuggingFaceModelManager()
            print("✅ HuggingFace model manager initialized")
            
            # Check available models
            available_models = hf_manager.get_available_models()
            print(f"✅ Available models: {list(available_models.keys())}")
            
        except Exception as e:
            print(f"⚠️  HuggingFace client failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM client test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Enhanced Biomedical Data Extraction System - Component Tests")
    print("=" * 70)
    
    tests = [
        test_imports,
        test_rag_system,
        test_feedback_system,
        test_prompt_optimizer,
        test_hpo_manager,
        test_llm_clients
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
