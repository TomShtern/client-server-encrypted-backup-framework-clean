"""
Memory Manager - FletV2 Phase 0 Critical Fix

Prevents memory leaks from event handler accumulation, control reference cycles,
and provides proper cleanup for view transitions.

Priority: CRITICAL - Prevents gradual memory exhaustion and crashes
"""

import weakref
import gc
import logging
import threading
from typing import Dict, Set, List, Any, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Centralized memory management with cleanup tracking.
    Prevents memory leaks through proper lifecycle management.
    """

    def __init__(self):
        self._active_handlers: Dict[str, List[Dict[str, Any]]] = {}
        self._control_references: Dict[str, weakref.ref] = {}
        self._cleanup_callbacks: List[Callable] = []
        self._disposed = False
        self._lock = threading.Lock()
        self._gc_stats = {
            "handlers_registered": 0,
            "controls_tracked": 0,
            "cleanup_callbacks_executed": 0,
            "memory_warnings_detected": 0
        }

    def register_event_handler(self,
                             control_name: str,
                             event_type: str,
                             handler: Callable,
                             control: Any = None) -> str:
        """
        Register event handler with automatic cleanup tracking.

        Args:
            control_name: Name/ID of the control
            event_type: Type of event ('on_click', 'on_change', etc.)
            handler: Event handler function
            control: Optional control reference for weak tracking

        Returns:
            Unique handler ID for cleanup
        """
        if self._disposed:
            logger.warning(f"MemoryManager disposed, cannot register handler: {control_name}.{event_type}")
            return ""

        handler_id = f"{control_name}_{event_type}_{len(self._active_handlers.get(control_name, []))}"

        with self._lock:
            if control_name not in self._active_handlers:
                self._active_handlers[control_name] = []
            self._active_handlers[control_name].append({
                "id": handler_id,
                "handler": handler,
                "event_type": event_type,
                "registered_at": datetime.now(),
                "cleanup_called": False
            })

            # Store weak reference to control if provided
            if control:
                self._control_references[handler_id] = weakref.ref(
                    control, lambda ref: self._cleanup_control_handler(handler_id, ref)
                )

            self._gc_stats["handlers_registered"] += 1
            logger.debug(f"Registered handler: {handler_id} for control: {control_name}")

        return handler_id

    def register_control(self, control_name: str, control: Any) -> str:
        """
        Register control for lifecycle tracking.
        """
        if self._disposed:
            logger.warning(f"MemoryManager disposed, cannot register control: {control_name}")
            return ""

        control_id = f"ctrl_{control_name}_{len(self._control_references)}"

        with self._lock:
            # Store weak reference to prevent memory cycles
            self._control_references[control_id] = weakref.ref(
                control, lambda ref: self._cleanup_control_reference(control_id, ref)
            )
            self._gc_stats["controls_tracked"] += 1

        logger.debug(f"Registered control for tracking: {control_id}")
        return control_id

    def cleanup_control_handlers(self, control_name: str) -> int:
        """
        Clean up all event handlers for a specific control.
        Call this when controls are removed or views are disposed.

        Args:
            control_name: Name of control to clean up

        Returns:
            Number of handlers cleaned up
        """
        if self._disposed:
            return 0

        cleaned_count = 0

        with self._lock:
            handlers = self._active_handlers.get(control_name, [])
            for handler_info in handlers:
                if not handler_info["cleanup_called"]:
                    handler_info["cleanup_called"] = True
                    self._cleanup_single_handler(handler_info["id"])
                    cleaned_count += 1

            # Clear all handlers for this control
            self._active_handlers[control_name] = []

        logger.info(f"Cleaned up {cleaned_count} handlers for control: {control_name}")
        return cleaned_count

    def cleanup_handler(self, handler_id: str) -> bool:
        """
        Clean up specific handler by ID.

        Args:
            handler_id: Unique handler identifier

        Returns:
            True if handler was found and cleaned up
        """
        return self._cleanup_single_handler(handler_id)

    def dispose_all_handlers(self) -> int:
        """
        Clean up ALL registered handlers and controls.
        Call this on view disposal or application shutdown.

        Returns:
            Total number of handlers cleaned up
        """
        if self._disposed:
            return 0

        total_cleaned = 0

        with self._lock:
            # Clean up all handlers
            for control_name, handler_list in list(self._active_handlers.items()):
                for handler_info in handler_list:
                    if not handler_info["cleanup_called"]:
                        self._cleanup_single_handler(handler_info["id"])
                        total_cleaned += 1

            # Clear all tracking
            self._active_handlers.clear()
            self._control_references.clear()

        self._disposed = True

        logger.info(f"MemoryManager disposed - cleaned up {total_cleaned} handlers")

        # Execute cleanup callbacks
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in memory cleanup callback: {e}")
            finally:
                self._gc_stats["cleanup_callbacks_executed"] += 1

        return total_cleaned

    def add_cleanup_callback(self, callback: Callable) -> None:
        """
        Add callback to execute on disposal.
        """
        self._cleanup_callbacks.append(callback)

    def detect_memory_growth(self) -> Dict[str, Any]:
        """
        Detect potential memory leaks through analysis of registered objects.

        Returns:
            Dictionary with memory statistics and warnings
        """
        with self._lock:
            active_handlers_count = sum(len(handlers) for handlers in self._active_handlers.values())
            tracked_controls_count = len(self._control_references)

        # Force garbage collection to get accurate counts
        gc.collect()

        # Memory warning thresholds
        warnings = []
        if active_handlers_count > 50:
            warnings.append(f"High handler count: {active_handlers_count}")
        if tracked_controls_count > 100:
            warnings.append(f"High control count: {tracked_controls_count}")

        # Check for zombie references (weak refs that are dead)
        dead_refs = 0
        for ref in self._control_references.values():
            if ref() is None:
                dead_refs += 1

        if dead_refs > 0:
            warnings.append(f"Dead control references detected: {dead_refs}")

        stats = {
            "active_handlers": active_handlers_count,
            "tracked_controls": tracked_controls_count,
            "dead_references": dead_refs,
            "warnings": warnings,
            "gc_stats": self._gc_stats.copy(),
            "memory_growth_detected": len(warnings) > 0
        }

        if warnings:
            self._gc_stats["memory_warnings_detected"] += 1
            logger.warning(f"Memory leak warnings detected: {warnings}")

        return stats

    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get comprehensive debugging information.
        """
        with self._lock:
            active_handlers_count = sum(len(handlers) for handlers in self._active_handlers.values())
            tracked_controls_count = len(self._control_references)

            # Analyze handler age
            old_handlers = []
            now = datetime.now()
            for handler_list in self._active_handlers.values():
                for handler_info in handler_list:
                    age = (now - handler_info["registered_at"]).total_seconds()
                    if age > 300:  # 5 minutes old
                        old_handlers.append({
                            "id": handler_info["id"],
                            "age_seconds": age,
                            "event_type": handler_info["event_type"]
                        })

            return {
                "active_handlers_count": active_handlers_count,
                "tracked_controls_count": tracked_controls_count,
                "old_handlers": len(old_handlers),
                "gc_stats": self._gc_stats.copy(),
                "disposed": self._disposed,
                "handler_types": list(set(
                    info["event_type"] for handlers in self._active_handlers.values() for info in handlers
                )),
                "oldest_handler_age": max([h["age_seconds"] for h in old_handlers], default=0) if old_handlers else 0
            }

    def _cleanup_single_handler(self, handler_id: str) -> bool:
        """
        Clean up single handler by ID.
        """
        try:
            with self._lock:
                # Find and remove from tracking
                for control_name, handler_list in self._active_handlers.items():
                    for i, handler_info in enumerate(handler_list):
                        if handler_info["id"] == handler_id:
                            handler_info["cleanup_called"] = True
                            del handler_list[i]

                            # Clean up control reference
                            if handler_id in self._control_references:
                                del self._control_references[handler_id]

                            logger.debug(f"Cleaned up handler: {handler_id}")
                            return True

            return False
        except Exception as e:
            logger.error(f"Error cleaning up handler {handler_id}: {e}")
            return False

    def _cleanup_control_handler(self, handler_id: str, weak_ref: weakref.ref) -> None:
        """
        Cleanup callback for weak reference finalization.
        """
        try:
            # This is called when control is garbage collected
            logger.debug(f"Control garbage collected, cleaning handler: {handler_id}")
            self._cleanup_single_handler(handler_id)
        except Exception as e:
            logger.error(f"Error in control cleanup callback: {e}")

    def _cleanup_control_reference(self, control_id: str, weak_ref: weakref.ref) -> None:
        """
        Cleanup callback for control reference finalization.
        """
        try:
            # This is called when control is garbage collected
            logger.debug(f"Control reference finalized: {control_id}")
            with self._lock:
                if control_id in self._control_references:
                    del self._control_references[control_id]
        except Exception as e:
            logger.error(f"Error in control reference cleanup: {e}")

# Global instance for FletV2
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """Get or create global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
        logger.info("Created global MemoryManager instance")
    return _memory_manager

def dispose_memory_manager() -> None:
    """Dispose global memory manager. Call on app shutdown."""
    global _memory_manager
    if _memory_manager:
        _memory_manager.dispose_all_handlers()
        _memory_manager = None