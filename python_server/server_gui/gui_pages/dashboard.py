# -*- coding: utf-8 -*-
"""
dashboard.py - The main command center page for the Server GUI.

This is a high-density information radiator, providing a rich, dynamic, and
visually engaging overview of the server's complete status and performance.
"""

from __future__ import annotations
import contextlib
import time
from datetime import timedelta, datetime
import shutil
from typing import TYPE_CHECKING, Dict, Any

# --- Widget Toolkit Import ---
try:
    import ttkbootstrap as ttk
    # Use the correct, safe constants import pattern
    from ttkbootstrap import constants
    from ttkbootstrap.widgets import Meter
except ImportError:
    from tkinter import ttk, constants
    try:
        from ttkbootstrap.widgets import Meter
    except ImportError:
        Meter = None  # Fallback when ttkbootstrap unavailable

# Essential tkinter imports
import tkinter as tk
from tkinter import NORMAL, DISABLED, LEFT

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
    Figure = None  # Ensure Figure is always defined
    CHARTS_AVAILABLE = False
    FigureCanvasTkAgg = None

if TYPE_CHECKING:
    from ..ServerGUI import ServerGUI
    if CHARTS_AVAILABLE:
        from matplotlib.axes import Axes
        # from matplotlib.lines import Line2D  # Currently unused
elif CHARTS_AVAILABLE:
    # Runtime imports for proper typing
    try:
        from matplotlib.backend_bases import MouseEvent
    except ImportError:
        MouseEvent = None  # Fallback type


def _get_color(colors: Dict[str, str] | object, key: str, default: str = '#f0f0f0') -> str:
    """Safely get a color value from colors, supporting dict or object."""
    if isinstance(colors, dict):
        return colors.get(key, default)  # type: ignore[return-value]
    return getattr(colors, key, default)


