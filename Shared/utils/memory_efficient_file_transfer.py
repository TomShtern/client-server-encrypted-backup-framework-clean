"""
MEMORY-EFFICIENT FILE TRANSFER MANAGER
======================================

PURPOSE: Enhances file transfer operations with memory management and cleanup
PREVENTS: Memory leaks from partial file accumulation and abandoned transfers
USED BY: FileTransferManager for improved memory management

KEY FEATURES:
- Bounded memory usage for partial file chunks
- Automatic cleanup of abandoned transfers
- Memory pressure monitoring
- Configurable transfer limits
- Comprehensive error handling and resource cleanup

MEMORY LEAKS PREVENTED:
1. Partial file chunks accumulating indefinitely
2. Failed transfers not cleaning up properly
3. Unbounded memory growth with many concurrent transfers
4. File handles not being closed properly

USAGE:
- Replace direct partial_files dict usage with MemoryEfficientTransferManager
- All operations include automatic cleanup and memory bounds
- Monitor memory usage and adjust limits as needed
"""

import logging
import threading
import time
import weakref
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TransferConfig:
    """Configuration for memory-efficient file transfers."""

    max_concurrent_transfers: int = 10
    max_chunks_per_file: int = 10000
    max_chunk_memory_mb: int = 100  # Maximum memory for chunks per transfer
    cleanup_interval_seconds: int = 300  # 5 minutes
    abandoned_transfer_timeout: int = 1800  # 30 minutes
    memory_pressure_threshold_mb: int = 500  # Start cleanup at 500MB


