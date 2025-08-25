#!/usr/bin/env python3
"""
Settings Export/Import Service
Handles exporting and importing settings to/from JSON files.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

import json
import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


class SettingsExportImportService:
    """Service for exporting and importing settings data"""
    
    def __init__(self, toast_manager=None):
        self.toast_manager = toast_manager
    
    def export_settings(self, settings_data: Dict[str, Any], file_path: str) -> Tuple[bool, str]:
        """Export settings to JSON file"""
        try:
            # Add metadata to the export
            export_data = {
                'metadata': {
                    'version': '1.0',
                    'exported_at': datetime.now().isoformat(),
                    'application': 'Flet Server GUI'
                },
                'settings': settings_data
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write to file with pretty formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            message = f"Settings exported successfully to {file_path}"
            if self.toast_manager:
                self.toast_manager.show_success(message)
            
            return True, message
            
        except Exception as e:
            error_message = f"Failed to export settings: {str(e)}"
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
            
            return False, error_message
    
    def import_settings(self, file_path: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Import settings from JSON file"""
        try:
            if not os.path.exists(file_path):
                error_message = f"Settings file not found: {file_path}"
                if self.toast_manager:
                    self.toast_manager.show_error(error_message)
                return False, error_message, None
            
            # Read and parse file
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Validate structure
            if 'settings' not in import_data:
                # Try to handle legacy format (direct settings object)
                if isinstance(import_data, dict) and 'port' in import_data:  # Assume direct settings format
                    settings_data = import_data
                else:
                    error_message = "Invalid settings file format"
                    if self.toast_manager:
                        self.toast_manager.show_error(error_message)
                    return False, error_message, None
            else:
                settings_data = import_data['settings']
            
            # Validate settings data structure
            validation_result = self._validate_settings_structure(settings_data)
            if not validation_result[0]:
                error_message = f"Invalid settings data: {validation_result[1]}"
                if self.toast_manager:
                    self.toast_manager.show_error(error_message)
                return False, error_message, None
            
            message = f"Settings imported successfully from {file_path}"
            if self.toast_manager:
                self.toast_manager.show_success(message)
            
            return True, message, settings_data
            
        except json.JSONDecodeError as e:
            error_message = f"Invalid JSON format: {str(e)}"
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
            return False, error_message, None
            
        except Exception as e:
            error_message = f"Failed to import settings: {str(e)}"
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
            return False, error_message, None
    
    def _validate_settings_structure(self, settings_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate the structure of imported settings"""
        try:
            if not isinstance(settings_data, dict):
                return False, "Settings data must be a dictionary"
            
            # Define expected structure with types
            expected_structure = {
                'port': (int, str),  # Allow string for conversion
                'host': str,
                'storage_directory': str,
                'max_connections': (int, str),
                'auto_start': bool,
                'enable_logging': bool,
                'theme_mode': str,
                'refresh_interval': (int, float),
                'show_notifications': bool,
                'minimize_to_tray': bool,
                'confirm_actions': bool,
                'enable_system_monitoring': bool,
                'cpu_alert_threshold': (int, str, float),
                'memory_alert_threshold': (int, str, float),
                'disk_alert_threshold': (int, str, float),
                'monitoring_interval': (int, str),
                'backup_frequency': str,
                'cleanup_old_files': bool,
                'cleanup_days': (int, str),
                'debug_mode': bool
            }
            
            # Check for required keys (at least some basic ones)
            required_keys = ['port', 'host', 'theme_mode']
            missing_keys = [key for key in required_keys if key not in settings_data]
            
            if missing_keys:
                return False, f"Missing required settings: {', '.join(missing_keys)}"
            
            # Validate types for present keys
            for key, value in settings_data.items():
                if key in expected_structure:
                    expected_types = expected_structure[key]
                    if not isinstance(expected_types, tuple):
                        expected_types = (expected_types,)
                    
                    if not isinstance(value, expected_types):
                        return False, f"Invalid type for '{key}': expected {expected_types}, got {type(value)}"
            
            return True, "Settings structure is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def create_settings_backup(self, settings_data: Dict[str, Any], 
                              backup_directory: str = "backups") -> Tuple[bool, str]:
        """Create a timestamped backup of current settings"""
        try:
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"settings_backup_{timestamp}.json"
            backup_path = os.path.join(backup_directory, backup_filename)
            
            return self.export_settings(settings_data, backup_path)
            
        except Exception as e:
            error_message = f"Failed to create settings backup: {str(e)}"
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
            return False, error_message
    
    def list_available_backups(self, backup_directory: str = "backups") -> list:
        """List available settings backups"""
        try:
            if not os.path.exists(backup_directory):
                return []
            
            backups = []
            for filename in os.listdir(backup_directory):
                if filename.startswith("settings_backup_") and filename.endswith(".json"):
                    filepath = os.path.join(backup_directory, filename)
                    stat = os.stat(filepath)
                    
                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
            
            # Sort by modification time, newest first
            backups.sort(key=lambda x: x['modified'], reverse=True)
            
            return backups
            
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
    
    def restore_from_backup(self, backup_filepath: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Restore settings from a backup file"""
        return self.import_settings(backup_filepath)
    
    def delete_backup(self, backup_filepath: str) -> Tuple[bool, str]:
        """Delete a settings backup file"""
        try:
            if not os.path.exists(backup_filepath):
                error_message = f"Backup file not found: {backup_filepath}"
                return False, error_message
            
            os.remove(backup_filepath)
            
            message = f"Backup deleted: {os.path.basename(backup_filepath)}"
            if self.toast_manager:
                self.toast_manager.show_success(message)
            
            return True, message
            
        except Exception as e:
            error_message = f"Failed to delete backup: {str(e)}"
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
            return False, error_message
