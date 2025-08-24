#!/usr/bin/env python3
"""
Analytics View Component
Material Design 3 view for data visualization and analytics.
"""

import flet as ft
from typing import List, Dict, Any
import random


class AnalyticsView:
    """Analytics view with charts and data visualization"""
    
    def __init__(self, server_bridge):
        self.server_bridge = server_bridge
        # Mock data for charts
        self.transfer_data = [
            {"hour": "00:00", "transfers": random.randint(5, 20)},
            {"hour": "04:00", "transfers": random.randint(2, 10)},
            {"hour": "08:00", "transfers": random.randint(15, 40)},
            {"hour": "12:00", "transfers": random.randint(20, 50)},
            {"hour": "16:00", "transfers": random.randint(25, 60)},
            {"hour": "20:00", "transfers": random.randint(30, 70)},
        ]
        
        self.client_data = [
            {"client": "Client A", "files": 120, "size": "2.4 GB"},
            {"client": "Client B", "files": 85, "size": "1.8 GB"},
            {"client": "Client C", "files": 210, "size": "4.2 GB"},
            {"client": "Client D", "files": 65, "size": "1.1 GB"},
            {"client": "Client E", "files": 150, "size": "3.0 GB"},
        ]
    
    def build(self) -> ft.Control:
        """Build the analytics view"""
        
        # Transfer activity chart (simplified bar chart representation)
        transfer_chart = self._create_transfer_chart()
        
        # Client distribution chart (simplified pie chart representation)
        client_chart = self._create_client_chart()
        
        # Analytics cards
        analytics_cards = ft.ResponsiveRow([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.TRENDING_UP, size=32, color=ft.Colors.GREEN),
                        ft.Text("Total Transfers", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text("1,248", style=ft.TextThemeStyle.DISPLAY_MEDIUM, weight=ft.FontWeight.BOLD),
                        ft.Text("+12% from last week", size=12, color=ft.Colors.GREEN),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 3}
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PEOPLE, size=32, color=ft.Colors.BLUE),
                        ft.Text("Active Clients", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text("42", style=ft.TextThemeStyle.DISPLAY_MEDIUM, weight=ft.FontWeight.BOLD),
                        ft.Text("+3 from yesterday", size=12, color=ft.Colors.GREEN),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 3}
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.STORAGE, size=32, color=ft.Colors.PURPLE),
                        ft.Text("Data Transferred", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text("24.8 TB", style=ft.TextThemeStyle.DISPLAY_MEDIUM, weight=ft.FontWeight.BOLD),
                        ft.Text("+5.2 TB this week", size=12, color=ft.Colors.GREEN),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 3}
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ACCESS_TIME, size=32, color=ft.Colors.ORANGE),
                        ft.Text("Avg. Transfer Time", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text("2.4s", style=ft.TextThemeStyle.DISPLAY_MEDIUM, weight=ft.FontWeight.BOLD),
                        ft.Text("-0.3s from last week", size=12, color=ft.Colors.GREEN),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 3}
            ),
        ], spacing=20)
        
        # Header with title and controls
        header = ft.Row([
            ft.Text("Analytics", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.IconButton(ft.Icons.REFRESH, tooltip="Refresh", on_click=self._on_refresh),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Time range selector
        time_selector = ft.Row([
            ft.Chip(label=ft.Text("24 Hours"), on_click=self._on_time_range_24h),
            ft.Chip(label=ft.Text("7 Days"), on_click=self._on_time_range_7d),
            ft.Chip(label=ft.Text("30 Days"), on_click=self._on_time_range_30d),
            ft.Chip(label=ft.Text("90 Days"), on_click=self._on_time_range_90d),
        ])
        
        return ft.Column([
            header,
            ft.Divider(),
            analytics_cards,
            ft.Divider(),
            time_selector,
            ft.Divider(),
            ft.Text("Transfer Activity (24h)", style=ft.TextThemeStyle.TITLE_LARGE),
            transfer_chart,
            ft.Divider(),
            ft.Text("Client Distribution", style=ft.TextThemeStyle.TITLE_LARGE),
            client_chart,
        ], spacing=20, expand=True, scroll=ft.ScrollMode.ADAPTIVE)
    
    def _create_transfer_chart(self) -> ft.Control:
        """Create a simple bar chart representation for transfer activity"""
        max_transfers = max([d["transfers"] for d in self.transfer_data])
        
        bars = []
        for data in self.transfer_data:
            height = (data["transfers"] / max_transfers) * 200  # Scale to 200px max
            bar = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=None,
                        width=30,
                        height=height,
                        bgcolor=ft.Colors.BLUE,
                        border_radius=ft.border_radius.only(top_left=5, top_right=5),
                    ),
                    ft.Text(str(data["transfers"]), size=12),
                    ft.Text(data["hour"], size=10, color=ft.Colors.GREY),
                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            )
            bars.append(bar)
        
        chart = ft.Row(bars, spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        return ft.Container(content=chart, padding=20)
    
    def _create_client_chart(self) -> ft.Control:
        """Create a simple pie chart representation for client distribution"""
        # Simplified pie chart using colored segments
        segments = []
        colors = [ft.Colors.BLUE, ft.Colors.GREEN, ft.Colors.ORANGE, ft.Colors.PURPLE, ft.Colors.RED]
        
        for i, data in enumerate(self.client_data):
            segment = ft.Container(
                content=ft.Row([
                    ft.Container(width=20, height=20, bgcolor=colors[i], border_radius=10),
                    ft.Text(f"{data['client']}: {data['files']} files ({data['size']})"),
                ], spacing=10),
                padding=5,
            )
            segments.append(segment)
        
        legend = ft.Column(segments, spacing=10)
        
        # Create a simple pie visualization
        pie_visual = ft.Container(
            content=ft.Stack([
                ft.Container(
                    content=None,
                    width=200,
                    height=200,
                    border_radius=100,
                    bgcolor=ft.Colors.GREY_300,
                ),
                # Simplified pie segments (would be more complex in a real implementation)
                ft.Container(
                    content=None,
                    width=200,
                    height=200,
                    border_radius=100,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=[ft.Colors.BLUE, ft.Colors.PURPLE],
                    ),
                ),
            ]),
            width=200,
            height=200,
        )
        
        chart = ft.Row([
            pie_visual,
            ft.VerticalDivider(),
            legend,
        ], spacing=20, expand=True)
        
        return ft.Container(content=chart, padding=20)

    def _on_refresh(self, e):
        """Handle refresh button click"""
        print("Refreshing analytics view")
        # In a real implementation, this would refresh all analytics data

    def _on_time_range_24h(self, e):
        """Handle 24 hours time range selection"""
        print("Time range: 24h")
        # In a real implementation, this would filter data to last 24 hours

    def _on_time_range_7d(self, e):
        """Handle 7 days time range selection"""
        print("Time range: 7d")
        # In a real implementation, this would filter data to last 7 days

    def _on_time_range_30d(self, e):
        """Handle 30 days time range selection"""
        print("Time range: 30d")
        # In a real implementation, this would filter data to last 30 days

    def _on_time_range_90d(self, e):
        """Handle 90 days time range selection"""
        print("Time range: 90d")
        # In a real implementation, this would filter data to last 90 days