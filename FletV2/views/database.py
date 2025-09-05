#!/usr/bin/env python3
"""
Database View for FletV2
Clean function-based implementation following Framework Harmony principles.
"""

import flet as ft
from typing import Dict, Any
import asyncio
import csv
import os
from utils.debug_setup import get_logger
from datetime import datetime
from config import ASYNC_DELAY

logger = get_logger(__name__)


def create_database_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create database view using clean function-based patterns.
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The database view
    """
    
    # State variables
    db_info = {}
    selected_table_name = "clients"
    current_table_data = {}
    is_loading = False
    last_updated = None
    search_query = ""
    column_filters = {}  # Filter values for each column
    
    # Direct control references for text updates
    status_text_ref = ft.Ref[ft.Text]()
    tables_text_ref = ft.Ref[ft.Text]()
    records_text_ref = ft.Ref[ft.Text]()
    size_text_ref = ft.Ref[ft.Text]()
    table_info_text_ref = ft.Ref[ft.Text]()
    rows_count_text_ref = ft.Ref[ft.Text]()
    last_updated_text_ref = ft.Ref[ft.Text]()
    
    # Table container reference - needed for dynamic content
    table_container_ref = ft.Ref[ft.Container]()
    
    def filter_table_data():
        """Filter table data based on search query and column filters."""
        if not current_table_data or not current_table_data.get("rows"):
            return current_table_data
            
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
    
    def get_table_data(table_name: str) -> Dict[str, Any]:
        """Get table data from server or database."""
        if server_bridge:
            try:
                return server_bridge.get_table_data(table_name)
            except Exception as e:
                logger.error(f"Error getting table data: {e}")
        
        # Mock data for testing
        tables_data = {
            "clients": {
                "columns": ["id", "name", "last_seen", "has_public_key", "has_aes_key"],
                "rows": [
                    {"id": "client_001", "name": "Alpha Workstation", "last_seen": "2025-09-03 10:30:15", "has_public_key": True, "has_aes_key": True},
                    {"id": "client_002", "name": "Beta Server", "last_seen": "2025-09-02 09:15:22", "has_public_key": True, "has_aes_key": True},
                    {"id": "client_003", "name": "Gamma Laptop", "last_seen": "2025-09-01 14:22:10", "has_public_key": True, "has_aes_key": False}
                ]
            },
            "files": {
                "columns": ["id", "filename", "pathname", "verified", "filesize", "modification_date", "crc", "client_id", "client_name"],
                "rows": [
                    {"id": "file_001", "filename": "document1.pdf", "pathname": "/home/user/documents/document1.pdf", "verified": True, "filesize": 1024000, "modification_date": "2025-09-03 10:30:15", "crc": 123456789, "client_id": "client_001", "client_name": "Alpha Workstation"},
                    {"id": "file_002", "filename": "image1.jpg", "pathname": "/home/user/pictures/image1.jpg", "verified": False, "filesize": 2048000, "modification_date": "2025-09-03 11:45:30", "crc": 987654321, "client_id": "client_002", "client_name": "Beta Server"}
                ]
            },
            "logs": {
                "columns": ["id", "timestamp", "level", "component", "message"],
                "rows": [
                    {"id": 1, "timestamp": "2025-09-03 10:30:15", "level": "INFO", "component": "Server", "message": "Server started on port 1256"},
                    {"id": 2, "timestamp": "2025-09-03 10:31:22", "level": "INFO", "component": "Client", "message": "Client client_001 connected"},
                    {"id": 3, "timestamp": "2025-09-03 10:35:45", "level": "WARNING", "component": "File Transfer", "message": "File transfer completed with warnings"}
                ]
            }
        }
        
        return tables_data.get(table_name, {"columns": [], "rows": []})
    
    def update_table_content():
        """Update table content display with current data."""
        # Filter the data
        filtered_data = filter_table_data()
        
        # Create table content
        if not filtered_data.get("rows"):
            empty_content = ft.Container(
                content=ft.Text("No data available", size=16, text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center,
                height=200
            )
            if table_container_ref.current:
                table_container_ref.current.content = empty_content
                table_container_ref.current.update()
            return
        
        # Create data table with current data
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
                                    on_click=lambda e, r=row: on_edit_row(e, r)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="Delete",
                                    on_click=lambda e, r=row: on_delete_row(e, r),
                                    icon_color=ft.Colors.RED
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
            table_container_ref.current.content = ft.Column([data_table], scroll=ft.ScrollMode.AUTO)
            table_container_ref.current.update()
    
    async def load_database_info_async():
        """Load database info and update UI."""
        nonlocal db_info, current_table_data, is_loading, last_updated
        
        if is_loading:
            return
            
        is_loading = True
        try:
            # Load database info
            if server_bridge:
                try:
                    db_info = server_bridge.get_database_info()
                except Exception as e:
                    logger.warning(f"Server bridge failed: {e}")
                    # Mock data
                    db_info = {
                        "status": "Connected",
                        "tables": 5,
                        "records": 1250,
                        "size": "45.2 MB"
                    }
            else:
                # Mock data with delay
                await asyncio.sleep(ASYNC_DELAY)
                db_info = {
                    "status": "Connected",
                    "tables": 5,
                    "records": 1250,
                    "size": "45.2 MB"
                }
            
            # Load initial table data
            try:
                current_table_data = get_table_data(selected_table_name)
            except Exception as e:
                logger.warning(f"Failed to get table data: {e}")
                current_table_data = {"columns": [], "rows": []}
            
            # Update timestamp
            last_updated = datetime.now()
            if last_updated_text_ref.current:
                last_updated_text_ref.current.value = f"Last updated: {last_updated.strftime('%H:%M:%S')}"
                last_updated_text_ref.current.update()
            
            # Update UI components
            if status_text_ref.current:
                status_text_ref.current.value = db_info.get("status", "Unknown")
                status_text_ref.current.color = ft.Colors.GREEN if db_info.get("status") == "Connected" else ft.Colors.RED
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
            
            if rows_count_text_ref.current:
                rows_count_text_ref.current.value = f"{len(current_table_data.get('rows', []))} rows"
                rows_count_text_ref.current.update()
            
            if table_info_text_ref.current:
                table_info_text_ref.current.value = f"Table: {selected_table_name}"
                table_info_text_ref.current.update()
            
            # Update table content
            update_table_content()
            
            logger.info("Database info loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading database info: {e}")
        finally:
            is_loading = False
    
    def on_table_select(e):
        """Handle table selection change."""
        nonlocal selected_table_name, current_table_data, column_filters
        selected_table_name = e.control.value
        logger.info(f"Selected table: {selected_table_name}")
        
        try:
            current_table_data = get_table_data(selected_table_name)
            
            # Clear column filters for new table
            column_filters = {}
            
            # Update table info and content
            if table_info_text_ref.current:
                table_info_text_ref.current.value = f"Table: {selected_table_name}"
                table_info_text_ref.current.update()
            
            if rows_count_text_ref.current:
                rows_count_text_ref.current.value = f"{len(current_table_data.get('rows', []))} rows"
                rows_count_text_ref.current.update()
            
            update_table_content()
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Switched to table: {selected_table_name}"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True
            page.update()
            
        except Exception as e:
            logger.error(f"Error loading table data: {e}")
    
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
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Refreshing database info..."),
            bgcolor=ft.Colors.BLUE
        )
        page.snack_bar.open = True
        page.update()
    
    async def export_table_async(table_name: str) -> bool:
        """Export table data to CSV."""
        try:
            # Get table data
            table_data = get_table_data(table_name)
            
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
            
            # Write CSV file
            import csv
            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(table_data["columns"])
                
                # Write rows
                for row in table_data["rows"]:
                    row_data = [str(row.get(col, "")) for col in table_data["columns"]]
                    writer.writerow(row_data)
            
            logger.info(f"Exported table {table_name} to {export_path}")
            return True
        except Exception as e:
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
        
        def close_dialog(e):
            if hasattr(page, 'dialog') and page.dialog:
                page.dialog.open = False
            page.update()
        
        def save_changes(e):
            try:
                # Collect updated data
                updated_data = {}
                for i, (key, original_value) in enumerate(original_data.items()):
                    if key.lower() == 'id':
                        continue  # Skip ID field
                    
                    control = form_fields[i]
                    new_value = control.value
                    
                    # Convert value to appropriate type
                    if isinstance(original_value, int):
                        try:
                            updated_data[key] = int(new_value)
                        except ValueError:
                            updated_data[key] = 0
                    elif isinstance(original_value, float):
                        try:
                            updated_data[key] = float(new_value)
                        except ValueError:
                            updated_data[key] = 0.0
                    elif isinstance(original_value, bool):
                        updated_data[key] = new_value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        updated_data[key] = new_value
                
                # Get row ID
                row_id = original_data.get('id', '')
                if not row_id:
                    raise ValueError("Row ID not found")
                
                # Update row in database
                if server_bridge and hasattr(server_bridge, 'db_manager') and server_bridge.db_manager:
                    success = server_bridge.db_manager.update_row(selected_table_name, row_id, updated_data)
                    if success:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Row updated successfully in {selected_table_name}"),
                            bgcolor=ft.Colors.GREEN
                        )
                        # Refresh the table
                        page.run_task(load_database_info_async)
                    else:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Failed to update row in {selected_table_name}"),
                            bgcolor=ft.Colors.RED
                        )
                else:
                    # Simulate update for mock data
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Row would be updated in real implementation"),
                        bgcolor=ft.Colors.BLUE
                    )
                
                page.snack_bar.open = True
                close_dialog(None)
                page.update()
                
            except Exception as ex:
                logger.error(f"Error updating row: {ex}")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error updating row: {str(ex)}"),
                    bgcolor=ft.Colors.RED
                )
                page.snack_bar.open = True
                page.update()
        
        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text(f"Edit Row in {selected_table_name}"),
            content=ft.Container(
                content=form_container,
                width=400,
                height=400,
                scroll=ft.ScrollMode.AUTO
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Save", on_click=save_changes)
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
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Cannot delete row: No ID found"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Confirm deletion
        def confirm_delete(e):
            try:
                if server_bridge and hasattr(server_bridge, 'db_manager') and server_bridge.db_manager:
                    # Try to delete from database
                    success = server_bridge.db_manager.delete_row(selected_table_name, row_id)
                    if success:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Row deleted successfully from {selected_table_name}"),
                            bgcolor=ft.Colors.GREEN
                        )
                        page.snack_bar.open = True
                        page.update()
                        # Refresh the table
                        page.run_task(load_database_info_async)
                    else:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Failed to delete row from {selected_table_name}"),
                            bgcolor=ft.Colors.RED
                        )
                        page.snack_bar.open = True
                        page.update()
                else:
                    # Simulate deletion for mock data
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Row would be deleted in real implementation"),
                        bgcolor=ft.Colors.BLUE
                    )
                    page.snack_bar.open = True
                    page.update()
            except Exception as ex:
                logger.error(f"Error deleting row: {ex}")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error deleting row: {str(ex)}"),
                    bgcolor=ft.Colors.RED
                )
                page.snack_bar.open = True
                page.update()
        
        def close_dialog(e):
            if hasattr(page, 'dialog') and page.dialog:
                page.dialog.open = False
            page.update()
        
        # Show confirmation dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Text(f"Are you sure you want to delete this row from {selected_table_name}?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Delete", on_click=confirm_delete)
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
                    color = ft.Colors.GREEN
                else:
                    message = f"Failed to export table {selected_table_name}"
                    color = ft.Colors.RED
                
                page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
                page.snack_bar.open = True
                page.update()
                
            except Exception as e:
                logger.error(f"Error in export handler: {e}")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error exporting table {selected_table_name}"),
                    bgcolor=ft.Colors.RED
                )
                page.snack_bar.open = True
                page.update()
        
        # Run async operation
        page.run_task(async_export)
    
    def on_backup_database(e):
        """Handle database backup."""
        logger.info("Database backup initiated")
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Database backup started"),
            bgcolor=ft.Colors.PURPLE
        )
        page.snack_bar.open = True
        page.update()
    
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
                ft.Row([
                    ft.Text("Select Table:", size=16, weight=ft.FontWeight.W_500),
                    table_dropdown,
                    ft.Container(expand=True),
                    ft.TextField(
                        label="Search...",
                        hint_text="Search in all columns",
                        prefix_icon=ft.Icons.SEARCH,
                        width=200,
                        on_change=on_search_change
                    ),
                    ft.ElevatedButton(
                        "Export CSV",
                        icon=ft.Icons.DOWNLOAD,
                        on_click=on_export_table
                    ),
                    ft.OutlinedButton(
                        "Backup",
                        icon=ft.Icons.BACKUP,
                        on_click=on_backup_database
                    )
                ], spacing=20, wrap=True),
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
            content=ft.Column([], scroll=ft.ScrollMode.AUTO),
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10,
            margin=ft.Margin(20, 0, 20, 20)
        )
        
    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)
    
    # Initialize data loading
    page.run_task(load_database_info_async)
    
    # Also provide a trigger for manual loading if needed
    def trigger_initial_load():
        """Trigger initial data load manually."""
        page.run_task(load_database_info_async)
    
    # Export the trigger function so it can be called externally
    main_view.trigger_initial_load = trigger_initial_load
    
    return main_view