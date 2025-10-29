#!/usr/bin/env python3
"""
Legacy FilterChip polyfill for Flet versions without native FilterChip support.

This was used in FletV2 before Flet 0.28.3 stable FilterChip support.
Moved to archive on 2025-10-28 as part of framework harmony consolidation.

NOTE: Flet 0.28.3 has native ft.FilterChip - use that instead.
This polyfill is only kept for reference/rollback purposes.
"""

from __future__ import annotations

import contextlib
from typing import Any, Callable

import flet as ft
from typing_extensions import cast


class FilterChip(ft.Container):  # sourcery skip: remove-unnecessary-cast, remove-unnecessary-try-except
    """Custom FilterChip implementation for Flet versions without native support."""

    def __init__(
        self,
        label: str = "",
        selected: bool = False,
        on_selected: Callable[[ft.ControlEvent], None] | None = None,
        **kwargs: Any,
    ) -> None:
        self.label = label
        self.selected = selected
        self.on_selected = on_selected
        self._button = ft.ElevatedButton(
            text=label,
            on_click=self._handle_click,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)),
        )
        super().__init__(
            content=self._button,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
            **kwargs,
        )
        self._refresh_style()

    def _handle_click(self, e: ft.ControlEvent) -> None:
        with contextlib.suppress(Exception):
            if callable(self.on_selected):
                ev = type("Evt", (), {"control": self})()
                self.on_selected(ev)

    def _refresh_style(self) -> None:
        with contextlib.suppress(Exception):
            if self.selected:
                self._button.bgcolor = ft.Colors.PRIMARY
                self._button.color = ft.Colors.ON_PRIMARY
            else:
                self._button.bgcolor = None
                self._button.color = None
            self._button.update()

    def update(self, *args: Any, **kwargs: Any) -> None:
        self._refresh_style()
        try:
            super().update(*args, **kwargs)
        except Exception:
            with contextlib.suppress(Exception):
                self._button.update()


# Usage: ft.FilterChip = cast(Any, FilterChip)  # type: ignore[attr-defined]
print("WARNING: This is legacy FilterChip polyfill. Use native ft.FilterChip in Flet 0.28.3+")