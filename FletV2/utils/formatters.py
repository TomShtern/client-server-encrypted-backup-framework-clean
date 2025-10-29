#!/usr/bin/env python3
"""
Data Formatters - Extracted normalization patterns from working views.

This module consolidates the duplicated formatting/normalization logic found in:
- dashboard.py:70-100 (_normalize_text, _format_uptime, _format_timestamp)
- database_pro.py:135-160 (stringify_value, format_table_cell_value)
- enhanced_logs.py:97-140 (_normalize_log_entry)
- files.py (file size formatting)
- analytics.py (timestamp and text normalization)

Original duplication: ~180 lines across 5 files
New module: ~100 lines of consolidated, reusable functions
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

import logging


logger = logging.getLogger(__name__)


def normalize_text(value: Any, max_length: int = 50, placeholder: str = "N/A") -> str:
    """
    Normalize any value to display text with optional truncation.

    Extracted from dashboard.py:70-74.

    Args:
        value: Value to normalize
        max_length: Maximum length before truncation
        placeholder: Text to show for None/empty values

    Returns:
        Normalized string

    Example:
        normalize_text(None) → "N/A"
        normalize_text("  hello  ") → "hello"
        normalize_text("long text" * 10, max_length=20) → "long textlong tex..."
    """
    if value is None or value == "":
        return placeholder

    text = str(value).strip()

    if len(text) > max_length:
        return f"{text[:max_length]}..."

    return text


def format_timestamp(value: Any, format_str: str = "%Y-%m-%d %H:%M:%S", placeholder: str = "—") -> str:
    """
    Format timestamp to standardized display string.

    Extracted from dashboard.py:92-99.

    Args:
        value: Timestamp value (ISO string, datetime, or timestamp)
        format_str: strftime format string
        placeholder: Text to show for invalid/missing timestamps

    Returns:
        Formatted timestamp string

    Example:
        format_timestamp("2025-01-14T10:30:00") → "2025-01-14 10:30:00"
        format_timestamp(None) → "—"
    """
    if not value:
        return placeholder

    try:
        if isinstance(value, datetime):
            parsed = value
        else:
            text_value = str(value).strip()
            # Allow trailing "Z" (Zulu) suffix and other common timestamp variants
            if text_value.endswith("Z"):
                text_value = text_value[:-1] + "+00:00"

            try:
                parsed = datetime.fromisoformat(text_value)
            except ValueError:
                # Fallback to a couple of common human readable formats (ui_helpers legacy)
                for candidate in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
                    try:
                        parsed = datetime.strptime(text_value, candidate)
                        break
                    except ValueError:
                        parsed = None
                if parsed is None:
                    raise
        return parsed.strftime(format_str)
    except Exception:
        return str(value)


def format_uptime(seconds: float | int, short: bool = False) -> str:
    """
    Format uptime duration to human-readable string.

    Extracted from dashboard.py:76-89.

    Args:
        seconds: Duration in seconds
        short: If True, use short format (1d 2h 3m)

    Returns:
        Formatted uptime string

    Example:
        format_uptime(0) → "—"
        format_uptime(90) → "1m 30s" or "1m" (short)
        format_uptime(90000) → "1d 1h"
    """
    if seconds <= 0:
        return "—"

    seconds_int = int(seconds)
    minutes, secs = divmod(seconds_int, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes and (not short or not days):
        parts.append(f"{minutes}m")
    if secs and not short and not hours and not days:
        parts.append(f"{secs}s")

    return " ".join(parts) or "<1m"


def format_file_size(bytes_value: Any) -> str:
    """
    Format file size to human-readable string with appropriate units.

    Extracted from files.py patterns.

    Args:
        bytes_value: Size in bytes

    Returns:
        Formatted size string

    Example:
        format_file_size(1024) → "1.0 KB"
        format_file_size(1048576) → "1.0 MB"
        format_file_size(0) → "0 B"
    """
    try:
        numeric_value = float(bytes_value)
    except (TypeError, ValueError):
        return str(bytes_value)

    if numeric_value < 0:
        return "—"
    if numeric_value == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(numeric_value)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:  # Bytes
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def stringify_database_value(value: Any, max_display_length: int = 100) -> str:
    """
    Convert database value to display string with smart formatting.

    Extracted from database_pro.py:135-152.

    Args:
        value: Database value (can be bytes, datetime, None, etc.)
        max_display_length: Maximum length before truncation

    Returns:
        Formatted string for display

    Example:
        stringify_database_value(None) → ""
        stringify_database_value(b'\\x01\\x02') → "0102" (hex)
        stringify_database_value(datetime.now()) → "2025-01-14 10:30:00"
    """
    if value is None:
        return ""

    # Handle binary data (UUIDs, keys)
    if isinstance(value, (bytes, bytearray)):
        hex_str = value.hex()
        return hex_str[:32] + "..." if len(hex_str) > 32 else hex_str

    # Handle datetime
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    # Convert to string and truncate
    str_value = str(value)
    if len(str_value) > max_display_length:
        return f"{str_value[:max_display_length]}..."

    return str_value


def format_table_cell_value(value: Any, column_name: str = "", max_length: int = 50) -> str:
    """
    Smart formatting for table cells with context-aware truncation.

    Extracted from database_pro.py:154-162.

    Args:
        value: Cell value
        column_name: Column name for context-aware formatting
        max_length: Maximum display length

    Returns:
        Formatted cell value

    Example:
        format_table_cell_value(None) → "—"
        format_table_cell_value(b'\\xaa\\xbb', "ID") → "aabb" (hex, shorter for IDs)
        format_table_cell_value("long text", "description", 10) → "long text..."
    """
    if value is None:
        return "—"  # Em dash for NULL

    # Handle binary data (IDs, keys)
    if isinstance(value, (bytes, bytearray)):
        hex_str = value.hex()
        # Shorter truncation for ID columns
        if "id" in column_name.lower():
            return hex_str[:16] + "..." if len(hex_str) > 16 else hex_str
        return hex_str[:32] + "..." if len(hex_str) > 32 else hex_str

    # Handle datetime
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    # Convert to string and truncate
    str_value = str(value)
    if len(str_value) > max_length:
        return f"{str_value[:max_length]}..."

    return str_value


def normalize_log_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize log entry to consistent format.

    Extracted from enhanced_logs.py:120-140.

    Args:
        entry: Raw log entry dict

    Returns:
        Normalized log entry with consistent fields

    Example:
        normalize_log_entry({
            'timestamp': '2025-01-14T10:30:00',
            'level': 'INFO',
            'message': 'Started'
        }) → {
            'timestamp': '2025-01-14 10:30:00',
            'level': 'INFO',
            'message': 'Started',
            'component': 'unknown'
        }
    """
    return {
        'timestamp': format_timestamp(entry.get('timestamp', '')),
        'level': str(entry.get('level', 'INFO')).upper(),
        'component': str(entry.get('component', entry.get('logger', 'unknown'))),
        'message': str(entry.get('message', '')),
        'details': entry.get('details', {}),
    }


