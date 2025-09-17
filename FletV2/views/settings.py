#!/usr/bin/env python3
"""
Simplified Settings View - The Flet Way
~400 lines instead of 968+ lines of framework fighting!

Core Principle: Use Flet's built-in Tabs, TextField, Switch, and Dropdown.
Clean settings management with server integration and simple validation.
"""

import flet as ft
from typing import Optional, Dict, Any
import json

from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.ui_components import themed_card, themed_button
from utils.user_feedback import show_success_message, show_error_message
from config import SETTINGS_FILE

logger = get_logger(__name__)


def create_settings_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    _state_manager: StateManager
) -> ft.Control:
    """Simple settings view using Flet's built-in components."""
    logger.info("Creating simplified settings view")

    # Simple state management
    current_settings = {}

    # Default settings structure
    def get_default_settings() -> Dict[str, Any]:
        """Get default settings structure."""
        return {
            "server": {
                "port": 1256,
                "host": "127.0.0.1",
                "max_clients": 50,
                "timeout": 30,
                "enable_ssl": False,
                "ssl_cert_path": "",
                "ssl_key_path": ""
            },
            "gui": {
                "theme_mode": "system",
                "color_scheme": "blue",
                "auto_refresh": True,
                "refresh_interval": 5,
                "auto_resize": True
            },
            "monitoring": {
                "enabled": True,
                "refresh_interval": 5.0,
                "cpu_threshold": 80.0,
                "memory_threshold": 85.0,
                "disk_threshold": 90.0
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file_path": "logs/server.log",
                "max_size_mb": 100,
                "max_files": 5
            },
            "security": {
                "require_auth": False,
                "api_key": "",
                "max_login_attempts": 3,
                "session_timeout": 3600
            },
            "backup": {
                "auto_backup": True,
                "backup_path": "backups/",
                "backup_interval_hours": 24,
                "retention_days": 30,
                "compress_backups": True
            }
        }

    # Load settings from server or file
    def load_settings():
        """Load settings using server bridge or local file."""
        nonlocal current_settings

        if server_bridge:
            try:
                result = server_bridge.load_settings()
                if result.get('success'):
                    current_settings = result.get('data', get_default_settings())
                else:
                    current_settings = get_default_settings()
            except Exception:
                current_settings = get_default_settings()
        else:
            # Load from local file
            try:
                if SETTINGS_FILE.exists():
                    with open(SETTINGS_FILE, 'r') as f:
                        loaded = json.load(f)
                        current_settings = {**get_default_settings(), **loaded}
                else:
                    current_settings = get_default_settings()
            except Exception:
                current_settings = get_default_settings()

        update_ui_from_settings()

    # Save settings to server or file
    def save_settings():
        """Save settings using server bridge or local file."""
        # Validate first
        validation_errors = validate_settings()
        if validation_errors:
            show_error_message(page, f"Validation failed: {'; '.join(validation_errors)}")
            return

        if server_bridge:
            try:
                result = server_bridge.save_settings(current_settings)
                if result.get('success'):
                    show_success_message(page, "Settings saved to server successfully")
                else:
                    show_error_message(page, f"Server save failed: {result.get('error', 'Unknown error')}")
            except Exception as ex:
                show_error_message(page, f"Error saving to server: {ex}")
        else:
            # Save to local file
            try:
                SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(SETTINGS_FILE, 'w') as f:
                    json.dump(current_settings, f, indent=2)
                show_success_message(page, "Settings saved locally")
            except Exception as ex:
                show_error_message(page, f"Error saving settings: {ex}")

    # Simple validation
    def validate_settings() -> list:
        """Validate current settings and return list of errors."""
        errors = []

        # Server validation
        server = current_settings.get("server", {})
        port = server.get("port", 0)
        if not isinstance(port, int) or port < 1024 or port > 65535:
            errors.append("Port must be between 1024-65535")

        max_clients = server.get("max_clients", 0)
        if not isinstance(max_clients, int) or max_clients < 1 or max_clients > 1000:
            errors.append("Max clients must be between 1-1000")

        # SSL validation
        if server.get("enable_ssl", False):
            if not server.get("ssl_cert_path", "").strip():
                errors.append("SSL certificate path required when SSL enabled")
            if not server.get("ssl_key_path", "").strip():
                errors.append("SSL key path required when SSL enabled")

        # Monitoring validation
        monitoring = current_settings.get("monitoring", {})
        if monitoring.get("enabled", False):
            cpu_threshold = monitoring.get("cpu_threshold", 0)
            if not isinstance(cpu_threshold, (int, float)) or cpu_threshold <= 0 or cpu_threshold > 100:
                errors.append("CPU threshold must be between 1-100")

            memory_threshold = monitoring.get("memory_threshold", 0)
            if not isinstance(memory_threshold, (int, float)) or memory_threshold <= 0 or memory_threshold > 100:
                errors.append("Memory threshold must be between 1-100")

        # Backup validation
        backup = current_settings.get("backup", {})
        if backup.get("auto_backup", False):
            interval = backup.get("backup_interval_hours", 0)
            if not isinstance(interval, (int, float)) or interval <= 0:
                errors.append("Backup interval must be greater than 0")

            if not backup.get("backup_path", "").strip():
                errors.append("Backup path required when auto-backup enabled")

        return errors

    # UI Controls - Server Tab
    server_port_field = ft.TextField(label="Port", value="1256", width=100)
    server_host_field = ft.TextField(label="Host", value="127.0.0.1", width=200)
    server_max_clients_field = ft.TextField(label="Max Clients", value="50", width=100)
    server_timeout_field = ft.TextField(label="Timeout (seconds)", value="30", width=100)
    server_enable_ssl_switch = ft.Switch(label="Enable SSL", value=False)
    server_ssl_cert_field = ft.TextField(label="SSL Certificate Path", value="", width=300)
    server_ssl_key_field = ft.TextField(label="SSL Key Path", value="", width=300)

    # UI Controls - GUI Tab
    gui_theme_dropdown = ft.Dropdown(
        label="Theme Mode",
        value="system",
        options=[
            ft.dropdown.Option("light", "Light"),
            ft.dropdown.Option("dark", "Dark"),
            ft.dropdown.Option("system", "System"),
        ],
        width=150
    )
    gui_color_dropdown = ft.Dropdown(
        label="Color Scheme",
        value="blue",
        options=[
            ft.dropdown.Option("blue", "Blue"),
            ft.dropdown.Option("green", "Green"),
            ft.dropdown.Option("purple", "Purple"),
            ft.dropdown.Option("orange", "Orange"),
        ],
        width=150
    )
    gui_auto_refresh_switch = ft.Switch(label="Auto Refresh", value=True)
    gui_refresh_interval_field = ft.TextField(label="Refresh Interval (seconds)", value="5", width=100)
    gui_auto_resize_switch = ft.Switch(label="Auto Resize", value=True)

    # UI Controls - Monitoring Tab
    monitoring_enabled_switch = ft.Switch(label="Enable Monitoring", value=True)
    monitoring_refresh_field = ft.TextField(label="Refresh Interval (seconds)", value="5.0", width=100)
    monitoring_cpu_field = ft.TextField(label="CPU Threshold (%)", value="80", width=100)
    monitoring_memory_field = ft.TextField(label="Memory Threshold (%)", value="85", width=100)
    monitoring_disk_field = ft.TextField(label="Disk Threshold (%)", value="90", width=100)

    # UI Controls - Logging Tab
    logging_enabled_switch = ft.Switch(label="Enable Logging", value=True)
    logging_level_dropdown = ft.Dropdown(
        label="Log Level",
        value="INFO",
        options=[
            ft.dropdown.Option("DEBUG", "Debug"),
            ft.dropdown.Option("INFO", "Info"),
            ft.dropdown.Option("WARNING", "Warning"),
            ft.dropdown.Option("ERROR", "Error"),
        ],
        width=120
    )
    logging_file_field = ft.TextField(label="Log File Path", value="logs/server.log", width=300)
    logging_max_size_field = ft.TextField(label="Max Size (MB)", value="100", width=100)
    logging_max_files_field = ft.TextField(label="Max Files", value="5", width=100)

    # UI Controls - Security Tab
    security_require_auth_switch = ft.Switch(label="Require Authentication", value=False)
    security_api_key_field = ft.TextField(label="API Key", value="", password=True, width=300)
    security_max_attempts_field = ft.TextField(label="Max Login Attempts", value="3", width=100)
    security_session_timeout_field = ft.TextField(label="Session Timeout (seconds)", value="3600", width=150)

    # UI Controls - Backup Tab
    backup_auto_switch = ft.Switch(label="Auto Backup", value=True)
    backup_path_field = ft.TextField(label="Backup Path", value="backups/", width=300)
    backup_interval_field = ft.TextField(label="Backup Interval (hours)", value="24", width=100)
    backup_retention_field = ft.TextField(label="Retention Days", value="30", width=100)
    backup_compress_switch = ft.Switch(label="Compress Backups", value=True)

    # Update UI from settings
    def update_ui_from_settings():
        """Update UI controls from current settings."""
        server = current_settings.get("server", {})
        server_port_field.value = str(server.get("port", 1256))
        server_host_field.value = server.get("host", "127.0.0.1")
        server_max_clients_field.value = str(server.get("max_clients", 50))
        server_timeout_field.value = str(server.get("timeout", 30))
        server_enable_ssl_switch.value = server.get("enable_ssl", False)
        server_ssl_cert_field.value = server.get("ssl_cert_path", "")
        server_ssl_key_field.value = server.get("ssl_key_path", "")

        gui = current_settings.get("gui", {})
        gui_theme_dropdown.value = gui.get("theme_mode", "system")
        gui_color_dropdown.value = gui.get("color_scheme", "blue")
        gui_auto_refresh_switch.value = gui.get("auto_refresh", True)
        gui_refresh_interval_field.value = str(gui.get("refresh_interval", 5))
        gui_auto_resize_switch.value = gui.get("auto_resize", True)

        monitoring = current_settings.get("monitoring", {})
        monitoring_enabled_switch.value = monitoring.get("enabled", True)
        monitoring_refresh_field.value = str(monitoring.get("refresh_interval", 5.0))
        monitoring_cpu_field.value = str(monitoring.get("cpu_threshold", 80.0))
        monitoring_memory_field.value = str(monitoring.get("memory_threshold", 85.0))
        monitoring_disk_field.value = str(monitoring.get("disk_threshold", 90.0))

        logging = current_settings.get("logging", {})
        logging_enabled_switch.value = logging.get("enabled", True)
        logging_level_dropdown.value = logging.get("level", "INFO")
        logging_file_field.value = logging.get("file_path", "logs/server.log")
        logging_max_size_field.value = str(logging.get("max_size_mb", 100))
        logging_max_files_field.value = str(logging.get("max_files", 5))

        security = current_settings.get("security", {})
        security_require_auth_switch.value = security.get("require_auth", False)
        security_api_key_field.value = security.get("api_key", "")
        security_max_attempts_field.value = str(security.get("max_login_attempts", 3))
        security_session_timeout_field.value = str(security.get("session_timeout", 3600))

        backup = current_settings.get("backup", {})
        backup_auto_switch.value = backup.get("auto_backup", True)
        backup_path_field.value = backup.get("backup_path", "backups/")
        backup_interval_field.value = str(backup.get("backup_interval_hours", 24))
        backup_retention_field.value = str(backup.get("retention_days", 30))
        backup_compress_switch.value = backup.get("compress_backups", True)

        # Update all controls - only if they're already attached to page
        for control in [server_port_field, server_host_field, server_max_clients_field, server_timeout_field,
                       server_enable_ssl_switch, server_ssl_cert_field, server_ssl_key_field,
                       gui_theme_dropdown, gui_color_dropdown, gui_auto_refresh_switch, gui_refresh_interval_field, gui_auto_resize_switch,
                       monitoring_enabled_switch, monitoring_refresh_field, monitoring_cpu_field, monitoring_memory_field, monitoring_disk_field,
                       logging_enabled_switch, logging_level_dropdown, logging_file_field, logging_max_size_field, logging_max_files_field,
                       security_require_auth_switch, security_api_key_field, security_max_attempts_field, security_session_timeout_field,
                       backup_auto_switch, backup_path_field, backup_interval_field, backup_retention_field, backup_compress_switch]:
            if hasattr(control, 'page') and control.page:
                control.update()

    # Safe type conversion helpers
    def safe_int(value: str | None, default: int = 0) -> int:
        """Safely convert string to int with fallback."""
        if value is None or value == "":
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def safe_float(value: str | None, default: float = 0.0) -> float:
        """Safely convert string to float with fallback."""
        if value is None or value == "":
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    # Update settings from UI
    def update_settings_from_ui():
        """Update current settings from UI controls."""
        try:
            current_settings["server"] = {
                "port": safe_int(server_port_field.value, 8080),
                "host": server_host_field.value or "localhost",
                "max_clients": safe_int(server_max_clients_field.value, 10),
                "timeout": safe_int(server_timeout_field.value, 30),
                "enable_ssl": server_enable_ssl_switch.value,
                "ssl_cert_path": server_ssl_cert_field.value,
                "ssl_key_path": server_ssl_key_field.value
            }

            current_settings["gui"] = {
                "theme_mode": gui_theme_dropdown.value or "system",
                "color_scheme": gui_color_dropdown.value or "blue",
                "auto_refresh": gui_auto_refresh_switch.value,
                "refresh_interval": safe_int(gui_refresh_interval_field.value, 5),
                "auto_resize": gui_auto_resize_switch.value
            }

            current_settings["monitoring"] = {
                "enabled": monitoring_enabled_switch.value,
                "refresh_interval": safe_float(monitoring_refresh_field.value, 1.0),
                "cpu_threshold": safe_float(monitoring_cpu_field.value, 80.0),
                "memory_threshold": safe_float(monitoring_memory_field.value, 85.0),
                "disk_threshold": safe_float(monitoring_disk_field.value, 90.0)
            }

            current_settings["logging"] = {
                "enabled": logging_enabled_switch.value,
                "level": logging_level_dropdown.value or "INFO",
                "file_path": logging_file_field.value or "app.log",
                "max_size_mb": safe_int(logging_max_size_field.value, 10),
                "max_files": safe_int(logging_max_files_field.value, 5)
            }

            current_settings["security"] = {
                "require_auth": security_require_auth_switch.value,
                "api_key": security_api_key_field.value or "",
                "max_login_attempts": safe_int(security_max_attempts_field.value, 3),
                "session_timeout": safe_int(security_session_timeout_field.value, 30)
            }

            current_settings["backup"] = {
                "auto_backup": backup_auto_switch.value,
                "backup_path": backup_path_field.value or "./backups",
                "backup_interval_hours": safe_int(backup_interval_field.value, 24),
                "retention_days": safe_int(backup_retention_field.value, 30),
                "compress_backups": backup_compress_switch.value
            }
        except ValueError as e:
            show_error_message(page, f"Invalid input: {e}")
            return False
        return True

    # Action handlers
    def on_save_click(_e):
        """Handle save button click."""
        if update_settings_from_ui():
            save_settings()

    def on_load_click(_e):
        """Handle load button click."""
        load_settings()
        show_success_message(page, "Settings loaded")

    def on_reset_click(_e):
        """Handle reset button click."""
        nonlocal current_settings
        current_settings = get_default_settings()
        update_ui_from_settings()
        show_success_message(page, "Settings reset to defaults")

    def on_export_click(_e):
        """Handle export button click."""
        def save_export(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    update_settings_from_ui()
                    with open(e.path, 'w') as f:
                        json.dump(current_settings, f, indent=2)
                    show_success_message(page, f"Settings exported to {e.path}")
                except Exception as ex:
                    show_error_message(page, f"Export failed: {ex}")

        file_picker = ft.FilePicker(on_result=save_export)
        page.overlay.append(file_picker)
        file_picker.save_file(
            dialog_title="Export Settings",
            file_name="settings_export.json",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"]
        )

    def on_import_click(_e):
        """Handle import button click."""
        def load_import(e: ft.FilePickerResultEvent):
            if e.files:
                try:
                    with open(e.files[0].path, 'r') as f:
                        imported = json.load(f)

                    # Merge with defaults
                    current_settings.update(imported)
                    update_ui_from_settings()
                    show_success_message(page, "Settings imported successfully")
                except Exception as ex:
                    show_error_message(page, f"Import failed: {ex}")

        file_picker = ft.FilePicker(on_result=load_import)
        page.overlay.append(file_picker)
        file_picker.pick_files(
            dialog_title="Import Settings",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"]
        )

    # Action buttons
    actions_row = ft.Row([
        themed_button("Save", on_save_click, "filled", ft.Icons.SAVE),
        themed_button("Load", on_load_click, "outlined", ft.Icons.REFRESH),
        themed_button("Reset", on_reset_click, "outlined", ft.Icons.RESTORE),
        themed_button("Export", on_export_click, "outlined", ft.Icons.UPLOAD),
        themed_button("Import", on_import_click, "outlined", ft.Icons.DOWNLOAD),
    ], spacing=10)

    # Create tabs with settings sections
    settings_tabs = ft.Tabs(
        tabs=[
            ft.Tab(
                text="Server",
                icon=ft.Icons.DNS,
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Server Configuration", size=20, weight=ft.FontWeight.BOLD),
                        ft.Row([server_port_field, server_host_field], spacing=10),
                        ft.Row([server_max_clients_field, server_timeout_field], spacing=10),
                        server_enable_ssl_switch,
                        ft.Row([server_ssl_cert_field], spacing=10),
                        ft.Row([server_ssl_key_field], spacing=10),
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20
                )
            ),
            ft.Tab(
                text="Interface",
                icon=ft.Icons.PALETTE,
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("User Interface Settings", size=20, weight=ft.FontWeight.BOLD),
                        ft.Row([gui_theme_dropdown, gui_color_dropdown], spacing=10),
                        gui_auto_refresh_switch,
                        gui_refresh_interval_field,
                        gui_auto_resize_switch,
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20
                )
            ),
            ft.Tab(
                text="Monitoring",
                icon=ft.Icons.MONITOR_HEART,
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("System Monitoring", size=20, weight=ft.FontWeight.BOLD),
                        monitoring_enabled_switch,
                        monitoring_refresh_field,
                        ft.Row([monitoring_cpu_field, monitoring_memory_field, monitoring_disk_field], spacing=10),
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20
                )
            ),
            ft.Tab(
                text="Logging",
                icon=ft.Icons.ARTICLE,
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Logging Configuration", size=20, weight=ft.FontWeight.BOLD),
                        logging_enabled_switch,
                        ft.Row([logging_level_dropdown, logging_max_size_field, logging_max_files_field], spacing=10),
                        logging_file_field,
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20
                )
            ),
            ft.Tab(
                text="Security",
                icon=ft.Icons.SECURITY,
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Security Settings", size=20, weight=ft.FontWeight.BOLD),
                        security_require_auth_switch,
                        security_api_key_field,
                        ft.Row([security_max_attempts_field, security_session_timeout_field], spacing=10),
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20
                )
            ),
            ft.Tab(
                text="Backup",
                icon=ft.Icons.BACKUP,
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Backup Configuration", size=20, weight=ft.FontWeight.BOLD),
                        backup_auto_switch,
                        backup_path_field,
                        ft.Row([backup_interval_field, backup_retention_field], spacing=10),
                        backup_compress_switch,
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20
                )
            ),
        ],
        expand=True
    )

    # Main layout
    main_content = ft.Column([
        ft.Row([
            ft.Icon(ft.Icons.SETTINGS, size=28, color=ft.Colors.PRIMARY),
            ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD),
        ], spacing=10),
        actions_row,
        ft.Container(
            content=settings_tabs,
            expand=True,
            padding=10,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE
        )
    ], expand=True, spacing=20)

    # Create the main container
    settings_container = themed_card(main_content, "Settings Management")

    def setup_subscriptions():
        """Setup subscriptions and initial data loading after view is added to page."""
        load_settings()

    def dispose():
        """Clean up subscriptions and resources."""
        logger.debug("Disposing settings view")
        # No subscriptions to clean up currently

    return settings_container, dispose, setup_subscriptions