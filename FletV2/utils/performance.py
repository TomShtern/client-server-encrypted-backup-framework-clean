"""
Performance Optimization Utilities for FletV2

This module provides utilities for improving Flet application performance:
- Debouncing for search and filtering operations
- Async data loading helpers
- Pagination utilities
- Memory management helpers
- Background task management

Author: Claude (2025-09-09)
"""

import asyncio
import threading
import time
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import weakref
import gc

logger = logging.getLogger(__name__)

T = TypeVar('T')

class Debouncer:
    """
    Debouncer utility for delaying function execution until after a specified delay.
    Useful for search inputs and filters to avoid excessive API calls.
    """
    
    def __init__(self, delay: float = 0.3):
        """
        Initialize debouncer.
        
        Args:
            delay: Delay in seconds before executing the function
        """
        self.delay = delay
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
    
    def debounce(self, func: Callable[[], None]) -> None:
        """
        Debounce a function call.
        
        Args:
            func: Function to execute after delay
        """
        with self._lock:
            if self._timer:
                self._timer.cancel()
            
            self._timer = threading.Timer(self.delay, func)
            self._timer.start()
    
    def cancel(self) -> None:
        """Cancel any pending debounced function call."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None

class AsyncDebouncer:
    """
    Async version of debouncer for async functions.
    """
    
    def __init__(self, delay: float = 0.3):
        self.delay = delay
        self._task: Optional[asyncio.Task] = None
    
    async def debounce(self, coro: Callable[[], Any]) -> None:
        """
        Debounce an async function call.
        
        Args:
            coro: Coroutine function to execute after delay
        """
        if self._task and not self._task.done():
            self._task.cancel()
        
        async def delayed_execution():
            await asyncio.sleep(self.delay)
            await coro()
        
        self._task = asyncio.create_task(delayed_execution())
    
    def cancel(self) -> None:
        """Cancel any pending debounced function call."""
        if self._task and not self._task.done():
            self._task.cancel()

@dataclass
class PaginationConfig:
    """Configuration for pagination."""
    page_size: int = 50
    current_page: int = 0
    total_items: int = 0
    
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return max(1, (self.total_items + self.page_size - 1) // self.page_size)
    
    @property
    def start_index(self) -> int:
        """Get start index for current page."""
        return self.current_page * self.page_size
    
    @property
    def end_index(self) -> int:
        """Get end index for current page."""
        return min(self.start_index + self.page_size, self.total_items)
    
    def get_page_data(self, data: List[T]) -> List[T]:
        """Get data for current page."""
        return data[self.start_index:self.end_index]
    
    def next_page(self) -> bool:
        """Move to next page. Returns True if successful."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            return True
        return False
    
    def prev_page(self) -> bool:
        """Move to previous page. Returns True if successful."""
        if self.current_page > 0:
            self.current_page -= 1
            return True
        return False
    
    def goto_page(self, page: int) -> bool:
        """Go to specific page. Returns True if successful."""
        if 0 <= page < self.total_pages:
            self.current_page = page
            return True
        return False

