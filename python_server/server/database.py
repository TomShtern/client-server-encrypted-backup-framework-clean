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
import queue
import threading
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, List, Tuple, Dict, Union
try:
    from .config import DATABASE_NAME, FILE_STORAGE_DIR
    from .exceptions import ServerError
except ImportError:
    # Fallback for direct execution
    DATABASE_NAME = "defensive.db"
    FILE_STORAGE_DIR = "received_files"
    class ServerError(Exception):
        pass

# Setup module logger
logger = logging.getLogger(__name__)


class DatabaseConnectionPool:
    """
    Connection pool for SQLite database to improve performance and reduce overhead.
    """
    
    def __init__(self, db_name: str, pool_size: int = 5, timeout: float = 30.0):
        self.db_name = db_name
        self.pool_size = pool_size
        self.timeout = timeout
        self.pool = queue.Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._create_connections()
    
    def _create_connections(self):
        """Create initial pool of database connections."""
        for _ in range(self.pool_size):
            conn = sqlite3.connect(
                self.db_name, 
                timeout=10.0,
                check_same_thread=False  # Allow connection sharing across threads
            )
            # Configure database for better performance while maintaining compatibility
            try:
                conn.execute("PRAGMA journal_mode=WAL")
            except sqlite3.OperationalError:
                # WAL mode not supported or database locked, use default
                logger.warning("WAL mode not available, using default journaling")
            conn.execute("PRAGMA synchronous=NORMAL")  # Balance safety vs performance
            conn.execute("PRAGMA cache_size=10000")  # Increase cache size
            conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
            self.pool.put(conn)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool."""
        try:
            return self.pool.get(timeout=self.timeout)
        except queue.Empty:
            logger.warning("Connection pool exhausted, creating new connection")
            conn = sqlite3.connect(self.db_name, timeout=10.0, check_same_thread=False)
            try:
                conn.execute("PRAGMA journal_mode=WAL")
            except sqlite3.OperationalError:
                pass  # WAL mode not available
            conn.execute("PRAGMA synchronous=NORMAL")
            return conn
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool."""
        try:
            # Ensure connection is still valid
            conn.execute("SELECT 1")
            self.pool.put_nowait(conn)
        except (sqlite3.Error, queue.Full):
            # Connection is invalid or pool is full, close it
            try:
                conn.close()
            except:
                pass
    
    def close_all(self):
        """Close all connections in the pool."""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except (queue.Empty, sqlite3.Error):
                break


