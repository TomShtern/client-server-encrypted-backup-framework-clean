"""
Python Server GUI Package

This package provides modern GUI components for the backup server including:
- EnhancedServerGUI: Main server GUI application  
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

# Import components from ServerGUI module including the main EnhancedServerGUI class
from .ServerGUI import (
    EnhancedServerGUI,  # ← REAL EnhancedServerGUI class imported here
    AppSettings,
    FramelessWindow,
    BasePage,
    StatCard,
    DashboardPage,
    ClientsPage,
    AnalyticsPage,
    SettingsPage,
    CHARTS_AVAILABLE, 
    SYSTEM_MONITOR_AVAILABLE, 
    TRAY_AVAILABLE,
    CALENDAR_AVAILABLE,
    PROCESS_MONITOR_AVAILABLE,
    launch_standalone
)

# Export all components
__all__ = [
    "EnhancedServerGUI",
    "AppSettings", 
    "FramelessWindow",
    "BasePage", 
    "StatCard",
    "DashboardPage",
    "ClientsPage",
    "AnalyticsPage",
    "SettingsPage",
    "CHARTS_AVAILABLE",
    "SYSTEM_MONITOR_AVAILABLE", 
    "TRAY_AVAILABLE",
    "CALENDAR_AVAILABLE",
    "PROCESS_MONITOR_AVAILABLE",
    "launch_standalone"
]
