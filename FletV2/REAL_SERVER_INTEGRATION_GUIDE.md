# FletV2 Real Server Integration Guide
written in 20.09.2025
**Complete implementation guide for integrating a real SQLite3-backed server with FletV2 GUI**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Understanding](#architecture-understanding)
3. [Server Object Interface Specification](#server-object-interface-specification)
4. [SQLite3 Database Schema](#sqlite3-database-schema)
5. [Implementation Examples](#implementation-examples)
6. [Integration Steps](#integration-steps)
7. [Testing & Validation](#testing--validation)
8. [Error Handling & Edge Cases](#error-handling--edge-cases)
9. [Performance Considerations](#performance-considerations)
10. [Troubleshooting](#troubleshooting)

---

## Overview

FletV2 GUI is designed with a **ServerBridge** abstraction that seamlessly delegates between real server implementations and mock data. The integration happens through **direct Python function calls** rather than HTTP APIs, making it faster, more secure, and easier to implement.

### Key Benefits of Direct Integration
- **🚀 Performance**: Direct function calls vs HTTP overhead
- **🔒 Security**: No network layer, no authentication complexity
- **🛠️ Simplicity**: No REST API implementation required
- **⚡ Low Latency**: No serialization/deserialization
- **🎯 Type Safety**: Direct Python objects, no JSON parsing

---

## Architecture Understanding

### ServerBridge Pattern

The `ServerBridge` class acts as an adapter between FletV2's UI components and your server implementation:

```python
# From utils/server_bridge.py
def _call_real_or_mock(self, method_name: str, *args, **kwargs):
    if self.real_server is not None and hasattr(self.real_server, method_name):
        result = getattr(self.real_server, method_name)(*args, **kwargs)
        return {'success': True, 'data': result, 'error': None}
    else:
        # Falls back to mock data
        return self._mock_db.method_name(*args, **kwargs)
```

### Integration Flow

1. **Your Server Object** ← Direct function calls ← **ServerBridge** ← **FletV2 Views**
2. Your server queries SQLite3 database
3. Returns Python objects (lists, dicts)
4. ServerBridge normalizes responses
5. UI updates with real data

---

## Server Object Interface Specification

Your server object must implement these methods to work with FletV2:

### Core Status Methods

```python
def is_connected(self) -> bool:
    """Health check - return True if server is operational"""

def get_server_status(self) -> dict:
    """Return server status for dashboard KPI cards

    Required fields:
    - running: bool
    - clients_connected: int
    - total_files: int
    - total_transfers: int
    - storage_used_gb: float
    - uptime_seconds: int
    """
```

### Client Management Methods

```python
def get_all_clients_from_db(self) -> list:
    """Return list of all clients

    Required fields per client:
    - id: str
    - client_id: str
    - name: str
    - status: str ("Connected", "Offline", "Registered")
    - last_seen: str (ISO format)
    - files_count: int
    - total_size: int (bytes)
    """

def get_client_details(self, client_id: str) -> dict:
    """Get detailed information for specific client"""

def add_client(self, client_data: dict) -> str:
    """Add new client, return client ID"""

def delete_client(self, client_id: str) -> bool:
    """Remove client and associated data"""

def disconnect_client(self, client_id: str) -> bool:
    """Disconnect active client"""
```

### File Management Methods

```python
def get_files(self) -> list:
    """Return all files

    Required fields per file:
    - id: str
    - filename: str
    - size: int (bytes)
    - client_id: str
    - uploaded_at: str (ISO format)
    - verified: bool
    - checksum: str (optional)
    """

def get_client_files(self, client_id: str) -> list:
    """Get files for specific client"""

def delete_file(self, file_id: str) -> bool:
    """Delete file from database and storage"""

def download_file(self, file_id: str) -> dict:
    """Prepare file for download

    Return format:
    - path: str (absolute path to file)
    - size: int
    - filename: str
    """

def verify_file(self, file_id: str) -> dict:
    """Verify file integrity

    Return format:
    - verified: bool
    - checksum: str
    - size: int
    """
```

### Database Access Methods

```python
def get_database_info(self) -> dict:
    """Return database schema information

    Return format:
    - tables: list[str]
    - total_size: str
    - version: str
    - last_backup: str (optional)
    """

def get_table_data(self, table_name: str) -> list:
    """Return all rows from specified table"""

def update_row(self, table_name: str, row_id: str, data: dict) -> bool:
    """Update database row"""

def delete_row(self, table_name: str, row_id: str) -> bool:
    """Delete database row"""
```

### Logging Methods

```python
def get_logs(self) -> list:
    """Return recent log entries

    Required fields per log:
    - id: int
    - timestamp: str (ISO format)
    - level: str ("info", "warning", "error", "debug")
    - message: str
    - source: str
    - client_id: str (optional)
    """

def clear_logs(self) -> bool:
    """Clear all log entries"""

def export_logs(self, format: str, filters: dict = None) -> dict:
    """Export logs in specified format

    Return format:
    - path: str (path to exported file)
    - format: str
    - count: int
    """
```

### Optional Async Methods

```python
async def get_clients_async(self) -> list:
    """Async version of get_all_clients_from_db"""

async def get_files_async(self) -> list:
    """Async version of get_files"""

async def get_logs_async(self) -> list:
    """Async version of get_logs"""
```

---

## SQLite3 Database Schema

### Recommended Schema Structure

```sql
-- Clients table
CREATE TABLE clients (
    id TEXT PRIMARY KEY,
    client_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'Registered',
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_size INTEGER DEFAULT 0,
    files_count INTEGER DEFAULT 0,
    ip_address TEXT,
    port INTEGER,
    encryption_key TEXT,
    metadata TEXT -- JSON for additional data
);

-- Files table
CREATE TABLE files (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    original_path TEXT,
    size INTEGER NOT NULL,
    checksum TEXT,
    client_id TEXT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified BOOLEAN DEFAULT FALSE,
    storage_path TEXT NOT NULL,
    mime_type TEXT,
    metadata TEXT, -- JSON for additional data
    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
);

-- Transfers table
CREATE TABLE transfers (
    id TEXT PRIMARY KEY,
    file_id TEXT NOT NULL,
    client_id TEXT NOT NULL,
    transfer_type TEXT NOT NULL, -- 'upload' or 'download'
    status TEXT DEFAULT 'pending', -- 'pending', 'active', 'completed', 'failed'
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    bytes_transferred INTEGER DEFAULT 0,
    total_bytes INTEGER,
    speed_mbps REAL,
    error_message TEXT,
    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE,
    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
);

-- Logs table
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    source TEXT DEFAULT 'server',
    client_id TEXT,
    file_id TEXT,
    metadata TEXT, -- JSON for additional data
    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE SET NULL,
    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE SET NULL
);

-- Server statistics table
CREATE TABLE server_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    clients_connected INTEGER DEFAULT 0,
    total_files INTEGER DEFAULT 0,
    total_storage_gb REAL DEFAULT 0,
    active_transfers INTEGER DEFAULT 0,
    cpu_usage REAL DEFAULT 0,
    memory_usage REAL DEFAULT 0,
    disk_usage REAL DEFAULT 0
);

-- Indexes for performance
CREATE INDEX idx_clients_status ON clients(status);
CREATE INDEX idx_files_client_id ON files(client_id);
CREATE INDEX idx_files_uploaded_at ON files(uploaded_at);
CREATE INDEX idx_transfers_status ON transfers(status);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_client_id ON logs(client_id);
```

### Database Triggers (Optional)

```sql
-- Auto-update client stats when files change
CREATE TRIGGER update_client_stats_on_file_insert
AFTER INSERT ON files
BEGIN
    UPDATE clients
    SET files_count = (
        SELECT COUNT(*) FROM files WHERE client_id = NEW.client_id
    ),
    total_size = (
        SELECT COALESCE(SUM(size), 0) FROM files WHERE client_id = NEW.client_id
    )
    WHERE id = NEW.client_id;
END;

CREATE TRIGGER update_client_stats_on_file_delete
AFTER DELETE ON files
BEGIN
    UPDATE clients
    SET files_count = (
        SELECT COUNT(*) FROM files WHERE client_id = OLD.client_id
    ),
    total_size = (
        SELECT COALESCE(SUM(size), 0) FROM files WHERE client_id = OLD.client_id
    )
    WHERE id = OLD.client_id;
END;
```

---

## Implementation Examples

### Basic Server Implementation

```python
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import hashlib
import shutil

class BackupServer:
    """Real backup server implementation with SQLite3 database"""

    def __init__(self, db_path: str, storage_path: str = "storage"):
        self.db_path = db_path
        self.storage_path = storage_path
        self.start_time = datetime.now()

        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize SQLite3 database with schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            # Create tables (use schema from above)
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS clients (
                    id TEXT PRIMARY KEY,
                    client_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    status TEXT DEFAULT 'Registered',
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_size INTEGER DEFAULT 0,
                    files_count INTEGER DEFAULT 0,
                    ip_address TEXT,
                    port INTEGER,
                    encryption_key TEXT,
                    metadata TEXT
                );

                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    original_path TEXT,
                    size INTEGER NOT NULL,
                    checksum TEXT,
                    client_id TEXT NOT NULL,
                    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    verified BOOLEAN DEFAULT FALSE,
                    storage_path TEXT NOT NULL,
                    mime_type TEXT,
                    metadata TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    source TEXT DEFAULT 'server',
                    client_id TEXT,
                    file_id TEXT,
                    metadata TEXT
                );
            """)
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn

    def _log(self, level: str, message: str, client_id: str = None, file_id: str = None):
        """Add log entry to database"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO logs (level, message, client_id, file_id)
                VALUES (?, ?, ?, ?)
            """, (level, message, client_id, file_id))
            conn.commit()

    # === Core Status Methods ===

    def is_connected(self) -> bool:
        """Health check"""
        try:
            with self._get_connection() as conn:
                conn.execute("SELECT 1").fetchone()
            return True
        except Exception:
            return False

    def get_server_status(self) -> dict:
        """Return server status for dashboard KPI cards"""
        try:
            with self._get_connection() as conn:
                # Get counts
                clients_count = conn.execute(
                    "SELECT COUNT(*) FROM clients WHERE status = 'Connected'"
                ).fetchone()[0]

                total_files = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]

                total_size = conn.execute(
                    "SELECT COALESCE(SUM(size), 0) FROM files"
                ).fetchone()[0]

                active_transfers = conn.execute(
                    "SELECT COUNT(*) FROM transfers WHERE status = 'active'"
                ).fetchone()[0] if self._table_exists("transfers") else 0

                uptime = int((datetime.now() - self.start_time).total_seconds())

                return {
                    "running": True,
                    "clients_connected": clients_count,
                    "total_files": total_files,
                    "total_transfers": active_transfers,
                    "storage_used_gb": round(total_size / (1024**3), 2),
                    "uptime_seconds": uptime
                }
        except Exception as e:
            self._log("error", f"Failed to get server status: {e}")
            return {
                "running": False,
                "clients_connected": 0,
                "total_files": 0,
                "total_transfers": 0,
                "storage_used_gb": 0.0,
                "uptime_seconds": 0
            }

    def _table_exists(self, table_name: str) -> bool:
        """Check if table exists in database"""
        with self._get_connection() as conn:
            result = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?
            """, (table_name,)).fetchone()
            return result is not None

    # === Client Management Methods ===

    def get_all_clients_from_db(self) -> List[Dict[str, Any]]:
        """Return list of all clients"""
        try:
            with self._get_connection() as conn:
                rows = conn.execute("""
                    SELECT id, client_id, name, status, last_seen,
                           total_size, files_count, ip_address, created_at
                    FROM clients
                    ORDER BY last_seen DESC
                """).fetchall()

                clients = []
                for row in rows:
                    clients.append({
                        "id": row["id"],
                        "client_id": row["client_id"],
                        "name": row["name"],
                        "status": row["status"],
                        "last_seen": row["last_seen"],
                        "files_count": row["files_count"],
                        "total_size": row["total_size"],
                        "ip_address": row["ip_address"],
                        "created_at": row["created_at"]
                    })

                return clients
        except Exception as e:
            self._log("error", f"Failed to get clients: {e}")
            return []

    def get_client_details(self, client_id: str) -> Dict[str, Any]:
        """Get detailed information for specific client"""
        try:
            with self._get_connection() as conn:
                row = conn.execute("""
                    SELECT * FROM clients WHERE id = ? OR client_id = ?
                """, (client_id, client_id)).fetchone()

                if not row:
                    return {}

                # Get recent files for this client
                recent_files = conn.execute("""
                    SELECT id, filename, size, uploaded_at, verified
                    FROM files
                    WHERE client_id = ?
                    ORDER BY uploaded_at DESC
                    LIMIT 10
                """, (row["id"],)).fetchall()

                return {
                    "id": row["id"],
                    "client_id": row["client_id"],
                    "name": row["name"],
                    "status": row["status"],
                    "last_seen": row["last_seen"],
                    "created_at": row["created_at"],
                    "total_size": row["total_size"],
                    "files_count": row["files_count"],
                    "ip_address": row["ip_address"],
                    "port": row["port"],
                    "recent_files": [dict(f) for f in recent_files]
                }
        except Exception as e:
            self._log("error", f"Failed to get client details for {client_id}: {e}")
            return {}

    def add_client(self, client_data: Dict[str, Any]) -> str:
        """Add new client"""
        try:
            client_id = client_data.get("client_id") or f"client_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO clients (id, client_id, name, ip_address, port, status)
                    VALUES (?, ?, ?, ?, ?, 'Registered')
                """, (
                    client_id,
                    client_data.get("client_id", client_id),
                    client_data.get("name", "Unknown Client"),
                    client_data.get("ip_address"),
                    client_data.get("port")
                ))
                conn.commit()

            self._log("info", f"Client added: {client_data.get('name', client_id)}")
            return client_id
        except Exception as e:
            self._log("error", f"Failed to add client: {e}")
            return ""

    def delete_client(self, client_id: str) -> bool:
        """Remove client and associated data"""
        try:
            with self._get_connection() as conn:
                # Get client name for logging
                client = conn.execute(
                    "SELECT name FROM clients WHERE id = ? OR client_id = ?",
                    (client_id, client_id)
                ).fetchone()

                if not client:
                    return False

                # Delete client (CASCADE will handle files)
                conn.execute(
                    "DELETE FROM clients WHERE id = ? OR client_id = ?",
                    (client_id, client_id)
                )
                conn.commit()

            self._log("info", f"Client deleted: {client['name']}")
            return True
        except Exception as e:
            self._log("error", f"Failed to delete client {client_id}: {e}")
            return False

    def disconnect_client(self, client_id: str) -> bool:
        """Disconnect active client"""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE clients
                    SET status = 'Offline', last_seen = CURRENT_TIMESTAMP
                    WHERE (id = ? OR client_id = ?) AND status = 'Connected'
                """, (client_id, client_id))
                conn.commit()

            self._log("info", f"Client disconnected: {client_id}")
            return True
        except Exception as e:
            self._log("error", f"Failed to disconnect client {client_id}: {e}")
            return False

    # === File Management Methods ===

    def get_files(self) -> List[Dict[str, Any]]:
        """Return all files"""
        try:
            with self._get_connection() as conn:
                rows = conn.execute("""
                    SELECT f.id, f.filename, f.size, f.client_id, f.uploaded_at,
                           f.verified, f.checksum, f.mime_type,
                           c.name as client_name
                    FROM files f
                    LEFT JOIN clients c ON f.client_id = c.id
                    ORDER BY f.uploaded_at DESC
                """).fetchall()

                files = []
                for row in rows:
                    files.append({
                        "id": row["id"],
                        "filename": row["filename"],
                        "size": row["size"],
                        "client_id": row["client_id"],
                        "client_name": row["client_name"],
                        "uploaded_at": row["uploaded_at"],
                        "verified": bool(row["verified"]),
                        "checksum": row["checksum"],
                        "mime_type": row["mime_type"]
                    })

                return files
        except Exception as e:
            self._log("error", f"Failed to get files: {e}")
            return []

    def get_client_files(self, client_id: str) -> List[Dict[str, Any]]:
        """Get files for specific client"""
        try:
            with self._get_connection() as conn:
                rows = conn.execute("""
                    SELECT id, filename, size, uploaded_at, verified, checksum, mime_type
                    FROM files
                    WHERE client_id = ?
                    ORDER BY uploaded_at DESC
                """, (client_id,)).fetchall()

                return [dict(row) for row in rows]
        except Exception as e:
            self._log("error", f"Failed to get files for client {client_id}: {e}")
            return []

    def delete_file(self, file_id: str) -> bool:
        """Delete file from database and storage"""
        try:
            with self._get_connection() as conn:
                # Get file info for cleanup
                file_info = conn.execute("""
                    SELECT filename, storage_path, client_id
                    FROM files WHERE id = ?
                """, (file_id,)).fetchone()

                if not file_info:
                    return False

                # Delete file from storage
                if file_info["storage_path"] and os.path.exists(file_info["storage_path"]):
                    os.remove(file_info["storage_path"])

                # Delete from database
                conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
                conn.commit()

            self._log("info", f"File deleted: {file_info['filename']}",
                     client_id=file_info["client_id"], file_id=file_id)
            return True
        except Exception as e:
            self._log("error", f"Failed to delete file {file_id}: {e}")
            return False

    def download_file(self, file_id: str) -> Dict[str, Any]:
        """Prepare file for download"""
        try:
            with self._get_connection() as conn:
                file_info = conn.execute("""
                    SELECT filename, storage_path, size, mime_type
                    FROM files WHERE id = ?
                """, (file_id,)).fetchone()

                if not file_info or not os.path.exists(file_info["storage_path"]):
                    return {}

                return {
                    "path": file_info["storage_path"],
                    "filename": file_info["filename"],
                    "size": file_info["size"],
                    "mime_type": file_info["mime_type"]
                }
        except Exception as e:
            self._log("error", f"Failed to prepare download for file {file_id}: {e}")
            return {}

    def verify_file(self, file_id: str) -> Dict[str, Any]:
        """Verify file integrity"""
        try:
            with self._get_connection() as conn:
                file_info = conn.execute("""
                    SELECT storage_path, checksum, size
                    FROM files WHERE id = ?
                """, (file_id,)).fetchone()

                if not file_info or not os.path.exists(file_info["storage_path"]):
                    return {"verified": False, "error": "File not found"}

                # Calculate checksum
                with open(file_info["storage_path"], "rb") as f:
                    calculated_checksum = hashlib.sha256(f.read()).hexdigest()

                verified = calculated_checksum == file_info["checksum"]

                # Update verification status
                conn.execute("""
                    UPDATE files SET verified = ? WHERE id = ?
                """, (verified, file_id))
                conn.commit()

                return {
                    "verified": verified,
                    "checksum": calculated_checksum,
                    "size": file_info["size"]
                }
        except Exception as e:
            self._log("error", f"Failed to verify file {file_id}: {e}")
            return {"verified": False, "error": str(e)}

    # === Database Access Methods ===

    def get_database_info(self) -> Dict[str, Any]:
        """Return database schema information"""
        try:
            with self._get_connection() as conn:
                # Get table names
                tables = conn.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """).fetchall()

                table_names = [t[0] for t in tables]

                # Get database size
                db_size = os.path.getsize(self.db_path)
                size_mb = round(db_size / (1024 * 1024), 2)

                return {
                    "tables": table_names,
                    "total_size": f"{size_mb} MB",
                    "version": sqlite3.sqlite_version,
                    "path": self.db_path,
                    "last_backup": None  # Implement if needed
                }
        except Exception as e:
            self._log("error", f"Failed to get database info: {e}")
            return {"tables": [], "total_size": "0 MB", "version": "unknown"}

    def get_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Return all rows from specified table"""
        try:
            with self._get_connection() as conn:
                # Validate table name to prevent SQL injection
                valid_tables = [t[0] for t in conn.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """).fetchall()]

                if table_name not in valid_tables:
                    return []

                rows = conn.execute(f"SELECT * FROM {table_name} LIMIT 1000").fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            self._log("error", f"Failed to get data from table {table_name}: {e}")
            return []

    def update_row(self, table_name: str, row_id: str, data: Dict[str, Any]) -> bool:
        """Update database row"""
        try:
            # This is a simplified implementation - you may want more sophisticated logic
            with self._get_connection() as conn:
                # Validate table name
                valid_tables = [t[0] for t in conn.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """).fetchall()]

                if table_name not in valid_tables:
                    return False

                # Build UPDATE query dynamically
                set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
                values = list(data.values()) + [row_id]

                conn.execute(f"""
                    UPDATE {table_name}
                    SET {set_clause}
                    WHERE id = ?
                """, values)
                conn.commit()

            self._log("info", f"Updated row in {table_name}: {row_id}")
            return True
        except Exception as e:
            self._log("error", f"Failed to update row in {table_name}: {e}")
            return False

    def delete_row(self, table_name: str, row_id: str) -> bool:
        """Delete database row"""
        try:
            with self._get_connection() as conn:
                # Validate table name
                valid_tables = [t[0] for t in conn.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """).fetchall()]

                if table_name not in valid_tables:
                    return False

                conn.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
                conn.commit()

            self._log("info", f"Deleted row from {table_name}: {row_id}")
            return True
        except Exception as e:
            self._log("error", f"Failed to delete row from {table_name}: {e}")
            return False

    # === Logging Methods ===

    def get_logs(self) -> List[Dict[str, Any]]:
        """Return recent log entries"""
        try:
            with self._get_connection() as conn:
                rows = conn.execute("""
                    SELECT id, timestamp, level, message, source, client_id, file_id
                    FROM logs
                    ORDER BY timestamp DESC
                    LIMIT 1000
                """).fetchall()

                logs = []
                for row in rows:
                    logs.append({
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "level": row["level"],
                        "message": row["message"],
                        "source": row["source"],
                        "client_id": row["client_id"],
                        "file_id": row["file_id"]
                    })

                return logs
        except Exception as e:
            print(f"Failed to get logs: {e}")  # Don't log this to avoid recursion
            return []

    def clear_logs(self) -> bool:
        """Clear all log entries"""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM logs")
                conn.commit()
            return True
        except Exception as e:
            self._log("error", f"Failed to clear logs: {e}")
            return False

    def export_logs(self, format: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export logs in specified format"""
        try:
            logs = self.get_logs()

            # Apply filters if provided
            if filters:
                if "level" in filters:
                    logs = [log for log in logs if log["level"] == filters["level"]]
                if "start_date" in filters:
                    logs = [log for log in logs if log["timestamp"] >= filters["start_date"]]
                if "end_date" in filters:
                    logs = [log for log in logs if log["timestamp"] <= filters["end_date"]]

            # Export to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs_export_{timestamp}.{format.lower()}"
            export_path = os.path.join(self.storage_path, filename)

            if format.lower() == "json":
                with open(export_path, "w") as f:
                    json.dump(logs, f, indent=2, default=str)
            elif format.lower() == "csv":
                import csv
                with open(export_path, "w", newline="") as f:
                    if logs:
                        writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                        writer.writeheader()
                        writer.writerows(logs)
            else:
                return {}

            return {
                "path": export_path,
                "format": format,
                "count": len(logs)
            }
        except Exception as e:
            self._log("error", f"Failed to export logs: {e}")
            return {}

    # === Optional Async Methods ===

    async def get_clients_async(self) -> List[Dict[str, Any]]:
        """Async version of get_all_clients_from_db"""
        return self.get_all_clients_from_db()

    async def get_files_async(self) -> List[Dict[str, Any]]:
        """Async version of get_files"""
        return self.get_files()

    async def get_logs_async(self) -> List[Dict[str, Any]]:
        """Async version of get_logs"""
        return self.get_logs()
```

### Integration Example

```python
# integration_example.py
import flet as ft
from utils.server_bridge import create_server_bridge
from main import FletV2App
from your_server import BackupServer  # Your implementation

def main():
    # Initialize your server
    server = BackupServer(
        db_path="backup_server.db",
        storage_path="backup_storage"
    )

    # Create server bridge with your server
    server_bridge = create_server_bridge(real_server=server)

    # Create and run FletV2 app
    def app_main(page: ft.Page):
        app = FletV2App(server_bridge=server_bridge)
        app._initialize_page(page)

    ft.app(target=app_main, port=8000, view=ft.WEB_BROWSER)

if __name__ == "__main__":
    main()
```

---

## Integration Steps

### Step 1: Implement Your Server Class

1. Create a new Python file (e.g., `backup_server.py`)
2. Implement the `BackupServer` class with all required methods
3. Test individual methods with sample data

### Step 2: Set Up SQLite3 Database

1. Create database schema using the provided SQL
2. Add sample data for testing
3. Verify database operations work correctly

### Step 3: Create Integration Script

1. Create a main script that instantiates your server
2. Pass server to `create_server_bridge()`
3. Initialize FletV2 with the server bridge

### Step 4: Test Integration

1. Start the application
2. Verify all views load correctly
3. Test CRUD operations in each view
4. Verify data persistence

### Step 5: Production Deployment

1. Configure proper database path
2. Set up file storage location
3. Implement backup procedures
4. Add monitoring and logging

---

## Testing & Validation

### Unit Tests

```python
import unittest
from your_server import BackupServer
import tempfile
import os

class TestBackupServer(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.mktemp(suffix=".db")
        self.storage_dir = tempfile.mkdtemp()
        self.server = BackupServer(self.db_file, self.storage_dir)

    def tearDown(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        if os.path.exists(self.storage_dir):
            import shutil
            shutil.rmtree(self.storage_dir)

    def test_server_health(self):
        self.assertTrue(self.server.is_connected())

    def test_server_status(self):
        status = self.server.get_server_status()
        self.assertIn("running", status)
        self.assertIn("clients_connected", status)
        self.assertIn("total_files", status)

    def test_client_management(self):
        # Test adding client
        client_id = self.server.add_client({
            "name": "Test Client",
            "ip_address": "127.0.0.1"
        })
        self.assertTrue(client_id)

        # Test getting clients
        clients = self.server.get_all_clients_from_db()
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0]["name"], "Test Client")

        # Test deleting client
        self.assertTrue(self.server.delete_client(client_id))
        clients = self.server.get_all_clients_from_db()
        self.assertEqual(len(clients), 0)

if __name__ == "__main__":
    unittest.main()
```

### Integration Testing

```python
# test_integration.py
def test_fletv2_integration():
    """Test FletV2 integration with real server"""
    from utils.server_bridge import create_server_bridge
    from your_server import BackupServer

    # Create test server
    server = BackupServer(":memory:", "/tmp/test_storage")

    # Create server bridge
    bridge = create_server_bridge(real_server=server)

    # Test server bridge methods
    assert bridge.is_connected()

    status = bridge.get_server_status()
    assert status["success"]
    assert "running" in status["data"]

    clients = bridge.get_all_clients_from_db()
    assert clients["success"]
    assert isinstance(clients["data"], list)

    print("✅ Integration test passed!")

if __name__ == "__main__":
    test_integration()
```

---

## Error Handling & Edge Cases

### Common Error Scenarios

1. **Database Connection Failures**
   ```python
   def is_connected(self) -> bool:
       try:
           with self._get_connection() as conn:
               conn.execute("SELECT 1").fetchone()
           return True
       except sqlite3.Error:
           return False
       except Exception:
           return False
   ```

2. **File System Errors**
   ```python
   def delete_file(self, file_id: str) -> bool:
       try:
           # ... database operations ...

           # Handle file deletion errors gracefully
           if file_info["storage_path"] and os.path.exists(file_info["storage_path"]):
               try:
                   os.remove(file_info["storage_path"])
               except (OSError, PermissionError) as e:
                   self._log("warning", f"Could not delete file from storage: {e}")
                   # Continue with database deletion

           return True
       except Exception as e:
           self._log("error", f"Failed to delete file {file_id}: {e}")
           return False
   ```

3. **Data Validation**
   ```python
   def add_client(self, client_data: Dict[str, Any]) -> str:
       # Validate required fields
       if not client_data.get("name"):
           raise ValueError("Client name is required")

       # Sanitize input
       name = client_data["name"].strip()[:100]  # Limit length

       # ... rest of implementation ...
   ```

### Graceful Degradation

```python
def get_server_status(self) -> dict:
    """Return server status with fallback values"""
    default_status = {
        "running": False,
        "clients_connected": 0,
        "total_files": 0,
        "total_transfers": 0,
        "storage_used_gb": 0.0,
        "uptime_seconds": 0
    }

    try:
        # ... actual implementation ...
        return actual_status
    except Exception as e:
        self._log("error", f"Failed to get server status: {e}")
        return default_status
```

---

## Performance Considerations

### Database Optimization

1. **Use Indexes**
   ```sql
   CREATE INDEX idx_files_client_id ON files(client_id);
   CREATE INDEX idx_logs_timestamp ON logs(timestamp);
   ```

2. **Limit Query Results**
   ```python
   def get_logs(self) -> List[Dict[str, Any]]:
       # Always limit results to prevent memory issues
       rows = conn.execute("""
           SELECT * FROM logs
           ORDER BY timestamp DESC
           LIMIT 1000
       """).fetchall()
   ```

3. **Use Connection Pooling** (for high-concurrency scenarios)
   ```python
   import threading
   from queue import Queue

   class ConnectionPool:
       def __init__(self, db_path: str, max_connections: int = 10):
           self.db_path = db_path
           self.pool = Queue(maxsize=max_connections)
           for _ in range(max_connections):
               conn = sqlite3.connect(db_path, check_same_thread=False)
               conn.row_factory = sqlite3.Row
               self.pool.put(conn)
   ```

### Memory Management

1. **Use Generators for Large Datasets**
   ```python
   def get_files_generator(self):
       """Generator version for large file lists"""
       with self._get_connection() as conn:
           cursor = conn.execute("SELECT * FROM files ORDER BY uploaded_at DESC")
           while True:
               rows = cursor.fetchmany(100)  # Process in batches
               if not rows:
                   break
               for row in rows:
                   yield dict(row)
   ```

2. **Implement Pagination**
   ```python
   def get_files_paginated(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
       offset = (page - 1) * per_page

       with self._get_connection() as conn:
           # Get total count
           total = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]

           # Get page data
           rows = conn.execute("""
               SELECT * FROM files
               ORDER BY uploaded_at DESC
               LIMIT ? OFFSET ?
           """, (per_page, offset)).fetchall()

           return {
               "files": [dict(row) for row in rows],
               "page": page,
               "per_page": per_page,
               "total": total,
               "pages": (total + per_page - 1) // per_page
           }
   ```

---

## Troubleshooting

### Common Issues and Solutions

1. **"Database is locked" Error**
   ```python
   # Solution: Use proper connection management
   def _get_connection(self):
       conn = sqlite3.connect(self.db_path, timeout=30.0)
       conn.execute("PRAGMA busy_timeout = 30000")
       return conn
   ```

2. **Memory Usage Growing**
   ```python
   # Solution: Implement cleanup and limits
   def cleanup_old_logs(self, days_to_keep: int = 30):
       cutoff_date = datetime.now() - timedelta(days=days_to_keep)
       with self._get_connection() as conn:
           conn.execute("DELETE FROM logs WHERE timestamp < ?", (cutoff_date,))
           conn.commit()
   ```

3. **FletV2 Shows Empty Data**
   - Check that your methods return the expected data structure
   - Verify ServerBridge is calling your methods (add logging)
   - Ensure database has sample data for testing

4. **Performance Issues**
   - Add database indexes
   - Implement pagination for large datasets
   - Use async methods where available
   - Profile database queries

### Debugging Tips

1. **Add Comprehensive Logging**
   ```python
   import logging

   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger(__name__)

   def get_clients(self):
       logger.debug("Getting all clients from database")
       try:
           # ... implementation ...
           logger.debug(f"Retrieved {len(clients)} clients")
           return clients
       except Exception as e:
           logger.error(f"Failed to get clients: {e}")
           raise
   ```

2. **Use Database Query Logging**
   ```python
   def _get_connection(self):
       conn = sqlite3.connect(self.db_path)
       conn.set_trace_callback(lambda sql: logger.debug(f"SQL: {sql}"))
       return conn
   ```

3. **Test Individual Methods**
   ```python
   if __name__ == "__main__":
       server = BackupServer("test.db")

       # Test individual methods
       print("Server status:", server.get_server_status())
       print("Clients:", server.get_all_clients_from_db())
       print("Files:", server.get_files())
   ```

---

## Conclusion

This guide provides a complete roadmap for integrating a real SQLite3-backed server with FletV2. The key points to remember:

1. **FletV2 is designed for this** - the ServerBridge pattern makes integration seamless
2. **Direct function calls** are simpler and more efficient than HTTP APIs
3. **Implement all required methods** for full functionality
4. **Use proper error handling** and logging
5. **Test thoroughly** before production deployment

The example implementation provides a solid foundation that you can customize for your specific backup server requirements. The ServerBridge will handle all the complexity of switching between your real server and mock data, making development and testing straightforward.

For questions or issues during implementation, refer to the troubleshooting section or examine the existing mock database implementation in `utils/mock_database_simulator.py` for additional patterns and examples.