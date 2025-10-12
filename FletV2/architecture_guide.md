# FletV2 Architecture Guide - 5-Section Pattern

**Version**: 1.0
**Last Updated**: October 12, 2025
**Applies To**: All FletV2 view files

---

## Overview

This guide defines the standard architecture pattern for all FletV2 view files. The **5-Section Pattern** organizes code into logical, testable, and maintainable sections with clear separation of concerns.

---

## The 5-Section Pattern

Every view file should follow this structure:

```python
#!/usr/bin/env python3
"""
View Name - Brief Description

Design Philosophy:
- Key design principle 1
- Key design principle 2
"""

# Standard imports
import asyncio
import flet as ft
from typing import Any, Callable, Optional

# Phase 1 utility imports
from FletV2.utils.loading_states import (
    create_loading_indicator,
    create_empty_state,
    show_snackbar,
    show_error_snackbar,
    show_success_snackbar
)
from FletV2.utils.data_export import (
    export_to_json,
    export_to_csv,
    export_to_txt,
    generate_export_filename
)
from FletV2.utils.ui_builders import (
    create_search_bar,
    create_filter_dropdown,
    create_action_button,
    create_confirmation_dialog
)
from FletV2.utils.async_helpers import (
    safe_server_call,
    safe_load_data,
    handle_server_result,
    debounce
)

# ===== SECTION 1: DATA FETCHING =====
# Async wrappers for server calls and data loading

# ===== SECTION 2: BUSINESS LOGIC =====
# Pure functions for data processing, filtering, and transformation

# ===== SECTION 3: UI COMPONENTS =====
# Flet control builders (cards, buttons, containers)

# ===== SECTION 4: EVENT HANDLERS =====
# User interaction handlers (clicks, changes, form submissions)

# ===== SECTION 5: MAIN VIEW =====
# View composition, lifecycle, and public API
```

---

## Section 1: Data Fetching

### Purpose
Isolate all server communication and data loading logic. This section contains async wrappers that safely interact with the ServerBridge.

### Rules
1. ✅ **DO**: Use `async def` for all data fetching functions
2. ✅ **DO**: Use `safe_server_call()` or `safe_load_data()` from async_helpers
3. ✅ **DO**: Handle errors gracefully with fallback data
4. ❌ **DON'T**: Mix UI logic in data fetching functions
5. ❌ **DON'T**: Directly update UI controls from this section

### Template
```python
# ===== SECTION 1: DATA FETCHING =====
# Async wrappers for server calls and data loading

def fetch_data_sync(server_bridge: Any | None, filter_params: dict) -> list[dict]:
    """
    Synchronously fetch data from server with error handling.

    Args:
        server_bridge: Server bridge instance (may be None)
        filter_params: Parameters for filtering

    Returns:
        List of data items or empty list on error
    """
    if not server_bridge:
        return []

    try:
        result = safe_server_call(server_bridge, 'get_data', filter_params)
        if result.get('success'):
            return result.get('data', [])
        return []
    except Exception as ex:
        logger.error(f"Failed to fetch data: {ex}")
        return []


async def fetch_data_async(server_bridge: Any | None, filter_params: dict) -> list[dict]:
    """
    Async wrapper for data fetching - runs sync code in executor.

    Args:
        server_bridge: Server bridge instance
        filter_params: Parameters for filtering

    Returns:
        List of data items
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, fetch_data_sync, server_bridge, filter_params)


def get_mock_data() -> list[dict]:
    """
    Provide mock data for GUI-only mode (no server).

    Returns:
        List of mock data items
    """
    return [
        {"id": 1, "name": "Sample Item 1", "status": "active"},
        {"id": 2, "name": "Sample Item 2", "status": "inactive"},
    ]
```

### Key Patterns
- **Sync → Async Wrapper**: Create a sync function, then wrap it with `run_in_executor`
- **Safe Server Calls**: Always use `safe_server_call()` for error handling
- **Fallback Data**: Provide mock data for GUI-only mode

---

## Section 2: Business Logic

### Purpose
Pure functions for data processing that don't depend on UI or server state. These functions are highly testable and reusable.

### Rules
1. ✅ **DO**: Keep functions pure (same input = same output)
2. ✅ **DO**: Focus on data transformation and filtering
3. ✅ **DO**: Add type hints for all parameters and returns
4. ❌ **DON'T**: Access global state or UI controls
5. ❌ **DON'T**: Make server calls from this section

