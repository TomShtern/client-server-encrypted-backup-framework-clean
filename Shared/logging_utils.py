#!/usr/bin/env python3
"""
Logging Utilities for Client-Server Encrypted Backup Framework
Provides standardized logging setup, dual output, and enhanced logging capabilities
with emoji and color support integration.
"""

import contextlib
import logging
import os
import sys
from typing import Tuple, Optional, Dict, Any, Union, Callable, List
from datetime import datetime
from pathlib import Path

# Try to import enhanced output for emoji/color support
try:
    from .utils.enhanced_output import enhance_existing_logger
    from .utils.enhanced_output import Emojis as EnhancedEmojis, Colors as EnhancedColors
    ENHANCED_OUTPUT_AVAILABLE = True
except ImportError:
    ENHANCED_OUTPUT_AVAILABLE = False
    enhance_existing_logger = None
    EnhancedEmojis = None
    EnhancedColors = None

# Define emoji interface that works with both enhanced and fallback
if ENHANCED_OUTPUT_AVAILABLE and EnhancedEmojis is not None:
    Emojis = EnhancedEmojis  # type: ignore
else:
    # Fallback emoji definitions if enhanced output is not available
    class Emojis:
        SUCCESS = "✅"
        ERROR = "❌"
        WARNING = "⚠️"
        INFO = "ℹ️"
        ROCKET = "🚀"
        GEAR = "⚙️"

# Fallback Colors implementation (no-op colorization) when enhanced colors are not available
if ENHANCED_OUTPUT_AVAILABLE and EnhancedColors is not None:
    Colors = EnhancedColors  # type: ignore
else:
    class Colors:
        _SUPPORTS_COLOR = False

        # Provide attributes expected by callers (no-op strings)
        BOLD = ''
        DIM = ''
        UNDERLINE = ''
        RESET = ''

        @classmethod
        def colorize(cls, text: str, color: str, bold: bool = False) -> str:
            return text

        @classmethod
        def success(cls, text: str, bold: bool = False) -> str:
            return text

        @classmethod
        def error(cls, text: str, bold: bool = False) -> str:
            return text

        @classmethod
        def warning(cls, text: str, bold: bool = False) -> str:
            return text

        @classmethod
        def info(cls, text: str, bold: bool = False) -> str:
            return text

        @classmethod
        def debug(cls, text: str, bold: bool = False) -> str:
            return text


