"""
Simple Database View - Minimal complexity to avoid browser crashes.

Design Philosophy:
- Use ONLY simple Flet controls (Text, TextField, Dropdown, Button)
- NO DataTable, NO ListView, NO complex nested Cards
- Display records as simple Text lines
- Pagination to limit records displayed
- Async data loading to avoid UI blocking
"""

import flet as ft
from typing import Any
import logging

logger = logging.getLogger(__name__)


def create_database_view(
    server_bridge: Any,
    page: ft.Page,
    state_manager: Any = None
) -> tuple:
    """Create a simple database view that won't crash the browser."""

    # State management
    current_table = "clients"
    current_page_num = 0
    records_per_page = 15
    all_records = []

    # UI components (will be updated dynamically)
    status_text = ft.Text("Ready", size=14, color=ft.Colors.GREY_400)
    table_dropdown = ft.Dropdown(
        label="Select Table",
        value="clients",
        options=[
            ft.dropdown.Option("clients", "Clients"),
            ft.dropdown.Option("files", "Files"),
        ],
        width=200,
    )
    search_field = ft.TextField(
        label="Search",
        hint_text="Search records...",
        width=300,
    )
    records_display = ft.Column(
        [ft.Text("Click 'Load Data' to display records", italic=True, color=ft.Colors.GREY_500)],
        scroll=ft.ScrollMode.AUTO,
        spacing=5,
    )
    page_indicator = ft.Text("Page 0 of 0", size=14, weight=ft.FontWeight.BOLD)

    def update_records_display():
        """Update the records display with simple Text controls."""
        nonlocal records_display, page_indicator

        if not all_records:
            records_display.controls = [
                ft.Text("No records found", italic=True, color=ft.Colors.GREY_500)
            ]
            page_indicator.value = "Page 0 of 0"
            records_display.update()
            page_indicator.update()
            return

        # Calculate pagination
        total_pages = (len(all_records) - 1) // records_per_page + 1
        start_idx = current_page_num * records_per_page
        end_idx = min(start_idx + records_per_page, len(all_records))
        page_records = all_records[start_idx:end_idx]

        # Create simple Text controls for each record
        record_controls = []
        for i, record in enumerate(page_records, start=start_idx + 1):
            # Format record as simple text line
            if current_table == "clients":
                text = f"{i}. ID: {record.get('id', 'N/A')} | Name: {record.get('name', 'Unknown')} | IP: {record.get('ip_address', 'N/A')} | Last: {record.get('last_connection', 'Never')}"
            else:  # files table
                text = f"{i}. ID: {record.get('id', 'N/A')} | Name: {record.get('filename', 'Unknown')} | Size: {record.get('size', 0)} bytes | Client: {record.get('client_id', 'N/A')}"

            record_controls.append(
                ft.Text(
                    text,
                    size=13,
                    selectable=True,
                    color=ft.Colors.ON_SURFACE,
                )
            )

        records_display.controls = record_controls
        page_indicator.value = f"Page {current_page_num + 1} of {total_pages}"

        # Update UI
        records_display.update()
        page_indicator.update()

    async def load_data_async():
        """Load data from server asynchronously."""
        nonlocal all_records, current_page_num

        status_text.value = f"Loading {current_table}..."
        status_text.update()

        try:
            if not server_bridge:
                all_records = []
                status_text.value = "Server not connected (GUI-only mode)"
                status_text.color = ft.Colors.ORANGE_400
                status_text.update()
                update_records_display()
                return

            # Fetch data from server
            result = await server_bridge.get_table_data_async(current_table)

            if result.get('success'):
                # Extract records (handle both dict and list formats)
                data = result.get('data', {})
                all_records = data.get('rows', []) if isinstance(data, dict) else data

                # Reset to first page
                current_page_num = 0

                status_text.value = f"Loaded {len(all_records)} records from {current_table}"
                status_text.color = ft.Colors.GREEN_400
                logger.info(f"Successfully loaded {len(all_records)} records from {current_table}")
            else:
                all_records = []
                error_msg = result.get('error', 'Unknown error')
                status_text.value = f"Error: {error_msg}"
                status_text.color = ft.Colors.ERROR
                logger.error(f"Failed to load {current_table}: {error_msg}")

        except Exception as e:
            all_records = []
            status_text.value = f"Exception: {str(e)}"
            status_text.color = ft.Colors.ERROR
            logger.exception(f"Exception loading {current_table}")

        status_text.update()
        update_records_display()

    def on_table_change(e):
        """Handle table selection change."""
        nonlocal current_table
        current_table = table_dropdown.value
        page.run_task(load_data_async)

    table_dropdown.on_change = on_table_change

    def on_load_click(e):
        """Handle load button click."""
        page.run_task(load_data_async)

    def on_prev_page(e):
        """Go to previous page."""
        nonlocal current_page_num
        if current_page_num > 0:
            current_page_num -= 1
            update_records_display()

    def on_next_page(e):
        """Go to next page."""
        nonlocal current_page_num
        total_pages = (len(all_records) - 1) // records_per_page + 1
        if current_page_num < total_pages - 1:
            current_page_num += 1
            update_records_display()

    def on_search(e):
        """Filter records based on search query."""
        nonlocal all_records, current_page_num
        query = search_field.value.lower().strip()

        if not query:
            # Reset to show all records
            page.run_task(load_data_async)
            return

        # Simple text-based filtering
        filtered = []
        for record in all_records:
            # Convert record to string and search
            record_str = str(record).lower()
            if query in record_str:
                filtered.append(record)

        all_records = filtered
        current_page_num = 0
        status_text.value = f"Found {len(filtered)} matching records"
        status_text.color = ft.Colors.BLUE_400
        status_text.update()
        update_records_display()

    search_field.on_submit = on_search

    # Build the UI
    content = ft.Container(
        content=ft.Column([
            # Header
            ft.Text("Database Management", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

            # Status
            status_text,

            # Controls row
            ft.Row([
                table_dropdown,
                search_field,
                ft.ElevatedButton("Load Data", on_click=on_load_click, icon=ft.Icons.REFRESH),
            ], spacing=10),

            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

            # Records display
            ft.Container(
                content=records_display,
                height=400,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=8,
                padding=10,
            ),

            # Pagination controls
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=on_prev_page,
                    tooltip="Previous page"
                ),
                page_indicator,
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=on_next_page,
                    tooltip="Next page"
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),

        ], spacing=15, scroll=ft.ScrollMode.AUTO),
        padding=20,
    )

    def dispose():
        """Cleanup resources."""
        pass

    async def setup():
        """Setup function - load initial data."""
        await load_data_async()

    return content, dispose, setup
