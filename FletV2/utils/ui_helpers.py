"""UI Helper Utilities for FletV2

Implements shared lightweight presentation + formatting helpers used by
Files and Logs views (Phase A of Visual Optimization Plan).

These helpers are intentionally dependency‑light and pure so they can be
imported without side effects and are easy to unit test.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple, Optional
import flet as ft

__all__ = [
	"size_to_human",
	"format_iso_short",
	"status_color",
	"level_colors",
	"build_status_badge",
	"build_level_badge",
	"striped_row_color",
	"compute_file_signature",
]


def size_to_human(size: Any) -> str:
	"""Convert bytes (int) to human readable string; pass through otherwise.
	Accepts preformatted strings (returns as-is) to avoid double formatting.
	"""
	try:
		if not isinstance(size, (int, float)):
			return str(size)
		b = int(size)
		if b < 1024:
			return f"{b} B"
		kb = b / 1024
		if kb < 1024:
			return f"{kb:.1f} KB"
		mb = kb / 1024
		if mb < 1024:
			return f"{mb:.1f} MB"
		gb = mb / 1024
		return f"{gb:.1f} GB"
	except Exception:  # pragma: no cover - defensive
		return str(size)


def format_iso_short(ts: Optional[str]) -> str:
	"""Format ISO timestamp to YYYY-MM-DD HH:MM; if already short or invalid return original."""
	if not ts:
		return "Unknown"
	try:
		# Handle already formatted strings without 'T'
		if "T" not in ts:
			# Best effort: attempt parse with common formats
			for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
				try:
					dt = datetime.strptime(ts, fmt)
					return dt.strftime("%Y-%m-%d %H:%M")
				except ValueError:
					continue
			return ts  # return as-is
		dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
		return dt.strftime("%Y-%m-%d %H:%M")
	except Exception:  # pragma: no cover
		return ts


_STATUS_COLOR_MAP = {
	"verified": ft.Colors.GREEN_600,
	"complete": ft.Colors.GREEN_600,
	"pending": ft.Colors.ORANGE_600,
	"received": ft.Colors.BLUE_600,
	"unverified": ft.Colors.RED_600,
	"stored": ft.Colors.PURPLE_600,
	"archived": ft.Colors.BROWN_600,
	"empty": ft.Colors.GREY_500,
}


def status_color(status: str) -> str:
	# Normalize non-string using f-string coercion (avoids explicit cast warning)
	key = status.lower() if isinstance(status, str) else f"{status}".lower()
	return _STATUS_COLOR_MAP.get(key, ft.Colors.GREY_400)


_LEVEL_COLOR_FG = {
	"INFO": ft.Colors.BLUE,
	"SUCCESS": ft.Colors.GREEN,
	"WARNING": ft.Colors.ORANGE,
	"ERROR": ft.Colors.RED,
	"DEBUG": ft.Colors.GREY,
}
_LEVEL_COLOR_BG = {
	"INFO": ft.Colors.BLUE_50,
	"SUCCESS": ft.Colors.GREEN_50,
	"WARNING": ft.Colors.ORANGE_50,
	"ERROR": ft.Colors.RED_50,
	"DEBUG": ft.Colors.GREY_50,
}


def level_colors(level: str) -> Tuple[str, str]:
	"""Return (fg,bg) colors for log level."""
	return (
		_LEVEL_COLOR_FG.get(level, ft.Colors.ON_SURFACE),
		_LEVEL_COLOR_BG.get(level, ft.Colors.SURFACE),
	)


def build_status_badge(text: str, status: str) -> ft.Control:
	"""Create a pill badge for statuses with consistent styling."""
	col = status_color(status)
	return ft.Container(
		content=ft.Text(text, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
		padding=ft.Padding(8, 4, 8, 4),
		border_radius=12,
		bgcolor=col,
		border=ft.border.all(1, col),
	)


def build_level_badge(level: str) -> ft.Control:
	"""Create a pill badge for log level using level_colors mapping."""
	fg, _bg = level_colors(level)
	return ft.Container(
		content=ft.Text(level, size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
		padding=ft.Padding(8, 4, 8, 4),
		bgcolor=fg,
		border_radius=12,
		border=ft.border.all(1, fg),
		alignment=ft.alignment.center,
	)


def striped_row_color(index: int) -> Optional[str]:
	"""Return subtle stripe color for even rows; odd rows transparent."""
	return ft.Colors.GREEN_50 if index % 2 == 0 else None


def compute_file_signature(file_dict: Dict[str, Any]):
	"""Return a lightweight immutable signature for a file row for future diffing."""
	return (
		file_dict.get("id"),
		file_dict.get("size"),
		file_dict.get("status"),
		file_dict.get("modified"),
	)

