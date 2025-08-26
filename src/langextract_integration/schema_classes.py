"""
LangExtract Schema Classes

Defines extraction classes that align with the biomedical table schema
for structured information extraction from medical literature.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ExtractionClass:
    """Base class for LangExtract extraction schemas."""
    extraction_class: str
    description: str
    attributes: List[Dict[str, Any]]
    few_shot_examples: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for LangExtract."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class Mutation(ExtractionClass):
    """Mutation extraction class for genetic variants."""
    
    def __init__(self):
        super().__init__(
            extraction_class="Mutation",
            description="A single genetic mutation, preferably in HGVS syntax if present.",
            attributes=[
                {
                    "name": "gene",
                    "description": "HGNC gene symbol if stated (e.g., SURF1, MT-ATP6)",
                    "type": "string",
                    "nullable": True
                },
                {
                    "name": "cdna",
                    "description": "cDNA notation if stated (e.g., c.26T>C, c.1276_1278delTAC)",
                    "type": "string",
                    "nullable": True
                },
                {
                    "name": "protein",
                    "description": "Protein notation if stated (e.g., p.Leu9Pro, p.Val426del)",
                    "type": "string",
                    "nullable": True
                },
                {
                    "name": "zygosity",
                    "description": "Zygosity if explicitly stated in text",
                    "type": "string",
                    "enum": ["homozygous", "heterozygous", "compound_het", "unknown"],
                    "default": "unknown"
                },
                {
                    "name": "inheritance",
                    "description": "Inheritance pattern if mentioned",
                    "type": "string",
                    "enum": ["autosomal_recessive", "autosomal_dominant", "x_linked", "mitochondrial", "unknown"],
                    "nullable": True
                }
            ]
        )


class PhenotypeMention(ExtractionClass):
    """Phenotype mention extraction class for clinical signs and symptoms."""
    
    def __init__(self):
        super().__init__(
            extraction_class="PhenotypeMention",
            description="One clinical phenotype, sign, or symptom from the text.",
            attributes=[
                {
                    "name": "surface_form",
                    "description": "Verbatim short phrase for the phenotype (e.g., 'generalized weakness', 'developmental delay')",
                    "type": "string"
                },
                {
                    "name": "negated",
                    "description": "Whether explicitly negated in text (e.g., 'no seizures', 'without fever')",
                    "type": "boolean",
                    "default": False
                },
                {
                    "name": "onset_age_years",
                    "description": "Numeric years if a local onset age is implied. Convert months to decimal years (e.g., 5 months → 0.42)",
                    "type": "number",
                    "minimum": 0,
                    "nullable": True
                },
                {
                    "name": "severity",
                    "description": "Severity if explicitly mentioned",
                    "type": "string",
                    "enum": ["mild", "moderate", "severe", "unknown"],
                    "nullable": True
                },
                {
                    "name": "hpo_id",
                    "description": "HPO ID if explicitly mentioned in text (do not infer)",
                    "type": "string",
                    "pattern": "^HP:\\d{7}$",
                    "nullable": True
                }
            ]
        )


class TreatmentEvent(ExtractionClass):
    """Treatment event extraction class for therapies and interventions."""
    
    def __init__(self):
        super().__init__(
            extraction_class="TreatmentEvent",
            description="Therapy, intervention, and immediate clinical outcome.",
            attributes=[
                {
                    "name": "therapy",
                    "description": "Drug(s) or therapy names (e.g., 'thiamine', 'coenzyme Q10', 'physical therapy')",
                    "type": "string"
                },
                {
                    "name": "dose",
                    "description": "Dose if explicitly stated (e.g., '100 mg/day', 'high-dose')",
                    "type": "string",
                    "nullable": True
                },
                {
                    "name": "route",
                    "description": "Route of administration if stated",
                    "type": "string",
                    "enum": ["oral", "iv", "im", "topical", "inhalation", "unknown"],
                    "nullable": True
                },
                {
                    "name": "duration",
                    "description": "Treatment duration if mentioned",
                    "type": "string",
                    "nullable": True
                },
                {
                    "name": "outcome",
                    "description": "Brief text outcome (e.g., 'improvement', 'no response', 'stabilization', 'death')",
                    "type": "string",
                    "nullable": True
                },
                {
                    "name": "response_time",
                    "description": "Time to response if mentioned",
                    "type": "string",
                    "nullable": True
                }
            ]
        )


class PatientRecord(ExtractionClass):
    """Top-level patient record extraction class."""
    
    def __init__(self):
        super().__init__(
            extraction_class="PatientRecord",
            description="All fields needed to build one structured row for a single patient.",
            attributes=[
                {
                    "name": "patient_label",
                    "type": "string",
                    "description": "Patient identifier from text (e.g., 'Patient 2', 'Case 1', 'P1')"
                },
                {
                    "name": "sex",
                    "type": "string",
                    "enum": ["m", "f"],
                    "description": "Map male→'m', female→'f' if stated. Use exact text indicators: girl/woman/female→'f', boy/man/male→'m'",
                    "nullable": True
                },
                {
                    "name": "age_of_onset_years",
                    "type": "number",
                    "minimum": 0,
                    "description": "Age at symptom onset in years. Convert months to decimal years (e.g., 5 months → 0.42). Use earliest age if multiple onsets described.",
                    "nullable": True
                },
                {
                    "name": "age_at_diagnosis_years",
                    "type": "number",
                    "minimum": 0,
                    "description": "Age at diagnosis in years if different from onset",
                    "nullable": True
                },
                {
                    "name": "last_seen_age_years",
                    "type": "number",
                    "minimum": 0,
                    "description": "Age at last follow-up in years",
                    "nullable": True
                },
                {
                    "name": "alive_flag",
                    "type": "integer",
                    "enum": [0, 1],
                    "description": "0=alive, 1=deceased. Only set to 1 if death is explicitly mentioned."
                },
                {
                    "name": "consanguinity",
                    "type": "boolean",
                    "description": "Whether consanguineous parents are mentioned",
                    "nullable": True
                },
                {
                    "name": "family_history",
                    "type": "string",
                    "description": "Brief family history if mentioned",
                    "nullable": True
                },
                {
                    "name": "mutations",
                    "type": "array",
                    "items_class": "Mutation",
                    "description": "Array of genetic mutations found in this patient"
                },
                {
                    "name": "phenotypes",
                    "type": "array", 
                    "items_class": "PhenotypeMention",
                    "description": "Array of clinical phenotypes observed in this patient"
                },
                {
                    "name": "treatments",
                    "type": "array",
                    "items_class": "TreatmentEvent", 
                    "description": "Array of treatments and interventions for this patient"
                }
            ],
            few_shot_examples=[
                {
                    "extraction_text": "Patient 1 was a 4-month-old female with Leigh syndrome. She had SLC19A3 c.1276_1278delTAC (p.Val426del) mutation. She presented with encephalopathy and was treated with thiamine and biotin with improvement. She is alive at last follow-up.",
                    "extractions": [
                        {
                            "PatientRecord": {
                                "patient_label": "Patient 1",
                                "sex": "f",
                                "age_of_onset_years": 0.33,
                                "age_at_diagnosis_years": None,
                                "last_seen_age_years": None,
                                "alive_flag": 0,
                                "consanguinity": None,
                                "family_history": None,
                                "mutations": [
                                    {
                                        "Mutation": {
                                            "gene": "SLC19A3",
                                            "cdna": "c.1276_1278delTAC",
                                            "protein": "p.Val426del",
                                            "zygosity": "unknown",
                                            "inheritance": None
                                        }
                                    }
                                ],
                                "phenotypes": [
                                    {
                                        "PhenotypeMention": {
                                            "surface_form": "encephalopathy",
                                            "negated": False,
                                            "onset_age_years": 0.33,
                                            "severity": None,
                                            "hpo_id": None
                                        }
                                    }
                                ],
                                "treatments": [
                                    {
                                        "TreatmentEvent": {
                                            "therapy": "thiamine and biotin",
                                            "dose": None,
                                            "route": None,
                                            "duration": None,
                                            "outcome": "improvement",
                                            "response_time": None
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        )


class BiomedicExtractionClasses:
    """Container for all biomedical extraction classes."""
    
    def __init__(self):
        """Initialize all extraction classes."""
        self.mutation = Mutation()
        self.phenotype = PhenotypeMention()
        self.treatment = TreatmentEvent()
        self.patient_record = PatientRecord()
        
        # Map class names to instances
        self.classes = {
            "Mutation": self.mutation,
            "PhenotypeMention": self.phenotype,
            "TreatmentEvent": self.treatment,
            "PatientRecord": self.patient_record
        }
    
    def get_class(self, class_name: str) -> ExtractionClass:
        """Get extraction class by name."""
        if class_name not in self.classes:
            raise ValueError(f"Unknown extraction class: {class_name}")
        return self.classes[class_name]
    
    def get_all_classes(self) -> List[ExtractionClass]:
        """Get all extraction classes."""
        return list(self.classes.values())
    
    def save_to_files(self, output_dir: Path):
        """Save all classes to JSON files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for class_name, extraction_class in self.classes.items():
            file_path = output_dir / f"{class_name.lower()}.json"
            with open(file_path, 'w') as f:
                f.write(extraction_class.to_json())
    
    def load_from_files(self, input_dir: Path):
        """Load classes from JSON files (for customization)."""
        input_dir = Path(input_dir)
        
        for class_name in self.classes.keys():
            file_path = input_dir / f"{class_name.lower()}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    class_data = json.load(f)
                    # Update the class with loaded data
                    self.classes[class_name] = ExtractionClass(**class_data)


