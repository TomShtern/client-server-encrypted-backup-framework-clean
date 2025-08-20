# -*- coding: utf-8 -*-
"""
Enhanced Dashboard screen for the KivyMD Encrypted Backup Server GUI

Comprehensive server monitoring dashboard with Material Design 3 styling featuring:
- 6-card grid layout with server status, client stats, transfer monitoring
- Live performance charts with real-time CPU/Memory tracking  
- Professional control panel with colorful action buttons
- Activity logging with proper text constraints and scrolling
"""

from __future__ import annotations
import sys
import os
from pathlib import Path

# Ensure UTF-8 solution is available
try:
    import Shared.utils.utf8_solution
except ImportError:
    # Try adding project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    try:
        import Shared.utils.utf8_solution
    except ImportError:
        pass  # Continue without UTF-8 solution

import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import psutil

# Import deque separately to avoid potential import issues
try:
    from collections import deque
    DEQUE_AVAILABLE = True
except ImportError:
    DEQUE_AVAILABLE = False
    # Fallback implementation
    class deque:
        def __init__(self, iterable=None, maxlen=None):
            self.data = list(iterable) if iterable else []
            self.maxlen = maxlen
        
        def append(self, item):
            self.data.append(item)
            if self.maxlen and len(self.data) > self.maxlen:
                self.data.pop(0)
        
        def __len__(self):
            return len(self.data)
        
        def __iter__(self):
            return iter(self.data)

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
    from kivymd.uix.progressindicator import MDCircularProgressIndicator
    from kivymd.uix.list import MDList, MDListItem
    from kivymd.uix.list import MDListItemHeadlineText, MDListItemSupportingText
    from kivymd.uix.badge import MDBadge
    from kivymd.uix.tooltip import MDTooltip
    
    from kivy.clock import Clock
    from kivy.metrics import dp
    from kivy.core.window import Window
    from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    
    KIVYMD_AVAILABLE = True
    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    print(f"[ERROR] KivyMD/Matplotlib not available: {e}")
    KIVYMD_AVAILABLE = False
    MATPLOTLIB_AVAILABLE = False

# Local imports
if KIVYMD_AVAILABLE:
    from ..utils.server_integration import ServerStatus, ServerIntegrationBridge
    from ..models.data_models import ServerStats


class ServerStatusCard(MDCard):
    """Enhanced server status card with comprehensive monitoring"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceContainerColor
        self.elevation = 2
        self.radius = [16]  # MD3 elevated card radius
        self.padding = dp(20)
        self.size_hint_y = None
        self.height = dp(160)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header with status badge
        header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))
        
        title = MDLabel(
            text="Server Status",
            theme_text_color="Primary",
            font_style="Headline",
            adaptive_height=True
        )
        header.add_widget(title)
        
        self.status_badge = MDBadge(
            text="OFFLINE",
            md_bg_color=self.theme_cls.errorColor,
            size_hint=(None, None),
            size=(dp(70), dp(24))
        )
        header.add_widget(self.status_badge)
        
        layout.add_widget(header)
        layout.add_widget(MDDivider())
        
        # Status information
        info_grid = MDGridLayout(cols=2, spacing=dp(8), adaptive_height=True)
        
        # Status details
        self.status_label = MDLabel(text="Status: Stopped", font_style="Body", theme_text_color="Secondary")
        self.address_label = MDLabel(text="Address: N/A", font_style="Body", theme_text_color="Secondary")
        self.uptime_label = MDLabel(text="Uptime: 00:00:00", font_style="Body", theme_text_color="Secondary")
        
        info_grid.add_widget(self.status_label)
        info_grid.add_widget(self.address_label)
        info_grid.add_widget(self.uptime_label)
        info_grid.add_widget(MDLabel())  # Spacer
        
        layout.add_widget(info_grid)
        self.add_widget(layout)
    
    def update_status(self, status: ServerStatus):
        """Update server status display"""
        try:
            if status.running:
                self.status_badge.text = "ONLINE"
                self.status_badge.md_bg_color = self.theme_cls.primaryColor
                self.status_label.text = "Status: Running"
                self.address_label.text = f"Address: {status.host}:{status.port}"
            else:
                self.status_badge.text = "OFFLINE"
                self.status_badge.md_bg_color = self.theme_cls.errorColor
                self.status_label.text = "Status: Stopped"
                self.address_label.text = "Address: N/A"
            
            # Format uptime
            if status.uptime_seconds > 0:
                hours = int(status.uptime_seconds // 3600)
                minutes = int((status.uptime_seconds % 3600) // 60)
                seconds = int(status.uptime_seconds % 60)
                self.uptime_label.text = f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                self.uptime_label.text = "Uptime: 00:00:00"
                
        except Exception as e:
            print(f"[ERROR] Failed to update server status: {e}")


class ClientStatsCard(MDCard):
    """Client statistics monitoring card"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceContainerColor
        self.elevation = 2
        self.radius = [16]
        self.padding = dp(20)
        self.size_hint_y = None
        self.height = dp(160)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header
        title = MDLabel(
            text="Client Stats",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title)
        layout.add_widget(MDDivider())
        
        # Stats grid
        stats_grid = MDGridLayout(cols=2, spacing=dp(8), adaptive_height=True)
        
        self.connected_label = MDLabel(text="Connected: 0", font_style="Body", theme_text_color="Secondary")
        self.total_label = MDLabel(text="Total: 0", font_style="Body", theme_text_color="Secondary")
        self.transfers_label = MDLabel(text="Active Transfers: 0", font_style="Body", theme_text_color="Secondary")
        
        stats_grid.add_widget(self.connected_label)
        stats_grid.add_widget(self.total_label)
        stats_grid.add_widget(self.transfers_label)
        stats_grid.add_widget(MDLabel())  # Spacer
        
        layout.add_widget(stats_grid)
        self.add_widget(layout)
    
    def update_stats(self, connected: int = 0, total: int = 0, active_transfers: int = 0):
        """Update client statistics"""
        try:
            self.connected_label.text = f"Connected: {connected}"
            self.total_label.text = f"Total: {total}"
            self.transfers_label.text = f"Active Transfers: {active_transfers}"
        except Exception as e:
            print(f"[ERROR] Failed to update client stats: {e}")


class TransferStatsCard(MDCard):
    """Transfer statistics monitoring card"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceContainerColor
        self.elevation = 2
        self.radius = [16]
        self.padding = dp(20)
        self.size_hint_y = None
        self.height = dp(160)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header
        title = MDLabel(
            text="Transfer Stats",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title)
        layout.add_widget(MDDivider())
        
        # Stats
        self.total_label = MDLabel(text="Total Transferred: 0 MB", font_style="Body", theme_text_color="Secondary")
        self.rate_label = MDLabel(text="Transfer Rate: 0 KB/s", font_style="Body", theme_text_color="Secondary")
        
        layout.add_widget(self.total_label)
        layout.add_widget(self.rate_label)
        
        self.add_widget(layout)
    
    def update_stats(self, total_mb: float = 0, rate_kbs: float = 0):
        """Update transfer statistics"""
        try:
            self.total_label.text = f"Total Transferred: {total_mb:.1f} MB"
            self.rate_label.text = f"Transfer Rate: {rate_kbs:.1f} KB/s"
        except Exception as e:
            print(f"[ERROR] Failed to update transfer stats: {e}")


class MaintenanceCard(MDCard):
    """Maintenance and cleanup statistics card"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceContainerColor
        self.elevation = 2
        self.radius = [16]
        self.padding = dp(20)
        self.size_hint_y = None
        self.height = dp(160)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header
        title = MDLabel(
            text="Maintenance",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title)
        layout.add_widget(MDDivider())
        
        # Maintenance info
        self.cleanup_label = MDLabel(text="Last Cleanup: Never", font_style="Body", theme_text_color="Secondary")
        self.files_label = MDLabel(text="Files Cleaned: 0", font_style="Body", theme_text_color="Secondary")
        
        layout.add_widget(self.cleanup_label)
        layout.add_widget(self.files_label)
        
        self.add_widget(layout)
    
    def update_maintenance(self, last_cleanup: str = "Never", files_cleaned: int = 0):
        """Update maintenance information"""
        try:
            self.cleanup_label.text = f"Last Cleanup: {last_cleanup}"
            self.files_label.text = f"Files Cleaned: {files_cleaned}"
        except Exception as e:
            print(f"[ERROR] Failed to update maintenance info: {e}")


