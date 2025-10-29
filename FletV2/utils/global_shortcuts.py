"""
Global Keyboard Shortcuts System for Desktop Applications

This module provides a comprehensive global keyboard shortcuts system for desktop
applications, including view navigation, common actions, and context-aware shortcuts.

Compatible with Flet 0.28.3 and desktop Windows 11 applications.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

import flet as ft

from .keyboard_handlers import (
    KeyCode,
    KeyboardHandler,
    ModifierKey,
    key_display_name,
    normalize_key,
)


class ShortcutCategory(Enum):
    """Categories of keyboard shortcuts"""
    NAVIGATION = "navigation"
    EDITING = "editing"
    VIEW = "view"
    ACTIONS = "actions"
    HELP = "help"


@dataclass
class GlobalShortcut:
    """Global shortcut configuration"""
    id: str
    key: str
    modifiers: set[ModifierKey]
    action: Callable[[ft.KeyboardEvent], Any] | None
    description: str
    category: ShortcutCategory
    context: str | None = None  # Optional context for context-aware shortcuts
    enabled: bool = True
    display_key: str | None = None


class GlobalShortcutManager:
    """
    Centralized global shortcut management system for desktop applications

    Features:
    - Global application shortcuts (Ctrl+N, Ctrl+S, etc.)
    - View navigation shortcuts (Ctrl+1-7)
    - Context-aware shortcuts
    - Shortcut conflict detection and resolution
    - Help system integration
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.keyboard_handler = KeyboardHandler(page)
        self.shortcuts: dict[str, GlobalShortcut] = {}
        self.context_handlers: dict[str, list[Callable]] = {}
        self.current_context = "global"

        # Register global keyboard event handler
        self._setup_global_handler()

    def register_shortcut(
        self,
        shortcut_id: str,
        key: str,
        modifiers: set[ModifierKey] | None = None,
        action: Callable[[ft.KeyboardEvent], Any] | None = None,
        description: str = "",
        category: ShortcutCategory = ShortcutCategory.ACTIONS,
        context: str | None = None,
        enabled: bool = True
    ):
        """
        Register a global shortcut

        Args:
            shortcut_id: Unique identifier for the shortcut
            key: String key identifier (see KeyCode constants or keyboard event values)
            modifiers: Set of modifier keys required
            action: Function to call when shortcut is activated
            description: Human-readable description
            category: Category of the shortcut
            context: Optional context for context-aware shortcuts
            enabled: Whether the shortcut is initially enabled
        """

        if modifiers is None:
            modifiers = set()

        normalized_key = normalize_key(key)
        if not normalized_key:
            raise ValueError("Shortcut key must be a non-empty string")

        # Create shortcut configuration
        shortcut = GlobalShortcut(
            id=shortcut_id,
            key=normalized_key,
            modifiers=modifiers,
            action=action,
            description=description,
            category=category,
            context=context,
            enabled=enabled,
            display_key=key_display_name(key)
        )

        # Store the shortcut
        self.shortcuts[shortcut_id] = shortcut

        # Register with keyboard handler
        return self.keyboard_handler.register_shortcut(
            key=normalized_key,
            modifiers=modifiers,
            description=description,
            action=lambda e: self._handle_shortcut_activation(shortcut_id, e),
            enabled=enabled
        )

    def unregister_shortcut(self, shortcut_id: str) -> bool:
        """Unregister a global shortcut"""
        if shortcut_id in self.shortcuts:
            del self.shortcuts[shortcut_id]
            return True
        return False

    def set_context(self, context: str):
        """Set the current context for context-aware shortcuts"""
        self.current_context = context

    def enable_shortcut(self, shortcut_id: str, enabled: bool = True):
        """Enable or disable a shortcut"""
        if shortcut_id in self.shortcuts:
            self.shortcuts[shortcut_id].enabled = enabled

    def register_context_handler(self, context: str, handler: Callable):
        """Register a handler for a specific context"""
        if context not in self.context_handlers:
            self.context_handlers[context] = []
        self.context_handlers[context].append(handler)

    def get_shortcuts_help(self, category: ShortcutCategory | None = None) -> list[dict[str, str]]:
        """Get formatted help for shortcuts, optionally filtered by category"""

        help_list = []

        for _shortcut_id, shortcut in self.shortcuts.items():
            # Filter by category if specified
            if category and shortcut.category != category:
                continue

            # Filter by context if shortcut has context requirement
            if shortcut.context and shortcut.context != self.current_context:
                continue

            if shortcut.enabled and shortcut.description:
                # Format the shortcut key combination
                key_parts: list[str] = []
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
                    "category": shortcut.category.value,
                    "context": shortcut.context or "global"
                })

        return sorted(help_list, key=lambda x: (x["category"], x["shortcut"]))

    def _setup_global_handler(self):
        """Setup the global keyboard event handler"""
        # The keyboard handler is already set up to handle events
        pass

    def _handle_shortcut_activation(self, shortcut_id: str, e: ft.KeyboardEvent):
        """Handle activation of a shortcut"""

        if shortcut_id not in self.shortcuts:
            return

        shortcut = self.shortcuts[shortcut_id]

        if not shortcut.enabled:
            return

        # Check context requirements
        if shortcut.context and shortcut.context != self.current_context:
            return

        try:
            # Execute the action
            if shortcut.action:
                shortcut.action(e)

        except Exception as ex:
            print(f"Error executing shortcut '{shortcut_id}': {ex}")

    def _format_key_name(self, key: str, display_key: str | None = None) -> str:
        """Format a key name for display"""

        if display_key:
            return display_key

        return key_display_name(key)

    def create_shortcuts_dialog(self) -> ft.AlertDialog:
        """Create a dialog showing all available shortcuts"""

        # Get shortcuts organized by category
        nav_shortcuts = self.get_shortcuts_help(ShortcutCategory.NAVIGATION)
        edit_shortcuts = self.get_shortcuts_help(ShortcutCategory.EDITING)
        view_shortcuts = self.get_shortcuts_help(ShortcutCategory.VIEW)
        action_shortcuts = self.get_shortcuts_help(ShortcutCategory.ACTIONS)

        tabs = ft.Tabs(
            scrollable=True,
            tabs=[
                ft.Tab(
                    text="Navigation",
                    content=ft.Column(
                        [ft.Text("Navigation Shortcuts", weight=ft.FontWeight.BOLD, size=16)] +
                        [
                            ft.Row([
                                ft.Text(s["shortcut"], width=150, weight=ft.FontWeight.W_500),
                                ft.Text(s["description"], expand=True)
                            ])
                            for s in nav_shortcuts
                        ] if nav_shortcuts else [ft.Text("No navigation shortcuts available")],
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO
                    )
                ),
                ft.Tab(
                    text="Editing",
                    content=ft.Column(
                        [ft.Text("Editing Shortcuts", weight=ft.FontWeight.BOLD, size=16)] +
                        [
                            ft.Row([
                                ft.Text(s["shortcut"], width=150, weight=ft.FontWeight.W_500),
                                ft.Text(s["description"], expand=True)
                            ])
                            for s in edit_shortcuts
                        ] if edit_shortcuts else [ft.Text("No editing shortcuts available")],
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO
                    )
                ),
                ft.Tab(
                    text="View",
                    content=ft.Column(
                        [ft.Text("View Shortcuts", weight=ft.FontWeight.BOLD, size=16)] +
                        [
                            ft.Row([
                                ft.Text(s["shortcut"], width=150, weight=ft.FontWeight.W_500),
                                ft.Text(s["description"], expand=True)
                            ])
                            for s in view_shortcuts
                        ] if view_shortcuts else [ft.Text("No view shortcuts available")],
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO
                    )
                ),
                ft.Tab(
                    text="Actions",
                    content=ft.Column(
                        [ft.Text("Action Shortcuts", weight=ft.FontWeight.BOLD, size=16)] +
                        [
                            ft.Row([
                                ft.Text(s["shortcut"], width=150, weight=ft.FontWeight.W_500),
                                ft.Text(s["description"], expand=True)
                            ])
                            for s in action_shortcuts
                        ] if action_shortcuts else [ft.Text("No action shortcuts available")],
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO
                    )
                ),
            ],
            expand=True,
        )

        return ft.AlertDialog(
            title=ft.Text("Keyboard Shortcuts"),
            content=ft.Container(
                content=tabs,
                width=600,
                height=500
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self._close_shortcuts_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _close_shortcuts_dialog(self):
        """Close the shortcuts dialog"""
        if hasattr(self.page, 'dialog') and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def show_shortcuts_dialog(self):
        """Show the keyboard shortcuts dialog"""
        dialog = self.create_shortcuts_dialog()
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()


def create_standard_application_shortcuts(
    shortcut_manager: GlobalShortcutManager,
    view_navigator: Callable[[str], None] | None = None
) -> dict[str, str]:
    """
    Create standard application shortcuts

    Args:
        shortcut_manager: GlobalShortcutManager instance
        view_navigator: Function to navigate to different views (receives view name)

    Returns:
        Dictionary mapping shortcut names to their IDs
    """

    shortcut_ids: dict[str, str] = {
        # Application shortcuts
        "quit": shortcut_manager.register_shortcut(
            shortcut_id="app_quit",
            key=KeyCode.Q,
            modifiers={ModifierKey.CTRL},
            action=lambda e: print("Quit application"),
            description="Quit application",
            category=ShortcutCategory.ACTIONS
        ),
        # Help shortcuts
        "help": shortcut_manager.register_shortcut(
            shortcut_id="help_shortcuts",
            key=KeyCode.F1,
            action=lambda e: shortcut_manager.show_shortcuts_dialog(),
            description="Show keyboard shortcuts",
            category=ShortcutCategory.HELP
        ),
    }

    # View shortcuts (if navigator provided)
    if view_navigator:
        shortcut_ids["dashboard"] = shortcut_manager.register_shortcut(
            shortcut_id="view_dashboard",
            key=KeyCode.D,
            modifiers={ModifierKey.CTRL},
            action=lambda e: view_navigator("dashboard"),
            description="Go to Dashboard",
            category=ShortcutCategory.NAVIGATION
        )

        shortcut_ids["database"] = shortcut_manager.register_shortcut(
            shortcut_id="view_database",
            key=KeyCode.L,
            modifiers={ModifierKey.CTRL},
            action=lambda e: view_navigator("database"),
            description="Go to Database",
            category=ShortcutCategory.NAVIGATION
        )

        shortcut_ids["clients"] = shortcut_manager.register_shortcut(
            shortcut_id="view_clients",
            key=KeyCode.C,
            modifiers={ModifierKey.CTRL, ModifierKey.SHIFT},
            action=lambda e: view_navigator("clients"),
            description="Go to Clients",
            category=ShortcutCategory.NAVIGATION
        )

        shortcut_ids["files"] = shortcut_manager.register_shortcut(
            shortcut_id="view_files",
            key=KeyCode.F,
            modifiers={ModifierKey.CTRL, ModifierKey.SHIFT},
            action=lambda e: view_navigator("files"),
            description="Go to Files",
            category=ShortcutCategory.NAVIGATION
        )

        shortcut_ids["logs"] = shortcut_manager.register_shortcut(
            shortcut_id="view_logs",
            key=KeyCode.L,
            modifiers={ModifierKey.CTRL, ModifierKey.SHIFT},
            action=lambda e: view_navigator("logs"),
            description="Go to Logs",
            category=ShortcutCategory.NAVIGATION
        )

        shortcut_ids["settings"] = shortcut_manager.register_shortcut(
            shortcut_id="view_settings",
            key=KeyCode.COMMA,
            modifiers={ModifierKey.CTRL},
            action=lambda e: view_navigator("settings"),
            description="Go to Settings",
            category=ShortcutCategory.NAVIGATION
        )

        # Numeric view navigation
        view_mapping = {
            KeyCode.DIGIT_1: "dashboard",
            KeyCode.DIGIT_2: "clients",
            KeyCode.DIGIT_3: "files",
            KeyCode.DIGIT_4: "database",
            KeyCode.DIGIT_5: "logs",
            KeyCode.DIGIT_6: "analytics",
            KeyCode.DIGIT_7: "settings"
        }

        for key, view_name in view_mapping.items():
            shortcut_ids[f"view_{view_name}_numeric"] = shortcut_manager.register_shortcut(
                shortcut_id=f"view_{view_name}_numeric",
                key=key,
                modifiers={ModifierKey.CTRL},
                action=lambda e, v=view_name: view_navigator(v),
                description=f"Go to {view_name.title()}",
                category=ShortcutCategory.NAVIGATION
            )

    # Refresh shortcut
    shortcut_ids["refresh"] = shortcut_manager.register_shortcut(
        shortcut_id="view_refresh",
        key=KeyCode.F5,
        action=lambda e: print("Refresh current view"),
        description="Refresh current view",
        category=ShortcutCategory.VIEW
    )

    # Global search
    shortcut_ids["search"] = shortcut_manager.register_shortcut(
        shortcut_id="global_search",
        key=KeyCode.F,
        modifiers={ModifierKey.CTRL},
        action=lambda e: print("Activate global search"),
        description="Global search",
        category=ShortcutCategory.VIEW
    )

    return shortcut_ids


def create_view_specific_shortcuts(
    shortcut_manager: GlobalShortcutManager,
    view_context: str,
    view_actions: dict[str, Callable]
) -> dict[str, str]:
    """
    Create shortcuts specific to a particular view

    Args:
        shortcut_manager: GlobalShortcutManager instance
        view_context: Context name (e.g., "database", "files")
        view_actions: Dictionary mapping action names to functions

    Returns:
        Dictionary mapping shortcut names to their IDs
    """

    shortcut_ids = {}

    # Common view-specific shortcuts
    if "new" in view_actions:
        shortcut_ids["new"] = shortcut_manager.register_shortcut(
            shortcut_id=f"{view_context}_new",
            key=KeyCode.N,
            modifiers={ModifierKey.CTRL},
            action=view_actions["new"],
            description="Create new item",
            category=ShortcutCategory.ACTIONS,
            context=view_context
        )

    if "edit" in view_actions:
        shortcut_ids["edit"] = shortcut_manager.register_shortcut(
            shortcut_id=f"{view_context}_edit",
            key=KeyCode.E,
            modifiers={ModifierKey.CTRL},
            action=view_actions["edit"],
            description="Edit selected item",
            category=ShortcutCategory.EDITING,
            context=view_context
        )

    if "delete" in view_actions:
        shortcut_ids["delete"] = shortcut_manager.register_shortcut(
            shortcut_id=f"{view_context}_delete",
            key=KeyCode.DELETE,
            action=view_actions["delete"],
            description="Delete selected item",
            category=ShortcutCategory.EDITING,
            context=view_context
        )

    if "export" in view_actions:
        shortcut_ids["export"] = shortcut_manager.register_shortcut(
            shortcut_id=f"{view_context}_export",
            key=KeyCode.E,
            modifiers={ModifierKey.CTRL, ModifierKey.SHIFT},
            action=view_actions["export"],
            description="Export data",
            category=ShortcutCategory.ACTIONS,
            context=view_context
        )

    return shortcut_ids
