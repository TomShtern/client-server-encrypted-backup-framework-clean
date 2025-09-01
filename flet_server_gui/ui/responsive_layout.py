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

# Import extracted breakpoint management components
from flet_server_gui.layout.breakpoint_manager import (
    BreakpointManager,
    ScreenSize,
    BreakpointSize,
    DeviceType,
    StandardBreakpoint,
    DesktopBreakpoint,
    BreakpointConfig,
    Breakpoint,
    MD3DesktopBreakpoints,
    STANDARD_MD3_BREAKPOINTS
)

# Import extracted navigation pattern management components
from flet_server_gui.layout.navigation_pattern_manager import (
    NavigationPatternManager,
    NavigationPattern,
    LayoutMode
)

# Import extracted responsive component registry components
from flet_server_gui.layout.responsive_component_registry import (
    ResponsiveComponentRegistry,
    ResponsiveConfig,
    LayoutConstraints
)

# Import extracted layout event dispatcher components
from flet_server_gui.layout.layout_event_dispatcher import (
    LayoutEventDispatcher
)

# Import extracted responsive layout utilities
from flet_server_gui.layout.responsive_layout_utils import (
    EnhancedResponsiveLayout,
    ResponsiveLayoutFactory,
    create_mobile_friendly_card,
    create_adaptive_grid
)


# Enums extracted to flet_server_gui.layout.breakpoint_manager


# LayoutMode and NavigationPattern enums extracted to flet_server_gui.layout.navigation_pattern_manager


# Dataclasses and constants extracted to flet_server_gui.layout.breakpoint_manager


# BreakpointManager and MD3DesktopBreakpoints extracted to flet_server_gui.layout.breakpoint_manager




# LayoutConstraints and ResponsiveConfig extracted to flet_server_gui.layout.responsive_component_registry


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
        
        # Initialize managers
        self.navigation_manager = NavigationPatternManager()
        self.component_registry = ResponsiveComponentRegistry(page)
        self.event_dispatcher = LayoutEventDispatcher(self.logger)
        
        # Current layout state
        self.current_screen_size = ScreenSize.DESKTOP
        
        # Configuration
        self.breakpoint_config = BreakpointConfig()
        
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
            asyncio.create_task(self.event_dispatcher.fire_event("screen_size_changed", {
                "old_size": old_screen_size,
                "new_size": new_screen_size,
                "width": width,
                "height": height
            }))
        
        # Calculate new layout mode using navigation manager
        new_layout_mode = self.navigation_manager.calculate_layout_mode(width, height, new_screen_size)
        if self.navigation_manager.update_layout_mode(new_layout_mode):
            asyncio.create_task(self.event_dispatcher.fire_event("layout_mode_changed", {
                "old_mode": old_layout_mode,
                "new_mode": new_layout_mode
            }))
        
        # Update navigation pattern if needed using navigation manager
        new_nav_pattern = self.navigation_manager.calculate_navigation_pattern(new_screen_size)
        if self.navigation_manager.update_navigation_pattern(new_nav_pattern):
            asyncio.create_task(self.event_dispatcher.fire_event("navigation_pattern_changed", {
                "new_pattern": new_nav_pattern
            }))
        
        # Update component registry with new screen size
        self.component_registry.update_screen_size(new_screen_size)
        
        # Update all responsive components (delegated to registry)
        asyncio.create_task(self.component_registry.update_all_components())
    
    def register_responsive_component(self, 
                                    component_id: str,
                                    component: ft.Control,
                                    config: ResponsiveConfig,
                                    constraints: Optional[LayoutConstraints] = None) -> None:
        """
        Register component for responsive layout management
        Delegates to ResponsiveComponentRegistry
        
        Args:
            component_id: Unique identifier for the component
            component: Flet control component
            config: Configuration for responsive behavior
            constraints: Optional layout constraints
        """
        self.component_registry.register_component(component_id, component, config, constraints)
    
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
        
        # Calculate responsive properties using registry
        responsive_props = self.component_registry.calculate_responsive_properties(config)
        
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
        return self.navigation_manager.adapt_navigation_for_screen_size(self.current_screen_size)
    
    def get_content_area_constraints(self) -> Tuple[int, int]:
        """
        Get available content area dimensions
        
        Returns:
            Tuple[int, int]: Available width and height
        """
        # Calculate content area using navigation manager
        return self.navigation_manager.get_content_area_constraints(self.page_width, self.page_height)
    
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
        self.event_dispatcher.register_callback(event_type, callback)
    
    def unregister_layout_callback(self, event_type: str, callback: Callable) -> bool:
        """Unregister layout change callback"""
        return self.event_dispatcher.unregister_callback(event_type, callback)
    
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
    
    # _calculate_layout_mode and _calculate_navigation_pattern extracted to NavigationPatternManager
    
    # _calculate_responsive_properties extracted to ResponsiveComponentRegistry
    
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
        return self.navigation_manager.get_responsive_spacing(self.current_screen_size, spacing_type)
    
    # _calculate_navigation_overhead extracted to NavigationPatternManager
    
    def _get_default_responsive_config(self) -> Dict[str, Any]:
        """Get default responsive configuration properties"""
        return {
            "margin": self._get_responsive_spacing("main") // 2,
            "padding": self._get_responsive_spacing("main"),
            "border_radius": 8 if self.current_screen_size != ScreenSize.MOBILE else 4
        }
    
    # _update_component_layout and _update_all_responsive_components extracted to ResponsiveComponentRegistry
    
    
    def get_layout_stats(self) -> Dict[str, Any]:
        """
        Get layout management statistics
        
        Returns:
            Dict with layout statistics
        """
        nav_stats = self.navigation_manager.get_navigation_stats()
        registry_stats = self.component_registry.get_registry_stats()
        return {
            "screen_size": self.current_screen_size.value,
            "layout_mode": nav_stats["layout_mode"],
            "navigation_pattern": nav_stats["navigation_pattern"],
            "page_dimensions": {"width": self.page_width, "height": self.page_height},
            "content_area": self.get_content_area_constraints(),
            "responsive_components": registry_stats["total_components"],
            "registered_callbacks": self.event_dispatcher.get_total_callbacks(),
            "navigation_stats": nav_stats,
            "registry_stats": registry_stats,
            "event_dispatcher_stats": self.event_dispatcher.get_event_statistics()
        }




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