# ServerGUI.py - ULTRA MODERN Cross-platform GUI for Encrypted Backup Server
# Enhanced version with real functionality and advanced features

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import queue
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import os
import sys
import json
import csv
import sqlite3
from collections import deque
import math
import shutil
import zlib
import socket
import gc

# Import server components for real server control
try:
    from .server import BackupServer # type: ignore
    SERVER_CONTROL_AVAILABLE = True
except ImportError:
    BackupServer = None
    SERVER_CONTROL_AVAILABLE = False
    print("Warning: Server control not available - server start/stop disabled")

# Import singleton manager
from .server_singleton import ensure_single_server_instance

# Import system tray functionality based on platform
try:
    import pystray
    try:
        from PIL import Image, ImageDraw
        TRAY_AVAILABLE = True
        print("[OK] System tray functionality available (pystray and PIL installed)")
    except ImportError as pil_error:
        print(f"[WARNING] PIL/Pillow not available: {pil_error}")
        print("[INFO] System tray will be disabled. To enable: pip install pillow")
        TRAY_AVAILABLE = False
        # Create dummy classes to prevent AttributeError
        Image = None
        ImageDraw = None
except ImportError as pystray_error:
    print(f"[WARNING] pystray not available: {pystray_error}")
    print("[INFO] To enable system tray: pip install pystray pillow")
    TRAY_AVAILABLE = False
    # Create dummy classes to prevent AttributeError
    pystray = None
    Image = None
    ImageDraw = None

# Import advanced features
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.animation as animation
    import matplotlib.dates as mdates
    plt.style.use('dark_background')  # Dark theme for charts
    CHARTS_AVAILABLE = True
    print("[OK] Advanced charts available (matplotlib installed)")
except ImportError as e:
    CHARTS_AVAILABLE = False
    plt = None
    FigureCanvasTkAgg = None
    Figure = None
    animation = None
    mdates = None
    print(f"[WARNING] matplotlib not available: {e}")
    print("[INFO] To enable advanced charts: pip install matplotlib")

try:
    import psutil  # For real system monitoring
    SYSTEM_MONITOR_AVAILABLE = True
except ImportError:
    psutil = None  # Explicitly set to None when not available
    SYSTEM_MONITOR_AVAILABLE = False
    print("Warning: psutil not available - real system monitoring disabled, using simulated data")

# Import enhanced process monitoring
try:
    from ..shared.utils.process_monitor_gui import ProcessMonitorWidget, create_process_monitor_tab
    PROCESS_MONITOR_AVAILABLE = True
    print("[OK] Enhanced process monitoring available")
except ImportError as e:
    PROCESS_MONITOR_AVAILABLE = False
    ProcessMonitorWidget = None
    create_process_monitor_tab = None
    print(f"[WARNING] Enhanced process monitoring not available: {e}")
    
    
# SENTRY - Initialize error tracking
try:
    import sentry_sdk
    sentry_sdk.init(
        dsn="https://094a0bee5d42a7f7e8ec8a78a37c8819@o4509746411470848.ingest.us.sentry.io/4509747877773312",
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
    )
    print("[OK] Sentry error tracking initialized")
except ImportError:
    print("[WARNING] Sentry not available - error tracking disabled")
except Exception as e:
    print(f"[WARNING] Sentry initialization failed: {e}")

# Sentry test - uncomment to test error reporting
# division_by_zero = 1 / 0
    
    
    
    
    
    
    
    
    
    
    
    

# --- ULTRA MODERN UI CONSTANTS ---
class ModernTheme:
    """Ultra modern dark theme with sophisticated color palette"""
    # Primary Colors - Deep space theme
    PRIMARY_BG = "#0D1117"          # Deep space black
    SECONDARY_BG = "#161B22"        # Slightly lighter space
    CARD_BG = "#21262D"             # Card backgrounds
    ACCENT_BG = "#30363D"           # Accent elements

    # Text Colors
    TEXT_PRIMARY = "#F0F6FC"        # Bright white text
    TEXT_SECONDARY = "#8B949E"      # Muted text
    TEXT_ACCENT = "#58A6FF"         # Accent blue text

    # Status Colors
    SUCCESS = "#238636"             # Green success
    WARNING = "#D29922"             # Orange warning
    ERROR = "#DA3633"               # Red error
    INFO = "#1F6FEB"                # Blue info

    # Accent Colors
    ACCENT_BLUE = "#58A6FF"         # Primary blue
    ACCENT_PURPLE = "#BC8CFF"       # Purple accent
    ACCENT_GREEN = "#56D364"        # Green accent
    ACCENT_ORANGE = "#FF9500"       # Orange accent

    # Glass Morphism Effects
    GLASS_BG = "#2A2A2A"           # Glass background with transparency
    GLASS_BORDER = "#4A4A4A"       # Glass border color
    GLASS_HIGHLIGHT = "#5A5A5A"    # Glass highlight
    GLASS_SHADOW = "#0A0A0A"       # Glass shadow

    # Gradients (for future use)
    GRADIENT_START = "#1F6FEB"
    GRADIENT_END = "#BC8CFF"

    # Modern Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_LARGE = 16
    FONT_SIZE_MEDIUM = 12
    FONT_SIZE_SMALL = 10

    # Spacing and Layout
    PADDING_LARGE = 20
    PADDING_MEDIUM = 15
    PADDING_SMALL = 10
    BORDER_RADIUS = 8

    # Animation Constants
    ANIMATION_SPEED = 50  # milliseconds
    FADE_STEPS = 20

    # Advanced UI Constants
    TOAST_DURATION = 3000  # milliseconds
    CHART_UPDATE_INTERVAL = 1000  # milliseconds
    PROGRESS_ANIMATION_SPEED = 100  # milliseconds

    # Interactive Features
    HOVER_ANIMATION_SPEED = 150  # milliseconds
    PULSE_ANIMATION_SPEED = 2000  # milliseconds
    GLOW_EFFECT_INTENSITY = 0.3

# --- MODERN CUSTOM WIDGETS ---
class ModernCard(tk.Frame):
    """Modern card widget with rounded corners and shadow effect"""
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, bg=ModernTheme.CARD_BG, relief="flat", bd=0, **kwargs)
        self.title = title
        self._create_card()

    def _create_card(self):
        # Title bar
        if self.title:
            title_frame = tk.Frame(self, bg=ModernTheme.ACCENT_BG, height=40)
            title_frame.pack(fill="x", padx=2, pady=(2, 0))
            title_frame.pack_propagate(False)

            title_label = tk.Label(title_frame, text=self.title,
                                 bg=ModernTheme.ACCENT_BG, fg=ModernTheme.TEXT_PRIMARY,
                                 font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MEDIUM, "bold"))
            title_label.pack(side="left", padx=ModernTheme.PADDING_MEDIUM, pady=8)

        # Content frame
        self.content_frame = tk.Frame(self, bg=ModernTheme.CARD_BG)
        self.content_frame.pack(fill="both", expand=True, padx=2, pady=(0, 2))

class GlassMorphismCard(tk.Frame):
    """Ultra modern glass morphism card with subtle borders and transparency effects"""
    def __init__(self, parent, title="", **kwargs):
        # Create outer frame with shadow effect
        super().__init__(parent, bg=ModernTheme.PRIMARY_BG, relief="flat", bd=0, **kwargs)

        # Create glass effect container
        self.glass_container = tk.Frame(self, bg=ModernTheme.GLASS_BG, relief="solid", bd=1)
        self.glass_container.configure(highlightbackground=ModernTheme.GLASS_BORDER,
                                     highlightcolor=ModernTheme.GLASS_HIGHLIGHT,
                                     highlightthickness=1)
        self.glass_container.pack(fill="both", expand=True, padx=2, pady=2)

        # Add subtle inner border for glass effect
        self.inner_frame = tk.Frame(self.glass_container, bg=ModernTheme.GLASS_BG, relief="flat", bd=0)
        self.inner_frame.pack(fill="both", expand=True, padx=1, pady=1)

        self.title = title
        self._create_glass_card()

    def _create_glass_card(self):
        # Title bar with glass effect
        if self.title:
            title_frame = tk.Frame(self.inner_frame, bg=ModernTheme.GLASS_HIGHLIGHT, height=35)
            title_frame.pack(fill="x", padx=1, pady=(1, 0))
            title_frame.pack_propagate(False)

            title_label = tk.Label(title_frame, text=self.title,
                                 bg=ModernTheme.GLASS_HIGHLIGHT, fg=ModernTheme.TEXT_PRIMARY,
                                 font=(ModernTheme.FONT_FAMILY, 11, "bold"))
            title_label.pack(side="left", padx=12, pady=8)

        # Content frame with glass background
        self.content_frame = tk.Frame(self.inner_frame, bg=ModernTheme.GLASS_BG)
        self.content_frame.pack(fill="both", expand=True, padx=1, pady=(0, 1))

