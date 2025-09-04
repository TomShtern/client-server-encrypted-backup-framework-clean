import logging
import sys
from typing import Optional

# Global flag to ensure setup runs only once
_debug_setup_done = False

def setup_terminal_debugging(log_level: int = logging.DEBUG, logger_name: Optional[str] = None) -> logging.Logger:
    """
    Set up centralized terminal debugging for FletV2.
    
    Args:
        log_level: Logging level (default: DEBUG)
        logger_name: Name for the logger (default: calling module name)
        
    Returns:
        Configured logger instance
    """
    global _debug_setup_done
    
    if not _debug_setup_done:
        # Configure Python's logging module
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stdout,
            force=True  # Override any existing configuration
        )
        
        # Implement global exception hook
        def custom_exception_hook(exc_type, exc_value, exc_traceback):
            """Global exception handler to catch all uncaught exceptions."""
            # Allow KeyboardInterrupt to work normally
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            # Log all other uncaught exceptions with full traceback
            logger = logging.getLogger("FletV2.exception_handler")
            logger.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Set the custom exception hook
        sys.excepthook = custom_exception_hook
        _debug_setup_done = True
        
        setup_logger = logging.getLogger("FletV2.debug_setup")
        setup_logger.info("Terminal debugging setup complete")
        setup_logger.debug(f"Logging level: {logging.getLevelName(log_level)}")
    
    # Create logger instance
    logger = logging.getLogger(logger_name or __name__)
    return logger

def get_logger(name):
    """
    Create a configured logger for consistent logging across the application.
    
    Args:
        name (str): Name of the logger, typically __name__
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
