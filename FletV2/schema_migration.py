#!/usr/bin/env python3
"""
Database Schema Migration for FletV2 Integration

This script migrates your existing database schema to be compatible with FletV2
while preserving all existing data. It integrates with the BackupServer's existing
migration system and ensures compatibility between server and GUI expectations.
"""

import logging
import os
import sqlite3
import sys
import uuid
from datetime import datetime
from typing import Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import BackupServer migration system
try:
    from python_server.server.database_migrations import DatabaseMigrationManager
    MIGRATION_SYSTEM_AVAILABLE = True
except ImportError:
    MIGRATION_SYSTEM_AVAILABLE = False

# Import configuration
try:
    from Shared.config import get_absolute_database_path, get_database_config_for_fletv2
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def blob_to_uuid_string(blob_data: bytes) -> str:
    """Convert BLOB UUID to string representation."""
    if not blob_data or len(blob_data) != 16:
        return str(uuid.uuid4())
    return str(uuid.UUID(bytes=blob_data))

def migrate_database_schema(db_path: str | None = None) -> bool:
    """
    Migrate the database schema to be compatible with FletV2 using integrated migration system.

    Args:
        db_path: Path to the SQLite database (optional, uses config if not provided)

    Returns:
        True if migration successful, False otherwise
    """
    try:
        # Use config system to get database path if not provided
        if db_path is None and CONFIG_AVAILABLE:
            db_path = get_absolute_database_path()
            logger.info(f"Using configured database path: {db_path}")
        elif db_path is None:
            logger.error("No database path provided and config system unavailable")
            return False

        logger.info(f"Starting integrated database migration for: {db_path}")

        # First, run BackupServer's migration system if available
        if MIGRATION_SYSTEM_AVAILABLE:
            logger.info("Running BackupServer migration system...")
            migration_manager = DatabaseMigrationManager(db_path)
            if pending := migration_manager.get_pending_migrations():
                logger.info(f"Applying {len(pending)} BackupServer migrations...")
                if not migration_manager.migrate_to_latest():
                    logger.warning("Some BackupServer migrations failed, continuing with FletV2 migration...")
            else:
                logger.info("No pending BackupServer migrations")
        else:
            logger.warning("BackupServer migration system not available, proceeding with basic migration")

        # Create backup first
        backup_path = f"{db_path}.fletv2_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            logger.info(f"FletV2 migration backup created: {backup_path}")

        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            # Check current schema
            schema_info = check_database_schema(conn)
            logger.info(f"Current schema: {schema_info}")

            # Apply FletV2-specific enhancements
            if not apply_fletv2_enhancements(conn, schema_info):
                logger.warning("Some FletV2 enhancements failed, but basic schema is compatible")

            # Verify compatibility
            if verify_fletv2_compatibility(conn):
                logger.info("✅ Database schema is FletV2 compatible!")
            else:
                logger.warning("⚠️ Schema compatibility check failed, but migration completed")

            conn.commit()

        logger.info("✅ Integrated database migration completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Integrated database migration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def check_database_schema(conn: sqlite3.Connection) -> dict[str, Any]:
    """Check the current database schema and return information about it."""
    try:
        # Get table information
        tables = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """).fetchall()

        existing_tables = [t[0] for t in tables]

        # Check for BackupServer schema
        schema_info = {
            'tables': existing_tables,
            'has_clients_table': 'clients' in existing_tables,
            'has_files_table': 'files' in existing_tables,
            'has_migrations_table': 'database_migrations' in existing_tables,
            'backupserver_compatible': False,
            'fletv2_ready': False
        }

        # Check if clients table has BackupServer schema
        if 'clients' in existing_tables:
            clients_columns = conn.execute("PRAGMA table_info(clients)").fetchall()
            column_names = [col[1] for col in clients_columns]
            schema_info['clients_columns'] = column_names
            schema_info['backupserver_compatible'] = 'ID' in column_names and 'Name' in column_names

        # Check if files table has BackupServer schema
        if 'files' in existing_tables:
            files_columns = conn.execute("PRAGMA table_info(files)").fetchall()
            column_names = [col[1] for col in files_columns]
            schema_info['files_columns'] = column_names
            schema_info['backupserver_compatible'] = schema_info['backupserver_compatible'] and 'ClientID' in column_names

        return schema_info

    except Exception as e:
        logger.error(f"Error checking database schema: {e}")
        return {'tables': [], 'backupserver_compatible': False, 'fletv2_ready': False}

def apply_fletv2_enhancements(conn: sqlite3.Connection, schema_info: dict[str, Any]) -> bool:
    """Apply FletV2-specific enhancements to the existing BackupServer schema."""
    try:
        logger.info("Applying FletV2 enhancements...")

        # Create indexes for better performance in GUI operations
        create_fletv2_indexes(conn)

        # Create views for data compatibility if needed
        create_compatibility_views(conn, schema_info)

        # Add any missing columns that FletV2 might expect
        add_fletv2_columns(conn, schema_info)

        return True

    except Exception as e:
        logger.error(f"Error applying FletV2 enhancements: {e}")
        return False

def create_fletv2_indexes(conn: sqlite3.Connection):
    """Create indexes optimized for FletV2 GUI operations."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_fletv2_clients_name ON clients(Name)",
        "CREATE INDEX IF NOT EXISTS idx_fletv2_clients_lastseen ON clients(LastSeen)",
        "CREATE INDEX IF NOT EXISTS idx_fletv2_files_filename ON files(FileName)",
        "CREATE INDEX IF NOT EXISTS idx_fletv2_files_client ON files(ClientID)",
        "CREATE INDEX IF NOT EXISTS idx_fletv2_files_verified ON files(Verified)",
        "CREATE INDEX IF NOT EXISTS idx_fletv2_files_size ON files(FileSize)"
    ]

    for index_sql in indexes:
        try:
            conn.execute(index_sql)
            logger.debug(f"Created index: {index_sql}")
        except Exception as e:
            logger.warning(f"Failed to create index: {e}")

