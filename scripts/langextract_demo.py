#!/usr/bin/env python3
"""
LangExtract Integration Demo

This script demonstrates the integration of LangExtract for biomedical text extraction.
It can be run directly or converted to a Jupyter notebook.
"""

import os
import sys
import json
import pandas as pd
import plotly.express as px
from IPython.display import display, Markdown
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import LangExtract integration
from langextract_integration import (
    LangExtractEngine,
    BiomedicExtractionClasses,
    BiomedicNormalizer,
    extract_from_text
)

def setup_environment():
    """Set up the environment and configuration."""
    # Load environment variables
    load_dotenv()
    
    # Configuration
    config = {
        'model_id': os.getenv("LANGEXTRACT_MODEL_ID", "gpt-4o-mini"),
        'use_local_model': os.getenv("USE_LOCAL_MODEL", "false").lower() in ("1", "true", "yes"),
        'local_model_id': os.getenv("LOCAL_MODEL_ID", "llama3"),
        'local_model_url': os.getenv("LOCAL_MODEL_URL", "http://localhost:11434"),
        'openrouter_api_key': os.getenv("OPENROUTER_API_KEY")
    }
    
    # Set up OpenRouter if not using local model
    if not config['use_local_model']:
        if not config['openrouter_api_key']:
            raise ValueError("OPENROUTER_API_KEY is not set in environment variables")
        
        os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
        os.environ["OPENAI_API_KEY"] = config['openrouter_api_key']
        os.environ["OPENROUTER_API_KEY"] = config['openrouter_api_key']
        print(f"✅ Using OpenRouter with model: {config['model_id']}")
    else:
        print(f"✅ Using local model: {config['local_model_id']} at {config['local_model_url']}")
    
    return config

def initialize_extraction():
    """Initialize the extraction components."""
    print("🚀 Initializing extraction components...")
    extraction_classes = BiomedicExtractionClasses()
    normalizer = BiomedicNormalizer()
    
    print("📋 Available extraction classes:")
    for cls_name in extraction_classes.classes:
        print(f"  - {cls_name}")
    
    return extraction_classes, normalizer

def run_extraction(text, extraction_classes, normalizer, config):
    """Run the extraction pipeline on the provided text."""
    print("\n🔍 Running extraction...")
    
    # Initialize the engine
    engine = LangExtractEngine(
        extraction_classes=extraction_classes,
        model_name=config['model_id'],
        use_local_model=config['use_local_model'],
        local_model_id=config['local_model_id'],
        local_model_url=config['local_model_url']
    )
    
    # Run extraction
    extractions = engine.extract(text)
    
    # Normalize the results
    normalized = normalizer.normalize(extractions)
    
    return extractions, normalized

def display_results(extractions, normalized):
    """Display the extraction results."""
    print("\n📊 Extraction Results:")
    print(json.dumps(extractions, indent=2))
    
    print("\n📋 Normalized Results:")
    if isinstance(normalized, pd.DataFrame):
        display(normalized)
    else:
        print(json.dumps(normalized, indent=2))

def main():
    """Main function to run the demo."""
    # Setup
    try:
        config = setup_environment()
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return
    
    # Initialize components
    extraction_classes, normalizer = initialize_extraction()
    
    # Sample text for extraction
    sample_text = """
    Patient 1 was a 3-year-old male with Leigh syndrome due to MT-ATP6 c.8993T>G (p.Leu156Arg).
    He presented with developmental delay and lactic acidosis at 6 months of age. Treatment included
    riboflavin 100 mg/day and coenzyme Q10 with clinical improvement. He is alive at last follow-up.
    """
    
    # Run extraction
    try:
        extractions, normalized = run_extraction(
            sample_text, 
            extraction_classes, 
            normalizer, 
            config
        )
        display_results(extractions, normalized)
    except Exception as e:
        print(f"❌ Error during extraction: {e}")

if __name__ == "__main__":
    main()
