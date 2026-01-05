#!/usr/bin/env python3
"""Canonical UI primitives used across multiple FletV2 views."""

import contextlib
from collections.abc import Callable
from typing import Any

import flet as ft
from theme import get_design_tokens

__all__ = [
    "AppButton",
    "AppCard",
    "DataTableWrapper",
    "FilterBar",
    "SectionHeader",
    "StatusPill",
    "create_pulsing_status_indicator",
    "create_status_pill",
    "create_matte_card",
    "ActivityItem",
    "HealthGauge",
    "HealthGaugeWithTooltip",
    "DiskUsageBar",
    "is_control_attached",
    "safe_update_control",
    "safe_update_controls",
]

_TOKENS = get_design_tokens()
_SPACING = _TOKENS["spacing"]
_RADII = _TOKENS["radii"]


def is_control_attached(control: ft.Control | None) -> bool:
    """Check if a control is attached to a page.

    In Flet 0.80.0, accessing .page on an unattached control raises RuntimeError,
    so we use try/except instead of getattr.

    Args:
        control: The Flet control to check

    Returns:
        True if the control is attached to a page, False otherwise
    """
    if control is None:
        return False
    try:
        return control.page is not None
    except (RuntimeError, AttributeError):
        return False


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
        padding=ft.Padding.all(padding if padding is not None else _SPACING["xl"]),
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=_RADII["lg"],
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=14,
            offset=ft.Offset(0, 6),
            color=ft.Colors.with_opacity(0.16, ft.Colors.SURFACE_TINT),
        ),
        bgcolor=ft.Colors.SURFACE,
        animate=None
        if disable_hover
        else ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        animate_scale=None
        if disable_hover
        else ft.Animation(120, ft.AnimationCurve.EASE_OUT),
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
        ([ft.Icon(icon, size=16)] if icon else [])
        + [ft.Text(text, size=14, weight=ft.FontWeight.W_500)],
        spacing=_SPACING["sm"],
        tight=True,
    )

    shape = ft.RoundedRectangleBorder(radius=_RADII["md"])
    padding = ft.Padding.symmetric(horizontal=_SPACING["xl"], vertical=_SPACING["md"])

    if variant == "outline":
        style = ft.ButtonStyle(shape=shape, padding=padding)
        return ft.OutlinedButton(content=content, on_click=on_click, style=style)
    if variant == "tonal":
        style = ft.ButtonStyle(shape=shape, padding=padding)
        return ft.FilledTonalButton(content=content, on_click=on_click, style=style)
    if variant == "danger":
        style = ft.ButtonStyle(
            shape=shape, padding=padding, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE
        )
        return ft.FilledButton(content=content, on_click=on_click, style=style)
    if variant == "success":
        style = ft.ButtonStyle(
            shape=shape, padding=padding, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE
        )
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
        content=ft.Text(
            label, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600
        ),
        padding=ft.Padding.symmetric(horizontal=_SPACING["md"], vertical=2),
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
        shadow=ft.BoxShadow(
            spread_radius=2, blur_radius=8, color=ft.Colors.with_opacity(0.4, color)
        ),
    )

    return ft.Container(
        content=ft.Row(
            [
                pulsing_dot,
                ft.Text(text, size=14, weight=ft.FontWeight.W_500, color="#F8FAFC"),
            ],
            spacing=_SPACING["sm"],
        ),
        padding=ft.Padding.symmetric(
            horizontal=_SPACING["lg"], vertical=_SPACING["sm"]
        ),
        border_radius=_RADII["lg"],
        bgcolor=ft.Colors.with_opacity(0.1, color),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, color)),
    )


def DataTableWrapper(table: ft.DataTable) -> ft.Container:
    """Shared container styling for data tables."""

    return ft.Container(
        content=table,
        padding=ft.Padding.all(_SPACING["lg"]),
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        border_radius=_RADII["lg"],
        bgcolor=ft.Colors.SURFACE,
    )


def FilterBar(controls: list[ft.Control]) -> ft.Row:
    """Consistent layout for filter rows."""

    return ft.Row(
        controls, spacing=_SPACING["lg"], alignment=ft.MainAxisAlignment.START
    )


