#!/usr/bin/env python3
"""
Enhanced Statistics Card Component
Material Design 3 card with enhanced statistics visualization including progress bars and trend indicators.
"""

import flet as ft
from typing import Optional, Union
from flet_server_gui.components.enhanced_components import (
    create_enhanced_button,
    create_enhanced_icon_button,
    EnhancedCard,
    EnhancedChip
)
from flet_server_gui.components.widgets import StatisticWidget, WidgetSize


class EnhancedStatsCard(EnhancedCard):
    """Enhanced statistics card with visual indicators and progress bars"""
    
    def __init__(self, 
                 title: str = "Statistics Overview",
                 animate_duration: int = 300,
                 **kwargs):
        self.title = title
        self.stats_data = {}
        
        # Create the main content
        content = self._build_content()
        
        super().__init__(
            content=content,
            animate_duration=animate_duration,
            **kwargs
        )
    
    def _build_content(self) -> ft.Control:
        """Build the enhanced statistics content"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.INSERT_CHART_OUTLINED, size=24),
            ft.Text(self.title, style=ft.TextThemeStyle.TITLE_LARGE),
        ], spacing=12)
        
        # Statistics grid
        stats_grid = ft.ResponsiveRow([
            # CPU Usage with progress bar
            ft.Column([
                ft.Text("CPU Usage", style=ft.TextThemeStyle.LABEL_LARGE),
                ft.ProgressBar(
                    value=0.0,
                    bar_height=8,
                    border_radius=4
                ),
                ft.Text("0%", style=ft.TextThemeStyle.BODY_MEDIUM, color=ft.Colors.ON_SURFACE_VARIANT)
            ], col={"sm": 6, "md": 3}),
            
            # Memory Usage with progress bar
            ft.Column([
                ft.Text("Memory Usage", style=ft.TextThemeStyle.LABEL_LARGE),
                ft.ProgressBar(
                    value=0.0,
                    bar_height=8,
                    border_radius=4
                ),
                ft.Text("0%", style=ft.TextThemeStyle.BODY_MEDIUM, color=ft.Colors.ON_SURFACE_VARIANT)
            ], col={"sm": 6, "md": 3}),
            
            # Network Traffic
            ft.Column([
                ft.Text("Network", style=ft.TextThemeStyle.LABEL_LARGE),
                ft.Row([
                    ft.Icon(ft.Icons.ARROW_UPWARD, size=16, color=ft.Colors.GREEN),
                    ft.Text("0 KB/s", style=ft.TextThemeStyle.BODY_MEDIUM),
                ], spacing=4),
                ft.Row([
                    ft.Icon(ft.Icons.ARROW_DOWNWARD, size=16, color=ft.Colors.BLUE),
                    ft.Text("0 KB/s", style=ft.TextThemeStyle.BODY_MEDIUM),
                ], spacing=4)
            ], col={"sm": 6, "md": 3}),
            
            # Storage Usage
            ft.Column([
                ft.Text("Storage", style=ft.TextThemeStyle.LABEL_LARGE),
                ft.ProgressBar(
                    value=0.0,
                    bar_height=8,
                    border_radius=4
                ),
                ft.Text("0%", style=ft.TextThemeStyle.BODY_MEDIUM, color=ft.Colors.ON_SURFACE_VARIANT)
            ], col={"sm": 6, "md": 3}),
        ], spacing=20)
        
        # Quick actions
        quick_actions = ft.Row([
            create_enhanced_button(
                text="Refresh",
                icon=ft.Icons.REFRESH,
                on_click=self._on_refresh,
                size=32
            ),
            create_enhanced_button(
                text="View Details",
                icon=ft.Icons.VISIBILITY,
                on_click=self._on_view_details,
                size=32
            )
        ], spacing=12)
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                stats_grid,
                ft.Divider(),
                quick_actions
            ], spacing=16),
            padding=ft.padding.all(20)
        )
    
    def update_stats(self, cpu_percent: float = 0.0, 
                     memory_percent: float = 0.0,
                     network_up: str = "0 KB/s",
                     network_down: str = "0 KB/s",
                     storage_percent: float = 0.0):
        """Update statistics with new data"""
        if not self.content:
            return
            
        # Get the stats grid (3rd control in the column)
        stats_grid = self.content.content.controls[2]
        
        # Update CPU usage
        cpu_col = stats_grid.controls[0]
        cpu_progress = cpu_col.controls[1]
        cpu_text = cpu_col.controls[2]
        cpu_progress.value = cpu_percent / 100.0
        cpu_text.value = f"{cpu_percent:.1f}%"
        
        # Update Memory usage
        mem_col = stats_grid.controls[1]
        mem_progress = mem_col.controls[1]
        mem_text = mem_col.controls[2]
        mem_progress.value = memory_percent / 100.0
        mem_text.value = f"{memory_percent:.1f}%"
        
        # Update Network traffic
        net_col = stats_grid.controls[2]
        net_up_text = net_col.controls[1].controls[1]
        net_down_text = net_col.controls[2].controls[1]
        net_up_text.value = network_up
        net_down_text.value = network_down
        
        # Update Storage usage
        storage_col = stats_grid.controls[3]
        storage_progress = storage_col.controls[1]
        storage_text = storage_col.controls[2]
        storage_progress.value = storage_percent / 100.0
        storage_text.value = f"{storage_percent:.1f}%"
        
        self.page.update()

    def _on_refresh(self, e):
        """Handle refresh button click"""
        # Show a toast notification
        self.toast_manager.show_success("Statistics refreshed", duration=3)

    def _on_view_details(self, e):
        """Handle view details button click"""
        # Show a toast notification
        self.toast_manager.show_info("Viewing detailed statistics", duration=3)


# Factory function
def create_enhanced_stats_card(title: str = "Statistics Overview", **kwargs) -> EnhancedStatsCard:
    """Create an enhanced statistics card"""
    return EnhancedStatsCard(title=title, **kwargs)