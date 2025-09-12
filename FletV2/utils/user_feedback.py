#!/usr/bin/env python3
"""
DEPRECATED: Centralized User Feedback Utilities for FletV2
This module has been deprecated. Please use utils.dialog_consolidation_helper instead.

Provides consistent user feedback patterns across the application.
"""

import warnings
from typing import Optional
import flet as ft

# Import the consolidated functions
from utils.dialog_consolidation_helper import (
    show_user_feedback as _show_user_feedback,
    show_success_message as _show_success_message,
    show_error_message as _show_error_message,
    show_info_message as _show_info_message,
    show_warning_message as _show_warning_message
)

def show_user_feedback(page: ft.Page, message: str, is_error: bool = False, action_label: Optional[str] = None) -> None:
    """
    DEPRECATED: Show centralized user feedback using Flet's SnackBar.
    This function has been moved to utils.dialog_consolidation_helper.
    
    Args:
        page: Flet page instance
        message: Message to display to user
        is_error: Whether this is an error message (changes color)
        action_label: Optional action button label
    """
    warnings.warn(
        "show_user_feedback has been moved to utils.dialog_consolidation_helper. "
        "Please update your imports.",
        DeprecationWarning,
        stacklevel=2
    )
    return _show_user_feedback(page, message, is_error, action_label)


def show_success_message(page: ft.Page, message: str, action_label: Optional[str] = None, mode: Optional[str] = None) -> None:
    """
    DEPRECATED: Show success message to user with optional mode indicator.
    This function has been moved to utils.dialog_consolidation_helper.
    """
    warnings.warn(
        "show_success_message has been moved to utils.dialog_consolidation_helper. "
        "Please update your imports.",
        DeprecationWarning,
        stacklevel=2
    )
    return _show_success_message(page, message, action_label, mode)


def show_error_message(page: ft.Page, message: str, action_label: Optional[str] = None) -> None:
    """
    DEPRECATED: Show error message to user.
    This function has been moved to utils.dialog_consolidation_helper.
    """
    warnings.warn(
        "show_error_message has been moved to utils.dialog_consolidation_helper. "
        "Please update your imports.",
        DeprecationWarning,
        stacklevel=2
    )
    return _show_error_message(page, message, action_label)


def show_info_message(page: ft.Page, message: str, action_label: Optional[str] = None, mode: Optional[str] = None) -> None:
    """
    DEPRECATED: Show info message to user with optional mode indicator.
    This function has been moved to utils.dialog_consolidation_helper.
    """
    warnings.warn(
        "show_info_message has been moved to utils.dialog_consolidation_helper. "
        "Please update your imports.",
        DeprecationWarning,
        stacklevel=2
    )
    return _show_info_message(page, message, action_label, mode)


def show_warning_message(page: ft.Page, message: str, action_label: Optional[str] = None) -> None:
    """
    DEPRECATED: Show warning message to user.
    This function has been moved to utils.dialog_consolidation_helper.
    """
    warnings.warn(
        "show_warning_message has been moved to utils.dialog_consolidation_helper. "
        "Please update your imports.",
        DeprecationWarning,
        stacklevel=2
    )
    return _show_warning_message(page, message, action_label)


# Dialog functions have been consolidated into utils.dialog_consolidation_helper
# Use show_confirmation, show_info, show_input from that module instead