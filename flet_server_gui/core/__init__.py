"""
Core Business Logic Module

This module contains the consolidated core business logic for the Flet server GUI,
separated from UI components for better maintainability and testability.

Classes:
    ServerOperations: Core server management operations
    ClientManagement: Core client management operations  
    FileManagement: Core file management operations

Usage:
    from flet_server_gui.core import ServerOperations, ClientManagement, FileManagement
    
    # Initialize with server bridge
    server_ops = ServerOperations(server_bridge)
    client_mgmt = ClientManagement(server_bridge)
    file_mgmt = FileManagement(server_bridge)
"""

from .server_operations import ServerOperations
from .client_management import ClientManagement
from .file_management import FileManagement

__all__ = [
    'ServerOperations',
    'ClientManagement', 
    'FileManagement'
]