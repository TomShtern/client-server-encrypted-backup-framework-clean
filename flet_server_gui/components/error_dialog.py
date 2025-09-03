"""
Professional Error Dialog Component for Flet Applications
Following Material Design 3 Guidelines for Error Handling

Key Features:
- Professional error presentation with clear messaging
- Detailed error information with expandable view
- User-friendly error reporting mechanism
- Material Design 3 compliant styling
- Responsive layout for all screen sizes
"""

import flet as ft
import asyncio
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from .error_context import ErrorContext, ErrorFormatter
# Updated import to use new theme structure
try:
    from ..theme import TOKENS
except ImportError:
    # Fallback for direct execution or missing modules
    TOKENS = {
        'primary': '#38A298',
        'on_primary': '#FFFFFF',
        'secondary': '#7C5CD9',
        'on_secondary': '#FFFFFF',
        'error': '#EF5350',
        'on_error': '#FFFFFF',
        'surface': '#F0F4F8',
        'on_surface': '#1C2A35',
        'background': '#F8F9FA',
        'on_background': '#1C2A35',
    }


class ErrorDialog:
    """Professional error dialog with Material Design 3 styling."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.dialog: Optional[ft.AlertDialog] = None
        self.on_report_callback: Optional[Callable[[ErrorContext], None]] = None
        
        # UI state
        self._details_expanded = False
        self._details_container: Optional[ft.Container] = None
        self._expand_button: Optional[ft.IconButton] = None
        
    def show_error(
        self,
        error_context: ErrorContext,
        on_report: Optional[Callable[[ErrorContext], None]] = None
    ) -> None:
        """Show the error dialog with the given error context."""
        self.on_report_callback = on_report
        self._details_expanded = False
        
        # Create dialog content
        title = self._create_title(error_context)
        content = self._create_content(error_context)
        actions = self._create_actions(error_context)
        
        # Create and show dialog
        self.dialog = ft.AlertDialog(
            modal=True,
            title=title,
            content=content,
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
        
    def _create_title(self, error_context: ErrorContext) -> ft.Row:
        """Create the dialog title with icon and text."""
        icon = ft.Icon(
            ft.Icons.ERROR_OUTLINE,
            color=TOKENS.get('error', '#EF5350'),
            size=24
        )
        
        title_text = ft.Text(
            error_context.friendly_title or "Error Occurred",
            weight=ft.FontWeight.BOLD,
            size=20
        )
        
        return ft.Row(
            controls=[icon, title_text],
            alignment=ft.MainAxisAlignment.START,
            spacing=12
        )
        
    def _create_content(self, error_context: ErrorContext) -> ft.Column:
        """Create the main content of the dialog."""
        # Main error message
        message = ft.Text(
            error_context.friendly_message or "An unexpected error occurred.",
            size=16,
            color=TOKENS.get('on_surface', '#1C2A35')
        )
        
        # Expandable details section
        self._details_container = self._create_details_container(error_context)
        
        # Expand/collapse button
        self._expand_button = ft.IconButton(
            icon=ft.Icons.EXPAND_MORE,
            tooltip="Show details",
            on_click=self._toggle_details,
            icon_color=TOKENS.get('on_surface', '#1C2A35')
        )
        
        # Details header row
        details_header = ft.Row(
            controls=[
                ft.Text("Details", size=14, weight=ft.FontWeight.W_500),
                self._expand_button
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        return ft.Column(
            controls=[
                message,
                ft.Divider(height=20, thickness=1, color=TOKENS.get('outline', '#6F797B')),
                details_header,
                self._details_container
            ],
            spacing=12
        )
        
    def _create_details_container(self, error_context: ErrorContext) -> ft.Container:
        """Create the expandable details container."""
        # Format error details
        formatter = ErrorFormatter()
        details_text = formatter.format_error_details(error_context)
        
        # Create text field for details
        details_field = ft.TextField(
            value=details_text,
            read_only=True,
            multiline=True,
            min_lines=3,
            max_lines=10,
            text_size=12,
            border=ft.InputBorder.OUTLINE,
            border_color=TOKENS.get('outline', '#6F797B'),
            focused_border_color=TOKENS.get('primary', '#38A298')
        )
        
        return ft.Container(
            content=details_field,
            visible=False,  # Hidden by default
            margin=ft.margin.only(top=8)
        )
        
    def _create_actions(self, error_context: ErrorContext) -> list:
        """Create the dialog action buttons."""
        actions = []
        
        # Report button (if callback provided)
        if self.on_report_callback:
            report_button = ft.TextButton(
                "Report Issue",
                on_click=lambda e: self._handle_report(error_context),
                style=ft.ButtonStyle(
                    color=TOKENS.get('primary', '#38A298')
                )
            )
            actions.append(report_button)
        
        # Copy details button
        copy_button = ft.TextButton(
            "Copy Details",
            on_click=lambda e: self._handle_copy(error_context),
            style=ft.ButtonStyle(
                color=TOKENS.get('on_surface', '#1C2A35')
            )
        )
        actions.append(copy_button)
        
        # Close button
        close_button = ft.TextButton(
            "Close",
            on_click=self._handle_close,
            style=ft.ButtonStyle(
                color=TOKENS.get('primary', '#38A298')
            )
        )
        actions.append(close_button)
        
        return actions
        
    def _toggle_details(self, e) -> None:
        """Toggle visibility of error details."""
        if self._details_container and self._expand_button:
            self._details_expanded = not self._details_expanded
            
            # Update container visibility
            self._details_container.visible = self._details_expanded
            
            # Update button icon and tooltip
            if self._details_expanded:
                self._expand_button.icon = ft.Icons.EXPAND_LESS
                self._expand_button.tooltip = "Hide details"
            else:
                self._expand_button.icon = ft.Icons.EXPAND_MORE
                self._expand_button.tooltip = "Show details"
            
            self.page.update()
            
    def _handle_report(self, error_context: ErrorContext) -> None:
        """Handle the report button click."""
        if self.on_report_callback:
            # Close dialog first
            self._handle_close(None)
            
            # Call report callback
            self.on_report_callback(error_context)
            
    def _handle_copy(self, error_context: ErrorContext) -> None:
        """Handle the copy details button click."""
        # Format and copy error details to clipboard
        formatter = ErrorFormatter()
        details_text = formatter.format_error_details(error_context)
        
        # Copy to clipboard (if supported)
        if hasattr(self.page, 'set_clipboard'):
            self.page.set_clipboard(details_text)
            
            # Show confirmation
            if hasattr(self.page, 'show_snack_bar'):
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Error details copied to clipboard"),
                        action="Dismiss"
                    )
                )
                
    def _handle_close(self, e) -> None:
        """Handle the close button click."""
        if self.dialog:
            self.dialog.open = False
            self.page.update()


def show_error_dialog(
    page: ft.Page,
    error_context: ErrorContext,
    on_report: Optional[Callable[[ErrorContext], None]] = None
) -> ErrorDialog:
    """
    Convenience function to show an error dialog.
    
    Args:
        page: Flet page instance
        error_context: Error context to display
        on_report: Optional callback for error reporting
        
    Returns:
        ErrorDialog: The created error dialog instance
    """
    dialog = ErrorDialog(page)
    dialog.show_error(error_context, on_report)
    return dialog


def show_simple_error(page: ft.Page, message: str, title: str = "Error") -> ErrorDialog:
    """
    Convenience function to show a simple error dialog.
    
    Args:
        page: Flet page instance
        message: Error message to display
        title: Error dialog title
        
    Returns:
        ErrorDialog: The created error dialog instance
    """
    error_context = ErrorContext(
        error_type="SimpleError",
        friendly_title=title,
        friendly_message=message
    )
    return show_error_dialog(page, error_context)