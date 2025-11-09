import importlib
import logging
import os
import sys
import traceback
from datetime import datetime
from functools import lru_cache

# Global flag to ensure setup runs only once
_debug_setup_done = False


@lru_cache(maxsize=1)
def _resolve_debug_mode() -> bool:
    """Determine whether debug mode is enabled without triggering circular imports."""
    flet_config = None
    if __package__:
        try:
            from .. import config as flet_config  # type: ignore
        except ImportError:
            flet_config = None

    if flet_config and hasattr(flet_config, "DEBUG_MODE"):
        return bool(flet_config.DEBUG_MODE)

    try:
        root_config = importlib.import_module("config")
    except ModuleNotFoundError:
        root_config = None

    if root_config and hasattr(root_config, "DEBUG_MODE"):
        return bool(root_config.DEBUG_MODE)

    return False


# Enhanced formatter with more context
class EnhancedFormatter(logging.Formatter):
    """Custom formatter with enhanced context information."""

    def format(self, record) -> str:
        # Add timestamp with microseconds
        record.asctime = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Add module and line number for better tracing
        if hasattr(record, "module") and hasattr(record, "lineno"):
            record.location = f"{record.module}:{record.lineno}"
        else:
            record.location = "unknown"

        # Add function name if available
        record.function = record.funcName if hasattr(record, "funcName") else "unknown"

        # Format the message with enhanced context
        log_message = super().format(record)

        # Add stack trace for errors and warnings
        if (
            record.levelno >= logging.WARNING
            and hasattr(record, "exc_info")
            and record.exc_info
            and record.exc_info != (None, None, None)
        ):
            # Add stack trace for better debugging
            tb_lines = traceback.format_exception(record.exc_info[0], record.exc_info[1], record.exc_info[2])
            tb_text = "".join(tb_lines)
            log_message += f"\nStack Trace:\n{tb_text}"

        return log_message


