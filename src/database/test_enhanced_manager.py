#!/usr/bin/env python3
"""
Test script for EnhancedSQLiteManager to verify functionality preservation and enhancements.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.enhanced_sqlite_manager import EnhancedSQLiteManager, SQLiteManager
from src.database.sqlite_manager import SQLiteManager as OriginalSQLiteManager

def test_functionality_preservation():
    """Test that all original functionality is preserved."""
    print("Testing functionality preservation...")
    
    # Create temporary database for testing
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # Test enhanced manager
        enhanced_manager = EnhancedSQLiteManager(db_path)
        
        # Test document operations
        test_doc = {
            "id": "test_doc_1",
            "title": "Test Document",
            "pmid": 12345,
            "abstract": "Test abstract"
        }
        
        result = enhanced_manager.store_document(test_doc)
        assert result.success, f"Document storage failed: {result.error}"
        print("✓ Document storage works")
        
        # Test document retrieval
        docs = enhanced_manager.get_documents(limit=10)
        assert len(docs) > 0, "Document retrieval failed"
        print("✓ Document retrieval works")
        
        # Test patient record operations
        test_record = PatientRecord(
            id="test_patient_1",
            patient_id="P001",
            source_document_id="test_doc_1",
            pmid=12345,
            gene="TEST_GENE",
            phenotypes="Test phenotype"
        )
        
        result = enhanced_manager.store_patient_records([test_record])
        assert result.success, f"Patient record storage failed: {result.error}"
        print("✓ Patient record storage works")
        
        # Test patient record retrieval
        result = enhanced_manager.get_patient_records(gene="TEST_GENE")
        assert result.success, f"Patient record retrieval failed: {result.error}"
        assert len(result.data) > 0, "No patient records found"
        print("✓ Patient record retrieval works")
        
        # Test search functionality
        result = enhanced_manager.search_records("TEST_GENE")
        assert result.success, f"Search failed: {result.error}"
        print("✓ Search functionality works")
        
        # Test statistics
        result = enhanced_manager.get_statistics()
        assert result.success, f"Statistics failed: {result.error}"
        print("✓ Statistics functionality works")
        
        print("✓ All original functionality preserved!")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

def test_enhanced_functionality():
    """Test enhanced functionality beyond the original."""
    print("\nTesting enhanced functionality...")
    
    # Create temporary database for testing
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        enhanced_manager = EnhancedSQLiteManager(db_path)
        
        # Test batch operations
        test_records = []
        for i in range(5):
            test_records.append({
                "patient_id": f"P{i:03d}",
                "pmid": 1000 + i,
                "gene": f"GENE_{i}",
                "phenotypes": f"Phenotype {i}"
            })
        
        result = enhanced_manager.store_patient_records_batch(test_records)
        assert result.success, f"Batch storage failed: {result.error}"
        assert result.data["total_stored"] > 0, "No records stored in batch"
        print("✓ Batch operations work")
        
        # Test table info
        result = enhanced_manager.get_table_info()
        assert result.success, f"Table info failed: {result.error}"
        assert "patient_records" in result.data, "Patient records table not found"
        print("✓ Table info functionality works")
        
        # Test schema migration
        result = enhanced_manager.migrate_schema()
        assert result.success, f"Schema migration failed: {result.error}"
        print("✓ Schema migration works")
        
        # Test database optimization
        result = enhanced_manager.optimize_database()
        assert result.success, f"Database optimization failed: {result.error}"
        print("✓ Database optimization works")
        
        print("✓ All enhanced functionality works!")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

def test_backward_compatibility():
    """Test that the enhanced manager maintains backward compatibility."""
    print("\nTesting backward compatibility...")
    
    # Create temporary database for testing
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # Test that SQLiteManager class still works
        manager = SQLiteManager(db_path)
        
        # Test basic functionality
        test_doc = {
            "id": "compat_test",
            "title": "Compatibility Test",
            "pmid": 99999
        }
        
        result = manager.store_document(test_doc)
        assert result.success, "Backward compatibility failed"
        print("✓ Backward compatibility maintained")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

def test_schema_synchronization():
    """Test that the enhanced manager properly handles schema files."""
    print("\nTesting schema synchronization...")
    
    # Create temporary database for testing
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # Test with schema path
        schema_path = "data/schemas/table_schema.json"
        enhanced_manager = EnhancedSQLiteManager(db_path, schema_path)
        
        # Verify schema was loaded
        assert enhanced_manager.schema is not None, "Schema not loaded"
        assert "properties" in enhanced_manager.schema, "Schema properties not found"
        print("✓ Schema loading works")
        
        # Test schema validation
        valid_record = {
            "pmid": 12345,
            "patient_id": "TEST001",
            "sex": "m"  # Valid enum value
        }
        
        is_valid = enhanced_manager._validate_record_against_schema(valid_record)
        assert is_valid, "Valid record failed validation"
        print("✓ Schema validation works")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("Testing EnhancedSQLiteManager...")
    print("=" * 50)
    
    try:
        test_functionality_preservation()
        test_enhanced_functionality()
        test_backward_compatibility()
        test_schema_synchronization()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed! EnhancedSQLiteManager is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)