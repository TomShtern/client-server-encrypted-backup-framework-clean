#!/usr/bin/env python3
"""
Purpose: Main dashboard view matching the screenshot layout
Logic: Aggregates data from various sources for display
UI: Professional grid layout with Material Design 3 styling
"""

import flet as ft
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
import psutil
import os
from flet_server_gui.utils.server_bridge import ServerBridge
from flet_server_gui.utils.thread_safe_ui import ThreadSafeUIUpdater, ui_safe_update
from flet_server_gui.components.base_component import BaseComponent
from flet_server_gui.core.semantic_colors import get_status_color
from flet_server_gui.ui.layouts.responsive_fixes import ResponsiveLayoutFixes, fix_content_clipping, fix_button_clickable_areas, ensure_windowed_compatibility

# Unified theme system - consolidated theme functionality
from flet_server_gui.core.theme_compatibility import TOKENS


class DashboardView(BaseComponent):
    def __init__(self, page: ft.Page, server_bridge: Optional[ServerBridge] = None, dialog_system: Optional[Any] = None, toast_manager: Optional[Any] = None) -> None:
        # Initialize parent BaseComponent
        super().__init__(page, dialog_system, toast_manager)
        
        self.page = page
        self.server_bridge = server_bridge or ServerBridge()
        self.controls = []
        
        # Semantic colors will be used from existing system
        
        # Initialize thread-safe UI updater
        self.ui_updater = ThreadSafeUIUpdater(page)
        self._updater_started = False
        
        # Status card refs for real-time updates
        self.server_status_text = ft.Ref[ft.Text]()
        self.server_address_text = ft.Ref[ft.Text]()
        self.server_uptime_text = ft.Ref[ft.Text]()
        
        self.connected_clients_text = ft.Ref[ft.Text]()
        self.total_clients_text = ft.Ref[ft.Text]()
        self.active_transfers_text = ft.Ref[ft.Text]()
        
        self.total_transferred_text = ft.Ref[ft.Text]()
        self.transfer_rate_text = ft.Ref[ft.Text]()
        
        self.last_cleanup_text = ft.Ref[ft.Text]()
        self.files_cleaned_text = ft.Ref[ft.Text]()
        
        self.activity_log_container = ft.Ref[ft.Column]()
        
        # Control panel refs
        self.start_button = ft.Ref[ft.ElevatedButton]()
        self.stop_button = ft.Ref[ft.ElevatedButton]()
        self.restart_button = ft.Ref[ft.ElevatedButton]()
        
        self.log_entries = []
        self.max_log_entries = 10
    
    def _create_status_row(self, label: str, value_ref: ft.Ref[ft.Text], default_value: str, value_color: Optional[str] = None) -> ft.Row:
        """Create a consistent status row with label and value"""
        return ft.Row([
            ft.Text(f"{label}:", 
                   style=ft.TextThemeStyle.BODY_MEDIUM, 
                   color=TOKENS['outline']),
            ft.Container(expand=True),
            ft.Text(ref=value_ref, 
                   value=default_value, 
                   style=ft.TextThemeStyle.BODY_MEDIUM,
                   weight=ft.FontWeight.W_500,
                   color=value_color or TOKENS['on_surface'])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
    def build(self) -> ft.Control:
        """Build the dashboard view with professional responsive design"""
        # Header with timestamp and system theme integration - eliminated outer container
        header = ft.ResponsiveRow([
            ft.Text(
                "Encrypted Backup Server",
                style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                weight=ft.FontWeight.W_600,
                color=TOKENS['on_surface'],
                col={"sm": 12, "md": 8}
            ),
            ft.Column([
                ft.Text(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=TOKENS['outline']
                ),
                ft.Row([
                    ft.Text("Server", style=ft.TextThemeStyle.BODY_SMALL, color=TOKENS['outline']),
                    ft.Icon(
                        ft.Icons.CIRCLE,
                        color=get_status_color("error"),
                        size=12
                    ),
                    ft.Text("Offline", style=ft.TextThemeStyle.BODY_SMALL, color=get_status_color("error"))
                ], spacing=6, alignment=ft.MainAxisAlignment.END)
            ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4,
            col={"sm": 12, "md": 4})
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER,
        padding=ft.padding.only(bottom=20),
        margin=ft.margin.only(bottom=8))
        
        # Main content with proper responsive grid - eliminated container wrappers
        content = ft.Column([
            # Status cards row - cards directly in responsive row
            ft.ResponsiveRow([
                ft.Column([self._create_server_status_card()], col={"xs": 12, "sm": 12, "md": 4, "lg": 4}),
                ft.Column([self._create_client_stats_card()], col={"xs": 12, "sm": 12, "md": 4, "lg": 4}),
                ft.Column([self._create_control_panel_card()], col={"xs": 12, "sm": 12, "md": 4, "lg": 4})
            ], spacing=12, run_spacing=12),
            
            # Stats row - cards directly in responsive row
            ft.ResponsiveRow([
                ft.Column([self._create_transfer_stats_card()], col={"xs": 12, "sm": 12, "md": 6, "lg": 6}),
                ft.Column([self._create_maintenance_card()], col={"xs": 12, "sm": 12, "md": 6, "lg": 6})
            ], spacing=12, run_spacing=12),
            
            # Chart and log row - cards directly in responsive row
            ft.ResponsiveRow([
                ft.Column([self._create_performance_chart_card()], col={"xs": 12, "sm": 12, "md": 8, "lg": 8}),
                ft.Column([self._create_activity_log_card()], col={"xs": 12, "sm": 12, "md": 4, "lg": 4})
            ], spacing=12, run_spacing=12)
        ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)
        
        return ft.Container(content=ft.Column([
                header,
                content
            ], spacing=0, expand=True),
            padding=ft.padding.all(16),
            expand=True
        )
    
    def _create_server_status_card(self) -> ft.Card:
        """Create the Server Status card with Material Design 3 styling"""
        return ft.Card(
            content=ft.Column([
                ft.Text("Server Status", 
                       style=ft.TextThemeStyle.TITLE_LARGE, 
                       weight=ft.FontWeight.W_500),
                ft.Divider(height=1, color=TOKENS['outline']),
                # Direct Column without container wrapper
                ft.Column([
                    self._create_status_row("Status", self.server_status_text, "Stopped", get_status_color("error")),
                    self._create_status_row("Address", self.server_address_text, "N/A"),
                    self._create_status_row("Uptime", self.server_uptime_text, "00:00:00")
                ], spacing=12, padding=ft.padding.symmetric(vertical=8))
            ], spacing=16, padding=ft.padding.all(20)),
            elevation=2,
            margin=ft.margin.all(0)
        )
    
    def _create_client_stats_card(self) -> ft.Card:
        """Create the Client Stats card with Material Design 3 styling"""
        return ft.Card(
            content=ft.Column([
                ft.Text("Client Stats", 
                       style=ft.TextThemeStyle.TITLE_LARGE, 
                       weight=ft.FontWeight.W_500),
                ft.Divider(height=1, color=TOKENS['outline']),
                # Direct Column without container wrapper
                ft.Column([
                    # Prominent connected clients display - direct Column styling
                    ft.Column([
                        ft.Text(ref=self.connected_clients_text, value="0",
                               style=ft.TextThemeStyle.DISPLAY_SMALL,
                               weight=ft.FontWeight.W_600,
                               color=TOKENS['primary'],
                               text_align=ft.TextAlign.CENTER),
                        ft.Text("Connected Clients",
                               style=ft.TextThemeStyle.BODY_MEDIUM,
                               color=TOKENS['outline'],
                               text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                    spacing=4, padding=ft.padding.symmetric(vertical=8)),
                    ft.Divider(height=1, color=TOKENS['outline']),
                    self._create_status_row("Total Registered", self.total_clients_text, "0"),
                    self._create_status_row("Active Transfers", self.active_transfers_text, "0")
                ], spacing=12, padding=ft.padding.symmetric(vertical=8))
            ], spacing=16, padding=ft.padding.all(20)),
            elevation=2,
            margin=ft.margin.all(0)
        )
    
    def _create_control_panel_card(self) -> ft.Card:
        """Create the Control Panel card with Material Design 3 buttons"""
        return ft.Card(
            content=ft.Column([
                ft.Text("Control Panel", 
                       style=ft.TextThemeStyle.TITLE_LARGE, 
                       weight=ft.FontWeight.W_500),
                ft.Divider(height=1, color=TOKENS['outline']),
                # Direct Column without container wrapper
                ft.Column([
                    # Primary actions row - buttons directly in responsive row
                    ft.ResponsiveRow([
                        ft.FilledButton(
                            ref=self.start_button,
                            content=ft.Row([
                                ft.Icon(ft.Icons.PLAY_ARROW, size=20),
                                ft.Text("Start", weight=ft.FontWeight.W_500)
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                            bgcolor=get_status_color("success"),
                            on_click=self._on_start_server,
                            col={"sm": 12, "md": 6},
                            expand=True
                        ),
                        ft.FilledButton(
                            ref=self.stop_button,
                            content=ft.Row([
                                ft.Icon(ft.Icons.STOP, size=20),
                                ft.Text("Stop", weight=ft.FontWeight.W_500)
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                            bgcolor=get_status_color("error"),
                            on_click=self._on_stop_server,
                            col={"sm": 12, "md": 6},
                            expand=True
                        )
                    ], spacing=12, run_spacing=8),
                    
                    # Secondary actions - button directly in responsive row
                    ft.ResponsiveRow([
                        ft.OutlinedButton(
                            ref=self.restart_button,
                            content=ft.Row([
                                ft.Icon(ft.Icons.REFRESH, size=20, color=get_status_color("warning")),
                                ft.Text("Restart", weight=ft.FontWeight.W_500, color=get_status_color("warning"))
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                            on_click=self._on_restart_server,
                            col={"sm": 12, "md": 12},
                            expand=True
                        )
                    ], spacing=12, run_spacing=8),
                    
                    # Utility actions - buttons directly in responsive row
                    ft.ResponsiveRow([
                        ft.OutlinedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.STORAGE, size=18, color=get_status_color("info")),
                                ft.Text("Backup DB", weight=ft.FontWeight.W_400, color=get_status_color("info"))
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                            on_click=self._on_backup_db,
                            col={"sm": 12, "md": 6},
                            expand=True
                        ),
                        ft.TextButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.EXIT_TO_APP, size=18, color=TOKENS['outline']),
                                ft.Text("Exit GUI", weight=ft.FontWeight.W_400, color=TOKENS['outline'])
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                            on_click=self._on_exit_gui,
                            col={"sm": 12, "md": 6},
                            expand=True
                        )
                    ], spacing=12, run_spacing=8)
                ], spacing=16, padding=ft.padding.symmetric(vertical=8))
            ], spacing=16, padding=ft.padding.all(20)),
            elevation=2,
            margin=ft.margin.all(0)
        )
    
    def _create_transfer_stats_card(self) -> ft.Card:
        """Create the Transfer Stats card with Material Design 3 styling"""
        return ft.Card(
            content=ft.Column([
                ft.Text("Transfer Stats", 
                       style=ft.TextThemeStyle.TITLE_LARGE, 
                       weight=ft.FontWeight.W_500),
                ft.Divider(height=1, color=TOKENS['outline']),
                # Direct Column without container wrapper
                ft.Column([
                    self._create_status_row("Total Transferred", self.total_transferred_text, "0 MB", TOKENS['primary']),
                    self._create_status_row("Transfer Rate", self.transfer_rate_text, "0 KB/s")
                ], spacing=16, padding=ft.padding.symmetric(vertical=8))
            ], spacing=16, padding=ft.padding.all(20)),
            elevation=2,
            surface_tint_color=TOKENS['primary'],
            margin=ft.margin.all(0)
        )
    
    def _create_maintenance_card(self) -> ft.Card:
        """Create the Maintenance card with Material Design 3 styling"""
        return ft.Card(
            content=ft.Column([
                ft.Text("Maintenance", 
                       style=ft.TextThemeStyle.TITLE_LARGE, 
                       weight=ft.FontWeight.W_500),
                ft.Divider(height=1, color=TOKENS['outline']),
                # Direct Column without container wrapper
                ft.Column([
                    self._create_status_row("Last Cleanup", self.last_cleanup_text, "Never"),
                    self._create_status_row("Files Cleaned", self.files_cleaned_text, "0")
                ], spacing=16, padding=ft.padding.symmetric(vertical=8))
            ], spacing=16, padding=ft.padding.all(20)),
            elevation=2,
            surface_tint_color=TOKENS['primary'],
            margin=ft.margin.all(0)
        )
    
    def _create_performance_chart_card(self) -> ft.Card:
        """Create the Live System Performance card with responsive chart"""
        return ft.Card(
            content=ft.Column([
                ft.Text("Live System Performance", 
                       style=ft.TextThemeStyle.TITLE_LARGE, 
                       weight=ft.FontWeight.W_500),
                ft.Divider(height=1, color=TOKENS['outline']),
                # Chart content - eliminated 3 layers of container nesting
                ft.Column([
                    # Chart area with gradient background - direct styling
                    ft.Container(
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_center,
                            end=ft.alignment.bottom_center,
                            colors=[TOKENS['surface_variant'], "transparent"]
                        ),
                        border_radius=8,
                        height=180,
                        # Chart content directly inside - no wrapper container
                        content=ft.Column([
                            ft.Text("System Performance Monitoring",
                                   style=ft.TextThemeStyle.BODY_LARGE,
                                   color=TOKENS['outline'],
                                   text_align=ft.TextAlign.CENTER),
                            # Direct Row without container wrapper
                            ft.Row([
                                ft.Icon(ft.Icons.TRENDING_UP, 
                                       color=TOKENS['primary'], size=48),
                                ft.Column([
                                    ft.Text("CPU: 12%", 
                                           style=ft.TextThemeStyle.BODY_MEDIUM,
                                           color=get_status_color("info")),
                                    ft.Text("Memory: 34%", 
                                           style=ft.TextThemeStyle.BODY_MEDIUM,
                                           color=get_status_color("info"))
                                ], spacing=4)
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True)
                        ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER),
                        alignment=ft.alignment.center,
                        padding=ft.padding.all(16)
                    ),
                    # Chart legend - eliminated container wrappers
                    ft.Row([
                        ft.Row([
                            ft.Container(width=12, height=3, bgcolor=get_status_color("info"), border_radius=2),
                            ft.Text("CPU %", style=ft.TextThemeStyle.BODY_SMALL)
                        ], spacing=6),
                        ft.Row([
                            ft.Container(width=12, height=3, bgcolor=get_status_color("info"), border_radius=2),
                            ft.Text("Memory %", style=ft.TextThemeStyle.BODY_SMALL)
                        ], spacing=6)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=24)
                ], spacing=12, padding=ft.padding.symmetric(vertical=8))
            ], spacing=16, padding=ft.padding.all(20)),
            elevation=2,
            surface_tint_color=TOKENS['primary'],
            margin=ft.margin.all(0)
        )
    
    def _create_activity_log_card(self) -> ft.Card:
        """Create the Activity Log card with responsive design"""
        return ft.Card(
            content=ft.Column([
                ft.Row([
                    ft.Text("Activity Log", 
                           style=ft.TextThemeStyle.TITLE_LARGE, 
                           weight=ft.FontWeight.W_500),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CLEAR_ALL,
                        tooltip="Clear log",
                        icon_size=18,
                        on_click=self._clear_activity_log
                    )
                ]),
                ft.Divider(height=1, color=TOKENS['outline']),
                # Direct Column without container wrapper
                ft.Column(
                    ref=self.activity_log_container,
                    controls=[
                        # Initial placeholder without container wrapper
                        ft.Text(
                            "No recent activity",
                            style=ft.TextThemeStyle.BODY_SMALL,
                            color=TOKENS['outline'],
                            italic=True,
                            text_align=ft.TextAlign.CENTER
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=2,
                    expand=True,
                    padding=ft.padding.all(8),
                    border_radius=8
                )
            ], spacing=16, expand=True, padding=ft.padding.all(20)),
            elevation=2,
            surface_tint_color=TOKENS['primary'],
            margin=ft.margin.all(0)
        )
    
    # Event handlers for control panel buttons
    async def _on_start_server(self, e: ft.ControlEvent) -> None:
        """Handle start server button with real functionality"""
        self.add_log_entry("System", "Starting backup server...", "INFO")
        try:
            success = await self.server_bridge.start_server()
            if success:
                self.add_log_entry("System", "Server started successfully!", "SUCCESS")
                await self._async_update_server_status()
            else:
                self.add_log_entry("System", "Failed to start server", "ERROR")
        except Exception as ex:
            self.add_log_entry("System", f"Start error: {str(ex)}", "ERROR")
        
    async def _on_stop_server(self, e: ft.ControlEvent) -> None:
        """Handle stop server button with real functionality"""
        self.add_log_entry("System", "Stopping backup server...", "INFO")
        try:
            success = await self.server_bridge.stop_server()
            if success:
                self.add_log_entry("System", "Server stopped successfully", "SUCCESS")
                await self._async_update_server_status()
            else:
                self.add_log_entry("System", "Failed to stop server", "ERROR")
        except Exception as ex:
            self.add_log_entry("System", f"Stop error: {str(ex)}", "ERROR")
        
    async def _on_restart_server(self, e: ft.ControlEvent) -> None:
        """Handle restart server button with real functionality"""
        self.add_log_entry("System", "Restarting backup server...", "INFO")
        try:
            success = await self.server_bridge.restart_server()
            if success:
                self.add_log_entry("System", "Server restarted successfully!", "SUCCESS")
                await self._async_update_server_status()
            else:
                self.add_log_entry("System", "Failed to restart server", "ERROR")
        except Exception as ex:
            self.add_log_entry("System", f"Restart error: {str(ex)}", "ERROR")
        
    async def _on_backup_db(self, e: ft.ControlEvent) -> None:
        """Handle backup database button with real functionality"""
        self.add_log_entry("Database", "Creating database backup...", "INFO")
        try:
            success = await self.server_bridge.backup_database()
            if success:
                self.add_log_entry("Database", "Database backup completed", "SUCCESS")
            else:
                self.add_log_entry("Database", "Database backup failed", "ERROR")
        except Exception as ex:
            self.add_log_entry("Database", f"Backup error: {str(ex)}", "ERROR")
        
    async def _on_exit_gui(self, e: ft.ControlEvent) -> None:
        """Handle exit GUI button"""
        self.add_log_entry("System", "Closing GUI...", "INFO")
        # Use the correct method to close the window
        if hasattr(self.page, 'window_destroy'):
            self.page.window_destroy()
        else:
            # Fallback: try to close via window visibility
            self.page.window_visible = False
            self.page.update()
    
    def _clear_activity_log(self, e: ft.ControlEvent) -> None:
        """Clear the activity log with visual feedback"""
        if self.activity_log_container.current:
            # Clear existing entries
            self.activity_log_container.current.controls.clear()
            
            # Add cleared message
            cleared_msg = ft.Container(
                content=ft.Text(
                    "Activity log cleared",
                    style=ft.TextThemeStyle.BODY_SMALL,
                    color=TOKENS['outline'],
                    italic=True
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.all(16),
                animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                opacity=0
            )
            
            self.activity_log_container.current.controls.append(cleared_msg)
            self.page.update()
            
            # Animate in the cleared message
            cleared_msg.opacity = 1
            self.page.update()
            
            # Add system log entry
            self.add_log_entry("System", "Activity log manually cleared", "INFO")
    
    def add_log_entry(self, source: str, message: str, level: str = "INFO") -> None:
        """Add entry to activity log with smooth animations"""
        if not self.activity_log_container.current:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Professional color coding with Material Design 3 colors
        color_map = {
            "INFO": TOKENS['on_surface'],
            "SUCCESS": get_status_color("success"),
            "WARNING": get_status_color("warning"),
            "ERROR": get_status_color("error")
        }
        
        # Icon mapping for log levels
        icon_map = {
            "INFO": ft.Icons.INFO_OUTLINE,
            "SUCCESS": ft.Icons.CHECK_CIRCLE_OUTLINE,
            "WARNING": ft.Icons.WARNING_AMBER,
            "ERROR": ft.Icons.ERROR_OUTLINE
        }
        
        # Create sophisticated log entry with icon and hover effect
        log_entry = ft.Container(
            content=ft.Row([
                ft.Icon(
                    icon_map.get(level, ft.Icons.INFO_OUTLINE),
                    size=14,
                    color=color_map.get(level, TOKENS['on_surface'])
                ),
                ft.Text(
                    f"[{timestamp}]",
                    style=ft.TextThemeStyle.BODY_SMALL,
                    color=TOKENS['outline'],
                    weight=ft.FontWeight.W_400
                ),
                ft.Text(
                    source,
                    style=ft.TextThemeStyle.BODY_SMALL,
                    color=color_map.get(level, TOKENS['on_surface']),
                    weight=ft.FontWeight.W_500
                ),
                ft.Text(":", style=ft.TextThemeStyle.BODY_SMALL, color=TOKENS['outline']),
                ft.Text(
                    message,
                    style=ft.TextThemeStyle.BODY_SMALL,
                    color=TOKENS['on_surface'],
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True
                )
            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            opacity=0,  # Start invisible for animation
            scale=ft.Scale(0.9)  # Start slightly smaller
        )
        
        # Keep only recent entries
        controls = self.activity_log_container.current.controls
        if len(controls) >= self.max_log_entries and controls:
            oldest = controls[0]
            oldest.opacity = 0
            oldest.scale = ft.Scale(0.8)
            # Thread-safe UI update
            if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
                self.ui_updater.queue_update(lambda: None)
            else:
                self.page.update()
            # Remove after animation
            asyncio.create_task(self._remove_old_entry())
        
        # Remove placeholder if present
        if (len(controls) == 1 and 
            hasattr(controls[0], 'content') and 
            hasattr(controls[0].content, 'value')):
            controls.clear()
            
        controls.append(log_entry)
        # Thread-safe UI update
        if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
            self.ui_updater.queue_update(lambda: None)
        else:
            self.page.update()
        
        # Animate in the new entry
        def animate_entry():
            log_entry.opacity = 1
            log_entry.scale = ft.Scale(1.0)
        
        # Thread-safe UI update
        if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
            self.ui_updater.queue_update(animate_entry)
        else:
            animate_entry()
            self.page.update()
    
    async def _remove_old_entry(self) -> None:
        """Remove old entry after fade animation"""
        await asyncio.sleep(0.3)
        if (self.activity_log_container.current and 
            len(self.activity_log_container.current.controls) >= self.max_log_entries):
            self.activity_log_container.current.controls.pop(0)
            # Thread-safe UI update
            if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
                self.ui_updater.queue_update(lambda: None)
            else:
                self.page.update()
    
    def start_dashboard_sync(self) -> None:
        """Initialize dashboard UI elements (synchronous part)"""
        # Add welcome messages to demonstrate the polished log system
        self.add_log_entry("System", "Dashboard initialized successfully", "SUCCESS")
        self.add_log_entry("Theme", "Material Design 3 theme applied", "INFO")
        self.add_log_entry("Monitor", "Starting real-time monitoring...", "INFO")
    
    async def start_dashboard_async(self) -> None:
        """Initialize dashboard background tasks (asynchronous part)"""
        # Start the thread-safe UI updater
        if not self._updater_started:
            await self.ui_updater.start()
            self._updater_started = True
            self.add_log_entry("UI", "Thread-safe UI updater started", "SUCCESS")
        
        # Wait briefly for UI to be fully ready
        await asyncio.sleep(1)
        self.add_log_entry("Server", "Real-time updates active", "SUCCESS")
        
        # Start the background monitoring loop
        asyncio.create_task(self._real_time_update_loop())
    
    async def _real_time_update_loop(self) -> None:
        """Background task for real-time dashboard updates"""
        update_count = 0
        while True:
            try:
                # Update every 5 seconds
                await asyncio.sleep(5)
                update_count += 1
                
                # Update system stats
                await self._update_system_stats()
                
                # Periodic status messages
                if update_count % 6 == 0:  # Every 30 seconds
                    self.add_log_entry("Monitor", "System status check completed", "SUCCESS")
                elif update_count % 12 == 0:  # Every minute
                    await self._check_server_health()
                    
            except Exception as e:
                self.add_log_entry("Monitor", f"Update error: {str(e)}", "ERROR")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def _update_system_stats(self) -> None:
        """Update system performance statistics"""
        try:
            # Get real system stats
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            
            # Update display values (if refs are available)
            # This is where real data would be updated
            
            # Occasionally add performance log entries
            if cpu_percent > 80:
                self.add_log_entry("Performance", f"High CPU usage: {cpu_percent:.1f}%", "WARNING")
            elif memory.percent > 85:
                self.add_log_entry("Performance", f"High memory usage: {memory.percent:.1f}%", "WARNING")
                
        except Exception as e:
            self.add_log_entry("Performance", f"Stats update failed: {str(e)}", "ERROR")
    
    async def _check_server_health(self) -> None:
        """Perform server health check"""
        try:
            if self.server_bridge:
                server_info = await self.server_bridge.get_server_status()
                if hasattr(server_info, 'running') and server_info.running:
                    self.add_log_entry("Health", "Server health check: OK", "SUCCESS")
                else:
                    self.add_log_entry("Health", "Server appears offline", "WARNING")
            else:
                self.add_log_entry("Health", "Server bridge not available", "WARNING")
        except Exception as e:
            self.add_log_entry("Health", f"Health check failed: {str(e)}", "ERROR")
    
    def update_data(self) -> None:
        """Update dashboard data with real system information"""
        try:
            # Update system performance data
            if hasattr(self, 'performance_chart'):
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                # Update chart data here
                
            # Update server status via server_bridge
            if self.server_bridge:
                # Use page.run_task if available, otherwise check for event loop
                if hasattr(self.page, 'run_task'):
                    self.page.run_task(self._async_update_server_status())
                else:
                    # Check if we're in an async context
                    try:
                        loop = asyncio.get_running_loop()
                        if loop.is_running():
                            asyncio.create_task(self._async_update_server_status())
                    except RuntimeError:
                        # No event loop running, skip async task creation
                        pass
                
        except Exception as e:
            self.add_log_entry("System", f"Error updating data: {str(e)}", "ERROR")
    
    async def _async_update_server_status(self) -> None:
        """Async update server status display"""
        try:
            server_info = await self.server_bridge.get_server_status()
            if server_info and self.server_status_text.current:
                if is_running := getattr(server_info, 'running', False):
                    self.server_status_text.current.value = "Online"
                    self.server_status_text.current.color = get_status_color("success")
                    if self.server_address_text.current:
                        self.server_address_text.current.value = f"{getattr(server_info, 'host', 'localhost')}:{getattr(server_info, 'port', '1256')}"
                else:
                    self.server_status_text.current.value = "Offline"
                    self.server_status_text.current.color = get_status_color("error")
                    if self.server_address_text.current:
                        self.server_address_text.current.value = "N/A"

                # Update client counts
                if self.connected_clients_text.current:
                    self.connected_clients_text.current.value = str(getattr(server_info, 'connected_clients', 0))
                if self.total_clients_text.current:
                    self.total_clients_text.current.value = str(getattr(server_info, 'total_clients', 0))

                # Thread-safe UI update
                if hasattr(self, 'ui_updater') and self.ui_updater.is_running():
                    self.ui_updater.queue_update(lambda: None)
                else:
                    self.page.update()

        except Exception as e:
            self.add_log_entry("Status", f"Failed to update server status: {str(e)}", "ERROR")
