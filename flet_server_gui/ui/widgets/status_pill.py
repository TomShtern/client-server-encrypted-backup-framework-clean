#!/usr/bin/env python3
"""
Status Pill - Animated server status indicator

Purpose: Real-time server status monitoring with visual indicators
Logic: Status tracking, animation management, server integration
UI: Animated status pill with color coding and tooltips
"""

import flet as ft
from typing import Optional, Callable, Dict, Any
from enum import Enum
import asyncio
from datetime import datetime, timedelta


class ServerStatus(Enum):
    """Server operational status with clear semantic meaning"""
    RUNNING = "running"           # Server actively handling requests
    STOPPED = "stopped"           # Server intentionally stopped by user
    STARTING = "starting"         # Server in startup process
    STOPPING = "stopping"        # Server in shutdown process
    ERROR = "error"              # Server encountered critical error
    UNKNOWN = "unknown"          # Status cannot be determined
    MAINTENANCE = "maintenance"   # Server in maintenance mode


class StatusSeverity(Enum):
    """Status indicator severity levels for visual hierarchy"""
    SUCCESS = "success"     # Green indicators - everything working
    INFO = "info"          # Blue indicators - informational status
    WARNING = "warning"    # Orange indicators - attention needed
    ERROR = "error"        # Red indicators - critical issues
    NEUTRAL = "neutral"    # Gray indicators - neutral status


class StatusPillConfig:
    """Configuration for status pill appearance and behavior"""
    def __init__(self, 
                 size: str = "normal",
                 show_text: bool = True,
                 show_icon: bool = True,
                 clickable: bool = True,
                 animation_duration: int = 300):
        self.size = size
        self.show_text = show_text
        self.show_icon = show_icon
        self.clickable = clickable
        self.animation_duration = animation_duration


