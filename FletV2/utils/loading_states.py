#!/usr/bin/env python3
"""
Enhanced Loading States for FletV2
Provides consistent loading feedback across all async operations.

This centralizes loading state management to provide professional
user feedback during data fetching operations.
"""

import flet as ft
import asyncio
from typing import Optional, Callable, Any
from utils.debug_setup import get_logger

logger = get_logger(__name__)


class LoadingState:
    """Manages loading state for a specific control or operation."""
    
    def __init__(self, 
                 status_control: Optional[ft.Control] = None,
                 loading_control: Optional[ft.Control] = None):
        """
        Initialize loading state manager.
        
        Args:
            status_control: Text control to show status messages
            loading_control: Control to show/hide during loading (e.g., ProgressRing)
        """
        self.status_control = status_control
        self.loading_control = loading_control
        self.is_loading = False
    
    async def set_loading(self, message: str = "Loading...") -> None:
        """Set loading state with message."""
        self.is_loading = True
        
        if (self.status_control and 
            hasattr(self.status_control, 'page') and 
            self.status_control.page is not None):
            self.status_control.value = message
            self.status_control.update()
        
        if (self.loading_control and 
            hasattr(self.loading_control, 'page') and 
            self.loading_control.page is not None):
            self.loading_control.visible = True
            self.loading_control.update()
    
    async def set_success(self, message: str) -> None:
        """Set success state with message."""
        self.is_loading = False
        
        if (self.status_control and 
            hasattr(self.status_control, 'page') and 
            self.status_control.page is not None):
            self.status_control.value = message
            self.status_control.color = ft.Colors.PRIMARY
            self.status_control.update()
        
        if (self.loading_control and 
            hasattr(self.loading_control, 'page') and 
            self.loading_control.page is not None):
            self.loading_control.visible = False
            self.loading_control.update()
    
    async def set_error(self, message: str) -> None:
        """Set error state with message."""
        self.is_loading = False
        
        if (self.status_control and 
            hasattr(self.status_control, 'page') and 
            self.status_control.page is not None):
            self.status_control.value = message
            self.status_control.color = ft.Colors.ERROR
            self.status_control.update()
        
        if (self.loading_control and 
            hasattr(self.loading_control, 'page') and 
            self.loading_control.page is not None):
            self.loading_control.visible = False
            self.loading_control.update()


def create_loading_indicator(size: int = 20) -> ft.Control:
    """Create a consistent loading indicator."""
    return ft.ProgressRing(
        width=size,
        height=size,
        visible=False,
        color=ft.Colors.PRIMARY
    )


def create_status_text(initial_text: str = "Ready") -> ft.Text:
    """Create a consistent status text control."""
    return ft.Text(
        initial_text,
        size=12,
        color=ft.Colors.ON_SURFACE,
        italic=True
    )


async def async_operation_with_loading(
    operation: Callable,
    loading_state: LoadingState,
    loading_message: str = "Loading...",
    success_message: str = "Operation completed",
    error_message: str = "Operation failed"
) -> tuple[bool, Any]:
    """
    Execute async operation with loading state management.
    
    Args:
        operation: Async function to execute
        loading_state: LoadingState instance to manage
        loading_message: Message during loading
        success_message: Message on success
        error_message: Message on error
        
    Returns:
        tuple: (success: bool, result: Any)
    """
    if loading_state.is_loading:
        return False, None
    
    try:
        await loading_state.set_loading(loading_message)
        result = await operation()
        await loading_state.set_success(success_message)
        return True, result
    except Exception as e:
        logger.error(f"Async operation failed: {e}")
        await loading_state.set_error(f"{error_message}: {str(e)}")
        return False, None


class SmartRefresh:
    """Manages smart refresh patterns with loading feedback."""
    
    def __init__(self, 
                 refresh_operation: Callable,
                 loading_state: LoadingState,
                 auto_refresh_interval: float = 0):
        """
        Initialize smart refresh manager.
        
        Args:
            refresh_operation: Async function to call for refresh
            loading_state: LoadingState to manage during refresh
            auto_refresh_interval: Seconds between auto-refreshes (0 = disabled)
        """
        self.refresh_operation = refresh_operation
        self.loading_state = loading_state
        self.auto_refresh_interval = auto_refresh_interval
        self.auto_refresh_task = None
        self.is_active = True
    
    async def refresh_once(self) -> bool:
        """Perform single refresh with loading state."""
        success, _ = await async_operation_with_loading(
            self.refresh_operation,
            self.loading_state,
            "Refreshing...",
            "Data refreshed",
            "Refresh failed"
        )
        return success
    
    async def start_auto_refresh(self, page: ft.Page) -> None:
        """Start auto-refresh loop."""
        if self.auto_refresh_interval <= 0:
            return
        
        async def refresh_loop():
            while self.is_active:
                await asyncio.sleep(self.auto_refresh_interval)
                if self.is_active:
                    await self.refresh_once()
        
        self.auto_refresh_task = page.run_task(refresh_loop)
    
    def stop_auto_refresh(self) -> None:
        """Stop auto-refresh loop."""
        self.is_active = False