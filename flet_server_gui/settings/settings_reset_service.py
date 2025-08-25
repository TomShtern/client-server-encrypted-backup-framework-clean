#!/usr/bin/env python3
"""
Settings Reset Service
Handles resetting settings to default values by category or globally.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

from typing import Dict, Any, List, Optional, Tuple


class SettingsResetService:
    """Service for resetting settings to default values"""
    
    def __init__(self, toast_manager=None, dialog_system=None):
        self.toast_manager = toast_manager
        self.dialog_system = dialog_system
        
        # Define default settings by category
        self.default_settings = {
            'server': {
                'port': 1256,
                'host': '127.0.0.1',
                'storage_directory': 'received_files',
                'max_connections': 100,
                'auto_start': False,
                'enable_logging': True
            },
            'gui': {
                'theme_mode': 'system',
                'refresh_interval': 30,
                'show_notifications': True,
                'minimize_to_tray': False,
                'confirm_actions': True
            },
            'monitoring': {
                'enable_system_monitoring': True,
                'cpu_alert_threshold': 80,
                'memory_alert_threshold': 85,
                'disk_alert_threshold': 90,
                'monitoring_interval': 60
            },
            'advanced': {
                'backup_frequency': 'weekly',
                'cleanup_old_files': False,
                'cleanup_days': 30,
                'debug_mode': False
            }
        }
    
    def get_default_settings(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get default settings for a category or all categories"""
        if category:
            return self.default_settings.get(category, {}).copy()
        
        # Return all defaults flattened
        all_defaults = {}
        for cat_defaults in self.default_settings.values():
            all_defaults.update(cat_defaults)
        
        return all_defaults
    
    def reset_category(self, category: str, current_settings: Dict[str, Any], 
                      confirm_callback: Optional[callable] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Reset settings for a specific category"""
        try:
            if category not in self.default_settings:
                error_message = f"Unknown settings category: {category}"
                if self.toast_manager:
                    self.toast_manager.show_error(error_message)
                return False, error_message, current_settings
            
            # Show confirmation dialog if callback provided
            if confirm_callback and self.dialog_system:
                self.dialog_system.show_confirmation_dialog(
                    title=f"Reset {category.title()} Settings",
                    message=f"Are you sure you want to reset all {category} settings to their default values? This action cannot be undone.",
                    on_confirm=lambda: self._execute_category_reset(category, current_settings, confirm_callback),
                    on_cancel=lambda: None
                )
                return True, "Reset confirmation requested", current_settings
            else:
                return self._execute_category_reset(category, current_settings, confirm_callback)
            
        except Exception as e:
            error_message = f"Failed to reset {category} settings: {str(e)}"
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
            return False, error_message, current_settings
    
    def _execute_category_reset(self, category: str, current_settings: Dict[str, Any],
                               callback: Optional[callable] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Execute the actual category reset"""
        try:
            category_defaults = self.default_settings[category]
            
            # Update current settings with defaults
            updated_settings = current_settings.copy()
            updated_settings.update(category_defaults)
            
            message = f"{category.title()} settings reset to defaults"
            if self.toast_manager:
                self.toast_manager.show_success(message)
            
            # Execute callback if provided
            if callback:
                callback(updated_settings)
            
            return True, message, updated_settings
            
        except Exception as e:
            error_message = f"Failed to execute {category} reset: {str(e)}"
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
            return False, error_message, current_settings
    
    def reset_all_settings(self, confirm_callback: Optional[callable] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Reset all settings to defaults"""
        try:
            # Show confirmation dialog if callback provided
            if confirm_callback and self.dialog_system:
                self.dialog_system.show_confirmation_dialog(
                    title="Reset All Settings",
                    message="Are you sure you want to reset ALL settings to their default values? This will affect server configuration, GUI preferences, monitoring settings, and advanced options. This action cannot be undone.",
                    on_confirm=lambda: self._execute_full_reset(confirm_callback),
                    on_cancel=lambda: None
                )
                return True, "Full reset confirmation requested", {}
            else:
                return self._execute_full_reset(confirm_callback)
            
        except Exception as e:
            error_message = f"Failed to reset all settings: {str(e)}"
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
            return False, error_message, {}
    
    def _execute_full_reset(self, callback: Optional[callable] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Execute the actual full reset"""
        try:
            # Get all default settings
            all_defaults = self.get_default_settings()
            
            message = "All settings reset to defaults"
            if self.toast_manager:
                self.toast_manager.show_success(message)
            
            # Execute callback if provided
            if callback:
                callback(all_defaults)
            
            return True, message, all_defaults
            
        except Exception as e:
            error_message = f"Failed to execute full reset: {str(e)}"
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
            return False, error_message, {}
    
    def get_changed_settings(self, current_settings: Dict[str, Any], 
                           category: Optional[str] = None) -> Dict[str, Any]:
        """Get settings that differ from defaults"""
        try:
            defaults = self.get_default_settings(category)
            changed = {}
            
            for key, default_value in defaults.items():
                current_value = current_settings.get(key)
                if current_value != default_value:
                    changed[key] = {
                        'current': current_value,
                        'default': default_value
                    }
            
            return changed
            
        except Exception as e:
            print(f"Error getting changed settings: {e}")
            return {}
    
    def has_unsaved_changes(self, current_settings: Dict[str, Any], 
                           original_settings: Dict[str, Any]) -> bool:
        """Check if current settings differ from original settings"""
        try:
            for key, current_value in current_settings.items():
                original_value = original_settings.get(key)
                if current_value != original_value:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking for unsaved changes: {e}")
            return False
    
    def get_category_status(self, current_settings: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Get status information for each settings category"""
        try:
            status = {}
            
            for category in self.default_settings.keys():
                defaults = self.get_default_settings(category)
                changed_settings = self.get_changed_settings(current_settings, category)
                
                status[category] = {
                    'total_settings': len(defaults),
                    'changed_settings': len(changed_settings),
                    'is_default': len(changed_settings) == 0,
                    'changed_keys': list(changed_settings.keys())
                }
            
            return status
            
        except Exception as e:
            print(f"Error getting category status: {e}")
            return {}
    
    def validate_settings_values(self, settings: Dict[str, Any]) -> List[str]:
        """Validate settings values and return list of validation errors"""
        errors = []
        
        try:
            # Port validation
            if 'port' in settings:
                port = settings['port']
                if not isinstance(port, int) or port < 1024 or port > 65535:
                    errors.append("Port must be between 1024 and 65535")
            
            # Host validation
            if 'host' in settings:
                host = settings['host']
                if not isinstance(host, str) or len(host.strip()) == 0:
                    errors.append("Host cannot be empty")
            
            # Threshold validations
            for threshold in ['cpu_alert_threshold', 'memory_alert_threshold', 'disk_alert_threshold']:
                if threshold in settings:
                    value = settings[threshold]
                    if not isinstance(value, (int, float)) or value < 0 or value > 100:
                        errors.append(f"{threshold.replace('_', ' ').title()} must be between 0 and 100")
            
            # Refresh interval validation
            if 'refresh_interval' in settings:
                interval = settings['refresh_interval']
                if not isinstance(interval, (int, float)) or interval < 5 or interval > 300:
                    errors.append("Refresh interval must be between 5 and 300 seconds")
            
            # Max connections validation
            if 'max_connections' in settings:
                max_conn = settings['max_connections']
                if not isinstance(max_conn, int) or max_conn < 1 or max_conn > 1000:
                    errors.append("Max connections must be between 1 and 1000")
            
            # Cleanup days validation
            if 'cleanup_days' in settings:
                days = settings['cleanup_days']
                if not isinstance(days, int) or days < 1 or days > 365:
                    errors.append("Cleanup days must be between 1 and 365")
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors
