#!/usr/bin/env python3
"""
Advanced Analytics Component for Flet GUI
Provides comprehensive system analytics, performance monitoring, and statistics.
"""

import flet as ft
import psutil
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..utils.server_bridge import ServerBridge


class AdvancedAnalytics:
    """Advanced analytics component with real-time monitoring."""
    
    def __init__(self, server_bridge: ServerBridge):
        self.server_bridge = server_bridge
        
        # Performance data tracking
        self.cpu_data = []
        self.memory_data = []
        self.disk_data = []
        self.network_data = []
        
        # UI components
        self.cpu_progress = None
        self.memory_progress = None
        self.disk_progress = None
        self.system_info_text = None
        self.performance_chart = None
        
    def build(self) -> ft.Control:
        """Build the advanced analytics view."""
        
        # System performance indicators
        self.cpu_progress = ft.ProgressRing(
            width=80, height=80, stroke_width=8,
            color=ft.Colors.BLUE_600
        )
        
        self.memory_progress = ft.ProgressRing(
            width=80, height=80, stroke_width=8,
            color=ft.Colors.GREEN_600
        )
        
        self.disk_progress = ft.ProgressRing(
            width=80, height=80, stroke_width=8,
            color=ft.Colors.ORANGE_600
        )
        
        # System information card
        self.system_info_text = ft.Text(
            "Loading system information...",
            size=14
        )
        
        system_info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("🖥️ System Information", 
                           style=ft.TextThemeStyle.TITLE_MEDIUM,
                           weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.system_info_text
                ], spacing=10),
                padding=20,
            )
        )
        
        # Performance monitoring cards
        performance_cards = ft.ResponsiveRow([
            ft.Column(col={"sm": 12, "md": 4}, controls=[
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("💻 CPU Usage", 
                                   style=ft.TextThemeStyle.TITLE_SMALL,
                                   weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Column([
                                    self.cpu_progress,
                                    ft.Text("0%", size=16, weight=ft.FontWeight.BOLD)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                alignment=ft.alignment.center
                            )
                        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        width=250
                    )
                )
            ]),
            ft.Column(col={"sm": 12, "md": 4}, controls=[
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("🧠 Memory Usage", 
                                   style=ft.TextThemeStyle.TITLE_SMALL,
                                   weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Column([
                                    self.memory_progress,
                                    ft.Text("0%", size=16, weight=ft.FontWeight.BOLD)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                alignment=ft.alignment.center
                            )
                        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        width=250
                    )
                )
            ]),
            ft.Column(col={"sm": 12, "md": 4}, controls=[
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("💾 Disk Usage", 
                                   style=ft.TextThemeStyle.TITLE_SMALL,
                                   weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Column([
                                    self.disk_progress,
                                    ft.Text("0%", size=16, weight=ft.FontWeight.BOLD)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                alignment=ft.alignment.center
                            )
                        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        width=250
                    )
                )
            ])
        ])
        
        # Database analytics card
        database_analytics_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📊 Database Analytics", 
                           style=ft.TextThemeStyle.TITLE_MEDIUM,
                           weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([
                        self._create_stat_item("Total Clients", "0", ft.Icons.PEOPLE),
                        self._create_stat_item("Total Files", "0", ft.Icons.FOLDER),
                        self._create_stat_item("Storage Used", "0 MB", ft.Icons.STORAGE),
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    ft.Divider(),
                    ft.Row([
                        self._create_stat_item("Today's Transfers", "0", ft.Icons.UPLOAD),
                        self._create_stat_item("Active Clients", "0", ft.Icons.ONLINE_PREDICTION),
                        self._create_stat_item("Success Rate", "0%", ft.Icons.CHECK_CIRCLE),
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                ], spacing=15),
                padding=20,
            )
        )
        
        # Server status analytics
        server_analytics_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("⚡ Server Performance", 
                           style=ft.TextThemeStyle.TITLE_MEDIUM,
                           weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Column([
                        self._create_performance_bar("Request Rate", 0, "req/min"),
                        self._create_performance_bar("Error Rate", 0, "%"),
                        self._create_performance_bar("Average Response", 0, "ms"),
                        self._create_performance_bar("Uptime", 100, "%"),
                    ], spacing=10)
                ], spacing=15),
                padding=20,
            )
        )
        
        # Export controls
        export_controls = ft.Row([
            ft.ElevatedButton(
                "📊 Export Analytics Report",
                icon=ft.Icons.DOWNLOAD,
                on_click=self._export_analytics,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            ),
            ft.ElevatedButton(
                "📈 Generate Performance Report",
                icon=ft.Icons.ANALYTICS,
                on_click=self._generate_performance_report,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            ),
            ft.ElevatedButton(
                "🔄 Refresh Data",
                icon=ft.Icons.REFRESH,
                on_click=self._refresh_analytics,
                bgcolor=ft.Colors.ORANGE_600,
                color=ft.Colors.WHITE
            )
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
        
        return ft.Column([
            ft.Text("📊 Advanced Analytics", 
                   style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                   weight=ft.FontWeight.BOLD),
            ft.Divider(),
            performance_cards,
            ft.Container(height=20),  # Spacing
            ft.ResponsiveRow([
                ft.Column(col={"sm": 12, "md": 6}, controls=[system_info_card]),
                ft.Column(col={"sm": 12, "md": 6}, controls=[database_analytics_card])
            ]),
            ft.Container(height=20),  # Spacing
            server_analytics_card,
            ft.Container(height=20),  # Spacing
            export_controls
        ], spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _create_stat_item(self, label: str, value: str, icon: str) -> ft.Control:
        """Create a statistic display item."""
        return ft.Column([
            ft.Icon(icon, size=32, color=ft.Colors.BLUE_600),
            ft.Text(value, size=20, weight=ft.FontWeight.BOLD),
            ft.Text(label, size=12, color=ft.Colors.GREY_600)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
    
    def _create_performance_bar(self, label: str, value: float, unit: str) -> ft.Control:
        """Create a performance progress bar."""
        return ft.Column([
            ft.Row([
                ft.Text(label, expand=True),
                ft.Text(f"{value} {unit}", weight=ft.FontWeight.BOLD)
            ]),
            ft.ProgressBar(value=value/100 if unit == "%" else min(value/100, 1.0), 
                          color=ft.Colors.BLUE_600, height=8)
        ], spacing=5)
    
    async def update_real_time(self):
        """Update analytics with real-time system data."""
        try:
            # Get system performance data
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Update progress rings
            if self.cpu_progress:
                self.cpu_progress.value = cpu_percent / 100
                # Update CPU text (find the text widget in the same card)
            
            if self.memory_progress:
                self.memory_progress.value = memory.percent / 100
            
            if self.disk_progress:
                self.disk_progress.value = disk.percent / 100
            
            # Update system information
            if self.system_info_text:
                system_info = self._get_system_info()
                self.system_info_text.value = system_info
            
            # Track historical data
            self.cpu_data.append((datetime.now(), cpu_percent))
            self.memory_data.append((datetime.now(), memory.percent))
            self.disk_data.append((datetime.now(), disk.percent))
            
            # Keep only last 100 data points
            self.cpu_data = self.cpu_data[-100:]
            self.memory_data = self.memory_data[-100:]
            self.disk_data = self.disk_data[-100:]
            
        except Exception as e:
            print(f"[ERROR] Failed to update analytics: {e}")
    
    def _get_system_info(self) -> str:
        """Get comprehensive system information."""
        try:
            # System info
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # Network info
            network_io = psutil.net_io_counters()
            
            # Process info
            process_count = len(psutil.pids())
            
            info = f"""🖥️ Platform: {psutil.virtual_memory().total // (1024**3)} GB RAM
⏱️ Uptime: {str(uptime).split('.')[0]}
🔌 Processes: {process_count}
📡 Network: ⬇️{network_io.bytes_recv // (1024**2)} MB  ⬆️{network_io.bytes_sent // (1024**2)} MB
🌡️ CPU Cores: {psutil.cpu_count()} physical, {psutil.cpu_count(logical=True)} logical"""
            
            return info
            
        except Exception as e:
            return f"System information unavailable: {e}"
    
    def _export_analytics(self, e):
        """Export analytics data to file."""
        print("[INFO] Exporting analytics report...")
        # TODO: Implement analytics export functionality
    
    def _generate_performance_report(self, e):
        """Generate performance report."""
        print("[INFO] Generating performance report...")
        # TODO: Implement performance report generation
    
    def _refresh_analytics(self, e):
        """Manually refresh analytics data."""
        print("[INFO] Refreshing analytics data...")
        # TODO: Implement manual refresh