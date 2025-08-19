"""
Data structures and models for the KivyMD GUI
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class ClientInfo:
    """Data class for client information"""
    client_id: str
    username: str
    ip_address: str
    last_seen: datetime
    files_transferred: int
    status: str = "offline"

@dataclass
class FileInfo:
    """Data class for transferred file information"""
    filename: str
    size: int
    transfer_time: datetime
    client_id: str
    checksum: str
    file_path: str

@dataclass
class ServerStats:
    """Data class for server statistics"""
    uptime: str
    total_files: int
    total_clients: int
    active_connections: int
    bytes_transferred: int
    last_update: datetime

class DataManager:
    """Manager for handling data operations"""
    
    def __init__(self):
        self.clients: List[ClientInfo] = []
        self.files: List[FileInfo] = []
        self.stats: Optional[ServerStats] = None
    
    def add_client(self, client: ClientInfo):
        """Add a new client to the list"""
        self.clients.append(client)
    
    def add_file(self, file_info: FileInfo):
        """Add a new file to the list"""
        self.files.append(file_info)
    
    def update_stats(self, stats: ServerStats):
        """Update server statistics"""
        self.stats = stats