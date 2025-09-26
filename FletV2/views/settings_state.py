#!/usr/bin/env python3
"""
Settings state management for FletV2 Settings View.

This module contains the EnhancedSettingsState class extracted from views/settings.py
and completed with helper methods (_load_default_settings, _deep_merge_settings,
_update_ui_from_settings, load_settings_async) to keep views lean.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
import flet as ft

# --- PATH SETUP (consistent with repository guidelines) ---
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _p in (_flet_v2_root, _repo_root):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Local imports after path setup
try:  # Prefer absolute package imports
    from FletV2.utils.debug_setup import get_logger  # type: ignore
    from FletV2.utils.server_bridge import ServerBridge  # type: ignore
    from FletV2.utils.state_manager import StateManager  # type: ignore
    from FletV2 import config as _app_config  # type: ignore
except Exception:  # noqa: BLE001 - fallback to relative (development mode)
    from utils.debug_setup import get_logger  # type: ignore
    from utils.server_bridge import ServerBridge  # type: ignore
    from utils.state_manager import StateManager  # type: ignore
    import config as _app_config  # type: ignore

_settings_file_raw = getattr(_app_config, 'SETTINGS_FILE', 'settings.json')
# Normalize to a Path object for filesystem operations
SETTINGS_PATH = _settings_file_raw if isinstance(_settings_file_raw, Path) else Path(_settings_file_raw)

logger = get_logger(__name__)


class EnhancedSettingsState:
    """Enhanced state management with server bridge integration and reactive updates."""

    def __init__(
        self,
        page: ft.Page,
        server_bridge: ServerBridge | None = None,
        state_manager: StateManager | None = None,
    ):
        self.page = page
        self.server_bridge = server_bridge
        self.state_manager = state_manager

        # Concurrency & syncing
        self._auto_save_lock: asyncio.Lock = asyncio.Lock()
        self._auto_save_task: asyncio.Task | None = None
        self._sync_enabled: bool = True
        self._pending_changes: dict[str, dict[str, Any]] = {}

        # UI and validation
        self._ui_refs: dict[str, list[ft.Control]] = {}
        self._validation_errors: dict[str, str] = {}

        # File picker for imports (one per view instance)
        self.file_picker: ft.FilePicker | None = None

        # State
        self.current_settings: dict[str, Any] = self._load_default_settings()
        self.is_saving = False
        self.is_loading = False
        self.last_saved: datetime | None = None
        self.last_loaded: datetime | None = None

        # Subscriptions cleanup callbacks
        self._unsubscribe_callbacks = []

    # ---- UI registration & updates ----
    def register_ui_control(self, section: str, key: str, control: ft.Control):
        """Register UI control for reactive updates."""
        section_key = f"{section}.{key}"
        self._ui_refs.setdefault(section_key, []).append(control)

    def _update_ui_from_settings(self) -> None:
        """Propagate current_settings values to registered controls safely."""
        try:
            for section_key, controls in self._ui_refs.items():
                try:
                    section, key = section_key.split(".", 1)
                except ValueError:
                    continue
                value = self.current_settings.get(section, {}).get(key)
                for ctrl in controls:
                    try:
                        # Compatible with TextField, Switch, Dropdown, Slider
                        if hasattr(ctrl, "value"):
                            ctrl.value = value
                        # Update suffix text for sliders if present
                        if hasattr(ctrl, "update") and getattr(ctrl, "page", None) is not None:
                            ctrl.update()
                    except Exception as e:
                        logger.debug(f"Failed updating control for {section_key}: {e}")
        except Exception as e:
            logger.debug(f"UI update from settings failed: {e}")

    # ---- Persistence helpers ----
    async def save_settings_async(self, auto_save: bool = False) -> bool:
        """Save settings with server bridge integration and validation."""
        if self.is_saving:
            return False

        self.is_saving = True
        try:
            if self.state_manager:
                self.state_manager.set_loading("settings_save", True)

            validation_result = await self.validate_settings_async(self.current_settings)
            if not validation_result.get("success", True):
                validation_data = validation_result.get("data", {})
                if not validation_data.get("valid", True):
                    errors = validation_data.get("errors", [])
                    logger.warning(f"Settings validation failed: {errors}")
                    if self.state_manager:
                        self.state_manager.set_error_state(
                            "settings_validation", "Validation failed", {"errors": errors}
                        )
                    return False

            # Try server bridge first
            if self.server_bridge:
                try:
                    result = await self.server_bridge.save_settings_async(self.current_settings)
                    if result.get("success"):
                        self.last_saved = datetime.now()
                        if self.state_manager:
                            await self.state_manager.update_settings_async(
                                self.current_settings, "server_save"
                            )
                            if not auto_save:
                                self.state_manager.add_notification(
                                    f"Settings saved to server ({result.get('mode', 'server')})",
                                    "success",
                                )
                        logger.info(
                            f"Settings saved to server ({result.get('mode', 'server')})"
                        )
                        await self._save_local_backup()
                        return True
                except Exception as e:
                    logger.warning(
                        f"Server settings save failed, falling back to local: {e}"
                    )

            # Fallback to local file
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                content = json.dumps(self.current_settings, indent=2, ensure_ascii=False)
                await f.write(content)
            self.last_saved = datetime.now()
            if self.state_manager:
                await self.state_manager.update_settings_async(
                    self.current_settings, "local_save"
                )
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
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                content = json.dumps(self.current_settings, indent=2, ensure_ascii=False)
                await f.write(content)
        except Exception as e:
            logger.debug(f"Failed to save local backup: {e}")

    async def load_settings_async(self) -> bool:
        """Load settings from server bridge or local file, update UI and state manager."""
        if self.is_loading:
            return False
        self.is_loading = True
        try:
            loaded: dict[str, Any] | None = None

            # Try server first
            if self.server_bridge:
                try:
                    result = await self.server_bridge.load_settings_async()
                    if isinstance(result, dict) and result.get("success"):
                        loaded = result.get("data") or result.get("settings")
                except Exception as e:
                    logger.debug(f"Server settings load failed; will try local. {e}")

            # Fallback local
            if loaded is None:
                try:
                    if SETTINGS_PATH.exists():
                        async with aiofiles.open(SETTINGS_PATH, encoding="utf-8") as f:
                            content = await f.read()
                            loaded = json.loads(content)
                except Exception as e:
                    logger.debug(f"Local settings load failed: {e}")

            # Merge with defaults and apply
            base = self._load_default_settings()
            merged = self._deep_merge_settings(base, loaded or {})
            self.current_settings = merged
            self.last_loaded = datetime.now()
            self._update_ui_from_settings()

            if self.state_manager:
                await self.state_manager.update_settings_async(self.current_settings, "load")
            return True
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            if self.state_manager:
                self.state_manager.set_error_state("settings_load", str(e))
            return False
        finally:
            self.is_loading = False

    # ---- Validation helpers (server-backed or local fallbacks) ----
    def _validate_server_settings(self, server_settings: dict[str, Any], validation_result: dict[str, Any]) -> None:
        """Validate server-specific settings."""
        port = server_settings.get("port")
        if port and (not isinstance(port, int) or port < 1024 or port > 65535):
            validation_result["errors"].append("Port must be between 1024-65535")
            validation_result["valid"] = False

        if server_settings.get("enable_ssl", False):
            cert = server_settings.get("ssl_cert_path", "").strip()
            key = server_settings.get("ssl_key_path", "").strip()
            if not cert:
                validation_result["errors"].append(
                    "SSL certificate path is required when SSL is enabled"
                )
                validation_result["valid"] = False
            if not key:
                validation_result["errors"].append(
                    "SSL key path is required when SSL is enabled"
                )
                validation_result["valid"] = False

    def _validate_backup_settings(self, backup_settings: dict[str, Any], validation_result: dict[str, Any]) -> None:
        if backup_settings.get("auto_backup", False):
            interval = backup_settings.get("backup_interval_hours", 0)
            if not isinstance(interval, (int, float)) or interval <= 0:
                validation_result["errors"].append(
                    "Backup interval must be greater than 0 hours when auto-backup is enabled"
                )
                validation_result["valid"] = False
            path = backup_settings.get("backup_path", "").strip()
            if not path:
                validation_result["errors"].append(
                    "Backup path is required when auto-backup is enabled"
                )
                validation_result["valid"] = False

    def _validate_monitoring_settings(self, monitoring_settings: dict[str, Any], validation_result: dict[str, Any]) -> None:
        if not monitoring_settings.get("enabled", False):
            return
        cpu = monitoring_settings.get("cpu_threshold", 80)
        mem = monitoring_settings.get("memory_threshold", 85)
        if not isinstance(cpu, (int, float)) or cpu <= 0 or cpu > 100:
            validation_result["errors"].append("CPU threshold must be between 1-100 when monitoring is enabled")
            validation_result["valid"] = False
        if not isinstance(mem, (int, float)) or mem <= 0 or mem > 100:
            validation_result["errors"].append("Memory threshold must be between 1-100 when monitoring is enabled")
            validation_result["valid"] = False
        if isinstance(cpu, (int, float)) and isinstance(mem, (int, float)) and cpu >= mem:
            validation_result["warnings"].append(
                "CPU threshold is higher than memory threshold - this may cause frequent alerts"
            )

    def _validate_gui_settings(self, gui_settings: dict[str, Any], validation_result: dict[str, Any]) -> None:
        if not gui_settings.get("auto_refresh", False):
            return
        refresh = gui_settings.get("refresh_interval", 5)
        if not isinstance(refresh, (int, float)) or refresh < 1:
            validation_result["errors"].append(
                "Refresh interval must be at least 1 second when auto-refresh is enabled"
            )
            validation_result["valid"] = False
        elif refresh < 3:
            validation_result["warnings"].append(
                "Refresh intervals below 3 seconds may impact performance"
            )

    async def validate_settings_async(self, settings_data: dict[str, Any]):
        try:
            if self.server_bridge:
                return await self.server_bridge.validate_settings_async(settings_data)
            validation_result = {"valid": True, "errors": [], "warnings": []}
            if "server" in settings_data:
                self._validate_server_settings(settings_data["server"], validation_result)
            if "backup" in settings_data:
                self._validate_backup_settings(settings_data["backup"], validation_result)
            if "monitoring" in settings_data:
                self._validate_monitoring_settings(settings_data["monitoring"], validation_result)
            if "gui" in settings_data:
                self._validate_gui_settings(settings_data["gui"], validation_result)
            return {"success": True, "data": validation_result}
        except Exception as e:
            logger.error(f"Settings validation failed: {e}")
            return {"success": False, "error": str(e)}

    # ---- State updates & autosave ----
    def update_setting(self, section: str, key: str, value, validate: bool = True) -> bool:
        try:
            if section not in self.current_settings:
                self.current_settings[section] = {}
            old_value = self.current_settings[section].get(key)
            self.current_settings[section][key] = value
            change_key = f"{section}.{key}"
            self._pending_changes[change_key] = {
                "old_value": old_value,
                "new_value": value,
                "timestamp": time.time(),
            }
            if self._sync_enabled:
                self._schedule_auto_save()
            if self.state_manager:
                self.state_manager.update(f"settings.{section}.{key}", value, source="user_input")
            logger.debug(f"Setting updated: {section}.{key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to update setting {section}.{key}: {e}")
            return False

    def _schedule_auto_save(self):
        if self._auto_save_task:
            self._auto_save_task.cancel()

        async def auto_save_worker():
            try:
                await asyncio.sleep(2.0)  # Debounce
                async with self._auto_save_lock:
                    pending_snapshot = self._pending_changes.copy()
                    if pending_snapshot:
                        await self.save_settings_async(auto_save=True)
                        for key in pending_snapshot:
                            self._pending_changes.pop(key, None)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.debug(f"Auto-save failed: {e}")

        async def start_auto_save():
            if self._auto_save_task and not self._auto_save_task.done():
                try:
                    await self._auto_save_task
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass
                finally:
                    self._auto_save_task = None
            self._auto_save_task = asyncio.create_task(auto_save_worker())

        asyncio.create_task(start_auto_save())

    def get_setting(self, section: str, key: str, default=None):
        return self.current_settings.get(section, {}).get(key, default)

    # ---- Subscriptions & events ----
    def _on_settings_changed(self, settings_data, old_data):
        if self._sync_enabled and settings_data != self.current_settings:
            self.current_settings = settings_data
            self._update_ui_from_settings()

    def _on_settings_event(self, event_data, old_data):
        if isinstance(event_data, dict):
            event_type = event_data.get("type")
            if event_type == "settings_updated":
                logger.debug("Settings updated event received")
            elif event_type == "settings_conflict_merged" and self.state_manager:
                self.state_manager.add_notification("Settings conflict resolved", "warning")

    # ---- Subscription initialization ----
    def init_subscriptions(self, state_manager: StateManager | None, on_loading_change):
        """Register subscriptions; stores unsubscribe callbacks for dispose."""
        if not state_manager:
            return

        # loading_states subscription
        state_manager.subscribe("loading_states", on_loading_change)
        self._unsubscribe_callbacks.append(lambda: state_manager.unsubscribe("loading_states", on_loading_change))

        # settings events
        state_manager.subscribe("settings_events", self._on_settings_event)
        self._unsubscribe_callbacks.append(lambda: state_manager.unsubscribe("settings_events", self._on_settings_event))

        # settings changes (if supported)
        if hasattr(state_manager, "subscribe_settings"):
            manager_ref: StateManager = state_manager
            with contextlib.suppress(Exception):
                manager_ref.subscribe_settings(self._on_settings_changed)
                self._unsubscribe_callbacks.append(
                    lambda: manager_ref.unsubscribe_settings(self._on_settings_changed)
                )

    # ---- Backup & restore ----
    async def backup_settings_async(self, backup_name: str):
        try:
            if self.state_manager:
                self.state_manager.start_progress("settings_backup", total_steps=2, message="Creating backup")
                self.state_manager.set_loading("settings_backup", True)
            if self.server_bridge:
                result = await self.server_bridge.backup_settings_async(
                    backup_name, self.current_settings
                )
                if result.get("success") and self.state_manager:
                    self.state_manager.update_progress("settings_backup", step=1, message="Saving")
                    self.state_manager.add_notification(f"Backup '{backup_name}' created", "success")
                    return result
            backup_dir = Path("settings_backups")
            backup_dir.mkdir(exist_ok=True)
            backup_file = backup_dir / f"{backup_name}.json"
            backup_data = {
                "created_at": time.time(),
                "backup_name": backup_name,
                "settings": self.current_settings,
            }
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            if self.state_manager:
                self.state_manager.update_progress("settings_backup", step=1, message="Saving")
                self.state_manager.add_notification(
                    f"Local backup '{backup_name}' created", "success"
                )
            return {"success": True, "backup_file": str(backup_file)}
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            if self.state_manager:
                self.state_manager.set_error_state("settings_backup", str(e))
            return {"success": False, "error": str(e)}
        finally:
            if self.state_manager:
                self.state_manager.clear_progress("settings_backup")
                self.state_manager.set_loading("settings_backup", False)

    async def restore_settings_async(self, backup_file: str):
        try:
            if self.state_manager:
                self.state_manager.set_loading("settings_restore", True)
            if self.server_bridge:
                result = await self.server_bridge.restore_settings_async(backup_file)
                if result.get("success"):
                    restored_settings = result.get("data", {}).get("restored_settings")
                    if restored_settings:
                        self.current_settings = restored_settings
                        self._update_ui_from_settings()
                        if self.state_manager:
                            await self.state_manager.update_settings_async(
                                self.current_settings, "restore"
                            )
                            self.state_manager.add_notification(
                                "Settings restored from backup", "success"
                            )
                    return result
            backup_path = Path(backup_file)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            with open(backup_path, encoding="utf-8") as f:
                backup_data = json.load(f)
            restored_settings = backup_data.get("settings", backup_data)
            self.current_settings = self._deep_merge_settings(
                self._load_default_settings(), restored_settings
            )
            self._update_ui_from_settings()
            if self.state_manager:
                await self.state_manager.update_settings_async(
                    self.current_settings, "local_restore"
                )
                self.state_manager.add_notification(
                    "Settings restored from local backup", "success"
                )
            return {"success": True}
        except Exception as e:
            logger.error(f"Failed to restore settings: {e}")
            if self.state_manager:
                self.state_manager.set_error_state("settings_restore", str(e))
            return {"success": False, "error": str(e)}
        finally:
            if self.state_manager:
                self.state_manager.set_loading("settings_restore", False)

    # ---- Import / Export (moved from utils.settings_io) ----
    async def export_settings(self, export_format: str = "json") -> dict:
        """Export settings to JSON or INI format with progress and notifications."""
        try:
            if self.state_manager:
                self.state_manager.start_progress("settings_export", total_steps=2, message="Preparing")
                self.state_manager.set_loading("settings_export", True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if export_format == "json":
                backup_file = f"settings_backup_{timestamp}.json"
                backup_data = {
                    'exported_at': timestamp,
                    'version': '2.0',
                    'settings': self.current_settings,
                    'metadata': {
                        'export_format': export_format,
                        'app_version': 'FletV2',
                        'total_sections': len(self.current_settings)
                    }
                }
                backup_path = Path(backup_file)
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)

            elif export_format == "ini":
                backup_file = f"settings_backup_{timestamp}.ini"
                backup_path = Path(backup_file)
                backup_path.parent.mkdir(parents=True, exist_ok=True)

                import configparser
                config = configparser.ConfigParser()
                for section, settings in self.current_settings.items():
                    config[section] = {}
                    for key, value in settings.items():
                        config[section][key] = str(value)
                with open(backup_path, 'w', encoding='utf-8') as f:
                    config.write(f)

            else:
                raise ValueError(f"Unsupported export format: {export_format}")

            if self.state_manager:
                self.state_manager.update_progress("settings_export", step=1, message="Writing file")
                self.state_manager.add_notification(f"Settings exported to {backup_file}", "success")

            logger.info(f"Settings exported to {backup_file}")
            return {'success': True, 'file': backup_file}

        except Exception as e:
            logger.error(f"Export failed: {e}")
            if self.state_manager:
                self.state_manager.set_error_state("settings_export", str(e))
            return {'success': False, 'error': str(e)}
        finally:
            if self.state_manager:
                self.state_manager.clear_progress("settings_export")
                self.state_manager.set_loading("settings_export", False)

    def _load_json_settings(self, file_path: str) -> dict:
        with open(file_path, encoding='utf-8') as f:
            imported_data = json.load(f)
        if 'settings' in imported_data:
            version = imported_data.get('version', '1.0')
            logger.info(f"Importing settings version {version}")
            return imported_data['settings']
        return imported_data

    def _load_ini_settings(self, file_path: str) -> dict:
        import configparser
        config = configparser.ConfigParser()
        config.read(file_path, encoding='utf-8')
        imported: dict[str, dict[str, object]] = {}
        for section in config.sections():
            imported[section] = {}
            for key, value in config[section].items():
                if value.lower() in ('true', 'false'):
                    imported[section][key] = value.lower() == 'true'
                elif value.isdigit():
                    imported[section][key] = int(value)
                elif value.replace('.', '').isdigit():
                    try:
                        imported[section][key] = float(value)
                    except Exception:
                        imported[section][key] = value
                else:
                    imported[section][key] = value
        return imported

    async def import_settings(self, file_path: str) -> dict:
        try:
            if self.state_manager:
                self.state_manager.set_loading("settings_import", True)

            file_ext = Path(file_path).suffix.lower()
            if file_ext == '.json':
                imported = self._load_json_settings(file_path)
            elif file_ext == '.ini':
                imported = self._load_ini_settings(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

            if not isinstance(imported, dict):
                raise ValueError("Invalid settings format")

            default_settings = self._load_default_settings()
            merged_settings = self._deep_merge_settings(default_settings, imported)
            validation_result = await self.validate_settings_async(merged_settings)
            if not validation_result.get('success', True):
                validation_data = validation_result.get('data', {})
                if not validation_data.get('valid', True):
                    errors = validation_data.get('errors', [])
                    raise ValueError(f"Settings validation failed: {'; '.join(errors)}")

            self.current_settings = merged_settings
            self._update_ui_from_settings()
            if self.state_manager:
                await self.state_manager.update_settings_async(self.current_settings, "import")
                self.state_manager.add_notification("Settings imported successfully", "success")
            return {'success': True}
        except Exception as e:
            logger.error(f"Import failed: {e}")
            if self.state_manager:
                self.state_manager.set_error_state("settings_import", str(e))
            return {'success': False, 'error': str(e)}
        finally:
            if self.state_manager:
                self.state_manager.set_loading("settings_import", False)

    def dispose(self):
        try:
            if self._auto_save_task and not self._auto_save_task.done():
                self._auto_save_task.cancel()
                logger.debug("Auto-save task cancelled")
            if self.state_manager:
                try:
                    for cb in self._unsubscribe_callbacks:
                        with contextlib.suppress(Exception):
                            cb()
                    logger.debug("State manager subscriptions cleaned up")
                except Exception as e:
                    logger.debug(f"Error unsubscribing from state manager: {e}")
            if self.page and self.file_picker is not None:
                try:
                    if self.file_picker in self.page.overlay:
                        self.page.overlay.remove(self.file_picker)
                        self.page.update()
                    self.file_picker = None
                    logger.debug("FilePicker removed from overlay")
                except Exception as e:
                    logger.debug(f"Error removing FilePicker: {e}")
            self._ui_refs.clear()
            self._validation_errors.clear()
            self._pending_changes.clear()
            logger.debug("Settings view disposed: cleaned up subscriptions, tasks, and UI references")
        except Exception as e:
            logger.warning(f"Error during settings view disposal: {e}")

    # ---- Defaults & merging ----
    def _load_default_settings(self) -> dict[str, Any]:
        """Derive defaults from SETTINGS_CONFIG when available; fallback to reasonable baseline."""
        try:
            # Local import to avoid circular dependency
            from views.settings_config import SETTINGS_CONFIG  # type: ignore
            defaults: dict[str, Any] = {}
            for section, sec_cfg in SETTINGS_CONFIG.items():
                sec_vals: dict[str, Any] = {}
                for subsection in sec_cfg.get("subsections", []):
                    for field in subsection.get("fields", []):
                        key = field.get("key")
                        if key is None:
                            continue
                        sec_vals.setdefault(key, field.get("default"))
                defaults[section] = sec_vals
            return defaults
        except Exception as e:
            logger.debug(f"Failed to build defaults from SETTINGS_CONFIG: {e}")
            return {
                "server": {"port": 1256, "host": "127.0.0.1", "max_clients": 50, "timeout": 30},
                "gui": {"theme_mode": "system", "color_scheme": "blue", "auto_resize": True},
                "monitoring": {"enabled": True, "refresh_interval": 5.0, "cpu_threshold": 80.0, "memory_threshold": 85.0},
                "logging": {"enabled": True, "level": "INFO", "file_path": "logs/server.log"},
                "security": {"require_auth": False, "api_key": ""},
                "backup": {"auto_backup": True, "backup_path": "backups/", "retention_days": 30},
            }

    def _deep_merge_settings(self, base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        result = dict(base)
        for k, v in (incoming or {}).items():
            if isinstance(v, dict) and isinstance(result.get(k), dict):
                result[k] = self._deep_merge_settings(result[k], v)
            else:
                result[k] = v
        return result
