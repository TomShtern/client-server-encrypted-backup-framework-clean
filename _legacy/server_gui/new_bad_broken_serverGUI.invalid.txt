# -*- coding: utf-8 -*-
# ServerGUI.py - The core application shell for the Encrypted Backup Server.
# This file manages the main window, navigation, page loading, and backend communication.
# Version: 2.1 - Re-architected for professional quality, features, and aesthetics.

from __future__ import annotations

# Import UTF-8 solution FIRST for proper Unicode handling
try:
    import Shared.utils.utf8_solution
except ImportError:
    # Add project root to path for direct execution
    import os
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    try:
        import Shared.utils.utf8_solution
    except ImportError:
        pass  # UTF-8 solution not available, continue without it
import sys
import os
import threading
import traceback
from collections import deque
from datetime import datetime
import time
import queue
import json
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.constants import LEFT, RIGHT, TOP, X, Y, BOTH, END, CENTER, BOTTOM
from typing import (Dict, Optional, Any, Deque, TYPE_CHECKING, Protocol,
                    runtime_checkable, cast)

# --- Type Hinting Setup for Backend, Pages, and DB ---
# This is the standard, non-negotiable pattern for type safety and avoiding circular imports.
if TYPE_CHECKING:
    from .gui_pages.dashboard import DashboardPage
    from .gui_pages.clients import ClientsPage
    from .gui_pages.files import FilesPage
    from .gui_pages.analytics import AnalyticsPage
    from .gui_pages.database_page import DatabasePage
    from .gui_pages.logs import LogsPage
    from .gui_pages.settings import SettingsPage
    from server.database import DatabaseManager # For the fallback manager
    import pystray
    from PIL import Image

# --- Protocol for Type-Checking the Server Instance ---
# Establishes a formal, verifiable contract with the server backend.
@runtime_checkable
class BackupServerLike(Protocol):
    running: bool
    db_manager: Any
    clients: Dict[bytes, Any]
    network_server: Any
    file_transfer_manager: Any
    host: str
    port: int
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def apply_settings(self, settings: Dict[str, Any]) -> None: ...

# --- Graceful Optional Dependency Imports ---
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *  # type: ignore[reportWildcardImportFromLibrary]
    from ttkbootstrap.toast import ToastNotification
except ImportError:
    print("[FATAL] ttkbootstrap is required. Please run: pip install ttkbootstrap")
    sys.exit(1)

try:
    import psutil
    SYSTEM_MONITOR_AVAILABLE = True
except ImportError:
    psutil = None
    SYSTEM_MONITOR_AVAILABLE = False
    print("[INFO] psutil not available. System monitoring will be disabled.")

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("[INFO] pystray/Pillow not available. System tray will be disabled.")

try:
    from playsound import playsound  # type: ignore[reportMissingImports]
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    def playsound(_path: str, _block: bool = False) -> None: pass
    print("[INFO] playsound not available. Audio cues will be disabled.")

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

# --- Project-Specific Imports ---
# Handle both direct execution and package execution
try:
    # Try relative import first (when run as package)
    from .gui_pages.base_page import BasePage
    from .assets.asset_manager import AssetManager
except ImportError:
    # Fallback to absolute import (when run directly)
    import os
    import sys
    # Add project root to path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from python_server.server_gui.gui_pages.base_page import BasePage
    from python_server.server_gui.assets.asset_manager import AssetManager

# Import DatabaseManager for standalone mode, with graceful fallback.
try:
    from server.database import DatabaseManager
except ImportError:
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from server.database import DatabaseManager
    except ImportError:
        DatabaseManager = None # type: ignore
        print("[WARNING] DatabaseManager not available - Database tab will be disabled.")


