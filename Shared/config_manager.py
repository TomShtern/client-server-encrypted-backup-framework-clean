"""
Production Configuration Management System
Centralized configuration with validation and environment support
"""

import json
import logging
from pathlib import Path
from typing import Any


class ConfigurationManager:
    """
    Production-grade configuration management system.
    Supports multiple environments, validation, and fallback values.
    """

    def __init__(self, config_dir: str = "config", environment: str = "production"):
        self.config_dir = Path(config_dir)
        self.environment = environment
        self.config_data: dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)

        # Load configuration
        self.load_configuration()

    def load_configuration(self) -> None:
        """Load configuration files in order of priority"""
        config_files = [
            "default.json",  # Base configuration
            f"{self.environment}.json",  # Environment-specific
            "local.json"  # Local overrides (not in version control)
        ]

        for config_file in config_files:
            config_path = self.config_dir / config_file
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        file_config = json.load(f)

                    # Merge configuration (later files override earlier ones)
                    self._deep_merge(self.config_data, file_config)
                    self.logger.info(f"Loaded configuration from {config_file}")

                except Exception as e:
                    self.logger.error(f"Failed to load configuration from {config_file}: {e}")

    def _deep_merge(self, base: dict[str, Any], update: dict[str, Any]) -> None:
        """Deep merge two dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'server.port')"""
        keys = key.split('.')
        value: Any = self.config_data

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        target: Any = self.config_data

        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        target[keys[-1]] = value

    def validate_configuration(self) -> list[str]:
        """Validate configuration and return list of errors"""
        errors: list[str] = []

        # Define required configuration keys and their types
        required_configs = {
            'server.port': int,
            'server.host': str,
            'server.max_clients': int,
            'server.timeout': int,
            'client.retry_attempts': int,
            'client.timeout': int,
            'encryption.rsa_key_size': int,
            'encryption.aes_key_size': int,
            'logging.level': str,
            'logging.file': str
        }

        for key, expected_type in required_configs.items():
            value = self.get(key)
            if value is None:
                errors.append(f"Missing required configuration: {key}")
            elif not isinstance(value, expected_type):
                type_name = getattr(expected_type, '__name__', str(expected_type))
                actual_type_name = getattr(type(value), '__name__', str(type(value)))
                errors.append(f"Invalid type for {key}: expected {type_name}, got {actual_type_name}")

        # Additional validation
        port = self.get('server.port', 0)
        if isinstance(port, int) and (port <= 0 or port > 65535):
            errors.append(f"Invalid server port: {port} (must be 1-65535)")

        max_clients = self.get('server.max_clients', 0)
        if isinstance(max_clients, int) and max_clients <= 0:
            errors.append(f"Invalid max_clients: {max_clients} (must be > 0)")

        return errors

    def save_configuration(self, filename: str | None = None) -> None:
        """Save current configuration to a file"""
        if filename is None:
            filename = f"{self.environment}.json"

        config_path = self.config_dir / filename
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            self.logger.info(f"Configuration saved to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {filename}: {e}")

    def create_default_configs(self) -> None:
        """Create default configuration files"""

        # Default configuration
        default_config = {
            "server": {
                "host": "localhost",
                "port": 1256,
                "max_clients": 50,
                "timeout": 60,
                "file_storage_dir": "received_files",
                "database_name": "defensive.db"
            },
            "client": {
                "retry_attempts": 3,
                "timeout": 30,
                "reconnect_delay": 5,
                "chunk_size": 65536
            },
            "encryption": {
                "rsa_key_size": 1024,
                "aes_key_size": 256
            },
            "logging": {
                "level": "INFO",
                "file": "application.log",
                "max_file_size": "10MB",
                "backup_count": 5
            },
            "performance": {
                "maintenance_interval": 60,
                "cleanup_old_files": True,
                "max_file_age_days": 30
            }
        }

        # Production configuration
        production_config = {
            "logging": {
                "level": "WARNING"
            },
            "server": {
                "timeout": 120
            }
        }

        # Development configuration
        development_config = {
            "logging": {
                "level": "DEBUG"
            },
            "server": {
                "max_clients": 10
            }
        }

        # Save configuration files
        configs = [
            ("default.json", default_config),
            ("production.json", production_config),
            ("development.json", development_config)
        ]

        for filename, config in configs:
            config_path = self.config_dir / filename
            if not config_path.exists():
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"Created {filename}")

def create_production_configs():
    """Create production-ready configuration files"""
    config_manager = ConfigurationManager()
    config_manager.create_default_configs()

    # Reload configuration after creating files
    config_manager.load_configuration()

    # Validate configuration
    errors = config_manager.validate_configuration()
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration validation passed!")

    return config_manager

if __name__ == "__main__":
    print("Creating production configuration files...")
    config_manager = create_production_configs()
    print("Configuration system ready!")