class DatabaseManager:
    """
    Manages all database operations for the backup server.
    Handles client persistence, file record management, and SQLite operations.
    """
    
    def __init__(self, db_name: Optional[str] = None, use_pool: bool = True):
        """
        Initialize the DatabaseManager.
        
        Args:
            db_name: Optional database name override. Uses config default if None.
            use_pool: Whether to use connection pooling for better performance.
        """
        self.db_name = db_name or DATABASE_NAME
        self.use_pool = use_pool
        self.connection_pool = None
        
        if use_pool:
            try:
                self.connection_pool = DatabaseConnectionPool(self.db_name)
                logger.info(f"DatabaseManager initialized with connection pool: {self.db_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize connection pool: {e}, falling back to direct connections")
                self.use_pool = False
        
        if not self.use_pool:
            logger.info(f"DatabaseManager initialized with direct connections: {self.db_name}")
    
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
            if self.use_pool and self.connection_pool:
                # Use connection pool for better performance
                conn = self.connection_pool.get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    if commit:
                        conn.commit()
                    if fetchone:
                        result = cursor.fetchone()
                        self.connection_pool.return_connection(conn)
                        return result
                    if fetchall:
                        result = cursor.fetchall()
                        self.connection_pool.return_connection(conn)
                        return result
                    # For cursor operations, we need to keep connection until cursor is used
                    # This is a design limitation - cursor operations should be avoided with pooling
                    result = cursor.lastrowid if hasattr(cursor, 'lastrowid') else None
                    self.connection_pool.return_connection(conn)
                    return result
                except Exception as e:
                    # Don't return potentially corrupted connection to pool
                    try:
                        conn.close()
                    except:
                        pass
                    raise e
            else:
                # Fallback to direct connection
                with sqlite3.connect(self.db_name, timeout=10.0) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    if commit:
                        conn.commit()
                    if fetchone:
                        return cursor.fetchone()
                    if fetchall:
                        return cursor.fetchall()
                    return cursor
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
        
        # First ensure basic schema exists, then apply migrations
        self._create_basic_schema()
        self._apply_database_migrations()
        
        logger.info("Database schema initialization complete.")
    
    def _create_basic_schema(self):
        """Create the basic schema tables if they don't exist."""
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
                ID BLOB(16) PRIMARY KEY,
                FileName VARCHAR(255) NOT NULL,
                PathName VARCHAR(255) NOT NULL,
                Verified BOOLEAN DEFAULT 0,
                FileSize INTEGER,
                ModificationDate TEXT,
                CRC INTEGER,
                ClientID BLOB(16) NOT NULL,
                FOREIGN KEY (ClientID) REFERENCES clients(ID) ON DELETE CASCADE
            )
        ''', commit=True)
        
        # Add missing columns to existing tables
        self._add_missing_columns()
    
    def _add_missing_columns(self):
        """Add missing columns to existing tables for backward compatibility."""
        # Add FileSize and ModificationDate to older tables if they don't exist
        try:
            self.execute("SELECT FileSize FROM files LIMIT 1", fetchone=True)
        except (sqlite3.OperationalError, ServerError):
            logger.info("Adding FileSize column to files table")
            self.execute("ALTER TABLE files ADD COLUMN FileSize INTEGER", commit=True)
        try:
            self.execute("SELECT ModificationDate FROM files LIMIT 1", fetchone=True)
        except (sqlite3.OperationalError, ServerError):
            logger.info("Adding ModificationDate column to files table")
            self.execute("ALTER TABLE files ADD COLUMN ModificationDate TEXT", commit=True)
        try:
            self.execute("SELECT CRC FROM files LIMIT 1", fetchone=True)
        except (sqlite3.OperationalError, ServerError):
            logger.info("Adding CRC column to files table")
            self.execute("ALTER TABLE files ADD COLUMN CRC INTEGER", commit=True)

        # Add ClientID column for proper foreign key relationship
        try:
            self.execute("SELECT ClientID FROM files LIMIT 1", fetchone=True)
        except (sqlite3.OperationalError, ServerError):
            logger.info("Adding ClientID column to files table and migrating data")
            self.execute("ALTER TABLE files ADD COLUMN ClientID BLOB(16)", commit=True)
            # Migrate existing data: move ID to ClientID and generate new unique IDs
            self._migrate_files_to_clientid_schema()
    
    def _apply_database_migrations(self):
        """Apply database migrations to enhance functionality."""
        try:
            from .database_migrations import DatabaseMigrationManager
            migration_manager = DatabaseMigrationManager(self.db_name)
            
            pending = migration_manager.get_pending_migrations()
            if pending:
                logger.info(f"Applying {len(pending)} database migrations...")
                success = migration_manager.migrate_to_latest()
                if success:
                    logger.info("Database migrations applied successfully")
                else:
                    logger.warning("Some database migrations failed - system will continue with existing schema")
            else:
                logger.debug("No pending database migrations")
        except ImportError:
            logger.debug("Migration system not available - skipping migrations")
        except Exception as e:
            logger.warning(f"Migration system error: {e} - continuing with basic schema")

    def _migrate_files_to_clientid_schema(self):
        """Migrate existing files table to use ClientID foreign key"""
        import uuid
        try:
            # Get all existing files
            existing_files = self.execute("SELECT ID, FileName FROM files WHERE ClientID IS NULL", fetchall=True)

            for file_id, filename in existing_files:
                # The current ID is actually the client ID, so move it to ClientID
                new_file_id = uuid.uuid4().bytes  # Generate new unique file ID

                self.execute("""
                    UPDATE files
                    SET ClientID = ?, ID = ?
                    WHERE ID = ? AND FileName = ? AND ClientID IS NULL
                """, (file_id, new_file_id, file_id, filename), commit=True)

            logger.info(f"Migrated {len(existing_files)} file records to use ClientID schema")

        except Exception as e:
            logger.error(f"Failed to migrate files to ClientID schema: {e}")
            raise

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

    def save_file_info_to_db(self, client_id: bytes, file_name: str, path_name: str, verified: bool, file_size: int, mod_date: str, crc: Optional[int] = None):
        """
        Saves or updates file information in the database.

        Args:
            client_id: The unique UUID (bytes) of the client who uploaded the file.
            file_name: The original filename.
            path_name: The stored file path (relative or absolute).
            verified: Whether the file has been verified (checksum validated).
            file_size: The size of the file in bytes.
            mod_date: The modification date of the file as an ISO 8601 string.
            crc: The CRC32 checksum of the file.
        """
        import uuid

        # Generate unique file ID
        file_id = uuid.uuid4().bytes

        # Ensure path_name is stored consistently (e.g., relative to FILE_STORAGE_DIR or absolute)
        # Current implementation assumes path_name is the final, usable path.
        if crc is not None:
            self.execute('''
                INSERT OR REPLACE INTO files (ID, FileName, PathName, Verified, FileSize, ModificationDate, CRC, ClientID)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (file_id, file_name, path_name, verified, file_size, mod_date, crc, client_id), commit=True)
        else:
            self.execute('''
                INSERT OR REPLACE INTO files (ID, FileName, PathName, Verified, FileSize, ModificationDate, ClientID)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (file_id, file_name, path_name, verified, file_size, mod_date, client_id), commit=True)
        
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

    def delete_file(self, client_id: str, filename: str) -> bool:
        """Deletes a file from the filesystem and the database."""
        try:
            # First, get the file path from the database
            file_info = self.execute("SELECT PathName FROM files WHERE ID = ? AND FileName = ?", 
                                    (bytes.fromhex(client_id), filename), fetchone=True)
            if not file_info:
                logger.warning(f"File '{filename}' not found in database for client {client_id}")
                return False

            file_path = file_info[0]

            # Delete the file from the filesystem
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file from filesystem: {file_path}")
            else:
                logger.warning(f"File not found on filesystem for deletion: {file_path}")

            # Delete the file record from the database
            return self.delete_file_record(bytes.fromhex(client_id), filename)

        except Exception as e:
            logger.error(f"Error deleting file '{filename}' for client {client_id}: {e}")
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

    def get_all_clients(self) -> list:
        """Retrieves all clients from the database."""
        try:
            clients = self.execute("SELECT ID, Name, LastSeen FROM clients", fetchall=True)
            if clients:
                return [{
                    'id': row[0].hex(),
                    'name': row[1],
                    'last_seen': row[2]
                } for row in clients]
            return []
        except Exception as e:
            logger.error(f"Database error while getting all clients: {e}")
            return []

    def get_files_for_client(self, client_id: str) -> list:
        """Retrieves all files for a given client."""
        try:
            files = self.execute("SELECT FileName, PathName, Verified FROM files WHERE ClientID=?",
                               (bytes.fromhex(client_id),), fetchall=True)
            if files:
                return [{
                    'filename': row[0],
                    'path': row[1],
                    'verified': bool(row[2])
                } for row in files]
            return []
        except Exception as e:
            logger.error(f"Database error while getting files for client {client_id}: {e}")
            return []

    def get_all_files(self) -> list:
        """Retrieves all files from the database."""
        try:
            files = self.execute("""
                SELECT f.FileName, f.PathName, f.Verified, c.Name, f.FileSize, f.ModificationDate
                FROM files f JOIN clients c ON f.ClientID = c.ID
            """, fetchall=True)
            if files:
                return [{
                    'filename': row[0],
                    'path': row[1],
                    'verified': bool(row[2]),
                    'client': row[3],
                    'size': row[4],
                    'date': row[5]
                } for row in files]
            return []
        except Exception as e:
            logger.error(f"Database error while getting all files: {e}")
            return []

    def get_file_info(self, client_id: str, filename: str) -> Optional[dict]:
        """Retrieves all information for a single file."""
        try:
            row = self.execute("""
                SELECT f.FileName, f.PathName, f.Verified, c.Name, f.FileSize, f.ModificationDate, f.CRC
                FROM files f JOIN clients c ON f.ClientID = c.ID
                WHERE f.ClientID = ? AND f.FileName = ?
            """, (bytes.fromhex(client_id), filename), fetchone=True)
            if row:
                return {
                    'filename': row[0],
                    'path': row[1],
                    'verified': bool(row[2]),
                    'client': row[3],
                    'size': row[4],
                    'date': row[5],
                    'crc': row[6]
                }
            return None
        except Exception as e:
            logger.error(f"Database error while getting file info for {client_id}/{filename}: {e}")
            return None

    def get_total_clients_count(self) -> int:
        """Returns the total number of registered clients."""
        try:
            result = self.execute("SELECT COUNT(*) FROM clients", fetchone=True)
            if result:
                return result[0] if result[0] is not None else 0
            return 0
        except Exception as e:
            logger.error(f"Database error while getting total client count: {e}")
            return 0

    def get_total_bytes_transferred(self) -> int:
        """Returns the total number of bytes transferred."""
        try:
            result = self.execute("SELECT SUM(FileSize) FROM files WHERE Verified = 1", fetchone=True)
            if result:
                return result[0] if result[0] is not None else 0
            return 0
        except Exception as e:
            logger.error(f"Database error while getting total bytes transferred: {e}")
            return 0

    # Enhanced Database Methods
    
    def execute_many(self, query: str, param_list: List[tuple], commit: bool = True) -> bool:
        """
        Execute a query multiple times with different parameters for bulk operations.
        
        Args:
            query: The SQL query string.
            param_list: List of parameter tuples.
            commit: Whether to commit the transaction.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            if self.use_pool and self.connection_pool:
                conn = self.connection_pool.get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.executemany(query, param_list)
                    if commit:
                        conn.commit()
                    self.connection_pool.return_connection(conn)
                    return True
                except Exception as e:
                    try:
                        conn.close()
                    except:
                        pass
                    raise e
            else:
                with sqlite3.connect(self.db_name, timeout=10.0) as conn:
                    cursor = conn.cursor()
                    cursor.executemany(query, param_list)
                    if commit:
                        conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Bulk database operation failed: {e}")
            return False
    
    def search_files_advanced(self, search_term: str = "", file_type: str = "", 
                             client_name: str = "", date_from: str = "", 
                             date_to: str = "", min_size: int = 0, 
                             max_size: int = 0, verified_only: bool = False) -> List[Dict]:
        """
        Advanced file search with multiple filters.
        
        Args:
            search_term: Search in filename or path
            file_type: File extension to filter by
            client_name: Client name to filter by
            date_from: Start date (ISO format)
            date_to: End date (ISO format)
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes
            verified_only: Only return verified files
            
        Returns:
            List of file dictionaries matching the criteria
        """
        conditions = ["1=1"]  # Base condition
        params = []
        
        if search_term:
            conditions.append("(f.FileName LIKE ? OR f.PathName LIKE ?)")
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if file_type:
            # Try to match FileExtension if available, otherwise extract from filename
            conditions.append("(f.FileExtension = ? OR f.FileName LIKE ?)")
            params.extend([file_type, f"%.{file_type}"])
        
        if client_name:
            conditions.append("c.Name LIKE ?")
            params.append(f"%{client_name}%")
        
        if date_from:
            conditions.append("f.ModificationDate >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("f.ModificationDate <= ?")
            params.append(date_to)
        
        if min_size > 0:
            conditions.append("f.FileSize >= ?")
            params.append(min_size)
        
        if max_size > 0:
            conditions.append("f.FileSize <= ?")
            params.append(max_size)
        
        if verified_only:
            conditions.append("f.Verified = 1")
        
        # Build SELECT clause dynamically based on available columns
        base_columns = "f.FileName, f.PathName, f.FileSize, f.ModificationDate, f.Verified, f.CRC, c.Name as ClientName"
        extended_columns = ""
        
        # Check if extended columns exist (from migrations)
        try:
            self.execute("SELECT FileCategory FROM files LIMIT 1", fetchone=True)
            extended_columns = ", f.FileCategory, f.MimeType, f.FileExtension, f.TransferDuration, f.TransferSpeed"
        except (sqlite3.OperationalError, ServerError):
            # Extended columns don't exist yet
            pass
        
        query = f"""
            SELECT {base_columns}{extended_columns}
            FROM files f 
            JOIN clients c ON f.ClientID = c.ID
            WHERE {' AND '.join(conditions)}
            ORDER BY f.ModificationDate DESC
            LIMIT 1000
        """
        
        try:
            results = self.execute(query, tuple(params), fetchall=True)
            if results:
                return [{
                    'filename': row[0],
                    'path': row[1],
                    'size': row[2],
                    'date': row[3],
                    'verified': bool(row[4]),
                    'crc': row[5],
                    'client': row[6],
                    'category': row[7] if len(row) > 7 else None,
                    'mime_type': row[8] if len(row) > 8 else None,
                    'extension': row[9] if len(row) > 9 else None,
                    'transfer_duration': row[10] if len(row) > 10 else None,
                    'transfer_speed': row[11] if len(row) > 11 else None
                } for row in results]
            return []
        except Exception as e:
            logger.error(f"Advanced file search failed: {e}")
            return []
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive storage and usage statistics."""
        stats = {
            'database_info': {},
            'storage_info': {},
            'client_stats': {},
            'file_stats': {},
            'performance_info': {}
        }
        
        try:
            # Database information
            stats['database_info'] = {
                'file_path': os.path.abspath(self.db_name),
                'file_size_mb': round(os.path.getsize(self.db_name) / (1024 * 1024), 2) if os.path.exists(self.db_name) else 0,
                'connection_pool_enabled': self.use_pool,
                'pool_size': self.connection_pool.pool_size if self.connection_pool else 0
            }
            
            # Storage directory information
            if os.path.exists(FILE_STORAGE_DIR):
                try:
                    total_size = sum(
                        os.path.getsize(os.path.join(FILE_STORAGE_DIR, f))
                        for f in os.listdir(FILE_STORAGE_DIR)
                        if os.path.isfile(os.path.join(FILE_STORAGE_DIR, f))
                    )
                except (OSError, PermissionError) as e:
                    logger.warning(f"Could not calculate storage directory size: {e}")
                    total_size = 0
                stats['storage_info'] = {
                    'directory': os.path.abspath(FILE_STORAGE_DIR),
                    'total_files': len([f for f in os.listdir(FILE_STORAGE_DIR) if os.path.isfile(os.path.join(FILE_STORAGE_DIR, f))]),
                    'total_size_mb': round(total_size / (1024 * 1024), 2)
                }
            
            # Client statistics
            client_stats = self.execute("""
                SELECT 
                    COUNT(*) as total_clients,
                    COUNT(CASE WHEN PublicKey IS NOT NULL THEN 1 END) as clients_with_keys,
                    AVG(CASE WHEN LastSeen IS NOT NULL THEN julianday('now') - julianday(LastSeen) END) as avg_days_since_seen
                FROM clients
            """, fetchone=True)
            
            if client_stats:
                stats['client_stats'] = {
                    'total_clients': client_stats[0],
                    'clients_with_keys': client_stats[1],
                    'average_days_since_seen': round(client_stats[2] or 0, 1)
                }
            
            # File statistics
            file_stats = self.execute("""
                SELECT 
                    COUNT(*) as total_files,
                    COUNT(CASE WHEN Verified = 1 THEN 1 END) as verified_files,
                    AVG(FileSize) as avg_file_size,
                    SUM(FileSize) as total_size,
                    MIN(FileSize) as min_size,
                    MAX(FileSize) as max_size
                FROM files
                WHERE FileSize IS NOT NULL
            """, fetchone=True)
            
            if file_stats:
                stats['file_stats'] = {
                    'total_files': file_stats[0],
                    'verified_files': file_stats[1],
                    'verification_rate': round((file_stats[1] / file_stats[0] * 100) if file_stats[0] > 0 else 0, 1),
                    'average_file_size_mb': round((file_stats[2] or 0) / (1024 * 1024), 2),
                    'total_size_gb': round((file_stats[3] or 0) / (1024 * 1024 * 1024), 2),
                    'min_file_size_kb': round((file_stats[4] or 0) / 1024, 2),
                    'max_file_size_mb': round((file_stats[5] or 0) / (1024 * 1024), 2)
                }
            
            # Performance info (if tables exist)
            try:
                index_info = self.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND sql IS NOT NULL
                    ORDER BY name
                """, fetchall=True)
                
                stats['performance_info'] = {
                    'indexes_count': len(index_info) if index_info else 0,
                    'indexes': [idx[0] for idx in index_info] if index_info else []
                }
            except:
                stats['performance_info'] = {'indexes_count': 0, 'indexes': []}
                
        except Exception as e:
            logger.error(f"Failed to collect storage statistics: {e}")
            stats['error'] = str(e)
        
        return stats
    
    def optimize_database(self) -> Dict[str, Any]:
        """
        Perform database optimization tasks.
        
        Returns:
            Dictionary with optimization results
        """
        results = {
            'vacuum_performed': False,
            'analyze_performed': False,
            'size_before_mb': 0,
            'size_after_mb': 0,
            'space_saved_mb': 0,
            'errors': []
        }
        
        try:
            # Get initial size
            if os.path.exists(self.db_name):
                results['size_before_mb'] = round(os.path.getsize(self.db_name) / (1024 * 1024), 2)
            
            # Perform VACUUM to reclaim space
            try:
                self.execute("VACUUM", commit=True)
                results['vacuum_performed'] = True
                logger.info("Database VACUUM completed")
            except Exception as e:
                results['errors'].append(f"VACUUM failed: {e}")
                logger.error(f"Database VACUUM failed: {e}")
            
            # Perform ANALYZE to update statistics
            try:
                self.execute("ANALYZE", commit=True)
                results['analyze_performed'] = True
                logger.info("Database ANALYZE completed")
            except Exception as e:
                results['errors'].append(f"ANALYZE failed: {e}")
                logger.error(f"Database ANALYZE failed: {e}")
            
            # Get final size
            if os.path.exists(self.db_name):
                results['size_after_mb'] = round(os.path.getsize(self.db_name) / (1024 * 1024), 2)
                results['space_saved_mb'] = round(results['size_before_mb'] - results['size_after_mb'], 2)
            
        except Exception as e:
            results['errors'].append(f"Optimization failed: {e}")
            logger.error(f"Database optimization failed: {e}")
        
        return results
    
    def backup_database_to_file(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Optional custom backup path
            
        Returns:
            Path to the created backup file
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.db_name}_backup_{timestamp}.db"
        
        try:
            if self.use_pool and self.connection_pool:
                conn = self.connection_pool.get_connection()
                try:
                    with sqlite3.connect(backup_path) as backup_conn:
                        conn.backup(backup_conn)
                    self.connection_pool.return_connection(conn)
                except Exception as e:
                    try:
                        conn.close()
                    except:
                        pass
                    raise e
            else:
                with sqlite3.connect(self.db_name) as source_conn:
                    with sqlite3.connect(backup_path) as backup_conn:
                        source_conn.backup(backup_conn)
            
            logger.info(f"Database backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            raise
    
    def get_database_health(self) -> Dict[str, Any]:
        """
        Check database health and integrity.
        
        Returns:
            Dictionary with health check results
        """
        health = {
            'integrity_check': False,
            'foreign_key_check': False,
            'table_count': 0,
            'index_count': 0,
            'connection_pool_healthy': False,
            'issues': []
        }
        
        try:
            # Integrity check
            result = self.execute("PRAGMA integrity_check", fetchone=True)
            if result and result[0] == "ok":
                health['integrity_check'] = True
            else:
                health['issues'].append(f"Integrity check failed: {result[0] if result else 'Unknown error'}")
            
            # Foreign key check
            fk_results = self.execute("PRAGMA foreign_key_check", fetchall=True)
            if not fk_results:  # Empty result means no foreign key violations
                health['foreign_key_check'] = True
            else:
                health['issues'].append(f"Foreign key violations found: {len(fk_results)}")
            
            # Count tables and indexes
            tables = self.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'", fetchone=True)
            indexes = self.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'", fetchone=True)
            
            health['table_count'] = tables[0] if tables else 0
            health['index_count'] = indexes[0] if indexes else 0
            
            # Check connection pool health
            if self.connection_pool:
                try:
                    # Try to get and return a connection
                    conn = self.connection_pool.get_connection()
                    conn.execute("SELECT 1")
                    self.connection_pool.return_connection(conn)
                    health['connection_pool_healthy'] = True
                except Exception as e:
                    health['issues'].append(f"Connection pool issue: {e}")
            else:
                health['connection_pool_healthy'] = True  # Not using pool is also healthy
                
        except Exception as e:
            health['issues'].append(f"Health check failed: {e}")
        
        return health
    
    def cleanup_connection_pool(self):
        """Close and cleanup the connection pool."""
        if self.connection_pool:
            try:
                self.connection_pool.close_all()
                logger.info("Database connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")

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
def get_database_manager(db_name: Optional[str] = None) -> DatabaseManager:
    """
    Factory function to get a DatabaseManager instance.
    
    Args:
        db_name: Optional database name override.
        
    Returns:
        DatabaseManager instance.
    """
    return DatabaseManager(db_name)


def init_database(db_name: Optional[str] = None):
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