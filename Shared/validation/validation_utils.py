"""
Shared validation utilities for CyberBackup 3.0
"""

import logging
import os
import re

# Configure logger for this module
logger = logging.getLogger(__name__)

# Constants
MAX_ACTUAL_FILENAME_LENGTH = 255  # Maximum filename length


def is_valid_filename_for_storage(filename: str) -> bool:
    """
    Validate a filename for safe storage, checking for security issues and OS compatibility.

    This is the canonical filename validation for the entire CyberBackup system.
    All filename validation should use this function to ensure consistency.

    Args:
        filename: The filename to validate

    Returns:
        True if the filename is valid, False otherwise
    """
    # Check length (must be between 1 and MAX_ACTUAL_FILENAME_LENGTH)
    if not (1 <= len(filename) <= MAX_ACTUAL_FILENAME_LENGTH):
        logger.debug(
            f"Filename validation failed: Length ({len(filename)}) out of range (1-{MAX_ACTUAL_FILENAME_LENGTH})"
        )
        return False

    # Prevent path traversal attacks
    if "/" in filename or "\\" in filename or ".." in filename or "\0" in filename:
        logger.debug("Filename validation failed: Contains path traversal or null characters")
        return False

    # Character validation using regex - allow common safe characters
    # Allows: alphanumeric, dot, underscore, hyphen, space, ampersand, hash, parentheses, plus, comma
    if not re.match(r"^[a-zA-Z0-9._\-\s&#()+,]+$", filename):
        logger.debug("Filename validation failed: Contains unsafe characters")
        return False

    # Check for OS reserved names (Windows)
    # Extract base name without extension for comparison
    base_name = os.path.splitext(filename)[0].upper()
    reserved_names = (
        {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}
    )

    if base_name in reserved_names:
        logger.debug(f"Filename validation failed: '{base_name}' is a reserved OS name")
        return False

    # All checks passed
    return True


def is_valid_client_name(client_name: str) -> bool:
    """
    Validate a client name for security and format compliance.

    Args:
        client_name: The client name to validate

    Returns:
        True if the client name is valid, False otherwise
    """
    if not client_name:
        return False
    if len(client_name) > 50:  # Reasonable length limit
        return False
    if not re.match(r"^[a-zA-Z0-9_-]+$", client_name):
        return False
    # Additional checks can be added here as needed
    return True


def is_valid_file_content(content: bytes, max_size: int = 100 * 1024 * 1024) -> bool:  # 100MB default
    """
    Validate file content for size and other constraints.

    Args:
        content: The file content to validate
        max_size: Maximum allowed file size in bytes

    Returns:
        True if the content is valid, False otherwise
    """
    if len(content) > max_size:
        logger.warning(f"File content validation failed: Size {len(content)} exceeds maximum {max_size}")
        return False

    # Additional content validation can be added here if needed
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing potentially problematic characters.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename
    """
    # Replace potentially problematic characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Truncate if too long (keeping extension)
    if len(sanitized) > MAX_ACTUAL_FILENAME_LENGTH:
        name, ext = os.path.splitext(sanitized)
        max_name_len = MAX_ACTUAL_FILENAME_LENGTH - len(ext)
        sanitized = name[:max_name_len] + ext

    return sanitized
