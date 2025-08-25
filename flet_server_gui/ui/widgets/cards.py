#!/usr/bin/env python3
"""
UI Widgets - Cards

Purpose: Reusable status and information display cards
Logic: Data formatting and status calculation
UI: Card layouts, Material Design 3 styling, animations
"""

import flet as ft
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flet_server_gui.utils.server_bridge import ServerBridge, ServerInfo


class ClientStatsCard:
    """Client statistics card with connection metrics"""
    
    def __init__(self, server_bridge: "ServerBridge", page: ft.Page):
        self.server_bridge = server_bridge
        self.page = page
        
        # UI components with Refs for dynamic updates
        self.connected_count = ft.Ref[ft.Text]()
        self.total_count = ft.Ref[ft.Text]()
        self.transfers_count = ft.Ref[ft.Text]()
        self.connection_indicator = ft.Ref[ft.Icon]()

    def build(self) -> ft.Card:
        """Build the client statistics card with responsive layout"""
        header = ft.Row([
            ft.Icon(ref=self.connection_indicator, name=ft.Icons.PEOPLE_ALT, size=24),
            ft.Text("Client Statistics", style=ft.TextThemeStyle.TITLE_LARGE)
        ], spacing=12)
        
        primary_metric = ft.Container(
            content=ft.Column([
                ft.Text(ref=self.connected_count, value="0", 
                       style=ft.TextThemeStyle.DISPLAY_MEDIUM, weight=ft.FontWeight.BOLD),
                ft.Text("Connected", style=ft.TextThemeStyle.LABEL_LARGE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            padding=ft.padding.all(12),
            border_radius=12,
            expand=True
        )
        
        secondary_metrics = ft.ResponsiveRow([
            ft.Column([
                ft.Text(ref=self.total_count, value="0", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text("Total Registered", style=ft.TextThemeStyle.BODY_MEDIUM)
            ], col={"sm": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
               spacing=4, expand=True),
            ft.Column([
                ft.Text(ref=self.transfers_count, value="0", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text("Active Transfers", style=ft.TextThemeStyle.BODY_MEDIUM)
            ], col={"sm": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
               spacing=4, expand=True)
        ], spacing=16, expand=True)
        
        card_content = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                primary_metric,
                secondary_metrics
            ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(20),
            expand=True
        )
        
        return ft.Card(content=card_content, elevation=1, expand=True)

    def update_stats(self, server_info: "ServerInfo"):
        """Update statistics with new data and animations"""
        if not self.connected_count.current:
            return
        
        self.connected_count.current.value = str(server_info.connected_clients)
        self.total_count.current.value = str(server_info.total_clients)
        self.transfers_count.current.value = str(server_info.active_transfers)
        
        # Enhanced icon animation for client count changes
        if hasattr(self.page.theme, 'color_scheme'):
            if server_info.connected_clients > 0:
                self.connection_indicator.current.color = self.page.theme.color_scheme.primary
                
                # Add pulse animation for new connections
                if hasattr(self.connected_count.current, '_last_value'):
                    if int(server_info.connected_clients) > int(self.connected_count.current._last_value):
                        # Pulse animation
                        self.connection_indicator.current.scale = ft.Scale(1.3)
                        self.page.update()
                        asyncio.create_task(self._reset_icon_scale())
                        
                self.connected_count.current._last_value = str(server_info.connected_clients)
            else:
                self.connection_indicator.current.color = self.page.theme.color_scheme.outline
        else:
            self.connection_indicator.current.color = ft.Colors.BLUE if server_info.connected_clients > 0 else ft.Colors.GREY
            
        self.page.update()

    async def _reset_icon_scale(self):
        """Reset icon scale after animation"""
        await asyncio.sleep(0.3)
        if self.connection_indicator.current:
            self.connection_indicator.current.scale = ft.Scale(1.0)
            self.page.update()

    async def update_real_time(self):
        """Update stats with real-time data from server bridge"""
        server_info = await self.server_bridge.get_server_status()
        self.update_stats(server_info)


class ServerStatusCard:
    """Server status card with real-time updates and self-updating uptime"""
    
    def __init__(self, server_bridge: "ServerBridge", page: ft.Page):
        self.server_bridge = server_bridge
        self.page = page
        self.server_info = None
        self._is_running = False
        self._uptime_task = None
        self._ticker_started = False

        # UI components with Refs for dynamic updates
        self.status_chip = ft.Ref[ft.Chip]()
        self.status_icon = ft.Ref[ft.Icon]()
        self.address_text = ft.Ref[ft.Text]()
        self.uptime_text = ft.Ref[ft.Text]()
        self.clients_text = ft.Ref[ft.Text]()

    def build(self) -> ft.Card:
        """Build the server status card with responsive layout"""
        header_row = ft.ResponsiveRow([
            ft.Row([
                ft.Icon(ref=self.status_icon, name=ft.Icons.RADIO_BUTTON_OFF, size=20),
                ft.Text("Server Status", style=ft.TextThemeStyle.TITLE_LARGE)
            ], col={"sm": 12, "md": 8}, spacing=12, expand=True),
            ft.Container(
                content=ft.Chip(ref=self.status_chip, 
                              label=ft.Text("OFFLINE", weight=ft.FontWeight.BOLD), 
                              elevation=0),
                col={"sm": 12, "md": 4},
                alignment=ft.alignment.center_right,
                expand=True
            )
        ], expand=True)
        
        details_column = ft.Column([
            ft.Text(ref=self.address_text, value="Address: N/A", 
                   style=ft.TextThemeStyle.BODY_MEDIUM),
            ft.Text(f"Port: {getattr(self.server_info, 'port', 'N/A') if self.server_info else 'N/A'}", 
                   style=ft.TextThemeStyle.BODY_MEDIUM),
            ft.Text(ref=self.uptime_text, value="Uptime: 00:00:00", 
                   style=ft.TextThemeStyle.BODY_MEDIUM),
            ft.Text(ref=self.clients_text, value="Connected: 0 clients", 
                   style=ft.TextThemeStyle.BODY_MEDIUM)
        ], spacing=8, expand=True)
        
        card_content = ft.Container(
            content=ft.Column([header_row, ft.Divider(), details_column], spacing=16),
            padding=ft.padding.all(20),
            expand=True
        )
        
        return ft.Card(content=card_content, elevation=1, expand=True)

    def update_status(self, server_info):
        """Update the status card with new server information"""
        if not self.status_chip.current:
            return

        self.server_info = server_info
        self._is_running = getattr(server_info, 'running', False)

        if self._is_running:
            self.status_chip.current.label.value = "ONLINE"
            # Use theme colors for status indication
            if hasattr(self.page.theme, 'color_scheme'):
                self.status_chip.current.bgcolor = self.page.theme.color_scheme.primary_container
                self.status_chip.current.label.color = self.page.theme.color_scheme.on_primary_container
                self.status_icon.current.color = self.page.theme.color_scheme.primary
            else:
                self.status_icon.current.color = ft.Colors.GREEN
                
            self.status_icon.current.name = ft.Icons.RADIO_BUTTON_CHECKED
            self.address_text.current.value = f"Address: {getattr(server_info, 'host', 'N/A')}:{getattr(server_info, 'port', 'N/A')}"
            self.clients_text.current.value = f"Connected: {getattr(server_info, 'connected_clients', 0)} clients"
        else:
            self.status_chip.current.label.value = "OFFLINE"
            # Use theme colors for status indication
            if hasattr(self.page.theme, 'color_scheme'):
                self.status_chip.current.bgcolor = self.page.theme.color_scheme.secondary_container
                self.status_chip.current.label.color = self.page.theme.color_scheme.on_secondary_container
                self.status_icon.current.color = self.page.theme.color_scheme.outline
            else:
                self.status_icon.current.color = ft.Colors.GREY
                
            self.status_icon.current.name = ft.Icons.RADIO_BUTTON_OFF
            self.address_text.current.value = "Address: N/A"
            self.uptime_text.current.value = "Uptime: 00:00:00"
            self.clients_text.current.value = "Connected: 0 clients"
            
        self.page.update()

    async def uptime_ticker(self):
        """A dedicated task to update the uptime every second"""
        while True:
            if (self._is_running and 
                getattr(self.server_info, 'uptime_start', None) and 
                self.uptime_text.current):
                
                uptime = datetime.now() - self.server_info.uptime_start
                hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                self.uptime_text.current.value = f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
                try:
                    await self.page.update_async()
                except Exception:
                    pass
            await asyncio.sleep(1)

    async def update_real_time(self):
        """Update status with real-time data from server bridge and start ticker if needed"""
        if not self._ticker_started:
            asyncio.create_task(self.uptime_ticker())
            self._ticker_started = True

        server_info = await self.server_bridge.get_server_status()
        self.update_status(server_info)


class ActivityLogCard:
    """Activity log card with real-time server activity and animations"""
    
    def __init__(self):
        self.log_entries: List[Dict[str, Any]] = []
        self.max_entries = 50
        self.log_container = ft.Ref[ft.Column]()
        self.page: Optional[ft.Page] = None

    def build(self) -> ft.Card:
        """Build the activity log card with responsive design"""
        header = ft.ResponsiveRow([
            ft.Row([
                ft.Icon(ft.Icons.TIMELINE),
                ft.Text("Activity Log", style=ft.TextThemeStyle.TITLE_LARGE)
            ], col={"sm": 12, "md": 8}, spacing=12, expand=True),
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.CLEAR_ALL,
                    tooltip="Clear activity log",
                    on_click=self.clear_log
                ),
                col={"sm": 12, "md": 4},
                alignment=ft.alignment.center_right,
                expand=True
            )
        ], expand=True)
        
        log_viewer = ft.Container(
            content=ft.Column(
                ref=self.log_container,
                scroll=ft.ScrollMode.ALWAYS,
                spacing=4,
                controls=[ft.Text("No activity yet.", italic=True)],
                expand=True
            ),
            border_radius=8,
            padding=ft.padding.all(12),
            expand=True,
            height=280
        )
        
        card_content = ft.Container(
            content=ft.Column([header, ft.Divider(), log_viewer], spacing=12, expand=True),
            padding=ft.padding.all(20),
            expand=True
        )
        
        return ft.Card(content=card_content, elevation=1, expand=True)

    def add_entry(self, source: str, message: str, level: str = "INFO"):
        """Add a new log entry with enhanced animations"""
        if not self.log_container.current or not self.page:
            return

        timestamp = datetime.now()
        entry_data = {"timestamp": timestamp, "source": source, "message": message, "level": level}
        
        self.log_entries.insert(0, entry_data)
        if len(self.log_entries) > self.max_entries:
            self.log_entries.pop()

        # Clear placeholder if it exists
        if (len(self.log_container.current.controls) == 1 and 
            isinstance(self.log_container.current.controls[0], ft.Text)):
            self.log_container.current.controls.clear()

        visual_entry = self.create_log_entry_visual(entry_data)
        
        # Add animation properties
        visual_entry.opacity = 0
        visual_entry.animate_opacity = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        visual_entry.offset = ft.Offset(0, 0.5)
        visual_entry.animate_offset = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        
        self.log_container.current.controls.insert(0, visual_entry)
        
        if len(self.log_container.current.controls) > self.max_entries:
            self.log_container.current.controls.pop()
        
        self.page.update()
        
        # Animate in with enhanced entrance effect
        visual_entry.opacity = 1
        visual_entry.offset = ft.Offset(0, 0)
        self.page.update()

    def create_log_entry_visual(self, entry_data: Dict[str, Any]) -> ft.Control:
        """Create visual representation of a log entry using theme colors"""
        # Level colors and icons
        if hasattr(self.page, 'theme') and self.page.theme and self.page.theme.color_scheme:
            color_scheme = self.page.theme.color_scheme
            level_colors = {
                "INFO": color_scheme.on_surface_variant,
                "SUCCESS": color_scheme.primary,
                "WARNING": color_scheme.tertiary,
                "ERROR": color_scheme.error
            }
            time_color = color_scheme.on_surface_variant
            message_color = color_scheme.on_surface
        else:
            # Fallback colors
            level_colors = {
                "INFO": ft.Colors.GREY_600,
                "SUCCESS": ft.Colors.GREEN_600,
                "WARNING": ft.Colors.ORANGE_600,
                "ERROR": ft.Colors.RED_600
            }
            time_color = ft.Colors.GREY_600
            message_color = ft.Colors.GREY_800
        
        level_icons = {
            "INFO": ft.Icons.INFO_OUTLINE,
            "SUCCESS": ft.Icons.CHECK_CIRCLE_OUTLINE,
            "WARNING": ft.Icons.WARNING_AMBER,
            "ERROR": ft.Icons.ERROR_OUTLINE
        }
        
        level = entry_data["level"]
        color = level_colors.get(level, level_colors["INFO"])
        icon = level_icons.get(level, ft.Icons.INFO_OUTLINE)
        
        time_str = entry_data["timestamp"].strftime("%H:%M:%S")
        
        return ft.ResponsiveRow([
            ft.Container(
                content=ft.Icon(icon, color=color, size=16),
                col={"sm": 1, "md": 1},
                alignment=ft.alignment.center
            ),
            ft.Container(
                content=ft.Text(f"[{time_str}]", style=ft.TextThemeStyle.BODY_SMALL, 
                              color=time_color),
                col={"sm": 2, "md": 2}
            ),
            ft.Container(
                content=ft.Text(entry_data["source"], style=ft.TextThemeStyle.BODY_SMALL, 
                              weight=ft.FontWeight.BOLD, color=color),
                col={"sm": 3, "md": 2}
            ),
            ft.Container(
                content=ft.Text(entry_data["message"], style=ft.TextThemeStyle.BODY_SMALL, 
                              color=message_color),
                col={"sm": 6, "md": 7},
                expand=True
            )
        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    async def clear_log(self, e=None):
        """Clear all log entries with enhanced animation"""
        self.log_entries.clear()
        if self.log_container.current:
            # Enhanced clear animation - fade out all entries
            if self.log_container.current.controls:
                for control in self.log_container.current.controls:
                    control.opacity = 1
                    control.animate_opacity = ft.Animation(200, ft.AnimationCurve.EASE_IN)
                self.page.update()
                
                for control in self.log_container.current.controls:
                    control.opacity = 0
                self.page.update()
                
                await asyncio.sleep(0.25)
            
            # Clear and add confirmation message
            self.log_container.current.controls.clear()
            confirmation = ft.Text("Log cleared.", italic=True, opacity=0)
            confirmation.animate_opacity = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
            self.log_container.current.controls.append(confirmation)
            self.page.update()
            confirmation.opacity = 1
            self.page.update()
            
            # Add system entry with animation
            self.add_entry("System", "Activity log cleared", "INFO")
            self.page.update()

    def set_page(self, page: ft.Page):
        """Sets the page context for the component"""
        self.page = page
        # Initialize with a welcome message once the page is set
        self.add_entry("System", "Activity log initialized", "INFO")


class EnhancedStatsCard:
    """Enhanced statistics card with visual indicators and progress bars"""
    
    def __init__(self, title: str = "Statistics Overview", page: ft.Page = None):
        self.title = title
        self.page = page
        self.stats_data = {}
        
        # UI component references
        self.cpu_progress = ft.Ref[ft.ProgressBar]()
        self.cpu_text = ft.Ref[ft.Text]()
        self.memory_progress = ft.Ref[ft.ProgressBar]()
        self.memory_text = ft.Ref[ft.Text]()
        self.net_up_text = ft.Ref[ft.Text]()
        self.net_down_text = ft.Ref[ft.Text]()
        self.storage_progress = ft.Ref[ft.ProgressBar]()
        self.storage_text = ft.Ref[ft.Text]()
    
    def build(self) -> ft.Card:
        """Build the enhanced statistics content with responsive design"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.INSERT_CHART_OUTLINED, size=24),
            ft.Text(self.title, style=ft.TextThemeStyle.TITLE_LARGE),
        ], spacing=12)
        
        # Statistics grid with responsive layout
        stats_grid = ft.ResponsiveRow([
            # CPU Usage with progress bar
            ft.Column([
                ft.Text("CPU Usage", style=ft.TextThemeStyle.LABEL_LARGE),
                ft.ProgressBar(
                    ref=self.cpu_progress,
                    value=0.0,
                    bar_height=8,
                    border_radius=4
                ),
                ft.Text(ref=self.cpu_text, value="0%", 
                       style=ft.TextThemeStyle.BODY_MEDIUM, 
                       color=ft.Colors.ON_SURFACE_VARIANT)
            ], col={"sm": 12, "md": 6, "lg": 3}, expand=True),
            
            # Memory Usage with progress bar
            ft.Column([
                ft.Text("Memory Usage", style=ft.TextThemeStyle.LABEL_LARGE),
                ft.ProgressBar(
                    ref=self.memory_progress,
                    value=0.0,
                    bar_height=8,
                    border_radius=4
                ),
                ft.Text(ref=self.memory_text, value="0%", 
                       style=ft.TextThemeStyle.BODY_MEDIUM, 
                       color=ft.Colors.ON_SURFACE_VARIANT)
            ], col={"sm": 12, "md": 6, "lg": 3}, expand=True),
            
            # Network Traffic
            ft.Column([
                ft.Text("Network", style=ft.TextThemeStyle.LABEL_LARGE),
                ft.Row([
                    ft.Icon(ft.Icons.ARROW_UPWARD, size=16, color=ft.Colors.GREEN),
                    ft.Text(ref=self.net_up_text, value="0 KB/s", style=ft.TextThemeStyle.BODY_MEDIUM),
                ], spacing=4),
                ft.Row([
                    ft.Icon(ft.Icons.ARROW_DOWNWARD, size=16, color=ft.Colors.BLUE),
                    ft.Text(ref=self.net_down_text, value="0 KB/s", style=ft.TextThemeStyle.BODY_MEDIUM),
                ], spacing=4)
            ], col={"sm": 12, "md": 6, "lg": 3}, expand=True),
            
            # Storage Usage
            ft.Column([
                ft.Text("Storage", style=ft.TextThemeStyle.LABEL_LARGE),
                ft.ProgressBar(
                    ref=self.storage_progress,
                    value=0.0,
                    bar_height=8,
                    border_radius=4
                ),
                ft.Text(ref=self.storage_text, value="0%", 
                       style=ft.TextThemeStyle.BODY_MEDIUM, 
                       color=ft.Colors.ON_SURFACE_VARIANT)
            ], col={"sm": 12, "md": 6, "lg": 3}, expand=True),
        ], spacing=20, expand=True)
        
        # Quick actions with responsive layout
        quick_actions = ft.ResponsiveRow([
            ft.Container(
                content=ft.ElevatedButton(
                    text="Refresh",
                    icon=ft.Icons.REFRESH,
                    on_click=self._on_refresh
                ),
                col={"sm": 12, "md": 6},
                expand=True
            ),
            ft.Container(
                content=ft.ElevatedButton(
                    text="View Details",
                    icon=ft.Icons.VISIBILITY,
                    on_click=self._on_view_details
                ),
                col={"sm": 12, "md": 6},
                expand=True
            )
        ], spacing=12, expand=True)

        card_content = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                stats_grid,
                ft.Divider(),
                quick_actions
            ], spacing=16),
            padding=ft.padding.all(20),
            expand=True
        )
        
        return ft.Card(content=card_content, elevation=1, expand=True)
    
    def update_stats(self, cpu_percent: float = 0.0, 
                     memory_percent: float = 0.0,
                     network_up: str = "0 KB/s",
                     network_down: str = "0 KB/s",
                     storage_percent: float = 0.0):
        """Update statistics with new data"""
        if not self.cpu_progress.current:
            return
            
        # Update CPU usage
        self.cpu_progress.current.value = cpu_percent / 100.0
        self.cpu_text.current.value = f"{cpu_percent:.1f}%"
        
        # Update Memory usage
        self.memory_progress.current.value = memory_percent / 100.0
        self.memory_text.current.value = f"{memory_percent:.1f}%"
        
        # Update Network traffic
        self.net_up_text.current.value = network_up
        self.net_down_text.current.value = network_down
        
        # Update Storage usage
        self.storage_progress.current.value = storage_percent / 100.0
        self.storage_text.current.value = f"{storage_percent:.1f}%"
        
        if self.page:
            self.page.update()

    def _on_refresh(self, e):
        """Handle refresh button click"""
        # Placeholder for refresh functionality
        pass

    def _on_view_details(self, e):
        """Handle view details button click"""
        # Placeholder for view details functionality
        pass


# Factory functions for easy card creation
def create_client_stats_card(server_bridge: "ServerBridge", page: ft.Page) -> ClientStatsCard:
    """Create a client statistics card"""
    return ClientStatsCard(server_bridge, page)

def create_server_status_card(server_bridge: "ServerBridge", page: ft.Page) -> ServerStatusCard:
    """Create a server status card"""
    return ServerStatusCard(server_bridge, page)

def create_activity_log_card() -> ActivityLogCard:
    """Create an activity log card"""
    return ActivityLogCard()

def create_enhanced_stats_card(title: str = "Statistics Overview", page: ft.Page = None) -> EnhancedStatsCard:
    """Create an enhanced statistics card"""
    return EnhancedStatsCard(title=title, page=page)