def safe_update_control(control: ft.Control | None, force: bool = False) -> bool:
    """Safely call ``update`` on a control when still attached to a page."""

    with contextlib.suppress(Exception):
        if control is None or not hasattr(control, "update"):
            return False

        if not force and not is_control_attached(control):
            return False

        control.update()
        return True

    return False


def safe_update_controls(*controls: ft.Control, force: bool = False) -> int:
    """Bulk variant of ``safe_update_control`` returning the update count."""

    return sum(safe_update_control(control, force) for control in controls)


def create_matte_card(
    accent_color: str = "",
    title: str | None = None,
    icon: str | None = None,
    value_control: ft.Control | None = None,
    subtext_control: ft.Control | None = None,
    on_click: Any | None = None,
    content: ft.Control | None = None,  # Support custom content
) -> ft.Container:
    """Create a premium matte-finish card with rounded rectangle shape.

    Supports either standard value/subtext layout OR custom content.
    Features: gradient background, hover animation, accent bar, glow shadow.
    """
    # Accent bar at top (separate from content to avoid clipping)
    accent_bar = ft.Container(
        height=2,  # Thinner bar
        bgcolor=accent_color if accent_color else "#38BDF8",
        border_radius=ft.border_radius.only(top_left=14, top_right=14),
        margin=ft.margin.only(left=-20, right=-20, top=-20, bottom=8),
    )

    header = ft.Row(
        [
            ft.Text(
                (title.upper() if title else ""),
                style=ft.TextStyle(
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color="#94A3B8",
                    letter_spacing=1.0,
                ),
            ),
            ft.Icon(icon, size=20, color=accent_color) if icon else ft.Container(),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    if content:
        # Custom content mode (for complex cards like Health/Disk)
        card_inner = ft.Column(
            [
                accent_bar,
                header,
                ft.Container(height=12),
                ft.Container(content=content),
            ],
            spacing=0,
        )
    else:
        # Standard metric mode
        card_inner = ft.Column(
            [
                accent_bar,
                header,
                ft.Container(height=12),
                value_control if value_control else ft.Container(),
                subtext_control if subtext_control else ft.Container(),
            ],
            spacing=0,
        )

    glow_color = accent_color if accent_color else "#38BDF8"

    container = ft.Container(
        content=card_inner,
        bgcolor="#1E293B",
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=["#1E293B", "#0F172A"],
        ),
        border=ft.border.all(
            1, "#334155"
        ),  # Uniform border (keeps border_radius working)
        border_radius=16,
        padding=20,
        expand=True,
        animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT_CUBIC),
        on_click=on_click,
        ink=True if on_click else False,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=16,
            color=ft.Colors.with_opacity(0.15, glow_color),
            offset=ft.Offset(0, 4),
        ),
    )

    def on_hover(e):
        e.control.scale = 1.02 if e.data == "true" else 1.0
        safe_update_control(e.control)

    container.on_hover = on_hover
    return container


def ActivityItem(
    title: str,
    subtitle: str,
    icon: str,
    color: str,
    timestamp: str | None = None,
) -> ft.Container:
    """Styled activity list item with premium feel."""
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon, color=color, size=18),
                    width=36,
                    height=36,
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.1, color),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    [
                        ft.Text(
                            title,
                            size=13,
                            weight=ft.FontWeight.W_500,  # Slightly lighter
                            color="#E2E8F0",  # Lighter slate
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Row(
                            [
                                ft.Text(subtitle, size=11, color="#94A3B8"),
                                ft.Text("•", size=11, color="#475569"),
                                ft.Text(timestamp or "", size=11, color="#64748B"),
                            ],
                            spacing=4,
                        )
                        if timestamp
                        else ft.Text(subtitle, size=11, color="#94A3B8"),
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            spacing=12,
        ),
        padding=ft.padding.symmetric(vertical=8, horizontal=4),
        border=ft.border.only(bottom=ft.BorderSide(1, "#1E293B")),
    )


