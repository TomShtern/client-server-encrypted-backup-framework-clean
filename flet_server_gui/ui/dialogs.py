#!/usr/bin/env python3
"""
Purpose: Centralized dialog and confirmation system
Logic: Dialog state management, user interaction flow
UI: Modal dialogs, confirmations, alerts
"""

import flet as ft
from typing import Optional, Callable, Any, Dict, List
import asyncio
from enum import Enum
from flet_server_gui.core.theme_compatibility import TOKENS

# ============================================================================
# DIALOG TYPES AND CONFIGURATIONS
# ============================================================================

class DialogType(Enum):
    """Types of dialogs available in the system."""
    INFO = "info"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    CONFIRMATION = "confirmation"
    INPUT = "input"
    CUSTOM = "custom"
    PROGRESS = "progress"

class DialogSize(Enum):
    """Standard dialog sizes."""
    SMALL = {"width": 300, "height": 200}
    MEDIUM = {"width": 500, "height": 350}
    LARGE = {"width": 700, "height": 500}
    EXTRA_LARGE = {"width": 900, "height": 700}

# ============================================================================
# MAIN DIALOG SYSTEM
# ============================================================================

class DialogSystem:
    """Central dialog management system with Material Design 3 styling and enhanced animations."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_dialog = None
        self.dialog_stack: List[ft.AlertDialog] = []
        
        # Enhanced animation properties
        self.default_scale_animation = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.default_opacity_animation = ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        self.default_offset_animation = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        
        # Dialog configuration
        self.default_size = DialogSize.MEDIUM
        self.auto_close_timeout = None
    
    def _apply_enhanced_animations(self, dialog: ft.AlertDialog):
        """Apply enhanced entrance animations to dialogs"""
        try:
            dialog.animate_scale = self.default_scale_animation
            dialog.animate_opacity = self.default_opacity_animation
            dialog.animate_offset = self.default_offset_animation
            
            # Initial animation states for smooth entrance
            dialog.scale = ft.Scale(0.9)
            dialog.opacity = 0.5
            dialog.offset = ft.Offset(0, -0.1)
        except Exception as e:
            # If animations fail, continue without them
            print(f"[WARNING] Dialog animation setup failed: {e}")
    
    def _create_dialog_base(self, 
                           title: str, 
                           content: ft.Control, 
                           actions: List[ft.Control],
                           dialog_type: DialogType = DialogType.INFO,
                           size: DialogSize = None) -> ft.AlertDialog:
        """Create a base dialog with consistent styling."""
        if size is None:
            size = self.default_size
        
        # Create title with appropriate icon
        title_icon = self._get_dialog_icon(dialog_type)
        title_row = ft.Row([
            ft.Icon(title_icon["icon"], color=title_icon["color"], size=24),
            ft.Text(title, size=18, weight=ft.FontWeight.BOLD, expand=True)
        ], spacing=10, alignment=ft.MainAxisAlignment.START)
        
        dialog = ft.AlertDialog(
            title=title_row,
            content=ft.Container(
                content=content,
                width=size.value["width"],
                height=size.value["height"] if hasattr(content, 'height') else None
            ),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True
        )
        
        self._apply_enhanced_animations(dialog)
        return dialog
    
    def _get_dialog_icon(self, dialog_type: DialogType) -> Dict[str, Any]:
        """Get appropriate icon and color for dialog type."""
        icons = {
            DialogType.INFO: {"icon": ft.Icons.INFO, "color": TOKENS['primary']},
            DialogType.SUCCESS: {"icon": ft.Icons.CHECK_CIRCLE, "color": TOKENS['secondary']},
            DialogType.ERROR: {"icon": ft.Icons.ERROR, "color": TOKENS['error']},
            DialogType.WARNING: {"icon": ft.Icons.WARNING, "color": TOKENS['secondary']},
            DialogType.CONFIRMATION: {"icon": ft.Icons.HELP, "color": TOKENS['secondary']},
            DialogType.INPUT: {"icon": ft.Icons.EDIT, "color": TOKENS['primary']},
            DialogType.CUSTOM: {"icon": ft.Icons.SETTINGS, "color": TOKENS['outline']},
            DialogType.PROGRESS: {"icon": ft.Icons.HOURGLASS_EMPTY, "color": TOKENS['primary']}
        }
        return icons.get(dialog_type, icons[DialogType.INFO])
    
    def _show_dialog(self, dialog: ft.AlertDialog):
        """Internal method to display a dialog."""
        # Store current dialog in stack if exists
        if self.current_dialog:
            self.dialog_stack.append(self.current_dialog)
        
        self.current_dialog = dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _close_current_dialog(self):
        """Internal method to close the current dialog."""
        if self.current_dialog:
            self.current_dialog.open = False
            self.page.update()
            
            # Restore previous dialog if exists
            if self.dialog_stack:
                self.current_dialog = self.dialog_stack.pop()
                self.page.dialog = self.current_dialog
                self.current_dialog.open = True
                self.page.update()
            else:
                self.current_dialog = None
    
    # ========================================================================
    # PUBLIC DIALOG METHODS
    # ========================================================================
    
    def show_info_dialog(self, 
                        title: str, 
                        message: str, 
                        on_close: Optional[Callable] = None,
                        size: DialogSize = None):
        """Show an information dialog."""
        
        def close_action(e):
            self._close_current_dialog()
            if on_close:
                on_close()
        
        content = ft.Text(message, size=14)
        actions = [ft.TextButton("OK", on_click=close_action)]
        
        dialog = self._create_dialog_base(title, content, actions, DialogType.INFO, size)
        self._show_dialog(dialog)
    
    def show_success_dialog(self, 
                           title: str, 
                           message: str, 
                           on_close: Optional[Callable] = None,
                           size: DialogSize = None):
        """Show a success dialog with green styling."""
        
        def close_action(e):
            self._close_current_dialog()
            if on_close:
                on_close()
        
        content = ft.Text(message, size=14)
        actions = [ft.FilledButton("OK", on_click=close_action, 
                                  style=ft.ButtonStyle(bgcolor=TOKENS['secondary']))]
        
        dialog = self._create_dialog_base(title, content, actions, DialogType.SUCCESS, size)
        self._show_dialog(dialog)
    
    def show_error_dialog(self, 
                         title: str, 
                         message: str, 
                         on_close: Optional[Callable] = None,
                         size: DialogSize = None,
                         details: Optional[str] = None):
        """Show an error dialog with red styling and optional details."""
        
        def close_action(e):
            self._close_current_dialog()
            if on_close:
                on_close()
        
        content_controls = [ft.Text(message, size=14)]
        
        # Add details section if provided
        if details:
            content_controls.extend([
                ft.Divider(),
                ft.Text("Details:", weight=ft.FontWeight.BOLD, size=12),
                ft.Container(
                    content=ft.Text(details, size=11, color=TOKENS['outline'], selectable=True),
                    bgcolor=TOKENS['surface_variant'],
                    padding=10,
                    border_radius=5,
                    width=float("inf")
                )
            ])
        
        content = ft.Column(content_controls, spacing=10, tight=True)
        actions = [ft.FilledButton("OK", on_click=close_action,
                                  style=ft.ButtonStyle(bgcolor=TOKENS['error']))]
        
        dialog = self._create_dialog_base(title, content, actions, DialogType.ERROR, size)
        self._show_dialog(dialog)
    
    def show_warning_dialog(self, 
                           title: str, 
                           message: str, 
                           on_close: Optional[Callable] = None,
                           size: DialogSize = None):
        """Show a warning dialog with orange styling."""
        
        def close_action(e):
            self._close_current_dialog()
            if on_close:
                on_close()
        
        content = ft.Text(message, size=14)
        actions = [ft.FilledButton("OK", on_click=close_action,
                                  style=ft.ButtonStyle(bgcolor=TOKENS['secondary']))]
        
        dialog = self._create_dialog_base(title, content, actions, DialogType.WARNING, size)
        self._show_dialog(dialog)
    
    def show_confirmation_dialog(self, 
                               title: str, 
                               message: str, 
                               on_confirm: Callable,
                               on_cancel: Optional[Callable] = None,
                               confirm_text: str = "Confirm",
                               cancel_text: str = "Cancel",
                               danger: bool = False,
                               size: DialogSize = None):
        """Show a confirmation dialog."""
        
        def confirm_action(e):
            self._close_current_dialog()
            on_confirm()
        
        def cancel_action(e):
            self._close_current_dialog()
            if on_cancel:
                on_cancel()
        
        content = ft.Text(message, size=14)
        
        confirm_button_color = TOKENS['error'] if danger else TOKENS['primary']
        actions = [
            ft.TextButton(cancel_text, on_click=cancel_action),
            ft.FilledButton(
                confirm_text, 
                on_click=confirm_action,
                style=ft.ButtonStyle(bgcolor=confirm_button_color)
            )
        ]
        
        dialog = self._create_dialog_base(title, content, actions, DialogType.CONFIRMATION, size)
        self._show_dialog(dialog)
    
    def show_input_dialog(self, 
                         title: str, 
                         message: str,
                         on_submit: Callable[[str], None],
                         on_cancel: Optional[Callable] = None,
                         placeholder: str = "",
                         initial_value: str = "",
                         multiline: bool = False,
                         validation_callback: Optional[Callable[[str], Optional[str]]] = None,
                         size: DialogSize = None):
        """Show an input dialog with validation support."""
        
        input_field = ft.TextField(
            label=placeholder,
            value=initial_value,
            multiline=multiline,
            max_lines=5 if multiline else 1,
            width=400,
            autofocus=True
        )
        
        error_text = ft.Text("", color=TOKENS['error'], size=12)
        
        def validate_and_submit():
            value = input_field.value or ""
            
            # Run validation if provided
            if validation_callback:
                error_message = validation_callback(value)
                if error_message:
                    error_text.value = error_message
                    self.page.update()
                    return False
            
            error_text.value = ""
            self.page.update()
            return True
        
        def submit_action(e):
            if validate_and_submit():
                value = input_field.value or ""
                self._close_current_dialog()
                on_submit(value)
        
        def cancel_action(e):
            self._close_current_dialog()
            if on_cancel:
                on_cancel()
        
        def on_input_change(e):
            # Clear error on input change
            if error_text.value:
                error_text.value = ""
                self.page.update()
        
        input_field.on_change = on_input_change
        input_field.on_submit = submit_action
        
        content = ft.Column([
            ft.Text(message, size=14) if message else None,
            input_field,
            error_text
        ], spacing=10, tight=True)
        
        actions = [
            ft.TextButton("Cancel", on_click=cancel_action),
            ft.FilledButton("Submit", on_click=submit_action)
        ]
        
        dialog = self._create_dialog_base(title, content, actions, DialogType.INPUT, size)
        self._show_dialog(dialog)
        
        # Focus the input field after dialog is shown
        self.page.update()
    
    def show_progress_dialog(self, 
                           title: str, 
                           message: str,
                           progress_value: Optional[float] = None,
                           cancelable: bool = True,
                           on_cancel: Optional[Callable] = None,
                           size: DialogSize = None):
        """Show a progress dialog and return the progress bar for updates."""
        
        progress_bar = ft.ProgressBar(
            value=progress_value,
            width=400,
            height=10
        )
        
        message_text = ft.Text(message, size=14)
        
        def cancel_action(e):
            self._close_current_dialog()
            if on_cancel:
                on_cancel()
        
        content = ft.Column([
            message_text,
            progress_bar
        ], spacing=15, tight=True)
        
        actions = []
        if cancelable:
            actions.append(ft.TextButton("Cancel", on_click=cancel_action))
        
        dialog = self._create_dialog_base(title, content, actions, DialogType.PROGRESS, size)
        self._show_dialog(dialog)
        
        # Return references for updates
        return {
            "progress_bar": progress_bar,
            "message_text": message_text,
            "dialog": dialog
        }
    
    def show_custom_dialog(self, 
                          title: str, 
                          content: ft.Control,
                          actions: Optional[List[ft.Control]] = None,
                          modal: bool = True,
                          scrollable: bool = False,
                          size: DialogSize = None):
        """Show a custom dialog with any content."""
        
        def close_action(e):
            self._close_current_dialog()
        
        dialog_content = content
        if scrollable:
            dialog_content = ft.Container(
                content=ft.Column([content], scroll=ft.ScrollMode.AUTO),
                height=400,
                width=600
            )
        
        default_actions = [ft.TextButton("Close", on_click=close_action)]
        dialog_actions = actions if actions is not None else default_actions
        
        dialog = self._create_dialog_base(title, dialog_content, dialog_actions, DialogType.CUSTOM, size)
        dialog.modal = modal
        self._show_dialog(dialog)
    
    def update_progress_dialog(self, progress_refs: Dict[str, Any], value: float, message: str = ""):
        """Update progress dialog with new values."""
        if "progress_bar" in progress_refs:
            progress_refs["progress_bar"].value = value
        
        if message and "message_text" in progress_refs:
            progress_refs["message_text"].value = message
        
        self.page.update()
    
    def close_current_dialog(self):
        """Close the currently open dialog."""
        self._close_current_dialog()
    
    def close_all_dialogs(self):
        """Close all open dialogs."""
        while self.current_dialog or self.dialog_stack:
            self._close_current_dialog()
    
    # ========================================================================
    # SPECIALIZED DIALOG METHODS
    # ========================================================================
    
    def show_file_details_dialog(self, file_info: Dict[str, Any]):
        """Show detailed file information dialog."""
        size_mb = (file_info.get('size', 0) or 0) / (1024 * 1024)
        
        details_content = ft.Column([
            self._create_detail_row("Filename:", file_info.get('filename', 'Unknown'), selectable=True),
            self._create_detail_row("Client:", file_info.get('client', 'Unknown')),
            self._create_detail_row("Size:", f"{size_mb:.2f} MB"),
            self._create_detail_row("Upload Date:", file_info.get('date', 'Unknown')),
            self._create_detail_row("Verified:", "Yes" if file_info.get('verified', False) else "No"),
            self._create_detail_row("Full Path:", file_info.get('path', 'Unknown'), selectable=True),
        ], spacing=10)
        
        self.show_custom_dialog(
            f"File Details: {file_info.get('filename', 'Unknown')}", 
            details_content,
            size=DialogSize.LARGE
        )
    
    def show_client_details_dialog(self, client_info: Dict[str, Any]):
        """Show detailed client information dialog."""
        details_content = ft.Column([
            self._create_detail_row("Username:", client_info.get('client_id', 'Unknown')),
            self._create_detail_row("Status:", client_info.get('status', 'Unknown')),
            self._create_detail_row("Address:", client_info.get('address', 'N/A')),
            self._create_detail_row("Last Activity:", str(client_info.get('last_activity', 'Unknown'))),
            self._create_detail_row("Files Count:", str(client_info.get('files_count', 0))),
            self._create_detail_row("Total Size:", f"{client_info.get('total_size', 0) / (1024*1024):.1f} MB"),
        ], spacing=10)
        
        self.show_custom_dialog(
            f"Client Details: {client_info.get('client_id', 'Unknown')}", 
            details_content,
            size=DialogSize.LARGE
        )
    
    def _create_detail_row(self, label: str, value: str, selectable: bool = False) -> ft.Row:
        """Create a detail row for information dialogs."""
        return ft.Row([
            ft.Text(label, weight=ft.FontWeight.BOLD, width=120), 
            ft.Text(value, selectable=selectable, expand=True)
        ], spacing=10)
    
    # ========================================================================
    # ASYNC DIALOG METHODS
    # ========================================================================
    
    async def show_confirmation_async(self, title: str, message: str) -> bool:
        """Show a confirmation dialog and return the user's choice asynchronously."""
        future = asyncio.Future()
        
        def on_confirm():
            if not future.done():
                future.set_result(True)
        
        def on_cancel():
            if not future.done():
                future.set_result(False)
        
        self.show_confirmation_dialog(
            title=title,
            message=message,
            on_confirm=on_confirm,
            on_cancel=on_cancel
        )
        
        return await future