class AsyncDataLoader:
    """
    Async data loader with caching and background prefetching.
    """
    
    def __init__(self, max_cache_size: int = 100):
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._max_cache_size = max_cache_size
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="DataLoader")
        self._prefetch_tasks: Dict[str, asyncio.Task] = {}
    
    async def load_data_async(self, 
                             key: str, 
                             loader_func: Callable[[], Any],
                             cache_ttl: float = 300.0,
                             use_cache: bool = True) -> Any:
        """
        Load data asynchronously with caching.
        
        Args:
            key: Cache key for the data
            loader_func: Function to load data (can be sync or async)
            cache_ttl: Cache time-to-live in seconds
            use_cache: Whether to use caching
            
        Returns:
            Loaded data
        """
        # Check cache first
        if use_cache and key in self._cache:
            cache_time = self._cache_timestamps.get(key, 0)
            if time.time() - cache_time < cache_ttl:
                logger.debug(f"Cache hit for key: {key}")
                return self._cache[key]
        
        # Load data asynchronously
        logger.debug(f"Loading data for key: {key}")
        try:
            if asyncio.iscoroutinefunction(loader_func):
                data = await loader_func()
            else:
                # Run sync function in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(self._executor, loader_func)
            
            # Cache the result
            if use_cache:
                self._cache[key] = data
                self._cache_timestamps[key] = time.time()
                self._cleanup_cache()
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to load data for key {key}: {e}")
            # Return cached data if available, even if expired
            if key in self._cache:
                logger.warning(f"Returning stale cached data for key: {key}")
                return self._cache[key]
            raise
    
    def prefetch_data(self, 
                     key: str, 
                     loader_func: Callable[[], Any],
                     cache_ttl: float = 300.0) -> None:
        """
        Prefetch data in the background.
        
        Args:
            key: Cache key for the data
            loader_func: Function to load data
            cache_ttl: Cache time-to-live in seconds
        """
        # Cancel existing prefetch task for this key
        if key in self._prefetch_tasks:
            self._prefetch_tasks[key].cancel()
        
        async def prefetch():
            try:
                await self.load_data_async(key, loader_func, cache_ttl, use_cache=True)
                logger.debug(f"Prefetched data for key: {key}")
            except Exception as e:
                logger.debug(f"Prefetch failed for key {key}: {e}")
            finally:
                self._prefetch_tasks.pop(key, None)
        
        self._prefetch_tasks[key] = asyncio.create_task(prefetch())
    
    def _cleanup_cache(self) -> None:
        """Clean up old cache entries."""
        if len(self._cache) > self._max_cache_size:
            # Remove oldest entries
            sorted_keys = sorted(self._cache_timestamps.items(), key=lambda x: x[1])
            keys_to_remove = [key for key, _ in sorted_keys[:len(self._cache) - self._max_cache_size]]
            
            for key in keys_to_remove:
                self._cache.pop(key, None)
                self._cache_timestamps.pop(key, None)
            
            logger.debug(f"Cleaned {len(keys_to_remove)} cache entries")
    
    def clear_cache(self, key: Optional[str] = None) -> None:
        """Clear cache entries."""
        if key:
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
        logger.debug(f"Cleared cache for key: {key if key else 'all'}")
    
    def shutdown(self) -> None:
        """Shutdown the data loader."""
        # Cancel all prefetch tasks
        for task in self._prefetch_tasks.values():
            task.cancel()
        
        # Shutdown thread pool
        self._executor.shutdown(wait=True)
        logger.debug("AsyncDataLoader shutdown complete")

class MemoryManager:
    """
    Memory management utilities for long-running Flet applications.
    """
    
    def __init__(self):
        self._weak_refs: List[weakref.ref] = []
        self._last_gc_time = time.time()
        self._gc_interval = 60.0  # Run GC every 60 seconds
    
    def register_cleanup(self, obj: Any, cleanup_func: Optional[Callable] = None) -> None:
        """
        Register an object for cleanup.
        
        Args:
            obj: Object to track
            cleanup_func: Optional cleanup function to call when object is deleted
        """
        if cleanup_func:
            ref = weakref.ref(obj, lambda x: cleanup_func())
        else:
            ref = weakref.ref(obj)
        self._weak_refs.append(ref)
    
    def register_component(self, component_name: str) -> None:
        """
        Register a component for memory tracking.
        
        Args:
            component_name: Name of the component being registered
        """
        logger.debug(f"Registered component for memory tracking: {component_name}")
        # For now, just log the registration. Could be extended for component-specific tracking.
    
    def force_cleanup(self) -> Dict[str, int]:
        """
        Force garbage collection and cleanup.
        
        Returns:
            Dictionary with cleanup statistics
        """
        # Clean up dead weak references
        alive_refs = []
        dead_count = 0
        
        for ref in self._weak_refs:
            if ref() is not None:
                alive_refs.append(ref)
            else:
                dead_count += 1
        
        self._weak_refs = alive_refs
        
        # Force garbage collection
        before = len(gc.get_objects())
        collected = gc.collect()
        after = len(gc.get_objects())
        
        stats = {
            'dead_refs_cleaned': dead_count,
            'gc_collected': collected,
            'objects_before': before,
            'objects_after': after,
            'objects_freed': before - after
        }
        
        self._last_gc_time = time.time()
        logger.debug(f"Memory cleanup completed: {stats}")
        return stats
    
    def maybe_cleanup(self) -> Optional[Dict[str, int]]:
        """
        Run cleanup if enough time has passed.
        
        Returns:
            Cleanup statistics if cleanup was performed, None otherwise
        """
        if time.time() - self._last_gc_time > self._gc_interval:
            return self.force_cleanup()
        return None

