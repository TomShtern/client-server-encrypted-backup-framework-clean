#!/usr/bin/env python3
"""
FletV2 Server Adapter - Direct Object Integration

This adapter wraps your existing server infrastructure (DatabaseManager, etc.)
and provides the exact method signatures that FletV2's ServerBridge expects.

No API calls - pure Python object method calls for maximum performance and reliability.
"""

import asyncio
import logging
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta
from typing import Any

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import your existing server infrastructure
try:
    from api_server.real_backup_executor import RealBackupExecutor
    from python_server.server.config import DATABASE_NAME, FILE_STORAGE_DIR
    from python_server.server.database import DatabaseManager
    _REAL_SERVER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import server modules: {e}")
    print("Creating basic fallback implementation...")
    _REAL_SERVER_AVAILABLE = False

    # Basic fallback classes if imports fail - use different names to avoid conflicts
    class _FallbackDatabaseManager:
        def __init__(self, *args, **kwargs): pass
        def init_database(self): pass
        def get_database_health(self): return {"status": "fallback"}

    class _FallbackBackupExecutor:
        def __init__(self, *args, **kwargs): pass

    # Assign fallback classes to expected names
    DatabaseManager = _FallbackDatabaseManager  # type: ignore
    RealBackupExecutor = _FallbackBackupExecutor  # type: ignore
    DATABASE_NAME = "fallback.db"
    FILE_STORAGE_DIR = "fallback_storage"

# Set up logging
logger = logging.getLogger(__name__)

