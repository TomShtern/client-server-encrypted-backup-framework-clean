#!/usr/bin/env python3
"""Clean, reliable Settings view for Flet 0.28.3.

Simple by design:
- Tabs with ListView per tab (predictable sizing/scrolling in web/desktop)
- Robust load/save with ServerBridge when present; JSON fallback otherwise
- Minimal validators and field binding
"""

from __future__ import annotations

import asyncio
import contextlib
import copy
import json
from collections.abc import Callable, Coroutine
from typing import Any

import aiofiles
import flet as ft

try:
    from ..config import SETTINGS_FILE
    from ..utils.async_helpers import debounce, run_sync_in_executor, safe_server_call
    from ..utils.debug_setup import get_logger
    from ..utils.server_bridge import ServerBridge
    from ..utils.simple_state import SimpleState
    from ..utils.ui_builders import create_action_button, create_view_header
except Exception:  # pragma: no cover
    from FletV2.config import SETTINGS_FILE  # type: ignore
    from FletV2.utils.async_helpers import debounce, run_sync_in_executor, safe_server_call  # type: ignore
    from FletV2.utils.debug_setup import get_logger  # type: ignore
    from FletV2.utils.server_bridge import ServerBridge  # type: ignore
    from FletV2.utils.simple_state import SimpleState  # type: ignore
    from FletV2.utils.ui_builders import create_action_button, create_view_header  # type: ignore


logger = get_logger(__name__)

Validator = Callable[[Any], tuple[bool, str | None]]
Parser = Callable[[Any], Any]

COLOR_SEEDS: dict[str, str] = {
    "blue": "#3B82F6",
    "indigo": "#6366F1",
    "purple": "#8B5CF6",
    "pink": "#EC4899",
    "green": "#10B981",
    "orange": "#F59E0B",
    "red": "#EF4444",
}

# Reused label constants (deduplicate literals for linters)
LABEL_MAX_CLIENTS = "Max clients"
LABEL_CERT_PATH = "Certificate path"
LABEL_KEY_PATH = "Key path"
LABEL_REFRESH_INTERVAL = "Refresh interval"
LABEL_CPU_THRESHOLD = "CPU threshold"
LABEL_MEMORY_THRESHOLD = "Memory threshold"
LABEL_DISK_THRESHOLD = "Disk threshold"
LABEL_LOG_FILE_PATH = "Log file path"
LABEL_API_KEY = "API key"
LABEL_MAX_LOGIN_ATTEMPTS = "Max login attempts"
LABEL_SESSION_TIMEOUT = "Session timeout"
LABEL_BACKUP_PATH = "Backup path"
LABEL_BACKUP_INTERVAL = "Backup interval"

DEFAULT_SETTINGS: dict[str, dict[str, Any]] = {
    "server": {
        "port": 1256,
        "host": "127.0.0.1",
        "max_clients": 50,
        "timeout": 30,
        "enable_ssl": False,
        "ssl_cert_path": "",
        "ssl_key_path": "",
    },
    "gui": {
        "theme_mode": "system",
        "color_scheme": "blue",
        "auto_refresh": True,
        "refresh_interval": 5,
        "auto_resize": True,
    },
    "monitoring": {
        "enabled": True,
        "refresh_interval": 5,
        "cpu_threshold": 80,
        "memory_threshold": 85,
        "disk_threshold": 90,
    },
    "logging": {
        "enabled": True,
        "level": "INFO",
        "file_path": "logs/server.log",
        "max_size_mb": 100,
        "max_files": 5,
    },
    "security": {
        "require_auth": False,
        "api_key": "",
        "max_login_attempts": 3,
        "session_timeout": 3600,
    },
    "backup": {
        "auto_backup": True,
        "backup_path": "backups/",
        "backup_interval_hours": 24,
        "retention_days": 30,
        "compress_backups": True,
    },
}


