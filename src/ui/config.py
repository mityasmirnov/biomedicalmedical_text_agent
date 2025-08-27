"""
UI Configuration for Biomedical Text Agent

Simplified configuration for the React frontend, now that backend is unified.
"""

import os
from pathlib import Path

# Base configuration
BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"
BUILD_DIR = FRONTEND_DIR / "build"

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Frontend configuration
FRONTEND_BUILD_PATH = BUILD_DIR
FRONTEND_STATIC_PATH = BUILD_DIR / "static" if BUILD_DIR.exists() else None

# Development configuration
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
RELOAD = os.getenv("RELOAD", "false").lower() == "true"

# CORS configuration
CORS_ORIGINS = [
    "http://127.0.0.1:3000",  # React dev server
    "http://127.0.0.1:8000",  # Production
    "http://localhost:3000",
    "http://localhost:8000",
]

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Database configuration (inherited from main system)
DATABASE_PATH = Path("data/database/biomedical_data.db")
VECTOR_DB_PATH = Path("data/vector_indices")

# Feature flags
FEATURES = {
    "authentication": False,  # Disabled for now
    "websockets": False,      # Disabled for now
    "file_upload": True,
    "real_time_updates": False,
    "advanced_search": True,
    "export_functionality": True,
}

def get_api_endpoint(endpoint: str) -> str:
    """Get full API endpoint URL."""
    return f"{API_BASE_URL}{API_PREFIX}{endpoint}"

def is_frontend_built() -> bool:
    """Check if frontend is built."""
    return BUILD_DIR.exists() and (BUILD_DIR / "index.html").exists()

def get_frontend_config() -> dict:
    """Get frontend configuration for React app."""
    return {
        "apiBaseUrl": API_BASE_URL,
        "apiVersion": API_VERSION,
        "debug": DEBUG,
        "features": FEATURES,
    }
