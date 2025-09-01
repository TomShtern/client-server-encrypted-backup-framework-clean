#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NavigationPatternManager - Extracted from responsive_layout.py
Handles navigation pattern calculation and switching logic.

This component was extracted to follow single responsibility principle
and reduce complexity of the ResponsiveLayoutManager.
"""

import Shared.utils.utf8_solution  # UTF-8 solution

from enum import Enum
from typing import Dict, Optional
from .breakpoint_manager import ScreenSize


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


class NavigationPatternManager:
    """
    Manages navigation pattern detection and switching.
    
    SINGLE RESPONSIBILITY: Navigation pattern calculation and adaptation
    """
    
    def __init__(self):
        """Initialize navigation pattern manager"""
        # Current navigation state
        self.current_navigation_pattern = NavigationPattern.RAIL
        self.current_layout_mode = LayoutMode.EXPANDED
        
        # Navigation overhead cache
        self._navigation_overhead_cache: Dict[NavigationPattern, Dict[str, int]] = {}
        
        # Initialize navigation overhead values
        self._init_navigation_overhead()
    
    def _init_navigation_overhead(self) -> None:
        """Initialize navigation overhead values for different patterns"""
        self._navigation_overhead_cache = {
            NavigationPattern.RAIL: {"width": 80, "height": 0},
            NavigationPattern.BOTTOM_NAV: {"width": 0, "height": 80},
            NavigationPattern.DRAWER: {"width": 0, "height": 0},  # Closed by default
            NavigationPattern.TOP_TABS: {"width": 0, "height": 48},
            NavigationPattern.BREADCRUMB: {"width": 0, "height": 32}
        }
    
    def calculate_navigation_pattern(self, screen_size: ScreenSize) -> NavigationPattern:
        """
        Calculate optimal navigation pattern for screen size
        
        Args:
            screen_size: Current screen size category
            
        Returns:
            NavigationPattern: Optimal navigation pattern for the screen size
        """
        if screen_size == ScreenSize.MOBILE:
            return NavigationPattern.BOTTOM_NAV
        elif screen_size == ScreenSize.TABLET:
            return NavigationPattern.DRAWER
        else:
            return NavigationPattern.RAIL
    
    def calculate_layout_mode(self, width: int, height: int, screen_size: ScreenSize) -> LayoutMode:
        """
        Calculate optimal layout mode for given dimensions
        
        Args:
            width: Page width in pixels
            height: Page height in pixels  
            screen_size: Current screen size category
            
        Returns:
            LayoutMode: Optimal layout mode for the dimensions
        """
        if screen_size == ScreenSize.MOBILE:
            return LayoutMode.COMPACT
        elif screen_size == ScreenSize.TABLET:
            return LayoutMode.MEDIUM
        else:
            return LayoutMode.EXPANDED
    
    def calculate_navigation_overhead(self, 
                                    navigation_pattern: Optional[NavigationPattern] = None) -> Dict[str, int]:
        """
        Calculate space consumed by navigation elements
        
        Args:
            navigation_pattern: Specific pattern to calculate for, or current if None
        
        Returns:
            Dict with width and height overhead in pixels
        """
        pattern = navigation_pattern or self.current_navigation_pattern
        return self._navigation_overhead_cache.get(pattern, {"width": 0, "height": 0}).copy()
    
    def adapt_navigation_for_screen_size(self, screen_size: ScreenSize) -> NavigationPattern:
        """
        Get appropriate navigation pattern for current screen size
        
        Args:
            screen_size: Screen size to adapt navigation for
        
        Returns:
            NavigationPattern: Recommended navigation pattern
        """
        return self.calculate_navigation_pattern(screen_size)
    
    def update_navigation_pattern(self, pattern: NavigationPattern) -> bool:
        """
        Update current navigation pattern
        
        Args:
            pattern: New navigation pattern to set
            
        Returns:
            bool: True if pattern was changed, False if it was already set
        """
        if self.current_navigation_pattern != pattern:
            self.current_navigation_pattern = pattern
            return True
        return False
    
    def update_layout_mode(self, mode: LayoutMode) -> bool:
        """
        Update current layout mode
        
        Args:
            mode: New layout mode to set
            
        Returns:
            bool: True if mode was changed, False if it was already set
        """
        if self.current_layout_mode != mode:
            self.current_layout_mode = mode
            return True
        return False
    
    def get_content_area_constraints(self, page_width: int, page_height: int) -> tuple[int, int]:
        """
        Get available content area dimensions accounting for navigation overhead
        
        Args:
            page_width: Total page width
            page_height: Total page height
            
        Returns:
            Tuple[int, int]: Available content width and height
        """
        nav_overhead = self.calculate_navigation_overhead()
        
        content_width = max(0, page_width - nav_overhead["width"])
        content_height = max(0, page_height - nav_overhead["height"])
        
        return content_width, content_height
    
    def is_navigation_collapsible(self, 
                                navigation_pattern: Optional[NavigationPattern] = None) -> bool:
        """
        Check if navigation pattern is collapsible/hideable
        
        Args:
            navigation_pattern: Pattern to check, or current if None
            
        Returns:
            bool: True if navigation can be collapsed/hidden
        """
        pattern = navigation_pattern or self.current_navigation_pattern
        
        # Drawer and rail can be collapsed, bottom nav and tabs cannot
        return pattern in (NavigationPattern.DRAWER, NavigationPattern.RAIL)
    
    def get_navigation_stats(self) -> Dict[str, str]:
        """
        Get current navigation state statistics
        
        Returns:
            Dict with current navigation state information
        """
        return {
            "navigation_pattern": self.current_navigation_pattern.value,
            "layout_mode": self.current_layout_mode.value,
            "is_collapsible": str(self.is_navigation_collapsible()),
            "overhead_width": str(self.calculate_navigation_overhead()["width"]),
            "overhead_height": str(self.calculate_navigation_overhead()["height"])
        }
    
    def get_responsive_spacing(self, screen_size: ScreenSize, spacing_type: str = "main") -> int:
        """
        Get responsive spacing value based on screen size and navigation pattern
        
        Args:
            screen_size: Current screen size
            spacing_type: Type of spacing ("main" or "run")
            
        Returns:
            int: Spacing value in pixels
        """
        base_spacing_map = {
            ScreenSize.MOBILE: {"main": 8, "run": 8},
            ScreenSize.TABLET: {"main": 12, "run": 12},
            ScreenSize.DESKTOP: {"main": 16, "run": 16},
            ScreenSize.WIDE_DESKTOP: {"main": 20, "run": 20}
        }
        
        return base_spacing_map[screen_size].get(spacing_type, 12)