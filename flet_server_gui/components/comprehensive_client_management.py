#!/usr/bin/env python3
"""
Comprehensive Client Management Component (Refactored)
Complete feature parity with TKinter GUI client management functionality.
Now uses modular architecture with separate components for better maintainability.
"""

import flet as ft
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from ..utils.server_bridge import ServerBridge
from .base_component import BaseComponent
from .button_factory import ActionButtonFactory
from .client_table_renderer import ClientTableRenderer
from .client_filter_manager import ClientFilterManager
from .client_action_handlers import ClientActionHandlers
from ..actions import ClientActions
from ..layouts import ResponsiveBuilder, BreakpointManager


class ComprehensiveClientManagement(BaseComponent):
    """
    Complete client management with modular architecture.
    Composed of specialized components for table rendering, filtering, and actions.
    """
    
    def __init__(self, server_bridge: ServerBridge, dialog_system, toast_manager, page):
        super().__init__(page, dialog_system, toast_manager)
        self.server_bridge = server_bridge
        
        # Initialize button factory
        self.button_factory = ActionButtonFactory(self, server_bridge, page)
        
        # Initialize modular components
        self.table_renderer = ClientTableRenderer(server_bridge, self.button_factory, page)
        self.filter_manager = ClientFilterManager(page, toast_manager)
        self.action_handlers = ClientActionHandlers(server_bridge, dialog_system, toast_manager, page)
        
        # Setup callbacks
        self.filter_manager.on_filter_changed = self._on_filtered_data_changed
        self.action_handlers.set_data_changed_callback(self._refresh_clients)
        
        # UI Components
        self.status_text = None
        self.refresh_button = None
        self.bulk_actions_row = None
        self.select_all_checkbox = None
        
        # Data
        self.selected_clients = []
    
    def build(self) -> ft.Control:
        """Build the comprehensive client management view using modular components."""
        
        # Header with title and status
        self.status_text = ft.Text(
            "Loading client data...",
            size=14,
            color=ft.Colors.BLUE_600
        )
        
        # Refresh button
        self.refresh_button = ft.ElevatedButton(
            "Refresh Clients",
            icon=ft.Icons.REFRESH,
            on_click=self._refresh_clients,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.ON_PRIMARY
            )
        )
        
        # Search and filter controls from filter manager
        search_controls = self.filter_manager.create_search_controls(self._on_filtered_data_changed)
        
        # Client table from table renderer
        client_table_container = self.table_renderer.get_table_container()
        
        # Select all checkbox
        self.select_all_checkbox = ft.Checkbox(
            label="Select All",
            on_change=self._on_select_all
        )
        
        # Bulk actions row
        self.bulk_actions_row = ft.Row([
            ft.Text("Bulk Actions:", weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Disconnect Selected",
                icon=ft.Icons.LOGOUT,
                on_click=self._bulk_disconnect,
                style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_100),
                visible=False
            ),
            ft.ElevatedButton(
                "Delete Selected",
                icon=ft.Icons.DELETE_FOREVER,
                on_click=self._bulk_delete,
                style=ft.ButtonStyle(bgcolor=ft.Colors.RED_100),
                visible=False
            ),
        ], spacing=10)
        
        # Main layout
        return ft.Container(
            content=ft.Column([
                # Header section
                ft.Row([
                    ft.Icon(ft.Icons.PEOPLE, size=24),
                    ft.Text("Client Management", style=ft.TextThemeStyle.TITLE_LARGE, expand=True),
                    self.refresh_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                # Status
                self.status_text,
                
                ft.Divider(),
                
                # Search and filters
                search_controls,
                
                ft.Divider(),
                
                # Selection and bulk actions
                ft.Row([
                    self.select_all_checkbox,
                    ft.VerticalDivider(width=20),
                    self.bulk_actions_row
                ]),
                
                ft.Divider(),
                
                # Client table
                client_table_container,
                
            ], spacing=10, expand=True),
            padding=20,
            expand=True
        )
    
    async def _refresh_clients(self, e=None):
        """Refresh client data from server"""
        try:
            self.status_text.value = "Refreshing client data..."
            self.page.update()
            
            # Get fresh client data from server bridge
            clients_data = await self.execute_with_loading(
                self.server_bridge.get_all_clients(),
                "Loading clients..."
            )
            
            if clients_data:
                # Update filter manager with new data
                self.filter_manager.set_client_data(clients_data)
                
                # Update status
                self.status_text.value = f"✅ Found {len(clients_data)} clients"
                self.status_text.color = ft.Colors.GREEN_600
            else:
                # No clients found
                self.filter_manager.set_client_data([])
                self.status_text.value = "No clients found"
                self.status_text.color = ft.Colors.GREY_600
            
            # Clear selections
            self.selected_clients.clear()
            self._update_bulk_actions_visibility()
            
            self.page.update()
            
        except Exception as e:
            # Handle error
            self.status_text.value = f"❌ Error loading clients: {str(e)}"
            self.status_text.color = ft.Colors.ERROR
            self.page.update()
            
            if self.toast_manager:
                self.toast_manager.show_error(f"Failed to refresh clients: {str(e)}")
    
    def _on_filtered_data_changed(self, filtered_clients: List[Any]):
        """Handle when filtered client data changes"""
        # Update table renderer with filtered data
        self.table_renderer.populate_client_table(
            filtered_clients, 
            self._on_client_select, 
            self.selected_clients
        )
        
        # Update status
        total_clients = len(self.filter_manager.all_clients)
        filtered_count = len(filtered_clients)
        
        if filtered_count == total_clients:
            self.status_text.value = f"✅ Showing all {total_clients} clients"
        else:
            self.status_text.value = f"✅ Showing {filtered_count} of {total_clients} clients"
        
        self.status_text.color = ft.Colors.GREEN_600
        
        # Update UI
        self.page.update()
    
    def _on_select_all(self, e):
        """Handle select all checkbox"""
        select_all = e.control.value
        self.selected_clients.clear()
        
        filtered_clients = self.filter_manager.get_filtered_clients()
        
        if select_all:
            self.selected_clients = [client.client_id for client in filtered_clients]
        
        # Update table display
        self.table_renderer.populate_client_table(
            filtered_clients,
            self._on_client_select,
            self.selected_clients
        )
        
        self._update_bulk_actions_visibility()
        self.page.update()
    
    def _on_client_select(self, e):
        """Handle individual client selection"""
        client_id = e.control.data
        
        if e.control.value:
            if client_id not in self.selected_clients:
                self.selected_clients.append(client_id)
        else:
            if client_id in self.selected_clients:
                self.selected_clients.remove(client_id)
        
        # Update select all checkbox state
        filtered_clients = self.filter_manager.get_filtered_clients()
        total_filtered = len(filtered_clients)
        selected_count = len(self.selected_clients)
        
        if selected_count == 0:
            self.select_all_checkbox.value = False
        elif selected_count == total_filtered:
            self.select_all_checkbox.value = True
        else:
            self.select_all_checkbox.value = None  # Indeterminate state
        
        self._update_bulk_actions_visibility()
        self.page.update()
    
    def _update_bulk_actions_visibility(self):
        """Update visibility of bulk action buttons"""
        has_selections = len(self.selected_clients) > 0
        
        if self.bulk_actions_row and len(self.bulk_actions_row.controls) > 1:
            # Show/hide bulk action buttons (skip the label)
            for i, control in enumerate(self.bulk_actions_row.controls):
                if i > 0 and isinstance(control, ft.ElevatedButton):
                    control.visible = has_selections
    
    async def _bulk_disconnect(self, e):
        """Handle bulk disconnect action"""
        await self.action_handlers.perform_bulk_action("disconnect", self.selected_clients)
        self.selected_clients.clear()
        self._update_bulk_actions_visibility()
        self.select_all_checkbox.value = False
    
    async def _bulk_delete(self, e):
        """Handle bulk delete action"""
        await self.action_handlers.perform_bulk_action("delete", self.selected_clients)
        self.selected_clients.clear()
        self._update_bulk_actions_visibility()
        self.select_all_checkbox.value = False
    
    # Auto-refresh functionality
    async def start_auto_refresh(self, interval_seconds: int = 30):
        """Start automatic refresh of client data"""
        while True:
            await asyncio.sleep(interval_seconds)
            if self.page:  # Check if page is still active
                await self._refresh_clients()
    
    def get_component_stats(self) -> Dict[str, Any]:
        """Get statistics about the component state"""
        return {
            'total_clients': len(self.filter_manager.all_clients),
            'filtered_clients': len(self.filter_manager.get_filtered_clients()),
            'selected_clients': len(self.selected_clients),
            'filter_stats': self.filter_manager.get_filter_stats()
        }