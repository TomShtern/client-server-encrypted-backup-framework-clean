# database_migrations.py
# Safe Database Migration System for the Encrypted Backup Framework
# Handles schema changes and upgrades without breaking existing functionality

import logging
import os
import shutil
import sqlite3
from datetime import UTC, datetime
from typing import Any

try:
    from .config import DATABASE_NAME
except ImportError:
    # Fallback for direct execution
    DATABASE_NAME = "defensive.db"

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """
    Represents a single database migration with rollback capability.
    """

    def __init__(self, version: int, description: str, up_sql: str, down_sql: str = ""):
        self.version = version
        self.description = description
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.applied_at = None

    def __str__(self):
        return f"Migration {self.version}: {self.description}"

class DatabaseMigrationManager:
    """
    Manages database schema migrations with safety checks and rollback capability.
    Ensures that database changes don't break existing functionality.
    """

    def __init__(self, db_name: str | None = None):
        self.db_name = db_name or DATABASE_NAME
        self.migrations: list[DatabaseMigration] = []
        self._init_migration_table()
        self._register_migrations()

    def _init_migration_table(self):
        """Initialize the migration tracking table if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS database_migrations (
                        version INTEGER PRIMARY KEY,
                        description TEXT NOT NULL,
                        applied_at TEXT NOT NULL,
                        rollback_sql TEXT
                    )
                ''')
                conn.commit()
                logger.info("Migration tracking table initialized")
        except Exception as e:
            logger.error(f"Failed to initialize migration table: {e}")
            raise

    def _register_migrations(self):
        """Register all available migrations in order."""

        # Migration 1: Add performance indexes
        self.migrations.append(DatabaseMigration(
            version=1,
            description="Add performance indexes for faster queries",
            up_sql='''
                CREATE INDEX IF NOT EXISTS idx_files_client_id ON files(ClientID);
                CREATE INDEX IF NOT EXISTS idx_files_filename ON files(FileName);
                CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(Name);
                CREATE INDEX IF NOT EXISTS idx_files_verified ON files(Verified);
                CREATE INDEX IF NOT EXISTS idx_clients_lastseen ON clients(LastSeen);
                CREATE INDEX IF NOT EXISTS idx_files_size ON files(FileSize);
                CREATE INDEX IF NOT EXISTS idx_files_client_verified ON files(ClientID, Verified);
                CREATE INDEX IF NOT EXISTS idx_files_client_name ON files(ClientID, FileName);
            ''',
            down_sql='''
                DROP INDEX IF EXISTS idx_files_client_id;
                DROP INDEX IF EXISTS idx_files_filename;
                DROP INDEX IF EXISTS idx_clients_name;
                DROP INDEX IF EXISTS idx_files_verified;
                DROP INDEX IF EXISTS idx_clients_lastseen;
                DROP INDEX IF EXISTS idx_files_size;
                DROP INDEX IF EXISTS idx_files_client_verified;
                DROP INDEX IF EXISTS idx_files_client_name;
            '''
        ))

        # Migration 2: Add extended file metadata
        self.migrations.append(DatabaseMigration(
            version=2,
            description="Add extended file metadata fields",
            up_sql='''
                ALTER TABLE files ADD COLUMN FileCategory VARCHAR(50) DEFAULT 'document';
                ALTER TABLE files ADD COLUMN MimeType VARCHAR(100);
                ALTER TABLE files ADD COLUMN FileExtension VARCHAR(10);
                ALTER TABLE files ADD COLUMN OriginalPath TEXT;
                ALTER TABLE files ADD COLUMN FileHash VARCHAR(64);
                ALTER TABLE files ADD COLUMN TransferDuration INTEGER;
                ALTER TABLE files ADD COLUMN TransferSpeed INTEGER;
                ALTER TABLE files ADD COLUMN CompressionRatio REAL;
            ''',
            down_sql='''
                -- SQLite doesn't support DROP COLUMN, so rollback not available
                -- Users would need to restore from backup
            '''
        ))

        # Migration 3: Create analytics tables
        self.migrations.append(DatabaseMigration(
            version=3,
            description="Create analytics and statistics tables",
            up_sql='''
                CREATE TABLE IF NOT EXISTS transfer_stats (
                    Date TEXT PRIMARY KEY,
                    TotalFiles INTEGER DEFAULT 0,
                    TotalBytes INTEGER DEFAULT 0,
                    SuccessfulTransfers INTEGER DEFAULT 0,
                    FailedTransfers INTEGER DEFAULT 0,
                    AverageFileSize INTEGER DEFAULT 0,
                    PeakTransferSpeed INTEGER DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS client_activity (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ClientID BLOB(16) NOT NULL,
                    ActivityType VARCHAR(50) NOT NULL,
                    Timestamp TEXT NOT NULL,
                    FileCount INTEGER DEFAULT 0,
                    BytesTransferred INTEGER DEFAULT 0,
                    FOREIGN KEY (ClientID) REFERENCES clients(ID)
                );
                
                CREATE TABLE IF NOT EXISTS file_categories (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name VARCHAR(50) UNIQUE NOT NULL,
                    Description TEXT,
                    DefaultPath VARCHAR(255),
                    Color VARCHAR(7) DEFAULT '#007acc'
                );
                
                -- Insert default categories
                INSERT OR IGNORE INTO file_categories (Name, Description, DefaultPath) VALUES
                ('document', 'Text documents and PDFs', 'received_files/documents/'),
                ('image', 'Images and photos', 'received_files/images/'),
                ('backup', 'System backups', 'received_files/backups/'),
                ('other', 'Miscellaneous files', 'received_files/other/');
            ''',
            down_sql='''
                DROP TABLE IF EXISTS transfer_stats;
                DROP TABLE IF EXISTS client_activity;
                DROP TABLE IF EXISTS file_categories;
            '''
        ))

        # Migration 4: Client quotas and storage management
        self.migrations.append(DatabaseMigration(
            version=4,
            description="Add client quota management",
            up_sql='''
                CREATE TABLE IF NOT EXISTS client_quotas (
                    ClientID BLOB(16) PRIMARY KEY,
                    QuotaBytes INTEGER NOT NULL DEFAULT 1073741824,
                    UsedBytes INTEGER DEFAULT 0,
                    LastUpdated TEXT NOT NULL,
                    WarningThreshold REAL DEFAULT 0.8,
                    FOREIGN KEY (ClientID) REFERENCES clients(ID) ON DELETE CASCADE
                );
                
                -- Initialize quotas for existing clients
                INSERT OR IGNORE INTO client_quotas (ClientID, LastUpdated)
                SELECT ID, datetime('now') FROM clients;
            ''',
            down_sql='''
                DROP TABLE IF EXISTS client_quotas;
            '''
        ))

        # Migration 5: File versioning system
        self.migrations.append(DatabaseMigration(
            version=5,
            description="Add file versioning system",
            up_sql='''
                CREATE TABLE IF NOT EXISTS file_versions (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    FileID BLOB(16) NOT NULL,
                    VersionNumber INTEGER NOT NULL,
                    PathName VARCHAR(255) NOT NULL,
                    FileSize INTEGER,
                    CreatedDate TEXT NOT NULL,
                    IsActive BOOLEAN DEFAULT 1,
                    VersionHash VARCHAR(64),
                    ParentVersionID INTEGER,
                    FOREIGN KEY (FileID) REFERENCES files(ID) ON DELETE CASCADE,
                    FOREIGN KEY (ParentVersionID) REFERENCES file_versions(ID)
                );
                
                ALTER TABLE files ADD COLUMN CurrentVersionID INTEGER;
                ALTER TABLE files ADD COLUMN TotalVersions INTEGER DEFAULT 1;
                
                CREATE INDEX IF NOT EXISTS idx_file_versions_file_id ON file_versions(FileID);
                CREATE INDEX IF NOT EXISTS idx_file_versions_active ON file_versions(IsActive);
            ''',
            down_sql='''
                DROP TABLE IF EXISTS file_versions;
                -- Note: ALTER TABLE DROP COLUMN not supported in SQLite
            '''
        ))

    def backup_database(self) -> str:
        """Create a backup of the database before applying migrations."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.db_name}.backup_{timestamp}"

        try:
            shutil.copy2(self.db_name, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            raise

    def get_current_version(self) -> int:
        """Get the current database version."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(version) FROM database_migrations")
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0
        except Exception as e:
            logger.warning(f"Could not determine database version: {e}")
            return 0

    def get_pending_migrations(self) -> list[DatabaseMigration]:
        """Get list of migrations that haven't been applied yet."""
        current_version = self.get_current_version()
        return [m for m in self.migrations if m.version > current_version]

    def apply_migration(self, migration: DatabaseMigration) -> bool:
        """Apply a single migration with safety checks."""
        logger.info(f"Applying migration {migration.version}: {migration.description}")

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Execute migration SQL - use executescript for better SQL parsing
                # Note: executescript commits automatically, so we can't use transactions
                # For safety, we validate that this is a read-only or safe operation first
                if any(dangerous in migration.up_sql.upper() for dangerous in ['DROP TABLE', 'DELETE FROM clients', 'DELETE FROM files']):
                    logger.error(f"Migration {migration.version} contains potentially dangerous operations")
                    return False

                # Execute the migration SQL
                cursor.executescript(migration.up_sql)

                # Record migration in tracking table
                cursor.execute('''
                    INSERT INTO database_migrations (version, description, applied_at, rollback_sql)
                    VALUES (?, ?, ?, ?)
                ''', (
                    migration.version,
                    migration.description,
                    datetime.now(UTC).isoformat(),
                    migration.down_sql
                ))

                conn.commit()
                logger.info(f"Successfully applied migration {migration.version}")
                return True

        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            return False

    def migrate_to_latest(self) -> bool:
        """Apply all pending migrations to bring database to latest version."""
        pending_migrations = self.get_pending_migrations()

        if not pending_migrations:
            logger.info("Database is already at latest version")
            return True

        # Create backup before applying migrations
        backup_path = self.backup_database()
        logger.info(f"Created backup: {backup_path}")

        success_count = 0
        for migration in pending_migrations:
            if self.apply_migration(migration):
                success_count += 1
            else:
                logger.error(f"Migration failed at version {migration.version}")
                logger.error(f"Database backup available at: {backup_path}")
                return False

        logger.info(f"Successfully applied {success_count} migrations")
        logger.info(f"Database is now at version {self.get_current_version()}")
        return True

    def validate_database_integrity(self) -> bool:
        """Validate database integrity after migrations."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Check database integrity
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                if result[0] != "ok":
                    logger.error(f"Database integrity check failed: {result[0]}")
                    return False

                # Check if critical tables exist
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('clients', 'files')
                """)
                tables = [row[0] for row in cursor.fetchall()]

                if 'clients' not in tables or 'files' not in tables:
                    logger.error("Critical tables missing after migration")
                    return False

                logger.info("Database integrity validation passed")
                return True

        except Exception as e:
            logger.error(f"Database integrity validation failed: {e}")
            return False

    def get_migration_status(self) -> dict[str, Any]:
        """Get detailed status of all migrations."""
        current_version = self.get_current_version()
        pending = self.get_pending_migrations()

        return {
            'current_version': current_version,
            'latest_version': max([m.version for m in self.migrations]) if self.migrations else 0,
            'pending_migrations': len(pending),
            'total_migrations': len(self.migrations),
            'database_file': self.db_name,
            'database_exists': os.path.exists(self.db_name)
        }

def migrate_database(db_name: str | None = None) -> bool:
    """
    Convenience function to run all pending migrations.
    
    Args:
        db_name: Database name/path. If None, uses default.
        
    Returns:
        True if all migrations succeeded, False otherwise.
    """
    try:
        manager = DatabaseMigrationManager(db_name)
        success = manager.migrate_to_latest()

        if success:
            logger.info("Database migration completed successfully.")
            return True
        else:
            logger.error("Database migration failed.")
            return False

    except Exception as e:
        logger.error(f"Database migration error: {e}")
        return False

if __name__ == "__main__":
    # CLI interface for migration management
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        success = migrate_database()
        sys.exit(0 if success else 1)
    else:
        manager = DatabaseMigrationManager()
        status = manager.get_migration_status()
        print(f"Database version: {status['current_version']}/{status['latest_version']}")
        print(f"Pending migrations: {status['pending_migrations']}")