### Template
```python
# ===== SECTION 2: BUSINESS LOGIC =====
# Pure functions for data processing, filtering, and transformation

def filter_by_search_query(items: list[dict], query: str) -> list[dict]:
    """
    Filter items by search query (case-insensitive).

    Args:
        items: List of items to filter
        query: Search query string

    Returns:
        Filtered list of items
    """
    if not query:
        return items

    query_lower = query.lower()
    return [
        item for item in items
        if query_lower in item.get('name', '').lower() or
           query_lower in item.get('description', '').lower()
    ]


def sort_by_field(items: list[dict], field: str, ascending: bool = True) -> list[dict]:
    """
    Sort items by specified field.

    Args:
        items: List of items to sort
        field: Field name to sort by
        ascending: Sort direction (True for ascending)

    Returns:
        Sorted list of items
    """
    return sorted(items, key=lambda x: x.get(field, ''), reverse=not ascending)


def calculate_statistics(items: list[dict]) -> dict[str, Any]:
    """
    Calculate statistics from item list.

    Args:
        items: List of items to analyze

    Returns:
        Dictionary with statistics
    """
    return {
        'total': len(items),
        'by_status': {
            'active': len([x for x in items if x.get('status') == 'active']),
            'inactive': len([x for x in items if x.get('status') == 'inactive']),
        },
        'average_size': sum(x.get('size', 0) for x in items) / len(items) if items else 0,
    }
```

### Key Patterns
- **Filter Functions**: Return filtered subset of input
- **Transform Functions**: Convert data to different format
- **Calculation Functions**: Derive metrics from data
- **Validation Functions**: Check data validity

---

## Section 3: UI Components

### Purpose
Flet control builders that create reusable UI elements. These functions should be pure UI construction without side effects.

### Rules
1. ✅ **DO**: Use Phase 1 utilities for common UI patterns
2. ✅ **DO**: Return Flet controls (ft.Container, ft.Row, etc.)
3. ✅ **DO**: Accept styling parameters for flexibility
4. ❌ **DON'T**: Fetch data or make server calls
5. ❌ **DON'T**: Update global state from builders

### Template
```python
# ===== SECTION 3: UI COMPONENTS =====
# Flet control builders (cards, buttons, containers)

def build_item_card(item: dict, on_click: Callable) -> ft.Control:
    """
    Build card component for displaying an item.

    Args:
        item: Item data dictionary
        on_click: Callback function for card click

    Returns:
        Container with card UI
    """
    status_color = ft.Colors.GREEN_400 if item.get('status') == 'active' else ft.Colors.GREY_400

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CIRCLE, color=status_color, size=12),
                ft.Text(item.get('name', 'Unknown'), size=16, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Text(item.get('description', ''), size=14, color=ft.Colors.ON_SURFACE_VARIANT),
        ], spacing=8),
        padding=16,
        border_radius=12,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        on_click=on_click,
        ink=True,
    )


def build_header_section(title: str, on_refresh: Callable, on_export: Callable) -> ft.Control:
    """
    Build header section with title and action buttons.

    Args:
        title: Header title text
        on_refresh: Callback for refresh button
        on_export: Callback for export button

    Returns:
        Row with header components
    """
    return ft.Row([
        ft.Text(title, size=24, weight=ft.FontWeight.BOLD),
        ft.Container(expand=True),  # Spacer
        create_action_button("Refresh", on_refresh, icon=ft.Icons.REFRESH_ROUNDED),
        create_action_button("Export", on_export, icon=ft.Icons.DOWNLOAD_ROUNDED, primary=False),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
```

### Key Patterns
- **Card Builders**: Create consistent card layouts
- **Header Builders**: Standardize view headers
- **List Item Builders**: Build repeatable list items
- **Use Phase 1 Utilities**: Leverage `ui_builders` for common patterns

---

## Section 4: Event Handlers

### Purpose
Handle user interactions and coordinate between data fetching, business logic, and UI updates.

### Rules
1. ✅ **DO**: Use `async def` for handlers that need data fetching
2. ✅ **DO**: Call Section 1 functions for data
3. ✅ **DO**: Call Section 2 functions for processing
4. ✅ **DO**: Update UI controls with processed data
5. ❌ **DON'T**: Inline complex logic - extract to Section 2

