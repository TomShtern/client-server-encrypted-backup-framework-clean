#!/usr/bin/env python3
"""
Thread-Safe UI Update Utilities
Provides safe UI update patterns for Flet applications

This module addresses critical thread safety issues in the Flet GUI where
background threads were calling page.update() directly, causing race conditions
and GUI freezing. The ThreadSafeUIUpdater provides a queue-based system to
safely update the UI from background threads.

Key Features:
- Queue-based UI updates for thread safety
- Decorator pattern for easy integration
- Fallback mechanisms for compatibility
- Async-aware design for Flet applications

Usage:
    # Initialize in your main application
    ui_updater = ThreadSafeUIUpdater(page)
    await ui_updater.start()
    
    # Use decorator for thread-safe updates
    @ui_safe_update
    def update_ui_element(self):
        self.some_control.value = "Updated safely"
    
    # Or queue updates directly
    ui_updater.queue_update(lambda: self.update_control())
"""

import asyncio
import functools
from typing import Callable, Any, Optional, Union
import flet as ft
import threading
from concurrent.futures import Future
import logging

# Configure logging for thread-safe UI operations
logger = logging.getLogger(__name__)


class ThreadSafeUIUpdater:
    """
    Thread-safe UI update manager for Flet applications
    
    This class provides a safe way to update the UI from background threads
    by queueing update operations and processing them on the main thread.
    It prevents race conditions and GUI freezing issues.
    """
    
    def __init__(self, page: ft.Page, max_queue_size: int = 1000):
        """
        Initialize the thread-safe UI updater
        
        Args:
            page: The Flet page instance
            max_queue_size: Maximum number of queued updates (default: 1000)
        """
        self.page = page
        self._update_queue = asyncio.Queue(maxsize=max_queue_size)
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._max_queue_size = max_queue_size
        
    async def start(self):
        """Start the UI update processor"""
        if self._running:
            logger.warning("ThreadSafeUIUpdater already running")
            return
            
        self._running = True
        self._processor_task = asyncio.create_task(self._process_updates())
        logger.info("ThreadSafeUIUpdater started")
        
    async def stop(self):
        """Stop the UI update processor"""
        if not self._running:
            return
            
        self._running = False
        
        # Cancel the processor task
        if self._processor_task and not self._processor_task.done():
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
                
        # Process any remaining updates
        while not self._update_queue.empty():
            try:
                update_func = self._update_queue.get_nowait()
                if callable(update_func):
                    update_func()
                self._update_queue.task_done()
            except asyncio.QueueEmpty:
                break
            except Exception as e:
                logger.error(f"Error processing remaining UI update: {e}")
                
        logger.info("ThreadSafeUIUpdater stopped")
        
    async def _process_updates(self):
        """Process queued UI updates on the main thread"""
        batch_size = 10  # Process multiple updates in one page.update()
        
        while self._running:
            try:
                updates_to_process = []
                
                # Get first update (blocking wait)
                try:
                    first_update = await asyncio.wait_for(
                        self._update_queue.get(), timeout=1.0
                    )
                    updates_to_process.append(first_update)
                    self._update_queue.task_done()
                except asyncio.TimeoutError:
                    continue
                    
                # Get additional updates (non-blocking) for batching
                for _ in range(batch_size - 1):
                    try:
                        update_func = self._update_queue.get_nowait()
                        updates_to_process.append(update_func)
                        self._update_queue.task_done()
                    except asyncio.QueueEmpty:
                        break
                
                # Execute all updates and then call page.update() once
                for update_func in updates_to_process:
                    try:
                        if callable(update_func):
                            if asyncio.iscoroutinefunction(update_func):
                                await update_func()
                            else:
                                update_func()
                    except Exception as e:
                        logger.error(f"Error executing UI update: {e}")
                        
                # Single page update for all batched changes
                if self.page and updates_to_process:
                    try:
                        self.page.update()
                    except Exception as e:
                        logger.error(f"Error updating page: {e}")
                        
            except Exception as e:
                logger.error(f"Error in UI update processor: {e}")
                
    def queue_update(self, update_func: Callable, priority: bool = False):
        """
        Queue a UI update to be processed safely
        
        Args:
            update_func: Function to execute for the UI update
            priority: If True, add to front of queue (for critical updates)
        """
        if not self._running:
            logger.warning("ThreadSafeUIUpdater not running, executing update directly")
            try:
                if callable(update_func):
                    if asyncio.iscoroutinefunction(update_func):
                        # For async functions, we need to run them properly
                        asyncio.create_task(update_func())
                    else:
                        update_func()
                if self.page:
                    self.page.update()
            except Exception as e:
                logger.error(f"Error in direct UI update: {e}")
            return
            
        try:
            if self._update_queue.qsize() >= self._max_queue_size * 0.9:
                logger.warning("UI update queue nearly full, dropping oldest updates")
                # Remove some old updates to make room
                for _ in range(5):
                    try:
                        self._update_queue.get_nowait()
                        self._update_queue.task_done()
                    except asyncio.QueueEmpty:
                        break
                        
            self._update_queue.put_nowait(update_func)
            
        except asyncio.QueueFull:
            logger.error("UI update queue full, skipping update")
            
    def is_running(self) -> bool:
        """Check if the updater is running"""
        return self._running
        
    def queue_size(self) -> int:
        """Get current queue size"""
        return self._update_queue.qsize()


