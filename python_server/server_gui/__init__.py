# -*- coding: utf-8 -*-
"""
server_gui - A modern, modular GUI package for the Encrypted Backup Server.

This package provides the main application shell and all related UI components
for monitoring and managing the backup server.

The primary public component is the `ServerGUI` class, which can be
imported directly from this package after ensuring the project root is in the
Python path:

    from python_server.server.server_gui import ServerGUI

    gui = ServerGUI(server_instance)
    gui.run()
"""

# --- Critical: Ensure Cross-Package Import Compatibility ---
# This logic is non-negotiable for a robust, multi-package project structure.
# It ensures that modules inside this package can reliably import from sibling
# packages like 'Shared'.
try:
    # First, try a direct import. This works if the project root is in PYTHONPATH.
    import Shared.utils.utf8_solution
except ImportError:
    try:
        import sys
        import os
        # If direct import fails, dynamically add the project root to the path.
        # server_gui -> server -> python_server -> Client_Server_Encrypted_Backup_Framework
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        import Shared.utils.utf8_solution
        print(f"[OK]   Project root dynamically added to path for cross-package imports.")
    except ImportError:
        print("[WARNING] Could not enable the project-wide UTF-8 solution. Cross-package imports may fail.")


# --- Public API Definition ---
# We only expose the main ServerGUI class from the top level of the package.
# All other components (pages, widgets) are considered internal implementation details,
# promoting strong encapsulation.
from .ServerGUI import ServerGUI

# The __all__ list formally declares the public API of the package.
__all__ = [
    "ServerGUI",
]