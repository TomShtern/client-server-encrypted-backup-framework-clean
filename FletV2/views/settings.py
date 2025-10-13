#!/usr/bin/env python3
"""Live settings view with Material Design 3 styling and immediate feedback."""

from __future__ import annotations

import asyncio
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
except Exception:  # pragma: no cover - fallback for loose execution contexts
    from FletV2.config import SETTINGS_FILE  # type: ignore
    from FletV2.utils.async_helpers import debounce, run_sync_in_executor, safe_server_call  # type: ignore
    from FletV2.utils.debug_setup import get_logger  # type: ignore
    from FletV2.utils.server_bridge import ServerBridge  # type: ignore
    from FletV2.utils.state_manager import StateManager  # type: ignore
    from FletV2.utils.ui_builders import create_action_button, create_view_header  # type: ignore
    from FletV2.utils.ui_components import AppCard  # type: ignore
    from FletV2.utils.user_feedback import show_error_message, show_success_message  # type: ignore


logger = get_logger(__name__)


# Keep references to background tasks to prevent garbage collection
_background_tasks: set[asyncio.Task] = set()


ColorSeed = dict[str, str]

COLOR_SEEDS: ColorSeed = {
    "blue": "#3B82F6",
    "indigo": "#6366F1",
    "purple": "#8B5CF6",
    "pink": "#EC4899",
    "green": "#10B981",
    "orange": "#F59E0B",
    "red": "#EF4444",
}


def _default_settings() -> dict[str, Any]:
    return {
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


Validator = Callable[[Any], tuple[bool, str | None]]
Parser = Callable[[Any], Any]


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def _validate_range(min_value: float, max_value: float, label: str) -> Validator:
    def _validator(value: Any) -> tuple[bool, str | None]:
        if value is None:
            return False, f"{label} is required"
        if isinstance(value, str) and not value.strip():
            return False, f"{label} is required"
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return False, f"{label} must be a number"
        if numeric < min_value or numeric > max_value:
            return False, f"{label} must be between {min_value:g}-{max_value:g}"
        return True, None

    return _validator


def _validate_required(label: str) -> Validator:
    def _validator(value: Any) -> tuple[bool, str | None]:
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"{label} is required"
        return True, None

    return _validator


def create_setting_row(label: str, control: ft.Control, description: str | None = None) -> ft.Container:
    caption = ft.Text(description, size=12, color=ft.Colors.ON_SURFACE_VARIANT) if description else None
    column = ft.Column([
        ft.Row([
            ft.Text(label, size=14, weight=ft.FontWeight.W_500),
            ft.Container(expand=True),
            control,
        ], spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        *( [caption] if caption else [] ),
    ], spacing=4)
    return ft.Container(content=column, padding=ft.padding.symmetric(vertical=6))


def create_settings_section(title: str, controls: list[ft.Control]) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=18, weight=ft.FontWeight.W_600),
            ft.Column(controls, spacing=4),
        ], spacing=12),
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


def _schedule(page: ft.Page, coro: Callable[[], Any] | asyncio.Future[Any]) -> None:
    async def _runner() -> None:
        result = coro() if callable(coro) else coro
        if asyncio.iscoroutine(result):
            await result

    if hasattr(page, "run_task"):
        page.run_task(_runner)
    else:
        task = asyncio.create_task(_runner())
        # Keep reference to avoid garbage collection
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)


