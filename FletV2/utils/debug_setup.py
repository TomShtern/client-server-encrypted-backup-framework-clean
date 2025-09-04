import logging
import sys
import traceback
from typing import Optional
from datetime import datetime

# Global flag to ensure setup runs only once
_debug_setup_done = False

# Enhanced formatter with more context
class EnhancedFormatter(logging.Formatter):
    """Custom formatter with enhanced context information."""
    
    def format(self, record):
        # Add timestamp with microseconds
        record.asctime = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Add module and line number for better tracing
        if hasattr(record, 'module') and hasattr(record, 'lineno'):
            record.location = f"{record.module}:{record.lineno}"
        else:
            record.location = "unknown"
        
        # Add function name if available
        if hasattr(record, 'funcName'):
            record.function = record.funcName
        else:
            record.function = "unknown"
        
        # Format the message with enhanced context
        log_message = super().format(record)
        
        # Add stack trace for errors and warnings
        if record.levelno >= logging.WARNING and hasattr(record, 'exc_info') and record.exc_info:
            # Add stack trace for better debugging
            tb_lines = traceback.format_exception(*record.exc_info)
            tb_text = ''.join(tb_lines)
            log_message += f"\nStack Trace:\n{tb_text}"
        
        return log_message


def setup_terminal_debugging(log_level: int = logging.DEBUG, logger_name: Optional[str] = None) -> logging.Logger:
    """
    Set up centralized terminal debugging for FletV2 with enhanced context.
    
    Args:
        log_level: Logging level (default: DEBUG)
        logger_name: Name for the logger (default: calling module name)
        
    Returns:
        Configured logger instance
    """
    global _debug_setup_done
    
    if not _debug_setup_done:
        # Create enhanced formatter
        formatter = EnhancedFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(location)s:%(function)s] - %(message)s'
        )
        
        # Configure Python's logging module with enhanced formatting
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(handler)
        
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
                    exc_info=(exc_type, exc_value, exc_traceback)
                )
            else:
                logger.critical(
                    f"Uncaught exception: {exc_value}",
                    exc_info=(exc_type, exc_value, exc_traceback)
                )
        
        # Set the custom exception hook
        sys.excepthook = custom_exception_hook
        _debug_setup_done = True
        
        setup_logger = logging.getLogger("FletV2.debug_setup")
        setup_logger.info("Enhanced terminal debugging setup complete")
        setup_logger.debug(f"Logging level: {logging.getLevelName(log_level)}")
        setup_logger.debug(f"Root logger configured with handlers: {len(root_logger.handlers)}")
    
    # Create logger instance
    logger = logging.getLogger(logger_name or __name__)
    return logger


def get_logger(name):
    """
    Create a configured logger for consistent logging across the application.
    
    Args:
        name (str): Name of the logger, typically __name__
        
    Returns:
        logging.Logger: Configured logger instance with enhanced context
    """
    logger = logging.getLogger(name)
    
    # Ensure the logger has the enhanced formatter
    if logger.handlers:
        for handler in logger.handlers:
            if not isinstance(handler.formatter, EnhancedFormatter):
                handler.setFormatter(
                    EnhancedFormatter(
                        '%(asctime)s - %(name)s - %(levelname)s - [%(location)s:%(function)s] - %(message)s'
                    )
                )
    
    return logger


def log_function_entry(logger, function_name, *args, **kwargs):
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
            arg_str = str(arg)[:50] + "..." if len(str(arg)) > 50 else str(arg)
            safe_args.append(f"arg{i}={arg_str}")
    
    safe_kwargs = {}
    for key, value in list(kwargs.items())[:3]:  # Only log first few kwargs
        if not any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
            value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            safe_kwargs[key] = value_str
    
    params = ", ".join(safe_args + [f"{k}={v}" for k, v in safe_kwargs.items()])
    logger.debug(f"Entering {function_name}({params})")


def log_function_exit(logger, function_name, result=None):
    """
    Log function exit with result.
    
    Args:
        logger: Logger instance
        function_name: Name of the function
        result: Function result (if applicable)
    """
    if result is not None:
        result_str = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
        logger.debug(f"Exiting {function_name} -> {result_str}")
    else:
        logger.debug(f"Exiting {function_name}")


def log_performance_timing(logger, operation_name, start_time, end_time):
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