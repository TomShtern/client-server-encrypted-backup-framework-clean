"""
Professional color system for log levels with distinct, recognizable colors.
Each level has a primary color, background tint, and semantic meaning.
Compatible with Flet 0.28.3
"""

import flet as ft


class LogColorSystem:
    """
    Professional color system with distinct, recognizable colors.
    Each level has a primary color, background tint, and semantic meaning.
    """

    # Color definitions optimized for both dark and light themes
    COLORS = {
        "DEBUG": {
            "primary": "#94A3B8",      # Slate gray - neutral, technical
            "secondary": "#CBD5E1",
            "bg_light": "#F8FAFC",
            "bg_dark": "#1E293B",
            "icon": ft.Icons.BUG_REPORT_ROUNDED,
            "label": "DEBUG",
            "description": "Debug information",
        },
        "INFO": {
            "primary": "#3B82F6",      # Bright blue - informational, clear
            "secondary": "#60A5FA",
            "bg_light": "#EFF6FF",
            "bg_dark": "#1E3A8A",
            "icon": ft.Icons.INFO_ROUNDED,
            "label": "INFO",
            "description": "General information",
        },
        "SUCCESS": {
            "primary": "#10B981",      # Emerald green - positive, successful
            "secondary": "#34D399",
            "bg_light": "#ECFDF5",
            "bg_dark": "#064E3B",
            "icon": ft.Icons.CHECK_CIRCLE_ROUNDED,
            "label": "SUCCESS",
            "description": "Successful operation",
        },
        "WARNING": {
            "primary": "#EAB308",      # Yellow - caution, attention needed
            "secondary": "#FDE047",
            "bg_light": "#FEFCE8",
            "bg_dark": "#713F12",
            "icon": ft.Icons.WARNING_ROUNDED,
            "label": "WARNING",
            "description": "Warning - review needed",
        },
        "IMPORTANT": {
            "primary": "#F97316",      # Orange - important warning, urgent
            "secondary": "#FB923C",
            "bg_light": "#FFF7ED",
            "bg_dark": "#7C2D12",
            "icon": ft.Icons.PRIORITY_HIGH_ROUNDED,
            "label": "IMPORTANT",
            "description": "Important warning",
        },
        "ERROR": {
            "primary": "#EF4444",      # Red - error, failure
            "secondary": "#F87171",
            "bg_light": "#FEF2F2",
            "bg_dark": "#7F1D1D",
            "icon": ft.Icons.ERROR_ROUNDED,
            "label": "ERROR",
            "description": "Error occurred",
        },
        "CRITICAL": {
            "primary": "#DC2626",      # Deep red - critical, severe
            "secondary": "#EF4444",
            "bg_light": "#FEE2E2",
            "bg_dark": "#991B1B",
            "icon": ft.Icons.DANGEROUS_ROUNDED,
            "label": "CRITICAL",
            "description": "Critical failure",
        },
        "SPECIAL": {
            "primary": "#A855F7",      # Purple - special events, unique
            "secondary": "#C084FC",
            "bg_light": "#FAF5FF",
            "bg_dark": "#581C87",
            "icon": ft.Icons.STARS_ROUNDED,
            "label": "SPECIAL",
            "description": "Special event",
        },
    }

    @staticmethod
    def get_level_config(level: str) -> dict:
        """Get complete color configuration for a log level"""
        return LogColorSystem.COLORS.get(level, LogColorSystem.COLORS["INFO"])

    @staticmethod
    def get_surface_tint(color: str, opacity: float = 0.05) -> str:
        """Create subtle surface tint for neomorphic backgrounds"""
        return ft.Colors.with_opacity(opacity, color)

    @staticmethod
    def get_border_color(color: str, opacity: float = 0.15) -> str:
        """Create border color with appropriate opacity"""
        return ft.Colors.with_opacity(opacity, color)
