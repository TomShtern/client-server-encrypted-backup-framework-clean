#!/usr/bin/env python3
"""
Settings View for FletV2
An improved implementation using ft.UserControl for better state management.
"""

import flet as ft
import json
import asyncio
from utils.debug_setup import get_logger
from pathlib import Path
from datetime import datetime
from config import SETTINGS_FILE, ASYNC_DELAY, MIN_PORT, MAX_PORT, MIN_MAX_CLIENTS

logger = get_logger(__name__)


class SettingsManager:
    """Manages application settings with async operations."""
    
    def __init__(self, settings_file: str = SETTINGS_FILE):
        self.settings_file = Path(settings_file)
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file (simple JSON handling)."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            else:
                # Default settings
                return {
                    'server': {
                        'port': 1256,
                        'host': '127.0.0.1',
                        'max_clients': 50,
                        'log_level': 'INFO'
                    },
                    'gui': {
                        'theme_mode': 'dark',
                        'auto_refresh': True,
                        'notifications': True
                    },
                    'monitoring': {
                        'enabled': True,
                        'interval': 2,
                        'alerts': True
                    }
                }
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return {
                'server': {'port': 1256, 'host': '127.0.0.1'},
                'gui': {'theme_mode': 'dark'},
                'monitoring': {'enabled': True}
            }
    
    async def save_settings_async(self, settings_data):
        """Async function to save settings."""
        try:
            # Simulate async operation
            await asyncio.sleep(ASYNC_DELAY)
            with open(self.settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    
    async def export_settings_async(self, settings_data, backup_file):
        """Async function to export settings."""
        try:
            # Simulate async operation
            await asyncio.sleep(ASYNC_DELAY)
            with open(backup_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return False


class SettingsView(ft.UserControl):
    """
    Settings view using ft.UserControl for better state management.
    """
    
    def __init__(self, server_bridge, page: ft.Page):
        super().__init__()
        self.server_bridge = server_bridge
        self.page = page
        self.settings_manager = SettingsManager()
        self.current_settings = self.settings_manager.settings
        self.is_saving = False
        self.last_saved = None
        
        # UI References
        self.last_saved_text = None
        self.server_port_field = None
        self.server_host_field = None
        self.max_clients_field = None
        self.log_level_dropdown = None
        self.theme_mode_switch = None
        self.auto_refresh_switch = None
        self.notifications_switch = None
        self.monitoring_enabled_switch = None
        self.monitoring_interval_field = None
        self.alerts_switch = None
        
    def build(self):
        """Build the settings view UI."""
        self.last_saved_text = ft.Text(
            value="Last saved: Never",
            size=12,
            color=ft.Colors.ON_SURFACE
        )
        
        # Server Settings Fields
        self.server_port_field = ft.TextField(
            label="Server Port",
            value=str(self.current_settings['server'].get('port', 1256)),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            on_change=self._on_port_change
        )
        
        self.server_host_field = ft.TextField(
            label="Server Host",
            value=self.current_settings['server'].get('host', '127.0.0.1'),
            expand=True,
            on_change=self._on_host_change
        )
        
        self.max_clients_field = ft.TextField(
            label="Max Clients",
            value=str(self.current_settings['server'].get('max_clients', 50)),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            on_change=self._on_max_clients_change
        )
        
        self.log_level_dropdown = ft.Dropdown(
            label="Log Level",
            value=self.current_settings['server'].get('log_level', 'INFO'),
            options=[
                ft.dropdown.Option("DEBUG", "Debug"),
                ft.dropdown.Option("INFO", "Info"),
                ft.dropdown.Option("WARNING", "Warning"),
                ft.dropdown.Option("ERROR", "Error")
            ],
            width=200,
            on_change=self._on_log_level_change
        )
        
        # GUI Settings Fields
        self.theme_mode_switch = ft.Switch(
            label="Dark Mode",
            value=self.current_settings['gui'].get('theme_mode', 'dark') == 'dark',
            on_change=self._on_theme_toggle
        )
        
        self.auto_refresh_switch = ft.Switch(
            label="Auto Refresh",
            value=self.current_settings['gui'].get('auto_refresh', True),
            on_change=self._on_auto_refresh_change
        )
        
        self.notifications_switch = ft.Switch(
            label="Show Notifications",
            value=self.current_settings['gui'].get('notifications', True),
            on_change=self._on_notifications_change
        )
        
        self.monitoring_enabled_switch = ft.Switch(
            label="Enable System Monitoring",
            value=self.current_settings['monitoring'].get('enabled', True),
            on_change=self._on_monitoring_enabled_change
        )
        
        self.monitoring_interval_field = ft.TextField(
            label="Monitoring Interval (seconds)",
            value=str(self.current_settings['monitoring'].get('interval', 2)),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            on_change=self._on_monitoring_interval_change
        )
        
        self.alerts_switch = ft.Switch(
            label="Performance Alerts",
            value=self.current_settings['monitoring'].get('alerts', True),
            on_change=self._on_alerts_change
        )
        
        # Build the main view
        return ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.SETTINGS, size=24),
                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                self.last_saved_text
            ]),
            ft.Divider(),
            # Action buttons
            ft.ResponsiveRow([
                ft.Column([
                    ft.ElevatedButton(
                        "Save Settings",
                        icon=ft.Icons.SAVE,
                        on_click=self._on_save_settings,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.PRIMARY,
                            color=ft.Colors.ON_PRIMARY
                        )
                    )
                ], col={"sm": 12, "md": 3}),
                ft.Column([
                    ft.OutlinedButton(
                        "Reset All",
                        icon=ft.Icons.RESTORE,
                        on_click=self._on_reset_settings
                    )
                ], col={"sm": 12, "md": 3}),
                ft.Column([
                    ft.OutlinedButton(
                        "Export Backup",
                        icon=ft.Icons.DOWNLOAD,
                        on_click=self._on_export_settings
                    )
                ], col={"sm": 12, "md": 3}),
                ft.Column([
                    ft.TextButton(
                        "Import Settings",
                        icon=ft.Icons.UPLOAD,
                        on_click=self._on_import_settings
                    )
                ], col={"sm": 12, "md": 3})
            ]),
            ft.Divider(),
            # Settings tabs using Flet's built-in Tabs component (this is the RIGHT way!)
            ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        text="Server",
                        icon=ft.Icons.SETTINGS,
                        content=self._create_server_settings()
                    ),
                    ft.Tab(
                        text="GUI",
                        icon=ft.Icons.PALETTE,
                        content=self._create_gui_settings()
                    ),
                    ft.Tab(
                        text="Monitoring",
                        icon=ft.Icons.MONITOR_HEART,
                        content=self._create_monitoring_settings()
                    )
                ],
                expand=True
            )
        ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)
    
    def _create_server_settings(self):
        """Create server settings form."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Server Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.server_port_field,
                    self.server_host_field,
                    self.max_clients_field,
                    self.log_level_dropdown
                ], spacing=15),
                padding=20
            )
        )
    
    def _create_gui_settings(self):
        """Create GUI settings form."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("GUI Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([
                        ft.Text("Theme Mode:", size=16, weight=ft.FontWeight.W_500),
                        self.theme_mode_switch
                    ]),
                    self.auto_refresh_switch,
                    self.notifications_switch
                ], spacing=15),
                padding=20
            )
        )
    
    def _create_monitoring_settings(self):
        """Create monitoring settings form."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Monitoring Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.monitoring_enabled_switch,
                    self.monitoring_interval_field,
                    self.alerts_switch
                ], spacing=15),
                padding=20
            )
        )
    
    # Event handlers for server settings
    def _on_port_change(self, e):
        try:
            port = int(e.control.value)
            if MIN_PORT <= port <= MAX_PORT:
                self.current_settings['server']['port'] = port
                logger.info(f"Server port changed to: {port}")
                e.control.error_text = None
                e.control.update()
                self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Port updated to {port}"), bgcolor=ft.Colors.GREEN)
            else:
                e.control.error_text = f"Port must be between {MIN_PORT}-{MAX_PORT}"
                e.control.update()
                return
        except ValueError:
            e.control.error_text = "Invalid port number"
            e.control.update()
            return
        e.control.error_text = None
        e.control.update()
        self.page.snack_bar.open = True
        self.page.update()
    
    def _on_host_change(self, e):
        host = e.control.value.strip()
        if host:
            self.current_settings['server']['host'] = host
            logger.info(f"Server host changed to: {host}")
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Host updated to {host}"), bgcolor=ft.Colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_max_clients_change(self, e):
        try:
            max_clients = int(e.control.value)
            if max_clients >= MIN_MAX_CLIENTS:
                self.current_settings['server']['max_clients'] = max_clients
                logger.info(f"Max clients changed to: {max_clients}")
                e.control.error_text = None
                e.control.update()
                self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Max clients updated to {max_clients}"), bgcolor=ft.Colors.GREEN)
            else:
                e.control.error_text = f"Must be at least {MIN_MAX_CLIENTS}"
                e.control.update()
                return
        except ValueError:
            e.control.error_text = "Invalid number"
            e.control.update()
            return
        e.control.error_text = None
        e.control.update()
        self.page.snack_bar.open = True
        self.page.update()
    
    def _on_log_level_change(self, e):
        level = e.control.value
        self.current_settings['server']['log_level'] = level
        logger.info(f"Log level changed to: {level}")
        self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Log level updated to {level}"), bgcolor=ft.Colors.GREEN)
        self.page.snack_bar.open = True
        self.page.update()
    
    # Event handlers for GUI settings
    def _on_theme_toggle(self, e):
        new_mode = "light" if self.current_settings['gui']['theme_mode'] == "dark" else "dark"
        self.current_settings['gui']['theme_mode'] = new_mode
        # Apply theme change immediately using Flet's built-in theme system
        self.page.theme_mode = ft.ThemeMode.LIGHT if new_mode == "light" else ft.ThemeMode.DARK
        self.page.update()
        self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Theme switched to {new_mode} mode"), bgcolor=ft.Colors.BLUE)
        self.page.snack_bar.open = True
        self.page.update()
    
    def _on_auto_refresh_change(self, e):
        self.current_settings['gui']['auto_refresh'] = e.control.value
        logger.info(f"Auto refresh set to: {e.control.value}")
        self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Auto refresh {'enabled' if e.control.value else 'disabled'}"), bgcolor=ft.Colors.GREEN)
        self.page.snack_bar.open = True
        self.page.update()
    
    def _on_notifications_change(self, e):
        self.current_settings['gui']['notifications'] = e.control.value
        logger.info(f"Notifications set to: {e.control.value}")
        self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Notifications {'enabled' if e.control.value else 'disabled'}"), bgcolor=ft.Colors.GREEN)
        self.page.snack_bar.open = True
        self.page.update()
    
    # Event handlers for monitoring settings
    def _on_monitoring_enabled_change(self, e):
        self.current_settings['monitoring']['enabled'] = e.control.value
        logger.info(f"System monitoring {'enabled' if e.control.value else 'disabled'}")
        self.page.snack_bar = ft.SnackBar(content=ft.Text(f"System monitoring {'enabled' if e.control.value else 'disabled'}"), bgcolor=ft.Colors.GREEN)
        self.page.snack_bar.open = True
        self.page.update()
    
    def _on_monitoring_interval_change(self, e):
        try:
            interval = int(e.control.value)
            if interval > 0:
                self.current_settings['monitoring']['interval'] = interval
                logger.info(f"Monitoring interval set to: {interval}s")
                e.control.error_text = None
                e.control.update()
                self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Monitoring interval set to {interval}s"), bgcolor=ft.Colors.GREEN)
            else:
                e.control.error_text = "Must be greater than 0"
                e.control.update()
                return
        except ValueError:
            e.control.error_text = "Invalid number"
            e.control.update()
            return
        e.control.error_text = None
        e.control.update()
        self.page.snack_bar.open = True
        self.page.update()
    
    def _on_alerts_change(self, e):
        self.current_settings['monitoring']['alerts'] = e.control.value
        logger.info(f"Performance alerts {'enabled' if e.control.value else 'disabled'}")
        self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Performance alerts {'enabled' if e.control.value else 'disabled'}"), bgcolor=ft.Colors.GREEN)
        self.page.snack_bar.open = True
        self.page.update()
    
    # Action handlers
    async def _save_settings_async(self):
        """Async function to save settings."""
        if self.is_saving:
            return
            
        self.is_saving = True
        try:
            success = await self.settings_manager.save_settings_async(self.current_settings)
            if success:
                self.last_saved = datetime.now()
                self.last_saved_text.value = f"Last saved: {self.last_saved.strftime('%H:%M:%S')}"
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Settings saved successfully"),
                    bgcolor=ft.Colors.GREEN
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Failed to save settings"),
                    bgcolor=ft.Colors.RED
                )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Error saving settings"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
        finally:
            self.is_saving = False
    
    def _on_save_settings(self, e):
        logger.info("Saving settings...")
        self.page.run_task(self._save_settings_async)
    
    def _on_reset_settings(self, e):
        # Show confirmation dialog using Flet's built-in AlertDialog
        def confirm_reset(e):
            # Reset to default settings
            default_settings = {
                'server': {'port': 1256, 'host': '127.0.0.1', 'max_clients': 50, 'log_level': 'INFO'},
                'gui': {'theme_mode': 'dark', 'auto_refresh': True, 'notifications': True},
                'monitoring': {'enabled': True, 'interval': 2, 'alerts': True}
            }
            
            # Update current settings
            self.current_settings.clear()
            self.current_settings.update(default_settings)
            
            # Update UI fields
            self._update_ui_fields()
            
            self.page.dialog.open = False
            self.page.update()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Settings reset to defaults"),
                bgcolor=ft.Colors.ORANGE
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        def cancel_reset(e):
            self.page.dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Reset Settings"),
            content=ft.Text("Are you sure you want to reset all settings to their default values? This cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_reset),
                ft.TextButton("Reset", on_click=confirm_reset)
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _update_ui_fields(self):
        """Update UI fields with current settings."""
        self.server_port_field.value = str(self.current_settings['server'].get('port', 1256))
        self.server_host_field.value = self.current_settings['server'].get('host', '127.0.0.1')
        self.max_clients_field.value = str(self.current_settings['server'].get('max_clients', 50))
        self.log_level_dropdown.value = self.current_settings['server'].get('log_level', 'INFO')
        self.theme_mode_switch.value = self.current_settings['gui'].get('theme_mode', 'dark') == 'dark'
        self.auto_refresh_switch.value = self.current_settings['gui'].get('auto_refresh', True)
        self.notifications_switch.value = self.current_settings['gui'].get('notifications', True)
        self.monitoring_enabled_switch.value = self.current_settings['monitoring'].get('enabled', True)
        self.monitoring_interval_field.value = str(self.current_settings['monitoring'].get('interval', 2))
        self.alerts_switch.value = self.current_settings['monitoring'].get('alerts', True)
        
        # Update all fields
        for field in [self.server_port_field, self.server_host_field, self.max_clients_field,
                      self.log_level_dropdown, self.theme_mode_switch, self.auto_refresh_switch,
                      self.notifications_switch, self.monitoring_enabled_switch,
                      self.monitoring_interval_field, self.alerts_switch]:
            field.update()
    
    async def _export_settings_async(self):
        """Async function to export settings."""
        try:
            backup_file = f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            success = await self.settings_manager.export_settings_async(self.current_settings, backup_file)
            if success:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Settings exported to {backup_file}"),
                    bgcolor=ft.Colors.GREEN
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Failed to export settings"),
                    bgcolor=ft.Colors.RED
                )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Error exporting settings"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_export_settings(self, e):
        logger.info("Exporting settings...")
        self.page.run_task(self._export_settings_async)
    
    def _on_import_settings(self, e):
        logger.info("Import settings clicked")
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Import settings feature coming soon"),
            bgcolor=ft.Colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()


def create_settings_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create settings view using ft.UserControl.
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The settings view
    """
    return SettingsView(server_bridge, page)