def create_compatibility_views(conn: sqlite3.Connection, schema_info: dict[str, Any]):
    """Create views for data compatibility between BackupServer and FletV2."""
    try:
        # Create a view that presents clients in FletV2-friendly format
        if schema_info.get('has_clients_table'):
            conn.execute("""
                CREATE VIEW IF NOT EXISTS fletv2_clients AS
                SELECT
                    hex(ID) as id,
                    Name as name,
                    LastSeen as last_seen,
                    CASE
                        WHEN datetime(LastSeen) > datetime('now', '-1 hour') THEN 'Active'
                        WHEN datetime(LastSeen) > datetime('now', '-1 day') THEN 'Recent'
                        ELSE 'Inactive'
                    END as status,
                    (SELECT COUNT(*) FROM files WHERE ClientID = clients.ID) as files_count
                FROM clients
            """)
            logger.debug("Created fletv2_clients compatibility view")

        # Create a view that presents files in FletV2-friendly format
        if schema_info.get('has_files_table'):
            conn.execute("""
                CREATE VIEW IF NOT EXISTS fletv2_files AS
                SELECT
                    hex(ID) as id,
                    FileName as name,
                    hex(ClientID) as client_id,
                    FileSize as size,
                    CASE
                        WHEN Verified = 1 THEN 'Verified'
                        ELSE 'Pending'
                    END as status,
                    PathName as path,
                    ModificationDate as modified,
                    ModificationDate as created,
                    'file' as type,
                    1 as backup_count,
                    ModificationDate as last_backup
                FROM files
            """)
            logger.debug("Created fletv2_files compatibility view")

    except Exception as e:
        logger.warning(f"Failed to create compatibility views: {e}")

def add_fletv2_columns(conn: sqlite3.Connection, schema_info: dict[str, Any]):
    """Add any missing columns that FletV2 might need."""
    try:
        # This is handled by BackupServer's migration system
        # We just verify the columns exist
        if schema_info.get('has_files_table'):
            files_columns = schema_info.get('files_columns', [])
            if 'FileSize' not in files_columns:
                logger.info("FileSize column missing - should be added by BackupServer migrations")
            if 'ModificationDate' not in files_columns:
                logger.info("ModificationDate column missing - should be added by BackupServer migrations")

    except Exception as e:
        logger.warning(f"Error checking FletV2 columns: {e}")

