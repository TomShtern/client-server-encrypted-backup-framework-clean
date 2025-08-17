# In file: gui_pages/clients.py

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.constants import *  # Import all tkinter constants (BOTH, LEFT, RIGHT, etc.)
from typing import TYPE_CHECKING, List, Dict, Any, Optional

# Conditional imports for type checking and runtime
if TYPE_CHECKING:
    from ..ServerGUI import EnhancedServerGUI, RoundedFrame

# Import base class and check for dependencies
try:
    from ..ServerGUI import BasePage, TKSHEET_AVAILABLE
except ImportError:
    # Fallback for different import paths
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from ServerGUI import BasePage, TKSHEET_AVAILABLE
    except ImportError:
        # Define minimal fallbacks
        class BasePage:
            def __init__(self, parent, app, **kwargs): pass
        TKSHEET_AVAILABLE = False

if TKSHEET_AVAILABLE:
    from tksheet import Sheet

class ClientsPage(BasePage):
    """A page for viewing and managing connected and historical clients."""

    def __init__(self, parent: tk.Widget, app: EnhancedServerGUI, **kwargs: Any) -> None:
        super().__init__(parent, app, **kwargs)

        self.all_clients_data: List[Dict[str, Any]] = []
        self.sheet: Optional[Sheet] = None
        self.detail_widgets: Dict[str, ttk.Label] = {}
        self.selected_client_id: Optional[str] = None
        self.search_var = tk.StringVar()

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and lay out all widgets for the clients page."""
        if not TKSHEET_AVAILABLE:
            ttk.Label(self, text="tksheet library not found.\nPlease run: pip install tksheet", style='danger.TLabel').pack(expand=True)
            return

        # Use a PanedWindow for resizable master-detail view
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL, bootstyle='primary')
        paned_window.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # --- Master View (Client List) ---
        master_frame_rounded = self.app.RoundedFrame(paned_window, bg_color=self.app.style.colors.secondary, border_color=self.app.style.colors.border)
        master_frame = master_frame_rounded.content_frame
        
        # Header with Title and Search Bar
        header = ttk.Frame(master_frame, style='secondary.TFrame')
        header.pack(fill=X, padx=10, pady=(5, 10))
        ttk.Label(header, text="👥 Client Roster", font=self.app.Theme.FONT_BOLD, style='secondary.TLabel').pack(side=LEFT)
        
        search_entry = ttk.Entry(header, textvariable=self.search_var, style='secondary.TEntry')
        search_entry.pack(side=RIGHT, fill=X, expand=True, padx=(20, 0))
        self.search_var.trace_add("write", self._filter_clients)
        CustomTooltip(search_entry, "Search by any client attribute...")

        # tksheet Table
        self.sheet = Sheet(master_frame,
                           headers=["Name", "Status", "Client ID", "Last Seen"],
                           show_x_scrollbar=False,
                           show_y_scrollbar=True,
                           width=550,
                           height=400)
        self.sheet.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self._configure_sheet_styles()
        self.sheet.enable_bindings("single_select", "row_select", "column_width_resize", "arrowkeys")
        self.sheet.extra_bindings([("row_select", self._on_client_selected)])

        paned_window.add(master_frame_rounded, weight=2)

        # --- Detail View ---
        detail_frame_rounded = self.app.RoundedFrame(paned_window, bg_color=self.app.style.colors.secondary, border_color=self.app.style.colors.border)
        self.detail_frame = detail_frame_rounded.content_frame
        paned_window.add(detail_frame_rounded, weight=1)

        self._create_detail_view_content()

    def _configure_sheet_styles(self) -> None:
        """Apply the current theme to the tksheet widget."""
        colors = self.app.style.colors
        self.sheet.config(
            background=colors.secondary,
            foreground=colors.fg,
            header_background=colors.bg,
            header_foreground=colors.fg,
            index_background=colors.bg,
            index_foreground=colors.fg,
            row_index_background=colors.bg,
            row_index_foreground=colors.fg,
            table_background=colors.secondary,
            selected_rows_background=colors.info,
            selected_rows_foreground=colors.light,
            selected_cells_background=colors.info,
            selected_cells_foreground=colors.light,
            header_selected_columns_background=colors.primary,
            header_selected_rows_background=colors.primary
        )

    def _create_detail_view_content(self) -> None:
        """Create the static labels and dynamic value labels for the detail pane."""
        ttk.Label(self.detail_frame, text="ℹ️ Client Details", font=self.app.Theme.FONT_BOLD, style='secondary.TLabel').pack(anchor=NW, padx=10, pady=5)

        detail_grid = ttk.Frame(self.detail_frame, style='secondary.TFrame')
        detail_grid.pack(fill=X, expand=True, padx=10, pady=10)
        detail_grid.columnconfigure(1, weight=1)

        details_to_show = {
            "name": "Name:", "id": "Client ID:", "status": "Status:", "last_seen": "Last Seen:",
            "ip_address": "IP Address:", "os_type": "Operating System:", "mac_address": "MAC Address:"
        }
        
        for i, (key, label_text) in enumerate(details_to_show.items()):
            ttk.Label(detail_grid, text=label_text, style='secondary.TLabel', font=self.app.Theme.FONT_SMALL).grid(row=i, column=0, sticky=W, pady=3)
            value_label = ttk.Label(detail_grid, text="N/A", style='secondary.TLabel', font=self.app.Theme.FONT_BOLD, anchor=W, wraplength=250)
            value_label.grid(row=i, column=1, sticky=EW, pady=3, padx=(5,0))
            self.detail_widgets[key] = value_label
        
        # Action Buttons
        action_frame = ttk.Frame(self.detail_frame, style='secondary.TFrame')
        action_frame.pack(side=BOTTOM, fill=X, padx=10, pady=10)
        
        ttk.Button(action_frame, text="🔄 Refresh List", command=self.refresh_data, bootstyle='info-outline').pack(side=LEFT, expand=True, padx=5)
        ttk.Button(action_frame, text="🔌 Disconnect", command=self._disconnect_selected_client, bootstyle='danger-outline').pack(side=LEFT, expand=True, padx=5)


    def refresh_data(self) -> None:
        """Fetch the latest client data from the database and update the sheet."""
        db = self.app.effective_db_manager
        if not db or not self.sheet:
            return

        try:
            self.all_clients_data = db.get_all_clients()
            online_ids = list(self.app.server.clients.keys()) if self.app.server else []
            
            for client in self.all_clients_data:
                client_id_bytes = bytes.fromhex(client['id']) if isinstance(client.get('id'), str) else client.get('id', b'')
                client['status'] = "Online" if client_id_bytes in online_ids else "Offline"
            
            self._filter_clients() # This will apply search and refresh sheet
            self.app.show_toast("Client list refreshed.", "success")
        except Exception as e:
            self.app.show_toast(f"Failed to load clients: {e}", "danger")
            print(f"ERROR refreshing client data: {e}")

    def _filter_clients(self, *args: Any) -> None:
        """Filter client data based on the search query and update the sheet."""
        if not self.sheet: return
        
        query = self.search_var.get().lower()
        
        if not query:
            filtered_data = self.all_clients_data
        else:
            filtered_data = [
                client for client in self.all_clients_data
                if any(query in str(val).lower() for val in client.values())
            ]
        
        # Prepare data for tksheet
        display_data = [[c.get('name', ''), c.get('status', ''), c.get('id', ''), c.get('last_seen', '')] for c in filtered_data]
        
        # Keep track of original data indices
        self.sheet.set_sheet_data(data=display_data, reset_highlights=True)
        self.sheet.user_data = filtered_data # Store full data dicts for selection

    def _on_client_selected(self, event: Any) -> None:
        """Handle the selection of a client in the tksheet."""
        if not self.sheet or not event.row: return

        selected_row_index = event.row
        
        # Get the full data dict from our stored user_data
        if hasattr(self.sheet, 'user_data') and len(self.sheet.user_data) > selected_row_index:
            selected_client = self.sheet.user_data[selected_row_index]
            self.selected_client_id = selected_client.get('id')
            self._update_detail_view(selected_client)

    def _update_detail_view(self, client_data: Dict[str, Any]) -> None:
        """Populate the detail view with data from the selected client."""
        for key, label in self.detail_widgets.items():
            value = client_data.get(key, "N/A")
            if key == 'status':
                style = 'success.TLabel' if value == 'Online' else 'danger.TLabel'
                label.config(text=value, style=style)
            else:
                label.config(text=value)

    def _disconnect_selected_client(self) -> None:
        """Disconnect the currently selected client if they are online."""
        if not self.selected_client_id:
            self.app.show_toast("No client selected.", "warning")
            return
        
        client_data = next((c for c in self.all_clients_data if c['id'] == self.selected_client_id), None)
        if not client_data or client_data.get('status') != 'Online':
            self.app.show_toast("Selected client is not online.", "info")
            return

        if self.app.server and self.app.server.network_server:
            if messagebox.askyesno("Confirm Disconnect", f"Are you sure you want to disconnect {client_data.get('name', 'this client')}?"):
                client_id_bytes = bytes.fromhex(self.selected_client_id)
                if self.app.server.network_server.disconnect_client(client_id_bytes):
                    self.app.show_toast(f"Client {client_data.get('name')} disconnected.", "success")
                    self.app.play_sound('disconnect')
                    self.refresh_data() # Refresh list to show new status
                else:
                    self.app.show_toast("Failed to send disconnect signal.", "danger")
    
    def on_show(self) -> None:
        """Called when the page is displayed. Triggers a data refresh."""
        self.refresh_data()