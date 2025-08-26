"""
Extraction Visualizer

Creates interactive visualizations for LangExtract results including
source grounding, extraction statistics, and quality metrics.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns


logger = logging.getLogger(__name__)


class ExtractionVisualizer:
    """
    Creates visualizations for LangExtract results.
    
    Provides interactive charts, statistics, and quality assessments
    for biomedical extraction results.
    """
    
    def __init__(self, style: str = "plotly_white"):
        """
        Initialize visualizer.
        
        Args:
            style: Plotly template style
        """
        self.style = style
        
        # Set up plotting styles
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def create_overview_dashboard(
        self,
        extraction_results: Dict[str, Any],
        title: str = "Biomedical Extraction Results - Overview"
    ) -> go.Figure:
        """
        Create overview dashboard with key metrics.
        
        Args:
            extraction_results: Normalized extraction results
            title: Dashboard title
            
        Returns:
            Plotly figure with overview dashboard
        """
        # Extract data
        normalized_data = extraction_results.get("normalized_data", [])
        if not normalized_data:
            return self._create_empty_figure("No data available")
        
        df = pd.DataFrame(normalized_data)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=[
                'Patient Sex Distribution',
                'Age of Onset Distribution',
                'Survival Status',
                'Gene Distribution',
                'Quality Scores',
                'Data Completeness'
            ],
            specs=[
                [{"type": "pie"}, {"type": "histogram"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "histogram"}, {"type": "bar"}]
            ]
        )
        
        # 1. Sex distribution
        if 'sex' in df.columns:
            sex_counts = df['sex'].value_counts()
            sex_labels = ['Male' if x == 'm' else 'Female' if x == 'f' else 'Unknown' for x in sex_counts.index]
            fig.add_trace(
                go.Pie(
                    labels=sex_labels,
                    values=sex_counts.values,
                    name="Sex",
                    marker_colors=['lightblue', 'lightpink', 'lightgray']
                ),
                row=1, col=1
            )
        
        # 2. Age of onset histogram
        if 'age_of_onset' in df.columns:
            ages = df['age_of_onset'].dropna()
            if len(ages) > 0:
                fig.add_trace(
                    go.Histogram(
                        x=ages,
                        name="Age of Onset",
                        nbinsx=min(10, len(ages)),
                        marker_color='skyblue'
                    ),
                    row=1, col=2
                )
        
        # 3. Survival status
        if '_0_alive_1_dead' in df.columns:
            survival_counts = df['_0_alive_1_dead'].value_counts()
            survival_labels = ['Alive' if x == 0 else 'Deceased' if x == 1 else 'Unknown' for x in survival_counts.index]
            fig.add_trace(
                go.Pie(
                    labels=survival_labels,
                    values=survival_counts.values,
                    name="Survival",
                    marker_colors=['lightgreen', 'lightcoral', 'lightgray']
                ),
                row=1, col=3
            )
        
        # 4. Gene distribution
        if 'gene' in df.columns:
            gene_counts = df['gene'].value_counts().head(10)
            if len(gene_counts) > 0:
                fig.add_trace(
                    go.Bar(
                        x=gene_counts.values,
                        y=gene_counts.index,
                        orientation='h',
                        name="Genes",
                        marker_color='lightcoral'
                    ),
                    row=2, col=1
                )
        
        # 5. Quality scores
        if 'normalization_quality' in df.columns:
            quality_scores = df['normalization_quality'].dropna()
            if len(quality_scores) > 0:
                fig.add_trace(
                    go.Histogram(
                        x=quality_scores,
                        name="Quality",
                        nbinsx=10,
                        marker_color='gold'
                    ),
                    row=2, col=2
                )
        
        # 6. Data completeness
        completeness_data = self._calculate_completeness(df)
        if completeness_data:
            fig.add_trace(
                go.Bar(
                    x=list(completeness_data.values()),
                    y=list(completeness_data.keys()),
                    orientation='h',
                    name="Completeness",
                    marker_color='lightseagreen'
                ),
                row=2, col=3
            )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text=title,
            showlegend=False,
            template=self.style
        )
        
        return fig
    
    def create_extraction_timeline(
        self,
        extraction_results: Dict[str, Any]
    ) -> go.Figure:
        """
        Create timeline visualization of extractions.
        
        Args:
            extraction_results: Extraction results
            
        Returns:
            Timeline figure
        """
        normalized_data = extraction_results.get("normalized_data", [])
        if not normalized_data:
            return self._create_empty_figure("No data for timeline")
        
        df = pd.DataFrame(normalized_data)
        
        # Create timeline based on age of onset
        if 'age_of_onset' in df.columns and 'patient_id' in df.columns:
            timeline_data = df[['patient_id', 'age_of_onset', 'gene', 'phenotypes_text']].dropna(subset=['age_of_onset'])
            
            if len(timeline_data) > 0:
                fig = px.scatter(
                    timeline_data,
                    x='age_of_onset',
                    y='patient_id',
                    color='gene',
                    hover_data=['phenotypes_text'],
                    title='Patient Timeline by Age of Onset',
                    labels={'age_of_onset': 'Age of Onset (years)', 'patient_id': 'Patient ID'}
                )
                
                fig.update_layout(template=self.style)
                return fig
        
        return self._create_empty_figure("Insufficient data for timeline")
    
    def create_phenotype_network(
        self,
        extraction_results: Dict[str, Any]
    ) -> go.Figure:
        """
        Create network visualization of phenotypes and genes.
        
        Args:
            extraction_results: Extraction results
            
        Returns:
            Network figure
        """
        normalized_data = extraction_results.get("normalized_data", [])
        if not normalized_data:
            return self._create_empty_figure("No data for network")
        
        df = pd.DataFrame(normalized_data)
        
        # Create co-occurrence matrix
        if 'gene' in df.columns and 'phenotypes_text' in df.columns:
            # Extract gene-phenotype relationships
            relationships = []
            
            for _, row in df.iterrows():
                gene = row.get('gene')
                phenotypes = row.get('phenotypes_text')
                
                if gene and phenotypes:
                    pheno_list = [p.strip() for p in str(phenotypes).split(';')]
                    for phenotype in pheno_list:
                        if phenotype:
                            relationships.append({'gene': gene, 'phenotype': phenotype})
            
            if relationships:
                rel_df = pd.DataFrame(relationships)
                
                # Create heatmap of gene-phenotype co-occurrence
                pivot_table = rel_df.groupby(['gene', 'phenotype']).size().unstack(fill_value=0)
                
                fig = px.imshow(
                    pivot_table.values,
                    x=pivot_table.columns,
                    y=pivot_table.index,
                    title='Gene-Phenotype Co-occurrence Matrix',
                    labels={'x': 'Phenotypes', 'y': 'Genes', 'color': 'Co-occurrence Count'}
                )
                
                fig.update_layout(template=self.style)
                return fig
        
        return self._create_empty_figure("Insufficient data for network")
    
    def create_quality_assessment(
        self,
        extraction_results: Dict[str, Any]
    ) -> go.Figure:
        """
        Create quality assessment visualization.
        
        Args:
            extraction_results: Extraction results
            
        Returns:
            Quality assessment figure
        """
        # Get quality metrics
        norm_meta = extraction_results.get("normalization_metadata", {})
        quality_metrics = norm_meta.get("quality_metrics", {})
        
        if not quality_metrics:
            return self._create_empty_figure("No quality metrics available")
        
        # Create quality dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Overall Quality Score',
                'Data Completeness',
                'HPO Mappings',
                'Gene Mappings'
            ],
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )
        
        # Overall quality indicator
        avg_quality = quality_metrics.get("average_quality", 0)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=avg_quality * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Quality Score (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=1, col=1
        )
        
        # Completeness indicator
        completeness = quality_metrics.get("completeness", 0)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=completeness * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Completeness (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgray"},
                        {'range': [30, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "green"}
                    ]
                }
            ),
            row=1, col=2
        )
        
        # HPO mappings
        hpo_mappings = norm_meta.get("hpo_mappings", 0)
        total_patients = quality_metrics.get("total_records", 1)
        
        fig.add_trace(
            go.Bar(
                x=['HPO Mappings'],
                y=[hpo_mappings],
                name="HPO",
                marker_color='lightblue',
                text=[f"{hpo_mappings} mappings<br>{hpo_mappings/total_patients:.1f} per patient"],
                textposition='auto'
            ),
            row=2, col=1
        )
        
        # Gene mappings
        gene_mappings = norm_meta.get("gene_mappings", 0)
        
        fig.add_trace(
            go.Bar(
                x=['Gene Mappings'],
                y=[gene_mappings],
                name="Genes",
                marker_color='lightcoral',
                text=[f"{gene_mappings} mappings<br>{gene_mappings/total_patients:.1f} per patient"],
                textposition='auto'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            title_text="Quality Assessment Dashboard",
            showlegend=False,
            template=self.style
        )
        
        return fig
    
    def create_field_comparison(
        self,
        evaluation_results: Dict[str, Any]
    ) -> go.Figure:
        """
        Create field-by-field comparison visualization.
        
        Args:
            evaluation_results: Evaluation results from ground truth comparison
            
        Returns:
            Field comparison figure
        """
        field_comparisons = evaluation_results.get("field_comparisons", {})
        
        if not field_comparisons:
            return self._create_empty_figure("No field comparison data")
        
        # Convert to DataFrame
        df = pd.DataFrame(field_comparisons).T
        df = df.reset_index()
        df.rename(columns={'index': 'field'}, inplace=True)
        
        # Create grouped bar chart
        fig = px.bar(
            df,
            x='field',
            y=['precision', 'recall', 'f1', 'accuracy'],
            title='Field-by-Field Performance Metrics',
            barmode='group',
            labels={'value': 'Score', 'field': 'Field', 'variable': 'Metric'}
        )
        
        fig.update_layout(
            template=self.style,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_extraction_statistics(
        self,
        extraction_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive extraction statistics.
        
        Args:
            extraction_results: Extraction results
            
        Returns:
            Dictionary of statistics
        """
        stats = {
            "overview": {},
            "quality": {},
            "content": {},
            "performance": {}
        }
        
        # Overview statistics
        normalized_data = extraction_results.get("normalized_data", [])
        total_extractions = len(extraction_results.get("extractions", []))
        
        stats["overview"] = {
            "total_patients": len(normalized_data),
            "total_extractions": total_extractions,
            "extractions_per_patient": total_extractions / len(normalized_data) if normalized_data else 0
        }
        
        if normalized_data:
            df = pd.DataFrame(normalized_data)
            
            # Quality statistics
            if 'normalization_quality' in df.columns:
                quality_scores = df['normalization_quality'].dropna()
                stats["quality"] = {
                    "average_quality": quality_scores.mean(),
                    "quality_std": quality_scores.std(),
                    "min_quality": quality_scores.min(),
                    "max_quality": quality_scores.max()
                }
            
            # Content statistics
            stats["content"] = {
                "patients_with_sex": df['sex'].notna().sum(),
                "patients_with_age": df['age_of_onset'].notna().sum(),
                "patients_with_genes": df['gene'].notna().sum(),
                "patients_with_phenotypes": df['phenotypes_text'].notna().sum(),
                "patients_with_treatments": df['treatments'].notna().sum()
            }
            
            # Age statistics
            if 'age_of_onset' in df.columns:
                ages = df['age_of_onset'].dropna()
                if len(ages) > 0:
                    stats["content"]["age_statistics"] = {
                        "mean_age": ages.mean(),
                        "median_age": ages.median(),
                        "age_range": [ages.min(), ages.max()],
                        "age_std": ages.std()
                    }
        
        # Performance statistics from metadata
        norm_meta = extraction_results.get("normalization_metadata", {})
        stats["performance"] = {
            "hpo_mappings": norm_meta.get("hpo_mappings", 0),
            "gene_mappings": norm_meta.get("gene_mappings", 0),
            "processing_timestamp": norm_meta.get("timestamp")
        }
        
        return stats
    
    def save_visualizations(
        self,
        extraction_results: Dict[str, Any],
        output_dir: Union[str, Path],
        filename_prefix: str = "extraction_viz"
    ) -> Dict[str, Path]:
        """
        Save all visualizations to files.
        
        Args:
            extraction_results: Extraction results
            output_dir: Output directory
            filename_prefix: Filename prefix
            
        Returns:
            Dictionary of saved file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        try:
            # Overview dashboard
            overview_fig = self.create_overview_dashboard(extraction_results)
            overview_path = output_dir / f"{filename_prefix}_overview.html"
            overview_fig.write_html(str(overview_path))
            saved_files["overview"] = overview_path
            
            # Quality assessment
            quality_fig = self.create_quality_assessment(extraction_results)
            quality_path = output_dir / f"{filename_prefix}_quality.html"
            quality_fig.write_html(str(quality_path))
            saved_files["quality"] = quality_path
            
            # Timeline
            timeline_fig = self.create_extraction_timeline(extraction_results)
            timeline_path = output_dir / f"{filename_prefix}_timeline.html"
            timeline_fig.write_html(str(timeline_path))
            saved_files["timeline"] = timeline_path
            
            # Phenotype network
            network_fig = self.create_phenotype_network(extraction_results)
            network_path = output_dir / f"{filename_prefix}_network.html"
            network_fig.write_html(str(network_path))
            saved_files["network"] = network_path
            
            # Statistics
            stats = self.create_extraction_statistics(extraction_results)
            stats_path = output_dir / f"{filename_prefix}_statistics.json"
            with open(stats_path, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            saved_files["statistics"] = stats_path
            
            logger.info(f"Visualizations saved to {len(saved_files)} files")
            
        except Exception as e:
            logger.error(f"Error saving visualizations: {e}")
        
        return saved_files
    
    def _calculate_completeness(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate data completeness for each field."""
        if df.empty:
            return {}
        
        completeness = {}
        key_fields = ['sex', 'age_of_onset', 'gene', 'phenotypes_text', 'treatments']
        
        for field in key_fields:
            if field in df.columns:
                completeness[field] = (df[field].notna().sum() / len(df)) * 100
        
        return completeness
    
    def _create_empty_figure(self, message: str) -> go.Figure:
        """Create empty figure with message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            template=self.style
        )
        return fig


# Example usage
if __name__ == "__main__":
    # Test visualization with sample data
    sample_results = {
        "normalized_data": [
            {
                "patient_id": "Patient 1",
                "sex": "m",
                "age_of_onset": 3.0,
                "gene": "MT-ATP6",
                "phenotypes_text": "developmental delay; lactic acidosis",
                "treatments": "riboflavin 100 mg/day",
                "_0_alive_1_dead": 0,
                "normalization_quality": 0.85
            },
            {
                "patient_id": "Patient 2", 
                "sex": "f",
                "age_of_onset": 2.42,
                "gene": "SLC19A3",
                "phenotypes_text": "generalized weakness; recurrent episodes",
                "treatments": "thiamine and biotin",
                "_0_alive_1_dead": 0,
                "normalization_quality": 0.92
            }
        ],
        "normalization_metadata": {
            "total_patients": 2,
            "hpo_mappings": 4,
            "gene_mappings": 2,
            "quality_metrics": {
                "average_quality": 0.885,
                "completeness": 0.9,
                "total_records": 2,
                "complete_records": 2
            }
        }
    }
    
    # Create visualizer
    visualizer = ExtractionVisualizer()
    
    # Create overview dashboard
    fig = visualizer.create_overview_dashboard(sample_results)
    fig.show()
    
    # Create quality assessment
    quality_fig = visualizer.create_quality_assessment(sample_results)
    quality_fig.show()
    
    # Get statistics
    stats = visualizer.create_extraction_statistics(sample_results)
    print("Statistics:")
    print(json.dumps(stats, indent=2, default=str))

