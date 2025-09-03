#!/usr/bin/env python3
"""
Responsive Design Enums and Configuration Classes

Extracted from the massive responsive.py file to provide focused, reusable enums
and configuration classes for responsive design without framework-fighting patterns.

This module contains only the essential enums and dataclasses needed for responsive
design decisions, keeping it under 200 lines and focused on configuration.
"""

import flet as ft
from typing import Optional
from enum import Enum
from dataclasses import dataclass

# Auto-enable UTF-8 for all subprocess operations
import Shared.utils.utf8_solution


class ScreenSize(Enum):
    """Screen size categories for responsive design"""
    MOBILE = "mobile"        # < 600px wide
    TABLET = "tablet"        # 600px - 1024px wide
    DESKTOP = "desktop"      # 1024px - 1440px wide
    WIDE_DESKTOP = "wide"    # > 1440px wide


class BreakpointSize(Enum):
    """Material Design 3 responsive breakpoint sizes"""
    COMPACT = "compact"      # 0-599 dp
    MEDIUM = "medium"        # 600-839 dp
    EXPANDED = "expanded"    # 840+ dp


class DeviceType(Enum):
    """Device type classification"""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"


class InteractionMethod(Enum):
    """Types of user interaction methods for touch target optimization"""
    MOUSE = "mouse"
    TOUCH = "touch"
    KEYBOARD = "keyboard"
    ACCESSIBILITY = "accessibility"


class DesktopBreakpoint(Enum):
    """Material Design 3 desktop breakpoints for desktop-focused layouts"""
    XS = "xs"      # < 600px - Very small windows
    SM = "sm"      # 600-905px - Small windows
    MD = "md"      # 905-1240px - Medium windows (13-16" displays)
    LG = "lg"      # 1240-1440px - Large windows (16-24" displays)
    XL = "xl"      # 1440-1920px - Extra large windows (24"+ displays)
    XXL = "xxl"    # > 1920px - Ultra large displays


class Breakpoint(Enum):
    """Standard responsive design breakpoints."""
    XS = "xs"    # Extra small devices (< 576px)
    SM = "sm"    # Small devices (≥ 576px)
    MD = "md"    # Medium devices (≥ 768px) 
    LG = "lg"    # Large devices (≥ 992px)
    XL = "xl"    # Extra large devices (≥ 1200px)
    XXL = "xxl"  # Extra extra large devices (≥ 1400px)


@dataclass
class BreakpointConfig:
    """Configuration for responsive breakpoints"""
    mobile_max: int = 599      # Maximum width for mobile
    tablet_max: int = 1023     # Maximum width for tablet
    desktop_max: int = 1439    # Maximum width for desktop
    # Wide desktop is anything above desktop_max


@dataclass
class BreakpointDataClass:
    """Responsive breakpoint definition with dataclass pattern"""
    name: str
    min_width: int
    max_width: Optional[int] = None
    device_type: DeviceType = DeviceType.DESKTOP
    
    def matches(self, width: int) -> bool:
        """Check if width matches this breakpoint"""
        min_match = width >= self.min_width
        max_match = self.max_width is None or width <= self.max_width
        return min_match and max_match


@dataclass
class TouchTargetSpec:
    """Touch target specifications for accessibility compliance"""
    min_width: int = 44          # Material Design minimum (44dp)
    min_height: int = 44         # Material Design minimum (44dp)
    min_spacing: int = 8         # Minimum spacing between targets
    touch_padding: int = 12      # Additional padding for touch
    accessibility_margin: int = 4   # Extra margin for accessibility


# Standard Material Design 3 breakpoints using dataclass pattern
STANDARD_MD3_BREAKPOINTS = [
    BreakpointDataClass("compact", 0, 599, DeviceType.MOBILE),
    BreakpointDataClass("medium", 600, 839, DeviceType.TABLET),
    BreakpointDataClass("expanded", 840, None, DeviceType.DESKTOP),
]


# Standard breakpoint values in pixels
STANDARD_BREAKPOINTS = {
    Breakpoint.XS: 0,
    Breakpoint.SM: 576,
    Breakpoint.MD: 768,
    Breakpoint.LG: 992,
    Breakpoint.XL: 1200,
    Breakpoint.XXL: 1400,
}


# Material Design 3 desktop breakpoints
MD3_DESKTOP_BREAKPOINTS = {
    DesktopBreakpoint.XS: {"min": 0, "max": 599, "name": "Extra Small"},
    DesktopBreakpoint.SM: {"min": 600, "max": 904, "name": "Small"},
    DesktopBreakpoint.MD: {"min": 905, "max": 1239, "name": "Medium"},
    DesktopBreakpoint.LG: {"min": 1240, "max": 1439, "name": "Large"},
    DesktopBreakpoint.XL: {"min": 1440, "max": 1919, "name": "Extra Large"},
    DesktopBreakpoint.XXL: {"min": 1920, "max": 4000, "name": "Extra Extra Large"}
}


