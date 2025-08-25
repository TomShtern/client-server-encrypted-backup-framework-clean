#!/usr/bin/env python3
"""
Settings Change Manager
Handles settings change detection, validation, and action management.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

import flet as ft
from typing import Dict, Any, Callable, Optional, List


class SettingsChangeManager:
    """Manages settings change detection and actions"""
    
    def __init__(self, page: ft.Page, toast_manager=None):
        self.page = page
        self.toast_manager = toast_manager
        
        # State tracking
        self.original_settings = {}
        self.current_settings = {}
        self.has_changes = False
        
        # Callbacks
        self.on_changes_detected: Optional[Callable] = None
        self.on_settings_saved: Optional[Callable] = None
        self.on_settings_cancelled: Optional[Callable] = None
    
    def initialize_settings(self, settings: Dict[str, Any]):
        """Initialize with original settings"""
        self.original_settings = settings.copy()
        self.current_settings = settings.copy()
        self.has_changes = False
        self._update_change_status()
    
    def on_setting_changed(self, updated_settings: Dict[str, Any] = None):
        """Handle when a setting value changes"""
        if updated_settings:
            self.current_settings.update(updated_settings)
        
        # Check for changes
        old_has_changes = self.has_changes
        self.has_changes = self._detect_changes()
        
        # Update UI if change status changed
        if old_has_changes != self.has_changes:
            self._update_change_status()
        
        # Trigger callback if provided
        if self.on_changes_detected:
            self.on_changes_detected(self.has_changes, self.current_settings)
    
    def _detect_changes(self) -> bool:
        """Detect if current settings differ from original"""
        try:
            for key, current_value in self.current_settings.items():
                original_value = self.original_settings.get(key)
                if current_value != original_value:
                    return True
            return False
        except Exception as e:
            print(f"Error detecting changes: {e}")
            return False
    
    def _update_change_status(self):
        """Update UI based on change status"""
        if self.page:
            self.page.update()
    
    def get_changed_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get settings that have changed with before/after values"""
        changes = {}
        
        for key, current_value in self.current_settings.items():
            original_value = self.original_settings.get(key)
            if current_value != original_value:
                changes[key] = {
                    'original': original_value,
                    'current': current_value
                }
        
        return changes
    
    def create_action_bar(self, on_save: Callable, on_cancel: Callable, 
                         on_reset_category: Callable, on_reset_all: Callable) -> ft.Container:
        """Create action bar with save, cancel, and reset buttons"""
        
        # Save button
        save_button = ft.ElevatedButton(
            "Save Settings",
            icon=ft.Icons.SAVE,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.ON_PRIMARY
            ),
            disabled=not self.has_changes,
            on_click=lambda e: self._handle_save(on_save)
        )
        
        # Cancel button
        cancel_button = ft.OutlinedButton(
            "Cancel Changes",
            icon=ft.Icons.CANCEL,
            disabled=not self.has_changes,
            on_click=lambda e: self._handle_cancel(on_cancel)
        )
        
        # Reset category dropdown
        reset_category_dropdown = ft.Dropdown(
            label="Reset Category",
            width=200,
            options=[
                ft.dropdown.Option("server", "Server Settings"),
                ft.dropdown.Option("gui", "GUI Preferences"),
                ft.dropdown.Option("monitoring", "Monitoring Config"),
                ft.dropdown.Option("advanced", "Advanced Settings")
            ],
            on_change=lambda e: self._handle_reset_category(e.control.value, on_reset_category)
        )
        
        # Reset all button
        reset_all_button = ft.TextButton(
            "Reset All to Defaults",
            icon=ft.Icons.RESTORE,
            style=ft.ButtonStyle(color=ft.Colors.ERROR),
            on_click=lambda e: self._handle_reset_all(on_reset_all)
        )
        
        # Changes indicator
        changes_indicator = ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.EDIT if self.has_changes else ft.Icons.CHECK_CIRCLE,
                    color=ft.Colors.ORANGE_600 if self.has_changes else ft.Colors.GREEN_600,
                    size=20
                ),
                ft.Text(
                    f"{len(self.get_changed_settings())} changes" if self.has_changes else "No changes",
                    color=ft.Colors.ORANGE_600 if self.has_changes else ft.Colors.GREEN_600,
                    weight=ft.FontWeight.BOLD
                )
            ], spacing=5, tight=True),
            padding=ft.Padding(10, 5, 10, 5),
            bgcolor=ft.Colors.ORANGE_50 if self.has_changes else ft.Colors.GREEN_50,
            border_radius=6
        )
        
        # Store references for updates
        self.save_button = save_button
        self.cancel_button = cancel_button
        self.changes_indicator = changes_indicator
        
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            changes_indicator,
                            ft.Spacer(),
                            save_button,
                            cancel_button
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        
                        ft.Divider(),
                        
                        ft.Row([
                            ft.Text("Reset Options:", weight=ft.FontWeight.BOLD),
                            reset_category_dropdown,
                            ft.VerticalDivider(),
                            reset_all_button
                        ], alignment=ft.MainAxisAlignment.START)
                    ], spacing=10),
                    padding=15
                ),
                elevation=2
            ),
            margin=ft.Margin(0, 0, 0, 20)
        )
    
    def update_action_bar(self):
        """Update action bar state based on changes"""
        if hasattr(self, 'save_button'):
            self.save_button.disabled = not self.has_changes
        
        if hasattr(self, 'cancel_button'):
            self.cancel_button.disabled = not self.has_changes
        
        if hasattr(self, 'changes_indicator'):
            # Update changes indicator
            indicator_row = self.changes_indicator.content
            
            # Update icon
            indicator_row.controls[0].name = ft.Icons.EDIT if self.has_changes else ft.Icons.CHECK_CIRCLE
            indicator_row.controls[0].color = ft.Colors.ORANGE_600 if self.has_changes else ft.Colors.GREEN_600
            
            # Update text
            indicator_row.controls[1].value = f"{len(self.get_changed_settings())} changes" if self.has_changes else "No changes"
            indicator_row.controls[1].color = ft.Colors.ORANGE_600 if self.has_changes else ft.Colors.GREEN_600
            
            # Update container background
            self.changes_indicator.bgcolor = ft.Colors.ORANGE_50 if self.has_changes else ft.Colors.GREEN_50
        
        if self.page:
            self.page.update()
    
    def _handle_save(self, on_save: Callable):
        """Handle save button click"""
        try:
            # Execute save callback
            if on_save:
                on_save(self.current_settings)
            
            # Update original settings to current
            self.original_settings = self.current_settings.copy()
            self.has_changes = False
            self.update_action_bar()
            
            # Show success message
            if self.toast_manager:
                self.toast_manager.show_success("Settings saved successfully")
            
            # Trigger callback
            if self.on_settings_saved:
                self.on_settings_saved(self.current_settings)
                
        except Exception as e:
            error_message = f"Failed to save settings: {str(e)}"
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
    
    def _handle_cancel(self, on_cancel: Callable):
        """Handle cancel button click"""
        try:
            # Revert to original settings
            self.current_settings = self.original_settings.copy()
            self.has_changes = False
            
            # Execute cancel callback
            if on_cancel:
                on_cancel(self.current_settings)
            
            self.update_action_bar()
            
            # Show info message
            if self.toast_manager:
                self.toast_manager.show_info("Changes cancelled")
            
            # Trigger callback
            if self.on_settings_cancelled:
                self.on_settings_cancelled(self.current_settings)
                
        except Exception as e:
            error_message = f"Failed to cancel changes: {str(e)}"
            if self.toast_manager:
                self.toast_manager.show_error(error_message)
    
    def _handle_reset_category(self, category: str, on_reset_category: Callable):
        """Handle reset category selection"""
        if category and on_reset_category:
            on_reset_category(category)
    
    def _handle_reset_all(self, on_reset_all: Callable):
        """Handle reset all button click"""
        if on_reset_all:
            on_reset_all()
    
    def apply_settings_update(self, updated_settings: Dict[str, Any]):
        """Apply updated settings and update change detection"""
        self.current_settings.update(updated_settings)
        self.on_setting_changed()
    
    def force_refresh_state(self):
        """Force refresh of the change detection state"""
        self.has_changes = self._detect_changes()
        self.update_action_bar()
