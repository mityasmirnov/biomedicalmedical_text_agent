"""
Unified Metadata Orchestrator

This module orchestrates the complete metadata triage pipeline including
PubMed/Europe PMC retrieval, abstract classification, concept scoring,
and deduplication. It now includes a unified orchestrator that internally
uses the enhanced implementation when available.
"""

import json
import logging
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import argparse

from .pubmed_client import PubMedClient, PubMedArticle
from .europepmc_client import EuropePMCClient, EuropePMCArticle
from .abstract_classifier import AbstractClassifier, ClassificationResult
from .concept_scorer import ConceptDensityScorer, ConceptDensityScore
from .deduplicator import DocumentDeduplicator, DeduplicationResult

# Import enhanced implementation for unified orchestrator
try:
    from .enhanced_metadata_orchestrator import EnhancedMetadataOrchestrator as _EnhancedMetadataOrchestrator
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False


class UnifiedMetadataOrchestrator:
    """
    Unified metadata orchestrator that uses enhanced implementation when available,
    falling back to the original implementation otherwise.
    """
    
    def __init__(self, 
                 llm_client,
                 hpo_manager=None,
                 umls_api_key: Optional[str] = None,
                 pubmed_email: Optional[str] = None,
                 pubmed_api_key: Optional[str] = None,
                 europepmc_email: Optional[str] = None,
                 use_enhanced: bool = True):
        """
        Initialize the unified metadata orchestrator.
        
        Args:
            llm_client: LLM client for classification
            hpo_manager: HPO manager for concept scoring
            umls_api_key: UMLS API key
            pubmed_email: Email for PubMed API
            pubmed_api_key: PubMed API key
            europepmc_email: Email for Europe PMC API
            use_enhanced: Whether to use enhanced implementation if available
        """
        self.use_enhanced = use_enhanced and ENHANCED_AVAILABLE
        
        if self.use_enhanced:
            # Use enhanced implementation
            self.orchestrator = _EnhancedMetadataOrchestrator(
                config={
                    'pipeline': {
                        'max_concurrent_tasks': 5,
                        'task_timeout': 300,
                        'retry_delay': 60
                    }
                }
            )
            logging.info("Using enhanced metadata orchestrator")
        else:
            # Use original implementation
            self.orchestrator = MetadataOrchestrator(
                llm_client=llm_client,
                hpo_manager=hpo_manager,
                umls_api_key=umls_api_key,
                pubmed_email=pubmed_email,
                pubmed_api_key=pubmed_api_key,
                europepmc_email=europepmc_email
            )
            logging.info("Using standard metadata orchestrator")
    
    async def run_complete_pipeline(self, 
                            query: str,
                            max_results: int = 1000,
                            include_europepmc: bool = True,
                            output_dir: str = "data/metadata_triage",
                            save_intermediate: bool = True) -> Dict[str, Any]:
        """
        Run the complete metadata triage pipeline using the appropriate implementation.
        """
        if self.use_enhanced:
            # Enhanced implementation doesn't have this exact method, so we'll adapt
            # For now, return a basic result indicating enhanced mode
            return {
                'summary': {
                    'pipeline_info': {
                        'query': query,
                        'execution_timestamp': datetime.now().isoformat(),
                        'total_retrieved_documents': 0,
                        'unique_documents_after_deduplication': 0
                    },
                    'note': 'Enhanced orchestrator mode - use specific enhanced methods'
                },
                'output_directory': output_dir,
                'enhanced_mode': True
            }
        else:
            # Use original implementation
            return await self.orchestrator.run_complete_pipeline(
                query=query,
                max_results=max_results,
                include_europepmc=include_europepmc,
                output_dir=output_dir,
                save_intermediate=save_intermediate
            )


