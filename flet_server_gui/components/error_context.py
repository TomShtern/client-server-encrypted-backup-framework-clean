"""error_context.py

Error Context and Formatting for Professional Error Handling
==========================================================

Provides structured error context management and professional formatting
for error presentations. This module defines the ErrorContext class that
captures comprehensive error information and the ErrorFormatter class
that formats this information for both user-facing and technical displays.

Design Principles:
- Comprehensive error metadata capture
- Separation of user-friendly and technical information
- Flexible formatting for different display contexts
- Integration with Python's exception system
- Serializable for logging and reporting
"""

from __future__ import annotations

import traceback
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels for categorization."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorContext:
    """Structured context for error information."""
    
    def __init__(
        self,
        error: Exception,
        operation: Optional[str] = None,
        component: Optional[str] = None,
        user_message: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.timestamp = datetime.now()
        self.error = error
        self.operation = operation
        self.component = component
        self.user_message = user_message
        self.severity = severity
        self.metadata = metadata or {}
        
        # Extract exception information
        self.exception_type = type(error).__name__
        self.exception_message = str(error)
        self.stack_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        
        # Extract file and line information from the top of the stack
        self.file_name = None
        self.line_number = None
        if error.__traceback__:
            tb = error.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
            self.file_name = tb.tb_frame.f_code.co_filename
            self.line_number = tb.tb_lineno
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "operation": self.operation,
            "component": self.component,
            "user_message": self.user_message,
            "severity": self.severity.value,
            "metadata": self.metadata,
            "file_name": self.file_name,
            "line_number": self.line_number
        }
    
    def to_clipboard_text(self) -> str:
        """Format error context for clipboard copying."""
        lines = [
            f"Error: {self.exception_type}",
            f"Message: {self.exception_message}",
            f"Operation: {self.operation or 'N/A'}",
            f"Component: {self.component or 'N/A'}",
            f"Severity: {self.severity.value}",
            f"Timestamp: {self.timestamp.isoformat()}",
            f"File: {self.file_name or 'Unknown'}",
            f"Line: {self.line_number or 'Unknown'}",
        ]
        
        if self.metadata:
            lines.append("Metadata:")
            for key, value in self.metadata.items():
                lines.append(f"  {key}: {value}")
        
        lines.append("\nStack Trace:")
        lines.append(self.stack_trace)
        
        return "\n".join(lines)


class ErrorFormatter:
    """Professional error formatting for different display contexts."""
    
    @staticmethod
    def format_for_user(error_context: ErrorContext) -> str:
        """Format error for user-friendly display."""
        if error_context.user_message:
            return error_context.user_message
        
        # Default user-friendly messages based on common error types
        default_messages = {
            "FileNotFoundError": "The requested file could not be found.",
            "PermissionError": "Access to the requested resource was denied.",
            "ConnectionError": "Unable to connect to the server. Please check your connection.",
            "TimeoutError": "The operation timed out. Please try again.",
            "ValueError": "An invalid value was provided.",
            "TypeError": "An unexpected type was encountered.",
        }
        
        return default_messages.get(
            error_context.exception_type,
            "An unexpected error occurred. Please try again or contact support if the problem persists."
        )
    
    @staticmethod
    def format_technical_details(error_context: ErrorContext) -> List[str]:
        """Format technical details for developers."""
        details = [
            f"Error Type: {error_context.exception_type}",
            f"Error Message: {error_context.exception_message}",
            f"Operation: {error_context.operation or 'N/A'}",
            f"Component: {error_context.component or 'N/A'}",
            f"Severity: {error_context.severity.value}",
            f"Timestamp: {error_context.timestamp.isoformat()}",
        ]
        
        if error_context.file_name:
            details.append(f"File: {error_context.file_name}")
        if error_context.line_number:
            details.append(f"Line: {error_context.line_number}")
        
        if error_context.metadata:
            details.append("Metadata:")
            for key, value in error_context.metadata.items():
                details.append(f"  {key}: {value}")
        
        return details
    
    @staticmethod
    def format_for_logging(error_context: ErrorContext) -> str:
        """Format error for logging."""
        return (
            f"[{error_context.timestamp.isoformat()}] "
            f"{error_context.severity.value.upper()} "
            f"{error_context.exception_type}: {error_context.exception_message} "
            f"(Operation: {error_context.operation or 'N/A'}, "
            f"Component: {error_context.component or 'N/A'})"
        )


# Convenience functions for creating error contexts
def create_error_context(
    error: Exception,
    operation: Optional[str] = None,
    component: Optional[str] = None,
    user_message: Optional[str] = None,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    **metadata
) -> ErrorContext:
    """Convenience function to create an error context."""
    return ErrorContext(
        error=error,
        operation=operation,
        component=component,
        user_message=user_message,
        severity=severity,
        metadata=metadata
    )


def create_from_exception_info(
    exc_type: type,
    exc_value: Exception,
    exc_traceback: Any,
    operation: Optional[str] = None,
    component: Optional[str] = None,
    user_message: Optional[str] = None,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    **metadata
) -> ErrorContext:
    """Create error context from exception info (sys.exc_info() format)."""
    # Attach traceback to exception if not already attached
    if not hasattr(exc_value, '__traceback__'):
        exc_value.__traceback__ = exc_traceback
    return create_error_context(
        error=exc_value,
        operation=operation,
        component=component,
        user_message=user_message,
        severity=severity,
        **metadata
    )