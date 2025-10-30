#!/usr/bin/env python3
"""Utility functions for formatting and normalizing data in the CyberBackup dashboard."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Union


def as_float(value: Any) -> float:
    """
    Safely convert a value to float with default fallback.

    Args:
        value: Any value that should be converted to float

    Returns:
        float representation of the value, or 0.0 if conversion fails
    """
    try:
        if value is None:
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def as_int(value: Any) -> int:
    """
    Safely convert a value to int with default fallback.

    Args:
        value: Any value that should be converted to int

    Returns:
        int representation of the value, or 0 if conversion fails
    """
    try:
        if value is None:
            return 0
        return int(value)
    except (ValueError, TypeError):
        return 0


def format_timestamp(timestamp: Union[str, datetime, None]) -> str:
    """
    Format a timestamp into a readable string format.

    Args:
        timestamp: Can be a datetime object, ISO string, or None

    Returns:
        Formatted timestamp string in 'YYYY-MM-DD HH:MM:SS' format,
        or 'N/A' if timestamp is invalid/None
    """
    if timestamp is None:
        return "N/A"

    if isinstance(timestamp, str):
        # Try to parse common timestamp formats
        formats_to_try = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y%m%d_%H%M%S",
        ]

        for fmt in formats_to_try:
            try:
                dt = datetime.strptime(timestamp, fmt)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

        # If parsing fails, return original string if it looks reasonable
        if len(str(timestamp)) > 6:  # Arbitrary minimum length
            return str(timestamp)
        return "N/A"

    if isinstance(timestamp, datetime):
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    return "N/A"


def format_uptime(seconds: Union[float, int, str, None]) -> str:
    """
    Format uptime seconds into a human-readable format.

    Args:
        seconds: Uptime in seconds (can be float, int, string, or None)

    Returns:
        Human-readable uptime string like '2 days, 3 hours, 45 minutes'
        or 'N/A' if seconds is invalid
    """
    try:
        if seconds is None:
            return "N/A"

        # Convert to float first to handle string inputs
        seconds_float = float(seconds)

        if seconds_float < 0:
            return "N/A"

        # Calculate time units
        days = int(seconds_float // 86400)
        hours = int((seconds_float % 86400) // 3600)
        minutes = int((seconds_float % 3600) // 60)
        secs = int(seconds_float % 60)

        # Build result string, only including non-zero units
        parts = []

        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")

        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")

        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

        if secs > 0 and not parts:  # Only show seconds if it's the only unit
            parts.append(f"{secs} second{'s' if secs != 1 else ''}")

        # Handle very small values
        if not parts and seconds_float > 0:
            if seconds_float < 1:
                return "< 1 second"
            else:
                return f"{seconds_float:.1f} seconds"

        if not parts:
            return "0 seconds"

        return ", ".join(parts)

    except (ValueError, TypeError):
        return "N/A"


def normalize_text(text: Any) -> str:
    """
    Normalize text values by converting to string and handling edge cases.

    Args:
        text: Any value that should be converted to a clean string

    Returns:
        Normalized string, or 'N/A' if text is None/empty
    """
    if text is None:
        return "N/A"

    # Convert to string
    str_text = str(text)

    # Clean up common whitespace issues
    cleaned = str_text.strip()

    # Replace empty strings after cleaning
    if not cleaned:
        return "N/A"

    # Handle common placeholder values that should be treated as missing
    placeholder_values = {
        "", " ", "-", "--", "null", "NULL", "none", "NONE",
        "undefined", "UNDEFINED", "n/a", "N/A"
    }

    if cleaned in placeholder_values:
        return "N/A"

    return cleaned


def format_bytes(bytes_value: Union[int, float, str, None]) -> str:
    """
    Format bytes into human-readable file sizes.

    Args:
        bytes_value: Number of bytes to format

    Returns:
        Human-readable size string like '1.5 MB' or 'N/A' if invalid
    """
    try:
        if bytes_value is None:
            return "N/A"

        bytes_float = float(bytes_value)

        if bytes_float < 0:
            return "N/A"

        # Define size units
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0

        # Convert to appropriate unit
        while bytes_float >= 1024 and unit_index < len(units) - 1:
            bytes_float /= 1024
            unit_index += 1

        # Format with appropriate decimal places
        if unit_index == 0:  # Bytes - no decimals
            return f"{int(bytes_float)} {units[unit_index]}"
        elif bytes_float < 10:  # Small values - 2 decimal places
            return f"{bytes_float:.2f} {units[unit_index]}"
        else:  # Larger values - 1 decimal place
            return f"{bytes_float:.1f} {units[unit_index]}"

    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value: Union[float, int, str, None], decimals: int = 1) -> str:
    """
    Format a decimal value as a percentage.

    Args:
        value: Value to format as percentage (0-1)
        decimals: Number of decimal places to show

    Returns:
        Formatted percentage string like '75.5%' or 'N/A' if invalid
    """
    try:
        if value is None:
            return "N/A"

        float_value = float(value)

        # Handle out-of-range values
        if float_value < 0 or float_value > 1:
            return "N/A"

        return f"{float_value * 100:.{decimals}f}%"

    except (ValueError, TypeError):
        return "N/A"