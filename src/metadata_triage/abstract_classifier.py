"""
Abstract Classifier using LLM

This module provides LLM-based classification of biomedical abstracts
for case reports, clinical relevance, and study type identification.
No fine-tuned BERT models are used as per requirements.
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from pathlib import Path


class StudyType(Enum):
    """Enumeration of study types."""
    CASE_REPORT = "case_report"
    CASE_SERIES = "case_series"
    CLINICAL_TRIAL = "clinical_trial"
    COHORT_STUDY = "cohort_study"
    CROSS_SECTIONAL = "cross_sectional"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    REVIEW = "review"
    BASIC_RESEARCH = "basic_research"
    OTHER = "other"


class ClinicalRelevance(Enum):
    """Enumeration of clinical relevance levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class ClassificationResult:
    """Result of abstract classification."""
    study_type: StudyType
    is_case_report: bool
    clinical_relevance: ClinicalRelevance
    patient_count: Optional[int]
    confidence_score: float
    reasoning: str
    extracted_features: Dict[str, Any]


class AbstractClassifier:
    """
    LLM-based classifier for biomedical abstracts.
    """
    
    def __init__(self, llm_client):
        """
        Initialize the abstract classifier.
        
        Args:
            llm_client: LLM client for text generation
        """
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
        
        # Pattern-based features for enhanced classification
        self.case_report_patterns = [
            r'\bcase\s+report\b',
            r'\bcase\s+study\b',
            r'\bwe\s+report\b',
            r'\bwe\s+present\b',
            r'\bwe\s+describe\b',
            r'\ba\s+\d+\s*[-\s]*year[-\s]*old\b',
            r'\bpatient\s+presented\b',
            r'\bpatient\s+was\b'
        ]
        
        self.patient_count_patterns = [
            r'\b(\d+)\s+patients?\b',
            r'\b(\d+)\s+cases?\b',
            r'\b(\d+)\s+subjects?\b',
            r'\b(\d+)\s+individuals?\b',
            r'\bcohort\s+of\s+(\d+)\b',
            r'\bseries\s+of\s+(\d+)\b'
        ]
        
        self.clinical_keywords = {
            'high': [
                'treatment', 'therapy', 'diagnosis', 'clinical', 'patient',
                'disease', 'syndrome', 'mutation', 'genetic', 'phenotype',
                'symptoms', 'prognosis', 'outcome', 'management'
            ],
            'medium': [
                'biomarker', 'pathway', 'mechanism', 'molecular', 'cellular',
                'protein', 'gene expression', 'analysis', 'study'
            ],
            'low': [
                'in vitro', 'cell culture', 'animal model', 'mouse', 'rat',
                'theoretical', 'computational', 'simulation'
            ]
        }
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for abstract classification."""
        return """You are a specialized biomedical literature classifier. Your task is to analyze abstracts and classify them according to study type, clinical relevance, and extract key features.

Classification Categories:

Study Types:
- case_report: Individual patient case descriptions
- case_series: Multiple related patient cases
- clinical_trial: Interventional studies with controls
- cohort_study: Observational studies following groups over time
- cross_sectional: Studies at a single time point
- systematic_review: Comprehensive literature reviews
- meta_analysis: Statistical synthesis of multiple studies
- review: Narrative reviews or commentaries
- basic_research: Laboratory or preclinical studies
- other: Studies that don't fit other categories

Clinical Relevance:
- high: Direct clinical application, patient care, diagnosis, treatment
- medium: Translational research, biomarkers, disease mechanisms
- low: Basic research, animal models, in vitro studies
- none: Non-medical content

Guidelines:
- Focus on the study design and methodology described
- Consider the patient population and clinical context
- Estimate patient/case numbers when mentioned
- Provide confidence scores based on clarity of evidence
- Give detailed reasoning for classifications"""
    
    def get_user_prompt_template(self) -> str:
        """Get the user prompt template for classification."""
        return """Classify this biomedical abstract:

Title: {title}

Abstract: {abstract}

