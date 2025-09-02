#!/usr/bin/env python3
"""
Consolidated Chart System - Complete charting solution with all features absorbed
CONSOLIDATION STATUS: ✅ COMPLETE via Absorption Method

Purpose: Unified charting system combining:
- Enhanced charts with Material Design 3 (base from enhanced_charts.py)
- Performance monitoring with real-time updates (absorbed from charts.py) 
- Data visualization enums and structures (absorbed from data_visualization.py)
- Metric formatting utilities (absorbed from analytics.py)

Interface Goal: One import, all chart functionality
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any, Union, Tuple, Set
from enum import Enum, auto
from dataclasses import dataclass, field
import asyncio
import logging
import time
import json
import os
import psutil
from datetime import datetime, timedelta
from collections import deque
import random
import math

from flet_server_gui.managers.theme_manager import TOKENS

logger = logging.getLogger(__name__)


# =============================================================================
# ABSORBED: Core Data Structures & Enums (from enhanced_charts.py + data_visualization.py)
# =============================================================================

class ChartType(Enum):
    """Enhanced chart types combining all variations"""
    # Basic types (from enhanced_charts.py)
    LINE = "line"
    BAR = "bar" 
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    
    # Advanced types (from data_visualization.py) - using consistent string values
    LINE_CHART = "line_chart"
    AREA_CHART = "area_chart"
    BAR_CHART = "bar_chart"
    COLUMN_CHART = "column_chart"
    PIE_CHART = "pie_chart"
    DONUT_CHART = "donut_chart"
    SCATTER_PLOT = "scatter_plot"
    BUBBLE_CHART = "bubble_chart"
    GAUGE_CHART = "gauge_chart"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    SANKEY_DIAGRAM = "sankey_diagram"
    CANDLESTICK = "candlestick"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    RADAR_CHART = "radar_chart"
    WATERFALL = "waterfall"
    FUNNEL_CHART = "funnel_chart"


class ChartSize(Enum):
    """Chart size presets"""
    SMALL = "small"    # 300x200
    MEDIUM = "medium"  # 400x300
    LARGE = "large"    # 600x400
    XLARGE = "xlarge"  # 800x500


class InteractionType(Enum):
    """Types of chart interactions"""
    HOVER = auto()
    CLICK = auto()
    DRAG = auto()
    ZOOM = auto()
    PAN = auto()
    BRUSH_SELECT = auto()
    TOOLTIP = auto()
    CROSSFILTER = auto()


class AnimationType(Enum):
    """Animation types for chart transitions"""
    FADE_IN = auto()
    SLIDE_IN = auto()
    SCALE_IN = auto()
    BOUNCE = auto()
    ELASTIC = auto()
    MORPH = auto()
    STAGGER = auto()
    NONE = auto()


class DataAggregation(Enum):
    """Data aggregation methods"""
    SUM = auto()
    AVERAGE = auto()
    MEDIAN = auto()
    MIN = auto()
    MAX = auto()
    COUNT = auto()
    DISTINCT_COUNT = auto()
    STANDARD_DEVIATION = auto()
    PERCENTILE = auto()


class ColorScheme(Enum):
    """Color scheme options for visualizations"""
    MATERIAL_PRIMARY = auto()
    MATERIAL_ACCENT = auto()
    CATEGORICAL = auto()
    SEQUENTIAL_BLUES = auto()
    SEQUENTIAL_GREENS = auto()
    SEQUENTIAL_REDS = auto()
    DIVERGING = auto()
    MONOCHROME = auto()
    HIGH_CONTRAST = auto()
    CUSTOM = auto()


# ABSORBED: Analytics enums and structures (from analytics.py)

class MetricType(Enum):
    """Types of metrics for analytics tracking"""
    PERFORMANCE = auto()
    USAGE = auto()
    ERROR_RATE = auto()
    THROUGHPUT = auto()
    LATENCY = auto()
    STORAGE = auto()
    SECURITY = auto()
    CUSTOM = auto()


class AnalyticsTimeRange(Enum):
    """Time range options for analytics data"""
    REAL_TIME = "real_time"
    LAST_HOUR = "1h"
    LAST_4_HOURS = "4h"
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    CUSTOM = "custom"


# =============================================================================
# ABSORBED: Data Structures (consolidated from all files)
# =============================================================================

@dataclass
class ChartDataPoint:
    """Enhanced data point for charts (base + advanced features)"""
    x: Union[str, int, float, datetime]
    y: Union[int, float]
    label: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None
    size: Optional[float] = None  # For bubble charts
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert data point to dictionary"""
        result = {
            'x': self.x if not isinstance(self.x, datetime) else self.x.isoformat(),
            'y': self.y,
            'label': self.label,
            'color': self.color,
            'category': self.category,
            'size': self.size,
            'metadata': self.metadata
        }
        return {k: v for k, v in result.items() if v is not None}