# Default column spans for desktop layouts
DEFAULT_DESKTOP_COLUMN_SPANS = {
    DesktopBreakpoint.XS: 12,    # Full width on very small windows
    DesktopBreakpoint.SM: 12,    # Full width on small windows
    DesktopBreakpoint.MD: 6,     # Half width on medium displays
    DesktopBreakpoint.LG: 4,     # Third width on large displays
    DesktopBreakpoint.XL: 3,     # Quarter width on extra large displays
    DesktopBreakpoint.XXL: 2     # Sixth width on ultra large displays
}


# Column configurations for each breakpoint (total cols = 12)
COLUMN_CONFIGS = {
    Breakpoint.XS: {"default": 12, "half": 12, "third": 12, "quarter": 12},
    Breakpoint.SM: {"default": 12, "half": 6, "third": 12, "quarter": 6},
    Breakpoint.MD: {"default": 12, "half": 6, "third": 4, "quarter": 6},
    Breakpoint.LG: {"default": 6, "half": 6, "third": 4, "quarter": 3},
    Breakpoint.XL: {"default": 4, "half": 6, "third": 4, "quarter": 3},
    Breakpoint.XXL: {"default": 3, "half": 6, "third": 4, "quarter": 3},
}


# Responsive spacing values
SPACING_CONFIG = {
    Breakpoint.XS: {"small": 8, "medium": 12, "large": 16, "xlarge": 20},
    Breakpoint.SM: {"small": 10, "medium": 16, "large": 20, "xlarge": 24},
    Breakpoint.MD: {"small": 12, "medium": 18, "large": 24, "xlarge": 30},
    Breakpoint.LG: {"small": 14, "medium": 20, "large": 28, "xlarge": 36},
    Breakpoint.XL: {"small": 16, "medium": 24, "large": 32, "xlarge": 40},
    Breakpoint.XXL: {"small": 18, "medium": 28, "large": 36, "xlarge": 48},
}


# Container max-widths for each breakpoint
CONTAINER_MAX_WIDTHS = {
    Breakpoint.XS: "100%",
    Breakpoint.SM: 540,
    Breakpoint.MD: 720,
    Breakpoint.LG: 960,
    Breakpoint.XL: 1140,
    Breakpoint.XXL: 1320,
}


def get_current_breakpoint(width: float) -> Breakpoint:
    """
    Determine the current breakpoint based on screen width.
    
    Args:
        width: Screen width in pixels
        
    Returns:
        Breakpoint: The appropriate breakpoint enum value
    """
    if width >= STANDARD_BREAKPOINTS[Breakpoint.XXL]:
        return Breakpoint.XXL
    elif width >= STANDARD_BREAKPOINTS[Breakpoint.XL]:
        return Breakpoint.XL
    elif width >= STANDARD_BREAKPOINTS[Breakpoint.LG]:
        return Breakpoint.LG
    elif width >= STANDARD_BREAKPOINTS[Breakpoint.MD]:
        return Breakpoint.MD
    elif width >= STANDARD_BREAKPOINTS[Breakpoint.SM]:
        return Breakpoint.SM
    else:
        return Breakpoint.XS


def get_desktop_breakpoint(window_width: int) -> DesktopBreakpoint:
    """Get the appropriate desktop breakpoint for a given window width"""
    return next(
        (
            breakpoint
            for breakpoint, config in MD3_DESKTOP_BREAKPOINTS.items()
            if config["min"] <= window_width <= config["max"]
        ),
        DesktopBreakpoint.MD,
    )


def is_mobile(width: float) -> bool:
    """Check if the given width represents a mobile device."""
    breakpoint = get_current_breakpoint(width)
    return breakpoint in [Breakpoint.XS, Breakpoint.SM]


def is_tablet(width: float) -> bool:
    """Check if the given width represents a tablet device."""
    return get_current_breakpoint(width) == Breakpoint.MD


def is_desktop(width: float) -> bool:
    """Check if the given width represents a desktop device."""
    breakpoint = get_current_breakpoint(width)
    return breakpoint in [Breakpoint.LG, Breakpoint.XL, Breakpoint.XXL]


# ============================================================================
# BREAKPOINT MANAGER CLASS
# ============================================================================

