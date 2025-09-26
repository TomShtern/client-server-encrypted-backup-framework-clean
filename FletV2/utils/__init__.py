#!/usr/bin/env python3
"""
Utils Package Init
Initialization file for utils package.
"""
# Import commonly used utility modules
from .database_manager import FletDatabaseManager, create_database_manager
from .debug_setup import get_logger, setup_terminal_debugging
from .performance import (
    AsyncDataLoader,
    AsyncDebouncer,
    BackgroundTaskManager,
    Debouncer,
    MemoryManager,
    PaginationConfig,
    async_debounce,
    cleanup_memory,
    debounce,
    load_async,
    paginate_data,
)
from .server_bridge import ServerBridge, create_server_bridge
from .state_manager import create_state_manager
from .ui_components import create_floating_action_button, create_modern_card
from .user_feedback import (
    show_confirmation,
    show_error_message,
    show_info,
    show_info_message,
    show_input,
    show_success_message,
    show_user_feedback,
    show_warning_message,
)

# Define what should be imported with "from utils import *"
__all__ = [
    "AsyncDataLoader",
    "AsyncDebouncer",
    "BackgroundTaskManager",
    "Debouncer",
    "FletDatabaseManager",
    "MemoryManager",
    "PaginationConfig",
    "ServerBridge",
    "async_debounce",
    "cleanup_memory",
    "create_database_manager",
    "create_floating_action_button",
    "create_modern_card",
    "create_server_bridge",
    "create_state_manager",
    "debounce",
    "get_logger",
    "load_async",
    "paginate_data",
    "setup_terminal_debugging",
    "show_confirmation",
    "show_error_message",
    "show_info",
    "show_info_message",
    "show_input",
    "show_success_message",
    "show_user_feedback",
    "show_warning_message"
]
