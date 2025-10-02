#!/usr/bin/env python3
"""
Views Package Init
Initialization file for views package.
"""

# Lazy imports - only import when requested to avoid blocking failures
__all__ = []  # Dynamic discovery; static list removed to avoid stale exports

# Import modules on demand to prevent startup failures
def __getattr__(name):
    try:
        if name == "dashboard":
            from . import dashboard
            return dashboard
        if name == "clients":
            from . import clients
            return clients
        if name == "analytics":
            from . import analytics
            return analytics
        if name == "database":
            from . import database
            return database
        if name == "files":
            from . import files
            return files
        if name == "logs":
            from . import logs
            return logs
        if name == "settings":
            from . import settings
            return settings
        if name == "experimental":
            from . import experimental
            return experimental
    except ImportError as e:
        print(f"Warning: Could not import {name}: {e}")
        return None
    raise AttributeError(f"module 'views' has no attribute '{name}'")
