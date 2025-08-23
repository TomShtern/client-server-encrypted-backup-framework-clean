#!/usr/bin/env python3
"""
Navigation Component for Flet Server GUI
Material Design 3 navigation rail implementation.
"""

import flet as ft
from typing import Callable


class NavigationManager:
    """Manages navigation between different views"""
    
    def __init__(self, page: ft.Page, switch_callback: Callable[[str], None]):
        self.page = page
        self.switch_callback = switch_callback
        self.current_index = 0
        
        self.nav_items = [
            {"icon": ft.Icons.DASHBOARD_OUTLINED, "selected_icon": ft.Icons.DASHBOARD, "label": "Dashboard", "view": "dashboard"},
            {"icon": ft.Icons.PEOPLE_OUTLINE, "selected_icon": ft.Icons.PEOPLE, "label": "Clients", "view": "clients"},
            {"icon": ft.Icons.FOLDER_OUTLINED, "selected_icon": ft.Icons.FOLDER, "label": "Files", "view": "files"},
            {"icon": ft.Icons.STORAGE_OUTLINED, "selected_icon": ft.Icons.STORAGE, "label": "Database", "view": "database"},
            {"icon": ft.Icons.AUTO_GRAPH_OUTLINED, "selected_icon": ft.Icons.AUTO_GRAPH, "label": "Analytics", "view": "analytics"},
            {"icon": ft.Icons.ARTICLE_OUTLINED, "selected_icon": ft.Icons.ARTICLE, "label": "Logs", "view": "logs"},
            {"icon": ft.Icons.SETTINGS_OUTLINED, "selected_icon": ft.Icons.SETTINGS, "label": "Settings", "view": "settings"}
        ]
        
        self.nav_rail: ft.NavigationRail | None = None
    
    def build(self) -> ft.NavigationRail:
        """Build the Material Design 3 navigation rail with animations."""
        destinations = []
        for item in self.nav_items:
            destination = ft.NavigationRailDestination(
                icon=item["icon"],
                selected_icon=item["selected_icon"],
                label=item["label"]
            )
            # Add hover effect to each destination
            destination.animate_scale = ft.Animation(100, ft.AnimationCurve.EASE_OUT)
            destinations.append(destination)
        
        self.nav_rail = ft.NavigationRail(
            selected_index=self.current_index,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=destinations,
            on_change=self.on_navigation_change,
            # Let the theme determine the background and indicator colors
            animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )
        return self.nav_rail
    
    def on_navigation_change(self, e):
        """Handle navigation change with animation."""
        self.current_index = e.control.selected_index
        view_name = self.nav_items[self.current_index]["view"]
        
        # Add subtle animation to navigation change
        if self.nav_rail:
            # Animate the selection change
            self.nav_rail.opacity = 1
            self.nav_rail.animate_opacity = ft.Animation(150, ft.AnimationCurve.EASE_OUT)
            self.page.update()
            
        self.switch_callback(view_name)
