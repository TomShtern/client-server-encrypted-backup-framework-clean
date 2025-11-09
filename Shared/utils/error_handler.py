#!/usr/bin/env python3
"""
Error Propagation Framework - Centralized Error Management
Provides comprehensive error handling across all 4 layers of the architecture.

This module creates structured error tracking from Web UI → Flask → C++ → Server
as recommended in CLAUDE.md to fix poor error tracking across layers.
"""

import logging
import threading
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for classification."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for systematic classification."""

    # Layer-specific errors
    WEB_UI = "web_ui"
    FLASK_API = "flask_api"
    CPP_CLIENT = "cpp_client"
    PYTHON_SERVER = "python_server"

    # Functional errors
    NETWORK = "network"
    PROTOCOL = "protocol"
    CRYPTO = "crypto"
    FILE_TRANSFER = "file_transfer"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    SUBPROCESS = "subprocess"

    # System errors
    SYSTEM = "system"
    UNKNOWN = "unknown"


class ErrorCode(Enum):
    """Structured error codes for systematic error identification."""

    # Generic errors (1000-1099)
    UNKNOWN_ERROR = 1000
    INVALID_INPUT = 1001
    INVALID_CONFIGURATION = 1002
    TIMEOUT = 1003

    # Network errors (1100-1199)
    CONNECTION_FAILED = 1100
    CONNECTION_TIMEOUT = 1101
    CONNECTION_REFUSED = 1102
    SOCKET_ERROR = 1103
    PORT_IN_USE = 1104
    NETWORK_ERROR = 1105  # General network error for backward compatibility

    # Protocol errors (1200-1299)
    INVALID_PROTOCOL_VERSION = 1200
    INVALID_HEADER = 1201
    INVALID_PAYLOAD = 1202
    MESSAGE_TOO_LARGE = 1203
    PROTOCOL_VIOLATION = 1204

    # Authentication errors (1300-1399)
    AUTH_FAILED = 1300
    INVALID_CREDENTIALS = 1301
    SESSION_EXPIRED = 1302
    CLIENT_NOT_REGISTERED = 1303

    # File transfer errors (1400-1499)
    FILE_NOT_FOUND = 1400
    FILE_ACCESS_DENIED = 1401
    FILE_CORRUPTION = 1402
    TRANSFER_FAILED = 1403
    INSUFFICIENT_SPACE = 1404

    # Crypto errors (1500-1599)
    ENCRYPTION_FAILED = 1500
    DECRYPTION_FAILED = 1501
    KEY_GENERATION_FAILED = 1502
    INVALID_KEY = 1503
    CRYPTO_INIT_FAILED = 1504

    # Subprocess errors (1600-1699)
    SUBPROCESS_FAILED = 1600
    SUBPROCESS_TIMEOUT = 1601
    SUBPROCESS_CRASHED = 1602
    EXECUTABLE_NOT_FOUND = 1603

    # Flask API errors (1700-1799)
    FLASK_INIT_FAILED = 1700
    INVALID_API_REQUEST = 1701
    API_HANDLER_FAILED = 1702
    UPLOAD_FAILED = 1703

    # Configuration errors (1800-1899)
    CONFIG_NOT_FOUND = 1800
    CONFIG_INVALID = 1801
    CONFIG_PERMISSION_DENIED = 1802


@dataclass
class ErrorInfo:
    """Structured error information container."""

    code: ErrorCode
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    layer: str = ""
    component: str = ""
    stack_trace: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    propagation_chain: list[str] = field(default_factory=list)
    error_id: str = field(default_factory=lambda: f"err_{int(time.time())}_{threading.get_ident()}")


