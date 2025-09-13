#!/usr/bin/env python3
"""
Enhanced State Manager for FletV2
Framework-harmonious state management with reactive patterns and async support.

Enhanced for server integration with:
- Async state operations for server-mediated updates
- Reactive cross-view updates with automatic control refresh
- Server bridge integration for state persistence
- Batch operations for efficient UI updates
- Event-driven architecture for real-time responsiveness
"""

import flet as ft
import asyncio
import time
from typing import Dict, Any, Callable, Optional, List, Union
from utils.debug_setup import get_logger

logger = get_logger(__name__)


class StateManager:
    """Enhanced state management with async support and reactive patterns"""
    
    def __init__(self, page: ft.Page, server_bridge=None):
        self.page = page
        self.server_bridge = server_bridge
        self.state = {
            "clients": [],
            "files": [],
            "server_status": {},
            "database_info": {},
            "system_status": {},
            "connection_status": "disconnected",
            "current_view": "dashboard",
            "last_activity": [],
            "notifications": [],
            "loading_states": {}  # Track loading states per operation
        }
        self.callbacks = {}  # {state_key: [callbacks]}
        self.async_callbacks = {}  # {state_key: [async_callbacks]}
        self.global_listeners = []  # Listeners for all state changes
        self._change_history = []  # Track state changes for debugging
        logger.info("Enhanced StateManager initialized with server bridge support")
    
    def update(self, key: str, value: Any, source: str = "manual"):
        """Update state and notify callbacks - Framework harmonious"""
        if self.state.get(key) == value:
            return  # No change needed
        
        old_value = self.state.get(key)
        self.state[key] = value
        
        # Track change for debugging
        change_record = {
            'key': key,
            'old_value': old_value,
            'new_value': value,
            'source': source,
            'timestamp': time.time()
        }
        self._change_history.append(change_record)
        
        # Keep only last 100 changes
        if len(self._change_history) > 100:
            self._change_history = self._change_history[-100:]
        
        logger.debug(f"State updated: {key} = {value} (source: {source})")
        
        # Notify sync callbacks for this key
        if key in self.callbacks:
            for callback in self.callbacks[key]:
                try:
                    callback(value, old_value)
                except Exception as e:
                    logger.error(f"Sync callback failed for {key}: {e}")
        
        # Notify global listeners
        for listener in self.global_listeners:
            try:
                listener(key, value, old_value)
            except Exception as e:
                logger.error(f"Global listener failed: {e}")
        
        # Schedule async callbacks
        if key in self.async_callbacks:
            for async_callback in self.async_callbacks[key]:
                try:
                    if self.page and hasattr(self.page, 'run_task'):
                        self.page.run_task(async_callback, value, old_value)
                    else:
                        # Fallback for environments without run_task
                        asyncio.create_task(async_callback(value, old_value))
                except Exception as e:
                    logger.error(f"Async callback scheduling failed for {key}: {e}")

    async def update_async(self, key: str, value: Any, source: str = "async"):
        """Async version of update with enhanced control refreshing"""
        if self.state.get(key) == value:
            return  # No change needed
        
        old_value = self.state.get(key)
        self.state[key] = value
        
        # Track change
        change_record = {
            'key': key,
            'old_value': old_value,
            'new_value': value,
            'source': source,
            'timestamp': time.time()
        }
        self._change_history.append(change_record)
        
        if len(self._change_history) > 100:
            self._change_history = self._change_history[-100:]
        
        logger.debug(f"State updated async: {key} = {value} (source: {source})")
        
        # Notify async callbacks first
        if key in self.async_callbacks:
            for async_callback in self.async_callbacks[key]:
                try:
                    await async_callback(value, old_value)
                except Exception as e:
                    logger.error(f"Async callback failed for {key}: {e}")
        
        # Notify sync callbacks
        if key in self.callbacks:
            for callback in self.callbacks[key]:
                try:
                    callback(value, old_value)
                except Exception as e:
                    logger.error(f"Sync callback failed for {key}: {e}")
        
        # Notify global listeners
        for listener in self.global_listeners:
            try:
                listener(key, value, old_value)
            except Exception as e:
                logger.error(f"Global listener failed: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get current state value"""
        return self.state.get(key, default)
    
    def subscribe(self, key: str, callback: Callable, control: Optional[ft.Control] = None):
        """Subscribe to state changes with optional automatic control updates"""
        if key not in self.callbacks:
            self.callbacks[key] = []
        
        # Wrap callback to include control.update() if provided
        if control:
            original_callback = callback
            def auto_update_callback(new_value, old_value):
                original_callback(new_value, old_value)
                if hasattr(control, 'update'):
                    control.update()  # Flet-native: control.update() not page.update()
            self.callbacks[key].append(auto_update_callback)
        else:
            self.callbacks[key].append(callback)
        
        # Call immediately with current value
        if key in self.state:
            callback(self.state[key], None)
        
        logger.debug(f"Subscribed to state key: {key}")

    def subscribe_async(self, key: str, async_callback: Callable, control: Optional[ft.Control] = None):
        """Subscribe to state changes with async callback"""
        if key not in self.async_callbacks:
            self.async_callbacks[key] = []
        
        # Wrap async callback to include control.update() if provided
        if control:
            original_callback = async_callback
            async def auto_update_async_callback(new_value, old_value):
                await original_callback(new_value, old_value)
                if hasattr(control, 'update'):
                    control.update()
            self.async_callbacks[key].append(auto_update_async_callback)
        else:
            self.async_callbacks[key].append(async_callback)
        
        # Call immediately with current value (async)
        if key in self.state:
            if self.page and hasattr(self.page, 'run_task'):
                self.page.run_task(async_callback, self.state[key], None)
            else:
                asyncio.create_task(async_callback(self.state[key], None))
        
        logger.debug(f"Subscribed async to state key: {key}")

    def subscribe_global(self, listener: Callable):
        """Subscribe to all state changes"""
        self.global_listeners.append(listener)
        logger.debug("Added global state listener")

    def unsubscribe(self, key: str, callback: Callable):
        """Unsubscribe from state changes"""
        if key in self.callbacks and callback in self.callbacks[key]:
            self.callbacks[key].remove(callback)
            logger.debug(f"Unsubscribed from state key: {key}")

    def unsubscribe_async(self, key: str, async_callback: Callable):
        """Unsubscribe from async state changes"""
        if key in self.async_callbacks and async_callback in self.async_callbacks[key]:
            self.async_callbacks[key].remove(async_callback)
            logger.debug(f"Unsubscribed async from state key: {key}")
    
    def batch_update(self, updates: Dict[str, Any], source: str = "batch"):
        """Update multiple state values efficiently"""
        logger.debug(f"Batch updating {len(updates)} state keys")
        for key, value in updates.items():
            self.update(key, value, source=source)

    async def batch_update_async(self, updates: Dict[str, Any], source: str = "batch_async"):
        """Async batch update for server-mediated operations"""
        logger.debug(f"Batch updating async {len(updates)} state keys")
        for key, value in updates.items():
            await self.update_async(key, value, source=source)

    def set_loading(self, operation: str, is_loading: bool):
        """Track loading states for operations"""
        loading_states = self.get("loading_states", {})
        loading_states[operation] = is_loading
        self.update("loading_states", loading_states, source="loading")

    def is_loading(self, operation: str) -> bool:
        """Check if an operation is currently loading"""
        loading_states = self.get("loading_states", {})
        return loading_states.get(operation, False)

    async def server_mediated_update(self, key: str, value: Any, server_operation: str | None = None, *args, **kwargs):
        """Update state through server bridge for persistence"""
        if self.server_bridge and server_operation:
            try:
                # Call server operation if specified
                server_method = getattr(self.server_bridge, server_operation, None)
                if server_method:
                    logger.debug(f"Calling server method: {server_operation}")
                    # Pass the arguments to the server method
                    if asyncio.iscoroutinefunction(server_method):
                        result = await server_method(*args, **kwargs)
                    else:
                        result = server_method(*args, **kwargs)

                    # Normalize non-dict results into dicts
                    if not isinstance(result, dict):
                        result = {'success': bool(result), 'data': result}

                    # Update state with server result if successful
                    if result.get('success'):
                        await self.update_async(key, result.get('data', value), source=f"server_{server_operation}")
                        return result
                    else:
                        # Fallback to direct state update
                        await self.update_async(key, value, source="server_fallback")
                        return {'success': True, 'mode': 'fallback'}
                else:
                    logger.warning(f"Server method {server_operation} not found")
                    await self.update_async(key, value, source="server_fallback")
                    return {'success': False, 'error': f'method {server_operation} not found', 'mode': 'fallback'}
            except Exception as e:
                logger.error(f"Server operation {server_operation} failed: {e}")
                await self.update_async(key, value, source="server_error")
                return {'success': False, 'error': str(e)}
        else:
            # Direct state update when no server bridge available
            await self.update_async(key, value, source="direct")
            return {'success': True, 'mode': 'direct'}

    def add_notification(self, message: str, notification_type: str = "info", auto_dismiss: int = 5):
        """Add notification to state"""
        notifications = self.get("notifications", [])
        notification = {
            'id': f"notif_{int(time.time() * 1000)}",
            'message': message,
            'type': notification_type,
            'timestamp': time.time(),
            'auto_dismiss': auto_dismiss
        }
        notifications.append(notification)
        self.update("notifications", notifications, source="notification")
        
        # Auto-dismiss if specified
        if auto_dismiss > 0 and self.page and hasattr(self.page, 'run_task'):
            self.page.run_task(self._dismiss_notification_after, notification['id'], auto_dismiss)

    async def _dismiss_notification_after(self, notification_id: str, delay: int):
        """Auto-dismiss notification after delay"""
        await asyncio.sleep(delay)
        self.dismiss_notification(notification_id)

    def dismiss_notification(self, notification_id: str):
        """Remove notification from state"""
        notifications = self.get("notifications", [])
        notifications = [n for n in notifications if n['id'] != notification_id]
        self.update("notifications", notifications, source="notification_dismiss")

    def get_change_history(self, limit: int = 10) -> List[Dict]:
        """Get recent state changes for debugging"""
        return self._change_history[-limit:]

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current state for debugging"""
        return {
            'state_keys': list(self.state.keys()),
            'callback_counts': {key: len(callbacks) for key, callbacks in self.callbacks.items()},
            'async_callback_counts': {key: len(callbacks) for key, callbacks in self.async_callbacks.items()},
            'global_listeners': len(self.global_listeners),
            'recent_changes': len(self._change_history),
            'has_server_bridge': self.server_bridge is not None
        }


# Factory function for backwards compatibility and easy creation
def create_state_manager(page: ft.Page, server_bridge=None) -> StateManager:
    """Create enhanced state manager with optional server bridge"""
    return StateManager(page, server_bridge)