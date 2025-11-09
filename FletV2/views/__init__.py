#!/usr/bin/env python3
"""
Views Package Init
Initialization file for views package.
"""

# Lazy imports - only import when requested to avoid blocking failures
__all__ = []  # Dynamic discovery; static list removed to avoid stale exports


# Import modules on demand to prevent startup failures
def __getattr__(name):
    import importlib

    try:
        # Use importlib to dynamically load submodules without recursion
        module_path = f"views.{name}"
        module = importlib.import_module(module_path)
        # Cache the imported module in globals to avoid re-importing
        globals()[name] = module
        return module
    except ImportError as e:
        print(f"Warning: Could not import {name}: {e}")
        return None
    except Exception as e:
        raise AttributeError(f"module 'views' has no attribute '{name}': {e}") from e
