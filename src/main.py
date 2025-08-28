#!/usr/bin/env python3
"""
Main entry point for the Biomedical Text Agent

This module has been updated to use unified orchestrators that internally
use enhanced implementations while maintaining backward compatibility.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main entry point."""
    try:
        logger.info("🚀 Starting Biomedical Text Agent (Unified Version)")
        logger.info("📝 Note: This version uses unified orchestrators with enhanced implementations")
        
        # Import and initialize the unified extraction orchestrator
        try:
            from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
            from agents.orchestrator.extraction_orchestrator import ExtractionConfig
            
            # Create configuration
            config = ExtractionConfig(
                use_rag=True,
                use_feedback=True,
                use_prompt_optimization=True,
                save_to_database=True
            )
            
            # Initialize orchestrator
            orchestrator = ExtractionOrchestrator(config=config)
            
            logger.info("✅ Extraction orchestrator initialized successfully")
            
            # Display system status
            orchestrator.display_system_status()
            
        except ImportError as e:
            logger.warning(f"Could not import extraction orchestrator: {e}")
            logger.info("Continuing with basic functionality...")
        
        # Import and initialize the unified metadata orchestrator
        try:
            from metadata_triage.metadata_orchestrator import UnifiedMetadataOrchestrator
            
            # Initialize metadata orchestrator
            metadata_orchestrator = UnifiedMetadataOrchestrator(
                llm_client=None,  # Placeholder
                use_enhanced=True
            )
            
            logger.info("✅ Metadata orchestrator initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Could not import metadata orchestrator: {e}")
            logger.info("Continuing with basic functionality...")
        
        # Import and initialize the unified HPO manager
        try:
            from ontologies.hpo_manager import HPOManager
            
            # Initialize HPO manager
            hpo_manager = HPOManager()
            
            logger.info("✅ HPO manager initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Could not import HPO manager: {e}")
            logger.info("Continuing with basic functionality...")
        
        # Import and initialize the unified PubMed client
        try:
            from metadata_triage.pubmed_client import PubMedClient
            
            # Initialize PubMed client
            pubmed_client = PubMedClient()
            
            logger.info("✅ PubMed client initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Could not import PubMed client: {e}")
            logger.info("Continuing with basic functionality...")
        
        logger.info("🎯 Biomedical Text Agent is ready!")
        logger.info("💡 All components now use unified implementations with enhanced features")
        
        # Keep the agent running for a moment to show status
        await asyncio.sleep(2)
        
        logger.info("🏁 Biomedical Text Agent startup completed")
        
    except Exception as e:
        logger.error(f"❌ Failed to start Biomedical Text Agent: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Biomedical Text Agent stopped by user")
    except Exception as e:
        logger.error(f"❌ Biomedical Text Agent failed: {e}")
        sys.exit(1)

