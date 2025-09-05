#!/usr/bin/env python3
"""
Database View for FletV2
Clean function-based implementation following Framework Harmony principles.
"""

import flet as ft
from typing import Dict, Any
import asyncio
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
    
    # State variables (replacing class attributes)
    db_info = {}
    selected_table_name = "clients"
    current_table_data = {}
    is_loading = False
    last_updated = None
    
    # Direct control references for text updates
    status_text = ft.Text("Connected", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
    tables_text = ft.Text("5", size=16, weight=ft.FontWeight.BOLD)
    records_text = ft.Text("1250", size=16, weight=ft.FontWeight.BOLD)
    size_text = ft.Text("45.2 MB", size=16, weight=ft.FontWeight.BOLD)
    table_info_text = ft.Text(f"Table: {selected_table_name}", size=14, color=ft.Colors.PRIMARY)
    rows_count_text = ft.Text("0 rows", size=14, color=ft.Colors.ON_SURFACE)
    last_updated_text = ft.Text("Last updated: Never", color=ft.Colors.ON_SURFACE, size=12)
    
    # Table container reference - needed for dynamic content
    table_container = ft.Container(
        content=ft.Column([], scroll=ft.ScrollMode.AUTO),
        expand=True,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=8,
        padding=10
    )
    
    def get_table_data(table_name: str) -> Dict[str, Any]:
        """Get table data from server or return mock data."""
        if server_bridge:
            try:
                return server_bridge.get_table_data(table_name)
            except Exception as e:
                logger.error(f"Error getting table data from server: {e}")
        
        # Mock data for testing
        tables_data = {
            "clients": {
                "columns": ["id", "client_id", "address", "status", "created_at"],
                "rows": [
                    {"id": 1, "client_id": "client_001", "address": "192.168.1.101", "status": "active", "created_at": "2025-09-01 10:00:00"},
                    {"id": 2, "client_id": "client_002", "address": "192.168.1.102", "status": "inactive", "created_at": "2025-09-02 11:30:00"},
                    {"id": 3, "client_id": "client_003", "address": "192.168.1.103", "status": "active", "created_at": "2025-09-03 09:15:00"}
                ]
            },
            "files": {
                "columns": ["id", "filename", "size", "client_id", "uploaded_at"],
                "rows": [
                    {"id": 1, "filename": "document.pdf", "size": "2.5MB", "client_id": "client_001", "uploaded_at": "2025-09-03 10:30:00"},
                    {"id": 2, "filename": "image.jpg", "size": "1.8MB", "client_id": "client_002", "uploaded_at": "2025-09-03 11:45:00"},
                    {"id": 3, "filename": "backup.zip", "size": "15.2MB", "client_id": "client_001", "uploaded_at": "2025-09-03 14:20:00"}
                ]
            },
            "logs": {
                "columns": ["id", "level", "message", "timestamp"],
                "rows": [
                    {"id": 1, "level": "INFO", "message": "Server started", "timestamp": "2025-09-03 08:00:00"},
                    {"id": 2, "level": "WARNING", "message": "High memory usage", "timestamp": "2025-09-03 12:30:00"},
                    {"id": 3, "level": "ERROR", "message": "Connection failed", "timestamp": "2025-09-03 15:45:00"}
                ]
            }
        }
        
        return tables_data.get(table_name, {"columns": [], "rows": []})
    
    def update_table_content():
        """Update table content display with current data."""
        nonlocal current_table_data
        
        if not current_table_data.get("rows"):
            empty_content = ft.Container(
                content=ft.Text("No data available", size=16, text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center,
                height=200
            )
            table_container.content.controls = [empty_content]
            table_container.update()
            return
        
        # Create data table with current data
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(col.upper(), weight=ft.FontWeight.BOLD))
                for col in current_table_data["columns"]
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row.get(col, ""))))
                        for col in current_table_data["columns"]
                    ]
                )
                for row in current_table_data["rows"]
            ],
            heading_row_color=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            data_row_min_height=45
        )
        
        table_container.content.controls = [data_table]
        table_container.update()
    
    async def load_database_info_async():
        """Load database info and update UI."""
        nonlocal db_info, current_table_data, is_loading, last_updated
        
        if is_loading:
            return
            
        is_loading = True
        try:
            # Load database info
            if server_bridge:
                db_info = await page.run_thread(server_bridge.get_database_info)
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
            current_table_data = await page.run_thread(get_table_data, selected_table_name)
            
            # Update timestamp
            last_updated = datetime.now()
            last_updated_text.value = f"Last updated: {last_updated.strftime('%H:%M:%S')}"
            
            # Update UI components
            status_text.value = db_info.get("status", "Unknown")
            status_text.color = ft.Colors.GREEN if db_info.get("status") == "Connected" else ft.Colors.RED
            
            tables_text.value = str(db_info.get("tables", 0))
            records_text.value = str(db_info.get("records", 0))
            size_text.value = db_info.get("size", "0 MB")
            
            rows_count_text.value = f"{len(current_table_data.get('rows', []))} rows"
            
            # Update all text controls
            status_text.update()
            tables_text.update()
            records_text.update()
            size_text.update()
            rows_count_text.update()
            last_updated_text.update()
            
            # Update table content
            update_table_content()
            
            logger.info("Database info loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading database info: {e}")
        finally:
            is_loading = False
    
    def on_table_select(e):
        """Handle table selection change."""
        nonlocal selected_table_name, current_table_data
        
        selected_table_name = e.control.value
        logger.info(f"Selected table: {selected_table_name}")
        
        async def load_table_data():
            try:
                current_table_data = await page.run_thread(get_table_data, selected_table_name)
                
                # Update table info and content
                table_info_text.value = f"Table: {selected_table_name}"
                rows_count_text.value = f"{len(current_table_data.get('rows', []))} rows"
                
                table_info_text.update()
                rows_count_text.update()
                
                update_table_content()
                
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Switched to table: {selected_table_name}"),
                    bgcolor=ft.Colors.GREEN
                )
                page.snack_bar.open = True
                page.update()
                
            except Exception as e:
                logger.error(f"Error loading table data: {e}")
        
        page.run_task(load_table_data)
    
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
            await asyncio.sleep(ASYNC_DELAY)  # Simulate export operation
            logger.info(f"Exported table: {table_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to export table {table_name}: {e}")
            return False
    
    def on_export_table(e):
        """Handle table export."""
        logger.info(f"Exporting table: {selected_table_name}")
        
        async def async_export():
            try:
                success = await export_table_async(selected_table_name)
                message = f"Table {selected_table_name} exported to CSV" if success else f"Failed to export table {selected_table_name}"
                color = ft.Colors.GREEN if success else ft.Colors.RED
                
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
        # Header
        ft.Row([
            ft.Icon(ft.Icons.STORAGE, size=24),
            ft.Text("Database Browser", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Refresh Database",
                on_click=on_refresh_table
            )
        ]),
        ft.Divider(),
        
        # Database statistics
        ft.Text("Database Statistics", size=18, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow([
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.STORAGE, size=24, color=ft.Colors.BLUE),
                            ft.Text("Status", size=12, weight=ft.FontWeight.W_500),
                            status_text
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
                            tables_text
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
                            records_text
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
                            size_text
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=15
                    )
                )
            ], col={"sm": 6, "md": 3})
        ]),
        ft.Divider(),
        
        # Table controls
        ft.Row([
            ft.Text("Select Table:", size=16, weight=ft.FontWeight.W_500),
            table_dropdown,
            ft.Container(expand=True),
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
        ], spacing=20),
        
        # Table info
        ft.Row([
            table_info_text,
            ft.Text("•", size=14, color=ft.Colors.ON_SURFACE),
            rows_count_text,
            ft.Container(expand=True),
            last_updated_text
        ]),
        
        # Table content in scrollable container
        table_container
        
    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)
    
    # Initialize data loading
    page.run_task(load_database_info_async)
    
    return main_view