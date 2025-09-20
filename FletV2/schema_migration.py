#!/usr/bin/env python3
"""
Database Schema Migration for FletV2 Integration

This script migrates your existing database schema to be compatible with FletV2
while preserving all existing data. It adds missing columns and creates views
to bridge between your current schema and FletV2's expectations.
"""

import os
import sys
import sqlite3
import logging
import uuid
from datetime import datetime
from typing import Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def blob_to_uuid_string(blob_data: bytes) -> str:
    """Convert BLOB UUID to string representation."""
    if not blob_data or len(blob_data) != 16:
        return str(uuid.uuid4())
    return str(uuid.UUID(bytes=blob_data))

def migrate_database_schema(db_path: str) -> bool:
    """
    Migrate the database schema to be compatible with FletV2.

    Args:
        db_path: Path to the SQLite database

    Returns:
        True if migration successful, False otherwise
    """
    try:
        logger.info(f"Starting database migration for: {db_path}")

        # Create backup first
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            logger.info(f"Database backup created: {backup_path}")

        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            # Check if tables exist
            tables = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """).fetchall()

            existing_tables = [t[0] for t in tables]
            logger.info(f"Existing tables: {existing_tables}")

            # Create new FletV2-compatible tables
            create_fletv2_tables(conn)

            # Migrate data from old tables if they exist
            if 'clients' in existing_tables:
                migrate_clients_data(conn)

            if 'files' in existing_tables:
                migrate_files_data(conn)

            # Create missing tables for FletV2
            create_additional_tables(conn)

            # Create indexes for performance
            create_indexes(conn)

            conn.commit()

        logger.info("✅ Database migration completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
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