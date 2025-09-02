#!/usr/bin/env python3
"""
Chart Service - Unified interface and factory for all chart types

Purpose: Provide single entry point for chart creation with consistent interfaces
Logic: Chart factory, service registry, and unified chart management
UI: Standardized chart creation with Material Design 3 integration
"""

from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
import flet as ft
import asyncio
import logging
from datetime import datetime

# Import unified types
from .chart_types import (
    ChartType, ChartSize, ChartConfiguration, ChartDimensions, 
    ChartColors, AnimationType, ColorScheme, create_chart_configuration,
    get_chart_type_capabilities, SIZE_DIMENSIONS, DEFAULT_COLOR_PALETTES
)
from .analytics_utilities import MetricData, DataAggregation, aggregate_metric_data

logger = logging.getLogger(__name__)


@dataclass
class ChartDataPoint:
    """Unified data point structure for all chart types"""
    x: Union[str, int, float, datetime]
    y: Union[int, float]
    label: Optional[str] = None
    color: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChartSeries:
    """Data series for charts with styling information"""
    name: str
    data_points: List[ChartDataPoint]
    chart_type: ChartType = ChartType.LINE
    color: Optional[str] = None
    visible: bool = True
    style_properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.style_properties is None:
            self.style_properties = {}


class ChartRegistry:
    """Registry for chart implementations and their capabilities"""
    
    def __init__(self):
        self._chart_creators: Dict[ChartType, Callable] = {}
        self._chart_updaters: Dict[ChartType, Callable] = {}
        
    def register_chart_creator(self, chart_type: ChartType, creator: Callable):
        """Register chart creator function for specific chart type"""
        self._chart_creators[chart_type] = creator
        
    def register_chart_updater(self, chart_type: ChartType, updater: Callable):
        """Register chart updater function for specific chart type"""
        self._chart_updaters[chart_type] = updater
        
    def get_creator(self, chart_type: ChartType) -> Optional[Callable]:
        """Get chart creator for specific type"""
        return self._chart_creators.get(chart_type)
        
    def get_updater(self, chart_type: ChartType) -> Optional[Callable]:
        """Get chart updater for specific type"""
        return self._chart_updaters.get(chart_type)
        
    def get_supported_chart_types(self) -> List[ChartType]:
        """Get list of supported chart types"""
        return list(self._chart_creators.keys())


