#!/usr/bin/env python3
"""Canonical UI primitives used across multiple FletV2 views."""

import contextlib
from collections.abc import Callable
from typing import Any

import flet as ft
from theme import get_design_tokens

__all__ = [
    "AppCard",
    "AppButton",
    "SectionHeader",
    "StatusPill",
    "create_status_pill",
    "create_pulsing_status_indicator",
    "create_progress_indicator",
    "DataTableWrapper",
    "FilterBar",
    "safe_update_control",
    "safe_update_controls",
]

_TOKENS = get_design_tokens()
_SPACING = _TOKENS["spacing"]
_RADII = _TOKENS["radii"]


def AppCard(
    content: ft.Control,
    title: str | None = None,
    actions: list[ft.Control] | None = None,
    padding: int | None = None,
    tooltip: str | None = None,
    expand_content: bool = True,
    disable_hover: bool = False,
) -> ft.Container:
    """Material-style card with shared spacing, borders, and hover behaviour."""

    body = ft.Container(content=content, expand=True) if expand_content else content
    header_controls: list[ft.Control] = []
    if title is not None or actions:
        header_controls.extend(
            (
                ft.Row(
                    [
                        ft.Text(title or "", size=16, weight=ft.FontWeight.W_600),
                        ft.Container(expand=True),
                        *(actions or []),
                    ]
                ),
                ft.Divider(height=1, color=ft.Colors.OUTLINE),
            )
        )

    container = ft.Container(
        content=ft.Column(
            [*header_controls, body],
            spacing=_SPACING["lg"],
            expand=expand_content,
            scroll=ft.ScrollMode.AUTO if expand_content else None,
        ),
        expand=1 if expand_content else None,
        padding=ft.padding.all(padding if padding is not None else _SPACING["xl"]),
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=_RADII["lg"],
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=14,
            offset=ft.Offset(0, 6),
            color=ft.Colors.with_opacity(0.16, ft.Colors.SURFACE_TINT),
        ),
        bgcolor=ft.Colors.SURFACE,
        animate=None if disable_hover else ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        animate_scale=None if disable_hover else ft.Animation(120, ft.AnimationCurve.EASE_OUT),
        tooltip=tooltip,
    )

    if not disable_hover:

        def _handle_hover(event: ft.ControlEvent) -> None:
            control = event.control
            if control is None:
                return
            control.scale = 1.01 if event.data == "true" else 1.0
            safe_update_control(control)

        container.on_hover = _handle_hover

    return container