class ErrorHandler:
    """
    Centralized error handling and propagation system.

    Features:
    - Structured error classification and tracking
    - Error propagation across architectural layers
    - Real-time error reporting and callbacks
    - Error statistics and analysis
    - Integration with logging systems
    """

    def __init__(self):
        """Initialize the error handler."""
        self.errors: dict[str, ErrorInfo] = {}
        self.error_callbacks: list[Callable[[ErrorInfo], None]] = []
        self.lock = threading.RLock()
        self.error_count_by_category: dict[ErrorCategory, int] = {}
        self.error_count_by_severity: dict[ErrorSeverity, int] = {}

        logger.info("ErrorHandler initialized")

    def register_error_callback(self, callback: Callable[[ErrorInfo], None]):
        """
        Register a callback function to be called when errors occur.

        Args:
            callback: Function that takes ErrorInfo as parameter
        """
        with self.lock:
            self.error_callbacks.append(callback)
            logger.debug(f"Registered error callback: {callback.__name__}")

    def remove_callback(self, callback: Callable[[ErrorInfo], None]):
        """Remove an error callback."""
        with self.lock:
            if callback in self.error_callbacks:
                self.error_callbacks.remove(callback)

    def create_error(
        self,
        code: ErrorCode,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: str = "",
        layer: str = "",
        component: str = "",
        context: dict[str, Any] | None = None,
        include_stack_trace: bool = True,
    ) -> ErrorInfo:
        """
        Create a new structured error.

        Args:
            code: Error code from ErrorCode enum
            message: Human-readable error message
            category: Error category for classification
            severity: Error severity level
            details: Additional error details
            layer: Architectural layer where error occurred
            component: Specific component where error occurred
            context: Additional context information
            include_stack_trace: Whether to include stack trace

        Returns:
            ErrorInfo object with structured error information
        """
        stack_trace = None
        if include_stack_trace:
            stack_trace = traceback.format_exc() if traceback.format_exc() != "NoneType: None\n" else None

        error_info = ErrorInfo(
            code=code,
            category=category,
            severity=severity,
            message=message,
            details=details,
            layer=layer,
            component=component,
            stack_trace=stack_trace,
            context=context or {},
            propagation_chain=[f"{layer}::{component}" if layer and component else "unknown"],
        )

        with self.lock:
            # Store error
            self.errors[error_info.error_id] = error_info

            # Update statistics
            self.error_count_by_category[category] = self.error_count_by_category.get(category, 0) + 1
            self.error_count_by_severity[severity] = self.error_count_by_severity.get(severity, 0) + 1

            # Log error
            log_level = self._get_log_level_for_severity(severity)
            logger.log(log_level, f"[{error_info.error_id}] {code.name}: {message}")
            if details:
                logger.log(log_level, f"[{error_info.error_id}] Details: {details}")

            # Call registered callbacks
            for callback in self.error_callbacks:
                try:
                    callback(error_info)
                except Exception as e:
                    logger.error(f"Error callback failed: {e}")

        return error_info

    def propagate_error(
        self,
        error_info: ErrorInfo,
        new_layer: str,
        new_component: str,
        additional_message: str = "",
        new_severity: ErrorSeverity | None = None,
    ) -> ErrorInfo:
        """
        Propagate an error to a new layer/component.

        Args:
            error_info: Original error information
            new_layer: New layer where error is being handled
            new_component: New component where error is being handled
            additional_message: Additional message for this layer
            new_severity: Optional new severity level

        Returns:
            New ErrorInfo object with propagation information
        """
        with self.lock:
            # Create propagated error
            propagated_error = ErrorInfo(
                code=error_info.code,
                category=error_info.category,
                severity=new_severity or error_info.severity,
                message=f"{error_info.message}" + (f" | {additional_message}" if additional_message else ""),
                details=error_info.details,
                layer=new_layer,
                component=new_component,
                stack_trace=error_info.stack_trace,
                context=error_info.context.copy(),
                propagation_chain=[*error_info.propagation_chain, f"{new_layer}::{new_component}"],
            )

            # Store propagated error
            self.errors[propagated_error.error_id] = propagated_error

            # Log propagation
            logger.warning(
                f"Error {error_info.error_id} propagated to {new_layer}::{new_component} as {propagated_error.error_id}"
            )

            # Call callbacks for propagated error
            for callback in self.error_callbacks:
                try:
                    callback(propagated_error)
                except Exception as e:
                    logger.error(f"Error callback failed during propagation: {e}")

        return propagated_error

    def get_error(self, error_id: str) -> ErrorInfo | None:
        """
        Get error information by ID.

        Args:
            error_id: Error ID to look up

        Returns:
            ErrorInfo object or None if not found
        """
        with self.lock:
            return self.errors.get(error_id)

    def get_errors_by_category(self, category: ErrorCategory) -> list[ErrorInfo]:
        """
        Get all errors of a specific category.

        Args:
            category: Error category to filter by

        Returns:
            List of ErrorInfo objects
        """
        with self.lock:
            return [error for error in self.errors.values() if error.category == category]

    def get_errors_by_severity(self, severity: ErrorSeverity) -> list[ErrorInfo]:
        """
        Get all errors of a specific severity.

        Args:
            severity: Error severity to filter by

        Returns:
            List of ErrorInfo objects
        """
        with self.lock:
            return [error for error in self.errors.values() if error.severity == severity]

    def get_recent_errors(self, hours: int = 1) -> list[ErrorInfo]:
        """
        Get errors from the last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            List of recent ErrorInfo objects
        """
        with self.lock:
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            return [error for error in self.errors.values() if error.timestamp.timestamp() > cutoff_time]

    def get_error_statistics(self) -> dict[str, Any]:
        """
        Get error statistics and analysis.

        Returns:
            Dictionary with error statistics
        """
        with self.lock:
            recent_errors = self.get_recent_errors(24)  # Last 24 hours

            return {
                "total_errors": len(self.errors),
                "recent_errors_24h": len(recent_errors),
                "by_category": dict(self.error_count_by_category),
                "by_severity": dict(self.error_count_by_severity),
                "most_common_category": max(
                    self.error_count_by_category.items(), key=lambda x: x[1], default=(None, 0)
                ),
                "most_severe_recent": max(
                    recent_errors, key=lambda x: list(ErrorSeverity).index(x.severity), default=None
                ),
            }

    def clear_old_errors(self, hours: int = 24):
        """
        Clear errors older than specified hours.

        Args:
            hours: Age threshold in hours
        """
        with self.lock:
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            old_error_ids = [
                error_id
                for error_id, error in self.errors.items()
                if error.timestamp.timestamp() < cutoff_time
            ]

            for error_id in old_error_ids:
                del self.errors[error_id]

            logger.info(f"Cleared {len(old_error_ids)} old errors")

    def format_error_for_display(self, error_info: ErrorInfo, include_stack: bool = False) -> str:
        """
        Format error for user-friendly display.

        Args:
            error_info: Error to format
            include_stack: Whether to include stack trace

        Returns:
            Formatted error string
        """
        formatted = f"[{error_info.severity.value.upper()}] {error_info.code.name}: {error_info.message}"

        if error_info.layer and error_info.component:
            formatted += f"\nLocation: {error_info.layer} -> {error_info.component}"

        if error_info.details:
            formatted += f"\nDetails: {error_info.details}"

        if error_info.propagation_chain and len(error_info.propagation_chain) > 1:
            formatted += f"\nPropagation: {' -> '.join(error_info.propagation_chain)}"

        if include_stack and error_info.stack_trace:
            formatted += f"\nStack Trace:\n{error_info.stack_trace}"

        return formatted

    def _get_log_level_for_severity(self, severity: ErrorSeverity) -> int:
        """Get logging level for error severity."""
        severity_to_log_level = {
            ErrorSeverity.LOW: logging.DEBUG,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL,
        }
        return severity_to_log_level.get(severity, logging.WARNING)


