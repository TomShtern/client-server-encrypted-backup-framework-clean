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
import aiofiles
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
                    ft.Icon(ft.Icons.TABLE_VIEW, size=64, color=ft.Colors.ON_SURFACE),
                    ft.Text(
                        "No records found in the selected table.",
                        size=14,
                        color=ft.Colors.ON_SURFACE
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
                ft.DataColumn(ft.Text(col.replace("_", " ").title(), weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PURPLE_800))
                for col in filtered_data["columns"]
            ] + [
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PURPLE_800))
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row.get(col, "")), size=13))
                        for col in filtered_data["columns"]
                    ] + [
                        ft.DataCell(
                            ft.PopupMenuButton(
                                icon=ft.Icons.MORE_VERT,
                                tooltip="Row Actions",
                                icon_color=ft.Colors.PURPLE_600,
                                items=[
                                    ft.PopupMenuItem(
                                        text="Edit Row",
                                        icon=ft.Icons.EDIT,
                                        on_click=lambda e, r=row: [logger.info(f"Edit row clicked: {r.get('id', 'unknown')}"), on_edit_row(e, r)]
                                    ),
                                    ft.PopupMenuItem(
                                        text="Delete Row",
                                        icon=ft.Icons.DELETE,
                                        on_click=lambda e, r=row: [logger.info(f"Delete row clicked: {r.get('id', 'unknown')}"), on_delete_row(e, r)]
                                    )
                                ]
                            )
                        )
                    ]
                )
                for row in filtered_data["rows"]
            ],
            heading_row_color=ft.Colors.PURPLE_50,
            border=ft.border.all(2, ft.Colors.PURPLE_300),
            border_radius=15,
            data_row_min_height=40,  # Reduced for better space utilization
            column_spacing=20,  # Reduced spacing for more content
            show_checkbox_column=False
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
                # Get actual row count from current table data to fix mismatch
                current_data = get_current_table_data()
                actual_records = len(current_data.get("rows", [])) if current_data else 0
                
                db_info = {
                    "status": "Mock Mode", 
                    "tables": 3,
                    "records": actual_records,  # Use actual row count instead of fake 173
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
            try:
                # Only show error message if page is ready to accept controls
                if hasattr(page, 'controls') and page.controls:
                    show_error_message(page, f"Failed to load database info: {str(e)}")
            except Exception as ui_error:
                logger.error(f"Could not show error message (page not ready): {ui_error}")
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

            # Write CSV file with progress simulation using aiofiles
            async with aiofiles.open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Write header
                header_line = ','.join(f'"{col}"' for col in table_data["columns"]) + '\n'
                await csvfile.write(header_line)
                progress_text.value = "Writing header..."
                page.update()

                # Write rows with progress updates
                for i, row in enumerate(table_data["rows"]):
                    row_data = [str(row.get(col, "")) for col in table_data["columns"]]
                    row_line = ','.join(f'"{cell}"' for cell in row_data) + '\n'
                    await csvfile.write(row_line)

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
        """Handle row editing with improved dialog and form handling."""
        logger.info(f"Editing row: {row_data}")

        # Create form fields map for each column with proper references
        form_fields = {}
        original_data = {}

        # Create form fields with proper field references
        form_controls = []
        
        for key, value in row_data.items():
            original_data[key] = value
            
            # Determine field type and create appropriate control
            is_readonly = key.lower() == 'id' or (isinstance(value, str) and len(value) == 32 and all(c in '0123456789abcdef' for c in value))
            
            # Create text field with proper labeling
            field = ft.TextField(
                label=key.replace("_", " ").title(),
                value=str(value) if value is not None else "",
                read_only=is_readonly,
                width=350,
                height=50
            )
            
            # Store field reference with key for easy access
            form_fields[key] = field
            form_controls.append(field)

        # Create scrollable form container
        form_container = ft.Container(
            content=ft.Column(
                form_controls, 
                spacing=12,
                scroll=ft.ScrollMode.AUTO
            ),
            width=380,
            height=350  # Fixed height with scrolling
        )

        def reset_changes(e):
            """Reset form fields to original values."""
            try:
                for key, original_value in original_data.items():
                    if key in form_fields and not form_fields[key].read_only:
                        form_fields[key].value = str(original_value) if original_value is not None else ""
                        form_fields[key].update()
                logger.info("Form fields reset to original values")
            except Exception as ex:
                logger.error(f"Error resetting form: {ex}")

        def close_dialog(e):
            """Close the edit dialog."""
            try:
                if hasattr(page, 'dialog') and page.dialog and page.dialog.open:
                    page.dialog.open = False
                    page.update()
                    page.dialog = None
                logger.info("Edit dialog closed")
            except Exception as ex:
                logger.error(f"Error closing edit dialog: {ex}")

        def save_changes(e):
            """Save form changes to database."""
            try:
                # Get row ID for update operation
                row_id = original_data.get('id', None)
                if not row_id:
                    show_error_message(page, "Cannot save: Row ID not found")
                    return

                # Collect updated data from form fields
                updated_data = {}
                validation_errors = []
                
                for key, field in form_fields.items():
                    if key.lower() == 'id' or field.read_only:
                        continue  # Skip ID and read-only fields
                    
                    try:
                        new_value = field.value if field.value is not None else ""
                        original_value = original_data.get(key)

                        # Convert value to appropriate type based on original
                        if isinstance(original_value, int):
                            if new_value.strip() == "":
                                updated_data[key] = 0
                            else:
                                updated_data[key] = int(new_value)
                        elif isinstance(original_value, float):
                            if new_value.strip() == "":
                                updated_data[key] = 0.0
                            else:
                                updated_data[key] = float(new_value)
                        elif isinstance(original_value, bool):
                            updated_data[key] = str(new_value).lower() in ('true', '1', 'yes', 'on', 'checked')
                        else:
                            updated_data[key] = str(new_value)
                            
                    except ValueError as ve:
                        validation_errors.append(f"{key}: {str(ve)}")
                    except Exception as fe:
                        validation_errors.append(f"{key}: Invalid value format")

                # Check for validation errors
                if validation_errors:
                    error_msg = "Validation errors:\n" + "\n".join(validation_errors)
                    show_error_message(page, error_msg)
                    return

                logger.info(f"Saving changes for row {row_id}: {updated_data}")

                # Attempt database update
                if server_bridge and hasattr(server_bridge, 'db_manager') and server_bridge.db_manager:
                    try:
                        result = server_bridge.db_manager.update_row(selected_table_name, row_id, updated_data)
                        
                        # Handle response format
                        if isinstance(result, dict):
                            success = result.get('success', False)
                            message = result.get('message', 'Unknown result')
                            mode = result.get('mode', 'unknown')
                        else:
                            # Backward compatibility
                            success = bool(result)
                            message = f'Row updated successfully in {selected_table_name}' if success else f'Failed to update row in {selected_table_name}'
                            mode = 'real'
                        
                        if success:
                            if mode == 'mock':
                                show_info_message(page, f"🧪 DEMO: {message}", mode='mock')
                            else:
                                show_success_message(page, message, mode='real')
                            # Refresh the table to show changes
                            page.run_task(load_database_info_async)
                        else:
                            show_error_message(page, f"Update failed: {message}")
                            return  # Don't close dialog on failure
                            
                    except Exception as db_ex:
                        logger.error(f"Database update error: {db_ex}")
                        show_error_message(page, f"Database error: {str(db_ex)}")
                        return  # Don't close dialog on error
                else:
                    # Mock mode - simulate successful update
                    changes_text = ", ".join([f"{k}='{v}'" for k, v in updated_data.items()])
                    mock_message = f"Updated {row_id}: {changes_text}"
                    show_info_message(page, mock_message, mode='mock')
                    
                    # Refresh table to show mock changes would appear
                    page.run_task(load_database_info_async)

                # Close dialog after successful save
                close_dialog(None)

            except Exception as ex:
                logger.error(f"Error saving row changes: {ex}")
                show_error_message(page, f"Error saving changes: {str(ex)}")

        # Create enhanced dialog with better styling
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.EDIT, size=20),
                ft.Text(f"Edit Row in {selected_table_name.title()}", size=18, weight=ft.FontWeight.BOLD)
            ]),
            content=form_container,
            actions=[
                ft.TextButton(
                    "Cancel", 
                    icon=ft.Icons.CANCEL, 
                    on_click=close_dialog, 
                    tooltip="Cancel changes without saving"
                ),
                ft.TextButton(
                    "Reset", 
                    icon=ft.Icons.RESTORE, 
                    on_click=reset_changes, 
                    tooltip="Reset all fields to original values"
                ),
                ft.FilledButton(
                    "Save Changes", 
                    icon=ft.Icons.SAVE, 
                    on_click=save_changes, 
                    tooltip="Save changes to database"
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        # Show dialog using proper Flet pattern
        try:
            # Ensure any existing dialog is closed first
            if hasattr(page, 'dialog') and page.dialog:
                page.dialog.open = False
                page.dialog = None
                
            # Set and open the new dialog
            page.dialog = dialog
            dialog.open = True
            page.update()
            
            logger.info(f"Edit dialog opened successfully for row {row_data.get('id', 'unknown')}")
            
        except Exception as ex:
            logger.error(f"Error opening edit dialog: {ex}")
            show_error_message(page, f"Failed to open edit dialog: {str(ex)}")

    def on_delete_row(e, row_data: Dict[str, Any]):
        """Handle row deletion with improved confirmation dialog."""
        logger.info(f"Deleting row: {row_data}")

        # Get row ID for deletion
        row_id = row_data.get("id", "")
        if not row_id:
            show_error_message(page, "Cannot delete row: No ID found")
            return

        # Create summary of row data for confirmation
        row_summary = []
        for key, value in list(row_data.items())[:3]:  # Show first 3 fields
            if value is not None and str(value).strip():
                display_key = key.replace("_", " ").title()
                display_value = str(value)[:30]  # Truncate long values
                row_summary.append(f"{display_key}: {display_value}")
        
        summary_text = "\n".join(row_summary) if row_summary else f"ID: {row_id}"

        def confirm_delete(e):
            """Execute the row deletion."""
            try:
                # Close dialog first using proper pattern
                if hasattr(page, 'dialog') and page.dialog and page.dialog.open:
                    page.dialog.open = False
                    page.update()
                    page.dialog = None
                
                if server_bridge and hasattr(server_bridge, 'db_manager') and server_bridge.db_manager:
                    try:
                        # Try to delete from database
                        result = server_bridge.db_manager.delete_row(selected_table_name, row_id)
                        
                        # Handle response format
                        if isinstance(result, dict):
                            success = result.get('success', False)
                            message = result.get('message', 'Unknown result')
                            mode = result.get('mode', 'unknown')
                        else:
                            # Backward compatibility
                            success = bool(result)
                            message = f'Row deleted successfully from {selected_table_name}' if success else f'Failed to delete row from {selected_table_name}'
                            mode = 'real'
                        
                        if success:
                            if mode == 'mock':
                                show_info_message(page, f"🧪 DEMO: {message}", mode='mock')
                            else:
                                show_success_message(page, message, mode='real')
                            # Refresh the table to show changes
                            page.run_task(load_database_info_async)
                        else:
                            show_error_message(page, f"Delete failed: {message}")
                            
                    except Exception as db_ex:
                        logger.error(f"Database deletion error: {db_ex}")
                        show_error_message(page, f"Database error: {str(db_ex)}")
                else:
                    # Mock mode - simulate deletion
                    mock_message = f"Deleted row {row_id} from {selected_table_name}"
                    show_info_message(page, mock_message, mode='mock')
                    
                    # Refresh table to show mock changes
                    page.run_task(load_database_info_async)
                    
            except Exception as ex:
                logger.error(f"Error deleting row: {ex}")
                show_error_message(page, f"Error deleting row: {str(ex)}")

        def close_dialog(e):
            """Close the confirmation dialog."""
            try:
                if hasattr(page, 'dialog') and page.dialog and page.dialog.open:
                    page.dialog.open = False
                    page.update()
                    page.dialog = None
                logger.info("Delete confirmation dialog closed")
            except Exception as ex:
                logger.error(f"Error closing delete dialog: {ex}")

        # Create enhanced confirmation dialog
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.DELETE_FOREVER, color=ft.Colors.RED, size=20),
                ft.Text("Confirm Row Deletion", size=18, weight=ft.FontWeight.BOLD)
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"Are you sure you want to delete this row from the {selected_table_name} table?",
                        size=14
                    ),
                    ft.Container(height=10),  # Spacer
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Row Details:", weight=ft.FontWeight.BOLD, size=12),
                            ft.Text(summary_text, size=12, color=ft.Colors.ON_SURFACE)
                        ]),
                        padding=10,
                        bgcolor=ft.Colors.SURFACE,
                        border_radius=8
                    ),
                    ft.Container(height=10),  # Spacer
                    ft.Row([
                        ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE, size=16),
                        ft.Text("This action cannot be undone!", size=12, color=ft.Colors.ORANGE, weight=ft.FontWeight.BOLD)
                    ])
                ], spacing=5),
                width=350,
                height=180
            ),
            actions=[
                ft.TextButton(
                    "Cancel", 
                    icon=ft.Icons.CANCEL, 
                    on_click=close_dialog, 
                    tooltip="Cancel deletion"
                ),
                ft.FilledButton(
                    "Delete Row", 
                    icon=ft.Icons.DELETE_FOREVER, 
                    on_click=confirm_delete, 
                    tooltip="Permanently delete this row",
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Show dialog using proper Flet pattern
        try:
            # Ensure any existing dialog is closed first
            if hasattr(page, 'dialog') and page.dialog:
                page.dialog.open = False
                page.dialog = None
                
            # Set and open the new dialog
            page.dialog = dialog
            dialog.open = True
            page.update()
            
            logger.info(f"Delete confirmation dialog opened successfully for row {row_id}")
            
        except Exception as ex:
            logger.error(f"Error opening delete dialog: {ex}")
            show_error_message(page, f"Failed to open delete dialog: {str(ex)}")

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
            content=ft.Text("Loading...", color=ft.Colors.ON_SURFACE),
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
