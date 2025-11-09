"""
Canonical filename validation for the Client-Server Encrypted Backup Framework.

This module provides centralized filename validation logic that ensures
consistent security and compatibility across all server components.
"""

import logging
import os
import re

logger = logging.getLogger(__name__)

# Configuration constants
MAX_ACTUAL_FILENAME_LENGTH = 200  # Maximum allowed filename length
MIN_FILENAME_LENGTH = 1  # Minimum allowed filename length

# Reserved OS names that should be rejected (case-insensitive)
RESERVED_OS_NAMES: set[str] = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}

# Allowed filename characters pattern
# Allows: alphanumeric, dots, underscores, hyphens, spaces, ampersands, hash symbols
ALLOWED_FILENAME_PATTERN = re.compile(r"^[a-zA-Z0-9._\-\s&#]+$")

# Path traversal patterns to reject
PATH_TRAVERSAL_CHARS = {"/", "\\", "..", "\0"}


class FilenameValidationError(Exception):
    """Raised when filename validation fails."""

    pass


def validate_filename(filename: str, strict: bool = True) -> bool:
    """
    Validate a filename for storage safety and compatibility.

    This is the canonical filename validation function that replaces
    all duplicate validation logic throughout the codebase.

    Args:
        filename: The filename string to validate
        strict: If True, applies strict validation rules. If False, allows more characters.

    Returns:
        True if filename is valid, False otherwise

    Raises:
        FilenameValidationError: If filename is invalid and strict validation is enabled
    """
    try:
        return _validate_filename_internal(filename, strict)
    except FilenameValidationError:
        if strict:
            raise
        return False


def _validate_filename_internal(filename: str, strict: bool) -> bool:
    """Internal filename validation logic."""

    # Check length constraints
    if not (MIN_FILENAME_LENGTH <= len(filename) <= MAX_ACTUAL_FILENAME_LENGTH):
        error_msg = f"Filename length ({len(filename)}) is out of allowed range ({MIN_FILENAME_LENGTH}-{MAX_ACTUAL_FILENAME_LENGTH})"
        logger.debug(f"Filename validation failed for '{filename}': {error_msg}")
        if strict:
            raise FilenameValidationError(error_msg)
        return False

    # Check for path traversal characters
    if any(char in filename for char in PATH_TRAVERSAL_CHARS):
        error_msg = "Contains path traversal sequence or null characters"
        logger.debug(f"Filename validation failed for '{filename}': {error_msg}")
        if strict:
            raise FilenameValidationError(error_msg)
        return False

    # Check allowed characters
    if not ALLOWED_FILENAME_PATTERN.match(filename):
        error_msg = (
            f"Contains disallowed characters (does not match pattern '{ALLOWED_FILENAME_PATTERN.pattern}')"
        )
        logger.debug(f"Filename validation failed for '{filename}': {error_msg}")
        if strict:
            raise FilenameValidationError(error_msg)
        return False

    # Check for reserved OS names
    base_filename_no_ext = os.path.splitext(filename)[0].upper()
    if base_filename_no_ext in RESERVED_OS_NAMES:
        error_msg = f"Base name '{base_filename_no_ext}' is a reserved OS name"
        logger.debug(f"Filename validation failed for '{filename}': {error_msg}")
        if strict:
            raise FilenameValidationError(error_msg)
        return False

    return True


def sanitize_filename(filename: str, replacement_char: str = "_") -> str:
    """
    Sanitize a filename by replacing invalid characters.

    Args:
        filename: Original filename
        replacement_char: Character to replace invalid characters with

    Returns:
        Sanitized filename that passes validation

    Raises:
        ValueError: If replacement_char is not a single valid character
    """
    if len(replacement_char) != 1 or not ALLOWED_FILENAME_PATTERN.match(replacement_char):
        raise ValueError(f"Replacement character must be a single valid character, got: '{replacement_char}'")

    # Truncate if too long
    if len(filename) > MAX_ACTUAL_FILENAME_LENGTH:
        filename = filename[:MAX_ACTUAL_FILENAME_LENGTH]

    # Replace path traversal characters
    for char in PATH_TRAVERSAL_CHARS:
        if char in filename:
            filename = filename.replace(char, replacement_char)

    # Replace disallowed characters
    sanitized = ""
    for char in filename:
        if ALLOWED_FILENAME_PATTERN.match(char):
            sanitized += char
        else:
            sanitized += replacement_char

    # Handle reserved names
    base_name, ext = os.path.splitext(sanitized)
    if base_name.upper() in RESERVED_OS_NAMES:
        base_name = f"{replacement_char}{base_name}"

    sanitized = base_name + ext

    # Ensure minimum length
    if len(sanitized) < MIN_FILENAME_LENGTH:
        sanitized = f"file{replacement_char}" + sanitized

    return sanitized


