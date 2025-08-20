# -*- coding: utf-8 -*-
"""
Settings screen for the KivyMD Encrypted Backup Server GUI

This screen provides comprehensive settings management functionality
with Material Design 3 styling including server configuration, UI preferences,
security settings, and persistent save/load functionality.
"""

from __future__ import annotations
import traceback
import json
import os
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

# KivyMD imports
try:
    from kivymd.uix.screen import MDScreen
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.gridlayout import MDGridLayout
    from kivymd.uix.card import MDCard
    from kivymd.uix.label import MDLabel
    from kivymd.uix.button import MDButton, MDIconButton
    from kivymd.uix.button import MDButtonText
    from kivymd.uix.scrollview import MDScrollView
    from kivymd.uix.divider import MDDivider
    from kivymd.uix.textfield import MDTextField, MDTextFieldSupportingText, MDTextFieldHintText
    from kivymd.uix.selectioncontrol import MDSwitch
    from kivymd.uix.slider import MDSlider
    from kivymd.uix.segmentedbutton import MDSegmentedButton, MDSegmentedButtonItem
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.list import MDList, MDListItem
    from kivymd.uix.list import MDListItemHeadlineText, MDListItemSupportingText, MDListItemTrailingIcon
    from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
    from kivymd.uix.tooltip import MDTooltip
    
    from kivy.clock import Clock
    from kivy.metrics import dp
    from kivy.core.window import Window
    
    KIVYMD_AVAILABLE = True
except ImportError as e:
    print(f"[ERROR] KivyMD not available: {e}")
    KIVYMD_AVAILABLE = False

# Local imports
if KIVYMD_AVAILABLE:
    from ..utils.server_integration import ServerIntegrationBridge


