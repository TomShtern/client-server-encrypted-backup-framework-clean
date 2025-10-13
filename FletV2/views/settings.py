#!/usr/bin/env python3
"""Professional settings view rebuilt for Flet 0.28.3."""

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
    from ..utils.state_manager import StateManager
    from ..utils.ui_builders import create_action_button, create_view_header
    from ..utils.ui_components import AppCard
    from ..utils.user_feedback import show_error_message, show_success_message
except Exception:  # pragma: no cover - fallback when running out of package context
    from FletV2.config import SETTINGS_FILE  # type: ignore
    from FletV2.utils.async_helpers import debounce, run_sync_in_executor, safe_server_call  # type: ignore
    from FletV2.utils.debug_setup import get_logger  # type: ignore
    from FletV2.utils.server_bridge import ServerBridge  # type: ignore
    from FletV2.utils.state_manager import StateManager  # type: ignore
    from FletV2.utils.ui_builders import create_action_button, create_view_header  # type: ignore
    from FletV2.utils.ui_components import AppCard  # type: ignore
    from FletV2.utils.user_feedback import show_error_message, show_success_message  # type: ignore


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


def create_setting_row(label: str, control: ft.Control, description: str | None = None) -> ft.Container:
    caption = ft.Text(description, size=12, color=ft.Colors.ON_SURFACE_VARIANT) if description else None
    items: list[ft.Control] = [
        ft.Row(
            [
                ft.Text(label, size=14, weight=ft.FontWeight.W_500),
                ft.Container(expand=True),
                control,
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    ]
    if caption:
        items.append(caption)
    return ft.Container(
        content=ft.Column(items, spacing=4),
        padding=ft.padding.symmetric(vertical=6),
    )


def create_settings_section(title: str, controls: list[ft.Control]) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(title, size=18, weight=ft.FontWeight.W_600),
                ft.Column(controls, spacing=4),
            ],
            spacing=12,
        ),
        padding=ft.padding.all(16),
        border_radius=12,
        bgcolor=ft.Colors.SURFACE,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=18,
            offset=ft.Offset(0, 6),
            color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
        ),
    )


