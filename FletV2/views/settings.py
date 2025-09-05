#!/usr/bin/env python3
"""
Settings View for FletV2
Function-based implementation following Framework Harmony principles.
"""

import flet as ft
import json
import asyncio
from utils.debug_setup import get_logger
from pathlib import Path
from datetime import datetime
from config import SETTINGS_FILE, ASYNC_DELAY, MIN_PORT, MAX_PORT, MIN_MAX_CLIENTS

logger = get_logger(__name__)


# Simple settings management functions (no class needed)
def load_settings(settings_file: str = SETTINGS_FILE):
    """Load settings from file."""
    try:
        settings_path = Path(settings_file)
        if settings_path.exists():
            with open(settings_path, 'r') as f:
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


async def save_settings_async(settings_data, settings_file: str = SETTINGS_FILE):
    """Async function to save settings."""
    try:
        await asyncio.sleep(ASYNC_DELAY)
        with open(settings_file, 'w') as f:
            json.dump(settings_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")
        return False


async def export_settings_async(settings_data, backup_file):
    """Async function to export settings."""
    try:
        await asyncio.sleep(ASYNC_DELAY)
        with open(backup_file, 'w') as f:
            json.dump(settings_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to export settings: {e}")
        return False


def create_settings_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create settings view using simple function-based pattern.
    Follows Framework Harmony principles - no custom classes, use Flet's built-ins.
    """
    # Simple state management
    current_settings = load_settings()
    is_saving = False
    last_saved = None
    
    # Direct control references
    last_saved_text = ft.Text(
        value="Last saved: Never",
        size=12,
        color=ft.Colors.ON_SURFACE
    )
    
    # Server Settings Fields
    server_port_field = ft.TextField(
        label="Server Port",
        value=str(current_settings['server'].get('port', 1256)),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200
    )
    
    server_host_field = ft.TextField(
        label="Server Host",
        value=current_settings['server'].get('host', '127.0.0.1'),
        expand=True
    )
    
    max_clients_field = ft.TextField(
        label="Max Clients",
        value=str(current_settings['server'].get('max_clients', 50)),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200
    )
    
    log_level_dropdown = ft.Dropdown(
        label="Log Level",
        value=current_settings['server'].get('log_level', 'INFO'),
        options=[
            ft.dropdown.Option("DEBUG", "Debug"),
            ft.dropdown.Option("INFO", "Info"),
            ft.dropdown.Option("WARNING", "Warning"),
            ft.dropdown.Option("ERROR", "Error")
        ],
        width=200
    )
    
    # GUI Settings Fields
    theme_mode_switch = ft.Switch(
        label="Dark Mode",
        value=current_settings['gui'].get('theme_mode', 'dark') == 'dark'
    )
    
    auto_refresh_switch = ft.Switch(
        label="Auto Refresh",
        value=current_settings['gui'].get('auto_refresh', True)
    )
    
    notifications_switch = ft.Switch(
        label="Show Notifications",
        value=current_settings['gui'].get('notifications', True)
    )
    
    monitoring_enabled_switch = ft.Switch(
        label="Enable System Monitoring",
        value=current_settings['monitoring'].get('enabled', True)
    )
    
    monitoring_interval_field = ft.TextField(
        label="Monitoring Interval (seconds)",
        value=str(current_settings['monitoring'].get('interval', 2)),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200
    )
    
    alerts_switch = ft.Switch(
        label="Performance Alerts",
        value=current_settings['monitoring'].get('alerts', True)
    )
    
    # Event handlers with closures
    def on_port_change(e):
        nonlocal current_settings
        try:
            port = int(e.control.value)
            if MIN_PORT <= port <= MAX_PORT:
                current_settings['server']['port'] = port
                logger.info(f"Server port changed to: {port}")
                e.control.error_text = None
                e.control.update()
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Port updated to {port}"), bgcolor=ft.Colors.GREEN)
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
        page.snack_bar.open = True
        page.update()
    
    def on_host_change(e):
        nonlocal current_settings
        host = e.control.value.strip()
        if host:
            current_settings['server']['host'] = host
            logger.info(f"Server host changed to: {host}")
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Host updated to {host}"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()
    
    def on_theme_toggle(e):
        nonlocal current_settings
        new_mode = "light" if current_settings['gui']['theme_mode'] == "dark" else "dark"
        current_settings['gui']['theme_mode'] = new_mode
        # Apply theme change immediately using Flet's built-in theme system
        page.theme_mode = ft.ThemeMode.LIGHT if new_mode == "light" else ft.ThemeMode.DARK
        page.update()
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Theme switched to {new_mode} mode"), bgcolor=ft.Colors.BLUE)
        page.snack_bar.open = True
        page.update()
    
    async def save_settings_handler():
        """Async function to save settings."""
        nonlocal is_saving, last_saved
        if is_saving:
            return
            
        is_saving = True
        try:
            success = await save_settings_async(current_settings)
            if success:
                last_saved = datetime.now()
                last_saved_text.value = f"Last saved: {last_saved.strftime('%H:%M:%S')}"
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Settings saved successfully"),
                    bgcolor=ft.Colors.GREEN
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Failed to save settings"),
                    bgcolor=ft.Colors.RED
                )
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Error saving settings"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()
        finally:
            is_saving = False
    
    def on_save_settings(e):
        logger.info("Saving settings...")
        page.run_task(save_settings_handler)
    
    def on_reset_settings(e):
        def confirm_reset(e):
            nonlocal current_settings
            # Reset to default settings
            default_settings = {
                'server': {'port': 1256, 'host': '127.0.0.1', 'max_clients': 50, 'log_level': 'INFO'},
                'gui': {'theme_mode': 'dark', 'auto_refresh': True, 'notifications': True},
                'monitoring': {'enabled': True, 'interval': 2, 'alerts': True}
            }
            
            current_settings.clear()
            current_settings.update(default_settings)
            
            # Update UI fields
            update_ui_fields()
            
            page.dialog.open = False
            page.update()
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Settings reset to defaults"),
                bgcolor=ft.Colors.ORANGE
            )
            page.snack_bar.open = True
            page.update()
        
        def cancel_reset(e):
            page.dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Reset Settings"),
            content=ft.Text("Are you sure you want to reset all settings to their default values? This cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_reset),
                ft.TextButton("Reset", on_click=confirm_reset)
            ]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def update_ui_fields():
        """Update UI fields with current settings."""
        server_port_field.value = str(current_settings['server'].get('port', 1256))
        server_host_field.value = current_settings['server'].get('host', '127.0.0.1')
        max_clients_field.value = str(current_settings['server'].get('max_clients', 50))
        log_level_dropdown.value = current_settings['server'].get('log_level', 'INFO')
        theme_mode_switch.value = current_settings['gui'].get('theme_mode', 'dark') == 'dark'
        auto_refresh_switch.value = current_settings['gui'].get('auto_refresh', True)
        notifications_switch.value = current_settings['gui'].get('notifications', True)
        monitoring_enabled_switch.value = current_settings['monitoring'].get('enabled', True)
        monitoring_interval_field.value = str(current_settings['monitoring'].get('interval', 2))
        alerts_switch.value = current_settings['monitoring'].get('alerts', True)
        
        # Update all fields
        for field in [server_port_field, server_host_field, max_clients_field,
                      log_level_dropdown, theme_mode_switch, auto_refresh_switch,
                      notifications_switch, monitoring_enabled_switch,
                      monitoring_interval_field, alerts_switch]:
            field.update()
    
    async def export_settings_handler():
        """Async function to export settings."""
        try:
            backup_file = f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            success = await export_settings_async(current_settings, backup_file)
            if success:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Settings exported to {backup_file}"),
                    bgcolor=ft.Colors.GREEN
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Failed to export settings"),
                    bgcolor=ft.Colors.RED
                )
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Error exporting settings"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()
    
    def on_export_settings(e):
        logger.info("Exporting settings...")
        page.run_task(export_settings_handler)
    
    def on_import_settings(e):
        logger.info("Import settings clicked")
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Import settings feature coming soon"),
            bgcolor=ft.Colors.BLUE
        )
        page.snack_bar.open = True
        page.update()
    
    # Assign event handlers to controls
    server_port_field.on_change = on_port_change
    server_host_field.on_change = on_host_change
    theme_mode_switch.on_change = on_theme_toggle
    
    def create_server_settings():
        """Create server settings form."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Server Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    server_port_field,
                    server_host_field,
                    max_clients_field,
                    log_level_dropdown
                ], spacing=15),
                padding=20
            )
        )
    
    def create_gui_settings():
        """Create GUI settings form."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("GUI Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([
                        ft.Text("Theme Mode:", size=16, weight=ft.FontWeight.W_500),
                        theme_mode_switch
                    ]),
                    auto_refresh_switch,
                    notifications_switch
                ], spacing=15),
                padding=20
            )
        )
    
    def create_monitoring_settings():
        """Create monitoring settings form."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Monitoring Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    monitoring_enabled_switch,
                    monitoring_interval_field,
                    alerts_switch
                ], spacing=15),
                padding=20
            )
        )
    
    # Build the main view using Flet's built-in components
    main_view = ft.Column([
        # Header
        ft.Row([
            ft.Icon(ft.Icons.SETTINGS, size=24),
            ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            last_saved_text
        ]),
        ft.Divider(),
        # Action buttons
        ft.ResponsiveRow([
            ft.Column([
                ft.ElevatedButton(
                    "Save Settings",
                    icon=ft.Icons.SAVE,
                    on_click=on_save_settings,
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
                    on_click=on_reset_settings
                )
            ], col={"sm": 12, "md": 3}),
            ft.Column([
                ft.OutlinedButton(
                    "Export Backup",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=on_export_settings
                )
            ], col={"sm": 12, "md": 3}),
            ft.Column([
                ft.TextButton(
                    "Import Settings",
                    icon=ft.Icons.UPLOAD,
                    on_click=on_import_settings
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
                    content=create_server_settings()
                ),
                ft.Tab(
                    text="GUI",
                    icon=ft.Icons.PALETTE,
                    content=create_gui_settings()
                ),
                ft.Tab(
                    text="Monitoring",
                    icon=ft.Icons.MONITOR_HEART,
                    content=create_monitoring_settings()
                )
            ],
            expand=True
        )
    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)
    
    return main_view