"""responsive_layout.py

Unified Responsive Layout System for Material Design 3
====================================================

Provides a comprehensive responsive layout system that adapts to different
screen sizes and device types following Material Design 3 guidelines.

Design Principles:
- Mobile-first responsive design
- Material Design 3 breakpoint system
- Flexible grid layouts
- Adaptive component sizing
- Device type detection
- Performance-optimized layout calculations
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class BreakpointSize(Enum):
    """Material Design 3 breakpoint sizes."""
    XS = "xs"      # 0-599dp (Mobile)
    SM = "sm"      # 600-899dp (Tablet)
    MD = "md"      # 900-1199dp (Tablet/Laptop)
    LG = "lg"      # 1200-1799dp (Desktop)
    XL = "xl"      # 1800+dp (Large Desktop)


class DeviceType(Enum):
    """Device type classification."""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    LARGE_DESKTOP = "large_desktop"


@dataclass
class Breakpoint:
    """Breakpoint definition with size and device type."""
    size: BreakpointSize
    min_width: int
    max_width: int
    device_type: DeviceType
    columns: int
    gutter: int  # spacing between columns


class ResponsiveLayoutSystem:
    """Unified responsive layout system following Material Design 3 guidelines."""
    
    # Material Design 3 breakpoints
    BREAKPOINTS = {
        BreakpointSize.XS: Breakpoint(
            size=BreakpointSize.XS,
            min_width=0,
            max_width=599,
            device_type=DeviceType.MOBILE,
            columns=4,
            gutter=16
        ),
        BreakpointSize.SM: Breakpoint(
            size=BreakpointSize.SM,
            min_width=600,
            max_width=899,
            device_type=DeviceType.TABLET,
            columns=8,
            gutter=24
        ),
        BreakpointSize.MD: Breakpoint(
            size=BreakpointSize.MD,
            min_width=900,
            max_width=1199,
            device_type=DeviceType.TABLET,
            columns=12,
            gutter=24
        ),
        BreakpointSize.LG: Breakpoint(
            size=BreakpointSize.LG,
            min_width=1200,
            max_width=1799,
            device_type=DeviceType.DESKTOP,
            columns=12,
            gutter=24
        ),
        BreakpointSize.XL: Breakpoint(
            size=BreakpointSize.XL,
            min_width=1800,
            max_width=float('inf'),  # No maximum
            device_type=DeviceType.LARGE_DESKTOP,
            columns=12,
            gutter=24
        )
    }
    
    def __init__(self):
        self.current_breakpoint: Optional[Breakpoint] = None
        self.window_width: int = 0
    
    def update_window_size(self, width: int) -> None:
        """Update the current window size and determine the breakpoint."""
        self.window_width = width
        self.current_breakpoint = self._get_breakpoint_for_width(width)
    
    def _get_breakpoint_for_width(self, width: int) -> Breakpoint:
        """Get the appropriate breakpoint for a given width."""
        for breakpoint in self.BREAKPOINTS.values():
            if breakpoint.min_width <= width <= breakpoint.max_width:
                return breakpoint
        # Default to mobile if no match (shouldn't happen)
        return self.BREAKPOINTS[BreakpointSize.XS]
    
    def get_current_breakpoint(self) -> Breakpoint:
        """Get the current breakpoint."""
        if not self.current_breakpoint:
            # Default to mobile breakpoint
            return self.BREAKPOINTS[BreakpointSize.XS]
        return self.current_breakpoint
    
    def get_current_device_type(self) -> DeviceType:
        """Get the current device type."""
        return self.get_current_breakpoint().device_type
    
    def get_columns_for_current_breakpoint(self) -> int:
        """Get the number of columns for the current breakpoint."""
        return self.get_current_breakpoint().columns
    
    def get_gutter_for_current_breakpoint(self) -> int:
        """Get the gutter size for the current breakpoint."""
        return self.get_current_breakpoint().gutter
    
    def is_mobile(self) -> bool:
        """Check if current device is mobile."""
        return self.get_current_device_type() == DeviceType.MOBILE
    
    def is_tablet(self) -> bool:
        """Check if current device is tablet."""
        device_type = self.get_current_device_type()
        return device_type in [DeviceType.TABLET]
    
    def is_desktop(self) -> bool:
        """Check if current device is desktop or large desktop."""
        device_type = self.get_current_device_type()
        return device_type in [DeviceType.DESKTOP, DeviceType.LARGE_DESKTOP]
    
    def get_responsive_spacing(self, base_spacing: int) -> int:
        """Get responsive spacing based on current breakpoint."""
        breakpoint = self.get_current_breakpoint()
        # Adjust spacing based on device type
        multiplier = {
            DeviceType.MOBILE: 0.75,
            DeviceType.TABLET: 1.0,
            DeviceType.DESKTOP: 1.25,
            DeviceType.LARGE_DESKTOP: 1.5
        }.get(breakpoint.device_type, 1.0)
        
        return int(base_spacing * multiplier)
    
    def get_responsive_width(self, percentage: float = 1.0) -> int:
        """Get a responsive width based on current breakpoint."""
        breakpoint = self.get_current_breakpoint()
        available_width = breakpoint.max_width - (2 * breakpoint.gutter)
        return int(available_width * percentage)
    
    def get_grid_column_width(self, span: int = 1) -> int:
        """Calculate the width of a grid column span."""
        breakpoint = self.get_current_breakpoint()
        total_gutter_space = (breakpoint.columns - 1) * breakpoint.gutter
        available_width = breakpoint.max_width - (2 * breakpoint.gutter) - total_gutter_space
        column_width = available_width / breakpoint.columns
        return int((column_width * span) + ((span - 1) * breakpoint.gutter))


# Global responsive layout system instance
responsive_layout_system = ResponsiveLayoutSystem()


def get_responsive_layout_system() -> ResponsiveLayoutSystem:
    """Get the global responsive layout system instance."""
    return responsive_layout_system


# Convenience functions
def get_current_breakpoint() -> Breakpoint:
    """Get the current breakpoint."""
    return responsive_layout_system.get_current_breakpoint()


def get_current_device_type() -> DeviceType:
    """Get the current device type."""
    return responsive_layout_system.get_current_device_type()


def is_mobile() -> bool:
    """Check if current device is mobile."""
    return responsive_layout_system.is_mobile()


def is_tablet() -> bool:
    """Check if current device is tablet."""
    return responsive_layout_system.is_tablet()


def is_desktop() -> bool:
    """Check if current device is desktop."""
    return responsive_layout_system.is_desktop()