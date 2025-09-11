#!/usr/bin/env python3
"""
Database View for FletV2
Clean, framework-harmonious implementation following successful patterns.
Optimized for database management and visual appeal at ~600 LOC.
"""

import flet as ft
import asyncio
import csv
import io
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.user_feedback import show_success_message, show_error_message
from utils.dialog_consolidation_helper import show_confirmation, show_input

logger = get_logger(__name__)

def create_database_view(
    server_bridge: Optional[ServerBridge], 
    page: ft.Page, 
    state_manager: Optional[StateManager] = None
) -> ft.Control:
    """
    Create database view with clean, maintainable implementation.
    Follows successful patterns from clients.py and analytics.py.
    """
    logger.info("Creating database view")
    
    # State Management - Simple and Direct
    db_info = {}
    selected_table = "clients"
    table_data = {"columns": [], "rows": []}
    search_query = ""
    is_loading = False
    
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
        on_change=lambda e: page.run_task(lambda: load_table_data(e.control.value)),
        width=200
    )
    
    search_field = ft.TextField(
        label="Search in table...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: apply_search(e.control.value),
        width=300
    )
    
    data_table = ft.DataTable(
        columns=[],
        rows=[],
        show_bottom_border=True,
        column_spacing=20,
        expand=True
    )
    
    table_info_text = ft.Text("No data", size=12, color=ft.Colors.GREY_600)
    last_updated_text = ft.Text("Never", size=12, color=ft.Colors.GREY_600)
    
    # Core Data Functions
    async def load_database_info():
        """Load database information from server bridge with fallback."""
        nonlocal db_info, is_loading
        
        if is_loading:
            return
            
        is_loading = True
        
        try:
            if server_bridge:
                try:
                    db_info = await server_bridge.get_database_info_async()
                    logger.info("Loaded database info from bridge")
                except Exception as e:
                    logger.warning(f"Server bridge failed, using mock data: {e}")
                    db_info = generate_mock_db_info()
            else:
                db_info = generate_mock_db_info()
                
            update_database_info_ui()
            
            # Update state manager
            if state_manager:
                state_manager.update("database_info", db_info)
                
        except Exception as e:
            logger.error(f"Failed to load database info: {e}")
            db_info = {"status": "Error", "error": str(e)}
            update_database_info_ui()
        finally:
            is_loading = False

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

    async def load_table_data(table_name: str):
        """Load data for selected table."""
        nonlocal selected_table, table_data, is_loading
        
        if is_loading:
            return
            
        selected_table = table_name
        is_loading = True
        
        try:
            if server_bridge:
                try:
                    table_data = await server_bridge.get_table_data_async(table_name)
                    logger.info(f"Loaded {table_name} table data from bridge")
                except Exception as e:
                    logger.warning(f"Server bridge failed for {table_name}, using mock data: {e}")
                    table_data = generate_mock_table_data(table_name)
            else:
                table_data = generate_mock_table_data(table_name)
                
            apply_search(search_query)  # Apply current search
            
            last_updated_text.value = f"Updated: {datetime.now().strftime('%H:%M:%S')}"
            last_updated_text.update()
            
        except Exception as e:
            logger.error(f"Failed to load table {table_name}: {e}")
            table_data = {"columns": [], "rows": []}
            update_table_display()
        finally:
            is_loading = False

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

    def update_database_info_ui():
        """Update database info UI elements."""
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

    def apply_search(query: str):
        """Apply search filter to table data."""
        nonlocal search_query
        search_query = query.lower().strip()
        update_table_display()

    def update_table_display():
        """Update the data table with filtered results."""
        # Clear existing columns and rows
        data_table.columns.clear()
        data_table.rows.clear()
        
        columns = table_data.get("columns", [])
        rows = table_data.get("rows", [])
        
        if not columns:
            table_info_text.value = "No data available"
            table_info_text.update()
            data_table.update()
            return
        
        # Create columns
        for col in columns:
            data_table.columns.append(
                ft.DataColumn(ft.Text(str(col).title(), weight=ft.FontWeight.BOLD, size=12))
            )
        
        # Filter rows based on search
        filtered_rows = rows
        if search_query:
            filtered_rows = [
                row for row in rows
                if any(search_query in str(cell).lower() for cell in row)
            ]
        
        # Add rows (limit to 50 for performance)
        for row in filtered_rows[:50]:
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
                
                cells.append(ft.DataCell(
                    ft.Text(formatted_value, size=12),
                    on_tap=lambda e, r=row, c=i: handle_cell_click(r, c)
                ))
            
            data_table.rows.append(ft.DataRow(cells))
        
        # Update info text
        total_rows = len(rows)
        filtered_count = len(filtered_rows)
        
        if search_query:
            table_info_text.value = f"Showing {min(50, filtered_count)} of {filtered_count} matches (total: {total_rows} records)"
        else:
            table_info_text.value = f"Showing {min(50, total_rows)} of {total_rows} records"
        
        table_info_text.update()
        data_table.update()

    def handle_cell_click(row_data: list, cell_index: int):
        """Handle cell click for viewing/editing."""
        column_name = table_data.get("columns", [])[cell_index] if cell_index < len(table_data.get("columns", [])) else "Unknown"
        cell_value = row_data[cell_index] if cell_index < len(row_data) else "N/A"
        
        logger.info(f"Cell clicked: {column_name} = {cell_value}")
        
        # Show cell details in a simple info dialog
        from utils.dialog_consolidation_helper import show_info
        
        cell_info = ft.Column([
            ft.Text(f"Column: {column_name}", weight=ft.FontWeight.BOLD),
            ft.Text(f"Value: {cell_value}"),
            ft.Divider(),
            ft.Text("Full Row Data:", weight=ft.FontWeight.BOLD),
            ft.Text(str(row_data), size=11, selectable=True)
        ], tight=True, spacing=8)
        
        show_info(page, f"Cell Details - {column_name}", cell_info, width=400)

    async def export_table_csv():
        """Export current table data to CSV."""
        try:
            if not table_data.get("columns") or not table_data.get("rows"):
                show_error_message(page, "No data to export")
                return
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(table_data["columns"])
            
            # Write rows
            for row in table_data["rows"]:
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
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            show_error_message(page, f"Export failed: {str(e)}")

    async def refresh_database():
        """Refresh all database data."""
        await asyncio.gather(
            load_database_info(),
            load_table_data(selected_table)
        )

    # UI Layout Construction
    def create_info_card(title: str, value_control: ft.Control, icon: str, color: ft.colors) -> ft.Container:
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
            border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=12,
            padding=16,
            expand=True
        )

    # Header section
    header_row = ft.Row([
        ft.Text("Database", size=24, weight=ft.FontWeight.BOLD),
        ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh database",
            on_click=lambda e: page.run_task(refresh_database)
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # Database status cards
    status_cards = ft.ResponsiveRow([
        ft.Column([
            create_info_card("Status", status_text, ft.Icons.DATABASE, ft.Colors.BLUE)
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
            on_click=lambda e: page.run_task(export_table_csv),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            )
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=16)
    
    # Data table container
    table_container = ft.Container(
        content=ft.Column([
            ft.Row([
                table_info_text,
                last_updated_text
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),  # Spacing
            data_table
        ], spacing=0),
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        border_radius=8,
        padding=16,
        expand=True
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
    
    # Initialize database
    page.run_task(refresh_database)
    
    return main_view