# FletV2 Pattern Reference - Quick Guide

**Quick reference for common patterns when building FletV2 views.**

---

## Phase 1 Utilities Quick Reference

### Loading States (`from FletV2.utils.loading_states import *`)

```python
# Loading indicator
loading = create_loading_indicator("Loading data...")
container.content = loading

# Empty state
empty = create_empty_state(
    title="No Items Found",
    message="Try adjusting your filters",
    icon=ft.Icons.INBOX_OUTLINED
)

# Success notification
show_success_snackbar(page, "Operation completed successfully")

# Error notification
show_error_snackbar(page, "Operation failed: connection timeout")

# Generic snackbar
show_snackbar(page, "Custom message", bgcolor=ft.Colors.BLUE_400)
```

### Data Export (`from FletV2.utils.data_export import *`)

```python
# Export to JSON
export_to_json(data, "output.json", indent=2)

# Export to CSV
export_to_csv(data, "output.csv", fieldnames=["id", "name", "status"])

# Export to TXT with custom formatter
export_to_txt(data, "output.txt", format_func=lambda x: f"{x['name']}: {x['value']}")

# Generate timestamped filename
filename = generate_export_filename("logs", "json")  # logs_20251012_143022.json
```

### UI Builders (`from FletV2.utils.ui_builders import *`)

```python
# Search bar
search = create_search_bar(
    on_change=handle_search,
    placeholder="Search items...",
    width=300
)

# Filter dropdown
filter = create_filter_dropdown(
    label="Status",
    options=["All", "Active", "Inactive"],
    on_change=handle_filter,
    width=150
)

# Action button
btn = create_action_button(
    text="Refresh",
    on_click=handle_refresh,
    icon=ft.Icons.REFRESH_ROUNDED,
    primary=True  # False for secondary style
)

# Confirmation dialog
dialog = create_confirmation_dialog(
    title="Delete Item",
    message="Are you sure you want to delete this item?",
    on_confirm=handle_confirm,
    on_cancel=handle_cancel
)
```

### Async Helpers (`from FletV2.utils.async_helpers import *`)

```python
# Safe server call
result = safe_server_call(server_bridge, 'get_data', param1, param2)
if result.get('success'):
    data = result.get('data')

# Handle server result with user feedback
if handle_server_result(page, result, "Success!", "Operation failed"):
    # Success - do something
    pass

# Safe data loading with fallback
data = safe_load_data(server_bridge, 'get_items', fallback_data=[])

# Debounce async function
@debounce(0.5)  # 500ms delay
async def on_search_change(query: str):
    results = await search_database(query)
    display_results(results)
```

---

## Common Patterns

### Pattern 1: Data Loading with Loading State

```python
async def load_data():
    # Show loading
    loading_overlay.visible = True
    loading_overlay.update()

    try:
        # Fetch data
        data = await fetch_data_async(server_bridge)

        # Process data
        filtered = filter_data(data, current_filter)

        # Update UI
        render_items(filtered)
        show_success_snackbar(page, "Data loaded successfully")

    except Exception as ex:
        show_error_snackbar(page, f"Failed to load: {ex}")

    finally:
        loading_overlay.visible = False
        loading_overlay.update()
```

### Pattern 2: Search with Debounce

```python
# In view setup
search_bar = create_search_bar(
    on_change=lambda e: page.run_task(handle_search, e.data),
    placeholder="Search...",
    width=300
)

# Debounced search handler
@debounce(0.3)
async def handle_search(query: str):
    filtered_data = filter_by_search(all_data, query)
    render_items(filtered_data)
```

### Pattern 3: Export with User Feedback

```python
async def handle_export(e):
    try:
        # Get data to export
        data_to_export = get_current_filtered_data()

        # Generate filename
        filename = generate_export_filename("export", "json")

        # Export
        export_to_json(data_to_export, filename)

        show_success_snackbar(page, f"Exported to {filename}")

    except Exception as ex:
        show_error_snackbar(page, f"Export failed: {ex}")
```