class UnifiedChart:
    """Unified chart wrapper providing consistent interface across chart types"""
    
    def __init__(self, config: ChartConfiguration, page: ft.Page):
        self.config = config
        self.page = page
        self.series_data: List[ChartSeries] = []
        self.chart_control: Optional[ft.Control] = None
        self.is_mounted = False
        
        # Real-time update support
        self.update_task: Optional[asyncio.Task] = None
        self.data_source: Optional[Callable] = None
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Performance tracking
        self.last_update_time: Optional[datetime] = None
        self.update_count = 0
        
    def add_series(self, series: ChartSeries) -> bool:
        """Add data series to chart"""
        try:
            # Validate series compatibility with chart type
            capabilities = get_chart_type_capabilities(self.config.chart_type)
            
            if not capabilities["supports_multiple_series"] and len(self.series_data) > 0:
                logger.warning(f"Chart type {self.config.chart_type} does not support multiple series")
                return False
                
            # Assign color if not provided
            if not series.color:
                series.color = self.config.colors.get_series_color(len(self.series_data))
                
            self.series_data.append(series)
            
            # Update chart if already mounted
            if self.is_mounted:
                self._refresh_chart()
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to add series to chart {self.config.chart_id}: {e}")
            return False
    
    def update_series_data(self, series_name: str, new_data: List[ChartDataPoint]) -> bool:
        """Update existing series with new data"""
        try:
            for series in self.series_data:
                if series.name == series_name:
                    series.data_points = new_data
                    
                    if self.is_mounted:
                        self._refresh_chart()
                        
                    self.last_update_time = datetime.now()
                    self.update_count += 1
                    return True
                    
            logger.warning(f"Series '{series_name}' not found in chart {self.config.chart_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to update series data: {e}")
            return False
    
    def build(self) -> ft.Control:
        """Build the chart control"""
        try:
            # Get chart creator from registry
            chart_service = ChartService.get_instance()
            creator = chart_service.registry.get_creator(self.config.chart_type)
            
            if not creator:
                return self._create_fallback_chart()
                
            # Create the chart control
            self.chart_control = creator(self.config, self.series_data, self.page)
            self.is_mounted = True
            
            # Set up real-time updates if configured
            if self.config.real_time_updates and self.data_source:
                self._start_real_time_updates()
                
            return self._wrap_chart_control()
            
        except Exception as e:
            logger.error(f"Failed to build chart {self.config.chart_id}: {e}")
            return self._create_error_chart(str(e))
    
    def _wrap_chart_control(self) -> ft.Control:
        """Wrap chart control with title, legends, and other elements"""
        controls = []
        
        # Add title if provided
        if self.config.title:
            controls.append(
                ft.Container(
                    content=ft.Text(
                        self.config.title,
                        style=ft.TextThemeStyle.TITLE_MEDIUM,
                        weight=ft.FontWeight.W_500
                    ),
                    padding=ft.padding.only(bottom=10)
                )
            )
        
        # Add main chart
        controls.append(self.chart_control)
        
        # Add legend if enabled and multiple series
        if self.config.show_legend and len(self.series_data) > 1:
            controls.append(self._create_legend())
        
        return ft.Container(
            content=ft.Column(
                controls=controls,
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=self.config.dimensions.width,
            height=self.config.dimensions.height,
            expand=self.config.dimensions.expand,
        )
    
    def _create_legend(self) -> ft.Control:
        """Create legend for the chart"""
        legend_items = []
        
        for series in self.series_data:
            if series.visible:
                legend_items.append(
                    ft.Row([
                        ft.Container(
                            width=12,
                            height=12,
                            bgcolor=series.color,
                            border_radius=2
                        ),
                        ft.Text(series.name, size=12)
                    ], spacing=6)
                )
        
        return ft.Container(
            content=ft.Row(
                legend_items,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=16
            ),
            padding=ft.padding.only(top=10)
        )
    
    def _refresh_chart(self):
        """Refresh chart display with current data"""
        if self.chart_control and self.page:
            # Use updater if available
            chart_service = ChartService.get_instance()
            updater = chart_service.registry.get_updater(self.config.chart_type)
            
            if updater:
                updater(self.chart_control, self.series_data)
            
            # Update the control
            if hasattr(self.chart_control, 'update'):
                self.chart_control.update()
    
    def _create_fallback_chart(self) -> ft.Control:
        """Create fallback chart when creator not available"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.ASSESSMENT, size=48, color=ft.colors.OUTLINE),
                ft.Text(
                    f"Chart type '{self.config.chart_type.value}' not supported",
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    text_align=ft.TextAlign.CENTER
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            alignment=ft.alignment.center,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
            padding=20,
            width=300,
            height=200
        )
    
    def _create_error_chart(self, error_message: str) -> ft.Control:
        """Create error display when chart creation fails"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.ERROR_OUTLINE, size=48, color=ft.colors.ERROR),
                ft.Text("Chart Error", style=ft.TextThemeStyle.TITLE_SMALL, color=ft.colors.ERROR),
                ft.Text(
                    error_message,
                    style=ft.TextThemeStyle.BODY_SMALL,
                    text_align=ft.TextAlign.CENTER
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            alignment=ft.alignment.center,
            bgcolor=ft.colors.ERROR_CONTAINER,
            border_radius=8,
            padding=20,
            width=300,
            height=200
        )
    
    async def start_real_time_updates(self, data_source: Callable) -> bool:
        """Start real-time data updates"""
        try:
            self.data_source = data_source
            
            if self.update_task:
                self.update_task.cancel()
            
            self.update_task = asyncio.create_task(self._update_loop())
            return True
            
        except Exception as e:
            logger.error(f"Failed to start real-time updates: {e}")
            return False
    
    async def stop_real_time_updates(self):
        """Stop real-time updates"""
        if self.update_task:
            self.update_task.cancel()
            self.update_task = None
    
    async def _update_loop(self):
        """Background update loop for real-time data"""
        try:
            while True:
                if self.data_source:
                    try:
                        new_data = await self.data_source()
                        if new_data:
                            # Process new data and update series
                            await self._process_real_time_data(new_data)
                    except Exception as e:
                        logger.error(f"Error in data source: {e}")
                
                await asyncio.sleep(self.config.update_interval)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in update loop: {e}")
    
    async def _process_real_time_data(self, data):
        """Process real-time data updates"""
        # This would be implemented based on the specific data format
        # For now, just trigger a refresh
        if self.is_mounted:
            self._refresh_chart()


class ChartService:
    """Main service class for chart creation and management"""
    
    _instance = None
    
    def __init__(self):
        self.registry = ChartRegistry()
        self.active_charts: Dict[str, UnifiedChart] = {}
        self.theme_manager = None
        
        # Initialize with default chart creators
        self._register_default_creators()
    
    @classmethod
    def get_instance(cls) -> 'ChartService':
        """Get singleton instance of chart service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def set_theme_manager(self, theme_manager):
        """Set theme manager for chart styling"""
        self.theme_manager = theme_manager
    
    def create_chart(self, config: ChartConfiguration, page: ft.Page) -> UnifiedChart:
        """Create a new chart with unified interface"""
        chart = UnifiedChart(config, page)
        self.active_charts[config.chart_id] = chart
        return chart
    
    def get_chart(self, chart_id: str) -> Optional[UnifiedChart]:
        """Get existing chart by ID"""
        return self.active_charts.get(chart_id)
    
    def remove_chart(self, chart_id: str) -> bool:
        """Remove chart from active charts"""
        if chart_id in self.active_charts:
            chart = self.active_charts[chart_id]
            # Stop real-time updates
            asyncio.create_task(chart.stop_real_time_updates())
            del self.active_charts[chart_id]
            return True
        return False
    
    def create_performance_chart(self, page: ft.Page, server_bridge=None, **kwargs) -> UnifiedChart:
        """Create performance monitoring chart"""
        config = create_chart_configuration(
            chart_id=kwargs.get('chart_id', 'performance_chart'),
            chart_type=ChartType.PERFORMANCE_LINE,
            title=kwargs.get('title', 'Performance Metrics'),
            size=kwargs.get('size', ChartSize.LARGE),
            **kwargs
        )
        
        chart = self.create_chart(config, page)
        
        # Add performance-specific configuration
        if server_bridge:
            chart.data_source = lambda: self._get_performance_metrics(server_bridge)
            
        return chart
    
    def create_enhanced_chart(
        self,
        page: ft.Page,
        chart_type: ChartType,
        data: List[Dict[str, Any]],
        title: str = "",
        size: ChartSize = ChartSize.MEDIUM,
        **kwargs
    ) -> UnifiedChart:
        """Create enhanced configurable chart"""
        config = create_chart_configuration(
            chart_id=kwargs.get('chart_id', f'{chart_type.value}_chart'),
            chart_type=chart_type,
            title=title,
            size=size,
            **kwargs
        )
        
        chart = self.create_chart(config, page)
        
        # Convert data to chart series
        if data:
            series_name = kwargs.get('series_name', 'Series 1')
            x_key = kwargs.get('x_key', 'x')
            y_key = kwargs.get('y_key', 'y')
            
            data_points = [
                ChartDataPoint(x=item[x_key], y=item[y_key])
                for item in data if x_key in item and y_key in item
            ]
            
            series = ChartSeries(
                name=series_name,
                data_points=data_points,
                chart_type=chart_type
            )
            
            chart.add_series(series)
        
        return chart
    
    def process_metric_data(
        self,
        metrics: List[MetricData],
        aggregation_method: DataAggregation = DataAggregation.AVERAGE
    ) -> List[ChartDataPoint]:
        """Process metric data for chart visualization"""
        try:
            # Aggregate the metrics
            aggregated = aggregate_metric_data(metrics, aggregation_method)
            
            # Convert to chart data points
            data_points = []
            for agg_metric in aggregated:
                data_points.append(
                    ChartDataPoint(
                        x=agg_metric.time_range[1],  # Use end time as x
                        y=agg_metric.value,
                        label=f"{agg_metric.value:.2f} {agg_metric.unit}",
                        metadata={
                            "aggregation": agg_metric.aggregation_method.name,
                            "data_points": agg_metric.data_points_count
                        }
                    )
                )
            
            return data_points
            
        except Exception as e:
            logger.error(f"Failed to process metric data: {e}")
            return []
    
    def _register_default_creators(self):
        """Register default chart creators"""
        # Import chart implementations
        try:
            from ..ui.widgets.charts import create_line_chart, create_bar_chart, create_pie_chart
            
            # Register enhanced chart creators
            self.registry.register_chart_creator(ChartType.LINE, self._create_line_chart)
            self.registry.register_chart_creator(ChartType.BAR, self._create_bar_chart)
            self.registry.register_chart_creator(ChartType.PIE, self._create_pie_chart)
            
        except ImportError as e:
            logger.warning(f"Could not import enhanced charts: {e}")
        
        try:
            from ..ui.widgets.charts import EnhancedPerformanceCharts
            
            # Register performance chart creator
            self.registry.register_chart_creator(ChartType.PERFORMANCE_LINE, self._create_performance_chart)
            
        except ImportError as e:
            logger.warning(f"Could not import performance charts: {e}")
    
    def _create_line_chart(self, config: ChartConfiguration, series_data: List[ChartSeries], page: ft.Page) -> ft.Control:
        """Create line chart control"""
        # Convert series data to Flet LineChart format
        line_chart_data = []
        
        for series in series_data:
            if series.visible:
                data_points = [
                    ft.LineChartDataPoint(
                        x=i if isinstance(point.x, str) else point.x,
                        y=point.y
                    )
                    for i, point in enumerate(series.data_points)
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
        
        return ft.LineChart(
            data_series=line_chart_data,
            **config.get_flet_chart_properties()
        )
    
    def _create_bar_chart(self, config: ChartConfiguration, series_data: List[ChartSeries], page: ft.Page) -> ft.Control:
        """Create bar chart control"""
        bar_groups = []
        
        for series in series_data:
            if series.visible:
                for i, point in enumerate(series.data_points):
                    bar_groups.append(
                        ft.BarChartGroup(
                            x=i,
                            bar_rods=[
                                ft.BarChartRod(
                                    from_y=0,
                                    to_y=point.y,
                                    width=20,
                                    color=series.color,
                                    tooltip=point.label or f"{point.y}",
                                    border_radius=4
                                )
                            ]
                        )
                    )
        
        return ft.BarChart(
            bar_groups=bar_groups,
            **config.get_flet_chart_properties()
        )
    
    def _create_pie_chart(self, config: ChartConfiguration, series_data: List[ChartSeries], page: ft.Page) -> ft.Control:
        """Create pie chart control"""
        sections = []
        
        for series in series_data:
            if series.visible and series.data_points:
                # For pie chart, use the first data point's value
                point = series.data_points[0]
                sections.append(
                    ft.PieChartSection(
                        value=point.y,
                        color=series.color,
                        radius=50,
                        title=series.name,
                        title_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
                    )
                )
        
        return ft.PieChart(
            sections=sections,
            center_space_radius=40,
            **config.get_flet_chart_properties()
        )
    
    def _create_performance_chart(self, config: ChartConfiguration, series_data: List[ChartSeries], page: ft.Page) -> ft.Control:
        """Create performance monitoring chart"""
        try:
            from ..ui.widgets.charts import EnhancedPerformanceCharts
            
            # This would need to be adapted to work with the unified interface
            # For now, return a placeholder
            return ft.Container(
                content=ft.Text("Performance Chart Integration Pending"),
                alignment=ft.alignment.center,
                width=config.dimensions.width or 400,
                height=config.dimensions.height or 300
            )
            
        except ImportError:
            return self._create_line_chart(config, series_data, page)
    
    async def _get_performance_metrics(self, server_bridge):
        """Get performance metrics from server bridge"""
        try:
            # This would interface with the actual server bridge
            # For now, return mock data
            return []
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return []


# Convenience functions for chart creation

def create_line_chart(page: ft.Page, title: str, data: List[Dict[str, Any]], **kwargs) -> UnifiedChart:
    """Create line chart with simplified interface"""
    service = ChartService.get_instance()
    return service.create_enhanced_chart(page, ChartType.LINE, data, title, **kwargs)


def create_bar_chart(page: ft.Page, title: str, data: List[Dict[str, Any]], **kwargs) -> UnifiedChart:
    """Create bar chart with simplified interface"""
    service = ChartService.get_instance()
    return service.create_enhanced_chart(page, ChartType.BAR, data, title, **kwargs)


def create_pie_chart(page: ft.Page, title: str, data: List[Dict[str, Any]], **kwargs) -> UnifiedChart:
    """Create pie chart with simplified interface"""
    service = ChartService.get_instance()
    return service.create_enhanced_chart(page, ChartType.PIE, data, title, **kwargs)


def create_performance_chart(page: ft.Page, server_bridge=None, **kwargs) -> UnifiedChart:
    """Create performance monitoring chart"""
    service = ChartService.get_instance()
    return service.create_performance_chart(page, server_bridge, **kwargs)


def initialize_chart_service(theme_manager=None) -> ChartService:
    """Initialize chart service with theme integration"""
    service = ChartService.get_instance()
    if theme_manager:
        service.set_theme_manager(theme_manager)
    return service