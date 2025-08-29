#!/usr/bin/env python3
"""
UI Widgets - Dashboard Widgets

Purpose: Reusable dashboard widgets with enhanced interactions and animations
Logic: Widget state management, refresh scheduling, content updates
UI: Collapsible widgets, animated transitions, responsive layouts

This module consolidates functionality from the previous components/widgets.py file
and integrates it with the existing card components to provide a comprehensive
widget system for the dashboard.
"""

import flet as ft
from typing import Optional, Callable, List, Dict, Union, Any
from enum import Enum
import asyncio
from datetime import datetime
from flet_server_gui.ui.unified_theme_system import TOKENS


class WidgetSize(Enum):
    """Standard widget sizes for responsive grid layouts"""
    SMALL = 1   # 1 column (25% width on large screens)
    MEDIUM = 2  # 2 columns (50% width on large screens)
    LARGE = 3   # 3 columns (75% width on large screens)
    FULL = 4    # Full width (100% width on all screens)


class DashboardWidget(ft.Card):
    """
    Base dashboard widget with enhanced features including:
    - Collapsible content
    - Auto-refresh capabilities
    - Animated transitions
    - Responsive sizing
    - Theme-aware styling
    """
    
    def __init__(self,
                 title: str,
                 content: ft.Control,
                 size: WidgetSize = WidgetSize.MEDIUM,
                 refresh_interval: Optional[int] = None,
                 on_refresh: Optional[Callable] = None,
                 collapsible: bool = True,
                 animate_duration: int = 200,
                 **kwargs):
        """
        Initialize dashboard widget.
        
        Args:
            title: Widget title displayed in header
            content: Main widget content control
            size: Widget size for responsive grid layout
            refresh_interval: Auto-refresh interval in seconds (None to disable)
            on_refresh: Callback function for refresh operations
            collapsible: Whether widget content can be collapsed
            animate_duration: Duration for animations in milliseconds
            **kwargs: Additional Card properties
        """
        super().__init__(**kwargs)
        
        self.title = title
        self.size = size
        self.refresh_interval = refresh_interval
        self.on_refresh_callback = on_refresh
        self.collapsible = collapsible
        self.is_collapsed = False
        self.animate_duration = animate_duration
        
        # Animation properties
        self.animate_scale = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
        self.animate_elevation = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
        
        # Store content reference for collapse/expand
        self.main_content = content
        
        # Create content container with initial state
        self.content_container = ft.Container(
            content=content,
            animate=ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT),
            expand=True
        )
        
        # Build the complete widget
        self.content = self._build_widget()
        
        # Start refresh timer if configured
        if refresh_interval and refresh_interval > 0:
            self._start_refresh_timer()
    
    def _build_widget(self) -> ft.Container:
        """Build the complete widget with header and content."""
        # Header with title and controls
        header_controls = []
        
        # Title
        title_text = ft.Text(
            self.title,
            style=ft.TextThemeStyle.TITLE_MEDIUM,
            weight=ft.FontWeight.BOLD,
            expand=True
        )
        header_controls.append(title_text)
        
        # Collapsible button if enabled
        if self.collapsible:
            collapse_button = ft.IconButton(
                icon=ft.Icons.EXPAND_LESS,
                tooltip="Collapse",
                on_click=self._toggle_collapse,
                icon_size=20
            )
            header_controls.append(collapse_button)
        
        # Refresh button if callback provided
        if self.on_refresh_callback:
            refresh_button = ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Refresh",
                on_click=self._refresh,
                icon_size=20
            )
            header_controls.append(refresh_button)
        
        # Header row
        header = ft.Row(
            header_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        # Divider
        divider = ft.Divider(height=1, thickness=1)
        
        # Widget content
        widget_content = ft.Column([
            header,
            divider,
            self.content_container
        ], spacing=12, expand=True)
        
        # Card container
        card_container = ft.Container(
            content=widget_content,
            padding=ft.padding.all(16),
            expand=True
        )
        
        return card_container
    
    def _toggle_collapse(self, e):
        """Toggle widget collapse state with animation."""
        self.is_collapsed = not self.is_collapsed
        
        # Update collapse button icon and tooltip
        header_row = self.content.content.controls[0]  # Header row
        collapse_button = header_row.controls[-2 if self.on_refresh_callback else -1]  # Collapse button
        collapse_button.icon = ft.Icons.EXPAND_MORE if self.is_collapsed else ft.Icons.EXPAND_LESS
        collapse_button.tooltip = "Expand" if self.is_collapsed else "Collapse"
        
        # Animate content visibility
        if self.is_collapsed:
            self.content_container.height = 0
            self.content_container.opacity = 0
        else:
            self.content_container.height = None  # Auto height
            self.content_container.opacity = 1
            
        self.page.update()
    
    def _refresh(self, e):
        """Refresh widget content."""
        if self.on_refresh_callback:
            self.on_refresh_callback(e)
    
    def _start_refresh_timer(self):
        """Start automatic refresh timer."""
        async def refresh_loop():
            while True:
                await asyncio.sleep(self.refresh_interval)
                if self.on_refresh_callback and self.page:
                    # Run refresh callback
                    try:
                        self.on_refresh_callback(None)
                    except Exception as ex:
                        print(f"[ERROR] Widget refresh failed: {ex}")
        
        if self.page:
            asyncio.create_task(refresh_loop())
    
    def update_content(self, new_content: ft.Control):
        """Update widget content with animation."""
        self.main_content = new_content
        if not self.is_collapsed:
            self.content_container.content = new_content
            # Add entrance animation
            self.content_container.opacity = 0
            self.content_container.animate_opacity = ft.Animation(200, ft.AnimationCurve.EASE_OUT)
            self.page.update()
            self.content_container.opacity = 1
            self.page.update()
    
    def set_title(self, new_title: str):
        """Update widget title."""
        header_row = self.content.content.controls[0]  # Header row
        title_control = header_row.controls[0]  # Title text
        title_control.value = new_title
        self.title = new_title
        self.page.update()


class StatisticWidget(DashboardWidget):
    """
    Specialized widget for displaying statistics with trends.
    Shows a numeric value with optional unit, icon, and trend indicator.
    """
    
    def __init__(self,
                 title: str,
                 value: Union[int, float, str],
                 unit: Optional[str] = None,
                 icon: Optional[ft.Icons] = None,
                 trend: Optional[float] = None,  # Positive/negative percentage
                 color: Optional[str] = None,
                 size: WidgetSize = WidgetSize.SMALL,
                 **kwargs):
        """
        Initialize statistic widget.
        
        Args:
            title: Statistic title
            value: Numeric value to display
            unit: Optional unit (e.g., "MB", "%", "clients")
            icon: Optional icon to display
            trend: Optional trend percentage (positive = up, negative = down)
            color: Optional color for value display
            size: Widget size
            **kwargs: Additional DashboardWidget properties
        """
        # Create statistic content
        content_items = []
        
        # Icon if provided
        if icon:
            content_items.append(
                ft.Icon(icon, size=32, color=color or TOKENS['primary'])
            )
        
        # Value display
        value_text = ft.Text(
            str(value),
            style=ft.TextThemeStyle.DISPLAY_MEDIUM,
            weight=ft.FontWeight.BOLD,
            color=color or TOKENS['on_background']
        )
        
        # Unit if provided
        if unit:
            value_with_unit = ft.Row([
                value_text,
                ft.Text(unit, style=ft.TextThemeStyle.LABEL_LARGE, color=TOKENS['outline'])
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER)
            content_items.append(value_with_unit)
        else:
            content_items.append(value_text)
        
        # Trend indicator if provided
        if trend is not None:
            trend_color = TOKENS['secondary'] if trend >= 0 else TOKENS['error']
            trend_icon = ft.Icons.ARROW_UPWARD if trend >= 0 else ft.Icons.ARROW_DOWNWARD
            trend_text = ft.Text(f"{abs(trend):.1f}%", color=trend_color, size=12)
            
            trend_indicator = ft.Row([
                ft.Icon(trend_icon, size=16, color=trend_color),
                trend_text
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER)
            
            content_items.append(trend_indicator)
        
        # Create content column
        stat_content = ft.Column(
            content_items,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        )
        
        super().__init__(
            title=title,
            content=stat_content,
            size=size,
            **kwargs
        )


class ActivityFeedWidget(DashboardWidget):
    """
    Specialized widget for displaying activity feeds.
    Shows a chronological list of activities with timestamps and severity levels.
    """
    
    def __init__(self,
                 title: str = "Recent Activity",
                 activities: Optional[List[Dict[str, str]]] = None,
                 max_activities: int = 10,
                 size: WidgetSize = WidgetSize.MEDIUM,
                 **kwargs):
        """
        Initialize activity feed widget.
        
        Args:
            title: Widget title
            activities: List of activity dictionaries with keys:
                       - timestamp: Activity timestamp
                       - message: Activity description
                       - source: Activity source (optional)
                       - level: Severity level (INFO, SUCCESS, WARNING, ERROR)
            max_activities: Maximum number of activities to display
            size: Widget size
            **kwargs: Additional DashboardWidget properties
        """
        self.activities = activities or []
        self.max_activities = max_activities
        
        # Create activity feed content
        feed_content = self._create_feed_content()
        
        super().__init__(
            title=title,
            content=feed_content,
            size=size,
            **kwargs
        )
    
    def _create_feed_content(self) -> ft.Control:
        """Create activity feed content."""
        activity_items = []
        
        # Limit to max_activities
        display_activities = self.activities[-self.max_activities:] if len(self.activities) > self.max_activities else self.activities
        
        for activity in display_activities:
            timestamp = activity.get("timestamp", "")
            message = activity.get("message", "")
            source = activity.get("source", "")
            level = activity.get("level", "INFO")
            
            # Determine icon and color based on level
            level_configs = {
                "INFO": (ft.Icons.INFO_OUTLINE, TOKENS['primary']),
                "SUCCESS": (ft.Icons.CHECK_CIRCLE_OUTLINE, TOKENS['secondary']),
                "WARNING": (ft.Icons.WARNING_AMBER, TOKENS['tertiary']),
                "ERROR": (ft.Icons.ERROR_OUTLINE, TOKENS['error'])
            }
            
            icon, color = level_configs.get(level.upper(), (ft.Icons.INFO_OUTLINE, TOKENS['primary']))
            
            activity_item = ft.ListTile(
                leading=ft.Icon(icon, color=color, size=16),
                title=ft.Text(message, size=13),
                subtitle=ft.Text(f"{source} • {timestamp}", size=11, color=TOKENS['outline']),
                dense=True
            )
            
            activity_items.append(activity_item)
            activity_items.append(ft.Divider(height=1))
        
        if not activity_items:
            activity_items.append(
                ft.Text("No recent activity", italic=True, color=TOKENS['outline'])
            )
        
        return ft.Column(activity_items, spacing=2, expand=True)
    
    def add_activity(self, activity: Dict[str, str]):
        """Add a new activity to the feed."""
        self.activities.append(activity)
        # Update the feed content
        feed_content = self._create_feed_content()
        self.update_content(feed_content)


# Factory functions for easy widget creation
def create_stat_widget(title: str,
                       value: Union[int, float, str],
                       unit: Optional[str] = None,
                       icon: Optional[ft.Icons] = None,
                       trend: Optional[float] = None,
                       color: Optional[str] = None,
                       size: WidgetSize = WidgetSize.SMALL,
                       **kwargs) -> StatisticWidget:
    """Create a statistic widget."""
    return StatisticWidget(
        title=title,
        value=value,
        unit=unit,
        icon=icon,
        trend=trend,
        color=color,
        size=size,
        **kwargs
    )


def create_activity_widget(title: str = "Recent Activity",
                          activities: Optional[List[Dict[str, str]]] = None,
                          max_activities: int = 10,
                          size: WidgetSize = WidgetSize.MEDIUM,
                          **kwargs) -> ActivityFeedWidget:
    """Create an activity feed widget."""
    return ActivityFeedWidget(
        title=title,
        activities=activities,
        max_activities=max_activities,
        size=size,
        **kwargs
    )


def create_dashboard_widget(title: str,
                           content: ft.Control,
                           size: WidgetSize = WidgetSize.MEDIUM,
                           refresh_interval: Optional[int] = None,
                           on_refresh: Optional[Callable] = None,
                           collapsible: bool = True,
                           **kwargs) -> DashboardWidget:
    """Create a generic dashboard widget."""
    return DashboardWidget(
        title=title,
        content=content,
        size=size,
        refresh_interval=refresh_interval,
        on_refresh=on_refresh,
        collapsible=collapsible,
        **kwargs
    )