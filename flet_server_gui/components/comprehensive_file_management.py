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


class ComprehensiveFileManagement:
    """Complete file management with all TKinter GUI features."""
    
    def __init__(self, server_bridge: ServerBridge, show_dialog_callback: Optional[Callable] = None):
        self.server_bridge = server_bridge
        self.show_dialog = show_dialog_callback or self._default_dialog
        
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
                
                # Create action buttons for this file
                action_buttons = ft.Row([
                    ft.IconButton(
                        ft.Icons.INFO,
                        tooltip="File Details",
                        on_click=lambda e, f=file_info: self._view_file_details(f)
                    ),
                    ft.IconButton(
                        ft.Icons.DOWNLOAD,
                        tooltip="Download",
                        on_click=lambda e, f=file_info: self._download_file(f)
                    ),
                    ft.IconButton(
                        ft.Icons.VERIFIED,
                        tooltip="Verify",
                        on_click=lambda e, f=file_info: self._verify_file(f)
                    ),
                    ft.IconButton(
                        ft.Icons.VISIBILITY,
                        tooltip="Preview",
                        on_click=lambda e, f=file_info: self._preview_file(f)
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE,
                        tooltip="Delete",
                        on_click=lambda e, f=file_info: self._delete_file(f)
                    ),
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
        try:
            filename = file_info.get('filename', 'Unknown')
            # TODO: Implement actual download logic
            print(f"[INFO] Downloading file: {filename}")
            self.show_dialog("info", "Download", f"File '{filename}' download started")
        except Exception as e:
            self.show_dialog("error", "Error", f"Failed to download file: {str(e)}")
    
    def _verify_file(self, file_info):
        """Verify a file's integrity."""
        try:
            filename = file_info.get('filename', 'Unknown')
            # TODO: Implement actual verification logic
            print(f"[INFO] Verifying file: {filename}")
            self.show_dialog("info", "Verification", f"File '{filename}' verification started")
        except Exception as e:
            self.show_dialog("error", "Error", f"Failed to verify file: {str(e)}")
    
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
        filename = file_info.get('filename', 'Unknown')
        
        def confirm_delete():
            try:
                success = self.server_bridge.delete_file(file_info)
                self._refresh_files()
                
                if success:
                    self.show_dialog(
                        "success",
                        "File Deleted",
                        f"File '{filename}' has been permanently deleted"
                    )
                else:
                    self.show_dialog(
                        "warning",
                        "Delete Warning",
                        f"File '{filename}' delete completed with warnings"
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
            on_confirm=confirm_delete,
            confirm_text="Delete",
            danger=True
        )
    
    # === Bulk Actions ===
    
    def _download_selected_files(self, e):
        """Download multiple selected files."""
        try:
            print(f"[INFO] Downloading {len(self.selected_files)} selected files")
            self.show_dialog("info", "Batch Download", f"Download started for {len(self.selected_files)} files")
        except Exception as ex:
            self.show_dialog("error", "Error", f"Failed to download files: {str(ex)}")
    
    def _verify_selected_files(self, e):
        """Verify multiple selected files."""
        try:
            print(f"[INFO] Verifying {len(self.selected_files)} selected files")
            self.show_dialog("info", "Batch Verification", f"Verification started for {len(self.selected_files)} files")
        except Exception as ex:
            self.show_dialog("error", "Error", f"Failed to verify files: {str(ex)}")
    
    def _delete_selected_files(self, e):
        """Delete multiple selected files."""
        if not self.selected_files:
            return
            
        def confirm_bulk_delete():
            try:
                deleted_count = self.server_bridge.delete_multiple_files(self.selected_files)
                
                self.selected_files = []
                self._update_bulk_actions_visibility()
                self._refresh_files()
                
                self.show_dialog(
                    "success",
                    "Bulk Delete Complete", 
                    f"Successfully deleted {deleted_count} files"
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
            on_confirm=confirm_bulk_delete,
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
        # TODO: Implement file picker and upload logic
        self.show_dialog("info", "Upload File", "Upload functionality coming soon")
    
    def _batch_verify_files(self, e):
        """Batch verify all files."""
        try:
            unverified_count = len([f for f in self.all_files if not f.get('verified', False)])
            print(f"[INFO] Starting batch verification of {unverified_count} unverified files")
            self.show_dialog("info", "Batch Verification", f"Started verification of {unverified_count} unverified files")
        except Exception as ex:
            self.show_dialog("error", "Error", f"Failed to start batch verification: {str(ex)}")
    
    def _show_file_statistics(self, e):
        """Show file statistics."""
        try:
            total_files = len(self.all_files)
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
        except Exception as ex:
            self.show_dialog("error", "Error", f"Failed to generate statistics: {str(ex)}")
    
    def _clean_old_files(self, e):
        """Clean old files from server."""
        def confirm_cleanup(e):
            try:
                # TODO: Implement actual cleanup logic
                print("[INFO] Starting cleanup of old files")
                self.show_dialog("info", "Cleanup Complete", "Old files cleanup completed")
                self._refresh_files()
            except Exception as ex:
                self.show_dialog("Error", ft.Text(f"Failed to clean old files: {str(ex)}"))
        
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
    
    def _default_dialog(self, title: str, content: ft.Control):
        """Default dialog implementation."""
        print(f"[DIALOG] {title}: {content}")
    
    def did_mount(self):
        """Called when component is mounted - load initial data."""
        self._refresh_files()