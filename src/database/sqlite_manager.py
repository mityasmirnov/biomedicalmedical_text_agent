"""
SQLite database manager for storing extracted patient records.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from core.base import PatientRecord, ProcessingResult
from core.logging_config import get_logger

log = get_logger(__name__)

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
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_pmid ON patient_records (pmid)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_gene ON patient_records (gene)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_records_phenotypes ON patient_records (phenotypes)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_pmid ON documents (pmid)")
                
                conn.commit()
                log.info(f"Database initialized at {self.db_path}")
                
        except Exception as e:
            log.error(f"Error initializing database: {str(e)}")
            raise
    
    def store_document(self, document) -> ProcessingResult[str]:
        """Store a document in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract PMID from metadata or filename
                pmid = None
                if hasattr(document, 'metadata') and document.metadata:
                    pmid = document.metadata.get('pmid')
                
                if not pmid and hasattr(document, 'source_path'):
                    filename = Path(document.source_path).stem
                    if filename.startswith("PMID"):
                        try:
                            pmid = int(filename[4:])
                        except ValueError:
                            pass
                
                cursor.execute("""
                    INSERT OR REPLACE INTO documents 
                    (id, title, source_path, pmid, content, metadata, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    document.id,
                    getattr(document, 'title', ''),
                    getattr(document, 'source_path', ''),
                    pmid,
                    getattr(document, 'content', ''),
                    json.dumps(getattr(document, 'metadata', {})),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                log.info(f"Stored document {document.id} in database")
                
                return ProcessingResult(
                    success=True,
                    data=document.id,
                    metadata={"pmid": pmid}
                )
                
        except Exception as e:
            log.error(f"Error storing document: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to store document: {str(e)}"
            )
    
    def store_patient_records(self, records: List[PatientRecord]) -> ProcessingResult[List[str]]:
        """Store multiple patient records in the database."""
        try:
            stored_ids = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for record in records:
                    # Convert record data to database format
                    db_data = self._convert_record_to_db_format(record)
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO patient_records 
                        (id, patient_id, source_document_id, pmid, 
                         sex, age_of_onset, age_at_diagnosis, age_at_death, ethnicity, consanguinity,
                         gene, mutations, inheritance, zygosity, parental_origin, genetic_testing, additional_genes,
                         phenotypes, symptoms, diagnostic_findings, lab_values, imaging_findings,
                         treatments, medications, dosages, treatment_response, adverse_events,
                         survival_status, survival_time, cause_of_death, follow_up_duration, clinical_outcome,
                         extraction_metadata, confidence_scores, validation_status, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, db_data)
                    
                    stored_ids.append(record.id)
                
                conn.commit()
                log.info(f"Stored {len(records)} patient records in database")
                
                return ProcessingResult(
                    success=True,
                    data=stored_ids,
                    metadata={"total_records": len(records)}
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
                           pmid: Optional[int] = None,
                           gene: Optional[str] = None,
                           limit: int = 100) -> ProcessingResult[List[Dict[str, Any]]]:
        """Retrieve patient records from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()
                
                query = "SELECT * FROM patient_records WHERE 1=1"
                params = []
                
                if pmid:
                    query += " AND pmid = ?"
                    params.append(pmid)
                
                if gene:
                    query += " AND gene = ?"
                    params.append(gene)
                
                query += f" ORDER BY created_at DESC LIMIT {limit}"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert rows to dictionaries
                records = []
                for row in rows:
                    record_dict = dict(row)
                    
                    # Parse JSON fields back to objects
                    json_fields = ['additional_genes', 'phenotypes', 'symptoms', 'diagnostic_findings',
                                 'lab_values', 'imaging_findings', 'treatments', 'medications',
                                 'dosages', 'adverse_events', 'extraction_metadata', 'confidence_scores']
                    
                    for field in json_fields:
                        if record_dict.get(field):
                            try:
                                record_dict[field] = json.loads(record_dict[field])
                            except (json.JSONDecodeError, TypeError):
                                pass  # Keep as string if not valid JSON
                    
                    records.append(record_dict)
                
                return ProcessingResult(
                    success=True,
                    data=records,
                    metadata={"total_found": len(records)}
                )
                
        except Exception as e:
            log.error(f"Error retrieving patient records: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to retrieve patient records: {str(e)}"
            )
    
    def get_statistics(self) -> ProcessingResult[Dict[str, Any]]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count records
                cursor.execute("SELECT COUNT(*) FROM documents")
                total_documents = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM patient_records")
                total_records = cursor.fetchone()[0]
                
                # Count by gene
                cursor.execute("""
                    SELECT gene, COUNT(*) as count 
                    FROM patient_records 
                    WHERE gene IS NOT NULL 
                    GROUP BY gene 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                top_genes = [{"gene": row[0], "count": row[1]} for row in cursor.fetchall()]
                
                # Count by PMID
                cursor.execute("""
                    SELECT pmid, COUNT(*) as count 
                    FROM patient_records 
                    WHERE pmid IS NOT NULL 
                    GROUP BY pmid 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                top_pmids = [{"pmid": row[0], "count": row[1]} for row in cursor.fetchall()]
                
                stats = {
                    "total_documents": total_documents,
                    "total_patient_records": total_records,
                    "top_genes": top_genes,
                    "top_pmids": top_pmids,
                    "database_path": str(self.db_path),
                    "database_size_mb": self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
                }
                
                return ProcessingResult(
                    success=True,
                    data=stats
                )
                
        except Exception as e:
            log.error(f"Error getting database statistics: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to get database statistics: {str(e)}"
            )
    
    def search_records(self, query: str, limit: int = 50) -> ProcessingResult[List[Dict[str, Any]]]:
        """Search patient records using full-text search."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Simple text search across multiple fields
                search_query = f"%{query}%"
                cursor.execute("""
                    SELECT * FROM patient_records 
                    WHERE patient_id LIKE ? 
                       OR gene LIKE ? 
                       OR mutations LIKE ? 
                       OR phenotypes LIKE ? 
                       OR symptoms LIKE ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (search_query, search_query, search_query, search_query, search_query, limit))
                
                rows = cursor.fetchall()
                records = [dict(row) for row in rows]
                
                return ProcessingResult(
                    success=True,
                    data=records,
                    metadata={"query": query, "total_found": len(records)}
                )
                
        except Exception as e:
            log.error(f"Error searching records: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to search records: {str(e)}"
            )
    
    def export_to_csv(self, output_path: str) -> ProcessingResult[str]:
        """Export patient records to CSV format."""
        try:
            import pandas as pd
            
            records_result = self.get_patient_records(limit=10000)  # Get all records
            if not records_result.success:
                return records_result
            
            records = records_result.data
            if not records:
                return ProcessingResult(
                    success=False,
                    error="No records to export"
                )
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Convert JSON fields to strings for CSV
            json_fields = ['additional_genes', 'phenotypes', 'symptoms', 'diagnostic_findings',
                         'lab_values', 'imaging_findings', 'treatments', 'medications',
                         'dosages', 'adverse_events']
            
            for field in json_fields:
                if field in df.columns:
                    df[field] = df[field].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
            
            # Export to CSV
            df.to_csv(output_path, index=False)
            log.info(f"Exported {len(records)} records to {output_path}")
            
            return ProcessingResult(
                success=True,
                data=output_path,
                metadata={"total_records": len(records)}
            )
            
        except Exception as e:
            log.error(f"Error exporting to CSV: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to export to CSV: {str(e)}"
            )

