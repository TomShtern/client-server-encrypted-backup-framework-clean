"""error_dialog.py

Professional Error Dialog Component for Centralized Error Boundary
==================================================================

Provides a user-friendly, professional error dialog that presents errors
in a non-intimidating way while still providing developers with detailed
debugging information. Features collapsible technical details and
copy-to-clipboard functionality.

Design Principles:
- User-friendly primary interface (non-technical language)
- Progressive disclosure of technical details
- Professional Material Design 3 styling
- Clear action buttons (Close, Copy, Report)
- Theme-aware coloring and typography
- Accessible design with proper contrast and focus management
"""
from __future__ import annotations

import flet as ft
import asyncio
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from .error_context import ErrorContext, ErrorFormatter
from ..ui.unified_theme_system import TOKENS


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
        self.dialog = self._create_error_dialog(error_context)
        
        # Show the dialog
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def _create_error_dialog(self, error_context: ErrorContext) -> ft.AlertDialog:
        """Create the error dialog with all components."""
        
        # Title with error icon
        title_row = ft.Row([
            ft.Icon(
                ft.icons.ERROR_OUTLINE,
                color=self._get_error_color(error_context.severity),
                size=28
            ),
            ft.Text(
                "Something went wrong",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.ON_SURFACE
            )
        ], spacing=12, alignment=ft.MainAxisAlignment.START)
        
        # Main content
        content = self._create_dialog_content(error_context)
        
        # Action buttons
        actions = self._create_action_buttons(error_context)
        
        return ft.AlertDialog(
            title=title_row,
            content=ft.Container(
                content=content,
                width=500,
                padding=ft.padding.all(10)
            ),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            modal=True,
            bgcolor=ft.colors.SURFACE,
            title_padding=ft.padding.all(20),
            content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
            actions_padding=ft.padding.all(20)
        )
    
    def _create_dialog_content(self, error_context: ErrorContext) -> ft.Column:
        """Create the main content of the dialog."""
        
        # User-friendly error message
        user_message = ft.Text(
            ErrorFormatter.format_for_user(error_context),
            size=16,
            color=ft.colors.ON_SURFACE,
            weight=ft.FontWeight.NORMAL
        )
        
        # Operation context if available
        context_widgets = []
        if error_context.operation:
            context_widgets.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.INFO_OUTLINE, size=16, color=ft.colors.OUTLINE),
                        ft.Text(
                            f"While performing: {error_context.operation}",
                            size=14,
                            color=ft.colors.OUTLINE,
                            italic=True
                        )
                    ], spacing=8),
                    margin=ft.margin.only(top=10)
                )
            )
        
        # Technical details section (collapsible)
        details_section = self._create_details_section(error_context)
        
        return ft.Column([
            user_message,
            *context_widgets,
            ft.Container(height=20),  # Spacer
            details_section
        ], spacing=0, tight=True)
    
    def _create_details_section(self, error_context: ErrorContext) -> ft.Container:
        """Create the collapsible technical details section."""
        
        # Expand/collapse button
        self._expand_button = ft.IconButton(
            icon=ft.icons.EXPAND_MORE,
            tooltip="Show technical details",
            on_click=lambda _: self._toggle_details(error_context),
            icon_size=20
        )
        
        # Details header
        details_header = ft.Container(
            content=ft.Row([
                ft.Text(
                    "Technical Details",
                    size=14,
                    weight=ft.FontWeight.W500,
                    color=ft.colors.PRIMARY
                ),
                self._expand_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border_radius=ft.border_radius.only(top_left=8, top_right=8),
            on_click=lambda _: self._toggle_details(error_context)
        )
        
        # Details content (initially hidden)
        self._details_container = ft.Container(
            content=self._create_details_content(error_context),
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=ft.padding.all(16),
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            visible=False
        )
        
        return ft.Container(
            content=ft.Column([
                details_header,
                self._details_container
            ], spacing=0),
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=8
        )
    
    def _create_details_content(self, error_context: ErrorContext) -> ft.Column:
        """Create the technical details content."""
        
        details = ErrorFormatter.format_technical_details(error_context)
        
        # Create detail items
        detail_widgets = []
        for detail in details:
            detail_widgets.append(
                ft.Text(
                    detail,
                    size=12,
                    color=ft.colors.ON_SURFACE_VARIANT,
                    selectable=True
                )
            )
        
        # Stack trace section
        stack_trace_section = None
        if error_context.stack_trace:
            stack_trace_section = ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Stack Trace:",
                        size=12,
                        weight=ft.FontWeight.W500,
                        color=ft.colors.ON_SURFACE_VARIANT
                    ),
                    ft.Container(
                        content=ft.Text(
                            error_context.stack_trace,
                            size=10,
                            color=ft.colors.ON_SURFACE_VARIANT,
                            font_family="Courier New",
                            selectable=True
                        ),
                        bgcolor=ft.colors.SURFACE,
                        padding=ft.padding.all(8),
                        border_radius=4,
                        border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
                        height=200,
                        scroll=ft.ScrollMode.AUTO
                    )
                ], spacing=8),
                margin=ft.margin.only(top=12)
            )
        
        content_widgets = detail_widgets.copy()
        if stack_trace_section:
            content_widgets.append(stack_trace_section)
        
        return ft.Column(content_widgets, spacing=8)
    
    def _create_action_buttons(self, error_context: ErrorContext) -> list:
        """Create the action buttons for the dialog."""
        
        # Copy button
        copy_button = ft.TextButton(
            text="Copy Details",
            icon=ft.icons.COPY,
            on_click=lambda _: self._copy_to_clipboard(error_context),
            style=ft.ButtonStyle(
                color=ft.colors.PRIMARY
            )
        )
        
        # Report button (if callback provided)
        report_button = None
        if self.on_report_callback:
            report_button = ft.TextButton(
                text="Report Issue",
                icon=ft.icons.BUG_REPORT,
                on_click=lambda _: self._report_error(error_context),
                style=ft.ButtonStyle(
                    color=ft.colors.SECONDARY
                )
            )
        
        # Close button
        close_button = ft.TextButton(
            text="Close",
            on_click=lambda _: self._close_dialog(),
            style=ft.ButtonStyle(
                color=ft.colors.PRIMARY
            )
        )
        
        # Arrange buttons
        left_buttons = [copy_button]
        if report_button:
            left_buttons.append(report_button)
        
        return [
            ft.Row(left_buttons, spacing=8),
            close_button
        ]
    
    def _toggle_details(self, error_context: ErrorContext) -> None:
        """Toggle the visibility of technical details."""
        self._details_expanded = not self._details_expanded
        
        if self._details_container:
            self._details_container.visible = self._details_expanded
        
        if self._expand_button:
            self._expand_button.icon = (
                ft.icons.EXPAND_LESS if self._details_expanded 
                else ft.icons.EXPAND_MORE
            )
            self._expand_button.tooltip = (
                "Hide technical details" if self._details_expanded 
                else "Show technical details"
            )
        
        self.page.update()
    
    def _copy_to_clipboard(self, error_context: ErrorContext) -> None:
        """Copy error details to clipboard."""
        try:
            clipboard_text = error_context.to_clipboard_text()
            self.page.set_clipboard(clipboard_text)
            
            # Show confirmation
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Error details copied to clipboard"),
                    bgcolor=ft.colors.SUCCESS,
                    duration=3000
                )
            )
        except Exception as e:
            # Show error if copy fails
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Failed to copy: {str(e)}"),
                    bgcolor=ft.colors.ERROR,
                    duration=3000
                )
            )
    
    def _report_error(self, error_context: ErrorContext) -> None:
        """Report the error using the provided callback."""
        if self.on_report_callback:
            try:
                self.on_report_callback(error_context)
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Error report submitted"),
                        bgcolor=ft.colors.SUCCESS,
                        duration=3000
                    )
                )
            except Exception as e:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Failed to report error: {str(e)}"),
                        bgcolor=ft.colors.ERROR,
                        duration=3000
                    )
                )
    
    def _close_dialog(self) -> None:
        """Close the error dialog."""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
    
    def _get_error_color(self, severity: str) -> str:
        """Get the appropriate color for error severity."""
        severity_colors = {
            "critical": ft.colors.ERROR,
            "error": ft.colors.ERROR,
            "warning": ft.colors.ORANGE,
            "info": ft.colors.BLUE
        }
        return severity_colors.get(severity, ft.colors.ERROR)


