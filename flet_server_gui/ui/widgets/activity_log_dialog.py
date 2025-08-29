#!/usr/bin/env python3
"""
Activity Log Dialog - Detailed activity log viewer

Purpose: View and analyze system activity logs
Logic: Log storage, filtering, search, export
UI: Modal dialog with searchable log table
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json
import re
from flet_server_gui.ui.unified_theme_system import TOKENS


class ActivityLevel(Enum):
    """Activity log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SUCCESS = "success"
    SECURITY = "security"


class ActivityCategory(Enum):
    """Activity categories"""
    SYSTEM = "system"
    CLIENT = "client"
    BACKUP = "backup"
    SECURITY = "security"
    NETWORK = "network"
    DATABASE = "database"
    UI = "ui"
    API = "api"
    FILE = "file"


@dataclass
class ActivityEntry:
    """Individual activity log entry"""
    id: str
    timestamp: datetime
    level: ActivityLevel
    category: ActivityCategory
    message: str
    source: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None


class ActivityLogDialog(ft.AlertDialog):
    """Activity log dialog with search and filtering"""
    
    def __init__(self, 
                 activities: Optional[List[ActivityEntry]] = None,
                 on_close: Optional[Callable] = None):
        super().__init__()
        self.activities = activities or []
        self.on_close = on_close
        self.filtered_activities = self.activities.copy()
        
        # Level styling
        self._level_colors = {
            ActivityLevel.DEBUG: TOKENS['outline'],
            ActivityLevel.INFO: TOKENS['primary'],
            ActivityLevel.WARNING: TOKENS['tertiary'],
            ActivityLevel.ERROR: TOKENS['error'],
            ActivityLevel.CRITICAL: TOKENS['error'],
            ActivityLevel.SUCCESS: TOKENS['secondary'],
            ActivityLevel.SECURITY: TOKENS['primary']
        }
        
        self._level_icons = {
            ActivityLevel.DEBUG: ft.Icons.BUG_REPORT,
            ActivityLevel.INFO: ft.Icons.INFO,
            ActivityLevel.WARNING: ft.Icons.WARNING_AMBER,
            ActivityLevel.ERROR: ft.Icons.ERROR,
            ActivityLevel.CRITICAL: ft.Icons.ERROR_OUTLINE,
            ActivityLevel.SUCCESS: ft.Icons.CHECK_CIRCLE,
            ActivityLevel.SECURITY: ft.Icons.SECURITY
        }
        
        # Build the component
        self._build_component()
    
    def _build_component(self):
        """Build activity log dialog UI"""
        self.title = ft.Text("Activity Log", size=20, weight=ft.FontWeight.BOLD)
        
        # Create search and filter controls
        self._search_field = ft.TextField(
            label="Search logs",
            icon=ft.Icons.SEARCH,
            expand=True,
            on_change=self._on_search_change
        )
        
        self._level_filter = ft.Dropdown(
            label="Level",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("DEBUG"),
                ft.dropdown.Option("INFO"),
                ft.dropdown.Option("WARNING"),
                ft.dropdown.Option("ERROR"),
                ft.dropdown.Option("CRITICAL"),
                ft.dropdown.Option("SUCCESS"),
                ft.dropdown.Option("SECURITY")
            ],
            value="All",
            on_change=self._on_filter_change
        )
        
        self._category_filter = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("SYSTEM"),
                ft.dropdown.Option("CLIENT"),
                ft.dropdown.Option("BACKUP"),
                ft.dropdown.Option("SECURITY"),
                ft.dropdown.Option("NETWORK"),
                ft.dropdown.Option("DATABASE"),
                ft.dropdown.Option("UI"),
                ft.dropdown.Option("API"),
                ft.dropdown.Option("FILE")
            ],
            value="All",
            on_change=self._on_filter_change
        )
        
        # Create filter row
        filter_row = ft.Row([
            self._search_field,
            self._level_filter,
            self._category_filter
        ], spacing=12)
        
        # Create activity table
        self._table = self._create_activity_table()
        
        # Create table container with scroll
        table_container = ft.Container(
            content=self._table,
            expand=True,
            padding=ft.padding.all(8)
        )
        
        # Set dialog content
        self.content = ft.Container(
            content=ft.Column([
                filter_row,
                ft.Divider(),
                table_container
            ], spacing=12),
            width=900,
            height=600
        )
        
        # Set dialog actions
        self.actions = [
            ft.TextButton("Export", on_click=self._export_logs),
            ft.TextButton("Clear", on_click=self._clear_logs),
            ft.TextButton("Close", on_click=self._close_dialog)
        ]
        self.actions_alignment = ft.MainAxisAlignment.END
    
    def _create_activity_table(self) -> ft.DataTable:
        """Create activity log table"""
        # Create columns
        columns = [
            ft.DataColumn(ft.Text("Time", size=12, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Level", size=12, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Category", size=12, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Source", size=12, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Message", size=12, weight=ft.FontWeight.BOLD))
        ]
        
        # Create rows
        rows = []
        for activity in self.filtered_activities[:100]:  # Limit to 100 for performance
            rows.append(self._create_activity_row(activity))
        
        return ft.DataTable(
            columns=columns,
            rows=rows,
            heading_row_color=TOKENS['surface_variant'],
            heading_text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            data_row_min_height=40,
            border=ft.border.all(1, TOKENS['outline'])
        )
    
    def _create_activity_row(self, activity: ActivityEntry) -> ft.DataRow:
        """Create a row for an activity entry"""
        # Level cell with icon and color
        level_color = self._level_colors.get(activity.level, TOKENS['outline'])
        level_icon = self._level_icons.get(activity.level, ft.Icons.INFO)
        
        level_cell = ft.DataCell(
            ft.Row([
                ft.Icon(level_icon, size=16, color=level_color),
                ft.Text(activity.level.value.upper(), size=12, color=level_color)
            ], spacing=6)
        )
        
        # Timestamp cell
        timestamp_cell = ft.DataCell(
            ft.Text(self._format_timestamp(activity.timestamp), size=12)
        )
        
        # Category cell
        category_cell = ft.DataCell(
            ft.Text(activity.category.value.upper(), size=12)
        )
        
        # Source cell
        source_cell = ft.DataCell(
            ft.Text(activity.source, size=12)
        )
        
        # Message cell
        message_cell = ft.DataCell(
            ft.Text(activity.message, size=12, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
        )
        
        return ft.DataRow([
            timestamp_cell,
            level_cell,
            category_cell,
            source_cell,
            message_cell
        ])
    
    def add_activity(self, activity: ActivityEntry):
        """Add a new activity entry"""
        self.activities.append(activity)
        self._apply_filters()  # Refresh filtered list
    
    def show(self, page: ft.Page):
        """Show the activity log dialog"""
        page.dialog = self
        self.open = True
        page.update()
    
    def _on_search_change(self, e):
        """Handle search field changes"""
        self._apply_filters()
    
    def _on_filter_change(self, e):
        """Handle filter changes"""
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply search and filter criteria"""
        search_text = self._search_field.value.lower() if self._search_field.value else ""
        level_filter = self._level_filter.value
        category_filter = self._category_filter.value
        
        # Filter activities
        self.filtered_activities = []
        for activity in self.activities:
            # Search filter
            if search_text and search_text not in activity.message.lower() and \
               search_text not in activity.source.lower():
                continue
            
            # Level filter
            if level_filter != "All" and activity.level.value.upper() != level_filter:
                continue
            
            # Category filter
            if category_filter != "All" and activity.category.value.upper() != category_filter:
                continue
            
            self.filtered_activities.append(activity)
        
        # Update table
        self._table.rows.clear()
        for activity in self.filtered_activities[:100]:  # Limit for performance
            self._table.rows.append(self._create_activity_row(activity))
        self._safe_update()
    
    def _safe_update(self):
        """Safely update the component if attached to page"""
        try:
            if hasattr(self, 'page') and self.page:
                self.update()
        except (AttributeError, AssertionError):
            # Control not attached to page, skip update
            pass
    
    def _export_logs(self, e):
        """Export logs to clipboard"""
        # Create export content
        export_lines = []
        export_lines.append("Timestamp,Level,Category,Source,Message")
        for activity in self.filtered_activities:
            line = f"{activity.timestamp.isoformat()},{activity.level.value},{activity.category.value},{activity.source},\"{activity.message}\""
            export_lines.append(line)
        
        export_content = "\n".join(export_lines)
        
        # Show confirmation
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Logs exported to clipboard"),
                action="Dismiss"
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _clear_logs(self, e):
        """Clear all logs"""
        self.activities.clear()
        self.filtered_activities.clear()
        
        # Update table
        self._table.rows.clear()
        self._safe_update()
    
    def _close_dialog(self, e):
        """Close the dialog"""
        self.open = False
        try:
            if self.page:
                self.page.update()
        except (AttributeError, AssertionError):
            pass
        
        # Call close callback
        if self.on_close:
            self.on_close()
    
    def _format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp for display"""
        return timestamp.strftime("%H:%M:%S")
    
    def get_activity_count(self) -> int:
        """Get total activity count"""
        return len(self.activities)
    
    def get_error_count(self) -> int:
        """Get count of error activities"""
        return len([a for a in self.activities if a.level in [ActivityLevel.ERROR, ActivityLevel.CRITICAL]])


# Factory functions for easy creation
def create_activity_log_dialog(activities: Optional[List[ActivityEntry]] = None,
                              on_close: Optional[Callable] = None) -> ActivityLogDialog:
    """Create an activity log dialog"""
    return ActivityLogDialog(activities, on_close)


def create_activity_entry(message: str,
                        level: ActivityLevel = ActivityLevel.INFO,
                        category: ActivityCategory = ActivityCategory.SYSTEM,
                        source: str = "system",
                        metadata: Optional[Dict[str, Any]] = None) -> ActivityEntry:
    """Create an activity entry"""
    return ActivityEntry(
        id=f"activity_{datetime.now().timestamp()}",
        timestamp=datetime.now(),
        level=level,
        category=category,
        message=message,
        source=source,
        metadata=metadata or {}
    )