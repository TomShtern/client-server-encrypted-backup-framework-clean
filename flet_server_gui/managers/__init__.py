"""
Manager Classes - Consolidated & Framework-Native Architecture
Following the Duplication Mindset and Flet Framework Best Practices

Consolidated Architecture:
- NO manager duplication (eliminated "Slightly Different" Fallacy)
- Clear naming without redundant prefixes  
- Each manager owns ONE clear domain
- Uses Flet framework patterns instead of custom implementations
- Theme management uses native Flet theming (no custom ThemeManager)
"""

# Core managers
from .view_manager import ViewManager

# Theme management - NATIVE FLET APPROACH (no custom manager needed)
from ..theme import (
    THEMES, DEFAULT_THEME_NAME, 
    apply_theme_to_page, toggle_theme_mode, 
    get_current_theme_colors, setup_default_theme
)

# Data and server lifecycle (CONSOLIDATED)
from .database_manager import DatabaseManager
from .server_manager import ServerManager  # Unified server operations (includes connection status, lifecycle, monitoring)

# File operations (CONSOLIDATED)
from .file_operations_manager import FileOperationsManager  # Unified file operations and filtering

# Filtering (CONSOLIDATED) 
from .unified_filter_manager import UnifiedFilterManager, FilterDataType, create_client_filter_manager, create_file_filter_manager
# Navigation utilities moved to utils/simple_navigation.py (no custom manager needed)

# UI and settings
from .settings_manager import SettingsManager
from .toast_manager import ToastManager

__all__ = [
    # Core managers
    "ViewManager",
    
    # Theme management - NATIVE FLET FUNCTIONS (work WITH framework)
    "THEMES", 
    "DEFAULT_THEME_NAME",
    "apply_theme_to_page",
    "toggle_theme_mode", 
    "get_current_theme_colors",
    "setup_default_theme",
    
    # Data and server lifecycle (CONSOLIDATED)
    "DatabaseManager",
    "ServerManager",  # Unified server operations (includes connection, lifecycle, monitoring, performance)
    
    # File operations (CONSOLIDATED)
    "FileOperationsManager",  # Unified file operations and filtering
    
    # Filtering (CONSOLIDATED)
    "UnifiedFilterManager",
    "FilterDataType", 
    "create_client_filter_manager",
    "create_file_filter_manager",
    # NavigationManager removed - replaced by simple navigation utilities
    
    # UI and settings
    "SettingsManager",
    "ToastManager",
]
