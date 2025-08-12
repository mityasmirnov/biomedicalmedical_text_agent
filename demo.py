#!/usr/bin/env python3
"""
Demonstration script for the Biomedical Data Extraction Engine.
This script shows the complete workflow from document processing to data extraction.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config import get_config
from core.logging_config import setup_logging
from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
from core.llm_client.openrouter_client import OpenRouterClient
from database.sqlite_manager import SQLiteManager
from ontologies.hpo_manager import HPOManager
from ontologies.gene_manager import GeneManager

def main():
    """Run the complete demonstration."""
    print("🚀 Biomedical Data Extraction Engine - Complete Demo")
    print("=" * 60)
    
    # Setup logging
    setup_logging({"log_level": "INFO"})
    
    # Get configuration
    config = get_config()
    print(f"📋 Configuration loaded: {config.llm.default_model}")
    
    async def run_demo():
        try:
            print("\n🔧 Step 1: Initializing Components...")
            
            # Initialize LLM client
            llm_client = OpenRouterClient()
            print("✅ LLM Client initialized")
            
            # Initialize orchestrator
            orchestrator = ExtractionOrchestrator(llm_client=llm_client)
            print("✅ Extraction Orchestrator initialized")
            
            # Initialize database manager
            db_manager = SQLiteManager()
            print("✅ Database Manager initialized")
            
            # Initialize ontology managers
            hpo_manager = HPOManager()
            gene_manager = GeneManager()
            print("✅ Ontology Managers initialized")
            
            print("\n📄 Step 2: Processing Sample Document...")
            
            # Process the sample PDF
            sample_file = "data/input/PMID32679198.pdf"
            if not Path(sample_file).exists():
                print(f"❌ Sample file not found: {sample_file}")
                return
            
            print(f"📖 Processing: {Path(sample_file).name}")
            result = await orchestrator.extract_from_file(sample_file)
            
            if not result.success:
                print(f"❌ Extraction failed: {result.error}")
                return
            
            records = result.data
            print(f"✅ Successfully extracted {len(records)} patient records")
            
            # Show sample records
            print("\n📊 Sample Extracted Records:")
            for i, record in enumerate(records[:3]):  # Show first 3
                print(f"  Record {i+1}: {record.patient_id}")
                if hasattr(record, 'data') and record.data:
                    for key, value in list(record.data.items())[:3]:  # Show first 3 fields
                        print(f"    {key}: {value}")
                print()
            
            print("\n🗄️ Step 3: Storing in Database...")
            
            # Store records in database
            store_result = db_manager.store_patient_records(records)
            if store_result.success:
                print(f"✅ Stored {len(records)} records in database")
                
                # Retrieve records
                retrieve_result = db_manager.get_patient_records(limit=5)
                if retrieve_result.success:
                    print(f"✅ Retrieved {len(retrieve_result.data)} records from database")
            else:
                print(f"❌ Database storage failed: {store_result.error}")
            
            print("\n🧬 Step 4: Ontology Normalization...")
            
            # Test phenotype normalization
            test_phenotypes = ["seizures", "developmental delay", "muscle weakness"]
            hpo_result = hpo_manager.batch_normalize_phenotypes(test_phenotypes)
            
            if hpo_result.success:
                print(f"✅ HPO normalization: {len(hpo_result.data)} phenotypes processed")
                for norm in hpo_result.data[:2]:  # Show first 2
                    if norm.get('best_match'):
                        match = norm['best_match']
                        print(f"  {norm['original_text']} → {match['hpo_id']}: {match['hpo_name']}")
            
            # Test gene normalization
            test_genes = ["SURF1", "surf1", "NDUFS1"]
            gene_result = gene_manager.batch_normalize_genes(test_genes)
            
            if gene_result.success:
                print(f"✅ Gene normalization: {len(gene_result.data)} genes processed")
                for norm in gene_result.data[:2]:  # Show first 2
                    print(f"  {norm['original_symbol']} → {norm['normalized_symbol']}")
            
            print("\n📈 Step 5: System Statistics...")
            
            # Get extraction statistics
            stats = orchestrator.get_extraction_statistics(records)
            print(f"📊 Total records: {stats.get('total_records', 0)}")
            print(f"👥 Unique patients: {stats.get('unique_patients', 0)}")
            print(f"📚 Unique sources: {stats.get('unique_sources', 0)}")
            
            # Field coverage
            field_coverage = stats.get('field_coverage', {})
            if field_coverage:
                print(f"📋 Fields with data: {len(field_coverage)}")
                for field, count in list(field_coverage.items())[:5]:  # Show top 5
                    print(f"  {field}: {count} records")
            
            print("\n🎉 Demo completed successfully!")
            print("\n💡 Next steps:")
            print("  • Use 'python src/main.py extract <file>' to extract from your documents")
            print("  • Use 'python src/main.py batch <directory>' for batch processing")
            print("  • Check the database for stored records")
            print("  • Explore the extracted data structure")
            
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Run the demo
    asyncio.run(run_demo())

if __name__ == "__main__":
    main()
