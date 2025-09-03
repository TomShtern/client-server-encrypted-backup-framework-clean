#!/usr/bin/env python3
"""
Simple navigation utilities that work with Flet's built-in NavigationRail.
Purpose: Replace NavigationManager with simple functions that don't fight the framework.
"""

import flet as ft
from typing import Callable, List, Dict, Optional
try:
    from .navigation_enums import NavigationView, NAVIGATION_ITEMS, get_view_by_index, get_index_by_view
except ImportError:
    # Fallback for standalone import during testing
    from navigation_enums import NavigationView, NAVIGATION_ITEMS, get_view_by_index, get_index_by_view

class SimpleNavigationState:
    """Simple navigation state tracker - no framework fighting."""
    
    def __init__(self):
        self.current_view = NavigationView.DASHBOARD.value
        self.current_index = 0
        self.history: List[str] = [NavigationView.DASHBOARD.value]
        self.badge_counts: Dict[str, int] = {}
    
    def update_current_view(self, view_name: str):
        """Update current view and add to history."""
        if view_name != self.current_view:
            self.history.append(view_name)
            # Limit history size
            if len(self.history) > 10:
                self.history = self.history[-10:]
        
        self.current_view = view_name
        self.current_index = get_index_by_view(view_name)
    
    def set_current_view(self, view_name: str):
        """Set current view - alias for update_current_view for compatibility."""
        self.update_current_view(view_name)
    
    def get_current_view(self) -> str:
        """Get the current view name."""
        return self.current_view
    
    def can_go_back(self) -> bool:
        """Check if we can navigate back."""
        return len(self.history) > 1
    
    def go_back(self) -> Optional[str]:
        """Get previous view from history."""
        if self.can_go_back():
            self.history.pop()  # Remove current
            return self.history[-1]  # Return previous
        return None
    
    def set_badge(self, view_name: str, count: int):
        """Set badge count for a view."""
        self.badge_counts[view_name] = count
    
    def get_badge(self, view_name: str) -> int:
        """Get badge count for a view."""
        return self.badge_counts.get(view_name, 0)
    
    def clear_badge(self, view_name: str):
        """Clear badge for a view."""
        self.badge_counts.pop(view_name, None)

def create_simple_navigation_rail(
    nav_state: SimpleNavigationState,
    on_change_callback: Callable[[str], None],
    extended: bool = False
) -> ft.NavigationRail:
    """Create a simple NavigationRail using Flet's built-in functionality."""
    
    def handle_navigation_change(e):
        """Simple navigation change handler."""
        new_index = e.control.selected_index
        new_view = get_view_by_index(new_index)
        
        # Clear badge when navigating to view
        nav_state.clear_badge(new_view)
        nav_state.update_current_view(new_view)
        
        # Call the main callback
        on_change_callback(new_view)
    
    # Create destinations with badges if needed
    destinations = []
    for item in NAVIGATION_ITEMS:
        view_name = item["view"]
        badge_count = nav_state.get_badge(view_name)
        
        # Simple badge implementation
        if badge_count > 0:
            # Create badge as simple container
            badge = ft.Container(
                content=ft.Text(str(badge_count), size=10, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.ERROR,
                border_radius=8,
                padding=ft.Padding(4, 2, 4, 2),
                alignment=ft.alignment.center
            )
            
            # Use Stack to overlay badge on icon
            icon_with_badge = ft.Stack([
                ft.Icon(item["icon"]),
                ft.Positioned(badge, right=0, top=0)
            ])
            
            selected_icon_with_badge = ft.Stack([
                ft.Icon(item["selected_icon"]),
                ft.Positioned(badge, right=0, top=0)
            ])
            
            destination = ft.NavigationRailDestination(
                icon=icon_with_badge,
                selected_icon=selected_icon_with_badge,
                label=item["label"]
            )
        else:
            # Simple destination without badge
            destination = ft.NavigationRailDestination(
                icon=item["icon"],
                selected_icon=item["selected_icon"],
                label=item["label"]
            )
        
        destination.tooltip = f"{item['label']}: {item['description']}"
        destinations.append(destination)
    
    # Create NavigationRail with responsive sizing
    nav_rail = ft.NavigationRail(
        selected_index=nav_state.current_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=72,
        min_extended_width=200,
        extended=extended,
        destinations=destinations,
        on_change=handle_navigation_change,
        leading=_create_simple_header() if extended else None,
    )
    
    return nav_rail

def _create_simple_header() -> ft.Control:
    """Create simple header for extended navigation rail."""
    return ft.Column([
        ft.Icon(ft.Icons.CLOUD_SYNC, size=32, color=ft.Colors.PRIMARY),
        ft.Text("Backup Server", size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    ], 
    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
    spacing=4, 
    padding=ft.Padding(16, 16, 16, 8))

def navigate_programmatically(
    nav_rail: ft.NavigationRail,
    nav_state: SimpleNavigationState,
    view_name: str,
    callback: Callable[[str], None]
) -> bool:
    """Programmatically navigate to a view."""
    try:
        new_index = get_index_by_view(view_name)
        
        # Update NavigationRail
        nav_rail.selected_index = new_index
        nav_rail.update()
        
        # Update state
        nav_state.clear_badge(view_name)
        nav_state.update_current_view(view_name)
        
        # Call callback
        callback(view_name)
        return True
        
    except Exception as e:
        print(f"[ERROR] Navigation failed: {e}")
        return False

def sync_navigation_state(
    nav_rail: ft.NavigationRail,
    nav_state: SimpleNavigationState,
    current_view: str
):
    """Sync NavigationRail with current view state."""
    new_index = get_index_by_view(current_view)
    nav_rail.selected_index = new_index
    nav_state.update_current_view(current_view)
    nav_rail.update()