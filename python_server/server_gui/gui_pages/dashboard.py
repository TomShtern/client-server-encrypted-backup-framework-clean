# In file: gui_pages/dashboard.py (CORRECTED)

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import time
from datetime import timedelta
from collections import deque
from typing import TYPE_CHECKING, Dict, Any, Deque

# --- CORRECTED IMPORTS ---
if TYPE_CHECKING:
    from ..EnhancedServerGUI import EnhancedServerGUI
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    from matplotlib.lines import Line2D
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- CORRECTED IMPORTS: Import the custom widgets directly ---
from ..EnhancedServerGUI import BasePage, RoundedFrame, CustomTooltip, CHARTS_AVAILABLE, SYSTEM_MONITOR_AVAILABLE, psutil

class DashboardPage(BasePage):
    """The main dashboard page, acting as the 'Command Center' of the application."""

    def __init__(self, parent: tk.Widget, app: EnhancedServerGUI, **kwargs: Any) -> None:
        super().__init__(parent, app, **kwargs)
        # ... (rest of the __init__ is the same) ...
        self.performance_data: Dict[str, Deque[Any]] = { 'cpu': deque(maxlen=60), 'memory': deque(maxlen=60), 'time': deque(maxlen=60) }
        self.ax: Axes | None = None
        self.cpu_line: Line2D | None = None
        self.mem_line: Line2D | None = None
        self.performance_chart: FigureCanvasTkAgg | None = None
        self.is_monitoring = False
        self.kpi_labels: Dict[str, ttk.Label] = {}
        self.control_buttons: Dict[str, ttk.Button] = {}
        self.activity_log: tk.Text | None = None
        self._create_widgets()
        self.start_monitoring()


    def _create_widgets(self) -> None:
        """Create and lay out all widgets for the dashboard."""
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=3)
        kpi_frame = ttk.Frame(self, style='primary.TFrame')
        kpi_frame.grid(row=0, column=0, sticky=NSEW, padx=(0, 10), pady=(0, 10))
        kpi_frame.columnconfigure((0, 1), weight=1)
        kpi_frame.rowconfigure((0, 1), weight=1)
        control_log_frame = ttk.Frame(self, style='primary.TFrame')
        control_log_frame.grid(row=0, column=1, rowspan=2, sticky=NSEW)
        control_log_frame.rowconfigure(0, weight=1)
        control_log_frame.rowconfigure(1, weight=1)
        control_log_frame.columnconfigure(0, weight=1)
        self._create_kpi_cards(kpi_frame)
        self._create_performance_chart(self).grid(row=1, column=0, sticky=NSEW, padx=(0, 10))
        self._create_control_panel(control_log_frame).grid(row=0, column=0, sticky=NSEW, pady=(0, 10))
        self._create_activity_log(control_log_frame).grid(row=1, column=0, sticky=NSEW)

    def _create_kpi_cards(self, parent: ttk.Frame) -> None:
        """Create the four key performance indicator cards."""
        card_data = [
            ("Server Status", [("Status:", 'status', "Offline"), ("Address:", 'address', "N/A"), ("Uptime:", 'uptime', "00:00:00")]),
            ("Client Stats", [("Connected:", 'connected', "0"), ("Total:", 'total', "0"), ("Active Transfers:", 'active_transfers', "0")]),
            ("Transfer Stats", [("Total Transferred:", 'bytes', "0 MB"), ("Transfer Rate:", 'rate', "0 KB/s")]),
            ("Maintenance", [("Last Cleanup:", 'last_cleanup', "Never"), ("Files Cleaned:", 'files_cleaned', "0")])
        ]

        for i, (title, data) in enumerate(card_data):
            row, col = divmod(i, 2)
            # --- CORRECTED WIDGET CALL ---
            card = RoundedFrame(parent, bg_color=self.app.style.colors.secondary, border_color=self.app.style.colors.border)
            card.grid(row=row, column=col, sticky=NSEW, padx=5, pady=5)
            ttk.Label(card.content_frame, text=title, style='secondary.TLabel', font=self.app.Theme.FONT_BOLD).pack(anchor=NW, padx=10, pady=5)
            
            for label_text, key, default in data:
                frame = ttk.Frame(card.content_frame, style='secondary.TFrame')
                frame.pack(fill=X, padx=10, pady=2)
                ttk.Label(frame, text=label_text, style='secondary.TLabel', font=self.app.Theme.FONT_SMALL).pack(side=LEFT)
                self.kpi_labels[key] = ttk.Label(frame, text=default, style='secondary.TLabel', font=self.app.Theme.FONT_BOLD)
                self.kpi_labels[key].pack(side=RIGHT)

    def _create_performance_chart(self, parent: ttk.Frame) -> RoundedFrame:
        """Create and embed the live Matplotlib performance chart."""
        # --- CORRECTED WIDGET CALL ---
        card = RoundedFrame(parent, bg_color=self.app.style.colors.secondary, border_color=self.app.style.colors.border)
        ttk.Label(card.content_frame, text="Live System Performance", style='secondary.TLabel', font=self.app.Theme.FONT_BOLD).pack(anchor=NW, padx=10, pady=5)
        # ... (rest of chart logic is the same) ...
        if not CHARTS_AVAILABLE or not SYSTEM_MONITOR_AVAILABLE:
            ttk.Label(card.content_frame, text="Charts disabled (matplotlib/psutil not found)", style='secondary.TLabel').pack(expand=True)
            return card
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        fig = Figure(figsize=(5, 2), dpi=100, facecolor=self.app.style.colors.secondary)
        self.ax = fig.add_subplot(111)
        self.ax.set_facecolor(self.app.style.colors.bg)
        self.ax.tick_params(colors=self.app.style.colors.secondary, labelsize=8)
        for spine in self.ax.spines.values(): spine.set_color(self.app.style.colors.border)
        self.cpu_line, = self.ax.plot([], [], color=self.app.style.colors.info, lw=2, label="CPU %")
        self.mem_line, = self.ax.plot([], [], color=self.app.style.colors.success, lw=2, label="Memory %")
        self.ax.set_ylim(0, 100)
        self.ax.legend(loc='upper left', fontsize=8, facecolor=self.app.style.colors.bg, labelcolor=self.app.style.colors.fg, frameon=False)
        fig.tight_layout(pad=1.5)
        self.performance_chart = FigureCanvasTkAgg(fig, master=card.content_frame)
        self.performance_chart.get_tk_widget().pack(fill=BOTH, expand=True, padx=5, pady=5)
        return card

    def _create_control_panel(self, parent: ttk.Frame) -> RoundedFrame:
        """Create the server control buttons."""
        # --- CORRECTED WIDGET CALL ---
        card = RoundedFrame(parent, bg_color=self.app.style.colors.secondary, border_color=self.app.style.colors.border)
        # ... (rest of control panel logic is the same) ...
        ttk.Label(card.content_frame, text="Control Panel", style='secondary.TLabel', font=self.app.Theme.FONT_BOLD).pack(anchor=NW, padx=10, pady=5)
        bf = ttk.Frame(card.content_frame, style='secondary.TFrame')
        bf.pack(fill=BOTH, expand=True, padx=5, pady=5)
        bf.columnconfigure((0, 1), weight=1)
        bf.rowconfigure((0, 1), weight=1)
        btn_data = [ ("start", "▶ Start", self._start_server, "success", (0, 0)), ("stop", "⏹ Stop", self._stop_server, "danger", (0, 1)), ("restart", "🔄 Restart", self._restart_server, "warning", (1, 0), 2) ]
        for key, text, cmd, style, grid, *span in btn_data:
            cspan = span[0] if span else 1
            btn = ttk.Button(bf, text=text, command=cmd, bootstyle=style, style=f'{style}.TButton')
            btn.grid(row=grid[0], column=grid[1], columnspan=cspan, sticky=NSEW, padx=2, pady=2, ipady=8)
            self.control_buttons[key] = btn
        self._update_control_buttons()
        return card


    def _create_activity_log(self, parent: ttk.Frame) -> RoundedFrame:
        """Create the recent activity ticker/log."""
        # --- CORRECTED WIDGET CALL ---
        card = RoundedFrame(parent, bg_color=self.app.style.colors.secondary, border_color=self.app.style.colors.border)
        # ... (rest of activity log logic is the same) ...
        ttk.Label(card.content_frame, text="Recent Activity", style='secondary.TLabel', font=self.app.Theme.FONT_BOLD).pack(anchor=NW, padx=10, pady=5)
        self.activity_log = tk.Text(card.content_frame, height=4, bg=self.app.style.colors.bg, fg=self.app.style.colors.fg, font=self.app.Theme.FONT_SMALL, wrap="word", relief="flat", bd=0, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(card.content_frame, orient="vertical", command=self.activity_log.yview, bootstyle='secondary-round')
        self.activity_log.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y, pady=5)
        self.activity_log.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        return card

    # The rest of the methods in DashboardPage remain unchanged.
    # Add the other methods from the previous response here...
    # (e.g., _start_server, _stop_server, update_status_card, etc.)
    def _start_server(self) -> None:
        if not self.app.server: self.app.show_toast("Server instance not available", "danger"); return
        if self.app.server.running: self.app.show_toast("Server is already running", "warning"); return
        threading.Thread(target=self.app.server.start, daemon=True).start()
        self.app.show_toast("Server starting...", "info")

    def _stop_server(self) -> None:
        if not self.app.server: self.app.show_toast("Server instance not available", "danger"); return
        if not self.app.server.running: self.app.show_toast("Server is not running", "warning"); return
        threading.Thread(target=self.app.server.stop, daemon=True).start()
        self.app.show_toast("Server stopping...", "info")

    def _restart_server(self) -> None:
        if not self.app.server: self.app.show_toast("Server instance not available", "danger"); return
        self.app.show_toast("Restarting server...", "info")
        def do_restart() -> None:
            if self.app.server:
                if self.app.server.running: self.app.server.stop(); time.sleep(2)
                self.app.server.start()
        threading.Thread(target=do_restart, daemon=True).start()

    def _update_control_buttons(self) -> None:
        is_running = self.app.server and self.app.server.running
        self.control_buttons['start'].config(state=tk.DISABLED if is_running else tk.NORMAL)
        self.control_buttons['stop'].config(state=tk.NORMAL if is_running else tk.DISABLED)
        self.control_buttons['restart'].config(state=tk.NORMAL if is_running else tk.DISABLED)

    def _flash_label(self, key: str) -> None:
        if key in self.kpi_labels:
            label = self.kpi_labels[key]
            original_style = label.cget('style')
            label.config(style='info.TLabel')
            self.after(500, lambda: label.config(style=original_style))

    def update_status_card(self, data: Dict[str, Any]) -> None:
        running = data.get('running', False)
        status_text = "Running" if running else "Offline"
        if 'status' in self.kpi_labels and self.kpi_labels['status'].cget('text') != status_text:
            self.kpi_labels['status'].config(text=status_text, style=f'{"success" if running else "danger"}.TLabel')
            self._flash_label('status')
        address = f"{data.get('address', 'N/A')}:{data.get('port', 0)}"
        if 'address' in self.kpi_labels and self.kpi_labels['address'].cget('text') != address:
             self.kpi_labels['address'].config(text=address)
             self._flash_label('address')
        self._update_control_buttons()
        self._update_uptime()

    def update_client_stats_card(self, data: Dict[str, Any]) -> None:
        for key in ['connected', 'total', 'active_transfers']:
            new_val = str(data.get(key, 0))
            if key in self.kpi_labels and self.kpi_labels[key].cget('text') != new_val:
                self.kpi_labels[key].config(text=new_val)
                self._flash_label(key)

    def update_transfer_stats_card(self, data: Dict[str, Any]) -> None:
        bytes_val = f"{data.get('bytes_transferred', 0) / (1024*1024):.2f} MB"
        rate_val = f"{data.get('rate_kbps', 0):.1f} KB/s"
        if 'bytes' in self.kpi_labels and self.kpi_labels['bytes'].cget('text') != bytes_val:
            self.kpi_labels['bytes'].config(text=bytes_val)
            self._flash_label('bytes')
        if 'rate' in self.kpi_labels and self.kpi_labels['rate'].cget('text') != rate_val:
            self.kpi_labels['rate'].config(text=rate_val)
            self._flash_label('rate')
            
    def add_activity_log(self, message: str) -> None:
        if not self.activity_log: return
        log_entry = f"[{time.strftime('%H:%M:%S')}] {message}\n"
        self.activity_log.config(state=tk.NORMAL)
        self.activity_log.insert(tk.END, log_entry)
        self.activity_log.see(tk.END)
        self.activity_log.config(state=tk.DISABLED)

    def _update_uptime(self) -> None:
        if self.app.server and self.app.server.running and self.app.start_time > 0:
            uptime = timedelta(seconds=int(time.time() - self.app.start_time))
            self.kpi_labels['uptime'].config(text=str(uptime))
        else:
            self.kpi_labels['uptime'].config(text="0:00:00")
            
    def _update_performance_metrics(self) -> None:
        if not all([self.is_monitoring, self.ax, self.performance_chart, self.cpu_line, self.mem_line]): return
        cpu, mem = psutil.cpu_percent(), psutil.virtual_memory().percent
        self.performance_data['cpu'].append(cpu)
        self.performance_data['memory'].append(mem)
        times = range(len(self.performance_data['cpu']))
        self.ax.set_xlim(0, max(1, len(times) - 1))
        self.cpu_line.set_data(times, list(self.performance_data['cpu']))
        self.mem_line.set_data(times, list(self.performance_data['memory']))
        self.performance_chart.draw_idle()

    def start_monitoring(self) -> None:
        if self.is_monitoring or not self.app._tkthread: return
        self.is_monitoring = True
        def monitor_loop() -> None:
            while self.is_monitoring:
                self.app._tkthread.call(self._update_performance_metrics)
                time.sleep(1)
        self.app._tkthread.call_in_thread(monitor_loop)

    def on_show(self) -> None:
        self.start_monitoring()
        self._update_uptime()

    def stop_monitoring(self) -> None:
        self.is_monitoring = False