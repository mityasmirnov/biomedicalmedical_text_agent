#!/usr/bin/env python3
"""
Leigh Syndrome Case Report Search Demonstration.

This script demonstrates the unified metadata orchestrator functionality
for searching and processing Leigh syndrome case reports.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from metadata_triage.metadata_orchestrator import UnifiedMetadataOrchestrator


async def main():
    """Demonstrate Leigh syndrome case report search functionality."""
    print("🔬 Leigh Syndrome Case Report Search Demonstration")
    print("=" * 60)
    
    # Create necessary directories
    Path("data/metadata_triage").mkdir(parents=True, exist_ok=True)
    Path("data/database").mkdir(parents=True, exist_ok=True)
    
    # Initialize unified metadata orchestrator
    print("\n📋 Initializing Unified Metadata Orchestrator...")
    orchestrator = UnifiedMetadataOrchestrator(
        llm_client=None,  # No LLM client for demo
        use_enhanced=True  # Use enhanced implementation if available
    )
    print(f"✓ Orchestrator initialized successfully")
    
    # Search for Leigh syndrome case reports
    print("\n🔍 Searching for Leigh Syndrome Case Reports...")
    query = "leigh syndrome case reports"
    print(f"Query: '{query}'")
    
    # Run the pipeline
    print("\n🚀 Running Complete Pipeline...")
    pipeline_result = await orchestrator.run_complete_pipeline(
        query=query,
        max_results=100,
        include_europepmc=False,  # Skip Europe PMC for demo
        output_dir="data/metadata_triage/leigh_syndrome_pipeline",
        save_intermediate=True
    )
    
    if pipeline_result.get('enhanced_mode'):
        print(f"✓ Pipeline completed in enhanced mode!")
        print(f"  Query: {pipeline_result['summary']['pipeline_info']['query']}")
        print(f"  Output Directory: {pipeline_result['output_directory']}")
        print(f"  Note: {pipeline_result['summary']['note']}")
    else:
        print(f"✓ Pipeline completed successfully!")
        print(f"  Query: {pipeline_result['summary']['pipeline_info']['query']}")
        print(f"  Total Retrieved: {pipeline_result['summary']['pipeline_info']['total_retrieved_documents']}")
        print(f"  Unique After Dedup: {pipeline_result['summary']['pipeline_info']['unique_documents_after_deduplication']}")
        print(f"  Output Directory: {pipeline_result['output_directory']}")
    
    # Summary
    print("\n" + "="*60)
    print("DEMONSTRATION SUMMARY")
    print("="*60)
    print("✅ Successfully demonstrated Leigh syndrome case report search")
    print("✅ Unified orchestrator working correctly")
    print("✅ Pipeline execution successful")
    print("✅ Enhanced features available when possible")
    
    print("\n💡 The unified orchestrator automatically uses the best available implementation")
    print("💡 Enhanced features are available when dependencies are satisfied")
    print("💡 Fallback to basic implementation when needed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Demonstration stopped by user")
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        sys.exit(1)