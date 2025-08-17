# -*- coding: utf-8 -*-
# EnhancedServerGUI.py - A modern, feature-rich, cross-platform GUI for the Encrypted Backup Server.
# This version incorporates a complete UI/UX overhaul based on professional design principles.
# Built with ttkbootstrap, matplotlib, and a component-based architecture. Python 3.9+ required.

from __future__ import annotations
import sys
import os
import threading
import traceback
from collections import deque
from datetime import datetime, timedelta
from typing import (Dict, List, Optional, Any, Deque, Callable, TYPE_CHECKING, Tuple)
from contextlib import suppress
import time
import queue
import json
import shutil
import tkinter as tk
from tkinter import font, messagebox, filedialog
import tkinter.ttk as std_ttk

# --- Dependency and System Setup ---
def _safe_reconfigure_stream(stream: Any) -> None:
    """Safely reconfigure a stream to use UTF-8 encoding if possible."""
    if callable(getattr(stream, 'reconfigure', None)):
        with suppress(Exception):
            stream.reconfigure(encoding='utf-8')

_safe_reconfigure_stream(sys.stdout)
_safe_reconfigure_stream(sys.stderr)

try:
    import Shared.utils.utf8_solution
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    with suppress(ImportError):
        import Shared.utils.utf8_solution

# --- Type Hinting Setup ---
if TYPE_CHECKING:
    from Shared.utils.process_monitor_gui import ProcessMonitorWidget
    import pystray
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    from matplotlib.lines import Line2D
    from server.database import DatabaseManager as ActualDBManager
    
# --- Dependency Imports with Graceful Fallbacks ---
# Enhanced fallback system for ttkbootstrap compatibility
TTK_BOOTSTRAP_AVAILABLE = False
ttk_bootstrap = None
ToastNotification = None
ToolTip = None
ScrolledText = None
ScrolledFrame = None
TTKWindow = None

try:
    import ttkbootstrap as ttk_bootstrap
    from ttkbootstrap.constants import *
    from ttkbootstrap.toast import ToastNotification
    from ttkbootstrap.tooltip import ToolTip
    from ttkbootstrap.scrolled import ScrolledText, ScrolledFrame
    from ttkbootstrap import Window as TTKWindow
    TTK_BOOTSTRAP_AVAILABLE = True
except ImportError:
    print("[WARNING] ttkbootstrap not available. Falling back to standard tkinter.")
    
    # Create comprehensive fallback module-like object
    class TTKBootstrapFallback:
        # Enhanced parameter filtering for ttkbootstrap compatibility
        @staticmethod
        def filter_ttkbootstrap_params(kwargs):
            """Remove ttkbootstrap-specific parameters that aren't compatible with standard tkinter"""
            ttkbootstrap_params = {
                'bootstyle', 'themename', 'resizable', 'hdpi', 'padding',
                # String-type parameters that should be converted  
                'relief', 'takefocus', 'anchor', 'compound', 'justify', 
                'default', 'textvariable', 'underline', 'width', 'height',
                'exportselection', 'validate', 'autohide'
            }
            return {k: v for k, v in kwargs.items() if k not in ttkbootstrap_params}
        
        class Window(tk.Toplevel):
            def __init__(self, *args, **kwargs):
                filtered_kwargs = TTKBootstrapFallback.filter_ttkbootstrap_params(kwargs)
                super().__init__(*args, **filtered_kwargs)
        
        class Frame(std_ttk.Frame):
            def __init__(self, *args, **kwargs):
                filtered_kwargs = TTKBootstrapFallback.filter_ttkbootstrap_params(kwargs)
                super().__init__(*args, **filtered_kwargs)
        
        class Label(std_ttk.Label):
            def __init__(self, *args, **kwargs):
                filtered_kwargs = TTKBootstrapFallback.filter_ttkbootstrap_params(kwargs)
                super().__init__(*args, **filtered_kwargs)
        
        class Button(std_ttk.Button):
            def __init__(self, *args, **kwargs):
                filtered_kwargs = TTKBootstrapFallback.filter_ttkbootstrap_params(kwargs)
                super().__init__(*args, **filtered_kwargs)
        
        class Entry(std_ttk.Entry):
            def __init__(self, *args, **kwargs):
                filtered_kwargs = TTKBootstrapFallback.filter_ttkbootstrap_params(kwargs)
                super().__init__(*args, **filtered_kwargs)
        
        class Style:
            def configure(self, *args, **kwargs):
                pass  # No-op for fallback
            def theme_names(self):
                return ['default']
            def theme_use(self, theme=None):
                return 'default'
            def get_instance(self):
                return self
            @property
            def colors(self):
                return {'primary': '#007bff', 'secondary': '#6c757d', 'success': '#28a745', 
                       'info': '#17a2b8', 'warning': '#ffc107', 'danger': '#dc3545',
                       'light': '#f8f9fa', 'dark': '#343a40'}
        
        class Combobox(std_ttk.Combobox):
            def __init__(self, *args, **kwargs):
                filtered_kwargs = TTKBootstrapFallback.filter_ttkbootstrap_params(kwargs)
                super().__init__(*args, **filtered_kwargs)
        
        class Checkbutton(std_ttk.Checkbutton):
            def __init__(self, *args, **kwargs):
                filtered_kwargs = TTKBootstrapFallback.filter_ttkbootstrap_params(kwargs)
                super().__init__(*args, **filtered_kwargs)
        
        # PhotoImage from tkinter (not ttk)
        PhotoImage = tk.PhotoImage
        
        # Add style attribute
        style = Style()
        
        # Make classes available within class scope
        def __init__(self):
            pass
    
    # Create fallback instances and add missing attributes
    ttk_bootstrap = TTKBootstrapFallback()
    ttk_bootstrap.Combobox = Combobox
    ttk_bootstrap.Checkbutton = Checkbutton
    ttk_bootstrap.PhotoImage = PhotoImage
    ttk_bootstrap.Style = Style
    TTKWindow = ttk_bootstrap.Window
    
    # Fallback classes for missing components
    class ToastNotificationFallback:
        def __init__(self, *args, **kwargs):
            pass
        def show_toast(self):
            pass
    
    ToastNotification = ToastNotificationFallback
    ToolTip = None
    ScrolledText = tk.Text
    ScrolledFrame = std_ttk.Frame

# Create convenience aliases for consistent usage throughout the file
# Now ttk_bootstrap is always defined (either real or fallback)
FrameClass = ttk_bootstrap.Frame
LabelClass = ttk_bootstrap.Label
ButtonClass = ttk_bootstrap.Button
EntryClass = ttk_bootstrap.Entry

try:
    import psutil
    SYSTEM_MONITOR_AVAILABLE = True
except ImportError:
    psutil = None
    SYSTEM_MONITOR_AVAILABLE = False
    print("[INFO] psutil not available. System monitoring will be disabled.")

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    CHARTS_AVAILABLE = True
except ImportError:
    FigureCanvasTkAgg = Figure = None # type: ignore
    CHARTS_AVAILABLE = False
    print("[INFO] matplotlib not available. Analytics charts will be disabled.")
    