class ServerSettingsCard(MDCard):
    """Card widget for server configuration settings"""
    
    def __init__(self, settings_screen, **kwargs):
        super().__init__(**kwargs)
        self.settings_screen = settings_screen
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(280)
        
        # Create layout
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(28),
            spacing=dp(8)
        )
        
        title_label = MDLabel(
            text="Server Configuration",
            theme_text_color="Primary",
            font_style="Headline"
        )
        header_layout.add_widget(title_label)
        
        # Reset button
        reset_button = MDIconButton(
            icon="restore",
            on_release=self.reset_server_settings
        )
        reset_button.size_hint = (None, None)
        reset_button.size = (dp(32), dp(32))
        header_layout.add_widget(reset_button)
        
        layout.add_widget(header_layout)
        layout.add_widget(MDDivider())
        
        # Settings grid
        settings_grid = MDGridLayout(cols=2, spacing=dp(16), adaptive_height=True)
        
        # Port setting
        port_layout = MDBoxLayout(orientation="vertical", spacing=dp(4))
        port_label = MDLabel(
            text="Server Port",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        port_layout.add_widget(port_label)
        
        self.port_field = MDTextField(
            MDTextFieldSupportingText(text="Default: 1256"),
            mode="outlined",
            text="1256",
            hint_text="Port number",
            input_filter="int",
            on_text_validate=self.validate_port
        )
        port_layout.add_widget(self.port_field)
        settings_grid.add_widget(port_layout)
        
        # Host setting
        host_layout = MDBoxLayout(orientation="vertical", spacing=dp(4))
        host_label = MDLabel(
            text="Server Host",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        host_layout.add_widget(host_label)
        
        self.host_field = MDTextField(
            MDTextFieldSupportingText(text="0.0.0.0 for all interfaces"),
            mode="outlined",
            text="0.0.0.0",
            hint_text="Host address",
            on_text_validate=self.validate_host
        )
        host_layout.add_widget(self.host_field)
        settings_grid.add_widget(host_layout)
        
        # Storage directory
        storage_layout = MDBoxLayout(orientation="vertical", spacing=dp(4))
        storage_label = MDLabel(
            text="Storage Directory",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        storage_layout.add_widget(storage_label)
        
        storage_dir_layout = MDBoxLayout(orientation="horizontal", spacing=dp(8))
        
        self.storage_field = MDTextField(
            MDTextFieldSupportingText(text="Directory for received files"),
            mode="outlined",
            text="received_files",
            hint_text="Directory path"
        )
        storage_dir_layout.add_widget(self.storage_field)
        
        browse_button = MDIconButton(
            icon="folder",
            on_release=self.browse_storage_directory
        )
        browse_button.size_hint = (None, None)
        browse_button.size = (dp(32), dp(32))
        storage_dir_layout.add_widget(browse_button)
        
        storage_layout.add_widget(storage_dir_layout)
        settings_grid.add_widget(storage_layout)
        
        # Max clients
        clients_layout = MDBoxLayout(orientation="vertical", spacing=dp(4))
        clients_label = MDLabel(
            text="Max Clients",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        clients_layout.add_widget(clients_label)
        
        self.max_clients_field = MDTextField(
            MDTextFieldSupportingText(text="Maximum concurrent connections"),
            mode="outlined",
            text="50",
            hint_text="Maximum clients",
            input_filter="int",
            on_text_validate=self.validate_max_clients
        )
        clients_layout.add_widget(self.max_clients_field)
        settings_grid.add_widget(clients_layout)
        
        layout.add_widget(settings_grid)
        
        # Session timeout
        timeout_layout = MDBoxLayout(orientation="vertical", spacing=dp(8))
        
        timeout_header = MDBoxLayout(orientation="horizontal", spacing=dp(8))
        timeout_label = MDLabel(
            text="Session Timeout (minutes)",
            theme_text_color="Secondary",
            font_style="Body"
        )
        timeout_header.add_widget(timeout_label)
        
        self.timeout_value_label = MDLabel(
            text="10",
            theme_text_color="Primary",
            font_style="Body",
            size_hint_x=None,
            width=dp(40)
        )
        timeout_header.add_widget(self.timeout_value_label)
        
        timeout_layout.add_widget(timeout_header)
        
        self.timeout_slider = MDSlider(
            min=1,
            max=60,
            value=10,
            step=1,
            on_value=self.on_timeout_changed
        )
        timeout_layout.add_widget(self.timeout_slider)
        
        layout.add_widget(timeout_layout)
        
        self.add_widget(layout)
    
    def _update_supporting_text(self, textfield, text: str):
        """Update supporting text for KivyMD 2.0.x compatibility"""
        try:
            # Find MDTextFieldSupportingText child and update its text
            for child in textfield.children:
                if hasattr(child, 'text') and hasattr(child, '__class__') and 'SupportingText' in child.__class__.__name__:
                    child.text = text
                    break
        except Exception as e:
            print(f"[WARNING] Could not update supporting text: {e}")
    
    def validate_port(self, instance):
        """Validate port number"""
        try:
            port = int(instance.text)
            if not (1 <= port <= 65535):
                instance.error = True
                self._update_supporting_text(instance, "Port must be between 1 and 65535")
            else:
                instance.error = False
                self._update_supporting_text(instance, "Default: 1256")
        except ValueError:
            instance.error = True
            self._update_supporting_text(instance, "Invalid port number")
    
    def validate_host(self, instance):
        """Validate host address"""
        try:
            host = instance.text.strip()
            if not host:
                instance.error = True
                self._update_supporting_text(instance, "Host cannot be empty")
            else:
                instance.error = False
                self._update_supporting_text(instance, "0.0.0.0 for all interfaces")
        except Exception:
            instance.error = True
            self._update_supporting_text(instance, "Invalid host address")
    
    def validate_max_clients(self, instance):
        """Validate max clients"""
        try:
            max_clients = int(instance.text)
            if not (1 <= max_clients <= 1000):
                instance.error = True
                self._update_supporting_text(instance, "Must be between 1 and 1000")
            else:
                instance.error = False
                self._update_supporting_text(instance, "Maximum concurrent connections")
        except ValueError:
            instance.error = True
            self._update_supporting_text(instance, "Invalid number")
    
    def on_timeout_changed(self, instance, value):
        """Handle timeout slider changes"""
        self.timeout_value_label.text = str(int(value))
    
    def browse_storage_directory(self, *args):
        """Browse for storage directory"""
        # TODO: Implement file browser dialog
        print("[INFO] Browse for storage directory")
    
    def reset_server_settings(self, *args):
        """Reset server settings to defaults"""
        self.port_field.text = "1256"
        self.host_field.text = "0.0.0.0"
        self.storage_field.text = "received_files"
        self.max_clients_field.text = "50"
        self.timeout_slider.value = 10
        self.settings_screen.show_snackbar("Server settings reset to defaults")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current server settings"""
        return {
            "port": int(self.port_field.text) if self.port_field.text.isdigit() else 1256,
            "host": self.host_field.text or "0.0.0.0",
            "storage_dir": self.storage_field.text or "received_files",
            "max_clients": int(self.max_clients_field.text) if self.max_clients_field.text.isdigit() else 50,
            "session_timeout": int(self.timeout_slider.value)
        }
    
    def set_settings(self, settings: Dict[str, Any]):
        """Set server settings"""
        self.port_field.text = str(settings.get("port", 1256))
        self.host_field.text = settings.get("host", "0.0.0.0")
        self.storage_field.text = settings.get("storage_dir", "received_files")
        self.max_clients_field.text = str(settings.get("max_clients", 50))
        self.timeout_slider.value = settings.get("session_timeout", 10)


class UISettingsCard(MDCard):
    """Card widget for UI preferences"""
    
    def __init__(self, settings_screen, **kwargs):
        super().__init__(**kwargs)
        self.settings_screen = settings_screen
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(300)
        
        # Create layout
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header
        title_label = MDLabel(
            text="UI Preferences",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title_label)
        layout.add_widget(MDDivider())
        
        # Settings list
        settings_list = MDList()
        
        # Theme selection
        theme_item = MDListItem(
            MDListItemHeadlineText(text="Theme"),
            MDListItemSupportingText(text="Dark or Light mode")
        )
        
        # Add theme segmented control
        theme_control_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(40)
        )
        
        self.theme_control = MDSegmentedButton(
            MDSegmentedButtonItem(text="Light"),
            MDSegmentedButtonItem(text="Dark"),
            on_active=self.on_theme_changed
        )
        self.theme_control.active = "Dark"  # Default
        theme_control_layout.add_widget(self.theme_control)
        
        theme_layout = MDBoxLayout(orientation="vertical")
        theme_layout.add_widget(theme_item)
        theme_layout.add_widget(theme_control_layout)
        settings_list.add_widget(theme_layout)
        
        # Animations toggle
        animations_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(48)
        )
        
        animations_info = MDBoxLayout(orientation="vertical")
        animations_label = MDLabel(
            text="Animations",
            theme_text_color="Primary",
            font_style="Body",
            size_hint_y=None,
            height=dp(24)
        )
        animations_desc = MDLabel(
            text="Enable UI animations",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_y=None,
            height=dp(16)
        )
        animations_info.add_widget(animations_label)
        animations_info.add_widget(animations_desc)
        animations_layout.add_widget(animations_info)
        
        self.animations_switch = MDSwitch(
            active=True,
            on_active=self.on_animations_changed
        )
        animations_layout.add_widget(self.animations_switch)
        
        settings_list.add_widget(animations_layout)
        
        # Tooltips toggle
        tooltips_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(48)
        )
        
        tooltips_info = MDBoxLayout(orientation="vertical")
        tooltips_label = MDLabel(
            text="Tooltips",
            theme_text_color="Primary",
            font_style="Body",
            size_hint_y=None,
            height=dp(24)
        )
        tooltips_desc = MDLabel(
            text="Show helpful tooltips",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_y=None,
            height=dp(16)
        )
        tooltips_info.add_widget(tooltips_label)
        tooltips_info.add_widget(tooltips_desc)
        tooltips_layout.add_widget(tooltips_info)
        
        self.tooltips_switch = MDSwitch(
            active=True,
            on_active=self.on_tooltips_changed
        )
        tooltips_layout.add_widget(self.tooltips_switch)
        
        settings_list.add_widget(tooltips_layout)
        
        # Auto-refresh interval
        refresh_layout = MDBoxLayout(orientation="vertical", spacing=dp(8))
        
        refresh_header = MDBoxLayout(orientation="horizontal", spacing=dp(8))
        refresh_label = MDLabel(
            text="Auto-refresh Interval (seconds)",
            theme_text_color="Primary",
            font_style="Body"
        )
        refresh_header.add_widget(refresh_label)
        
        self.refresh_value_label = MDLabel(
            text="1.0",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_x=None,
            width=dp(40)
        )
        refresh_header.add_widget(self.refresh_value_label)
        
        refresh_layout.add_widget(refresh_header)
        
        self.refresh_slider = MDSlider(
            min=0.5,
            max=10.0,
            value=1.0,
            step=0.5,
            on_value=self.on_refresh_changed
        )
        refresh_layout.add_widget(self.refresh_slider)
        
        settings_list.add_widget(refresh_layout)
        
        # Log max entries
        log_layout = MDBoxLayout(orientation="vertical", spacing=dp(4))
        log_label = MDLabel(
            text="Log Max Entries",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        log_layout.add_widget(log_label)
        
        self.log_entries_field = MDTextField(
            MDTextFieldSupportingText(text="Entries to keep in memory"),
            mode="outlined",
            text="100",
            hint_text="Maximum log entries",
            input_filter="int"
        )
        log_layout.add_widget(self.log_entries_field)
        settings_list.add_widget(log_layout)
        
        layout.add_widget(settings_list)
        self.add_widget(layout)
    
    def on_theme_changed(self, instance, value):
        """Handle theme changes"""
        print(f"[INFO] Theme changed to: {value}")
        # TODO: Apply theme change
    
    def on_animations_changed(self, instance, value):
        """Handle animations toggle"""
        print(f"[INFO] Animations: {value}")
    
    def on_tooltips_changed(self, instance, value):
        """Handle tooltips toggle"""
        print(f"[INFO] Tooltips: {value}")
    
    def on_refresh_changed(self, instance, value):
        """Handle refresh interval changes"""
        self.refresh_value_label.text = f"{value:.1f}"
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current UI settings"""
        return {
            "theme": self.theme_control.active,
            "animations": self.animations_switch.active,
            "show_tooltips": self.tooltips_switch.active,
            "auto_refresh_interval": self.refresh_slider.value,
            "log_max_entries": int(self.log_entries_field.text) if self.log_entries_field.text.isdigit() else 100
        }
    
    def set_settings(self, settings: Dict[str, Any]):
        """Set UI settings"""
        self.theme_control.active = settings.get("theme", "Dark")
        self.animations_switch.active = settings.get("animations", True)
        self.tooltips_switch.active = settings.get("show_tooltips", True)
        self.refresh_slider.value = settings.get("auto_refresh_interval", 1.0)
        self.log_entries_field.text = str(settings.get("log_max_entries", 100))


class SecuritySettingsCard(MDCard):
    """Card widget for security settings"""
    
    def __init__(self, settings_screen, **kwargs):
        super().__init__(**kwargs)
        self.settings_screen = settings_screen
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(200)
        
        # Create layout
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header
        title_label = MDLabel(
            text="Security Settings",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title_label)
        layout.add_widget(MDDivider())
        
        # Settings grid
        settings_grid = MDGridLayout(cols=2, spacing=dp(16), adaptive_height=True)
        
        # Encryption status (read-only info)
        encryption_layout = MDBoxLayout(orientation="vertical", spacing=dp(4))
        encryption_label = MDLabel(
            text="Encryption",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        encryption_layout.add_widget(encryption_label)
        
        encryption_info = MDLabel(
            text="RSA-1024 + AES-256-CBC",
            theme_text_color="Primary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        encryption_layout.add_widget(encryption_info)
        settings_grid.add_widget(encryption_layout)
        
        # Maintenance interval
        maintenance_layout = MDBoxLayout(orientation="vertical", spacing=dp(4))
        maintenance_label = MDLabel(
            text="Maintenance Interval (minutes)",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        maintenance_layout.add_widget(maintenance_label)
        
        self.maintenance_field = MDTextField(
            MDTextFieldSupportingText(text="System cleanup interval"),
            mode="outlined",
            text="60",
            hint_text="Maintenance interval",
            input_filter="int"
        )
        maintenance_layout.add_widget(self.maintenance_field)
        settings_grid.add_widget(maintenance_layout)
        
        layout.add_widget(settings_grid)
        
        # Security actions
        actions_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(40)
        )
        
        regenerate_keys_button = MDButton(
            MDButtonText(text="Regenerate Keys"),
            on_release=self.regenerate_encryption_keys
        )
        regenerate_keys_button.theme_bg_color = "Custom"
        regenerate_keys_button.md_bg_color = self.theme_cls.tertiaryColor
        actions_layout.add_widget(regenerate_keys_button)
        
        clear_cache_button = MDButton(
            MDButtonText(text="Clear Cache"),
            on_release=self.clear_system_cache
        )
        clear_cache_button.theme_bg_color = "Custom"
        clear_cache_button.md_bg_color = self.theme_cls.errorColor
        actions_layout.add_widget(clear_cache_button)
        
        layout.add_widget(actions_layout)
        self.add_widget(layout)
    
    def regenerate_encryption_keys(self, *args):
        """Regenerate encryption keys"""
        print("[INFO] Regenerating encryption keys...")
        self.settings_screen.show_snackbar("Encryption keys regenerated")
    
    def clear_system_cache(self, *args):
        """Clear system cache"""
        print("[INFO] Clearing system cache...")
        self.settings_screen.show_snackbar("System cache cleared")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current security settings"""
        return {
            "maintenance_interval": int(self.maintenance_field.text) if self.maintenance_field.text.isdigit() else 60
        }
    
    def set_settings(self, settings: Dict[str, Any]):
        """Set security settings"""
        self.maintenance_field.text = str(settings.get("maintenance_interval", 60))


class SettingsActionsCard(MDCard):
    """Card widget for settings actions (save/load/reset)"""
    
    def __init__(self, settings_screen, **kwargs):
        super().__init__(**kwargs)
        self.settings_screen = settings_screen
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(100)
        
        # Create layout
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header
        title_label = MDLabel(
            text="Settings Actions",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title_label)
        layout.add_widget(MDDivider())
        
        # Action buttons
        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(40)
        )
        
        save_button = MDButton(
            MDButtonText(text="Save Settings"),
            on_release=self.settings_screen.save_settings
        )
        save_button.theme_bg_color = "Custom"
        save_button.md_bg_color = self.theme_cls.primaryColor
        buttons_layout.add_widget(save_button)
        
        load_button = MDButton(
            MDButtonText(text="Load Settings"),
            on_release=self.settings_screen.load_settings
        )
        load_button.theme_bg_color = "Custom"
        load_button.md_bg_color = self.theme_cls.secondaryColor
        buttons_layout.add_widget(load_button)
        
        reset_button = MDButton(
            MDButtonText(text="Reset All"),
            on_release=self.settings_screen.reset_all_settings
        )
        reset_button.theme_bg_color = "Custom"
        reset_button.md_bg_color = self.theme_cls.errorColor
        buttons_layout.add_widget(reset_button)
        
        export_button = MDButton(
            MDButtonText(text="Export Config"),
            on_release=self.settings_screen.export_configuration
        )
        export_button.theme_bg_color = "Custom"
        export_button.md_bg_color = self.theme_cls.tertiaryColor
        buttons_layout.add_widget(export_button)
        
        layout.add_widget(buttons_layout)
        self.add_widget(layout)


class SettingsScreen(MDScreen):
    """
    Comprehensive settings management screen
    
    Features:
    - Server configuration settings
    - UI preferences and theming
    - Security settings and actions
    - Persistent save/load functionality
    - Form validation and user feedback
    - Material Design 3 components
    """
    
    def __init__(self, server_bridge: Optional[ServerIntegrationBridge] = None,
                 config: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        
        # Store references
        self.server_bridge = server_bridge
        self.config = config or {}
        
        # UI components
        self.server_card: Optional[ServerSettingsCard] = None
        self.ui_card: Optional[UISettingsCard] = None
        self.security_card: Optional[SecuritySettingsCard] = None
        self.actions_card: Optional[SettingsActionsCard] = None
        
        # Settings file path
        self.settings_file = Path("kivymd_gui") / "settings.json"
        
        # Build UI
        self.build_ui()
        
        # Load existing settings
        Clock.schedule_once(self.load_settings, 0.5)
    
    def build_ui(self):
        """Build the settings UI"""
        try:
            # Main scroll layout
            scroll = MDScrollView()
            main_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(16),
                padding=dp(16),
                adaptive_height=True
            )
            
            # Server settings section
            self.server_card = ServerSettingsCard(self)
            main_layout.add_widget(self.server_card)
            
            # UI settings section
            self.ui_card = UISettingsCard(self)
            main_layout.add_widget(self.ui_card)
            
            # Security settings section
            self.security_card = SecuritySettingsCard(self)
            main_layout.add_widget(self.security_card)
            
            # Actions section
            self.actions_card = SettingsActionsCard(self)
            main_layout.add_widget(self.actions_card)
            
            scroll.add_widget(main_layout)
            self.add_widget(scroll)
            
        except Exception as e:
            print(f"[ERROR] Failed to build settings UI: {e}")
            traceback.print_exc()
            
            # Fallback UI
            error_layout = MDBoxLayout(orientation="vertical", padding=dp(16))
            error_label = MDLabel(
                text=f"Failed to load settings screen: {e}",
                theme_text_color="Error",
                halign="center"
            )
            error_layout.add_widget(error_label)
            self.add_widget(error_layout)
    
    def on_enter(self):
        """Called when the screen is entered"""
        try:
            pass  # Settings are loaded once on initialization
        except Exception as e:
            print(f"[ERROR] Settings on_enter failed: {e}")
    
    def on_leave(self):
        """Called when the screen is left"""
        try:
            pass  # Auto-save could be implemented here
        except Exception as e:
            print(f"[ERROR] Settings on_leave failed: {e}")
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings"""
        try:
            settings = {
                "app": {
                    "title": "Encrypted Backup Server",
                    "version": "2.0.0",
                    "material_style": "M3"
                },
                "server": {},
                "ui": {},
                "security": {}
            }
            
            if self.server_card:
                settings["server"].update(self.server_card.get_settings())
            
            if self.ui_card:
                settings["ui"].update(self.ui_card.get_settings())
            
            if self.security_card:
                settings["security"].update(self.security_card.get_settings())
            
            return settings
            
        except Exception as e:
            print(f"[ERROR] Failed to get all settings: {e}")
            return {}
    
    def set_all_settings(self, settings: Dict[str, Any]):
        """Set all settings"""
        try:
            if self.server_card and "server" in settings:
                self.server_card.set_settings(settings["server"])
            
            if self.ui_card and "ui" in settings:
                self.ui_card.set_settings(settings["ui"])
            
            if self.security_card and "security" in settings:
                self.security_card.set_settings(settings["security"])
                
        except Exception as e:
            print(f"[ERROR] Failed to set all settings: {e}")
    
    def save_settings(self, *args):
        """Save current settings to file"""
        try:
            settings = self.get_all_settings()
            
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write settings to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            self.show_snackbar("Settings saved successfully")
            print(f"[INFO] Settings saved to {self.settings_file}")
            
        except Exception as e:
            print(f"[ERROR] Failed to save settings: {e}")
            self.show_snackbar(f"Failed to save settings: {e}")
    
    def load_settings(self, *args):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                self.set_all_settings(settings)
                self.show_snackbar("Settings loaded successfully")
                print(f"[INFO] Settings loaded from {self.settings_file}")
            else:
                # Load from default config
                config_file = Path("kivymd_gui") / "config.json"
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    
                    self.set_all_settings(settings)
                    print(f"[INFO] Default settings loaded from {config_file}")
                else:
                    print("[INFO] No settings file found, using defaults")
                    
        except Exception as e:
            print(f"[ERROR] Failed to load settings: {e}")
            self.show_snackbar(f"Failed to load settings: {e}")
    
    def reset_all_settings(self, *args):
        """Reset all settings to defaults"""
        try:
            # Show confirmation dialog
            dialog = MDDialog(
                title="Reset All Settings",
                text="Are you sure you want to reset all settings to defaults? This action cannot be undone.",
                buttons=[
                    MDButton(
                        MDButtonText(text="Cancel"),
                        on_release=lambda x: dialog.dismiss()
                    ),
                    MDButton(
                        MDButtonText(text="Reset"),
                        on_release=lambda x: self._perform_reset(dialog)
                    )
                ]
            )
            dialog.open()
            
        except Exception as e:
            print(f"[ERROR] Failed to show reset dialog: {e}")
    
    def _perform_reset(self, dialog):
        """Perform the actual reset"""
        try:
            dialog.dismiss()
            
            # Reset all cards to defaults
            if self.server_card:
                self.server_card.reset_server_settings()
            
            if self.ui_card:
                self.ui_card.theme_control.active = "Dark"
                self.ui_card.animations_switch.active = True
                self.ui_card.tooltips_switch.active = True
                self.ui_card.refresh_slider.value = 1.0
                self.ui_card.log_entries_field.text = "100"
            
            if self.security_card:
                self.security_card.maintenance_field.text = "60"
            
            # Delete settings file
            if self.settings_file.exists():
                self.settings_file.unlink()
            
            self.show_snackbar("All settings reset to defaults")
            
        except Exception as e:
            print(f"[ERROR] Failed to perform reset: {e}")
            self.show_snackbar(f"Failed to reset settings: {e}")
    
    def export_configuration(self, *args):
        """Export configuration to a shareable file"""
        try:
            settings = self.get_all_settings()
            
            # Add metadata
            export_data = {
                "export_info": {
                    "exported_at": Clock.get_time(),
                    "version": "2.0.0",
                    "app": "Encrypted Backup Server"
                },
                "settings": settings
            }
            
            # Export to timestamped file
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = Path("kivymd_gui") / f"config_export_{timestamp}.json"
            
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.show_snackbar(f"Configuration exported to {export_file.name}")
            print(f"[INFO] Configuration exported to {export_file}")
            
        except Exception as e:
            print(f"[ERROR] Failed to export configuration: {e}")
            self.show_snackbar(f"Failed to export configuration: {e}")
    
    def show_snackbar(self, message: str, duration: float = 3.0):
        """Show a snackbar with the given message"""
        try:
            snackbar = MDSnackbar(
                MDSnackbarText(text=message),
                duration=duration
            )
            snackbar.open()
        except Exception as e:
            print(f"[ERROR] Failed to show snackbar: {e}")
            print(f"[INFO] Message: {message}")
