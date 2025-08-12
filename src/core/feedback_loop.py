"""
Feedback Loop System for Biomedical Text Agent

This module implements a comprehensive feedback loop that compares predictions
with ground truth, calculates metrics, analyzes errors, and generates
improvement rules for the RAG system.

Location: src/core/feedback_loop.py
"""

import json
import logging
import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re


@dataclass
class FieldMetrics:
    """Metrics for a specific field."""
    field_name: str
    precision: float
    recall: float
    accuracy: float
    completeness: float
    total_predictions: int
    total_ground_truth: int
    correct_predictions: int
    missing_predictions: int
    extra_predictions: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ErrorPattern:
    """Represents an identified error pattern."""
    pattern_id: str
    field_name: str
    pattern_description: str
    frequency: int
    examples: List[Dict[str, Any]]
    suggested_rule: str
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationResult:
    """Result of validation against ground truth."""
    overall_accuracy: float
    field_metrics: Dict[str, FieldMetrics]
    error_patterns: List[ErrorPattern]
    improvement_suggestions: List[str]
    total_records: int
    successful_records: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'overall_accuracy': self.overall_accuracy,
            'field_metrics': {k: v.to_dict() for k, v in self.field_metrics.items()},
            'error_patterns': [p.to_dict() for p in self.error_patterns],
            'improvement_suggestions': self.improvement_suggestions,
            'total_records': self.total_records,
            'successful_records': self.successful_records
        }