def create_settings_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    state_manager: StateManager | None = None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    current_settings: dict[str, Any] = _default_settings()
    dirty_tracker: dict[str, set[str]] = {section: set() for section in current_settings}

    controls: dict[tuple[str, str], ft.Control] = {}
    validation_rules: dict[tuple[str, str], Validator] = {}
    parsers: dict[tuple[str, str], Parser] = {}

    autosave_enabled = True
    status_text = ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT)

    async def load_settings(show_feedback: bool = False) -> None:
        nonlocal current_settings

        logger.info("Loading settings (with server bridge: %s)", bool(server_bridge))
        data: dict[str, Any] | None = None

        if server_bridge:
            result = await run_sync_in_executor(safe_server_call, server_bridge, "load_settings")
            if result.get("success"):
                data = result.get("data")
            else:
                logger.warning("Server settings load failed: %s", result.get("error"))
        elif SETTINGS_FILE.exists():
            async with aiofiles.open(SETTINGS_FILE) as fp:
                try:
                    data = json.loads(await fp.read())
                except json.JSONDecodeError as err:
                    logger.error("Failed parsing settings file: %s", err)

        merged = _default_settings()
        if isinstance(data, dict):
            for category, values in data.items():
                if category in merged and isinstance(values, dict):
                    merged[category].update(values)
        current_settings = merged
        for section in dirty_tracker:
            dirty_tracker[section].clear()

        _refresh_controls()
        _apply_theme(current_settings["gui"].get("theme_mode", "system"))
        _apply_color_seed(current_settings["gui"].get("color_scheme", "blue"))
        if state_manager:
            state_manager.update(
                "settings_data",
                copy.deepcopy(current_settings),
                source="settings_view_load",
            )
        if show_feedback:
            show_success_message(page, "Settings loaded")

    async def persist_settings(auto: bool = False) -> None:
        errors = _validate_all()
        if errors:
            show_error_message(page, "; ".join(errors))
            return

        payload = copy.deepcopy(current_settings)

        if server_bridge:
            result = await run_sync_in_executor(safe_server_call, server_bridge, "save_settings", payload)
            if not result.get("success"):
                show_error_message(page, f"Save failed: {result.get('error', 'Unknown error')}")
                return
        else:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(SETTINGS_FILE, "w") as fp:
                await fp.write(json.dumps(payload, indent=2))

        if state_manager:
            state_manager.update("settings_data", copy.deepcopy(payload), source="settings_view_save")
            state_manager.broadcast_settings_event("settings_saved", {"auto": auto})

        for section in dirty_tracker:
            dirty_tracker[section].clear()
        _update_status()

        if status_text:
            status_text.value = "Settings synchronized" if auto else "Settings saved"
            if status_text.page:
                status_text.update()

        if not auto:
            show_success_message(page, "Settings saved")

    @debounce(2.0)
    async def autosave_worker() -> None:
        await persist_settings(auto=True)

    def _schedule_autosave() -> None:
        if autosave_enabled:
            _schedule(page, autosave_worker)

    def _refresh_controls() -> None:
        for (category, key), control in controls.items():
            value = current_settings.get(category, {}).get(key)
            if isinstance(control, ft.TextField):
                control.value = str(value) if value is not None else ""
            elif isinstance(control, (ft.Switch, ft.Checkbox)):
                control.value = bool(value)
            elif isinstance(control, ft.Dropdown):
                control.value = value
            elif isinstance(control, ft.Slider):
                control.value = float(value or 0)
            if isinstance(control, ft.TextField):
                control.error_text = None
            if control.page:
                control.update()
        _apply_dependent_states()
        _update_status()

    def _validate_all() -> list[str]:
        errors: list[str] = []
        for identifier, validator in validation_rules.items():
            value = current_settings.get(identifier[0], {}).get(identifier[1])
            control = controls.get(identifier)
            if (identifier in {("server", "ssl_cert_path"), ("server", "ssl_key_path")} and
                not current_settings.get("server", {}).get("enable_ssl", False)):
                if control and isinstance(control, ft.TextField):
                    control.error_text = None
                if control and control.page:
                    control.update()
                continue
            if (identifier == ("security", "api_key") and
                not current_settings.get("security", {}).get("require_auth", False)):
                if control and isinstance(control, ft.TextField):
                    control.error_text = None
                if control and control.page:
                    control.update()
                continue
            ok, message = validator(value)
            if not ok and message:
                errors.append(message)
                if control and isinstance(control, ft.TextField):
                    control.error_text = message
                if control and control.page:
                    control.update()
            else:
                if control and isinstance(control, ft.TextField):
                    control.error_text = None
                if control and control.page:
                    control.update()
        return errors

    def _apply_theme(mode: str) -> None:
        if not page:
            return
        theme_mode = mode.lower()
        if theme_mode == "light":
            page.theme_mode = ft.ThemeMode.LIGHT
        elif theme_mode == "dark":
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.SYSTEM
        page.update()
        if state_manager:
            state_manager.broadcast_settings_event("theme_change", {"theme_mode": theme_mode})

    def _apply_color_seed(seed_key: str) -> None:
        seed = COLOR_SEEDS.get(seed_key, COLOR_SEEDS["blue"])
        theme = page.theme or ft.Theme()
        theme.color_scheme_seed = seed
        theme.use_material3 = True
        page.theme = theme
        page.update()
        if state_manager:
            state_manager.broadcast_settings_event("color_seed_change", {"color": seed_key})

    def _apply_dependent_states() -> None:
        enable_ssl = bool(current_settings.get("server", {}).get("enable_ssl"))
        server_cert.disabled = not enable_ssl
        server_key.disabled = not enable_ssl
        require_auth = bool(current_settings.get("security", {}).get("require_auth"))
        security_api_key.disabled = not require_auth
        for control in (server_cert, server_key, security_api_key):
            if hasattr(control, "update") and control.page:
                control.update()

    def _update_status() -> None:
        if not status_text:
            return
        dirty_count = sum(len(items) for items in dirty_tracker.values())
        if dirty_count:
            status_text.value = f"{dirty_count} pending change(s); auto-save in 2s"
        else:
            status_text.value = ""
        if status_text.page:
            status_text.update()

    def _record_dirty(category: str, key: str) -> None:
        dirty_tracker.setdefault(category, set()).add(key)
        _update_status()

    def _update_state(category: str, key: str, value: Any) -> None:
        current_settings.setdefault(category, {})[key] = value
        _record_dirty(category, key)
        if state_manager:
            state_manager.update(
                f"settings.{category}.{key}",
                value,
                source="settings_view_change",
            )

    def _handle_validation(category: str, key: str, value: Any, control: ft.Control) -> bool:
        validator = validation_rules.get((category, key))
        if (category, key) in {
            ("server", "ssl_cert_path"),
            ("server", "ssl_key_path"),
        }:
            # Conditional requirement based on SSL state
            if not current_settings.get("server", {}).get("enable_ssl", False):
                if isinstance(control, ft.TextField):
                    control.error_text = None
                if isinstance(control, ft.TextField):
                    control.disabled = True
                    if control.page:
                        control.update()
                return True
            if isinstance(control, ft.TextField):
                control.disabled = False
                if control.page:
                    control.update()
        if (category, key) == ("security", "api_key"):
            if not current_settings.get("security", {}).get("require_auth", False):
                if isinstance(control, ft.TextField):
                    control.error_text = None
                if isinstance(control, ft.TextField):
                    control.disabled = True
                    if control.page:
                        control.update()
                return True
            if isinstance(control, ft.TextField):
                control.disabled = False
                if control.page:
                    control.update()
        if not validator:
            if isinstance(control, ft.TextField):
                control.error_text = None
            return True
        ok, message = validator(value)
        if isinstance(control, ft.TextField):
            control.error_text = message
        if control.page:
            control.update()
        return ok

    def _apply_and_schedule(category: str, key: str, value: Any, control: ft.Control) -> None:
        if not _handle_validation(category, key, value, control):
            return
        _update_state(category, key, value)

        if category == "gui" and key == "theme_mode":
            _apply_theme(str(value))
        if category == "gui" and key == "color_scheme":
            _apply_color_seed(str(value))
        if category == "gui" and key == "refresh_interval" and state_manager:
            state_manager.broadcast_settings_event("refresh_interval_change", {"interval": value})
        if category == "logging" and key == "level" and state_manager:
            state_manager.broadcast_settings_event("logging_level_change", {"level": value})
        if category == "server" and key == "enable_ssl":
            server_cert.disabled = not bool(value)
            server_key.disabled = not bool(value)
            if server_cert.page:
                server_cert.update()
            if server_key.page:
                server_key.update()
        if category == "security" and key == "require_auth":
            security_api_key.disabled = not bool(value)
            if security_api_key.page:
                security_api_key.update()
        _update_status()

        _schedule_autosave()

    def _bind_control(
        category: str,
        key: str,
        control: ft.Control,
        *,
        parser: Parser | None = None,
        validator: Validator | None = None,
    ) -> ft.Control:
        controls[(category, key)] = control
        if validator:
            validation_rules[(category, key)] = validator
        if parser:
            parsers[(category, key)] = parser

        def _on_change(event: ft.ControlEvent) -> None:
            raw_value = getattr(event.control, "value", None)
            parse = parsers.get((category, key))
            value = parse(raw_value) if parse else raw_value
            _apply_and_schedule(category, key, value, event.control)

        if isinstance(control, ft.TextField):
            control.on_change = _on_change
        elif isinstance(control, (ft.Switch, ft.Checkbox, ft.Dropdown, ft.Slider)):
            control.on_change = _on_change

        return control

    # Server tab controls
    server_port = _bind_control(
        "server",
        "port",
        ft.TextField(width=140, label="Port", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(1024, 65535, "Port"),
    )
    server_host = _bind_control(
        "server",
        "host",
        ft.TextField(width=220, label="Host"),
        validator=_validate_required("Host"),
    )
    server_max_clients = _bind_control(
        "server",
        "max_clients",
        ft.TextField(width=160, label="Max clients", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(1, 1000, "Max clients"),
    )
    server_timeout = _bind_control(
        "server",
        "timeout",
        ft.TextField(width=160, label="Timeout (s)", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(5, 600, "Timeout"),
    )
    server_ssl = _bind_control("server", "enable_ssl", ft.Switch(label="Enable SSL"))
    server_cert = _bind_control(
        "server",
        "ssl_cert_path",
        ft.TextField(label="SSL certificate path", expand=True),
        validator=_validate_required("Certificate path"),
    )
    server_key = _bind_control(
        "server",
        "ssl_key_path",
        ft.TextField(label="SSL key path", expand=True),
        validator=_validate_required("Key path"),
    )

    # Interface tab
    theme_dropdown = _bind_control(
        "gui",
        "theme_mode",
        ft.Dropdown(
            width=180,
            label="Theme mode",
            options=[
                ft.dropdown.Option("light", "Light"),
                ft.dropdown.Option("dark", "Dark"),
                ft.dropdown.Option("system", "System"),
            ],
        ),
    )
    color_dropdown = _bind_control(
        "gui",
        "color_scheme",
        ft.Dropdown(
            width=200,
            label="Color seed",
            options=[ft.dropdown.Option(key, key.title()) for key in COLOR_SEEDS],
        ),
    )
    auto_refresh = _bind_control("gui", "auto_refresh", ft.Switch(label="Auto refresh"))
    refresh_interval = _bind_control(
        "gui",
        "refresh_interval",
        ft.TextField(width=180, label="Refresh interval (s)", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(1, 300, "Refresh interval"),
    )
    auto_resize = _bind_control("gui", "auto_resize", ft.Switch(label="Responsive layout"))

    # Monitoring tab
    monitoring_enabled = _bind_control("monitoring", "enabled", ft.Switch(label="Enable monitoring"))
    monitoring_refresh = _bind_control(
        "monitoring",
        "refresh_interval",
        ft.TextField(width=200, label="Refresh interval (s)", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(5, 600, "Monitoring interval"),
    )
    monitoring_cpu = _bind_control(
        "monitoring",
        "cpu_threshold",
        ft.TextField(width=200, label="CPU threshold (%)", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(1, 100, "CPU threshold"),
    )
    monitoring_memory = _bind_control(
        "monitoring",
        "memory_threshold",
        ft.TextField(width=200, label="Memory threshold (%)", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(1, 100, "Memory threshold"),
    )
    monitoring_disk = _bind_control(
        "monitoring",
        "disk_threshold",
        ft.TextField(width=200, label="Disk threshold (%)", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(1, 100, "Disk threshold"),
    )

    # Logging tab
    logging_enabled = _bind_control("logging", "enabled", ft.Switch(label="Enable logging"))
    logging_level = _bind_control(
        "logging",
        "level",
        ft.Dropdown(
            width=180,
            label="Log level",
            options=[
                ft.dropdown.Option("DEBUG"),
                ft.dropdown.Option("INFO"),
                ft.dropdown.Option("WARNING"),
                ft.dropdown.Option("ERROR"),
            ],
        ),
    )
    logging_file = _bind_control(
        "logging",
        "file_path",
        ft.TextField(label="Log file path", expand=True),
        validator=_validate_required("Log file path"),
    )
    logging_max_size = _bind_control(
        "logging",
        "max_size_mb",
        ft.TextField(width=200, label="Max size (MB)", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(1, 10240, "Max file size"),
    )
    logging_max_files = _bind_control(
        "logging",
        "max_files",
        ft.TextField(width=200, label="Max files", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(1, 50, "Rotation count"),
    )

    # Security tab
    security_require_auth = _bind_control(
        "security",
        "require_auth",
        ft.Switch(label="Require authentication"),
    )
    security_api_key = _bind_control(
        "security",
        "api_key",
        ft.TextField(label="API key", password=True, can_reveal_password=True, expand=True),
        validator=_validate_required("API key")
    )
    security_max_attempts = _bind_control(
        "security",
        "max_login_attempts",
        ft.TextField(width=220, label="Max login attempts", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(1, 10, "Max login attempts"),
    )
    security_session_timeout = _bind_control(
        "security",
        "session_timeout",
        ft.TextField(width=220, label="Session timeout (s)", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(60, 86400, "Session timeout"),
    )

    # Backup tab
    backup_auto = _bind_control("backup", "auto_backup", ft.Switch(label="Auto backups"))
    backup_path = _bind_control(
        "backup",
        "backup_path",
        ft.TextField(label="Backup path", expand=True),
        validator=_validate_required("Backup path"),
    )
    backup_interval = _bind_control(
        "backup",
        "backup_interval_hours",
        ft.TextField(width=220, label="Backup interval (hours)", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(1, 168, "Backup interval"),
    )
    backup_retention = _bind_control(
        "backup",
        "retention_days",
        ft.TextField(width=220, label="Retention (days)", keyboard_type=ft.KeyboardType.NUMBER),
        parser=_safe_int,
        validator=_validate_range(1, 365, "Retention"),
    )
    backup_compress = _bind_control("backup", "compress_backups", ft.Switch(label="Compress backups"))

    server_section = create_settings_section(
        "Server",
        [
            create_setting_row("Connection", ft.Row([server_host, server_port], spacing=12)),
            create_setting_row("Capacity", ft.Row([server_max_clients, server_timeout], spacing=12)),
            create_setting_row("Security", server_ssl, "Enable TLS for client connections"),
            create_setting_row("Certificate", server_cert),
            create_setting_row("Key", server_key),
        ],
    )

    interface_section = create_settings_section(
        "Interface",
        [
            create_setting_row("Theme", ft.Row([theme_dropdown, color_dropdown], spacing=12)),
            create_setting_row("Refresh", ft.Row([auto_refresh, refresh_interval], spacing=12)),
            create_setting_row("Layout", auto_resize, "Automatically adapt layout to window size"),
        ],
    )

    monitoring_section = create_settings_section(
        "Monitoring",
        [
            create_setting_row("Status", monitoring_enabled),
            create_setting_row("Sampling", monitoring_refresh, "Frequency for health polls"),
            create_setting_row(
                "Thresholds",
                ft.Row([monitoring_cpu, monitoring_memory, monitoring_disk], spacing=12),
            ),
        ],
    )

    logging_section = create_settings_section(
        "Logging",
        [
            create_setting_row("Status", logging_enabled),
            create_setting_row("Level", logging_level),
            create_setting_row("Storage", logging_file),
            create_setting_row("Rotation", ft.Row([logging_max_size, logging_max_files], spacing=12)),
        ],
    )

    security_section = create_settings_section(
        "Security",
        [
            create_setting_row("Authentication", security_require_auth),
            create_setting_row("API key", security_api_key),
            create_setting_row(
                "Login policy",
                ft.Row([security_max_attempts, security_session_timeout], spacing=12),
            ),
        ],
    )

    backup_section = create_settings_section(
        "Backup",
        [
            create_setting_row("Automation", backup_auto),
            create_setting_row("Destination", backup_path),
            create_setting_row("Cadence", ft.Row([backup_interval, backup_retention], spacing=12)),
            create_setting_row("Compression", backup_compress),
        ],
    )

    tabs = ft.Tabs(
        expand=True,
        animation_duration=300,
        divider_color=ft.Colors.TRANSPARENT,
        tabs=[
            ft.Tab(text="Server", icon=ft.Icons.DNS, content=server_section),
            ft.Tab(text="Interface", icon=ft.Icons.PALETTE, content=interface_section),
            ft.Tab(text="Monitoring", icon=ft.Icons.MONITOR_HEART, content=monitoring_section),
            ft.Tab(text="Logging", icon=ft.Icons.ARTICLE, content=logging_section),
            ft.Tab(text="Security", icon=ft.Icons.SECURITY, content=security_section),
            ft.Tab(text="Backup", icon=ft.Icons.BACKUP, content=backup_section),
        ],
    )

    async def _export_settings(path: str) -> None:
        payload = copy.deepcopy(current_settings)
        async with aiofiles.open(path, "w") as fp:
            await fp.write(json.dumps(payload, indent=2))
        show_success_message(page, f"Settings exported to {path}")

    async def _import_settings(path: str) -> None:
        nonlocal current_settings
        async with aiofiles.open(path) as fp:
            data = json.loads(await fp.read())
        if not isinstance(data, dict):
            raise ValueError("Invalid settings file")
        merged = _default_settings()
        for category, values in data.items():
            if category in merged and isinstance(values, dict):
                merged[category].update(values)
        current_settings = merged
        _refresh_controls()
        _apply_theme(current_settings["gui"].get("theme_mode", "system"))
        _apply_color_seed(current_settings["gui"].get("color_scheme", "blue"))
        if state_manager:
            state_manager.update(
                "settings_data",
                copy.deepcopy(current_settings),
                source="settings_view_import",
            )
        show_success_message(page, "Settings imported")

    def _handle_export(_: ft.ControlEvent) -> None:
        def _on_export_result(e: ft.FilePickerResultEvent) -> None:
            if e.path:
                _schedule(page, lambda: _export_settings(e.path))

        picker = ft.FilePicker(on_result=_on_export_result)
        page.overlay.append(picker)
        picker.save_file(
            dialog_title="Export settings",
            file_name="settings.json",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
        )

    def _handle_import(_: ft.ControlEvent) -> None:
        def _on_import_result(e: ft.FilePickerResultEvent) -> None:
            if e.files and len(e.files) > 0 and e.files[0] and getattr(e.files[0], "path", None):
                path = e.files[0].path
                _schedule(page, lambda: _import_settings(path))

        picker = ft.FilePicker(on_result=_on_import_result)
        page.overlay.append(picker)
        picker.pick_files(
            dialog_title="Import settings",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
        )

    def _handle_reset(_: ft.ControlEvent) -> None:
        nonlocal current_settings
        current_settings = _default_settings()
        _refresh_controls()
        _apply_theme(current_settings["gui"].get("theme_mode", "system"))
        _apply_color_seed(current_settings["gui"].get("color_scheme", "blue"))
        if state_manager:
            state_manager.update(
                "settings_data",
                copy.deepcopy(current_settings),
                source="settings_view_reset",
            )
        show_success_message(page, "Settings reset to defaults")

    def _handle_save(_: ft.ControlEvent) -> None:
        _schedule(page, lambda: persist_settings(auto=False))

    utilities = ft.Row(
        [
            create_action_button("Export", _handle_export, icon=ft.Icons.UPLOAD, primary=False),
            create_action_button("Import", _handle_import, icon=ft.Icons.DOWNLOAD, primary=False),
            create_action_button("Reset", _handle_reset, icon=ft.Icons.RESTORE, primary=False),
        ],
        spacing=12,
        wrap=True,
    )

    header = create_view_header(
        "Settings",
        icon=ft.Icons.SETTINGS,
        description="Configure server connectivity, interface preferences, monitoring, and automation.",
        actions=[create_action_button("Save", _handle_save, icon=ft.Icons.SAVE)],
    )

    utility_card = AppCard(utilities, title="Utilities", expand_content=False)
    tabs_card = AppCard(tabs, title="Configuration")
    message_bar = ft.Container(content=status_text, padding=ft.padding.symmetric(vertical=4))

    content = ft.Column(
        [
            header,
            message_bar,
            utility_card,
            tabs_card,
        ],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    layout = ft.Container(
        content=content,
        expand=True,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
    )

    async def setup() -> None:
        status_text.value = "Loading settings…"
        status_text.update()
        await load_settings()
        status_text.value = ""
        status_text.update()

    def dispose() -> None:
        logger.debug("Disposing settings view")

    return layout, dispose, setup