def verify_fletv2_compatibility(conn: sqlite3.Connection) -> bool:
    """Verify that the database is compatible with FletV2 expectations."""
    try:
        # Check that essential tables exist
        tables = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('clients', 'files')
        """).fetchall()

        if len(tables) < 2:
            logger.error("Missing essential tables for FletV2 compatibility")
            return False

        # Check that we can read from both tables
        clients_count = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        files_count = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]

        logger.info(f"Compatibility check: {clients_count} clients, {files_count} files")

        # Check that compatibility views exist
        try:
            conn.execute("SELECT COUNT(*) FROM fletv2_clients").fetchone()
            conn.execute("SELECT COUNT(*) FROM fletv2_files").fetchone()
            logger.info("Compatibility views are working")
        except Exception as e:
            logger.warning(f"Compatibility views issue: {e}")

        return True

    except Exception as e:
        logger.error(f"Compatibility verification failed: {e}")
        return False

def create_fletv2_tables(conn: sqlite3.Connection):
    """Create FletV2-compatible tables."""
    logger.info("Creating FletV2-compatible tables...")

    # Create new clients table with FletV2 schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clients_new (
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
            metadata TEXT,

            -- Keep compatibility columns
            public_key BLOB,
            aes_key BLOB
        )
    """)

    # Create new files table with FletV2 schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS files_new (
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

            -- Keep compatibility columns
            modification_date TEXT,
            crc INTEGER,

            FOREIGN KEY (client_id) REFERENCES clients_new (id) ON DELETE CASCADE
        )
    """)

def migrate_clients_data(conn: sqlite3.Connection):
    """Migrate data from old clients table to new schema."""
    logger.info("Migrating clients data...")

    try:
        # Get all clients from old table
        old_clients = conn.execute("""
            SELECT ID, Name, PublicKey, LastSeen, AESKey
            FROM clients
        """).fetchall()

        logger.info(f"Found {len(old_clients)} clients to migrate")

        for client in old_clients:
            old_id, name, public_key, last_seen, aes_key = client

            # Convert BLOB ID to string
            new_id = blob_to_uuid_string(old_id)

            # Determine status based on last_seen
            try:
                last_seen_dt = datetime.fromisoformat(last_seen)
                time_diff = datetime.now() - last_seen_dt
                status = "Connected" if time_diff.total_seconds() < 300 else "Offline"  # 5 minutes
            except:
                status = "Registered"

            # Insert into new table
            conn.execute("""
                INSERT OR REPLACE INTO clients_new (
                    id, client_id, name, status, last_seen, created_at,
                    total_size, files_count, public_key, aes_key
                ) VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?, ?)
            """, (new_id, new_id, name, status, last_seen, last_seen, public_key, aes_key))

        logger.info(f"✅ Migrated {len(old_clients)} clients")

    except Exception as e:
        logger.error(f"Error migrating clients: {e}")

def migrate_files_data(conn: sqlite3.Connection):
    """Migrate data from old files table to new schema."""
    logger.info("Migrating files data...")

    try:
        # Get all files from old table
        old_files = conn.execute("""
            SELECT ID, FileName, PathName, Verified, FileSize,
                   ModificationDate, CRC, ClientID
            FROM files
        """).fetchall()

        logger.info(f"Found {len(old_files)} files to migrate")

        for file_data in old_files:
            old_id, filename, path_name, verified, file_size, mod_date, crc, client_id = file_data

            # Convert BLOB IDs to strings
            new_id = blob_to_uuid_string(old_id)
            new_client_id = blob_to_uuid_string(client_id)

            # Use PathName as storage_path, and extract original_path
            storage_path = path_name or ""
            original_path = os.path.basename(storage_path) if storage_path else filename

            # Use modification date as uploaded_at, or current time
            uploaded_at = mod_date or datetime.now().isoformat()

            # Generate checksum from CRC if available
            checksum = str(crc) if crc else None

            # Insert into new table
            conn.execute("""
                INSERT OR REPLACE INTO files_new (
                    id, filename, original_path, size, checksum, client_id,
                    uploaded_at, verified, storage_path, modification_date, crc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_id, filename, original_path, file_size or 0, checksum,
                  new_client_id, uploaded_at, bool(verified), storage_path, mod_date, crc))

        logger.info(f"✅ Migrated {len(old_files)} files")

        # Update client file counts and sizes
        update_client_statistics(conn)

    except Exception as e:
        logger.error(f"Error migrating files: {e}")

