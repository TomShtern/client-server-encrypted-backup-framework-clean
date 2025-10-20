# ServerGUI.py - ULTRA MODERN Cross-platform GUI for Encrypted Backup Server
# Final Version: Fully implemented, refactored, and meticulously type-safe for strict checkers (Python 3.9+).

from __future__ import annotations

import json
import os
import queue
import shutil
import sys
import threading
import time
import traceback
from collections import deque
from collections.abc import Callable
from contextlib import suppress
from datetime import datetime, timedelta
from typing import (
    TYPE_CHECKING,
    Any,
    Protocol,
    cast,
    runtime_checkable,
)


# --- Dependency and System Setup ---
def _safe_reconfigure_stream(stream: Any) -> None:
    if callable(getattr(stream, 'reconfigure', None)):
        with suppress(Exception):
            stream.reconfigure(encoding='utf-8')

_safe_reconfigure_stream(sys.stdout)

try:
    import Shared.utils.utf8_solution  # this is important, this makes it so its utf-8 all across, very important to not have encoding problems.
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    try:
        import Shared.utils.utf8_solution
    except ImportError:
        print("[WARNING] Could not enable UTF-8 solution.")

if TYPE_CHECKING:
    import pystray
    from matplotlib.axes import Axes
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from matplotlib.lines import Line2D

    from Shared.utils.process_monitor_gui import ProcessMonitorWidget
else:
    # Runtime fallbacks for when packages aren't available
    ProcessMonitorWidget = type(None)
    pystray = type(None)
    FigureCanvasTkAgg = type(None)
    Figure = type(None)
    Axes = type(None)
    Line2D = type(None)

@runtime_checkable
class BackupServerLike(Protocol):
    running: bool
    db_manager: Any
    clients: dict[bytes, Any]
    clients_by_name: dict[str, bytes]
    network_server: Any
    file_transfer_manager: Any
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def apply_settings(self, settings: dict[str, Any]) -> None: ...

# Import DatabaseManager for standalone mode
try:
    from python_server.server.database import DatabaseManager
except ImportError:
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from server.database import DatabaseManager
    except ImportError:
        DatabaseManager = None # type: ignore
        print("[WARNING] DatabaseManager not available - Database tab will be disabled.")

# --- Optional Dependency Imports with Graceful Fallbacks ---
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from tkcalendar import DateEntry as CalDateEntry  # type: ignore
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    print("[INFO] tkcalendar not available. Fallback to simple Entry widgets.")

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    TkinterDnD = None
    DND_FILES = 'DND_FILES'
    print("[INFO] tkinterdnd2 not available. Drag-and-drop will be disabled.")

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    pystray = None # type: ignore
    print("[INFO] pystray/Pillow not available. System tray will be disabled.")

try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt  # Import pyplot properly
    from matplotlib.axes import Axes
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from matplotlib.lines import Line2D
    plt.style.use('dark_background')  # type: ignore
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    FigureCanvasTkAgg = Figure = Axes = Line2D = None # type: ignore
    print("[INFO] matplotlib not available. Analytics charts will be disabled.")

try:
    import psutil
    SYSTEM_MONITOR_AVAILABLE = True
except ImportError:
    psutil = None
    SYSTEM_MONITOR_AVAILABLE = False
    print("[INFO] psutil not available. System monitoring will be disabled.")

try:
    from Shared.utils.process_monitor_gui import ProcessMonitorWidget
    PROCESS_MONITOR_AVAILABLE = True
except ImportError:
    ProcessMonitorWidget = None # type: ignore
    PROCESS_MONITOR_AVAILABLE = False
    print("[INFO] ProcessMonitorWidget not found.")

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

# --- UI Constants & Theme ---
class ModernTheme:
    PRIMARY_BG, SECONDARY_BG, CARD_BG, ACCENT_BG = "#0D1117", "#161B22", "#21262D", "#30363D"
    TEXT_PRIMARY, TEXT_SECONDARY = "#F0F6FC", "#8B949E"
    SUCCESS, WARNING, ERROR, INFO = "#238636", "#D29922", "#DA3633", "#1F6FEB"
    ACCENT_BLUE, ACCENT_PURPLE, BORDER_COLOR = "#58A6FF", "#7C4DFF", "#30363D"
    FONT_FAMILY, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL = "Segoe UI", 11, 9

class Icons:
    ICONS: dict[str, str] = {"dashboard": "🏠", "clients": "👥", "files": "📁", "analytics": "📊",
        "database": "🗄️", "logs": "📝", "settings": "⚙️", "processes": "⚙️", "start": "▶️",
        "stop": "⏹️", "restart": "🔄", "save": "💾", "delete": "🗑️", "info": "ℹ️", "disconnect": "🔌", "exit": "🚪"}
    @classmethod
    def get(cls, name: str) -> str: return cls.ICONS.get(name, "🔹")

# --- Custom Modern Widgets ---
class ModernTooltip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tooltip_window: tk.Toplevel | None = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event: tk.Event) -> None:
        if self.tooltip_window or not self.text: return
        x, y = self.widget.winfo_rootx() + 20, self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, justify='left', background=ModernTheme.ACCENT_BG, fg=ModernTheme.TEXT_PRIMARY,
                 relief='solid', borderwidth=1, font=(ModernTheme.FONT_FAMILY, 9), padx=8, pady=5).pack(ipadx=1)

    def hide_tooltip(self, event: tk.Event) -> None:
        if self.tooltip_window: self.tooltip_window.destroy()
        self.tooltip_window = None

class ModernCard(tk.Frame):
    def __init__(self, parent: tk.Widget, title: str = "", **kwargs: Any) -> None:
        super().__init__(parent, bg=ModernTheme.CARD_BG, relief="solid", bd=1,
                         highlightbackground=ModernTheme.BORDER_COLOR, highlightthickness=1, **kwargs)
        self.content_frame: tk.Frame = self._create_card(title)

    def _create_card(self, title: str) -> tk.Frame:
        if title:
            title_frame = tk.Frame(self, bg=ModernTheme.ACCENT_BG)
            title_frame.pack(fill="x", padx=1, pady=1)
            tk.Label(title_frame, text=title, bg=ModernTheme.ACCENT_BG, fg=ModernTheme.TEXT_PRIMARY,
                     font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MEDIUM, "bold")
                     ).pack(side="left", padx=10, pady=5)
        content_frame = tk.Frame(self, bg=ModernTheme.CARD_BG)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        return content_frame

