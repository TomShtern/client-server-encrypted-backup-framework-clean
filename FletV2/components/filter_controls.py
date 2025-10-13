"""Reusable search and filter controls for view modules."""

from __future__ import annotations

import asyncio
import inspect
from typing import Callable, Dict, List, Optional, Awaitable, Any

import flet as ft

from FletV2.utils.async_helpers import debounce
from FletV2.utils.ui_builders import create_filter_dropdown, create_search_bar


class FilterControls(ft.UserControl):
    """
    Combined search and filter controls with state management.

    This component provides a standardized interface for filtering data with:
    - Debounced search functionality
    - Multiple filter dropdowns
    - Clear filters capability
    - State management for all filters
    """

    def __init__(
        self,
        on_search_change: Callable[[str], None],
        filter_options: Optional[Dict[str, List[str]]] = None,
        on_filter_change: Optional[Callable[[str, str], None]] = None,
        on_clear_filters: Optional[Callable[[], None]] = None,
        search_placeholder: str = "Search...",
        search_width: int = 300,
        filter_width: int = 150,
        debounce_time: float = 0.5
    ):
        super().__init__()

        self.on_search_change = on_search_change
        self.filter_options = filter_options or {}
        self.on_filter_change = on_filter_change
        self.on_clear_filters = on_clear_filters
        self.search_placeholder = search_placeholder
        self.search_width = search_width
        self.filter_width = filter_width
        self.debounce_time = debounce_time

        # Filter state dictionary
        self.filter_state = {key: "All" for key in self.filter_options.keys()}

        # Create debounced search function
        self.debounced_search = debounce(self.debounce_time)(self._internal_search_handler)

        # Create UI controls
        self.search_control = create_search_bar(
            on_change=self._handle_search_change,
            placeholder=self.search_placeholder,
            width=self.search_width
        )

        # Create filter dropdowns
        self.filter_controls = {}
        for key, options in self.filter_options.items():
            # Add "All" option at the beginning
            all_options = ["All"] + options
            self.filter_controls[key] = create_filter_dropdown(
                label=key.capitalize(),
                options=all_options,
                on_change=lambda e, filter_key=key: self._handle_filter_change(e, filter_key),
                width=self.filter_width
            )

        # Create clear filters button
        self.clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR_ALL,
            tooltip="Clear all filters",
            on_click=self._handle_clear_filters
        )

    def _handle_search_change(self, e: ft.ControlEvent):
        """Handle search input changes with debouncing."""
        asyncio.create_task(self.debounced_search(e.control.value))

    async def _internal_search_handler(self, query: str):
        """Internal method to handle the debounced search."""
        try:
            result: Any = self.on_search_change(query)
            if inspect.isawaitable(result):
                awaited: Awaitable[Any] = result  # type: ignore[assignment]
                await awaited
        except Exception as exc:  # pragma: no cover - UI feedback path
            page = getattr(self, "page", None)
            if isinstance(page, ft.Page):
                page.snack_bar = ft.SnackBar(content=ft.Text(str(exc)))
                page.snack_bar.open = True
                page.update()

    def _handle_filter_change(self, e: ft.ControlEvent, filter_key: str):
        """Handle filter dropdown changes."""
        selected_value = e.control.value
        self.filter_state[filter_key] = selected_value

        # Call the provided filter handler if available
        if self.on_filter_change:
            self.on_filter_change(filter_key, selected_value)

        # In a real implementation, you would typically call the main filter handler here
        # which would apply all active filters together

    def _handle_clear_filters(self, e: ft.ControlEvent):
        """Handle clear filters button click."""
        # Reset all filter states to "All"
        for key in self.filter_state.keys():
            self.filter_state[key] = "All"

        # Reset search control
        self.search_control.value = ""

        # Update the UI controls to reflect the reset state
        for key, control in self.filter_controls.items():
            control.value = "All"

        # Call the clear filters handler if provided
        if self.on_clear_filters:
            self.on_clear_filters()

        self.update()

    def get_active_filters(self) -> Dict[str, str]:
        """Get a dictionary of all active filters (non-All values)."""
        return {k: v for k, v in self.filter_state.items() if v != "All"}

    def set_search_query(self, query: str):
        """Programmatically set the search query."""
        self.search_control.value = query
        self.update()

    def set_filter_value(self, filter_key: str, filter_value: str):
        """Programmatically set a filter value."""
        if filter_key in self.filter_controls:
            self.filter_state[filter_key] = filter_value
            self.filter_controls[filter_key].value = filter_value
            self.update()

    def clear_all_filters(self):
        """Programmatically clear all filters."""
        self._handle_clear_filters(None)

    def build(self):
        """Build the filter controls UI."""
        # Create a row with all controls
        controls = [self.search_control, *list(self.filter_controls.values())]

        # Add space and clear button if we have filters
        if self.filter_controls:
            controls.extend([ft.VerticalDivider(width=20), self.clear_button])

        return ft.Row(
            controls=controls,
            spacing=10,
            wrap=True,  # Allow wrapping on smaller screens
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )


# Convenience function to create filter controls with common patterns
def create_common_filter_controls(
    on_search_change: Callable[[str], None],
    default_filters: Optional[Dict[str, List[str]]] = None,
    on_filter_change: Optional[Callable[[str, str], None]] = None,
    on_clear_filters: Optional[Callable[[], None]] = None
) -> FilterControls:
    """
    Create filter controls with common default filter options.

    Args:
        on_search_change: Function to call when search query changes
        default_filters: Dictionary of filter names and their options
        on_filter_change: Function to call when a filter value changes
        on_clear_filters: Function to call when filters are cleared

    Returns:
        FilterControls instance with common configuration
    """
    if default_filters is None:
        default_filters = {}

    return FilterControls(
        on_search_change=on_search_change,
        filter_options=default_filters,
        on_filter_change=on_filter_change,
        on_clear_filters=on_clear_filters
    )