class BreakpointManager:
    """
    Manages responsive breakpoints and provides utilities for adaptive layouts.
    
    This class provides methods to determine current breakpoint, get responsive
    configurations, and check device categories based on screen width.
    """
    
    # Use the constants already defined above
    BREAKPOINTS = STANDARD_BREAKPOINTS
    COLUMN_CONFIGS = COLUMN_CONFIGS
    SPACING_CONFIG = SPACING_CONFIG
    CONTAINER_MAX_WIDTHS = CONTAINER_MAX_WIDTHS
    
    @classmethod
    def get_current_breakpoint(cls, width: float) -> Breakpoint:
        """
        Determine the current breakpoint based on screen width.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            Breakpoint: The appropriate breakpoint enum value
        """
        return get_current_breakpoint(width)
    
    @classmethod
    def get_column_config(cls, breakpoint: Breakpoint) -> dict:
        """
        Get column configuration for the given breakpoint.
        
        Args:
            breakpoint: The breakpoint to get configuration for
            
        Returns:
            Dict containing column counts for different layout patterns
        """
        return cls.COLUMN_CONFIGS.get(breakpoint, cls.COLUMN_CONFIGS[Breakpoint.MD])
    
    @classmethod
    def get_columns_for_layout(cls, width: float, layout_type: str = "default") -> int:
        """
        Get number of columns for a specific layout type at the given width.
        
        Args:
            width: Screen width in pixels
            layout_type: Type of layout ("default", "half", "third", "quarter")
            
        Returns:
            Number of columns to use
        """
        current_breakpoint = cls.get_current_breakpoint(width)
        config = cls.get_column_config(current_breakpoint)
        return config.get(layout_type, config["default"])
    
    @classmethod
    def is_mobile(cls, width: float) -> bool:
        """Check if the given width represents a mobile device."""
        return is_mobile(width)
    
    @classmethod
    def is_tablet(cls, width: float) -> bool:
        """Check if the given width represents a tablet device."""
        return is_tablet(width)
    
    @classmethod
    def is_desktop(cls, width: float) -> bool:
        """Check if the given width represents a desktop device."""
        return is_desktop(width)
    
    @classmethod
    def get_responsive_spacing(cls, width: float, size: str = "medium") -> int:
        """
        Get responsive spacing value based on screen width.
        
        Args:
            width: Screen width in pixels
            size: Spacing size ("small", "medium", "large", "xlarge")
            
        Returns:
            Spacing value in pixels
        """
        breakpoint = cls.get_current_breakpoint(width)
        spacing_config = cls.SPACING_CONFIG.get(breakpoint, cls.SPACING_CONFIG[Breakpoint.MD])
        return spacing_config.get(size, spacing_config["medium"])
    
    @classmethod
    def get_container_max_width(cls, width: float) -> Optional[int]:
        """
        Get maximum container width for the current breakpoint.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            Maximum container width in pixels, or None for 100% width
        """
        breakpoint = cls.get_current_breakpoint(width)
        max_width = cls.CONTAINER_MAX_WIDTHS.get(breakpoint)
        return max_width if isinstance(max_width, int) else None


# ============================================================================
# SIMPLIFIED RESPONSIVE BUILDER
# ============================================================================

class ResponsiveBuilder:
    """
    Simplified utility class for building responsive UI components.
    
    This is a lightweight version that provides essential responsive building
    methods without the framework-fighting complexity of the original.
    """
    
    @staticmethod
    def create_responsive_row(
        controls: list,
        column_configs: Optional[dict] = None,
        spacing: Optional[int] = None,
        alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.START,
        **kwargs
    ) -> ft.ResponsiveRow:
        """
        Create a responsive row with automatic column configuration.
        
        Args:
            controls: List of controls to include in the row
            column_configs: Optional custom column configurations per control
            spacing: Optional custom spacing between controls
            alignment: Horizontal alignment of controls
            **kwargs: Additional ResponsiveRow properties
            
        Returns:
            Configured ResponsiveRow with responsive controls
        """
        responsive_controls = []
        for i, control in enumerate(controls):
            # Set default column configuration if not provided
            if not hasattr(control, 'col') or control.col is None:
                control.col = {"xs": 12, "sm": 6, "md": 4, "lg": 3}
            
            # Ensure expand is set for responsive behavior
            if not hasattr(control, 'expand') or control.expand is None:
                control.expand = True
                
            responsive_controls.append(control)
            
        return ft.ResponsiveRow(
            controls=responsive_controls,
            spacing=spacing or 20,
            alignment=alignment,
            **kwargs
        )
    
    @staticmethod
    def create_adaptive_container(
        content: ft.Control,
        responsive_padding: bool = True,
        **kwargs
    ) -> ft.Container:
        """
        Create an adaptive container that responds to screen size changes.
        
        Args:
            content: The control to wrap in the container
            responsive_padding: Whether to apply responsive padding
            **kwargs: Additional Container properties
            
        Returns:
            Configured Container with adaptive properties
        """
        container_kwargs = kwargs.copy()
        
        # Set responsive width behavior
        if 'expand' not in container_kwargs:
            container_kwargs['expand'] = True
            
        # Apply responsive padding if enabled
        if responsive_padding and 'padding' not in container_kwargs:
            container_kwargs['padding'] = 16  # Simple default padding
            
        return ft.Container(
            content=content,
            **container_kwargs
        )