# 📋 Models Module - Biomedical Text Agent

> **Protein Structures: Data Models & Schemas Defining Medical Information Organization**

The models module serves as the **"protein structures"** of the Biomedical Text Agent, defining the shape, organization, and relationships of all medical data that flows through the system, ensuring consistency and enabling meaningful analysis.

## 🏗️ **Biological Purpose & Architecture**

### **Protein Structure Analogy**
Like proteins that define biological function, the models module:
- **Defines** data structure (like protein folding patterns)
- **Enables** function (like protein catalytic activity)
- **Maintains** consistency (like protein stability)
- **Facilitates** interactions (like protein-protein binding)

## 📁 **Module Components & Medical Context**

### **🏗️ Data Schemas** (`schemas.py`)
**Biological Purpose**: "Structural blueprint" defining data organization

- **Function**: Defines the structure and validation rules for all medical data
- **Medical Analogy**: Like **anatomical structures** defining how body parts are organized
- **Key Features**:
  - Patient data models
  - Genetic information schemas
  - Phenotype and clinical data structures
  - Treatment and outcome models
  - Document and metadata schemas

**Medical Use Case**: Ensuring consistent data structure across different research studies and clinical reports

### **📊 Data Models** (Various model classes)
**Biological Purpose**: "Functional units" implementing specific data structures

- **Function**: Concrete implementations of data schemas with validation and methods
- **Medical Analogy**: Like **functional proteins** carrying out specific biological tasks
- **Key Features**:
  - Data validation and cleaning
  - Serialization and deserialization
  - Business logic and calculations
  - Integration with external systems
  - Performance optimization

**Medical Use Case**: Processing and validating medical data from various sources

## 🧬 **Biological Data Flow**

### **1. Data Definition**
```
Medical Concepts → Schema Design → Model Implementation → Validation Rules
```

**Biological Analogy**: Like **gene expression** creating protein structures

### **2. Data Validation**
```
Input Data → Schema Validation → Data Cleaning → Quality Assurance
```

**Biological Analogy**: Like **protein quality control** ensuring proper folding

### **3. Data Processing**
```
Validated Data → Model Processing → Business Logic → Output Generation
```

**Biological Analogy**: Like **protein function** carrying out biological processes

### **4. Data Integration**
```
Processed Data → Schema Compliance → System Integration → Knowledge Synthesis
```

**Biological Analogy**: Like **protein interactions** creating functional networks

## 🔬 **Medical Research Applications**

### **Patient Data Management**
- **Demographic Information**: Age, sex, ethnicity, family history
- **Clinical Data**: Symptoms, diagnoses, treatments, outcomes
- **Genetic Information**: Variants, mutations, inheritance patterns
- **Temporal Data**: Disease progression, treatment timelines

### **Research Data Organization**
- **Literature Metadata**: Paper information, authors, citations
- **Study Design**: Methodology, population, interventions
- **Results Data**: Outcomes, statistics, significance
- **Quality Metrics**: Confidence scores, validation results

### **System Integration**
- **API Communication**: Request/response data structures
- **Database Storage**: Table schemas and relationships
- **External Systems**: Integration with medical databases
- **Data Export**: Standardized output formats

## 🚀 **Technical Implementation**

### **Schema Architecture**
- **Pydantic Models**: Python data validation and serialization
- **Type Hints**: Clear data type definitions and documentation
- **Validation Rules**: Automated data quality checks
- **Serialization**: JSON, XML, and other format support

### **Data Validation**
- **Type Checking**: Ensuring correct data types
- **Range Validation**: Checking value boundaries
- **Format Validation**: Verifying data formats
- **Business Rules**: Enforcing domain-specific constraints

### **Performance Features**
- **Lazy Loading**: Efficient data loading and processing
- **Caching**: Intelligent caching of frequently accessed data
- **Optimization**: Memory and CPU usage optimization
- **Scalability**: Handling large datasets efficiently

## 📊 **Data Model Examples**

### **Patient Demographics Model**
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class PatientDemographics(BaseModel):
    """Patient demographic information model."""
    
    patient_id: str = Field(..., description="Unique patient identifier")
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    sex: str = Field(..., regex="^(M|F|Other)$", description="Patient sex")
    ethnicity: Optional[str] = Field(None, description="Patient ethnicity")
    consanguinity: bool = Field(False, description="Parental consanguinity")
    family_history: Optional[str] = Field(None, description="Family medical history")
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": "P001",
                "age": 25,
                "sex": "F",
                "ethnicity": "Caucasian",
                "consanguinity": False,
                "family_history": "Mother with diabetes"
            }
        }
