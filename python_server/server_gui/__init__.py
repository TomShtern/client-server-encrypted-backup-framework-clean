# -*- coding: utf-8 -*-
"""
server_gui - A modern, modular GUI package for the Encrypted Backup Server.
this init path is :C:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework\python_server\server_gui\__init__.py
This package provides the main application shell and all related UI components
for monitoring and managing the backup server.

The primary public component is the `ServerGUI` class, which can be
imported directly from this package:

    from server_gui import ServerGUI

    gui = ServerGUI(server_instance)
    gui.run()
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any, Dict, List, Union
import threading
import time
from datetime import datetime

# --- Critical: Ensure UTF-8 Support ---
# This import is crucial for consistent encoding across the application,
# especially when handling file paths, logs, and international characters.
# Import UTF-8 support for international characters and emojis
try:
    import Shared.utils.utf8_solution  # 🚀 UTF-8 support enabled automatically
except ImportError:
    try:
        import sys
        import os
          # Add the project root to the path to find the 'Shared' module
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        import Shared.utils.utf8_solution  # 🚀 UTF-8 support enabled automatically
    except ImportError:
        print("[WARNING] Could not enable the project-wide UTF-8 solution.")
        
# --- Public API ---
# We only expose the main ServerGUI class from the top level of the package.
# All other components (pages, widgets) are considered internal implementation details.
from .ServerGUI import ServerGUI

# The __all__ list defines the public API of the package.
__all__ = [
    "ServerGUI",
]