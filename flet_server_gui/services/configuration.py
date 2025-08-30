#!/usr/bin/env python3
"""
Purpose: Settings management and persistence
Logic: Configuration CRUD, validation, import/export
UI: None - pure service layer
"""

import os
import json
import logging
from typing import Dict, Any, Callable, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from enum import Enum

# Enable UTF-8 support
try:
    import Shared.utils.utf8_solution
except ImportError:
    pass

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION ENUMS AND CONSTANTS
# ============================================================================

class SettingsCategory(Enum):
    """Settings categories for organization."""
    SERVER = "server"
    GUI = "gui"
    MONITORING = "monitoring"
    ADVANCED = "advanced"

class ValidationError(Exception):
    """Exception raised when settings validation fails."""
    pass

# ============================================================================
# MAIN CONFIGURATION SERVICE (consolidated from settings_manager.py)
# ============================================================================

class ConfigurationService:
    """
    Comprehensive settings management with unified configuration integration.
    NO mock data - all settings are persisted and validated.
    Consolidates functionality from multiple settings-related files.
    """
    
    def __init__(self):
        """Initialize with real configuration paths and validation"""
        self.settings_file = Path("flet_server_gui_settings.json")
        self.config_watchers: List[Callable[[Dict[str, Any]], None]] = []
        
        # Import unified config if available, fallback to direct JSON
        try:
            from Shared.utils.unified_config import get_unified_config
            self.unified_config = get_unified_config()
            self.use_unified = True
            logger.info("✅ Using unified configuration system")
        except ImportError:
            self.unified_config = None
            self.use_unified = False
            logger.warning("⚠️ Unified config not available, using direct JSON")
        
        # Default server settings based on TKinter analysis
        self.default_settings = {
            'server': {
                'port': 1256,
                'host': '127.0.0.1',
                'storage_dir': 'received_files',
                'max_clients': 50,
                'session_timeout': 10,
                'maintenance_interval': 60,
                'auto_start': False,
                'log_level': 'INFO'
            },
            'gui': {
                'theme_mode': 'dark',
                'auto_refresh_interval': 5,
                'show_notifications': True,
                'last_tab': 'dashboard',
                'window_maximized': False,
                'confirm_deletions': True
            },
            'monitoring': {
                'enable_system_monitoring': True,
                'monitoring_interval': 2,
                'history_retention_days': 7,
                'performance_alerts': True,
                'alert_thresholds': {
                    'cpu_percent': 80,
                    'memory_percent': 85,
                    'disk_percent': 90
                }
            },
            'advanced': {
                'backup_frequency': 'weekly',
                'cleanup_old_files': False,
                'cleanup_days': 30,
                'debug_mode': False
            }
        }
        
        # Change tracking
        self._original_settings = {}
        self._current_settings = {}
        self._has_changes = False
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load real settings from unified config or JSON file.
        Returns validated settings with proper defaults.
        """
        try:
            if self.use_unified and self.unified_config:
                settings = self._load_from_unified_config()
            else:
                settings = self._load_from_json_file()
            
            # Update internal state for change tracking
            self._original_settings = settings.copy()
            self._current_settings = settings.copy()
            self._has_changes = False
            
            return settings
        except Exception as e:
            logger.error(f"❌ Failed to load settings: {e}")
            default_copy = self.default_settings.copy()
            self._original_settings = default_copy.copy()
            self._current_settings = default_copy.copy()
            self._has_changes = False
            return default_copy
    
    def _load_from_unified_config(self) -> Dict[str, Any]:
        """Load settings from unified configuration system"""
        settings = {
            'server': {
                'port': self.unified_config.get(
                    'server.port', self.default_settings['server']['port']
                ),
                'host': self.unified_config.get(
                    'server.host', self.default_settings['server']['host']
                ),
                'storage_dir': self.unified_config.get(
                    'server.file_storage_dir',
                    self.default_settings['server']['storage_dir'],
                ),
                'max_clients': self.unified_config.get(
                    'server.max_clients',
                    self.default_settings['server']['max_clients'],
                ),
                'session_timeout': self.unified_config.get(
                    'server.session_timeout',
                    self.default_settings['server']['session_timeout'],
                ),
                'maintenance_interval': self.unified_config.get(
                    'server.maintenance_interval',
                    self.default_settings['server']['maintenance_interval'],
                ),
                'auto_start': self.unified_config.get(
                    'server.auto_start',
                    self.default_settings['server']['auto_start'],
                ),
                'log_level': self.unified_config.get(
                    'server.log_level',
                    self.default_settings['server']['log_level'],
                ),
            }
        }

        # GUI settings
        settings['gui'] = {
            'theme_mode': self.unified_config.get('gui.theme_mode', self.default_settings['gui']['theme_mode']),
            'auto_refresh_interval': self.unified_config.get('gui.auto_refresh_interval', self.default_settings['gui']['auto_refresh_interval']),
            'show_notifications': self.unified_config.get('gui.show_notifications', self.default_settings['gui']['show_notifications']),
            'last_tab': self.unified_config.get('gui.last_tab', self.default_settings['gui']['last_tab']),
            'window_maximized': self.unified_config.get('gui.window_maximized', self.default_settings['gui']['window_maximized']),
            'confirm_deletions': self.unified_config.get('gui.confirm_deletions', self.default_settings['gui']['confirm_deletions'])
        }

        # Monitoring settings
        settings['monitoring'] = {
            'enable_system_monitoring': self.unified_config.get('monitoring.enable_system_monitoring', self.default_settings['monitoring']['enable_system_monitoring']),
            'monitoring_interval': self.unified_config.get('monitoring.monitoring_interval', self.default_settings['monitoring']['monitoring_interval']),
            'history_retention_days': self.unified_config.get('monitoring.history_retention_days', self.default_settings['monitoring']['history_retention_days']),
            'performance_alerts': self.unified_config.get('monitoring.performance_alerts', self.default_settings['monitoring']['performance_alerts']),
            'alert_thresholds': {
                'cpu_percent': self.unified_config.get('monitoring.alert_thresholds.cpu_percent', self.default_settings['monitoring']['alert_thresholds']['cpu_percent']),
                'memory_percent': self.unified_config.get('monitoring.alert_thresholds.memory_percent', self.default_settings['monitoring']['alert_thresholds']['memory_percent']),
                'disk_percent': self.unified_config.get('monitoring.alert_thresholds.disk_percent', self.default_settings['monitoring']['alert_thresholds']['disk_percent'])
            }
        }

        # Advanced settings
        settings['advanced'] = {
            'backup_frequency': self.unified_config.get('advanced.backup_frequency', self.default_settings['advanced']['backup_frequency']),
            'cleanup_old_files': self.unified_config.get('advanced.cleanup_old_files', self.default_settings['advanced']['cleanup_old_files']),
            'cleanup_days': self.unified_config.get('advanced.cleanup_days', self.default_settings['advanced']['cleanup_days']),
            'debug_mode': self.unified_config.get('advanced.debug_mode', self.default_settings['advanced']['debug_mode'])
        }

        logger.info("✅ Settings loaded from unified configuration")
        return settings
    
    def _load_from_json_file(self) -> Dict[str, Any]:
        """Load settings from JSON file fallback"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    stored_settings = json.load(f)
                
                # Merge with defaults to ensure all settings exist
                settings = self._merge_with_defaults(stored_settings)
                logger.info(f"✅ Settings loaded from {self.settings_file}")
                return settings
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"❌ Failed to load settings file: {e}")
        
        # Return defaults if file doesn't exist or is corrupt
        logger.info("ℹ️ Using default settings")
        return self.default_settings.copy()
    
    def _merge_with_defaults(self, stored_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Merge stored settings with defaults to ensure completeness"""
        merged = self.default_settings.copy()
        
        for category, settings in stored_settings.items():
            if category in merged and isinstance(settings, dict):
                if isinstance(merged[category], dict):
                    merged[category].update(settings)
                else:
                    merged[category] = settings
        
        return merged
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save real settings to unified config or JSON file.
        Validates settings before saving.
        """
        try:
            # Validate settings first
            validated_settings = self._validate_settings(settings)
            
            if self.use_unified and self.unified_config:
                success = self._save_to_unified_config(validated_settings)
            else:
                success = self._save_to_json_file(validated_settings)
            
            if success:
                # Update internal state
                self._original_settings = validated_settings.copy()
                self._current_settings = validated_settings.copy()
                self._has_changes = False
                
            return success
        except Exception as e:
            logger.error(f"❌ Failed to save settings: {e}")
            return False
    
    def _save_to_unified_config(self, settings: Dict[str, Any]) -> bool:
        """Save settings to unified configuration system"""
        try:
            # Save server settings
            for key, value in settings['server'].items():
                config_key = f'server.{key}' if key != 'storage_dir' else 'server.file_storage_dir'
                self.unified_config.set(config_key, value, persist=True)
            
            # Save GUI settings  
            for key, value in settings['gui'].items():
                self.unified_config.set(f'gui.{key}', value, persist=True)
            
            # Save monitoring settings
            for key, value in settings['monitoring'].items():
                if key == 'alert_thresholds':
                    for threshold_key, threshold_value in value.items():
                        self.unified_config.set(f'monitoring.alert_thresholds.{threshold_key}', threshold_value, persist=True)
                else:
                    self.unified_config.set(f'monitoring.{key}', value, persist=True)
            
            # Save advanced settings
            for key, value in settings['advanced'].items():
                self.unified_config.set(f'advanced.{key}', value, persist=True)
            
            logger.info("✅ Settings saved to unified configuration")
            self._notify_watchers(settings)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save to unified config: {e}")
            return False
    
    def _save_to_json_file(self, settings: Dict[str, Any]) -> bool:
        """Save settings to JSON file fallback"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Settings saved to {self.settings_file}")
            self._notify_watchers(settings)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save settings file: {e}")
            return False
    
    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate settings with proper type conversion and range checking.
        Returns validated settings or raises ValidationError.
        """
        validated = {}
        
        # Validate server settings
        if 'server' in settings:
            validated['server'] = {}
            server = settings['server']
            
            # Port validation
            port = int(server.get('port', self.default_settings['server']['port']))
            if not (1024 <= port <= 65535):
                raise ValidationError(f"Port {port} must be between 1024 and 65535")
            validated['server']['port'] = port
            
            # Host validation
            host = str(server.get('host', self.default_settings['server']['host']))
            if not host.strip():
                raise ValidationError("Host cannot be empty")
            validated['server']['host'] = host.strip()
            
            # Storage directory validation
            storage_dir = str(server.get('storage_dir', self.default_settings['server']['storage_dir']))
            if not storage_dir.strip():
                raise ValidationError("Storage directory cannot be empty")
            validated['server']['storage_dir'] = storage_dir.strip()
            
            # Numeric validations
            max_clients = int(server.get('max_clients', self.default_settings['server']['max_clients']))
            if not (1 <= max_clients <= 1000):
                raise ValidationError("Max clients must be between 1 and 1000")
            validated['server']['max_clients'] = max_clients
            
            session_timeout = int(server.get('session_timeout', self.default_settings['server']['session_timeout']))
            if not (1 <= session_timeout <= 1440):  # 1 minute to 24 hours
                raise ValidationError("Session timeout must be between 1 and 1440 minutes")
            validated['server']['session_timeout'] = session_timeout
            
            maintenance_interval = int(server.get('maintenance_interval', self.default_settings['server']['maintenance_interval']))
            if not (10 <= maintenance_interval <= 3600):  # 10 seconds to 1 hour
                raise ValidationError("Maintenance interval must be between 10 and 3600 seconds")
            validated['server']['maintenance_interval'] = maintenance_interval
            
            # Boolean settings
            validated['server']['auto_start'] = bool(server.get('auto_start', self.default_settings['server']['auto_start']))
            
            # Log level validation
            log_level = str(server.get('log_level', self.default_settings['server']['log_level'])).upper()
            if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                raise ValidationError("Log level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
            validated['server']['log_level'] = log_level
        
        # Validate GUI settings
        if 'gui' in settings:
            validated['gui'] = {}
            gui = settings['gui']
            
            # Theme validation
            theme_mode = str(gui.get('theme_mode', self.default_settings['gui']['theme_mode'])).lower()
            if theme_mode not in ['light', 'dark', 'system']:
                raise ValidationError("Theme mode must be light, dark, or system")
            validated['gui']['theme_mode'] = theme_mode
            
            # Auto refresh interval
            auto_refresh = int(gui.get('auto_refresh_interval', self.default_settings['gui']['auto_refresh_interval']))
            if not (1 <= auto_refresh <= 60):
                raise ValidationError("Auto refresh interval must be between 1 and 60 seconds")
            validated['gui']['auto_refresh_interval'] = auto_refresh
            
            # Boolean settings
            validated['gui']['show_notifications'] = bool(gui.get('show_notifications', self.default_settings['gui']['show_notifications']))
            validated['gui']['window_maximized'] = bool(gui.get('window_maximized', self.default_settings['gui']['window_maximized']))
            validated['gui']['confirm_deletions'] = bool(gui.get('confirm_deletions', self.default_settings['gui']['confirm_deletions']))
            
            # Last tab
            validated['gui']['last_tab'] = str(gui.get('last_tab', self.default_settings['gui']['last_tab']))
        
        # Validate monitoring settings
        if 'monitoring' in settings:
            validated['monitoring'] = {}
            monitoring = settings['monitoring']
            
            # Boolean settings
            validated['monitoring']['enable_system_monitoring'] = bool(monitoring.get('enable_system_monitoring', self.default_settings['monitoring']['enable_system_monitoring']))
            validated['monitoring']['performance_alerts'] = bool(monitoring.get('performance_alerts', self.default_settings['monitoring']['performance_alerts']))
            
            # Monitoring interval
            interval = int(monitoring.get('monitoring_interval', self.default_settings['monitoring']['monitoring_interval']))
            if not (1 <= interval <= 60):
                raise ValidationError("Monitoring interval must be between 1 and 60 seconds")
            validated['monitoring']['monitoring_interval'] = interval
            
            # History retention
            retention = int(monitoring.get('history_retention_days', self.default_settings['monitoring']['history_retention_days']))
            if not (1 <= retention <= 365):
                raise ValidationError("History retention must be between 1 and 365 days")
            validated['monitoring']['history_retention_days'] = retention
            
            # Alert thresholds
            if 'alert_thresholds' in monitoring:
                validated['monitoring']['alert_thresholds'] = {}
                thresholds = monitoring['alert_thresholds']
                
                for metric in ['cpu_percent', 'memory_percent', 'disk_percent']:
                    value = int(thresholds.get(metric, self.default_settings['monitoring']['alert_thresholds'][metric]))
                    if not (50 <= value <= 99):
                        raise ValidationError(f"{metric} threshold must be between 50 and 99")
                    validated['monitoring']['alert_thresholds'][metric] = value
            else:
                validated['monitoring']['alert_thresholds'] = self.default_settings['monitoring']['alert_thresholds'].copy()
        
        # Validate advanced settings
        if 'advanced' in settings:
            validated['advanced'] = {}
            advanced = settings['advanced']
            
            # Backup frequency validation
            backup_freq = str(advanced.get('backup_frequency', self.default_settings['advanced']['backup_frequency']))
            if backup_freq not in ['daily', 'weekly', 'monthly', 'manual']:
                raise ValidationError("Backup frequency must be daily, weekly, monthly, or manual")
            validated['advanced']['backup_frequency'] = backup_freq
            
            # Boolean settings
            validated['advanced']['cleanup_old_files'] = bool(advanced.get('cleanup_old_files', self.default_settings['advanced']['cleanup_old_files']))
            validated['advanced']['debug_mode'] = bool(advanced.get('debug_mode', self.default_settings['advanced']['debug_mode']))
            
            # Cleanup days validation
            cleanup_days = int(advanced.get('cleanup_days', self.default_settings['advanced']['cleanup_days']))
            if not (1 <= cleanup_days <= 365):
                raise ValidationError("Cleanup days must be between 1 and 365")
            validated['advanced']['cleanup_days'] = cleanup_days
        
        return validated
    
    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """
        Get a specific setting using dot notation.
        Example: get_setting('server.port') or get_setting('gui.theme_mode')
        """
        settings = self._current_settings or self.load_settings()
        keys = key_path.split('.')
        
        current = settings
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set_setting(self, key_path: str, value: Any) -> bool:
        """
        Set a specific setting using dot notation and save.
        Example: set_setting('server.port', 1256)
        """
        if not self._current_settings:
            self._current_settings = self.load_settings()
        
        keys = key_path.split('.')
        
        # Navigate to the parent dict
        current = self._current_settings
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
        
        # Update change tracking
        self._has_changes = self._detect_changes()
        
        # Save the updated settings
        return self.save_settings(self._current_settings)
    
    def add_config_watcher(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a callback to be notified when settings change"""
        if callback not in self.config_watchers:
            self.config_watchers.append(callback)
            logger.info("✅ Config watcher added")
    
    def remove_config_watcher(self, callback: Callable[[Dict[str, Any]], None]):
        """Remove a config watcher callback"""
        if callback in self.config_watchers:
            self.config_watchers.remove(callback)
            logger.info("✅ Config watcher removed")
    
    def _notify_watchers(self, settings: Dict[str, Any]):
        """Notify all watchers of settings changes"""
        for callback in self.config_watchers:
            try:
                callback(settings)
            except Exception as e:
                logger.error(f"❌ Config watcher callback failed: {e}")
    
    def reset_to_defaults(self, category: Optional[str] = None) -> bool:
        """
        Reset settings to defaults.
        If category is specified, only reset that category.
        """
        if category:
            if category not in self.default_settings:
                raise ValidationError(f"Unknown settings category: {category}")

            if not self._current_settings:
                self._current_settings = self.load_settings()

            self._current_settings[category] = self.default_settings[category].copy()
            result = self.save_settings(self._current_settings)

            if result:
                logger.info(f"✅ Settings category '{category}' reset to defaults")
        else:
            # Reset all settings
            result = self.save_settings(self.default_settings.copy())
            if result:
                logger.info("✅ All settings reset to defaults")

        return result
    
    def export_settings(self, file_path: str) -> bool:
        """Export current settings to a JSON file"""
        try:
            settings = self._current_settings or self.load_settings()
            
            export_data = {
                'metadata': {
                    'version': '1.0',
                    'exported_at': datetime.now().isoformat(),
                    'application': 'Flet Server GUI'
                },
                'settings': settings
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Settings exported to {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to export settings: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """Import settings from a JSON file"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Settings file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Extract settings data
            if 'settings' in import_data:
                settings_data = import_data['settings']
            else:
                # Assume direct settings format
                settings_data = import_data
            
            # Validate and save imported settings
            result = self.save_settings(settings_data)
            
            if result:
                logger.info(f"✅ Settings imported from {file_path}")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to import settings: {e}")
            return False
    
    # ========================================================================
    # CHANGE TRACKING (consolidated from settings_change_manager.py)
    # ========================================================================
    
    def _detect_changes(self) -> bool:
        """Detect if current settings differ from original"""
        try:
            for category, current_settings in self._current_settings.items():
                original_settings = self._original_settings.get(category, {})
                if isinstance(current_settings, dict) and isinstance(original_settings, dict):
                    for key, current_value in current_settings.items():
                        original_value = original_settings.get(key)
                        if current_value != original_value:
                            return True
                elif current_settings != original_settings:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error detecting changes: {e}")
            return False
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self._has_changes
    
    def get_changed_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get settings that have changed with before/after values"""
        changes = {}
        
        try:
            for category, current_settings in self._current_settings.items():
                original_settings = self._original_settings.get(category, {})
                if isinstance(current_settings, dict) and isinstance(original_settings, dict):
                    category_changes = {}
                    for key, current_value in current_settings.items():
                        original_value = original_settings.get(key)
                        if current_value != original_value:
                            category_changes[key] = {
                                'original': original_value,
                                'current': current_value
                            }
                    if category_changes:
                        changes[category] = category_changes
                elif current_settings != original_settings:
                    changes[category] = {
                        'original': original_settings,
                        'current': current_settings
                    }
        except Exception as e:
            logger.error(f"Error getting changed settings: {e}")
        
        return changes
    
    def apply_temporary_changes(self, settings: Dict[str, Any]):
        """Apply temporary changes without saving."""
        if not self._current_settings:
            self._current_settings = self.load_settings()
        
        # Deep merge the changes
        for category, category_settings in settings.items():
            if category not in self._current_settings:
                self._current_settings[category] = {}
            
            if isinstance(category_settings, dict):
                self._current_settings[category].update(category_settings)
            else:
                self._current_settings[category] = category_settings
        
        # Update change tracking
        self._has_changes = self._detect_changes()
    
    def discard_changes(self):
        """Discard unsaved changes and revert to original settings."""
        self._current_settings = self._original_settings.copy()
        self._has_changes = False

# ============================================================================
# BACKUP AND RESTORE SERVICE (consolidated from export/import)
# ============================================================================

class SettingsBackupService:
    """Service for creating and managing settings backups."""
    
    def __init__(self, config_service: ConfigurationService):
        self.config_service = config_service
        self.backup_directory = Path("backups")
        self.backup_directory.mkdir(exist_ok=True)
    
    def create_backup(self, name: Optional[str] = None) -> Tuple[bool, str]:
        """Create a timestamped backup of current settings."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = name or f"settings_backup_{timestamp}"
            backup_filename = f"{backup_name}.json"
            backup_path = self.backup_directory / backup_filename
            
            success = self.config_service.export_settings(str(backup_path))
            message = f"Backup created: {backup_filename}" if success else "Backup creation failed"
            
            return success, message
        except Exception as e:
            return False, f"Failed to create backup: {str(e)}"
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available settings backups."""
        try:
            backups = []
            if not self.backup_directory.exists():
                return backups
            
            for filepath in self.backup_directory.glob("*.json"):
                if filepath.name.startswith("settings_backup_"):
                    stat = filepath.stat()
                    backups.append({
                        'filename': filepath.name,
                        'filepath': str(filepath),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
            
            # Sort by modification time, newest first
            backups.sort(key=lambda x: x['modified'], reverse=True)
            return backups
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def restore_backup(self, backup_filepath: str) -> Tuple[bool, str]:
        """Restore settings from a backup file."""
        try:
            success = self.config_service.import_settings(backup_filepath)
            message = "Settings restored from backup" if success else "Restore failed"
            return success, message
        except Exception as e:
            return False, f"Failed to restore backup: {str(e)}"
    
    def delete_backup(self, backup_filepath: str) -> Tuple[bool, str]:
        """Delete a settings backup file."""
        try:
            backup_path = Path(backup_filepath)
            if not backup_path.exists():
                return False, f"Backup file not found: {backup_filepath}"
            
            backup_path.unlink()
            return True, f"Backup deleted: {backup_path.name}"
        except Exception as e:
            return False, f"Failed to delete backup: {str(e)}"

# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_configuration_service() -> ConfigurationService:
    """Create and initialize the configuration service."""
    return ConfigurationService()

def create_settings_backup_service(config_service: ConfigurationService) -> SettingsBackupService:
    """Create the settings backup service."""
    return SettingsBackupService(config_service)

# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def validate_settings_structure(settings: Dict[str, Any]) -> List[str]:
    """Validate settings structure and return list of validation errors."""
    errors = []
    
    try:
        if not isinstance(settings, dict):
            errors.append("Settings data must be a dictionary")
            return errors
        
        # Check for required categories
        required_categories = ['server', 'gui', 'monitoring', 'advanced']
        for category in required_categories:
            if category not in settings:
                errors.append(f"Missing required category: {category}")
            elif not isinstance(settings[category], dict):
                errors.append(f"Category '{category}' must be a dictionary")
        
        # Validate specific settings
        if 'server' in settings and isinstance(settings['server'], dict):
            server = settings['server']
            
            if 'port' in server:
                try:
                    port = int(server['port'])
                    if not (1024 <= port <= 65535):
                        errors.append("Server port must be between 1024 and 65535")
                except (ValueError, TypeError):
                    errors.append("Server port must be a number")
            
            if 'host' in server and (not isinstance(server['host'], str) or not server['host'].strip()):
                errors.append("Server host cannot be empty")
        
        # Add more validation as needed
        
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
    
    return errors