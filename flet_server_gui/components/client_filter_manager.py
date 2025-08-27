#!/usr/bin/env python3
"""
Client Filter Manager Component
Handles search, filtering, and sorting logic for client data with debouncing.
"""

import flet as ft
import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime


class ClientFilterManager:
    """Manages filtering and search functionality for client data"""
    
    def __init__(self, page: ft.Page, toast_manager=None):
        self.page = page
        self.toast_manager = toast_manager
        
        # Data storage
        self.all_clients = []
        self.filtered_clients = []
        
        # Filter state
        self._current_filter = "all"
        
        # Search debouncing (with fix from comprehensive_client_management.py)
        self._search_timer: Optional[asyncio.Task] = None
        
        # UI Components
        self.search_field = None
        self.status_chips = None
        
        # Callbacks
        self.on_filter_changed: Optional[Callable] = None
    
    def create_search_controls(self, on_filter_change_callback: Callable) -> ft.Column:
        """Create search and filter UI controls"""
        self.on_filter_changed = on_filter_change_callback
        
        # Search field with debouncing
        self.search_field = ft.TextField(
            label="Search clients...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            expand=True,
        )
        
        # Status filter chips
        self.status_chips = ft.Row([
            ft.Chip(
                label=ft.Text("All"),
                selected=True,
                on_select=lambda e: self._on_chip_select("all", e),
                bgcolor=ft.Colors.PRIMARY_CONTAINER,
            ),
            ft.Chip(
                label=ft.Text("Connected"),
                on_select=lambda e: self._on_chip_select("connected", e),
                bgcolor=ft.Colors.GREEN_100,
            ),
            ft.Chip(
                label=ft.Text("Registered"),
                on_select=lambda e: self._on_chip_select("registered", e),
                bgcolor=ft.Colors.BLUE_100,
            ),
            ft.Chip(
                label=ft.Text("Offline"),
                on_select=lambda e: self._on_chip_select("offline", e),
                bgcolor=ft.Colors.ORANGE_100,
            )
        ], spacing=8, wrap=True)
        
        return ft.Column([
            ft.Row([
                self.search_field,
            ], expand=True),
            ft.Divider(height=10),
            ft.Text("Filter by Status:", size=12, weight=ft.FontWeight.BOLD),
            self.status_chips
        ], spacing=10)
    
    def set_client_data(self, clients: List[Any]) -> None:
        """Set the client data to filter"""
        self.all_clients = clients
        self._apply_filters()
    
    def update_client_data(self, clients: List[Any]) -> None:
        """Update client data - alias for set_client_data"""
        self.set_client_data(clients)
    
    def get_filtered_clients(self) -> List[Any]:
        """Get the current filtered client list"""
        return self.filtered_clients
    
    def _apply_filters(self) -> None:
        """Apply current search and filter criteria"""
        # Start with all clients
        filtered = self.all_clients[:]
        
        # Apply search filter
        search_term = self.search_field.value.lower() if self.search_field and self.search_field.value else ""
        if search_term:
            filtered_search = []
            for c in filtered:
                client_id = ""
                if hasattr(c, 'client_id'):
                    client_id = c.client_id.lower()
                elif hasattr(c, '__getitem__'):  # Check if it's dict-like
                    client_id = c['client_id'].lower() if 'client_id' in c else ''
                if search_term in client_id:
                    filtered_search.append(c)
            filtered = filtered_search
        
        # Apply status filter
        if self._current_filter != "all":
            filtered_status = []
            for c in filtered:
                status = ""
                if hasattr(c, 'status'):
                    status = c.status.lower()
                elif hasattr(c, '__getitem__'):  # Check if it's dict-like
                    status = c['status'].lower() if 'status' in c else ''
                if status == self._current_filter.lower():
                    filtered_status.append(c)
            filtered = filtered_status
        
        self.filtered_clients = filtered
        
        # Notify parent of filter change
        if self.on_filter_changed:
            self.on_filter_changed(self.filtered_clients)
    
    def _on_search_change(self, e):
        """Handle search field changes with debouncing (fixed implementation)"""
        # Cancel existing timer if running
        if self._search_timer and not self._search_timer.done():
            self._search_timer.cancel()
        
        # Start new debounced search timer
        self._search_timer = asyncio.create_task(self._debounced_search(e.control.value))
    
    async def _debounced_search(self, query: str):
        """Execute search after debounce delay (fixed implementation)"""
        try:
            # Wait for debounce delay (300ms)
            await asyncio.sleep(0.3)
            
            # Apply filters on main thread
            if self.page:
                self.page.run_in_thread(self._apply_filters)
        except asyncio.CancelledError:
            # Timer was cancelled, ignore
            pass
        except Exception as e:
            print(f"Error in debounced search: {e}")
    
    def _on_chip_select(self, filter_value: str, e):
        """Handle status chip selection"""
        # Update current filter
        self._current_filter = filter_value
        
        # Update chip selection states
        if self.status_chips:
            for chip in self.status_chips.controls:
                if isinstance(chip, ft.Chip):
                    chip.selected = False
        
        # Set selected chip
        if e and e.control:
            e.control.selected = True
        
        # Apply filters and update UI
        self._apply_filters()
        
        # Show toast notification for user feedback
        if self.toast_manager:
            self.toast_manager.show_success(f"Filtered by: {filter_value.title()}")
    
    def reset_filters(self) -> None:
        """Reset all filters to default state"""
        # Reset search field
        if self.search_field:
            self.search_field.value = ""
        
        # Reset filter chips
        self._current_filter = "all"
        if self.status_chips:
            for i, chip in enumerate(self.status_chips.controls):
                if isinstance(chip, ft.Chip):
                    chip.selected = (i == 0)  # Select "All" chip
        
        # Apply filters
        self._apply_filters()
    
    def get_filter_stats(self) -> Dict[str, int]:
        """Get statistics about current filtering"""
        return {
            'total_clients': len(self.all_clients),
            'filtered_clients': len(self.filtered_clients),
            'current_filter': self._current_filter,
            'search_active': bool(self.search_field and self.search_field.value)
        }