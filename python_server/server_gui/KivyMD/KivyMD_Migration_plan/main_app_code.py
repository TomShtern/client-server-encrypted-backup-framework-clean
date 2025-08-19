# -*- coding: utf-8 -*-
"""
ServerGUI_KivyMD.py - Material Design 3 GUI for Encrypted Backup Server
Main application entry point with KivyMD framework
"""

from __future__ import annotations
import os
import sys
import json
import threading
import queue
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Deque
from collections import deque
from pathlib import Path

# Kivy imports
from kivy.config import Config
Config.set('graphics', 'width', '1400')
Config.set('graphics', 'height', '900')

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.navigationrail import (
    MDNavigationRail,
    MDNavigationRailItem,
    MDNavigationRailMenuButton,
    MDNavigationRailFabButton,
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton, MDFabButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.list import MDList, ThreeLineListItem, IconLeftWidget
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.chip import MDChip
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.fitimage import FitImage
from kivymd.uix.segmentedcontrol import MDSegmentedControl, MDSegmentedControlItem
from kivymd.theming import ThemeManager

from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty, 
    ObjectProperty, ListProperty, DictProperty
)
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.scrollview import ScrollView

# Optional imports with fallbacks
try:
    import psutil
    SYSTEM_MONITOR_AVAILABLE = True
except ImportError:
    psutil = None
    SYSTEM_MONITOR_AVAILABLE = False

try:
    from kivy_garden.matplotlib import FigureCanvasKivyAgg
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    print("[INFO] kivy-garden.matplotlib not available. Charts will be disabled.")

# ============================================================================
# Custom Material Design 3 Components
# ============================================================================

