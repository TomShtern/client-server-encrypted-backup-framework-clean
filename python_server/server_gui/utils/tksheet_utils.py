# -*- coding: utf-8 -*-
"""
tksheet_utils.py - A professional wrapper for the tksheet library.

This module provides a `ModernSheet` class that standardizes the appearance
and behavior of all `tksheet` tables used in the application. It ensures a
consistent, polished, and theme-aware look and feel, abstracting away the
complex configuration details from the page modules.
"""

from tksheet import Sheet
import ttkbootstrap as ttk
from typing import List, Optional, Callable, Dict, Any

class ModernSheet(Sheet):
    """
    A pre-styled, enhanced tksheet widget conforming to the app's design system.
    """
    def __init__(self, parent, **kwargs: Any):
        """
        Initializes a tksheet instance with a professional, consistent theme.
        """
        super().__init__(parent, **kwargs)  # type: ignore
        self._apply_modern_styling()

    def _apply_modern_styling(self) -> None:
        """Configures the sheet's appearance to match the ttkbootstrap theme."""
        style = ttk.Style.get_instance()  # type: ignore
        # Defensive: fallback to defaults if style/colors missing
        if style is not None and hasattr(style, "colors"):
            raw_colors = style.colors
            if isinstance(raw_colors, dict):
                bg = raw_colors.get("bg", "#f0f0f0")
                fg = raw_colors.get("fg", "#222")
                border = raw_colors.get("border", "#ccc")
                secondary = raw_colors.get("secondary", "#0078d7")
                light = raw_colors.get("light", "#fff")
                inputbg = raw_colors.get("inputbg", "#fff")
                primary = raw_colors.get("primary", "#005fa3")
                selectbg = raw_colors.get("selectbg", "#e0eaff")
                selectfg = raw_colors.get("selectfg", "#222")
            else:
                # Assume it's an object with attributes
                bg = getattr(raw_colors, "bg", "#f0f0f0")
                fg = getattr(raw_colors, "fg", "#222")
                border = getattr(raw_colors, "border", "#ccc")
                secondary = getattr(raw_colors, "secondary", "#0078d7")
                light = getattr(raw_colors, "light", "#fff")
                inputbg = getattr(raw_colors, "inputbg", "#fff")
                primary = getattr(raw_colors, "primary", "#005fa3")
                selectbg = getattr(raw_colors, "selectbg", "#e0eaff")
                selectfg = getattr(raw_colors, "selectfg", "#222")
        else:
            # Fallback colors (adjust as needed for your app)
            bg = "#f0f0f0"
            fg = "#222"
            border = "#ccc"
            secondary = "#0078d7"
            light = "#fff"
            inputbg = "#fff"
            primary = "#005fa3"
            selectbg = "#e0eaff"
            selectfg = "#222"

        self.set_options(
            font=("Segoe UI", 10),
            header_font=("Segoe UI", 10, "bold"),
            background=bg,
            foreground=fg,
            grid_color=border,
            header_background=secondary,
            header_foreground=light,
            header_grid_color=border,
            header_border_color=border,
            table_background=inputbg,
            table_foreground=fg,
            table_grid_color=border,
            table_selected_rows_background=primary,
            table_selected_rows_foreground=light,
            table_selected_columns_background=primary,
            table_selected_columns_foreground=light,
            table_selected_cells_background=selectbg,
            table_selected_cells_foreground=selectfg,
            # Disable default tksheet right-click menus for custom implementation
            enable_edit_cell_auto_resize=False,
        )
        self.readonly(True) # Default to read-only for safety
        
    def align_column(self, column: int, align: str) -> None:
        """Sets the alignment for all cells in a given column."""
        self.set_column_options(column=column, align=align)

    def set_sheet_headers(self, headers: List[str]) -> None:
        """Sets the column headers for the sheet."""
        self.headers(headers)

    def readonly_columns(self, columns: List[int]) -> None:
        """Makes a specific set of columns read-only."""
        super().readonly_columns(columns)

    def set_sheet_data(self, data: List[list], redraw: bool = True) -> None:
        """
        Clears the sheet and populates it with new data.

        Args:
            data (List[list]): A list of lists representing the rows.
            redraw (bool): Whether to redraw the sheet immediately.
        """
        # Overriding to provide a simpler, safer interface than the base class
        current_rows = self.get_total_rows()
        if current_rows > 0:
            self.delete_rows(0, current_rows)
        if data:
            self.insert_rows(0, data)
        
        if redraw:
            self.redraw()