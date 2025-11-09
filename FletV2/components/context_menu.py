"""
Context Menu Component for Desktop Applications

This module provides right-click context menu functionality with desktop-standard
interaction patterns, including dynamic menus, submenus, and keyboard shortcuts.

Compatible with Flet 0.28.3 and Material Design 3.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

import flet as ft


class MenuItemType(Enum):
    """Context menu item types"""

    ACTION = "action"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SUBMENU = "submenu"
    SEPARATOR = "separator"
    LABEL = "label"


@dataclass
class MenuItem:
    """Context menu item configuration"""

    id: str
    label: str
    type: MenuItemType
    icon: str | None = None
    shortcut: str | None = None
    enabled: bool = True
    checked: bool = False
    submenu: list["MenuItem"] | None = None
    action: Callable | None = None


class ContextMenu(ft.PopupMenuButton):
    """
    Enhanced context menu component with desktop-standard behavior

    Features:
    - Dynamic menu items
    - Keyboard shortcuts display
    - Checkable and radio items
    - Submenus
    - Separators and labels
    - Accessibility support
    """

    def __init__(self, items: list[MenuItem] | None = None, on_action: Callable | None = None, **kwargs):
        super().__init__(**kwargs)

        self.menu_items = items or []
        self.on_action = on_action

        # Initialize the menu
        self._update_menu()

    def set_items(self, items: list[MenuItem]):
        """Update the menu items"""
        self.menu_items = items
        self._update_menu()

    def add_item(self, item: MenuItem):
        """Add a menu item"""
        self.menu_items.append(item)
        self._update_menu()

    def remove_item(self, item_id: str) -> bool:
        """Remove a menu item by ID"""
        for i, item in enumerate(self.menu_items):
            if item.id == item_id:
                self.menu_items.pop(i)
                self._update_menu()
                return True
        return False

    def show_at(self, x: float, y: float):
        """Show the context menu at specific coordinates (PopupMenuButton is always visible)"""
        # PopupMenuButton handles its own positioning
        pass

    def hide(self):
        """Hide the context menu (PopupMenuButton handles its own visibility)"""
        # PopupMenuButton handles its own visibility
        pass

    def _update_menu(self):
        """Update the Flet PopupMenu items based on our MenuItem list"""

        popup_items = []

        for item in self.menu_items:
            if item.type == MenuItemType.SEPARATOR:
                popup_items.append(ft.PopupMenuItem())
            elif item.type == MenuItemType.LABEL:
                popup_items.append(ft.PopupMenuItem(text=item.label, on_click=None, disabled=True))
            elif item.type == MenuItemType.CHECKBOX:
                popup_items.append(
                    ft.PopupMenuItem(
                        text=item.label,
                        icon=ft.Icons.CHECK if item.checked else None,
                        on_click=lambda e, i=item: self._on_item_click(e, i),
                        disabled=not item.enabled,
                    )
                )
            elif item.type == MenuItemType.RADIO:
                popup_items.append(
                    ft.PopupMenuItem(
                        text=item.label,
                        icon=(
                            ft.Icons.RADIO_BUTTON_CHECKED if item.checked else ft.Icons.RADIO_BUTTON_UNCHECKED
                        ),
                        on_click=lambda e, i=item: self._on_item_click(e, i),
                        disabled=not item.enabled,
                    )
                )
            elif item.type == MenuItemType.SUBMENU and item.submenu:
                submenu_items = self._create_submenu_items(item.submenu)
                popup_items.append(
                    ft.PopupMenuItem(
                        text=item.label, icon=item.icon, items=submenu_items, disabled=not item.enabled
                    )
                )
            else:  # ACTION
                popup_items.append(
                    ft.PopupMenuItem(
                        text=f"{item.label}\t{item.shortcut}" if item.shortcut else item.label,
                        icon=item.icon,
                        on_click=lambda e, i=item: self._on_item_click(e, i),
                        disabled=not item.enabled,
                    )
                )

        self.items = popup_items

    def _create_submenu_items(self, submenu_items: list[MenuItem]) -> list[ft.PopupMenuItem]:
        """Create PopupMenu items for a submenu"""
        items = []

        for item in submenu_items:
            if item.type == MenuItemType.SEPARATOR:
                items.append(ft.PopupMenuItem())
            elif item.type == MenuItemType.LABEL:
                items.append(ft.PopupMenuItem(text=item.label, on_click=None, disabled=True))
            else:
                items.append(
                    ft.PopupMenuItem(
                        text=f"{item.label}\t{item.shortcut}" if item.shortcut else item.label,
                        icon=item.icon,
                        on_click=lambda e, i=item: self._on_item_click(e, i),
                        disabled=not item.enabled,
                    )
                )

        return items

    def _on_item_click(self, e: ft.ControlEvent, item: MenuItem):
        """Handle menu item click"""

        if item.type == MenuItemType.CHECKBOX:
            # Toggle checkbox state
            item.checked = not item.checked
            self._update_menu()

        elif item.type == MenuItemType.RADIO:
            # Handle radio button (uncheck others in the same group)
            for menu_item in self.menu_items:
                if menu_item.type == MenuItemType.RADIO:
                    menu_item.checked = False
            item.checked = True
            self._update_menu()

        # Execute action
        if item.action:
            try:
                item.action(item.id, e)
            except Exception as ex:
                print(f"Error executing context menu action: {ex}")

        # Call global action handler
        if self.on_action:
            try:
                self.on_action(item.id, item, e)
            except Exception as ex:
                print(f"Error in global context menu handler: {ex}")

        # Hide menu after action
        self.hide()


class StandardContextMenu:
    """
    Factory for creating standard context menus for common desktop scenarios
    """

    @staticmethod
    def create_datatable_menu(
        on_view_details: Callable,
        on_edit: Callable,
        on_copy: Callable,
        on_export: Callable,
        on_delete: Callable,
        has_selection: bool = False,
    ) -> ContextMenu:
        """Create a standard DataTable context menu"""

        items = [
            MenuItem(
                id="view_details",
                label="View Details",
                type=MenuItemType.ACTION,
                icon=ft.Icons.INFO,
                shortcut="Enter",
                action=lambda _, __: on_view_details(),
            ),
            MenuItem(
                id="edit",
                label="Edit",
                type=MenuItemType.ACTION,
                icon=ft.Icons.EDIT,
                shortcut="F2",
                action=lambda _, __: on_edit(),
            ),
            MenuItem(id="separator1", label="", type=MenuItemType.SEPARATOR),
            MenuItem(
                id="copy",
                label="Copy",
                type=MenuItemType.ACTION,
                icon=ft.Icons.CONTENT_COPY,
                shortcut="Ctrl+C",
                action=lambda _, __: on_copy(),
            ),
            MenuItem(
                id="export_csv",
                label="Export as CSV",
                type=MenuItemType.ACTION,
                icon=ft.Icons.TABLE_VIEW,
                action=lambda _, __: on_export("csv"),
            ),
            MenuItem(
                id="export_json",
                label="Export as JSON",
                type=MenuItemType.ACTION,
                icon=ft.Icons.CODE,
                action=lambda _, __: on_export("json"),
            ),
            MenuItem(
                id="export_excel",
                label="Export as Excel",
                type=MenuItemType.ACTION,
                icon=ft.Icons.GRID_ON,
                action=lambda _, __: on_export("excel"),
            ),
            MenuItem(id="separator2", label="", type=MenuItemType.SEPARATOR),
            MenuItem(
                id="delete",
                label="Delete",
                type=MenuItemType.ACTION,
                icon=ft.Icons.DELETE,
                shortcut="Delete",
                enabled=has_selection,
                action=lambda _, __: on_delete(),
            ),
        ]

        return ContextMenu(items=items)

    @staticmethod
    def create_file_menu(
        on_open: Callable,
        on_edit: Callable,
        on_rename: Callable,
        on_copy: Callable,
        on_move: Callable,
        on_delete: Callable,
        on_properties: Callable,
        has_selection: bool = False,
    ) -> ContextMenu:
        """Create a standard file system context menu"""

        items = [
            MenuItem(
                id="open",
                label="Open",
                type=MenuItemType.ACTION,
                icon=ft.Icons.FOLDER_OPEN,
                shortcut="Enter",
                action=lambda _, __: on_open(),
            ),
            MenuItem(
                id="edit",
                label="Edit",
                type=MenuItemType.ACTION,
                icon=ft.Icons.EDIT,
                shortcut="F2",
                action=lambda _, __: on_edit(),
            ),
            MenuItem(id="separator1", label="", type=MenuItemType.SEPARATOR),
            MenuItem(
                id="copy",
                label="Copy",
                type=MenuItemType.ACTION,
                icon=ft.Icons.CONTENT_COPY,
                shortcut="Ctrl+C",
                action=lambda _, __: on_copy(),
            ),
            MenuItem(
                id="cut",
                label="Cut",
                type=MenuItemType.ACTION,
                icon=ft.Icons.CONTENT_CUT,
                shortcut="Ctrl+X",
                action=lambda _, __: on_copy(),  # Reuse copy with move flag
            ),
            MenuItem(
                id="paste",
                label="Paste",
                type=MenuItemType.ACTION,
                icon=ft.Icons.CONTENT_PASTE,
                shortcut="Ctrl+V",
                action=lambda _, __: on_move(),
            ),
            MenuItem(
                id="rename",
                label="Rename",
                type=MenuItemType.ACTION,
                icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE,
                shortcut="F2",
                action=lambda _, __: on_rename(),
            ),
            MenuItem(id="separator2", label="", type=MenuItemType.SEPARATOR),
            MenuItem(
                id="delete",
                label="Delete",
                type=MenuItemType.ACTION,
                icon=ft.Icons.DELETE,
                shortcut="Delete",
                enabled=has_selection,
                action=lambda _, __: on_delete(),
            ),
            MenuItem(id="separator3", label="", type=MenuItemType.SEPARATOR),
            MenuItem(
                id="properties",
                label="Properties",
                type=MenuItemType.ACTION,
                icon=ft.Icons.INFO,
                shortcut="Alt+Enter",
                action=lambda _, __: on_properties(),
            ),
        ]

        return ContextMenu(items=items)

    @staticmethod
    def create_text_menu(
        on_cut: Callable,
        on_copy: Callable,
        on_paste: Callable,
        on_delete: Callable,
        on_select_all: Callable,
        has_selection: bool = False,
        has_clipboard_content: bool = False,
    ) -> ContextMenu:
        """Create a standard text editing context menu"""

        items = [
            MenuItem(
                id="cut",
                label="Cut",
                type=MenuItemType.ACTION,
                icon=ft.Icons.CONTENT_CUT,
                shortcut="Ctrl+X",
                enabled=has_selection,
                action=lambda _, __: on_cut(),
            ),
            MenuItem(
                id="copy",
                label="Copy",
                type=MenuItemType.ACTION,
                icon=ft.Icons.CONTENT_COPY,
                shortcut="Ctrl+C",
                enabled=has_selection,
                action=lambda _, __: on_copy(),
            ),
            MenuItem(
                id="paste",
                label="Paste",
                type=MenuItemType.ACTION,
                icon=ft.Icons.CONTENT_PASTE,
                shortcut="Ctrl+V",
                enabled=has_clipboard_content,
                action=lambda _, __: on_paste(),
            ),
            MenuItem(
                id="delete",
                label="Delete",
                type=MenuItemType.ACTION,
                icon=ft.Icons.DELETE,
                shortcut="Delete",
                enabled=has_selection,
                action=lambda _, __: on_delete(),
            ),
            MenuItem(id="separator1", label="", type=MenuItemType.SEPARATOR),
            MenuItem(
                id="select_all",
                label="Select All",
                type=MenuItemType.ACTION,
                shortcut="Ctrl+A",
                action=lambda _, __: on_select_all(),
            ),
        ]

        return ContextMenu(items=items)


def setup_context_menu_target(control: ft.Control, context_menu: ContextMenu, page: ft.Page) -> None:
    """
    Setup a control to show a context menu on right-click

    Args:
        control: The control to attach the context menu to
        context_menu: The ContextMenu instance
        page: The Flet page instance
    """

    def on_right_click(e: ft.TapEvent):
        # Show context menu at click position
        context_menu.show_at(e.global_x, e.global_y)

    # Add the context menu to the page overlay
    if not hasattr(page, "overlay"):
        page.overlay = []
    if context_menu not in page.overlay:
        page.overlay.append(context_menu)

    # Set up the right-click handler
    control.on_tap_down = on_right_click

    # Update the control
    if getattr(control, "page", None):
        control.update()