def as_float(value: Any, default: float | None = None) -> float | None:
    """
    Safely convert value to float with fallback.

    Extracted from dashboard.py:102-107.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value or default

    Example:
        as_float("3.14") → 3.14
        as_float(None) → None
        as_float("invalid", 0.0) → 0.0
    """
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int | None = None) -> int | None:
    """
    Safely convert value to int with fallback.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Int value or default

    Example:
        as_int("42") → 42
        as_int(None) → None
        as_int("invalid", 0) → 0
    """
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def compute_file_signature(file_dict: dict[str, Any]) -> tuple[Any, Any, Any, Any]:
    """Return a lightweight immutable signature for a file row for future diffing.

    Extracted from utils.ui_helpers (legacy). Keeping it here ensures a single
    canonical place for row identity helpers.
    """

    if not isinstance(file_dict, dict):
        return tuple()

    return (
        file_dict.get("id"),
        file_dict.get("size"),
        file_dict.get("status"),
        file_dict.get("modified"),
    )


def annotate_size_strings(
    rows: Iterable[dict[str, Any]],
    size_key: str = "size",
    target_key: str = "size_formatted",
) -> list[dict[str, Any]]:
    """Attach human readable sizes for each row (from server_mediated_operations)."""

    annotated: list[dict[str, Any]] = []
    for row in rows or []:
        if isinstance(row, dict):
            value = row.get(size_key, 0)
            row[target_key] = format_file_size(value)
            annotated.append(row)
    return annotated


def parse_timestamp_columns(
    rows: Iterable[dict[str, Any]],
    key: str = "timestamp",
) -> list[dict[str, Any]]:
    """Parse ISO timestamp strings into ``datetime`` objects in-place.

    Mirrors the timestamp_processor utility from server_mediated_operations.
    """

    parsed_rows: list[dict[str, Any]] = []
    for row in rows or []:
        if isinstance(row, dict) and key in row and isinstance(row[key], str):
            try:
                row[key] = datetime.fromisoformat(row[key])
            except ValueError:
                logger.debug("Failed to parse timestamp %s", row[key])
        parsed_rows.append(row)
    return parsed_rows


def append_percentage(
    rows: Iterable[dict[str, Any]],
    key: str = "value",
    target_key: str = "value_percentage",
) -> list[dict[str, Any]]:
    """Append percentage string fields for numeric values."""

    processed: list[dict[str, Any]] = []
    for row in rows or []:
        if isinstance(row, dict) and key in row:
            try:
                numeric = float(row[key])
                row[target_key] = f"{numeric:.1f}%"
            except (TypeError, ValueError):
                row[target_key] = "—"
        processed.append(row)
    return processed


def annotate_status_display(
    rows: Iterable[dict[str, Any]],
    status_key: str = "status",
    target_key: str = "status_display",
) -> list[dict[str, Any]]:
    """Attach normalized status metadata (text + color) to each row."""

    palette = {
        "running": {"text": "Running", "color": "green"},
        "stopped": {"text": "Stopped", "color": "red"},
        "pending": {"text": "Pending", "color": "orange"},
        "error": {"text": "Error", "color": "red"},
        "completed": {"text": "Completed", "color": "green"},
        "failed": {"text": "Failed", "color": "red"},
    }

    annotated: list[dict[str, Any]] = []
    for row in rows or []:
        if isinstance(row, dict):
            status_value = str(row.get(status_key, "")).lower()
            row[target_key] = palette.get(status_value, {"text": status_value.title() or "Unknown", "color": "neutral"})
            annotated.append(row)
    return annotated
