#!/usr/bin/env python3
"""
Modular Settings View (Refactored)
Composition-based architecture using specialized settings components.
Replaces the monolithic settings_view.py with focused single-responsibility modules.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

import flet as ft
from typing import Dict, Any
import logging

# Import modular settings components
sys_path_added = False
try:
    from ..settings.settings_form_generator import SettingsFormGenerator
    from ..settings.settings_export_import_service import SettingsExportImportService
    from ..settings.settings_reset_service import SettingsResetService
    from ..settings.settings_change_manager import SettingsChangeManager
except ImportError:
    # Add parent directory to path for settings modules
    import sys
    import os
    settings_path = os.path.join(os.path.dirname(__file__), '..', 'settings')
    if settings_path not in sys.path:
        sys.path.insert(0, settings_path)
        sys_path_added = True
    
    from settings_form_generator import SettingsFormGenerator
    from settings_export_import_service import SettingsExportImportService
    from settings_reset_service import SettingsResetService
    from settings_change_manager import SettingsChangeManager

from ..utils.settings_manager import SettingsManager

logger = logging.getLogger(__name__)


class ModularSettingsView:
    """Refactored settings view using composition pattern with specialized components."""
    
    def __init__(self, page: ft.Page, dialog_system, toast_manager):
        """Initialize with modular settings components."""
        self.page = page
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self.settings_manager = SettingsManager()
        
        # Initialize modular components with dependency injection
        self.form_generator = SettingsFormGenerator(page, self._on_setting_changed)
        self.export_import_service = SettingsExportImportService(toast_manager)
        self.reset_service = SettingsResetService(toast_manager, dialog_system)
        self.change_manager = SettingsChangeManager(page, toast_manager)
        
        # Setup callbacks
        self.change_manager.on_changes_detected = self._on_changes_detected
        self.change_manager.on_settings_saved = self._on_settings_saved
        self.change_manager.on_settings_cancelled = self._on_settings_cancelled
        
        # UI state
        self.form_containers = {}
        
        logger.info("✅ Modular settings view initialized with specialized components")
    
    def create_settings_view(self) -> ft.Container:
        """Create the main settings view with modular components"""
        
        # Load current settings
        current_settings = self.settings_manager.load_settings()
        self.change_manager.initialize_settings(current_settings)
        
        # Create form sections using form generator
        self.form_containers = {
            'server': self.form_generator.create_server_settings_form(current_settings),
            'gui': self.form_generator.create_gui_settings_form(current_settings),
            'monitoring': self.form_generator.create_monitoring_settings_form(current_settings),
            'advanced': self.form_generator.create_advanced_settings_form(current_settings)
        }
        
        # Create action bar using change manager
        action_bar = self.change_manager.create_action_bar(
            on_save=self._handle_save_settings,
            on_cancel=self._handle_cancel_changes,
            on_reset_category=self._handle_reset_category,
            on_reset_all=self._handle_reset_all
        )
        
        # Create export/import section
        export_import_section = self._create_export_import_section()
        
        # Create tabs for different setting categories
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Server",
                    icon=ft.Icons.SETTINGS,
                    content=self.form_containers['server']
                ),
                ft.Tab(
                    text="GUI",
                    icon=ft.Icons.PALETTE,
                    content=self.form_containers['gui']
                ),
                ft.Tab(
                    text="Monitoring",
                    icon=ft.Icons.MONITOR_HEART,
                    content=self.form_containers['monitoring']
                ),
                ft.Tab(
                    text="Advanced",
                    icon=ft.Icons.TUNE,
                    content=self.form_containers['advanced']
                )
            ],
            expand=True
        )
        
        # Main layout with action bar at top
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Icon(ft.Icons.SETTINGS, size=28),
                    ft.Text("Settings Configuration", 
                            style=ft.TextThemeStyle.TITLE_LARGE, 
                            expand=True),
                ], alignment=ft.MainAxisAlignment.START),
                
                ft.Divider(),
                
                # Action bar
                action_bar,
                
                # Settings tabs
                tabs,
                
                # Export/Import section
                export_import_section
                
            ], spacing=10, expand=True),
            padding=20,
            expand=True
        )
    
    def _create_export_import_section(self) -> ft.Container:
        """Create export/import controls section"""
        
        export_button = ft.ElevatedButton(
            "Export Settings",
            icon=ft.Icons.DOWNLOAD,
            on_click=self._handle_export_settings,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_100)
        )
        
        import_button = ft.ElevatedButton(
            "Import Settings",
            icon=ft.Icons.UPLOAD,
            on_click=self._handle_import_settings,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_100)
        )
        
        backup_button = ft.OutlinedButton(
            "Create Backup",
            icon=ft.Icons.BACKUP,
            on_click=self._handle_create_backup
        )
        
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.IMPORT_EXPORT, size=20),
                            ft.Text("Export & Import", weight=ft.FontWeight.BOLD)
                        ], spacing=5),
                        
                        ft.Divider(),
                        
                        ft.Row([
                            export_button,
                            import_button,
                            ft.VerticalDivider(),
                            backup_button
                        ], spacing=10)
                    ], spacing=10),
                    padding=15
                ),
                elevation=1
            ),
            margin=ft.Margin(0, 10, 0, 0)
        )
    
    # ============================================================================
    # EVENT HANDLERS (delegated to specialized components)
    # ============================================================================
    
    def _on_setting_changed(self):
        """Handle when any setting changes"""
        # Collect current values from all forms
        current_values = {}
        
        for form_name, form_container in self.form_containers.items():
            form_values = self.form_generator.get_form_values(form_container)
            current_values.update(form_values)
        
        # Update change manager
        self.change_manager.on_setting_changed(current_values)
    
    def _on_changes_detected(self, has_changes: bool, current_settings: Dict[str, Any]):
        """Handle when changes are detected"""
        logger.info(f"Settings changes detected: {has_changes}")
    
    def _on_settings_saved(self, settings: Dict[str, Any]):
        """Handle when settings are successfully saved"""
        logger.info("Settings saved successfully")
    
    def _on_settings_cancelled(self, reverted_settings: Dict[str, Any]):
        """Handle when changes are cancelled"""
        # Update all forms with reverted values
        for form_name, form_container in self.form_containers.items():
            self.form_generator.update_form_values(form_container, reverted_settings)
        
        self.page.update()
        logger.info("Settings changes cancelled")
    
    def _handle_save_settings(self, settings: Dict[str, Any]):
        """Handle save settings action"""
        try:
            # Validate settings using reset service
            validation_errors = self.reset_service.validate_settings_values(settings)
            
            if validation_errors:
                error_message = "Settings validation failed:\n" + "\n".join(validation_errors)
                self.dialog_system.show_error_dialog(
                    title="Validation Error",
                    message=error_message
                )
                return
            
            # Save settings using settings manager
            self.settings_manager.save_settings(settings)
            
            logger.info("Settings saved successfully via modular architecture")
            
        except Exception as e:
            error_message = f"Failed to save settings: {str(e)}"
            logger.error(error_message)
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
    
    def _handle_cancel_changes(self, reverted_settings: Dict[str, Any]):
        """Handle cancel changes action"""
        # Already handled by change manager callback
        pass
    
    def _handle_reset_category(self, category: str):
        """Handle reset category action"""
        current_settings = self.change_manager.current_settings
        
        def apply_category_reset(updated_settings):
            # Update forms with reset values
            for form_name, form_container in self.form_containers.items():
                self.form_generator.update_form_values(form_container, updated_settings)
            
            # Update change manager
            self.change_manager.apply_settings_update(updated_settings)
            self.page.update()
        
        self.reset_service.reset_category(
            category, 
            current_settings, 
            confirm_callback=apply_category_reset
        )
    
    def _handle_reset_all(self):
        """Handle reset all settings action"""
        def apply_full_reset(updated_settings):
            # Update all forms with default values
            for form_name, form_container in self.form_containers.items():
                self.form_generator.update_form_values(form_container, updated_settings)
            
            # Update change manager
            self.change_manager.initialize_settings(updated_settings)
            self.page.update()
        
        self.reset_service.reset_all_settings(confirm_callback=apply_full_reset)
    
    def _handle_export_settings(self, e):
        """Handle export settings action"""
        def on_file_selected(file_path):
            if file_path:
                current_settings = self.change_manager.current_settings
                success, message = self.export_import_service.export_settings(current_settings, file_path)
                
                if success:
                    logger.info(f"Settings exported to: {file_path}")
        
        # Use file picker dialog
        def pick_files_result(e: ft.FilePickerResultEvent):
            if e.path:
                on_file_selected(e.path)
        
        file_picker = ft.FilePicker(on_result=pick_files_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        file_picker.save_file(
            dialog_title="Export Settings",
            file_name="settings.json",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"]
        )
    
    def _handle_import_settings(self, e):
        """Handle import settings action"""
        def on_file_selected(file_path):
            if file_path:
                success, message, imported_settings = self.export_import_service.import_settings(file_path)
                
                if success and imported_settings:
                    # Update all forms with imported values
                    for form_name, form_container in self.form_containers.items():
                        self.form_generator.update_form_values(form_container, imported_settings)
                    
                    # Update change manager
                    self.change_manager.apply_settings_update(imported_settings)
                    self.page.update()
                    
                    logger.info(f"Settings imported from: {file_path}")
        
        # Use file picker dialog
        def pick_files_result(e: ft.FilePickerResultEvent):
            if e.files:
                on_file_selected(e.files[0].path)
        
        file_picker = ft.FilePicker(on_result=pick_files_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        file_picker.pick_files(
            dialog_title="Import Settings",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"]
        )
    
    def _handle_create_backup(self, e):
        """Handle create backup action"""
        current_settings = self.change_manager.current_settings
        success, message = self.export_import_service.create_settings_backup(current_settings)
        
        if success:
            logger.info("Settings backup created successfully")
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings values from all forms"""
        return self.change_manager.current_settings
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        return self.change_manager.has_changes
    
    def get_component_stats(self) -> Dict[str, Any]:
        """Get statistics about settings components"""
        return {
            'current_settings_count': len(self.change_manager.current_settings),
            'changed_settings_count': len(self.change_manager.get_changed_settings()),
            'has_changes': self.change_manager.has_changes,
            'form_sections': list(self.form_containers.keys()),
            'reset_service_categories': list(self.reset_service.default_settings.keys())
        }


# Backward compatibility alias
SettingsView = ModularSettingsView
