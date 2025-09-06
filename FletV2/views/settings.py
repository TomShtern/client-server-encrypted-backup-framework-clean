#!/usr/bin/env python3
"""
Settings View for FletV2
Function-based implementation following Framework Harmony principles.
Updated with working event handlers.
"""

import flet as ft
import json
import asyncio
from utils.debug_setup import get_logger
from utils.user_feedback import show_success_message, show_error_message, show_info_message
from pathlib import Path
from datetime import datetime
from config import SETTINGS_FILE, ASYNC_DELAY, MIN_PORT, MAX_PORT, MIN_MAX_CLIENTS

# Add UTF-8 support for file operations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import Shared.utils.utf8_solution

logger = get_logger(__name__)
# Hot reload test - event handlers fixed - RELOAD TEST


# Simple settings management functions (no class needed)
def load_settings(settings_file: str = SETTINGS_FILE):
    """Load settings from file."""
    try:
        settings_path = Path(settings_file)
        if settings_path.exists():
            # Use UTF-8 encoding for file operations
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
                # Ensure all required sections exist
                if 'server' not in settings_data:
                    settings_data['server'] = {
                        'port': 1256,
                        'host': '127.0.0.1',
                        'max_clients': 50,
                        'log_level': 'INFO'
                    }
                if 'gui' not in settings_data:
                    settings_data['gui'] = {
                        'theme_mode': 'dark',
                        'auto_refresh': True,
                        'notifications': True
                    }
                if 'monitoring' not in settings_data:
                    settings_data['monitoring'] = {
                        'enabled': True,
                        'interval': 2,
                        'alerts': True
                    }
                return settings_data
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
            'server': {'port': 1256, 'host': '127.0.0.1', 'max_clients': 50, 'log_level': 'INFO'},
            'gui': {'theme_mode': 'dark', 'auto_refresh': True, 'notifications': True},
            'monitoring': {'enabled': True, 'interval': 2, 'alerts': True}
        }


