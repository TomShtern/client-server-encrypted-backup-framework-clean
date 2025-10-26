#!/usr/bin/env python3
"""Compatibility layer for historical enhanced logs experimental module.

The modern application refactored the enhanced logs view into
`FletV2.views.enhanced_logs`.  Legacy test suites – notably the `_exp`
benchmarks – still import the earlier helper functions.  This module
re-implements the tiny functional surface expected by those tests while
delegating heavy lifting to the production module where possible.
"""

from __future__ import annotations

import asyncio
import csv
import json
import re
from pathlib import Path
from typing import Any, Callable, Iterable
import threading

# Project requirement – must be first import for reliable UTF-8 I/O on Windows.
import Shared.utils.utf8_solution as _  # noqa: F401

import flet as ft

from FletV2.utils.async_helpers import safe_server_call
from FletV2.views.enhanced_logs import (
    fetch_app_logs_async,
    fetch_server_logs_async,
    create_logs_view as _create_logs_view,
)

# Sensitive field handling mirrors the production view.
SENSITIVE_FIELDS = {
    "aes_key",
    "public_key",
    "private_key",
    "password",
    "secret",
    "token",
}


# ---------------------------------------------------------------------------
# View factory
# ---------------------------------------------------------------------------

def create_enhanced_logs_view(*args: Any, **kwargs: Any):
    """Return the modern logs view while preserving the historical name."""
    return _create_logs_view(*args, **kwargs)


# ---------------------------------------------------------------------------
# Filtering utilities (pure functions exercised by unit tests)
# ---------------------------------------------------------------------------

def _normalise_text(value: Any) -> str:
    return str(value or "")


def filter_logs_by_query(logs: Iterable[dict[str, Any]], query: str | None) -> list[dict[str, Any]]:
    if not query:
        return list(logs)

    pattern = _compile_search_regex(query)
    results: list[dict[str, Any]] = []
    for entry in logs:
        payload = _normalise_text(entry.get("message"))
        component = _normalise_text(entry.get("component"))
        timestamp = _normalise_text(entry.get("time"))
        if pattern.search(payload) or pattern.search(component) or pattern.search(timestamp):
            results.append(entry)
    return results


def filter_logs_by_level(logs: Iterable[dict[str, Any]], level: str | None) -> list[dict[str, Any]]:
    if not level or level == "All":
        return list(logs)
    level_upper = level.upper()
    return [entry for entry in logs if _normalise_text(entry.get("level")).upper() == level_upper]


def _compile_search_regex(query: str) -> re.Pattern[str]:
    if not query:
        return re.compile("", re.IGNORECASE)

    if query.startswith("/") and query.count("/") >= 2:
        pattern, _, flags_token = query[1:].partition("/")
        flags = 0
        if "i" in flags_token:
            flags |= re.IGNORECASE
        if "m" in flags_token:
            flags |= re.MULTILINE
        if "s" in flags_token:
            flags |= re.DOTALL
        try:
            return re.compile(pattern, flags)
        except re.error:
            return re.compile(re.escape(pattern), flags)

    return re.compile(re.escape(query), re.IGNORECASE)


def calculate_log_statistics(logs: Iterable[dict[str, Any]]) -> dict[str, Any]:
    logs_list = list(logs)
    by_level: dict[str, int] = {}
    by_hour: dict[str, int] = {}

    for entry in logs_list:
        level = _normalise_text(entry.get("level") or "INFO")
        by_level[level] = by_level.get(level, 0) + 1

        timestamp = _normalise_text(entry.get("time"))
        hour_bucket = timestamp[:13] if len(timestamp) >= 13 else ""
        if hour_bucket:
            by_hour[hour_bucket] = by_hour.get(hour_bucket, 0) + 1

    latest = logs_list[0] if logs_list else None
    return {
        "total": len(logs_list),
        "by_level": by_level,
        "by_hour": by_hour,
        "latest": latest,
    }


def highlight_text_with_search(text: str, query: str | None) -> ft.Text:
    text = text or ""
    if not query:
        return ft.Text(text)

    pattern = _compile_search_regex(query)
    matches = list(pattern.finditer(text))
    if not matches:
        return ft.Text(text)

    spans: list[ft.TextSpan] = []
    cursor = 0
    for match in matches:
        start, end = match.span()
        if start > cursor:
            spans.append(ft.TextSpan(text[cursor:start]))
        spans.append(
            ft.TextSpan(
                text[start:end],
                ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
            )
        )
        cursor = end
    if cursor < len(text):
        spans.append(ft.TextSpan(text[cursor:]))

    return ft.Text(spans=spans)


def export_logs_to_csv(logs: Iterable[dict[str, Any]], filename: str | Path) -> None:
    rows = list(logs)
    if not rows:
        Path(filename).write_text("")
        return

    fieldnames = sorted({key for row in rows for key in row.keys()})
    with open(filename, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_logs_to_json(logs: Iterable[dict[str, Any]], filename: str | Path) -> None:
    with open(filename, "w", encoding="utf-8") as handle:
        json.dump(list(logs), handle, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Async helpers mirroring the historical experimental API
# ---------------------------------------------------------------------------

async def fetch_logs_async(server_bridge: Any | None) -> list[dict[str, Any]]:
    if not server_bridge:
        return []

    loop = asyncio.get_running_loop()
    future: asyncio.Future = loop.create_future()

    def _worker() -> None:
        try:
            result = safe_server_call(server_bridge, "get_logs")
        except Exception as exc:  # pragma: no cover - defensive guard
            if not future.done():
                loop.call_soon_threadsafe(future.set_exception, exc)
            return

        if not future.done():
            loop.call_soon_threadsafe(future.set_result, result)

    threading.Thread(target=_worker, daemon=True).start()

    try:
        result = await asyncio.wait_for(future, timeout=0.35)
    except asyncio.TimeoutError:
        return []

    if not result.get("success"):
        return []

    data = result.get("data", {})
    logs = data.get("logs") if isinstance(data, dict) else data
    if not isinstance(logs, list):
        return []
    return [entry for entry in logs if isinstance(entry, dict)]


async def fetch_log_statistics_async(server_bridge: Any | None) -> dict[str, Any]:
    logs = await fetch_logs_async(server_bridge)
    return calculate_log_statistics(logs)


# Legacy experimental suite called into the modern async helpers, so we simply
# reuse the production fetchers for completeness.
async def fetch_logs_with_sources_async(server_bridge: Any | None, page: ft.Page | None = None) -> dict[str, Any]:
    server_logs_task = fetch_server_logs_async(server_bridge, page)
    app_logs_task = fetch_app_logs_async(page)
    server_logs, app_logs = await asyncio.gather(server_logs_task, app_logs_task)
    return {"server_logs": server_logs, "app_logs": app_logs}


__all__ = [
    "create_enhanced_logs_view",
    "filter_logs_by_query",
    "filter_logs_by_level",
    "calculate_log_statistics",
    "export_logs_to_csv",
    "export_logs_to_json",
    "highlight_text_with_search",
    "_compile_search_regex",
    "fetch_logs_async",
    "fetch_log_statistics_async",
]
