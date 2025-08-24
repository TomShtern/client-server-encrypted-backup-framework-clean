#!/usr/bin/env python3
"""
Real Data Files Component for Flet Server GUI
Displays actual file data from the database with real filenames, sizes, and client info.
"""

import flet as ft
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..utils.server_bridge import ServerBridge


class RealDataFilesView:
    """Component for displaying real file data from the database."""
    
    def __init__(self, server_bridge: ServerBridge):
        self.server_bridge = server_bridge
        self.files_table = None
        self.refresh_button = None
        self.status_text = None
        self.search_field = None
        self.all_files = []  # Store all files for filtering
        
    def build(self) -> ft.Control:
        """Build the real data files view."""
        # Status indicator
        self.status_text = ft.Text(
            "Loading real file data...",
            size=14,
            color=ft.Colors.BLUE_600
        )
        
        # Search field
        self.search_field = ft.TextField(
            label="Search files...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.filter_files,
            width=300,
        )
        
        # Refresh button
        self.refresh_button = ft.ElevatedButton(
            "Refresh File Data",
            icon=ft.Icons.REFRESH,
            on_click=self.refresh_data,
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE
        )
        
        # Files data table
        self.files_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Filename", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Client", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Upload Date", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Verified", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        )
        
        # Container with scrollable table
        table_container = ft.Container(
            content=ft.Column([
                self.files_table
            ], scroll=ft.ScrollMode.AUTO),
            height=450,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10,
        )
        
        # Main container
        return ft.Container(
            content=ft.Column([
                ft.Text("Real File Data", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.status_text,
                ft.Row([
                    self.search_field,
                    self.refresh_button,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),  # Spacer
                table_container,
            ], spacing=10),
            padding=20,
        )
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        elif size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def format_date(self, date_str: str) -> str:
        """Format date string for display."""
        try:
            if date_str:
                # Try to parse ISO format
                if 'T' in date_str:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    date_obj = datetime.fromisoformat(date_str)
                return date_obj.strftime('%Y-%m-%d %H:%M')
        except Exception:
            pass
        return date_str or "Unknown"
    
    def filter_files(self, e=None):
        """Filter files based on search term."""
        search_term = self.search_field.value.lower() if self.search_field.value else ""
        
        if not search_term:
            # Show all files
            self.populate_table(self.all_files)
        else:
            # Filter files
            filtered_files = [
                file_info for file_info in self.all_files
                if search_term in file_info.get('filename', '').lower() or
                   search_term in file_info.get('client', '').lower()
            ]
            self.populate_table(filtered_files)
    
    def populate_table(self, files: List[Dict[str, Any]]):
        """Populate the table with file data."""
        # Clear existing rows
        self.files_table.rows.clear()
        
        if not files:
            # No files found
            self.files_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("No files found", italic=True)),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            )
        else:
            # Add file data
            for file_info in files:
                # Format file size
                size_bytes = file_info.get('size', 0) or 0
                size_display = self.format_file_size(size_bytes)
                
                # Format upload date
                date_display = self.format_date(file_info.get('date', ''))
                
                # Verification status
                verified = file_info.get('verified', False)
                verified_display = "✅ Yes" if verified else "❌ No"
                verified_color = ft.Colors.GREEN_600 if verified else ft.Colors.RED_600
                
                # Add row to table
                self.files_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(
                            file_info.get('filename', 'Unknown'), 
                            weight=ft.FontWeight.BOLD,
                            tooltip=file_info.get('path', '')
                        )),
                        ft.DataCell(ft.Text(
                            file_info.get('client', 'Unknown'),
                            color=ft.Colors.BLUE_600
                        )),
                        ft.DataCell(ft.Text(size_display)),
                        ft.DataCell(ft.Text(date_display, size=12)),
                        ft.DataCell(ft.Text(verified_display, color=verified_color)),
                    ])
                )
        
        # Update handled by parent
    
    def refresh_data(self, e=None):
        """Refresh file data from the server."""
        try:
            self.status_text.value = "🔄 Refreshing file data..."
            self.status_text.color = ft.Colors.BLUE_600
            # Update handled by parent
            
            # Get real file data
            files = self.server_bridge.get_file_list()
            self.all_files = files
            
            if not files:
                # No files found
                self.all_files = []
                self.populate_table([])
                self.status_text.value = "⚠️ No files found in database"
                self.status_text.color = ft.Colors.ORANGE_600
            else:
                # Calculate statistics
                total_size = sum(f.get('size', 0) or 0 for f in files)
                verified_count = sum(1 for f in files if f.get('verified', False))
                
                # Show files
                self.populate_table(files)
                
                # Update status
                mode_text = "📊 Mock Data" if self.server_bridge.is_mock_mode() else "🗄️ Real Database"
                size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
                self.status_text.value = (
                    f"✅ Found {len(files)} files, {verified_count} verified, "
                    f"{size_mb:.1f} MB total ({mode_text})"
                )
                self.status_text.color = ft.Colors.GREEN_600
            
            # Update handled by parent
            
        except Exception as e:
            self.status_text.value = f"❌ Error loading files: {str(e)}"
            self.status_text.color = ft.Colors.RED_600
            # Update handled by parent
            print(f"[ERROR] Failed to refresh file data: {e}")
    


class FileTypeBreakdownCard:
    """Card showing breakdown of files by type."""
    
    def __init__(self, server_bridge: ServerBridge):
        self.server_bridge = server_bridge
        
    def build(self) -> ft.Control:
        """Build the file type breakdown card."""
        try:
            files = self.server_bridge.get_file_list()
            
            if not files:
                return ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("File Types", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("No files to analyze", italic=True, color=ft.Colors.GREY_600),
                        ], spacing=8),
                        padding=20,
                    ),
                    elevation=2,
                )
            
            # Analyze file types
            file_types = {}
            for file_info in files:
                filename = file_info.get('filename', '')
                if '.' in filename:
                    ext = filename.rsplit('.', 1)[-1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
                else:
                    file_types['no extension'] = file_types.get('no extension', 0) + 1
            
            # Sort by count
            sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]  # Top 5
            
            # Create breakdown display
            breakdown_items = []
            for ext, count in sorted_types:
                percentage = (count / len(files)) * 100
                breakdown_items.append(
                    ft.Row([
                        ft.Text(f".{ext}", weight=ft.FontWeight.BOLD, width=80),
                        ft.Text(f"{count} files ({percentage:.1f}%)", size=14),
                    ])
                )
            
            data_source = "📊 Mock Data" if self.server_bridge.is_mock_mode() else "🗄️ Real Database"
            
        except Exception as e:
            breakdown_items = [ft.Text(f"Error: {str(e)}", color=ft.Colors.RED_600)]
            data_source = "❌ Error"
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("File Type Breakdown", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    *breakdown_items,
                    ft.Divider(),
                    ft.Text(data_source, size=12, color=ft.Colors.GREY_600, italic=True),
                ], spacing=8),
                padding=20,
            ),
            elevation=2,
        )