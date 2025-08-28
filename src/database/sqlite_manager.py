"""
SQLite database manager for storing extracted patient records.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

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

class SQLiteManager:
    """Manages SQLite database operations for patient records."""
    
    def __init__(self, db_path: str = "data/database/biomedical_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
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
                
                # Create patient_records table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patient_records (
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
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        
                        FOREIGN KEY (source_document_id) REFERENCES documents (id)
                    )
                """)
                
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
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_pmid ON patient_records (pmid)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_gene ON patient_records (gene)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_phenotypes ON patient_records (phenotypes)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_pmid ON documents (pmid)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_extractions_document_id ON extractions (document_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_extractions_agent_type ON extractions (agent_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_activities_type ON system_activities (activity_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_alerts_status ON system_alerts (status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_requests_endpoint ON api_requests (endpoint)")
                
                conn.commit()
                log.info("Database initialized successfully")
                
        except Exception as e:
            log.error(f"Failed to initialize database: {e}")
            raise
    
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
                    # Insert patient record
                    cursor.execute("""
                        INSERT OR REPLACE INTO patient_records (
                            id, patient_id, source_document_id, pmid,
                            sex, age_of_onset, age_at_diagnosis, age_at_death,
                            ethnicity, consanguinity, gene, mutations, inheritance,
                            zygosity, parental_origin, genetic_testing, additional_genes,
                            phenotypes, symptoms, diagnostic_findings, lab_values,
                            imaging_findings, treatments, medications, dosages,
                            treatment_response, adverse_events, survival_status,
                            survival_time, cause_of_death, follow_up_duration,
                            clinical_outcome, extraction_metadata, confidence_scores,
                            validation_status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record.id,
                        record.patient_id,
                        record.source_document_id,
                        record.pmid,
                        record.sex,
                        record.age_of_onset,
                        record.age_at_diagnosis,
                        record.age_at_death,
                        record.ethnicity,
                        record.consanguinity,
                        record.gene,
                        record.mutations,
                        record.inheritance,
                        record.zygosity,
                        record.parental_origin,
                        record.genetic_testing,
                        record.additional_genes,
                        record.phenotypes,
                        record.symptoms,
                        record.diagnostic_findings,
                        record.lab_values,
                        record.imaging_findings,
                        record.treatments,
                        record.medications,
                        record.dosages,
                        record.treatment_response,
                        record.adverse_events,
                        record.survival_status,
                        record.survival_time,
                        record.cause_of_death,
                        record.follow_up_duration,
                        record.clinical_outcome,
                        json.dumps(record.extraction_metadata) if hasattr(record, 'extraction_metadata') else None,
                        json.dumps(record.confidence_scores) if hasattr(record, 'confidence_scores') else None,
                        record.validation_status
                    ))
                    
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
<<<<<<< Current (Your changes)
=======
    
    # Validation interface methods for enhanced LangExtract
    async def store_validation_data(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store validation data for extraction results."""
        try:
            # Create validation table if it doesn't exist
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS validation_data (
                        id TEXT PRIMARY KEY,
                        extraction_id TEXT UNIQUE,
                        original_text TEXT,
                        highlighted_text TEXT,
                        extractions TEXT,
                        spans TEXT,
                        confidence_scores TEXT,
                        validation_status TEXT DEFAULT 'pending',
                        validator_notes TEXT,
                        corrections TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        validated_at TIMESTAMP
                    )
                """)
                
                # Insert validation data
                import uuid
                validation_id = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO validation_data (
                        id, extraction_id, original_text, highlighted_text,
                        extractions, spans, confidence_scores, validation_status,
                        validator_notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    validation_id,
                    validation_data['extraction_id'],
                    validation_data['original_text'],
                    validation_data['highlighted_text'],
                    validation_data['extractions'],
                    validation_data['spans'],
                    validation_data['confidence_scores'],
                    validation_data['validation_status'],
                    validation_data.get('validator_notes'),
                    validation_data['created_at']
                ))
                
                conn.commit()
                return {'id': validation_id, 'extraction_id': validation_data['extraction_id']}
                
        except Exception as e:
            log.error(f"Failed to store validation data: {e}")
            raise
    
    async def update_validation_data(self, extraction_id: str, update_data: Dict[str, Any]) -> bool:
        """Update validation data with corrections and status."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build update query dynamically
                update_fields = []
                values = []
                
                for field, value in update_data.items():
                    update_fields.append(f"{field} = ?")
                    values.append(value)
                
                values.append(extraction_id)
                
                query = f"""
                    UPDATE validation_data 
                    SET {', '.join(update_fields)}
                    WHERE extraction_id = ?
                """
                
                cursor.execute(query, values)
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            log.error(f"Failed to update validation data: {e}")
            raise
    
    async def get_validation_queue(self, status: str = "pending") -> List[Dict[str, Any]]:
        """Get validation queue filtered by status."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM validation_data
                    WHERE validation_status = ?
                    ORDER BY created_at ASC
                """, (status,))
                
                columns = [description[0] for description in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
                
        except Exception as e:
            log.error(f"Failed to get validation queue: {e}")
            return []
    
    async def store_extraction_with_linking(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store extraction with complete linking to documents and validation."""
        try:
            # Create extraction_linking table if needed
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS extraction_linking (
                        id TEXT PRIMARY KEY,
                        document_id TEXT,
                        metadata_id TEXT,
                        fulltext_id TEXT,
                        validation_id TEXT,
                        model_id TEXT,
                        extraction_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (document_id) REFERENCES documents (id)
                    )
                """)
                
                # Insert extraction with linking
                import uuid
                extraction_id = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO extraction_linking (
                        id, document_id, metadata_id, fulltext_id,
                        validation_id, model_id, extraction_data, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    extraction_id,
                    extraction_data['document_id'],
                    extraction_data.get('metadata_id'),
                    extraction_data.get('fulltext_id'),
                    extraction_data.get('validation_id'),
                    extraction_data['model_id'],
                    extraction_data['extraction_data'],
                    extraction_data['created_at']
                ))
                
                conn.commit()
                return {'id': extraction_id}
                
        except Exception as e:
            log.error(f"Failed to store extraction with linking: {e}")
            raise
    
    async def get_extraction_with_validation(self, extraction_id: str) -> Optional[Dict[str, Any]]:
        """Get extraction data with validation information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT el.*, vd.validation_status, vd.validator_notes, vd.corrections
                    FROM extraction_linking el
                    LEFT JOIN validation_data vd ON vd.extraction_id = el.id
                    WHERE el.id = ?
                """, (extraction_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                
                return None
                
        except Exception as e:
            log.error(f"Failed to get extraction with validation: {e}")
            return None
    
    async def get_extraction_data(self, extraction_id: str) -> Optional[Dict[str, Any]]:
        """Get extraction data by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM extraction_linking
                    WHERE id = ?
                """, (extraction_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    result = dict(zip(columns, row))
                    # Parse extraction_data JSON
                    if result.get('extraction_data'):
                        result['extraction_data'] = json.loads(result['extraction_data'])
                    return result
                
                return None
                
        except Exception as e:
            log.error(f"Failed to get extraction data: {e}")
            return None
    
    async def update_extraction_data(self, extraction_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update extraction data with corrections."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE extraction_linking
                    SET extraction_data = ?
                    WHERE id = ?
                """, (json.dumps(updated_data), extraction_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            log.error(f"Failed to update extraction data: {e}")
            raise
    
    async def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total extractions
                cursor.execute("SELECT COUNT(*) FROM validation_data")
                total_extractions = cursor.fetchone()[0]
                
                # Get counts by status
                cursor.execute("""
                    SELECT validation_status, COUNT(*) 
                    FROM validation_data 
                    GROUP BY validation_status
                """)
                status_counts = dict(cursor.fetchall())
                
                # Get average confidence
                cursor.execute("""
                    SELECT AVG(CAST(confidence_scores AS REAL))
                    FROM validation_data
                    WHERE confidence_scores IS NOT NULL
                """)
                avg_confidence = cursor.fetchone()[0] or 0
                
                # Calculate validation rate
                completed = status_counts.get('validated', 0) + status_counts.get('rejected', 0)
                validation_rate = (completed / total_extractions * 100) if total_extractions > 0 else 0
                
                return {
                    "total_extractions": total_extractions,
                    "pending_validations": status_counts.get('pending', 0),
                    "completed_validations": completed,
                    "validated_count": status_counts.get('validated', 0),
                    "rejected_count": status_counts.get('rejected', 0),
                    "needs_correction_count": status_counts.get('needs_correction', 0),
                    "average_confidence": round(avg_confidence, 2),
                    "validation_rate": round(validation_rate, 2)
                }
                
        except Exception as e:
            log.error(f"Failed to get validation statistics: {e}")
            return {
                "total_extractions": 0,
                "pending_validations": 0,
                "completed_validations": 0,
                "validated_count": 0,
                "rejected_count": 0,
                "needs_correction_count": 0,
                "average_confidence": 0,
                "validation_rate": 0
            }
    
    async def get_extractions_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all extractions for a specific document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First check if validation_data table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='validation_data'
                """)
                if not cursor.fetchone():
                    return []
                
                # Get extractions linked to the document
                cursor.execute("""
                    SELECT 
                        vd.id,
                        vd.extraction_id,
                        vd.original_text,
                        vd.highlighted_text,
                        vd.extractions,
                        vd.spans,
                        vd.confidence_scores,
                        vd.validation_status,
                        vd.created_at
                    FROM validation_data vd
                    LEFT JOIN extraction_linking el ON vd.extraction_id = el.extraction_id
                    WHERE el.document_id = ? OR vd.extraction_id LIKE ?
                    ORDER BY vd.created_at DESC
                """, (document_id, f"%{document_id}%"))
                
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
                
        except Exception as e:
            log.error(f"Failed to get extractions by document: {e}")
            return []
