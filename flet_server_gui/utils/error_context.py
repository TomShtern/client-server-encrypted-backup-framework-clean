"""error_context.py

Error Context Utility for Centralized Error Boundary System
===========================================================

Provides utilities for capturing, formatting, and managing error information
in a user-friendly and developer-friendly manner. Integrates with the existing
correlation ID and logging systems for seamless error tracking.

Features:
- Capture detailed error context including stack traces
- Format errors for both user and developer consumption  
- Generate correlation IDs for error tracking
- Integration with existing logging and tracing systems
- Support for error severity classification
- Context information for better debugging
"""
from __future__ import annotations

import traceback
import inspect
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Union
from datetime import datetime

from .trace_center import get_trace_center


@dataclass
class ErrorContext:
    """Comprehensive error context for debugging and user feedback."""
    
    # Core error information
    exception: Exception
    error_type: str
    error_message: str
    
    # Context information
    operation: Optional[str] = None
    component: Optional[str] = None
    user_message: Optional[str] = None
    
    # Technical details
    stack_trace: str = ""
    local_variables: Dict[str, Any] = field(default_factory=dict)
    function_name: Optional[str] = None
    file_name: Optional[str] = None
    line_number: Optional[int] = None
    
    # Tracking information
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    severity: str = "error"  # error, warning, critical
    
    # Additional metadata
    meta: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_exception(
        cls,
        exception: Exception,
        operation: Optional[str] = None,
        component: Optional[str] = None,
        user_message: Optional[str] = None,
        capture_locals: bool = False,
        correlation_id: Optional[str] = None
    ) -> "ErrorContext":
        """Create ErrorContext from an exception with optional context."""
        
        # Generate correlation ID if not provided
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        # Extract exception details
        error_type = type(exception).__name__
        error_message = str(exception)
        
        # Capture stack trace
        stack_trace = traceback.format_exc()
        
        # Extract location information from traceback
        tb = exception.__traceback__
        function_name = None
        file_name = None
        line_number = None
        local_vars = {}
        
        if tb:
            # Get the most recent frame (where exception occurred)
            while tb.tb_next:
                tb = tb.tb_next
            
            frame = tb.tb_frame
            function_name = frame.f_code.co_name
            file_name = frame.f_code.co_filename
            line_number = tb.tb_lineno
            
            # Capture local variables if requested
            if capture_locals:
                local_vars = cls._sanitize_locals(frame.f_locals)
        
        # Generate user-friendly message if not provided
        if user_message is None:
            user_message = cls._generate_user_message(error_type, error_message, operation)
        
        # Determine severity
        severity = cls._determine_severity(exception)
        
        return cls(
            exception=exception,
            error_type=error_type,
            error_message=error_message,
            operation=operation,
            component=component,
            user_message=user_message,
            stack_trace=stack_trace,
            local_variables=local_vars,
            function_name=function_name,
            file_name=file_name,
            line_number=line_number,
            correlation_id=correlation_id,
            severity=severity
        )
    
    @staticmethod
    def _sanitize_locals(local_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize local variables for safe serialization and display."""
        sanitized = {}
        
        for key, value in local_vars.items():
            # Skip private variables and common non-essential variables
            if key.startswith('_') or key in ['self', 'cls', 'page', 'event']:
                continue
            
            try:
                # Convert to string representation, limiting length
                str_value = str(value)
                if len(str_value) > 200:
                    str_value = str_value[:200] + "..."
                sanitized[key] = str_value
            except Exception:
                sanitized[key] = "<unable to serialize>"
        
        return sanitized
    
    @staticmethod
    def _generate_user_message(error_type: str, error_message: str, operation: Optional[str]) -> str:
        """Generate a user-friendly error message."""
        
        # Common error type mappings
        user_friendly_messages = {
            "FileNotFoundError": "The requested file could not be found.",
            "PermissionError": "Permission denied. Please check file permissions.",
            "ConnectionError": "Unable to connect to the server. Please check your connection.",
            "TimeoutError": "The operation timed out. Please try again.",
            "ValueError": "Invalid input provided. Please check your data.",
            "KeyError": "Required information is missing.",
            "AttributeError": "An internal error occurred while processing your request.",
            "TypeError": "Invalid data type encountered during processing.",
            "RuntimeError": "An unexpected error occurred during processing.",
        }
        
        # Get user-friendly message or use generic fallback
        base_message = user_friendly_messages.get(error_type, "An unexpected error occurred.")
        
        # Add operation context if available
        if operation:
            return f"Error during {operation.lower()}: {base_message}"
        
        return base_message
    
    @staticmethod
    def _determine_severity(exception: Exception) -> str:
        """Determine error severity based on exception type."""
        
        critical_errors = {
            "MemoryError", "SystemExit", "KeyboardInterrupt", 
            "SystemError", "OSError"
        }
        
        warning_errors = {
            "UserWarning", "DeprecationWarning", "FutureWarning",
            "FileExistsError"
        }
        
        error_type = type(exception).__name__
        
        if error_type in critical_errors:
            return "critical"
        elif error_type in warning_errors:
            return "warning"
        else:
            return "error"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ErrorContext to dictionary for serialization."""
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "operation": self.operation,
            "component": self.component,
            "user_message": self.user_message,
            "function_name": self.function_name,
            "file_name": self.file_name,
            "line_number": self.line_number,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "local_variables": self.local_variables,
            "meta": self.meta
        }
    
    def to_clipboard_text(self) -> str:
        """Format error information for clipboard copying."""
        lines = [
            f"Error Report - {self.timestamp}",
            f"Correlation ID: {self.correlation_id}",
            "",
            f"Operation: {self.operation or 'Unknown'}",
            f"Component: {self.component or 'Unknown'}",
            f"Error Type: {self.error_type}",
            f"Error Message: {self.error_message}",
            "",
            "Stack Trace:",
            self.stack_trace,
        ]
        
        if self.local_variables:
            lines.extend([
                "",
                "Local Variables:",
                ""
            ])
            for key, value in self.local_variables.items():
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
    
    def log_error(self, logger_name: str = "error_boundary") -> None:
        """Log the error using the trace center."""
        trace_center = get_trace_center()
        
        # Log the error with full context
        trace_center.emit(
            type="ERROR_BOUNDARY",
            level="ERROR",
            message=f"{self.error_type}: {self.error_message}",
            meta={
                "operation": self.operation,
                "component": self.component,
                "function_name": self.function_name,
                "file_name": self.file_name,
                "line_number": self.line_number,
                "severity": self.severity,
                "local_variables_count": len(self.local_variables),
                "stack_trace_lines": len(self.stack_trace.split('\n')) if self.stack_trace else 0,
                **self.meta
            },
            correlation_id=self.correlation_id
        )