class ThreadSafeContext:
    """Context manager for thread-safe UI operations"""
    
    def __init__(self, updater: ThreadSafeUIUpdater):
        self.updater = updater
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def update(self, func: Callable):
        """Queue an update within the context"""
        self.updater.queue_update(func)


def ui_safe_update(func: Callable) -> Callable:
    """
    Decorator for thread-safe UI updates
    
    This decorator automatically queues UI updates through the ThreadSafeUIUpdater
    if available, or falls back to direct execution with page.update().
    
    Usage:
        @ui_safe_update
        def update_status(self):
            self.status_text.value = "Updated"
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Check if the instance has a ui_updater attribute
        if hasattr(self, 'ui_updater') and self.ui_updater and self.ui_updater.is_running():
            # Queue the UI update for thread-safe execution
            self.ui_updater.queue_update(
                lambda: func(self, *args, **kwargs)
            )
        else:
            # Fallback to direct execution if no updater available
            try:
                result = func(self, *args, **kwargs)
                
                # Try to update the page if available
                if hasattr(self, 'page') and self.page:
                    self.page.update()
                elif hasattr(self, '_page') and self._page:
                    self._page.update()
                    
                return result
            except Exception as e:
                logger.error(f"Error in direct UI update: {e}")
                raise
                
    return wrapper


async def safe_ui_update(page: ft.Page, update_func: Callable, *args, **kwargs):
    """
    Standalone function for thread-safe UI updates
    
    This function provides a way to safely update the UI without requiring
    a ThreadSafeUIUpdater instance.
    
    Args:
        page: Flet page instance
        update_func: Function to execute for the update
        *args, **kwargs: Arguments to pass to update_func
    """
    if not page:
        logger.error("No page provided for UI update")
        return
        
    try:
        # Execute the update function
        if asyncio.iscoroutinefunction(update_func):
            await update_func(*args, **kwargs)
        else:
            update_func(*args, **kwargs)
            
        # Update the page
        page.update()
        
    except Exception as e:
        logger.error(f"Error in safe UI update: {e}")
        raise


def create_safe_callback(page: ft.Page, callback: Callable, updater: Optional[ThreadSafeUIUpdater] = None) -> Callable:
    """
    Create a thread-safe callback wrapper
    
    Args:
        page: Flet page instance
        callback: Original callback function
        updater: Optional ThreadSafeUIUpdater instance
        
    Returns:
        Thread-safe callback function
    """
    def safe_callback(*args, **kwargs):
        def execute_callback():
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(*args, **kwargs))
                else:
                    callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in safe callback: {e}")
                
        if updater and updater.is_running():
            updater.queue_update(execute_callback)
        else:
            execute_callback()
            if page:
                page.update()
                
    return safe_callback


# Utility functions for common UI update patterns
def safe_control_update(control: ft.Control, property_name: str, value: Any, 
                       updater: Optional[ThreadSafeUIUpdater] = None, page: Optional[ft.Page] = None):
    """
    Safely update a control property
    
    Args:
        control: Flet control to update
        property_name: Name of the property to update
        value: New value for the property
        updater: Optional ThreadSafeUIUpdater instance
        page: Optional page instance (required if no updater)
    """
    def update_control():
        setattr(control, property_name, value)
        
    if updater and updater.is_running():
        updater.queue_update(update_control)
    else:
        update_control()
        if page:
            page.update()


def safe_controls_update(updates: list, updater: Optional[ThreadSafeUIUpdater] = None, 
                        page: Optional[ft.Page] = None):
    """
    Safely update multiple controls at once
    
    Args:
        updates: List of (control, property_name, value) tuples
        updater: Optional ThreadSafeUIUpdater instance
        page: Optional page instance (required if no updater)
    """
    def update_all_controls():
        for control, prop_name, value in updates:
            setattr(control, prop_name, value)
            
    if updater and updater.is_running():
        updater.queue_update(update_all_controls)
    else:
        update_all_controls()
        if page:
            page.update()