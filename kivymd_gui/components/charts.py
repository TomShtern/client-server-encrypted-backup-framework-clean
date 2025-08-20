"""
Enhanced chart components with Material Design 3 styling and real-time monitoring
"""

import time
from collections import deque
from typing import Optional

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.metrics import dp

# Optional imports with graceful fallbacks
try:
    import psutil
    SYSTEM_MONITOR_AVAILABLE = True
except ImportError:
    psutil = None
    SYSTEM_MONITOR_AVAILABLE = False
    print("[INFO] psutil not available - system monitoring disabled")

try:
    from kivy_garden.matplotlib import FigureCanvasKivyAgg
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    print("[INFO] kivy-garden.matplotlib not available - advanced charts disabled")


class MDPerformanceChart(MDCard):
    """Material Design 3 Performance Chart with real-time system monitoring"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.radius = dp(12)
        self.padding = dp(16)
        
        if CHARTS_AVAILABLE and SYSTEM_MONITOR_AVAILABLE:
            self._setup_chart()
        else:
            self._setup_fallback()
    
    def _setup_chart(self):
        """Setup matplotlib chart for performance monitoring"""
        # Create figure with Material Design styling
        self.figure = Figure(figsize=(6, 4), facecolor='none', edgecolor='none')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('none')
        
        # Apply Material Design 3 styling
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#666666')
        self.ax.spines['bottom'].set_color('#666666')
        self.ax.tick_params(colors='#666666', labelsize=8)
        self.ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        
        # Initialize data collections (60 second rolling window)
        self.cpu_data = deque(maxlen=60)
        self.mem_data = deque(maxlen=60)
        self.time_data = deque(maxlen=60)
        
        # Create performance lines with Material Design colors
        self.cpu_line, = self.ax.plot([], [], 
                                     color='#1976D2', linewidth=2.5, 
                                     label='CPU %', marker='o', markersize=2)
        self.mem_line, = self.ax.plot([], [], 
                                     color='#7C4DFF', linewidth=2.5, 
                                     label='Memory %', marker='s', markersize=2)
        
        # Configure chart appearance
        self.ax.set_ylim(0, 100)
        self.ax.set_ylabel('Usage (%)', color='#666666', fontsize=9)
        self.ax.set_xlabel('Time (seconds)', color='#666666', fontsize=9)
        self.ax.legend(loc='upper left', frameon=False, fontsize=8)
        self.ax.set_title('System Performance Monitor', color='#666666', fontsize=10, pad=10)
        
        # Add canvas to card
        self.canvas_widget = FigureCanvasKivyAgg(self.figure)
        self.add_widget(self.canvas_widget)
        
        # Schedule periodic updates
        self.update_event = Clock.schedule_interval(self.update_chart, 1.0)
        print("[INFO] Performance chart initialized with real-time monitoring")
    
    def _setup_fallback(self):
        """Setup fallback when dependencies are not available"""
        fallback_layout = MDBoxLayout(orientation="vertical", spacing=dp(8))
        
        fallback_layout.add_widget(MDLabel(
            text="📊 Performance Chart",
            font_style="Headline",
            theme_text_color="Primary",
            halign="center",
            size_hint_y=None,
            height=dp(32)
        ))
        
        missing_deps = []
        if not CHARTS_AVAILABLE:
            missing_deps.append("kivy-garden.matplotlib")
        if not SYSTEM_MONITOR_AVAILABLE:
            missing_deps.append("psutil")
            
        fallback_layout.add_widget(MDLabel(
            text=f"Missing dependencies: {', '.join(missing_deps)}\n\n"
                 "Install with:\n"
                 "pip install kivy-garden.matplotlib psutil",
            font_style="Body",
            theme_text_color="Secondary",
            halign="center"
        ))
        
        self.add_widget(fallback_layout)
    
    def update_chart(self, dt):
        """Update chart with current system metrics"""
        if not SYSTEM_MONITOR_AVAILABLE or not CHARTS_AVAILABLE:
            return
        
        try:
            # Get current system metrics
            now = time.time()
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            
            # Update data collections
            self.cpu_data.append(cpu)
            self.mem_data.append(mem)
            self.time_data.append(now)
            
            if len(self.time_data) > 1:
                # Convert to relative time for x-axis
                times = [t - self.time_data[0] for t in self.time_data]
                
                # Update line data
                self.cpu_line.set_data(times, list(self.cpu_data))
                self.mem_line.set_data(times, list(self.mem_data))
                
                # Update axis limits
                self.ax.set_xlim(0, max(times) if times else 60)
                self.ax.set_xlabel(f'Time (last {len(times)}s)', color='#666666', fontsize=9)
                
                # Refresh canvas
                self.canvas_widget.draw()
                
        except Exception as e:
            print(f"[WARNING] Chart update failed: {e}")
    
    def cleanup(self):
        """Clean up scheduled events when component is destroyed"""
        if hasattr(self, 'update_event') and self.update_event:
            self.update_event.cancel()


class ChartWidget(MDBoxLayout):
    """Base chart widget component - legacy compatibility"""
    
    def __init__(self, chart_type="line", **kwargs):
        super().__init__(**kwargs)
        self.chart_type = chart_type
        self.orientation = "vertical"
        
        # Use MDPerformanceChart for performance monitoring
        if chart_type.lower() in ["performance", "system", "monitor"]:
            if CHARTS_AVAILABLE and SYSTEM_MONITOR_AVAILABLE:
                self.add_widget(MDPerformanceChart())
                return
        
        # Fallback for other chart types
        self.add_widget(MDLabel(
            text=f"📊 {chart_type.upper()} Chart\n\n"
                 "Advanced charts require:\n"
                 "kivy-garden.matplotlib and psutil",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body"
        ))