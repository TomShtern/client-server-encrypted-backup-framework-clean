#!/usr/bin/env python3
"""
UI Widgets - Charts

Purpose: Performance monitoring charts with real-time updates
Logic: Metrics calculation, data aggregation, threshold monitoring
UI: Chart rendering, animations, Material Design 3 styling
"""

import flet as ft
import asyncio
import time
import json
import os
import psutil
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
    Advanced performance monitoring with interactive controls and responsive design.
    Enhanced charts with real-time alerts, time range controls, and export features.
    """
    
    def __init__(self, server_bridge, page):
        """Initialize with real server bridge for metrics"""
        self.server_bridge = server_bridge
        self.page = page
        
        # Chart settings and configuration
        self.settings = ChartSettings()
        
        # Performance thresholds
        self.thresholds = {
            'cpu': MetricThreshold(warning=70.0, critical=90.0),
            'memory': MetricThreshold(warning=80.0, critical=95.0),
            'disk': MetricThreshold(warning=85.0, critical=95.0),
            'network': MetricThreshold(warning=50.0, critical=80.0)
        }
        
        # Real-time data storage (bounded queues)
        max_points = 300  # Store up to 300 data points
        self.metrics_history = {
            'timestamps': deque(maxlen=max_points),
            'cpu': deque(maxlen=max_points),
            'memory': deque(maxlen=max_points),
            'disk': deque(maxlen=max_points),
            'network': deque(maxlen=max_points)
        }
        
        # Monitoring state
        self.monitoring_active = False
        self.last_update = None
        self.active_alerts = []
        
        # UI components
        self.stat_displays = {}
        self.chart_containers = {}
        self.alert_panel = None
        self.control_panel = None
        
        logger.info("✅ Enhanced performance charts initialized")
    
    def build(self) -> ft.Container:
        """Build the enhanced performance monitoring dashboard with responsive design"""
        
        # Main layout with responsive rows
        dashboard = ft.Container(
            content=ft.Column([
                # Control panel
                self._create_control_panel(),
                
                # Alert panel (shows threshold violations)
                self._create_alert_panel(),
                
                # Metrics overview cards - responsive grid
                ft.ResponsiveRow([
                    ft.Container(
                        content=self._create_metrics_grid(),
                        col={"sm": 12, "md": 12, "lg": 12},
                        expand=True
                    )
                ], expand=True),
                
                # Charts section - responsive grid
                ft.ResponsiveRow([
                    ft.Container(
                        content=self._create_charts_section(),
                        col={"sm": 12, "md": 12, "lg": 12},
                        expand=True
                    )
                ], expand=True)
                
            ], spacing=10, expand=True),
            padding=ft.padding.all(10),
            expand=True
        )
        
        return dashboard
    
    def _create_control_panel(self) -> ft.Container:
        """Create responsive control panel with monitoring controls"""
        
        start_stop_button = ft.ElevatedButton(
            text="Start Monitoring",
            icon=ft.Icons.PLAY_ARROW,
            bgcolor=ft.Colors.GREEN,
            on_click=self._toggle_monitoring,
            expand=True
        )
        
        # Time range selector - responsive
        time_range_dropdown = ft.Dropdown(
            label="Time Range",
            options=[
                ft.dropdown.Option("1", "1 minute"),
                ft.dropdown.Option("5", "5 minutes"), 
                ft.dropdown.Option("15", "15 minutes"),
                ft.dropdown.Option("30", "30 minutes"),
                ft.dropdown.Option("60", "1 hour")
            ],
            value=str(self.settings.time_range_minutes),
            on_change=self._on_time_range_changed,
            expand=True
        )
        
        # Update interval slider - responsive
        update_interval_slider = ft.Container(
            content=ft.Column([
                ft.Text(f"Update: {self.settings.update_interval}s", size=12),
                ft.Slider(
                    min=1,
                    max=30,
                    value=self.settings.update_interval,
                    divisions=29,
                    on_change=self._on_update_interval_changed
                )
            ], spacing=2),
            expand=True
        )
        
        # Chart type selector - responsive
        chart_type_segmented = ft.Dropdown(
            label="Chart Type",
            options=[
                ft.dropdown.Option("line", "Line Chart"),
                ft.dropdown.Option("bar", "Bar Chart"),
                ft.dropdown.Option("area", "Area Chart")
            ],
            value=self.settings.chart_type,
            on_change=self._on_chart_type_changed,
            expand=True
        )
        
        threshold_switch = ft.Switch(
            label="Show Thresholds",
            value=self.settings.show_thresholds,
            on_change=self._on_threshold_toggle
        )
        
        # Responsive control panel layout
        controls = ft.ResponsiveRow([
            ft.Container(
                content=start_stop_button,
                col={"sm": 12, "md": 6, "lg": 2},
                expand=True
            ),
            ft.Container(
                content=time_range_dropdown,
                col={"sm": 12, "md": 6, "lg": 2},
                expand=True
            ),
            ft.Container(
                content=update_interval_slider,
                col={"sm": 12, "md": 6, "lg": 2},
                expand=True
            ),
            ft.Container(
                content=chart_type_segmented,
                col={"sm": 12, "md": 6, "lg": 2},
                expand=True
            ),
            ft.Container(
                content=threshold_switch,
                col={"sm": 12, "md": 6, "lg": 2},
                alignment=ft.alignment.center,
                expand=True
            ),
            ft.Container(
                content=ft.ElevatedButton(
                    text="Reset View",
                    icon=ft.Icons.REFRESH,
                    on_click=self._reset_charts
                ),
                col={"sm": 12, "md": 6, "lg": 2},
                expand=True
            )
        ], expand=True)
        
        return ft.Container(
            content=controls,
            bgcolor=ft.Colors.SURFACE_VARIANT,
            padding=ft.padding.all(10),
            border_radius=8,
            expand=True
        )
    
    def _create_alert_panel(self) -> ft.Container:
        """Create alert panel for threshold violations with responsive design"""
        self.alert_panel = ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS, color=ft.Colors.AMBER),
                        ft.Text("No active alerts", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                    ], spacing=8),
                    col={"sm": 12, "md": 8},
                    expand=True
                ),
                ft.Container(
                    content=ft.TextButton("Clear All", on_click=self._clear_alerts, visible=False),
                    col={"sm": 12, "md": 4},
                    alignment=ft.alignment.center_right,
                    expand=True
                )
            ], expand=True),
            bgcolor=ft.Colors.SURFACE,
            padding=ft.padding.all(8),
            border_radius=4,
            height=40,
            expand=True
        )
        return self.alert_panel
    
    def _create_metrics_grid(self) -> ft.ResponsiveRow:
        """Create responsive metrics display grid"""
        self.stat_displays = {
            'cpu': self._create_metric_card("CPU", ft.Icons.MEMORY, ft.Colors.BLUE),
            'memory': self._create_metric_card("Memory", ft.Icons.STORAGE, ft.Colors.GREEN),
            'disk': self._create_metric_card("Disk", ft.Icons.STORAGE, ft.Colors.ORANGE),
            'network': self._create_metric_card("Network", ft.Icons.NETWORK_CHECK, ft.Colors.PURPLE)
        }
        
        return ft.ResponsiveRow([
            ft.Container(
                content=self.stat_displays['cpu'],
                col={"sm": 12, "md": 6, "lg": 3},
                expand=True
            ),
            ft.Container(
                content=self.stat_displays['memory'],
                col={"sm": 12, "md": 6, "lg": 3},
                expand=True
            ),
            ft.Container(
                content=self.stat_displays['disk'],
                col={"sm": 12, "md": 6, "lg": 3},
                expand=True
            ),
            ft.Container(
                content=self.stat_displays['network'],
                col={"sm": 12, "md": 6, "lg": 3},
                expand=True
            )
        ], spacing=10, expand=True)
    
    def _create_metric_card(self, title: str, icon, color) -> ft.Card:
        """Create responsive enhanced metric display card"""
        current_text = ft.Text("--", style=ft.TextThemeStyle.HEADLINE_MEDIUM, 
                              weight=ft.FontWeight.BOLD, color=color)
        avg_text = ft.Text("Avg: --", style=ft.TextThemeStyle.BODY_SMALL, 
                          color=ft.Colors.ON_SURFACE_VARIANT)
        max_text = ft.Text("Max: --", style=ft.TextThemeStyle.BODY_SMALL, 
                          color=ft.Colors.ON_SURFACE_VARIANT)
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
                        ft.Container(expand=True),
                        status_indicator
                    ]),
                    ft.Text(title, style=ft.TextThemeStyle.LABEL_LARGE, 
                           weight=ft.FontWeight.W_500),
                    current_text,
                    avg_text,
                    max_text
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.START),
                padding=ft.padding.all(12),
                expand=True
            ),
            expand=True
        )
    
    def _create_charts_section(self) -> ft.ResponsiveRow:
        """Create responsive charts display section"""
        self.chart_containers = {
            'cpu': self._create_enhanced_chart("CPU Usage %", ft.Colors.BLUE),
            'memory': self._create_enhanced_chart("Memory Usage %", ft.Colors.GREEN),
            'disk': self._create_enhanced_chart("Disk Usage %", ft.Colors.ORANGE),
            'network': self._create_enhanced_chart("Network Activity (MB/s)", ft.Colors.PURPLE)
        }
        
        return ft.ResponsiveRow([
            ft.Container(
                content=self.chart_containers['cpu'],
                col={"sm": 12, "md": 6, "lg": 6},
                expand=True
            ),
            ft.Container(
                content=self.chart_containers['memory'],
                col={"sm": 12, "md": 6, "lg": 6},
                expand=True
            ),
            ft.Container(
                content=self.chart_containers['disk'],
                col={"sm": 12, "md": 6, "lg": 6},
                expand=True
            ),
            ft.Container(
                content=self.chart_containers['network'],
                col={"sm": 12, "md": 6, "lg": 6},
                expand=True
            )
        ], spacing=10, expand=True)
    
    def _create_enhanced_chart(self, title: str, color) -> ft.Container:
        """Create enhanced chart container with interactive features and responsive design"""
        chart_display = ft.Container(
            content=ft.Column([
                ft.Text("Start monitoring to see live data", 
                       style=ft.TextThemeStyle.BODY_MEDIUM, 
                       color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Container(height=100, expand=True)  # Chart area
            ], expand=True),
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=4,
            padding=ft.padding.all(8),
            expand=True
        )
        
        return ft.Container(
            content=ft.Column([
                ft.ResponsiveRow([
                    ft.Container(
                        content=ft.Text(title, style=ft.TextThemeStyle.TITLE_MEDIUM, 
                                       weight=ft.FontWeight.BOLD),
                        col={"sm": 12, "md": 8},
                        expand=True
                    ),
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.FULLSCREEN,
                            tooltip="Full Screen",
                            on_click=lambda e, t=title: self._show_fullscreen_chart(t)
                        ),
                        col={"sm": 12, "md": 4},
                        alignment=ft.alignment.center_right,
                        expand=True
                    )
                ], expand=True),
                chart_display
            ], expand=True),
            padding=ft.padding.all(10),
            expand=True
        )
    
    def _toggle_monitoring(self, e):
        """Toggle enhanced monitoring with better state management"""
        if self.monitoring_active:
            self._stop_monitoring()
            e.control.text = "Start Monitoring"
            e.control.icon = ft.Icons.PLAY_ARROW
            e.control.bgcolor = ft.Colors.GREEN
        else:
            self._start_monitoring()
            e.control.text = "Stop Monitoring"
            e.control.icon = ft.Icons.STOP
            e.control.bgcolor = ft.Colors.RED_ACCENT
        
        e.control.update()
    
    def _start_monitoring(self):
        """Start enhanced monitoring with alert system"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.active_alerts.clear()
        # Use page's run_task to schedule the async monitoring loop properly
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
                metrics = self._get_system_metrics()
                
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
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get real system metrics using psutil"""
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Get network stats (simplified)
            net_io = psutil.net_io_counters()
            
            return {
                'available': True,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'network_bytes_sent': net_io.bytes_sent if net_io else 0,
                'network_bytes_recv': net_io.bytes_recv if net_io else 0
            }
        except Exception as e:
            logger.warning(f"⚠️ Could not get system metrics: {e}")
            return {'available': False}
    
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
            
            # Create simple text-based chart for now (can be enhanced with actual chart library)
            if len(data) > 0:
                latest_value = data[-1]
                trend = "↑" if len(data) > 1 and data[-1] > data[-2] else "↓" if len(data) > 1 and data[-1] < data[-2] else "→"
                
                # Create a simple progress bar representation
                progress_bar = ft.ProgressBar(
                    value=min(latest_value / 100.0, 1.0),
                    height=20,
                    border_radius=4
                )
                
                chart_content = ft.Column([
                    ft.Row([
                        ft.Text(f"Current: {latest_value:.1f}% {trend}", 
                               style=ft.TextThemeStyle.BODY_MEDIUM),
                        ft.Container(expand=True),
                        ft.Text(f"Points: {len(data)}", 
                               style=ft.TextThemeStyle.BODY_SMALL,
                               color=ft.Colors.ON_SURFACE_VARIANT)
                    ]),
                    progress_bar,
                    ft.Text(f"Range: {min(data):.1f}% - {max(data):.1f}%",
                           style=ft.TextThemeStyle.BODY_SMALL,
                           color=ft.Colors.ON_SURFACE_VARIANT)
                ], spacing=5)
                
                chart_display.content = chart_content
                chart_display.update()
        except Exception as e:
            logger.error(f"❌ Error updating chart for {metric_name}: {e}")
    
    def _update_alert_panel(self, alerts: List[Dict]):
        """Update alert panel with current alerts"""
        if not self.alert_panel:
            return
            
        panel_content = self.alert_panel.content.controls[0]  # ResponsiveRow
        alert_container = panel_content.controls[0].content  # First container with alerts
        clear_button_container = panel_content.controls[1].content  # Second container with clear button
        
        if alerts:
            # Show alerts
            alert_texts = []
            for alert in alerts:
                color = ft.Colors.RED if alert['level'] == 'critical' else ft.Colors.AMBER
                icon = ft.Icons.ERROR if alert['level'] == 'critical' else ft.Icons.WARNING
                alert_texts.append(
                    ft.Row([
                        ft.Icon(icon, color=color, size=16),
                        ft.Text(alert['message'], size=12, color=color)
                    ], spacing=4)
                )
            
            alert_container.controls = alert_texts
            clear_button_container.visible = True
            self.alert_panel.bgcolor = ft.Colors.ERROR_CONTAINER if any(a['level'] == 'critical' for a in alerts) else ft.Colors.SURFACE_VARIANT
        else:
            # No alerts
            alert_container.controls = [
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=16),
                    ft.Text("All systems normal", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                ], spacing=4)
            ]
            clear_button_container.visible = False
            self.alert_panel.bgcolor = ft.Colors.SURFACE
        
        self.alert_panel.update()
    
    def _clear_alerts(self, e):
        """Clear all active alerts"""
        self.active_alerts.clear()
        self._update_alert_panel([])
    
    def _reset_charts(self, e):
        """Reset all charts and clear data"""
        # Clear all historical data
        for key in self.metrics_history:
            self.metrics_history[key].clear()
        
        # Clear alerts
        self.active_alerts.clear()
        self._update_alert_panel([])
        
        # Reset chart displays
        for container in self.chart_containers.values():
            chart_display = container.content.controls[1]
            chart_display.content = ft.Column([
                ft.Text("Start monitoring to see live data", 
                       style=ft.TextThemeStyle.BODY_MEDIUM, 
                       color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Container(height=100, expand=True)
            ], expand=True)
            chart_display.update()
    
    def _show_fullscreen_chart(self, title: str):
        """Show fullscreen chart (placeholder implementation)"""
        # Placeholder for fullscreen chart functionality
        pass
    
    def _on_time_range_changed(self, e):
        """Handle time range change"""
        self.settings.time_range_minutes = int(e.control.value)
        logger.info(f"Time range changed to {self.settings.time_range_minutes} minutes")
    
    def _on_update_interval_changed(self, e):
        """Handle update interval change"""
        self.settings.update_interval = int(e.control.value)
        # Update the label
        slider_container = e.control.parent
        slider_container.controls[0].value = f"Update: {self.settings.update_interval}s"
        slider_container.update()
    
    def _on_chart_type_changed(self, e):
        """Handle chart type change"""
        self.settings.chart_type = e.control.value
        logger.info(f"Chart type changed to {self.settings.chart_type}")
    
    def _on_threshold_toggle(self, e):
        """Handle threshold display toggle"""
        self.settings.show_thresholds = e.control.value
        logger.info(f"Threshold display toggled to {self.settings.show_thresholds}")


# Enhanced Chart Components
# Custom Material Design 3 charts and data visualizations

class EnhancedBarChart(ft.Container):
    """Enhanced bar chart using ft.BarChart for real visualization."""
    
    def __init__(self,
                 data: List[Dict[str, Union[str, int, float]]],
                 x_field: str,
                 y_field: str,
                 title: Optional[str] = None,
                 bar_color: str = ft.colors.PRIMARY,
                 **kwargs):
        super().__init__(**kwargs)
        
        self.data = data
        self.x_field = x_field
        self.y_field = y_field
        self.title = title
        self.bar_color = bar_color
        
        self.content = self._build_chart()
    
    def _build_chart(self) -> ft.Control:
        """Build the bar chart using ft.BarChart."""
        if not self.data:
            return ft.Text("No data available for chart.")

        max_y = max(item[self.y_field] for item in self.data) if self.data else 1

        bar_groups = []
        for i, item in enumerate(self.data):
            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=item[self.y_field],
                            width=20,
                            color=self.bar_color,
                            tooltip=f"{item[self.x_field]}: {item[self.y_field]}",
                            border_radius=4,
                        ),
                    ],
                )
            )

        chart = ft.BarChart(
            bar_groups=bar_groups,
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=i, label=ft.Text(str(item[self.x_field]), size=10)) for i, item in enumerate(self.data)
                ],
            ),
            left_axis=ft.ChartAxis(
                labels_size=40,
            ),
            expand=True,
        )

        return ft.Column([
            ft.Text(self.title, style=ft.TextThemeStyle.TITLE_LARGE) if self.title else ft.Container(),
            chart,
        ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)


class EnhancedLineChart(ft.Container):
    """Enhanced line chart using ft.LineChart for real visualization."""
    
    def __init__(self,
                 data: List[Dict[str, Union[str, int, float]]],
                 x_field: str,
                 y_field: str,
                 title: Optional[str] = None,
                 line_color: str = ft.colors.PRIMARY,
                 **kwargs):
        super().__init__(**kwargs)
        
        self.data = data
        self.x_field = x_field
        self.y_field = y_field
        self.title = title
        self.line_color = line_color
        
        self.content = self._build_chart()
    
    def _build_chart(self) -> ft.Control:
        """Build the line chart using ft.LineChart."""
        if not self.data:
            return ft.Text("No data available for chart.")

        data_points = [
            ft.LineChartDataPoint(i, item[self.y_field], tooltip=f"{item[self.x_field]}: {item[self.y_field]}")
            for i, item in enumerate(self.data)
        ]

        line_data = [
            ft.LineChartData(
                data_points=data_points,
                color=self.line_color,
                stroke_width=3,
                curved=True,
                stroke_cap_round=True,
            )
        ]

        chart = ft.LineChart(
            data_series=line_data,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            horizontal_grid_lines=ft.ChartGridLines(interval=10, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
            vertical_grid_lines=ft.ChartGridLines(interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
            expand=True,
        )

        return ft.Column([
            ft.Text(self.title, style=ft.TextThemeStyle.TITLE_LARGE) if self.title else ft.Container(),
            chart,
        ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)


class EnhancedPieChart(ft.Container):
    """Enhanced pie chart with animations and interactions"""
    
    def __init__(self,
                 data: List[Dict[str, Union[str, int, float]]],
                 label_field: str,
                 value_field: str,
                 title: Optional[str] = None,
                 animate_duration: int = 400,
                 colors: Optional[List[str]] = None,
                 show_labels: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        
        self.data = data
        self.label_field = label_field
        self.value_field = value_field
        self.title = title
        self.animate_duration = animate_duration
        self.show_labels = show_labels
        
        self.colors = colors or [
            ft.Colors.PRIMARY,
            ft.Colors.SECONDARY,
            ft.Colors.TERTIARY,
            ft.Colors.ERROR,
            ft.Colors.OUTLINE,
            ft.Colors.ON_SURFACE_VARIANT
        ]
        
        self.total = sum(item[self.value_field] for item in data) if data else 1
        self.chart_size = 200
        
        self.content = self._build_chart()
        self.animate_scale = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
    
    def _build_chart(self) -> ft.Control:
        """Build the pie chart (placeholder)."""
        # Flet does not have a native Pie chart, this remains a placeholder.
        # A more advanced implementation would use ft.Canvas or a custom control.
        
        if not self.data:
            return ft.Text("No data for pie chart.")

        legend_items = []
        for i, item in enumerate(self.data):
            label = str(item[self.label_field])
            color = self.colors[i % len(self.colors)]
            legend_items.append(
                ft.Row([
                    ft.Container(width=12, height=12, bgcolor=color, border_radius=6),
                    ft.Text(label, size=12)
                ], spacing=8)
            )
        
        legend = ft.Column(legend_items, spacing=8)

        placeholder = ft.Container(
            width=self.chart_size, 
            height=self.chart_size, 
            content=ft.Icon(ft.icons.PIE_CHART, size=100, color=ft.colors.OUTLINE),
            alignment=ft.alignment.center
        )

        chart_row = ft.Row([
            placeholder,
            legend
        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        
        return ft.Column([
            ft.Text(self.title, style=ft.TextThemeStyle.TITLE_LARGE) if self.title else ft.Container(),
            chart_row
        ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)


# Factory function for easy chart creation
def create_enhanced_performance_charts(server_bridge, page: ft.Page) -> EnhancedPerformanceCharts:
    """Create enhanced performance monitoring charts"""
    return EnhancedPerformanceCharts(server_bridge, page)


# Factory functions for easy chart creation
def create_bar_chart(data: List[Dict[str, Union[str, int, float]]],
                    x_field: str,
                    y_field: str,
                    title: Optional[str] = None,
                    **kwargs) -> EnhancedBarChart:
    return EnhancedBarChart(data=data, x_field=x_field, y_field=y_field, title=title, **kwargs)

def create_line_chart(data: List[Dict[str, Union[str, int, float]]],
                     x_field: str,
                     y_field: str,
                     title: Optional[str] = None,
                     **kwargs) -> EnhancedLineChart:
    return EnhancedLineChart(data=data, x_field=x_field, y_field=y_field, title=title, **kwargs)

def create_pie_chart(data: List[Dict[str, Union[str, int, float]]],
                    label_field: str,
                    value_field: str,
                    title: Optional[str] = None,
                     **kwargs) -> EnhancedPieChart:
    return EnhancedPieChart(data=data, label_field=label_field, value_field=value_field, title=title, **kwargs)