def setup_terminal_debugging(log_level: int = logging.INFO, logger_name: str | None = None) -> logging.Logger:
    """
    Set up centralized terminal debugging for FletV2 with enhanced context.

    Args:
        log_level: Logging level (default: INFO, but will be overridden by DEBUG_MODE)
        logger_name: Name for the logger (default: calling module name)

    Returns:
        Configured logger instance
    """
    global _debug_setup_done

    # Determine effective log level based on debug mode configuration
    debug_mode_enabled = _resolve_debug_mode()
    log_level = logging.INFO if debug_mode_enabled else logging.WARNING

    if not _debug_setup_done:
        # Create enhanced formatter
        formatter = EnhancedFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(location)s:%(function)s] - %(message)s"
        )

        # Configure Python's logging module with enhanced formatting
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)

        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(handler)

        # Configure third-party library loggers to reduce noise (applied regardless of DEBUG_MODE)
        # matplotlib produces hundreds of font scanning debug logs
        logging.getLogger("matplotlib").setLevel(logging.ERROR)
        logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

        # PIL produces debug logs for every plugin import
        logging.getLogger("PIL").setLevel(logging.ERROR)
        logging.getLogger("PIL.Image").setLevel(logging.ERROR)

        # Flet produces many internal debug events, keep at INFO for useful logs
        logging.getLogger("flet").setLevel(logging.WARNING)

        # Python server components - reduce database connection spam
        logging.getLogger("python_server.server.database").setLevel(logging.ERROR)  # Only show errors
        logging.getLogger("python_server.server.database").propagate = False  # Prevent duplication
        logging.getLogger("python_server.server.server").setLevel(logging.WARNING)  # Reduce server debug logs
        logging.getLogger("python_server.server.server").propagate = False
        logging.getLogger("observability").setLevel(logging.ERROR)  # Reduce structured logging noise
        logging.getLogger("Shared.utils.thread_manager").setLevel(
            logging.ERROR
        )  # Reduce thread management logs
        logging.getLogger("Shared.utils.process_monitor").setLevel(
            logging.WARNING
        )  # Reduce process monitor logs
        logging.getLogger("Shared.utils.process_monitor_gui").setLevel(logging.WARNING)

        # Application-specific loggers - reduce verbosity for cleaner output (allow override below)
        logging.getLogger("views.dashboard").setLevel(
            logging.ERROR
        )  # Suppress dashboard logs unless explicitly overridden
        logging.getLogger("views").setLevel(logging.WARNING)  # Suppress all view debug logs
        logging.getLogger("FletV2.main").setLevel(logging.WARNING)  # Reduce main app logs to warnings only
        logging.getLogger("utils.server_bridge").setLevel(logging.WARNING)  # Reduce bridge logs
        logging.getLogger("FletV2.state_manager").setLevel(logging.ERROR)  # Suppress state manager debug logs

        # Suppress verbose server initialization logs
        logging.getLogger("python_server.server.database_migrations").setLevel(logging.WARNING)
        logging.getLogger("python_server.server.file_transfer").setLevel(logging.WARNING)
        logging.getLogger("python_server.server.gui_integration").setLevel(logging.WARNING)
        logging.getLogger("Shared.sentry_config").setLevel(logging.WARNING)

        # Suppress code map and verbose initialization output from server components
        logging.getLogger("Shared.logging_utils").setLevel(logging.ERROR)  # Suppress code map output
        logging.getLogger("api_server.cyberbackup_api_server").setLevel(
            logging.WARNING
        )  # Reduce API server logs
        logging.getLogger("python_server.server.server").setLevel(
            logging.WARNING
        )  # Reduce backup server logs

        # Suppress GUI thread initialization details
        logging.getLogger("MainThread").setLevel(logging.WARNING)  # Suppress thread-related logs

        # Implement global exception hook with enhanced context
        def custom_exception_hook(exc_type, exc_value, exc_traceback):
            """Global exception handler to catch all uncaught exceptions with full context."""
            # Allow KeyboardInterrupt to work normally
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            # Log all other uncaught exceptions with full traceback and context
            logger = logging.getLogger("FletV2.exception_handler")

            # Get additional context from the traceback
            if exc_traceback:
                # Get the frame where the exception occurred
                tb_frame = exc_traceback.tb_frame
                filename = tb_frame.f_code.co_filename
                line_number = exc_traceback.tb_lineno
                function_name = tb_frame.f_code.co_name

                # Log with enhanced context
                logger.critical(
                    f"Uncaught exception in {filename}:{line_number} in function '{function_name}': {exc_value}",
                    exc_info=(exc_type, exc_value, exc_traceback),
                )
            else:
                logger.critical(
                    f"Uncaught exception: {exc_value}", exc_info=(exc_type, exc_value, exc_traceback)
                )

        # Set the custom exception hook
        sys.excepthook = custom_exception_hook
        _debug_setup_done = True

        # Conditional override: allow targeted dashboard diagnostics without increasing global verbosity
        if os.environ.get("FLET_DASHBOARD_DEBUG") == "1":  # pragma: no cover - diagnostic mode
            logging.getLogger("views.dashboard").setLevel(logging.WARNING)
            logging.getLogger("views.dashboard").warning(
                "[DASHBOARD_DEBUG] FLET_DASHBOARD_DEBUG=1 -> elevating dashboard logger to WARNING"
            )

        setup_logger = logging.getLogger("FletV2.debug_setup")
        setup_logger.info("Enhanced terminal debugging setup complete")
        setup_logger.debug(f"Logging level: {logging.getLevelName(log_level)}")
        setup_logger.debug(f"Root logger configured with handlers: {len(root_logger.handlers)}")

    # Create logger instance
    logger = logging.getLogger(logger_name or __name__)
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Create a configured logger for consistent logging across the application.

    Args:
        name (str): Name of the logger, typically __name__

    Returns:
        logging.Logger: Configured logger instance with enhanced context
    """
    logger = logging.getLogger(name)

    # Only set level if not already configured (respect levels set in setup_terminal_debugging)
    if logger.level == logging.NOTSET:
        debug_mode_enabled = _resolve_debug_mode()
        log_level = logging.INFO if debug_mode_enabled else logging.WARNING

        logger.setLevel(log_level)

    # Ensure the logger has the enhanced formatter
    if logger.handlers:
        for handler in logger.handlers:
            if not isinstance(handler.formatter, EnhancedFormatter):
                handler.setFormatter(
                    EnhancedFormatter(
                        "%(asctime)s - %(name)s - %(levelname)s - [%(location)s:%(function)s] - %(message)s"
                    )
                )
    else:
        # Create handler if none exist
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            EnhancedFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(location)s:%(function)s] - %(message)s"
            )
        )
        logger.addHandler(handler)

    return logger


def log_function_entry(logger: logging.Logger, function_name: str, *args, **kwargs) -> None:
    """
    Log function entry with parameters (without sensitive data).

    Args:
        logger: Logger instance
        function_name: Name of the function
        *args: Positional arguments
        **kwargs: Keyword arguments
    """
    # Filter out sensitive parameters
    safe_args = []
    for i, arg in enumerate(args):
        if i < 3:  # Only log first few args
            arg_str = f"{str(arg)[:50]}..." if len(str(arg)) > 50 else str(arg)
            safe_args.append(f"arg{i}={arg_str}")

    safe_kwargs = {}
    for key, value in list(kwargs.items())[:3]:  # Only log first few kwargs
        if all(sensitive not in key.lower() for sensitive in ["password", "secret", "key", "token"]):
            value_str = f"{str(value)[:50]}..." if len(str(value)) > 50 else str(value)
            safe_kwargs[key] = value_str

    params = ", ".join(safe_args + [f"{k}={v}" for k, v in safe_kwargs.items()])
    logger.debug(f"Entering {function_name}({params})")


def log_function_exit(logger: logging.Logger, function_name: str, result=None) -> None:
    """
    Log function exit with result.

    Args:
        logger: Logger instance
        function_name: Name of the function
        result: Function result (if applicable)
    """
    if result is not None:
        result_str = f"{str(result)[:100]}..." if len(str(result)) > 100 else str(result)
        logger.debug(f"Exiting {function_name} -> {result_str}")
    else:
        logger.debug(f"Exiting {function_name}")


def log_performance_timing(
    logger: logging.Logger, operation_name: str, start_time: float, end_time: float
) -> None:
    """
    Log performance timing for operations.

    Args:
        logger: Logger instance
        operation_name: Name of the operation
        start_time: Start timestamp
        end_time: End timestamp
    """
    duration = end_time - start_time
    logger.info(f"Performance timing: {operation_name} took {duration:.4f} seconds")
