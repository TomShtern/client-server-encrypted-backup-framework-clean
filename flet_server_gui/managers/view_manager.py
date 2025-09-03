#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ViewManager - Extracted from main.py God Component
Handles view switching, lifecycle management, and view state coordination.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Import utf8_solution for proper encoding handling
safe_print = print  # Default fallback
try:
    from Shared.utils.utf8_solution import safe_print
except ImportError:
    pass

import flet as ft
from typing import Dict, Optional, Any, Callable
from datetime import datetime


class ViewManager:
    """
    Manages view switching, lifecycle, and state coordination.
    
    Extracted from main.py (lines 619-676) to follow Single Responsibility Principle.
    This class is responsible ONLY for view management - no UI building, no monitoring.
    """
    
    def __init__(self, page: ft.Page, content_area: ft.AnimatedSwitcher):
        self.page = page
        self.content_area = content_area
        self.current_view = "dashboard"
        self.active_view_instance = None
        
        # View registry - populated by main app
        self.view_registry: Dict[str, Any] = {}
        
        # Navigation state reference (set later)
        self.navigation_state = None
        
        # View lifecycle callbacks
        self.view_change_callbacks: list[Callable] = []
    
    def register_view(self, view_name: str, view_instance: Any) -> None:
        """
        Register a view instance for management.
        
        Args:
            view_name: Name identifier for the view
            view_instance: The view instance to register
        """
        self.view_registry[view_name] = view_instance
        
        # Set initial active view if this is the dashboard
        if view_name == "dashboard":
            self.active_view_instance = view_instance
    
    def set_navigation_state(self, navigation_state: Any) -> None:
        """Set the navigation state for synchronization."""
        self.navigation_state = navigation_state
    
    def add_view_change_callback(self, callback: Callable[[str], None]) -> None:
        """Add callback to be called when view changes."""
        self.view_change_callbacks.append(callback)
    
    def get_current_view(self) -> str:
        """Get the current active view name."""
        return self.current_view
    
    def get_active_view_instance(self) -> Optional[Any]:
        """Get the current active view instance."""
        return self.active_view_instance
    
    def switch_view(self, view_name: str) -> bool:
        """
        Switch to a different view by showing the pre-instantiated control.
        
        Args:
            view_name: Name of the view to switch to
            
        Returns:
            bool: True if switch was successful, False otherwise
        """
        if self.current_view == view_name:
            return True

        # Call lifecycle method on the old view if it exists
        self._call_view_lifecycle_method(self.active_view_instance, 'on_hide')

        # Store previous view for potential rollback
        previous_view = self.current_view
        previous_instance = self.active_view_instance
        
        # Update current view state
        self.current_view = view_name
        
        # Get the new view instance from registry
        new_view_instance = self.view_registry.get(view_name)
        
        if new_view_instance:
            try:
                # Build the view content
                new_content = self._build_view_content(view_name, new_view_instance)
                
                if new_content:
                    # Update the animated switcher content
                    self.content_area.content = new_content
                    self.active_view_instance = new_view_instance
                    
                    # Call lifecycle method on the new view
                    self._call_view_lifecycle_method(new_view_instance, 'on_show')
                    
                    # Update navigation state
                    if self.navigation_state:
                        self.navigation_state.update_current_view(view_name)
                    
                    # Notify callbacks
                    for callback in self.view_change_callbacks:
                        try:
                            callback(view_name)
                        except Exception as e:
                            safe_print(f"[WARNING] View change callback error: {e}")
                    
                    # Update the page
                    self.page.update()
                    return True
                else:
                    # Failed to build content - rollback
                    self._rollback_view_switch(previous_view, previous_instance)
                    return False
                    
            except Exception as e:
                safe_print(f"[ERROR] Failed to build view '{view_name}': {e}")
                self._rollback_view_switch(previous_view, previous_instance)
                return False
        else:
            # Unknown view - rollback and show error
            self._rollback_view_switch(previous_view, previous_instance)
            self._show_view_error(f"Error: View '{view_name}' not found.")
            return False
    
    def _build_view_content(self, view_name: str, view_instance: Any) -> Optional[ft.Control]:
        """
        Build content for a specific view instance.
        
        Args:
            view_name: Name of the view
            view_instance: View instance to build content from
            
        Returns:
            ft.Control: Built content or None if failed
        """
        try:
            # Different views have different content building methods
            if view_name == "settings" and hasattr(view_instance, 'create_settings_view'):
                return view_instance.create_settings_view()
            elif view_name == "logs" and hasattr(view_instance, 'create_logs_view'):
                return view_instance.create_logs_view()
            elif hasattr(view_instance, 'build'):
                return view_instance.build()
            else:
                # View instance itself is the content
                return view_instance
                
        except Exception as e:
            safe_print(f"[ERROR] Failed to build content for view '{view_name}': {e}")
            return None
    
    def _call_view_lifecycle_method(self, view_instance: Any, method_name: str) -> None:
        """
        Safely call a lifecycle method on a view instance.
        
        Args:
            view_instance: View instance to call method on
            method_name: Name of the lifecycle method
        """
        if view_instance and hasattr(view_instance, method_name):
            try:
                method = getattr(view_instance, method_name)
                method()
            except Exception as e:
                safe_print(f"[WARNING] Error calling {method_name} on view: {e}")
    
    def _rollback_view_switch(self, previous_view: str, previous_instance: Any) -> None:
        """
        Rollback to previous view on switch failure.
        
        Args:
            previous_view: Previous view name
            previous_instance: Previous view instance
        """
        self.current_view = previous_view
        self.active_view_instance = previous_instance
    
    def _show_view_error(self, error_message: str) -> None:
        """
        Show error message in content area.
        
        Args:
            error_message: Error message to display
        """
        error_content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.ERROR),
                ft.Text(error_message, style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text("Please try again or contact support.", style=ft.TextThemeStyle.BODY_MEDIUM),
                ft.ElevatedButton(
                    "Back to Dashboard", 
                    on_click=lambda _: self.switch_view("dashboard"),
                    icon=ft.Icons.DASHBOARD
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16),
            padding=ft.padding.all(40),
            alignment=ft.alignment.center
        )
        self.content_area.content = error_content
        self.page.update()
    
    def refresh_current_view(self) -> None:
        """Refresh the current view by rebuilding its content."""
        if self.active_view_instance:
            try:
                new_content = self._build_view_content(self.current_view, self.active_view_instance)
                if new_content:
                    self.content_area.content = new_content
                    self.page.update()
            except Exception as e:
                safe_print(f"[ERROR] Failed to refresh view '{self.current_view}': {e}")
    
    def dispose(self) -> None:
        """Clean up view manager resources."""
        # Call dispose on all registered views
        for view_name, view_instance in self.view_registry.items():
            self._call_view_lifecycle_method(view_instance, 'dispose')
        
        # Clear registries
        self.view_registry.clear()
        self.view_change_callbacks.clear()
        
        # Clear references
        self.active_view_instance = None
        self.navigation_state = None