"""
Professional Global Search using Flet 0.28.3 Native SearchBar Component

This implementation follows the Flet Simplicity Principle:
- Uses ft.SearchBar (Material Design 3 native component)
- No custom Stack positioning (framework does it correctly)
- No layout shifts or positioning bugs
- Built-in dropdown view support

Based on official Flet 0.28.3 patterns and Material Design 3 guidelines.
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable

import flet as ft


class SearchCategory(Enum):
    """Search result categories"""
    CLIENTS = "clients"
    FILES = "files"
    DATABASE = "database"
    LOGS = "logs"
    SETTINGS = "settings"
    ALL = "all"


@dataclass
class SearchResult:
    """Represents a single search result"""
    id: str
    title: str
    description: str
    category: SearchCategory
    action: Callable
    icon: str | None = None
    metadata: dict[str, Any] | None = None


class ProfessionalGlobalSearch(ft.SearchBar):
    """
    Professional global search using Flet 0.28.3 native SearchBar.

    This is the CORRECT way to implement search in Flet:
    - Uses ft.SearchBar (not custom Stack positioning)
    - Built-in Material Design 3 styling
    - No layout shifts or positioning bugs
    - Flet framework handles all dropdown positioning

    Features:
    - Debounced search (300ms)
    - Async search with task cancellation
    - Category filtering
    - Keyboard navigation (Ctrl+F, Esc, arrows)
    - Result limiting (max 50)
    """

    def __init__(
        self,
        on_search: Callable[[str, SearchCategory], Awaitable[list[SearchResult]] | list[SearchResult]] | None = None,
        max_results: int = 50,
        **kwargs
    ):
        # Material Design 3 SearchBar configuration
        super().__init__(
            bar_hint_text="Search the platform (Ctrl+F)",
            view_hint_text="Type to search clients, files, database...",
            view_elevation=4,
            bar_bgcolor={
                ft.MaterialState.DEFAULT: ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
                ft.MaterialState.FOCUSED: ft.Colors.SURFACE,
            },
            bar_overlay_color={
                ft.MaterialState.DEFAULT: ft.Colors.with_opacity(0, ft.Colors.PRIMARY),
                ft.MaterialState.HOVERED: ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
            },
            bar_shadow_color=ft.Colors.with_opacity(0.24, ft.Colors.BLACK),
            bar_elevation=0,  # Flat when unfocused
            bar_border_side=ft.BorderSide(1, ft.Colors.with_opacity(0.14, ft.Colors.OUTLINE)),
            bar_padding=ft.padding.symmetric(horizontal=12, vertical=6),
            bar_text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_400),
            divider_color=ft.Colors.OUTLINE_VARIANT,
            controls=[],  # Start empty, populated on search
            on_change=self._on_search_change,
            on_submit=self._on_search_submit,
            **kwargs
        )

        self.on_search_callback = on_search
        self.max_results = max_results

        # State
        self.current_category = SearchCategory.ALL
        self.current_results: list[SearchResult] = []
        self._active_search_task: asyncio.Task | None = None
        self._debounce_delay = 0.3  # 300ms

        # Add category filter and keyboard shortcuts info to search bar
        self._build_search_header()

    def _build_search_header(self):
        """Build the search bar leading/trailing icons"""
        # Leading icon (search)
        self.bar_leading = ft.Icon(ft.Icons.SEARCH, size=20, color=ft.Colors.PRIMARY)

        # Trailing: category dropdown + keyboard shortcuts badge
        self.bar_trailing = [
            self._create_category_dropdown(),
            ft.Container(
                content=ft.Text("Ctrl+F", size=11, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT),
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                border_radius=4,
                bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.ON_SURFACE),
            )
        ]

    def _create_category_dropdown(self) -> ft.Dropdown:
        """Create category filter dropdown"""
        return ft.Dropdown(
            value=SearchCategory.ALL.value,
            options=[
                ft.dropdown.Option(key=cat.value, text=cat.value.capitalize())
                for cat in SearchCategory
            ],
            width=120,
            height=36,
            text_size=13,
            border_radius=8,
            border_color=ft.Colors.OUTLINE_VARIANT,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.SURFACE),
            on_change=self._on_category_change,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=4),
        )

    def _on_category_change(self, e: ft.ControlEvent):
        """Handle category filter change"""
        self.current_category = SearchCategory(e.control.value)
        # Re-run search with new category
        if self.value and len(self.value.strip()) >= 2:
            self._trigger_debounced_search(self.value)

    def _on_search_change(self, e: ft.ControlEvent):
        """Handle search input change with debouncing"""
        query = e.control.value.strip()

        if len(query) < 2:
            # Clear results if query too short
            self.controls = []
            self.update()
            return

        # Trigger debounced search
        self._trigger_debounced_search(query)

    def _on_search_submit(self, e: ft.ControlEvent):
        """Handle Enter key press in search"""
        # If there are results, select the first one
        if self.current_results:
            self._execute_result_action(self.current_results[0])

    def _trigger_debounced_search(self, query: str):
        """
        Debounce search input - only search after 300ms of no typing.
        Cancels previous search task if still running.
        """
        # Cancel previous search
        if self._active_search_task and not self._active_search_task.done():
            self._active_search_task.cancel()

        async def debounced_search():
            await asyncio.sleep(self._debounce_delay)
            await self._perform_search(query)

        self._active_search_task = asyncio.create_task(debounced_search())

    async def _perform_search(self, query: str):
        """
        Perform async search and update results.
        Calls the on_search callback provided during initialization.
        """
        if not self.on_search_callback:
            # No search provider, show placeholder
            self.controls = [
                ft.ListTile(
                    title=ft.Text("No search provider configured", size=13, italic=True),
                    disabled=True
                )
            ]
            self.update()
            return

        try:
            # Call search provider (can be sync or async)
            results = self.on_search_callback(query, self.current_category)
            if asyncio.iscoroutine(results):
                results = await results

            # Limit results
            results = results[:self.max_results]
            self.current_results = results

            # Build result tiles
            if results:
                self.controls = self._build_result_tiles(results)
            else:
                self.controls = [
                    ft.ListTile(
                        title=ft.Text(f"No results found for '{query}'", size=13, italic=True),
                        subtitle=ft.Text(f"Try searching in category: {self.current_category.value}", size=11),
                        disabled=True
                    )
                ]

            self.update()

        except asyncio.CancelledError:
            # Search was cancelled (user typed more), ignore
            pass
        except Exception as ex:
            print(f"Search error: {ex}")
            self.controls = [
                ft.ListTile(
                    title=ft.Text(f"Search error: {ex}", size=13, color=ft.Colors.ERROR),
                    disabled=True
                )
            ]
            self.update()

    def _build_result_tiles(self, results: list[SearchResult]) -> list[ft.Control]:
        """Build list tiles for search results"""
        tiles = []

        # Group by category for better organization
        grouped = {}
        for result in results:
            if result.category not in grouped:
                grouped[result.category] = []
            grouped[result.category].append(result)

        # Build tiles with category headers
        for category, category_results in grouped.items():
            # Category header
            tiles.append(
                ft.Container(
                    content=ft.Text(
                        category.value.upper(),
                        size=11,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.PRIMARY
                    ),
                    padding=ft.padding.only(left=16, top=8, bottom=4),
                )
            )

            # Results for this category
            for result in category_results:
                tiles.append(
                    ft.ListTile(
                        leading=ft.Icon(result.icon or ft.Icons.DESCRIPTION, size=20) if result.icon else None,
                        title=ft.Text(result.title, size=13, weight=ft.FontWeight.W_500),
                        subtitle=ft.Text(result.description, size=11, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        on_click=lambda e, r=result: self._execute_result_action(r),
                        hover_color=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
                    )
                )

        return tiles

    def _execute_result_action(self, result: SearchResult):
        """Execute the action for a selected result"""
        try:
            # Close the search view
            asyncio.create_task(self.close_view())

            # Clear search input
            self.value = ""
            self.update()

            # Execute result action
            if result.action:
                result.action()
        except Exception as ex:
            print(f"Error executing result action: {ex}")


def create_global_search_bar(
    on_search: Callable[[str, SearchCategory], Awaitable[list[SearchResult]] | list[SearchResult]] | None = None
) -> ProfessionalGlobalSearch:
    """
    Factory function to create a professional global search bar.

    Usage in main.py:
    ```python
    # Define search provider
    async def search_platform(query: str, category: SearchCategory) -> list[SearchResult]:
        # Your search logic here
        results = []

        if category in (SearchCategory.CLIENTS, SearchCategory.ALL):
            # Search clients
            clients = server_bridge.search_clients(query)
            for client in clients:
                results.append(SearchResult(
                    id=client['id'],
                    title=client['name'],
                    description=f"Last seen: {client['last_seen']}",
                    category=SearchCategory.CLIENTS,
                    action=lambda: navigate_to_client(client['id']),
                    icon=ft.Icons.COMPUTER
                ))

        # ... search other categories ...

        return results

    # Create search bar
    global_search = create_global_search_bar(on_search=search_platform)

    # Add to header (it's just a regular control!)
    header_row = ft.Row([
        breadcrumb,
        global_search  # Simple! No Stack, no positioning nightmares
    ])
    ```

    Args:
        on_search: Async or sync function that takes (query, category) and returns list of SearchResults

    Returns:
        ProfessionalGlobalSearch instance ready to use
    """
    return ProfessionalGlobalSearch(on_search=on_search)
