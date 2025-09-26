"""
utils - A package for GUI-specific helper modules and utility classes.

This package contains helper modules that encapsulate complex logic or provide
reusable components that are not themselves full pages, such as the ModernSheet
wrapper for the tksheet library.
"""

from .tksheet_utils import ModernSheet

__all__ = ["ModernSheet"]
