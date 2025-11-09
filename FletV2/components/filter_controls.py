"""Reusable search and filter controls for view modules.

Functional composition replacement for deprecated ft.UserControl.

Usage Example:
    def handle_search(query: str):
        print(f"Searching for: {query}")

    def handle_filter_change(filter_key: str, value: str):
        print(f"Filter {filter_key} changed to: {value}")

    def handle_clear_filters():
        print("All filters cleared")

    # Create filter controls
    filter_options = {
        "status": ["Active", "Inactive", "Pending"],
        "type": ["Client", "Server", "Admin"]
    }

    filter_controls, control_state = create_filter_controls(
        on_search_change=handle_search,
        filter_options=filter_options,
        on_filter_change=handle_filter_change,
        on_clear_filters=handle_clear_filters
    )

    # Programmatic control
    control_state["set_search_query"]("test query")
    control_state["set_filter_value"]("status", "Active")
    active_filters = control_state["get_active_filters"]()

    # Add to view
    view = ft.Column([
        filter_controls,
        # ... other content
    ])
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from typing import Any

import flet as ft

from FletV2.utils.async_helpers import debounce
from FletV2.utils.ui_builders import create_filter_dropdown, create_search_bar


def create_filter_controls(
    on_search_change: Callable[[str], None],
    filter_options: dict[str, list[str]] | None = None,
    on_filter_change: Callable[[str, str], None] | None = None,
    on_clear_filters: Callable[[], None] | None = None,
    search_placeholder: str = "Search...",
    search_width: int = 300,
    filter_width: int = 150,
    debounce_time: float = 0.5,
) -> tuple[ft.Row, dict[str, Any]]:
    """
    Create combined search and filter controls with state management.

    This function provides a standardized interface for filtering data with:
    - Debounced search functionality
    - Multiple filter dropdowns
    - Clear filters capability
    - State management for all filters

    Args:
        on_search_change: Function to call when search query changes
        filter_options: Dictionary of filter names and their options
        on_filter_change: Function to call when a filter value changes
        on_clear_filters: Function to call when filters are cleared
        search_placeholder: Placeholder text for search bar
        search_width: Width of search bar
        filter_width: Width of filter dropdowns
        debounce_time: Debounce time for search input

    Returns:
        Tuple containing:
        - ft.Row: The complete filter controls UI
        - Dict: Control state object with methods for programmatic control
    """
    filter_options = filter_options or {}

    # Filter state dictionary
    filter_state = {key: "All" for key in filter_options.keys()}

    # Create refs for UI controls that need updates
    search_ref = ft.Ref[ft.TextField]()
    filter_refs = {key: ft.Ref[ft.Dropdown]() for key in filter_options.keys()}

    # Event handlers - defined before being referenced
    async def _internal_search_handler(query: str):
        """Internal method to handle the debounced search."""
        try:
            # Make on_search_change available in closure
            nonlocal on_search_change
            result: Any = on_search_change(query)
            if inspect.isawaitable(result):
                awaited: Awaitable[Any] = result  # type: ignore[assignment]
                await awaited
        except Exception as exc:  # pragma: no cover - UI feedback path
            # For functional approach, we need to handle error display differently
            # This would typically be handled by the calling code
            print(f"Search error: {exc}")

    # Create debounced search function after defining the handler
    debounced_search = debounce(debounce_time)(_internal_search_handler)

    def _handle_search_change(e: ft.ControlEvent | str):
        """Handle search input changes with debouncing."""
        value = e if isinstance(e, str) else getattr(getattr(e, "control", None), "value", "")
        asyncio.create_task(debounced_search(value))

    def _handle_filter_change(e: ft.ControlEvent, filter_key: str):
        """Handle filter dropdown changes."""
        selected_value = e.control.value
        filter_state[filter_key] = selected_value

        # Call the provided filter handler if available
        if on_filter_change:
            on_filter_change(filter_key, selected_value)

    def _handle_clear_filters(e: ft.ControlEvent):
        """Handle clear filters button click."""
        # Reset all filter states to "All"
        for key in filter_state.keys():
            filter_state[key] = "All"

        # Reset search control
        if search_ref.current:
            search_ref.current.value = ""

        # Update the UI controls to reflect the reset state
        for _, ref in filter_refs.items():
            if ref.current:
                ref.current.value = "All"

        # Call the clear filters handler if provided
        if on_clear_filters:
            on_clear_filters()

        # Update all controls efficiently
        controls_to_update = [search_ref.current] + [ref.current for ref in filter_refs.values()]
        for control in controls_to_update:
            if control:
                control.update()

    # Create search control
    search_control = create_search_bar(
        on_change=_handle_search_change, placeholder=search_placeholder, width=search_width
    )
    search_control.ref = search_ref

    # Create filter dropdowns
    filter_controls = []
    for key, options in filter_options.items():
        # Add "All" option at the beginning
        all_options = ["All", *options]
        dropdown = create_filter_dropdown(
            label=key.capitalize(),
            options=all_options,
            on_change=lambda e, filter_key=key: _handle_filter_change(e, filter_key),
            width=filter_width,
        )
        dropdown.ref = filter_refs[key]
        filter_controls.append(dropdown)

    # Create clear filters button
    clear_button = ft.IconButton(
        icon=ft.Icons.CLEAR_ALL, tooltip="Clear all filters", on_click=_handle_clear_filters
    )

    # Control API methods
    def get_active_filters() -> dict[str, str]:
        """Get a dictionary of all active filters (non-All values)."""
        return {k: v for k, v in filter_state.items() if v != "All"}

    def set_search_query(query: str):
        """Programmatically set the search query."""
        if search_ref.current:
            search_ref.current.value = query
            search_ref.current.update()

    def set_filter_value(filter_key: str, filter_value: str):
        """Programmatically set a filter value."""
        if filter_key in filter_refs and filter_refs[filter_key].current:
            filter_state[filter_key] = filter_value
            filter_refs[filter_key].current.value = filter_value
            filter_refs[filter_key].current.update()

    def clear_all_filters():
        """Programmatically clear all filters."""
        _handle_clear_filters(None)

    def update_all():
        """Update all controls efficiently."""
        controls_to_update = [search_ref.current] + [ref.current for ref in filter_refs.values()]
        for control in controls_to_update:
            if control:
                control.update()

    # Create control state object with methods
    control_state = {
        "get_active_filters": get_active_filters,
        "set_search_query": set_search_query,
        "set_filter_value": set_filter_value,
        "clear_all_filters": clear_all_filters,
        "update_all": update_all,
        "search_ref": search_ref,
        "filter_refs": filter_refs,
        "filter_state": filter_state,
    }

    # Create the main UI row
    controls = [search_control, *filter_controls]

    # Add space and clear button if we have filters
    if filter_controls:
        controls.extend([ft.VerticalDivider(width=20), clear_button])

    ui_row = ft.Row(
        controls=controls,
        spacing=10,
        wrap=True,  # Allow wrapping on smaller screens
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ui_row, control_state


# Convenience function to create filter controls with common patterns
def create_common_filter_controls(
    on_search_change: Callable[[str], None],
    default_filters: dict[str, list[str]] | None = None,
    on_filter_change: Callable[[str, str], None] | None = None,
    on_clear_filters: Callable[[], None] | None = None,
) -> tuple[ft.Row, dict[str, Any]]:
    """
    Create filter controls with common default filter options.

    Args:
        on_search_change: Function to call when search query changes
        default_filters: Dictionary of filter names and their options
        on_filter_change: Function to call when a filter value changes
        on_clear_filters: Function to call when filters are cleared

    Returns:
        Tuple containing:
        - ft.Row: The complete filter controls UI
        - Dict: Control state object with methods for programmatic control
    """
    if default_filters is None:
        default_filters = {}

    return create_filter_controls(
        on_search_change=on_search_change,
        filter_options=default_filters,
        on_filter_change=on_filter_change,
        on_clear_filters=on_clear_filters,
    )
