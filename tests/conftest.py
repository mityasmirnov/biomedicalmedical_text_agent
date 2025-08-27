"""
Pytest configuration for Biomedical Text Agent tests.

This file configures the test environment and provides common fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory path."""
    return Path(__file__).parent.parent / "data" / "test"

@pytest.fixture(scope="session")
def sample_pdf_path():
    """Provide path to a sample PDF for testing."""
    return Path(__file__).parent.parent / "data" / "input" / "PMID32679198.pdf"

@pytest.fixture(scope="session")
def test_db_path():
    """Provide test database path."""
    return Path(__file__).parent.parent / "data" / "test" / "test_biomedical_data.db"
