#!/usr/bin/env python3
"""
Test script for enhanced UI components
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import flet as ft
from flet_server_gui.ui.widgets import (
    EnhancedButton,
    EnhancedCard,
    EnhancedChart,
    EnhancedTable,
    EnhancedWidget,
    EnhancedButtonConfig,
    EnhancedCardConfig,
    ButtonVariant,
    CardVariant,
    ChartType,
    ChartDataPoint,
    ChartSeries,
    EnhancedChartConfig,
    TableColumn,
    TableConfig,
    WidgetConfig,
    WidgetType,
    WidgetSize
)


def main(page: ft.Page):
    # Configure the page
    page.title = "Enhanced Components Test"
    page.scroll = ft.ScrollMode.AUTO
    
    # Test Enhanced Button
    button_config = EnhancedButtonConfig(
        text="Click Me",
        variant=ButtonVariant.FILLED,
        on_click=lambda e: print("Button clicked!")
    )
    enhanced_button = EnhancedButton(page, button_config)
    
    # Test Enhanced Card
    card_config = EnhancedCardConfig(
        title="Test Card",
        content="This is a test card content",
        variant=CardVariant.ELEVATED
    )
    enhanced_card = EnhancedCard(page, card_config)
    
    # Test Enhanced Chart
    data_points = [
        ChartDataPoint(x=1, y=10),
        ChartDataPoint(x=2, y=20),
        ChartDataPoint(x=3, y=15)
    ]
    series = ChartSeries(name="Test Series", data=data_points)
    chart_config = EnhancedChartConfig(
        title="Test Chart",
        series=[series],
        chart_type=ChartType.LINE
    )
    enhanced_chart = EnhancedChart(page, chart_config)
    
    # Test Enhanced Table
    columns = [
        TableColumn(name="id", label="ID", numeric=True),
        TableColumn(name="name", label="Name")
    ]
    data = [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"}
    ]
    table_config = TableConfig(columns=columns, data=data)
    enhanced_table = EnhancedTable(page, table_config)
    
    # Test Enhanced Widget
    widget_config = WidgetConfig(
        title="Test Widget",
        widget_type=WidgetType.STAT,
        content="Widget content",
        size=WidgetSize.MEDIUM
    )
    enhanced_widget = EnhancedWidget(page, widget_config)
    
    # Create layout
    layout = ft.Column([
        ft.Text("Enhanced Components Test", size=32, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Text("Enhanced Button:", size=20, weight=ft.FontWeight.W_500),
        enhanced_button.get_control(),
        ft.Divider(),
        ft.Text("Enhanced Card:", size=20, weight=ft.FontWeight.W_500),
        enhanced_card.get_control(),
        ft.Divider(),
        ft.Text("Enhanced Chart:", size=20, weight=ft.FontWeight.W_500),
        enhanced_chart.get_control(),
        ft.Divider(),
        ft.Text("Enhanced Table:", size=20, weight=ft.FontWeight.W_500),
        enhanced_table.get_control(),
        ft.Divider(),
        ft.Text("Enhanced Widget:", size=20, weight=ft.FontWeight.W_500),
        enhanced_widget.get_control(),
    ], spacing=20)
    
    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main)