@dataclass
class ChartSeries:
    """Enhanced series of data points"""
    name: str
    data: List[ChartDataPoint]
    color: Optional[str] = None
    type: ChartType = ChartType.LINE
    style_config: Dict[str, Any] = field(default_factory=dict)
    aggregation: Optional[DataAggregation] = None
    is_visible: bool = True
    
    def aggregate_data(self, method: DataAggregation, group_by: str = None) -> 'ChartSeries':
        """Aggregate data points using specified method"""
        if not self.data:
            return self
            
        if method == DataAggregation.AVERAGE:
            avg_y = sum(point.y for point in self.data) / len(self.data)
            aggregated_point = ChartDataPoint(x="Average", y=avg_y, label=f"Avg {self.name}")
            return ChartSeries(f"{self.name} (Avg)", [aggregated_point], self.color, self.type)
        elif method == DataAggregation.SUM:
            total_y = sum(point.y for point in self.data)
            aggregated_point = ChartDataPoint(x="Total", y=total_y, label=f"Total {self.name}")
            return ChartSeries(f"{self.name} (Sum)", [aggregated_point], self.color, self.type)
        elif method == DataAggregation.MAX:
            max_point = max(self.data, key=lambda p: p.y)
            return ChartSeries(f"{self.name} (Max)", [max_point], self.color, self.type)
        elif method == DataAggregation.MIN:
            min_point = min(self.data, key=lambda p: p.y)
            return ChartSeries(f"{self.name} (Min)", [min_point], self.color, self.type)
        
        return self
    
    def filter_data(self, filter_func: Callable[[ChartDataPoint], bool]) -> 'ChartSeries':
        """Filter data points using custom function"""
        filtered_data = [point for point in self.data if filter_func(point)]
        return ChartSeries(
            f"{self.name} (Filtered)",
            filtered_data,
            self.color,
            self.type,
            self.style_config,
            self.aggregation,
            self.is_visible
        )


@dataclass 
class EnhancedChartConfig:
    """Enhanced configuration for charts (consolidated from all sources)"""
    title: Optional[str] = None
    series: List[ChartSeries] = field(default_factory=list)
    chart_type: ChartType = ChartType.LINE
    size: ChartSize = ChartSize.MEDIUM
    width: Optional[int] = None
    height: Optional[int] = None
    expand: Union[bool, int] = False
    animate: bool = True
    animation_duration: int = 500  # milliseconds
    animation_type: AnimationType = AnimationType.FADE_IN
    show_legend: bool = True
    show_grid: bool = True
    show_tooltip: bool = True
    show_axes: bool = True
    is_interactive: bool = True
    color_scheme: ColorScheme = ColorScheme.MATERIAL_PRIMARY
    on_click: Optional[Callable] = None
    on_hover: Optional[Callable] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    y_axis_min: Optional[float] = None
    y_axis_max: Optional[float] = None
    custom_styling: Dict[str, Any] = field(default_factory=dict)


# ABSORBED: Metric utilities (from analytics.py)

