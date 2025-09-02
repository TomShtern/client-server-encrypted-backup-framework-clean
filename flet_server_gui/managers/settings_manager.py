"""
Settings Manager for Flet Server GUI
Real settings management with unified configuration integration
"""

import os
import json
from typing import Dict, Any, Callable, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SettingsManager:
    """
    Real settings management with unified configuration integration.
    NO mock data - all settings are persisted and validated.
    """
    
    def __init__(self):
        """Initialize with real configuration paths and validation"""
        self.settings_file = Path("flet_server_gui_settings.json")
        self.config_watchers: List[Callable] = []
        
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
            }
        }
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load real settings from unified config or JSON file.
        Returns validated settings with proper defaults.
        """
        try:
            if self.use_unified and self.unified_config:
                return self._load_from_unified_config()
            else:
                return self._load_from_json_file()
        except Exception as e:
            logger.error(f"❌ Failed to load settings: {e}")
            return self.default_settings.copy()
    
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
                merged[category].update(settings)
        
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
                return self._save_to_unified_config(validated_settings)
            else:
                return self._save_to_json_file(validated_settings)
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
        Returns validated settings or raises ValueError.
        """
        validated = {}
        
        # Validate server settings
        if 'server' in settings:
            validated['server'] = {}
            server = settings['server']
            
            # Port validation
            port = int(server.get('port', self.default_settings['server']['port']))
            if not (1024 <= port <= 65535):
                raise ValueError(f"Port {port} must be between 1024 and 65535")
            validated['server']['port'] = port
            
            # Host validation
            host = str(server.get('host', self.default_settings['server']['host']))
            if not host.strip():
                raise ValueError("Host cannot be empty")
            validated['server']['host'] = host.strip()
            
            # Storage directory validation
            storage_dir = str(server.get('storage_dir', self.default_settings['server']['storage_dir']))
            if not storage_dir.strip():
                raise ValueError("Storage directory cannot be empty")
            validated['server']['storage_dir'] = storage_dir.strip()
            
            # Numeric validations
            max_clients = int(server.get('max_clients', self.default_settings['server']['max_clients']))
            if not (1 <= max_clients <= 1000):
                raise ValueError("Max clients must be between 1 and 1000")
            validated['server']['max_clients'] = max_clients
            
            session_timeout = int(server.get('session_timeout', self.default_settings['server']['session_timeout']))
            if not (1 <= session_timeout <= 1440):  # 1 minute to 24 hours
                raise ValueError("Session timeout must be between 1 and 1440 minutes")
            validated['server']['session_timeout'] = session_timeout
            
            maintenance_interval = int(server.get('maintenance_interval', self.default_settings['server']['maintenance_interval']))
            if not (10 <= maintenance_interval <= 3600):  # 10 seconds to 1 hour
                raise ValueError("Maintenance interval must be between 10 and 3600 seconds")
            validated['server']['maintenance_interval'] = maintenance_interval
            
            # Boolean settings
            validated['server']['auto_start'] = bool(server.get('auto_start', self.default_settings['server']['auto_start']))
            
            # Log level validation
            log_level = str(server.get('log_level', self.default_settings['server']['log_level'])).upper()
            if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                raise ValueError("Log level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
            validated['server']['log_level'] = log_level
        
        # Validate GUI settings
        if 'gui' in settings:
            validated['gui'] = {}
            gui = settings['gui']
            
            # Theme validation
            theme_mode = str(gui.get('theme_mode', self.default_settings['gui']['theme_mode'])).lower()
            if theme_mode not in ['light', 'dark', 'system']:
                raise ValueError("Theme mode must be light, dark, or system")
            validated['gui']['theme_mode'] = theme_mode
            
            # Auto refresh interval
            auto_refresh = int(gui.get('auto_refresh_interval', self.default_settings['gui']['auto_refresh_interval']))
            if not (1 <= auto_refresh <= 60):
                raise ValueError("Auto refresh interval must be between 1 and 60 seconds")
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
                raise ValueError("Monitoring interval must be between 1 and 60 seconds")
            validated['monitoring']['monitoring_interval'] = interval
            
            # History retention
            retention = int(monitoring.get('history_retention_days', self.default_settings['monitoring']['history_retention_days']))
            if not (1 <= retention <= 365):
                raise ValueError("History retention must be between 1 and 365 days")
            validated['monitoring']['history_retention_days'] = retention
            
            # Alert thresholds
            if 'alert_thresholds' in monitoring:
                validated['monitoring']['alert_thresholds'] = {}
                thresholds = monitoring['alert_thresholds']
                
                for metric in ['cpu_percent', 'memory_percent', 'disk_percent']:
                    value = int(thresholds.get(metric, self.default_settings['monitoring']['alert_thresholds'][metric]))
                    if not (50 <= value <= 99):
                        raise ValueError(f"{metric} threshold must be between 50 and 99")
                    validated['monitoring']['alert_thresholds'][metric] = value
        
        return validated
    
    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """
        Get a specific setting using dot notation.
        Example: get_setting('server.port') or get_setting('gui.theme_mode')
        """
        settings = self.load_settings()
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
        settings = self.load_settings()
        keys = key_path.split('.')
        
        # Navigate to the parent dict
        current = settings
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
        
        # Save the updated settings
        return self.save_settings(settings)
    
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
                raise ValueError(f"Unknown settings category: {category}")

            current_settings = self.load_settings()
            current_settings[category] = self.default_settings[category].copy()
            result = self.save_settings(current_settings)

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
            settings = self.load_settings()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
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
                imported_settings = json.load(f)
            
            # Validate and save imported settings
            result = self.save_settings(imported_settings)
            
            if result:
                logger.info(f"✅ Settings imported from {file_path}")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to import settings: {e}")
            return False