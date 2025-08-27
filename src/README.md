# 🧬 Source Code - Biomedical Text Agent

> **Core System Architecture for Biomedical Literature Processing & Patient Data Extraction**

This directory contains the complete source code for the Biomedical Text Agent, a unified system designed to bridge the gap between published medical literature and clinical data analysis.

## 🏗️ **Architecture Overview**

The system follows a **layered architecture** that mirrors the workflow of medical research:

```
📚 Literature Input → 🔍 Metadata Analysis → 🧠 AI Processing → 💾 Data Storage → 🔬 Analysis & Query
```

## 📁 **Directory Structure & Biological Context**

### **🧠 Core Processing (`core/`)**
**Biological Purpose**: Central nervous system of the system - coordinates all biological data processing

- **`unified_orchestrator.py`** - Master coordinator for all extraction processes
- **`config.py`** - System configuration and environment management
- **`llm_client/`** - AI language model integration for medical text understanding
- **`base.py`** - Foundation classes for all biological data processors
- **`logging_config.py`** - System monitoring and audit trails

**Medical Use Case**: Like a **clinical decision support system** that coordinates multiple diagnostic tools

### **🔬 AI Extraction Agents (`agents/`)**
**Biological Purpose**: Specialized "organs" that extract specific types of medical information

- **`extraction_agents/`** - Specialized AI agents for different data types:
  - **Demographics Agent**: Age, sex, ethnicity, consanguinity patterns
  - **Genetics Agent**: Gene variants, mutations, inheritance patterns
  - **Phenotypes Agent**: Clinical manifestations, HPO terms, symptoms
  - **Treatments Agent**: Medications, therapies, interventions
- **`orchestrator/`** - Coordinates multiple agents for comprehensive extraction

**Medical Use Case**: Similar to **multi-specialty medical teams** working together on complex cases

### **📊 Metadata Triage (`metadata_triage/`)**
**Biological Purpose**: "Immune system" that filters and prioritizes relevant medical literature

- **`metadata_orchestrator.py`** - Orchestrates literature retrieval and classification
- **`abstract_classifier.py`** - AI-powered classification of research relevance
- **`concept_scorer.py`** - Scores papers based on concept density and clinical relevance
- **`deduplicator.py`** - Identifies and removes duplicate patient cases
- **`pubmed_client.py`** - Integration with PubMed for literature retrieval
- **`europepmc_client.py`** - European biomedical database integration

**Medical Use Case**: Like **medical librarians** who curate and prioritize research literature

### **🧬 Ontology Management (`ontologies/`)**
**Biological Purpose**: "Genetic code" that provides standardized terminology for medical concepts

- **`hpo_manager.py`** - Human Phenotype Ontology integration
  - Maps clinical descriptions to standardized HPO terms
  - Enables phenotype-genotype correlation analysis
- **`gene_manager.py`** - Gene ontology and normalization
  - Standardizes gene names and identifiers
  - Links genes to diseases and phenotypes

**Medical Use Case**: Like **medical dictionaries** that ensure consistent terminology across studies

### **📄 Document Processing (`processors/`)**
**Biological Purpose**: "Digestive system" that breaks down complex medical documents

- **`pdf_parser.py`** - Extracts text from PDF medical papers
- **`patient_segmenter.py`** - Identifies and segments individual patient cases

**Medical Use Case**: Like **medical transcriptionists** who convert unstructured documents to structured data

### **💾 Data Storage (`database/`)**
**Biological Purpose**: "Memory system" that stores and retrieves medical knowledge

- **`sqlite_manager.py`** - Structured storage for patient records and metadata
- **`vector_manager.py`** - Semantic search using FAISS for finding similar cases

**Medical Use Case**: Like **electronic health records** with advanced search capabilities

### **🔍 RAG System (`rag/`)**
**Biological Purpose**: "Cognitive system" that answers questions using stored medical knowledge

- **`rag_system.py`** - Retrieval-Augmented Generation for medical Q&A
- **`rag_integration.py`** - Integration with the main system

**Medical Use Case**: Like **medical consultation systems** that provide evidence-based answers

### **🌐 User Interface (`ui/`)**
**Biological Purpose**: "Sensory system" that provides human-computer interaction

- **`frontend/`** - React-based web interface
- **`config.py`** - Frontend configuration

**Medical Use Case**: Like **medical dashboards** that present complex data in understandable formats

