# -*- coding: utf-8 -*-
"""
logs.py - The advanced log viewer page for the Server GUI.

This page provides a powerful, professional-grade interface for viewing,
filtering, searching, and exporting server logs.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import filedialog
import csv
from typing import TYPE_CHECKING, Dict, Any, List
from datetime import date, timedelta, datetime
import contextlib

try:
    import ttkbootstrap as ttk
    from ttkbootstrap import constants as ttk_constants
    # Use constants from ttkbootstrap - only what we need
    _VERTICAL = ttk_constants.VERTICAL
    _LEFT = ttk_constants.LEFT
    _RIGHT = ttk_constants.RIGHT
    _X = ttk_constants.X
    _END = ttk_constants.END
    _NORMAL = ttk_constants.NORMAL
    _DISABLED = ttk_constants.DISABLED
except ImportError:
    from tkinter import ttk
    # Fallback constants - only define what we actually use
    _VERTICAL = 'vertical'
    _LEFT = 'left'
    _RIGHT = 'right'
    _X = 'x'
    _END = 'end'
    _NORMAL = 'normal'
    _DISABLED = 'disabled'

try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    DateEntry = None
    CALENDAR_AVAILABLE = False

from .base_page import BasePage

if TYPE_CHECKING:
    from ..ServerGUI import ServerGUI

class LogsPage(BasePage):
    """The page for viewing and filtering server logs."""

    def __init__(self, parent: ttk.Frame, controller: 'ServerGUI') -> None:
        super().__init__(parent, controller)
        self.all_logs: List[Dict[str, Any]] = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        self._create_page_header("Log Viewer", "file-text-fill").grid(row=0, column=0, sticky='new')
        self._create_filter_bar().grid(row=1, column=0, sticky='ew', padx=5, pady=(0,5))
        self._create_log_view().grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        self._create_status_bar().grid(row=3, column=0, sticky='sew', padx=5)

    def _create_filter_bar(self) -> ttk.Frame:
        bar = ttk.Frame(self, style='secondary.TFrame', padding=10, borderwidth=1, relief="solid")
        
        # --- Filters ---
        ttk.Label(bar, text="Level:").pack(side=_LEFT, padx=(0,5))
        self.level_var = tk.StringVar(value="ALL")
        level_combo = ttk.Combobox(bar, textvariable=self.level_var, state='readonly', values=["ALL", "INFO", "WARNING", "ERROR", "DEBUG"])
        level_combo.pack(side=_LEFT, padx=(0, 15))

        if CALENDAR_AVAILABLE and DateEntry is not None:
            ttk.Label(bar, text="From:").pack(side=_LEFT, padx=(0,5))
            self.start_date_entry = DateEntry(bar, date_pattern='yyyy-mm-dd', firstweekday='sunday', startdate=date.today()-timedelta(days=7))
            # Type ignore for third-party DateEntry pack method
            self.start_date_entry.pack(side=_LEFT, padx=(0, 10))  # type: ignore[attr-defined]
            ttk.Label(bar, text="To:").pack(side=_LEFT, padx=(0,5))
            self.end_date_entry = DateEntry(bar, date_pattern='yyyy-mm-dd', firstweekday='sunday')
            # Type ignore for third-party DateEntry pack method  
            self.end_date_entry.pack(side=_LEFT, padx=(0, 20))  # type: ignore[attr-defined]
        else:
            # Fallback when calendar is not available
            self.start_date_entry = None
            self.end_date_entry = None
        
        ttk.Label(bar, text="Search:").pack(side=_LEFT, padx=(0,5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(bar, textvariable=self.search_var, width=30)
        search_entry.pack(side=_LEFT, fill=_X, expand=True, padx=(0, 10))
        search_entry.bind("<Return>", lambda _: self._apply_filters())
        
        ttk.Button(bar, text="Filter", command=self._apply_filters, style='info.TButton').pack(side=_LEFT, padx=(0,5))
        ttk.Button(bar, text="Clear", command=self._clear_filters, style='secondary.Outline.TButton').pack(side=_LEFT)

        # --- Actions (Right side) ---
        self.follow_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(bar, text="Follow", variable=self.follow_var, style='info.Roundtoggle.Toolbutton').pack(side=_RIGHT, padx=10)
        ttk.Button(bar, text="Export CSV", command=self._export_to_csv, style='success.Outline.TButton').pack(side=_RIGHT)
        return bar

    def _create_log_view(self) -> ttk.Frame:
        frame = ttk.Frame(self, style='secondary.TFrame', padding=0, borderwidth=1, relief="solid")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        
        # Safe color access with fallbacks
        try:
            style_colors = getattr(self.controller.root.style, 'colors', None)
            if style_colors:
                bg_color = getattr(style_colors, 'inputbg', 'white')
                fg_color = getattr(style_colors, 'fg', 'black')
            else:
                bg_color, fg_color = 'white', 'black'
        except (AttributeError, TypeError):
            bg_color, fg_color = 'white', 'black'
            
        self.log_text = tk.Text(frame, bg=bg_color, fg=fg_color,
                                font=('Consolas', 10), relief='flat', wrap='word', state=_DISABLED, bd=0, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(frame, orient=_VERTICAL, command=self.log_text.yview)  # type: ignore[misc]
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Right-click context menu with safe color access
        try:
            style_colors = getattr(self.controller.root.style, 'colors', None)
            if style_colors:
                menu_bg = getattr(style_colors, 'secondary', 'lightgray')
                menu_fg = getattr(style_colors, 'fg', 'black')
            else:
                menu_bg, menu_fg = 'lightgray', 'black'
        except (AttributeError, TypeError):
            menu_bg, menu_fg = 'lightgray', 'black'
            
        self.context_menu = tk.Menu(self.log_text, tearoff=0, background=menu_bg, foreground=menu_fg)
        self.context_menu.add_command(label="Copy Selection", command=self._copy_selection)
        self.context_menu.add_command(label="Copy All", command=self._copy_all)
        self.log_text.bind("<Button-3>", lambda e: self.context_menu.tk_popup(e.x_root, e.y_root))

        self.log_text.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        return frame

    def _create_status_bar(self) -> ttk.Frame:
        bar = ttk.Frame(self, style='TFrame', padding=(5,2))
        self.status_label = ttk.Label(bar, text="Status: Ready", style='secondary.TLabel', font=('Segoe UI', 8))
        self.status_label.pack(side=_LEFT)
        return bar

    def _clear_filters(self):
        self.level_var.set("ALL")
        if CALENDAR_AVAILABLE and self.start_date_entry is not None and self.end_date_entry is not None:
            # Type ignore for third-party DateEntry methods
            self.start_date_entry.set_date(date.today()-timedelta(days=7))  # type: ignore[attr-defined]
            self.end_date_entry.set_date(date.today())  # type: ignore[attr-defined]
        self.search_var.set("")
        self._apply_filters()
        
    def _apply_filters(self):
        """Fetches all logs from DB and then applies filters locally for responsiveness."""
        db_manager = getattr(self.controller, 'effective_db_manager', None)
        if not db_manager: 
            return self.controller.show_toast("Database not available.", "error")
            
        try:
            # Type ignore for dynamic database manager method
            self.all_logs = db_manager.get_logs()  # type: ignore[attr-defined]
            self.filter_and_display_logs()
        except Exception as e:
            self.controller.show_toast(f"Failed to retrieve logs: {e}", "error")

    def filter_and_display_logs(self):
        level = self.level_var.get()
        start_dt = (self.start_date_entry.get_date() 
                   if CALENDAR_AVAILABLE and self.start_date_entry is not None 
                   else date.min)
        end_dt = (self.end_date_entry.get_date() 
                 if CALENDAR_AVAILABLE and self.end_date_entry is not None 
                 else date.max)
        search = self.search_var.get().lower()

        filtered_logs = []
        for log in self.all_logs:
            # Level Filter
            if level != "ALL" and log.get('level', '').upper() != level:
                continue
            # Search Filter
            if search and search not in log.get('message', '').lower():
                continue
            # Date Filter
            with contextlib.suppress(ValueError, TypeError):
                log_date = datetime.fromisoformat(log.get('timestamp', '')).date()
                if not (start_dt <= log_date <= end_dt):
                    continue
            
            filtered_logs.append(log)  # type: ignore[arg-type]

        self._populate_log_view(filtered_logs)

    def _populate_log_view(self, logs: List[Dict[str, Any]]):
        self.log_text.config(state=_NORMAL)
        self.log_text.delete(1.0, _END)
        for log in reversed(logs): # Show most recent first
            self._insert_log_entry(log)
        self.log_text.config(state=_DISABLED)
        self.status_label.config(text=f"Displaying {len(logs)} of {len(self.all_logs)} total entries.")

    def _insert_log_entry(self, log_item: Dict[str, Any]):
        timestamp = log_item.get('timestamp', '')
        level = log_item.get('level', 'INFO').upper()
        message = log_item.get('message', '')

        self.log_text.insert(1.0, f" {message}\n", (level,))
        # Embed a styled label "pill" for the log level  
        level_pill = self._create_level_pill(self.log_text, level)  # type: ignore[arg-type]
        self.log_text.window_create(1.0, window=level_pill, padx=5)
        self.log_text.insert(1.0, f"[{timestamp}]", ("timestamp",))
        
        if self.follow_var.get(): self.log_text.see(1.0)

    def _create_level_pill(self, parent, level: str):
        style_map = {"INFO": "info", "WARNING": "warning", "ERROR": "danger", "DEBUG": "secondary"}
        style = f"Inverse.{style_map.get(level, 'primary')}.TLabel"
        return ttk.Label(parent, text=f"{level:^7}", style=style, font=('Consolas', 8, 'bold'), padding=(5, 1))
    
    def _export_to_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="server_logs.csv", filetypes=[("CSV files", "*.csv")])
        if not path: return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "message"])
                writer.writeheader()
                writer.writerows(self.all_logs) # Export all logs
            self.controller.show_toast(f"Successfully exported {len(self.all_logs)} logs.", "success")
        except Exception as e:
            self.controller.show_toast(f"Export failed: {e}", "error")

    def _copy_selection(self):
        with contextlib.suppress(tk.TclError):
            text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
    
    def _copy_all(self):
        text = self.log_text.get(1.0, tk.END)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.controller.show_toast("All visible logs copied.", "info")

    def on_show(self):
        self._apply_filters()

    def handle_update(self, update_type: str, data: Dict[str, Any]):
        if update_type == 'log':
            self.all_logs.append(data)  # type: ignore[arg-type]
            # Live update the view only if filters match
            self.filter_and_display_logs()