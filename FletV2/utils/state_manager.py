#!/usr/bin/env python3
"""
Enhanced State Manager for FletV2
Framework-h        # Track change for debugging
        change_record = {
            'key': key,
            'old_value': old_value,
            'new_value': value,
            'source': source,
            'timestamp': time.time()
        }
        self._change_history.append(change_record)

        # Trim history to last 100 changes
        if len(self._change_history) > 100:
            self._change_history = self._change_history[-100:]

        # Update deduplication tracking (Comment 10: Fix duplicate event notifications)
        self._last_update_source[key] = source
        self._update_counter[key] = self._update_counter.get(key, 0) + 1
        current_count = self._update_counter[key]

        logger.debug(f"State updated: {key} = {value} (source: {source}, count: {current_count})") management with reactive patterns and async support.

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
            "loading_states": {},  # Track loading states per operation
            "logs_data": [],
            "logs_filters": {"level": "ALL", "component": "ALL", "search": ""},
            "logs_statistics": {},
            "settings_data": {},
            "settings_validation": {},
            "settings_backups": [],
            "error_states": {},
            "logs_events": {},
            "settings_events": {},
            "progress_states": {},
            "retry_states": {},
        }
        self.callbacks = {}  # {state_key: [callbacks]}
        self.async_callbacks = {}  # {state_key: [async_callbacks]}
        self.global_listeners = []  # Listeners for all state changes
        self._change_history = []  # Track state changes for debugging
        # Debounce tasks for frequently changing operations (not persisted in state)
        self._debounce_tasks: Dict[str, asyncio.Task] = {}
        # Event deduplication tracking (Comment 10: Fix duplicate event notifications)
        self._last_update_source: Dict[str, str] = {}  # {state_key: last_source}
        self._update_counter: Dict[str, int] = {}  # {state_key: update_count}
        # Lock & versioning for settings conflict resolution
        self._settings_lock = asyncio.Lock()
        self._settings_version = 0
        # Track pending progress operations (mirrors state['progress_states'])
        self._progress_internal: Dict[str, Dict[str, Any]] = {}
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
            for callback in list(self.callbacks[key]):
                try:
                    # Check deduplication rules (Comment 10: Fix duplicate event notifications)
                    if self._should_notify_callback(key, callback, source):
                        callback(value, old_value)
                    else:
                        logger.debug(f"Skipped sync callback for {key} due to deduplication")
                except Exception as e:
                    logger.error(f"Sync callback failed for {key}: {e}")

        # Notify global listeners
        for listener in list(self.global_listeners):
            try:
                listener(key, value, old_value)
            except Exception as e:
                logger.error(f"Global listener failed: {e}")

        # Schedule async callbacks
        if key in self.async_callbacks:
            for async_callback in list(self.async_callbacks[key]):
                try:
                    # Check deduplication rules (Comment 10: Fix duplicate event notifications)
                    if self._should_notify_callback(key, async_callback, source):
                        if self.page and hasattr(self.page, 'run_task'):
                            # Flet's run_task accepts a callable and its args
                            self.page.run_task(async_callback, value, old_value)
                        else:
                            # Fallback for environments without run_task
                            asyncio.create_task(async_callback(value, old_value))
                    else:
                        logger.debug(f"Skipped async callback for {key} due to deduplication")
                except Exception as e:
                    logger.error(f"Async callback scheduling failed for {key}: {e}")

    def _should_notify_callback(self, key: str, callback: Any, source: str) -> bool:
        """Check if callback should be notified based on deduplication rules (Comment 10)"""
        # For now, use simple heuristic: if callback has a __name__ or __qualname__ attribute
        # indicating it comes from a view, check if it's the same source triggering again
        try:
            callback_name = getattr(callback, '__name__', '') or getattr(callback, '__qualname__', '')
            if callback_name and source != "manual" and (source.lower() in callback_name.lower() or callback_name.lower() in source.lower()):
                logger.debug(f"Skipping callback {callback_name} for {key} (source: {source}) - preventing re-entry")
                return False
        except Exception:
            pass  # Fall through to normal notification
        return True

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

        # Update deduplication tracking (Comment 10: Fix duplicate event notifications)
        self._last_update_source[key] = source
        self._update_counter[key] = self._update_counter.get(key, 0) + 1
        current_count = self._update_counter[key]

        logger.debug(f"State updated async: {key} = {value} (source: {source}, count: {current_count})")

        # Notify async callbacks first
        if key in self.async_callbacks:
            for async_callback in list(self.async_callbacks[key]):
                try:
                    # Check deduplication rules (Comment 10: Fix duplicate event notifications)
                    if self._should_notify_callback(key, async_callback, source):
                        await async_callback(value, old_value)
                    else:
                        logger.debug(f"Skipped async callback for {key} due to deduplication (async)")
                except Exception as e:
                    logger.error(f"Async callback failed for {key}: {e}")

        # Notify sync callbacks
        if key in self.callbacks:
            for callback in list(self.callbacks[key]):
                try:
                    # Check deduplication rules (Comment 10: Fix duplicate event notifications)
                    if self._should_notify_callback(key, callback, source):
                        callback(value, old_value)
                    else:
                        logger.debug(f"Skipped sync callback for {key} due to deduplication (async)")
                except Exception as e:
                    logger.error(f"Sync callback failed for {key}: {e}")

        # Notify global listeners
        for listener in list(self.global_listeners):
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
                # Safe control update with page attachment check
                if hasattr(control, 'update') and hasattr(control, 'page') and control.page is not None:
                    try:
                        control.update()  # Flet-native: control.update() not page.update()
                    except Exception as e:
                        logger.debug(f"Control update failed for {key}: {e}")
            self.callbacks[key].append(auto_update_callback)
        else:
            self.callbacks[key].append(callback)

        # Call immediately with current value
        if key in self.state:
            try:
                callback(self.state[key], None)
            except Exception as e:
                logger.debug(f"Immediate callback invocation failed for {key}: {e}")

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
                # Safe control update with page attachment check
                if hasattr(control, 'update') and hasattr(control, 'page') and control.page is not None:
                    try:
                        control.update()
                    except Exception as e:
                        logger.debug(f"Async control update failed for {key}: {e}")
            self.async_callbacks[key].append(auto_update_async_callback)
        else:
            self.async_callbacks[key].append(async_callback)

        # Call immediately with current value (async)
        if key in self.state:
            try:
                if self.page and hasattr(self.page, 'run_task'):
                    self.page.run_task(async_callback, self.state[key], None)
                else:
                    asyncio.create_task(async_callback(self.state[key], None))
            except Exception as e:
                logger.debug(f"Immediate async callback scheduling failed for {key}: {e}")

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

                    # Handle different result formats from server bridge
                    if isinstance(result, dict):
                        # If result already has success field, use as-is
                        if 'success' in result:
                            if result.get('success'):
                                await self.update_async(key, result.get('data', value), source=f"server_{server_operation}")
                                return result
                            else:
                                # Fallback to direct state update
                                await self.update_async(key, value, source="server_fallback")
                                return {'success': True, 'mode': 'fallback'}
                        else:
                            # Raw dict result without success field - treat as successful data
                            await self.update_async(key, result, source=f"server_{server_operation}")
                            return {'success': True, 'data': result, 'mode': 'server'}
                    else:
                        # Non-dict result - wrap it
                        result_dict = {'success': bool(result), 'data': result}
                        if result_dict.get('success'):
                            await self.update_async(key, result_dict.get('data', value), source=f"server_{server_operation}")
                            return result_dict
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
            'has_server_bridge': self.server_bridge is not None,
            'logs_count': len(self.state.get('logs_data', [])),
            'settings_sections': list(self.state.get('settings_data', {}).keys()),
            'active_loading_operations': [k for k, v in self.state.get('loading_states', {}).items() if v]
        }

    # --- Enhanced Logs-Specific State Management ---

    def subscribe_to_logs(self, callback: Callable, control: Optional[ft.Control] = None):
        """Subscribe specifically to logs data changes with automatic UI updates"""
        self.subscribe("logs_data", callback, control)
        # Also subscribe to related logs state
        # When filters change, call user's callback with current filtered data snapshot
        def filter_proxy(filters, _):
            try:
                callback(self.get("logs_filtered", self.get("logs_data", [])), None)
            except Exception as e:
                logger.debug(f"Filter proxy callback failed: {e}")
        self.subscribe("logs_filters", filter_proxy, control)
        logger.debug("Subscribed to logs with automatic filtering")

    def subscribe_to_logs_async(self, async_callback: Callable, control: Optional[ft.Control] = None):
        """Subscribe to logs data changes with async callback"""
        self.subscribe_async("logs_data", async_callback, control)
        # Also subscribe to related logs state
        async def async_filter_callback(filters, _):
            await async_callback(self.get("logs_filtered", self.get("logs_data", [])), None)
        self.subscribe_async("logs_filters", async_filter_callback, control)
        logger.debug("Subscribed to logs async with automatic filtering")

    async def update_logs_async(self, logs_data: List[Dict[str, Any]], source: str = "server"):
        """Update logs data with intelligent caching and filtering"""
        try:
            # Update main logs data
            await self.update_async("logs_data", logs_data, source=f"logs_{source}")

            # Update logs statistics if server bridge available
            if self.server_bridge and hasattr(self.server_bridge, 'get_log_statistics_async'):
                try:
                    stats = await self.server_bridge.get_log_statistics_async()
                    await self.update_async("logs_statistics", stats, source="server_stats")
                except Exception as e:
                    logger.warning(f"Failed to update logs statistics: {e}")

            # Re-apply current filters (debounced)
            current_filters = self.get("logs_filters", {"level": "ALL", "component": "ALL", "search": ""})
            # schedule filter apply - quick debounce to avoid thrash
            self._debounce_call("filter_logs", lambda: self._apply_logs_filter(current_filters), delay=0.05)

            logger.debug(f"Updated logs data: {len(logs_data)} entries from {source}")
        except Exception as e:
            logger.error(f"Failed to update logs data: {e}")

    async def clear_logs_state(self):
        """Clear logs state and notify subscribers"""
        try:
            # If server_bridge supports clearing logs on server, prefer that
            if self.server_bridge and hasattr(self.server_bridge, 'clear_logs_async'):
                try:
                    self.set_loading("clear_logs", True)
                    result = await self.server_bridge.clear_logs_async()
                    # If server responded with success and returned data, reflect that
                    if isinstance(result, dict) and result.get('success', True):
                        await self.update_async("logs_data", [], source="server_clear")
                        await self.update_async("logs_statistics", {}, source="server_clear")
                        self.add_notification("Logs cleared on server", "success")
                    else:
                        # Fallback local clear
                        await self.update_async("logs_data", [], source="clear")
                        await self.update_async("logs_statistics", {}, source="clear")
                        self.add_notification("Logs cleared (local fallback)", "warning")
                except Exception as e:
                    logger.warning(f"Server clear logs failed, performing local clear: {e}")
                    await self.update_async("logs_data", [], source="clear")
                    await self.update_async("logs_statistics", {}, source="clear")
                    self.add_notification("Logs cleared (local)", "success")
                finally:
                    self.set_loading("clear_logs", False)
            else:
                await self.update_async("logs_data", [], source="clear")
                await self.update_async("logs_statistics", {}, source="clear")
                self.add_notification("Logs cleared successfully", "success")
            logger.debug("Logs state cleared")
        except Exception as e:
            logger.error(f"Failed to clear logs state: {e}")

    def filter_logs_state(self, filters: Dict[str, Any]):
        """Apply filters to logs and update state reactively (debounced)"""
        try:
            # Update filter state immediately (so UI shows current selected filters)
            self.update("logs_filters", filters, source="user_filter")
            # Debounce the expensive filter operation
            self._debounce_call("filter_logs", lambda: self._apply_logs_filter(filters), delay=0.18)
            logger.debug(f"Scheduled logs filter application (debounced): {filters}")
        except Exception as e:
            logger.error(f"Failed to filter logs state: {e}")

    async def _apply_logs_filter(self, filters: Dict[str, Any]):
        """Internal helper to apply log filters and update logs_filtered state"""
        try:
            # Get current logs
            logs_data = self.get("logs_data", [])
            filtered_logs = logs_data.copy()

            if filters.get("level") and filters["level"] != "ALL":
                filtered_logs = [log for log in filtered_logs if log.get("level") == filters["level"]]

            if filters.get("component") and filters["component"] != "ALL":
                filtered_logs = [log for log in filtered_logs if log.get("component") == filters["component"]]

            if filters.get("search"):
                search_term = filters["search"].lower()
                filtered_logs = [log for log in filtered_logs if
                               search_term in (log.get("message") or "").lower() or
                               search_term in (log.get("component") or "").lower()]

            # Update filtered logs (separate state key for performance)
            await self.update_async("logs_filtered", filtered_logs, source="filter_applied")
            logger.debug(f"Applied logs filters: {filters}, result: {len(filtered_logs)} entries")
        except Exception as e:
            logger.error(f"Failed to apply logs filter: {e}")

    async def export_logs_state(self, format: str, filters: Optional[Dict[str, Any]] = None):
        """Export logs through server bridge with state tracking"""
        try:
            self.set_loading("logs_export", True)

            if self.server_bridge:
                result = await self.server_mediated_update(
                    "logs_export_result",
                    {"format": format, "filters": filters},
                    "export_logs_async",
                    format,
                    filters or {}
                )

                if result.get('success'):
                    self.add_notification(f"Logs exported as {format.upper()} ({result.get('mode', 'server')})", "success")
                    return result
                else:
                    self.add_notification(f"Export failed: {result.get('error', 'Unknown error')}", "error")
                    # set retry state for export
                    retry_info = self.get("retry_states", {})
                    retry_info["logs_export"] = retry_info.get("logs_export", {"attempts": 0, "last_error": None})
                    retry_info["logs_export"]["last_error"] = result.get("error")
                    self.update("retry_states", retry_info, source="set_retry")
                    return result
            else:
                self.add_notification("No server bridge available for export", "warning")
                return {'success': False, 'error': 'No server bridge'}
        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
            self.add_notification(f"Export error: {str(e)}", "error")
            retry_info = self.get("retry_states", {})
            retry_info["logs_export"] = retry_info.get("logs_export", {"attempts": 0, "last_error": None})
            retry_info["logs_export"]["last_error"] = str(e)
            self.update("retry_states", retry_info, source="set_retry")
            return {'success': False, 'error': str(e)}
        finally:
            self.set_loading("logs_export", False)

    # --- Enhanced Settings-Specific State Management ---

    def subscribe_to_settings(self, callback: Callable, control: Optional[ft.Control] = None):
        """Subscribe specifically to settings data changes with automatic UI updates"""
        self.subscribe("settings_data", callback, control)
        logger.debug("Subscribed to settings with automatic UI updates")

    def subscribe_to_settings_async(self, async_callback: Callable, control: Optional[ft.Control] = None):
        """Subscribe to settings data changes with async callback"""
        self.subscribe_async("settings_data", async_callback, control)
        logger.debug("Subscribed to settings async with automatic UI updates")

    async def update_settings_async(self, settings_data: Dict[str, Any], source: str = "server"):
        """Update settings data with validation and server integration"""
        try:
            # Basic optimistic versioning for conflict resolution
            incoming_version = settings_data.get("_version", None)
            async with self._settings_lock:
                current_settings = self.get("settings_data", {}) or {}
                self._settings_version += 1
                current_version = self._settings_version

                # If incoming version present and older than current, attempt merge
                if incoming_version is not None and incoming_version < current_version:
                    # Conflict detected: merge shallowly and notify
                    merged = self._deep_merge_dicts(current_settings, settings_data)
                    await self.update_async("settings_data", merged, source=f"merge_{source}")
                    self.add_notification("Concurrent settings update merged", "warning")
                    logger.warning("Settings conflict detected and merged")
                    # Broadcast settings event
                    self.broadcast_settings_event("settings_conflict_merged", {"version": current_version})
                    return {'success': True, 'merged': True, 'version': current_version}

                # Validate settings if server bridge available
                if self.server_bridge and hasattr(self.server_bridge, 'validate_settings_async'):
                    try:
                        validation_result = await self.server_bridge.validate_settings_async(settings_data)
                        await self.update_async("settings_validation", validation_result, source="server_validation")

                        if not validation_result.get('data', {}).get('valid', True):
                            errors = validation_result.get('data', {}).get('errors', [])
                            self.add_notification(f"Settings validation failed: {'; '.join(errors)}", "error")
                            # Record error state
                            self.set_error_state("settings_validation", "Validation failed", {"errors": errors})
                            return {'success': False, 'errors': errors}
                    except Exception as e:
                        logger.warning(f"Settings validation failed: {e}")

                # Update main settings data
                await self.update_async("settings_data", settings_data, source=f"settings_{source}")

                # Broadcast settings change to all views (granular updates)
                for section, section_data in (settings_data.items() if isinstance(settings_data, dict) else []):
                    if isinstance(section_data, dict):
                        for key, value in section_data.items():
                            await self.update_async(f"settings.{section}.{key}", value, source=f"settings_update_{section}")
                    else:
                        await self.update_async(f"settings.{section}", section_data, source=f"settings_update_{section}")

                # Update version metadata
                await self.update_async("settings_version", current_version, source="version_update")

                # Broadcast event for settings update
                self.broadcast_settings_event("settings_updated", {"version": current_version, "source": source})
                logger.debug(f"Updated settings data from {source}")
                return {'success': True, 'version': current_version}
        except Exception as e:
            logger.error(f"Failed to update settings data: {e}")
            self.set_error_state("settings_update", str(e))
            return {'success': False, 'error': str(e)}

    async def validate_settings_state(self, settings_data: Dict[str, Any]):
        """Validate settings and update validation state"""
        try:
            if self.server_bridge and hasattr(self.server_bridge, 'validate_settings_async'):
                result = await self.server_bridge.validate_settings_async(settings_data)
                await self.update_async("settings_validation", result, source="validation")
                return result
            else:
                # Local validation fallback
                validation_result = {
                    'valid': True,
                    'errors': [],
                    'warnings': []
                }
                await self.update_async("settings_validation", {'data': validation_result}, source="local_validation")
                return {'success': True, 'data': validation_result}
        except Exception as e:
            logger.error(f"Settings validation failed: {e}")
            self.set_error_state("settings_validation", str(e))
            return {'success': False, 'error': str(e)}

    async def backup_settings_state(self, backup_name: str):
        """Create settings backup and update backup list"""
        try:
            self.set_loading("settings_backup", True)

            settings_data = self.get("settings_data", {})
            if not settings_data:
                self.add_notification("No settings to backup", "warning")
                return {'success': False, 'error': 'No settings data'}

            if self.server_bridge:
                result = await self.server_mediated_update(
                    "settings_backup_result",
                    {"name": backup_name, "data": settings_data},
                    "backup_settings_async",
                    backup_name,
                    settings_data
                )

                if result.get('success'):
                    # Update backup list
                    backups = self.get("settings_backups", [])
                    backups.append({
                        'name': backup_name,
                        'created_at': time.time(),
                        'mode': result.get('mode', 'server')
                    })
                    await self.update_async("settings_backups", backups, source="backup_created")

                    self.add_notification(f"Settings backup '{backup_name}' created ({result.get('mode', 'server')})", "success")
                    # Broadcast event
                    self.broadcast_settings_event("settings_backup_created", {"name": backup_name})
                    return result
                else:
                    self.add_notification(f"Backup failed: {result.get('error', 'Unknown error')}", "error")
                    self.set_error_state("settings_backup", result.get('error', 'Unknown'))
                    return result
            else:
                self.add_notification("No server bridge available for backup", "warning")
                return {'success': False, 'error': 'No server bridge'}
        except Exception as e:
            logger.error(f"Failed to backup settings: {e}")
            self.add_notification(f"Backup error: {str(e)}", "error")
            self.set_error_state("settings_backup", str(e))
            return {'success': False, 'error': str(e)}
        finally:
            self.set_loading("settings_backup", False)

    async def restore_settings_state(self, backup_file: str, settings_data: Optional[Dict[str, Any]] = None):
        """Restore settings from backup"""
        try:
            self.set_loading("settings_restore", True)

            if self.server_bridge:
                result = await self.server_mediated_update(
                    "settings_restore_result",
                    {"file": backup_file, "data": settings_data},
                    "restore_settings_async",
                    backup_file,
                    settings_data
                )

                if result.get('success'):
                    restored_settings = result.get('data', {}).get('restored_settings', settings_data)
                    if restored_settings:
                        await self.update_settings_async(restored_settings, "restore")
                        self.add_notification(f"Settings restored from backup ({result.get('mode', 'server')})", "success")
                        self.broadcast_settings_event("settings_restored", {"file": backup_file})
                    return result
                else:
                    self.add_notification(f"Restore failed: {result.get('error', 'Unknown error')}", "error")
                    self.set_error_state("settings_restore", result.get('error', 'Unknown'))
                    return result
            else:
                # Local restore fallback
                if settings_data:
                    await self.update_settings_async(settings_data, "local_restore")
                    self.add_notification("Settings restored (local)", "success")
                    self.broadcast_settings_event("settings_restored", {"mode": "local"})
                    return {'success': True, 'mode': 'local'}
                else:
                    self.add_notification("No settings data to restore", "warning")
                    return {'success': False, 'error': 'No settings data'}
        except Exception as e:
            logger.error(f"Failed to restore settings: {e}")
            self.add_notification(f"Restore error: {str(e)}", "error")
            self.set_error_state("settings_restore", str(e))
            return {'success': False, 'error': str(e)}
        finally:
            self.set_loading("settings_restore", False)

    # --- Enhanced Cross-View Synchronization ---

    def broadcast_logs_event(self, event_type: str, event_data: Dict[str, Any]):
        """Broadcast logs-related events to all subscribers"""
        event = {
            'type': event_type,
            'data': event_data,
            'timestamp': time.time()
        }
        # Store as last event for subscribers and also update an events history list
        self.update("logs_events", event, source="broadcast")
        # Append history in state for potential UI consumption
        history = self.get("logs_events_history", [])
        history.append(event)
        # Keep history length reasonable
        if len(history) > 200:
            history = history[-200:]
        self.update("logs_events_history", history, source="broadcast_history")
        logger.debug(f"Broadcasted logs event: {event_type}")

    def broadcast_settings_event(self, event_type: str, event_data: Dict[str, Any]):
        """Broadcast settings-related events to all subscribers"""
        event = {
            'type': event_type,
            'data': event_data,
            'timestamp': time.time()
        }
        self.update("settings_events", event, source="broadcast")

        # Append history
        history = self.get("settings_events_history", [])
        history.append(event)
        if len(history) > 200:
            history = history[-200:]
        self.update("settings_events_history", history, source="broadcast_history")

        # Update theme immediately if theme-related setting changed
        if event_type == "theme_change" and self.page:
            theme_mode = event_data.get('theme_mode')
            if theme_mode:
                try:
                    self.page.theme_mode = ft.ThemeMode.LIGHT if theme_mode == "light" else ft.ThemeMode.DARK
                    self.page.update()
                except Exception as e:
                    logger.debug(f"Failed to update page theme: {e}")

        logger.debug(f"Broadcasted settings event: {event_type}")

    # --- Debounce & Utilities ---

    def _debounce_call(self, key: str, func: Callable, delay: float = 0.2):
        """Debounce callable execution identified by key; func can be coroutine or callable"""
        # Cancel existing task if present
        task = self._debounce_tasks.get(key)
        if task and not task.done():
            task.cancel()

        async def _worker():
            try:
                await asyncio.sleep(delay)
                result = func()
                if asyncio.iscoroutine(result):
                    await result
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Debounced task '{key}' failed: {e}")
            finally:
                # Clean up
                if key in self._debounce_tasks and self._debounce_tasks[key] == asyncio.current_task():
                    del self._debounce_tasks[key]

        # Schedule new task
        try:
            loop = asyncio.get_running_loop()
            new_task = loop.create_task(_worker())
        except RuntimeError:
            # No running loop -> use create_task (will error if truly unavailable)
            new_task = asyncio.create_task(_worker())
        self._debounce_tasks[key] = new_task

    def _deep_merge_dicts(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge dict b into a and return new dict (b overrides a)"""
        result = dict(a) if a else {}
        for k, v in (b or {}).items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self._deep_merge_dicts(result[k], v)
            else:
                result[k] = v
        return result

    # --- Enhanced Progress Tracking for Long-Running Operations ---

    def start_progress(self, operation: str, total_steps: int = 1, message: str = ""):
        """Initialize a progress tracker for an operation"""
        p = {
            "operation": operation,
            "total_steps": total_steps,
            "current_step": 0,
            "percentage": 0.0,
            "start_time": time.time(),
            "message": message,
            "completed": False
        }
        progress_states = self.get("progress_states", {})
        progress_states[operation] = p
        self.update("progress_states", progress_states, source="progress_start")
        self._progress_internal[operation] = p

    def update_progress(self, operation: str, step: Optional[int] = None, message: Optional[str] = None):
        """Update progress for an operation"""
        progress_states = self.get("progress_states", {})
        p = progress_states.get(operation, None)
        if not p:
            # Initialize if missing
            self.start_progress(operation, total_steps=step or 1, message=message or "")
            p = self.get("progress_states", {}).get(operation)

        if step is not None:
            p["current_step"] = step
        else:
            p["current_step"] = p.get("current_step", 0) + 1

        total = p.get("total_steps", 1) or 1
        p["percentage"] = min(100.0, (p["current_step"] / total) * 100.0)
        if message:
            p["message"] = message
        if p["current_step"] >= total:
            p["completed"] = True

        progress_states[operation] = p
        self.update("progress_states", progress_states, source="progress_update")

    def get_progress(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get current progress for an operation"""
        return self.get("progress_states", {}).get(operation)

    def clear_progress(self, operation: str):
        """Clear progress tracking for an operation"""
        progress_states = self.get("progress_states", {})
        if operation in progress_states:
            del progress_states[operation]
            self.update("progress_states", progress_states, source="progress_clear")
        if operation in self._progress_internal:
            del self._progress_internal[operation]

    # --- Enhanced Retry Mechanism Management ---

    async def retry_operation(self, operation_name: str, coro_func: Callable, max_retries: int = 3, retry_delay: float = 1.0):
        """Retry coroutine operation with exponential backoff and update retry state"""
        retry_info = self.get("retry_states", {})
        retry_record = retry_info.get(operation_name, {"attempts": 0, "last_error": None, "last_success": None})
        attempt = 0
        last_exception = None

        while attempt <= max_retries:
            try:
                attempt += 1
                retry_record["attempts"] = attempt
                self.update("retry_states", {**retry_info, operation_name: retry_record}, source="retry_update")
                result = await coro_func()
                # If result indicates failure in dict form, raise to trigger retry
                if isinstance(result, dict) and not result.get("success", True):
                    last_exception = Exception(result.get("error", "Unknown"))
                    raise last_exception
                # success
                retry_record["last_success"] = time.time()
                retry_record["last_error"] = None
                retry_info[operation_name] = retry_record
                self.update("retry_states", retry_info, source="retry_success")
                return result
            except Exception as e:
                last_exception = e
                retry_record["last_error"] = str(e)
                retry_info[operation_name] = retry_record
                self.update("retry_states", retry_info, source="retry_failed")
                logger.warning(f"Retry attempt {attempt} for {operation_name} failed: {e}")
                if attempt > max_retries:
                    break
                backoff = retry_delay * (2 ** (attempt - 1))
                await asyncio.sleep(backoff)

        # All retries failed
        self.set_error_state(operation_name, f"Operation failed after {max_retries} retries", {"last_error": str(last_exception)})
        return {'success': False, 'error': str(last_exception)}

    # --- Enhanced Error State Management ---

    def set_error_state(self, operation: str, error: str, details: Optional[Dict[str, Any]] = None):
        """Set error state for an operation"""
        error_data = {
            'operation': operation,
            'error': error,
            'details': details or {},
            'timestamp': time.time()
        }

        errors = self.get("error_states", {})
        errors[operation] = error_data
        self.update("error_states", errors, source="error")

        # Also add as notification
        self.add_notification(f"{operation.replace('_', ' ').title()}: {error}", "error")

        logger.error(f"Error state set for {operation}: {error}")

    def clear_error_state(self, operation: str):
        """Clear error state for an operation"""
        errors = self.get("error_states", {})
        if operation in errors:
            del errors[operation]
            self.update("error_states", errors, source="error_clear")
            logger.debug(f"Error state cleared for {operation}")

    def get_error_state(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get error state for an operation"""
        errors = self.get("error_states", {})
        return errors.get(operation)


# Factory function for backwards compatibility and easy creation
def create_state_manager(page: ft.Page, server_bridge=None) -> StateManager:
    """Create enhanced state manager with optional server bridge and specialized support"""
    state_manager = StateManager(page, server_bridge)

    # Initialize specialized state keys
    initial_state = {
        "logs_data": [],
        "logs_filters": {"level": "ALL", "component": "ALL", "search": ""},
        "logs_statistics": {},
        "settings_data": {},
        "settings_validation": {},
        "settings_backups": [],
        "error_states": {},
        "logs_events": {},
        "settings_events": {},
        "progress_states": {},
        "retry_states": {},
        "logs_filtered": [],
        "settings_version": 0,
        "settings_events_history": [],
        "logs_events_history": []
    }

    # Set initial state without triggering callbacks
    for key, value in initial_state.items():
        if key not in state_manager.state:
            state_manager.state[key] = value

    logger.info("Enhanced StateManager created with logs and settings support")
    return state_manager


