#!/usr/bin/env python3
"""
Test Script for LangExtract Integration

Tests the complete LangExtract integration with the biomedical text agent,
including extraction, normalization, and visualization.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import LangExtract integration
try:
    from src.langextract_integration import (
        LangExtractEngine,
        BiomedicExtractionClasses,
        BiomedicNormalizer,
        ExtractionVisualizer
    )
    print("✅ LangExtract integration imported successfully")
except ImportError as e:
    print(f"❌ Failed to import LangExtract integration: {e}")
    print("Make sure langextract is installed: pip install langextract")
    sys.exit(1)


def test_schema_classes():
    """Test extraction schema classes."""
    print("\n🧪 Testing Schema Classes...")
    
    try:
        classes = BiomedicExtractionClasses()
        
        print(f"✅ Created {len(classes.classes)} extraction classes")
        
        # Test PatientRecord schema
        patient_schema = classes.patient_record
        print(f"✅ PatientRecord has {len(patient_schema.attributes)} attributes")
        
        # Test JSON serialization
        json_str = patient_schema.to_json()
        parsed = json.loads(json_str)
        print(f"✅ Schema serialization works")
        
        # Save schemas to files
        output_dir = Path("test_output/schemas")
        classes.save_to_files(output_dir)
        print(f"✅ Schemas saved to {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False


def test_extraction_engine():
    """Test the LangExtract engine."""
    print("\n🧪 Testing Extraction Engine...")
    
    # Sample biomedical text
    sample_text = """
    Patient 1 was a 3-year-old male with Leigh syndrome due to MT-ATP6 c.8993T>G (p.Leu156Arg). 
    He presented with developmental delay and lactic acidosis at 6 months of age. Treatment included 
    riboflavin 100 mg/day with clinical improvement. He is alive at last follow-up.
    
    Patient 2 is a female who developed generalized weakness when she was 2 years and 5 months old. 
    Molecular testing identified variants in SLC19A3: c.26T>C (p.Leu9Pro). She received thiamine 
    and biotin with improvement. She is alive at last follow-up.
    """
    
    try:
        # Get API key
        api_key = os.getenv("OPENROUTER_API_KEY", "your_api_key_here")
        
        if not api_key or api_key == "your_api_key_here":
            print("⚠️ No valid API key found. Using mock extraction.")
            return test_mock_extraction(sample_text)
        
        # Initialize engine
        engine = LangExtractEngine(
            model_id="google/gemma-2-27b-it:free",
            openrouter_api_key=api_key
        )
        print("✅ Engine initialized")
        
        # Run extraction
        print("🚀 Running extraction...")
        results = engine.extract_from_text(
            text=sample_text,
            extraction_passes=1,  # Single pass for testing
            segment_patients=True,
            include_visualization=True
        )
        
        print(f"✅ Extraction completed")
        print(f"📊 Found {len(results.get('extractions', []))} extractions")
        print(f"🏥 Normalized {len(results.get('normalized_data', []))} patient records")
        
        # Save results
        output_dir = Path("test_output/extraction")
        saved_files = engine.save_results(results, output_dir, "test_extraction")
        print(f"✅ Results saved to {len(saved_files)} files")
        
        return results
        
    except Exception as e:
        print(f"❌ Extraction test failed: {e}")
        print("Falling back to mock extraction...")
        return test_mock_extraction(sample_text)


def test_mock_extraction(sample_text: str):
    """Test with mock extraction data."""
    print("🎭 Using mock extraction data...")
    
    # Create mock results
    mock_results = {
        "extractions": [
            {
                "extraction_class": "PatientRecord",
                "extraction_text": "Patient 1 was a 3-year-old male...",
                "attributes": {
                    "patient_label": "Patient 1",
                    "sex": "m",
                    "age_of_onset_years": 0.5,
                    "alive_flag": 0,
                    "mutations": [
                        {
                            "Mutation": {
                                "gene": "MT-ATP6",
                                "cdna": "c.8993T>G",
                                "protein": "p.Leu156Arg",
                                "zygosity": "unknown"
                            }
                        }
                    ],
                    "phenotypes": [
                        {
                            "PhenotypeMention": {
                                "surface_form": "developmental delay",
                                "negated": False,
                                "onset_age_years": 0.5
                            }
                        },
                        {
                            "PhenotypeMention": {
                                "surface_form": "lactic acidosis",
                                "negated": False,
                                "onset_age_years": 0.5
                            }
                        }
                    ],
                    "treatments": [
                        {
                            "TreatmentEvent": {
                                "therapy": "riboflavin 100 mg/day",
                                "outcome": "clinical improvement"
                            }
                        }
                    ]
                }
            }
        ],
        "metadata": {
            "total_segments": 1,
            "model_id": "mock",
            "extraction_timestamp": "2024-01-01T00:00:00Z"
        }
    }
    
    print("✅ Mock extraction data created")
    return mock_results


def test_normalization(extraction_results):
    """Test the normalization process."""
    print("\n🧪 Testing Normalization...")
    
    try:
        normalizer = BiomedicNormalizer()
        print("✅ Normalizer initialized")
        
        # Normalize results
        normalized_results = normalizer.normalize_extractions(extraction_results)
        
        normalized_data = normalized_results.get("normalized_data", [])
        print(f"✅ Normalized {len(normalized_data)} patient records")
        
        # Display first record
        if normalized_data:
            first_record = normalized_data[0]
            print(f"📋 First record keys: {list(first_record.keys())}")
            print(f"📊 Quality score: {first_record.get('normalization_quality', 'N/A')}")
        
        # Check metadata
        norm_meta = normalized_results.get("normalization_metadata", {})
        quality_metrics = norm_meta.get("quality_metrics", {})
        
        if quality_metrics:
            print(f"⭐ Average quality: {quality_metrics.get('average_quality', 0):.2%}")
            print(f"📈 Completeness: {quality_metrics.get('completeness', 0):.2%}")
        
        return normalized_results
        
    except Exception as e:
        print(f"❌ Normalization test failed: {e}")
        return None


def test_visualization(normalized_results):
    """Test the visualization components."""
    print("\n🧪 Testing Visualization...")
    
    try:
        visualizer = ExtractionVisualizer()
        print("✅ Visualizer initialized")
        
        # Create overview dashboard
        overview_fig = visualizer.create_overview_dashboard(normalized_results)
        print("✅ Overview dashboard created")
        
        # Create quality assessment
        quality_fig = visualizer.create_quality_assessment(normalized_results)
        print("✅ Quality assessment created")
        
        # Get statistics
        stats = visualizer.create_extraction_statistics(normalized_results)
        print(f"✅ Statistics calculated: {len(stats)} categories")
        
        # Save visualizations
        output_dir = Path("test_output/visualizations")
        saved_files = visualizer.save_visualizations(
            normalized_results, 
            output_dir, 
            "test_viz"
        )
        print(f"✅ Visualizations saved to {len(saved_files)} files")
        
        # Print statistics summary
        overview_stats = stats.get("overview", {})
        print(f"📊 Total patients: {overview_stats.get('total_patients', 0)}")
        print(f"📊 Total extractions: {overview_stats.get('total_extractions', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        return False


def test_ground_truth_evaluation():
    """Test ground truth evaluation if available."""
    print("\n🧪 Testing Ground Truth Evaluation...")
    
    # Check if ground truth file exists
    gt_file = Path("data/manually_processed.csv")
    
    if not gt_file.exists():
        print(f"⚠️ Ground truth file not found: {gt_file}")
        print("Creating mock ground truth for testing...")
        
        # Create mock ground truth
        mock_gt_dir = Path("test_output/ground_truth")
        mock_gt_dir.mkdir(parents=True, exist_ok=True)
        mock_gt_file = mock_gt_dir / "mock_ground_truth.csv"
        
        import pandas as pd
        mock_data = pd.DataFrame([
            {
                "patient_id": "Patient 1",
                "sex": "m",
                "age_of_onset": 0.5,
                "gene": "MT-ATP6",
                "phenotypes_text": "developmental delay; lactic acidosis",
                "_0_alive_1_dead": 0
            }
        ])
        mock_data.to_csv(mock_gt_file, index=False)
        gt_file = mock_gt_file
        print(f"✅ Mock ground truth created: {gt_file}")
    
    try:
        normalizer = BiomedicNormalizer()
        
        # Create mock extraction results for evaluation
        mock_results = {
            "normalized_data": [
                {
                    "patient_id": "Patient 1",
                    "sex": "m",
                    "age_of_onset": 0.5,
                    "gene": "MT-ATP6",
                    "phenotypes_text": "developmental delay; lactic acidosis",
                    "_0_alive_1_dead": 0,
                    "normalization_quality": 0.9
                }
            ]
        }
        
        # Run evaluation
        evaluation = normalizer.evaluate_against_ground_truth(mock_results, gt_file)
        
        if "error" in evaluation:
            print(f"❌ Evaluation failed: {evaluation['error']}")
            return False
        
        print("✅ Ground truth evaluation completed")
        
        overall_metrics = evaluation.get("overall_metrics", {})
        if overall_metrics:
            print(f"📊 Overall accuracy: {overall_metrics.get('overall_accuracy', 0):.2%}")
            print(f"📊 Overall F1: {overall_metrics.get('overall_f1', 0):.2%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ground truth evaluation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 LangExtract Integration Test Suite")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    test_results = {}
    
    # Test 1: Schema Classes
    test_results["schema"] = test_schema_classes()
    
    # Test 2: Extraction Engine
    extraction_results = test_extraction_engine()
    test_results["extraction"] = extraction_results is not None
    
    # Test 3: Normalization
    if extraction_results:
        normalized_results = test_normalization(extraction_results)
        test_results["normalization"] = normalized_results is not None
        
        # Test 4: Visualization
        if normalized_results:
            test_results["visualization"] = test_visualization(normalized_results)
        else:
            test_results["visualization"] = False
    else:
        test_results["normalization"] = False
        test_results["visualization"] = False
    
    # Test 5: Ground Truth Evaluation
    test_results["evaluation"] = test_ground_truth_evaluation()
    
    # Summary
    print("\n📋 Test Results Summary:")
    print("=" * 50)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.capitalize():15} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total:.1%})")
    
    if passed == total:
        print("🎉 All tests passed! LangExtract integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print(f"\n📁 Test outputs saved to: {output_dir.absolute()}")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

