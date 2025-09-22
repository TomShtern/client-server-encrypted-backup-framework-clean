"""
Canonical configuration management for the Client-Server Encrypted Backup Framework.

This module provides centralized configuration management that replaces
scattered configuration logic throughout the codebase.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Server configuration parameters."""
    host: str = "127.0.0.1"
    port: int = 1256
    max_connections: int = 10
    buffer_size: int = 8192
    timeout: int = 30
    enable_logging: bool = True
    log_level: str = "INFO"
    database_path: str = "defensive.db"
    received_files_dir: str = "received_files"
    keys_dir: str = "data/keys"


@dataclass
class APIServerConfig:
    """API server configuration parameters."""
    host: str = "127.0.0.1"
    port: int = 9090
    debug: bool = False
    max_content_length: int = 16 * 1024 * 1024  # 16MB
    upload_timeout: int = 300
    enable_cors: bool = True


@dataclass
class CryptoConfig:
    """Cryptographic configuration parameters."""
    rsa_key_size: int = 2048
    aes_key_size: int = 256
    private_key_file: str = "priv.key"
    public_key_file: str = "valid_public_key.der"
    keys_dir: str = "data/keys"
    enable_compression: bool = True


@dataclass
class ProtocolConfig:
    """Protocol configuration parameters."""
    version: int = 3
    max_filename_length: int = 200
    max_payload_size: int = 1024 * 1024  # 1MB
    crc_polynomial: int = 0x04C11DB7
    header_timeout: int = 10
    chunk_size: int = 64 * 1024  # 64KB


@dataclass
class SystemConfig:
    """Complete system configuration."""
    server: ServerConfig
    api_server: APIServerConfig
    crypto: CryptoConfig
    protocol: ProtocolConfig
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration parameters."""
        if self.server.port == self.api_server.port:
            raise ValueError("Server and API server cannot use the same port")
        
        if self.server.port < 1 or self.server.port > 65535:
            raise ValueError(f"Invalid server port: {self.server.port}")
        
        if self.api_server.port < 1 or self.api_server.port > 65535:
            raise ValueError(f"Invalid API server port: {self.api_server.port}")
        
        if self.protocol.max_filename_length < 1:
            raise ValueError("Max filename length must be positive")


class ConfigManager:
    """Centralized configuration manager."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config_file = config_file or "config.json"
        self._config: Optional[SystemConfig] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                self._config = self._dict_to_config(config_data)
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_file}: {e}")
                self._config = self._create_default_config()
        else:
            self._config = self._create_default_config()
            self.save_config()
    
    def _create_default_config(self) -> SystemConfig:
        """Create default configuration."""
        return SystemConfig(
            server=ServerConfig(),
            api_server=APIServerConfig(),
            crypto=CryptoConfig(),
            protocol=ProtocolConfig()
        )
    
    def _dict_to_config(self, config_data: Dict[str, Any]) -> SystemConfig:
        """Convert dictionary to SystemConfig object."""
        return SystemConfig(
            server=ServerConfig(**config_data.get('server', {})),
            api_server=APIServerConfig(**config_data.get('api_server', {})),
            crypto=CryptoConfig(**config_data.get('crypto', {})),
            protocol=ProtocolConfig(**config_data.get('protocol', {}))
        )
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            if self._config is not None:
                config_dict = asdict(self._config)
                with open(self.config_file, 'w') as f:
                    json.dump(config_dict, f, indent=2)
                logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_file}: {e}")
            raise
    
    @property
    def config(self) -> SystemConfig:
        """Get current configuration."""
        if self._config is None:
            self._config = self._create_default_config()
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration parameters."""
        config = self.config  # Use property to ensure non-None config
        config_dict = asdict(config)
        
        for key, value in kwargs.items():
            if '.' in key:
                # Handle nested keys like 'server.port'
                parts = key.split('.')
                current = config_dict
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                config_dict[key] = value
        
        self._config = self._dict_to_config(config_dict)
        self.save_config()
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        try:
            config = self.config  # Use property to ensure non-None config  
            if '.' not in key:
                return getattr(config, key, default)
            parts = key.split('.')
            current = asdict(config)
            for part in parts:
                current = current[part]
            return current
        except (KeyError, AttributeError):
            return default
    
    def reload_config(self):
        """Reload configuration from file."""
        self._load_config()


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_file: Optional[str] = None) -> ConfigManager:
    """
    Get global configuration manager instance.
    
    Args:
        config_file: Path to configuration file (only used on first call)
        
    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    return _config_manager


