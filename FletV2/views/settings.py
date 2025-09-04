#!/usr/bin/env python3
"""
Simple Settings View - Hiroshima Protocol Compliant
A clean, minimal implementation using pure Flet patterns.
This demonstrates the Hiroshima ideal:
- Uses Flet's built-in Tabs for categories
- Uses Flet's TextField, Dropdown, Switch for form controls
- Simple function returning ft.Control (composition over inheritance)
- Works WITH the framework, not against it
"""
import flet as ft
import json
# Import debugging setup
from utils.debug_setup import get_logger
logger = get_logger(__name__)
# Import debugging setup
# Import debugging setup
import os
from pathlib import Path
from datetime import datetime
def create_settings_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create settings view using simple Flet patterns (no class inheritance needed).
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
    Returns:
        ft.Control: The settings view
    """
    # Load settings from file (simple JSON handling)
    settings_file = Path("flet_server_gui_settings.json")
    def load_settings():
        try:
            if settings_file.exists():
                with open(settings_file, 'r') as f:
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
    def save_settings(settings_data):
        try:
            with open(settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    # Load current settings
    current_settings = load_settings()
    # Action handlers
    def on_save_settings(e):
        if save_settings(current_settings):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Settings saved successfully"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True
            page.update()
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Failed to save settings"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()
    def on_reset_settings(e):
        # Show confirmation dialog using Flet's built-in AlertDialog
        def confirm_reset(e):
            nonlocal current_settings
            current_settings = {
                'server': {'port': 1256, 'host': '127.0.0.1', 'max_clients': 50, 'log_level': 'INFO'},
                'gui': {'theme_mode': 'dark', 'auto_refresh': True, 'notifications': True},
                'monitoring': {'enabled': True, 'interval': 2, 'alerts': True}
            }
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
    def on_theme_toggle(e):
        new_mode = "light" if current_settings['gui']['theme_mode'] == "dark" else "dark"
        current_settings['gui']['theme_mode'] = new_mode
        # Apply theme change immediately using Flet's built-in theme system
        page.theme_mode = ft.ThemeMode.LIGHT if new_mode == "light" else ft.ThemeMode.DARK
        page.update()
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Theme switched to {new_mode} mode"),
            bgcolor=ft.Colors.BLUE
        )
        page.snack_bar.open = True
        page.update()
    def on_export_settings(e):
        backup_file = f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(backup_file, 'w') as f:
                json.dump(current_settings, f, indent=2)
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Settings exported to {backup_file}"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            logger.error(f"Export failed: {ex}")
    # Create settings forms using Flet's built-in components
    def create_server_settings():
        # Create event handlers for server settings
        def on_port_change(e):
            try:
                port = int(e.control.value)
                if 1024 <= port <= 65535:
                    current_settings['server']['port'] = port
                    logger.info(f"Server port changed to: {port}")
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Port updated to {port}"), bgcolor=ft.Colors.GREEN)
                else:
                    e.control.error_text = "Port must be between 1024-65535"
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
            host = e.control.value.strip()
            if host:
                current_settings['server']['host'] = host
                logger.info(f"Server host changed to: {host}")
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Host updated to {host}"), bgcolor=ft.Colors.GREEN)
                page.snack_bar.open = True
                page.update()
        
        def on_max_clients_change(e):
            try:
                max_clients = int(e.control.value)
                if max_clients > 0:
                    current_settings['server']['max_clients'] = max_clients
                    logger.info(f"Max clients changed to: {max_clients}")
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Max clients updated to {max_clients}"), bgcolor=ft.Colors.GREEN)
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
            page.snack_bar.open = True
            page.update()
        
        def on_log_level_change(e):
            level = e.control.value
            current_settings['server']['log_level'] = level
            logger.info(f"Log level changed to: {level}")
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Log level updated to {level}"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Server Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.TextField(
                        label="Server Port",
                        value=str(current_settings['server'].get('port', 1256)),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_change=on_port_change
                    ),
                    ft.TextField(
                        label="Server Host",
                        value=current_settings['server'].get('host', '127.0.0.1'),
                        expand=True,
                        on_change=on_host_change
                    ),
                    ft.TextField(
                        label="Max Clients",
                        value=str(current_settings['server'].get('max_clients', 50)),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_change=on_max_clients_change
                    ),
                    ft.Dropdown(
                        label="Log Level",
                        value=current_settings['server'].get('log_level', 'INFO'),
                        options=[
                            ft.dropdown.Option("DEBUG", "Debug"),
                            ft.dropdown.Option("INFO", "Info"),
                            ft.dropdown.Option("WARNING", "Warning"),
                            ft.dropdown.Option("ERROR", "Error")
                        ],
                        width=200,
                        on_change=on_log_level_change
                    )
                ], spacing=15),
                padding=20
            )
        )
    def create_gui_settings():
        # Create event handlers for GUI settings
        def on_auto_refresh_change(e):
            current_settings['gui']['auto_refresh'] = e.control.value
            logger.info(f"Auto refresh set to: {e.control.value}")
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Auto refresh {'enabled' if e.control.value else 'disabled'}"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()
        
        def on_notifications_change(e):
            current_settings['gui']['notifications'] = e.control.value
            logger.info(f"Notifications set to: {e.control.value}")
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Notifications {'enabled' if e.control.value else 'disabled'}"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()
        
        def on_refresh_interval_change(e):
            try:
                interval = int(e.control.value)
                if interval > 0:
                    current_settings['gui']['refresh_interval'] = interval
                    logger.info(f"Refresh interval changed to: {interval}s")
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Refresh interval set to {interval}s"), bgcolor=ft.Colors.GREEN)
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
            page.snack_bar.open = True
            page.update()
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("GUI Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([
                        ft.Text("Theme Mode:", size=16, weight=ft.FontWeight.W_500),
                        ft.Switch(
                            label="Dark Mode",
                            value=current_settings['gui'].get('theme_mode', 'dark') == 'dark',
                            on_change=on_theme_toggle
                        )
                    ]),
                    ft.Switch(
                        label="Auto Refresh",
                        value=current_settings['gui'].get('auto_refresh', True),
                        on_change=on_auto_refresh_change
                    ),
                    ft.Switch(
                        label="Show Notifications",
                        value=current_settings['gui'].get('notifications', True),
                        on_change=on_notifications_change
                    ),
                    ft.TextField(
                        label="Refresh Interval (seconds)",
                        value=str(current_settings['gui'].get('refresh_interval', 5)),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_change=on_refresh_interval_change
                    )
                ], spacing=15),
                padding=20
            )
        )
    def create_monitoring_settings():
        # Create event handlers for monitoring settings
        def on_monitoring_enabled_change(e):
            current_settings['monitoring']['enabled'] = e.control.value
            logger.info(f"System monitoring {'enabled' if e.control.value else 'disabled'}")
            page.snack_bar = ft.SnackBar(content=ft.Text(f"System monitoring {'enabled' if e.control.value else 'disabled'}"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()
        
        def on_monitoring_interval_change(e):
            try:
                interval = int(e.control.value)
                if interval > 0:
                    current_settings['monitoring']['interval'] = interval
                    logger.info(f"Monitoring interval set to: {interval}s")
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Monitoring interval set to {interval}s"), bgcolor=ft.Colors.GREEN)
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
            page.snack_bar.open = True
            page.update()
        
        def on_alerts_change(e):
            current_settings['monitoring']['alerts'] = e.control.value
            logger.info(f"Performance alerts {'enabled' if e.control.value else 'disabled'}")
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Performance alerts {'enabled' if e.control.value else 'disabled'}"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()
        
        def create_threshold_handler(threshold_type):
            def handler(e):
                try:
                    value = int(e.control.value)
                    if 0 <= value <= 100:
                        if 'thresholds' not in current_settings['monitoring']:
                            current_settings['monitoring']['thresholds'] = {}
                        current_settings['monitoring']['thresholds'][threshold_type] = value
                        logger.info(f"{threshold_type} alert threshold set to: {value}%")
                        page.snack_bar = ft.SnackBar(content=ft.Text(f"{threshold_type} alert set to {value}%"), bgcolor=ft.Colors.GREEN)
                    else:
                        e.control.error_text = "Must be 0-100"
                        e.control.update()
                        return
                except ValueError:
                    e.control.error_text = "Invalid number"
                    e.control.update()
                    return
                e.control.error_text = None
                e.control.update()
                page.snack_bar.open = True
                page.update()
            return handler
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Monitoring Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Switch(
                        label="Enable System Monitoring",
                        value=current_settings['monitoring'].get('enabled', True),
                        on_change=on_monitoring_enabled_change
                    ),
                    ft.TextField(
                        label="Monitoring Interval (seconds)",
                        value=str(current_settings['monitoring'].get('interval', 2)),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200,
                        on_change=on_monitoring_interval_change
                    ),
                    ft.Switch(
                        label="Performance Alerts",
                        value=current_settings['monitoring'].get('alerts', True),
                        on_change=on_alerts_change
                    ),
                    ft.Text("Alert Thresholds", size=16, weight=ft.FontWeight.W_500),
                    ft.Row([
                        ft.TextField(
                            label="CPU Alert (%)",
                            value=str(current_settings['monitoring'].get('thresholds', {}).get('cpu', 80)),
                            keyboard_type=ft.KeyboardType.NUMBER,
                            width=120,
                            on_change=create_threshold_handler('cpu')
                        ),
                        ft.TextField(
                            label="Memory Alert (%)",
                            value=str(current_settings['monitoring'].get('thresholds', {}).get('memory', 85)),
                            keyboard_type=ft.KeyboardType.NUMBER,
                            width=120,
                            on_change=create_threshold_handler('memory')
                        ),
                        ft.TextField(
                            label="Disk Alert (%)",
                            value=str(current_settings['monitoring'].get('thresholds', {}).get('disk', 90)),
                            keyboard_type=ft.KeyboardType.NUMBER,
                            width=120,
                            on_change=create_threshold_handler('disk')
                        )
                    ], spacing=20)
                ], spacing=15),
                padding=20
            )
        )
    # Create settings tabs using Flet's built-in Tabs component (this is the RIGHT way!)
    settings_tabs = ft.Tabs(
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
    # Action buttons
    action_buttons = ft.ResponsiveRow([
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
                on_click=lambda e: logger.info("Import settings clicked")
            )
        ], col={"sm": 12, "md": 3})
    ])
    # Main layout using simple Column
    return ft.Column([
        # Header
        ft.Row([
            ft.Icon(ft.Icons.SETTINGS, size=24),
            ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.Text("Last saved: " + datetime.now().strftime("%H:%M:%S"), size=12, color=ft.Colors.ON_SURFACE)
        ]),
        ft.Divider(),
        # Action buttons
        action_buttons,
        ft.Divider(),
        # Settings tabs (using Flet's built-in Tabs!)
        settings_tabs
    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)