class BackgroundTaskManager:
    """
    Manager for background tasks with proper cleanup.
    """
    
    def __init__(self):
        self._tasks: Dict[str, asyncio.Task] = {}
        self._shutdown = False
    
    def start_task(self, name: str, coro: Callable[[], Any], restart_on_error: bool = False) -> str:
        """
        Start a background task.
        
        Args:
            name: Task name
            coro: Coroutine to run
            restart_on_error: Whether to restart task if it fails
            
        Returns:
            Task name
        """
        # Cancel existing task with same name
        self.stop_task(name)
        
        async def task_wrapper():
            try:
                while not self._shutdown:
                    try:
                        await coro()
                        break  # Task completed successfully
                    except Exception as e:
                        logger.error(f"Background task '{name}' failed: {e}")
                        if not restart_on_error:
                            break
                        await asyncio.sleep(1)  # Brief delay before restart
            except asyncio.CancelledError:
                logger.debug(f"Background task '{name}' was cancelled")
                raise
        
        self._tasks[name] = asyncio.create_task(task_wrapper())
        logger.debug(f"Started background task: {name}")
        return name
    
    def stop_task(self, name: str) -> bool:
        """
        Stop a background task.
        
        Args:
            name: Task name
            
        Returns:
            True if task was stopped, False if task didn't exist
        """
        if name in self._tasks:
            task = self._tasks.pop(name)
            if not task.done():
                task.cancel()
            logger.debug(f"Stopped background task: {name}")
            return True
        return False
    
    def get_task_status(self, name: str) -> Optional[str]:
        """
        Get status of a background task.
        
        Args:
            name: Task name
            
        Returns:
            Task status or None if task doesn't exist
        """
        if name in self._tasks:
            task = self._tasks[name]
            if task.done():
                if task.cancelled():
                    return "cancelled"
                elif task.exception():
                    return f"failed: {task.exception()}"
                else:
                    return "completed"
            else:
                return "running"
        return None
    
    def shutdown(self) -> None:
        """Shutdown all background tasks."""
        self._shutdown = True
        for name, task in self._tasks.items():
            if not task.done():
                task.cancel()
                logger.debug(f"Cancelled background task: {name}")
        self._tasks.clear()

# Global instances for easy access
global_debouncer = Debouncer()
global_async_debouncer = AsyncDebouncer()
global_data_loader = AsyncDataLoader()
global_memory_manager = MemoryManager()
global_task_manager = BackgroundTaskManager()

# Utility functions for easy use
def debounce(func: Callable[[], None], delay: float = 0.3) -> None:
    """Convenience function for debouncing."""
    debouncer = Debouncer(delay)
    debouncer.debounce(func)

async def async_debounce(coro: Callable[[], Any], delay: float = 0.3) -> None:
    """Convenience function for async debouncing."""
    debouncer = AsyncDebouncer(delay)
    await debouncer.debounce(coro)

def paginate_data(data: List[T], page: int = 0, page_size: int = 50) -> tuple[List[T], PaginationConfig]:
    """
    Convenience function for paginating data.
    
    Returns:
        Tuple of (paginated_data, pagination_config)
    """
    config = PaginationConfig(page_size=page_size, current_page=page, total_items=len(data))
    return config.get_page_data(data), config

async def load_async(key: str, loader_func: Callable[[], Any], cache_ttl: float = 300.0) -> Any:
    """Convenience function for async data loading."""
    return await global_data_loader.load_data_async(key, loader_func, cache_ttl)

def cleanup_memory() -> Dict[str, int]:
    """Convenience function for memory cleanup."""
    return global_memory_manager.force_cleanup()
