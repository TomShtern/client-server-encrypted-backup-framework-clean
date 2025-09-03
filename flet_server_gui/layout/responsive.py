#!/usr/bin/env python3
"""
Responsive Design and Breakpoint Management System (Consolidated)

This module provides comprehensive responsive design utilities and breakpoint management,
consolidated from multiple separate files to eliminate duplication and provide a single
source of truth for all responsive/breakpoint functionality.

Consolidated from:
- flet_server_gui/layout/responsive.py (original comprehensive system)
- flet_server_gui/layout/breakpoint_manager.py (duplicate functionality + MD3 desktop components)
- flet_server_gui/layout/responsive_layout_utils.py (unique utilities + ResponsiveLayoutFactory)
- flet_server_gui/layout/responsive_fixes.py (specialized accessibility and layout fixes)

Purpose: Screen size detection, layout adaptation, responsive containers and layout helpers
Logic: Material Design 3 breakpoint definitions, device classification, responsive calculations
UI: Responsive UI component builders and adaptive layout patterns

Phase 2.1 Layout Deduplication - Absorption Method Applied
Phase 2.2 Layout Deduplication - Absorbed unique utilities from responsive_layout_utils.py  
Phase 2.3 Layout Deduplication - Absorbed specialized layout fixes from responsive_fixes.py
Status: Complete consolidated responsive system with factory patterns, enhanced utilities, and accessibility fixes
"""

import flet as ft
from typing import List, Dict, Any, Optional, Union, Callable, Tuple, Set
from enum import Enum
from dataclasses import dataclass

# Auto-enable UTF-8 for all subprocess operations
import Shared.utils.utf8_solution

# ============================================================================
# ENHANCED BREAKPOINT SYSTEM (Consolidated from multiple sources)
# ============================================================================

# Additional enums from breakpoint_manager.py
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
STANDARD_MD3_BREAKPOINTS: List[BreakpointDataClass] = [
    BreakpointDataClass("compact", 0, 599, DeviceType.MOBILE),
    BreakpointDataClass("medium", 600, 839, DeviceType.TABLET),
    BreakpointDataClass("expanded", 840, None, DeviceType.DESKTOP),
]


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
        breakpoint = cls.get_current_breakpoint(width)
        return breakpoint in [Breakpoint.XS, Breakpoint.SM]
    
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

# ============================================================================
# RESPONSIVE BUILDER (consolidated from responsive_utils.py)
# ============================================================================

