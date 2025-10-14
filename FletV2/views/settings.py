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
    from ..utils.state_manager import StateManager
    from ..utils.ui_builders import create_action_button, create_view_header
except Exception:  # pragma: no cover
    from FletV2.config import SETTINGS_FILE  # type: ignore
    from FletV2.utils.async_helpers import debounce, run_sync_in_executor, safe_server_call  # type: ignore
    from FletV2.utils.debug_setup import get_logger  # type: ignore
    from FletV2.utils.server_bridge import ServerBridge  # type: ignore
    from FletV2.utils.state_manager import StateManager  # type: ignore
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


def _row(label: str, control: ft.Control, desc: str | None = None) -> ft.Container:
    caption = ft.Text(desc, size=12, color=ft.Colors.ON_SURFACE_VARIANT) if desc else None
    col = ft.Column(
        [
            ft.Row([ft.Text(label, size=14, weight=ft.FontWeight.W_500), ft.Container(expand=True), control], spacing=12),
            *( [caption] if caption else [] ),
        ],
        spacing=4,
    )
    return ft.Container(content=col, padding=ft.padding.symmetric(vertical=8))


class _SettingsView:
    def __init__(self, page: ft.Page, server_bridge: ServerBridge | None, state_manager: StateManager | None) -> None:
        self.page = page
        self.server_bridge = server_bridge
        self.state_manager = state_manager
        self.data = copy.deepcopy(DEFAULT_SETTINGS)
        self.controls: dict[tuple[str, str], ft.Control] = {}
        self.parsers: dict[tuple[str, str], Parser] = {}
        self.validators: dict[tuple[str, str], Validator] = {}
        self.status_text = ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        self._is_disposed = False

        self._export_picker = ft.FilePicker(on_result=self._handle_export_result)
        self._import_picker = ft.FilePicker(on_result=self._handle_import_result)

        @debounce(1.5)
        async def _auto_save() -> None:
            await self.persist(auto=True)

        self._autosave = _auto_save

    def build(self) -> ft.Control:
        self._ensure_overlay(self._export_picker)
        self._ensure_overlay(self._import_picker)

        header = create_view_header(
            "Settings",
            icon=ft.Icons.SETTINGS,
            description="Configure networking, interface, monitoring, logging, security, and backup policies.",
            actions=[create_action_button("Save", self._on_save_clicked, icon=ft.Icons.SAVE)],
        )

        utilities = ft.Row(
            [
                create_action_button("Export", self._on_export_clicked, icon=ft.Icons.UPLOAD, primary=False),
                create_action_button("Import", self._on_import_clicked, icon=ft.Icons.DOWNLOAD, primary=False),
                create_action_button("Reset", self._on_reset_clicked, icon=ft.Icons.RESTORE, primary=False),
            ],
            spacing=12,
            wrap=True,
        )

        tabs = ft.Tabs(
            expand=True,
            height=self._compute_tabs_height(),
            divider_color=ft.Colors.TRANSPARENT,
            tabs=[
                ft.Tab(text="Server", icon=ft.Icons.DNS, content=self._server_tab()),
                ft.Tab(text="Interface", icon=ft.Icons.PALETTE, content=self._interface_tab()),
                ft.Tab(text="Monitoring", icon=ft.Icons.MONITOR_HEART, content=self._monitoring_tab()),
                ft.Tab(text="Logging", icon=ft.Icons.ARTICLE, content=self._logging_tab()),
                ft.Tab(text="Security", icon=ft.Icons.SECURITY, content=self._security_tab()),
                ft.Tab(text="Backup", icon=ft.Icons.BACKUP, content=self._backup_tab()),
            ],
        )

        body = ft.Column(
            [
                header,
                ft.Container(content=self.status_text, padding=ft.padding.symmetric(vertical=4)),
                ft.Container(content=utilities, padding=16, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=12, bgcolor=ft.Colors.SURFACE),
                ft.Container(content=tabs, padding=16, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=12, bgcolor=ft.Colors.SURFACE, expand=True),
            ],
            expand=True,
            spacing=16,
        )
        return ft.Container(content=body, expand=True, padding=ft.padding.symmetric(horizontal=20, vertical=16))

    async def setup(self) -> None:
        self._update_status("Loading settings…")
        await self.load_settings()
        self._update_status("")

    def dispose(self) -> None:
        self._is_disposed = True
        for picker in (self._export_picker, self._import_picker):
            with contextlib.suppress(ValueError):
                if picker in self.page.overlay:
                    self.page.overlay.remove(picker)

    # Tabs --------------------------------------------------------------
    def _server_tab(self) -> ft.Control:
        host = self._text("server", "host", "Host", width=260, validator=_require("Host"))
        port = self._text("server", "port", "Port", width=180, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(1024, 65535, "Port"))
        max_clients = self._text("server", "max_clients", "Max clients", width=200, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(1, 1000, "Max clients"))
        timeout = self._text("server", "timeout", "Timeout (s)", width=200, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(5, 600, "Timeout"))
        enable_ssl = self._switch("server", "enable_ssl", "Enable TLS")
        cert = self._text("server", "ssl_cert_path", "Certificate path", expand=True, validator=_require("Certificate path"))
        key = self._text("server", "ssl_key_path", "Key path", expand=True, validator=_require("Key path"))

        lv = ft.ListView(expand=True, spacing=4, controls=[
            _row("Host", host),
            _row("Port", port),
            _row("Max clients", max_clients),
            _row("Timeout (s)", timeout),
            _row("Enable TLS", enable_ssl, "Encrypt client connections"),
            _row("Certificate path", cert),
            _row("Key path", key),
        ])
        return lv

    def _interface_tab(self) -> ft.Control:
        theme = self._dropdown("gui", "theme_mode", "Theme mode", [("light", "Light"), ("dark", "Dark"), ("system", "System")], width=220)
        color = self._dropdown("gui", "color_scheme", "Color seed", [(k, k.title()) for k in COLOR_SEEDS], width=220)
        auto_refresh = self._switch("gui", "auto_refresh", "Auto refresh")
        refresh_int = self._text("gui", "refresh_interval", "Refresh interval (s)", width=200, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(1, 300, "Refresh interval"))
        auto_resize = self._switch("gui", "auto_resize", "Responsive layout")
        return ft.ListView(expand=True, spacing=4, controls=[
            _row("Theme mode", theme),
            _row("Color seed", color),
            _row("Auto refresh", auto_refresh),
            _row("Refresh interval (s)", refresh_int),
            _row("Responsive layout", auto_resize),
        ])

    def _monitoring_tab(self) -> ft.Control:
        enabled = self._switch("monitoring", "enabled", "Enable monitoring")
        refresh = self._text("monitoring", "refresh_interval", "Refresh interval (s)", width=200, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(5, 600, "Monitoring interval"))
        cpu = self._text("monitoring", "cpu_threshold", "CPU threshold (%)", width=200, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(1, 100, "CPU threshold"))
        mem = self._text("monitoring", "memory_threshold", "Memory threshold (%)", width=200, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(1, 100, "Memory threshold"))
        disk = self._text("monitoring", "disk_threshold", "Disk threshold (%)", width=200, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(1, 100, "Disk threshold"))
        return ft.ListView(expand=True, spacing=4, controls=[
            _row("Enable monitoring", enabled),
            _row("Refresh interval (s)", refresh),
            _row("CPU threshold (%)", cpu),
            _row("Memory threshold (%)", mem),
            _row("Disk threshold (%)", disk),
        ])

    def _logging_tab(self) -> ft.Control:
        enabled = self._switch("logging", "enabled", "Enable logging")
        level = self._dropdown("logging", "level", "Log level", ["DEBUG", "INFO", "WARNING", "ERROR"], width=220)
        path = self._text("logging", "file_path", "Log file path", expand=True, validator=_require("Log file path"))
        size = self._text("logging", "max_size_mb", "Max size (MB)", width=200, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(1, 10240, "Max file size"))
        files = self._text("logging", "max_files", "Max files", width=200, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(1, 50, "Rotation count"))
        return ft.ListView(expand=True, spacing=4, controls=[
            _row("Enable logging", enabled),
            _row("Log level", level),
            _row("Log file path", path),
            _row("Max size (MB)", size),
            _row("Max files", files),
        ])

    def _security_tab(self) -> ft.Control:
        require = self._switch("security", "require_auth", "Require authentication")
        api_key = self._text("security", "api_key", "API key", expand=True, validator=_require("API key"), password=True)
        attempts = self._text("security", "max_login_attempts", "Max login attempts", width=220, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(1, 10, "Max login attempts"))
        timeout = self._text("security", "session_timeout", "Session timeout (s)", width=220, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(60, 86400, "Session timeout"))
        return ft.ListView(expand=True, spacing=4, controls=[
            _row("Require authentication", require),
            _row("API key", api_key),
            _row("Max login attempts", attempts),
            _row("Session timeout (s)", timeout),
        ])

    def _backup_tab(self) -> ft.Control:
        auto = self._switch("backup", "auto_backup", "Auto backups")
        path = self._text("backup", "backup_path", "Backup path", expand=True, validator=_require("Backup path"))
        interval = self._text("backup", "backup_interval_hours", "Backup interval (hours)", width=220, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(1, 168, "Backup interval"))
        retention = self._text("backup", "retention_days", "Retention (days)", width=220, keyboard=ft.KeyboardType.NUMBER, parser=_safe_int, validator=_numeric_range(1, 365, "Retention"))
        compress = self._switch("backup", "compress_backups", "Compress backups")
        return ft.ListView(expand=True, spacing=4, controls=[
            _row("Auto backups", auto),
            _row("Backup path", path),
            _row("Backup interval (hours)", interval),
            _row("Retention (days)", retention),
            _row("Compress backups", compress),
        ])

    # Control factories -------------------------------------------------
    def _text(self, section: str, key: str, label: str, *, width: int | None = None, expand: bool = False, keyboard: ft.KeyboardType | None = None, parser: Parser | None = None, validator: Validator | None = None, password: bool = False) -> ft.TextField:
        field = ft.TextField(label=label, width=width, expand=expand, keyboard_type=keyboard, password=password, can_reveal_password=password)
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
        sw = ft.Switch(label=label)
        ident = (section, key)
        self.controls[ident] = sw

        def _on_change(e: ft.ControlEvent) -> None:
            self._on_value_changed(section, key, bool(getattr(e.control, "value", False)))

        sw.on_change = _on_change
        return sw

    def _dropdown(self, section: str, key: str, label: str, options: list[str] | list[tuple[str, str]], *, width: int | None = None) -> ft.Dropdown:
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
            control = self.controls.get(("server", ssl_field))
            if isinstance(control, ft.TextField):
                control.disabled = not ssl_enabled
                if control.page:
                    control.update()
        # API key enabled only when auth required
        auth_required = bool(self.data.get("security", {}).get("require_auth"))
        api_control = self.controls.get(("security", "api_key"))
        if isinstance(api_control, ft.TextField):
            api_control.disabled = not auth_required
            if api_control.page:
                api_control.update()

    def _apply_side_effects(self, section: str, key: str, value: Any) -> None:
        if section == "gui" and key == "theme_mode":
            theme_mode = str(value or "system").lower()
            self.page.theme_mode = ft.ThemeMode.SYSTEM if theme_mode == "system" else (ft.ThemeMode.DARK if theme_mode == "dark" else ft.ThemeMode.LIGHT)
            self.page.update()
        elif section == "gui" and key == "color_scheme":
            seed = COLOR_SEEDS.get(str(value), COLOR_SEEDS["blue"]) if value else COLOR_SEEDS["blue"]
            theme = self.page.theme or ft.Theme()
            theme.color_scheme_seed = seed
            theme.use_material3 = True
            self.page.theme = theme
            self.page.update()

    def _schedule_autosave(self) -> None:
        if hasattr(self.page, "run_task"):
            self.page.run_task(self._autosave)
        else:
            asyncio.create_task(self._autosave())

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

    async def persist(self, auto: bool = False) -> None:
        # minimal validation using registered validators
        errors: list[str] = []
        for (section, key), control in list(self.controls.items()):
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
        if errors:
            self._update_status("; ".join(errors))
            return

        payload = copy.deepcopy(self.data)
        if self.server_bridge:
            result = await run_sync_in_executor(safe_server_call, self.server_bridge, "save_settings", payload)
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
            if control.page:
                control.update()
        self._apply_dependencies()

    # Events ------------------------------------------------------------
    def _on_export_clicked(self, _: ft.ControlEvent) -> None:
        self._export_picker.save_file(dialog_title="Export settings", file_name="settings.json", file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["json"])

    def _handle_export_result(self, e: ft.FilePickerResultEvent) -> None:
        if e.path:
            self.page.run_task(self._export_to_path, e.path)

    def _on_import_clicked(self, _: ft.ControlEvent) -> None:
        self._import_picker.pick_files(dialog_title="Import settings", file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["json"])

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


def create_settings_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    state_manager: StateManager | None = None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    view = _SettingsView(page, server_bridge, state_manager)
    root = view.build()
    return root, view.dispose, view.setup
