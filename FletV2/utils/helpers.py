#!/usr/bin/env python3
"""Dashboard helper utilities for FletV2.

Provides utility functions for:
- Relative timestamp formatting
- Disk usage retrieval
- Byte formatting
"""

from __future__ import annotations

import datetime
from typing import Any

# Optional psutil import with graceful fallback
try:
    import psutil

    _PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None  # type: ignore[assignment]
    _PSUTIL_AVAILABLE = False


def format_relative_timestamp(iso_timestamp: str | None) -> str:
    """Convert ISO timestamp to human-readable relative format.

    Args:
        iso_timestamp: ISO format timestamp string (e.g., "2025-12-31T22:46:17")

    Returns:
        Relative time string like "Just now", "5m ago", "2h ago", "Yesterday"
    """
    if not iso_timestamp:
        return ""

    try:
        # Parse ISO timestamp
        if "T" in iso_timestamp:
            ts = datetime.datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        else:
            ts = datetime.datetime.fromisoformat(iso_timestamp)

        # Make timezone-aware if naive
        now = datetime.datetime.now(tz=ts.tzinfo if ts.tzinfo else None)
        if ts.tzinfo is None:
            now = datetime.datetime.now()

        delta = now - ts
        seconds = delta.total_seconds()

        if seconds < 0:
            return "Just now"  # Future timestamps treated as now
        if seconds < 60:
            return "Just now"
        if seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes}m ago"
        if seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours}h ago"
        if seconds < 172800:
            return "Yesterday"

        days = int(seconds // 86400)
        if days < 7:
            return f"{days}d ago"
        if days < 30:
            weeks = days // 7
            return f"{weeks}w ago"

        return ts.strftime("%b %d")

    except (ValueError, TypeError, AttributeError):
        return ""


def format_bytes(bytes_val: int | float) -> str:
    """Convert bytes to human-readable format.

    Args:
        bytes_val: Number of bytes

    Returns:
        Human-readable string like "850 GB", "1.2 TB"
    """
    if bytes_val < 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(bytes_val)

    for unit in units:
        if size < 1024:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024

    return f"{size:.1f} PB"


def get_disk_usage(path: str = "/") -> dict[str, Any]:
    """Get disk usage statistics.

    Args:
        path: Path to check disk usage for (defaults to root)

    Returns:
        Dictionary with keys: used, total, percent, available, formatted_used, formatted_total
    """
    if not _PSUTIL_AVAILABLE:
        return {
            "used": 0,
            "total": 0,
            "percent": 0.0,
            "available": 0,
            "formatted_used": "N/A",
            "formatted_total": "N/A",
            "error": "psutil not available",
        }

    try:
        # On Windows, use C: drive if path is /
        import os

        if os.name == "nt" and path == "/":
            path = "C:\\"

        if psutil is None:
            raise ImportError("psutil not available")
        usage = psutil.disk_usage(path)
        return {
            "used": usage.used,
            "total": usage.total,
            "percent": usage.percent,
            "available": usage.free,
            "formatted_used": format_bytes(usage.used),
            "formatted_total": format_bytes(usage.total),
        }
    except Exception as e:
        return {
            "used": 0,
            "total": 0,
            "percent": 0.0,
            "available": 0,
            "formatted_used": "N/A",
            "formatted_total": "N/A",
            "error": str(e),
        }


__all__ = [
    "format_relative_timestamp",
    "format_bytes",
    "get_disk_usage",
]
