"""
Global Keyboard Shortcuts System for Desktop Applications - Flet Native Edition

This module provides a comprehensive global keyboard shortcuts system using Flet 0.28.3's
NATIVE keyboard event handling (page.on_keyboard_event).

Compatible with Flet 0.28.3 and desktop Windows 11 applications.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

import flet as ft


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
    key: str  # Flet key name (e.g., "s", "f5", "delete")
    ctrl: bool = False
    shift: bool = False
    alt: bool = False
    meta: bool = False  # Windows key
    action: Callable[[ft.KeyboardEvent], Any] | None = None
    description: str = ""
    category: ShortcutCategory = ShortcutCategory.ACTIONS
    context: str | None = None
    enabled: bool = True


class GlobalShortcutManager:
    """
    Centralized global shortcut management using Flet's NATIVE keyboard events.

    Uses page.on_keyboard_event for zero-overhead keyboard handling.

    Features:
    - Global application shortcuts (Ctrl+N, Ctrl+S, etc.)
    - View navigation shortcuts (Ctrl+1-7)
    - Context-aware shortcuts
    - Help system integration
    - NATIVE Flet keyboard event handling (no custom wrapper needed!)
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.shortcuts: dict[str, GlobalShortcut] = {}
        self.current_context = "global"

        # Register NATIVE Flet keyboard event handler
        self.page.on_keyboard_event = self._handle_keyboard_event

    def register_shortcut(
        self,
        shortcut_id: str,
        key: str,
        ctrl: bool = False,
        shift: bool = False,
        alt: bool = False,
        meta: bool = False,
        action: Callable[[ft.KeyboardEvent], Any] | None = None,
        description: str = "",
        category: ShortcutCategory = ShortcutCategory.ACTIONS,
        context: str | None = None,
        enabled: bool = True
    ) -> str:
        """
        Register a global shortcut using Flet native key names.

        Args:
            shortcut_id: Unique identifier for the shortcut
            key: Flet key name (e.g., "s", "f5", "delete", "arrow down")
            ctrl: Whether Ctrl modifier is required
            shift: Whether Shift modifier is required
            alt: Whether Alt modifier is required
            meta: Whether Windows/Meta key is required
            action: Function to call when shortcut is activated
            description: Human-readable description
            category: Category of the shortcut
            context: Optional context for context-aware shortcuts
            enabled: Whether the shortcut is initially enabled

        Returns:
            The shortcut_id for reference
        """
        shortcut = GlobalShortcut(
            id=shortcut_id,
            key=key.lower(),  # Normalize to lowercase
            ctrl=ctrl,
            shift=shift,
            alt=alt,
            meta=meta,
            action=action,
            description=description,
            category=category,
            context=context,
            enabled=enabled
        )

        self.shortcuts[shortcut_id] = shortcut
        return shortcut_id

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

    def _handle_keyboard_event(self, e: ft.KeyboardEvent):
        """
        Handle keyboard events using Flet's NATIVE event system.

        Flet provides:
        - e.key: normalized key name
        - e.ctrl: Ctrl modifier state (built-in!)
        - e.shift: Shift modifier state (built-in!)
        - e.alt: Alt modifier state (built-in!)
        - e.meta: Meta/Windows key state (built-in!)
        """
        if not e.key:
            return

        key_lower = e.key.lower()

        # Find matching shortcuts
        for shortcut in self.shortcuts.values():
            if not shortcut.enabled:
                continue

            # Check context requirements
            if shortcut.context and shortcut.context != self.current_context:
                continue

            # Check if modifiers match (Flet provides these built-in!)
            if (shortcut.ctrl != e.ctrl or
                shortcut.shift != e.shift or
                shortcut.alt != e.alt or
                shortcut.meta != e.meta):
                continue

            # Check if key matches
            if shortcut.key != key_lower:
                continue

            # Execute the shortcut action
            try:
                if shortcut.action:
                    shortcut.action(e)
            except Exception as ex:
                print(f"Error executing shortcut '{shortcut.id}': {ex}")

            # Shortcut matched, stop processing
            return

    def get_shortcuts_help(self, category: ShortcutCategory | None = None) -> list[dict[str, str]]:
        """Get formatted help for shortcuts, optionally filtered by category"""
        help_list = []

        for shortcut in self.shortcuts.values():
            # Filter by category if specified
            if category and shortcut.category != category:
                continue

            # Filter by context if shortcut has context requirement
            if shortcut.context and shortcut.context != self.current_context:
                continue

            if shortcut.enabled and shortcut.description:
                # Format the shortcut key combination
                key_parts: list[str] = []
                if shortcut.ctrl:
                    key_parts.append("Ctrl")
                if shortcut.shift:
                    key_parts.append("Shift")
                if shortcut.alt:
                    key_parts.append("Alt")
                if shortcut.meta:
                    key_parts.append("Win")

                # Add the key name (capitalized for display)
                key_parts.append(shortcut.key.upper() if len(shortcut.key) == 1 else shortcut.key.title())

                help_list.append({
                    "shortcut": "+".join(key_parts),
                    "description": shortcut.description,
                    "category": shortcut.category.value,
                    "context": shortcut.context or "global"
                })

        return sorted(help_list, key=lambda x: (x["category"], x["shortcut"]))

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
    view_navigator: Callable[[str], None] | None = None,
    open_search_callback: Callable[[ft.KeyboardEvent | None], Any] | None = None,
    close_search_callback: Callable[[ft.KeyboardEvent | None], Any] | None = None,
) -> dict[str, str]:
    """
    Create standard application shortcuts using Flet native keyboard events.

    Args:
        shortcut_manager: GlobalShortcutManager instance
        view_navigator: Function to navigate to different views (receives view name)
        open_search_callback: Function to invoke for global search shortcuts
        close_search_callback: Function to invoke when closing global search (Esc)

    Returns:
        Dictionary mapping shortcut names to their IDs
    """
    shortcut_ids: dict[str, str] = {}

    # Application shortcuts
    shortcut_ids["quit"] = shortcut_manager.register_shortcut(
        shortcut_id="app_quit",
        key="q",
        ctrl=True,
        action=lambda e: print("Quit application"),
        description="Quit application",
        category=ShortcutCategory.ACTIONS
    )

    # Help shortcuts
    shortcut_ids["help"] = shortcut_manager.register_shortcut(
        shortcut_id="help_shortcuts",
        key="f1",
        action=lambda e: shortcut_manager.show_shortcuts_dialog(),
        description="Show keyboard shortcuts",
        category=ShortcutCategory.HELP
    )

    # View shortcuts (if navigator provided)
    if view_navigator:
        shortcut_ids["dashboard"] = shortcut_manager.register_shortcut(
            shortcut_id="view_dashboard",
            key="d",
            ctrl=True,
            action=lambda e: view_navigator("dashboard"),
            description="Go to Dashboard",
            category=ShortcutCategory.NAVIGATION
        )

        shortcut_ids["database"] = shortcut_manager.register_shortcut(
            shortcut_id="view_database",
            key="l",
            ctrl=True,
            action=lambda e: view_navigator("database"),
            description="Go to Database",
            category=ShortcutCategory.NAVIGATION
        )

        shortcut_ids["clients"] = shortcut_manager.register_shortcut(
            shortcut_id="view_clients",
            key="c",
            ctrl=True,
            shift=True,
            action=lambda e: view_navigator("clients"),
            description="Go to Clients",
            category=ShortcutCategory.NAVIGATION
        )

        shortcut_ids["files"] = shortcut_manager.register_shortcut(
            shortcut_id="view_files",
            key="f",
            ctrl=True,
            shift=True,
            action=lambda e: view_navigator("files"),
            description="Go to Files",
            category=ShortcutCategory.NAVIGATION
        )

        shortcut_ids["logs"] = shortcut_manager.register_shortcut(
            shortcut_id="view_logs",
            key="l",
            ctrl=True,
            shift=True,
            action=lambda e: view_navigator("logs"),
            description="Go to Logs",
            category=ShortcutCategory.NAVIGATION
        )

        shortcut_ids["settings"] = shortcut_manager.register_shortcut(
            shortcut_id="view_settings",
            key="comma",
            ctrl=True,
            action=lambda e: view_navigator("settings"),
            description="Go to Settings",
            category=ShortcutCategory.NAVIGATION
        )

        # Numeric view navigation (Ctrl+1 through Ctrl+7)
        view_mapping = {
            "1": "dashboard",
            "2": "clients",
            "3": "files",
            "4": "database",
            "5": "logs",
            "6": "analytics",
            "7": "settings"
        }

        for key, view_name in view_mapping.items():
            shortcut_ids[f"view_{view_name}_numeric"] = shortcut_manager.register_shortcut(
                shortcut_id=f"view_{view_name}_numeric",
                key=key,
                ctrl=True,
                action=lambda e, v=view_name: view_navigator(v),
                description=f"Go to {view_name.title()}",
                category=ShortcutCategory.NAVIGATION
            )

    # Refresh shortcut
    shortcut_ids["refresh"] = shortcut_manager.register_shortcut(
        shortcut_id="view_refresh",
        key="f5",
        action=lambda e: print("Refresh current view"),
        description="Refresh current view",
        category=ShortcutCategory.VIEW
    )

    # Global search
    if open_search_callback:
        shortcut_ids["search"] = shortcut_manager.register_shortcut(
            shortcut_id="global_search",
            key="f",
            ctrl=True,
            action=lambda e: open_search_callback(e),
            description="Open global search",
            category=ShortcutCategory.VIEW
        )

        shortcut_ids["search_alt"] = shortcut_manager.register_shortcut(
            shortcut_id="global_search_alt",
            key="k",
            ctrl=True,
            action=lambda e: open_search_callback(e),
            description="Open global search",
            category=ShortcutCategory.VIEW
        )
    else:
        shortcut_ids["search"] = shortcut_manager.register_shortcut(
            shortcut_id="global_search",
            key="f",
            ctrl=True,
            action=lambda e: print("Activate global search"),
            description="Global search",
            category=ShortcutCategory.VIEW
        )

    if close_search_callback:
        shortcut_ids["search_escape"] = shortcut_manager.register_shortcut(
            shortcut_id="global_search_escape",
            key="escape",
            action=lambda e: close_search_callback(e),
            description="Close global search",
            category=ShortcutCategory.VIEW
        )

    return shortcut_ids


