#!/usr/bin/env python3
"""
Simplified State Manager for FletV2
Framework-harmonious state management using Flet's built-in patterns.

Simplified from 415 lines to ~60 lines by:
- Removing complex caching (Flet handles this natively)
- Eliminating performance tracking (not needed)
- Removing StateProvider class (use direct Flet controls)
- Using simple state dictionary instead of complex subscriptions
- Direct control.update() calls for UI updates
"""

import flet as ft
from typing import Dict, Any, Callable, Optional
from utils.debug_setup import get_logger

logger = get_logger(__name__)


class StateManager:
    """Simplified state management using Flet's native patterns"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.state = {
            "clients": [],
            "files": [],
            "server_status": {},
            "database_info": {},
            "system_status": {},
            "connection_status": "disconnected",
            "current_view": "dashboard"
        }
        self.callbacks = {}  # {state_key: [callbacks]}
        logger.info("Simplified StateManager initialized")
    
    def update(self, key: str, value: Any):
        """Update state and notify callbacks - Framework harmonious"""
        if self.state.get(key) == value:
            return  # No change needed
        
        old_value = self.state.get(key)
        self.state[key] = value
        
        # Notify callbacks for this key
        if key in self.callbacks:
            for callback in self.callbacks[key]:
                try:
                    callback(value, old_value)
                except Exception as e:
                    logger.error(f"Callback failed for {key}: {e}")
    
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
    
    def batch_update(self, updates: Dict[str, Any]):
        """Update multiple state values efficiently"""
        for key, value in updates.items():
            self.update(key, value)


# Factory function for backwards compatibility
def create_state_manager(page: ft.Page) -> StateManager:
    """Create simplified state manager"""
    return StateManager(page)