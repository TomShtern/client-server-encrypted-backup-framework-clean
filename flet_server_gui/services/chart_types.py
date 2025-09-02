#!/usr/bin/env python3
"""
Chart Types Service - Unified type definitions and configurations for all chart components

Purpose: Consolidate chart type enums, configuration classes, and common data structures
Logic: Single source of truth for chart type definitions and configuration patterns
UI: Material Design 3 compatible chart configurations and theme integration
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union, Callable
from datetime import datetime, timedelta
import flet as ft


class ChartType(Enum):
    """Unified chart type definitions covering all chart implementations"""
    # Basic charts
    LINE = "line"
    BAR = "bar"  
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    
    # Advanced charts
    DONUT = "donut"
    GAUGE = "gauge"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    CANDLESTICK = "candlestick"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    RADAR = "radar"
    WATERFALL = "waterfall"
    FUNNEL = "funnel"
    BUBBLE = "bubble"
    
    # Performance-specific charts
    PERFORMANCE_LINE = "performance_line"
    METRICS_GAUGE = "metrics_gauge"
    REAL_TIME_AREA = "real_time_area"


class ChartSize(Enum):
    """Chart size variations for responsive design"""
    SMALL = "small"      # 300x200
    MEDIUM = "medium"    # 400x300
    LARGE = "large"      # 600x400
    XLARGE = "xlarge"    # 800x500
    RESPONSIVE = "responsive"  # Auto-sizing based on container


class AnimationType(Enum):
    """Chart animation types"""
    NONE = "none"
    FADE_IN = "fade_in"
    SLIDE_IN = "slide_in"
    SLIDE_UP = "slide_up"
    SCALE_IN = "scale_in"
    GROW = "grow"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    MORPH = "morph"
    STAGGER = "stagger"


class ColorScheme(Enum):
    """Color scheme options for visualizations"""
    MATERIAL_PRIMARY = "material_primary"
    MATERIAL_ACCENT = "material_accent"
    CATEGORICAL = "categorical"
    SEQUENTIAL_BLUES = "sequential_blues"
    SEQUENTIAL_GREENS = "sequential_greens"
    SEQUENTIAL_REDS = "sequential_reds"
    DIVERGING = "diverging"
    MONOCHROME = "monochrome"
    HIGH_CONTRAST = "high_contrast"
    PERFORMANCE = "performance"  # Special scheme for performance charts
    CUSTOM = "custom"


class InteractionType(Enum):
    """Types of chart interactions"""
    HOVER = "hover"
    CLICK = "click"
    DRAG = "drag"
    ZOOM = "zoom"
    PAN = "pan"
    BRUSH_SELECT = "brush_select"
    TOOLTIP = "tooltip"
    CROSSFILTER = "crossfilter"
    LEGEND_TOGGLE = "legend_toggle"


@dataclass
class ChartDimensions:
    """Chart dimension configuration with responsive support"""
    width: Optional[int] = None
    height: Optional[int] = None
    expand: Union[bool, int] = True
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    aspect_ratio: Optional[float] = None  # width/height ratio
    
    @classmethod
    def from_size(cls, size: ChartSize) -> 'ChartDimensions':
        """Create dimensions from predefined size"""
        size_mappings = {
            ChartSize.SMALL: (300, 200),
            ChartSize.MEDIUM: (400, 300),
            ChartSize.LARGE: (600, 400),
            ChartSize.XLARGE: (800, 500),
            ChartSize.RESPONSIVE: (None, None)
        }
        
        width, height = size_mappings.get(size, (400, 300))
        return cls(
            width=width, 
            height=height,
            expand=size == ChartSize.RESPONSIVE
        )


@dataclass
class ChartColors:
    """Chart color configuration with theme integration"""
    primary: Optional[str] = None
    secondary: Optional[str] = None
    accent: Optional[str] = None
    background: Optional[str] = None
    text: Optional[str] = None
    grid: Optional[str] = None
    series_colors: List[str] = field(default_factory=list)
    
    def get_series_color(self, index: int) -> str:
        """Get color for data series at index"""
        if self.series_colors:
            return self.series_colors[index % len(self.series_colors)]
        # Fallback to Material Design defaults
        default_colors = [
            "#1976D2", "#388E3C", "#F57C00", "#D32F2F", 
            "#7B1FA2", "#455A64", "#00796B", "#F44336"
        ]
        return default_colors[index % len(default_colors)]


@dataclass 
class AxisConfiguration:
    """Configuration for chart axes with validation"""
    title: str = ""
    data_type: str = "numeric"  # numeric, categorical, datetime
    min_value: Optional[Union[float, datetime]] = None
    max_value: Optional[Union[float, datetime]] = None
    tick_interval: Optional[Union[float, timedelta]] = None
    format_string: Optional[str] = None
    is_logarithmic: bool = False
    show_grid_lines: bool = True
    show_labels: bool = True
    reverse_order: bool = False
    
    def format_value(self, value: Union[float, str, datetime]) -> str:
        """Format value for axis display with proper handling"""
        if self.format_string:
            try:
                return self.format_string.format(value)
            except (ValueError, KeyError):
                pass
        
        # Apply type-specific formatting
        if self.data_type == "datetime" and isinstance(value, datetime):
            return value.strftime("%H:%M" if value.date() == datetime.now().date() else "%m/%d")
        elif self.data_type == "numeric" and isinstance(value, (int, float)):
            if self.is_logarithmic and value > 0:
                import math
                value = math.log10(value)
            return f"{value:.1f}" if isinstance(value, float) else str(value)
        
        return str(value)


@dataclass
class ChartConfiguration:
    """Unified chart configuration supporting all chart types"""
    chart_id: str
    title: str = ""
    chart_type: ChartType = ChartType.LINE
    dimensions: ChartDimensions = field(default_factory=lambda: ChartDimensions())
    colors: ChartColors = field(default_factory=lambda: ChartColors())
    animation: AnimationType = AnimationType.FADE_IN
    animation_duration: int = 500  # milliseconds
    
    # Display options
    show_legend: bool = True
    show_axes: bool = True
    show_grid: bool = True
    show_tooltips: bool = True
    is_interactive: bool = True
    
    # Axes configuration
    x_axis: Optional[AxisConfiguration] = None
    y_axis: Optional[AxisConfiguration] = None
    secondary_y_axis: Optional[AxisConfiguration] = None
    
    # Performance-specific options
    real_time_updates: bool = False
    update_interval: int = 5  # seconds
    max_data_points: int = 100
    
    # Event handlers
    on_click: Optional[Callable] = None
    on_hover: Optional[Callable] = None
    on_selection: Optional[Callable] = None
    
    # Custom styling
    custom_properties: Dict[str, Any] = field(default_factory=dict)
    
    def validate_configuration(self) -> List[str]:
        """Validate chart configuration and return error messages"""
        errors = []
        
        # Required fields
        if not self.chart_id:
            errors.append("Chart ID is required")
        
        # Chart type compatibility
        if self.chart_type in [ChartType.PIE, ChartType.DONUT] and self.secondary_y_axis:
            errors.append("Pie/Donut charts cannot have secondary Y-axis")
        
        # Dimension validation
        if self.dimensions.width and self.dimensions.width < 100:
            errors.append("Width must be at least 100 pixels")
        if self.dimensions.height and self.dimensions.height < 100:
            errors.append("Height must be at least 100 pixels")
        
        # Animation validation
        if self.animation_duration < 0:
            errors.append("Animation duration must be non-negative")
        
        return errors
    
    def get_flet_chart_properties(self) -> Dict[str, Any]:
        """Convert configuration to Flet chart properties"""
        properties = {
            "width": self.dimensions.width,
            "height": self.dimensions.height,
            "expand": self.dimensions.expand,
        }
        
        # Add chart-specific properties
        if self.show_tooltips:
            properties["tooltip_bgcolor"] = self.colors.background or ft.colors.with_opacity(0.8, ft.colors.SURFACE)
        
        if self.is_interactive:
            properties["interactive"] = True
            properties["show_cursor"] = True
        
        return properties


@dataclass
class MetricThreshold:
    """Threshold configuration for performance monitoring"""
    warning: float
    critical: float
    enabled: bool = True
    warning_color: str = "#FF9800"  # Orange
    critical_color: str = "#F44336"  # Red


@dataclass
class PerformanceChartSettings:
    """Settings specific to performance monitoring charts"""
    time_range_minutes: int = 5
    update_interval: int = 5
    chart_type: str = "line"
    show_thresholds: bool = True
    auto_scale: bool = True
    theme: str = "default"
    
    # Thresholds for different metrics
    cpu_threshold: MetricThreshold = field(default_factory=lambda: MetricThreshold(70.0, 90.0))
    memory_threshold: MetricThreshold = field(default_factory=lambda: MetricThreshold(80.0, 95.0))
    disk_threshold: MetricThreshold = field(default_factory=lambda: MetricThreshold(85.0, 95.0))
    network_threshold: MetricThreshold = field(default_factory=lambda: MetricThreshold(50.0, 80.0))


# Size mappings for backward compatibility
SIZE_DIMENSIONS = {
    ChartSize.SMALL: (300, 200),
    ChartSize.MEDIUM: (400, 300),
    ChartSize.LARGE: (600, 400),
    ChartSize.XLARGE: (800, 500),
    ChartSize.RESPONSIVE: (None, None)
}

# Default color palettes
DEFAULT_COLOR_PALETTES = {
    ColorScheme.MATERIAL_PRIMARY: ["#1976D2", "#1565C0", "#0D47A1"],
    ColorScheme.MATERIAL_ACCENT: ["#FF4081", "#F50057", "#C51162"],
    ColorScheme.CATEGORICAL: ["#1976D2", "#388E3C", "#F57C00", "#D32F2F", "#7B1FA2", "#455A64"],
    ColorScheme.PERFORMANCE: ["#4CAF50", "#FF9800", "#F44336"],  # Green, Orange, Red
    ColorScheme.HIGH_CONTRAST: ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF"]
}


def create_chart_configuration(
    chart_id: str,
    chart_type: ChartType,
    title: str = "",
    size: ChartSize = ChartSize.MEDIUM,
    **kwargs
) -> ChartConfiguration:
    """Factory function to create chart configuration with sensible defaults"""
    
    config = ChartConfiguration(
        chart_id=chart_id,
        title=title,
        chart_type=chart_type,
        dimensions=ChartDimensions.from_size(size),
        **kwargs
    )
    
    # Set chart-specific defaults
    if chart_type in [ChartType.PERFORMANCE_LINE, ChartType.REAL_TIME_AREA]:
        config.real_time_updates = True
        config.show_grid = True
        config.is_interactive = True
    
    elif chart_type in [ChartType.PIE, ChartType.DONUT]:
        config.show_axes = False
        config.show_grid = False
    
    elif chart_type == ChartType.GAUGE:
        config.show_axes = False
        config.show_legend = False
    
    return config


def get_chart_type_capabilities(chart_type: ChartType) -> Dict[str, bool]:
    """Get capabilities and limitations for specific chart type"""
    capabilities = {
        "supports_multiple_series": True,
        "supports_real_time": True,
        "supports_zoom": True,
        "supports_pan": True,
        "supports_selection": True,
        "supports_axes": True,
        "supports_grid": True,
        "supports_legend": True
    }
    
    # Chart-specific limitations
    if chart_type in [ChartType.PIE, ChartType.DONUT]:
        capabilities.update({
            "supports_multiple_series": False,
            "supports_axes": False,
            "supports_grid": False,
            "supports_zoom": False,
            "supports_pan": False
        })
    
    elif chart_type == ChartType.GAUGE:
        capabilities.update({
            "supports_multiple_series": False,
            "supports_axes": False,
            "supports_grid": False,
            "supports_legend": False,
            "supports_zoom": False,
            "supports_pan": False
        })
    
    return capabilities