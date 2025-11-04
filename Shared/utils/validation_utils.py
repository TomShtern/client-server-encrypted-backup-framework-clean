"""
Shared validation utilities for CyberBackup 3.0
"""
import os
import re
import logging
from typing import Optional


# Configure logger for this module
logger = logging.getLogger(__name__)

# Constants
MAX_ACTUAL_FILENAME_LENGTH = 255  # Maximum filename length


def is_valid_filename_for_storage(filename: str) -> bool:
    """
    Validate a filename for safe storage, checking for security issues and OS compatibility.
    
    Args:
        filename: The filename to validate
        
    Returns:
        True if the filename is valid, False otherwise
    """
    if not filename:
        logger.warning("Filename validation failed: Empty filename")
        return False
        
    if len(filename) < 1 or len(filename) > MAX_ACTUAL_FILENAME_LENGTH:
        logger.warning(f"Filename validation failed: Length check failed for '{filename}'")
        return False

    # Check for path traversal characters
    if any(char in filename for char in ('/', '\\', '..', '\0')):
        logger.warning(f"Filename validation failed: Path traversal detected in '{filename}'")
        return False

    # Special character checks for reserved names
    if filename.strip().lower() in {'con', 'prn', 'aux', 'nul'}:
        logger.warning(f"Filename validation failed: Reserved filename '{filename}'")
        return False

    # Reserved device names (COM/LPT + number)
    if re.match(r'^(com|lpt)[1-9]$', filename.strip().lower()):
        logger.warning(f"Filename validation failed: Reserved device name '{filename}'")
        return False

    # Character validation using regex - only allow safe characters
    if not re.match(r"^[a-zA-Z0-9._\-\s&#]+$", filename):
        logger.warning(f"Filename validation failed: Invalid characters in '{filename}'")
        return False

    # If all checks pass
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
    if not re.match(r'^[a-zA-Z0-9_-]+$', client_name):
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
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Truncate if too long (keeping extension)
    if len(sanitized) > MAX_ACTUAL_FILENAME_LENGTH:
        name, ext = os.path.splitext(sanitized)
        max_name_len = MAX_ACTUAL_FILENAME_LENGTH - len(ext)
        sanitized = name[:max_name_len] + ext
    
    return sanitized