def get_config() -> SystemConfig:
    """Get current system configuration."""
    return get_config_manager().config


def get_server_config() -> ServerConfig:
    """Get server configuration."""
    return get_config().server


def get_api_server_config() -> APIServerConfig:
    """Get API server configuration."""
    return get_config().api_server


def get_crypto_config() -> CryptoConfig:
    """Get crypto configuration."""
    return get_config().crypto


def get_protocol_config() -> ProtocolConfig:
    """Get protocol configuration."""
    return get_config().protocol


# Legacy compatibility functions
def load_port_from_file(filename: str = "port.info") -> int:
    """
    Legacy function to load port from file.
    
    DEPRECATED: Use get_server_config().port instead.
    """
    logger.warning("load_port_from_file() is deprecated, use get_server_config().port instead")
    try:
        with open(filename, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return get_server_config().port


def get_database_path() -> str:
    """Get database file path."""
    return get_server_config().database_path

def get_absolute_database_path() -> str:
    """Get absolute path to the database file for cross-module access."""
    import os
    from pathlib import Path

    # Get the project root (where this file's parent's parent is)
    project_root = Path(__file__).parent.parent
    db_path = project_root / get_server_config().database_path
    return str(db_path.resolve())


def get_received_files_dir() -> str:
    """Get received files directory path."""
    return get_server_config().received_files_dir


def get_keys_dir() -> str:
    """Get keys directory path."""
    return get_crypto_config().keys_dir


# Configuration constants for backward compatibility
DEFAULT_PORT = 1256
DEFAULT_API_PORT = 9090
DEFAULT_BUFFER_SIZE = 8192
DEFAULT_TIMEOUT = 30
MAX_FILENAME_FIELD_SIZE = 255
MAX_ACTUAL_FILENAME_LENGTH = 200

# Protocol constants
VERSION = 3
REQ_REGISTER = 1025
REQ_PUBLIC_KEY = 1026
REQ_SEND_FILE = 1027
REQ_CRC_OK = 1028
REQ_CRC_FAIL = 1029

RESP_REGISTER_SUCCESS = 1600
RESP_REGISTER_FAIL = 1601
RESP_PUBLIC_KEY = 1602
RESP_FILE_CRC = 1603
RESP_FILE_RECEIVED = 1604
RESP_GENERIC_SERVER_ERROR = 1605


def initialize_config(config_file: Optional[str] = None) -> ConfigManager:
    """
    Initialize global configuration.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        ConfigManager instance
    """
    global _config_manager
    _config_manager = ConfigManager(config_file)
    return _config_manager


def reset_config():
    """Reset global configuration (mainly for testing)."""
    global _config_manager
    _config_manager = None


# Database Integration Functions for FletV2 Compatibility

def get_database_config_for_fletv2() -> Dict[str, Any]:
    """
    Get database configuration optimized for FletV2 GUI integration.

    Returns:
        Dictionary with all database configuration needed by FletV2
    """
    return {
        'database_path': get_absolute_database_path(),
        'database_name': get_server_config().database_path,
        'file_storage_dir': get_received_files_dir(),
        'connection_pool_enabled': True,
        'connection_pool_size': 5,
        'timeout': 10.0,
        'max_connection_age': 3600.0,
        'cleanup_interval': 300.0,
        # Additional compatibility settings
        'use_blob_uuids': True,  # BackupServer uses BLOB UUIDs
        'schema_version': 'backupserver_v3',
        'migration_enabled': True
    }

def is_database_compatible() -> bool:
    """
    Check if the database exists and is accessible.

    Returns:
        True if database file exists and is readable
    """
    import os
    try:
        db_path = get_absolute_database_path()
        return os.path.exists(db_path) and os.access(db_path, os.R_OK)
    except Exception:
        return False

def get_database_schema_info() -> Dict[str, Any]:
    """
    Get information about the database schema for compatibility checking.

    Returns:
        Dictionary with schema information
    """
    return {
        'version': 3,
        'tables': ['clients', 'files'],
        'id_format': 'blob_uuid',  # BackupServer uses BLOB UUIDs
        'client_id_column': 'ID',  # BackupServer column name
        'file_client_ref': 'ClientID',  # BackupServer foreign key column
        'supports_migrations': True,
        'pool_compatible': True
    }
