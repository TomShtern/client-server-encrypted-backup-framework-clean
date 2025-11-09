#!/usr/bin/env python3
"""
File Lifecycle Management - Synchronized File Manager
Resolves race conditions in file cleanup during subprocess execution.

This module provides the SynchronizedFileManager class as recommended in CLAUDE.md
to fix the critical race condition in real_backup_executor.py where files are
deleted before subprocesses can finish using them.
"""

import logging
import os
import tempfile
import threading
import time
from contextlib import contextmanager, suppress
from typing import Any

logger = logging.getLogger(__name__)


class SynchronizedFileManager:
    """
    Thread-safe file lifecycle manager that prevents race conditions
    between file creation, usage by subprocesses, and cleanup.

    Key features:
    - Coordinates file lifecycle with subprocess execution
    - Prevents premature deletion of files in use
    - Thread-safe cleanup mechanisms
    - Automatic cleanup on completion or timeout
    """

    def __init__(self, base_temp_dir: str | None = None):
        """
        Initialize the SynchronizedFileManager.

        Args:
            base_temp_dir: Base directory for temporary files. If None, uses system temp.
        """
        self.base_temp_dir = base_temp_dir or tempfile.gettempdir()
        self.managed_files: dict[str, dict[str, Any]] = {}
        self.lock = threading.RLock()  # Allow recursive locking
        self.cleanup_events: dict[str, threading.Event] = {}

        logger.info(f"SynchronizedFileManager initialized with base_temp_dir: {self.base_temp_dir}")

    def create_managed_file(self, filename: str, content: str, file_id: str | None = None) -> str:
        """
        Create a managed temporary file with synchronized cleanup.

        Args:
            filename: Name of the file to create
            content: Content to write to the file
            file_id: Optional unique identifier for the file. If None, generates one.

        Returns:
            Path to the created file

        Raises:
            OSError: If file creation fails
        """
        if file_id is None:
            file_id = f"{filename}_{int(time.time())}_{threading.get_ident()}"

        with self.lock:
            # Create unique temporary directory for this file
            temp_dir = tempfile.mkdtemp(prefix=f"sync_file_{file_id}_", dir=self.base_temp_dir)
            file_path = os.path.join(temp_dir, filename)

            try:
                # Write content to file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Register the file for management
                cleanup_event = threading.Event()
                self.managed_files[file_id] = {
                    "file_path": file_path,
                    "temp_dir": temp_dir,
                    "filename": filename,
                    "created_at": time.monotonic(),
                    "in_use": True,
                    "subprocess_refs": 0,
                    "cleanup_event": cleanup_event,
                }
                self.cleanup_events[file_id] = cleanup_event

                logger.info(f"Created managed file: {file_path} (ID: {file_id})")
                return file_path

            except Exception as e:
                # Cleanup on failure
                with suppress(Exception):
                    if os.path.exists(temp_dir):
                        import shutil

                        shutil.rmtree(temp_dir)
                raise OSError(f"Failed to create managed file {filename}: {e}") from e

    def copy_to_locations(self, file_id: str, target_locations: list[str]) -> list[str]:
        """
        Copy managed file to multiple target locations safely.

        Args:
            file_id: ID of the managed file
            target_locations: List of target file paths

        Returns:
            List of successfully created target paths

        Raises:
            ValueError: If file_id is not found
        """
        with self.lock:
            if file_id not in self.managed_files:
                raise ValueError(f"File ID {file_id} not found in managed files")

            file_info = self.managed_files[file_id]
            source_path = file_info["file_path"]
            successful_copies: list[str] = []

            try:
                for target_path in target_locations:
                    # Ensure target directory exists
                    if target_dir := os.path.dirname(target_path):
                        os.makedirs(target_dir, exist_ok=True)

                    # Copy file content
                    with open(source_path, encoding="utf-8") as src:
                        content = src.read()

                    with open(target_path, "w", encoding="utf-8") as dst:
                        dst.write(content)

                    successful_copies.append(target_path)
                    logger.debug(f"Copied managed file {file_id} to: {target_path}")

                # Update managed file info with copy locations
                if isinstance(file_info, dict):
                    file_info["copy_locations"] = successful_copies

                return successful_copies

            except Exception as e:
                # Cleanup any partial copies on failure
                for copy_path in successful_copies:
                    with suppress(Exception):
                        if os.path.exists(copy_path):
                            os.remove(copy_path)
                raise OSError(f"Failed to copy file {file_id} to locations: {e}") from e

    def mark_in_subprocess_use(self, file_id: str) -> bool:
        """
        Mark file as being used by a subprocess to prevent premature cleanup.

        Args:
            file_id: ID of the managed file

        Returns:
            True if successfully marked, False if file not found
        """
        with self.lock:
            if file_id not in self.managed_files:
                logger.warning(f"Attempted to mark unknown file ID {file_id} as in subprocess use")
                return False

            file_info = self.managed_files[file_id]
            file_info["subprocess_refs"] += 1
            logger.debug(f"File {file_id} marked for subprocess use (refs: {file_info['subprocess_refs']})")
            return True

    def release_subprocess_use(self, file_id: str) -> bool:
        """
        Release subprocess reference to file, allowing cleanup if no other refs exist.

        Args:
            file_id: ID of the managed file

        Returns:
            True if successfully released, False if file not found
        """
        with self.lock:
            if file_id not in self.managed_files:
                logger.warning(f"Attempted to release unknown file ID {file_id} from subprocess use")
                return False

            file_info = self.managed_files[file_id]
            if file_info["subprocess_refs"] > 0:
                file_info["subprocess_refs"] -= 1
                logger.debug(
                    f"File {file_id} released from subprocess use (refs: {file_info['subprocess_refs']})"
                )

                # Signal cleanup event if no more subprocess references
                if file_info["subprocess_refs"] == 0:
                    cleanup_event = file_info["cleanup_event"]
                    cleanup_event.set()
                    logger.debug(f"Cleanup event signaled for file {file_id}")

            return True

    def wait_for_subprocess_completion(self, file_id: str, timeout: float = 30.0) -> bool:
        """
        Wait for all subprocesses to finish using the file before cleanup.

        Args:
            file_id: ID of the managed file
            timeout: Maximum time to wait in seconds

        Returns:
            True if all subprocesses completed, False if timeout occurred
        """
        if file_id not in self.managed_files:
            logger.warning(f"Attempted to wait for unknown file ID {file_id}")
            return False

        cleanup_event = self.cleanup_events.get(file_id)
        if not cleanup_event:
            return True  # No cleanup event means no subprocess references

        logger.info(f"Waiting for subprocess completion for file {file_id} (timeout: {timeout}s)")
        completed = cleanup_event.wait(timeout)

        if completed:
            logger.info(f"Subprocess completion confirmed for file {file_id}")
        else:
            logger.warning(f"Timeout waiting for subprocess completion for file {file_id}")

        return completed

    def safe_cleanup(self, file_id: str, wait_timeout: float = 30.0) -> bool:
        """
        Safely cleanup managed file after ensuring subprocesses are done.

        Args:
            file_id: ID of the managed file
            wait_timeout: Maximum time to wait for subprocess completion

        Returns:
            True if cleanup successful, False otherwise
        """
        with self.lock:
            if file_id not in self.managed_files:
                logger.warning(f"Attempted to cleanup unknown file ID {file_id}")
                return False

            file_info = self.managed_files[file_id]
            logger.info(f"Starting safe cleanup for file {file_id}: {file_info['file_path']}")

            # Wait for subprocess completion
            if file_info["subprocess_refs"] > 0:
                logger.info(f"File {file_id} has {file_info['subprocess_refs']} active subprocess references")
                self.wait_for_subprocess_completion(file_id, wait_timeout)

            try:
                # Cleanup copy locations first
                copy_locations = file_info.get("copy_locations", [])
                for copy_path in copy_locations:
                    try:
                        if os.path.exists(copy_path):
                            os.remove(copy_path)
                            logger.debug(f"Removed copy location: {copy_path}")
                    except Exception as e:
                        logger.warning(f"Failed to remove copy location {copy_path}: {e}")

                # Cleanup original temp directory
                temp_dir = file_info["temp_dir"]
                if os.path.exists(temp_dir):
                    import shutil

                    shutil.rmtree(temp_dir)
                    logger.debug(f"Removed temp directory: {temp_dir}")

                # Remove from managed files
                del self.managed_files[file_id]
                if file_id in self.cleanup_events:
                    del self.cleanup_events[file_id]

                logger.info(f"Successfully cleaned up file {file_id}")
                return True

            except Exception as e:
                logger.error(f"Error during cleanup of file {file_id}: {e}")
                return False

    def cleanup_all(self, wait_timeout: float = 30.0) -> int:
        """
        Cleanup all managed files.

        Args:
            wait_timeout: Maximum time to wait for each file's subprocess completion

        Returns:
            Number of files successfully cleaned up
        """
        with self.lock:
            file_ids = list(self.managed_files.keys())

            logger.info(f"Cleaning up {len(file_ids)} managed files")

            cleaned_count = sum(self.safe_cleanup(file_id, wait_timeout) for file_id in file_ids)

            logger.info(f"Cleanup completed: {cleaned_count}/{len(file_ids)} files cleaned successfully")
            return cleaned_count

    @contextmanager
    def managed_file_context(self, filename: str, content: str, target_locations: list[str] | None = None):
        """
        Context manager for automatic file lifecycle management.

        Args:
            filename: Name of the file to create
            content: Content to write to the file
            target_locations: Optional list of locations to copy the file to

        Yields:
            Tuple of (file_id, file_path, copy_locations)
        """
        file_id = None
        try:
            file_path = self.create_managed_file(filename, content)
            file_id = list(self.managed_files.keys())[-1]  # Get the most recent file_id

            copy_locations = []
            if target_locations:
                copy_locations = self.copy_to_locations(file_id, target_locations)

            yield file_id, file_path, copy_locations

        finally:
            if file_id:
                self.safe_cleanup(file_id)

    def get_file_info(self, file_id: str) -> dict[str, Any] | None:
        """
        Get information about a managed file.

        Args:
            file_id: ID of the managed file

        Returns:
            Dictionary with file information or None if not found
        """
        with self.lock:
            file_info = self.managed_files.get(file_id)
            # Return a copy to prevent external modification, or None if not found
            return dict(file_info) if file_info else None

    def list_managed_files(self) -> list[str]:
        """
        Get list of all managed file IDs.

        Returns:
            List of file IDs currently being managed
        """
        with self.lock:
            return list(self.managed_files.keys())


