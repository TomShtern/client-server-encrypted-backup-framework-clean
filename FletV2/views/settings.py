#!/usr/bin/env python3
"""
Modern Settings View for FletV2
Single-file implementation following Framework Harmony principles.
Refactored from 865-line monolith to clean, modular functions.
"""

import flet as ft
import json
import asyncio
from utils.debug_setup import get_logger
from utils.user_feedback import show_success_message, show_error_message, show_info_message
from pathlib import Path
from datetime import datetime
from config import SETTINGS_FILE, ASYNC_DELAY, MIN_PORT, MAX_PORT, MIN_MAX_CLIENTS

# UTF-8 support
import sys
import os
os.environ.setdefault("PYTHONUTF8", "1")
try:
    from utils import utf8_patch  # noqa: F401
except ImportError:
    pass

logger = get_logger(__name__)


class SettingsState:
    """Modern state management following CLAUDE.md principles."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.current_settings = self._load_default_settings()
        self.is_saving = False
        self.last_saved = None
        self._ui_refs = {}

    def _load_default_settings(self):
        """Load default settings structure."""
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

    async def load_settings(self):
        """Load settings from file asynchronously."""
        try:
            settings_path = Path(SETTINGS_FILE)
            if settings_path.exists():
                with open(settings_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.current_settings.update(loaded)
                self._update_ui_from_settings()
            logger.info("Settings loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")

    def _update_ui_from_settings(self):
        """Update all UI controls with loaded settings."""
        for section_key, controls in self._ui_refs.items():
            section, key = section_key.split('.')
            value = self.current_settings.get(section, {}).get(key)
            if value is not None:
                for control in controls:
                    if hasattr(control, 'value'):
                        if isinstance(control, ft.Switch):
                            control.value = bool(value)
                        else:
                            control.value = str(value)
                        control.update()

    def register_ui_control(self, section: str, key: str, control):
        """Register UI control for automatic updates."""
        section_key = f"{section}.{key}"
        if section_key not in self._ui_refs:
            self._ui_refs[section_key] = []
        self._ui_refs[section_key].append(control)

    async def save_settings(self):
        """Save settings asynchronously."""
        if self.is_saving:
            return False

        self.is_saving = True
        try:
            settings_path = Path(SETTINGS_FILE)
            settings_path.parent.mkdir(parents=True, exist_ok=True)

            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=2, ensure_ascii=False)

            self.last_saved = datetime.now()
            logger.info("Settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
        finally:
            self.is_saving = False

    def update_setting(self, section: str, key: str, value):
        """Update a setting with validation."""
        if section in self.current_settings:
            self.current_settings[section][key] = value
            logger.info(f"Setting updated: {section}.{key} = {value}")
            return True
        return False

    def get_setting(self, section: str, key: str, default=None):
        """Get a setting value safely."""
        return self.current_settings.get(section, {}).get(key, default)


def validate_port(value: str) -> tuple[bool, str]:
    """Validate port number."""
    try:
        port = int(value)
        min_port = getattr(sys.modules[__name__], 'MIN_PORT', 1024)
        max_port = getattr(sys.modules[__name__], 'MAX_PORT', 65535)
        if min_port <= port <= max_port:
            return True, ""
        return False, f"Port must be between {min_port}-{max_port}"
    except ValueError:
        return False, "Please enter a valid number"


def validate_max_clients(value: str) -> tuple[bool, str]:
    """Validate max clients."""
    try:
        clients = int(value)
        if 1 <= clients <= 1000:
            return True, ""
        return False, "Must be between 1-1000"
    except ValueError:
        return False, "Please enter a valid number"


def validate_monitoring_interval(value: str) -> tuple[bool, str]:
    """Validate monitoring interval."""
    try:
        interval = int(value)
        if 1 <= interval <= 60:
            return True, ""
        return False, "Must be between 1-60 seconds"
    except ValueError:
        return False, "Please enter a valid number"


def create_field_handler(state: SettingsState, section: str, key: str, validator=None):
    """Factory for consistent field change handlers."""
    def handler(e):
        value = e.control.value

        if validator:
            is_valid, error_msg = validator(value)
            e.control.error_text = error_msg if not is_valid else None
            if not is_valid:
                e.control.update()
                return

        # Convert to appropriate type for numeric fields
        if key in ['port', 'max_clients', 'interval']:
            try:
                value = int(value)
            except ValueError:
                return

        state.update_setting(section, key, value)
        e.control.update()

        if state.page:
            show_success_message(state.page, f"{key.title().replace('_', ' ')} updated")

    return handler


def create_switch_handler(state: SettingsState, section: str, key: str):
    """Factory for switch toggle handlers."""
    def handler(e):
        value = e.control.value
        state.update_setting(section, key, value)

        if state.page:
            show_success_message(state.page, f"{key.title().replace('_', ' ')} {'enabled' if value else 'disabled'}")

    return handler


def create_reset_button(field: ft.TextField, default_value: str, state: SettingsState):
    """Create reset button for field."""
    def reset_handler(e):
        field.value = default_value
        field.error_text = None
        field.update()
        if state.page:
            show_info_message(state.page, f"{field.label} reset to default")

    return ft.IconButton(
        icon=ft.Icons.REFRESH,
        tooltip=f"Reset to default ({default_value})",
        on_click=reset_handler,
        icon_size=16
    )


def create_server_section(state: SettingsState) -> ft.Card:
    """Create server settings section."""
    port_field = ft.TextField(
        label="Server Port",
        value=str(state.get_setting('server', 'port', 1256)),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200,
        on_change=create_field_handler(state, 'server', 'port', validate_port)
    )
    state.register_ui_control('server', 'port', port_field)

    host_field = ft.TextField(
        label="Server Host",
        value=state.get_setting('server', 'host', '127.0.0.1'),
        expand=True,
        on_change=create_field_handler(state, 'server', 'host')
    )
    state.register_ui_control('server', 'host', host_field)

    max_clients_field = ft.TextField(
        label="Max Clients",
        value=str(state.get_setting('server', 'max_clients', 50)),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200,
        on_change=create_field_handler(state, 'server', 'max_clients', validate_max_clients)
    )
    state.register_ui_control('server', 'max_clients', max_clients_field)

    log_level_dropdown = ft.Dropdown(
        label="Log Level",
        value=state.get_setting('server', 'log_level', 'INFO'),
        options=[
            ft.dropdown.Option("DEBUG", "Debug"),
            ft.dropdown.Option("INFO", "Info"),
            ft.dropdown.Option("WARNING", "Warning"),
            ft.dropdown.Option("ERROR", "Error")
        ],
        width=200,
        on_change=create_field_handler(state, 'server', 'log_level')
    )
    state.register_ui_control('server', 'log_level', log_level_dropdown)

    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Server Configuration", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Column([
                    ft.Text("Port Configuration", size=14, weight=ft.FontWeight.W_500),
                    ft.Row([port_field, create_reset_button(port_field, "1256", state)], spacing=5)
                ], spacing=5),
                ft.Column([
                    ft.Text("Host Configuration", size=14, weight=ft.FontWeight.W_500),
                    ft.Row([host_field, create_reset_button(host_field, "127.0.0.1", state)], spacing=5)
                ], spacing=5),
                ft.Column([
                    ft.Text("Client Limits", size=14, weight=ft.FontWeight.W_500),
                    ft.Row([max_clients_field, create_reset_button(max_clients_field, "50", state)], spacing=5)
                ], spacing=5),
                ft.Column([
                    ft.Text("Logging", size=14, weight=ft.FontWeight.W_500),
                    log_level_dropdown
                ], spacing=5)
            ], spacing=15),
            padding=20
        )
    )


def create_gui_section(state: SettingsState) -> ft.Card:
    """Create GUI settings section."""
    def handle_theme_toggle(e):
        new_mode = "light" if state.get_setting('gui', 'theme_mode') == "dark" else "dark"
        state.update_setting('gui', 'theme_mode', new_mode)

        if state.page:
            state.page.theme_mode = ft.ThemeMode.LIGHT if new_mode == "light" else ft.ThemeMode.DARK
            state.page.update()
            show_info_message(state.page, f"Theme switched to {new_mode} mode")

    theme_switch = ft.Switch(
        label="Dark Mode",
        value=state.get_setting('gui', 'theme_mode', 'dark') == 'dark',
        on_change=handle_theme_toggle
    )

    auto_refresh_switch = ft.Switch(
        label="Auto Refresh",
        value=state.get_setting('gui', 'auto_refresh', True),
        on_change=create_switch_handler(state, 'gui', 'auto_refresh')
    )
    state.register_ui_control('gui', 'auto_refresh', auto_refresh_switch)

    notifications_switch = ft.Switch(
        label="Show Notifications",
        value=state.get_setting('gui', 'notifications', True),
        on_change=create_switch_handler(state, 'gui', 'notifications')
    )
    state.register_ui_control('gui', 'notifications', notifications_switch)

    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("GUI Configuration", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Column([
                    ft.Text("Theme Mode:", size=16, weight=ft.FontWeight.W_500),
                    theme_switch
                ], spacing=5),
                ft.Divider(),
                auto_refresh_switch,
                notifications_switch
            ], spacing=15),
            padding=20
        )
    )


def create_monitoring_section(state: SettingsState) -> ft.Card:
    """Create monitoring settings section."""
    monitoring_switch = ft.Switch(
        label="Enable System Monitoring",
        value=state.get_setting('monitoring', 'enabled', True),
        on_change=create_switch_handler(state, 'monitoring', 'enabled')
    )
    state.register_ui_control('monitoring', 'enabled', monitoring_switch)

    interval_field = ft.TextField(
        label="Monitoring Interval (seconds)",
        value=str(state.get_setting('monitoring', 'interval', 2)),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200,
        on_change=create_field_handler(state, 'monitoring', 'interval', validate_monitoring_interval)
    )
    state.register_ui_control('monitoring', 'interval', interval_field)

    alerts_switch = ft.Switch(
        label="Performance Alerts",
        value=state.get_setting('monitoring', 'alerts', True),
        on_change=create_switch_handler(state, 'monitoring', 'alerts')
    )
    state.register_ui_control('monitoring', 'alerts', alerts_switch)

    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Monitoring Configuration", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Column([
                    ft.Text("System Monitoring", size=16, weight=ft.FontWeight.W_500),
                    monitoring_switch
                ], spacing=5),
                ft.Column([
                    ft.Text("Monitoring Interval", size=16, weight=ft.FontWeight.W_500),
                    ft.Row([interval_field, create_reset_button(interval_field, "2", state)], spacing=5)
                ], spacing=5),
                ft.Column([
                    ft.Text("Performance Alerts", size=16, weight=ft.FontWeight.W_500),
                    alerts_switch
                ], spacing=5)
            ], spacing=15),
            padding=20
        )
    )


async def export_settings(state: SettingsState):
    """Export settings to backup file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"settings_backup_{timestamp}.json"

    try:
        backup_path = Path(backup_file)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(state.current_settings, f, indent=2, ensure_ascii=False)

        show_success_message(state.page, f"Settings exported to {backup_file}")
        return True
    except Exception as e:
        logger.error(f"Export failed: {e}")
        show_error_message(state.page, "Failed to export settings")
        return False