class ServerGUI:
    """
    The main class for the Encrypted Backup Server GUI.
    This class is the application controller, orchestrating the main window, pages,
    and all communication with the server logic.
    """
    def __init__(self, server_instance: Optional[BackupServerLike] = None) -> None:
        self.server = server_instance
        self.settings: Dict[str, Any] = self._load_settings()
        self._fallback_db_manager: Optional[Any] = None  # DatabaseManager when available

        self.root = ttk.Window(
            themename=self.settings.get('theme', 'cyborg'),
            title="Encrypted Backup Server",
            minsize=(1200, 800)
        )
        self.root.geometry(self.settings.get('geometry', '1400x900'))
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # --- Core Application State ---
        self.is_running = False
        self.current_page_id: str = "dashboard"
        self.update_queue: queue.Queue[Dict[str, Any]] = queue.Queue()
        self.performance_data: Dict[str, Deque[Any]] = {
            'cpu': deque(maxlen=120),
            'memory': deque(maxlen=120),
            'time': deque(maxlen=120)
        }

        # --- Managers and Controllers ---
        self.asset_manager = AssetManager()
        self.tray_icon: Optional[Any] = None  # pystray.Icon when available

        # --- UI Component References ---
        self.pages: Dict[str, BasePage] = {}
        self.nav_buttons: Dict[str, ttk.Button] = {}
        self.title_bar: Optional[ttk.Frame] = None
        self.status_indicator: Optional[tk.Canvas] = None
        self.status_indicator_oval: int = 0
        self.status_label: Optional[ttk.Label] = None
        self.clock_label: Optional[ttk.Label] = None
        self.warning_banner: Optional[ttk.Label] = None

        # --- For Custom Title Bar Dragging ---
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # --- Initialize UI and background tasks ---
        self._setup_styles()
        self._setup_custom_title_bar()
        self._setup_main_layout()
        self._load_pages()
        self._create_system_tray()
        self._schedule_updates()
        
        # Final setup step, sync with server after UI is built
        self.root.after(100, self.sync_current_server_state)

    def run(self) -> None:
        """Starts the GUI main loop. This is a blocking call."""
        self.is_running = True
        print("[OK] GUI initialized successfully!")
        self.root.mainloop()
        self.is_running = False
        print("GUI main loop ended.")

    @property
    def effective_db_manager(self) -> Optional[Any]:  # DatabaseManager when available
        """Gets the DB manager from the server or creates a fallback for standalone mode."""
        if self.server and hasattr(self.server, 'db_manager') and self.server.db_manager:
            return self.server.db_manager
        
        if DatabaseManager is None: 
            return None
            
        if self._fallback_db_manager is None:
            try:
                self._fallback_db_manager = DatabaseManager()  # type: ignore[reportUnknownMemberType]
            except Exception as e:
                print(f"[WARNING] Could not create fallback DatabaseManager: {e}")
                self.show_toast("Could not initialize DB Manager", "error")
                return None
        return self._fallback_db_manager

    # --- UI Setup Methods ---

    def _setup_styles(self) -> None:
        """Defines custom ttk styles for a bespoke, polished look."""
        s = self.root.style
        # Navigation buttons: No border, larger padding for a modern feel
        s.configure('Nav.TButton', font=('Segoe UI', 11), borderwidth=0, padding=(20, 10))  # type: ignore[reportUnknownMemberType]
        s.map('Nav.TButton',  # type: ignore[reportUnknownMemberType]
              background=[('active', getattr(s.colors, 'primary', '#007acc')),  # type: ignore[reportUnknownMemberType]
                         ('!active', getattr(s.colors, 'secondary', '#404040'))],  # type: ignore[reportUnknownMemberType]
              foreground=[('!disabled', getattr(s.colors, 'light', '#ffffff'))])  # type: ignore[reportUnknownMemberType]
        # Active navigation button: A distinct style to indicate the current page
        s.configure('NavActive.TButton', font=('Segoe UI Semibold', 11), borderwidth=0, padding=(20, 10))  # type: ignore[reportUnknownMemberType]
        s.map('NavActive.TButton', background=[('!disabled', getattr(s.colors, 'primary', '#007acc'))])  # type: ignore[reportUnknownMemberType,reportUnknownMemberType]
        # Pill-shaped entry for a modern global search bar
        s.configure('Pill.TEntry', relief='flat', borderwidth=10,  # type: ignore[reportUnknownMemberType]
                   bordercolor=getattr(s.colors, 'secondary', '#404040'))  # type: ignore[reportUnknownMemberType]
        # Custom title bar buttons for a seamless look
        s.configure('Titlebar.TButton', font=('Segoe UI Symbol', 10), padding=5, relief='flat', borderwidth=0)  # type: ignore[reportUnknownMemberType]
        s.map('Titlebar.TButton', background=[('active', getattr(s.colors, 'selectbg', '#0066cc')),  # type: ignore[reportUnknownMemberType]
                                            ('!active', getattr(s.colors, 'primary', '#007acc'))])  # type: ignore[reportUnknownMemberType]
        s.configure('Titlebar.danger.TButton', font=('Segoe UI Symbol', 10), padding=5, relief='flat', borderwidth=0)  # type: ignore[reportUnknownMemberType]
        s.map('Titlebar.danger.TButton', background=[('active', getattr(s.colors, 'danger', '#dc3545')),  # type: ignore[reportUnknownMemberType]
                                                   ('!active', getattr(s.colors, 'primary', '#007acc'))])  # type: ignore[reportUnknownMemberType]

    def _setup_custom_title_bar(self) -> None:
        """Creates a custom, draggable title bar (Feature #15)."""
        self.root.overrideredirect(True)

        self.title_bar = ttk.Frame(self.root, style='primary.TFrame', height=50)
        self.title_bar.pack(fill=X, side=TOP)
        self.title_bar.pack_propagate(False)

        # Bind dragging events
        self.title_bar.bind("<ButtonPress-1>", self._on_drag_start)
        self.title_bar.bind("<B1-Motion>", self._on_drag_motion)

        # Left side: Icon and Title
        left_frame = ttk.Frame(self.title_bar, style='primary.TFrame')
        left_frame.pack(side=LEFT, padx=10, fill=Y)
        if logo_icon := self.asset_manager.get_icon('logo_small'):
            ttk.Label(left_frame, image=logo_icon, style='primary.TLabel').pack(side=LEFT)
        ttk.Label(left_frame, text="Encrypted Backup Server", font=('Segoe UI', 12, 'bold'), style='primary.TLabel').pack(side=LEFT, padx=10)

        # Right side: Window controls
        right_frame = ttk.Frame(self.title_bar, style='primary.TFrame')
        right_frame.pack(side=RIGHT, padx=5, fill=Y)
        ttk.Button(right_frame, text="—", command=self.root.iconify, style='Titlebar.TButton', width=4).pack(side=LEFT)
        ttk.Button(right_frame, text="▢", command=self._toggle_maximize, style='Titlebar.TButton', width=4).pack(side=LEFT)
        ttk.Button(right_frame, text="✕", command=self._on_window_close, style='Titlebar.danger.TButton', width=4).pack(side=LEFT)

        # Center: Global Search (Feature #Refined 5)
        search_frame = ttk.Frame(self.title_bar, style='primary.TFrame')
        search_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=50, pady=8)
        search_entry = ttk.Entry(search_frame, style='Pill.TEntry', font=('Segoe UI', 11))
        search_entry.pack(fill=BOTH, expand=True)
        search_entry.insert(0, '🔍 Search clients, files, logs...')
        search_entry.bind("<FocusIn>", lambda e: e.widget.delete(0, END) if "Search" not in e.widget.get() else None)
        search_entry.bind("<FocusOut>", lambda e: e.widget.insert(0, '🔍 Search clients, files, logs...') if not e.widget.get() else None)

    def _setup_main_layout(self) -> None:
        """Creates the main sidebar and content area layout."""
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=BOTH, expand=True)

        sidebar = ttk.Frame(main_container, style='secondary.TFrame', width=240)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)

        self.content_area = ttk.Frame(main_container)
        self.content_area.pack(side=LEFT, fill=BOTH, expand=True)

        self._populate_sidebar(sidebar)

    def _populate_sidebar(self, sidebar: ttk.Frame) -> None:
        """Creates the navigation buttons and status indicators in the sidebar."""
        status_frame = ttk.Frame(sidebar, style='secondary.TFrame')
        status_frame.pack(fill=X, pady=20, padx=10)

        self.status_indicator = tk.Canvas(status_frame, width=20, height=20, 
                                        bg=getattr(self.root.style.colors, 'secondary', '#404040'),  # type: ignore[reportUnknownMemberType]
                                        highlightthickness=0)
        self.status_indicator.pack(side=LEFT, padx=(5, 10))
        self.status_indicator_oval = self.status_indicator.create_oval(4, 4, 16, 16, 
                                                                     fill=getattr(self.root.style.colors, 'danger', '#dc3545'),  # type: ignore[reportUnknownMemberType]
                                                                     outline="")
        self.status_label = ttk.Label(status_frame, text="Server Offline", style='secondary.TLabel', font=('Segoe UI', 10, 'bold'))
        self.status_label.pack(side=LEFT, expand=True, fill=X)
        
        ttk.Separator(sidebar).pack(fill=X, padx=10, pady=10)

        page_definitions = [
            ("dashboard", "Dashboard", "house-door-fill"), ("clients", "Clients", "people-fill"),
            ("files", "Files", "file-earmark-zip-fill"), ("analytics", "Analytics", "graph-up-arrow"),
            ("database", "Database", "database-fill"), ("logs", "Logs", "file-text-fill"),
            ("settings", "Settings", "gear-fill")
        ]
        for page_id, text, icon_name in page_definitions:
            icon = self.asset_manager.get_icon(icon_name)
            btn_kwargs = {
                'text': f" {text}",
                'compound': LEFT,
                'command': lambda p=page_id: self._switch_page(p),
                'style': 'Nav.TButton'
            }
            if icon:
                btn_kwargs['image'] = icon
            btn = ttk.Button(sidebar, **btn_kwargs)
            btn.pack(fill=X, padx=10, pady=3)
            self.nav_buttons[page_id] = btn
            
        footer = ttk.Frame(sidebar, style='secondary.TFrame')
        footer.pack(side=BOTTOM, fill=X, pady=10)
        self.clock_label = ttk.Label(footer, text="", style='secondary.TLabel', font=('Segoe UI', 9))
        self.clock_label.pack()

    def _load_pages(self) -> None:
        """Dynamically imports and instantiates all page modules."""
        page_modules = {
            "dashboard": ".gui_pages.dashboard", "clients": ".gui_pages.clients",
            "files": ".gui_pages.files", "analytics": ".gui_pages.analytics",
            "database": ".gui_pages.database_page", "logs": ".gui_pages.logs",
            "settings": ".gui_pages.settings"
        }
        from importlib import import_module
        for page_id, module_path in page_modules.items():
            try:
                # Try package-relative import first
                try:
                    module = import_module(module_path, package='server_gui')
                except ImportError:
                    # Fallback to absolute import for direct execution
                    abs_module_path = f"python_server.server_gui.{module_path[1:]}"
                    module = import_module(abs_module_path)
                PageClass = getattr(module, f"{page_id.title().replace('_', '')}Page")
                self.pages[page_id] = PageClass(self.content_area, self)
            except (ImportError, AttributeError) as e:
                print(f"[ERROR] Could not load page '{page_id}': {e}")
                error_page = ttk.Frame(self.content_area)
                ttk.Label(error_page, text=f"Error loading {page_id} page.", font=('Segoe UI', 16), style='danger.TLabel').pack(pady=50)
                self.pages[page_id] = cast(BasePage, error_page)

    def _switch_page(self, page_id: str) -> None:
        """Hides the current page and shows the selected one with a subtle animation."""
        if page_id not in self.pages or page_id == self.current_page_id:
            return
        
        if self.current_page_id in self.pages:
            self.pages[self.current_page_id].place_forget()
            
        self.current_page_id = page_id
        self.settings['last_tab'] = page_id

        page_to_show = self.pages[page_id]
        if hasattr(page_to_show, 'on_show'): page_to_show.on_show()

        page_to_show.place(relx=0, rely=0.03, relwidth=1, relheight=1) # Place off-screen
        self._animate_page_rise(page_to_show) # Animate into view

        for pid, button in self.nav_buttons.items():
            button.configure(style='Nav.TButton' if pid != page_id else 'NavActive.TButton')

    def _animate_page_rise(self, page: ttk.Frame, current_y: float = 0.03) -> None:
        """Helper to animate a page rising into its final position."""
        if not page.winfo_exists() or page is not self.pages[self.current_page_id]: return

        new_y = current_y - 0.005
        if new_y <= 0:
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
        else:
            page.place(relx=0, rely=new_y, relwidth=1, relheight=1)
            self.root.after(5, lambda: self._animate_page_rise(page, new_y))

    # --- Event Handlers & System Tray ---

    def _on_window_close(self) -> None:
        """Handles the window close event, confirming with the user (Feature #14)."""
        confirm = True
        if self.server and self.server.running:
            confirm = messagebox.askyesno("Exit Confirmation", "The server is running.\nStop server and exit?", icon='warning')
        
        if confirm:
            if self.server and self.server.running: self.stop_server()
            self.shutdown()

    def _on_drag_start(self, event: tk.Event) -> None: 
        self._drag_start_x, self._drag_start_y = event.x, event.y
        
    def _on_drag_motion(self, event: tk.Event) -> None:
        dx, dy = event.x - self._drag_start_x, event.y - self._drag_start_y
        new_x = self.root.winfo_x() + dx
        new_y = self.root.winfo_y() + dy
        self.root.geometry(f"+{new_x}+{new_y}")
    def _toggle_maximize(self) -> None: 
        from contextlib import suppress
        with suppress(tk.TclError):
            current_state = self.root.attributes('-zoomed')  # type: ignore[reportUnknownMemberType]
            self.root.attributes('-zoomed', not current_state)  # type: ignore[reportUnknownMemberType]

    def _create_system_tray(self) -> None:
        if not TRAY_AVAILABLE:
            return
        from contextlib import suppress
        with suppress(ImportError):
            import pystray
            menu = (pystray.MenuItem('Show/Hide', self._toggle_window, default=True), 
                   pystray.MenuItem('Quit', self._quit_app))
            if image := self.asset_manager.get_image('logo_tray'):
                self.tray_icon = pystray.Icon("ServerGUI", image, "Encrypted Backup Server", menu)
                if hasattr(self.tray_icon, 'run'):
                    threading.Thread(target=self.tray_icon.run, daemon=True).start()  # type: ignore[reportUnknownMemberType]

    def _toggle_window(self) -> None:
        if self.root.state() == 'withdrawn':
            self.root.deiconify()
        else:
            self.root.withdraw()
    def _quit_app(self) -> None:
        if self.tray_icon and hasattr(self.tray_icon, 'stop'):
            self.tray_icon.stop()  # type: ignore
        self.root.after(100, self._on_window_close)

    # --- Server Control & Action Methods (The Controller's Public API) ---

    def start_server(self) -> None:
        if not self.server: self.show_toast("Server instance not available.", "error"); return
        if self.server.running: self.show_toast("Server is already running.", "warning"); return
        threading.Thread(target=self.server.start, daemon=True).start()
        self.show_toast("Server starting...", "info", icon="▶")
        self.play_sound('startup')

    def stop_server(self) -> None:
        if not self.server: self.show_toast("Server instance not available.", "error"); return
        if not self.server.running: self.show_toast("Server is not running.", "warning"); return
        threading.Thread(target=self.server.stop, daemon=True).start()
        self.show_toast("Server stopping...", "info", icon="⏹")
        self.play_sound('shutdown')

    def restart_server(self) -> None:
        if not self.server: self.show_toast("Server instance not available.", "error"); return
        self.show_toast("Restarting server...", "info", icon="🔄")
        def do_restart():
            if self.server:
                if self.server.running: self.server.stop(); time.sleep(2)
                self.server.start()
        threading.Thread(target=do_restart, daemon=True).start()

    def backup_database(self) -> None:
        db_manager = self.effective_db_manager  # type: ignore[reportUnknownMemberType]
        if not db_manager or not hasattr(db_manager, 'db_path') or not os.path.exists(getattr(db_manager, 'db_path', '')):
            self.show_toast("Database not available for backup.", "error"); return

        if path := filedialog.asksaveasfilename(defaultextension=".db", initialfile=f"backup_{datetime.now():%Y%m%d}.db"):
            try:
                if db_path := getattr(db_manager, 'db_path', ''):
                    shutil.copy2(db_path, path)
                self.show_toast("Database backed up!", "success", icon="💾")
                self.play_sound('success')
            except Exception as e:
                self.show_toast(f"Backup failed: {e}", "error"); self.play_sound('failure')

    # --- Update Loop & Backend Communication ---
    
    def _schedule_updates(self) -> None:
        if not self.is_running: return
        try:
            self._process_update_queue()
            self._update_clock()
            self._update_performance_metrics()
            self._check_disk_space()
        except Exception as e:
            print(f"Error in GUI update loop: {e}")
            if SENTRY_AVAILABLE:
                from contextlib import suppress
                with suppress(ImportError):
                    import sentry_sdk
                    sentry_sdk.capture_exception(e)
        self.root.after(1000, self._schedule_updates)

    def _process_update_queue(self) -> None:
        while not self.update_queue.empty():
            try:
                msg = self.update_queue.get_nowait()
                update_type, data = msg.get("type"), msg.get("data", {})
                if update_type == "status_update": 
                    self._handle_global_status_update(data)
                for page in self.pages.values():
                    if hasattr(page, 'handle_update') and update_type:
                        page.handle_update(update_type, data)
            except queue.Empty: break
            except Exception as e: print(f"Error processing update queue: {e}"); traceback.print_exc()

    def _handle_global_status_update(self, data: Dict[str, Any]) -> None:
        if (running := data.get('running', False)):  # Parentheses help Pylance understand scope
            _ = running  # Mark variable as used to avoid false positive warnings
            if self.status_label:
                self.status_label.config(text="Server Online")
            if self.status_indicator:
                self.status_indicator.itemconfig(self.status_indicator_oval, 
                                                fill=getattr(self.root.style.colors, 'success', '#28a745'))  # type: ignore[reportUnknownMemberType]
        else:
            if self.status_label:
                self.status_label.config(text="Server Offline")
            if self.status_indicator:
                self.status_indicator.itemconfig(self.status_indicator_oval, 
                                                fill=getattr(self.root.style.colors, 'danger', '#dc3545'))  # type: ignore[reportUnknownMemberType]

    def _update_clock(self) -> None:
        if self.clock_label:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.clock_label.config(text=current_time)

    def _update_performance_metrics(self) -> None:
        if not SYSTEM_MONITOR_AVAILABLE or not psutil: return
        self.performance_data['cpu'].append(psutil.cpu_percent())
        self.performance_data['memory'].append(psutil.virtual_memory().percent)
        self.performance_data['time'].append(datetime.now())

    def _check_disk_space(self) -> None:
        """Checks disk space and shows a warning banner if low (Feature #12)."""
        try:
            if (usage := shutil.disk_usage(os.path.abspath(self.settings.get('storage_dir', '.')))).free / (1024 ** 3) < self.settings.get('disk_warning_gb', 10):
                if not self.warning_banner:
                    self.warning_banner = ttk.Label(self.root, text="", style='warning.TLabel', font=('Segoe UI', 10, 'bold'), anchor=CENTER)
                    title_bar_height = self.title_bar.winfo_height() if self.title_bar else 50
                    self.warning_banner.place(x=0, y=title_bar_height, relwidth=1.0, height=25)
                self.warning_banner.config(text=f"⚠️ LOW DISK SPACE: {usage.free / (1024**3):.1f} GB remaining.")
            elif self.warning_banner: self.warning_banner.destroy(); self.warning_banner = None
        except FileNotFoundError:
            from contextlib import suppress
            with suppress(Exception):
                pass

    # --- Public API for Backend and Pages ---
    
    def post_update(self, update_type: str, data: Dict[str, Any]) -> None:
        self.update_queue.put({"type": update_type, "data": data})

    def play_sound(self, sound_name: str) -> None:
        if self.settings.get('audio_enabled', True):
            if path := self.asset_manager.get_sound(sound_name):
                threading.Thread(target=playsound, args=(path,), daemon=True).start()

    def change_theme(self, theme_name: str) -> None:
        self.root.style.theme_use(theme_name)  # type: ignore[reportUnknownMemberType]
        self.settings['theme'] = theme_name
        self._save_settings_to_file()
        self.show_toast(f"Theme changed to '{theme_name}'", "info")

    def show_toast(self, message: str, level: str = "info", icon: str = "💬", duration: int = 3000) -> None:
        bootstyle_map = {"info":"info", "success":"success", "warning":"warning", "error":"danger"}
        ToastNotification(title=f"{icon} {level.title()}", message=message, duration=duration,
                          bootstyle=bootstyle_map.get(level, "info"), alert=True)
                          
    def sync_current_server_state(self) -> None:
        """Synchronizes GUI with current server state on initialization."""
        if not self.server: self.post_update("status_update", {"running": False}); return
        self.post_update("status_update", {'running': self.server.running, 'start_time': time.time() if self.server.running else 0})
        if hasattr(self.server, 'db_manager') and self.server.db_manager:
            try:
                self.post_update("client_stats_update", {
                    'connected': len(getattr(self.server, 'clients', {})),
                    'total': len(self.server.db_manager.get_all_clients())
                })
            except Exception as e: print(f"[GUI] Error syncing client stats: {e}")

    def shutdown(self) -> None:
        print("Starting GUI shutdown...")
        self.is_running = False
        
        # Stop system tray first
        if self.tray_icon and hasattr(self.tray_icon, 'stop'):
            self.tray_icon.stop()  # type: ignore
        
        # Save settings before cleanup
        if self.root.winfo_exists():
            self.settings['geometry'] = self.root.geometry()
        self._save_settings_to_file()
        
        # Clean up pages with safe widget destruction
        try:
            for page_id, page in self.pages.items():
                try:
                    # Check if page has custom cleanup method
                    if hasattr(page, 'cleanup'):
                        page.cleanup()  # type: ignore
                    
                    # Safe widget cleanup - handle DateEntry and other problematic widgets
                    self._safe_widget_cleanup(page)
                except Exception as e:
                    print(f"[WARNING] Error cleaning up page '{page_id}': {e}")
        except Exception as e:
            print(f"[WARNING] Error during page cleanup: {e}")
        
        # Final root destruction
        try:
            if self.root.winfo_exists():
                # Cancel any pending after() calls
                try:
                    self.root.after_cancel('all')  # Cancel all pending after() calls
                except Exception:
                    pass
                self.root.destroy()
        except Exception as e:
            print(f"[WARNING] Error during root destruction: {e}")
            
        print("GUI shutdown completed.")
    
    def _safe_widget_cleanup(self, widget: tk.Widget) -> None:
        """Safely cleanup widget and its children to prevent after_cancel errors."""
        try:
            # Handle specific problematic widgets
            for child in widget.winfo_children():
                try:
                    # Recursively cleanup children first
                    self._safe_widget_cleanup(child)
                    
                    # Special handling for DateEntry widgets (tkcalendar) and SafeDateEntry
                    widget_class_str = str(child.__class__) if hasattr(child, '__class__') else ""
                    if 'DateEntry' in widget_class_str or 'SafeDateEntry' in widget_class_str:
                        # For SafeDateEntry, call its destroy method
                        if hasattr(child, 'destroy') and 'SafeDateEntry' in widget_class_str:
                            child.destroy()  # type: ignore
                            continue
                        
                        # For tkcalendar DateEntry, handle after_cancel issues
                        if hasattr(child, 'after_cancel'):
                            # Use specific known problematic attributes instead of dir()
                            problematic_attrs = [
                                '_determine_downarrow_name_after_id',
                                '_determine_uparrow_name_after_id'
                            ]
                            for attr_name in problematic_attrs:
                                if hasattr(child, attr_name):
                                    try:
                                        after_id = getattr(child, attr_name, None)
                                        if after_id and isinstance(after_id, (int, str)):
                                            child.after_cancel(after_id)  # type: ignore
                                            setattr(child, attr_name, None)
                                    except Exception:
                                        pass
                    
                    # General widget cleanup
                    if hasattr(child, 'destroy'):
                        child.destroy()
                        
                except Exception:
                    # Suppress all cleanup errors to prevent cascading issues
                    continue
                    
        except Exception:
            # Suppress all cleanup errors
            pass
        
    def _load_settings(self) -> Dict[str, Any]:
        defaults = {
            'theme': 'cyborg', 
            'geometry': '1400x900', 
            'audio_enabled': True, 
            'disk_warning_gb': 10,
            'storage_dir': 'received_files', 
            'last_tab': 'dashboard'
        }
        try:
            with open("server_gui_settings.json", 'r') as f: 
                loaded_settings = json.load(f)
                defaults |= loaded_settings  # type: ignore[reportUnknownMemberType]
        except (FileNotFoundError, json.JSONDecodeError):
            from contextlib import suppress
            with suppress(Exception):
                self._save_settings_to_file(defaults)
        return defaults

    def _save_settings_to_file(self, data: Optional[Dict[str, Any]] = None) -> None:
        settings_to_save = data or self.settings
        with open("server_gui_settings.json", 'w') as f: 
            json.dump(settings_to_save, f, indent=4)

def launch_standalone() -> None:
    print("[INFO] Launching Server GUI in standalone mode...")
    try:
        gui = ServerGUI()
        gui.run()
    except Exception as e:
        print(f"[FATAL] GUI could not be initialized: {e}"); traceback.print_exc()
    print("[INFO] Application has exited.")

if __name__ == "__main__":
    launch_standalone()