class _SettingsView:
    def __init__(
        self,
        page: ft.Page,
        server_bridge: ServerBridge | None,
        state_manager: StateManager | None,
    ) -> None:
        self.page = page
        self.server_bridge = server_bridge
        self.state_manager = state_manager
        self.data = copy.deepcopy(DEFAULT_SETTINGS)
        self.controls: dict[tuple[str, str], ft.Control] = {}
        self.validators: dict[tuple[str, str], Validator] = {}
        self.parsers: dict[tuple[str, str], Parser] = {}
        self.dirty: dict[str, set[str]] = {section: set() for section in self.data}
        self.status_text = ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        self.autosave_enabled = True
        self._is_disposed = False

        self._export_picker = ft.FilePicker(on_result=self._handle_export_result)
        self._import_picker = ft.FilePicker(on_result=self._handle_import_result)

        @debounce(2.0)
        async def _auto_save() -> None:
            await self.persist(auto=True)

        self._autosave = _auto_save

    # ------------------------------------------------------------------
    # Public lifecycle hooks
    # ------------------------------------------------------------------
    def build(self) -> ft.Control:
        self._ensure_overlay(self._export_picker)
        self._ensure_overlay(self._import_picker)

        header = create_view_header(
            "Settings",
            icon=ft.Icons.SETTINGS,
            description="Configure networking, interface, monitoring, logging, security, and backup policies.",
            actions=[create_action_button("Save", self._on_save_clicked, icon=ft.Icons.SAVE)],
        )

        layout = ft.Container(
            content=ft.Column(
                [
                    header,
                    ft.Container(content=self.status_text, padding=ft.padding.symmetric(vertical=4)),
                    self._build_utilities_card(),
                    self._build_tabs_card(),
                ],
                spacing=16,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=ft.padding.symmetric(horizontal=20, vertical=16),
        )
        return layout

    async def setup(self) -> None:
        self._update_status_text("Loading settings…")
        await self.load_settings()
        self._update_status_text("")

    def dispose(self) -> None:
        self._is_disposed = True
        for picker in (self._export_picker, self._import_picker):
            with contextlib.suppress(ValueError):
                if picker in self.page.overlay:
                    self.page.overlay.remove(picker)

    # ------------------------------------------------------------------
    # UI builders
    # ------------------------------------------------------------------
    def _build_utilities_card(self) -> ft.Control:
        utilities = ft.Row(
            [
                create_action_button("Export", self._on_export_clicked, icon=ft.Icons.UPLOAD, primary=False),
                create_action_button("Import", self._on_import_clicked, icon=ft.Icons.DOWNLOAD, primary=False),
                create_action_button("Reset", self._on_reset_clicked, icon=ft.Icons.RESTORE, primary=False),
            ],
            spacing=12,
            wrap=True,
        )
        return AppCard(utilities, title="Utilities", expand_content=False)

    def _build_tabs_card(self) -> ft.Control:
        tabs = ft.Tabs(
            expand=True,
            animation_duration=250,
            divider_color=ft.Colors.TRANSPARENT,
            tabs=[
                ft.Tab(text="Server", icon=ft.Icons.DNS, content=self._build_server_section()),
                ft.Tab(text="Interface", icon=ft.Icons.PALETTE, content=self._build_interface_section()),
                ft.Tab(text="Monitoring", icon=ft.Icons.MONITOR_HEART, content=self._build_monitoring_section()),
                ft.Tab(text="Logging", icon=ft.Icons.ARTICLE, content=self._build_logging_section()),
                ft.Tab(text="Security", icon=ft.Icons.SECURITY, content=self._build_security_section()),
                ft.Tab(text="Backup", icon=ft.Icons.BACKUP, content=self._build_backup_section()),
            ],
        )
        first_tab = tabs.tabs[0]
        tab_summary = {
            "tab_count": len(tabs.tabs),
            "first_tab_type": type(first_tab.content).__name__ if first_tab.content else None,
            "first_tab_children": (
                len(getattr(getattr(first_tab.content, "content", None), "controls", []))
                if first_tab.content else 0
            ),
        }
        logger.warning("[settings] Tabs built: %s", [tab.text for tab in tabs.tabs])
        logger.warning("[settings] First tab summary: %s", tab_summary)
        return AppCard(tabs, title="Configuration", expand_content=False)

    def _build_server_section(self) -> ft.Control:
        host = self._text_field("server", "host", "Host", width=220, validator=_require("Host"))
        port = self._text_field(
            "server",
            "port",
            "Port",
            width=140,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1024, 65535, "Port"),
        )
        max_clients = self._text_field(
            "server",
            "max_clients",
            "Max clients",
            width=160,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 1000, "Max clients"),
        )
        timeout = self._text_field(
            "server",
            "timeout",
            "Timeout (s)",
            width=160,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(5, 600, "Timeout"),
        )
        enable_ssl = self._switch("server", "enable_ssl", "Enable TLS")
        cert_path = self._text_field(
            "server",
            "ssl_cert_path",
            "Certificate path",
            expand=True,
            validator=_require("Certificate path"),
        )
        key_path = self._text_field(
            "server",
            "ssl_key_path",
            "Key path",
            expand=True,
            validator=_require("Key path"),
        )
        return create_settings_section(
            "Server",
            [
                create_setting_row("Connection", ft.Row([host, port], spacing=12)),
                create_setting_row("Capacity", ft.Row([max_clients, timeout], spacing=12)),
                create_setting_row("Security", enable_ssl, "Enable TLS for client connections"),
                create_setting_row("Certificate", cert_path),
                create_setting_row("Key", key_path),
            ],
        )

    def _build_interface_section(self) -> ft.Control:
        theme = self._dropdown(
            "gui",
            "theme_mode",
            "Theme mode",
            options=[("light", "Light"), ("dark", "Dark"), ("system", "System")],
            width=200,
        )
        color = self._dropdown(
            "gui",
            "color_scheme",
            "Color seed",
            options=[(key, key.title()) for key in COLOR_SEEDS],
            width=220,
        )
        auto_refresh = self._switch("gui", "auto_refresh", "Auto refresh")
        refresh_interval = self._text_field(
            "gui",
            "refresh_interval",
            "Refresh interval (s)",
            width=180,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 300, "Refresh interval"),
        )
        auto_resize = self._switch("gui", "auto_resize", "Responsive layout")
        return create_settings_section(
            "Interface",
            [
                create_setting_row("Theme", ft.Row([theme, color], spacing=12)),
                create_setting_row("Refresh", ft.Row([auto_refresh, refresh_interval], spacing=12)),
                create_setting_row("Layout", auto_resize, "Automatically adapt UI elements to window size"),
            ],
        )

    def _build_monitoring_section(self) -> ft.Control:
        monitoring_enabled = self._switch("monitoring", "enabled", "Enable monitoring")
        refresh = self._text_field(
            "monitoring",
            "refresh_interval",
            "Refresh interval (s)",
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(5, 600, "Monitoring interval"),
        )
        cpu = self._text_field(
            "monitoring",
            "cpu_threshold",
            "CPU threshold (%)",
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 100, "CPU threshold"),
        )
        memory = self._text_field(
            "monitoring",
            "memory_threshold",
            "Memory threshold (%)",
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 100, "Memory threshold"),
        )
        disk = self._text_field(
            "monitoring",
            "disk_threshold",
            "Disk threshold (%)",
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 100, "Disk threshold"),
        )
        return create_settings_section(
            "Monitoring",
            [
                create_setting_row("Status", monitoring_enabled),
                create_setting_row("Sampling", refresh, "Frequency for health polling"),
                create_setting_row("Thresholds", ft.Row([cpu, memory, disk], spacing=12)),
            ],
        )

    def _build_logging_section(self) -> ft.Control:
        logging_enabled = self._switch("logging", "enabled", "Enable logging")
        level = self._dropdown(
            "logging",
            "level",
            "Log level",
            options=["DEBUG", "INFO", "WARNING", "ERROR"],
            width=200,
        )
        file_path = self._text_field(
            "logging",
            "file_path",
            "Log file path",
            expand=True,
            validator=_require("Log file path"),
        )
        max_size = self._text_field(
            "logging",
            "max_size_mb",
            "Max size (MB)",
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 10240, "Max file size"),
        )
        max_files = self._text_field(
            "logging",
            "max_files",
            "Max files",
            width=200,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 50, "Rotation count"),
        )
        return create_settings_section(
            "Logging",
            [
                create_setting_row("Status", logging_enabled),
                create_setting_row("Level", level),
                create_setting_row("Storage", file_path),
                create_setting_row("Rotation", ft.Row([max_size, max_files], spacing=12)),
            ],
        )

    def _build_security_section(self) -> ft.Control:
        require_auth = self._switch("security", "require_auth", "Require authentication")
        api_key = self._text_field(
            "security",
            "api_key",
            "API key",
            expand=True,
            validator=_require("API key"),
            password=True,
        )
        max_attempts = self._text_field(
            "security",
            "max_login_attempts",
            "Max login attempts",
            width=220,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 10, "Max login attempts"),
        )
        session_timeout = self._text_field(
            "security",
            "session_timeout",
            "Session timeout (s)",
            width=220,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(60, 86400, "Session timeout"),
        )
        return create_settings_section(
            "Security",
            [
                create_setting_row("Authentication", require_auth),
                create_setting_row("API key", api_key),
                create_setting_row("Login policy", ft.Row([max_attempts, session_timeout], spacing=12)),
            ],
        )

    def _build_backup_section(self) -> ft.Control:
        auto_backup = self._switch("backup", "auto_backup", "Auto backups")
        backup_path = self._text_field(
            "backup",
            "backup_path",
            "Backup path",
            expand=True,
            validator=_require("Backup path"),
        )
        interval = self._text_field(
            "backup",
            "backup_interval_hours",
            "Backup interval (hours)",
            width=220,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 168, "Backup interval"),
        )
        retention = self._text_field(
            "backup",
            "retention_days",
            "Retention (days)",
            width=220,
            keyboard=ft.KeyboardType.NUMBER,
            parser=_safe_int,
            validator=_numeric_range(1, 365, "Retention"),
        )
        compress = self._switch("backup", "compress_backups", "Compress backups")
        return create_settings_section(
            "Backup",
            [
                create_setting_row("Automation", auto_backup),
                create_setting_row("Destination", backup_path),
                create_setting_row("Cadence", ft.Row([interval, retention], spacing=12)),
                create_setting_row("Compression", compress),
            ],
        )

    # ------------------------------------------------------------------
    # Control factories
    # ------------------------------------------------------------------
    def _text_field(
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
    ) -> ft.TextField:
        field = ft.TextField(
            label=label,
            width=width,
            expand=expand,
            keyboard_type=keyboard,
            password=password,
            can_reveal_password=password,
        )
        return self._bind_control(section, key, field, parser=parser, validator=validator)

    def _switch(self, section: str, key: str, label: str) -> ft.Switch:
        control = ft.Switch(label=label)
        return self._bind_control(section, key, control)

    def _dropdown(
        self,
        section: str,
        key: str,
        label: str,
        *,
        options: list[str] | list[tuple[str, str]],
        width: int | None = None,
        validator: Validator | None = None,
    ) -> ft.Dropdown:
        dropdown_options: list[ft.dropdown.Option] = []
        for option in options:
            if isinstance(option, tuple):
                dropdown_options.append(ft.dropdown.Option(option[0], option[1]))
            else:
                dropdown_options.append(ft.dropdown.Option(option))
        control = ft.Dropdown(label=label, options=dropdown_options, width=width)
        return self._bind_control(section, key, control, validator=validator)

    def _bind_control(
        self,
        section: str,
        key: str,
        control: ft.Control,
        *,
        parser: Parser | None = None,
        validator: Validator | None = None,
    ) -> ft.Control:
        identifier = (section, key)
        self.controls[identifier] = control
        if parser:
            self.parsers[identifier] = parser
        if validator:
            self.validators[identifier] = validator

        def _on_change(event: ft.ControlEvent) -> None:
            raw_value = getattr(event.control, "value", None)
            parsed_value = self.parsers.get(identifier, lambda value: value)(raw_value)
            self._on_value_changed(section, key, parsed_value)

        control.on_change = _on_change
        return control

    # ------------------------------------------------------------------
    # State handling
    # ------------------------------------------------------------------
    def _on_value_changed(self, section: str, key: str, value: Any) -> None:
        if self._is_disposed:
            return
        self.data.setdefault(section, {})[key] = value
        self._mark_dirty(section, key)
        self._apply_dependencies()
        self._apply_side_effects(section, key, value)
        self._schedule_autosave()
        self._push_state_update(section, key, value)

    def _mark_dirty(self, section: str, key: str) -> None:
        self.dirty.setdefault(section, set()).add(key)
        self._update_status_text()

    def _schedule_autosave(self) -> None:
        if not self.autosave_enabled:
            return
        if hasattr(self.page, "run_task"):
            self.page.run_task(self._autosave)
        else:
            asyncio.create_task(self._autosave())

    def _apply_dependencies(self) -> None:
        ssl_enabled = bool(self.data.get("server", {}).get("enable_ssl"))
        for ssl_field in ("ssl_cert_path", "ssl_key_path"):
            control = self.controls.get(("server", ssl_field))
            if control and isinstance(control, ft.TextField):
                control.disabled = not ssl_enabled
                if control.page:
                    control.update()
        auth_required = bool(self.data.get("security", {}).get("require_auth"))
        api_control = self.controls.get(("security", "api_key"))
        if api_control and isinstance(api_control, ft.TextField):
            api_control.disabled = not auth_required
            if api_control.page:
                api_control.update()

    def _apply_side_effects(self, section: str, key: str, value: Any) -> None:
        if section == "gui" and key == "theme_mode":
            self._apply_theme(str(value))
        elif section == "gui" and key == "color_scheme":
            self._apply_color_seed(str(value))
        elif section == "gui" and key == "refresh_interval":
            self._broadcast("refresh_interval_change", {"interval": value})
        elif section == "logging" and key == "level":
            self._broadcast("logging_level_change", {"level": value})

    def _push_state_update(self, section: str, key: str, value: Any) -> None:
        if self.state_manager:
            self.state_manager.update(
                f"settings.{section}.{key}",
                value,
                source="settings_view_change",
            )

    def _broadcast(self, event_name: str, payload: dict[str, Any]) -> None:
        if self.state_manager:
            self.state_manager.broadcast_settings_event(event_name, payload)

    def _update_status_text(self, message: str | None = None) -> None:
        if message is not None:
            self.status_text.value = message
        else:
            pending = sum(len(items) for items in self.dirty.values())
            self.status_text.value = (
                f"{pending} pending change(s); auto-save in progress" if pending else ""
            )
        if self.status_text.page:
            self.status_text.update()

    # ------------------------------------------------------------------
    # Data IO
    # ------------------------------------------------------------------
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
        self.dirty = {section: set() for section in self.data}
        self._refresh_controls()
        self._apply_theme(str(self.data["gui"].get("theme_mode", "system")))
        self._apply_color_seed(str(self.data["gui"].get("color_scheme", "blue")))
        self._push_full_state("settings_view_load")
        if show_feedback:
            show_success_message(self.page, "Settings loaded")

    async def persist(self, auto: bool = False) -> None:
        errors = self._validate_all()
        if errors:
            show_error_message(self.page, "; ".join(errors))
            return

        payload = copy.deepcopy(self.data)
        if self.server_bridge:
            result = await run_sync_in_executor(
                safe_server_call,
                self.server_bridge,
                "save_settings",
                payload,
            )
            if not result.get("success"):
                show_error_message(
                    self.page,
                    f"Save failed: {result.get('error', 'Unknown error')}",
                )
                return
        else:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(SETTINGS_FILE, "w") as handle:
                await handle.write(json.dumps(payload, indent=2))

        self.dirty = {section: set() for section in self.data}
        self._push_full_state("settings_view_autosave" if auto else "settings_view_save")
        self._update_status_text("Settings synchronized" if auto else "Settings saved")
        if not auto:
            show_success_message(self.page, "Settings saved")
        self._broadcast("settings_saved", {"auto": auto})

    async def _export_to_path(self, path: str) -> None:
        payload = copy.deepcopy(self.data)
        async with aiofiles.open(path, "w") as handle:
            await handle.write(json.dumps(payload, indent=2))
        show_success_message(self.page, f"Settings exported to {path}")

    async def _import_from_path(self, path: str) -> None:
        async with aiofiles.open(path) as handle:
            imported = json.loads(await handle.read())
        self.data = _merge_settings(imported)
        self.dirty = {section: set(values.keys()) for section, values in self.data.items()}
        self._refresh_controls()
        self._apply_theme(str(self.data["gui"].get("theme_mode", "system")))
        self._apply_color_seed(str(self.data["gui"].get("color_scheme", "blue")))
        self._push_full_state("settings_view_import")
        self._update_status_text("Imported settings; remember to save")
        show_success_message(self.page, "Settings imported")

    def _refresh_controls(self) -> None:
        for (section, key), control in self.controls.items():
            value = self.data.get(section, {}).get(key)
            if isinstance(control, ft.TextField):
                control.value = "" if value is None else str(value)
                control.error_text = None
            elif isinstance(control, ft.Switch):
                control.value = bool(value)
            elif isinstance(control, ft.Dropdown):
                control.value = value
            if control.page:
                control.update()
        self._apply_dependencies()
        self._update_status_text()

    def _validate_all(self) -> list[str]:
        errors: list[str] = []
        for identifier, validator in self.validators.items():
            section, key = identifier
            if section == "server" and key in {"ssl_cert_path", "ssl_key_path"} and not self.data["server"]["enable_ssl"]:
                continue
            if section == "security" and key == "api_key" and not self.data["security"]["require_auth"]:
                continue
            value = self.data.get(section, {}).get(key)
            ok, message = validator(value)
            control = self.controls.get(identifier)
            if ok:
                if isinstance(control, ft.TextField):
                    control.error_text = None
                    if control.page:
                        control.update()
                continue
            if message:
                errors.append(message)
            if isinstance(control, ft.TextField):
                control.error_text = message
                if control.page:
                    control.update()
        return errors

    def _apply_theme(self, mode: str) -> None:
        theme_mode = (mode or "system").lower()
        if theme_mode == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        elif theme_mode == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.update()
        self._broadcast("theme_change", {"theme_mode": theme_mode})

    def _apply_color_seed(self, seed_key: str) -> None:
        seed = COLOR_SEEDS.get(seed_key, COLOR_SEEDS["blue"])
        theme = self.page.theme or ft.Theme()
        theme.color_scheme_seed = seed
        theme.use_material3 = True
        self.page.theme = theme
        self.page.update()
        self._broadcast("color_seed_change", {"color": seed_key})

    def _push_full_state(self, source: str) -> None:
        if self.state_manager:
            self.state_manager.update(
                "settings_data",
                copy.deepcopy(self.data),
                source=source,
            )

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_export_clicked(self, _: ft.ControlEvent) -> None:
        self._export_picker.save_file(
            dialog_title="Export settings",
            file_name="settings.json",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
        )

    def _handle_export_result(self, event: ft.FilePickerResultEvent) -> None:
        if event.path:
            self.page.run_task(self._export_to_path, event.path)

    def _on_import_clicked(self, _: ft.ControlEvent) -> None:
        self._import_picker.pick_files(
            dialog_title="Import settings",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
        )

    def _handle_import_result(self, event: ft.FilePickerResultEvent) -> None:
        if event.files and event.files[0] and getattr(event.files[0], "path", None):
            self.page.run_task(self._import_from_path, event.files[0].path)

    def _on_reset_clicked(self, _: ft.ControlEvent) -> None:
        self.data = copy.deepcopy(DEFAULT_SETTINGS)
        self.dirty = {section: set(values.keys()) for section, values in self.data.items()}
        self._refresh_controls()
        self._apply_theme(str(self.data["gui"].get("theme_mode", "system")))
        self._apply_color_seed(str(self.data["gui"].get("color_scheme", "blue")))
        self._push_full_state("settings_view_reset")
        self._update_status_text("Defaults loaded; save to persist")
        show_success_message(self.page, "Settings reset to defaults")

    def _on_save_clicked(self, _: ft.ControlEvent) -> None:
        self.page.run_task(self.persist)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_overlay(self, picker: ft.FilePicker) -> None:
        if picker not in self.page.overlay:
            self.page.overlay.append(picker)


def create_settings_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    state_manager: StateManager | None = None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    view = _SettingsView(page, server_bridge, state_manager)
    root = view.build()
    return root, view.dispose, view.setup