async def import_settings(state: SettingsState, file_path: str):
    """Import settings from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            imported = json.load(f)

        if not isinstance(imported, dict):
            raise ValueError("Invalid settings format")

        # Validate structure and merge with defaults
        default_settings = state._load_default_settings()
        for section in default_settings:
            if section in imported:
                default_settings[section].update(imported[section])

        state.current_settings = default_settings
        state._update_ui_from_settings()
        show_success_message(state.page, "Settings imported successfully")
        return True
    except Exception as e:
        logger.error(f"Import failed: {e}")
        show_error_message(state.page, "Failed to import settings")
        return False


def create_settings_view(server_bridge, page: ft.Page, state_manager=None) -> ft.Control:
    """
    Create modern settings view following Framework Harmony principles.
    Single-file implementation with clean, modular functions.
    """
    logger.info("Creating modern settings view")

    # Initialize state management
    settings_state = SettingsState(page)

    # Status display
    last_saved_text = ft.Text(
        value="Last saved: Never",
        size=12,
        color=ft.Colors.ON_SURFACE
    )

    # Progress indicator for save operations
    save_progress = ft.ProgressRing(width=16, height=16, visible=False)

    # Action handlers
    async def save_settings_handler(e):
        # Show saving feedback
        save_progress.visible = True
        last_saved_text.value = "Saving..."
        last_saved_text.update()
        save_progress.update()

        success = await settings_state.save_settings()

        # Hide progress and update status
        save_progress.visible = False
        if success:
            last_saved_text.value = f"Last saved: {settings_state.last_saved.strftime('%H:%M:%S')}"
            last_saved_text.update()  # Framework-harmonious: use control.update()
            save_progress.update()
            show_success_message(page, "Settings saved successfully")
        else:
            last_saved_text.value = "Save failed"
            last_saved_text.update()
            save_progress.update()
            show_error_message(page, "Failed to save settings")

    def reset_all_settings(e):
        def confirm_reset(e):
            settings_state.current_settings = settings_state._load_default_settings()
            settings_state._update_ui_from_settings()
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

    def export_handler(e):
        page.run_task(export_settings, settings_state)

    # File picker for import
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            page.run_task(import_settings, settings_state, e.files[0].path)
        else:
            show_info_message(page, "Import cancelled")

    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)

    def import_handler(e):
        try:
            file_picker.pick_files(
                allowed_extensions=["json"],
                dialog_title="Select Settings File"
            )
        except Exception as e:
            logger.error(f"Error opening file picker: {e}")
            show_error_message(page, "Error opening file picker")

    # Build main view using modern Flet patterns
    main_view = ft.Column([
        # Header
        ft.Row([
            ft.Icon(ft.Icons.SETTINGS, size=24),
            ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            last_saved_text,
            save_progress  # Progress indicator for save operations
        ]),
        ft.Divider(),

        # Action buttons
        ft.Row([
            ft.FilledButton(
                "Save Settings",
                icon=ft.Icons.SAVE,
                on_click=save_settings_handler,
                tooltip="Save current settings"
            ),
            ft.OutlinedButton(
                "Reset All",
                icon=ft.Icons.RESTORE,
                on_click=reset_all_settings,
                tooltip="Reset all settings to defaults"
            ),
            ft.OutlinedButton(
                "Export Backup",
                icon=ft.Icons.DOWNLOAD,
                on_click=export_handler,
                tooltip="Export settings to backup file"
            ),
            ft.TextButton(
                "Import Settings",
                icon=ft.Icons.UPLOAD,
                on_click=import_handler,
                tooltip="Import settings from file"
            )
        ], spacing=10, wrap=True),
        ft.Divider(),

        # Settings tabs using Flet's built-in Tabs component
        ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Server",
                    icon=ft.Icons.SETTINGS,
                    content=create_server_section(settings_state)
                ),
                ft.Tab(
                    text="GUI",
                    icon=ft.Icons.PALETTE,
                    content=create_gui_section(settings_state)
                ),
                ft.Tab(
                    text="Monitoring",
                    icon=ft.Icons.MONITOR_HEART,
                    content=create_monitoring_section(settings_state)
                )
            ],
            expand=True
        )
    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)

    # Load settings asynchronously
    page.run_task(settings_state.load_settings)

    return main_view