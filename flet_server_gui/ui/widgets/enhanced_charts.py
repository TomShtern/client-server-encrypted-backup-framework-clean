#!/usr/bin/env python3
"""
Enhanced Chart Components - Advanced charting system with animations and Material Design 3

Purpose: Provide consistent, animated chart components with proper styling
Logic: Chart creation, data handling, animation, and interaction
UI: Material Design 3 styled charts with interactive features
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import logging
from flet_server_gui.ui.unified_theme_system import TOKENS
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ChartType(Enum):
    """Chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"


class ChartSize(Enum):
    """Chart sizes"""
    SMALL = "small"    # 300x200
    MEDIUM = "medium"  # 400x300
    LARGE = "large"    # 600x400
    XLARGE = "xlarge"  # 800x500


@dataclass
class ChartDataPoint:
    """Data point for charts"""
    x: Union[str, int, float, datetime]
    y: Union[int, float]
    label: Optional[str] = None
    color: Optional[str] = None


@dataclass
class ChartSeries:
    """Series of data points"""
    name: str
    data: List[ChartDataPoint]
    color: Optional[str] = None
    type: ChartType = ChartType.LINE


@dataclass
class EnhancedChartConfig:
    """Configuration for enhanced charts"""
    title: Optional[str] = None
    series: List[ChartSeries] = field(default_factory=list)
    chart_type: ChartType = ChartType.LINE
    size: ChartSize = ChartSize.MEDIUM
    width: Optional[int] = None
    height: Optional[int] = None
    expand: Union[bool, int] = False
    animate: bool = True
    animation_duration: int = 500  # milliseconds
    show_legend: bool = True
    show_grid: bool = True
    show_tooltip: bool = True
    on_click: Optional[Callable] = None
    on_hover: Optional[Callable] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    y_axis_min: Optional[float] = None
    y_axis_max: Optional[float] = None


