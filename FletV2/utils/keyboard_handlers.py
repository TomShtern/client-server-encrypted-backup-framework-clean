"""
Keyboard Handlers for Desktop Navigation

This module provides keyboard event handling utilities for desktop applications,
including navigation shortcuts, modifier key detection, and event routing.

Compatible with Flet 0.28.3 and desktop Windows 11 applications.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

import flet as ft


class ModifierKey(Enum):
    """Modifier key enumeration"""
    CTRL = "ctrl"
    SHIFT = "shift"
    ALT = "alt"
    META = "meta"  # Windows key


class KeyCode:
    """String-based key codes compatible with Flet 0.28.3 keyboard events."""

    ARROW_DOWN = "arrow down"
    ARROW_UP = "arrow up"
    ARROW_LEFT = "arrow left"
    ARROW_RIGHT = "arrow right"
    HOME = "home"
    END = "end"
    PAGE_DOWN = "page down"
    PAGE_UP = "page up"
    ENTER = "enter"
    DELETE = "delete"
    ESCAPE = "escape"
    TAB = "tab"

    A = "a"
    C = "c"
    D = "d"
    E = "e"
    F = "f"
    L = "l"
    N = "n"
    Q = "q"
    S = "s"
    V = "v"
    X = "x"
    Z = "z"

    COMMA = "comma"

    DIGIT_1 = "1"
    DIGIT_2 = "2"
    DIGIT_3 = "3"
    DIGIT_4 = "4"
    DIGIT_5 = "5"
    DIGIT_6 = "6"
    DIGIT_7 = "7"

    F1 = "f1"
    F5 = "f5"


KEY_NORMALIZATION_MAP: dict[str, str] = {
    "arrowdown": KeyCode.ARROW_DOWN,
    "arrow_down": KeyCode.ARROW_DOWN,
    "arrow up": KeyCode.ARROW_UP,
    "arrowup": KeyCode.ARROW_UP,
    "arrow_left": KeyCode.ARROW_LEFT,
    "arrowleft": KeyCode.ARROW_LEFT,
    "arrow_right": KeyCode.ARROW_RIGHT,
    "arrowright": KeyCode.ARROW_RIGHT,
    "pagedown": KeyCode.PAGE_DOWN,
    "page_down": KeyCode.PAGE_DOWN,
    "pageup": KeyCode.PAGE_UP,
    "page_up": KeyCode.PAGE_UP,
    "return": KeyCode.ENTER,
    "enter": KeyCode.ENTER,
    "esc": KeyCode.ESCAPE,
    "escape": KeyCode.ESCAPE,
    "del": KeyCode.DELETE,
    "delete": KeyCode.DELETE,
    "bksp": "backspace",
    ",": KeyCode.COMMA,
    "comma": KeyCode.COMMA,
}


DISPLAY_KEY_MAP: dict[str, str] = {
    KeyCode.ARROW_DOWN: "↓",
    KeyCode.ARROW_UP: "↑",
    KeyCode.ARROW_LEFT: "←",
    KeyCode.ARROW_RIGHT: "→",
    KeyCode.PAGE_DOWN: "Page Down",
    KeyCode.PAGE_UP: "Page Up",
    KeyCode.HOME: "Home",
    KeyCode.END: "End",
    KeyCode.ENTER: "Enter",
    KeyCode.DELETE: "Delete",
    KeyCode.ESCAPE: "Esc",
    KeyCode.TAB: "Tab",
    KeyCode.COMMA: ",",
}


def normalize_key(key: str | None) -> str:
    """Normalize a keyboard key into a lowercase comparable string."""

    if key is None:
        return ""

    normalized = key.strip().lower().replace("_", " ")
    normalized = KEY_NORMALIZATION_MAP.get(normalized, normalized)

    if normalized.startswith("digit") and normalized[5:].isdigit():
        return normalized[5:]
    if normalized.startswith("numpad") and normalized[6:].isdigit():
        return normalized[6:]

    if len(normalized) == 1:
        return normalized

    if normalized.startswith("f") and normalized[1:].isdigit():
        return normalized

    return normalized


def key_display_name(key: str | None) -> str:
    """Return a human-readable label for a normalized key."""

    normalized = normalize_key(key)
    if not normalized:
        return ""

    if normalized in DISPLAY_KEY_MAP:
        return DISPLAY_KEY_MAP[normalized]

    if len(normalized) == 1:
        return normalized.upper()

    if normalized.isdigit():
        return normalized

    if normalized.startswith("f") and normalized[1:].isdigit():
        return normalized.upper()

    return normalized.title()


@dataclass
class KeyboardShortcut:
    """Keyboard shortcut configuration"""
    key: str
    modifiers: set[ModifierKey]
    description: str
    action: Callable[[ft.KeyboardEvent], Any] | None
    enabled: bool = True
    display_key: str | None = None


class KeyboardHandler:
    """
    Centralized keyboard event handler for desktop applications

    Provides:
    - Global keyboard shortcut registration
    - Modifier key detection
    - Event routing to active components
    - Conflict resolution between shortcuts
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.shortcuts: dict[str, KeyboardShortcut] = {}
        self.active_handlers: list[Callable] = []
        self.enabled = True

        # Register global keyboard event handler
        self.page.on_keyboard_event = self._on_keyboard_event

    def register_shortcut(
        self,
        key: str,
        modifiers: set[ModifierKey] | None = None,
        description: str = "",
        action: Callable[[ft.KeyboardEvent], Any] | None = None,
        enabled: bool = True
    ) -> str:
        """
        Register a global keyboard shortcut

        Returns a unique shortcut ID that can be used to unregister the shortcut
        """

        if modifiers is None:
            modifiers = set()

        normalized_key = normalize_key(key)
        if not normalized_key:
            raise ValueError("Keyboard shortcut key must be a non-empty string")

        # Generate unique shortcut ID
        shortcut_id = self._generate_shortcut_id(normalized_key, modifiers)

        # Create shortcut configuration
        shortcut = KeyboardShortcut(
            key=normalized_key,
            modifiers=modifiers,
            description=description,
            action=action,
            enabled=enabled,
            display_key=key_display_name(key)
        )

        # Store the shortcut
        self.shortcuts[shortcut_id] = shortcut

        return shortcut_id

    def unregister_shortcut(self, shortcut_id: str) -> bool:
        """Unregister a keyboard shortcut by ID"""
        if shortcut_id in self.shortcuts:
            del self.shortcuts[shortcut_id]
            return True
        return False

    def enable_shortcut(self, shortcut_id: str, enabled: bool = True):
        """Enable or disable a keyboard shortcut"""
        if shortcut_id in self.shortcuts:
            self.shortcuts[shortcut_id].enabled = enabled

    def add_active_handler(self, handler: Callable):
        """Add an active keyboard handler (e.g., for DataTable navigation)"""
        if handler not in self.active_handlers:
            self.active_handlers.append(handler)

    def remove_active_handler(self, handler: Callable):
        """Remove an active keyboard handler"""
        if handler in self.active_handlers:
            self.active_handlers.remove(handler)

    def set_enabled(self, enabled: bool):
        """Enable or disable all keyboard handling"""
        self.enabled = enabled

    def _on_keyboard_event(self, e: ft.KeyboardEvent):
        """Handle keyboard events and route to appropriate handlers"""

        if not self.enabled:
            return

        # First, try active handlers (component-specific navigation)
        for handler in self.active_handlers:
            try:
                if handler(e):
                    # Event was handled by the component
                    return
            except Exception as ex:
                print(f"Error in keyboard handler: {ex}")

        # Then, try global shortcuts
        matching_shortcut_id = self._find_matching_shortcut(e)
        if matching_shortcut_id:
            shortcut = self.shortcuts[matching_shortcut_id]
            if shortcut.enabled and shortcut.action:
                try:
                    shortcut.action(e)
                    return
                except Exception as ex:
                    print(f"Error executing keyboard shortcut action: {ex}")

    def _find_matching_shortcut(self, e: ft.KeyboardEvent) -> str | None:
        """Find a shortcut that matches the keyboard event"""

        for shortcut_id, shortcut in self.shortcuts.items():
            if not shortcut.enabled:
                continue

            # Check if the key matches
            if normalize_key(e.key) != shortcut.key:
                continue

            # Check if all required modifiers are present
            required_modifiers = shortcut.modifiers
            event_modifiers = self._get_event_modifiers(e)

            if required_modifiers == event_modifiers:
                return shortcut_id

        return None

    def _get_event_modifiers(self, e: ft.KeyboardEvent) -> set[ModifierKey]:
        """Extract modifier keys from a keyboard event"""

        modifiers = set()

        if e.ctrl or e.meta:
            modifiers.add(ModifierKey.CTRL)
        if e.shift:
            modifiers.add(ModifierKey.SHIFT)
        if e.alt:
            modifiers.add(ModifierKey.ALT)

        return modifiers

    def _generate_shortcut_id(self, key: str, modifiers: set[ModifierKey]) -> str:
        """Generate a unique shortcut ID from key and modifiers"""

        parts = []

        # Add modifiers in consistent order
        for modifier in sorted([m.value for m in modifiers]):
            parts.append(modifier)

        # Add the key
        parts.append(key)

        return "+".join(parts)

    def get_shortcuts_help(self) -> list[dict[str, str]]:
        """Get a list of all registered shortcuts for help display"""

        help_list = []

        for shortcut_id, shortcut in self.shortcuts.items():
            if shortcut.enabled and shortcut.description:
                # Format the shortcut key combination
                key_parts = []

                for modifier in sorted(shortcut.modifiers, key=lambda m: m.value):
                    if modifier == ModifierKey.CTRL:
                        key_parts.append("Ctrl")
                    elif modifier == ModifierKey.SHIFT:
                        key_parts.append("Shift")
                    elif modifier == ModifierKey.ALT:
                        key_parts.append("Alt")
                    elif modifier == ModifierKey.META:
                        key_parts.append("Win")

                # Add the key name
                key_parts.append(self._format_key_name(shortcut.key, shortcut.display_key))

                help_list.append({
                    "shortcut": "+".join(key_parts),
                    "description": shortcut.description,
                    "id": shortcut_id
                })

        return sorted(help_list, key=lambda x: x["shortcut"])

    def _format_key_name(self, key: str, display_key: str | None = None) -> str:
        """Format a key name for display"""

        if display_key:
            return display_key

        return key_display_name(key)