# Global system prompt for LangExtract
BIOMEDICAL_SYSTEM_PROMPT = """
You are a biomedical information extraction agent. Extract only facts that are explicitly stated in the provided context.

CORE RULES:
1. If a value is missing in the context, return null or an empty list (do not infer or hallucinate).
2. Return strictly valid JSON that conforms to the attribute schemas and enumerations.
3. Use exact text spans for extraction_text (no paraphrasing).
4. For genes: use official HGNC symbols when possible (e.g., SURF1, MT-ATP6, SLC19A3).
5. For variants: use HGVS notation if present (c.26T>C, p.Leu9Pro).
6. For phenotypes: keep the concise surface form from text (we will map to HPO downstream).
7. For ages: convert months to decimal years (5 months → 0.42, 2 years 5 months → 2.42).
8. For negation: set negated=true only if explicit negation words apply (no, without, denies, absent).
9. For zygosity: only specify if words like 'homozygous', 'heterozygous', or 'compound' appear.
10. For outcomes: use brief, factual descriptions (improvement, no response, stabilization, death).

PATIENT IDENTIFICATION:
- Look for patient identifiers like "Patient 1", "Case 2", "P1", "Subject A"
- If multiple patients in text, extract each separately
- Maintain patient_id consistency across all extractions for the same patient

QUALITY CONTROL:
- Double-check that all extracted information is explicitly stated in the source text
- Ensure JSON structure matches the defined schema exactly
- Verify that enums use only allowed values
- Confirm that numeric fields contain valid numbers
"""


# Example usage and testing
if __name__ == "__main__":
    # Create extraction classes
    classes = BiomedicExtractionClasses()
    
    # Save to files for inspection
    output_dir = Path("extraction_classes")
    classes.save_to_files(output_dir)
    
    print("Extraction classes created and saved to:", output_dir)
    
    # Print patient record schema for verification
    print("\nPatientRecord schema:")
    print(classes.patient_record.to_json())

