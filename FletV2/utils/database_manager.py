#!/usr/bin/env python3
"""
FletV2 Database Manager
Handles database operations for FletV2 using MockaBase as a drop-in replacement
"""

import os
import sqlite3
import sys
from typing import Any

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

from FletV2.utils.debug_setup import get_logger

logger = get_logger(__name__)


class FletDatabaseManager:
    """
    Database manager for FletV2 that works with MockaBase as a drop-in replacement.
    """

    def __init__(self, database_path: str = "MockaBase.db"):
        """Initialize database manager with database path."""
        self.database_path = database_path
        self.connection = None
        logger.info(f"Initialized FletDatabaseManager with database: {database_path}")

    def connect(self) -> bool:
        """Connect to the database."""
        try:
            if os.path.exists(self.database_path):
                self.connection = sqlite3.connect(self.database_path)
                self.connection.row_factory = sqlite3.Row  # Enable column access by name
                logger.info(f"Connected to database: {self.database_path}")
                return True
            else:
                logger.warning(f"Database file not found: {self.database_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from database")

    def get_table_names(self) -> list[str]:
        """Get list of table names in the database."""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            return tables
        except Exception as e:
            logger.error(f"Failed to get table names: {e}")
            return []

    def get_table_data(self, table_name: str) -> dict[str, Any]:
        """Get table data including columns and rows."""
        if not self.connection:
            return {"columns": [], "rows": []}

        try:
            cursor = self.connection.cursor()

            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            columns = [row[1] for row in columns_info]  # Column names

            # Get row data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = [dict(row) for row in cursor.fetchall()]

            # Convert binary data to hex strings for display
            processed_rows = []
            for row in rows:
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, bytes):
                        processed_row[key] = value.hex() if value else ""
                    else:
                        processed_row[key] = value
                processed_rows.append(processed_row)

            return {
                "columns": columns,
                "rows": processed_rows
            }
        except Exception as e:
            logger.error(f"Failed to get table data for {table_name}: {e}")
            return {"columns": [], "rows": []}

    def get_database_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        if not self.connection:
            return {}

        try:
            cursor = self.connection.cursor()

            # Get table names
            tables = self.get_table_names()

            # Get record counts for each table
            total_records = 0
            table_stats = {}

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_stats[table] = count
                total_records += count

            # Get database size
            if os.path.exists(self.database_path):
                size_bytes = os.path.getsize(self.database_path)
                size_mb = size_bytes / (1024 * 1024)
                size_str = f"{size_mb:.1f} MB"
            else:
                size_str = "Unknown"

            return {
                "status": "Connected",
                "tables": len(tables),
                "records": total_records,
                "size": size_str,
                "table_details": table_stats
            }
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

    def get_clients(self) -> list[dict[str, Any]]:
        """Get all clients from the database."""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT ID, Name, LastSeen,
                       CASE WHEN PublicKey IS NOT NULL THEN 1 ELSE 0 END as HasPublicKey,
                       CASE WHEN AESKey IS NOT NULL THEN 1 ELSE 0 END as HasAESKey
                FROM clients
                ORDER BY LastSeen DESC
            """)

            clients = []
            for row in cursor.fetchall():
                client = {
                    "id": row["ID"].hex() if isinstance(row["ID"], bytes) else row["ID"],
                    "name": row["Name"],
                    "last_seen": row["LastSeen"],
                    "has_public_key": bool(row["HasPublicKey"]),
                    "has_aes_key": bool(row["HasAESKey"])
                }
                clients.append(client)

            return clients
        except Exception as e:
            logger.error(f"Failed to get clients: {e}")
            return []

    def get_files(self) -> list[dict[str, Any]]:
        """Get all files from the database."""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT f.ID, f.FileName, f.PathName, f.Verified, f.FileSize,
                       f.ModificationDate, f.CRC, f.ClientID, c.Name as ClientName
                FROM files f
                LEFT JOIN clients c ON f.ClientID = c.ID
                ORDER BY f.ModificationDate DESC
            """)

            files = []
            for row in cursor.fetchall():
                file = {
                    "id": row["ID"].hex() if isinstance(row["ID"], bytes) else row["ID"],
                    "filename": row["FileName"],
                    "pathname": row["PathName"],
                    "verified": bool(row["Verified"]),
                    "filesize": row["FileSize"],
                    "modification_date": row["ModificationDate"],
                    "crc": row["CRC"],
                    "client_id": row["ClientID"].hex() if isinstance(row["ClientID"], bytes) else row["ClientID"],
                    "client_name": row["ClientName"] or "Unknown"
                }
                files.append(file)

            return files
        except Exception as e:
            logger.error(f"Failed to get files: {e}")
            return []

    def update_row(self, table_name: str, row_id: str, update_data: dict[str, Any]) -> bool:
        """Update a row in a table."""
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()

            # Build update query
            set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(bytes.fromhex(row_id) if isinstance(row_id, str) else row_id)

            query = f"UPDATE {table_name} SET {set_clause} WHERE ID = ?"
            cursor.execute(query, values)

            self.connection.commit()
            logger.info(f"Updated row in {table_name} with ID {row_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update row in {table_name}: {e}")
            return False

    def delete_row(self, table_name: str, row_id: str) -> bool:
        """Delete a row from a table."""
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()
            query = f"DELETE FROM {table_name} WHERE ID = ?"
            cursor.execute(query, (bytes.fromhex(row_id) if isinstance(row_id, str) else row_id,))

            self.connection.commit()
            logger.info(f"Deleted row from {table_name} with ID {row_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete row from {table_name}: {e}")
            return False


def create_database_manager(database_path: str = "MockaBase.db") -> FletDatabaseManager | None:
    """
    Factory function to create a database manager.

    Args:
        database_path (str): Path to the database file

    Returns:
        FletDatabaseManager: Instance of database manager
    """
    try:
        db_manager = FletDatabaseManager(database_path)
        return db_manager
    except Exception as e:
        logger.error(f"Error creating FletDatabaseManager: {e}")
        return None