class ModernTable(tk.Frame):
    def __init__(self, parent: tk.Widget, columns: dict[str, dict[str, Any]], **kwargs: Any) -> None:
        super().__init__(parent, bg=ModernTheme.CARD_BG, **kwargs)
        self.columns = columns
        self.data: list[dict[str, Any]] = []
        self.filtered_data: list[dict[str, Any]] = []
        self.sort_column: str | None = None
        self.sort_reverse: bool = False
        self.selection_callback: Callable[[dict[str, Any]], None] | None = None
        self.context_menu_builder: Callable[[dict[str, Any]], tk.Menu] | None = None
        self.search_var = tk.StringVar()
        self.tree = self._create_table()

    def _create_table(self) -> ttk.Treeview:
        search_frame = tk.Frame(self, bg=ModernTheme.CARD_BG)
        search_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(search_frame, text="🔍", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                 font=(ModernTheme.FONT_FAMILY, 12)).pack(side="left", padx=(5, 2))
        self.search_var.trace_add("write", self._on_search_change)
        tk.Entry(search_frame, textvariable=self.search_var, bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                 font=(ModernTheme.FONT_FAMILY, 10), relief="flat", insertbackground=ModernTheme.TEXT_PRIMARY
                 ).pack(side="left", fill="x", expand=True, ipady=4)

        table_container = tk.Frame(self)
        table_container.pack(fill="both", expand=True)
        tree = ttk.Treeview(table_container, columns=list(self.columns.keys()), show="headings")
        v_scroll = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)  # type: ignore
        h_scroll = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview)  # type: ignore
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        for col_id, col_info in self.columns.items():
            tree.column(col_id, width=col_info.get('width', 100), anchor=col_info.get('anchor', 'w'))
            tree.heading(col_id, text=col_info['text'], command=lambda c=col_id: self._sort_by_column(c))

        tree.bind("<<TreeviewSelect>>", self._on_selection_change)
        tree.bind("<Button-3>", self._show_context_menu)
        return tree

    def set_data(self, data: list[dict[str, Any]]) -> None:
        self.data = data
        self._apply_filter()

    def _apply_filter(self) -> None:
        search_text = self.search_var.get().lower()
        self.filtered_data = [item for item in self.data if not search_text or
                              any(search_text in str(val).lower() for val in item.values())]
        self._refresh_display()

    def _refresh_display(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for item in self.filtered_data:
            values = tuple(item.get(col, '') for col in self.columns.keys())
            item_id = str(item.get('id', str(values)))
            self.tree.insert("", "end", iid=item_id, values=values)

    def _sort_by_column(self, col: str) -> None:
        if self.sort_column == col: self.sort_reverse = not self.sort_reverse
        else: self.sort_column, self.sort_reverse = col, False
        self.filtered_data.sort(key=lambda x: str(x.get(col, '')), reverse=self.sort_reverse)
        self._refresh_display()

    def _on_search_change(self, *args: Any) -> None: self._apply_filter()

    def _on_selection_change(self, event: tk.Event) -> None:
        if not self.selection_callback: return
        if selection := self.tree.selection():
            item_id = selection[0]
            if selected_item := next((item for item in self.filtered_data if str(item.get('id', '')) == item_id), None):
                self.selection_callback(selected_item)

    def _show_context_menu(self, event: tk.Event) -> None:
        if not self.context_menu_builder: return
        if iid := self.tree.identify_row(event.y):
            self.tree.selection_set(iid)
            if selected_item := next((item for item in self.filtered_data if str(item.get('id', '')) == iid), None):
                menu = self.context_menu_builder(selected_item)
                menu.post(event.x_root, event.y_root)

    def set_selection_callback(self, cb: Callable[[dict[str, Any]], None]) -> None: self.selection_callback = cb
    def set_context_menu_builder(self, builder: Callable[[dict[str, Any]], tk.Menu]) -> None: self.context_menu_builder = builder

class ModernStatusIndicator(tk.Frame):
    """Modern status indicator with colored LED-style indicator."""
    def __init__(self, parent: tk.Widget, **kwargs: Any) -> None:
        super().__init__(parent, bg=ModernTheme.CARD_BG, **kwargs)
        self.status_label = tk.Label(self, text="●", fg=ModernTheme.ERROR, bg=ModernTheme.CARD_BG,
                                   font=(ModernTheme.FONT_FAMILY, 12))
        self.status_label.pack()

    def set_status(self, status: str) -> None:
        """Set the status indicator color based on status."""
        if status.lower() in {"online", "running", "connected"}:
            self.status_label.config(fg=ModernTheme.SUCCESS)
        elif status.lower() in {"warning", "pending"}:
            self.status_label.config(fg=ModernTheme.WARNING)
        else:
            self.status_label.config(fg=ModernTheme.ERROR)

class ModernProgressBar(tk.Frame):
    """Modern progress bar with percentage display."""
    def __init__(self, parent: tk.Widget, **kwargs: Any) -> None:
        super().__init__(parent, bg=ModernTheme.CARD_BG, **kwargs)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, length=200)
        self.progress_bar.pack(side="left", padx=(0, 10))
        self.label = tk.Label(self, text="0%", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SMALL))
        self.label.pack(side="right")

    def set_progress(self, value: float) -> None:
        """Set progress value (0-100)."""
        self.progress_var.set(value)
        self.label.config(text=f"{value:.1f}%")

class ToastNotification:
    """Toast notification system for showing temporary messages."""
    def __init__(self, parent: tk.Widget) -> None:
        self.parent = parent
        self.toasts: list[tk.Toplevel] = []

    def show_toast(self, message: str, level: str = "info") -> None:
        """Show a toast notification."""
        colors = {
            "info": ModernTheme.INFO,
            "success": ModernTheme.SUCCESS,
            "warning": ModernTheme.WARNING,
            "error": ModernTheme.ERROR
        }

        toast = tk.Toplevel(self.parent)
        toast.withdraw()
        toast.overrideredirect(True)
        toast.configure(bg=colors.get(level, ModernTheme.INFO))

        label = tk.Label(toast, text=message, bg=colors.get(level, ModernTheme.INFO),
                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 10),
                        padx=20, pady=10)
        label.pack()

        # Position toast
        toast.update_idletasks()
        x = self.parent.winfo_rootx() + self.parent.winfo_width() - toast.winfo_width() - 20
        y = self.parent.winfo_rooty() + 20 + len(self.toasts) * 60
        toast.geometry(f"+{x}+{y}")
        toast.deiconify()

        self.toasts.append(toast)

        # Auto-hide after 3 seconds
        def hide_toast() -> None:
            if toast in self.toasts:
                self.toasts.remove(toast)
                toast.destroy()

        toast.after(3000, hide_toast)

