#!/usr/bin/env python3
"""
Enhanced Settings View for FletV2
Optimized responsive design with comprehensive server bridge integration, Material Design 3 styling, and enhanced interactivity.
"""

import flet as ft
from typing import Optional, Dict, Any, Callable
import json
import asyncio
import sys
import time
from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.user_feedback import show_success_message, show_error_message, show_info_message
from utils.ui_components import create_modern_card
from pathlib import Path
from datetime import datetime
from config import SETTINGS_FILE, ASYNC_DELAY, MIN_PORT, MAX_PORT, MIN_MAX_CLIENTS

# UTF-8 support
import sys
import os
# Add parent directory to path to access Shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import Shared.utils.utf8_solution
except ImportError:
    # Fallback: use local utf8_patch if available
    try:
        from utils import utf8_patch
    except ImportError:
        pass  # Continue without UTF-8 patch

logger = get_logger(__name__)


class EnhancedSettingsState:
    """Enhanced state management with server bridge integration and reactive updates."""

    def __init__(self, page: ft.Page, server_bridge: Optional[ServerBridge] = None, state_manager: Optional[StateManager] = None):
        self.page = page
        self.server_bridge = server_bridge
        self.state_manager = state_manager
        self.current_settings = self._load_default_settings()
        self.is_saving = False
        self.is_loading = False
        self.last_saved = None
        self.last_loaded = None
        self._ui_refs = {}
        self._validation_errors = {}
        self._pending_changes = {}
        self._auto_save_task = None
        self._sync_enabled = True
        self._auto_save_lock = asyncio.Lock()  # Thread-safety for auto-save operations

        # Subscribe to state manager for reactive updates
        if self.state_manager:
            self.state_manager.subscribe_to_settings(self._on_settings_changed)
            self.state_manager.subscribe("settings_events", self._on_settings_event)

    def _load_default_settings(self):
        """Load comprehensive default settings structure."""
        return {
            'server': {
                'port': 1256,
                'host': '127.0.0.1',
                'max_clients': 50,
                'log_level': 'INFO',
                'timeout': 30,
                'buffer_size': 4096,
                'enable_ssl': False,
                'ssl_cert_path': '',
                'ssl_key_path': ''
            },
            'gui': {
                'theme_mode': 'dark',
                'auto_refresh': True,
                'notifications': True,
                'refresh_interval': 5,
                'page_size': 50,
                'language': 'en',
                'animations_enabled': True,
                'sound_enabled': False
            },
            'monitoring': {
                'enabled': True,
                'interval': 2,
                'alerts': True,
                'cpu_threshold': 80,
                'memory_threshold': 85,
                'disk_threshold': 90,
                'network_monitoring': True,
                'log_monitoring': True
            },
            'logging': {
                'level': 'INFO',
                'file_path': 'server.log',
                'max_file_size': 10485760,  # 10MB
                'backup_count': 5,
                'console_output': True
            },
            'security': {
                'authentication_required': False,
                'session_timeout': 3600,
                'max_login_attempts': 5,
                'lockout_duration': 900
            },
            'backup': {
                'auto_backup_settings': True,
                'backup_interval_hours': 24,
                'max_backups': 10,
                'compression_enabled': True
            }
        }

    async def load_settings_async(self):
        """Load settings with server bridge integration and fallback."""
        if self.is_loading:
            return False

        self.is_loading = True
        try:
            # Set loading state in state manager
            if self.state_manager:
                self.state_manager.set_loading("settings_load", True)

            # Try server bridge first
            if self.server_bridge:
                try:
                    result = await self.server_bridge.load_settings_async()
                    if result.get('success') and result.get('data'):
                        loaded_settings = result['data']
                        # Merge with defaults to ensure all keys exist
                        merged_settings = self._deep_merge_settings(self._load_default_settings(), loaded_settings)
                        self.current_settings = merged_settings
                        self.last_loaded = datetime.now()

                        # Update state manager
                        if self.state_manager:
                            await self.state_manager.update_settings_async(self.current_settings, "server_load")

                        self._update_ui_from_settings()
                        logger.info(f"Settings loaded from server ({result.get('mode', 'server')})")
                        return True
                except Exception as e:
                    logger.warning(f"Server settings load failed, falling back to local: {e}")

            # Fallback to local file
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    merged_settings = self._deep_merge_settings(self._load_default_settings(), loaded)
                    self.current_settings = merged_settings
                    self.last_loaded = datetime.now()

                    # Update state manager
                    if self.state_manager:
                        await self.state_manager.update_settings_async(self.current_settings, "local_load")

                    self._update_ui_from_settings()
                    logger.info("Settings loaded from local file")
                    return True

                # Use defaults (when settings file doesn't exist)
                if self.state_manager:
                    await self.state_manager.update_settings_async(self.current_settings, "defaults")
                self._update_ui_from_settings()
                logger.info("Using default settings")
                return True

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            if self.state_manager:
                self.state_manager.set_error_state("settings_load", str(e))
            return False
        finally:
            self.is_loading = False
            if self.state_manager:
                self.state_manager.set_loading("settings_load", False)

    def _deep_merge_settings(self, defaults: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge loaded settings with defaults to ensure all keys exist."""
        result = defaults.copy()
        for section, section_data in loaded.items():
            if section in result and isinstance(section_data, dict) and isinstance(result[section], dict):
                result[section].update(section_data)
            else:
                result[section] = section_data
        return result

    def _update_ui_from_settings(self):
        """Update all UI controls with loaded settings."""
        for section_key, controls in self._ui_refs.items():
            try:
                section, key = section_key.split('.')
                value = self.current_settings.get(section, {}).get(key)
                if value is not None:
                    for control in controls:
                        if hasattr(control, 'value') and isinstance(control, ft.Switch):
                            control.value = bool(value)
                        elif hasattr(control, 'value') and isinstance(control, ft.Slider):
                            control.value = float(value)
                        elif hasattr(control, 'value'):
                            control.value = str(value)

                            # Clear any validation errors
                            if hasattr(control, 'error_text'):
                                control.error_text = None

                            if hasattr(control, 'update'):
                                control.update()
            except Exception as e:
                logger.debug(f"Failed to update UI control for {section_key}: {e}")

    def register_ui_control(self, section: str, key: str, control):
        """Register UI control for automatic updates."""
        section_key = f"{section}.{key}"
        if section_key not in self._ui_refs:
            self._ui_refs[section_key] = []
        self._ui_refs[section_key].append(control)

    async def save_settings_async(self, auto_save: bool = False):
        """Save settings with server bridge integration and validation."""
        if self.is_saving:
            return False

        self.is_saving = True
        try:
            # Set loading state
            if self.state_manager:
                self.state_manager.set_loading("settings_save", True)

            # Validate settings first
            validation_result = await self.validate_settings_async(self.current_settings)
            if not validation_result.get('success', True):
                validation_data = validation_result.get('data', {})
                if not validation_data.get('valid', True):
                    errors = validation_data.get('errors', [])
                    logger.warning(f"Settings validation failed: {errors}")
                    if self.state_manager:
                        self.state_manager.set_error_state("settings_validation", "Validation failed", {"errors": errors})
                    return False

            # Try server bridge first
            if self.server_bridge:
                try:
                    result = await self.server_bridge.save_settings_async(self.current_settings)
                    if result.get('success'):
                        self.last_saved = datetime.now()

                        # Update state manager
                        if self.state_manager:
                            await self.state_manager.update_settings_async(self.current_settings, "server_save")
                            if not auto_save:
                                self.state_manager.add_notification(
                                    f"Settings saved to server ({result.get('mode', 'server')})",
                                    "success"
                                )

                        logger.info(f"Settings saved to server ({result.get('mode', 'server')})")

                        # Also save locally as backup
                        await self._save_local_backup()
                        return True
                except Exception as e:
                    logger.warning(f"Server settings save failed, falling back to local: {e}")

            # Fallback to local file
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=2, ensure_ascii=False)

            self.last_saved = datetime.now()

            # Update state manager
            if self.state_manager:
                await self.state_manager.update_settings_async(self.current_settings, "local_save")
                if not auto_save:
                    self.state_manager.add_notification("Settings saved locally", "success")

            logger.info("Settings saved to local file")
            return True

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            if self.state_manager:
                self.state_manager.set_error_state("settings_save", str(e))
            return False
        finally:
            self.is_saving = False
            if self.state_manager:
                self.state_manager.set_loading("settings_save", False)

    async def _save_local_backup(self):
        """Save local backup of settings."""
        try:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Failed to save local backup: {e}")

    async def validate_settings_async(self, settings_data: Dict[str, Any]):
        """Validate settings with comprehensive cross-field checks and server bridge integration."""
        try:
            if self.server_bridge:
                return await self.server_bridge.validate_settings_async(settings_data)

            # Local validation fallback with comprehensive cross-field checks
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }

            # Basic validation
            if 'server' in settings_data:
                server_settings = settings_data['server']
                port = server_settings.get('port')
                if port and (not isinstance(port, int) or port < 1024 or port > 65535):
                    validation_result['errors'].append("Port must be between 1024-65535")
                    validation_result['valid'] = False

                # Cross-field validation: SSL configuration
                if (ssl_enabled := server_settings.get('ssl_enabled', False)):
                    ssl_cert_path = server_settings.get('ssl_cert_path', '').strip()
                    ssl_key_path = server_settings.get('ssl_key_path', '').strip()

                    if not ssl_cert_path:
                        validation_result['errors'].append("SSL certificate path is required when SSL is enabled")
                        validation_result['valid'] = False
                    elif not Path(ssl_cert_path).exists():
                        validation_result['warnings'].append(f"SSL certificate file not found: {ssl_cert_path}")

                    if not ssl_key_path:
                        validation_result['errors'].append("SSL key path is required when SSL is enabled")
                        validation_result['valid'] = False
                    elif not Path(ssl_key_path).exists():
                        validation_result['warnings'].append(f"SSL key file not found: {ssl_key_path}")

            # Cross-field validation: Backup settings
            if 'backup' in settings_data:
                backup_settings = settings_data['backup']
                if (auto_backup := backup_settings.get('auto_backup_enabled', False)):
                    backup_interval = backup_settings.get('backup_interval_hours', 0)
                    if not isinstance(backup_interval, (int, float)) or backup_interval <= 0:
                        validation_result['errors'].append("Backup interval must be greater than 0 hours when auto-backup is enabled")
                        validation_result['valid'] = False

                    backup_path = backup_settings.get('backup_path', '').strip()
                    if not backup_path:
                        validation_result['errors'].append("Backup path is required when auto-backup is enabled")
                        validation_result['valid'] = False
                    else:
                        # Check if backup directory exists or can be created
                        try:
                            backup_dir = Path(backup_path).parent
                            if not backup_dir.exists():
                                validation_result['warnings'].append(f"Backup directory does not exist: {backup_dir}")
                        except Exception:
                            validation_result['errors'].append(f"Invalid backup path: {backup_path}")
                            validation_result['valid'] = False

            # Cross-field validation: Monitoring thresholds
            if 'monitoring' in settings_data:
                monitoring_settings = settings_data['monitoring']
                monitoring_enabled = monitoring_settings.get('enabled', False)

                if monitoring_enabled:
                    cpu_threshold = monitoring_settings.get('cpu_threshold', 80)
                    memory_threshold = monitoring_settings.get('memory_threshold', 85)

                    if not isinstance(cpu_threshold, (int, float)) or cpu_threshold <= 0 or cpu_threshold > 100:
                        validation_result['errors'].append("CPU threshold must be between 1-100 when monitoring is enabled")
                        validation_result['valid'] = False

                    if not isinstance(memory_threshold, (int, float)) or memory_threshold <= 0 or memory_threshold > 100:
                        validation_result['errors'].append("Memory threshold must be between 1-100 when monitoring is enabled")
                        validation_result['valid'] = False

                    # Logical validation: CPU threshold should typically be lower than memory threshold
                    if isinstance(cpu_threshold, (int, float)) and isinstance(memory_threshold, (int, float)) and cpu_threshold >= memory_threshold:
                        validation_result['warnings'].append("CPU threshold is higher than memory threshold - this may cause frequent alerts")

            # Cross-field validation: GUI refresh settings
            if 'gui' in settings_data:
                gui_settings = settings_data['gui']
                auto_refresh = gui_settings.get('auto_refresh', False)

                if auto_refresh:
                    refresh_interval = gui_settings.get('refresh_interval', 5)
                    if not isinstance(refresh_interval, (int, float)) or refresh_interval < 1:
                        validation_result['errors'].append("Refresh interval must be at least 1 second when auto-refresh is enabled")
                        validation_result['valid'] = False
                    elif refresh_interval < 3:
                        validation_result['warnings'].append("Refresh intervals below 3 seconds may impact performance")

            return {'success': True, 'data': validation_result}
        except Exception as e:
            logger.error(f"Settings validation failed: {e}")
            return {'success': False, 'error': str(e)}

    def update_setting(self, section: str, key: str, value, validate: bool = True):
        """Update a setting with validation and reactive updates."""
        try:
            if section not in self.current_settings:
                self.current_settings[section] = {}

            old_value = self.current_settings[section].get(key)
            self.current_settings[section][key] = value

            # Track pending changes for auto-save
            change_key = f"{section}.{key}"
            self._pending_changes[change_key] = {
                'old_value': old_value,
                'new_value': value,
                'timestamp': time.time()
            }

            # Schedule auto-save if enabled
            if self._sync_enabled:
                self._schedule_auto_save()

            # Update state manager
            if self.state_manager:
                self.state_manager.update(f"settings.{section}.{key}", value, source="user_input")

            logger.debug(f"Setting updated: {section}.{key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to update setting {section}.{key}: {e}")
            return False

    def _schedule_auto_save(self):
        """Schedule auto-save with debouncing and proper concurrency control."""
        if self._auto_save_task:
            self._auto_save_task.cancel()

        async def auto_save_worker():
            try:
                await asyncio.sleep(2.0)  # Debounce delay

                # Use lock for thread-safety
                async with self._auto_save_lock:
                    # Snapshot pending changes atomically
                    pending_snapshot = self._pending_changes.copy()

                    if pending_snapshot:
                        await self.save_settings_async(auto_save=True)
                        # Only clear the changes that were present at snapshot time
                        for key in pending_snapshot:
                            self._pending_changes.pop(key, None)

            except asyncio.CancelledError:
                pass  # Expected cancellation
            except Exception as e:
                logger.debug(f"Auto-save failed: {e}")

        # Create task and await previous task cancellation if needed
        async def start_auto_save():
            if self._auto_save_task and not self._auto_save_task.done():
                try:
                    await self._auto_save_task
                except asyncio.CancelledError:
                    pass  # Expected cancellation
                except Exception:
                    pass  # Ignore other errors during cleanup
                finally:
                    self._auto_save_task = None

            self._auto_save_task = asyncio.create_task(auto_save_worker())

        # Schedule the start task
        asyncio.create_task(start_auto_save())

    def get_setting(self, section: str, key: str, default=None):
        """Get a setting value safely."""
        return self.current_settings.get(section, {}).get(key, default)

    def _on_settings_changed(self, settings_data, old_data):
        """Handle settings changes from state manager."""
        if self._sync_enabled and settings_data != self.current_settings:
            self.current_settings = settings_data
            self._update_ui_from_settings()

    def _on_settings_event(self, event_data, old_data):
        """Handle settings events from state manager."""
        if isinstance(event_data, dict):
            event_type = event_data.get('type')
            if event_type == 'settings_updated':
                logger.debug("Settings updated event received")
            elif event_type == 'settings_conflict_merged' and self.state_manager:
                self.state_manager.add_notification("Settings conflict resolved", "warning")

    async def backup_settings_async(self, backup_name: str):
        """Create settings backup with versioning and progress tracking."""
        try:
            if self.state_manager:
                self.state_manager.start_progress("settings_backup", total_steps=2, message="Creating backup")
                self.state_manager.set_loading("settings_backup", True)

            if self.server_bridge:
                result = await self.server_bridge.backup_settings_async(backup_name, self.current_settings)
                if result.get('success') and self.state_manager:
                    self.state_manager.update_progress("settings_backup", step=1, message="Saving")
                    self.state_manager.add_notification(f"Backup '{backup_name}' created", "success")
                    return result

            # Local backup fallback
            backup_dir = Path("settings_backups")
            backup_dir.mkdir(exist_ok=True)

            backup_file = backup_dir / f"{backup_name}.json"
            backup_data = {
                'created_at': time.time(),
                'backup_name': backup_name,
                'settings': self.current_settings
            }

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            if self.state_manager:
                self.state_manager.update_progress("settings_backup", step=1, message="Saving")
                self.state_manager.add_notification(f"Local backup '{backup_name}' created", "success")

            return {'success': True, 'backup_file': str(backup_file)}

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            if self.state_manager:
                self.state_manager.set_error_state("settings_backup", str(e))
            return {'success': False, 'error': str(e)}
        finally:
            if self.state_manager:
                self.state_manager.clear_progress("settings_backup")
                self.state_manager.set_loading("settings_backup", False)

    async def restore_settings_async(self, backup_file: str):
        """Restore settings from backup."""
        try:
            if self.state_manager:
                self.state_manager.set_loading("settings_restore", True)

            if self.server_bridge:
                result = await self.server_bridge.restore_settings_async(backup_file)
                if result.get('success'):
                    restored_settings = result.get('data', {}).get('restored_settings')
                    if restored_settings:
                        self.current_settings = restored_settings
                        self._update_ui_from_settings()
                        if self.state_manager:
                            await self.state_manager.update_settings_async(self.current_settings, "restore")
                            self.state_manager.add_notification("Settings restored from backup", "success")
                    return result

            # Local restore fallback
            backup_path = Path(backup_file)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")

            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            restored_settings = backup_data.get('settings', backup_data)
            self.current_settings = self._deep_merge_settings(self._load_default_settings(), restored_settings)
            self._update_ui_from_settings()

            if self.state_manager:
                await self.state_manager.update_settings_async(self.current_settings, "local_restore")
                self.state_manager.add_notification("Settings restored from local backup", "success")

            return {'success': True}

        except Exception as e:
            logger.error(f"Failed to restore settings: {e}")
            if self.state_manager:
                self.state_manager.set_error_state("settings_restore", str(e))
            return {'success': False, 'error': str(e)}
        finally:
            if self.state_manager:
                self.state_manager.set_loading("settings_restore", False)

    def dispose(self):
        """Enhanced disposal with comprehensive cleanup for settings view."""
        try:
            # Cancel auto-save task if running
            if self._auto_save_task and not self._auto_save_task.done():
                self._auto_save_task.cancel()
                logger.debug("Auto-save task cancelled")

            # Unsubscribe from state manager events
            if self.state_manager:
                try:
                    if hasattr(self.state_manager, 'unsubscribe_settings'):
                        self.state_manager.unsubscribe_settings(self._on_settings_changed)
                    else:
                        logger.debug("Settings-specific unsubscribe not available")

                    # Unsubscribe from all event types
                    self.state_manager.unsubscribe("settings_events", self._on_settings_event)
                    self.state_manager.unsubscribe("loading_states", lambda x, y: None)
                    logger.debug("State manager subscriptions cleaned up")
                except Exception as e:
                    logger.debug(f"Error unsubscribing from state manager: {e}")

            # Remove FilePicker from overlay if present
            if self.page and hasattr(self, 'file_picker') and self.file_picker is not None:
                try:
                    if self.file_picker in self.page.overlay:
                        self.page.overlay.remove(self.file_picker)
                        self.page.update()
                    self.file_picker = None
                    logger.debug("FilePicker removed from overlay")
                except Exception as e:
                    logger.debug(f"Error removing FilePicker: {e}")

            # Clear UI control references to prevent memory leaks
            self._ui_refs.clear()
            self._validation_errors.clear()
            self._pending_changes.clear()

            logger.debug("Settings view disposed: cleaned up subscriptions, tasks, and UI references")
        except Exception as e:
            logger.warning(f"Error during settings view disposal: {e}")


# Enhanced validation functions with comprehensive checks
def validate_port(value: str) -> tuple[bool, str]:
    """Validate port number with enhanced checks."""
    try:
        port = int(value)
        min_port = getattr(sys.modules[__name__], 'MIN_PORT', 1024)
        max_port = getattr(sys.modules[__name__], 'MAX_PORT', 65535)

        if port < min_port:
            return False, f"Port must be at least {min_port} (system reserved)"
        elif port > max_port:
            return False, f"Port cannot exceed {max_port}"
        privileged_ports = {80, 443}
        if port in privileged_ports:
            return True, f"⚠️ Port {port} may require administrator privileges"
        else:
            return True, ""
    except ValueError:
        return False, "Please enter a valid number"

def validate_max_clients(value: str) -> tuple[bool, str]:
    """Validate max clients with performance warnings."""
    try:
        clients = int(value)
        if clients < 1:
            return False, "Must be at least 1"
        elif clients > 1000:
            return False, "Cannot exceed 1000 clients"
        elif clients > 100:
            return True, "⚠️ High client count may impact performance"
        else:
            return True, ""
    except ValueError:
        return False, "Please enter a valid number"

def validate_monitoring_interval(value: str) -> tuple[bool, str]:
    """Validate monitoring interval with performance guidance."""
    try:
        interval = int(value)
        if interval < 1:
            return False, "Interval must be at least 1 second"
        elif interval > 60:
            return False, "Interval cannot exceed 60 seconds"
        elif interval < 2:
            return True, "⚠️ Very frequent monitoring may impact performance"
        else:
            return True, ""
    except ValueError:
        return False, "Please enter a valid number"

def validate_file_size(value: str) -> tuple[bool, str]:
    """Validate file size in bytes."""
    try:
        size = int(value)
        if size < 1024:  # 1KB minimum
            return False, "File size must be at least 1KB (1024 bytes)"
        elif size > 1073741824:  # 1GB maximum
            return False, "File size cannot exceed 1GB"
        else:
            return True, ""
    except ValueError:
        return False, "Please enter a valid number"

def validate_timeout(value: str) -> tuple[bool, str]:
    """Validate timeout values."""
    try:
        timeout = int(value)
        if timeout < 1:
            return False, "Timeout must be at least 1 second"
        elif timeout > 3600:
            return False, "Timeout cannot exceed 1 hour (3600 seconds)"
        else:
            return True, ""
    except ValueError:
        return False, "Please enter a valid number"

def create_enhanced_field_handler(state: EnhancedSettingsState, section: str, key: str, validator=None, data_type=str):
    """Enhanced field change handler with real-time validation and feedback."""
    def handler(e):
        value = e.control.value

        # Real-time validation
        if validator:
            if (result := validator(value)):
                is_valid, error_msg = result
                e.control.error_text = None if is_valid else error_msg

            # Visual feedback for validation state
            if not is_valid:
                e.control.border_color = ft.Colors.ERROR
            elif error_msg.startswith("⚠️"):
                e.control.border_color = ft.Colors.ORANGE
            else:
                e.control.border_color = ft.Colors.PRIMARY

            e.control.update()

            if not is_valid:
                return

        # Convert to appropriate type
        type_converters = {int: int, float: float, bool: bool}
        converter = type_converters.get(data_type)
        if converter:
            try:
                value = converter(value)
            except ValueError:
                e.control.error_text = f"Invalid {data_type.__name__} value"
                e.control.border_color = ft.Colors.ERROR
                e.control.update()
                return

        # Update setting with reactive state management
        success = state.update_setting(section, key, value)

        if success:
            # Visual success feedback
            e.control.border_color = ft.Colors.PRIMARY
            e.control.update()

            # Show success notification for important settings
            if key in {'port', 'host', 'max_clients'} and state.state_manager:
                state.state_manager.add_notification(
                    f"{key.title().replace('_', ' ')} updated to {value}",
                    "success",
                    auto_dismiss=3
                )

    return handler

def create_enhanced_switch_handler(state: EnhancedSettingsState, section: str, key: str, on_change_callback: Optional[Callable] = None):
    """Enhanced switch handler with animations and feedback."""
    def handler(e):
        value = e.control.value
        success = state.update_setting(section, key, value)

        if success:
            # Animate switch feedback
            e.control.scale = 1.1
            e.control.update()

            # Reset scale after animation
            async def reset_scale():
                await asyncio.sleep(0.1)
                e.control.scale = 1.0
                e.control.update()

            if state.page:
                state.page.run_task(reset_scale)

            # Custom callback for special handling
            if on_change_callback:
                on_change_callback(value)

            # Notification for important toggles
            if key in {'enabled', 'alerts', 'notifications'} and state.state_manager:
                state.state_manager.add_notification(
                    f"{key.title().replace('_', ' ')} {'enabled' if value else 'disabled'}",
                    "info",
                    auto_dismiss=2
                )

    return handler

def create_modern_reset_button(field: ft.Control, default_value: Any, state: EnhancedSettingsState, field_type: str = "text"):
    """Create modern reset button with enhanced styling and animations."""
    def reset_handler(e):
        # Animate button press
        e.control.scale = 0.9
        e.control.update()

        # Reset field value
        if hasattr(field, 'value'):
            if isinstance(field, ft.Switch):
                field.value = bool(default_value)
            elif isinstance(field, ft.Slider):
                field.value = float(default_value)
            else:
                field.value = str(default_value)

        # Clear validation errors
        if hasattr(field, 'error_text'):
            field.error_text = None
        if hasattr(field, 'border_color'):
            field.border_color = ft.Colors.PRIMARY

        field.update()

        # Reset button scale and show feedback
        async def reset_animation():
            await asyncio.sleep(0.1)
            e.control.scale = 1.0
            e.control.update()

            if state.state_manager:
                state.state_manager.add_notification(
                    f"{getattr(field, 'label', field_type)} reset to default",
                    "info",
                    auto_dismiss=2
                )

        if state.page:
            state.page.run_task(reset_animation)

    return ft.IconButton(
        icon=ft.Icons.REFRESH,
        tooltip=f"Reset to default ({default_value})",
        on_click=reset_handler,
        icon_size=18,
        style=ft.ButtonStyle(
            color={
                ft.ControlState.DEFAULT: ft.Colors.ON_SURFACE_VARIANT,
                ft.ControlState.HOVERED: ft.Colors.PRIMARY,
            },
            bgcolor={
                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
            },
            shape=ft.CircleBorder(),
            animation_duration=150,
        )
    )

def create_modern_text_field(
    label: str,
    value: Any,
    state: EnhancedSettingsState,
    section: str,
    key: str,
    validator: Optional[Callable] = None,
    data_type: type = str,
    width: Optional[int] = None,
    keyboard_type: Optional[ft.KeyboardType] = None,
    prefix_icon: Optional[str] = None,
    suffix_text: Optional[str] = None
) -> ft.TextField:
    """Create modern Material Design 3 text field with enhanced styling and proper event handlers."""

    # Ensure the field has proper event handlers
    def on_focus_handler(e):
        """Handle focus events for better user feedback."""
        e.control.focused_border_color = ft.Colors.PRIMARY
        e.control.update()

    def on_blur_handler(e):
        """Handle blur events to validate and save changes."""
        if validator:
            is_valid, error_msg = validator(e.control.value)
            if not is_valid:
                e.control.error_text = error_msg
                e.control.border_color = ft.Colors.ERROR
            else:
                e.control.error_text = None
                e.control.border_color = ft.Colors.PRIMARY
        e.control.update()

    field = ft.TextField(
        label=label,
        value=str(value),
        width=width,
        keyboard_type=keyboard_type,
        prefix_icon=ft.Icon(prefix_icon) if prefix_icon else None,
        suffix_text=suffix_text,
        border_radius=12,
        filled=True,
        border=ft.InputBorder.OUTLINE,
        focused_border_color=ft.Colors.PRIMARY,
        focused_bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
        cursor_color=ft.Colors.PRIMARY,
        selection_color=ft.Colors.with_opacity(0.3, ft.Colors.PRIMARY),
        on_change=create_enhanced_field_handler(state, section, key, validator, data_type),
        on_focus=on_focus_handler,
        on_blur=on_blur_handler,
        animate_size=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
    )

    state.register_ui_control(section, key, field)
    return field

def create_modern_switch(
    label: str,
    value: bool,
    state: EnhancedSettingsState,
    section: str,
    key: str,
    on_change_callback: Optional[Callable] = None
) -> ft.Switch:
    """Create modern Material Design 3 switch with enhanced styling and proper event handlers."""

    # Enhanced switch handler with proper error handling
    def enhanced_switch_handler(e):
        try:
            value = e.control.value
            success = state.update_setting(section, key, value)

            if success:
                # Visual feedback
                e.control.scale = 1.1
                e.control.update()

                # Reset scale after animation
                async def reset_scale():
                    await asyncio.sleep(0.1)
                    e.control.scale = 1.0
                    e.control.update()

                if state.page:
                    state.page.run_task(reset_scale)

                # Custom callback
                if on_change_callback:
                    on_change_callback(value)

                # Notification for important toggles
                if key in {'enabled', 'alerts', 'notifications'} and state.state_manager:
                    state.state_manager.add_notification(
                        f"{key.title().replace('_', ' ')} {'enabled' if value else 'disabled'}",
                        "info",
                        auto_dismiss=2
                    )
            else:
                # Show error feedback
                e.control.scale = 0.9
                e.control.update()
                async def reset_error_scale():
                    await asyncio.sleep(0.1)
                    e.control.scale = 1.0
                    e.control.update()
                if state.page:
                    state.page.run_task(reset_error_scale)

        except Exception as ex:
            logger.error(f"Switch handler error for {section}.{key}: {ex}")
            if state.state_manager:
                state.state_manager.add_notification(f"Error updating {key}", "error")

    switch = ft.Switch(
        label=label,
        value=value,
        active_color=ft.Colors.PRIMARY,
        active_track_color=ft.Colors.with_opacity(0.5, ft.Colors.PRIMARY),
        inactive_thumb_color=ft.Colors.OUTLINE,
        inactive_track_color=ft.Colors.with_opacity(0.3, ft.Colors.OUTLINE),
        on_change=enhanced_switch_handler,
        scale=ft.Scale(1.0),
    )

    state.register_ui_control(section, key, switch)
    return switch

def create_modern_dropdown(
    label: str,
    value: str,
    options: list,
    state: EnhancedSettingsState,
    section: str,
    key: str,
    width: Optional[int] = None
) -> ft.Dropdown:
    """Create modern Material Design 3 dropdown with enhanced styling and proper event handlers."""

    # Enhanced dropdown handler
    def enhanced_dropdown_handler(e):
        try:
            new_value = e.control.value
            success = state.update_setting(section, key, new_value)

            if success:
                # Visual feedback
                e.control.border_color = ft.Colors.PRIMARY
                e.control.update()

                # Show notification for important settings
                if key in {'log_level', 'language', 'theme_mode'} and state.state_manager:
                    state.state_manager.add_notification(
                        f"{key.title().replace('_', ' ')} changed to {new_value}",
                        "success",
                        auto_dismiss=3
                    )
            else:
                # Show error feedback
                e.control.border_color = ft.Colors.ERROR
                e.control.update()

        except Exception as ex:
            logger.error(f"Dropdown handler error for {section}.{key}: {ex}")
            if state.state_manager:
                state.state_manager.add_notification(f"Error updating {key}", "error")

    dropdown = ft.Dropdown(
        label=label,
        value=value,
        options=options,
        width=width,
        border_radius=12,
        filled=True,
        border=ft.InputBorder.OUTLINE,
        focused_border_color=ft.Colors.PRIMARY,
        focused_bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
        on_change=enhanced_dropdown_handler,
    )

    state.register_ui_control(section, key, dropdown)
    return dropdown

def create_modern_slider(
    label: str,
    value: float,
    min_val: float,
    max_val: float,
    divisions: int,
    state: EnhancedSettingsState,
    section: str,
    key: str,
    suffix: str = ""
) -> ft.Column:
    """Create modern Material Design 3 slider with value display and proper event handlers."""
    value_text = ft.Text(f"{value}{suffix}", size=14, weight=ft.FontWeight.W_500)

    def enhanced_slider_change(e):
        try:
            new_value = e.control.value
            value_text.value = f"{new_value}{suffix}"
            value_text.update()

            success = state.update_setting(section, key, new_value)

            if success:
                # Visual feedback for slider
                e.control.active_color = ft.Colors.PRIMARY
                e.control.update()

                # Show notification for important sliders
                important_sliders = {'refresh_interval', 'cpu_threshold', 'memory_threshold'}
                if key in important_sliders and state.state_manager:
                    state.state_manager.add_notification(
                        f"{label} set to {new_value}{suffix}",
                        "info",
                        auto_dismiss=2
                    )
            else:
                # Show error feedback
                e.control.active_color = ft.Colors.ERROR
                e.control.update()

        except Exception as ex:
            logger.error(f"Slider handler error for {section}.{key}: {ex}")
            if state.state_manager:
                state.state_manager.add_notification(f"Error updating {label}", "error")

    # Enhanced slider with better interaction feedback
    def on_slider_start(e):
        """Handle when user starts dragging slider."""
        e.control.thumb_color = ft.Colors.with_opacity(0.8, ft.Colors.PRIMARY)
        e.control.update()

    def on_slider_end(e):
        """Handle when user stops dragging slider."""
        e.control.thumb_color = ft.Colors.PRIMARY
        e.control.update()

    slider = ft.Slider(
        min=min_val,
        max=max_val,
        divisions=divisions,
        value=value,
        label="{value}",
        active_color=ft.Colors.PRIMARY,
        inactive_color=ft.Colors.with_opacity(0.3, ft.Colors.PRIMARY),
        thumb_color=ft.Colors.PRIMARY,
        on_change=enhanced_slider_change,
        on_change_start=on_slider_start,
        on_change_end=on_slider_end,
    )

    state.register_ui_control(section, key, slider)

    return ft.Column([
        ft.Row([
            ft.Text(label, size=14, weight=ft.FontWeight.W_500),
            ft.Container(expand=True),
            value_text
        ]),
        slider
    ], spacing=5)


def create_enhanced_server_section(state: EnhancedSettingsState) -> ft.Control:
    """Create enhanced server settings section with responsive layout and comprehensive controls."""

    # Network Configuration with proper event handlers
    port_field = create_modern_text_field(
        "Server Port",
        state.get_setting('server', 'port', 1256),
        state, 'server', 'port',
        validator=validate_port,
        data_type=int,
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.ROUTER
    )

    host_field = create_modern_text_field(
        "Server Host",
        state.get_setting('server', 'host', '127.0.0.1'),
        state, 'server', 'host',
        width=300,
        prefix_icon=ft.Icons.COMPUTER
    )

    # Client Management
    max_clients_field = create_modern_text_field(
        "Maximum Clients",
        state.get_setting('server', 'max_clients', 50),
        state, 'server', 'max_clients',
        validator=validate_max_clients,
        data_type=int,
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.PEOPLE
    )

    timeout_field = create_modern_text_field(
        "Connection Timeout",
        state.get_setting('server', 'timeout', 30),
        state, 'server', 'timeout',
        validator=validate_timeout,
        data_type=int,
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        suffix_text="seconds"
    )

    # Buffer and Performance
    buffer_size_field = create_modern_text_field(
        "Buffer Size",
        state.get_setting('server', 'buffer_size', 4096),
        state, 'server', 'buffer_size',
        validator=validate_file_size,
        data_type=int,
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        suffix_text="bytes"
    )

    # Logging Configuration
    log_level_value = state.get_setting('server', 'log_level', 'INFO')
    if log_level_value is None:
        log_level_value = 'INFO'
    log_level_dropdown = create_modern_dropdown(
        "Log Level",
        log_level_value,
        [
            ft.dropdown.Option("DEBUG", "Debug - Detailed information"),
            ft.dropdown.Option("INFO", "Info - General information"),
            ft.dropdown.Option("WARNING", "Warning - Warning messages"),
            ft.dropdown.Option("ERROR", "Error - Error messages only")
        ],
        state, 'server', 'log_level',
        width=250
    )

    # SSL Configuration
    ssl_switch_value = state.get_setting('server', 'enable_ssl', False)
    if ssl_switch_value is None:
        ssl_switch_value = False
    ssl_switch = create_modern_switch(
        "Enable SSL/TLS",
        ssl_switch_value,
        state, 'server', 'enable_ssl'
    )

    ssl_cert_field = create_modern_text_field(
        "SSL Certificate Path",
        state.get_setting('server', 'ssl_cert_path', ''),
        state, 'server', 'ssl_cert_path',
        width=400,
        prefix_icon=ft.Icons.SECURITY
    )

    ssl_key_field = create_modern_text_field(
        "SSL Private Key Path",
        state.get_setting('server', 'ssl_key_path', ''),
        state, 'server', 'ssl_key_path',
        width=400,
        prefix_icon=ft.Icons.KEY
    )

    # Create responsive layout using ResponsiveRow
    network_settings = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Network Settings", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.PRIMARY),
            ft.ResponsiveRow([
                ft.Column([port_field], col={"sm": 12, "md": 6}),
                ft.Column([create_modern_reset_button(port_field, 1256, state, "port")], col={"sm": 12, "md": 6}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([host_field], col={"sm": 12, "md": 6}),
                ft.Column([create_modern_reset_button(host_field, "127.0.0.1", state, "host")], col={"sm": 12, "md": 6}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Client Management section with responsive layout
    client_settings = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Client Management", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.SECONDARY),
            ft.ResponsiveRow([
                ft.Column([max_clients_field], col={"sm": 12, "md": 6}),
                ft.Column([create_modern_reset_button(max_clients_field, 50, state, "max clients")], col={"sm": 12, "md": 6}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([timeout_field], col={"sm": 12, "md": 6}),
                ft.Column([create_modern_reset_button(timeout_field, 30, state, "timeout")], col={"sm": 12, "md": 6}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Performance settings with responsive layout
    performance_settings = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Performance Settings", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.TERTIARY),
            ft.ResponsiveRow([
                ft.Column([buffer_size_field], col={"sm": 12, "md": 6}),
                ft.Column([create_modern_reset_button(buffer_size_field, 4096, state, "buffer size")], col={"sm": 12, "md": 6}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([log_level_dropdown], col={"sm": 12, "md": 12}),
            ], spacing=5),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # SSL/TLS Configuration with responsive layout
    ssl_settings = ft.ResponsiveRow([
        ft.Column([
            ft.Text("SSL/TLS Security", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.ERROR),
            ft.ResponsiveRow([
                ft.Column([ssl_switch], col={"sm": 12, "md": 12}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([ssl_cert_field], col={"sm": 12, "md": 10}),
                ft.Column([create_modern_reset_button(ssl_cert_field, "", state, "SSL certificate")], col={"sm": 12, "md": 2}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([ssl_key_field], col={"sm": 12, "md": 10}),
                ft.Column([create_modern_reset_button(ssl_key_field, "", state, "SSL key")], col={"sm": 12, "md": 2}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Use create_modern_card for consistent styling
    return create_modern_card(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.DNS, size=24, color=ft.Colors.PRIMARY),
                ft.Text("Server Configuration", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

            # All settings sections with responsive layout
            ft.Container(
                content=network_settings,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
                border_radius=8,
            ),
            ft.Container(
                content=client_settings,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.SECONDARY),
                border_radius=8,
            ),
            ft.Container(
                content=performance_settings,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.TERTIARY),
                border_radius=8,
            ),
            ft.Container(
                content=ssl_settings,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ERROR),
                border_radius=8,
            ),
        ], spacing=20),
        elevation="elevated",
        hover_effect=True,
        padding=20,
        return_type="container"
    )


def create_enhanced_gui_section(state: EnhancedSettingsState) -> ft.Control:
    """Create enhanced GUI settings section with responsive layout and comprehensive controls."""

    def handle_theme_toggle(value):
        """Handle theme mode changes with immediate application."""
        new_mode = "dark" if value else "light"
        state.update_setting('gui', 'theme_mode', new_mode)

        if state.page:
            state.page.theme_mode = ft.ThemeMode.DARK if value else ft.ThemeMode.LIGHT
            state.page.update()  # Page update needed for theme change

            if state.state_manager:
                state.state_manager.broadcast_settings_event("theme_change", {"theme_mode": new_mode})

    # Theme and Appearance
    theme_switch = create_modern_switch(
        "Dark Mode",
        state.get_setting('gui', 'theme_mode', 'dark') == 'dark',
        state, 'gui', 'theme_mode',
        on_change_callback=handle_theme_toggle
    )

    animations_switch_value = state.get_setting('gui', 'animations_enabled', True)
    if animations_switch_value is None:
        animations_switch_value = True
    animations_switch = create_modern_switch(
        "Enable Animations",
        animations_switch_value,
        state, 'gui', 'animations_enabled'
    )

    sound_switch_value = state.get_setting('gui', 'sound_enabled', False)
    if sound_switch_value is None:
        sound_switch_value = False
    sound_switch = create_modern_switch(
        "Sound Effects",
        sound_switch_value,
        state, 'gui', 'sound_enabled'
    )

    # Refresh and Updates
    auto_refresh_switch_value = state.get_setting('gui', 'auto_refresh', True)
    if auto_refresh_switch_value is None:
        auto_refresh_switch_value = True
    auto_refresh_switch = create_modern_switch(
        "Auto Refresh Data",
        auto_refresh_switch_value,
        state, 'gui', 'auto_refresh'
    )

    refresh_interval_value = state.get_setting('gui', 'refresh_interval', 5)
    if refresh_interval_value is None:
        refresh_interval_value = 5
    refresh_interval_slider = create_modern_slider(
        "Refresh Interval",
        float(refresh_interval_value),
        1.0, 30.0, 29,
        state, 'gui', 'refresh_interval',
        suffix=" seconds"
    )

    # Notifications and Feedback
    notifications_switch_value = state.get_setting('gui', 'notifications', True)
    if notifications_switch_value is None:
        notifications_switch_value = True
    notifications_switch = create_modern_switch(
        "Show Notifications",
        notifications_switch_value,
        state, 'gui', 'notifications'
    )

    # Data Display
    page_size_field = create_modern_text_field(
        "Items per Page",
        state.get_setting('gui', 'page_size', 50),
        state, 'gui', 'page_size',
        data_type=int,
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.VIEW_LIST
    )

    # Language Selection
    language_value = state.get_setting('gui', 'language', 'en')
    if language_value is None:
        language_value = 'en'
    language_dropdown = create_modern_dropdown(
        "Language",
        language_value,
        [
            ft.dropdown.Option("en", "English"),
            ft.dropdown.Option("es", "Español"),
            ft.dropdown.Option("fr", "Français"),
            ft.dropdown.Option("de", "Deutsch"),
            ft.dropdown.Option("zh", "中文"),
        ],
        state, 'gui', 'language',
        width=200
    )

    # Theme and Appearance with responsive layout
    theme_settings = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Theme & Appearance", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.PRIMARY),
            ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.DARK_MODE, size=20),
                        theme_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 6}),
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ANIMATION, size=20),
                        animations_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 6}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.VOLUME_UP, size=20),
                        sound_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 6}),
                ft.Column([
                    ft.Row([
                        language_dropdown,
                        create_modern_reset_button(language_dropdown, "en", state, "language")
                    ], spacing=10)
                ], col={"sm": 12, "md": 6}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Data Refresh Settings with responsive layout
    refresh_settings = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Data & Refresh", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.SECONDARY),
            ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.REFRESH, size=20),
                        auto_refresh_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 12}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([refresh_interval_slider], col={"sm": 12, "md": 12}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([page_size_field], col={"sm": 12, "md": 8}),
                ft.Column([create_modern_reset_button(page_size_field, 50, state, "page size")], col={"sm": 12, "md": 4}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Notifications with responsive layout
    notification_settings = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Notifications & Feedback", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.TERTIARY),
            ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS, size=20),
                        notifications_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 12}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Use create_modern_card for consistent styling
    return create_modern_card(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.PALETTE, size=24, color=ft.Colors.PRIMARY),
                ft.Text("User Interface", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

            # All settings sections with responsive layout
            ft.Container(
                content=theme_settings,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
                border_radius=8,
            ),
            ft.Container(
                content=refresh_settings,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.SECONDARY),
                border_radius=8,
            ),
            ft.Container(
                content=notification_settings,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.TERTIARY),
                border_radius=8,
            ),
        ], spacing=20),
        elevation="elevated",
        hover_effect=True,
        padding=20,
        return_type="container"
    )


def create_enhanced_monitoring_section(state: EnhancedSettingsState) -> ft.Control:
    """Create enhanced monitoring settings section with responsive layout and comprehensive controls."""

    # Core Monitoring
    monitoring_switch_value = bool(state.get_setting('monitoring', 'enabled', True))
    monitoring_switch = create_modern_switch(
        "Enable System Monitoring",
        monitoring_switch_value,
        state, 'monitoring', 'enabled'
    )

    interval_field = create_modern_text_field(
        "Monitoring Interval",
        state.get_setting('monitoring', 'interval', 2),
        state, 'monitoring', 'interval',
        validator=validate_monitoring_interval,
        data_type=int,
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        suffix_text="seconds",
        prefix_icon=ft.Icons.TIMER
    )

    # Alert Configuration
    alerts_switch_value = state.get_setting('monitoring', 'alerts', True)
    if alerts_switch_value is None:
        alerts_switch_value = True
    alerts_switch = create_modern_switch(
        "Performance Alerts",
        alerts_switch_value,
        state, 'monitoring', 'alerts'
    )

    # Threshold Sliders
    cpu_threshold_value = state.get_setting('monitoring', 'cpu_threshold', 80)
    if cpu_threshold_value is None:
        cpu_threshold_value = 80
    cpu_threshold_slider = create_modern_slider(
        "CPU Alert Threshold",
        float(cpu_threshold_value),
        50.0, 95.0, 45,
        state, 'monitoring', 'cpu_threshold',
        suffix="%"
    )

    memory_threshold_value = state.get_setting('monitoring', 'memory_threshold', 85)
    if memory_threshold_value is None:
        memory_threshold_value = 85
    memory_threshold_slider = create_modern_slider(
        "Memory Alert Threshold",
        float(memory_threshold_value),
        60.0, 95.0, 35,
        state, 'monitoring', 'memory_threshold',
        suffix="%"
    )

    disk_threshold_value = state.get_setting('monitoring', 'disk_threshold', 90)
    if disk_threshold_value is None:
        disk_threshold_value = 90
    disk_threshold_slider = create_modern_slider(
        "Disk Alert Threshold",
        float(disk_threshold_value),
        70.0, 98.0, 28,
        state, 'monitoring', 'disk_threshold',
        suffix="%"
    )

    # Monitoring Features
    network_monitoring_switch_value = state.get_setting('monitoring', 'network_monitoring', True)
    if network_monitoring_switch_value is None:
        network_monitoring_switch_value = True
    network_monitoring_switch = create_modern_switch(
        "Network Monitoring",
        network_monitoring_switch_value,
        state, 'monitoring', 'network_monitoring'
    )

    log_monitoring_switch_value = state.get_setting('monitoring', 'log_monitoring', True)
    if log_monitoring_switch_value is None:
        log_monitoring_switch_value = True
    log_monitoring_switch = create_modern_switch(
        "Log Monitoring",
        log_monitoring_switch_value,
        state, 'monitoring', 'log_monitoring'
    )

    # Core monitoring settings with responsive layout
    core_monitoring = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Core Monitoring", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.PRIMARY),
            ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.MONITOR, size=20),
                        monitoring_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 12}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([interval_field], col={"sm": 12, "md": 8}),
                ft.Column([create_modern_reset_button(interval_field, 2, state, "interval")], col={"sm": 12, "md": 4}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Alert configuration with responsive layout
    alert_settings = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Alert Configuration", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.SECONDARY),
            ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=20),
                        alerts_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 12}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([cpu_threshold_slider], col={"sm": 12, "md": 12}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([memory_threshold_slider], col={"sm": 12, "md": 12}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([disk_threshold_slider], col={"sm": 12, "md": 12}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Monitoring features with responsive layout
    monitoring_features = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Monitoring Features", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.TERTIARY),
            ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.NETWORK_CHECK, size=20),
                        network_monitoring_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 6}),
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.DESCRIPTION, size=20),
                        log_monitoring_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 6}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Use create_modern_card for consistent styling
    return create_modern_card(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.MONITOR_HEART, size=24, color=ft.Colors.PRIMARY),
                ft.Text("System Monitoring", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

            # All monitoring sections with responsive layout
            ft.Container(
                content=core_monitoring,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
                border_radius=8,
            ),
            ft.Container(
                content=alert_settings,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.SECONDARY),
                border_radius=8,
            ),
            ft.Container(
                content=monitoring_features,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.TERTIARY),
                border_radius=8,
            ),
        ], spacing=20),
        elevation="elevated",
        hover_effect=True,
        padding=20,
        return_type="container"
    )

def create_enhanced_logging_section(state: EnhancedSettingsState) -> ft.Control:
    """Create enhanced logging settings section with responsive layout."""

    # Log Level and Output
    log_level_value = state.get_setting('logging', 'level', 'INFO')
    if log_level_value is None:
        log_level_value = 'INFO'
    log_level_dropdown = create_modern_dropdown(
        "Log Level",
        log_level_value,
        [
            ft.dropdown.Option("DEBUG", "Debug - Detailed information"),
            ft.dropdown.Option("INFO", "Info - General information"),
            ft.dropdown.Option("WARNING", "Warning - Warning messages"),
            ft.dropdown.Option("ERROR", "Error - Error messages only")
        ],
        state, 'logging', 'level',
        width=300
    )

    console_output_value = state.get_setting('logging', 'console_output', True)
    if console_output_value is None:
        console_output_value = True
    console_output_switch = create_modern_switch(
        "Console Output",
        console_output_value,
        state, 'logging', 'console_output'
    )

    # File Configuration
    log_file_field = create_modern_text_field(
        "Log File Path",
        state.get_setting('logging', 'file_path', 'server.log'),
        state, 'logging', 'file_path',
        width=400,
        prefix_icon=ft.Icons.DESCRIPTION
    )

    max_file_size_field = create_modern_text_field(
        "Max File Size",
        state.get_setting('logging', 'max_file_size', 10485760),
        state, 'logging', 'max_file_size',
        validator=validate_file_size,
        data_type=int,
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        suffix_text="bytes"
    )

    backup_count_field = create_modern_text_field(
        "Backup File Count",
        state.get_setting('logging', 'backup_count', 5),
        state, 'logging', 'backup_count',
        data_type=int,
        width=150,
        keyboard_type=ft.KeyboardType.NUMBER
    )

    # Log level and output with responsive layout
    log_output = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Log Level & Output", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.PRIMARY),
            ft.ResponsiveRow([
                ft.Column([log_level_dropdown], col={"sm": 12, "md": 12}),
            ], spacing=5),
            ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TERMINAL, size=20),
                        console_output_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 12}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # File configuration with responsive layout
    file_config = ft.ResponsiveRow([
        ft.Column([
            ft.Text("File Configuration", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.SECONDARY),
            ft.ResponsiveRow([
                ft.Column([log_file_field], col={"sm": 12, "md": 8}),
                ft.Column([create_modern_reset_button(log_file_field, "server.log", state, "log file")], col={"sm": 12, "md": 4}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([max_file_size_field], col={"sm": 12, "md": 8}),
                ft.Column([create_modern_reset_button(max_file_size_field, 10485760, state, "file size")], col={"sm": 12, "md": 4}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([backup_count_field], col={"sm": 12, "md": 8}),
                ft.Column([create_modern_reset_button(backup_count_field, 5, state, "backup count")], col={"sm": 12, "md": 4}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Use create_modern_card for consistent styling
    return create_modern_card(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.ARTICLE, size=24, color=ft.Colors.PRIMARY),
                ft.Text("Logging Configuration", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

            # All logging sections with responsive layout
            ft.Container(
                content=log_output,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
                border_radius=8,
            ),
            ft.Container(
                content=file_config,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.SECONDARY),
                border_radius=8,
            ),
        ], spacing=20),
        elevation="elevated",
        hover_effect=True,
        padding=20,
        return_type="container"
    )

def create_enhanced_security_section(state: EnhancedSettingsState) -> ft.Control:
    """Create enhanced security settings section with responsive layout."""

    # Authentication
    auth_switch_value = state.get_setting('security', 'authentication_required', False)
    if auth_switch_value is None:
        auth_switch_value = False
    auth_switch = create_modern_switch(
        "Require Authentication",
        auth_switch_value,
        state, 'security', 'authentication_required'
    )

    session_timeout_field = create_modern_text_field(
        "Session Timeout",
        state.get_setting('security', 'session_timeout', 3600),
        state, 'security', 'session_timeout',
        validator=validate_timeout,
        data_type=int,
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        suffix_text="seconds"
    )

    # Login Security
    max_login_attempts_field = create_modern_text_field(
        "Max Login Attempts",
        state.get_setting('security', 'max_login_attempts', 5),
        state, 'security', 'max_login_attempts',
        data_type=int,
        width=150,
        keyboard_type=ft.KeyboardType.NUMBER
    )

    lockout_duration_field = create_modern_text_field(
        "Lockout Duration",
        state.get_setting('security', 'lockout_duration', 900),
        state, 'security', 'lockout_duration',
        validator=validate_timeout,
        data_type=int,
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        suffix_text="seconds"
    )

    # Authentication settings with responsive layout
    auth_settings = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Authentication", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.PRIMARY),
            ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.LOGIN, size=20),
                        auth_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 12}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([session_timeout_field], col={"sm": 12, "md": 8}),
                ft.Column([create_modern_reset_button(session_timeout_field, 3600, state, "session timeout")], col={"sm": 12, "md": 4}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Login security settings with responsive layout
    login_security = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Login Security", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.ERROR),
            ft.ResponsiveRow([
                ft.Column([max_login_attempts_field], col={"sm": 12, "md": 8}),
                ft.Column([create_modern_reset_button(max_login_attempts_field, 5, state, "max attempts")], col={"sm": 12, "md": 4}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([lockout_duration_field], col={"sm": 12, "md": 8}),
                ft.Column([create_modern_reset_button(lockout_duration_field, 900, state, "lockout duration")], col={"sm": 12, "md": 4}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Use create_modern_card for consistent styling
    return create_modern_card(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.SECURITY, size=24, color=ft.Colors.PRIMARY),
                ft.Text("Security Configuration", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

            # All security sections with responsive layout
            ft.Container(
                content=auth_settings,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
                border_radius=8,
            ),
            ft.Container(
                content=login_security,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ERROR),
                border_radius=8,
            ),
        ], spacing=20),
        elevation="elevated",
        hover_effect=True,
        padding=20,
        return_type="container"
    )


def create_enhanced_backup_section(state: EnhancedSettingsState) -> ft.Control:
    """Create enhanced backup settings section with responsive layout."""

    # Auto Backup
    auto_backup_switch_value = bool(state.get_setting('backup', 'auto_backup_settings', True))
    auto_backup_switch = create_modern_switch(
        "Auto Backup Settings",
        auto_backup_switch_value,
        state, 'backup', 'auto_backup_settings'
    )

    backup_interval_value = state.get_setting('backup', 'backup_interval_hours', 24)
    if backup_interval_value is None:
        backup_interval_value = 24
    backup_interval_slider = create_modern_slider(
        "Backup Interval",
        float(backup_interval_value),
        1.0, 168.0, 167,  # 1 hour to 1 week
        state, 'backup', 'backup_interval_hours',
        suffix=" hours"
    )

    max_backups_field = create_modern_text_field(
        "Maximum Backups",
        state.get_setting('backup', 'max_backups', 10),
        state, 'backup', 'max_backups',
        data_type=int,
        width=150,
        keyboard_type=ft.KeyboardType.NUMBER
    )

    compression_switch_value = state.get_setting('backup', 'compression_enabled', True)
    if compression_switch_value is None:
        compression_switch_value = True
    compression_switch = create_modern_switch(
        "Enable Compression",
        compression_switch_value,
        state, 'backup', 'compression_enabled'
    )

    # Backup settings with responsive layout
    backup_settings = ft.ResponsiveRow([
        ft.Column([
            ft.Text("Automatic Backup", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.PRIMARY),
            ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SCHEDULE, size=20),
                        auto_backup_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 6}),
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.COMPRESS, size=20),
                        compression_switch,
                    ], spacing=10)
                ], col={"sm": 12, "md": 6}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([backup_interval_slider], col={"sm": 12, "md": 12}),
            ], spacing=10),
            ft.ResponsiveRow([
                ft.Column([max_backups_field], col={"sm": 12, "md": 8}),
                ft.Column([create_modern_reset_button(max_backups_field, 10, state, "max backups")], col={"sm": 12, "md": 4}),
            ], spacing=10),
        ], spacing=10, col={"sm": 12, "md": 12}),
    ], spacing=10)

    # Use create_modern_card for consistent styling
    return create_modern_card(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.BACKUP, size=24, color=ft.Colors.PRIMARY),
                ft.Text("Backup Configuration", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

            # All backup sections with responsive layout
            ft.Container(
                content=backup_settings,
                padding=ft.Padding(15, 10, 15, 10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
                border_radius=8,
            ),
        ], spacing=20),
        elevation="elevated",
        hover_effect=True,
        padding=20,
        return_type="container"
    )


async def enhanced_export_settings(state: EnhancedSettingsState, export_format: str = "json"):
    """Enhanced export settings with multiple formats and server integration."""
    try:
        if state.state_manager:
            state.state_manager.start_progress("settings_export", total_steps=2, message="Preparing")
            state.state_manager.set_loading("settings_export", True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if export_format == "json":
            backup_file = f"settings_backup_{timestamp}.json"
            backup_data = {
                'exported_at': timestamp,
                'version': '2.0',
                'settings': state.current_settings,
                'metadata': {
                    'export_format': export_format,
                    'app_version': 'FletV2',
                    'total_sections': len(state.current_settings)
                }
            }

            backup_path = Path(backup_file)
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

        elif export_format == "ini":
            backup_file = f"settings_backup_{timestamp}.ini"
            backup_path = Path(backup_file)
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            import configparser
            config = configparser.ConfigParser()

            for section, settings in state.current_settings.items():
                config[section] = {}
                for key, value in settings.items():
                    config[section][key] = str(value)

            with open(backup_file, 'w', encoding='utf-8') as f:
                config.write(f)

        else:
            raise ValueError(f"Unsupported export format: {export_format}")

        if state.state_manager:
            state.state_manager.update_progress("settings_export", step=1, message="Writing file")
            state.state_manager.add_notification(f"Settings exported to {backup_file}", "success")

        logger.info(f"Settings exported to {backup_file}")
        return {'success': True, 'file': backup_file}

    except Exception as e:
        logger.error(f"Export failed: {e}")
        if state.state_manager:
            state.state_manager.set_error_state("settings_export", str(e))
        return {'success': False, 'error': str(e)}
    finally:
        if state.state_manager:
            state.state_manager.clear_progress("settings_export")
            state.state_manager.set_loading("settings_export", False)

async def enhanced_import_settings(state: EnhancedSettingsState, file_path: str):
    """Enhanced import settings with validation and server integration."""
    try:
        if state.state_manager:
            state.state_manager.set_loading("settings_import", True)

        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)

            # Handle both old and new format
            if 'settings' in imported_data:
                imported = imported_data['settings']
                version = imported_data.get('version', '1.0')
                logger.info(f"Importing settings version {version}")
            else:
                imported = imported_data

        elif file_ext == '.ini':
            import configparser
            config = configparser.ConfigParser()
            config.read(file_path, encoding='utf-8')

            imported = {}
            for section in config.sections():
                imported[section] = dict(config[section])
                # Convert string values back to appropriate types
                for key, value in imported[section].items():
                    if value.lower() in ('true', 'false'):
                        imported[section][key] = value.lower() == 'true'
                    elif value.isdigit():
                        imported[section][key] = int(value)
                    elif value.replace('.', '').isdigit():
                        imported[section][key] = float(value)

        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        if not isinstance(imported, dict):
            raise ValueError("Invalid settings format")

        # Validate and merge with defaults
        default_settings = state._load_default_settings()
        merged_settings = state._deep_merge_settings(default_settings, imported)

        # Validate settings before applying
        validation_result = await state.validate_settings_async(merged_settings)
        if not validation_result.get('success', True):
            validation_data = validation_result.get('data', {})
            if not validation_data.get('valid', True):
                errors = validation_data.get('errors', [])
                raise ValueError(f"Settings validation failed: {'; '.join(errors)}")

        # Apply settings
        state.current_settings = merged_settings
        state._update_ui_from_settings()

        # Update state manager
        if state.state_manager:
            await state.state_manager.update_settings_async(state.current_settings, "import")
            state.state_manager.add_notification("Settings imported successfully", "success")

        logger.info("Settings imported successfully")
        return {'success': True}

    except Exception as e:
        logger.error(f"Import failed: {e}")
        if state.state_manager:
            state.state_manager.set_error_state("settings_import", str(e))
        return {'success': False, 'error': str(e)}
    finally:
        if state.state_manager:
            state.state_manager.set_loading("settings_import", False)

def create_modern_progress_indicator(operation: str, state_manager: Optional[StateManager]) -> ft.Container:
    """Create modern progress indicator with enhanced Material Design 3 styling and state management integration."""
    # Enhanced progress ring with Material Design 3 styling
    progress_ring = ft.ProgressRing(
        width=20,
        height=20,
        visible=False,
        color=ft.Colors.PRIMARY,
        stroke_width=3
    )

    # Enhanced progress text with better typography
    progress_text = ft.Text(
        "",
        size=12,
        visible=False,
        color=ft.Colors.ON_SURFACE_VARIANT,
        weight=ft.FontWeight.W_500
    )

    def update_progress(loading_states, old_states):
        try:
            is_loading = loading_states.get(operation, False)
            progress_ring.visible = is_loading
            progress_text.visible = is_loading
            progress_text.value = f"{operation.replace('_', ' ').title()}..." if is_loading else ""

            # Safe update with error handling
            if hasattr(progress_ring, 'update'):
                progress_ring.update()
            if hasattr(progress_text, 'update'):
                progress_text.update()
        except Exception as e:
            logger.debug(f"Progress indicator update error for {operation}: {e}")

    if state_manager:
        try:
            state_manager.subscribe("loading_states", update_progress)
        except Exception as e:
            logger.debug(f"Failed to subscribe progress indicator for {operation}: {e}")

    return ft.Container(
        content=ft.Row([
            progress_ring,
            progress_text
        ], spacing=5),
        visible=False,
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )

def create_enhanced_action_buttons(state: EnhancedSettingsState) -> ft.Column:
    """Create enhanced action buttons with responsive layout, modern styling and progress indicators."""

    # Progress indicators
    save_progress = create_modern_progress_indicator("settings_save", state.state_manager)
    export_progress = create_modern_progress_indicator("settings_export", state.state_manager)
    import_progress = create_modern_progress_indicator("settings_import", state.state_manager)

    async def save_settings_handler(e):
        success = await state.save_settings_async()
        if not success and state.state_manager:
            state.state_manager.add_notification("Failed to save settings", "error")

    async def export_handler(e):
        result = await enhanced_export_settings(state, "json")
        if not result['success'] and state.state_manager:
            state.state_manager.add_notification(f"Export failed: {result.get('error', 'Unknown error')}", "error")

    async def backup_handler(e):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"settings_backup_{timestamp}"
        result = await state.backup_settings_async(backup_name)
        if not result['success'] and state.state_manager:
            state.state_manager.add_notification(f"Backup failed: {result.get('error', 'Unknown error')}", "error")

    def reset_all_settings(e):
        def confirm_reset(e):
            state.current_settings = state._load_default_settings()
            state._update_ui_from_settings()
            if state.page:
                state.page.dialog.open = False
                state.page.dialog.update()
            if state.state_manager:
                state.state_manager.add_notification("Settings reset to defaults", "info")

        def cancel_reset(e):
            if state.page:
                state.page.dialog.open = False
                state.page.dialog.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Reset All Settings"),
            content=ft.Text(
                "Are you sure you want to reset all settings to their default values?\n\n"
                "This action cannot be undone and will affect:\n"
                "• Server configuration\n"
                "• User interface preferences\n"
                "• Monitoring settings\n"
                "• Security settings\n"
                "• All other configurations"
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    icon=ft.Icons.CANCEL,
                    on_click=cancel_reset,
                    style=ft.ButtonStyle(color=ft.Colors.ON_SURFACE)
                ),
                ft.FilledButton(
                    "Reset All",
                    icon=ft.Icons.RESTORE,
                    on_click=confirm_reset,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        if state.page:
            state.page.dialog = dialog
            dialog.open = True
            state.page.dialog.update()


    # FilePicker lifecycle management
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            state.page.run_task(enhanced_import_settings, state, e.files[0].path)
        else:
            if state.state_manager:
                state.state_manager.add_notification("Import cancelled", "info")

    # Ensure only one FilePicker per view instance
    if not hasattr(state, 'file_picker') or state.file_picker is None:
        state.file_picker = ft.FilePicker(on_result=pick_files_result)
    file_picker = state.file_picker
    # Add to overlay if not already present
    if state.page and file_picker not in state.page.overlay:
        state.page.overlay.append(file_picker)

    def import_handler(e):
        try:
            state.file_picker.pick_files(
                allowed_extensions=["json", "ini"],
                dialog_title="Select Settings File"
            )
        except Exception as e:
            logger.error(f"Error opening file picker: {e}")
            if state.state_manager:
                state.state_manager.add_notification("Error opening file picker", "error")

    # Create responsive button layout
    return ft.Column([
        ft.ResponsiveRow([
            ft.Column([
                ft.FilledButton(
                    "Save Settings",
                    icon=ft.Icons.SAVE,
                    on_click=lambda e: state.page.run_task(save_settings_handler, e),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY,
                        elevation=2,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    expand=True
                )
            ], col={"sm": 12, "md": 6, "lg": 2}),
            ft.Column([
                ft.OutlinedButton(
                    "Export Backup",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: state.page.run_task(export_handler, e),
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(2, ft.Colors.PRIMARY),
                        color=ft.Colors.PRIMARY,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    expand=True
                )
            ], col={"sm": 12, "md": 6, "lg": 2}),
            ft.Column([
                ft.OutlinedButton(
                    "Create Backup",
                    icon=ft.Icons.BACKUP,
                    on_click=lambda e: state.page.run_task(backup_handler, e),
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(2, ft.Colors.SECONDARY),
                        color=ft.Colors.SECONDARY,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    expand=True
                )
            ], col={"sm": 12, "md": 6, "lg": 2}),
            ft.Column([
                ft.TextButton(
                    "Import Settings",
                    icon=ft.Icons.UPLOAD,
                    on_click=import_handler,
                    style=ft.ButtonStyle(
                        color=ft.Colors.TERTIARY,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    expand=True
                )
            ], col={"sm": 12, "md": 6, "lg": 3}),
            ft.Column([
                ft.TextButton(
                    "Reset All",
                    icon=ft.Icons.RESTORE,
                    on_click=reset_all_settings,
                    style=ft.ButtonStyle(
                        color=ft.Colors.ERROR,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    expand=True
                )
            ], col={"sm": 12, "md": 12, "lg": 3}),
        ], spacing=10),

        # Progress indicators row with responsive layout
        ft.ResponsiveRow([
            ft.Column([save_progress], col={"sm": 12, "md": 4}),
            ft.Column([export_progress], col={"sm": 12, "md": 4}),
            ft.Column([import_progress], col={"sm": 12, "md": 4}),
        ], spacing=20),
    ], spacing=10)

def create_settings_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    state_manager: StateManager
) -> ft.Control:
    """
    Create enhanced settings view with comprehensive server bridge integration and Material Design 3 styling.
    """
    logger.info("Creating enhanced settings view with server bridge integration")

    # Initialize enhanced state management
    settings_state = EnhancedSettingsState(page, server_bridge, state_manager)

    # Status display with enhanced information
    status_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CLOUD_SYNC, size=16),
                ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
            ], spacing=5),
            ft.Row([
                ft.Icon(ft.Icons.SCHEDULE, size=16),
                ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
            ], spacing=5),
        ], spacing=2),
        padding=10,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
        border_radius=8,
    )

    def update_status_display():
        """Update status display with current information."""
        status_lines = status_container.content.controls

        # Server connection status
        if server_bridge:
            connection_status = "Connected to server" if server_bridge.is_connected() else "Using local storage"
            status_lines[0].controls[1].value = connection_status
        else:
            status_lines[0].controls[1].value = "No server bridge"

        # Last saved/loaded status
        if settings_state.last_saved:
            status_lines[1].controls[1].value = f"Last saved: {settings_state.last_saved.strftime('%H:%M:%S')}"
        elif settings_state.last_loaded:
            status_lines[1].controls[1].value = f"Last loaded: {settings_state.last_loaded.strftime('%H:%M:%S')}"
        else:
            status_lines[1].controls[1].value = "No recent activity"

        # Only update if container is attached to page
        if hasattr(status_container, 'page') and status_container.page is not None:
            status_container.update()

    # Subscribe to state changes for reactive status updates
    # Defer subscription setup until view is added to page to prevent "Control must be added to page first" error
    def setup_subscriptions():
        """Set up subscriptions after view is added to page."""
        if state_manager:
            def on_loading_change(loading_states, old_states):
                if loading_states.get("settings_save") or loading_states.get("settings_load"):
                    update_status_display()

            state_manager.subscribe("loading_states", on_loading_change)

    # Store subscription setup function for later execution
    settings_state.setup_subscriptions = setup_subscriptions

    # Enhanced action buttons with responsive layout
    action_buttons = create_enhanced_action_buttons(settings_state)

    # Create enhanced tabs with responsive content
    enhanced_tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        indicator_color=ft.Colors.PRIMARY,
        label_color=ft.Colors.PRIMARY,
        unselected_label_color=ft.Colors.ON_SURFACE_VARIANT,
        tabs=[
            ft.Tab(
                text="Server",
                icon=ft.Icons.DNS,
                content=ft.Container(
                    content=ft.Column([
                        create_enhanced_server_section(settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
            ft.Tab(
                text="Interface",
                icon=ft.Icons.PALETTE,
                content=ft.Container(
                    content=ft.Column([
                        create_enhanced_gui_section(settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
            ft.Tab(
                text="Monitoring",
                icon=ft.Icons.MONITOR_HEART,
                content=ft.Container(
                    content=ft.Column([
                        create_enhanced_monitoring_section(settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
            ft.Tab(
                text="Logging",
                icon=ft.Icons.ARTICLE,
                content=ft.Container(
                    content=ft.Column([
                        create_enhanced_logging_section(settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
            ft.Tab(
                text="Security",
                icon=ft.Icons.SECURITY,
                content=ft.Container(
                    content=ft.Column([
                        create_enhanced_security_section(settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
            ft.Tab(
                text="Backup",
                icon=ft.Icons.BACKUP,
                content=ft.Container(
                    content=ft.Column([
                        create_enhanced_backup_section(settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
        ],
        expand=True,
        scrollable=True,
    )

    # Build main view with responsive layout and enhanced Material Design 3 styling
    main_view = ft.Column([
        # Enhanced header with responsive status display
        ft.Container(
            content=ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, size=28, color=ft.Colors.PRIMARY),
                        ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD),
                    ], spacing=10)
                ], col={"sm": 12, "md": 6}),
                ft.Column([
                    status_container
                ], col={"sm": 12, "md": 6}, alignment=ft.MainAxisAlignment.END),
            ]),
            padding=ft.Padding(20, 20, 20, 10),
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.PRIMARY),
        ),
        ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

        # Enhanced action buttons with responsive layout
        ft.Container(
            content=action_buttons,
            padding=ft.Padding(20, 10, 20, 10),
        ),

        # Enhanced tabs with responsive content
        ft.Container(
            content=enhanced_tabs,
            expand=True,
            padding=ft.Padding(10, 0, 10, 10),
        ),

    ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)

    # Load settings asynchronously with enhanced error handling
    async def load_settings_with_status():
        try:
            success = await settings_state.load_settings_async()
            update_status_display()
            if success:
                logger.info("Settings loaded successfully")
            else:
                logger.warning("Settings load completed with issues")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            if state_manager:
                state_manager.add_notification("Failed to load settings", "error")

    # Modified return to make dispose accessible
    main_view.dispose = settings_state.dispose

    # Run setup after view is constructed
    page.run_task(load_settings_with_status)

    # Call setup function after the view is added to the page
    page.run_task(lambda: setup_view())

    return main_view
    return main_view, lambda: settings_state.dispose(), setup_view
