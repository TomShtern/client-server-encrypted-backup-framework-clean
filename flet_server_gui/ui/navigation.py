#!/usr/bin/env python3
"""
Purpose: App navigation and routing system
Logic: Navigation state management, view switching
UI: Navigation rail, routing controls
"""

import flet as ft
from typing import Callable, Dict, Any, Optional, List
from enum import Enum
from flet_server_gui.ui.theme_m3 import TOKENS

# ============================================================================
# NAVIGATION DEFINITIONS
# ============================================================================

class NavigationView(Enum):
    """Enumeration of available navigation views."""
    DASHBOARD = "dashboard"
    CLIENTS = "clients"
    FILES = "files"
    DATABASE = "database"
    ANALYTICS = "analytics"
    LOGS = "logs"
    SETTINGS = "settings"

class NavigationManager:
    """Manages navigation between different views with enhanced routing capabilities."""
    
    def __init__(self, page: ft.Page, switch_callback: Callable[[str], None], content_area=None):
        self.page = page
        self.switch_callback = switch_callback
        self.content_area = content_area
        self.current_index = 0
        self.current_view = NavigationView.DASHBOARD
        
        # Enhanced navigation configuration with breadcrumbs and permissions
        self.nav_items = [
            {
                "icon": ft.Icons.DASHBOARD_OUTLINED, 
                "selected_icon": ft.Icons.DASHBOARD, 
                "label": "Dashboard", 
                "view": NavigationView.DASHBOARD.value,
                "description": "System overview and status",
                "requires_permission": None,
                "badge_count": 0
            },
            {
                "icon": ft.Icons.PEOPLE_OUTLINE, 
                "selected_icon": ft.Icons.PEOPLE, 
                "label": "Clients", 
                "view": NavigationView.CLIENTS.value,
                "description": "Client management and monitoring",
                "requires_permission": None,
                "badge_count": 0
            },
            {
                "icon": ft.Icons.FOLDER_OUTLINED, 
                "selected_icon": ft.Icons.FOLDER, 
                "label": "Files", 
                "view": NavigationView.FILES.value,
                "description": "File browser and management",
                "requires_permission": None,
                "badge_count": 0
            },
            {
                "icon": ft.Icons.STORAGE_OUTLINED, 
                "selected_icon": ft.Icons.STORAGE, 
                "label": "Database", 
                "view": NavigationView.DATABASE.value,
                "description": "Database operations and queries",
                "requires_permission": None,
                "badge_count": 0
            },
            {
                "icon": ft.Icons.AUTO_GRAPH_OUTLINED, 
                "selected_icon": ft.Icons.AUTO_GRAPH, 
                "label": "Analytics", 
                "view": NavigationView.ANALYTICS.value,
                "description": "Performance metrics and charts",
                "requires_permission": None,
                "badge_count": 0
            },
            {
                "icon": ft.Icons.ARTICLE_OUTLINED, 
                "selected_icon": ft.Icons.ARTICLE, 
                "label": "Logs", 
                "view": NavigationView.LOGS.value,
                "description": "System logs and monitoring",
                "requires_permission": None,
                "badge_count": 0
            },
            {
                "icon": ft.Icons.SETTINGS_OUTLINED, 
                "selected_icon": ft.Icons.SETTINGS, 
                "label": "Settings", 
                "view": NavigationView.SETTINGS.value,
                "description": "Application configuration",
                "requires_permission": None,
                "badge_count": 0
            }
        ]
        
        # Navigation state
        self.nav_rail: Optional[ft.NavigationRail] = None
        self.navigation_history: List[str] = [NavigationView.DASHBOARD.value]
        self.forward_history: List[str] = []
        self.navigation_callbacks: Dict[str, List[Callable]] = {}
    
    def build(self, extended: bool = False, show_labels: bool = True) -> ft.NavigationRail:
        """Build the Material Design 3 navigation rail with enhanced features."""
        destinations = []
        
        for i, item in enumerate(self.nav_items):
            # Create destination with optional badge using Row instead of Stack for better hitbox
            icon_content = None
            selected_icon_content = None
            
            if item.get("badge_count", 0) > 0:
                # Use Row for better clickable area instead of Stack
                badge = ft.Container(
                    content=ft.Text(str(item["badge_count"]), size=10, color=TOKENS['on_error']),
                    bgcolor=TOKENS['error'],
                    border_radius=8,
                    alignment=ft.alignment.center
                )
                
                icon_content = ft.Row([
                    ft.Icon(item["icon"]),
                    badge
                ], spacing=4, alignment=ft.MainAxisAlignment.CENTER)
                
                selected_icon_content = ft.Row([
                    ft.Icon(item["selected_icon"]),
                    badge
                ], spacing=4, alignment=ft.MainAxisAlignment.CENTER)
            else:
                # Simple icons without badges
                icon_content = item["icon"]
                selected_icon_content = item["selected_icon"]
            
            destination = ft.NavigationRailDestination(
                icon=icon_content,
                selected_icon=selected_icon_content,
                label=item["label"]
            )
            
            # Enhanced hover effects and animations
            destination.tooltip = f"{item['label']}: {item['description']}"
            destinations.append(destination)
        
        self.nav_rail = ft.NavigationRail(
            selected_index=self.current_index,
            label_type=ft.NavigationRailLabelType.ALL if show_labels else ft.NavigationRailLabelType.SELECTED,
            min_width=72,
            min_extended_width=256,
            extended=extended,
            destinations=destinations,
            on_change=self.on_navigation_change,
            # Enhanced styling - use theme colors instead of hardcoded
            bgcolor=None,  # Let Material Design 3 theme control the background
            leading=self._create_navigation_header() if extended else None,
            trailing=self._create_navigation_footer() if extended else None,
            # Enhanced animations for better user experience
            animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            animate_rotation=ft.Animation(300, ft.AnimationCurve.DECELERATE)
        )
        
        return self.nav_rail
    
    def _create_navigation_header(self) -> ft.Control:
        """Create header for extended navigation rail."""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CLOUD_SYNC, size=32, color=TOKENS['primary']),
                ft.Text("Backup Server", size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            padding=ft.Padding(16, 16, 16, 8)
        )
    
    def _create_navigation_footer(self) -> ft.Control:
        """Create footer for extended navigation rail."""
        return ft.Container(
            content=ft.Column([
                ft.IconButton(
                    icon=ft.Icons.HELP_OUTLINE,
                    tooltip="Help & Support",
                    on_click=lambda e: self._show_help_dialog()
                ),
                ft.IconButton(
                    icon=ft.Icons.INFO_OUTLINE,
                    tooltip="About",
                    on_click=lambda e: self._show_about_dialog()
                )
            ], spacing=4),
            padding=ft.Padding(16, 8, 16, 16)
        )
    
    def on_navigation_change(self, e):
        """Handle navigation change with enhanced state management."""
        new_index = e.control.selected_index
        
        # Prevent unnecessary navigation to the same view
        if new_index == self.current_index:
            return
        
        old_view = self.nav_items[self.current_index]["view"]
        new_view = self.nav_items[new_index]["view"]
        
        # Check permissions (if implemented)
        if not self._check_view_permission(new_view):
            self._show_permission_denied_dialog(new_view)
            # Reset selection
            e.control.selected_index = self.current_index
            self.page.update()
            return
        
        # Update state
        self.current_index = new_index
        self.current_view = NavigationView(new_view)
        
        # Update navigation history
        self._update_navigation_history(new_view)
        
        # Ensure content is not None
        if self.content_area.content is None:
            self.content_area.content = ft.Container(
                content=ft.Text("View content not available", 
                               style=ft.TextThemeStyle.BODY_MEDIUM,
                               text_align=ft.TextAlign.CENTER),
                padding=20,
                alignment=ft.alignment.center
            )
        
        # Apply smooth navigation animation with scale effect
        if self.nav_rail:
            # Scale animation for visual feedback
            self.nav_rail.scale = 0.98
            self.nav_rail.animate_scale = ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT)
            self.page.update()
            
            # Reset scale after animation
            self.nav_rail.scale = 1.0
            self.page.update()
        
        # Trigger callbacks
        self._trigger_navigation_callbacks(old_view, new_view)
        
        # Execute main switch callback
        self.switch_callback(new_view)
    
    def sync_navigation_state(self, current_view_name: str):
        """Sync navigation rail selection with current view."""
        # Find the view index
        for i, item in enumerate(self.nav_items):
            if item["view"] == current_view_name:
                self.current_index = i
                self.current_view = NavigationView(current_view_name)
                if self.nav_rail:
                    self.nav_rail.selected_index = i
                break
    
    def navigate_to(self, view_name: str, add_to_history: bool = True) -> bool:
        """Programmatically navigate to a specific view."""
        try:
            # Find the view index
            view_index = None
            for i, item in enumerate(self.nav_items):
                if item["view"] == view_name:
                    view_index = i
                    break
            
            if view_index is None:
                print(f"[ERROR] Unknown view: {view_name}")
                return False
            
            # Check permissions
            if not self._check_view_permission(view_name):
                self._show_permission_denied_dialog(view_name)
                return False
            
            # Update navigation rail
            if self.nav_rail:
                self.nav_rail.selected_index = view_index
            
            # Update state
            old_view = self.current_view.value if self.current_view else None
            self.current_index = view_index
            self.current_view = NavigationView(view_name)
            
            # Update history
            if add_to_history:
                self._update_navigation_history(view_name)
            
            # Clear badge
            self._clear_view_badge(view_name)
            
            # Trigger callbacks
            if old_view:
                self._trigger_navigation_callbacks(old_view, view_name)
            
            # Execute main switch callback
            self.switch_callback(view_name)
            
            # Update UI
            self.page.update()
            return True
            
        except Exception as e:
            print(f"[ERROR] Navigation failed: {e}")
            return False
    
    def go_back(self) -> bool:
        """Navigate back to the previous view in history."""
        if len(self.navigation_history) < 2:
            return False
        
        # Move current view to forward history
        current = self.navigation_history.pop()
        self.forward_history.append(current)
        
        # Navigate to previous view
        previous = self.navigation_history[-1]
        return self.navigate_to(previous, add_to_history=False)
    
    def go_forward(self) -> bool:
        """Navigate forward in history."""
        if not self.forward_history:
            return False
        
        # Get next view from forward history
        next_view = self.forward_history.pop()
        return self.navigate_to(next_view, add_to_history=True)
    
    def can_go_back(self) -> bool:
        """Check if navigation can go back."""
        return len(self.navigation_history) > 1
    
    def can_go_forward(self) -> bool:
        """Check if navigation can go forward."""
        return len(self.forward_history) > 0
    
    def set_view_badge(self, view_name: str, count: int):
        """Set badge count for a specific view."""
        for item in self.nav_items:
            if item["view"] == view_name:
                item["badge_count"] = count
                if self.nav_rail:
                    # Rebuild navigation rail to show badge
                    self.page.update()
                break
    
    def _clear_view_badge(self, view_name: str):
        """Clear badge for a specific view."""
        self.set_view_badge(view_name, 0)
    
    def _update_navigation_history(self, new_view: str):
        """Update navigation history."""
        # Add to history if not the same as current
        if not self.navigation_history or self.navigation_history[-1] != new_view:
            self.navigation_history.append(new_view)
            # Clear forward history when navigating to new view
            self.forward_history.clear()
            
            # Limit history size
            if len(self.navigation_history) > 20:
                self.navigation_history = self.navigation_history[-20:]
    
    def _check_view_permission(self, view_name: str) -> bool:
        """Check if user has permission to access the view."""
        # Find the view configuration
        for item in self.nav_items:
            if item["view"] == view_name:
                required_permission = item.get("requires_permission")
                if required_permission:
                    # Implement permission checking logic here
                    # For now, return True (no restrictions)
                    return True
                return True
        return False
    
    def _show_permission_denied_dialog(self, view_name: str):
        """Show permission denied dialog."""
        # This would integrate with the dialog system
        print(f"[WARNING] Access denied to view: {view_name}")
    
    def _show_help_dialog(self):
        """Show help dialog."""
        # This would integrate with the dialog system
        print("[INFO] Help dialog requested")
    
    def _show_about_dialog(self):
        """Show about dialog."""
        # This would integrate with the dialog system
        print("[INFO] About dialog requested")
    
    def add_navigation_callback(self, view_name: str, callback: Callable[[str, str], None]):
        """Add callback for navigation events to/from a specific view."""
        if view_name not in self.navigation_callbacks:
            self.navigation_callbacks[view_name] = []
        self.navigation_callbacks[view_name].append(callback)
    
    def remove_navigation_callback(self, view_name: str, callback: Callable[[str, str], None]):
        """Remove navigation callback."""
        if view_name in self.navigation_callbacks:
            try:
                self.navigation_callbacks[view_name].remove(callback)
            except ValueError:
                pass
    
    def _trigger_navigation_callbacks(self, from_view: str, to_view: str):
        """Trigger navigation callbacks."""
        # Callbacks for leaving a view
        if from_view in self.navigation_callbacks:
            for callback in self.navigation_callbacks[from_view]:
                try:
                    callback(from_view, to_view)
                except Exception as e:
                    print(f"[ERROR] Navigation callback failed: {e}")
        
        # Callbacks for entering a view
        if to_view in self.navigation_callbacks:
            for callback in self.navigation_callbacks[to_view]:
                try:
                    callback(from_view, to_view)
                except Exception as e:
                    print(f"[ERROR] Navigation callback failed: {e}")
    
    def get_current_view(self) -> NavigationView:
        """Get the current active view."""
        return self.current_view
    
    def get_navigation_breadcrumb(self) -> List[Dict[str, str]]:
        """Get navigation breadcrumb for current location."""
        breadcrumb = []
        for view_name in self.navigation_history[-3:]:  # Show last 3 views
            for item in self.nav_items:
                if item["view"] == view_name:
                    breadcrumb.append({
                        "name": item["label"],
                        "view": view_name,
                        "icon": item["icon"]
                    })
                    break
        return breadcrumb

