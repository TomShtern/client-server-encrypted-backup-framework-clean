# -*- coding: utf-8 -*-
"""
clients.py - The Client Management page for the Server GUI.

This page provides a powerful and interactive view for monitoring and managing
all connected and historical clients. It features a master-detail layout,
real-time filtering, and contextual actions.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Dict, Any, List, Union

try:
    from ttkbootstrap import constants
except ImportError:
    from tkinter import constants

from .base_page import BasePage

try:
    from tksheet import Sheet
    TKSHEET_AVAILABLE = True
except ImportError:
    Sheet = None
    TKSHEET_AVAILABLE = False

if TYPE_CHECKING:
    from ..ServerGUI import ServerGUI

class ClientsPage(BasePage):
    """A page for managing and viewing server clients."""

    def __init__(self, parent: ttk.Frame, controller: 'ServerGUI') -> None:
        super().__init__(parent, controller)
        self.clients_data: List[Dict[str, Any]] = []
        self._current_filtered_data: List[Dict[str, Any]] = []
        
        # UI component type annotations
        self.client_sheet: Union[Any, ttk.Treeview]  # tksheet.Sheet or Treeview fallback
        self.client_tree: ttk.Treeview
        self.detail_frame: ttk.Frame
        self.search_var: tk.StringVar
        self.status_filter_var: tk.StringVar
        
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and lay out all widgets for the clients page."""
        self._create_page_header("Client Management", "people-fill")
        self._create_separator()

        # --- Main Layout: Master-Detail using a PanedWindow ---
        main_pane = ttk.PanedWindow(self, orient=constants.HORIZONTAL)
        main_pane.pack(fill=constants.BOTH, expand=True, padx=10, pady=(0, 10))

        # --- Master View (Left Side): Client List ---
        master_frame = ttk.Frame(main_pane)
        self._create_client_list_view(master_frame)
        main_pane.add(master_frame, weight=3)  # type: ignore[attr-defined]

        # --- Detail View (Right Side): Client Information ---
        self.detail_frame = ttk.Frame(main_pane)
        self._create_detail_view_placeholder() # Initially show a placeholder
        main_pane.add(self.detail_frame, weight=2)  # type: ignore[attr-defined]

    def _create_client_list_view(self, parent: ttk.Frame) -> None:
        """Creates the controls and table for the main client list."""
        controls_frame = self._create_list_controls(parent)
        controls_frame.pack(fill=constants.X, pady=(0, 5))

        # --- Client Table ---
        # Using Treeview as a fallback when tksheet is not available
        if TKSHEET_AVAILABLE and Sheet is not None:
            self.client_sheet = Sheet(parent,
                headers=["Status", "Name", "Client ID", "Last Seen"]
            )
            self.client_sheet.pack(fill=constants.BOTH, expand=True)
            # Configure column properties for visual polish
            self.client_sheet.column_width(column=0, width=80)
            self.client_sheet.column_width(column=1, width=150)
            self.client_sheet.column_width(column=2, width=250)
            self.client_sheet.readonly_columns(columns=[0, 1, 2, 3]) # Make table non-editable
            self.client_sheet.enable_bindings("single_select", "row_select", "arrowkeys")  # type: ignore[attr-defined]
            self.client_sheet.bind("<<SelectCellFinal>>", self._on_client_selected)  # type: ignore[attr-defined]
        else:
            # Fallback to Treeview when tksheet is not available
            self.client_tree = ttk.Treeview(parent, 
                columns=("Status", "Name", "Client ID", "Last Seen"),
                show='headings'
            )
            self.client_tree.pack(fill=constants.BOTH, expand=True)
            
            # Configure column headers and widths
            for col, width in [("Status", 80), ("Name", 150), ("Client ID", 250), ("Last Seen", 120)]:
                self.client_tree.heading(col, text=col)
                self.client_tree.column(col, width=width)
            
            self.client_tree.bind("<<TreeviewSelect>>", self._on_client_selected)
            self.client_sheet = self.client_tree  # type: ignore[assignment] # Unify interface

    def _create_list_controls(self, parent: ttk.Frame) -> ttk.Frame:
        """Creates filtering and search controls for the client list."""
        frame = ttk.Frame(parent)
        
        # Search Entry
        search_icon = self.controller.asset_manager.get_icon("search")
        search_label = ttk.Label(frame, image=search_icon)
        search_label.pack(side=constants.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._apply_filters)  # type: ignore[arg-type]
        search_entry = ttk.Entry(frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=constants.LEFT, fill=constants.X, expand=True)

        # Status Filter Buttons (Layer 3 Polish)
        style = 'Outline.TButton'
        self.status_filter_var = tk.StringVar(value="All")
        ttk.Radiobutton(frame, text="All", variable=self.status_filter_var, value="All", command=self._apply_filters, style=style).pack(side=constants.RIGHT, padx=(5, 0))  # type: ignore[arg-type]
        ttk.Radiobutton(frame, text="Online", variable=self.status_filter_var, value="Online", command=self._apply_filters, style=style).pack(side=constants.RIGHT, padx=(5, 0))  # type: ignore[arg-type]
        ttk.Radiobutton(frame, text="Offline", variable=self.status_filter_var, value="Offline", command=self._apply_filters, style=style).pack(side=constants.RIGHT, padx=(5, 0))  # type: ignore[arg-type]

        return frame

    def _create_detail_view_placeholder(self) -> None:
        """Creates a placeholder message for the detail view when no client is selected."""
        # Clear any existing widgets in the detail frame
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        placeholder = self._create_placeholder(
            "Select a client to view details", "person-badge"
        )
        placeholder.pack(expand=True)

    def _populate_detail_view(self, client_data: Dict[str, Any]) -> None:
        """Populates the detail view with rich information for the selected client."""
        # Clear placeholder or previous details
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        
        card = ttk.Frame(self.detail_frame, style='secondary.TFrame', padding=20, borderwidth=1, relief="solid")
        card.pack(fill=constants.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(card, style='secondary.TFrame')
        header_frame.pack(fill=constants.X, pady=(0, 15))
        icon = self.controller.asset_manager.get_icon("person-vcard-fill", size=(32,32))
        ttk.Label(header_frame, image=icon, style='secondary.TLabel').pack(side=constants.LEFT, padx=(0, 10))
        ttk.Label(header_frame, text=client_data.get('name', 'Unknown Client'), font=('Segoe UI', 16, 'bold'), style='secondary.TLabel').pack(side=constants.LEFT)
        
        # Detail Grid
        details_container = ttk.Frame(card, style='secondary.TFrame')
        details_container.pack(fill=constants.BOTH, expand=True)
        details = {
            "Status": client_data.get('status', 'N/A'),
            "Client ID": client_data.get('id', 'N/A'),
            "IP Address": client_data.get('ip_address', 'N/A'),
            "Last Seen": client_data.get('last_seen', 'N/A'),
            "OS Version": client_data.get('os_version', 'N/A'),
            "Joined": client_data.get('join_date', 'N/A'),
        }
        for i, (key, value) in enumerate(details.items()):
            label = ttk.Label(details_container, text=key, font=('Segoe UI', 10, 'bold'), style='secondary.TLabel')
            label.grid(row=i, column=0, sticky='nw', pady=2)

            val_label = ttk.Entry(details_container, font=('Consolas', 10), style='secondary.TEntry')
            val_label.insert(0, str(value))
            val_label.configure(state='readonly')
            val_label.grid(row=i, column=1, sticky='nsew', padx=(10, 0), pady=2)
        details_container.columnconfigure(1, weight=1)

        # Action Buttons (Layer 3 Innovation)
        actions_frame = ttk.Frame(card, style='secondary.TFrame')
        actions_frame.pack(fill=constants.X, pady=(20, 0))
        ttk.Button(actions_frame, text=" Copy ID", image=self.controller.asset_manager.get_icon("clipboard"), compound=constants.LEFT, style='info.Outline.TButton').pack(side=constants.LEFT)
        # TODO: Add commands to buttons
        if client_data.get('status') == 'Online':
            ttk.Button(actions_frame, text=" Disconnect", image=self.controller.asset_manager.get_icon("power"), compound=constants.LEFT, style='danger.TButton').pack(side=constants.RIGHT)


    def on_show(self) -> None:
        """Called when the page becomes visible; refreshes client data."""
        self._refresh_client_data()

    def handle_update(self, update_type: str, data: Dict[str, Any]) -> None:
        """Handles backend updates relevant to clients."""
        if update_type in {"client_list_changed", "client_stats_update", "status_update"}:
            self._refresh_client_data()

    def _refresh_client_data(self) -> None:
        """Fetches the latest client list from the database and updates the view."""
        db_manager = self.controller.effective_db_manager  # type: ignore[attr-defined]
        server_instance = self.controller.server  # type: ignore[attr-defined]
        if not db_manager or not server_instance:
            self.clients_data = []
            self._apply_filters()
            return
        
        try:
            clients_from_db = db_manager.get_all_clients()  # type: ignore[attr-defined]
            online_ids = list(getattr(server_instance, 'clients', {}).keys())
            
            self.clients_data = [
                {
                    **client,
                    'status': "Online" if bytes.fromhex(client['id']) in online_ids else "Offline"
                }
                for client in clients_from_db
            ]
            self._apply_filters()
        except Exception as e:
            print(f"[ERROR] Failed to refresh client data: {e}")
            self.clients_data = []
            self._apply_filters()

    def _apply_filters(self, *_args: Any) -> None:
        """Filters the client data based on search and status filters, then updates the table."""
        search_term = self.search_var.get().lower()
        status_filter = self.status_filter_var.get()

        filtered_data = self.clients_data
        
        # Apply status filter
        if status_filter != "All":
            filtered_data = [c for c in filtered_data if c['status'] == status_filter]
        
        # Apply search filter
        if search_term:
            filtered_data = [
                c for c in filtered_data if
                search_term in c.get('name', '').lower() or
                search_term in c.get('id', '').lower() or
                search_term in c.get('ip_address', '').lower()
            ]

        # --- Update table with filtered data ---
        if TKSHEET_AVAILABLE and hasattr(self.client_sheet, 'set_sheet_data'):
            # Using tksheet
            table_data: List[List[str]] = []
            for client in filtered_data:
                # Data visualization in the table (Layer 3)
                status_pill = f"● {client['status']}"
                table_data.append([
                    status_pill,
                    client.get('name', ''),
                    client.get('id', ''),
                    client.get('last_seen', '')
                ])
            
            self.client_sheet.set_sheet_data(table_data, redraw=True)  # type: ignore[attr-defined]
            # Apply color coding to the status column
            for r_idx, client in enumerate(filtered_data):
                color = "green" if client['status'] == "Online" else "gray"
                self.client_sheet.highlight_cells(row=r_idx, column=0, bg=color, fg='white')  # type: ignore[attr-defined]
        else:
            # Using Treeview fallback
            # Clear existing items
            for item in self.client_tree.get_children():
                self.client_tree.delete(item)
            
            # Insert new data
            for client in filtered_data:
                status_pill = f"● {client['status']}"
                item_id = self.client_tree.insert('', 'end', values=(
                    status_pill,
                    client.get('name', ''),
                    client.get('id', ''),
                    client.get('last_seen', '')
                ))
                # Apply color coding (limited in Treeview)
                if client['status'] == "Online":
                    self.client_tree.set(item_id, "Status", "🟢 Online")
                else:
                    self.client_tree.set(item_id, "Status", "🔴 Offline")
        
        # Store filtered data for selection events
        self._current_filtered_data = filtered_data

    def _on_client_selected(self, _event: Any) -> None:
        """Callback for when a client is selected in the table."""
        try:
            if TKSHEET_AVAILABLE and hasattr(self.client_sheet, 'get_currently_selected'):
                # tksheet selection handling
                selection = self.client_sheet.get_currently_selected()  # type: ignore[attr-defined]
                if selection and selection[0] is not None:
                    selected_row_index = selection[0]
                else:
                    self._create_detail_view_placeholder()
                    return
            else:
                # Treeview selection handling
                if not hasattr(self.client_tree, 'selection') or not self.client_tree.selection():
                    self._create_detail_view_placeholder()
                    return
                    
                selected_item = self.client_tree.selection()[0]
                selected_row_index = self.client_tree.index(selected_item)
            
            # Use the stored filtered data
            if hasattr(self, '_current_filtered_data') and 0 <= selected_row_index < len(self._current_filtered_data):
                selected_client_data = self._current_filtered_data[selected_row_index]
                self._populate_detail_view(selected_client_data)
            else:
                self._create_detail_view_placeholder()
                
        except (IndexError, AttributeError, TypeError) as e:
            print(f"[DEBUG] Selection event error: {e}")
            self._create_detail_view_placeholder()