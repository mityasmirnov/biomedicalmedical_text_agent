"""
Enhanced SQLite database manager for storing extracted patient records.
This enhanced version preserves all functionality from sqlite_manager.py while adding
improvements for better data management, schema validation, and performance.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
import hashlib
import uuid

# Remove circular imports
# from core.base import PatientRecord, ProcessingResult
# from core.logging_config import get_logger

log = logging.getLogger(__name__)

# Simple classes to avoid circular imports
class PatientRecord:
    """Simple patient record class for database operations."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ProcessingResult:
    """Simple processing result class for database operations."""
    def __init__(self, success: bool, data: Any = None, error: str = None, metadata: Dict[str, Any] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}

class EnhancedSQLiteManager:
    """Enhanced SQLite database manager with improved functionality and schema support."""
    
    def __init__(self, db_path: str = "data/database/biomedical_data.db", 
                 schema_path: str = "data/schemas/table_schema.json"):
        self.db_path = Path(db_path)
        self.schema_path = Path(schema_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Performance optimization settings
        self.batch_size = 1000
        self.enable_wal = True
        self.enable_foreign_keys = True
        
        # Load schema for validation
        self.schema = self._load_schema()
        
        # Initialize database
        self._initialize_database()
        
        if self.enable_wal:
            self._enable_wal_mode()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema for validation."""
        try:
            if self.schema_path.exists():
                with open(self.schema_path, 'r') as f:
                    return json.load(f)
            else:
                log.warning(f"Schema file not found at {self.schema_path}")
                return {}
        except Exception as e:
            log.error(f"Failed to load schema: {e}")
            return {}
    
    def _enable_wal_mode(self):
        """Enable WAL mode for better concurrent access."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA cache_size=10000")
                conn.execute("PRAGMA temp_store=MEMORY")
                log.info("WAL mode enabled for better performance")
        except Exception as e:
            log.warning(f"Failed to enable WAL mode: {e}")
    
    def _initialize_database(self):
        """Initialize database with required tables and enhanced structure."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Enable foreign keys
                if self.enable_foreign_keys:
                    cursor.execute("PRAGMA foreign_keys=ON")
                
                # Create documents table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        source_path TEXT,
                        pmid INTEGER,
                        doi TEXT,
                        authors TEXT,
                        journal TEXT,
                        publication_date TEXT,
                        abstract TEXT,
                        content TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create enhanced patient_records table with all schema fields
                self._create_enhanced_patient_records_table(cursor)
                
                # Create extraction_runs table for tracking
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS extraction_runs (
                        id TEXT PRIMARY KEY,
                        document_id TEXT,
                        run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        model_used TEXT,
                        extraction_config TEXT,
                        total_records INTEGER,
                        successful_records INTEGER,
                        failed_records INTEGER,
                        processing_time REAL,
                        errors TEXT,
                        
                        FOREIGN KEY (document_id) REFERENCES documents (id)
                    )
                """)
                
                # Create extractions table (from UI backend)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS extractions (
                        id TEXT PRIMARY KEY,
                        document_id TEXT NOT NULL,
                        agent_type TEXT NOT NULL,
                        extracted_data TEXT DEFAULT '{}',
                        status TEXT DEFAULT 'pending',
                        confidence_score REAL DEFAULT 0.0,
                        processing_time_seconds REAL DEFAULT 0.0,
                        validation_status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (document_id) REFERENCES documents (id)
                    )
                """)
                
                # Create system_activities table (from UI backend)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_activities (
                        id TEXT PRIMARY KEY,
                        activity_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        user_id TEXT,
                        metadata TEXT DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create system_alerts table (from UI backend)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_alerts (
                        id TEXT PRIMARY KEY,
                        alert_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        dismissed_at TIMESTAMP,
                        dismissed_by TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create api_requests table (from UI backend)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_requests (
                        id TEXT PRIMARY KEY,
                        endpoint TEXT NOT NULL,
                        method TEXT NOT NULL,
                        user_id TEXT,
                        response_status INTEGER,
                        response_time_ms REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create users table (from UI backend)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT DEFAULT 'user',
                        permissions TEXT DEFAULT '[]',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create default admin user (from UI backend)
                cursor.execute("""
                    INSERT OR IGNORE INTO users (id, email, name, password_hash, role, permissions)
                    VALUES ('admin', 'admin@example.com', 'Administrator', 
                            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6QBjDKJhOu', 
                            'admin', '["read", "write", "admin"]')
                """)
                
                # Create enhanced indexes for better performance
                self._create_enhanced_indexes(cursor)
                
                conn.commit()
                log.info("Enhanced database initialized successfully")
                
        except Exception as e:
            log.error(f"Failed to initialize enhanced database: {e}")
            raise

    def _create_enhanced_patient_records_table(self, cursor):
        """Create enhanced patient_records table with all schema fields."""
        # Start with the base fields from original manager
        base_fields = """
            id TEXT PRIMARY KEY,
            patient_id TEXT,
            source_document_id TEXT,
            pmid INTEGER,
            
            -- Demographics
            sex INTEGER,
            age_of_onset REAL,
            age_at_diagnosis REAL,
            age_at_death REAL,
            ethnicity TEXT,
            consanguinity INTEGER,
            
            -- Genetics
            gene TEXT,
            mutations TEXT,
            inheritance TEXT,
            zygosity TEXT,
            parental_origin TEXT,
            genetic_testing TEXT,
            additional_genes TEXT,
            
            -- Clinical
            phenotypes TEXT,
            symptoms TEXT,
            diagnostic_findings TEXT,
            lab_values TEXT,
            imaging_findings TEXT,
            
            -- Treatment
            treatments TEXT,
            medications TEXT,
            dosages TEXT,
            treatment_response TEXT,
            adverse_events TEXT,
            
            -- Outcomes
            survival_status INTEGER,
            survival_time REAL,
            cause_of_death TEXT,
            follow_up_duration REAL,
            clinical_outcome TEXT,
            
            -- Metadata
            extraction_metadata TEXT,
            confidence_scores TEXT,
            validation_status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """
        
        # Add additional schema fields if they exist
        additional_fields = []
        base_field_names = {
            'id', 'patient_id', 'source_document_id', 'pmid', 'sex', 'age_of_onset', 
            'age_at_diagnosis', 'age_at_death', 'ethnicity', 'consanguinity', 'gene', 
            'mutations', 'inheritance', 'zygosity', 'parental_origin', 'genetic_testing', 
            'additional_genes', 'phenotypes', 'symptoms', 'diagnostic_findings', 
            'lab_values', 'imaging_findings', 'treatments', 'medications', 'dosages', 
            'treatment_response', 'adverse_events', 'survival_status', 'survival_time', 
            'cause_of_death', 'follow_up_duration', 'clinical_outcome', 
            'extraction_metadata', 'confidence_scores', 'validation_status', 
            'created_at', 'updated_at'
        }
        
        if self.schema and 'properties' in self.schema:
            for field_name, field_info in self.schema['properties'].items():
                if field_name not in base_field_names:  # Skip all base fields
                    field_type = self._get_sqlite_type(field_info.get('type', 'string'))
                    additional_fields.append(f"{field_name} {field_type}")
        
        # Combine all fields
        all_fields = base_fields
        if additional_fields:
            all_fields += ",\n            " + ",\n            ".join(additional_fields)
        
        # Create the table
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS patient_records (
                {all_fields},
                FOREIGN KEY (source_document_id) REFERENCES documents (id)
            )
        """
        
        cursor.execute(create_sql)
    
    def _get_sqlite_type(self, json_type: str) -> str:
        """Convert JSON schema type to SQLite type."""
        type_mapping = {
            'string': 'TEXT',
            'number': 'REAL',
            'integer': 'INTEGER',
            'boolean': 'INTEGER',
            'array': 'TEXT',  # Store as JSON string
            'object': 'TEXT'  # Store as JSON string
        }
        return type_mapping.get(json_type, 'TEXT')
    
    def _create_enhanced_indexes(self, cursor):
        """Create enhanced indexes for better performance."""
        # Original indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_pmid ON patient_records (pmid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_gene ON patient_records (gene)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_phenotypes ON patient_records (phenotypes)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_pmid ON documents (pmid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_extractions_document_id ON extractions (document_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_extractions_agent_type ON extractions (agent_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_activities_type ON system_activities (activity_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_alerts_status ON system_alerts (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_requests_endpoint ON api_requests (endpoint)")
        
        # Enhanced indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_patient_id ON patient_records (patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_source_document ON patient_records (source_document_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_created_at ON patient_records (created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents (created_at)")
        
        # Composite indexes for common query patterns
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_gene_phenotype ON patient_records (gene, phenotypes)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_pmid_gene ON patient_records (pmid, gene)")

    # Core methods preserving all functionality from original sqlite_manager.py
    
    def store_document(self, document_data: Dict[str, Any]) -> ProcessingResult:
        """Store a document in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO documents (
                        id, title, source_path, pmid, doi, authors, journal, 
                        publication_date, abstract, content, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    document_data.get("id"),
                    document_data.get("title"),
                    document_data.get("source_path"),
                    document_data.get("pmid"),
                    document_data.get("doi"),
                    document_data.get("authors"),
                    document_data.get("journal"),
                    document_data.get("publication_date"),
                    document_data.get("abstract"),
                    document_data.get("content"),
                    document_data.get("metadata")
                ))
                
                conn.commit()
                
                return ProcessingResult(
                    success=True,
                    data={"document_id": document_data.get("id")},
                    metadata={"stored_at": datetime.now().isoformat()}
                )
                
        except Exception as e:
            log.error(f"Failed to store document: {e}")
            return ProcessingResult(
                success=False,
                error=str(e)
            )
    
    def get_documents(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get documents from the database with pagination."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, title, source_path, pmid, doi, authors, journal, 
                           publication_date, abstract, content, metadata, created_at
                    FROM documents
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                columns = [description[0] for description in cursor.description]
                documents = []
                
                for row in cursor.fetchall():
                    doc = dict(zip(columns, row))
                    documents.append(doc)
                
                return documents
                
        except Exception as e:
            log.error(f"Failed to get documents: {e}")
            return []
    
    def get_documents_by_pmid(self, pmid: int) -> List[Dict[str, Any]]:
        """Get documents by PMID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, title, source_path, pmid, doi, authors, journal, 
                           publication_date, abstract, content, metadata, created_at
                    FROM documents
                    WHERE pmid = ?
                    ORDER BY created_at DESC
                """, (pmid,))
                
                columns = [description[0] for description in cursor.description]
                documents = []
                
                for row in cursor.fetchall():
                    doc = dict(zip(columns, row))
                    documents.append(doc)
                
                return documents
                
        except Exception as e:
            log.error(f"Failed to get documents by PMID: {e}")
            return []
    
    def store_patient_records(self, records: List[PatientRecord]) -> ProcessingResult:
        """Store multiple patient records in the database."""
        try:
            stored_ids = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for record in records:
                    # Use the enhanced batch storage method for individual records
                    result = self._store_single_patient_record(cursor, record)
                    if result:
                        stored_ids.append(record.id)
                
                conn.commit()
                log.info(f"Stored {len(records)} patient records")
                
                return ProcessingResult(
                    success=True,
                    data=stored_ids,
                    metadata={"total_stored": len(records)}
                )
                
        except Exception as e:
            log.error(f"Error storing patient records: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to store patient records: {str(e)}"
            )
    
    def _store_single_patient_record(self, cursor, record) -> bool:
        """Store a single patient record using dynamic field handling."""
        try:
            # Convert record to dict format
            record_dict = {
                'id': record.id,
                'patient_id': record.patient_id,
                'source_document_id': record.source_document_id,
                'pmid': record.pmid,
                'sex': getattr(record, 'sex', None),
                'age_of_onset': getattr(record, 'age_of_onset', None),
                'age_at_diagnosis': getattr(record, 'age_at_diagnosis', None),
                'age_at_death': getattr(record, 'age_at_death', None),
                'ethnicity': getattr(record, 'ethnicity', None),
                'consanguinity': getattr(record, 'consanguinity', None),
                'gene': getattr(record, 'gene', None),
                'mutations': getattr(record, 'mutations', None),
                'inheritance': getattr(record, 'inheritance', None),
                'zygosity': getattr(record, 'zygosity', None),
                'parental_origin': getattr(record, 'parental_origin', None),
                'genetic_testing': getattr(record, 'genetic_testing', None),
                'additional_genes': getattr(record, 'additional_genes', None),
                'phenotypes': getattr(record, 'phenotypes', None),
                'symptoms': getattr(record, 'symptoms', None),
                'diagnostic_findings': getattr(record, 'diagnostic_findings', None),
                'lab_values': getattr(record, 'lab_values', None),
                'imaging_findings': getattr(record, 'imaging_findings', None),
                'treatments': getattr(record, 'treatments', None),
                'medications': getattr(record, 'medications', None),
                'dosages': getattr(record, 'dosages', None),
                'treatment_response': getattr(record, 'treatment_response', None),
                'adverse_events': getattr(record, 'adverse_events', None),
                'survival_status': getattr(record, 'survival_status', None),
                'survival_time': getattr(record, 'survival_time', None),
                'cause_of_death': getattr(record, 'cause_of_death', None),
                'follow_up_duration': getattr(record, 'follow_up_duration', None),
                'clinical_outcome': getattr(record, 'clinical_outcome', None),
                'extraction_metadata': getattr(record, 'extraction_metadata', None),
                'confidence_scores': getattr(record, 'confidence_scores', None),
                'validation_status': getattr(record, 'validation_status', None)
            }
            
            # Use the existing batch storage logic
            fields, values = self._prepare_record_for_insertion(record_dict)
            placeholders = ', '.join(['?' for _ in values])
            insert_sql = f"INSERT OR REPLACE INTO patient_records ({fields}) VALUES ({placeholders})"
            
            cursor.execute(insert_sql, values)
            return True
            
        except Exception as e:
            log.error(f"Error storing single patient record: {str(e)}")
            return False
    
    def _convert_record_to_db_format(self, record: PatientRecord) -> Tuple:
        """Convert PatientRecord to database tuple format."""
        data = record.data
        
        # Helper function to convert lists to JSON strings
        def list_to_json(value):
            if isinstance(value, list):
                return json.dumps(value)
            return value
        
        return (
            record.id,
            data.get('patient_id'),
            record.source_document_id,
            data.get('pmid'),
            
            # Demographics
            data.get('sex'),
            data.get('age_of_onset'),
            data.get('age_at_diagnosis'),
            data.get('age_at_death'),
            data.get('ethnicity'),
            data.get('consanguinity'),
            
            # Genetics
            data.get('gene'),
            data.get('mutations'),
            data.get('inheritance'),
            data.get('zygosity'),
            data.get('parental_origin'),
            data.get('genetic_testing'),
            list_to_json(data.get('additional_genes')),
            
            # Clinical
            list_to_json(data.get('phenotypes')),
            list_to_json(data.get('symptoms')),
            list_to_json(data.get('diagnostic_findings')),
            list_to_json(data.get('lab_values')),
            list_to_json(data.get('imaging_findings')),
            
            # Treatment
            list_to_json(data.get('treatments')),
            list_to_json(data.get('medications')),
            list_to_json(data.get('dosages')),
            data.get('treatment_response'),
            list_to_json(data.get('adverse_events')),
            
            # Outcomes
            data.get('survival_status'),
            data.get('survival_time'),
            data.get('cause_of_death'),
            data.get('follow_up_duration'),
            data.get('clinical_outcome'),
            
            # Metadata
            json.dumps(record.extraction_metadata or {}),
            json.dumps(record.confidence_scores or {}),
            record.validation_status,
            datetime.now().isoformat()
        )
    
    def get_patient_records(self, 
                           gene: Optional[str] = None,
                           phenotype: Optional[str] = None,
                           age_range: Optional[Tuple[float, float]] = None,
                           limit: int = 100) -> ProcessingResult:
        """Get patient records with optional filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query
                query = "SELECT * FROM patient_records WHERE 1=1"
                params = []
                
                if gene:
                    query += " AND gene LIKE ?"
                    params.append(f"%{gene}%")
                
                if phenotype:
                    query += " AND phenotypes LIKE ?"
                    params.append(f"%{phenotype}%")
                
                if age_range:
                    min_age, max_age = age_range
                    query += " AND age_of_onset BETWEEN ? AND ?"
                    params.extend([min_age, max_age])
                
                query += f" LIMIT {limit}"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to dictionaries
                records = []
                for row in rows:
                    record = dict(zip([col[0] for col in cursor.description], row))
                    records.append(record)
                
                return ProcessingResult(
                    success=True,
                    data=records,
                    metadata={"total_found": len(records)}
                )
                
        except Exception as e:
            log.error(f"Error getting patient records: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to get patient records: {str(e)}"
            )
    
    def get_statistics(self) -> ProcessingResult:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count documents
                cursor.execute("SELECT COUNT(*) FROM documents")
                doc_count = cursor.fetchone()[0]
                
                # Count patient records
                cursor.execute("SELECT COUNT(*) FROM patient_records")
                patient_count = cursor.fetchone()[0]
                
                # Count by gene
                cursor.execute("SELECT gene, COUNT(*) FROM patient_records WHERE gene IS NOT NULL GROUP BY gene ORDER BY COUNT(*) DESC LIMIT 10")
                gene_counts = dict(cursor.fetchall())
                
                # Count by phenotype
                cursor.execute("SELECT phenotypes, COUNT(*) FROM patient_records WHERE phenotypes IS NOT NULL GROUP BY phenotypes ORDER BY COUNT(*) DESC LIMIT 10")
                phenotype_counts = dict(cursor.fetchall())
                
                stats = {
                    "total_documents": doc_count,
                    "total_patients": patient_count,
                    "top_genes": gene_counts,
                    "top_phenotypes": phenotype_counts,
                    "database_path": str(self.db_path)
                }
                
                return ProcessingResult(
                    success=True,
                    data=stats
                )
                
        except Exception as e:
            log.error(f"Error getting statistics: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to get statistics: {str(e)}"
            )
    
    def search_records(self, query: str, limit: int = 50) -> ProcessingResult:
        """Search patient records by text query."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Search across multiple fields
                search_query = """
                    SELECT * FROM patient_records 
                    WHERE gene LIKE ? OR mutations LIKE ? OR phenotypes LIKE ? 
                    OR symptoms LIKE ? OR diagnostic_findings LIKE ?
                    ORDER BY id
                    LIMIT ?
                """
                
                search_term = f"%{query}%"
                cursor.execute(search_query, [search_term] * 5 + [limit])
                rows = cursor.fetchall()
                
                # Convert to dictionaries
                records = []
                for row in rows:
                    record = dict(zip([col[0] for col in cursor.description], row))
                    records.append(record)
                
                return ProcessingResult(
                    success=True,
                    data=records,
                    metadata={"query": query, "total_found": len(records)}
                )
                
        except Exception as e:
            log.error(f"Error searching records: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Search failed: {str(e)}"
            )
    
    def export_to_csv(self, output_path: str) -> ProcessingResult:
        """Export patient records to CSV file."""
        try:
            import pandas as pd
            
            with sqlite3.connect(self.db_path) as conn:
                # Read all patient records
                df = pd.read_sql_query("SELECT * FROM patient_records", conn)
                
                # Export to CSV
                df.to_csv(output_path, index=False)
                
                log.info(f"Exported {len(df)} records to {output_path}")
                
                return ProcessingResult(
                    success=True,
                    data=output_path,
                    metadata={"total_exported": len(df)}
                )
                
        except ImportError:
            return ProcessingResult(
                success=False,
                error="pandas not available for CSV export"
            )
        except Exception as e:
            log.error(f"Error exporting to CSV: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Export failed: {str(e)}"
            )
    
    # Enhanced functionality beyond original sqlite_manager.py
    
    def store_patient_records_batch(self, records: List[Dict[str, Any]], batch_size: int = None) -> ProcessingResult:
        """Store patient records in batches for better performance."""
        if batch_size is None:
            batch_size = self.batch_size
        
        try:
            total_stored = 0
            failed_records = []
            
            # Process in batches
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    for record in batch:
                        try:
                            # Validate record against schema
                            if not self._validate_record_against_schema(record):
                                failed_records.append({
                                    'record': record,
                                    'error': 'Schema validation failed'
                                })
                                continue
                            
                            # Generate ID if not provided
                            if 'id' not in record:
                                record['id'] = str(uuid.uuid4())
                            
                            # Prepare fields for insertion
                            fields, values = self._prepare_record_for_insertion(record)
                            
                            # Insert record
                            placeholders = ', '.join(['?' for _ in values])
                            insert_sql = f"INSERT OR REPLACE INTO patient_records ({fields}) VALUES ({placeholders})"
                            
                            cursor.execute(insert_sql, values)
                            total_stored += 1
                            
                        except Exception as e:
                            failed_records.append({
                                'record': record,
                                'error': str(e)
                            })
                    
                    conn.commit()
            
            return ProcessingResult(
                success=True,
                data={"total_stored": total_stored, "failed_records": failed_records},
                metadata={"batch_size": batch_size, "total_processed": len(records)}
            )
            
        except Exception as e:
            log.error(f"Error in batch storage: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Batch storage failed: {str(e)}"
            )
    
    def _validate_record_against_schema(self, record: Dict[str, Any]) -> bool:
        """Validate a record against the loaded JSON schema."""
        if not self.schema or 'properties' not in self.schema:
            return True  # No schema to validate against
        
        try:
            for field_name, field_info in self.schema['properties'].items():
                if field_name in record:
                    value = record[field_name]
                    field_type = field_info.get('type')
                    
                    # Type validation
                    if field_type == 'string' and not isinstance(value, str):
                        if value is not None:  # Allow None values
                            return False
                    elif field_type == 'number' and not isinstance(value, (int, float)):
                        if value is not None:  # Allow None values
                            return False
                    elif field_type == 'integer' and not isinstance(value, int):
                        if value is not None:  # Allow None values
                            return False
                    
                    # Enum validation
                    if 'enum' in field_info and value not in field_info['enum']:
                        if value is not None:  # Allow None values
                            return False
            
            return True
            
        except Exception as e:
            log.warning(f"Schema validation error: {e}")
            return True  # Continue if validation fails
    
    def _prepare_record_for_insertion(self, record: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Prepare a record for database insertion."""
        # Get all available columns from the table
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(patient_records)")
            columns = [row[1] for row in cursor.fetchall()]
        
        # Filter record to only include valid columns
        valid_fields = []
        valid_values = []
        
        for column in columns:
            if column in record:
                value = record[column]
                
                # Convert lists and dicts to JSON strings
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                
                valid_fields.append(column)
                valid_values.append(value)
        
        return ', '.join(valid_fields), valid_values
    
    def migrate_schema(self, target_schema_path: str = None) -> ProcessingResult:
        """Migrate database schema to match a new schema file."""
        try:
            if target_schema_path:
                target_schema = self._load_schema_from_path(target_schema_path)
            elif self.schema:
                target_schema = self.schema
            else:
                # Create a minimal default schema if none exists
                target_schema = {
                    "properties": {
                        "pmid": {"type": "number"},
                        "patient_id": {"type": "string"}
                    }
                }
            
            # Get current table structure
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(patient_records)")
                current_columns = {row[1]: row[2] for row in cursor.fetchall()}
                
                # Find new columns to add
                new_columns = []
                for field_name, field_info in target_schema.get('properties', {}).items():
                    if field_name not in current_columns:
                        field_type = self._get_sqlite_type(field_info.get('type', 'string'))
                        new_columns.append((field_name, field_type))
                
                # Add new columns
                for column_name, column_type in new_columns:
                    try:
                        cursor.execute(f"ALTER TABLE patient_records ADD COLUMN {column_name} {column_type}")
                        log.info(f"Added column: {column_name}")
                    except Exception as e:
                        log.warning(f"Failed to add column {column_name}: {e}")
                
                conn.commit()
            
            return ProcessingResult(
                success=True,
                data={"columns_added": len(new_columns)},
                metadata={"new_columns": [col[0] for col in new_columns]}
            )
            
        except Exception as e:
            log.error(f"Schema migration failed: {e}")
            return ProcessingResult(
                success=False,
                error=f"Schema migration failed: {str(e)}"
            )
    
    def _load_schema_from_path(self, schema_path: str) -> Dict[str, Any]:
        """Load schema from a specific path."""
        try:
            path = Path(schema_path)
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
            else:
                log.warning(f"Schema file not found at {schema_path}")
                return {}
        except Exception as e:
            log.error(f"Failed to load schema from {schema_path}: {e}")
            return {}
    
    def get_table_info(self) -> ProcessingResult:
        """Get detailed information about database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                table_info = {}
                for table in tables:
                    # Get column information
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = []
                    for row in cursor.fetchall():
                        columns.append({
                            'name': row[1],
                            'type': row[2],
                            'not_null': bool(row[3]),
                            'default_value': row[4],
                            'primary_key': bool(row[5])
                        })
                    
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]
                    
                    table_info[table] = {
                        'columns': columns,
                        'row_count': row_count
                    }
                
                return ProcessingResult(
                    success=True,
                    data=table_info
                )
                
        except Exception as e:
            log.error(f"Error getting table info: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to get table info: {str(e)}"
            )
    
    def optimize_database(self) -> ProcessingResult:
        """Optimize database performance."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Analyze tables for better query planning
                cursor.execute("ANALYZE")
                
                # Update statistics
                cursor.execute("PRAGMA optimize")
                
                # Vacuum to reclaim space
                cursor.execute("VACUUM")
                
                conn.commit()
                
                return ProcessingResult(
                    success=True,
                    data="Database optimization completed",
                    metadata={"optimization_time": datetime.now().isoformat()}
                )
                
        except Exception as e:
            log.error(f"Database optimization failed: {e}")
            return ProcessingResult(
                success=False,
                error=f"Database optimization failed: {str(e)}"
            )
    
    def backup_database(self, backup_path: str) -> ProcessingResult:
        """Create a backup of the database."""
        try:
            import shutil
            
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            
            log.info(f"Database backed up to {backup_path}")
            
            return ProcessingResult(
                success=True,
                data=str(backup_path),
                metadata={"backup_time": datetime.now().isoformat()}
            )
            
        except Exception as e:
            log.error(f"Database backup failed: {e}")
            return ProcessingResult(
                success=False,
                error=f"Database backup failed: {str(e)}"
            )


# Backward compatibility - provide the same interface as the original
class SQLiteManager(EnhancedSQLiteManager):
    """Backward compatibility class that inherits from EnhancedSQLiteManager."""
    def __init__(self, db_path: str = "data/database/biomedical_data.db"):
        super().__init__(db_path)
        log.info("Using enhanced SQLite manager with backward compatibility")