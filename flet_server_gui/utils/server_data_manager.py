#!/usr/bin/env python3
"""
Server Data Manager
Handles database operations, client/file data retrieval, and bulk operations.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

try:
    from python_server.server.server import BackupServer
    from python_server.server.database import DatabaseManager
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("[WARNING] Database integration not available")


@dataclass
class RealClient:
    """Real client data structure"""
    client_id: str
    address: str
    connected_at: datetime
    last_activity: datetime
    status: str = "Connected"


class ServerDataManager:
    """Manages server data operations and database interactions"""
    
    def __init__(self, server_instance: Optional[BackupServer] = None, database_name: Optional[str] = None):
        self.server_instance = server_instance
        self.db_manager = None

        # Use MockaBase when running standalone (no server instance)
        if database_name is None and server_instance is None:
            # Check if MockaBase exists, if not create it
            mockabase_path = "MockaBase.db"
            if not os.path.exists(mockabase_path):
                print("[INFO] MockaBase not found, will use default database")
            else:
                database_name = mockabase_path
                print(f"[INFO] Using MockaBase: {database_name}")

        if DATABASE_AVAILABLE:
            try:
                self.db_manager = DatabaseManager(database_name)
                print(f"[INFO] Database connection established ({database_name or 'default'})")
            except Exception as e:
                print(f"[ERROR] Database initialization failed: {e}")
                raise RuntimeError(f"Database connection required: {e}") from e
        else:
            raise RuntimeError("Database integration required but not available")
    
    def get_all_clients(self) -> List[RealClient]:
        """Get list of all clients from database"""
        print("[DB_TRACE] ========== DATA MANAGER GET ALL CLIENTS ==========")
        print(f"[DB_TRACE] Database manager: {self.db_manager is not None}")
        print(f"[DB_TRACE] Server instance: {self.server_instance is not None}")

        try:
            clients = []

            if self.db_manager:
                print("[DB_TRACE] Calling db_manager.get_all_clients()")
                # Get clients from database
                client_records = self.db_manager.get_all_clients()
                print(f"[DB_TRACE] Database returned {len(client_records)} client records")

                active_client_ids = []
                if self.server_instance and hasattr(self.server_instance, 'clients'):
                    active_client_ids = list(self.server_instance.clients.keys())
                    print(f"[DB_TRACE] Active client IDs: {active_client_ids}")

                for i, record in enumerate(client_records):
                    print(f"[DB_TRACE] Processing client record {i}: {record}")
                    client_id = record.get('id', 'unknown')
                    is_connected = client_id in active_client_ids

                    client = RealClient(
                        client_id=client_id,
                        address=record.get('ip_address', 'unknown'),
                        connected_at=record.get('connected_at', datetime.now()),
                        last_activity=record.get('last_activity', datetime.now()),
                        status="Connected" if is_connected else "Offline"
                    )
                    clients.append(client)
                    print(f"[DB_TRACE] Created client: {client.client_id} ({client.status})")
            else:
                print("[DB_TRACE] ! No database manager available")

            print(f"[DB_TRACE] OK Returning {len(clients)} clients")
            return clients

        except Exception as e:
            print(f"[DB_TRACE] X Failed to get client list: {e}")
            import traceback
            print(f"[DB_TRACE] Traceback: {traceback.format_exc()}")
            return []
    
    def get_all_files(self) -> List[Dict[str, Any]]:
        """Get list of all files from database"""
        try:
            return self.db_manager.get_all_files() if self.db_manager else []
        except Exception as e:
            print(f"[ERROR] Failed to get file list: {e}")
            return []
    
    def get_recent_activity(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent activity from database"""
        try:
            if self.db_manager:
                return self.db_manager.get_recent_activity(limit=count)
            return []
            
        except Exception as e:
            print(f"[ERROR] Failed to get recent activity: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            if self.db_manager:
                return self.db_manager.get_database_stats()
            return {'total_clients': 0, 'total_files': 0, 'total_size': 0}
            
        except Exception as e:
            print(f"[ERROR] Failed to get database stats: {e}")
            return {'total_clients': 0, 'total_files': 0, 'total_size': 0}
    
    def disconnect_client(self, client_id: str) -> bool:
        """Disconnect a specific client"""
        print("[DB_TRACE] ========== DATA MANAGER DISCONNECT CLIENT ==========")
        print(f"[DB_TRACE] Client ID: {client_id}")
        print(f"[DB_TRACE] Server instance: {self.server_instance is not None}")

        try:
            if self.server_instance:
                print(f"[DB_TRACE] Server instance clients: {list(self.server_instance.clients.keys()) if self.server_instance.clients else []}")
                if client_id in self.server_instance.clients:
                    client = self.server_instance.clients[client_id]
                    print(f"[DB_TRACE] Found client object: {type(client)}")
                    client.disconnect()
                    print(f"[DB_TRACE] ✓ Client {client_id} disconnected")
                    return True
                else:
                    print(f"[DB_TRACE] ⚠ Client {client_id} not found in active clients")
                    return False
            else:
                print("[DB_TRACE] ⚠ No server instance available")
                return False

        except Exception as e:
            print(f"[DB_TRACE] ✗ Failed to disconnect client {client_id}: {e}")
            import traceback
            print(f"[DB_TRACE] Traceback: {traceback.format_exc()}")
            return False
    
    def delete_client(self, client_id: str) -> bool:
        """Delete a client from database"""
        print("[DB_TRACE] ========== DATA MANAGER DELETE CLIENT ==========")
        print(f"[DB_TRACE] Client ID: {client_id}")
        print(f"[DB_TRACE] Database manager: {self.db_manager is not None}")

        try:
            if self.db_manager:
                print(f"[DB_TRACE] Database manager type: {type(self.db_manager)}")
                print(f"[DB_TRACE] Calling db_manager.delete_client({client_id})")
                success = self.db_manager.delete_client(client_id)
                print(f"[DB_TRACE] Database manager returned: {success}")
                if success:
                    print(f"[DB_TRACE] ✓ Client {client_id} deleted from database")
                return success
            else:
                print("[DB_TRACE] ✗ No database manager available")
                return False

        except Exception as e:
            print(f"[DB_TRACE] ✗ Failed to delete client {client_id}: {e}")
            import traceback
            print(f"[DB_TRACE] Traceback: {traceback.format_exc()}")
            return False
    
    def disconnect_multiple_clients(self, client_ids: List[str]) -> int:
        """Disconnect multiple clients"""
        return sum(bool(self.disconnect_client(client_id))
               for client_id in client_ids)
    
    def delete_multiple_clients(self, client_ids: List[str]) -> int:
        """Delete multiple clients from database"""
        return sum(bool(self.delete_client(client_id))
               for client_id in client_ids)
    
    def delete_file(self, file_info: Dict[str, Any]) -> bool:
        """Delete a file from database and storage"""
        try:
            filename = file_info.get('filename')
            if not filename:
                print("[ERROR] No filename provided for deletion")
                return False
            
            if self.db_manager:
                success = self.db_manager.delete_file_record(filename)
                if success:
                    print(f"[SUCCESS] File {filename} deleted from database")
                    
                    # Also try to delete physical file
                    try:
                        file_path = os.path.join('received_files', filename)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"[SUCCESS] Physical file {filename} deleted")
                    except Exception as e:
                        print(f"[WARNING] Could not delete physical file: {e}")
                
                return success
            return False
            
        except Exception as e:
            print(f"[ERROR] Failed to delete file: {e}")
            return False
    
    def delete_multiple_files(self, file_infos: List[Dict[str, Any]]) -> int:
        """Delete multiple files"""
        return sum(bool(self.delete_file(file_info))
               for file_info in file_infos)
    
    def backup_database(self, destination_path: str) -> bool:
        """Create database backup"""
        try:
            if self.db_manager:
                return self.db_manager.backup_database(destination_path)
            return False
            
        except Exception as e:
            print(f"[ERROR] Failed to backup database: {e}")
            return False
    
    def export_database_to_csv(self, table_name: str, destination_path: str) -> bool:
        """Export database table to CSV"""
        try:
            if self.db_manager:
                return self.db_manager.export_to_csv(table_name, destination_path)
            return False
            
        except Exception as e:
            print(f"[ERROR] Failed to export database: {e}")
            return False
    
    def get_database_tables(self) -> List[str]:
        """Get list of database tables"""
        try:
            return self.db_manager.get_table_names() if self.db_manager else []
        except Exception as e:
            print(f"[ERROR] Failed to get database tables: {e}")
            return []
    
    def import_clients_from_data(self, client_data_list: List[Dict[str, Any]]) -> int:
        """Import clients from data"""
        try:
            if self.db_manager:
                return self.db_manager.import_clients(client_data_list)
            return 0
            
        except Exception as e:
            print(f"[ERROR] Failed to import clients: {e}")
            return 0
