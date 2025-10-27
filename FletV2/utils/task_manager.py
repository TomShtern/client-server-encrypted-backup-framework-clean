"""
Async Task Manager - FletV2 Phase 0 Critical Fix

Prevents async task leaks, provides proper cleanup, and eliminates orphaned operations.
Replaces scattered task management with centralized, trackable system.

Priority: CRITICAL - Prevents production crashes and memory leaks
"""

import asyncio
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import weakref

logger = logging.getLogger(__name__)

class TaskManager:
    """
    Centralized async task management with proper cleanup.
    Prevents memory leaks and orphaned operations.
    """

    def __init__(self):
        self._tasks: Dict[str, asyncio.Task] = {}
        self._background_tasks: List[asyncio.Task] = []
        self._cleanup_callbacks: List[Callable] = []
        self._lock = threading.Lock()
        self._disposed = False

    def create_task(self,
                   name: str,
                   coro,
                   timeout: Optional[float] = None,
                   cleanup_on_dispose: bool = True) -> asyncio.Task:
        """
        Create and track a named async task with optional timeout.

        Args:
            name: Unique task identifier for tracking
            coro: Coroutine to execute
            timeout: Optional timeout in seconds
            cleanup_on_dispose: Whether task should be cancelled on dispose

        Returns:
            Created and tracked task
        """
        if self._disposed:
            logger.warning(f"TaskManager disposed, cannot create task: {name}")
            # Return cancelled task instead of crashing
            task = asyncio.create_task(asyncio.sleep(0))
            task.cancel()
            return task

        with self._lock:
            # Cancel existing task with same name
            if name in self._tasks:
                old_task = self._tasks[name]
                if not old_task.done():
                    logger.info(f"Cancelling existing task: {name}")
                    old_task.cancel()
                    # Don't remove yet - let cleanup handle it

            # Create new task with timeout wrapper if specified
            if timeout:
                coro = self._wrap_with_timeout(coro, name, timeout)

            task = asyncio.create_task(self._wrap_task_logging(coro, name), name=name)
            self._tasks[name] = task

            # Add cleanup callback
            if cleanup_on_dispose:
                task.add_done_callback(lambda t: self._cleanup_task(name, t))

            logger.info(f"Created tracked task: {name}")
            return task

    def create_background_task(self, coro, name: Optional[str] = None) -> asyncio.Task:
        """
        Create background task that's cleaned up on dispose.
        Used for fire-and-forget operations.
        """
        task = asyncio.create_task(self._wrap_task_logging(coro, name or "background"))
        self._background_tasks.append(task)

        # Add cleanup callback
        task.add_done_callback(lambda t: self._cleanup_background_task(t))

        logger.info(f"Created background task: {name or 'unnamed'}")
        return task

    async def run_with_timeout(self,
                             func: Callable,
                             timeout: float,
                             *args,
                             **kwargs) -> Any:
        """
        Run synchronous function with timeout and proper error handling.
        Prevents deadlocks from blocking operations.
        """
        try:
            loop = asyncio.get_running_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: func(*args, **kwargs)),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Operation timed out after {timeout}s: {func.__name__}")
            raise TimeoutError(f"Operation {func.__name__} timed out after {timeout}s")
        except Exception as e:
            logger.error(f"Error in timeout wrapper for {func.__name__}: {e}")
            raise

    def get_task_status(self, name: str) -> Optional[str]:
        """Get status of tracked task."""
        with self._lock:
            task = self._tasks.get(name)
            if task:
                if task.done():
                    if task.cancelled():
                        return "cancelled"
                    elif task.exception():
                        return "error: " + str(task.exception())
                    else:
                        return "completed"
                return "running"
            return None

    def cancel_task(self, name: str) -> bool:
        """Cancel specific task by name."""
        with self._lock:
            task = self._tasks.get(name)
            if task and not task.done():
                logger.info(f"Cancelling task: {name}")
                task.cancel()
                return True
            return False

    def cancel_all_tasks(self) -> int:
        """Cancel all tracked tasks. Returns count of cancelled tasks."""
        cancelled_count = 0

        with self._lock:
            # Cancel named tasks
            for name, task in list(self._tasks.items()):
                if not task.done():
                    logger.info(f"Cancelling task: {name}")
                    task.cancel()
                    cancelled_count += 1

            # Cancel background tasks
            for task in self._background_tasks:
                if not task.done():
                    task.cancel()
                    cancelled_count += 1

        return cancelled_count

    def dispose(self) -> None:
        """
        Cancel all tasks and cleanup resources.
        Call this when page/view is disposed.
        """
        if self._disposed:
            return

        self._disposed = True
        logger.info("Disposing TaskManager - cleaning up all tasks")

        # Cancel all tasks
        cancelled_count = self.cancel_all_tasks()

        # Wait for tasks to finish cleanup
        with self._lock:
            self._tasks.clear()
            self._background_tasks.clear()

        # Run cleanup callbacks
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in cleanup callback: {e}")

        logger.info(f"TaskManager disposed - cancelled {cancelled_count} tasks")

    def add_cleanup_callback(self, callback: Callable) -> None:
        """Add callback to run on disposal."""
        self._cleanup_callbacks.append(callback)

    def _wrap_task_logging(self, coro, name: str):
        """Wrap coroutine with logging and error handling."""
        async def wrapped():
            start_time = datetime.now()
            try:
                logger.debug(f"Task starting: {name}")
                result = await coro
                duration = (datetime.now() - start_time).total_seconds()
                logger.debug(f"Task completed: {name} in {duration:.2f}s")
                return result
            except asyncio.CancelledError:
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"Task cancelled: {name} after {duration:.2f}s")
                raise
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(f"Task failed: {name} after {duration:.2f}s - {e}")
                raise

        return wrapped()

    def _wrap_with_timeout(self, coro, name: str, timeout: float):
        """Wrap coroutine with timeout."""
        async def wrapped():
            try:
                return await asyncio.wait_for(coro, timeout=timeout)
            except asyncio.TimeoutError:
                logger.error(f"Task timeout: {name} after {timeout}s")
                raise

        return wrapped()

    def _cleanup_task(self, name: str, task: asyncio.Task) -> None:
        """Remove completed task from tracking."""
        with self._lock:
            if name in self._tasks and self._tasks[name] == task:
                del self._tasks[name]
                logger.debug(f"Cleaned up completed task: {name}")

    def _cleanup_background_task(self, task: asyncio.Task) -> None:
        """Remove completed background task."""
        try:
            if task in self._background_tasks:
                self._background_tasks.remove(task)
                logger.debug("Cleaned up completed background task")
        except ValueError:
            # Task already removed
            pass

    def get_debug_info(self) -> Dict[str, Any]:
        """Get debugging information about task manager state."""
        with self._lock:
            active_named_tasks = len([t for t in self._tasks.values() if not t.done()])
            active_background_tasks = len([t for t in self._background_tasks if not t.done()])

            return {
                "tracked_tasks": len(self._tasks),
                "background_tasks": len(self._background_tasks),
                "active_named_tasks": active_named_tasks,
                "active_background_tasks": active_background_tasks,
                "disposed": self._disposed,
                "task_names": list(self._tasks.keys())
            }

# Global instance for FletV2
_task_manager = None

def get_task_manager() -> TaskManager:
    """Get or create global task manager instance."""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
        logger.info("Created global TaskManager instance")
    return _task_manager

def dispose_task_manager() -> None:
    """Dispose global task manager. Call on app shutdown."""
    global _task_manager
    if _task_manager:
        _task_manager.dispose()
        _task_manager = None