class FeedbackLoop:
    """
    Main feedback loop system for validation and continuous improvement.
    """
    
    def __init__(self, storage_path: str = "data/feedback"):
        """
        Initialize feedback loop system.
        
        Args:
            storage_path: Path to store feedback data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Database for storing metrics and patterns
        self.db_path = self.storage_path / "feedback.db"
        self._init_database()
        
        # Field mappings for normalization
        self.field_mappings = self._init_field_mappings()
        
        logging.info("Feedback loop system initialized")
    
    def _init_database(self):
        """Initialize SQLite database for feedback data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Validation runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validation_runs (
                    run_id TEXT PRIMARY KEY,
                    model_name TEXT,
                    total_records INTEGER,
                    overall_accuracy REAL,
                    created_at TEXT
                )
            """)
            
            # Field metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS field_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT,
                    field_name TEXT,
                    precision_score REAL,
                    recall_score REAL,
                    accuracy_score REAL,
                    completeness_score REAL,
                    total_predictions INTEGER,
                    total_ground_truth INTEGER,
                    correct_predictions INTEGER,
                    FOREIGN KEY (run_id) REFERENCES validation_runs (run_id)
                )
            """)
            
            # Error patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    field_name TEXT,
                    pattern_description TEXT,
                    frequency INTEGER,
                    suggested_rule TEXT,
                    confidence REAL,
                    created_at TEXT,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Error examples table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_examples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT,
                    predicted_value TEXT,
                    ground_truth_value TEXT,
                    context_text TEXT,
                    FOREIGN KEY (pattern_id) REFERENCES error_patterns (pattern_id)
                )
            """)
            
            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_run ON field_metrics(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_field ON error_patterns(field_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_examples_pattern ON error_examples(pattern_id)")
            
            conn.commit()
    
    def _init_field_mappings(self) -> Dict[str, List[str]]:
        """Initialize field name mappings for normalization."""
        return {
            'sex': ['sex', 'gender', 'male', 'female'],
            'age_of_onset': ['age_of_onset', 'onset_age', 'age_onset', 'symptom_onset'],
            'age_at_diagnosis': ['age_at_diagnosis', 'diagnosis_age', 'age_diagnosis'],
            'ethnicity': ['ethnicity', 'race', 'ethnic_background', 'ancestry'],
            'consanguinity': ['consanguinity', 'consanguineous', 'related_parents'],
            'gene': ['gene', 'gene_symbol', 'gene_name'],
            'mutations': ['mutations', 'mutation', 'variant', 'variants'],
            'inheritance': ['inheritance', 'inheritance_pattern', 'mode_of_inheritance'],
            'phenotypes': ['phenotypes', 'phenotype', 'clinical_features', 'symptoms'],
            'treatment': ['treatment', 'therapy', 'medication', 'intervention'],
            'outcome': ['outcome', 'prognosis', 'survival', 'status']
        }
    
    def normalize_field_name(self, field_name: str) -> str:
        """Normalize field name to standard format."""
        field_lower = field_name.lower().strip()
        
        for standard_name, variants in self.field_mappings.items():
            if field_lower in variants:
                return standard_name
        
        return field_lower
    
    def compare_predictions(self, 
                          predictions: List[Dict[str, Any]], 
                          ground_truth: List[Dict[str, Any]],
                          model_name: str = "unknown") -> ValidationResult:
        """
        Compare predictions with ground truth and calculate metrics.
        
        Args:
            predictions: List of predicted records
            ground_truth: List of ground truth records
            model_name: Name of the model used
            
        Returns:
            ValidationResult with detailed metrics
        """
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Normalize and align records
        aligned_predictions, aligned_ground_truth = self._align_records(predictions, ground_truth)
        
        # Calculate field-level metrics
        field_metrics = {}
        all_fields = set()
        
        # Collect all field names
        for record in aligned_predictions + aligned_ground_truth:
            all_fields.update(record.keys())
        
        # Remove metadata fields
        all_fields = {f for f in all_fields if not f.startswith('_')}
        
        # Calculate metrics for each field
        for field in all_fields:
            metrics = self._calculate_field_metrics(
                field, aligned_predictions, aligned_ground_truth
            )
            field_metrics[field] = metrics
        
        # Calculate overall accuracy
        overall_accuracy = self._calculate_overall_accuracy(aligned_predictions, aligned_ground_truth)
        
        # Analyze error patterns
        error_patterns = self.analyze_errors(aligned_predictions, aligned_ground_truth)
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(field_metrics, error_patterns)
        
        # Create validation result
        result = ValidationResult(
            overall_accuracy=overall_accuracy,
            field_metrics=field_metrics,
            error_patterns=error_patterns,
            improvement_suggestions=improvement_suggestions,
            total_records=len(aligned_ground_truth),
            successful_records=len(aligned_predictions)
        )
        
        # Store results in database
        self._store_validation_result(run_id, result, model_name)
        
        return result
    
    def _align_records(self, 
                      predictions: List[Dict[str, Any]], 
                      ground_truth: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Align prediction and ground truth records."""
        # Simple alignment by index for now
        # In a more sophisticated system, you might align by patient ID or other identifiers
        
        min_length = min(len(predictions), len(ground_truth))
        
        aligned_predictions = []
        aligned_ground_truth = []
        
        for i in range(min_length):
            pred = predictions[i].copy()
            truth = ground_truth[i].copy()
            
            # Normalize field names
            normalized_pred = {}
            for key, value in pred.items():
                normalized_key = self.normalize_field_name(key)
                normalized_pred[normalized_key] = value
            
            normalized_truth = {}
            for key, value in truth.items():
                normalized_key = self.normalize_field_name(key)
                normalized_truth[normalized_key] = value
            
            aligned_predictions.append(normalized_pred)
            aligned_ground_truth.append(normalized_truth)
        
        return aligned_predictions, aligned_ground_truth
    
    def _calculate_field_metrics(self, 
                                field_name: str, 
                                predictions: List[Dict[str, Any]], 
                                ground_truth: List[Dict[str, Any]]) -> FieldMetrics:
        """Calculate metrics for a specific field."""
        pred_values = []
        truth_values = []
        
        # Extract values for this field
        for pred, truth in zip(predictions, ground_truth):
            pred_val = pred.get(field_name)
            truth_val = truth.get(field_name)
            
            pred_values.append(pred_val)
            truth_values.append(truth_val)
        
        # Calculate metrics
        total_predictions = sum(1 for v in pred_values if v is not None and v != "")
        total_ground_truth = sum(1 for v in truth_values if v is not None and v != "")
        
        correct_predictions = 0
        for pred_val, truth_val in zip(pred_values, truth_values):
            if self._values_match(pred_val, truth_val):
                correct_predictions += 1
        
        # Calculate precision, recall, accuracy
        precision = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        recall = correct_predictions / total_ground_truth if total_ground_truth > 0 else 0.0
        accuracy = correct_predictions / len(predictions) if len(predictions) > 0 else 0.0
        
        # Calculate completeness (how many ground truth values were predicted)
        completeness = total_predictions / total_ground_truth if total_ground_truth > 0 else 0.0
        
        missing_predictions = total_ground_truth - correct_predictions
        extra_predictions = total_predictions - correct_predictions
        
        return FieldMetrics(
            field_name=field_name,
            precision=precision,
            recall=recall,
            accuracy=accuracy,
            completeness=completeness,
            total_predictions=total_predictions,
            total_ground_truth=total_ground_truth,
            correct_predictions=correct_predictions,
            missing_predictions=missing_predictions,
            extra_predictions=extra_predictions
        )
    
    def _values_match(self, pred_val: Any, truth_val: Any) -> bool:
        """Check if predicted and ground truth values match."""
        if pred_val is None and truth_val is None:
            return True
        
        if pred_val is None or truth_val is None:
            return False
        
        # Convert to strings for comparison
        pred_str = str(pred_val).strip().lower()
        truth_str = str(truth_val).strip().lower()
        
        if pred_str == truth_str:
            return True
        
        # Handle numeric values
        try:
            pred_num = float(pred_str)
            truth_num = float(truth_str)
            return abs(pred_num - truth_num) < 0.01
        except (ValueError, TypeError):
            pass
        
        # Handle lists/arrays
        if isinstance(pred_val, (list, tuple)) and isinstance(truth_val, (list, tuple)):
            pred_set = set(str(v).strip().lower() for v in pred_val)
            truth_set = set(str(v).strip().lower() for v in truth_val)
            return pred_set == truth_set
        
        # Fuzzy matching for strings
        if len(pred_str) > 3 and len(truth_str) > 3:
            # Simple substring matching
            return pred_str in truth_str or truth_str in pred_str
        
        return False
    
    def _calculate_overall_accuracy(self, 
                                  predictions: List[Dict[str, Any]], 
                                  ground_truth: List[Dict[str, Any]]) -> float:
        """Calculate overall accuracy across all fields."""
        total_comparisons = 0
        correct_comparisons = 0
        
        for pred, truth in zip(predictions, ground_truth):
            all_fields = set(pred.keys()) | set(truth.keys())
            
            for field in all_fields:
                if not field.startswith('_'):  # Skip metadata fields
                    total_comparisons += 1
                    if self._values_match(pred.get(field), truth.get(field)):
                        correct_comparisons += 1
        
        return correct_comparisons / total_comparisons if total_comparisons > 0 else 0.0
    
    def analyze_errors(self, 
                      predictions: List[Dict[str, Any]], 
                      ground_truth: List[Dict[str, Any]]) -> List[ErrorPattern]:
        """Analyze errors and identify patterns."""
        error_patterns = []
        field_errors = defaultdict(list)
        
        # Collect errors by field
        for i, (pred, truth) in enumerate(zip(predictions, ground_truth)):
            all_fields = set(pred.keys()) | set(truth.keys())
            
            for field in all_fields:
                if field.startswith('_'):  # Skip metadata
                    continue
                
                pred_val = pred.get(field)
                truth_val = truth.get(field)
                
                if not self._values_match(pred_val, truth_val):
                    error_info = {
                        'record_index': i,
                        'field': field,
                        'predicted': pred_val,
                        'ground_truth': truth_val,
                        'context': pred.get('_context', '')
                    }
                    field_errors[field].append(error_info)
        
        # Analyze patterns for each field
        for field, errors in field_errors.items():
            patterns = self._identify_error_patterns(field, errors)
            error_patterns.extend(patterns)
        
        return error_patterns
    
    def _identify_error_patterns(self, field_name: str, errors: List[Dict[str, Any]]) -> List[ErrorPattern]:
        """Identify patterns in errors for a specific field."""
        patterns = []
        
        if not errors:
            return patterns
        
        # Pattern 1: Missing values (predicted None/empty when truth has value)
        missing_errors = [e for e in errors if (e['predicted'] is None or e['predicted'] == '') and e['ground_truth']]
        if missing_errors:
            pattern = ErrorPattern(
                pattern_id=f"{field_name}_missing_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                field_name=field_name,
                pattern_description=f"Missing {field_name} values when ground truth exists",
                frequency=len(missing_errors),
                examples=missing_errors[:5],
                suggested_rule=f"Always extract {field_name} when mentioned in text. Look for synonyms and alternative phrasings.",
                confidence=0.8
            )
            patterns.append(pattern)
        
        # Pattern 2: Extra values (predicted value when truth is None/empty)
        extra_errors = [e for e in errors if e['predicted'] and (e['ground_truth'] is None or e['ground_truth'] == '')]
        if extra_errors:
            pattern = ErrorPattern(
                pattern_id=f"{field_name}_extra_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                field_name=field_name,
                pattern_description=f"Extracting {field_name} when not present in ground truth",
                frequency=len(extra_errors),
                examples=extra_errors[:5],
                suggested_rule=f"Be more conservative when extracting {field_name}. Only extract when explicitly stated.",
                confidence=0.7
            )
            patterns.append(pattern)
        
        # Pattern 3: Value mismatches
        mismatch_errors = [e for e in errors if e['predicted'] and e['ground_truth'] and 
                          e['predicted'] != e['ground_truth']]
        if mismatch_errors:
            # Analyze common mismatch types
            mismatch_types = defaultdict(list)
            for error in mismatch_errors:
                mismatch_type = self._categorize_mismatch(error['predicted'], error['ground_truth'])
                mismatch_types[mismatch_type].append(error)
            
            for mismatch_type, type_errors in mismatch_types.items():
                if len(type_errors) >= 2:  # Only create pattern if multiple occurrences
                    pattern = ErrorPattern(
                        pattern_id=f"{field_name}_{mismatch_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        field_name=field_name,
                        pattern_description=f"{field_name} {mismatch_type} mismatch",
                        frequency=len(type_errors),
                        examples=type_errors[:5],
                        suggested_rule=self._generate_mismatch_rule(field_name, mismatch_type, type_errors),
                        confidence=0.6
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _categorize_mismatch(self, predicted: Any, ground_truth: Any) -> str:
        """Categorize the type of mismatch between predicted and ground truth."""
        pred_str = str(predicted).lower().strip()
        truth_str = str(ground_truth).lower().strip()
        
        # Numeric vs text
        try:
            float(pred_str)
            if not pred_str.replace('.', '').isdigit():
                return "format_mismatch"
        except ValueError:
            pass
        
        # Case mismatch
        if pred_str == truth_str:
            return "case_mismatch"
        
        # Partial match
        if pred_str in truth_str or truth_str in pred_str:
            return "partial_match"
        
        # Length difference
        if abs(len(pred_str) - len(truth_str)) > 10:
            return "length_mismatch"
        
        return "value_mismatch"
    
    def _generate_mismatch_rule(self, field_name: str, mismatch_type: str, errors: List[Dict[str, Any]]) -> str:
        """Generate a rule to address a specific mismatch type."""
        rules = {
            "case_mismatch": f"Ensure consistent case formatting for {field_name}",
            "partial_match": f"Extract complete {field_name} values, not partial matches",
            "format_mismatch": f"Use consistent format for {field_name} (numeric vs text)",
            "length_mismatch": f"Avoid truncating or over-expanding {field_name} values",
            "value_mismatch": f"Improve accuracy for {field_name} extraction"
        }
        
        return rules.get(mismatch_type, f"Review {field_name} extraction methodology")
    
    def _generate_improvement_suggestions(self, 
                                        field_metrics: Dict[str, FieldMetrics], 
                                        error_patterns: List[ErrorPattern]) -> List[str]:
        """Generate improvement suggestions based on metrics and patterns."""
        suggestions = []
        
        # Suggestions based on field metrics
        for field_name, metrics in field_metrics.items():
            if metrics.precision < 0.7:
                suggestions.append(f"Improve precision for {field_name} (currently {metrics.precision:.2f})")
            
            if metrics.recall < 0.7:
                suggestions.append(f"Improve recall for {field_name} (currently {metrics.recall:.2f})")
            
            if metrics.completeness < 0.5:
                suggestions.append(f"Increase completeness for {field_name} (currently {metrics.completeness:.2f})")
        
        # Suggestions based on error patterns
        pattern_counts = defaultdict(int)
        for pattern in error_patterns:
            pattern_counts[pattern.field_name] += pattern.frequency
        
        for field_name, error_count in pattern_counts.items():
            if error_count > 5:
                suggestions.append(f"Address frequent errors in {field_name} ({error_count} errors)")
        
        # General suggestions
        if len(suggestions) == 0:
            suggestions.append("Overall performance is good. Continue monitoring.")
        
        return suggestions
    
    def _store_validation_result(self, run_id: str, result: ValidationResult, model_name: str):
        """Store validation result in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store validation run
            cursor.execute("""
                INSERT INTO validation_runs (run_id, model_name, total_records, overall_accuracy, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                run_id,
                model_name,
                result.total_records,
                result.overall_accuracy,
                datetime.now().isoformat()
            ))
            
            # Store field metrics
            for field_name, metrics in result.field_metrics.items():
                cursor.execute("""
                    INSERT INTO field_metrics 
                    (run_id, field_name, precision_score, recall_score, accuracy_score, 
                     completeness_score, total_predictions, total_ground_truth, correct_predictions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id,
                    field_name,
                    metrics.precision,
                    metrics.recall,
                    metrics.accuracy,
                    metrics.completeness,
                    metrics.total_predictions,
                    metrics.total_ground_truth,
                    metrics.correct_predictions
                ))
            
            # Store error patterns
            for pattern in result.error_patterns:
                cursor.execute("""
                    INSERT OR REPLACE INTO error_patterns 
                    (pattern_id, field_name, pattern_description, frequency, suggested_rule, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_id,
                    pattern.field_name,
                    pattern.pattern_description,
                    pattern.frequency,
                    pattern.suggested_rule,
                    pattern.confidence,
                    datetime.now().isoformat()
                ))
                
                # Store error examples
                for example in pattern.examples:
                    cursor.execute("""
                        INSERT INTO error_examples 
                        (pattern_id, predicted_value, ground_truth_value, context_text)
                        VALUES (?, ?, ?, ?)
                    """, (
                        pattern.pattern_id,
                        str(example.get('predicted', '')),
                        str(example.get('ground_truth', '')),
                        str(example.get('context', ''))
                    ))
            
            conn.commit()
    
    def generate_report(self, result: ValidationResult) -> str:
        """Generate a human-readable report from validation results."""
        report = []
        report.append("=" * 60)
        report.append("VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Overall Accuracy: {result.overall_accuracy:.2%}")
        report.append(f"Total Records: {result.total_records}")
        report.append(f"Successful Records: {result.successful_records}")
        report.append("")
        
        # Field-level metrics
        report.append("FIELD-LEVEL METRICS")
        report.append("-" * 30)
        for field_name, metrics in result.field_metrics.items():
            report.append(f"{field_name}:")
            report.append(f"  Precision: {metrics.precision:.2%}")
            report.append(f"  Recall: {metrics.recall:.2%}")
            report.append(f"  Accuracy: {metrics.accuracy:.2%}")
            report.append(f"  Completeness: {metrics.completeness:.2%}")
            report.append("")
        
        # Error patterns
        if result.error_patterns:
            report.append("ERROR PATTERNS")
            report.append("-" * 30)
            for pattern in result.error_patterns:
                report.append(f"{pattern.pattern_description} (frequency: {pattern.frequency})")
                report.append(f"  Suggested rule: {pattern.suggested_rule}")
                report.append("")
        
        # Improvement suggestions
        if result.improvement_suggestions:
            report.append("IMPROVEMENT SUGGESTIONS")
            report.append("-" * 30)
            for suggestion in result.improvement_suggestions:
                report.append(f"• {suggestion}")
            report.append("")
        
        return "\n".join(report)
    
    def get_historical_metrics(self, field_name: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get historical metrics for analysis."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if field_name:
                cursor.execute("""
                    SELECT vr.run_id, vr.model_name, vr.created_at, fm.*
                    FROM validation_runs vr
                    JOIN field_metrics fm ON vr.run_id = fm.run_id
                    WHERE fm.field_name = ?
                    ORDER BY vr.created_at DESC
                    LIMIT ?
                """, (field_name, limit))
            else:
                cursor.execute("""
                    SELECT vr.run_id, vr.model_name, vr.created_at, vr.overall_accuracy
                    FROM validation_runs vr
                    ORDER BY vr.created_at DESC
                    LIMIT ?
                """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results

