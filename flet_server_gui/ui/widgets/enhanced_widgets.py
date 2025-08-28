#!/usr/bin/env python3
"""
Enhanced Widget Components - Advanced widget system with animations and Material Design 3

Purpose: Provide consistent, animated widget components with proper styling
Logic: Widget creation, data handling, state management, and interaction
UI: Material Design 3 styled widgets with interactive features
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import logging
import random
from datetime import datetime, timedelta
from flet_server_gui.ui.theme_m3 import TOKENS

logger = logging.getLogger(__name__)


class WidgetType(Enum):
    """Widget types"""
    STAT = "stat"
    CHART = "chart"
    TABLE = "table"
    LIST = "list"
    PROGRESS = "progress"
    STATUS = "status"


class WidgetSize(Enum):
    """Widget sizes"""
    SMALL = "small"    # 1x1 grid cell
    MEDIUM = "medium"  # 2x1 grid cell
    LARGE = "large"    # 2x2 grid cell
    WIDE = "wide"      # 4x1 grid cell
    FULL = "full"      # Full width


@dataclass
class WidgetConfig:
    """Configuration for enhanced widgets"""
    title: str
    widget_type: WidgetType
    content: Any = None
    size: WidgetSize = WidgetSize.MEDIUM
    collapsible: bool = True
    refreshable: bool = False
    refresh_interval: int = 0  # seconds, 0 = no auto-refresh
    on_refresh: Optional[Callable] = None
    on_collapse: Optional[Callable] = None
    on_expand: Optional[Callable] = None
    on_click: Optional[Callable] = None
    expanded: bool = True
    show_header: bool = True
    show_footer: bool = True
    border_radius: int = 16
    elevation: int = 2
    animate: bool = True
    animation_duration: int = 300  # milliseconds


class EnhancedWidget:
    """
    Enhanced widget with Material Design 3 styling and animations
    """
    
    def __init__(self, page: ft.Page, config: WidgetConfig):
        self.page = page
        self.config = config
        self.widget_ref = ft.Ref[ft.Card]()
        self.content_ref = ft.Ref[ft.Control]()
        self.is_collapsed = not config.expanded
        self.refresh_task = None
        
        # Create the widget
        self.widget = self._create_widget()
        
        # Start auto-refresh if configured
        if self.config.refresh_interval > 0 and self.config.on_refresh:
            self._start_auto_refresh()
    
    def _create_widget(self) -> ft.Card:
        """Create the enhanced widget"""
        # Create header
        header = self._create_header() if self.config.show_header else None
        
        # Create content
        content = self._create_content()
        
        # Create footer
        footer = self._create_footer() if self.config.show_footer else None
        
        # Combine controls
        controls = []
        if header:
            controls.append(header)
        controls.append(content)
        if footer:
            controls.append(footer)
        
        # Create container for content
        content_container = ft.Container(
            ref=self.content_ref,
            content=ft.Column(controls, spacing=0, expand=True),
            padding=16,
            expand=True
        )
        
        # Create card
        card = ft.Card(
            ref=self.widget_ref,
            content=content_container,
            elevation=self.config.elevation
        )
        
        # Add click handler if specified
        if self.config.on_click:
            card.on_click = self.config.on_click
        
        return card
    
    def _create_header(self) -> ft.Control:
        """Create widget header"""
        # Title
        title = ft.Text(
            self.config.title,
            style=ft.TextThemeStyle.TITLE_MEDIUM,
            weight=ft.FontWeight.W_500,
            expand=True
        )
        
        # Action buttons
        actions = []
        
        # Refresh button
        if self.config.refreshable and self.config.on_refresh:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refresh",
                    on_click=self._on_refresh
                )
            )
        
        # Collapse/expand button
        if self.config.collapsible:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.EXPAND_LESS if not self.is_collapsed else ft.Icons.EXPAND_MORE,
                    tooltip="Collapse" if not self.is_collapsed else "Expand",
                    on_click=self._on_toggle_collapse
                )
            )
        
        # Create header row
        header_row = ft.Row(
            [title] + actions,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        return ft.Container(
            content=header_row,
            padding=ft.Padding(16, 16, 16, 8)
        )
    
    def _create_content(self) -> ft.Control:
        """Create widget content"""
        if self.is_collapsed:
            # Return empty container when collapsed
            return ft.Container()
        
        # Handle different content types
        if isinstance(self.config.content, ft.Control):
            return self.config.content
        elif isinstance(self.config.content, str):
            return ft.Text(self.config.content, style=ft.TextThemeStyle.BODY_MEDIUM)
        elif isinstance(self.config.content, list):
            return ft.Column(self.config.content, spacing=8)
        elif self.config.content is None:
            return ft.Text("No content", style=ft.TextThemeStyle.BODY_MEDIUM, color=TOKENS['outline'])
        else:
            return ft.Text(str(self.config.content), style=ft.TextThemeStyle.BODY_MEDIUM)
    
    def _create_footer(self) -> Optional[ft.Control]:
        """Create widget footer"""
        # For now, return None - can be extended later
        return None
    
    def _on_refresh(self, e):
        """Handle refresh action"""
        if self.config.on_refresh:
            self.config.on_refresh()
    
    def _on_toggle_collapse(self, e):
        """Handle collapse/expand toggle"""
        self.is_collapsed = not self.is_collapsed
        
        # Update content
        new_content = self._create_content()
        self.content_ref.current.content.controls = [
            control for control in self.content_ref.current.content.controls 
            if not isinstance(control, ft.Container) or control.content != self.content_ref.current.content.controls[-1].content
        ]
        self.content_ref.current.content.controls.append(new_content)
        
        # Update collapse/expand button icon
        # Find the icon button and update it
        if hasattr(self.widget.content, 'content') and hasattr(self.widget.content.content, 'controls'):
            for control in self.widget.content.content.controls:
                if isinstance(control, ft.Container) and hasattr(control, 'content'):
                    if isinstance(control.content, ft.Row):
                        for action in control.content.controls:
                            if isinstance(action, ft.IconButton):
                                action.icon = ft.Icons.EXPAND_LESS if not self.is_collapsed else ft.Icons.EXPAND_MORE
                                action.tooltip = "Collapse" if not self.is_collapsed else "Expand"
        
        # Call callbacks
        if self.is_collapsed and self.config.on_collapse:
            self.config.on_collapse()
        elif not self.is_collapsed and self.config.on_expand:
            self.config.on_expand()
        
        self.page.update()
    
    def _start_auto_refresh(self):
        """Start auto-refresh task"""
        async def refresh_loop():
            while True:
                await asyncio.sleep(self.config.refresh_interval)
                if self.config.on_refresh:
                    self.config.on_refresh()
        
        self.refresh_task = asyncio.create_task(refresh_loop())
    
    def update_content(self, content: Any):
        """Update widget content"""
        self.config.content = content
        
        if not self.is_collapsed:
            # Update content if not collapsed
            new_content = self._create_content()
            # Find content control and replace it
            if hasattr(self.content_ref.current.content, 'controls'):
                # Replace the last control (assuming it's the content)
                if len(self.content_ref.current.content.controls) > 0:
                    self.content_ref.current.content.controls[-1] = new_content
                else:
                    self.content_ref.current.content.controls.append(new_content)
                self.page.update()
    
    def set_title(self, title: str):
        """Update widget title"""
        self.config.title = title
        # Update header
        new_header = self._create_header()
        # Find header control and replace it
        if hasattr(self.content_ref.current.content, 'controls') and len(self.content_ref.current.content.controls) > 0:
            self.content_ref.current.content.controls[0] = new_header
            self.page.update()
    
    def get_control(self) -> ft.Control:
        """Get the Flet control"""
        return self.widget
    
    def dispose(self):
        """Clean up resources"""
        if self.refresh_task:
            self.refresh_task.cancel()


# Specialized widget types
class StatWidget(EnhancedWidget):
    """
    Specialized widget for displaying statistics
    """
    
    def __init__(
        self,
        page: ft.Page,
        title: str,
        value: Union[str, int, float],
        unit: Optional[str] = None,
        icon: Optional[str] = None,
        trend: Optional[str] = None,
        trend_color: Optional[str] = None,
        **kwargs
    ):
        # Format value
        if isinstance(value, (int, float)):
            formatted_value = f"{value:,}"
        else:
            formatted_value = str(value)
        
        # Create content
        content_controls = []
        
        # Icon and value row
        value_row_controls = []
        
        if icon:
            value_row_controls.append(ft.Icon(icon, size=24))
        
        value_text = ft.Text(
            formatted_value,
            style=ft.TextThemeStyle.HEADLINE_MEDIUM,
            weight=ft.FontWeight.W_300
        )
        value_row_controls.append(value_text)
        
        if unit:
            value_row_controls.append(
                ft.Text(
                    unit,
                    style=ft.TextThemeStyle.TITLE_MEDIUM,
                    color=TOKENS['outline']
                )
            )
        
        content_controls.append(
            ft.Row(
                value_row_controls,
                alignment=ft.MainAxisAlignment.START,
                spacing=8
            )
        )
        
        # Trend indicator
        if trend:
            trend_color = trend_color or TOKENS['on_background']
            content_controls.append(
                ft.Text(
                    trend,
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=trend_color
                )
            )
        
        config = WidgetConfig(
            title=title,
            widget_type=WidgetType.STAT,
            content=ft.Column(content_controls, spacing=8),
            size=WidgetSize.SMALL,
            **kwargs
        )
        
        super().__init__(page, config)


class ProgressWidget(EnhancedWidget):
    """
    Specialized widget for displaying progress
    """
    
    def __init__(
        self,
        page: ft.Page,
        title: str,
        progress: float,  # 0.0 to 1.0
        description: Optional[str] = None,
        show_percentage: bool = True,
        color: Optional[str] = None,
        **kwargs
    ):
        # Create content
        content_controls = []
        
        # Progress bar
        progress_bar = ft.ProgressBar(
            value=progress,
            color=color or TOKENS['primary'],
            bar_height=8,
            border_radius=4
        )
        content_controls.append(progress_bar)
        
        # Percentage and description
        bottom_controls = []
        
        if show_percentage:
            bottom_controls.append(
                ft.Text(
                    f"{int(progress * 100)}%",
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    weight=ft.FontWeight.W_500
                )
            )
        
        if description:
            bottom_controls.append(
                ft.Text(
                    description,
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=TOKENS['outline']
                )
            )
        
        if bottom_controls:
            content_controls.append(
                ft.Row(
                    bottom_controls,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
        
        config = WidgetConfig(
            title=title,
            widget_type=WidgetType.PROGRESS,
            content=ft.Column(content_controls, spacing=12),
            size=WidgetSize.SMALL,
            **kwargs
        )
        
        super().__init__(page, config)
        
        # Store reference to progress bar for updates
        self.progress_bar = progress_bar
    
    def update_progress(self, progress: float, description: Optional[str] = None):
        """Update progress value"""
        self.progress_bar.value = progress
        # Update percentage text if it exists
        if hasattr(self.content_ref.current.content, 'controls') and len(self.content_ref.current.content.controls) > 1:
            row = self.content_ref.current.content.controls[1]
            if isinstance(row, ft.Row) and hasattr(row, 'controls') and len(row.controls) > 0:
                text_control = row.controls[0]
                if isinstance(text_control, ft.Text):
                    text_control.value = f"{int(progress * 100)}%"
        
        # Update description if provided
        if description and hasattr(self.content_ref.current.content, 'controls') and len(self.content_ref.current.content.controls) > 1:
            row = self.content_ref.current.content.controls[1]
            if isinstance(row, ft.Row) and hasattr(row, 'controls') and len(row.controls) > 1:
                text_control = row.controls[1]
                if isinstance(text_control, ft.Text):
                    text_control.value = description
        
        self.page.update()


class StatusWidget(EnhancedWidget):
    """
    Specialized widget for displaying status
    """
    
    def __init__(
        self,
        page: ft.Page,
        title: str,
        status: str,
        status_color: Optional[str] = None,
        details: Optional[str] = None,
        last_updated: Optional[datetime] = None,
        **kwargs
    ):
        # Determine status color
        if not status_color:
            status_color = self._get_status_color(status)
        
        # Create content
        content_controls = []
        
        # Status indicator
        status_row = ft.Row([
            ft.Icon(
                self._get_status_icon(status),
                color=status_color,
                size=20
            ),
            ft.Text(
                status,
                style=ft.TextThemeStyle.TITLE_MEDIUM,
                weight=ft.FontWeight.W_500
            )
        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        content_controls.append(status_row)
        
        # Details
        if details:
            content_controls.append(
                ft.Text(
                    details,
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=TOKENS['outline']
                )
            )
        
        # Last updated
        if last_updated:
            content_controls.append(
                ft.Text(
                    f"Last updated: {last_updated.strftime('%Y-%m-%d %H:%M')}",
                    style=ft.TextThemeStyle.BODY_SMALL,
                    color=TOKENS['outline']
                )
            )
        
        config = WidgetConfig(
            title=title,
            widget_type=WidgetType.STATUS,
            content=ft.Column(content_controls, spacing=8),
            size=WidgetSize.SMALL,
            **kwargs
        )
        
        super().__init__(page, config)
    
    def _get_status_color(self, status: str) -> str:
        """Get color for status"""
        status_lower = status.lower()
        if "online" in status_lower or "active" in status_lower or "success" in status_lower:
            return TOKENS['secondary']
        elif "offline" in status_lower or "error" in status_lower or "failed" in status_lower:
            return TOKENS['error']
        elif "warning" in status_lower or "pending" in status_lower:
            return TOKENS['tertiary']
        else:
            return TOKENS['on_background']
    
    def _get_status_icon(self, status: str) -> str:
        """Get icon for status"""
        status_lower = status.lower()
        if "online" in status_lower or "active" in status_lower or "success" in status_lower:
            return ft.Icons.CHECK_CIRCLE
        elif "offline" in status_lower or "error" in status_lower or "failed" in status_lower:
            return ft.Icons.ERROR
        elif "warning" in status_lower or "pending" in status_lower:
            return ft.Icons.WARNING
        else:
            return ft.Icons.INFO
    
    def update_status(self, status: str, details: Optional[str] = None, last_updated: Optional[datetime] = None):
        """Update status"""
        # Update status text and icon
        if hasattr(self.content_ref.current.content, 'controls') and len(self.content_ref.current.content.controls) > 0:
            status_row = self.content_ref.current.content.controls[0]
            if isinstance(status_row, ft.Row) and hasattr(status_row, 'controls') and len(status_row.controls) > 1:
                # Update icon
                icon_control = status_row.controls[0]
                if isinstance(icon_control, ft.Icon):
                    icon_control.name = self._get_status_icon(status)
                    icon_control.color = self._get_status_color(status)
                
                # Update text
                text_control = status_row.controls[1]
                if isinstance(text_control, ft.Text):
                    text_control.value = status
        
        # Update details if provided
        if details and hasattr(self.content_ref.current.content, 'controls') and len(self.content_ref.current.content.controls) > 1:
            details_control = self.content_ref.current.content.controls[1]
            if isinstance(details_control, ft.Text):
                details_control.value = details
        
        # Update last updated if provided
        if last_updated and hasattr(self.content_ref.current.content, 'controls') and len(self.content_ref.current.content.controls) > 2:
            last_updated_control = self.content_ref.current.content.controls[2]
            if isinstance(last_updated_control, ft.Text):
                last_updated_control.value = f"Last updated: {last_updated.strftime('%Y-%m-%d %H:%M')}"
        
        self.page.update()


# Widget manager for dashboard
class WidgetManager:
    """
    Manager for organizing and layouting widgets in a dashboard
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.widgets: List[EnhancedWidget] = []
        self.grid_ref = ft.Ref[ft.ResponsiveRow]()
    
    def add_widget(self, widget: EnhancedWidget):
        """Add widget to manager"""
        self.widgets.append(widget)
    
    def remove_widget(self, widget: EnhancedWidget):
        """Remove widget from manager"""
        if widget in self.widgets:
            widget.dispose()
            self.widgets.remove(widget)
    
    def create_dashboard(self) -> ft.Control:
        """Create dashboard layout with widgets"""
        # Create grid controls
        grid_controls = []
        for widget in self.widgets:
            # Determine column span based on widget size
            col_span = self._get_column_span(widget.config.size)
            
            grid_controls.append(
                ft.ResponsiveGridCell(
                    widget.get_control(),
                    col_span=col_span
                )
            )
        
        # Create responsive grid
        grid = ft.ResponsiveRow(
            ref=self.grid_ref,
            controls=grid_controls,
            spacing=20,
            run_spacing=20
        )
        
        return grid
    
    def _get_column_span(self, size: WidgetSize) -> int:
        """Get column span for widget size"""
        if size == WidgetSize.SMALL:
            return 3  # 1/4 of 12-column grid
        elif size == WidgetSize.MEDIUM:
            return 6  # 1/2 of 12-column grid
        elif size == WidgetSize.LARGE:
            return 12  # Full width
        elif size == WidgetSize.WIDE:
            return 12  # Full width
        elif size == WidgetSize.FULL:
            return 12  # Full width
        else:
            return 6  # Default to medium


