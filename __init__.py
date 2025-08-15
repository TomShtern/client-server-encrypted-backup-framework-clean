"""
CyberBackup 3.0 - Automatic UTF-8 Project Initialization

This file automatically installs the UTF-8 import hook when ANY file
in the project is imported, providing zero-configuration Unicode support.
"""

# Enable UTF-8 support automatically
try:
    import utf8_solution
    # UTF-8 support activates automatically on import
except ImportError:
    # Fallback if import fails
    pass