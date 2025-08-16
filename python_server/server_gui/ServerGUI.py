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
from typing import Dict, List, Optional, Any, Union, Deque, Callable, TYPE_CHECKING, Protocol, runtime_checkable, cast
from contextlib import suppress
import time
import queue
import json
import csv
import shutil

# UTF-8 support for international characters and emojis
try:
    import Shared.utils.utf8_solution  # 🚀 UTF-8 support enabled automatically
    # Keep a reference to avoid 'imported but unused' linters; module is imported for side-effects
    _utf8_solution = Shared.utils.utf8_solution
except ImportError:
    # Fallback for when running from within python_server directory
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    import Shared.utils.utf8_solution  # 🚀 UTF-8 support enabled automatically
    _utf8_solution = Shared.utils.utf8_solution

# Type-safe reconfigure for stdout/stderr (guarded for analyzers)
def _safe_reconfigure_stream(stream: Any) -> None:
    """Call reconfigure on a stream if available (safe for static analysis)."""
    reconfig = getattr(stream, 'reconfigure', None)
    if callable(reconfig):
        with suppress(Exception):
            reconfig(encoding='utf-8')


# Try to reconfigure std streams to UTF-8 where available
_safe_reconfigure_stream(sys.stdin)
_safe_reconfigure_stream(sys.stdout)

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
    from tkcalendar import DateEntry as CalDateEntry  # type: ignore
    CALENDAR_AVAILABLE = True
    print("[OK] Date entry for analytics available (tkcalendar installed)")
    DateEntry = CalDateEntry
except Exception:
    CALENDAR_AVAILABLE = False
    CalDateEntry = None  # type: ignore
    DateEntry = None
    print("[WARNING] tkcalendar not available. To enable date range selection: pip install tkcalendar")

# Drag and Drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD as DNDTk  # type: ignore
    DND_AVAILABLE = True
    TkinterDnD = DNDTk
    print("[OK] Drag-and-drop functionality available (tkinterdnd2 installed)")
except Exception:
    DND_AVAILABLE = False
    DNDTk = None  # type: ignore
    TkinterDnD = None
    # Provide fallbacks so static analyzers know the names exist at runtime
    DND_FILES = 'DND_FILES'
    print("[WARNING] tkinterdnd2 not available. To enable drag-and-drop: pip install tkinterdnd2")


# Import server components for real server control (TYPE_CHECKING-aware)
if TYPE_CHECKING:
    from python_server.server.server import BackupServer  # type: ignore

try:
    from python_server.server.server import BackupServer
    SERVER_CONTROL_AVAILABLE = True
except Exception:
    BackupServer = None  # type: ignore
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
    FigureCanvasTkAgg = MatplotlibCanvas
    Figure = MatplotlibFigure
    print("[OK] Advanced charts available (matplotlib installed)")
except ImportError as e:
    CHARTS_AVAILABLE = False
    plt = None # type: ignore
    MatplotlibCanvas = None # type: ignore
    MatplotlibFigure = None # type: ignore
    FigureCanvasTkAgg = None
    Figure = None
    print(f"[WARNING] matplotlib not available: {e}")
    print("[INFO] To enable advanced charts: pip install matplotlib")

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
    ProcessMonitorWidget = PMWidget
    print("[OK] Enhanced process monitoring available")
except Exception as e:
    PROCESS_MONITOR_AVAILABLE = False
    PMWidget = None  # type: ignore
    ProcessMonitorWidget = None
    print(f"[WARNING] Enhanced process monitoring not available: {e}")

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
    ACCENT_PURPLE = "#7C4DFF"
    ACCENT_GREEN = "#2DD4BF"
    ACCENT_ORANGE = "#FF8A00"
    # Spacing / animation constants used by widgets
    PADDING_MEDIUM = 12
    ANIMATION_SPEED = 30
    PROGRESS_ANIMATION_SPEED = 30
    # Glass morphism colors
    GLASS_BG = "#1B2430"
    GLASS_BORDER = "#2A3646"
    GLASS_HIGHLIGHT = "#233044"
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

# --- MODERN CUSTOM WIDGETS ---
class ModernCard(tk.Frame):
    """Modern card widget with rounded corners and shadow effect"""
    def __init__(self, parent: Any, title: str = "", **kwargs: Any) -> None:
        super().__init__(parent, bg=ModernTheme.CARD_BG, relief="flat", bd=0, **kwargs)
        self.title: str = title
        self.content_frame: Optional[tk.Frame] = None
        self._create_card()

    def _create_card(self):
        # Title bar
        if self.title:
            title_frame = tk.Frame(self, bg=ModernTheme.ACCENT_BG, height=40)
            title_frame.pack(fill="x", padx=2, pady=(2, 0))
            title_frame.pack_propagate(False)

            title_label = tk.Label(title_frame, text=self.title,
                                 bg=ModernTheme.ACCENT_BG, fg=ModernTheme.TEXT_PRIMARY,
                                 font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MEDIUM, "bold"))
            title_label.pack(side="left", padx=ModernTheme.PADDING_MEDIUM, pady=8)

        # Content frame
        self.content_frame = tk.Frame(self, bg=ModernTheme.CARD_BG)
        self.content_frame.pack(fill="both", expand=True, padx=2, pady=(0, 2))

class GlassMorphismCard(tk.Frame):
    """Ultra modern glass morphism card with subtle borders and transparency effects"""
    def __init__(self, parent: tk.Widget, title: str = "", **kwargs: Any) -> None:
        # Create outer frame with shadow effect
        super().__init__(parent, bg=ModernTheme.PRIMARY_BG, relief="flat", bd=0, **kwargs)

        # Create glass effect container
        self.glass_container = tk.Frame(self, bg=ModernTheme.GLASS_BG, relief="solid", bd=1)
        self.glass_container.configure(highlightbackground=ModernTheme.GLASS_BORDER,
                                     highlightcolor=ModernTheme.GLASS_HIGHLIGHT,
                                     highlightthickness=1)
        self.glass_container.pack(fill="both", expand=True, padx=2, pady=2)

        # Add subtle inner border for glass effect
        self.inner_frame = tk.Frame(self.glass_container, bg=ModernTheme.GLASS_BG, relief="flat", bd=0)
        self.inner_frame.pack(fill="both", expand=True, padx=1, pady=1)

        self.title = title
        self.content_frame: Optional[tk.Frame] = None
        self._create_glass_card()

    def _create_glass_card(self) -> None:
        # Title bar with glass effect
        if self.title:
            title_frame = tk.Frame(self.inner_frame, bg=ModernTheme.GLASS_HIGHLIGHT, height=35)
            title_frame.pack(fill="x", padx=1, pady=(1, 0))
            title_frame.pack_propagate(False)

            title_label = tk.Label(title_frame, text=self.title,
                                 bg=ModernTheme.GLASS_HIGHLIGHT, fg=ModernTheme.TEXT_PRIMARY,
                                 font=(ModernTheme.FONT_FAMILY, 11, "bold"))
            title_label.pack(side="left", padx=12, pady=8)

        # Content frame with glass background
        self.content_frame = tk.Frame(self.inner_frame, bg=ModernTheme.GLASS_BG)
        self.content_frame.pack(fill="both", expand=True, padx=1, pady=(0, 1))

class ModernProgressBar(tk.Canvas):
    """Modern animated progress bar with gradient effect"""
    def __init__(self, parent: tk.Widget, width: int = 300, height: int = 20, **kwargs: Any) -> None:
        super().__init__(parent, width=width, height=height,
                        bg=ModernTheme.SECONDARY_BG, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.progress = 0.0
        self.target_progress = 0.0
        self.animation_id: Optional[str] = None
        self._draw_background()

    def _draw_background(self) -> None:
        self.delete("all")
        # Background
        self.create_rectangle(0, 0, self.width, self.height,
                            fill=ModernTheme.SECONDARY_BG, outline="")
        # Border
        self.create_rectangle(0, 0, self.width, self.height,
                            fill="", outline=ModernTheme.ACCENT_BG, width=1)

    def set_progress(self, value: float) -> None:
        """Set progress value (0-100) with smooth animation"""
        self.target_progress = max(0.0, min(100.0, value))
        self._animate_to_target()

    def _animate_to_target(self) -> None:
        if self.animation_id:
            self.after_cancel(self.animation_id)

        diff = self.target_progress - self.progress
        if abs(diff) < 0.5:
            self.progress = self.target_progress
            self._draw_progress()
            return

        self.progress += diff * 0.1
        self._draw_progress()
        self.animation_id = self.after(ModernTheme.ANIMATION_SPEED, self._animate_to_target)

    def _draw_progress(self) -> None:
        self._draw_background()
        if self.progress > 0:
            progress_width = (self.progress / 100) * (self.width - 2)
            # Gradient effect simulation
            self.create_rectangle(1, 1, progress_width + 1, self.height - 1,
                                fill=ModernTheme.ACCENT_BLUE, outline="")

class ModernStatusIndicator(tk.Canvas):
    """Modern status indicator with pulsing animation"""
    def __init__(self, parent: tk.Widget, size: int = 16, **kwargs: Any) -> None:
        super().__init__(parent, width=size, height=size,
                        bg=ModernTheme.CARD_BG, highlightthickness=0, **kwargs)
        self.size: int = size
        self.status: str = "offline"  # offline, online, warning, error
        self.pulse_alpha: float = 0.0
        self.pulse_direction: int = 1
        self.animation_id: Optional[str] = None
        self._draw_indicator()

    def set_status(self, status: str) -> None:
        """Set status: offline, online, warning, error"""
        self.status = status
        self._draw_indicator()
        if status == "online":
            self._start_pulse()
        else:
            self._stop_pulse()

    def _draw_indicator(self) -> None:
        self.delete("all")
        colors = {
            "offline": ModernTheme.TEXT_SECONDARY,
            "online": ModernTheme.SUCCESS,
            "warning": ModernTheme.WARNING,
            "error": ModernTheme.ERROR
        }
        color = colors.get(self.status, ModernTheme.TEXT_SECONDARY)

        center = self.size // 2
        radius = center - 2
        self.create_oval(center - radius, center - radius,
                        center + radius, center + radius,
                        fill=color, outline="")

    def _start_pulse(self) -> None:
        if self.animation_id:
            self.after_cancel(self.animation_id)
        self._pulse_animation()

    def _stop_pulse(self) -> None:
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None

    def _pulse_animation(self) -> None:
        self.pulse_alpha += self.pulse_direction * 0.1
        if self.pulse_alpha >= 1:
            self.pulse_alpha = 1
            self.pulse_direction = -1
        elif self.pulse_alpha <= 0:
            self.pulse_alpha = 0
            self.pulse_direction = 1

        self._draw_indicator()
        self.animation_id = self.after(100, self._pulse_animation)

class AdvancedProgressBar(tk.Canvas):
    """Advanced animated progress bar with gradient and glow effects"""
    def __init__(self, parent: tk.Widget, width: int = 300, height: int = 25, **kwargs: Any) -> None:
        super().__init__(parent, width=width, height=height,
                        bg=ModernTheme.SECONDARY_BG, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.progress = 0.0
        self.target_progress = 0.0
        self.animation_id: Optional[str] = None
        self.glow_alpha = 0.0
        self.glow_direction = 1
        self._draw_background()

    def _draw_background(self) -> None:
        self.delete("all")
        # Background with rounded corners effect
        self.create_rectangle(2, 2, self.width-2, self.height-2,
                            fill=ModernTheme.SECONDARY_BG, outline=ModernTheme.ACCENT_BG, width=1)

    def set_progress(self, value: float, animated: bool = True) -> None:
        """Set progress value (0-100) with smooth animation"""
        self.target_progress = max(0.0, min(100.0, value))
        if animated:
            self._animate_to_target()
        else:
            self.progress = self.target_progress
            self._draw_progress()

    def _animate_to_target(self) -> None:
        if self.animation_id:
            self.after_cancel(self.animation_id)

        diff = self.target_progress - self.progress
        if abs(diff) < 0.5:
            self.progress = self.target_progress
            self._draw_progress()
            return

        self.progress += diff * 0.15  # Smooth animation
        self._draw_progress()
        self.animation_id = self.after(ModernTheme.PROGRESS_ANIMATION_SPEED, self._animate_to_target)

    def _draw_progress(self) -> None:
        self._draw_background()
        if self.progress > 0:
            progress_width = (self.progress / 100) * (self.width - 6)
            # Main progress bar
            self.create_rectangle(3, 3, progress_width + 3, self.height - 3,
                                fill=ModernTheme.ACCENT_BLUE, outline="")
            # Highlight effect
            if progress_width > 10:
                self.create_rectangle(3, 3, progress_width + 3, 8,
                                    fill=ModernTheme.ACCENT_PURPLE, outline="")

class ToastNotification:
    """Modern toast notification system"""
    def __init__(self, parent: tk.Widget) -> None:
        self.parent = parent
        self.notifications: List[tk.Toplevel] = []  # List of toast windows
        self.notification_id: int = 0

    def show_toast(self, message: str, toast_type: str = "info", duration: int = 3000) -> None:
        """Show a toast notification"""
        self.notification_id += 1

        # Create notification window
        toast = tk.Toplevel(self.parent)
        toast.withdraw()  # Hide initially
        toast.overrideredirect(True)  # Remove window decorations
        toast.attributes('-topmost', True)  # type: ignore # Always on top

        # Configure toast appearance
        colors = {
            "info": ModernTheme.INFO,
            "success": ModernTheme.SUCCESS,
            "warning": ModernTheme.WARNING,
            "error": ModernTheme.ERROR
        }

        bg_color = colors.get(toast_type, ModernTheme.INFO)

        # Create toast content
        frame = tk.Frame(toast, bg=bg_color, padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        # Message label
        label = tk.Label(frame, text=message, bg=bg_color, fg=ModernTheme.TEXT_PRIMARY,
                        font=(ModernTheme.FONT_FAMILY, 11, 'bold'), wraplength=300)
        label.pack()

        # Position toast - Bottom right corner, less intrusive
        toast.update_idletasks()
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        # Position at bottom-right of screen, stacked upward
        x = screen_width - toast.winfo_width() - 20
        y = screen_height - 100 - (len(self.notifications) * 80)
        toast.geometry(f"+{x}+{y}")

        # Show toast with fade-in effect
        toast.deiconify()
        self.notifications.append(toast)

        # Auto-hide after duration
        toast.after(duration, lambda: self._hide_toast(toast))

    def _hide_toast(self, toast: tk.Toplevel) -> None:
        """Hide and destroy toast notification"""
        if toast in self.notifications:
            self.notifications.remove(toast)
        toast.destroy()

        # Reposition remaining toasts - Bottom right, less intrusive
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        for i, notification in enumerate(self.notifications):
            x = screen_width - notification.winfo_width() - 20
            y = screen_height - 100 - (i * 80)
            notification.geometry(f"+{x}+{y}")

# --- ENHANCED TABLE WIDGET ---
class ModernTooltip:
    """Modern tooltip that appears on hover"""
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text: str = text
        self.tooltip_window: Optional[tk.Toplevel] = None
        # Use safe attribute access for bind method
        if hasattr(self.widget, 'bind') and callable(getattr(self.widget, 'bind', None)):
            self.widget.bind("<Enter>", self.show_tooltip)
            self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event: tk.Event) -> None:
        if self.tooltip_window or not self.text:
            return

        # Use safe attribute access for bbox and winfo methods
        try:
            if hasattr(self.widget, 'bbox') and callable(getattr(self.widget, 'bbox', None)):
                # For text widgets, use "insert" index; for other widgets, use 0 or None
                try:
                    bbox_result = self.widget.bbox("insert")  # type: ignore[attr-defined]
                    if bbox_result and isinstance(bbox_result, (list, tuple)) and len(bbox_result) >= 4:
                        x, y, _, _ = bbox_result
                    else:
                        x, y = 0, 0
                except (tk.TclError, TypeError, ValueError, AttributeError):
                    # Fallback for widgets that don't support "insert" index
                    try:
                        bbox_result = self.widget.bbox(0)  # type: ignore[attr-defined]
                        if bbox_result and isinstance(bbox_result, (list, tuple)) and len(bbox_result) >= 4:
                            x, y, _, _ = bbox_result
                        else:
                            x, y = 0, 0
                    except (tk.TclError, TypeError, ValueError, AttributeError):
                        x, y = 0, 0
            else:
                x, y = 0, 0
        except (AttributeError, tk.TclError, TypeError, ValueError):
            x, y = 0, 0

        if hasattr(self.widget, 'winfo_rootx') and hasattr(self.widget, 'winfo_rooty'):
            x += getattr(self.widget, 'winfo_rootx', lambda: 0)() + 25
            y += getattr(self.widget, 'winfo_rooty', lambda: 0)() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify='left',
                      background=ModernTheme.ACCENT_BG, foreground=ModernTheme.TEXT_PRIMARY,
                      relief='solid', borderwidth=1,
                      font=(ModernTheme.FONT_FAMILY, 9, "normal"), padx=8, pady=5)
        label.pack(ipadx=1)

    def hide_tooltip(self, event: tk.Event) -> None:
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

class DetailPane(ModernCard):
    """A card-like pane to display details of a selected item."""
    def __init__(self, parent: tk.Widget, title: str, **kwargs: Any):
        super().__init__(parent, title=title, **kwargs)
        self.detail_labels: Dict[str, tk.Label] = {}
        if self.content_frame:
            self.text_area = tk.Text(self.content_frame, bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                                     font=(ModernTheme.FONT_FAMILY, 10), relief="flat", wrap="word", height=10)
            self.text_area.pack(fill="both", expand=True, padx=10, pady=10)
            self.text_area.config(state=tk.DISABLED)

    def update_details(self, data: Dict[str, Any]) -> None:
        """Update the details displayed in the pane."""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        formatted_text = json.dumps(data, indent=2)
        self.text_area.insert(tk.END, formatted_text)
        self.text_area.config(state=tk.DISABLED)

    def clear_details(self) -> None:
        """Clear the detail pane."""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)