class NavigationKeyboardHandler:
    """
    Specialized keyboard handler for navigation-focused components like DataTable

    Provides desktop-standard navigation patterns:
    - Arrow key navigation
    - Modifier key combinations
    - Page navigation
    - Action keys (Enter, Escape, Delete)
    """

    def __init__(self):
        self.callbacks: dict[str, Callable] = {}

    def register_callback(self, action: str, callback: Callable):
        """Register a callback for a specific navigation action"""
        self.callbacks[action] = callback

    def handle_event(self, e: ft.KeyboardEvent) -> bool:
        """
        Handle a keyboard event for navigation

        Returns True if the event was handled, False otherwise
        """

        action = None

        event_key = normalize_key(e.key)

        # Map keyboard events to navigation actions
        if event_key == KeyCode.ARROW_DOWN:
            action = "navigate_down"
        elif event_key == KeyCode.ARROW_UP:
            action = "navigate_up"
        elif event_key == KeyCode.ARROW_LEFT:
            action = "navigate_left"
        elif event_key == KeyCode.ARROW_RIGHT:
            action = "navigate_right"
        elif event_key == KeyCode.HOME:
            action = "navigate_to_start"
        elif event_key == KeyCode.END:
            action = "navigate_to_end"
        elif event_key == KeyCode.PAGE_DOWN:
            action = "navigate_page_down"
        elif event_key == KeyCode.PAGE_UP:
            action = "navigate_page_up"
        elif event_key == KeyCode.ENTER:
            action = "activate"
        elif event_key == KeyCode.DELETE:
            action = "delete"
        elif event_key == KeyCode.ESCAPE:
            action = "escape"
        elif event_key == KeyCode.TAB:
            action = "navigate_back" if e.shift else "navigate_forward"
        elif event_key == KeyCode.A and (e.ctrl or e.meta):
            action = "select_all"
        elif event_key == KeyCode.C and (e.ctrl or e.meta):
            action = "copy"
        elif event_key == KeyCode.V and (e.ctrl or e.meta):
            action = "paste"
        elif event_key == KeyCode.X and (e.ctrl or e.meta):
            action = "cut"
        elif event_key == KeyCode.Z and (e.ctrl or e.meta):
            action = "redo" if e.shift else "undo"

        # Execute the action if we have a callback
        if action and action in self.callbacks:
            try:
                self.callbacks[action](e)
                return True
            except Exception as ex:
                print(f"Error executing navigation callback '{action}': {ex}")

        return False