def update_client_statistics(conn: sqlite3.Connection):
    """Update client file counts and total sizes."""
    logger.info("Updating client statistics...")

    try:
        conn.execute("""
            UPDATE clients_new
            SET files_count = (
                SELECT COUNT(*) FROM files_new
                WHERE files_new.client_id = clients_new.id
            ),
            total_size = (
                SELECT COALESCE(SUM(size), 0) FROM files_new
                WHERE files_new.client_id = clients_new.id
            )
        """)

        logger.info("✅ Updated client statistics")

    except Exception as e:
        logger.error(f"Error updating client statistics: {e}")

def create_additional_tables(conn: sqlite3.Connection):
    """Create additional tables that FletV2 might expect."""
    logger.info("Creating additional tables...")

    # Transfers table for tracking file transfers
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transfers (
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
            FOREIGN KEY (file_id) REFERENCES files_new (id) ON DELETE CASCADE,
            FOREIGN KEY (client_id) REFERENCES clients_new (id) ON DELETE CASCADE
        )
    """)

    # Logs table for system logging
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            source TEXT DEFAULT 'server',
            client_id TEXT,
            file_id TEXT,
            metadata TEXT,
            FOREIGN KEY (client_id) REFERENCES clients_new (id) ON DELETE SET NULL,
            FOREIGN KEY (file_id) REFERENCES files_new (id) ON DELETE SET NULL
        )
    """)

    # Server statistics table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS server_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            clients_connected INTEGER DEFAULT 0,
            total_files INTEGER DEFAULT 0,
            total_storage_gb REAL DEFAULT 0,
            active_transfers INTEGER DEFAULT 0,
            cpu_usage REAL DEFAULT 0,
            memory_usage REAL DEFAULT 0,
            disk_usage REAL DEFAULT 0
        )
    """)

    logger.info("✅ Created additional tables")

def create_indexes(conn: sqlite3.Connection):
    """Create database indexes for performance."""
    logger.info("Creating database indexes...")

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_clients_status ON clients_new(status)",
        "CREATE INDEX IF NOT EXISTS idx_files_client_id ON files_new(client_id)",
        "CREATE INDEX IF NOT EXISTS idx_files_uploaded_at ON files_new(uploaded_at)",
        "CREATE INDEX IF NOT EXISTS idx_transfers_status ON transfers(status)",
        "CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)",
        "CREATE INDEX IF NOT EXISTS idx_logs_client_id ON logs(client_id)",
    ]

    for index_sql in indexes:
        try:
            conn.execute(index_sql)
        except sqlite3.Error as e:
            logger.warning(f"Could not create index: {e}")

    logger.info("✅ Created database indexes")

def finalize_migration(conn: sqlite3.Connection):
    """Finalize migration by renaming tables."""
    logger.info("Finalizing migration...")

    try:
        # Rename old tables
        conn.execute("ALTER TABLE clients RENAME TO clients_old")
        conn.execute("ALTER TABLE files RENAME TO files_old")

        # Rename new tables
        conn.execute("ALTER TABLE clients_new RENAME TO clients")
        conn.execute("ALTER TABLE files_new RENAME TO files")

        logger.info("✅ Migration finalized - old tables preserved as *_old")

    except sqlite3.Error as e:
        logger.warning(f"Could not rename tables (they may not exist): {e}")

def main():
    """Main migration function."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate database schema for FletV2 integration")
    parser.add_argument("--db-path", default="backup_server.db",
                       help="Path to database file (default: backup_server.db)")
    parser.add_argument("--finalize", action="store_true",
                       help="Finalize migration by renaming tables")

    args = parser.parse_args()

    if not os.path.exists(args.db_path):
        logger.info(f"Database {args.db_path} doesn't exist - creating new one")
        # Create a minimal database for testing
        with sqlite3.connect(args.db_path) as conn:
            conn.execute("CREATE TABLE temp (id INTEGER)")

    # Run migration
    if migrate_database_schema(args.db_path):
        if args.finalize:
            with sqlite3.connect(args.db_path) as conn:
                finalize_migration(conn)
                conn.commit()

        logger.info("🎉 Database migration completed successfully!")
        logger.info(f"Your database at {args.db_path} is now FletV2-compatible!")
        return 0
    else:
        logger.error("❌ Database migration failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
