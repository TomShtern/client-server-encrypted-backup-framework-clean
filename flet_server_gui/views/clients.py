"""
Purpose: Client management view
Logic: Client listing, filtering, and management operations
UI: Client table, action buttons, and client details
"""

#!/usr/bin/env python3
"""
Client Management View
Complete feature parity with TKinter GUI client management functionality.
Now uses modular architecture with separate components for better maintainability.
"""

import flet as ft
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

# Existing imports
from flet_server_gui.core.client_management import ClientManagement
from flet_server_gui.ui.widgets.tables import EnhancedDataTable
from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
from flet_server_gui.utils.thread_safe_ui import ThreadSafeUIUpdater, ui_safe_update
from flet_server_gui.components.client_table_renderer import ClientTableRenderer
from flet_server_gui.components.client_filter_manager import ClientFilterManager
from flet_server_gui.components.client_action_handlers import ClientActionHandlers
from flet_server_gui.actions.client_actions import ClientActions
from flet_server_gui.layouts.responsive_utils import ResponsiveBuilder
from flet_server_gui.layouts.breakpoint_manager import BreakpointManager
from flet_server_gui.components.base_component import BaseComponent

# Theme consistency import
from flet_server_gui.ui.unified_theme_system import apply_theme_consistency

# Enhanced components imports
from flet_server_gui.ui.widgets import (
    EnhancedButton,
    EnhancedCard,
    EnhancedTable,
    EnhancedWidget,
    EnhancedButtonConfig,
    ButtonVariant,
    CardVariant,
    TableSize,
    WidgetSize,
    WidgetType
)

# Layout fixes imports
from flet_server_gui.ui.layouts.responsive_fixes import ResponsiveLayoutFixes
# Unified theme system - consolidated theme functionality
from flet_server_gui.ui.unified_theme_system import ThemeConsistencyManager, TOKENS



