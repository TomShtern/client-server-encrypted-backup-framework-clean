# database.py
# Database operations module for the Secure File Transfer System
# Extracted from monolithic server.py for better modularity and maintainability
#
# This module provides a DatabaseManager class that handles all SQLite database
# operations for the backup server, including:
# - Client registration and persistence
# - File upload record management
# - Database schema initialization
# - Startup permission checks
# 
# Usage:
#   from database import DatabaseManager
#   db_manager = DatabaseManager()
#   db_manager.init_database()
#   db_manager.save_client_to_db(client_id, name, public_key, aes_key)

import sqlite3
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional, List, Tuple
from config import DATABASE_NAME, FILE_STORAGE_DIR
from exceptions import ServerError

# Setup module logger
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages all database operations for the backup server.
    Handles client persistence, file record management, and SQLite operations.
    """
    
    def __init__(self, db_name: str = None):
        """
        Initialize the DatabaseManager.
        
        Args:
            db_name: Optional database name override. Uses config default if None.
        """
        self.db_name = db_name or DATABASE_NAME
        logger.info(f"DatabaseManager initialized with database: {self.db_name}")
    
    def execute(self, query: str, params: tuple = (), commit: bool = False, 
                fetchone: bool = False, fetchall: bool = False) -> Any:
        """
        Helper function for executing SQLite database operations.
        Manages connection, cursor, commit, and error handling.

        Args:
            query: The SQL query string.
            params: A tuple of parameters for the query.
            commit: True if the transaction should be committed.
            fetchone: True to fetch a single row.
            fetchall: True to fetch all rows.

        Returns:
            Query result (row, list of rows, or cursor) or None on failure for non-SELECTs.

        Raises:
            ServerError: If a database read error occurs that prevents server operation.
        """
        try:
            # Using a timeout for the connection can prevent indefinite blocking if the DB is locked.
            # `check_same_thread=False` is generally needed if DB connection is shared across threads,
            # but here, each call creates a new connection, which is safer for SQLite threading.
            with sqlite3.connect(self.db_name, timeout=10.0) as conn:  # `timeout` is for busy_timeout
                cursor = conn.cursor()
                cursor.execute(query, params)
                if commit:
                    conn.commit()
                if fetchone:
                    return cursor.fetchone()
                if fetchall:
                    return cursor.fetchall()
                return cursor  # For operations where cursor properties (e.g., lastrowid) are needed
        except sqlite3.OperationalError as e:  # Specific error for "database is locked", "no such table" etc.
            logger.error(f"Database operational error: {e} | Query: {query[:150]}... | Params: {params}")
            # Depending on severity, re-raise or return specific error indicator
            if "locked" in str(e).lower():
                logger.warning("Database was locked during operation. This might indicate contention or a long-running transaction.")
            # If it's a critical read operation (e.g., loading clients), we might need to halt.
            if not commit and (fetchone or fetchall):  # This was a read operation
                raise ServerError(f"Critical database read error: {e}") from e
            return None  # Indicate failure for write operations
        except sqlite3.Error as e:  # Catch other, more general SQLite errors
            logger.error(f"General database error: {e} | Query: {query[:150]}... | Params: {params}")
            if not commit and (fetchone or fetchall):
                raise ServerError(f"General database read error: {e}") from e
            return None

    def init_database(self):
        """Initializes the database schema if tables do not exist."""
        logger.info(f"Initializing database schema in '{self.db_name}' if needed...")
        
        # Client Table: Stores information about registered clients.
        # LastSeen is stored as ISO8601 UTC text for portability and readability.
        # AESKey is per spec, though session-based keys are usually not persisted this way.
        self.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                ID BLOB(16) PRIMARY KEY,
                Name VARCHAR(255) UNIQUE NOT NULL,
                PublicKey BLOB(160),
                LastSeen TEXT NOT NULL, 
                AESKey BLOB(32) 
            )
        ''', commit=True)
        
        # Files Table: Stores information about files backed up by clients.
        # ON DELETE CASCADE ensures that if a client is deleted, their file records are also removed.
        self.execute('''
            CREATE TABLE IF NOT EXISTS files (
                ID BLOB(16) NOT NULL, 
                FileName VARCHAR(255) NOT NULL,
                PathName VARCHAR(255) NOT NULL, 
                Verified BOOLEAN DEFAULT 0,
                PRIMARY KEY (ID, FileName), 
                FOREIGN KEY (ID) REFERENCES clients(ID) ON DELETE CASCADE
            )
        ''', commit=True)
        
        logger.info("Database schema initialization complete.")

    def load_clients_from_db(self) -> List[Tuple[bytes, str, Optional[bytes], str]]:
        """
        Loads existing client data from the database.
        
        Returns:
            List of tuples containing (client_id, name, public_key_bytes, last_seen_iso_utc)
            
        Raises:
            ServerError: If a critical database read error occurs.
        """
        logger.info("Loading existing clients from database...")
        try:
            rows = self.execute("SELECT ID, Name, PublicKey, LastSeen FROM clients", fetchall=True)
            if rows:
                logger.info(f"Successfully loaded {len(rows)} client(s) from database.")
                return rows
            else:
                logger.info("No existing clients found in database.")
                return []
        except ServerError as e:  # Raised by execute on critical read failure
            logger.critical(f"CRITICAL FAILURE: Could not load client data from database: {e}")
            raise

    def save_client_to_db(self, client_id: bytes, name: str, public_key_bytes: Optional[bytes], aes_key: Optional[bytes]):
        """
        Saves or updates a client's information in the database.
        
        Args:
            client_id: The unique UUID (bytes) of the client.
            name: The username of the client.
            public_key_bytes: The client's RSA public key in X.509 format.
            aes_key: The client's current AES session key.
        """
        # Convert monotonic client.last_seen to a wall-clock datetime for storage.
        # For the DB's LastSeen, always use current UTC wall-clock time to reflect this update event.
        current_wall_time_utc_iso = datetime.now(timezone.utc).isoformat(timespec='seconds') + "Z"
        
        self.execute('''
            INSERT OR REPLACE INTO clients (ID, Name, PublicKey, LastSeen, AESKey) 
            VALUES (?, ?, ?, ?, ?)
        ''', (client_id, name, public_key_bytes, current_wall_time_utc_iso, aes_key), commit=True)
        
        logger.debug(f"Client '{name}' data saved/updated in database (Recorded LastSeen: {current_wall_time_utc_iso}).")

    def save_file_info_to_db(self, client_id: bytes, file_name: str, path_name: str, verified: bool):
        """
        Saves or updates file information in the database.
        
        Args:
            client_id: The unique UUID (bytes) of the client who uploaded the file.
            file_name: The original filename.
            path_name: The stored file path (relative or absolute).
            verified: Whether the file has been verified (checksum validated).
        """
        # Ensure path_name is stored consistently (e.g., relative to FILE_STORAGE_DIR or absolute)
        # Current implementation assumes path_name is the final, usable path.
        self.execute('''
            INSERT OR REPLACE INTO files (ID, FileName, PathName, Verified) 
            VALUES (?, ?, ?, ?)
        ''', (client_id, file_name, path_name, verified), commit=True)
        
        logger.debug(f"File info for '{file_name}' (Client ID: {client_id.hex()}) saved/updated in database. Verified status: {verified}.")

    def get_client_by_id(self, client_id: bytes) -> Optional[Tuple[bytes, str, Optional[bytes], str, Optional[bytes]]]:
        """
        Retrieves a client record by ID.
        
        Args:
            client_id: The unique UUID (bytes) of the client.
            
        Returns:
            Tuple containing (client_id, name, public_key_bytes, last_seen_iso_utc, aes_key) or None if not found.
        """
        try:
            result = self.execute("SELECT ID, Name, PublicKey, LastSeen, AESKey FROM clients WHERE ID = ?", 
                                (client_id,), fetchone=True)
            return result
        except ServerError as e:
            logger.error(f"Error retrieving client by ID {client_id.hex()}: {e}")
            return None

    def get_client_by_name(self, name: str) -> Optional[Tuple[bytes, str, Optional[bytes], str, Optional[bytes]]]:
        """
        Retrieves a client record by name.
        
        Args:
            name: The username of the client.
            
        Returns:
            Tuple containing (client_id, name, public_key_bytes, last_seen_iso_utc, aes_key) or None if not found.
        """
        try:
            result = self.execute("SELECT ID, Name, PublicKey, LastSeen, AESKey FROM clients WHERE Name = ?", 
                                (name,), fetchone=True)
            return result
        except ServerError as e:
            logger.error(f"Error retrieving client by name '{name}': {e}")
            return None

    def get_client_files(self, client_id: bytes) -> List[Tuple[str, str, bool]]:
        """
        Retrieves all files for a specific client.
        
        Args:
            client_id: The unique UUID (bytes) of the client.
            
        Returns:
            List of tuples containing (file_name, path_name, verified) for each file.
        """
        try:
            results = self.execute("SELECT FileName, PathName, Verified FROM files WHERE ID = ?", 
                                 (client_id,), fetchall=True)
            return results or []
        except ServerError as e:
            logger.error(f"Error retrieving files for client {client_id.hex()}: {e}")
            return []

    def delete_client(self, client_id: bytes) -> bool:
        """
        Deletes a client and all associated file records.
        
        Args:
            client_id: The unique UUID (bytes) of the client to delete.
            
        Returns:
            True if the client was deleted, False if an error occurred.
        """
        try:
            cursor = self.execute("DELETE FROM clients WHERE ID = ?", (client_id,), commit=True)
            if cursor and cursor.rowcount > 0:
                logger.info(f"Successfully deleted client {client_id.hex()} and associated files.")
                return True
            else:
                logger.warning(f"No client found with ID {client_id.hex()} to delete.")
                return False
        except Exception as e:
            logger.error(f"Error deleting client {client_id.hex()}: {e}")
            return False

    def delete_file_record(self, client_id: bytes, file_name: str) -> bool:
        """
        Deletes a specific file record for a client.
        
        Args:
            client_id: The unique UUID (bytes) of the client.
            file_name: The filename to delete from records.
            
        Returns:
            True if the file record was deleted, False if an error occurred.
        """
        try:
            cursor = self.execute("DELETE FROM files WHERE ID = ? AND FileName = ?", 
                                (client_id, file_name), commit=True)
            if cursor and cursor.rowcount > 0:
                logger.info(f"Successfully deleted file record '{file_name}' for client {client_id.hex()}.")
                return True
            else:
                logger.warning(f"No file record found for '{file_name}' and client {client_id.hex()}.")
                return False
        except Exception as e:
            logger.error(f"Error deleting file record '{file_name}' for client {client_id.hex()}: {e}")
            return False

    def get_database_stats(self) -> dict:
        """
        Retrieves basic statistics about the database.
        
        Returns:
            Dictionary containing database statistics.
        """
        stats = {
            'total_clients': 0,
            'total_files': 0,
            'verified_files': 0,
            'database_size_bytes': 0
        }
        
        try:
            # Count clients
            result = self.execute("SELECT COUNT(*) FROM clients", fetchone=True)
            if result:
                stats['total_clients'] = result[0]
            
            # Count files
            result = self.execute("SELECT COUNT(*) FROM files", fetchone=True)
            if result:
                stats['total_files'] = result[0]
            
            # Count verified files
            result = self.execute("SELECT COUNT(*) FROM files WHERE Verified = 1", fetchone=True)
            if result:
                stats['verified_files'] = result[0]
            
            # Get database file size
            if os.path.exists(self.db_name):
                stats['database_size_bytes'] = os.path.getsize(self.db_name)
                
        except Exception as e:
            logger.error(f"Error retrieving database statistics: {e}")
        
        return stats

    def check_startup_permissions(self):
        """
        Performs critical permission checks before the server starts.
        
        Raises:
            SystemExit: If critical permissions are not available.
        """
        logger.info("Performing database startup checks...")
        
        # Check write permissions for file storage directory
        if not os.access(FILE_STORAGE_DIR, os.W_OK):
            logger.critical(f"Fatal: No write permission for file storage directory: '{os.path.abspath(FILE_STORAGE_DIR)}'.")
            raise SystemExit(f"Startup failed: No write access to '{FILE_STORAGE_DIR}'.")

        # Check write permissions for the directory where the database file resides
        db_dir = os.path.dirname(os.path.abspath(self.db_name))
        if not os.access(db_dir or '.', os.W_OK):  # Use current dir if DATABASE_NAME is relative with no path
            logger.critical(f"Fatal: No write permission for database directory: '{db_dir or os.path.abspath('.')}'.")
            raise SystemExit(f"Startup failed: No write access to database directory '{db_dir}'.")
        
        logger.info("Database startup permission checks passed.")

    def ensure_storage_dir(self):
        """
        Ensures that the file storage directory exists.
        
        Raises:
            OSError: If the directory cannot be created or accessed.
        """
        try:
            os.makedirs(FILE_STORAGE_DIR, exist_ok=True)  # exist_ok=True means no error if dir already exists
            logger.info(f"File storage directory is set to: '{os.path.abspath(FILE_STORAGE_DIR)}'")
        except OSError as e:
            logger.critical(f"Fatal: Could not create or access file storage directory '{FILE_STORAGE_DIR}': {e}")
            raise  # This is a critical failure, server cannot operate


# Module-level convenience functions for backward compatibility
def get_database_manager(db_name: str = None) -> DatabaseManager:
    """
    Factory function to get a DatabaseManager instance.
    
    Args:
        db_name: Optional database name override.
        
    Returns:
        DatabaseManager instance.
    """
    return DatabaseManager(db_name)


def init_database(db_name: str = None):
    """
    Initialize the database schema.
    
    Args:
        db_name: Optional database name override.
    """
    db_manager = DatabaseManager(db_name)
    db_manager.init_database()


def check_database_permissions():
    """Check database and storage directory permissions."""
    db_manager = DatabaseManager()
    db_manager.check_startup_permissions()
    db_manager.ensure_storage_dir()