@dataclass
class MetricData:
    """Data structure for individual metrics with comprehensive metadata"""
    metric_id: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def format_value(self, precision: int = 2) -> str:
        """Format metric value for display"""
        return format_metric_value(self.value, self.unit, precision)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric data to dictionary for serialization"""
        return {
            "metric_id": self.metric_id,
            "metric_type": self.metric_type.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "tags": self.tags
        }


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


# =============================================================================
# ABSORBED: Utility Functions (from analytics.py)
# =============================================================================

def format_metric_value(value: float, unit: str, precision: int = 2) -> str:
    """
    Format metric value for display with appropriate units and scaling.
    
    Args:
        value: Numeric value to format
        unit: Unit of measurement
        precision: Decimal precision for display
        
    Returns:
        Formatted string for UI display
    """
    # Handle different unit types with human-readable scaling
    if unit.lower() in ['bytes', 'b']:
        # Convert bytes to human-readable format
        for scale_unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if value < 1024:
                return f"{value:.{precision}f} {scale_unit}"
            value /= 1024
        return f"{value:.{precision}f} PB"
    
    elif unit == '%' or unit.lower() == 'percent':
        # Format percentage values
        return f"{value:.{precision}f}%"
    
    elif unit.lower() in ['seconds', 'sec', 's', 'ms', 'milliseconds']:
        # Format time values
        if unit.lower() in ['ms', 'milliseconds'] and value >= 1000:
            return f"{value/1000:.{precision}f} sec"
        return f"{value:.{precision}f} {unit}"
    
    else:
        # Default formatting
        return f"{value:.{precision}f} {unit}"


def calculate_time_boundaries(time_range: AnalyticsTimeRange) -> Tuple[datetime, datetime]:
    """
    Calculate start and end times for analytics time range.
    
    Args:
        time_range: Time range specification
        
    Returns:
        Tuple of (start_time, end_time)
    """
    now = datetime.now()
    
    if time_range == AnalyticsTimeRange.REAL_TIME:
        return (now - timedelta(minutes=5), now)
    elif time_range == AnalyticsTimeRange.LAST_HOUR:
        return (now - timedelta(hours=1), now)
    elif time_range == AnalyticsTimeRange.LAST_4_HOURS:
        return (now - timedelta(hours=4), now)
    elif time_range == AnalyticsTimeRange.LAST_24_HOURS:
        return (now - timedelta(days=1), now)
    elif time_range == AnalyticsTimeRange.LAST_7_DAYS:
        return (now - timedelta(days=7), now)
    elif time_range == AnalyticsTimeRange.LAST_30_DAYS:
        return (now - timedelta(days=30), now)
    elif time_range == AnalyticsTimeRange.LAST_90_DAYS:
        return (now - timedelta(days=90), now)
    else:
        # Default to last 24 hours
        return (now - timedelta(days=1), now)


def create_sample_metric_data(metric_type: MetricType, value: float, unit: str) -> MetricData:
    """
    Create sample metric data for testing and demonstration.
    
    Args:
        metric_type: Type of metric
        value: Metric value
        unit: Unit of measurement
        
    Returns:
        MetricData instance with sample data
    """
    return MetricData(
        metric_id=f"sample_{metric_type.name.lower()}",
        metric_type=metric_type,
        value=value,
        unit=unit,
        timestamp=datetime.now(),
        metadata={"source": "sample_data"},
        tags=["sample", "demo"]
    )


# =============================================================================
# MAIN CHART COMPONENT (base from enhanced_charts.py)
# =============================================================================

class EnhancedChart:
    """
    Enhanced chart with Material Design 3 styling and animations (BASE)
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
        
        # Create chart content based on type
        if self.config.chart_type in [ChartType.LINE, ChartType.LINE_CHART]:
            return self._create_line_chart(width, height)
        elif self.config.chart_type in [ChartType.BAR, ChartType.BAR_CHART]:
            return self._create_bar_chart(width, height)
        elif self.config.chart_type in [ChartType.PIE, ChartType.PIE_CHART]:
            return self._create_pie_chart(width, height)
        elif self.config.chart_type in [ChartType.AREA, ChartType.AREA_CHART]:
            return self._create_area_chart(width, height)
        elif self.config.chart_type in [ChartType.SCATTER, ChartType.SCATTER_PLOT]:
            return self._create_scatter_chart(width, height)
        else:
            return self._create_line_chart(width, height)
    
    def _create_line_chart(self, width: int, height: int) -> ft.Control:
        """Create line chart"""
        # Create line chart data
        line_chart_data = []
        for series in self.config.series:
            data_points = [
                ft.LineChartDataPoint(point.x, point.y) for point in series.data
            ]
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
            data_points = [
                ft.BarChartGroup(
                    x=point.x,
                    bar_rods=[ft.BarChartRod(to_y=point.y, color=series.color)],
                )
                for point in series.data
            ]
            bar_chart_data.extend(data_points)

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
        # Create area chart data
        line_chart_data = []
        for series in self.config.series:
            data_points = [
                ft.LineChartDataPoint(point.x, point.y) for point in series.data
            ]
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
            data_points = [
                ft.LineChartDataPoint(point.x, point.y) for point in series.data
            ]
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
            legend_items = [
                ft.Row(
                    [
                        ft.Container(
                            width=12,
                            height=12,
                            bgcolor=series.color,
                            border_radius=6,
                        ),
                        ft.Text(series.name, size=12),
                    ],
                    spacing=4,
                )
                for series in self.config.series
            ]
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