class MDStatusCard(MDCard):
    """Material Design 3 Status Card with dynamic updates"""
    title = StringProperty("")
    icon = StringProperty("information")
    primary_text = StringProperty("")
    secondary_text = StringProperty("")
    status_color = StringProperty("green")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 1
        self.radius = dp(12)
        self.padding = dp(16)
        self.adaptive_height = True
        self._setup_layout()
        
    def _setup_layout(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(8))
        
        # Header with icon and title
        header = MDBoxLayout(size_hint_y=None, height=dp(40))
        icon = MDIconButton(
            icon=self.icon,
            theme_icon_color="Custom",
            icon_color=self.theme_cls.primaryColor,
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        title_label = MDLabel(
            text=self.title,
            font_style="Title",
            adaptive_height=True
        )
        header.add_widget(icon)
        header.add_widget(title_label)
        
        # Content
        content = MDBoxLayout(orientation="vertical", spacing=dp(4))
        self.primary_label = MDLabel(
            text=self.primary_text,
            font_style="Headline",
            theme_text_color="Primary",
            adaptive_height=True
        )
        self.secondary_label = MDLabel(
            text=self.secondary_text,
            font_style="Body",
            theme_text_color="Secondary",
            adaptive_height=True
        )
        content.add_widget(self.primary_label)
        content.add_widget(self.secondary_label)
        
        layout.add_widget(header)
        layout.add_widget(content)
        self.add_widget(layout)
    
    def update_status(self, primary: str, secondary: str = "", color: str = "green"):
        """Update the card's status display"""
        self.primary_label.text = primary
        self.secondary_label.text = secondary
        self.status_color = color
        
        # Animate the update
        anim = Animation(opacity=0.5, duration=0.1) + Animation(opacity=1, duration=0.1)
        anim.start(self)


class MDPerformanceChart(MDCard):
    """Material Design 3 Performance Chart using matplotlib"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 1
        self.radius = dp(12)
        self.padding = dp(16)
        
        if CHARTS_AVAILABLE:
            self._setup_chart()
        else:
            self.add_widget(MDLabel(
                text="Charts require kivy-garden.matplotlib",
                theme_text_color="Secondary",
                halign="center"
            ))
    
    def _setup_chart(self):
        """Setup matplotlib chart for performance monitoring"""
        self.figure = Figure(figsize=(5, 3), facecolor='none')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('none')
        
        # Style for Material Design
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#666666')
        self.ax.spines['bottom'].set_color('#666666')
        self.ax.tick_params(colors='#666666')
        
        # Initialize data
        self.cpu_data = deque(maxlen=60)
        self.mem_data = deque(maxlen=60)
        self.time_data = deque(maxlen=60)
        
        # Create lines
        self.cpu_line, = self.ax.plot([], [], color='#1976D2', linewidth=2, label='CPU %')
        self.mem_line, = self.ax.plot([], [], color='#7C4DFF', linewidth=2, label='Memory %')
        
        self.ax.set_ylim(0, 100)
        self.ax.set_ylabel('Usage (%)', color='#666666')
        self.ax.legend(loc='upper left', frameon=False)
        
        # Add canvas to card
        self.canvas_widget = FigureCanvasKivyAgg(self.figure)
        self.add_widget(self.canvas_widget)
        
        # Schedule updates
        Clock.schedule_interval(self.update_chart, 1.0)
    
    def update_chart(self, dt):
        """Update chart with current system metrics"""
        if not SYSTEM_MONITOR_AVAILABLE or not CHARTS_AVAILABLE:
            return
        
        now = time.time()
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        
        self.cpu_data.append(cpu)
        self.mem_data.append(mem)
        self.time_data.append(now)
        
        if len(self.time_data) > 1:
            # Convert time to relative seconds
            times = [t - self.time_data[0] for t in self.time_data]
            
            self.cpu_line.set_data(times, list(self.cpu_data))
            self.mem_line.set_data(times, list(self.mem_data))
            
            self.ax.set_xlim(0, max(times) if times else 60)
            self.ax.set_xlabel(f'Time (last {len(times)}s)', color='#666666')
            
            self.canvas_widget.draw()


# ============================================================================
# Screen Classes
# ============================================================================

class DashboardScreen(MDScreen):
    """Material Design 3 Dashboard Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "dashboard"
        self._build_ui()
    
    def _build_ui(self):
        """Build the dashboard UI"""
        layout = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(16))
        
        # Header
        header = MDBoxLayout(size_hint_y=None, height=dp(56))
        header.add_widget(MDLabel(
            text="Dashboard",
            font_style="Display",
            theme_text_color="Primary"
        ))
        header.add_widget(MDLabel(
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            font_style="Body",
            theme_text_color="Secondary",
            halign="right"
        ))
        layout.add_widget(header)
        
        # Status Cards Grid
        cards_layout = MDBoxLayout(orientation="horizontal", spacing=dp(16), size_hint_y=None, height=dp(200))
        
        # Server Status Card
        self.server_card = MDStatusCard(
            title="Server Status",
            icon="server",
            primary_text="Offline",
            secondary_text="Not running"
        )
        cards_layout.add_widget(self.server_card)
        
        # Client Stats Card
        self.client_card = MDStatusCard(
            title="Clients",
            icon="account-group",
            primary_text="0 Connected",
            secondary_text="0 Total registered"
        )
        cards_layout.add_widget(self.client_card)
        
        # Transfer Stats Card
        self.transfer_card = MDStatusCard(
            title="Transfers",
            icon="transfer",
            primary_text="0 MB",
            secondary_text="0 KB/s"
        )
        cards_layout.add_widget(self.transfer_card)
        
        layout.add_widget(cards_layout)
        
        # Performance Chart
        if CHARTS_AVAILABLE:
            self.performance_chart = MDPerformanceChart(size_hint_y=0.4)
            layout.add_widget(self.performance_chart)
        
        # Control Panel
        control_panel = MDCard(
            md_bg_color=self.theme_cls.surfaceVariantColor,
            elevation=1,
            radius=dp(12),
            padding=dp(16),
            size_hint_y=None,
            height=dp(120)
        )
        
        controls = MDBoxLayout(spacing=dp(16))
        
        # Control buttons with Material Design 3 styling
        self.start_btn = MDButton(
            MDButtonText(text="Start Server"),
            MDButtonIcon(icon="play"),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color="green",
            on_release=self.start_server
        )
        controls.add_widget(self.start_btn)
        
        self.stop_btn = MDButton(
            MDButtonText(text="Stop Server"),
            MDButtonIcon(icon="stop"),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color="red",
            on_release=self.stop_server,
            disabled=True
        )
        controls.add_widget(self.stop_btn)
        
        self.restart_btn = MDButton(
            MDButtonText(text="Restart"),
            MDButtonIcon(icon="restart"),
            style="tonal",
            on_release=self.restart_server
        )
        controls.add_widget(self.restart_btn)
        
        control_panel.add_widget(controls)
        layout.add_widget(control_panel)
        
        # Activity Log
        log_card = MDCard(
            md_bg_color=self.theme_cls.surfaceVariantColor,
            elevation=1,
            radius=dp(12),
            padding=dp(16)
        )
        
        log_header = MDLabel(text="Activity Log", font_style="Title", size_hint_y=None, height=dp(32))
        log_card.add_widget(log_header)
        
        self.activity_list = MDList()
        scroll = ScrollView()
        scroll.add_widget(self.activity_list)
        log_card.add_widget(scroll)
        
        layout.add_widget(log_card)
        
        self.add_widget(layout)
    
    def start_server(self, *args):
        """Start the backup server"""
        app = MDApp.get_running_app()
        if app.server_instance:
            threading.Thread(target=app.server_instance.start, daemon=True).start()
            self.add_log_entry("Server starting...", "information")
            self.start_btn.disabled = True
            self.stop_btn.disabled = False
    
    def stop_server(self, *args):
        """Stop the backup server"""
        app = MDApp.get_running_app()
        if app.server_instance:
            threading.Thread(target=app.server_instance.stop, daemon=True).start()
            self.add_log_entry("Server stopping...", "information")
            self.start_btn.disabled = False
            self.stop_btn.disabled = True
    
    def restart_server(self, *args):
        """Restart the backup server"""
        self.stop_server()
        Clock.schedule_once(lambda dt: self.start_server(), 2)
        self.add_log_entry("Server restarting...", "information")
    
    def add_log_entry(self, text: str, icon: str = "information"):
        """Add an entry to the activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        item = ThreeLineListItem(
            text=text,
            secondary_text=timestamp,
            tertiary_text=""
        )
        icon_widget = IconLeftWidget(icon=icon)
        item.add_widget(icon_widget)
        self.activity_list.add_widget(item, index=0)
        
        # Limit log entries
        if len(self.activity_list.children) > 50:
            self.activity_list.remove_widget(self.activity_list.children[-1])


class ClientsScreen(MDScreen):
    """Material Design 3 Clients Management Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "clients"
        self._build_ui()
    
    def _build_ui(self):
        """Build the clients UI"""
        layout = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(16))
        
        # Header with search
        header = MDBoxLayout(size_hint_y=None, height=dp(56))
        header.add_widget(MDLabel(
            text="Client Management",
            font_style="Display",
            theme_text_color="Primary"
        ))
        
        # Search field with Material You styling
        self.search_field = MDTextField(
            MDTextFieldLeadingIcon(icon="magnify"),
            MDTextFieldHintText(text="Search clients..."),
            mode="outlined",
            size_hint_x=0.3
        )
        header.add_widget(self.search_field)
        
        layout.add_widget(header)
        
        # Filter chips
        chips_layout = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(48))
        chips_layout.add_widget(MDChip(
            MDChipText(text="All"),
            type="filter",
            active=True
        ))
        chips_layout.add_widget(MDChip(
            MDChipText(text="Online"),
            type="filter"
        ))
        chips_layout.add_widget(MDChip(
            MDChipText(text="Offline"),
            type="filter"
        ))
        layout.add_widget(chips_layout)
        
        # Data table with Material Design 3
        self.clients_table = MDDataTable(
            size_hint=(1, 1),
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("Status", dp(30)),
                ("Client Name", dp(40)),
                ("Client ID", dp(60)),
                ("IP Address", dp(40)),
                ("Last Seen", dp(40)),
                ("Files", dp(30)),
                ("Actions", dp(30))
            ],
            row_data=[],
            sorted_on="Client Name",
            sorted_order="ASC",
            elevation=2,
            background_color_header=self.theme_cls.primaryColor,
            background_color_cell=self.theme_cls.surfaceColor,
            background_color_selected_cell=self.theme_cls.primaryContainer
        )
        
        # Bind row press event
        self.clients_table.bind(on_row_press=self.on_client_selected)
        
        layout.add_widget(self.clients_table)
        
        # FAB for adding clients
        fab = MDFabButton(
            icon="plus",
            pos_hint={"right": 0.95, "bottom": 0.05},
            on_release=self.add_client_dialog
        )
        layout.add_widget(fab)
        
        self.add_widget(layout)
    
    def on_client_selected(self, instance_table, instance_row):
        """Handle client selection"""
        # Show client details in a bottom sheet or dialog
        client_data = instance_row.text
        self.show_client_details(client_data)
    
    def show_client_details(self, client_data):
        """Show detailed client information"""
        # Implement client details dialog
        pass
    
    def add_client_dialog(self, *args):
        """Show dialog to add a new client"""
        # Implement add client dialog
        pass


