#!/usr/bin/env python3
"""
Mock Data Generator for FletV2 Development
Provides realistic test data for GUI development and testing.

TODO: DELETE THIS ENTIRE FILE when connecting to production server/database
This file is ONLY for development purposes and should not exist in production.
"""

import random
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

# Set up logger for this module
logger = logging.getLogger(__name__)


class MockDataGenerator:
    """
    Generate realistic mock data for development
    
    Features:
    - 30-60 client profiles with realistic data
    - Dynamic file metadata
    - Simulated server activity
    - Consistent data relationships
    - Time-based data changes for testing real-time updates
    """
    
    def __init__(self, num_clients: int = 45):
        """Initialize with specified number of mock clients"""
        self.num_clients = num_clients
        self.start_time = time.time()
        
        # Generate consistent mock data
        self._generate_base_data()
        
        # Track dynamic changes for real-time testing
        self.last_update = time.time()
        self.change_counter = 0
    
    def _generate_base_data(self):
        """Generate base mock data that remains consistent"""
        
        # Client name templates for realistic variety
        client_prefixes = [
            "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
            "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi",
            "Rho", "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega",
            "Enterprise", "Production", "Development", "Testing", "Staging"
        ]
        
        client_suffixes = [
            "Workstation", "Server", "Laptop", "Desktop", "Node", "Instance",
            "Machine", "Host", "System", "Device", "Terminal", "Client"
        ]
        
        # File type distributions for realism
        file_types = {
            ".pdf": 25,
            ".docx": 20,
            ".xlsx": 15,
            ".jpg": 12,
            ".png": 10,
            ".txt": 8,
            ".mp4": 5,
            ".zip": 3,
            ".py": 2
        }
        
        # Generate clients
        self.clients = []
        for i in range(self.num_clients):
            client_id = f"client_{i+1:03d}"
            
            # Generate realistic client data
            prefix = random.choice(client_prefixes)
            suffix = random.choice(client_suffixes)
            client_name = f"{prefix} {suffix}"
            
            # Generate IP in realistic ranges
            ip = f"192.168.{random.randint(1, 10)}.{random.randint(10, 250)}"
            port = random.randint(54321, 54400)
            
            # Generate connection times
            base_time = datetime.now() - timedelta(days=random.randint(0, 30))
            last_activity = base_time + timedelta(
                hours=random.randint(0, 24),
                minutes=random.randint(0, 59)
            )
            
            # Realistic status distribution
            status_weights = [
                ("Connected", 40),
                ("Registered", 35),
                ("Offline", 20),
                ("Error", 5)
            ]
            status = random.choices(
                [s[0] for s in status_weights],
                weights=[s[1] for s in status_weights]
            )[0]
            
            client = {
                "client_id": client_id,
                "name": client_name,
                "address": f"{ip}:{port}",
                "status": status,
                "connected_at": base_time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_activity": last_activity.strftime("%Y-%m-%d %H:%M:%S"),
                "has_public_key": random.choice([True, False]),
                "has_aes_key": random.choice([True, False]),
                "files_count": 0,  # Will be calculated
                "total_size": 0    # Will be calculated
            }
            self.clients.append(client)
        
        # Generate files for clients
        self.files = []
        for client in self.clients:
            # Each client has 0-3 files (most have 1)
            num_files = random.choices([0, 1, 2, 3], weights=[10, 70, 15, 5])[0]
            
            for j in range(num_files):
                # Generate realistic filename
                base_names = [
                    "document", "report", "image", "photo", "data", "backup",
                    "config", "log", "archive", "export", "import", "script"
                ]
                base_name = random.choice(base_names)
                file_extension = random.choices(
                    list(file_types.keys()),
                    weights=list(file_types.values())
                )[0]
                filename = f"{base_name}_{j+1}{file_extension}"
                
                # Generate consistent file_id that matches files view format  
                file_id = f"file_{hash(filename) % 10000}"
                
                # Generate realistic file sizes
                if file_extension in [".jpg", ".png"]:
                    file_size = random.randint(500_000, 5_000_000)  # 500KB - 5MB
                elif file_extension in [".pdf", ".docx"]:
                    file_size = random.randint(100_000, 2_000_000)  # 100KB - 2MB
                elif file_extension in [".mp4"]:
                    file_size = random.randint(10_000_000, 100_000_000)  # 10MB - 100MB
                elif file_extension in [".zip"]:
                    file_size = random.randint(1_000_000, 50_000_000)  # 1MB - 50MB
                else:
                    file_size = random.randint(1000, 500_000)  # 1KB - 500KB
                
                # Generate upload time
                upload_time = datetime.now() - timedelta(
                    days=random.randint(0, 7),
                    hours=random.randint(0, 23)
                )
                
                file_data = {
                    "id": file_id,  # Primary ID for UI consistency  
                    "file_id": file_id,
                    "name": filename,  # Changed from "filename" to match files view expectation
                    "filename": filename,  # Keep both for compatibility
                    "path": f"/home/user/{random.choice(['documents', 'downloads', 'desktop'])}/{filename}",
                    "pathname": f"/home/user/{random.choice(['documents', 'downloads', 'desktop'])}/{filename}",  # Keep both for compatibility
                    "size": file_size,
                    "type": file_extension.replace('.', ''),  # File extension without dot for type field
                    "uploaded_at": upload_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "modification_date": upload_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "modified": upload_time.isoformat(),  # ISO format for modified field
                    "owner": client["name"].split()[0].lower(),  # Extract owner from client name
                    "client_id": client["client_id"],
                    "client_name": client["name"],
                    "verified": random.choice([True, False]),
                    "crc": random.randint(100000000, 999999999),
                    "status": random.choice(["Complete", "Uploading", "Failed", "Queued"])
                }
                
                self.files.append(file_data)
                
                # Update client totals
                client["files_count"] += 1
                client["total_size"] += file_size
    
    def get_clients(self) -> List[Dict[str, Any]]:
        """Get client data with dynamic updates for real-time testing"""
        self._apply_dynamic_changes()
        return self.clients.copy()
    
    def get_files(self) -> List[Dict[str, Any]]:
        """Get file data with dynamic updates"""
        self._apply_dynamic_changes()
        return self.files.copy()
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get dynamic server status for real-time testing"""
        uptime_seconds = int(time.time() - self.start_time)
        uptime_minutes = uptime_seconds // 60
        uptime_hours = uptime_minutes // 60
        
        if uptime_hours > 0:
            uptime = f"{uptime_hours}h {uptime_minutes % 60}m"
        else:
            uptime = f"{uptime_minutes}m"
        
        active_clients = len([c for c in self.clients if c["status"] == "Connected"])
        total_files = len(self.files)
        total_size = sum(f["size"] for f in self.files)
        storage_gb = total_size / (1024 * 1024 * 1024)
        
        return {
            "server_running": True,
            "port": 1256,
            "uptime": uptime,
            "total_transfers": total_files + random.randint(0, 50),
            "active_clients": active_clients,
            "total_files": total_files,
            "storage_used": f"{storage_gb:.2f} GB",
            "cpu_usage": random.uniform(10, 40),
            "memory_usage": random.uniform(30, 60),
            "disk_usage": random.uniform(60, 80)
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get dynamic system metrics"""
        # Simulate realistic system metrics with some variation
        base_cpu = 25 + 10 * (0.5 - random.random())  # 20-30% base
        base_memory = 45 + 10 * (0.5 - random.random())  # 40-50% base
        base_disk = 75 + 5 * (0.5 - random.random())  # 72-78% base
        
        return {
            'cpu_usage': max(5, min(95, base_cpu + random.uniform(-5, 15))),
            'memory_usage': max(10, min(90, base_memory + random.uniform(-5, 10))),
            'disk_usage': max(50, min(95, base_disk + random.uniform(-2, 5))),
            'memory_total_gb': 16,
            'memory_used_gb': random.uniform(6, 12),
            'disk_total_gb': 500,
            'disk_used_gb': random.uniform(350, 400),
            'network_sent_mb': random.uniform(1000, 5000),
            'network_recv_mb': random.uniform(2000, 8000),
            'active_connections': len([c for c in self.clients if c["status"] == "Connected"]),
            'cpu_cores': 8
        }
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        total_records = len(self.clients) + len(self.files) + random.randint(500, 1000)
        size_mb = (total_records * 0.5) + random.uniform(10, 50)
        
        return {
            "status": "Connected",
            "tables": 6,
            "records": total_records,
            "size": f"{size_mb:.1f} MB"
        }
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get mock log entries"""
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        components = ["Server", "Client", "Database", "File Transfer", "Authentication"]
        
        logs = []
        for i in range(50):  # Last 50 log entries
            timestamp = datetime.now() - timedelta(
                hours=random.randint(0, 24),
                minutes=random.randint(0, 59)
            )
            
            level = random.choices(log_levels, weights=[50, 25, 15, 10])[0]
            component = random.choice(components)
            
            # Generate realistic log messages
            messages = {
                "INFO": [
                    f"Client connected from {random.choice([c['address'] for c in self.clients[:5]])}",
                    f"File transfer completed successfully",
                    f"Database backup completed",
                    f"Server status check passed"
                ],
                "WARNING": [
                    f"Client connection unstable",
                    f"High memory usage detected",
                    f"File verification failed, retrying",
                    f"Database query slow"
                ],
                "ERROR": [
                    f"Failed to authenticate client",
                    f"File transfer interrupted",
                    f"Database connection lost",
                    f"Disk space running low"
                ],
                "DEBUG": [
                    f"Processing client request",
                    f"Cache hit ratio: {random.randint(70, 95)}%",
                    f"Memory usage: {random.randint(30, 70)}%",
                    f"Active threads: {random.randint(5, 15)}"
                ]
            }
            
            message = random.choice(messages[level])
            
            logs.append({
                "id": i + 1,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "level": level,
                "component": component,
                "message": message
            })
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return logs
    
    def _apply_dynamic_changes(self):
        """Apply small changes to simulate real-time activity"""
        current_time = time.time()
        
        # Apply changes every 30 seconds
        if current_time - self.last_update > 30:
            self.last_update = current_time
            self.change_counter += 1
            
            # Randomly change 1-2 client statuses
            clients_to_change = random.sample(self.clients, min(2, len(self.clients)))
            for client in clients_to_change:
                old_status = client["status"]
                
                # Status transition probabilities
                if old_status == "Connected":
                    new_status = random.choices(
                        ["Connected", "Offline"],
                        weights=[90, 10]
                    )[0]
                elif old_status == "Offline":
                    new_status = random.choices(
                        ["Offline", "Connected"],
                        weights=[80, 20]
                    )[0]
                else:
                    new_status = random.choices(
                        ["Connected", "Registered", "Offline"],
                        weights=[40, 50, 10]
                    )[0]
                
                if new_status != old_status:
                    client["status"] = new_status
                    client["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Occasionally add a new file
            if self.change_counter % 3 == 0 and len(self.files) < 100:
                self._add_random_file()
    
    def _add_random_file(self):
        """Add a random new file for dynamic testing"""
        if not self.clients:
            return
        
        client = random.choice(self.clients)
        file_id = f"file_{len(self.files)+1:03d}"
        
        filename = f"new_file_{len(self.files)}.pdf"
        file_size = random.randint(100_000, 2_000_000)
        
        new_file = {
            "file_id": file_id,
            "filename": filename,
            "pathname": f"/home/user/documents/{filename}",
            "size": file_size,
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modification_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "client_id": client["client_id"],
            "client_name": client["name"],
            "verified": False,
            "crc": random.randint(100000000, 999999999),
            "status": "Uploading"
        }
        
        self.files.append(new_file)
        client["files_count"] += 1
        client["total_size"] += file_size
    
    def get_table_data(self, table_name: str) -> Dict[str, Any]:
        """Get table data for database view"""
        if table_name == "clients":
            return {
                "columns": ["id", "name", "address", "status", "last_seen", "files_count"],
                "rows": [
                    {
                        "id": c["client_id"],
                        "name": c["name"],
                        "address": c["address"],
                        "status": c["status"],
                        "last_seen": c["last_activity"],
                        "files_count": c["files_count"]
                    }
                    for c in self.clients
                ]
            }
        elif table_name == "files":
            return {
                "columns": ["id", "filename", "client_id", "size", "uploaded_at", "verified"],
                "rows": [
                    {
                        "id": f["file_id"],
                        "filename": f["filename"],
                        "client_id": f["client_id"],
                        "size": f["size"],
                        "uploaded_at": f["uploaded_at"],
                        "verified": f["verified"]
                    }
                    for f in self.files
                ]
            }
        else:
            return {"columns": [], "rows": []}

    def delete_file(self, file_id: str) -> bool:
        """Delete a file from mock data by file_id."""
        try:
            original_count = len(self.files)
            # Remove file with matching id (could be file_id or id field)
            self.files = [f for f in self.files if f.get('file_id') != file_id and f.get('id') != file_id]
            deleted = len(self.files) < original_count
            if deleted:
                logger.info(f"MockDataGenerator: Deleted file {file_id}")
            else:
                logger.warning(f"MockDataGenerator: File {file_id} not found for deletion")
            return deleted
        except Exception as e:
            logger.error(f"MockDataGenerator delete_file error: {e}")
            return False

    def delete_client(self, client_id: str) -> bool:
        """Delete a client from mock data by client_id."""
        try:
            original_count = len(self.clients)
            # Remove client with matching id (could be client_id or id field)
            self.clients = [c for c in self.clients if c.get('client_id') != client_id and c.get('id') != client_id]
            deleted = len(self.clients) < original_count
            if deleted:
                logger.info(f"MockDataGenerator: Deleted client {client_id}")
            else:
                logger.warning(f"MockDataGenerator: Client {client_id} not found for deletion")
            return deleted
        except Exception as e:
            logger.error(f"MockDataGenerator delete_client error: {e}")
            return False


# Singleton instance for consistent data across the application
_mock_generator_instance = None

def get_mock_generator() -> MockDataGenerator:
    """Get singleton mock data generator instance"""
    global _mock_generator_instance
    if _mock_generator_instance is None:
        _mock_generator_instance = MockDataGenerator()
    return _mock_generator_instance