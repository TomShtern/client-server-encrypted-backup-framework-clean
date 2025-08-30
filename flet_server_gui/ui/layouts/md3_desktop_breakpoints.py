#!/usr/bin/env python3
"""
Material Design 3 Desktop Breakpoint System
Enhanced responsive layout utilities with full MD3 desktop breakpoints
"""

import flet as ft
from typing import Dict, Any, Optional, Union
from enum import Enum


class DesktopBreakpoint(Enum):
    """Material Design 3 desktop breakpoints"""
    XS = "xs"      # < 600px - Very small windows
    SM = "sm"      # 600-905px - Small windows
    MD = "md"      # 905-1240px - Medium windows (13-16" displays)
    LG = "lg"      # 1240-1440px - Large windows (16-24" displays)
    XL = "xl"      # 1440-1920px - Extra large windows (24"+ displays)
    XXL = "xxl"    # > 1920px - Ultra large displays


class MD3DesktopBreakpoints:
    """Material Design 3 desktop breakpoint system"""
    
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
    """Enhanced responsive layout utilities with full MD3 desktop support"""
    
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
            span_config = MD3DesktopBreakpoints.create_column_config()
        
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


# Export commonly used functions
__all__ = [
    "DesktopBreakpoint",
    "MD3DesktopBreakpoints",
    "EnhancedResponsiveLayout"
]