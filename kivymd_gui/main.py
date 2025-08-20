# -*- coding: utf-8 -*-
"""
main.py - KivyMD Encrypted Backup Server GUI Application
Main entry point for the Material Design 3 server management interface
"""

from __future__ import annotations
import sys
import os
import json
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

# --- VENV CHECK: Ensure we're running inside kivy_venv_new ---
expected_venv = "kivy_venv_new"
venv_path = os.environ.get("VIRTUAL_ENV", "")
if expected_venv not in venv_path:
    print(f"[ERROR] You are NOT running inside the '{expected_venv}' virtual environment.")
    print("To fix: Activate your venv before running this script:")
    print("  cd C:\\Users\\tom7s\\Desktopp\\Claude_Folder_2\\Client_Server_Encrypted_Backup_Framework")
    print("  .\\kivy_venv_new\\Scripts\\activate")
    print("  python kivymd_gui\\main.py")
    sys.exit(1)

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# UTF-8 solution import - MUST be imported early to fix encoding issues
try:
    import Shared.utils.utf8_solution
    print("[INFO] UTF-8 solution enabled for KivyMD GUI")
except ImportError:
    print("[WARNING] Could not enable UTF-8 solution - encoding issues may occur.")

# Sentry error tracking initialization
try:
    from Shared.sentry_config import init_sentry
    SENTRY_AVAILABLE = True
except ImportError:
    print("[WARNING] Sentry configuration not available - error tracking disabled")
    SENTRY_AVAILABLE = False

# Kivy config - must be set before importing kivy modules
try:
    from kivy.config import Config
except ImportError:
    print("[ERROR] Kivy is not installed in your current environment.")
    print("To fix: Activate your venv and run:")
    print("  pip install kivy==2.3.1")
    sys.exit(1)
Config.set('graphics', 'width', '1400')
Config.set('graphics', 'height', '900')
Config.set('graphics', 'minimum_width', '1000')
Config.set('graphics', 'minimum_height', '700')
# KivyMD and Kivy imports
try:
    from kivymd.app import MDApp
    from kivymd.uix.screenmanager import MDScreenManager
    from kivymd.uix.screen import MDScreen
    # NavigationRail components removed due to animation stability issues in KivyMD 2.0.x
    from kivymd.uix.button import MDIconButton
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarTitle, MDTopAppBarLeadingButtonContainer, MDTopAppBarTrailingButtonContainer, MDActionTopAppBarButton
    from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
    from kivy.clock import Clock
    from kivy.metrics import dp
    from kivy.core.window import Window
    KIVYMD_AVAILABLE = True
    
except ImportError as e:
    print(f"[ERROR] KivyMD not available: {e}")
    print("Please install KivyMD: pip install git+https://github.com/kivymd/KivyMD.git@d2f7740")
    KIVYMD_AVAILABLE = False
    sys.exit(1)

# Local imports
from kivymd_gui.themes.custom_theme import CustomTheme, ThemeConfig
from kivymd_gui.utils.server_integration import get_server_bridge, ServerStatus
from kivymd_gui.screens.dashboard import DashboardScreen
from kivymd_gui.screens.clients import ClientsScreen
from kivymd_gui.screens.settings import SettingsScreen
from kivymd_gui.screens.files import FilesScreen
from kivymd_gui.screens.analytics import AnalyticsScreen
from kivymd_gui.screens.database import DatabaseScreen
from kivymd_gui.screens.logs import LogsScreen

# Import server instance if available
try:
    from python_server.server.backup_server import BackupServer
    SERVER_AVAILABLE = True
except ImportError:
    BackupServer = None
    SERVER_AVAILABLE = False
    print("[INFO] Server module not available - running in standalone mode")


