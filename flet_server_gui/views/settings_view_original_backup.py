"""
Settings View for Flet Server GUI
Real settings management UI with Material Design 3 components
"""

import flet as ft
from typing import Dict, Any, Optional
import logging
from ..utils.settings_manager import SettingsManager

logger = logging.getLogger(__name__)

class SettingsView:
    """
    Real settings management UI with comprehensive server configuration.
    NO mock data - all settings are validated and persisted.
    """
    
    def __init__(self, page: ft.Page, dialog_system, toast_manager):
        """Initialize with real settings manager and UI components"""
        self.page = page
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self.settings_manager = SettingsManager()
        
        # Current settings state
        self.current_settings: Dict[str, Any] = {}
        self.settings_changed = False
        
        # UI component references
        self.server_controls: Dict[str, ft.Control] = {}
        self.gui_controls: Dict[str, ft.Control] = {}
        self.monitoring_controls: Dict[str, ft.Control] = {}
        
        logger.info("✅ Settings view initialized with real settings manager")
    
    def create_settings_view(self) -> ft.Container:
        """Create the main settings view with tabbed interface"""
        
        # Load current settings
        self.current_settings = self.settings_manager.load_settings()
        
        # Create tabs for different setting categories
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Server",
                    icon=ft.Icons.SETTINGS,
                    content=self._create_server_settings()
                ),
                ft.Tab(
                    text="GUI",
                    icon=ft.Icons.SETTINGS,
                    content=self._create_gui_settings()
                ),
                ft.Tab(
                    text="Monitoring",
                    icon=ft.Icons.MONITOR,
                    content=self._create_monitoring_settings()
                ),
                ft.Tab(
                    text="Advanced",
                    icon=ft.Icons.TUNE,
                    content=self._create_advanced_settings()
                )
            ],
            expand=1
        )
        
        # Main action buttons
        action_bar = self._create_action_bar()
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Server Settings",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PRIMARY
                ),
                ft.Text(
                    "Configure server behavior, GUI preferences, and monitoring",
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                ),
                ft.Divider(height=20),
                tabs,
                action_bar
            ]),
            padding=20,
            expand=True
        )
    
    def _create_server_settings(self) -> ft.Container:
        """Create server configuration settings panel"""
        server_settings = self.current_settings.get('server', {})
        
        # Create input controls
        self.server_controls['port'] = ft.TextField(
            label="Server Port",
            value=str(server_settings.get('port', 1256)),
            helper_text="Port number for the backup server (1024-65535)",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_setting_changed
        )
        
        self.server_controls['host'] = ft.TextField(
            label="Server Host",
            value=str(server_settings.get('host', '127.0.0.1')),
            helper_text="IP address to bind the server to",
            on_change=self._on_setting_changed
        )
        
        self.server_controls['storage_dir'] = ft.TextField(
            label="Storage Directory",
            value=str(server_settings.get('storage_dir', 'received_files')),
            helper_text="Directory where received files are stored",
            on_change=self._on_setting_changed,
            suffix=ft.IconButton(
                icon=ft.Icons.FOLDER_OPEN,
                tooltip="Browse for directory",
                on_click=self._browse_storage_directory
            )
        )
        
        self.server_controls['max_clients'] = ft.TextField(
            label="Maximum Clients",
            value=str(server_settings.get('max_clients', 50)),
            helper_text="Maximum number of concurrent client connections",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_setting_changed
        )
        
        self.server_controls['session_timeout'] = ft.TextField(
            label="Session Timeout (minutes)",
            value=str(server_settings.get('session_timeout', 10)),
            helper_text="Timeout for idle client sessions",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_setting_changed
        )
        
        self.server_controls['maintenance_interval'] = ft.TextField(
            label="Maintenance Interval (seconds)",
            value=str(server_settings.get('maintenance_interval', 60)),
            helper_text="Interval for server maintenance tasks",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_setting_changed
        )
        
        self.server_controls['auto_start'] = ft.Switch(
            label="Auto-start server on GUI launch",
            value=server_settings.get('auto_start', False),
            on_change=self._on_setting_changed
        )
        
        self.server_controls['log_level'] = ft.Dropdown(
            label="Log Level",
            value=server_settings.get('log_level', 'INFO'),
            options=[
                ft.dropdown.Option("DEBUG"),
                ft.dropdown.Option("INFO"),
                ft.dropdown.Option("WARNING"),
                ft.dropdown.Option("ERROR"),
                ft.dropdown.Option("CRITICAL")
            ],
            on_change=self._on_setting_changed
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Server Configuration", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            self.server_controls['port'],
                            self.server_controls['host'],
                            self.server_controls['storage_dir'],
                            self.server_controls['max_clients']
                        ]),
                        expand=1
                    ),
                    ft.Container(
                        content=ft.Column([
                            self.server_controls['session_timeout'],
                            self.server_controls['maintenance_interval'],
                            self.server_controls['log_level'],
                            self.server_controls['auto_start']
                        ]),
                        expand=1
                    )
                ])
            ]),
            padding=20
        )
    
    def _create_gui_settings(self) -> ft.Container:
        """Create GUI preferences settings panel"""
        gui_settings = self.current_settings.get('gui', {})
        
        self.gui_controls['theme_mode'] = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="light", label="Light Theme"),
                ft.Radio(value="dark", label="Dark Theme"),
                ft.Radio(value="system", label="Follow System")
            ]),
            value=gui_settings.get('theme_mode', 'dark'),
            on_change=self._on_setting_changed
        )
        
        self.gui_controls['auto_refresh_interval'] = ft.Slider(
            min=1,
            max=60,
            divisions=59,
            value=float(gui_settings.get('auto_refresh_interval', 5)),
            label="Auto Refresh: {value} seconds",
            on_change=self._on_setting_changed
        )
        
        self.gui_controls['show_notifications'] = ft.Switch(
            label="Show desktop notifications",
            value=gui_settings.get('show_notifications', True),
            on_change=self._on_setting_changed
        )
        
        self.gui_controls['window_maximized'] = ft.Switch(
            label="Start with maximized window",
            value=gui_settings.get('window_maximized', False),
            on_change=self._on_setting_changed
        )
        
        self.gui_controls['confirm_deletions'] = ft.Switch(
            label="Confirm before deleting items",
            value=gui_settings.get('confirm_deletions', True),
            on_change=self._on_setting_changed
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("GUI Preferences", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Theme Mode", size=16, weight=ft.FontWeight.W_500),
                self.gui_controls['theme_mode'],
                ft.Divider(),
                ft.Text("Auto Refresh Interval", size=16, weight=ft.FontWeight.W_500),
                self.gui_controls['auto_refresh_interval'],
                ft.Divider(),
                ft.Text("Behavior Settings", size=16, weight=ft.FontWeight.W_500),
                self.gui_controls['show_notifications'],
                self.gui_controls['window_maximized'],
                self.gui_controls['confirm_deletions']
            ]),
            padding=20
        )
    
    def _create_monitoring_settings(self) -> ft.Container:
        """Create monitoring configuration settings panel"""
        monitoring_settings = self.current_settings.get('monitoring', {})
        
        self.monitoring_controls['enable_system_monitoring'] = ft.Switch(
            label="Enable system monitoring",
            value=monitoring_settings.get('enable_system_monitoring', True),
            on_change=self._on_setting_changed
        )
        
        self.monitoring_controls['monitoring_interval'] = ft.Slider(
            min=1,
            max=60,
            divisions=59,
            value=float(monitoring_settings.get('monitoring_interval', 2)),
            label="Monitoring Interval: {value} seconds",
            on_change=self._on_setting_changed
        )
        
        self.monitoring_controls['history_retention_days'] = ft.TextField(
            label="History Retention (days)",
            value=str(monitoring_settings.get('history_retention_days', 7)),
            helper_text="Number of days to keep monitoring history",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_setting_changed
        )
        
        self.monitoring_controls['performance_alerts'] = ft.Switch(
            label="Enable performance alerts",
            value=monitoring_settings.get('performance_alerts', True),
            on_change=self._on_setting_changed
        )
        
        # Alert thresholds
        alert_thresholds = monitoring_settings.get('alert_thresholds', {})
        
        self.monitoring_controls['cpu_threshold'] = ft.Slider(
            min=50,
            max=99,
            divisions=49,
            value=float(alert_thresholds.get('cpu_percent', 80)),
            label="CPU Alert Threshold: {value}%",
            on_change=self._on_setting_changed
        )
        
        self.monitoring_controls['memory_threshold'] = ft.Slider(
            min=50,
            max=99,
            divisions=49,
            value=float(alert_thresholds.get('memory_percent', 85)),
            label="Memory Alert Threshold: {value}%",
            on_change=self._on_setting_changed
        )
        
        self.monitoring_controls['disk_threshold'] = ft.Slider(
            min=50,
            max=99,
            divisions=49,
            value=float(alert_thresholds.get('disk_percent', 90)),
            label="Disk Alert Threshold: {value}%",
            on_change=self._on_setting_changed
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Monitoring Configuration", size=20, weight=ft.FontWeight.BOLD),
                self.monitoring_controls['enable_system_monitoring'],
                ft.Divider(),
                ft.Text("Monitoring Interval", size=16, weight=ft.FontWeight.W_500),
                self.monitoring_controls['monitoring_interval'],
                ft.Row([
                    ft.Container(
                        content=self.monitoring_controls['history_retention_days'],
                        expand=1
                    ),
                    ft.Container(width=20),
                    ft.Container(
                        content=self.monitoring_controls['performance_alerts'],
                        expand=1
                    )
                ]),
                ft.Divider(),
                ft.Text("Performance Alert Thresholds", size=16, weight=ft.FontWeight.W_500),
                self.monitoring_controls['cpu_threshold'],
                self.monitoring_controls['memory_threshold'],
                self.monitoring_controls['disk_threshold']
            ]),
            padding=20
        )
    
    def _create_advanced_settings(self) -> ft.Container:
        """Create advanced settings panel with import/export functionality"""
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Advanced Settings", size=20, weight=ft.FontWeight.BOLD),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Configuration Management", size=16, weight=ft.FontWeight.W_500),
                            ft.Row([
                                ft.ElevatedButton(
                                    text="Export Settings",
                                    icon=ft.Icons.DOWNLOAD,
                                    on_click=self._export_settings
                                ),
                                ft.ElevatedButton(
                                    text="Import Settings",
                                    icon=ft.Icons.UPLOAD,
                                    on_click=self._import_settings
                                )
                            ]),
                            ft.Divider(),
                            ft.Text("Reset Options", size=16, weight=ft.FontWeight.W_500),
                            ft.Row([
                                ft.ElevatedButton(
                                    text="Reset Server Settings",
                                    icon=ft.Icons.REFRESH,
                                    on_click=lambda _: self._reset_category('server')
                                ),
                                ft.ElevatedButton(
                                    text="Reset GUI Settings",
                                    icon=ft.Icons.REFRESH,
                                    on_click=lambda _: self._reset_category('gui')
                                ),
                                ft.ElevatedButton(
                                    text="Reset All Settings",
                                    icon=ft.Icons.RESTORE,
                                    color=ft.Colors.ERROR,
                                    on_click=self._reset_all_settings
                                )
                            ])
                        ]),
                        padding=20
                    )
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("System Information", size=16, weight=ft.FontWeight.W_500),
                            ft.Text(f"Settings File: {self.settings_manager.settings_file}", size=12),
                            ft.Text(f"Using Unified Config: {self.settings_manager.use_unified}", size=12),
                            ft.Text("Configuration is validated and persisted automatically", size=12, 
                                   color=ft.Colors.ON_SURFACE_VARIANT)
                        ]),
                        padding=20
                    )
                )
            ]),
            padding=20
        )
    
    def _create_action_bar(self) -> ft.Container:
        """Create action buttons for saving/canceling changes"""
        
        return ft.Container(
            content=ft.Row([
                ft.ElevatedButton(
                    text="Save Changes",
                    icon=ft.Icons.SAVE,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY
                    ),
                    on_click=self._save_settings
                ),
                ft.ElevatedButton(
                    text="Cancel Changes",
                    icon=ft.Icons.CANCEL,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.ON_SURFACE_VARIANT,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                    on_click=self._cancel_changes
                ),
                ft.Container(expand=1),
                ft.Text(
                    "● Changes pending" if self.settings_changed else "✓ All changes saved",
                    color=ft.Colors.ORANGE if self.settings_changed else ft.Colors.GREEN,
                    size=12
                )
            ]),
            padding=ft.padding.symmetric(vertical=10)
        )
    
    def _on_setting_changed(self, e):
        """Handle setting value changes"""
        self.settings_changed = True
        self.page.update()
        logger.debug("Settings changed - pending save")
    
    def _browse_storage_directory(self, e):
        """Open file picker for storage directory selection"""
        # Note: Flet file picker for directories
        # This would require implementing a directory picker dialog
        self.toast_manager.show_info("Directory browser not yet implemented. Enter path manually.")
    
    def _save_settings(self, e):
        """Save all current settings with validation"""
        try:
            # Collect all current values
            new_settings = self._collect_current_values()
            
            # Save through settings manager (includes validation)
            if self.settings_manager.save_settings(new_settings):
                self.current_settings = new_settings
                self.settings_changed = False
                self.page.update()
                
                self.toast_manager.show_success("Settings saved successfully!")
                logger.info("✅ Settings saved successfully")
            else:
                self.toast_manager.show_error("Failed to save settings. Check logs for details.")
                
        except ValueError as e:
            self.dialog_system.show_error_dialog(
                title="Invalid Settings",
                message=f"Please check your settings:\n{str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error saving settings: {e}")
            self.dialog_system.show_error_dialog(
                title="Save Error",
                message="An unexpected error occurred while saving settings."
            )
    
    def _collect_current_values(self) -> Dict[str, Any]:
        """Collect current values from all UI controls"""
        settings = {
            'server': {
                'port': int(self.server_controls['port'].value),
                'host': self.server_controls['host'].value,
                'storage_dir': self.server_controls['storage_dir'].value,
                'max_clients': int(self.server_controls['max_clients'].value),
                'session_timeout': int(self.server_controls['session_timeout'].value),
                'maintenance_interval': int(self.server_controls['maintenance_interval'].value),
                'auto_start': self.server_controls['auto_start'].value,
                'log_level': self.server_controls['log_level'].value
            },
            'gui': {
                'theme_mode': self.gui_controls['theme_mode'].value,
                'auto_refresh_interval': int(self.gui_controls['auto_refresh_interval'].value),
                'show_notifications': self.gui_controls['show_notifications'].value,
                'window_maximized': self.gui_controls['window_maximized'].value,
                'confirm_deletions': self.gui_controls['confirm_deletions'].value,
                'last_tab': self.current_settings.get('gui', {}).get('last_tab', 'dashboard')
            },
            'monitoring': {
                'enable_system_monitoring': self.monitoring_controls['enable_system_monitoring'].value,
                'monitoring_interval': int(self.monitoring_controls['monitoring_interval'].value),
                'history_retention_days': int(self.monitoring_controls['history_retention_days'].value),
                'performance_alerts': self.monitoring_controls['performance_alerts'].value,
                'alert_thresholds': {
                    'cpu_percent': int(self.monitoring_controls['cpu_threshold'].value),
                    'memory_percent': int(self.monitoring_controls['memory_threshold'].value),
                    'disk_percent': int(self.monitoring_controls['disk_threshold'].value)
                }
            }
        }
        
        return settings
    
    def _cancel_changes(self, e):
        """Cancel pending changes and reload original settings"""
        self.current_settings = self.settings_manager.load_settings()
        self.settings_changed = False
        
        # Reset all UI controls to original values
        self._update_ui_controls()
        
        self.toast_manager.show_info("Changes cancelled")
        self.page.update()
    
    def _update_ui_controls(self):
        """Update UI controls with current settings values"""
        server_settings = self.current_settings.get('server', {})
        gui_settings = self.current_settings.get('gui', {})
        monitoring_settings = self.current_settings.get('monitoring', {})
        
        # Update server controls
        self.server_controls['port'].value = str(server_settings.get('port', 1256))
        self.server_controls['host'].value = str(server_settings.get('host', '127.0.0.1'))
        self.server_controls['storage_dir'].value = str(server_settings.get('storage_dir', 'received_files'))
        self.server_controls['max_clients'].value = str(server_settings.get('max_clients', 50))
        self.server_controls['session_timeout'].value = str(server_settings.get('session_timeout', 10))
        self.server_controls['maintenance_interval'].value = str(server_settings.get('maintenance_interval', 60))
        self.server_controls['auto_start'].value = server_settings.get('auto_start', False)
        self.server_controls['log_level'].value = server_settings.get('log_level', 'INFO')
        
        # Update GUI controls
        self.gui_controls['theme_mode'].value = gui_settings.get('theme_mode', 'dark')
        self.gui_controls['auto_refresh_interval'].value = float(gui_settings.get('auto_refresh_interval', 5))
        self.gui_controls['show_notifications'].value = gui_settings.get('show_notifications', True)
        self.gui_controls['window_maximized'].value = gui_settings.get('window_maximized', False)
        self.gui_controls['confirm_deletions'].value = gui_settings.get('confirm_deletions', True)
        
        # Update monitoring controls
        self.monitoring_controls['enable_system_monitoring'].value = monitoring_settings.get('enable_system_monitoring', True)
        self.monitoring_controls['monitoring_interval'].value = float(monitoring_settings.get('monitoring_interval', 2))
        self.monitoring_controls['history_retention_days'].value = str(monitoring_settings.get('history_retention_days', 7))
        self.monitoring_controls['performance_alerts'].value = monitoring_settings.get('performance_alerts', True)
        
        alert_thresholds = monitoring_settings.get('alert_thresholds', {})
        self.monitoring_controls['cpu_threshold'].value = float(alert_thresholds.get('cpu_percent', 80))
        self.monitoring_controls['memory_threshold'].value = float(alert_thresholds.get('memory_percent', 85))
        self.monitoring_controls['disk_threshold'].value = float(alert_thresholds.get('disk_percent', 90))
    
    def _export_settings(self, e):
        """Export current settings to a file"""
        try:
            # Simple filename for now - could be enhanced with file picker
            filename = f"flet_server_settings_export.json"
            
            if self.settings_manager.export_settings(filename):
                self.dialog_system.show_success_dialog(
                    title="Export Successful",
                    message=f"Settings exported to {filename}"
                )
            else:
                self.dialog_system.show_error_dialog(
                    title="Export Failed",
                    message="Failed to export settings. Check logs for details."
                )
        except Exception as e:
            logger.error(f"❌ Export error: {e}")
            self.dialog_system.show_error_dialog(
                title="Export Error",
                message="An unexpected error occurred during export."
            )
    
    def _import_settings(self, e):
        """Import settings from a file"""
        try:
            # Simple filename for now - could be enhanced with file picker
            filename = f"flet_server_settings_export.json"
            
            if self.settings_manager.import_settings(filename):
                # Reload current settings and update UI
                self.current_settings = self.settings_manager.load_settings()
                self._update_ui_controls()
                self.settings_changed = False
                self.page.update()
                
                self.dialog_system.show_success_dialog(
                    title="Import Successful",
                    message=f"Settings imported from {filename}"
                )
            else:
                self.dialog_system.show_error_dialog(
                    title="Import Failed",
                    message="Failed to import settings. Check that the file exists and is valid."
                )
        except Exception as e:
            logger.error(f"❌ Import error: {e}")
            self.dialog_system.show_error_dialog(
                title="Import Error",
                message="An unexpected error occurred during import."
            )
    
    def _reset_category(self, category: str):
        """Reset a specific category of settings to defaults"""
        def confirm_reset(confirmed):
            if confirmed:
                if self.settings_manager.reset_to_defaults(category):
                    self.current_settings = self.settings_manager.load_settings()
                    self._update_ui_controls()
                    self.settings_changed = False
                    self.page.update()
                    
                    self.toast_manager.show_success(f"{category.title()} settings reset to defaults")
                else:
                    self.toast_manager.show_error(f"Failed to reset {category} settings")
        
        self.dialog_system.show_confirmation_dialog(
            title=f"Reset {category.title()} Settings",
            message=f"Are you sure you want to reset all {category} settings to their default values?",
            on_confirm=confirm_reset
        )
    
    def _reset_all_settings(self, e):
        """Reset all settings to defaults with confirmation"""
        def confirm_reset_all(confirmed):
            if confirmed:
                if self.settings_manager.reset_to_defaults():
                    self.current_settings = self.settings_manager.load_settings()
                    self._update_ui_controls()
                    self.settings_changed = False
                    self.page.update()
                    
                    self.toast_manager.show_success("All settings reset to defaults")
                else:
                    self.toast_manager.show_error("Failed to reset settings")
        
        self.dialog_system.show_confirmation_dialog(
            title="Reset All Settings",
            message="Are you sure you want to reset ALL settings to their default values?\n\nThis action cannot be undone.",
            on_confirm=confirm_reset_all
        )