def HealthGauge(value: float) -> ft.Stack:
    """Circular health gauge using SVG representation - Compact Version."""
    import base64

    # Compact gauge for better fit in top row
    size = 80  # Reduced from 100 for row alignment
    stroke = 7  # Proportional stroke
    radius = (size - stroke) / 2
    circumference = 2 * 3.14159 * radius
    offset = circumference - (value / 100) * circumference

    color = "#10B981" if value > 70 else "#F59E0B" if value > 30 else "#EF4444"

    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
        <circle cx="{size / 2}" cy="{size / 2}" r="{radius}" fill="none" stroke="#1E293B" stroke-width="{stroke}" />
        <circle cx="{size / 2}" cy="{size / 2}" r="{radius}" fill="none" stroke="{color}" stroke-width="{stroke}"
            stroke-dasharray="{circumference}" stroke-dashoffset="{offset}" stroke-linecap="round"
            transform="rotate(-90 {size / 2} {size / 2})" />
    </svg>
    """
    svg_base64 = base64.b64encode(svg.encode()).decode()

    return ft.Stack(
        [
            ft.Image(
                src=f"data:image/svg+xml;base64,{svg_base64}", width=size, height=size
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            f"{int(value)}",
                            size=18,  # Smaller for 80px gauge
                            weight=ft.FontWeight.BOLD,
                            color="#F1F5F9",
                        ),
                        ft.Text(
                            "HEALTH",
                            size=8,
                            weight=ft.FontWeight.W_700,
                            color="#64748B",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=-1,
                ),
                width=size,
                height=size,
                alignment=ft.Alignment(0, 0),
            ),
        ],
        width=size,
        height=size,
    )


def HealthGaugeWithTooltip(
    value: float,
    tooltip: str = "Health = 100 - (CPU×0.4 + Mem×0.4) - (20 if disconnected)",
) -> ft.Container:
    """Circular health gauge with explanatory tooltip.

    Args:
        value: Health percentage (0-100)
        tooltip: Tooltip message explaining the health calculation

    Returns:
        ft.Container wrapping the HealthGauge with tooltip
    """
    # In Flet 0.80.0, tooltip is a property on Container, not a wrapper
    gauge = HealthGauge(value)
    return ft.Container(
        content=gauge,
        tooltip=tooltip,
    )


def DiskUsageBar(
    used: int = 0,
    total: int = 0,
    percent: float = 0.0,
    formatted_used: str = "0 GB",
    formatted_total: str = "0 GB",
    color_hex: str = "#F472B6",  # Pink accent
) -> ft.Container:
    """Compact disk usage display with progress bar.

    Args:
        used: Used bytes
        total: Total bytes
        percent: Usage percentage (0-100)
        formatted_used: Human-readable used string
        formatted_total: Human-readable total string
        color_hex: Accent color for the progress bar

    Returns:
        ft.Container with disk usage visualization
    """
    # Determine color based on usage percentage
    if percent >= 90:
        bar_color = "#EF4444"  # Red - critical
    elif percent >= 75:
        bar_color = "#F59E0B"  # Amber - warning
    else:
        bar_color = color_hex  # Default pink

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "DISK USAGE",
                            size=10,
                            weight=ft.FontWeight.W_600,
                            color="#94A3B8",  # Slate-400
                        ),
                        ft.Text(
                            f"{percent:.0f}%",
                            size=20,
                            weight=ft.FontWeight.W_700,
                            color="#F1F5F9",  # Slate-100
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=8),
                # Progress bar container
                ft.Container(
                    content=ft.Stack(
                        [
                            # Background bar
                            ft.Container(
                                width=None,
                                height=8,
                                border_radius=4,
                                bgcolor="#334155",  # Slate-700
                                expand=True,
                            ),
                            # Foreground bar
                            ft.Container(
                                width=f"{min(percent, 100)}%",
                                height=8,
                                border_radius=4,
                                bgcolor=bar_color,
                            ),
                        ],
                    ),
                    expand=True,
                    height=8,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    border_radius=4,
                ),
                ft.Container(height=4),
                ft.Text(
                    f"{formatted_used} / {formatted_total}",
                    size=11,
                    color="#64748B",  # Slate-500
                ),
            ],
            spacing=0,
        ),
        bgcolor="#1E293B",  # Slate-800 - matte background
        border=ft.border.all(1, "#334155"),  # Slate-700
        border_radius=16,  # Rounded corners (consistent with matte cards)
        padding=16,
        expand=True,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=12,
            color=ft.Colors.with_opacity(0.2, color_hex),  # Colored glow
            offset=ft.Offset(0, 3),
        ),
    )
