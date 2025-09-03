#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ResponsiveComponentRegistry - Extracted from responsive_layout.py
Handles registration, storage, and updates of responsive UI components.

EXTRACTION STATUS: Phase 2 Continuation - Third of four manager extractions
SINGLE RESPONSIBILITY: Component registry management and lifecycle
"""

import Shared.utils.utf8_solution  # UTF-8 solution

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import flet as ft

# Import screen size enum from breakpoint manager
from flet_server_gui.utils.responsive_enums import ScreenSize


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


class ResponsiveComponentRegistry:
    """
    Manages responsive component registration and updates.
    
    SINGLE RESPONSIBILITY: Component registry management and lifecycle
    
    This class handles:
    - Registration of components for responsive behavior
    - Storage of component configurations and constraints  
    - Updates to component layout properties based on screen size changes
    - Lifecycle management of registered responsive components
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.logger = logging.getLogger(__name__)
        
        # Component registry storage
        self.responsive_components: Dict[str, Any] = {}
        self.layout_constraints: Dict[str, LayoutConstraints] = {}
        
        # Current screen size (will be updated by ResponsiveLayoutManager)
        self.current_screen_size = ScreenSize.DESKTOP
    
    def register_component(self, 
                          component_id: str,
                          component: ft.Control,
                          config: ResponsiveConfig,
                          constraints: Optional[LayoutConstraints] = None) -> None:
        """
        Register component for responsive layout management
        
        Args:
            component_id: Unique identifier for the component
            component: Flet control component
            config: Configuration for responsive behavior
            constraints: Optional layout constraints
        """
        self.responsive_components[component_id] = {
            "component": component,
            "config": config,
            "last_updated": datetime.now()
        }
        
        if constraints:
            self.layout_constraints[component_id] = constraints
        
        # Apply current responsive settings immediately
        asyncio.create_task(self.update_component(component_id))
    
    def unregister_component(self, component_id: str) -> bool:
        """
        Unregister component from responsive management
        
        Args:
            component_id: ID of component to unregister
            
        Returns:
            bool: True if component was found and removed
        """
        removed = False
        if component_id in self.responsive_components:
            del self.responsive_components[component_id]
            removed = True
        
        if component_id in self.layout_constraints:
            del self.layout_constraints[component_id]
        
        return removed
    
    def get_component_info(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about registered component
        
        Args:
            component_id: ID of component
            
        Returns:
            Optional[Dict]: Component info or None if not found
        """
        return self.responsive_components.get(component_id)
    
    def update_screen_size(self, new_screen_size: ScreenSize) -> None:
        """
        Update current screen size and trigger component updates
        
        Args:
            new_screen_size: New screen size category
        """
        self.current_screen_size = new_screen_size
        # Update all components for new screen size
        asyncio.create_task(self.update_all_components())
    
    def calculate_responsive_properties(self, config: ResponsiveConfig) -> Dict[str, Any]:
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
    
    async def update_component(self, component_id: str) -> None:
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
            responsive_props = self.calculate_responsive_properties(config)
            
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
    
    async def update_all_components(self) -> None:
        """Update all registered responsive components"""
        for component_id in list(self.responsive_components.keys()):
            await self.update_component(component_id)
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get component registry statistics
        
        Returns:
            Dict with registry statistics
        """
        return {
            "total_components": len(self.responsive_components),
            "total_constraints": len(self.layout_constraints),
            "current_screen_size": self.current_screen_size.value,
            "component_ids": list(self.responsive_components.keys())
        }
    
    def _get_default_responsive_config(self) -> Dict[str, Any]:
        """Get default responsive configuration properties"""
        spacing = self._get_responsive_spacing()
        return {
            "margin": spacing // 2,
            "padding": spacing,
            "border_radius": 8 if self.current_screen_size != ScreenSize.MOBILE else 4
        }
    
    def _get_responsive_spacing(self) -> int:
        """Get responsive spacing value based on screen size"""
        if self.current_screen_size == ScreenSize.MOBILE:
            return 8
        elif self.current_screen_size == ScreenSize.TABLET:
            return 12
        elif self.current_screen_size == ScreenSize.DESKTOP:
            return 16
        else:  # WIDE_DESKTOP
            return 20