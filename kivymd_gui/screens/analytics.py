# -*- coding: utf-8 -*-
"""
analytics.py - Analytics screen with charts and metrics
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.segmentedbutton import MDSegmentedButton, MDSegmentedButtonItem
from kivy.metrics import dp
import os

try:
    from kivy_garden.matplotlib import FigureCanvasKivyAgg
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import matplotlib.style as style
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False

class AnalyticsScreen(MDScreen):
    """Material Design 3 Analytics Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "analytics"
        self._build_ui()
    
    def _build_ui(self):
        """Build analytics UI with charts"""
        layout = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(16))
        
        # Header
        header = MDLabel(
            text="Analytics & Insights",
            font_style="Display",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(56)
        )
        layout.add_widget(header)
        
        # Time range selector
        time_selector = MDSegmentedButton(
            MDSegmentedButtonItem(text="24h"),
            MDSegmentedButtonItem(text="7d"),
            MDSegmentedButtonItem(text="30d"),
            MDSegmentedButtonItem(text="All"),
            size_hint_y=None,
            height=dp(48)
        )
        time_selector.active = "7d"  # Set default selection
        layout.add_widget(time_selector)
        
        if CHARTS_AVAILABLE:
            # Charts grid
            charts_layout = MDBoxLayout(orientation="horizontal", spacing=dp(16))
            
            # Transfer volume chart
            self.transfer_chart = self._create_chart_card(
                "Transfer Volume",
                "Area chart showing data transfer over time"
            )
            charts_layout.add_widget(self.transfer_chart)
            
            # Client activity chart
            self.activity_chart = self._create_chart_card(
                "Client Activity",
                "Bar chart showing client connections"
            )
            charts_layout.add_widget(self.activity_chart)
            
            layout.add_widget(charts_layout)
            
            # Metrics cards
            metrics_layout = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(16),
                size_hint_y=None,
                height=dp(120)
            )
            
            # Calculate actual metrics from received files
            total_size, file_count = self._calculate_file_metrics()
            
            for title, value, change in [
                ("Total Transferred", total_size, "+15%"),
                ("Files Received", str(file_count), "+3"),
                ("Success Rate", "99.8%", "+0.2%"),
                ("Avg Size", self._calculate_avg_size(), "+5 MB")
            ]:
                metrics_layout.add_widget(self._create_metric_card(title, value, change))
            
            layout.add_widget(metrics_layout)
        else:
            layout.add_widget(MDLabel(
                text="Charts require kivy-garden.matplotlib\\nRun: pip install kivy-garden.matplotlib",
                theme_text_color="Secondary",
                halign="center"
            ))
        
        self.add_widget(layout)
    
    def _calculate_file_metrics(self):
        """Calculate metrics from actual received files"""
        try:
            received_files_dir = os.path.join(os.getcwd(), "received_files")
            if not os.path.exists(received_files_dir):
                return "0 B", 0
            
            total_size = 0
            file_count = 0
            
            for filename in os.listdir(received_files_dir):
                file_path = os.path.join(received_files_dir, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            return self._format_file_size(total_size), file_count
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return "0 B", 0
    
    def _calculate_avg_size(self):
        """Calculate average file size"""
        try:
            received_files_dir = os.path.join(os.getcwd(), "received_files")
            if not os.path.exists(received_files_dir):
                return "0 B"
            
            total_size = 0
            file_count = 0
            
            for filename in os.listdir(received_files_dir):
                file_path = os.path.join(received_files_dir, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            if file_count == 0:
                return "0 B"
            
            avg_size = total_size / file_count
            return self._format_file_size(avg_size)
        except Exception as e:
            print(f"Error calculating average size: {e}")
            return "0 B"
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _create_chart_card(self, title, subtitle):
        """Create a chart card with Material Design styling"""
        card = MDCard(
            md_bg_color=self.theme_cls.surfaceVariantColor,
            elevation=1,
            radius=dp(12),
            padding=dp(16)
        )
        
        layout = MDBoxLayout(orientation="vertical")
        layout.add_widget(MDLabel(text=title, font_style="Title"))
        layout.add_widget(MDLabel(text=subtitle, font_style="Body", theme_text_color="Secondary"))
        
        if CHARTS_AVAILABLE:
            # Set dark theme for matplotlib
            style.use('dark_background')
            
            fig = Figure(figsize=(4, 3), facecolor="none")
            ax = fig.add_subplot(111)
            ax.set_facecolor("none")
            
            # Sample data - replace with actual analytics data
            import numpy as np
            if "Transfer Volume" in title:
                # Create area chart for transfer volume
                x = np.linspace(0, 24, 24)  # 24 hours
                y = np.random.exponential(2, 24) * 10  # Random transfer data
                ax.plot(x, y, color="#1976D2", linewidth=2, label="MB/hour")
                ax.fill_between(x, y, alpha=0.3, color="#1976D2")
                ax.set_xlabel("Hours")
                ax.set_ylabel("MB")
            else:
                # Create bar chart for client activity
                clients = ['Client-1', 'Client-2', 'Client-3', 'Client-4']
                connections = [15, 8, 12, 5]
                bars = ax.bar(clients, connections, color="#1976D2", alpha=0.7)
                ax.set_ylabel("Connections")
                ax.set_xticklabels(clients, rotation=45)
            
            # Style the plot
            ax.grid(True, alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            canvas = FigureCanvasKivyAgg(fig)
            layout.add_widget(canvas)
        
        card.add_widget(layout)
        return card
    
    def _create_metric_card(self, title, value, change):
        """Create a metric card"""
        card = MDCard(
            md_bg_color=self.theme_cls.surfaceVariantColor,
            elevation=1,
            radius=dp(12),
            padding=dp(12)
        )
        
        layout = MDBoxLayout(orientation="vertical")
        layout.add_widget(MDLabel(
            text=title,
            font_style="Label",
            theme_text_color="Secondary"
        ))
        layout.add_widget(MDLabel(
            text=str(value),
            font_style="Headline",
            theme_text_color="Primary"
        ))
        
        # Determine change color
        if isinstance(change, str):
            change_color = [0, 0.8, 0, 1] if change.startswith("+") else [0.8, 0, 0, 1]
        else:
            change_color = [0.6, 0.6, 0.6, 1]  # Neutral color
            
        layout.add_widget(MDLabel(
            text=str(change),
            font_style="Body",
            theme_text_color="Custom",
            text_color=change_color
        ))
        
        card.add_widget(layout)
        return card
    
    def on_enter(self):
        """Called when the screen is entered"""
        # Refresh analytics data
        if hasattr(self, 'transfer_chart'):
            # Update charts with fresh data
            pass