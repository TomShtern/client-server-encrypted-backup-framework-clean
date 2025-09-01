#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LayoutEventDispatcher - Extracted from responsive_layout.py

Handles layout event callback registration, storage, and dispatching.
Part of Phase 2 God Component decomposition: Final extraction (4th of 4 managers).

SINGLE RESPONSIBILITY: Event callback lifecycle and notification system
- Register/unregister event callbacks
- Store event callbacks by type
- Dispatch events to registered callbacks with error handling
- Provide event system statistics

STATUS: Phase 2 Complete - 50%+ reduction achieved
"""

import Shared.utils.utf8_solution  # UTF-8 solution

from typing import Dict, List, Callable, Any
import asyncio
import logging


class LayoutEventDispatcher:
    """
    Manages layout event callback registration and dispatching.
    
    SINGLE RESPONSIBILITY: Event callback lifecycle and notification system
    
    Supports event types:
    - screen_size_changed: Screen size category changes
    - layout_mode_changed: Layout mode transitions 
    - navigation_pattern_changed: Navigation pattern switches
    - component_resized: Component resize events
    """
    
    def __init__(self, logger: logging.Logger = None):
        """
        Initialize layout event dispatcher
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Event callback storage organized by event type
        self.layout_callbacks: Dict[str, List[Callable]] = {
            "screen_size_changed": [],
            "layout_mode_changed": [], 
            "navigation_pattern_changed": [],
            "component_resized": []
        }
        
        self.logger.debug("LayoutEventDispatcher initialized")
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        Register callback for layout change events
        
        Args:
            event_type: Type of layout event to listen for
            callback: Callback function to register
        """
        if event_type in self.layout_callbacks:
            if callback not in self.layout_callbacks[event_type]:
                self.layout_callbacks[event_type].append(callback)
                self.logger.debug(f"Registered callback for {event_type}")
            else:
                self.logger.warning(f"Callback already registered for {event_type}")
        else:
            self.logger.error(f"Unknown event type: {event_type}")
    
    def unregister_callback(self, event_type: str, callback: Callable) -> bool:
        """
        Unregister layout change callback
        
        Args:
            event_type: Type of layout event
            callback: Callback function to unregister
            
        Returns:
            bool: True if callback was found and removed, False otherwise
        """
        if event_type in self.layout_callbacks and callback in self.layout_callbacks[event_type]:
            self.layout_callbacks[event_type].remove(callback)
            self.logger.debug(f"Unregistered callback for {event_type}")
            return True
        
        self.logger.warning(f"Callback not found for unregistration: {event_type}")
        return False
    
    async def fire_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Fire layout change event to all registered callbacks
        
        Args:
            event_type: Type of event to fire
            event_data: Event data to pass to callbacks
        """
        try:
            callbacks = self.layout_callbacks.get(event_type, [])
            self.logger.debug(f"Firing {event_type} event to {len(callbacks)} callbacks")
            
            for callback in callbacks:
                try:
                    # Handle both async and sync callbacks
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_data)
                    else:
                        callback(event_data)
                        
                except Exception as e:
                    self.logger.error(f"Layout callback error in {event_type}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Layout event firing error for {event_type}: {e}")
    
    def get_registered_events(self) -> Dict[str, int]:
        """
        Get statistics on registered event callbacks
        
        Returns:
            Dict[str, int]: Event types and their callback counts
        """
        return {
            event_type: len(callbacks) 
            for event_type, callbacks in self.layout_callbacks.items()
        }
    
    def get_total_callbacks(self) -> int:
        """
        Get total number of registered callbacks across all event types
        
        Returns:
            int: Total callback count
        """
        return sum(len(callbacks) for callbacks in self.layout_callbacks.values())
    
    def clear_callbacks(self, event_type: str = None) -> None:
        """
        Clear callbacks for specific event type or all event types
        
        Args:
            event_type: Specific event type to clear, or None for all
        """
        if event_type is None:
            # Clear all callbacks
            for event_callbacks in self.layout_callbacks.values():
                event_callbacks.clear()
            self.logger.debug("Cleared all layout event callbacks")
        elif event_type in self.layout_callbacks:
            self.layout_callbacks[event_type].clear()
            self.logger.debug(f"Cleared callbacks for {event_type}")
        else:
            self.logger.warning(f"Unknown event type for clearing: {event_type}")
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive event dispatcher statistics
        
        Returns:
            Dict: Complete event system statistics
        """
        return {
            "supported_events": list(self.layout_callbacks.keys()),
            "registered_callbacks": self.get_registered_events(),
            "total_callbacks": self.get_total_callbacks(),
            "active_event_types": len([
                event_type for event_type, callbacks in self.layout_callbacks.items()
                if len(callbacks) > 0
            ])
        }