### Pattern 4: Server Call with Error Handling

```python
async def perform_server_operation(item_id):
    # Call server
    result = safe_server_call(server_bridge, 'delete_item', item_id)

    # Handle result with automatic user feedback
    if handle_server_result(page, result, "Item deleted", "Delete failed"):
        # Success - refresh data
        await load_data()
```

### Pattern 5: Empty State with Action

```python
def render_items(items):
    if not items:
        # Show empty state with action
        items_list.controls = [
            create_empty_state(
                title="No Items",
                message="No items match your filters",
                icon=ft.Icons.INBOX_OUTLINED
            ),
            create_action_button(
                "Clear Filters",
                on_click=handle_clear_filters,
                icon=ft.Icons.CLEAR_ALL
            )
        ]
    else:
        # Show items
        items_list.controls = [build_item_card(item) for item in items]

    items_list.update()
```

---

## 5-Section Template (Minimal)

```python
#!/usr/bin/env python3
"""View Name - Description"""

import asyncio
import flet as ft
from typing import Any, Callable

# Phase 1 utilities
from FletV2.utils.loading_states import *
from FletV2.utils.data_export import *
from FletV2.utils.ui_builders import *
from FletV2.utils.async_helpers import *

# ===== SECTION 1: DATA FETCHING =====

def fetch_data_sync(server_bridge) -> list:
    result = safe_server_call(server_bridge, 'get_data')
    return result.get('data', []) if result.get('success') else []

async def fetch_data_async(server_bridge) -> list:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, fetch_data_sync, server_bridge)

# ===== SECTION 2: BUSINESS LOGIC =====

def filter_data(items: list, query: str) -> list:
    """Filter items by search query."""
    if not query:
        return items
    return [x for x in items if query.lower() in x['name'].lower()]

# ===== SECTION 3: UI COMPONENTS =====

def build_item_card(item: dict) -> ft.Control:
    """Build card for item display."""
    return ft.Container(
        content=ft.Text(item['name']),
        padding=16,
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_CONTAINER
    )

# ===== SECTION 4: EVENT HANDLERS =====

# Create handlers factory for closure access
def create_handlers(page, server_bridge, items_list_ref, current_items):

    async def on_refresh(e):
        items = await fetch_data_async(server_bridge)
        current_items.clear()
        current_items.extend(items)
        render_items()

    @debounce(0.3)
    async def on_search(query: str):
        filtered = filter_data(current_items, query)
        render_items(filtered)

    def render_items(items=None):
        items = items or current_items
        items_list_ref.current.controls = [build_item_card(x) for x in items]
        items_list_ref.current.update()

    return on_refresh, on_search, render_items

# ===== SECTION 5: MAIN VIEW =====

def create_view(server_bridge, page, state_manager):
    """Create the main view."""

    # State
    current_items = []

    # Refs
    items_list_ref = ft.Ref[ft.ListView]()

    # Handlers
    on_refresh, on_search, render_items = create_handlers(
        page, server_bridge, items_list_ref, current_items
    )

    # UI
    items_list = ft.ListView(ref=items_list_ref, expand=True)

    main_container = ft.Container(
        content=items_list,
        padding=20,
        expand=True
    )

    # Lifecycle
    def dispose():
        pass

    async def setup():
        items = await fetch_data_async(server_bridge)
        current_items.extend(items)
        render_items()

    return main_container, dispose, setup
```

---

## Before/After Examples

### Before: Custom Loading Indicator

