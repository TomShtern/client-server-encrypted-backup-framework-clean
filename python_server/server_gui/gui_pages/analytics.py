# In file: gui_pages/analytics.py

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *  # Import all tkinter constants (BOTH, LEFT, RIGHT, etc.)
import time
from collections import deque
from typing import TYPE_CHECKING, Dict, Any, Deque

# Conditional imports for type checking and runtime
if TYPE_CHECKING:
    from ..ServerGUI import EnhancedServerGUI, RoundedFrame
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    from matplotlib.lines import Line2D
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import base class and check for dependencies
try:
    from ..ServerGUI import BasePage, CHARTS_AVAILABLE, SYSTEM_MONITOR_AVAILABLE, psutil
except ImportError:
    # Fallback for different import paths
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from ServerGUI import BasePage, CHARTS_AVAILABLE, SYSTEM_MONITOR_AVAILABLE, psutil
    except ImportError:
        # Define minimal fallbacks
        class BasePage:
            def __init__(self, parent, app, **kwargs): pass
        CHARTS_AVAILABLE = False
        SYSTEM_MONITOR_AVAILABLE = False
        psutil = None

class AnalyticsPage(BasePage):
    """A page dedicated to in-depth, larger visualizations of server performance."""

    def __init__(self, parent: tk.Widget, app: EnhancedServerGUI, **kwargs: Any) -> None:
        super().__init__(parent, app, **kwargs)

        # Chart data with a longer history
        self.history_data: Dict[str, Deque[Any]] = {
            'cpu': deque(maxlen=300),  # 5 minutes of data
            'memory': deque(maxlen=300),
            'time': deque(maxlen=300)
        }
        self.history_ax: Axes | None = None
        self.history_cpu_line: Line2D | None = None
        self.history_mem_line: Line2D | None = None
        self.history_chart: FigureCanvasTkAgg | None = None
        self.is_monitoring = False

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and lay out all widgets for the analytics page."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # You can add more charts here by changing the grid layout
        self._create_history_chart(self).grid(row=0, column=0, sticky=NSEW)
        
        # Placeholder for a future chart
        # placeholder = self.app.RoundedFrame(self, bg_color=self.app.style.colors.secondary, border_color=self.app.style.colors.border)
        # placeholder.grid(row=0, column=1, sticky=NSEW, padx=10)
        # ttk.Label(placeholder.content_frame, text="Future Network Chart", style='secondary.TLabel').pack(expand=True)

    def _create_history_chart(self, parent: ttk.Frame) -> RoundedFrame:
        """Create a larger, more detailed historical performance chart."""
        card = self.app.RoundedFrame(parent, bg_color=self.app.style.colors.secondary, border_color=self.app.style.colors.border)
        ttk.Label(card.content_frame, text="System Performance History (Last 5 Minutes)", style='secondary.TLabel', font=self.app.Theme.FONT_BOLD).pack(anchor=NW, padx=10, pady=5)

        if not CHARTS_AVAILABLE or not SYSTEM_MONITOR_AVAILABLE:
            ttk.Label(card.content_frame, text="Charts disabled (matplotlib/psutil not found)", style='secondary.TLabel').pack(expand=True)
            return card

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        fig = Figure(figsize=(10, 5), dpi=100, facecolor=self.app.style.colors.secondary)
        self.history_ax = fig.add_subplot(111)
        self.history_ax.set_facecolor(self.app.style.colors.bg)
        self.history_ax.tick_params(colors=self.app.style.colors.secondary)
        for spine in self.history_ax.spines.values(): spine.set_color(self.app.style.colors.border)
        
        self.history_cpu_line, = self.history_ax.plot([], [], color=self.app.style.colors.info, lw=2, label="CPU %")
        self.history_mem_line, = self.history_ax.plot([], [], color=self.app.style.colors.success, lw=2, label="Memory %")
        
        self.history_ax.set_ylim(0, 100)
        self.history_ax.set_xlabel("Time (seconds ago)", color=self.app.style.colors.secondary)
        self.history_ax.legend(loc='upper left', facecolor=self.app.style.colors.bg, labelcolor=self.app.style.colors.fg, frameon=False)
        fig.tight_layout(pad=1.5)

        self.history_chart = FigureCanvasTkAgg(fig, master=card.content_frame)
        self.history_chart.get_tk_widget().pack(fill=BOTH, expand=True, padx=5, pady=5)
        return card

    def _update_history_chart(self) -> None:
        """Polls psutil and updates the history chart."""
        if not all([self.is_monitoring, self.history_ax, self.history_chart, self.history_cpu_line, self.history_mem_line]):
            return

        cpu, mem = psutil.cpu_percent(), psutil.virtual_memory().percent
        self.history_data['cpu'].append(cpu)
        self.history_data['memory'].append(mem)
        
        # X-axis represents seconds ago, from -300 to 0
        data_len = len(self.history_data['cpu'])
        times = range(-data_len + 1, 1)

        self.history_ax.set_xlim(min(0, -data_len + 1), 0)
        self.history_cpu_line.set_data(times, list(self.history_data['cpu']))
        self.history_mem_line.set_data(times, list(self.history_data['memory']))
        
        self.history_chart.draw_idle()

    def start_monitoring(self) -> None:
        """Starts the periodic polling for this page only."""
        if self.is_monitoring or not self.app._tkthread: return
        self.is_monitoring = True
        
        def monitor_loop() -> None:
            while self.is_monitoring:
                self.app._tkthread.call(self._update_history_chart)
                time.sleep(1)
        
        self.app._tkthread.call_in_thread(monitor_loop)

    def stop_monitoring(self) -> None:
        """Stops the polling for this page to save resources."""
        self.is_monitoring = False
    
    def on_show(self) -> None:
        """Called when the page is displayed. Starts monitoring."""
        self.start_monitoring()

    def on_hide(self) -> None:
        """A custom method to be called when the page is hidden. Stops monitoring."""
        self.stop_monitoring()

    # We need to override the pack_forget method to call on_hide
    def pack_forget(self) -> None:
        self.on_hide()
        super().pack_forget()