"""
Breadcrumb Navigation Component for Desktop Applications

This module provides a breadcrumb navigation component for desktop applications,
showing the current location context and allowing quick navigation to parent levels.

Compatible with Flet 0.28.3 and Material Design 3.
"""

from collections.abc import Callable
from typing import Any, Optional

import flet as ft


class BreadcrumbItem:
    """Represents a single breadcrumb item"""

    def __init__(
        self,
        label: str,
        action: Callable | None = None,
        icon: str | None = None,
        is_current: bool = False,
        tooltip: str | None = None
    ):
        self.label = label
        self.action = action
        self.icon = icon
        self.is_current = is_current
        self.tooltip = tooltip or label


class BreadcrumbNavigation(ft.Row):
    """
    Breadcrumb navigation component for desktop applications

    Features:
    - Visual navigation hierarchy
    - Click navigation to parent levels
    - Search context display
    - View hierarchy display
    - Responsive design
    - Accessibility support
    """

    def __init__(
        self,
        items: list[BreadcrumbItem] | None = None,
        on_navigation: Callable[[str], None] | None = None,
        show_home: bool = True,
        separator: str = "/",
        max_items: int = 5,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.items = items or []
        self.on_navigation = on_navigation
        self.show_home = show_home
        self.separator = separator
        self.max_items = max_items

        # Initialize the breadcrumb
        self._update_breadcrumb()

    def set_items(self, items: list[BreadcrumbItem]):
        """Update the breadcrumb items"""
        self.items = items
        self._update_breadcrumb()

    def add_item(self, item: BreadcrumbItem):
        """Add a breadcrumb item"""
        self.items.append(item)
        self._update_breadcrumb()

    def clear_items(self):
        """Clear all breadcrumb items"""
        self.items = []
        self._update_breadcrumb()

    def navigate_to_root(self):
        """Navigate to the root level"""
        if self.items:
            self.items = [self.items[0]]
            self._update_breadcrumb()

    def set_search_context(self, search_text: str, filter_count: int = 0):
        """Set search context display"""
        if search_text:
            search_item = BreadcrumbItem(
                label=f"Search: {search_text}",
                icon=ft.Icons.SEARCH,
                is_current=True,
                tooltip=f"Current search: {search_text}"
            )
            self.set_items([search_item])

    def _update_breadcrumb(self):
        """Update the breadcrumb display"""

        self.controls = []
        display_items = self._get_display_items()

        # Add home item if enabled
        if self.show_home and (not display_items or display_items[0].label != "Home"):
            home_item = BreadcrumbItem(
                label="Home",
                icon=ft.Icons.HOME,
                action=lambda: self._navigate_to_item("home")
            )
            display_items.insert(0, home_item)

        # Create breadcrumb controls
        for i, item in enumerate(display_items):
            # Add separator (except for first item)
            if i > 0:
                separator_text = ft.Text(
                    self.separator,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    weight=ft.FontWeight.W_400
                )
                self.controls.append(
                    ft.Container(
                        content=separator_text,
                        margin=ft.margin.symmetric(horizontal=4)
                    )
                )

            # Create breadcrumb item
            if item.is_current:
                # Current item (not clickable)
                current_text = ft.Text(
                    item.label,
                    size=14,
                    color=ft.Colors.PRIMARY,
                    weight=ft.FontWeight.W_500
                )
                if item.icon:
                    icon_control = ft.Icon(
                        item.icon,
                        size=16,
                        color=ft.Colors.PRIMARY
                    )
                    item_control = ft.Row(
                        [icon_control, current_text],
                        spacing=4,
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                else:
                    item_control = current_text

                self.controls.append(item_control)

            else:
                # Navigable item (clickable)
                nav_button = ft.TextButton(
                    text=item.label,
                    icon=item.icon,
                    style=ft.ButtonStyle(
                        color=ft.Colors.PRIMARY,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        shape=ft.RoundedRectangleBorder(radius=4),
                        overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY)
                    ),
                    on_click=lambda _, item=item: self._navigate_to_item(item),
                    tooltip=item.tooltip
                )

                self.controls.append(nav_button)

        # Update the component only when attached to a page
        if getattr(self, "page", None):
            self.update()

    def _get_display_items(self) -> list[BreadcrumbItem]:
        """Get the items to display, handling overflow with ellipsis"""

        if len(self.items) <= self.max_items:
            return self.items.copy()

        # Too many items, show ellipsis
        result = []

        # Always show first item (root)
        if self.items:
            result.append(self.items[0])

        # Show ellipsis if needed
        if len(self.items) > self.max_items:
            ellipsis_item = BreadcrumbItem(
                label="...",
                tooltip=f"{len(self.items) - 2} more levels"
            )
            result.append(ellipsis_item)

        # Show last few items
        result.extend(self.items[-(self.max_items - 2):])

        return result

    def _navigate_to_item(self, item: BreadcrumbItem | str):
        """Navigate to a breadcrumb item"""

        if isinstance(item, str) and item == "home":
            # Special case for home
            if self.on_navigation:
                self.on_navigation("home")
            else:
                self.navigate_to_root()
            return

        if isinstance(item, BreadcrumbItem):
            if item.action:
                # Execute item-specific action
                item.action()
            elif self.on_navigation:
                # Use global navigation handler
                self.on_navigation(item.label)
        elif self.on_navigation and isinstance(item, str):
            # Handle string items
            self.on_navigation(item)
        else:
            # Default behavior: navigate to this level
            if isinstance(item, BreadcrumbItem):
                target_index = self.items.index(item)
            elif isinstance(item, str):
                # Find the breadcrumb item by label
                target_index = next((i for i, breadcrumb_item in enumerate(self.items)
                                       if isinstance(breadcrumb_item, BreadcrumbItem) and breadcrumb_item.label == item), -1)
            else:
                target_index = -1

            if target_index >= 0:
                self.items = self.items[:target_index + 1]
                self._update_breadcrumb()


class BreadcrumbFactory:
    """Factory for creating standard breadcrumb configurations"""

    @staticmethod
    def create_database_breadcrumb(
        table_name: str | None = None,
        record_id: str | None = None,
        on_navigate: Callable[[str], None] | None = None
    ) -> list[BreadcrumbItem]:
        """Create database navigation breadcrumb"""

        items = [
            BreadcrumbItem(
                label="Database",
                icon=ft.Icons.STORAGE,
                action=lambda: on_navigate("database") if on_navigate else None
            )
        ]

        if table_name:
            items.append(
                BreadcrumbItem(
                    label=table_name,
                    icon=ft.Icons.TABLE_VIEW,
                    action=lambda: on_navigate("table") if on_navigate else None
                )
            )

        if record_id:
            items.append(
                BreadcrumbItem(
                    label=f"Record {record_id}",
                    icon=ft.Icons.DESCRIPTION,
                    is_current=True
                )
            )

        return items

    @staticmethod
    def create_file_breadcrumb(
        folder_path: list[str],
        file_name: str | None = None,
        on_navigate: Callable[[str], None] | None = None
    ) -> list[BreadcrumbItem]:
        """Create file system navigation breadcrumb"""

        items = [
            BreadcrumbItem(
                label="Files",
                icon=ft.Icons.FOLDER,
                action=lambda: on_navigate("files_root") if on_navigate else None
            )
        ]

        # Add folder path
        for i, folder in enumerate(folder_path):
            if i == len(folder_path) - 1 and not file_name:
                # Last folder without file - current location
                items.append(
                    BreadcrumbItem(
                        label=folder,
                        icon=ft.Icons.FOLDER,
                        is_current=True
                    )
                )
            else:
                # Navigable folder
                items.append(
                    BreadcrumbItem(
                        label=folder,
                        icon=ft.Icons.FOLDER_OUTLINE,
                        action=lambda _, f=folder, idx=i: (
                    on_navigate(f"folder_{idx}") if on_navigate else None
                )
                    )
                )

        # Add file if provided
        if file_name:
            items.append(
                BreadcrumbItem(
                    label=file_name,
                    icon=ft.Icons.INSERT_DRIVE_FILE,
                    is_current=True
                )
            )

        return items

    @staticmethod
    def create_log_breadcrumb(
        log_level: str | None = None,
        search_term: str | None = None,
        date_range: str | None = None,
        on_navigate: Callable[[str], None] | None = None
    ) -> list[BreadcrumbItem]:
        """Create log navigation breadcrumb"""

        items = [
            BreadcrumbItem(
                label="Logs",
                icon=ft.Icons.ARTICLE,
                action=lambda: on_navigate("logs") if on_navigate else None
            )
        ]

        if log_level:
            items.append(
                BreadcrumbItem(
                    label=f"Level: {log_level.upper()}",
                    icon=ft.Icons.FILTER_ALT,
                    action=lambda: on_navigate("logs") if on_navigate else None
                )
            )

        if date_range:
            items.append(
                BreadcrumbItem(
                    label=date_range,
                    icon=ft.Icons.DATE_RANGE,
                    action=lambda: on_navigate("logs_filtered") if on_navigate else None
                )
            )

        if search_term:
            items.append(
                BreadcrumbItem(
                    label=f"Search: {search_term}",
                    icon=ft.Icons.SEARCH,
                    is_current=True
                )
            )

        return items

    @staticmethod
    def create_settings_breadcrumb(
        section: str | None = None,
        subsection: str | None = None,
        on_navigate: Callable[[str], None] | None = None
    ) -> list[BreadcrumbItem]:
        """Create settings navigation breadcrumb"""

        items = [
            BreadcrumbItem(
                label="Settings",
                icon=ft.Icons.SETTINGS,
                action=lambda: on_navigate("settings") if on_navigate else None
            )
        ]

        if section:
            items.append(
                BreadcrumbItem(
                    label=section.title(),
                    icon=ft.Icons.TUNE,
                    action=lambda: on_navigate("settings_section") if on_navigate else None
                )
            )

        if subsection:
            items.append(
                BreadcrumbItem(
                    label=subsection.title(),
                    icon=ft.Icons.TUNE,
                    is_current=True
                )
            )

        return items


def setup_breadcrumb_navigation(
    page: ft.Page,
    breadcrumb: BreadcrumbNavigation,
    navigation_handler: Callable[[str], None]
) -> None:
    """
    Setup breadcrumb navigation with proper event handling

    Args:
        page: Flet page instance
        breadcrumb: BreadcrumbNavigation instance
        navigation_handler: Function to handle navigation events
    """

    # Set up navigation callback
    breadcrumb.on_navigation = navigation_handler

    # Add breadcrumb to a container for proper styling
    breadcrumb_container = ft.Container(
        content=breadcrumb,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.SURFACE),
        border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
    )

    return breadcrumb_container

