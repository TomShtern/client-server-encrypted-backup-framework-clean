"""
Core Business Logic Module

This module contains the consolidated core business logic for the Flet server GUI,
separated from UI components for better maintainability and testability.

Classes:
    ServerOperations: Core server management operations
    ClientManagement: Core client management operations  
    FileManagement: Core file management operations
    
Phase 4 Consolidation:
    MaterialDesign3ThemeSystem: Unified theme system for Material Design 3
    ResponsiveLayoutSystem: Unified responsive layout system
    Design tokens and responsive utilities

Usage:
    from flet_server_gui.core import ServerOperations, ClientManagement, FileManagement
    from flet_server_gui.core import MaterialDesign3ThemeSystem, ResponsiveLayoutSystem
    
    # Initialize with server bridge
    server_ops = ServerOperations(server_bridge)
    client_mgmt = ClientManagement(server_bridge)
    file_mgmt = FileManagement(server_bridge)
    
    # Phase 4 theme and layout systems
    theme_system = MaterialDesign3ThemeSystem()
    layout_system = ResponsiveLayoutSystem()
"""

from .server_operations import ServerOperations
from .client_management import ClientManagement
from .file_management import FileManagement
from ..ui.unified_theme_system import MaterialDesign3ThemeSystem, theme_system, get_theme_system
from .design_tokens import (
    ColorRole, TypographyRole, LIGHT_COLOR_TOKENS, DARK_COLOR_TOKENS,
    TYPOGRAPHY_TOKENS, SPACING_TOKENS, ELEVATION_TOKENS,
    get_color_token, get_typography_token, get_spacing_token, get_elevation_token
)
from .responsive_layout import (
    ResponsiveLayoutSystem, BreakpointSize, DeviceType, Breakpoint,
    responsive_layout_system, get_responsive_layout_system
)

__all__ = [
    # Original core classes
    'ServerOperations',
    'ClientManagement', 
    'FileManagement',
    
    # Phase 4 theme system
    'MaterialDesign3ThemeSystem',
    'theme_system',
    'get_theme_system',
    
    # Phase 4 design tokens
    'ColorRole',
    'TypographyRole',
    'LIGHT_COLOR_TOKENS',
    'DARK_COLOR_TOKENS',
    'TYPOGRAPHY_TOKENS',
    'SPACING_TOKENS',
    'ELEVATION_TOKENS',
    'get_color_token',
    'get_typography_token',
    'get_spacing_token',
    'get_elevation_token',
    
    # Phase 4 responsive layout system
    'ResponsiveLayoutSystem',
    'BreakpointSize',
    'DeviceType',
    'Breakpoint',
    'responsive_layout_system',
    'get_responsive_layout_system',
]