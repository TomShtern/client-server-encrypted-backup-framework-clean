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

# Import main application components
# Import views package
# Import utils package
from . import utils, views
from .main import FletV2App, main
from .theme import (
    create_modern_button_style,
    create_modern_card_container,
    create_trend_indicator,
    get_design_tokens,
    setup_modern_theme,
    toggle_theme_mode,
)

# Define what should be imported with "from FletV2 import *"
__all__ = [
    "FletV2App",
    "create_modern_button_style",
    "create_modern_card_container",
    "create_trend_indicator",
    "get_design_tokens",
    "main",
    "setup_modern_theme",
    "toggle_theme_mode",
    "utils",
    "views"
]
