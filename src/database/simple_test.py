#!/usr/bin/env python3
"""
Simple test script for EnhancedSQLiteManager that can run independently.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from enhanced_sqlite_manager import EnhancedSQLiteManager, PatientRecord
    print("✓ Successfully imported EnhancedSQLiteManager")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic functionality of the enhanced manager."""
    print("\nTesting basic functionality...")
    
    # Create temporary database for testing
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # Test initialization
        manager = EnhancedSQLiteManager(db_path)
        print("✓ EnhancedSQLiteManager initialized successfully")
        
        # Test document storage
        test_doc = {
            "id": "test_doc_1",
            "title": "Test Document",
            "pmid": 12345,
            "abstract": "Test abstract"
        }
        
        result = manager.store_document(test_doc)
        if result.success:
            print("✓ Document storage works")
        else:
            print(f"❌ Document storage failed: {result.error}")
            return False
        
        # Test document retrieval
        docs = manager.get_documents(limit=10)
        if len(docs) > 0:
            print("✓ Document retrieval works")
        else:
            print("❌ Document retrieval failed")
            return False
        
        # Test patient record storage
        test_record = PatientRecord(
            id="test_patient_1",
            patient_id="P001",
            source_document_id="test_doc_1",
            pmid=12345,
            gene="TEST_GENE",
            phenotypes="Test phenotype",
            sex=1,  # Add required attributes
            age_of_onset=25.0,
            age_at_diagnosis=25.0,
            age_at_death=None,
            ethnicity=None,
            consanguinity=None,
            mutations=None,
            inheritance=None,
            zygosity=None,
            parental_origin=None,
            genetic_testing=None,
            additional_genes=None,
            symptoms=None,
            diagnostic_findings=None,
            lab_values=None,
            imaging_findings=None,
            treatments=None,
            medications=None,
            dosages=None,
            treatment_response=None,
            adverse_events=None,
            survival_status=None,
            survival_time=None,
            cause_of_death=None,
            follow_up_duration=None,
            clinical_outcome=None,
            extraction_metadata=None,
            confidence_scores=None,
            validation_status=None
        )
        
        result = manager.store_patient_records([test_record])
        if result.success:
            print("✓ Patient record storage works")
        else:
            print(f"❌ Patient record storage failed: {result.error}")
            return False
        
        # Test patient record retrieval
        result = manager.get_patient_records(gene="TEST_GENE")
        if result.success and len(result.data) > 0:
            print("✓ Patient record retrieval works")
        else:
            print("❌ Patient record retrieval failed")
            return False
        
        # Test search functionality
        result = manager.search_records("TEST_GENE")
        if result.success:
            print("✓ Search functionality works")
        else:
            print(f"❌ Search failed: {result.error}")
            return False
        
        # Test statistics
        result = manager.get_statistics()
        if result.success:
            print("✓ Statistics functionality works")
        else:
            print(f"❌ Statistics failed: {result.error}")
            return False
        
        print("✓ All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

def test_enhanced_features():
    """Test enhanced features beyond the original."""
    print("\nTesting enhanced features...")
    
    # Create temporary database for testing
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        manager = EnhancedSQLiteManager(db_path)
        
        # Test batch operations
        test_records = []
        for i in range(5):
            test_records.append({
                "patient_id": f"P{i:03d}",
                "pmid": 1000 + i,
                "gene": f"GENE_{i}",
                "phenotypes": f"Phenotype {i}"
            })
        
        result = manager.store_patient_records_batch(test_records)
        if result.success and result.data["total_stored"] > 0:
            print("✓ Batch operations work")
        else:
            print(f"❌ Batch operations failed: {result.error}")
            return False
        
        # Test table info
        result = manager.get_table_info()
        if result.success and "patient_records" in result.data:
            print("✓ Table info functionality works")
        else:
            print(f"❌ Table info failed: {result.error}")
            return False
        
        # Test schema migration
        result = manager.migrate_schema()
        if result.success:
            print("✓ Schema migration works")
        else:
            print(f"❌ Schema migration failed: {result.error}")
            return False
        
        # Test database optimization
        result = manager.optimize_database()
        if result.success:
            print("✓ Database optimization works")
        else:
            print(f"❌ Database optimization failed: {result.error}")
            return False
        
        print("✓ All enhanced feature tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced features test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

def test_schema_integration():
    """Test schema integration features."""
    print("\nTesting schema integration...")
    
    # Create temporary database for testing
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # Test with schema path
        schema_path = "data/schemas/table_schema.json"
        if os.path.exists(schema_path):
            manager = EnhancedSQLiteManager(db_path, schema_path)
            
            # Verify schema was loaded
            if manager.schema is not None and "properties" in manager.schema:
                print("✓ Schema loading works")
            else:
                print("❌ Schema loading failed")
                return False
            
            # Test schema validation
            valid_record = {
                "pmid": 12345,
                "patient_id": "TEST001",
                "sex": "m"  # Valid enum value
            }
            
            is_valid = manager._validate_record_against_schema(valid_record)
            if is_valid:
                print("✓ Schema validation works")
            else:
                print("❌ Schema validation failed")
                return False
        else:
            print("⚠ Schema file not found, skipping schema tests")
            return True
        
        print("✓ All schema integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema integration test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("Testing EnhancedSQLiteManager...")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run all tests
    if not test_basic_functionality():
        all_tests_passed = False
    
    if not test_enhanced_features():
        all_tests_passed = False
    
    if not test_schema_integration():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    
    if all_tests_passed:
        print("✓ All tests passed! EnhancedSQLiteManager is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the output above.")
        sys.exit(1)