class ErrorFormatter:
    """Utility class for formatting errors in different contexts."""
    
    @staticmethod
    def format_for_user(context: ErrorContext) -> str:
        """Format error message for end users."""
        return context.user_message or context.error_message
    
    @staticmethod
    def format_for_developer(context: ErrorContext) -> str:
        """Format error message for developers with technical details."""
        return f"{context.error_type}: {context.error_message}"
    
    @staticmethod
    def format_summary(context: ErrorContext) -> str:
        """Format a brief error summary."""
        operation = f" during {context.operation}" if context.operation else ""
        return f"{context.error_type}{operation}: {context.user_message}"
    
    @staticmethod
    def format_technical_details(context: ErrorContext) -> List[str]:
        """Format technical details as a list of lines."""
        details = []
        
        if context.function_name:
            location = f"{context.function_name}()"
            if context.file_name:
                location += f" in {context.file_name}"
            if context.line_number:
                location += f" at line {context.line_number}"
            details.append(f"Location: {location}")
        
        details.append(f"Error Type: {context.error_type}")
        details.append(f"Correlation ID: {context.correlation_id}")
        details.append(f"Timestamp: {context.timestamp}")
        
        if context.local_variables:
            details.append(f"Local Variables: {len(context.local_variables)} captured")
        
        return details


def create_error_context(
    exception: Exception,
    operation: Optional[str] = None,
    component: Optional[str] = None,
    user_message: Optional[str] = None,
    capture_locals: bool = False,
    correlation_id: Optional[str] = None
) -> ErrorContext:
    """Convenience function to create ErrorContext from exception."""
    return ErrorContext.from_exception(
        exception=exception,
        operation=operation,
        component=component,
        user_message=user_message,
        capture_locals=capture_locals,
        correlation_id=correlation_id
    )
