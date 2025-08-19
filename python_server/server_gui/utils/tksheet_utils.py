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
from typing import List, Any, Union, Dict, Optional


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
            raw_colors: Any = style.colors  # type: ignore[reportUnknownMemberType]
            if isinstance(raw_colors, dict):
                colors_dict: Dict[str, Any] = raw_colors  # type: ignore[reportUnknownMemberType]
                bg = colors_dict.get("bg", "#f0f0f0")  # type: ignore[reportUnknownMemberType]
                fg = colors_dict.get("fg", "#222")  # type: ignore[reportUnknownMemberType]
                border = colors_dict.get("border", "#ccc")  # type: ignore[reportUnknownMemberType]
                secondary = colors_dict.get("secondary", "#0078d7")  # type: ignore[reportUnknownMemberType]
                light = colors_dict.get("light", "#fff")  # type: ignore[reportUnknownMemberType]
                inputbg = colors_dict.get("inputbg", "#fff")  # type: ignore[reportUnknownMemberType]
                primary = colors_dict.get("primary", "#005fa3")  # type: ignore[reportUnknownMemberType]
                selectbg = colors_dict.get("selectbg", "#e0eaff")  # type: ignore[reportUnknownMemberType]
                selectfg = colors_dict.get("selectfg", "#222")  # type: ignore[reportUnknownMemberType]
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

        self.set_options(  # type: ignore[reportUnknownMemberType]
            font=("Segoe UI", 10, "normal"),
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
        self.readonly(True)  # Default to read-only for safety

    def align_column(self, column: int, align: str) -> None:
        """Sets the alignment for all cells in a given column."""
        self.set_column_options(column=column, align=align)  # type: ignore[reportUnknownMemberType, reportAttributeAccessIssue]

    def set_sheet_headers(self, headers: List[str]) -> None:
        """Sets the column headers for the sheet."""
        self.headers(headers)

    def readonly_columns(self, columns: Union[List[int], int], readonly: bool = True, redraw: bool = True) -> 'Sheet':
        """Makes a specific set of columns read-only."""
        return super().readonly_columns(columns, readonly=readonly, redraw=redraw)

    def set_sheet_data(self, data: Optional[Union[List[List[Any]], tuple]] = None, 
                       reset_col_positions: bool = True, 
                       reset_row_positions: bool = True, 
                       redraw: bool = True, 
                       verify: bool = False, 
                       reset_highlights: bool = False, 
                       keep_formatting: bool = True, 
                       delete_options: bool = False) -> 'Sheet':
        """
        Clears the sheet and populates it with new data.

        Args:
            data: A list of lists representing the rows or None.
            reset_col_positions: Whether to reset column positions.
            reset_row_positions: Whether to reset row positions.
            redraw: Whether to redraw the sheet immediately.
            verify: Whether to verify the data.
            reset_highlights: Whether to reset highlights.
            keep_formatting: Whether to keep formatting.
            delete_options: Whether to delete options.
        """
        # Call the parent method with all parameters
        return super().set_sheet_data(  # type: ignore[reportUnknownMemberType]
            data=data, 
            reset_col_positions=reset_col_positions,
            reset_row_positions=reset_row_positions,
            redraw=redraw,
            verify=verify,
            reset_highlights=reset_highlights,
            keep_formatting=keep_formatting,
            delete_options=delete_options
        )