def create_standard_shortcuts(handler: KeyboardHandler) -> dict[str, str]:
    """
    Create standard application shortcuts and return their IDs

    Returns a dictionary mapping shortcut names to their IDs
    """

    shortcut_ids = {}

    # Common application shortcuts
    shortcut_ids["copy"] = handler.register_shortcut(
        key=KeyCode.C,
        modifiers={ModifierKey.CTRL},
        description="Copy selection",
        action=lambda e: print("Copy action")
    )

    shortcut_ids["paste"] = handler.register_shortcut(
        key=KeyCode.V,
        modifiers={ModifierKey.CTRL},
        description="Paste",
        action=lambda e: print("Paste action")
    )

    shortcut_ids["undo"] = handler.register_shortcut(
        key=KeyCode.Z,
        modifiers={ModifierKey.CTRL},
        description="Undo",
        action=lambda e: print("Undo action")
    )

    shortcut_ids["redo"] = handler.register_shortcut(
        key=KeyCode.Z,
        modifiers={ModifierKey.CTRL, ModifierKey.SHIFT},
        description="Redo",
        action=lambda e: print("Redo action")
    )

    shortcut_ids["select_all"] = handler.register_shortcut(
        key=KeyCode.A,
        modifiers={ModifierKey.CTRL},
        description="Select all",
        action=lambda e: print("Select all action")
    )

    shortcut_ids["save"] = handler.register_shortcut(
        key=KeyCode.S,
        modifiers={ModifierKey.CTRL},
        description="Save",
        action=lambda e: print("Save action")
    )

    shortcut_ids["find"] = handler.register_shortcut(
        key=KeyCode.F,
        modifiers={ModifierKey.CTRL},
        description="Find/Search",
        action=lambda e: print("Find action")
    )

    # Navigation shortcuts
    shortcut_ids["refresh"] = handler.register_shortcut(
        key=KeyCode.F5,
        description="Refresh current view",
        action=lambda e: print("Refresh action")
    )

    return shortcut_ids


def create_datatable_shortcuts(handler: KeyboardHandler, datatable) -> dict[str, str]:
    """
    Create DataTable-specific shortcuts and return their IDs

    Args:
        handler: KeyboardHandler instance
        datatable: EnhancedDataTable instance

    Returns:
        Dictionary mapping shortcut names to their IDs
    """

    shortcut_ids = {}

    # DataTable navigation shortcuts
    shortcut_ids["delete_selected"] = handler.register_shortcut(
        key=KeyCode.DELETE,
        description="Delete selected rows",
        action=lambda e: datatable._bulk_delete(None) if datatable.selected_rows else None
    )

    shortcut_ids["clear_selection"] = handler.register_shortcut(
        key=KeyCode.ESCAPE,
        description="Clear selection",
        action=lambda e: datatable._clear_selection(None)
    )

    return shortcut_ids