def setup_dual_logging(
    logger_name: str,
    server_type: str,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    console_format: str = '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    file_format: Optional[str] = None,
    log_dir: str = "logs",
    enable_enhanced_output: bool = True
) -> Tuple[logging.Logger, str]:
    """
    Set up dual logging: console and file output with different levels.
    Now with enhanced emoji and color support!
    
    Args:
        logger_name: Name for the logger
        server_type: Type of server (e.g., "backup-server", "api-server")
        console_level: Logging level for console output
        file_level: Logging level for file output
        console_format: Format string for console messages
        file_format: Format string for file messages (defaults to console_format)
        log_dir: Directory to store log files
        enable_enhanced_output: Enable emoji and color output (default: True)
        
    Returns:
        Tuple of (logger, log_file_path)
    """
    if file_format is None:
        file_format = console_format
        
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate log file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{server_type}_{timestamp}.log"
    log_file_path = os.path.join(log_dir, log_filename)
    
    # Console handler with enhanced output support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(console_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Enhance logger with emoji and color support if available and enabled
    if enable_enhanced_output and ENHANCED_OUTPUT_AVAILABLE and enhance_existing_logger is not None:
        with contextlib.suppress(Exception):
            # Disable emojis on Windows to prevent Unicode encoding errors with cp1255
            use_emojis = sys.platform != 'win32'
            enhance_existing_logger(logger, use_colors=True, use_emojis=use_emojis)
    
    # File handler
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(file_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Plain startup messages that will be logged to file (no ANSI/color sequences)
    file_startup_messages = [
        f"=== {server_type.upper()} LOGGING INITIALIZED ===",
        f"Console Level: {logging.getLevelName(console_level)}",
        f"File Level: {logging.getLevelName(file_level)}",
        f"Log File: {log_file_path}",
        "=" * 60,
        f"Live Monitoring: Get-Content {log_file_path} -Wait -Tail 50"
    ]

    # Console-only colored/emoji CODE-MAP (printed to stdout only so file logs remain plain)
    console_lines: List[str] = []
    console_lines.append(Colors.info(f"=== {server_type.upper()} LOGGING INITIALIZED ===", bold=True))
    console_lines.append(Colors.info(f"Console Level: {logging.getLevelName(console_level)}"))
    console_lines.append(Colors.info(f"File Level: {logging.getLevelName(file_level)}"))
    console_lines.append(Colors.debug(f"Log File: {log_file_path}"))
    console_lines.append("" )
    console_lines.append(Colors.BOLD + Colors.UNDERLINE + "CODE MAP: Common status / progress codes" + Colors.RESET)

    # Helper to build colored code lines with emoji
    def codeline(code: str, text: str, emoji: str, color_fn: Callable[..., str]) -> str:
        # color_fn is a Colors.<method> callable that accepts (text, bold=False)
        return color_fn(f" {emoji} {code} - {text}")

    # 1xx informational
    console_lines.append(codeline("1xx", "Informational (100 Continue, 101 Switching Protocols)", Emojis.INFO, Colors.info))

    # 2xx success/ok
    console_lines.append(codeline("200", "OK (Success)", Emojis.SUCCESS, Colors.success))
    console_lines.append(codeline("201", "Created", Emojis.SUCCESS, Colors.success))
    console_lines.append(codeline("202", "Accepted", Emojis.INFO, Colors.info))
    console_lines.append(codeline("204", "No Content", Emojis.INFO, Colors.info))

    # 3xx redirection - informational/neutral
    console_lines.append(codeline("3xx", "Redirection (301/302)", Emojis.ROCKET, Colors.info))

    # 4xx client issues - varying severity
    console_lines.append(codeline("400", "Bad Request", Emojis.WARNING, Colors.warning))
    console_lines.append(codeline("401", "Unauthorized", Emojis.WARNING, Colors.warning))
    console_lines.append(codeline("403", "Forbidden", Emojis.WARNING, Colors.warning))
    console_lines.append(codeline("404", "Not Found", Emojis.ERROR, Colors.error))
    console_lines.append(codeline("408", "Request Timeout", Emojis.WARNING, Colors.warning))
    console_lines.append(codeline("409", "Conflict", Emojis.WARNING, Colors.warning))
    console_lines.append(codeline("413", "Payload Too Large", Emojis.WARNING, Colors.warning))
    console_lines.append(codeline("415", "Unsupported Media Type", Emojis.WARNING, Colors.warning))
    console_lines.append(codeline("429", "Too Many Requests", Emojis.WARNING, Colors.warning))

    # 5xx server errors - red = bad
    console_lines.append(codeline("500", "Internal Server Error", Emojis.ERROR, Colors.error))
    console_lines.append(codeline("502", "Bad Gateway", Emojis.ERROR, Colors.error))
    console_lines.append(codeline("503", "Service Unavailable", Emojis.ERROR, Colors.error))
    console_lines.append(codeline("504", "Gateway Timeout", Emojis.ERROR, Colors.error))

    console_lines.append("" )
    console_lines.append(Colors.debug("=" * 60))
    console_lines.append(Colors.debug(f"Live Monitoring: Get-Content {log_file_path} -Wait -Tail 50"))
    
    # Print the colorful console-only banner (keeps file logs plain)
    try:
        for line in console_lines:
            # Use print so the console shows ANSI/colors when available
            print(line)
    except Exception:
        # Fall back to logging plain lines if printing fails
        for line in console_lines:
            logger.info(line)

    # Log startup messages to file (plain text)
    for msg in file_startup_messages:
        logger.info(msg)
    
    return logger, log_file_path


def create_log_monitor_info(server_type: str, log_file_path: str) -> Dict[str, Any]:
    """
    Create monitoring information for log files.
    
    Args:
        server_type: Type of server
        log_file_path: Path to the log file
        
    Returns:
        Dictionary with monitoring information
    """
    return {
        "server_type": server_type,
        "log_file": log_file_path,
        "created_at": datetime.now().isoformat(),
        "monitor_commands": {
            "tail_logs": f"tail -f {log_file_path}",
            "grep_errors": f"grep -i error {log_file_path}",
            "grep_warnings": f"grep -i warn {log_file_path}"
        }
    }


class EnhancedLogger:
    """
    Enhanced logger wrapper that provides structured logging capabilities.
    """
    
    def __init__(self, component: str, base_logger: logging.Logger):
        self.component = component
        self.base_logger = base_logger
        self._context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs: Any) -> None:
        """Set context variables for this logger."""
        self._context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear all context variables."""
        self._context.clear()
    
    def _log_structured(self, level: int, message: str, **kwargs: Any) -> None:
        """Log a structured message with context."""
        context = self._context.copy()
        context.update(kwargs)
        
        # Log as human-readable for console with context information
        structured_msg = f"[{self.component}] {message}"
        if context:
            structured_msg += f" | Context: {context}"
            
        self.base_logger.log(level, structured_msg)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with context."""
        self._log_structured(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with context."""
        self._log_structured(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with context."""
        self._log_structured(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with context."""
        self._log_structured(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with context."""
        self._log_structured(logging.CRITICAL, message, **kwargs)


def create_enhanced_logger(component: str, base_logger: logging.Logger) -> EnhancedLogger:
    """
    Create an enhanced logger with structured logging capabilities.
    
    Args:
        component: Component name for logging context
        base_logger: Base Python logger to wrap
        
    Returns:
        Enhanced logger instance
    """
    return EnhancedLogger(component, base_logger)


def log_performance_metrics(logger: logging.Logger, operation: str, duration_ms: float, success: bool = True, **kwargs: Any) -> None:
    """
    Log performance metrics for operations.
    
    Args:
        logger: Logger to use
        operation: Operation name
        duration_ms: Duration in milliseconds
        success: Whether the operation was successful
        **kwargs: Additional context
    """
    context: Dict[str, Any] = kwargs | {
        "operation": operation,
        "duration_ms": duration_ms,
        "success": success,
        "performance_metric": True
    }
    
    status = "completed" if success else "failed"
    logger.info(f"⚡ Performance: {operation} {status} in {duration_ms:.2f}ms", extra=context)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with standard configuration.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    return logging.getLogger(name)


def configure_root_logger(level: int = logging.INFO):
    """
    Configure the root logger with basic settings.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


# Convenience functions for quick setup
def quick_console_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Quickly create a console-only logger.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Console logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:  # Only add handler if none exist
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


def quick_file_logger(name: str, filename: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Quickly create a file-only logger.
    
    Args:
        name: Logger name
        filename: Log file name
        level: Logging level
        
    Returns:
        File logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:  # Only add handler if none exist
        handler = logging.FileHandler(filename, mode='a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


if __name__ == "__main__":
    # Test the logging utilities
    print("Testing logging utilities...")
    
    # Test dual logging setup
    logger, log_file = setup_dual_logging(
        logger_name="test_logger",
        server_type="test-server",
        console_level=logging.INFO,
        file_level=logging.DEBUG
    )
    
    # Test enhanced logger
    enhanced = create_enhanced_logger("test-component", logger)
    enhanced.set_context(user_id="test_user", session_id="test_session")
    
    # Test logging
    logger.info("Standard logger test message")
    enhanced.info("Enhanced logger test message")
    enhanced.error("Test error message", error_code="TEST_001")
    
    # Test performance logging
    log_performance_metrics(logger, "test_operation", 123.45, status="success")
    
    print("Logging utilities test completed!")
    print(f"Log file created: {log_file}")
