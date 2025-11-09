"""
Unified Database Configuration for CyberBackup 3.0

This module provides a single source of truth for database configuration
across all components of the CyberBackup system.

Author: Claude Code
Date: 2025-11-07
Version: 1.0
"""

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """
    Centralized database configuration management.

    Provides consistent database path resolution across all components:
    - Python Backup Server
    - FletV2 Desktop GUI
    - Flask API Server
    - Database utilities and tools
    """

    # Project root determination
    _PROJECT_ROOT = Path(__file__).resolve().parents[1]

    # Database directory structure
    _DATA_DIR = _PROJECT_ROOT / 'data'
    _DATABASE_DIR = _DATA_DIR / 'database'

    # Canonical database paths
    _CANONICAL_DATABASE_PATH = _DATABASE_DIR / 'defensive.db'
    _BACKUP_DATABASE_PATH = _DATABASE_DIR / 'backups' / 'defensive_backup_{timestamp}.db'

    # Legacy database paths (for migration)
    _LEGACY_DATABASE_PATHS = [
        _PROJECT_ROOT / 'defensive.db',
        _PROJECT_ROOT / 'FletV2' / 'defensive.db',
        _PROJECT_ROOT / 'Database' / 'defensive.db',
        _PROJECT_ROOT / 'python_server' / 'defensive.db',
        _PROJECT_ROOT / 'python_server' / 'server' / 'defensive.db',
        _PROJECT_ROOT / 'data' / 'databases' / 'defensive.db',
    ]

    class DatabaseEnvironment:
        """Environment-specific database configuration."""
        DEVELOPMENT = "development"
        PRODUCTION = "production"
        TESTING = "testing"

    def __init__(self, environment: str = None):
        """
        Initialize database configuration.

        Args:
            environment: Environment name (development/production/testing)
                        If None, determined from environment variables
        """
        self.environment = environment or self._detect_environment()
        self._ensure_database_directory()

    @classmethod
    def get_canonical_database_path(cls) -> str:
        """
        Get the canonical database path as string.

        Returns:
            str: Absolute path to the canonical database file
        """
        return str(cls._CANONICAL_DATABASE_PATH.absolute())

    @classmethod
    def get_database_path(cls, environment: str = None) -> str:
        """
        Get database path for specific environment.

        Args:
            environment: Environment name (development/production/testing)

        Returns:
            str: Database path for the specified environment
        """
        env = environment or DatabaseConfig()._detect_environment()

        if env == DatabaseConfig.DatabaseEnvironment.TESTING:
            # Use separate test database
            test_db_path = cls._DATABASE_DIR / 'test_defensive.db'
            return str(test_db_path.absolute())

        # For development and production, use canonical database
        return cls.get_canonical_database_path()

    @classmethod
    def get_project_root(cls) -> Path:
        """Get the project root directory."""
        return cls._PROJECT_ROOT

    @classmethod
    def get_data_directory(cls) -> Path:
        """Get the data directory path."""
        return cls._DATA_DIR

    @classmethod
    def get_database_directory(cls) -> Path:
        """Get the database directory path."""
        return cls._DATABASE_DIR

    @classmethod
    def get_backup_directory(cls) -> Path:
        """Get the database backup directory path."""
        return cls._DATABASE_DIR / 'backups'

    @classmethod
    def get_legacy_database_paths(cls) -> list:
        """Get list of known legacy database paths."""
        return [str(path) for path in cls._LEGACY_DATABASE_PATHS]

    def _detect_environment(self) -> str:
        """
        Detect the current environment from environment variables.

        Returns:
            str: Environment name
        """
        # Check environment variables
        env = os.environ.get('CYBERBACKUP_ENV', '').lower()
        if env in ['prod', 'production']:
            return self.DatabaseEnvironment.PRODUCTION
        elif env in ['test', 'testing']:
            return self.DatabaseEnvironment.TESTING
        elif env in ['dev', 'development']:
            return self.DatabaseEnvironment.DEVELOPMENT

        # Check for debug mode
        if os.environ.get('DEBUG', '').lower() in ['true', '1', 'yes']:
            return self.DatabaseEnvironment.DEVELOPMENT

        # Default to development
        return self.DatabaseEnvironment.DEVELOPMENT

    def _ensure_database_directory(self) -> None:
        """Ensure database directory structure exists."""
        try:
            # Create data directory
            self._DATA_DIR.mkdir(parents=True, exist_ok=True)

            # Create database directory
            self._DATABASE_DIR.mkdir(parents=True, exist_ok=True)

            # Create backup directory
            self.get_backup_directory().mkdir(parents=True, exist_ok=True)

            logger.debug(f"Database directories ensured: {self._DATABASE_DIR}")

        except Exception as e:
            logger.error(f"Failed to create database directories: {e}")
            raise

    def validate_database_access(self, db_path: str = None) -> dict[str, Any]:
        """
        Validate database file access and permissions.

        Args:
            db_path: Database path to validate (default: canonical path)

        Returns:
            dict: Validation results with status and details
        """
        if db_path is None:
            db_path = self.get_canonical_database_path()

        db_file = Path(db_path)
        result = {
            'path': db_path,
            'exists': False,
            'readable': False,
            'writable': False,
            'size': 0,
            'error': None,
            'status': 'invalid'
        }

        try:
            # Check if file exists
            result['exists'] = db_file.exists()

            if result['exists']:
                # Check file size
                result['size'] = db_file.stat().st_size

                # Test read access
                try:
                    with open(db_file, 'rb') as f:
                        f.read(1)  # Try to read 1 byte
                    result['readable'] = True
                except Exception as e:
                    result['error'] = f"Read access failed: {e}"

                # Test write access
                try:
                    # Test by opening in append mode
                    with open(db_file, 'ab') as f:
                        pass  # Just test access
                    result['writable'] = True
                except Exception as e:
                    result['error'] = f"Write access failed: {e}"

                # Set status based on access
                if result['readable'] and result['writable']:
                    result['status'] = 'valid'
                elif result['readable']:
                    result['status'] = 'read_only'
                else:
                    result['status'] = 'inaccessible'
            else:
                # Check if parent directory is writable
                parent_dir = db_file.parent
                if parent_dir.exists() and os.access(parent_dir, os.W_OK):
                    result['status'] = 'creatable'
                    result['writable'] = True
                else:
                    result['error'] = f"Parent directory not writable: {parent_dir}"
                    result['status'] = 'cannot_create'

        except Exception as e:
            result['error'] = f"Validation failed: {e}"
            result['status'] = 'error'

        return result

    def get_database_connection_string(self, environment: str = None) -> str:
        """
        Get SQLite connection string for the specified environment.

        Args:
            environment: Environment name

        Returns:
            str: SQLite connection string with appropriate parameters
        """
        db_path = self.get_database_path(environment)

        # For Flet applications, we need check_same_thread=False
        # This is required due to Flet's WebSocket architecture
        connection_params = [
            f"'{db_path}'",
            "check_same_thread=False",  # Required for Flet
            "timeout=30.0",  # Connection timeout
        ]

        return f"sqlite3.connect({', '.join(connection_params)})"

    def export_config(self) -> dict[str, Any]:
        """
        Export configuration as dictionary for logging/debugging.

        Returns:
            dict: Configuration details
        """
        return {
            'environment': self.environment,
            'project_root': str(self._PROJECT_ROOT),
            'data_directory': str(self._DATA_DIR),
            'database_directory': str(self._DATABASE_DIR),
            'canonical_database_path': str(self._CANONICAL_DATABASE_PATH),
            'backup_directory': str(self.get_backup_directory()),
            'current_database_path': self.get_database_path(),
            'legacy_paths': self.get_legacy_database_paths(),
        }


