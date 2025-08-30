"""
Components Module

Provides base classes and utilities for action handlers and UI components.
Includes the centralized error boundary system for robust error handling.
"""

from .base_action_handler import BaseActionHandler, UIActionMixin
from .error_boundary import ErrorBoundary, GlobalErrorBoundary, safe_callback, protect
from .error_dialog import ErrorDialog, show_error_dialog, show_simple_error

__all__ = [
    'BaseActionHandler',
    'UIActionMixin',
    'ErrorBoundary',
    'GlobalErrorBoundary', 
    'safe_callback',
    'protect',
    'ErrorDialog',
    'show_error_dialog',
    'show_simple_error'
]
