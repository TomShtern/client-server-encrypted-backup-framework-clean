#!/usr/bin/env python3
"""
Modern loading components for Flet 0.28.3 lazy loading patterns.

Provides clean, skeleton loading states with subtle animations and
progressive enhancement patterns.
"""

from __future__ import annotations

from typing import Any

import flet as ft

try:  # pragma: no cover - UTF-8 bootstrap required by project
    pass
except Exception:  # pragma: no cover - allow running in isolation
    pass


class SkeletonCard(ft.Container):
    """A modern skeleton loader card with subtle shimmer effect."""

    def __init__(
        self,
        width: float | None = None,
        height: float = 120,
        has_title: bool = True,
        has_subtitle: bool = True,
        has_value: bool = True,
        border_radius: float = 12,
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.bgcolor = ft.Colors.with_opacity(0.08, ft.Colors.GREY_300)
        self.border_radius = ft.border_radius.all(border_radius)
        self.padding = ft.padding.all(16)

        # Build skeleton content
        skeleton_content = []

        if has_title:
            skeleton_content.append(
                ft.Container(
                    width=80,
                    height=16,
                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.GREY_400),
                    border_radius=ft.border_radius.all(4),
                )
            )

        if has_value:
            skeleton_content.append(
                ft.Container(
                    width=60,
                    height=24,
                    margin=ft.margin.only(top=8),
                    bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.GREY_500),
                    border_radius=ft.border_radius.all(4),
                )
            )

        if has_subtitle:
            skeleton_content.append(
                ft.Container(
                    width=100,
                    height=12,
                    margin=ft.margin.only(top=8),
                    bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.GREY_400),
                    border_radius=ft.border_radius.all(4),
                )
            )

        self.content = ft.Column(
            skeleton_content,
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
        )


class LoadingStateCard(ft.Container):
    """A loading state card with ProgressRing and status text."""

    def __init__(
        self,
        title: str,
        subtitle: str = "Loading...",
        show_progress: bool = True,
        color: ft.Color = ft.Colors.BLUE,
    ):
        super().__init__()
        self.bgcolor = ft.Colors.with_opacity(0.05, color)
        self.border_radius = ft.border_radius.all(16)
        self.padding = ft.padding.all(20)

        content_elements = []

        if show_progress:
            content_elements.append(
                ft.Row(
                    [
                        ft.ProgressRing(
                            width=24,
                            height=24,
                            stroke_width=2,
                            color=color,
                        ),
                        ft.Container(width=16),
                        ft.Text(
                            subtitle,
                            size=14,
                            color=ft.Colors.with_opacity(0.7, color),
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )

        content_elements.append(
            ft.Text(
                title,
                size=20,
                weight=ft.FontWeight.W_600,
                color=color,
            )
        )

        self.content = ft.Column(
            content_elements,
            spacing=12,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )


class ErrorStateCard(ft.Container):
    """An error state card with retry functionality."""

    def __init__(
        self,
        title: str,
        error_message: str,
        on_retry: Any = None,
        color: ft.Color = ft.Colors.RED,
    ):
        super().__init__()
        self.bgcolor = ft.Colors.with_opacity(0.05, color)
        self.border_radius = ft.border_radius.all(16)
        self.padding = ft.padding.all(20)

        content_elements = [
            ft.Row(
                [
                    ft.Icon(
                        ft.Icons.ERROR_OUTLINE,
                        size=24,
                        color=color,
                    ),
                    ft.Container(width=12),
                    ft.Text(
                        title,
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color=color,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Text(
                error_message,
                size=14,
                color=ft.Colors.with_opacity(0.7, color),
            ),
        ]

        if on_retry:
            content_elements.append(
                ft.Container(
                    margin=ft.margin.only(top=12),
                    content=ft.ElevatedButton(
                        "Retry",
                        icon=ft.Icons.REFRESH,
                        on_click=on_retry,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.1, color),
                            color=color,
                            elevation=1,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                )
            )

        self.content = ft.Column(
            content_elements,
            spacing=12,
            alignment=ft.MainAxisAlignment.START,
        )


class MetricLoadingCard(ft.Container):
    """A specialized loading card for metrics with skeleton and progress state."""

    def __init__(
        self,
        title: str,
        icon: str,
        color: ft.Color,
        width: float | None = None,
        height: float = 120,
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.bgcolor = ft.Colors.with_opacity(0.02, color)
        self.border = ft.border.all(1, ft.Colors.with_opacity(0.1, color))
        self.border_radius = ft.border_radius.all(12)
        self.padding = ft.padding.all(16)

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(icon, size=20, color=ft.Colors.with_opacity(0.5, color)),
                        ft.Container(width=8),
                        ft.Text(
                            title,
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=ft.Colors.with_opacity(0.7, color),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Container(
                    margin=ft.margin.only(top=16),
                    content=ft.ProgressRing(
                        width=16,
                        height=16,
                        stroke_width=2,
                        color=color,
                    ),
                    alignment=ft.alignment.center_left,
                ),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )


def create_dashboard_skeleton_layout() -> ft.Column:
    """Create the initial skeleton layout for the dashboard."""

    # Create skeleton metric cards
    skeleton_metrics = ft.ResponsiveRow([
        ft.Container(
            content=MetricLoadingCard("Clients", ft.Icons.PEOPLE_OUTLINED, ft.Colors.BLUE),
            col={"xs": 12, "sm": 6, "md": 3},
        ),
        ft.Container(
            content=MetricLoadingCard("Active", ft.Icons.CAST_CONNECTED, ft.Colors.TEAL),
            col={"xs": 12, "sm": 6, "md": 3},
        ),
        ft.Container(
            content=MetricLoadingCard("Files", ft.Icons.INSERT_DRIVE_FILE_OUTLINED, ft.Colors.PURPLE),
            col={"xs": 12, "sm": 6, "md": 3},
        ),
        ft.Container(
            content=MetricLoadingCard("Uptime", ft.Icons.SCHEDULE, ft.Colors.GREEN),
            col={"xs": 12, "sm": 6, "md": 3},
        ),
    ], spacing=12, run_spacing=12)

    # Create skeleton status section
    skeleton_status = ft.Container(
        content=ft.Column([
            ft.ResponsiveRow([
                ft.Container(
                    content=LoadingStateCard("Server Status", "Initializing..."),
                    col={"xs": 12, "md": 4},
                ),
                ft.Container(
                    content=LoadingStateCard("Performance", "Collecting metrics..."),
                    col={"xs": 12, "md": 4},
                ),
                ft.Container(
                    content=LoadingStateCard("Recent Activity", "Loading events..."),
                    col={"xs": 12, "md": 4},
                ),
            ], spacing=12, run_spacing=12),
        ]),
        margin=ft.margin.only(top=24),
    )

    return ft.Column(
        [
            skeleton_metrics,
            skeleton_status,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