def get_safe_filename(original_filename: str, fallback_name: str = "unnamed_file") -> str:
    """
    Get a safe filename, sanitizing if necessary or using fallback.

    Args:
        original_filename: Original filename to validate/sanitize
        fallback_name: Fallback name if sanitization fails

    Returns:
        A valid, safe filename
    """
    if not original_filename:
        return fallback_name

    try:
        if validate_filename(original_filename, strict=False):
            return original_filename
    except Exception:
        pass

    try:
        sanitized = sanitize_filename(original_filename)
        if validate_filename(sanitized, strict=False):
            return sanitized
    except Exception:
        pass

    return fallback_name


def validate_filename_for_storage(filename: str) -> bool:
    """
    Legacy compatibility function for existing code.

    DEPRECATED: Use validate_filename() instead.
    This function is provided for backward compatibility during migration.
    """
    logger.warning("validate_filename_for_storage() is deprecated, use validate_filename() instead")
    return validate_filename(filename, strict=False)


def is_valid_filename_for_storage(filename: str) -> bool:
    """
    Legacy compatibility function for existing code.

    DEPRECATED: Use validate_filename() instead.
    This function is provided for backward compatibility during migration.
    """
    logger.warning("is_valid_filename_for_storage() is deprecated, use validate_filename() instead")
    return validate_filename(filename, strict=False)


# Configuration for different validation levels
class ValidationLevel:
    """Predefined validation levels for different use cases."""

    STRICT = True  # Strict validation with exceptions
    PERMISSIVE = False  # Permissive validation without exceptions


def configure_validation(
    max_length: int | None = None,
    min_length: int | None = None,
    additional_allowed_chars: str | None = None,
    additional_reserved_names: set[str] | None = None,
) -> None:
    """
    Configure global validation parameters.

    Args:
        max_length: Override maximum filename length
        min_length: Override minimum filename length
        additional_allowed_chars: Additional characters to allow in filenames
        additional_reserved_names: Additional reserved names to reject

    Note:
        This function modifies global state and should be used carefully.
        Consider using custom validation functions for application-specific needs.
    """
    global MAX_ACTUAL_FILENAME_LENGTH, MIN_FILENAME_LENGTH, ALLOWED_FILENAME_PATTERN, RESERVED_OS_NAMES

    if max_length is not None:
        MAX_ACTUAL_FILENAME_LENGTH = max_length
        logger.info(f"Updated max filename length to {max_length}")

    if min_length is not None:
        MIN_FILENAME_LENGTH = min_length
        logger.info(f"Updated min filename length to {min_length}")

    if additional_allowed_chars:
        # Escape special regex characters
        escaped_chars = re.escape(additional_allowed_chars)
        new_pattern = ALLOWED_FILENAME_PATTERN.pattern[:-2] + escaped_chars + "]+$"
        ALLOWED_FILENAME_PATTERN = re.compile(new_pattern)
        logger.info(f"Added allowed characters: {additional_allowed_chars}")

    if additional_reserved_names:
        RESERVED_OS_NAMES.update(name.upper() for name in additional_reserved_names)
        logger.info(f"Added reserved names: {additional_reserved_names}")


def get_validation_info() -> dict:
    """
    Get current validation configuration.

    Returns:
        Dictionary with current validation settings
    """
    return {
        "max_length": MAX_ACTUAL_FILENAME_LENGTH,
        "min_length": MIN_FILENAME_LENGTH,
        "allowed_pattern": ALLOWED_FILENAME_PATTERN.pattern,
        "reserved_names": sorted(RESERVED_OS_NAMES),
        "path_traversal_chars": sorted(PATH_TRAVERSAL_CHARS),
    }
