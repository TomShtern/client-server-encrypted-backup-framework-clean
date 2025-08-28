#!/usr/bin/env python3
"""
Upload Progress Component
Material Design 3 component for visualizing file upload progress with enhanced UI.
"""

import flet as ft
from typing import List, Dict, Optional, Callable
import asyncio
from flet_server_gui.ui.theme_m3 import TOKENS
from flet_server_gui.components.enhanced_components import (
    EnhancedCard,
    CircularProgressIndicator,
    create_enhanced_button,
    create_enhanced_icon_button
)
from flet_server_gui.components.dialogs import create_toast_notification


class UploadProgress(EnhancedCard):
    """Upload progress component with visual feedback"""
    
    def __init__(self,
                 files: List[Dict] = None,
                 on_cancel: Optional[Callable] = None,
                 on_close: Optional[Callable] = None,
                 animate_duration: int = 200,
                 **kwargs):
        self.files = files or []
        self.on_cancel = on_cancel
        self.on_close = on_close
        self.is_uploading = False
        self.upload_tasks = []
        
        # Create the main content
        content = self._build_content()
        
        super().__init__(
            content=content,
            animate_duration=animate_duration,
            **kwargs
        )
    
    def _build_content(self) -> ft.Control:
        """Build the upload progress content"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.CLOUD_UPLOAD, size=24),
            ft.Text("Upload Progress", style=ft.TextThemeStyle.TITLE_LARGE),
            ft.Container(expand=True),
            create_enhanced_icon_button(
                icon=ft.Icons.CLOSE,
                tooltip="Close",
                on_click=self._on_close
            )
        ], spacing=12)
        
        # Files progress list
        files_progress = self._create_files_progress()
        
        # Overall progress
        overall_progress = self._create_overall_progress()
        
        # Control buttons
        control_buttons = self._create_control_buttons()
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                files_progress,
                ft.Divider(),
                overall_progress,
                ft.Divider(),
                control_buttons
            ], spacing=16),
            padding=ft.padding.all(20),
            width=500
        )
    
    def _create_files_progress(self) -> ft.Control:
        """Create individual file progress indicators"""
        if not self.files:
            return ft.Text("No files to upload", italic=True, color=TOKENS["outline"])
        
        file_items = []
        for file_info in self.files:
            # Create progress bar for each file
            progress_bar = ft.ProgressBar(
                value=file_info.get("progress", 0),
                bar_height=6,
                border_radius=3,
                animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
            )
            
            # Status icon
            status_icon = ft.Icon(
                ft.Icons.CHECK_CIRCLE if file_info.get("progress", 0) == 1.0 else
                ft.Icons.ERROR if file_info.get("error") else
                ft.Icons.HOURGLASS_EMPTY,
                color=TOKENS["tertiary"] if file_info.get("progress", 0) == 1.0 else
                TOKENS["error"] if file_info.get("error") else
                TOKENS["primary"],
                size=16
            )
            
            file_item = ft.ListTile(
                leading=status_icon,
                title=ft.Text(file_info.get("name", "Unknown")),
                subtitle=ft.Column([
                    ft.Row([
                        ft.Text(
                            f"{int(file_info.get('progress', 0) * 100)}%" if not file_info.get("error") else "Error",
                            style=ft.TextThemeStyle.BODY_SMALL,
                            color=TOKENS["outline"]
                        ),
                        ft.Text(
                            file_info.get("size", "Unknown"),
                            style=ft.TextThemeStyle.BODY_SMALL,
                            color=TOKENS["outline"]
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    progress_bar
                ], spacing=4),
                dense=True
            )
            
            file_items.append(file_item)
        
        return ft.Column(file_items, spacing=2)
    
    def _create_overall_progress(self) -> ft.Control:
        """Create overall progress indicator"""
        total_files = len(self.files)
        completed_files = sum(1 for f in self.files if f.get("progress", 0) == 1.0)
        error_files = sum(1 for f in self.files if f.get("error"))
        overall_progress = sum(f.get("progress", 0) for f in self.files) / total_files if total_files > 0 else 0
        
        return ft.Column([
            ft.Text("Overall Progress", style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.ProgressBar(
                value=overall_progress,
                bar_height=8,
                border_radius=4,
                animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
            ),
            ft.Row([
                ft.Text(
                    f"{completed_files}/{total_files} files completed",
                    style=ft.TextThemeStyle.BODY_MEDIUM
                ),
                ft.Container(expand=True),
                ft.Text(
                    f"{int(overall_progress * 100)}%",
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    weight=ft.FontWeight.BOLD
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], spacing=8)
    
    def _create_control_buttons(self) -> ft.Control:
        """Create control buttons"""
        return ft.Row([
            create_enhanced_button(
                text="Cancel All",
                icon=ft.Icons.CANCEL,
                on_click=self._on_cancel,
                disabled=not self.is_uploading
            ),
            create_enhanced_button(
                text="Close",
                icon=ft.Icons.CLOSE,
                on_click=self._on_close,
                disabled=self.is_uploading
            )
        ], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
    
    def _on_cancel(self, e):
        """Handle cancel action"""
        if self.on_cancel:
            self.on_cancel(e)
        else:
            # Cancel all upload tasks
            for task in self.upload_tasks:
                task.cancel()
            
            self.is_uploading = False
            self._update_content()
            
            toast = create_toast_notification(
                message="Upload cancelled",
                bgcolor=TOKENS["surface_variant"]
            )
            toast.show(self.page)
    
    def _on_close(self, e):
        """Handle close action"""
        if self.on_close:
            self.on_close(e)
    
    def _update_content(self):
        """Update the component content"""
        new_content = self._build_content()
        self.content = new_content
        self.page.update()
    
    async def start_upload(self):
        """Start the upload process"""
        self.is_uploading = True
        self._update_content()
        
        # Simulate upload process
        for file_info in self.files:
            if not file_info.get("error"):
                # Create a task for each file upload
                task = asyncio.create_task(self._upload_file(file_info))
                self.upload_tasks.append(task)
        
        # Wait for all uploads to complete
        if self.upload_tasks:
            await asyncio.gather(*self.upload_tasks, return_exceptions=True)
        
        self.is_uploading = False
        self._update_content()
        
        # Show completion message
        completed_files = sum(1 for f in self.files if f.get("progress", 0) == 1.0)
        total_files = len(self.files)
        
        if completed_files == total_files:
            toast = create_toast_notification(
                message=f"All {total_files} files uploaded successfully",
                bgcolor=TOKENS["container"]
            )
        else:
            toast = create_toast_notification(
                message=f"Uploaded {completed_files}/{total_files} files",
                bgcolor=TOKENS["surface_variant"]
            )
        
        toast.show(self.page)
    
    async def _upload_file(self, file_info: Dict):
        """Simulate uploading a single file"""
        try:
            # Simulate upload progress
            for i in range(101):
                await asyncio.sleep(0.05)  # Simulate time taken to upload
                file_info["progress"] = i / 100.0
                self._update_content()
            
            # Mark as completed
            file_info["progress"] = 1.0
        except asyncio.CancelledError:
            # Handle cancellation
            file_info["progress"] = 0.0
            file_info["error"] = "Cancelled"
        except Exception as e:
            # Handle errors
            file_info["error"] = str(e)
        
        self._update_content()


# Factory function
def create_upload_progress(files: List[Dict] = None, **kwargs) -> UploadProgress:
    """Create upload progress component"""
    return UploadProgress(files=files, **kwargs)