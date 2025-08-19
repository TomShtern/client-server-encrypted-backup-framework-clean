# -*- coding: utf-8 -*-
"""
files.py - The File Management page for the Server GUI.

This page provides a comprehensive browser for all files stored on the server.
It defaults to a filterable "single giant list" view, as requested, with options
to drill down into specific clients, dates, and file types.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Dict, Any, List

try:
    from ttkbootstrap import constants
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    from tkinter import ttk, constants
    CALENDAR_AVAILABLE = False
    DateEntry = None  # type: ignore

from .base_page import BasePage
from ..utils.tksheet_utils import ModernSheet

if TYPE_CHECKING:
    from ..ServerGUI import ServerGUI

class FilesPage(BasePage):
    """A page for browsing and managing backed-up files."""

    def __init__(self, parent: ttk.Frame, controller: 'ServerGUI') -> None:
        super().__init__(parent, controller)
        self.all_files_data: List[Dict[str, Any]] = []
        # Initialize instance variables without type annotations in __init__
        # (type annotations here would cause runtime errors)
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and lay out all widgets for the files page."""
        self._create_page_header("File Repository", "file-earmark-zip-fill")
        self._create_separator()

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=constants.BOTH, expand=True, padx=10, pady=(0, 10))

        # --- Top Control Bar for Filtering ---
        self._create_filter_controls(main_frame).pack(fill=constants.X, pady=(0, 10))
        
        # --- File Table ---
        self.file_sheet = ModernSheet(main_frame,
            headers=["✔️", "Filename", "Client", "Size", "Date Modified"],
        )
        self.file_sheet.pack(fill=constants.BOTH, expand=True)
        # Configure columns for visual polish and data density
        self.file_sheet.column_width(column=0, width=30)
        self.file_sheet.column_width(column=1, width=350)
        self.file_sheet.column_width(column=2, width=150)
        self.file_sheet.column_width(column=3, width=100)
        self.file_sheet.column_width(column=4, width=150)
        self.file_sheet.align_column(column=0, align='center')
        self.file_sheet.align_column(column=3, align='e')
        self.file_sheet.readonly_columns(columns=[0,1,2,3,4])
        self.file_sheet.enable_bindings("single_select", "row_select") # Can add "multi_select"

    def _create_filter_controls(self, parent: ttk.Frame) -> ttk.Frame:
        """Creates the comprehensive filtering UI."""
        frame = ttk.Frame(parent)
        
        # Search Entry
        ttk.Label(frame, text="Search:").pack(side=constants.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filters())
        ttk.Entry(frame, textvariable=self.search_var, width=30).pack(side=constants.LEFT)
        
        # Client Filter
        ttk.Label(frame, text="Client:").pack(side=constants.LEFT, padx=(15, 5))
        self.client_filter_var = tk.StringVar(value="All Clients")
        self.client_filter_combo = ttk.Combobox(frame, textvariable=self.client_filter_var, state='readonly', width=20)
        self.client_filter_combo.pack(side=constants.LEFT)
        self.client_filter_combo.bind("<<ComboboxSelected>>", lambda _: self._apply_filters())

        # Date Range Filter
        if CALENDAR_AVAILABLE and DateEntry is not None:
            ttk.Label(frame, text="From:").pack(side=constants.LEFT, padx=(15, 5))
            # Create DateEntry widgets with proper type handling
            start_date_widget = DateEntry(frame, date_pattern='yyyy-mm-dd')  # type: ignore
            start_date_widget.pack(side=constants.LEFT)  # type: ignore
            self.start_date_entry = start_date_widget
            
            ttk.Label(frame, text="To:").pack(side=constants.LEFT, padx=(5, 5))
            end_date_widget = DateEntry(frame, date_pattern='yyyy-mm-dd')  # type: ignore
            end_date_widget.pack(side=constants.LEFT)  # type: ignore
            self.end_date_entry = end_date_widget

            start_date_widget.bind("<<DateEntrySelected>>", lambda _: self._apply_filters())  # type: ignore
            end_date_widget.bind("<<DateEntrySelected>>", lambda _: self._apply_filters())  # type: ignore
        
        ttk.Button(frame, text="Refresh", command=self.on_show, style='info.Outline.TButton').pack(side=constants.RIGHT, padx=(15,0))
        return frame

    def on_show(self) -> None:
        """Called when page is shown; fetches all data and updates filters."""
        self._refresh_all_data()
        self._update_client_filter_dropdown()

    def handle_update(self, update_type: str, data: Dict[str, Any]) -> None:
        """Handles backend updates relevant to files."""
        _ = data  # Explicitly mark as used to avoid linting warnings
        if update_type in {"file_list_changed", "transfer_stats_update"}:
            self._refresh_all_data()

    def _refresh_all_data(self) -> None:
        """Fetches the complete file list from the database."""
        db_manager = getattr(self.controller, 'effective_db_manager', None)
        if not db_manager:
            self.all_files_data = []
            self._apply_filters()
            return
            
        try:
            # Use getattr with fallback for unknown method types
            get_files_method = getattr(db_manager, 'get_all_files_with_client_names', None)
            if get_files_method and callable(get_files_method):
                self.all_files_data = get_files_method()  # type: ignore[misc]
            else:
                self.all_files_data = []
            self._apply_filters()
        except Exception as e:
            print(f"[ERROR] Failed to refresh file data: {e}")

    def _update_client_filter_dropdown(self) -> None:
        """Populates the client filter dropdown with current client names."""
        db_manager = getattr(self.controller, 'effective_db_manager', None)
        if not db_manager: return
        
        try:
            # Use getattr with fallback for unknown method types
            get_clients_method = getattr(db_manager, 'get_all_clients', None)
            if get_clients_method and callable(get_clients_method):
                clients_result = get_clients_method()  # type: ignore[misc]
                # Ensure we have a list to work with
                if isinstance(clients_result, list):
                    client_names = ["All Clients"] + sorted([str(c.get('name', '')) for c in clients_result if isinstance(c, dict) and 'name' in c])  # type: ignore[misc]
                    self.client_filter_combo['values'] = client_names
        except Exception as e:
            print(f"[ERROR] Failed to update client filter: {e}")

    def _apply_filters(self) -> None:
        """Applies all active filters to the file list and updates the table."""
        search_term = self.search_var.get().lower()
        client_filter = self.client_filter_var.get()

        filtered_data = self.all_files_data

        if client_filter != "All Clients":
            filtered_data = [f for f in filtered_data if f.get('client_name') == client_filter]

        if search_term:
            filtered_data = [
                f for f in filtered_data if
                search_term in f.get('filename', '').lower()
            ]

        # TODO: Add date range filtering logic using self.start_date_entry etc.

        # --- Update tksheet with filtered data ---
        table_data: List[List[str]] = []
        for file in filtered_data:
            # Data Visualization in table (Layer 3)
            verified_icon = "✔" if file.get('verified') else "❌"
            size_bytes = file.get('size_bytes', 0)
            if size_bytes > 1024*1024*1024: size_str = f"{size_bytes/(1024**3):.2f} GB"
            elif size_bytes > 1024*1024: size_str = f"{size_bytes/(1024**2):.2f} MB"
            else: size_str = f"{size_bytes/1024:.2f} KB"

            table_data.append([
                verified_icon,
                file.get('filename', ''),
                file.get('client_name', 'Unknown'),
                size_str,
                file.get('date', '')
            ])
        
        self.file_sheet.set_sheet_data(table_data, redraw=True)  # type: ignore[misc]
        # Apply color coding to the verified column
        for r_idx, file in enumerate(filtered_data):
            color = "green" if file.get('verified') else "red"
            # Use getattr to safely call highlight_cells method
            highlight_method = getattr(self.file_sheet, 'highlight_cells', None)
            if highlight_method and callable(highlight_method):
                highlight_method(row=r_idx, column=0, fg=color)  # type: ignore[misc]