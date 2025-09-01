#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ResponsiveLayoutUtils - Extracted from responsive_layout.py

Utility classes and functions for responsive layout creation.
Part of Phase 2 God Component decomposition: Final push extraction (5th manager).

SINGLE RESPONSIBILITY: Static utility methods for responsive UI component creation
- Enhanced responsive layout utilities with Material Design 3 support
- Utility functions for common responsive patterns
- Static factory methods for responsive components

STATUS: Phase 2 Final Push - Achieving 50%+ reduction
"""

import Shared.utils.utf8_solution  # UTF-8 solution

from typing import Dict, List, Optional, Union, Any
import flet as ft

# Import breakpoint components for MD3 support
from flet_server_gui.layout.breakpoint_manager import (
    MD3DesktopBreakpoints,
    ScreenSize
)


class EnhancedResponsiveLayout:
    """
    Enhanced responsive layout utilities with full MD3 desktop support
    Consolidated from ui/layouts/md3_desktop_breakpoints.py
    
    SINGLE RESPONSIBILITY: Static factory methods for responsive components
    """
    
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


# Utility functions for common responsive patterns
def create_mobile_friendly_card(content: ft.Control, 
                               screen_size: ScreenSize) -> ft.Card:
    """
    Create card optimized for mobile display
    
    Args:
        content: Content for the card
        screen_size: Current screen size
        
    Returns:
        ft.Card: Mobile-optimized card
    """
    from flet_server_gui.layout.responsive_component_registry import LayoutConstraints
    
    constraints = LayoutConstraints(
        min_width=280,
        max_width=400 if screen_size != ScreenSize.MOBILE else None,
        expand=True
    )
    
    container = EnhancedResponsiveLayout.create_responsive_container(
        content=content,
        padding=16 if screen_size != ScreenSize.MOBILE else 12,
        margin=8 if screen_size != ScreenSize.MOBILE else 4
    )
    
    return ft.Card(
        content=container,
        elevation=2 if screen_size == ScreenSize.MOBILE else 4
    )


def create_adaptive_grid(items: List[ft.Control], 
                        content_width: int,
                        min_item_width: int = 200,
                        screen_size: ScreenSize = ScreenSize.DESKTOP) -> ft.Control:
    """
    Create adaptive grid that adjusts to screen size
    
    Args:
        items: List of items to display in grid
        content_width: Available content width
        min_item_width: Minimum width for grid items
        screen_size: Current screen size
        
    Returns:
        ft.Control: Adaptive grid component
    """
    # Calculate columns based on available width and minimum item width
    cols = max(1, content_width // min_item_width)
    
    # Calculate responsive spacing
    spacing = _get_responsive_spacing_for_screen_size(screen_size, "main")
    run_spacing = _get_responsive_spacing_for_screen_size(screen_size, "run")
    
    # Create grid with calculated columns
    return ft.GridView(
        controls=items,
        runs_count=cols,
        max_extent=min_item_width,
        child_aspect_ratio=1.0,
        spacing=spacing,
        run_spacing=run_spacing
    )


def _get_responsive_spacing_for_screen_size(screen_size: ScreenSize, spacing_type: str) -> int:
    """
    Get responsive spacing value based on screen size
    
    Args:
        screen_size: Current screen size
        spacing_type: Type of spacing ("main" or "run")
        
    Returns:
        int: Spacing value in pixels
    """
    base_spacing = {
        "main": 16,
        "run": 12
    }.get(spacing_type, 16)
    
    # Adjust spacing based on screen size
    if screen_size == ScreenSize.MOBILE:
        return max(8, base_spacing // 2)
    elif screen_size == ScreenSize.TABLET:
        return int(base_spacing * 0.75)
    elif screen_size == ScreenSize.WIDE_DESKTOP:
        return int(base_spacing * 1.25)
    else:  # DESKTOP
        return base_spacing


class ResponsiveLayoutFactory:
    """
    Factory class for creating responsive layout components
    
    SINGLE RESPONSIBILITY: Centralized factory for responsive UI creation
    """
    
    @staticmethod
    def create_responsive_card_grid(
        items: List[ft.Control],
        screen_size: ScreenSize,
        content_width: int,
        card_min_width: int = 280
    ) -> ft.Control:
        """
        Create a grid of responsive cards
        
        Args:
            items: Content items for cards
            screen_size: Current screen size
            content_width: Available content width
            card_min_width: Minimum card width
            
        Returns:
            ft.Control: Grid of responsive cards
        """
        # Wrap items in mobile-friendly cards
        cards = [create_mobile_friendly_card(item, screen_size) for item in items]
        
        # Create adaptive grid
        return create_adaptive_grid(cards, content_width, card_min_width, screen_size)
    
    @staticmethod
    def create_responsive_form(
        fields: List[ft.Control],
        screen_size: ScreenSize,
        single_column_threshold: ScreenSize = ScreenSize.TABLET
    ) -> ft.Control:
        """
        Create responsive form layout
        
        Args:
            fields: Form field controls
            screen_size: Current screen size
            single_column_threshold: Screen size below which to use single column
            
        Returns:
            ft.Control: Responsive form layout
        """
        if screen_size.value <= single_column_threshold.value:
            # Single column for mobile/tablet
            return ft.Column(
                controls=fields,
                spacing=_get_responsive_spacing_for_screen_size(screen_size, "main"),
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
            ], spacing=_get_responsive_spacing_for_screen_size(screen_size, "main"))
    
    @staticmethod
    def create_responsive_header(
        title: str,
        actions: List[ft.Control] = None,
        screen_size: ScreenSize = ScreenSize.DESKTOP
    ) -> ft.Control:
        """
        Create responsive header with title and actions
        
        Args:
            title: Header title text
            actions: Optional action controls
            screen_size: Current screen size
            
        Returns:
            ft.Control: Responsive header component
        """
        title_text = EnhancedResponsiveLayout.create_text_with_truncation(
            text=title,
            size=24 if screen_size != ScreenSize.MOBILE else 20,
            weight=ft.FontWeight.BOLD
        )
        
        if not actions:
            return title_text
        
        if screen_size == ScreenSize.MOBILE:
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