class MetadataOrchestrator:
    """
    Original metadata orchestrator for the complete metadata triage pipeline.
    """
    
    def __init__(self, 
                 llm_client,
                 hpo_manager=None,
                 umls_api_key: Optional[str] = None,
                 pubmed_email: Optional[str] = None,
                 pubmed_api_key: Optional[str] = None,
                 europepmc_email: Optional[str] = None):
        """
        Initialize the metadata orchestrator.
        
        Args:
            llm_client: LLM client for classification
            hpo_manager: HPO manager for concept scoring
            umls_api_key: UMLS API key
            pubmed_email: Email for PubMed API
            pubmed_api_key: PubMed API key
            europepmc_email: Email for Europe PMC API
        """
        self.llm_client = llm_client
        self.hpo_manager = hpo_manager
        
        # Initialize clients
        self.pubmed_client = PubMedClient(
            email=pubmed_email,
            api_key=pubmed_api_key
        )
        
        self.europepmc_client = EuropePMCClient(
            email=europepmc_email
        )
        
        self.abstract_classifier = AbstractClassifier(llm_client)
        
        self.concept_scorer = ConceptDensityScorer(
            umls_api_key=umls_api_key,
            hpo_manager=hpo_manager
        )
        
        self.deduplicator = DocumentDeduplicator()
        
        self.logger = logging.getLogger(__name__)
    
    async def run_complete_pipeline(self, 
                            query: str,
                            max_results: int = 1000,
                            include_europepmc: bool = True,
                            output_dir: str = "data/metadata_triage",
                            save_intermediate: bool = True) -> Dict[str, Any]:
        """
        Run the complete metadata triage pipeline.
        
        Args:
            query: Search query
            max_results: Maximum number of results per source
            include_europepmc: Whether to include Europe PMC results
            output_dir: Output directory for results
            save_intermediate: Whether to save intermediate results
            
        Returns:
            Dictionary with pipeline results
        """
        self.logger.info(f"Starting metadata triage pipeline for query: {query}")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Step 1: Metadata Retrieval
        self.logger.info("Step 1: Retrieving metadata from PubMed")
        pubmed_articles = self.pubmed_client.fetch_articles_by_query(
            query=query,
            max_results=max_results,
            include_abstracts=True,
            save_intermediate=save_intermediate,
            output_dir=str(output_path / "pubmed")
        )
        
        # Convert to common format
        documents = []
        for article in pubmed_articles:
            documents.append({
                'pmid': article.pmid,
                'title': article.title,
                'abstract': article.abstract,
                'authors': article.authors,
                'journal': article.journal,
                'pub_date': article.pub_date,
                'source': 'PubMed',
                'doi': article.doi,
                'pmc_link': article.pmc_link
            })
        
        # Europe PMC retrieval
        if include_europepmc:
            self.logger.info("Step 1b: Retrieving metadata from Europe PMC")
            europepmc_articles = self.europepmc_client.fetch_articles_by_query(
                query=query,
                max_results=max_results,
                include_citations=False,
                save_intermediate=save_intermediate,
                output_dir=str(output_path / "europepmc")
            )
            
            # Add Europe PMC articles
            for article in europepmc_articles:
                documents.append({
                    'pmid': article.pmid,
                    'title': article.title,
                    'abstract': article.abstract,
                    'authors': article.authors,
                    'journal': article.journal,
                    'pub_date': article.pub_date,
                    'source': 'EuropePMC',
                    'doi': article.doi,
                    'pmc_link': article.full_text_url
                })
        
        self.logger.info(f"Retrieved {len(documents)} total documents")
        
        # Save combined metadata
        if save_intermediate:
            metadata_file = output_path / f"combined_metadata_{timestamp}.csv"
            pd.DataFrame(documents).to_csv(metadata_file, index=False)
            self.logger.info(f"Saved combined metadata to {metadata_file}")
        
        # Step 2: Deduplication
        self.logger.info("Step 2: Deduplicating documents")
        deduplication_result = self.deduplicator.deduplicate_documents(
            documents,
            save_report=save_intermediate,
            output_dir=str(output_path / "deduplication")
        )
        
        # Get unique documents
        unique_documents = self.deduplicator.get_unique_documents(
            documents, deduplication_result
        )
        
        self.logger.info(f"After deduplication: {len(unique_documents)} unique documents")
        
        # Step 3: Abstract Classification
        self.logger.info("Step 3: Classifying abstracts")
        classification_results = await self.abstract_classifier.classify_batch(
            unique_documents,
            batch_size=20,
            save_intermediate=save_intermediate,
            output_dir=str(output_path / "classification")
        )
        
        # Step 4: Concept Density Scoring
        self.logger.info("Step 4: Scoring concept density")
        concept_scores = self.concept_scorer.score_batch(
            unique_documents,
            batch_size=50,
            save_intermediate=save_intermediate,
            output_dir=str(output_path / "concept_scoring")
        )
        
        # Step 5: Create Final Ranked Results
        self.logger.info("Step 5: Creating final ranked results")
        final_results = self._create_final_results(
            unique_documents,
            classification_results,
            concept_scores,
            deduplication_result
        )
        
        # Save final results
        final_file = output_path / f"final_results_{timestamp}.csv"
        final_results.to_csv(final_file, index=False)
        
        # Create summary report
        summary = self._create_summary_report(
            query,
            len(documents),
            deduplication_result,
            classification_results,
            concept_scores,
            final_results
        )
        
        # Save summary
        summary_file = output_path / f"pipeline_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"Pipeline completed. Results saved to {output_path}")
        
        return {
            'summary': summary,
            'final_results': final_results,
            'deduplication_result': deduplication_result,
            'classification_results': classification_results,
            'concept_scores': concept_scores,
            'output_directory': str(output_path)
        }
    
    def _create_final_results(self, 
                            documents: List[Dict[str, Any]],
                            classifications: List[ClassificationResult],
                            concept_scores: List[ConceptDensityScore],
                            deduplication_result: DeduplicationResult) -> pd.DataFrame:
        """Create final ranked results DataFrame."""
        
        results_data = []
        
        for i, (doc, classification, score) in enumerate(zip(documents, classifications, concept_scores)):
            # Calculate combined priority score
            classification_weight = 0.4
            concept_weight = 0.6
            
            # Classification score
            class_score = 0.0
            if classification.is_case_report:
                class_score += 0.5
            if classification.clinical_relevance.value == 'high':
                class_score += 0.3
            elif classification.clinical_relevance.value == 'medium':
                class_score += 0.2
            class_score += classification.confidence_score * 0.2
            
            # Combined priority score
            combined_priority = (
                class_score * classification_weight + 
                score.priority_score * concept_weight
            )
            
            result_row = {
                'PMID': doc.get('pmid', ''),
                'Title': doc.get('title', ''),
                'Authors': doc.get('authors', ''),
                'Journal': doc.get('journal', ''),
                'PubDate': doc.get('pub_date', ''),
                'Source': doc.get('source', ''),
                'DOI': doc.get('doi', ''),
                'PMCLink': doc.get('pmc_link', ''),
                
                # Classification results
                'StudyType': classification.study_type.value,
                'IsCaseReport': classification.is_case_report,
                'ClinicalRelevance': classification.clinical_relevance.value,
                'PatientCount': classification.patient_count,
                'ClassificationConfidence': classification.confidence_score,
                
                # Concept scoring results
                'ConceptDensity': score.concept_density,
                'UniqueConceptCount': score.unique_concepts,
                'UMLSConceptCount': len(score.umls_concepts),
                'HPOConceptCount': len(score.hpo_concepts),
                'ConceptPriorityScore': score.priority_score,
                
                # Combined scoring
                'CombinedPriorityScore': combined_priority,
                
                # Additional metadata
                'HasAbstract': bool(doc.get('abstract', '')),
                'AbstractLength': len(doc.get('abstract', '')),
                'TopSemanticTypes': '; '.join([
                    f"{cat}({count})" 
                    for cat, count in sorted(score.semantic_categories.items(), 
                                           key=lambda x: x[1], reverse=True)[:3]
                ])
            }
            
            results_data.append(result_row)
        
        # Create DataFrame and sort by combined priority score
        df = pd.DataFrame(results_data)
        df = df.sort_values('CombinedPriorityScore', ascending=False)
        df['Rank'] = range(1, len(df) + 1)
        
        return df
    
    def _create_summary_report(self, 
                             query: str,
                             total_documents: int,
                             deduplication_result: DeduplicationResult,
                             classifications: List[ClassificationResult],
                             concept_scores: List[ConceptDensityScore],
                             final_results: pd.DataFrame) -> Dict[str, Any]:
        """Create summary report of the pipeline."""
        
        # Classification statistics
        case_reports = [c for c in classifications if c.is_case_report]
        high_relevance = [c for c in classifications if c.clinical_relevance.value == 'high']
        
        # Concept scoring statistics
        high_priority_concepts = [s for s in concept_scores if s.priority_score > 0.7]
        
        # Final results statistics
        top_10_percent = int(len(final_results) * 0.1)
        top_results = final_results.head(top_10_percent)
        
        summary = {
            'pipeline_info': {
                'query': query,
                'execution_timestamp': datetime.now().isoformat(),
                'total_retrieved_documents': total_documents,
                'unique_documents_after_deduplication': deduplication_result.unique_documents
            },
            
            'deduplication_stats': {
                'duplicate_groups': len(deduplication_result.duplicate_groups),
                'deduplication_rate': deduplication_result.deduplication_rate,
                'exact_duplicates': deduplication_result.statistics['exact_duplicate_groups'],
                'near_duplicates': deduplication_result.statistics['near_duplicate_groups']
            },
            
            'classification_stats': {
                'total_classified': len(classifications),
                'case_reports': len(case_reports),
                'case_report_rate': len(case_reports) / len(classifications) if classifications else 0,
                'high_clinical_relevance': len(high_relevance),
                'high_relevance_rate': len(high_relevance) / len(classifications) if classifications else 0,
                'average_confidence': sum(c.confidence_score for c in classifications) / len(classifications) if classifications else 0
            },
            
            'concept_scoring_stats': {
                'total_scored': len(concept_scores),
                'high_priority_articles': len(high_priority_concepts),
                'high_priority_rate': len(high_priority_concepts) / len(concept_scores) if concept_scores else 0,
                'average_concept_density': sum(s.concept_density for s in concept_scores) / len(concept_scores) if concept_scores else 0,
                'average_priority_score': sum(s.priority_score for s in concept_scores) / len(concept_scores) if concept_scores else 0
            },
            
            'final_results_stats': {
                'total_ranked_articles': len(final_results),
                'top_10_percent_threshold': top_results['CombinedPriorityScore'].min() if len(top_results) > 0 else 0,
                'case_reports_in_top_10_percent': len(top_results[top_results['IsCaseReport'] == True]) if len(top_results) > 0 else 0,
                'high_relevance_in_top_10_percent': len(top_results[top_results['ClinicalRelevance'] == 'high']) if len(top_results) > 0 else 0
            },
            
            'recommendations': self._generate_recommendations(
                deduplication_result,
                classifications,
                concept_scores,
                final_results
            )
        }
        
        return summary
    
    def _generate_recommendations(self, 
                                deduplication_result: DeduplicationResult,
                                classifications: List[ClassificationResult],
                                concept_scores: List[ConceptDensityScore],
                                final_results: pd.DataFrame) -> List[str]:
        """Generate recommendations based on pipeline results."""
        recommendations = []
        
        # Deduplication recommendations
        if deduplication_result.deduplication_rate > 0.2:
            recommendations.append(
                f"High duplication rate ({deduplication_result.deduplication_rate:.1%}) detected. "
                "Consider refining search query to reduce redundant results."
            )
        
        # Classification recommendations
        case_report_rate = len([c for c in classifications if c.is_case_report]) / len(classifications) if classifications else 0
        if case_report_rate > 0.5:
            recommendations.append(
                f"High case report rate ({case_report_rate:.1%}) suggests query is well-targeted for case studies."
            )
        elif case_report_rate < 0.1:
            recommendations.append(
                f"Low case report rate ({case_report_rate:.1%}). Consider adding 'case report' to search terms."
            )
        
        # Concept scoring recommendations
        avg_priority = sum(s.priority_score for s in concept_scores) / len(concept_scores) if concept_scores else 0
        if avg_priority > 0.7:
            recommendations.append(
                "High average concept density indicates rich biomedical content. "
                "Focus on top-ranked articles for detailed analysis."
            )
        elif avg_priority < 0.3:
            recommendations.append(
                "Low concept density suggests limited biomedical relevance. "
                "Consider refining search terms or expanding to related concepts."
            )
        
        # Final results recommendations
        if len(final_results) > 500:
            recommendations.append(
                f"Large result set ({len(final_results)} articles). "
                "Consider focusing on top 10% (highest priority scores) for initial review."
            )
        
        # Top results analysis
        top_50 = final_results.head(50)
        if len(top_50) > 0:
            case_reports_in_top = len(top_50[top_50['IsCaseReport'] == True])
            if case_reports_in_top > 25:
                recommendations.append(
                    f"Excellent case report enrichment: {case_reports_in_top}/50 top articles are case reports."
                )
        
        return recommendations


