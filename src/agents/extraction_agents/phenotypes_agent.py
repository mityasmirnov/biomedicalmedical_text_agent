"""
Enhanced Phenotypes Agent for Biomedical Text Extraction

This agent specializes in extracting phenotypic information from biomedical text,
including clinical phenotypes, symptoms, diagnostic findings, and laboratory values.
It integrates with the HPO manager for phenotype normalization and provides
comprehensive validation and statistics.

Location: src/agents/extraction_agents/phenotypes_agent.py
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid

from core.base import ProcessingResult, PatientRecord
from core.llm_client.openrouter_client import OpenRouterClient
from core.llm_client.huggingface_client import HuggingFaceClient
from ontologies.hpo_manager import HPOManager
from ontologies.hpo_manager_optimized import OptimizedHPOManager


@dataclass
class PhenotypeExtraction:
    """Represents extracted phenotype information."""
    phenotypes: List[str]
    symptoms: List[str]
    diagnostic_findings: List[str]
    lab_values: List[str]
    imaging_findings: List[str]
    confidence_scores: Dict[str, float]
    hpo_mappings: List[Dict[str, Any]]
    extraction_metadata: Dict[str, Any]


class PhenotypesAgent:
    """
    Enhanced phenotypes extraction agent with HPO integration.
    """
    
    def __init__(self, 
                 llm_client=None,
                 hpo_manager=None,
                 use_optimized_hpo: bool = True):
        """
        Initialize phenotypes agent.
        
        Args:
            llm_client: LLM client for text processing
            hpo_manager: HPO manager instance
            use_optimized_hpo: Whether to use optimized HPO manager
        """
        self.llm_client = llm_client
        self.use_optimized_hpo = use_optimized_hpo
        
        # Initialize HPO manager
        if hpo_manager:
            self.hpo_manager = hpo_manager
        else:
            if use_optimized_hpo:
                try:
                    # Try to use optimized HPO manager with official hp.json
                    hpo_path = "data/ontologies/hp.json"
                    self.hpo_manager = OptimizedHPOManager(hpo_path)
                    logging.info("Using optimized HPO manager")
                except Exception as e:
                    logging.warning(f"Failed to load optimized HPO manager: {e}")
                    self.hpo_manager = HPOManager()
                    self.use_optimized_hpo = False
            else:
                self.hpo_manager = HPOManager()
        
        # Pattern-based phenotype recognition
        self.phenotype_patterns = self._init_phenotype_patterns()
        
        # Clinical terminology mappings
        self.clinical_terms = self._init_clinical_terms()
        
        logging.info("Phenotypes agent initialized")
    
    def _init_phenotype_patterns(self) -> Dict[str, List[str]]:
        """Initialize pattern-based phenotype recognition."""
        return {
            'developmental': [
                r'\b(?:developmental|development)\s+(?:delay|regression|disorder|abnormality)\b',
                r'\b(?:delayed|delayed)\s+(?:milestone|development|growth)\b',
                r'\b(?:failure\s+to\s+thrive|FTT)\b',
                r'\b(?:psychomotor\s+)?retardation\b'
            ],
            'neurological': [
                r'\b(?:seizure|epileptic|convulsion)\b',
                r'\b(?:muscular\s+)?hypotonia\b',
                r'\b(?:hypertonia|spasticity|rigidity)\b',
                r'\b(?:ataxia|dysmetria|dysdiadochokinesia)\b',
                r'\b(?:tremor|myoclonus|chorea)\b',
                r'\b(?:dystonia|dyskinesia)\b'
            ],
            'cognitive': [
                r'\b(?:intellectual\s+)?disability\b',
                r'\b(?:learning\s+)?difficulty\b',
                r'\b(?:cognitive\s+)?impairment\b',
                r'\b(?:mental\s+)?retardation\b',
                r'\b(?:autism|autistic)\b'
            ],
            'sensory': [
                r'\b(?:visual|vision)\s+(?:impairment|loss|defect)\b',
                r'\b(?:hearing|auditory)\s+(?:loss|impairment|deafness)\b',
                r'\b(?:blindness|deafness)\b'
            ],
            'cardiac': [
                r'\b(?:cardiac|heart)\s+(?:defect|anomaly|disease)\b',
                r'\b(?:cardiomyopathy|arrhythmia)\b',
                r'\b(?:ventricular|atrial)\s+(?:septal\s+)?defect\b'
            ],
            'respiratory': [
                r'\b(?:respiratory|breathing)\s+(?:distress|failure|difficulty)\b',
                r'\b(?:apnea|apneic)\b',
                r'\b(?:tachypnea|dyspnea)\b'
            ],
            'gastrointestinal': [
                r'\b(?:feeding|swallowing)\s+(?:difficulty|disorder)\b',
                r'\b(?:gastroesophageal\s+)?reflux\b',
                r'\b(?:vomiting|nausea|diarrhea)\b',
                r'\b(?:constipation|obstruction)\b'
            ],
            'musculoskeletal': [
                r'\b(?:joint\s+)?contracture\b',
                r'\b(?:scoliosis|kyphosis|lordosis)\b',
                r'\b(?:clubfoot|talipes)\b',
                r'\b(?:hip\s+)?dysplasia\b'
            ]
        }
    
    def _init_clinical_terms(self) -> Dict[str, List[str]]:
        """Initialize clinical terminology mappings."""
        return {
            'developmental_delay': ['developmental delay', 'delayed development', 'delayed milestones'],
            'seizures': ['seizures', 'epilepsy', 'epileptic seizures', 'convulsions'],
            'hypotonia': ['hypotonia', 'muscular hypotonia', 'low muscle tone', 'floppy infant'],
            'failure_to_thrive': ['failure to thrive', 'FTT', 'poor growth', 'growth failure'],
            'intellectual_disability': ['intellectual disability', 'mental retardation', 'cognitive impairment'],
            'autism': ['autism', 'autistic disorder', 'ASD', 'autism spectrum disorder'],
            'visual_impairment': ['visual impairment', 'vision loss', 'blindness', 'visual defect'],
            'hearing_loss': ['hearing loss', 'deafness', 'auditory impairment'],
            'cardiac_defect': ['cardiac defect', 'heart defect', 'congenital heart disease'],
            'respiratory_distress': ['respiratory distress', 'breathing difficulty', 'respiratory failure']
        }
    
    async def extract_phenotypes(self, 
                               patient_text: str,
                               patient_id: Optional[str] = None) -> ProcessingResult[PhenotypeExtraction]:
        """
        Extract phenotypic information from patient text.
        
        Args:
            patient_text: Text describing the patient's phenotype
            patient_id: Optional patient identifier
            
        Returns:
            ProcessingResult containing PhenotypeExtraction
        """
        try:
            # Pattern-based extraction first
            pattern_results = self._extract_by_patterns(patient_text)
            
            # LLM-based extraction
            llm_results = await self._extract_by_llm(patient_text)
            
            # Combine and validate results
            combined_results = self._combine_extraction_results(pattern_results, llm_results)
            
            # HPO normalization
            hpo_mappings = self._normalize_phenotypes(combined_results['phenotypes'])
            
            # Create extraction result
            extraction = PhenotypeExtraction(
                phenotypes=combined_results['phenotypes'],
                symptoms=combined_results['symptoms'],
                diagnostic_findings=combined_results['diagnostic_findings'],
                lab_values=combined_results['lab_values'],
                imaging_findings=combined_results['imaging_findings'],
                confidence_scores=combined_results['confidence_scores'],
                hpo_mappings=hpo_mappings,
                extraction_metadata={
                    'extraction_method': 'pattern_llm_combined',
                    'pattern_matches': len(pattern_results['phenotypes']),
                    'llm_extractions': len(llm_results['phenotypes']),
                    'hpo_mappings_count': len(hpo_mappings),
                    'extraction_timestamp': datetime.now().isoformat()
                }
            )
            
            return ProcessingResult(
                success=True,
                data=extraction,
                metadata={
                    'agent_type': 'phenotypes',
                    'patient_id': patient_id,
                    'extraction_method': 'enhanced_phenotypes_agent'
                }
            )
            
        except Exception as e:
            logging.error(f"Phenotype extraction failed: {e}")
            return ProcessingResult(
                success=False,
                error=f"Phenotype extraction failed: {str(e)}",
                metadata={'agent_type': 'phenotypes'}
            )
    
    def _extract_by_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract phenotypes using pattern matching."""
        results = {
            'phenotypes': [],
            'symptoms': [],
            'diagnostic_findings': [],
            'lab_values': [],
            'imaging_findings': []
        }
        
        text_lower = text.lower()
        
        # Extract phenotypes by category
        for category, patterns in self.phenotype_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    phenotype = match.group(0)
                    if phenotype not in results['phenotypes']:
                        results['phenotypes'].append(phenotype)
        
        # Extract lab values (numbers with units)
        lab_patterns = [
            r'\b\d+(?:\.\d+)?\s*(?:mg/dL|mmol/L|g/dL|mEq/L|U/L|ng/mL|pg/mL)\b',
            r'\b(?:glucose|glu)\s*[:=]\s*\d+(?:\.\d+)?\b',
            r'\b(?:creatinine|creat)\s*[:=]\s*\d+(?:\.\d+)?\b',
            r'\b(?:hemoglobin|hgb|hb)\s*[:=]\s*\d+(?:\.\d+)?\b'
        ]
        
        for pattern in lab_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                lab_value = match.group(0)
                if lab_value not in results['lab_values']:
                    results['lab_values'].append(lab_value)
        
        # Extract imaging findings
        imaging_patterns = [
            r'\b(?:MRI|CT|X-ray|ultrasound|echocardiogram)\s+(?:shows|reveals|demonstrates)\b',
            r'\b(?:brain|cardiac|abdominal)\s+(?:MRI|CT|ultrasound)\b',
            r'\b(?:enlarged|atrophic|dysplastic)\s+(?:ventricles|brain|heart|liver)\b'
        ]
        
        for pattern in imaging_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                imaging_finding = match.group(0)
                if imaging_finding not in results['imaging_findings']:
                    results['imaging_findings'].append(imaging_finding)
        
        return results
    
    async def _extract_by_llm(self, text: str) -> Dict[str, List[str]]:
        """Extract phenotypes using LLM."""
        if not self.llm_client:
            return {
                'phenotypes': [],
                'symptoms': [],
                'diagnostic_findings': [],
                'lab_values': [],
                'imaging_findings': []
            }
        
        try:
            # Create prompt for phenotype extraction
            system_prompt = """You are a clinical phenotype extraction specialist. Extract phenotypic information from the given patient text, focusing on clinical features, symptoms, and findings."""
            
            user_prompt = f"""Extract phenotypic information from this patient case:

{text}

Return a JSON object with these fields:
- phenotypes: list of clinical phenotypes/features
- symptoms: list of symptoms reported
- diagnostic_findings: diagnostic test results or findings
- lab_values: laboratory test results if mentioned
- imaging_findings: imaging study results if mentioned

Focus on medical terminology and clinical observations. Only include information that is explicitly stated in the text."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await self.llm_client.generate(messages, max_tokens=1000)
            
            if response and response.content:
                try:
                    # Try to parse JSON response
                    content = response.content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    
                    llm_results = json.loads(content)
                    
                    # Ensure all fields are lists
                    for field in ['phenotypes', 'symptoms', 'diagnostic_findings', 'lab_values', 'imaging_findings']:
                        if field not in llm_results:
                            llm_results[field] = []
                        elif not isinstance(llm_results[field], list):
                            llm_results[field] = [llm_results[field]] if llm_results[field] else []
                    
                    return llm_results
                    
                except json.JSONDecodeError as e:
                    logging.warning(f"Failed to parse LLM response as JSON: {e}")
                    # Fallback: extract text patterns
                    return self._extract_fallback_from_llm(response.content)
            
        except Exception as e:
            logging.error(f"LLM extraction failed: {e}")
        
        return {
            'phenotypes': [],
            'symptoms': [],
            'diagnostic_findings': [],
            'lab_values': [],
            'imaging_findings': []
        }
    
    def _extract_fallback_from_llm(self, llm_text: str) -> Dict[str, List[str]]:
        """Fallback extraction from LLM text when JSON parsing fails."""
        results = {
            'phenotypes': [],
            'symptoms': [],
            'diagnostic_findings': [],
            'lab_values': [],
            'imaging_findings': []
        }
        
        # Simple pattern matching on LLM output
        lines = llm_text.split('\n')
        current_field = None
        
        for line in lines:
            line = line.strip().lower()
            if not line:
                continue
            
            if 'phenotype' in line:
                current_field = 'phenotypes'
            elif 'symptom' in line:
                current_field = 'symptoms'
            elif 'diagnostic' in line or 'finding' in line:
                current_field = 'diagnostic_findings'
            elif 'lab' in line or 'laboratory' in line:
                current_field = 'lab_values'
            elif 'imaging' in line or 'mri' in line or 'ct' in line:
                current_field = 'imaging_findings'
            elif current_field and line.startswith('-') or line.startswith('•'):
                # Extract item
                item = line[1:].strip()
                if item and item not in results[current_field]:
                    results[current_field].append(item)
        
        return results
    
    def _combine_extraction_results(self, 
                                  pattern_results: Dict[str, List[str]], 
                                  llm_results: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Combine pattern-based and LLM-based extraction results."""
        combined = {
            'phenotypes': [],
            'symptoms': [],
            'diagnostic_findings': [],
            'lab_values': [],
            'imaging_findings': [],
            'confidence_scores': {}
        }
        
        # Combine all fields
        for field in ['phenotypes', 'symptoms', 'diagnostic_findings', 'lab_values', 'imaging_findings']:
            combined[field] = list(set(pattern_results[field] + llm_results[field]))
            
            # Calculate confidence scores
            pattern_count = len(pattern_results[field])
            llm_count = len(llm_results[field])
            total_count = len(combined[field])
            
            if total_count > 0:
                # Higher confidence for items found by both methods
                pattern_items = set(pattern_results[field])
                llm_items = set(llm_results[field])
                overlap = len(pattern_items & llm_items)
                
                combined['confidence_scores'][field] = {
                    'pattern_matches': pattern_count,
                    'llm_extractions': llm_count,
                    'overlap': overlap,
                    'confidence': min(1.0, (overlap + 0.5 * (total_count - overlap)) / total_count)
                }
            else:
                combined['confidence_scores'][field] = {
                    'pattern_matches': 0,
                    'llm_extractions': 0,
                    'overlap': 0,
                    'confidence': 0.0
                }
        
        return combined
    
    def _normalize_phenotypes(self, phenotypes: List[str]) -> List[Dict[str, Any]]:
        """Normalize phenotypes using HPO manager."""
        if not phenotypes:
            return []
        
        mappings = []
        
        for phenotype in phenotypes:
            try:
                if self.use_optimized_hpo and hasattr(self.hpo_manager, 'normalize_phenotype'):
                    # Use optimized HPO manager
                    match = self.hpo_manager.normalize_phenotype(phenotype)
                    if match:
                        mappings.append({
                            'original_text': phenotype,
                            'hpo_id': match.hpo_term.hpo_id,
                            'hpo_name': match.hpo_term.name,
                            'confidence': match.confidence,
                            'match_type': match.match_type,
                            'normalized': True
                        })
                    else:
                        mappings.append({
                            'original_text': phenotype,
                            'hpo_id': None,
                            'hpo_name': None,
                            'confidence': 0.0,
                            'match_type': 'no_match',
                            'normalized': False
                        })
                else:
                    # Use standard HPO manager
                    if hasattr(self.hpo_manager, 'search_terms'):
                        matches = self.hpo_manager.search_terms(phenotype, max_results=1)
                        if matches:
                            match = matches[0]
                            mappings.append({
                                'original_text': phenotype,
                                'hpo_id': match.hpo_term.hpo_id,
                                'hpo_name': match.hpo_term.name,
                                'confidence': match.confidence,
                                'match_type': match.match_type,
                                'normalized': True
                            })
                        else:
                            mappings.append({
                                'original_text': phenotype,
                                'hpo_id': None,
                                'hpo_name': None,
                                'confidence': 0.0,
                                'match_type': 'no_match',
                                'normalized': False
                            })
                    else:
                        # Fallback: no normalization
                        mappings.append({
                            'original_text': phenotype,
                            'hpo_id': None,
                            'hpo_name': None,
                            'confidence': 0.0,
                            'match_type': 'not_supported',
                            'normalized': False
                        })
                        
            except Exception as e:
                logging.warning(f"Failed to normalize phenotype '{phenotype}': {e}")
                mappings.append({
                    'original_text': phenotype,
                    'hpo_id': None,
                    'hpo_name': None,
                    'confidence': 0.0,
                    'match_type': 'error',
                    'normalized': False,
                    'error': str(e)
                })
        
        return mappings
    
    def get_extraction_statistics(self, extraction: PhenotypeExtraction) -> Dict[str, Any]:
        """Generate statistics about phenotype extraction."""
        total_phenotypes = len(extraction.phenotypes)
        total_symptoms = len(extraction.symptoms)
        total_findings = len(extraction.diagnostic_findings)
        total_lab_values = len(extraction.lab_values)
        total_imaging = len(extraction.imaging_findings)
        
        # HPO normalization statistics
        normalized_count = sum(1 for m in extraction.hpo_mappings if m['normalized'])
        normalization_rate = normalized_count / len(extraction.hpo_mappings) if extraction.hpo_mappings else 0
        
        # Confidence statistics
        avg_confidence = sum(
            extraction.confidence_scores.get(field, {}).get('confidence', 0.0)
            for field in ['phenotypes', 'symptoms', 'diagnostic_findings', 'lab_values', 'imaging_findings']
        ) / 5
        
        return {
            'total_extractions': total_phenotypes + total_symptoms + total_findings + total_lab_values + total_imaging,
            'phenotypes_count': total_phenotypes,
            'symptoms_count': total_symptoms,
            'diagnostic_findings_count': total_findings,
            'lab_values_count': total_lab_values,
            'imaging_findings_count': total_imaging,
            'hpo_normalization_rate': normalization_rate,
            'normalized_phenotypes': normalized_count,
            'average_confidence': avg_confidence,
            'extraction_method': 'enhanced_phenotypes_agent',
            'hpo_manager_type': 'optimized' if self.use_optimized_hpo else 'standard'
        }
    
    def validate_extraction(self, extraction: PhenotypeExtraction) -> Dict[str, Any]:
        """Validate phenotype extraction results."""
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        # Check for empty extractions
        if not extraction.phenotypes and not extraction.symptoms:
            validation_results['warnings'].append("No phenotypes or symptoms extracted")
            validation_results['suggestions'].append("Review text for clinical features")
        
        # Check HPO normalization rate
        if extraction.hpo_mappings:
            normalization_rate = sum(1 for m in extraction.hpo_mappings if m['normalized']) / len(extraction.hpo_mappings)
            if normalization_rate < 0.5:
                validation_results['warnings'].append(f"Low HPO normalization rate: {normalization_rate:.2%}")
                validation_results['suggestions'].append("Consider improving phenotype terminology")
        
        # Check confidence scores
        low_confidence_fields = []
        for field, scores in extraction.confidence_scores.items():
            if scores.get('confidence', 0.0) < 0.3:
                low_confidence_fields.append(field)
        
        if low_confidence_fields:
            validation_results['warnings'].append(f"Low confidence in fields: {', '.join(low_confidence_fields)}")
            validation_results['suggestions'].append("Review extraction patterns and LLM prompts")
        
        # Check for potential duplicates
        all_texts = extraction.phenotypes + extraction.symptoms + extraction.diagnostic_findings
        duplicates = [text for text in set(all_texts) if all_texts.count(text) > 1]
        if duplicates:
            validation_results['warnings'].append(f"Potential duplicates found: {', '.join(duplicates[:3])}")
            validation_results['suggestions'].append("Implement deduplication logic")
        
        # Overall validation
        if validation_results['warnings']:
            validation_results['is_valid'] = False
        
        return validation_results
