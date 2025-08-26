"""
Purpose: Main dashboard view matching the screenshot layout
Logic: Aggregates data from various sources for display
UI: Professional grid layout with Material Design 3 styling
"""

import flet as ft
import asyncio
from datetime import datetime
from typing import Optional
import psutil
import os
from flet_server_gui.utils.server_bridge import ServerBridge

class DashboardView:
    def __init__(self, page: ft.Page, server_bridge: Optional[ServerBridge] = None):
        self.page = page
        self.server_bridge = server_bridge or ServerBridge()
        self.controls = []
        
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
    
    def _create_status_row(self, label: str, value_ref: ft.Ref[ft.Text], default_value: str, value_color=None) -> ft.Row:
        """Create a consistent status row with label and value"""
        return ft.Row([
            ft.Text(f"{label}:", 
                   style=ft.TextThemeStyle.BODY_MEDIUM, 
                   color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Container(expand=True),
            ft.Text(ref=value_ref, 
                   value=default_value, 
                   style=ft.TextThemeStyle.BODY_MEDIUM,
                   weight=ft.FontWeight.W_500,
                   color=value_color or ft.Colors.ON_SURFACE)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
    def build(self):
        """Build the dashboard view with professional responsive design"""
        # Header with timestamp and system theme integration
        header = ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(
                    content=ft.Text(
                        "Encrypted Backup Server",
                        style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.ON_SURFACE
                    ),
                    col={"sm": 12, "md": 8},
                    alignment=ft.alignment.center_left
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        ),
                        ft.Row([
                            ft.Text("Server", style=ft.TextThemeStyle.BODY_SMALL, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Icon(
                                ft.Icons.CIRCLE,
                                color=ft.Colors.ERROR,
                                size=12
                            ),
                            ft.Text("Offline", style=ft.TextThemeStyle.BODY_SMALL, color=ft.Colors.ERROR)
                        ], spacing=6, alignment=ft.MainAxisAlignment.END)
                    ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4),
                    col={"sm": 12, "md": 4},
                    alignment=ft.alignment.center_right
                )
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(bottom=20),
            margin=ft.margin.only(bottom=8)
        )
        
        # Main content with proper responsive grid
        content = ft.Column([
            # Status cards row - equal height cards
            ft.ResponsiveRow([
                ft.Container(
                    content=self._create_server_status_card(),
                    col={"xs": 12, "sm": 12, "md": 4, "lg": 4},
                    expand=False
                ),
                ft.Container(
                    content=self._create_client_stats_card(),
                    col={"xs": 12, "sm": 12, "md": 4, "lg": 4},
                    expand=False
                ),
                ft.Container(
                    content=self._create_control_panel_card(),
                    col={"xs": 12, "sm": 12, "md": 4, "lg": 4},
                    expand=False
                )
            ], spacing=12, run_spacing=12),
            
            # Stats row
            ft.ResponsiveRow([
                ft.Container(
                    content=self._create_transfer_stats_card(),
                    col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                    expand=False
                ),
                ft.Container(
                    content=self._create_maintenance_card(),
                    col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                    expand=False
                )
            ], spacing=12, run_spacing=12),
            
            # Chart and log row
            ft.ResponsiveRow([
                ft.Container(
                    content=self._create_performance_chart_card(),
                    col={"xs": 12, "sm": 12, "md": 8, "lg": 8},
                    expand=False
                ),
                ft.Container(
                    content=self._create_activity_log_card(),
                    col={"xs": 12, "sm": 12, "md": 4, "lg": 4},
                    expand=False
                )
            ], spacing=12, run_spacing=12)
        ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)
        
        return ft.Container(
            content=ft.Column([
                header,
                content
            ], spacing=0, expand=True),
            padding=ft.padding.all(16),
            expand=True
        )
    
    def _create_server_status_card(self):
        """Create the Server Status card with Material Design 3 styling"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Server Status", 
                           style=ft.TextThemeStyle.TITLE_LARGE, 
                           weight=ft.FontWeight.W_500),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Container(
                        content=ft.Column([
                            self._create_status_row("Status", self.server_status_text, "Stopped", ft.Colors.ERROR),
                            self._create_status_row("Address", self.server_address_text, "N/A"),
                            self._create_status_row("Uptime", self.server_uptime_text, "00:00:00")
                        ], spacing=12),
                        padding=ft.padding.symmetric(vertical=8)
                    )
                ], spacing=16),
                padding=ft.padding.all(20),
                width=None,  # Let it flex
                expand=False
            ),
            elevation=2,
            surface_tint_color=ft.Colors.PRIMARY,
            margin=ft.margin.all(0)
        )
    
    def _create_client_stats_card(self):
        """Create the Client Stats card with Material Design 3 styling"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Client Stats", 
                           style=ft.TextThemeStyle.TITLE_LARGE, 
                           weight=ft.FontWeight.W_500),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Container(
                        content=ft.Column([
                            # Prominent connected clients display
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(ref=self.connected_clients_text, value="0",
                                           style=ft.TextThemeStyle.DISPLAY_SMALL,
                                           weight=ft.FontWeight.W_600,
                                           color=ft.Colors.PRIMARY,
                                           text_align=ft.TextAlign.CENTER),
                                    ft.Text("Connected Clients",
                                           style=ft.TextThemeStyle.BODY_MEDIUM,
                                           color=ft.Colors.ON_SURFACE_VARIANT,
                                           text_align=ft.TextAlign.CENTER)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                                alignment=ft.alignment.center,
                                padding=ft.padding.symmetric(vertical=8)
                            ),
                            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                            self._create_status_row("Total Registered", self.total_clients_text, "0"),
                            self._create_status_row("Active Transfers", self.active_transfers_text, "0")
                        ], spacing=12),
                        padding=ft.padding.symmetric(vertical=8)
                    )
                ], spacing=16),
                padding=ft.padding.all(20),
                width=None,
                expand=False
            ),
            elevation=2,
            surface_tint_color=ft.Colors.PRIMARY,
            margin=ft.margin.all(0)
        )
    
    def _create_control_panel_card(self):
        """Create the Control Panel card with Material Design 3 buttons"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Control Panel", 
                           style=ft.TextThemeStyle.TITLE_LARGE, 
                           weight=ft.FontWeight.W_500),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Container(
                        content=ft.Column([
                            # Primary actions row
                            ft.ResponsiveRow([
                                ft.Container(
                                    content=ft.FilledButton(
                                        ref=self.start_button,
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.PLAY_ARROW, size=20),
                                            ft.Text("Start", weight=ft.FontWeight.W_500)
                                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                                        bgcolor=ft.Colors.GREEN_600,
                                        color=ft.Colors.WHITE,
                                        on_click=self._on_start_server
                                    ),
                                    col={"sm": 12, "md": 6},
                                    expand=True
                                ),
                                ft.Container(
                                    content=ft.FilledButton(
                                        ref=self.stop_button,
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.STOP, size=20),
                                            ft.Text("Stop", weight=ft.FontWeight.W_500)
                                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                                        bgcolor=ft.Colors.RED_600,
                                        color=ft.Colors.WHITE,
                                        on_click=self._on_stop_server
                                    ),
                                    col={"sm": 12, "md": 6},
                                    expand=True
                                )
                            ], spacing=12, run_spacing=8),
                            
                            # Secondary actions
                            ft.ResponsiveRow([
                                ft.Container(
                                    content=ft.OutlinedButton(
                                        ref=self.restart_button,
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.REFRESH, size=20, color=ft.Colors.ORANGE_600),
                                            ft.Text("Restart", weight=ft.FontWeight.W_500, color=ft.Colors.ORANGE_600)
                                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                                        on_click=self._on_restart_server
                                    ),
                                    col={"sm": 12, "md": 12},
                                    expand=True
                                )
                            ], spacing=12, run_spacing=8),
                            
                            # Utility actions
                            ft.ResponsiveRow([
                                ft.Container(
                                    content=ft.OutlinedButton(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.STORAGE, size=18, color=ft.Colors.PURPLE_600),
                                            ft.Text("Backup DB", weight=ft.FontWeight.W_400, color=ft.Colors.PURPLE_600)
                                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                                        on_click=self._on_backup_db
                                    ),
                                    col={"sm": 12, "md": 6},
                                    expand=True
                                ),
                                ft.Container(
                                    content=ft.TextButton(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.EXIT_TO_APP, size=18, color=ft.Colors.ON_SURFACE_VARIANT),
                                            ft.Text("Exit GUI", weight=ft.FontWeight.W_400, color=ft.Colors.ON_SURFACE_VARIANT)
                                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                                        on_click=self._on_exit_gui
                                    ),
                                    col={"sm": 12, "md": 6},
                                    expand=True
                                )
                            ], spacing=12, run_spacing=8)
                        ], spacing=16),
                        padding=ft.padding.symmetric(vertical=8)
                    )
                ], spacing=16),
                padding=ft.padding.all(20),
                expand=False
            ),
            elevation=2,
            surface_tint_color=ft.Colors.PRIMARY,
            margin=ft.margin.all(0)
        )
    
    def _create_transfer_stats_card(self):
        """Create the Transfer Stats card with Material Design 3 styling"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Transfer Stats", 
                           style=ft.TextThemeStyle.TITLE_LARGE, 
                           weight=ft.FontWeight.W_500),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Container(
                        content=ft.Column([
                            self._create_status_row("Total Transferred", self.total_transferred_text, "0 MB", ft.Colors.PRIMARY),
                            self._create_status_row("Transfer Rate", self.transfer_rate_text, "0 KB/s")
                        ], spacing=16),
                        padding=ft.padding.symmetric(vertical=8)
                    )
                ], spacing=16),
                padding=ft.padding.all(20),
                expand=False
            ),
            elevation=2,
            surface_tint_color=ft.Colors.PRIMARY,
            margin=ft.margin.all(0)
        )
    
    def _create_maintenance_card(self):
        """Create the Maintenance card with Material Design 3 styling"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Maintenance", 
                           style=ft.TextThemeStyle.TITLE_LARGE, 
                           weight=ft.FontWeight.W_500),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Container(
                        content=ft.Column([
                            self._create_status_row("Last Cleanup", self.last_cleanup_text, "Never"),
                            self._create_status_row("Files Cleaned", self.files_cleaned_text, "0")
                        ], spacing=16),
                        padding=ft.padding.symmetric(vertical=8)
                    )
                ], spacing=16),
                padding=ft.padding.all(20),
                expand=False
            ),
            elevation=2,
            surface_tint_color=ft.Colors.PRIMARY,
            margin=ft.margin.all(0)
        )
    
    def _create_performance_chart_card(self):
        """Create the Live System Performance card with responsive chart"""
        # Create a professional performance visualization
        chart_content = ft.Container(
            content=ft.Column([
                # Chart placeholder with gradient background
                ft.Container(
                    content=ft.Stack([
                        # Background gradient
                        ft.Container(
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_center,
                                end=ft.alignment.bottom_center,
                                colors=[ft.Colors.BLUE_100, ft.Colors.TRANSPARENT]
                            ),
                            border_radius=8
                        ),
                        # Chart lines simulation
                        ft.Container(
                            content=ft.Column([
                                ft.Text("System Performance Monitoring",
                                       style=ft.TextThemeStyle.BODY_LARGE,
                                       color=ft.Colors.ON_SURFACE_VARIANT,
                                       text_align=ft.TextAlign.CENTER),
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.TRENDING_UP, 
                                               color=ft.Colors.PRIMARY, size=48),
                                        ft.Column([
                                            ft.Text("CPU: 12%", 
                                                   style=ft.TextThemeStyle.BODY_MEDIUM,
                                                   color=ft.Colors.BLUE_600),
                                            ft.Text("Memory: 34%", 
                                                   style=ft.TextThemeStyle.BODY_MEDIUM,
                                                   color=ft.Colors.PURPLE_600)
                                        ], spacing=4)
                                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=16),
                                    expand=True
                                )
                            ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            alignment=ft.alignment.center,
                            padding=ft.padding.all(16)
                        )
                    ]),
                    height=180,  # Flexible height
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
                ),
                # Chart legend
                ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Container(width=12, height=3, bgcolor=ft.Colors.BLUE_600, border_radius=2),
                            ft.Text("CPU %", style=ft.TextThemeStyle.BODY_SMALL)
                        ], spacing=6)
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.Container(width=12, height=3, bgcolor=ft.Colors.PURPLE_600, border_radius=2),
                            ft.Text("Memory %", style=ft.TextThemeStyle.BODY_SMALL)
                        ], spacing=6)
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=24)
            ], spacing=12),
            padding=ft.padding.symmetric(vertical=8)
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Live System Performance", 
                           style=ft.TextThemeStyle.TITLE_LARGE, 
                           weight=ft.FontWeight.W_500),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    chart_content
                ], spacing=16),
                padding=ft.padding.all(20),
                expand=False
            ),
            elevation=2,
            surface_tint_color=ft.Colors.PRIMARY,
            margin=ft.margin.all(0)
        )
    
    def _create_activity_log_card(self):
        """Create the Activity Log card with responsive design"""
        return ft.Card(
            content=ft.Container(
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
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Container(
                        content=ft.Column(
                            ref=self.activity_log_container,
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        "No recent activity",
                                        style=ft.TextThemeStyle.BODY_SMALL,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                        italic=True
                                    ),
                                    alignment=ft.alignment.center,
                                    padding=ft.padding.all(16)
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO,
                            spacing=2,
                            expand=True
                        ),
                        expand=True,  # Let it flex with the card
                        padding=ft.padding.all(8),
                        border_radius=8,
                        bgcolor=ft.Colors.SURFACE_TINT,
                        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
                    )
                ], spacing=16, expand=True),
                padding=ft.padding.all(20),
                expand=False
            ),
            elevation=2,
            surface_tint_color=ft.Colors.PRIMARY,
            margin=ft.margin.all(0)
        )
    
    # Event handlers for control panel buttons
    async def _on_start_server(self, e):
        """Handle start server button"""
        self.add_log_entry("System", "Starting server...", "INFO")
        # Add server start logic here
        
    async def _on_stop_server(self, e):
        """Handle stop server button"""
        self.add_log_entry("System", "Stopping server...", "INFO")
        # Add server stop logic here
        
    async def _on_restart_server(self, e):
        """Handle restart server button"""
        self.add_log_entry("System", "Restarting server...", "INFO")
        # Add server restart logic here
        
    async def _on_backup_db(self, e):
        """Handle backup database button"""
        self.add_log_entry("Database", "Creating database backup...", "INFO")
        # Add database backup logic here
        
    async def _on_exit_gui(self, e):
        """Handle exit GUI button"""
        self.add_log_entry("System", "Closing GUI...", "INFO")
        self.page.window_close()
    
    def _clear_activity_log(self, e):
        """Clear the activity log"""
        if self.activity_log_container.current:
            self.activity_log_container.current.controls.clear()
            self.activity_log_container.current.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Activity log cleared",
                        style=ft.TextThemeStyle.BODY_SMALL,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        italic=True
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(16)
                )
            )
            self.page.update()
    
    def add_log_entry(self, source: str, message: str, level: str = "INFO"):
        """Add entry to activity log with smooth animations"""
        if not self.activity_log_container.current:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Professional color coding with Material Design 3 colors
        color_map = {
            "INFO": ft.Colors.ON_SURFACE,
            "SUCCESS": ft.Colors.GREEN_600,
            "WARNING": ft.Colors.AMBER_600,
            "ERROR": ft.Colors.ERROR
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
                    color=color_map.get(level, ft.Colors.ON_SURFACE)
                ),
                ft.Text(
                    f"[{timestamp}]",
                    style=ft.TextThemeStyle.BODY_SMALL,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    weight=ft.FontWeight.W_400
                ),
                ft.Text(
                    source,
                    style=ft.TextThemeStyle.BODY_SMALL,
                    color=color_map.get(level, ft.Colors.ON_SURFACE),
                    weight=ft.FontWeight.W_500
                ),
                ft.Text(":", style=ft.TextThemeStyle.BODY_SMALL, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(
                    message,
                    style=ft.TextThemeStyle.BODY_SMALL,
                    color=ft.Colors.ON_SURFACE,
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
        if len(controls) >= self.max_log_entries:
            # Animate out the oldest entry
            if controls:
                oldest = controls[0]
                oldest.opacity = 0
                oldest.scale = ft.Scale(0.8)
                self.page.update()
                # Remove after animation
                asyncio.create_task(self._remove_old_entry())
        
        # Remove placeholder if present
        if (len(controls) == 1 and 
            hasattr(controls[0], 'content') and 
            hasattr(controls[0].content, 'value')):
            controls.clear()
            
        controls.append(log_entry)
        self.page.update()
        
        # Animate in the new entry
        log_entry.opacity = 1
        log_entry.scale = ft.Scale(1.0)
        self.page.update()
    
    async def _remove_old_entry(self):
        """Remove old entry after fade animation"""
        await asyncio.sleep(0.3)
        if (self.activity_log_container.current and 
            len(self.activity_log_container.current.controls) >= self.max_log_entries):
            self.activity_log_container.current.controls.pop(0)
            self.page.update()
    
    def start_dashboard(self):
        """Initialize dashboard with welcome messages and start real-time updates"""
        # Add welcome messages to demonstrate the polished log system
        self.add_log_entry("System", "Dashboard initialized successfully", "SUCCESS")
        self.add_log_entry("Theme", "Material Design 3 theme applied", "INFO")
        self.add_log_entry("Server", "Monitoring server status...", "INFO")
        
        # Schedule background update task to start after a brief delay
        # This ensures the event loop is fully established
        try:
            # Try to create the task, but don't fail if event loop isn't ready
            asyncio.create_task(self._delayed_start_updates())
        except RuntimeError:
            # Event loop not ready yet, log will show anyway
            self.add_log_entry("Monitor", "Real-time updates will start when ready", "INFO")
    
    async def _delayed_start_updates(self):
        """Start updates after a brief delay to ensure event loop is ready"""
        await asyncio.sleep(2)  # Give the GUI time to fully initialize
        asyncio.create_task(self._real_time_update_loop())
    
    async def _real_time_update_loop(self):
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
    
    async def _update_system_stats(self):
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
    
    async def _check_server_health(self):
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
    
    def update_data(self):
        """Update dashboard data with real system information"""
        try:
            # Update system performance data
            if hasattr(self, 'performance_chart'):
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                # Update chart data here
                
            # Update server status via server_bridge
            if self.server_bridge:
                asyncio.create_task(self._async_update_server_status())
                
        except Exception as e:
            self.add_log_entry("System", f"Error updating data: {str(e)}", "ERROR")
    
    async def _async_update_server_status(self):
        """Async update server status display"""
        try:
            server_info = await self.server_bridge.get_server_status()
            if server_info and self.server_status_text.current:
                # Update status displays
                is_running = getattr(server_info, 'running', False)
                if is_running:
                    self.server_status_text.current.value = "Online"
                    self.server_status_text.current.color = ft.Colors.GREEN_600
                    if self.server_address_text.current:
                        self.server_address_text.current.value = f"{getattr(server_info, 'host', 'localhost')}:{getattr(server_info, 'port', '1256')}"
                else:
                    self.server_status_text.current.value = "Offline"
                    self.server_status_text.current.color = ft.Colors.ERROR
                    if self.server_address_text.current:
                        self.server_address_text.current.value = "N/A"
                        
                # Update client counts
                if self.connected_clients_text.current:
                    self.connected_clients_text.current.value = str(getattr(server_info, 'connected_clients', 0))
                if self.total_clients_text.current:
                    self.total_clients_text.current.value = str(getattr(server_info, 'total_clients', 0))
                
                self.page.update()
                
        except Exception as e:
            self.add_log_entry("Status", f"Failed to update server status: {str(e)}", "ERROR")