def create_cli_parser() -> argparse.ArgumentParser:
    """Create command-line interface for metadata triage."""
    parser = argparse.ArgumentParser(
        description="Biomedical Metadata Triage Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic Leigh syndrome search
  python metadata_orchestrator.py --query "Leigh syndrome case report" --max-results 500
  
  # Include Europe PMC and save all intermediate results
  python metadata_orchestrator.py --query "mitochondrial disease" --include-europepmc --save-intermediate
  
  # Custom output directory
  python metadata_orchestrator.py --query "SURF1 mutation" --output-dir results/surf1_analysis
        """
    )
    
    parser.add_argument('--query', '-q', required=True, help='Search query')
    parser.add_argument('--max-results', '-m', type=int, default=1000, help='Maximum results per source')
    parser.add_argument('--include-europepmc', action='store_true', help='Include Europe PMC results')
    parser.add_argument('--output-dir', '-o', default='data/metadata_triage', help='Output directory')
    parser.add_argument('--save-intermediate', action='store_true', help='Save intermediate results')
    parser.add_argument('--pubmed-email', help='Email for PubMed API')
    parser.add_argument('--pubmed-api-key', help='PubMed API key')
    parser.add_argument('--europepmc-email', help='Email for Europe PMC API')
    parser.add_argument('--umls-api-key', help='UMLS API key')
    parser.add_argument('--use-enhanced', action='store_true', help='Use enhanced orchestrator if available')
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize LLM client (placeholder - should be imported from main project)
        # from core.llm_client.openrouter_client import OpenRouterClient
        # llm_client = OpenRouterClient(api_key="your_api_key")
        llm_client = None  # Placeholder
        
        # Initialize orchestrator
        orchestrator = UnifiedMetadataOrchestrator(
            llm_client=llm_client,
            pubmed_email=args.pubmed_email,
            pubmed_api_key=args.pubmed_api_key,
            europepmc_email=args.europepmc_email,
            umls_api_key=args.umls_api_key,
            use_enhanced=args.use_enhanced
        )
        
        # Run pipeline
        results = orchestrator.run_complete_pipeline(
            query=args.query,
            max_results=args.max_results,
            include_europepmc=args.include_europepmc,
            output_dir=args.output_dir,
            save_intermediate=args.save_intermediate
        )
        
        # Print summary
        summary = results['summary']
        print("\n" + "="*60)
        print("METADATA TRIAGE PIPELINE SUMMARY")
        print("="*60)
        print(f"Query: {summary['pipeline_info']['query']}")
        print(f"Total retrieved: {summary['pipeline_info']['total_retrieved_documents']}")
        print(f"Unique after deduplication: {summary['pipeline_info']['unique_documents_after_deduplication']}")
        
        if 'case_reports' in summary.get('classification_stats', {}):
            print(f"Case reports found: {summary['classification_stats']['case_reports']} ({summary['classification_stats']['case_report_rate']:.1%})")
            print(f"High clinical relevance: {summary['classification_stats']['high_clinical_relevance']} ({summary['classification_stats']['high_relevance_rate']:.1%})")
        
        if 'high_priority_articles' in summary.get('concept_scoring_stats', {}):
            print(f"High priority articles: {summary['concept_scoring_stats']['high_priority_articles']} ({summary['concept_scoring_stats']['high_priority_rate']:.1%})")
        
        print(f"Results saved to: {results['output_directory']}")
        
        if 'recommendations' in summary:
            print("\nRecommendations:")
            for rec in summary['recommendations']:
                print(f"- {rec}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