class EnhancedChart:
    """
    Enhanced chart with Material Design 3 styling and animations
    """
    
    # Size mappings
    SIZE_DIMENSIONS = {
        ChartSize.SMALL: (300, 200),
        ChartSize.MEDIUM: (400, 300),
        ChartSize.LARGE: (600, 400),
        ChartSize.XLARGE: (800, 500)
    }
    
    # Default colors
    DEFAULT_COLORS = [
        TOKENS['primary'],
        TOKENS['secondary'],
        TOKENS['tertiary'],
        TOKENS['error'],
        TOKENS['tertiary'],
        TOKENS['secondary']
    ]
    
    def __init__(self, page: ft.Page, config: EnhancedChartConfig):
        self.page = page
        self.config = config
        self.chart_ref = ft.Ref[ft.Control]()
        
        # Assign colors to series if not provided
        self._assign_colors()
        
        # Create the chart
        self.chart = self._create_chart()
    
    def _assign_colors(self):
        """Assign colors to series if not provided"""
        for i, series in enumerate(self.config.series):
            if not series.color:
                series.color = self.DEFAULT_COLORS[i % len(self.DEFAULT_COLORS)]
    
    def _create_chart(self) -> ft.Control:
        """Create the enhanced chart based on type"""
        # Determine dimensions
        if self.config.width and self.config.height:
            width, height = self.config.width, self.config.height
        else:
            width, height = self.SIZE_DIMENSIONS.get(self.config.size, (400, 300))
        
        # Create chart content
        if self.config.chart_type == ChartType.LINE:
            return self._create_line_chart(width, height)
        elif self.config.chart_type == ChartType.BAR:
            return self._create_bar_chart(width, height)
        elif self.config.chart_type == ChartType.PIE:
            return self._create_pie_chart(width, height)
        elif self.config.chart_type == ChartType.AREA:
            return self._create_area_chart(width, height)
        elif self.config.chart_type == ChartType.SCATTER:
            return self._create_scatter_chart(width, height)
        else:
            return self._create_line_chart(width, height)
    
    def _create_line_chart(self, width: int, height: int) -> ft.Control:
        """Create line chart"""
        # Create line chart data
        line_chart_data = []
        for series in self.config.series:
            # Convert data points
            data_points = []
            for point in series.data:
                data_points.append(ft.LineChartDataPoint(point.x, point.y))
            
            line_chart_data.append(
                ft.LineChartData(
                    data_points=data_points,
                    stroke_width=3,
                    color=series.color,
                    curved=True,
                    stroke_cap_round=True
                )
            )
        
        # Create chart
        chart = ft.LineChart(
            data_series=line_chart_data,
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text(self.config.y_axis_label) if self.config.y_axis_label else None
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=30,
                title=ft.Text(self.config.x_axis_label) if self.config.x_axis_label else None
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, TOKENS['surface']),
            show_cursor=True,
            interactive=True,
            width=width,
            height=height
        )
        
        return self._wrap_chart(chart)
    
    def _create_bar_chart(self, width: int, height: int) -> ft.Control:
        """Create bar chart"""
        # Create bar chart data
        bar_chart_data = []
        for series in self.config.series:
            # Convert data points
            data_points = []
            for point in series.data:
                data_points.append(ft.BarChartGroup(x=point.x, bar_rods=[ft.BarChartRod(to_y=point.y, color=series.color)]))
            
            bar_chart_data.append(
                ft.BarChartGroup(
                    x=len(bar_chart_data),
                    bar_rods=[ft.BarChartRod(to_y=0, color=series.color)]  # Initial state for animation
                )
            )
        
        # Create chart
        chart = ft.BarChart(
            bar_groups=bar_chart_data,
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text(self.config.y_axis_label) if self.config.y_axis_label else None
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=30,
                title=ft.Text(self.config.x_axis_label) if self.config.x_axis_label else None
            ),
            width=width,
            height=height
        )
        
        return self._wrap_chart(chart)
    
    def _create_pie_chart(self, width: int, height: int) -> ft.Control:
        """Create pie chart"""
        # Create pie chart data
        sections = []
        for series in self.config.series:
            if series.data:
                # For pie chart, we typically use the first data point's y value
                value = series.data[0].y
                sections.append(
                    ft.PieChartSection(
                        value=value,
                        color=series.color,
                        radius=50,
                        title=series.name,
                        title_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
                    )
                )
        
        # Create chart
        chart = ft.PieChart(
            sections=sections,
            center_space_radius=40,
            width=width,
            height=height
        )
        
        return self._wrap_chart(chart)
    
    def _create_area_chart(self, width: int, height: int) -> ft.Control:
        """Create area chart"""
        # For simplicity, we'll create an area chart similar to line chart but filled
        # Create line chart data
        line_chart_data = []
        for series in self.config.series:
            # Convert data points
            data_points = []
            for point in series.data:
                data_points.append(ft.LineChartDataPoint(point.x, point.y))
            
            line_chart_data.append(
                ft.LineChartData(
                    data_points=data_points,
                    stroke_width=0,  # No stroke for area chart
                    color=ft.colors.with_opacity(0.5, series.color),
                    below_line_bgcolor=ft.colors.with_opacity(0.5, series.color),
                    curved=True
                )
            )
        
        # Create chart
        chart = ft.LineChart(
            data_series=line_chart_data,
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text(self.config.y_axis_label) if self.config.y_axis_label else None
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=30,
                title=ft.Text(self.config.x_axis_label) if self.config.x_axis_label else None
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, TOKENS['surface']),
            show_cursor=True,
            interactive=True,
            width=width,
            height=height
        )
        
        return self._wrap_chart(chart)
    
    def _create_scatter_chart(self, width: int, height: int) -> ft.Control:
        """Create scatter chart"""
        # Create scatter chart data
        line_chart_data = []
        for series in self.config.series:
            # Convert data points
            data_points = []
            for point in series.data:
                data_points.append(ft.LineChartDataPoint(point.x, point.y))
            
            line_chart_data.append(
                ft.LineChartData(
                    data_points=data_points,
                    point_style=ft.FlPointStyle(
                        color=series.color,
                        stroke_width=2,
                        radius=4
                    ),
                    color=None  # No line connecting points
                )
            )
        
        # Create chart
        chart = ft.LineChart(
            data_series=line_chart_data,
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text(self.config.y_axis_label) if self.config.y_axis_label else None
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=30,
                title=ft.Text(self.config.x_axis_label) if self.config.x_axis_label else None
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, TOKENS['surface']),
            show_cursor=True,
            interactive=True,
            width=width,
            height=height
        )
        
        return self._wrap_chart(chart)
    
    def _wrap_chart(self, chart: ft.Control) -> ft.Control:
        """Wrap chart with title and legend if needed"""
        controls = []
        
        # Add title
        if self.config.title:
            controls.append(
                ft.Text(
                    self.config.title,
                    style=ft.TextThemeStyle.TITLE_MEDIUM,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER
                )
            )
        
        # Add chart
        controls.append(chart)
        
        # Add legend
        if self.config.show_legend and len(self.config.series) > 1:
            legend_items = []
            for series in self.config.series:
                legend_items.append(
                    ft.Row([
                        ft.Container(
                            width=12,
                            height=12,
                            bgcolor=series.color,
                            border_radius=6
                        ),
                        ft.Text(series.name, size=12)
                    ], spacing=4)
                )
            
            controls.append(
                ft.Row(
                    legend_items,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=16
                )
            )
        
        return ft.Column(
            controls,
            spacing=12,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    
    def update_data(self, series_index: int, data: List[ChartDataPoint]):
        """Update chart data for a specific series"""
        if 0 <= series_index < len(self.config.series):
            self.config.series[series_index].data = data
            # Reassign colors and recreate chart
            self._assign_colors()
            new_chart = self._create_chart()
            # Update the chart (implementation depends on how the chart is integrated)
            # This is a simplified approach - in practice, you might need to replace the control
            self.chart = new_chart
            self.page.update()
    
    def add_series(self, series: ChartSeries):
        """Add a new series to the chart"""
        self.config.series.append(series)
        # Reassign colors and recreate chart
        self._assign_colors()
        new_chart = self._create_chart()
        self.chart = new_chart
        self.page.update()
    
    def get_control(self) -> ft.Control:
        """Get the Flet control"""
        return self.chart


# Convenience functions for common chart types
def create_line_chart(
    page: ft.Page,
    title: str,
    data: List[Dict[str, Any]],
    x_key: str = "x",
    y_key: str = "y",
    series_name: str = "Series",
    color: Optional[str] = None,
    **kwargs
) -> EnhancedChart:
    """Create a line chart"""
    # Convert data to ChartDataPoint
    points = []
    for item in data:
        points.append(
            ChartDataPoint(
                x=item[x_key],
                y=item[y_key]
            )
        )
    
    series = ChartSeries(
        name=series_name,
        data=points,
        color=color
    )
    
    config = EnhancedChartConfig(
        title=title,
        series=[series],
        chart_type=ChartType.LINE,
        **kwargs
    )
    
    return EnhancedChart(page, config)


def create_bar_chart(
    page: ft.Page,
    title: str,
    data: List[Dict[str, Any]],
    x_key: str = "x",
    y_key: str = "y",
    series_name: str = "Series",
    color: Optional[str] = None,
    **kwargs
) -> EnhancedChart:
    """Create a bar chart"""
    # Convert data to ChartDataPoint
    points = []
    for item in data:
        points.append(
            ChartDataPoint(
                x=item[x_key],
                y=item[y_key]
            )
        )
    
    series = ChartSeries(
        name=series_name,
        data=points,
        color=color
    )
    
    config = EnhancedChartConfig(
        title=title,
        series=[series],
        chart_type=ChartType.BAR,
        **kwargs
    )
    
    return EnhancedChart(page, config)


def create_pie_chart(
    page: ft.Page,
    title: str,
    data: List[Dict[str, Any]],
    label_key: str = "label",
    value_key: str = "value",
    **kwargs
) -> EnhancedChart:
    """Create a pie chart"""
    # Convert data to ChartSeries
    series_list = []
    for i, item in enumerate(data):
        points = [ChartDataPoint(x=0, y=item[value_key], label=item[label_key])]
        series = ChartSeries(
            name=item[label_key],
            data=points
        )
        series_list.append(series)
    
    config = EnhancedChartConfig(
        title=title,
        series=series_list,
        chart_type=ChartType.PIE,
        **kwargs
    )
    
    return EnhancedChart(page, config)


# Test function
async def test_enhanced_charts(page: ft.Page):
    """Test enhanced charts functionality"""
    print("Testing enhanced charts...")
    
    # Generate sample data
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    values1 = [random.randint(10, 100) for _ in range(7)]
    values2 = [random.randint(10, 100) for _ in range(7)]
    
    # Create line chart data
    line_data = [{"x": days[i], "y": values1[i]} for i in range(7)]
    
    # Create line chart
    line_chart = create_line_chart(
        page,
        title="Weekly Performance",
        data=line_data,
        x_key="x",
        y_key="y",
        series_name="Performance"
    )
    
    # Create bar chart data
    bar_data = [{"x": days[i], "y": values2[i]} for i in range(7)]
    
    # Create bar chart
    bar_chart = create_bar_chart(
        page,
        title="Daily Activity",
        data=bar_data,
        x_key="x",
        y_key="y",
        series_name="Activity"
    )
    
    # Create pie chart data
    pie_data = [
        {"label": "Files", "value": 45},
        {"label": "Images", "value": 25},
        {"label": "Documents", "value": 20},
        {"label": "Others", "value": 10}
    ]
    
    # Create pie chart
    pie_chart = create_pie_chart(
        page,
        title="File Types Distribution",
        data=pie_data,
        label_key="label",
        value_key="value"
    )
    
    # Create layout
    layout = ft.Column([
        ft.Text("Enhanced Charts Test", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
        ft.Row([
            line_chart.get_control(),
            bar_chart.get_control()
        ], spacing=20),
        ft.Row([
            pie_chart.get_control()
        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
    ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
    
    # Add to page
    page.add(layout)
    page.update()
    
    # Test data updates
    await asyncio.sleep(2)
    new_values = [random.randint(10, 100) for _ in range(7)]
    new_data = [{"x": days[i], "y": new_values[i]} for i in range(7)]
    line_chart.update_data(0, [ChartDataPoint(x=d["x"], y=d["y"]) for d in new_data])
    
    print("Enhanced charts test completed")


if __name__ == "__main__":
    print("Enhanced Chart Components Module")
    print("This module provides enhanced chart components for the Flet Server GUI")
