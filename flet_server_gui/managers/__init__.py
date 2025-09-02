"""
Manager Classes - Single Responsibility Coordinators
Following the Duplication Mindset and Manager Class Consolidation Plan

Consolidated Architecture:
- NO manager duplication (eliminated "Slightly Different" Fallacy)
- Clear naming without redundant prefixes
- Each manager owns ONE clear domain
- Uses Flet framework patterns instead of custom implementations
"""

# Core managers
from .view_manager import ViewManager
from .theme_manager import ThemeManager

# Data and server lifecycle (CONSOLIDATED)
from .database_manager import DatabaseManager
from .server_manager import ServerManager  # Unified server operations (includes connection status, lifecycle, monitoring)

# File operations (CONSOLIDATED)
from .file_operations_manager import FileOperationsManager  # Unified file operations and filtering

# Filtering (CONSOLIDATED) 
from .unified_filter_manager import UnifiedFilterManager, FilterDataType, create_client_filter_manager, create_file_filter_manager
from .navigation_manager import NavigationManager

# UI and settings
from .settings_manager import SettingsManager
from .toast_manager import ToastManager

__all__ = [
    # Core managers
    "ViewManager",
    "ThemeManager", 
    
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
    "NavigationManager",
    
    # UI and settings
    "SettingsManager",
    "ToastManager",
]
