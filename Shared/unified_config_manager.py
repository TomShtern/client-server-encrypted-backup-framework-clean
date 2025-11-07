"""
Unified Configuration Manager for CyberBackup 3.0
Addresses configuration consolidation issues across multiple sources:

Precedence (highest to lowest):
1. Environment variables (runtime overrides)
2. config.local.json (local overrides, gitignored)
3. config.json (base defaults, committed)
4. .env files (development secrets)
5. FletV2/.env (Flet-specific settings)

This replaces the fragmented configuration approach with a single source of truth.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ServerConfig:
    """Server configuration with defaults from config.json"""
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
class ApiServerConfig:
    """API server configuration with defaults from config.json"""
    host: str = "127.0.0.1"
    port: int = 9090
    debug: bool = False
    max_content_length: int = 16777216
    upload_timeout: int = 300
    enable_cors: bool = True

@dataclass
class CryptoConfig:
    """Cryptography configuration with defaults from config.json"""
    rsa_key_size: int = 2048
    aes_key_size: int = 256
    private_key_file: str = "priv.key"
    public_key_file: str = "valid_public_key.der"
    keys_dir: str = "data/keys"
    enable_compression: bool = True

@dataclass
class ProtocolConfig:
    """Protocol configuration with defaults from config.json"""
    version: int = 3
    max_filename_length: int = 200
    max_payload_size: int = 1048576
    crc_polynomial: int = 79764919
    header_timeout: int = 10
    chunk_size: int = 65536

@dataclass
class DevelopmentConfig:
    """Development configuration from .env files"""
    flet_development: bool = False
    flet_debug: bool = False
    disable_integrated_gui: bool = False
    gui_only_mode: bool = False
    pythonioencoding: str = "utf-8"
    pythonpath: str = "..;../Shared"

@dataclass
class SecurityConfig:
    """Security configuration (secrets) from environment variables"""
    github_personal_access_token: Optional[str] = None
    server_api_key: Optional[str] = None
    database_password: Optional[str] = None

@dataclass
class CyberBackupConfig:
    """Main configuration container"""
    server: ServerConfig = field(default_factory=ServerConfig)
    api_server: ApiServerConfig = field(default_factory=ApiServerConfig)
    crypto: CryptoConfig = field(default_factory=CryptoConfig)
    protocol: ProtocolConfig = field(default_factory=ProtocolConfig)
    development: DevelopmentConfig = field(default_factory=DevelopmentConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

class ConfigurationError(Exception):
    """Configuration-related errors"""
    pass

class UnifiedConfigurationManager:
    """
    Unified configuration manager that consolidates all configuration sources.

    Addresses the issue from FUNCTIONAL_ISSUES_REPORT.md about configuration
    being split across 4 different files with overlapping concerns.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize unified configuration manager

        Args:
            base_dir: Base directory for config files. Defaults to current working directory.
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()

        # Configuration file paths (from the report)
        self.config_file = self.base_dir / "config.json"
        self.local_config_file = self.base_dir / "config.local.json"
        self.env_file = self.base_dir / ".env"
        self.flet_env_file = self.base_dir / "FletV2" / ".env"

        self._config: Optional[CyberBackupConfig] = None
        self._config_hash: Optional[str] = None

        logger.debug(f"Unified configuration manager initialized with base directory: {self.base_dir}")

    def load(self, force_reload: bool = False) -> CyberBackupConfig:
        """
        Load configuration from all sources with proper precedence

        Args:
            force_reload: Force reload even if config hasn't changed

        Returns:
            CyberBackupConfig: Loaded configuration
        """
        if not force_reload and self._config and self._is_config_unchanged():
            return self._config

        try:
            # 1. Load base configuration from config.json
            config_data = self._load_base_config()

            # 2. Apply local overrides from config.local.json
            local_overrides = self._load_local_config()
            if local_overrides:
                config_data = self._merge_configs(config_data, local_overrides)
                logger.debug("Applied local configuration overrides from config.local.json")

            # 3. Load environment variables from .env files
            self._load_env_files()

            # 4. Apply environment variable overrides
            env_overrides = self._load_env_overrides()
            if env_overrides:
                config_data = self._merge_configs(config_data, env_overrides)
                logger.debug("Applied environment variable overrides")

            # 5. Create configuration object
            self._config = self._create_config_from_dict(config_data)
            self._config_hash = self._calculate_config_hash(config_data)

            logger.info("Unified configuration loaded successfully")
            return self._config

        except Exception as e:
            logger.error(f"Failed to load unified configuration: {e}")
            raise ConfigurationError(f"Failed to load unified configuration: {e}")

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value

        Args:
            section: Configuration section (e.g., 'server', 'api_server')
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        config = self.load()
        section_obj = getattr(config, section, None)
        if not section_obj:
            return default

        return getattr(section_obj, key, default)

    def set(self, section: str, key: str, value: Any, persist: bool = False) -> None:
        """
        Set a configuration value

        Args:
            section: Configuration section
            key: Configuration key
            value: New value
            persist: Whether to persist to local config file
        """
        config = self.load()
        section_obj = getattr(config, section, None)
        if not section_obj:
            raise ConfigurationError(f"Unknown configuration section: {section}")

        setattr(section_obj, key, value)

        if persist:
            self._save_local_config(config)
            logger.info(f"Saved {section}.{key} to config.local.json")

    def reload(self) -> CyberBackupConfig:
        """Force reload configuration"""
        return self.load(force_reload=True)

    def get_config_sources(self) -> Dict[str, bool]:
        """Get status of all configuration sources"""
        return {
            "config.json": self.config_file.exists(),
            "config.local.json": self.local_config_file.exists(),
            ".env": self.env_file.exists(),
            "FletV2/.env": self.flet_env_file.exists()
        }

    def validate_configuration(self) -> list[str]:
        """Validate loaded configuration and return list of errors"""
        config = self.load()
        errors = []

        # Validate server configuration
        if not (1 <= config.server.port <= 65535):
            errors.append(f"Invalid server port: {config.server.port} (must be 1-65535)")

        if config.server.max_connections <= 0:
            errors.append(f"Invalid max_connections: {config.server.max_connections} (must be > 0)")

        # Validate API server configuration
        if not (1 <= config.api_server.port <= 65535):
            errors.append(f"Invalid API server port: {config.api_server.port} (must be 1-65535)")

        # Validate crypto configuration
        if config.crypto.rsa_key_size not in [1024, 2048, 4096]:
            errors.append(f"Invalid RSA key size: {config.crypto.rsa_key_size} (should be 1024, 2048, or 4096)")

        if config.crypto.aes_key_size not in [128, 192, 256]:
            errors.append(f"Invalid AES key size: {config.crypto.aes_key_size} (should be 128, 192, or 256)")

        # Validate protocol configuration
        if config.protocol.max_filename_length <= 0:
            errors.append(f"Invalid max filename length: {config.protocol.max_filename_length} (must be > 0)")

        if config.protocol.max_payload_size <= 0:
            errors.append(f"Invalid max payload size: {config.protocol.max_payload_size} (must be > 0)")

        return errors

    def _load_base_config(self) -> Dict[str, Any]:
        """Load base configuration from config.json"""
        if not self.config_file.exists():
            logger.warning(f"Base config file not found: {self.config_file}")
            return {}

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.debug(f"Loaded base configuration from config.json")
            return config
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in config.json: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to read config.json: {e}")

    def _load_local_config(self) -> Dict[str, Any]:
        """Load local configuration overrides from config.local.json"""
        if not self.local_config_file.exists():
            return {}

        try:
            with open(self.local_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.debug(f"Loaded local configuration from config.local.json")
            return config
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in config.local.json, ignoring: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Failed to read config.local.json, ignoring: {e}")
            return {}

    def _load_env_files(self) -> None:
        """Load environment variables from .env files"""
        env_files = [self.env_file, self.flet_env_file]

        for env_file in env_files:
            if env_file.exists():
                try:
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()

                                # Remove quotes if present
                                if (value.startswith('"') and value.endswith('"')) or \
                                   (value.startswith("'") and value.endswith("'")):
                                    value = value[1:-1]

                                os.environ[key] = value

                    logger.debug(f"Loaded environment variables from {env_file}")
                except Exception as e:
                    logger.warning(f"Failed to load {env_file}: {e}")

    def _load_env_overrides(self) -> Dict[str, Any]:
        """Load configuration overrides from environment variables"""
        overrides = {}

        # Server configuration overrides
        if 'SERVER_HOST' in os.environ:
            overrides.setdefault('server', {})['host'] = os.environ['SERVER_HOST']
        if 'SERVER_PORT' in os.environ:
            overrides.setdefault('server', {})['port'] = int(os.environ['SERVER_PORT'])
        if 'MAX_CONNECTIONS' in os.environ:
            overrides.setdefault('server', {})['max_connections'] = int(os.environ['MAX_CONNECTIONS'])
        if 'DATABASE_PATH' in os.environ:
            overrides.setdefault('server', {})['database_path'] = os.environ['DATABASE_PATH']

        # API server configuration overrides
        if 'API_HOST' in os.environ:
            overrides.setdefault('api_server', {})['host'] = os.environ['API_HOST']
        if 'API_PORT' in os.environ:
            overrides.setdefault('api_server', {})['port'] = int(os.environ['API_PORT'])
        if 'API_DEBUG' in os.environ:
            overrides.setdefault('api_server', {})['debug'] = os.environ['API_DEBUG'].lower() == 'true'

        # Development configuration overrides
        if 'FLET_DEVELOPMENT' in os.environ:
            overrides.setdefault('development', {})['flet_development'] = os.environ['FLET_DEVELOPMENT'].lower() == 'true'
        if 'FLET_DEBUG' in os.environ:
            overrides.setdefault('development', {})['flet_debug'] = os.environ['FLET_DEBUG'].lower() == 'true'
        if 'FLET_V2_DEBUG' in os.environ:
            overrides.setdefault('development', {})['flet_debug'] = os.environ['FLET_V2_DEBUG'].lower() == 'true'
        if 'CYBERBACKUP_DISABLE_INTEGRATED_GUI' in os.environ:
            overrides.setdefault('development', {})['disable_integrated_gui'] = os.environ['CYBERBACKUP_DISABLE_INTEGRATED_GUI'].lower() == 'true'
        if 'FLET_GUI_ONLY_MODE' in os.environ:
            overrides.setdefault('development', {})['gui_only_mode'] = os.environ['FLET_GUI_ONLY_MODE'].lower() == 'true'
        if 'PYTHONIOENCODING' in os.environ:
            overrides.setdefault('development', {})['pythonioencoding'] = os.environ['PYTHONIOENCODING']
        if 'PYTHONPATH' in os.environ:
            overrides.setdefault('development', {})['pythonpath'] = os.environ['PYTHONPATH']

        # Security configuration overrides (secrets)
        if 'GITHUB_PERSONAL_ACCESS_TOKEN' in os.environ:
            overrides.setdefault('security', {})['github_personal_access_token'] = os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']
        if 'SERVER_API_KEY' in os.environ:
            overrides.setdefault('security', {})['server_api_key'] = os.environ['SERVER_API_KEY']
        if 'DATABASE_PASSWORD' in os.environ:
            overrides.setdefault('security', {})['database_password'] = os.environ['DATABASE_PASSWORD']

        return overrides

    def _merge_configs(self, base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries"""
        result = base.copy()

        for key, value in overrides.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _create_config_from_dict(self, config_data: Dict[str, Any]) -> CyberBackupConfig:
        """Create configuration object from dictionary"""
        try:
            return CyberBackupConfig(
                server=ServerConfig(**config_data.get('server', {})),
                api_server=ApiServerConfig(**config_data.get('api_server', {})),
                crypto=CryptoConfig(**config_data.get('crypto', {})),
                protocol=ProtocolConfig(**config_data.get('protocol', {})),
                development=DevelopmentConfig(**config_data.get('development', {})),
                security=SecurityConfig(**config_data.get('security', {}))
            )
        except TypeError as e:
            raise ConfigurationError(f"Invalid configuration structure: {e}")

    def _save_local_config(self, config: CyberBackupConfig) -> None:
        """Save configuration to config.local.json (excluding secrets)"""
        try:
            config_dict = {
                'server': {
                    'host': config.server.host,
                    'port': config.server.port,
                    'max_connections': config.server.max_connections,
                    'buffer_size': config.server.buffer_size,
                    'timeout': config.server.timeout,
                    'enable_logging': config.server.enable_logging,
                    'log_level': config.server.log_level,
                    'database_path': config.server.database_path,
                    'received_files_dir': config.server.received_files_dir,
                    'keys_dir': config.server.keys_dir
                },
                'api_server': {
                    'host': config.api_server.host,
                    'port': config.api_server.port,
                    'debug': config.api_server.debug,
                    'max_content_length': config.api_server.max_content_length,
                    'upload_timeout': config.api_server.upload_timeout,
                    'enable_cors': config.api_server.enable_cors
                },
                'crypto': {
                    'rsa_key_size': config.crypto.rsa_key_size,
                    'aes_key_size': config.crypto.aes_key_size,
                    'private_key_file': config.crypto.private_key_file,
                    'public_key_file': config.crypto.public_key_file,
                    'keys_dir': config.crypto.keys_dir,
                    'enable_compression': config.crypto.enable_compression
                },
                'protocol': {
                    'version': config.protocol.version,
                    'max_filename_length': config.protocol.max_filename_length,
                    'max_payload_size': config.protocol.max_payload_size,
                    'crc_polynomial': config.protocol.crc_polynomial,
                    'header_timeout': config.protocol.header_timeout,
                    'chunk_size': config.protocol.chunk_size
                },
                'development': {
                    'flet_development': config.development.flet_development,
                    'flet_debug': config.development.flet_debug,
                    'disable_integrated_gui': config.development.disable_integrated_gui,
                    'gui_only_mode': config.development.gui_only_mode,
                    'pythonioencoding': config.development.pythonioencoding,
                    'pythonpath': config.development.pythonpath
                }
                # Note: Security section (secrets) is NOT saved to config file
            }

            with open(self.local_config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved configuration to config.local.json")

        except Exception as e:
            raise ConfigurationError(f"Failed to save local configuration: {e}")

    def _is_config_unchanged(self) -> bool:
        """Check if configuration files have changed since last load"""
        if not self._config_hash:
            return False

        try:
            current_hash = self._calculate_config_hash(self._load_base_config())
            return current_hash == self._config_hash
        except:
            return False

    def _calculate_config_hash(self, config_data: Dict[str, Any]) -> str:
        """Calculate hash of configuration data"""
        import hashlib
        config_str = json.dumps(config_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(config_str.encode('utf-8')).hexdigest()

    def get_server_url(self) -> str:
        """Get complete server URL"""
        config = self.load()
        return f"http://{config.server.host}:{config.server.port}"

    def get_api_server_url(self) -> str:
        """Get complete API server URL"""
        config = self.load()
        return f"http://{config.api_server.host}:{config.api_server.port}"

    def is_development_mode(self) -> bool:
        """Check if running in development mode"""
        config = self.load()
        return config.development.flet_development or config.development.flet_debug

    def get_database_path(self) -> Path:
        """Get absolute database path"""
        config = self.load()
        return self.base_dir / config.server.database_path

    def get_keys_directory(self) -> Path:
        """Get absolute keys directory path"""
        config = self.load()
        return self.base_dir / config.crypto.keys_dir

    def get_received_files_directory(self) -> Path:
        """Get absolute received files directory path"""
        config = self.load()
        return self.base_dir / config.server.received_files_dir

# Global unified configuration manager instance
_unified_config_manager: Optional[UnifiedConfigurationManager] = None

def get_unified_config_manager(base_dir: Optional[str] = None) -> UnifiedConfigurationManager:
    """Get global unified configuration manager instance"""
    global _unified_config_manager
    if _unified_config_manager is None:
        _unified_config_manager = UnifiedConfigurationManager(base_dir)
    return _unified_config_manager

def load_unified_config(base_dir: Optional[str] = None) -> CyberBackupConfig:
    """Load unified configuration using global manager"""
    return get_unified_config_manager(base_dir).load()

def get_unified_config(section: str, key: str, default: Any = None) -> Any:
    """Get unified configuration value using global manager"""
    return get_unified_config_manager().get(section, key, default)

# Convenience functions for common configuration values
def get_server_config() -> ServerConfig:
    """Get server configuration"""
    return load_unified_config().server

def get_api_server_config() -> ApiServerConfig:
    """Get API server configuration"""
    return load_unified_config().api_server

def get_crypto_config() -> CryptoConfig:
    """Get crypto configuration"""
    return load_unified_config().crypto

def get_protocol_config() -> ProtocolConfig:
    """Get protocol configuration"""
    return load_unified_config().protocol

def is_development() -> bool:
    """Check if in development mode"""
    return load_unified_config().development.flet_development

if __name__ == "__main__":
    # Example usage
    config_manager = UnifiedConfigurationManager()
    config = config_manager.load()

    print("Unified Configuration Manager Demo")
    print("================================")
    print(f"Config sources: {config_manager.get_config_sources()}")
    print(f"Server URL: {config_manager.get_server_url()}")
    print(f"API Server URL: {config_manager.get_api_server_url()}")
    print(f"Development mode: {config_manager.is_development_mode()}")

    # Validate configuration
    errors = config_manager.validate_configuration()
    if errors:
        print("\nConfiguration validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\nConfiguration validation passed!")