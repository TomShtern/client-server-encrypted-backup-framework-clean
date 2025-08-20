# -*- coding: utf-8 -*-
"""
Settings screen for the KivyMD Encrypted Backup Server GUI

This screen provides comprehensive settings management functionality
with Material Design 3 styling including server configuration,
UI preferences, security settings, and persistent configuration.
"""

from __future__ import annotations
import json
import traceback
from typing import Optional, Dict, Any
from pathlib import Path

# Ensure UTF-8 solution is available
try:
    import Shared.utils.utf8_solution
except ImportError:
    pass

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
    from kivymd.uix.textfield import MDTextField
    from kivymd.uix.slider import MDSlider
    from kivymd.uix.switch import MDSwitch
    from kivymd.uix.list import MDList, MDListItem
    from kivymd.uix.list import MDListItemHeadlineText, MDListItemSupportingText
    from kivymd.uix.segmentedcontrol import MDSegmentedControl, MDSegmentedControlItem
    from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.dialog import MDDialogHeadlineText, MDDialogContentText
    from kivymd.uix.dialog import MDDialogButtonContainer, MDDialogIcon
    
    from kivy.clock import Clock
    from kivy.metrics import dp
    
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
        self.height = dp(320)
        
        # Create layout
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header
        title_label = MDLabel(
            text="Server Configuration",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title_label)
        layout.add_widget(MDDivider())
        
        # Settings grid
        settings_grid = MDGridLayout(cols=2, spacing=dp(16), adaptive_height=True)
        
        # Host setting
        host_layout = MDBoxLayout(orientation="vertical", spacing=dp(4))
        host_label = MDLabel(
            text="Host Address",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        host_layout.add_widget(host_label)
        
        self.host_field = MDTextField(
            mode="outlined",
            text="0.0.0.0",
            hint_text="Host address",
            helper_text="0.0.0.0 for all interfaces",
            on_text_validate=self.validate_host
        )
        host_layout.add_widget(self.host_field)
        settings_grid.add_widget(host_layout)
        
        # Port setting
        port_layout = MDBoxLayout(orientation="vertical", spacing=dp(4))
        port_label = MDLabel(
            text="Port",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        port_layout.add_widget(port_label)
        
        self.port_field = MDTextField(
            mode="outlined",
            text="1256",
            hint_text="Port number",
            helper_text="Default: 1256",
            input_filter="int",
            on_text_validate=self.validate_port
        )
        port_layout.add_widget(self.port_field)
        settings_grid.add_widget(port_layout)
        
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
            mode="outlined",
            text="received_files",
            hint_text="Directory path",
            helper_text="Directory for received files"
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
            mode="outlined",
            text="50",
            hint_text="Maximum clients",
            helper_text="Maximum concurrent connections",
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
    
    def validate_port(self, instance):
        """Validate port number"""
        try:
            port = int(instance.text)
            if not (1 <= port <= 65535):
                instance.error = True
                instance.helper_text = "Port must be between 1 and 65535"
            else:
                instance.error = False
                instance.helper_text = "Default: 1256"
        except ValueError:
            instance.error = True
            instance.helper_text = "Invalid port number"
    
    def validate_host(self, instance):
        """Validate host address"""
        try:
            host = instance.text.strip()
            if not host:
                instance.error = True
                instance.helper_text = "Host cannot be empty"
            else:
                instance.error = False
                instance.helper_text = "0.0.0.0 for all interfaces"
        except Exception:
            instance.error = True
            instance.helper_text = "Invalid host address"
    
    def validate_max_clients(self, instance):
        """Validate max clients"""
        try:
            max_clients = int(instance.text)
            if not (1 <= max_clients <= 1000):
                instance.error = True
                instance.helper_text = "Must be between 1 and 1000"
            else:
                instance.error = False
                instance.helper_text = "Maximum concurrent connections"
        except ValueError:
            instance.error = True
            instance.helper_text = "Invalid number"
    
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
                print("[INFO] No settings file found, using defaults")
                
        except Exception as e:
            print(f"[ERROR] Failed to load settings: {e}")
            self.show_snackbar(f"Failed to load settings: {e}")
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings"""
        try:
            settings = {
                "app": {
                    "title": "Encrypted Backup Server",
                    "version": "2.0.0",
                    "material_style": "M3"
                },
                "server": {}
            }
            
            if self.server_card:
                settings["server"].update(self.server_card.get_settings())
            
            return settings
            
        except Exception as e:
            print(f"[ERROR] Failed to get all settings: {e}")
            return {}
    
    def set_all_settings(self, settings: Dict[str, Any]):
        """Set all settings"""
        try:
            if self.server_card and "server" in settings:
                self.server_card.set_settings(settings["server"])
                
        except Exception as e:
            print(f"[ERROR] Failed to set all settings: {e}")
    
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