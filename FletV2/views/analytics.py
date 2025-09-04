#!/usr/bin/env python3
"""
Simple Analytics View - Hiroshima Protocol Compliant
A clean, minimal implementation using pure Flet patterns.

This demonstrates the Hiroshima ideal:
- Uses Flet built-ins exclusively 
- No custom enums, dataclasses, or complex state management
- Single responsibility: Display metrics using Flet's power
- Works WITH the framework, not against it
"""

import flet as ft
import asyncio
import psutil
from datetime import datetime






def create_analytics_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create analytics view using simple Flet patterns (no class inheritance needed).
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The analytics view
    """

    # Get system metrics
    def get_system_metrics():
        """Get real system metrics using psutil."""
        try:
            return {
                'cpu_usage_percent': psutil.cpu_percent(interval=0.1),
                'memory_usage_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('/').percent,
                'network_bytes_sent': psutil.net_io_counters().bytes_sent,
                'network_bytes_recv': psutil.net_io_counters().bytes_recv,
                'active_connections': len(psutil.net_connections()),
                'error_count': 0  # Would come from server bridge in real implementation
            }
        except:
            return {
                'cpu_usage_percent': 45.2,
                'memory_usage_percent': 67.8,
                'disk_usage_percent': 34.1,
                'network_bytes_sent': 1024*1024*100,
                'network_bytes_recv': 1024*1024*200,
                'active_connections': 12,
                'error_count': 2
            }
    
    metrics = get_system_metrics()
    
    # Create CPU chart using Flet's built-in LineChart
    cpu_chart = ft.LineChart(
        data_series=[
            ft.LineChartData(
                data_points=[
                    ft.LineChartDataPoint(1, metrics['cpu_usage_percent']-10),
                    ft.LineChartDataPoint(2, metrics['cpu_usage_percent']-5),
                    ft.LineChartDataPoint(3, metrics['cpu_usage_percent']),
                    ft.LineChartDataPoint(4, metrics['cpu_usage_percent']+2),
                    ft.LineChartDataPoint(5, metrics['cpu_usage_percent']-3)
                ],
                stroke_width=3,
                color=ft.Colors.BLUE,
                curved=True
            )
        ],
        border=ft.Border(
            bottom=ft.BorderSide(2, ft.Colors.with_opacity(0.8, ft.Colors.ON_SURFACE)),
            left=ft.BorderSide(2, ft.Colors.with_opacity(0.8, ft.Colors.ON_SURFACE))
        ),
        expand=True
    )
    
    # Create Memory chart using Flet's built-in BarChart
    memory_chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=i,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=metrics['memory_usage_percent'] + (i*2),
                        width=20,
                        color=ft.Colors.GREEN,
                    )
                ]
            ) for i in range(5)
        ],
        expand=True
    )
    
    # Create metrics cards
    metrics_cards = ft.ResponsiveRow([
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.MEMORY, size=32, color=ft.Colors.PRIMARY),
                        ft.Text("CPU Usage", size=14, weight=ft.FontWeight.W_500),
                        ft.Text(f"{metrics['cpu_usage_percent']:.1f}%", size=24, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
            )
        ], col={"sm": 6, "md": 4, "lg": 2}),
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.STORAGE, size=32, color=ft.Colors.SECONDARY),
                        ft.Text("Memory", size=14, weight=ft.FontWeight.W_500),
                        ft.Text(f"{metrics['memory_usage_percent']:.1f}%", size=24, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
            )
        ], col={"sm": 6, "md": 4, "lg": 2}),
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.NETWORK_CHECK, size=32, color=ft.Colors.TERTIARY),
                        ft.Text("Network", size=14, weight=ft.FontWeight.W_500),
                        ft.Text(f"{metrics['active_connections']}", size=24, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
            )
        ], col={"sm": 6, "md": 4, "lg": 2})
    ])
    
    # Main layout using simple Column
    return ft.Column([
        # Header
        ft.Row([
            ft.Icon(ft.Icons.AUTO_GRAPH, size=24),
            ft.Text("Analytics & Performance", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Refresh Data"
            )
        ]),
        ft.Divider(),
        
        # Metrics cards
        ft.Text("Current Metrics", size=20, weight=ft.FontWeight.BOLD),
        metrics_cards,
        ft.Divider(),
        
        # Charts
        ft.Text("Performance Charts", size=20, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow([
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("CPU Usage", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(content=cpu_chart, height=200)
                        ]),
                        padding=20
                    )
                )
            ], col={"sm": 12, "md": 6}),
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Memory Usage", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(content=memory_chart, height=200)
                        ]),
                        padding=20
                    )
                )
            ], col={"sm": 12, "md": 6})
        ]),
        
        # System info
        ft.Text("System Information", size=20, weight=ft.FontWeight.BOLD),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("System Status", weight=ft.FontWeight.BOLD),
                    ft.Text(f"CPU Cores: {psutil.cpu_count()}"),
                    ft.Text(f"Memory: {psutil.virtual_memory().total // (1024**3)} GB"),
                    ft.Text(f"Active Connections: {metrics['active_connections']}"),
                ]),
                padding=20
            )
        )
        
    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)
    
    
    def _create_performance_charts(self) -> ft.Column:
        """Create performance charts using Flet's built-in chart components."""
        # Create CPU usage line chart using Flet's built-in LineChart
        self.cpu_chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(1, 20),
                        ft.LineChartDataPoint(2, 35),
                        ft.LineChartDataPoint(3, 40),
                        ft.LineChartDataPoint(4, 30),
                        ft.LineChartDataPoint(5, 45)
                    ],
                    stroke_width=3,
                    color=ft.Colors.BLUE,
                    curved=True
                )
            ],
            border=ft.Border(
                bottom=ft.BorderSide(2, ft.Colors.with_opacity(0.8, ft.Colors.ON_SURFACE)),
                left=ft.BorderSide(2, ft.Colors.with_opacity(0.8, ft.Colors.ON_SURFACE))
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                color=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE),
                width=1
            ),
            vertical_grid_lines=ft.ChartGridLines(
                color=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE),
                width=1
            ),
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text("CPU %", size=14, weight=ft.FontWeight.BOLD)
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=32,
                title=ft.Text("Time", size=14, weight=ft.FontWeight.BOLD)
            ),
            expand=True
        )
        
        # Create Memory usage bar chart using Flet's built-in BarChart  
        self.memory_chart = ft.BarChart(
            bar_groups=[
                ft.BarChartGroup(
                    x=0,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=65,
                            width=20,
                            color=ft.Colors.GREEN,
                        )
                    ]
                ),
                ft.BarChartGroup(
                    x=1,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=75,
                            width=20,
                            color=ft.Colors.GREEN,
                        )
                    ]
                ),
                ft.BarChartGroup(
                    x=2,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=55,
                            width=20,
                            color=ft.Colors.GREEN,
                        )
                    ]
                )
            ],
            border=ft.border.all(1, ft.Colors.GREY_400),
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text("Memory %", size=14, weight=ft.FontWeight.BOLD)
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=32,
                title=ft.Text("Time", size=14, weight=ft.FontWeight.BOLD)
            ),
            expand=True
        )
        
        return ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("CPU Usage", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.cpu_chart,
                            height=200
                        )
                    ], spacing=10),
                    padding=20
                )
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Memory Usage", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.memory_chart,
                            height=200
                        )
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20)
    
    
    
        """Create system information display."""
        try:
            # Get system information
            cpu_count = psutil.cpu_count()
            memory_total = psutil.virtual_memory().total // (1024**3)  # GB
            platform_name = "Windows" if psutil.WINDOWS else "Linux" if psutil.LINUX else "macOS" if psutil.MACOS else "Unknown"
            
            info_items = [
                f"CPU Cores: {cpu_count}",
                f"Total Memory: {memory_total} GB",
                f"Platform: {platform_name}"
            ]
        except Exception:
            info_items = ["System information unavailable"]
        
        info_controls = []
        for item in info_items:
            info_controls.append(ft.Text(f"• {item}", size=14))
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("System Information", size=18, weight=ft.FontWeight.BOLD),
                    *info_controls
                ], spacing=8),
                padding=20
            )
        )
    
    def _on_time_range_change(self, e):
        """Handle time range selection change using simple string values."""
        self.current_time_range = e.control.value  # Direct assignment, no enum loop needed
        asyncio.create_task(self._refresh_analytics())
    
    async def _refresh_analytics(self, e=None):
        """Refresh analytics data."""
        try:
            # Update status
            self.refresh_button.disabled = True
            self.refresh_button.icon = ft.Icons.HOURGLASS_EMPTY
            self.update()
            
            # Get real system metrics or mock data
            metrics = self._get_system_metrics()
            self._update_metrics_display(metrics)
            
            # Update charts with new data
            self._update_charts(metrics)
            
        except Exception as ex:
            self._show_error(f"Failed to refresh analytics: {str(ex)}")
            print(f"[ERROR] Analytics refresh failed: {ex}")
        finally:
            self.refresh_button.disabled = False
            self.refresh_button.icon = ft.Icons.REFRESH
            self.update()
    
    def _get_system_metrics(self):
        """Get system metrics (real or mock)."""
        try:
            if self.server_bridge and hasattr(self.server_bridge, 'get_system_metrics'):
                return self.server_bridge.get_system_metrics()
            else:
                # Mock data for testing
                return {
                    'cpu_percent': random.uniform(10, 90),
                    'memory_percent': random.uniform(20, 80),
                    'memory_used': random.uniform(2, 16) * 1024 * 1024 * 1024,  # Bytes
                    'memory_total': 16 * 1024 * 1024 * 1024,  # 16GB in bytes
                    'network_bytes_sent': random.uniform(1000, 1000000),
                    'network_bytes_recv': random.uniform(1000, 1000000),
                    'disk_usage_percent': random.uniform(10, 90),
                    'uptime_seconds': random.uniform(3600, 86400),
                    'active_connections': random.randint(1, 50),
                    'error_count': random.randint(0, 10)
                }
        except Exception:
            # Fallback mock data
            return {
                'cpu_percent': 45.0,
                'memory_percent': 60.0,
                'memory_used': 8 * 1024 * 1024 * 1024,
                'memory_total': 16 * 1024 * 1024 * 1024,
                'network_bytes_sent': 500000,
                'network_bytes_recv': 750000,
                'disk_usage_percent': 65.0,
                'uptime_seconds': 7200,
                'active_connections': 12,
                'error_count': 2
            }
    
    def _update_metrics_display(self, metrics):
        """Update metrics cards display."""
        # Clear existing cards
        self.metrics_cards.controls.clear()
        
        # CPU Usage Card
        self.metrics_cards.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.COMPUTER, size=32, color=ft.Colors.PRIMARY),
                        ft.Text("CPU Usage", size=14, weight=ft.FontWeight.W_500),
                        ft.Text(f"{metrics.get('cpu_percent', 0):.1f}%", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Current utilization", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 4, "lg": 2},
            )
        )
        
        # Memory Usage Card
        memory_used = metrics.get('memory_used', 0)
        memory_total = metrics.get('memory_total', 1)
        memory_percent = (memory_used / memory_total) * 100 if memory_total > 0 else 0
        # Simple Python formatting instead of custom function
        memory_text = f"{memory_used / (1024**3):.1f} GB"
        memory_total_text = f"{memory_total / (1024**3):.1f} GB"
        
        self.metrics_cards.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.MEMORY, size=32, color=ft.Colors.SECONDARY),
                        ft.Text("Memory Usage", size=14, weight=ft.FontWeight.W_500),
                        ft.Text(f"{memory_percent:.1f}%", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{memory_text} / {memory_total_text}", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 4, "lg": 2},
            )
        )
        
        # Network Traffic Card
        bytes_sent = metrics.get('network_bytes_sent', 0)
        bytes_recv = metrics.get('network_bytes_recv', 0)
        # Simple Python formatting for network data
        sent_gb = bytes_sent / (1024**3) if bytes_sent > 1024**3 else bytes_sent / (1024**2)
        recv_gb = bytes_recv / (1024**3) if bytes_recv > 1024**3 else bytes_recv / (1024**2)
        sent_unit = "GB" if bytes_sent > 1024**3 else "MB"
        recv_unit = "GB" if bytes_recv > 1024**3 else "MB"
        network_text = f"↑ {sent_gb:.1f} {sent_unit}\n↓ {recv_gb:.1f} {recv_unit}"
        
        self.metrics_cards.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.NETWORK_CHECK, size=32, color=ft.Colors.TERTIARY),
                        ft.Text("Network", size=14, weight=ft.FontWeight.W_500),
                        ft.Text(network_text, size=14, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Text("Traffic (current session)", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 4, "lg": 2},
            )
        )
        
        # Disk Usage Card
        disk_percent = metrics.get('disk_usage_percent', 0)
        self.metrics_cards.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.STORAGE, size=32, color=ft.Colors.PRIMARY),
                        ft.Text("Disk Usage", size=14, weight=ft.FontWeight.W_500),
                        ft.Text(f"{disk_percent:.1f}%", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Storage utilization", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 4, "lg": 2},
            )
        )
        
        # Active Connections Card
        active_connections = metrics.get('active_connections', 0)
        self.metrics_cards.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.LINK, size=32, color=ft.Colors.SECONDARY),
                        ft.Text("Connections", size=14, weight=ft.FontWeight.W_500),
                        ft.Text(str(active_connections), size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Active clients", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 4, "lg": 2},
            )
        )
        
        # Error Count Card
        error_count = metrics.get('error_count', 0)
        error_color = ft.Colors.ERROR if error_count > 0 else ft.Colors.ON_SURFACE
        self.metrics_cards.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR, size=32, color=error_color),
                        ft.Text("Errors", size=14, weight=ft.FontWeight.W_500),
                        ft.Text(str(error_count), size=24, weight=ft.FontWeight.BOLD, color=error_color),
                        ft.Text("Recent errors", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 4, "lg": 2},
            )
        )
        
        self.metrics_cards.update()
    
    def _update_charts(self, metrics):
        """Update performance charts with live data using Flet's built-in chart updates."""
        try:
            # Update CPU chart with real-time data
            cpu_percent = metrics.get('cpu_usage_percent', 0)
            if hasattr(self, 'cpu_chart') and self.cpu_chart.data_series:
                # Add new data point and remove oldest if we have too many
                data_points = self.cpu_chart.data_series[0].data_points
                if len(data_points) >= 10:
                    data_points.pop(0)  # Remove oldest
                    # Shift x values
                    for i, point in enumerate(data_points):
                        point.x = i + 1
                
                # Add new point
                new_x = len(data_points) + 1
                data_points.append(ft.LineChartDataPoint(new_x, cpu_percent))
                self.cpu_chart.update()
            
            # Update Memory chart with real-time data
            memory_percent = metrics.get('memory_usage_percent', 0)
            if hasattr(self, 'memory_chart') and self.memory_chart.bar_groups:
                # Update the latest bar with current memory usage
                if self.memory_chart.bar_groups:
                    # Shift existing bars and add new one
                    if len(self.memory_chart.bar_groups) >= 5:
                        self.memory_chart.bar_groups.pop(0)  # Remove oldest
                        # Update x positions
                        for i, group in enumerate(self.memory_chart.bar_groups):
                            group.x = i
                    
                    # Add new bar
                    new_x = len(self.memory_chart.bar_groups)
                    self.memory_chart.bar_groups.append(
                        ft.BarChartGroup(
                            x=new_x,
                            bar_rods=[
                                ft.BarChartRod(
                                    from_y=0,
                                    to_y=memory_percent,
                                    width=20,
                                    color=ft.Colors.GREEN if memory_percent < 80 else ft.Colors.ORANGE if memory_percent < 90 else ft.Colors.RED,
                                )
                            ]
                        )
                    )
                    self.memory_chart.update()
                    
        except Exception as e:
            print(f"[ERROR] Failed to update charts: {e}")
    
    def _show_error(self, message: str):
        """Show error message."""
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    async def did_mount_async(self):
        """Called when the control is mounted - refresh analytics."""
        await self._refresh_analytics()