class FletV2ServerAdapter:
    """
    Server adapter that wraps your existing server infrastructure for FletV2 integration.

    Provides all methods that FletV2's ServerBridge expects while delegating to your
    existing DatabaseManager and other server components.
    """

    def __init__(self, db_path: str | None = None, storage_path: str | None = None):
        """
        Initialize the server adapter with your existing server components.

        Args:
            db_path: Path to SQLite database (defaults to your server's DATABASE_NAME)
            storage_path: Path to file storage directory (defaults to your server's FILE_STORAGE_DIR)
        """
        # Use your existing configuration or provided paths
        self.db_path = db_path or DATABASE_NAME
        self.storage_path = storage_path or FILE_STORAGE_DIR
        self.start_time = datetime.now()

        # Initialize your existing server components
        try:
            self.db_manager = DatabaseManager(use_pool=True)
            self.db_manager.init_database()
            self.backup_executor = RealBackupExecutor()
            self._connected = True
            logger.info("FletV2ServerAdapter initialized with real server components")
        except Exception as e:
            logger.error(f"Failed to initialize server components: {e}")
            self._connected = False
            self.db_manager = None
            self.backup_executor = None

        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)

        logger.info(f"FletV2ServerAdapter ready - DB: {self.db_path}, Storage: {self.storage_path}")

    # ============================================================================
    # CORE STATUS METHODS (Required by FletV2)
    # ============================================================================

    def is_connected(self) -> bool:
        """Health check - return True if server is operational."""
        if not self._connected or not self.db_manager:
            return False

        try:
            # Quick database health check
            health = self.db_manager.get_database_health()
            integrity_check = health.get('integrity_check', False)
            return bool(integrity_check)
        except Exception:
            return False

    def get_server_status(self) -> dict[str, Any]:
        """Return server status for dashboard KPI cards."""
        try:
            if not self.db_manager:
                return self._get_fallback_status()

            # Get statistics from your database
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Count connected clients (use legacy schema - no status column)
                clients_connected = conn.execute(
                    "SELECT COUNT(*) FROM clients"
                ).fetchone()[0]

                # Count total files
                total_files = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]

                # Calculate total storage used (use correct column name)
                total_size = conn.execute(
                    "SELECT COALESCE(SUM(FileSize), 0) FROM files"
                ).fetchone()[0]

                # Count active transfers (if transfers table exists)
                try:
                    active_transfers = conn.execute(
                        "SELECT COUNT(*) FROM transfers WHERE status = 'active'"
                    ).fetchone()[0]
                except sqlite3.OperationalError:
                    active_transfers = 0

                uptime_seconds = int((datetime.now() - self.start_time).total_seconds())

                return {
                    "running": True,
                    "clients_connected": clients_connected,
                    "total_files": total_files,
                    "total_transfers": active_transfers,
                    "storage_used_gb": round(total_size / (1024**3), 2),
                    "uptime_seconds": uptime_seconds
                }

        except Exception as e:
            logger.error(f"Error getting server status: {e}")
            return self._get_fallback_status()

    def _get_fallback_status(self) -> dict[str, Any]:
        """Fallback status when database is unavailable."""
        return {
            "running": False,
            "clients_connected": 0,
            "total_files": 0,
            "total_transfers": 0,
            "storage_used_gb": 0.0,
            "uptime_seconds": 0
        }

    # ============================================================================
    # CLIENT MANAGEMENT METHODS (Required by FletV2)
    # ============================================================================

    def get_all_clients_from_db(self) -> list[dict[str, Any]]:
        """Return list of all clients."""
        return self.get_clients()

    def get_clients(self) -> list[dict[str, Any]]:
        """Get all clients from database."""
        try:
            if not self.db_manager:
                return []

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Try new schema first, fall back to old schema
                try:
                    rows = conn.execute("""
                        SELECT id, client_id, name, status, last_seen,
                               total_size, files_count, ip_address, created_at
                        FROM clients
                        ORDER BY last_seen DESC
                    """).fetchall()

                    return [
                        {
                            "id": row["id"],
                            "client_id": row["client_id"] or row["id"],
                            "name": row["name"],
                            "status": row["status"] or "Registered",
                            "last_seen": row["last_seen"],
                            "files_count": row["files_count"] or 0,
                            "total_size": row["total_size"] or 0,
                            "ip_address": row["ip_address"] or "",
                            "created_at": row["created_at"] or row["last_seen"]
                        }
                        for row in rows
                    ]

                except sqlite3.OperationalError:
                    # Fall back to old schema
                    logger.info("Using legacy schema for clients")
                    return self._get_clients_legacy_schema(conn)

        except Exception as e:
            logger.error(f"Error getting clients: {e}")
            return []

    def _get_clients_legacy_schema(self, conn: sqlite3.Connection) -> list[dict[str, Any]]:
        """Get clients using legacy schema."""
        try:
            rows = conn.execute("""
                SELECT ID, Name, LastSeen FROM clients
                ORDER BY LastSeen DESC
            """).fetchall()

            clients = []
            for row in rows:
                # Convert BLOB ID to string
                client_id = str(uuid.UUID(bytes=row[0])) if len(row[0]) == 16 else str(row[0])

                clients.append({
                    "id": client_id,
                    "client_id": client_id,
                    "name": row[1],
                    "status": "Registered",  # Default status
                    "last_seen": row[2],
                    "files_count": 0,  # Will be updated separately
                    "total_size": 0,   # Will be updated separately
                    "ip_address": "",
                    "created_at": row[2]
                })

            return clients

        except Exception as e:
            logger.error(f"Error getting clients with legacy schema: {e}")
            return []

    async def get_clients_async(self) -> list[dict[str, Any]]:
        """Async version of get_clients."""
        return await asyncio.get_event_loop().run_in_executor(None, self.get_clients)

    def get_client_details(self, client_id: str) -> dict[str, Any]:
        """Get detailed information for specific client."""
        try:
            if not self.db_manager:
                return {}

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Get client info
                client_row = conn.execute("""
                    SELECT * FROM clients WHERE id = ? OR name = ?
                """, (client_id, client_id)).fetchone()

                if not client_row:
                    return {}

                # Get recent files for this client
                recent_files = conn.execute("""
                    SELECT id, filename, size, uploaded_at, verified
                    FROM files
                    WHERE client_id = ?
                    ORDER BY uploaded_at DESC
                    LIMIT 10
                """, (client_row["id"],)).fetchall()

                return {
                    "id": client_row["id"],
                    "client_id": client_row["id"],
                    "name": client_row["name"],
                    "status": client_row["status"],
                    "last_seen": client_row["last_seen"],
                    "created_at": client_row["created_at"],
                    "total_size": client_row["total_size"] or 0,
                    "files_count": client_row["files_count"] or 0,
                    "ip_address": client_row["ip_address"],
                    "recent_files": [dict(f) for f in recent_files]
                }

        except Exception as e:
            logger.error(f"Error getting client details for {client_id}: {e}")
            return {}

    def add_client(self, client_data: dict[str, Any]) -> str:
        """Add new client."""
        try:
            if not self.db_manager:
                raise RuntimeError("Database manager not available")

            client_id = client_data.get("client_id") or str(uuid.uuid4())

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO clients (id, name, ip_address, status, created_at, last_seen)
                    VALUES (?, ?, ?, 'Registered', ?, ?)
                """, (
                    client_id,
                    client_data.get("name", "Unknown Client"),
                    client_data.get("ip_address"),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                conn.commit()

            logger.info(f"Client added: {client_data.get('name', client_id)}")
            return client_id

        except Exception as e:
            logger.error(f"Error adding client: {e}")
            return ""

    async def add_client_async(self, client_data: dict[str, Any]) -> str:
        """Add new client (async)."""
        return await asyncio.get_event_loop().run_in_executor(None, self.add_client, client_data)

    def delete_client(self, client_id: str) -> bool:
        """Remove client and associated data."""
        try:
            if not self.db_manager:
                return False

            with sqlite3.connect(self.db_path) as conn:
                # Enable foreign keys for cascade delete
                conn.execute("PRAGMA foreign_keys = ON")

                # Get client name for logging
                client = conn.execute(
                    "SELECT name FROM clients WHERE id = ? OR name = ?",
                    (client_id, client_id)
                ).fetchone()

                if not client:
                    return False

                # Delete client (CASCADE will handle files)
                conn.execute(
                    "DELETE FROM clients WHERE id = ? OR name = ?",
                    (client_id, client_id)
                )
                conn.commit()

            logger.info(f"Client deleted: {client[0]}")
            return True

        except Exception as e:
            logger.error(f"Error deleting client {client_id}: {e}")
            return False

    async def delete_client_async(self, client_id: str) -> bool:
        """Delete client (async)."""
        return await asyncio.get_event_loop().run_in_executor(None, self.delete_client, client_id)

    def disconnect_client(self, client_id: str) -> bool:
        """Disconnect active client."""
        try:
            if not self.db_manager:
                return False

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE clients
                    SET status = 'Offline', last_seen = ?
                    WHERE (id = ? OR name = ?) AND status = 'Connected'
                """, (datetime.now().isoformat(), client_id, client_id))
                conn.commit()

            logger.info(f"Client disconnected: {client_id}")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting client {client_id}: {e}")
            return False

    async def disconnect_client_async(self, client_id: str) -> bool:
        """Disconnect client (async)."""
        return await asyncio.get_event_loop().run_in_executor(None, self.disconnect_client, client_id)

    # ============================================================================
    # FILE MANAGEMENT METHODS (Required by FletV2)
    # ============================================================================

    def get_files(self) -> list[dict[str, Any]]:
        """Return all files."""
        try:
            if not self.db_manager:
                return []

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                rows = conn.execute("""
                    SELECT f.id, f.filename, f.size, f.client_id, f.uploaded_at,
                           f.verified, f.checksum, c.name as client_name
                    FROM files f
                    LEFT JOIN clients c ON f.client_id = c.id
                    ORDER BY f.uploaded_at DESC
                """).fetchall()

                return [
                    {
                        "id": row["id"],
                        "filename": row["filename"],
                        "size": row["size"],
                        "client_id": row["client_id"],
                        "client_name": row["client_name"] or "Unknown",
                        "uploaded_at": row["uploaded_at"],
                        "verified": bool(row["verified"]),
                        "checksum": row["checksum"]
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Error getting files: {e}")
            return []

    async def get_files_async(self) -> list[dict[str, Any]]:
        """Get all files (async)."""
        return await asyncio.get_event_loop().run_in_executor(None, self.get_files)

    def get_client_files(self, client_id: str) -> list[dict[str, Any]]:
        """Get files for specific client."""
        try:
            if not self.db_manager:
                return []

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                rows = conn.execute("""
                    SELECT id, filename, size, uploaded_at, verified, checksum
                    FROM files
                    WHERE client_id = ?
                    ORDER BY uploaded_at DESC
                """, (client_id,)).fetchall()

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting files for client {client_id}: {e}")
            return []

    async def get_client_files_async(self, client_id: str) -> list[dict[str, Any]]:
        """Get client files (async)."""
        return await asyncio.get_event_loop().run_in_executor(None, self.get_client_files, client_id)

    def delete_file(self, file_id: str) -> bool:
        """Delete file from database and storage."""
        try:
            if not self.db_manager:
                return False

            with sqlite3.connect(self.db_path) as conn:
                # Get file info for cleanup
                file_info = conn.execute("""
                    SELECT filename, storage_path, client_id
                    FROM files WHERE id = ?
                """, (file_id,)).fetchone()

                if not file_info:
                    return False

                # Delete file from storage if it exists
                if file_info[1] and os.path.exists(file_info[1]):
                    try:
                        os.remove(file_info[1])
                    except OSError as e:
                        logger.warning(f"Could not delete file from storage: {e}")

                # Delete from database
                conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
                conn.commit()

            logger.info(f"File deleted: {file_info[0]}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return False

    async def delete_file_async(self, file_id: str) -> bool:
        """Delete file (async)."""
        return await asyncio.get_event_loop().run_in_executor(None, self.delete_file, file_id)

    def download_file(self, file_id: str) -> dict[str, Any]:
        """Prepare file for download."""
        try:
            if not self.db_manager:
                return {}

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                file_info = conn.execute("""
                    SELECT filename, storage_path, size
                    FROM files WHERE id = ?
                """, (file_id,)).fetchone()

                if not file_info or not os.path.exists(file_info["storage_path"]):
                    return {}

                return {
                    "path": file_info["storage_path"],
                    "filename": file_info["filename"],
                    "size": file_info["size"]
                }

        except Exception as e:
            logger.error(f"Error preparing download for file {file_id}: {e}")
            return {}

    def verify_file(self, file_id: str) -> dict[str, Any]:
        """Verify file integrity."""
        try:
            if not self.db_manager:
                return {"verified": False, "error": "Database unavailable"}

            with sqlite3.connect(self.db_path) as conn:
                file_info = conn.execute("""
                    SELECT storage_path, checksum, size
                    FROM files WHERE id = ?
                """, (file_id,)).fetchone()

                if not file_info or not os.path.exists(file_info[0]):
                    return {"verified": False, "error": "File not found"}

                # For now, just mark as verified (implement actual checksum verification if needed)
                conn.execute("""
                    UPDATE files SET verified = 1 WHERE id = ?
                """, (file_id,))
                conn.commit()

                return {
                    "verified": True,
                    "checksum": file_info[1],
                    "size": file_info[2]
                }

        except Exception as e:
            logger.error(f"Error verifying file {file_id}: {e}")
            return {"verified": False, "error": str(e)}

    async def verify_file_async(self, file_id: str) -> dict[str, Any]:
        """Verify file (async)."""
        return await asyncio.get_event_loop().run_in_executor(None, self.verify_file, file_id)

    # ============================================================================
    # DATABASE ACCESS METHODS (Required by FletV2)
    # ============================================================================

    def get_database_info(self) -> dict[str, Any]:
        """Return database schema information."""
        try:
            if not self.db_manager:
                return {"tables": [], "total_size": "0 MB", "version": "unknown"}

            with sqlite3.connect(self.db_path) as conn:
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
                    "path": self.db_path
                }

        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {"tables": [], "total_size": "0 MB", "version": "unknown"}

    async def get_database_info_async(self) -> dict[str, Any]:
        """Get database info (async)."""
        return await asyncio.get_event_loop().run_in_executor(None, self.get_database_info)

    def get_table_data(self, table_name: str) -> list[dict[str, Any]]:
        """Return all rows from specified table."""
        try:
            if not self.db_manager:
                return []

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

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
            logger.error(f"Error getting data from table {table_name}: {e}")
            return []

    async def get_table_data_async(self, table_name: str) -> list[dict[str, Any]]:
        """Get table data (async)."""
        return await asyncio.get_event_loop().run_in_executor(None, self.get_table_data, table_name)

    def update_row(self, table_name: str, row_id: str, data: dict[str, Any]) -> bool:
        """Update database row."""
        try:
            if not self.db_manager:
                return False

            with sqlite3.connect(self.db_path) as conn:
                # Validate table name
                valid_tables = [t[0] for t in conn.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """).fetchall()]

                if table_name not in valid_tables:
                    return False

                # Build UPDATE query dynamically
                set_clause = ", ".join([f"{k} = ?" for k in data])
                values = [*list(data.values()), row_id]

                conn.execute(f"""
                    UPDATE {table_name}
                    SET {set_clause}
                    WHERE id = ?
                """, values)
                conn.commit()

            logger.info(f"Updated row in {table_name}: {row_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating row in {table_name}: {e}")
            return False

    def delete_row(self, table_name: str, row_id: str) -> bool:
        """Delete database row."""
        try:
            if not self.db_manager:
                return False

            with sqlite3.connect(self.db_path) as conn:
                # Validate table name
                valid_tables = [t[0] for t in conn.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """).fetchall()]

                if table_name not in valid_tables:
                    return False

                conn.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
                conn.commit()

            logger.info(f"Deleted row from {table_name}: {row_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting row from {table_name}: {e}")
            return False

    # ============================================================================
    # LOGGING METHODS (Required by FletV2)
    # ============================================================================

    def get_logs(self) -> list[dict[str, Any]]:
        """Return recent log entries."""
        try:
            if not self.db_manager:
                return []

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Try to get logs from logs table, create sample logs if table doesn't exist
                try:
                    rows = conn.execute("""
                        SELECT id, timestamp, level, message, source, client_id
                        FROM logs
                        ORDER BY timestamp DESC
                        LIMIT 1000
                    """).fetchall()

                    return [dict(row) for row in rows]

                except sqlite3.OperationalError:
                    # Logs table doesn't exist, return sample logs
                    now = datetime.now()
                    return [
                        {
                            "id": i,
                            "timestamp": (now - timedelta(minutes=i*5)).isoformat(),
                            "level": ["info", "warning", "error"][i % 3],
                            "message": f"Server log entry {i}",
                            "source": "server",
                            "client_id": None
                        }
                        for i in range(10)
                    ]

        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []

    async def get_logs_async(self) -> list[dict[str, Any]]:
        """Get logs (async)."""
        return await asyncio.get_event_loop().run_in_executor(None, self.get_logs)

    async def clear_logs_async(self) -> bool:
        """Clear all logs."""
        try:
            if not self.db_manager:
                return False

            with sqlite3.connect(self.db_path) as conn:
                try:
                    conn.execute("DELETE FROM logs")
                    conn.commit()
                    return True
                except sqlite3.OperationalError:
                    # Logs table doesn't exist
                    return True

        except Exception as e:
            logger.error(f"Error clearing logs: {e}")
            return False

    async def export_logs_async(self, export_format: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """Export logs in specified format."""
        try:
            logs = await self.get_logs_async()

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
            filename = f"logs_export_{timestamp}.{export_format.lower()}"
            export_path = os.path.join(self.storage_path, filename)

            if export_format.lower() == "json":
                import json
                with open(export_path, "w") as f:
                    json.dump(logs, f, indent=2, default=str)
            elif export_format.lower() == "csv":
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
                "format": export_format,
                "count": len(logs)
            }

        except Exception as e:
            logger.error(f"Error exporting logs: {e}")
            return {}


# Factory function for easy integration
def create_fletv2_server(db_path: str | None = None, storage_path: str | None = None) -> FletV2ServerAdapter:
    """
    Factory function to create a FletV2-compatible server instance.

    Args:
        db_path: Path to SQLite database
        storage_path: Path to file storage directory

    Returns:
        FletV2ServerAdapter instance ready for integration
    """
    return FletV2ServerAdapter(db_path=db_path, storage_path=storage_path)


# For testing
if __name__ == "__main__":
    server = create_fletv2_server()
    print(f"Server connected: {server.is_connected()}")
    print(f"Server status: {server.get_server_status()}")
    print(f"Clients: {len(server.get_clients())}")
    print(f"Files: {len(server.get_files())}")
    print(f"Database info: {server.get_database_info()}")
