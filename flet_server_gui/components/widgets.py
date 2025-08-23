#!/usr/bin/env python3
"""
Dashboard Widget System
Modular dashboard widgets with enhanced interactions and animations.
"""

import flet as ft
from typing import Optional, Callable, List, Dict, Union
from enum import Enum
import asyncio


class WidgetSize(Enum):
    """Standard widget sizes"""
    SMALL = 1  # 1 column
    MEDIUM = 2  # 2 columns
    LARGE = 3   # 3 columns
    FULL = 4    # Full width


class DashboardWidget(ft.Card):
    """Base dashboard widget with enhanced features"""
    
    def __init__(self,
                 title: str,
                 content: ft.Control,
                 size: WidgetSize = WidgetSize.MEDIUM,
                 refresh_interval: Optional[int] = None,
                 on_refresh: Optional[Callable] = None,
                 collapsible: bool = True,
                 animate_duration: int = 200,
                 **kwargs):
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
        
        # Create header controls
        self.header_controls = self._create_header_controls()
        
        # Store content for collapse/expand
        self.main_content = content
        
        # Build widget
        self.content = self._build_widget()
        
        # Start refresh timer if interval specified
        if refresh_interval:
            self._start_refresh_timer()
    
    def _create_header_controls(self) -> List[ft.Control]:
        """Create header controls (title, buttons)"""
        controls = [
            ft.Text(self.title, style=ft.TextThemeStyle.TITLE_MEDIUM, expand=True)
        ]
        
        if self.collapsible:
            controls.append(
                ft.IconButton(
                    icon=ft.Icons.EXPAND_LESS,
                    tooltip="Collapse",
                    on_click=self._toggle_collapse,
                    animate_scale=ft.Animation(100, ft.AnimationCurve.EASE_OUT)
                )
            )
        
        if self.refresh_interval or self.on_refresh_callback:
            controls.append(
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refresh",
                    on_click=self._refresh,
                    animate_scale=ft.Animation(100, ft.AnimationCurve.EASE_OUT)
                )
            )
        
        return controls
    
    def _build_widget(self) -> ft.Control:
        """Build the complete widget"""
        # Header row
        header = ft.Row(
            self.header_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # Divider
        divider = ft.Divider()
        
        # Content container (for collapse/expand)
        self.content_container = ft.Container(
            content=self.main_content,
            animate=ft.Animation(self.animate_duration, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(self.animate_duration, ft.AnimationCurve.EASE_OUT)
        )
        
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
        """Toggle widget collapse state"""
        self.is_collapsed = not self.is_collapsed
        
        # Update header button icon
        header_row = self.content.content.controls[0]  # Header row
        collapse_button = header_row.controls[-1]  # Last button (collapse)
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
        """Refresh widget content"""
        if self.on_refresh_callback:
            self.on_refresh_callback(e)
    
    def _start_refresh_timer(self):
        """Start automatic refresh timer"""
        async def refresh_loop():
            while True:
                await asyncio.sleep(self.refresh_interval)
                if self.on_refresh_callback and self.page:
                    self.on_refresh_callback(None)
        
        if self.page:
            asyncio.create_task(refresh_loop())
    
    def update_content(self, new_content: ft.Control):
        """Update widget content"""
        self.main_content = new_content
        if not self.is_collapsed:
            self.content_container.content = new_content
            self.page.update()


class StatisticWidget(DashboardWidget):
    """Specialized widget for displaying statistics"""
    
    def __init__(self,
                 title: str,
                 value: Union[int, float, str],
                 unit: Optional[str] = None,
                 icon: Optional[ft.Icons] = None,
                 trend: Optional[float] = None,  # Positive/negative percentage
                 color: Optional[str] = None,
                 size: WidgetSize = WidgetSize.SMALL,
                 **kwargs):
        # Create statistic content
        content_items = []
        
        # Icon if provided
        if icon:
            content_items.append(
                ft.Icon(icon, size=32, color=color or ft.Colors.PRIMARY)
            )
        
        # Value display
        value_text = ft.Text(
            str(value),
            style=ft.TextThemeStyle.DISPLAY_MEDIUM,
            weight=ft.FontWeight.BOLD,
            color=color or ft.Colors.ON_SURFACE
        )
        
        # Unit if provided
        if unit:
            value_with_unit = ft.Row([
                value_text,
                ft.Text(unit, style=ft.TextThemeStyle.LABEL_LARGE, color=ft.Colors.ON_SURFACE_VARIANT)
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER)
            content_items.append(value_with_unit)
        else:
            content_items.append(value_text)
        
        # Trend indicator if provided
        if trend is not None:
            trend_color = ft.Colors.GREEN if trend >= 0 else ft.Colors.RED
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
    """Specialized widget for displaying activity feeds"""
    
    def __init__(self,
                 title: str = "Recent Activity",
                 activities: Optional[List[Dict[str, str]]] = None,
                 max_activities: int = 10,
                 size: WidgetSize = WidgetSize.MEDIUM,
                 **kwargs):
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
        """Create activity feed content"""
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
                "INFO": (ft.Icons.INFO_OUTLINE, ft.Colors.PRIMARY),
                "SUCCESS": (ft.Icons.CHECK_CIRCLE_OUTLINE, ft.Colors.GREEN),
                "WARNING": (ft.Icons.WARNING_AMBER, ft.Colors.ORANGE),
                "ERROR": (ft.Icons.ERROR_OUTLINE, ft.Colors.RED)
            }
            
            icon, color = level_configs.get(level.upper(), (ft.Icons.INFO_OUTLINE, ft.Colors.PRIMARY))
            
            activity_item = ft.ListTile(
                leading=ft.Icon(icon, color=color, size=16),
                title=ft.Text(message, size=13),
                subtitle=ft.Text(f"{source} • {timestamp}", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                dense=True
            )
            
            activity_items.append(activity_item)
            activity_items.append(ft.Divider(height=1))
        
        if not activity_items:
            activity_items.append(
                ft.Text("No recent activity", italic=True, color=ft.Colors.ON_SURFACE_VARIANT)
            )
        
        return ft.Column(activity_items, spacing=2, expand=True)


# Factory functions for easy widget creation
def create_stat_widget(title: str,
                       value: Union[int, float, str],
                       unit: Optional[str] = None,
                       icon: Optional[ft.Icons] = None,
                       trend: Optional[float] = None,
                       color: Optional[str] = None,
                       size: WidgetSize = WidgetSize.SMALL,
                       **kwargs) -> StatisticWidget:
    """Create a statistic widget"""
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
    """Create an activity feed widget"""
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
    """Create a generic dashboard widget"""
    return DashboardWidget(
        title=title,
        content=content,
        size=size,
        refresh_interval=refresh_interval,
        on_refresh=on_refresh,
        collapsible=collapsible,
        **kwargs
    )