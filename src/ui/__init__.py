"""
UI Module for Biomedical Text Agent

This module provides a comprehensive web-based user interface for managing
the biomedical text extraction system, including dashboard, knowledge base
management, database tools, and monitoring interfaces.
"""

from .backend.app import create_app
from .backend.api import api_router
from .backend.websocket_manager import WebSocketManager

__all__ = [
    'create_app',
    'api_router', 
    'WebSocketManager'
]