# Global instance for easy import
_database_config = None

def get_database_config() -> DatabaseConfig:
    """Get global database configuration instance."""
    global _database_config
    if _database_config is None:
        _database_config = DatabaseConfig()
    return _database_config

def get_database_path(environment: str = None) -> str:
    """Get database path for specified environment."""
    return DatabaseConfig.get_database_path(environment)

def get_canonical_database_path() -> str:
    """Get canonical database path."""
    return DatabaseConfig.get_canonical_database_path()

def validate_database_environment() -> dict[str, Any]:
    """Validate database environment and return status."""
    config = get_database_config()
    validation = config.validate_database_access()

    # Add configuration details to validation
    validation.update(config.export_config())

    return validation


# Convenience functions for backward compatibility
def get_project_root() -> Path:
    """Get project root directory."""
    return DatabaseConfig.get_project_root()

def get_data_directory() -> Path:
    """Get data directory."""
    return DatabaseConfig.get_data_directory()

def get_database_directory() -> Path:
    """Get database directory."""
    return DatabaseConfig.get_database_directory()


if __name__ == '__main__':
    # Test the configuration
    config = get_database_config()

    print("Database Configuration Test")
    print("=" * 40)
    print(f"Environment: {config.environment}")
    print(f"Project Root: {config.get_project_root()}")
    print(f"Data Directory: {config.get_data_directory()}")
    print(f"Database Directory: {config.get_database_directory()}")
    print(f"Canonical Database Path: {config.get_canonical_database_path()}")
    print(f"Current Database Path: {config.get_database_path()}")
    print()

    # Validate database access
    validation = validate_database_environment()
    print("Database Validation:")
    print(f"Status: {validation['status']}")
    print(f"Path: {validation['path']}")
    print(f"Exists: {validation['exists']}")
    print(f"Readable: {validation['readable']}")
    print(f"Writable: {validation['writable']}")
    print(f"Size: {validation['size']} bytes")

    if validation['error']:
        print(f"Error: {validation['error']}")

    print()
    print("Legacy Database Paths:")
    for path in config.get_legacy_database_paths():
        exists = Path(path).exists()
        print(f"  {'✓' if exists else '✗'} {path}")
