"""
Base Action Handler

Provides common functionality and eliminates boilerplate patterns for all action handlers.
This base class implements the consolidated action execution patterns using the enhanced
ActionExecutor and standardizes UI integration patterns. Now includes integration with
the centralized error boundary system for robust error handling.
"""

import flet as ft
import asyncio
from typing import Optional, Callable, Dict, Any, List
from abc import ABC
from ..utils.action_executor import get_action_executor
from ..utils.action_result import ActionResult
from ..utils.trace_center import get_trace_center
from .error_boundary import ErrorBoundary


class BaseActionHandler(ABC):
    """
    Base class for all action handlers.
    
    Provides standardized patterns for:
    - Action execution through ActionExecutor
    - Data change callback management
    - Dialog system integration
    - Toast/notification management
    - Error handling through ErrorBoundary
    - Centralized exception management
    """
    
    def __init__(self, server_bridge, dialog_system, toast_manager, page: ft.Page):
        """
        Initialize base action handler with common dependencies.
        
        Args:
            server_bridge: Server integration interface
            dialog_system: Dialog system for confirmations and custom dialogs
            toast_manager: Toast notification manager
            page: Flet page for UI updates
        """
        self.server_bridge = server_bridge
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self.page = page
        
        # Get the enhanced action executor
        self.action_executor = get_action_executor()
        
        # Set up dialog system integration
        if dialog_system:
            self.action_executor.set_dialog_system(dialog_system)
        
        # Set up error boundary for this handler
        self.error_boundary = ErrorBoundary(page)
        self.action_executor.set_error_boundary(self.error_boundary)
        
        # Configure error boundary settings
        self.error_boundary.auto_show_dialog = False  # Actions should not auto-show dialogs
        self.error_boundary.log_errors = True
        
        # Data change callbacks
        self.on_data_changed: Optional[Callable] = None
        
        # Initialize trace center
        self._trace = get_trace_center()
    
    def create_safe_callback(self, callback: Callable, operation: Optional[str] = None) -> Callable:
        """
        Create a UI callback protected by the error boundary.
        
        This method wraps UI callbacks (like button clicks) with error boundary
        protection, ensuring that exceptions are caught and handled gracefully
        with professional error dialogs.
        
        Args:
            callback: The callback function to protect
            operation: Optional operation name for error context
            
        Returns:
            Protected callback function
        """
        return self.error_boundary.wrap_callback(
            callback, 
            operation=operation,
            component=self.__class__.__name__
        )
    
    def safe_callback(self, operation: Optional[str] = None):
        """
        Decorator for creating safe UI callbacks.
        
        Usage:
            @self.safe_callback("button click operation")
            async def on_button_click(e):
                # callback code
        """
        def decorator(func):
            return self.create_safe_callback(func, operation)
        return decorator
    
    def set_data_changed_callback(self, callback: Callable):
        """
        Set callback for when data changes and refresh is needed.
        
        Args:
            callback: Function to call when data changes occur
        """
        self.on_data_changed = callback
        # Register with action executor for automatic triggering
        self.action_executor.add_data_change_callback(callback)
    
    def remove_data_changed_callback(self):
        """Remove the current data change callback"""
        if self.on_data_changed:
            self.action_executor.remove_data_change_callback(self.on_data_changed)
            self.on_data_changed = None
    
    async def execute_action(self,
                           action_name: str,
                           action_coro: Callable,
                           confirmation_text: Optional[str] = None,
                           confirmation_title: Optional[str] = None,
                           require_selection: bool = False,
                           selection_provider: Optional[Callable] = None,
                           trigger_data_change: bool = True,
                           show_success_toast: bool = True,
                           success_message: Optional[str] = None) -> ActionResult:
        """
        Execute an action using the standardized pipeline.
        
        This method provides a consistent interface for all action execution,
        eliminating the need for boilerplate try/catch, toast management,
        busy indicators, and correlation ID handling.
        
        Args:
            action_name: Human-readable action name
            action_coro: Async function that performs the action
            confirmation_text: Optional confirmation dialog text
            confirmation_title: Optional confirmation dialog title
            require_selection: Whether action requires items to be selected
            selection_provider: Function that returns selected items
            trigger_data_change: Whether to trigger data change callbacks
            show_success_toast: Whether to show success toast
            success_message: Custom success message for toast
            
        Returns:
            ActionResult with operation outcome
        """
        try:
            # Execute with confirmation if needed
            if confirmation_text:
                result = await self.action_executor.run_with_confirmation(
                    action_name=action_name,
                    action_coro=action_coro,
                    confirmation_text=confirmation_text,
                    confirmation_title=confirmation_title,
                    require_selection=require_selection,
                    selection_provider=selection_provider,
                    trigger_data_change=trigger_data_change,
                    mutate=True  # Most actions that need confirmation are mutations
                )
            else:
                # Execute without confirmation
                result = await self.action_executor.run(
                    action_name=action_name,
                    action_coro=action_coro,
                    require_selection=require_selection,
                    selection_provider=selection_provider,
                    mutate=trigger_data_change
                )
                
                # Manually trigger data change callbacks if successful
                if trigger_data_change and result.success and self.on_data_changed:
                    await self._trigger_data_change()
            
            # Show custom success toast if requested and not handled by ActionExecutor
            if (show_success_toast and result.success and success_message 
                and self.toast_manager):
                self.toast_manager.show_success(success_message)
            
            return result
            
        except Exception as e:
            # This should rarely happen as ActionExecutor handles most exceptions
            # But provide a fallback for edge cases
            cid = self._trace.new_correlation_id()
            self._trace.emit(
                type="ACTION_HANDLER_ERROR",
                level="ERROR",
                message=f"Unexpected error in action handler: {str(e)}",
                correlation_id=cid
            )
            
            return ActionResult.error(
                code="HANDLER_EXCEPTION",
                message=f"Action execution failed: {str(e)}",
                correlation_id=cid,
                error_code="HANDLER_EXCEPTION"
            )
    
    async def _trigger_data_change(self):
        """Trigger data change callback if set"""
        if self.on_data_changed:
            try:
                if asyncio.iscoroutinefunction(self.on_data_changed):
                    await self.on_data_changed()
                else:
                    self.on_data_changed()
            except Exception as e:
                self._trace.emit(
                    type="DATA_CALLBACK_ERROR",
                    level="WARN",
                    message=f"Data change callback failed: {str(e)}"
                )
    
    def _close_dialog(self):
        """Close the current dialog if dialog system is available"""
        if self.dialog_system:
            self.dialog_system.close_dialog()
    
    async def show_custom_dialog(self, title: str, content, actions: List[ft.Control] = None):
        """
        Show a custom dialog with the given content.
        
        Args:
            title: Dialog title
            content: Dialog content (Flet control or controls)
            actions: Optional dialog action buttons
        """
        if self.dialog_system:
            self.dialog_system.show_custom_dialog(
                title=title,
                content=content,
                actions=actions or [ft.TextButton("Close", on_click=lambda e: self._close_dialog())]
            )
        elif self.toast_manager:
            # Fallback to toast if no dialog system
            self.toast_manager.show_info(f"{title}: Dialog not available")
    
    async def show_confirmation(self, title: str, message: str) -> bool:
        """
        Show a confirmation dialog and return the result.
        
        Args:
            title: Confirmation dialog title
            message: Confirmation message
            
        Returns:
            True if user confirmed, False otherwise
        """
        if self.dialog_system:
            return await self.dialog_system.show_confirmation_async(
                title=title,
                message=message
            )
        else:
            # If no dialog system, default to True (assume confirmation)
            # This ensures functionality doesn't break in fallback scenarios
            if self.toast_manager:
                self.toast_manager.show_warning("Confirmation dialog not available - proceeding")
            return True
    
    def show_error(self, message: str, title: str = "Error"):
        """Show an error message to the user"""
        if self.toast_manager:
            self.toast_manager.show_error(message)
        elif self.dialog_system:
            self.dialog_system.show_error(title, message)
    
    def show_success(self, message: str):
        """Show a success message to the user"""
        if self.toast_manager:
            self.toast_manager.show_success(message)
    
    def show_warning(self, message: str):
        """Show a warning message to the user"""
        if self.toast_manager:
            self.toast_manager.show_warning(message)
    
    def show_info(self, message: str):
        """Show an info message to the user"""
        if self.toast_manager:
            self.toast_manager.show_info(message)