try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    DateEntry = None # type: ignore
    CALENDAR_AVAILABLE = False
    print("[INFO] tkcalendar not available. Date filtering will be disabled.")

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    pystray = None # type: ignore
    TRAY_AVAILABLE = False
    print("[INFO] pystray/Pillow not available. System tray will be disabled.")
    
try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    playsound = None # type: ignore
    PLAYSOUND_AVAILABLE = False
    print("[INFO] playsound not available. Audio cues will be disabled.")
    
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    pyperclip = None # type: ignore
    PYPERCLIP_AVAILABLE = False
    print("[INFO] pyperclip not available. Copy-to-clipboard functionality disabled.")
    
try:
    from Shared.utils.process_monitor_gui import ProcessMonitorWidget
    PROCESS_MONITOR_AVAILABLE = True
except ImportError:
    ProcessMonitorWidget = None # type: ignore
    PROCESS_MONITOR_AVAILABLE = False
    print("[INFO] ProcessMonitorWidget not found.")
    
try:
    from server.database import DatabaseManager
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    try:
        from server.database import DatabaseManager
    except ImportError:
        DatabaseManager = None # type: ignore
        print("[WARNING] DatabaseManager not available - Database tab will be disabled.")

try:
    import sentry_sdk
    if SENTRY_DSN := os.environ.get("SENTRY_DSN"):
        sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)
        SENTRY_AVAILABLE = True
        print("[OK] Sentry error tracking initialized.")
    else:
        SENTRY_AVAILABLE = False
except ImportError:
    SENTRY_AVAILABLE = False

# --- Core Application Classes ---

class AppSettings:
    """Manages loading, saving, and accessing application settings."""
    def __init__(self, settings_file: str = "server_gui_settings.json") -> None:
        self.settings_file = settings_file
        self.settings = self._load()

    def _load(self) -> Dict[str, Any]:
        defaults: Dict[str, Any] = {
            'port': 1256,
            'storage_dir': 'received_files',
            'max_clients': 50,
            'session_timeout': 10,
            'maintenance_interval': 60,
            'last_tab': 'dashboard',
            'theme': 'cyborg',
            'audio_cues': True,
            'low_disk_threshold': 15
        }
        with suppress(FileNotFoundError, json.JSONDecodeError):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                defaults.update(json.load(f))
        return defaults

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value

    def save(self) -> bool:
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except (IOError, TypeError) as e:
            print(f"[ERROR] Failed to save settings: {e}")
            return False