class SettingsScreen(MDScreen):
    """Material Design 3 Settings Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self._build_ui()
    
    def _build_ui(self):
        """Build the settings UI"""
        layout = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(16))
        
        # Header
        header = MDLabel(
            text="Settings",
            font_style="Display",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(56)
        )
        layout.add_widget(header)
        
        # Settings sections with cards
        scroll = ScrollView()
        settings_layout = MDBoxLayout(orientation="vertical", spacing=dp(16), adaptive_height=True)
        
        # Server Settings Card
        server_card = MDCard(
            md_bg_color=self.theme_cls.surfaceVariantColor,
            elevation=1,
            radius=dp(12),
            padding=dp(16),
            adaptive_height=True
        )
        
        server_layout = MDBoxLayout(orientation="vertical", spacing=dp(12), adaptive_height=True)
        server_layout.add_widget(MDLabel(
            text="Server Configuration",
            font_style="Title",
            theme_text_color="Primary",
            adaptive_height=True
        ))
        
        # Port setting
        port_field = MDTextField(
            MDTextFieldLeadingIcon(icon="ethernet-cable"),
            MDTextFieldHintText(text="Server Port"),
            MDTextFieldHelperText(text="Default: 1256", mode="persistent"),
            text="1256",
            mode="outlined"
        )
        server_layout.add_widget(port_field)
        
        # Storage directory
        storage_field = MDTextField(
            MDTextFieldLeadingIcon(icon="folder"),
            MDTextFieldHintText(text="Storage Directory"),
            MDTextFieldTrailingIcon(icon="folder-open"),
            text="received_files",
            mode="outlined"
        )
        server_layout.add_widget(storage_field)
        
        # Max clients
        max_clients_field = MDTextField(
            MDTextFieldLeadingIcon(icon="account-multiple"),
            MDTextFieldHintText(text="Maximum Clients"),
            text="50",
            mode="outlined"
        )
        server_layout.add_widget(max_clients_field)
        
        server_card.add_widget(server_layout)
        settings_layout.add_widget(server_card)
        
        # Appearance Settings Card
        appearance_card = MDCard(
            md_bg_color=self.theme_cls.surfaceVariantColor,
            elevation=1,
            radius=dp(12),
            padding=dp(16),
            adaptive_height=True
        )
        
        appearance_layout = MDBoxLayout(orientation="vertical", spacing=dp(12), adaptive_height=True)
        appearance_layout.add_widget(MDLabel(
            text="Appearance",
            font_style="Title",
            theme_text_color="Primary",
            adaptive_height=True
        ))
        
        # Theme selector
        theme_layout = MDBoxLayout(size_hint_y=None, height=dp(48))
        theme_layout.add_widget(MDLabel(
            text="Theme Mode",
            theme_text_color="Primary"
        ))
        theme_switch = MDSwitch(
            active=MDApp.get_running_app().theme_cls.theme_style == "Dark"
        )
        theme_switch.bind(active=self.toggle_theme)
        theme_layout.add_widget(theme_switch)
        appearance_layout.add_widget(theme_layout)
        
        # Primary color selector using segmented control
        color_selector = MDSegmentedControl(
            MDSegmentedControlItem(text="Blue"),
            MDSegmentedControlItem(text="Green"),
            MDSegmentedControlItem(text="Purple"),
            size_hint_y=None,
            height=dp(48)
        )
        appearance_layout.add_widget(color_selector)
        
        appearance_card.add_widget(appearance_layout)
        settings_layout.add_widget(appearance_card)
        
        scroll.add_widget(settings_layout)
        layout.add_widget(scroll)
        
        # Save button
        save_btn = MDButton(
            MDButtonText(text="Save Settings"),
            MDButtonIcon(icon="content-save"),
            style="filled",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.3,
            on_release=self.save_settings
        )
        layout.add_widget(save_btn)
        
        self.add_widget(layout)
    
    def toggle_theme(self, switch, value):
        """Toggle between light and dark theme"""
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = "Dark" if value else "Light"
    
    def save_settings(self, *args):
        """Save settings to file"""
        # Implement settings save logic
        MDSnackbar(
            MDSnackbarText(text="Settings saved successfully!"),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.5,
            duration=2
        ).open()


# ============================================================================
# Main Application
# ============================================================================

class EncryptedBackupServerApp(MDApp):
    """Main KivyMD Application with Material Design 3"""
    
    def __init__(self, server_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.server_instance = server_instance
        self.title = "Encrypted Backup Server"
        self.icon = "assets/icon.png"  # Add your icon
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.material_style = "M3"
        
        # State management
        self.update_queue = queue.Queue()
        self.settings = self.load_settings()
    
    def build(self):
        """Build the application UI"""
        # Main layout
        main_layout = MDBoxLayout(orientation="horizontal")
        
        # Navigation Rail (Material Design 3)
        self.nav_rail = MDNavigationRail(
            MDNavigationRailMenuButton(
                icon="menu",
                on_release=self.open_menu
            ),
            MDNavigationRailFabButton(
                icon="plus",
                on_release=self.quick_action
            ),
            MDNavigationRailItem(
                icon="view-dashboard",
                text="Dashboard",
                on_release=lambda x: self.switch_screen("dashboard")
            ),
            MDNavigationRailItem(
                icon="account-group",
                text="Clients",
                on_release=lambda x: self.switch_screen("clients")
            ),
            MDNavigationRailItem(
                icon="folder",
                text="Files",
                on_release=lambda x: self.switch_screen("files")
            ),
            MDNavigationRailItem(
                icon="chart-line",
                text="Analytics",
                on_release=lambda x: self.switch_screen("analytics")
            ),
            MDNavigationRailItem(
                icon="database",
                text="Database",
                on_release=lambda x: self.switch_screen("database")
            ),
            MDNavigationRailItem(
                icon="text-box-multiple",
                text="Logs",
                on_release=lambda x: self.switch_screen("logs")
            ),
            MDNavigationRailItem(
                icon="cog",
                text="Settings",
                on_release=lambda x: self.switch_screen("settings")
            ),
            anchor="top",
            color_normal=self.theme_cls.onSurfaceVariantColor,
            color_active=self.theme_cls.primaryColor,
            use_hover_behavior=True,
            hover_bg=self.theme_cls.primaryContainer
        )
        
        main_layout.add_widget(self.nav_rail)
        
        # Screen Manager
        self.screen_manager = MDScreenManager()
        
        # Add screens
        self.screen_manager.add_widget(DashboardScreen())
        self.screen_manager.add_widget(ClientsScreen())
        self.screen_manager.add_widget(SettingsScreen())
        # Add other screens as they're implemented
        
        main_layout.add_widget(self.screen_manager)
        
        # Schedule periodic updates
        Clock.schedule_interval(self.process_updates, 1.0)
        
        return main_layout
    
    def switch_screen(self, screen_name: str):
        """Switch to a different screen with animation"""
        if screen_name in self.screen_manager.screen_names:
            self.screen_manager.transition.direction = "left"
            self.screen_manager.current = screen_name
            
            # Update navigation rail selection
            for item in self.nav_rail.children:
                if isinstance(item, MDNavigationRailItem):
                    if item.text.lower() == screen_name:
                        item.active = True
                    else:
                        item.active = False
    
    def open_menu(self, *args):
        """Open navigation menu"""
        menu_items = [
            {
                "text": "About",
                "leading_icon": "information",
                "on_release": lambda x: self.show_about_dialog()
            },
            {
                "text": "Help",
                "leading_icon": "help",
                "on_release": lambda x: self.show_help()
            },
            {
                "text": "Exit",
                "leading_icon": "exit-to-app",
                "on_release": lambda x: self.stop()
            }
        ]
        
        self.menu = MDDropdownMenu(
            caller=self.nav_rail.children[-1],
            items=menu_items,
            width_mult=3
        )
        self.menu.open()
    
    def quick_action(self, *args):
        """Handle FAB quick action"""
        # Show quick actions menu
        pass
    
    def process_updates(self, dt):
        """Process update queue from server"""
        while not self.update_queue.empty():
            try:
                update = self.update_queue.get_nowait()
                self.handle_update(update)
            except queue.Empty:
                break
    
    def handle_update(self, update: Dict[str, Any]):
        """Handle server updates"""
        update_type = update.get("type")
        data = update.get("data", {})
        
        # Route to appropriate handler
        if update_type == "server_status":
            self.update_server_status(data)
        elif update_type == "client_stats":
            self.update_client_stats(data)
        elif update_type == "log":
            self.add_log_entry(data.get("message", ""))
    
    def update_server_status(self, data: Dict[str, Any]):
        """Update server status in dashboard"""
        if self.screen_manager.current == "dashboard":
            dashboard = self.screen_manager.get_screen("dashboard")
            status = "Online" if data.get("running") else "Offline"
            dashboard.server_card.update_status(
                status,
                f"Port: {data.get('port', 'N/A')}",
                "green" if data.get("running") else "red"
            )
    
    def update_client_stats(self, data: Dict[str, Any]):
        """Update client statistics"""
        if self.screen_manager.current == "dashboard":
            dashboard = self.screen_manager.get_screen("dashboard")
            dashboard.client_card.update_status(
                f"{data.get('connected', 0)} Connected",
                f"{data.get('total', 0)} Total registered"
            )
    
    def add_log_entry(self, message: str):
        """Add entry to activity log"""
        if self.screen_manager.current == "dashboard":
            dashboard = self.screen_manager.get_screen("dashboard")
            dashboard.add_log_entry(message)
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        defaults = {
            "port": 1256,
            "storage_dir": "received_files",
            "max_clients": 50,
            "theme": "Dark",
            "primary_color": "Blue"
        }
        
        try:
            with open("kivymd_settings.json", "r") as f:
                settings = json.load(f)
                return {**defaults, **settings}
        except (FileNotFoundError, json.JSONDecodeError):
            return defaults
    
    def save_settings(self, settings: Dict[str, Any]):
        """Save settings to file"""
        with open("kivymd_settings.json", "w") as f:
            json.dump(settings, f, indent=4)
    
    def show_about_dialog(self):
        """Show about dialog"""
        dialog = MDDialog(
            MDDialogHeadline(text="About"),
            MDDialogSupportingText(
                text="Encrypted Backup Server v2.0\n"
                     "Built with KivyMD and Material Design 3\n\n"
                     "A modern, secure backup solution."
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Close"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                )
            )
        )
        dialog.open()
    
    def show_help(self):
        """Show help documentation"""
        # Implement help viewer
        pass
    
    def on_stop(self):
        """Clean up when app stops"""
        if self.server_instance and hasattr(self.server_instance, 'running'):
            if self.server_instance.running:
                self.server_instance.stop()


# ============================================================================
# Entry Point
# ============================================================================

def main(server_instance=None):
    """Main entry point for the KivyMD application"""
    app = EncryptedBackupServerApp(server_instance=server_instance)
    app.run()


if __name__ == "__main__":
    # For standalone testing
    print("[INFO] Starting KivyMD GUI in standalone mode...")
    main()