class ModernProgressBar(tk.Canvas):
    """Modern animated progress bar with gradient effect"""
    def __init__(self, parent, width=300, height=20, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=ModernTheme.SECONDARY_BG, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.progress = 0
        self.target_progress = 0
        self.animation_id = None
        self._draw_background()

    def _draw_background(self):
        self.delete("all")
        # Background
        self.create_rectangle(0, 0, self.width, self.height,
                            fill=ModernTheme.SECONDARY_BG, outline="")
        # Border
        self.create_rectangle(0, 0, self.width, self.height,
                            fill="", outline=ModernTheme.ACCENT_BG, width=1)

    def set_progress(self, value):
        """Set progress value (0-100) with smooth animation"""
        self.target_progress = max(0, min(100, value))
        self._animate_to_target()

    def _animate_to_target(self):
        if self.animation_id:
            self.after_cancel(self.animation_id)

        diff = self.target_progress - self.progress
        if abs(diff) < 0.5:
            self.progress = self.target_progress
            self._draw_progress()
            return

        self.progress += diff * 0.1
        self._draw_progress()
        self.animation_id = self.after(ModernTheme.ANIMATION_SPEED, self._animate_to_target)

    def _draw_progress(self):
        self._draw_background()
        if self.progress > 0:
            progress_width = (self.progress / 100) * (self.width - 2)
            # Gradient effect simulation
            self.create_rectangle(1, 1, progress_width + 1, self.height - 1,
                                fill=ModernTheme.ACCENT_BLUE, outline="")

class ModernStatusIndicator(tk.Canvas):
    """Modern status indicator with pulsing animation"""
    def __init__(self, parent, size=16, **kwargs):
        super().__init__(parent, width=size, height=size,
                        bg=ModernTheme.CARD_BG, highlightthickness=0, **kwargs)
        self.size = size
        self.status = "offline"  # offline, online, warning, error
        self.pulse_alpha = 0
        self.pulse_direction = 1
        self.animation_id = None
        self._draw_indicator()

    def set_status(self, status):
        """Set status: offline, online, warning, error"""
        self.status = status
        self._draw_indicator()
        if status == "online":
            self._start_pulse()
        else:
            self._stop_pulse()

    def _draw_indicator(self):
        self.delete("all")
        colors = {
            "offline": ModernTheme.TEXT_SECONDARY,
            "online": ModernTheme.SUCCESS,
            "warning": ModernTheme.WARNING,
            "error": ModernTheme.ERROR
        }
        color = colors.get(self.status, ModernTheme.TEXT_SECONDARY)

        center = self.size // 2
        radius = center - 2
        self.create_oval(center - radius, center - radius,
                        center + radius, center + radius,
                        fill=color, outline="")

    def _start_pulse(self):
        if self.animation_id:
            self.after_cancel(self.animation_id)
        self._pulse_animation()

    def _stop_pulse(self):
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None

    def _pulse_animation(self):
        self.pulse_alpha += self.pulse_direction * 0.1
        if self.pulse_alpha >= 1:
            self.pulse_alpha = 1
            self.pulse_direction = -1
        elif self.pulse_alpha <= 0:
            self.pulse_alpha = 0
            self.pulse_direction = 1

        self._draw_indicator()
        self.animation_id = self.after(100, self._pulse_animation)

class AdvancedProgressBar(tk.Canvas):
    """Advanced animated progress bar with gradient and glow effects"""
    def __init__(self, parent, width=300, height=25, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=ModernTheme.SECONDARY_BG, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.progress = 0
        self.target_progress = 0
        self.animation_id = None
        self.glow_alpha = 0
        self.glow_direction = 1
        self._draw_background()

    def _draw_background(self):
        self.delete("all")
        # Background with rounded corners effect
        self.create_rectangle(2, 2, self.width-2, self.height-2,
                            fill=ModernTheme.SECONDARY_BG, outline=ModernTheme.ACCENT_BG, width=1)

    def set_progress(self, value, animated=True):
        """Set progress value (0-100) with smooth animation"""
        self.target_progress = max(0, min(100, value))
        if animated:
            self._animate_to_target()
        else:
            self.progress = self.target_progress
            self._draw_progress()

    def _animate_to_target(self):
        if self.animation_id:
            self.after_cancel(self.animation_id)

        diff = self.target_progress - self.progress
        if abs(diff) < 0.5:
            self.progress = self.target_progress
            self._draw_progress()
            return

        self.progress += diff * 0.15  # Smooth animation
        self._draw_progress()
        self.animation_id = self.after(ModernTheme.PROGRESS_ANIMATION_SPEED, self._animate_to_target)

    def _draw_progress(self):
        self._draw_background()
        if self.progress > 0:
            progress_width = (self.progress / 100) * (self.width - 6)
            # Main progress bar
            self.create_rectangle(3, 3, progress_width + 3, self.height - 3,
                                fill=ModernTheme.ACCENT_BLUE, outline="")
            # Highlight effect
            if progress_width > 10:
                self.create_rectangle(3, 3, progress_width + 3, 8,
                                    fill=ModernTheme.ACCENT_PURPLE, outline="")

class ToastNotification:
    """Modern toast notification system"""
    def __init__(self, parent):
        self.parent = parent
        self.notifications = []
        self.notification_id = 0

    def show_toast(self, message, toast_type="info", duration=3000):
        """Show a toast notification"""
        self.notification_id += 1

        # Create notification window
        toast = tk.Toplevel(self.parent)
        toast.withdraw()  # Hide initially
        toast.overrideredirect(True)  # Remove window decorations
        toast.attributes('-topmost', True)  # Always on top

        # Configure toast appearance
        colors = {
            "info": ModernTheme.INFO,
            "success": ModernTheme.SUCCESS,
            "warning": ModernTheme.WARNING,
            "error": ModernTheme.ERROR
        }

        bg_color = colors.get(toast_type, ModernTheme.INFO)

        # Create toast content
        frame = tk.Frame(toast, bg=bg_color, padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        # Message label
        label = tk.Label(frame, text=message, bg=bg_color, fg=ModernTheme.TEXT_PRIMARY,
                        font=(ModernTheme.FONT_FAMILY, 11, 'bold'), wraplength=300)
        label.pack()

        # Position toast - Bottom right corner, less intrusive
        toast.update_idletasks()
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        # Position at bottom-right of screen, stacked upward
        x = screen_width - toast.winfo_width() - 20
        y = screen_height - 100 - (len(self.notifications) * 80)
        toast.geometry(f"+{x}+{y}")

        # Show toast with fade-in effect
        toast.deiconify()
        self.notifications.append(toast)

        # Auto-hide after duration
        toast.after(duration, lambda: self._hide_toast(toast))

    def _hide_toast(self, toast):
        """Hide and destroy toast notification"""
        if toast in self.notifications:
            self.notifications.remove(toast)
        toast.destroy()

        # Reposition remaining toasts - Bottom right, less intrusive
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        for i, notification in enumerate(self.notifications):
            x = screen_width - notification.winfo_width() - 20
            y = screen_height - 100 - (i * 80)
            notification.geometry(f"+{x}+{y}")

# --- ENHANCED TABLE WIDGET ---
class ModernTooltip:
    """Modern tooltip that appears on hover"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window or not self.text:
            return

        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify='left',
                      background=ModernTheme.ACCENT_BG, foreground=ModernTheme.TEXT_PRIMARY,
                      relief='solid', borderwidth=1,
                      font=(ModernTheme.FONT_FAMILY, 9, "normal"), padx=8, pady=5)
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

class ModernTable(tk.Frame):
    """Modern table widget with sorting, filtering, and selection"""
    def __init__(self, parent, columns, **kwargs):
        super().__init__(parent, bg=ModernTheme.CARD_BG, **kwargs)
        self.columns = columns
        self.data = []
        self.filtered_data = []
        self.sort_column = None
        self.sort_reverse = False
        self.selection_callback = None
        self._create_table()

    def _create_table(self):
        # Search frame
        search_frame = tk.Frame(self, bg=ModernTheme.CARD_BG)
        search_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(search_frame, text="🔍", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 12)).pack(side="left", padx=(5, 2))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                               font=(ModernTheme.FONT_FAMILY, 10), relief="flat", bd=5)
        search_entry.pack(side="left", fill="x", expand=True)

        # Table frame with scrollbars
        table_container = tk.Frame(self, bg=ModernTheme.CARD_BG)
        table_container.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # Create Treeview
        self.tree = ttk.Treeview(table_container, columns=list(self.columns.keys()), 
                                show="tree headings", height=10)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                       background=ModernTheme.SECONDARY_BG,
                       foreground=ModernTheme.TEXT_PRIMARY,
                       fieldbackground=ModernTheme.SECONDARY_BG,
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background=ModernTheme.ACCENT_BG,
                       foreground=ModernTheme.TEXT_PRIMARY,
                       relief="flat")
        style.map("Treeview",
                 background=[('selected', ModernTheme.ACCENT_BLUE)])

        # Configure columns
        self.tree.column("#0", width=50, stretch=False)
        for col_id, col_info in self.columns.items():
            self.tree.column(col_id, width=col_info.get('width', 100), 
                           minwidth=col_info.get('minwidth', 50))
            self.tree.heading(col_id, text=col_info['text'],
                            command=lambda c=col_id: self._sort_by_column(c))

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Pack elements
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_change)

    def set_data(self, data):
        """Set table data"""
        self.data = data
        self._apply_filter()

    def _apply_filter(self):
        """Apply search filter to data"""
        search_text = self.search_var.get().lower()
        if search_text:
            self.filtered_data = []
            for item in self.data:
                # Check if search text is in any column
                if any(search_text in str(item.get(col, '')).lower() 
                      for col in self.columns.keys()):
                    self.filtered_data.append(item)
        else:
            self.filtered_data = self.data.copy()
        
        self._refresh_display()

    def _refresh_display(self):
        """Refresh the table display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add filtered items
        for idx, item in enumerate(self.filtered_data):
            values = [item.get(col, '') for col in self.columns.keys()]
            self.tree.insert("", "end", text=str(idx + 1), values=values)

    def _sort_by_column(self, column):
        """Sort table by column"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        self.filtered_data.sort(key=lambda x: x.get(column, ''), 
                               reverse=self.sort_reverse)
        self._refresh_display()

    def _on_search_change(self, *args):
        """Handle search text change"""
        self._apply_filter()

    def _on_selection_change(self, event):
        """Handle selection change"""
        selection = self.tree.selection()
        if selection and self.selection_callback:
            item = self.tree.item(selection[0])
            index = int(item['text']) - 1
            if 0 <= index < len(self.filtered_data):
                self.selection_callback(self.filtered_data[index])

    def set_selection_callback(self, callback):
        """Set callback for selection changes"""
        self.selection_callback = callback

    def get_selected_items(self):
        """Get currently selected items"""
        selected = []
        for item_id in self.tree.selection():
            item = self.tree.item(item_id)
            index = int(item['text']) - 1
            if 0 <= index < len(self.filtered_data):
                selected.append(self.filtered_data[index])
        return selected

# --- SETTINGS DIALOG ---
class SettingsDialog:
    """Modern settings dialog"""
    def __init__(self, parent, current_settings):
        self.parent = parent
        self.settings = current_settings.copy()
        self.dialog = None
        self.result = None

    def show(self):
        """Show the settings dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Server Settings")
        self.dialog.geometry("500x600")
        self.dialog.configure(bg=ModernTheme.PRIMARY_BG)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_settings_ui()
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
        return self.result

    def _create_settings_ui(self):
        """Create settings UI"""
        # Main container
        main_frame = tk.Frame(self.dialog, bg=ModernTheme.PRIMARY_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(main_frame, text="Server Configuration",
                             bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 16, 'bold'))
        title_label.pack(pady=(0, 20))

        # Create notebook for tabs
        style = ttk.Style()
        style.configure('Dark.TNotebook', background=ModernTheme.PRIMARY_BG)
        style.configure('Dark.TNotebook.Tab', background=ModernTheme.CARD_BG,
                       foreground=ModernTheme.TEXT_PRIMARY, padding=[20, 10])
        style.map('Dark.TNotebook.Tab',
                 background=[('selected', ModernTheme.ACCENT_BG)])

        notebook = ttk.Notebook(main_frame, style='Dark.TNotebook')
        notebook.pack(fill="both", expand=True)

        # General tab
        general_frame = tk.Frame(notebook, bg=ModernTheme.CARD_BG)
        notebook.add(general_frame, text="General")
        self._create_general_settings(general_frame)

        # Security tab
        security_frame = tk.Frame(notebook, bg=ModernTheme.CARD_BG)
        notebook.add(security_frame, text="Security")
        self._create_security_settings(security_frame)

        # Performance tab
        performance_frame = tk.Frame(notebook, bg=ModernTheme.CARD_BG)
        notebook.add(performance_frame, text="Performance")
        self._create_performance_settings(performance_frame)

        # Buttons
        button_frame = tk.Frame(main_frame, bg=ModernTheme.PRIMARY_BG)
        button_frame.pack(fill="x", pady=(20, 0))

        save_btn = tk.Button(button_frame, text="💾 Save", command=self._save_settings,
                           bg=ModernTheme.SUCCESS, fg=ModernTheme.TEXT_PRIMARY,
                           font=(ModernTheme.FONT_FAMILY, 11, 'bold'),
                           relief="flat", bd=0, padx=20, pady=8)
        save_btn.pack(side="right", padx=(10, 0))

        cancel_btn = tk.Button(button_frame, text="[CANCEL] Cancel", command=self._cancel,
                             bg=ModernTheme.ERROR, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 11, 'bold'),
                             relief="flat", bd=0, padx=20, pady=8)
        cancel_btn.pack(side="right")

    def _create_general_settings(self, parent):
        """Create general settings"""
        # Port setting
        port_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        port_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(port_frame, text="Server Port:", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        self.port_var = tk.StringVar(value=str(self.settings.get('port', 1256)))
        port_entry = tk.Entry(port_frame, textvariable=self.port_var,
                            bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                            font=(ModernTheme.FONT_FAMILY, 11))
        port_entry.pack(fill="x", pady=(5, 0))

        # Storage directory
        storage_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        storage_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(storage_frame, text="Storage Directory:", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        storage_subframe = tk.Frame(storage_frame, bg=ModernTheme.CARD_BG)
        storage_subframe.pack(fill="x", pady=(5, 0))

        self.storage_var = tk.StringVar(value=str(self.settings.get('storage_dir', 'received_files')))
        storage_entry = tk.Entry(storage_subframe, textvariable=self.storage_var,
                               bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                               font=(ModernTheme.FONT_FAMILY, 11))
        storage_entry.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Button(storage_subframe, text="📁", command=self._browse_directory,
                             bg=ModernTheme.ACCENT_BLUE, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 11), relief="flat", bd=0, padx=10)
        browse_btn.pack(side="right", padx=(5, 0))

        # Max clients
        clients_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        clients_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(clients_frame, text="Max Concurrent Clients:", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        self.max_clients_var = tk.StringVar(value=str(self.settings.get('max_clients', 50)))
        clients_entry = tk.Entry(clients_frame, textvariable=self.max_clients_var,
                               bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                               font=(ModernTheme.FONT_FAMILY, 11))
        clients_entry.pack(fill="x", pady=(5, 0))

    def _create_security_settings(self, parent):
        """Create security settings"""
        # Client timeout
        timeout_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        timeout_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(timeout_frame, text="Client Session Timeout (minutes):", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        self.timeout_var = tk.StringVar(value=str(self.settings.get('session_timeout', 10)))
        timeout_entry = tk.Entry(timeout_frame, textvariable=self.timeout_var,
                               bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                               font=(ModernTheme.FONT_FAMILY, 11))
        timeout_entry.pack(fill="x", pady=(5, 0))

        # Encryption info
        enc_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        enc_frame.pack(fill="x", padx=20, pady=20)

        tk.Label(enc_frame, text="Encryption Settings:", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11, 'bold')).pack(anchor="w")
        
        enc_info = [
            "• RSA Key Size: 1024 bits",
            "• AES Key Size: 256 bits",
            "• AES Mode: CBC with PKCS7 padding",
            "• Hash Algorithm: SHA256 for OAEP"
        ]
        
        for info in enc_info:
            tk.Label(enc_frame, text=info, bg=ModernTheme.CARD_BG,
                    fg=ModernTheme.TEXT_SECONDARY, font=(ModernTheme.FONT_FAMILY, 10)).pack(anchor="w", pady=2)

    def _create_performance_settings(self, parent):
        """Create performance settings"""
        # Maintenance interval
        maintenance_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        maintenance_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(maintenance_frame, text="Maintenance Interval (seconds):", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        self.maintenance_var = tk.StringVar(value=str(self.settings.get('maintenance_interval', 60)))
        maintenance_entry = tk.Entry(maintenance_frame, textvariable=self.maintenance_var,
                                   bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                                   font=(ModernTheme.FONT_FAMILY, 11))
        maintenance_entry.pack(fill="x", pady=(5, 0))

        # File size limits
        size_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        size_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(size_frame, text="Max File Size (MB):", bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 11)).pack(anchor="w")
        
        self.max_size_var = tk.StringVar(value=str(self.settings.get('max_file_size_mb', 4096)))
        size_entry = tk.Entry(size_frame, textvariable=self.max_size_var,
                            bg=ModernTheme.SECONDARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                            font=(ModernTheme.FONT_FAMILY, 11))
        size_entry.pack(fill="x", pady=(5, 0))

        # Performance options
        perf_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        perf_frame.pack(fill="x", padx=20, pady=20)

        self.log_verbose_var = tk.BooleanVar(value=self.settings.get('verbose_logging', False))
        verbose_check = tk.Checkbutton(perf_frame, text="Verbose Logging",
                                     variable=self.log_verbose_var,
                                     bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                                     font=(ModernTheme.FONT_FAMILY, 11),
                                     selectcolor=ModernTheme.SECONDARY_BG)
        verbose_check.pack(anchor="w")

        self.auto_backup_var = tk.BooleanVar(value=self.settings.get('auto_backup_db', True))
        backup_check = tk.Checkbutton(perf_frame, text="Auto-backup Database",
                                    variable=self.auto_backup_var,
                                    bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                                    font=(ModernTheme.FONT_FAMILY, 11),
                                    selectcolor=ModernTheme.SECONDARY_BG)
        backup_check.pack(anchor="w", pady=(10, 0))

    def _browse_directory(self):
        """Browse for storage directory"""
        directory = filedialog.askdirectory(parent=self.dialog,
                                          initialdir=self.storage_var.get())
        if directory:
            self.storage_var.set(directory)

    def _save_settings(self):
        """Save settings to file and close dialog"""
        try:
            # Validate inputs
            port = int(self.port_var.get())
            if not 1024 <= port <= 65535:
                raise ValueError("Port must be between 1024 and 65535")

            max_clients = int(self.max_clients_var.get())
            if max_clients < 1:
                raise ValueError("Max clients must be at least 1")

            timeout = int(self.timeout_var.get())
            if timeout < 1:
                raise ValueError("Timeout must be at least 1 minute")

            maintenance = int(self.maintenance_var.get())
            if maintenance < 10:
                raise ValueError("Maintenance interval must be at least 10 seconds")

            max_size = int(self.max_size_var.get())
            if max_size < 1:
                raise ValueError("Max file size must be at least 1 MB")

            # Update settings
            self.settings['port'] = port
            self.settings['storage_dir'] = self.storage_var.get()
            self.settings['max_clients'] = max_clients
            self.settings['session_timeout'] = timeout
            self.settings['maintenance_interval'] = maintenance
            self.settings['max_file_size_mb'] = max_size
            self.settings['verbose_logging'] = self.log_verbose_var.get()
            self.settings['auto_backup_db'] = self.auto_backup_var.get()

            # Save settings to file
            self._persist_settings_to_file()

            self.result = self.settings
            if self.dialog:
                self.dialog.destroy()
                
        except Exception as e:
            messagebox.showerror("Settings Error", f"Failed to save settings: {str(e)}", 
                               parent=self.dialog if self.dialog else self.parent)

    def _persist_settings_to_file(self):
        """Persist settings to configuration file"""
        try:
            settings_file = "server_gui_settings.json"
            settings_data = {
                'server_settings': self.settings,
                'gui_preferences': {
                    'last_tab': getattr(self, 'current_tab', 'dashboard'),
                    'window_state': 'normal',
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
                
            print(f"Settings saved to {settings_file}")
            
        except Exception as e:
            print(f"Failed to save settings to file: {e}")
            raise

    def _cancel(self):
        """Cancel and close dialog"""
        self.result = None
        if self.dialog:
            self.dialog.destroy()

# --- CHART WIDGET ---
class ModernChart(tk.Frame):
    """Modern chart widget using matplotlib"""
    def __init__(self, parent, chart_type="line", **kwargs):
        super().__init__(parent, bg=ModernTheme.CARD_BG, **kwargs)
        self.chart_type = chart_type
        self.data = {}
        self.figure = None
        self.canvas = None
        self.ax = None
        self._create_chart()

    def _create_chart(self):
        """Create the chart"""
        if not CHARTS_AVAILABLE or not Figure:
            label = tk.Label(self, text="Charts not available\n(matplotlib not installed)",
                           bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                           font=(ModernTheme.FONT_FAMILY, 12))
            label.pack(expand=True)
            return

        # Create figure with dark background
        self.figure = Figure(figsize=(6, 4), dpi=100, facecolor=ModernTheme.CARD_BG)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(ModernTheme.SECONDARY_BG)

        # Style the axes
        self.ax.spines['bottom'].set_color(ModernTheme.TEXT_SECONDARY)
        self.ax.spines['top'].set_color(ModernTheme.TEXT_SECONDARY)
        self.ax.spines['left'].set_color(ModernTheme.TEXT_SECONDARY)
        self.ax.spines['right'].set_color(ModernTheme.TEXT_SECONDARY)
        self.ax.tick_params(colors=ModernTheme.TEXT_SECONDARY)
        self.ax.xaxis.label.set_color(ModernTheme.TEXT_PRIMARY)
        self.ax.yaxis.label.set_color(ModernTheme.TEXT_PRIMARY)
        # Fix: Use set_title with color parameter instead of accessing title attribute
        self.ax.set_title('', color=ModernTheme.TEXT_PRIMARY)

        # Create canvas
        if FigureCanvasTkAgg:
            self.canvas = FigureCanvasTkAgg(self.figure, self)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_data(self, data, title="", xlabel="", ylabel=""):
        """Update chart data"""
        if not CHARTS_AVAILABLE or not self.ax or not Figure:
            return

        self.data = data
        self.ax.clear()

        # Set labels
        self.ax.set_title(title, color=ModernTheme.TEXT_PRIMARY, fontsize=12, pad=10)
        self.ax.set_xlabel(xlabel, color=ModernTheme.TEXT_PRIMARY, fontsize=10)
        self.ax.set_ylabel(ylabel, color=ModernTheme.TEXT_PRIMARY, fontsize=10)

        # Plot based on chart type
        if self.chart_type == "line":
            for label, (x_data, y_data) in data.items():
                self.ax.plot(x_data, y_data, label=label, linewidth=2)
        elif self.chart_type == "bar":
            if data:
                labels = list(data.keys())
                values = list(data.values())
                colors = [ModernTheme.ACCENT_BLUE, ModernTheme.ACCENT_PURPLE, 
                         ModernTheme.ACCENT_GREEN, ModernTheme.ACCENT_ORANGE] * len(labels)
                self.ax.bar(labels, values, color=colors[:len(labels)])
        elif self.chart_type == "pie":
            if data:
                labels = list(data.keys())
                values = list(data.values())
                colors = [ModernTheme.ACCENT_BLUE, ModernTheme.ACCENT_PURPLE,
                         ModernTheme.ACCENT_GREEN, ModernTheme.ACCENT_ORANGE] * len(labels)
                self.ax.pie(values, labels=labels, colors=colors[:len(labels)],
                           autopct='%1.1f%%', textprops={'color': ModernTheme.TEXT_PRIMARY})

        # Configure grid
        self.ax.grid(True, alpha=0.3, color=ModernTheme.TEXT_SECONDARY, linestyle='--')

        # Add legend if needed
        if self.chart_type == "line" and len(data) > 1:
            legend = self.ax.legend(facecolor=ModernTheme.CARD_BG, 
                                  edgecolor=ModernTheme.TEXT_SECONDARY)
            for text in legend.get_texts():
                text.set_color(ModernTheme.TEXT_PRIMARY)        # Style the plot
        self.ax.set_facecolor(ModernTheme.SECONDARY_BG)
        if self.figure:
            self.figure.tight_layout()
        if self.canvas:
            self.canvas.draw()

# --- MAIN GUI CLASS ---
class ServerGUIStatus:
    """Server status information structure"""
    def __init__(self):
        self.running = False
        self.server_address = ""
        self.port = 0
        self.clients_connected = 0
        self.connected_clients = 0  # Alias for consistency
        self.total_clients = 0
        self.active_transfers = 0
        self.bytes_transferred = 0
        self.uptime_seconds = 0
        self.last_activity = ""
        self.error_message = ""
        self.maintenance_stats = {
            'files_cleaned': 0,
            'partial_files_cleaned': 0,
            'clients_cleaned': 0,
            'last_cleanup': 'Never'
        }

class ServerGUI:
    """ULTRA MODERN GUI class for the server dashboard - Enhanced version"""

    def __init__(self, server_instance=None):
        self.server = server_instance
        self.status = ServerGUIStatus()
        self.gui_enabled = False
        self.root = None
        self.tray_icon = None
        self.update_queue = queue.Queue()
        self.running = False
        self.gui_thread = None
        self.start_time = time.time()

        # GUI update lock
        self.lock = threading.Lock()

        # Status widgets references
        self.status_labels = {}
        self.progress_vars = {}

        # Advanced UI components
        self.toast_system = None
        self.advanced_progress_bars = {}
        self.activity_log = []
        self.performance_data = {
            'cpu_usage': deque(maxlen=60),
            'memory_usage': deque(maxlen=60),
            'network_activity': deque(maxlen=60),
            'client_connections': deque(maxlen=60),
            'timestamps': deque(maxlen=60),
            'bytes_transferred': deque(maxlen=60)
        }
        
        # Current tab tracking
        self.current_tab = "dashboard"
        
        # Tables for clients and files
        self.client_table = None
        self.file_table = None
        
        # Charts
        self.performance_chart = None
        self.transfer_chart = None
        self.client_chart = None
        
        # Server reference is already set in __init__ - don't overwrite it!
        
        # Settings - Load from file or use defaults
        self.settings = self._load_settings_from_file()
        
        # Database path
        self.db_path = "defensive.db"
        
        # Performance monitoring
        self.last_bytes_transferred = 0
        self.network_monitor_start = time.time()
    
    def _load_settings_from_file(self):
        """Load settings from configuration file or return defaults"""
        default_settings = {
            'port': 1256,
            'storage_dir': 'received_files',
            'max_clients': 50,
            'session_timeout': 10,
            'maintenance_interval': 60,
            'max_file_size_mb': 4096,
            'verbose_logging': False,
            'auto_backup_db': True
        }
        
        try:
            settings_file = "server_gui_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings_data = json.load(f)
                
                # Merge loaded settings with defaults to ensure all keys exist
                if 'server_settings' in settings_data:
                    loaded_settings = settings_data['server_settings']
                    # Update defaults with loaded values
                    for key, value in loaded_settings.items():
                        if key in default_settings:
                            default_settings[key] = value
                    
                    # Restore GUI preferences if available
                    if 'gui_preferences' in settings_data:
                        gui_prefs = settings_data['gui_preferences']
                        if 'last_tab' in gui_prefs:
                            self.current_tab = gui_prefs['last_tab']
                    
                    print(f"Settings loaded from {settings_file}")
                else:
                    print(f"Invalid settings file format, using defaults")
            else:
                print(f"Settings file not found, using defaults")
                
        except Exception as e:
            print(f"Failed to load settings from file: {e}, using defaults")
            
        return default_settings
    
    def _save_current_settings(self):
        """Save current settings to file (for use during runtime)"""
        try:
            settings_file = "server_gui_settings.json"
            settings_data = {
                'server_settings': self.settings,
                'gui_preferences': {
                    'last_tab': self.current_tab,
                    'window_state': 'normal',
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
                
            print(f"Current settings saved to {settings_file}")
            return True
            
        except Exception as e:
            print(f"Failed to save current settings: {e}")
            return False
        
    def initialize(self) -> bool:
        """Initialize GUI system"""
        try:
            self.running = True
            self.gui_thread = threading.Thread(target=self._gui_main_loop, daemon=False)
            self.gui_thread.start()

            # Wait for GUI to initialize
            max_wait = 50  # 5 seconds max
            wait_count = 0
            while not self.gui_enabled and wait_count < max_wait:
                time.sleep(0.1)
                wait_count += 1

            if self.gui_enabled:
                print("[OK] Enhanced Modern GUI initialized successfully!")
                return True
            else:
                print("[ERROR] Modern GUI initialization timed out")
                return False

        except Exception as e:
            print(f"GUI initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def shutdown(self):
        """Enhanced shutdown with settings persistence and cleanup"""
        print("Starting GUI shutdown process...")
        self.running = False
        
        try:
            # Save current settings and state before shutdown
            self._save_current_settings()
            self._add_activity_log("💾 Settings saved during shutdown")
        except Exception as e:
            print(f"Warning: Failed to save settings during shutdown: {e}")
        
        try:
            # Stop system tray
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                    print("[OK] System tray stopped")
                except Exception as e:
                    print(f"Warning: Failed to stop tray icon: {e}")
            
            # Gracefully shutdown GUI
            if self.root:
                try:
                    self.root.quit()
                    print("[OK] GUI root window closed")
                except Exception as e:
                    print(f"Warning: Failed to quit GUI root window: {e}")
            
            # Wait for GUI thread to complete
            if self.gui_thread and self.gui_thread.is_alive():
                print("Waiting for GUI thread to complete...")
                self.gui_thread.join(timeout=3.0)
                if self.gui_thread.is_alive():
                    print("Warning: GUI thread did not complete within timeout")
                else:
                    print("[OK] GUI thread completed successfully")
                    
        except Exception as e:
            print(f"Error during shutdown: {e}")

        print("GUI shutdown completed")

    def _gui_main_loop(self):
        """Main GUI thread loop"""
        try:
            print("Starting enhanced ultra modern GUI main loop...")
            # Initialize tkinter with error handling
            try:
                self.root = tk.Tk()
                print("Tkinter root created")
            except Exception as e:
                print(f"Failed to create Tkinter root: {e}")
                print("GUI will not be available - continuing in console mode")
                return

            # Configure the root window
            try:
                self.root.title("[SECURE] ULTRA MODERN Encrypted Backup Server - Enhanced")
                self.root.geometry("1200x800")
                self.root.minsize(1000, 700)
                self.root.configure(bg=ModernTheme.PRIMARY_BG)
                self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

                # Force window to front and make it visible
                self.root.lift()
                self.root.attributes('-topmost', True)
                self.root.after(1000, lambda: self.root.attributes('-topmost', False) if self.root else None)
                self.root.focus_force()
                self.root.deiconify()  # Ensure window is not minimized
                self.root.state('normal')  # Ensure window is in normal state
                
                # Additional visibility fixes
                self.root.wm_state('normal')
                self.root.tkraise()
                self.root.grab_set()  # Keep focus initially
                self.root.after(2000, lambda: self.root.grab_release() if self.root else None)

                print("Root window configured with modern theme")
            except Exception as e:
                print(f"Failed to configure root window: {e}")
                if self.root:
                    self.root.destroy()
                return

            # Create modern GUI components
            try:
                print("Creating enhanced ultra modern main window...")
                self._create_main_window()
                print("Creating enhanced ultra modern main window...")
                self._create_system_tray()
                print("System tray created")
            except Exception as e:
                print(f"Failed to create GUI components: {e}")
                if self.root:
                    self.root.destroy()
                return

            # Mark GUI as enabled
            self.gui_enabled = True
            print("Enhanced Modern GUI enabled, starting main loop")

            # Start update timer
            self._schedule_updates()

            # Run GUI main loop
            self.root.mainloop()

        except Exception as e:
            print(f"Modern GUI main loop error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.gui_enabled = False
            print("Modern GUI main loop ended")
    
    def _create_main_window(self):
        """Create the enhanced main window with tabs"""
        print("Creating enhanced ultra modern main window...")

        # Configure modern styling
        self._setup_modern_styles()

        # Create menu bar
        self._create_menu_bar()

        # Create main container
        main_container = tk.Frame(self.root, bg=ModernTheme.PRIMARY_BG, padx=10, pady=10)
        main_container.pack(fill="both", expand=True)

        # Header with title and real-time clock
        self._create_header(main_container)

        # Create tab system
        self._create_tab_system(main_container)

        # Initialize components
        self.toast_system = ToastNotification(self.root)        # Show welcome toast
        if self.root and self.toast_system:
            def show_welcome():
                if self.toast_system:  # Double-check it's still available
                    self.toast_system.show_toast("[READY] Enhanced Ultra Modern GUI Ready", "success", 3000)
            self.root.after(1000, show_welcome)

        print("Enhanced ultra modern main window created successfully!")

    def _create_menu_bar(self):
        """Create modern menu bar"""
        if not self.root:
            return
            
        menubar = tk.Menu(self.root, bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                         activebackground=ModernTheme.ACCENT_BLUE,
                         activeforeground=ModernTheme.TEXT_PRIMARY)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="💾 Export Clients...", command=self._export_clients)
        file_menu.add_command(label="📊 Export Files...", command=self._export_files)
        file_menu.add_separator()
        file_menu.add_command(label="🔄 Backup Database", command=self._backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="[EXIT] Exit", command=self._exit_server)

        # Server menu
        server_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                             fg=ModernTheme.TEXT_PRIMARY,
                             activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="Server", menu=server_menu)
        server_menu.add_command(label="Settings...", command=self._show_settings)
        server_menu.add_command(label="🔄 Restart Server", command=self._restart_server)
        server_menu.add_separator()
        server_menu.add_command(label="Clear Activity Log", command=self._clear_activity_log)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="🏠 Dashboard", command=lambda: self._switch_tab("dashboard"))
        view_menu.add_command(label="👥 Clients", command=lambda: self._switch_tab("clients"))
        view_menu.add_command(label="📁 Files", command=lambda: self._switch_tab("files"))
        view_menu.add_command(label="📈 Analytics", command=lambda: self._switch_tab("analytics"))

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="🏥 Component Status", command=self.show_component_status_dialog)
        tools_menu.add_separator()
        tools_menu.add_command(label="🔧 System Diagnostics", command=self._run_system_diagnostics)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="📖 Documentation", command=self._show_documentation)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_header(self, parent):
        """Create header with title and clock"""
        header_frame = tk.Frame(parent, bg=ModernTheme.PRIMARY_BG, height=60)
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(header_frame, text="[SECURE] Encrypted Backup Server",
                              bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                              font=(ModernTheme.FONT_FAMILY, 22, 'bold'))
        title_label.pack(side="left", padx=10, pady=10)

        # Clock and status
        status_frame = tk.Frame(header_frame, bg=ModernTheme.PRIMARY_BG)
        status_frame.pack(side="right", padx=10, pady=10)

        self.clock_label = tk.Label(status_frame, text="",
                                   bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_SECONDARY,
                                   font=(ModernTheme.FONT_FAMILY, 12))
        self.clock_label.pack(anchor="e")

        # Server status indicator
        status_indicator_frame = tk.Frame(status_frame, bg=ModernTheme.PRIMARY_BG)
        status_indicator_frame.pack(pady=(5, 0), anchor="e")

        self.header_status_label = tk.Label(status_indicator_frame, text="Server Offline",
                                           bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_SECONDARY,
                                           font=(ModernTheme.FONT_FAMILY, 11))
        self.header_status_label.pack(side="left", padx=(0, 5))

        self.header_status_indicator = ModernStatusIndicator(status_indicator_frame)
        self.header_status_indicator.pack(side="left")

    def _create_tab_system(self, parent):
        """Create tab navigation system"""
        # Tab buttons frame
        tab_frame = tk.Frame(parent, bg=ModernTheme.SECONDARY_BG)
        tab_frame.pack(fill="x", padx=10)

        self.tab_buttons = {}
        tabs = [
            ("dashboard", "🏠 Dashboard"),
            ("clients", "👥 Clients"),
            ("files", "📁 Files"),
            ("analytics", "📈 Analytics")
        ]

        # Add process monitoring tab if available
        if PROCESS_MONITOR_AVAILABLE:
            tabs.append(("processes", "🔍 Processes"))

        for tab_id, tab_label in tabs:
            btn = tk.Button(tab_frame, text=tab_label, 
                           command=lambda t=tab_id: self._switch_tab(t),
                           bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                           font=(ModernTheme.FONT_FAMILY, 12, 'bold'),
                           relief="flat", bd=0, padx=30, pady=10)
            btn.pack(side="left", padx=2, pady=2)
            self.tab_buttons[tab_id] = btn

        # Content area
        self.content_area = tk.Frame(parent, bg=ModernTheme.PRIMARY_BG)
        self.content_area.pack(fill="both", expand=True, padx=10, pady=10)

        # Create all tab contents
        self.tab_contents = {}
        self._create_dashboard_tab()
        self._create_clients_tab()
        self._create_files_tab()
        self._create_analytics_tab()

        # Create process monitoring tab if available
        if PROCESS_MONITOR_AVAILABLE:
            self._create_process_monitor_tab()

        # Show dashboard by default
        self._switch_tab("dashboard")

    def _switch_tab(self, tab_id):
        """Switch between tabs"""
        # Update button appearance
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.configure(bg=ModernTheme.ACCENT_BLUE)
            else:
                btn.configure(bg=ModernTheme.CARD_BG)

        # Hide all tabs
        for content in self.tab_contents.values():
            content.pack_forget()

        # Show selected tab
        if tab_id in self.tab_contents:
            self.tab_contents[tab_id].pack(fill="both", expand=True)
            self.current_tab = tab_id

            # Update data for specific tabs
            if tab_id == "clients":
                self._refresh_client_table()
            elif tab_id == "files":
                self._refresh_file_table()
            elif tab_id == "analytics":
                self._update_analytics_charts()

    def _create_dashboard_tab(self):
        """Create dashboard tab content"""
        dashboard = tk.Frame(self.content_area, bg=ModernTheme.PRIMARY_BG)
        self.tab_contents["dashboard"] = dashboard

        # Create scrollable container
        canvas = tk.Canvas(dashboard, bg=ModernTheme.PRIMARY_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(dashboard, orient="vertical", command=canvas.yview,
                               bg=ModernTheme.ACCENT_BG, troughcolor=ModernTheme.SECONDARY_BG)

        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.PRIMARY_BG)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind canvas resize
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create dashboard layout
        self._create_compact_two_column_layout(scrollable_frame)

    def _create_clients_tab(self):
        """Create clients tab content"""
        clients_tab = tk.Frame(self.content_area, bg=ModernTheme.PRIMARY_BG)
        self.tab_contents["clients"] = clients_tab

        # Client management card
        client_card = ModernCard(clients_tab, title="👥 Client Management")
        client_card.pack(fill="both", expand=True, padx=5, pady=5)

        # Control buttons
        control_frame = tk.Frame(client_card.content_frame, bg=ModernTheme.CARD_BG)
        control_frame.pack(fill="x", padx=10, pady=10)

        refresh_btn = tk.Button(control_frame, text="🔄 Refresh",
                              command=self._refresh_client_table,
                              bg=ModernTheme.ACCENT_BLUE, fg=ModernTheme.TEXT_PRIMARY,
                              font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                              relief="flat", bd=0, padx=15, pady=5)
        refresh_btn.pack(side="left", padx=(0, 5))

        details_btn = tk.Button(control_frame, text="📋 Details",
                              command=self._show_client_details,
                              bg=ModernTheme.ACCENT_PURPLE, fg=ModernTheme.TEXT_PRIMARY,
                              font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                              relief="flat", bd=0, padx=15, pady=5)
        details_btn.pack(side="left", padx=5)

        disconnect_btn = tk.Button(control_frame, text="🔌 Disconnect",
                                 command=self._disconnect_client,
                                 bg=ModernTheme.WARNING, fg=ModernTheme.TEXT_PRIMARY,
                                 font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                                 relief="flat", bd=0, padx=15, pady=5)
        disconnect_btn.pack(side="left", padx=5)

        export_btn = tk.Button(control_frame, text="💾 Export",
                             command=self._export_clients,
                             bg=ModernTheme.ACCENT_GREEN, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                             relief="flat", bd=0, padx=15, pady=5)
        export_btn.pack(side="left", padx=5)

        # Client table
        columns = {
            'name': {'text': 'Client Name', 'width': 200},
            'id': {'text': 'Client ID', 'width': 300},
            'status': {'text': 'Status', 'width': 100},
            'last_seen': {'text': 'Last Seen', 'width': 200},
            'files': {'text': 'Files', 'width': 80}
        }

        self.client_table = ModernTable(client_card.content_frame, columns)
        self.client_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.client_table.set_selection_callback(self._on_client_selected)

    def _create_files_tab(self):
        """Create files tab content"""
        files_tab = tk.Frame(self.content_area, bg=ModernTheme.PRIMARY_BG)
        self.tab_contents["files"] = files_tab

        # File management card
        file_card = ModernCard(files_tab, title="📁 File Management")
        file_card.pack(fill="both", expand=True, padx=5, pady=5)

        # Control buttons
        control_frame = tk.Frame(file_card.content_frame, bg=ModernTheme.CARD_BG)
        control_frame.pack(fill="x", padx=10, pady=10)

        refresh_btn = tk.Button(control_frame, text="🔄 Refresh",
                              command=self._refresh_file_table,
                              bg=ModernTheme.ACCENT_BLUE, fg=ModernTheme.TEXT_PRIMARY,
                              font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                              relief="flat", bd=0, padx=15, pady=5)
        refresh_btn.pack(side="left", padx=(0, 5))

        details_btn = tk.Button(control_frame, text="📋 Details",
                              command=self._show_file_details,
                              bg=ModernTheme.ACCENT_PURPLE, fg=ModernTheme.TEXT_PRIMARY,
                              font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                              relief="flat", bd=0, padx=15, pady=5)
        details_btn.pack(side="left", padx=5)

        view_content_btn = tk.Button(control_frame, text="View Content",
                                   command=self._view_file_content,
                                   bg=ModernTheme.ACCENT_PURPLE, fg=ModernTheme.TEXT_PRIMARY,
                                   font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SMALL),
                                   relief="flat", bd=0, padx=15, pady=5)
        view_content_btn.pack(side="left", padx=2)

        verify_btn = tk.Button(control_frame, text="Verify",
                             command=self._verify_file,
                             bg=ModernTheme.SUCCESS, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                             relief="flat", bd=0, padx=15, pady=5)
        verify_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(control_frame, text="Delete",
                             command=self._delete_file,
                             bg=ModernTheme.ERROR, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                             relief="flat", bd=0, padx=15, pady=5)
        delete_btn.pack(side="left", padx=5)

        export_btn = tk.Button(control_frame, text="💾 Export",
                             command=self._export_files,
                             bg=ModernTheme.ACCENT_GREEN, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                             relief="flat", bd=0, padx=15, pady=5)
        export_btn.pack(side="left", padx=5)

        # File table
        columns = {
            'filename': {'text': 'File Name', 'width': 250},
            'client': {'text': 'Client', 'width': 150},
            'size': {'text': 'Size', 'width': 100},
            'date': {'text': 'Date', 'width': 150},
            'verified': {'text': 'Verified', 'width': 80},
            'path': {'text': 'Path', 'width': 200}
        }

        self.file_table = ModernTable(file_card.content_frame, columns)
        self.file_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.file_table.set_selection_callback(self._on_file_selected)

    def _create_analytics_tab(self):
        """Create analytics tab content"""
        analytics_tab = tk.Frame(self.content_area, bg=ModernTheme.PRIMARY_BG)
        self.tab_contents["analytics"] = analytics_tab

        # Create grid layout
        analytics_tab.grid_columnconfigure(0, weight=1)
        analytics_tab.grid_columnconfigure(1, weight=1)
        analytics_tab.grid_rowconfigure(0, weight=1)
        analytics_tab.grid_rowconfigure(1, weight=1)

        # Performance chart
        perf_card = ModernCard(analytics_tab, title="⚡ System Performance")
        perf_card.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.performance_chart = ModernChart(perf_card.content_frame, chart_type="line")
        self.performance_chart.pack(fill="both", expand=True, padx=10, pady=10)

        # Transfer volume chart
        transfer_card = ModernCard(analytics_tab, title="📊 Transfer Volume")
        transfer_card.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.transfer_chart = ModernChart(transfer_card.content_frame, chart_type="line")
        self.transfer_chart.pack(fill="both", expand=True, padx=10, pady=10)

        # Client connections chart
        client_card = ModernCard(analytics_tab, title="👥 Client Activity")
        client_card.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.client_chart = ModernChart(client_card.content_frame, chart_type="bar")
        self.client_chart.pack(fill="both", expand=True, padx=10, pady=10)

        # Summary statistics
        stats_card = ModernCard(analytics_tab, title="📈 Summary Statistics")
        stats_card.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self._create_summary_stats(stats_card.content_frame)

    def _create_summary_stats(self, parent):
        """Create summary statistics panel"""
        stats_frame = tk.Frame(parent, bg=ModernTheme.CARD_BG)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.stats_labels = {}
        stats = [
            ('total_files', '📁 Total Files:', '0'),
            ('total_size', '💾 Total Size:', '0 MB'),
            ('avg_file_size', '📊 Avg File Size:', '0 MB'),
            ('success_rate', 'Success Rate:', '100%'),
            ('peak_clients', '👥 Peak Clients:', '0'),
            ('uptime_days', '⏰ Uptime:', '0 days')
        ]

        for stat_id, label_text, default_value in stats:
            stat_frame = tk.Frame(stats_frame, bg=ModernTheme.CARD_BG)
            stat_frame.pack(fill="x", pady=5)

            label = tk.Label(stat_frame, text=label_text, bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.TEXT_SECONDARY, font=(ModernTheme.FONT_FAMILY, 11))
            label.pack(side="left")

            value_label = tk.Label(stat_frame, text=default_value, bg=ModernTheme.CARD_BG,
                                 fg=ModernTheme.ACCENT_BLUE, font=(ModernTheme.FONT_FAMILY, 11, 'bold'))
            value_label.pack(side="right")
            self.stats_labels[stat_id] = value_label

    def _create_process_monitor_tab(self):
        """Create process monitoring tab content"""
        if not PROCESS_MONITOR_AVAILABLE:
            return

        process_tab = tk.Frame(self.content_area, bg=ModernTheme.PRIMARY_BG)
        self.tab_contents["processes"] = process_tab

        # Create main container with padding
        main_container = tk.Frame(process_tab, bg=ModernTheme.PRIMARY_BG)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            main_container,
            text="🔍 Process Monitoring",
            font=("Segoe UI", 16, "bold"),
            bg=ModernTheme.PRIMARY_BG,
            fg=ModernTheme.TEXT_PRIMARY
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Create process monitor widget - Fixed availability check
        try:
            if PROCESS_MONITOR_AVAILABLE and ProcessMonitorWidget is not None:
                self.process_monitor_widget = ProcessMonitorWidget(
                    main_container,
                    title="Active Backup Processes",
                    update_interval=3.0
                )
                self.process_monitor_widget.pack(fill="both", expand=True)
            else:
                # Fallback when process monitor is not available
                error_label = tk.Label(
                    main_container,
                    text="Process monitoring not available\n(ProcessMonitorWidget not installed)",
                    font=("Segoe UI", 12),
                    bg=ModernTheme.PRIMARY_BG,
                    fg=ModernTheme.TEXT_SECONDARY
                )
                error_label.pack(pady=50)

        except Exception as e:
            # Fallback if process monitor widget fails
            error_label = tk.Label(
                main_container,
                text=f"Process monitoring unavailable: {e}",
                font=("Segoe UI", 12),
                bg=ModernTheme.PRIMARY_BG,
                fg=ModernTheme.TEXT_SECONDARY
            )
            error_label.pack(pady=50)

    def _create_compact_two_column_layout(self, parent):
        """Create a compact two-column layout for dashboard"""
        # Main container with two columns
        main_container = tk.Frame(parent, bg=ModernTheme.PRIMARY_BG)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Configure grid weights for responsive columns
        main_container.columnconfigure(0, weight=1, uniform="group1")
        main_container.columnconfigure(1, weight=1, uniform="group1")
        main_container.rowconfigure(0, weight=1)

        # Left Column
        left_column = tk.Frame(main_container, bg=ModernTheme.PRIMARY_BG)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Right Column
        right_column = tk.Frame(main_container, bg=ModernTheme.PRIMARY_BG)
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # LEFT COLUMN CONTENT (Primary Stats)
        self._create_compact_server_status_card(left_column)
        self._create_compact_client_stats_card(left_column)
        self._create_compact_transfer_stats_card(left_column)
        self._create_compact_performance_card(left_column)

        # RIGHT COLUMN CONTENT (Secondary Info & Controls)
        self._create_enhanced_control_panel(right_column)
        self._create_compact_health_monitoring_card(right_column)
        self._create_compact_maintenance_card(right_column)
        self._create_compact_activity_log_card(right_column)
        self._create_compact_status_message_card(right_column)

    def _create_compact_server_status_card(self, parent):
        """Create compact server status card with glass morphism"""
        card = GlassMorphismCard(parent, title="Server Status")
        card.pack(fill="x", pady=(0, 8), padx=3)

        # Status display
        status_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        status_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(status_frame, text="Status:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['status'] = tk.Label(status_frame, text="🛑 Stopped",
                                               bg=ModernTheme.GLASS_BG, fg=ModernTheme.ERROR,
                                               font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['status'].pack(side="right")

        # Address
        addr_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        addr_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(addr_frame, text="Address:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['address'] = tk.Label(addr_frame, text="🌐 Not configured",
                                                bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_PRIMARY,
                                                font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['address'].pack(side="right")

        # Uptime
        uptime_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        uptime_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(uptime_frame, text="Uptime:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY,  9)).pack(side="left")
        self.status_labels['uptime'] = tk.Label(uptime_frame, text="Uptime: 00:00:00",
                                              bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_PRIMARY,
                                              font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['uptime'].pack(side="right")

        # Port
        port_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        port_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(port_frame, text="Port:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['port'] = tk.Label(port_frame, text="1256", bg=ModernTheme.GLASS_BG,
                                            fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['port'].pack(side="right")

    def _create_compact_client_stats_card(self, parent):
        """Create compact client statistics card with glass morphism"""
        card = GlassMorphismCard(parent, title="👥 Client Statistics")
        card.pack(fill="x", pady=(0, 8), padx=3)

        # Connected clients
        conn_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        conn_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(conn_frame, text="Connected:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['connected'] = tk.Label(conn_frame, text="0", bg=ModernTheme.GLASS_BG,
                                                  fg=ModernTheme.ACCENT_BLUE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['connected'].pack(side="right")

        # Total registered
        total_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        total_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(total_frame, text="Total Registered:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['total'] = tk.Label(total_frame, text="0", bg=ModernTheme.GLASS_BG,
                                              fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['total'].pack(side="right")

        # Active transfers
        trans_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        trans_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(trans_frame, text="Active Transfers:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['active_transfers'] = tk.Label(trans_frame, text="0", bg=ModernTheme.GLASS_BG,
                                                         fg=ModernTheme.ACCENT_GREEN, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['active_transfers'].pack(side="right")

    def _create_compact_transfer_stats_card(self, parent):
        """Create compact transfer statistics card with glass morphism"""
        card = GlassMorphismCard(parent, title="📊 Transfer Statistics")
        card.pack(fill="x", pady=(0, 8), padx=3)

        # Bytes transferred
        bytes_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        bytes_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(bytes_frame, text="Bytes Transferred:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['bytes'] = tk.Label(bytes_frame, text="0 B", bg=ModernTheme.CARD_BG,
                                              fg=ModernTheme.ACCENT_PURPLE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['bytes'].pack(side="right")

        # Transfer rate
        rate_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        rate_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(rate_frame, text="Transfer Rate:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['transfer_rate'] = tk.Label(rate_frame, text="0 KB/s", bg=ModernTheme.CARD_BG,
                                                      fg=ModernTheme.ACCENT_ORANGE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['transfer_rate'].pack(side="right")

        # Last activity
        activity_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        activity_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(activity_frame, text="Last Activity:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['activity'] = tk.Label(activity_frame, text="None", bg=ModernTheme.CARD_BG,
                                                 fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['activity'].pack(side="right")

    def _create_compact_performance_card(self, parent):
        """Create compact performance monitoring card with real data"""
        card = ModernCard(parent, title="⚡ Performance Monitor") # Changed to ModernCard
        card.pack(fill="x", pady=(0, 8), padx=3)

        # CPU Usage with mini progress bar
        cpu_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        cpu_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(cpu_frame, text="CPU:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['cpu_usage'] = tk.Label(cpu_frame, text="0%", bg=ModernTheme.CARD_BG,
                                                  fg=ModernTheme.ACCENT_GREEN, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['cpu_usage'].pack(side="right")

        self.advanced_progress_bars['cpu'] = AdvancedProgressBar(card.content_frame, width=200, height=12) # Changed to card.content_frame
        self.advanced_progress_bars['cpu'].pack(padx=10, pady=(0, 3))

        # Memory Usage with mini progress bar
        mem_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        mem_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(mem_frame, text="Memory:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['memory_usage'] = tk.Label(mem_frame, text="0%", bg=ModernTheme.CARD_BG,
                                                     fg=ModernTheme.ACCENT_PURPLE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['memory_usage'].pack(side="right")

        self.advanced_progress_bars['memory'] = AdvancedProgressBar(card.content_frame, width=200, height=12) # Changed to card.content_frame
        self.advanced_progress_bars['memory'].pack(padx=10, pady=(0, 3))

        # Disk Usage
        disk_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        disk_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(disk_frame, text="Disk:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['disk_usage'] = tk.Label(disk_frame, text="0%", bg=ModernTheme.CARD_BG,
                                                   fg=ModernTheme.ACCENT_ORANGE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['disk_usage'].pack(side="right")

        self.advanced_progress_bars['disk'] = AdvancedProgressBar(card.content_frame, width=200, height=12) # Changed to card.content_frame
        self.advanced_progress_bars['disk'].pack(padx=10, pady=(0, 3))

        # Network Activity
        net_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        net_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(net_frame, text="Network:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['network_activity'] = tk.Label(net_frame, text="Idle", bg=ModernTheme.CARD_BG,
                                                         fg=ModernTheme.ACCENT_BLUE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['network_activity'].pack(side="right")

    def _create_compact_health_monitoring_card(self, parent):
        """Create compact system health monitoring card with visual indicators"""
        card = ModernCard(parent, title="🏥 System Health")
        card.pack(fill="x", pady=(0, 8), padx=3)

        # Database Connection Health
        db_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        db_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(db_frame, text="Database:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['db_health'] = tk.Label(db_frame, text="🔴 Disconnected", bg=ModernTheme.CARD_BG,
                                                  fg=ModernTheme.ERROR, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['db_health'].pack(side="right")

        # Network Server Health
        net_health_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        net_health_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(net_health_frame, text="Network Server:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['network_health'] = tk.Label(net_health_frame, text="🔴 Offline", bg=ModernTheme.CARD_BG,
                                                       fg=ModernTheme.ERROR, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['network_health'].pack(side="right")

        # GUI Integration Health
        gui_health_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        gui_health_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(gui_health_frame, text="GUI Integration:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['gui_health'] = tk.Label(gui_health_frame, text="🟢 Active", bg=ModernTheme.CARD_BG,
                                                   fg=ModernTheme.SUCCESS, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['gui_health'].pack(side="right")

        # System Resources Health
        system_health_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        system_health_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(system_health_frame, text="System Resources:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['system_health'] = tk.Label(system_health_frame, text="🟡 Monitoring", bg=ModernTheme.CARD_BG,
                                                      fg=ModernTheme.WARNING, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['system_health'].pack(side="right")

        # Overall Health Status
        overall_health_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        overall_health_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(overall_health_frame, text="Overall Status:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9, 'bold')).pack(side="left")
        self.status_labels['overall_health'] = tk.Label(overall_health_frame, text="🟡 Partial", bg=ModernTheme.CARD_BG,
                                                       fg=ModernTheme.WARNING, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['overall_health'].pack(side="right")

    def _create_compact_maintenance_card(self, parent):
        """Create compact maintenance statistics card"""
        card = ModernCard(parent, title="Maintenance") # Changed to ModernCard
        card.pack(fill="x", pady=(0, 8), padx=3)

        # Files cleaned
        files_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        files_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(files_frame, text="Files Cleaned:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['files_cleaned'] = tk.Label(files_frame, text="0", bg=ModernTheme.CARD_BG,
                                                      fg=ModernTheme.ACCENT_ORANGE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['files_cleaned'].pack(side="right")

        # Partial files cleaned
        partial_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        partial_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(partial_frame, text="Partial Files:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['partial_cleaned'] = tk.Label(partial_frame, text="0", bg=ModernTheme.CARD_BG,
                                                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['partial_cleaned'].pack(side="right")

        # Clients cleaned
        clients_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        clients_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(clients_frame, text="Clients Cleaned:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['clients_cleaned'] = tk.Label(clients_frame, text="0", bg=ModernTheme.CARD_BG,
                                                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['clients_cleaned'].pack(side="right")

        # Last cleanup
        cleanup_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        cleanup_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(cleanup_frame, text="Last Cleanup:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['last_cleanup'] = tk.Label(cleanup_frame, text="Never", bg=ModernTheme.CARD_BG,
                                                     fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['last_cleanup'].pack(side="right")

    def _create_compact_activity_log_card(self, parent):
        """Create compact activity log card"""
        card = ModernCard(parent, title="📋 Activity Log") # Changed to ModernCard
        card.pack(fill="x", pady=(0, 8), padx=3)

        title_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        title_frame.pack(fill="x", padx=10, pady=(8, 5))

        title = tk.Label(title_frame, text="📋 Activity Log", bg=ModernTheme.CARD_BG,
                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 12, 'bold'))
        title.pack(side="left")

        # Clear log button (smaller)
        clear_btn = tk.Button(title_frame, text="Clear", command=self._clear_activity_log,
                             bg=ModernTheme.WARNING, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 8, 'bold'), relief="flat", bd=0, padx=5, pady=2)
        clear_btn.pack(side="right")

        # Compact scrollable text area
        log_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG) # Changed to card.content_frame
        log_frame.pack(fill="x", padx=10, pady=(0, 8))

        scrollbar = tk.Scrollbar(log_frame, bg=ModernTheme.ACCENT_BG, width=12)
        scrollbar.pack(side="right", fill="y")

        self.activity_log_text = tk.Text(log_frame, height=4, bg=ModernTheme.SECONDARY_BG,
                                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 8),
                                        yscrollcommand=scrollbar.set, wrap="word", relief="flat", bd=0)
        self.activity_log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.activity_log_text.yview)

        self._add_activity_log("[SYSTEM] Enhanced Ultra Modern GUI System Initialized")

    def _create_compact_status_message_card(self, parent):
        """Create compact status message card"""
        card = ModernCard(parent, title="📢 Status") # Changed to ModernCard
        card.pack(fill="x", pady=(0, 8), padx=3)

        title = tk.Label(card.content_frame, text="📢 Status", bg=ModernTheme.CARD_BG, # Changed to card.content_frame
                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 12, 'bold'))
        title.pack(anchor="w", padx=10, pady=(8, 5))

        self.status_labels['error'] = tk.Label(card.content_frame, text="[READY] Ready", bg=ModernTheme.CARD_BG, # Changed to card.content_frame
                                              fg=ModernTheme.SUCCESS, font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['error'].pack(padx=10, pady=(5, 8), anchor="w")

    def _create_enhanced_control_panel(self, parent):
        """Create enhanced compact control panel"""
        card = ModernCard(parent, title="🎛️ Control Panel") # Changed to ModernCard
        card.pack(fill="x", pady=(0, 8), padx=3)

        # Compact button grid
        button_frame = tk.Frame(card.content_frame, bg=ModernTheme.CARD_BG)
        button_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure grid
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.rowconfigure(0, weight=1)
        button_frame.rowconfigure(1, weight=1)
        button_frame.rowconfigure(2, weight=1)

        # Row 1
        start_btn = self._create_modern_button(button_frame, "▶️ Start Server", self._start_server, ModernTheme.SUCCESS)
        start_btn.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0,5))
        ModernTooltip(start_btn, "Start the main backup server")

        stop_btn = self._create_modern_button(button_frame, "⏹️ Stop Server", self._stop_server, ModernTheme.ERROR)
        stop_btn.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0,5))
        ModernTooltip(stop_btn, "Stop the server gracefully")

        # Row 2
        settings_btn = self._create_modern_button(button_frame, "⚙️ Settings", self._show_settings, ModernTheme.ACCENT_BLUE)
        settings_btn.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(5,5))
        ModernTooltip(settings_btn, "Configure server settings")

        restart_btn = self._create_modern_button(button_frame, "🔄 Restart Server", self._restart_server, ModernTheme.WARNING)
        restart_btn.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5,5))
        ModernTooltip(restart_btn, "Restart the server")

        # Row 3
        analytics_btn = self._create_modern_button(button_frame, "📈 Analytics", lambda: self._switch_tab("analytics"), ModernTheme.ACCENT_PURPLE)
        analytics_btn.grid(row=2, column=0, sticky="nsew", padx=(0, 5), pady=(5,0))
        ModernTooltip(analytics_btn, "View performance and usage analytics")

        exit_btn = self._create_modern_button(button_frame, "[EXIT] Exit Application", self._exit_server, ModernTheme.TEXT_SECONDARY)
        exit_btn.grid(row=2, column=1, sticky="nsew", padx=(5, 0), pady=(5,0))
        ModernTooltip(exit_btn, "Exit the GUI application")

    def _create_modern_button(self, parent, text, command, bg_color):
        """Helper to create a modern button."""
        btn = tk.Button(parent, text=text, command=command,
                        bg=bg_color, fg=ModernTheme.TEXT_PRIMARY,
                        font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                        relief="flat", bd=0, padx=15, pady=8)
        return btn

    def _start_server(self):
        """Start the backup server."""
        from .server import BackupServer # Local import to avoid circular dependency # type: ignore
        if self.server and not self.server.running:
            try:
                # The server's start method is already designed to run in threads
                self.server.start()
                if self.toast_system:
                    self.toast_system.show_toast("Server starting...", "info")
                self._add_activity_log("Server start command issued.")
                # The server will update its own status, which will be reflected in the GUI
            except Exception as e:
                if self.toast_system:
                    self.toast_system.show_toast(f"Failed to start server: {e}", "error")
                self._add_activity_log(f"Error starting server: {e}")
        elif self.server and self.server.running:
            if self.toast_system:
                self.toast_system.show_toast("Server is already running.", "warning")
        else:
            if self.toast_system:
                self.toast_system.show_toast("Server instance not available. Please start the server using 'python server.py'", "error")
            self._add_activity_log("[ERROR] Server instance not available. Use 'python server.py' to start properly.")

    def _stop_server(self):
        """Stop the backup server."""
        if self.server and self.server.running:
            try:
                self.server.stop()
                if self.toast_system:
                    self.toast_system.show_toast("Server stopping...", "info")
                self._add_activity_log("Server stop command issued.")
            except Exception as e:
                if self.toast_system:
                    self.toast_system.show_toast(f"Failed to stop server: {e}", "error")
                self._add_activity_log(f"Error stopping server: {e}")
        elif self.server:
            if self.toast_system:
                self.toast_system.show_toast("Server is not running.", "warning")
        else:
            if self.toast_system:
                self.toast_system.show_toast("Server instance not available.", "error")

    def _restart_server(self):
        """Restart the server."""
        if self.server:
            if self.toast_system:
                self.toast_system.show_toast("Restarting server...", "info")
            self.server.stop()
            # Give it a moment to truly stop
            time.sleep(1)
            self.server.start()
            self._add_activity_log("Server restarted.")
        else:
            if self.toast_system:
                self.toast_system.show_toast("Server instance not available.", "warning")

    def _show_settings(self):
        """Show settings dialog."""
        if self.server:
            dialog = SettingsDialog(self.root, self.settings)
            new_settings = dialog.show()
            if new_settings:
                self.settings = new_settings
                # Apply new settings to server if it's running
                if self.server.running:
                    self.server.apply_settings(self.settings) # Assuming BackupServer has apply_settings
                if self.toast_system:
                    self.toast_system.show_toast("Settings saved and applied!", "success")
                self._add_activity_log("Server settings updated.")
            else:
                if self.toast_system:
                    self.toast_system.show_toast("Settings dialog cancelled.", "info")
        else:
            if self.toast_system:
                self.toast_system.show_toast("Server instance not available to configure.", "error")

    def _export_clients(self):
        """Export client data to CSV."""
        if self.server and self.server.db_manager:
            try:
                clients = self.server.db_manager.get_all_clients()
                if not clients:
                    if self.toast_system:
                        self.toast_system.show_toast("No client data to export.", "warning")
                    return

                file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                       filetypes=[("CSV files", "*.csv")],
                                                       title="Export Clients to CSV")
                if file_path:
                    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                        fieldnames = ['id', 'name', 'last_seen']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        for client in clients:
                            writer.writerow(client)
                    if self.toast_system:
                        self.toast_system.show_toast(f"Clients exported to {file_path}", "success")
                    self._add_activity_log(f"Exported client data to {file_path}")
            except Exception as e:
                if self.toast_system:
                    self.toast_system.show_toast(f"Error exporting clients: {e}", "error")
                self._add_activity_log(f"Error exporting clients: {e}")
        else:
            if self.toast_system:
                self.toast_system.show_toast("Server or database not available.", "error")

    def _export_files(self):
        """Export file data to CSV."""
        if self.server and self.server.db_manager:
            try:
                files = self.server.db_manager.get_all_files()
                if not files:
                    if self.toast_system:
                        self.toast_system.show_toast("No file data to export.", "warning")
                    return

                file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                       filetypes=[("CSV files", "*.csv")],
                                                       title="Export Files to CSV")
                if file_path:
                    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                        fieldnames = ['filename', 'client', 'size', 'date', 'verified', 'path']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        for f in files:
                            writer.writerow(f)
                    if self.toast_system:
                        self.toast_system.show_toast(f"Files exported to {file_path}", "success")
                    self._add_activity_log(f"Exported file data to {file_path}")
            except Exception as e:
                if self.toast_system:
                    self.toast_system.show_toast(f"Error exporting files: {e}", "error")
                self._add_activity_log(f"Error exporting files: {e}")
        else:
            if self.toast_system:
                self.toast_system.show_toast("Server or database not available.", "error")

    def _backup_database(self):
        """Create a backup of the SQLite database."""
        if self.server and self.server.db_manager:
            try:
                backup_dir = filedialog.askdirectory(title="Select Backup Directory")
                if backup_dir:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_filename = f"defensive_backup_{timestamp}.db"
                    backup_path = os.path.join(backup_dir, backup_filename)
                    shutil.copy2(self.db_path, backup_path)
                    if self.toast_system:
                        self.toast_system.show_toast(f"Database backed up to {backup_path}", "success")
                    self._add_activity_log(f"Database backed up to {backup_path}")
            except Exception as e:
                if self.toast_system:
                    self.toast_system.show_toast(f"Error backing up database: {e}", "error")
                self._add_activity_log(f"Error backing up database: {e}")
        else:
            if self.toast_system:
                self.toast_system.show_toast("Server or database not available.", "error")

    def _exit_server(self):
        """Exit the application."""
        if self.root:
            self.root.quit()

    def _clear_activity_log(self):
        """Clear the activity log display."""
        self.activity_log.clear()
        if hasattr(self, 'activity_log_text') and self.activity_log_text:
            self.activity_log_text.config(state=tk.NORMAL)
            self.activity_log_text.delete(1.0, tk.END)
            self.activity_log_text.config(state=tk.DISABLED)
        self._add_activity_log("Activity log cleared.")
        if self.toast_system:
            self.toast_system.show_toast("Activity log cleared.", "info")

    def _show_documentation(self):
        """Open documentation."""
        if self.toast_system:
            self.toast_system.show_toast("Documentation not yet implemented.", "info")

    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", "Encrypted Backup Server GUI\nVersion 1.0\nDeveloped by Gemini")

    def _add_activity_log(self, message: str):
        """Add a message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.activity_log.append(log_entry)
        if hasattr(self, 'activity_log_text') and self.activity_log_text:
            self.activity_log_text.config(state=tk.NORMAL)
            self.activity_log_text.insert(tk.END, log_entry + "\n")
            self.activity_log_text.see(tk.END)
            self.activity_log_text.config(state=tk.DISABLED)
        logging.info(message) # Also log to console/file

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in H:M:S."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _update_clock(self):
        """Update the real-time clock display."""
        if hasattr(self, 'clock_label') and self.clock_label:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.clock_label.config(text=now)

    def _update_health_monitoring(self):
        """Update system health monitoring indicators with real data source checks"""
        try:
            # Database Health Check
            db_healthy = False
            db_status = "🔴 Disconnected"
            db_color = ModernTheme.ERROR
            
            if hasattr(self, 'server') and self.server and hasattr(self.server, 'db_manager'):
                try:
                    # Test database connection with actual query
                    if self.server.db_manager and hasattr(self.server.db_manager, 'execute_query'):
                        test_result = self.server.db_manager.execute_query("SELECT 1 as test", fetch=True)
                        if test_result:
                            db_healthy = True
                            db_status = "🟢 Connected"
                            db_color = ModernTheme.SUCCESS
                        else:
                            db_status = "🟡 Limited"
                            db_color = ModernTheme.WARNING
                    else:
                        db_status = "🟡 Available"
                        db_color = ModernTheme.WARNING
                except Exception as db_e:
                    db_status = f"🔴 Error: {str(db_e)[:20]}..."
                    db_color = ModernTheme.ERROR
            
            # Network Server Health Check
            net_healthy = False
            net_status = "🔴 Offline"
            net_color = ModernTheme.ERROR
            
            if hasattr(self, 'server') and self.server and hasattr(self.server, 'network_server'):
                try:
                    if self.server.running and self.server.network_server:
                        # Check if network server is actually listening
                        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        test_socket.settimeout(1)
                        result = test_socket.connect_ex(('127.0.0.1', self.server.port))
                        test_socket.close()
                        
                        if result == 0:
                            net_healthy = True
                            net_status = "🟢 Online"
                            net_color = ModernTheme.SUCCESS
                        else:
                            net_status = "🟡 Starting"
                            net_color = ModernTheme.WARNING
                    else:
                        net_status = "🔴 Stopped"
                        net_color = ModernTheme.ERROR
                except Exception as net_e:
                    net_status = f"🟡 Check Failed"
                    net_color = ModernTheme.WARNING
            
            # System Resources Health Check
            system_healthy = False
            system_status = "🟡 Monitoring"
            system_color = ModernTheme.WARNING
            
            if SYSTEM_MONITOR_AVAILABLE:
                try:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    # Consider system healthy if CPU < 80%, Memory < 85%, Disk < 90%
                    if cpu_percent < 80 and memory.percent < 85 and disk.percent < 90:
                        system_healthy = True
                        system_status = "🟢 Healthy"
                        system_color = ModernTheme.SUCCESS
                    elif cpu_percent >= 90 or memory.percent >= 95 or disk.percent >= 95:
                        system_status = "🔴 Critical"
                        system_color = ModernTheme.ERROR
                    else:
                        system_status = "🟡 Warning"
                        system_color = ModernTheme.WARNING
                except Exception:
                    system_status = "🟡 Fallback"
                    system_color = ModernTheme.WARNING
            else:
                system_status = "🔴 No psutil"
                system_color = ModernTheme.ERROR
            
            # GUI Integration is always healthy if we're here
            gui_status = "🟢 Active"
            gui_color = ModernTheme.SUCCESS
            gui_healthy = True
            
            # Calculate Overall Health
            healthy_components = sum([db_healthy, net_healthy, system_healthy, gui_healthy])
            total_components = 4
            
            if healthy_components == total_components:
                overall_status = "🟢 Excellent"
                overall_color = ModernTheme.SUCCESS
            elif healthy_components >= 3:
                overall_status = "🟡 Good"
                overall_color = ModernTheme.WARNING
            elif healthy_components >= 2:
                overall_status = "🟡 Partial"
                overall_color = ModernTheme.WARNING
            else:
                overall_status = "🔴 Poor"
                overall_color = ModernTheme.ERROR
            
            # Update UI labels
            if 'db_health' in self.status_labels:
                self.status_labels['db_health'].config(text=db_status, fg=db_color)
            if 'network_health' in self.status_labels:
                self.status_labels['network_health'].config(text=net_status, fg=net_color)
            if 'gui_health' in self.status_labels:
                self.status_labels['gui_health'].config(text=gui_status, fg=gui_color)
            if 'system_health' in self.status_labels:
                self.status_labels['system_health'].config(text=system_status, fg=system_color)
            if 'overall_health' in self.status_labels:
                self.status_labels['overall_health'].config(text=overall_status, fg=overall_color)
                
        except Exception as e:
            # Fallback to error status if monitoring fails
            error_msg = f"Health check error: {str(e)[:30]}..."
            if 'overall_health' in self.status_labels:
                self.status_labels['overall_health'].config(text="🔴 Monitor Error", fg=ModernTheme.ERROR)
            print(f"[DEBUG] Health monitoring error: {e}")

    def show_enhanced_error(self, error_message: str, component: str = "System", details: Optional[Dict[str, Any]] = None):
        """Show enhanced error message with specific component status and actionable suggestions"""
        try:
            # Create detailed error information
            error_info = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'component': component,
                'message': error_message,
                'details': details or {}
            }
            
            # Determine error severity and suggested actions
            severity = "error"
            suggested_actions = []
            
            # Component-specific error analysis
            if component.lower() == "database":
                if "permission" in error_message.lower():
                    suggested_actions.extend([
                        "Check file permissions for defensive.db",
                        "Ensure the application has write access",
                        "Try running as administrator"
                    ])
                elif "locked" in error_message.lower():
                    suggested_actions.extend([
                        "Close other applications using the database",
                        "Wait for database lock to release",
                        "Restart the server if lock persists"
                    ])
                elif "connection" in error_message.lower():
                    suggested_actions.extend([
                        "Check if database file exists",
                        "Verify database file integrity",
                        "Restart the database connection"
                    ])
                else:
                    suggested_actions.append("Check database status in System Health panel")
                    
            elif component.lower() == "network":
                if "port" in error_message.lower():
                    suggested_actions.extend([
                        f"Check if port {getattr(self.server, 'port', 1256)} is available",
                        "Close applications using the same port",
                        "Configure a different port in settings"
                    ])
                elif "connection" in error_message.lower():
                    suggested_actions.extend([
                        "Check network connectivity",
                        "Verify firewall settings",
                        "Restart network services"
                    ])
                else:
                    suggested_actions.append("Check network status in System Health panel")
                    
            elif component.lower() == "system":
                if "memory" in error_message.lower():
                    suggested_actions.extend([
                        "Close unnecessary applications",
                        "Free up system memory",
                        "Check system resource usage"
                    ])
                elif "disk" in error_message.lower():
                    suggested_actions.extend([
                        "Free up disk space",
                        "Check disk permissions",
                        "Move files to another drive"
                    ])
                else:
                    suggested_actions.append("Check system resources in Performance Monitor")
                    
            elif component.lower() == "client":
                suggested_actions.extend([
                    "Check client connection status",
                    "Verify client authentication",
                    "Review client logs for details"
                ])
            
            # Default suggestions if none specific found
            if not suggested_actions:
                suggested_actions.extend([
                    "Check system health indicators",
                    "Review activity log for more details",
                    "Restart the affected component"
                ])
            
            # Create enhanced error message for toast
            enhanced_message = f"{component}: {error_message}"
            
            # Show immediate toast notification
            if hasattr(self, 'toast_system') and self.toast_system:
                self.toast_system.show_toast(enhanced_message, severity, duration=5000)
            
            # Log detailed error with suggestions
            detailed_log_entry = f"❌ {component} Error: {error_message}"
            if suggested_actions:
                detailed_log_entry += f" | Suggestions: {'; '.join(suggested_actions[:2])}..."
            
            self._add_activity_log(detailed_log_entry)
            
            # Update component-specific status if error is critical
            if severity == "error":
                # Update relevant health status based on component
                if component.lower() == "database" and 'db_health' in self.status_labels:
                    self.status_labels['db_health'].config(text="🔴 Error", fg=ModernTheme.ERROR)
                elif component.lower() == "network" and 'network_health' in self.status_labels:
                    self.status_labels['network_health'].config(text="🔴 Error", fg=ModernTheme.ERROR)
                elif component.lower() == "system" and 'system_health' in self.status_labels:
                    self.status_labels['system_health'].config(text="🔴 Error", fg=ModernTheme.ERROR)
                
                # Update overall health to reflect error
                if 'overall_health' in self.status_labels:
                    self.status_labels['overall_health'].config(text="🔴 Component Error", fg=ModernTheme.ERROR)
            
            # For debugging, print enhanced error info
            print(f"[ENHANCED ERROR] {component}: {error_message}")
            if details:
                print(f"[ERROR DETAILS] {details}")
            if suggested_actions:
                print(f"[SUGGESTIONS] {'; '.join(suggested_actions)}")
                
        except Exception as e:
            # Fallback to basic error display if enhanced error handling fails
            print(f"[ERROR] Enhanced error display failed: {e}")
            if hasattr(self, 'toast_system') and self.toast_system:
                self.toast_system.show_toast(f"{component}: {error_message}", "error")

    def show_component_status_dialog(self):
        """Show detailed component status dialog with diagnostics"""
        try:
            # Create status dialog window
            dialog = tk.Toplevel(self.root)
            dialog.title("System Component Status")
            dialog.geometry("600x400")
            dialog.configure(bg=ModernTheme.CARD_BG)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
            y = (dialog.winfo_screenheight() // 2) - (400 // 2)
            dialog.geometry(f"600x400+{x}+{y}")
            
            # Create scrollable frame
            canvas = tk.Canvas(dialog, bg=ModernTheme.CARD_BG)
            scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=ModernTheme.CARD_BG)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Title
            title_label = tk.Label(scrollable_frame, text="System Component Diagnostics", 
                                 bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                                 font=(ModernTheme.FONT_FAMILY, 14, 'bold'))
            title_label.pack(pady=10)
            
            # Get current component status
            components_status = self._get_detailed_component_status()
            
            # Display each component status
            for component_name, status_info in components_status.items():
                # Component frame
                comp_frame = tk.LabelFrame(scrollable_frame, text=component_name,
                                          bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                                          font=(ModernTheme.FONT_FAMILY, 10, 'bold'))
                comp_frame.pack(fill="x", padx=10, pady=5)
                
                # Status
                status_text = f"Status: {status_info.get('status', 'Unknown')}"
                tk.Label(comp_frame, text=status_text, bg=ModernTheme.CARD_BG,
                        fg=status_info.get('color', ModernTheme.TEXT_PRIMARY),
                        font=(ModernTheme.FONT_FAMILY, 9)).pack(anchor="w", padx=5, pady=2)
                
                # Details
                if 'details' in status_info:
                    for detail in status_info['details']:
                        tk.Label(comp_frame, text=f"• {detail}", bg=ModernTheme.CARD_BG,
                               fg=ModernTheme.TEXT_SECONDARY,
                               font=(ModernTheme.FONT_FAMILY, 8)).pack(anchor="w", padx=15, pady=1)
                
                # Suggestions
                if 'suggestions' in status_info and status_info['suggestions']:
                    tk.Label(comp_frame, text="Suggestions:", bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.ACCENT_BLUE,
                           font=(ModernTheme.FONT_FAMILY, 8, 'bold')).pack(anchor="w", padx=5, pady=(5,0))
                    for suggestion in status_info['suggestions'][:3]:  # Show max 3 suggestions
                        tk.Label(comp_frame, text=f"→ {suggestion}", bg=ModernTheme.CARD_BG,
                               fg=ModernTheme.TEXT_SECONDARY,
                               font=(ModernTheme.FONT_FAMILY, 8)).pack(anchor="w", padx=15, pady=1)
            
            # Buttons frame
            button_frame = tk.Frame(dialog, bg=ModernTheme.CARD_BG)
            button_frame.pack(fill="x", pady=10)
            
            # Refresh button
            refresh_btn = tk.Button(button_frame, text="Refresh Status",
                                   command=lambda: self._refresh_component_status_dialog(dialog),
                                   bg=ModernTheme.ACCENT_BLUE, fg="white",
                                   font=(ModernTheme.FONT_FAMILY, 9))
            refresh_btn.pack(side="left", padx=10)
            
            # Close button
            close_btn = tk.Button(button_frame, text="Close",
                                 command=dialog.destroy,
                                 bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                                 font=(ModernTheme.FONT_FAMILY, 9))
            close_btn.pack(side="right", padx=10)
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
        except Exception as e:
            print(f"[ERROR] Failed to show component status dialog: {e}")
            if hasattr(self, 'toast_system') and self.toast_system:
                self.toast_system.show_toast("Failed to show component status", "error")

    def _get_detailed_component_status(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed status information for all components"""
        status = {}
        
        try:
            # Database Component
            db_status = {"status": "🔴 Disconnected", "color": ModernTheme.ERROR, "details": [], "suggestions": []}
            if hasattr(self, 'server') and self.server and hasattr(self.server, 'db_manager'):
                try:
                    if self.server.db_manager and hasattr(self.server.db_manager, 'execute_query'):
                        test_result = self.server.db_manager.execute_query("SELECT 1", fetch=True)
                        if test_result:
                            db_status.update({
                                "status": "🟢 Connected", 
                                "color": ModernTheme.SUCCESS,
                                "details": ["Database connection active", "Queries executing normally"],
                                "suggestions": []
                            })
                        else:
                            db_status.update({
                                "status": "🟡 Limited", 
                                "color": ModernTheme.WARNING,
                                "details": ["Database accessible but queries failing"],
                                "suggestions": ["Check database integrity", "Restart database connection"]
                            })
                except Exception as e:
                    db_status.update({
                        "details": [f"Error: {str(e)[:50]}..."],
                        "suggestions": ["Check database file permissions", "Verify database file exists", "Restart application"]
                    })
            else:
                db_status["details"] = ["Database manager not initialized"]
                db_status["suggestions"] = ["Restart application", "Check configuration"]
            status["Database"] = db_status
            
            # Network Component
            net_status = {"status": "🔴 Offline", "color": ModernTheme.ERROR, "details": [], "suggestions": []}
            if hasattr(self, 'server') and self.server:
                if self.server.running:
                    try:
                        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        test_socket.settimeout(1)
                        result = test_socket.connect_ex(('127.0.0.1', self.server.port))
                        test_socket.close()
                        
                        if result == 0:
                            net_status.update({
                                "status": "🟢 Online",
                                "color": ModernTheme.SUCCESS,
                                "details": [f"Server listening on port {self.server.port}", "Network connections active"],
                                "suggestions": []
                            })
                        else:
                            net_status.update({
                                "status": "🟡 Starting",
                                "color": ModernTheme.WARNING,
                                "details": [f"Port {self.server.port} not responding"],
                                "suggestions": ["Wait for server startup", "Check port availability"]
                            })
                    except Exception as e:
                        net_status.update({
                            "details": [f"Network test failed: {str(e)[:40]}..."],
                            "suggestions": ["Check firewall settings", "Verify network configuration"]
                        })
                else:
                    net_status.update({
                        "details": ["Server not running"],
                        "suggestions": ["Start the server", "Check server configuration"]
                    })
            status["Network"] = net_status
            
            # System Resources Component
            sys_status = {"status": "🟡 Monitoring", "color": ModernTheme.WARNING, "details": [], "suggestions": []}
            if SYSTEM_MONITOR_AVAILABLE:
                try:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory = psutil.virtual_memory()
                    
                    sys_status["details"] = [
                        f"CPU Usage: {cpu_percent:.1f}%",
                        f"Memory Usage: {memory.percent:.1f}%",
                        f"Available Memory: {memory.available / (1024**3):.1f} GB"
                    ]
                    
                    if cpu_percent < 80 and memory.percent < 85:
                        sys_status.update({
                            "status": "🟢 Healthy",
                            "color": ModernTheme.SUCCESS,
                            "suggestions": []
                        })
                    elif cpu_percent >= 90 or memory.percent >= 95:
                        sys_status.update({
                            "status": "🔴 Critical",
                            "color": ModernTheme.ERROR,
                            "suggestions": ["Close unnecessary applications", "Free up system resources", "Restart system"]
                        })
                    else:
                        sys_status["suggestions"] = ["Monitor resource usage", "Close unused applications"]
                        
                except Exception as e:
                    sys_status.update({
                        "details": [f"Monitoring error: {str(e)[:40]}..."],
                        "suggestions": ["Install psutil package", "Check system permissions"]
                    })
            else:
                sys_status.update({
                    "status": "🔴 No Monitor",
                    "color": ModernTheme.ERROR,
                    "details": ["psutil package not available"],
                    "suggestions": ["Install psutil: pip install psutil", "Restart application after install"]
                })
            status["System Resources"] = sys_status
            
            # GUI Component (always healthy if we're here)
            status["GUI Integration"] = {
                "status": "🟢 Active",
                "color": ModernTheme.SUCCESS,
                "details": ["GUI interface running", "User interaction available"],
                "suggestions": []
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get component status: {e}")
            
        return status

    def _refresh_component_status_dialog(self, dialog):
        """Refresh the component status dialog"""
        try:
            # Close and recreate the dialog
            dialog.destroy()
            self.show_component_status_dialog()
        except Exception as e:
            print(f"[ERROR] Failed to refresh component status dialog: {e}")

    def _run_system_diagnostics(self):
        """Run comprehensive system diagnostics and show results"""
        try:
            # Run diagnostics
            diagnostics_results = []
            
            # Test 1: Database Connection
            diagnostics_results.append("🔍 Testing Database Connection...")
            try:
                if hasattr(self, 'server') and self.server and hasattr(self.server, 'db_manager'):
                    if self.server.db_manager:
                        test_result = self.server.db_manager.execute_query("SELECT COUNT(*) as count FROM sqlite_master WHERE type='table'", fetch=True)
                        if test_result:
                            table_count = test_result[0]['count'] if test_result else 0
                            diagnostics_results.append(f"✅ Database: {table_count} tables found")
                        else:
                            diagnostics_results.append("❌ Database: Query failed")
                    else:
                        diagnostics_results.append("❌ Database: Manager not available")
                else:
                    diagnostics_results.append("❌ Database: Server not available")
            except Exception as e:
                diagnostics_results.append(f"❌ Database: Error - {str(e)[:50]}")
            
            # Test 2: Network Connectivity
            diagnostics_results.append("🔍 Testing Network Server...")
            try:
                if hasattr(self, 'server') and self.server and self.server.running:
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.settimeout(2)
                    result = test_socket.connect_ex(('127.0.0.1', self.server.port))
                    test_socket.close()
                    
                    if result == 0:
                        diagnostics_results.append(f"✅ Network: Port {self.server.port} accessible")
                    else:
                        diagnostics_results.append(f"❌ Network: Port {self.server.port} not responding")
                else:
                    diagnostics_results.append("❌ Network: Server not running")
            except Exception as e:
                diagnostics_results.append(f"❌ Network: Error - {str(e)[:50]}")
            
            # Test 3: System Resources
            diagnostics_results.append("🔍 Testing System Resources...")
            if SYSTEM_MONITOR_AVAILABLE:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('.')
                    
                    diagnostics_results.append(f"✅ CPU: {cpu_percent:.1f}% usage")
                    diagnostics_results.append(f"✅ Memory: {memory.percent:.1f}% used ({memory.available/(1024**3):.1f}GB free)")
                    diagnostics_results.append(f"✅ Disk: {disk.percent:.1f}% used ({disk.free/(1024**3):.1f}GB free)")
                    
                    # Check for issues
                    if cpu_percent > 90:
                        diagnostics_results.append("⚠️ Warning: High CPU usage detected")
                    if memory.percent > 90:
                        diagnostics_results.append("⚠️ Warning: High memory usage detected")
                    if disk.percent > 90:
                        diagnostics_results.append("⚠️ Warning: Low disk space detected")
                        
                except Exception as e:
                    diagnostics_results.append(f"❌ System: Error - {str(e)[:50]}")
            else:
                diagnostics_results.append("❌ System: psutil not available")
            
            # Test 4: File Permissions
            diagnostics_results.append("🔍 Testing File Permissions...")
            try:
                # Test write permissions in current directory
                test_file = "diagnostic_test.tmp"
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                diagnostics_results.append("✅ File System: Write permissions OK")
            except Exception as e:
                diagnostics_results.append(f"❌ File System: {str(e)[:50]}")
            
            # Test 5: GUI Components
            diagnostics_results.append("🔍 Testing GUI Components...")
            try:
                widget_count = 0
                if hasattr(self, 'root') and self.root:
                    widget_count = len(self.root.winfo_children())
                    diagnostics_results.append(f"✅ GUI: {widget_count} widgets loaded")
                else:
                    diagnostics_results.append("❌ GUI: Root window not available")
            except Exception as e:
                diagnostics_results.append(f"❌ GUI: Error - {str(e)[:50]}")
            
            # Create results dialog
            self._show_diagnostics_results(diagnostics_results)
            
        except Exception as e:
            print(f"[ERROR] System diagnostics failed: {e}")
            if hasattr(self, 'toast_system') and self.toast_system:
                self.toast_system.show_toast(f"Diagnostics failed: {e}", "error")

    def _show_diagnostics_results(self, results: List[str]):
        """Show system diagnostics results in a dialog"""
        try:
            # Create results dialog window
            dialog = tk.Toplevel(self.root)
            dialog.title("System Diagnostics Results")
            dialog.geometry("500x600")
            dialog.configure(bg=ModernTheme.CARD_BG)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (250)
            y = (dialog.winfo_screenheight() // 2) - (300)
            dialog.geometry(f"500x600+{x}+{y}")
            
            # Title
            title_label = tk.Label(dialog, text="System Diagnostics Report", 
                                 bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                                 font=(ModernTheme.FONT_FAMILY, 14, 'bold'))
            title_label.pack(pady=10)
            
            # Results text area with scrollbar
            text_frame = tk.Frame(dialog, bg=ModernTheme.CARD_BG)
            text_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                                font=(ModernTheme.FONT_FAMILY, 9), wrap="word")
            scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            # Add results to text widget
            for result in results:
                text_widget.insert(tk.END, result + "\n")
            
            text_widget.config(state="disabled")  # Make read-only
            
            # Pack text widget and scrollbar
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Buttons frame
            button_frame = tk.Frame(dialog, bg=ModernTheme.CARD_BG)
            button_frame.pack(fill="x", pady=10)
            
            # Copy to clipboard button
            copy_btn = tk.Button(button_frame, text="Copy to Clipboard",
                               command=lambda: self._copy_diagnostics_to_clipboard(results),
                               bg=ModernTheme.ACCENT_BLUE, fg="white",
                               font=(ModernTheme.FONT_FAMILY, 9))
            copy_btn.pack(side="left", padx=10)
            
            # Close button
            close_btn = tk.Button(button_frame, text="Close",
                                 command=dialog.destroy,
                                 bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_PRIMARY,
                                 font=(ModernTheme.FONT_FAMILY, 9))
            close_btn.pack(side="right", padx=10)
            
        except Exception as e:
            print(f"[ERROR] Failed to show diagnostics results: {e}")

    def _copy_diagnostics_to_clipboard(self, results: List[str]):
        """Copy diagnostics results to clipboard"""
        try:
            report_text = "System Diagnostics Report\n" + "="*30 + "\n\n"
            report_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            report_text += "\n".join(results)
            
            self.root.clipboard_clear()
            self.root.clipboard_append(report_text)
            self.root.update()  # Required for clipboard update
            
            if hasattr(self, 'toast_system') and self.toast_system:
                self.toast_system.show_toast("Diagnostics copied to clipboard", "success")
                
        except Exception as e:
            print(f"[ERROR] Failed to copy to clipboard: {e}")
            if hasattr(self, 'toast_system') and self.toast_system:
                self.toast_system.show_toast("Failed to copy to clipboard", "error")

    def _update_performance_metrics(self, performance_data: Optional[dict] = None):
        """Update performance metrics on the dashboard."""
        if not SYSTEM_MONITOR_AVAILABLE:
            # Disable performance monitoring entirely when psutil is not available
            if 'cpu_usage' in self.status_labels:
                self.status_labels['cpu_usage'].config(text="N/A")
            if 'memory_usage' in self.status_labels:
                self.status_labels['memory_usage'].config(text="N/A")
            if 'disk_usage' in self.status_labels:
                self.status_labels['disk_usage'].config(text="N/A")
            if 'network_activity' in self.status_labels:
                self.status_labels['network_activity'].config(text="Disabled")

            # Disable progress bars
            for key in ['cpu', 'memory', 'disk']:
                if key in self.advanced_progress_bars:
                    self.advanced_progress_bars[key].set_progress(0, animated=False)
            return

        try:
            # Get real system stats with comprehensive error handling and validation
            if not SYSTEM_MONITOR_AVAILABLE or psutil is None:
                # Provide simulated fallback data when psutil unavailable
                cpu_percent = self._get_fallback_cpu_usage()
                mem_percent = self._get_fallback_memory_usage()
                disk_usage_percent = None
                network_status = "Simulated"
            else:
                # Get real system metrics with bounds checking
                cpu_percent = psutil.cpu_percent(interval=None)
                # Validate CPU percentage bounds (should be 0-100)
                cpu_percent = max(0.0, min(100.0, cpu_percent)) if cpu_percent is not None else 0.0
                
                memory_info = psutil.virtual_memory()
                mem_percent = memory_info.percent if memory_info else 0.0
                # Validate memory percentage bounds
                mem_percent = max(0.0, min(100.0, mem_percent)) if mem_percent is not None else 0.0

                # Enhanced disk usage monitoring with multiple fallbacks
                disk_usage_percent = self._get_disk_usage_with_fallbacks()

            # Enhanced network activity monitoring with proper rate calculation
            network_status = self._get_enhanced_network_activity()

        except Exception as e:
            print(f"Critical error getting system metrics: {e}")
            # If psutil fails completely, disable monitoring
            if 'cpu_usage' in self.status_labels:
                self.status_labels['cpu_usage'].config(text="Error")
            if 'memory_usage' in self.status_labels:
                self.status_labels['memory_usage'].config(text="Error")
            if 'disk_usage' in self.status_labels:
                self.status_labels['disk_usage'].config(text="Error")
            if 'network_activity' in self.status_labels:
                self.status_labels['network_activity'].config(text="Error")
            return

        # Update labels with real data only
        if 'cpu_usage' in self.status_labels:
            self.status_labels['cpu_usage'].config(text=f"{cpu_percent:.1f}%")
        if 'memory_usage' in self.status_labels:
            self.status_labels['memory_usage'].config(text=f"{mem_percent:.1f}%")
        if 'disk_usage' in self.status_labels and disk_usage_percent is not None:
            self.status_labels['disk_usage'].config(text=f"{disk_usage_percent:.1f}%")
        elif 'disk_usage' in self.status_labels:
            self.status_labels['disk_usage'].config(text="N/A")
        if 'network_activity' in self.status_labels:
            self.status_labels['network_activity'].config(text=network_status)

        # Update progress bars with real data only
        if 'cpu' in self.advanced_progress_bars:
            self.advanced_progress_bars['cpu'].set_progress(cpu_percent)
        if 'memory' in self.advanced_progress_bars:
            self.advanced_progress_bars['memory'].set_progress(mem_percent)
        if 'disk' in self.advanced_progress_bars and disk_usage_percent is not None:
            self.advanced_progress_bars['disk'].set_progress(disk_usage_percent)

        # Update performance data for charts with real data only
        now = datetime.now()
        self.performance_data['timestamps'].append(now)
        self.performance_data['cpu_usage'].append(cpu_percent)
        self.performance_data['memory_usage'].append(mem_percent)

        # Update analytics charts if the tab is active
        if self.current_tab == "analytics":
            self._update_analytics_charts()

    def _get_fallback_cpu_usage(self) -> float:
        """Provide simulated CPU usage when psutil unavailable"""
        # Simple simulation based on server activity
        if hasattr(self, 'server') and self.server and hasattr(self.server, 'clients'):
            try:
                with self.server.clients_lock:
                    client_count = len(self.server.clients)
                # Simulate CPU usage based on client activity (5-15% base + 2% per client)
                simulated_cpu = min(15 + (client_count * 2), 100)
                return float(simulated_cpu)
            except:
                pass
        # Default fallback
        return 5.0

    def _get_fallback_memory_usage(self) -> float:
        """Provide simulated memory usage when psutil unavailable"""
        # Simple simulation - assume moderate memory usage
        import sys
        try:
            # Try to get rough memory usage from Python process
            if hasattr(sys, 'getsizeof'):
                # Very rough estimate based on object count
                return min(30.0 + (len(gc.get_objects()) / 10000), 80.0)
        except:
            pass
        return 25.0  # Default simulated memory usage

    def _get_disk_usage_with_fallbacks(self) -> Optional[float]:
        """Get disk usage with multiple fallback strategies"""
        if not SYSTEM_MONITOR_AVAILABLE or not psutil:
            return None
        
        # Strategy 1: Script directory
        try:
            script_path = os.path.abspath(sys.argv[0])
            disk_path = os.path.splitdrive(script_path)[0]
            if not disk_path:  # Unix-like systems
                disk_path = '/'
            disk_usage = psutil.disk_usage(disk_path)
            return max(0.0, min(100.0, disk_usage.percent))
        except Exception as e1:
            print(f"[DEBUG] Script path disk usage failed: {e1}")
        
        # Strategy 2: Current working directory
        try:
            cwd_usage = psutil.disk_usage(os.getcwd())
            return max(0.0, min(100.0, cwd_usage.percent))
        except Exception as e2:
            print(f"[DEBUG] CWD disk usage failed: {e2}")
        
        # Strategy 3: Home directory
        try:
            home_usage = psutil.disk_usage(os.path.expanduser('~'))
            return max(0.0, min(100.0, home_usage.percent))
        except Exception as e3:
            print(f"[DEBUG] Home dir disk usage failed: {e3}")
        
        # Strategy 4: Root/C: drive
        try:
            root_path = 'C:\\' if os.name == 'nt' else '/'
            root_usage = psutil.disk_usage(root_path)
            return max(0.0, min(100.0, root_usage.percent))
        except Exception as e4:
            print(f"[DEBUG] Root disk usage failed: {e4}")
        
        return None  # All strategies failed

    def _get_enhanced_network_activity(self) -> str:
        """Enhanced network activity tracking with proper rate calculation and time windows"""
        if not SYSTEM_MONITOR_AVAILABLE or not psutil:
            return "Simulated"
        
        try:
            current_time = time.time()
            network_stats = psutil.net_io_counters()
            
            if not network_stats:
                return "No Interface"
            
            total_bytes = network_stats.bytes_sent + network_stats.bytes_recv
            
            # Initialize tracking if not present
            if not hasattr(self, '_network_tracking'):
                self._network_tracking = {
                    'last_bytes': total_bytes,
                    'last_time': current_time,
                    'rate_history': deque(maxlen=10),  # Keep last 10 measurements
                    'avg_window': 5.0  # 5-second averaging window
                }
                return "Initializing..."
            
            # Calculate time and bytes difference
            time_diff = current_time - self._network_tracking['last_time']
            
            # Only update if enough time has passed (avoid noise from rapid updates)
            if time_diff >= 1.0:  # Update every second minimum
                bytes_diff = total_bytes - self._network_tracking['last_bytes']
                
                # Validate bytes difference (handle counter resets)
                if bytes_diff < 0:
                    # Counter reset detected, skip this measurement
                    self._network_tracking['last_bytes'] = total_bytes
                    self._network_tracking['last_time'] = current_time
                    return "Counter Reset"
                
                # Calculate rate in bytes per second
                bytes_per_second = bytes_diff / time_diff
                
                # Add to history for smoothing
                self._network_tracking['rate_history'].append(bytes_per_second)
                
                # Update tracking
                self._network_tracking['last_bytes'] = total_bytes
                self._network_tracking['last_time'] = current_time
                
                # Calculate smoothed average rate
                if len(self._network_tracking['rate_history']) >= 3:
                    avg_rate = sum(self._network_tracking['rate_history']) / len(self._network_tracking['rate_history'])
                else:
                    avg_rate = bytes_per_second
                
                # Format rate for display with intelligent units
                return self._format_network_rate(avg_rate)
            
            else:
                # Not enough time passed, return last known status
                if hasattr(self, '_last_network_status'):
                    return self._last_network_status
                return "Monitoring..."
        
        except Exception as e:
            print(f"[DEBUG] Enhanced network activity error: {e}")
            return "Error"
    
    def _format_network_rate(self, bytes_per_second: float) -> str:
        """Format network rate with appropriate units and activity level indication"""
        # Store for quick access
        self._last_network_status = ""
        
        if bytes_per_second < 100:  # Less than 100 B/s
            self._last_network_status = "Idle"
        elif bytes_per_second < 1024:  # Less than 1 KB/s
            self._last_network_status = f"Low ({int(bytes_per_second)} B/s)"
        elif bytes_per_second < 1024 * 1024:  # Less than 1 MB/s
            kb_rate = bytes_per_second / 1024
            self._last_network_status = f"Active ({kb_rate:.1f} KB/s)"
        else:  # 1 MB/s or higher
            mb_rate = bytes_per_second / (1024 * 1024)
            self._last_network_status = f"High ({mb_rate:.1f} MB/s)"
        
        return self._last_network_status

    def _update_analytics_charts(self):
        """Update the charts on the analytics tab with the latest data."""
        if not CHARTS_AVAILABLE:
            return

        # Performance Chart (CPU and Memory over time)
        if self.performance_chart:
            chart_data = {
                'CPU Usage (%)': (list(self.performance_data['timestamps']), list(self.performance_data['cpu_usage'])),
                'Memory Usage (%)': (list(self.performance_data['timestamps']), list(self.performance_data['memory_usage']))
            }
            self.performance_chart.update_data(chart_data, title="System Performance Over Time", xlabel="Time", ylabel="Usage (%)")

        # Transfer Volume Chart
        if self.transfer_chart and self.server and hasattr(self.server, 'db_manager') and self.server.db_manager:
            try:
                total_bytes = self.server.db_manager.get_total_bytes_transferred()
                # This is a single value, so we'll display it as a bar chart.
                chart_data = {
                    'Total MB Transferred': total_bytes / (1024*1024)
                }
                self.transfer_chart.update_data(chart_data, title="Total Verified Transfer Volume")
            except Exception as e:
                print(f"[DEBUG] Error updating transfer volume chart: {e}")
                # Show fallback data
                chart_data = {'Total MB Transferred': 0}
                self.transfer_chart.update_data(chart_data, title="Total Verified Transfer Volume (Error)")

        # Client Activity Chart
        if self.client_chart:
            online_clients = self.status.clients_connected
            total_clients = self.status.total_clients
            offline_clients = total_clients - online_clients

            chart_data = {
                'Online': online_clients,
                'Offline': offline_clients
            }
            self.client_chart.update_data(chart_data, title="Client Status")

    def _refresh_client_table(self):
        """Refresh the client table with data from the database."""
        if not self.client_table:
            if self.toast_system:
                self.toast_system.show_toast("Client table not initialized.", "error")
            return
        
        if not self.server:
            if self.toast_system:
                self.toast_system.show_toast("Server instance not available.", "error")
            self._add_activity_log("❌ Cannot refresh client table: Server instance not available")
            return
            
        if not hasattr(self.server, 'db_manager') or not self.server.db_manager:
            if self.toast_system:
                self.toast_system.show_toast("Database manager not available.", "error")
            self._add_activity_log("❌ Cannot refresh client table: Database manager not available")
            return
        
        try:
            clients = self.server.db_manager.get_all_clients()
            
            # Get online status from the server's in-memory client list (with proper locking)
            if hasattr(self.server, 'clients_lock'):
                with self.server.clients_lock:
                    online_client_ids = list(self.server.clients.keys())
            else:
                # Fallback if no lock available (should not happen in production)
                online_client_ids = list(self.server.clients.keys())

            table_data = []
            for client in clients:
                client_id_bytes = bytes.fromhex(client['id'])
                status = "🟢 Online" if client_id_bytes in online_client_ids else "⚫ Offline"
                
                table_data.append({
                        'name': client['name'],
                        'id': client['id'],
                        'status': status,
                        'last_seen': client['last_seen'],
                        'files': 'N/A' # Placeholder
                    })
                
                self.client_table.set_data(table_data)
                self._add_activity_log("Client table refreshed.")
            except Exception as e:
                error_msg = f"Database error refreshing client table: {str(e)}"
                self._add_activity_log(f"❌ {error_msg}")
                
                # Show enhanced error with specific component status
                error_details = {'table': 'clients', 'operation': 'refresh', 'error_type': type(e).__name__}
                self.show_enhanced_error(f"Failed to refresh clients: Database connection issue", "Database", error_details)
                
                # Update status to show error state
                if 'error' in self.status_labels:
                    self.status_labels['error'].config(text="⚠️ Database Error", fg=ModernTheme.ERROR)
                
                # Clear table to avoid showing stale data
                if self.client_table:
                    self.client_table.set_data([])
                
                # Log detailed error for debugging
                print(f"[DEBUG] Client table refresh error: {e}")
                import traceback
                traceback.print_exc()

    def _on_client_selected(self, selected_item):
        """Handle client selection in the table."""
        if selected_item:
            self._add_activity_log(f"Client selected: {selected_item.get('name')}")

    def _show_client_details(self):
        """Show details for the selected client."""
        if self.client_table:
            selected = self.client_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No client selected", "warning")
                return
            
            # For now, just show a message box with the client info
            client_info = selected[0]
            messagebox.showinfo("Client Details", json.dumps(client_info, indent=2))
        else:
            if self.toast_system:
                self.toast_system.show_toast("Client table not initialized.", "error")

    def _disconnect_client(self):
        """Disconnect a selected client."""
        if self.client_table:
            selected = self.client_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No client selected", "warning")
                return
            
            client_id_hex = selected[0].get('id')
            client_id_bytes = bytes.fromhex(client_id_hex)

            if self.server and self.server.network_server:
                if self.server.network_server.disconnect_client(client_id_bytes):
                    if self.toast_system:
                        self.toast_system.show_toast("Client disconnected successfully.", "success")
                    self._add_activity_log(f"Disconnected client: {client_id_hex}")
                    self._refresh_client_table()
                else:
                    if self.toast_system:
                        self.toast_system.show_toast("Failed to disconnect client (might be offline).", "error")
            else:
                if self.toast_system:
                    self.toast_system.show_toast("Server is not running.", "error")
        else:
            if self.toast_system:
                self.toast_system.show_toast("Client table not initialized.", "error")

    def _refresh_file_table(self):
        """Refresh the file table with data from the database."""
        if not self.file_table:
            if self.toast_system:
                self.toast_system.show_toast("File table not initialized.", "error")
            return
        
        if not self.server:
            if self.toast_system:
                self.toast_system.show_toast("Server instance not available.", "error")
            self._add_activity_log("❌ Cannot refresh file table: Server instance not available")
            return
            
        if not hasattr(self.server, 'db_manager') or not self.server.db_manager:
            if self.toast_system:
                self.toast_system.show_toast("Database manager not available.", "error")
            self._add_activity_log("❌ Cannot refresh file table: Database manager not available")
            return
        
        try:
            files = self.server.db_manager.get_all_files()
            
            table_data = []
            for f in files:
                size_in_mb = f.get('size', 0) / (1024 * 1024) if f.get('size') else 0
                table_data.append({
                        'filename': f['filename'],
                        'client': f['client'],
                        'size': f"{size_in_mb:.2f} MB" if f.get('size') is not None else 'N/A',
                        'date': f.get('date', 'N/A'),
                        'verified': "[OK] Yes" if f['verified'] else "[NO] No",
                        'path': f['path']
                    })
                
                self.file_table.set_data(table_data)
                self._add_activity_log("File table refreshed.")
            except Exception as e:
                error_msg = f"Database error refreshing file table: {str(e)}"
                self._add_activity_log(f"❌ {error_msg}")
                
                # Show enhanced error with specific component status
                error_details = {'table': 'files', 'operation': 'refresh', 'error_type': type(e).__name__}
                
                if "permission" in str(e).lower():
                    self.show_enhanced_error("Database permission error. Check file access rights.", "Database", error_details)
                elif "locked" in str(e).lower():
                    self.show_enhanced_error("Database is locked. Another process may be using it.", "Database", error_details)
                elif "connection" in str(e).lower():
                    self.show_enhanced_error("Database connection lost. Attempting to reconnect...", "Database", error_details)
                else:
                    self.show_enhanced_error(f"Database error refreshing files: {str(e)}", "Database", error_details)
                
                # Update status to show error state
                if 'error' in self.status_labels:
                    self.status_labels['error'].config(text="⚠️ File DB Error", fg=ModernTheme.ERROR)
                
                # Clear table to avoid showing stale data
                if self.file_table:
                    self.file_table.set_data([])
                
                # Log detailed error for debugging
                print(f"[DEBUG] File table refresh error: {e}")
                import traceback
                traceback.print_exc()
                
                # Attempt recovery for certain error types
                if "locked" in str(e).lower():
                    self._add_activity_log("🔄 Attempting database recovery in 5 seconds...")
                    # Schedule retry after delay
                    if self.root:
                        self.root.after(5000, self._refresh_file_table)
        else:
            if self.toast_system:
                self.toast_system.show_toast("File table not initialized.", "error")

    def _on_file_selected(self, selected_item):
        """Handle file selection in the table."""
        if selected_item:
            self._add_activity_log(f"File selected: {selected_item.get('filename')}")

    def _show_file_details(self):
        """Show details for the selected file."""
        if self.file_table:
            selected = self.file_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No file selected", "warning")
                return
            
            file_info = selected[0]
            messagebox.showinfo("File Details", json.dumps(file_info, indent=2))
        else:
            if self.toast_system:
                self.toast_system.show_toast("File table not initialized.", "error")

    def _view_file_content(self):
        """View the content of the selected file."""
        if self.file_table:
            selected = self.file_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No file selected", "warning")
                return

            file_info = selected[0]
            file_path = file_info.get('path')

            if not os.path.exists(file_path):
                if self.toast_system:
                    self.toast_system.show_toast(f"File not found on disk: {file_path}", "error")
                return

            try:
                os.startfile(file_path)
            except AttributeError:
                # os.startfile is only available on Windows. For other platforms, we can use other commands.
                import subprocess
                if sys.platform == "darwin": # macOS
                    subprocess.call(["open", file_path])
                elif sys.platform == "linux2": # Linux
                    subprocess.call(["xdg-open", file_path])
                else:
                    if self.toast_system:
                        self.toast_system.show_toast("Viewing files is not supported on this platform.", "error")
            except Exception as e:
                if self.toast_system:
                    self.toast_system.show_toast(f"Error opening file: {e}", "error")
                self._add_activity_log(f"Error opening file: {e}")
        else:
            if self.toast_system:
                self.toast_system.show_toast("File table not initialized.", "error")

    def _verify_file(self):
        """Verify the selected file."""
        if self.file_table:
            selected = self.file_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No file selected", "warning")
                return

            file_info = selected[0]
            filename = file_info.get('filename')
            client_name = file_info.get('client')

            if self.server and self.server.db_manager:
                client_id_bytes = self.server.clients_by_name.get(client_name)
                if not client_id_bytes:
                    if self.toast_system:
                        self.toast_system.show_toast(f"Could not find client ID for {client_name}", "error")
                    return
                client_id_hex = client_id_bytes.hex()

                db_file_info = self.server.db_manager.get_file_info(client_id_hex, filename)
                if not db_file_info:
                    if self.toast_system:
                        self.toast_system.show_toast(f"Could not find file info for {filename}", "error")
                    return

                file_path = db_file_info.get('path')
                stored_crc = db_file_info.get('crc')

                if not os.path.exists(file_path):
                    if self.toast_system:
                        self.toast_system.show_toast(f"File not found on disk: {file_path}", "error")
                    return

                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # Since the CRC calculation is in file_transfer, we need to access it from there.
                # This is not ideal, but it's the quickest way to implement this feature.
                from file_transfer import FileTransferManager
                calculated_crc = FileTransferManager(self.server)._calculate_crc(file_data)

                if stored_crc == calculated_crc:
                    if self.toast_system:
                        self.toast_system.show_toast("File verification successful!", "success")
                    # Update the database to mark the file as verified
                    self.server.db_manager.save_file_info_to_db(client_id_bytes, filename, file_path, True, len(file_data), db_file_info.get('date'), stored_crc)
                    self._refresh_file_table()
                else:
                    if self.toast_system:
                        self.toast_system.show_toast(f"File verification failed!\n\nStored CRC: {stored_crc}\nCalculated CRC: {calculated_crc}", "error")
            else:
                if self.toast_system:
                    self.toast_system.show_toast("Server is not running.", "error")
        else:
            if self.toast_system:
                self.toast_system.show_toast("File table not initialized.", "error")

    def _delete_file(self):
        """Delete the selected file."""
        if self.file_table:
            selected = self.file_table.get_selected_items()
            if not selected:
                if self.toast_system:
                    self.toast_system.show_toast("No file selected", "warning")
                return

            file_info = selected[0]
            filename = file_info.get('filename')
            client_name = file_info.get('client')

            if not messagebox.askyesno("Delete File", f"Are you sure you want to delete the file '\n{filename}' for client '\n{client_name}'?\n\nThis action cannot be undone."):
                return

            if self.server and self.server.db_manager:
                # We need the client ID to delete the file. We can get it from the client name.
                client_id_bytes = self.server.clients_by_name.get(client_name)
                if not client_id_bytes:
                    if self.toast_system:
                        self.toast_system.show_toast(f"Could not find client ID for {client_name}", "error")
                    return

                client_id_hex = client_id_bytes.hex()

                if self.server.db_manager.delete_file(client_id_hex, filename):
                    if self.toast_system:
                        self.toast_system.show_toast(f"File '{filename}' deleted successfully.", "success")
                    self._add_activity_log(f"Deleted file: {filename}")
                    self._refresh_file_table()
                else:
                    if self.toast_system:
                        self.toast_system.show_toast(f"Failed to delete file '{filename}'.", "error")
            else:
                if self.toast_system:
                    self.toast_system.show_toast("Server is not running.", "error")
        else:
            if self.toast_system:
                self.toast_system.show_toast("File table not initialized.", "error")

    def update_client_stats(self, stats_data: dict):
        """Update client statistics"""
        if not self.gui_enabled:
            return
        if 'connected' in self.status_labels:
            self.status_labels['connected'].config(text=str(stats_data.get('connected', 0)))
        if 'total' in self.status_labels:
            self.status_labels['total'].config(text=str(stats_data.get('total', 0)))
        if 'active_transfers' in self.status_labels:
            self.status_labels['active_transfers'].config(text=str(stats_data.get('active_transfers', 0)))

    def update_transfer_stats(self, stats_data: dict):
        """Update transfer statistics"""
        if not self.gui_enabled:
            return
        
        bytes_transferred = stats_data.get('bytes_transferred', 0)
        last_activity = stats_data.get('last_activity', 'None')
        
        # Update bytes transferred display
        if 'bytes' in self.status_labels:
            self.status_labels['bytes'].config(text=f"{bytes_transferred / 1024 / 1024:.2f} MB")
        
        # Update last activity display
        if 'activity' in self.status_labels:
            self.status_labels['activity'].config(text=last_activity)
        
        # Calculate and update transfer rate
        self._update_transfer_rate(bytes_transferred)

    def _update_transfer_rate(self, current_bytes_transferred: int):
        """Calculate and display real-time transfer rate"""
        current_time = time.time()
        
        # Initialize tracking variables if not present
        if not hasattr(self, '_last_transfer_bytes'):
            self._last_transfer_bytes = current_bytes_transferred
            self._last_transfer_time = current_time
            if 'transfer_rate' in self.status_labels:
                self.status_labels['transfer_rate'].config(text="0 KB/s")
            return
        
        # Calculate rate only if enough time has passed (avoid division by zero)
        time_diff = current_time - self._last_transfer_time
        if time_diff >= 1.0:  # Update rate every second minimum
            bytes_diff = current_bytes_transferred - self._last_transfer_bytes
            rate_bps = bytes_diff / time_diff
            
            # Format rate for display
            if rate_bps >= 1024 * 1024:  # MB/s
                rate_text = f"{rate_bps / (1024 * 1024):.1f} MB/s"
            elif rate_bps >= 1024:  # KB/s
                rate_text = f"{rate_bps / 1024:.1f} KB/s"
            else:  # B/s
                rate_text = f"{rate_bps:.0f} B/s"
            
            # Update display
            if 'transfer_rate' in self.status_labels:
                self.status_labels['transfer_rate'].config(text=rate_text)
            
            # Update tracking variables
            self._last_transfer_bytes = current_bytes_transferred
            self._last_transfer_time = current_time

    def update_maintenance_stats(self, stats_data: dict):
        """Update maintenance statistics"""
        if not self.gui_enabled:
            return
        if 'files_cleaned' in self.status_labels:
            self.status_labels['files_cleaned'].config(text=str(stats_data.get('files_cleaned', 0)))
        if 'partial_cleaned' in self.status_labels:
            self.status_labels['partial_cleaned'].config(text=str(stats_data.get('partial_files_cleaned', 0)))
        if 'clients_cleaned' in self.status_labels:
            self.status_labels['clients_cleaned'].config(text=str(stats_data.get('clients_cleaned', 0)))
        last_cleanup = stats_data.get('last_cleanup', 'Never')
        if last_cleanup != 'Never':
            last_cleanup = datetime.fromisoformat(last_cleanup).strftime('%Y-%m-%d %H:%M:%S')
        if 'last_cleanup' in self.status_labels:
            self.status_labels['last_cleanup'].config(text=last_cleanup)

    def update_server_status(self, running: bool, address: str, port: int):
        """Update server status display"""
        print(f"[DEBUG] update_server_status called: running={running}, address={address}, port={port}")

        if not self.gui_enabled:
            print("[DEBUG] GUI not enabled, returning")
            return

        # Update the status object
        self.status.running = running
        self.status.server_address = address
        self.status.port = port
        
        # Track server start time for accurate uptime calculation
        if running and not hasattr(self, '_server_start_time'):
            self._server_start_time = time.time()
            print(f"[DEBUG] Server start time recorded: {self._server_start_time}")
        elif not running:
            # Reset server start time when server stops
            if hasattr(self, '_server_start_time'):
                delattr(self, '_server_start_time')
            print("[DEBUG] Server start time cleared")

        # Update status labels
        if running:
            status_text = "🟢 Running"
            status_color = ModernTheme.SUCCESS
            header_text = "Server Online"
            indicator_status = "online"
        else:
            status_text = "🛑 Stopped"
            status_color = ModernTheme.ERROR
            header_text = "Server Offline"
            indicator_status = "offline"

        print(f"[DEBUG] Status text: {status_text}, Available status_labels keys: {list(self.status_labels.keys())}")

        # Update main status label
        if 'status' in self.status_labels:
            print("[DEBUG] Updating main status label")
            self.status_labels['status'].config(text=status_text, fg=status_color)
        else:
            print("[DEBUG] 'status' key not found in status_labels")

        # Update header status label
        if hasattr(self, 'header_status_label'):
            print("[DEBUG] Updating header status label")
            self.header_status_label.config(text=header_text)
        else:
            print("[DEBUG] header_status_label not found")

        # Update header status indicator
        if hasattr(self, 'header_status_indicator'):
            print("[DEBUG] Updating header status indicator")
            self.header_status_indicator.set_status(indicator_status)
        else:
            print("[DEBUG] header_status_indicator not found")

        # Update address and port labels if they exist
        if 'address' in self.status_labels:
            self.status_labels['address'].config(text=address)
        if 'port' in self.status_labels:
            self.status_labels['port'].config(text=str(port))

        # Update uptime display with real server uptime
        if 'uptime' in self.status_labels:
            if running and hasattr(self, '_server_start_time'):
                server_uptime = time.time() - self._server_start_time
                uptime_str = self._format_uptime(server_uptime)
                self.status_labels['uptime'].config(text=uptime_str)
            elif running:
                self.status_labels['uptime'].config(text="Starting...")
            else:
                self.status_labels['uptime'].config(text="0:00:00")

        print("[DEBUG] update_server_status completed")

    # --- Missing Method Implementations (Stubs) ---
    
    def _setup_modern_styles(self):
        """Setup modern styling for the GUI."""
        # Apply modern theme styles to the root window
        if self.root:
            self.root.configure(bg=ModernTheme.PRIMARY_BG)
    
    def _create_system_tray(self):
        """Create system tray icon if available."""
        # System tray functionality is optional
        if TRAY_AVAILABLE:
            # TODO: Implement system tray functionality
            pass
    
    def _schedule_updates(self):
        """Schedule periodic GUI updates."""
        try:
            # Process queued updates
            self._process_update_queue()

            # Update real-time elements
            self._update_clock()
            self._update_performance_metrics()
            self._update_health_monitoring()
            
            # Auto-refresh file table every 5 seconds when server is running
            # This ensures new files appear automatically without manual refresh
            if self.status.running and hasattr(self, '_last_file_refresh_time'):
                current_time = time.time()
                if current_time - self._last_file_refresh_time >= 5.0:  # 5 second interval
                    if hasattr(self, 'current_tab') and self.current_tab == 'files':
                        self._refresh_file_table()
                    self._last_file_refresh_time = current_time
            elif self.status.running and not hasattr(self, '_last_file_refresh_time'):
                # Initialize refresh timer
                self._last_file_refresh_time = time.time()

            # Update uptime if server is running (use real server start time)
            if self.status.running and hasattr(self, '_server_start_time'):
                current_time = time.time()
                server_uptime = current_time - self._server_start_time
                self.status.uptime_seconds = int(server_uptime)
                if 'uptime' in self.status_labels:
                    uptime_str = self._format_uptime(server_uptime)
                    self.status_labels['uptime'].config(text=uptime_str)

        except Exception as e:
            print(f"[DEBUG] Error in _schedule_updates: {e}")

        # Schedule next update
        if self.root:
            self.root.after(1000, self._schedule_updates)  # Update every second

    def _process_update_queue(self):
        """Process all pending updates from the queue with comprehensive error handling."""
        processed_count = 0
        error_count = 0
        max_per_cycle = 50  # Prevent UI blocking with too many updates
        
        try:
            while not self.update_queue.empty() and processed_count < max_per_cycle:
                try:
                    update_type, data = self.update_queue.get_nowait()
                    processed_count += 1

                    # Core update types
                    if update_type == "status":
                        self._handle_status_update(data)
                    elif update_type == "client_stats":
                        self._handle_client_stats_update(data)
                    elif update_type == "transfer_stats":
                        self._handle_transfer_stats_update(data)
                    elif update_type == "maintenance_stats":
                        self._handle_maintenance_stats_update(data)
                    elif update_type == "log":
                        self._handle_log_update(data)
                    
                    # Enhanced update types for real-time features
                    elif update_type == "file_complete":
                        self._handle_file_complete_update(data)
                    elif update_type == "client_connect":
                        self._handle_client_connect_update(data)
                    elif update_type == "client_disconnect":
                        self._handle_client_disconnect_update(data)
                    elif update_type == "error":
                        self._handle_error_update(data)
                    elif update_type == "refresh_tables":
                        self._handle_refresh_tables_update(data)
                    elif update_type == "performance":
                        self._handle_performance_update(data)
                    
                    else:
                        print(f"[DEBUG] Unknown update type: {update_type}")
                        error_count += 1

                except Exception as e:
                    error_count += 1
                    print(f"[DEBUG] Error processing queue item: {e}")
                    # Continue processing other items
                    continue
            
            # Log queue processing stats if there were issues
            if error_count > 0:
                print(f"[DEBUG] Queue processing: {processed_count} processed, {error_count} errors")
                
            # Check for queue overflow
            if self.update_queue.qsize() > 100:
                print(f"[WARNING] Update queue size: {self.update_queue.qsize()}")
                # Clear excess items to prevent memory issues
                excess_items = 0
                while self.update_queue.qsize() > 50 and excess_items < 50:
                    try:
                        self.update_queue.get_nowait()
                        excess_items += 1
                    except:
                        break
                if excess_items > 0:
                    print(f"[WARNING] Cleared {excess_items} excess queue items")

        except Exception as e:
            print(f"[DEBUG] Critical error in queue processing: {e}")
            import traceback
            traceback.print_exc()

    # Individual update handlers for better organization and error isolation
    def _handle_status_update(self, data):
        """Handle server status updates"""
        self.update_server_status(
            data.get('running', False),
            data.get('address', ''),
            data.get('port', 0)
        )

    def _handle_client_stats_update(self, data):
        """Handle client statistics updates"""
        self.update_client_stats(data)

    def _handle_transfer_stats_update(self, data):
        """Handle transfer statistics updates"""
        self.update_transfer_stats(data)

    def _handle_maintenance_stats_update(self, data):
        """Handle maintenance statistics updates"""
        self.update_maintenance_stats(data)

    def _handle_log_update(self, data):
        """Handle activity log updates"""
        if hasattr(self, 'activity_log'):
            self.activity_log.append({
                'timestamp': datetime.now().isoformat(),
                'message': str(data)
            })
            # Keep only last 100 log entries
            if len(self.activity_log) > 100:
                self.activity_log = self.activity_log[-100:]

    def _handle_file_complete_update(self, data):
        """Handle file completion events"""
        try:
            filename = data.get('filename', 'Unknown')
            client_name = data.get('client_name', 'Unknown')
            
            # Auto-refresh file table regardless of current tab
            self._refresh_file_table()
            
            # Show success notification
            if self.toast_system:
                self.toast_system.show_toast(f"File '{filename}' received from '{client_name}'", "success")
            
            # Update activity log
            self._add_activity_log(f"✅ File completed: {filename} from {client_name}")
            
        except Exception as e:
            print(f"[DEBUG] Error handling file complete update: {e}")

    def _handle_client_connect_update(self, data):
        """Handle client connection events"""
        try:
            client_name = data.get('client_name', 'Unknown')
            
            # Refresh client table to show new connection
            self._refresh_client_table()
            
            # Update activity log
            self._add_activity_log(f"🟢 Client connected: {client_name}")
            
        except Exception as e:
            print(f"[DEBUG] Error handling client connect update: {e}")

    def _handle_client_disconnect_update(self, data):
        """Handle client disconnection events"""
        try:
            client_name = data.get('client_name', 'Unknown')
            
            # Refresh client table to show disconnection
            self._refresh_client_table()
            
            # Update activity log
            self._add_activity_log(f"⚫ Client disconnected: {client_name}")
            
        except Exception as e:
            print(f"[DEBUG] Error handling client disconnect update: {e}")

    def _handle_error_update(self, data):
        """Handle error notifications"""
        try:
            error_msg = data.get('message', 'Unknown error')
            error_type = data.get('type', 'general')
            
            # Update error status display
            if 'error' in self.status_labels:
                self.status_labels['error'].config(text=f"❌ {error_type.title()}", fg=ModernTheme.ERROR)
            
            # Show error toast
            if self.toast_system:
                self.toast_system.show_toast(error_msg, "error")
            
            # Add to activity log
            self._add_activity_log(f"❌ Error: {error_msg}")
            
        except Exception as e:
            print(f"[DEBUG] Error handling error update: {e}")

    def _handle_refresh_tables_update(self, data):
        """Handle table refresh requests"""
        try:
            table_type = data.get('table', 'all')
            
            if table_type in ['clients', 'all']:
                self._refresh_client_table()
            if table_type in ['files', 'all']:
                self._refresh_file_table()
                
        except Exception as e:
            print(f"[DEBUG] Error handling refresh tables update: {e}")

    def _handle_performance_update(self, data):
        """Handle performance data updates"""
        try:
            # Update performance metrics with external data
            self._update_performance_metrics(data)
            
        except Exception as e:
            print(f"[DEBUG] Error handling performance update: {e}")

    def _on_window_close(self):
        """Handle window close event."""
        # Graceful shutdown when window is closed
        if self.root:
            self.root.destroy()

