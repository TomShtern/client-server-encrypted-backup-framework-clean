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
from .main import FletV2App, main
from .theme import (
    setup_default_theme, 
    toggle_theme_mode, 
    apply_theme_variant,
    get_available_themes,
    get_current_theme_colors,
    setup_modern_theme,
    get_shadow_style,
    get_brand_color,
    create_modern_button_style,
    create_gradient_container
)

# Import views package
from . import views

# Import utils package
from . import utils

# Define what should be imported with "from FletV2 import *"
__all__ = [
    "FletV2App",
    "main",
    "setup_default_theme",
    "toggle_theme_mode", 
    "apply_theme_variant",
    "get_available_themes",
    "get_current_theme_colors",
    "setup_modern_theme",
    "get_shadow_style",
    "get_brand_color",
    "create_modern_button_style",
    "create_gradient_container",
    "views",
    "utils"
]