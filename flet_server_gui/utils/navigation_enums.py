#!/usr/bin/env python3
"""
Navigation constants and enums for Flet server GUI.
Purpose: Simple navigation definitions without framework fighting.
"""

import flet as ft
from enum import Enum
from typing import Dict, Any, List

class NavigationView(Enum):
    """Enumeration of available navigation views."""
    DASHBOARD = "dashboard"
    CLIENTS = "clients"
    FILES = "files"
    DATABASE = "database"
    ANALYTICS = "analytics"
    LOGS = "logs"
    SETTINGS = "settings"

# Navigation configuration - icons and labels for NavigationRail
NAVIGATION_ITEMS = [
    {
        "icon": ft.Icons.DASHBOARD_OUTLINED, 
        "selected_icon": ft.Icons.DASHBOARD, 
        "label": "Dashboard", 
        "view": NavigationView.DASHBOARD.value,
        "description": "System overview and status"
    },
    {
        "icon": ft.Icons.PEOPLE_OUTLINE, 
        "selected_icon": ft.Icons.PEOPLE, 
        "label": "Clients", 
        "view": NavigationView.CLIENTS.value,
        "description": "Client management and monitoring"
    },
    {
        "icon": ft.Icons.FOLDER_OUTLINED, 
        "selected_icon": ft.Icons.FOLDER, 
        "label": "Files", 
        "view": NavigationView.FILES.value,
        "description": "File browser and management"
    },
    {
        "icon": ft.Icons.STORAGE_OUTLINED, 
        "selected_icon": ft.Icons.STORAGE, 
        "label": "Database", 
        "view": NavigationView.DATABASE.value,
        "description": "Database operations and queries"
    },
    {
        "icon": ft.Icons.AUTO_GRAPH_OUTLINED, 
        "selected_icon": ft.Icons.AUTO_GRAPH, 
        "label": "Analytics", 
        "view": NavigationView.ANALYTICS.value,
        "description": "Performance metrics and charts"
    },
    {
        "icon": ft.Icons.ARTICLE_OUTLINED, 
        "selected_icon": ft.Icons.ARTICLE, 
        "label": "Logs", 
        "view": NavigationView.LOGS.value,
        "description": "System logs and monitoring"
    },
    {
        "icon": ft.Icons.SETTINGS_OUTLINED, 
        "selected_icon": ft.Icons.SETTINGS, 
        "label": "Settings", 
        "view": NavigationView.SETTINGS.value,
        "description": "Application configuration"
    }
]

def get_navigation_destinations() -> List[ft.NavigationRailDestination]:
    """Create NavigationRail destinations from configuration."""
    destinations = []
    
    for item in NAVIGATION_ITEMS:
        destination = ft.NavigationRailDestination(
            icon=item["icon"],
            selected_icon=item["selected_icon"],
            label=item["label"]
        )
        destination.tooltip = f"{item['label']}: {item['description']}"
        destinations.append(destination)
    
    return destinations

def get_view_by_index(index: int) -> str:
    """Get view name by navigation index."""
    if 0 <= index < len(NAVIGATION_ITEMS):
        return NAVIGATION_ITEMS[index]["view"]
    return NavigationView.DASHBOARD.value

def get_index_by_view(view_name: str) -> int:
    """Get navigation index by view name."""
    for i, item in enumerate(NAVIGATION_ITEMS):
        if item["view"] == view_name:
            return i
    return 0  # Default to dashboard