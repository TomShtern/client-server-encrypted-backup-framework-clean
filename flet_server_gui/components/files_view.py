#!/usr/bin/env python3
"""
Files View Component
Material Design 3 view for managing files.
"""

import flet as ft
from typing import List, Dict, Any


class FilesView:
    """Files view with file management capabilities"""
    
    def __init__(self, server_bridge):
        self.server_bridge = server_bridge
        self.files_data = [
            {"name": "document1.pdf", "size": "2.4 MB", "date": "2025-08-20", "owner": "client_001"},
            {"name": "backup_data.zip", "size": "15.7 MB", "date": "2025-08-19", "owner": "client_002"},
            {"name": "config.json", "size": "1.2 KB", "date": "2025-08-18", "owner": "client_003"},
            {"name": "image_gallery.png", "size": "5.8 MB", "date": "2025-08-17", "owner": "client_001"},
            {"name": "database_backup.sql", "size": "42.3 MB", "date": "2025-08-16", "owner": "client_004"},
        ]
    
    def build(self) -> ft.Control:
        """Build the files view with M3 compliance and theme integration"""
        
        # Create data table for files
        files_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("File Name")),
                ft.DataColumn(ft.Text("Size")),
                ft.DataColumn(ft.Text("Date")),
                ft.DataColumn(ft.Text("Owner")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Row([
                            ft.Icon(ft.Icons.DESCRIPTION),
                            ft.Text(file["name"])
                        ])),
                        ft.DataCell(ft.Text(file["size"])),
                        ft.DataCell(ft.Text(file["date"])),
                        ft.DataCell(ft.Text(file["owner"])),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.Icons.DOWNLOAD, tooltip="Download",
                                            animate_scale=100, on_click=lambda e, f=file: self._on_download_file(f)),
                                ft.IconButton(ft.Icons.DELETE, tooltip="Delete",
                                            animate_scale=100, on_click=lambda e, f=file: self._on_delete_file(f)),
                                ft.IconButton(ft.Icons.INFO, tooltip="Details",
                                            animate_scale=100, on_click=lambda e, f=file: self._on_file_details(f)),
                            ])
                        ),
                    ]
                )
                for file in self.files_data
            ],
            # Use theme colors for table
            heading_row_color=ft.Colors.PRIMARY_CONTAINER if not hasattr(ft, 'Colors') else None
        )
        
        # Wrap table in a scrollable container
        table_container = ft.Container(
            content=files_table,
            padding=20,
            border_radius=8,
        )
        
        # Add search and filter controls
        search_bar = ft.TextField(
            label="Search files...",
            icon=ft.Icons.SEARCH,
            expand=True,
            # Add animation for text field interactions
            animate_scale=100
        )
        
        filter_chips = ft.Row([
            ft.Chip(label=ft.Text("All Files"), on_click=self._on_filter_all,
                   animate_scale=100),
            ft.Chip(label=ft.Text("PDF"), on_click=self._on_filter_pdf,
                   animate_scale=100),
            ft.Chip(label=ft.Text("Images"), on_click=self._on_filter_images,
                   animate_scale=100),
            ft.Chip(label=ft.Text("Archives"), on_click=self._on_filter_archives,
                   animate_scale=100),
        ])
        
        # Header with title and controls
        header = ft.Row([
            ft.Text("Files", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.IconButton(ft.Icons.REFRESH, tooltip="Refresh",
                         animate_scale=100, on_click=self._on_refresh),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Controls row with gradient button if theme is available
        try:
            from flet_server_gui.ui.theme_m3 import gradient_button
            upload_button = gradient_button(
                ft.Row([ft.Icon(ft.Icons.UPLOAD), ft.Text("Upload File")]),
                on_click=self._on_upload_file
            )
        except ImportError:
            upload_button = ft.FilledButton("Upload File", icon=ft.Icons.UPLOAD,
                                          animate_scale=100, on_click=self._on_upload_file)
        
        controls_row = ft.Row([
            search_bar,
            upload_button,
        ])
        
        # Add animation to the entire view
        view_content = ft.Column([
            header,
            ft.Divider(),
            controls_row,
            filter_chips,
            ft.Divider(),
            table_container,
        ], spacing=20, expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        
        # Add entrance animation
        view_content.opacity = 0
        view_content.animate_opacity = 300
        
        return view_content

    def _on_download_file(self, file):
        """Handle file download"""
        print(f"Downloading {file['name']}")
        # In a real implementation, this would trigger a file download

    def _on_delete_file(self, file):
        """Handle file deletion"""
        print(f"Deleting {file['name']}")
        # In a real implementation, this would show a confirmation dialog and delete the file

    def _on_file_details(self, file):
        """Handle file details view"""
        print(f"Viewing details for {file['name']}")
        # In a real implementation, this would show a detailed view of the file

    def _on_filter_all(self, e):
        """Handle filter all files"""
        print("Filtering: All files")
        # In a real implementation, this would filter the file list

    def _on_filter_pdf(self, e):
        """Handle filter PDF files"""
        print("Filtering: PDF files")
        # In a real implementation, this would filter the file list

    def _on_filter_images(self, e):
        """Handle filter image files"""
        print("Filtering: Image files")
        # In a real implementation, this would filter the file list

    def _on_filter_archives(self, e):
        """Handle filter archive files"""
        print("Filtering: Archive files")
        # In a real implementation, this would filter the file list

    def _on_refresh(self, e):
        """Handle refresh button click"""
        print("Refreshing files list")
        # In a real implementation, this would refresh the file list from the server

    def _on_upload_file(self, e):
        """Handle upload file button click"""
        print("Upload file clicked")
        # In a real implementation, this would open a file dialog and upload the selected file

    def show_view(self):
        """Show the view with animation"""
        content = self.build()
        content.opacity = 0
        return content