```python
# OLD: 32 lines of custom code
loading_overlay = ft.Container(
    content=ft.Column([
        ft.Container(
            content=ft.ProgressRing(
                width=40,
                height=40,
                stroke_width=4,
                color=ft.Colors.PRIMARY,
            ),
            width=80,
            height=80,
            bgcolor=ft.Colors.SURFACE,
            border_radius=40,
            alignment=ft.alignment.center,
            shadow=NeomorphicShadows.get_card_shadows("high"),
        ),
        ft.Container(height=16),
        ft.Text(
            "Loading...",
            size=14,
            color=ft.Colors.ON_SURFACE_VARIANT,
            weight=ft.FontWeight.W_500,
        ),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    bgcolor=ft.Colors.with_opacity(0.96, ft.Colors.SURFACE),
    alignment=ft.alignment.center,
    visible=False,
    padding=50,
)
```

```python
# NEW: 1 line with Phase 1 utility
loading_overlay = create_loading_indicator("Loading...")
loading_overlay.visible = False
```

### Before: Custom Export Logic

```python
# OLD: 45 lines of inline export
def perform_export(e):
    try:
        export_dir = os.path.join(_repo_root, "exports")
        os.makedirs(export_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if export_format == "json":
            filepath = os.path.join(export_dir, f"data_{timestamp}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif export_format == "csv":
            filepath = os.path.join(export_dir, f"data_{timestamp}.csv")
            with open(filepath, "w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

        show_toast(page, f"Exported to {filepath}", "success")
    except Exception as ex:
        show_toast(page, f"Export failed: {ex}", "error")
```

```python
# NEW: 8 lines with Phase 1 utilities
async def perform_export(e):
    try:
        filename = generate_export_filename("data", "json")
        export_to_json(data, filename)
        show_success_snackbar(page, f"Exported to {filename}")
    except Exception as ex:
        show_error_snackbar(page, f"Export failed: {ex}")
```

---

## Testing Patterns

### Test Section 1: Data Fetching

```python
def test_fetch_data_sync():
    # Mock server bridge
    mock_bridge = Mock()
    mock_bridge.get_data.return_value = {'success': True, 'data': [{'id': 1}]}

    # Test
    result = fetch_data_sync(mock_bridge)

    # Assert
    assert len(result) == 1
    assert result[0]['id'] == 1
```

### Test Section 2: Business Logic

```python
def test_filter_data():
    # Setup
    items = [
        {'id': 1, 'name': 'Apple'},
        {'id': 2, 'name': 'Banana'},
        {'id': 3, 'name': 'Cherry'},
    ]

    # Test
    result = filter_data(items, 'an')

    # Assert
    assert len(result) == 1
    assert result[0]['name'] == 'Banana'
```

---

## Performance Tips

### 1. Use Targeted Updates
```python
# BAD: Full page update
page.update()

# GOOD: Update only the control that changed
items_list.update()
```

### 2. Batch Updates
```python
# BAD: Update after each item
for item in items:
    list.controls.append(build_card(item))
    list.update()  # N updates

# GOOD: Batch all changes
list.controls = [build_card(item) for item in items]
list.update()  # 1 update
```

### 3. Use Visibility Instead of Recreating
```python
# BAD: Recreate controls
loading_overlay = create_loading_indicator()

# GOOD: Toggle visibility
loading_overlay.visible = True
loading_overlay.update()
```

---

## Common Mistakes

### ❌ Awaiting Non-Async Functions
```python
# WRONG
result = await server_bridge.get_data()  # ServerBridge methods are sync!

# CORRECT
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(None, server_bridge.get_data)
```

### ❌ Not Using Phase 1 Utilities
```python
# WRONG: Custom implementation
page.snack_bar = ft.SnackBar(content=ft.Text("Success"))
page.snack_bar.open = True
page.update()

# CORRECT: Use utility
show_success_snackbar(page, "Success")
```

### ❌ Mixing Concerns
```python
# WRONG: Data fetching + UI in one function
def load_and_display():
    data = server_bridge.get_data()
    list.controls = [build_card(x) for x in data]
    list.update()

# CORRECT: Separate concerns
async def load_data():
    data = await fetch_data_async(server_bridge)
    render_items(data)
```

---

**Quick Reference v1.0** | Last Updated: October 12, 2025
