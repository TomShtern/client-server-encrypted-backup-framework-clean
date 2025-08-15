"""
CyberBackup 3.0 - Automatic UTF-8 Project Initialization

This file automatically installs the UTF-8 import hook when ANY file
in the project is imported, providing zero-configuration Unicode support.
"""


import contextlib
# Enable UTF-8 support automatically
with contextlib.suppress(ImportError):
    from Shared.utils import utf8_solution