#!/usr/bin/env python3
"""
Enhanced Biomedical Text Agent Startup Script.

This script demonstrates how to start the enhanced backend API structure
alongside the original system, showing the integration and synchronization.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import enhanced components
from api.enhanced_server import create_enhanced_app, run_enhanced_server
from database.enhanced_sqlite_manager import EnhancedSQLiteManager
from metadata_triage.enhanced_metadata_orchestrator import EnhancedMetadataOrchestrator
from langextract_integration.enhanced_langextract_integration import EnhancedLangExtractIntegration

# Import original components for comparison
from api.main import create_api_router
from database.sqlite_manager import SQLiteManager
from metadata_triage.metadata_orchestrator import MetadataOrchestrator
from langextract_integration.extractor import LangExtractEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demonstrate_enhanced_system():
    """Demonstrate the enhanced system capabilities."""
    logger.info("🚀 Starting Enhanced Biomedical Text Agent System Demonstration...")
    
    try:
        # Initialize enhanced components
        logger.info("📊 Initializing Enhanced Components...")
        
        # Enhanced SQLite Manager
        enhanced_db = EnhancedSQLiteManager()
        logger.info("✅ Enhanced SQLite Manager initialized")
        
        # Enhanced Metadata Orchestrator
        enhanced_orchestrator = EnhancedMetadataOrchestrator(
            enhanced_db_manager=enhanced_db
        )
        logger.info("✅ Enhanced Metadata Orchestrator initialized")
        
        # Enhanced LangExtract Integration
        enhanced_langextract = EnhancedLangExtractIntegration(
            enhanced_db_manager=enhanced_db,
            enhanced_orchestrator=enhanced_orchestrator
        )
        logger.info("✅ Enhanced LangExtract Integration initialized")
        
        # Demonstrate enhanced features
        await demonstrate_enhanced_features(enhanced_db, enhanced_orchestrator, enhanced_langextract)
        
        # Start enhanced pipeline
        logger.info("🔄 Starting Enhanced Processing Pipeline...")
        pipeline_task = asyncio.create_task(enhanced_orchestrator.start_enhanced_pipeline())
        
        # Start enhanced extraction workers
        logger.info("🔧 Starting Enhanced Extraction Workers...")
        extraction_task = asyncio.create_task(enhanced_langextract.start_enhanced_extraction_workers())
        
        # Wait for a bit to see the system in action
        await asyncio.sleep(10)
        
        # Stop enhanced components
        logger.info("🛑 Stopping Enhanced Components...")
        pipeline_task.cancel()
        extraction_task.cancel()
        
        await enhanced_orchestrator.close()
        await enhanced_langextract.close()
        await enhanced_db.close()
        
        logger.info("✅ Enhanced system demonstration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error in enhanced system demonstration: {e}")
        raise

async def demonstrate_enhanced_features(
    enhanced_db: EnhancedSQLiteManager,
    enhanced_orchestrator: EnhancedMetadataOrchestrator,
    enhanced_langextract: EnhancedLangExtractIntegration
):
    """Demonstrate enhanced system features."""
    try:
        logger.info("🎯 Demonstrating Enhanced Features...")
        
        # 1. Enhanced Document Management
        logger.info("📄 Testing Enhanced Document Management...")
        doc_id = await enhanced_db.create_enhanced_document(
            title="Sample Biomedical Document",
            content="This document discusses diabetes treatment with insulin and its effects on blood sugar levels.",
            metadata={"source": "demo", "category": "medical"},
            tags=["diabetes", "insulin", "treatment"],
            annotations={"priority": "high", "review_required": True}
        )
        logger.info(f"✅ Created enhanced document: {doc_id}")
        
        # 2. Enhanced Extraction
        logger.info("🔍 Testing Enhanced Extraction...")
        extraction_id = await enhanced_langextract.submit_enhanced_extraction(
            document_id=doc_id,
            mode="enhanced",
            schemas=["biomedical_entities", "clinical_relationships"],
            priority="high"
        )
        logger.info(f"✅ Submitted enhanced extraction: {extraction_id}")
        
        # 3. Enhanced Task Submission
        logger.info("📋 Testing Enhanced Task Submission...")
        task_id = await enhanced_orchestrator.submit_enhanced_task(
            document_id=doc_id,
            task_type="enhanced_extraction",
            parameters={"extraction_mode": "comprehensive"},
            priority="high"
        )
        logger.info(f"✅ Submitted enhanced task: {task_id}")
        
        # 4. Enhanced Analytics
        logger.info("📊 Testing Enhanced Analytics...")
        await enhanced_db.record_metric(
            metric_name="demo_metric",
            metric_value=0.95,
            metric_data={"feature": "enhanced_demo", "success": True},
            category="demonstration"
        )
        logger.info("✅ Recorded enhanced metric")
        
        # 5. Enhanced Relationships
        logger.info("🔗 Testing Enhanced Relationships...")
        rel_id = await enhanced_db.create_relationship(
            source_id=f"{doc_id}_diabetes",
            target_id=f"{doc_id}_insulin",
            relationship_type="treated_by",
            relationship_data={"evidence": "text_analysis", "confidence": "high"},
            confidence_score=0.92,
            source_type="disease",
            target_type="medication"
        )
        logger.info(f"✅ Created enhanced relationship: {rel_id}")
        
        # 6. Enhanced Search
        logger.info("🔎 Testing Enhanced Search...")
        search_results, total_count = await enhanced_db.search_enhanced_documents(
            query="diabetes",
            filters={"category": "medical"},
            limit=10
        )
        logger.info(f"✅ Enhanced search completed: {len(search_results)} results found")
        
        # 7. Get Enhanced Statistics
        logger.info("📈 Getting Enhanced Database Statistics...")
        stats = await enhanced_db.get_database_stats()
        logger.info(f"✅ Database statistics: {stats}")
        
        # 8. Get Pipeline Status
        logger.info("🔄 Getting Enhanced Pipeline Status...")
        pipeline_status = await enhanced_orchestrator.get_pipeline_status()
        logger.info(f"✅ Pipeline status: {pipeline_status}")
        
        logger.info("🎉 All enhanced features demonstrated successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error demonstrating enhanced features: {e}")
        raise

def start_enhanced_server():
    """Start the enhanced FastAPI server."""
    try:
        logger.info("🌐 Starting Enhanced FastAPI Server...")
        
        # Create enhanced app
        app = create_enhanced_app()
        
        # Run enhanced server
        run_enhanced_server(
            host="0.0.0.0",
            port=8001,
            reload=False
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting enhanced server: {e}")
        raise

def main():
    """Main function to run the enhanced system."""
    try:
        logger.info("🚀 Biomedical Text Agent - Enhanced System")
        logger.info("=" * 50)
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "server":
                # Start enhanced server
                start_enhanced_server()
            elif sys.argv[1] == "demo":
                # Run enhanced system demonstration
                asyncio.run(demonstrate_enhanced_system())
            else:
                logger.error(f"Unknown command: {sys.argv[1]}")
                logger.info("Available commands: server, demo")
                sys.exit(1)
        else:
            # Default: run demonstration
            logger.info("No command specified, running demonstration...")
            asyncio.run(demonstrate_enhanced_system())
            
    except KeyboardInterrupt:
        logger.info("🛑 Enhanced system stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error in enhanced system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
