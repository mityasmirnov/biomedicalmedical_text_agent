"""
Schema manager for handling JSON schemas and patient record validation.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from jsonschema import validate, ValidationError, Draft7Validator
from core.base import ProcessingResult, PatientRecord, ValidationError as BaseValidationError
from core.config import get_config
from core.logging_config import get_logger

log = get_logger(__name__)

class SchemaManager:
    """Manages JSON schemas for patient records and validation."""
    
    def __init__(self, schema_path: Optional[str] = None):
        self.config = get_config()
        self.schema_path = schema_path or self.config.get_schema_path("table_schema.json")
        self.schema = None
        self.validator = None
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load the JSON schema from file."""
        try:
            if not self.schema_path.exists():
                raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
            
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            
            # Create validator
            self.validator = Draft7Validator(self.schema)
            
            log.info(f"Loaded schema from: {self.schema_path}")
            
            # Log schema info
            properties = self.schema.get("properties", {})
            log.info(f"Schema contains {len(properties)} fields")
            
        except Exception as e:
            log.error(f"Error loading schema: {str(e)}")
            raise BaseValidationError(f"Failed to load schema: {str(e)}")
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the loaded schema."""
        return self.schema
    
    def get_field_info(self, field_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific field."""
        properties = self.schema.get("properties", {})
        return properties.get(field_name)
    
    def get_all_fields(self) -> List[str]:
        """Get list of all field names in the schema."""
        properties = self.schema.get("properties", {})
        return list(properties.keys())
    
    def get_required_fields(self) -> List[str]:
        """Get list of required field names."""
        return self.schema.get("required", [])
    
    def get_field_type(self, field_name: str) -> Optional[str]:
        """Get the type of a specific field."""
        field_info = self.get_field_info(field_name)
        if field_info:
            return field_info.get("type")
        return None
    
    def get_field_enum_values(self, field_name: str) -> Optional[List[Any]]:
        """Get enum values for a field if it has them."""
        field_info = self.get_field_info(field_name)
        if field_info:
            return field_info.get("enum")
        return None
    
    def create_default_record(self) -> Dict[str, Any]:
        """Create a record with default values for all fields."""
        record = {}
        properties = self.schema.get("properties", {})
        
        for field_name, field_info in properties.items():
            field_type = field_info.get("type")
            default_value = field_info.get("default")
            
            if default_value is not None:
                record[field_name] = default_value
            elif field_type == "string":
                record[field_name] = ""
            elif field_type == "number":
                record[field_name] = None
            elif field_type == "integer":
                record[field_name] = None
            elif field_type == "boolean":
                record[field_name] = False
            elif field_type == "array":
                record[field_name] = []
            elif field_type == "object":
                record[field_name] = {}
            else:
                record[field_name] = None
        
        return record
    
    def validate_record(self, record: Dict[str, Any]) -> ProcessingResult[bool]:
        """
        Validate a record against the schema.
        
        Args:
            record: Record to validate
            
        Returns:
            ProcessingResult indicating validation success/failure
        """
        try:
            # Validate against schema
            validate(instance=record, schema=self.schema)
            
            # Additional custom validations
            warnings = []
            
            # Check for missing recommended fields
            recommended_fields = ["pmid", "patient_id", "sex", "age_of_onset"]
            for field in recommended_fields:
                if field in record and (record[field] is None or record[field] == ""):
                    warnings.append(f"Recommended field '{field}' is missing or empty")
            
            # Check for logical consistency
            consistency_warnings = self._check_logical_consistency(record)
            warnings.extend(consistency_warnings)
            
            result = ProcessingResult(
                success=True,
                data=True,
                warnings=warnings
            )
            
            if warnings:
                log.debug(f"Validation passed with {len(warnings)} warnings")
            
            return result
            
        except ValidationError as e:
            error_msg = f"Schema validation failed: {e.message}"
            if e.absolute_path:
                error_msg += f" at path: {'.'.join(str(p) for p in e.absolute_path)}"
            
            log.error(error_msg)
            return ProcessingResult(
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            log.error(error_msg)
            return ProcessingResult(
                success=False,
                error=error_msg
            )
    
    def _check_logical_consistency(self, record: Dict[str, Any]) -> List[str]:
        """Check for logical consistency in the record."""
        warnings = []
        
        # Check alive/dead consistency
        alive_status = record.get("_0_alive_1_dead")
        age_of_death = record.get("age_of_death")
        
        if alive_status == 1 and (age_of_death is None or age_of_death == ""):
            warnings.append("Patient marked as dead but age_of_death is missing")
        elif alive_status == 0 and age_of_death is not None and age_of_death != "":
            warnings.append("Patient marked as alive but age_of_death is provided")
        
        # Check age consistency
        age_of_onset = record.get("age_of_onset")
        last_seen = record.get("last_seen")
        
        if (age_of_onset is not None and last_seen is not None and 
            isinstance(age_of_onset, (int, float)) and isinstance(last_seen, (int, float))):
            if age_of_onset > last_seen:
                warnings.append("Age of onset is greater than last seen age")
        
        # Check gene and mutation consistency
        gene = record.get("gene", "")
        mutations = record.get("mutations", "")
        
        if gene and not mutations:
            warnings.append("Gene specified but mutations field is empty")
        elif mutations and not gene:
            warnings.append("Mutations specified but gene field is empty")
        
        return warnings
    
    def normalize_record(self, record: Dict[str, Any]) -> ProcessingResult[Dict[str, Any]]:
        """
        Normalize a record to match schema requirements.
        
        Args:
            record: Record to normalize
            
        Returns:
            ProcessingResult containing normalized record
        """
        try:
            normalized = {}
            properties = self.schema.get("properties", {})
            
            for field_name, field_info in properties.items():
                field_type = field_info.get("type")
                raw_value = record.get(field_name)
                
                # Normalize based on field type
                if raw_value is None or raw_value == "":
                    if field_type == "string":
                        normalized[field_name] = ""
                    elif field_type in ["number", "integer"]:
                        normalized[field_name] = None
                    elif field_type == "boolean":
                        normalized[field_name] = False
                    else:
                        normalized[field_name] = None
                else:
                    normalized[field_name] = self._normalize_field_value(
                        raw_value, field_type, field_info
                    )
            
            return ProcessingResult(
                success=True,
                data=normalized
            )
            
        except Exception as e:
            error_msg = f"Normalization error: {str(e)}"
            log.error(error_msg)
            return ProcessingResult(
                success=False,
                error=error_msg
            )
    
    def _normalize_field_value(self, value: Any, field_type: str, field_info: Dict[str, Any]) -> Any:
        """Normalize a single field value."""
        # Handle enum values
        enum_values = field_info.get("enum")
        if enum_values and value not in enum_values:
            # Try to map common variations
            if field_type == "string":
                value_lower = str(value).lower()
                for enum_val in enum_values:
                    if str(enum_val).lower() == value_lower:
                        return enum_val
            # If no match found, keep original value (will fail validation)
        
        # Type conversion
        if field_type == "number":
            try:
                return float(value) if value not in [None, ""] else None
            except (ValueError, TypeError):
                return None
        elif field_type == "integer":
            try:
                return int(float(value)) if value not in [None, ""] else None
            except (ValueError, TypeError):
                return None
        elif field_type == "string":
            return str(value) if value is not None else ""
        elif field_type == "boolean":
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                return value.lower() in ["true", "1", "yes", "on"]
            elif isinstance(value, (int, float)):
                return bool(value)
            else:
                return False
        
        return value
    
    def create_patient_record(self, data: Dict[str, Any], **kwargs) -> PatientRecord:
        """
        Create a PatientRecord object from validated data.
        
        Args:
            data: Validated patient data
            **kwargs: Additional metadata
            
        Returns:
            PatientRecord object
        """
        record = PatientRecord(
            patient_id=data.get("patient_id", ""),
            pmid=data.get("pmid"),
            data=data,
            **kwargs
        )
        
        return record
    
    def get_field_description(self, field_name: str) -> Optional[str]:
        """Get the description of a field."""
        field_info = self.get_field_info(field_name)
        if field_info:
            return field_info.get("description")
        return None
    
    def get_schema_summary(self) -> Dict[str, Any]:
        """Get a summary of the schema."""
        properties = self.schema.get("properties", {})
        
        field_types = {}
        enum_fields = []
        required_fields = self.get_required_fields()
        
        for field_name, field_info in properties.items():
            field_type = field_info.get("type", "unknown")
            field_types[field_type] = field_types.get(field_type, 0) + 1
            
            if field_info.get("enum"):
                enum_fields.append(field_name)
        
        return {
            "total_fields": len(properties),
            "required_fields": len(required_fields),
            "field_types": field_types,
            "enum_fields": len(enum_fields),
            "schema_title": self.schema.get("title", "Unknown"),
            "schema_version": self.schema.get("$schema", "Unknown")
        }