class StatusPill(ft.Container):
    """Animated server status indicator pill with Material Design 3 styling"""
    
    def __init__(self, 
                 initial_status: ServerStatus = ServerStatus.UNKNOWN,
                 config: Optional[StatusPillConfig] = None,
                 on_click: Optional[Callable] = None):
        super().__init__()
        self.status = initial_status
        self.config = config or StatusPillConfig()
        self.on_click = on_click
        self._text: Optional[ft.Text] = None
        self._icon: Optional[ft.Icon] = None
        self._tooltip_content: Optional[ft.Tooltip] = None
        
        # Status mapping
        self._status_text_map = {
            ServerStatus.RUNNING: "ONLINE",
            ServerStatus.STOPPED: "OFFLINE",
            ServerStatus.STARTING: "STARTING...",
            ServerStatus.STOPPING: "STOPPING...",
            ServerStatus.ERROR: "ERROR",
            ServerStatus.UNKNOWN: "UNKNOWN",
            ServerStatus.MAINTENANCE: "MAINTENANCE"
        }
        
        self._status_color_map = {
            ServerStatus.RUNNING: ft.Colors.GREEN,
            ServerStatus.STOPPED: ft.Colors.GREY,
            ServerStatus.STARTING: ft.Colors.BLUE,
            ServerStatus.STOPPING: ft.Colors.ORANGE,
            ServerStatus.ERROR: ft.Colors.RED,
            ServerStatus.UNKNOWN: ft.Colors.AMBER,
            ServerStatus.MAINTENANCE: ft.Colors.PURPLE
        }
        
        self._status_icon_map = {
            ServerStatus.RUNNING: ft.Icons.PLAY_CIRCLE,
            ServerStatus.STOPPED: ft.Icons.STOP_CIRCLE,
            ServerStatus.STARTING: ft.Icons.REFRESH,
            ServerStatus.STOPPING: ft.Icons.PAUSE_CIRCLE,
            ServerStatus.ERROR: ft.Icons.ERROR,
            ServerStatus.UNKNOWN: ft.Icons.HELP,
            ServerStatus.MAINTENANCE: ft.Icons.BUILD
        }
        
        # Build the component
        self._build_component()
    
    def _build_component(self):
        """Build the status pill UI with Material Design 3 styling"""
        # Create text component
        if self.config.show_text:
            self._text = ft.Text(
                self._get_status_text(),
                size=12,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.WHITE
            )
        
        # Create icon component
        if self.config.show_icon:
            self._icon = ft.Icon(
                self._get_status_icon(),
                size=16,
                color=ft.Colors.WHITE
            )
        
        # Create content row
        content_items = []
        if self._icon:
            content_items.append(self._icon)
        if self._text:
            content_items.append(self._text)
        
        content_row = ft.Row(
            content_items,
            tight=True,
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER
        )
        
        # Configure container
        self.content = content_row
        self.bgcolor = self._get_status_color()
        self.border_radius = 16
        self.padding = ft.padding.symmetric(horizontal=12, vertical=6)
        self.animate = ft.Animation(self.config.animation_duration, ft.AnimationCurve.EASE_OUT)
        
        if self.config.clickable and self.on_click:
            self.ink = True
            self.on_click = self._handle_click
    
    def set_status(self, status: ServerStatus, animate: bool = True):
        """Update status with optional animation"""
        if self.status != status:
            old_status = self.status
            self.status = status
            
            # Update UI components
            self.bgcolor = self._get_status_color()
            
            # Update text if shown
            if self._text:
                self._text.value = self._get_status_text()
            
            # Update icon if shown
            if self._icon:
                self._icon.name = self._get_status_icon()
                self._icon.color = ft.Colors.WHITE
            
            # Trigger animation
            if animate:
                self.scale = 0.95
                self.update()
                self.scale = 1.0
                self.update()
            else:
                # Only update if attached to a page
                try:
                    if self.page:
                        self.update()
                except (AttributeError, AssertionError):
                    # Control not attached to page, skip update
                    pass
    
    def _get_status_text(self) -> str:
        """Get display text for current status"""
        return self._status_text_map.get(self.status, "UNKNOWN")
    
    def _get_status_color(self) -> str:
        """Get background color for current status"""
        return self._status_color_map.get(self.status, ft.Colors.GREY)
    
    def _get_status_icon(self) -> str:
        """Get icon for current status"""
        return self._status_icon_map.get(self.status, ft.Icons.CIRCLE)
    
    def _get_tooltip_text(self) -> str:
        """Get tooltip text for current status"""
        tooltip_map = {
            ServerStatus.RUNNING: "Server is online and ready to handle requests",
            ServerStatus.STOPPED: "Server is offline",
            ServerStatus.STARTING: "Server is starting up",
            ServerStatus.STOPPING: "Server is shutting down",
            ServerStatus.ERROR: "Server encountered an error",
            ServerStatus.UNKNOWN: "Server status cannot be determined",
            ServerStatus.MAINTENANCE: "Server is in maintenance mode"
        }
        return tooltip_map.get(self.status, "Unknown server status")
    
    def _handle_click(self, e):
        """Handle click events"""
        if self.on_click:
            self.on_click(e)
    
    def pulse(self):
        """Add a pulse animation to draw attention"""
        self.scale = 1.1
        self.update()
        self.scale = 1.0
        self.update()


# Factory functions for easy creation
def create_status_pill(status: ServerStatus = ServerStatus.UNKNOWN,
                      config: Optional[StatusPillConfig] = None,
                      on_click: Optional[Callable] = None) -> StatusPill:
    """Create a status pill with the given configuration"""
    return StatusPill(status, config, on_click)


def create_hero_status_pill(status: ServerStatus = ServerStatus.UNKNOWN,
                           on_click: Optional[Callable] = None) -> StatusPill:
    """Create a large hero status pill for main dashboard display"""
    config = StatusPillConfig(
        size="hero",
        show_text=True,
        show_icon=True,
        clickable=True,
        animation_duration=500
    )
    return StatusPill(status, config, on_click)


def create_compact_status_pill(status: ServerStatus = ServerStatus.UNKNOWN,
                              on_click: Optional[Callable] = None) -> StatusPill:
    """Create a compact status pill for dense layouts"""
    config = StatusPillConfig(
        size="compact",
        show_text=True,
        show_icon=True,
        clickable=True,
        animation_duration=200
    )
    return StatusPill(status, config, on_click)