class EncryptedBackupServerApp(MDApp):
    """Main KivyMD Application for Encrypted Backup Server"""
    
    # Type annotations for instance variables (VS Code Pylance compatibility)
    screen_manager: Optional[MDScreenManager] = None
    navigation_panel: Optional[MDBoxLayout] = None 
    nav_buttons: Optional[Dict[str, Any]] = None
    top_bar: Optional[MDTopAppBar] = None
    server_bridge: Optional[Any] = None
    config_data: Dict[str, Any]
    theme_config: Optional[Any] = None
    server_instance: Optional[Any] = None
    current_screen: str = "dashboard"
    update_event: Optional[Any] = None
    update_interval: float = 1.0
    last_status: Optional[Any] = None
    
    def __init__(self, server_instance: Optional[Any] = None, **kwargs):
        super().__init__(**kwargs)
        
        # App metadata
        self.title = "Encrypted Backup Server"
        self.icon = str(Path(__file__).parent / "assets" / "images" / "icon.png")
        
        # Configuration
        self.config_data = self.load_configuration()
        try:
            self.theme_config = ThemeConfig(self.config_data)
        except Exception as e:
            print(f"[WARNING] Theme configuration failed: {e}")
            self.theme_config = None
        
        # Apply theme configuration
        self.theme_cls.theme_style = self.config_data.get("app", {}).get("theme", "Dark")
        self.theme_cls.primary_palette = self.config_data.get("app", {}).get("primary_color", "Blue")
        self.theme_cls.material_style = "M3"
        
        # Server integration
        self.server_instance = server_instance
        self.server_bridge = None
        
        # UI components
        self.screen_manager = None
        self.navigation_panel = None
        self.nav_buttons = None
        self.top_bar = None
        
        # Update scheduling
        self.update_event = None
        self.update_interval = self.config_data.get("ui", {}).get("auto_refresh_interval", 1.0)
        
        # Navigation state
        self.current_screen = "dashboard"
    
    def build(self):
        """Build the application UI"""
        try:
            # Initialize server bridge
            self.setup_server_integration()
            
            # Create main layout
            main_layout = self.create_main_layout()
            
            # Schedule updates
            self.schedule_periodic_updates()
            
            # Set initial navigation and show startup message
            Clock.schedule_once(lambda dt: self._set_initial_navigation_state(), 0.5)
            Clock.schedule_once(lambda dt: self.show_startup_message(), 2.0)
            
            return main_layout
            
        except Exception as e:
            print(f"[ERROR] Failed to build application: {e}")
            traceback.print_exc()
            return MDBoxLayout()  # Return empty layout as fallback
    
    def setup_server_integration(self):
        """Initialize server integration bridge"""
        try:
            self.server_bridge = get_server_bridge()
            if self.server_instance:
                self.server_bridge.set_server_instance(self.server_instance)
                print("[INFO] Server integration initialized with provided instance")
            else:
                print("[INFO] Server integration initialized in standalone mode")
            
            # Register for status updates
            self.server_bridge.add_status_callback(self.on_server_status_update)
            
        except Exception as e:
            print(f"[WARNING] Failed to setup server integration: {e}")
            self.server_bridge = None
    
    def create_main_layout(self) -> MDBoxLayout:
        """Create the main application layout"""
        # Main container
        main_layout = MDBoxLayout(orientation="vertical")
        
        # Top app bar
        self.top_bar = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon="menu",
                    on_release=lambda x: self.show_menu()
                )
            ),
            MDTopAppBarTitle(
                text="Server Dashboard"
            ),
            MDTopAppBarTrailingButtonContainer(
                MDActionTopAppBarButton(
                    icon="refresh",
                    on_release=lambda x: self.refresh_data()
                ),
                MDActionTopAppBarButton(
                    icon="theme-light-dark",
                    on_release=lambda x: self.toggle_theme()
                )
            ),
            type="small"
        )
        main_layout.add_widget(self.top_bar)
        
        # Content area with navigation
        content_layout = MDBoxLayout(orientation="horizontal")
        
        # Navigation panel (replacing NavigationRail to avoid animation bug)
        self.navigation_panel = self.create_navigation_panel()
        content_layout.add_widget(self.navigation_panel)
        
        # Screen manager
        self.screen_manager = self.create_screen_manager()
        content_layout.add_widget(self.screen_manager)
        
        main_layout.add_widget(content_layout)
        
        return main_layout
    
    def create_navigation_panel(self) -> MDBoxLayout:
        """Create a simple navigation panel using buttons to avoid NavigationRail animation bug"""
        from kivymd.uix.button import MDIconButton
        from kivymd.uix.label import MDLabel
        
        nav_panel = MDBoxLayout(
            orientation="vertical",
            size_hint_x=None,
            width="80dp",
            spacing="8dp",
            padding=["8dp", "16dp", "8dp", "16dp"]
        )
        
        # Navigation items
        nav_items = [
            ("dashboard", "view-dashboard", "Dashboard"),
            ("clients", "account-group", "Clients"), 
            ("files", "file-multiple", "Files"),
            ("analytics", "chart-line", "Analytics"),
            ("database", "database", "Database"),
            ("logs", "text-box-multiple", "Logs"),
            ("settings", "cog", "Settings")
        ]
        
        self.nav_buttons = {}
        
        for screen_name, icon, text in nav_items:
            # Create icon button for navigation
            nav_button = MDIconButton(
                icon=icon,
                theme_icon_color="Custom", 
                icon_color=self.theme_cls.onSurfaceColor,
                size_hint_y=None,
                height="48dp",
                on_release=lambda x, screen=screen_name: self.navigate_to_screen(screen)
            )
            nav_button.screen_name = screen_name
            nav_button.tooltip_text = text
            
            self.nav_buttons[screen_name] = nav_button
            nav_panel.add_widget(nav_button)
        
        return nav_panel
    
    def _set_initial_navigation_state(self):
        """Set initial navigation to dashboard after UI is fully loaded"""
        try:
            print("[INFO] Setting initial navigation to dashboard")
            # Navigate to dashboard programmatically
            Clock.schedule_once(lambda dt: self.navigate_to_screen("dashboard"), 0.1)
                        
        except Exception as e:
            print(f"[WARNING] Initial navigation state setup failed: {e}")
    
    def create_screen_manager(self) -> MDScreenManager:
        """Create and populate the screen manager"""
        screen_manager = MDScreenManager()
        
        # Create screens with server bridge
        try:
            print("[INFO] Creating dashboard screen...")
            dashboard = DashboardScreen(
                name="dashboard",
                server_bridge=self.server_bridge,
                config=self.config_data
            )
            print(f"[INFO] Dashboard screen created, children count: {len(dashboard.children)}")
            screen_manager.add_widget(dashboard)
            print("[INFO] Dashboard added to screen manager")
            
            # Add additional screens with KivyMD 2.0.x compatible initialization
            clients = ClientsScreen(
                name="clients", 
                server_bridge=self.server_bridge,
                config=self.config_data
            )
            screen_manager.add_widget(clients)
            
            settings = SettingsScreen(
                name="settings",
                server_bridge=self.server_bridge,
                config=self.config_data
            )
            screen_manager.add_widget(settings)
            
            # Add enhanced screens with Material Design 3 implementations
            files_screen = FilesScreen(name="files")
            screen_manager.add_widget(files_screen)
            
            analytics_screen = AnalyticsScreen(name="analytics")  
            screen_manager.add_widget(analytics_screen)
            
            database_screen = DatabaseScreen(name="database")
            screen_manager.add_widget(database_screen)
            
            logs_screen = LogsScreen(name="logs")
            screen_manager.add_widget(logs_screen)
            
        except Exception as e:
            print(f"[ERROR] Failed to create screens: {e}")
            traceback.print_exc()
            
            # Add a simple fallback screen if dashboard creation fails
            from kivymd.uix.label import MDLabel
            fallback_screen = MDScreen(name="dashboard")
            fallback_screen.add_widget(MDLabel(
                text="Dashboard Loading...\n\nPlease check console for errors",
                halign="center",
                theme_text_color="Primary"
            ))
            screen_manager.add_widget(fallback_screen)
            print("[INFO] Added fallback dashboard screen")
        
        return screen_manager
    
    def navigate_to_screen(self, screen_name: str) -> None:
        """Navigate to a specific screen"""
        try:
            if self.screen_manager and screen_name in self.screen_manager.screen_names:
                self.screen_manager.current = screen_name
                self.current_screen = screen_name
                
                # Update top bar title if top_bar exists
                if self.top_bar:
                    screen_titles = {
                        "dashboard": "Server Dashboard",
                        "clients": "Client Management",
                        "files": "File Management", 
                        "analytics": "Analytics & Reports",
                        "database": "Database Browser",
                        "logs": "System Logs",
                        "settings": "Settings & Configuration"
                    }
                    # Find and update MDTopAppBarTitle component
                    for child in self.top_bar.children:
                        if hasattr(child, 'text') and hasattr(child, '__class__') and 'Title' in child.__class__.__name__:
                            child.text = screen_titles.get(screen_name, "Server Control")
                            break
                
                # Update navigation panel active state safely  
                if hasattr(self, 'nav_buttons'):
                    self._update_navigation_state(screen_name)
                
                print(f"[INFO] Navigated to {screen_name}")
            else:
                self.show_snackbar(f"Screen '{screen_name}' not available yet")
                
        except Exception as e:
            print(f"[ERROR] Navigation failed: {e}")
            self.show_snackbar("Navigation error occurred")
    
    def _update_navigation_state(self, target_screen: str):
        """Update navigation button states safely"""
        try:
            if not hasattr(self, 'nav_buttons'):
                return
                
            # Update button colors to show active state
            for screen_name, button in self.nav_buttons.items():
                if screen_name == target_screen:
                    # Active button - use accent/primary color  
                    button.icon_color = self.theme_cls.primaryColor
                else:
                    # Inactive button - use surface color
                    button.icon_color = self.theme_cls.onSurfaceColor
                        
        except Exception as e:
            print(f"[WARNING] Navigation state update failed: {e}")
    
    def schedule_periodic_updates(self):
        """Schedule periodic updates for real-time data"""
        if self.update_event:
            self.update_event.cancel()
        
        self.update_event = Clock.schedule_interval(
            self.periodic_update,
            self.update_interval
        )
    
    def periodic_update(self, dt):
        """Perform periodic updates"""
        try:
            # Update server status
            if self.server_bridge:
                # Server bridge handles its own updates
                pass
                
            # Update current screen if it has an update method
            if self.screen_manager is not None:
                current_screen = self.screen_manager.current_screen
                if hasattr(current_screen, 'periodic_update'):
                    current_screen.periodic_update(dt)
                
        except Exception as e:
            print(f"[ERROR] Periodic update failed: {e}")
    
    def on_server_status_update(self, status: ServerStatus):
        """Handle server status updates from bridge"""
        try:
            # Update current screen if it handles server status
            if self.screen_manager is not None:
                current_screen = self.screen_manager.current_screen
                if hasattr(current_screen, 'on_server_status_update'):
                    current_screen.on_server_status_update(status)
                
        except Exception as e:
            print(f"[ERROR] Server status update failed: {e}")
    
    def show_menu(self) -> None:
        """Show application menu"""
        # TODO: Implement dropdown menu with options
        self.show_snackbar("Menu functionality coming soon")
    
    def refresh_data(self) -> None:
        """Refresh all data displays"""
        try:
            # Force immediate update
            self.periodic_update(0)
            
            # Refresh current screen
            if self.screen_manager is not None:
                current_screen = self.screen_manager.current_screen
                if hasattr(current_screen, 'refresh_data'):
                    current_screen.refresh_data()
            
            self.show_snackbar("Data refreshed")
            
        except Exception as e:
            print(f"[ERROR] Data refresh failed: {e}")
            self.show_snackbar("Refresh failed")
    
    def toggle_theme(self) -> None:
        """Toggle between light and dark theme"""
        try:
            current_style = self.theme_cls.theme_style
            new_style = "Light" if current_style == "Dark" else "Dark"
            
            self.theme_cls.theme_style = new_style
            if self.theme_config:
                self.theme_config.update_theme(self.theme_config.current_theme, new_style)
            
            # Save configuration
            self.save_configuration()
            
            self.show_snackbar(f"Switched to {new_style} theme")
            
        except Exception as e:
            print(f"[ERROR] Theme toggle failed: {e}")
            self.show_snackbar("Theme change failed")
    
    def show_snackbar(self, message: str, duration: float = 3.0) -> None:
        """Show a snackbar notification"""
        try:
            snackbar = MDSnackbar(
                MDSnackbarText(text=message),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
                duration=duration
            )
            snackbar.open()
        except Exception as e:
            print(f"[ERROR] Snackbar failed: {e}")
            # Fallback to console
            print(f"[INFO] {message}")
    
    def show_startup_message(self) -> None:
        """Show startup message"""
        if self.server_bridge and hasattr(self.server_bridge, 'is_server_available') and self.server_bridge.is_server_available():
            self.show_snackbar("✅ Server connection established")
        else:
            self.show_snackbar("⚠️ Running in standalone mode")
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        config_path = Path(__file__).parent / "config.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[WARNING] Could not load config: {e}")
            # Return default configuration
            return {
                "app": {
                    "title": "Encrypted Backup Server",
                    "version": "2.0.0",
                    "theme": "Dark",
                    "primary_color": "Blue",
                    "material_style": "M3"
                },
                "ui": {
                    "auto_refresh_interval": 1.0
                }
            }
    
    def save_configuration(self) -> None:
        """Save configuration to JSON file"""
        config_path = Path(__file__).parent / "config.json"
        try:
            # Update current settings
            self.config_data["app"]["theme"] = self.theme_cls.theme_style
            self.config_data["app"]["primary_color"] = self.theme_cls.primary_palette
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Could not save config: {e}")
    
    def on_stop(self) -> None:
        """Clean up when application stops"""
        try:
            # Cancel scheduled updates
            if self.update_event:
                self.update_event.cancel()
            
            # Save configuration
            self.save_configuration()
            
            # Clean up server bridge
            if self.server_bridge:
                self.server_bridge.cleanup()
            
            print("[INFO] Application shutdown complete")
            
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")


