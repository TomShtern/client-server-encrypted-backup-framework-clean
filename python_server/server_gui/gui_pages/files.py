# In file: gui_pages/files.py

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.constants import *  # Import all tkinter constants (BOTH, LEFT, RIGHT, etc.)
from typing import TYPE_CHECKING, List, Dict, Any, Optional

# Conditional imports for type checking and runtime
if TYPE_CHECKING:
    from ..ServerGUI import EnhancedServerGUI

# Import base class and check for dependencies
try:
    from ..ServerGUI import BasePage, TKSHEET_AVAILABLE, CustomTooltip
except ImportError:
    # Fallback for different import paths
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from ServerGUI import BasePage, TKSHEET_AVAILABLE, CustomTooltip
    except ImportError:
        # Define minimal fallbacks
        class BasePage:
            def __init__(self, parent, app, **kwargs): pass
        class CustomTooltip:
            def __init__(self, *args, **kwargs): pass
        TKSHEET_AVAILABLE = False

if TKSHEET_AVAILABLE:
    from tksheet import Sheet

class FilesPage(BasePage):
    """A page for viewing and managing backed-up files."""

    def __init__(self, parent: tk.Widget, app: EnhancedServerGUI, **kwargs: Any) -> None:
        super().__init__(parent, app, **kwargs)

        self.all_files_data: List[Dict[str, Any]] = []
        self.sheet: Optional[Sheet] = None
        self.search_var = tk.StringVar()
        self.client_filter_var = tk.StringVar()
        self.client_list: List[Dict[str, Any]] = []

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and lay out all widgets for the files page."""
        if not TKSHEET_AVAILABLE:
            ttk.Label(self, text="tksheet library not found.\nPlease run: pip install tksheet", style='danger.TLabel').pack(expand=True)
            return

        # Main frame with rounded corners
        main_frame_rounded = self.app.RoundedFrame(self, bg_color=self.app.style.colors.secondary, border_color=self.app.style.colors.border)
        main_frame_rounded.pack(fill=BOTH, expand=True, padx=5, pady=5)
        main_frame = main_frame_rounded.content_frame

        # --- Header with Controls ---
        header = ttk.Frame(main_frame, style='secondary.TFrame')
        header.pack(fill=X, padx=10, pady=(5, 10))
        
        ttk.Label(header, text="📁 File Browser", font=self.app.Theme.FONT_BOLD, style='secondary.TLabel').pack(side=LEFT)
        ttk.Button(header, text="🔄 Refresh", command=self.refresh_data, bootstyle='info-outline').pack(side=RIGHT, padx=(10, 0))

        # Client Filter Dropdown
        self.client_filter_combo = ttk.Combobox(header, textvariable=self.client_filter_var, state="readonly", bootstyle='secondary')
        self.client_filter_combo.pack(side=RIGHT, padx=(10, 0))
        self.client_filter_var.trace_add("write", self._filter_files)
        CustomTooltip(self.client_filter_combo, "Filter files by client")

        # Search Entry
        search_entry = ttk.Entry(header, textvariable=self.search_var, style='secondary.TEntry', width=40)
        search_entry.pack(side=RIGHT, fill=X, expand=True, padx=(20, 0))
        self.search_var.trace_add("write", self._filter_files)
        CustomTooltip(search_entry, "Search by filename, size, date...")

        # --- tksheet Table ---
        self.sheet = Sheet(main_frame,
                           headers=["Filename", "Client", "Size (MB)", "Date", "Verified"],
                           show_x_scrollbar=False,
                           show_y_scrollbar=True)
        self.sheet.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self._configure_sheet_styles()
        self.sheet.enable_bindings("single_select", "row_select", "column_width_resize", "arrowkeys", "right_click_popup_menu")
        self.sheet.extra_bindings([("begin_right_click_popup_menu", self._create_context_menu)])

    def _configure_sheet_styles(self) -> None:
        """Apply the current theme to the tksheet widget."""
        # This is the same styling as the Clients page, could be moved to a helper
        colors = self.app.style.colors
        self.sheet.config(
            background=colors.secondary, foreground=colors.fg, header_background=colors.bg,
            header_foreground=colors.fg, index_background=colors.bg, index_foreground=colors.fg,
            row_index_background=colors.bg, row_index_foreground=colors.fg, table_background=colors.secondary,
            selected_rows_background=colors.info, selected_rows_foreground=colors.light,
            selected_cells_background=colors.info, selected_cells_foreground=colors.light,
            header_selected_columns_background=colors.primary, header_selected_rows_background=colors.primary
        )

    def refresh_data(self) -> None:
        """Fetch latest file and client data from the database."""
        db = self.app.effective_db_manager
        if not db or not self.sheet: return

        try:
            # Fetch clients for the filter dropdown
            self.client_list = db.get_all_clients()
            client_names = ["All Clients"] + [c.get('name', 'Unknown') for c in self.client_list]
            self.client_filter_combo['values'] = client_names
            if not self.client_filter_var.get():
                self.client_filter_var.set("All Clients")

            # Fetch all files
            self.all_files_data = db.get_all_files()
            for f in self.all_files_data:
                f['size_mb'] = f"{f.get('size_bytes', 0) / (1024*1024):.3f}"
                f['verified'] = "✔ Yes" if f.get('verified') else "❌ No"

            self._filter_files()
            self.app.show_toast("File list refreshed.", "success")
        except Exception as e:
            self.app.show_toast(f"Failed to load files: {e}", "danger")
            print(f"ERROR refreshing file data: {e}")

    def _filter_files(self, *args: Any) -> None:
        """Filter file data based on client selection and search query."""
        if not self.sheet: return

        search_query = self.search_var.get().lower()
        client_query = self.client_filter_var.get()

        # First, filter by selected client
        temp_data = self.all_files_data
        if client_query and client_query != "All Clients":
            selected_client_id = next((c['id'] for c in self.client_list if c['name'] == client_query), None)
            if selected_client_id:
                temp_data = [f for f in temp_data if f.get('client_id') == selected_client_id]

        # Then, filter by search text
        if not search_query:
            filtered_data = temp_data
        else:
            filtered_data = [
                f for f in temp_data
                if any(search_query in str(val).lower() for val in f.values())
            ]

        display_data = [[f.get('filename'), f.get('client_name'), f.get('size_mb'), f.get('date'), f.get('verified')] for f in filtered_data]
        self.sheet.set_sheet_data(data=display_data, reset_highlights=True)
        self.sheet.user_data = filtered_data

    def _create_context_menu(self, event: Any) -> None:
        """Create a right-click context menu for the selected file."""
        if not self.sheet: return
        
        selected_rows = self.sheet.get_selected_rows(get_cells=False)
        if not selected_rows: return
        
        selected_row_index = list(selected_rows)[0]
        selected_file = self.sheet.user_data[selected_row_index]

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label=f"🗑️ Delete '{selected_file.get('filename', '')}'", command=lambda f=selected_file: self._delete_file(f))
        menu.add_command(label="🔄 Verify File Integrity") # Placeholder
        menu.tk_popup(event.x_root, event.y_root)

    def _delete_file(self, file_info: Dict[str, Any]) -> None:
        """Handle the file deletion process."""
        db = self.app.effective_db_manager
        if not db: return

        filename = file_info.get('filename', 'this file')
        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {filename}?\nThis action cannot be undone."):
            return
        
        try:
            if db.delete_file(file_info['client_id'], file_info['filename']):
                self.app.show_toast(f"File '{filename}' deleted successfully.", "success")
                self.app.play_sound('success')
                self.refresh_data()
            else:
                self.app.show_toast(f"Failed to delete '{filename}' from database.", "danger")
                self.app.play_sound('failure')
        except Exception as e:
            self.app.show_toast(f"Error deleting file: {e}", "danger")
            self.app.play_sound('failure')

    def on_show(self) -> None:
        """Called when the page is displayed. Triggers a data refresh."""
        self.refresh_data()