#!/usr/bin/env python3
"""
Simplified Database View - The Flet Way
~300 lines instead of 1,736 lines of framework fighting!

Core Principle: Use Flet's built-in DataTable, AlertDialog, and TextField.
Let Flet handle CRUD operations with simple, clean patterns.
"""

# Standard library imports
import json
import os
import sys
from datetime import datetime
from typing import Any

# Ensure repository and package roots are on sys.path for runtime resolution
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Third-party imports
import aiofiles
import flet as ft

# ALWAYS import this in any Python file that deals with subprocess or console I/O
import Shared.utils.utf8_solution as _  # noqa: F401

try:
    from FletV2.utils.debug_setup import get_logger
except ImportError:  # pragma: no cover - fallback logging
    import logging

    from FletV2 import config

    def get_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name or __name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if getattr(config, "DEBUG_MODE", False) else logging.WARNING)
        return logger
from FletV2.utils.server_bridge import ServerBridge
from FletV2.utils.state_manager import StateManager
from FletV2.utils.ui_components import create_status_pill, themed_button, themed_card, themed_metric_card
from FletV2.utils.user_feedback import show_error_message, show_success_message

logger = get_logger(__name__)


def create_database_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    _state_manager: StateManager | None = None
) -> Any:
    """Simple database view using Flet's built-in components."""
    logger.info("Creating simplified database view")

    # Simple state management
    selected_table = "clients"
    table_data = []
    filtered_data = []
    search_query = ""

    # Helper for a no-data placeholder table
    def load_data() -> None:
        """Load database data using server bridge."""
        nonlocal table_data, filtered_data

        if not server_bridge:
            logger.error("Server bridge not available")
            show_error_message(page, "Server not connected. Please start the backup server.")
            table_data = []
            filtered_data = []
            update_table()
            return

        try:
            result = server_bridge.get_table_data(selected_table)
            if not result.get('success'):
                logger.error(f"Failed to fetch data for {selected_table}: {result.get('error', 'Unknown error')}")
                show_error_message(page, f"Failed to load {selected_table} table: {result.get('error', 'Unknown error')}")
                table_data = []
                filtered_data = []
            else:
                # Ensure we handle both dict and list results consistently
                table_data = result.get('data', {}).get('rows', []) if isinstance(result.get('data'), dict) else result.get('data', [])
                logger.info(f"Loaded {len(table_data)} records for {selected_table}")
        except Exception as ex:
            logger.error(f"Exception while loading {selected_table} data: {ex}")
            show_error_message(page, f"Error loading {selected_table} table: {str(ex)}")
            table_data = []

        filtered_data = table_data.copy()
        update_table()

    # Apply search filter
    def apply_search() -> None:
        """Simple search filtering."""
        nonlocal filtered_data

        if search_query.strip():
            query = search_query.lower()
            filtered_data = [
                row for row in table_data
                if any(query in str(value).lower() for value in row.values())
            ]
        else:
            filtered_data = table_data.copy()

        update_table()

    def get_status_type(status: str) -> str:
        """Map database status to status pill type."""
        status_mapping = {
            "active": "success",        # Green for active records
            "connected": "success",     # Green for connected database
            "inactive": "error",        # Red for inactive records
            "pending": "warning",       # Orange for pending records
            "disconnected": "error",    # Red for disconnected database
            "unknown": "unknown"        # Light Blue Grey for unknown states
        }
        return status_mapping.get(status.lower(), "default")

    # Create DataTable using Flet's built-in functionality with enhanced header
    database_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("No Data")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("Loading...")),
                ft.DataCell(ft.Text(""))
            ])
        ],
        heading_row_color="#212121",  # Enhanced darker header as specified in document
        border_radius=12,
        expand=True
    )

    def update_table() -> None:
        """Update table using Flet's simple patterns."""
        if not filtered_data:
            # Always keep at least one column to prevent DataTable errors
            database_table.columns = [
                ft.DataColumn(ft.Text("No Data")),
                ft.DataColumn(ft.Text("Actions"))
            ]
            database_table.rows = [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("No data available")),
                    ft.DataCell(ft.Text(""))
                ])
            ]
            return

        # Set columns based on first row
        first_row = filtered_data[0]
        database_table.columns = [
            ft.DataColumn(ft.Text(str(key).title())) for key in first_row.keys()
        ]

        # Always add Actions column
        database_table.columns.append(ft.DataColumn(ft.Text("Actions")))

        # Set rows with status pill support
        database_table.rows = []
        for row in filtered_data:
            cells = []
            for key, value in row.items():
                if key.lower() == "status":
                    # Apply status pill for status columns
                    cells.append(ft.DataCell(create_status_pill(str(value), get_status_type(str(value)))))
                else:
                    # Regular text for other columns
                    cells.append(ft.DataCell(ft.Text(str(value))))

            # Add action button to each row
            cells.append(
                ft.DataCell(
                    ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        items=[
                            ft.PopupMenuItem(text="Edit", icon=ft.Icons.EDIT, on_click=lambda e, r=row: edit_record(r)),
                            ft.PopupMenuItem(text="Delete", icon=ft.Icons.DELETE, on_click=lambda e, r=row: delete_record(r)),
                        ]
                    )
                )
            )

            database_table.rows.append(ft.DataRow(cells=cells))

        # Add Actions column if not present
        if len(database_table.columns) == len(first_row.keys()):
            database_table.columns.append(ft.DataColumn(ft.Text("Actions")))

        database_table.update()

    # Edit record dialog using Flet's AlertDialog
    def edit_record(record: dict[str, Any]) -> None:
        """Edit record dialog with server integration."""
        if not server_bridge:
            show_error_message(page, "Server not connected. Please start the backup server.")
            return

        fields = {}

        # Create text fields for each editable column (skip id)
        field_controls = []
        for key, value in record.items():
            if key.lower() != 'id':
                field = ft.TextField(
                    label=str(key).title(),
                    value=str(value)
                )
                fields[key] = field
                field_controls.append(field)

        def save_changes(_e: ft.ControlEvent) -> None:
            """Save edited record via server bridge."""
            updated_record = record.copy()
            for key, field in fields.items():
                updated_record[key] = field.value

            try:
                result = server_bridge.update_table_record(selected_table, updated_record)
                if result.get('success'):
                    # Update local data with server-confirmed record
                    updated_record = result.get('data', updated_record)
                    for i, row in enumerate(table_data):
                        if row.get('id') == record.get('id'):
                            table_data[i] = updated_record
                            break

                    apply_search()  # Refresh the view
                    page.close(edit_dialog)
                    show_success_message(page, "Record updated successfully")
                else:
                    show_error_message(page, f"Failed to update record: {result.get('error', 'Unknown error')}")
            except Exception as ex:
                show_error_message(page, f"Error updating record: {str(ex)}")

        edit_dialog = ft.AlertDialog(
            title=ft.Text("Edit Record"),
            content=ft.Column(field_controls, height=300, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: page.close(edit_dialog)),
                ft.FilledButton("Save", on_click=save_changes),
            ],
        )

        page.open(edit_dialog)

    def delete_record(record: dict[str, Any]) -> None:
        """Delete record with server integration."""
        if not server_bridge:
            show_error_message(page, "Server not connected. Please start the backup server.")
            return

        def confirm_delete(_e: ft.ControlEvent) -> None:
            try:
                result = server_bridge.delete_table_record(selected_table, record.get('id'))
                if result.get('success'):
                    # Remove from local data after server confirms deletion
                    table_data[:] = [row for row in table_data if row.get('id') != record.get('id')]
                    apply_search()  # Refresh the view
                    page.close(delete_dialog)
                    show_success_message(page, "Record deleted successfully")
                else:
                    show_error_message(page, f"Failed to delete record: {result.get('error', 'Unknown error')}")
            except Exception as ex:
                show_error_message(page, f"Error deleting record: {str(ex)}")

        delete_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete this record?\n\nID: {record.get('id', 'N/A')}"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: page.close(delete_dialog)),
                ft.FilledButton("Delete", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED)),
            ],
        )

        page.open(delete_dialog)

    def add_record() -> None:
        """Add new record with server integration."""
        if not server_bridge:
            show_error_message(page, "Server not connected. Please start the backup server.")
            return

        if not table_data:
            show_error_message(page, "No table selected")
            return

        fields = {}
        field_controls = []

        # Create fields based on first row structure (skip id)
        first_row = table_data[0]
        for key in first_row.keys():
            if key.lower() != 'id':
                field = ft.TextField(label=str(key).title())
                fields[key] = field
                field_controls.append(field)

        def save_new_record(_e: ft.ControlEvent) -> None:
            """Save new record via server bridge."""
            # Prepare new record data
            new_record_data = {}
            for key, field in fields.items():
                new_record_data[key] = field.value

            try:
                result = server_bridge.add_table_record(selected_table, new_record_data)
                if result.get('success'):
                    # Use server-returned record to ensure consistency
                    new_record = result.get('data', new_record_data)
                    table_data.append(new_record)
                    apply_search()  # Refresh the view
                    page.close(add_dialog)
                    show_success_message(page, "Record added successfully")
                else:
                    show_error_message(page, f"Failed to add record: {result.get('error', 'Unknown error')}")
            except Exception as ex:
                show_error_message(page, f"Error adding record: {str(ex)}")

        add_dialog = ft.AlertDialog(
            title=ft.Text("Add New Record"),
            content=ft.Column(field_controls, height=300, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: page.close(add_dialog)),
                ft.FilledButton("Add", on_click=save_new_record),
            ],
        )

        page.open(add_dialog)

    # Table selector dropdown
    def on_table_change(e: ft.ControlEvent) -> None:
        """Handle table selection change."""
        nonlocal selected_table
        selected_table = e.control.value
        load_data()

    table_dropdown = ft.Dropdown(
        label="Select Table",
        value="clients",
        options=[
            ft.dropdown.Option("clients", "Clients"),
            ft.dropdown.Option("files", "Files"),
            ft.dropdown.Option("logs", "Logs"),
            ft.dropdown.Option("settings", "Settings"),
            ft.dropdown.Option("backups", "Backups"),
        ],
        on_change=on_table_change,
        width=200
    )

    # Search field
    def on_search_change(e: ft.ControlEvent) -> None:
        """Handle search input."""
        nonlocal search_query
        search_query = e.control.value
        apply_search()

    search_field = ft.TextField(
        label="Search records",
        prefix_icon=ft.Icons.SEARCH,
        on_change=on_search_change,
        width=300
    )

    # Export functionality using FilePicker
    async def save_as_json(e: ft.FilePickerResultEvent) -> None:
        """Export table data as JSON."""
        if e.path:
            try:
                async with aiofiles.open(e.path, 'w') as f:
                    await f.write(json.dumps(filtered_data, indent=2))
                show_success_message(page, f"Data exported to {e.path}")
            except Exception as ex:
                show_error_message(page, f"Export failed: {ex}")

    file_picker = ft.FilePicker(on_result=save_as_json)
    page.overlay.append(file_picker)

    def export_data(_e: ft.ControlEvent) -> None:
        """Export table data."""
        file_picker.save_file(
            dialog_title="Export Table Data",
            file_name=f"{selected_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"]
        )

    # Action buttons
    actions_row = ft.Row([
        table_dropdown,
        search_field,
        ft.Container(expand=True),  # Spacer
        themed_button("Add Record", lambda _e: add_record(), "filled", ft.Icons.ADD),
        themed_button("Export", export_data, "outlined", ft.Icons.DOWNLOAD),
        themed_button("Refresh", lambda _e: load_data(), "outlined", ft.Icons.REFRESH),
    ], spacing=10)

    # Database stats from server with error handling
    db_status = {"status": "Server not connected", "tables": 0, "total_records": 0, "size": "--"}
    if not server_bridge:
        logger.error("Server bridge not available for database info")
        show_error_message(page, "Server not connected. Cannot retrieve database statistics.")
    else:
        try:
            info_res = server_bridge.get_database_info()
            if not info_res.get('success'):
                logger.error(f"Failed to fetch database info: {info_res.get('error', 'Unknown error')}")
                show_error_message(page, f"Could not retrieve database statistics: {info_res.get('error', 'Unknown error')}")
                db_status["status"] = "Database info unavailable"
            else:
                db_status = info_res.get('data', db_status)
                logger.info(f"Database info retrieved successfully: {db_status}")
        except Exception as ex:
            logger.error(f"Exception while fetching database info: {ex}")
            show_error_message(page, f"Error retrieving database statistics: {str(ex)}")
            db_status["status"] = "Error fetching info"

    # Enhanced table with layered card design
    table_card = themed_card(database_table, "Database Records", page)

    # Main layout with responsive design and scrollbar
    main_content = ft.Column([
        ft.Text("Database Management", size=28, weight=ft.FontWeight.BOLD),
        # Responsive stats row
        ft.ResponsiveRow([
            ft.Column([themed_metric_card("Status", db_status["status"], ft.Icons.STORAGE)],
                     col={"sm": 12, "md": 6, "lg": 3}),
            ft.Column([themed_metric_card("Tables", str(db_status["tables"]), ft.Icons.TABLE_CHART)],
                     col={"sm": 12, "md": 6, "lg": 3}),
            ft.Column([themed_metric_card("Records", str(db_status["total_records"]), ft.Icons.STORAGE)],
                     col={"sm": 12, "md": 6, "lg": 3}),
            ft.Column([themed_metric_card("Size", db_status["size"], ft.Icons.FOLDER)],
                     col={"sm": 12, "md": 6, "lg": 3}),
        ]),
        actions_row,
        table_card
    ], expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)

    # Create the main container with theme support
    database_container = themed_card(main_content, None, page)  # No title since we have one in content

    def setup_subscriptions() -> None:
        """Setup subscriptions and initial data loading after view is added to page."""
        load_data()

    def dispose() -> None:
        """Clean up subscriptions and resources."""
        logger.debug("Disposing database view")
        # No subscriptions to clean up currently

    return database_container, dispose, setup_subscriptions
