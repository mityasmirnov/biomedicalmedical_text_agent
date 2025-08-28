# Enhanced SQLite Manager

## Overview

The `EnhancedSQLiteManager` is an improved version of the original `SQLiteManager` that preserves all existing functionality while adding new features for better data management, schema validation, and performance optimization.

## Key Features

### ✅ Preserved Functionality
All methods from the original `sqlite_manager.py` are fully preserved:

- **Document Management**: `store_document()`, `get_documents()`, `get_documents_by_pmid()`
- **Patient Records**: `store_patient_records()`, `get_patient_records()`, `search_records()`
- **Statistics & Export**: `get_statistics()`, `export_to_csv()`
- **Database Operations**: All CRUD operations and querying capabilities

### 🚀 Enhanced Features

#### 1. Schema Integration & Validation
- **Automatic Schema Loading**: Loads JSON schema files for validation
- **Field Type Validation**: Validates data types against schema definitions
- **Enum Validation**: Enforces enum constraints from schema
- **Dynamic Table Creation**: Automatically creates tables with all schema fields

#### 2. Performance Optimizations
- **WAL Mode**: Enables Write-Ahead Logging for better concurrent access
- **Enhanced Indexing**: Additional indexes for common query patterns
- **Batch Operations**: Process large datasets efficiently
- **Database Optimization**: Built-in ANALYZE, VACUUM, and PRAGMA optimization

#### 3. Advanced Data Management
- **Batch Storage**: `store_patient_records_batch()` for efficient bulk operations
- **Schema Migration**: `migrate_schema()` for evolving database schemas
- **Data Validation**: Automatic validation against JSON schemas
- **Flexible Field Handling**: Automatically handles missing or extra fields

#### 4. Database Maintenance
- **Table Information**: `get_table_info()` for detailed schema inspection
- **Database Backup**: `backup_database()` for data safety
- **Performance Monitoring**: Built-in statistics and optimization tools

## Usage

### Basic Usage (Same as Original)

```python
from src.database.enhanced_sqlite_manager import EnhancedSQLiteManager

# Initialize with default settings
manager = EnhancedSQLiteManager()

# Use all original methods
result = manager.store_document(document_data)
records = manager.get_patient_records(gene="BRCA1")
stats = manager.get_statistics()
```

### Enhanced Features

```python
# Initialize with custom schema
manager = EnhancedSQLiteManager(
    db_path="data/custom.db",
    schema_path="data/schemas/custom_schema.json"
)

# Batch operations for large datasets
test_records = [
    {"patient_id": "P001", "pmid": 12345, "gene": "GENE1"},
    {"patient_id": "P002", "pmid": 12346, "gene": "GENE2"},
    # ... more records
]

result = manager.store_patient_records_batch(test_records)
print(f"Stored {result.data['total_stored']} records")

# Schema migration
migration_result = manager.migrate_schema("data/schemas/new_schema.json")
print(f"Added {migration_result.data['columns_added']} new columns")

# Database optimization
manager.optimize_database()

# Get detailed table information
table_info = manager.get_table_info()
for table_name, info in table_info.data.items():
    print(f"Table: {table_name}, Rows: {info['row_count']}")

# Create database backup
backup_result = manager.backup_database("backups/db_backup.db")
```

### Backward Compatibility

The enhanced manager maintains full backward compatibility:

```python
# This still works exactly as before
from src.database import SQLiteManager

manager = SQLiteManager()  # Uses EnhancedSQLiteManager under the hood
result = manager.store_document(document_data)
```

## Schema Integration

### Automatic Schema Loading

The enhanced manager automatically loads JSON schema files and creates database tables that match the schema structure:

```json
{
  "properties": {
    "pmid": {"type": "number"},
    "patient_id": {"type": "string"},
    "sex": {"type": "string", "enum": ["m", "f"]},
    "age_of_onset": {"type": "number"}
  }
}
```

### Schema Validation