## 🧬 **Biological Data Flow**

### **1. Literature Ingestion**
```
PubMed/Europe PMC → Metadata Triage → Relevance Scoring → Document Classification
```

**Biological Analogy**: Like **nutrient absorption** in the digestive system

### **2. Document Processing**
```
PDF/Text → Text Extraction → Patient Segmentation → AI Analysis
```

**Biological Analogy**: Like **cellular metabolism** breaking down complex molecules

### **3. Data Extraction**
```
Raw Text → AI Agents → Structured Data → Ontology Mapping
```

**Biological Analogy**: Like **protein synthesis** converting genetic information to functional molecules

### **4. Knowledge Storage**
```
Extracted Data → Database Storage → Vector Indexing → Semantic Search
```

**Biological Analogy**: Like **memory formation** in neural networks

### **5. Knowledge Retrieval**
```
User Queries → Semantic Search → RAG Generation → Evidence-Based Answers
```

**Biological Analogy**: Like **recall and reasoning** in cognitive processes

## 🔬 **Medical Research Applications**

### **Rare Disease Research**
- **Leigh Syndrome**: Mitochondrial disorders, genetic mutations
- **Genetic Conditions**: Gene-phenotype correlations, inheritance patterns
- **Case Report Analysis**: Patient presentation patterns, treatment outcomes

### **Clinical Data Mining**
- **Patient Demographics**: Age, sex, ethnicity, consanguinity
- **Genetic Markers**: Gene mutations, inheritance patterns, zygosity
- **Phenotypic Features**: HPO terms, clinical manifestations
- **Treatment Outcomes**: Medication responses, therapeutic strategies

### **Research Applications**
- **Literature Reviews**: Systematic analysis of published research
- **Meta-Analysis**: Cross-study patient data aggregation
- **Drug Discovery**: Treatment pattern identification
- **Biomarker Research**: Phenotype-genotype correlations

## 🚀 **Development Workflow**

### **Adding New Features**
1. **Identify Biological Need**: What medical data type needs extraction?
2. **Design Agent**: Create specialized AI agent for the data type
3. **Add Ontology Support**: Ensure standardized terminology
4. **Update Database Schema**: Store new data types
5. **Add API Endpoints**: Expose functionality to users
6. **Test Thoroughly**: Ensure medical accuracy

### **Testing Strategy**
- **Unit Tests**: Individual component functionality
- **Integration Tests**: Component interactions
- **E2E Tests**: Complete medical workflows
- **Medical Validation**: Expert review of extracted data

## 📚 **Key Biological Concepts**

### **HPO (Human Phenotype Ontology)**
- Standardized vocabulary for human phenotypes
- Enables phenotype-genotype correlation analysis
- Critical for rare disease diagnosis and research

### **Gene Ontology**
- Standardized gene names and identifiers
- Links genes to diseases and biological processes
- Essential for genetic variant interpretation

### **Clinical Terminology**
- Standardized medical language
- Ensures consistency across studies
- Enables cross-study data aggregation

## 🔧 **Technical Implementation**

### **AI/ML Components**
- **LangExtract Engine**: Primary extraction engine
- **OpenRouter Integration**: Access to multiple LLM providers
- **Vector Embeddings**: Semantic search capabilities
- **RAG System**: Question answering using extracted data

### **Data Processing**
- **Async Processing**: Non-blocking document processing
- **Batch Operations**: Efficient handling of multiple documents
- **Error Handling**: Robust processing of malformed documents
- **Quality Control**: Validation of extracted data

### **Performance Optimization**
- **Database Indexing**: Fast query performance
- **Caching**: Reduced computation overhead
- **Parallel Processing**: Multi-document processing
- **Memory Management**: Efficient resource utilization

## 🎯 **Future Directions**

### **Biological Enhancements**
- **Multi-modal Data**: Integration with imaging, lab results
- **Temporal Analysis**: Disease progression patterns
- **Population Studies**: Epidemiological analysis
- **Drug Interactions**: Medication combination effects

### **Technical Enhancements**
- **Distributed Processing**: Scalability for large datasets
- **Real-time Updates**: Live data integration
- **Advanced Analytics**: Machine learning for pattern discovery
- **API Ecosystem**: Integration with external medical systems

---

**This system represents the convergence of medical informatics, artificial intelligence, and clinical research - empowering researchers to extract meaningful insights from the vast body of biomedical literature.** 🧬🔬💊