class ModernTable(tk.Frame):
    """Modern table widget with sorting, filtering, and selection"""
    def __init__(self, parent: tk.Widget, columns: Dict[str, Any], **kwargs: Any) -> None:
        super().__init__(parent, bg=ModernTheme.CARD_BG, **kwargs)
        self.columns: Dict[str, Any] = columns
        self.data: List[Dict[str, Any]] = []
        self.filtered_data: List[Dict[str, Any]] = []
        self.sort_column: Optional[str] = None
        self.sort_reverse: bool = False
        self.selection_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self._create_table()

    def _create_table(self) -> None:
        # Search frame
        search_frame = tk.Frame(self, bg=ModernTheme.CARD_BG)
        search_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(search_frame, text="🔍", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 12)).pack(side="left", padx=(5, 2))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                               font=(ModernTheme.FONT_FAMILY, 10), relief="flat", bd=5)
        search_entry.pack(side="left", fill="x", expand=True)

        # Table frame with scrollbars
        table_container = tk.Frame(self, bg=ModernTheme.CARD_BG)
        table_container.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # Create Treeview
        self.tree = ttk.Treeview(table_container, columns=list(self.columns.keys()), 
                                show="tree headings", height=10)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",   # type: ignore
                       background=ModernTheme.SECONDARY_BG,
                       foreground=ModernTheme.TEXT_PRIMARY,
                       fieldbackground=ModernTheme.SECONDARY_BG,
                       borderwidth=0)
        style.configure("Treeview.Heading",  # type: ignore
                       background=ModernTheme.ACCENT_BG,
                       foreground=ModernTheme.TEXT_PRIMARY,
                       relief="flat")
        style.map("Treeview",  # type: ignore
                 background=[('selected', ModernTheme.ACCENT_BLUE)])

        # Configure columns
        self.tree.column("#0", width=50, stretch=False)
        for col_id, col_info in self.columns.items():
            self.tree.column(col_id, width=col_info.get('width', 100), 
                           minwidth=col_info.get('minwidth', 50))
            self.tree.heading(col_id, text=col_info['text'],
                            command=lambda c=col_id: self._sort_by_column(c))

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)  # type: ignore
        h_scroll = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)  # type: ignore
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Pack elements
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_change)
        self.tree.bind("<Button-3>", self._show_context_menu) # Right-click
        self.tree.bind("<ButtonPress-1>", self._on_mouse_press)
        self.tree.bind("<B1-Motion>", self._on_mouse_drag)

        self.context_menu: Optional[tk.Menu] = None
        self.drag_start_x = 0
        self.drag_start_y = 0

    def _on_mouse_press(self, event: tk.Event) -> None:
        """Record starting position of a potential drag."""
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_mouse_drag(self, event: tk.Event) -> None:
        """If mouse is dragged significantly, start a drag-and-drop operation."""
        if not DND_AVAILABLE:
            return

        distance = ((event.x - self.drag_start_x)**2 + (event.y - self.drag_start_y)**2)**0.5
        if distance > 10: # Start drag after 10 pixels
            self._start_drag(event)

    def _start_drag(self, event: tk.Event) -> None:
        """Initiates the drag and drop operation."""
        # This is a placeholder for the actual DND logic
        print("Drag operation started!")
        # In a real implementation, we would use self.tree.dnd_start() here
        # with the appropriate data.

    def _show_context_menu(self, event: tk.Event) -> None:
        """Show context menu on right-click."""
        if not self.context_menu:
            return

        # Select row under cursor using named expression
        if iid := self.tree.identify_row(event.y):
            self.tree.selection_set(iid)
            self.context_menu.post(event.x_root, event.y_root)

    def set_context_menu(self, menu: tk.Menu) -> None:
        """Set the context menu for the table."""
        self.context_menu = menu
        self.tree.bind("<Button-3>", self._show_context_menu) # Right-click

    def set_data(self, data: List[Dict[str, Any]]) -> None:
        """Set table data"""
        self.data = data
        self._apply_filter()

    def _apply_filter(self) -> None:
        """Apply search filter to data"""
        search_text = self.search_var.get().lower() if hasattr(self.search_var, 'get') else ''
        if search_text:
            self.filtered_data = []
            for item in self.data:
                # Check if search text is in any column
                if any(search_text in str(item.get(col, '')).lower() 
                      for col in self.columns.keys() if isinstance(item, dict)):
                    self.filtered_data.append(item)
        else:
            self.filtered_data = self.data.copy()
        
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Refresh the table display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add filtered items
        for idx, item in enumerate(self.filtered_data):
            values = [item.get(col, '') if isinstance(item, dict) else '' for col in self.columns.keys()]
            self.tree.insert("", "end", text=str(idx + 1), values=values)

    def _sort_by_column(self, column: str) -> None:
        """Sort table by column"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        self.filtered_data.sort(key=lambda x: x.get(column, '') if isinstance(x, dict) else '', 
                               reverse=self.sort_reverse)
        self._refresh_display()

    def _on_search_change(self, *args: Any) -> None:
        """Handle search text change"""
        self._apply_filter()

    def _on_selection_change(self, event: tk.Event) -> None:
        """Handle selection change"""
        selection = self.tree.selection()
        if selection and self.selection_callback:
            item = self.tree.item(selection[0])
            index = int(item['text']) - 1
            if 0 <= index < len(self.filtered_data):
                self.selection_callback(self.filtered_data[index])

    def set_selection_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Set callback for selection changes"""
        self.selection_callback = callback

    def get_selected_items(self) -> List[Dict[str, Any]]:
        """Get currently selected items"""
        selected: List[Dict[str, Any]] = []
        for item_id in self.tree.selection():
            item = self.tree.item(item_id)
            if item and 'text' in item and item['text']:
                try:
                    index = int(item['text']) - 1
                    if 0 <= index < len(self.filtered_data):
                        selected.append(self.filtered_data[index])
                except (ValueError, TypeError):
                    continue
        return selected