# ============================================================================
# ROUTING UTILITIES
# ============================================================================

class Router:
    """Simple routing system for handling navigation state."""
    
    def __init__(self, navigation_manager: NavigationManager):
        self.navigation_manager = navigation_manager
        self.routes: Dict[str, Dict[str, Any]] = {}
        self.current_route = None
    
    def register_route(self, path: str, view: str, **kwargs):
        """Register a route with optional parameters."""
        self.routes[path] = {
            "view": view,
            "params": kwargs
        }
    
    def navigate(self, path: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Navigate to a specific route."""
        if path in self.routes:
            route = self.routes[path]
            # Merge parameters
            if params:
                route["params"].update(params)
            
            # Navigate to the view
            success = self.navigation_manager.navigate_to(route["view"])
            if success:
                self.current_route = path
            return success
        return False
    
    def get_current_route(self) -> Optional[str]:
        """Get the current route path."""
        return self.current_route

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_navigation_manager(page: ft.Page, switch_callback: Callable[[str], None]) -> NavigationManager:
    """Create and configure a navigation manager."""
    return NavigationManager(page, switch_callback)

def create_router(navigation_manager: NavigationManager) -> Router:
    """Create a router for the navigation manager."""
    router = Router(navigation_manager)
    
    # Register default routes
    for item in navigation_manager.nav_items:
        route_path = f"/{item['view']}"
        router.register_route(route_path, item['view'])
    
    return router