class DashboardPage(BasePage):
    """The main dashboard view, acting as a command center."""

    def __init__(self, parent: ttk.Frame, controller: 'ServerGUI') -> None:
        super().__init__(parent, controller)
        self.server_start_time: float = 0.0

        self._create_widgets()
        self._setup_text_tags()
        self._update_uptime()

    def _create_widgets(self) -> None:
        """Create and lay out all dashboard widgets."""
        # Main layout using a PanedWindow for resizability (Layer 3 polish)
        main_pane = ttk.PanedWindow(self, orient=constants.HORIZONTAL)
        main_pane.pack(fill=constants.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_pane)
        left_frame.rowconfigure(0, weight=1) # Stat cards
        left_frame.rowconfigure(1, weight=2) # Performance Chart
        left_frame.columnconfigure(0, weight=1)
        
        right_frame = ttk.Frame(main_pane)
        right_frame.rowconfigure(0, weight=1) # Control Panel
        right_frame.rowconfigure(1, weight=1) # Meter Grid
        right_frame.rowconfigure(2, weight=1) # Activity Ticker
        right_frame.columnconfigure(0, weight=1)
        
        main_pane.add(left_frame, weight=3)  # type: ignore[misc]
        main_pane.add(right_frame, weight=2)  # type: ignore[misc]

        # --- Populate Left Frame ---
        self._create_stat_cards_grid(left_frame).grid(row=0, column=0, sticky=constants.NSEW, pady=(0, 5))
        self._create_performance_chart(left_frame).grid(row=1, column=0, sticky=constants.NSEW, pady=(5, 0))

        # --- Populate Right Frame ---
        self._create_control_panel(right_frame).grid(row=0, column=0, sticky=constants.NSEW, pady=(0, 5))
        self._create_meter_grid(right_frame).grid(row=1, column=0, sticky=constants.NSEW, pady=5)
        self._create_activity_ticker(right_frame).grid(row=2, column=0, sticky=constants.NSEW, pady=(5, 0))

    def _create_performance_chart(self, parent: ttk.Frame) -> ttk.Frame:
        card = ttk.Frame(parent, padding=20, style='secondary.TFrame', borderwidth=1, relief="solid")
        card.rowconfigure(1, weight=1)
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Live System Performance", font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, sticky='w')

        if not CHARTS_AVAILABLE or Figure is None:
            placeholder = ttk.Label(card, text="Matplotlib not found. Charts unavailable.", font=('Segoe UI', 10))
            placeholder.grid(row=1, column=0, pady=20)
            return card

        fig = Figure(figsize=(5, 3), dpi=100)
        colors = getattr(self.controller.root.style, 'colors', {})
        fig.patch.set_facecolor(_get_color(colors, 'secondary', '#f0f0f0'))
        self.ax: 'Axes' = fig.add_subplot(111)
        self.ax.set_facecolor(_get_color(colors, 'inputbg', '#ffffff'))
        self.ax.tick_params(colors=_get_color(colors, 'fg', '#222222'), labelsize=8)  # type: ignore[misc]
        for spine in self.ax.spines.values():
            spine.set_color(_get_color(colors, 'border', '#cccccc'))
        self.ax.set_ylim(0, 105)
        self.ax.set_ylabel("Usage %", fontsize=9, color=_get_color(colors, 'fg', '#222222'))  # type: ignore[misc]
        if CHARTS_AVAILABLE and 'mdates' in globals():
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))  # type: ignore[misc]

        self.cpu_line, = self.ax.plot([], [], color=_get_color(colors, 'info', '#007bff'), lw=2, label="CPU %")  # type: ignore[misc]
        self.mem_line, = self.ax.plot([], [], color=_get_color(colors, 'warning', '#ffc107'), lw=2, label="Memory %")  # type: ignore[misc]

        self.ax.legend(loc='upper left', fontsize=8).get_frame().set_alpha(0)  # type: ignore[misc]
        fig.tight_layout(pad=1.5)

        if CHARTS_AVAILABLE:
            with contextlib.suppress(NameError):
                self.canvas = FigureCanvasTkAgg(fig, master=card)  # type: ignore[misc]
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky='nsew', pady=(10,0))

        # Interactive Hover Tooltip
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",  # type: ignore[misc]
                                      bbox=dict(boxstyle="round", fc="w", alpha=0.7), arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        if hasattr(self, 'canvas'):
            self.canvas.mpl_connect("motion_notify_event", self._on_chart_hover)  # type: ignore[misc]
        return card

    def _create_stat_cards_grid(self, parent: ttk.Frame) -> ttk.Frame:
        card = ttk.Frame(parent, padding=20, style='secondary.TFrame', borderwidth=1, relief="solid")
        card.columnconfigure((0,1,2,3), weight=1)
        
        # This grid preserves all stats from the original monolithic GUI
        kpi_widgets = {
            'status': self._create_kpi_widget(card, "Server Status", "-"),
            'address': self._create_kpi_widget(card, "Address", "-"),
            'uptime': self._create_kpi_widget(card, "Uptime", "0:00:00"),
            'total_clients': self._create_kpi_widget(card, "Total Clients", "0"),
            'total_transferred': self._create_kpi_widget(card, "Total Transferred", "0 MB"),
            'transfer_rate': self._create_kpi_widget(card, "Transfer Rate", "0 KB/s"),
            'last_cleanup': self._create_kpi_widget(card, "Last Cleanup", "Never"),
            'files_cleaned': self._create_kpi_widget(card, "Files Cleaned", "0")
        }
        
        # Extract labels for easy access
        self.kpi_labels: Dict[str, ttk.Label] = {k: v[0] for k, v in kpi_widgets.items()}
        
        # Layout the KPI widgets
        kpi_keys = ['status', 'address', 'uptime', 'total_clients', 
                   'total_transferred', 'transfer_rate', 'last_cleanup', 'files_cleaned']
        
        for i, key in enumerate(kpi_keys):
            row = i // 4
            col = i % 4
            kpi_widgets[key][1].grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
        
        return card

    def _create_kpi_widget(self, parent: ttk.Frame, title: str, initial_value: str) -> tuple[ttk.Label, ttk.Frame]:
        frame = ttk.Frame(parent, style='secondary.TFrame')
        ttk.Label(frame, text=title, font=('Segoe UI', 9, 'bold'), style='secondary.TLabel').pack()
        value_label = ttk.Label(frame, text=initial_value, font=('Segoe UI Semibold', 14), style='secondary.TLabel')
        value_label.pack()
        return value_label, frame

    def _create_control_panel(self, parent: ttk.Frame) -> ttk.Frame:
        card = ttk.Frame(parent, padding=20, style='secondary.TFrame', borderwidth=1, relief="solid")
        card.columnconfigure(0, weight=1)
        ttk.Label(card, text="Control Panel", font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 10))
        self.btn_start = ttk.Button(card, text=" Start Server", command=self.controller.start_server, style='success.TButton', image=self.controller.asset_manager.get_icon('play-circle-fill'), compound=LEFT)
        self.btn_stop = ttk.Button(card, text=" Stop Server", command=self.controller.stop_server, style='danger.TButton', image=self.controller.asset_manager.get_icon('stop-circle-fill'), compound=LEFT, state=DISABLED)
        self.btn_restart = ttk.Button(card, text=" Restart Server", command=self.controller.restart_server, style='warning.TButton', image=self.controller.asset_manager.get_icon('arrow-clockwise'), compound=LEFT, state=DISABLED)
        btn_backup_db = ttk.Button(card, text=" Backup DB", command=self.controller.backup_database, style='info.Outline.TButton', image=self.controller.asset_manager.get_icon('database-down'), compound=LEFT)

        self.btn_start.grid(row=1, column=0, sticky='ew', pady=4, ipady=8)
        self.btn_stop.grid(row=2, column=0, sticky='ew', pady=4, ipady=8)
        self.btn_restart.grid(row=3, column=0, sticky='ew', pady=4, ipady=8)
        btn_backup_db.grid(row=4, column=0, sticky='ew', pady=(10, 0), ipady=8)
        return card

    def _create_meter_grid(self, parent: ttk.Frame) -> ttk.Frame:
        card = ttk.Frame(parent, padding=10, style='secondary.TFrame', borderwidth=1, relief="solid")
        card.columnconfigure((0, 1), weight=1)
        card.rowconfigure(0, weight=1)
        
        if Meter is not None:
            self.client_meter = Meter(card, metersize=150, padding=10, amounttotal=1, amountused=0, metertype='semi', subtext="Client Load", interactive=False, bootstyle='primary', textright='/ 50')
            self.client_meter.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
            
            self.disk_meter = Meter(card, metersize=150, padding=10, amountused=0, metertype='semi', subtext="Disk Usage", interactive=False, bootstyle='danger', textright='%')
            self.disk_meter.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        else:
            # Fallback when Meter is unavailable
            placeholder = ttk.Label(card, text="Meter widgets unavailable.\nInstall ttkbootstrap for enhanced meters.")
            placeholder.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            self.client_meter = None
            self.disk_meter = None
        return card

    def _create_activity_ticker(self, parent: ttk.Frame) -> ttk.Frame:
        card = ttk.Frame(parent, padding=20, style='secondary.TFrame', borderwidth=1, relief="solid")
        card.rowconfigure(1, weight=1)
        card.columnconfigure(0, weight=1)
        ttk.Label(card, text="Recent Activity", font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 10))
        colors = getattr(self.controller.root.style, 'colors', {})
        self.ticker_text = tk.Text(card,
            bg=_get_color(colors, 'inputbg', '#ffffff'),
            fg=_get_color(colors, 'fg', '#222222'),
            font=('Consolas', 9), relief='flat', height=5, wrap='word', state=DISABLED, bd=0)
        self.ticker_text.grid(row=1, column=0, sticky='nsew')
        return card

    def _setup_text_tags(self):
        colors = getattr(self.controller.root.style, 'colors', {})
        self.ticker_text.tag_configure("success", foreground=_get_color(colors, 'success', '#28a745'))
        self.ticker_text.tag_configure("error", foreground=_get_color(colors, 'danger', '#dc3545'))
        self.ticker_text.tag_configure("warning", foreground=_get_color(colors, 'warning', '#ffc107'))
        self.ticker_text.tag_configure("info", foreground=_get_color(colors, 'info', '#007bff'))
        self.ticker_text.tag_configure("timestamp", foreground=_get_color(colors, 'secondary', '#6c757d'))

    def _update_uptime(self):
        if self.server_start_time > 0:
            uptime_delta = timedelta(seconds=int(time.time() - self.server_start_time))
            self.kpi_labels['uptime'].config(text=str(uptime_delta))
        self.after(1000, self._update_uptime)

    def _on_chart_hover(self, event: Any) -> None:
        if not hasattr(event, 'inaxes') or getattr(event, 'inaxes', None) != self.ax:
            if hasattr(self, 'annot'):
                self.annot.set_visible(False)
                self.canvas.draw_idle()
            return

        if hasattr(self, 'annot'):
            self._extracted_from__on_chart_hover_9(event)

    # TODO Rename this here and in `_on_chart_hover`
    def _extracted_from__on_chart_hover_9(self, event: Any) -> None:
        self.annot.set_visible(True)
        # This part is complex. We find the closest data point to the mouse.
        min_dist = float('inf')
        closest_point = None
        for line in [self.cpu_line, self.mem_line]:
            xdata, ydata = line.get_data()
            # Safe length check for array-like objects
            try:
                # Handle matplotlib ArrayLike objects safely
                if hasattr(xdata, '__len__'):
                    try:
                        x_len = len(xdata)  # type: ignore[arg-type]
                    except TypeError:
                        # Handle Buffer-like objects that don't support len()
                        x_len = 0
                elif hasattr(xdata, '__iter__'):
                    try:
                        x_len = len(list(xdata))  # type: ignore[arg-type]
                    except TypeError:
                        x_len = 0
                else:
                    x_len = 0
                if x_len == 0:
                    continue
            except (TypeError, AttributeError):
                continue

            # This is a simplified distance check; more accurate methods exist
            try:
                # Safe conversion to iterable for matplotlib ArrayLike objects
                if hasattr(xdata, 'tolist'):
                    x_list = xdata.tolist()  # type: ignore[attr-defined]
                elif hasattr(xdata, '__iter__'):
                    x_list = list(xdata)  # type: ignore[arg-type]
                else:
                    x_list = []

                if hasattr(ydata, 'tolist'):
                    y_list = ydata.tolist()  # type: ignore[attr-defined]
                elif hasattr(ydata, '__iter__'):
                    y_list = list(ydata)  # type: ignore[arg-type]
                else:
                    y_list = []

                for x, y in zip(x_list, y_list):
                    event_xdata = getattr(event, 'xdata', None)
                    if hasattr(event, 'xdata') and event_xdata is not None and CHARTS_AVAILABLE and 'mdates' in globals():
                        dist = (mdates.date2num(x) - event_xdata)**2  # type: ignore[misc]
                        if dist < min_dist:
                            min_dist = dist
                            closest_point = (x, y, line.get_label())
            except (TypeError, AttributeError, ValueError):
                continue

        if closest_point:
            x, y, label = closest_point
            self.annot.xy = (x, y)
            self.annot.set_text(f"{label}: {y:.1f}%")

        self.canvas.draw_idle()

    # --- Update Handling ---
    def handle_update(self, update_type: str, data: Dict[str, Any]):
        handler_map = {
            "status_update": self._handle_status_update,
            "client_stats_update": self._handle_client_stats_update,
            "performance_update": self._handle_performance_update,
            "transfer_stats_update": self._handle_transfer_stats_update,
            "maintenance_update": self._handle_maintenance_update,
            "log": lambda log_data: self.add_ticker_entry(
                log_data.get("message", "") if hasattr(log_data, 'get') else "",  # type: ignore[attr-defined] 
                log_data.get("level", "info") if hasattr(log_data, 'get') else "info"  # type: ignore[attr-defined]
            )
        }
        if handler := handler_map.get(update_type):  # type: ignore[misc]
            handler(data)

    def add_ticker_entry(self, message: str, level: str):
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] "
        self.ticker_text.config(state=NORMAL)
        self.ticker_text.insert(1.0, f" {message}\n", (level,))
        self.ticker_text.insert(1.0, timestamp, ("timestamp",))
        self.ticker_text.config(state=DISABLED)
        self.ticker_text.see(1.0) # Scroll to top

    def _handle_status_update(self, data: Dict[str, Any]):
        is_running = data.get('running', False)
        self.server_start_time = data.get('start_time', 0.0) if is_running else 0.0
        
        status_text = "Online" if is_running else "Offline"
        self.kpi_labels['status'].config(text=status_text)
        self.kpi_labels['address'].config(text=f"{data.get('address', 'N/A')}:{data.get('port', 0)}")
        
        self.btn_start.config(state=DISABLED if is_running else NORMAL)
        self.btn_stop.config(state=NORMAL if is_running else DISABLED)
        self.btn_restart.config(state=NORMAL if is_running else DISABLED)

    def _handle_client_stats_update(self, data: Dict[str, Any]):
        connected = data.get('connected', 0)
        total = data.get('total', 0)
        max_clients = self.controller.settings.get('max_clients', 50)
        
        self.kpi_labels['total_clients'].config(text=str(total))
        if hasattr(self, 'client_meter') and self.client_meter is not None:
            self.client_meter.configure(amountused=connected, amounttotal=max_clients, textright=f'/ {max_clients}')  # type: ignore[misc]
        
    def _handle_performance_update(self, data: Dict[str, Any]) -> None:
        # Extract performance data for chart updates  
        _ = data  # Mark parameter as used
        perf_data = self.controller.performance_data
        
        if hasattr(self, 'cpu_line') and hasattr(self, 'mem_line') and len(perf_data['time']) > 1:
            self.cpu_line.set_data(perf_data['time'], perf_data['cpu'])
            self.mem_line.set_data(perf_data['time'], perf_data['memory'])
            if hasattr(self, 'ax'):
                self.ax.relim()
                self.ax.set_xlim(perf_data['time'][0], perf_data['time'][-1])
                self.ax.autoscale_view(scalex=True, scaley=False)
            if hasattr(self, 'canvas'):
                self.canvas.draw_idle()
            
        # Update Disk Meter
        if hasattr(self, 'disk_meter') and self.disk_meter is not None:
            try:
                usage = shutil.disk_usage(self.controller.settings.get('storage_dir', '.'))
                disk_percent = (usage.used / usage.total) * 100
                self.disk_meter.configure(amountused=int(disk_percent))  # type: ignore[misc]
            except FileNotFoundError:
                self.disk_meter.configure(amountused=0, subtext="Dir Not Found", bootstyle='secondary')  # type: ignore[misc]

    def _handle_transfer_stats_update(self, data: Dict[str, Any]):
        bytes_total = data.get('bytes_transferred', 0)
        rate_kbps = data.get('rate_kbps', 0.0)
        self.kpi_labels['total_transferred'].config(text=f"{bytes_total / (1024*1024):.2f} MB")
        self.kpi_labels['transfer_rate'].config(text=f"{rate_kbps:.1f} KB/s")

    def _handle_maintenance_update(self, data: Dict[str, Any]):
        last_cleanup = data.get('last_cleanup', 'Never')
        if isinstance(last_cleanup, str) and last_cleanup != 'Never':
            from contextlib import suppress
            with suppress(ValueError):
                last_cleanup = datetime.fromisoformat(last_cleanup).strftime('%Y-%m-%d %H:%M')
            
        self.kpi_labels['last_cleanup'].config(text=str(last_cleanup))
        self.kpi_labels['files_cleaned'].config(text=str(data.get('files_cleaned', 0)))