Provide a JSON response with the following structure:
{{
  "study_type": "case_report|case_series|clinical_trial|cohort_study|cross_sectional|systematic_review|meta_analysis|review|basic_research|other",
  "is_case_report": true/false,
  "clinical_relevance": "high|medium|low|none",
  "patient_count": number or null,
  "confidence_score": 0.0-1.0,
  "reasoning": "Detailed explanation of classification decisions",
  "extracted_features": {{
    "mentions_patients": true/false,
    "describes_treatment": true/false,
    "reports_outcomes": true/false,
    "includes_genetics": true/false,
    "has_statistical_analysis": true/false,
    "study_design_keywords": ["keyword1", "keyword2"],
    "medical_specialties": ["specialty1", "specialty2"]
  }}
}}

Focus on:
1. Study design indicators in the methodology
2. Patient population descriptions
3. Clinical vs. research context
4. Outcome measures and endpoints
5. Statistical analysis methods"""
    
    def extract_pattern_features(self, title: str, abstract: str) -> Dict[str, Any]:
        """Extract features using pattern matching."""
        text = f"{title} {abstract}".lower()
        
        features = {
            'case_report_indicators': 0,
            'patient_count_estimates': [],
            'clinical_relevance_score': 0,
            'study_design_keywords': [],
            'medical_specialties': []
        }
        
        # Count case report indicators
        for pattern in self.case_report_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            features['case_report_indicators'] += len(matches)
        
        # Extract patient counts
        for pattern in self.patient_count_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    count = int(match)
                    if 1 <= count <= 10000:  # Reasonable range
                        features['patient_count_estimates'].append(count)
                except ValueError:
                    continue
        
        # Calculate clinical relevance score
        total_keywords = 0
        relevance_score = 0
        
        for level, keywords in self.clinical_keywords.items():
            level_count = sum(1 for keyword in keywords if keyword in text)
            total_keywords += level_count
            
            if level == 'high':
                relevance_score += level_count * 3
            elif level == 'medium':
                relevance_score += level_count * 2
            elif level == 'low':
                relevance_score += level_count * 1
        
        features['clinical_relevance_score'] = relevance_score / max(total_keywords, 1)
        
        # Extract study design keywords
        design_keywords = [
            'randomized', 'controlled', 'trial', 'cohort', 'case-control',
            'cross-sectional', 'longitudinal', 'prospective', 'retrospective',
            'systematic review', 'meta-analysis', 'case report', 'case series'
        ]
        
        for keyword in design_keywords:
            if keyword in text:
                features['study_design_keywords'].append(keyword)
        
        # Extract medical specialties (basic list)
        specialties = [
            'cardiology', 'neurology', 'oncology', 'pediatrics', 'psychiatry',
            'dermatology', 'ophthalmology', 'orthopedics', 'radiology',
            'pathology', 'genetics', 'immunology', 'endocrinology'
        ]
        
        for specialty in specialties:
            if specialty in text:
                features['medical_specialties'].append(specialty)
        
        return features
    
    async def classify_abstract(self, title: str, abstract: str, pmid: str) -> ClassificationResult:
        """
        Classify an abstract using LLM and pattern matching.
        
        Args:
            title: Article title
            abstract: Article abstract
            pmid: PubMed ID
            
        Returns:
            ClassificationResult object
        """
        try:
            # Extract pattern-based features
            pattern_features = self.extract_pattern_features(title, abstract)
            
            # Prepare LLM prompt
            user_prompt = self.get_user_prompt_template().format(
                title=title,
                abstract=abstract
            )
            
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": user_prompt}
            ]
            
            # Get LLM response
            response = await self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=self.get_system_prompt(),
                temperature=0.1,
                max_tokens=800
            )
            
            # Parse JSON response
            try:
                result_data = json.loads(response.data)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', response.data, re.DOTALL)
                if json_match:
                    result_data = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON response")
            
            # Validate and create result
            study_type = StudyType(result_data.get('study_type', 'other'))
            clinical_relevance = ClinicalRelevance(result_data.get('clinical_relevance', 'low'))
            
            # Enhance with pattern-based features
            extracted_features = result_data.get('extracted_features', {})
            extracted_features.update(pattern_features)
            
            # Adjust patient count based on pattern extraction
            llm_patient_count = result_data.get('patient_count')
            pattern_patient_counts = pattern_features.get('patient_count_estimates', [])
            
            if pattern_patient_counts and not llm_patient_count:
                # Use the most common pattern-extracted count
                patient_count = max(set(pattern_patient_counts), key=pattern_patient_counts.count)
            else:
                patient_count = llm_patient_count
            
            # Adjust confidence based on pattern consistency
            base_confidence = result_data.get('confidence_score', 0.5)
            
            # Boost confidence for case reports if patterns align
            if (study_type == StudyType.CASE_REPORT and 
                pattern_features['case_report_indicators'] > 0):
                base_confidence = min(1.0, base_confidence + 0.2)
            
            result = ClassificationResult(
                study_type=study_type,
                is_case_report=result_data.get('is_case_report', False),
                clinical_relevance=clinical_relevance,
                patient_count=patient_count,
                confidence_score=base_confidence,
                reasoning=result_data.get('reasoning', ''),
                extracted_features=extracted_features
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Classification failed for PMID {pmid}: {e}")
            
            # Return default classification
            return ClassificationResult(
                study_type=StudyType.OTHER,
                is_case_report=False,
                clinical_relevance=ClinicalRelevance.LOW,
                patient_count=None,
                confidence_score=0.0,
                reasoning=f"Classification failed: {str(e)}",
                extracted_features={}
            )
    
    async def classify_batch(self, 
                      articles: List[Dict[str, Any]],
                      batch_size: int = 10,
                      save_intermediate: bool = True,
                      output_dir: str = "data/classification") -> List[ClassificationResult]:
        """
        Classify a batch of abstracts.
        
        Args:
            articles: List of article dictionaries with 'title', 'abstract', 'pmid'
            batch_size: Number of articles to process before saving intermediate results
            save_intermediate: Whether to save intermediate results
            output_dir: Directory for intermediate files
            
        Returns:
            List of ClassificationResult objects
        """
        results = []
        
        if save_intermediate:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for i, article in enumerate(articles):
            try:
                title = article.get('title', '')
                abstract = article.get('abstract', '')
                pmid = article.get('pmid', f'unknown_{i}')
                
                if not abstract:
                    self.logger.warning(f"No abstract for article {pmid}, skipping")
                    continue
                
                # Classify abstract
                result = await self.classify_abstract(title, abstract, pmid)
                results.append(result)
                
                # Save intermediate results
                if save_intermediate and (i + 1) % batch_size == 0:
                    self._save_intermediate_results(results, output_dir, f"batch_{i//batch_size + 1}")
                    self.logger.info(f"Saved intermediate results for batch {i//batch_size + 1}")
                    
            except Exception as e:
                self.logger.error(f"Failed to classify article {i}: {e}")
                # Add default result
                results.append(ClassificationResult(
                    study_type=StudyType.OTHER,
                    is_case_report=False,
                    clinical_relevance=ClinicalRelevance.LOW,
                    patient_count=None,
                    confidence_score=0.0,
                    reasoning=f"Classification failed: {str(e)}",
                    extracted_features={}
                ))
        
        # Save final results
        if save_intermediate:
            self._save_intermediate_results(results, output_dir, "final")
        
        return results
    
    def _save_intermediate_results(self, 
                                 results: List[ClassificationResult],
                                 output_dir: str,
                                 count: int,
                                 final: bool = False) -> None:
        """Save intermediate classification results."""
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        
        if final:
            filename = f"classification_final_{timestamp}.json"
        else:
            filename = f"classification_batch_{count}_{timestamp}.json"
        
        output_path = Path(output_dir) / filename
        
        # Convert results to serializable format
        serializable_results = []
        for result in results:
            result_dict = {
                'study_type': result.study_type.value,
                'is_case_report': result.is_case_report,
                'clinical_relevance': result.clinical_relevance.value,
                'patient_count': result.patient_count,
                'confidence_score': result.confidence_score,
                'reasoning': result.reasoning,
                'extracted_features': result.extracted_features
            }
            serializable_results.append(result_dict)
        
        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        self.logger.info(f"Saved {len(results)} classification results to {output_path}")
    
    def create_classification_report(self, results: List[ClassificationResult]) -> Dict[str, Any]:
        """Create a summary report of classification results."""
        if not results:
            return {}
        
        total_articles = len(results)
        
        # Study type distribution
        study_type_counts = {}
        for result in results:
            study_type = result.study_type.value
            study_type_counts[study_type] = study_type_counts.get(study_type, 0) + 1
        
        # Clinical relevance distribution
        relevance_counts = {}
        for result in results:
            relevance = result.clinical_relevance.value
            relevance_counts[relevance] = relevance_counts.get(relevance, 0) + 1
        
        # Case report statistics
        case_reports = [r for r in results if r.is_case_report]
        case_report_count = len(case_reports)
        
        # Patient count statistics
        patient_counts = [r.patient_count for r in results if r.patient_count is not None]
        avg_patient_count = sum(patient_counts) / len(patient_counts) if patient_counts else 0
        
        # Confidence statistics
        confidences = [r.confidence_score for r in results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # High-confidence case reports
        high_conf_case_reports = [
            r for r in case_reports 
            if r.confidence_score >= 0.8
        ]
        
        report = {
            'total_articles': total_articles,
            'study_type_distribution': study_type_counts,
            'clinical_relevance_distribution': relevance_counts,
            'case_report_statistics': {
                'total_case_reports': case_report_count,
                'case_report_rate': case_report_count / total_articles if total_articles > 0 else 0,
                'high_confidence_case_reports': len(high_conf_case_reports),
                'high_confidence_rate': len(high_conf_case_reports) / case_report_count if case_report_count > 0 else 0
            },
            'patient_count_statistics': {
                'articles_with_patient_counts': len(patient_counts),
                'average_patient_count': avg_patient_count,
                'patient_count_range': [min(patient_counts), max(patient_counts)] if patient_counts else [0, 0]
            },
            'confidence_statistics': {
                'average_confidence': avg_confidence,
                'high_confidence_articles': len([c for c in confidences if c >= 0.8]),
                'low_confidence_articles': len([c for c in confidences if c < 0.5])
            }
        }
        
        return report
    
    def save_results_to_csv(self, 
                           results: List[ClassificationResult],
                           articles: List[Dict[str, Any]],
                           output_path: str) -> None:
        """
        Save classification results to CSV format.
        
        Args:
            results: List of ClassificationResult objects
            articles: Original article data
            output_path: Output CSV file path
        """
        # Combine results with original article data
        combined_data = []
        
        for i, (result, article) in enumerate(zip(results, articles)):
            row = {
                'PMID': article.get('pmid', ''),
                'Title': article.get('title', ''),
                'Abstract': article.get('abstract', ''),
                'StudyType': result.study_type.value,
                'IsCaseReport': result.is_case_report,
                'ClinicalRelevance': result.clinical_relevance.value,
                'PatientCount': result.patient_count,
                'ConfidenceScore': result.confidence_score,
                'Reasoning': result.reasoning,
                'CaseReportIndicators': result.extracted_features.get('case_report_indicators', 0),
                'ClinicalRelevanceScore': result.extracted_features.get('clinical_relevance_score', 0),
                'StudyDesignKeywords': '; '.join(result.extracted_features.get('study_design_keywords', [])),
                'MedicalSpecialties': '; '.join(result.extracted_features.get('medical_specialties', []))
            }
            combined_data.append(row)
        
        # Create DataFrame and save
        df = pd.DataFrame(combined_data)
        df.to_csv(output_path, index=False)
        
        self.logger.info(f"Saved classification results to {output_path}")


# Utility functions

def classify_leigh_syndrome_abstracts(llm_client, 
                                    input_csv: str,
                                    output_csv: str = "data/leigh_syndrome_classified.csv") -> List[ClassificationResult]:
    """
    Classify Leigh syndrome abstracts from CSV file.
    
    Args:
        llm_client: LLM client for classification
        input_csv: Input CSV file with abstracts
        output_csv: Output CSV file for results
        
    Returns:
        List of ClassificationResult objects
    """
    # Load articles from CSV
    df = pd.read_csv(input_csv)
    
    articles = []
    for _, row in df.iterrows():
        articles.append({
            'pmid': str(row.get('PMID', '')),
            'title': str(row.get('Title', '')),
            'abstract': str(row.get('Abstract', ''))
        })
    
    # Initialize classifier
    classifier = AbstractClassifier(llm_client)
    
    # Classify articles
    results = classifier.classify_batch(articles)
    
    # Save results
    classifier.save_results_to_csv(results, articles, output_csv)
    
    # Print report
    report = classifier.create_classification_report(results)
    print(f"Classification Report:")
    print(f"Total articles: {report['total_articles']}")
    print(f"Case reports: {report['case_report_statistics']['total_case_reports']}")
    print(f"Case report rate: {report['case_report_statistics']['case_report_rate']:.2%}")
    print(f"Average confidence: {report['confidence_statistics']['average_confidence']:.2f}")
    
    return results

