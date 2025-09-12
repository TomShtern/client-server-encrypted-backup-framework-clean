#!/usr/bin/env python3
"""
Server-Mediated Operations Utility
Modular, reusable patterns for server-bridge operations with state management.
Eliminates duplication across views by providing common operation patterns.
"""

import asyncio

from typing import Any, Dict, Optional, Callable, List
from utils.debug_setup import get_logger
from utils.state_manager import StateManager
from utils.dialog_consolidation_helper import show_success_message, show_error_message

logger = get_logger(__name__)


class ServerMediatedOperations:
    """Reusable server-mediated operation patterns to eliminate code duplication"""

    def __init__(self, state_manager: StateManager, page):
        self.state_manager = state_manager
        self.page = page

    async def load_data_operation(
        self,
        state_key: str,
        server_operation: str,
        fallback_data: Any = None,
        data_processor: Optional[Callable] = None,
        loading_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Standard pattern for loading data through server bridge with fallback.

        Args:
            state_key: Key to store data in state manager
            server_operation: Name of server bridge method to call
            fallback_data: Data to use if server operation fails
            data_processor: Optional function to process data after loading
            loading_key: Loading state key (defaults to state_key)

        Returns:
            Result dictionary with success status and data
        """
        loading_key = loading_key or state_key

        try:
            self.state_manager.set_loading(loading_key, True)

            result = await self.state_manager.server_mediated_update(
                key=state_key,
                value=fallback_data,
                server_operation=server_operation
            )

            # Process data if processor provided
            if result.get('success') and data_processor:
                current_data = self.state_manager.get(state_key)
                processed_data = data_processor(current_data)
                await self.state_manager.update_async(state_key, processed_data, source="processed")

            return result

        except Exception as e:
            logger.error(f"Load operation failed for {state_key}: {e}")
            if fallback_data is not None:
                await self.state_manager.update_async(state_key, fallback_data, source="error_fallback")
            return {'success': False, 'error': str(e)}
        finally:
            self.state_manager.set_loading(loading_key, False)

    async def action_operation(
        self,
        action_name: str,
        server_operation: str,
        operation_data: Any,
        success_message: str = None,
        error_message: str = None,
        refresh_keys: List[str] = None,
        loading_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Standard pattern for user actions that modify server state.

        Args:
            action_name: Human-readable action name for logging
            server_operation: Name of server bridge method to call
            operation_data: Data to pass to server operation
            success_message: Message to show user on success
            error_message: Message to show user on error
            refresh_keys: List of state keys to refresh after operation
            loading_key: Loading state key (defaults to action_name)

        Returns:
            Result dictionary with success status and data
        """
        loading_key = loading_key or action_name

        try:
            self.state_manager.set_loading(loading_key, True)

            result = await self.state_manager.server_mediated_update(
                key=f"{action_name}_result",
                value=operation_data,
                server_operation=server_operation
            )

            if result.get('success'):
                if success_message:
                    show_success_message(self.page, success_message)

                # Refresh related data if specified
                if refresh_keys:
                    await self._refresh_data_keys(refresh_keys)

            else:
                error_msg = error_message or f"Failed to {action_name}: {result.get('message', 'Unknown error')}"
                show_error_message(self.page, error_msg)

            return result

        except Exception as e:
            logger.error(f"Action operation failed for {action_name}: {e}")
            error_msg = error_message or f"Failed to {action_name}: {str(e)}"
            show_error_message(self.page, error_msg)
            return {'success': False, 'error': str(e)}
        finally:
            self.state_manager.set_loading(loading_key, False)

    async def batch_load_operations(self, operations: List[Dict]) -> Dict[str, Any]:
        """
        Execute multiple load operations in parallel for better performance.

        Args:
            operations: List of operation configs, each containing:
                - state_key: Key for state storage
                - server_operation: Server method name
                - fallback_data: Fallback data
                - data_processor: Optional data processor function

        Returns:
            Results dictionary with success status for each operation
        """
        tasks = []
        results = {}

        for op in operations:
            task = self.load_data_operation(
                state_key=op['state_key'],
                server_operation=op['server_operation'],
                fallback_data=op.get('fallback_data'),
                data_processor=op.get('data_processor')
            )
            tasks.append((op['state_key'], task))

        # Execute all operations in parallel
        for state_key, task in tasks:
            try:
                result = await task
                results[state_key] = result
            except Exception as e:
                logger.error(f"Batch operation failed for {state_key}: {e}")
                results[state_key] = {'success': False, 'error': str(e)}

        return results

    async def _refresh_data_keys(self, state_keys: List[str]):
        """Refresh multiple state keys by triggering their reload operations"""
        for key in state_keys:
            try:
                # Trigger refresh by calling the corresponding load operation
                # This assumes a naming convention: load_{key}_operation
                current_data = self.state_manager.get(key)
                if current_data:
                    # Force refresh by clearing and reloading
                    await self.state_manager.update_async(key, None, source="refresh_clear")
                    # The UI subscriptions should handle reloading
            except Exception as e:
                logger.error(f"Failed to refresh {key}: {e}")

    def create_reactive_subscription(
        self,
        state_key: str,
        ui_update_callback: Callable,
        control: Optional[Any] = None
    ):
        """
        Create a reactive subscription that automatically updates UI when state changes.

        Args:
            state_key: State key to subscribe to
            ui_update_callback: Function to call when state changes
            control: Optional control to auto-update
        """
        def reactive_callback(new_value, old_value):
            try:
                ui_update_callback(new_value, old_value)
                logger.debug(f"Reactive UI update completed for {state_key}")
            except Exception as e:
                logger.error(f"Reactive callback failed for {state_key}: {e}")

        self.state_manager.subscribe(state_key, reactive_callback, control)

    def create_loading_subscription(self, loading_indicator, operation_keys: List[str]):
        """
        Create a subscription that shows loading indicator for multiple operations.

        Args:
            loading_indicator: UI control to show/hide based on loading state
            operation_keys: List of loading keys to monitor
        """
        def loading_callback(loading_states, old_states):
            try:
                # Show indicator if any tracked operation is loading
                is_loading = any(loading_states.get(key, False) for key in operation_keys)
                if hasattr(loading_indicator, 'visible'):
                    loading_indicator.visible = is_loading
                    loading_indicator.update()
            except Exception as e:
                logger.error(f"Loading subscription callback failed: {e}")

        self.state_manager.subscribe("loading_states", loading_callback)


# Factory function for easy instantiation
def create_server_mediated_operations(state_manager: StateManager, page) -> ServerMediatedOperations:
    """Create server-mediated operations utility"""
    return ServerMediatedOperations(state_manager, page)


# Common data processors for reuse
def timestamp_processor(data: List[Dict]) -> List[Dict]:
    """Process timestamp strings in data list"""
    if not isinstance(data, list):
        return data

    from datetime import datetime
    for item in data:
        if isinstance(item, dict) and 'timestamp' in item:
            if isinstance(item['timestamp'], str):
                try:
                    item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                except ValueError:
                    logger.warning(f"Failed to parse timestamp: {item['timestamp']}")
    return data


def file_size_processor(data: List[Dict]) -> List[Dict]:
    """Process file sizes into human-readable format"""
    if not isinstance(data, list):
        return data

    def format_size(size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"

    for item in data:
        if isinstance(item, dict) and 'size' in item:
            if isinstance(item['size'], (int, float)):
                item['size_formatted'] = format_size(item['size'])
    return data