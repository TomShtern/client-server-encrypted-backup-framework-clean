#!/usr/bin/env python3
"""
FletV2 Package Init
Main package init file for FletV2.
"""

import os
import sys

# Add the package directory to the Python path if needed
package_dir = os.path.dirname(__file__)
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

# Import utility and view packages (but NOT main to avoid circular imports)
# main.py imports FletV2.components which triggers this __init__.py
# If we import main here, it creates a circular import that breaks direct script execution
from . import utils, views  # noqa: E402
from .theme import (  # noqa: E402
    create_modern_card,
    get_design_tokens,
    setup_sophisticated_theme,
    themed_button,
    toggle_theme_mode,
)


def get_app_class():
    """Lazy import of FletV2App to avoid circular imports."""
    from .main import FletV2App

    return FletV2App


# Define what should be imported with "from FletV2 import *"
__all__ = [
    "get_app_class",
    "create_modern_card",
    "get_design_tokens",
    "setup_sophisticated_theme",
    "themed_button",
    "toggle_theme_mode",
    "utils",
    "views",
]
