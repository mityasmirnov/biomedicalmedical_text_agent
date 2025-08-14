"""
Concept Density Scorer for UMLS/HPO Terms

This module provides concept density scoring for biomedical abstracts
using UMLS and HPO concept extraction and density calculation.
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import Counter
import pandas as pd
from pathlib import Path
import requests
import time


@dataclass
class ConceptMatch:
    """Represents a matched concept in text."""
    concept_id: str
    concept_name: str
    matched_text: str
    start_pos: int
    end_pos: int
    confidence: float
    source: str  # 'UMLS', 'HPO', etc.
    semantic_type: Optional[str] = None


@dataclass
class ConceptDensityScore:
    """Result of concept density scoring."""
    total_concepts: int
    unique_concepts: int
    concept_density: float  # concepts per 100 words
    umls_concepts: List[ConceptMatch]
    hpo_concepts: List[ConceptMatch]
    priority_score: float  # 0-1 score for prioritization
    semantic_categories: Dict[str, int]
    reasoning: str


class ConceptDensityScorer:
    """
    Scorer for UMLS/HPO concept density in biomedical text.
    """
    
    def __init__(self, 
                 umls_api_key: Optional[str] = None,
                 hpo_manager=None):
        """
        Initialize the concept density scorer.
        
        Args:
            umls_api_key: UMLS API key for concept recognition
            hpo_manager: HPO manager instance for phenotype concepts
        """
        self.umls_api_key = umls_api_key
        self.hpo_manager = hpo_manager
        self.logger = logging.getLogger(__name__)
        
        # UMLS REST API base URL
        self.umls_base_url = "https://uts-ws.nlm.nih.gov/rest"
        
        # Session for API requests
        self.session = requests.Session()
        
        # Rate limiting for UMLS API
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 10 requests per second
        
        # Semantic type weights for priority scoring
        self.semantic_type_weights = {
            # High priority - clinical concepts
            'Disease or Syndrome': 3.0,
            'Sign or Symptom': 3.0,
            'Congenital Abnormality': 3.0,
            'Neoplastic Process': 3.0,
            'Mental or Behavioral Dysfunction': 2.5,
            'Pathologic Function': 2.5,
            'Therapeutic or Preventive Procedure': 2.5,
            'Pharmacologic Substance': 2.5,
            'Diagnostic Procedure': 2.0,
            'Laboratory Procedure': 2.0,
            'Gene or Genome': 2.0,
            'Amino Acid, Peptide, or Protein': 1.5,
            'Nucleic Acid, Nucleoside, or Nucleotide': 1.5,
            # Medium priority
            'Body Part, Organ, or Organ Component': 1.0,
            'Cell or Molecular Dysfunction': 1.0,
            'Molecular Function': 1.0,
            # Lower priority
            'Temporal Concept': 0.5,
            'Quantitative Concept': 0.5,
            'Qualitative Concept': 0.5
        }
        
        # Pre-compiled patterns for basic concept recognition
        self.basic_patterns = {
            'gene_symbols': re.compile(r'\b[A-Z][A-Z0-9]{2,10}\b'),
            'hpo_ids': re.compile(r'\bHP:\d{7}\b'),
            'omim_ids': re.compile(r'\bOMIM:\d{6}\b'),
            'mesh_terms': re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'),
            'drug_names': re.compile(r'\b\w+(?:mab|nib|zole|pril|sartan|statin)\b', re.IGNORECASE),
            'medical_abbreviations': re.compile(r'\b[A-Z]{2,6}\b')
        }
        
        # Load common medical terms if available
        self.medical_terms = self._load_medical_terms()
    
    def _load_medical_terms(self) -> Set[str]:
        """Load common medical terms for basic recognition."""
        # Basic medical terms - in production, this could be loaded from a file
        terms = {
            'syndrome', 'disease', 'disorder', 'deficiency', 'mutation',
            'phenotype', 'genotype', 'symptom', 'diagnosis', 'treatment',
            'therapy', 'medication', 'protein', 'enzyme', 'gene',
            'chromosome', 'inheritance', 'clinical', 'patient', 'case',
            'manifestation', 'feature', 'abnormality', 'dysfunction'
        }
        return terms
    
    def _rate_limit_umls(self):
        """Apply rate limiting for UMLS API requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def extract_umls_concepts(self, text: str, max_concepts: int = 50) -> List[ConceptMatch]:
        """
        Extract UMLS concepts from text using the UMLS API.
        
        Args:
            text: Input text
            max_concepts: Maximum number of concepts to extract
            
        Returns:
            List of ConceptMatch objects
        """
        if not self.umls_api_key:
            self.logger.warning("UMLS API key not provided, using basic pattern matching")
            return self._extract_basic_medical_concepts(text)
        
        concepts = []
        
        try:
            # Use UMLS MetaMap or similar service
            # For now, implement basic concept extraction
            concepts = self._extract_basic_medical_concepts(text)
            
        except Exception as e:
            self.logger.error(f"UMLS concept extraction failed: {e}")
            # Fallback to basic extraction
            concepts = self._extract_basic_medical_concepts(text)
        
        return concepts[:max_concepts]
    
    def _extract_basic_medical_concepts(self, text: str) -> List[ConceptMatch]:
        """Extract medical concepts using basic pattern matching."""
        concepts = []
        text_lower = text.lower()
        
        # Extract gene symbols
        for match in self.basic_patterns['gene_symbols'].finditer(text):
            gene_symbol = match.group()
            if len(gene_symbol) >= 3:  # Filter very short matches
                concepts.append(ConceptMatch(
                    concept_id=f"GENE:{gene_symbol}",
                    concept_name=gene_symbol,
                    matched_text=gene_symbol,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.7,
                    source="BASIC",
                    semantic_type="Gene or Genome"
                ))
        
        # Extract HPO IDs
        for match in self.basic_patterns['hpo_ids'].finditer(text):
            hpo_id = match.group()
            concepts.append(ConceptMatch(
                concept_id=hpo_id,
                concept_name=hpo_id,
                matched_text=hpo_id,
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.9,
                source="HPO",
                semantic_type="Sign or Symptom"
            ))
        
        # Extract medical terms
        words = re.findall(r'\b\w+\b', text_lower)
        for i, word in enumerate(words):
            if word in self.medical_terms:
                # Find position in original text
                start_pos = text_lower.find(word)
                if start_pos != -1:
                    concepts.append(ConceptMatch(
                        concept_id=f"MEDICAL:{word.upper()}",
                        concept_name=word,
                        matched_text=word,
                        start_pos=start_pos,
                        end_pos=start_pos + len(word),
                        confidence=0.6,
                        source="BASIC",
                        semantic_type="Medical Concept"
                    ))
        
        return concepts
    
    def extract_hpo_concepts(self, text: str, max_concepts: int = 30) -> List[ConceptMatch]:
        """
        Extract HPO concepts from text using the HPO manager.
        
        Args:
            text: Input text
            max_concepts: Maximum number of concepts to extract
            
        Returns:
            List of ConceptMatch objects
        """
        concepts = []
        
        if not self.hpo_manager:
            self.logger.warning("HPO manager not provided, using basic HPO pattern matching")
            return self._extract_basic_hpo_concepts(text)
        
        try:
            # Split text into sentences for better matching
            sentences = re.split(r'[.!?]+', text)
            
            for sentence in sentences:
                if len(sentence.strip()) < 10:
                    continue
                
                # Search for HPO terms in the sentence
                hpo_matches = self.hpo_manager.search_terms(sentence, max_results=5)
                
                for match in hpo_matches:
                    if match.confidence > 0.5:  # Only high-confidence matches
                        # Find position in original text
                        start_pos = text.lower().find(match.matched_text.lower())
                        if start_pos != -1:
                            concepts.append(ConceptMatch(
                                concept_id=match.hpo_term.hpo_id,
                                concept_name=match.hpo_term.name,
                                matched_text=match.matched_text,
                                start_pos=start_pos,
                                end_pos=start_pos + len(match.matched_text),
                                confidence=match.confidence,
                                source="HPO",
                                semantic_type="Sign or Symptom"
                            ))
            
        except Exception as e:
            self.logger.error(f"HPO concept extraction failed: {e}")
            concepts = self._extract_basic_hpo_concepts(text)
        
        # Remove duplicates and sort by confidence
        unique_concepts = {}
        for concept in concepts:
            key = (concept.concept_id, concept.matched_text)
            if key not in unique_concepts or concept.confidence > unique_concepts[key].confidence:
                unique_concepts[key] = concept
        
        sorted_concepts = sorted(unique_concepts.values(), key=lambda x: x.confidence, reverse=True)
        return sorted_concepts[:max_concepts]
    
    def _extract_basic_hpo_concepts(self, text: str) -> List[ConceptMatch]:
        """Extract HPO concepts using basic pattern matching."""
        concepts = []
        
        # Common phenotype terms
        phenotype_terms = [
            'intellectual disability', 'developmental delay', 'seizures', 'epilepsy',
            'hypotonia', 'hypertonia', 'ataxia', 'dystonia', 'spasticity',
            'microcephaly', 'macrocephaly', 'growth retardation', 'failure to thrive',
            'hearing loss', 'vision loss', 'cataracts', 'retinal degeneration',
            'cardiomyopathy', 'heart defect', 'arrhythmia', 'hepatomegaly',
            'muscle weakness', 'myopathy', 'neuropathy', 'encephalopathy'
        ]
        
        text_lower = text.lower()
        
        for term in phenotype_terms:
            if term in text_lower:
                start_pos = text_lower.find(term)
                concepts.append(ConceptMatch(
                    concept_id=f"HPO_BASIC:{term.replace(' ', '_').upper()}",
                    concept_name=term,
                    matched_text=term,
                    start_pos=start_pos,
                    end_pos=start_pos + len(term),
                    confidence=0.7,
                    source="HPO_BASIC",
                    semantic_type="Sign or Symptom"
                ))
        
        return concepts
    
    def calculate_concept_density(self, 
                                text: str,
                                title: str = "",
                                pmid: str = None) -> ConceptDensityScore:
        """
        Calculate concept density score for a text.
        
        Args:
            text: Abstract or full text
            title: Article title (optional)
            pmid: PubMed ID (optional)
            
        Returns:
            ConceptDensityScore object
        """
        try:
            # Combine title and text for analysis
            full_text = f"{title} {text}".strip()
            
            # Count words
            word_count = len(re.findall(r'\b\w+\b', full_text))
            
            if word_count == 0:
                return ConceptDensityScore(
                    total_concepts=0,
                    unique_concepts=0,
                    concept_density=0.0,
                    umls_concepts=[],
                    hpo_concepts=[],
                    priority_score=0.0,
                    semantic_categories={},
                    reasoning="Empty text"
                )
            
            # Extract concepts
            umls_concepts = self.extract_umls_concepts(full_text)
            hpo_concepts = self.extract_hpo_concepts(full_text)
            
            # Combine all concepts
            all_concepts = umls_concepts + hpo_concepts
            
            # Remove duplicates based on concept ID
            unique_concept_ids = set()
            unique_concepts = []
            for concept in all_concepts:
                if concept.concept_id not in unique_concept_ids:
                    unique_concept_ids.add(concept.concept_id)
                    unique_concepts.append(concept)
            
            # Calculate density (concepts per 100 words)
            concept_density = (len(unique_concepts) / word_count) * 100
            
            # Count semantic categories
            semantic_categories = Counter()
            for concept in unique_concepts:
                if concept.semantic_type:
                    semantic_categories[concept.semantic_type] += 1
            
            # Calculate priority score
            priority_score = self._calculate_priority_score(
                unique_concepts, 
                concept_density, 
                word_count
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                unique_concepts, 
                concept_density, 
                semantic_categories,
                word_count
            )
            
            result = ConceptDensityScore(
                total_concepts=len(all_concepts),
                unique_concepts=len(unique_concepts),
                concept_density=concept_density,
                umls_concepts=umls_concepts,
                hpo_concepts=hpo_concepts,
                priority_score=priority_score,
                semantic_categories=dict(semantic_categories),
                reasoning=reasoning
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Concept density calculation failed for PMID {pmid}: {e}")
            
            return ConceptDensityScore(
                total_concepts=0,
                unique_concepts=0,
                concept_density=0.0,
                umls_concepts=[],
                hpo_concepts=[],
                priority_score=0.0,
                semantic_categories={},
                reasoning=f"Calculation failed: {str(e)}"
            )
    
    def _calculate_priority_score(self, 
                                concepts: List[ConceptMatch],
                                concept_density: float,
                                word_count: int) -> float:
        """Calculate priority score based on concept types and density."""
        if not concepts:
            return 0.0
        
        # Base score from concept density (normalized to 0-1)
        density_score = min(1.0, concept_density / 20.0)  # 20 concepts per 100 words = max
        
        # Weighted score from semantic types
        semantic_score = 0.0
        total_weight = 0.0
        
        for concept in concepts:
            weight = self.semantic_type_weights.get(concept.semantic_type, 1.0)
            semantic_score += weight * concept.confidence
            total_weight += weight
        
        if total_weight > 0:
            semantic_score = semantic_score / total_weight
        
        # Combine scores
        priority_score = (density_score * 0.4 + semantic_score * 0.6)
        
        # Bonus for high-value concept types
        high_value_types = {
            'Disease or Syndrome', 'Sign or Symptom', 'Congenital Abnormality',
            'Gene or Genome', 'Therapeutic or Preventive Procedure'
        }
        
        high_value_count = sum(
            1 for concept in concepts 
            if concept.semantic_type in high_value_types
        )
        
        if high_value_count >= 3:
            priority_score = min(1.0, priority_score + 0.1)
        
        return priority_score
    
    def _generate_reasoning(self, 
                          concepts: List[ConceptMatch],
                          concept_density: float,
                          semantic_categories: Counter,
                          word_count: int) -> str:
        """Generate human-readable reasoning for the score."""
        if not concepts:
            return "No medical concepts detected in the text."
        
        reasoning_parts = []
        
        # Density assessment
        if concept_density > 15:
            reasoning_parts.append("Very high concept density")
        elif concept_density > 10:
            reasoning_parts.append("High concept density")
        elif concept_density > 5:
            reasoning_parts.append("Moderate concept density")
        else:
            reasoning_parts.append("Low concept density")
        
        reasoning_parts.append(f"({concept_density:.1f} concepts per 100 words)")
        
        # Top semantic categories
        if semantic_categories:
            top_categories = semantic_categories.most_common(3)
            category_names = [cat for cat, count in top_categories]
            reasoning_parts.append(f"Primary concept types: {', '.join(category_names)}")
        
        # High-confidence concepts
        high_conf_concepts = [c for c in concepts if c.confidence > 0.8]
        if high_conf_concepts:
            reasoning_parts.append(f"{len(high_conf_concepts)} high-confidence matches")
        
        # Source distribution
        sources = Counter(c.source for c in concepts)
        if len(sources) > 1:
            source_info = ", ".join([f"{count} {source}" for source, count in sources.items()])
            reasoning_parts.append(f"Sources: {source_info}")
        
        return ". ".join(reasoning_parts) + "."
    
    def score_batch(self, 
                   articles: List[Dict[str, Any]],
                   batch_size: int = 50,
                   save_intermediate: bool = True,
                   output_dir: str = "data/concept_scoring") -> List[ConceptDensityScore]:
        """
        Score a batch of articles for concept density.
        
        Args:
            articles: List of article dictionaries
            batch_size: Batch size for intermediate saves
            save_intermediate: Whether to save intermediate results
            output_dir: Output directory for intermediate files
            
        Returns:
            List of ConceptDensityScore objects
        """
        results = []
        
        if save_intermediate:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for i, article in enumerate(articles):
            try:
                title = article.get('title', '')
                abstract = article.get('abstract', '')
                pmid = article.get('pmid', str(i))
                
                if not abstract:
                    self.logger.warning(f"No abstract for article {pmid}, skipping")
                    continue
                
                score = self.calculate_concept_density(abstract, title, pmid)
                results.append(score)
                
                # Log progress
                if (i + 1) % 10 == 0:
                    self.logger.info(f"Scored {i + 1}/{len(articles)} articles")
                
                # Save intermediate results
                if save_intermediate and (i + 1) % batch_size == 0:
                    self._save_intermediate_scores(results, output_dir, i + 1)
                
            except Exception as e:
                self.logger.error(f"Failed to score article {i}: {e}")
                continue
        
        # Save final results
        if save_intermediate:
            self._save_intermediate_scores(results, output_dir, len(articles), final=True)
        
        self.logger.info(f"Completed concept scoring for {len(results)} articles")
        return results
    
    def _save_intermediate_scores(self, 
                                results: List[ConceptDensityScore],
                                output_dir: str,
                                count: int,
                                final: bool = False) -> None:
        """Save intermediate scoring results."""
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        
        if final:
            filename = f"concept_scores_final_{timestamp}.json"
        else:
            filename = f"concept_scores_batch_{count}_{timestamp}.json"
        
        output_path = Path(output_dir) / filename
        
        # Convert results to serializable format
        serializable_results = []
        for score in results:
            score_dict = {
                'total_concepts': score.total_concepts,
                'unique_concepts': score.unique_concepts,
                'concept_density': score.concept_density,
                'priority_score': score.priority_score,
                'semantic_categories': score.semantic_categories,
                'reasoning': score.reasoning,
                'umls_concept_count': len(score.umls_concepts),
                'hpo_concept_count': len(score.hpo_concepts)
            }
            serializable_results.append(score_dict)
        
        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        self.logger.info(f"Saved {len(results)} concept scores to {output_path}")
    
    def create_priority_ranking(self, 
                              articles: List[Dict[str, Any]],
                              scores: List[ConceptDensityScore]) -> pd.DataFrame:
        """
        Create priority ranking of articles based on concept density scores.
        
        Args:
            articles: Original article data
            scores: Concept density scores
            
        Returns:
            DataFrame with ranked articles
        """
        # Combine articles with scores
        ranked_data = []
        
        for article, score in zip(articles, scores):
            row = {
                'PMID': article.get('pmid', ''),
                'Title': article.get('title', ''),
                'PriorityScore': score.priority_score,
                'ConceptDensity': score.concept_density,
                'UniqueConceptCount': score.unique_concepts,
                'UMLSConceptCount': len(score.umls_concepts),
                'HPOConceptCount': len(score.hpo_concepts),
                'TopSemanticTypes': '; '.join([
                    f"{cat}({count})" 
                    for cat, count in sorted(score.semantic_categories.items(), 
                                           key=lambda x: x[1], reverse=True)[:3]
                ]),
                'Reasoning': score.reasoning
            }
            ranked_data.append(row)
        
        # Create DataFrame and sort by priority score
        df = pd.DataFrame(ranked_data)
        df = df.sort_values('PriorityScore', ascending=False)
        df['Rank'] = range(1, len(df) + 1)
        
        return df
    
    def get_scoring_statistics(self, scores: List[ConceptDensityScore]) -> Dict[str, Any]:
        """Get statistics about concept scoring results."""
        if not scores:
            return {}
        
        priority_scores = [s.priority_score for s in scores]
        concept_densities = [s.concept_density for s in scores]
        unique_concept_counts = [s.unique_concepts for s in scores]
        
        # Aggregate semantic categories
        all_semantic_categories = Counter()
        for score in scores:
            all_semantic_categories.update(score.semantic_categories)
        
        stats = {
            'total_articles': len(scores),
            'priority_score_stats': {
                'mean': sum(priority_scores) / len(priority_scores),
                'min': min(priority_scores),
                'max': max(priority_scores),
                'high_priority_count': len([s for s in priority_scores if s > 0.7])
            },
            'concept_density_stats': {
                'mean': sum(concept_densities) / len(concept_densities),
                'min': min(concept_densities),
                'max': max(concept_densities)
            },
            'concept_count_stats': {
                'mean': sum(unique_concept_counts) / len(unique_concept_counts),
                'min': min(unique_concept_counts),
                'max': max(unique_concept_counts)
            },
            'top_semantic_categories': dict(all_semantic_categories.most_common(10))
        }
        
        return stats


# Utility functions

def score_leigh_syndrome_concepts(articles: List[Dict[str, Any]], 
                                hpo_manager=None,
                                output_csv: str = "data/leigh_syndrome_concept_scores.csv") -> List[ConceptDensityScore]:
    """
    Score Leigh syndrome articles for concept density.
    
    Args:
        articles: List of article dictionaries
        hpo_manager: HPO manager instance
        output_csv: Output CSV file path
        
    Returns:
        List of ConceptDensityScore objects
    """
    # Initialize scorer
    scorer = ConceptDensityScorer(hpo_manager=hpo_manager)
    
    # Score articles
    scores = scorer.score_batch(articles)
    
    # Create priority ranking
    ranking_df = scorer.create_priority_ranking(articles, scores)
    
    # Save results
    ranking_df.to_csv(output_csv, index=False)
    
    # Print statistics
    stats = scorer.get_scoring_statistics(scores)
    print(f"Concept Scoring Statistics:")
    print(f"Total articles: {stats['total_articles']}")
    print(f"Average priority score: {stats['priority_score_stats']['mean']:.3f}")
    print(f"High priority articles: {stats['priority_score_stats']['high_priority_count']}")
    print(f"Average concept density: {stats['concept_density_stats']['mean']:.1f}")
    
    return scores

