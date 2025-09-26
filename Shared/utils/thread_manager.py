#!/usr/bin/env python3
"""
Thread Management System - Centralized Thread Lifecycle Management
Provides coordinated shutdown signaling and resource cleanup across all components.

This module addresses the thread cleanup requirements from SYSTEM_REMEDIATION_REPORT.md
by providing proper shutdown signaling for all background threads in the system.
"""

import atexit
import logging
import signal
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, cast

logger = logging.getLogger(__name__)

class ThreadState(Enum):
    """Thread lifecycle states for monitoring."""
    CREATED = "created"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class ThreadInfo:
    """Information about a managed thread."""
    thread_id: int
    name: str
    thread_obj: threading.Thread
    created_at: datetime = field(default_factory=datetime.now)
    state: ThreadState = ThreadState.CREATED
    stop_event: threading.Event = field(default_factory=threading.Event)
    component: str = "unknown"
    daemon: bool = True
    cleanup_callback: Callable[[], None] | None = None

class ThreadManager:
    """
    Centralized thread management system for coordinated shutdown and resource cleanup.

    Features:
    - Thread registration and lifecycle tracking
    - Coordinated shutdown signaling across all threads
    - Resource cleanup callbacks
    - Thread health monitoring
    - Graceful vs forceful termination
    - Integration with system signals for clean shutdown
    """

    def __init__(self):
        """Initialize the thread manager."""
        self.threads: dict[str, ThreadInfo] = {}
        self.lock = threading.RLock()
        self.shutdown_event = threading.Event()
        self.shutdown_timeout = 30.0  # Default shutdown timeout

        # Register signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self.shutdown_all)

        logger.info("ThreadManager initialized with signal handlers")

    def register_thread(self, name: str, thread_obj: threading.Thread,
                       component: str = "unknown", daemon: bool = True,
                       cleanup_callback: Callable[[], None] | None = None) -> str:
        """
        Register a thread for management.

        Args:
            name: Unique thread name
            thread_obj: Thread object to manage
            component: Component name that owns the thread
            daemon: Whether thread is daemon
            cleanup_callback: Optional cleanup function to call on shutdown

        Returns:
            Thread ID for reference
        """
        with self.lock:
            # Create stop event for thread coordination
            stop_event = threading.Event()

            thread_info = ThreadInfo(
                thread_id=thread_obj.ident or id(thread_obj),
                name=name,
                thread_obj=thread_obj,
                component=component,
                daemon=daemon,
                cleanup_callback=cleanup_callback,
                stop_event=stop_event
            )

            # Add stop_event to thread object for easy access
            thread_dynamic = cast(Any, thread_obj)
            thread_dynamic.stop_event = stop_event
            thread_dynamic.thread_manager_name = name

            self.threads[name] = thread_info
            logger.info(f"Registered thread '{name}' from component '{component}' (daemon={daemon})")

            return name

    def start_thread(self, name: str) -> bool:
        """
        Start a registered thread.

        Args:
            name: Thread name to start

        Returns:
            True if started successfully, False otherwise
        """
        with self.lock:
            if name not in self.threads:
                logger.error(f"Cannot start unregistered thread '{name}'")
                return False

            thread_info = self.threads[name]

            try:
                if not thread_info.thread_obj.is_alive():
                    thread_info.thread_obj.start()
                    thread_info.state = ThreadState.RUNNING
                    logger.info(f"Started thread '{name}'")
                else:
                    logger.warning(f"Thread '{name}' is already running")
                return True
            except Exception as e:
                thread_info.state = ThreadState.ERROR
                logger.error(f"Failed to start thread '{name}': {e}")
                return False

    def stop_thread(self, name: str, timeout: float | None = None) -> bool:
        """
        Stop a specific thread gracefully.

        Args:
            name: Thread name to stop
            timeout: Timeout for graceful shutdown

        Returns:
            True if stopped successfully, False otherwise
        """
        with self.lock:
            if name not in self.threads:
                logger.warning(f"Cannot stop unregistered thread '{name}'")
                return True  # Consider it "stopped"

            thread_info = self.threads[name]

            if not thread_info.thread_obj.is_alive():
                logger.debug(f"Thread '{name}' is already stopped")
                thread_info.state = ThreadState.STOPPED
                return True

            # Signal the thread to stop
            thread_info.state = ThreadState.STOPPING
            thread_info.stop_event.set()
            logger.info(f"Signaled thread '{name}' to stop")

            # Wait for graceful shutdown
            shutdown_timeout = timeout or self.shutdown_timeout
            thread_info.thread_obj.join(timeout=shutdown_timeout)

            if thread_info.thread_obj.is_alive():
                logger.warning(f"Thread '{name}' did not stop gracefully within {shutdown_timeout}s")
                return False
            else:
                thread_info.state = ThreadState.STOPPED
                logger.info(f"Thread '{name}' stopped gracefully")

                # Run cleanup callback if provided
                if thread_info.cleanup_callback:
                    try:
                        thread_info.cleanup_callback()
                        logger.debug(f"Cleanup callback executed for thread '{name}'")
                    except Exception as e:
                        logger.error(f"Cleanup callback failed for thread '{name}': {e}")

                return True

    def shutdown_all(self, timeout: float | None = None) -> dict[str, bool]:
        """
        Shutdown all managed threads gracefully.

        Args:
            timeout: Total timeout for all threads to shutdown

        Returns:
            Dictionary mapping thread names to shutdown success status
        """
        logger.info("Starting coordinated shutdown of all managed threads")

        # Set global shutdown event
        self.shutdown_event.set()

        shutdown_timeout = timeout or self.shutdown_timeout
        start_time = time.time()
        results = {}

        with self.lock:
            # First, signal all threads to stop
            for name, thread_info in self.threads.items():
                if thread_info.thread_obj.is_alive():
                    thread_info.state = ThreadState.STOPPING
                    thread_info.stop_event.set()
                    logger.debug(f"Signaled thread '{name}' to stop")

            # Wait for threads to stop gracefully
            for name, thread_info in self.threads.items():
                if not thread_info.thread_obj.is_alive():
                    results[name] = True
                    continue

                # Calculate remaining timeout
                elapsed = time.time() - start_time
                remaining_timeout = max(0, shutdown_timeout - elapsed)

                if remaining_timeout > 0:
                    logger.info(f"Waiting for thread '{name}' to shutdown (timeout: {remaining_timeout:.1f}s)")
                    thread_info.thread_obj.join(timeout=remaining_timeout)

                if thread_info.thread_obj.is_alive():
                    logger.warning(f"Thread '{name}' did not stop gracefully")
                    results[name] = False
                else:
                    thread_info.state = ThreadState.STOPPED
                    logger.info(f"Thread '{name}' stopped gracefully")
                    results[name] = True

                    # Run cleanup callback
                    if thread_info.cleanup_callback:
                        try:
                            thread_info.cleanup_callback()
                            logger.debug(f"Cleanup callback executed for thread '{name}'")
                        except Exception as e:
                            logger.error(f"Cleanup callback failed for thread '{name}': {e}")

        successful_stops = sum(success for success in results.values() if success)
        total_threads = len(results)

        logger.info(f"Thread shutdown completed: {successful_stops}/{total_threads} threads stopped gracefully")

        return results

    def get_thread_status(self) -> dict[str, Any]:
        """
        Get status of all managed threads.

        Returns:
            Dictionary with thread status information
        """
        with self.lock:
            status: dict[str, Any] = {
                'total_threads': len(self.threads),
                'threads': {},
                'by_state': {},
                'by_component': {},
                'shutdown_in_progress': self.shutdown_event.is_set()
            }

            for name, thread_info in self.threads.items():
                # Update state based on actual thread status
                if thread_info.thread_obj.is_alive():
                    if thread_info.state == ThreadState.CREATED:
                        thread_info.state = ThreadState.RUNNING
                elif thread_info.state in [ThreadState.RUNNING, ThreadState.STOPPING]:
                    thread_info.state = ThreadState.STOPPED

                status['threads'][name] = {
                    'thread_id': thread_info.thread_id,
                    'component': thread_info.component,
                    'state': thread_info.state.value,
                    'daemon': thread_info.daemon,
                    'is_alive': thread_info.thread_obj.is_alive(),
                    'created_at': thread_info.created_at.isoformat(),
                    'has_cleanup_callback': thread_info.cleanup_callback is not None
                }

                # Count by state
                state_key = thread_info.state.value
                status['by_state'][state_key] = status['by_state'].get(state_key, 0) + 1

                # Count by component
                comp_key = thread_info.component
                status['by_component'][comp_key] = status['by_component'].get(comp_key, 0) + 1

            return status

    def is_shutdown_requested(self) -> bool:
        """
        Check if shutdown has been requested.

        Returns:
            True if shutdown is in progress
        """
        return self.shutdown_event.is_set()

    def wait_for_shutdown(self, timeout: float | None = None) -> bool:
        """
        Wait for shutdown signal.

        Args:
            timeout: Maximum time to wait

        Returns:
            True if shutdown was signaled, False if timed out
        """
        return self.shutdown_event.wait(timeout)

    def create_managed_thread(self, target: Callable, name: str,
                            component: str = "unknown", daemon: bool = True,
                            cleanup_callback: Callable[[], None] | None = None,
                            args: tuple = (), kwargs: dict[str, Any] | None = None,
                            auto_start: bool = True) -> str | None:
        """
        Create and register a managed thread.

        Args:
            target: Thread target function
            name: Unique thread name
            component: Component that owns the thread
            daemon: Whether thread should be daemon
            cleanup_callback: Optional cleanup function
            args: Arguments for target function
            kwargs: Keyword arguments for target function
            auto_start: Whether to start thread immediately

        Returns:
            Thread name if successful, None otherwise
        """
        try:
            # Create wrapper that checks for shutdown signals
            def managed_target(*args, **kwargs):
                thread_name = getattr(threading.current_thread(), 'thread_manager_name', name)
                logger.debug(f"Managed thread '{thread_name}' started")

                try:
                    # Check if we have a stop event
                    stop_event = getattr(threading.current_thread(), 'stop_event', None)

                    # Call original target with stop_event awareness if needed
                    if stop_event and hasattr(target, '__code__') and 'stop_event' in target.__code__.co_varnames:
                        kwargs = kwargs or {}
                        kwargs['stop_event'] = stop_event

                    return target(*args, **kwargs)

                except Exception as e:
                    logger.error(f"Managed thread '{thread_name}' encountered error: {e}")
                    raise
                finally:
                    logger.debug(f"Managed thread '{thread_name}' finished")

            # Create thread
            thread_obj = threading.Thread(
                target=managed_target,
                name=name,
                daemon=daemon,
                args=args,
                kwargs=kwargs or {}
            )

            # Register thread
            thread_name = self.register_thread(
                name=name,
                thread_obj=thread_obj,
                component=component,
                daemon=daemon,
                cleanup_callback=cleanup_callback
            )

            # Start if requested
            if auto_start:
                if self.start_thread(thread_name):
                    return thread_name
                # Clean up failed thread
                self.unregister_thread(thread_name)
                return None
            return thread_name

        except Exception as e:
            logger.error(f"Failed to create managed thread '{name}': {e}")
            return None

    def unregister_thread(self, name: str) -> bool:
        """
        Unregister a thread (removes from management).

        Args:
            name: Thread name to unregister

        Returns:
            True if unregistered successfully
        """
        with self.lock:
            if name in self.threads:
                thread_info = self.threads[name]

                # Stop thread if still running
                if thread_info.thread_obj.is_alive():
                    logger.warning(f"Unregistering still-running thread '{name}' - attempting to stop")
                    self.stop_thread(name)

                del self.threads[name]
                logger.info(f"Unregistered thread '{name}'")
                return True
            else:
                logger.warning(f"Cannot unregister unknown thread '{name}'")
                return False

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle system signals for graceful shutdown."""
        signal_names: dict[int, str] = {signal.SIGINT: 'SIGINT', signal.SIGTERM: 'SIGTERM'}
        signal_name = signal_names.get(signum, f'Signal {signum}')

        logger.info(f"Received {signal_name} - initiating graceful shutdown")

        # Start shutdown in background thread to avoid blocking signal handler
        shutdown_thread = threading.Thread(
            target=self.shutdown_all,
            name="SignalShutdownHandler",
            daemon=False  # Don't make this daemon so it can complete shutdown
        )
        shutdown_thread.start()


# Global thread manager instance
_global_thread_manager = None
_thread_manager_lock = threading.Lock()

def get_thread_manager() -> ThreadManager:
    """Get the global thread manager instance (singleton pattern)."""
    global _global_thread_manager
    with _thread_manager_lock:
        if _global_thread_manager is None:
            _global_thread_manager = ThreadManager()
        return _global_thread_manager

# Convenience functions for easy integration

def register_thread(name: str, thread_obj: threading.Thread, component: str = "unknown",
                   daemon: bool = True, cleanup_callback: Callable[[], None] | None = None) -> str:
    """Register a thread with the global thread manager."""
    return get_thread_manager().register_thread(name, thread_obj, component, daemon, cleanup_callback)

def create_managed_thread(target: Callable, name: str, component: str = "unknown",
                         daemon: bool = True, cleanup_callback: Callable[[], None] | None = None,
                         args: tuple = (), kwargs: dict[str, Any] | None = None,
                         auto_start: bool = True) -> str | None:
    """Create a managed thread with the global thread manager."""
    return get_thread_manager().create_managed_thread(  # type: ignore
        target, name, component, daemon, cleanup_callback, args, kwargs, auto_start
    )

def shutdown_all_threads(timeout: float | None = None) -> dict[str, bool]:
    """Shutdown all threads managed by the global thread manager."""
    return get_thread_manager().shutdown_all(timeout)

def get_thread_status() -> dict[str, Any]:
    """Get status of all managed threads."""
    return get_thread_manager().get_thread_status()

def is_shutdown_requested() -> bool:
    """Check if shutdown has been requested."""
    return get_thread_manager().is_shutdown_requested()

# Example integration patterns

def example_managed_background_task(stop_event: threading.Event):
    """Example of how to write a background task that respects shutdown signals."""
    logger.info("Background task started")

    while not stop_event.is_set():
        try:
            # Do some work
            time.sleep(1)

            # Check for shutdown signal
            if stop_event.wait(0):  # Non-blocking check
                logger.info("Background task received stop signal")
                break

        except Exception as e:
            logger.error(f"Background task error: {e}")
            break

    logger.info("Background task finished")

def cleanup_example():
    """Example cleanup function."""
    logger.info("Performing cleanup operations...")
    # Clean up resources here

# Test and demonstration
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Testing Thread Management System...")

    # Create managed thread
    if thread_name := create_managed_thread(
        target=example_managed_background_task,
        name="test_background_task",
        component="test_component",
        cleanup_callback=cleanup_example,
        auto_start=True
    ):
        print(f"Created managed thread: {thread_name}")

        # Show thread status
        status = get_thread_status()
        print(f"Thread status: {status}")

        # Let it run for a bit
        time.sleep(3)

        # Shutdown
    results = shutdown_all_threads(timeout=5)
    print(f"Shutdown results: {results}")

    print("Thread management system test completed!")
