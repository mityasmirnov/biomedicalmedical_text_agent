# 📊 Data Directory - Biomedical Text Agent

> **Biological Data Storage & Sample Datasets for Medical Research**

This directory contains all data used by the Biomedical Text Agent, including sample documents, extracted patient records, metadata collections, and biological ontologies.

## 🧬 **Biological Data Organization**

The data structure mirrors the **hierarchical organization of biological information**:

```
📊 Data
├── 🧬 Ontologies (Standardized Biological Terms)
├── 📚 Input Documents (Raw Medical Literature)
├── 🔬 Processed Data (Extracted Patient Information)
├── 📈 Metadata Collections (Research Paper Analysis)
└── 💾 Database Files (Structured Patient Records)
```

## 📁 **Directory Structure & Medical Context**

### **🧬 Ontologies (`ontologies/`)**
**Biological Purpose**: Standardized vocabularies that ensure consistent medical terminology

- **`hpo/`** - Human Phenotype Ontology
  - **Purpose**: Standardized vocabulary for human phenotypes
  - **Medical Use**: Enables phenotype-genotype correlation analysis
  - **Example**: "HP:0001250" = "Seizure" (standardized seizure terminology)
  - **Files**: `.obo`, `.owl`, `.json` formats for different applications

- **`genes/`** - Gene Ontology & Normalization
  - **Purpose**: Standardized gene names and identifiers
  - **Medical Use**: Links genes to diseases and biological processes
  - **Example**: "NDUFS2" = "NADH:ubiquinone oxidoreductase core subunit S2"
  - **Files**: Gene databases, mapping tables, normalization rules

**Biological Analogy**: Like **DNA sequences** that provide the genetic code for consistent terminology

### **📚 Input Documents (`input/`)**
**Biological Purpose**: Raw medical literature that serves as the "food" for the system

- **`PMID32679198.pdf`** - Sample research paper
  - **Content**: Medical case report or research study
  - **Purpose**: Testing document processing capabilities
  - **Medical Context**: Real-world example of medical literature

**Biological Analogy**: Like **raw nutrients** that need to be processed and broken down

### **🔬 Processed Data (`output/`)**
**Biological Purpose**: Extracted and structured information from medical documents

- **`api_usage_test.csv`** - System usage analytics
- **`enhanced_demo_results.json`** - Demo extraction results
- **`test_report.json`** - System testing results

**Biological Analogy**: Like **metabolites** - processed and usable forms of raw information

### **📈 Metadata Collections (`metadata_triage/`)**
**Biological Purpose**: Organized collections of research papers and their analysis

- **`leigh_syndrome/`** - Leigh Syndrome Research Collection
  - **Purpose**: Focused collection on mitochondrial disorders
  - **Medical Context**: Rare disease research and case analysis
  - **Contents**:
    - `combined_metadata_*.csv` - Aggregated paper metadata
    - `final_results_*.csv` - Processed research results
    - `pipeline_summary_*.json` - Processing pipeline summaries
    - `classification/` - AI-classified research papers
    - `concept_scoring/` - Relevance scoring results
    - `deduplication/` - Duplicate removal results
    - `pubmed/` - PubMed retrieval results

**Biological Analogy**: Like **organ systems** - specialized collections focused on specific medical domains

### **💾 Database Files (`database/`)**
**Biological Purpose**: Structured storage of extracted patient information

- **`biomedical_data.db`** - SQLite database
  - **Purpose**: Store patient records and extracted data
  - **Medical Context**: Electronic health record system
  - **Contents**: Patient demographics, genetics, phenotypes, treatments

**Biological Analogy**: Like **cellular organelles** - specialized structures for data storage and retrieval

### **🔍 RAG System (`rag/`)**
**Biological Purpose**: Semantic search and question-answering capabilities

- **`rag.db`** - Vector database for semantic search
- **`vectors/`** - FAISS index files for similarity search

**Biological Analogy**: Like **neural networks** - enables pattern recognition and knowledge retrieval

### **📊 Schemas (`schemas/`)**
**Biological Purpose**: Data structure definitions that ensure consistency

- **`table_schema.json`** - Database table definitions
- **`table_schema_original.json`** - Original schema for reference

**Biological Analogy**: Like **protein structures** - defines the shape and organization of data

## 🧬 **Biological Data Flow**

### **1. Data Ingestion**
```
Medical Literature → Document Storage → Metadata Extraction → Relevance Scoring
```

**Biological Analogy**: Like **nutrient absorption** - taking in raw materials for processing

### **2. Data Processing**
```
Raw Documents → AI Extraction → Structured Data → Ontology Mapping
```

**Biological Analogy**: Like **cellular metabolism** - converting raw materials to usable forms

### **3. Data Organization**
```
Extracted Data → Categorization → Collection Formation → Knowledge Base
```

