#!/usr/bin/env python3
"""
Simplified Database View - The Flet Way
~300 lines instead of 1,736 lines of framework fighting!

Core Principle: Use Flet's built-in DataTable, AlertDialog, and TextField.
Let Flet handle CRUD operations with simple, clean patterns.
"""

import flet as ft
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.ui_components import themed_card, themed_button, themed_metric_card, create_status_pill
from utils.user_feedback import show_success_message, show_error_message

logger = get_logger(__name__)


def create_database_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    _state_manager: StateManager
) -> ft.Control:
    """Simple database view using Flet's built-in components."""
    logger.info("Creating simplified database view")

    # Simple state management
    selected_table = "clients"
    table_data = []
    filtered_data = []
    search_query = ""

    # Mock database info for demonstration
    def get_mock_db_info():
        """Simple database info generator."""
        return {
            "status": "Connected",
            "tables": 5,
            "total_records": 1247,
            "size": "15.3 MB"
        }

    # Mock table data generator
    def get_mock_table_data(table_name: str) -> List[Dict[str, Any]]:
        """Simple table data generator."""
        if table_name == "clients":
            return [
                {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "status": "Active", "created": "2024-01-15"},
                {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "status": "Inactive", "created": "2024-01-10"},
                {"id": 3, "name": "Carol Davis", "email": "carol@example.com", "status": "Active", "created": "2024-01-20"},
                {"id": 4, "name": "David Wilson", "email": "david@example.com", "status": "Pending", "created": "2024-01-25"},
                {"id": 5, "name": "Eve Brown", "email": "eve@example.com", "status": "Active", "created": "2024-01-30"},
            ]
        elif table_name == "files":
            return [
                {"id": 1, "filename": "document1.pdf", "size": "2.5 MB", "type": "PDF", "uploaded": "2024-01-15"},
                {"id": 2, "filename": "image.jpg", "size": "1.2 MB", "type": "Image", "uploaded": "2024-01-16"},
                {"id": 3, "filename": "archive.zip", "size": "5.8 MB", "type": "Archive", "uploaded": "2024-01-17"},
            ]
        else:
            return [
                {"id": 1, "column1": "Value 1", "column2": "Data A", "column3": "Info X"},
                {"id": 2, "column1": "Value 2", "column2": "Data B", "column3": "Info Y"},
                {"id": 3, "column1": "Value 3", "column2": "Data C", "column3": "Info Z"},
            ]

    # Load data from server or use mock
    def load_data():
        """Load database data using server bridge or mock."""
        nonlocal table_data, filtered_data

        if server_bridge:
            try:
                result = server_bridge.get_table_data(selected_table)
                if result.get('success'):
                    table_data = result.get('data', [])
                else:
                    table_data = get_mock_table_data(selected_table)
            except Exception:
                table_data = get_mock_table_data(selected_table)
        else:
            table_data = get_mock_table_data(selected_table)

        filtered_data = table_data.copy()
        update_table()

    # Apply search filter
    def apply_search():
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

    def update_table():
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
    def edit_record(record: Dict[str, Any]):
        """Simple edit dialog using AlertDialog."""
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

        def save_changes(_e):
            """Save edited record."""
            # Update the record with new values
            updated_record = record.copy()
            for key, field in fields.items():
                updated_record[key] = field.value

            # Update in data
            for i, row in enumerate(table_data):
                if row.get('id') == record.get('id'):
                    table_data[i] = updated_record
                    break

            apply_search()  # Refresh the view
            page.close(edit_dialog)
            show_success_message(page, f"Record updated successfully")

        edit_dialog = ft.AlertDialog(
            title=ft.Text("Edit Record"),
            content=ft.Column(field_controls, height=300, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: page.close(edit_dialog)),
                ft.FilledButton("Save", on_click=save_changes),
            ],
        )

        page.open(edit_dialog)

    # Delete record dialog using Flet's AlertDialog
    def delete_record(record: Dict[str, Any]):
        """Simple delete confirmation dialog."""
        def confirm_delete(_e):
            # Remove from data
            table_data[:] = [row for row in table_data if row.get('id') != record.get('id')]
            apply_search()  # Refresh the view
            page.close(delete_dialog)
            show_success_message(page, f"Record deleted successfully")

        delete_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete this record?\n\nID: {record.get('id', 'N/A')}"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: page.close(delete_dialog)),
                ft.FilledButton("Delete", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED)),
            ],
        )

        page.open(delete_dialog)

    # Add new record dialog
    def add_record():
        """Simple add record dialog."""
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

        def save_new_record(_e):
            """Save new record."""
            # Create new record
            new_record = {}

            # Generate new ID
            max_id = max([row.get('id', 0) for row in table_data], default=0)
            new_record['id'] = max_id + 1

            # Add field values
            for key, field in fields.items():
                new_record[key] = field.value

            table_data.append(new_record)
            apply_search()  # Refresh the view
            page.close(add_dialog)
            show_success_message(page, f"Record added successfully")

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
    def on_table_change(e):
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
    def on_search_change(e):
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
    def save_as_json(e: ft.FilePickerResultEvent):
        """Export table data as JSON."""
        if e.path:
            try:
                with open(e.path, 'w') as f:
                    json.dump(filtered_data, f, indent=2)
                show_success_message(page, f"Data exported to {e.path}")
            except Exception as ex:
                show_error_message(page, f"Export failed: {ex}")

    file_picker = ft.FilePicker(on_result=save_as_json)
    page.overlay.append(file_picker)

    def export_data(_e):
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

    # Database stats using simple metric cards
    db_info = get_mock_db_info()
    stats_row = ft.Row([
        themed_metric_card("Status", db_info["status"], ft.Icons.STORAGE),
        themed_metric_card("Tables", str(db_info["tables"]), ft.Icons.TABLE_CHART),
        themed_metric_card("Records", str(db_info["total_records"]), ft.Icons.STORAGE),
        themed_metric_card("Size", db_info["size"], ft.Icons.FOLDER),
    ], spacing=10)

    # Enhanced table with layered card design
    table_card = themed_card(database_table, "Database Records", page)

    # Main layout with responsive design and scrollbar
    main_content = ft.Column([
        ft.Text("Database Management", size=28, weight=ft.FontWeight.BOLD),
        # Responsive stats row
        ft.ResponsiveRow([
            ft.Column([themed_metric_card("Status", db_info["status"], ft.Icons.STORAGE)],
                     col={"sm": 12, "md": 6, "lg": 3}),
            ft.Column([themed_metric_card("Tables", str(db_info["tables"]), ft.Icons.TABLE_CHART)],
                     col={"sm": 12, "md": 6, "lg": 3}),
            ft.Column([themed_metric_card("Records", str(db_info["total_records"]), ft.Icons.STORAGE)],
                     col={"sm": 12, "md": 6, "lg": 3}),
            ft.Column([themed_metric_card("Size", db_info["size"], ft.Icons.FOLDER)],
                     col={"sm": 12, "md": 6, "lg": 3}),
        ]),
        actions_row,
        table_card
    ], expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)

    # Create the main container with theme support
    database_container = themed_card(main_content, None, page)  # No title since we have one in content

    def setup_subscriptions():
        """Setup subscriptions and initial data loading after view is added to page."""
        load_data()

    def dispose():
        """Clean up subscriptions and resources."""
        logger.debug("Disposing database view")
        # No subscriptions to clean up currently

    return database_container, dispose, setup_subscriptions