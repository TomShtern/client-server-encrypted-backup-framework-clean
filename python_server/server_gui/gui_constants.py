# -*- coding: utf-8 -*-
"""
gui_constants.py - A single source of truth for UI constants.

This module centralizes the import of constants from the UI toolkit.
It attempts to import from ttkbootstrap, falling back to the standard
tkinter.constants if ttkbootstrap is not available.

This prevents code duplication and ensures that all other modules
have a consistent and unambiguous way to access UI constants.
"""

# This flag can be used by other modules to conditionally import
# or use features specific to ttkbootstrap.
TTK_IS_AVAILABLE = False

try:
    from ttkbootstrap import constants
    TTK_IS_AVAILABLE = True
except ImportError:
    from tkinter import constants

# --- Re-export all commonly used constants ---
# By explicitly defining them here, we create a clear public API
# for this module and decouple other modules from the specific
# source of the constants.

# Sizing and Packing
HORIZONTAL = constants.HORIZONTAL
VERTICAL = constants.VERTICAL
SOLID = constants.SOLID
LEFT = constants.LEFT
RIGHT = constants.RIGHT
TOP = constants.TOP
BOTTOM = constants.BOTTOM
X = constants.X
Y = constants.Y
BOTH = constants.BOTH
END = constants.END
NORMAL = constants.NORMAL
DISABLED = constants.DISABLED
CENTER = constants.CENTER

# Grid sticky options
NSEW = constants.NSEW
EW = constants.EW
NS = constants.NS
W = constants.W

# Other
SEL_FIRST = constants.SEL_FIRST
SEL_LAST = constants.SEL_LAST