"""
Phase 3 UI Stability & Navigation: Responsive Layout Manager (CONSOLIDATED)

Purpose: Manage responsive design patterns and prevent layout issues
Status: COMPLETED IMPLEMENTATION - All Phase 3 requirements fulfilled

This module provides:
1. Dynamic breakpoint management for different screen sizes
2. Responsive component sizing and layout adaptation
3. Container overflow prevention and content fitting
4. Adaptive navigation patterns (drawer, rail, bottom nav)

CONSOLIDATION STATUS:
- Material Design 3 breakpoints integrated from core/responsive_layout.py
- Standard MD3 breakpoint definitions added alongside custom breakpoints
- DeviceType and BreakpointSize enums consolidated
- Breakpoint dataclass with width matching logic integrated

IMPLEMENTATION NOTES:
- Complete responsive layout management with breakpoint detection
- Integrate with existing ResponsiveRow patterns from Flet
- Implement proper container sizing to prevent clipping/cramming
- Add adaptive navigation patterns for mobile/tablet/desktop
- Ensure consistent responsive behavior across all views
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import flet as ft


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


class LayoutMode(Enum):
    """Layout modes for different screen configurations"""
    COMPACT = "compact"      # Single column, minimal spacing
    MEDIUM = "medium"        # Two columns, standard spacing
    EXPANDED = "expanded"    # Three+ columns, generous spacing
    ADAPTIVE = "adaptive"    # Automatically choose based on content


class NavigationPattern(Enum):
    """Navigation patterns for different screen sizes"""
    BOTTOM_NAV = "bottom_nav"     # Mobile bottom navigation
    RAIL = "rail"                 # Desktop navigation rail
    DRAWER = "drawer"             # Tablet/mobile drawer
    TOP_TABS = "top_tabs"         # Tablet top tabs
    BREADCRUMB = "breadcrumb"     # Desktop breadcrumb only


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


class EnhancedResponsiveLayout:
    """Enhanced responsive layout utilities with full MD3 desktop support (consolidated from ui/layouts/md3_desktop_breakpoints.py)"""
    
    @staticmethod
    def create_adaptive_responsive_row(
        controls: list,
        spacing: int = 16,
        run_spacing: int = 16,
        expand: bool = False
    ) -> ft.ResponsiveRow:
        """Create a responsive row with adaptive desktop breakpoints"""
        return ft.ResponsiveRow(
            controls=controls,
            spacing=spacing,
            run_spacing=run_spacing,
            expand=expand
        )
    
    @staticmethod
    def create_adaptive_column(
        controls: list,
        span_config: Optional[Dict[str, int]] = None,
        **kwargs
    ) -> ft.Column:
        """Create a column with adaptive desktop breakpoint configuration"""
        if span_config is None:
            span_config = MD3DesktopBreakpoints.create_responsive_column_config()
        
        # Create responsive column wrapper
        responsive_wrapper = ft.ResponsiveRow([
            ft.Column(
                controls=controls,
                col=span_config,
                **kwargs
            )
        ])
        
        return ft.Column([responsive_wrapper], expand=True)
    
    @staticmethod
    def create_text_with_truncation(
        text: str,
        max_lines: int = 1,
        size: Optional[int] = None,
        weight: Optional[ft.FontWeight] = None,
        **kwargs
    ) -> ft.Text:
        """Create text with proper truncation for responsive layouts"""
        text_kwargs = {
            "value": text,
            "max_lines": max_lines,
            "overflow": ft.TextOverflow.ELLIPSIS
        }

        if size:
            text_kwargs["size"] = size
        if weight:
            text_kwargs["weight"] = weight

        text_kwargs |= kwargs

        return ft.Text(**text_kwargs)
    
    @staticmethod
    def create_responsive_container(
        content: ft.Control,
        padding: Union[int, ft.Padding] = 16,
        margin: Union[int, ft.Margin] = 8,
        expand: bool = True,
        **kwargs
    ) -> ft.Container:
        """Create a responsive container with proper clipping handling"""
        container_kwargs = {
            "content": content,
            "padding": padding,
            "margin": margin,
            "expand": expand,
            "clip_behavior": ft.ClipBehavior.NONE,
        } | kwargs
        return ft.Container(**container_kwargs)


@dataclass
class LayoutConstraints:
    """Layout constraints for responsive components"""
    min_width: Optional[int] = None
    max_width: Optional[int] = None
    min_height: Optional[int] = None
    max_height: Optional[int] = None
    aspect_ratio: Optional[float] = None
    expand: bool = True
    flexible: bool = True


@dataclass
class ResponsiveConfig:
    """Configuration for responsive component behavior"""
    mobile: Dict[str, Any] = field(default_factory=dict)
    tablet: Dict[str, Any] = field(default_factory=dict)  
    desktop: Dict[str, Any] = field(default_factory=dict)
    wide: Dict[str, Any] = field(default_factory=dict)


class ResponsiveLayoutManager:
    """
    Manages responsive layout behavior across the application
    
    COMPLETED STATUS: All Phase 3 requirements implemented:
    - Dynamic breakpoint detection and handling
    - Responsive component adaptation system
    - Container overflow prevention
    - Adaptive navigation pattern switching
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.logger = logging.getLogger(__name__)
        
        # Current layout state
        self.current_screen_size = ScreenSize.DESKTOP
        self.current_layout_mode = LayoutMode.EXPANDED
        self.current_navigation_pattern = NavigationPattern.RAIL
        
        # Configuration
        self.breakpoint_config = BreakpointConfig()
        self.responsive_components: Dict[str, Any] = {}
        self.layout_constraints: Dict[str, LayoutConstraints] = {}
        
        # Event callbacks for layout changes
        self.layout_callbacks: Dict[str, List[Callable]] = {
            "screen_size_changed": [],
            "layout_mode_changed": [],
            "navigation_pattern_changed": [],
            "component_resized": []
        }
        
        # Initialize responsive layout components
        self.page_width = 0
        self.page_height = 0
        self.content_area_width = 0
        self.content_area_height = 0
        
        # Set up page resize monitoring
        self._setup_resize_monitoring()
    
    def update_page_size(self, width: int, height: int) -> None:
        """
        Update page dimensions and recalculate responsive layout
        
        Args:
            width: New page width in pixels
            height: New page height in pixels
        """
        old_screen_size = self.current_screen_size
        old_layout_mode = self.current_layout_mode
        
        self.page_width = width
        self.page_height = height
        
        # Calculate new screen size category
        new_screen_size = self._calculate_screen_size(width)
        if new_screen_size != self.current_screen_size:
            self.current_screen_size = new_screen_size
            asyncio.create_task(self._fire_layout_event("screen_size_changed", {
                "old_size": old_screen_size,
                "new_size": new_screen_size,
                "width": width,
                "height": height
            }))
        
        # Calculate new layout mode
        new_layout_mode = self._calculate_layout_mode(width, height)
        if new_layout_mode != self.current_layout_mode:
            self.current_layout_mode = new_layout_mode
            asyncio.create_task(self._fire_layout_event("layout_mode_changed", {
                "old_mode": old_layout_mode,
                "new_mode": new_layout_mode
            }))
        
        # Update navigation pattern if needed
        new_nav_pattern = self._calculate_navigation_pattern(new_screen_size)
        if new_nav_pattern != self.current_navigation_pattern:
            self.current_navigation_pattern = new_nav_pattern
            asyncio.create_task(self._fire_layout_event("navigation_pattern_changed", {
                "new_pattern": new_nav_pattern
            }))
        
        # Update all responsive components
        asyncio.create_task(self._update_all_responsive_components())
    
    def register_responsive_component(self, 
                                    component_id: str,
                                    component: ft.Control,
                                    config: ResponsiveConfig) -> None:
        """
        Register component for responsive layout management
        
        Args:
            component_id: Unique identifier for the component
            component: Flet control component
            config: Configuration for responsive behavior
        """
        self.responsive_components[component_id] = {
            "component": component,
            "config": config,
            "last_updated": datetime.now()
        }
        
        # Apply current responsive settings immediately
        asyncio.create_task(self._update_component_layout(component_id))
    
    def create_responsive_container(self,
                                  content: ft.Control,
                                  constraints: LayoutConstraints = None,
                                  config: ResponsiveConfig = None) -> ft.Container:
        """
        Create container with responsive behavior
        
        Args:
            content: Content to wrap in responsive container
            constraints: Layout constraints
            config: Responsive configuration
            
        Returns:
            ft.Container: Responsive container component
        """
        if constraints is None:
            constraints = LayoutConstraints()
        
        if config is None:
            config = ResponsiveConfig()
        
        # Calculate responsive properties
        responsive_props = self._calculate_responsive_properties(config)
        
        container = ft.Container(
            content=content,
            expand=constraints.expand,
            # Apply calculated responsive properties
            **responsive_props
        )
        
        # Register container for responsive updates
        component_id = f"responsive_container_{id(container)}"
        self.register_responsive_component(component_id, container, config)
        
        return container
    
    def create_responsive_row(self,
                            controls: List[ft.Control],
                            responsive_columns: Dict[str, Dict[str, int]] = None) -> ft.ResponsiveRow:
        """
        Create responsive row with adaptive column sizing
        
        Args:
            controls: List of controls to arrange in row
            responsive_columns: Column configuration for different screen sizes
            
        Returns:
            ft.ResponsiveRow: Responsive row component
        """
        if responsive_columns is None:
            # Default responsive column configuration
            responsive_columns = self._get_default_column_config(len(controls))
        
        # Create responsive columns for controls
        responsive_controls = []
        for i, control in enumerate(controls):
            col_config = responsive_columns.get(str(i), {"sm": 12, "md": 6, "lg": 4})
            
            responsive_control = ft.Column(
                col=col_config,
                controls=[control],
                expand=True
            )
            responsive_controls.append(responsive_control)
        
        return ft.ResponsiveRow(
            controls=responsive_controls,
            run_spacing=self._get_responsive_spacing("run"),
            spacing=self._get_responsive_spacing("main")
        )
    
    def adapt_navigation_for_screen_size(self) -> NavigationPattern:
        """
        Get appropriate navigation pattern for current screen size
        
        Returns:
            NavigationPattern: Recommended navigation pattern
        """
        return self.current_navigation_pattern
    
    def get_content_area_constraints(self) -> Tuple[int, int]:
        """
        Get available content area dimensions
        
        Returns:
            Tuple[int, int]: Available width and height
        """
        # Calculate content area based on navigation pattern
        nav_overhead = self._calculate_navigation_overhead()
        
        content_width = max(0, self.page_width - nav_overhead["width"])
        content_height = max(0, self.page_height - nav_overhead["height"])
        
        return content_width, content_height
    
    def prevent_container_overflow(self, container: ft.Container) -> None:
        """
        Apply overflow prevention to container
        
        Args:
            container: Container to prevent overflow for
        """
        content_width, content_height = self.get_content_area_constraints()
        
        # Apply constraints to prevent overflow
        if hasattr(container, 'width') and container.width and container.width > content_width:
            container.width = content_width
            container.scroll = ft.ScrollMode.AUTO
        
        if hasattr(container, 'height') and container.height and container.height > content_height:
            container.height = content_height
            container.scroll = ft.ScrollMode.AUTO
    
    def register_layout_callback(self, event_type: str, callback: Callable) -> None:
        """Register callback for layout change events"""
        if event_type in self.layout_callbacks:
            self.layout_callbacks[event_type].append(callback)
    
    def unregister_layout_callback(self, event_type: str, callback: Callable) -> bool:
        """Unregister layout change callback"""
        if event_type in self.layout_callbacks and callback in self.layout_callbacks[event_type]:
            self.layout_callbacks[event_type].remove(callback)
            return True
        return False
    
    # Private implementation methods
    def _setup_resize_monitoring(self) -> None:
        """Set up page resize monitoring"""
        # Set up page resize event listener
        self.page.on_resize = self._on_page_resize
    
    def _on_page_resize(self, e) -> None:
        """Handle page resize events"""
        if hasattr(e, 'width') and hasattr(e, 'height'):
            self.update_page_size(int(e.width), int(e.height))
    
    def _calculate_screen_size(self, width: int) -> ScreenSize:
        """Calculate screen size category from width"""
        if width <= self.breakpoint_config.mobile_max:
            return ScreenSize.MOBILE
        elif width <= self.breakpoint_config.tablet_max:
            return ScreenSize.TABLET
        elif width <= self.breakpoint_config.desktop_max:
            return ScreenSize.DESKTOP
        else:
            return ScreenSize.WIDE_DESKTOP
    
    def _calculate_layout_mode(self, width: int, height: int) -> LayoutMode:
        """
        Calculate optimal layout mode for given dimensions
        
        Args:
            width: Page width
            height: Page height
            
        Returns:
            LayoutMode: Optimal layout mode
        """
        screen_size = self._calculate_screen_size(width)
        
        if screen_size == ScreenSize.MOBILE:
            return LayoutMode.COMPACT
        elif screen_size == ScreenSize.TABLET:
            return LayoutMode.MEDIUM
        else:
            return LayoutMode.EXPANDED
    
    def _calculate_navigation_pattern(self, screen_size: ScreenSize) -> NavigationPattern:
        """Calculate optimal navigation pattern for screen size"""
        if screen_size == ScreenSize.MOBILE:
            return NavigationPattern.BOTTOM_NAV
        elif screen_size == ScreenSize.TABLET:
            return NavigationPattern.DRAWER
        else:
            return NavigationPattern.RAIL
    
    def _calculate_responsive_properties(self, config: ResponsiveConfig) -> Dict[str, Any]:
        """
        Calculate responsive properties for current screen size
        
        Args:
            config: Responsive configuration
            
        Returns:
            Dict[str, Any]: Calculated responsive properties
        """
        screen_config = {}
        
        if self.current_screen_size == ScreenSize.MOBILE:
            screen_config = config.mobile
        elif self.current_screen_size == ScreenSize.TABLET:
            screen_config = config.tablet
        elif self.current_screen_size == ScreenSize.DESKTOP:
            screen_config = config.desktop
        else:
            screen_config = config.wide
        
        # Apply default values for missing properties
        default_config = self._get_default_responsive_config()
        return {**default_config, **screen_config}
    
    def _get_default_column_config(self, num_controls: int) -> Dict[str, Dict[str, int]]:
        """
        Get default responsive column configuration
        
        Args:
            num_controls: Number of controls in row
            
        Returns:
            Dict: Column configuration
        """
        configs = {}
        for i in range(num_controls):
            if num_controls <= 2:
                configs[str(i)] = {"sm": 12, "md": 6, "lg": 6}
            elif num_controls <= 3:
                configs[str(i)] = {"sm": 12, "md": 6, "lg": 4}
            else:
                configs[str(i)] = {"sm": 12, "md": 6, "lg": 3}
        
        return configs
    
    def _get_responsive_spacing(self, spacing_type: str) -> int:
        """Get responsive spacing value based on screen size"""
        spacing_map = {
            ScreenSize.MOBILE: {"main": 8, "run": 8},
            ScreenSize.TABLET: {"main": 12, "run": 12},
            ScreenSize.DESKTOP: {"main": 16, "run": 16},
            ScreenSize.WIDE_DESKTOP: {"main": 20, "run": 20}
        }
        
        return spacing_map[self.current_screen_size].get(spacing_type, 12)
    
    def _calculate_navigation_overhead(self) -> Dict[str, int]:
        """
        Calculate space consumed by navigation elements
        
        Returns:
            Dict with width and height overhead
        """
        overhead = {"width": 0, "height": 0}
        
        if self.current_navigation_pattern == NavigationPattern.RAIL:
            overhead["width"] = 80  # Navigation rail width
        elif self.current_navigation_pattern == NavigationPattern.BOTTOM_NAV:
            overhead["height"] = 80  # Bottom navigation height
        # Drawer doesn't consume permanent space when closed
        
        return overhead
    
    def _get_default_responsive_config(self) -> Dict[str, Any]:
        """Get default responsive configuration properties"""
        return {
            "margin": self._get_responsive_spacing("main") // 2,
            "padding": self._get_responsive_spacing("main"),
            "border_radius": 8 if self.current_screen_size != ScreenSize.MOBILE else 4
        }
    
    async def _update_component_layout(self, component_id: str) -> None:
        """
        Update responsive layout for specific component
        
        Args:
            component_id: ID of component to update
        """
        try:
            component_info = self.responsive_components.get(component_id)
            if not component_info:
                return
            
            component = component_info["component"]
            config = component_info["config"]
            
            # Calculate and apply new responsive properties
            responsive_props = self._calculate_responsive_properties(config)
            
            # Update component properties
            for prop_name, prop_value in responsive_props.items():
                if hasattr(component, prop_name):
                    setattr(component, prop_name, prop_value)
            
            # Update component timestamp
            component_info["last_updated"] = datetime.now()
            
            # Trigger UI update
            self.page.update()
            
        except Exception as e:
            self.logger.error(f"Component layout update error: {e}")
    
    async def _update_all_responsive_components(self) -> None:
        """Update all registered responsive components"""
        for component_id in list(self.responsive_components.keys()):
            await self._update_component_layout(component_id)
    
    async def _fire_layout_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Fire layout change event to all registered callbacks
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        try:
            callbacks = self.layout_callbacks.get(event_type, [])
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_data)
                    else:
                        callback(event_data)
                except Exception as e:
                    self.logger.error(f"Layout callback error: {e}")
                    
        except Exception as e:
            self.logger.error(f"Layout event firing error: {e}")
    
    def get_layout_stats(self) -> Dict[str, Any]:
        """
        Get layout management statistics
        
        Returns:
            Dict with layout statistics
        """
        return {
            "screen_size": self.current_screen_size.value,
            "layout_mode": self.current_layout_mode.value,
            "navigation_pattern": self.current_navigation_pattern.value,
            "page_dimensions": {"width": self.page_width, "height": self.page_height},
            "content_area": self.get_content_area_constraints(),
            "responsive_components": len(self.responsive_components),
            "registered_callbacks": sum(len(callbacks) for callbacks in self.layout_callbacks.values())
        }


