#!/usr/bin/env python3
"""
Purpose: Responsive design utilities and breakpoint management
Logic: Screen size detection, layout adaptation
UI: Responsive containers and layout helpers
"""

import flet as ft
from typing import List, Dict, Any, Optional, Union, Callable, Tuple
from enum import Enum

# ============================================================================
# BREAKPOINT SYSTEM (consolidated from breakpoint_manager.py)
# ============================================================================

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
    def get_columns_for_width(cls, width: float, layout_type: str = "default") -> int:
        """
        Get column count for a given width and layout type.
        
        Args:
            width: Screen width in pixels
            layout_type: Type of layout ("default", "half", "third", "quarter")
            
        Returns:
            Number of columns to use
        """
        breakpoint = cls.get_current_breakpoint(width)
        config = cls.get_column_config(breakpoint)
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
                    
                    # Apply column configuration to control
                    if hasattr(control, 'col'):
                        if isinstance(col_config, dict):
                            control.col = col_config
                        else:
                            # Create default responsive config
                            control.col = {"xs": 12, "sm": 6, "md": 4, "lg": col_config}
            else:
                # Apply default responsive behavior
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
        
        if symmetric:
            return ft.padding.all(padding_value)
        else:
            return padding_value
    
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
        
        if symmetric:
            return ft.margin.all(margin_value)
        else:
            return margin_value
    
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