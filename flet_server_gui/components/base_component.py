"""
Base Component Class

Provides common patterns and utilities for all UI components.
This enables consistent behavior and reduces code duplication.
"""

import flet as ft
from typing import Callable, Optional, Any, Dict, List
from flet_server_gui.actions.base_action import ActionResult
import asyncio


class BaseComponent:
    """
    Base class for all UI components providing common patterns.
    
    This class implements generic UI patterns that components can reuse,
    such as confirmation dialogs, error handling, and loading states.
    """
    
    def __init__(self, page: ft.Page, dialog_system=None, toast_manager=None):
        """
        Initialize base component.
        
        Args:
            page: Flet page instance for UI updates
            dialog_system: Optional dialog system for confirmations
            toast_manager: Optional toast manager for notifications
        """
        self.page = page
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self._loading_states: Dict[str, bool] = {}
    
    async def execute_with_confirmation(
        self,
        action: Callable[[], Any],
        confirmation_text: str,
        success_message: str,
        operation_name: str = "Operation"
    ) -> bool:
        """
        Execute an action with user confirmation and comprehensive feedback.
        
        This method implements the common pattern of:
        1. Show confirmation dialog
        2. Execute action if confirmed  
        3. Show success/error feedback
        4. Handle loading states
        
        Args:
            action: Async function to execute
            confirmation_text: Text to display in confirmation dialog
            success_message: Message to show on success
            operation_name: Name of operation for loading state tracking
            
        Returns:
            True if operation completed successfully, False otherwise
        """
        # Show confirmation dialog
        confirmed = await self._show_confirmation(confirmation_text)
        if not confirmed:
            return False
        
        # Set loading state
        self._set_loading_state(operation_name, True)
        
        try:
            # Execute the action
            result = await action()
            
            # Handle ActionResult or direct boolean results
            if isinstance(result, ActionResult):
                if result.success:
                    await self._show_success(success_message)
                    return True
                else:
                    await self._show_error(result.error_message or "Operation failed")
                    return False
            else:
                # Assume boolean or truthy result
                if result:
                    await self._show_success(success_message)
                    return True
                else:
                    await self._show_error("Operation failed")
                    return False
                    
        except Exception as e:
            await self._show_error(f"Unexpected error: {str(e)}")
            return False
            
        finally:
            # Clear loading state
            self._set_loading_state(operation_name, False)
    
    async def execute_bulk_action(
        self,
        action: Callable[[List[str]], Any],
        selected_items: List[str],
        item_type: str,
        action_name: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """
        Execute a bulk action with progress tracking and comprehensive feedback.
        
        Args:
            action: Async function that takes list of IDs and returns ActionResult
            selected_items: List of item IDs to process
            item_type: Type of items (e.g., "clients", "files") for messages
            action_name: Name of action (e.g., "delete", "download") for messages
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if all operations succeeded, False otherwise
        """
        if not selected_items:
            await self._show_error(f"No {item_type} selected for {action_name}")
            return False
        
        # Show confirmation
        confirmation_text = f"{action_name.title()} {len(selected_items)} selected {item_type}?"
        confirmed = await self._show_confirmation(confirmation_text)
        if not confirmed:
            return False
        
        # Set loading state
        operation_name = f"bulk_{action_name}_{item_type}"
        self._set_loading_state(operation_name, True)
        
        try:
            # Execute bulk action
            result = await action(selected_items)
            
            # Update progress if callback provided
            if progress_callback:
                progress_callback(len(selected_items), len(selected_items))
            
            # Handle result
            if isinstance(result, ActionResult):
                if result.success:
                    success_count = len(selected_items)
                    if result.metadata and 'successful_operations' in result.metadata:
                        success_count = result.metadata['successful_operations']
                    
                    success_message = f"Successfully processed {success_count} {item_type}"
                    await self._show_success(success_message)
                    return True
                else:
                    error_message = result.error_message or f"Bulk {action_name} failed"
                    if result.metadata and 'failure_messages' in result.metadata:
                        # Show detailed error information
                        failure_count = result.metadata.get('failed_operations', 0)
                        error_message = f"{failure_count} {item_type} failed to {action_name}"
                    
                    await self._show_error(error_message)
                    return False
            else:
                # Handle non-ActionResult responses
                if result:
                    await self._show_success(f"Successfully processed {len(selected_items)} {item_type}")
                    return True
                else:
                    await self._show_error(f"Bulk {action_name} failed")
                    return False
                    
        except Exception as e:
            await self._show_error(f"Bulk {action_name} failed: {str(e)}")
            return False
            
        finally:
            self._set_loading_state(operation_name, False)
    
    async def _show_confirmation(self, message: str) -> bool:
        """
        Show confirmation dialog.
        
        Args:
            message: Confirmation message to display
            
        Returns:
            True if user confirmed, False otherwise
        """
        if self.dialog_system:
            return await self.dialog_system.show_confirmation_async(
                title="Confirm Action",
                message=message
            )
        else:
            # Fallback to simple confirm dialog
            # For now, just return True to allow the action to proceed
            # In a real app, you'd implement proper async dialog handling
            print(f"CONFIRMATION: {message}")
            return True  # Default to True for fallback to allow actions to proceed
    
    async def _show_success(self, message: str):
        """Show success notification."""
        try:
            if self.toast_manager and hasattr(self.toast_manager, 'show_success'):
                # Check if the method returns an awaitable
                result = self.toast_manager.show_success(message)
                if hasattr(result, '__await__'):
                    await result
                else:
                    # If it's not awaitable, just call it
                    result
            else:
                # Fallback - could show snackbar or other notification
                print(f"SUCCESS: {message}")
        except Exception as e:
            # Fallback if anything fails
            print(f"SUCCESS: {message}")
            print(f"Toast manager error: {e}")
    
    async def _show_error(self, message: str):
        """Show error notification.""" 
        try:
            if self.toast_manager and hasattr(self.toast_manager, 'show_error'):
                # Check if the method returns an awaitable
                result = self.toast_manager.show_error(message)
                if hasattr(result, '__await__'):
                    await result
                else:
                    # If it's not awaitable, just call it
                    result
            else:
                # Fallback - could show snackbar or other notification
                print(f"ERROR: {message}")
        except Exception as e:
            # Fallback if anything fails
            print(f"ERROR: {message}")
            print(f"Toast manager error: {e}")
    
    def _set_loading_state(self, operation_name: str, loading: bool):
        """
        Set loading state for an operation.
        
        Args:
            operation_name: Unique identifier for the operation
            loading: Whether operation is loading
        """
        self._loading_states[operation_name] = loading
        # Subclasses can override to update UI loading indicators
        self._on_loading_state_changed(operation_name, loading)
    
    def _on_loading_state_changed(self, operation_name: str, loading: bool):
        """
        Called when loading state changes. Override in subclasses.
        
        Args:
            operation_name: Name of the operation
            loading: New loading state
        """
        pass
    
    def is_loading(self, operation_name: str = None) -> bool:
        """
        Check if component is in loading state.
        
        Args:
            operation_name: Specific operation to check, or None for any operation
            
        Returns:
            True if loading, False otherwise
        """
        if operation_name:
            return self._loading_states.get(operation_name, False)
        else:
            return any(self._loading_states.values())
    
    def get_responsive_width(self, base_width: int, screen_width: int) -> Optional[int]:
        """
        Calculate responsive width based on screen size.
        
        Args:
            base_width: Base width for large screens
            screen_width: Current screen width
            
        Returns:
            Responsive width or None for full width
        """
        if screen_width < 768:  # Mobile
            return None  # Full width
        elif screen_width < 992:  # Tablet
            return min(base_width, screen_width - 40)  # Leave some margin
        else:  # Desktop
            return base_width
    
    def get_responsive_padding(self, screen_width: int) -> ft.padding:
        """
        Get responsive padding based on screen size.
        
        Args:
            screen_width: Current screen width
            
        Returns:
            Appropriate padding for screen size
        """
        if screen_width < 576:  # Extra small
            return ft.padding.all(8)
        elif screen_width < 768:  # Small
            return ft.padding.all(12)
        elif screen_width < 992:  # Medium
            return ft.padding.all(16)
        else:  # Large and above
            return ft.padding.all(20)
    
    def _close_dialog(self, result: bool):
        """Close dialog with result (simplified implementation)."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
        return result