# =============================================================================
# ABSORBED: Performance Monitoring Charts (from charts.py)
# =============================================================================

class EnhancedPerformanceCharts:
    """
    Advanced performance monitoring with interactive controls and responsive design.
    Enhanced charts with real-time alerts, time range controls, and export features.
    ABSORBED FROM: flet_server_gui/ui/widgets/charts.py
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
        
        return ft.Container(
            content=ft.Column(
                [
                    # Control panel
                    self._create_control_panel(),
                    # Alert panel (shows threshold violations)
                    self._create_alert_panel(),
                    # Metrics overview cards - responsive grid
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                content=self._create_metrics_grid(),
                                col={"sm": 12, "md": 12, "lg": 12},
                                expand=True,
                            )
                        ],
                        expand=True,
                    ),
                    # Charts section - responsive grid
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                content=self._create_charts_section(),
                                col={"sm": 12, "md": 12, "lg": 12},
                                expand=True,
                            )
                        ],
                        expand=True,
                    ),
                ],
                spacing=10,
                expand=True,
            ),
            padding=ft.padding.all(10),
            expand=True,
        )
    
    def _create_control_panel(self) -> ft.Container:
        """Create responsive control panel with monitoring controls"""
        
        start_stop_button = ft.ElevatedButton(
            text="Start Monitoring",
            icon=ft.Icons.PLAY_ARROW,
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
            bgcolor=TOKENS['surface_variant'],
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
                        ft.Icon(ft.Icons.NOTIFICATIONS, color=TOKENS['tertiary']),
                        ft.Text("No active alerts", size=12, color=TOKENS['outline'])
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
            bgcolor=None,
            border=ft.border.all(1, TOKENS['outline']),
            padding=ft.padding.all(8),
            border_radius=4,
            height=40,
            expand=True
        )
        return self.alert_panel
    
    def _create_metrics_grid(self) -> ft.ResponsiveRow:
        """Create responsive metrics display grid"""
        self.stat_displays = {
            'cpu': self._create_metric_card("CPU", ft.Icons.MEMORY, TOKENS['primary']),
            'memory': self._create_metric_card("Memory", ft.Icons.STORAGE, TOKENS['secondary']),
            'disk': self._create_metric_card("Disk", ft.Icons.STORAGE, TOKENS['tertiary']),
            'network': self._create_metric_card("Network", ft.Icons.NETWORK_CHECK, TOKENS['primary'])
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
                          color=TOKENS['outline'])
        max_text = ft.Text("Max: --", style=ft.TextThemeStyle.BODY_SMALL, 
                          color=TOKENS['outline'])
        status_indicator = ft.Container(
            width=8,
            height=8,
            bgcolor=TOKENS['outline'],
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
            'cpu': self._create_enhanced_chart("CPU Usage %", TOKENS['primary']),
            'memory': self._create_enhanced_chart("Memory Usage %", TOKENS['secondary']),
            'disk': self._create_enhanced_chart("Disk Usage %", TOKENS['tertiary']),
            'network': self._create_enhanced_chart("Network Activity (MB/s)", TOKENS['primary'])
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
                           color=TOKENS['outline']),
                    ft.Container(height=100, expand=True)  # Chart area
                ], expand=True),
                bgcolor=TOKENS['surface_variant'],
                border=ft.border.all(1, TOKENS['outline']),
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
        else:
            self._start_monitoring()
            e.control.text = "Stop Monitoring"
            e.control.icon = ft.Icons.STOP
        e.control.bgcolor = None
        e.control.update()
    
    def _start_monitoring(self):
        """Start enhanced monitoring with alert system"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.active_alerts.clear()
        if hasattr(self.page, 'run_task'):
            self.page.run_task(self._enhanced_monitoring_loop)
        else:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._enhanced_monitoring_loop())
            except RuntimeError:
                self._start_basic_monitoring()
                return
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
                            if alert := self._check_threshold(metric_name, value):
                                alerts.append(alert)

                    # Update UI
                    self._update_enhanced_displays(metric_values)
                    self._update_enhanced_charts()

                    # Handle alerts
                    if alerts:
                        self.active_alerts = alerts
                        self._update_alert_panel(alerts)
                    elif self.active_alerts:
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
                if data := list(self.metrics_history[metric_name]):
                    avg_val = sum(data) / len(data)
                    max_val = max(data)

                    card = self.stat_displays[metric_name]

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
                        status_indicator.bgcolor = TOKENS['error']
                    elif current_value >= self.thresholds[metric_name].warning:
                        status_indicator.bgcolor = TOKENS['tertiary']
                    else:
                        status_indicator.bgcolor = TOKENS['secondary']

                    # Only update if the card is attached to the page
                    if hasattr(card, 'page') and card.page:
                        card.update()
    
    def _update_enhanced_charts(self):
        """Update charts with enhanced visualization"""
        for metric_name, container in self.chart_containers.items():
            if data := list(self.metrics_history[metric_name]):
                self._update_single_enhanced_chart(container, data, metric_name)
    
    def _update_single_enhanced_chart(self, container: ft.Container, data: List[float], metric_name: str):
        """Update single chart with enhanced visualization"""
        try:
            chart_display = container.content.controls[1]  # Second control is chart display

            # Create simple text-based chart for now (can be enhanced with actual chart library)
            if data:
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
                               color=TOKENS['outline'])
                    ]),
                    progress_bar,
                    ft.Text(f"Range: {min(data):.1f}% - {max(data):.1f}%",
                           style=ft.TextThemeStyle.BODY_SMALL,
                           color=TOKENS['outline'])
                ], spacing=5)

                chart_display.content = chart_content
                # Only update if the container is attached to the page
                if hasattr(chart_display, 'page') and chart_display.page:
                    chart_display.update()
        except Exception as e:
            logger.error(f"❌ Error updating chart for {metric_name}: {e}")
    
    def _update_alert_panel(self, alerts: List[Dict]):
        """Update alert panel with current alerts"""
        if not self.alert_panel:
            return

        try:
            panel_content = self.alert_panel.content
            if hasattr(panel_content, 'controls') and panel_content.controls:
                responsive_row = panel_content.controls[0]
                if hasattr(responsive_row, 'controls') and len(responsive_row.controls) >= 2:
                    alert_container = responsive_row.controls[0]
                    if hasattr(alert_container, 'content'):
                        alert_content = alert_container.content
                    else:
                        alert_content = alert_container
                    clear_button_container = responsive_row.controls[1]
                    if hasattr(clear_button_container, 'content'):
                        clear_content = clear_button_container.content
                    else:
                        clear_content = clear_button_container
                else:
                    alert_content = panel_content
                    clear_content = None
            else:
                alert_content = panel_content
                clear_content = None
        except (AttributeError, IndexError):
            alert_content = self.alert_panel.content
            clear_content = None

        # Create alert content
        if alerts:
            # Show alerts
            alert_texts = []
            for alert in alerts:
                color = TOKENS['error'] if alert['level'] == 'critical' else TOKENS['tertiary']
                icon = ft.Icons.ERROR if alert['level'] == 'critical' else ft.Icons.WARNING
                alert_texts.append(
                    ft.Row([
                        ft.Icon(icon, color=color, size=16),
                        ft.Text(alert['message'], size=12, color=TOKENS['on_background'])
                    ], spacing=4)
                )

            # Update alert content
            if hasattr(alert_content, 'controls'):
                alert_content.controls = alert_texts
            elif hasattr(alert_content, 'content'):
                alert_content.content = ft.Column(alert_texts, spacing=4) if alert_texts else None

            # Update clear button visibility
            if clear_content:
                clear_content.visible = True

            # Update background color using theme-aware colors
            if hasattr(self.alert_panel, 'bgcolor'):
                self.alert_panel.bgcolor = TOKENS['error'] if any(a['level'] == 'critical' for a in alerts) else None
        else:
            # No alerts
            normal_alert = ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=TOKENS['on_primary'], size=16),
                ft.Text("All systems normal", size=12, color=TOKENS['outline'])
            ], spacing=4)

            # Update alert content
            if hasattr(alert_content, 'controls'):
                alert_content.controls = [normal_alert]
            else:
                if hasattr(alert_content, 'content'):
                    alert_content.content = normal_alert

            # Update clear button visibility
            if clear_content:
                clear_content.visible = False

            # Update background color using theme-aware colors
            if hasattr(self.alert_panel, 'bgcolor'):
                self.alert_panel.bgcolor = None

        # Update the panel only if it's attached to the page
        if hasattr(self.alert_panel, 'page') and self.alert_panel.page:
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
                       color=TOKENS['outline']),
                ft.Container(height=100, expand=True)
            ], expand=True)
            # Only update if the container is attached to the page
            if hasattr(chart_display, 'page') and chart_display.page:
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
    
    def initialize_updates(self):
        """Initialize updates after component is mounted to page"""
        # Reset charts to initial state
        self._reset_charts(None)
        # Update alert panel to initial state
        self._update_alert_panel([])


