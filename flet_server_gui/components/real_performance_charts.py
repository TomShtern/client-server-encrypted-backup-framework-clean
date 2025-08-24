"""
Real Performance Charts for Flet Server GUI
Live system performance visualization with actual metrics
"""

import flet as ft
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)

class RealPerformanceCharts:
    """
    Real-time performance charts with live system metrics.
    NO mock data - uses actual psutil metrics from server bridge.
    """
    
    def __init__(self, server_bridge):
        """Initialize with real server bridge for metrics"""
        self.server_bridge = server_bridge
        
        # Real-time data storage (last 60 data points = 5 minutes at 5-second intervals)
        self.max_data_points = 60
        self.cpu_data = deque(maxlen=self.max_data_points)
        self.memory_data = deque(maxlen=self.max_data_points)
        self.disk_data = deque(maxlen=self.max_data_points)
        self.network_data = deque(maxlen=self.max_data_points)
        self.timestamps = deque(maxlen=self.max_data_points)
        
        # Chart update state
        self.monitoring_active = False
        self.update_interval = 5  # seconds
        
        # UI components
        self.cpu_chart_container = ft.Container()
        self.memory_chart_container = ft.Container()
        self.disk_chart_container = ft.Container()
        self.network_chart_container = ft.Container()
        
        # Stats displays
        self.cpu_stats = ft.Text("CPU: --", size=12, weight=ft.FontWeight.BOLD)
        self.memory_stats = ft.Text("Memory: --", size=12, weight=ft.FontWeight.BOLD)
        self.disk_stats = ft.Text("Disk: --", size=12, weight=ft.FontWeight.BOLD)
        self.network_stats = ft.Text("Network: --", size=12, weight=ft.FontWeight.BOLD)
        
        logger.info("✅ Real performance charts initialized")
    
    def create_performance_charts(self) -> ft.Container:
        """Create the main performance charts view with real metrics"""
        
        # Controls bar
        controls_bar = ft.Row([
            ft.ElevatedButton(
                text="Start Monitoring" if not self.monitoring_active else "Stop Monitoring",
                icon=ft.icons.play_arrow if not self.monitoring_active else ft.icons.stop,
                on_click=self._toggle_monitoring
            ),
            ft.VerticalDivider(width=1),
            ft.Text(f"Update Interval: {self.update_interval}s", size=12),
            ft.Slider(
                min=1,
                max=30,
                divisions=29,
                value=float(self.update_interval),
                label="{value}s",
                width=150,
                on_change=self._on_interval_changed
            ),
            ft.Container(expand=1),
            ft.ElevatedButton(
                text="Export Data",
                icon=ft.icons.download,
                on_click=self._export_performance_data
            ),
            ft.ElevatedButton(
                text="Clear History",
                icon=ft.icons.clear,
                on_click=self._clear_history
            )
        ])
        
        # Current metrics row
        metrics_row = ft.Row([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.memory, size=24, color=ft.Colors.BLUE),
                        self.cpu_stats
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    width=120
                )
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.storage, size=24, color=ft.Colors.GREEN),
                        self.memory_stats
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    width=120
                )
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.hard_drive, size=24, color=ft.Colors.ORANGE),
                        self.disk_stats
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    width=120
                )
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.network_check, size=24, color=ft.Colors.PURPLE),
                        self.network_stats
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    width=120
                )
            )
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        
        # Charts grid
        charts_grid = ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("CPU Usage %", size=14, weight=ft.FontWeight.BOLD),
                        self._create_text_chart("cpu", ft.Colors.BLUE)
                    ]),
                    expand=1,
                    padding=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Memory Usage %", size=14, weight=ft.FontWeight.BOLD),
                        self._create_text_chart("memory", ft.Colors.GREEN)
                    ]),
                    expand=1,
                    padding=10
                )
            ]),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Disk Usage %", size=14, weight=ft.FontWeight.BOLD),
                        self._create_text_chart("disk", ft.Colors.ORANGE)
                    ]),
                    expand=1,
                    padding=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Network Activity", size=14, weight=ft.FontWeight.BOLD),
                        self._create_text_chart("network", ft.Colors.PURPLE)
                    ]),
                    expand=1,
                    padding=10
                )
            ])
        ])
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Performance Monitoring",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PRIMARY
                ),
                ft.Text(
                    "Real-time system performance metrics and historical data",
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                ),
                ft.Divider(height=20),
                controls_bar,
                ft.Divider(),
                metrics_row,
                ft.Divider(),
                charts_grid
            ]),
            padding=20,
            expand=True
        )
    
    def _create_text_chart(self, metric_type: str, color: str) -> ft.Container:
        """Create a text-based chart for the metric (Flet doesn't have built-in charts)"""
        chart_container = ft.Container(
            content=ft.Column([
                ft.Text("No data yet - start monitoring to see live metrics", 
                       size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Container(
                    content=ft.Row([]),  # Will be populated with data bars
                    height=100,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=4,
                    padding=5
                )
            ]),
            expand=True
        )
        
        # Store reference for updates
        if metric_type == "cpu":
            self.cpu_chart_container = chart_container
        elif metric_type == "memory":
            self.memory_chart_container = chart_container
        elif metric_type == "disk":
            self.disk_chart_container = chart_container
        elif metric_type == "network":
            self.network_chart_container = chart_container
            
        return chart_container
    
    def _toggle_monitoring(self, e):
        """Toggle performance monitoring"""
        if self.monitoring_active:
            self._stop_monitoring()
            e.control.text = "Start Monitoring"
            e.control.icon = ft.icons.play_arrow
        else:
            self._start_monitoring()
            e.control.text = "Stop Monitoring"
            e.control.icon = ft.icons.stop
        
        e.control.update()
    
    def _start_monitoring(self):
        """Start real-time performance monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        asyncio.create_task(self._monitoring_loop())
        logger.info("✅ Performance monitoring started")
    
    def _stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        logger.info("✅ Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop for collecting real metrics"""
        while self.monitoring_active:
            try:
                # Get real system metrics from server bridge
                metrics = self.server_bridge.get_system_metrics()
                
                if metrics.get('available', False):
                    # Add timestamp
                    current_time = datetime.now()
                    self.timestamps.append(current_time)
                    
                    # Add real metric values
                    self.cpu_data.append(metrics.get('cpu_percent', 0))
                    self.memory_data.append(metrics.get('memory_percent', 0))
                    self.disk_data.append(metrics.get('disk_percent', 0))
                    
                    # Calculate network activity (simple bytes/sec measure)
                    network_activity = metrics.get('network_bytes_sent', 0) + metrics.get('network_bytes_recv', 0)
                    self.network_data.append(min(network_activity / 1024 / 1024, 100))  # MB/s, capped at 100
                    
                    # Update UI
                    self._update_charts_display()
                    self._update_stats_display(metrics)
                    
                else:
                    logger.warning("⚠️ System metrics not available")
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    def _update_charts_display(self):
        """Update the text-based chart displays with current data"""
        if not self.cpu_data:
            return
        
        # Update CPU chart
        self._update_single_chart(self.cpu_chart_container, self.cpu_data, ft.Colors.BLUE, "CPU")
        
        # Update Memory chart  
        self._update_single_chart(self.memory_chart_container, self.memory_data, ft.Colors.GREEN, "Memory")
        
        # Update Disk chart
        self._update_single_chart(self.disk_chart_container, self.disk_data, ft.Colors.ORANGE, "Disk")
        
        # Update Network chart
        self._update_single_chart(self.network_chart_container, self.network_data, ft.Colors.PURPLE, "Network")
    
    def _update_single_chart(self, container: ft.Container, data: deque, color: str, label: str):
        """Update a single chart container with text-based visualization"""
        if not data or not container.content:
            return
        
        try:
            # Create text representation of the chart
            recent_data = list(data)[-20:]  # Show last 20 points
            
            # Create a simple text chart
            chart_text = self._create_text_visualization(recent_data, label)
            
            # Update the chart container
            if isinstance(container.content, ft.Column) and len(container.content.controls) >= 2:
                chart_display = container.content.controls[1]
                
                if isinstance(chart_display, ft.Container):
                    chart_display.content = ft.Column([
                        ft.Text(f"Last 20 data points:", size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text(chart_text, size=10, font_family="monospace"),
                        ft.Text(f"Current: {recent_data[-1]:.1f}% | Avg: {sum(recent_data)/len(recent_data):.1f}% | Max: {max(recent_data):.1f}%", 
                               size=10, color=color)
                    ], spacing=5)
                    
                    chart_display.update()
                    
        except Exception as e:
            logger.error(f"❌ Error updating chart for {label}: {e}")
    
    def _create_text_visualization(self, data: List[float], label: str) -> str:
        """Create a simple text-based visualization of the data"""
        if not data:
            return "No data"
        
        # Create a simple bar chart using characters
        max_val = max(data) if data else 100
        min_val = min(data) if data else 0
        
        # Normalize data to 0-10 scale for visualization
        normalized = []
        for val in data:
            if max_val > min_val:
                norm = int((val - min_val) / (max_val - min_val) * 10)
            else:
                norm = 5  # Default middle value
            normalized.append(min(10, max(0, norm)))
        
        # Create bar chart using Unicode blocks
        bars = []
        for val in normalized:
            if val == 0:
                bars.append('▁')
            elif val <= 1:
                bars.append('▂')
            elif val <= 2:
                bars.append('▃')
            elif val <= 3:
                bars.append('▄')
            elif val <= 4:
                bars.append('▅')
            elif val <= 5:
                bars.append('▆')
            elif val <= 6:
                bars.append('▇')
            else:
                bars.append('█')
        
        return ''.join(bars)
    
    def _update_stats_display(self, metrics: Dict[str, Any]):
        """Update the current stats display"""
        try:
            self.cpu_stats.value = f"CPU: {metrics.get('cpu_percent', 0):.1f}%"
            self.memory_stats.value = f"Memory: {metrics.get('memory_percent', 0):.1f}%"
            self.disk_stats.value = f"Disk: {metrics.get('disk_percent', 0):.1f}%"
            
            network_mb = (metrics.get('network_bytes_sent', 0) + metrics.get('network_bytes_recv', 0)) / 1024 / 1024
            self.network_stats.value = f"Net: {network_mb:.1f} MB/s"
            
            # Update the stats
            self.cpu_stats.update()
            self.memory_stats.update()
            self.disk_stats.update()
            self.network_stats.update()
            
        except Exception as e:
            logger.error(f"❌ Error updating stats display: {e}")
    
    def _on_interval_changed(self, e):
        """Handle update interval change"""
        self.update_interval = int(e.control.value)
        logger.info(f"✅ Update interval changed to {self.update_interval} seconds")
    
    def _export_performance_data(self, e):
        """Export performance data to file"""
        try:
            if not self.timestamps:
                return
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_data_{timestamp}.csv"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Timestamp,CPU%,Memory%,Disk%,Network MB/s\n")
                
                for i, ts in enumerate(self.timestamps):
                    cpu = self.cpu_data[i] if i < len(self.cpu_data) else 0
                    memory = self.memory_data[i] if i < len(self.memory_data) else 0
                    disk = self.disk_data[i] if i < len(self.disk_data) else 0
                    network = self.network_data[i] if i < len(self.network_data) else 0
                    
                    f.write(f"{ts.isoformat()},{cpu:.2f},{memory:.2f},{disk:.2f},{network:.2f}\n")
            
            logger.info(f"✅ Performance data exported to {filename}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting performance data: {e}")
    
    def _clear_history(self, e):
        """Clear performance history"""
        self.cpu_data.clear()
        self.memory_data.clear()  
        self.disk_data.clear()
        self.network_data.clear()
        self.timestamps.clear()
        
        # Clear chart displays
        self._update_charts_display()
        
        logger.info("✅ Performance history cleared")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        if not self.cpu_data:
            return {}
        
        return {
            'cpu_current': self.cpu_data[-1] if self.cpu_data else 0,
            'memory_current': self.memory_data[-1] if self.memory_data else 0,
            'disk_current': self.disk_data[-1] if self.disk_data else 0,
            'network_current': self.network_data[-1] if self.network_data else 0,
            'data_points': len(self.timestamps),
            'monitoring_active': self.monitoring_active,
            'update_interval': self.update_interval
        }