# -*- coding: utf-8 -*-
# ServerGUI.py - ULTRA MODERN Cross-platform GUI for Encrypted Backup Server
# Enhanced version with real functionality and advanced features

import sys
import os
import threading
import logging
import traceback
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Deque, Callable, TYPE_CHECKING, Protocol, runtime_checkable, Type
from functools import partial

# UTF-8 support for international characters and emojis
try:
    import Shared.utils.utf8_solution  # 🚀 UTF-8 support enabled automatically
except ImportError:
    # Fallback for when running from within python_server directory
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    import Shared.utils.utf8_solution  # 🚀 UTF-8 support enabled automatically

# Type-safe reconfigure for stdout/stderr
if hasattr(sys.stdin, 'reconfigure') and callable(getattr(sys.stdin, 'reconfigure', None)):
    sys.stdin.reconfigure(encoding="utf-8")
if hasattr(sys.stdout, 'reconfigure') and callable(getattr(sys.stdout, 'reconfigure', None)):
    sys.stdout.reconfigure(encoding="utf-8")

if TYPE_CHECKING:
    from Shared.utils.process_monitor_gui import ProcessMonitorWidget
    from python_server.server.server import BackupServer

# Lightweight structural type to satisfy static type checkers for the server used by the GUI
@runtime_checkable
class BackupServerLike(Protocol):
    running: bool
    db_manager: Any
    clients: Dict[bytes, Any]
    clients_by_name: Dict[str, bytes]
    network_server: Any

    def start(self) -> None: ...
    def stop(self) -> None: ...
    def apply_settings(self, settings: Dict[str, Any]) -> None: ...

# GUI Imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Calendar for date range selection
try:
    from tkcalendar import DateEntry as CalDateEntry
    CALENDAR_AVAILABLE = True
    print("[OK] Date entry for analytics available (tkcalendar installed)")
except ImportError:
    CALENDAR_AVAILABLE = False
    CalDateEntry = None
    print("[WARNING] tkcalendar not available. To enable date range selection: pip install tkcalendar")

DateEntry = Optional[Type[CalDateEntry]]
if CalDateEntry:
    DateEntry = CalDateEntry

# Drag and Drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD as DNDTk
    DND_AVAILABLE = True
    print("[OK] Drag-and-drop functionality available (tkinterdnd2 installed)")
except ImportError:
    DND_AVAILABLE = False
    DNDTk = None
    print("[WARNING] tkinterdnd2 not available. To enable drag-and-drop: pip install tkinterdnd2")

TkinterDnD = Optional[Type[DNDTk]]
if DNDTk:
    TkinterDnD = DNDTk

# Import server components for real server control
try:
    from python_server.server.server import BackupServer
    SERVER_CONTROL_AVAILABLE = True
except ImportError:
    BackupServer = None # type: ignore
    SERVER_CONTROL_AVAILABLE = False
    print("Warning: Server control not available - server start/stop disabled")

# Import singleton manager
try:
    from python_server.server.server_singleton import ensure_single_server_instance
except ImportError:
    # Fallback for when running from within python_server directory
    try:
        from server.server_singleton import ensure_single_server_instance
    except ImportError:
        # Another fallback for direct execution
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from server.server_singleton import ensure_single_server_instance

# Import system tray functionality based on platform
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
    print("[OK] System tray functionality available (pystray and PIL installed)")
except ImportError:
    TRAY_AVAILABLE = False
    pystray = None # type: ignore
    Image = None # type: ignore
    ImageDraw = None # type: ignore
    print("[INFO] System tray will be disabled. To enable: pip install pystray pillow")

# Import advanced features
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as MatplotlibCanvas
    from matplotlib.figure import Figure as MatplotlibFigure
    if plt:
        plt.style.use('dark_background')
    CHARTS_AVAILABLE = True
    print("[OK] Advanced charts available (matplotlib installed)")
except ImportError as e:
    CHARTS_AVAILABLE = False
    plt = None # type: ignore
    MatplotlibCanvas = None # type: ignore
    MatplotlibFigure = None # type: ignore
    print(f"[WARNING] matplotlib not available: {e}")
    print("[INFO] To enable advanced charts: pip install matplotlib")

FigureCanvasTkAgg = Optional[Type[MatplotlibCanvas]]
if MatplotlibCanvas:
    FigureCanvasTkAgg = MatplotlibCanvas
Figure = Optional[Type[MatplotlibFigure]]
if MatplotlibFigure:
    Figure = MatplotlibFigure


try:
    import psutil
    SYSTEM_MONITOR_AVAILABLE = True
except ImportError:
    psutil = None # type: ignore
    SYSTEM_MONITOR_AVAILABLE = False
    print("Warning: psutil not available - real system monitoring disabled, using simulated data")

# Import enhanced process monitoring
try:
    from Shared.utils.process_monitor_gui import ProcessMonitorWidget as PMWidget
    PROCESS_MONITOR_AVAILABLE = True
    print("[OK] Enhanced process monitoring available")
except ImportError as e:
    PROCESS_MONITOR_AVAILABLE = False
    PMWidget = None # type: ignore
    print(f"[WARNING] Enhanced process monitoring not available: {e}")

ProcessMonitorWidget = Optional[Type[PMWidget]]
if PMWidget:
    ProcessMonitorWidget = PMWidget

# SENTRY - Initialize error tracking
try:
    import sentry_sdk
    sentry_sdk.init(
        dsn="https://094a0bee5d42a7f7e8ec8a78a37c8819@o4509746411470848.ingest.us.sentry.io/4509747877773312",
        send_default_pii=True,
    )
    print("[OK] Sentry error tracking initialized")
except ImportError:
    print("[WARNING] Sentry not available - error tracking disabled")
except Exception as e:
    print(f"[WARNING] Sentry initialization failed: {e}")

# --- UI CONSTANTS & ICONS ---
class ModernTheme:
    PRIMARY_BG = "#0D1117"
    SECONDARY_BG = "#161B22"
    CARD_BG = "#21262D"
    ACCENT_BG = "#30363D"
    TEXT_PRIMARY = "#F0F6FC"
    TEXT_SECONDARY = "#8B949E"
    SUCCESS = "#238636"
    WARNING = "#D29922"
    ERROR = "#DA3633"
    INFO = "#1F6FEB"
    ACCENT_BLUE = "#58A6FF"
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_MEDIUM = 12
    FONT_SIZE_SMALL = 10

class IconProvider:
    # Simple text-based icons instead of base64 encoded images
    _icons: Dict[str, str] = {
        "dashboard": "🏠",
        "clients": "👥",
        "files": "📁",
        "analytics": "📊",
        "settings": "⚙️",
        "logs": "📝",
        "process": "⚡",
        "database": "🗄️",
        "network": "🌐",
        "security": "🔒",
        "maintenance": "🛠️",
        "help": "❓",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }

    @classmethod
    def get_icon(cls, name: str, size: int = 16) -> Optional[str]:
        """Get a text-based icon by name."""
        return cls._icons.get(name, "🔹")  # Default icon

    @classmethod
    def get_icon_text(cls, name: str) -> str:
        """Get the text representation of an icon."""
        return cls._icons.get(name, "🔹")

# [Rest of the file would continue here...]