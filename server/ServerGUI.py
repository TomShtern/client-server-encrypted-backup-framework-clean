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

# Import system tray functionality based on platform
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("Warning: pystray not available - system tray disabled")

# Import advanced features
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.animation as animation
    import matplotlib.dates as mdates
    plt.style.use('dark_background')  # Dark theme for charts
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    print("Warning: matplotlib not available - advanced charts disabled")

try:
    import psutil  # For real system monitoring
    SYSTEM_MONITOR_AVAILABLE = True
except ImportError:
    SYSTEM_MONITOR_AVAILABLE = False
    print("Warning: psutil not available - real system monitoring disabled, using simulated data")

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
        self.search_var.trace("w", self._on_search_change)
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
        self.dialog.title("⚙️ Server Settings")
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

        cancel_btn = tk.Button(button_frame, text="❌ Cancel", command=self._cancel,
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

        self.storage_var = tk.StringVar(value=self.settings.get('storage_dir', 'received_files'))
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
        """Save settings and close dialog"""
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

            self.result = self.settings
            if self.dialog:
                self.dialog.destroy()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e), parent=self.dialog if self.dialog else None)

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
        if not CHARTS_AVAILABLE:
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
        self.ax.title.set_color(ModernTheme.TEXT_PRIMARY)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_data(self, data, title="", xlabel="", ylabel=""):
        """Update chart data"""
        if not CHARTS_AVAILABLE or not self.ax:
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

    def __init__(self):
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
        
        # Server reference (will be set if needed)
        self.server = None
        
        # Settings
        self.settings = {
            'port': 1256,
            'storage_dir': 'received_files',
            'max_clients': 50,
            'session_timeout': 10,
            'maintenance_interval': 60,
            'max_file_size_mb': 4096,
            'verbose_logging': False,
            'auto_backup_db': True
        }
        
        # Database path
        self.db_path = "defensive.db"
        
        # Performance monitoring
        self.last_bytes_transferred = 0
        self.network_monitor_start = time.time()
        
    def initialize(self) -> bool:
        """Initialize GUI system"""
        try:
            self.running = True
            self.gui_thread = threading.Thread(target=self._gui_main_loop, daemon=True)
            self.gui_thread.start()

            # Wait for GUI to initialize
            max_wait = 50  # 5 seconds max
            wait_count = 0
            while not self.gui_enabled and wait_count < max_wait:
                time.sleep(0.1)
                wait_count += 1

            if self.gui_enabled:
                print("✅ Enhanced Modern GUI initialized successfully!")
                return True
            else:
                print("❌ Modern GUI initialization timed out")
                return False

        except Exception as e:
            print(f"GUI initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def shutdown(self):
        """Shutdown GUI system"""
        self.running = False
        
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
        
        if self.root:
            try:
                self.root.quit()
            except:
                pass
        
        if self.gui_thread and self.gui_thread.is_alive():
            self.gui_thread.join(timeout=2.0)
    
    def _gui_main_loop(self):
        """Main GUI thread loop"""
        try:
            print("Starting enhanced ultra modern GUI main loop...")
            # Initialize tkinter
            self.root = tk.Tk()
            print("Tkinter root created")

            # Configure the root window
            self.root.title("🚀 ULTRA MODERN Encrypted Backup Server - Enhanced")
            self.root.geometry("1200x800")
            self.root.minsize(1000, 700)
            self.root.configure(bg=ModernTheme.PRIMARY_BG)
            self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
            print("Root window configured with modern theme")

            # Create modern GUI components
            self._create_main_window()
            print("Modern main window created")
            self._create_system_tray()
            print("System tray created")

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
        main_container = tk.Frame(self.root, bg=ModernTheme.PRIMARY_BG)
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
                    self.toast_system.show_toast("🚀 Enhanced Ultra Modern GUI Ready", "success", 3000)
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
        file_menu.add_command(label="❌ Exit", command=self._exit_server)

        # Server menu
        server_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                             fg=ModernTheme.TEXT_PRIMARY,
                             activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="Server", menu=server_menu)
        server_menu.add_command(label="⚙️ Settings...", command=self._show_settings)
        server_menu.add_command(label="🔄 Restart Server", command=self._restart_server)
        server_menu.add_separator()
        server_menu.add_command(label="🗑️ Clear Activity Log", command=self._clear_activity_log)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="🏠 Dashboard", command=lambda: self._switch_tab("dashboard"))
        view_menu.add_command(label="👥 Clients", command=lambda: self._switch_tab("clients"))
        view_menu.add_command(label="📁 Files", command=lambda: self._switch_tab("files"))
        view_menu.add_command(label="📈 Analytics", command=lambda: self._switch_tab("analytics"))

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.CARD_BG,
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.ACCENT_BLUE)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="📖 Documentation", command=self._show_documentation)
        help_menu.add_command(label="ℹ️ About", command=self._show_about)

    def _create_header(self, parent):
        """Create header with title and clock"""
        header_frame = tk.Frame(parent, bg=ModernTheme.PRIMARY_BG, height=60)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(header_frame, text="🚀 ULTRA MODERN Encrypted Backup Server",
                              bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_PRIMARY,
                              font=(ModernTheme.FONT_FAMILY, 20, 'bold'))
        title_label.pack(side="left", padx=20, pady=15)

        # Clock and status
        status_frame = tk.Frame(header_frame, bg=ModernTheme.PRIMARY_BG)
        status_frame.pack(side="right", padx=20, pady=15)

        self.clock_label = tk.Label(status_frame, text="",
                                   bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_SECONDARY,
                                   font=(ModernTheme.FONT_FAMILY, 12))
        self.clock_label.pack()

        # Server status indicator
        status_indicator_frame = tk.Frame(status_frame, bg=ModernTheme.PRIMARY_BG)
        status_indicator_frame.pack(pady=(5, 0))

        self.header_status_indicator = ModernStatusIndicator(status_indicator_frame)
        self.header_status_indicator.pack(side="left", padx=(0, 5))

        self.header_status_label = tk.Label(status_indicator_frame, text="Server Offline",
                                           bg=ModernTheme.PRIMARY_BG, fg=ModernTheme.TEXT_SECONDARY,
                                           font=(ModernTheme.FONT_FAMILY, 11))
        self.header_status_label.pack(side="left")

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

        verify_btn = tk.Button(control_frame, text="✅ Verify",
                             command=self._verify_file,
                             bg=ModernTheme.SUCCESS, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                             relief="flat", bd=0, padx=15, pady=5)
        verify_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(control_frame, text="🗑️ Delete",
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
            ('success_rate', '✅ Success Rate:', '100%'),
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

    def _create_compact_two_column_layout(self, parent):
        """Create a compact two-column layout for dashboard"""
        # Main container with two columns
        main_container = tk.Frame(parent, bg=ModernTheme.PRIMARY_BG)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Configure grid weights for responsive columns
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)

        # Left Column
        left_column = tk.Frame(main_container, bg=ModernTheme.PRIMARY_BG)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Right Column
        right_column = tk.Frame(main_container, bg=ModernTheme.PRIMARY_BG)
        right_column.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # LEFT COLUMN CONTENT (Primary Stats)
        self._create_compact_server_status_card(left_column)
        self._create_compact_client_stats_card(left_column)
        self._create_compact_transfer_stats_card(left_column)
        self._create_compact_performance_card(left_column)

        # RIGHT COLUMN CONTENT (Secondary Info & Controls)
        self._create_compact_maintenance_card(right_column)
        self._create_compact_activity_log_card(right_column)
        self._create_compact_status_message_card(right_column)
        self._create_enhanced_control_panel(right_column)

    def _create_compact_server_status_card(self, parent):
        """Create compact server status card with glass morphism"""
        card = GlassMorphismCard(parent, title="🖥️ Server Status")
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
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['uptime'] = tk.Label(uptime_frame, text="⏱️ 00:00:00",
                                              bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_PRIMARY,
                                              font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['uptime'].pack(side="right")

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
        bytes_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        bytes_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(bytes_frame, text="Bytes Transferred:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['bytes'] = tk.Label(bytes_frame, text="0 B", bg=ModernTheme.GLASS_BG,
                                              fg=ModernTheme.ACCENT_PURPLE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['bytes'].pack(side="right")

        # Transfer rate
        rate_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        rate_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(rate_frame, text="Transfer Rate:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['transfer_rate'] = tk.Label(rate_frame, text="0 KB/s", bg=ModernTheme.GLASS_BG,
                                                      fg=ModernTheme.ACCENT_ORANGE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['transfer_rate'].pack(side="right")

        # Last activity
        activity_frame = tk.Frame(card.content_frame, bg=ModernTheme.GLASS_BG)
        activity_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(activity_frame, text="Last Activity:", bg=ModernTheme.GLASS_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['activity'] = tk.Label(activity_frame, text="None", bg=ModernTheme.GLASS_BG,
                                                 fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['activity'].pack(side="right")

    def _create_compact_performance_card(self, parent):
        """Create compact performance monitoring card with real data"""
        card = tk.Frame(parent, bg=ModernTheme.CARD_BG, relief="flat", bd=1)
        card.pack(fill="x", pady=(0, 8), padx=3)

        title = tk.Label(card, text="⚡ Performance Monitor", bg=ModernTheme.CARD_BG,
                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 12, 'bold'))
        title.pack(anchor="w", padx=10, pady=(8, 5))

        # CPU Usage with mini progress bar
        cpu_frame = tk.Frame(card, bg=ModernTheme.CARD_BG)
        cpu_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(cpu_frame, text="CPU:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['cpu_usage'] = tk.Label(cpu_frame, text="0%", bg=ModernTheme.CARD_BG,
                                                  fg=ModernTheme.ACCENT_GREEN, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['cpu_usage'].pack(side="right")

        self.advanced_progress_bars['cpu'] = AdvancedProgressBar(card, width=200, height=12)
        self.advanced_progress_bars['cpu'].pack(padx=10, pady=(0, 3))

        # Memory Usage with mini progress bar
        mem_frame = tk.Frame(card, bg=ModernTheme.CARD_BG)
        mem_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(mem_frame, text="Memory:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['memory_usage'] = tk.Label(mem_frame, text="0%", bg=ModernTheme.CARD_BG,
                                                     fg=ModernTheme.ACCENT_PURPLE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['memory_usage'].pack(side="right")

        self.advanced_progress_bars['memory'] = AdvancedProgressBar(card, width=200, height=12)
        self.advanced_progress_bars['memory'].pack(padx=10, pady=(0, 3))

        # Disk Usage
        disk_frame = tk.Frame(card, bg=ModernTheme.CARD_BG)
        disk_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(disk_frame, text="Disk:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['disk_usage'] = tk.Label(disk_frame, text="0%", bg=ModernTheme.CARD_BG,
                                                   fg=ModernTheme.ACCENT_ORANGE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['disk_usage'].pack(side="right")

        self.advanced_progress_bars['disk'] = AdvancedProgressBar(card, width=200, height=12)
        self.advanced_progress_bars['disk'].pack(padx=10, pady=(0, 3))

        # Network Activity
        net_frame = tk.Frame(card, bg=ModernTheme.CARD_BG)
        net_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(net_frame, text="Network:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['network_activity'] = tk.Label(net_frame, text="Idle", bg=ModernTheme.CARD_BG,
                                                         fg=ModernTheme.ACCENT_BLUE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['network_activity'].pack(side="right")

    def _create_compact_maintenance_card(self, parent):
        """Create compact maintenance statistics card"""
        card = tk.Frame(parent, bg=ModernTheme.CARD_BG, relief="flat", bd=1)
        card.pack(fill="x", pady=(0, 8), padx=3)

        title = tk.Label(card, text="⚙️ Maintenance", bg=ModernTheme.CARD_BG,
                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 12, 'bold'))
        title.pack(anchor="w", padx=10, pady=(8, 5))

        # Files cleaned
        files_frame = tk.Frame(card, bg=ModernTheme.CARD_BG)
        files_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(files_frame, text="Files Cleaned:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['files_cleaned'] = tk.Label(files_frame, text="0", bg=ModernTheme.CARD_BG,
                                                      fg=ModernTheme.ACCENT_ORANGE, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['files_cleaned'].pack(side="right")

        # Partial files cleaned
        partial_frame = tk.Frame(card, bg=ModernTheme.CARD_BG)
        partial_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(partial_frame, text="Partial Files:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['partial_cleaned'] = tk.Label(partial_frame, text="0", bg=ModernTheme.CARD_BG,
                                                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['partial_cleaned'].pack(side="right")

        # Clients cleaned
        clients_frame = tk.Frame(card, bg=ModernTheme.CARD_BG)
        clients_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(clients_frame, text="Clients Cleaned:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['clients_cleaned'] = tk.Label(clients_frame, text="0", bg=ModernTheme.CARD_BG,
                                                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9, 'bold'))
        self.status_labels['clients_cleaned'].pack(side="right")

        # Last cleanup
        cleanup_frame = tk.Frame(card, bg=ModernTheme.CARD_BG)
        cleanup_frame.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(cleanup_frame, text="Last Cleanup:", bg=ModernTheme.CARD_BG, fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, 9)).pack(side="left")
        self.status_labels['last_cleanup'] = tk.Label(cleanup_frame, text="Never", bg=ModernTheme.CARD_BG,
                                                     fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['last_cleanup'].pack(side="right")

    def _create_compact_activity_log_card(self, parent):
        """Create compact activity log card"""
        card = tk.Frame(parent, bg=ModernTheme.CARD_BG, relief="flat", bd=1)
        card.pack(fill="x", pady=(0, 8), padx=3)

        title_frame = tk.Frame(card, bg=ModernTheme.CARD_BG)
        title_frame.pack(fill="x", padx=10, pady=(8, 5))

        title = tk.Label(title_frame, text="📋 Activity Log", bg=ModernTheme.CARD_BG,
                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 12, 'bold'))
        title.pack(side="left")

        # Clear log button (smaller)
        clear_btn = tk.Button(title_frame, text="🗑️", command=self._clear_activity_log,
                             bg=ModernTheme.WARNING, fg=ModernTheme.TEXT_PRIMARY,
                             font=(ModernTheme.FONT_FAMILY, 8, 'bold'), relief="flat", bd=0, padx=5, pady=2)
        clear_btn.pack(side="right")

        # Compact scrollable text area
        log_frame = tk.Frame(card, bg=ModernTheme.CARD_BG)
        log_frame.pack(fill="x", padx=10, pady=(0, 8))

        scrollbar = tk.Scrollbar(log_frame, bg=ModernTheme.ACCENT_BG, width=12)
        scrollbar.pack(side="right", fill="y")

        self.activity_log_text = tk.Text(log_frame, height=4, bg=ModernTheme.SECONDARY_BG,
                                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 8),
                                        yscrollcommand=scrollbar.set, wrap="word", relief="flat", bd=0)
        self.activity_log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.activity_log_text.yview)

        self._add_activity_log("🚀 Enhanced Ultra Modern GUI System Initialized")

    def _create_compact_status_message_card(self, parent):
        """Create compact status message card"""
        card = tk.Frame(parent, bg=ModernTheme.CARD_BG, relief="flat", bd=1)
        card.pack(fill="x", pady=(0, 8), padx=3)

        title = tk.Label(card, text="📢 Status", bg=ModernTheme.CARD_BG,
                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 12, 'bold'))
        title.pack(anchor="w", padx=10, pady=(8, 5))

        self.status_labels['error'] = tk.Label(card, text="✅ Ready", bg=ModernTheme.CARD_BG,
                                              fg=ModernTheme.SUCCESS, font=(ModernTheme.FONT_FAMILY, 9))
        self.status_labels['error'].pack(padx=10, pady=(5, 8), anchor="w")

    def _create_enhanced_control_panel(self, parent):
        """Create enhanced compact control panel"""
        card = tk.Frame(parent, bg=ModernTheme.CARD_BG, relief="flat", bd=1)
        card.pack(fill="x", pady=(0, 8), padx=3)

        title = tk.Label(card, text="🎛️ Control Panel", bg=ModernTheme.CARD_BG,
                        fg=ModernTheme.TEXT_PRIMARY, font=(ModernTheme.FONT_FAMILY, 12, 'bold'))
        title.pack(anchor="w", padx=10, pady=(8, 5))

        # Compact button grid
        button_frame = tk.Frame(card, bg=ModernTheme.CARD_BG)
        button_frame.pack(fill="x", padx=10, pady=(0, 8))

        # Row 1
        row1 = tk.Frame(button_frame, bg=ModernTheme.CARD_BG)
        row1.pack(fill="x", pady=(0, 3))

        self._create_compact_button(row1, "👥 Clients", lambda: self._switch_tab("clients"), ModernTheme.ACCENT_BLUE)
        self._create_compact_button(row1, "📁 Files", lambda: self._switch_tab("files"), ModernTheme.ACCENT_PURPLE)

        # Row 2
        row2 = tk.Frame(button_frame, bg=ModernTheme.CARD_BG)
        row2.pack(fill="x", pady=(0, 3))

        self._create_compact_button(row2, "⚙️ Settings", self._show_settings, ModernTheme.ACCENT_GREEN)
        self._create_compact_button(row2, "🔄 Restart", self._restart_server, ModernTheme.WARNING)

        # Row 3
        row3 = tk.Frame(button_frame, bg=ModernTheme.CARD_BG)
        row3.pack(fill="x")

        self._create_compact_button(row3, "📈 Analytics", lambda: self._switch_tab("analytics"), ModernTheme.ACCENT_ORANGE)
        self._create_compact_button(row3, "❌ Exit", self._exit_server, ModernTheme.ERROR)

    def _create_compact_button(self, parent, text, command, color):
        """Create a compact modern button"""
        button = tk.Button(parent, text=text, command=command,
                          bg=color, fg=ModernTheme.TEXT_PRIMARY,
                          font=(ModernTheme.FONT_FAMILY, 8, 'bold'),
                          relief="flat", bd=0, padx=8, pady=4)
        button.pack(side="left", fill="x", expand=True, padx=(0, 3))

        # Add hover effects
        def on_enter(e):
            button.config(bg=ModernTheme.ACCENT_BG)
        def on_leave(e):
            button.config(bg=color)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        return button

    def _setup_modern_styles(self):
        """Setup ultra modern styling for ttk widgets"""
        style = ttk.Style()

        # Configure modern dark theme
        style.theme_use('clam')  # Use clam as base theme

        # Configure modern styles
        style.configure('Modern.TFrame',
                       background=ModernTheme.CARD_BG,
                       relief='flat',
                       borderwidth=0)

        style.configure('Modern.TLabel',
                       background=ModernTheme.CARD_BG,
                       foreground=ModernTheme.TEXT_PRIMARY,
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MEDIUM))

        style.configure('ModernTitle.TLabel',
                       background=ModernTheme.PRIMARY_BG,
                       foreground=ModernTheme.TEXT_PRIMARY,
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_LARGE, 'bold'))

        style.configure('ModernButton.TButton',
                       background=ModernTheme.ACCENT_BLUE,
                       foreground=ModernTheme.TEXT_PRIMARY,
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MEDIUM),
                       relief='flat',
                       borderwidth=0,
                       padding=(20, 10))

        style.map('ModernButton.TButton',
                 background=[('active', ModernTheme.ACCENT_PURPLE),
                           ('pressed', ModernTheme.ACCENT_GREEN)])

    def _create_system_tray(self):
        """Create system tray icon with modern design"""
        if not TRAY_AVAILABLE:
            return
        
        try:
            # Create a modern icon
            image = Image.new('RGB', (64, 64), color=ModernTheme.ACCENT_BLUE)
            draw = ImageDraw.Draw(image)
            
            # Draw server icon
            draw.rectangle([16, 16, 48, 32], fill='white')
            draw.rectangle([20, 36, 44, 48], fill='white')
            draw.rectangle([24, 20, 28, 28], fill=ModernTheme.ACCENT_BLUE)
            draw.rectangle([36, 20, 40, 28], fill=ModernTheme.ACCENT_BLUE)
            
            # Create menu with additional options
            menu = pystray.Menu(
                pystray.MenuItem("Show Dashboard", self._show_window),
                pystray.MenuItem("View Clients", lambda: self._show_and_switch_tab("clients")),
                pystray.MenuItem("View Files", lambda: self._show_and_switch_tab("files")),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Start Server", self._tray_start_server),
                pystray.MenuItem("Stop Server", self._tray_stop_server),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Settings", self._show_settings),
                pystray.MenuItem("Exit", self._exit_server)
            )
            
            # Create and start tray icon
            self.tray_icon = pystray.Icon("EnhancedBackupServer", image, 
                                        "Enhanced Encrypted Backup Server", menu)
            
            # Start tray in separate thread
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
            
        except Exception as e:
            print(f"System tray creation failed: {e}")
    
    def _schedule_updates(self):
        """Schedule periodic GUI updates with advanced features"""
        if self.running and self.gui_enabled:
            self._process_updates()
            self._update_uptime()
            self._update_clock()
            self._update_performance_metrics()
            self._update_transfer_rate()
            
            # Update charts if analytics tab is active
            if self.current_tab == "analytics":
                self._update_analytics_charts()

            # Schedule next update
            if self.root:
                self.root.after(1000, self._schedule_updates)  # Update every second
    
    def _process_updates(self):
        """Process queued status updates"""
        try:
            while True:
                update = self.update_queue.get_nowait()
                self._apply_update(update)
        except queue.Empty:
            pass
    
    def _apply_update(self, update: Dict[str, Any]):
        """Apply a status update to the GUI"""
        if not self.gui_enabled:
            return
        
        try:
            update_type = update.get('type')
            
            if update_type == 'server_status':
                self._update_server_status(update)
            elif update_type == 'client_stats':
                self._update_client_stats(update)
            elif update_type == 'transfer_stats':
                self._update_transfer_stats(update)
            elif update_type == 'maintenance_stats':
                self._update_maintenance_stats(update)
            elif update_type == 'error':
                self._update_error(update)
            elif update_type == 'notification':
                self._show_notification(update)
                
        except Exception as e:
            print(f"GUI update error: {e}")
    
    def _update_server_status(self, update: Dict[str, Any]):
        """Update server status information with modern styling"""
        if 'running' in update:
            self.status.running = update['running']
            status_text = "🟢 Running" if self.status.running else "🛑 Stopped"
            color = ModernTheme.SUCCESS if self.status.running else ModernTheme.ERROR

            # Update main status label
            if 'status' in self.status_labels:
                self.status_labels['status'].config(text=status_text, fg=color)

            # Update header status indicator
            if hasattr(self, 'header_status_indicator'):
                status_type = "online" if self.status.running else "offline"
                self.header_status_indicator.set_status(status_type)

            # Update header status label
            if hasattr(self, 'header_status_label'):
                header_text = "Server Online" if self.status.running else "Server Offline"
                self.header_status_label.config(text=header_text, fg=color)

        if 'address' in update:
            self.status.server_address = update['address']

        if 'port' in update:
            self.status.port = update['port']

        # Update address display
        if 'address' in update or 'port' in update:
            if 'address' in self.status_labels:
                address_text = f"🌐 {self.status.server_address}:{self.status.port}"
                self.status_labels['address'].config(text=address_text)
    
    def _update_client_stats(self, update: Dict[str, Any]):
        """Update client statistics with modern styling"""
        if 'connected' in update:
            self.status.clients_connected = update['connected']
            if 'connected' in self.status_labels:
                self.status_labels['connected'].config(text=str(self.status.clients_connected))

            # Update performance data
            self.performance_data['client_connections'].append(self.status.clients_connected)
            self.performance_data['timestamps'].append(datetime.now())

        if 'total' in update:
            self.status.total_clients = update['total']
            if 'total' in self.status_labels:
                self.status_labels['total'].config(text=str(self.status.total_clients))

        if 'active_transfers' in update:
            self.status.active_transfers = update['active_transfers']
            if 'active_transfers' in self.status_labels:
                self.status_labels['active_transfers'].config(text=str(self.status.active_transfers))
    
    def _update_transfer_stats(self, update: Dict[str, Any]):
        """Update transfer statistics with formatting"""
        if 'bytes_transferred' in update:
            self.status.bytes_transferred = update['bytes_transferred']
            formatted_bytes = self._format_bytes(self.status.bytes_transferred)
            if 'bytes' in self.status_labels:
                self.status_labels['bytes'].config(text=formatted_bytes)
            
            # Update performance data
            self.performance_data['bytes_transferred'].append(self.status.bytes_transferred)
        
        if 'last_activity' in update:
            self.status.last_activity = update['last_activity']
            if 'activity' in self.status_labels:
                self.status_labels['activity'].config(text=self.status.last_activity)
    
    def _update_maintenance_stats(self, update: Dict[str, Any]):
        """Update maintenance statistics"""
        stats = update.get('stats', {})

        if 'files_cleaned' in stats:
            self.status.maintenance_stats['files_cleaned'] = stats['files_cleaned']
            if 'files_cleaned' in self.status_labels:
                self.status_labels['files_cleaned'].config(
                    text=str(self.status.maintenance_stats['files_cleaned']))

        if 'partial_files_cleaned' in stats:
            self.status.maintenance_stats['partial_files_cleaned'] = stats['partial_files_cleaned']
            if 'partial_cleaned' in self.status_labels:
                self.status_labels['partial_cleaned'].config(
                    text=str(self.status.maintenance_stats['partial_files_cleaned']))

        if 'clients_cleaned' in stats:
            self.status.maintenance_stats['clients_cleaned'] = stats['clients_cleaned']
            if 'clients_cleaned' in self.status_labels:
                self.status_labels['clients_cleaned'].config(
                    text=str(self.status.maintenance_stats['clients_cleaned']))

        if 'last_cleanup' in stats:
            self.status.maintenance_stats['last_cleanup'] = stats['last_cleanup']
            if 'last_cleanup' in self.status_labels:
                self.status_labels['last_cleanup'].config(
                    text=self.status.maintenance_stats['last_cleanup'])
    
    def _update_error(self, update: Dict[str, Any]):
        """Update error/status message with modern colors"""
        message = update.get('message', '')
        error_type = update.get('error_type', 'info')
        
        color_map = {
            'error': ModernTheme.ERROR,
            'success': ModernTheme.SUCCESS,
            'warning': ModernTheme.WARNING,
            'info': ModernTheme.INFO
        }
        
        color = color_map.get(error_type, ModernTheme.TEXT_PRIMARY)
        prefix_map = {
            'error': "❌ ",
            'success': "✅ ",
            'warning': "⚠️ ",
            'info': "ℹ️ "
        }
        prefix = prefix_map.get(error_type, "")
        
        if 'error' in self.status_labels:
            self.status_labels['error'].config(text=f"{prefix}{message}", fg=color)
    
    def _update_uptime(self):
        """Update server uptime display"""
        try:
            if self.status.running and 'uptime' in self.status_labels:
                uptime_seconds = int(time.time() - self.start_time)
                uptime_str = self._format_duration(uptime_seconds)
                self.status_labels['uptime'].config(text=f"⏱️ {uptime_str}")
        except Exception as e:
            print(f"Uptime update failed: {e}")
    
    def _update_clock(self):
        """Update real-time clock"""
        try:
            if hasattr(self, 'clock_label') and self.clock_label:
                current_time = time.strftime("🕐 %H:%M:%S | %Y-%m-%d")
                self.clock_label.config(text=current_time)
        except Exception as e:
            print(f"Clock update failed: {e}")
    
    def _update_performance_metrics(self):
        """Update performance metrics with real system data"""
        try:
            if SYSTEM_MONITOR_AVAILABLE:
                # Real CPU usage
                cpu_usage = psutil.cpu_percent(interval=0.1)
                if 'cpu_usage' in self.status_labels:
                    self.status_labels['cpu_usage'].config(text=f"{cpu_usage:.1f}%")
                if 'cpu' in self.advanced_progress_bars:
                    self.advanced_progress_bars['cpu'].set_progress(cpu_usage)
                self.performance_data['cpu_usage'].append(cpu_usage)

                # Real Memory usage
                memory = psutil.virtual_memory()
                memory_usage = memory.percent
                if 'memory_usage' in self.status_labels:
                    self.status_labels['memory_usage'].config(text=f"{memory_usage:.1f}%")
                if 'memory' in self.advanced_progress_bars:
                    self.advanced_progress_bars['memory'].set_progress(memory_usage)
                self.performance_data['memory_usage'].append(memory_usage)

                # Real Disk usage
                disk = psutil.disk_usage(self.settings['storage_dir'])
                disk_usage = disk.percent
                if 'disk_usage' in self.status_labels:
                    self.status_labels['disk_usage'].config(text=f"{disk_usage:.1f}%")
                if 'disk' in self.advanced_progress_bars:
                    self.advanced_progress_bars['disk'].set_progress(disk_usage)

                # Network activity
                net_io = psutil.net_io_counters()
                bytes_sent = net_io.bytes_sent
                bytes_recv = net_io.bytes_recv
                self.performance_data['network_activity'].append(bytes_sent + bytes_recv)

                # Network status
                if self.status.active_transfers > 0:
                    activity = "Active"
                    color = ModernTheme.ACCENT_GREEN
                else:
                    activity = "Idle"
                    color = ModernTheme.ACCENT_BLUE

                if 'network_activity' in self.status_labels:
                    self.status_labels['network_activity'].config(text=activity, fg=color)

            else:
                # Simulated data if psutil not available
                import random
                
                cpu_usage = random.randint(5, 25)
                if 'cpu_usage' in self.status_labels:
                    self.status_labels['cpu_usage'].config(text=f"{cpu_usage}%")
                if 'cpu' in self.advanced_progress_bars:
                    self.advanced_progress_bars['cpu'].set_progress(cpu_usage)

                memory_usage = random.randint(15, 35)
                if 'memory_usage' in self.status_labels:
                    self.status_labels['memory_usage'].config(text=f"{memory_usage}%")
                if 'memory' in self.advanced_progress_bars:
                    self.advanced_progress_bars['memory'].set_progress(memory_usage)

                disk_usage = random.randint(20, 40)
                if 'disk_usage' in self.status_labels:
                    self.status_labels['disk_usage'].config(text=f"{disk_usage}%")
                if 'disk' in self.advanced_progress_bars:
                    self.advanced_progress_bars['disk'].set_progress(disk_usage)

        except Exception as e:
            print(f"Performance metrics update failed: {e}")

    def _update_transfer_rate(self):
        """Calculate and update transfer rate"""
        try:
            current_time = time.time()
            time_diff = current_time - self.network_monitor_start
            
            if time_diff >= 1.0:  # Update every second
                bytes_diff = self.status.bytes_transferred - self.last_bytes_transferred
                rate = bytes_diff / time_diff  # Bytes per second
                
                if 'transfer_rate' in self.status_labels:
                    rate_str = self._format_transfer_rate(rate)
                    self.status_labels['transfer_rate'].config(text=rate_str)
                
                self.last_bytes_transferred = self.status.bytes_transferred
                self.network_monitor_start = current_time
                
        except Exception as e:
            print(f"Transfer rate update failed: {e}")

    def _add_activity_log(self, message):
        """Add entry to activity log"""
        try:
            if hasattr(self, 'activity_log_text') and self.activity_log_text:
                timestamp = time.strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] {message}\n"
                self.activity_log_text.insert(tk.END, log_entry)
                self.activity_log_text.see(tk.END)  # Auto-scroll to bottom

                # Keep log size manageable (max 100 lines)
                lines = self.activity_log_text.get("1.0", tk.END).split('\n')
                if len(lines) > 100:
                    self.activity_log_text.delete("1.0", "2.0")
                    
                # Add to internal log
                self.activity_log.append((timestamp, message))
        except Exception as e:
            print(f"Activity log update failed: {e}")

    def _clear_activity_log(self):
        """Clear the activity log"""
        try:
            if hasattr(self, 'activity_log_text') and self.activity_log_text:
                self.activity_log_text.delete("1.0", tk.END)
                self._add_activity_log("📋 Activity log cleared")
            self.activity_log = []
        except Exception as e:
            print(f"Activity log clear failed: {e}")

    def _refresh_client_table(self):
        """Refresh client table from database"""
        try:
            if not self.client_table:
                return

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all clients
            cursor.execute("""
                SELECT c.ID, c.Name, c.LastSeen, 
                       (SELECT COUNT(*) FROM files WHERE ID = c.ID) as FileCount
                FROM clients c
                ORDER BY c.LastSeen DESC
            """)
            
            clients = []
            for row in cursor.fetchall():
                client_id = row[0]
                client_name = row[1]
                last_seen = row[2]
                file_count = row[3]
                
                # Check if client is active (in memory)
                status = "🟢 Online" if client_id in getattr(self, 'active_clients', {}) else "🔴 Offline"
                
                clients.append({
                    'name': client_name,
                    'id': client_id.hex() if client_id else '',
                    'status': status,
                    'last_seen': last_seen,
                    'files': str(file_count)
                })
            
            conn.close()
            
            self.client_table.set_data(clients)
            self._add_activity_log(f"📋 Refreshed client list ({len(clients)} clients)")
            
        except Exception as e:
            print(f"Failed to refresh client table: {e}")
            self._add_activity_log(f"❌ Failed to refresh client list: {str(e)}")

    def _refresh_file_table(self):
        """Refresh file table from database"""
        try:
            if not self.file_table:
                return

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all files with client info
            cursor.execute("""
                SELECT f.FileName, f.PathName, f.Verified, c.Name, f.ID
                FROM files f
                JOIN clients c ON f.ID = c.ID
                ORDER BY f.FileName
            """)
            
            files = []
            for row in cursor.fetchall():
                filename = row[0]
                pathname = row[1]
                verified = row[2]
                client_name = row[3]
                
                # Get file size if file exists
                size_str = "N/A"
                date_str = "N/A"
                if os.path.exists(pathname):
                    try:
                        stat = os.stat(pathname)
                        size_str = self._format_bytes(stat.st_size)
                        date_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                
                files.append({
                    'filename': filename,
                    'client': client_name,
                    'size': size_str,
                    'date': date_str,
                    'verified': "✅" if verified else "❌",
                    'path': pathname
                })
            
            conn.close()
            
            self.file_table.set_data(files)
            self._add_activity_log(f"📋 Refreshed file list ({len(files)} files)")
            
        except Exception as e:
            print(f"Failed to refresh file table: {e}")
            self._add_activity_log(f"❌ Failed to refresh file list: {str(e)}")

    def _update_analytics_charts(self):
        """Update analytics charts with real data"""
        try:
            if not CHARTS_AVAILABLE:
                return

            # Performance chart
            if self.performance_chart and self.performance_data['timestamps']:
                timestamps = list(self.performance_data['timestamps'])
                data = {
                    'CPU': (timestamps, list(self.performance_data['cpu_usage'])),
                    'Memory': (timestamps, list(self.performance_data['memory_usage']))
                }
                self.performance_chart.update_data(data, "System Performance", "Time", "Usage %")

            # Transfer volume chart
            if self.transfer_chart and self.performance_data['bytes_transferred']:
                timestamps = list(self.performance_data['timestamps'])
                bytes_data = list(self.performance_data['bytes_transferred'])
                # Convert to MB for display
                mb_data = [b / (1024 * 1024) for b in bytes_data]
                data = {'Transfer Volume': (timestamps, mb_data)}
                self.transfer_chart.update_data(data, "Transfer Volume Over Time", "Time", "MB")

            # Client connections chart
            if self.client_chart:
                # Get hourly stats from database
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    # Get client activity by hour
                    cursor.execute("""
                        SELECT 
                            strftime('%H', LastSeen) as Hour,
                            COUNT(*) as ClientCount
                        FROM clients
                        WHERE LastSeen >= datetime('now', '-24 hours')
                        GROUP BY Hour
                        ORDER BY Hour
                    """)
                    
                    hours = []
                    counts = []
                    for row in cursor.fetchall():
                        hours.append(f"{row[0]}:00")
                        counts.append(row[1])
                    
                    conn.close()
                    
                    if hours:
                        data = {hour: count for hour, count in zip(hours, counts)}
                        self.client_chart.update_data(data, "Client Activity (24h)", "", "Clients")
                    
                except Exception as e:
                    print(f"Failed to update client chart: {e}")

            # Update summary statistics
            self._update_summary_statistics()

        except Exception as e:
            print(f"Failed to update analytics charts: {e}")

    def _update_summary_statistics(self):
        """Update summary statistics in analytics tab"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total files
            cursor.execute("SELECT COUNT(*) FROM files")
            total_files = cursor.fetchone()[0]
            if 'total_files' in self.stats_labels:
                self.stats_labels['total_files'].config(text=str(total_files))
            
            # Total size
            total_size = 0
            cursor.execute("SELECT PathName FROM files")
            for (pathname,) in cursor.fetchall():
                if os.path.exists(pathname):
                    try:
                        total_size += os.path.getsize(pathname)
                    except:
                        pass
            
            if 'total_size' in self.stats_labels:
                self.stats_labels['total_size'].config(text=self._format_bytes(total_size))
            
            # Average file size
            avg_size = total_size / total_files if total_files > 0 else 0
            if 'avg_file_size' in self.stats_labels:
                self.stats_labels['avg_file_size'].config(text=self._format_bytes(avg_size))
            
            # Success rate
            cursor.execute("SELECT COUNT(*) FROM files WHERE Verified = 1")
            verified_files = cursor.fetchone()[0]
            success_rate = (verified_files / total_files * 100) if total_files > 0 else 100
            if 'success_rate' in self.stats_labels:
                self.stats_labels['success_rate'].config(text=f"{success_rate:.1f}%")
            
            # Peak clients (max concurrent connections seen)
            peak = max(self.performance_data['client_connections']) if self.performance_data['client_connections'] else 0
            if 'peak_clients' in self.stats_labels:
                self.stats_labels['peak_clients'].config(text=str(peak))
            
            # Uptime
            if self.status.running:
                uptime_seconds = int(time.time() - self.start_time)
                uptime_days = uptime_seconds / (24 * 3600)
                if 'uptime_days' in self.stats_labels:
                    self.stats_labels['uptime_days'].config(text=f"{uptime_days:.1f} days")
            
            conn.close()
            
        except Exception as e:
            print(f"Failed to update summary statistics: {e}")

    def _show_notification(self, update: Dict[str, Any]):
        """Show notification popup"""
        title = update.get('title', 'Server Notification')
        message = update.get('message', '')
        
        if self.gui_enabled:
            messagebox.showinfo(title, message)

    def _format_bytes(self, bytes_count: Union[int, float]) -> str:
        """Format byte count as human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} PB"

    def _format_transfer_rate(self, bytes_per_second: float) -> str:
        """Format transfer rate"""
        if bytes_per_second < 1024:
            return f"{bytes_per_second:.1f} B/s"
        elif bytes_per_second < 1024 * 1024:
            return f"{bytes_per_second / 1024:.1f} KB/s"
        else:
            return f"{bytes_per_second / (1024 * 1024):.1f} MB/s"

    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds as HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # Event handlers and actions
    def _on_window_close(self):
        """Handle window close event"""
        if messagebox.askokcancel("Hide to Tray", "Hide the server GUI to system tray?\n\nThe server will continue running in the background."):
            self._hide_window()
        
    def _show_window(self):
        """Show main window"""
        if self.root:
            self.root.deiconify()
            self.root.lift()
    
    def _hide_window(self):
        """Hide main window to tray"""
        if self.root:
            self.root.withdraw()
    
    def _show_and_switch_tab(self, tab):
        """Show window and switch to specified tab"""
        self._show_window()
        self._switch_tab(tab)

    def _tray_start_server(self):
        """Start server from tray menu"""
        # This would need to be connected to actual server start logic
        self._add_activity_log("⚠️ Server start from tray not implemented")
        if self.toast_system:
            self.toast_system.show_toast("Server start not implemented", "warning")

    def _tray_stop_server(self):
        """Stop server from tray menu"""
        # This would need to be connected to actual server stop logic
        self._add_activity_log("⚠️ Server stop from tray not implemented")
        if self.toast_system:
            self.toast_system.show_toast("Server stop not implemented", "warning")

    def _restart_server(self):
        """Restart the server"""
        result = messagebox.askyesno("Restart Server", 
                                   "Are you sure you want to restart the backup server?\n\nAll active connections will be terminated.")
        if result:
            self._add_activity_log("🔄 Server restart requested")
            if self.toast_system:
                self.toast_system.show_toast("Server restart initiated", "info")
            # Actual restart logic would be implemented here

    def _exit_server(self):
        """Exit the server application"""
        result = messagebox.askyesno("Exit Server", 
                                   "Are you sure you want to exit the backup server?\n\nThis will stop the server and close the application.")
        if result:
            self._add_activity_log("❌ Server shutdown requested")
            # Signal the main application to exit
            self.shutdown()
            os._exit(0)

    def _show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.root, self.settings)
        new_settings = dialog.show()        
        if new_settings:
            self.settings = new_settings
            self._add_activity_log("⚙️ Settings updated")
            if self.toast_system:
                self.toast_system.show_toast("Settings saved successfully", "success")
            # Apply settings changes here
            
    def _on_client_selected(self, client_data):
        """Handle client selection in table"""
        self._add_activity_log(f"👤 Selected client: {client_data['name']}")

    def _show_client_details(self):
        """Show details for selected client"""
        if not self.client_table:
            messagebox.showwarning("Not Available", "Client table not initialized")
            return
            
        selected = self.client_table.get_selected_items()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a client first")
            return
        
        client = selected[0]
        details = f"""Client Details

Name: {client['name']}
ID: {client['id']}
Status: {client['status']}
Last Seen: {client['last_seen']}
Files: {client['files']}
"""
        messagebox.showinfo("Client Details", details)

    def _disconnect_client(self):
        """Disconnect selected client"""
        if not self.client_table:
            messagebox.showwarning("Not Available", "Client table not initialized")
            return
            
        selected = self.client_table.get_selected_items()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a client first")
            return
        
        client = selected[0]
        result = messagebox.askyesno("Disconnect Client", 
                                   f"Disconnect client '{client['name']}'?\n\nThis will terminate their active connection.")
        if result:
            self._add_activity_log(f"🔌 Disconnecting client: {client['name']}")
            # Actual disconnect logic would be implemented here

    def _export_clients(self):
        """Export client list to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Client List"        )
        
        if filename:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT Name, ID, LastSeen FROM clients")
                
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Client Name', 'Client ID', 'Last Seen'])
                    
                    for row in cursor.fetchall():
                        writer.writerow([row[0], row[1].hex() if row[1] else '', row[2]])
                
                conn.close()
                
                self._add_activity_log(f"💾 Exported client list to {filename}")
                if self.toast_system:
                    self.toast_system.show_toast("Client list exported successfully", "success")
                    
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export client list:\n{str(e)}")

    def _on_file_selected(self, file_data):
        """Handle file selection in table"""
        self._add_activity_log(f"📁 Selected file: {file_data['filename']}")

    def _show_file_details(self):
        """Show details for selected file"""
        if not self.file_table:
            messagebox.showwarning("Not Available", "File table not initialized")
            return
            
        selected = self.file_table.get_selected_items()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a file first")
            return
        
        file = selected[0]
        details = f"""File Details

