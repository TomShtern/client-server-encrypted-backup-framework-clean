#!/usr/bin/env python3
"""
Views Package Init
Initialization file for views package.
"""

# Lazy imports - only import when requested to avoid blocking failures
__all__ = [
    "analytics",
    "clients",
    "dashboard",
    "database",
    "files",
    "logs",
    "settings"
]

# Import modules on demand to prevent startup failures
def __getattr__(name):
    if name in __all__:
        try:
            if name == "dashboard":
                from . import dashboard
                return dashboard
            elif name == "clients":
                from . import clients
                return clients
            elif name == "analytics":
                from . import analytics
                return analytics
            elif name == "database":
                from . import database
                return database
            elif name == "files":
                from . import files
                return files
            elif name == "logs":
                from . import logs
                return logs
            elif name == "settings":
                from . import settings
                return settings
        except ImportError as e:
            print(f"Warning: Could not import {name}: {e}")
            return None
    raise AttributeError(f"module 'views' has no attribute '{name}'")
