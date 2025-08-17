"""
Python Server GUI Package

This package provides modern GUI components for the backup server including:
- ServerGUI: Main server GUI application  
- Modern UI components with consistent theming
- Real-time status monitoring and progress tracking
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any, Dict, List, Union
import threading
import time
from datetime import datetime

# Import UTF-8 support for international characters and emojis
try:
    import Shared.utils.utf8_solution  # 🚀 UTF-8 support enabled automatically
except ImportError:
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        import Shared.utils.utf8_solution  # 🚀 UTF-8 support enabled automatically
    except ImportError:
        pass  # Continue without UTF-8 support if not available

# Import components from ServerGUI module including the main ServerGUI class
from .ServerGUI import (
    ServerGUI,  # ← REAL ServerGUI class imported here
    ModernTheme,
    ModernCard,
    ModernProgressBar,
    ModernStatusIndicator,
    ToastNotification,
    ModernTable,
    CHARTS_AVAILABLE, 
    SYSTEM_MONITOR_AVAILABLE, 
    TRAY_AVAILABLE,
    CALENDAR_AVAILABLE,
    DND_AVAILABLE,
    SERVER_CONTROL_AVAILABLE,
    PROCESS_MONITOR_AVAILABLE,
    BackupServerLike
)

# Export all components
__all__ = [
    "ServerGUI",
    "ModernTheme", 
    "ModernCard",
    "ModernProgressBar", 
    "ModernStatusIndicator",
    "ToastNotification",
    "ModernTable",
    "CHARTS_AVAILABLE",
    "SYSTEM_MONITOR_AVAILABLE", 
    "TRAY_AVAILABLE",
    "CALENDAR_AVAILABLE",
    "DND_AVAILABLE",
    "SERVER_CONTROL_AVAILABLE",
    "PROCESS_MONITOR_AVAILABLE",
    "BackupServerLike"
]