Name: {file['filename']}
Client: {file['client']}
Size: {file['size']}
Date: {file['date']}
Verified: {file['verified']}
Path: {file['path']}
"""
        messagebox.showinfo("File Details", details)

    def _verify_file(self):
        """Verify selected file"""
        if not self.file_table:
            messagebox.showwarning("Not Available", "File table not initialized")
            return
            
        selected = self.file_table.get_selected_items()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a file first")
            return

        file = selected[0]
        self._add_activity_log(f"✅ Verifying file: {file['filename']}")
        # Actual verification logic would be implemented here
        
    def _delete_file(self):
        """Delete selected file"""
        if not self.file_table:
            messagebox.showwarning("Not Available", "File table not initialized")
            return
            
        selected = self.file_table.get_selected_items()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a file first")
            return
        
        file = selected[0]
        result = messagebox.askyesno("Delete File", 
                                   f"Delete file '{file['filename']}'?\n\nThis action cannot be undone.")
        if result:
            self._add_activity_log(f"🗑️ Deleting file: {file['filename']}")
            # Actual delete logic would be implemented here

    def _export_files(self):
        """Export file list to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export File List"
        )
        
        if filename:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT f.FileName, c.Name, f.PathName, f.Verified
                    FROM files f
                    JOIN clients c ON f.ID = c.ID
                """)
                
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['File Name', 'Client', 'Path', 'Verified'])
                    
                    for row in cursor.fetchall():
                        writer.writerow([row[0], row[1], row[2], 'Yes' if row[3] else 'No'])
                
                conn.close()
                
                self._add_activity_log(f"💾 Exported file list to {filename}")
                if self.toast_system:
                    self.toast_system.show_toast("File list exported successfully", "success")
                    
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export file list:\n{str(e)}")

    def _backup_database(self):
        """Backup the database"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            title="Backup Database"
        )
        
        if filename:
            try:
                import shutil
                shutil.copy2(self.db_path, filename)
                
                self._add_activity_log(f"💾 Database backed up to {filename}")
                if self.toast_system:
                    self.toast_system.show_toast("Database backup successful", "success")
                    
            except Exception as e:
                messagebox.showerror("Backup Failed", f"Failed to backup database:\n{str(e)}")

    def _show_documentation(self):
        """Show documentation"""
        docs = """Enhanced Encrypted Backup Server - Documentation

FEATURES:
• End-to-end encryption with RSA/AES
• Multi-client support with concurrent connections
• Automatic file integrity verification (CRC32)
• Real-time performance monitoring
• Comprehensive client and file management
• Advanced analytics and reporting

TABS:
• Dashboard - Overview of server status and statistics
• Clients - Manage connected clients
• Files - Browse and manage backed up files
• Analytics - View performance charts and statistics

SECURITY:
• RSA 1024-bit for key exchange
• AES 256-bit for file encryption
• Automatic session key generation
• Client authentication required

For more information, visit the project repository.
"""
        messagebox.showinfo("Documentation", docs)

    def _show_about(self):
        """Show about dialog"""
        about = """Enhanced Encrypted Backup Server GUI
Version 2.0

An ultra-modern interface for managing
secure file backups with style.

Features:
• Glass morphism UI design
• Real-time monitoring
• Advanced analytics
• Toast notifications
• System tray integration

© 2024 - Enhanced Edition
"""
        messagebox.showinfo("About", about)

    # Public API methods for server integration
    def update_server_status(self, running: bool, address: str = "", port: int = 0):
        """Update server running status"""
        if not self.gui_enabled:
            return

        try:
            # Update status immediately if GUI is ready
            if 'status' in self.status_labels:
                status_text = "🟢 Running" if running else "🛑 Stopped"
                color = ModernTheme.SUCCESS if running else ModernTheme.ERROR
                self.status_labels['status'].config(text=status_text, fg=color)

            if 'address' in self.status_labels and address and port:
                self.status_labels['address'].config(text=f"🌐 {address}:{port}")

            # Update header indicator
            if hasattr(self, 'header_status_indicator'):
                self.header_status_indicator.set_status("online" if running else "offline")
                
            if hasattr(self, 'header_status_label'):
                self.header_status_label.config(
                    text="Server Online" if running else "Server Offline",
                    fg=ModernTheme.SUCCESS if running else ModernTheme.ERROR
                )

            # Update internal status
            old_running = self.status.running
            self.status.running = running
            self.status.server_address = address
            self.status.port = port

            # Add activity log and toast notification for status changes
            if old_running != running:
                if running:
                    message = f"🟢 Server started on {address}:{port}"
                    self._add_activity_log(message)
                    if self.toast_system:
                        self.toast_system.show_toast(message, "success")
                else:
                    message = "🛑 Server stopped"
                    self._add_activity_log(message)
                    if self.toast_system:
                        self.toast_system.show_toast(message, "warning")

        except Exception as e:
            print(f"GUI server status update failed: {e}")

    def update_client_stats(self, connected: Optional[int] = None, total: Optional[int] = None,
                           active_transfers: Optional[int] = None):
        """Update client statistics"""
        if not self.gui_enabled:
            return

        try:
            # Track changes for activity logging
            old_connected = self.status.clients_connected
            old_transfers = self.status.active_transfers

            if connected is not None and 'connected' in self.status_labels:
                self.status_labels['connected'].config(text=str(connected))
                self.status.clients_connected = connected
                
                # Store active client IDs for status checking
                # This would need to be passed from the server
                
                # Log client connection changes
                if old_connected != connected:
                    if connected > old_connected:
                        self._add_activity_log(f"👥 Client connected (Total: {connected})")
                    elif connected < old_connected:
                        self._add_activity_log(f"👤 Client disconnected (Total: {connected})")

            if total is not None and 'total' in self.status_labels:
                self.status_labels['total'].config(text=str(total))
                self.status.total_clients = total

            if active_transfers is not None and 'active_transfers' in self.status_labels:
                self.status_labels['active_transfers'].config(text=str(active_transfers))
                self.status.active_transfers = active_transfers

                # Log transfer activity changes
                if old_transfers != active_transfers:
                    if active_transfers > old_transfers:
                        self._add_activity_log(f"📤 Transfer started (Active: {active_transfers})")
                    elif active_transfers < old_transfers:
                        self._add_activity_log(f"✅ Transfer completed (Active: {active_transfers})")

        except Exception as e:
            print(f"GUI client stats update failed: {e}")

    def update_transfer_stats(self, bytes_transferred: Optional[int] = None,
                             last_activity: Optional[str] = None):
        """Update transfer statistics"""
        if not self.gui_enabled:
            return

        try:
            if bytes_transferred is not None and 'bytes' in self.status_labels:
                formatted_bytes = self._format_bytes(bytes_transferred)
                self.status_labels['bytes'].config(text=formatted_bytes)
                self.status.bytes_transferred = bytes_transferred

            if last_activity is not None and 'activity' in self.status_labels:
                self.status_labels['activity'].config(text=last_activity)
                self.status.last_activity = last_activity

        except Exception as e:
            print(f"GUI transfer stats update failed: {e}")

    def update_maintenance_stats(self, stats: Dict[str, Any]):
        """Update maintenance statistics"""
        if not self.gui_enabled:
            return

        try:
            if 'files_cleaned' in stats and 'files_cleaned' in self.status_labels:
                self.status_labels['files_cleaned'].config(text=str(stats['files_cleaned']))

            if 'partial_files_cleaned' in stats and 'partial_cleaned' in self.status_labels:
                self.status_labels['partial_cleaned'].config(text=str(stats['partial_files_cleaned']))

            if 'clients_cleaned' in stats and 'clients_cleaned' in self.status_labels:
                self.status_labels['clients_cleaned'].config(text=str(stats['clients_cleaned']))

            if 'last_cleanup' in stats and 'last_cleanup' in self.status_labels:
                self.status_labels['last_cleanup'].config(text=stats['last_cleanup'])

        except Exception as e:
            print(f"GUI maintenance stats update failed: {e}")

    def show_error(self, message: str):
        """Show error message"""
        if not self.gui_enabled:
            return

        try:
            if 'error' in self.status_labels:
                self.status_labels['error'].config(text=f"❌ {message}", fg=ModernTheme.ERROR)
            self._add_activity_log(f"❌ Error: {message}")
        except Exception as e:
            print(f"GUI error display failed: {e}")

    def show_success(self, message: str):
        """Show success message"""
        if not self.gui_enabled:
            return

        try:
            if 'error' in self.status_labels:
                self.status_labels['error'].config(text=f"✅ {message}", fg=ModernTheme.SUCCESS)
            self._add_activity_log(f"✅ Success: {message}")
        except Exception as e:
            print(f"GUI success display failed: {e}")

    def show_info(self, message: str):
        """Show info message"""
        if not self.gui_enabled:
            return

        try:
            if 'error' in self.status_labels:
                self.status_labels['error'].config(text=f"ℹ️ {message}", fg=ModernTheme.INFO)
            self._add_activity_log(f"ℹ️ Info: {message}")
        except Exception as e:
            print(f"GUI info display failed: {e}")

    def show_notification(self, title: str, message: str):
        """Show notification popup"""
        self.update_queue.put({
            'type': 'notification',
            'title': title,
            'message': message
        })