### Template
```python
# ===== SECTION 4: EVENT HANDLERS =====
# User interaction handlers (clicks, changes, form submissions)

async def on_refresh_click(e: ft.ControlEvent) -> None:
    """Handle refresh button click."""
    # Show loading indicator
    loading_overlay.visible = True
    loading_overlay.update()

    try:
        # Fetch data (Section 1)
        data = await fetch_data_async(server_bridge, filter_params)

        # Process data (Section 2)
        filtered_data = filter_by_search_query(data, search_query)
        sorted_data = sort_by_field(filtered_data, 'name')

        # Update UI
        render_items(sorted_data)
        show_success_snackbar(page, "Data refreshed successfully")

    except Exception as ex:
        show_error_snackbar(page, f"Refresh failed: {ex}")
    finally:
        loading_overlay.visible = False
        loading_overlay.update()


def on_search_change(e: ft.ControlEvent) -> None:
    """Handle search input change with debounce."""
    nonlocal search_query
    search_query = e.data or ""

    # Trigger debounced search (defined with @debounce decorator)
    page.run_task(perform_search_async)


@debounce(0.5)  # 500ms delay
async def perform_search_async() -> None:
    """Execute search after debounce delay."""
    # Get current data
    data = current_data_cache

    # Filter (Section 2)
    filtered_data = filter_by_search_query(data, search_query)

    # Update UI
    render_items(filtered_data)


async def on_export_click(e: ft.ControlEvent) -> None:
    """Handle export button click."""
    try:
        # Get current filtered data
        data_to_export = [item for item in current_data_cache if item.get('visible')]

        # Generate filename
        filename = generate_export_filename("data", "json")

        # Export (Phase 1 utility)
        export_to_json(data_to_export, filename)

        show_success_snackbar(page, f"Exported to {filename}")
    except Exception as ex:
        show_error_snackbar(page, f"Export failed: {ex}")
```

### Key Patterns
- **Async Event Handlers**: Use `async def` when fetching data
- **Error Handling**: Always wrap in try/except with user feedback
- **Debounced Handlers**: Use `@debounce` decorator for expensive operations
- **Loading States**: Show/hide loading indicators during operations

---

## Section 5: Main View

### Purpose
Compose the view from all previous sections and manage lifecycle (setup, dispose).

### Rules
1. ✅ **DO**: Return tuple: (container, dispose_func, setup_func)
2. ✅ **DO**: Use Refs for controls that need updates
3. ✅ **DO**: Implement proper cleanup in dispose function
4. ❌ **DON'T**: Inline complex logic - extract to other sections
5. ❌ **DON'T**: Create monolithic setup functions

### Template
```python
# ===== SECTION 5: MAIN VIEW =====
# View composition, lifecycle, and public API

def create_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Any]]:
    """
    Create the main view with all components.

    Args:
        server_bridge: Server bridge instance (may be None)
        page: Flet page instance
        state_manager: State manager instance

    Returns:
        Tuple of (main_container, dispose_function, setup_function)
    """

    # ========== STATE ==========
    # Local state variables
    search_query = ""
    current_data_cache: list[dict] = []
    filter_params = {}

    # UI refs
    items_list_ref = ft.Ref[ft.ListView]()
    loading_overlay_ref = ft.Ref[ft.Container]()

    # ========== UI CONSTRUCTION ==========
    # Build header
    header = build_header_section(
        "View Title",
        on_refresh=on_refresh_click,
        on_export=on_export_click
    )

    # Build search controls
    search_bar = create_search_bar(
        on_change=on_search_change,
        placeholder="Search items...",
        width=300
    )

    # Build items list
    items_list = ft.ListView(
        ref=items_list_ref,
        spacing=12,
        padding=20,
        expand=True,
    )

    # Build loading overlay
    loading_overlay = create_loading_indicator("Loading items...")
    loading_overlay.visible = False
    loading_overlay.ref = loading_overlay_ref

    # Main layout
    main_container = ft.Container(
        content=ft.Column([
            header,
            search_bar,
            ft.Stack([
                items_list,
                loading_overlay,
            ], expand=True),
        ], spacing=16, expand=True),
        padding=20,
        expand=True,
    )

    # ========== LIFECYCLE ==========
    def dispose() -> None:
        """Cleanup function for view disposal."""
        # Cancel any running tasks
        if hasattr(page, '_search_task') and page._search_task:
            page._search_task.cancel()

        # Clear refs
        items_list_ref.current = None
        loading_overlay_ref.current = None

    async def setup() -> None:
        """Initialize view with initial data load."""
        # Load initial data
        data = await fetch_data_async(server_bridge, filter_params)
        current_data_cache.extend(data)

        # Render initial UI
        render_items(data)

        # Setup subscriptions if state manager available
        if state_manager:
            state_manager.subscribe('data_updated', on_data_updated)

    return main_container, dispose, setup
```