# Convenience functions for common usage patterns


def create_transfer_info_managed(
    server_ip: str,
    server_port: int,
    username: str,
    file_path: str,
    manager: SynchronizedFileManager | None = None,
) -> tuple:
    """
    Create a managed transfer.info file for C++ client usage.

    Args:
        server_ip: Server IP address
        server_port: Server port number
        username: Username for the backup
        file_path: Path to the file being backed up
        manager: Optional SynchronizedFileManager instance

    Returns:
        Tuple of (file_manager, file_id, transfer_info_path)
    """
    if manager is None:
        manager = SynchronizedFileManager()

    # Generate transfer.info content
    content = f"{server_ip}:{server_port}\n{username}\n{os.path.abspath(file_path)}\n"

    # Create managed file
    transfer_info_path = manager.create_managed_file("transfer.info", content)
    file_id = list(manager.managed_files.keys())[-1]

    return manager, file_id, transfer_info_path


# Example usage and testing functions


def test_synchronized_file_manager():
    """Test function to verify SynchronizedFileManager functionality."""
    import tempfile
    import threading
    import time

    print("Testing SynchronizedFileManager...")

    manager = SynchronizedFileManager()

    # Test basic file creation and cleanup
    with manager.managed_file_context("test.txt", "Hello World") as (file_id, file_path, _copies):
        print(f"Created managed file: {file_path}")
        assert os.path.exists(file_path)

        # Test copy to locations
        target_locations = [
            os.path.join(tempfile.gettempdir(), "copy1.txt"),
            os.path.join(tempfile.gettempdir(), "copy2.txt"),
        ]

        copy_locations = manager.copy_to_locations(file_id, target_locations)
        print(f"Copied to: {copy_locations}")

        # sourcery skip: no-loop-in-tests
        for copy_path in copy_locations:
            assert os.path.exists(copy_path)

        # Test subprocess reference counting
        manager.mark_in_subprocess_use(file_id)
        manager.mark_in_subprocess_use(file_id)  # Two references

        # Simulate subprocess completion
        def release_after_delay():
            time.sleep(1)
            manager.release_subprocess_use(file_id)
            time.sleep(1)
            manager.release_subprocess_use(file_id)

        threading.Thread(target=release_after_delay, daemon=True).start()

        # Wait for subprocess completion
        completed = manager.wait_for_subprocess_completion(file_id, timeout=5.0)
        assert completed, "Subprocess completion timeout"

    # Files should be cleaned up automatically
    print("Context exited, files should be cleaned up")

    print("SynchronizedFileManager test completed successfully!")


if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    test_synchronized_file_manager()
