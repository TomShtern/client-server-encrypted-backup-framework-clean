#!/usr/bin/env python3
"""
Singleton FletLogCapture - Early Initialization Log Handler

This module provides a singleton logging handler that captures logs from:
1. Flet framework (flet.*) - GUI framework internals
2. Application (FletV2.*) - Application-level logs

Must be imported EARLY in the application lifecycle (before Flet loads)
to ensure all logs are captured.

Usage:
    # In start_with_server.py or main.py (VERY EARLY):
    from Shared.logging.flet_log_capture import get_flet_log_capture
    capture = get_flet_log_capture()  # Initializes and attaches to root logger

    # In views/enhanced_logs.py:
    from Shared.logging.flet_log_capture import get_flet_log_capture
    capture = get_flet_log_capture()
    flet_logs = capture.get_flet_logs()
    app_logs = capture.get_app_logs()
"""

import logging
import contextlib
from datetime import datetime
from typing import List, Dict, Any
from collections import deque


class FletLogCapture(logging.Handler):
    """
    Enhanced logging handler that captures logs from Flet framework and application.

    Features:
    - Separate buffers for Flet framework logs and application logs
    - Rolling buffers with configurable max size
    - Thread-safe operations
    - Timestamp formatting
    - Metadata preservation
    """

    def __init__(self, max_logs: int = 500):
        """
        Initialize log capture handler.

        Args:
            max_logs: Maximum number of logs to store in each buffer
        """
        super().__init__()
        self.max_logs = max_logs

        # Separate buffers for different log sources
        self.flet_logs: deque = deque(maxlen=max_logs)  # flet.* loggers
        self.app_logs: deque = deque(maxlen=max_logs)   # FletV2.* loggers
        self.all_logs: deque = deque(maxlen=max_logs * 2)  # Combined buffer

        # Statistics
        self.total_captured = 0
        self.flet_count = 0
        self.app_count = 0

    def emit(self, record: logging.LogRecord):
        """
        Capture log record and route to appropriate buffer.

        Args:
            record: LogRecord from Python logging system
        """
        with contextlib.suppress(Exception):
            # Format timestamp
            timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

            # Extract logger name and determine source
            logger_name = record.name
            is_flet = logger_name.startswith("flet.")
            is_app = logger_name.startswith("FletV2.") or logger_name.startswith("views.")

            # Build log entry
            log_entry = {
                "time": timestamp,
                "level": record.levelname,
                "component": logger_name,
                "message": self.format(record),
                "timestamp": record.created,
                # Additional metadata
                "thread": record.threadName,
                "filename": record.filename,
                "lineno": record.lineno,
                "funcName": record.funcName,
            }

            # Route to appropriate buffer
            if is_flet:
                self.flet_logs.append(log_entry)
                self.flet_count += 1
            elif is_app:
                self.app_logs.append(log_entry)
                self.app_count += 1

            # Always add to combined buffer
            self.all_logs.append(log_entry)
            self.total_captured += 1

    def get_flet_logs(self) -> List[Dict[str, Any]]:
        """
        Get all captured Flet framework logs.

        Returns:
            List of log dictionaries (newest first)
        """
        return list(reversed(self.flet_logs))

    def get_app_logs(self) -> List[Dict[str, Any]]:
        """
        Get all captured application logs.

        Returns:
            List of log dictionaries (newest first)
        """
        return list(reversed(self.app_logs))

    def get_all_logs(self) -> List[Dict[str, Any]]:
        """
        Get all captured logs (combined).

        Returns:
            List of log dictionaries (newest first)
        """
        return list(reversed(self.all_logs))

    def clear_flet_logs(self):
        """Clear Flet framework logs buffer."""
        self.flet_logs.clear()

    def clear_app_logs(self):
        """Clear application logs buffer."""
        self.app_logs.clear()

    def clear_all(self):
        """Clear all log buffers."""
        self.flet_logs.clear()
        self.app_logs.clear()
        self.all_logs.clear()

    def get_stats(self) -> Dict[str, int]:
        """
        Get capture statistics.

        Returns:
            Dictionary with counts
        """
        return {
            "total_captured": self.total_captured,
            "flet_count": self.flet_count,
            "app_count": self.app_count,
            "flet_buffer_size": len(self.flet_logs),
            "app_buffer_size": len(self.app_logs),
            "all_buffer_size": len(self.all_logs),
        }


# --------------------------------------------------------------------------------------
# SINGLETON INSTANCE
# --------------------------------------------------------------------------------------

_flet_log_capture_instance: FletLogCapture | None = None
_is_attached: bool = False


def get_flet_log_capture() -> FletLogCapture:
    """
    Get the singleton FletLogCapture instance.

    On first call, creates instance and attaches to root logger.
    Subsequent calls return the same instance.

    Returns:
        Singleton FletLogCapture instance
    """
    global _flet_log_capture_instance, _is_attached

    if _flet_log_capture_instance is None:
        # Create singleton instance
        _flet_log_capture_instance = FletLogCapture(max_logs=500)
        _flet_log_capture_instance.setFormatter(logging.Formatter('%(message)s'))

        # Attach to root logger (only once)
        if not _is_attached:
            root_logger = logging.getLogger()
            # Check if already attached (avoid duplicates on hot reload)
            if not any(isinstance(h, FletLogCapture) for h in root_logger.handlers):
                root_logger.addHandler(_flet_log_capture_instance)
                _is_attached = True

                # Optional: Log the initialization
                with contextlib.suppress(Exception):
                    logging.info("[FletLogCapture] Singleton initialized and attached to root logger")

    return _flet_log_capture_instance


def reset_capture():
    """
    Reset the singleton instance (useful for testing).

    WARNING: This will lose all captured logs!
    """
    global _flet_log_capture_instance, _is_attached

    if _flet_log_capture_instance is not None:
        # Remove from root logger
        root_logger = logging.getLogger()
        with contextlib.suppress(Exception):
            root_logger.removeHandler(_flet_log_capture_instance)

    _flet_log_capture_instance = None
    _is_attached = False
