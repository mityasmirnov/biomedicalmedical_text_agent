"""
Biomedic Data Normalizer

This module normalizes LangExtract results to biomedical table schema.
"""

import logging
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Set
from pathlib import Path
from datetime import datetime

# Remove circular import
# from core.config import Config
# Import ontology managers lazily to avoid circular imports
# from ..ontologies.hpo_manager import HPOManager
# from ..ontologies.gene_manager import GeneManager


logger = logging.getLogger(__name__)


class BiomedicNormalizer:
    """
    Normalizes LangExtract results to biomedical table schema.
    
    Handles:
    - Ontology mapping (HPO, HGNC)
    - Data type normalization
    - Schema alignment
    - Quality validation
    """
    
    def __init__(self, config: Optional[Any] = None):
        """
        Initialize normalizer.
        
        Args:
            config: System configuration (optional to avoid circular imports)
        """
        self.config = config
        
        # Initialize ontology managers lazily to avoid circular imports
        self.hpo_manager = None
        self.gene_manager = None
        
        # Try to initialize ontology managers
        self._init_ontology_managers()
    
    def _init_ontology_managers(self):
        """Initialize ontology managers lazily."""
        try:
            from ontologies.hpo_manager import HPOManager
            self.hpo_manager = HPOManager()
            logger.info("HPO manager initialized")
        except Exception as e:
            logger.warning(f"HPO manager initialization failed: {e}")
            self.hpo_manager = None
        
        try:
            from ontologies.gene_manager import GeneManager
            self.gene_manager = GeneManager()
            logger.info("Gene manager initialized")
        except Exception as e:
            logger.warning(f"Gene manager initialization failed: {e}")
            self.gene_manager = None
    
    def normalize_extractions(self, extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize extraction results to table schema.
        
        Args:
            extraction_results: Raw LangExtract results
            
        Returns:
            Normalized results with schema-aligned data
        """
        logger.info("Starting normalization of extraction results")
        
        try:
            # Extract patient records from results
            patient_records = self._extract_patient_records(extraction_results)
            
            # Normalize each patient record
            normalized_records = []
            for record in patient_records:
                normalized_record = self._normalize_patient_record(record)
                if normalized_record:
                    normalized_records.append(normalized_record)
            
            # Create final result structure
            normalized_result = {
                "normalized_data": normalized_records,
                "normalization_metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_patients": len(normalized_records),
                    "hpo_mappings": self._count_hpo_mappings(normalized_records),
                    "gene_mappings": self._count_gene_mappings(normalized_records),
                    "quality_metrics": self._calculate_quality_metrics(normalized_records)
                },
                "original_extractions": extraction_results.get("extractions", []),
                "extraction_metadata": extraction_results.get("metadata", {})
            }
            
            # Add visualization if present
            if "visualization_html" in extraction_results:
                normalized_result["visualization_html"] = extraction_results["visualization_html"]
            
            logger.info(f"Normalization completed: {len(normalized_records)} patient records")
            return normalized_result
            
        except Exception as e:
            logger.error(f"Error during normalization: {e}")
            raise
    
    def _extract_patient_records(self, extraction_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract PatientRecord objects from LangExtract results.
        
        Args:
            extraction_results: Raw extraction results
            
        Returns:
            List of patient record dictionaries
        """
        patient_records = []
        
        extractions = extraction_results.get("extractions", [])
        
        for extraction in extractions:
            # Handle different extraction formats
            if isinstance(extraction, dict):
                # Look for PatientRecord class
                if "extraction_class" in extraction and extraction["extraction_class"] == "PatientRecord":
                    patient_records.append(extraction.get("attributes", {}))
                elif "PatientRecord" in extraction:
                    patient_records.append(extraction["PatientRecord"])
            
        return patient_records
    
    def _normalize_patient_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize a single patient record to table schema.
        
        Args:
            record: Raw patient record
            
        Returns:
            Normalized patient record or None if invalid
        """
        try:
            normalized = {}
            
            # Basic patient information
            normalized["patient_id"] = record.get("patient_label", "unknown")
            normalized["sex"] = self._normalize_sex(record.get("sex"))
            normalized["age_of_onset"] = self._normalize_age(record.get("age_of_onset_years"))
            normalized["age_at_diagnosis"] = self._normalize_age(record.get("age_at_diagnosis_years"))
            normalized["last_seen"] = self._normalize_age(record.get("last_seen_age_years"))
            normalized["_0_alive_1_dead"] = self._normalize_alive_flag(record.get("alive_flag"))
            normalized["consanguinity"] = record.get("consanguinity")
            normalized["family_history"] = record.get("family_history")
            
            # Process mutations
            mutations = record.get("mutations", [])
            gene_info = self._process_mutations(mutations)
            normalized.update(gene_info)
            
            # Process phenotypes
            phenotypes = record.get("phenotypes", [])
            phenotype_info = self._process_phenotypes(phenotypes)
            normalized.update(phenotype_info)
            
            # Process treatments
            treatments = record.get("treatments", [])
            treatment_info = self._process_treatments(treatments)
            normalized.update(treatment_info)
            
            # Add metadata
            normalized["extraction_timestamp"] = datetime.utcnow().isoformat()
            normalized["normalization_quality"] = self._assess_record_quality(normalized)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing patient record: {e}")
            return None
    
    def _normalize_sex(self, sex: Optional[str]) -> Optional[str]:
        """Normalize sex field."""
        if not sex:
            return None
        
        sex_lower = sex.lower().strip()
        if sex_lower in ['m', 'male', 'boy', 'man']:
            return 'm'
        elif sex_lower in ['f', 'female', 'girl', 'woman']:
            return 'f'
        else:
            return None
    
    def _normalize_age(self, age: Optional[Union[int, float, str]]) -> Optional[float]:
        """Normalize age to years."""
        if age is None:
            return None
        
        try:
            if isinstance(age, str):
                # Try to extract numeric value
                import re
                numbers = re.findall(r'\d+\.?\d*', age)
                if numbers:
                    age = float(numbers[0])
                else:
                    return None
            
            return float(age) if age >= 0 else None
            
        except (ValueError, TypeError):
            return None
    
    def _normalize_alive_flag(self, alive_flag: Optional[Union[int, str, bool]]) -> Optional[int]:
        """Normalize alive flag."""
        if alive_flag is None:
            return None
        
        if isinstance(alive_flag, bool):
            return 0 if alive_flag else 1
        elif isinstance(alive_flag, str):
            alive_lower = alive_flag.lower().strip()
            if alive_lower in ['alive', 'living', '0']:
                return 0
            elif alive_lower in ['dead', 'deceased', 'died', '1']:
                return 1
        elif isinstance(alive_flag, (int, float)):
            return int(alive_flag) if alive_flag in [0, 1] else None
        
        return None
    
    def _process_mutations(self, mutations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process mutations and normalize gene information.
        
        Args:
            mutations: List of mutation objects
            
        Returns:
            Dictionary with normalized gene information
        """
        gene_info = {
            "gene": None,
            "mutations": None,
            "zygosity": None,
            "inheritance": None
        }
        
        if not mutations:
            return gene_info
        
        # Collect all mutations
        all_genes = set()
        all_mutations = []
        zygosities = set()
        inheritances = set()
        
        for mutation in mutations:
            # Handle nested structure
            mut_data = mutation.get("Mutation", mutation)
            
            # Gene normalization
            gene = mut_data.get("gene")
            if gene and self.gene_manager:
                normalized_gene = self.gene_manager.normalize_gene_symbol(gene)
                if normalized_gene:
                    all_genes.add(normalized_gene)
                else:
                    all_genes.add(gene)
            elif gene:
                all_genes.add(gene)
            
            # Mutation notation
            cdna = mut_data.get("cdna")
            protein = mut_data.get("protein")
            
            if cdna:
                all_mutations.append(cdna)
            if protein:
                all_mutations.append(protein)
            
            # Zygosity and inheritance
            zygosity = mut_data.get("zygosity")
            if zygosity and zygosity != "unknown":
                zygosities.add(zygosity)
            
            inheritance = mut_data.get("inheritance")
            if inheritance:
                inheritances.add(inheritance)
        
        # Set normalized values
        if all_genes:
            gene_info["gene"] = "; ".join(sorted(all_genes))
        
        if all_mutations:
            gene_info["mutations"] = "; ".join(all_mutations)
        
        if zygosities:
            gene_info["zygosity"] = "; ".join(sorted(zygosities))
        
        if inheritances:
            gene_info["inheritance"] = "; ".join(sorted(inheritances))
        
        return gene_info
    
    def _process_phenotypes(self, phenotypes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process phenotypes and map to HPO terms.
        
        Args:
            phenotypes: List of phenotype objects
            
        Returns:
            Dictionary with HPO mappings and phenotype information
        """
        phenotype_info = {
            "phenotypes_text": None,
            "hpo_terms": set(),
            "negated_phenotypes": []
        }
        
        if not phenotypes:
            return phenotype_info
        
        all_phenotypes = []
        hpo_terms = set()
        negated = []
        
        for phenotype in phenotypes:
            # Handle nested structure
            pheno_data = phenotype.get("PhenotypeMention", phenotype)
            
            surface_form = pheno_data.get("surface_form")
            if not surface_form:
                continue
            
            # Check if negated
            is_negated = pheno_data.get("negated", False)
            if is_negated:
                negated.append(surface_form)
                continue
            
            all_phenotypes.append(surface_form)
            
            # HPO mapping
            hpo_id = pheno_data.get("hpo_id")
            if hpo_id:
                hpo_terms.add(hpo_id)
            elif self.hpo_manager:
                # Try to map using HPO manager
                mapped_hpo = self.hpo_manager.map_phenotype_to_hpo(surface_form)
                if mapped_hpo:
                    hpo_terms.update(mapped_hpo)
        
        # Set results
        if all_phenotypes:
            phenotype_info["phenotypes_text"] = "; ".join(all_phenotypes)
        
        phenotype_info["hpo_terms"] = hpo_terms
        phenotype_info["negated_phenotypes"] = negated
        
        # Add HPO columns (this would be expanded based on your schema)
        phenotype_info.update(self._create_hpo_columns(hpo_terms))
        
        return phenotype_info
    
    def _process_treatments(self, treatments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process treatments and outcomes.
        
        Args:
            treatments: List of treatment objects
            
        Returns:
            Dictionary with treatment information
        """
        treatment_info = {
            "treatments": None,
            "treatment_outcomes": None,
            "treatment_response": None
        }
        
        if not treatments:
            return treatment_info
        
        all_treatments = []
        all_outcomes = []
        responses = set()
        
        for treatment in treatments:
            # Handle nested structure
            treat_data = treatment.get("TreatmentEvent", treatment)
            
            therapy = treat_data.get("therapy")
            dose = treat_data.get("dose")
            outcome = treat_data.get("outcome")
            
            # Build treatment string
            if therapy:
                treatment_str = therapy
                if dose:
                    treatment_str += f" ({dose})"
                all_treatments.append(treatment_str)
            
            if outcome:
                all_outcomes.append(outcome)
                
                # Categorize response
                outcome_lower = outcome.lower()
                if any(word in outcome_lower for word in ['improve', 'better', 'response', 'stable']):
                    responses.add('improvement')
                elif any(word in outcome_lower for word in ['no response', 'failed', 'worse']):
                    responses.add('no_response')
                elif any(word in outcome_lower for word in ['death', 'died', 'fatal']):
                    responses.add('death')
        
        # Set results
        if all_treatments:
            treatment_info["treatments"] = "; ".join(all_treatments)
        
        if all_outcomes:
            treatment_info["treatment_outcomes"] = "; ".join(all_outcomes)
        
        if responses:
            treatment_info["treatment_response"] = "; ".join(sorted(responses))
        
        return treatment_info
    
    def _create_hpo_columns(self, hpo_terms: Set[str]) -> Dict[str, int]:
        """
        Create HPO binary columns based on mapped terms.
        
        Args:
            hpo_terms: Set of HPO term IDs
            
        Returns:
            Dictionary with HPO binary columns
        """
        # This would be expanded based on your specific HPO schema
        # For now, return a simplified version
        hpo_columns = {}
        
        # Common HPO terms mapping (example)
        common_hpo_mappings = {
            "HP:0001250": "seizures",
            "HP:0001263": "developmental_delay", 
            "HP:0003128": "lactic_acidosis",
            "HP:0001508": "failure_to_thrive",
            "HP:0001252": "hypotonia"
        }
        
        for hpo_id in hpo_terms:
            if hpo_id in common_hpo_mappings:
                column_name = f"hpo_{common_hpo_mappings[hpo_id]}"
                hpo_columns[column_name] = 1
        
        return hpo_columns
    
    def _assess_record_quality(self, record: Dict[str, Any]) -> float:
        """
        Assess the quality/completeness of a normalized record.
        
        Args:
            record: Normalized patient record
            
        Returns:
            Quality score between 0 and 1
        """
        total_fields = 0
        filled_fields = 0
        
        # Core fields
        core_fields = ["patient_id", "sex", "age_of_onset", "gene", "phenotypes_text"]
        
        for field in core_fields:
            total_fields += 1
            if record.get(field) is not None:
                filled_fields += 1
        
        # Additional scoring for specific content
        if record.get("mutations"):
            filled_fields += 0.5
        if record.get("hpo_terms"):
            filled_fields += 0.5
        if record.get("treatments"):
            filled_fields += 0.5
        
        total_fields += 1.5  # Account for additional scoring
        
        return min(filled_fields / total_fields, 1.0) if total_fields > 0 else 0.0
    
    def _count_hpo_mappings(self, records: List[Dict[str, Any]]) -> int:
        """Count total HPO mappings across all records."""
        total = 0
        for record in records:
            hpo_terms = record.get("hpo_terms", set())
            if isinstance(hpo_terms, (set, list)):
                total += len(hpo_terms)
        return total
    
    def _count_gene_mappings(self, records: List[Dict[str, Any]]) -> int:
        """Count records with gene information."""
        return sum(1 for record in records if record.get("gene"))
    
    def _calculate_quality_metrics(self, records: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate overall quality metrics."""
        if not records:
            return {"average_quality": 0.0, "completeness": 0.0}
        
        qualities = [record.get("normalization_quality", 0.0) for record in records]
        avg_quality = sum(qualities) / len(qualities)
        
        # Completeness based on core fields
        complete_records = sum(
            1 for record in records 
            if all(record.get(field) for field in ["patient_id", "gene", "phenotypes_text"])
        )
        completeness = complete_records / len(records)
        
        return {
            "average_quality": avg_quality,
            "completeness": completeness,
            "total_records": len(records),
            "complete_records": complete_records
        }
    
    def evaluate_against_ground_truth(
        self,
        extraction_results: Dict[str, Any],
        ground_truth_file: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Evaluate extraction results against ground truth data.
        
        Args:
            extraction_results: Normalized extraction results
            ground_truth_file: Path to ground truth CSV file
            
        Returns:
            Evaluation metrics and detailed comparison
        """
        logger.info(f"Evaluating against ground truth: {ground_truth_file}")
        
        try:
            # Load ground truth
            gt_df = pd.read_csv(ground_truth_file)
            
            # Get normalized data
            normalized_data = extraction_results.get("normalized_data", [])
            if not normalized_data:
                return {"error": "No normalized data found"}
            
            # Convert to DataFrame
            extracted_df = pd.DataFrame(normalized_data)
            
            # Perform field-by-field comparison
            evaluation = {
                "timestamp": datetime.utcnow().isoformat(),
                "ground_truth_records": len(gt_df),
                "extracted_records": len(extracted_df),
                "field_comparisons": {},
                "overall_metrics": {}
            }
            
            # Compare common fields
            common_fields = set(gt_df.columns) & set(extracted_df.columns)
            
            for field in common_fields:
                field_eval = self._evaluate_field(
                    gt_df[field], 
                    extracted_df[field] if field in extracted_df.columns else None,
                    field
                )
                evaluation["field_comparisons"][field] = field_eval
            
            # Calculate overall metrics
            evaluation["overall_metrics"] = self._calculate_overall_metrics(
                evaluation["field_comparisons"]
            )
            
            logger.info("Evaluation completed")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            return {"error": str(e)}
    
    def _evaluate_field(
        self, 
        ground_truth: pd.Series, 
        extracted: Optional[pd.Series],
        field_name: str
    ) -> Dict[str, Any]:
        """Evaluate a specific field against ground truth."""
        if extracted is None:
            return {
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "accuracy": 0.0,
                "missing": True
            }
        
        # Align series by index
        min_len = min(len(ground_truth), len(extracted))
        gt_values = ground_truth.iloc[:min_len]
        ext_values = extracted.iloc[:min_len]
        
        # Calculate metrics based on field type
        if field_name in ["sex", "_0_alive_1_dead"]:
            # Categorical field
            return self._evaluate_categorical_field(gt_values, ext_values)
        elif field_name in ["age_of_onset", "last_seen"]:
            # Numeric field
            return self._evaluate_numeric_field(gt_values, ext_values)
        else:
            # Text field
            return self._evaluate_text_field(gt_values, ext_values)
    
    def _evaluate_categorical_field(self, gt_values: pd.Series, ext_values: pd.Series) -> Dict[str, float]:
        """Evaluate categorical field."""
        # Simple accuracy for categorical
        matches = (gt_values == ext_values).sum()
        total = len(gt_values)
        accuracy = matches / total if total > 0 else 0.0
        
        return {
            "precision": accuracy,
            "recall": accuracy,
            "f1": accuracy,
            "accuracy": accuracy
        }
    
    def _evaluate_numeric_field(self, gt_values: pd.Series, ext_values: pd.Series) -> Dict[str, float]:
        """Evaluate numeric field."""
        # For numeric fields, consider values within tolerance as matches
        tolerance = 0.1  # 0.1 years tolerance for ages
        
        gt_numeric = pd.to_numeric(gt_values, errors='coerce')
        ext_numeric = pd.to_numeric(ext_values, errors='coerce')
        
        # Count matches within tolerance
        matches = 0
        total = 0
        
        for gt_val, ext_val in zip(gt_numeric, ext_numeric):
            if pd.notna(gt_val) and pd.notna(ext_val):
                total += 1
                if abs(gt_val - ext_val) <= tolerance:
                    matches += 1
        
        accuracy = matches / total if total > 0 else 0.0
        
        return {
            "precision": accuracy,
            "recall": accuracy,
            "f1": accuracy,
            "accuracy": accuracy,
            "tolerance": tolerance
        }
    
    def _evaluate_text_field(self, gt_values: pd.Series, ext_values: pd.Series) -> Dict[str, float]:
        """Evaluate text field using fuzzy matching."""
        from difflib import SequenceMatcher
        
        total_similarity = 0.0
        comparisons = 0
        
        for gt_val, ext_val in zip(gt_values, ext_values):
            if pd.notna(gt_val) and pd.notna(ext_val):
                similarity = SequenceMatcher(None, str(gt_val), str(ext_val)).ratio()
                total_similarity += similarity
                comparisons += 1
        
        avg_similarity = total_similarity / comparisons if comparisons > 0 else 0.0
        
        return {
            "precision": avg_similarity,
            "recall": avg_similarity,
            "f1": avg_similarity,
            "accuracy": avg_similarity,
            "similarity_threshold": 0.8
        }
    
    def _calculate_overall_metrics(self, field_comparisons: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """Calculate overall evaluation metrics."""
        if not field_comparisons:
            return {"overall_accuracy": 0.0, "overall_f1": 0.0}
        
        accuracies = [comp.get("accuracy", 0.0) for comp in field_comparisons.values()]
        f1_scores = [comp.get("f1", 0.0) for comp in field_comparisons.values()]
        
        return {
            "overall_accuracy": sum(accuracies) / len(accuracies),
            "overall_f1": sum(f1_scores) / len(f1_scores),
            "fields_evaluated": len(field_comparisons)
        }


# Example usage
if __name__ == "__main__":
    # Test normalization
    normalizer = BiomedicNormalizer()
    
    # Sample extraction result
    sample_result = {
        "extractions": [
            {
                "extraction_class": "PatientRecord",
                "attributes": {
                    "patient_label": "Patient 1",
                    "sex": "f",
                    "age_of_onset_years": 2.42,
                    "alive_flag": 0,
                    "mutations": [
                        {
                            "Mutation": {
                                "gene": "SLC19A3",
                                "cdna": "c.26T>C",
                                "protein": "p.Leu9Pro",
                                "zygosity": "unknown"
                            }
                        }
                    ],
                    "phenotypes": [
                        {
                            "PhenotypeMention": {
                                "surface_form": "generalized weakness",
                                "negated": False,
                                "onset_age_years": 2.42
                            }
                        }
                    ],
                    "treatments": [
                        {
                            "TreatmentEvent": {
                                "therapy": "thiamine and biotin",
                                "outcome": "improvement"
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    # Normalize
    normalized = normalizer.normalize_extractions(sample_result)
    
    print("Normalization completed!")
    print(f"Normalized {len(normalized['normalized_data'])} records")
    
    # Print first record
    if normalized["normalized_data"]:
        print("\nFirst normalized record:")
        print(json.dumps(normalized["normalized_data"][0], indent=2, default=str))