```

### **Genetic Variant Model**
```python
class GeneticVariant(BaseModel):
    """Genetic variant information model."""
    
    variant_id: str = Field(..., description="Unique variant identifier")
    gene_symbol: str = Field(..., description="Gene symbol (e.g., NDUFS2)")
    chromosome: str = Field(..., description="Chromosome location")
    position: int = Field(..., description="Genomic position")
    reference_allele: str = Field(..., description="Reference allele sequence")
    alternate_allele: str = Field(..., description="Alternate allele sequence")
    variant_type: str = Field(..., description="Type of variant (SNV, INDEL, etc.)")
    pathogenicity: Optional[str] = Field(None, description="Pathogenicity assessment")
    inheritance: Optional[str] = Field(None, description="Inheritance pattern")
    
    class Config:
        schema_extra = {
            "example": {
                "variant_id": "VAR001",
                "gene_symbol": "NDUFS2",
                "chromosome": "1",
                "position": 161200000,
                "reference_allele": "A",
                "alternate_allele": "G",
                "variant_type": "SNV",
                "pathogenicity": "Likely pathogenic",
                "inheritance": "Autosomal recessive"
            }
        }
```

### **Phenotype Model**
```python
class Phenotype(BaseModel):
    """Clinical phenotype information model."""
    
    phenotype_id: str = Field(..., description="Unique phenotype identifier")
    hpo_term: str = Field(..., description="HPO term identifier (e.g., HP:0001250)")
    hpo_name: str = Field(..., description="HPO term name (e.g., Seizures)")
    severity: Optional[str] = Field(None, description="Symptom severity")
    onset_age: Optional[int] = Field(None, description="Age of onset in months")
    frequency: Optional[str] = Field(None, description="Frequency in population")
    notes: Optional[str] = Field(None, description="Additional clinical notes")
    
    class Config:
        schema_extra = {
            "example": {
                "phenotype_id": "PHEN001",
                "hpo_term": "HP:0001250",
                "hpo_name": "Seizures",
                "severity": "Moderate",
                "onset_age": 24,
                "frequency": "Frequent",
                "notes": "Generalized tonic-clonic seizures"
            }
        }
```

### **Treatment Model**
```python
class Treatment(BaseModel):
    """Treatment and intervention information model."""
    
    treatment_id: str = Field(..., description="Unique treatment identifier")
    medication: str = Field(..., description="Medication or treatment name")
    dosage: Optional[str] = Field(None, description="Dosage information")
    frequency: Optional[str] = Field(None, description="Administration frequency")
    start_date: Optional[date] = Field(None, description="Treatment start date")
    end_date: Optional[date] = Field(None, description="Treatment end date")
    response: Optional[str] = Field(None, description="Treatment response")
    adverse_events: Optional[List[str]] = Field(None, description="Adverse events")
    
    class Config:
        schema_extra = {
            "example": {
                "treatment_id": "TREAT001",
                "medication": "Coenzyme Q10",
                "dosage": "100mg",
                "frequency": "Twice daily",
                "start_date": "2023-01-15",
                "end_date": None,
                "response": "Partial improvement",
                "adverse_events": ["Mild nausea"]
            }
        }
```

## 🎯 **Future Enhancements**

### **Medical Capabilities**
- **Multi-modal Data**: Support for images, genetic sequences, and lab results
- **Temporal Models**: Time-series data for disease progression
- **Population Models**: Large-scale epidemiological data structures
- **Precision Medicine**: Personalized data models and predictions

### **Technical Improvements**
- **Advanced Validation**: More sophisticated validation rules and constraints
- **Schema Evolution**: Version management and backward compatibility
- **Performance Optimization**: Faster validation and processing
- **Integration Standards**: Compliance with medical data standards

## 🔧 **Usage Examples**

### **Data Validation**
```python
from src.models.schemas import PatientDemographics

# Validate patient data
try:
    patient_data = PatientDemographics(
        patient_id="P001",
        age=25,
        sex="F",
        ethnicity="Caucasian"
    )
    print(f"Valid patient data: {patient_data.patient_id}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

### **Data Serialization**
```python
# Convert to dictionary
patient_dict = patient_data.dict()
print(f"Patient dict: {patient_dict}")

# Convert to JSON
patient_json = patient_data.json()
print(f"Patient JSON: {patient_json}")

# Convert from dictionary
new_patient = PatientDemographics(**patient_dict)
print(f"New patient: {new_patient.patient_id}")
```

### **Batch Validation**
```python
from typing import List

def validate_patients(patient_list: List[dict]) -> List[PatientDemographics]:
    """Validate a list of patient data."""
    validated_patients = []
    
    for patient_data in patient_list:
        try:
            patient = PatientDemographics(**patient_data)
            validated_patients.append(patient)
        except ValidationError as e:
            print(f"Invalid patient data: {e}")
    
    return validated_patients

# Validate multiple patients
patients_data = [
    {"patient_id": "P001", "age": 25, "sex": "F"},
    {"patient_id": "P002", "age": 30, "sex": "M"}
]

validated_patients = validate_patients(patients_data)
print(f"Validated {len(validated_patients)} patients")
```

---

**The models module represents the structural foundation of the Biomedical Text Agent - defining how medical information is organized, validated, and processed to ensure data quality and enable meaningful analysis in biomedical research.** 🧬🔬💊
