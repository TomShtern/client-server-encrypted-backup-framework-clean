"""error_boundary.py

Centralized Error Boundary Component for UI Exception Handling
==============================================================

Provides a comprehensive error boundary system that catches unhandled exceptions
in UI callbacks and presents them through a professional error dialog. Supports
multiple usage patterns including decorators, context managers, and automatic
integration with the action handler system.

Key Features:
- Catch unhandled exceptions in UI callbacks
- Professional error dialog with collapsible stack traces
- Integration with existing logging and correlation ID systems
- Multiple usage patterns for flexibility
- Automatic error reporting and logging
- User-friendly error messages with technical details available

Usage Patterns:
1. Decorator: @error_boundary.safe_callback
2. Context Manager: async with error_boundary.protect("operation"):
3. Direct wrapping: error_boundary.wrap_callback(callback)
4. Automatic integration with BaseActionHandler
"""
from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any, Awaitable, Callable, Optional, TypeVar, Union
from contextlib import asynccontextmanager

import flet as ft

from ..utils.error_context import ErrorContext, create_error_context
from .error_dialog import ErrorDialog, show_error_dialog
from ..utils.trace_center import get_trace_center

# Type variables for generic typing
F = TypeVar('F', bound=Callable[..., Any])
AF = TypeVar('AF', bound=Callable[..., Awaitable[Any]])


