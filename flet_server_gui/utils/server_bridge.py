#!/usr/bin/env python3
"""
Modular Server Bridge (Refactored)
Composition-based architecture using specialized manager components.
Replaces the monolithic server_bridge.py with focused single-responsibility modules.
"""

import sys
import os
from typing import Optional, List, Dict, Any, Callable

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

# Import modular components from managers directory
from ..managers.server_manager import ServerManager, ServerInfo
from ..managers.database_manager import DatabaseManager as ServerDataManager, RealClient
from ..managers.file_operations_manager import FileOperationsManager

try:
    from python_server.server.server import BackupServer
    SERVER_AVAILABLE = True
except ImportError:
    SERVER_AVAILABLE = False
    print("[WARNING] Server integration not available")


class ModularServerBridge:
    """Refactored server bridge using composition pattern with specialized managers."""
    
    def __init__(self, server_instance: Optional[BackupServer] = None, database_name: Optional[str] = None) -> None:
        """Initialize with modular component managers."""
        
        if not SERVER_AVAILABLE:
            raise RuntimeError("Server integration required but not available")
        
        self.server_instance = server_instance
        
                # Initialize UNIFIED server manager (consolidates lifecycle + monitoring + connection status)
        self.server_manager = ServerManager(server_instance)
        
        # Initialize database manager
        self.data_manager = ServerDataManager(server_instance, database_name)
        
        print(f"[SUCCESS] Modular server bridge initialized with specialized managers ({database_name or 'default database'})")
    
    # ============================================================================
    # SERVER OPERATIONS (delegated to unified server_manager)
    # ============================================================================
    
    async def get_server_status(self) -> ServerInfo:
        """Get current server status"""
        status = await self.server_manager.get_server_status()
        
        # Enhance with database stats from data manager
        try:
            db_stats = self.data_manager.get_database_stats()
            status.total_clients = db_stats.get('total_clients', 0)
            status.total_transfers = db_stats.get('total_files', 0)
        except Exception as e:
            print(f"[WARNING] Could not enhance status with database stats: {e}")
        
        return status
    
    async def start_server(self) -> bool:
        """Start the server"""
        return await self.server_manager.start_server()
    
    async def stop_server(self) -> bool:
        """Stop the server"""
        return await self.server_manager.stop_server()
    
    async def restart_server(self) -> bool:
        """Restart the server"""
        return await self.server_manager.restart_server()
    
    # ============================================================================
    # DATA OPERATIONS (delegated to data_manager)
    # ============================================================================
    
    def get_all_clients(self) -> List[RealClient]:
        """Get all clients"""
        print("[BRIDGE_TRACE] ========== BRIDGE GET ALL CLIENTS ==========")
        print(f"[BRIDGE_TRACE] Data manager: {type(self.data_manager)}")

        try:
            result = self.data_manager.get_all_clients()
            print(f"[BRIDGE_TRACE] Data manager returned {len(result)} clients")
            return result
        except Exception as e:
            print(f"[BRIDGE_TRACE] X Exception in get_all_clients: {e}")
            import traceback
            print(f"[BRIDGE_TRACE] Traceback: {traceback.format_exc()}")
            return []
    
    def get_all_files(self) -> List[Dict[str, Any]]:
        """Get all files"""
        return self.data_manager.get_all_files()
    
    def get_recent_activity(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent activity"""
        return self.data_manager.get_recent_activity(count)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return self.data_manager.get_database_stats()
    
    # Client operations
    def disconnect_client(self, client_id: str) -> bool:
        """Disconnect a client"""
        print("[BRIDGE_TRACE] ========== BRIDGE DISCONNECT CLIENT ==========")
        print(f"[BRIDGE_TRACE] Client ID: {client_id}")
        print(f"[BRIDGE_TRACE] Data manager: {type(self.data_manager)}")

        try:
            result = self.data_manager.disconnect_client(client_id)
            print(f"[BRIDGE_TRACE] Data manager returned: {result}")
            return result
        except Exception as e:
            print(f"[BRIDGE_TRACE] ✗ Exception in disconnect_client: {e}")
            import traceback
            print(f"[BRIDGE_TRACE] Traceback: {traceback.format_exc()}")
            return False
    
    def delete_client(self, client_id: str) -> bool:
        """Delete a client"""
        print("[BRIDGE_TRACE] ========== BRIDGE DELETE CLIENT ==========")
        print(f"[BRIDGE_TRACE] Client ID: {client_id}")
        print(f"[BRIDGE_TRACE] Data manager: {type(self.data_manager)}")

        try:
            result = self.data_manager.delete_client(client_id)
            print(f"[BRIDGE_TRACE] Data manager returned: {result}")
            return result
        except Exception as e:
            print(f"[BRIDGE_TRACE] ✗ Exception in delete_client: {e}")
            import traceback
            print(f"[BRIDGE_TRACE] Traceback: {traceback.format_exc()}")
            return False
    
    def disconnect_multiple_clients(self, client_ids: List[str]) -> int:
        """Disconnect multiple clients"""
        return self.data_manager.disconnect_multiple_clients(client_ids)
    
    def delete_multiple_clients(self, client_ids: List[str]) -> int:
        """Delete multiple clients"""
        return self.data_manager.delete_multiple_clients(client_ids)
    
    # Database operations
    def backup_database(self, destination_path: str) -> bool:
        """Backup database"""
        return self.data_manager.backup_database(destination_path)
    
    def export_database_to_csv(self, table_name: str, destination_path: str) -> bool:
        """Export database to CSV"""
        return self.data_manager.export_database_to_csv(table_name, destination_path)
    
    def get_database_tables(self) -> List[str]:
        """Get database tables"""
        return self.data_manager.get_database_tables()
    
    def import_clients_from_data(self, client_data_list: List[Dict[str, Any]]) -> int:
        """Import clients from data"""
        return self.data_manager.import_clients_from_data(client_data_list)
    
    def update_client(self, client_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a client's record"""
        print("[BRIDGE_TRACE] ========== BRIDGE UPDATE CLIENT ==========")
        print(f"[BRIDGE_TRACE] Client ID: {client_id}")
        print(f"[BRIDGE_TRACE] Update Data: {update_data}")
        print(f"[BRIDGE_TRACE] Data manager: {type(self.data_manager)}")

        try:
            result = self.data_manager.update_client(client_id, update_data)
            print(f"[BRIDGE_TRACE] Data manager returned: {result}")
            return result
        except Exception as e:
            print(f"[BRIDGE_TRACE] ✗ Exception in update_client: {e}")
            import traceback
            print(f"[BRIDGE_TRACE] Traceback: {traceback.format_exc()}")
            return False
    
    def update_database_row(self, table_name: str, row_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a row in a database table"""
        print("[BRIDGE_TRACE] ========== BRIDGE UPDATE DATABASE ROW ==========")
        print(f"[BRIDGE_TRACE] Table: {table_name}")
        print(f"[BRIDGE_TRACE] Row ID: {row_id}")
        print(f"[BRIDGE_TRACE] Update Data: {update_data}")
        print(f"[BRIDGE_TRACE] Data manager: {type(self.data_manager)}")

        try:
            result = self.data_manager.update_database_row(table_name, row_id, update_data)
            print(f"[BRIDGE_TRACE] Data manager returned: {result}")
            return result
        except Exception as e:
            print(f"[BRIDGE_TRACE] ✗ Exception in update_database_row: {e}")
            import traceback
            print(f"[BRIDGE_TRACE] Traceback: {traceback.format_exc()}")
            return False
    
    # ============================================================================
    # FILE OPERATIONS (delegated to file_manager)
    # ============================================================================
    
    def delete_file(self, file_info: Dict[str, Any]) -> bool:
        """Delete a file"""
        return self.data_manager.delete_file(file_info)
    
    def delete_multiple_files(self, file_infos: List[Dict[str, Any]]) -> int:
        """Delete multiple files"""
        return self.data_manager.delete_multiple_files(file_infos)
    
    def download_file(self, file_info: Dict[str, Any], destination_path: str) -> bool:
        """Download a file"""
        return self.file_manager.download_file(file_info, destination_path)
    
    def verify_file(self, file_info: Dict[str, Any]) -> bool:
        """Verify a file"""
        return self.file_manager.verify_file(file_info)
    
    def upload_file_to_storage(self, file_path: str, client_name: str = "system") -> bool:
        """Upload file to storage"""
        return self.file_manager.upload_file_to_storage(file_path, client_name)
    
    def cleanup_old_files_by_age(self, days_threshold: int) -> Dict[str, Any]:
        """Clean up old files"""
        return self.file_manager.cleanup_old_files_by_age(days_threshold)
    
    def get_file_content(self, filename: str) -> bytes:
        """Get file content for preview"""
        return self.file_manager.get_file_content(filename)
    
    # ============================================================================
    # MONITORING OPERATIONS (delegated to unified server_manager)
    # ============================================================================
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return self.server_manager.get_system_metrics()
    
    def get_server_performance_metrics(self) -> Dict[str, Any]:
        """Get server performance metrics"""
        return self.server_manager.get_server_performance_metrics()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        return self.server_manager.get_health_status()
    
    def is_monitoring_available(self) -> bool:
        """Check if monitoring is available"""
        return self.server_manager.is_monitoring_available()
    
    # ============================================================================
    # COMPATIBILITY AND UTILITY METHODS
    # ============================================================================
    
    def is_real_integration(self) -> bool:
        """Check if using real integration (always True for modular bridge)"""
        return True
    
    def get_component_stats(self) -> Dict[str, Any]:
        """Get statistics about all components"""
        return {
            'server_manager': {
                'server_running': self.server_manager.is_server_running(),
                'uptime_start': self.server_manager.get_uptime(),
                'health_status': self.server_manager.get_health_status(),
                'monitoring_available': self.server_manager.is_monitoring_available()
            },
            'data_manager': self.data_manager.get_database_stats(),
            'file_manager': self.file_manager.get_storage_stats()
        }
    
    def get_client_list(self) -> List[RealClient]:
        """Legacy compatibility method"""
        return self.get_all_clients()
    
    def get_file_list(self) -> List[Dict[str, Any]]:
        """Legacy compatibility method"""
        return self.get_all_files()
    
    # ============================================================================
    # STANDARDIZED API METHODS (Phase 1 Critical Stability Fixes)
    # ============================================================================
    
    def is_server_running(self) -> bool:
        """Check if backup server is running (standardized API)"""
        return self.server_manager.is_server_running()
    
    def get_clients(self) -> List[RealClient]:
        """Get list of connected clients (standardized API)"""
        return self.get_all_clients()
    
    def get_files(self) -> List[Dict[str, Any]]:
        """Get list of managed files (standardized API)"""
        return self.get_all_files()
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get pending notifications (standardized API)"""
        notifications = []

        try:
            # Get system status notifications
            health = self.get_health_status()
            server_running = self.is_server_running()

            # Add server status notification
            notifications.append({
                "id": 1,
                "type": "system",
                "message": f"Server {'running' if server_running else 'stopped'}",
                "timestamp": health.get('timestamp', 'unknown'),
                "severity": "info" if server_running else "warning"
            })

            # Add health notifications
            if health.get('status') == 'unhealthy':
                notifications.append({
                    "id": 2,
                    "type": "system",
                    "message": "System health check failed",
                    "timestamp": health.get('timestamp', 'unknown'),
                    "severity": "error"
                })

            # Get recent activity for activity notifications  
            recent_activity = self.get_recent_activity(5)
            notifications.extend(
                {
                    "id": 10 + i,
                    "type": "activity",
                    "message": f"{activity.get('action', 'Unknown action')}: {activity.get('details', 'No details')}",
                    "timestamp": activity.get('timestamp', 'unknown'),
                    "severity": "info",
                }
                for i, activity in enumerate(recent_activity[:3])
            )
            # Add client/file count notifications
            clients = self.get_clients()
            files = self.get_files()

            notifications.append({
                "id": 20,
                "type": "stats",
                "message": f"Total: {len(clients)} clients, {len(files)} files",
                "timestamp": health.get('timestamp', 'unknown'),
                "severity": "info"
            })

        except Exception as e:
            # Fallback notification if data retrieval fails
            notifications.append({
                "id": 999,
                "type": "system",
                "message": f"Notification system error: {str(e)}",
                "timestamp": "error",
                "severity": "error"
            })

        # Sort by severity (error, warning, info) then by timestamp
        severity_order = {"error": 0, "warning": 1, "info": 2}
        notifications.sort(key=lambda x: (severity_order.get(x.get('severity', 'info'), 3), x.get('timestamp', '')))

        return notifications

    def register_connection_callback(self, callback: Callable[[Any], None]) -> None:
        """Register callback for connection status changes"""
        # Use the server lifecycle manager to register the callback
        if hasattr(self.server_lifecycle_manager, 'register_callback'):
            self.server_lifecycle_manager.register_callback(callback)


# Backward compatibility alias
ServerBridge = ModularServerBridge
