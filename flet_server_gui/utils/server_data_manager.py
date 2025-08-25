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
    
    def __init__(self, server_instance: Optional[BackupServer] = None):
        self.server_instance = server_instance
        self.db_manager = None
        
        if DATABASE_AVAILABLE:
            try:
                self.db_manager = DatabaseManager()
                print("[INFO] Database connection established")
            except Exception as e:
                print(f"[ERROR] Database initialization failed: {e}")
                raise RuntimeError(f"Database connection required: {e}")
        else:
            raise RuntimeError("Database integration required but not available")
    
    def get_all_clients(self) -> List[RealClient]:
        """Get list of all clients from database"""
        try:
            clients = []
            
            if self.db_manager:
                # Get clients from database
                client_records = self.db_manager.get_all_clients()
                
                for record in client_records:
                    client = RealClient(
                        client_id=record.get('id', 'unknown'),
                        address=record.get('ip_address', 'unknown'),
                        connected_at=record.get('connected_at', datetime.now()),
                        last_activity=record.get('last_activity', datetime.now()),
                        status="Connected" if record.get('id') in 
                               (self.server_instance.clients.keys() if self.server_instance else [])
                               else "Offline"
                    )
                    clients.append(client)
            
            return clients
            
        except Exception as e:
            print(f"[ERROR] Failed to get client list: {e}")
            return []
    
    def get_all_files(self) -> List[Dict[str, Any]]:
        """Get list of all files from database"""
        try:
            if self.db_manager:
                return self.db_manager.get_all_files()
            return []
            
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
        try:
            if self.server_instance and client_id in self.server_instance.clients:
                client = self.server_instance.clients[client_id]
                client.disconnect()
                print(f"[SUCCESS] Client {client_id} disconnected")
                return True
            else:
                print(f"[WARNING] Client {client_id} not found or not connected")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to disconnect client {client_id}: {e}")
            return False
    
    def delete_client(self, client_id: str) -> bool:
        """Delete a client from database"""
        try:
            if self.db_manager:
                success = self.db_manager.delete_client(client_id)
                if success:
                    print(f"[SUCCESS] Client {client_id} deleted from database")
                return success
            return False
            
        except Exception as e:
            print(f"[ERROR] Failed to delete client {client_id}: {e}")
            return False
    
    def disconnect_multiple_clients(self, client_ids: List[str]) -> int:
        """Disconnect multiple clients"""
        success_count = 0
        for client_id in client_ids:
            if self.disconnect_client(client_id):
                success_count += 1
        return success_count
    
    def delete_multiple_clients(self, client_ids: List[str]) -> int:
        """Delete multiple clients from database"""
        success_count = 0
        for client_id in client_ids:
            if self.delete_client(client_id):
                success_count += 1
        return success_count
    
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
        success_count = 0
        for file_info in file_infos:
            if self.delete_file(file_info):
                success_count += 1
        return success_count
    
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
            if self.db_manager:
                return self.db_manager.get_table_names()
            return []
            
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
