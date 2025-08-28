"""
Unified Extraction Orchestrator for Biomedical Data Extraction

This module provides a unified extraction orchestrator that internally uses
the enhanced implementation while maintaining backward compatibility with the original API.
"""

# Import the enhanced implementation
try:
    from .enhanced_orchestrator import (
        EnhancedExtractionOrchestrator as _EnhancedExtractionOrchestrator,
        ExtractionConfig,
        SystemStatus
    )
    _ExtractionOrchestrator = _EnhancedExtractionOrchestrator
except ImportError:
    # Fallback to basic implementation if enhanced is not available
    from .extraction_orchestrator_basic import BasicExtractionOrchestrator as _ExtractionOrchestrator
    from .extraction_orchestrator_basic import ExtractionConfig, SystemStatus

# Alias the enhanced orchestrator as the main orchestrator
ExtractionOrchestrator = _ExtractionOrchestrator

# Re-export configuration classes for backward compatibility
__all__ = ['ExtractionOrchestrator', 'ExtractionConfig', 'SystemStatus']