# Test function
async def test_enhanced_widgets(page: ft.Page):
    """Test enhanced widgets functionality"""
    print("Testing enhanced widgets...")
    
    # Create different widget types
    stat_widget = StatWidget(
        page,
        title="Total Files",
        value=1250,
        unit="files",
        icon=ft.Icons.FOLDER,
        trend="+12% from last week"
    )
    
    progress_widget = ProgressWidget(
        page,
        title="Backup Progress",
        progress=0.75,
        description="Processing files...",
        show_percentage=True
    )
    
    status_widget = StatusWidget(
        page,
        title="Server Status",
        status="Online",
        details="All systems operational",
        last_updated=datetime.now()
    )
    
    # Create widget manager and dashboard
    widget_manager = WidgetManager(page)
    widget_manager.add_widget(stat_widget)
    widget_manager.add_widget(progress_widget)
    widget_manager.add_widget(status_widget)
    
    dashboard = widget_manager.create_dashboard()
    
    # Create layout
    layout = ft.Column([
        ft.Text("Enhanced Widgets Test", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
        dashboard
    ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
    
    # Add to page
    page.add(layout)
    page.update()
    
    # Test updates
    await asyncio.sleep(2)
    progress_widget.update_progress(0.9, "Finalizing backup...")
    await asyncio.sleep(1)
    status_widget.update_status("Maintenance", "System update in progress", datetime.now())
    
    print("Enhanced widgets test completed")


if __name__ == "__main__":
    print("Enhanced Widget Components Module")
    print("This module provides enhanced widget components for the Flet Server GUI")