class UIActionMixin:
    """
    Mixin class providing common UI action patterns.
    
    This can be used alongside BaseActionHandler for handlers that need
    additional UI-specific functionality.
    """
    
    def create_details_content(self, data: Dict[str, Any], title: str = "Details") -> ft.Control:
        """
        Create a standardized details view for data objects.
        
        Args:
            data: Data dictionary to display
            title: Title for the details view
            
        Returns:
            Flet control with formatted details
        """
        details_rows = []
        
        for key, value in data.items():
            # Format key (capitalize and replace underscores)
            formatted_key = key.replace('_', ' ').title()
            
            # Format value based on type
            if isinstance(value, dict):
                formatted_value = f"{len(value)} items"
            elif isinstance(value, list):
                formatted_value = f"{len(value)} items" 
            elif isinstance(value, bool):
                formatted_value = "Yes" if value else "No"
            elif value is None:
                formatted_value = "N/A"
            else:
                formatted_value = str(value)
            
            details_rows.append(
                ft.Row([
                    ft.Text(f"{formatted_key}:", weight=ft.FontWeight.BOLD, expand=1),
                    ft.Text(formatted_value, expand=2)
                ])
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(title, style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Divider(),
                ft.Column(details_rows, spacing=8)
            ]),
            padding=16,
            width=500
        )
    
    def create_confirmation_content(self, message: str, details: Optional[str] = None) -> ft.Control:
        """
        Create standardized confirmation dialog content.
        
        Args:
            message: Main confirmation message
            details: Optional additional details
            
        Returns:
            Flet control with confirmation content
        """
        content_items = [ft.Text(message)]
        
        if details:
            content_items.extend([
                ft.Divider(),
                ft.Text(details, style=ft.TextThemeStyle.BODY_SMALL)
            ])
        
        return ft.Column(content_items, spacing=8)
