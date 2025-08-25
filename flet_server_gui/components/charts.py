#!/usr/bin/env python3
"""
Enhanced Chart Components
Custom Material Design 3 charts and data visualizations.
"""

import flet as ft
from typing import List, Dict, Optional, Union
import math

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
