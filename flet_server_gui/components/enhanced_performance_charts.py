"""
Enhanced Performance Charts for Flet Server GUI
Advanced real-time system monitoring with interactive controls and multiple visualization modes
Phase 7.1 Implementation: Interactive charts, time range selection, multiple chart types
"""

import flet as ft
import asyncio
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class MetricThreshold:
    """Performance threshold configuration"""
    warning: float
    critical: float
    enabled: bool = True

@dataclass
class ChartSettings:
    """Chart display and behavior settings"""
    time_range_minutes: int = 5
    update_interval: int = 5
    chart_type: str = "line"  # line, bar, area
    show_thresholds: bool = True
    auto_scale: bool = True
    theme: str = "default"

class EnhancedPerformanceCharts:
    """
    Advanced performance monitoring with interactive controls and multiple visualization modes.
    Phase 7.1: Enhanced charts with real-time alerts, time range controls, and export features.
    """
    
    def __init__(self, server_bridge):
        """Initialize with real server bridge for metrics"""
        self.server_bridge = server_bridge
        
        # Chart settings and configuration
        self.settings = ChartSettings()
        self.thresholds = {
            'cpu': MetricThreshold(warning=70.0, critical=90.0),
            'memory': MetricThreshold(warning=80.0, critical=95.0),
            'disk': MetricThreshold(warning=85.0, critical=95.0),
            'network': MetricThreshold(warning=50.0, critical=100.0)  # MB/s
        }
        
        # Enhanced data storage with configurable history
        self.max_data_points = self._calculate_max_points()
        self.metrics_history = {
            'cpu': deque(maxlen=self.max_data_points),
            'memory': deque(maxlen=self.max_data_points), 
            'disk': deque(maxlen=self.max_data_points),
            'network': deque(maxlen=self.max_data_points),
            'timestamps': deque(maxlen=self.max_data_points)
        }
        
        # Alert system
        self.active_alerts = []
        self.alert_history = deque(maxlen=50)
        
        # Monitoring state
        self.monitoring_active = False
        self.last_update = None
        
        # UI components
        self.chart_containers = {}
        self.stat_displays = {}
        self.control_panel = None
        self.alert_panel = None
        
        # Load saved settings
        self._load_chart_settings()
        
        logger.info("✅ Enhanced performance charts initialized")
    
    def _calculate_max_points(self) -> int:
        """Calculate maximum data points based on time range and update interval"""
        return max(60, (self.settings.time_range_minutes * 60) // self.settings.update_interval)
    
    def create_enhanced_charts_view(self) -> ft.Container:
        """Create the main enhanced charts view with interactive controls"""
        
        # Header with title and controls
        header = self._create_header()
        
        # Control panel for chart settings
        control_panel = self._create_control_panel()
        
        # Alert panel for threshold violations
        alert_panel = self._create_alert_panel()
        
        # Main metrics dashboard
        metrics_grid = self._create_metrics_grid()
        
        # Charts section
        charts_section = self._create_charts_section()
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=10),
                control_panel,
                ft.Divider(),
                alert_panel,
                ft.Divider(),
                metrics_grid,
                ft.Divider(),
                charts_section
            ], spacing=10),
            padding=20,
            expand=True
        )
    
    def _create_header(self) -> ft.Row:
        """Create header with title and main controls"""
        return ft.Row([
            ft.Icon(ft.icons.analytics, size=32, color=ft.Colors.PRIMARY),
            ft.Text(
                "Enhanced Performance Monitoring",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.PRIMARY
            ),
            ft.Container(expand=1),
            ft.ElevatedButton(
                text="Start Monitoring" if not self.monitoring_active else "Stop Monitoring",
                icon=ft.icons.play_arrow if not self.monitoring_active else ft.icons.stop,
                on_click=self._toggle_monitoring,
                bgcolor=ft.Colors.GREEN if not self.monitoring_active else ft.Colors.RED_ACCENT
            ),
            ft.ElevatedButton(
                text="Export Data",
                icon=ft.icons.file_download,
                on_click=self._export_performance_data
            )
        ], alignment=ft.MainAxisAlignment.START)
    
    def _create_control_panel(self) -> ft.Container:
        """Create interactive control panel for chart settings"""
        time_range_dropdown = ft.Dropdown(
            label="Time Range",
            value=str(self.settings.time_range_minutes),
            options=[
                ft.dropdown.Option("1", "1 Minute"),
                ft.dropdown.Option("5", "5 Minutes"), 
                ft.dropdown.Option("10", "10 Minutes"),
                ft.dropdown.Option("30", "30 Minutes"),
                ft.dropdown.Option("60", "1 Hour")
            ],
            on_change=self._on_time_range_changed,
            width=120
        )
        
        update_interval_slider = ft.Row([
            ft.Text("Update Interval:", size=12),
            ft.Slider(
                min=1,
                max=30,
                divisions=29,
                value=float(self.settings.update_interval),
                label=f"{self.settings.update_interval}s",
                width=150,
                on_change=self._on_interval_changed
            )
        ])
        
        chart_type_segmented = ft.SegmentedButton(
            selected={self.settings.chart_type},
            allow_empty_selection=False,
            segments=[
                ft.Segment(
                    value="line",
                    label=ft.Text("Line"),
                    icon=ft.Icon(ft.icons.show_chart)
                ),
                ft.Segment(
                    value="bar", 
                    label=ft.Text("Bar"),
                    icon=ft.Icon(ft.icons.bar_chart)
                ),
                ft.Segment(
                    value="area",
                    label=ft.Text("Area"),
                    icon=ft.Icon(ft.icons.area_chart)
                )
            ],
            on_change=self._on_chart_type_changed
        )
        
        threshold_switch = ft.Switch(
            label="Show Thresholds",
            value=self.settings.show_thresholds,
            on_change=self._on_threshold_toggle
        )
        
        return ft.Container(
            content=ft.Row([
                time_range_dropdown,
                ft.VerticalDivider(width=1),
                update_interval_slider,
                ft.VerticalDivider(width=1),
                chart_type_segmented,
                ft.VerticalDivider(width=1),
                threshold_switch,
                ft.Container(expand=1),
                ft.ElevatedButton(
                    text="Reset View",
                    icon=ft.icons.refresh,
                    on_click=self._reset_charts
                )
            ], alignment=ft.MainAxisAlignment.START),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            padding=10,
            border_radius=8
        )
    
    def _create_alert_panel(self) -> ft.Container:
        """Create alert panel for threshold violations"""
        self.alert_panel = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.notifications, color=ft.Colors.AMBER),
                ft.Text("No active alerts", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Container(expand=1),
                ft.TextButton("Clear All", on_click=self._clear_alerts, visible=False)
            ]),
            bgcolor=ft.Colors.SURFACE,
            padding=8,
            border_radius=4,
            height=40
        )
        return self.alert_panel
    
    def _create_metrics_grid(self) -> ft.Row:
        """Create enhanced metrics display grid"""
        self.stat_displays = {
            'cpu': self._create_metric_card("CPU", ft.icons.memory, ft.Colors.BLUE),
            'memory': self._create_metric_card("Memory", ft.icons.storage, ft.Colors.GREEN),
            'disk': self._create_metric_card("Disk", ft.icons.hard_drive, ft.Colors.ORANGE),
            'network': self._create_metric_card("Network", ft.icons.network_check, ft.Colors.PURPLE)
        }
        
        return ft.Row([
            self.stat_displays['cpu'],
            self.stat_displays['memory'],
            self.stat_displays['disk'],
            self.stat_displays['network']
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
    
    def _create_metric_card(self, title: str, icon, color) -> ft.Card:
        """Create enhanced metric display card"""
        current_text = ft.Text("--", size=24, weight=ft.FontWeight.BOLD, color=color)
        avg_text = ft.Text("Avg: --", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        max_text = ft.Text("Max: --", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        status_indicator = ft.Container(
            width=8,
            height=8,
            bgcolor=ft.Colors.GREY,
            border_radius=4
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, size=24, color=color),
                        ft.Container(expand=1),
                        status_indicator
                    ]),
                    ft.Text(title, size=14, weight=ft.FontWeight.W500),
                    current_text,
                    avg_text,
                    max_text
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.START),
                padding=12,
                width=140
            )
        )
    
    def _create_charts_section(self) -> ft.Container:
        """Create the main charts display section"""
        self.chart_containers = {
            'cpu': self._create_enhanced_chart("CPU Usage %", ft.Colors.BLUE),
            'memory': self._create_enhanced_chart("Memory Usage %", ft.Colors.GREEN),
            'disk': self._create_enhanced_chart("Disk Usage %", ft.Colors.ORANGE),
            'network': self._create_enhanced_chart("Network Activity (MB/s)", ft.Colors.PURPLE)
        }
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self.chart_containers['cpu'],
                    self.chart_containers['memory']
                ]),
                ft.Row([
                    self.chart_containers['disk'],
                    self.chart_containers['network']
                ])
            ], spacing=10),
            expand=True
        )
    
    def _create_enhanced_chart(self, title: str, color) -> ft.Container:
        """Create enhanced chart container with interactive features"""
        chart_display = ft.Container(
            content=ft.Column([
                ft.Text("Start monitoring to see live data", 
                       size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Container(height=100)  # Chart area
            ]),
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=4,
            padding=8,
            expand=True
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=1),
                    ft.IconButton(
                        icon=ft.icons.fullscreen,
                        tooltip="Full Screen",
                        on_click=lambda e, t=title: self._show_fullscreen_chart(t)
                    )
                ]),
                chart_display
            ]),
            expand=1,
            padding=10
        )
    
    def _toggle_monitoring(self, e):
        """Toggle enhanced monitoring with better state management"""
        if self.monitoring_active:
            self._stop_monitoring()
            e.control.text = "Start Monitoring"
            e.control.icon = ft.icons.play_arrow
            e.control.bgcolor = ft.Colors.GREEN
        else:
            self._start_monitoring()
            e.control.text = "Stop Monitoring"
            e.control.icon = ft.icons.stop
            e.control.bgcolor = ft.Colors.RED_ACCENT
        
        e.control.update()
    
    def _start_monitoring(self):
        """Start enhanced monitoring with alert system"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.active_alerts.clear()
        asyncio.create_task(self._enhanced_monitoring_loop())
        logger.info("✅ Enhanced performance monitoring started")
    
    def _stop_monitoring(self):
        """Stop monitoring and cleanup"""
        self.monitoring_active = False
        self._update_alert_panel([])
        logger.info("✅ Enhanced performance monitoring stopped")
    
    async def _enhanced_monitoring_loop(self):
        """Enhanced monitoring loop with alerting and advanced metrics"""
        while self.monitoring_active:
            try:
                # Get real system metrics
                metrics = self.server_bridge.get_system_metrics()
                
                if metrics.get('available', False):
                    current_time = datetime.now()
                    self.metrics_history['timestamps'].append(current_time)
                    
                    # Process each metric
                    metric_values = {
                        'cpu': metrics.get('cpu_percent', 0),
                        'memory': metrics.get('memory_percent', 0), 
                        'disk': metrics.get('disk_percent', 0),
                        'network': min((metrics.get('network_bytes_sent', 0) + 
                                      metrics.get('network_bytes_recv', 0)) / 1024 / 1024, 100)
                    }
                    
                    # Store metric values and check thresholds
                    alerts = []
                    for metric_name, value in metric_values.items():
                        self.metrics_history[metric_name].append(value)
                        
                        # Check for threshold violations
                        if self.thresholds[metric_name].enabled:
                            alert = self._check_threshold(metric_name, value)
                            if alert:
                                alerts.append(alert)
                    
                    # Update UI
                    self._update_enhanced_displays(metric_values)
                    self._update_enhanced_charts()
                    
                    # Handle alerts
                    if alerts:
                        self.active_alerts = alerts
                        self._update_alert_panel(alerts)
                    elif not alerts and self.active_alerts:
                        self.active_alerts = []
                        self._update_alert_panel([])
                    
                    self.last_update = current_time
                
                await asyncio.sleep(self.settings.update_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in enhanced monitoring loop: {e}")
                await asyncio.sleep(5)
    
    def _check_threshold(self, metric_name: str, value: float) -> Optional[Dict]:
        """Check if metric value exceeds thresholds"""
        threshold = self.thresholds[metric_name]
        
        if value >= threshold.critical:
            return {
                'metric': metric_name,
                'value': value,
                'level': 'critical',
                'message': f"{metric_name.upper()} critical: {value:.1f}%"
            }
        elif value >= threshold.warning:
            return {
                'metric': metric_name,
                'value': value,
                'level': 'warning', 
                'message': f"{metric_name.upper()} warning: {value:.1f}%"
            }
        return None
    
    def _update_enhanced_displays(self, metric_values: Dict[str, float]):
        """Update enhanced metric displays with statistics"""
        for metric_name, current_value in metric_values.items():
            if metric_name in self.stat_displays:
                card = self.stat_displays[metric_name]
                
                # Get historical data for statistics
                data = list(self.metrics_history[metric_name])
                if data:
                    avg_val = sum(data) / len(data)
                    max_val = max(data)
                    
                    # Update card content
                    card_content = card.content.content
                    
                    # Current value (third Text component)
                    card_content.controls[2].value = f"{current_value:.1f}%"
                    
                    # Average value (fourth Text component)
                    card_content.controls[3].value = f"Avg: {avg_val:.1f}%"
                    
                    # Max value (fifth Text component)
                    card_content.controls[4].value = f"Max: {max_val:.1f}%"
                    
                    # Status indicator color based on thresholds
                    status_indicator = card_content.controls[0].controls[2]
                    if current_value >= self.thresholds[metric_name].critical:
                        status_indicator.bgcolor = ft.Colors.RED
                    elif current_value >= self.thresholds[metric_name].warning:
                        status_indicator.bgcolor = ft.Colors.AMBER
                    else:
                        status_indicator.bgcolor = ft.Colors.GREEN
                    
                    card.update()
    
    def _update_enhanced_charts(self):
        """Update charts with enhanced visualization"""
        for metric_name, container in self.chart_containers.items():
            data = list(self.metrics_history[metric_name])
            if data:
                self._update_single_enhanced_chart(container, data, metric_name)
    
    def _update_single_enhanced_chart(self, container: ft.Container, data: List[float], metric_name: str):
        """Update single chart with enhanced visualization"""
        try:
            chart_display = container.content.controls[1]  # Second control is chart display
            
            # Create enhanced visualization based on chart type
            if self.settings.chart_type == "line":
                viz_text = self._create_line_visualization(data, metric_name)
            elif self.settings.chart_type == "bar":
                viz_text = self._create_bar_visualization(data, metric_name)
            else:  # area
                viz_text = self._create_area_visualization(data, metric_name)
            
            # Statistics
            recent_data = data[-20:] if len(data) > 20 else data
            current = recent_data[-1] if recent_data else 0
            avg = sum(recent_data) / len(recent_data) if recent_data else 0
            max_val = max(recent_data) if recent_data else 0
            
            # Threshold indicators
            threshold_info = ""
            if self.settings.show_thresholds and self.thresholds[metric_name].enabled:
                threshold_info = f" | ⚠️{self.thresholds[metric_name].warning:.0f}% 🔴{self.thresholds[metric_name].critical:.0f}%"
            
            # Update chart display
            chart_display.content = ft.Column([
                ft.Text(f"Last {len(recent_data)} points:", size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(viz_text, size=10, font_family="monospace"),
                ft.Text(
                    f"Current: {current:.1f}% | Avg: {avg:.1f}% | Max: {max_val:.1f}%{threshold_info}",
                    size=10
                )
            ], spacing=5)
            
            chart_display.update()
            
        except Exception as e:
            logger.error(f"❌ Error updating enhanced chart for {metric_name}: {e}")
    
    def _create_line_visualization(self, data: List[float], metric_name: str) -> str:
        """Create line chart visualization"""
        if not data:
            return "No data"
        
        recent_data = data[-40:] if len(data) > 40 else data
        max_val = max(recent_data) if recent_data else 100
        min_val = min(recent_data) if recent_data else 0
        
        # Create line chart using Unicode characters
        chars = []
        for val in recent_data:
            if max_val > min_val:
                norm = (val - min_val) / (max_val - min_val)
            else:
                norm = 0.5
            
            # Line chart characters
            if norm < 0.1:
                chars.append('▁')
            elif norm < 0.2:
                chars.append('▂')
            elif norm < 0.3:
                chars.append('▃')
            elif norm < 0.4:
                chars.append('▄')
            elif norm < 0.5:
                chars.append('▅')
            elif norm < 0.6:
                chars.append('▆')
            elif norm < 0.8:
                chars.append('▇')
            else:
                chars.append('█')
        
        return ''.join(chars)
    
    def _create_bar_visualization(self, data: List[float], metric_name: str) -> str:
        """Create bar chart visualization"""
        if not data:
            return "No data"
        
        recent_data = data[-20:] if len(data) > 20 else data
        max_val = max(recent_data) if recent_data else 100
        
        # Create bar chart
        bars = []
        for val in recent_data:
            norm = val / max_val if max_val > 0 else 0
            if norm < 0.25:
                bars.append('▁')
            elif norm < 0.5:
                bars.append('▃')
            elif norm < 0.75:
                bars.append('▆')
            else:
                bars.append('█')
        
        return ' '.join(bars)
    
    def _create_area_visualization(self, data: List[float], metric_name: str) -> str:
        """Create area chart visualization"""
        # For simplicity, use filled blocks for area chart
        return self._create_line_visualization(data, metric_name).replace('▁', '░').replace('▂', '▒').replace('▃', '▓')
    
    def _update_alert_panel(self, alerts: List[Dict]):
        """Update alert panel with current alerts"""
        try:
            if not alerts:
                self.alert_panel.content = ft.Row([
                    ft.Icon(ft.icons.notifications, color=ft.Colors.GREEN),
                    ft.Text("All systems normal", size=12, color=ft.Colors.GREEN),
                    ft.Container(expand=1)
                ])
                self.alert_panel.bgcolor = ft.Colors.SURFACE
            else:
                alert_text = " | ".join([alert['message'] for alert in alerts])
                critical_count = len([a for a in alerts if a['level'] == 'critical'])
                
                icon_color = ft.Colors.RED if critical_count > 0 else ft.Colors.AMBER
                
                self.alert_panel.content = ft.Row([
                    ft.Icon(ft.icons.warning, color=icon_color),
                    ft.Text(alert_text, size=12, color=icon_color, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=1),
                    ft.TextButton("Clear", on_click=self._clear_alerts, visible=True)
                ])
                
                self.alert_panel.bgcolor = ft.Colors.ERROR_CONTAINER if critical_count > 0 else ft.Colors.WARNING_CONTAINER
            
            self.alert_panel.update()
            
        except Exception as e:
            logger.error(f"❌ Error updating alert panel: {e}")
    
    def _on_time_range_changed(self, e):
        """Handle time range selection change"""
        self.settings.time_range_minutes = int(e.control.value)
        self.max_data_points = self._calculate_max_points()
        
        # Resize data collections
        for key in self.metrics_history:
            old_data = list(self.metrics_history[key])
            self.metrics_history[key] = deque(old_data[-self.max_data_points:], maxlen=self.max_data_points)
        
        self._save_chart_settings()
        logger.info(f"✅ Time range changed to {self.settings.time_range_minutes} minutes")
    
    def _on_interval_changed(self, e):
        """Handle update interval change"""
        self.settings.update_interval = int(e.control.value)
        e.control.label = f"{self.settings.update_interval}s"
        self._save_chart_settings()
        logger.info(f"✅ Update interval changed to {self.settings.update_interval} seconds")
    
    def _on_chart_type_changed(self, e):
        """Handle chart type change"""
        if e.control.selected:
            self.settings.chart_type = list(e.control.selected)[0]
            self._save_chart_settings()
            logger.info(f"✅ Chart type changed to {self.settings.chart_type}")
    
    def _on_threshold_toggle(self, e):
        """Handle threshold display toggle"""
        self.settings.show_thresholds = e.control.value
        self._save_chart_settings()
        logger.info(f"✅ Threshold display: {self.settings.show_thresholds}")
    
    def _clear_alerts(self, e):
        """Clear all active alerts"""
        self.active_alerts = []
        self._update_alert_panel([])
    
    def _reset_charts(self, e):
        """Reset charts to default view"""
        for key in self.metrics_history:
            self.metrics_history[key].clear()
        self._update_enhanced_charts()
        logger.info("✅ Charts reset")
    
    def _show_fullscreen_chart(self, title: str):
        """Show fullscreen view of specific chart (placeholder for future implementation)"""
        logger.info(f"📊 Fullscreen chart requested: {title}")
        # TODO: Implement fullscreen chart dialog
    
    def _export_performance_data(self, e):
        """Export enhanced performance data with multiple formats"""
        try:
            if not any(self.metrics_history[key] for key in ['cpu', 'memory', 'disk', 'network']):
                logger.warning("⚠️ No data to export")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export CSV
            csv_filename = f"performance_data_{timestamp}.csv"
            self._export_csv(csv_filename)
            
            # Export JSON with metadata
            json_filename = f"performance_data_{timestamp}.json"
            self._export_json(json_filename)
            
            logger.info(f"✅ Performance data exported: {csv_filename}, {json_filename}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting performance data: {e}")
    
    def _export_csv(self, filename: str):
        """Export data as CSV"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Timestamp,CPU%,Memory%,Disk%,Network MB/s\n")
            
            timestamps = list(self.metrics_history['timestamps'])
            for i, ts in enumerate(timestamps):
                cpu = self.metrics_history['cpu'][i] if i < len(self.metrics_history['cpu']) else 0
                memory = self.metrics_history['memory'][i] if i < len(self.metrics_history['memory']) else 0
                disk = self.metrics_history['disk'][i] if i < len(self.metrics_history['disk']) else 0
                network = self.metrics_history['network'][i] if i < len(self.metrics_history['network']) else 0
                
                f.write(f"{ts.isoformat()},{cpu:.2f},{memory:.2f},{disk:.2f},{network:.2f}\n")
    
    def _export_json(self, filename: str):
        """Export data as JSON with metadata"""
        export_data = {
            'metadata': {
                'export_time': datetime.now().isoformat(),
                'time_range_minutes': self.settings.time_range_minutes,
                'update_interval': self.settings.update_interval,
                'chart_type': self.settings.chart_type,
                'thresholds': {k: asdict(v) for k, v in self.thresholds.items()},
                'data_points': len(self.metrics_history['timestamps'])
            },
            'metrics': {
                'timestamps': [ts.isoformat() for ts in self.metrics_history['timestamps']],
                'cpu': list(self.metrics_history['cpu']),
                'memory': list(self.metrics_history['memory']),
                'disk': list(self.metrics_history['disk']),
                'network': list(self.metrics_history['network'])
            },
            'alerts_history': list(self.alert_history)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
    
    def _load_chart_settings(self):
        """Load saved chart settings"""
        try:
            settings_file = "chart_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load settings
                if 'settings' in data:
                    settings_data = data['settings']
                    self.settings.time_range_minutes = settings_data.get('time_range_minutes', 5)
                    self.settings.update_interval = settings_data.get('update_interval', 5)
                    self.settings.chart_type = settings_data.get('chart_type', 'line')
                    self.settings.show_thresholds = settings_data.get('show_thresholds', True)
                
                # Load thresholds
                if 'thresholds' in data:
                    for metric, threshold_data in data['thresholds'].items():
                        if metric in self.thresholds:
                            self.thresholds[metric] = MetricThreshold(**threshold_data)
                
                logger.info("✅ Chart settings loaded")
        
        except Exception as e:
            logger.warning(f"⚠️ Could not load chart settings: {e}")
    
    def _save_chart_settings(self):
        """Save current chart settings"""
        try:
            settings_data = {
                'settings': asdict(self.settings),
                'thresholds': {k: asdict(v) for k, v in self.thresholds.items()}
            }
            
            with open("chart_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error saving chart settings: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics with enhanced statistics"""
        if not any(self.metrics_history[key] for key in ['cpu', 'memory', 'disk', 'network']):
            return {}
        
        stats = {}
        for metric in ['cpu', 'memory', 'disk', 'network']:
            data = list(self.metrics_history[metric])
            if data:
                stats[metric] = {
                    'current': data[-1],
                    'average': sum(data) / len(data),
                    'maximum': max(data),
                    'minimum': min(data),
                    'trend': 'up' if len(data) > 1 and data[-1] > data[-2] else 'down' if len(data) > 1 else 'stable'
                }
        
        return {
            'metrics': stats,
            'monitoring_active': self.monitoring_active,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'data_points': len(self.metrics_history['timestamps']),
            'active_alerts': len(self.active_alerts),
            'settings': asdict(self.settings)
        }