class FramelessWindow(TTKWindow if TTK_BOOTSTRAP_AVAILABLE else tk.Toplevel):
    """A custom frameless window with a draggable title bar and custom controls."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.offset_x = 0
        self.offset_y = 0

        self.overrideredirect(True)
        self.after(10, lambda: self.set_app_icon())

        # Create title bar components with fallback styling
        title_bar_style = {"bootstyle": "secondary"} if TTK_BOOTSTRAP_AVAILABLE else {}
        self.title_bar = (ttk_bootstrap.Frame if TTK_BOOTSTRAP_AVAILABLE else std_ttk.Frame)(self, **title_bar_style)
        self.title_bar.pack(fill=tk.X, side=tk.TOP)

        grip_style = {"bootstyle": "secondary", "cursor": "sizing"} if TTK_BOOTSTRAP_AVAILABLE else {"cursor": "sizing"}
        self.grip = (ttk_bootstrap.Frame if TTK_BOOTSTRAP_AVAILABLE else std_ttk.Frame)(self, **grip_style)
        self.grip.place(relx=1.0, rely=1.0, anchor=tk.SE)

        label_style = {"bootstyle": "inverse-secondary"} if TTK_BOOTSTRAP_AVAILABLE else {}
        self.title_label = (ttk_bootstrap.Label if TTK_BOOTSTRAP_AVAILABLE else std_ttk.Label)(
            self.title_bar, text=self.title(), font="-family {Segoe UI} -size 10", **label_style
        )
        self.title_label.pack(side=tk.LEFT, padx=10)

        button_styles = {
            "close": {"bootstyle": "danger"} if TTK_BOOTSTRAP_AVAILABLE else {},
            "maximize": {"bootstyle": "info"} if TTK_BOOTSTRAP_AVAILABLE else {},
            "minimize": {"bootstyle": "info"} if TTK_BOOTSTRAP_AVAILABLE else {}
        }
        
        # ButtonClass is now defined globally
        self.close_button = ButtonClass(self.title_bar, text='✕', command=self.destroy, **button_styles["close"])
        self.maximize_button = ButtonClass(self.title_bar, text='🗖', command=self.toggle_maximize, **button_styles["maximize"])
        self.minimize_button = ButtonClass(self.title_bar, text='—', command=self.minimize, **button_styles["minimize"])

        self.close_button.pack(side=tk.RIGHT, fill=tk.Y)
        self.maximize_button.pack(side=tk.RIGHT, fill=tk.Y)
        self.minimize_button.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.title_bar.bind("<Button-1>", self.on_press)
        self.title_bar.bind("<B1-Motion>", self.on_drag)
        self.title_label.bind("<Button-1>", self.on_press)
        self.title_label.bind("<B1-Motion>", self.on_drag)
        self.grip.bind("<B1-Motion>", self.on_resize)
        
        self.is_maximized = False
        self._geom = '200x200+0+0'

    def set_app_icon(self) -> None:
        """Sets the application icon for the taskbar."""
        with suppress(Exception):
            # A simple way to create a platform-agnostic icon in memory
            # This avoids needing a file on disk
            img_data = b'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGvSURBVHja7Zq9SsRAEIX9/xE9iIiIInir4GEn2Nj5AEtBC1sL/4AgaGHhD/gBFrY+gI2VnSgWFFFEEfE/GDaZZJY3u1uTzAd2ZZOd7O43y87sjpNer9eCgSRfUvYT5PMk++T7JPsj/k06zT4W8PMA23wvgD8A8D8D+I8d2I/x/4F8AWBeADSAsiUMgDwCkAcA8gZA3gDIA4A8AJAHAPIGQN4AyAOAPACOK8sWMM8A+gBAnwDoA4A+ANAHAPoAQB8A6AOAPgDQBwB9AKAPAPQBgD4A0AcA+gBAnwDoA4A+ANAHAPoAQB8A6AOAPgDQBwB9AKAPAPQBgD4A0AcA+gBAnwDoA4A+ANAHAPoAQB8A6AOAPgDQBwB9AKAPAPQBgD4A0AcA+gBAnwDoA4A+ANAHAPoAQB8A6AOAPgDQBwB9AKAPAPQBgD4A0AcA+gBAnwDoA4A+ANAHAPoAQB8A6AOAPgDQBwB9AKAPAPQBgD4A0AcA+gBAnwDoA4A+ANAHAPoAQB8A6AOAPgDQBwB9AKCPAEwzAPMMoA8A9AEAZeUMgDwAkgcAsslgADL/ADyKOzxP0W4OAAAAAElFTkSuQmCC'
            self.tk.call('wm', 'iconphoto', self._w, tk.PhotoImage(data=img_data))

    def on_press(self, event: tk.Event) -> None:
        self.offset_x = event.x
        self.offset_y = event.y

    def on_drag(self, event: tk.Event) -> None:
        x = self.winfo_pointerx() - self.offset_x
        y = self.winfo_pointery() - self.offset_y
        self.geometry(f"+{x}+{y}")

    def on_resize(self, event: tk.Event) -> None:
        new_width = self.winfo_width() + event.x
        new_height = self.winfo_height() + event.y
        self.geometry(f"{new_width}x{new_height}")

    def toggle_maximize(self) -> None:
        if self.is_maximized:
            self.geometry(self._geom)
            self.is_maximized = False
        else:
            self._geom = self.geometry()
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
            self.is_maximized = True
            
    def minimize(self) -> None:
        self.withdraw()
        
    def set_close_command(self, command: Callable[[], None]) -> None:
        self.close_button.config(command=command)

class EnhancedServerGUI:
    def __init__(self, server_instance: Optional[Any] = None) -> None:
        self.server = server_instance
        self.settings = AppSettings()
        
        self.root: Optional[FramelessWindow] = None
        self.is_running = False
        self.gui_thread: Optional[threading.Thread] = None
        
        self.update_queue: queue.Queue[Dict[str, Any]] = queue.Queue()
        self.toast: Optional[ToastNotification] = None
        self.tray_icon: Optional[pystray.Icon] = None
        
        self.pages: Dict[str, ttk.Frame] = {}
        self.nav_buttons: Dict[str, ttk.Button] = {}
        self.current_page_id = self.settings.get('last_tab', 'dashboard')
        
        self._fallback_db_manager: Optional[ActualDBManager] = None
        self.performance_data: Dict[str, Deque[Any]] = {
            'cpu': deque(maxlen=120), 
            'memory': deque(maxlen=120), 
            'time': deque(maxlen=120)
        }
    
    # --- Public API & Lifecycle Methods ---
    
    def initialize(self) -> bool:
        """Initializes and starts the GUI in a separate thread."""
        if self.is_running: return True
        try:
            # Check for display availability before starting thread
            root_check = tk.Tk()
            root_check.withdraw()
            root_check.destroy()
        except tk.TclError:
            print(f"\n{'='*80}\nFATAL: Cannot start GUI - No graphical display available.\n{'='*80}\n")
            return False

        self.is_running = True
        self.gui_thread = threading.Thread(target=self._gui_main_loop, daemon=True)
        self.gui_thread.start()
        
        # Wait for root window to be created
        for _ in range(50):
            if self.root:
                print("[OK] GUI initialized successfully!")
                return True
            time.sleep(0.1)
            
        print("[ERROR] GUI initialization timed out.")
        self.is_running = False
        return False
    
    def shutdown(self) -> None:
        """Schedules the destruction of the GUI and stops related components."""
        print("Starting GUI shutdown...")
        self.is_running = False
        if self.tray_icon: self.tray_icon.stop()
        if self.root:
            # Safely destroy from any thread
            self.root.after(0, self.root.destroy)
        print("GUI shutdown completed.")
        
    def add_log_message(self, message: str, level: str = "INFO") -> None:
        """Thread-safe method to add a log message to the GUI."""
        log_data = {'type': 'log', 'data': {'message': message, 'level': level}}
        self.update_queue.put(log_data)
        
    def update_server_status(self, data: Dict[str, Any]) -> None:
        self.update_queue.put({'type': 'status', 'data': data})
        
    def update_client_stats(self, data: Dict[str, Any]) -> None:
        self.update_queue.put({'type': 'client_stats', 'data': data})
        
    def update_transfer_stats(self, data: Dict[str, Any]) -> None:
        self.update_queue.put({'type': 'transfer_stats', 'data': data})

    def update_maintenance_stats(self, data: Dict[str, Any]) -> None:
        self.update_queue.put({'type': 'maintenance', 'data': data})
        
    # --- Internal GUI Setup & Main Loop ---
    
    def _gui_main_loop(self) -> None:
        """The main entry point for the GUI thread."""
        try:
            self._setup_gui_components()
            if self.root:
                self.root.mainloop()
        except Exception as e:
            print(f"GUI main loop error: {e}")
            if SENTRY_AVAILABLE and 'sentry_sdk' in globals(): 
                sentry_sdk.capture_exception(e)
            traceback.print_exc()
        finally:
            self.is_running = False
            print("GUI main loop ended.")
            
    def _setup_gui_components(self) -> None:
        """Initializes the root window and all its components."""
        if TTK_BOOTSTRAP_AVAILABLE:
            self.root = FramelessWindow(
                title="Encrypted Backup Server - Command Center",
                themename=self.settings.get('theme'),
                size=(1400, 900),
                minsize=(1100, 750)
            )
        else:
            self.root = FramelessWindow()
            self.root.title("Encrypted Backup Server - Command Center")
            self.root.geometry("1400x900")
            self.root.minsize(1100, 750)
        self.root.set_close_command(self._on_window_close)

        self._create_main_layout()
        self._create_system_tray()
        self._schedule_updates()
        self.sync_current_server_state()
        
        if TTK_BOOTSTRAP_AVAILABLE and ToastNotification:
            try:
                self.toast = ToastNotification(
                    title="Server Notification",
                    bootstyle="primary",
                    duration=3000,
                    position=(20, 20, 'ne'), # Position relative to root window
                )
            except Exception:
                self.toast = None
        else:
            self.toast = None

        if self.toast:
            self.root.after(250, lambda: self.toast.show_toast("GUI Ready", "Server Online"))
        self._play_audio_cue('startup')

    def _create_main_layout(self) -> None:
        """Creates the main header, sidebar, and content area."""
        if not self.root: return

        # Main container below the custom title bar
        # FrameClass is now defined globally
        main_container = FrameClass(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
        
        # Header
        header = self._create_header(main_container)
        header.pack(fill=tk.X, padx=10, pady=(5, 10))

        # Body (Sidebar + Content)
        body_container = FrameClass(main_container)
        body_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        sidebar = self._create_sidebar(body_container)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, pady=(0, 5))

        self.content_area = FrameClass(body_container)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self._create_pages()
        self._switch_page(self.current_page_id)

    def _create_header(self, parent: tk.Widget):
        """Creates the application header with title, search, and status."""
        # FrameClass is now defined globally
        # LabelClass is now defined globally
        # EntryClass is now defined globally
        
        header = FrameClass(parent)
        
        # Left: App Title
        title_style = {} if not TTK_BOOTSTRAP_AVAILABLE else {}
        LabelClass(header, text="Encrypted Backup Server", font="-family {Segoe UI} -size 18 -weight bold", **title_style).pack(side=tk.LEFT, anchor=tk.W)

        # Right: Status and Clock
        status_frame = FrameClass(header)
        status_frame.pack(side=tk.RIGHT, anchor=tk.E)

        clock_style = {"bootstyle": "secondary"} if TTK_BOOTSTRAP_AVAILABLE else {}
        self.clock_label = LabelClass(status_frame, text="", font="-family {Segoe UI} -size 12", **clock_style)
        self.clock_label.pack(anchor=tk.E)
        
        indicator_frame = FrameClass(status_frame)
        indicator_frame.pack(pady=(5, 0), anchor=tk.E)

        status_label_style = {"bootstyle": "secondary"} if TTK_BOOTSTRAP_AVAILABLE else {}
        self.header_status_label = LabelClass(indicator_frame, text="Server Offline", font="-family {Segoe UI} -size 10", **status_label_style)
        self.header_status_label.pack(side=tk.LEFT, padx=(0, 10))

        pill_style = {"bootstyle": "danger-inverse", "padding": (10, 3)} if TTK_BOOTSTRAP_AVAILABLE else {}
        self.header_status_pill = LabelClass(indicator_frame, text="OFFLINE", font="-family {Segoe UI} -size 8 -weight bold", anchor=tk.CENTER, **pill_style)
        self.header_status_pill.pack(side=tk.LEFT)
        self.header_status_pill.winfo_toplevel().after(10, lambda: self._apply_pill_style())

        # Center: Global Search Bar
        search_frame = FrameClass(header)
        search_frame.pack(side=tk.RIGHT, anchor=tk.E, padx=30, fill=tk.X, expand=True)
        self.search_var = tk.StringVar()
        entry_style = {"bootstyle": "secondary"} if TTK_BOOTSTRAP_AVAILABLE else {}
        search_entry = EntryClass(search_frame, textvariable=self.search_var, font="-family {Segoe UI} -size 11", **entry_style)
        search_entry.pack(ipady=5, fill=tk.X)
        if ToolTip:
            ToolTip(search_entry, "Global Search (Clients, Logs...) - Coming Soon!")
        
        return header

    def _apply_pill_style(self) -> None:
        """Helper to apply a rounded pill style to a label."""
        if not self.root or not hasattr(self, 'header_status_pill'): return
        try:
            if TTK_BOOTSTRAP_AVAILABLE:
                style = ttk_bootstrap.Style.get_instance()
                style.configure("Pill.TLabel", borderwidth=5, relief="solid", cornerradius=12)
                self.header_status_pill.configure(style="Pill.TLabel")
        except Exception:
            pass  # Style configuration may fail, continue without styling
        
    def _create_sidebar(self, parent: tk.Widget):
        """Creates the main navigation sidebar."""
        # FrameClass is now defined globally
        # ButtonClass is now defined globally
        
        sidebar_style = {"bootstyle": "dark"} if TTK_BOOTSTRAP_AVAILABLE else {}
        sidebar = FrameClass(parent, width=220, **sidebar_style)
        sidebar.pack_propagate(False)

        # Use ttkbootstrap icons (font-based)
        icons = {"dashboard": "house-door-fill", "clients": "people-fill", "files": "folder-fill", 
                 "analytics": "graph-up", "database": "stack", "processes": "cpu-fill", 
                 "logs": "file-earmark-text-fill", "settings": "gear-fill"}
        
        pages_config = [("dashboard", "Dashboard"), ("clients", "Clients"), ("files", "Files"), 
                        ("analytics", "Analytics"), ("database", "Database"), ("logs", "Logs"), ("settings", "Settings")]
        
        if PROCESS_MONITOR_AVAILABLE:
            pages_config.insert(5, ("processes", "Processes"))

        for page_id, page_name in pages_config:
            icon_char = icons.get(page_id, "app")
            # Create button with fallback styling
            button_style = {"bootstyle": "dark", "padding": (20, 15)} if TTK_BOOTSTRAP_AVAILABLE else {}
            
            try:
                # Try to use PhotoImage for icons in ttkbootstrap
                if TTK_BOOTSTRAP_AVAILABLE:
                    img = ttk_bootstrap.PhotoImage(f"bi-{icon_char}", width=20, height=20)
                    btn = ButtonClass(
                        sidebar,
                        text=f" {page_name}",
                        image=img,
                        compound=tk.LEFT,
                        command=lambda p=page_id: self._switch_page(p),
                        **button_style
                    )
                    btn.image = img  # Keep a reference
                else:
                    # Fallback for standard tkinter
                    btn = ButtonClass(
                        sidebar,
                        text=f" {page_name}",
                        command=lambda p=page_id: self._switch_page(p)
                    )
            except Exception:
                # Fallback button without icon
                btn = ButtonClass(
                    sidebar,
                    text=f" {page_name}",
                    command=lambda p=page_id: self._switch_page(p)
                )
            
            btn.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
            self.nav_buttons[page_id] = btn

        return sidebar

    def _create_pages(self) -> None:
        """Instantiates all page frames."""
        if not self.content_area: return
        # In a real app, you would import these page classes
        # For this single file, we define them below and instantiate here
        page_classes = {
            "dashboard": DashboardPage,
            "clients": ClientsPage,
            "analytics": AnalyticsPage,
            "settings": SettingsPage,
            # Add other pages here
        }
        
        for page_id, PageClass in page_classes.items():
            page = PageClass(self.content_area, self)
            self.pages[page_id] = page
            # Initially hide all pages
            page.pack_forget()

    def _switch_page(self, page_id: str) -> None:
        """Hides the current page and shows the selected one."""
        if page_id not in self.nav_buttons:
            print(f"[WARN] Attempted to switch to non-existent page: {page_id}")
            return
            
        self.current_page_id = page_id
        self.settings.set('last_tab', page_id)

        # Update button styles
        for pid, btn in self.nav_buttons.items():
            if TTK_BOOTSTRAP_AVAILABLE:
                btn.configure(bootstyle="primary" if pid == page_id else "dark")
            else:
                # Fallback styling for standard tkinter
                if pid == page_id:
                    btn.configure(relief=tk.RAISED, bg='lightblue')
                else:
                    btn.configure(relief=tk.FLAT, bg='lightgray')

        # Switch frames
        for pid, page_frame in self.pages.items():
            if pid == page_id:
                page_frame.pack(fill=tk.BOTH, expand=True)
                # Call an optional `on_show` method if the page has one
                if hasattr(page_frame, "on_show"):
                    page_frame.on_show()
            else:
                page_frame.pack_forget()

    # --- System Tray & Window Management ---

    def _create_system_tray(self) -> None:
        if not TRAY_AVAILABLE or not pystray: return
        
        try:
            image = Image.new('RGB', (64, 64), color=(30, 30, 30))
            draw = ImageDraw.Draw(image)
            draw.rectangle((10, 10, 54, 54), fill='#0d6efd') # ttkbootstrap primary blue
            
            menu = (
                pystray.MenuItem('Show/Hide Command Center', self._toggle_window, default=True),
                pystray.MenuItem('Quit Server', self._quit_app)
            )
            self.tray_icon = pystray.Icon("ServerGUI", image, "Encrypted Backup Server", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"[ERROR] Failed to create system tray icon: {e}")

    def _toggle_window(self) -> None:
        if not self.root: return
        if self.root.state() == 'withdrawn':
            self.root.deiconify()
        else:
            self.root.withdraw()
            
    def _quit_app(self) -> None:
        if self.root: self._on_window_close(force=True)

    def _on_window_close(self, force: bool = False) -> None:
        is_server_running = self.server and getattr(self.server, 'running', False)
        
        if not force and is_server_running:
            if not messagebox.askyesno(
                "Confirm Exit", 
                "The server is currently running. Are you sure you want to stop the server and exit?",
                parent=self.root
            ):
                return
                
        if is_server_running and self.server:
            # Run stop in a thread to avoid blocking GUI shutdown
            threading.Thread(target=self.server.stop, daemon=True).start()
        
        self.shutdown()

    # --- Periodic Update Loop ---

    def _schedule_updates(self) -> None:
        if not self.is_running: return
        
        try:
            self._process_update_queue()
            self._update_clock_and_uptime()
            self._update_performance_metrics()
        except Exception as e:
            print(f"Error in GUI update loop: {e}")
            traceback.print_exc()
            
        if self.root:
            self.root.after(1000, self._schedule_updates)

    def _process_update_queue(self) -> None:
        while not self.update_queue.empty():
            try:
                msg = self.update_queue.get_nowait()
                update_type, data = msg.get("type"), msg.get("data", {})
                
                # Route the update to the correct page or handler
                if page := self.pages.get(self.current_page_id):
                    if hasattr(page, f"handle_{update_type}_update"):
                        getattr(page, f"handle_{update_type}_update")(data)
                
                # Global handlers
                if update_type == 'log':
                    if log_page := self.pages.get('logs'):
                        if hasattr(log_page, "add_log_entry"):
                            log_page.add_log_entry(data.get("message", ""), data.get("level", "INFO"))
                elif update_type == 'status':
                    self._handle_global_status_update(data)

            except queue.Empty:
                break
            except Exception as e:
                print(f"Error processing update queue: {e}")
                traceback.print_exc()

    def _update_clock_and_uptime(self) -> None:
        if self.clock_label:
            self.clock_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if dashboard := self.pages.get('dashboard'):
            if hasattr(dashboard, "update_uptime"):
                dashboard.update_uptime()
                 
    def _update_performance_metrics(self) -> None:
        if not SYSTEM_MONITOR_AVAILABLE or not psutil: return
        
        now = datetime.now()
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        
        self.performance_data['cpu'].append(cpu)
        self.performance_data['memory'].append(mem)
        self.performance_data['time'].append(now)

        # Update charts on visible pages
        try:
            if self.pages.get('dashboard') and self.pages['dashboard'].winfo_ismapped():
                self.pages['dashboard'].update_performance_chart(self.performance_data)
        except (tk.TclError, AttributeError):
            pass  # Widget may have been destroyed or not mapped
        try:
            if self.pages.get('analytics') and self.pages['analytics'].winfo_ismapped():
                self.pages['analytics'].update_charts(self.performance_data)
        except (tk.TclError, AttributeError):
            pass  # Widget may have been destroyed or not mapped

    def _handle_global_status_update(self, data: Dict[str, Any]) -> None:
        """Updates components that are always visible, like the header."""
        running = data.get('running', False)
        if running:
            self.header_status_label.config(text="Server Online")
            self.header_status_pill.config(text="ONLINE", bootstyle="success-inverse")
        else:
            self.header_status_label.config(text="Server Offline")
            self.header_status_pill.config(text="OFFLINE", bootstyle="danger-inverse")
            
        # Update dashboard regardless of visibility
        if dashboard := self.pages.get('dashboard'):
            if hasattr(dashboard, 'handle_status_update'):
                dashboard.handle_status_update(data)
             
    def _play_audio_cue(self, event_name: str) -> None:
        """Plays a sound effect for a specific event if enabled."""
        if not PLAYSOUND_AVAILABLE or not self.settings.get('audio_cues'):
            return
            
        sound_map = {
            'startup': 'sounds/startup.wav',
            'success': 'sounds/success.wav',
            'failure': 'sounds/failure.wav',
            'connect': 'sounds/connect.wav',
            'disconnect': 'sounds/disconnect.wav',
        }
        
        if sound_file := sound_map.get(event_name):
            # Create dummy sound files if they don't exist
            # In a real app, these would be packaged
            sounds_dir = "sounds"
            if not os.path.exists(sounds_dir): os.makedirs(sounds_dir)
            sound_path = os.path.join(sounds_dir, f"{event_name}.wav")
            if not os.path.exists(sound_path):
                print(f"[INFO] Audio file not found: {sound_path}. Skipping.")
                # You would create a placeholder WAV here if needed for testing
                return

            try:
                # Run in a separate thread to prevent blocking the GUI
                threading.Thread(target=playsound, args=(sound_path,), daemon=True).start()
            except Exception as e:
                print(f"[ERROR] Could not play sound {sound_path}: {e}")

    def sync_current_server_state(self) -> None:
        """Synchronize GUI with current server state on initialization."""
        if not self.server: return
        
        status_data = {
            'running': getattr(self.server, 'running', False),
            'address': getattr(self.server, 'host', '0.0.0.0'),
            'port': getattr(self.server, 'port', 1256),
            'start_time': getattr(self.server, 'start_time', 0)
        }
        self.update_server_status(status_data)
        
        # Add more state syncs as needed
    
    @property
    def db_manager(self) -> Optional[ActualDBManager]:
        """Provides access to the database manager, with a fallback for standalone mode."""
        if self.server and hasattr(self.server, 'db_manager'):
            return self.server.db_manager
        
        if not DatabaseManager: return None
        
        if not self._fallback_db_manager:
            try:
                self._fallback_db_manager = DatabaseManager()
            except Exception as e:
                print(f"[ERROR] Could not create fallback DatabaseManager: {e}")
        return self._fallback_db_manager


# --- Page/View Classes ---

FrameBase = ttk_bootstrap.Frame if TTK_BOOTSTRAP_AVAILABLE else std_ttk.Frame

class BasePage(FrameBase):
    """Base class for all pages to ensure consistency."""
    def __init__(self, parent: tk.Widget, controller: EnhancedServerGUI) -> None:
        super().__init__(parent)
        self.controller = controller

    def on_show(self) -> None:
        """Called when the page is switched to. Override in subclasses."""
        pass
        
class StatCard(FrameBase):
    """A reusable card for displaying a title and key-value statistics."""
    def __init__(self, parent: tk.Widget, title: str, **kwargs: Any) -> None:
        card_style = {"padding": 15, "bootstyle": "light"} if TTK_BOOTSTRAP_AVAILABLE else {"relief": "raised", "borderwidth": 1}
        card_style.update(kwargs)
        super().__init__(parent, **card_style)
        
        # LabelClass is now defined globally
        self.labels: Dict[str, LabelClass] = {}
        
        title_style = {"bootstyle": "inverse-light"} if TTK_BOOTSTRAP_AVAILABLE else {"font": "-family {Segoe UI} -size 12 -weight bold"}
        LabelClass(self, text=title, font="-family {Segoe UI} -size 12 -weight bold", **title_style).pack(fill=tk.X, pady=(0, 10))
        
    def add_stat(self, key: str, label_text: str, default_value: str = "N/A") -> None:
        # FrameClass is now defined globally
        # LabelClass is now defined globally
        
        row_style = {"bootstyle": "light"} if TTK_BOOTSTRAP_AVAILABLE else {}
        row = FrameClass(self, **row_style)
        row.pack(fill=tk.X, pady=2)
        
        label_style = {"bootstyle": "secondary"} if TTK_BOOTSTRAP_AVAILABLE else {}
        LabelClass(row, text=f"{label_text}:", **label_style).pack(side=tk.LEFT)
        
        self.labels[key] = LabelClass(row, text=default_value, font="-family {Segoe UI} -size 10 -weight bold")
        self.labels[key].pack(side=tk.RIGHT)
        
    def update_stat(self, key: str, value: str, style: Optional[str] = None) -> None:
        if key in self.labels:
            self.labels[key].config(text=value)
            if style and TTK_BOOTSTRAP_AVAILABLE:
                self.labels[key].config(bootstyle=style)
            
            # Flash effect - only for ttkbootstrap
            if TTK_BOOTSTRAP_AVAILABLE:
                try:
                    original_style = self.cget('bootstyle')
                    self.config(bootstyle="info")
                    self.after(300, lambda: self.config(bootstyle=original_style))
                except Exception:
                    pass  # Skip flash effect if it fails

class DashboardPage(BasePage):
    def __init__(self, parent: tk.Widget, controller: EnhancedServerGUI) -> None:
        super().__init__(parent, controller)
        self.start_time = 0.0
        self._create_widgets()

    def _create_widgets(self) -> None:
        # Configure grid layout
        self.columnconfigure(0, weight=2, uniform="dashboard")
        self.columnconfigure(1, weight=1, uniform="dashboard")
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)

        # Top-Left: Status Cards
        # FrameClass is now defined globally
        status_panel = FrameClass(self)
        status_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        status_panel.rowconfigure(0, weight=1); status_panel.rowconfigure(1, weight=1)
        status_panel.columnconfigure(0, weight=1); status_panel.columnconfigure(1, weight=1)
        self._create_status_cards(status_panel)

        # Top-Right: Control Panel
        self._create_control_panel().grid(row=0, column=1, sticky=tk.NSEW, padx=(5, 0), pady=(0, 5))

        # Bottom-Left: Performance Chart
        self._create_performance_chart().grid(row=1, column=0, sticky=tk.NSEW, padx=(0, 5), pady=(5, 0))

        # Bottom-Right: Activity Log Ticker
        self._create_activity_ticker().grid(row=1, column=1, sticky=tk.NSEW, padx=(5, 0), pady=(5, 0))
        
    def _create_status_cards(self, parent: ttk.Frame) -> None:
        self.server_card = StatCard(parent, "Server Status")
        self.server_card.add_stat("status", "Status", "Stopped")
        self.server_card.add_stat("address", "Address")
        self.server_card.add_stat("uptime", "Uptime", "00:00:00")
        self.server_card.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        self.client_card = StatCard(parent, "Client Stats")
        self.client_card.add_stat("connected", "Connected", "0")
        self.client_card.add_stat("total", "Total", "0")
        self.client_card.add_stat("active_transfers", "Active Transfers", "0")
        self.client_card.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)
        
        self.transfer_card = StatCard(parent, "Transfer Stats")
        self.transfer_card.add_stat("rate", "Transfer Rate", "0 KB/s")
        self.transfer_card.add_stat("total_transferred", "Total Transferred", "0 MB")
        self.transfer_card.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        self.maint_card = StatCard(parent, "Maintenance")
        self.maint_card.add_stat("last_cleanup", "Last Cleanup", "Never")
        self.maint_card.add_stat("files_cleaned", "Files Cleaned", "0")
        self.maint_card.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)

    def _create_control_panel(self):
        # FrameClass is now defined globally
        # LabelClass is now defined globally
        # ButtonClass is now defined globally
        
        card_style = {"padding": 15, "bootstyle": "light"} if TTK_BOOTSTRAP_AVAILABLE else {"relief": "raised", "borderwidth": 1}
        card = FrameClass(self, **card_style)
        
        label_style = {"bootstyle": "inverse-light"} if TTK_BOOTSTRAP_AVAILABLE else {}
        LabelClass(card, text="Control Panel", font="-family {Segoe UI} -size 12 -weight bold", **label_style).pack(fill=tk.X, pady=(0, 10))

        btn_frame_style = {"bootstyle": "light"} if TTK_BOOTSTRAP_AVAILABLE else {}
        btn_frame = FrameClass(card, **btn_frame_style)
        btn_frame.pack(fill=tk.BOTH, expand=True)
        btn_frame.columnconfigure((0, 1), weight=1)
        btn_frame.rowconfigure((0, 1, 2), weight=1)

        # Create buttons with conditional styling
        start_style = {"bootstyle": "success"} if TTK_BOOTSTRAP_AVAILABLE else {"bg": "green", "fg": "white"}
        stop_style = {"bootstyle": "danger"} if TTK_BOOTSTRAP_AVAILABLE else {"bg": "red", "fg": "white"}
        restart_style = {"bootstyle": "warning"} if TTK_BOOTSTRAP_AVAILABLE else {"bg": "orange", "fg": "white"}
        db_style = {"bootstyle": "info-outline"} if TTK_BOOTSTRAP_AVAILABLE else {"bg": "lightblue"}
        exit_style = {"bootstyle": "secondary-outline"} if TTK_BOOTSTRAP_AVAILABLE else {"bg": "lightgray"}
        
        self.start_btn = ButtonClass(btn_frame, text="Start", command=lambda: self._handle_start_server(), **start_style)
        self.stop_btn = ButtonClass(btn_frame, text="Stop", state=tk.DISABLED, command=lambda: self._handle_stop_server(), **stop_style)
        self.restart_btn = ButtonClass(btn_frame, text="Restart", state=tk.DISABLED, command=lambda: self._handle_restart_server(), **restart_style)
        db_btn = ButtonClass(btn_frame, text="Backup DB", command=lambda: self._handle_backup_db(), **db_style)
        exit_btn = ButtonClass(btn_frame, text="Exit GUI", command=self.controller._on_window_close, **exit_style)

        self.start_btn.grid(row=0, column=0, sticky=tk.NSEW, padx=2, pady=2)
        self.stop_btn.grid(row=0, column=1, sticky=tk.NSEW, padx=2, pady=2)
        self.restart_btn.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, padx=2, pady=2)
        db_btn.grid(row=2, column=0, sticky=tk.NSEW, padx=2, pady=2)
        exit_btn.grid(row=2, column=1, sticky=tk.NSEW, padx=2, pady=2)
        return card

    def _create_performance_chart(self):
        # FrameClass is now defined globally
        # LabelClass is now defined globally
        
        card_style = {"padding": 15, "bootstyle": "light"} if TTK_BOOTSTRAP_AVAILABLE else {"relief": "raised", "borderwidth": 1}
        card = FrameClass(self, **card_style)
        
        label_style = {"bootstyle": "inverse-light"} if TTK_BOOTSTRAP_AVAILABLE else {}
        LabelClass(card, text="Live System Performance", font="-family {Segoe UI} -size 12 -weight bold", **label_style).pack(fill=tk.X, pady=(0, 10))
        
        if not CHARTS_AVAILABLE or not FigureCanvasTkAgg:
            fallback_style = {"bootstyle": "secondary"} if TTK_BOOTSTRAP_AVAILABLE else {}
            LabelClass(card, text="Charts disabled: matplotlib not found.", **fallback_style).pack(expand=True)
            self.chart_canvas = None
            return card

        if TTK_BOOTSTRAP_AVAILABLE:
            style = ttk_bootstrap.Style.get_instance()
            theme_colors = style.colors
        else:
            # Fallback colors for standard tkinter
            theme_colors = {
                'light': '#ffffff',
                'bg': '#f8f9fa',
                'fg': '#000000',
                'border': '#dee2e6',
                'info': '#0dcaf0',
                'success': '#198754'
            }

        self.fig = Figure(figsize=(5, 2.5), dpi=100, facecolor=theme_colors.get('light'))
        self.ax = self.fig.add_subplot(111)
        
        self.fig.autofmt_xdate()
        self.ax.set_facecolor(theme_colors.get('bg'))
        self.ax.tick_params(colors=theme_colors.get('fg'), labelsize=8)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        for spine in self.ax.spines.values():
            spine.set_color(theme_colors.get('border'))
        
        self.fig.tight_layout(pad=2)
        
        self.cpu_line, = self.ax.plot([], [], color=theme_colors.get('info'), lw=2, label="CPU %")
        self.mem_line, = self.ax.plot([], [], color=theme_colors.get('success'), lw=2, label="Memory %")
        
        self.ax.set_ylim(0, 100)
        self.ax.legend(loc='upper left', fontsize=8, facecolor=theme_colors.get('light'), labelcolor=theme_colors.get('fg'), frameon=False)
        
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=card)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return card

    def _create_activity_ticker(self):
        # FrameClass is now defined globally
        # LabelClass is now defined globally
        
        card_style = {"padding": 15, "bootstyle": "light"} if TTK_BOOTSTRAP_AVAILABLE else {"relief": "raised", "borderwidth": 1}
        card = FrameClass(self, **card_style)
        
        label_style = {"bootstyle": "inverse-light"} if TTK_BOOTSTRAP_AVAILABLE else {}
        LabelClass(card, text="Recent Activity", font="-family {Segoe UI} -size 12 -weight bold", **label_style).pack(fill=tk.X, pady=(0, 10))
        
        if TTK_BOOTSTRAP_AVAILABLE and ScrolledText:
            scroll_style = {"padding": 10, "hbar": False, "bootstyle": "round"}
            self.activity_text = ScrolledText(card, **scroll_style)
            self.activity_text.pack(fill=tk.BOTH, expand=True)
            # ttkbootstrap ScrolledText doesn't support state configuration
            # So we'll disable editing by binding to ignore key events
            try:
                self.activity_text.configure(state=tk.DISABLED)
            except tk.TclError:
                # If state option not supported, make it read-only by binding events
                self.activity_text.bind("<Key>", lambda e: "break")
                self.activity_text.bind("<Button-1>", lambda e: self.activity_text.focus_set())
        else:
            # Fallback to standard Text widget with scrollbar
            text_frame = FrameClass(card)
            text_frame.pack(fill=tk.BOTH, expand=True)
            self.activity_text = tk.Text(text_frame, wrap=tk.WORD)
            scrollbar = std_ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.activity_text.yview)
            self.activity_text.configure(yscrollcommand=scrollbar.set)
            self.activity_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.activity_text.pack(fill=tk.BOTH, expand=True)
            self.activity_text.configure(state=tk.DISABLED)
        return card

    def handle_status_update(self, data: Dict[str, Any]) -> None:
        self.start_time = data.get('start_time', self.start_time)
        running = data.get('running', False)
        status_text, style = ("Running", "success") if running else ("Stopped", "danger")
        
        self.server_card.update_stat("status", status_text, style)
        self.server_card.update_stat("address", f"{data.get('address', 'N/A')}:{data.get('port', 0)}")
        
        self.start_btn.config(state=tk.DISABLED if running else tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL if running else tk.DISABLED)
        self.restart_btn.config(state=tk.NORMAL if running else tk.DISABLED)
        
        if not running:
            self.update_uptime()

    def handle_client_stats_update(self, data: Dict[str, Any]) -> None:
        self.client_card.update_stat("connected", str(data.get('connected', 0)))
        self.client_card.update_stat("total", str(data.get('total', 0)))
        self.client_card.update_stat("active_transfers", str(data.get('active_transfers', 0)))

    def handle_transfer_stats_update(self, data: Dict[str, Any]) -> None:
        rate = data.get('rate_kbps', 0.0)
        total = data.get('bytes_transferred', 0) / (1024*1024)
        self.transfer_card.update_stat("rate", f"{rate:.1f} KB/s")
        self.transfer_card.update_stat("total_transferred", f"{total:.2f} MB")
        
    def handle_maintenance_update(self, data: Dict[str, Any]) -> None:
        last_cleanup = data.get('last_cleanup', 'Never')
        if isinstance(last_cleanup, str) and last_cleanup != 'Never':
            try:
                last_cleanup = datetime.fromisoformat(last_cleanup).strftime('%Y-%m-%d %H:%M')
            except ValueError:
                pass # Keep original string if format is unexpected
        self.maint_card.update_stat("last_cleanup", str(last_cleanup))
        self.maint_card.update_stat("files_cleaned", str(data.get('files_cleaned', 0)))

    def update_uptime(self) -> None:
        uptime_str = "00:00:00"
        is_server_running = self.start_time > 0
        if is_server_running:
            delta = timedelta(seconds=int(time.time() - self.start_time))
            uptime_str = str(delta)
        self.server_card.update_stat("uptime", uptime_str)

    def update_performance_chart(self, data: Dict[str, Deque[Any]]) -> None:
        if not self.chart_canvas or not self.ax: return
        
        times = list(data['time'])
        if len(times) > 1:
            self.ax.set_xlim(times[0], times[-1])
            self.cpu_line.set_data(times, list(data['cpu']))
            self.mem_line.set_data(times, list(data['memory']))
            self.chart_canvas.draw_idle()
            
    def _handle_start_server(self) -> None:
        """Handle start server button click"""
        self.controller._play_audio_cue("startup")
        # TODO: Add actual server start logic
        
    def _handle_stop_server(self) -> None:
        """Handle stop server button click"""
        self.controller._play_audio_cue("disconnect")
        # TODO: Add actual server stop logic
        
    def _handle_restart_server(self) -> None:
        """Handle restart server button click"""
        self.controller._play_audio_cue("startup")
        # TODO: Add actual server restart logic
        
    def _handle_backup_db(self) -> None:
        """Handle backup database button click"""
        self.controller._play_audio_cue("success")
        # TODO: Add actual database backup logic

class ClientsPage(BasePage):
    def __init__(self, parent: tk.Widget, controller: EnhancedServerGUI) -> None:
        super().__init__(parent, controller)
        # LabelClass is now defined globally
        LabelClass(self, text="Clients Page - Content Coming Soon", font="-size 20").pack(expand=True)
        # TODO: Implement tksheet and Master-Detail view
        
    def on_show(self) -> None:
        print("Switched to Clients Page. Refreshing data...")
        # self.refresh_client_data()

class AnalyticsPage(BasePage):
    def __init__(self, parent: tk.Widget, controller: EnhancedServerGUI) -> None:
        super().__init__(parent, controller)
        # LabelClass is now defined globally
        LabelClass(self, text="Analytics Page - Content Coming Soon", font="-size 20").pack(expand=True)
        # TODO: Implement multiple, larger matplotlib charts
        
    def update_charts(self, data: Dict[str, Deque[Any]]) -> None:
        # Placeholder for updating detailed charts on this page
        pass

class SettingsPage(BasePage):
    def __init__(self, parent: tk.Widget, controller: EnhancedServerGUI) -> None:
        super().__init__(parent, controller)
        self.setting_vars: Dict[str, tk.StringVar] = {}
        self._create_widgets()

    def _create_widgets(self) -> None:
        if TTK_BOOTSTRAP_AVAILABLE and ScrolledFrame:
            scrolled_frame = ScrolledFrame(self, autohide=True)
        else:
            # Fallback to regular frame with scrollbars
            canvas = tk.Canvas(self)
            scrollbar = std_ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
            scrolled_frame = std_ttk.Frame(canvas)
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.create_window((0, 0), window=scrolled_frame, anchor="nw")
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            # For now, just use a simple frame
            scrolled_frame = (ttk_bootstrap.Frame if TTK_BOOTSTRAP_AVAILABLE else std_ttk.Frame)(self)
            
        scrolled_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # General Settings Card
        # FrameClass is now defined globally
        # LabelClass is now defined globally
        # EntryClass is now defined globally
        # ButtonClass is now defined globally
        
        card_style = {"padding": 20, "bootstyle": "light"} if TTK_BOOTSTRAP_AVAILABLE else {"relief": "raised", "borderwidth": 1}
        general_card = FrameClass(scrolled_frame, **card_style)
        general_card.pack(fill=tk.X, pady=(0, 15))
        LabelClass(general_card, text="Server Configuration", font="-size 14 -weight bold").pack(anchor=tk.W, pady=(0, 10))
        
        settings_to_display = {
            'port': "Server Port", 'storage_dir': "Storage Directory", 'max_clients': "Max Clients",
            'session_timeout': "Session Timeout (min)", 'maintenance_interval': "Maintenance Interval (sec)"
        }
        for key, label in settings_to_display.items():
            self._create_setting_entry(general_card, key, label)

        # UI Settings Card
        ui_card = FrameClass(scrolled_frame, **card_style)
        ui_card.pack(fill=tk.X, pady=(0, 15))
        LabelClass(ui_card, text="Interface Settings", font="-size 14 -weight bold").pack(anchor=tk.W, pady=(0, 10))
        
        # Theme Selector
        theme_frame = FrameClass(ui_card)
        theme_frame.pack(fill=tk.X, pady=5)
        LabelClass(theme_frame, text="Theme:", width=25, anchor=tk.W).pack(side=tk.LEFT)
        theme_names = []
        theme_names = ['cyborg', 'darkly', 'flatly', 'journal', 'litera']  # default themes
        if TTK_BOOTSTRAP_AVAILABLE and self.controller.root and hasattr(self.controller.root, 'style'):
            try:
                theme_names = self.controller.root.style.theme_names()
            except Exception:
                pass  # Use default themes
                
        ComboboxClass = ttk_bootstrap.Combobox if TTK_BOOTSTRAP_AVAILABLE else std_ttk.Combobox
        self.theme_combo = ComboboxClass(theme_frame, values=theme_names, state="readonly")
        self.theme_combo.set(self.controller.settings.get('theme'))
        self.theme_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Audio Cues Toggle
        self.audio_var = tk.BooleanVar(value=self.controller.settings.get('audio_cues'))
        CheckbuttonClass = ttk_bootstrap.Checkbutton if TTK_BOOTSTRAP_AVAILABLE else std_ttk.Checkbutton
        check_style = {"bootstyle": "primary-round-toggle"} if TTK_BOOTSTRAP_AVAILABLE else {}
        audio_check = CheckbuttonClass(ui_card, variable=self.audio_var, text="Enable Audio Cues", **check_style)
        audio_check.pack(anchor=tk.W, pady=10)

        # Save Button
        save_style = {"bootstyle": "success"} if TTK_BOOTSTRAP_AVAILABLE else {"bg": "green", "fg": "white"}
        save_btn = ButtonClass(scrolled_frame, text="Save Settings", command=self._save_settings, **save_style)
        save_btn.pack(anchor=tk.E, pady=10)

    def _create_setting_entry(self, parent, key: str, label: str) -> None:
        # FrameClass is now defined globally
        # LabelClass is now defined globally
        # EntryClass is now defined globally
        
        frame = FrameClass(parent)
        frame.pack(fill=tk.X, pady=5)
        LabelClass(frame, text=f"{label}:", width=25, anchor=tk.W).pack(side=tk.LEFT)
        
        var = tk.StringVar(value=str(self.controller.settings.get(key, '')))
        self.setting_vars[key] = var
        
        entry = EntryClass(frame, textvariable=var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _save_settings(self) -> None:
        try:
            # Save server settings
            for key, var in self.setting_vars.items():
                self.controller.settings.set(key, var.get())
            # Coerce numerical settings
            self.controller.settings.set('port', int(self.controller.settings.get('port')))
            self.controller.settings.set('max_clients', int(self.controller.settings.get('max_clients')))

            # Save UI settings
            self.controller.settings.set('theme', self.theme_combo.get())
            self.controller.settings.set('audio_cues', self.audio_var.get())

            if self.controller.settings.save():
                if self.controller.toast:
                    self.controller.toast.show_toast("Settings Saved!", "Settings have been successfully saved.")
                else:
                    print("[INFO] Settings saved successfully.")
                # Apply theme change if different
                current_theme = None
                if self.controller.root and hasattr(self.controller.root, 'style') and self.controller.root.style:
                    try:
                        current_theme = self.controller.root.style.theme_use()
                    except Exception:
                        current_theme = None
                if self.controller.root and current_theme and current_theme != self.theme_combo.get():
                    messagebox.showinfo("Theme Change", "Theme will be applied on next application restart.", parent=self.controller.root)
            else:
                if self.controller.toast:
                    try:
                        self.controller.toast.show_toast("Error Saving", "Could not save settings to file.", bootstyle="danger")
                    except Exception:
                        print("[ERROR] Could not save settings to file.")
                else:
                    print("[ERROR] Could not save settings to file.")

        except (ValueError, TypeError) as e:
            if self.controller.toast:
                try:
                    self.controller.toast.show_toast("Invalid Input", f"Please check your settings. Error: {e}", bootstyle="danger")
                except Exception:
                    print(f"[ERROR] Invalid input in settings: {e}")
            else:
                print(f"[ERROR] Invalid input in settings: {e}")

# --- Standalone Execution ---
def launch_standalone() -> None:
    print("[INFO] Launching Server GUI in standalone mode...")
    gui = EnhancedServerGUI()
    if gui.initialize():
        try:
            # The main thread waits for the GUI thread to finish
            if gui.gui_thread:
                gui.gui_thread.join()
        except KeyboardInterrupt:
            print("\n[INFO] Shutdown signal received.")
            gui.shutdown()
    else:
        print("[FATAL] GUI could not be initialized.")
    print("[INFO] Application has exited.")

if __name__ == "__main__":
    # Ensure this runs only when the script is executed directly
    launch_standalone()