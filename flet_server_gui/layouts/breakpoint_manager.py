"""
Breakpoint management system for responsive layouts in Flet GUI.

This module provides a comprehensive breakpoint system based on standard responsive 
design patterns, allowing components to adapt to different screen sizes.
"""

from typing import Dict, Any, Optional, Tuple
from enum import Enum


class Breakpoint(Enum):
    """Standard responsive design breakpoints."""
    XS = "xs"    # Extra small devices (< 576px)
    SM = "sm"    # Small devices (≥ 576px)
    MD = "md"    # Medium devices (≥ 768px) 
    LG = "lg"    # Large devices (≥ 992px)
    XL = "xl"    # Extra large devices (≥ 1200px)
    XXL = "xxl"  # Extra extra large devices (≥ 1400px)


class BreakpointManager:
    """
    Manages responsive breakpoints and provides utilities for adaptive layouts.
    
    This class provides methods to determine current breakpoint, get responsive
    configurations, and check device categories based on screen width.
    """
    
    # Standard breakpoint values in pixels
    BREAKPOINTS = {
        Breakpoint.XS: 0,
        Breakpoint.SM: 576,
        Breakpoint.MD: 768,
        Breakpoint.LG: 992,
        Breakpoint.XL: 1200,
        Breakpoint.XXL: 1400,
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
    
    @classmethod
    def get_current_breakpoint(cls, width: float) -> Breakpoint:
        """
        Determine the current breakpoint based on screen width.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            Breakpoint: The appropriate breakpoint enum value
        """
        if width >= cls.BREAKPOINTS[Breakpoint.XXL]:
            return Breakpoint.XXL
        elif width >= cls.BREAKPOINTS[Breakpoint.XL]:
            return Breakpoint.XL
        elif width >= cls.BREAKPOINTS[Breakpoint.LG]:
            return Breakpoint.LG
        elif width >= cls.BREAKPOINTS[Breakpoint.MD]:
            return Breakpoint.MD
        elif width >= cls.BREAKPOINTS[Breakpoint.SM]:
            return Breakpoint.SM
        else:
            return Breakpoint.XS
    
    @classmethod
    def get_column_config(cls, breakpoint: Breakpoint) -> Dict[str, int]:
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
            layout_type: Type of layout ("default", "compact", "spacious")
            
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
        return current_breakpoint in [Breakpoint.XS, Breakpoint.SM]
    
    @classmethod
    def is_tablet(cls, width: float) -> bool:
        """
        Check if the given width represents a tablet device.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            True if tablet (md), False otherwise
        """
        return cls.get_current_breakpoint(width) == Breakpoint.MD
    
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
        return breakpoint in [Breakpoint.LG, Breakpoint.XL, Breakpoint.XXL]
    
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
            Breakpoint.XS: 0.85,
            Breakpoint.SM: 0.9,
            Breakpoint.MD: 1.0,
            Breakpoint.LG: 1.05,
            Breakpoint.XL: 1.1,
            Breakpoint.XXL: 1.15,
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
            "spacing": cls.SPACING_CONFIG.get(breakpoint, cls.SPACING_CONFIG[Breakpoint.MD]),
            "container_max_width": cls.get_container_max_width(width),
            "font_scale": cls.get_responsive_font_scale(width),
        }