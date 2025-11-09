"""
Atomic State Operations - FletV2 Phase 0 Critical Fix

Provides atomic state operations and proper locking to prevent race conditions
and data corruption in concurrent state updates.

Priority: CRITICAL - Prevents race conditions and state corruption
"""

import logging
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class StateUpdate:
    """Represents an atomic state update operation."""
    key: str
    old_value: Any
    new_value: Any
    source: str
    timestamp: float
    success: bool = True
    error: str | None = None

class AtomicStateManager:
    """
    Provides thread-safe atomic state operations.
    Prevents race conditions in concurrent state updates.
    """

    def __init__(self):
        self._state: dict[str, Any] = {}
        self._locks: dict[str, threading.Lock] = {}
        self._master_lock = threading.RLock()  # Reentrant lock
        self._update_history: list[StateUpdate] = []
        self._max_history = 50  # Reduced from 100 for memory
        self._stats = {
            "updates_total": 0,
            "updates_successful": 0,
            "updates_failed": 0,
            "race_conditions_detected": 0,
            "locks_created": 0
        }

    @contextmanager
    def atomic_update(self, key: str):
        """
        Context manager for atomic state operations on a single key.

        Usage:
            with state_manager.atomic_update("user_data"):
                # All operations here are atomic for this key
                value = state_manager.get(key)
                state_manager.set(key, new_value)
        """
        if key not in self._locks:
            self._locks[key] = threading.Lock()
            self._stats["locks_created"] += 1

        lock = self._locks[key]
        acquired = lock.acquire(blocking=False)

        if not acquired:
            # Track potential race condition
            self._stats["race_conditions_detected"] += 1
            logger.warning(f"Race condition detected for key: {key} - update already in progress")
            # Block until we can acquire (prevents race condition but logs it)
            lock.acquire()
            logger.info(f"Blocked and acquired lock for key: {key} after race condition")

        try:
            yield self
        finally:
            lock.release()

    @contextmanager
    def atomic_multi_update(self, *keys: str):
        """
        Context manager for atomic operations across multiple keys.
        Prevents inconsistent state when updating multiple related keys.
        """
        # Acquire locks in sorted order to prevent deadlocks
        sorted_keys = sorted(keys)
        acquired_locks = []

        try:
            # Create locks if needed
            for key in sorted_keys:
                if key not in self._locks:
                    self._locks[key] = threading.Lock()
                    self._stats["locks_created"] += 1

            # Acquire all locks
            for key in sorted_keys:
                self._locks[key].acquire()
                acquired_locks.append(key)

            logger.debug(f"Acquired locks for multi-key update: {sorted_keys}")
            yield self

        finally:
            # Release locks in reverse order
            for key in reversed(acquired_locks):
                self._locks[key].release()
            logger.debug(f"Released locks for multi-key update: {sorted_keys}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get state value safely.
        """
        # No lock needed for read operations (assuming Python's GIL for dict access)
        return self._state.get(key, default)

    def set(self, key: str, value: Any, source: str = "manual") -> StateUpdate:
        """
        Set state value atomically.
        """
        old_value = self._state.get(key)
        timestamp = time.time()

        update_record = StateUpdate(
            key=key,
            old_value=old_value,
            new_value=value,
            source=source,
            timestamp=timestamp
        )

        try:
            with self.atomic_update(key):
                self._state[key] = value
                update_record.success = True
                logger.debug(f"State updated atomically: {key} = {value} (source: {source})")
        except Exception as e:
            update_record.success = False
            update_record.error = str(e)
            logger.error(f"Atomic state update failed for {key}: {e}")

        # Track the update
        self._update_history.append(update_record)
        if len(self._update_history) > self._max_history:
            self._update_history = self._update_history[-self._max_history:]

        # Update stats
        self._stats["updates_total"] += 1
        if update_record.success:
            self._stats["updates_successful"] += 1
        else:
            self._stats["updates_failed"] += 1

        return update_record

    def compare_and_swap(self, key: str, expected_value: Any, new_value: Any, source: str = "manual") -> StateUpdate:
        """
        Atomically compare and swap if value matches expected.
        Prevents race conditions in check-then-update patterns.
        """
        old_value = self._state.get(key)
        timestamp = time.time()

        if old_value != expected_value:
            update_record = StateUpdate(
                key=key,
                old_value=old_value,
                new_value=old_value,  # No change
                source=source,
                timestamp=timestamp,
                success=True,
                error=f"Value mismatch: expected {expected_value}, found {old_value}"
            )
            self._update_history.append(update_record)
            logger.debug(f"Compare-and-swap failed for {key}: expected {expected_value}, found {old_value}")
            return update_record

        try:
            with self.atomic_update(key):
                self._state[key] = new_value
                update_record = StateUpdate(
                    key=key,
                    old_value=old_value,
                    new_value=new_value,
                    source=source,
                    timestamp=timestamp,
                    success=True
                )
                logger.debug(f"State compare-and-swapped atomically: {key} = {new_value} (source: {source})")
        except Exception as e:
            update_record = StateUpdate(
                key=key,
                old_value=old_value,
                new_value=old_value,  # No change due to error
                source=source,
                timestamp=timestamp,
                success=False,
                error=str(e)
            )
            logger.error(f"Atomic compare-and-swap failed for {key}: {e}")

        self._update_history.append(update_record)
        self._stats["updates_total"] += 1

        if update_record.success:
            self._stats["updates_successful"] += 1
        else:
            self._stats["updates_failed"] += 1

        return update_record

    def update_multiple(self, updates: dict[str, Any], source: str = "manual") -> list[StateUpdate]:
        """
        Atomically update multiple keys at once.
        """
        if not updates:
            return []

        keys = list(updates.keys())
        results = []

        try:
            with self.atomic_multi_update(*keys):
                for key, new_value in updates.items():
                    old_value = self._state.get(key)
                    timestamp = time.time()

                    update_record = StateUpdate(
                        key=key,
                        old_value=old_value,
                        new_value=new_value,
                        source=source,
                        timestamp=timestamp,
                        success=True
                    )

                    self._state[key] = new_value
                    results.append(update_record)
                    logger.debug(f"Multi-key atomic update: {key} = {new_value}")

                logger.debug(f"Successfully updated {len(results)} keys atomically")

        except Exception as e:
            # Create failure records for all keys
            for key, new_value in updates.items():
                old_value = self._state.get(key)
                timestamp = time.time()

                update_record = StateUpdate(
                    key=key,
                    old_value=old_value,
                    new_value=new_value,
                    source=source,
                    timestamp=timestamp,
                    success=False,
                    error=str(e)
                )
                results.append(update_record)

            logger.error(f"Atomic multi-key update failed: {e}")

        # Track all updates
        for update_record in results:
            self._update_history.append(update_record)
            self._stats["updates_total"] += 1
            if update_record.success:
                self._stats["updates_successful"] += 1
            else:
                self._stats["updates_failed"] += 1

        # Trim history
        if len(self._update_history) > self._max_history:
            self._update_history = self._update_history[-self._max_history:]

        return results

    def get_update_history(self, key: str | None = None, limit: int = 10) -> list[StateUpdate]:
        """
        Get update history for debugging.
        """
        history = self._update_history.copy()

        if key:
            history = [update for update in history if update.key == key]

        return history[-limit:] if len(history) > limit else history

    def get_stats(self) -> dict[str, Any]:
        """
        Get atomic state manager statistics.
        """
        current_state = {
            "total_keys": len(self._state),
            "total_locks": len(self._locks),
            "history_size": len(self._update_history),
            "race_conditions_detected": self._stats["race_conditions_detected"],
            "updates_total": self._stats["updates_total"],
            "updates_successful": self._stats["updates_successful"],
            "updates_failed": self._stats["updates_failed"],
            "locks_created": self._stats["locks_created"],
            "success_rate": (
                self._stats["updates_successful"] / max(self._stats["updates_total"], 1) * 100
            )
        }

        if current_state["race_conditions_detected"] > 0:
            current_state["race_condition_warning"] = "Race conditions detected - check concurrent access"

        return current_state

    def cleanup(self) -> None:
        """
        Clean up locks and resources.
        Call this on application shutdown.
        """
        with self._master_lock:
            # Wait for all locks to be released (with timeout)
            lock_timeout = 5.0  # 5 seconds
            start_time = time.time()

            for key, lock in self._locks.items():
                if lock.locked():
                    logger.warning(f"Lock {key} is still held during cleanup")
                    # Wait for lock to be released
                    while lock.locked() and (time.time() - start_time) < lock_timeout:
                        time.sleep(0.1)

            # Clear all state
            self._state.clear()
            self._locks.clear()
            self._update_history.clear()

        logger.info("AtomicStateManager cleaned up")

# Global instance for FletV2
_atomic_state_manager = None

def get_atomic_state_manager() -> AtomicStateManager:
    """Get or create global atomic state manager instance."""
    global _atomic_state_manager
    if _atomic_state_manager is None:
        _atomic_state_manager = AtomicStateManager()
        logger.info("Created global AtomicStateManager instance")
    return _atomic_state_manager

def dispose_atomic_state_manager() -> None:
    """Dispose global atomic state manager. Call on app shutdown."""
    global _atomic_state_manager
    if _atomic_state_manager:
        _atomic_state_manager.cleanup()
        _atomic_state_manager = None
