"""
Responsive utility functions for building adaptive Flet UI components.

This module provides the ResponsiveBuilder class with static methods for creating
responsive layouts, containers, and UI elements that adapt to different screen sizes.
"""

import flet as ft
from typing import List, Dict, Any, Optional, Union, Callable
from .breakpoint_manager import BreakpointManager, Breakpoint


class ResponsiveBuilder:
    """
    Static utility class for building responsive UI components.
    
    Provides methods to create adaptive layouts, containers, and UI elements
    that automatically adjust to different screen sizes and breakpoints.
    """
    
    @staticmethod
    def create_responsive_row(
        controls: List[ft.Control],
        column_configs: Optional[Dict[str, int]] = None,
        spacing: Optional[int] = None,
        alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.START,
        vertical_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER,
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
            **kwargs: Additional ResponsiveRow properties
            
        Returns:
            Configured ResponsiveRow with responsive controls
        """
        responsive_controls = []
        
        for i, control in enumerate(controls):
            # Set column configuration if provided
            if column_configs and len(column_configs) > i:
                config_key = list(column_configs.keys())[i]
                col_config = column_configs[config_key]
                
                # Apply column configuration to control
                if hasattr(control, 'col'):
                    if isinstance(col_config, dict):
                        control.col = col_config
                    else:
                        control.col = {"xs": 12, "sm": 6, "md": 4, "lg": col_config}
                        
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
        **kwargs
    ) -> ft.Card:
        """
        Create a responsive card that adapts to screen size.
        
        Args:
            content: Content to display in the card
            width: Optional fixed width (None for responsive)
            elevation: Optional fixed elevation
            responsive_elevation: Whether to scale elevation responsively
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
            
        style_dict = base_style.__dict__.copy()
        
        if scale_size and 'size' in style_dict and style_dict['size']:
            original_size = style_dict['size']
            scale_factor = BreakpointManager.get_responsive_font_scale(width)
            style_dict['size'] = int(original_size * scale_factor)
            
        return ft.TextStyle(**style_dict)
    
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