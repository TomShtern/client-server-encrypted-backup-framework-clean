#!/usr/bin/env python3
"""
Real-time Charts Component
Material Design 3 component with live updating charts for server metrics.
"""

import flet as ft
from typing import List, Dict, Optional
import asyncio
import random
from flet_server_gui.components.charts import (
    EnhancedBarChart,
    EnhancedLineChart,
    EnhancedPieChart
)
from flet_server_gui.components.enhanced_components import EnhancedCard


class RealTimeCharts(EnhancedCard):
    """Real-time charts component with live updating data"""
    
    def __init__(self, 
                 title: str = "Server Metrics",
                 animate_duration: int = 300,
                 **kwargs):
        self.title = title
        self.chart_data = {
            "cpu": [],
            "memory": [],
            "network": [],
            "clients": []
        }
        self.is_updating = False
        
        # Create the main content
        content = self._build_content()
        
        super().__init__(
            content=content,
            animate_duration=animate_duration,
            **kwargs
        )
    
    def _build_content(self) -> ft.Control:
        """Build the real-time charts content"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.AUTO_GRAPH, size=24),
            ft.Text(self.title, style=ft.TextThemeStyle.TITLE_LARGE),
        ], spacing=12)
        
        # Initialize chart data
        self._initialize_chart_data()
        
        # Create charts
        self.cpu_chart = EnhancedLineChart(
            data=self.chart_data["cpu"],
            x_field="time",
            y_field="value",
            title="CPU Usage (%)",
            line_color=ft.Colors.PRIMARY,
            point_color=ft.Colors.SECONDARY,
            animate_duration=500,
            width=300,
            height=150
        )
        
        self.memory_chart = EnhancedLineChart(
            data=self.chart_data["memory"],
            x_field="time",
            y_field="value",
            title="Memory Usage (%)",
            line_color=ft.Colors.TERTIARY,
            point_color=ft.Colors.ERROR,
            animate_duration=500,
            width=300,
            height=150
        )
        
        self.clients_chart = EnhancedBarChart(
            data=self.chart_data["clients"],
            x_field="time",
            y_field="value",
            title="Active Clients",
            bar_color=ft.Colors.SECONDARY,
            animate_duration=300,
            bar_width=30,
            width=300,
            height=150
        )
        
        # Charts grid
        charts_grid = ft.ResponsiveRow([
            ft.Column([
                self.cpu_chart
            ], col={"sm": 12, "md": 4}),
            ft.Column([
                self.memory_chart
            ], col={"sm": 12, "md": 4}),
            ft.Column([
                self.clients_chart
            ], col={"sm": 12, "md": 4}),
        ], spacing=20)
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                charts_grid
            ], spacing=16),
            padding=ft.padding.all(20)
        )
    
    def _initialize_chart_data(self):
        """Initialize chart data with some sample data"""
        import datetime
        
        # Generate initial data points
        for i in range(10):
            timestamp = (datetime.datetime.now() - datetime.timedelta(minutes=(9-i)*5)).strftime("%H:%M")
            
            self.chart_data["cpu"].append({
                "time": timestamp,
                "value": random.randint(10, 80)
            })
            
            self.chart_data["memory"].append({
                "time": timestamp,
                "value": random.randint(30, 90)
            })
            
            self.chart_data["clients"].append({
                "time": timestamp,
                "value": random.randint(0, 15)
            })
    
    async def update_charts(self):
        """Update charts with new data points"""
        if self.is_updating:
            return
            
        self.is_updating = True
        
        try:
            import datetime
            import random
            
            # Generate new data points
            timestamp = datetime.datetime.now().strftime("%H:%M")
            
            new_cpu = {
                "time": timestamp,
                "value": random.randint(10, 80)
            }
            
            new_memory = {
                "time": timestamp,
                "value": random.randint(30, 90)
            }
            
            new_clients = {
                "time": timestamp,
                "value": random.randint(0, 15)
            }
            
            # Add new data points
            self.chart_data["cpu"].append(new_cpu)
            self.chart_data["memory"].append(new_memory)
            self.chart_data["clients"].append(new_clients)
            
            # Keep only last 10 data points
            if len(self.chart_data["cpu"]) > 10:
                self.chart_data["cpu"].pop(0)
                self.chart_data["memory"].pop(0)
                self.chart_data["clients"].pop(0)
            
            # Rebuild charts with updated data
            self._rebuild_charts()
            
        finally:
            self.is_updating = False
    
    def _rebuild_charts(self):
        """Rebuild charts with updated data"""
        # Update CPU chart
        self.cpu_chart.data = self.chart_data["cpu"]
        new_cpu_content = self.cpu_chart._build_chart()
        self.cpu_chart.content = new_cpu_content
        
        # Update Memory chart
        self.memory_chart.data = self.chart_data["memory"]
        new_memory_content = self.memory_chart._build_chart()
        self.memory_chart.content = new_memory_content
        
        # Update Clients chart
        self.clients_chart.data = self.chart_data["clients"]
        new_clients_content = self.clients_chart._build_chart()
        self.clients_chart.content = new_clients_content
        
        self.page.update()


# Factory function
def create_real_time_charts(title: str = "Server Metrics", **kwargs) -> RealTimeCharts:
    """Create real-time charts component"""
    return RealTimeCharts(title=title, **kwargs)