### Key Patterns
- **Triple Return**: Always return (container, dispose, setup)
- **Refs for Updates**: Use Refs for controls that need targeted updates
- **Lifecycle Management**: Implement proper cleanup and initialization
- **State Isolation**: Keep view state self-contained

---

## Complete Example: Small View

Here's a complete example following the 5-section pattern:

```python
#!/usr/bin/env python3
"""
Simple Items View - Demonstrates 5-Section Pattern

This view displays a list of items with search and filter capabilities.
"""

import asyncio
import flet as ft
from typing import Any, Callable

# Phase 1 utilities
from FletV2.utils.loading_states import create_loading_indicator, create_empty_state, show_success_snackbar
from FletV2.utils.ui_builders import create_search_bar, create_action_button
from FletV2.utils.async_helpers import safe_server_call, debounce

# ===== SECTION 1: DATA FETCHING =====

def fetch_items_sync(server_bridge: Any | None) -> list[dict]:
    """Fetch items from server."""
    if not server_bridge:
        return get_mock_items()

    result = safe_server_call(server_bridge, 'get_items')
    return result.get('data', []) if result.get('success') else get_mock_items()

async def fetch_items_async(server_bridge: Any | None) -> list[dict]:
    """Async wrapper for item fetching."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, fetch_items_sync, server_bridge)

def get_mock_items() -> list[dict]:
    """Mock data for GUI-only mode."""
    return [{"id": 1, "name": "Sample Item", "status": "active"}]

# ===== SECTION 2: BUSINESS LOGIC =====

def filter_items(items: list[dict], query: str) -> list[dict]:
    """Filter items by search query."""
    if not query:
        return items
    query_lower = query.lower()
    return [item for item in items if query_lower in item['name'].lower()]

# ===== SECTION 3: UI COMPONENTS =====

def build_item_card(item: dict) -> ft.Control:
    """Build card for single item."""
    return ft.Container(
        content=ft.Text(item['name'], size=16),
        padding=16,
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
    )

# ===== SECTION 4: EVENT HANDLERS =====

def create_event_handlers(page, server_bridge, items_list_ref, current_items):
    """Factory function for event handlers with closure."""

    search_query = ""

    async def on_refresh(e):
        """Handle refresh button."""
        items = await fetch_items_async(server_bridge)
        current_items.clear()
        current_items.extend(items)
        render_items()
        show_success_snackbar(page, "Refreshed successfully")

    @debounce(0.3)
    async def on_search(query: str):
        """Handle search with debounce."""
        nonlocal search_query
        search_query = query
        filtered = filter_items(current_items, query)
        render_items(filtered)

    def render_items(items=None):
        """Render items to list."""
        items_to_render = items if items is not None else current_items
        items_list_ref.current.controls = [build_item_card(item) for item in items_to_render]
        items_list_ref.current.update()

    return on_refresh, on_search, render_items

# ===== SECTION 5: MAIN VIEW =====

def create_items_view(server_bridge, page, state_manager):
    """Create the items view."""

    # State
    current_items = []

    # Refs
    items_list_ref = ft.Ref[ft.ListView]()

    # Create event handlers
    on_refresh, on_search, render_items = create_event_handlers(
        page, server_bridge, items_list_ref, current_items
    )

    # UI construction
    header = ft.Row([
        ft.Text("Items", size=20, weight=ft.FontWeight.BOLD),
        create_action_button("Refresh", on_refresh, icon=ft.Icons.REFRESH_ROUNDED),
    ])

    search = create_search_bar(
        on_change=lambda e: page.run_task(on_search, e.data),
        placeholder="Search items..."
    )

    items_list = ft.ListView(ref=items_list_ref, spacing=8, expand=True)

    main_container = ft.Container(
        content=ft.Column([header, search, items_list], spacing=16, expand=True),
        padding=20,
        expand=True,
    )

    # Lifecycle
    def dispose():
        items_list_ref.current = None

    async def setup():
        items = await fetch_items_async(server_bridge)
        current_items.extend(items)
        render_items()

    return main_container, dispose, setup
```

