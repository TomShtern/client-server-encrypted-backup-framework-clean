#!/usr/bin/env python3
"""
Simple Server Bridge for FletV2
A minimal server bridge implementation for fallback scenarios.
"""

import flet as ft
from typing import List, Dict, Any, Optional


class SimpleServerBridge:
    """
    Simple server bridge implementation for fallback scenarios.
    
    This provides minimal functionality for when the full server bridge is not available.
    """
    
    def __init__(self):
        """Initialize simple server bridge."""
        self.connected = True
        print("[INFO] SimpleServerBridge initialized")
    
    def get_clients(self) -> List[Dict[str, Any]]:
        """
        Get mock client data.
        
        Returns:
            List[Dict[str, Any]]: List of client dictionaries
        """
        return [
            {
                "client_id": "client_001",
                "address": "192.168.1.101:54321",
                "status": "Connected",
                "connected_at": "2025-09-03 10:30:15",
                "last_activity": "2025-09-03 14:45:30"
            },
            {
                "client_id": "client_002",
                "address": "192.168.1.102:54322",
                "status": "Registered",
                "connected_at": "2025-09-02 09:15:22",
                "last_activity": "2025-09-03 12:20:45"
            },
            {
                "client_id": "client_003",
                "address": "192.168.1.103:54323",
                "status": "Offline",
                "connected_at": "2025-09-01 14:22:10",
                "last_activity": "2025-09-02 16:33:55"
            },
            {
                "client_id": "client_004",
                "address": "192.168.1.104:54324",
                "status": "Connected",
                "connected_at": "2025-09-03 11:45:05",
                "last_activity": "2025-09-03 15:12:33"
            }
        ]
    
    def get_files(self) -> List[Dict[str, Any]]:
        """
        Get mock file data.
        
        Returns:
            List[Dict[str, Any]]: List of file dictionaries
        """
        return [
            {
                "file_id": "file_001",
                "filename": "document1.pdf",
                "size": 1024000,
                "uploaded_at": "2025-09-03 10:30:15",
                "client_id": "client_001"
            },
            {
                "file_id": "file_002",
                "filename": "image1.jpg",
                "size": 2048000,
                "uploaded_at": "2025-09-03 11:45:30",
                "client_id": "client_002"
            }
        ]
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get mock database information.
        
        Returns:
            Dict[str, Any]: Database information
        """
        return {
            "status": "Connected",
            "tables": 5,
            "records": 1250,
            "size": "45.2 MB"
        }
    
    def disconnect_client(self, client_id: str) -> bool:
        """
        Simulate disconnecting a client.
        
        Args:
            client_id (str): ID of client to disconnect
            
        Returns:
            bool: True if successful
        """
        print(f"[INFO] Simulated disconnect for client {client_id}")
        return True
    
    def delete_client(self, client_id: str) -> bool:
        """
        Simulate deleting a client.
        
        Args:
            client_id (str): ID of client to delete
            
        Returns:
            bool: True if successful
        """
        print(f"[INFO] Simulated delete for client {client_id}")
        return True
    
    def is_connected(self) -> bool:
        """
        Check if server is connected.
        
        Returns:
            bool: True if connected
        """
        return self.connected


# Factory function for easy instantiation
def create_simple_server_bridge() -> SimpleServerBridge:
    """
    Factory function to create a simple server bridge.
    
    Returns:
        SimpleServerBridge: Instance of simple server bridge
    """
    return SimpleServerBridge()