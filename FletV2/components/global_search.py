"""
Global Search Component for Desktop Applications

This module provides a comprehensive global search component for desktop applications,
supporting cross-data-type search, categorized results, and search history.

Compatible with Flet 0.28.3 and Material Design 3.
"""

import asyncio
import contextlib
import inspect
import math
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


class GlobalSearch(ft.Container):
    """
    Global search component with comprehensive search capabilities

    Features:
    - Cross-data-type search
    - Categorized results
    - Search history
    - Quick access shortcuts
    - Real-time search suggestions
    - Keyboard navigation
    """

    def __init__(
        self,
        search_providers: dict[SearchCategory, Callable] | None = None,
        on_search: Callable[[str, SearchCategory], Awaitable[list[SearchResult]] | list[SearchResult]] | None = None,
        max_results: int = 50,
        show_history: bool = True,
        **kwargs
    ):
        # Inline positioning – component will be embedded in headers
        kwargs.setdefault('alignment', ft.alignment.top_right)
        kwargs.setdefault('padding', 0)
        kwargs.setdefault('bgcolor', None)
        kwargs.setdefault('shadow', None)
        kwargs.setdefault('expand', False)

        super().__init__(**kwargs)

        self.search_providers = search_providers or {}
        self.on_search = on_search
        self.max_results = max_results
        self.show_history = show_history
        self._active_search_task: asyncio.Task[list[SearchResult]] | None = None

        # State
        self.search_history: list[str] = []
        self.current_results: list[SearchResult] = []
        self.selected_index = 0
        self.is_expanded = False
        self._panel_width = 360

        # UI Components
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components"""

        # Search input field
        clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            tooltip="Clear search",
            on_click=self._clear_search,
            icon_size=20,
        )

        self.search_input = ft.TextField(
            label=None,
            hint_text="Search the platform (Ctrl+F)",
            prefix_icon=ft.Icons.SEARCH,
            suffix=clear_button,
            on_change=self._on_search_change,
            on_submit=self._on_search_submit,
            autofocus=False,
            border_radius=12,
            height=48,
            text_size=14,
            width=self._panel_width - 40,
            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.SURFACE),
            focused_bgcolor=ft.Colors.SURFACE,
            filled=True,
            dense=True,
        )
        self.search_input.animate_opacity = ft.Animation(120, ft.AnimationCurve.EASE_OUT)

        # Search suggestions
        self.suggestions_list = ft.ListView(
            spacing=2,
            padding=ft.padding.symmetric(vertical=4),
            height=120,
            visible=False
        )

        # Search results container
        self.results_container = ft.Container(
            content=ft.Column([], spacing=4, scroll=ft.ScrollMode.AUTO),
            visible=False,
            height=220,
            bgcolor=ft.Colors.SURFACE,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            padding=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

        # Category filters
        self.category_filter = ft.Dropdown(
            options=[
                ft.dropdown.Option("all", "All Categories"),
                ft.dropdown.Option("clients", "Clients"),
                ft.dropdown.Option("files", "Files"),
                ft.dropdown.Option("database", "Database"),
                ft.dropdown.Option("logs", "Logs"),
                ft.dropdown.Option("settings", "Settings"),
            ],
            value="all",
            width=144,
            text_size=12,
            on_change=self._on_category_change
        )

        # Search toolbar
        self.search_toolbar = ft.Row(
            [
                self.search_input,
                ft.Container(width=6),
                self.category_filter,
                ft.IconButton(
                    icon=ft.Icons.KEYBOARD,
                    tooltip="Keyboard shortcuts (Ctrl+K)",
                    on_click=self._show_shortcuts_help
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=8,
        )

        # Trigger button with chevron indicator
        self._chevron_icon = ft.Icon(
            ft.Icons.KEYBOARD_ARROW_DOWN,
            size=16,
            color=ft.Colors.PRIMARY,
        )
        self._chevron_icon.rotate = ft.Rotate(0, alignment=ft.alignment.center)
        self._chevron_icon.animate_rotation = ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC)

        trigger_content = ft.Row(
            [
                ft.Icon(ft.Icons.SEARCH, size=18, color=ft.Colors.PRIMARY),
                ft.Text(
                    "Search",
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.PRIMARY,
                ),
                self._chevron_icon,
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        )

        self._trigger_container = ft.Container(
            content=trigger_content,
            padding=ft.padding.symmetric(horizontal=14, vertical=9),
            border_radius=18,
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.PRIMARY),
            border=ft.border.all(1, ft.Colors.with_opacity(0.14, ft.Colors.PRIMARY)),
            ink=True,
            on_click=lambda e: self.toggle(),
            tooltip="Search (Ctrl+F)",
        )

        # Dropdown panel with animation
        panel_content = ft.Column(
            [
                self.search_toolbar,
                self.suggestions_list,
                self.results_container,
            ],
            spacing=8,
            tight=True,
            scroll=ft.ScrollMode.AUTO,
        )

        self.dropdown_panel = ft.Container(
            content=panel_content,
            width=self._panel_width,
            padding=ft.padding.all(12),
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.98, ft.Colors.SURFACE),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=24,
                color=ft.Colors.with_opacity(0.32, ft.Colors.BLACK),
                offset=ft.Offset(0, 6),
            ),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            opacity=0,
            visible=False,
            disabled=True,
        )
        self.dropdown_panel.scale = ft.Scale(0.95, alignment=ft.alignment.top_center)
        self.dropdown_panel.animate_opacity = ft.Animation(160, ft.AnimationCurve.EASE_OUT)
        self.dropdown_panel.animate_scale = ft.Animation(200, ft.AnimationCurve.EASE_OUT_CUBIC)

        # Main layout - stack to allow floating dropdown without shifting layout
        # In Flet 0.28.3, controls in Stack use top/left/right/bottom properties directly
        self.dropdown_panel.right = 0
        self.dropdown_panel.top = 48

        stack = ft.Stack(
            [
                self._trigger_container,
                self.dropdown_panel,
            ],
            clip_behavior=ft.ClipBehavior.NONE,
            expand=False,
        )

        stack.width = self._panel_width
        stack.height = 44
        self.width = self._panel_width
        self.height = 44
        self.content = stack

    @property
    def is_open(self) -> bool:
        """Return whether the dropdown is currently expanded."""
        return self.is_expanded

    def focus_search(self):
        """Ensure the search is expanded and focused."""
        self.expand()
        self._schedule_focus()

    def hide_search(self):
        """Hide the search component and clear state."""
        self.collapse(clear=True)

    def show_search(self, initial_query: str = ""):
        """Show the search component with optional initial query"""
        self.expand(initial_query=initial_query)
        self._schedule_focus()

    def expand(self, initial_query: str = "") -> None:
        """Animate open the dropdown panel."""
        if self.is_expanded and not initial_query:
            return

        self.is_expanded = True
        if initial_query:
            self.search_input.value = initial_query
            self._perform_search(initial_query)

        self.dropdown_panel.disabled = False
        self.dropdown_panel.visible = True
        self.dropdown_panel.opacity = 1
        self.dropdown_panel.scale = ft.Scale(1, alignment=ft.alignment.top_center)
        self._update_trigger_state(expanded=True)
        self._safe_update(self.dropdown_panel)
        self._safe_update(self._trigger_container)
        self._safe_update(self._chevron_icon)

    def collapse(self, clear: bool = False) -> None:
        """Animate close the dropdown panel."""
        if not self.is_expanded and not clear:
            return

        self.is_expanded = False
        if clear:
            self._clear_search(None)

        self.dropdown_panel.opacity = 0
        self.dropdown_panel.scale = ft.Scale(0.95, alignment=ft.alignment.top_center)
        self.dropdown_panel.disabled = True
        self._update_trigger_state(expanded=False)
        self._safe_update(self.dropdown_panel)
        self._safe_update(self._trigger_container)
        self._safe_update(self._chevron_icon)

    def toggle(self) -> None:
        """Toggle dropdown visibility."""
        if self.is_expanded:
            self.collapse(clear=False)
        else:
            self.expand()
            self._schedule_focus()

    def _update_trigger_state(self, expanded: bool) -> None:
        """Update trigger styling based on expansion state."""

        if expanded:
            self._trigger_container.bgcolor = ft.Colors.PRIMARY_CONTAINER
            self._trigger_container.border = ft.border.all(1, ft.Colors.with_opacity(0.22, ft.Colors.PRIMARY))
            rotation = math.pi
        else:
            self._trigger_container.bgcolor = ft.Colors.with_opacity(0.12, ft.Colors.PRIMARY)
            self._trigger_container.border = ft.border.all(1, ft.Colors.with_opacity(0.14, ft.Colors.PRIMARY))
            rotation = 0

        self._chevron_icon.rotate = ft.Rotate(rotation, alignment=ft.alignment.center)

    def _schedule_focus(self) -> None:
        """Focus search input after animation tick."""
        if not getattr(self, "page", None):
            return

        async def _focus_later():
            try:
                await asyncio.sleep(0.05)
            except asyncio.CancelledError:
                raise
            self.search_input.focus()
            self.search_input.select_all()

        with contextlib.suppress(AttributeError, RuntimeError):
            self.page.run_task(_focus_later)
            return

        # Fallback synchronous focus if run_task unavailable
        self.search_input.focus()
        self.search_input.select_all()

    @staticmethod
    def _safe_update(control: ft.Control) -> None:
        if control is None:
            return
        if getattr(control, "page", None):
            try:
                control.update()
            except Exception:
                pass

    def _on_search_change(self, e: ft.ControlEvent):
        """Handle search input change"""
        query = e.control.value or ""

        if len(query) >= 2:
            # Show suggestions or perform search
            if self.show_history and not query.strip() and self.search_history:
                self._show_history()
            else:
                self._show_suggestions(query)
        else:
            self._hide_suggestions()

    def _on_search_submit(self, e: ft.ControlEvent):
        """Handle search submission"""
        query = e.control.value or ""
        if query.strip():
            self._perform_search(query)

    def _on_category_change(self, e: ft.ControlEvent):
        """Handle category filter change"""
        if self.search_input.value:
            self._perform_search(self.search_input.value)

    def _clear_search(self, e: ft.ControlEvent):
        """Clear the search"""
        self.search_input.value = ""
        self.current_results = []
        self._hide_results()
        self._hide_suggestions()
        self._safe_update(self.search_input)

    def _perform_search(self, query: str):
        """Perform the actual search"""

        # Add to search history
        self._add_to_history(query)

        # Get category filter
        category_filter = self.category_filter.value
        try:
            category = SearchCategory(category_filter)
        except ValueError:
            category = SearchCategory.ALL

        # Perform search
        if self.on_search:
            try:
                result = self.on_search(query, category)
                if inspect.isawaitable(result):
                    self._launch_async_search(result)
                else:
                    self._display_results(result)
            except Exception as ex:
                print(f"Search error: {ex}")
                self._show_error("Search failed. Please try again.")
        else:
            # Use built-in search providers
            self._search_with_providers(query, category)

    def _launch_async_search(self, awaitable: Awaitable[list[SearchResult]]) -> None:
        """Start async search task and manage its lifecycle."""

        if self._active_search_task and not self._active_search_task.done():
            self._active_search_task.cancel()

        async def run_async() -> list[SearchResult]:
            return await awaitable

        task = asyncio.create_task(run_async())
        self._active_search_task = task

        def _handle_completion(completed: asyncio.Task[list[SearchResult]]) -> None:
            if completed.cancelled():
                return
            try:
                results = completed.result()
            except Exception as ex:  # pragma: no cover - diagnostic path
                print(f"Async search error: {ex}")
                self._show_error("Search failed. Please try again.")
                return
            self._display_results(results)

        task.add_done_callback(_handle_completion)

    def _search_with_providers(self, query: str, category: SearchCategory):
        """Search using registered providers"""

        results = []
        query_lower = query.lower()

        # Search in relevant categories
        categories_to_search = [category] if category != SearchCategory.ALL else list(SearchCategory)
        categories_to_search = [c for c in categories_to_search if c != SearchCategory.ALL]

        for cat in categories_to_search:
            if cat in self.search_providers:
                try:
                    provider_results = self.search_providers[cat](query_lower)
                    results.extend(provider_results)
                except Exception as ex:
                    print(f"Search provider error for {cat}: {ex}")

        # Limit results
        results = results[:self.max_results]
        self._display_results(results)

    def _display_results(self, results: list[SearchResult]):
        """Display search results"""

        self.current_results = results
        self.selected_index = 0

        if not results:
            self._show_no_results()
            return

        # Group results by category
        grouped_results = {}
        for result in results:
            category = result.category.value
            if category not in grouped_results:
                grouped_results[category] = []
            grouped_results[category].append(result)

        # Create result items
        result_items = []

        for category, category_results in grouped_results.items():
            # Category header
            category_icon = self._get_category_icon(SearchCategory(category))
            category_items = ft.Column([
                ft.Row([
                    ft.Icon(category_icon, size=16, color=ft.Colors.PRIMARY),
                    ft.Text(category.title(), weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.ON_SURFACE),
                ], spacing=8),
                ft.Container(height=1, bgcolor=ft.Colors.OUTLINE_VARIANT, margin=ft.margin.symmetric(vertical=4))
            ], spacing=4)

            result_items.append(category_items)

            # Category results
            for i, result in enumerate(category_results):
                result_item = self._create_result_item(result, i)
                result_items.append(result_item)

        # Update results container
        self.results_container.content = ft.Column(result_items, spacing=4)
        self.results_container.visible = True
        self._hide_suggestions()

        # Update UI
        self._safe_update(self.results_container)

    def _create_result_item(self, result: SearchResult, index: int) -> ft.Container:
        """Create a search result item"""

        icon = ft.Icon(result.icon or ft.Icons.DESCRIPTION, size=20)

        title_text = ft.Text(
            result.title,
            weight=ft.FontWeight.W_500,
            size=14,
            color=ft.Colors.ON_SURFACE,
            expand=True
        )

        description_text = ft.Text(
            result.description,
            size=12,
            color=ft.Colors.ON_SURFACE_VARIANT,
            max_lines=2,
            expand=True
        )

        content = ft.Column([
            ft.Row([icon, title_text], spacing=8),
            description_text
        ], spacing=2, expand=True)

        return ft.Container(
            content=content,
            padding=12,
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.SURFACE),
            on_click=lambda e, r=result: self._on_result_click(r),
            on_hover=lambda e: self._on_result_hover(e, index)
        )

    def _on_result_click(self, result: SearchResult):
        """Handle result item click"""
        if result.action:
            try:
                result.action()
            except Exception as ex:
                print(f"Error executing result action: {ex}")
        self.collapse(clear=False)

    def _on_result_hover(self, e: ft.ControlEvent, index: int):
        """Handle result item hover"""
        self.selected_index = index

    def _show_no_results(self):
        """Show no results message"""
        no_results = ft.Column([
            ft.Icon(ft.Icons.SEARCH_OFF, size=48, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text(
                "No results found",
                size=16,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.ON_SURFACE_VARIANT,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                "Try different keywords or check your spelling",
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT,
                text_align=ft.TextAlign.CENTER
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)

        self.results_container.content = no_results
        self.results_container.visible = True
        self._hide_suggestions()
        self._safe_update(self.results_container)

    def _show_error(self, error_message: str):
        """Show error message"""
        error_content = ft.Column([
            ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.ERROR),
            ft.Text(
                "Search Error",
                size=16,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.ERROR,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                error_message,
                size=12,
                color=ft.Colors.ERROR,
                text_align=ft.TextAlign.CENTER
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)

        self.results_container.content = error_content
        self.results_container.visible = True
        self._hide_suggestions()
        self._safe_update(self.results_container)

    def _show_suggestions(self, query: str):
        """Show search suggestions"""
        # Simple suggestion implementation - could be enhanced with actual suggestions
        lower_query = query.lower()
        common_terms = ["client", "file", "database", "log", "backup", "settings"]
        suggestions = [
            term for term in common_terms
            if term.startswith(lower_query) and term != lower_query
        ]

        history_matches = [
            history_item
            for history_item in self.search_history[-5:]
            if lower_query in history_item.lower() and history_item not in suggestions
        ]
        suggestions.extend(history_matches)

        if suggestions:
            self.suggestions_list.controls = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HISTORY, size=16),
                    title=ft.Text(suggestion, size=13),
                    on_click=lambda e, s=suggestion: self._apply_suggestion(s)
                )
                for suggestion in suggestions[:5]
            ]
            self.suggestions_list.visible = True
        else:
            self._hide_suggestions()

        self._safe_update(self.suggestions_list)

    def _show_history(self):
        """Show search history"""
        if not self.search_history:
            return

        history_items = []
        for history_item in reversed(self.search_history[-10:]):
            item = ft.ListTile(
                leading=ft.Icon(ft.Icons.HISTORY, size=16),
                title=ft.Text(history_item, size=13),
                on_click=lambda e, h=history_item: self._apply_suggestion(h)
            )
            history_items.append(item)

        self.suggestions_list.controls = history_items
        self.suggestions_list.visible = True
        self._safe_update(self.suggestions_list)

    def _hide_suggestions(self):
        """Hide suggestions"""
        self.suggestions_list.visible = False
        self._safe_update(self.suggestions_list)

    def _hide_results(self):
        """Hide search results"""
        self.results_container.visible = False
        self._safe_update(self.results_container)

    def _apply_suggestion(self, suggestion: str):
        """Apply a search suggestion"""
        self.search_input.value = suggestion
        self._perform_search(suggestion)
        self._hide_suggestions()

    def _add_to_history(self, query: str):
        """Add query to search history"""
        if query in self.search_history:
            self.search_history.remove(query)
        self.search_history.append(query)

        # Limit history size
        if len(self.search_history) > 50:
            self.search_history = self.search_history[-50:]

    def _get_category_icon(self, category: SearchCategory) -> str:
        """Get icon for search category"""
        icon_map = {
            SearchCategory.CLIENTS: ft.Icons.PEOPLE,
            SearchCategory.FILES: ft.Icons.INSERT_DRIVE_FILE,
            SearchCategory.DATABASE: ft.Icons.STORAGE,
            SearchCategory.LOGS: ft.Icons.ARTICLE,
            SearchCategory.SETTINGS: ft.Icons.SETTINGS,
        }
        return icon_map.get(category, ft.Icons.SEARCH)

    def _show_shortcuts_help(self, e: ft.ControlEvent):
        """Show keyboard shortcuts help"""
        help_text = """
        Global Search Shortcuts:

        Ctrl+F - Open global search
        Ctrl+K - Open global search
        Esc - Close search
        ↑/↓ - Navigate results
        Enter - Select result
        Tab - Move to category filter
        """

        # This would show a help dialog - implementation depends on parent app
        print(help_text)


def create_global_search_bar(
    search_providers: dict[SearchCategory, Callable] | None = None,
    on_search: Callable[[str, SearchCategory], list[SearchResult]] | None = None
) -> GlobalSearch:
    """
    Factory function to create a global search bar

    Args:
        search_providers: Dictionary of search functions by category
        on_search: Global search function

    Returns:
        Configured GlobalSearch instance
    """

    return GlobalSearch(
        search_providers=search_providers,
        on_search=on_search,
        max_results=50,
        show_history=True
    )