class ClientsView(BaseComponent):
    """
    Complete client management view with modular architecture.
    Composed of specialized components for table rendering, filtering, and actions.
    """
    
    def __init__(self, server_bridge, dialog_system, toast_manager, page):
        self.server_bridge = server_bridge
        self.page = page
        self.toast_manager = toast_manager
        self.dialog_system = dialog_system
        
        # Initialize thread-safe UI updater
        self.ui_updater = ThreadSafeUIUpdater(page)
        self._updater_started = False
        
        # Initialize parent BaseComponent
        super().__init__(page, dialog_system, toast_manager)
        
        # Initialize theme consistency manager
        self.theme_manager = ThemeConsistencyManager(page)
        
        # Initialize button factory
        self.button_factory = ActionButtonFactory(self, server_bridge, page)
        
        # Initialize modular components
        self.table_renderer = ClientTableRenderer(server_bridge, self.button_factory, page)
        self.filter_manager = ClientFilterManager(page, toast_manager)
        self.action_handlers = ClientActionHandlers(server_bridge, dialog_system, toast_manager, page)
        
        # Set action handlers in button factory
        self.button_factory.actions["ClientActionHandlers"] = self.action_handlers
        
        # Also set in the base component for backward compatibility
        self.actions = {
            "ClientActionHandlers": self.action_handlers
        }
        
        # Setup callbacks
        self.filter_manager.on_filter_changed = self._on_filtered_data_changed
        print(f"[DEBUG] Setting on_data_changed callback: {self._refresh_clients}")
        self.action_handlers.set_data_changed_callback(self._refresh_clients)
        print(f"[DEBUG] on_data_changed callback set successfully")
        
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
            color=TOKENS['primary']
        )
        
        # Refresh button
        self.refresh_button = ft.ElevatedButton(
            "Refresh Clients",
            icon=ft.Icons.REFRESH,
            on_click=self._refresh_clients,
            # Let theme handle button colors automatically
        )
        
        # Search and filter controls from filter manager
        search_controls = self.filter_manager.create_search_controls(self._on_filtered_data_changed)
        
        # Bulk actions row - Remove hardcoded styles and apply responsive fixes
        self.bulk_actions_row = ft.Row([
            ft.Text("Bulk Actions:", weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Disconnect Selected",
                icon=ft.Icons.LOGOUT,
                on_click=self._bulk_disconnect,
                visible=False
            ),
            ft.ElevatedButton(
                "Delete Selected",
                icon=ft.Icons.DELETE_FOREVER,
                on_click=self._bulk_delete,
                visible=False
            ),
        ], spacing=10)
        
        # Apply hitbox fixes to bulk action buttons
        for control in self.bulk_actions_row.controls:
            if isinstance(control, ft.ElevatedButton):
                control = ResponsiveLayoutFixes.fix_button_hitbox(control)
        
        # Select all checkbox
        self.select_all_checkbox = ft.Checkbox(
            label="Select All",
            on_change=self._on_select_all
        )
        
        # Apply hitbox fixes to buttons
        if self.refresh_button:
            self.refresh_button = ResponsiveLayoutFixes.fix_button_hitbox(self.refresh_button)
        
        if self.select_all_checkbox:
            self.select_all_checkbox = ResponsiveLayoutFixes.fix_hitbox_alignment(self.select_all_checkbox)
        
        # Client table from table renderer - Apply responsive layout fixes
        client_table_container = self.table_renderer.get_table_container()
        # Ensure client_table_container is not None
        if client_table_container is None:
            client_table_container = ft.Container(
                content=ft.Text("Client table not available"),
                padding=20,
                alignment=ft.alignment.center
            )
        client_table_container = ResponsiveLayoutFixes.create_clipping_safe_container(
            client_table_container
        )
        
        # Apply windowed mode compatibility
        main_content = ft.Column([
            # Header section
            ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PEOPLE, size=24),
                        ft.Text("Client Management", style=ft.TextThemeStyle.TITLE_LARGE),
                    ])
                ], col={"xs": 12, "sm": 6, "md": 8}),
                ft.Column([
                    self.refresh_button
                ], col={"xs": 12, "sm": 6, "md": 4}, alignment=ft.MainAxisAlignment.END)
            ]),
            
            ft.Divider(),
            
            # Status
            self.status_text,
            
            ft.Divider(),
            
            # Search and filters
            search_controls,
            
            ft.Divider(),
            
            # Selection and bulk actions
            ft.ResponsiveRow([
                ft.Column([
                    self.select_all_checkbox
                ], col={"xs": 12, "sm": 6}),
                ft.Column([
                    self.bulk_actions_row
                ], col={"xs": 12, "sm": 6})
            ]),
            
            ft.Divider(),
            
            # Client table
            ft.ResponsiveRow([
                ft.Column([
                    client_table_container
                ], col={"xs": 12})
            ], expand=True),
            
        ], spacing=10, expand=True)
        
        # Apply windowed mode compatibility
        main_layout = ResponsiveLayoutFixes.create_windowed_layout_fix(main_content)
        
        # Apply theme consistency
        apply_theme_consistency(self.page)
        
        # Main layout
        return ft.Container(
            content=main_layout,
            padding=20,
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE
        )
    
    async def _refresh_clients(self, e=None):
        """Refresh client data with comprehensive error handling and user feedback."""
        print(f"[DEBUG] _refresh_clients called with event: {e}")
        try:
            # Disable refresh button during refresh
            if self.refresh_button:
                self.refresh_button.disabled = True
                self.refresh_button.text = "Refreshing..."
                # Thread-safe UI update
                if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
                    self.ui_updater.queue_update(lambda: None)
                else:
                    self.page.update()

            # Validate server bridge availability
            if not self.server_bridge:
                raise ConnectionError("Server bridge is not initialized")
            
            # Check if server bridge has connection validation
            if hasattr(self.server_bridge, 'is_connected'):
                if not await self.server_bridge.is_connected():
                    raise ConnectionError("Server is not connected. Please check server status.")

            # Get fresh client data with timeout
            clients = self.server_bridge.get_clients()

            # Update filter manager with new data
            self.filter_manager.update_client_data(clients)

            # Update table with filtered data
            filtered_clients = self.filter_manager.get_filtered_clients()
            self.table_renderer.update_table_data(filtered_clients, self._on_client_selected, self.selected_clients)

            # Update status
            if self.status_text:
                self.status_text.value = f"Loaded {len(clients)} clients"
                # Use theme-aware color or let it inherit from theme
            
            # Reset selection
            self.selected_clients.clear()
            if self.select_all_checkbox:
                self.select_all_checkbox.value = False
            
            print(f"[DEBUG] _refresh_clients completed successfully, loaded {len(clients)} clients")
            
        except asyncio.TimeoutError:
            if self.status_text:
                self.status_text.value = "❌ Timeout loading client data"
                # Use theme-aware color or let it inherit from theme
            if self.toast_manager:
                self.toast_manager.show_error("Timeout loading client data. Please try again.")
            print(f"[ERROR] Timeout error in _refresh_clients")
            
        except Exception as e:
            if self.status_text:
                self.status_text.value = f"❌ Error loading client data: {str(e)}"
                # Use theme-aware color or let it inherit from theme
            if self.toast_manager:
                self.toast_manager.show_error(f"Error loading client data: {str(e)}")
            print(f"[ERROR] Exception in _refresh_clients: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Re-enable refresh button
            if self.refresh_button:
                self.refresh_button.disabled = False
                self.refresh_button.text = "Refresh Clients"
                # Thread-safe UI update
                if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
                    self.ui_updater.queue_update(lambda: None)
                else:
                    self.page.update()
    
    def _on_filtered_data_changed(self, filtered_clients: List[Dict[str, Any]]):
        """Handle filtered data changes from filter manager with defensive checks."""
        try:
            # Defensive check for None or empty data
            if filtered_clients is None:
                filtered_clients = []
                if self.status_text:
                    self.status_text.value = "No client data available"
                    # Use theme-aware color or let it inherit from theme
                return
            
            # Update table with new filtered data
            if hasattr(self, 'table_renderer') and self.table_renderer:
                self.table_renderer.update_table_data(filtered_clients, self._on_client_selected, self.selected_clients)
            else:
                print("[WARNING] Table renderer not available for client data update")
            
            # Update status text
            if self.status_text:
                total_clients = len(self.filter_manager.all_clients)
                self.status_text.value = f"Showing {len(filtered_clients)} of {total_clients} clients"
                # Use theme-aware color or let it inherit from theme
            
            # Reset selection when filter changes
            self.selected_clients.clear()
            if self.select_all_checkbox:
                self.select_all_checkbox.value = False
                self._update_bulk_actions_visibility()
            
            # Thread-safe UI update
            if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
                self.ui_updater.queue_update(lambda: None)
            else:
                self.page.update()
            
        except Exception as ex:
            if self.status_text:
                self.status_text.value = f"Error updating filter: {str(ex)}"
                # Use theme-aware color or let it inherit from theme
            # Thread-safe UI update
            if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
                self.ui_updater.queue_update(lambda: None)
            else:
                self.page.update()
    
    def _on_select_all(self, e):
        """Handle select all checkbox changes."""
        try:
            if e.control.value:  # Select all
                filtered_clients = self.filter_manager.get_filtered_clients()
                self.selected_clients = [client['id'] for client in filtered_clients]
                # Update table selection
                self.table_renderer.select_all_rows()
            else:  # Deselect all
                self.selected_clients.clear()
                # Update table selection
                self.table_renderer.deselect_all_rows()
            
            self._update_bulk_actions_visibility()
            # Thread-safe UI update
            if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
                self.ui_updater.queue_update(lambda: None)
            else:
                self.page.update()
            
        except Exception as ex:
            if self.toast_manager:
                self.toast_manager.show_error(f"Error in selection: {str(ex)}")
    
    def _on_client_selected(self, e):
        """Handle individual client selection from table."""
        try:
            # Extract client_id and selection state from the event
            client_id = e.data
            selected = e.control.value if hasattr(e.control, 'value') else False
            
            if selected:
                if client_id not in self.selected_clients:
                    self.selected_clients.append(client_id)
            else:
                if client_id in self.selected_clients:
                    self.selected_clients.remove(client_id)
            
            # Update select all checkbox state
            self._update_select_all_checkbox()
            
            self._update_bulk_actions_visibility()
            # Thread-safe UI update
            if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
                self.ui_updater.queue_update(lambda: None)
            else:
                self.page.update()
            
        except Exception as ex:
            if self.toast_manager:
                self.toast_manager.show_error(f"Error in client selection: {str(ex)}")
    
    def _update_select_all_checkbox(self):
        """Update select all checkbox based on current selection state."""
        try:
            filtered_clients = self.filter_manager.get_filtered_clients()
            total_filtered = len(filtered_clients)
            selected_count = len(self.selected_clients)
            
            if self.select_all_checkbox is None:
                return
                
            if selected_count == 0:
                self.select_all_checkbox.value = False
            elif selected_count == total_filtered:
                self.select_all_checkbox.value = True
            else:
                self.select_all_checkbox.value = None  # Indeterminate state
            
            self._update_bulk_actions_visibility()
            # Thread-safe UI update
            if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
                self.ui_updater.queue_update(lambda: None)
            else:
                self.page.update()
        except Exception:
            pass  # Ignore errors in checkbox updates
    
    def _update_bulk_actions_visibility(self):
        """Update visibility of bulk action buttons"""
        try:
            has_selections = len(self.selected_clients) > 0
            
            if self.bulk_actions_row and len(self.bulk_actions_row.controls) > 1:
                # Show/hide bulk action buttons (skip the label)
                for i, control in enumerate(self.bulk_actions_row.controls):
                    if i > 0 and isinstance(control, ft.ElevatedButton):
                        control.visible = has_selections
        except Exception:
            pass  # Ignore errors in visibility updates
    
    async def _bulk_disconnect(self, e):
        """Handle bulk disconnect action"""
        try:
            await self.action_handlers.perform_bulk_action("disconnect", self.selected_clients)
            self.selected_clients.clear()
            self._update_bulk_actions_visibility()
            if self.select_all_checkbox:
                self.select_all_checkbox.value = False
            await self._refresh_clients()
        except Exception as ex:
            if self.toast_manager:
                self.toast_manager.show_error(f"Error in bulk disconnect: {str(ex)}")
    
    async def _bulk_delete(self, e):
        """Handle bulk delete action"""
        try:
            await self.action_handlers.perform_bulk_action("delete", self.selected_clients)
            self.selected_clients.clear()
            self._update_bulk_actions_visibility()
            if self.select_all_checkbox:
                self.select_all_checkbox.value = False
            await self._refresh_clients()
        except Exception as ex:
            if self.toast_manager:
                self.toast_manager.show_error(f"Error in bulk delete: {str(ex)}")
    
    # Auto-refresh functionality
    async def start_auto_refresh(self, interval_seconds: int = 30):
        """Start automatic refresh of client data"""
        # Start the thread-safe UI updater
        if not self._updater_started:
            await self.ui_updater.start()
            self._updater_started = True
            
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

    def update_data(self):
        """Update client data"""
        # Implementation will be added here
        pass