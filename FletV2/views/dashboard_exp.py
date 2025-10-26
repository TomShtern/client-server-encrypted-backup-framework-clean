#!/usr/bin/env python3
"""Compatibility helpers for the legacy dashboard experimental module."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Iterable

# Project requirement – must be first import for reliable UTF-8 I/O on Windows.
import Shared.utils.utf8_solution as _  # noqa: F401

import flet as ft

if not hasattr(ft, "colors"):
    class _LegacyColorsProxy:
        def __getattr__(self, name: str):
            return getattr(ft.Colors, name)

    ft.colors = _LegacyColorsProxy()  # type: ignore[attr-defined]

from FletV2.utils.async_helpers import run_sync_in_executor, safe_server_call
from FletV2.views.dashboard import create_dashboard_view as _create_dashboard_view


def create_dashboard_view(*args: Any, **kwargs: Any):  # pragma: no cover - thin wrapper
    """Expose the modern dashboard view under the historical function name."""
    return _create_dashboard_view(*args, **kwargs)


# ---------------------------------------------------------------------------
# Pure data-transformation helpers expected by historical unit tests
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class _MetricDefaults:
    clients_count: int = 0
    files_count: int = 0
    total_storage: int = 0
    uptime: Any = "Unknown"
    server_status: str = "Unknown"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_usage: float = 0.0
    backup_success_rate: float = 0.0
    active_sessions: int = 0
    pending_operations: int = 0


def _extract_payload(block: Any) -> dict[str, Any]:
    if isinstance(block, dict) and "data" in block and isinstance(block["data"], dict):
        return block["data"]
    if isinstance(block, dict):
        return block
    return {}


def calculate_metrics_summary(
    dashboard_data: Any,
    system_data: Any,
    performance_data: Any,
    stats_data: Any,
) -> dict[str, Any]:
    defaults = _MetricDefaults()
    dashboard = _extract_payload(dashboard_data)
    system = _extract_payload(system_data)
    performance = _extract_payload(performance_data)
    stats = _extract_payload(stats_data)

    summary = {
        "clients_count": int(dashboard.get("clients_count", defaults.clients_count)),
        "files_count": int(dashboard.get("files_count", defaults.files_count)),
        "total_storage": int(dashboard.get("total_storage", defaults.total_storage)),
        "uptime": system.get("uptime", defaults.uptime),
        "server_status": system.get("server_status", defaults.server_status),
        "cpu_usage": float(performance.get("cpu_usage", defaults.cpu_usage)),
        "memory_usage": float(performance.get("memory_usage", defaults.memory_usage)),
        "network_usage": float(performance.get("network_usage", defaults.network_usage)),
        "backup_success_rate": float(stats.get("backup_success_rate", defaults.backup_success_rate)),
        "active_sessions": int(stats.get("active_sessions", defaults.active_sessions)),
        "pending_operations": int(stats.get("pending_operations", defaults.pending_operations)),
    }

    # Normalise unknown uptime values
    if summary["uptime"] in (None, ""):
        summary["uptime"] = defaults.uptime
    return summary


_UNITS = [
    (1024 ** 4, "TB"),
    (1024 ** 3, "GB"),
    (1024 ** 2, "MB"),
    (1024, "KB"),
    (1, "B"),
]


def format_storage_value(value: Any) -> str:
    try:
        bytes_value = float(value)
    except (TypeError, ValueError):
        bytes_value = 0.0

    for factor, suffix in _UNITS:
        if bytes_value >= factor:
            return f"{bytes_value / factor:.2f} {suffix}"
    return "0 B"


def format_duration(seconds: Any) -> str:
    try:
        total = int(seconds)
    except (TypeError, ValueError):
        return "Unknown"

    if total < 60:
        return f"{total}s"

    minutes, sec = divmod(total, 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"

    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{hours}h {minutes}m {sec}s"

    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {minutes}m"


_STATUS_COLOR_MAP = {
    "connected": ft.Colors.GREEN,
    "online": ft.Colors.GREEN,
    "active": ft.Colors.GREEN,
    "disconnected": ft.Colors.RED,
    "offline": ft.Colors.RED,
    "error": ft.Colors.RED,
    "inactive": ft.Colors.AMBER,
}


def get_status_color(status: str | None) -> str:
    if not status:
        return ft.Colors.GREY
    key = status.strip().lower()
    return _STATUS_COLOR_MAP.get(key, ft.Colors.GREY)


def process_activity_logs(activity_data: Any) -> list[dict[str, Any]]:
    if isinstance(activity_data, dict):
        if activity_data.get("success") is False:
            return []
        payload = activity_data.get("data")
    else:
        payload = activity_data

    if not isinstance(payload, list):
        return []
    result: list[dict[str, Any]] = []
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        result.append(
            {
                "timestamp": entry.get("timestamp"),
                "type": entry.get("type"),
                "message": entry.get("message"),
                "source": entry.get("source"),
            }
        )
    return result


# ---------------------------------------------------------------------------
# Async helpers mirroring the experimental API
# ---------------------------------------------------------------------------

async def fetch_dashboard_summary_async(server_bridge: Any | None) -> dict[str, Any]:
    if not server_bridge:
        return {"success": False, "error": "No server bridge", "data": None}
    return await run_sync_in_executor(safe_server_call, server_bridge, "get_dashboard_summary")


async def fetch_system_status_async(server_bridge: Any | None) -> dict[str, Any]:
    if not server_bridge:
        return {"success": False, "error": "No server bridge", "data": None}
    return await run_sync_in_executor(safe_server_call, server_bridge, "get_system_status")


__all__ = [
    "create_dashboard_view",
    "calculate_metrics_summary",
    "format_storage_value",
    "format_duration",
    "get_status_color",
    "process_activity_logs",
    "fetch_dashboard_summary_async",
    "fetch_system_status_async",
]
