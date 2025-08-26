# Extraction Agents API - Detailed Reference

## Overview

The Biomedical Data Extraction Engine provides specialized agents for extracting different types of information from biomedical literature. Each agent is designed to handle specific data types with domain-specific knowledge and validation.

## Table of Contents

1. [Base Agent Class](#base-agent-class)
2. [Phenotypes Agent](#phenotypes-agent)
3. [Genetics Agent](#genetics-agent)
4. [Treatments Agent](#treatments-agent)
5. [Demographics Agent](#demographics-agent)
6. [Agent Orchestration](#agent-orchestration)
7. [Custom Agent Development](#custom-agent-development)
8. [Configuration and Tuning](#configuration-and-tuning)

## Base Agent Class

**Location**: `src/core/base.py`

All extraction agents inherit from the `BaseAgent` abstract base class, which provides common functionality and interfaces.

### Abstract Methods

#### `extract(text: str) -> ProcessingResult[T]`

**Abstract method** that must be implemented by all agents.

**Parameters:**
- `text` (str): Input text to extract information from

**Returns:**
- `ProcessingResult[T]`: Extracted data or error information

### Common Properties

```python
class BaseAgent(ABC):
    agent_type: str                    # Type of agent (e.g., "phenotypes", "genetics")
    llm_client: Optional[BaseLLMClient]  # LLM client for text processing
    confidence_threshold: float        # Minimum confidence for extraction
    validation_enabled: bool          # Whether to enable validation
    extraction_metadata: Dict[str, Any]  # Metadata about extraction process
```

### Common Methods

#### `validate_extraction(data: T) -> ProcessingResult[T]`

Validates extracted data against schemas or rules.

#### `get_extraction_statistics() -> Dict[str, Any]`

Returns statistics about extraction performance.

#### `reset_statistics() -> None`

Resets extraction statistics.

## Phenotypes Agent

**Location**: `src/agents/extraction_agents/phenotypes_agent.py`

Specialized agent for extracting phenotypic information, symptoms, diagnostic findings, and laboratory values with HPO integration.

### Initialization

```python
from agents.extraction_agents.phenotypes_agent import PhenotypesAgent
from ontologies.hpo_manager import HPOManager

# Basic initialization
agent = PhenotypesAgent()

# With HPO manager
hpo_manager = HPOManager()
agent = PhenotypesAgent(
    llm_client=llm_client,
    hpo_manager=hpo_manager,
    use_optimized_hpo=True
)

# With custom configuration
agent = PhenotypesAgent(
    llm_client=llm_client,
    confidence_threshold=0.7,
    validation_enabled=True
)
```

### Methods

#### `extract_phenotypes(text: str) -> ProcessingResult[PhenotypeExtraction]`

Extracts phenotype information from biomedical text.

**Parameters:**
- `text` (str): Input text to analyze

**Returns:**
- `ProcessingResult[PhenotypeExtraction]`: Extracted phenotype data with HPO mappings

**Example:**
```python
result = await agent.extract_phenotypes(
    "Patient presented with developmental delay, hypotonia, and seizures."
)

if result.success:
    extraction = result.data
    print(f"Phenotypes: {extraction.phenotypes}")
    print(f"HPO mappings: {extraction.hpo_mappings}")
    print(f"Confidence scores: {extraction.confidence_scores}")
```

#### `normalize_phenotypes(phenotypes: List[str]) -> ProcessingResult[List[Dict[str, Any]]]`

Normalizes phenotype descriptions to HPO terms.

**Parameters:**
- `phenotypes` (List[str]): List of phenotype descriptions

**Returns:**
- `ProcessingResult[List[Dict[str, Any]]]`: Normalized HPO terms with mappings

**Example:**
```python
phenotypes = ["developmental delay", "muscle weakness", "seizures"]
result = await agent.normalize_phenotypes(phenotypes)

if result.success:
    normalized = result.data
    for norm in normalized:
        print(f"Original: {norm['original']}")
        print(f"HPO ID: {norm['hpo_id']}")
        print(f"HPO Term: {norm['hpo_term']}")
        print(f"Confidence: {norm['confidence']}")
```

#### `extract_symptoms(text: str) -> ProcessingResult[List[str]]`

Extracts symptom descriptions from text.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[List[str]]`: List of extracted symptoms

#### `extract_diagnostic_findings(text: str) -> ProcessingResult[List[str]]`

Extracts diagnostic test results and findings.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[List[str]]`: List of diagnostic findings

#### `extract_lab_values(text: str) -> ProcessingResult[List[Dict[str, Any]]]`

Extracts laboratory values with units and reference ranges.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[List[Dict[str, Any]]]`: List of lab values with metadata

**Example:**
```python
result = await agent.extract_lab_values(
    "Lactate levels were elevated at 5.2 mmol/L (normal: 0.5-2.2 mmol/L)"
)

if result.success:
    lab_values = result.data
    for lab in lab_values:
        print(f"Test: {lab['test']}")
        print(f"Value: {lab['value']} {lab['unit']}")
        print(f"Reference: {lab['reference_range']}")
        print(f"Status: {lab['status']}")  # normal, elevated, decreased
```

#### `extract_imaging_findings(text: str) -> ProcessingResult[List[str]]`

Extracts imaging study findings.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[List[str]]`: List of imaging findings

#### `get_extraction_statistics() -> Dict[str, Any]`

Returns comprehensive extraction statistics.

**Returns:**
- `Dict[str, Any]`: Statistics including success rate, average confidence, etc.

**Example:**
```python
stats = agent.get_extraction_statistics()
print(f"Total extractions: {stats['total_extractions']}")
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Average confidence: {stats['average_confidence']:.2f}")
print(f"HPO mapping rate: {stats['hpo_mapping_rate']:.2%}")
```

### Phenotype Extraction Data Structure

```python
@dataclass
class PhenotypeExtraction:
    phenotypes: List[str]                    # Raw phenotype descriptions
    symptoms: List[str]                      # Symptom descriptions
    diagnostic_findings: List[str]           # Diagnostic test results
    lab_values: List[Dict[str, Any]]        # Laboratory values
    imaging_findings: List[str]              # Imaging findings
    confidence_scores: Dict[str, float]     # Confidence for each field
    hpo_mappings: List[Dict[str, Any]]      # HPO term mappings
    extraction_metadata: Dict[str, Any]     # Extraction process metadata
```

### Pattern-Based Recognition

The Phenotypes Agent uses pattern-based recognition for common clinical terms:

```python
# Developmental patterns
developmental_patterns = [
    r'\b(?:developmental|development)\s+(?:delay|regression|disorder|abnormality)\b',
    r'\b(?:delayed|delayed)\s+(?:milestone|development|growth)\b',
    r'\b(?:failure\s+to\s+thrive|FTT)\b'
]

# Neurological patterns
neurological_patterns = [
    r'\b(?:seizure|epileptic|convulsion)\b',
    r'\b(?:muscular\s+)?hypotonia\b',
    r'\b(?:hypertonia|spasticity|rigidity)\b'
]

# Usage
text = "Patient shows developmental delay and hypotonia"
matches = agent._find_pattern_matches(text, developmental_patterns + neurological_patterns)
print(f"Pattern matches: {matches}")
```

## Genetics Agent

**Location**: `src/agents/extraction_agents/genetics_agent.py`

Specialized agent for extracting genetic information, mutations, inheritance patterns, and gene symbols.

### Initialization

```python
from agents.extraction_agents.genetics_agent import GeneticsAgent
from ontologies.gene_manager import GeneManager

# Basic initialization
agent = GeneticsAgent()

# With gene manager for normalization
gene_manager = GeneManager()
agent = GeneticsAgent(
    llm_client=llm_client,
    gene_manager=gene_manager
)
```

### Methods

#### `extract_genetics(text: str) -> ProcessingResult[Dict[str, Any]]`

Extracts comprehensive genetic information from text.

**Parameters:**
- `text` (str): Input text to analyze

**Returns:**
- `ProcessingResult[Dict[str, Any]]`: Extracted genetic data

**Example:**
```python
result = await agent.extract_genetics(
    "Patient has a homozygous mutation in the SURF1 gene, inherited in an autosomal recessive pattern."
)

if result.success:
    genetics = result.data
    print(f"Gene: {genetics['gene']}")
    print(f"Mutation: {genetics['mutation']}")
    print(f"Inheritance: {genetics['inheritance']}")
    print(f"Zygosity: {genetics['zygosity']}")
```

#### `extract_gene_symbols(text: str) -> ProcessingResult[List[str]]`

Extracts gene symbols from text.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[List[str]]`: List of extracted gene symbols

#### `extract_mutations(text: str) -> ProcessingResult[List[Dict[str, Any]]]`

Extracts specific mutation information.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[List[Dict[str, Any]]]`: List of mutations with details

**Example:**
```python
result = await agent.extract_mutations(
    "c.845_846delCT mutation in exon 8"
)

if result.success:
    mutations = result.data
    for mutation in mutations:
        print(f"Type: {mutation['type']}")  # deletion, insertion, etc.
        print(f"Position: {mutation['position']}")
        print(f"Exon: {mutation['exon']}")
        print(f"Nucleotide change: {mutation['nucleotide_change']}")
```

#### `extract_inheritance_patterns(text: str) -> ProcessingResult[List[str]]`

Extracts inheritance pattern information.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[List[str]]`: List of inheritance patterns

#### `normalize_gene_symbols(genes: List[str]) -> ProcessingResult[List[Dict[str, Any]]]`

Normalizes gene symbols to official HGNC standards.

**Parameters:**
- `genes` (List[str]): List of gene symbols to normalize

**Returns:**
- `ProcessingResult[List[Dict[str, Any]]]`: Normalized gene information

**Example:**
```python
genes = ["SURF1", "surf1", "Surf1"]
result = await agent.normalize_gene_symbols(genes)

if result.success:
    normalized = result.data
    for norm in normalized:
        print(f"Original: {norm['original']}")
        print(f"Official: {norm['official_symbol']}")
        print(f"HGNC ID: {norm['hgnc_id']}")
        print(f"Confidence: {norm['confidence']}")
```

#### `categorize_mutations(mutations: List[str]) -> ProcessingResult[Dict[str, List[str]]]`

Categorizes mutations by type.

**Parameters:**
- `mutations` (List[str]): List of mutation descriptions

**Returns:**
- `ProcessingResult[Dict[str, List[str]]]`: Mutations grouped by category

### Genetic Data Structure

```python
@dataclass
class GeneticExtraction:
    gene: Optional[str]                    # Primary gene involved
    mutations: List[Dict[str, Any]]        # Specific mutations
    inheritance: Optional[str]              # Inheritance pattern
    zygosity: Optional[str]                # Mutation zygosity
    parental_origin: Optional[str]          # Origin of mutation
    genetic_testing: List[str]             # Types of genetic testing
    additional_genes: List[str]             # Other genes mentioned
    confidence_scores: Dict[str, float]    # Confidence for each field
```

## Treatments Agent

**Location**: `src/agents/extraction_agents/treatments_agent.py`

Specialized agent for extracting treatment information, medications, dosages, and therapeutic interventions.

### Initialization

```python
from agents.extraction_agents.treatments_agent import TreatmentsAgent

# Basic initialization
agent = TreatmentsAgent()

# With custom configuration
agent = TreatmentsAgent(
    llm_client=llm_client,
    confidence_threshold=0.8,
    enable_dosage_extraction=True
)
```

### Methods

#### `extract_treatments(text: str) -> ProcessingResult[Dict[str, Any]]`

Extracts comprehensive treatment information from text.

**Parameters:**
- `text` (str): Input text to analyze

**Returns:**
- `ProcessingResult[Dict[str, Any]]`: Extracted treatment data

**Example:**
```python
result = await agent.extract_treatments(
    "Patient was treated with coenzyme Q10 100mg twice daily and thiamine 100mg daily."
)

if result.success:
    treatments = result.data
    print(f"Medications: {treatments['medications']}")
    print(f"Dosages: {treatments['dosages']}")
    print(f"Frequency: {treatments['frequency']}")
```

#### `extract_medications(text: str) -> ProcessingResult[List[Dict[str, Any]]]`

Extracts medication information with details.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[List[Dict[str, Any]]]`: List of medications with details

#### `extract_dosages(text: str) -> ProcessingResult[List[Dict[str, Any]]]`

Extracts dosage information with units and frequency.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[List[Dict[str, Any]]]`: List of dosages with metadata

**Example:**
```python
result = await agent.extract_dosages(
    "Administered 100mg coenzyme Q10 BID and 50mg thiamine QD"
)

if result.success:
    dosages = result.data
    for dosage in dosages:
        print(f"Medication: {dosage['medication']}")
        print(f"Amount: {dosage['amount']} {dosage['unit']}")
        print(f"Frequency: {dosage['frequency']}")
        print(f"Route: {dosage['route']}")  # oral, IV, etc.
```

#### `extract_therapeutic_interventions(text: str) -> ProcessingResult[List[str]]`

Extracts non-pharmacological treatments.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[List[str]]`: List of therapeutic interventions

#### `categorize_treatments(treatments: List[str]) -> ProcessingResult[Dict[str, List[str]]]`

Categorizes treatments by type.

**Parameters:**
- `treatments` (List[str]): List of treatment descriptions

**Returns:**
- `ProcessingResult[Dict[str, List[str]]]`: Treatments grouped by category

**Example:**
```python
treatments = ["coenzyme Q10", "physical therapy", "diet modification"]
result = await agent.categorize_treatments(treatments)

if result.success:
    categories = result.data
    print(f"Medications: {categories['medications']}")
    print(f"Therapies: {categories['therapies']}")
    print(f"Lifestyle: {categories['lifestyle']}")
```

#### `extract_treatment_response(text: str) -> ProcessingResult[Dict[str, Any]]`

Extracts information about treatment effectiveness.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[Dict[str, Any]]`: Treatment response data

#### `extract_adverse_events(text: str) -> ProcessingResult[List[str]]`

Extracts adverse events and side effects.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[List[str]]`: List of adverse events

### Treatment Data Structure

```python
@dataclass
class TreatmentExtraction:
    medications: List[Dict[str, Any]]       # Medication details
    dosages: List[Dict[str, Any]]           # Dosage information
    frequency: List[str]                    # Administration frequency
    route: List[str]                        # Administration route
    therapeutic_interventions: List[str]     # Non-pharmacological treatments
    treatment_response: Optional[str]        # Response to treatment
    adverse_events: List[str]               # Side effects and adverse events
    confidence_scores: Dict[str, float]     # Confidence for each field
```

## Demographics Agent

**Location**: `src/agents/extraction_agents/demographics_agent.py`

Specialized agent for extracting demographic information including age, sex, ethnicity, and family history.

### Initialization

```python
from agents.extraction_agents.demographics_agent import DemographicsAgent

# Basic initialization
agent = DemographicsAgent()

# With custom configuration
agent = DemographicsAgent(
    llm_client=llm_client,
    enable_age_calculation=True,
    validate_demographics=True
)
```

### Methods

#### `extract_demographics(text: str) -> ProcessingResult[Dict[str, Any]]`

Extracts comprehensive demographic information from text.

**Parameters:**
- `text` (str): Input text to analyze

**Returns:**
- `ProcessingResult[Dict[str, Any]]`: Extracted demographic data

**Example:**
```python
result = await agent.extract_demographics(
    "A 3-year-old female patient of Middle Eastern descent presented with symptoms."
)

if result.success:
    demographics = result.data
    print(f"Age: {demographics['age']} years")
    print(f"Sex: {demographics['sex']}")
    print(f"Ethnicity: {demographics['ethnicity']}")
```

#### `extract_age_information(text: str) -> ProcessingResult[Dict[str, Any]]`

Extracts age-related information including onset, diagnosis, and current age.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[Dict[str, Any]]`: Age information with different timepoints

#### `extract_family_history(text: str) -> ProcessingResult[Dict[str, Any]]`

Extracts family history and consanguinity information.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `ProcessingResult[Dict[str, Any]]`: Family history data

#### `normalize_ethnicity(ethnicity_text: str) -> ProcessingResult[str]`

Normalizes ethnicity descriptions to standard terms.

**Parameters:**
- `ethnicity_text` (str): Raw ethnicity description

**Returns:**
- `ProcessingResult[str]`: Normalized ethnicity term

#### `calculate_age_at_onset(onset_age: str, current_age: str) -> ProcessingResult[float]`

Calculates age at symptom onset.

**Parameters:**
- `onset_age` (str): Age at onset description
- `current_age` (str): Current age description

**Returns:**
- `ProcessingResult[float]`: Calculated age at onset in years

### Demographics Data Structure

```python
@dataclass
class DemographicsExtraction:
    age: Optional[float]                    # Current age in years
    age_of_onset: Optional[float]           # Age at symptom onset
    age_at_diagnosis: Optional[float]       # Age at diagnosis
    sex: Optional[str]                      # Biological sex
    ethnicity: Optional[str]                # Ethnic background
    consanguinity: Optional[bool]           # Consanguineous parents
    family_history: Dict[str, Any]          # Family medical history
    geographic_origin: Optional[str]        # Geographic origin
    confidence_scores: Dict[str, float]     # Confidence for each field
```

## Agent Orchestration

### Extraction Orchestrator

**Location**: `src/agents/orchestrator/extraction_orchestrator.py`

Coordinates multiple extraction agents for comprehensive data extraction.

### Initialization

```python
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator

# Initialize with all agents
orchestrator = ExtractionOrchestrator(
    llm_client=llm_client,
    use_demographics=True,
    use_genetics=True,
    use_phenotypes=True,
    use_treatments=True
)
```

### Methods

#### `extract_from_file(file_path: str) -> ProcessingResult[List[PatientRecord]]`

Extracts data from a document file using all enabled agents.

#### `extract_batch(file_paths: List[str]) -> ProcessingResult[List[PatientRecord]]`

Processes multiple files in batch.

#### `extract_from_text(text: str) -> ProcessingResult[List[PatientRecord]]`

Extracts data from raw text.

### Enhanced Orchestrator

**Location**: `src/agents/orchestrator/enhanced_orchestrator.py`

Advanced orchestrator with validation and quality control.

```python
from agents.orchestrator.enhanced_orchestrator import EnhancedExtractionOrchestrator

orchestrator = EnhancedExtractionOrchestrator(
    config=config,
    llm_client=llm_client
)
```

## Custom Agent Development

### Creating a Custom Agent

```python
from core.base import BaseAgent, ProcessingResult
from typing import Dict, Any

class CustomExtractionAgent(BaseAgent):
    """Custom extraction agent example."""
    
    def __init__(self, llm_client=None, **kwargs):
        super().__init__(llm_client=llm_client, **kwargs)
        self.agent_type = "custom_extraction"
        self.confidence_threshold = kwargs.get('confidence_threshold', 0.7)
    
    async def extract(self, text: str) -> ProcessingResult[Dict[str, Any]]:
        """Extract custom information from text."""
        try:
            # Custom extraction logic
            extracted_data = await self._perform_extraction(text)
            
            # Validate extraction
            if self.validation_enabled:
                validation_result = self.validate_extraction(extracted_data)
                if not validation_result.success:
                    return validation_result
            
            return ProcessingResult(
                success=True,
                data=extracted_data,
                metadata={"agent": self.agent_type}
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e),
                metadata={"agent": self.agent_type}
            )
    
    async def _perform_extraction(self, text: str) -> Dict[str, Any]:
        """Implement custom extraction logic."""
        # Your custom extraction implementation here
        # This could involve:
        # - Pattern matching
        # - LLM prompting
        # - Rule-based extraction
        # - External API calls
        
        extracted_data = {}
        
        # Example: Extract using LLM
        if self.llm_client:
            prompt = f"Extract the following information from this text: [your custom fields]\n\nText: {text}"
            result = await self.llm_client.generate(prompt)
            
            if result.success:
                # Parse LLM response into structured data
                extracted_data = self._parse_llm_response(result.data)
        
        return extracted_data
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured data."""
        # Implement parsing logic based on your expected output format
        # This could be JSON parsing, regex extraction, etc.
        pass
    
    def validate_extraction(self, data: Dict[str, Any]) -> ProcessingResult[Dict[str, Any]]:
        """Validate extracted data."""
        # Implement validation logic
        # Check required fields, data types, value ranges, etc.
        
        required_fields = ['field1', 'field2']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return ProcessingResult(
                success=False,
                error=f"Missing required fields: {missing_fields}",
                metadata={"agent": self.agent_type}
            )
        
        return ProcessingResult(
            success=True,
            data=data,
            metadata={"agent": self.agent_type}
        )
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Return extraction statistics."""
        return {
            "agent_type": self.agent_type,
            "total_extractions": getattr(self, '_total_extractions', 0),
            "successful_extractions": getattr(self, '_successful_extractions', 0),
            "average_confidence": getattr(self, '_average_confidence', 0.0)
        }

# Usage
agent = CustomExtractionAgent(
    llm_client=llm_client,
    confidence_threshold=0.8,
    validation_enabled=True
)

result = await agent.extract("Sample text to extract from")
```

### Agent Registration

```python
# Register custom agent with orchestrator
class CustomOrchestrator(ExtractionOrchestrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_agent = CustomExtractionAgent(
            llm_client=self.llm_client
        )
    
    async def extract_from_text(self, text: str) -> ProcessingResult[List[PatientRecord]]:
        # Use custom agent alongside standard agents
        custom_result = await self.custom_agent.extract(text)
        
        # Combine with standard extractions
        # ... implementation details
```

## Configuration and Tuning

### Agent-Specific Configuration

```python
# Phenotypes Agent Configuration
phenotypes_config = {
    "confidence_threshold": 0.7,
    "validation_enabled": True,
    "use_optimized_hpo": True,
    "enable_pattern_matching": True,
    "enable_llm_extraction": True
}

# Genetics Agent Configuration
genetics_config = {
    "confidence_threshold": 0.8,
    "enable_gene_normalization": True,
    "enable_mutation_categorization": True,
    "strict_gene_symbols": True
}

# Treatments Agent Configuration
treatments_config = {
    "confidence_threshold": 0.75,
    "enable_dosage_extraction": True,
    "enable_frequency_extraction": True,
    "enable_route_extraction": True
}
```

### Performance Tuning

```python
# Batch processing configuration
batch_config = {
    "batch_size": 10,
    "max_workers": 4,
    "enable_parallel_processing": True,
    "cache_results": True
}

# LLM prompt optimization
prompt_config = {
    "use_few_shot_examples": True,
    "enable_chain_of_thought": True,
    "temperature": 0.0,
    "max_tokens": 1000
}
```

### Validation Rules

```python
# Custom validation rules
validation_rules = {
    "phenotypes": {
        "min_confidence": 0.6,
        "require_hpo_mapping": True,
        "max_phenotypes_per_record": 20
    },
    "genetics": {
        "min_confidence": 0.8,
        "require_gene_normalization": True,
        "validate_mutation_format": True
    },
    "treatments": {
        "min_confidence": 0.7,
        "require_dosage_info": False,
        "validate_medication_names": True
    }
}
```

This comprehensive documentation covers all extraction agent APIs with detailed examples, configuration options, and best practices for development and usage.