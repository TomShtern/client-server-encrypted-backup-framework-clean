#!/usr/bin/env python3
"""
Settings Form Generator
Generates UI forms for different settings categories with consistent styling.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

import flet as ft
from typing import Dict, Any, List, Callable, Optional


class SettingsFormGenerator:
    """Generates consistent forms for settings categories"""
    
    def __init__(self, page: ft.Page, on_change_callback: Optional[Callable] = None):
        self.page = page
        self.on_change_callback = on_change_callback
    
    def create_server_settings_form(self, current_values: Dict[str, Any]) -> ft.Container:
        """Create server settings form section"""
        
        # Create form controls
        controls = {
            'port': ft.TextField(
                label="Server Port",
                value=str(current_values.get('port', 1256)),
                expand=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=self._trigger_change_callback
            ),
            'host': ft.TextField(
                label="Server Host",
                value=current_values.get('host', '127.0.0.1'),
                expand=True,
                on_change=self._trigger_change_callback
            ),
            'storage_directory': ft.TextField(
                label="Storage Directory",
                value=current_values.get('storage_directory', 'received_files'),
                expand=True,
                on_change=self._trigger_change_callback
            ),
            'max_connections': ft.TextField(
                label="Max Connections",
                value=str(current_values.get('max_connections', 100)),
                expand=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=self._trigger_change_callback
            ),
            'auto_start': ft.Switch(
                label="Auto-start server",
                value=current_values.get('auto_start', False),
                on_change=self._trigger_change_callback
            ),
            'enable_logging': ft.Switch(
                label="Enable detailed logging",
                value=current_values.get('enable_logging', True),
                on_change=self._trigger_change_callback
            )
        }
        
        return self._create_section_container(
            "Server Configuration",
            ft.Icons.SETTINGS,
            [
                ft.ResponsiveRow([
                    ft.Container(content=controls['host'], col={"sm": 12, "md": 6}, expand=True),
                    ft.Container(content=controls['port'], col={"sm": 12, "md": 6}, expand=True)
                ]),
                ft.Row([
                    controls['storage_directory'],
                    ft.VerticalDivider(width=20),
                    controls['max_connections']
                ]),
                ft.Row([
                    controls['auto_start'],
                    ft.VerticalDivider(width=20),
                    controls['enable_logging']
                ])
            ],
            controls
        )
    
    def create_gui_settings_form(self, current_values: Dict[str, Any]) -> ft.Container:
        """Create GUI preferences form section"""
        
        controls = {
            'theme_mode': ft.Dropdown(
                label="Theme Mode",
                expand=True,
                value=current_values.get('theme_mode', 'system'),
                options=[
                    ft.dropdown.Option("light", "Light"),
                    ft.dropdown.Option("dark", "Dark"),
                    ft.dropdown.Option("system", "System Default")
                ],
                on_change=self._trigger_change_callback
            ),
            'refresh_interval': ft.Slider(
                label="Auto-refresh interval (seconds)",
                min=5,
                max=300,
                divisions=59,
                value=current_values.get('refresh_interval', 30),
                expand=True,
                on_change=self._trigger_change_callback
            ),
            'show_notifications': ft.Switch(
                label="Show notifications",
                value=current_values.get('show_notifications', True),
                on_change=self._trigger_change_callback
            ),
            'minimize_to_tray': ft.Switch(
                label="Minimize to system tray",
                value=current_values.get('minimize_to_tray', False),
                on_change=self._trigger_change_callback
            ),
            'confirm_actions': ft.Switch(
                label="Confirm destructive actions",
                value=current_values.get('confirm_actions', True),
                on_change=self._trigger_change_callback
            )
        }
        
        # Create refresh interval display
        refresh_display = ft.Text(
            f"{int(controls['refresh_interval'].value)}s",
            weight=ft.FontWeight.BOLD
        )
        
        def update_refresh_display(e):
            refresh_display.value = f"{int(e.control.value)}s"
            self.page.update()
            if self.on_change_callback:
                self.on_change_callback()
        
        controls['refresh_interval'].on_change = update_refresh_display
        
        return self._create_section_container(
            "GUI Preferences",
            ft.Icons.PALETTE,
            [
                ft.Row([
                    controls['theme_mode']
                ]),
                ft.Row([
                    ft.Column([
                        controls['refresh_interval'],
                        refresh_display
                    ], spacing=5, tight=True)
                ]),
                ft.Row([
                    controls['show_notifications'],
                    ft.VerticalDivider(width=20),
                    controls['minimize_to_tray']
                ]),
                ft.Row([
                    controls['confirm_actions']
                ])
            ],
            controls
        )
    
    def create_monitoring_settings_form(self, current_values: Dict[str, Any]) -> ft.Container:
        """Create monitoring configuration form section"""
        
        controls = {
            'enable_system_monitoring': ft.Switch(
                label="Enable system monitoring",
                value=current_values.get('enable_system_monitoring', True),
                on_change=self._trigger_change_callback
            ),
            'cpu_alert_threshold': ft.TextField(
                label="CPU Alert Threshold (%)",
                value=str(current_values.get('cpu_alert_threshold', 80)),
                expand=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=self._trigger_change_callback
            ),
            'memory_alert_threshold': ft.TextField(
                label="Memory Alert Threshold (%)",
                value=str(current_values.get('memory_alert_threshold', 85)),
                expand=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=self._trigger_change_callback
            ),
            'disk_alert_threshold': ft.TextField(
                label="Disk Alert Threshold (%)",
                value=str(current_values.get('disk_alert_threshold', 90)),
                expand=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=self._trigger_change_callback
            ),
            'monitoring_interval': ft.Dropdown(
                label="Monitoring Interval",
                expand=True,
                value=str(current_values.get('monitoring_interval', 60)),
                options=[
                    ft.dropdown.Option("30", "30 seconds"),
                    ft.dropdown.Option("60", "1 minute"),
                    ft.dropdown.Option("300", "5 minutes"),
                    ft.dropdown.Option("600", "10 minutes")
                ],
                on_change=self._trigger_change_callback
            )
        }
        
        return self._create_section_container(
            "Monitoring Configuration",
            ft.Icons.MONITOR_HEART,
            [
                ft.Row([
                    controls['enable_system_monitoring']
                ]),
                ft.Row([
                    controls['cpu_alert_threshold'],
                    ft.VerticalDivider(width=10),
                    controls['memory_alert_threshold'],
                    ft.VerticalDivider(width=10),
                    controls['disk_alert_threshold']
                ]),
                ft.Row([
                    controls['monitoring_interval']
                ])
            ],
            controls
        )
    
    def create_advanced_settings_form(self, current_values: Dict[str, Any]) -> ft.Container:
        """Create advanced settings form section"""
        
        controls = {
            'backup_frequency': ft.Dropdown(
                label="Database Backup Frequency",
                expand=True,
                value=current_values.get('backup_frequency', 'weekly'),
                options=[
                    ft.dropdown.Option("daily", "Daily"),
                    ft.dropdown.Option("weekly", "Weekly"),
                    ft.dropdown.Option("monthly", "Monthly"),
                    ft.dropdown.Option("manual", "Manual Only")
                ],
                on_change=self._trigger_change_callback
            ),
            'cleanup_old_files': ft.Switch(
                label="Auto-cleanup old files",
                value=current_values.get('cleanup_old_files', False),
                on_change=self._trigger_change_callback
            ),
            'cleanup_days': ft.TextField(
                label="Days to keep files",
                value=str(current_values.get('cleanup_days', 30)),
                expand=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=self._trigger_change_callback
            ),
            'debug_mode': ft.Switch(
                label="Enable debug mode",
                value=current_values.get('debug_mode', False),
                on_change=self._trigger_change_callback
            )
        }
        
        return self._create_section_container(
            "Advanced Settings",
            ft.Icons.TUNE,
            [
                ft.Row([
                    controls['backup_frequency']
                ]),
                ft.Row([
                    controls['cleanup_old_files'],
                    ft.VerticalDivider(width=20),
                    controls['cleanup_days']
                ]),
                ft.Row([
                    controls['debug_mode']
                ])
            ],
            controls
        )
    
    def _create_section_container(self, title: str, icon: str, content: List[ft.Control], 
                                 controls: Dict[str, ft.Control]) -> ft.Container:
        """Create a standardized section container"""
        
        container = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        # Section header
                        ft.Row([
                            ft.Icon(icon, size=24),
                            ft.Text(title, style=ft.TextThemeStyle.TITLE_MEDIUM, expand=True)
                        ], alignment=ft.MainAxisAlignment.START),
                        
                        ft.Divider(),
                        
                        # Section content
                        ft.Column(content, spacing=15)
                    ], spacing=10),
                    padding=20
                ),
                elevation=2
            ),
            margin=ft.Margin(0, 0, 0, 15),
            expand=True
        )
        
        # Store controls reference for easy access
        container.data = controls
        
        return container
    
    def _trigger_change_callback(self, e=None):
        """Trigger the change callback if provided"""
        if self.on_change_callback:
            self.on_change_callback()
    
    def get_form_values(self, form_container: ft.Container) -> Dict[str, Any]:
        """Extract values from a form container"""
        if not hasattr(form_container, 'data') or not form_container.data:
            return {}
        
        values = {}
        for key, control in form_container.data.items():
            if isinstance(control, (ft.TextField, ft.Dropdown)):
                values[key] = control.value
            elif isinstance(control, ft.Switch):
                values[key] = control.value
            elif isinstance(control, ft.Slider):
                values[key] = control.value
        
        return values
    
    def update_form_values(self, form_container: ft.Container, values: Dict[str, Any]):
        """Update form container with new values"""
        if not hasattr(form_container, 'data') or not form_container.data:
            return
        
        for key, value in values.items():
            if key in form_container.data:
                control = form_container.data[key]
                if isinstance(control, (ft.TextField, ft.Dropdown)):
                    control.value = str(value)
                elif isinstance(control, ft.Switch):
                    control.value = bool(value)
                elif isinstance(control, ft.Slider):
                    control.value = float(value)