# ==============================================================================
# SECTION 1: HELPER FUNCTIONS
# Validators, parsers, and utility functions for settings management
# ==============================================================================


def _merge_settings(data: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    merged = copy.deepcopy(DEFAULT_SETTINGS)
    if isinstance(data, dict):
        for section, values in data.items():
            if section in merged and isinstance(values, dict):
                merged[section].update(values)
    return merged


def _safe_int(value: Any) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def _require(label: str) -> Validator:
    def _validator(value: Any) -> tuple[bool, str | None]:
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"{label} is required"
        return True, None

    return _validator


def _numeric_range(min_value: float, max_value: float, label: str) -> Validator:
    def _validator(value: Any) -> tuple[bool, str | None]:
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            return False, f"{label} must be numeric"
        if numeric_value < min_value or numeric_value > max_value:
            return False, f"{label} must be between {min_value:g}-{max_value:g}"
        return True, None

    return _validator


def _row(label: str, control: ft.Control, desc: str | None = None) -> ft.Container:
    """Compact horizontal field row - label left, control right, tooltip for description."""
    is_switch = isinstance(control, ft.Switch)

    # Set tooltip if description provided
    if desc and hasattr(control, "tooltip"):
        control.tooltip = desc

    # Horizontal layout for all field types: label left, control right
    main_row = ft.Row(
        [
            ft.Container(
                content=ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE),
                width=140 if not is_switch else None,
                expand=is_switch,
            ),
            control,
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    return ft.Container(
        content=main_row,
        padding=ft.padding.symmetric(horizontal=16, vertical=6),
        border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.08, ft.Colors.OUTLINE))),
    )


# ==============================================================================
# SECTION 2: SETTINGS VIEW CLASS
# Main settings management with embedded state and UI logic
# ==============================================================================


