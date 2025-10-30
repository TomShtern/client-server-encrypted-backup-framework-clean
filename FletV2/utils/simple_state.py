"""
Simple State Management - Flet Native Approach

Replaces 1,036-line StateManager with Flet-idiomatic patterns.
Follows Flet Simplicity Principle: use built-in features over custom solutions.

Core patterns:
- Simple dictionaries for state storage
- control.update() for reactive updates
- page.run_task() for async operations
- Direct method calls instead of callback systems
"""

import asyncio
import time
from collections.abc import Callable
from typing import Any, Dict, Optional

import flet as ft


class SimpleState:
    """
    Flet-native state management using simple patterns.

    Replaces complex StateManager with idiomatic Flet approach:
    - Dictionary-based state storage
    - Direct control updates
    - Simple async helpers
    """

    def __init__(self, page: ft.Page, server_bridge=None):
        self.page = page
        self.server_bridge = server_bridge

        # Simple state dictionary (replaces complex state.manager.state)
        self.state: Dict[str, Any] = {
            "clients": [],
            "files": [],
            "server_status": {},
            "database_info": {},
            "system_status": {},
            "connection_status": "disconnected",
            "current_view": "dashboard",
            "last_activity": [],
            "notifications": [],
            "loading_states": {},
            "logs_data": [],
            "logs_filters": {"level": "ALL", "component": "ALL", "search": ""},
            "logs_statistics": {},
            "settings_data": {},
            "settings_validation": {},
            "settings_backups": [],
            "error_states": {},
        }

        # Control registry for targeted updates (replaces complex callback system)
        self.controls: Dict[str, ft.Control] = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get state value - simple dictionary access"""
        return self.state.get(key, default)

    def update(self, key: str, value: Any, update_control: str | None = None, source: str = "manual"):
        """
        Update state and optionally refresh specific control.

        Replaces complex callback/notification system with simple targeted updates.
        """
        self.state[key] = value

        # Flet-native: update specific control if provided
        if update_control and update_control in self.controls:
            try:
                self.controls[update_control].update()
            except Exception as e:
                print(f"Control update failed: {e}")

    def register_control(self, name: str, control: ft.Control):
        """Register control for targeted updates (replaces callback system)"""
        self.controls[name] = control

    def subscribe(self, key: str, callback: Callable[[Any, Any], None], control: ft.Control | None = None):
        """
        Subscribe to state changes (simplified for compatibility).

        In the SimpleState approach, we just call the callback immediately
        and rely on direct state.update() calls for changes.
        """
        # Call immediately with current value
        current_value = self.get(key)
        try:
            callback(current_value, None)
        except Exception as e:
            print(f"Callback subscription failed: {e}")

    def unsubscribe(self, key: str, callback: Callable[[Any, Any], None]):
        """
        Unsubscribe from state changes (no-op in SimpleState).

        SimpleState doesn't maintain complex callback subscriptions.
        """
        pass  # No-op for SimpleState approach

    def set_loading(self, operation: str, is_loading: bool):
        """Set loading state for operation"""
        loading_states = self.get("loading_states", {})
        loading_states[operation] = is_loading
        self.update("loading_states", loading_states)

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
        self.update("notifications", notifications)

        # Auto-dismiss using Flet's native run_task
        if auto_dismiss > 0:
            self.page.run_task(self._dismiss_notification_after, notification['id'], auto_dismiss)

    async def _dismiss_notification_after(self, notification_id: str, delay: int):
        """Auto-dismiss notification after delay"""
        await asyncio.sleep(delay)
        notifications = self.get("notifications", [])
        notifications = [n for n in notifications if n['id'] != notification_id]
        self.update("notifications", notifications)

    # Simple server integration (replaces complex server_mediated_update)
    async def fetch_data(self, operation: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Fetch data using server bridge with simple pattern.

        Replaces complex server_mediated_update with direct calls.
        """
        if not self.server_bridge:
            return {'success': False, 'error': 'No server bridge', 'data': []}

        try:
            # Get the method from server bridge
            method = getattr(self.server_bridge, operation, None)
            if not method:
                return {'success': False, 'error': f'Method {operation} not found'}

            # Call sync method in executor (non-blocking)
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, method, *args, **kwargs)

            # Handle result format
            if isinstance(result, dict) and 'success' in result:
                return result
            else:
                return {'success': True, 'data': result}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # Simple logs management (replaces complex async system)
    async def load_logs(self, filters: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Load logs data using simple pattern"""
        filters = filters or self.get("logs_filters", {"level": "ALL", "component": "ALL", "search": ""})

        result = await self.fetch_data("get_logs", 1000, 0, filters)
        if result.get('success'):
            self.update("logs_data", result.get('data', []))
            self.update("logs_filters", filters)

        return result

    def filter_logs(self, filters: Dict[str, Any]):
        """Apply filters to logs data (simple synchronous)"""
        logs_data = self.get("logs_data", [])

        if not filters.get("level") or filters["level"] == "ALL":
            filtered = logs_data
        else:
            filtered = [log for log in logs_data if log.get("level") == filters["level"]]

        if filters.get("component") and filters["component"] != "ALL":
            filtered = [log for log in filtered if log.get("component") == filters["component"]]

        if filters.get("search"):
            search_term = filters["search"].lower()
            filtered = [log for log in filtered if
                       search_term in (log.get("message") or "").lower() or
                       search_term in (log.get("component") or "").lower()]

        self.update("logs_filtered", filtered)
        self.update("logs_filters", filters)

    # Simple settings management (replaces complex versioning system)
    async def load_settings(self) -> Dict[str, Any]:
        """Load settings data using simple pattern"""
        result = await self.fetch_data("load_settings")
        if result.get('success'):
            self.update("settings_data", result.get('data', {}))
        return result

    async def save_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save settings data using simple pattern"""
        result = await self.fetch_data("save_settings", settings_data)
        if result.get('success'):
            self.update("settings_data", settings_data)
        return result

    # Simple progress tracking (replaces complex system)
    def set_progress(self, operation: str, progress: float, message: str = ""):
        """Set progress for operation"""
        progress_states = self.get("progress_states", {})
        progress_states[operation] = {
            "progress": max(0, min(100, progress)),
            "message": message,
            "timestamp": time.time()
        }
        self.update("progress_states", progress_states)

    def clear_progress(self, operation: str):
        """Clear progress for operation"""
        progress_states = self.get("progress_states", {})
        if operation in progress_states:
            del progress_states[operation]
            self.update("progress_states", progress_states)


# Factory function for easy creation
def create_simple_state(page: ft.Page, server_bridge=None) -> SimpleState:
    """Create simple state manager with Flet-native patterns"""
    state = SimpleState(page, server_bridge)

    # Initialize with empty state values
    initial_state = {
        "clients": [],
        "files": [],
        "logs_data": [],
        "logs_filtered": [],
        "logs_statistics": {},
        "settings_data": {},
        "settings_validation": {},
        "settings_backups": [],
        "notifications": [],
        "loading_states": {},
        "error_states": {},
        "progress_states": {},
        "current_view": "dashboard",
        "connection_status": "disconnected"
    }

    for key, value in initial_state.items():
        if key not in state.state:
            state.state[key] = value

    return state