Records are automatically validated against the loaded schema:

```python
# Valid record (passes validation)
valid_record = {
    "pmid": 12345,
    "patient_id": "P001",
    "sex": "m",  # Valid enum value
    "age_of_onset": 25.5
}

# Invalid record (fails validation)
invalid_record = {
    "pmid": 12345,
    "patient_id": "P001",
    "sex": "invalid",  # Invalid enum value
    "age_of_onset": "not_a_number"  # Wrong type
}
```

## Performance Features

### WAL Mode
- Enables concurrent read/write operations
- Better performance for multi-user scenarios
- Automatic journal management

### Enhanced Indexing
- Primary indexes for common queries
- Composite indexes for complex queries
- Automatic index creation during initialization

### Batch Processing
- Configurable batch sizes
- Efficient bulk operations
- Error handling for individual records

## Database Maintenance

### Optimization
```python
# Run database optimization
manager.optimize_database()

# This performs:
# - ANALYZE for better query planning
# - PRAGMA optimize for performance tuning
# - VACUUM for space reclamation
```

### Backup
```python
# Create database backup
backup_result = manager.backup_database("backups/backup.db")
if backup_result.success:
    print(f"Backup created at: {backup_result.data}")
```

### Monitoring
```python
# Get detailed table information
table_info = manager.get_table_info()
for table_name, info in table_info.data.items():
    print(f"Table: {table_name}")
    print(f"  Columns: {len(info['columns'])}")
    print(f"  Rows: {info['row_count']}")
```

## Configuration

### Initialization Options

```python
manager = EnhancedSQLiteManager(
    db_path="data/custom.db",           # Custom database path
    schema_path="data/schemas/schema.json",  # Custom schema path
)

# Performance settings
manager.batch_size = 2000              # Custom batch size
manager.enable_wal = True              # Enable WAL mode
manager.enable_foreign_keys = True     # Enable foreign key constraints
```

## Migration from Original

### Simple Migration
```python
# Old code (still works)
from src.database.sqlite_manager import SQLiteManager
manager = SQLiteManager()

# New code (recommended)
from src.database.enhanced_sqlite_manager import EnhancedSQLiteManager
manager = EnhancedSQLiteManager()
```

### Gradual Migration
```python
# Start with enhanced features
manager = EnhancedSQLiteManager()

# Use original methods
manager.store_document(doc)

# Gradually adopt new features
manager.store_patient_records_batch(records)
manager.optimize_database()
```

## Testing

Run the test suite to verify functionality:

```bash
cd src/database
python test_enhanced_manager.py
```

This will test:
- ✅ Functionality preservation
- ✅ Enhanced features
- ✅ Backward compatibility
- ✅ Schema synchronization

## Error Handling

The enhanced manager provides comprehensive error handling:

```python
try:
    result = manager.store_patient_records_batch(records)
    if result.success:
        print(f"Stored {result.data['total_stored']} records")
        if result.data['failed_records']:
            print(f"Failed to store {len(result.data['failed_records'])} records")
    else:
        print(f"Batch storage failed: {result.error}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Use Enhanced Features**: Leverage batch operations for large datasets
2. **Schema Validation**: Always validate data against schemas
3. **Regular Optimization**: Run `optimize_database()` periodically
4. **Backup Strategy**: Use `backup_database()` before major changes
5. **Error Handling**: Check `ProcessingResult.success` for all operations

## Troubleshooting

### Common Issues

1. **Schema Loading Failed**: Check schema file path and JSON format
2. **Validation Errors**: Review data types and enum values
3. **Performance Issues**: Run `optimize_database()` and check indexes
4. **Migration Failures**: Ensure schema compatibility and backup first

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

manager = EnhancedSQLiteManager()
# Detailed logs will show database operations
```

## Future Enhancements

Planned features for upcoming versions:
- Advanced query builder
- Data versioning and history
- Real-time synchronization
- Advanced analytics and reporting
- Multi-database support