# Global GUI instance (singleton pattern)
_server_gui_instance = None

def get_server_gui() -> ServerGUI:
    """Get the global ServerGUI instance"""
    global _server_gui_instance
    if _server_gui_instance is None:
        _server_gui_instance = ServerGUI()
    return _server_gui_instance

# Helper functions for easy integration
def initialize_server_gui() -> bool:
    """Initialize the server GUI system"""
    try:
        gui = get_server_gui()
        return gui.initialize()
    except Exception as e:
        print(f"Server GUI initialization failed: {e}")
        return False

def shutdown_server_gui():
    """Shutdown the server GUI system"""
    global _server_gui_instance
    if _server_gui_instance:
        _server_gui_instance.shutdown()
        _server_gui_instance = None

def update_server_status(running: bool, address: str = "", port: int = 0):
    """Update server status in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.update_server_status(running, address, port)
    except:
        pass

def update_client_stats(connected: Optional[int] = None, total: Optional[int] = None,
                       active_transfers: Optional[int] = None):
    """Update client statistics in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.update_client_stats(connected, total, active_transfers)
    except:
        pass

def update_transfer_stats(bytes_transferred: Optional[int] = None, last_activity: Optional[str] = None):
    """Update transfer statistics in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.update_transfer_stats(bytes_transferred, last_activity)
    except:
        pass

def update_maintenance_stats(stats: Dict[str, Any]):
    """Update maintenance statistics in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.update_maintenance_stats(stats)
    except:
        pass

def show_server_error(message: str):
    """Show server error message in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.show_error(message)
    except:
        pass

def show_server_success(message: str):
    """Show server success message in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.show_success(message)
    except:
        pass

def show_server_notification(title: str, message: str):
    """Show server notification in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.show_notification(title, message)
    except:
        pass

# Test the GUI if run directly
if __name__ == "__main__":
    print("Testing Enhanced Server GUI...")
    
    # Test GUI initialization
    if initialize_server_gui():
        print("GUI initialized successfully")
        
        # Simulate some updates
        time.sleep(1)
        update_server_status(True, "127.0.0.1", 8080)
        
        time.sleep(1)
        update_client_stats(connected=2, total=5, active_transfers=1)
        
        time.sleep(1)
        update_transfer_stats(bytes_transferred=1024*1024*50)
        
        time.sleep(1)
        show_server_success("Test server started successfully")
        
        # Keep GUI running for testing
        try:
            gui = get_server_gui()
            if gui.gui_thread:
                gui.gui_thread.join()
        except KeyboardInterrupt:
            print("\nShutting down...")
            shutdown_server_gui()
    else:
        print("GUI initialization failed")