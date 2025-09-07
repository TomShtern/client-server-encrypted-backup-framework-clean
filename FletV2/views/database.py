#!/usr/bin/env python3
"""
Database View for FletV2
Enhanced with reactive state management and optimized data loading.
"""

import flet as ft
from typing import Dict, Any
import asyncio
import csv
import os
from utils.debug_setup import get_logger
from utils.user_feedback import show_success_message, show_error_message, show_info_message
from datetime import datetime

logger = get_logger(__name__)


def create_database_view(server_bridge, page: ft.Page, state_manager=None) -> ft.Control:
    """
    Create database view with enhanced infrastructure and reactive state management.

    Args:
        server_bridge: Enhanced server bridge for data access
        page: Flet page instance
        state_manager: Reactive state manager for cross-view data sharing

    Returns:
        ft.Control: The database view
    """
    logger.info("Creating database view with enhanced infrastructure")

    # State variables for local UI management
    selected_table_name = "clients"
    search_query = ""
    column_filters = {}
    is_loading = False

    # Control references for direct updates
    status_text_ref = ft.Ref[ft.Text]()
    tables_text_ref = ft.Ref[ft.Text]()
    records_text_ref = ft.Ref[ft.Text]()
    size_text_ref = ft.Ref[ft.Text]()
    table_info_text_ref = ft.Ref[ft.Text]()
    rows_count_text_ref = ft.Ref[ft.Text]()
    last_updated_text_ref = ft.Ref[ft.Text]()
    table_container_ref = ft.Ref[ft.Container]()

    def get_current_table_data():
        """Get current table data from state manager or fallback to mock data."""
        # Try to get from state manager first
        if state_manager:
            cached_data = state_manager.get_cached(f"table_data_{selected_table_name}", max_age_seconds=60)
            if cached_data:
                logger.debug(f"Using cached table data for {selected_table_name}")
                return cached_data
        
        # Fallback to mock data since we can't await here
        logger.debug(f"Using mock data for table {selected_table_name}")
        return get_mock_table_data(selected_table_name)

    def get_mock_table_data(table_name: str) -> Dict[str, Any]:
        """Fallback mock data for development/testing."""
        mock_data = {
            "clients": {
                "columns": ["id", "name", "address", "status", "last_seen", "files_count"],
                "rows": [
                    {"id": "client_001", "name": "Alpha Workstation", "address": "192.168.1.100", "status": "Connected", "last_seen": "2025-09-07 10:30:15", "files_count": 42},
                    {"id": "client_002", "name": "Beta Server", "address": "192.168.1.101", "status": "Connected", "last_seen": "2025-09-07 10:25:22", "files_count": 128},
                    {"id": "client_003", "name": "Gamma Laptop", "address": "192.168.1.102", "status": "Offline", "last_seen": "2025-09-06 14:22:10", "files_count": 23}
                ]
            },
            "files": {
                "columns": ["id", "filename", "path", "size", "modified", "client_id", "verified"],
                "rows": [
                    {"id": "file_001", "filename": "document.pdf", "path": "/docs/document.pdf", "size": "2.4 MB", "modified": "2025-09-07 09:15:30", "client_id": "client_001", "verified": True},
                    {"id": "file_002", "filename": "image.jpg", "path": "/media/image.jpg", "size": "5.1 MB", "modified": "2025-09-07 08:45:20", "client_id": "client_002", "verified": True}
                ]
            },
            "logs": {
                "columns": ["id", "timestamp", "level", "component", "message"],
                "rows": [
                    {"id": 1, "timestamp": "2025-09-07 10:30:15", "level": "INFO", "component": "Server", "message": "Database connection established"},
                    {"id": 2, "timestamp": "2025-09-07 10:29:22", "level": "INFO", "component": "Client", "message": "Client client_001 connected successfully"}
                ]
            }
        }
        return mock_data.get(table_name, {"columns": [], "rows": []})

    async def get_table_data_from_bridge(table_name: str) -> Dict[str, Any]:
        """Get table data from enhanced server bridge."""
        if not server_bridge:
            logger.warning("No server bridge available - using fallback mock data")
            return get_mock_table_data(table_name)
        
        try:
            # Enhanced server bridge supports async methods
            if hasattr(server_bridge, 'get_table_data') and asyncio.iscoroutinefunction(getattr(server_bridge, 'get_table_data', None)):
                data = await server_bridge.get_table_data(table_name)
            elif hasattr(server_bridge, 'get_table_data'):
                data = server_bridge.get_table_data(table_name)
            else:
                logger.warning(f"Server bridge does not support get_table_data - using mock data")
                data = get_mock_table_data(table_name)
            
            # Update state manager cache
            if state_manager and data:
                await state_manager.update_state(f"table_data_{table_name}", data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting table data from server bridge: {e}")
            return get_mock_table_data(table_name)

    def filter_table_data():
        """Filter table data based on search query and column filters."""
        current_table_data = get_current_table_data()
        
        # Ensure we have valid data structure
        if not current_table_data or not isinstance(current_table_data, dict):
            logger.warning("No valid table data available for filtering")
            return {"columns": [], "rows": []}
            
        if not current_table_data.get("rows") or not current_table_data.get("columns"):
            logger.warning("Table data missing rows or columns")
            return {"columns": current_table_data.get("columns", []), "rows": []}

        filtered_rows = current_table_data["rows"]

        # Apply search filter across all columns
        if search_query.strip():
            query = search_query.lower().strip()
            filtered_rows = [
                row for row in filtered_rows
                if any(
                    query in str(value).lower()
                    for value in row.values()
                    if value is not None
                )
            ]

        # Apply column-specific filters
        for column_name, filter_value in column_filters.items():
            if filter_value.strip():
                filter_text = filter_value.lower().strip()
                filtered_rows = [
                    row for row in filtered_rows
                    if column_name in row and
                    row[column_name] is not None and
                    filter_text in str(row[column_name]).lower()
                ]

        # Return filtered data
        return {
            "columns": current_table_data["columns"],
            "rows": filtered_rows
        }


    def update_table_content():
        """Update the table content with filtered data."""
        filtered_data = filter_table_data()
        logger.info(f"Updating table content for {selected_table_name} - rows: {len(filtered_data.get('rows', []))}")
        
        if not filtered_data or not filtered_data.get("columns") or not filtered_data.get("rows"):
            logger.warning(f"No data available for table {selected_table_name}")
            empty_content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.TABLE_VIEW, size=64, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(
                        "No records found in the selected table.",
                        size=14,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16
                ),
                alignment=ft.alignment.center,
                height=300
            )
            if table_container_ref.current:
                logger.info("Setting empty content in table container")
                table_container_ref.current.content = empty_content
                table_container_ref.current.update()
            else:
                logger.error("table_container_ref.current is None - cannot show empty state")
            return
        
        # Create data table with current data
        logger.info(f"Creating data table with {len(filtered_data['rows'])} rows and {len(filtered_data['columns'])} columns")
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(col.replace("_", " ").title(), weight=ft.FontWeight.BOLD))
                for col in filtered_data["columns"]
            ] + [
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row.get(col, ""))))
                        for col in filtered_data["columns"]
                    ] + [
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Edit",
                                    icon_size=16,
                                    on_click=lambda e, r=row: [logger.info(f"Edit row: {r.get('id', 'unknown')}"), on_edit_row(e, r)]
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="Delete",
                                    icon_size=16,
                                    icon_color=ft.Colors.RED,
                                    on_click=lambda e, r=row: [logger.info(f"Delete row: {r.get('id', 'unknown')}"), on_delete_row(e, r)]
                                )
                            ], spacing=5)
                        )
                    ]
                )
                for row in filtered_data["rows"]
            ],
            heading_row_color=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            data_row_min_height=45,
            column_spacing=20
        )

        if table_container_ref.current:
            logger.info("Successfully setting data table in container")
            table_container_ref.current.content = data_table
            table_container_ref.current.update()
        else:
            logger.error("table_container_ref.current is None - cannot update table display")

    async def load_database_info_async():
        """Load database info and update UI with enhanced infrastructure."""
        nonlocal is_loading

        if is_loading:
            logger.debug("Database info loading already in progress")
            return

        is_loading = True
        logger.info("Loading database info with enhanced infrastructure")
        
        try:
            # Load database info from server bridge or state manager
            db_info = None
            
            # Check state manager cache first
            if state_manager:
                db_info = state_manager.get_cached("database_info", max_age_seconds=30)
                if db_info:
                    logger.debug("Using cached database info from state manager")

            # If no cached data, fetch from server bridge
            if not db_info and server_bridge:
                try:
                    if hasattr(server_bridge, 'get_database_info') and asyncio.iscoroutinefunction(getattr(server_bridge, 'get_database_info', None)):
                        db_info = await server_bridge.get_database_info()
                    elif hasattr(server_bridge, 'get_database_info'):
                        db_info = server_bridge.get_database_info()
                    
                    # Cache the result in state manager
                    if state_manager and db_info:
                        await state_manager.update_state("database_info", db_info)
                        
                except Exception as e:
                    logger.warning(f"Server bridge database info failed: {e}")

            # Fallback to mock data if no server bridge data
            if not db_info:
                logger.warning("Using fallback database info")
                db_info = {
                    "status": "Mock Mode",
                    "tables": 3,
                    "records": 173,
                    "size": "12.4 MB"
                }
                # Cache fallback data too
                if state_manager:
                    await state_manager.update_state("database_info", db_info)

            # Load initial table data
            try:
                current_table_data = await get_table_data_from_bridge(selected_table_name)
            except Exception as e:
                logger.warning(f"Failed to get table data: {e}")
                current_table_data = get_mock_table_data(selected_table_name)

            # Update timestamp
            last_updated = datetime.now()
            if last_updated_text_ref.current:
                last_updated_text_ref.current.value = f"Last updated: {last_updated.strftime('%H:%M:%S')}"
                last_updated_text_ref.current.update()

            # Update UI components with precise control updates
            if status_text_ref.current:
                status = db_info.get("status", "Unknown")
                status_text_ref.current.value = status
                status_text_ref.current.color = ft.Colors.GREEN if status == "Connected" else (ft.Colors.BLUE if "Mock" in status else ft.Colors.RED)
                status_text_ref.current.update()

            if tables_text_ref.current:
                tables_text_ref.current.value = str(db_info.get("tables", 0))
                tables_text_ref.current.update()

            if records_text_ref.current:
                records_text_ref.current.value = str(db_info.get("records", 0))
                records_text_ref.current.update()

            if size_text_ref.current:
                size_text_ref.current.value = db_info.get("size", "0 MB")
                size_text_ref.current.update()

            # Calculate row count once for reuse
            row_count = len(current_table_data.get("rows", []))
            
            if rows_count_text_ref.current:
                rows_count_text_ref.current.value = f"{row_count} rows"
                rows_count_text_ref.current.update()

            if table_info_text_ref.current:
                table_info_text_ref.current.value = f"Table: {selected_table_name}"
                table_info_text_ref.current.update()

            # Update table content
            update_table_content()

            logger.info(f"Database info loaded successfully - {db_info.get('status')} with {row_count} rows in {selected_table_name}")

        except Exception as e:
            logger.error(f"Error loading database info: {e}")
            show_error_message(page, f"Failed to load database info: {str(e)}")
        finally:
            is_loading = False

    # Setup state subscriptions for real-time updates if state manager available
    if state_manager:
        def on_database_state_change(new_data, old_data):
            """React to database state changes from other views."""
            logger.debug("Database state changed - refreshing view")
            page.run_task(load_database_info_async)
        
        # Subscribe to database-related state changes
        state_manager.subscribe("database_info", on_database_state_change)
        logger.info("Database view subscribed to state manager updates")

    def on_table_select(e):
        """Handle table selection change with enhanced infrastructure."""
        nonlocal selected_table_name, column_filters
        selected_table_name = e.control.value
        logger.info(f"Selected table: {selected_table_name}")

        async def load_table_async():
            try:
                # Clear column filters for new table
                column_filters = {}

                # Load new table data
                current_table_data = await get_table_data_from_bridge(selected_table_name)

                # Update table info and content with precise control updates
                if table_info_text_ref.current:
                    table_info_text_ref.current.value = f"Table: {selected_table_name}"
                    table_info_text_ref.current.update()

                if rows_count_text_ref.current:
                    row_count = len(current_table_data.get('rows', []))
                    rows_count_text_ref.current.value = f"{row_count} rows"
                    rows_count_text_ref.current.update()

                # Update table content display
                update_table_content()

                show_info_message(page, f"Switched to table: {selected_table_name}")
                logger.info(f"Table switched successfully to {selected_table_name} with {row_count} rows")

            except Exception as e:
                logger.error(f"Error loading table data: {e}")
                show_error_message(page, f"Failed to load table {selected_table_name}: {str(e)}")

        # Run async table loading
        page.run_task(load_table_async)

    def on_search_change(e):
        """Handle search input changes."""
        nonlocal search_query
        search_query = e.control.value
        logger.info(f"Search query changed to: '{search_query}'")
        update_table_content()

    def on_column_filter_change(column_name, e):
        """Handle column filter changes."""
        nonlocal column_filters
        column_filters[column_name] = e.control.value
        logger.info(f"Column filter '{column_name}' changed to: '{e.control.value}'")
        update_table_content()

    def on_refresh_table(e):
        """Handle table refresh."""
        logger.info(f"Refreshing table: {selected_table_name}")
        page.run_task(load_database_info_async)
        show_info_message(page, "Refreshing database info...")

    async def export_table_async(table_name: str) -> bool:
        """Export table data to CSV with progress indication."""
        try:
            # Get table data
            table_data = filter_table_data()

            if not table_data or not table_data.get("columns") or not table_data.get("rows"):
                logger.warning(f"No data to export for table: {table_name}")
                return False

            # Create export filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"{table_name}_export_{timestamp}.csv"

            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(exports_dir):
                os.makedirs(exports_dir)

            # Create full export path
            export_path = os.path.join(exports_dir, export_filename)

            # Show progress dialog
            progress_ring = ft.ProgressRing(width=40, height=40)
            progress_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Exporting Table Data"),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"Exporting {table_name} table to CSV..."),
                        ft.Container(height=20),
                        ft.Row([
                            progress_ring,
                            ft.Container(width=20),
                            ft.Text("Processing data...", size=14)
                        ], alignment=ft.MainAxisAlignment.CENTER)
                    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=300,
                    height=150
                ),
                actions_alignment=ft.MainAxisAlignment.CENTER
            )

            page.dialog = progress_dialog
            progress_dialog.open = True
            page.update()

            # Simulate progress updates
            total_rows = len(table_data["rows"])
            progress_text = ft.Text("Preparing export...", size=14)
            progress_dialog.content.content.controls[2].controls[2] = progress_text
            page.update()

            # Write CSV file with progress simulation
            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(table_data["columns"])
                progress_text.value = "Writing header..."
                page.update()

                # Write rows with progress updates
                for i, row in enumerate(table_data["rows"]):
                    row_data = [str(row.get(col, "")) for col in table_data["columns"]]
                    writer.writerow(row_data)

                    # Update progress every 10% or so
                    if (i + 1) % max(1, total_rows // 10) == 0:
                        progress_percent = int((i + 1) / total_rows * 100)
                        progress_text.value = f"Exporting... {progress_percent}% ({i + 1}/{total_rows} rows)"
                        page.update()

                        # Small delay to show progress
                        await asyncio.sleep(0.01)

                progress_text.value = "Finalizing export..."
                page.update()

            # Close progress dialog
            progress_dialog.open = False
            page.update()

            logger.info(f"Exported table {table_name} to {export_path}")
            return True
        except Exception as e:
            # Close progress dialog on error
            if 'progress_dialog' in locals() and progress_dialog.open:
                progress_dialog.open = False
                page.update()
            logger.error(f"Failed to export table {table_name}: {e}")
            return False

    def on_edit_row(e, row_data: Dict[str, Any]):
        """Handle row editing."""
        logger.info(f"Editing row: {row_data}")

        # Create form fields for each column
        form_fields = []
        original_data = {}

        for key, value in row_data.items():
            # Skip binary data and ID fields for editing
            if key.lower() == 'id' or (isinstance(value, str) and len(value) == 32 and all(c in '0123456789abcdef' for c in value)):
                # Display ID as read-only
                form_fields.append(
                    ft.TextField(
                        label=key.replace("_", " ").title(),
                        value=str(value),
                        read_only=True,
                        width=300
                    )
                )
                original_data[key] = value
            else:
                form_fields.append(
                    ft.TextField(
                        label=key.replace("_", " ").title(),
                        value=str(value) if value is not None else "",
                        width=300
                    )
                )
                original_data[key] = value

        # Create form container
        form_container = ft.Column(form_fields, spacing=10)

        def reset_changes(e):
            """Reset form fields to original values."""
            for i, field in enumerate(form_container.controls):
                if hasattr(field, 'value') and not field.read_only:
                    key = list(original_data.keys())[i]
                    field.value = str(original_data.get(key, "")) if original_data.get(key) is not None else ""
            form_container.update()

        def close_dialog(e):
            if hasattr(page, 'dialog') and page.dialog:
                page.dialog.open = False
            page.update()

        def save_changes(e):
            try:
                # Collect updated data
                updated_data = {}
                
                # Safely access the original data for ID
                row_id = original_data.get('id', None)
                if not row_id:
                    show_error_message(page, "Cannot save: Row ID not found")
                    return
                
                for i, (key, original_value) in enumerate(original_data.items()):
                    if key.lower() == 'id':
                        continue  # Skip ID field

                    # Ensure we have a valid form field
                    if i < len(form_fields):
                        control = form_fields[i]
                        new_value = getattr(control, 'value', '')

                        # Convert value to appropriate type
                        if isinstance(original_value, int):
                            try:
                                updated_data[key] = int(new_value)
                            except (ValueError, TypeError):
                                updated_data[key] = 0
                        elif isinstance(original_value, float):
                            try:
                                updated_data[key] = float(new_value)
                            except (ValueError, TypeError):
                                updated_data[key] = 0.0
                        elif isinstance(original_value, bool):
                            updated_data[key] = str(new_value).lower() in ('true', '1', 'yes', 'on')
                        else:
                            updated_data[key] = str(new_value) if new_value is not None else ""

                # Update row in database
                if server_bridge and hasattr(server_bridge, 'db_manager') and server_bridge.db_manager:
                    success = server_bridge.db_manager.update_row(selected_table_name, row_id, updated_data)
                    if success:
                        show_success_message(page, f"Row updated successfully in {selected_table_name}")
                        # Refresh the table
                        page.run_task(load_database_info_async)
                    else:
                        show_error_message(page, f"Failed to update row in {selected_table_name}")
                else:
                    # Simulate update for mock data
                    show_info_message(page, "Row would be updated in real implementation")

                close_dialog(None)

            except Exception as ex:
                logger.error(f"Error updating row: {ex}")
                show_error_message(page, f"Error updating row: {str(ex)}")

        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text(f"Edit Row in {selected_table_name.title()}"),
            content=ft.Container(
                content=form_container,
                width=400,
                height=400
            ),
            actions=[
                ft.TextButton("Cancel", icon=ft.Icons.CANCEL, on_click=close_dialog, tooltip="Cancel changes"),
                ft.TextButton("Reset", icon=ft.Icons.RESTORE, on_click=reset_changes, tooltip="Reset to original values"),
                ft.TextButton("Save", icon=ft.Icons.SAVE, on_click=save_changes, tooltip="Save database changes")
            ]
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def on_delete_row(e, row_data: Dict[str, Any]):
        """Handle row deletion."""
        logger.info(f"Deleting row: {row_data}")

        # Get row ID
        row_id = row_data.get("id", "")
        if not row_id:
            show_error_message(page, "Cannot delete row: No ID found")
            return

        # Confirm deletion
        def confirm_delete(e):
            try:
                if server_bridge and hasattr(server_bridge, 'db_manager') and server_bridge.db_manager:
                    # Try to delete from database
                    success = server_bridge.db_manager.delete_row(selected_table_name, row_id)
                    if success:
                        show_success_message(page, f"Row deleted successfully from {selected_table_name}")
                        # Refresh the table
                        page.run_task(load_database_info_async)
                    else:
                        show_error_message(page, f"Failed to delete row from {selected_table_name}")
                else:
                    # Simulate deletion for mock data
                    show_info_message(page, "Row would be deleted in real implementation")
            except Exception as ex:
                logger.error(f"Error deleting row: {ex}")
                show_error_message(page, f"Error deleting row: {str(ex)}")

        def close_dialog(e):
            if hasattr(page, 'dialog') and page.dialog:
                page.dialog.open = False
            page.update()

        # Show confirmation dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Text(f"Are you sure you want to delete this row from {selected_table_name}?"),
            actions=[
                ft.TextButton("Cancel", icon=ft.Icons.CANCEL, on_click=close_dialog, tooltip="Cancel deletion"),
                ft.TextButton("Delete", icon=ft.Icons.DELETE, on_click=confirm_delete, tooltip="Confirm row deletion")
            ]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def on_export_table(e):
        """Handle table export."""
        logger.info(f"Exporting table: {selected_table_name}")

        async def async_export():
            try:
                success = await export_table_async(selected_table_name)
                if success:
                    # Create export filename for user message
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    export_filename = f"{selected_table_name}_export_{timestamp}.csv"
                    export_path = os.path.join(os.path.expanduser("~"), "Downloads", export_filename)

                    message = f"Table {selected_table_name} exported to {export_path}"
                else:
                    message = f"Failed to export table {selected_table_name}"

                if success:
                    show_success_message(page, message)
                else:
                    show_error_message(page, message)

            except Exception as e:
                logger.error(f"Error in export handler: {e}")
                show_error_message(page, f"Error exporting table {selected_table_name}")

        # Run async operation
        page.run_task(async_export)

    def on_backup_database(e):
        """Handle database backup."""
        logger.info("Database backup initiated")
        show_info_message(page, "Database backup started")

    # Create table dropdown
    table_dropdown = ft.Dropdown(
        label="Database Table",
        value=selected_table_name,
        options=[
            ft.dropdown.Option("clients", "Clients"),
            ft.dropdown.Option("files", "Files"),
            ft.dropdown.Option("logs", "Logs")
        ],
        width=200,
        on_change=on_table_select
    )

    # Build the main view using clean Flet patterns
    main_view = ft.Column([
        # Header with title and action buttons
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.STORAGE, size=24),
                ft.Text("Database Browser", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),  # Spacer
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Refresh Database",
                        on_click=on_refresh_table
                    )
                ], spacing=5)
            ]),
            padding=ft.Padding(20, 20, 20, 10)
        ),
        ft.Divider(),

        # Database statistics
        ft.Container(
            content=ft.Text("Database Statistics", size=18, weight=ft.FontWeight.BOLD),
            padding=ft.Padding(20, 0, 20, 10)
        ),
        ft.Container(
            content=ft.Column([
                ft.ResponsiveRow([
                    ft.Column([
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.STORAGE, size=24, color=ft.Colors.BLUE),
                                    ft.Text("Status", size=12, weight=ft.FontWeight.W_500),
                                    ft.Text(
                                        ref=status_text_ref,
                                        value="Connected",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.GREEN
                                    )
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                padding=15
                            )
                        )
                    ], col={"sm": 6, "md": 3}),
                    ft.Column([
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.TABLE_VIEW, size=24, color=ft.Colors.PURPLE),
                                    ft.Text("Tables", size=12, weight=ft.FontWeight.W_500),
                                    ft.Text(
                                        ref=tables_text_ref,
                                        value="5",
                                        size=16,
                                        weight=ft.FontWeight.BOLD
                                    )
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                padding=15
                            )
                        )
                    ], col={"sm": 6, "md": 3}),
                    ft.Column([
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.STORAGE, size=24, color=ft.Colors.ORANGE),
                                    ft.Text("Records", size=12, weight=ft.FontWeight.W_500),
                                    ft.Text(
                                        ref=records_text_ref,
                                        value="1250",
                                        size=16,
                                        weight=ft.FontWeight.BOLD
                                    )
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                padding=15
                            )
                        )
                    ], col={"sm": 6, "md": 3}),
                    ft.Column([
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.FOLDER, size=24, color=ft.Colors.GREEN),
                                    ft.Text("Size", size=12, weight=ft.FontWeight.W_500),
                                    ft.Text(
                                        ref=size_text_ref,
                                        value="45.2 MB",
                                        size=16,
                                        weight=ft.FontWeight.BOLD
                                    )
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                padding=15
                            )
                        )
                    ], col={"sm": 6, "md": 3})
                ])
            ]),
            padding=ft.Padding(20, 0, 20, 10)
        ),
        ft.Divider(),

        # Table controls
        ft.Container(
            content=ft.Column([
                ft.ResponsiveRow([
                    ft.Column([
                        ft.Text("Select Table:", size=16, weight=ft.FontWeight.W_500),
                    ], col={"sm": 12, "md": 2}),
                    ft.Column([
                        table_dropdown,
                    ], col={"sm": 12, "md": 2}),
                    ft.Column([
                        ft.TextField(
                            label="Search...",
                            hint_text="Search in all columns",
                            prefix_icon=ft.Icons.SEARCH,
                            on_change=on_search_change,
                            expand=True
                        ),
                    ], col={"sm": 12, "md": 4}),
                    ft.Column([
                        ft.FilledButton(
                            "Export CSV",
                            icon=ft.Icons.DOWNLOAD,
                            on_click=on_export_table,
                            tooltip="Export table to CSV file"
                        ),
                    ], col={"sm": 6, "md": 2}),
                    ft.Column([
                        ft.OutlinedButton(
                            "Backup",
                            icon=ft.Icons.BACKUP,
                            on_click=on_backup_database,
                            tooltip="Create database backup"
                        )
                    ], col={"sm": 6, "md": 2})
                ], spacing=20),
                # Column filters will be added dynamically based on selected table
            ], spacing=10),
            padding=ft.Padding(20, 0, 20, 10)
        ),

        # Table info
        ft.Container(
            content=ft.Row([
                ft.Text(
                    ref=table_info_text_ref,
                    value=f"Table: {selected_table_name}",
                    size=14,
                    color=ft.Colors.PRIMARY
                ),
                ft.Text("•", size=14, color=ft.Colors.ON_SURFACE),
                ft.Text(
                    ref=rows_count_text_ref,
                    value="0 rows",
                    size=14,
                    color=ft.Colors.ON_SURFACE
                ),
                ft.Container(expand=True),
                ft.Text(
                    ref=last_updated_text_ref,
                    value="Last updated: Never",
                    color=ft.Colors.ON_SURFACE,
                    size=12
                )
            ]),
            padding=ft.Padding(20, 0, 20, 10)
        ),

        # Table content in scrollable container
        ft.Container(
            ref=table_container_ref,
            content=ft.Text("Loading...", color=ft.Colors.ON_SURFACE_VARIANT),
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10,
            margin=ft.Margin(20, 0, 20, 20)
        )

    ], spacing=20, expand=True)

    # Also provide a trigger for manual loading if needed
    def trigger_initial_load():
        """Trigger initial data load manually."""
        page.run_task(load_database_info_async)

    # Export the trigger function so it can be called externally
    main_view.trigger_initial_load = trigger_initial_load

    # CRITICAL: Load initial table data when view is created
    def load_initial_table():
        """Load the initial table (clients) when view is first shown."""
        logger.info(f"Loading initial table: {selected_table_name}")
        # Trigger table load for the default selected table
        page.run_task(load_database_info_async)
        # Use a small delay to ensure the UI is ready, then load the table
        async def delayed_table_load():
            await asyncio.sleep(0.1)  # Small delay to ensure UI is ready
            try:
                # Simulate dropdown selection to load the table
                class MockEvent:
                    def __init__(self, value):
                        self.control = MockControl(value)
                
                class MockControl:
                    def __init__(self, value):
                        self.value = value
                
                mock_event = MockEvent(selected_table_name)
                on_table_select(mock_event)
                logger.info(f"Initial table load triggered for: {selected_table_name}")
            except Exception as e:
                logger.error(f"Error in initial table load: {e}")
        
        page.run_task(delayed_table_load)
    
    # Schedule initial load
    load_initial_table()

    return main_view