class ControlPanelCard(MDCard):
    """Enhanced control panel with colorful MD3 action buttons"""
    
    def __init__(self, dashboard_screen, **kwargs):
        super().__init__(**kwargs)
        self.dashboard_screen = dashboard_screen
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceContainerColor
        self.elevation = 2
        self.radius = [16]
        self.padding = dp(20)
        self.size_hint_y = None
        self.height = dp(160)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header
        title = MDLabel(
            text="Control Panel",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title)
        layout.add_widget(MDDivider())
        
        # Button grid
        button_grid = MDGridLayout(cols=2, spacing=dp(8), adaptive_height=True)
        
        # Start button (Green)
        self.start_button = MDButton(
            MDButtonText(text="▶ Start"),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color="#4CAF50",  # Green
            size_hint_y=None,
            height=dp(36)
        )
        self.start_button.bind(on_release=self.dashboard_screen.start_server)
        
        # Stop button (Red)
        self.stop_button = MDButton(
            MDButtonText(text="⏹ Stop"),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color="#F44336",  # Red
            size_hint_y=None,
            height=dp(36)
        )
        self.stop_button.bind(on_release=self.dashboard_screen.stop_server)
        
        # Restart button (Orange)
        self.restart_button = MDButton(
            MDButtonText(text="🔄 Restart"),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color="#FF9800",  # Orange
            size_hint_y=None,
            height=dp(36)
        )
        self.restart_button.bind(on_release=self.dashboard_screen.restart_server)
        
        # Backup DB button (Purple)
        self.backup_button = MDButton(
            MDButtonText(text="💾 Backup DB"),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color="#9C27B0",  # Purple
            size_hint_y=None,
            height=dp(36)
        )
        self.backup_button.bind(on_release=self.on_backup_db)
        
        button_grid.add_widget(self.start_button)
        button_grid.add_widget(self.stop_button)
        button_grid.add_widget(self.restart_button)
        button_grid.add_widget(self.backup_button)
        
        layout.add_widget(button_grid)
        self.add_widget(layout)
    
    def on_backup_db(self, *args):
        """Handle backup database button"""
        print("[INFO] Backup DB requested")
        # TODO: Implement database backup functionality
    
    def update_button_states(self, server_running: bool):
        """Update button states based on server status"""
        try:
            self.start_button.disabled = server_running
            self.stop_button.disabled = not server_running
            self.restart_button.disabled = not server_running
        except Exception as e:
            print(f"[ERROR] Failed to update button states: {e}")