class _SettingsView:
    def __init__(
        self,
        page: ft.Page,
        server_bridge: ServerBridge | None,
        state_manager: SimpleState | None,
        global_search: ft.Control | None,
    ) -> None:
        self.page = page
        self.server_bridge = server_bridge
        self.state_manager = state_manager
        self.global_search = global_search
        self.data = copy.deepcopy(DEFAULT_SETTINGS)
        self.controls: dict[tuple[str, str], ft.Control] = {}
        self.parsers: dict[tuple[str, str], Parser] = {}
        self.validators: dict[tuple[str, str], Validator] = {}
        self.status_text = ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        self._is_disposed = False

        # Autosave toggle for status bar
        self._autosave_ref = ft.Ref[ft.Switch]()
        self._autosave_ref.current = ft.Switch(value=True, label="")

        self._export_picker = ft.FilePicker(on_result=self._handle_export_result)
        self._import_picker = ft.FilePicker(on_result=self._handle_import_result)

        @debounce(1.5)
        async def _auto_save() -> None:
            await self.persist(auto=True)

        self._autosave = _auto_save

    def build(self) -> ft.Control:
        self._ensure_overlay(self._export_picker)
        self._ensure_overlay(self._import_picker)

        # Note: Global search is in the app-level header (main.py), not view-level
        header_actions: list[ft.Control] = [
            create_action_button("Export", self._on_export_clicked, icon=ft.Icons.UPLOAD, primary=False),
            create_action_button("Import", self._on_import_clicked, icon=ft.Icons.DOWNLOAD, primary=False),
            create_action_button("Reset", self._on_reset_clicked, icon=ft.Icons.RESTORE, primary=False),
            create_action_button("Save", self._on_save_clicked, icon=ft.Icons.SAVE),
        ]

        header = create_view_header(
            "Settings",
            icon=ft.Icons.SETTINGS,
            description="Configure networking, interface, monitoring, logging, security, and backup policies.",
            actions=header_actions,
        )

        status_bar = self._build_status_bar()

        tabs = ft.Tabs(
            expand=True,
            height=self._compute_tabs_height(),
            divider_color=ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE),
            animation_duration=300,
            scrollable=True,
            indicator_color=ft.Colors.PRIMARY,
            indicator_thickness=2,
            tabs=[
                ft.Tab(text="Server", icon=ft.Icons.DNS, content=self._server_tab()),
                ft.Tab(text="Interface", icon=ft.Icons.PALETTE, content=self._interface_tab()),
                ft.Tab(text="Monitoring", icon=ft.Icons.INSIGHTS, content=self._monitoring_tab()),
                ft.Tab(text="Logging", icon=ft.Icons.ARTICLE, content=self._logging_tab()),
                ft.Tab(text="Security", icon=ft.Icons.SECURITY, content=self._security_tab()),
                ft.Tab(text="Backup", icon=ft.Icons.BACKUP, content=self._backup_tab()),
            ],
        )

        tabs_container = ft.Container(
            content=tabs,
            padding=ft.padding.all(0),
            expand=True,
        )

        body = ft.Column(
            [
                header,
                status_bar,
                ft.Container(
                    content=self.status_text, padding=ft.padding.symmetric(vertical=2, horizontal=16)
                ),
                tabs_container,
            ],
            expand=True,
            spacing=0,
        )
        return ft.Container(content=body, expand=True, padding=ft.padding.all(0))

    async def setup(self) -> None:
        self._update_status("Loading settings…")
        await self.load_settings()
        self._update_status("")

    def dispose(self) -> None:
        self._is_disposed = True
        # cancel pending autosave task if any
        with contextlib.suppress(Exception):
            if getattr(self, "_autosave_task", None) and not self._autosave_task.done():
                self._autosave_task.cancel()
        for picker in (self._export_picker, self._import_picker):
            with contextlib.suppress(ValueError):
                if picker in self.page.overlay:
                    self.page.overlay.remove(picker)

    # Tabs --------------------------------------------------------------
    def _build_status_bar(self) -> ft.Container:
        """Clean status bar with key indicators - professional settings pattern."""
        bridge_label, _, bridge_is_real = self._bridge_descriptor()
        mode_color = ft.Colors.GREEN if bridge_is_real else ft.Colors.AMBER

        # Calculate validation errors dynamically
        validation_errors = self._collect_validation_errors()
        validation_count = len(validation_errors)
        validation_str = (
            f"{validation_count} issue{'s' if validation_count != 1 else ''}"
            if validation_count > 0
            else "All valid"
        )
        validation_color = ft.Colors.RED if validation_count > 0 else ft.Colors.GREEN

        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CABLE, size=14, color=mode_color),
                    ft.Text(bridge_label, size=11, color=mode_color, weight=ft.FontWeight.W_500),
                    ft.Container(width=10),  # Spacer
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE_OUTLINE if validation_count == 0 else ft.Icons.ERROR_OUTLINE,
                        size=14,
                        color=validation_color,
                    ),
                    ft.Text(validation_str, size=11, color=validation_color, weight=ft.FontWeight.W_500),
                    ft.Container(expand=True),  # Push autosave to right
                    ft.Text("Autosave", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Container(width=6),
                    self._autosave_ref.current,
                ],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=6),
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.PRIMARY_CONTAINER),
            border=ft.border.only(
                bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.15, ft.Colors.OUTLINE)),
                top=ft.BorderSide(2, ft.Colors.PRIMARY),
            ),
        )

    def _bridge_descriptor(self) -> tuple[str, str, bool]:
        if not self.server_bridge:
            return "Offline mode", "Mock bridge with local JSON storage", False
        bridge_checker = getattr(self.server_bridge, "is_real", None)
        try:
            is_real = bool(bridge_checker()) if callable(bridge_checker) else True
        except Exception:
            is_real = True
        if is_real:
            return "Direct server", "Live connection to BackupServer", True
        return "Bridge fallback", "Operating with cached data", False

    def _section_card(self, title: str, icon: str, rows: list[ft.Control]) -> ft.Container:
        """Compact section with simple header - space-efficient settings pattern."""
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=18, color=ft.Colors.PRIMARY),
                    ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
                ],
                spacing=10,
            ),
            padding=ft.padding.only(left=16, right=12, top=10, bottom=6),
        )

        return ft.Container(
            content=ft.Column([header, *rows], spacing=0),
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.PRIMARY_CONTAINER),
            border_radius=10,
            border=ft.border.only(
                left=ft.BorderSide(3, ft.Colors.PRIMARY),
                top=ft.BorderSide(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
                right=ft.BorderSide(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
                bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            ),
            margin=ft.margin.only(bottom=10),
        )

    def _server_tab(self) -> ft.Control:
        # Network
        host = self._text(
            "server", "host", "Host", width=260, validator=_require("Host"), hint_text="IPv4/IPv6 or hostname"
        )
        port = self._text(
            "server",
            "port",
            "Port",
            width=180,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1024, 65535, "Port"),
        )
        max_clients = self._text(
            "server",
            "max_clients",
            LABEL_MAX_CLIENTS,
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 1000, "Max clients"),
        )
        timeout = self._text(
            "server",
            "timeout",
            "Timeout",
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(5, 600, "Timeout"),
            suffix_text="s",
        )
        network_rows = [
            _row("Host", host, "Server interface"),
            _row("Port", port, "Listening TCP port"),
            _row(LABEL_MAX_CLIENTS, max_clients, "Concurrent client connections"),
            _row("Timeout", timeout, "Idle client timeout"),
        ]

        # TLS
        enable_ssl = self._switch("server", "enable_ssl", "Enable TLS")
        cert = self._text(
            "server",
            "ssl_cert_path",
            LABEL_CERT_PATH,
            expand=True,
            validator=_require(LABEL_CERT_PATH),
            hint_text=".crt or .pem",
        )
        key = self._text(
            "server",
            "ssl_key_path",
            LABEL_KEY_PATH,
            expand=True,
            validator=_require(LABEL_KEY_PATH),
            hint_text=".key private key",
        )
        tls_rows = [
            _row("Enable TLS", enable_ssl, "Encrypt client connections"),
            _row(LABEL_CERT_PATH, cert, "Public certificate file path"),
            _row(LABEL_KEY_PATH, key, "Private key file path"),
        ]

        return ft.ListView(
            expand=True,
            spacing=0,
            padding=ft.padding.all(10),
            controls=[
                self._section_card("Network", ft.Icons.ROUTER, network_rows),
                self._section_card("TLS", ft.Icons.LOCK, tls_rows),
            ],
        )

    def _interface_tab(self) -> ft.Control:
        # Theme
        theme = self._dropdown(
            "gui",
            "theme_mode",
            "Theme mode",
            [("light", "Light"), ("dark", "Dark"), ("system", "System")],
            width=220,
        )
        color = self._dropdown(
            "gui", "color_scheme", "Color seed", [(k, k.title()) for k in COLOR_SEEDS], width=220
        )
        theme_rows = [
            _row("Theme mode", theme, "Light, Dark or follow System"),
            _row("Color seed", color, "Primary color accent"),
        ]

        # Behavior
        auto_refresh = self._switch("gui", "auto_refresh", "Auto refresh")
        refresh_int = self._text(
            "gui",
            "refresh_interval",
            LABEL_REFRESH_INTERVAL,
            width=220,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 300, LABEL_REFRESH_INTERVAL),
            suffix_text="s",
        )
        auto_resize = self._switch("gui", "auto_resize", "Responsive layout")
        behavior_rows = [
            _row("Auto refresh", auto_refresh, "Refresh dashboard automatically"),
            _row(LABEL_REFRESH_INTERVAL, refresh_int),
            _row("Responsive layout", auto_resize, "Auto-adjust widgets to page size"),
        ]

        return ft.ListView(
            expand=True,
            spacing=0,
            padding=ft.padding.all(10),
            controls=[
                self._section_card("Theme", ft.Icons.PALETTE, theme_rows),
                self._section_card("Behavior", ft.Icons.TUNE, behavior_rows),
            ],
        )

    def _monitoring_tab(self) -> ft.Control:
        enabled = self._switch("monitoring", "enabled", "Enable monitoring")
        refresh = self._text(
            "monitoring",
            "refresh_interval",
            LABEL_REFRESH_INTERVAL,
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(5, 600, "Monitoring interval"),
            suffix_text="s",
        )
        cpu = self._text(
            "monitoring",
            "cpu_threshold",
            LABEL_CPU_THRESHOLD,
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 100, "CPU threshold"),
            suffix_text="%",
        )
        mem = self._text(
            "monitoring",
            "memory_threshold",
            LABEL_MEMORY_THRESHOLD,
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 100, "Memory threshold"),
            suffix_text="%",
        )
        disk = self._text(
            "monitoring",
            "disk_threshold",
            LABEL_DISK_THRESHOLD,
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 100, "Disk threshold"),
            suffix_text="%",
        )
        rows = [
            _row("Enable monitoring", enabled, "Collect and display system metrics"),
            _row(LABEL_REFRESH_INTERVAL, refresh),
            _row(LABEL_CPU_THRESHOLD, cpu),
            _row(LABEL_MEMORY_THRESHOLD, mem),
            _row(LABEL_DISK_THRESHOLD, disk),
        ]
        return ft.ListView(
            expand=True,
            spacing=0,
            padding=ft.padding.all(10),
            controls=[self._section_card("Monitoring", ft.Icons.ASSESSMENT, rows)],
        )

    def _logging_tab(self) -> ft.Control:
        enabled = self._switch("logging", "enabled", "Enable logging")
        level = self._dropdown(
            "logging", "level", "Log level", ["DEBUG", "INFO", "WARNING", "ERROR"], width=220
        )
        path = self._text(
            "logging",
            "file_path",
            LABEL_LOG_FILE_PATH,
            expand=True,
            validator=_require(LABEL_LOG_FILE_PATH),
            hint_text="logs/server.log",
        )
        size = self._text(
            "logging",
            "max_size_mb",
            "Max size",
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 10240, "Max file size"),
            suffix_text="MB",
        )
        files = self._text(
            "logging",
            "max_files",
            "Max files",
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 50, "Rotation count"),
        )
        rows = [
            _row("Enable logging", enabled, "Write structured logs to a rotating file"),
            _row("Log level", level),
            _row(LABEL_LOG_FILE_PATH, path),
            _row("Max size", size),
            _row("Max files", files),
        ]
        return ft.ListView(
            expand=True,
            spacing=0,
            padding=ft.padding.all(10),
            controls=[self._section_card("Logging", ft.Icons.ARTICLE, rows)],
        )

    def _security_tab(self) -> ft.Control:
        require = self._switch("security", "require_auth", "Require authentication")
        api_key = self._text(
            "security",
            "api_key",
            LABEL_API_KEY,
            expand=True,
            validator=_require(LABEL_API_KEY),
            password=True,
            hint_text="Paste API key",
        )
        attempts = self._text(
            "security",
            "max_login_attempts",
            LABEL_MAX_LOGIN_ATTEMPTS,
            width=220,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 10, "Max login attempts"),
        )
        timeout = self._text(
            "security",
            "session_timeout",
            LABEL_SESSION_TIMEOUT,
            width=220,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(60, 86400, "Session timeout"),
            suffix_text="s",
        )
        rows = [
            _row("Require authentication", require, "Protect admin features"),
            _row(LABEL_API_KEY, api_key),
            _row(LABEL_MAX_LOGIN_ATTEMPTS, attempts),
            _row(LABEL_SESSION_TIMEOUT, timeout),
        ]
        return ft.ListView(
            expand=True,
            spacing=0,
            padding=ft.padding.all(10),
            controls=[self._section_card("Security", ft.Icons.SECURITY, rows)],
        )

    def _backup_tab(self) -> ft.Control:
        auto = self._switch("backup", "auto_backup", "Auto backups")
        path = self._text(
            "backup",
            "backup_path",
            LABEL_BACKUP_PATH,
            expand=True,
            validator=_require(LABEL_BACKUP_PATH),
            hint_text="backups/",
        )
        interval = self._text(
            "backup",
            "backup_interval_hours",
            LABEL_BACKUP_INTERVAL,
            width=220,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 168, "Backup interval"),
            suffix_text="h",
        )
        retention = self._text(
            "backup",
            "retention_days",
            "Retention",
            width=220,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 365, "Retention"),
            suffix_text="days",
        )
        compress = self._switch("backup", "compress_backups", "Compress backups")
        rows = [
            _row("Auto backups", auto, "Run periodic backups automatically"),
            _row(LABEL_BACKUP_PATH, path),
            _row(LABEL_BACKUP_INTERVAL, interval),
            _row("Retention", retention),
            _row("Compress backups", compress),
        ]
        return ft.ListView(
            expand=True,
            spacing=0,
            padding=ft.padding.all(10),
            controls=[self._section_card("Backup", ft.Icons.BACKUP, rows)],
        )

    # Control factories -------------------------------------------------
    def _text(
        self,
        section: str,
        key: str,
        label: str,
        *,
        width: int | None = None,
        expand: bool = False,
        keyboard: ft.KeyboardType | None = None,
        parser: Parser | None = None,
        validator: Validator | None = None,
        password: bool = False,
        suffix_text: str | None = None,
        hint_text: str | None = None,
    ) -> ft.TextField:
        field = ft.TextField(
            label=label,
            width=width,
            expand=expand,
            keyboard_type=keyboard,
            password=password,
            can_reveal_password=password,
            suffix_text=suffix_text,
            hint_text=hint_text,
            border_color=ft.Colors.with_opacity(0.3, ft.Colors.OUTLINE),
            focused_border_color=ft.Colors.PRIMARY,
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.SURFACE),
            content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        )
        ident = (section, key)
        self.controls[ident] = field
        if parser:
            self.parsers[ident] = parser
        if validator:
            self.validators[ident] = validator

        def _on_change(e: ft.ControlEvent) -> None:
            raw = getattr(e.control, "value", None)
            val = self.parsers.get(ident, lambda v: v)(raw)
            self._on_value_changed(section, key, val)

        field.on_change = _on_change
        return field

    def _switch(self, section: str, key: str, label: str) -> ft.Switch:
        sw = ft.Switch()
        sw.tooltip = label
        ident = (section, key)
        self.controls[ident] = sw

        def _on_change(e: ft.ControlEvent) -> None:
            self._on_value_changed(section, key, bool(getattr(e.control, "value", False)))

        sw.on_change = _on_change
        return sw

    def _dropdown(
        self,
        section: str,
        key: str,
        label: str,
        options: list[str] | list[tuple[str, str]],
        *,
        width: int | None = None,
    ) -> ft.Dropdown:
        dd_options: list[ft.dropdown.Option] = []
        for opt in options:
            if isinstance(opt, tuple):
                dd_options.append(ft.dropdown.Option(opt[0], opt[1]))
            else:
                dd_options.append(ft.dropdown.Option(opt))
        dd = ft.Dropdown(label=label, options=dd_options, width=width)
        ident = (section, key)
        self.controls[ident] = dd

        def _on_change(e: ft.ControlEvent) -> None:
            self._on_value_changed(section, key, getattr(e.control, "value", None))

        dd.on_change = _on_change
        return dd

    # State & side-effects ---------------------------------------------
    def _on_value_changed(self, section: str, key: str, value: Any) -> None:
        if self._is_disposed:
            return
        self.data.setdefault(section, {})[key] = value
        self._apply_dependencies()
        self._apply_side_effects(section, key, value)
        self._schedule_autosave()
        if self.state_manager:
            self.state_manager.update(f"settings.{section}.{key}", value, source="settings_view_change")

    def _apply_dependencies(self) -> None:
        # TLS fields enabled only when TLS is enabled
        ssl_enabled = bool(self.data.get("server", {}).get("enable_ssl"))
        for ssl_field in ("ssl_cert_path", "ssl_key_path"):
            ctl = self.controls.get(("server", ssl_field))
            tf = ctl if isinstance(ctl, ft.TextField) else None
            if tf:
                tf.disabled = not ssl_enabled
                if getattr(tf, "page", None):
                    tf.update()
        # API key enabled only when auth required
        auth_required = bool(self.data.get("security", {}).get("require_auth"))
        ctl_api = self.controls.get(("security", "api_key"))
        api_tf = ctl_api if isinstance(ctl_api, ft.TextField) else None
        if api_tf:
            api_tf.disabled = not auth_required
            if getattr(api_tf, "page", None):
                api_tf.update()

    def _apply_side_effects(self, section: str, key: str, value: Any) -> None:
        if section != "gui":
            return
        theme_changed = False
        if key == "theme_mode":
            theme_mode = str(value or "system").lower()
            if theme_mode == "system":
                self.page.theme_mode = ft.ThemeMode.SYSTEM
            elif theme_mode == "dark":
                self.page.theme_mode = ft.ThemeMode.DARK
            else:
                self.page.theme_mode = ft.ThemeMode.LIGHT
            theme_changed = True
        elif key == "color_scheme":
            seed = COLOR_SEEDS.get(str(value), COLOR_SEEDS["blue"]) if value else COLOR_SEEDS["blue"]
            theme = self.page.theme or ft.Theme()
            theme.color_scheme_seed = seed
            theme.use_material3 = True
            self.page.theme = theme
            theme_changed = True

        # Optimize: Single page update for all theme changes
        if theme_changed:
            self.page.update()

    def _schedule_autosave(self) -> None:
        if hasattr(self.page, "run_task"):
            self.page.run_task(self._autosave)
        else:
            # store task reference to avoid GC and allow cancellation on dispose
            if getattr(self, "_autosave_task", None) and not self._autosave_task.done():
                with contextlib.suppress(Exception):
                    self._autosave_task.cancel()
            self._autosave_task = asyncio.create_task(self._autosave())

    # Data IO -----------------------------------------------------------
    async def load_settings(self, show_feedback: bool = False) -> None:
        logger.info("Loading settings (bridge: %s)", bool(self.server_bridge))
        data: dict[str, Any] | None = None
        if self.server_bridge:
            result = await run_sync_in_executor(safe_server_call, self.server_bridge, "load_settings")
            if result.get("success"):
                data = result.get("data")
            else:
                logger.warning("Server settings load failed: %s", result.get("error"))
        elif SETTINGS_FILE.exists():
            async with aiofiles.open(SETTINGS_FILE) as handle:
                try:
                    data = json.loads(await handle.read())
                except json.JSONDecodeError as err:
                    logger.error("Failed to parse local settings file: %s", err)

        self.data = _merge_settings(data)
        self._refresh_controls()
        if show_feedback:
            self._update_status("Settings loaded")

    def _collect_validation_errors(self) -> list[str]:
        errors: list[str] = []
        for (section, key), control in self.controls.items():
            validator = self.validators.get((section, key))
            if not validator:
                continue
            value = self.data.get(section, {}).get(key)
            ok, message = validator(value)
            if not ok and message:
                errors.append(message)
                if isinstance(control, ft.TextField):
                    control.error_text = message
                    if control.page:
                        control.update()
        return errors

    async def persist(self, auto: bool = False) -> None:
        # minimal validation using registered validators
        errors = self._collect_validation_errors()
        if errors:
            self._update_status("; ".join(errors))
            return

        payload = copy.deepcopy(self.data)
        if self.server_bridge:
            result = await run_sync_in_executor(
                safe_server_call, self.server_bridge, "save_settings", payload
            )
            if not result.get("success"):
                self._update_status(f"Save failed: {result.get('error', 'Unknown error')}")
                return
        else:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(SETTINGS_FILE, "w") as handle:
                await handle.write(json.dumps(payload, indent=2))

        self._update_status("Settings synchronized" if auto else "Settings saved")

    async def _export_to_path(self, path: str) -> None:
        async with aiofiles.open(path, "w") as handle:
            await handle.write(json.dumps(self.data, indent=2))
        self._update_status(f"Settings exported to {path}")

    async def _import_from_path(self, path: str) -> None:
        async with aiofiles.open(path) as handle:
            imported = json.loads(await handle.read())
        self.data = _merge_settings(imported)
        self._refresh_controls()
        self._update_status("Imported settings; remember to save")

    def _refresh_controls(self) -> None:
        # populate all bound controls from self.data
        for (section, key), control in self.controls.items():
            value = self.data.get(section, {}).get(key)
            if isinstance(control, ft.TextField):
                control.value = "" if value is None else str(value)
                control.error_text = None
            elif isinstance(control, ft.Switch):
                control.value = bool(value)
            elif isinstance(control, ft.Dropdown):
                control.value = value
            if getattr(control, "page", None):
                control.update()
        self._apply_dependencies()

    # Events ------------------------------------------------------------
    def _on_export_clicked(self, _: ft.ControlEvent) -> None:
        self._export_picker.save_file(
            dialog_title="Export settings",
            file_name="settings.json",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
        )

    def _handle_export_result(self, e: ft.FilePickerResultEvent) -> None:
        if e.path:
            self.page.run_task(self._export_to_path, e.path)

    def _on_import_clicked(self, _: ft.ControlEvent) -> None:
        self._import_picker.pick_files(
            dialog_title="Import settings",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
        )

    def _handle_import_result(self, e: ft.FilePickerResultEvent) -> None:
        if e.files and e.files[0] and getattr(e.files[0], "path", None):
            self.page.run_task(self._import_from_path, e.files[0].path)

    def _on_reset_clicked(self, _: ft.ControlEvent) -> None:
        self.data = copy.deepcopy(DEFAULT_SETTINGS)
        self._refresh_controls()
        self._update_status("Defaults loaded; save to persist")

    def _on_save_clicked(self, _: ft.ControlEvent) -> None:
        self.page.run_task(self.persist)

    # Helpers -----------------------------------------------------------
    def _ensure_overlay(self, picker: ft.FilePicker) -> None:
        if picker not in self.page.overlay:
            self.page.overlay.append(picker)

    def _update_status(self, message: str) -> None:
        self.status_text.value = message
        if self.status_text.page:
            self.status_text.update()

    def _compute_tabs_height(self) -> int:
        # fixed, safe default for web; big enough to show fields but not overflow
        try:
            raw = getattr(self.page, "window_height", None) or getattr(self.page, "height", None) or 0
            h = int(str(raw)) if str(raw).isdigit() else 0
        except Exception:
            h = 0
        return max(420, min(900, (h - 280) if h else 560))


# ==============================================================================
# SECTION 3: VIEW FACTORY
# Creates and initializes the settings view with proper lifecycle management
# ==============================================================================


def create_settings_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    state_manager: SimpleState | None = None,
    global_search: ft.Control | None = None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    view = _SettingsView(page, server_bridge, state_manager, global_search)
    root = view.build()
    return root, view.dispose, view.setup
