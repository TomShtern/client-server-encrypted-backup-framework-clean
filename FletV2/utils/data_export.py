"""
Data Export Utilities for FletV2 - Reusable CSV/JSON export functionality.

This module provides reusable functions for:
- Exporting data to CSV format
- Exporting data to JSON format
- Exporting data to TXT format
- Generating timestamped export filenames
- Export with progress tracking
"""

import csv
import json
from collections.abc import Callable
from datetime import datetime
from typing import Any


def export_to_csv(data: list[dict[str, Any]], filepath: str, fieldnames: list[str] | None = None):
    """
    Export data to CSV file.

    Args:
        data: List of dictionaries to export
        filepath: Path to the output file
        fieldnames: List of field names to include in the CSV (optional)

    Raises:
        ValueError: If no data is provided
        IOError: If there's an issue writing the file
    """
    if not data:
        raise ValueError("No data to export")

    if fieldnames is None:
        fieldnames = list(data[0].keys()) if data else []

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def export_to_json(data: list[dict[str, Any]], filepath: str, indent: int = 2):
    """
    Export data to JSON file.

    Args:
        data: List of dictionaries to export
        filepath: Path to the output file
        indent: Number of spaces for indentation (default: 2)

    Raises:
        IOError: If there's an issue writing the file
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str, ensure_ascii=False)


def export_to_txt(data: list[dict[str, Any]], filepath: str, format_func: Callable | None = None):
    """
    Export data to TXT file with optional custom formatting.

    Args:
        data: List of dictionaries to export
        filepath: Path to the output file
        format_func: Optional function to format each item (default: str)

    Raises:
        IOError: If there's an issue writing the file
    """
    with open(filepath, "w", encoding="utf-8") as f:
        for item in data:
            if format_func:
                line = format_func(item)
            else:
                line = str(item)
            f.write(line + "\n")


def generate_export_filename(prefix: str, extension: str) -> str:
    """
    Generate timestamped export filename.

    Args:
        prefix: Prefix for the filename
        extension: File extension without the dot (e.g., "csv", "json")

    Returns:
        Generated filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


async def export_with_progress(
    data: list[dict[str, Any]],
    filepath: str,
    export_func: Callable,
    progress_callback: Callable | None = None,
):
    """
    Export data with progress updates.

    Args:
        data: List of dictionaries to export
        filepath: Path to the output file
        export_func: Function to perform the export (e.g., export_to_csv)
        progress_callback: Optional callback function to report progress
    """
    if progress_callback:
        progress_callback(0, len(data), "Starting export...")

    export_func(data, filepath)

    if progress_callback:
        progress_callback(len(data), len(data), "Export complete!")
