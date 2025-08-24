#!/usr/bin/env python3
"""
Comprehensive Dialog System for Flet GUI
Provides all dialog types: confirmation, info, error, success, input, progress, etc.
"""

import flet as ft
from typing import Optional, Callable, Any, Dict
import asyncio


class DialogSystem:
    """Central dialog management system with Material Design 3 styling."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_dialog = None
        
    def show_info_dialog(self, title: str, message: str, on_close: Optional[Callable] = None):
        """Show an information dialog."""
        
        def close_dialog(e):
            self.current_dialog.open = False
            self.page.update()
            if on_close:
                on_close()
        
        self.current_dialog = ft.AlertDialog(
            title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
            content=ft.Text(message, size=14),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.current_dialog
        self.current_dialog.open = True
        self.page.update()
    
    def show_success_dialog(self, title: str, message: str, on_close: Optional[Callable] = None):
        """Show a success dialog with green styling."""
        
        def close_dialog(e):
            self.current_dialog.open = False
            self.page.update()
            if on_close:
                on_close()
        
        self.current_dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=24),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600)
            ], tight=True),
            content=ft.Text(message, size=14),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.current_dialog
        self.current_dialog.open = True
        self.page.update()
    
    def show_error_dialog(self, title: str, message: str, on_close: Optional[Callable] = None):
        """Show an error dialog with red styling."""
        
        def close_dialog(e):
            self.current_dialog.open = False
            self.page.update()
            if on_close:
                on_close()
        
        self.current_dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_600, size=24),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_600)
            ], tight=True),
            content=ft.Text(message, size=14),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.current_dialog
        self.current_dialog.open = True
        self.page.update()
    
    def show_warning_dialog(self, title: str, message: str, on_close: Optional[Callable] = None):
        """Show a warning dialog with orange styling."""
        
        def close_dialog(e):
            self.current_dialog.open = False
            self.page.update()
            if on_close:
                on_close()
        
        self.current_dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE_600, size=24),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_600)
            ], tight=True),
            content=ft.Text(message, size=14),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.current_dialog
        self.current_dialog.open = True
        self.page.update()
    
    def show_confirmation_dialog(self, 
                                title: str, 
                                message: str, 
                                on_confirm: Callable,
                                on_cancel: Optional[Callable] = None,
                                confirm_text: str = "Confirm",
                                cancel_text: str = "Cancel",
                                danger: bool = False):
        """Show a confirmation dialog."""
        
        def confirm_action(e):
            self.current_dialog.open = False
            self.page.update()
            on_confirm()
        
        def cancel_action(e):
            self.current_dialog.open = False
            self.page.update()
            if on_cancel:
                on_cancel()
        
        confirm_button_color = ft.Colors.RED_600 if danger else ft.Colors.BLUE_600
        
        self.current_dialog = ft.AlertDialog(
            title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
            content=ft.Text(message, size=14),
            actions=[
                ft.TextButton(cancel_text, on_click=cancel_action),
                ft.ElevatedButton(
                    confirm_text, 
                    on_click=confirm_action,
                    bgcolor=confirm_button_color,
                    color=ft.Colors.WHITE
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.current_dialog
        self.current_dialog.open = True
        self.page.update()
    
    def show_input_dialog(self, 
                         title: str, 
                         message: str,
                         on_submit: Callable[[str], None],
                         on_cancel: Optional[Callable] = None,
                         placeholder: str = "",
                         initial_value: str = "",
                         multiline: bool = False):
        """Show an input dialog."""
        
        input_field = ft.TextField(
            label=placeholder,
            value=initial_value,
            multiline=multiline,
            max_lines=5 if multiline else 1,
            width=400
        )
        
        def submit_action(e):
            value = input_field.value or ""
            self.current_dialog.open = False
            self.page.update()
            on_submit(value)
        
        def cancel_action(e):
            self.current_dialog.open = False
            self.page.update()
            if on_cancel:
                on_cancel()
        
        self.current_dialog = ft.AlertDialog(
            title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(message, size=14) if message else None,
                input_field
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_action),
                ft.ElevatedButton("Submit", on_click=submit_action, bgcolor=ft.Colors.BLUE_600)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.current_dialog
        self.current_dialog.open = True
        self.page.update()
        
        # Focus the input field
        input_field.focus()
    
    def show_custom_dialog(self, 
                          title: str, 
                          content: ft.Control,
                          actions: Optional[list] = None,
                          modal: bool = True,
                          scrollable: bool = False):
        """Show a custom dialog with any content."""
        
        def close_dialog(e):
            self.current_dialog.open = False
            self.page.update()
        
        dialog_content = content
        if scrollable:
            dialog_content = ft.Container(
                content=ft.Column([content], scroll=ft.ScrollMode.AUTO),
                height=400,
                width=600
            )
        
        default_actions = [ft.TextButton("Close", on_click=close_dialog)]
        dialog_actions = actions if actions is not None else default_actions
        
        self.current_dialog = ft.AlertDialog(
            title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
            content=dialog_content,
            actions=dialog_actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.current_dialog
        self.current_dialog.open = True
        self.page.update()
    
    def show_progress_dialog(self, 
                           title: str, 
                           message: str,
                           progress_value: Optional[float] = None,
                           cancelable: bool = True,
                           on_cancel: Optional[Callable] = None):
        """Show a progress dialog."""
        
        progress_bar = ft.ProgressBar(
            value=progress_value,
            width=400,
            height=10
        )
        
        def cancel_action(e):
            self.current_dialog.open = False
            self.page.update()
            if on_cancel:
                on_cancel()
        
        actions = []
        if cancelable:
            actions.append(ft.TextButton("Cancel", on_click=cancel_action))
        
        self.current_dialog = ft.AlertDialog(
            title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(message, size=14),
                progress_bar
            ], tight=True, spacing=10),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.current_dialog
        self.current_dialog.open = True
        self.page.update()
        
        return progress_bar  # Return progress bar for updates
    
    def update_progress_dialog(self, progress_bar: ft.ProgressBar, value: float, message: str = ""):
        """Update progress dialog."""
        progress_bar.value = value
        if message and self.current_dialog and self.current_dialog.content:
            # Update message if provided
            content_column = self.current_dialog.content
            if isinstance(content_column, ft.Column) and len(content_column.controls) > 0:
                content_column.controls[0] = ft.Text(message, size=14)
        self.page.update()
    
    def close_current_dialog(self):
        """Close the currently open dialog."""
        if self.current_dialog:
            self.current_dialog.open = False
            self.page.update()
            self.current_dialog = None
    
    def show_file_details_dialog(self, file_info: Dict[str, Any]):
        """Show detailed file information dialog."""
        size_mb = (file_info.get('size', 0) or 0) / (1024 * 1024)
        
        details_content = ft.Column([
            ft.Row([ft.Text("Filename:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text(file_info.get('filename', 'Unknown'), selectable=True, expand=True)]),
            ft.Row([ft.Text("Client:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text(file_info.get('client', 'Unknown'))]),
            ft.Row([ft.Text("Size:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text(f"{size_mb:.2f} MB")]),
            ft.Row([ft.Text("Upload Date:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text(file_info.get('date', 'Unknown'))]),
            ft.Row([ft.Text("Verified:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text("Yes" if file_info.get('verified', False) else "No")]),
            ft.Row([ft.Text("Full Path:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text(file_info.get('path', 'Unknown'), selectable=True, expand=True)]),
        ], spacing=10)
        
        self.show_custom_dialog(
            f"File Details: {file_info.get('filename', 'Unknown')}", 
            details_content
        )
    
    def show_client_details_dialog(self, client_info: Dict[str, Any]):
        """Show detailed client information dialog."""
        details_content = ft.Column([
            ft.Row([ft.Text("Username:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text(client_info.get('client_id', 'Unknown'))]),
            ft.Row([ft.Text("Status:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text(client_info.get('status', 'Unknown'))]),
            ft.Row([ft.Text("Address:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text(client_info.get('address', 'N/A'))]),
            ft.Row([ft.Text("Last Activity:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text(str(client_info.get('last_activity', 'Unknown')))]),
            ft.Row([ft.Text("Files Count:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text(str(client_info.get('files_count', 0)))]),
            ft.Row([ft.Text("Total Size:", weight=ft.FontWeight.BOLD, width=120), 
                   ft.Text(f"{client_info.get('total_size', 0) / (1024*1024):.1f} MB")]),
        ], spacing=10)
        
        self.show_custom_dialog(
            f"Client Details: {client_info.get('client_id', 'Unknown')}", 
            details_content
        )


class ToastManager:
    """Toast notification system for quick feedback."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        
    def show_success(self, message: str, duration: int = 3):
        """Show success toast."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                ft.Text(message, color=ft.Colors.WHITE)
            ], tight=True),
            bgcolor=ft.Colors.GREEN_600,
            duration=duration * 1000
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_error(self, message: str, duration: int = 5):
        """Show error toast."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE),
                ft.Text(message, color=ft.Colors.WHITE)
            ], tight=True),
            bgcolor=ft.Colors.RED_600,
            duration=duration * 1000
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_warning(self, message: str, duration: int = 4):
        """Show warning toast."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING, color=ft.Colors.WHITE),
                ft.Text(message, color=ft.Colors.WHITE)
            ], tight=True),
            bgcolor=ft.Colors.ORANGE_600,
            duration=duration * 1000
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_info(self, message: str, duration: int = 3):
        """Show info toast."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO, color=ft.Colors.WHITE),
                ft.Text(message, color=ft.Colors.WHITE)
            ], tight=True),
            bgcolor=ft.Colors.BLUE_600,
            duration=duration * 1000
        )
        self.page.snack_bar.open = True
        self.page.update()