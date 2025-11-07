"""
STREAMING FILE UTILITIES - MEMORY-EFFICIENT FILE OPERATIONS
=================================================================

PURPOSE: Provides memory-efficient file operations for large file handling
PREVENTS: Memory leaks from loading entire files into RAM
USED BY: API server, file transfer manager, and backup executors

KEY FEATURES:
- Streaming hash calculation (fixed-size chunks)
- Memory-bounded file reading
- Proper resource cleanup with context managers
- Configurable buffer sizes for different use cases

MEMORY SAVINGS:
- Hash calculation: O(1) memory instead of O(file_size)
- File validation: Streaming instead of whole-file loading
- Backup operations: Configurable memory limits

USAGE:
- Use calculate_file_hash_streaming() instead of hashlib.sha256(f.read())
- Use read_file_chunks() for processing large files
- All operations include proper cleanup and error handling
"""

import hashlib
import logging
import os
from typing import Optional, Iterator, Union
from pathlib import Path

logger = logging.getLogger(__name__)

# Default chunk size: 64KB - good balance between I/O efficiency and memory usage
DEFAULT_CHUNK_SIZE = 64 * 1024  # 64KB
# Large file chunk size: 1MB - for very large files to reduce I/O overhead
LARGE_FILE_CHUNK_SIZE = 1024 * 1024  # 1MB


def calculate_file_hash_streaming(file_path: str,
                                algorithm: str = 'sha256',
                                chunk_size: Optional[int] = None) -> Optional[str]:
    """
    Calculate file hash using streaming to prevent memory overload.

    This function reads the file in fixed-size chunks rather than loading
    the entire file into memory, making it safe for files of any size.

    Args:
        file_path: Path to the file to hash
        algorithm: Hash algorithm to use ('sha256', 'md5', 'sha1', etc.)
        chunk_size: Size of chunks to read (default: 64KB)

    Returns:
        Hexadecimal hash string or None if error occurs

    Memory Usage: O(chunk_size) instead of O(file_size)

    Example:
        # Old way (memory leak for large files):
        # with open(file_path, 'rb') as f:
        #     file_hash = hashlib.sha256(f.read()).hexdigest()

        # New way (memory efficient):
        file_hash = calculate_file_hash_streaming(file_path, 'sha256')
    """
    if chunk_size is None:
        # Use larger chunks for very large files to improve I/O efficiency
        try:
            file_size = os.path.getsize(file_path)
            chunk_size = LARGE_FILE_CHUNK_SIZE if file_size > 100 * 1024 * 1024 else DEFAULT_CHUNK_SIZE
        except OSError:
            chunk_size = DEFAULT_CHUNK_SIZE

    try:
        # Initialize hash algorithm
        if algorithm.lower() == 'sha256':
            hash_obj = hashlib.sha256()
        elif algorithm.lower() == 'md5':
            hash_obj = hashlib.md5()
        elif algorithm.lower() == 'sha1':
            hash_obj = hashlib.sha1()
        else:
            logger.error(f"Unsupported hash algorithm: {algorithm}")
            return None

        # Process file in chunks to limit memory usage
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hash_obj.update(chunk)

        file_hash = hash_obj.hexdigest()
        logger.debug(f"Calculated {algorithm} hash for {file_path}: {file_hash[:16]}...")
        return file_hash

    except FileNotFoundError:
        logger.error(f"File not found for hashing: {file_path}")
        return None
    except PermissionError:
        logger.error(f"Permission denied accessing file: {file_path}")
        return None
    except OSError as e:
        logger.error(f"OS error accessing file {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calculating hash for {file_path}: {e}")
        return None


def read_file_chunks(file_path: str,
                    chunk_size: int = DEFAULT_CHUNK_SIZE,
                    max_chunks: Optional[int] = None) -> Iterator[bytes]:
    """
    Generator that yields file contents in chunks to limit memory usage.

    Args:
        file_path: Path to the file to read
        chunk_size: Size of each chunk in bytes
        max_chunks: Maximum number of chunks to yield (None for unlimited)

    Yields:
        File content chunks as bytes

    Memory Usage: O(chunk_size) regardless of file size

    Example:
        for chunk in read_file_chunks(large_file_path, chunk_size=1024*1024):
            process_chunk(chunk)  # Process 1MB at a time
    """
    chunk_count = 0

    try:
        with open(file_path, 'rb') as f:
            while True:
                if max_chunks is not None and chunk_count >= max_chunks:
                    break

                chunk = f.read(chunk_size)
                if not chunk:
                    break

                yield chunk
                chunk_count += 1

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except PermissionError:
        logger.error(f"Permission denied accessing file: {file_path}")
        raise
    except OSError as e:
        logger.error(f"OS error reading file {file_path}: {e}")
        raise


