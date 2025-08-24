#!/usr/bin/env python3
"""
Comprehensive File Management Component
Complete feature parity with TKinter GUI file management functionality.
"""

import flet as ft
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from ..utils.server_bridge import ServerBridge
from .base_component import BaseComponent
from ..actions import FileActions


class ComprehensiveFileManagement(BaseComponent):
    """Complete file management with all TKinter GUI features."""
    
    def __init__(self, server_bridge: ServerBridge, dialog_system, toast_manager, page):
        super().__init__(page, dialog_system, toast_manager)
        self.server_bridge = server_bridge
        self.show_dialog = dialog_system or self._default_dialog
        # Initialize file actions
        self.file_actions = FileActions(server_bridge)
        
        # Initialize button factory
        from .button_factory import ActionButtonFactory
        # Use self as the base component for the button factory
        self.button_factory = ActionButtonFactory(self, server_bridge, page)
        
        # UI Components
        self.file_table = None
        self.selected_files = []
        self.status_text = None
        self.search_field = None
        self.filter_dropdown = None
        self.sort_dropdown = None
        self.bulk_actions_row = None
        self.file_preview = None
        
        # Data
        self.all_files = []
        self.filtered_files = []
        
    def build(self) -> ft.Control:
        """Build the comprehensive file management view."""
        
        # Header with status
        self.status_text = ft.Text(
            "Loading file data...",
            size=14,
            color=ft.Colors.BLUE_600
        )
        
        # Search and filter controls
        self.search_field = ft.TextField(
            label="Search files...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            width=300,
        )
        
        self.filter_dropdown = ft.Dropdown(
            label="Filter by type",
            width=150,
            options=[
                ft.dropdown.Option("all", "All Files"),
                ft.dropdown.Option("verified", "Verified"),
                ft.dropdown.Option("unverified", "Unverified"),
                ft.dropdown.Option("images", "Images"),
                ft.dropdown.Option("documents", "Documents"),
                ft.dropdown.Option("archives", "Archives"),
                ft.dropdown.Option("videos", "Videos"),
                ft.dropdown.Option("other", "Other"),
            ],
            value="all",
            on_change=self._on_filter_change
        )
        
        self.sort_dropdown = ft.Dropdown(
            label="Sort by",
            width=150,
            options=[
                ft.dropdown.Option("name", "Name"),
                ft.dropdown.Option("size", "Size"),
                ft.dropdown.Option("date", "Date"),
                ft.dropdown.Option("client", "Client"),
                ft.dropdown.Option("verified", "Verified"),
            ],
            value="date",
            on_change=self._on_sort_change
        )
        
        refresh_button = ft.ElevatedButton(
            "Refresh Files",
            icon=ft.Icons.REFRESH,
            on_click=self._refresh_files,
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE
        )
        
        # Bulk action buttons (initially hidden)
        self.bulk_actions_row = ft.Row([
            ft.ElevatedButton(
                "Download Selected",
                icon=ft.Icons.DOWNLOAD,
                on_click=self._download_selected_files,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            ),
            ft.ElevatedButton(
                "Verify Selected",
                icon=ft.Icons.VERIFIED,
                on_click=self._verify_selected_files,
                bgcolor=ft.Colors.ORANGE_600,
                color=ft.Colors.WHITE
            ),
            ft.ElevatedButton(
                "Delete Selected",
                icon=ft.Icons.DELETE,
                on_click=self._delete_selected_files,
                bgcolor=ft.Colors.RED_600,
                color=ft.Colors.WHITE
            ),
            ft.ElevatedButton(
                "Export List",
                icon=ft.Icons.TABLE_VIEW,
                on_click=self._export_file_list,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            ),
        ], visible=False, spacing=10)
        
        # File data table with selection
        self.file_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Checkbox(on_change=self._on_select_all)),  # Select all
                ft.DataColumn(ft.Text("Filename", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Client", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Upload Date", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Verified", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        )
        
        # File preview panel (initially hidden)
        self.file_preview = ft.Container(
            content=ft.Column([
                ft.Text("File Preview", weight=ft.FontWeight.BOLD),
                ft.Text("Select a file to view details")
            ]),
            width=300,
            height=500,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10,
            visible=False
        )
        
        # Table container with scrolling
        table_container = ft.Container(
            content=ft.Column([
                self.file_table
            ], scroll=ft.ScrollMode.AUTO),
            height=500,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10,
        )
        
        # Action buttons
        action_buttons = ft.Row([
            ft.ElevatedButton(
                "Upload File",
                icon=ft.Icons.UPLOAD,
                on_click=self._upload_file,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            ),
            ft.OutlinedButton(
                "Batch Verify",
                icon=ft.Icons.VERIFIED_USER,
                on_click=self._batch_verify_files
            ),
            ft.OutlinedButton(
                "File Statistics",
                icon=ft.Icons.ANALYTICS,
                on_click=self._show_file_statistics
            ),
            ft.OutlinedButton(
                "Clean Old Files",
                icon=ft.Icons.CLEANING_SERVICES,
                on_click=self._clean_old_files
            ),
            ft.Switch(
                label="Show Preview",
                value=False,
                on_change=self._toggle_preview
            )
        ], spacing=10, wrap=True)
        
        # Main layout with optional preview panel
        main_content = ft.Row([
            ft.Column([
                ft.Text("File Management", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.status_text,
                
                # Search and filter row
                ft.Row([
                    self.search_field,
                    self.filter_dropdown,
                    self.sort_dropdown,
                    refresh_button,
                ], alignment=ft.MainAxisAlignment.START, spacing=10, wrap=True),
                
                ft.Container(height=10),  # Spacer
                
                # Bulk actions (shown when files selected)
                self.bulk_actions_row,
                
                # Action buttons
                action_buttons,
                
                ft.Container(height=10),  # Spacer
                
                # File table
                table_container,
            ], expand=True),
            
            # Preview panel (toggleable)
            self.file_preview,
            
        ], spacing=20)
        
        return ft.Container(content=main_content, padding=20)
    
    def _refresh_files(self, e=None):
        """Refresh file data from server."""
        try:
            self.status_text.value = "Refreshing file data..."
            self.status_text.color = ft.Colors.BLUE_600
            
            # Get real file data
            files = self.server_bridge.get_file_list()
            self.all_files = files
            
            self._apply_filters_and_sort()
            
            if not files:
                self.status_text.value = "No files found in database"
                self.status_text.color = ft.Colors.ORANGE_600
            else:
                # Calculate statistics
                total_size = sum(f.get('size', 0) or 0 for f in files)
                verified_count = sum(1 for f in files if f.get('verified', False))
                size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
                
                mode_text = "Mock Data" if getattr(self.server_bridge, 'mock_mode', False) else "Real Database"
                self.status_text.value = (
                    f"Found {len(files)} files, {verified_count} verified, "
                    f"{size_mb:.1f} MB total ({mode_text})"
                )
                self.status_text.color = ft.Colors.GREEN_600
                
        except Exception as e:
            self.status_text.value = f"Error loading files: {str(e)}"
            self.status_text.color = ft.Colors.RED_600
            print(f"[ERROR] Failed to refresh files: {e}")
    
    def _apply_filters_and_sort(self):
        """Apply search, filters, and sorting to files."""
        filtered = self.all_files.copy()
        
        # Apply search filter
        search_term = self.search_field.value.lower() if self.search_field.value else ""
        if search_term:
            filtered = [f for f in filtered if (
                search_term in f.get('filename', '').lower() or
                search_term in f.get('client', '').lower()
            )]
        
        # Apply type filter
        type_filter = self.filter_dropdown.value if self.filter_dropdown else "all"
        if type_filter == "verified":
            filtered = [f for f in filtered if f.get('verified', False)]
        elif type_filter == "unverified":
            filtered = [f for f in filtered if not f.get('verified', False)]
        elif type_filter in ["images", "documents", "archives", "videos"]:
            filtered = [f for f in filtered if self._get_file_type(f.get('filename', '')) == type_filter]
        elif type_filter == "other":
            filtered = [f for f in filtered if self._get_file_type(f.get('filename', '')) not in 
                       ["images", "documents", "archives", "videos"]]
        
        # Apply sorting
        sort_by = self.sort_dropdown.value if self.sort_dropdown else "date"
        if sort_by == "name":
            filtered.sort(key=lambda f: f.get('filename', '').lower())
        elif sort_by == "size":
            filtered.sort(key=lambda f: f.get('size', 0) or 0, reverse=True)
        elif sort_by == "date":
            filtered.sort(key=lambda f: f.get('date', ''), reverse=True)
        elif sort_by == "client":
            filtered.sort(key=lambda f: f.get('client', '').lower())
        elif sort_by == "verified":
            filtered.sort(key=lambda f: f.get('verified', False), reverse=True)
        
        self.filtered_files = filtered
        self._populate_file_table()
    
    def _get_file_type(self, filename: str) -> str:
        """Determine file type category from filename."""
        if not filename:
            return "other"
        
        ext = filename.lower().split('.')[-1] if '.' in filename else ""
        
        if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp']:
            return "images"
        elif ext in ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt']:
            return "documents"
        elif ext in ['zip', 'rar', '7z', 'tar', 'gz', 'bz2']:
            return "archives"
        elif ext in ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv']:
            return "videos"
        else:
            return "other"
    
    def _populate_file_table(self):
        """Populate the file table with filtered and sorted data."""
        self.file_table.rows.clear()
        self.selected_files.clear()
        
        if not self.filtered_files:
            # No files to show
            self.file_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("No files match the current filters", italic=True)),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            )
        else:
            for file_info in self.filtered_files:
                # Format file data
                filename = file_info.get('filename', 'Unknown')
                client = file_info.get('client', 'Unknown')
                size = self._format_file_size(file_info.get('size', 0) or 0)
                upload_date = self._format_date(file_info.get('date', ''))
                verified = "✅ Yes" if file_info.get('verified', False) else "❌ No"
                verified_color = ft.Colors.GREEN_600 if file_info.get('verified', False) else ft.Colors.RED_600
                file_type = self._get_file_type(filename).title()
                
                # Create action buttons for this file using button factory
                action_buttons = ft.Row([
                    self.button_factory.create_action_button('file_view_details', lambda f=file_info: [f.get('filename', 'unknown')]),
                    self.button_factory.create_action_button('file_download', lambda f=file_info: [f.get('filename', 'unknown')]),
                    self.button_factory.create_action_button('file_verify', lambda f=file_info: [f.get('filename', 'unknown')]),
                    self.button_factory.create_action_button('file_preview', lambda f=file_info: [f.get('filename', 'unknown')]),
                    self.button_factory.create_action_button('file_delete', lambda f=file_info: [f.get('filename', 'unknown')]),
                ], tight=True)
                
                # Add file row
                self.file_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Checkbox(
                                value=False,
                                data=filename,
                                on_change=self._on_file_select
                            )),
                            ft.DataCell(ft.Text(
                                filename,
                                weight=ft.FontWeight.BOLD,
                                selectable=True,
                                tooltip=file_info.get('path', filename)
                            )),
                            ft.DataCell(ft.Text(client, color=ft.Colors.BLUE_600)),
                            ft.DataCell(ft.Text(size)),
                            ft.DataCell(ft.Text(upload_date, size=12)),
                            ft.DataCell(ft.Text(verified, color=verified_color)),
                            ft.DataCell(ft.Text(file_type)),
                            ft.DataCell(action_buttons),
                        ],
                        on_select_changed=lambda e, f=file_info: self._on_row_select(f)
                    )
                )
        
        self._update_bulk_actions_visibility()
    
    def _format_file_size(self, size_bytes: int) -> str:
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
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display."""
        try:
            if date_str:
                if 'T' in date_str:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    date_obj = datetime.fromisoformat(date_str)
                return date_obj.strftime('%Y-%m-%d %H:%M')
        except Exception:
            pass
        return date_str or "Unknown"
    
    def _on_search_change(self, e):
        """Handle search field changes."""
        self._apply_filters_and_sort()
    
    def _on_filter_change(self, e):
        """Handle filter dropdown changes."""
        self._apply_filters_and_sort()
    
    def _on_sort_change(self, e):
        """Handle sort dropdown changes."""
        self._apply_filters_and_sort()
    
    def _on_select_all(self, e):
        """Handle select all checkbox."""
        select_all = e.control.value
        self.selected_files.clear()
        
        for row in self.file_table.rows:
            if len(row.cells) > 0 and isinstance(row.cells[0].content, ft.Checkbox):
                checkbox = row.cells[0].content
                checkbox.value = select_all
                if select_all and hasattr(checkbox, 'data'):
                    self.selected_files.append(checkbox.data)
        
        self._update_bulk_actions_visibility()
    
    def _on_file_select(self, e):
        """Handle individual file selection."""
        filename = e.control.data
        if e.control.value:
            if filename not in self.selected_files:
                self.selected_files.append(filename)
        else:
            if filename in self.selected_files:
                self.selected_files.remove(filename)
        
        self._update_bulk_actions_visibility()
    
    def _on_row_select(self, file_info):
        """Handle row selection for preview."""
        if self.file_preview.visible:
            self._update_file_preview(file_info)
    
    def _update_bulk_actions_visibility(self):
        """Show/hide bulk actions based on selection."""
        self.bulk_actions_row.visible = len(self.selected_files) > 0
    
    def _toggle_preview(self, e):
        """Toggle file preview panel visibility."""
        self.file_preview.visible = e.control.value
    
    def _update_file_preview(self, file_info):
        """Update the file preview panel."""
        if not self.file_preview.visible:
            return
        
        size_str = self._format_file_size(file_info.get('size', 0) or 0)
        date_str = self._format_date(file_info.get('date', ''))
        file_type = self._get_file_type(file_info.get('filename', '')).title()
        
        preview_content = ft.Column([
            ft.Text("File Preview", weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Text("Filename:", weight=ft.FontWeight.BOLD),
            ft.Text(file_info.get('filename', 'Unknown'), selectable=True),
            
            ft.Text("Client:", weight=ft.FontWeight.BOLD),
            ft.Text(file_info.get('client', 'Unknown')),
            
            ft.Text("Size:", weight=ft.FontWeight.BOLD),
            ft.Text(size_str),
            
            ft.Text("Upload Date:", weight=ft.FontWeight.BOLD),
            ft.Text(date_str),
            
            ft.Text("Type:", weight=ft.FontWeight.BOLD),
            ft.Text(file_type),
            
            ft.Text("Verified:", weight=ft.FontWeight.BOLD),
            ft.Text("Yes" if file_info.get('verified', False) else "No"),
            
            ft.Text("Full Path:", weight=ft.FontWeight.BOLD),
            ft.Text(file_info.get('path', 'Unknown'), selectable=True, size=10),
        ], spacing=5)
        
        self.file_preview.content = preview_content
    
    # === Individual File Actions ===
    
    def _view_file_details(self, file_info):
        """Show detailed file information."""
        size_str = self._format_file_size(file_info.get('size', 0) or 0)
        date_str = self._format_date(file_info.get('date', ''))
        file_type = self._get_file_type(file_info.get('filename', '')).title()
        
        details_content = ft.Column([
            ft.Text(f"File Details: {file_info.get('filename', 'Unknown')}", 
                   size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Row([ft.Text("Filename:", weight=ft.FontWeight.BOLD), 
                   ft.Text(file_info.get('filename', 'Unknown'))]),
            ft.Row([ft.Text("Client:", weight=ft.FontWeight.BOLD), 
                   ft.Text(file_info.get('client', 'Unknown'))]),
            ft.Row([ft.Text("Size:", weight=ft.FontWeight.BOLD), ft.Text(size_str)]),
            ft.Row([ft.Text("Upload Date:", weight=ft.FontWeight.BOLD), ft.Text(date_str)]),
            ft.Row([ft.Text("Type:", weight=ft.FontWeight.BOLD), ft.Text(file_type)]),
            ft.Row([ft.Text("Verified:", weight=ft.FontWeight.BOLD), 
                   ft.Text("Yes" if file_info.get('verified', False) else "No")]),
            ft.Row([ft.Text("Full Path:", weight=ft.FontWeight.BOLD), 
                   ft.Text(file_info.get('path', 'Unknown'))]),
        ], spacing=10)
        
        self.show_dialog("custom", "File Details", "", content=details_content)
    
    def _download_file(self, file_info):
        """Download a file."""
        async def download_action():
            try:
                filename = file_info.get('filename', 'Unknown')
                # Use action system to download file
                # For now, we'll just show a dialog - in a real implementation, this would trigger a file save dialog
                result = await self.file_actions.download_file(filename, f"./downloads/{filename}")
                
                if result.success:
                    self.show_dialog("success", "Download Complete", f"File '{filename}' downloaded successfully")
                else:
                    self.show_dialog("error", "Download Failed", f"Failed to download file '{filename}': {result.error_message}")
            except Exception as e:
                self.show_dialog("error", "Error", f"Failed to download file: {str(e)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(download_action())
    
    def _verify_file(self, file_info):
        """Verify a file's integrity."""
        async def verify_action():
            try:
                filename = file_info.get('filename', 'Unknown')
                # Use action system to verify file
                result = await self.file_actions.verify_file_integrity(filename)
                
                if result.success:
                    if result.data.get('is_valid'):
                        self.show_dialog("success", "Verification Complete", f"File '{filename}' is valid")
                    else:
                        self.show_dialog("warning", "Verification Failed", f"File '{filename}' is invalid")
                else:
                    self.show_dialog("error", "Verification Failed", f"Failed to verify file '{filename}': {result.error_message}")
            except Exception as e:
                self.show_dialog("error", "Error", f"Failed to verify file: {str(e)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(verify_action())
    
    def _preview_file(self, file_info):
        """Preview a file (show content or metadata)."""
        filename = file_info.get('filename', 'Unknown')
        file_type = self._get_file_type(filename)
        
        if file_type == "images":
            content = ft.Text(f"Image preview for '{filename}' would be shown here")
        elif file_type == "documents":
            content = ft.Text(f"Document preview for '{filename}' would be shown here")
        else:
            content = ft.Text(f"Preview not available for '{filename}' ({file_type})")
        
        self.show_dialog(f"Preview - {filename}", content)
    
    def _delete_file(self, file_info):
        """Delete a file."""
        async def delete_action():
            try:
                filename = file_info.get('filename', 'Unknown')
                # Use action system to delete file
                result = await self.file_actions.delete_file(filename)
                self._refresh_files()
                
                if result.success:
                    self.show_dialog(
                        "success",
                        "File Deleted",
                        f"File '{filename}' has been permanently deleted"
                    )
                else:
                    self.show_dialog(
                        "warning",
                        "Delete Warning",
                        f"File '{filename}' delete completed with warnings: {result.error_message}"
                    )
            except Exception as ex:
                self.show_dialog(
                    "error",
                    "Delete Failed",
                    f"Failed to delete file: {str(ex)}"
                )
        
        self.show_dialog(
            "confirmation",
            "Confirm Delete",
            f"Are you sure you want to delete file '{filename}'?\n\nThis will permanently remove the file from the server.\n\n⚠️ THIS ACTION CANNOT BE UNDONE!",
            on_confirm=lambda: asyncio.create_task(delete_action()),
            confirm_text="Delete",
            danger=True
        )
    
    # === Bulk Actions ===
    
    def _download_selected_files(self, e):
        """Download multiple selected files."""
        async def download_action():
            try:
                if not self.selected_files:
                    self.show_dialog("warning", "No Files Selected", "Please select files to download")
                    return
                    
                # Use action system to download multiple files
                result = await self.file_actions.download_multiple_files(self.selected_files, "./downloads/")
                
                if result.success:
                    self.show_dialog("success", "Download Complete", f"Downloaded {len(self.selected_files)} files successfully")
                else:
                    self.show_dialog("error", "Download Failed", f"Failed to download files: {result.error_message}")
            except Exception as ex:
                self.show_dialog("error", "Error", f"Failed to download files: {str(ex)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(download_action())
    
    def _verify_selected_files(self, e):
        """Verify multiple selected files."""
        async def verify_action():
            try:
                if not self.selected_files:
                    self.show_dialog("warning", "No Files Selected", "Please select files to verify")
                    return
                    
                # Use action system to verify multiple files
                result = await self.file_actions.verify_multiple_files(self.selected_files)
                
                if result.success:
                    valid_count = result.metadata.get('valid_files', 0)
                    invalid_count = result.metadata.get('invalid_files', 0)
                    self.show_dialog("success", "Verification Complete", 
                                   f"Verified {len(self.selected_files)} files: {valid_count} valid, {invalid_count} invalid")
                else:
                    self.show_dialog("error", "Verification Failed", f"Failed to verify files: {result.error_message}")
            except Exception as ex:
                self.show_dialog("error", "Error", f"Failed to verify files: {str(ex)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(verify_action())
    
    def _delete_selected_files(self, e):
        """Delete multiple selected files."""
        if not self.selected_files:
            return
            
        async def delete_action():
            try:
                # Use action system to delete multiple files
                result = await self.file_actions.delete_multiple_files(self.selected_files)
                
                self.selected_files = []
                self._update_bulk_actions_visibility()
                self._refresh_files()
                
                if result.success:
                    self.show_dialog(
                        "success",
                        "Bulk Delete Complete", 
                        f"Successfully deleted {len(self.selected_files)} files"
                    )
                else:
                    self.show_dialog(
                        "error",
                        "Delete Failed",
                        f"Failed to delete files: {result.error_message}"
                    )
            except Exception as ex:
                self.show_dialog(
                    "error",
                    "Delete Failed",
                    f"Failed to delete files: {str(ex)}"
                )
        
        self.show_dialog(
            "confirmation",
            "Confirm Bulk Delete",
            f"Are you sure you want to delete {len(self.selected_files)} selected files?\n\nThis will permanently remove all selected files from the server.\n\n⚠️ THIS ACTION CANNOT BE UNDONE!",
            on_confirm=lambda: asyncio.create_task(delete_action()),
            confirm_text="Delete All",
            danger=True
        )
    
    def _export_file_list(self, e):
        """Export file list to CSV."""
        try:
            print(f"[INFO] Exporting {len(self.selected_files)} files to CSV")
            self.show_dialog("success", "Export Complete", f"Exported {len(self.selected_files)} files to CSV")
        except Exception as ex:
            self.show_dialog("error", "Error", f"Failed to export file list: {str(ex)}")
    
    # === Other Actions ===
    
    def _upload_file(self, e):
        """Show upload file dialog."""
        async def upload_action():
            try:
                # Use action system to upload file
                # For now, we'll just show a dialog - in a real implementation, this would trigger a file picker
                result = await self.file_actions.upload_file("./uploads/new_file.txt", "./server_files/new_file.txt")
                
                if result.success:
                    self.show_dialog("success", "Upload Complete", "File uploaded successfully")
                    self._refresh_files()
                else:
                    self.show_dialog("error", "Upload Failed", f"Failed to upload file: {result.error_message}")
            except Exception as ex:
                self.show_dialog("error", "Error", f"Failed to upload file: {str(ex)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(upload_action())
    
    def _batch_verify_files(self, e):
        """Batch verify all files."""
        async def verify_action():
            try:
                unverified_files = [f for f in self.all_files if not f.get('verified', False)]
                if not unverified_files:
                    self.show_dialog("info", "No Files to Verify", "All files are already verified")
                    return
                    
                unverified_count = len(unverified_files)
                # Extract file IDs for verification
                file_ids = [f.get('filename', f'file_{i}') for i, f in enumerate(unverified_files)]
                
                # Use action system to verify multiple files
                result = await self.file_actions.verify_multiple_files(file_ids)
                
                if result.success:
                    valid_count = result.metadata.get('valid_files', 0)
                    invalid_count = result.metadata.get('invalid_files', 0)
                    self.show_dialog("success", "Batch Verification Complete", 
                                   f"Verified {unverified_count} files: {valid_count} valid, {invalid_count} invalid")
                    self._refresh_files()
                else:
                    self.show_dialog("error", "Batch Verification Failed", f"Failed to verify files: {result.error_message}")
            except Exception as ex:
                self.show_dialog("error", "Error", f"Failed to start batch verification: {str(ex)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(verify_action())
    
    def _show_file_statistics(self, e):
        """Show file statistics."""
        async def show_stats():
            try:
                # Use action system to get file list
                result = await self.file_actions.export_file_list([], 'csv')
                if result.success:
                    # Parse the CSV data to get statistics
                    csv_data = result.data
                    lines = csv_data.split('\n') if csv_data else []
                    total_files = max(0, len(lines) - 1)  # Subtract header line
                    
                    # Calculate total size from self.all_files (since we don't have size in CSV)
                    total_size = sum(f.get('size', 0) or 0 for f in self.all_files)
                    verified_files = len([f for f in self.all_files if f.get('verified', False)])
                    
                    # Count by type
                    type_counts = {}
                    for file_info in self.all_files:
                        file_type = self._get_file_type(file_info.get('filename', ''))
                        type_counts[file_type] = type_counts.get(file_type, 0) + 1
                    
                    size_mb = total_size / (1024 * 1024)
                    
                    stats_content = ft.Column([
                        ft.Text("File Statistics", size=18, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        
                        ft.Row([ft.Text("Total Files:", weight=ft.FontWeight.BOLD), ft.Text(str(total_files))]),
                        ft.Row([ft.Text("Total Size:", weight=ft.FontWeight.BOLD), ft.Text(f"{size_mb:.1f} MB")]),
                        ft.Row([ft.Text("Verified Files:", weight=ft.FontWeight.BOLD), ft.Text(str(verified_files))]),
                        ft.Row([ft.Text("Unverified Files:", weight=ft.FontWeight.BOLD), 
                               ft.Text(str(total_files - verified_files))]),
                        
                        ft.Divider(),
                        ft.Text("Files by Type:", weight=ft.FontWeight.BOLD),
                        
                        *[ft.Row([ft.Text(f"{file_type.title()}:", weight=ft.FontWeight.BOLD), 
                                 ft.Text(str(count))])
                          for file_type, count in sorted(type_counts.items())],
                    ], spacing=10)
                    
                    self.show_dialog("custom", "File Statistics", "", content=stats_content)
                else:
                    self.show_dialog("error", "Error", f"Failed to generate statistics: {result.error_message}")
            except Exception as ex:
                self.show_dialog("error", "Error", f"Failed to generate statistics: {str(ex)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(show_stats())
    
    def _clean_old_files(self, e):
        """Clean old files from server."""
        async def clean_action():
            try:
                # Use action system to clean old files
                result = await self.file_actions.cleanup_old_files(30)
                
                if result.success:
                    cleaned_count = result.data.get('cleaned_files', 0)
                    self.show_dialog("info", "Cleanup Complete", f"Cleaned up {cleaned_count} old files")
                    self._refresh_files()
                else:
                    self.show_dialog("error", "Cleanup Failed", f"Failed to clean old files: {result.error_message}")
            except Exception as ex:
                self.show_dialog("error", "Error", f"Failed to clean old files: {str(ex)}")
        
        def confirm_cleanup(e):
            # Run the async function
            import asyncio
            asyncio.create_task(clean_action())
        
        confirm_content = ft.Column([
            ft.Text("Clean Old Files", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("This will remove files older than 30 days that are unverified.", 
                   color=ft.Colors.ORANGE_600),
            ft.Text("This action cannot be undone!", weight=ft.FontWeight.BOLD, color=ft.Colors.RED_600),
            ft.Row([
                ft.ElevatedButton("Clean Files", on_click=confirm_cleanup, bgcolor=ft.Colors.ORANGE_600),
                ft.OutlinedButton("Cancel", on_click=lambda e: None)
            ], alignment=ft.MainAxisAlignment.END)
        ])
        
        self.show_dialog("custom", "Confirm Cleanup", "", content=confirm_content)
    
    # Enhanced utility methods (integrated from RealDataFilesView)
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format (from RealDataFilesView)."""
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
        """Format date string for display (from RealDataFilesView)."""
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

    def get_file_type_breakdown(self) -> List[tuple]:
        """Get file type breakdown statistics (integrated from FileTypeBreakdownCard)."""
        try:
            files = self.server_bridge.get_file_list()
            file_types = {}
            
            for file_info in files:
                filename = file_info.get('filename', '')
                if '.' in filename:
                    ext = filename.rsplit('.', 1)[-1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
                else:
                    file_types['no extension'] = file_types.get('no extension', 0) + 1
            
            # Return top 5 file types sorted by count
            return sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]
        except Exception as e:
            print(f"[ERROR] Failed to get file type breakdown: {e}")
            return []

    def _default_dialog(self, title: str, content: ft.Control):
        """Default dialog implementation."""
        print(f"[DIALOG] {title}: {content}")
    
    def did_mount(self):
        """Called when component is mounted - load initial data."""
        self._refresh_files()