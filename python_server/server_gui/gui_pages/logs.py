# In file: gui_pages/logs.py

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *  # Import all tkinter constants (BOTH, LEFT, RIGHT, etc.)
from typing import TYPE_CHECKING, List, Dict, Any, Optional

# Conditional imports
if TYPE_CHECKING:
    from ..ServerGUI import EnhancedServerGUI

try:
    from ..ServerGUI import BasePage, TKSHEET_AVAILABLE, CALENDAR_AVAILABLE, CustomTooltip
except ImportError:
    # Fallback for different import paths
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from ServerGUI import BasePage, TKSHEET_AVAILABLE, CALENDAR_AVAILABLE, CustomTooltip
    except ImportError:
        # Define minimal fallbacks
        class BasePage:
            def __init__(self, parent, app, **kwargs): pass
        class CustomTooltip:
            def __init__(self, *args, **kwargs): pass
        TKSHEET_AVAILABLE = False
        CALENDAR_AVAILABLE = False

if TKSHEET_AVAILABLE:
    from tksheet import Sheet
if CALENDAR_AVAILABLE:
    from tkcalendar import DateEntry

class LogsPage(BasePage):
    """A page for advanced viewing and filtering of server logs."""

    def __init__(self, parent: tk.Widget, app: EnhancedServerGUI, **kwargs: Any) -> None:
        super().__init__(parent, app, **kwargs)

        self.all_logs_data: List[Dict[str, Any]] = []
        self.sheet: Optional[Sheet] = None
        self.search_var = tk.StringVar()
        self.level_var = tk.StringVar(value="All Levels")
        
        # We will need start_date_var and end_date_var for DateEntry
        # but their initialization depends on CALENDAR_AVAILABLE

        self._create_widgets()

    def _create_widgets(self) -> None:
        if not TKSHEET_AVAILABLE:
            ttk.Label(self, text="tksheet library not found.\nPlease run: pip install tksheet", style='danger.TLabel').pack(expand=True)
            return

        main_frame_rounded = self.app.RoundedFrame(self, bg_color=self.app.style.colors.secondary, border_color=self.app.style.colors.border)
        main_frame_rounded.pack(fill=BOTH, expand=True, padx=5, pady=5)
        main_frame = main_frame_rounded.content_frame

        # --- Header with Filter Controls ---
        header = ttk.Frame(main_frame, style='secondary.TFrame')
        header.pack(fill=X, padx=10, pady=(5, 10))
        
        ttk.Label(header, text="📝 Log Viewer", font=self.app.Theme.FONT_BOLD, style='secondary.TLabel').pack(side=LEFT)
        
        # Refresh Button
        ttk.Button(header, text="🔄 Refresh", command=self.refresh_data, bootstyle='info-outline').pack(side=RIGHT, padx=(10, 0))

        # Date Filters
        if CALENDAR_AVAILABLE:
            ttk.Label(header, text="To:", style='secondary.TLabel').pack(side=RIGHT)
            self.end_date_entry = DateEntry(header, date_pattern='y-mm-dd', bootstyle='secondary')
            self.end_date_entry.pack(side=RIGHT, padx=5)
            self.end_date_entry.bind("<<DateEntrySelected>>", self._filter_logs)

            ttk.Label(header, text="From:", style='secondary.TLabel').pack(side=RIGHT)
            self.start_date_entry = DateEntry(header, date_pattern='y-mm-dd', bootstyle='secondary')
            self.start_date_entry.pack(side=RIGHT, padx=5)
            self.start_date_entry.bind("<<DateEntrySelected>>", self._filter_logs)
            
        # Level Filter
        level_combo = ttk.Combobox(header, textvariable=self.level_var, state="readonly", bootstyle='secondary',
                                   values=["All Levels", "INFO", "WARNING", "ERROR", "CRITICAL"])
        level_combo.pack(side=RIGHT, padx=5)
        self.level_var.trace_add("write", self._filter_logs)

        # Search Entry
        search_entry = ttk.Entry(header, textvariable=self.search_var, style='secondary.TEntry', width=30)
        search_entry.pack(side=RIGHT, fill=X, expand=True, padx=(20, 0))
        self.search_var.trace_add("write", self._filter_logs)
        CustomTooltip(search_entry, "Search log messages...")

        # --- tksheet Table ---
        self.sheet = Sheet(main_frame, headers=["Timestamp", "Level", "Message"], show_x_scrollbar=False)
        self.sheet.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self._configure_sheet_styles()
        self.sheet.enable_bindings("single_select", "row_select", "column_width_resize", "arrowkeys")
        self.sheet.set_column_widths([160, 80, 800])

    def _configure_sheet_styles(self) -> None:
        """Apply the current theme to the tksheet widget."""
        colors = self.app.style.colors
        self.sheet.config(
            background=colors.secondary, foreground=colors.fg, header_background=colors.bg,
            header_foreground=colors.fg, index_background=colors.bg, index_foreground=colors.fg,
            row_index_background=colors.bg, row_index_foreground=colors.fg, table_background=colors.secondary,
            selected_rows_background=colors.info, selected_rows_foreground=colors.light,
        )

    def refresh_data(self) -> None:
        """Fetch latest log data from the database."""
        db = self.app.effective_db_manager
        if not db or not self.sheet: return

        # This assumes your DatabaseManager has a method `get_all_logs`
        # which returns a list of dicts like: [{'timestamp': '...', 'level': '...', 'message': '...'}]
        if not hasattr(db, 'get_all_logs'):
            self.app.show_toast("Log fetching not implemented in backend.", "warning")
            # You can populate with dummy data for testing
            self.all_logs_data = [
                {'timestamp': '2023-10-28 10:00:00', 'level': 'INFO', 'message': 'Server started successfully.'},
                {'timestamp': '2023-10-28 10:05:10', 'level': 'WARNING', 'message': 'Client X disconnected unexpectedly.'},
            ]
        else:
            try:
                self.all_logs_data = db.get_all_logs()
            except Exception as e:
                self.app.show_toast(f"Failed to load logs: {e}", "danger")
                return
        
        self._filter_logs()
        self.app.show_toast("Logs refreshed.", "success")
    
    def _filter_logs(self, *args: Any) -> None:
        """Apply all active filters to the log data and update the sheet."""
        if not self.sheet: return

        search_query = self.search_var.get().lower()
        level_query = self.level_var.get()

        temp_data = self.all_logs_data

        # Filter by level
        if level_query and level_query != "All Levels":
            temp_data = [log for log in temp_data if log.get('level') == level_query]

        # Filter by date range (if tkcalendar is available)
        if CALENDAR_AVAILABLE:
            try:
                start_date = self.start_date_entry.get_date()
                end_date = self.end_date_entry.get_date()
                temp_data = [
                    log for log in temp_data 
                    if start_date <= datetime.strptime(log.get('timestamp', '1970-01-01'), '%Y-%m-%d %H:%M:%S').date() <= end_date
                ]
            except (ValueError, TypeError):
                # Handle cases where dates are not yet set or invalid
                pass

        # Filter by search text
        if search_query:
            temp_data = [log for log in temp_data if search_query in str(log.get('message', '')).lower()]
        
        display_data = [[log.get('timestamp', ''), log.get('level', ''), log.get('message', '')] for log in temp_data]
        self.sheet.set_sheet_data(data=display_data, reset_highlights=True)

        # Custom row highlighting for log levels
        for i, log in enumerate(temp_data):
            level = log.get('level')
            color = self.app.style.colors.secondary # Default
            if level == 'WARNING': color = self.app.style.colors.warning
            elif level in ['ERROR', 'CRITICAL']: color = self.app.style.colors.danger
            self.sheet.highlight_rows(rows=[i], bg=color, fg='white' if level != 'INFO' else self.app.style.colors.fg)


    def on_show(self) -> None:
        """Called when the page is displayed. Triggers a data refresh."""
        self.refresh_data()