def validate_file_size_safe(file_path: str,
                          max_size_bytes: int) -> tuple[bool, Optional[int]]:
    """
    Safely check file size without loading file content.

    Args:
        file_path: Path to the file
        max_size_bytes: Maximum allowed file size

    Returns:
        Tuple of (is_valid, actual_size_or_None)

    Memory Usage: O(1) - only reads file metadata
    """
    try:
        actual_size = os.path.getsize(file_path)
        is_valid = actual_size <= max_size_bytes

        if not is_valid:
            logger.warning(f"File {file_path} exceeds size limit: "
                         f"{actual_size:,} bytes > {max_size_bytes:,} bytes")

        return is_valid, actual_size

    except FileNotFoundError:
        logger.error(f"File not found for size validation: {file_path}")
        return False, None
    except PermissionError:
        logger.error(f"Permission denied accessing file: {file_path}")
        return False, None
    except OSError as e:
        logger.error(f"OS error checking file size {file_path}: {e}")
        return False, None


def calculate_file_crc32_streaming(file_path: str,
                                  chunk_size: int = DEFAULT_CHUNK_SIZE) -> Optional[int]:
    """
    Calculate CRC32 checksum using streaming to prevent memory usage.

    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read

    Returns:
        CRC32 checksum or None if error occurs

    Memory Usage: O(chunk_size) instead of O(file_size)
    """
    try:
        crc_value = 0

        for chunk in read_file_chunks(file_path, chunk_size):
            crc_value = calculate_crc32_chunk(chunk, crc_value)

        logger.debug(f"Calculated CRC32 for {file_path}: 0x{crc_value:08x}")
        return crc_value

    except Exception as e:
        logger.error(f"Error calculating CRC32 for {file_path}: {e}")
        return None


def calculate_crc32_chunk(chunk: bytes, previous_crc: int = 0) -> int:
    """
    Calculate CRC32 for a chunk, continuing from previous CRC value.

    This allows incremental CRC32 calculation for streaming processing.

    Args:
        chunk: Data chunk to calculate CRC32 for
        previous_crc: Previous CRC32 value (default: 0)

    Returns:
        Updated CRC32 value

    Memory Usage: O(1)
    """
    import zlib
    return zlib.crc32(chunk, previous_crc)


class StreamingFileReader:
    """
    Context manager for memory-efficient file reading.

    Provides automatic resource cleanup and chunked reading for large files.
    """

    def __init__(self, file_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.file_handle = None

    def __enter__(self) -> 'StreamingFileReader':
        """Open file handle when entering context."""
        try:
            self.file_handle = open(self.file_path, 'rb')
            return self
        except Exception as e:
            logger.error(f"Failed to open file {self.file_path}: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure file handle is closed when exiting context."""
        if self.file_handle:
            try:
                self.file_handle.close()
            except Exception as e:
                logger.error(f"Error closing file {self.file_path}: {e}")
        # Return False to propagate exceptions, True to suppress them
        return False

    def read_chunk(self) -> Optional[bytes]:
        """
        Read a single chunk from the file.

        Returns:
            Chunk data or None if EOF reached
        """
        if not self.file_handle:
            logger.error("File handle not initialized")
            return None

        try:
            chunk = self.file_handle.read(self.chunk_size)
            return chunk if chunk else None
        except Exception as e:
            logger.error(f"Error reading chunk from {self.file_path}: {e}")
            return None

    def read_all_chunks(self) -> Iterator[bytes]:
        """
        Generator that yields all chunks from the file.

        Yields:
            File chunks as bytes
        """
        while True:
            chunk = self.read_chunk()
            if not chunk:
                break
            yield chunk


# Performance monitoring utilities
class MemoryUsageTracker:
    """
    Simple memory usage tracker for file operations.

    This helps identify memory-efficient patterns during development
    and can be used for monitoring in production.
    """

    def __init__(self):
        self.baseline_memory = self._get_memory_usage()
        self.peak_memory = self.baseline_memory

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            import psutil
            return psutil.Process().memory_info().rss
        except ImportError:
            # psutil not available - can't track memory
            return 0
        except Exception:
            return 0

    def update_peak(self):
        """Update peak memory usage."""
        current = self._get_memory_usage()
        if current > self.peak_memory:
            self.peak_memory = current

    def get_memory_delta(self) -> int:
        """Get memory usage delta from baseline."""
        return self._get_memory_usage() - self.baseline_memory

    def get_peak_delta(self) -> int:
        """Get peak memory usage delta from baseline."""
        return self.peak_memory - self.baseline_memory


def log_memory_efficiency(operation: str, file_size: int, memory_delta: int):
    """
    Log memory efficiency metrics for file operations.

    Args:
        operation: Description of the operation performed
        file_size: Size of the file processed
        memory_delta: Memory usage change during operation
    """
    if file_size > 0:
        efficiency = (file_size / memory_delta) if memory_delta > 0 else float('inf')
        logger.info(f"Memory efficiency - {operation}: "
                   f"File: {file_size:,} bytes, "
                   f"Memory: {memory_delta:,} bytes, "
                   f"Ratio: {efficiency:.1f}x")