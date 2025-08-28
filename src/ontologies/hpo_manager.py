"""
Unified HPO Manager for Biomedical Information Extraction

This module provides a unified HPO manager that internally uses the optimized
implementation while maintaining backward compatibility with the original API.
"""

# Import the optimized implementation
try:
    from .hpo_manager_optimized import (
        OptimizedHPOManager as _OptimizedHPOManager,
        ProcessingResult
    )
    _HPOManager = _OptimizedHPOManager
except ImportError:
    # Fallback to basic implementation if optimized is not available
    from .hpo_manager_basic import BasicHPOManager as _HPOManager
    from .hpo_manager_basic import ProcessingResult

# Alias the optimized manager as the main manager
HPOManager = _HPOManager

# Re-export ProcessingResult for backward compatibility
__all__ = ['HPOManager', 'ProcessingResult']