class DetailPane(ModernCard):
    """Detail pane for showing detailed information about selected items."""
    def __init__(self, parent: tk.Widget, title: str = "", **kwargs: Any) -> None:
        super().__init__(parent, title=title, **kwargs)
        self.content_text = tk.Text(self.content_frame, bg=ModernTheme.CARD_BG,
                                  fg=ModernTheme.TEXT_PRIMARY, wrap=tk.WORD,
                                  font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SMALL))
        self.content_text.pack(fill="both", expand=True)

    def update_details(self, item: dict[str, Any]) -> None:
        """Update the detail pane with information about the selected item."""
        self.content_text.delete(1.0, tk.END)
        for key, value in item.items():
            self.content_text.insert(tk.END, f"{key}: {value}\n")

# Constants
SERVER_CONTROL_AVAILABLE = True

class ServerGUI:
    def __init__(self, server_instance: BackupServerLike | None = None) -> None:
        self.server = server_instance
        self.root: tk.Tk | None = None
        self.is_running = False
        self.gui_thread: threading.Thread | None = None
        self.start_time: float = 0.0
        self.current_tab = "dashboard"
        self.settings: dict[str, Any] = self._load_settings()
        self.update_queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self.toast_system: ToastNotification | None = None
        self.tray_icon: Any = None
        self.tab_buttons: dict[str, tk.Button] = {}
        self.tab_contents: dict[str, tk.Frame] = {}
        self.status_labels: dict[str, tk.Label] = {}
        self.header_status_indicator: ModernStatusIndicator | None = None
        self.clock_label: tk.Label | None = None
        self.header_status_label: tk.Label | None = None
        self.activity_log_text: tk.Text | None = None
        self.client_table: ModernTable | None = None
        self.client_detail_pane: DetailPane | None = None
        self.file_table: ModernTable | None = None
        self.file_detail_pane: DetailPane | None = None
        self.db_table: ModernTable | None = None
        self.db_table_selector: ttk.Combobox | None = None
        self.setting_vars: dict[str, tk.StringVar] = {}
        self.performance_chart: Any = None
        self.ax: Any = None
        self.cpu_line: Any = None
        self.mem_line: Any = None
        self.performance_data: dict[str, deque[Any]] = {'cpu': deque(maxlen=60), 'memory': deque(maxlen=60), 'time': deque(maxlen=60)}
        self._fallback_db_manager: Any | None = None

    @property
    def effective_db_manager(self) -> Any:
        """Get database manager from server or create fallback for standalone mode."""
        if self.server and hasattr(self.server, 'db_manager') and self.server.db_manager:
            return self.server.db_manager

        # Fallback for standalone mode
        if DatabaseManager is None:
            return None

        if self._fallback_db_manager is None:
            try:
                self._fallback_db_manager = DatabaseManager()
            except Exception as e:
                print(f"[WARNING] Could not create fallback DatabaseManager: {e}")
                return None
        return self._fallback_db_manager

    def initialize(self) -> bool:
        if self.is_running: return True
        try:
            temp_root = tk.Tk(); temp_root.withdraw(); temp_root.destroy()
        except tk.TclError:
            print(f"\n{'='*80}\nFATAL: Cannot start GUI - No graphical display available.\n{'='*80}\n")
            return False

        self.is_running = True
        self.gui_thread = threading.Thread(target=self._gui_main_loop, daemon=True)
        self.gui_thread.start()
        for _ in range(50):
            if self.root and self.toast_system:
                print("[OK] GUI initialized successfully!")
                return True
            time.sleep(0.1)
        print("[ERROR] GUI initialization timed out.")
        self.is_running = False
        return False

    def shutdown(self) -> None:
        print("Starting GUI shutdown...")
        self.is_running = False
        if self.tray_icon: self.tray_icon.stop()
        if self.root: self.root.destroy()
        print("GUI shutdown completed.")

    def _initialize_root_window(self) -> None:
        """Initialize the root window with proper configuration."""
        self.root = TkinterDnD.Tk() if DND_AVAILABLE and TkinterDnD else tk.Tk()  # type: ignore
        self.root = cast(tk.Tk, self.root)  # type: ignore

        self.root.title("Encrypted Backup Server")  # type: ignore
        self.root.geometry("1400x900")  # type: ignore
        self.root.minsize(1000, 700)  # type: ignore
        self.root.configure(bg=ModernTheme.PRIMARY_BG)  # type: ignore
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)  # type: ignore

    def _setup_gui_components(self) -> None:
        """Initialize and setup all GUI components."""
        self._initialize_root_window()
        self.toast_system = ToastNotification(self.root)  # type: ignore
        self._setup_modern_styles()
        self._create_main_window()
        self._create_system_tray()
        self._schedule_updates()
        # Sync current server state with GUI display
        self.sync_current_server_state()
        self.root.after(500, lambda: self._show_toast("GUI Ready", "success"))  # type: ignore

    def _gui_main_loop(self) -> None:
        try:
            self._setup_gui_components()
            self.root.mainloop()  # type: ignore
        except Exception as e:
            print(f"GUI main loop error: {e}")
            if SENTRY_AVAILABLE and 'sentry_sdk' in globals():
                sentry_sdk.capture_exception(e)  # type: ignore
            traceback.print_exc()
        finally:
            self.is_running = False
            print("GUI main loop ended.")

    def _setup_modern_styles(self) -> None:
        if not self.root: return
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure("Treeview", background=ModernTheme.SECONDARY_BG, foreground=ModernTheme.TEXT_PRIMARY,  # type: ignore
                        fieldbackground=ModernTheme.SECONDARY_BG, borderwidth=0, rowheight=25)
        style.configure("Treeview.Heading", background=ModernTheme.ACCENT_BG, foreground=ModernTheme.TEXT_PRIMARY,  # type: ignore
                        font=(ModernTheme.FONT_FAMILY, 10, 'bold'), relief="flat", padding=5)
        style.map("Treeview", background=[('selected', ModernTheme.ACCENT_BLUE)])  # type: ignore
        style.configure("TScrollbar", troughcolor=ModernTheme.SECONDARY_BG, background=ModernTheme.ACCENT_BG,  # type: ignore
                        bordercolor=ModernTheme.PRIMARY_BG, arrowcolor=ModernTheme.TEXT_PRIMARY)
        self.root.option_add('*TCombobox*Listbox*Background', ModernTheme.SECONDARY_BG)  # type: ignore
        self.root.option_add('*TCombobox*Listbox*Foreground', ModernTheme.TEXT_PRIMARY)  # type: ignore
        style.configure("TCombobox", fieldbackground=ModernTheme.SECONDARY_BG, background=ModernTheme.ACCENT_BG,  # type: ignore
                        foreground=ModernTheme.TEXT_PRIMARY, bordercolor=ModernTheme.BORDER_COLOR,
                        arrowcolor=ModernTheme.TEXT_PRIMARY, selectbackground=ModernTheme.ACCENT_BG)

    def _create_main_window(self) -> None:
        if not self.root: return
        main_container = tk.Frame(self.root, bg=ModernTheme.PRIMARY_BG)
        main_container.pack(fill="both", expand=True)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(1, weight=1)

        self._create_header(main_container).grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 0))
        self._create_sidebar(main_container).grid(row=1, column=0, sticky="nsw", padx=(10, 0), pady=10)
        content_area = tk.Frame(main_container, bg=ModernTheme.PRIMARY_BG)
        content_area.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self._create_all_tabs(content_area)
        self._switch_page(self.settings.get('last_tab', 'dashboard'))

    def _create_header(self, parent: tk.Widget) -> tk.Frame:
        header = tk.Frame(parent, bg=ModernTheme.PRIMARY_BG, height=60)
        header.pack_propagate(False)
        tk.Label(header, text="Encrypted Backup Server", bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                 font=(ModernTheme.FONT_FAMILY, 18, 'bold')).pack(side="left", padx=20)
        status_frame = tk.Frame(header, bg=ModernTheme.PRIMARY_BG)
        status_frame.pack(side="right", padx=20)
        self.clock_label = tk.Label(status_frame, text="", bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_SECONDARY, font=("Segoe UI", 12))
        self.clock_label.pack(anchor="e")
        indicator_frame = tk.Frame(status_frame, bg=ModernTheme.PRIMARY_BG)
        indicator_frame.pack(pady=(5, 0), anchor="e")
        self.header_status_label = tk.Label(indicator_frame, text="Server Offline", bg=ModernTheme.PRIMARY_BG,
                                            fg=ModernTheme.TEXT_SECONDARY, font=(ModernTheme.FONT_FAMILY, 10))
        self.header_status_label.pack(side="left", padx=(0, 5))
        self.header_status_indicator = ModernStatusIndicator(indicator_frame)
        self.header_status_indicator.pack(side="left")
        return header

    def _create_sidebar(self, parent: tk.Widget) -> tk.Frame:
        sidebar = tk.Frame(parent, bg=ModernTheme.SECONDARY_BG, width=220)
        sidebar.pack_propagate(False)
        pages = [("dashboard", "Dashboard"), ("clients", "Clients"), ("files", "Files"),
                 ("analytics", "Analytics"), ("database", "Database"), ("logs", "Logs"), ("settings", "Settings")]
        if PROCESS_MONITOR_AVAILABLE: pages.insert(5, ("processes", "Processes"))

        for page_id, page_name in pages:
            btn = tk.Button(sidebar, text=f" {Icons.get(page_id)}  {page_name}", command=lambda p=page_id: self._switch_page(p),
                            bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 12, 'bold'),
                            relief="flat", bd=0, padx=20, pady=15, anchor="w")
            btn.pack(side="top", fill="x", padx=10, pady=5)
            self.tab_buttons[page_id] = btn
        return sidebar

    def _create_all_tabs(self, content_area: tk.Frame) -> None:
        for page_id in self.tab_buttons:
            frame = tk.Frame(content_area, bg=ModernTheme.PRIMARY_BG)
            self.tab_contents[page_id] = frame
            creation_method = getattr(self, f"_create_{page_id}_tab", None)
            if callable(creation_method): creation_method(frame)

    # --- Individual Tab Creators ---
    def _create_dashboard_tab(self, parent: tk.Frame) -> None:
        parent.columnconfigure(0, weight=2, uniform="dashboard"); parent.columnconfigure(1, weight=1, uniform="dashboard")
        parent.rowconfigure(0, weight=1); parent.rowconfigure(1, weight=2)
        status_panel = tk.Frame(parent, bg=ModernTheme.PRIMARY_BG)
        status_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 5))
        status_panel.rowconfigure(0, weight=1); status_panel.rowconfigure(1, weight=1)
        status_panel.columnconfigure(0, weight=1); status_panel.columnconfigure(1, weight=1)
        self._create_dashboard_status_cards(status_panel)
        self._create_dashboard_control_card(parent).grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        self._create_dashboard_performance_chart(parent).grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(5, 0))
        self._create_dashboard_log_card(parent).grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))

    def _create_clients_tab(self, parent: tk.Frame) -> None:
        paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True)
        table_card = ModernCard(paned_window, title=f"{Icons.get('clients')} Client Management")
        columns: dict[str, dict[str, Any]] = {'name': {'text': 'Name', 'width': 150}, 'id': {'text': 'Client ID', 'width': 250},
                   'status': {'text': 'Status', 'width': 100}, 'last_seen': {'text': 'Last Seen', 'width': 150}}
        self.client_table = ModernTable(table_card.content_frame, columns)
        self.client_table.pack(fill="both", expand=True)
        self.client_table.set_selection_callback(self._on_client_selected)
        self.client_table.set_context_menu_builder(self._build_client_context_menu)
        paned_window.add(table_card, weight=3)  # type: ignore
        self.client_detail_pane = DetailPane(paned_window, title=f"{Icons.get('info')} Client Details")
        paned_window.add(self.client_detail_pane, weight=1)  # type: ignore

    def _create_files_tab(self, parent: tk.Frame) -> None:
        paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True)
        table_card = ModernCard(paned_window, title=f"{Icons.get('files')} File Management")
        columns: dict[str, dict[str, Any]] = {'filename': {'text': 'File Name', 'width': 250}, 'client_name': {'text': 'Client', 'width': 150},
                   'size_mb': {'text': 'Size (MB)', 'width': 80, 'anchor': 'e'}, 'date': {'text': 'Date', 'width': 150},
                   'verified': {'text': 'Verified', 'width': 80, 'anchor': 'center'}}
        self.file_table = ModernTable(table_card.content_frame, columns)
        self.file_table.pack(fill="both", expand=True)
        self.file_table.set_selection_callback(self._on_file_selected)
        self.file_table.set_context_menu_builder(self._build_file_context_menu)
        paned_window.add(table_card, weight=3)  # type: ignore
        if DND_AVAILABLE and self.root:
            # table_card.drop_target_register(DND_FILES)  # Commented out - method doesn't exist
            # table_card.dnd_bind('<<Drop>>', self._on_file_drop)  # Commented out
            ModernTooltip(table_card, "Drag and drop files here to upload")
        self.file_detail_pane = DetailPane(paned_window, title=f"{Icons.get('info')} File Details")
        paned_window.add(self.file_detail_pane, weight=1)  # type: ignore

    def _create_analytics_tab(self, parent: tk.Frame) -> None:
        if not CHARTS_AVAILABLE:
            tk.Label(parent, text="Analytics require matplotlib: pip install matplotlib",
                     bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_SECONDARY, font=(ModernTheme.FONT_FAMILY, 14)).pack(expand=True)
            return
        self._create_dashboard_performance_chart(parent, title="Live System Analytics").pack(fill="both", expand=True)

    def _create_database_tab(self, parent: tk.Frame) -> None:
        card = ModernCard(parent, title=f"{Icons.get('database')} Database Browser")
        card.pack(fill="both", expand=True)
        controls_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        controls_frame.pack(fill="x", pady=(0, 10))
        tk.Label(controls_frame, text="Table:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY).pack(side="left")
        self.db_table_selector = ttk.Combobox(controls_frame, state="readonly", style="TCombobox")
        self.db_table_selector.pack(side="left", padx=10)
        self.db_table_selector.bind("<<ComboboxSelected>>", self._on_db_table_select)
        tk.Button(controls_frame, text="Refresh", command=self._refresh_db_tables, relief="flat",
                  bg=ModernTheme.ACCENT_BG, fg=ModernTheme.TEXT_PRIMARY).pack(side="left")
        db_table_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        db_table_frame.pack(fill="both", expand=True)
        self.db_table = ModernTable(db_table_frame, columns={})
        self.db_table.pack(fill="both", expand=True)

    def _create_logs_tab(self, parent: tk.Frame) -> None:
        card = ModernCard(parent, title=f"{Icons.get('logs')} Log Viewer")
        card.pack(fill="both", expand=True)
        text_frame = tk.Frame(card.content_frame)
        text_frame.pack(fill="both", expand=True)
        self.activity_log_text = tk.Text(text_frame, bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_SECONDARY,
                                       font=("Consolas", 10), wrap="word", relief="flat", state=tk.DISABLED, padx=10, pady=10)
        v_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.activity_log_text.yview)  # type: ignore
        self.activity_log_text['yscrollcommand'] = v_scroll.set
        v_scroll.pack(side="right", fill="y")
        self.activity_log_text.pack(side="left", fill="both", expand=True)

    def _create_processes_tab(self, parent: tk.Frame) -> None:
        if PROCESS_MONITOR_AVAILABLE and ProcessMonitorWidget:
            ProcessMonitorWidget(parent, title="Server Processes", update_interval=2.0).pack(fill="both", expand=True)
        else:
            tk.Label(parent, text="ProcessMonitorWidget not available.", bg=ModernTheme.PRIMARY_BG,
                     fg=ModernTheme.TEXT_SECONDARY, font=(ModernTheme.FONT_FAMILY, 14)).pack(expand=True)

    def _create_settings_tab(self, parent: tk.Frame) -> None:
        card = ModernCard(parent, title=f"{Icons.get('settings')} Server Settings")
        card.pack(fill="both", expand=True)
        settings_to_display = {'port': "Server Port", 'storage_dir': "Storage Directory", 'max_clients': "Max Clients",
                               'session_timeout': "Session Timeout (min)", 'maintenance_interval': "Maintenance Interval (sec)"}
        for key, label in settings_to_display.items():
            frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
            frame.pack(fill="x", pady=5)
            tk.Label(frame, text=label, bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY, width=25, anchor="w").pack(side="left")
            var = tk.StringVar(value=str(self.settings.get(key, '')))
            self.setting_vars[key] = var
            tk.Entry(frame, textvariable=var, bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                     relief="flat").pack(side="left", fill="x", expand=True, ipady=4)
        button_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        button_frame.pack(fill="x", pady=20)
        tk.Button(button_frame, text=f"{Icons.get('save')} Save Settings", command=self._save_settings,
                  relief="flat", bg=ModernTheme.SUCCESS, fg=ModernTheme.TEXT_PRIMARY,
                  font=(ModernTheme.FONT_FAMILY, 10, 'bold'), padx=10, pady=5).pack(side="right")

    # --- Dashboard Sub-components ---
    def _create_dashboard_status_cards(self, parent: tk.Frame) -> None:
        datasets: list[tuple[str, list[tuple[str, str, str]], tuple[int, int]]] = [
            ("Server Status", [("Status", 'status', "Stopped"), ("Address", 'address', "N/A"), ("Uptime", 'uptime', "00:00:00")], (0,0)),
            ("Client Stats", [("Connected", 'connected', "0"), ("Total", 'total', "0"), ("Active Transfers", 'active_transfers', "0")], (0,1)),
            ("Transfer Stats", [("Total Transferred", 'bytes', "0 MB"), ("Transfer Rate", 'rate', "0 KB/s")], (1,0)),
            ("Maintenance", [("Last Cleanup", 'last_cleanup', "Never"), ("Files Cleaned", 'files_cleaned', "0")], (1,1))
        ]
        for title, data, (row, col) in datasets:
            card = ModernCard(parent, title=title)
            card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            for label, key, default in data:
                frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
                frame.pack(fill="x", pady=2)
                tk.Label(frame, text=f"{label}:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY).pack(side="left")
                self.status_labels[key] = tk.Label(frame, text=default, bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 10, 'bold'))
                self.status_labels[key].pack(side="right")

    def _create_dashboard_control_card(self, parent: tk.Frame) -> ModernCard:
        card = ModernCard(parent, title="Control Panel")
        bf = card.content_frame
        bf.columnconfigure(0, weight=1); bf.columnconfigure(1, weight=1)
        def create_button(text: str, icon: str, cmd: Callable[[], None], color: str, r: int, c: int, cspan: int = 1) -> None:
            tk.Button(bf, text=f"{Icons.get(icon)} {text}", command=cmd, bg=color, fg=ModernTheme.TEXT_PRIMARY,
                      font=(ModernTheme.FONT_FAMILY, 10, 'bold'), relief="flat", padx=10, pady=8
                      ).grid(row=r, column=c, columnspan=cspan, sticky="nsew", padx=2, pady=2)
        create_button("Start", "start", self._start_server, ModernTheme.SUCCESS, 0, 0)
        create_button("Stop", "stop", self._stop_server, ModernTheme.ERROR, 0, 1)
        create_button("Restart", "restart", self._restart_server, ModernTheme.WARNING, 1, 0, 2)
        create_button("Backup DB", "save", self._backup_database, ModernTheme.ACCENT_PURPLE, 2, 0)
        create_button("Exit GUI", "exit", self._on_window_close, ModernTheme.ACCENT_BG, 2, 1)
        return card

    def _create_dashboard_performance_chart(self, parent: tk.Frame, title: str = "Live System Performance") -> ModernCard:
        card = ModernCard(parent, title=title)
        if not all([CHARTS_AVAILABLE, Figure, Line2D]):
            tk.Label(card.content_frame, text="Charts disabled (matplotlib not found)", bg=ModernTheme.CARD_BG,
                     fg=ModernTheme.TEXT_SECONDARY).pack(expand=True)
            return card
        fig = Figure(figsize=(5, 2), dpi=100, facecolor=ModernTheme.CARD_BG)  # type: ignore
        self.ax = fig.add_subplot(111)  # type: ignore
        self.ax.set_facecolor(ModernTheme.SECONDARY_BG)  # type: ignore
        self.ax.tick_params(colors=ModernTheme.TEXT_SECONDARY, labelsize=8)  # type: ignore
        for spine in self.ax.spines.values(): spine.set_color(ModernTheme.BORDER_COLOR)  # type: ignore
        fig.tight_layout(pad=2)  # type: ignore
        self.cpu_line, = self.ax.plot([], [], color=ModernTheme.ACCENT_BLUE, lw=2, label="CPU %")  # type: ignore
        self.mem_line, = self.ax.plot([], [], color=ModernTheme.ACCENT_PURPLE, lw=2, label="Memory %")  # type: ignore
        self.ax.set_ylim(0, 100)  # type: ignore
        self.ax.legend(loc='upper left', fontsize=8, facecolor=ModernTheme.ACCENT_BG, labelcolor=ModernTheme.TEXT_PRIMARY, frameon=False)  # type: ignore
        self.performance_chart = FigureCanvasTkAgg(fig, master=card.content_frame)  # type: ignore
        self.performance_chart.get_tk_widget().pack(fill="both", expand=True)  # type: ignore
        return card

    def _create_dashboard_log_card(self, parent: tk.Frame) -> ModernCard:
        card = ModernCard(parent, title="Activity Log")
        self.activity_log_text = tk.Text(card.content_frame, height=4, bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                                         font=(ModernTheme.FONT_FAMILY, 8), wrap="word", relief="flat", bd=0, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(card.content_frame, orient="vertical", command=self.activity_log_text.yview)  # type: ignore
        self.activity_log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.activity_log_text.pack(side="left", fill="both", expand=True)
        return card

    # --- System Tray ---
    def _create_system_tray(self) -> None:
        if not TRAY_AVAILABLE or not pystray:
            return
        with suppress(ImportError):
            from PIL import Image, ImageDraw
            image = Image.new('RGB', (64, 64), ModernTheme.PRIMARY_BG)
            ImageDraw.Draw(image).rectangle((10, 10, 54, 54), fill=ModernTheme.ACCENT_BLUE)
            menu = (pystray.MenuItem('Show/Hide', self._toggle_window, default=True), pystray.MenuItem('Quit', self._quit_app))  # type: ignore
            self.tray_icon = pystray.Icon("ServerGUI", image, "Server GUI", menu)  # type: ignore
            threading.Thread(target=self.tray_icon.run, daemon=True).start()  # type: ignore

    def _toggle_window(self) -> None:
        if not self.root: return
        self.root.deiconify() if self.root.state() == 'withdrawn' else self.root.withdraw()

    def _quit_app(self) -> None:
        if self.tray_icon: self.tray_icon.stop()
        if self.root: self.root.destroy()
        self.is_running = False

    # --- GUI Update Loop ---
    def _schedule_updates(self) -> None:
        if not self.is_running: return
        try:
            self._process_update_queue()
            self._update_clock()
            self._update_performance_metrics()
        except Exception as e: print(f"Error in GUI update loop: {e}")
        if self.root: self.root.after(1000, self._schedule_updates)

    def _process_update_queue(self) -> None:
        while not self.update_queue.empty():
            try:
                msg = self.update_queue.get_nowait()
                update_type, data = msg.get("type"), msg.get("data", {})
                handler = getattr(self, f"_handle_{update_type}_update", None)
                if callable(handler): handler(data)
                elif update_type == "log": self._add_activity_log(str(data.get("message", "")))
            except queue.Empty: break
            except Exception as e: print(f"Error processing update queue: {e}")

    def _update_clock(self) -> None:
        if self.clock_label: self.clock_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def _update_performance_metrics(self) -> None:
        if not all([SYSTEM_MONITOR_AVAILABLE, psutil, self.ax, self.performance_chart, self.cpu_line, self.mem_line]): return
        cpu, mem, now = psutil.cpu_percent(), psutil.virtual_memory().percent, datetime.now()  # type: ignore
        self.performance_data['cpu'].append(cpu)
        self.performance_data['memory'].append(mem)
        self.performance_data['time'].append(now)
        times = list(self.performance_data['time'])
        if len(times) > 1:
            self.ax.set_xlim(times[0], times[-1])  # type: ignore
            self.cpu_line.set_data(times, list(self.performance_data['cpu']))  # type: ignore
            self.mem_line.set_data(times, list(self.performance_data['memory']))  # type: ignore
            self.performance_chart.draw_idle()  # type: ignore

    def _handle_status_update(self, data: dict[str, Any]) -> None:
        self.start_time = data.get('start_time', self.start_time)
        running = data.get('running', False)
        status_text, color = ("Running", ModernTheme.SUCCESS) if running else ("Stopped", ModernTheme.ERROR)
        if 'status' in self.status_labels: self.status_labels['status'].config(text=status_text, fg=color)
        if 'address' in self.status_labels: self.status_labels['address'].config(text=f"{data.get('address', 'N/A')}:{data.get('port', 0)}")
        if self.header_status_label: self.header_status_label.config(text="Server Online" if running else "Server Offline")
        if self.header_status_indicator: self.header_status_indicator.set_status("online" if running else "offline")
        if running and self.start_time > 0 and 'uptime' in self.status_labels:
            self.status_labels['uptime'].config(text=str(timedelta(seconds=int(time.time() - self.start_time))))
        elif 'uptime' in self.status_labels: self.status_labels['uptime'].config(text="0:00:00")

    def _handle_client_stats_update(self, data: dict[str, Any]) -> None:
        if 'connected' in self.status_labels: self.status_labels['connected'].config(text=str(data.get('connected', 0)))
        if 'total' in self.status_labels: self.status_labels['total'].config(text=str(data.get('total', 0)))
        if 'active_transfers' in self.status_labels: self.status_labels['active_transfers'].config(text=str(data.get('active_transfers', 0)))
        if self.current_tab == 'clients': self._refresh_client_table()

    def _handle_transfer_stats_update(self, data: dict[str, Any]) -> None:
        if 'bytes' in self.status_labels: self.status_labels['bytes'].config(text=f"{data.get('bytes_transferred', 0) / (1024*1024):.2f} MB")
        if 'rate' in self.status_labels: self.status_labels['rate'].config(text=f"{data.get('rate_kbps', 0):.1f} KB/s")
        if self.current_tab == 'files': self._refresh_file_table()

    def _handle_maintenance_update(self, data: dict[str, Any]) -> None:
        last_cleanup = data.get('last_cleanup', 'Never')
        if last_cleanup != 'Never': last_cleanup = datetime.fromisoformat(last_cleanup).strftime('%Y-%m-%d %H:%M')
        if 'last_cleanup' in self.status_labels: self.status_labels['last_cleanup'].config(text=last_cleanup)
        if 'files_cleaned' in self.status_labels: self.status_labels['files_cleaned'].config(text=str(data.get('files_cleaned', 0)))

    def _switch_page(self, page_id: str) -> None:
        if page_id not in self.tab_buttons: return
        self.current_tab = page_id
        self.settings['last_tab'] = page_id
        for pid, btn in self.tab_buttons.items():
            btn.configure(bg=ModernTheme.ACCENT_BLUE if pid == page_id else ModernTheme.SECONDARY_BG)
        for content in self.tab_contents.values(): content.pack_forget()
        self.tab_contents[page_id].pack(fill="both", expand=True)
        refresh_map: dict[str, Callable[[], None]] = {'clients': self._refresh_client_table, 'files': self._refresh_file_table, 'database': self._refresh_db_tables}
        if page_id in refresh_map: refresh_map[page_id]()

    def _start_server(self) -> None:
        if not self.server: self._show_toast("Server instance not available", "error"); return
        if self.server.running: self._show_toast("Server is already running", "warning"); return
        threading.Thread(target=self.server.start, daemon=True).start()
        self._show_toast("Server starting...", "info")

    def _stop_server(self) -> None:
        if not self.server: self._show_toast("Server instance not available", "error"); return
        if not self.server.running: self._show_toast("Server is not running", "warning"); return
        threading.Thread(target=self.server.stop, daemon=True).start()
        self._show_toast("Server stopping...", "info")

    def _restart_server(self) -> None:
        if not self.server: self._show_toast("Server instance not available", "error"); return
        self._show_toast("Restarting server...", "info")
        def do_restart() -> None:
            if self.server:
                if self.server.running: self.server.stop(); time.sleep(2)
                self.server.start()
        threading.Thread(target=do_restart, daemon=True).start()

    def _save_settings(self) -> None:
        try:
            for key, var in self.setting_vars.items(): self.settings[key] = var.get()
            self.settings['port'] = int(self.settings['port'])
            self.settings['max_clients'] = int(self.settings['max_clients'])
            with open("server_gui_settings.json", 'w') as f: json.dump(self.settings, f, indent=4)
            self._show_toast("Settings saved!", "success")
            if self.server and self.server.running:
                self.server.apply_settings(self.settings)
                self._show_toast("Settings applied to running server.", "info")
        except (ValueError, TypeError): self._show_toast("Invalid number in settings", "error")

    def _on_window_close(self) -> None:
        if messagebox.askyesno("Exit", "Exit and stop the server?"):
            if self.server and self.server.running: self.server.stop()
            self.shutdown()

    def _on_file_drop(self, event: tk.Event) -> None:
        if not self.root or not self.server: return
        filepaths = self.root.tk.splitlist(getattr(event, 'data', ''))  # type: ignore
        if not filepaths: return
        file_list = "\n".join(f"- {os.path.basename(p)}" for p in filepaths[:5])
        if len(filepaths) > 5: file_list += f"\n...and {len(filepaths) - 5} more"
        if messagebox.askyesno("Upload Files", f"Add the following files?\n\n{file_list}"):
            if hasattr(self.server, 'file_transfer_manager') and hasattr(self.server.file_transfer_manager, 'add_local_file_for_backup'):
                for path in filepaths: self.server.file_transfer_manager.add_local_file_for_backup(path)
                self._show_toast(f"Queued {len(filepaths)} files.", "success")
            else: self._show_toast("Server cannot handle file drops.", "error")

    def _refresh_client_table(self) -> None:
        if not self.client_table or not self.server or not self.server.db_manager: return
        clients_db = self.server.db_manager.get_all_clients()
        online_ids = list(self.server.clients.keys())
        for client in clients_db:
            client['status'] = "Online" if bytes.fromhex(client['id']) in online_ids else "Offline"
        self.client_table.set_data(clients_db)

    def _on_client_selected(self, item: dict[str, Any]) -> None:
        if self.client_detail_pane: self.client_detail_pane.update_details(item)

    def _build_client_context_menu(self, item: dict[str, Any]) -> tk.Menu:
        if not self.root: return tk.Menu()
        menu = tk.Menu(self.root, tearoff=0, bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY, activebackground=ModernTheme.ACCENT_BLUE)
        if self.client_detail_pane: menu.add_command(label=f"{Icons.get('info')} Show Details", command=lambda: self.client_detail_pane.update_details(item))  # type: ignore
        if item.get('status') == 'Online': menu.add_command(label=f"{Icons.get('disconnect')} Disconnect", command=lambda: self._disconnect_client(item['id']))
        return menu

    def _disconnect_client(self, client_id_hex: str) -> None:
        if self.server and self.server.network_server:
            if self.server.network_server.disconnect_client(bytes.fromhex(client_id_hex)): self._show_toast("Client disconnected.", "success")
            else: self._show_toast("Failed to disconnect client.", "error")

    def _refresh_file_table(self) -> None:
        if not self.file_table or not self.server or not self.server.db_manager: return
        files_db = self.server.db_manager.get_all_files()
        for f in files_db:
            f['size_mb'] = f"{f.get('size_bytes', 0) / (1024*1024):.3f}"
            f['verified'] = "Yes" if f.get('verified') else "No"
        self.file_table.set_data(files_db)

    def _on_file_selected(self, item: dict[str, Any]) -> None:
        if self.file_detail_pane: self.file_detail_pane.update_details(item)

    def _build_file_context_menu(self, item: dict[str, Any]) -> tk.Menu:
        if not self.root: return tk.Menu()
        menu = tk.Menu(self.root, tearoff=0, bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY, activebackground=ModernTheme.ACCENT_BLUE)
        if self.file_detail_pane: menu.add_command(label=f"{Icons.get('info')} Show Details", command=lambda: self.file_detail_pane.update_details(item))  # type: ignore
        menu.add_command(label=f"{Icons.get('delete')} Delete File", command=lambda: self._delete_file(item))
        return menu

    def _delete_file(self, file_info: dict[str, Any]) -> None:
        if not self.server or not self.server.db_manager: return
        if not messagebox.askyesno("Confirm Delete", f"Permanently delete {file_info['filename']}?"): return
        if self.server.db_manager.delete_file(file_info['client_id'], file_info['filename']):
            self._show_toast("File deleted.", "success")
            self._refresh_file_table()
        else: self._show_toast("Failed to delete file.", "error")

    def _refresh_db_tables(self) -> None:
        if not self.db_table_selector: return
        db_manager = self.effective_db_manager
        if not db_manager:
            self._show_toast("Database not available", "error")
            return
        try:
            tables = db_manager.get_table_names()
            self.db_table_selector['values'] = tables
            if tables:
                self.db_table_selector.set(tables[0])
                self._on_db_table_select()
        except Exception as e: self._show_toast(f"DB Error: {e}", "error")

    def _on_db_table_select(self, event: tk.Event | None = None) -> None:
        if not self.db_table_selector or not self.db_table: return
        db_manager = self.effective_db_manager
        if not db_manager:
            self._show_toast("Database not available", "error")
            return
        table_name = self.db_table_selector.get()
        try:
            self._rebuild_database_table(db_manager, table_name)
        except Exception as e:
            self._show_toast(f"DB Error: {e}", "error")

    def _rebuild_database_table(self, db_manager: Any, table_name: str) -> None:
        """Rebuild the database table with new data."""
        columns, data = db_manager.get_table_content(table_name)
        table_cols: dict[str, dict[str, Any]] = {col: {'text': col, 'width': 120} for col in columns}
        parent = self.db_table.master  # type: ignore
        if self.db_table is not None:
            self.db_table.destroy()
        self.db_table = ModernTable(parent, table_cols)  # type: ignore
        self.db_table.pack(fill="both", expand=True)
        self.db_table.set_data(data)

    def _add_activity_log(self, message: str) -> None:
        if not self.activity_log_text: return
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n"
        self.activity_log_text.config(state=tk.NORMAL)
        self.activity_log_text.insert(tk.END, log_entry)
        self.activity_log_text.see(tk.END)
        self.activity_log_text.config(state=tk.DISABLED)

    def _load_settings(self) -> dict[str, Any]:
        defaults: dict[str, Any] = {'port': 1256, 'storage_dir': 'received_files', 'max_clients': 50,
                    'session_timeout': 10, 'maintenance_interval': 60, 'last_tab': 'dashboard'}
        with suppress(FileNotFoundError, json.JSONDecodeError):
            with open("server_gui_settings.json") as f:
                defaults |= json.load(f)
        return defaults

    def _backup_database(self) -> None:
        if not self.server or not self.server.db_manager: self._show_toast("Server not available.", "error"); return
        db_path = self.server.db_manager.db_path
        if backup_path := filedialog.asksaveasfilename(defaultextension=".db",
            initialfile=f"backup_{datetime.now().strftime('%Y%m%d')}.db", filetypes=[("Database files", "*.db")]):
            try:
                shutil.copy2(db_path, backup_path)
                self._show_toast(f"Database backed up to {backup_path}", "success")
            except Exception as e: self._show_toast(f"Backup failed: {e}", "error")

    def _show_toast(self, message: str, level: str = "info") -> None:
        if self.toast_system: self.toast_system.show_toast(message, level)

    # Integration methods required by gui_integration.py
    def update_server_status(self, running: bool, address: str, port: int) -> None:
        """Update server status display in the GUI."""
        data = {
            'running': running,
            'address': address,
            'port': port,
            'start_time': self.start_time
        }
        self._handle_status_update(data)

    def update_client_stats(self, stats_data: dict[str, Any]) -> None:
        """Update client statistics display in the GUI."""
        # Ensure expected keys exist with defaults
        processed_data = {
            'connected': stats_data.get('connected', 0),
            'total': stats_data.get('total', 0),
            'active_transfers': stats_data.get('active_transfers', 0)
        }
        self._handle_client_stats_update(processed_data)

    def update_transfer_stats(self, stats_data: dict[str, Any]) -> None:
        """Update transfer statistics display in the GUI."""
        # Process the data to match expected format
        processed_data = {
            'bytes_transferred': stats_data.get('bytes_transferred', 0),
            'rate_kbps': stats_data.get('rate_kbps', 0.0),
            'last_activity': stats_data.get('last_activity', '')
        }
        self._handle_transfer_stats_update(processed_data)

    def update_maintenance_stats(self, stats: dict[str, Any]) -> None:
        """Update maintenance statistics display in the GUI."""
        # For now, just log maintenance stats as there's no specific handler yet
        print(f"[GUI] Maintenance stats update: {stats}")
        # TODO: Implement _handle_maintenance_stats_update if needed

    def sync_current_server_state(self) -> None:
        """Synchronize GUI with current server state on initialization."""
        if not self.server:
            return

        # Update server status based on current server state
        running = getattr(self.server, 'running', False)
        address = getattr(self.server, 'host', '0.0.0.0')
        port = getattr(self.server, 'port', 1256)

        self.update_server_status(running, address, port)

        # Update client stats if database is available
        if hasattr(self.server, 'db_manager') and self.server.db_manager:
            try:
                # Get total clients from database
                total_clients = len(self.server.db_manager.get_all_clients())
                connected_clients = len(getattr(self.server, 'client_connections', {}))

                self.update_client_stats({
                    'connected': connected_clients,
                    'total': total_clients,
                    'active_transfers': 0  # TODO: Get actual active transfers
                })
            except Exception as e:
                print(f"[GUI] Error syncing client stats: {e}")

        # Update database display if on database tab
        if self.current_tab == 'database':
            self._refresh_db_tables()


def launch_standalone() -> None:
    print("[INFO] Launching Server GUI in standalone mode...")
    gui = ServerGUI()
    if gui.initialize():
        try:
            if gui.gui_thread: gui.gui_thread.join()
        except KeyboardInterrupt:
            print("\n[INFO] Shutdown signal received.")
            gui.shutdown()
    else:
        print("[FATAL] GUI could not be initialized.")
    print("[INFO] Application has exited.")

if __name__ == "__main__":
    launch_standalone()
