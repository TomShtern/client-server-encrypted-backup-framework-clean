#!/usr/bin/env python3
"""
Integration test helpers for FletV2 views.

- FakePage: minimal Page-like object to satisfy views that open dialogs, use overlay, and run tasks
- find_control: recursive control tree search utilities
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Optional, Type, Awaitable, Coroutine

import flet as ft


class FakePage:
    """A minimal Flet Page stub for headless integration tests."""

    def __init__(self) -> None:
        self.overlay: list[Any] = []
        self.snack_bar: Optional[ft.SnackBar] = None
        self.last_opened_dialog: Optional[ft.AlertDialog] = None

    # API used by views
    def open(self, dialog: ft.AlertDialog) -> None:
        self.last_opened_dialog = dialog
        dialog.open = True

    def close(self, dialog: ft.AlertDialog) -> None:
        dialog.open = False

    def update(self) -> None:  # no-op
        return None

    def run_task(self, fn_or_coro: Callable[..., Any] | Awaitable[Any] | Coroutine[Any, Any, Any], *args: Any, **kwargs: Any) -> None:
        """Execute a function with args or a coroutine synchronously for tests."""
        try:
            if asyncio.iscoroutine(fn_or_coro):
                asyncio.run(fn_or_coro)  # type: ignore[arg-type]
            elif callable(fn_or_coro):
                result = fn_or_coro(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    asyncio.run(result)
        except RuntimeError:
            # If there's an event loop already running (e.g., in some environments), use a new loop
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                if callable(fn_or_coro):
                    result = fn_or_coro(*args, **kwargs)
                    if asyncio.iscoroutine(result):
                        loop.run_until_complete(result)
                else:
                    loop.run_until_complete(fn_or_coro)  # type: ignore[arg-type]
            finally:
                loop.close()


def find_control_by_type(root: Any, type_cls: Type[Any]) -> Optional[Any]:
    """Depth-first search for the first control instance of the given type."""
    try:
        if isinstance(root, type_cls):
            return root
    except Exception:
        pass

    # Explore common child properties on Flet controls
    for attr in ("content", "controls"):
        child = getattr(root, attr, None)
        if child is None:
            continue

        if isinstance(child, list):
            for c in child:
                found = find_control_by_type(c, type_cls)
                if found is not None:
                    return found
        else:
            found = find_control_by_type(child, type_cls)
            if found is not None:
                return found

    return None


def count_rows_in_datatable(table: ft.DataTable) -> int:
    try:
        return len(table.rows)
    except Exception:
        return 0


def trigger_first_popup_item_with_text(root: Any, text: str) -> bool:
    """Find the first PopupMenuButton and activate the item by visible text.

    Returns True if an item was found and its handler invoked.
    """
    btn = find_control_by_type(root, ft.PopupMenuButton)
    if btn is None:
        return False
    items = getattr(btn, "items", []) or []
    for it in items:
        try:
            if getattr(it, "text", None) == text and getattr(it, "on_click", None):
                # Invoke handler with a dummy event (handlers in code ignore the event)
                it.on_click(None)
                return True
        except Exception:
            continue
    return False


def confirm_dialog_action(page: FakePage, action_text: str = "Delete") -> bool:
    """Click an action button in the last opened dialog by its text (e.g., 'Delete')."""
    dlg = getattr(page, "last_opened_dialog", None)
    if dlg is None:
        return False
    actions = getattr(dlg, "actions", []) or []
    for act in actions:
        try:
            # Buttons may be created with text positional arg (Flet sets .text attribute)
            if isinstance(act, (ft.FilledButton, ft.TextButton)) and getattr(act, "text", None) == action_text:
                if getattr(act, "on_click", None):
                    act.on_click(None)
                    return True
        except Exception:
            continue
    return False