# Utility functions for common responsive patterns
def create_mobile_friendly_card(content: ft.Control, 
                               layout_manager: ResponsiveLayoutManager) -> ft.Card:
    """
    Create card optimized for mobile display
    
    Args:
        content: Content for the card
        layout_manager: Responsive layout manager
        
    Returns:
        ft.Card: Mobile-optimized card
    """
    constraints = LayoutConstraints(
        min_width=280,
        max_width=400 if layout_manager.current_screen_size != ScreenSize.MOBILE else None,
        expand=True
    )
    
    container = layout_manager.create_responsive_container(
        content=content,
        constraints=constraints
    )
    
    return ft.Card(
        content=container,
        elevation=2 if layout_manager.current_screen_size == ScreenSize.MOBILE else 4
    )


def create_adaptive_grid(items: List[ft.Control], 
                        layout_manager: ResponsiveLayoutManager,
                        min_item_width: int = 200) -> ft.Control:
    """
    Create adaptive grid that adjusts to screen size
    
    Args:
        items: List of items to display in grid
        layout_manager: Responsive layout manager
        min_item_width: Minimum width for grid items
        
    Returns:
        ft.Control: Adaptive grid component
    """
    content_width, _ = layout_manager.get_content_area_constraints()
    
    # Calculate columns based on available width and minimum item width
    cols = max(1, content_width // min_item_width)
    
    # Create grid with calculated columns
    return ft.GridView(
        controls=items,
        runs_count=cols,
        max_extent=min_item_width,
        child_aspect_ratio=1.0,
        spacing=layout_manager._get_responsive_spacing("main"),
        run_spacing=layout_manager._get_responsive_spacing("run")
    )


# Global responsive layout manager instance
_global_responsive_layout: Optional[ResponsiveLayoutManager] = None


def initialize_responsive_layout(page: ft.Page) -> ResponsiveLayoutManager:
    """
    Initialize global responsive layout manager
    
    Args:
        page: Flet page instance
        
    Returns:
        ResponsiveLayoutManager: Responsive layout manager instance
    """
    global _global_responsive_layout
    if _global_responsive_layout is None:
        _global_responsive_layout = ResponsiveLayoutManager(page)
    return _global_responsive_layout


def get_global_responsive_layout() -> Optional[ResponsiveLayoutManager]:
    """Get the global responsive layout manager instance"""
    return _global_responsive_layout