def create_server_instance():
    """Create server instance if available"""
    if not SERVER_AVAILABLE:
        return None
    
    try:
        server = BackupServer()
        print("[INFO] BackupServer instance created")
        return server
    except Exception as e:
        print(f"[WARNING] Could not create server instance: {e}")
        return None


def main(server_instance: Optional[Any] = None):
    """Main entry point for the KivyMD application"""
    if not KIVYMD_AVAILABLE:
        print("[ERROR] KivyMD is not available. Please install it with: pip install git+https://github.com/kivymd/KivyMD.git@d2f7740")
        return
    
    print("[INFO] Starting KivyMD Encrypted Backup Server GUI...")
    
    # Initialize Sentry error tracking
    if SENTRY_AVAILABLE:
        try:
            init_sentry(component_name="kivymd-server-gui", debug=False)
            print("[INFO] Sentry error tracking enabled")
        except Exception as e:
            print(f"[WARNING] Sentry initialization failed: {e}")
    else:
        print("[INFO] Sentry error tracking disabled")
    
    try:
        # Create server instance if not provided
        if server_instance is None:
            server_instance = create_server_instance()
        
        # Create and run the app
        app = EncryptedBackupServerApp(server_instance=server_instance)
        app.run()
        
    except KeyboardInterrupt:
        print("\n[INFO] Application interrupted by user")
    except Exception as e:
        print(f"[ERROR] Application crashed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    # Command line argument handling
    import argparse
    
    parser = argparse.ArgumentParser(description="KivyMD Encrypted Backup Server GUI")
    parser.add_argument("--standalone", action="store_true", 
                       help="Run without server integration")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Run in standalone mode if requested
    server = None if args.standalone else create_server_instance()
    main(server_instance=server)