# --- SETTINGS DIALOG ---
class SettingsDialog:
    """Modern settings dialog"""
    def __init__(self, parent: Union[tk.Widget, tk.Tk], current_settings: Dict[str, Any]) -> None:
        self.parent = parent
        self.settings: Dict[str, Any] = current_settings.copy() if hasattr(current_settings, 'copy') and callable(getattr(current_settings, 'copy', None)) else dict(current_settings) if current_settings else {}
        self.dialog: Optional[tk.Toplevel] = None
        self.result: Optional[Dict[str, Any]] = None

    def show(self) -> Optional[Dict[str, Any]]:
        """Show the settings dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Server Settings")
        self.dialog.geometry("500x600")
        self.dialog.configure(bg=ModernTheme.PRIMARY_BG)
        # Set transient relationship if parent supports it
        with suppress(tk.TclError, AttributeError, TypeError):
            if (hasattr(self.dialog, 'transient') and 
                callable(getattr(self.dialog, 'transient', None)) and
                hasattr(self.parent, 'winfo_class')):
                self.dialog.transient(self.parent)  # type: ignore[arg-type]
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_settings_ui()
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
        return self.result

    def _create_settings_ui(self) -> None:
        """Create settings UI"""
        # Main container
        main_frame = tk.Frame(self.dialog, bg=ModernTheme.PRIMARY_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(main_frame, text="Server Configuration",
                             bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 16, 'bold'))
        title_label.pack(pady=(0, 20))

        # Create notebook for tabs
        style = ttk.Style()
        style.configure('Dark.TNotebook', background=ModernTheme.PRIMARY_BG)  # type: ignore
        style.configure('Dark.TNotebook.Tab', background=ModernTheme.CARD_BG,  # type: ignore
                       foreground=ModernTheme.TEXT_PRIMARY, padding=[20, 10])
        style.map('Dark.TNotebook.Tab',  # type: ignore
                 background=[('selected', ModernTheme.ACCENT_BG)])

        notebook = ttk.Notebook(main_frame, style='Dark.TNotebook')
        notebook.pack(fill="both", expand=True)

        # General tab
        general_frame = tk.Frame(notebook, bg=ModernTheme.CARD_BG)
        notebook.add(general_frame, text="General")
        self._create_general_settings(general_frame)

        # Security tab
        security_frame = tk.Frame(notebook, bg=ModernTheme.CARD_BG)
        notebook.add(security_frame, text="Security")
        self._create_security_settings(security_frame)

        # Performance tab
        performance_frame = tk.Frame(notebook, bg=ModernTheme.CARD_BG)
        notebook.add(performance_frame, text="Performance")
        self._create_performance_settings(performance_frame)

        # Buttons
        button_frame = tk.Frame(main_frame, bg=ModernTheme.PRIMARY_BG)
        button_frame.pack(fill="x", pady=(20, 0))

        save_btn = tk.Button(button_frame, text="💾 Save", command=self._save_settings,
                           bg=ModernTheme.SUCCESS, fg=ModernTheme.TEXT_PRIMARY,
                           font=(ModernTheme.FONT_FAMILY, 11, 'bold'),
                           relief="flat", bd=0, padx=20, pady=8)
        save_btn.pack(side="right", padx=(10, 0))

        cancel_btn = tk.Button(button_frame, text="[CANCEL] Cancel", command=self._cancel,
                             bg=ModernTheme.ERROR, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 11, 'bold'),
                             relief="flat", bd=0, padx=20, pady=8)
        cancel_btn.pack(side="right")

    def _create_general_settings(self, parent: tk.Widget) -> None:
        """Create general settings"""
        # Port setting
        port_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        port_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(port_frame, text="Server Port:", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        port_value = self.settings.get('port', 1256) if isinstance(self.settings, dict) else 1256
        self.port_var = tk.StringVar(value=str(port_value))
        port_entry = tk.Entry(port_frame, textvariable=self.port_var,
                            bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                            font=(ModernTheme.FONT_FAMILY, 11))
        port_entry.pack(fill="x", pady=(5, 0))

        # Storage directory
        storage_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        storage_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(storage_frame, text="Storage Directory:", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        storage_subframe = tk.Frame(storage_frame, bg=ModernTheme.CARD_BG)
        storage_subframe.pack(fill="x", pady=(5, 0))

        storage_value = self.settings.get('storage_dir', 'received_files') if isinstance(self.settings, dict) else 'received_files'
        self.storage_var = tk.StringVar(value=str(storage_value))
        storage_entry = tk.Entry(storage_subframe, textvariable=self.storage_var,
                               bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                               font=(ModernTheme.FONT_FAMILY, 11))
        storage_entry.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Button(storage_subframe, text="📁", command=self._browse_directory,
                             bg=ModernTheme.ACCENT_BLUE, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 11), relief="flat", bd=0, padx=10)
        browse_btn.pack(side="right", padx=(5, 0))

        # Max clients
        clients_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        clients_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(clients_frame, text="Max Concurrent Clients:", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        self.max_clients_var = tk.StringVar(value=str(self.settings.get('max_clients', 50)))
        clients_entry = tk.Entry(clients_frame, textvariable=self.max_clients_var,
                               bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                               font=(ModernTheme.FONT_FAMILY, 11))
        clients_entry.pack(fill="x", pady=(5, 0))

    def _create_security_settings(self, parent: tk.Widget) -> None:
        """Create security settings"""
        # Client timeout
        timeout_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        timeout_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(timeout_frame, text="Client Session Timeout (minutes):", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        self.timeout_var = tk.StringVar(value=str(self.settings.get('session_timeout', 10)))
        timeout_entry = tk.Entry(timeout_frame, textvariable=self.timeout_var,
                               bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                               font=(ModernTheme.FONT_FAMILY, 11))
        timeout_entry.pack(fill="x", pady=(5, 0))

        # Encryption info
        enc_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        enc_frame.pack(fill="x", padx=20, pady=20)

        tk.Label(enc_frame, text="Encryption Settings:", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11, 'bold')).pack(anchor="w")
        
        enc_info = [
            "• RSA Key Size: 1024 bits",
            "• AES Key Size: 256 bits",
            "• AES Mode: CBC with PKCS7 padding",
            "• Hash Algorithm: SHA256 for OAEP"
        ]
        
        for info in enc_info:
            tk.Label(enc_frame, text=info, bg=ModernTheme.CARD_BG,
                    fg=ModernTheme.TEXT_SECONDARY, font=(ModernTheme.FONT_FAMILY, 10)).pack(anchor="w", pady=2)

    def _create_performance_settings(self, parent: tk.Widget) -> None:
        """Create performance settings"""
        # Maintenance interval
        maintenance_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        maintenance_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(maintenance_frame, text="Maintenance Interval (seconds):", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        self.maintenance_var = tk.StringVar(value=str(self.settings.get('maintenance_interval', 60)))
        maintenance_entry = tk.Entry(maintenance_frame, textvariable=self.maintenance_var,
                                   bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                                   font=(ModernTheme.FONT_FAMILY, 11))
        maintenance_entry.pack(fill="x", pady=(5, 0))

        # File size limits
        size_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        size_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(size_frame, text="Max File Size (MB):", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        self.max_size_var = tk.StringVar(value=str(self.settings.get('max_file_size_mb', 4096)))
        size_entry = tk.Entry(size_frame, textvariable=self.max_size_var,
                            bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                            font=(ModernTheme.FONT_FAMILY, 11))
        size_entry.pack(fill="x", pady=(5, 0))

        # Performance options
        perf_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        perf_frame.pack(fill="x", padx=20, pady=20)

        self.log_verbose_var = tk.BooleanVar(value=self.settings.get('verbose_logging', False))
        verbose_check = tk.Checkbutton(perf_frame, text="Verbose Logging",
                                     variable=self.log_verbose_var,
                                     bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                                     font=(ModernTheme.FONT_FAMILY, 11),
                                     selectcolor=ModernTheme.SECONDARY_BG)
        verbose_check.pack(anchor="w")

        self.auto_backup_var = tk.BooleanVar(value=self.settings.get('auto_backup_db', True))
        backup_check = tk.Checkbutton(perf_frame, text="Auto-backup Database",
                                    variable=self.auto_backup_var,
                                    bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                                    font=(ModernTheme.FONT_FAMILY, 11),
                                    selectcolor=ModernTheme.SECONDARY_BG)
        backup_check.pack(anchor="w", pady=(10, 0))

    def _browse_directory(self) -> None:
        """Browse for storage directory"""
        if directory := filedialog.askdirectory(parent=self.dialog,
                                          initialdir=self.storage_var.get()):
            self.storage_var.set(directory)

    def _save_settings(self) -> None:
        """Save settings to file and close dialog"""
        try:
            # Validate inputs
            port = int(self.port_var.get())
            if not 1024 <= port <= 65535:
                raise ValueError("Port must be between 1024 and 65535")

            max_clients = int(self.max_clients_var.get())
            if max_clients < 1:
                raise ValueError("Max clients must be at least 1")

            timeout = int(self.timeout_var.get())
            if timeout < 1:
                raise ValueError("Timeout must be at least 1 minute")

            maintenance = int(self.maintenance_var.get())
            if maintenance < 10:
                raise ValueError("Maintenance interval must be at least 10 seconds")

            max_size = int(self.max_size_var.get())
            if max_size < 1:
                raise ValueError("Max file size must be at least 1 MB")

            # Update settings
            self.settings['port'] = port
            self.settings['storage_dir'] = self.storage_var.get()
            self.settings['max_clients'] = max_clients
            self.settings['session_timeout'] = timeout
            self.settings['maintenance_interval'] = maintenance
            self.settings['max_file_size_mb'] = max_size
            self.settings['verbose_logging'] = self.log_verbose_var.get()
            self.settings['auto_backup_db'] = self.auto_backup_var.get()

            # Save settings to file
            self._persist_settings_to_file()

            self.result = self.settings
            if self.dialog:
                self.dialog.destroy()
                
        except Exception as e:
            messagebox.showerror("Settings Error", f"Failed to save settings: {str(e)}", 
                               parent=self.dialog or self.parent)

    def _persist_settings_to_file(self) -> None:
        """Persist settings to configuration file"""
        try:
            settings_file = "server_gui_settings.json"
            settings_data = {
                'server_settings': self.settings,
                'gui_preferences': {
                    'last_tab': getattr(self, 'current_tab', 'dashboard'),
                    'window_state': 'normal',
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2)
                
            print(f"Settings saved to {settings_file}")
            
        except Exception as e:
            print(f"Failed to save settings to file: {e}")
            raise

    def _cancel(self) -> None:
        """Cancel and close dialog"""
        self.result = None
        if self.dialog:
            self.dialog.destroy()

# --- CHART WIDGET ---
class ModernChart(tk.Frame):
    """Modern chart widget using matplotlib"""
    def __init__(self, parent: tk.Widget, chart_type: str = "line", **kwargs: Any) -> None:
        super().__init__(parent, bg=ModernTheme.CARD_BG, **kwargs)
        self.chart_type = chart_type
        self.data: Dict[str, Any] = {}
        if TYPE_CHECKING:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.axes import Axes
        self.figure: Optional[Any] = None  # Will be Figure when available
        self.canvas: Optional[Any] = None  # Will be FigureCanvasTkAgg when available
        self.ax: Optional[Any] = None      # Will be Axes when available
        self._create_chart()

    def _create_chart(self) -> None:
        """Create the chart"""
        if not CHARTS_AVAILABLE or not Figure or not plt:
            label = tk.Label(self, text="Charts not available\n(matplotlib not installed)",
                           bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                           font=(ModernTheme.FONT_FAMILY, 12))
            label.pack(expand=True)
            return

        # Create figure with dark background 
        self.figure = Figure(figsize=(6, 4), dpi=100, facecolor=ModernTheme.CARD_BG)
        self.ax = self.figure.add_subplot(111)
        
        # Style the axes (with safety check)
        if self.ax is not None:
            self._configure_chart_axes()

        # Create canvas
        if FigureCanvasTkAgg and self.figure:
            self.canvas = FigureCanvasTkAgg(self.figure, self)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _configure_chart_axes(self) -> None:
        """Configure chart axes styling for dark theme."""
        if self.ax is None:
            return
        self.ax.set_facecolor(ModernTheme.SECONDARY_BG)
        self.ax.spines['bottom'].set_color(ModernTheme.TEXT_SECONDARY)
        self.ax.spines['top'].set_color(ModernTheme.TEXT_SECONDARY)
        self.ax.spines['left'].set_color(ModernTheme.TEXT_SECONDARY)
        self.ax.spines['right'].set_color(ModernTheme.TEXT_SECONDARY)
        self.ax.tick_params(colors=ModernTheme.TEXT_SECONDARY)
        self.ax.xaxis.label.set_color(ModernTheme.TEXT_PRIMARY)
        self.ax.yaxis.label.set_color(ModernTheme.TEXT_PRIMARY)
        # Fix: Use set_title with color parameter instead of accessing title attribute
        self.ax.set_title('', color=ModernTheme.TEXT_PRIMARY)

    def update_data(self, data: Dict[str, Any], title: str = "", xlabel: str = "", ylabel: str = "") -> None:
        """Update chart data"""
        if not CHARTS_AVAILABLE or not self.ax or not self.figure or not self.canvas:
            return

        self.data = data
        self.ax.clear()

        # Set labels
        self.ax.set_title(title, color=ModernTheme.TEXT_PRIMARY, fontsize=12, pad=10)
        self.ax.set_xlabel(xlabel, color=ModernTheme.TEXT_PRIMARY, fontsize=10)
        self.ax.set_ylabel(ylabel, color=ModernTheme.TEXT_PRIMARY, fontsize=10)

        # Plot based on chart type
        if self.chart_type == "line":
            for label, (x_data, y_data) in data.items():
                if self.ax and hasattr(self.ax, 'plot'):
                    self.ax.plot(x_data, y_data, label=label, linewidth=2)
        elif self.chart_type == "bar":
            if data:
                labels = list(data.keys())
                values = list(data.values())
                colors = [ModernTheme.ACCENT_BLUE, ModernTheme.ACCENT_PURPLE, 
                         ModernTheme.ACCENT_GREEN, ModernTheme.ACCENT_ORANGE] * len(labels)
                if self.ax and hasattr(self.ax, 'bar'):
                    self.ax.bar(labels, values, color=colors[:len(labels)])
        elif self.chart_type == "pie":
            if data:
                labels = list(data.keys())
                values = list(data.values())
                colors = [ModernTheme.ACCENT_BLUE, ModernTheme.ACCENT_PURPLE,
                         ModernTheme.ACCENT_GREEN, ModernTheme.ACCENT_ORANGE] * len(labels)
                if self.ax and hasattr(self.ax, 'pie'):
                    self.ax.pie(values, labels=labels, colors=colors[:len(labels)],
                               autopct='%1.1f%%', textprops={'color': ModernTheme.TEXT_PRIMARY})

        # Configure grid
        if self.ax and hasattr(self.ax, 'grid'):
            self.ax.grid(True, alpha=0.3, color=ModernTheme.TEXT_SECONDARY, linestyle='--')

        # Add legend if needed
        if self.chart_type == "line" and len(data) > 1 and self.ax and hasattr(self.ax, 'legend'):
            legend = self.ax.legend(facecolor=ModernTheme.CARD_BG, 
                                  edgecolor=ModernTheme.TEXT_SECONDARY)
            if legend and hasattr(legend, 'get_texts'):
                for text in legend.get_texts():
                    if hasattr(text, 'set_color'):
                        text.set_color(ModernTheme.TEXT_PRIMARY)        # Style the plot
        self.ax.set_facecolor(ModernTheme.SECONDARY_BG)
        if self.figure:
            self.figure.tight_layout()
        if self.canvas:
            self.canvas.draw()


# --- MAIN GUI CLASS ---
class ServerGUIStatus:
    """Server status information structure"""
    def __init__(self):
        self.running = False
        self.server_address = ""
        self.port = 0
        self.clients_connected = 0
        self.connected_clients = 0  # Alias for consistency
        self.total_clients = 0
        self.active_transfers = 0
        self.bytes_transferred = 0
        self.uptime_seconds = 0
        self.last_activity = ""
        self.error_message = ""
        self.maintenance_stats = {  # type: ignore
            'files_cleaned': 0,
            'partial_files_cleaned': 0,
            'clients_cleaned': 0,
            'last_cleanup': 'Never'
        }

class ServerGUI:
    """ULTRA MODERN GUI class for the server dashboard - Enhanced version"""

    def __init__(self, server_instance: Optional[Any] = None) -> None:  # BackupServer when available
        # Narrow the server to a structural protocol to help type checking without changing runtime
        self.server: Optional[BackupServerLike] = server_instance  # type: ignore[assignment]
        self.status = ServerGUIStatus()
        self.gui_enabled = False
        self.root: Optional[tk.Tk] = None
        self.tray_icon: Optional[Any] = None  # pystray.Icon when available
        self.update_queue: queue.Queue[Any] = queue.Queue()
        self.running = False
        self.gui_thread: Optional[threading.Thread] = None
        self.start_time = time.time()

        # GUI update lock
        self.lock = threading.Lock()

        # Status widgets references
        self.status_labels: Dict[str, tk.Label] = {}
        self.progress_vars: Dict[str, tk.DoubleVar] = {}
        # Late-bound widgets (created in builders)
        self.clock_label: Optional[tk.Label] = None
        self.header_status_label: Optional[tk.Label] = None
        self.activity_log_text: Optional[tk.Text] = None

        # Advanced UI components
        self.toast_system: Optional[ToastNotification] = None
        self.advanced_progress_bars: Dict[str, AdvancedProgressBar] = {}
        self.activity_log: List[str] = []
        self.performance_data: Dict[str, Deque[Any]] = {
            'cpu_usage': deque(maxlen=60),
            'memory_usage': deque(maxlen=60),
            'network_activity': deque(maxlen=60),
            'client_connections': deque(maxlen=60),
            'timestamps': deque(maxlen=60),
            'bytes_transferred': deque(maxlen=60)
        }
        # Current tab tracking
        self.current_tab: str = "dashboard"

        # Tables for clients and files
        self.client_table: Optional[ModernTable] = None
        self.file_table: Optional[ModernTable] = None
        
        # Detail panes for tables
        self.client_detail_pane: Optional['DetailPane'] = None
        self.file_detail_pane: Optional['DetailPane'] = None

        # Charts
        self.performance_chart: Optional[ModernChart] = None
        self.transfer_chart: Optional[ModernChart] = None
        self.client_chart: Optional[ModernChart] = None
        # Analytics date entries (may be tk.Entry or tkcalendar.DateEntry)
        # Use Any to allow access to get/get_date without analyzer complaints
        self.start_date_entry: Optional[Any] = None
        self.end_date_entry: Optional[Any] = None

        # Status indicators
        self.header_status_indicator: Optional[ModernStatusIndicator] = None
        self.tab_buttons: Dict[str, tk.Button] = {}
        self.tab_contents: Dict[str, tk.Frame] = {}

        # Additional GUI components with proper typing
        self.main_frame: Optional[tk.Frame] = None
        self.header_frame: Optional[tk.Frame] = None
        self.content_area: Optional[tk.Frame] = None
        self.dashboard_frame: Optional[tk.Frame] = None
        self.control_frame: Optional[tk.Frame] = None
        self.status_frame: Optional[tk.Frame] = None
        self.process_monitor_widget: Optional[Any] = None  # ProcessMonitorWidget when available

        # Server reference is already set in __init__ - don't overwrite it!

        # Settings - Load from file or use defaults
        self.settings: Dict[str, Any] = self._load_settings_from_file()

        # Database path
        self.db_path = "defensive.db"

        # Performance monitoring
        self.last_bytes_transferred = 0
        self.network_monitor_start = time.time()
        # Network counters cached between updates
        self.last_network_bytes: Optional[int] = None
        # Auto-refresh timer cache
        self._last_file_refresh_time: Optional[float] = None

    def _make_date_entry(self, parent: tk.Widget, **kwargs: Any) -> tk.Widget:
        """Create a date entry widget that falls back to a plain tk.Entry when tkcalendar isn't available.

        This centralizes the conditional creation so static analyzers don't see a possible None call on DateEntry.
        """
        if CALENDAR_AVAILABLE and DateEntry is not None:
            # DateEntry is provided by tkcalendar; cast to a generic Widget for type checkers
            try:
                return cast(tk.Widget, DateEntry(parent, **kwargs))  # type: ignore[call-arg]
            except Exception:
                # Fall back to standard Entry on any runtime issue
                return tk.Entry(parent, width=15)
        # Fallback
        return tk.Entry(parent, width=15)
        
    def _load_settings_from_file(self) -> Dict[str, Any]:
        """Load settings from configuration file or return defaults"""
        default_settings: Dict[str, Any] = {
            'port': 1256,
            'storage_dir': 'received_files',
            'max_clients': 50,
            'session_timeout': 10,
            'maintenance_interval': 60,
            'max_file_size_mb': 4096,
            'verbose_logging': False,
            'auto_backup_db': True
        }
        
        try:
            settings_file = "server_gui_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                
                # Merge loaded settings with defaults to ensure all keys exist
                if 'server_settings' in settings_data:
                    loaded_settings = settings_data['server_settings']
                    # Update defaults with loaded values
                    for key, value in loaded_settings.items():
                        if key in default_settings:
                            default_settings[key] = value
                    
                    # Restore GUI preferences if available
                    if 'gui_preferences' in settings_data:
                        gui_prefs = settings_data['gui_preferences']
                        if 'last_tab' in gui_prefs:
                            self.current_tab = gui_prefs['last_tab']
                    
                    print(f"Settings loaded from {settings_file}")
                else:
                    print("Invalid settings file format, using defaults")
            else:
                print("Settings file not found, using defaults")
                
        except Exception as e:
            print(f"Failed to load settings from file: {e}, using defaults")
            
        return default_settings
    
    def _save_current_settings(self) -> bool:
        """Save current settings to file (for use during runtime)"""
        try:
            settings_file = "server_gui_settings.json"
            settings_data = {
                'server_settings': self.settings,
                'gui_preferences': {
                    'last_tab': self.current_tab,
                    'window_state': 'normal',
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2)
                
            print(f"Current settings saved to {settings_file}")
            return True
            
        except Exception as e:
            print(f"Failed to save current settings: {e}")
            return False
        
    def initialize(self) -> bool:
        """Initialize GUI system"""
        try:
            self.running = True
            self.gui_thread = threading.Thread(target=self._gui_main_loop, daemon=False)
            self.gui_thread.start()

            # Wait for GUI to initialize
            max_wait = 50  # 5 seconds max
            wait_count = 0
            while not self.gui_enabled and wait_count < max_wait:
                time.sleep(0.1)
                wait_count += 1

            if self.gui_enabled:
                print("[OK] Enhanced Modern GUI initialized successfully!")
                return True
            else:
                print("[ERROR] Modern GUI initialization timed out")
                return False

        except Exception as e:
            print(f"GUI initialization failed: {e}")
            # Cleaned up duplicate import
            traceback.print_exc()
            return False
    
    def shutdown(self) -> None:
        """Enhanced shutdown with settings persistence and cleanup"""
        print("Starting GUI shutdown process...")
        self.running = False
        
        try:
            # Save current settings and state before shutdown
            self._save_current_settings()
            self._add_activity_log("💾 Settings saved during shutdown")
        except Exception as e:
            print(f"Warning: Failed to save settings during shutdown: {e}")
        
        try:
            # Stop system tray
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                    print("[OK] System tray stopped")
                except Exception as e:
                    print(f"Warning: Failed to stop tray icon: {e}")
            
            # Gracefully shutdown GUI
            if self.root:
                try:
                    self.root.quit()
                    print("[OK] GUI root window closed")
                except Exception as e:
                    print(f"Warning: Failed to quit GUI root window: {e}")
            
            # Wait for GUI thread to complete
            if self.gui_thread and self.gui_thread.is_alive():
                print("Waiting for GUI thread to complete...")
                self.gui_thread.join(timeout=3.0)
                if self.gui_thread.is_alive():
                    print("Warning: GUI thread did not complete within timeout")
                else:
                    print("[OK] GUI thread completed successfully")
                    
        except Exception as e:
            print(f"Error during shutdown: {e}")

        print("GUI shutdown completed")

    def _gui_main_loop(self) -> None:
        """Main GUI thread loop"""
        try:
            print("Starting enhanced ultra modern GUI main loop...")
            # Initialize tkinter with error handling
            try:
                if DND_AVAILABLE and TkinterDnD is not None:
                    # Use TkinterDnD if available and not None; cast to tk.Tk for type checkers
                    self.root = cast(tk.Tk, TkinterDnD.Tk())  # type: ignore[assignment]
                    print("TkinterDnD root created for drag-and-drop support.")
                else:
                    # Create standard Tk root and hint its type for static analyzers
                    self.root = cast(tk.Tk, tk.Tk())
                    print("Tkinter root created")
            except Exception as e:
                print(f"Failed to create Tkinter root: {e}")
                print("GUI will not be available - continuing in console mode")
                return

            # Configure the root window
            try:
                self.root.title("[SECURE] ULTRA MODERN Encrypted Backup Server - Enhanced")
                self.root.geometry("1200x800")
                self.root.minsize(800, 600) # Lowered minsize for better responsiveness
                self.root.configure(bg=ModernTheme.PRIMARY_BG)
                self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

                # Force window to front and make it visible
                self.root.lift()  # type: ignore
                self.root.attributes('-topmost', True)  # type: ignore
                def _clear_topmost() -> None:
                    if self.root is not None:
                        with suppress(Exception):
                            self.root.attributes('-topmost', False)  # type: ignore[attr-defined]
                self.root.after(1000, _clear_topmost)  # type: ignore
                self.root.focus_force()
                self.root.deiconify()  # Ensure window is not minimized
                self.root.state('normal')  # Ensure window is in normal state
                
                # Additional visibility fixes
                self.root.wm_state('normal')
                self.root.tkraise()  # type: ignore
                self.root.grab_set()  # Keep focus initially
                def _safe_grab_release() -> None:
                    if self.root is not None:
                        with suppress(Exception):
                            self.root.grab_release()
                self.root.after(2000, _safe_grab_release)

                print("Root window configured with modern theme")
            except Exception as e:
                print(f"Failed to configure root window: {e}")
                if self.root:
                    self.root.destroy()
                return

            # Create modern GUI components
            try:
                print("Creating enhanced ultra modern main window...")
                self._create_main_window()
                print("Creating enhanced ultra modern main window...")
                self._create_system_tray()
                print("System tray created")
            except Exception as e:
                print(f"Failed to create GUI components: {e}")
                if self.root:
                    self.root.destroy()
                return

            # Mark GUI as enabled
            self.gui_enabled = True
            print("Enhanced Modern GUI enabled, starting main loop")

            # Start update timer
            self._schedule_updates()

            # Run GUI main loop
            if self.root is not None:
                self.root.mainloop()

        except Exception as e:
            print(f"Modern GUI main loop error: {e}")
            import traceback
# Cleaned up duplicate import
            traceback.print_exc()
        finally:
            self.gui_enabled = False
            print("Modern GUI main loop ended")
    
    def _create_main_window(self) -> None:
        """Create the enhanced main window with a sidebar navigation."""
        print("Creating enhanced ultra modern main window with sidebar...")

        # Configure modern styling
        self._setup_modern_styles()

        # Create menu bar
        self._create_menu_bar()

        # Create main container with Grid layout
        main_container = tk.Frame(self.root, bg=ModernTheme.PRIMARY_BG)
        main_container.pack(fill="both", expand=True)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(1, weight=1)

        # Header with title and real-time clock (spans across sidebar and content)
        self._create_header(main_container)
        if self.header_frame:
            self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10,0))

        # Create sidebar navigation
        self._create_sidebar(main_container)

        # Create content area for pages
        self._create_content_pages(main_container)

        # Initialize components
        if self.root is not None:
            # Cast root to Widget for ToastNotification constructor to satisfy type checkers
            self.toast_system = ToastNotification(cast(tk.Widget, self.root))
        else:
            self.toast_system = None
            
        # Show welcome toast
        if self.root and self.toast_system:
            def show_welcome():
                self._safe_toast("[READY] Enhanced Ultra Modern GUI Ready", "success", 3000)
            self.root.after(1000, show_welcome)

        print("Enhanced ultra modern main window with sidebar created successfully!")

    def _safe_toast(self, message: str, level: str = "info", duration: int = 3000) -> None:
        """Safely show a toast if toast system exists. Keeps single-point guard for optional toast_system."""
        with suppress(Exception):
            if self.toast_system:
                self.toast_system.show_toast(message, level, duration)

    def _create_menu_bar(self) -> None:
        """Create modern menu bar"""
        if not self.root:
            return
            
        menubar = tk.Menu(self.root, bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                         activebackground=ModernTheme.ACCENT_BLUE,
                         activeforeground=ModernTheme.TEXT_PRIMARY)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Clients...", command=self._export_clients)
        file_menu.add_command(label="Export Files...", command=self._export_files)
        file_menu.add_separator()
        file_menu.add_command(label="Backup Database", command=self._backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="[EXIT] Exit", command=self._exit_server)

        # Server menu
        server_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                             fg=ModernTheme.TEXT_PRIMARY,
                             activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="Server", menu=server_menu)
        server_menu.add_command(label="Settings...", command=self._show_settings)
        server_menu.add_command(label="🔄 Restart Server", command=self._restart_server)
        server_menu.add_separator()
        server_menu.add_command(label="Clear Activity Log", command=self._clear_activity_log)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="🏠 Dashboard", command=lambda: self._switch_page("dashboard"))
        view_menu.add_command(label="👥 Clients", command=lambda: self._switch_page("clients"))
        view_menu.add_command(label="📁 Files", command=lambda: self._switch_page("files"))
        view_menu.add_command(label="📈 Analytics", command=lambda: self._switch_page("analytics"))

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="📖 Documentation", command=self._show_documentation)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_header(self, parent: tk.Widget) -> None:
        """Create header with title and clock"""
        self.header_frame = tk.Frame(parent, bg=ModernTheme.PRIMARY_BG, height=60)
        # self.header_frame.pack(fill="x", pady=(0, 15)) # Changed to grid in _create_main_window
        self.header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(self.header_frame, text="[SECURE] Encrypted Backup Server",
                              bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                              font=(ModernTheme.FONT_FAMILY, 22, 'bold'))
        title_label.pack(side="left", padx=10, pady=10)

        # Global Search Bar
        search_frame = tk.Frame(self.header_frame, bg=ModernTheme.PRIMARY_BG)
        search_frame.pack(side="left", padx=20, fill="x", expand=True)

        self.global_search_var = tk.StringVar()
        self.global_search_var.trace_add("write", self._on_global_search)
        search_entry = tk.Entry(search_frame, textvariable=self.global_search_var,
                               bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                               font=(ModernTheme.FONT_FAMILY, 11), relief="flat", bd=8,
                               width=50)
        search_entry.insert(0, "🔍 Search clients, files, logs...")
        search_entry.bind("<FocusIn>", self._on_search_focus_in)
        search_entry.bind("<FocusOut>", self._on_search_focus_out)
        search_entry.pack(side="left", fill="x", expand=True)

        # Clock and status
        status_frame = tk.Frame(self.header_frame, bg=ModernTheme.PRIMARY_BG)
        status_frame.pack(side="right", padx=10, pady=10)

        self.clock_label = tk.Label(status_frame, text="",
                                   bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_SECONDARY,
                                   font=(ModernTheme.FONT_FAMILY, 12))
        self.clock_label.pack(anchor="e")

        # Server status indicator
        status_indicator_frame = tk.Frame(status_frame, bg=ModernTheme.PRIMARY_BG)
        status_indicator_frame.pack(pady=(5, 0), anchor="e")

        self.header_status_label = tk.Label(status_indicator_frame, text="Server Offline",
                                           bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_SECONDARY,
                                           font=(ModernTheme.FONT_FAMILY, 11))
        self.header_status_label.pack(side="left", padx=(0, 5))

        self.header_status_indicator = ModernStatusIndicator(status_indicator_frame)
        self.header_status_indicator.pack(side="left")

    def _create_sidebar(self, parent: tk.Widget) -> None:
        """Creates the main navigation sidebar."""
        sidebar_frame = tk.Frame(parent, bg=ModernTheme.SECONDARY_BG, width=200)
        sidebar_frame.grid(row=1, column=0, sticky="nsw", padx=(10,0), pady=10)
        sidebar_frame.pack_propagate(False)

        self.tab_buttons = {}
        pages = [
            ("dashboard", "🏠 Dashboard"),
            ("clients", "👥 Clients"),
            ("files", "📁 Files"),
            ("analytics", "📈 Analytics")
        ]

        if PROCESS_MONITOR_AVAILABLE:
            pages.append(("processes", "🔍 Processes"))

        for page_id, page_label in pages:
            btn = tk.Button(sidebar_frame, text=page_label, 
                           command=lambda p=page_id: self._switch_page(p),
                           bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                           font=(ModernTheme.FONT_FAMILY, 12, 'bold'),
                           relief="flat", bd=0, padx=20, pady=15, anchor="w")
            btn.pack(side="top", fill="x", padx=5, pady=5)
            self.tab_buttons[page_id] = btn

    def _create_content_pages(self, parent: tk.Widget) -> None:
        """Create the content frames for each page."""
        self.content_area = tk.Frame(parent, bg=ModernTheme.PRIMARY_BG)
        self.content_area.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Create all page content frames
        self.tab_contents = {}
        self._create_dashboard_tab()
        self._create_clients_tab()
        self._create_files_tab()
        self._create_analytics_tab()

        if PROCESS_MONITOR_AVAILABLE:
            self._create_process_monitor_tab()

        # Show dashboard by default
        self._switch_page("dashboard")

    def _switch_page(self, page_id: str) -> None:
        """Switch between content pages."""
        # Update button appearance
        for pid, btn in self.tab_buttons.items():
            if pid == page_id:
                btn.configure(bg=ModernTheme.ACCENT_BLUE)
            else:
                btn.configure(bg=ModernTheme.SECONDARY_BG)

        # Hide all tabs
        for content in self.tab_contents.values():
            content.pack_forget()

        # Show selected tab
        if page_id in self.tab_contents:
            self.tab_contents[page_id].pack(fill="both", expand=True)
            self.current_tab = page_id

            # Update data for specific tabs
            if page_id == "clients":
                self._refresh_client_table()
            elif page_id == "files":
                self._refresh_file_table()
            elif page_id == "analytics":
                self._update_analytics_charts()

    def _create_dashboard_tab(self) -> None:
        """Create dashboard tab content"""
        dashboard = tk.Frame(self.content_area, bg=ModernTheme.PRIMARY_BG)
        self.tab_contents["dashboard"] = dashboard

        # Create scrollable container
        canvas = tk.Canvas(dashboard, bg=ModernTheme.PRIMARY_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(dashboard, orient="vertical", command=canvas.yview,  # type: ignore
                               bg=ModernTheme.ACCENT_BG, troughcolor=ModernTheme.SECONDARY_BG)

        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.PRIMARY_BG)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind canvas resize
        def on_canvas_configure(event: tk.Event) -> None:
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create dashboard layout
        self.dashboard_content_frame = scrollable_frame
        self._create_compact_two_column_layout(self.dashboard_content_frame)
        # Guard bind call in case root is None to satisfy static analyzers
        if self.root is not None:
            self.root.bind("<Configure>", self._check_layout)

    def _create_clients_tab(self) -> None:
        """Create clients tab content"""
        clients_tab = tk.Frame(self.content_area, bg=ModernTheme.PRIMARY_BG)
        self.tab_contents["clients"] = clients_tab

        # Client management card
        client_card = ModernCard(clients_tab, title="👥 Client Management")
        client_card.pack(fill="both", expand=True, padx=5, pady=5)

        # Paned window for table and detail pane
        paned_window = cast(tk.PanedWindow, tk.PanedWindow(client_card.content_frame, orient=tk.HORIZONTAL, bg=ModernTheme.CARD_BG, sashwidth=8))
        paned_window.pack(fill="both", expand=True, padx=10, pady=10)

        # Client table
        columns = {
            'name': {'text': 'Client Name', 'width': 200},
            'id': {'text': 'Client ID', 'width': 300},
            'status': {'text': 'Status', 'width': 100},
            'last_seen': {'text': 'Last Seen', 'width': 200},
            'files': {'text': 'Files', 'width': 80}
        }

        self.client_table = ModernTable(paned_window, columns)
        cast(Any, paned_window).add(self.client_table, width=800)

        # Detail Pane
        self.client_detail_pane = DetailPane(paned_window, title="Client Details")
        cast(Any, paned_window).add(self.client_detail_pane)

        self.client_table.set_selection_callback(self._on_client_selected)

    def _create_files_tab(self) -> None:
        """Create files tab content"""
        files_tab = tk.Frame(self.content_area, bg=ModernTheme.PRIMARY_BG)
        self.tab_contents["files"] = files_tab

        # File management card
        file_card = ModernCard(files_tab, title="📁 File Management")
        file_card.pack(fill="both", expand=True, padx=5, pady=5)

        # Paned window for table and detail pane
        paned_window = cast(tk.PanedWindow, tk.PanedWindow(file_card.content_frame, orient=tk.HORIZONTAL, bg=ModernTheme.CARD_BG, sashwidth=8))
        paned_window.pack(fill="both", expand=True, padx=10, pady=10)

        # File table
        columns = {
            'filename': {'text': 'File Name', 'width': 250},
            'client': {'text': 'Client', 'width': 150},
            'size': {'text': 'Size', 'width': 100},
            'date': {'text': 'Date', 'width': 150},
            'verified': {'text': 'Verified', 'width': 80},
            'path': {'text': 'Path', 'width': 200}
        }

        self.file_table = ModernTable(paned_window, columns)
        cast(Any, paned_window).add(self.file_table, width=800)

        # Detail Pane
        self.file_detail_pane = DetailPane(paned_window, title="File Details")
        cast(Any, paned_window).add(self.file_detail_pane)

        self.file_table.set_selection_callback(self._on_file_selected)

    def _create_analytics_tab(self) -> None:
        """Create analytics tab content"""
        analytics_tab = tk.Frame(self.content_area, bg=ModernTheme.PRIMARY_BG)
        self.tab_contents["analytics"] = analytics_tab

        # Add date range filter
        filter_frame = tk.Frame(analytics_tab, bg=ModernTheme.CARD_BG)
        filter_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(filter_frame, text="From:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY).pack(side="left", padx=(10,5), pady=10)
        # Create a safe date entry widget (tkcalendar.DateEntry when available)
        self.start_date_entry = self._make_date_entry(filter_frame, width=12, background=ModernTheme.ACCENT_BLUE, foreground='white', borderwidth=2)
        self.start_date_entry.pack(side="left", pady=10)

        tk.Label(filter_frame, text="To:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY).pack(side="left", padx=(20,5), pady=10)
        self.end_date_entry = self._make_date_entry(filter_frame, width=12, background=ModernTheme.ACCENT_BLUE, foreground='white', borderwidth=2)
        self.end_date_entry.pack(side="left", pady=10)

        filter_btn = tk.Button(filter_frame, text="Filter", command=self._apply_analytics_filter, bg=ModernTheme.SUCCESS, fg=ModernTheme.TEXT_PRIMARY)
        filter_btn.pack(side="left", padx=20, pady=10)

        # Create grid layout
        charts_frame = tk.Frame(analytics_tab, bg=ModernTheme.PRIMARY_BG)
        charts_frame.pack(fill="both", expand=True)
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        charts_frame.grid_rowconfigure(1, weight=1)

        # Performance chart
        perf_card = ModernCard(charts_frame, title="[PERF] System Performance")
        perf_card.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        if perf_card.content_frame is not None:
            self.performance_chart = ModernChart(perf_card.content_frame, chart_type="line")
            self.performance_chart.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            self.performance_chart = None

        # Transfer volume chart
        transfer_card = ModernCard(analytics_tab, title="📊 Transfer Volume")
        transfer_card.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        if transfer_card.content_frame is not None:
            self.transfer_chart = ModernChart(transfer_card.content_frame, chart_type="line")
            self.transfer_chart.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            self.transfer_chart = None

        # Client connections chart
        client_card = ModernCard(analytics_tab, title="👥 Client Activity")
        client_card.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        if client_card.content_frame is not None:
            self.client_chart = ModernChart(client_card.content_frame, chart_type="bar")
            self.client_chart.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            self.client_chart = None

        # Summary statistics
        stats_card = ModernCard(analytics_tab, title="📈 Summary Statistics")
        stats_card.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        if stats_card.content_frame is not None:
            self._create_summary_stats(stats_card.content_frame)
        else:
            print("Warning: Could not create summary stats - content frame is None")

    def _create_summary_stats(self, parent: tk.Widget) -> None:
        """Create summary statistics panel"""
        stats_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.stats_labels: Dict[str, tk.Label] = {}
        stats = [
            ('total_files', '📁 Total Files:', '0'),
            ('total_size', '💾 Total Size:', '0 MB'),
            ('avg_file_size', '📊 Avg File Size:', '0 MB'),
            ('success_rate', 'Success Rate:', '100%'),
            ('peak_clients', '👥 Peak Clients:', '0'),
            ('uptime_days', '⏰ Uptime:', '0 days')
        ]

        for stat_id, label_text, default_value in stats:
            stat_frame = tk.Frame(stats_frame, bg=ModernTheme.CARD_BG)
            stat_frame.pack(fill="x", pady=5)

            label = tk.Label(stat_frame, text=label_text, bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.TEXT_SECONDARY, font=(ModernTheme.FONT_FAMILY, 11))
            label.pack(side="left")

            value_label = tk.Label(stat_frame, text=default_value, bg=ModernTheme.CARD_BG,
                                 fg=ModernTheme.ACCENT_BLUE, font=(ModernTheme.FONT_FAMILY, 11, 'bold'))
            value_label.pack(side="right")
            self.stats_labels[stat_id] = value_label

    def _create_process_monitor_tab(self) -> None:
        """Create process monitoring tab content"""
        if not PROCESS_MONITOR_AVAILABLE:
            return

        process_tab = tk.Frame(self.content_area, bg=ModernTheme.PRIMARY_BG)
        self.tab_contents["processes"] = process_tab

        # Create main container with padding
        main_container = tk.Frame(process_tab, bg=ModernTheme.PRIMARY_BG)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            main_container,
            text="🔍 Process Monitoring",
            font=("Segoe UI", 16, "bold"),
            bg=ModernTheme.PRIMARY_BG,
            fg=ModernTheme.TEXT_PRIMARY
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Create process monitor widget - Fixed availability check
        try:
            if PROCESS_MONITOR_AVAILABLE and ProcessMonitorWidget is not None:
                self.process_monitor_widget = ProcessMonitorWidget(
                    main_container,
                    title="Active Backup Processes",
                    update_interval=3.0
                )
                self.process_monitor_widget.pack(fill="both", expand=True)
            else:
                # Fallback when process monitor is not available
                error_label = tk.Label(
                    main_container,
                    text="Process monitoring not available\n(ProcessMonitorWidget not installed)",
                    font=("Segoe UI", 12),
                    bg=ModernTheme.PRIMARY_BG,
                    fg=ModernTheme.TEXT_SECONDARY
                )
                error_label.pack(pady=50)

        except Exception as e:
            # Fallback if process monitor widget fails
            error_label = tk.Label(
                main_container,
                text=f"Process monitoring unavailable: {e}",
                font=("Segoe UI", 12),
                bg=ModernTheme.PRIMARY_BG,
                fg=ModernTheme.TEXT_SECONDARY
            )
            error_label.pack(pady=50)

    def _create_compact_two_column_layout(self, parent: tk.Widget) -> None:
        """Create a compact two-column layout for dashboard"""
        # Main container with two columns
        main_container = tk.Frame(parent, bg=ModernTheme.PRIMARY_BG)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Configure grid weights for responsive columns
        main_container.columnconfigure(0, weight=1, uniform="group1")
        main_container.columnconfigure(1, weight=1, uniform="group1")
        main_container.rowconfigure(0, weight=1)

        # Left Column
        left_column = tk.Frame(main_container, bg=ModernTheme.PRIMARY_BG)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Right Column
        right_column = tk.Frame(main_container, bg=ModernTheme.PRIMARY_BG)
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # LEFT COLUMN CONTENT (Primary Stats)
        self._create_compact_server_status_card(left_column)
        self._create_compact_client_stats_card(left_column)
        self._create_compact_transfer_stats_card(left_column)
        self._create_compact_performance_card(left_column)

        # RIGHT COLUMN CONTENT (Secondary Info & Controls)
        self._create_enhanced_control_panel(right_column)
        self._create_live_transfer_feed(right_column) # New live feed
        self._create_compact_maintenance_card(right_column)
        self._create_compact_activity_log_card(right_column)
        self._create_compact_status_message_card(right_column)

    def _create_info_row(self, parent: tk.Widget, label_text: str, key: str, default_text: str, text_color: Optional[str] = None) -> None:
        """Create a consistent info row with label and value."""
        row_frame = tk.Frame(parent, bg=ModernTheme.GLASS_BG)
        row_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(row_frame, text=f"{label_text}:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels[key] = tk.Label(row_frame, text=default_text,
                                          bg=ModernTheme.GLASS_BG, 
                                          fg=text_color or ModernTheme.TEXT_PRIMARY,
                                          font=(ModernTheme.FONT_FAMILY, 9, 'bold' if text_color else 'normal'))
        self.status_labels[key].pack(side="right")

    def _create_compact_server_status_card(self, parent: tk.Widget) -> None:
        """Create compact server status card with glass morphism"""
        card = GlassMorphismCard(parent, title="Server Status")
        card.pack(fill="x", pady=(0, 8), padx=3)

        # Create status info rows using helper method
        if card.content_frame:
            self._create_info_row(card.content_frame, "Status", 'status', "🛑 Stopped", ModernTheme.ERROR)
            self._create_info_row(card.content_frame, "Address", 'address', "🌐 Not configured")

        # Uptime
        uptime_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        uptime_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(uptime_frame, text="Uptime:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY,  9)).pack(side="left")
        self.status_labels['uptime'] = tk.Label(uptime_frame, text="Uptime: 00:00:00",
                                              bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_PRIMARY,
                                              font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['uptime'].pack(side="right")

    def _check_layout(self, event: tk.Event) -> None:
        """Check the window size and adjust the layout accordingly."""
        if self.dashboard_content_frame is None or not self.dashboard_content_frame.winfo_exists():
            return

        width = event.width
        # Clear the dashboard content frame before re-drawing
        for widget in self.dashboard_content_frame.winfo_children():
            widget.destroy()

        if width < 900: # Threshold for switching to single column
            self._create_compact_single_column_layout(self.dashboard_content_frame)
        else:
            self._create_compact_two_column_layout(self.dashboard_content_frame)

    def _create_compact_single_column_layout(self, parent: tk.Widget) -> None:
        """Create a single-column layout for smaller window sizes."""
        main_container = tk.Frame(parent, bg=ModernTheme.PRIMARY_BG)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)

        self._create_compact_server_status_card(main_container)
        self._create_compact_client_stats_card(main_container)
        self._create_compact_transfer_stats_card(main_container)
        self._create_compact_performance_card(main_container)
        self._create_enhanced_control_panel(main_container)
        self._create_live_transfer_feed(main_container)
        self._create_compact_maintenance_card(main_container)
        self._create_compact_activity_log_card(main_container)
        self._create_compact_status_message_card(main_container)

    def _create_compact_client_stats_card(self, parent: tk.Widget) -> None:
        """Create compact client statistics card with glass morphism"""
        card = GlassMorphismCard(parent, title="👥 Client Statistics")
        card.pack(fill="x", pady=(0, 8), padx=3)

        # Create client info rows using helper method
        if card.content_frame:
            self._create_info_row(card.content_frame, "Connected", 'connected', "0", ModernTheme.ACCENT_BLUE)
            self._create_info_row(card.content_frame, "Total Registered", 'total', "0")
            self._create_info_row(card.content_frame, "Active Transfers", 'active_transfers', "0", ModernTheme.ACCENT_GREEN)

    def _create_compact_transfer_stats_card(self, parent: tk.Widget) -> None:
        """Create compact transfer statistics card with glass morphism"""
        card = GlassMorphismCard(parent, title="📊 Transfer Statistics")
        card.pack(fill="x", pady=(0, 8), padx=3)

        # Bytes transferred
        bytes_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        bytes_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(bytes_frame, text="Bytes Transferred:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['bytes'] = tk.Label(bytes_frame, text="0 B", bg=ModernTheme.GLASS_BG,
                                              fg=ModernTheme.ACCENT_PURPLE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['bytes'].pack(side="right")

        # Transfer rate
        if card.content_frame is not None:
            rate_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        else:
            return
        rate_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(rate_frame, text="Transfer Rate:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['transfer_rate'] = tk.Label(rate_frame, text="0 KB/s", bg=ModernTheme.GLASS_BG,
                                                      fg=ModernTheme.ACCENT_ORANGE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['transfer_rate'].pack(side="right")

        # Last activity
        activity_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        activity_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(activity_frame, text="Last Activity:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['activity'] = tk.Label(activity_frame, text="None", bg=ModernTheme.GLASS_BG,
                                                 fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['activity'].pack(side="right")

    def _create_live_transfer_feed(self, parent: tk.Widget) -> None:
        """Create the live transfer feed card on the dashboard."""
        card = ModernCard(parent, title="⚡ Live Transfers")
        card.pack(fill="x", pady=(0, 8), padx=3)

        if card.content_frame:
            columns = {
                'client': {'text': 'Client', 'width': 120},
                'file': {'text': 'File', 'width': 180},
                'progress': {'text': 'Progress', 'width': 100}
            }
            self.live_transfer_table = ModernTable(card.content_frame, columns)
            self.live_transfer_table.pack(fill="both", expand=True, padx=5, pady=5)
            # We will need a way to update this table with live data later

    def _on_global_search(self, *args: Any) -> None:
        """Handle global search text change."""
        # Placeholder for future search logic implementation
        search_query = self.global_search_var.get()
        if search_query and search_query != "🔍 Search clients, files, logs...":
            print(f"Global search for: {search_query}")
            # Here we would trigger a search across different data sources

    def _on_search_focus_in(self, event: tk.Event) -> None:
        """Clear placeholder text on focus."""
        if self.global_search_var.get() == "🔍 Search clients, files, logs...":
            self.global_search_var.set("")
            if isinstance(event.widget, tk.Entry):
                event.widget.config(fg=ModernTheme.TEXT_PRIMARY)

    def _on_search_focus_out(self, event: tk.Event) -> None:
        """Restore placeholder text if empty."""
        if not self.global_search_var.get():
            self.global_search_var.set("🔍 Search clients, files, logs...")
            if isinstance(event.widget, tk.Entry):
                event.widget.config(fg=ModernTheme.TEXT_SECONDARY)

    def _create_compact_performance_card(self, parent: tk.Widget) -> None:
        """Create compact performance monitoring card with real data"""
        card = ModernCard(parent, title="[PERF] Performance Monitor") # Changed to ModernCard
        card.pack(fill="x", pady=(0, 8), padx=3)

        # CPU Usage with mini progress bar
        if card.content_frame is not None:
            cpu_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)  # Changed to card.content_frame
        else:
            return
        cpu_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(cpu_frame, text="CPU:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['cpu_usage'] = tk.Label(cpu_frame, text="0%", bg=ModernTheme.CARD_BG,
                                                  fg=ModernTheme.ACCENT_GREEN, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['cpu_usage'].pack(side="right")

        if card.content_frame is not None:
            self.advanced_progress_bars['cpu'] = AdvancedProgressBar(card.content_frame, width=200, height=12)  # Changed to card.content_frame
        self.advanced_progress_bars['cpu'].pack(padx=10, pady=(0, 3))

        # Memory Usage with mini progress bar
        if card.content_frame is not None:
            mem_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)  # Changed to card.content_frame
        else:
            return
        mem_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(mem_frame, text="Memory:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['memory_usage'] = tk.Label(mem_frame, text="0%", bg=ModernTheme.CARD_BG,
                                                     fg=ModernTheme.ACCENT_PURPLE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['memory_usage'].pack(side="right")

        if card.content_frame is not None:
            self.advanced_progress_bars['memory'] = AdvancedProgressBar(card.content_frame, width=200, height=12)  # Changed to card.content_frame
        self.advanced_progress_bars['memory'].pack(padx=10, pady=(0, 3))

        # Disk Usage
        disk_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        disk_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(disk_frame, text="Disk:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['disk_usage'] = tk.Label(disk_frame, text="0%", bg=ModernTheme.CARD_BG,
                                                   fg=ModernTheme.ACCENT_ORANGE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['disk_usage'].pack(side="right")

        self.advanced_progress_bars['disk'] = AdvancedProgressBar(card.content_frame, width=200, height=12) # Changed to card.content_frame
        self.advanced_progress_bars['disk'].pack(padx=10, pady=(0, 3))

        # Network Activity
        net_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        net_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(net_frame, text="Network:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['network_activity'] = tk.Label(net_frame, text="Idle", bg=ModernTheme.CARD_BG,
                                                         fg=ModernTheme.ACCENT_BLUE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['network_activity'].pack(side="right")

    def _create_compact_maintenance_card(self, parent: tk.Widget) -> None:
        """Create compact maintenance statistics card"""
        card = ModernCard(parent, title="Maintenance") # Changed to ModernCard
        card.pack(fill="x", pady=(0, 8), padx=3)

        # Files cleaned
        files_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        files_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(files_frame, text="Files Cleaned:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['files_cleaned'] = tk.Label(files_frame, text="0", bg=ModernTheme.CARD_BG,
                                                      fg=ModernTheme.ACCENT_ORANGE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['files_cleaned'].pack(side="right")

        # Partial files cleaned
        partial_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        partial_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(partial_frame, text="Partial Files:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['partial_cleaned'] = tk.Label(partial_frame, text="0", bg=ModernTheme.CARD_BG,
                                                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['partial_cleaned'].pack(side="right")

        # Clients cleaned
        clients_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        clients_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(clients_frame, text="Clients Cleaned:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['clients_cleaned'] = tk.Label(clients_frame, text="0", bg=ModernTheme.CARD_BG,
                                                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['clients_cleaned'].pack(side="right")

        # Last cleanup
        cleanup_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        cleanup_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(cleanup_frame, text="Last Cleanup:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['last_cleanup'] = tk.Label(cleanup_frame, text="Never", bg=ModernTheme.CARD_BG,
                                                     fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['last_cleanup'].pack(side="right")

    def _create_compact_activity_log_card(self, parent: Any) -> None:
        """Create compact activity log card"""
        card = ModernCard(parent, title="📋 Activity Log") # Changed to ModernCard
        card.pack(fill="x", pady=(0, 8), padx=3)

        title_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        title_frame.pack(fill="x", padx=10, pady=(8, 5))

        title = tk.Label(title_frame, text="📋 Activity Log", bg=ModernTheme.CARD_BG,
                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 12, 'bold'))
        title.pack(side="left")

        # Clear log button (smaller)
        clear_btn = tk.Button(title_frame, text="Clear", command=self._clear_activity_log,
                             bg=ModernTheme.WARNING, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 8, 'bold'), relief="flat", bd=0, padx=5, pady=2)
        clear_btn.pack(side="right")

        # Compact scrollable text area
        log_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        log_frame.pack(fill="x", padx=10, pady=(0, 8))

        scrollbar = tk.Scrollbar(log_frame, bg=ModernTheme.ACCENT_BG, width=12)
        scrollbar.pack(side="right", fill="y")

        self.activity_log_text = tk.Text(log_frame, height=4, bg=ModernTheme.SECONDARY_BG,
                                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 8),
                                        yscrollcommand=scrollbar.set, wrap="word", relief="flat", bd=0)
        self.activity_log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.activity_log_text.yview)  # type: ignore

        self._add_activity_log("[SYSTEM] Enhanced Ultra Modern GUI System Initialized")

    def _create_compact_status_message_card(self, parent: Any) -> None:
        """Create compact status message card"""
        card = ModernCard(parent, title="📢 Status") # Changed to ModernCard
        card.pack(fill="x", pady=(0, 8), padx=3)

        title = tk.Label(card.content_frame, text="📢 Status", bg=ModernTheme.CARD_BG, # Changed to card.content_frame
                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 12, 'bold'))
        title.pack(anchor="w", padx=10, pady=(8, 5))

        self.status_labels['error'] = tk.Label(card.content_frame, text="[READY] Ready", bg=ModernTheme.CARD_BG, # Changed to card.content_frame
                                              fg=ModernTheme.SUCCESS, font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['error'].pack(padx=10, pady=(5, 8), anchor="w")

    def _create_enhanced_control_panel(self, parent: Any) -> None:
        """Create enhanced compact control panel"""
        card = ModernCard(parent, title="🎛️ Control Panel") # Changed to ModernCard
        card.pack(fill="x", pady=(0, 8), padx=3)

        # Compact button grid
        button_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        button_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure grid
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.rowconfigure(0, weight=1)
        button_frame.rowconfigure(1, weight=1)
        button_frame.rowconfigure(2, weight=1)

        # Row 1
        start_btn = self._create_modern_button(button_frame, "▶️ Start Server", self._start_server, ModernTheme.SUCCESS)  # type: ignore
        start_btn.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0,5))
        ModernTooltip(start_btn, "Start the main backup server")

        stop_btn = self._create_modern_button(button_frame, "⏹️ Stop Server", self._stop_server, ModernTheme.ERROR)  # type: ignore
        stop_btn.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0,5))
        ModernTooltip(stop_btn, "Stop the server gracefully")

        # Row 2
        settings_btn = self._create_modern_button(button_frame, "[SETTINGS] Settings", self._show_settings, ModernTheme.ACCENT_BLUE)  # type: ignore
        settings_btn.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(5,5))
        ModernTooltip(settings_btn, "Configure server settings")

        restart_btn = self._create_modern_button(button_frame, "🔄 Restart Server", self._restart_server, ModernTheme.WARNING)  # type: ignore
        restart_btn.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5,5))
        ModernTooltip(restart_btn, "Restart the server")

        # Row 3
        analytics_btn = self._create_modern_button(button_frame, "📈 Analytics", lambda: self._switch_tab("analytics"), ModernTheme.ACCENT_PURPLE)  # type: ignore
        analytics_btn.grid(row=2, column=0, sticky="nsew", padx=(0, 5), pady=(5,0))
        ModernTooltip(analytics_btn, "View performance and usage analytics")

        exit_btn = self._create_modern_button(button_frame, "[EXIT] Exit Application", self._exit_server, ModernTheme.TEXT_SECONDARY)  # type: ignore
        exit_btn.grid(row=2, column=1, sticky="nsew", padx=(5, 0), pady=(5,0))
        ModernTooltip(exit_btn, "Exit the GUI application")

    def _create_modern_button(self, parent: Any, text: str, command: Callable, bg_color: str) -> tk.Button:
        """Helper to create a modern button."""
        return tk.Button(parent, text=text, command=command,
                        bg=bg_color, fg=ModernTheme.TEXT_PRIMARY,
                        font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                        relief="flat", bd=0, padx=15, pady=8)

    def _start_server(self):
        """Start the backup server."""
        from python_server.server.server import BackupServer # Local import to avoid circular dependency # type: ignore
# Cleaned up duplicate import
        
        if not self.server:
            if self.toast_system:
                self.toast_system.show_toast("Server instance not available. Please start the server using 'python server.py'", "error")
            self._add_activity_log("[ERROR] Server instance not available. Use 'python server.py' to start properly.")
            return
            
        if hasattr(self.server, 'running') and self.server.running and self.toast_system:
            self.toast_system.show_toast("Server is already running.", "warning")
            return
            
        try:
            # The server's start method is already designed to run in threads
            if hasattr(self.server, 'start'):
                self.server.start()
            if self.toast_system:
                self.toast_system.show_toast("Server starting...", "info")
            self._add_activity_log("Server start command issued.")
            # The server will update its own status, which will be reflected in the GUI
        except Exception as e:
            if self.toast_system:
                self.toast_system.show_toast(f"Failed to start server: {e}", "error")
            self._add_activity_log(f"Error starting server: {e}")

    def _stop_server(self):
        """Stop the backup server."""
        if self.server and hasattr(self.server, 'running') and self.server.running:
            try:
                if hasattr(self.server, 'stop'):
                    self.server.stop()
                if self.toast_system:
                    self.toast_system.show_toast("Server stopping...", "info")
                self._add_activity_log("Server stop command issued.")
            except Exception as e:
                if self.toast_system:
                    self.toast_system.show_toast(f"Failed to stop server: {e}", "error")
                self._add_activity_log(f"Error stopping server: {e}")
        elif self.server:
            if self.toast_system:
                self.toast_system.show_toast("Server is not running.", "warning")
        elif self.toast_system:
            self.toast_system.show_toast("Server instance not available.", "error")

    def _restart_server(self):
        """Restart the server."""
        if self.server:
            if self.toast_system:
                self.toast_system.show_toast("Restarting server...", "info")
            if hasattr(self.server, 'stop'):
                self.server.stop()
            # Give it a moment to truly stop
            time.sleep(1)
            if hasattr(self.server, 'start'):
                self.server.start()
            self._add_activity_log("Server restarted.")
        elif self.toast_system:
            self.toast_system.show_toast("Server instance not available.", "warning")

    def _show_settings(self):
        """Show settings dialog."""
        if self.server and self.root:
            dialog = SettingsDialog(self.root, self.settings)
            if new_settings := dialog.show():
                self.settings = new_settings
                # Apply new settings to server if it's running
                if (hasattr(self.server, 'running') and self.server.running and 
                    hasattr(self.server, 'apply_settings')):
                    self.server.apply_settings(self.settings)  # Assuming BackupServer has apply_settings
                if self.toast_system:
                    self.toast_system.show_toast("Settings saved and applied!", "success")
                self._add_activity_log("Server settings updated.")
            elif self.toast_system:
                self.toast_system.show_toast("Settings dialog cancelled.", "info")
        elif self.toast_system:
            self.toast_system.show_toast("Server instance not available to configure.", "error")

    def _export_clients(self):
        """Export client data to CSV."""
        if (self.server and hasattr(self.server, 'db_manager') and 
            self.server.db_manager):
            try:
                clients = self.server.db_manager.get_all_clients()
                if not clients:
                    if self.toast_system:
                        self.toast_system.show_toast("No client data to export.", "warning")
                    return

                if file_path := filedialog.asksaveasfilename(defaultextension=".csv",
                                                       filetypes=[("CSV files", "*.csv")],
                                                       title="Export Clients to CSV"):
                    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                        fieldnames = ['id', 'name', 'last_seen']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        for client in clients:
                            writer.writerow(client)
                    if self.toast_system:
                        self.toast_system.show_toast(f"Clients exported to {file_path}", "success")
                    self._add_activity_log(f"Exported client data to {file_path}")
            except Exception as e:
                if self.toast_system:
                    self.toast_system.show_toast(f"Error exporting clients: {e}", "error")
                self._add_activity_log(f"Error exporting clients: {e}")
        elif self.toast_system:
            self.toast_system.show_toast("Server or database not available.", "error")

    def _export_selected_clients(self):
        """Export selected client data to CSV."""
        if not self.client_table:
            if self.toast_system: self.toast_system.show_toast("Client table not available.", "error")
            return

        selected_clients = self.client_table.get_selected_items()
        if not selected_clients:
            if self.toast_system: self.toast_system.show_toast("No clients selected to export.", "warning")
            return

        if file_path := filedialog.asksaveasfilename(defaultextension=".csv",
                                                   filetypes=[("CSV files", "*.csv")],
                                                   title="Export Selected Clients to CSV"):
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    # Note: We are exporting the formatted data from the table directly
                    fieldnames = list(selected_clients[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(selected_clients)
                if self.toast_system: self.toast_system.show_toast(f"Selected clients exported to {file_path}", "success")
                self._add_activity_log(f"Exported {len(selected_clients)} clients to {file_path}")
            except Exception as e:
                if self.toast_system: self.toast_system.show_toast(f"Error exporting selected clients: {e}", "error")
                self._add_activity_log(f"Error exporting selected clients: {e}")

    def _export_files(self):
        """Export file data to CSV."""
        if (self.server and hasattr(self.server, 'db_manager') and 
            self.server.db_manager):
            try:
                files = self.server.db_manager.get_all_files()
                if not files:
                    if self.toast_system:
                        self.toast_system.show_toast("No file data to export.", "warning")
                    return

                if file_path := filedialog.asksaveasfilename(defaultextension=".csv",
                                                       filetypes=[("CSV files", "*.csv")],
                                                       title="Export Files to CSV"):
                    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                        fieldnames = ['filename', 'client', 'size', 'date', 'verified', 'path']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        for f in files:
                            writer.writerow(f)
                    if self.toast_system:
                        self.toast_system.show_toast(f"Files exported to {file_path}", "success")
                    self._add_activity_log(f"Exported file data to {file_path}")
            except Exception as e:
                if self.toast_system:
                    self.toast_system.show_toast(f"Error exporting files: {e}", "error")
                self._add_activity_log(f"Error exporting files: {e}")
        elif self.toast_system:
            self.toast_system.show_toast("Server or database not available.", "error")

    def _create_backup_filename(self, backup_dir: str) -> str:
        """Create a timestamped backup filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"defensive_backup_{timestamp}.db"
        return os.path.join(backup_dir, backup_filename)

    def _backup_database(self):
        """Create a backup of the SQLite database."""
        if (self.server and hasattr(self.server, 'db_manager') and 
            self.server.db_manager):
            try:
                if backup_dir := filedialog.askdirectory(title="Select Backup Directory"):
                    backup_path = self._create_backup_filename(backup_dir)
                    shutil.copy2(self.db_path, backup_path)
                    if self.toast_system:
                        self.toast_system.show_toast(f"Database backed up to {backup_path}", "success")
                    self._add_activity_log(f"Database backed up to {backup_path}")
            except Exception as e:
                if self.toast_system:
                    self.toast_system.show_toast(f"Error backing up database: {e}", "error")
                self._add_activity_log(f"Error backing up database: {e}")
        elif self.toast_system:
            self.toast_system.show_toast("Server or database not available.", "error")

    def _exit_server(self):
        """Exit the application."""
        if self.root:
            self.root.quit()

    def _clear_activity_log(self):
        """Clear the activity log display."""
        self.activity_log.clear()
        if self.activity_log_text is not None:
            self.activity_log_text.config(state=tk.NORMAL)
            self.activity_log_text.delete(1.0, tk.END)
            self.activity_log_text.config(state=tk.DISABLED)
        self._add_activity_log("Activity log cleared.")
        if self.toast_system:
            self.toast_system.show_toast("Activity log cleared.", "info")

    def _show_documentation(self):
        """Open documentation."""
        if self.toast_system:
            self.toast_system.show_toast("Documentation not yet implemented.", "info")

    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", "Encrypted Backup Server GUI\nVersion 1.0\nDeveloped by Gemini")

    def _add_activity_log(self, message: str):
        """Add a message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.activity_log.append(log_entry)  # type: ignore
        if (self.activity_log_text is not None and 
            hasattr(self.activity_log_text, 'config') and 
            hasattr(self.activity_log_text, 'insert')):
            self.activity_log_text.config(state=tk.NORMAL)
            self.activity_log_text.insert(tk.END, log_entry + "\n")
            if hasattr(self.activity_log_text, 'see'):
                self.activity_log_text.see(tk.END)
            self.activity_log_text.config(state=tk.DISABLED)
        logging.info(message) # Also log to console/file

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in H:M:S."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _update_clock(self):
        """Update the real-time clock display."""
        if self.clock_label is not None:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.clock_label.config(text=now)

    def _update_status_label(self, key: str, text: str) -> None:
        """Update a status label if it exists."""
        if key in self.status_labels:
            self.status_labels[key].config(text=text)

    def _update_performance_metrics(self, performance_data: Optional[Dict[str, Any]] = None):
        """Update performance metrics on the dashboard."""
        if not SYSTEM_MONITOR_AVAILABLE:
            # Disable performance monitoring entirely when psutil is not available
            if 'cpu_usage' in self.status_labels:
                self.status_labels['cpu_usage'].config(text="N/A")
            if 'memory_usage' in self.status_labels:
                self.status_labels['memory_usage'].config(text="N/A")
            if 'disk_usage' in self.status_labels:
                self.status_labels['disk_usage'].config(text="N/A")
            if 'network_activity' in self.status_labels:
                self.status_labels['network_activity'].config(text="Disabled")

            # Disable progress bars
            for key in ['cpu', 'memory', 'disk']:
                if key in self.advanced_progress_bars:
                    self.advanced_progress_bars[key].set_progress(0, animated=False)
            return

        try:
            # Get real system stats with comprehensive error handling
            if not SYSTEM_MONITOR_AVAILABLE or psutil is None:
                # Fallback when psutil is not available
                cpu_percent = 0
                mem_percent = 0
                disk_usage_percent = None
                network_status = "N/A"
            else:
                cpu_percent = psutil.cpu_percent(interval=None)  # Non-blocking call
                memory_info = psutil.virtual_memory()
                mem_percent = memory_info.percent

                # Find the disk usage for the drive where the script is running
                try:
                    script_path = os.path.abspath(sys.argv[0])
                    disk_path = os.path.splitdrive(script_path)[0] or '/'
                    disk_usage = psutil.disk_usage(disk_path)
                    disk_usage_percent = disk_usage.percent
                except Exception as disk_error:
                    print(f"Warning: Failed to get disk usage: {disk_error}")
                    disk_usage_percent = None

            # Network activity monitoring
            try:
                # Add proper bounds checking for psutil
                if SYSTEM_MONITOR_AVAILABLE and psutil is not None:
                    network_stats = psutil.net_io_counters()
                    if self.last_network_bytes is not None:
                        bytes_diff = (network_stats.bytes_sent + network_stats.bytes_recv) - self.last_network_bytes
                        if bytes_diff > 1024:  # More than 1KB activity
                            network_status = f"Active ({bytes_diff//1024}KB/s)"
                        else:
                            network_status = "Idle"
                    else:
                        network_status = "Monitoring..."
                    self.last_network_bytes = int(network_stats.bytes_sent + network_stats.bytes_recv)
                else:
                    network_status = "N/A"
            except Exception as net_error:
                print(f"Warning: Failed to get network stats: {net_error}")
                network_status = "N/A"

        except Exception as e:
            print(f"Critical error getting system metrics: {e}")
            # If psutil fails completely, disable monitoring
            self._update_status_label('cpu_usage', "Error")
            self._update_status_label('memory_usage', "Error") 
            self._update_status_label('disk_usage', "Error")
            self._update_status_label('network_activity', "Error")
            return

        # Update labels with real data only
        self._update_status_label('cpu_usage', f"{cpu_percent:.1f}%")
        if 'memory_usage' in self.status_labels:
            self.status_labels['memory_usage'].config(text=f"{mem_percent:.1f}%")
        if 'disk_usage' in self.status_labels and disk_usage_percent is not None:
            self.status_labels['disk_usage'].config(text=f"{disk_usage_percent:.1f}%")
        elif 'disk_usage' in self.status_labels:
            self.status_labels['disk_usage'].config(text="N/A")
        if 'network_activity' in self.status_labels:
            self.status_labels['network_activity'].config(text=network_status)

        # Update progress bars with real data only
        if 'cpu' in self.advanced_progress_bars:
            self.advanced_progress_bars['cpu'].set_progress(cpu_percent)
        if 'memory' in self.advanced_progress_bars:
            self.advanced_progress_bars['memory'].set_progress(mem_percent)
        if 'disk' in self.advanced_progress_bars and disk_usage_percent is not None:
            self.advanced_progress_bars['disk'].set_progress(disk_usage_percent)

        # Update performance data for charts with real data only
        now = datetime.now()
        if 'timestamps' in self.performance_data and hasattr(self.performance_data['timestamps'], 'append'):
            self.performance_data['timestamps'].append(now)
        if 'cpu_usage' in self.performance_data and hasattr(self.performance_data['cpu_usage'], 'append'):
            self.performance_data['cpu_usage'].append(cpu_percent)
        if 'memory_usage' in self.performance_data and hasattr(self.performance_data['memory_usage'], 'append'):
            self.performance_data['memory_usage'].append(mem_percent)

        # Update analytics charts if the tab is active
        if self.current_tab == "analytics":
            self._update_analytics_charts()

    def _update_analytics_charts(self):
        """Update the charts on the analytics tab with the latest data."""
        if not CHARTS_AVAILABLE:
            return

        # Performance Chart (CPU and Memory over time)
        if self.performance_chart:
            chart_data = {
                'CPU Usage (%)': (list(self.performance_data['timestamps']), list(self.performance_data['cpu_usage'])),
                'Memory Usage (%)': (list(self.performance_data['timestamps']), list(self.performance_data['memory_usage']))
            }
            self.performance_chart.update_data(chart_data, title="System Performance Over Time", xlabel="Time", ylabel="Usage (%)")

        # Transfer Volume Chart
        if (self.transfer_chart and self.server and hasattr(self.server, 'db_manager') and 
            self.server.db_manager and hasattr(self.server.db_manager, 'get_total_bytes_transferred')):
            total_bytes = self.server.db_manager.get_total_bytes_transferred()
            # This is a single value, so we'll display it as a bar chart.
            chart_data = {
                'Total MB Transferred': total_bytes / (1024*1024)
            }
            self.transfer_chart.update_data(chart_data, title="Total Verified Transfer Volume") # Removed chart_type

        # Client Activity Chart
        if self.client_chart:
            online_clients = self.status.clients_connected
            total_clients = self.status.total_clients
            offline_clients = total_clients - online_clients

            chart_data = {
                'Online': online_clients,
                'Offline': offline_clients
            }
            self.client_chart.update_data(chart_data, title="Client Status")

    def _apply_analytics_filter(self):
        """Apply the selected date range to the analytics charts."""
        # start_date_entry/end_date_entry may be DateEntry (has get_date) or Entry (has get)
        start_date = None
        end_date = None
        if self.start_date_entry is not None:
            if hasattr(self.start_date_entry, 'get_date'):
                start_date = self.start_date_entry.get_date()
            elif hasattr(self.start_date_entry, 'get'):
                start_date = self.start_date_entry.get()
        if self.end_date_entry is not None:
            if hasattr(self.end_date_entry, 'get_date'):
                end_date = self.end_date_entry.get_date()
            elif hasattr(self.end_date_entry, 'get'):
                end_date = self.end_date_entry.get()
        self._add_activity_log(f"Filtering analytics from {start_date} to {end_date}")
        # Safely show a toast about filtering
        with suppress(Exception):
            self._safe_toast(f"Filtering data from {start_date} to {end_date}", "info")
        # Placeholder for actual data filtering and chart updating logic
        self._update_analytics_charts()

    def _refresh_client_table(self):
        """Refresh the client table with data from the database."""
        if not (self.client_table and self.server):
            return
        
        self._populate_client_table()

    def _populate_client_table(self):
        """Populate the client table with current data."""
        if not (self.server and self.client_table):
            return
            
        try:
            if not (hasattr(self.server, 'db_manager') and self.server.db_manager):
                return
                
            clients = self.server.db_manager.get_all_clients()
            
            # Get online status from the server's in-memory client list
            if hasattr(self.server, 'clients'):
                online_client_ids = list(self.server.clients.keys())
            else:
                online_client_ids = []

            table_data: List[Dict[str, Any]] = []
            for client in clients:
                client_id_bytes = bytes.fromhex(client['id'])
                status = "🟢 Online" if client_id_bytes in online_client_ids else "[OFFLINE] Offline"
                
                table_data.append({
                    'name': client['name'],
                    'id': client['id'],
                    'status': status,
                    'last_seen': client['last_seen'],
                    'files': 'N/A' # Placeholder
                })
            
            self.client_table.set_data(table_data)
            self._add_activity_log("Client table refreshed.")
        except Exception as e:
            self._add_activity_log(f"Error refreshing client table: {e}")
            if self.toast_system is not None:
                self.toast_system.show_toast(f"Failed to refresh clients: {e}", "error")

    def _on_client_selected(self, selected_item: Optional[Dict[str, Any]]) -> None:
        """Handle client selection in the table."""
        if selected_item and hasattr(self, 'client_detail_pane') and self.client_detail_pane:
            self.client_detail_pane.update_details(selected_item)
        elif hasattr(self, 'client_detail_pane') and self.client_detail_pane:
            self.client_detail_pane.clear_details()

    def _show_client_details(self):
        """Show details for the selected client."""
        if self.client_table:
            selected = self.client_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No client selected", "warning")
                return
            
            # For now, just show a message box with the client info
            client_info = selected[0]
            messagebox.showinfo("Client Details", json.dumps(client_info, indent=2))
        elif self.toast_system:
            self.toast_system.show_toast("Client table not initialized.", "error")

    def _disconnect_client(self):
        """Disconnect a selected client."""
        if self.client_table:
            selected = self.client_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No client selected", "warning")
                return
            
            client_id_hex = selected[0].get('id')
            if not client_id_hex:
                if self.toast_system:
                    self.toast_system.show_toast("Invalid client ID", "error")
                return
            client_id_bytes = bytes.fromhex(client_id_hex)

            if self.server and self.server.network_server:
                disconnect_method = getattr(self.server.network_server, 'disconnect_client', None)
                if disconnect_method and disconnect_method(client_id_bytes):
                    if self.toast_system is not None:
                        self.toast_system.show_toast("Client disconnected successfully.", "success")
                    self._add_activity_log(f"Disconnected client: {client_id_hex}")
                    self._refresh_client_table()
                elif self.toast_system is not None:
                    self.toast_system.show_toast("Failed to disconnect client (might be offline).", "error")
            elif self.toast_system is not None:
                self.toast_system.show_toast("Server is not running.", "error")
        elif self.toast_system is not None:
            self.toast_system.show_toast("Client table not initialized.", "error")

    def _refresh_file_table(self):
        """Refresh the file table with data from the database."""
        if self.file_table and self.server:
            try:
                files = self.server.db_manager.get_all_files()
                
                table_data: List[Dict[str, Any]] = []
                for f in files:
                    size_in_mb = f.get('size', 0) / (1024 * 1024) if f.get('size') else 0
                    table_data.append({
                        'filename': f['filename'],
                        'client': f['client'],
                        'size': f"{size_in_mb:.2f} MB" if f.get('size') is not None else 'N/A',
                        'date': f.get('date', 'N/A'),
                        'verified': "[OK] Yes" if f['verified'] else "[NO] No",
                        'path': f['path']
                    })
                
                if self.file_table is not None:
                    self.file_table.set_data(table_data)
                self._add_activity_log("File table refreshed.")
            except Exception as e:
                self._add_activity_log(f"Error refreshing file table: {e}")
                if self.toast_system:
                    self.toast_system.show_toast(f"Failed to refresh files: {e}", "error")
        elif self.toast_system:
            self.toast_system.show_toast("File table not initialized.", "error")

    def _on_file_selected(self, selected_item: Any) -> None:
        """Handle file selection in the table."""
        if selected_item and hasattr(self, 'file_detail_pane') and self.file_detail_pane:
            self.file_detail_pane.update_details(selected_item)
        elif hasattr(self, 'file_detail_pane') and self.file_detail_pane:
            self.file_detail_pane.clear_details()

    def _show_file_details(self):
        """Show details for the selected file."""
        if self.file_table:
            selected = self.file_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No file selected", "warning")
                return
            
            file_info = selected[0]
            messagebox.showinfo("File Details", json.dumps(file_info, indent=2))
        elif self.toast_system:
            self.toast_system.show_toast("File table not initialized.", "error")

    def _view_file_content(self):
        """View the content of the selected file."""
        if self.file_table:
            selected = self.file_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No file selected", "warning")
                return

            file_info = selected[0]
            file_path = file_info.get('path')
            
            if not file_path:
                if self.toast_system:
                    self.toast_system.show_toast("No file path available", "error")
                return

            if not os.path.exists(file_path):
                if self.toast_system:
                    self.toast_system.show_toast(f"File not found on disk: {file_path}", "error")
                return

            try:
                os.startfile(file_path)  # type: ignore
            except AttributeError:
                # os.startfile is only available on Windows. For other platforms, we can use other commands.
                import subprocess
# Cleaned up duplicate import
                if sys.platform == "darwin": # macOS
                    subprocess.call(["open", file_path])
                elif sys.platform == "linux2": # Linux
                    subprocess.call(["xdg-open", file_path])
                elif self.toast_system:
                    self.toast_system.show_toast("Viewing files is not supported on this platform.", "error")
            except Exception as e:
                if self.toast_system:
                    self.toast_system.show_toast(f"Error opening file: {e}", "error")
                self._add_activity_log(f"Error opening file: {e}")
        elif self.toast_system:
            self.toast_system.show_toast("File table not initialized.", "error")

    def _verify_file(self):
        """Verify the selected file."""
        if self.file_table:
            selected = self.file_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No file selected", "warning")
                return

            file_info = selected[0]
            filename = file_info.get('filename', '') if isinstance(file_info, dict) else ''
            client_name = file_info.get('client', '') if isinstance(file_info, dict) else ''

            if (self.server and hasattr(self.server, 'db_manager') and 
            self.server.db_manager):
                client_id_bytes = getattr(self.server, 'clients_by_name', {}).get(client_name)
                if not client_id_bytes:
                    if self.toast_system:
                        self.toast_system.show_toast(f"Could not find client ID for {client_name}", "error")
                    return
                client_id_hex = client_id_bytes.hex() if isinstance(client_id_bytes, bytes) else str(client_id_bytes)

                db_file_info = self.server.db_manager.get_file_info(client_id_hex, filename)
                if not db_file_info:
                    if self.toast_system:
                        self.toast_system.show_toast(f"Could not find file info for {filename}", "error")
                    return

                file_path = db_file_info.get('path', '') if isinstance(db_file_info, dict) else ''  # type: ignore
                stored_crc = db_file_info.get('crc') if isinstance(db_file_info, dict) else None  # type: ignore

                if not os.path.exists(file_path):
                    if self.toast_system:
                        self.toast_system.show_toast(f"File not found on disk: {file_path}", "error")
                    return

                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # Since the CRC calculation is in file_transfer, we need to access it from there.
                # This is not ideal, but it's the quickest way to implement this feature.
                from python_server.server.file_transfer import FileTransferManager
# Cleaned up duplicate import
                calculated_crc = FileTransferManager(self.server)._calculate_crc(file_data)

                if stored_crc == calculated_crc:
                    if self.toast_system:
                        self.toast_system.show_toast("File verification successful!", "success")
                    # Update the database to mark the file as verified
                    file_size = len(file_data)
                    file_date = db_file_info.get('date') if isinstance(db_file_info, dict) else None  # type: ignore
                    self.server.db_manager.save_file_info_to_db(client_id_bytes, filename, file_path, True, file_size, file_date, stored_crc)
                    self._refresh_file_table()
                else:
                    if self.toast_system:
                        self.toast_system.show_toast(f"File verification failed!\n\nStored CRC: {stored_crc}\nCalculated CRC: {calculated_crc}", "error")
            else:
                if self.toast_system:
                    self.toast_system.show_toast("Server is not running.", "error")
        elif self.toast_system:
            self.toast_system.show_toast("File table not initialized.", "error")

    def _delete_file(self):
        """Delete the selected file."""
        if self.file_table:
            selected = self.file_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No file selected", "warning")
                return

            file_info = selected[0]
            filename = file_info.get('filename', '') if isinstance(file_info, dict) else ''
            client_name = file_info.get('client', '') if isinstance(file_info, dict) else ''

            if not messagebox.askyesno("Delete File", f"Are you sure you want to delete the file '\n{filename}' for client '\n{client_name}'?\n\nThis action cannot be undone."):
                return

            if self.server and hasattr(self.server, 'db_manager') and self.server.db_manager:
                # We need the client ID to delete the file. We can get it from the client name.
                clients_by_name = getattr(self.server, 'clients_by_name', {})
                client_id_bytes = clients_by_name.get(client_name)
                if not client_id_bytes:
                    if self.toast_system:
                        self.toast_system.show_toast(f"Could not find client ID for {client_name}", "error")
                    return

                client_id_hex = client_id_bytes.hex() if hasattr(client_id_bytes, 'hex') else str(client_id_bytes)

                delete_method = getattr(self.server.db_manager, 'delete_file', None)
                if delete_method and delete_method(client_id_hex, filename):
                    if self.toast_system:
                        self.toast_system.show_toast(f"File '{filename}' deleted successfully.", "success")
                    self._add_activity_log(f"Deleted file: {filename}")
                    self._refresh_file_table()
                elif self.toast_system:
                    self.toast_system.show_toast(f"Failed to delete file '{filename}'.", "error")
            else:
                if self.toast_system:
                    self.toast_system.show_toast("Server is not running.", "error")
        elif self.toast_system:
            self.toast_system.show_toast("File table not initialized.", "error")

    def update_client_stats(self, stats_data: Dict[str, Any]):
        """Update client statistics"""
        if not self.gui_enabled:
            return
        if 'connected' in self.status_labels:
            connected_value = stats_data.get('connected', 0) if isinstance(stats_data, dict) else 0
            self.status_labels['connected'].config(text=str(connected_value))
        if 'total' in self.status_labels:
            total_value = stats_data.get('total', 0) if isinstance(stats_data, dict) else 0
            self.status_labels['total'].config(text=str(total_value))
        if 'active_transfers' in self.status_labels:
            active_value = stats_data.get('active_transfers', 0) if isinstance(stats_data, dict) else 0
            self.status_labels['active_transfers'].config(text=str(active_value))

    def update_transfer_stats(self, stats_data: Dict[str, Any]):
        """Update transfer statistics"""
        if not self.gui_enabled:
            return
        bytes_transferred = stats_data.get('bytes_transferred', 0) if isinstance(stats_data, dict) else 0
        if 'bytes' in self.status_labels:
            bytes_mb = bytes_transferred / 1024 / 1024 if isinstance(bytes_transferred, (int, float)) else 0
            self.status_labels['bytes'].config(text=f"{bytes_mb:.2f} MB")
        # Other transfer stats can be updated here

    def update_maintenance_stats(self, stats_data: Dict[str, Any]):
        """Update maintenance statistics"""
        if not self.gui_enabled:
            return
        if 'files_cleaned' in self.status_labels:
            files_value = stats_data.get('files_cleaned', 0) if isinstance(stats_data, dict) else 0
            self.status_labels['files_cleaned'].config(text=str(files_value))
        if 'partial_cleaned' in self.status_labels:
            partial_value = stats_data.get('partial_files_cleaned', 0) if isinstance(stats_data, dict) else 0
            self.status_labels['partial_cleaned'].config(text=str(partial_value))
        if 'clients_cleaned' in self.status_labels:
            clients_value = stats_data.get('clients_cleaned', 0) if isinstance(stats_data, dict) else 0
            self.status_labels['clients_cleaned'].config(text=str(clients_value))
        last_cleanup = stats_data.get('last_cleanup', 'Never') if isinstance(stats_data, dict) else 'Never'
        if last_cleanup != 'Never':
            try:
                last_cleanup = datetime.fromisoformat(str(last_cleanup)).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                last_cleanup = 'Never'
        if 'last_cleanup' in self.status_labels:
            self.status_labels['last_cleanup'].config(text=last_cleanup)

    def update_server_status(self, running: bool, address: str, port: int):
        """Update server status display"""
        print(f"[DEBUG] update_server_status called: running={running}, address={address}, port={port}")

        if not self.gui_enabled:
            print("[DEBUG] GUI not enabled, returning")
            return

        # Update the status object
        self.status.running = running
        self.status.server_address = address
        self.status.port = port

        # Update status labels
        if running:
            status_text = "🟢 Running"
            status_color = ModernTheme.SUCCESS
            header_text = "Server Online"
            indicator_status = "online"
        else:
            status_text = "🛑 Stopped"
            status_color = ModernTheme.ERROR
            header_text = "Server Offline"
            indicator_status = "offline"

        # Fix Unicode encoding issue - safely print debug info
        try:
            print(f"[DEBUG] Status text: {status_text}, Available status_labels keys: {list(self.status_labels.keys())}")
        except UnicodeEncodeError:
            # Fallback to ASCII-safe version
            safe_status = status_text.encode('ascii', 'ignore').decode('ascii')
            print(f"[DEBUG] Status text: {safe_status}, Available status_labels keys: {list(self.status_labels.keys())}")

        # Update main status label
        if 'status' in self.status_labels:
            print("[DEBUG] Updating main status label")
            self.status_labels['status'].config(text=status_text, fg=status_color)
        else:
            print("[DEBUG] 'status' key not found in status_labels")

        # Update header status label
        if hasattr(self, 'header_status_label') and self.header_status_label is not None:
            print("[DEBUG] Updating header status label")
            self.header_status_label.config(text=header_text)
        else:
            print("[DEBUG] header_status_label not found")

        # Update header status indicator
        if self.header_status_indicator is not None and hasattr(self.header_status_indicator, 'set_status'):
            print("[DEBUG] Updating header status indicator")
            self.header_status_indicator.set_status(indicator_status)
        else:
            print("[DEBUG] header_status_indicator not found")

        # Update address and port labels if they exist
        if 'address' in self.status_labels:
            self.status_labels['address'].config(text=address)
        if 'port' in self.status_labels:
            self.status_labels['port'].config(text=str(port))

        # Update uptime display
        if 'uptime' in self.status_labels:
            if running:
                self.status_labels['uptime'].config(text="Just started")
            else:
                self.status_labels['uptime'].config(text="0:00:00")

        print("[DEBUG] update_server_status completed")

    # --- Missing Method Implementations (Stubs) ---
    
    def _setup_modern_styles(self):
        """Setup modern styling for the GUI."""
        # Apply modern theme styles to the root window
        if self.root:
            self.root.configure(bg=ModernTheme.PRIMARY_BG)
    
    def _create_system_tray(self):
        """Create system tray icon if available."""
        # System tray functionality is optional - TODO: Implement when needed
        # Currently TRAY_AVAILABLE but no implementation yet
    
    def _schedule_updates(self):
        """Schedule periodic GUI updates."""
        try:
            # Process queued updates
            self._process_update_queue()

            # Update real-time elements
            self._update_clock()
            self._update_performance_metrics()
            
            # Auto-refresh file table every 5 seconds when server is running
            # This ensures new files appear automatically without manual refresh
            if self.status.running:
                if not hasattr(self, '_last_file_refresh_time'):
                    # Initialize refresh timer
                    self._last_file_refresh_time = time.time()
                else:
                    current_time = time.time()
                    if self._last_file_refresh_time is not None and (current_time - self._last_file_refresh_time) >= 5.0:  # 5 second interval
                        if hasattr(self, 'current_tab') and self.current_tab == 'files':
                            self._refresh_file_table()
                        self._last_file_refresh_time = current_time

            # Update uptime if server is running
            if self.status.running:
                current_time = time.time()
                self.status.uptime_seconds = int(current_time - self.start_time)
                if 'uptime' in self.status_labels:
                    uptime_str = self._format_uptime(self.status.uptime_seconds)
                    self.status_labels['uptime'].config(text=uptime_str)

        except Exception as e:
            print(f"[DEBUG] Error in _schedule_updates: {e}")

        # Schedule next update
        if self.root is not None:
            self.root.after(1000, self._schedule_updates)  # Update every second

    def _process_update_queue(self):
        """Process all pending updates from the queue."""
        try:
            while not self.update_queue.empty():
                payload = self.update_queue.get_nowait()
                # Support both tuple(old) and dict(new) payloads safely
                update_type: Optional[str] = None
                data: Dict[str, Any] = {}
                if isinstance(payload, tuple) and len(payload) == 2:
                    update_type, raw = payload  # type: ignore[misc]
                    if isinstance(raw, dict):
                        data = raw
                elif isinstance(payload, dict):
                    update_type = payload.get('type')  # type: ignore[assignment]
                    data = payload  # type: ignore[assignment]

                if update_type == "status":
                    running_status = bool(data.get('running', False))
                    address = str(data.get('address', ''))
                    port = int(data.get('port', 0))
                    self.update_server_status(running_status, address, port)
                elif update_type == "client_stats":
                    self.update_client_stats(data)
                elif update_type == "transfer_stats":
                    self.update_transfer_stats(data)
                elif update_type == "maintenance_stats":
                    self.update_maintenance_stats(data)
                elif update_type == "log":
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    self.activity_log.append(f"[{timestamp}] {str(data)}")
                    if len(self.activity_log) > 100:
                        self.activity_log = self.activity_log[-100:]

        except Exception as e:
            print(f"[DEBUG] Error processing update queue: {e}")

    def _on_window_close(self):
        """Handle window close event."""
        # Graceful shutdown when window is closed
        if self.root:
            self.root.destroy()

def launch_standalone():
    """Launch the Server GUI when this file is executed directly.

    Previously the file had no __main__ entrypoint so the process exited
    immediately when started by one_click_build_and_run.py. This function
    provides a stable entry so running `python ServerGUI.py` opens the window.
    """
    try:
        from Shared.path_utils import setup_imports
# Cleaned up duplicate import
        setup_imports()
        print("[INFO] Launching Server GUI (standalone mode)...")

        # Instantiate GUI (don't pass tk root; initialize() creates it internally)
        try:
            gui = ServerGUI()
        except Exception as e:
            print(f"[FATAL] Failed to construct ServerGUI object: {e}")
            import traceback; traceback.print_exc()
# Cleaned up duplicate import
            return 1

        # Initialize (spawns GUI thread which builds full window & enters mainloop)
        if not gui.initialize():
            print("[ERROR] Server GUI failed to initialize")
            return 1

        print("[OK] Server GUI initialized. Waiting for GUI thread to finish (Ctrl+C to exit)...")
        try:
            while gui.gui_thread and gui.gui_thread.is_alive():
                gui.gui_thread.join(timeout=0.5)
        except KeyboardInterrupt:
            print("\n[INFO] Interrupt received. Shutting down Server GUI...")
            try:
                gui.shutdown()
            except Exception as e:
                print(f"[WARN] Error during GUI shutdown: {e}")
        return 0
    except Exception as e:
        print(f"[FATAL] Unhandled exception launching Server GUI: {e}")
        import traceback; traceback.print_exc()
# Cleaned up duplicate import
        return 1


if __name__ == "__main__":
    sys.exit(launch_standalone())