**Biological Analogy**: Like **tissue formation** - organizing cells into functional structures

### **4. Data Retrieval**
```
User Queries → Semantic Search → Knowledge Retrieval → Evidence-Based Answers
```

**Biological Analogy**: Like **memory recall** - accessing stored information when needed

## 🔬 **Medical Research Applications**

### **Rare Disease Research**
- **Leigh Syndrome Collection**: Mitochondrial disorders, genetic mutations
- **Case Report Analysis**: Patient presentation patterns, treatment outcomes
- **Literature Synthesis**: Cross-study analysis and meta-analysis

### **Clinical Data Mining**
- **Patient Demographics**: Age, sex, ethnicity, consanguinity patterns
- **Genetic Markers**: Gene variants, inheritance patterns, zygosity
- **Phenotypic Features**: HPO terms, clinical manifestations
- **Treatment Outcomes**: Medication responses, therapeutic strategies

### **Research Applications**
- **Literature Reviews**: Systematic analysis of published research
- **Meta-Analysis**: Cross-study patient data aggregation
- **Drug Discovery**: Treatment pattern identification
- **Biomarker Research**: Phenotype-genotype correlations

## 📊 **Data Quality & Standards**

### **Medical Accuracy**
- **Expert Validation**: Medical professionals review extracted data
- **Ontology Compliance**: All terms mapped to standard vocabularies
- **Source Attribution**: Clear tracking of data sources
- **Quality Metrics**: Confidence scores for extracted information

### **Data Privacy**
- **De-identification**: Patient identifiers removed from research data
- **Access Control**: Secure access to sensitive medical information
- **Audit Trails**: Complete tracking of data access and modifications
- **Compliance**: HIPAA and research ethics compliance

### **Data Consistency**
- **Standardized Formats**: Consistent data structure across all sources
- **Ontology Mapping**: Unified terminology for medical concepts
- **Validation Rules**: Automated checks for data quality
- **Error Handling**: Robust processing of malformed data

## 🚀 **Data Management Workflow**

### **Adding New Data**
1. **Source Identification**: Identify relevant medical literature
2. **Quality Assessment**: Evaluate data quality and relevance
3. **Processing Pipeline**: Run through extraction and analysis
4. **Validation**: Verify extracted information accuracy
5. **Integration**: Add to appropriate collections
6. **Documentation**: Update metadata and documentation

### **Data Maintenance**
- **Regular Updates**: Keep ontologies and databases current
- **Quality Monitoring**: Track data quality metrics
- **Backup Procedures**: Regular data backup and recovery
- **Version Control**: Track changes and maintain data lineage

## 📚 **Sample Data Usage**

### **For Researchers**
```python
# Access Leigh Syndrome collection
from pathlib import Path
data_dir = Path("data/metadata_triage/leigh_syndrome")
metadata_files = list(data_dir.glob("combined_metadata_*.csv"))

# Load and analyze data
import pandas as pd
df = pd.read_csv(metadata_files[-1])  # Latest data
print(f"Total papers: {len(df)}")
print(f"Case reports: {df['IsCaseReport'].sum()}")
```

### **For Developers**
```python
# Access database
from src.database.sqlite_manager import SQLiteManager
db = SQLiteManager()
stats = db.get_statistics()
print(f"Database statistics: {stats.data}")
```

### **For Medical Professionals**
- **Literature Review**: Browse organized research collections
- **Case Analysis**: Find similar patient cases
- **Treatment Patterns**: Identify effective therapeutic strategies
- **Research Gaps**: Discover areas needing further study

## 🎯 **Future Data Enhancements**

### **Biological Data Types**
- **Imaging Data**: MRI, CT scans, pathology images
- **Lab Results**: Blood tests, genetic testing results
- **Temporal Data**: Disease progression over time
- **Population Data**: Epidemiological information

### **Data Integration**
- **External Databases**: NCBI, ClinVar, OMIM integration
- **Real-time Updates**: Live data from medical systems
- **Multi-modal Analysis**: Text, image, and structured data
- **Cross-species Data**: Animal model information

## 🔧 **Technical Data Details**

### **File Formats**
- **CSV**: Tabular data (metadata, results)
- **JSON**: Structured data (pipeline summaries, configurations)
- **SQLite**: Relational database (patient records)
- **FAISS**: Vector database (semantic search)
- **PDF**: Source documents (research papers)

### **Data Processing**
- **Batch Processing**: Efficient handling of large datasets
- **Incremental Updates**: Add new data without reprocessing
- **Data Validation**: Automated quality checks
- **Error Recovery**: Robust handling of processing failures

---

**This data directory represents the foundation of medical knowledge - organized, accessible, and ready to support groundbreaking research in biomedical science.** 🧬🔬💊
