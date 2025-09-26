#!/usr/bin/env python3
"""
Settings import/export helpers for FletV2 Settings.
Extracted from views/settings.py to reduce view size and centralize IO.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from utils.debug_setup import get_logger
from views.settings_state import EnhancedSettingsState

logger = get_logger(__name__)


async def enhanced_export_settings(state: EnhancedSettingsState, export_format: str = "json"):
    """Export settings to JSON or INI format, with progress reporting via StateManager."""
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


def _load_json_settings(file_path: str) -> dict:
    with open(file_path, encoding='utf-8') as f:
        imported_data = json.load(f)
    if 'settings' in imported_data:
        version = imported_data.get('version', '1.0')
        logger.info(f"Importing settings version {version}")
        return imported_data['settings']
    return imported_data


def _load_ini_settings(file_path: str) -> dict:
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
                imported[section][key] = float(value)
            else:
                imported[section][key] = value
    return imported


async def _apply_imported_settings(state: EnhancedSettingsState, imported: dict) -> dict:
    default_settings = state._load_default_settings()
    merged_settings = state._deep_merge_settings(default_settings, imported)
    validation_result = await state.validate_settings_async(merged_settings)
    if not validation_result.get('success', True):
        validation_data = validation_result.get('data', {})
        if not validation_data.get('valid', True):
            errors = validation_data.get('errors', [])
            raise ValueError(f"Settings validation failed: {'; '.join(errors)}")
    state.current_settings = merged_settings
    state._update_ui_from_settings()
    if state.state_manager:
        await state.state_manager.update_settings_async(state.current_settings, "import")
        state.state_manager.add_notification("Settings imported successfully", "success")
    return {'success': True}


async def enhanced_import_settings(state: EnhancedSettingsState, file_path: str):
    try:
        if state.state_manager:
            state.state_manager.set_loading("settings_import", True)

        file_ext = Path(file_path).suffix.lower()
        if file_ext == '.json':
            imported = _load_json_settings(file_path)
        elif file_ext == '.ini':
            imported = _load_ini_settings(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        if not isinstance(imported, dict):
            raise ValueError("Invalid settings format")
        result = await _apply_imported_settings(state, imported)
        logger.info("Settings imported successfully")
        return result
    except Exception as e:
        logger.error(f"Import failed: {e}")
        if state.state_manager:
            state.state_manager.set_error_state("settings_import", str(e))
        return {'success': False, 'error': str(e)}
    finally:
        if state.state_manager:
            state.state_manager.set_loading("settings_import", False)