# ============================================================================
# TOAST NOTIFICATION SYSTEM
# ============================================================================

class ToastManager:
    """Toast notification system for quick feedback."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        
    def show_success(self, message: str, duration: int = 3):
        """Show success toast."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=TOKENS['on_secondary']),
                ft.Text(message, color=TOKENS['on_secondary'])
            ]),
            bgcolor=TOKENS['secondary'],
            duration=duration * 1000
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_error(self, message: str, duration: int = 5):
        """Show error toast."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR, color=TOKENS['on_error']),
                ft.Text(message, color=TOKENS['on_error'])
            ]),
            bgcolor=TOKENS['error'],
            duration=duration * 1000
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_warning(self, message: str, duration: int = 4):
        """Show warning toast."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING, color=TOKENS['on_secondary']),
                ft.Text(message, color=TOKENS['on_secondary'])
            ]),
            bgcolor=TOKENS['secondary'],
            duration=duration * 1000
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_info(self, message: str, duration: int = 3):
        """Show info toast."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO, color=TOKENS['on_primary']),
                ft.Text(message, color=TOKENS['on_primary'])
            ]),
            bgcolor=TOKENS['primary'],
            duration=duration * 1000
        )
        self.page.snack_bar.open = True
        self.page.update()

# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_dialog_system(page: ft.Page) -> DialogSystem:
    """Create and initialize a dialog system for the page."""
    return DialogSystem(page)

def create_toast_manager(page: ft.Page) -> ToastManager:
    """Create and initialize a toast manager for the page."""
    return ToastManager(page)

# Legacy compatibility functions (integrated from original dialog_system.py)
def create_enhanced_dialog_system(page: ft.Page) -> DialogSystem:
    """Create an enhanced dialog system with animations - legacy compatibility."""
    return DialogSystem(page)

def show_enhanced_confirmation(page: ft.Page, title: str, message: str, 
                             on_confirm: Optional[Callable] = None,
                             on_cancel: Optional[Callable] = None):
    """Show enhanced confirmation dialog with animations - legacy compatibility."""
    dialog_system = DialogSystem(page)
    return dialog_system.show_confirmation_dialog(title, message, on_confirm, on_cancel)

def show_enhanced_info(page: ft.Page, title: str, message: str, 
                      on_close: Optional[Callable] = None):
    """Show enhanced info dialog with animations - legacy compatibility."""
    dialog_system = DialogSystem(page)
    return dialog_system.show_info_dialog(title, message, on_close)

def show_enhanced_success(page: ft.Page, title: str, message: str, 
                         on_close: Optional[Callable] = None):
    """Show enhanced success dialog with animations - legacy compatibility."""
    dialog_system = DialogSystem(page)
    return dialog_system.show_success_dialog(title, message, on_close)

def show_enhanced_error(page: ft.Page, title: str, message: str, 
                       on_close: Optional[Callable] = None):
    """Show enhanced error dialog with animations - legacy compatibility."""
    dialog_system = DialogSystem(page)
    return dialog_system.show_error_dialog(title, message, on_close)