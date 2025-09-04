# FletV2 View Creation Functions

## Overview

Each view in FletV2 is created using a consistent pattern with a `create_*_view` function. This document describes the standard interface and patterns used across all views.

## Standard Interface

All view creation functions follow the same signature:

```python
def create_view_name_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create view_name view using simple Flet patterns.
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The view_name view
    """
```

## Common Patterns

### 1. Data Retrieval

Views typically retrieve data using the server bridge:

```python
def get_view_data():
    """Get data from server bridge or return mock data."""
    if server_bridge:
        try:
            return server_bridge.get_view_data()
        except Exception as e:
            logger.warning(f"Failed to get data from server bridge: {e}")
    
    # Fallback to mock data
    return mock_data
```

### 2. Event Handlers

Event handlers are defined as inner functions:

```python
def on_button_click(e):
    """Handle button click event."""
    logger.info("Button clicked")
    # Perform action
    page.snack_bar = ft.SnackBar(
        content=ft.Text("Action completed"),
        bgcolor=ft.Colors.GREEN
    )
    page.snack_bar.open = True
    page.update()
```

### 3. Async Operations

For long-running operations, views use async patterns:

```python
async def async_operation():
    """Async function to perform long-running operation."""
    try:
        # Simulate async operation
        await asyncio.sleep(1.0)
        logger.info("Operation completed")
        return True
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return False

def on_action_click(e):
    """Handle action click with async operation."""
    async def async_handler():
        try:
            success = await async_operation()
            if success:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Operation completed successfully"),
                    bgcolor=ft.Colors.GREEN
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Operation failed"),
                    bgcolor=ft.Colors.RED
                )
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            logger.error(f"Error in async handler: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Error occurred"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()
    
    # Run async operation
    page.run_task(async_handler)
```

### 4. UI Components

Views use Flet's built-in components:

```python
# Create a card with consistent styling
card = ft.Card(
    content=ft.Container(
        content=ft.Column([
            ft.Text("Title", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Content", size=14)
        ], spacing=8),
        padding=16
    )
)

# Create a data table
table = ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text("Column 1", weight=ft.FontWeight.BOLD)),
        ft.DataColumn(ft.Text("Column 2", weight=ft.FontWeight.BOLD))
    ],
    rows=[
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Cell 1")),
                ft.DataCell(ft.Text("Cell 2"))
            ]
        )
    ]
)
```

## Available Views

### Dashboard View

- Provides server status overview
- Shows system metrics using psutil
- Includes quick action buttons
- Displays recent activity

### Clients View

- Lists connected clients
- Provides search and filter functionality
- Allows client management (disconnect, delete)
- Shows client details in dialogs

### Files View

- Lists files in the system
- Shows file details (size, type, modification date)
- Provides file operations (download, verify, delete)
- Includes search functionality

### Database View

- Shows database statistics
- Provides table browsing
- Allows data export
- Includes database management actions

### Analytics View

- Displays system performance metrics
- Shows charts using Flet's chart components
- Provides real-time data updates
- Includes system information

### Logs View

- Displays system logs
- Provides log filtering by level
- Allows log export
- Includes log clearing functionality

### Settings View

- Provides application configuration
- Allows theme switching
- Supports settings export/import
- Includes reset functionality

## Best Practices

1. **Use Flet's Built-in Components**: Leverage Flet's native components instead of creating custom ones
2. **Consistent Error Handling**: Use try/except blocks and provide user feedback
3. **Async Operations**: Use async/await for long-running operations to prevent UI freezing
4. **Logging**: Use the provided logger for debugging and monitoring
5. **Responsive Design**: Use ResponsiveRow for layouts that adapt to different screen sizes
6. **User Feedback**: Provide immediate feedback through SnackBar notifications
7. **Confirmation Dialogs**: Use dialogs for destructive actions