def AppButton(
    text: str,
    on_click: Callable,
    icon: str | None = None,
    variant: str = "primary",
) -> ft.Control:
    """Unified button surface with consistent shape and padding."""

    content = ft.Row(
        ([ft.Icon(icon, size=16)] if icon else []) + [ft.Text(text, size=14, weight=ft.FontWeight.W_500)],
        spacing=_SPACING["sm"],
        tight=True,
    )

    shape = ft.RoundedRectangleBorder(radius=_RADII["md"])
    padding = ft.padding.symmetric(horizontal=_SPACING["xl"], vertical=_SPACING["md"])

    if variant == "outline":
        style = ft.ButtonStyle(shape=shape, padding=padding)
        return ft.OutlinedButton(content=content, on_click=on_click, style=style)
    if variant == "tonal":
        style = ft.ButtonStyle(shape=shape, padding=padding)
        return ft.FilledTonalButton(content=content, on_click=on_click, style=style)
    if variant == "danger":
        style = ft.ButtonStyle(shape=shape, padding=padding, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
        return ft.FilledButton(content=content, on_click=on_click, style=style)
    if variant == "success":
        style = ft.ButtonStyle(shape=shape, padding=padding, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
        return ft.FilledButton(content=content, on_click=on_click, style=style)

    style = ft.ButtonStyle(shape=shape, padding=padding)
    return ft.FilledButton(content=content, on_click=on_click, style=style)


def SectionHeader(title: str, actions: list[ft.Control] | None = None) -> ft.Row:
    """Section heading row with optional trailing action controls."""

    return ft.Row(
        [
            ft.Text(title, size=20, weight=ft.FontWeight.W_600),
            ft.Container(expand=True),
            *(actions or []),
        ]
    )


def StatusPill(label: str, level: str = "info") -> ft.Container:
    """Compact pill used for status display across views."""

    palette = {
        "success": ft.Colors.GREEN,
        "warning": ft.Colors.AMBER,
        "error": ft.Colors.RED,
        "info": ft.Colors.BLUE,
        "neutral": ft.Colors.GREY,
    }
    color = palette.get(level.lower(), palette["neutral"])

    return ft.Container(
        content=ft.Text(label, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
        padding=ft.padding.symmetric(horizontal=_SPACING["md"], vertical=2),
        bgcolor=color,
        border_radius=_RADII.get("chip", _RADII["lg"]),
    )


def create_status_pill(label: str, level: str = "info") -> ft.Container:
    """Compatibility wrapper retained for legacy imports."""

    return StatusPill(label, level)


def create_pulsing_status_indicator(status: str, text: str) -> ft.Container:
    """Soft pulsing indicator used by the dashboard status block."""

    status_colors = {
        "excellent": "#10B981",
        "good": "#059669",
        "warning": "#F59E0B",
        "critical": "#EF4444",
        "info": "#3B82F6",
        "neutral": "#6B7280",
    }

    color = status_colors.get(status, status_colors["neutral"])

    pulsing_dot = ft.Container(
        width=12,
        height=12,
        border_radius=6,
        bgcolor=color,
        animate=ft.Animation(1500, ft.AnimationCurve.EASE_IN_OUT),
        shadow=ft.BoxShadow(spread_radius=2, blur_radius=8, color=ft.Colors.with_opacity(0.4, color)),
    )

    return ft.Container(
        content=ft.Row(
            [
                pulsing_dot,
                ft.Text(text, size=14, weight=ft.FontWeight.W_500, color="#F8FAFC"),
            ],
            spacing=_SPACING["sm"],
        ),
        padding=ft.padding.symmetric(horizontal=_SPACING["lg"], vertical=_SPACING["sm"]),
        border_radius=_RADII["lg"],
        bgcolor=ft.Colors.with_opacity(0.1, color),
        border=ft.border.all(1, ft.Colors.with_opacity(0.2, color)),
    )


def DataTableWrapper(table: ft.DataTable) -> ft.Container:
    """Shared container styling for data tables."""

    return ft.Container(
        content=table,
        padding=ft.padding.all(_SPACING["lg"]),
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=_RADII["lg"],
        bgcolor=ft.Colors.SURFACE,
    )


def FilterBar(controls: list[ft.Control]) -> ft.Row:
    """Consistent layout for filter rows."""

    return ft.Row(controls, spacing=_SPACING["lg"], alignment=ft.MainAxisAlignment.START)


def safe_update_control(control: ft.Control | None, force: bool = False) -> bool:
    """Safely call ``update`` on a control when still attached to a page."""

    with contextlib.suppress(Exception):
        if control is None or not hasattr(control, "update"):
            return False

        if not force and getattr(control, "page", None) is None:
            return False

        control.update()
        return True

    return False


def safe_update_controls(*controls: ft.Control, force: bool = False) -> int:
    """Bulk variant of ``safe_update_control`` returning the update count."""

    return sum(safe_update_control(control, force) for control in controls)


def create_progress_indicator(operation: str, state_manager: Any | None = None) -> ft.Container:
    """Compact progress indicator used by settings action blocks."""

    _ = operation, state_manager  # Maintained for compatibility hooks

    return ft.Container(
        content=ft.Row(
            [
                ft.ProgressRing(width=20, height=20, visible=False),
                ft.Text("", size=12, visible=False),
            ],
            spacing=_SPACING["sm"],
        ),
        visible=False,
    )
