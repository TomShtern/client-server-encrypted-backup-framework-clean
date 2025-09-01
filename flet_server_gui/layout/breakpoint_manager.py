#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Breakpoint Management System for Responsive Layouts

Single Responsibility: This module is dedicated exclusively to screen detection, 
breakpoint calculation, and responsive configuration management. It provides 
the core logic for determining appropriate UI configurations based on screen 
dimensions without coupling to specific UI components or layout implementations.

Extracted from: flet_server_gui/ui/responsive_layout.py
Purpose: Decompose God Component by extracting breakpoint management logic
Status: Phase 2 UI Layer Decomposition - Specialized Component

Key Features:
- Material Design 3 breakpoint definitions
- Screen size detection and categorization  
- Responsive spacing and layout calculations
- Device type classification (mobile/tablet/desktop)
- Column span configuration for different breakpoints
- Font scaling and container sizing logic
"""

import Shared.utils.utf8_solution  # Auto-enable UTF-8 for all subprocess operations

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class ScreenSize(Enum):
    """Screen size categories for responsive design"""
    MOBILE = "mobile"        # < 600px wide
    TABLET = "tablet"        # 600px - 1024px wide
    DESKTOP = "desktop"      # 1024px - 1440px wide
    WIDE_DESKTOP = "wide"    # > 1440px wide


class BreakpointSize(Enum):
    """Material Design 3 responsive breakpoint sizes (consolidated from core/responsive_layout.py)"""
    COMPACT = "compact"      # 0-599 dp
    MEDIUM = "medium"        # 600-839 dp
    EXPANDED = "expanded"    # 840+ dp


class DeviceType(Enum):
    """Device type classification (consolidated from core/responsive_layout.py)"""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"


class StandardBreakpoint(Enum):
    """Standard responsive design breakpoints (consolidated from layouts/breakpoint_manager.py)."""
    XS = "xs"    # Extra small devices (< 576px)
    SM = "sm"    # Small devices (≥ 576px)
    MD = "md"    # Medium devices (≥ 768px) 
    LG = "lg"    # Large devices (≥ 992px)
    XL = "xl"    # Extra large devices (≥ 1200px)
    XXL = "xxl"  # Extra extra large devices (≥ 1400px)


class DesktopBreakpoint(Enum):
    """Material Design 3 desktop breakpoints (consolidated from ui/layouts/md3_desktop_breakpoints.py)"""
    XS = "xs"      # < 600px - Very small windows
    SM = "sm"      # 600-905px - Small windows
    MD = "md"      # 905-1240px - Medium windows (13-16" displays)
    LG = "lg"      # 1240-1440px - Large windows (16-24" displays)
    XL = "xl"      # 1440-1920px - Extra large windows (24"+ displays)
    XXL = "xxl"    # > 1920px - Ultra large displays


@dataclass
class BreakpointConfig:
    """Configuration for responsive breakpoints"""
    mobile_max: int = 599      # Maximum width for mobile
    tablet_max: int = 1023     # Maximum width for tablet
    desktop_max: int = 1439    # Maximum width for desktop
    # Wide desktop is anything above desktop_max


@dataclass
class Breakpoint:
    """Responsive breakpoint definition (consolidated from core/responsive_layout.py)"""
    name: str
    min_width: int
    max_width: Optional[int] = None
    device_type: DeviceType = DeviceType.DESKTOP
    
    def matches(self, width: int) -> bool:
        """Check if width matches this breakpoint"""
        min_match = width >= self.min_width
        max_match = self.max_width is None or width <= self.max_width
        return min_match and max_match


# Standard Material Design 3 breakpoints (consolidated from core/responsive_layout.py)
STANDARD_MD3_BREAKPOINTS: List[Breakpoint] = [
    Breakpoint("compact", 0, 599, DeviceType.MOBILE),
    Breakpoint("medium", 600, 839, DeviceType.TABLET),
    Breakpoint("expanded", 840, None, DeviceType.DESKTOP),
]


class BreakpointManager:
    """
    Comprehensive breakpoint system for responsive layouts (consolidated from layouts/breakpoint_manager.py).
    
    This class provides methods to determine current breakpoint, get responsive
    configurations, and check device categories based on screen width.
    """
    
    # Standard breakpoint values in pixels
    BREAKPOINTS = {
        StandardBreakpoint.XS: 0,
        StandardBreakpoint.SM: 576,
        StandardBreakpoint.MD: 768,
        StandardBreakpoint.LG: 992,
        StandardBreakpoint.XL: 1200,
        StandardBreakpoint.XXL: 1400,
    }
    
    # Column configurations for each breakpoint (total cols = 12)
    COLUMN_CONFIGS = {
        StandardBreakpoint.XS: {"default": 12, "half": 12, "third": 12, "quarter": 12},
        StandardBreakpoint.SM: {"default": 12, "half": 6, "third": 12, "quarter": 6},
        StandardBreakpoint.MD: {"default": 12, "half": 6, "third": 4, "quarter": 6},
        StandardBreakpoint.LG: {"default": 6, "half": 6, "third": 4, "quarter": 3},
        StandardBreakpoint.XL: {"default": 4, "half": 6, "third": 4, "quarter": 3},
        StandardBreakpoint.XXL: {"default": 3, "half": 6, "third": 4, "quarter": 3},
    }
    
    # Responsive spacing values
    SPACING_CONFIG = {
        StandardBreakpoint.XS: {"small": 8, "medium": 12, "large": 16, "xlarge": 20},
        StandardBreakpoint.SM: {"small": 10, "medium": 16, "large": 20, "xlarge": 24},
        StandardBreakpoint.MD: {"small": 12, "medium": 18, "large": 24, "xlarge": 30},
        StandardBreakpoint.LG: {"small": 14, "medium": 20, "large": 28, "xlarge": 36},
        StandardBreakpoint.XL: {"small": 16, "medium": 24, "large": 32, "xlarge": 40},
        StandardBreakpoint.XXL: {"small": 18, "medium": 28, "large": 36, "xlarge": 48},
    }
    
    # Container max-widths for each breakpoint
    CONTAINER_MAX_WIDTHS = {
        StandardBreakpoint.XS: "100%",
        StandardBreakpoint.SM: 540,
        StandardBreakpoint.MD: 720,
        StandardBreakpoint.LG: 960,
        StandardBreakpoint.XL: 1140,
        StandardBreakpoint.XXL: 1320,
    }
    
    @classmethod
    def get_current_breakpoint(cls, width: float) -> StandardBreakpoint:
        """
        Determine the current breakpoint based on screen width.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            StandardBreakpoint: The appropriate breakpoint enum value
        """
        if width >= cls.BREAKPOINTS[StandardBreakpoint.XXL]:
            return StandardBreakpoint.XXL
        elif width >= cls.BREAKPOINTS[StandardBreakpoint.XL]:
            return StandardBreakpoint.XL
        elif width >= cls.BREAKPOINTS[StandardBreakpoint.LG]:
            return StandardBreakpoint.LG
        elif width >= cls.BREAKPOINTS[StandardBreakpoint.MD]:
            return StandardBreakpoint.MD
        elif width >= cls.BREAKPOINTS[StandardBreakpoint.SM]:
            return StandardBreakpoint.SM
        else:
            return StandardBreakpoint.XS
    
    @classmethod
    def get_column_config(cls, breakpoint: StandardBreakpoint) -> Dict[str, int]:
        """
        Get column configuration for the given breakpoint.
        
        Args:
            breakpoint: The breakpoint to get configuration for
            
        Returns:
            Dict containing column counts for different layout patterns
        """
        return cls.COLUMN_CONFIGS.get(breakpoint, cls.COLUMN_CONFIGS[StandardBreakpoint.MD])
    
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
        """
        Check if the given width represents a mobile device.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            True if mobile (xs or sm), False otherwise
        """
        current_breakpoint = cls.get_current_breakpoint(width)
        return current_breakpoint in [StandardBreakpoint.XS, StandardBreakpoint.SM]
    
    @classmethod
    def is_tablet(cls, width: float) -> bool:
        """
        Check if the given width represents a tablet device.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            True if tablet (md), False otherwise
        """
        return cls.get_current_breakpoint(width) == StandardBreakpoint.MD
    
    @classmethod
    def is_desktop(cls, width: float) -> bool:
        """
        Check if the given width represents a desktop device.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            True if desktop (lg, xl, or xxl), False otherwise
        """
        breakpoint = cls.get_current_breakpoint(width)
        return breakpoint in [StandardBreakpoint.LG, StandardBreakpoint.XL, StandardBreakpoint.XXL]
    
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
        spacing_config = cls.SPACING_CONFIG.get(breakpoint, cls.SPACING_CONFIG[StandardBreakpoint.MD])
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
    
    @classmethod
    def get_responsive_font_scale(cls, width: float) -> float:
        """
        Get font scaling factor based on screen width.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            Font scaling factor (e.g., 0.8 for smaller, 1.2 for larger)
        """
        breakpoint = cls.get_current_breakpoint(width)
        scales = {
            StandardBreakpoint.XS: 0.85,
            StandardBreakpoint.SM: 0.9,
            StandardBreakpoint.MD: 1.0,
            StandardBreakpoint.LG: 1.05,
            StandardBreakpoint.XL: 1.1,
            StandardBreakpoint.XXL: 1.15,
        }
        return scales.get(breakpoint, 1.0)
    
    @classmethod
    def should_stack_components(cls, width: float) -> bool:
        """
        Determine if components should stack vertically based on screen width.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            True if components should stack (mobile/tablet), False otherwise
        """
        return cls.is_mobile(width) or cls.is_tablet(width)
    
    @classmethod
    def get_grid_breakpoint_config(cls, width: float) -> Dict[str, Any]:
        """
        Get comprehensive grid configuration for current breakpoint.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            Dictionary with complete responsive configuration
        """
        breakpoint = cls.get_current_breakpoint(width)
        
        return {
            "breakpoint": breakpoint.value,
            "is_mobile": cls.is_mobile(width),
            "is_tablet": cls.is_tablet(width),
            "is_desktop": cls.is_desktop(width),
            "should_stack": cls.should_stack_components(width),
            "columns": cls.get_column_config(breakpoint),
            "spacing": cls.SPACING_CONFIG.get(breakpoint, cls.SPACING_CONFIG[StandardBreakpoint.MD]),
            "container_max_width": cls.get_container_max_width(width),
            "font_scale": cls.get_responsive_font_scale(width),
        }


class MD3DesktopBreakpoints:
    """
    Material Design 3 desktop breakpoint system (consolidated from ui/layouts/md3_desktop_breakpoints.py)
    """
    
    # Breakpoint definitions (desktop-focused)
    BREAKPOINTS = {
        DesktopBreakpoint.XS: {"min": 0, "max": 599, "name": "Extra Small"},
        DesktopBreakpoint.SM: {"min": 600, "max": 904, "name": "Small"},
        DesktopBreakpoint.MD: {"min": 905, "max": 1239, "name": "Medium"},
        DesktopBreakpoint.LG: {"min": 1240, "max": 1439, "name": "Large"},
        DesktopBreakpoint.XL: {"min": 1440, "max": 1919, "name": "Extra Large"},
        DesktopBreakpoint.XXL: {"min": 1920, "max": 4000, "name": "Extra Extra Large"}
    }
    
    # Default column spans for desktop layouts
    DEFAULT_COLUMN_SPANS = {
        DesktopBreakpoint.XS: 12,    # Full width on very small windows
        DesktopBreakpoint.SM: 12,    # Full width on small windows
        DesktopBreakpoint.MD: 6,     # Half width on medium displays
        DesktopBreakpoint.LG: 4,     # Third width on large displays
        DesktopBreakpoint.XL: 3,     # Quarter width on extra large displays
        DesktopBreakpoint.XXL: 2     # Sixth width on ultra large displays
    }
    
    @staticmethod
    def get_breakpoint(window_width: int) -> DesktopBreakpoint:
        """Get the appropriate breakpoint for a given window width"""
        return next(
            (
                breakpoint
                for breakpoint, config in MD3DesktopBreakpoints.BREAKPOINTS.items()
                if config["min"] <= window_width <= config["max"]
            ),
            DesktopBreakpoint.MD,
        )
    
    @staticmethod
    def get_column_span(window_width: int) -> int:
        """Get appropriate column span for a given window width"""
        breakpoint = MD3DesktopBreakpoints.get_breakpoint(window_width)
        return MD3DesktopBreakpoints.DEFAULT_COLUMN_SPANS.get(breakpoint, 6)
    
    @staticmethod
    def create_responsive_column_config() -> Dict[str, int]:
        """Create a comprehensive column configuration for desktop layouts"""
        return {
            "xs": 12,   # Very small windows - full width
            "sm": 12,   # Small windows - full width
            "md": 6,    # Medium displays - half width
            "lg": 4,    # Large displays - third width
            "xl": 3,    # Extra large displays - quarter width
            "xxl": 2    # Ultra large displays - sixth width
        }