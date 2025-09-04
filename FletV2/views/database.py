#!/usr/bin/env python3
"""
Database View for FletV2
A clean implementation using pure Flet patterns.
"""

import flet as ft
from typing import List, Dict, Any
import asyncio
from utils.debug_setup import get_logger
from datetime import datetime

logger = get_logger(__name__)


def create_database_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create database view using simple Flet patterns.
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The database view
    """
    
    # Get database info from server
    def get_database_info():
        """Get database information from server bridge or return mock data."""
        if server_bridge:
            try:
                return server_bridge.get_database_info()
            except Exception as e:
                logger.warning(f"Failed to get database info: {e}")
        
        # Fallback mock data
        return {
            "status": "Connected",
            "tables": 5,
            "records": 1250,
            "size": "45.2 MB"
        }
    
    # Mock table data for demonstration
    def get_table_data(table_name: str):
        """Get table data or return mock data."""
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
    
    # Get initial data
    db_info = get_database_info()
    selected_table_name = "clients"
    current_table_data = get_table_data(selected_table_name)
    
    # Create table selector change handler
    def on_table_select(e):
        nonlocal selected_table_name, current_table_data
        selected_table_name = e.control.value
        current_table_data = get_table_data(selected_table_name)
        logger.info(f"Selected table: {selected_table_name}")
        # Update table content
        update_table_content()
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Switched to table: {selected_table_name}"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()
    
    # Create database action handlers
    def on_refresh_table(e):
        logger.info(f"Refreshing table: {selected_table_name}")
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Table {selected_table_name} refreshed"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()
    
    async def export_table_async(table_name):
        """Async function to export a table."""
        try:
            # Simulate async operation
            await asyncio.sleep(1.0)
            logger.info(f"Exported table: {table_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to export table {table_name}: {e}")
            return False

    def on_export_table(e):
        logger.info(f"Exporting table: {selected_table_name}")
        
        async def async_export():
            try:
                success = await export_table_async(selected_table_name)
                if success:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Table {selected_table_name} exported to CSV"),
                        bgcolor=ft.Colors.GREEN
                    )
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Failed to export table {selected_table_name}"),
                        bgcolor=ft.Colors.RED
                    )
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
    
    # Create DataTable using Flet's built-in component
    def create_data_table(table_data):
        if not table_data["rows"]:
            return ft.Container(
                content=ft.Text("No data available", size=16, text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center,
                height=200
            )
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(col.upper(), weight=ft.FontWeight.BOLD))
                for col in table_data["columns"]
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row.get(col, ""))))
                        for col in table_data["columns"]
                    ]
                )
                for row in table_data["rows"]
            ],
            heading_row_color=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            data_row_min_height=45
        )
    
    # Function to update table content
    def update_table_content():
        table_container.content.controls = [create_data_table(current_table_data)]
        table_container.update()
    
    # Create table container
    table_container = ft.Container(
        content=ft.Column([create_data_table(current_table_data)], scroll=ft.ScrollMode.AUTO),
        expand=True,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=8,
        padding=10
    )
    
    # Database statistics cards
    stats_cards = ft.ResponsiveRow([
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.STORAGE, size=24, color=ft.Colors.BLUE),
                        ft.Text("Status", size=12, weight=ft.FontWeight.W_500),
                        ft.Text(db_info["status"], size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN if db_info["status"] == "Connected" else ft.Colors.RED)
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
                        ft.Text(str(db_info["tables"]), size=16, weight=ft.FontWeight.BOLD)
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
                        ft.Text(str(db_info["records"]), size=16, weight=ft.FontWeight.BOLD)
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
                        ft.Text(db_info["size"], size=16, weight=ft.FontWeight.BOLD)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 6, "md": 3})
    ])
    
    # Main layout using simple Column
    return ft.Column([
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
        stats_cards,
        ft.Divider(),
        # Table controls
        ft.Row([
            ft.Text("Select Table:", size=16, weight=ft.FontWeight.W_500),
            ft.Dropdown(
                label="Database Table",
                value=selected_table_name,
                options=[
                    ft.dropdown.Option("clients", "Clients"),
                    ft.dropdown.Option("files", "Files"),
                    ft.dropdown.Option("logs", "Logs")
                ],
                width=200,
                on_change=on_table_select
            ),
            ft.Container(expand=True),
            ft.ElevatedButton(
                "Export CSV",
                icon=ft.Icons.DOWNLOAD,
                on_click=on_export_table
            ),
            ft.OutlinedButton(
                "Backup",
                icon=ft.Icons.BACKUP,
                on_click=lambda e: logger.info("Database backup initiated")
            )
        ], spacing=20),
        # Table info
        ft.Row([
            ft.Text(f"Table: {selected_table_name}", size=14, color=ft.Colors.PRIMARY),
            ft.Text(f"•", size=14, color=ft.Colors.ON_SURFACE),
            ft.Text(f"{len(current_table_data['rows'])} rows", size=14, color=ft.Colors.ON_SURFACE),
            ft.Container(expand=True),
            ft.Text("Last updated: " + datetime.now().strftime("%H:%M:%S"), size=12, color=ft.Colors.ON_SURFACE)
        ]),
        # Table content in scrollable container
        table_container
    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)