---

## Migration Checklist

Use this checklist when refactoring an existing view:

### Phase 1: Utility Integration
- [ ] Add Phase 1 utility imports at top
- [ ] Replace custom loading indicators with `loading_states` utilities
- [ ] Replace custom empty states with `loading_states.create_empty_state()`
- [ ] Replace inline export logic with `data_export` functions
- [ ] Replace custom search bars with `ui_builders.create_search_bar()`
- [ ] Replace custom toast notifications with `loading_states.show_snackbar()`

### Phase 2: Section Organization
- [ ] Extract data fetching functions to Section 1
- [ ] Extract pure business logic to Section 2
- [ ] Extract UI builders to Section 3
- [ ] Extract event handlers to Section 4
- [ ] Organize main view logic in Section 5

### Phase 3: Testing & Validation
- [ ] Test all user interactions work correctly
- [ ] Verify loading states display properly
- [ ] Test error handling with server disconnected
- [ ] Verify export functionality works
- [ ] Check for memory leaks (dispose called correctly)

---

## Best Practices

### 1. Keep Sections Focused
Each section should have a single responsibility. If a section gets too large (>200 lines), extract subsections.

### 2. Use Type Hints
Always add type hints to function signatures:
```python
def process_data(items: list[dict], query: str) -> list[dict]:
    ...
```

### 3. Document Public Functions
Add docstrings to all functions that are part of the public API:
```python
def create_view(server_bridge, page, state_manager):
    """
    Create the main view.

    Args:
        server_bridge: Server communication interface
        page: Flet page instance
        state_manager: State management instance

    Returns:
        Tuple of (container, dispose_func, setup_func)
    """
```

### 4. Use Phase 1 Utilities
Always check if a Phase 1 utility exists before implementing custom logic:
- Loading states → `loading_states`
- Data export → `data_export`
- Search/filter UI → `ui_builders`
- Async helpers → `async_helpers`

### 5. Test Sections Independently
The 5-section pattern makes unit testing easy:
- Section 1: Mock server_bridge, test data fetching
- Section 2: Pure functions, test with sample data
- Section 3: Test UI builders return correct controls
- Section 4: Test event handlers with mock events
- Section 5: Integration test the full view

---

## Anti-Patterns to Avoid

### ❌ Mixing Concerns
```python
# BAD: Mixing data fetching, processing, and UI in one function
def load_and_display_data():
    result = server_bridge.get_data()  # Data fetching
    filtered = [x for x in result if x['active']]  # Processing
    items_list.controls = [build_card(x) for x in filtered]  # UI update
    items_list.update()
```

```python
# GOOD: Separate concerns into sections
async def on_load_data():
    data = await fetch_data_async(server_bridge)  # Section 1
    filtered = filter_active_items(data)  # Section 2
    render_items(filtered)  # Section 3/4
```

### ❌ Hardcoded Values
```python
# BAD: Hardcoded dimensions and styles
ft.Container(width=300, height=200, bgcolor="#FF5733")
```

```python
# GOOD: Use constants and theme system
ft.Container(
    width=SEARCH_BAR_WIDTH,
    height=CARD_HEIGHT,
    bgcolor=ft.Colors.PRIMARY
)
```

### ❌ Global State Abuse
```python
# BAD: Using global variables for view state
global_search_query = ""
global_items_cache = []
```

```python
# GOOD: Encapsulate state in view closure
def create_view(server_bridge, page, state_manager):
    search_query = ""  # Local to view
    items_cache = []   # Local to view
    ...
```

---

## Conclusion

The 5-Section Pattern provides a clear, maintainable architecture for FletV2 views. By following this guide, you'll create views that are:

- **Testable**: Each section can be tested independently
- **Maintainable**: Clear separation of concerns makes changes easier
- **Consistent**: All views follow the same pattern
- **Reusable**: Sections can be extracted and shared across views

**Next Steps**: Start with a small view as practice, then progressively refactor larger views.

---

**Document Version**: 1.0
**Last Updated**: October 12, 2025
**Maintained By**: FletV2 Architecture Team