# Global error handler instance
_global_error_handler = None
_error_handler_lock = threading.Lock()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance (singleton pattern)."""
    global _global_error_handler
    with _error_handler_lock:
        if _global_error_handler is None:
            _global_error_handler = ErrorHandler()
        return _global_error_handler


# Convenience functions for common error scenarios


def handle_network_error(
    message: str, details: str = "", component: str = "", severity: ErrorSeverity = ErrorSeverity.HIGH
) -> ErrorInfo:
    """Create a network-related error."""
    return get_error_handler().create_error(
        code=ErrorCode.CONNECTION_FAILED,
        category=ErrorCategory.NETWORK,
        severity=severity,
        message=message,
        details=details,
        layer="network",
        component=component,
    )


def handle_protocol_error(
    message: str, details: str = "", component: str = "", severity: ErrorSeverity = ErrorSeverity.HIGH
) -> ErrorInfo:
    """Create a protocol-related error."""
    return get_error_handler().create_error(
        code=ErrorCode.PROTOCOL_VIOLATION,
        category=ErrorCategory.PROTOCOL,
        severity=severity,
        message=message,
        details=details,
        layer="protocol",
        component=component,
    )


def handle_file_transfer_error(
    message: str, details: str = "", component: str = "", severity: ErrorSeverity = ErrorSeverity.HIGH
) -> ErrorInfo:
    """Create a file transfer-related error."""
    return get_error_handler().create_error(
        code=ErrorCode.TRANSFER_FAILED,
        category=ErrorCategory.FILE_TRANSFER,
        severity=severity,
        message=message,
        details=details,
        layer="file_transfer",
        component=component,
    )


def handle_subprocess_error(
    message: str, details: str = "", component: str = "", severity: ErrorSeverity = ErrorSeverity.HIGH
) -> ErrorInfo:
    """Create a subprocess-related error."""
    return get_error_handler().create_error(
        code=ErrorCode.SUBPROCESS_FAILED,
        category=ErrorCategory.SUBPROCESS,
        severity=severity,
        message=message,
        details=details,
        layer="subprocess",
        component=component,
    )


def handle_flask_api_error(
    message: str, details: str = "", component: str = "", severity: ErrorSeverity = ErrorSeverity.MEDIUM
) -> ErrorInfo:
    """Create a Flask API-related error."""
    return get_error_handler().create_error(
        code=ErrorCode.API_HANDLER_FAILED,
        category=ErrorCategory.FLASK_API,
        severity=severity,
        message=message,
        details=details,
        layer="flask_api",
        component=component,
    )


# Example usage and testing


def test_error_propagation():
    """Test the error propagation framework."""
    print("Testing Error Propagation Framework...")

    handler = get_error_handler()

    # Register a test callback
    def error_callback(error_info: ErrorInfo):
        print(f"Error callback triggered: {error_info.code.name}")

    handler.register_error_callback(error_callback)

    # Create an error in the C++ client layer
    cpp_error = handler.create_error(
        code=ErrorCode.ENCRYPTION_FAILED,
        category=ErrorCategory.CRYPTO,
        severity=ErrorSeverity.HIGH,
        message="AES encryption failed during file processing",
        details="Invalid key length provided",
        layer="cpp_client",
        component="AESWrapper",
        context={"file_size": 1024, "key_length": 16},
    )

    print(f"Created error: {cpp_error.error_id}")

    # Propagate to Flask API layer
    flask_error = handler.propagate_error(
        cpp_error,
        new_layer="flask_api",
        new_component="backup_executor",
        additional_message="Subprocess encryption failed",
    )

    print(f"Propagated to Flask: {flask_error.error_id}")

    # Propagate to Web UI layer
    ui_error = handler.propagate_error(
        flask_error,
        new_layer="web_ui",
        new_component="upload_handler",
        additional_message="File upload failed",
        new_severity=ErrorSeverity.MEDIUM,
    )

    print(f"Propagated to UI: {ui_error.error_id}")

    # Display propagation chain
    print("\nError propagation chain:")
    print(handler.format_error_for_display(ui_error))

    # Get statistics
    stats = handler.get_error_statistics()
    print(f"\nError statistics: {stats}")

    print("Error propagation framework test completed!")


if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    test_error_propagation()