def save_settings_sync(settings_data, settings_file: str = SETTINGS_FILE):
    """Sync function to save settings with proper error handling."""
    try:
        # Ensure directory exists
        settings_path = Path(settings_file)
        settings_path.parent.mkdir(parents=True, exist_ok=True)

        # Use UTF-8 encoding for file operations
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Settings saved successfully to {settings_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")
        return False


def export_settings_sync(settings_data, backup_file):
    """Sync function to export settings with proper error handling."""
    try:
        # Ensure directory exists
        backup_path = Path(backup_file)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Use UTF-8 encoding for file operations
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Settings exported successfully to {backup_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to export settings: {e}")
        return False


def import_settings_sync(file_path):
    """Sync function to import settings from a file with proper error handling."""
    try:
        # Use UTF-8 encoding for file operations
        with open(file_path, 'r', encoding='utf-8') as f:
            imported_settings = json.load(f)

        # Validate imported settings structure
        if not isinstance(imported_settings, dict):
            raise ValueError("Invalid settings format")

        # Ensure required sections exist
        if 'server' not in imported_settings:
            imported_settings['server'] = {
                'port': 1256,
                'host': '127.0.0.1',
                'max_clients': 50,
                'log_level': 'INFO'
            }
        if 'gui' not in imported_settings:
            imported_settings['gui'] = {
                'theme_mode': 'dark',
                'auto_refresh': True,
                'notifications': True
            }
        if 'monitoring' not in imported_settings:
            imported_settings['monitoring'] = {
                'enabled': True,
                'interval': 2,
                'alerts': True
            }

        logger.info(f"Settings imported successfully from {file_path}")
        return imported_settings
    except Exception as e:
        logger.error(f"Failed to import settings: {e}")
        return None


def create_settings_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create settings view using simple function-based pattern.
    Follows Framework Harmony principles - no custom classes, use Flet's built-ins.
    """
    # Simple state management
    # Initialize with default values, load actual settings asynchronously
    current_settings = {
        'server': {'port': 1256, 'host': '127.0.0.1', 'max_clients': 50, 'log_level': 'INFO'},
        'gui': {'theme_mode': 'dark', 'auto_refresh': True, 'notifications': True},
        'monitoring': {'enabled': True, 'interval': 2, 'alerts': True}
    }
    is_saving = False
    last_saved = None

    # Direct control references
    last_saved_text = ft.Text(
        value="Last saved: Never",
        size=12,
        color=ft.Colors.ON_SURFACE
    )

    # Event handlers with closures - DEFINE FIRST, BEFORE CONTROLS
    async def on_port_change(e):
        nonlocal current_settings
        try:
            port = int(e.control.value)
            # Use default values if constants are not defined
            min_port = getattr(sys.modules[__name__], 'MIN_PORT', 1024)
            max_port = getattr(sys.modules[__name__], 'MAX_PORT', 65535)
            if min_port <= port <= max_port:
                current_settings['server']['port'] = port
                logger.info(f"Server port changed to: {port}")
                e.control.error_text = None
                if e.control.page:  # Check if control is attached to page
                    await e.control.update_async()
                if page:  # Check if page is still available
                    show_success_message(page, f"Port updated to {port}")
            else:
                e.control.error_text = f"Port must be between {min_port}-{max_port}"
                if e.control.page:  # Check if control is attached to page
                    await e.control.update_async()
                return
        except ValueError:
            e.control.error_text = "Invalid port number"
            if e.control.page:  # Check if control is attached to page
                await e.control.update_async()
            return
        e.control.error_text = None
        if e.control.page:  # Check if control is attached to page
            await e.control.update_async()

    async def on_host_change(e):
        nonlocal current_settings
        host = e.control.value.strip()
        if host:
            current_settings['server']['host'] = host
            logger.info(f"Server host changed to: {host}")
            if page:  # Check if page is still available
                show_success_message(page, f"Host updated to {host}")

    async def on_max_clients_change(e):
        nonlocal current_settings
        try:
            max_clients = int(e.control.value)
            # Use default value if constant is not defined
            min_max_clients = getattr(sys.modules[__name__], 'MIN_MAX_CLIENTS', 1)
            if max_clients >= min_max_clients:
                current_settings['server']['max_clients'] = max_clients
                logger.info(f"Max clients changed to: {max_clients}")
                e.control.error_text = None
                if e.control.page:  # Check if control is attached to page
                    await e.control.update_async()
                if page:  # Check if page is still available
                    show_success_message(page, f"Max clients updated to {max_clients}")
            else:
                e.control.error_text = f"Must be at least {min_max_clients}"
                if e.control.page:  # Check if control is attached to page
                    await e.control.update_async()
                return
        except ValueError:
            e.control.error_text = "Invalid number"
            if e.control.page:  # Check if control is attached to page
                await e.control.update_async()
            return
        e.control.error_text = None
        if e.control.page:  # Check if control is attached to page
            await e.control.update_async()

    async def on_log_level_change(e):
        nonlocal current_settings
        log_level = e.control.value
        current_settings['server']['log_level'] = log_level
        logger.info(f"Log level changed to: {log_level}")
        if page:  # Check if page is still available
            show_success_message(page, f"Log level updated to {log_level}")

    async def on_auto_refresh_toggle(e):
        nonlocal current_settings
        new_value = e.control.value
        current_settings['gui']['auto_refresh'] = new_value
        logger.info(f"Auto refresh changed to: {new_value}")
        if page:  # Check if page is still available
            show_success_message(page, f"Auto refresh {'enabled' if new_value else 'disabled'}")

    async def on_notifications_toggle(e):
        nonlocal current_settings
        new_value = e.control.value
        current_settings['gui']['notifications'] = new_value
        logger.info(f"Notifications changed to: {new_value}")
        if page:  # Check if page is still available
            show_success_message(page, f"Notifications {'enabled' if new_value else 'disabled'}")

    async def on_monitoring_enabled_toggle(e):
        nonlocal current_settings
        new_value = e.control.value
        current_settings['monitoring']['enabled'] = new_value
        logger.info(f"Monitoring enabled changed to: {new_value}")
        if page:  # Check if page is still available
            show_success_message(page, f"System monitoring {'enabled' if new_value else 'disabled'}")

    async def on_monitoring_interval_change(e):
        nonlocal current_settings
        try:
            interval = int(e.control.value)
            if interval > 0:
                current_settings['monitoring']['interval'] = interval
                logger.info(f"Monitoring interval changed to: {interval}")
                e.control.error_text = None
                if e.control.page:  # Check if control is attached to page
                    await e.control.update_async()
                if page:  # Check if page is still available
                    show_success_message(page, f"Monitoring interval updated to {interval} seconds")
            else:
                e.control.error_text = "Must be greater than 0"
                if e.control.page:  # Check if control is attached to page
                    await e.control.update_async()
                return
        except ValueError:
            e.control.error_text = "Invalid number"
            if e.control.page:  # Check if control is attached to page
                await e.control.update_async()
            return
        e.control.error_text = None
        if e.control.page:  # Check if control is attached to page
            await e.control.update_async()

    async def on_alerts_toggle(e):
        nonlocal current_settings
        new_value = e.control.value
        current_settings['monitoring']['alerts'] = new_value
        logger.info(f"Performance alerts changed to: {new_value}")
        if page:  # Check if page is still available
            show_success_message(page, f"Performance alerts {'enabled' if new_value else 'disabled'}")

    async def on_theme_toggle(e):
        nonlocal current_settings
        new_mode = "light" if current_settings['gui']['theme_mode'] == "dark" else "dark"
        current_settings['gui']['theme_mode'] = new_mode
        if page:  # Check if page is still available
            page.theme_mode = ft.ThemeMode.LIGHT if new_mode == "light" else ft.ThemeMode.DARK
            await page.update_async()
            show_info_message(page, f"Theme switched to {new_mode} mode")

    # Server Settings Fields
    server_port_field = ft.TextField(
        label="Server Port",
        value=str(current_settings['server'].get('port', 1256)),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200,
        on_change=on_port_change
    )

    def reset_port_field(e):
        server_port_field.value = "1256"
        server_port_field.error_text = None
        current_settings['server']['port'] = 1256
        server_port_field.update()
        if page:
            show_info_message(page, "Port reset to default")

    server_host_field = ft.TextField(
        label="Server Host",
        value=current_settings['server'].get('host', '127.0.0.1'),
        expand=True,
        on_change=on_host_change
    )

    def reset_host_field(e):
        server_host_field.value = "127.0.0.1"
        current_settings['server']['host'] = "127.0.0.1"
        server_host_field.update()
        if page:
            show_info_message(page, "Host reset to default")

    max_clients_field = ft.TextField(
        label="Max Clients",
        value=str(current_settings['server'].get('max_clients', 50)),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200,
        on_change=on_max_clients_change
    )

    def reset_max_clients_field(e):
        max_clients_field.value = "50"
        max_clients_field.error_text = None
        current_settings['server']['max_clients'] = 50
        max_clients_field.update()
        if page:
            show_info_message(page, "Max clients reset to default")

    log_level_dropdown = ft.Dropdown(
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

    # GUI Settings Fields
    theme_mode_switch = ft.Switch(
        label="Dark Mode",
        value=current_settings['gui'].get('theme_mode', 'dark') == 'dark',
        on_change=on_theme_toggle
    )

    auto_refresh_switch = ft.Switch(
        label="Auto Refresh",
        value=current_settings['gui'].get('auto_refresh', True),
        on_change=on_auto_refresh_toggle
    )

    notifications_switch = ft.Switch(
        label="Show Notifications",
        value=current_settings['gui'].get('notifications', True),
        on_change=on_notifications_toggle
    )

    monitoring_enabled_switch = ft.Switch(
        label="Enable System Monitoring",
        value=current_settings['monitoring'].get('enabled', True),
        on_change=on_monitoring_enabled_toggle
    )

    monitoring_interval_field = ft.TextField(
        label="Monitoring Interval (seconds)",
        value=str(current_settings['monitoring'].get('interval', 2)),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200,
        on_change=on_monitoring_interval_change
    )

    def reset_monitoring_interval_field(e):
        monitoring_interval_field.value = "2"
        monitoring_interval_field.error_text = None
        current_settings['monitoring']['interval'] = 2
        monitoring_interval_field.update()
        if page:
            show_info_message(page, "Monitoring interval reset to default")

    alerts_switch = ft.Switch(
        label="Performance Alerts",
        value=current_settings['monitoring'].get('alerts', True),
        on_change=on_alerts_toggle
    )
    # Additional async handlers for buttons and file operations
    async def save_settings_handler():
        nonlocal is_saving, last_saved
        if is_saving:
            return

        is_saving = True

        try:
            # Perform actual save operation
            success = save_settings_sync(current_settings)
            if success:
                # Update UI on success
                last_saved = datetime.now()
                last_saved_text.value = f"Last saved: {last_saved.strftime('%H:%M:%S')}"
                await last_saved_text.update_async()
                show_success_message(page, "Settings saved successfully")
            else:
                show_error_message(page, "Failed to save settings")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            show_error_message(page, f"Error saving settings: {str(e)}")
        finally:
            is_saving = False

    async def on_save_settings(e):
        logger.info("Saving settings...")
        await save_settings_handler()

    async def on_reset_settings(e):
        def confirm_reset(e):
            nonlocal current_settings
            default_settings = {
                'server': {'port': 1256, 'host': '127.0.0.1', 'max_clients': 50, 'log_level': 'INFO'},
                'gui': {'theme_mode': 'dark', 'auto_refresh': True, 'notifications': True},
                'monitoring': {'enabled': True, 'interval': 2, 'alerts': True}
            }

            current_settings.clear()
            current_settings.update(default_settings)
            update_ui_fields()

            page.dialog.open = False
            page.update()
            show_info_message(page, "Settings reset to defaults")

        def cancel_reset(e):
            page.dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Reset Settings"),
            content=ft.Text("Are you sure you want to reset all settings to their default values? This cannot be undone."),
            actions=[
                ft.TextButton("Cancel", icon=ft.Icons.CANCEL, on_click=cancel_reset, tooltip="Cancel settings reset"),
                ft.TextButton("Reset", icon=ft.Icons.RESET_TV, on_click=confirm_reset, tooltip="Reset all settings to defaults")
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

        # Update all fields efficiently
        for field in [server_port_field, server_host_field, max_clients_field,
                      log_level_dropdown, theme_mode_switch, auto_refresh_switch,
                      notifications_switch, monitoring_enabled_switch,
                      monitoring_interval_field, alerts_switch]:
            field.update()

    async def export_settings_handler():
        """Export settings using proper async pattern."""
        backup_file = f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            success = export_settings_sync(current_settings, backup_file)
            if success:
                show_success_message(page, f"Settings exported to {backup_file}")
            else:
                show_error_message(page, "Failed to export settings")
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            show_error_message(page, "Error exporting settings")

    async def on_export_settings(e):
        logger.info("Exporting settings...")
        await export_settings_handler()

    # File picker for import functionality
    file_picker = None  # Initialize as None and set later

    def initialize_file_picker():
        """Initialize file picker when view is attached to page."""
        nonlocal file_picker
        # Only initialize if not already initialized and page is available
        if file_picker is None and page:
            def pick_files_result(e: ft.FilePickerResultEvent):
                if e.files:
                    async def async_import():
                        try:
                            imported_settings = import_settings_sync(e.files[0].path)
                            if imported_settings:
                                nonlocal current_settings
                                current_settings.clear()
                                current_settings.update(imported_settings)

                                update_ui_fields()

                                show_success_message(page, f"Settings imported from {e.files[0].name}")
                            else:
                                show_error_message(page, "Failed to import settings")
                        except Exception as ex:
                            logger.error(f"Error importing settings: {ex}")
                            show_error_message(page, "Error importing settings")

                    # Use page.run_task for async operations
                    page.run_task(async_import)
                else:
                    show_info_message(page, "Import cancelled")

            file_picker = ft.FilePicker(on_result=pick_files_result)
            # Only add to overlay if page overlay is available
            if hasattr(page, 'overlay'):
                page.overlay.append(file_picker)
                # Only update if page is attached
                if hasattr(page, 'update') and callable(page.update):
                    try:
                        page.update()
                    except Exception as e:
                        logger.warning(f"Could not update page during file picker initialization: {e}")

    async def on_import_settings(e):
        logger.info("Import settings clicked")
        # Initialize file picker if not already done
        initialize_file_picker()
        # Only pick files if file picker was successfully initialized
        if file_picker:
            try:
                file_picker.pick_files(
                    allowed_extensions=["json"],
                    dialog_title="Select Settings File"
                )
            except Exception as e:
                logger.error(f"Error opening file picker: {e}")
                show_error_message(page, "Error opening file picker")
        else:
            show_error_message(page, "File picker not available")

    def create_server_settings():
        """Create server settings form."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Server Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    # Use simple column layout for form fields
                    ft.Column([
                        ft.Text("Port Configuration", size=14, weight=ft.FontWeight.W_500),
                        ft.Row([
                            server_port_field,
                            ft.IconButton(
                                icon=ft.Icons.CLEAR,
                                tooltip="Reset to default (1256)",
                                on_click=reset_port_field,
                                icon_size=16
                            )
                        ], spacing=5)
                    ], spacing=5),
                    ft.Column([
                        ft.Text("Host Configuration", size=14, weight=ft.FontWeight.W_500),
                        ft.Row([
                            server_host_field,
                            ft.IconButton(
                                icon=ft.Icons.CLEAR,
                                tooltip="Reset to default (127.0.0.1)",
                                on_click=reset_host_field,
                                icon_size=16
                            )
                        ], spacing=5)
                    ], spacing=5),
                    ft.Column([
                        ft.Text("Client Limits", size=14, weight=ft.FontWeight.W_500),
                        ft.Row([
                            max_clients_field,
                            ft.IconButton(
                                icon=ft.Icons.CLEAR,
                                tooltip="Reset to default (50)",
                                on_click=reset_max_clients_field,
                                icon_size=16
                            )
                        ], spacing=5)
                    ], spacing=5),
                    ft.Column([
                        ft.Text("Logging", size=14, weight=ft.FontWeight.W_500),
                        log_level_dropdown
                    ], spacing=5)
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
                    # Use simple column layout instead of row with mixed controls
                    ft.Column([
                        ft.Text("Theme Mode:", size=16, weight=ft.FontWeight.W_500),
                        theme_mode_switch
                    ], spacing=5),
                    ft.Divider(),
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
                    # Use simple column layout for monitoring settings
                    ft.Column([
                        ft.Text("System Monitoring", size=16, weight=ft.FontWeight.W_500),
                        monitoring_enabled_switch
                    ], spacing=5),
                    ft.Column([
                        ft.Text("Monitoring Interval", size=16, weight=ft.FontWeight.W_500),
                        ft.Row([
                            monitoring_interval_field,
                            ft.IconButton(
                                icon=ft.Icons.CLEAR,
                                tooltip="Reset to default (2 seconds)",
                                on_click=reset_monitoring_interval_field,
                                icon_size=16
                            )
                        ], spacing=5)
                    ], spacing=5),
                    ft.Column([
                        ft.Text("Performance Alerts", size=16, weight=ft.FontWeight.W_500),
                        alerts_switch
                    ], spacing=5)
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
        # Action buttons using simple Row instead of ResponsiveRow to avoid parent data conflicts
        ft.Row([
            ft.FilledButton(
                "Save Settings",
                icon=ft.Icons.SAVE,
                on_click=on_save_settings,
                tooltip="Save current settings"
            ),
            ft.OutlinedButton(
                "Reset All",
                icon=ft.Icons.RESTORE,
                on_click=on_reset_settings,
                tooltip="Reset all settings to defaults"
            ),
            ft.OutlinedButton(
                "Export Backup",
                icon=ft.Icons.DOWNLOAD,
                on_click=on_export_settings,
                tooltip="Export settings to backup file"
            ),
            ft.TextButton(
                "Import Settings",
                icon=ft.Icons.UPLOAD,
                on_click=on_import_settings,
                tooltip="Import settings from file"
            )
        ], spacing=10, wrap=True),  # Enable wrapping for smaller screens
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

    def schedule_initial_load():
        """Schedule initial data load with proper error handling."""
        async def delayed_load():
            try:
                # Wait for controls to be properly attached
                await asyncio.sleep(0.1)
                # Load settings and update UI
                nonlocal current_settings
                logger.info("Starting background settings load...")
                loaded = load_settings()
                current_settings.clear()
                current_settings.update(loaded)
                logger.info("Settings loaded. Updating UI fields.")
                update_ui_fields()
            except Exception as e:
                logger.error(f"Error during initial settings load: {e}")

        # Use page.run_task for proper async execution if page is available
        if page:
            try:
                page.run_task(delayed_load)
            except Exception as e:
                logger.error(f"Failed to schedule initial load: {e}")

    # Schedule the initial load
    schedule_initial_load()

    return main_view
