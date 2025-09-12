#!/usr/bin/env python3
"""
Database View for FletV2
Clean, framework-harmonious implementation with server-mediated state management.
Follows server-mediated pattern: user action → server bridge → state manager → reactive UI update.
Optimized for database management and visual appeal at ~600 LOC.
"""

import flet as ft
import asyncio
import csv
import io
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.dialog_consolidation_helper import show_success_message, show_error_message, show_confirmation, show_input
from utils.server_mediated_operations import create_server_mediated_operations

logger = get_logger(__name__)

def create_database_view(
    server_bridge: Optional[ServerBridge], 
    page: ft.Page, 
    state_manager: StateManager
) -> ft.Control:
    """
    Create database view with server-mediated state management.
    Follows successful server-mediated patterns from dashboard.py.
    """
    logger.info("Creating database view with server-mediated state management")
    
    # State variables (managed through state_manager)
    selected_table = "clients"
    search_query = ""
    last_export_time = None
    
    # UI Control References
    status_text = ft.Text("Unknown", size=14, weight=ft.FontWeight.BOLD)
    tables_count_text = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)
    records_count_text = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)
    size_text = ft.Text("0 MB", size=20, weight=ft.FontWeight.BOLD)
    
    table_selector = ft.Dropdown(
        label="Select Table",
        options=[
            ft.dropdown.Option("clients", "Clients"),
            ft.dropdown.Option("files", "Files"),
            ft.dropdown.Option("backups", "Backups"),
            ft.dropdown.Option("logs", "Logs"),
            ft.dropdown.Option("settings", "Settings")
        ],
        value="clients",
        on_change=lambda e: page.run_task(load_table_data_action, e.control.value),
        width=200
    )
    
    search_field = ft.TextField(
        label="Search in table...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: page.run_task(search_table_action, e.control.value),
        width=300
    )
    
    data_table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Loading...", weight=ft.FontWeight.BOLD))],
        rows=[],
        show_bottom_border=True,
        column_spacing=35,
        data_row_max_height=65,
        data_row_min_height=50,
        heading_row_height=55,
        border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.ON_SURFACE)),
        border_radius=6,
        expand=True,
        bgcolor=ft.Colors.SURFACE,
        heading_row_color=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
        data_row_color={
            ft.ControlState.HOVERED: ft.Colors.with_opacity(0.04, ft.Colors.ON_SURFACE),
            ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
        },
        divider_thickness=0.5,
        horizontal_lines=ft.BorderSide(0.5, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
        show_checkbox_column=False
    )
    
    table_info_text = ft.Text("No data", size=12, color=ft.Colors.GREY_600)
    last_updated_text = ft.Text("Never", size=12, color=ft.Colors.GREY_600)
    loading_indicator = ft.ProgressRing(visible=False, width=20, height=20)
    
    # --- Server-Mediated Data Functions ---
    
    async def load_database_info():
        """Load database info through server-mediated state management"""
        try:
            # Set loading state
            state_manager.set_loading("database_info", True)
            
            # Use server-mediated update for state persistence
            result = await state_manager.server_mediated_update(
                key="database_info",
                value=None,  # Will be set by server response
                server_operation="get_database_info_async"
            )
            
            if not result.get('success'):
                # Fallback to mock data if server operation fails
                mock_info = generate_mock_db_info()
                await state_manager.update_async("database_info", mock_info, source="fallback")
                logger.warning("Using mock database info")
                
        except Exception as e:
            logger.error(f"Failed to load database info: {e}")
            error_info = {"status": "Error", "error": str(e), "tables": 0, "total_records": 0, "size": "0 MB"}
            await state_manager.update_async("database_info", error_info, source="error")
        finally:
            state_manager.set_loading("database_info", False)

    async def load_table_data_action(table_name: str):
        """Load table data through server-mediated state management"""
        nonlocal selected_table
        selected_table = table_name
        
        try:
            # Set loading state for specific table
            state_manager.set_loading(f"table_data_{table_name}", True)
            loading_indicator.visible = True
            loading_indicator.update()
            
            # Use server-mediated update for table data
            result = await state_manager.server_mediated_update(
                key="current_table_data",
                value={"table_name": table_name, "search_query": search_query},
                server_operation="get_table_data_async"
            )
            
            if not result.get('success'):
                # Fallback to mock data
                mock_data = generate_mock_table_data(table_name)
                table_data = {"table_name": table_name, "columns": mock_data["columns"], "rows": mock_data["rows"]}
                await state_manager.update_async("current_table_data", table_data, source="fallback")
                logger.warning(f"Using mock data for table {table_name}")
            
            # Update last updated time
            await state_manager.update_async("table_last_updated", datetime.now(), source="load_table")
                
        except Exception as e:
            logger.error(f"Failed to load table {table_name}: {e}")
            error_data = {"table_name": table_name, "columns": [], "rows": [], "error": str(e)}
            await state_manager.update_async("current_table_data", error_data, source="error")
        finally:
            state_manager.set_loading(f"table_data_{table_name}", False)
            loading_indicator.visible = False
            loading_indicator.update()

    async def search_table_action(query: str):
        """Search table through server-mediated state management"""
        nonlocal search_query
        search_query = query.lower().strip()
        
        try:
            # Set loading state for search
            state_manager.set_loading("table_search", True)
            
            # Use server-mediated update for search results
            result = await state_manager.server_mediated_update(
                key="table_search_results",
                value={"table_name": selected_table, "query": search_query},
                server_operation="search_table_data_async"
            )
            
            if not result.get('success'):
                # Fallback to client-side filtering
                current_data = state_manager.get("current_table_data", {})
                filtered_rows = filter_rows_client_side(current_data.get("rows", []), query)
                search_results = {
                    "table_name": selected_table,
                    "query": search_query,
                    "columns": current_data.get("columns", []),
                    "rows": filtered_rows
                }
                await state_manager.update_async("table_search_results", search_results, source="client_filter")
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
            await state_manager.update_async("table_search_results", 
                                            {"error": str(e), "query": search_query}, source="search_error")
        finally:
            state_manager.set_loading("table_search", False)

    async def update_row_action(row_id: Any, updated_data: Dict[str, Any]):
        """Update table row through server-mediated state management"""
        try:
            state_manager.set_loading("row_update", True)
            
            # Use server-mediated update for row modification
            result = await state_manager.server_mediated_update(
                key="row_update_result",
                value={"table": selected_table, "row_id": row_id, "data": updated_data},
                server_operation="update_table_row_async"
            )
            
            if result.get('success'):
                show_success_message(page, "Row updated successfully")
                # Refresh table data to reflect changes
                await load_table_data_action(selected_table)
            else:
                show_error_message(page, f"Failed to update row: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Row update failed: {e}")
            show_error_message(page, f"Update failed: {str(e)}")
        finally:
            state_manager.set_loading("row_update", False)

    async def delete_row_action(row_id: Any):
        """Delete table row through server-mediated state management"""
        try:
            state_manager.set_loading("row_delete", True)
            
            # Use server-mediated update for row deletion
            result = await state_manager.server_mediated_update(
                key="row_delete_result",
                value={"table": selected_table, "row_id": row_id},
                server_operation="delete_table_row_async"
            )
            
            if result.get('success'):
                show_success_message(page, "Row deleted successfully")
                # Refresh table data to reflect changes
                await load_table_data_action(selected_table)
            else:
                show_error_message(page, f"Failed to delete row: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Row deletion failed: {e}")
            show_error_message(page, f"Deletion failed: {str(e)}")
        finally:
            state_manager.set_loading("row_delete", False)

    async def export_table_action():
        """Export table data through server-mediated state management"""
        nonlocal last_export_time
        
        try:
            state_manager.set_loading("table_export", True)
            
            # Use server-mediated update for export operation
            result = await state_manager.server_mediated_update(
                key="table_export_result",
                value={"table": selected_table, "format": "csv"},
                server_operation="export_table_data_async"
            )
            
            if result.get('success'):
                # If server export succeeded, show success
                export_path = result.get('data', {}).get('file_path', 'Downloads folder')
                show_success_message(page, f"Table exported to {export_path}")
                last_export_time = datetime.now()
                await state_manager.update_async("last_export_time", last_export_time, source="export_success")
            else:
                # Fallback to client-side export
                await export_table_csv_fallback()
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            await export_table_csv_fallback()
        finally:
            state_manager.set_loading("table_export", False)

    async def export_table_csv_fallback():
        """Fallback client-side CSV export"""
        nonlocal last_export_time
        
        try:
            current_data = state_manager.get("current_table_data", {})
            search_results = state_manager.get("table_search_results", {})
            
            # Use search results if available and query exists, otherwise use current data
            if search_query and search_results.get("rows"):
                export_data = search_results
            else:
                export_data = current_data
                
            if not export_data.get("columns") or not export_data.get("rows"):
                show_error_message(page, "No data to export")
                return
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(export_data["columns"])
            
            # Write rows
            for row in export_data["rows"]:
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            # Save to Downloads folder
            import os
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            
            filename = f"{selected_table}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(downloads_dir, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_content)
            
            show_success_message(page, f"Table exported to {filename}")
            logger.info(f"Table {selected_table} exported to {filepath}")
            
            # Update export state
            last_export_time = datetime.now()
            await state_manager.update_async("last_export_time", last_export_time, source="fallback_export")
            
        except Exception as e:
            logger.error(f"Fallback export failed: {e}")
            show_error_message(page, f"Export failed: {str(e)}")

    # --- State Management Subscriptions ---
    
    def subscribe_to_state_changes():
        """Subscribe to state changes for reactive UI updates"""
        
        # Database info subscription
        def update_database_info_ui(db_info, old_value):
            """Update database info UI elements reactively"""
            if not db_info:
                return
                
            db_status = db_info.get("status", "Unknown")
            
            if db_status == "Connected":
                status_text.value = "Connected"
                status_text.color = ft.Colors.GREEN
            elif db_status == "Disconnected":
                status_text.value = "Disconnected" 
                status_text.color = ft.Colors.RED
            else:
                status_text.value = db_status
                status_text.color = ft.Colors.ORANGE
            
            tables_count_text.value = str(db_info.get("tables", 0))
            records_count_text.value = str(db_info.get("total_records", 0))
            size_text.value = db_info.get("size", "0 MB")
            
            # Update controls
            status_text.update()
            tables_count_text.update()
            records_count_text.update()
            size_text.update()
        
        # Table data subscription
        def update_table_display_ui(table_data, old_value):
            """Update data table with reactive state changes"""
            if not table_data:
                return
                
            # Clear existing columns and rows
            data_table.columns.clear()
            data_table.rows.clear()
            
            columns = table_data.get("columns", [])
            rows = table_data.get("rows", [])
            
            if not columns:
                table_info_text.value = "No data available"
                table_info_text.update()
                return
            
            # Create columns with better styling
            for col in columns:
                data_table.columns.append(
                    ft.DataColumn(
                        ft.Container(
                            content=ft.Text(
                                str(col).title().replace('_', ' '), 
                                weight=ft.FontWeight.BOLD, 
                                size=13,
                                color=ft.Colors.ON_SURFACE
                            ),
                            padding=ft.Padding(8, 4, 8, 4),
                            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
                            border_radius=4
                        )
                    )
                )
            
            # Add rows (limit to 50 for performance)
            for row in rows[:50]:
                cells = []
                for i, cell in enumerate(row):
                    # Format cell value
                    if isinstance(cell, int) and cell > 1000000:  # Large numbers (file sizes)
                        if cell > 1024*1024*1024:  # GB
                            formatted_value = f"{cell/(1024*1024*1024):.1f} GB"
                        elif cell > 1024*1024:  # MB
                            formatted_value = f"{cell/(1024*1024):.1f} MB" 
                        elif cell > 1024:  # KB
                            formatted_value = f"{cell/1024:.1f} KB"
                        else:
                            formatted_value = f"{cell} B"
                    else:
                        formatted_value = str(cell)
                    
                    # Add status-based styling
                    cell_color = ft.Colors.ON_SURFACE
                    cell_bgcolor = None
                    
                    if i < len(columns) and columns[i].lower() == 'status':
                        if str(cell).lower() in ['online', 'active', 'completed', 'connected']:
                            cell_color = ft.Colors.GREEN
                            cell_bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.GREEN)
                        elif str(cell).lower() in ['offline', 'inactive', 'error', 'failed']:
                            cell_color = ft.Colors.RED  
                            cell_bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.RED)
                        elif str(cell).lower() in ['pending', 'warning', 'in_progress']:
                            cell_color = ft.Colors.ORANGE
                            cell_bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.ORANGE)
                    
                    cells.append(ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                formatted_value, 
                                size=12,
                                color=cell_color,
                                weight=ft.FontWeight.W_500 if i < len(columns) and columns[i].lower() == 'status' else ft.FontWeight.NORMAL
                            ),
                            padding=ft.Padding(8, 8, 8, 8),
                            bgcolor=cell_bgcolor,
                            border_radius=4,
                            on_click=lambda e, r=row, c=i: handle_cell_click(r, c)
                        )
                    ))
                
                data_table.rows.append(ft.DataRow(cells))
            
            # Update info text
            total_rows = len(rows)
            search_results = state_manager.get("table_search_results", {})
            
            if search_query and search_results.get("query") == search_query:
                filtered_count = len(search_results.get("rows", []))
                table_info_text.value = f"Showing {min(50, filtered_count)} of {filtered_count} matches (total: {total_rows} records)"
            else:
                table_info_text.value = f"Showing {min(50, total_rows)} of {total_rows} records"
            
            table_info_text.update()
            data_table.update()
        
        # Search results subscription
        def update_search_results_ui(search_results, old_value):
            """Update UI based on search results"""
            if search_results and search_results.get("query") == search_query:
                # Update table display with search results
                table_data = {
                    "columns": search_results.get("columns", []),
                    "rows": search_results.get("rows", [])
                }
                update_table_display_ui(table_data, None)
        
        # Last updated subscription
        def update_last_updated_ui(timestamp, old_value):
            """Update last updated timestamp"""
            if timestamp:
                last_updated_text.value = f"Updated: {timestamp.strftime('%H:%M:%S')}"
                last_updated_text.update()
        
        # Register subscriptions
        state_manager.subscribe("database_info", update_database_info_ui)
        state_manager.subscribe("current_table_data", update_table_display_ui)
        state_manager.subscribe("table_search_results", update_search_results_ui)
        state_manager.subscribe("table_last_updated", update_last_updated_ui)

    # --- Helper Functions ---
    
    def generate_mock_db_info() -> Dict[str, Any]:
        """Generate mock database information for development/fallback."""
        return {
            "status": "Connected",
            "database_name": "backup_system.db",
            "tables": 5,
            "total_records": 1247,
            "size": "12.4 MB",
            "last_backup": "2025-01-11 14:30:00"
        }

    def generate_mock_table_data(table_name: str) -> Dict[str, Any]:
        """Generate mock table data based on table name."""
        
        if table_name == "clients":
            return {
                "columns": ["id", "name", "ip_address", "status", "last_seen", "files_count"],
                "rows": [
                    [1, "Client-001", "192.168.1.101", "online", "2025-01-11 15:30", 42],
                    [2, "Client-002", "192.168.1.102", "offline", "2025-01-11 14:15", 38],
                    [3, "Client-003", "192.168.1.105", "online", "2025-01-11 15:28", 55],
                    [4, "Client-004", "192.168.1.110", "online", "2025-01-11 15:25", 29]
                ]
            }
        elif table_name == "files":
            return {
                "columns": ["id", "filename", "size", "type", "status", "client_id", "created_at"],
                "rows": [
                    [1, "backup_001.zip", 1024*1024*5, "archive", "complete", 1, "2025-01-11 14:20"],
                    [2, "document.pdf", 1024*512, "document", "verified", 2, "2025-01-11 14:22"],
                    [3, "photo.jpg", 1024*256, "image", "complete", 3, "2025-01-11 14:25"],
                    [4, "code.py", 1024*8, "code", "pending", 1, "2025-01-11 14:30"]
                ]
            }
        elif table_name == "backups":
            return {
                "columns": ["id", "backup_name", "client_id", "files_count", "total_size", "status", "created_at"],
                "rows": [
                    [1, "Daily_Backup_2025_01_11", 1, 42, 1024*1024*120, "completed", "2025-01-11 02:00"],
                    [2, "Weekly_Backup_2025_W02", 2, 38, 1024*1024*95, "completed", "2025-01-10 23:00"],
                    [3, "Manual_Backup_Client3", 3, 55, 1024*1024*180, "in_progress", "2025-01-11 15:00"]
                ]
            }
        elif table_name == "logs":
            return {
                "columns": ["id", "timestamp", "level", "source", "message", "client_id"],
                "rows": [
                    [1, "2025-01-11 15:30:15", "INFO", "client_manager", "Client connected", 3],
                    [2, "2025-01-11 15:28:42", "INFO", "file_transfer", "File uploaded successfully", 1],
                    [3, "2025-01-11 15:25:10", "WARNING", "backup_service", "Backup delayed", 2],
                    [4, "2025-01-11 15:20:05", "ERROR", "network", "Connection timeout", 4]
                ]
            }
        else:  # settings
            return {
                "columns": ["key", "value", "description", "modified_at"],
                "rows": [
                    ["backup_interval", "24", "Backup interval in hours", "2025-01-10 12:00"],
                    ["max_file_size", "1073741824", "Maximum file size in bytes", "2025-01-09 14:30"],
                    ["retention_days", "30", "Backup retention in days", "2025-01-08 10:15"],
                    ["compression_level", "6", "Compression level (0-9)", "2025-01-07 16:45"]
                ]
            }
    
    def filter_rows_client_side(rows: List[List], query: str) -> List[List]:
        """Client-side row filtering fallback"""
        if not query:
            return rows
        
        query = query.lower()
        return [
            row for row in rows
            if any(query in str(cell).lower() for cell in row)
        ]

    def handle_cell_click(row_data: list, cell_index: int):
        """Handle cell click for viewing/editing."""
        current_data = state_manager.get("current_table_data", {})
        columns = current_data.get("columns", [])
        
        column_name = columns[cell_index] if cell_index < len(columns) else "Unknown"
        cell_value = row_data[cell_index] if cell_index < len(row_data) else "N/A"
        
        logger.info(f"Cell clicked: {column_name} = {cell_value}")
        
        # Show cell details in a simple info dialog
        from utils.dialog_consolidation_helper import show_info
        
        cell_info = ft.Column([
            ft.Text(f"Column: {column_name}", weight=ft.FontWeight.BOLD),
            ft.Text(f"Value: {cell_value}"),
            ft.Divider(),
            ft.Text("Full Row Data:", weight=ft.FontWeight.BOLD),
            ft.Text(str(row_data), size=11, selectable=True),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton(
                    "Edit Row", 
                    icon=ft.Icons.EDIT,
                    on_click=lambda e: page.run_task(edit_row_dialog, row_data),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
                ),
                ft.ElevatedButton(
                    "Delete Row", 
                    icon=ft.Icons.DELETE,
                    on_click=lambda e: page.run_task(delete_row_dialog, row_data),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
                )
            ], spacing=8)
        ], tight=True, spacing=8)
        
        show_info(page, f"Cell Details - {column_name}", cell_info, width=500)

    async def edit_row_dialog(row_data: list):
        """Show edit row dialog"""
        current_data = state_manager.get("current_table_data", {})
        columns = current_data.get("columns", [])
        
        if not columns:
            show_error_message(page, "No column information available")
            return
        
        # Create edit form (simplified for demo)
        edit_fields = []
        for i, (column, value) in enumerate(zip(columns, row_data)):
            if column.lower() != 'id':  # Don't allow editing ID
                field = ft.TextField(
                    label=column.title().replace('_', ' '),
                    value=str(value),
                    width=300
                )
                edit_fields.append(field)
        
        if not edit_fields:
            show_error_message(page, "No editable fields found")
            return
        
        edit_content = ft.Column([
            ft.Text("Edit Row Data", size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            *edit_fields
        ], spacing=8, width=400)
        
        async def save_changes(e):
            try:
                # Get updated values
                updated_data = {}
                field_index = 0
                for i, column in enumerate(columns):
                    if column.lower() != 'id':
                        updated_data[column] = edit_fields[field_index].value
                        field_index += 1
                
                # Get row ID (assuming first column is ID)
                row_id = row_data[0] if row_data else None
                
                # Close dialog
                page.close_dialog()
                
                # Perform server-mediated update
                await update_row_action(row_id, updated_data)
                
            except Exception as ex:
                logger.error(f"Failed to save row changes: {ex}")
                show_error_message(page, f"Save failed: {str(ex)}")
        
        # Show dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Edit Row"),
            content=edit_content,
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.close_dialog()),
                ft.ElevatedButton("Save Changes", on_click=save_changes, 
                                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE))
            ]
        )
        page.show_dialog(dialog)

    async def delete_row_dialog(row_data: list):
        """Show delete confirmation dialog"""
        row_id = row_data[0] if row_data else None
        
        async def confirm_delete(confirmed):
            if confirmed:
                await delete_row_action(row_id)
        
        await show_confirmation(
            page, 
            "Delete Row", 
            f"Are you sure you want to delete this row?\n\nRow ID: {row_id}",
            confirm_delete
        )

    async def refresh_database():
        """Refresh all database data through server-mediated operations"""
        await asyncio.gather(
            load_database_info(),
            load_table_data_action(selected_table)
        )

    # --- UI Layout Construction ---
    
    def create_info_card(title: str, value_control: ft.Control, icon: str, color: str) -> ft.Container:
        """Create an information card."""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=24, color=color),
                    ft.Column([
                        value_control,
                        ft.Text(title, size=12, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD)
                    ], spacing=2, tight=True)
                ], alignment=ft.MainAxisAlignment.START, spacing=12)
            ], spacing=8),
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=12,
            padding=16,
            expand=True
        )

    # Header section
    header_row = ft.Row([
        ft.Text("Database", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([
            loading_indicator,
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Refresh database",
                on_click=lambda e: page.run_task(refresh_database)
            )
        ], spacing=8)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # Database status cards
    status_cards = ft.ResponsiveRow([
        ft.Column([
            create_info_card("Status", status_text, ft.Icons.STORAGE, ft.Colors.BLUE)
        ], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([
            create_info_card("Tables", tables_count_text, ft.Icons.TABLE_CHART, ft.Colors.GREEN)
        ], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([
            create_info_card("Records", records_count_text, ft.Icons.FORMAT_LIST_NUMBERED, ft.Colors.ORANGE)
        ], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([
            create_info_card("Size", size_text, ft.Icons.STORAGE, ft.Colors.PURPLE)
        ], col={"sm": 12, "md": 6, "lg": 3})
    ])
    
    # Table controls
    table_controls = ft.Row([
        table_selector,
        search_field,
        ft.ElevatedButton(
            "Export CSV",
            icon=ft.Icons.DOWNLOAD,
            on_click=lambda e: page.run_task(export_table_action),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            )
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=16)
    
    # Enhanced data table container with modern styling
    table_container = ft.Container(
        content=ft.Column([
            # Table header with better styling
            ft.Container(
                content=ft.Row([
                    table_info_text,
                    last_updated_text
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.Padding(16, 12, 16, 12),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
                border_radius=ft.border_radius.only(top_left=8, top_right=8),
                margin=ft.Margin(0, 0, 0, 0)
            ),
            # Table content area with scroll
            ft.Container(
                content=ft.Column([data_table], scroll=ft.ScrollMode.ADAPTIVE),
                padding=ft.Padding(16, 0, 16, 16),
                expand=True,
                bgcolor=ft.Colors.SURFACE,
                border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8)
            )
        ], spacing=0),
        border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE)),
        border_radius=8,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            offset=ft.Offset(0, 2),
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
        ),
        bgcolor=ft.Colors.SURFACE,
        expand=True,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )
    
    # Main layout
    main_view = ft.Column([
        header_row,
        ft.Divider(),
        status_cards,
        ft.Container(height=20),  # Spacing
        table_controls,
        ft.Container(height=16),  # Spacing
        table_container
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
    
    # Initialize state subscriptions
    subscribe_to_state_changes()
    
    # Initialize with mock data and trigger server-mediated loading
    try:
        # Set initial mock data in state
        mock_db_info = generate_mock_db_info()
        mock_table_data = generate_mock_table_data(selected_table)
        
        state_manager.update("database_info", mock_db_info, source="init")
        state_manager.update("current_table_data", {
            "table_name": selected_table,
            "columns": mock_table_data["columns"],
            "rows": mock_table_data["rows"]
        }, source="init")
        
        logger.info("Database view initialized with server-mediated state management")
    except Exception as e:
        logger.error(f"Failed to initialize database view: {e}")
    
    # Schedule server-mediated refresh
    page.run_task(refresh_database)
    
    return main_view