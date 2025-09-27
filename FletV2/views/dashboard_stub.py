#!/usr/bin/env python3
"""Minimal stub dashboard view used when full dashboard fails to load.

This keeps the UI responsive and surfaces an explicit diagnostic panel so the
user knows the primary dashboard module encountered a problem.
"""
from __future__ import annotations
import os
import sys
from contextlib import suppress
from typing import Any
import flet as ft

# Ensure Shared UTF-8 side effects (mirrors pattern elsewhere) - safe no-op if missing
with suppress(Exception):  # pragma: no cover - defensive
    import Shared.utils.utf8_solution as _  # noqa: F401


def create_dashboard_stub(page: ft.Page | None = None) -> ft.Control:
    """Return a very small, static dashboard placeholder.

    Parameters
    ----------
    page: Optional ft.Page. Only used to show a one-time SnackBar if available.

    Returns
    -------
    ft.Control
        A container with diagnostic info instructing how to view logs.
    """
    diag = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.DASHBOARD, color=ft.Colors.PRIMARY, size=32),
                        ft.Text("Dashboard Stub Active", size=24, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=12,
                ),
                ft.Text(
                    "The full dashboard failed to load. This lightweight stub is shown so the app remains usable.",
                    size=14,
                ),
                ft.Text(
                    "Check application logs for the original exception. Once fixed, reload the application.",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Divider(height=24),
                ft.Text("Quick Tips:", weight=ft.FontWeight.BOLD, size=14),
                ft.Column(
                    [
                        ft.Text("1. Look for 'Error during view creation for dashboard' in logs."),
                        ft.Text("2. Verify 'create_dashboard_view' returns a 2 or 3 tuple as expected."),
                        ft.Text("3. Ensure no long blocking operations occur at import time."),
                        ft.Text("4. Temporarily reduce heavy queries or network calls in the dashboard."),
                    ],
                    spacing=4,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
        ),
        padding=24,
        expand=True,
    )

    # Optional one-time notification
    try:  # pragma: no cover - best effort
        if page and hasattr(page, "overlay"):
            sb = ft.SnackBar(
                content=ft.Text("Loaded dashboard stub (see logs)"),
                bgcolor=ft.Colors.AMBER,
                duration=4000,
            )
            page.overlay.append(sb)
            sb.open = True
            page.update()
    except Exception:
        pass

    return diag
    return diag