@dataclass
class TransferState:
    """Memory-bounded transfer state for a single file."""

    filename: str
    total_packets: int
    original_size: int
    timestamp: float
    received_chunks: dict[int, bytes]
    client_ref: weakref.ReferenceType[Any] | None  # Weak reference to prevent cycles

    def __post_init__(self):
        # Validate memory constraints
        if self.total_packets > 100000:  # Arbitrary large number
            raise ValueError(f"Too many packets for transfer: {self.total_packets}")

    def add_chunk(self, packet_number: int, chunk_data: bytes, config: TransferConfig | None = None) -> bool:
        """
        Add a chunk to the transfer state with memory bounds checking.

        Args:
            packet_number: Packet number (1-based)
            chunk_data: Chunk data as bytes
            config: Transfer configuration (optional)

        Returns:
            True if chunk was added, False if memory limit exceeded
        """
        if config is None:
            config = TransferConfig()

        # Check if we already have this chunk
        if packet_number in self.received_chunks:
            return True

        # Check memory constraints
        current_memory = sum(len(chunk) for chunk in self.received_chunks.values())
        chunk_size = len(chunk_data)

        # Estimate memory usage if we add this chunk
        estimated_memory = current_memory + chunk_size
        max_memory_bytes = config.max_chunk_memory_mb * 1024 * 1024

        if estimated_memory > max_memory_bytes:
            logger.warning(
                f"Memory limit exceeded for transfer {self.filename}: "
                f"current={current_memory:,}, chunk={chunk_size:,}, "
                f"limit={max_memory_bytes:,}"
            )
            return False

        # Check packet count limits
        if len(self.received_chunks) >= config.max_chunks_per_file:
            logger.warning(
                f"Chunk count limit exceeded for transfer {self.filename}: "
                f"current={len(self.received_chunks)}, "
                f"limit={config.max_chunks_per_file}"
            )
            return False

        self.received_chunks[packet_number] = chunk_data
        self.timestamp = time.time()  # Update timestamp for LRU tracking
        return True

    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes for this transfer."""
        return sum(len(chunk) for chunk in self.received_chunks.values())

    def is_complete(self) -> bool:
        """Check if all packets have been received."""
        expected_packets = set(range(1, self.total_packets + 1))
        received_packets = set(self.received_chunks.keys())
        return received_packets == expected_packets

    def get_missing_packets(self) -> list[int]:
        """Get list of missing packet numbers."""
        expected_packets = set(range(1, self.total_packets + 1))
        received_packets = set(self.received_chunks.keys())
        return sorted(expected_packets - received_packets)


class MemoryEfficientTransferManager:
    """
    Manages file transfers with memory efficiency and automatic cleanup.

    Key features:
    - LRU eviction for memory management
    - Weak references to prevent memory leaks
    - Automatic cleanup of abandoned transfers
    - Memory pressure monitoring
    """

    def __init__(self, config: TransferConfig | None = None):
        self.config = config or TransferConfig()
        self._transfers: OrderedDict[str, TransferState] = OrderedDict()  # LRU cache
        self._lock = threading.RLock()
        self._last_cleanup = time.time()
        self._stats: dict[str, int | float] = {
            "total_transfers": 0,
            "completed_transfers": 0,
            "abandoned_transfers": 0,
            "memory_cleanups": 0,
            "current_memory_mb": 0,
        }

        logger.info(
            f"MemoryEfficientTransferManager initialized: "
            f"max_concurrent={self.config.max_concurrent_transfers}, "
            f"max_memory_mb={self.config.max_chunk_memory_mb}"
        )

        # Start cleanup daemon thread
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_worker, name="TransferCleanup", daemon=True
        )
        self._cleanup_thread.start()

    def create_transfer(
        self, client_id: bytes, filename: str, total_packets: int, original_size: int
    ) -> bool:
        """
        Create a new transfer state with memory bounds checking.

        Args:
            client_id: Client identifier
            filename: Filename being transferred
            total_packets: Total number of packets expected
            original_size: Original file size in bytes

        Returns:
            True if transfer was created, False if limits exceeded
        """
        with self._lock:
            transfer_key = f"{client_id.hex()}:{filename}"

            # Check concurrent transfer limits, evict oldest incomplete transfer if needed
            if (
                len(self._transfers) >= self.config.max_concurrent_transfers
                and not self._evict_oldest_incomplete()
            ):
                logger.warning(
                    f"Concurrent transfer limit exceeded: current={len(self._transfers)}, "
                    f"limit={self.config.max_concurrent_transfers}"
                )
                return False

            # Remove existing transfer if present (restart)
            if transfer_key in self._transfers:
                self._cleanup_transfer(transfer_key, reason="transfer_restart")

            try:
                self._store_transfer_state(transfer_key, filename, total_packets, original_size)
                return True

            except ValueError as e:
                logger.error(f"Failed to create transfer {transfer_key}: {e}")
                return False

    def _create_transfer_state(self, filename: str, total_packets: int, original_size: int) -> TransferState:
        """
        Create a new TransferState instance.

        Args:
            filename: Filename being transferred
            total_packets: Total number of packets expected
            original_size: Original file size in bytes

        Returns:
            TransferState instance
        """
        client_ref = None  # Will be set by calling code
        return TransferState(
            filename=filename,
            total_packets=total_packets,
            original_size=original_size,
            timestamp=time.time(),
            received_chunks={},
            client_ref=client_ref,
        )

    def _store_transfer_state(
        self, transfer_key: str, filename: str, total_packets: int, original_size: int
    ) -> None:
        """
        Store transfer state in the transfers dictionary with LRU tracking.

        Args:
            transfer_key: Transfer identifier
            filename: Filename being transferred
            total_packets: Total number of packets expected
            original_size: Original file size in bytes

        Raises:
            ValueError: If transfer state creation fails
        """
        transfer_state = self._create_transfer_state(filename, total_packets, original_size)

        self._transfers[transfer_key] = transfer_state
        self._transfers.move_to_end(transfer_key)  # Mark as recently used

        self._stats["total_transfers"] += 1
        logger.debug(f"Created transfer: {transfer_key} ({total_packets} packets, {original_size:,} bytes)")

    def add_packet(self, client_id: bytes, filename: str, packet_number: int, chunk_data: bytes) -> bool:
        """
        Add a packet to an existing transfer with memory bounds checking.

        Args:
            client_id: Client identifier
            filename: Filename being transferred
            packet_number: Packet number (1-based)
            chunk_data: Chunk data as bytes

        Returns:
            True if packet was added, False if transfer doesn't exist or limits exceeded
        """
        with self._lock:
            transfer_key = f"{client_id.hex()}:{filename}"

            if transfer_key not in self._transfers:
                logger.warning(f"Transfer not found for packet: {transfer_key}")
                return False

            transfer_state = self._transfers[transfer_key]

            # Add chunk with memory bounds checking
            if not transfer_state.add_chunk(packet_number, chunk_data, self.config):
                return False

            # Mark as recently used (LRU)
            self._transfers.move_to_end(transfer_key)

            # Check if transfer is complete
            if transfer_state.is_complete():
                self._stats["completed_transfers"] += 1
                logger.info(f"Transfer completed: {transfer_key}")

            return True

    def get_transfer_state(self, client_id: bytes, filename: str) -> TransferState | None:
        """
        Get transfer state without modifying LRU order.

        Args:
            client_id: Client identifier
            filename: Filename being transferred

        Returns:
            TransferState or None if not found
        """
        with self._lock:
            transfer_key = f"{client_id.hex()}:{filename}"
            return self._transfers.get(transfer_key)

    def remove_transfer(self, client_id: bytes, filename: str, reason: str = "completed") -> bool:
        """
        Remove a transfer state and clean up memory.

        Args:
            client_id: Client identifier
            filename: Filename being transferred
            reason: Reason for removal (for logging)

        Returns:
            True if transfer was removed, False if not found
        """
        with self._lock:
            transfer_key = f"{client_id.hex()}:{filename}"
            return self._cleanup_transfer(transfer_key, reason)

    def _cleanup_transfer(self, transfer_key: str, reason: str) -> bool:
        """
        Internal method to clean up a transfer.

        Args:
            transfer_key: Transfer identifier
            reason: Reason for cleanup

        Returns:
            True if transfer was cleaned up
        """
        if transfer_key not in self._transfers:
            return False

        transfer_state = self._transfers[transfer_key]
        memory_freed = transfer_state.get_memory_usage()

        del self._transfers[transfer_key]

        if reason == "abandoned":
            self._stats["abandoned_transfers"] += 1

        logger.debug(f"Cleaned up transfer {transfer_key} ({memory_freed:,} bytes, reason: {reason})")

        return True

    def _evict_oldest_incomplete(self) -> bool:
        """
        Evict the oldest incomplete transfer to make room for new ones.

        Returns:
            True if a transfer was evicted, False if no incomplete transfers found
        """
        for transfer_key, transfer_state in list(self._transfers.items()):
            if not transfer_state.is_complete():
                logger.info(f"Evicting oldest incomplete transfer: {transfer_key}")
                return self._cleanup_transfer(transfer_key, "memory_eviction")

        return False  # No incomplete transfers to evict

    def _cleanup_worker(self):
        """
        Background worker that periodically cleans up abandoned transfers.
        """
        while True:
            try:
                time.sleep(self.config.cleanup_interval_seconds)
                self._perform_cleanup()
            except Exception as e:
                logger.error(f"Error in transfer cleanup worker: {e}")

    def _perform_cleanup(self):
        """
        Perform cleanup of abandoned transfers and memory pressure management.
        """
        with self._lock:
            current_time = time.time()
            abandoned_count = 0

            # Find abandoned transfers
            for transfer_key, transfer_state in list(self._transfers.items()):
                age = current_time - transfer_state.timestamp

                if age > self.config.abandoned_transfer_timeout and self._cleanup_transfer(
                    transfer_key, "timeout_abandoned"
                ):
                    abandoned_count += 1

            if abandoned_count > 0:
                self._stats["memory_cleanups"] += 1
                logger.info(f"Cleaned up {abandoned_count} abandoned transfers")

            # Update memory usage statistics
            total_memory = sum(ts.get_memory_usage() for ts in self._transfers.values())
            self._stats["current_memory_mb"] = total_memory // (1024 * 1024)

            # Check memory pressure
            if total_memory > self.config.memory_pressure_threshold_mb * 1024 * 1024:
                logger.warning(f"High memory usage detected: {self._stats['current_memory_mb']}MB")
                # Trigger aggressive cleanup
                self._aggressive_cleanup()

    def _aggressive_cleanup(self):
        """
        Perform aggressive cleanup under memory pressure.
        """
        evicted_count = 0

        # Evict incomplete transfers oldest first
        for transfer_key, transfer_state in list(self._transfers.items()):
            # Merge nested conditions: only attempt cleanup for incomplete transfers,
            # and count eviction only if cleanup succeeded.
            if not transfer_state.is_complete() and self._cleanup_transfer(transfer_key, "memory_pressure"):
                evicted_count += 1

                # Stop when memory is manageable
                total_memory = sum(ts.get_memory_usage() for ts in self._transfers.values())
                if total_memory < self.config.memory_pressure_threshold_mb * 1024 * 1024 * 0.8:
                    break

        if evicted_count > 0:
            logger.warning(f"Aggressive cleanup evicted {evicted_count} transfers due to memory pressure")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get transfer manager statistics.

        Returns:
            Dictionary with current statistics
        """
        with self._lock:
            stats = self._stats.copy()
            stats["active_transfers"] = len(self._transfers)
            stats["max_memory_mb"] = self.config.max_chunk_memory_mb
            stats["last_cleanup"] = self._last_cleanup
            return stats

    def set_client_reference(self, client_id: bytes, filename: str, client_obj):
        """
        Set weak reference to client object for a transfer.

        This should be called after creating a transfer to prevent
        reference cycles and allow proper garbage collection.

        Args:
            client_id: Client identifier
            filename: Filename being transferred
            client_obj: Client object to create weak reference to
        """
        with self._lock:
            transfer_key = f"{client_id.hex()}:{filename}"
            if transfer_key in self._transfers:
                self._transfers[transfer_key].client_ref = weakref.ref(client_obj)

    def shutdown(self):
        """
        Shutdown the transfer manager and clean up all transfers.
        """
        logger.info("Shutting down MemoryEfficientTransferManager")

        with self._lock:
            # Clean up all active transfers
            for transfer_key in list(self._transfers.keys()):
                self._cleanup_transfer(transfer_key, "shutdown")

            logger.info(f"Shutdown complete. Final stats: {self._stats}")


# Global instance for use by the file transfer system
_transfer_manager: MemoryEfficientTransferManager | None = None


def get_transfer_manager() -> MemoryEfficientTransferManager:
    """
    Get the global transfer manager instance.

    Returns:
        MemoryEfficientTransferManager instance
    """
    global _transfer_manager
    if _transfer_manager is None:
        _transfer_manager = MemoryEfficientTransferManager()
    return _transfer_manager


def shutdown_transfer_manager():
    """
    Shutdown the global transfer manager.

    Call this during application shutdown to ensure proper cleanup.
    """
    global _transfer_manager
    if _transfer_manager is not None:
        _transfer_manager.shutdown()
        _transfer_manager = None
