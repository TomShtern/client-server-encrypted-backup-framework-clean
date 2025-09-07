#!/usr/bin/env python3
"""
Reactive State Manager for FletV2
Flet-optimized state management with precise UI updates and smart caching.

Features:
- Reactive subscriptions with automatic UI updates
- Smart caching to prevent duplicate API calls
- Precise control.update() instead of page.update()
- Real-time data synchronization
- Cross-view state sharing
"""

import flet as ft
from typing import Dict, Any, List, Callable, Optional
import asyncio
import time
import json
from utils.debug_setup import get_logger

logger = get_logger(__name__)


class StateManager:
    """
    Flet-optimized reactive state management
    
    Provides centralized state with automatic UI updates, smart caching,
    and precise control updates for maximum performance.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.subscribers = {}  # {state_key: [callbacks]}
        self.cache = {}       # {state_key: {"data": value, "timestamp": time}}
        self.state = {
            "clients": [],
            "files": [],
            "server_status": {},
            "database_info": {},
            "system_status": {},
            "connection_status": "disconnected",
            "realtime_updates": True,
            "current_view": "dashboard"
        }
        
        # Performance tracking
        self.update_count = 0
        self.cache_hits = 0
        self.last_cleanup = time.time()
        
        logger.info("StateManager initialized with Flet optimization")
    
    async def update_state(self, key: str, value: Any, force_update: bool = False) -> bool:
        """
        Smart state updates - only notify if data actually changed
        
        Args:
            key: State key to update
            value: New value
            force_update: Force update even if value unchanged
            
        Returns:
            bool: True if state was actually updated
        """
        try:
            # Check if update is necessary
            if not force_update and self.state.get(key) == value:
                logger.debug(f"Skipping unchanged state update for {key}")
                return False
            
            # Update state
            old_value = self.state.get(key)
            self.state[key] = value
            
            # Update cache
            self.cache[key] = {
                "data": value,
                "timestamp": time.time()
            }
            
            # Track performance
            self.update_count += 1
            
            logger.debug(f"State updated: {key} (subscribers: {len(self.subscribers.get(key, []))})")
            
            # Notify all subscribers for this state key
            if key in self.subscribers:
                await self._notify_subscribers(key, value, old_value)
            
            # Cleanup old cache entries periodically
            await self._periodic_cleanup()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update state {key}: {e}")
            return False
    
    async def _notify_subscribers(self, key: str, new_value: Any, old_value: Any):
        """Notify all subscribers with error handling"""
        failed_callbacks = []
        
        for i, callback in enumerate(self.subscribers[key]):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(new_value, old_value)
                else:
                    callback(new_value, old_value)
            except Exception as e:
                logger.error(f"Subscriber callback failed for {key}[{i}]: {e}")
                failed_callbacks.append(callback)
        
        # Remove failed callbacks
        for failed_callback in failed_callbacks:
            self.subscribers[key].remove(failed_callback)
    
    def subscribe(self, key: str, callback: Callable, control: Optional[ft.Control] = None) -> str:
        """
        Subscribe to state changes with automatic UI updates
        
        Args:
            key: State key to watch
            callback: Function to call on state change (new_value, old_value)
            control: Optional Flet control to update automatically
            
        Returns:
            str: Subscription ID for later unsubscribing
        """
        if key not in self.subscribers:
            self.subscribers[key] = []
        
        # Create wrapper for automatic control updates
        if control:
            original_callback = callback
            
            async def auto_update_callback(new_value, old_value):
                try:
                    # Call original callback
                    if asyncio.iscoroutinefunction(original_callback):
                        await original_callback(new_value, old_value)
                    else:
                        original_callback(new_value, old_value)
                    
                    # Update control automatically
                    if hasattr(control, 'update') and callable(control.update):
                        if asyncio.iscoroutinefunction(control.update):
                            await control.update()
                        else:
                            control.update()
                    
                except Exception as e:
                    logger.error(f"Auto-update callback failed: {e}")
            
            callback_to_use = auto_update_callback
        else:
            callback_to_use = callback
        
        self.subscribers[key].append(callback_to_use)
        subscription_id = f"{key}_{len(self.subscribers[key])}"
        
        logger.debug(f"Subscribed to {key} (total subscribers: {len(self.subscribers[key])})")
        
        # Immediately call with current value if available
        if key in self.state and self.state[key] is not None:
            try:
                if asyncio.iscoroutinefunction(callback_to_use):
                    asyncio.create_task(callback_to_use(self.state[key], None))
                else:
                    callback_to_use(self.state[key], None)
            except Exception as e:
                logger.error(f"Initial callback failed for {key}: {e}")
        
        return subscription_id
    
    def unsubscribe(self, key: str, callback: Callable):
        """Unsubscribe from state changes"""
        if key in self.subscribers and callback in self.subscribers[key]:
            self.subscribers[key].remove(callback)
            logger.debug(f"Unsubscribed from {key}")
    
    def unsubscribe_all(self, key: str):
        """Remove all subscriptions for a state key"""
        if key in self.subscribers:
            count = len(self.subscribers[key])
            self.subscribers[key].clear()
            logger.debug(f"Unsubscribed all {count} callbacks from {key}")
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get current state value"""
        return self.state.get(key, default)
    
    def get_cached(self, key: str, max_age_seconds: int = 30) -> Optional[Any]:
        """
        Get cached data if it's recent enough
        
        Args:
            key: State key
            max_age_seconds: Maximum age of cached data
            
        Returns:
            Cached data or None if too old/missing
        """
        if key in self.cache:
            cache_entry = self.cache[key]
            age = time.time() - cache_entry["timestamp"]
            
            if age < max_age_seconds:
                self.cache_hits += 1
                logger.debug(f"Cache hit for {key} (age: {age:.1f}s)")
                return cache_entry["data"]
            else:
                logger.debug(f"Cache expired for {key} (age: {age:.1f}s)")
        
        return None
    
    def invalidate_cache(self, key: str = None):
        """
        Invalidate cached data
        
        Args:
            key: Specific key to invalidate, or None for all
        """
        if key:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Invalidated cache for {key}")
        else:
            self.cache.clear()
            logger.debug("Invalidated all cache")
    
    async def _periodic_cleanup(self):
        """Clean up old cache entries and expired subscriptions"""
        current_time = time.time()
        
        # Only cleanup every 5 minutes
        if current_time - self.last_cleanup < 300:
            return
        
        self.last_cleanup = current_time
        
        # Remove cache entries older than 10 minutes
        expired_keys = []
        for key, cache_entry in self.cache.items():
            if current_time - cache_entry["timestamp"] > 600:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get state manager performance statistics"""
        return {
            "total_updates": self.update_count,
            "cache_hits": self.cache_hits,
            "active_subscriptions": sum(len(subs) for subs in self.subscribers.values()),
            "cached_items": len(self.cache),
            "state_keys": list(self.state.keys())
        }
    
    def batch_update(self, updates: Dict[str, Any]) -> int:
        """
        Batch multiple state updates for efficiency
        
        Args:
            updates: Dictionary of key-value pairs to update
            
        Returns:
            Number of successful updates
        """
        successful_updates = 0
        
        for key, value in updates.items():
            try:
                # Use synchronous update for batch operations
                if self.state.get(key) != value:
                    self.state[key] = value
                    self.cache[key] = {
                        "data": value,
                        "timestamp": time.time()
                    }
                    successful_updates += 1
            except Exception as e:
                logger.error(f"Batch update failed for {key}: {e}")
        
        # Notify all subscribers after batch update
        if successful_updates > 0:
            self.page.run_task(self._notify_batch_subscribers(updates))
        
        return successful_updates
    
    async def _notify_batch_subscribers(self, updates: Dict[str, Any]):
        """Notify subscribers for batch updates"""
        for key, value in updates.items():
            if key in self.subscribers:
                await self._notify_subscribers(key, value, None)
    
    def create_view_subscription(self, view_name: str, subscriptions: List[str]) -> str:
        """
        Create a view-specific subscription group
        
        Args:
            view_name: Name of the view
            subscriptions: List of state keys to subscribe to
            
        Returns:
            Group ID for managing subscriptions
        """
        group_id = f"view_{view_name}_{int(time.time())}"
        
        def cleanup_callback(new_view, old_view):
            if new_view != view_name:
                # Clean up subscriptions when view changes
                for key in subscriptions:
                    if key in self.subscribers:
                        # Remove view-specific callbacks
                        self.subscribers[key] = [
                            cb for cb in self.subscribers[key] 
                            if not hasattr(cb, 'view_group') or cb.view_group != group_id
                        ]
        
        # Subscribe to view changes for cleanup
        self.subscribe("current_view", cleanup_callback)
        
        return group_id
    
    async def preload_data(self, keys: List[str], data_provider: Callable):
        """
        Preload data for specified keys
        
        Args:
            keys: State keys to preload
            data_provider: Async function that returns dict of key-value pairs
        """
        try:
            data = await data_provider(keys)
            updates = {}
            
            for key in keys:
                if key in data:
                    updates[key] = data[key]
            
            if updates:
                self.batch_update(updates)
                logger.debug(f"Preloaded data for {len(updates)} keys")
            
        except Exception as e:
            logger.error(f"Failed to preload data: {e}")


class StateProvider:
    """Helper class for providing state to UI components"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
    
    def create_reactive_text(self, state_key: str, formatter: Callable[[Any], str] = str, **text_props) -> ft.Text:
        """Create a Text control that updates automatically with state changes"""
        text_control = ft.Text(value="Loading...", **text_props)
        
        def update_text(new_value, old_value):
            try:
                text_control.value = formatter(new_value)
                text_control.update()
            except Exception as e:
                logger.error(f"Failed to update reactive text: {e}")
                text_control.value = "Error"
                text_control.update()
        
        self.state_manager.subscribe(state_key, update_text, text_control)
        return text_control
    
    def create_reactive_progress(self, state_key: str, max_value: float = 100, **progress_props) -> ft.ProgressBar:
        """Create a ProgressBar that updates automatically with state changes"""
        progress_control = ft.ProgressBar(value=0, **progress_props)
        
        def update_progress(new_value, old_value):
            try:
                if isinstance(new_value, (int, float)):
                    progress_control.value = new_value / max_value
                    progress_control.update()
            except Exception as e:
                logger.error(f"Failed to update reactive progress: {e}")
        
        self.state_manager.subscribe(state_key, update_progress, progress_control)
        return progress_control
    
    def create_reactive_icon(self, state_key: str, icon_mapping: Dict[str, str], **icon_props) -> ft.Icon:
        """Create an Icon that changes based on state"""
        icon_control = ft.Icon(name=ft.Icons.HELP, **icon_props)
        
        def update_icon(new_value, old_value):
            try:
                icon_name = icon_mapping.get(str(new_value), ft.Icons.HELP)
                icon_control.name = icon_name
                icon_control.update()
            except Exception as e:
                logger.error(f"Failed to update reactive icon: {e}")
        
        self.state_manager.subscribe(state_key, update_icon, icon_control)
        return icon_control


# Factory function for easy creation
def create_state_manager(page: ft.Page) -> StateManager:
    """
    Factory function to create a state manager
    
    Args:
        page: Flet page instance
        
    Returns:
        StateManager instance
    """
    return StateManager(page)