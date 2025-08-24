#!/usr/bin/env python3
"""
Database View Component
Material Design 3 view for database management and monitoring.
"""

import flet as ft
from typing import List, Dict, Any


class DatabaseView:
    """Database view with monitoring and management capabilities"""
    
    def __init__(self, server_bridge):
        self.server_bridge = server_bridge
        self.db_stats = {
            "total_records": 12450,
            "tables": 8,
            "indexes": 16,
            "size": "2.4 GB",
            "last_backup": "2025-08-23 14:30:22"
        }
        
        self.table_data = [
            {"name": "clients", "records": 42, "size": "1.2 MB"},
            {"name": "files", "records": 12450, "size": "2.1 GB"},
            {"name": "transfers", "records": 893, "size": "32.5 MB"},
            {"name": "logs", "records": 5678, "size": "156.3 MB"},
            {"name": "users", "records": 23, "size": "45.7 KB"},
        ]
    
    def _get_container_color(self):
        """Get the container color from theme or fallback to teal"""
        try:
            from flet_server_gui.ui.theme_m3 import TOKENS
            return TOKENS.get("container", "#38A298")
        except ImportError:
            return "#38A298"
    
    def build(self) -> ft.Control:
        """Build the database view with M3 compliance and theme integration"""
        
        # Database stats cards
        stats_cards = ft.ResponsiveRow([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.TABLE_CHART, size=32),
                        ft.Text("Total Records", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text(f"{self.db_stats['total_records']:,}", style=ft.TextThemeStyle.DISPLAY_MEDIUM, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 3},
                elevation=2
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.TABLE_ROWS, size=32),
                        ft.Text("Tables", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text(str(self.db_stats['tables']), style=ft.TextThemeStyle.DISPLAY_MEDIUM, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 3},
                elevation=2
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.FORMAT_LIST_BULLETED, size=32),
                        ft.Text("Indexes", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text(str(self.db_stats['indexes']), style=ft.TextThemeStyle.DISPLAY_MEDIUM, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 3},
                elevation=2
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.STORAGE, size=32),
                        ft.Text("Size", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text(self.db_stats['size'], style=ft.TextThemeStyle.DISPLAY_MEDIUM, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                    # Use container color to showcase the custom teal color
                    bgcolor=self._get_container_color(),
                    border_radius=12
                ),
                col={"sm": 6, "md": 3},
                elevation=2
            ),
        ], spacing=20)
        
        # Tables data table
        tables_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Table Name")),
                ft.DataColumn(ft.Text("Records")),
                ft.DataColumn(ft.Text("Size")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Row([
                            ft.Icon(ft.Icons.TABLE_VIEW),
                            ft.Text(table["name"])
                        ])),
                        ft.DataCell(ft.Text(f"{table['records']:,}")),
                        ft.DataCell(ft.Text(table["size"])),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.Icons.VISIBILITY, tooltip="View Data",
                                            animate_scale=100, on_click=lambda e, t=table: self._on_view_table_data(t)),
                                ft.IconButton(ft.Icons.EDIT, tooltip="Edit Schema",
                                            animate_scale=100, on_click=lambda e, t=table: self._on_edit_table_schema(t)),
                                ft.IconButton(ft.Icons.DELETE, tooltip="Drop Table",
                                            animate_scale=100, on_click=lambda e, t=table: self._on_drop_table(t)),
                            ])
                        ),
                    ]
                )
                for table in self.table_data
            ]
        )
        
        # Wrap table in a scrollable container
        table_container = ft.Container(
            content=tables_table,
            padding=20,
            border_radius=8,
        )
        
        # Header with title and controls
        header = ft.Row([
            ft.Text("Database", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.IconButton(ft.Icons.REFRESH, tooltip="Refresh",
                         animate_scale=100, on_click=self._on_refresh),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Database controls
        db_controls = ft.Row([
            ft.FilledButton("Backup Database", icon=ft.Icons.BACKUP,
                           animate_scale=100, on_click=self._on_backup_database),
            ft.OutlinedButton("Optimize", icon=ft.Icons.AUTO_FIX_HIGH,
                             animate_scale=100, on_click=self._on_optimize_database),
            ft.OutlinedButton("Analyze", icon=ft.Icons.TROUBLESHOOT,
                             animate_scale=100, on_click=self._on_analyze_database),
        ])
        
        # Last backup info
        backup_info = ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CLOUD_DOWNLOAD, size=24),
                    ft.Text("Last Backup:", weight=ft.FontWeight.BOLD),
                    ft.Text(self.db_stats['last_backup']),
                    ft.TextButton("Restore", icon=ft.Icons.RESTORE,
                                 animate_scale=100, on_click=self._on_restore_backup),
                ], spacing=10),
                padding=15,
            ),
            elevation=2
        )
        
        # Add animation to the entire view
        view_content = ft.Column([
            header,
            ft.Divider(),
            stats_cards,
            ft.Divider(),
            backup_info,
            ft.Divider(),
            db_controls,
            ft.Divider(),
            table_container,
        ], spacing=20, expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        
        # Add entrance animation
        view_content.opacity = 0
        view_content.animate_opacity = 300
        
        return view_content

    def _on_view_table_data(self, table):
        """Handle view table data"""
        print(f"Viewing data for table: {table['name']}")
        # In a real implementation, this would show the table data

    def _on_edit_table_schema(self, table):
        """Handle edit table schema"""
        print(f"Editing schema for table: {table['name']}")
        # In a real implementation, this would open a schema editor

    def _on_drop_table(self, table):
        """Handle drop table"""
        print(f"Dropping table: {table['name']}")
        # In a real implementation, this would show a confirmation dialog and drop the table

    def _on_refresh(self, e):
        """Handle refresh button click"""
        print("Refreshing database view")
        # In a real implementation, this would refresh all database information

    def _on_backup_database(self, e):
        """Handle backup database button click"""
        print("Backing up database")
        # In a real implementation, this would start a database backup

    def _on_optimize_database(self, e):
        """Handle optimize database button click"""
        print("Optimizing database")
        # In a real implementation, this would run database optimization

    def _on_analyze_database(self, e):
        """Handle analyze database button click"""
        print("Analyzing database")
        # In a real implementation, this would run database analysis

    def _on_restore_backup(self, e):
        """Handle restore backup button click"""
        print("Restoring database backup")
        # In a real implementation, this would show backup options and restore selected backup

    def show_view(self):
        """Show the view with animation"""
        content = self.build()
        content.opacity = 0
        return content