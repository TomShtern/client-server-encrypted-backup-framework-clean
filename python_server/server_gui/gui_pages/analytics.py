# -*- coding: utf-8 -*-
"""
analytics.py - The Data Visualization & Analytics page.

This page provides large, detailed, and interactive charts for deep analysis
of server performance and backup history over time.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any

try:
    import ttkbootstrap as ttk
    from ttkbootstrap import constants
except ImportError:
    from tkinter import ttk, constants

from .base_page import BasePage

# Optional Dependency for Charts
try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates
    CHARTS_AVAILABLE = True
except ImportError:
    # Create stub classes for type checking when matplotlib is not available
    CHARTS_AVAILABLE = False
    FigureCanvasTkAgg = None
    Figure = None  # type: ignore
    mdates = None  # type: ignore

if TYPE_CHECKING:
    from ..ServerGUI import ServerGUI
    if CHARTS_AVAILABLE:
        from matplotlib.axes import Axes
        from matplotlib.lines import Line2D

class AnalyticsPage(BasePage):
    """A page for displaying detailed performance and analytics charts."""

    def __init__(self, parent: ttk.Frame, controller: 'ServerGUI') -> None:
        super().__init__(parent, controller)
        self._create_widgets()
        if CHARTS_AVAILABLE:
            self._update_performance_chart()

    def _create_widgets(self) -> None:
        self._create_page_header("Analytics Dashboard", "graph-up-arrow")
        self._create_separator()
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=constants.BOTH, expand=True, padx=10, pady=(0, 10))

        # We can use a Notebook for multiple chart tabs or a PanedWindow for side-by-side
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=constants.BOTH, expand=True)
        
        # --- Tab 1: System Performance ---
        perf_tab = ttk.Frame(notebook, padding=10)
        notebook.add(perf_tab, text=" System Performance ")
        self._create_performance_chart_widget(perf_tab).pack(fill=constants.BOTH, expand=True)

        # --- Tab 2: Network Throughput (Placeholder) ---
        network_tab = ttk.Frame(notebook, padding=10)
        notebook.add(network_tab, text=" Network I/O ")
        if CHARTS_AVAILABLE:
            self._create_placeholder("Network throughput chart coming soon!", "reception-4").pack(expand=True)
        else:
            self._create_placeholder("Install matplotlib for network charts", "reception-4").pack(expand=True)

        # --- Tab 3: Backup History (Placeholder) ---
        history_tab = ttk.Frame(notebook, padding=10)
        notebook.add(history_tab, text=" Backup History ")
        if CHARTS_AVAILABLE:
            self._create_placeholder("Backup success/failure history coming soon!", "clock-history").pack(expand=True)
        else:
            self._create_placeholder("Install matplotlib for backup history charts", "clock-history").pack(expand=True)

    def _create_performance_chart_widget(self, parent: ttk.Frame) -> ttk.Frame:
        """Creates the large, detailed Matplotlib chart for system performance."""
        if not CHARTS_AVAILABLE or not FigureCanvasTkAgg or Figure is None:
            return self._create_placeholder("Charts require Matplotlib", "graph-up-arrow")
            
        # Get theme colors with fallbacks
        try:
            style_obj = getattr(self.controller.root, 'style', None)
            colors = getattr(style_obj, 'colors', None) if style_obj else None
            if colors:
                bg_color = getattr(colors, 'bg', '#ffffff')
                fg_color = getattr(colors, 'fg', '#000000')
                input_color = getattr(colors, 'inputbg', '#f0f0f0')
                border_color = getattr(colors, 'border', '#cccccc')
                info_color = getattr(colors, 'info', '#007bff')
                warning_color = getattr(colors, 'warning', '#ffc107')
            else:
                raise AttributeError("Style colors not available")
        except (AttributeError, TypeError):
            # Fallback colors if style system is not available
            bg_color, fg_color, input_color = '#ffffff', '#000000', '#f0f0f0'
            border_color, info_color, warning_color = '#cccccc', '#007bff', '#ffc107'
            
        fig = Figure(figsize=(10, 6), dpi=100)
        fig.patch.set_facecolor(bg_color)
        self.ax: 'Axes' = fig.add_subplot(111, facecolor=input_color)
        self.ax.tick_params(colors=fg_color, labelsize=9)  # type: ignore[misc]
        for spine in self.ax.spines.values(): spine.set_color(border_color)
        
        self.ax.set_ylim(0, 105)
        self.ax.set_ylabel("Usage %", fontsize=10, color=fg_color)  # type: ignore[misc]
        self.ax.set_title("Live System Performance (Last 2 Minutes)", fontsize=12, color=fg_color)  # type: ignore[misc]
        if mdates is not None:
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.grid(True, which='major', linestyle='--', linewidth=0.5, color=border_color)  # type: ignore[misc]

        self.cpu_line: 'Line2D'
        self.mem_line: 'Line2D'
        self.cpu_line, = self.ax.plot([], [], color=info_color, lw=2, label="CPU %", marker='o', markersize=2, linestyle='-')  # type: ignore[misc]
        self.mem_line, = self.ax.plot([], [], color=warning_color, lw=2, label="Memory %", marker='o', markersize=2, linestyle='-')  # type: ignore[misc]
        
        # Configure legend (returned object not needed)
        self.ax.legend(loc='upper left', fontsize=9, facecolor=input_color,  # type: ignore[misc]
                      labelcolor=fg_color, frameon=True, edgecolor=border_color)
        fig.tight_layout(pad=2)
        
        # Create a frame to contain the canvas
        chart_frame = ttk.Frame(parent)
        self.canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill=constants.BOTH, expand=True)
        return chart_frame

    def _update_performance_chart(self) -> None:
        """Recurring function to redraw the performance chart with the latest data."""
        if CHARTS_AVAILABLE and hasattr(self, 'canvas') and hasattr(self, 'ax'):
            try:
                data = self.controller.performance_data
                if len(data['time']) > 1:
                    self.cpu_line.set_data(data['time'], data['cpu'])
                    self.mem_line.set_data(data['time'], data['memory'])
                    self.ax.set_xlim(data['time'][0], data['time'][-1])
                    self.ax.relim()
                    self.ax.autoscale_view(True, False)
                    self.canvas.draw_idle()
            except (AttributeError, KeyError, IndexError):
                # Handle cases where performance data is not available or malformed
                pass
        
        # Schedule next update only if we're still active
        if hasattr(self, 'winfo_exists') and self.winfo_exists():
            self.after(2000, self._update_performance_chart)

    def handle_update(self, update_type: str, data: Dict[str, Any]) -> None:
        """Analytics page currently updates via its own recurring timer, not backend pushes."""
        # Parameters intentionally unused - this page uses timer-based updates
        _ = update_type, data