class ResponsiveBuilder:
    """
    Static utility class for building responsive UI components.
    
    Provides methods to create adaptive layouts, containers, and UI elements
    that automatically adjust to different screen sizes and breakpoints.
    """
    
    @staticmethod
    def create_responsive_row(
        controls: List[ft.Control],
        column_configs: Optional[Dict[str, Union[int, Dict[str, int]]]] = None,
        spacing: Optional[int] = None,
        alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.START,
        vertical_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER,
        wrap: bool = False,
        **kwargs
    ) -> ft.ResponsiveRow:
        """
        Create a responsive row with automatic column configuration.
        
        Args:
            controls: List of controls to include in the row
            column_configs: Optional custom column configurations per control
            spacing: Optional custom spacing between controls
            alignment: Horizontal alignment of controls
            vertical_alignment: Vertical alignment of controls
            wrap: Whether to wrap controls to next line
            **kwargs: Additional ResponsiveRow properties
            
        Returns:
            Configured ResponsiveRow with responsive controls
        """
        responsive_controls = []

        for i, control in enumerate(controls):
            # Set column configuration if provided
            if column_configs:
                if i < len(column_configs):
                    config_key = list(column_configs.keys())[i]
                    col_config = column_configs[config_key]

                    if hasattr(control, 'col'):
                        control.col = (
                            col_config
                            if isinstance(col_config, dict)
                            else {"xs": 12, "sm": 6, "md": 4, "lg": col_config}
                        )
            elif not hasattr(control, 'col') or control.col is None:
                control.col = {"xs": 12, "sm": 6, "md": 4, "lg": 3}

            # Ensure expand is set for responsive behavior
            if not hasattr(control, 'expand') or control.expand is None:
                control.expand = True

            responsive_controls.append(control)

        return ft.ResponsiveRow(
            controls=responsive_controls,
            spacing=spacing or 20,
            alignment=alignment,
            vertical_alignment=vertical_alignment,
            **kwargs
        )
    
    @staticmethod
    def create_adaptive_container(
        content: ft.Control,
        width: Optional[float] = None,
        min_width: Optional[float] = None,
        max_width: Optional[float] = None,
        responsive_padding: bool = True,
        responsive_margin: bool = True,
        breakpoint_configs: Optional[Dict[str, Dict[str, Any]]] = None,
        **kwargs
    ) -> ft.Container:
        """
        Create an adaptive container that responds to screen size changes.
        
        Args:
            content: The control to wrap in the container
            width: Base width (will be made responsive if None)
            min_width: Minimum width constraint
            max_width: Maximum width constraint  
            responsive_padding: Whether to apply responsive padding
            responsive_margin: Whether to apply responsive margin
            breakpoint_configs: Custom configurations per breakpoint
            **kwargs: Additional Container properties
            
        Returns:
            Configured Container with adaptive properties
        """
        container_kwargs = kwargs.copy()
        
        # Set responsive width behavior
        if width is None and 'expand' not in container_kwargs:
            container_kwargs['expand'] = True
            
        # Apply responsive padding if enabled
        if responsive_padding and 'padding' not in container_kwargs:
            container_kwargs['padding'] = ft.padding.symmetric(
                horizontal=16, vertical=12
            )
            
        # Apply responsive margin if enabled
        if responsive_margin and 'margin' not in container_kwargs:
            container_kwargs['margin'] = ft.margin.symmetric(
                horizontal=8, vertical=4
            )
        
        return ft.Container(
            content=content,
            width=width,
            **container_kwargs
        )
    
    @staticmethod
    def get_adaptive_padding(
        width: float,
        size: str = "medium",
        symmetric: bool = True
    ) -> Union[int, ft.Padding]:
        """
        Get adaptive padding based on screen width.
        
        Args:
            width: Current screen width in pixels
            size: Padding size category ("small", "medium", "large", "xlarge")
            symmetric: Whether to return symmetric padding
            
        Returns:
            Padding value or ft.Padding object
        """
        padding_value = BreakpointManager.get_responsive_spacing(width, size)

        return ft.padding.all(padding_value) if symmetric else padding_value
    
    @staticmethod
    def get_adaptive_margin(
        width: float,
        size: str = "medium",
        symmetric: bool = True
    ) -> Union[int, ft.Margin]:
        """
        Get adaptive margin based on screen width.
        
        Args:
            width: Current screen width in pixels
            size: Margin size category ("small", "medium", "large", "xlarge")
            symmetric: Whether to return symmetric margin
            
        Returns:
            Margin value or ft.Margin object
        """
        margin_value = BreakpointManager.get_responsive_spacing(width, size)

        return ft.margin.all(margin_value) if symmetric else margin_value
    
    @staticmethod
    def get_responsive_font_size(
        width: float,
        base_size: int = 14,
        scale_factor: Optional[float] = None
    ) -> int:
        """
        Calculate responsive font size based on screen width.
        
        Args:
            width: Current screen width in pixels
            base_size: Base font size in pixels
            scale_factor: Optional custom scaling factor
            
        Returns:
            Scaled font size in pixels
        """
        if scale_factor is None:
            scale_factor = BreakpointManager.get_responsive_font_scale(width)
            
        return int(base_size * scale_factor)
    
    @staticmethod
    def create_responsive_card(
        content: ft.Control,
        width: Optional[float] = None,
        elevation: Optional[int] = None,
        responsive_elevation: bool = True,
        responsive_padding: bool = True,
        **kwargs
    ) -> ft.Card:
        """
        Create a responsive card that adapts to screen size.
        
        Args:
            content: Content to display in the card
            width: Optional fixed width (None for responsive)
            elevation: Optional fixed elevation
            responsive_elevation: Whether to scale elevation responsively
            responsive_padding: Whether to apply responsive padding to content
            **kwargs: Additional Card properties
            
        Returns:
            Configured responsive Card
        """
        card_kwargs = kwargs.copy()
        
        # Set responsive elevation
        if elevation is None and responsive_elevation:
            # Lower elevation on mobile for flatter design
            elevation = 2
            
        # Ensure expand behavior for responsive width
        if width is None and 'expand' not in card_kwargs:
            card_kwargs['expand'] = True
        
        # Wrap content with responsive padding if enabled
        if responsive_padding:
            content = ft.Container(
                content=content,
                padding=ft.padding.all(16),
                expand=True
            )
            
        return ft.Card(
            content=content,
            width=width,
            elevation=elevation,
            **card_kwargs
        )
    
    @staticmethod
    def create_responsive_column(
        controls: List[ft.Control],
        spacing: Optional[int] = None,
        responsive_spacing: bool = True,
        tight: Optional[bool] = None,
        **kwargs
    ) -> ft.Column:
        """
        Create a responsive column with adaptive spacing.
        
        Args:
            controls: List of controls in the column
            spacing: Optional fixed spacing between controls
            responsive_spacing: Whether to calculate spacing responsively
            tight: Whether to use tight layout
            **kwargs: Additional Column properties
            
        Returns:
            Configured responsive Column
        """
        column_kwargs = kwargs.copy()
        
        # Set default tight behavior for responsive layouts
        if tight is None:
            tight = False
            
        # Ensure expand for responsive behavior
        if 'expand' not in column_kwargs:
            column_kwargs['expand'] = True
            
        return ft.Column(
            controls=controls,
            spacing=spacing or 16,
            tight=tight,
            **column_kwargs
        )
    
    @staticmethod
    def create_responsive_grid(
        controls: List[ft.Control],
        width: float,
        max_extent: Optional[float] = None,
        child_aspect_ratio: float = 1.0,
        spacing: Optional[int] = None,
        **kwargs
    ) -> ft.GridView:
        """
        Create a responsive grid that adapts to screen width.
        
        Args:
            controls: List of controls to display in grid
            width: Current screen width
            max_extent: Maximum extent of each grid item
            child_aspect_ratio: Aspect ratio of grid children
            spacing: Spacing between grid items
            **kwargs: Additional GridView properties
            
        Returns:
            Configured responsive GridView
        """
        # Calculate responsive max extent
        if max_extent is None:
            if BreakpointManager.is_mobile(width):
                max_extent = width / 2 - 20  # 2 columns on mobile
            elif BreakpointManager.is_tablet(width):
                max_extent = width / 3 - 20  # 3 columns on tablet
            else:
                max_extent = width / 4 - 20  # 4 columns on desktop
                
        # Get responsive spacing
        if spacing is None:
            spacing = BreakpointManager.get_responsive_spacing(width, "medium")
            
        return ft.GridView(
            controls=controls,
            max_extent=max_extent,
            child_aspect_ratio=child_aspect_ratio,
            spacing=spacing,
            **kwargs
        )
    
    @staticmethod
    def create_breakpoint_specific_layout(
        width: float,
        layouts: Dict[str, Callable[[], ft.Control]]
    ) -> ft.Control:
        """
        Create a layout that changes completely based on breakpoint.
        
        Args:
            width: Current screen width
            layouts: Dictionary mapping breakpoint names to layout functions
            
        Returns:
            The appropriate layout for the current breakpoint
        """
        breakpoint = BreakpointManager.get_current_breakpoint(width)
        
        # Try specific breakpoint first
        if breakpoint.value in layouts:
            return layouts[breakpoint.value]()
            
        # Fallback hierarchy
        fallbacks = {
            "xs": ["mobile", "sm", "default"],
            "sm": ["mobile", "xs", "default"],
            "md": ["tablet", "sm", "mobile", "default"],
            "lg": ["desktop", "md", "tablet", "default"],
            "xl": ["desktop", "lg", "md", "default"],
            "xxl": ["desktop", "xl", "lg", "default"]
        }
        
        for fallback in fallbacks.get(breakpoint.value, ["default"]):
            if fallback in layouts:
                return layouts[fallback]()
                
        # Final fallback to first available layout
        return list(layouts.values())[0]()
    
    @staticmethod
    def get_responsive_text_style(
        width: float,
        base_style: Optional[ft.TextStyle] = None,
        scale_size: bool = True
    ) -> ft.TextStyle:
        """
        Get a responsive text style that scales with screen size.
        
        Args:
            width: Current screen width
            base_style: Base text style to modify
            scale_size: Whether to scale the font size
            
        Returns:
            Responsive TextStyle
        """
        if base_style is None:
            base_style = ft.TextStyle()
        
        # Create a copy of the base style
        responsive_style = ft.TextStyle(
            size=base_style.size,
            weight=base_style.weight,
            color=base_style.color,
            bgcolor=base_style.bgcolor,
            decoration=base_style.decoration,
            font_family=base_style.font_family,
            italic=base_style.italic
        )
        
        if scale_size and responsive_style.size:
            scale_factor = BreakpointManager.get_responsive_font_scale(width)
            responsive_style.size = int(responsive_style.size * scale_factor)
            
        return responsive_style
    
    @staticmethod
    def create_adaptive_app_bar(
        title: str,
        width: float,
        actions: Optional[List[ft.Control]] = None,
        compact: Optional[bool] = None,
        **kwargs
    ) -> ft.AppBar:
        """
        Create an adaptive app bar that adjusts to screen size.
        
        Args:
            title: App bar title
            width: Current screen width
            actions: Optional action controls
            compact: Whether to use compact layout (auto-determined if None)
            **kwargs: Additional AppBar properties
            
        Returns:
            Configured adaptive AppBar
        """
        if compact is None:
            compact = BreakpointManager.is_mobile(width)
            
        # Limit actions on mobile
        if BreakpointManager.is_mobile(width) and actions and len(actions) > 2:
            actions = actions[:2]  # Show only first 2 actions on mobile
            
        return ft.AppBar(
            title=ft.Text(title),
            actions=actions,
            **kwargs
        )
    
    # ============================================================================
    # ABSORBED UNIQUE UTILITIES FROM responsive_layout_utils.py
    # ============================================================================
    
    @staticmethod
    def create_text_with_truncation(
        text: str,
        max_lines: int = 1,
        size: Optional[int] = None,
        weight: Optional[ft.FontWeight] = None,
        **kwargs
    ) -> ft.Text:
        """
        Create text with proper truncation for responsive layouts.
        
        Args:
            text: Text content to display
            max_lines: Maximum number of lines before truncation
            size: Optional font size
            weight: Optional font weight
            **kwargs: Additional Text properties
            
        Returns:
            Configured Text with truncation
        """
        text_kwargs = {
            "value": text,
            "max_lines": max_lines,
            "overflow": ft.TextOverflow.ELLIPSIS
        }

        if size:
            text_kwargs["size"] = size
        if weight:
            text_kwargs["weight"] = weight

        text_kwargs.update(kwargs)

        return ft.Text(**text_kwargs)
    
    @staticmethod
    def create_mobile_friendly_card(
        content: ft.Control, 
        width: float,
        elevation: Optional[int] = None
    ) -> ft.Card:
        """
        Create card optimized for mobile display.
        
        Args:
            content: Content for the card
            width: Current screen width
            elevation: Optional custom elevation
            
        Returns:
            Mobile-optimized Card
        """
        # Determine if mobile
        is_mobile = BreakpointManager.is_mobile(width)
        
        # Create responsive container
        container = ResponsiveBuilder.create_adaptive_container(
            content=content,
            responsive_padding=True,
            responsive_margin=True
        )
        
        # Set elevation based on screen size
        if elevation is None:
            elevation = 2 if is_mobile else 4
        
        return ft.Card(
            content=container,
            elevation=elevation,
            expand=True
        )
    
    @staticmethod
    def create_adaptive_grid_with_columns(
        items: List[ft.Control], 
        width: float,
        min_item_width: int = 200,
        **kwargs
    ) -> ft.Control:
        """
        Create adaptive grid that calculates columns based on screen size.
        
        Args:
            items: List of items to display in grid
            width: Current screen width
            min_item_width: Minimum width for grid items
            **kwargs: Additional GridView properties
            
        Returns:
            Adaptive grid component
        """
        # Calculate columns based on available width and minimum item width
        cols = max(1, int(width // min_item_width))
        
        # Get responsive spacing
        spacing = BreakpointManager.get_responsive_spacing(width, "medium")
        
        # Create grid with calculated columns
        return ft.GridView(
            controls=items,
            runs_count=cols,
            max_extent=min_item_width,
            child_aspect_ratio=1.0,
            spacing=spacing,
            run_spacing=spacing,
            **kwargs
        )
    
    @staticmethod
    def get_responsive_spacing_for_screen_size(
        width: float, 
        spacing_type: str = "medium"
    ) -> int:
        """
        Get responsive spacing value based on screen width.
        
        Args:
            width: Current screen width
            spacing_type: Type of spacing ("small", "medium", "large", "xlarge")
            
        Returns:
            Spacing value in pixels
        """
        return BreakpointManager.get_responsive_spacing(width, spacing_type)

# ============================================================================
# RESPONSIVE LAYOUT FACTORY (Absorbed from responsive_layout_utils.py)
# ============================================================================

class ResponsiveLayoutFactory:
    """
    Factory class for creating responsive layout components.
    
    Provides centralized factory methods for responsive UI creation with
    built-in Material Design 3 support and screen size adaptation.
    
    Absorbed from responsive_layout_utils.py in Phase 2.2 Layout Deduplication.
    """
    
    @staticmethod
    def create_responsive_card_grid(
        items: List[ft.Control],
        width: float,
        card_min_width: int = 280
    ) -> ft.Control:
        """
        Create a grid of responsive cards.
        
        Args:
            items: Content items for cards
            width: Current screen width
            card_min_width: Minimum card width
            
        Returns:
            Grid of responsive cards
        """
        # Wrap items in mobile-friendly cards
        cards = [
            ResponsiveBuilder.create_mobile_friendly_card(item, width) 
            for item in items
        ]
        
        # Create adaptive grid
        return ResponsiveBuilder.create_adaptive_grid_with_columns(
            cards, width, card_min_width
        )
    
    @staticmethod
    def create_responsive_form(
        fields: List[ft.Control],
        width: float,
        single_column_threshold: int = 768  # MD breakpoint
    ) -> ft.Control:
        """
        Create responsive form layout.
        
        Args:
            fields: Form field controls
            width: Current screen width
            single_column_threshold: Width below which to use single column
            
        Returns:
            Responsive form layout
        """
        spacing = BreakpointManager.get_responsive_spacing(width, "medium")
        
        if width <= single_column_threshold:
            # Single column for mobile/tablet
            return ft.Column(
                controls=fields,
                spacing=spacing,
                expand=True
            )
        else:
            # Two column for desktop
            half = len(fields) // 2
            left_column = fields[:half]
            right_column = fields[half:]
            
            return ft.Row([
                ft.Column(controls=left_column, expand=True),
                ft.Column(controls=right_column, expand=True)
            ], spacing=spacing)
    
    @staticmethod
    def create_responsive_header(
        title: str,
        width: float,
        actions: Optional[List[ft.Control]] = None
    ) -> ft.Control:
        """
        Create responsive header with title and actions.
        
        Args:
            title: Header title text
            actions: Optional action controls
            width: Current screen width
            
        Returns:
            Responsive header component
        """
        is_mobile = BreakpointManager.is_mobile(width)
        title_size = 20 if is_mobile else 24
        
        title_text = ResponsiveBuilder.create_text_with_truncation(
            text=title,
            size=title_size,
            weight=ft.FontWeight.BOLD
        )
        
        if not actions:
            return title_text
        
        if is_mobile:
            # Stack vertically on mobile
            return ft.Column([
                title_text,
                ft.Row(actions, spacing=8)
            ], spacing=8)
        else:
            # Side by side on larger screens
            return ft.Row([
                title_text,
                ft.Row(actions, spacing=12)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

# ============================================================================
# MD3 DESKTOP BREAKPOINTS SYSTEM (from breakpoint_manager.py)
# ============================================================================

class MD3DesktopBreakpoints:
    """
    Material Design 3 desktop breakpoint system for desktop-focused layouts.
    Provides specialized breakpoint logic optimized for desktop window management.
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

# ============================================================================
# RESPONSIVE LAYOUT MANAGER
# ============================================================================

class ResponsiveLayoutManager:
    """Advanced responsive layout management with viewport detection and automatic adaptation."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_width = 1200  # Default width
        self.current_breakpoint = Breakpoint.LG
        self.layout_callbacks: List[Callable[[float, Breakpoint], None]] = []
        
        # Viewport detection
        self.page.on_window_event = self._on_window_event
    
    def _on_window_event(self, e: ft.WindowEvent):
        """Handle window resize events."""
        if e.event_type == "resize":
            self.update_viewport(e.width)
    
    def update_viewport(self, width: float):
        """Update viewport size and trigger layout adaptations."""
        old_breakpoint = self.current_breakpoint
        self.current_width = width
        self.current_breakpoint = BreakpointManager.get_current_breakpoint(width)
        
        # Trigger callbacks if breakpoint changed
        if old_breakpoint != self.current_breakpoint:
            for callback in self.layout_callbacks:
                try:
                    callback(width, self.current_breakpoint)
                except Exception as e:
                    print(f"[ERROR] Layout callback failed: {e}")
    
    def add_layout_callback(self, callback: Callable[[float, Breakpoint], None]):
        """Add callback to be notified of layout changes."""
        if callback not in self.layout_callbacks:
            self.layout_callbacks.append(callback)
    
    def remove_layout_callback(self, callback: Callable[[float, Breakpoint], None]):
        """Remove layout callback."""
        if callback in self.layout_callbacks:
            self.layout_callbacks.remove(callback)
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current responsive configuration."""
        return BreakpointManager.get_grid_breakpoint_config(self.current_width)
    
    def create_adaptive_layout(self, 
                              mobile_layout: ft.Control,
                              tablet_layout: ft.Control,
                              desktop_layout: ft.Control) -> ft.Control:
        """Create a layout that adapts based on current viewport."""
        config = self.get_current_config()
        
        if config["is_mobile"]:
            return mobile_layout
        elif config["is_tablet"]:
            return tablet_layout
        else:
            return desktop_layout

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_responsive_layout_manager(page: ft.Page) -> ResponsiveLayoutManager:
    """Create and initialize a responsive layout manager."""
    return ResponsiveLayoutManager(page)

def get_viewport_info(page: ft.Page) -> Dict[str, Any]:
    """Get viewport information from the page."""
    try:
        width = page.window_width or 1200
        height = page.window_height or 800
        
        return {
            "width": width,
            "height": height,
            "breakpoint": BreakpointManager.get_current_breakpoint(width),
            "config": BreakpointManager.get_grid_breakpoint_config(width)
        }
    except Exception:
        # Fallback values
        return {
            "width": 1200,
            "height": 800,
            "breakpoint": Breakpoint.LG,
            "config": BreakpointManager.get_grid_breakpoint_config(1200)
        }

def create_responsive_container_with_breakpoints(
    content: ft.Control,
    breakpoint_configs: Dict[Breakpoint, Dict[str, Any]]
) -> ft.Control:
    """Create a container that changes properties based on breakpoints."""
    
    def get_container_for_width(width: float) -> ft.Container:
        breakpoint = BreakpointManager.get_current_breakpoint(width)
        config = breakpoint_configs.get(breakpoint, {})
        
        return ft.Container(
            content=content,
            **config
        )
    
    # For now, return with default config - would need viewport detection for full functionality
    default_breakpoint = Breakpoint.LG
    default_config = breakpoint_configs.get(default_breakpoint, {})
    
    return ft.Container(
        content=content,
        **default_config
    )

# ============================================================================
# LAYOUT FIX UTILITIES (Absorbed from responsive_fixes.py)
# ============================================================================

def apply_layout_fixes(page: ft.Page) -> None:
    """
    Apply general layout fixes to the entire page.
    
    Args:
        page: The Flet page to apply fixes to
    """
    # Ensure page has proper constraints
    if not page.window_min_width:
        page.window_min_width = 800
    if not page.window_min_height:
        page.window_min_height = 600
        
    # Apply clipping behavior to root container if it exists
    if hasattr(page, 'controls') and page.controls:
        for control in page.controls:
            if isinstance(control, ft.Container):
                control.clip_behavior = ft.ClipBehavior.NONE


# Helper functions for common fixes
def fix_content_clipping(content: ft.Control) -> ft.Container:
    """Quick fix for content clipping issues."""
    return ResponsiveLayoutFixes.create_clipping_safe_container(content)


def fix_button_clickable_areas(button: ft.Control) -> ft.Container:
    """Quick fix for button clickable area issues."""
    return ResponsiveLayoutFixes.fix_button_hitbox(button)


def ensure_windowed_compatibility(content: ft.Control) -> ft.Container:
    """Ensure content works well in windowed mode (800x600)."""
    return ResponsiveLayoutFixes.create_windowed_layout_fix(content)

# ============================================================================
# RESPONSIVE PATTERNS
# ============================================================================

class ResponsivePatterns:
    """Collection of common responsive design patterns."""
    
    @staticmethod
    def create_sidebar_layout(
        main_content: ft.Control,
        sidebar_content: ft.Control,
        width: float,
        sidebar_width: int = 250
    ) -> ft.Control:
        """Create a responsive sidebar layout."""
        if BreakpointManager.is_mobile(width):
            # Stack vertically on mobile
            return ft.Column([
                sidebar_content,
                ft.Divider(),
                main_content
            ], expand=True)
        else:
            # Side-by-side on larger screens
            return ft.Row([
                ft.Container(content=sidebar_content, width=sidebar_width),
                ft.VerticalDivider(width=1),
                ft.Container(content=main_content, expand=True)
            ], expand=True)
    
    @staticmethod
    def create_hero_section(
        title: str,
        subtitle: str,
        actions: List[ft.Control],
        width: float
    ) -> ft.Control:
        """Create a responsive hero section."""
        title_size = ResponsiveBuilder.get_responsive_font_size(width, 32)
        subtitle_size = ResponsiveBuilder.get_responsive_font_size(width, 16)
        
        if BreakpointManager.is_mobile(width):
            # Centered layout for mobile
            return ft.Column([
                ft.Text(title, size=title_size, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(subtitle, size=subtitle_size, text_align=ft.TextAlign.CENTER),
                ft.Column(actions, spacing=10)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        else:
            # Left-aligned layout for desktop
            return ft.Column([
                ft.Text(title, size=title_size, weight=ft.FontWeight.BOLD),
                ft.Text(subtitle, size=subtitle_size),
                ft.Row(actions, spacing=15)
            ], spacing=20)
    
    @staticmethod
    def create_card_grid(
        cards: List[ft.Control],
        width: float
    ) -> ft.Control:
        """Create a responsive card grid."""
        if BreakpointManager.is_mobile(width):
            # Single column on mobile
            return ft.Column(cards, spacing=15)
        elif BreakpointManager.is_tablet(width):
            # Two columns on tablet
            rows = []
            for i in range(0, len(cards), 2):
                row_cards = cards[i:i+2]
                if len(row_cards) == 2:
                    rows.append(ft.Row(row_cards, spacing=15, expand=True))
                else:
                    rows.append(ft.Row([row_cards[0]], spacing=15, expand=True))
            return ft.Column(rows, spacing=15)
        else:
            # Three or more columns on desktop
            return ResponsiveBuilder.create_responsive_grid(
                cards, width, child_aspect_ratio=0.8
            )

# ============================================================================
# RESPONSIVE LAYOUT FIXES (Absorbed from responsive_fixes.py)
# ============================================================================

class ResponsiveLayoutFixes:
    """Collection of utilities to fix common responsive layout issues."""
    
    @staticmethod
    def create_clipping_safe_container(
        content: ft.Control,
        min_width: Optional[float] = None,
        min_height: Optional[float] = None,
        padding: Union[int, ft.Padding] = 16,
        margin: Union[int, ft.Margin] = 8,
        **kwargs
    ) -> ft.Container:
        """
        Create a container that prevents content clipping.
        
        Args:
            content: The content to wrap
            min_width: Minimum width constraint
            min_height: Minimum height constraint
            padding: Padding around content
            margin: Margin around container
            **kwargs: Additional Container properties
        """
        container_kwargs = {
            "content": content,
            "padding": padding,
            "margin": margin,
            "clip_behavior": ft.ClipBehavior.NONE,  # Prevent clipping
            "expand": True,
        }

        # Add optional constraints
        if min_width:
            container_kwargs["min_width"] = min_width
        if min_height:
            container_kwargs["min_height"] = min_height

        # Add any additional kwargs
        container_kwargs |= kwargs

        return ft.Container(**container_kwargs)
    
    @staticmethod
    def fix_hitbox_alignment(
        content: ft.Control,
        width: Optional[float] = None,
        height: Optional[float] = None,
        alignment: ft.Alignment = ft.alignment.center,
        **kwargs
    ) -> ft.Container:
        """
        Fix hitbox alignment issues by ensuring proper sizing and alignment.
        
        Args:
            content: The content to fix
            width: Fixed width (None for responsive)
            height: Fixed height (None for responsive)
            alignment: Alignment within container
            **kwargs: Additional Container properties
        """
        container_kwargs = {
            "content": content,
            "alignment": alignment,
            "clip_behavior": ft.ClipBehavior.NONE,
        }

        # Add sizing if specified
        if width:
            container_kwargs["width"] = width
        if height:
            container_kwargs["height"] = height

        # Add any additional kwargs
        container_kwargs |= kwargs

        return ft.Container(**container_kwargs)
    
    @staticmethod
    def create_responsive_scroll_container(
        content: ft.Control,
        max_height: Optional[float] = None,
        padding: Union[int, ft.Padding] = 16,
        **kwargs
    ) -> ft.Container:
        """
        Create a scrollable container that works well in responsive layouts.
        
        Args:
            content: The content to make scrollable
            max_height: Maximum height before scrolling
            padding: Padding around content
            **kwargs: Additional Container properties
        """
        # Wrap content in a scrollable column
        scrollable_content = ft.Column(
            controls=content.controls if isinstance(content, (ft.Column, ft.Row)) else [content],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        container_kwargs = {
            "content": scrollable_content,
            "padding": padding,
            "expand": True,
            "clip_behavior": ft.ClipBehavior.NONE,
        }

        # Add max height if specified
        if max_height:
            container_kwargs["max_height"] = max_height

        # Add any additional kwargs
        container_kwargs |= kwargs

        return ft.Container(**container_kwargs)
    
    @staticmethod
    def fix_button_hitbox(
        button: ft.Control,
        min_width: float = 48,
        min_height: float = 48,
        padding: Union[int, ft.Padding] = 8,
        **kwargs
    ) -> ft.Container:
        """
        Fix button hitbox issues by ensuring minimum touch target size.
        
        Args:
            button: The button to fix
            min_width: Minimum touch target width (48px recommended)
            min_height: Minimum touch target height (48px recommended)
            padding: Padding around button
            **kwargs: Additional Container properties
        """
        return ft.Container(
            content=button,
            width=min_width,
            height=min_height,
            padding=padding,
            alignment=ft.alignment.center,
            clip_behavior=ft.ClipBehavior.NONE,
            **kwargs
        )
    
    @staticmethod
    def create_windowed_layout_fix(
        content: ft.Control,
        window_width: int = 800,
        window_height: int = 600,
        padding: Union[int, ft.Padding] = 16,
        **kwargs
    ) -> ft.Container:
        """
        Create layout that works well in windowed mode (800x600 minimum).
        
        Args:
            content: The content to fix for windowed mode
            window_width: Target window width (800px minimum)
            window_height: Target window height (600px minimum)
            padding: Padding around content
            **kwargs: Additional Container properties
        """
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=content,
                    expand=True,
                )
            ], expand=True),
            padding=padding,
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            **kwargs
        )
    
    @staticmethod
    def ensure_minimum_touch_target(
        component: ft.Control, 
        spec: TouchTargetSpec = None,
        interaction_methods: Set[InteractionMethod] = None
    ) -> ft.Container:
        """
        Ensure component meets minimum touch target requirements with flexible configuration.
        
        Args:
            component: Component to wrap with proper touch target
            spec: Touch target specifications (uses default if None)
            interaction_methods: Supported interaction methods (auto-detects if None)
            
        Returns:
            Container with guaranteed minimum touch target size
        """
        if spec is None:
            spec = TouchTargetSpec()
            
        if interaction_methods is None:
            interaction_methods = {InteractionMethod.MOUSE, InteractionMethod.TOUCH}
        
        # Calculate required dimensions based on interaction methods
        min_width = spec.min_width
        min_height = spec.min_height
        
        # Add accessibility margin if accessibility support is needed
        if InteractionMethod.ACCESSIBILITY in interaction_methods:
            min_width += spec.accessibility_margin * 2
            min_height += spec.accessibility_margin * 2
        
        return ft.Container(
            content=component,
            min_width=min_width,
            min_height=min_height,
            alignment=ft.alignment.center,
            clip_behavior=ft.ClipBehavior.NONE,
        )
    
    @staticmethod
    def create_accessible_button(
        text: str, 
        on_click: Callable,
        spec: TouchTargetSpec = None,
        interaction_methods: Set[InteractionMethod] = None,
        **button_kwargs
    ) -> ft.ElevatedButton:
        """
        Create button with accessibility-compliant touch target sizing.
        
        Args:
            text: Button text
            on_click: Click handler function
            spec: Touch target specifications (uses default if None) 
            interaction_methods: Supported interaction methods
            **button_kwargs: Additional button properties
            
        Returns:
            ElevatedButton with proper accessibility sizing
        """
        if spec is None:
            spec = TouchTargetSpec()
            
        if interaction_methods is None:
            interaction_methods = {InteractionMethod.MOUSE, InteractionMethod.TOUCH, InteractionMethod.ACCESSIBILITY}
        
        # Calculate minimum width based on text length and specifications
        estimated_text_width = len(text) * 8 + 32  # Rough estimate
        min_width = max(estimated_text_width, spec.min_width)
        
        # Add accessibility margin if needed
        if InteractionMethod.ACCESSIBILITY in interaction_methods:
            min_width += spec.accessibility_margin * 2
        
        return ft.ElevatedButton(
            text=text,
            on_click=on_click,
            height=max(spec.min_height, 44),  # Ensure minimum height
            width=min_width,
            **button_kwargs
        )