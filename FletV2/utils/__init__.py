#!/usr/bin/env python3
"""
Utils Package Init
Initialization file for utils package.
"""
# Import commonly used utility modules
from .debug_setup import setup_terminal_debugging, get_logger
from .server_bridge import ServerBridge, create_server_bridge
from .mock_mode_indicator import create_mock_mode_banner, add_mock_indicator_to_snackbar_message
from .state_manager import create_state_manager
from .database_manager import FletDatabaseManager, create_database_manager
from .mock_data_generator import MockDataGenerator
from .ui_components import create_modern_card, create_floating_action_button
from .user_feedback import (
    show_user_feedback, show_success_message, show_error_message,
    show_info_message, show_warning_message, show_confirmation,
    show_info, show_input
)
from .performance import (
    Debouncer,
    AsyncDebouncer,
    PaginationConfig,
    AsyncDataLoader,
    MemoryManager,
    BackgroundTaskManager,
    debounce,
    async_debounce,
    paginate_data,
    load_async,
    cleanup_memory
)

# Define what should be imported with "from utils import *"
__all__ = [
    "setup_terminal_debugging",
    "get_logger",
    "ServerBridge", 
    "create_server_bridge",
    "create_mock_mode_banner",
    "add_mock_indicator_to_snackbar_message",
    "create_state_manager",
    "FletDatabaseManager",
    "create_database_manager",
    "MockDataGenerator",
    "create_modern_card",
    "create_floating_action_button",
    "show_user_feedback",
    "show_success_message",
    "show_error_message",
    "show_info_message",
    "show_warning_message",
    "show_confirmation",
    "show_info",
    "show_input",
    "Debouncer",
    "AsyncDebouncer",
    "PaginationConfig",
    "AsyncDataLoader",
    "MemoryManager",
    "BackgroundTaskManager",
    "debounce",
    "async_debounce",
    "paginate_data",
    "load_async",
    "cleanup_memory"
]