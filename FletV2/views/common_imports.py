#!/usr/bin/env python3
"""
Common Imports Module for FletV2 Views
Eliminates import duplication across view files.

Only includes imports that appear in 3+ view files for focused, maintainable design.
Following the Flet Simplicity Principle: Don't over-engineer.
"""

# Core Flet framework

# Standard library imports (appear in 3+ view files)

# FletV2 utility imports (appear in all 7 view files)
from ..utils.debug_setup import get_logger

# Convenience logger setup
logger = get_logger(__name__)
