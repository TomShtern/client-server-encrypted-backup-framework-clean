#!/usr/bin/env python3
"""
Enhanced Chart Components
Custom Material Design 3 charts and data visualizations.
"""

import flet as ft
from typing import List, Dict, Optional, Tuple, Union
import math


class EnhancedBarChart(ft.Container):
    """Enhanced bar chart with animations and interactions"""
    
    def __init__(self,
                 data: List[Dict[str, Union[str, int, float]]],
                 x_field: str,
                 y_field: str,
                 title: Optional[str] = None,
                 animate_duration: int = 300,
                 bar_color: str = ft.Colors.PRIMARY,
                 bar_width: int = 40,
                 spacing: int = 20,
                 **kwargs):
        super().__init__(**kwargs)
        
        self.data = data
        self.x_field = x_field
        self.y_field = y_field
        self.title = title
        self.animate_duration = animate_duration
        self.bar_color = bar_color
        self.bar_width = bar_width
        self.spacing = spacing
        
        # Calculate max value for scaling
        self.max_y = max([item[y_field] for item in data]) if data else 1
        self.chart_height = 200
        
        # Build the chart
        self.content = self._build_chart()
        
        # Animation properties
        self.animate_scale = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
    
    def _build_chart(self) -> ft.Control:
        """Build the bar chart"""
        # Create bars
        bars = []
        labels = []
        
        for i, item in enumerate(self.data):
            x_value = str(item[self.x_field])
            y_value = item[self.y_field]
            
            # Calculate bar height (scaled to chart height)
            bar_height = (y_value / self.max_y) * self.chart_height if self.max_y > 0 else 0
            
            # Create bar
            bar = ft.Container(
                width=self.bar_width,
                height=0,  # Start with zero height for entrance animation
                bgcolor=self.bar_color,
                border_radius=ft.border_radius.only(top_left=4, top_right=4),
                animate=ft.Animation(self.animate_duration, ft.AnimationCurve.EASE_OUT)
            )
            
            # Create label
            label = ft.Text(x_value, size=12, text_align=ft.TextAlign.CENTER)
            
            # Create bar column
            bar_column = ft.Column([
                ft.Container(height=self.chart_height - bar_height),
                bar,
                label
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=self.bar_width)
            
            bars.append(bar_column)
        
        # Create chart content
        chart_content = ft.Column([
            ft.Text(self.title, style=ft.TextThemeStyle.TITLE_LARGE) if self.title else None,
            ft.Row(bars, spacing=self.spacing, alignment=ft.MainAxisAlignment.CENTER, wrap=True)
        ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Animate bars in after a short delay
        def animate_bars():
            import asyncio
            async def delayed_animation():
                await asyncio.sleep(0.1)
                for bar_column in bars:
                    bar = bar_column.controls[1]  # The actual bar container
                    original_height = (bar_column.controls[2].value / self.max_y) * self.chart_height if self.max_y > 0 else 0
                    bar.height = original_height
                    bar.page.update()
            
            if hasattr(self, 'page') and self.page:
                asyncio.create_task(delayed_animation())
        
        # Schedule animation
        if hasattr(self, 'page'):
            animate_bars()
        
        return chart_content


class EnhancedLineChart(ft.Container):
    """Enhanced line chart with animations and interactions"""
    
    def __init__(self,
                 data: List[Dict[str, Union[str, int, float]]],
                 x_field: str,
                 y_field: str,
                 title: Optional[str] = None,
                 animate_duration: int = 500,
                 line_color: str = ft.Colors.PRIMARY,
                 point_color: str = ft.Colors.SECONDARY,
                 line_width: int = 3,
                 point_size: int = 6,
                 show_points: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        
        self.data = data
        self.x_field = x_field
        self.y_field = y_field
        self.title = title
        self.animate_duration = animate_duration
        self.line_color = line_color
        self.point_color = point_color
        self.line_width = line_width
        self.point_size = point_size
        self.show_points = show_points
        
        # Calculate chart dimensions
        self.chart_width = 400
        self.chart_height = 200
        self.padding = 20
        
        # Calculate min/max values
        self.min_y = min([item[y_field] for item in data]) if data else 0
        self.max_y = max([item[y_field] for item in data]) if data else 1
        self.range_y = self.max_y - self.min_y if self.max_y != self.min_y else 1
        
        # Build the chart
        self.content = self._build_chart()
        
        # Animation properties
        self.animate_scale = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
    
    def _build_chart(self) -> ft.Control:
        """Build the line chart"""
        # Create coordinate points
        points = []
        for i, item in enumerate(self.data):
            x_value = item[self.x_field]
            y_value = item[self.y_field]
            
            # Scale to chart dimensions
            x_pos = (i / (len(self.data) - 1)) * self.chart_width if len(self.data) > 1 else self.chart_width / 2
            y_pos = self.chart_height - ((y_value - self.min_y) / self.range_y) * self.chart_height
            
            points.append((x_pos, y_pos, x_value, y_value))
        
        # Create lines and points
        chart_elements = []
        
        # Create lines
        if len(points) > 1:
            for i in range(len(points) - 1):
                x1, y1, _, _ = points[i]
                x2, y2, _, _ = points[i + 1]
                
                line = ft.Container(
                    width=math.sqrt((x2-x1)**2 + (y2-y1)**2),
                    height=self.line_width,
                    bgcolor=self.line_color,
                    rotate=math.atan2(y2-y1, x2-x1),
                    left=x1,
                    top=y1,
                    animate=ft.Animation(self.animate_duration, ft.AnimationCurve.EASE_OUT)
                )
                chart_elements.append(line)
        
        # Create points
        if self.show_points:
            for x_pos, y_pos, x_value, y_value in points:
                point = ft.Container(
                    width=self.point_size,
                    height=self.point_size,
                    bgcolor=self.point_color,
                    border_radius=self.point_size // 2,
                    left=x_pos - self.point_size // 2,
                    top=y_pos - self.point_size // 2,
                    animate=ft.Animation(self.animate_duration, ft.AnimationCurve.EASE_OUT)
                )
                chart_elements.append(point)
        
        # Create chart container
        chart_container = ft.Container(
            content=ft.Stack(chart_elements),
            width=self.chart_width + self.padding * 2,
            height=self.chart_height + self.padding * 2,
            padding=self.padding
        )
        
        # Create chart content
        chart_content = ft.Column([
            ft.Text(self.title, style=ft.TextThemeStyle.TITLE_LARGE) if self.title else None,
            chart_container
        ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        return chart_content


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
        
        # Default colors if none provided
        self.colors = colors or [
            ft.Colors.PRIMARY,
            ft.Colors.SECONDARY,
            ft.Colors.TERTIARY,
            ft.Colors.ERROR,
            ft.Colors.OUTLINE,
            ft.Colors.ON_SURFACE_VARIANT
        ]
        
        # Calculate total value
        self.total = sum([item[value_field] for item in data]) if data else 1
        
        # Chart dimensions
        self.chart_size = 200
        self.inner_radius = 0  # For donut chart, set to > 0
        
        # Build the chart
        self.content = self._build_chart()
        
        # Animation properties
        self.animate_scale = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
    
    def _build_chart(self) -> ft.Control:
        """Build the pie chart"""
        # Create pie slices
        slices = []
        current_angle = 0
        
        for i, item in enumerate(self.data):
            label = str(item[self.label_field])
            value = item[self.value_field]
            
            # Calculate angle for this slice
            angle = (value / self.total) * 360 if self.total > 0 else 0
            
            # Create slice (simplified representation)
            color = self.colors[i % len(self.colors)]
            slice_container = ft.Container(
                width=self.chart_size,
                height=self.chart_size,
                bgcolor=color,
                border_radius=self.chart_size // 2,
                animate=ft.Animation(self.animate_duration, ft.AnimationCurve.EASE_OUT),
                tooltip=f"{label}: {value} ({(value/self.total)*100:.1f}%)" if self.total > 0 else f"{label}: {value}"
            )
            
            slices.append(slice_container)
            current_angle += angle
        
        # Create chart container
        chart_stack = ft.Stack(slices)
        chart_container = ft.Container(
            content=chart_stack,
            width=self.chart_size,
            height=self.chart_size
        )
        
        # Create legend if labels are shown
        legend = None
        if self.show_labels:
            legend_items = []
            for i, item in enumerate(self.data):
                label = str(item[self.label_field])
                color = self.colors[i % len(self.colors)]
                
                legend_item = ft.Row([
                    ft.Container(width=12, height=12, bgcolor=color, border_radius=6),
                    ft.Text(label, size=12)
                ], spacing=8)
                
                legend_items.append(legend_item)
            
            legend = ft.Column(legend_items, spacing=8)
        
        # Create chart content
        content_items = []
        if self.title:
            content_items.append(ft.Text(self.title, style=ft.TextThemeStyle.TITLE_LARGE))
        
        chart_row = ft.Row([
            chart_container,
            legend
        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER) if legend else chart_container
        
        content_items.append(chart_row)
        
        chart_content = ft.Column(
            content_items,
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        return chart_content


# Factory functions for easy chart creation
def create_bar_chart(data: List[Dict[str, Union[str, int, float]]],
                    x_field: str,
                    y_field: str,
                    title: Optional[str] = None,
                    **kwargs) -> EnhancedBarChart:
    """Create an enhanced bar chart"""
    return EnhancedBarChart(data=data, x_field=x_field, y_field=y_field, title=title, **kwargs)

def create_line_chart(data: List[Dict[str, Union[str, int, float]]],
                     x_field: str,
                     y_field: str,
                     title: Optional[str] = None,
                     **kwargs) -> EnhancedLineChart:
    """Create an enhanced line chart"""
    return EnhancedLineChart(data=data, x_field=x_field, y_field=y_field, title=title, **kwargs)

def create_pie_chart(data: List[Dict[str, Union[str, int, float]]],
                    label_field: str,
                    value_field: str,
                    title: Optional[str] = None,
                     **kwargs) -> EnhancedPieChart:
    """Create an enhanced pie chart"""
    return EnhancedPieChart(data=data, label_field=label_field, value_field=value_field, title=title, **kwargs)