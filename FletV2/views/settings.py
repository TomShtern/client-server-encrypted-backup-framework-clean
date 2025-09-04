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
            print(f"[ERROR] Failed to load settings: {e}")
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
            print(f"[ERROR] Failed to save settings: {e}")
            return False
    
    # Load current settings
    current_settings = load_settings()
    
    # Action handlers
    def on_save_settings(e):
        if save_settings(current_settings):
            if page.snack_bar:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Settings saved successfully"),
                    bgcolor=ft.Colors.GREEN
                )
                page.snack_bar.open = True
                page.update()
        else:
            if page.snack_bar:
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
            if page.snack_bar:
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
        
        if page.snack_bar:
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
            if page.snack_bar:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Settings exported to {backup_file}"),
                    bgcolor=ft.Colors.GREEN
                )
                page.snack_bar.open = True
                page.update()
        except Exception as ex:
            print(f"[ERROR] Export failed: {ex}")
    
    # Create settings forms using Flet's built-in components
    def create_server_settings():
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Server Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    ft.TextField(
                        label="Server Port",
                        value=str(current_settings['server'].get('port', 1256)),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200
                    ),
                    
                    ft.TextField(
                        label="Server Host",
                        value=current_settings['server'].get('host', '127.0.0.1'),
                        expand=True
                    ),
                    
                    ft.TextField(
                        label="Max Clients",
                        value=str(current_settings['server'].get('max_clients', 50)),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200
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
                        width=200
                    )
                ], spacing=15),
                padding=20
            )
        )
    
    def create_gui_settings():
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
                    ),
                    
                    ft.Switch(
                        label="Show Notifications",
                        value=current_settings['gui'].get('notifications', True),
                    ),
                    
                    ft.TextField(
                        label="Refresh Interval (seconds)",
                        value="5",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200
                    )
                ], spacing=15),
                padding=20
            )
        )
    
    def create_monitoring_settings():
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Monitoring Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    ft.Switch(
                        label="Enable System Monitoring",
                        value=current_settings['monitoring'].get('enabled', True),
                    ),
                    
                    ft.TextField(
                        label="Monitoring Interval (seconds)",
                        value=str(current_settings['monitoring'].get('interval', 2)),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        width=200
                    ),
                    
                    ft.Switch(
                        label="Performance Alerts",
                        value=current_settings['monitoring'].get('alerts', True),
                    ),
                    
                    ft.Text("Alert Thresholds", size=16, weight=ft.FontWeight.W_500),
                    
                    ft.Row([
                        ft.TextField(
                            label="CPU Alert (%)",
                            value="80",
                            keyboard_type=ft.KeyboardType.NUMBER,
                            width=120
                        ),
                        ft.TextField(
                            label="Memory Alert (%)",
                            value="85",
                            keyboard_type=ft.KeyboardType.NUMBER,
                            width=120
                        ),
                        ft.TextField(
                            label="Disk Alert (%)",
                            value="90",
                            keyboard_type=ft.KeyboardType.NUMBER,
                            width=120
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
                on_click=lambda e: print("[INFO] Import settings clicked")
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