class QuickErrorDialog:
    """Simplified error dialog for quick error display."""
    
    @staticmethod
    def show_simple_error(
        page: ft.Page,
        message: str,
        title: str = "Error",
        details: Optional[str] = None
    ) -> None:
        """Show a simple error dialog with minimal information."""
        
        content_widgets = [
            ft.Text(message, size=14, color=ft.colors.ON_SURFACE)
        ]
        
        if details:
            content_widgets.extend([
                ft.Container(height=10),
                ft.Text(
                    "Details:",
                    size=12,
                    weight=ft.FontWeight.W500,
                    color=ft.colors.ON_SURFACE_VARIANT
                ),
                ft.Container(
                    content=ft.Text(
                        details,
                        size=11,
                        color=ft.colors.ON_SURFACE_VARIANT,
                        font_family="Courier New",
                        selectable=True
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    padding=ft.padding.all(8),
                    border_radius=4,
                    margin=ft.margin.only(top=4)
                )
            ])
        
        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.ERROR_OUTLINE, color=ft.colors.ERROR, size=24),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD)
            ], spacing=10),
            content=ft.Container(
                content=ft.Column(content_widgets, spacing=8),
                width=400,
                padding=ft.padding.all(10)
            ),
            actions=[
                ft.TextButton(
                    text="Close",
                    on_click=lambda _: setattr(dialog, 'open', False) or page.update()
                )
            ],
            modal=True
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()


# Convenience function for showing errors
def show_error_dialog(
    page: ft.Page,
    error_context: ErrorContext,
    on_report: Optional[Callable[[ErrorContext], None]] = None
) -> None:
    """Convenience function to show an error dialog."""
    error_dialog = ErrorDialog(page)
    error_dialog.show_error(error_context, on_report)


def show_simple_error(
    page: ft.Page,
    message: str,
    title: str = "Error",
    details: Optional[str] = None
) -> None:
    """Convenience function to show a simple error dialog."""
    QuickErrorDialog.show_simple_error(page, message, title, details)