class ErrorBoundary:
    """Central error boundary for catching and handling UI exceptions."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.error_dialog = ErrorDialog(page)
        self._error_handlers = []
        self._report_callback: Optional[Callable[[ErrorContext], None]] = None
        
        # Configuration
        self.auto_show_dialog = True
        self.capture_locals = False  # Set to True for debugging
        self.log_errors = True
        
    def set_error_report_callback(
        self, 
        callback: Callable[[ErrorContext], None]
    ) -> None:
        """Set a callback for reporting errors (e.g., to external service)."""
        self._report_callback = callback
    
    def add_error_handler(
        self, 
        handler: Callable[[ErrorContext], bool]
    ) -> None:
        """Add a custom error handler. Return True to prevent default handling."""
        self._error_handlers.append(handler)
    
    def safe_callback(self, func: F) -> F:
        """Decorator to wrap UI callbacks with error boundary protection."""
        
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._handle_async_callback(func, *args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self._handle_sync_callback(func, *args, **kwargs)
            return sync_wrapper
    
    def wrap_callback(
        self, 
        callback: Callable,
        operation: Optional[str] = None,
        component: Optional[str] = None
    ) -> Callable:
        """Programmatically wrap a callback with error boundary protection."""
        
        if asyncio.iscoroutinefunction(callback):
            async def wrapped_async(*args, **kwargs):
                return await self._handle_async_callback(
                    callback, *args, 
                    operation=operation, 
                    component=component, 
                    **kwargs
                )
            return wrapped_async
        else:
            def wrapped_sync(*args, **kwargs):
                return self._handle_sync_callback(
                    callback, *args,
                    operation=operation,
                    component=component,
                    **kwargs
                )
            return wrapped_sync
    
    @asynccontextmanager
    async def protect(
        self, 
        operation: str,
        component: Optional[str] = None,
        user_message: Optional[str] = None
    ):
        """Context manager for protecting code blocks with error boundary."""
        try:
            yield
        except Exception as e:
            await self._handle_exception(
                e, 
                operation=operation, 
                component=component,
                user_message=user_message
            )
            raise  # Re-raise after handling
    
    async def _handle_async_callback(
        self, 
        callback: Callable,
        *args,
        operation: Optional[str] = None,
        component: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Handle async callback execution with error boundary."""
        try:
            return await callback(*args, **kwargs)
        except Exception as e:
            await self._handle_exception(
                e,
                operation=operation or f"async callback {callback.__name__}",
                component=component or self._extract_component_name(callback)
            )
            # Don't re-raise for UI callbacks to prevent crash
            return None
    
    def _handle_sync_callback(
        self, 
        callback: Callable,
        *args,
        operation: Optional[str] = None,
        component: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Handle sync callback execution with error boundary."""
        try:
            return callback(*args, **kwargs)
        except Exception as e:
            # Create async task to handle the exception
            asyncio.create_task(self._handle_exception(
                e,
                operation=operation or f"sync callback {callback.__name__}",
                component=component or self._extract_component_name(callback)
            ))
            # Don't re-raise for UI callbacks to prevent crash
            return None
    
    async def _handle_exception(
        self,
        exception: Exception,
        operation: Optional[str] = None,
        component: Optional[str] = None,
        user_message: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """Handle an exception with error context creation and processing."""
        
        # Create error context
        error_context = create_error_context(
            exception=exception,
            operation=operation,
            component=component,
            user_message=user_message,
            capture_locals=self.capture_locals,
            correlation_id=correlation_id
        )
        
        # Log the error
        if self.log_errors:
            error_context.log_error()
        
        # Process through custom error handlers
        handled = False
        for handler in self._error_handlers:
            try:
                if handler(error_context):
                    handled = True
                    break
            except Exception as handler_error:
                # Log handler errors but don't let them break error processing
                get_trace_center().emit(
                    type="ERROR_HANDLER_FAILED",
                    level="ERROR",
                    message=f"Error handler failed: {str(handler_error)}",
                    correlation_id=error_context.correlation_id
                )
        
        # Show error dialog if not handled and auto-show is enabled
        if not handled and self.auto_show_dialog:
            try:
                show_error_dialog(
                    self.page, 
                    error_context, 
                    on_report=self._report_callback
                )
            except Exception as dialog_error:
                # Fallback to simple error display if dialog fails
                get_trace_center().emit(
                    type="ERROR_DIALOG_FAILED",
                    level="ERROR",
                    message=f"Error dialog failed: {str(dialog_error)}",
                    correlation_id=error_context.correlation_id
                )
                self._show_fallback_error(error_context)
    
    def _extract_component_name(self, callback: Callable) -> Optional[str]:
        """Extract component name from callback if possible."""
        try:
            if hasattr(callback, '__self__'):
                return callback.__self__.__class__.__name__
            elif hasattr(callback, '__qualname__'):
                parts = callback.__qualname__.split('.')
                if len(parts) > 1:
                    return parts[-2]  # Class name
        except Exception:
            pass
        return None
    
    def _show_fallback_error(self, error_context: ErrorContext) -> None:
        """Show a simple fallback error if the main dialog fails."""
        try:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(
                        f"Error: {error_context.user_message} (ID: {error_context.correlation_id[:8]})"
                    ),
                    bgcolor=ft.colors.ERROR,
                    duration=5000
                )
            )
        except Exception:
            # Ultimate fallback - just print to console
            print(f"CRITICAL ERROR: {error_context.error_message}")
            print(f"Correlation ID: {error_context.correlation_id}")


class GlobalErrorBoundary:
    """Global error boundary singleton for application-wide error handling."""
    
    _instance: Optional[ErrorBoundary] = None
    _page: Optional[ft.Page] = None
    
    @classmethod
    def initialize(cls, page: ft.Page) -> ErrorBoundary:
        """Initialize the global error boundary with a Flet page."""
        cls._page = page
        cls._instance = ErrorBoundary(page)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> Optional[ErrorBoundary]:
        """Get the global error boundary instance."""
        return cls._instance
    
    @classmethod
    def safe_callback(cls, func: F) -> F:
        """Decorator for the global error boundary."""
        if cls._instance:
            return cls._instance.safe_callback(func)
        else:
            # Return unwrapped function if not initialized
            return func
    
    @classmethod
    async def protect(
        cls,
        operation: str,
        component: Optional[str] = None,
        user_message: Optional[str] = None
    ):
        """Context manager for the global error boundary."""
        if cls._instance:
            async with cls._instance.protect(operation, component, user_message):
                yield
        else:
            # No protection if not initialized
            yield


# Global instance decorator and context manager
safe_callback = GlobalErrorBoundary.safe_callback
protect = GlobalErrorBoundary.protect


# Utility functions for common error handling patterns
def handle_ui_error(
    page: ft.Page,
    exception: Exception,
    operation: str = "UI operation",
    component: Optional[str] = None,
    show_dialog: bool = True
) -> None:
    """Handle a UI error with proper error context and dialog."""
    
    error_context = create_error_context(
        exception=exception,
        operation=operation,
        component=component
    )
    
    error_context.log_error()
    
    if show_dialog:
        show_error_dialog(page, error_context)


async def safe_async_operation(
    operation: Callable[[], Awaitable[Any]],
    page: ft.Page,
    operation_name: str = "async operation",
    component: Optional[str] = None,
    show_dialog: bool = True
) -> Optional[Any]:
    """Safely execute an async operation with error handling."""
    
    try:
        return await operation()
    except Exception as e:
        handle_ui_error(
            page=page,
            exception=e,
            operation=operation_name,
            component=component,
            show_dialog=show_dialog
        )
        return None


def safe_sync_operation(
    operation: Callable[[], Any],
    page: ft.Page,
    operation_name: str = "sync operation",
    component: Optional[str] = None,
    show_dialog: bool = True
) -> Optional[Any]:
    """Safely execute a sync operation with error handling."""
    
    try:
        return operation()
    except Exception as e:
        handle_ui_error(
            page=page,
            exception=e,
            operation=operation_name,
            component=component,
            show_dialog=show_dialog
        )
        return None


# Integration helpers for existing systems
def create_safe_button(
    text: str,
    on_click: Callable,
    page: ft.Page,
    operation: Optional[str] = None,
    **button_kwargs
) -> ft.ElevatedButton:
    """Create a button with automatic error boundary protection."""
    
    safe_click = GlobalErrorBoundary.safe_callback(on_click) if GlobalErrorBoundary.get_instance() else on_click
    
    return ft.ElevatedButton(
        text=text,
        on_click=safe_click,
        **button_kwargs
    )


def create_safe_icon_button(
    icon: str,
    on_click: Callable,
    page: ft.Page,
    operation: Optional[str] = None,
    **button_kwargs
) -> ft.IconButton:
    """Create an icon button with automatic error boundary protection."""
    
    safe_click = GlobalErrorBoundary.safe_callback(on_click) if GlobalErrorBoundary.get_instance() else on_click
    
    return ft.IconButton(
        icon=icon,
        on_click=safe_click,
        **button_kwargs
    )