def create_view_specific_shortcuts(
    shortcut_manager: GlobalShortcutManager,
    view_context: str,
    view_actions: dict[str, Callable]
) -> dict[str, str]:
    """
    Create shortcuts specific to a particular view using Flet native events.

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
            key="n",
            ctrl=True,
            action=view_actions["new"],
            description="Create new item",
            category=ShortcutCategory.ACTIONS,
            context=view_context
        )

    if "edit" in view_actions:
        shortcut_ids["edit"] = shortcut_manager.register_shortcut(
            shortcut_id=f"{view_context}_edit",
            key="e",
            ctrl=True,
            action=view_actions["edit"],
            description="Edit selected item",
            category=ShortcutCategory.EDITING,
            context=view_context
        )

    if "delete" in view_actions:
        shortcut_ids["delete"] = shortcut_manager.register_shortcut(
            shortcut_id=f"{view_context}_delete",
            key="delete",
            action=view_actions["delete"],
            description="Delete selected item",
            category=ShortcutCategory.EDITING,
            context=view_context
        )

    if "export" in view_actions:
        shortcut_ids["export"] = shortcut_manager.register_shortcut(
            shortcut_id=f"{view_context}_export",
            key="e",
            ctrl=True,
            shift=True,
            action=view_actions["export"],
            description="Export data",
            category=ShortcutCategory.ACTIONS,
            context=view_context
        )

    return shortcut_ids
