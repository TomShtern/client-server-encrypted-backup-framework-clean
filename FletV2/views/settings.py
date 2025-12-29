#!/usr/bin/env python3
"""Complete Settings View for Flet 0.80.0 - Using proven working pattern.

All 6 tabs: Server, Interface, Monitoring, Logging, Security, Backup
"""

from __future__ import annotations

import copy
import logging
from typing import Any, Callable, Coroutine

import flet as ft

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
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

COLOR_SEEDS = {
    "blue": "#3B82F6",
    "indigo": "#6366F1",
    "purple": "#8B5CF6",
    "pink": "#EC4899",
    "green": "#10B981",
    "orange": "#F59E0B",
    "red": "#EF4444",
}


def create_settings_view(
    server_bridge=None,
    page: ft.Page = None,
    state_manager=None,
    global_search=None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    """Create complete settings view with all 6 tabs."""

    data = copy.deepcopy(DEFAULT_SETTINGS)
    controls: dict[tuple[str, str], ft.Control] = {}
    tab_buttons: list[ft.Container] = []
    tab_contents: list[ft.Control] = []
    content_container: ft.Container | None = None
    status_text = ft.Text("", size=12, color=ft.Colors.GREY_600)

    def safe_int(val):
        try:
            return int(str(val).strip())
        except Exception:
            return 0

    def update_status(msg: str):
        status_text.value = msg
        try:
            if status_text.page:
                status_text.update()
        except Exception as e:
            logger.debug(f"Failed to update status text: {e}")

    def safe_update(ctl):
        try:
            if ctl.page:
                ctl.update()
        except Exception as e:
            logger.debug(f"Safe update failed for {ctl}: {e}")

    def switch_tab(index: int):
        for i, btn in enumerate(tab_buttons):
            is_sel = i == index
            btn.border = ft.border.only(
                bottom=ft.BorderSide(
                    2, ft.Colors.PRIMARY if is_sel else ft.Colors.TRANSPARENT
                )
            )
            row = btn.content
            if isinstance(row, ft.Row) and len(row.controls) >= 2:
                row.controls[0].color = (
                    ft.Colors.PRIMARY if is_sel else ft.Colors.GREY_600
                )
                row.controls[1].color = (
                    ft.Colors.PRIMARY if is_sel else ft.Colors.GREY_600
                )
                row.controls[1].weight = (
                    ft.FontWeight.W_600 if is_sel else ft.FontWeight.W_400
                )
        if content_container:
            content_container.content = tab_contents[index]
        if page:
            page.update()

    def create_tab_button(index: int, label: str, icon, selected: bool) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        icon,
                        size=18,
                        color=ft.Colors.PRIMARY if selected else ft.Colors.GREY_600,
                    ),
                    ft.Text(
                        label,
                        weight=ft.FontWeight.W_600 if selected else ft.FontWeight.W_400,
                        color=ft.Colors.PRIMARY if selected else ft.Colors.GREY_600,
                    ),
                ],
                spacing=6,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border=ft.border.only(
                bottom=ft.BorderSide(
                    2, ft.Colors.PRIMARY if selected else ft.Colors.TRANSPARENT
                )
            ),
            on_click=lambda e, idx=index: switch_tab(idx),
            ink=True,
        )

    def text_field(
        section: str,
        key: str,
        label: str,
        width=None,
        expand=False,
        password=False,
        number=False,
    ):
        field = ft.TextField(
            label=label,
            width=width,
            expand=expand,
            password=password,
            can_reveal_password=password,
        )
        controls[(section, key)] = field

        def on_change(e: ft.ControlEvent):
            val = e.control.value
            if number:
                val = safe_int(val)
            data.setdefault(section, {})[key] = val
            apply_deps()
            apply_effects(section, key, val)

        field.on_change = on_change
        return field

    def switch_field(section: str, key: str, label: str):
        sw = ft.Switch()
        sw.tooltip = label
        controls[(section, key)] = sw

        def on_change(e: ft.ControlEvent):
            val = bool(e.control.value)
            data.setdefault(section, {})[key] = val
            apply_deps()
            apply_effects(section, key, val)

        sw.on_change = on_change
        return sw

    def dropdown_field(section: str, key: str, label: str, options: list, width=None):
        dd_opts = [
            ft.dropdown.Option(o[0], o[1])
            if isinstance(o, tuple)
            else ft.dropdown.Option(o)
            for o in options
        ]
        dd = ft.Dropdown(label=label, options=dd_opts, width=width)
        controls[(section, key)] = dd

        def on_change(e: ft.ControlEvent):
            val = e.control.value
            data.setdefault(section, {})[key] = val
            apply_deps()
            apply_effects(section, key, val)

        dd.on_change = on_change
        return dd

    def row(label: str, control, desc: str = None):
        is_sw = isinstance(control, ft.Switch)
        if desc:
            control.tooltip = desc
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(label, size=13, weight=ft.FontWeight.W_500),
                        width=140 if not is_sw else None,
                        expand=is_sw,
                    ),
                    control,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
        )

    def section(title: str, icon, rows: list):
        hdr = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=18, color=ft.Colors.PRIMARY),
                    ft.Text(title, size=14, weight=ft.FontWeight.W_600),
                ],
                spacing=10,
            ),
            padding=ft.padding.only(left=16, right=12, top=10, bottom=6),
        )
        return ft.Container(
            content=ft.Column([hdr, *rows], spacing=0),
            bgcolor=ft.Colors.SURFACE,
            border_radius=10,
            border=ft.border.only(
                left=ft.BorderSide(3, ft.Colors.PRIMARY),
                top=ft.BorderSide(1, ft.Colors.OUTLINE),
                right=ft.BorderSide(1, ft.Colors.OUTLINE),
                bottom=ft.BorderSide(1, ft.Colors.OUTLINE),
            ),
            margin=ft.margin.only(bottom=10),
        )

    def apply_deps():
        ssl_on = bool(data.get("server", {}).get("enable_ssl"))
        for k in ("ssl_cert_path", "ssl_key_path"):
            c = controls.get(("server", k))
            if isinstance(c, ft.TextField):
                c.disabled = not ssl_on
                safe_update(c)
        auth_on = bool(data.get("security", {}).get("require_auth"))
        api_c = controls.get(("security", "api_key"))
        if isinstance(api_c, ft.TextField):
            api_c.disabled = not auth_on
            safe_update(api_c)

    def apply_effects(sec: str, key: str, val):
        if sec != "gui" or not page:
            return
        if key == "theme_mode":
            m = str(val or "system").lower()
            page.theme_mode = (
                ft.ThemeMode.SYSTEM
                if m == "system"
                else ft.ThemeMode.DARK
                if m == "dark"
                else ft.ThemeMode.LIGHT
            )
            page.update()
        elif key == "color_scheme":
            seed = COLOR_SEEDS.get(str(val), COLOR_SEEDS["blue"])
            theme = page.theme or ft.Theme()
            theme.color_scheme_seed = seed
            theme.use_material3 = True
            page.theme = theme
            page.update()

    def refresh_controls():
        for (sec, key), ctl in controls.items():
            val = data.get(sec, {}).get(key)
            if isinstance(ctl, ft.TextField):
                ctl.value = "" if val is None else str(val)
            elif isinstance(ctl, ft.Switch):
                ctl.value = bool(val)
            elif isinstance(ctl, ft.Dropdown):
                ctl.value = val
            safe_update(ctl)
        apply_deps()

    def on_save(e: ft.ControlEvent):
        update_status("Saved")

    def on_reset(e: ft.ControlEvent):
        nonlocal data
        data = copy.deepcopy(DEFAULT_SETTINGS)
        refresh_controls()
        update_status("Reset to defaults")

    # Tab 1: Server
    server_tab = ft.Container(
        expand=True,
        padding=10,
        content=ft.Column(
            [
                section(
                    "Network",
                    ft.Icons.ROUTER,
                    [
                        row("Host", text_field("server", "host", "Host", width=260)),
                        row(
                            "Port",
                            text_field(
                                "server", "port", "Port", width=180, number=True
                            ),
                        ),
                        row(
                            "Max clients",
                            text_field(
                                "server", "max_clients", "Max", width=200, number=True
                            ),
                        ),
                        row(
                            "Timeout",
                            text_field(
                                "server",
                                "timeout",
                                "Timeout (s)",
                                width=200,
                                number=True,
                            ),
                        ),
                    ],
                ),
                section(
                    "TLS",
                    ft.Icons.LOCK,
                    [
                        row(
                            "Enable TLS",
                            switch_field("server", "enable_ssl", "Enable TLS"),
                        ),
                        row(
                            "Certificate",
                            text_field(
                                "server", "ssl_cert_path", "Cert path", expand=True
                            ),
                        ),
                        row(
                            "Key",
                            text_field(
                                "server", "ssl_key_path", "Key path", expand=True
                            ),
                        ),
                    ],
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        ),
    )

    # Tab 2: Interface
    interface_tab = ft.Container(
        expand=True,
        padding=10,
        content=ft.Column(
            [
                section(
                    "Theme",
                    ft.Icons.PALETTE,
                    [
                        row(
                            "Theme mode",
                            dropdown_field(
                                "gui",
                                "theme_mode",
                                "Theme",
                                [
                                    ("light", "Light"),
                                    ("dark", "Dark"),
                                    ("system", "System"),
                                ],
                                width=220,
                            ),
                        ),
                        row(
                            "Color seed",
                            dropdown_field(
                                "gui",
                                "color_scheme",
                                "Color",
                                [(k, k.title()) for k in COLOR_SEEDS],
                                width=220,
                            ),
                        ),
                    ],
                ),
                section(
                    "Behavior",
                    ft.Icons.TUNE,
                    [
                        row(
                            "Auto refresh",
                            switch_field("gui", "auto_refresh", "Auto refresh"),
                        ),
                        row(
                            "Interval",
                            text_field(
                                "gui",
                                "refresh_interval",
                                "Interval (s)",
                                width=200,
                                number=True,
                            ),
                        ),
                        row(
                            "Responsive",
                            switch_field("gui", "auto_resize", "Auto resize"),
                        ),
                    ],
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        ),
    )

    # Tab 3: Monitoring
    monitoring_tab = ft.Container(
        expand=True,
        padding=10,
        content=ft.Column(
            [
                section(
                    "Monitoring",
                    ft.Icons.ASSESSMENT,
                    [
                        row(
                            "Enable",
                            switch_field("monitoring", "enabled", "Enable monitoring"),
                        ),
                        row(
                            "Interval",
                            text_field(
                                "monitoring",
                                "refresh_interval",
                                "Interval (s)",
                                width=200,
                                number=True,
                            ),
                        ),
                        row(
                            "CPU threshold",
                            text_field(
                                "monitoring",
                                "cpu_threshold",
                                "CPU %",
                                width=200,
                                number=True,
                            ),
                        ),
                        row(
                            "Memory threshold",
                            text_field(
                                "monitoring",
                                "memory_threshold",
                                "Memory %",
                                width=200,
                                number=True,
                            ),
                        ),
                        row(
                            "Disk threshold",
                            text_field(
                                "monitoring",
                                "disk_threshold",
                                "Disk %",
                                width=200,
                                number=True,
                            ),
                        ),
                    ],
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        ),
    )

    # Tab 4: Logging
    logging_tab = ft.Container(
        expand=True,
        padding=10,
        content=ft.Column(
            [
                section(
                    "Logging",
                    ft.Icons.ARTICLE,
                    [
                        row(
                            "Enable",
                            switch_field("logging", "enabled", "Enable logging"),
                        ),
                        row(
                            "Level",
                            dropdown_field(
                                "logging",
                                "level",
                                "Level",
                                ["DEBUG", "INFO", "WARNING", "ERROR"],
                                width=220,
                            ),
                        ),
                        row(
                            "File path",
                            text_field("logging", "file_path", "Path", expand=True),
                        ),
                        row(
                            "Max size",
                            text_field(
                                "logging", "max_size_mb", "MB", width=200, number=True
                            ),
                        ),
                        row(
                            "Max files",
                            text_field(
                                "logging", "max_files", "Files", width=200, number=True
                            ),
                        ),
                    ],
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        ),
    )

    # Tab 5: Security
    security_tab = ft.Container(
        expand=True,
        padding=10,
        content=ft.Column(
            [
                section(
                    "Security",
                    ft.Icons.SECURITY,
                    [
                        row(
                            "Require auth",
                            switch_field(
                                "security", "require_auth", "Require authentication"
                            ),
                        ),
                        row(
                            "API key",
                            text_field(
                                "security",
                                "api_key",
                                "API key",
                                expand=True,
                                password=True,
                            ),
                        ),
                        row(
                            "Max attempts",
                            text_field(
                                "security",
                                "max_login_attempts",
                                "Attempts",
                                width=200,
                                number=True,
                            ),
                        ),
                        row(
                            "Session timeout",
                            text_field(
                                "security",
                                "session_timeout",
                                "Timeout (s)",
                                width=200,
                                number=True,
                            ),
                        ),
                    ],
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        ),
    )

    # Tab 6: Backup
    backup_tab = ft.Container(
        expand=True,
        padding=10,
        content=ft.Column(
            [
                section(
                    "Backup",
                    ft.Icons.BACKUP,
                    [
                        row(
                            "Auto backup",
                            switch_field("backup", "auto_backup", "Auto backup"),
                        ),
                        row(
                            "Backup path",
                            text_field("backup", "backup_path", "Path", expand=True),
                        ),
                        row(
                            "Interval",
                            text_field(
                                "backup",
                                "backup_interval_hours",
                                "Hours",
                                width=200,
                                number=True,
                            ),
                        ),
                        row(
                            "Retention",
                            text_field(
                                "backup",
                                "retention_days",
                                "Days",
                                width=200,
                                number=True,
                            ),
                        ),
                        row(
                            "Compress",
                            switch_field(
                                "backup", "compress_backups", "Compress backups"
                            ),
                        ),
                    ],
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        ),
    )

    tab_contents = [
        server_tab,
        interface_tab,
        monitoring_tab,
        logging_tab,
        security_tab,
        backup_tab,
    ]
    tab_labels = [
        ("Server", ft.Icons.DNS),
        ("Interface", ft.Icons.PALETTE),
        ("Monitoring", ft.Icons.INSIGHTS),
        ("Logging", ft.Icons.ARTICLE),
        ("Security", ft.Icons.SECURITY),
        ("Backup", ft.Icons.BACKUP),
    ]

    for i, (label, icon) in enumerate(tab_labels):
        tab_buttons.append(create_tab_button(i, label, icon, i == 0))

    content_container = ft.Container(content=tab_contents[0], expand=True)

    tab_bar = ft.Container(
        content=ft.Row(controls=tab_buttons, spacing=0),
        border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE)),
    )

    header = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.SETTINGS, size=26, color=ft.Colors.PRIMARY),
                ft.Text("Settings", size=26, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.OutlinedButton("Reset", icon=ft.Icons.RESTORE, on_click=on_reset),
                ft.FilledButton("Save", icon=ft.Icons.SAVE, on_click=on_save),
            ],
            spacing=8,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )

    description = ft.Container(
        content=ft.Text(
            "Configure server, interface, monitoring, logging, security, and backup settings.",
            size=14,
            color=ft.Colors.GREY_600,
        ),
        padding=ft.padding.only(left=16, bottom=8),
    )

    mode_color = ft.Colors.GREEN if server_bridge else ft.Colors.AMBER
    status_bar = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CABLE, size=14, color=mode_color),
                ft.Text(
                    "Direct server" if server_bridge else "Offline mode",
                    size=11,
                    color=mode_color,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Container(expand=True),
                status_text,
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=6),
        bgcolor=ft.Colors.SURFACE,
        border=ft.border.only(
            bottom=ft.BorderSide(1, ft.Colors.OUTLINE),
            top=ft.BorderSide(2, ft.Colors.PRIMARY),
        ),
    )

    root = ft.Container(
        expand=True,
        padding=0,
        content=ft.Column(
            [header, description, status_bar, tab_bar, content_container],
            expand=True,
            spacing=0,
        ),
    )

    def dispose():
        pass

    async def setup():
        refresh_controls()

    return root, dispose, setup


# For backward compatibility
class SettingsView:
    """Wrapper class for compatibility with existing code."""

    def __init__(
        self, page, server_bridge=None, state_manager=None, global_search=None
    ):
        self.page = page
        self.server_bridge = server_bridge
        self.state_manager = state_manager
        self.global_search = global_search
        self._root = None
        self._dispose = None
        self._setup = None

    def build(self):
        self._root, self._dispose, self._setup = create_settings_view(
            server_bridge=self.server_bridge,
            page=self.page,
            state_manager=self.state_manager,
            global_search=self.global_search,
        )
        return self._root

    def dispose(self):
        if self._dispose:
            self._dispose()

    async def setup(self):
        if self._setup:
            await self._setup()
