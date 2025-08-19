# -*- coding: utf-8 -*-
"""
Dashboard screen for the KivyMD Encrypted Backup Server GUI

This screen provides a comprehensive overview of server status, controls,
statistics, and activity monitoring with Material Design 3 styling.
"""

from __future__ import annotations
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

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
    from kivymd.uix.progressbar import MDProgressBar
    from kivymd.uix.list import MDList, MDListItem
    from kivymd.uix.list import MDListItemHeadlineText, MDListItemSupportingText
    from kivymd.uix.badge import MDBadge
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
    from ..utils.server_integration import ServerStatus, ServerIntegrationBridge
    from ..models.data_models import ServerStats


class ServerStatusCard(MDCard):
    """Card widget displaying server status information"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(180)
        
        # Create layout
        layout = MDBoxLayout(orientation="vertical", spacing=dp(8))
        
        # Header with title and status indicator
        header_layout = MDBoxLayout(
            orientation="horizontal", 
            adaptive_height=True,
            spacing=dp(12)
        )
        
        self.title_label = MDLabel(
            text="Server Status",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        header_layout.add_widget(self.title_label)
        
        # Status badge
        self.status_badge = MDBadge(
            text="OFFLINE",
            md_bg_color=self.theme_cls.errorColor,
            size_hint=(None, None),
            size=(dp(80), dp(24))
        )
        header_layout.add_widget(self.status_badge)
        
        layout.add_widget(header_layout)
        layout.add_widget(MDDivider())
        
        # Server information grid
        info_grid = MDGridLayout(cols=2, spacing=dp(8), adaptive_height=True)
        
        # Left column
        left_col = MDBoxLayout(orientation="vertical", spacing=dp(4))
        
        self.port_label = MDLabel(
            text="Port: 1256",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        left_col.add_widget(self.port_label)
        
        self.uptime_label = MDLabel(
            text="Uptime: 00:00:00",
            theme_text_color="Secondary", 
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        left_col.add_widget(self.uptime_label)
        
        self.clients_label = MDLabel(
            text="Active Clients: 0",
            theme_text_color="Secondary",
            font_style="Body", 
            size_hint_y=None,
            height=dp(20)
        )
        left_col.add_widget(self.clients_label)
        
        info_grid.add_widget(left_col)
        
        # Right column  
        right_col = MDBoxLayout(orientation="vertical", spacing=dp(4))
        
        self.host_label = MDLabel(
            text="Host: localhost",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        right_col.add_widget(self.host_label)
        
        self.files_label = MDLabel(
            text="Files: 0",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None, 
            height=dp(20)
        )
        right_col.add_widget(self.files_label)
        
        self.bytes_label = MDLabel(
            text="Data: 0 bytes",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(20)
        )
        right_col.add_widget(self.bytes_label)
        
        info_grid.add_widget(right_col)
        layout.add_widget(info_grid)
        
        self.add_widget(layout)
    
    def update_status(self, status: ServerStatus):
        """Update the card with new server status"""
        try:
            # Update status badge
            if status.running:
                self.status_badge.text = "ONLINE"
                self.status_badge.md_bg_color = self.theme_cls.primaryColor
            else:
                self.status_badge.text = "OFFLINE"
                self.status_badge.md_bg_color = self.theme_cls.errorColor
            
            # Update information
            self.port_label.text = f"Port: {status.port}"
            self.host_label.text = f"Host: {status.host}"
            self.clients_label.text = f"Active Clients: {status.client_count}"
            self.files_label.text = f"Files: {status.total_files}"
            
            # Format uptime
            if status.uptime_seconds > 0:
                hours = int(status.uptime_seconds // 3600)
                minutes = int((status.uptime_seconds % 3600) // 60)
                seconds = int(status.uptime_seconds % 60)
                self.uptime_label.text = f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                self.uptime_label.text = "Uptime: 00:00:00"
            
            # Format bytes
            if status.bytes_transferred > 0:
                if status.bytes_transferred < 1024:
                    self.bytes_label.text = f"Data: {status.bytes_transferred} bytes"
                elif status.bytes_transferred < 1024**2:
                    self.bytes_label.text = f"Data: {status.bytes_transferred/1024:.1f} KB"
                elif status.bytes_transferred < 1024**3:
                    self.bytes_label.text = f"Data: {status.bytes_transferred/(1024**2):.1f} MB"
                else:
                    self.bytes_label.text = f"Data: {status.bytes_transferred/(1024**3):.2f} GB"
            else:
                self.bytes_label.text = "Data: 0 bytes"
                
        except Exception as e:
            print(f"[ERROR] Failed to update status card: {e}")


class ServerControlCard(MDCard):
    """Card widget with server control buttons"""
    
    def __init__(self, dashboard_screen, **kwargs):
        super().__init__(**kwargs)
        self.dashboard_screen = dashboard_screen
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(120)
        
        # Create layout
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Title
        title_label = MDLabel(
            text="Server Control",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title_label)
        layout.add_widget(MDDivider())
        
        # Control buttons
        button_layout = MDBoxLayout(orientation="horizontal", spacing=dp(12))
        
        self.start_button = MDButton(
            MDButtonText(text="START"),
            on_release=self.on_start_server
        )
        self.start_button.theme_bg_color = "Custom"
        self.start_button.md_bg_color = self.theme_cls.primaryColor
        button_layout.add_widget(self.start_button)
        
        self.stop_button = MDButton(
            MDButtonText(text="STOP"),
            on_release=self.on_stop_server
        )
        self.stop_button.theme_bg_color = "Custom"
        self.stop_button.md_bg_color = self.theme_cls.errorColor
        button_layout.add_widget(self.stop_button)
        
        self.restart_button = MDButton(
            MDButtonText(text="RESTART"),
            on_release=self.on_restart_server
        )
        self.restart_button.theme_bg_color = "Custom"
        self.restart_button.md_bg_color = self.theme_cls.tertiaryColor
        button_layout.add_widget(self.restart_button)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
        
        # Initial button state
        self.update_button_states(False)
    
    def update_button_states(self, server_running: bool):
        """Update button enabled states based on server status"""
        try:
            self.start_button.disabled = server_running
            self.stop_button.disabled = not server_running  
            self.restart_button.disabled = not server_running
        except Exception as e:
            print(f"[ERROR] Failed to update button states: {e}")
    
    def on_start_server(self, *args):
        """Handle start server button press"""
        try:
            self.dashboard_screen.start_server()
        except Exception as e:
            print(f"[ERROR] Start server failed: {e}")
    
    def on_stop_server(self, *args):
        """Handle stop server button press"""
        try:
            self.dashboard_screen.stop_server()
        except Exception as e:
            print(f"[ERROR] Stop server failed: {e}")
    
    def on_restart_server(self, *args):
        """Handle restart server button press"""
        try:
            self.dashboard_screen.restart_server()
        except Exception as e:
            print(f"[ERROR] Restart server failed: {e}")


class ActivityLogCard(MDCard):
    """Card widget showing activity log"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.padding = dp(16)
        
        # Create layout
        layout = MDBoxLayout(orientation="vertical", spacing=dp(8))
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, 
            height=dp(32),
            spacing=dp(8)
        )
        
        title_label = MDLabel(
            text="Activity Log",
            theme_text_color="Primary",
            font_style="Headline"
        )
        header_layout.add_widget(title_label)
        
        # Clear button
        clear_button = MDIconButton(
            icon="delete",
            on_release=self.clear_log
        )
        clear_button.size_hint = (None, None)
        clear_button.size = (dp(32), dp(32))
        header_layout.add_widget(clear_button)
        
        layout.add_widget(header_layout)
        layout.add_widget(MDDivider())
        
        # Scrollable log list
        scroll = MDScrollView()
        self.log_list = MDList()
        scroll.add_widget(self.log_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
        # Add initial message
        self.add_log_entry("System", "Dashboard initialized")
    
    def add_log_entry(self, source: str, message: str, level: str = "INFO"):
        """Add a new log entry"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Create list item
            item = MDListItem(
                MDListItemHeadlineText(text=f"[{timestamp}] {source}"),
                MDListItemSupportingText(text=message)
            )
            
            # Color coding by level
            if level == "ERROR":
                item.theme_text_color = "Custom"
                item.text_color = self.theme_cls.errorColor
            elif level == "WARNING":
                item.theme_text_color = "Custom"
                item.text_color = self.theme_cls.tertiaryColor
            else:
                item.theme_text_color = "Primary"
            
            self.log_list.add_widget(item, index=0)  # Add to top
            
            # Keep only last 50 entries
            if len(self.log_list.children) > 50:
                self.log_list.remove_widget(self.log_list.children[-1])
                
        except Exception as e:
            print(f"[ERROR] Failed to add log entry: {e}")
    
    def clear_log(self, *args):
        """Clear all log entries"""
        try:
            self.log_list.clear_widgets()
            self.add_log_entry("System", "Log cleared")
        except Exception as e:
            print(f"[ERROR] Failed to clear log: {e}")


class DashboardScreen(MDScreen):
    """
    Main dashboard screen showing comprehensive server overview
    
    Features:
    - Real-time server status monitoring
    - Server control buttons (start/stop/restart)
    - Statistics display
    - Activity logging
    - Auto-refresh capabilities
    """
    
    def __init__(self, server_bridge: Optional[ServerIntegrationBridge] = None,
                 config: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        
        # Store references
        self.server_bridge = server_bridge
        self.config = config or {}
        
        # UI components
        self.status_card: Optional[ServerStatusCard] = None
        self.control_card: Optional[ServerControlCard] = None
        self.activity_card: Optional[ActivityLogCard] = None
        
        # State tracking
        self.last_status: Optional[ServerStatus] = None
        self.update_event = None
        
        # Build UI
        self.build_ui()
        
        # Schedule initial data load
        Clock.schedule_once(self.initial_data_load, 0.5)
    
    def build_ui(self):
        """Build the dashboard UI"""
        try:
            # Main scroll layout
            scroll = MDScrollView()
            main_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(16),
                padding=dp(16),
                adaptive_height=True
            )
            
            # Status overview section
            status_section = MDBoxLayout(
                orientation="horizontal", 
                spacing=dp(16),
                size_hint_y=None,
                height=dp(180)
            )
            
            # Server status card
            self.status_card = ServerStatusCard()
            self.status_card.size_hint_x = 0.6
            status_section.add_widget(self.status_card)
            
            # Control card
            self.control_card = ServerControlCard(self)
            self.control_card.size_hint_x = 0.4
            status_section.add_widget(self.control_card)
            
            main_layout.add_widget(status_section)
            
            # Activity log section
            self.activity_card = ActivityLogCard()
            main_layout.add_widget(self.activity_card)
            
            scroll.add_widget(main_layout)
            self.add_widget(scroll)
            
        except Exception as e:
            print(f"[ERROR] Failed to build dashboard UI: {e}")
            traceback.print_exc()
            
            # Fallback UI
            error_layout = MDBoxLayout(orientation="vertical", padding=dp(16))
            error_label = MDLabel(
                text=f"Failed to load dashboard: {e}",
                theme_text_color="Error",
                halign="center"
            )
            error_layout.add_widget(error_label)
            self.add_widget(error_layout)
    
    def on_enter(self):
        """Called when the screen is entered"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Dashboard entered")
            
            # Start periodic updates
            self.schedule_updates()
            
            # Refresh data immediately
            self.refresh_data()
            
        except Exception as e:
            print(f"[ERROR] Dashboard on_enter failed: {e}")
    
    def on_leave(self):
        """Called when the screen is left"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Dashboard left")
            
            # Stop periodic updates
            self.stop_updates()
            
        except Exception as e:
            print(f"[ERROR] Dashboard on_leave failed: {e}")
    
    def schedule_updates(self):
        """Schedule periodic updates"""
        try:
            self.stop_updates()  # Stop any existing updates
            
            update_interval = self.config.get("ui", {}).get("auto_refresh_interval", 2.0)
            self.update_event = Clock.schedule_interval(self.periodic_update, update_interval)
            
        except Exception as e:
            print(f"[ERROR] Failed to schedule updates: {e}")
    
    def stop_updates(self):
        """Stop periodic updates"""
        try:
            if self.update_event:
                self.update_event.cancel()
                self.update_event = None
        except Exception as e:
            print(f"[ERROR] Failed to stop updates: {e}")
    
    def initial_data_load(self, dt):
        """Perform initial data loading"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Loading initial data...")
            
            self.refresh_data()
            
        except Exception as e:
            print(f"[ERROR] Initial data load failed: {e}")
            if self.activity_card:
                self.activity_card.add_log_entry("System", f"Initial load failed: {e}", "ERROR")
    
    def periodic_update(self, dt):
        """Perform periodic updates"""
        try:
            # Get latest server status
            if self.server_bridge:
                latest_status = self.server_bridge.get_latest_status()
                if latest_status:
                    self.on_server_status_update(latest_status)
            
        except Exception as e:
            print(f"[ERROR] Periodic update failed: {e}")
    
    def refresh_data(self):
        """Refresh all dashboard data"""
        try:
            if not self.server_bridge:
                if self.activity_card:
                    self.activity_card.add_log_entry("System", "No server bridge available", "WARNING")
                return
            
            # Get server information
            server_info = self.server_bridge.get_server_info()
            
            # Create status object
            status = ServerStatus(
                running=server_info.get('running', False),
                port=server_info.get('port', 1256),
                host=server_info.get('host', 'localhost'),
                uptime_seconds=server_info.get('uptime_seconds', 0),
                client_count=server_info.get('client_count', 0)
            )
            
            # Update UI
            self.on_server_status_update(status)
            
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Data refreshed")
            
        except Exception as e:
            print(f"[ERROR] Data refresh failed: {e}")
            if self.activity_card:
                self.activity_card.add_log_entry("System", f"Refresh failed: {e}", "ERROR")
    
    def on_server_status_update(self, status: ServerStatus):
        """Handle server status updates"""
        try:
            # Update status card
            if self.status_card:
                self.status_card.update_status(status)
            
            # Update control buttons
            if self.control_card:
                self.control_card.update_button_states(status.running)
            
            # Log status changes
            if self.last_status is None or self.last_status.running != status.running:
                if self.activity_card:
                    status_msg = "Server started" if status.running else "Server stopped" 
                    self.activity_card.add_log_entry("Server", status_msg)
            
            self.last_status = status
            
        except Exception as e:
            print(f"[ERROR] Status update failed: {e}")
    
    def start_server(self):
        """Start the backup server"""
        try:
            if not self.server_bridge:
                if self.activity_card:
                    self.activity_card.add_log_entry("System", "No server bridge available", "ERROR")
                return
            
            if self.activity_card:
                self.activity_card.add_log_entry("User", "Starting server...")
            
            # Use async method to avoid blocking UI
            self.server_bridge.start_server_async()
            
            # Check for response after a short delay
            Clock.schedule_once(self.check_server_command_response, 2.0)
            
        except Exception as e:
            print(f"[ERROR] Start server failed: {e}")
            if self.activity_card:
                self.activity_card.add_log_entry("System", f"Start failed: {e}", "ERROR")
    
    def stop_server(self):
        """Stop the backup server"""
        try:
            if not self.server_bridge:
                if self.activity_card:
                    self.activity_card.add_log_entry("System", "No server bridge available", "ERROR")
                return
            
            if self.activity_card:
                self.activity_card.add_log_entry("User", "Stopping server...")
            
            # Use async method to avoid blocking UI
            self.server_bridge.stop_server_async()
            
            # Check for response after a short delay
            Clock.schedule_once(self.check_server_command_response, 2.0)
            
        except Exception as e:
            print(f"[ERROR] Stop server failed: {e}")
            if self.activity_card:
                self.activity_card.add_log_entry("System", f"Stop failed: {e}", "ERROR")
    
    def restart_server(self):
        """Restart the backup server"""
        try:
            if not self.server_bridge:
                if self.activity_card:
                    self.activity_card.add_log_entry("System", "No server bridge available", "ERROR") 
                return
            
            if self.activity_card:
                self.activity_card.add_log_entry("User", "Restarting server...")
            
            # Use async method to avoid blocking UI
            self.server_bridge.restart_server_async()
            
            # Check for response after a longer delay for restart
            Clock.schedule_once(self.check_server_command_response, 5.0)
            
        except Exception as e:
            print(f"[ERROR] Restart server failed: {e}")
            if self.activity_card:
                self.activity_card.add_log_entry("System", f"Restart failed: {e}", "ERROR")
    
    def check_server_command_response(self, dt):
        """Check for server command response"""
        try:
            if not self.server_bridge:
                return
            
            response = self.server_bridge.get_command_response()
            if response:
                command = response.get('command', 'unknown')
                success = response.get('success', False)
                message = response.get('message', 'No message')
                
                if self.activity_card:
                    level = "INFO" if success else "ERROR"
                    self.activity_card.add_log_entry("Server", f"{command}: {message}", level)
            
        except Exception as e:
            print(f"[ERROR] Command response check failed: {e}")