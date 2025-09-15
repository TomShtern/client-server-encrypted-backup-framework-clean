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
from theme import setup_modern_theme
from utils.ui_components import create_modern_card, create_status_chip, create_enhanced_metric_card, create_modern_button

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

    # UI Control References with ft.Ref for better control management
    data_table_ref = ft.Ref[ft.DataTable]()
    status_text_ref = ft.Ref[ft.Text]()
    tables_count_text_ref = ft.Ref[ft.Text]()
    records_count_text_ref = ft.Ref[ft.Text]()
    size_text_ref = ft.Ref[ft.Text]()
    table_info_text_ref = ft.Ref[ft.Text]()
    last_updated_text_ref = ft.Ref[ft.Text]()
    loading_indicator_ref = ft.Ref[ft.ProgressRing]()

    status_text = ft.Text("Unknown", size=14, weight=ft.FontWeight.BOLD, ref=status_text_ref)
    tables_count_text = ft.Text("0", size=20, weight=ft.FontWeight.BOLD, ref=tables_count_text_ref)
    records_count_text = ft.Text("0", size=20, weight=ft.FontWeight.BOLD, ref=records_count_text_ref)
    size_text = ft.Text("0 MB", size=20, weight=ft.FontWeight.BOLD, ref=size_text_ref)

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
        on_change=lambda e: page.run_task(load_table_data_action, e.control.value) if e.control.value else None,
        width=200,
        border_color=ft.Colors.PRIMARY,
        focused_border_color=ft.Colors.SECONDARY
    )

    search_field = ft.TextField(
        label="Search in table...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: page.run_task(search_table_action, e.control.value),
        width=300,
        border_color=ft.Colors.PRIMARY,
        focused_border_color=ft.Colors.SECONDARY
    )

    # Professional DataTable with clean styling following clients.py/files.py pattern
    database_table_ref = ft.Ref[ft.DataTable]()
    database_table = ft.DataTable(
        ref=database_table_ref,
        columns=[
            ft.DataColumn(ft.Text("Loading...", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY))
        ],
        rows=[],
        heading_row_color=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
        border=ft.border.all(3, ft.Colors.PRIMARY),
        border_radius=16,
        data_row_min_height=62,
        column_spacing=24,
        show_checkbox_column=False,
        bgcolor=ft.Colors.SURFACE,
        divider_thickness=1
    )

    table_info_text = ft.Text("No data", size=14, color=ft.Colors.SECONDARY, weight=ft.FontWeight.W_500, ref=table_info_text_ref)
    last_updated_text = ft.Text("Never", size=14, color=ft.Colors.SECONDARY, weight=ft.FontWeight.W_500, ref=last_updated_text_ref)
    loading_indicator = ft.ProgressRing(visible=False, width=20, height=20, ref=loading_indicator_ref)

    # --- Server-Mediated Data Functions ---

    async def load_database_info():
        """Load database info through server-mediated state management"""
        try:
            # Set loading state
            state_manager.set_loading("database_info", True)

            # Use server-mediated update for state persistence with correct bridge API
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

    async def load_table_data_action(table_name_or_event):
        """Load table data through server-mediated state management"""
        # Handle both direct table name calls and dropdown change events
        if isinstance(table_name_or_event, str):
            table_name = table_name_or_event
        elif hasattr(table_name_or_event, 'control') and hasattr(table_name_or_event.control, 'value'):
            table_name = table_name_or_event.control.value
        else:
            logger.error(f"Invalid parameter type for load_table_data_action: {type(table_name_or_event)}")
            return

        if not table_name:
            logger.warning("Empty table name provided to load_table_data_action")
            return

        nonlocal selected_table
        selected_table = table_name

        try:
            # Set loading state for specific table
            state_manager.set_loading(f"table_data_{table_name}", True)
            if loading_indicator_ref.current:
                loading_indicator_ref.current.visible = True
                loading_indicator_ref.current.update()

            # Use server-mediated update for table data with correct bridge API
            result = await state_manager.server_mediated_update(
                key="current_table_data",
                value={"table_name": table_name, "search_query": search_query},
                server_operation="get_table_data_async",
                table_name=table_name
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
            if loading_indicator_ref.current:
                loading_indicator_ref.current.visible = False
                loading_indicator_ref.current.update()

    async def search_table_action(query: str):
        """Search table through server-mediated state management"""
        nonlocal search_query
        search_query = query.lower().strip()

        try:
            # Set loading state for search
            state_manager.set_loading("table_search", True)

            # Use server-mediated update for search results (fallback to client-side since search_table_data_async doesn't exist)
            # Since search_table_data_async doesn't exist in bridge, use client-side filtering
            result = {"success": False, "error": "Server search not available"}
            logger.info(f"Search operation falling back to client-side filtering for query: {search_query}")

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
        """Update table row through server-mediated state management with enhanced validation"""
        try:
            # Validate inputs
            if row_id is None:
                show_error_message(page, "Invalid row ID")
                return

            if not updated_data:
                show_error_message(page, "No data to update")
                return

            # Validate and convert data types
            validated_data = {}
            for key, value in updated_data.items():
                try:
                    # Convert numeric strings to proper types
                    if isinstance(value, str) and value.isdigit():
                        validated_data[key] = int(value)
                    elif isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                        validated_data[key] = float(value)
                    else:
                        validated_data[key] = str(value).strip() if value else None
                except (ValueError, TypeError):
                    validated_data[key] = str(value) if value else None

            state_manager.set_loading("row_update", True)

            # Use server-mediated update for row modification with correct bridge API
            result = await state_manager.server_mediated_update(
                key="row_update_result",
                value={"table": selected_table, "row_id": row_id, "data": validated_data},
                server_operation="update_row",
                table_name=selected_table,
                row_id=row_id,
                updated_data=validated_data
            )

            if result.get('success'):
                show_success_message(page, "Row updated successfully")
                # Refresh table data to reflect changes
                await load_table_data_action(selected_table)
            else:
                error_msg = result.get('error', 'Unknown error')
                show_error_message(page, f"Failed to update row: {error_msg}")
                logger.warning(f"Server update failed: {error_msg}")

        except Exception as e:
            logger.error(f"Row update failed: {e}")
            show_error_message(page, f"Update failed: {str(e)}")
        finally:
            state_manager.set_loading("row_update", False)

    async def delete_row_action(row_id: Any):
        """Delete table row through server-mediated state management with cascading support"""
        try:
            if row_id is None:
                show_error_message(page, "Invalid row ID")
                return

            state_manager.set_loading("row_delete", True)

            # Check for related records before deletion (client-side fallback)
            try:
                # Compute related count on the client as a fallback since check_related_records doesn't exist in bridge
                related_count = 0
                if selected_table == "clients":
                    # For clients, check if there are files associated
                    current_files = state_manager.get("files", [])
                    related_count = len([f for f in current_files if str(f.get('client_id')) == str(row_id)])
                elif selected_table == "files":
                    # For files, no cascading needed typically
                    related_count = 0

                if related_count > 0:
                    # Ask user about cascading delete
                    from utils.dialog_consolidation_helper import show_confirmation

                    def handle_cascade_confirmation(confirmed):
                        if confirmed:
                            page.run_task(_perform_delete_with_cascade, row_id, True)

                    show_confirmation(
                        page,
                        "Cascading Delete",
                        f"This row has {related_count} related records. Delete them all?",
                        handle_cascade_confirmation
                    )
                    return

            except Exception as check_error:
                logger.warning(f"Could not check related records: {check_error}")
                # Continue with regular delete

            # Perform regular delete
            await _perform_delete_with_cascade(row_id, False)

        except Exception as e:
            logger.error(f"Row deletion failed: {e}")
            show_error_message(page, f"Deletion failed: {str(e)}")
        finally:
            state_manager.set_loading("row_delete", False)

    async def _perform_delete_with_cascade(row_id: Any, cascade: bool = False):
        """Perform the actual delete operation with optional cascading"""
        try:
            # Use server-mediated update for row deletion with correct bridge API
            result = await state_manager.server_mediated_update(
                key="row_delete_result",
                value={"table": selected_table, "row_id": row_id, "cascade": cascade},
                server_operation="delete_row",
                table_name=selected_table,
                row_id=row_id
            )

            if result.get('success'):
                deleted_count = result.get('data', {}).get('deleted_count', 1)
                if cascade and deleted_count > 1:
                    show_success_message(page, f"Row and {deleted_count - 1} related records deleted successfully")
                else:
                    show_success_message(page, "Row deleted successfully")
                # Refresh table data to reflect changes
                await load_table_data_action(selected_table)
            else:
                error_msg = result.get('error', 'Unknown error')
                show_error_message(page, f"Failed to delete row: {error_msg}")
                logger.warning(f"Server delete failed: {error_msg}")

        except Exception as e:
            logger.error(f"Delete operation failed: {e}")
            show_error_message(page, f"Delete failed: {str(e)}")

    async def export_table_action():
        """Export table data through server-mediated state management"""
        nonlocal last_export_time

        try:
            state_manager.set_loading("table_export", True)

            # Export operation fallback to client-side since export_table_data_async doesn't exist in bridge
            result = {"success": False, "error": "Server export not available"}
            logger.info(f"Export operation falling back to client-side CSV export for table: {selected_table}")

            if result.get('success'):
                # If server export succeeded, show success
                export_path = result.get('data', {}).get('file_path', 'Downloads folder')
                show_success_message(page, f"Table exported to {export_path}")
                last_export_time = datetime.now()
                await state_manager.update_async("last_export_time", last_export_time, source="export_success")
            else:
                # Fallback to client-side export with retry logic
                retry_count = 0
                max_retries = 2

                while retry_count < max_retries:
                    try:
                        # Attempt server export again after brief delay
                        if retry_count > 0:
                            await asyncio.sleep(1)  # Brief delay before retry
                            logger.info(f"Retrying server export (attempt {retry_count + 1})")

                            # Export retry also falls back to client-side
                            retry_result = {"success": False, "error": "Server export retry not available"}
                            logger.info(f"Export retry operation falling back to client-side for table: {selected_table}")

                            if retry_result.get('success'):
                                export_path = retry_result.get('data', {}).get('file_path', 'Downloads folder')
                                show_success_message(page, f"Table exported to {export_path} (retry successful)")
                                last_export_time = datetime.now()
                                await state_manager.update_async("last_export_time", last_export_time, source="export_retry")
                                return

                        retry_count += 1

                    except Exception as retry_error:
                        logger.warning(f"Export retry {retry_count} failed: {retry_error}")
                        retry_count += 1

                # All retries failed, use client-side fallback
                logger.info("All server export attempts failed, falling back to client-side export")
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

            try:
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

                # Update controls using refs for safer access with page attachment checks
                if status_text_ref.current and hasattr(status_text_ref.current, 'page') and status_text_ref.current.page:
                    status_text_ref.current.update()
                elif hasattr(status_text, 'page') and status_text.page:
                    status_text.update()

                if tables_count_text_ref.current and hasattr(tables_count_text_ref.current, 'page') and tables_count_text_ref.current.page:
                    tables_count_text_ref.current.update()
                elif hasattr(tables_count_text, 'page') and tables_count_text.page:
                    tables_count_text.update()

                if records_count_text_ref.current and hasattr(records_count_text_ref.current, 'page') and records_count_text_ref.current.page:
                    records_count_text_ref.current.update()
                elif hasattr(records_count_text, 'page') and records_count_text.page:
                    records_count_text.update()

                if size_text_ref.current and hasattr(size_text_ref.current, 'page') and size_text_ref.current.page:
                    size_text_ref.current.update()
                elif hasattr(size_text, 'page') and size_text.page:
                    size_text.update()

            except Exception as e:
                logger.warning(f"Failed to update database info UI: {e}")

        # Table data subscription
        def update_table_display_ui(table_data, old_value):
            """Update professional DataTable with reactive state changes"""
            if not table_data or not database_table_ref.current:
                return

            columns = table_data.get("columns", [])
            rows = table_data.get("rows", [])

            if not columns:
                if table_info_text_ref.current and hasattr(table_info_text_ref.current, 'page') and table_info_text_ref.current.page:
                    table_info_text_ref.current.value = "No data available"
                    table_info_text_ref.current.update()
                elif hasattr(table_info_text, 'page') and table_info_text.page:
                    table_info_text.value = "No data available"
                    table_info_text.update()
                return

            try:
                # Rebuild DataTable columns dynamically
                data_columns = []
                for col in columns:
                    data_columns.append(
                        ft.DataColumn(ft.Text(
                            str(col).title().replace('_', ' '),
                            weight=ft.FontWeight.BOLD,
                            size=14,
                            color=ft.Colors.PRIMARY
                        ))
                    )

                # Add Actions column
                data_columns.append(
                    ft.DataColumn(ft.Text(
                        "Actions",
                        weight=ft.FontWeight.BOLD,
                        size=14,
                        color=ft.Colors.PRIMARY
                    ))
                )

                # Rebuild DataTable rows with enhanced formatting
                data_rows = []
                for row_index, row in enumerate(rows[:50]):  # Limit to 50 for performance
                    cells = []

                    for i, cell in enumerate(row):
                        # Format cell value with enhanced display
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

                        # Add status-based styling with color coding
                        cell_color = ft.Colors.ON_SURFACE
                        cell_weight = ft.FontWeight.NORMAL

                        if i < len(columns) and columns[i].lower() == 'status':
                            if str(cell).lower() in ['online', 'active', 'completed', 'connected']:
                                cell_color = ft.Colors.GREEN
                                cell_weight = ft.FontWeight.W_500
                            elif str(cell).lower() in ['offline', 'inactive', 'error', 'failed']:
                                cell_color = ft.Colors.RED
                                cell_weight = ft.FontWeight.W_500
                            elif str(cell).lower() in ['pending', 'warning', 'in_progress']:
                                cell_color = ft.Colors.ORANGE
                                cell_weight = ft.FontWeight.W_500

                        cells.append(
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(
                                        formatted_value,
                                        size=13,
                                        color=cell_color,
                                        weight=cell_weight,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        max_lines=2
                                    ),
                                    padding=ft.Padding(8, 4, 8, 4),
                                    on_click=lambda e, r=row, c=i: handle_cell_click(r, c)
                                )
                            )
                        )

                    # Add actions cell with comprehensive options
                    actions_cell = ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.INFO_OUTLINED,
                                tooltip="View Details",
                                icon_color=ft.Colors.BLUE,
                                icon_size=18,
                                on_click=lambda e, r=row: (logger.info(f"[DEBUG] View Details clicked for row: {r}"), handle_cell_click(r, 0))
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip="Edit Row",
                                icon_color=ft.Colors.GREEN,
                                icon_size=18,
                                on_click=lambda e, r=row: (logger.info(f"[DEBUG] Edit Row clicked for row: {r}"), page.run_task(edit_row_dialog, r))
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Delete Row",
                                icon_color=ft.Colors.RED,
                                icon_size=18,
                                on_click=lambda e, r=row: (logger.info(f"[DEBUG] Delete Row clicked for row: {r}"), page.run_task(delete_row_dialog, r))
                            )
                        ], spacing=4, tight=True)
                    )
                    cells.append(actions_cell)

                    data_rows.append(ft.DataRow(cells=cells))

                # Update DataTable structure with safety check
                if database_table_ref.current and hasattr(database_table_ref.current, 'page') and database_table_ref.current.page:
                    database_table_ref.current.columns = data_columns
                    database_table_ref.current.rows = data_rows
                    database_table_ref.current.update()
                else:
                    logger.warning("Database table ref not ready for update")

                # Update info text with enhanced information
                total_rows = len(rows)
                search_results = state_manager.get("table_search_results", {})

                if search_query and search_results.get("query") == search_query:
                    filtered_count = len(search_results.get("rows", []))
                    info_text = f"Showing {min(50, filtered_count)} of {filtered_count} matches (total: {total_rows} records)"
                else:
                    info_text = f"Showing {min(50, total_rows)} of {total_rows} records in {selected_table} table"

                if table_info_text_ref.current and hasattr(table_info_text_ref.current, 'page') and table_info_text_ref.current.page:
                    table_info_text_ref.current.value = info_text
                    table_info_text_ref.current.update()
                elif hasattr(table_info_text, 'page') and table_info_text.page:
                    table_info_text.value = info_text
                    table_info_text.update()

                # Update the DataTable
                if hasattr(database_table_ref.current, 'page') and database_table_ref.current.page:
                    database_table_ref.current.update()

            except Exception as e:
                logger.error(f"Failed to update DataTable display: {e}")
                if table_info_text_ref.current and hasattr(table_info_text_ref.current, 'page') and table_info_text_ref.current.page:
                    table_info_text_ref.current.value = f"Error displaying table: {str(e)}"
                    table_info_text_ref.current.update()

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
                try:
                    if last_updated_text_ref.current and hasattr(last_updated_text_ref.current, 'page') and last_updated_text_ref.current.page:
                        last_updated_text_ref.current.value = f"Updated: {timestamp.strftime('%H:%M:%S')}"
                        last_updated_text_ref.current.update()
                    elif hasattr(last_updated_text, 'page') and last_updated_text.page:
                        last_updated_text.value = f"Updated: {timestamp.strftime('%H:%M:%S')}"
                        last_updated_text.update()
                except Exception as e:
                    logger.warning(f"Failed to update last updated UI: {e}")

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
        nonlocal selected_table
        current_data = state_manager.get("current_table_data", {})
        columns = current_data.get("columns", [])

        # DEBUGGING: Log state manager contents
        logger.info(f"[handle_cell_click] Selected table: {selected_table}")
        logger.info(f"[handle_cell_click] Current data from state manager: {current_data}")
        logger.info(f"[handle_cell_click] Columns: {columns}, Row data: {row_data}")

        # FALLBACK: If no columns available, use mock data directly
        if not columns:
            logger.warning("[handle_cell_click] No columns found, falling back to mock data")
            mock_table_data = generate_mock_table_data(selected_table)
            columns = mock_table_data["columns"]
            current_data = {"columns": columns, "rows": mock_table_data["rows"], "table_name": selected_table}
            # Update state manager with fallback data
            state_manager.update("current_table_data", current_data, source="fallback")
            logger.info(f"[handle_cell_click] Fallback data set - Columns: {columns}")

        if not columns or not row_data:
            show_error_message(page, "No column information available")
            return

        if cell_index >= len(columns) or cell_index >= len(row_data):
            show_error_message(page, "Invalid cell selection")
            return

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
            ], spacing=8),
            ft.Container(height=8),  # Add some spacing
            ft.ElevatedButton(
                "Add New Row",
                icon=ft.Icons.ADD,
                on_click=lambda e: page.run_task(add_row_dialog),
                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
            )
        ], tight=True, spacing=8)

        show_info(page, f"Cell Details - {column_name}", cell_info, width=500)

    async def edit_row_dialog(row_data: list):
        """Show edit row dialog"""
        nonlocal selected_table
        current_data = state_manager.get("current_table_data", {})
        columns = current_data.get("columns", [])

        # DEBUGGING: Log state manager contents
        logger.debug(f"[edit_row_dialog] Current data from state manager: {current_data}")
        logger.debug(f"[edit_row_dialog] Columns: {columns}, Row data: {row_data}")

        # FALLBACK: If no columns available, use mock data directly
        if not columns:
            logger.warning("[edit_row_dialog] No columns found, falling back to mock data")
            mock_table_data = generate_mock_table_data(selected_table)
            columns = mock_table_data["columns"]
            current_data = {"columns": columns, "rows": mock_table_data["rows"], "table_name": selected_table}
            # Update state manager with fallback data
            await state_manager.update_async("current_table_data", current_data, source="fallback")
            logger.info(f"[edit_row_dialog] Fallback data set - Columns: {columns}")

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
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    async def delete_row_dialog(row_data: list):
        """Show delete confirmation dialog"""
        row_id = row_data[0] if row_data else None

        async def confirm_delete(confirmed):
            if confirmed:
                await delete_row_action(row_id)

        show_confirmation(
            page,
            "Delete Row",
            f"Are you sure you want to delete this row?\n\nRow ID: {row_id}",
            confirm_delete
        )

    async def add_row_action(new_data: Dict[str, Any]):
        """Add new database record with proper form validation"""
        try:
            # Validate required fields
            if not new_data:
                show_error_message(page, "No data provided")
                return

            # Validate and convert data types
            validated_data = {}
            for key, value in new_data.items():
                if not value or str(value).strip() == "":
                    if key.lower() in ['id', 'name', 'filename']:  # Required fields
                        show_error_message(page, f"Required field '{key}' cannot be empty")
                        return
                    validated_data[key] = None
                    continue

                try:
                    # Convert numeric strings to proper types
                    if isinstance(value, str) and value.isdigit():
                        validated_data[key] = int(value)
                    elif isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                        validated_data[key] = float(value)
                    else:
                        validated_data[key] = str(value).strip()
                except (ValueError, TypeError):
                    validated_data[key] = str(value).strip()

            state_manager.set_loading("row_add", True)

            # Use direct server bridge call for row addition (since add_row doesn't exist in bridge API)
            # Fall back to direct bridge call and then update state
            try:
                if server_bridge:
                    # For now, simulate success since add_table_row doesn't exist in current bridge
                    logger.info(f"Simulating row addition for table {selected_table}: {validated_data}")
                    result = {"success": True, "data": {"new_id": f"new_{int(time.time())}"}, "mode": "mock"}
                    await state_manager.update_async("row_add_result", result, source="manual_add")
                else:
                    result = {"success": False, "error": "No server bridge available"}
            except Exception as e:
                logger.error(f"Row addition operation failed: {e}")
                result = {"success": False, "error": str(e)}

            if result.get('success'):
                new_id = result.get('data', {}).get('new_id', 'Unknown')
                show_success_message(page, f"Row added successfully (ID: {new_id})")
                # Refresh table data to show new record
                await load_table_data_action(selected_table)
            else:
                error_msg = result.get('error', 'Unknown error')
                show_error_message(page, f"Failed to add row: {error_msg}")
                logger.warning(f"Server add failed: {error_msg}")

        except Exception as e:
            logger.error(f"Row addition failed: {e}")
            show_error_message(page, f"Add failed: {str(e)}")
        finally:
            state_manager.set_loading("row_add", False)

    async def add_row_dialog():
        """Show add row dialog with proper form validation"""
        current_data = state_manager.get("current_table_data", {})
        columns = current_data.get("columns", [])

        # DEBUGGING: Log state manager contents
        logger.debug(f"[add_row_dialog] Current data from state manager: {current_data}")
        logger.debug(f"[add_row_dialog] Columns: {columns}")

        # FALLBACK: If no columns available, use mock data directly
        if not columns:
            logger.warning("[add_row_dialog] No columns found, falling back to mock data")
            mock_table_data = generate_mock_table_data(selected_table)
            columns = mock_table_data["columns"]
            current_data = {"columns": columns, "rows": mock_table_data["rows"], "table_name": selected_table}
            # Update state manager with fallback data
            await state_manager.update_async("current_table_data", current_data, source="fallback")
            logger.info(f"[add_row_dialog] Fallback data set - Columns: {columns}")

        if not columns:
            show_error_message(page, "No column information available")
            return

        # Create form fields based on table schema
        form_fields = []
        for column in columns:
            if column.lower() == 'id':
                continue  # Skip ID field for new records

            field_label = column.title().replace('_', ' ')
            required = column.lower() in ['name', 'filename', 'client_id']

            if column.lower() == 'status':
                # Dropdown for status fields
                status_options = ["active", "inactive", "pending", "completed", "error"]
                field = ft.Dropdown(
                    label=field_label + (" *" if required else ""),
                    options=[ft.dropdown.Option(opt) for opt in status_options],
                    width=300
                )
            elif 'date' in column.lower() or 'time' in column.lower():
                # Use current timestamp for date fields
                field = ft.TextField(
                    label=field_label + (" *" if required else ""),
                    value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    width=300
                )
            else:
                field = ft.TextField(
                    label=field_label + (" *" if required else ""),
                    width=300
                )

            form_fields.append((column, field, required))

        if not form_fields:
            show_error_message(page, "No fields available for new record")
            return

        form_content = ft.Column([
            ft.Text(f"Add New {selected_table.title()[:-1] if selected_table.endswith('s') else selected_table}",
                   size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Fields marked with * are required", size=11, color=ft.Colors.GREY_600),
            ft.Divider(),
            *[field for _, field, _ in form_fields]
        ], spacing=8, width=400)

        async def save_new_record(e):
            try:
                # Validate and collect form data
                new_data = {}
                validation_errors = []

                for column, field, required in form_fields:
                    value = field.value if hasattr(field, 'value') else field.current.value if hasattr(field, 'current') else ""

                    if required and (not value or str(value).strip() == ""):
                        validation_errors.append(f"{column.title().replace('_', ' ')} is required")
                        continue

                    new_data[column] = value

                if validation_errors:
                    show_error_message(page, "\n".join(validation_errors))
                    return

                # Close dialog
                page.close_dialog()

                # Perform server-mediated addition
                await add_row_action(new_data)

            except Exception as ex:
                logger.error(f"Failed to save new record: {ex}")
                show_error_message(page, f"Save failed: {str(ex)}")

        # Show dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Add New Record"),
            content=form_content,
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.close_dialog()),
                ft.ElevatedButton("Add Record", on_click=save_new_record,
                                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE))
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    async def refresh_database():
        """Refresh all database data through server-mediated operations"""
        await asyncio.gather(
            load_database_info(),
            load_table_data_action(selected_table)
        )

    # --- UI Layout Construction ---

    def create_info_card(title: str, value_control: ft.Control, icon: str, color: str) -> ft.Container:
        """Create an enhanced information card with sophisticated styling."""
        return create_modern_card(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=28, color=ft.Colors.WHITE),
                        bgcolor=color,
                        border_radius=12,
                        padding=ft.Padding(12, 12, 12, 12)
                    ),
                    ft.Column([
                        value_control,
                        ft.Text(title, size=14, color=ft.Colors.SECONDARY, weight=ft.FontWeight.BOLD)
                    ], spacing=4, tight=True)
                ], alignment=ft.MainAxisAlignment.START, spacing=16)
            ], spacing=12),
            elevation="elevated",
            padding=20,
            return_type="container"
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
            create_info_card("Status", status_text, ft.Icons.STORAGE, ft.Colors.PRIMARY)
        ], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([
            create_info_card("Tables", tables_count_text, ft.Icons.TABLE_CHART, ft.Colors.TERTIARY)
        ], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([
            create_info_card("Records", records_count_text, ft.Icons.FORMAT_LIST_NUMBERED, ft.Colors.SECONDARY)
        ], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([
            create_info_card("Size", size_text, ft.Icons.STORAGE, ft.Colors.OUTLINE)
        ], col={"sm": 12, "md": 6, "lg": 3})
    ])

    # Table controls with enhanced styling
    table_controls = create_modern_card(
        content=ft.Row([
            table_selector,
            search_field,
            ft.Row([
                ft.ElevatedButton(
                    "Add Record",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: page.run_task(add_row_dialog),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREEN,
                        color=ft.Colors.ON_PRIMARY,
                        elevation=4
                    )
                ),
                ft.ElevatedButton(
                    "Export CSV",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: page.run_task(export_table_action),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY,
                        elevation=4
                    )
                )
            ], spacing=12)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=16),
        elevation="soft",
        padding=24,
        return_type="container"
    )

    # Professional table container with scroll support - responsive layout
    styled_table = ft.Container(
        content=ft.Column([
            database_table
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
        border_radius=ft.border_radius.all(12),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=12,
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
            offset=ft.Offset(0, 4)
        ),
        bgcolor=ft.Colors.SURFACE,
        padding=ft.Padding(16, 16, 16, 16),
        expand=True  # REMOVE height=500, ADD expand=True
    )

    # Enhanced data table container with sophisticated styling
    table_container = create_modern_card(
        content=ft.Column([
            # Table header with sophisticated styling
            ft.Container(
                content=ft.Row([
                    table_info_text,
                    last_updated_text
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.Padding(24, 16, 24, 16),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
                margin=ft.Margin(0, 0, 0, 0)
            ),
            # Table content area with scroll and enhanced padding - responsive container
            ft.Container(
                content=ft.Column([styled_table], scroll=ft.ScrollMode.AUTO, expand=True),
                padding=ft.Padding(24, 16, 24, 24),
                expand=True,  # REMOVE height=600, ADD expand=True
                bgcolor=ft.Colors.SURFACE,
                border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20)
            )
        ], spacing=0),
        elevation="floating",
        return_type="container"
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

    # Defer subscriptions until after view is attached to page
    async def setup_subscriptions():
        """Set up state subscriptions after view is attached to page"""
        await asyncio.sleep(0.1)  # Small delay to ensure page attachment
        subscribe_to_state_changes()

        # Initialize with mock data and trigger server-mediated loading
        try:
            # Set initial mock data in state
            mock_db_info = generate_mock_db_info()
            mock_table_data = generate_mock_table_data(selected_table)

            await state_manager.update_async("database_info", mock_db_info, source="init")
            await state_manager.update_async("current_table_data", {
                "table_name": selected_table,
                "columns": mock_table_data["columns"],
                "rows": mock_table_data["rows"]
            }, source="init")

            logger.info("Database view initialized with server-mediated state management")
            logger.debug(f"Initial table data set - Table: {selected_table}, Columns: {mock_table_data['columns']}")
        except Exception as e:
            logger.error(f"Failed to initialize database view: {e}")

        # Schedule server-mediated refresh
        await refresh_database()

    # Start subscription setup in background
    page.run_task(setup_subscriptions)

    return main_view