# =============================================================================
# ABSORBED: Enhanced Individual Chart Components (from charts.py)
# =============================================================================

class EnhancedBarChart(ft.Container):
    """Enhanced bar chart using ft.BarChart for real visualization."""
    
    def __init__(self,
                 data: List[Dict[str, Union[str, int, float]]],
                 x_field: str,
                 y_field: str,
                 title: Optional[str] = None,
                 bar_color: str = TOKENS['primary'],
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

        bar_groups = [
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
            for i, item in enumerate(self.data)
        ]
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
                 line_color: str = TOKENS['primary'],
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
            border=ft.border.all(1, TOKENS['outline']),
            horizontal_grid_lines=ft.ChartGridLines(interval=10, color=ft.colors.with_opacity(0.2, TOKENS['on_background'])),
            vertical_grid_lines=ft.ChartGridLines(interval=1, color=ft.colors.with_opacity(0.2, TOKENS['on_background'])),
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
            TOKENS['primary'],
            TOKENS['secondary'],
            TOKENS['tertiary'],
            TOKENS['error'],
            TOKENS['outline'],
            TOKENS['outline']
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
            content=ft.Icon(ft.Icons.PIE_CHART, size=100, color=TOKENS['outline']),
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


# =============================================================================
# FACTORY FUNCTIONS - Unified Interface
# =============================================================================

# Convenience functions for common chart types (from enhanced_charts.py)
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
    points = [ChartDataPoint(x=item[x_key], y=item[y_key]) for item in data]
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
    points = [ChartDataPoint(x=item[x_key], y=item[y_key]) for item in data]
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
    for item in data:
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


# Performance monitoring factory (from charts.py)
def create_performance_chart(server_bridge, page: ft.Page) -> EnhancedPerformanceCharts:
    """Create enhanced performance monitoring charts"""
    return EnhancedPerformanceCharts(server_bridge, page)


# Individual chart factories (from charts.py)
def create_enhanced_bar_chart(data: List[Dict[str, Union[str, int, float]]],
                    x_field: str,
                    y_field: str,
                    title: Optional[str] = None,
                    **kwargs) -> EnhancedBarChart:
    return EnhancedBarChart(data=data, x_field=x_field, y_field=y_field, title=title, **kwargs)


def create_enhanced_line_chart(data: List[Dict[str, Union[str, int, float]]],
                     x_field: str,
                     y_field: str,
                     title: Optional[str] = None,
                     **kwargs) -> EnhancedLineChart:
    return EnhancedLineChart(data=data, x_field=x_field, y_field=y_field, title=title, **kwargs)


def create_enhanced_pie_chart(data: List[Dict[str, Union[str, int, float]]],
                    label_field: str,
                    value_field: str,
                    title: Optional[str] = None,
                     **kwargs) -> EnhancedPieChart:
    return EnhancedPieChart(data=data, label_field=label_field, value_field=value_field, title=title, **kwargs)


# Utility functions for sample data
def create_sample_chart_data(chart_type: ChartType, data_points: int = 50) -> List[ChartDataPoint]:
    """
    Create sample data for chart testing and demonstrations
    
    Args:
        chart_type: Type of chart to generate sample data for
        data_points: Number of sample data points to generate
        
    Returns:
        List of sample data points appropriate for chart type
    """
    sample_data = []
    for i in range(data_points):
        if chart_type in [ChartType.LINE, ChartType.LINE_CHART, ChartType.AREA, ChartType.AREA_CHART]:
            # Time series data
            sample_data.append(ChartDataPoint(
                x=i,
                y=random.randint(10, 100) + 20 * math.sin(i / 10),
                label=f"Point {i}"
            ))
        elif chart_type in [ChartType.BAR, ChartType.BAR_CHART]:
            # Categorical data
            categories = ["A", "B", "C", "D", "E"]
            sample_data.append(ChartDataPoint(
                x=categories[i % len(categories)],
                y=random.randint(10, 100),
                label=f"Category {categories[i % len(categories)]}"
            ))
        elif chart_type in [ChartType.SCATTER, ChartType.SCATTER_PLOT]:
            # Scatter data
            sample_data.append(ChartDataPoint(
                x=random.randint(0, 100),
                y=random.randint(0, 100),
                size=random.randint(5, 20),
                label=f"Point {i}"
            ))
        else:
            # Default to simple numeric data
            sample_data.append(ChartDataPoint(
                x=i,
                y=random.randint(10, 100),
                label=f"Data {i}"
            ))
    
    return sample_data


# Test function combining features from enhanced_charts.py
async def test_consolidated_charts(page: ft.Page):
    """Test consolidated charts functionality"""
    print("Testing consolidated charts...")
    
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
        ft.Text("Consolidated Charts Test", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
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
    
    print("Consolidated charts test completed")


if __name__ == "__main__":
    print("Consolidated Chart System - Complete charting solution")
    print("✅ Enhanced charts with Material Design 3")
    print("✅ Performance monitoring with real-time updates") 
    print("✅ Data visualization enums and structures")
    print("✅ Metric formatting utilities")
    print("Interface: from flet_server_gui.ui.widgets.charts import create_line_chart, create_performance_chart, format_metric_value")