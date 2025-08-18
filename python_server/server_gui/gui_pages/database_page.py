# -*- coding: utf-8 -*-
"""
database_page.py - The Database Browser page for the Server GUI.

This page provides a powerful, read-only interface for inspecting the raw data
in the server's SQLite database tables.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Dict, Any, List, Tuple, cast

try:
    from ttkbootstrap import constants
except ImportError:
    from tkinter import constants

from .base_page import BasePage
from ..utils.tksheet_utils import ModernSheet

if TYPE_CHECKING:
    from ..ServerGUI import ServerGUI

class DatabasePage(BasePage):
    """A page for browsing the server database."""

    def __init__(self, parent: ttk.Frame, controller: 'ServerGUI') -> None:
        super().__init__(parent, controller)
        self._create_widgets()

    def _create_widgets(self) -> None:
        self._create_page_header("Database Browser", "database-fill")
        self._create_separator()

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=constants.BOTH, expand=True, padx=10, pady=(0, 10))

        self._create_db_controls(main_frame).pack(fill=constants.X, pady=(0, 10))
        
        self.sheet_container = ttk.Frame(main_frame)
        self.sheet_container.pack(fill=constants.BOTH, expand=True)
        
        self.placeholder = self._create_placeholder("Select a table to view its contents", "table")
        self.placeholder.pack(expand=True)

    def _create_db_controls(self, parent: ttk.Frame) -> ttk.Frame:
        """Creates the table selector and other controls."""
        frame = ttk.Frame(parent)
        
        ttk.Label(frame, text="Table:").pack(side=constants.LEFT, padx=(0, 5))
        self.table_selector_var = tk.StringVar()
        self.table_selector = ttk.Combobox(frame, textvariable=self.table_selector_var, state='readonly', width=30)
        self.table_selector.pack(side=constants.LEFT)
        self.table_selector.bind("<<ComboboxSelected>>", self._on_table_select)
        
        refresh_icon = self.controller.asset_manager.get_icon("arrow-clockwise")
        ttk.Button(frame, image=refresh_icon, command=self.on_show, style='Outline.TButton').pack(side=constants.LEFT, padx=(5,0))

        self.status_label = ttk.Label(frame, text="Ready.", style='secondary.TLabel')
        self.status_label.pack(side=constants.RIGHT, padx=5)
        return frame

    def on_show(self) -> None:
        """Refreshes the list of available database tables."""
        db_manager = cast(Any, self.controller).effective_db_manager
        if not db_manager:
            self.controller.show_toast("Database connection not available.", "error")
            self.table_selector['values'] = []
            self.table_selector_var.set("")
            return
        
        try:
            # Type cast to ensure proper method access
            tables: List[str] = cast(Any, db_manager).get_table_names()
            self.table_selector['values'] = tables
            if tables:
                current_selection = self.table_selector_var.get()
                if not current_selection or current_selection not in tables:
                    self.table_selector_var.set(tables[0])
                self._on_table_select()
            else:
                self.table_selector_var.set("")
                self.table_selector['values'] = []

        except Exception as e:
            self.controller.show_toast(f"Failed to fetch tables: {e}", "error")

    def _on_table_select(self, _: Any = None) -> None:
        """Fetches and displays content for the selected table."""
        table_name = self.table_selector_var.get()
        if not table_name: return
        
        db_manager = cast(Any, self.controller).effective_db_manager
        if not db_manager: return

        try:
            self.status_label.config(text=f"Loading '{table_name}'...")
            self.update_idletasks() # Force UI update
            
            # Type cast to ensure proper method access
            result: Tuple[List[str], List[Dict[str, Any]]] = cast(Any, db_manager).get_table_content(table_name)
            headers: List[str] = result[0]
            data: List[Dict[str, Any]] = result[1]
            
            # Clear previous content
            for widget in self.sheet_container.winfo_children():
                widget.destroy()

            if not data:
                self._create_placeholder(f"Table '{table_name}' is empty.", "table").pack(expand=True)
                self.status_label.config(text=f"Table '{table_name}' (0 rows)")
                return

            sheet = ModernSheet(self.sheet_container, headers=headers)
            sheet.pack(fill=constants.BOTH, expand=True)
            
            # Data-aware formatting (Layer 3)
            formatted_data: List[List[Any]] = []
            for row in data:
                formatted_row: List[Any] = []
                for header in headers:
                    # Ensure proper dict access with type casting
                    row_dict = cast(Dict[str, Any], row)
                    val: Any = row_dict.get(header)
                    if isinstance(val, int) and header in {'verified', 'is_admin'}:
                        formatted_row.append("✔" if val == 1 else "❌")
                    else:
                        formatted_row.append(val)
                formatted_data.append(formatted_row)

            sheet.set_sheet_data(formatted_data, redraw=True)
            sheet.readonly_columns(columns=list(range(len(headers)))) # Make fully read-only
            
            self.status_label.config(text=f"Table '{table_name}' ({len(data)} rows)")
            
        except Exception as e:
            self.controller.show_toast(f"Error loading table '{table_name}': {e}", "error")
            self.status_label.config(text=f"Error loading '{table_name}'.")

    def handle_update(self, update_type: str, data: Dict[str, Any]) -> None:
        """Database page can refresh on certain updates if it's visible."""
        if self.winfo_ismapped() and update_type in {"client_list_changed", "file_list_changed"}:
            self._on_table_select() # Refresh current view
        # Note: data parameter kept for base class compatibility but not used
        _ = data  # Explicitly mark as used to avoid linting warnings