class PerformanceChartCard(MDCard):
    """Live system performance chart with CPU and Memory monitoring"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceContainerColor
        self.elevation = 2
        self.radius = [16]
        self.padding = dp(20)
        self.size_hint_y = None
        self.height = dp(300)
        
        # Performance data
        self.cpu_data = deque(maxlen=60)  # Last 60 readings
        self.memory_data = deque(maxlen=60)
        self.time_data = deque(maxlen=60)
        
        self._build_ui()
        
        # Schedule performance updates
        Clock.schedule_interval(self.update_performance_data, 1.0)
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header
        title = MDLabel(
            text="Live System Performance",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title)
        layout.add_widget(MDDivider())
        
        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure
            self.fig, self.ax = plt.subplots(figsize=(8, 4))
            self.fig.patch.set_facecolor('#2E2E2E')  # Dark background
            self.ax.set_facecolor('#2E2E2E')
            
            # Initialize empty lines
            self.cpu_line, = self.ax.plot([], [], 'g-', label='CPU %', linewidth=2)
            self.memory_line, = self.ax.plot([], [], 'b-', label='Memory %', linewidth=2)
            
            self.ax.set_xlim(0, 60)
            self.ax.set_ylim(0, 100)
            self.ax.set_xlabel('Time (seconds ago)', color='white')
            self.ax.set_ylabel('Usage (%)', color='white')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            self.ax.tick_params(colors='white')
            
            # Add to layout
            canvas = FigureCanvasKivyAgg(self.fig)
            layout.add_widget(canvas)
        else:
            # Fallback if matplotlib not available
            fallback_label = MDLabel(
                text="Performance chart unavailable\n(matplotlib not installed)",
                theme_text_color="Secondary",
                halign="center"
            )
            layout.add_widget(fallback_label)
        
        self.add_widget(layout)
    
    def update_performance_data(self, dt):
        """Update performance data and chart"""
        try:
            if not MATPLOTLIB_AVAILABLE:
                return
            
            # Get current system stats
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            # Add to data queues
            self.cpu_data.append(cpu_percent)
            self.memory_data.append(memory_percent)
            self.time_data.append(len(self.cpu_data))
            
            # Update chart
            if len(self.cpu_data) > 1:
                x_data = list(range(len(self.cpu_data)))
                self.cpu_line.set_data(x_data, list(self.cpu_data))
                self.memory_line.set_data(x_data, list(self.memory_data))
                
                # Adjust x-axis
                self.ax.set_xlim(max(0, len(self.cpu_data) - 60), max(60, len(self.cpu_data)))
                
                # Redraw
                self.fig.canvas.draw()
                
        except Exception as e:
            print(f"[ERROR] Failed to update performance data: {e}")


class ActivityLogCard(MDCard):
    """Enhanced activity log with proper text constraints"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceContainerColor
        self.elevation = 2
        self.radius = [16]
        self.padding = dp(20)
        self.size_hint_y = None
        self.height = dp(300)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header with clear button
        header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))
        
        title = MDLabel(
            text="Activity Log",
            theme_text_color="Primary",
            font_style="Headline",
            adaptive_height=True
        )
        header.add_widget(title)
        
        clear_button = MDIconButton(
            icon="delete",
            on_release=self.clear_log,
            size_hint=(None, None),
            size=(dp(32), dp(32))
        )
        header.add_widget(clear_button)
        
        layout.add_widget(header)
        layout.add_widget(MDDivider())
        
        # Scrollable log
        scroll = MDScrollView()
        self.log_list = MDList()
        scroll.add_widget(self.log_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
        # Add initial message
        self.add_log_entry("System", "Enhanced dashboard initialized")
    
    def add_log_entry(self, source: str, message: str, level: str = "INFO"):
        """Add log entry with proper text constraints"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Create properly constrained list item
            item = MDListItem(
                size_hint_y=None,
                height=dp(56),
                spacing=dp(4)
            )
            
            # Headline with source and timestamp
            headline = MDListItemHeadlineText(
                text=f"[{timestamp}] {source}",
                adaptive_width=True,
                shorten=True,
                max_lines=1
            )
            
            # Supporting text with message
            supporting = MDListItemSupportingText(
                text=message,
                adaptive_width=True,
                shorten=True,
                max_lines=1
            )
            
            # Apply color coding
            if level == "ERROR":
                headline.text_color = supporting.text_color = self.theme_cls.errorColor
            elif level == "WARNING":
                headline.text_color = supporting.text_color = self.theme_cls.tertiaryColor
            else:
                headline.theme_text_color = "Primary"
                supporting.theme_text_color = "Secondary"
            
            item.add_widget(headline)
            item.add_widget(supporting)
            
            self.log_list.add_widget(item, index=0)
            
            # Keep only last 100 entries
            if len(self.log_list.children) > 100:
                self.log_list.remove_widget(self.log_list.children[-1])
                
        except Exception as e:
            print(f"[ERROR] Failed to add log entry: {e}")
    
    def clear_log(self, *args):
        """Clear activity log"""
        try:
            self.log_list.clear_widgets()
            self.add_log_entry("System", "Activity log cleared")
        except Exception as e:
            print(f"[ERROR] Failed to clear log: {e}")


class DashboardScreen(MDScreen):
    """
    Enhanced dashboard with comprehensive 6-card layout
    
    Features:
    - Responsive 3-column grid layout
    - Real-time performance monitoring with charts
    - Professional control panel with colorful buttons
    - Enhanced activity logging with proper constraints
    - Material Design 3 styling throughout
    """
    
    def __init__(self, server_bridge: Optional[ServerIntegrationBridge] = None,
                 config: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        
        self.server_bridge = server_bridge
        self.config = config or {}
        
        # Card references
        self.server_status_card: Optional[ServerStatusCard] = None
        self.client_stats_card: Optional[ClientStatsCard] = None
        self.transfer_stats_card: Optional[TransferStatsCard] = None
        self.control_panel_card: Optional[ControlPanelCard] = None
        self.maintenance_card: Optional[MaintenanceCard] = None
        self.performance_card: Optional[PerformanceChartCard] = None
        self.activity_card: Optional[ActivityLogCard] = None
        
        # State tracking
        self.last_status: Optional[ServerStatus] = None
        self.update_event = None
        
        self.build_ui()
        Clock.schedule_once(self.initial_load, 0.5)
    
    def build_ui(self):
        """Build comprehensive dashboard UI with 6-card layout"""
        try:
            # Main scroll container
            scroll = MDScrollView()
            main_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(16),
                padding=[dp(16), dp(16), dp(16), dp(16)],
                adaptive_height=True
            )
            
            # Top row: Server Status, Client Stats, Control Panel
            top_grid = MDGridLayout(
                cols=3,
                spacing=dp(16),
                adaptive_height=True,
                size_hint_y=None,
                height=dp(160)
            )
            
            self.server_status_card = ServerStatusCard()
            self.client_stats_card = ClientStatsCard()
            self.control_panel_card = ControlPanelCard(self)
            
            top_grid.add_widget(self.server_status_card)
            top_grid.add_widget(self.client_stats_card)
            top_grid.add_widget(self.control_panel_card)
            
            main_layout.add_widget(top_grid)
            
            # Middle row: Transfer Stats, Maintenance
            middle_grid = MDGridLayout(
                cols=2,
                spacing=dp(16),
                adaptive_height=True,
                size_hint_y=None,
                height=dp(160)
            )
            
            self.transfer_stats_card = TransferStatsCard()
            self.maintenance_card = MaintenanceCard()
            
            middle_grid.add_widget(self.transfer_stats_card)
            middle_grid.add_widget(self.maintenance_card)
            
            main_layout.add_widget(middle_grid)
            
            # Bottom row: Performance Chart, Activity Log
            bottom_grid = MDGridLayout(
                cols=2,
                spacing=dp(16),
                adaptive_height=True,
                size_hint_y=None,
                height=dp(300)
            )
            
            self.performance_card = PerformanceChartCard()
            self.activity_card = ActivityLogCard()
            
            bottom_grid.add_widget(self.performance_card)
            bottom_grid.add_widget(self.activity_card)
            
            main_layout.add_widget(bottom_grid)
            
            scroll.add_widget(main_layout)
            self.add_widget(scroll)
            
        except Exception as e:
            print(f"[ERROR] Failed to build enhanced dashboard: {e}")
            traceback.print_exc()
    
    def initial_load(self, dt):
        """Initial data loading and setup"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Loading comprehensive dashboard...")
            
            self.refresh_all_data()
            self.schedule_updates()
            
        except Exception as e:
            print(f"[ERROR] Initial load failed: {e}")
    
    def schedule_updates(self):
        """Schedule periodic updates"""
        try:
            self.stop_updates()
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
    
    def periodic_update(self, dt):
        """Periodic data refresh"""
        try:
            if self.server_bridge:
                status = self.server_bridge.get_latest_status()
                if status:
                    self.update_server_status(status)
        except Exception as e:
            print(f"[ERROR] Periodic update failed: {e}")
    
    def refresh_all_data(self):
        """Refresh all dashboard data"""
        try:
            # Update client stats (mock data for now)
            if self.client_stats_card:
                self.client_stats_card.update_stats(connected=0, total=0, active_transfers=0)
            
            # Update transfer stats (mock data for now)
            if self.transfer_stats_card:
                self.transfer_stats_card.update_stats(total_mb=0, rate_kbs=0)
            
            # Update maintenance info (mock data for now)
            if self.maintenance_card:
                self.maintenance_card.update_maintenance(last_cleanup="Never", files_cleaned=0)
            
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Dashboard data refreshed")
                
        except Exception as e:
            print(f"[ERROR] Data refresh failed: {e}")
    
    def update_server_status(self, status: ServerStatus):
        """Update server status across all cards"""
        try:
            if self.server_status_card:
                self.server_status_card.update_status(status)
            
            if self.control_panel_card:
                self.control_panel_card.update_button_states(status.running)
            
            # Log status changes
            if self.last_status is None or self.last_status.running != status.running:
                if self.activity_card:
                    msg = "Server started" if status.running else "Server stopped"
                    self.activity_card.add_log_entry("Server", msg)
            
            self.last_status = status
            
        except Exception as e:
            print(f"[ERROR] Status update failed: {e}")
    
    def start_server(self, *args):
        """Start the server"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("User", "Starting server...")
            
            if self.server_bridge:
                self.server_bridge.start_server_async()
                Clock.schedule_once(self.check_command_response, 2.0)
        except Exception as e:
            print(f"[ERROR] Start server failed: {e}")
    
    def stop_server(self, *args):
        """Stop the server"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("User", "Stopping server...")
            
            if self.server_bridge:
                self.server_bridge.stop_server_async()
                Clock.schedule_once(self.check_command_response, 2.0)
        except Exception as e:
            print(f"[ERROR] Stop server failed: {e}")
    
    def restart_server(self, *args):
        """Restart the server"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("User", "Restarting server...")
            
            if self.server_bridge:
                self.server_bridge.restart_server_async()
                Clock.schedule_once(self.check_command_response, 5.0)
        except Exception as e:
            print(f"[ERROR] Restart server failed: {e}")
    
    def check_command_response(self, dt):
        """Check server command response"""
        try:
            if self.server_bridge and self.activity_card:
                response = self.server_bridge.get_command_response()
                if response:
                    command = response.get('command', 'unknown')
                    success = response.get('success', False)
                    message = response.get('message', 'No message')
                    level = "INFO" if success else "ERROR"
                    self.activity_card.add_log_entry("Server", f"{command}: {message}", level)
        except Exception as e:
            print(f"[ERROR] Command response check failed: {e}")
    
    def on_enter(self):
        """Screen entered"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Enhanced dashboard entered")
            self.schedule_updates()
            self.refresh_all_data()
        except Exception as e:
            print(f"[ERROR] Dashboard on_enter failed: {e}")
    
    def on_leave(self):
        """Screen left"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Dashboard left")
            self.stop_updates()
        except Exception as e:
            print(f"[ERROR] Dashboard on_leave failed: {e}")