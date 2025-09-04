#!/usr/bin/env python3
"""
Database View for FletV2
An improved implementation using ft.UserControl for better state management.
"""

import flet as ft
from typing import List, Dict, Any
import asyncio
from utils.debug_setup import get_logger
from datetime import datetime
from config import ASYNC_DELAY

logger = get_logger(__name__)


class DatabaseView(ft.UserControl):
    """
    Database view using ft.UserControl for better state management.
    """
    
    def __init__(self, server_bridge, page: ft.Page):
        super().__init__()
        self.server_bridge = server_bridge
        self.page = page
        self.db_info = {}
        self.selected_table_name = "clients"
        self.current_table_data = {}
        self.is_loading = False
        self.last_updated = None
        
        # UI References
        self.table_container = None
        self.status_text = None
        self.table_dropdown = None
        self.last_updated_text = None
        
    def build(self):
        """Build the database view UI."""
        self.status_text = ft.Text(
            value="Loading database info...",
            color=ft.Colors.ON_SURFACE_VARIANT
        )
        
        self.last_updated_text = ft.Text(
            value="Last updated: Never",
            color=ft.Colors.ON_SURFACE,
            size=12
        )
        
        self.table_dropdown = ft.Dropdown(
            label="Database Table",
            value=self.selected_table_name,
            options=[
                ft.dropdown.Option("clients", "Clients"),
                ft.dropdown.Option("files", "Files"),
                ft.dropdown.Option("logs", "Logs")
            ],
            width=200,
            on_change=self._on_table_select
        )
        
        self.table_container = ft.Container(
            content=ft.Column([], scroll=ft.ScrollMode.AUTO),
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10
        )
        
        # Build the main view
        return ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.STORAGE, size=24),
                ft.Text("Database Browser", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refresh Database",
                    on_click=self._on_refresh_table
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
                                ft.Text("Unknown", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY, ref=ft.Ref[ft.Text]())
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
                                ft.Text("0", size=16, weight=ft.FontWeight.BOLD, ref=ft.Ref[ft.Text]())
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
                                ft.Text("0", size=16, weight=ft.FontWeight.BOLD, ref=ft.Ref[ft.Text]())
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
                                ft.Text("0 MB", size=16, weight=ft.FontWeight.BOLD, ref=ft.Ref[ft.Text]())
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
                self.table_dropdown,
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Export CSV",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=self._on_export_table
                ),
                ft.OutlinedButton(
                    "Backup",
                    icon=ft.Icons.BACKUP,
                    on_click=self._on_backup_database
                )
            ], spacing=20),
            # Table info
            ft.Row([
                ft.Text("Loading...", size=14, color=ft.Colors.PRIMARY, ref=ft.Ref[ft.Text]()),
                ft.Text("•", size=14, color=ft.Colors.ON_SURFACE),
                ft.Text("0 rows", size=14, color=ft.Colors.ON_SURFACE, ref=ft.Ref[ft.Text]()),
                ft.Container(expand=True),
                self.last_updated_text
            ]),
            # Table content in scrollable container
            self.table_container
        ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)
    
    async def _load_database_info_async(self):
        """Asynchronously load database info."""
        if self.is_loading:
            return
            
        self.is_loading = True
        try:
            # Show loading state
            self.status_text.value = "Loading database info..."
            self.status_text.update()
            
            # Load data asynchronously
            if self.server_bridge:
                self.db_info = await self.page.run_thread(self.server_bridge.get_database_info)
            else:
                # Fallback mock data
                await asyncio.sleep(ASYNC_DELAY)
                self.db_info = {
                    "status": "Connected",
                    "tables": 5,
                    "records": 1250,
                    "size": "45.2 MB"
                }
            
            # Load table data
            self.current_table_data = await self.page.run_thread(self._get_table_data, self.selected_table_name)
            
            # Update last updated timestamp
            self.last_updated = datetime.now()
            self.last_updated_text.value = f"Last updated: {self.last_updated.strftime('%H:%M:%S')}"
            
            # Update UI
            self._update_ui()
            self.status_text.value = "Database info loaded"
            
        except Exception as e:
            logger.error(f"Error loading database info: {e}")
            self.status_text.value = "Error loading database info"
        finally:
            self.is_loading = False
            self.update()
    
    def _get_table_data(self, table_name: str):
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
    
    def _update_ui(self):
        """Update UI with loaded data."""
        # Update database statistics cards
        # Status card
        status_text_control = self.controls[3].controls[0].controls[0].content.content.controls[2]  # Status text
        status_text_control.value = self.db_info.get("status", "Unknown")
        status_text_control.color = ft.Colors.GREEN if self.db_info.get("status") == "Connected" else ft.Colors.RED
        
        # Tables card
        tables_text_control = self.controls[3].controls[1].controls[0].content.content.controls[2]  # Tables text
        tables_text_control.value = str(self.db_info.get("tables", 0))
        
        # Records card
        records_text_control = self.controls[3].controls[2].controls[0].content.content.controls[2]  # Records text
        records_text_control.value = str(self.db_info.get("records", 0))
        
        # Size card
        size_text_control = self.controls[3].controls[3].controls[0].content.content.controls[2]  # Size text
        size_text_control.value = self.db_info.get("size", "0 MB")
        
        # Update table info
        table_info_control = self.controls[7].controls[0]  # Table name text
        table_info_control.value = f"Table: {self.selected_table_name}"
        
        rows_info_control = self.controls[7].controls[2]  # Rows count text
        rows_info_control.value = f"{len(self.current_table_data.get('rows', []))} rows"
        
        # Update table content
        self._update_table_content()
    
    def _update_table_content(self):
        """Update table content display."""
        if not self.current_table_data.get("rows"):
            empty_content = ft.Container(
                content=ft.Text("No data available", size=16, text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center,
                height=200
            )
            self.table_container.content.controls = [empty_content]
            return
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(col.upper(), weight=ft.FontWeight.BOLD))
                for col in self.current_table_data["columns"]
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row.get(col, ""))))
                        for col in self.current_table_data["columns"]
                    ]
                )
                for row in self.current_table_data["rows"]
            ],
            heading_row_color=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            data_row_min_height=45
        )
        
        self.table_container.content.controls = [table]
    
    def _on_table_select(self, e):
        self.selected_table_name = e.control.value
        logger.info(f"Selected table: {self.selected_table_name}")
        
        # Load table data asynchronously
        async def load_table_data():
            try:
                self.current_table_data = await self.page.run_thread(self._get_table_data, self.selected_table_name)
                self._update_table_content()
                
                # Update table info
                table_info_control = self.controls[7].controls[0]  # Table name text
                table_info_control.value = f"Table: {self.selected_table_name}"
                
                rows_info_control = self.controls[7].controls[2]  # Rows count text
                rows_info_control.value = f"{len(self.current_table_data.get('rows', []))} rows"
                
                self.update()
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Switched to table: {self.selected_table_name}"),
                    bgcolor=ft.Colors.GREEN
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as e:
                logger.error(f"Error loading table data: {e}")
        
        self.page.run_task(load_table_data)
    
    def _on_refresh_table(self, e):
        logger.info(f"Refreshing table: {self.selected_table_name}")
        self.page.run_task(self._load_database_info_async)
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Refreshing database info..."),
            bgcolor=ft.Colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    async def _export_table_async(self, table_name):
        """Async function to export a table."""
        try:
            # Simulate async operation
            await asyncio.sleep(ASYNC_DELAY)
            logger.info(f"Exported table: {table_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to export table {table_name}: {e}")
            return False

    def _on_export_table(self, e):
        logger.info(f"Exporting table: {self.selected_table_name}")
        
        async def async_export():
            try:
                success = await self._export_table_async(self.selected_table_name)
                if success:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Table {self.selected_table_name} exported to CSV"),
                        bgcolor=ft.Colors.GREEN
                    )
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Failed to export table {self.selected_table_name}"),
                        bgcolor=ft.Colors.RED
                    )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as e:
                logger.error(f"Error in export handler: {e}")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error exporting table {self.selected_table_name}"),
                    bgcolor=ft.Colors.RED
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        # Run async operation
        self.page.run_task(async_export)
    
    def _on_backup_database(self, e):
        logger.info("Database backup initiated")
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Database backup started"),
            bgcolor=ft.Colors.PURPLE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def did_mount(self):
        """Called when the control is added to the page."""
        self.page.run_task(self._load_database_info_async)


def create_database_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create database view using ft.UserControl.
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The database view
    """
    return DatabaseView(server_bridge, page)