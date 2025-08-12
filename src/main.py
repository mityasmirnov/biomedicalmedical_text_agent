"""
Main CLI interface for the Biomedical Data Extraction Engine.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.json import JSON

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.config import get_config
from core.logging_config import setup_logging, get_logger
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator

console = Console()
log = get_logger(__name__)

@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--log-file', help='Log file path')
def cli(debug, log_file):
    """Biomedical Data Extraction Engine CLI."""
    # Setup logging
    log_config = {}
    if debug:
        log_config['log_level'] = 'DEBUG'
    if log_file:
        log_config['log_file'] = log_file
    
    setup_logging(log_config)
    
    console.print(Panel.fit(
        "[bold blue]Biomedical Data Extraction Engine[/bold blue]\n"
        "AI-powered extraction of patient data from medical literature",
        border_style="blue"
    ))

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file path (JSON format)')
@click.option('--format', 'output_format', default='json', 
              type=click.Choice(['json', 'csv', 'table']), 
              help='Output format')
@click.option('--validate', is_flag=True, help='Validate against ground truth')
@click.option('--ground-truth', help='Ground truth file for validation')
def extract(file_path, output, output_format, validate, ground_truth):
    """Extract patient data from a medical document."""
    
    async def run_extraction():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                
                # Initialize orchestrator
                task = progress.add_task("Initializing extraction pipeline...", total=None)
                orchestrator = ExtractionOrchestrator()
                
                # Run extraction
                progress.update(task, description=f"Processing {Path(file_path).name}...")
                result = await orchestrator.extract_from_file(file_path)
                
                progress.update(task, description="Extraction completed", completed=True)
            
            if not result.success:
                console.print(f"[red]Extraction failed: {result.error}[/red]")
                return
            
            records = result.data
            console.print(f"[green]Successfully extracted {len(records)} patient records[/green]")
            
            # Display warnings if any
            if result.warnings:
                console.print(f"[yellow]Warnings ({len(result.warnings)}):[/yellow]")
                for warning in result.warnings:
                    console.print(f"  • {warning}")
            
            # Output results
            if output_format == 'table':
                display_records_table(records)
            elif output_format == 'json':
                json_output = [record.data for record in records]
                if output:
                    save_json_output(json_output, output)
                else:
                    console.print(JSON.from_data(json_output))
            elif output_format == 'csv':
                if not output:
                    output = f"{Path(file_path).stem}_extracted.csv"
                save_csv_output(records, output)
            
            # Validation against ground truth
            if validate and ground_truth:
                validate_against_ground_truth(records, ground_truth)
            
            # Display statistics
            stats = orchestrator.get_extraction_statistics(records)
            display_statistics(stats)
            
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            log.error(f"CLI extraction error: {str(e)}")
    
    asyncio.run(run_extraction())

@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False))
@click.option('--pattern', default='*.pdf', help='File pattern to match')
@click.option('--output', '-o', help='Output directory')
@click.option('--max-files', type=int, help='Maximum number of files to process')
def batch(directory, pattern, output, max_files):
    """Extract patient data from multiple files in a directory."""
    
    async def run_batch_extraction():
        try:
            # Find files
            dir_path = Path(directory)
            files = list(dir_path.glob(pattern))
            
            if max_files:
                files = files[:max_files]
            
            if not files:
                console.print(f"[yellow]No files found matching pattern '{pattern}' in {directory}[/yellow]")
                return
            
            console.print(f"Found {len(files)} files to process")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                
                # Initialize orchestrator
                task = progress.add_task("Initializing batch extraction...", total=None)
                orchestrator = ExtractionOrchestrator()
                
                # Run batch extraction
                progress.update(task, description=f"Processing {len(files)} files...")
                result = await orchestrator.extract_batch([str(f) for f in files])
                
                progress.update(task, description="Batch extraction completed", completed=True)
            
            if not result.success:
                console.print(f"[red]Batch extraction failed: {result.error}[/red]")
                return
            
            records = result.data
            console.print(f"[green]Successfully extracted {len(records)} patient records from {len(files)} files[/green]")
            
            # Save results
            if output:
                output_path = Path(output)
                output_path.mkdir(parents=True, exist_ok=True)
                
                # Save individual files
                for i, record in enumerate(records):
                    record_file = output_path / f"record_{i+1}_{record.patient_id}.json"
                    with open(record_file, 'w') as f:
                        json.dump(record.data, f, indent=2, default=str)
                
                # Save combined file
                combined_file = output_path / "all_records.json"
                with open(combined_file, 'w') as f:
                    json.dump([r.data for r in records], f, indent=2, default=str)
                
                console.print(f"Results saved to {output_path}")
            
            # Display statistics
            stats = orchestrator.get_extraction_statistics(records)
            display_statistics(stats)
            
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            log.error(f"CLI batch extraction error: {str(e)}")
    
    asyncio.run(run_batch_extraction())

@cli.command()
def test():
    """Test the extraction pipeline with the provided sample file."""
    
    config = get_config()
    sample_file = config.paths.data_dir / "input" / "PMID32679198.pdf"
    
    if not sample_file.exists():
        console.print(f"[red]Sample file not found: {sample_file}[/red]")
        console.print("Please ensure PMID32679198.pdf is in the data/input directory")
        return
    
    console.print(f"Testing extraction with sample file: {sample_file.name}")
    
    # Run extraction
    ctx = click.Context(extract)
    ctx.invoke(extract, 
               file_path=str(sample_file), 
               output_format='table',
               validate=True,
               ground_truth=str(config.paths.data_dir / "ground_truth" / "manually_processed.csv"))

@cli.command()
def config_info():
    """Display current configuration information."""
    config = get_config()
    
    config_table = Table(title="Configuration Information")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Environment", config.environment)
    config_table.add_row("Debug Mode", str(config.debug))
    config_table.add_row("Data Directory", str(config.paths.data_dir))
    config_table.add_row("LLM Model", config.llm.default_model)
    config_table.add_row("LLM Temperature", str(config.llm.temperature))
    config_table.add_row("Max Workers", str(config.processing.max_workers))
    config_table.add_row("Supported Formats", ", ".join(config.processing.supported_formats))
    
    console.print(config_table)

def display_records_table(records):
    """Display extracted records in a table format."""
    if not records:
        console.print("[yellow]No records to display[/yellow]")
        return
    
    table = Table(title="Extracted Patient Records")
    
    # Add columns based on first record
    first_record = records[0]
    key_fields = ["patient_id", "sex", "age_of_onset", "gene", "mutations"]
    
    for field in key_fields:
        if field in first_record.data:
            table.add_column(field.replace("_", " ").title(), style="cyan")
    
    # Add rows
    for record in records:
        row_data = []
        for field in key_fields:
            if field in record.data:
                value = record.data[field]
                if value is None:
                    row_data.append("[dim]null[/dim]")
                else:
                    row_data.append(str(value))
        table.add_row(*row_data)
    
    console.print(table)

def save_json_output(data, output_path):
    """Save data as JSON file."""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    console.print(f"[green]Results saved to {output_path}[/green]")

def save_csv_output(records, output_path):
    """Save records as CSV file."""
    import pandas as pd
    
    # Convert records to DataFrame
    data = [record.data for record in records]
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    console.print(f"[green]Results saved to {output_path}[/green]")

def validate_against_ground_truth(records, ground_truth_path):
    """Validate extracted records against ground truth."""
    try:
        import pandas as pd
        
        # Load ground truth
        gt_df = pd.read_csv(ground_truth_path)
        
        # Convert records to DataFrame
        extracted_df = pd.DataFrame([r.data for r in records])
        
        console.print(f"\n[bold]Validation Results:[/bold]")
        console.print(f"Ground truth records: {len(gt_df)}")
        console.print(f"Extracted records: {len(extracted_df)}")
        
        # Compare key fields if they exist in both
        common_fields = set(gt_df.columns) & set(extracted_df.columns)
        if common_fields:
            console.print(f"Common fields: {', '.join(common_fields)}")
            
            # Simple accuracy calculation for non-null values
            for field in common_fields:
                if field in ['patient_id']:  # Skip ID fields
                    continue
                
                gt_values = gt_df[field].dropna()
                ext_values = extracted_df[field].dropna()
                
                if len(gt_values) > 0 and len(ext_values) > 0:
                    # This is a simplified comparison - in practice, you'd want more sophisticated matching
                    console.print(f"  {field}: GT={len(gt_values)} values, Extracted={len(ext_values)} values")
        
    except Exception as e:
        console.print(f"[red]Validation error: {str(e)}[/red]")

def display_statistics(stats):
    """Display extraction statistics."""
    if not stats:
        return
    
    console.print(f"\n[bold]Extraction Statistics:[/bold]")
    
    stats_table = Table()
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Total Records", str(stats.get("total_records", 0)))
    stats_table.add_row("Unique Sources", str(stats.get("unique_sources", 0)))
    stats_table.add_row("Average Confidence", f"{stats.get('avg_confidence', 0):.2f}")
    
    console.print(stats_table)
    
    # Field extraction rates
    fields_extracted = stats.get("fields_extracted", {})
    if fields_extracted:
        console.print(f"\n[bold]Field Extraction Rates:[/bold]")
        field_table = Table()
        field_table.add_column("Field", style="cyan")
        field_table.add_column("Count", style="green")
        field_table.add_column("Percentage", style="yellow")
        
        for field, info in fields_extracted.items():
            field_table.add_row(
                field,
                str(info["count"]),
                f"{info['percentage']:.1f}%"
            )
        
        console.print(field_table)

if __name__ == "__main__":
    cli()

